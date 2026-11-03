"""Database helpers shared by the Streamlit app (app.py) and the REST API (server.py)."""
import hashlib
import json
import os
import sqlite3
from collections import defaultdict

import hmac
import secrets

from audit_ledger import get_ledger, clear_ledger, get_roster_seal, put_roster_seal, roster_tag, verify_roster_seal

DB_PATH = 'polyvote_relational.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Passwords are stored salted and slowed down (PBKDF2-HMAC-SHA256). Older rows hold a bare SHA-256 hex digest;
# they still verify and are upgraded to the new format the next time that person signs in.
PW_SCHEME = 'pbkdf2_sha256'
PW_ITERATIONS = int(os.environ.get('PASSWORD_HASH_ITERATIONS', '600000') or 600000)   # OWASP 2023 minimum for PBKDF2-SHA256

def hash_pw(password: str, iterations: int | None = None) -> str:
    it = iterations or PW_ITERATIONS
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, it)
    return f'{PW_SCHEME}${it}${salt.hex()}${digest.hex()}'

def verify_pw(password: str, stored: str | None) -> bool:
    stored = stored or ''
    if stored.startswith(PW_SCHEME + '$'):
        try:
            _, it, salt, digest = stored.split('$')
            calc = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(it))
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(calc.hex(), digest)
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)   # legacy unsalted row

def pw_needs_upgrade(stored: str | None) -> bool:
    stored = stored or ''
    if not stored.startswith(PW_SCHEME + '$'):
        return True
    try:
        return int(stored.split('$')[1]) < PW_ITERATIONS
    except (IndexError, ValueError):
        return True

def reseal_roster(election_id: int, conn=None):
    """Record the roster the application just built, in the ledger store, so a voter added behind its back is noticed."""
    own = conn is None
    conn = conn or get_db()
    try:
        regs = [r[0] for r in conn.execute("SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id = ?", (election_id,))]
    finally:
        if own:
            conn.close()
    put_roster_seal(election_id, regs)

def init_admin_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS ADMIN_USERS (
                    username TEXT UNIQUE,
                    password_hash TEXT)''')
    if conn.execute("SELECT COUNT(*) FROM ADMIN_USERS").fetchone()[0] == 0:
        conn.execute("INSERT INTO ADMIN_USERS (username, password_hash) VALUES (?, ?)", ('admin', hash_pw('admin123')))
    # ADMIN_PASSWORD (from .env) overrides the default so a public demo is not left on admin123.
    admin_pw = os.environ.get('ADMIN_PASSWORD', '').strip()
    if admin_pw:
        conn.execute("UPDATE ADMIN_USERS SET password_hash = ? WHERE username = 'admin'", (hash_pw(admin_pw),))
    conn.commit()
    conn.close()

def wipe_all_database_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    for table in ['BALLOT_RANKS', 'VOTER_PARTICIPATION', 'CANDIDATE', 'ELECTION', 'ORGANIZATION', 'sqlite_sequence']:
        cursor.execute(f"DELETE FROM {table};")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    clear_ledger()

def roster_hash(conn, election_id):
    """SHA-256 over the election's (candidate_id, name) pairs; sealed into every ledger block."""
    pairs = conn.execute("SELECT candidate_id, name FROM CANDIDATE WHERE election_id = ? ORDER BY candidate_id", (election_id,)).fetchall()
    return hashlib.sha256(json.dumps([list(p) for p in pairs]).encode()).hexdigest()

def check_election_integrity(election_id):
    conn = get_db()
    rows = conn.execute("SELECT ballot_token, candidate_id, preference_rank FROM BALLOT_RANKS WHERE election_id = ? ORDER BY ballot_token, preference_rank", (election_id,)).fetchall()
    voted_flags = conn.execute("SELECT COALESCE(SUM(has_voted), 0) FROM VOTER_PARTICIPATION WHERE election_id = ?", (election_id,)).fetchone()[0]
    current_roster = roster_hash(conn, election_id)
    current_voters = [r[0] for r in conn.execute("SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id = ?", (election_id,))]
    conn.close()

    # Only pull ledger blocks for this specific election
    blocks = [b for b in get_ledger() if b.get('election_id') == election_id]
    ledger_dict = {b['ballot_token']: b['vote_data_hash'] for b in blocks}

    empty = {"modified": [], "deleted": [], "injected": [], "roster_changed": False, "count_mismatch": None,
             "voters_added": [], "voters_removed": 0, "roster_seal": "not_sealed"}

    # 6. Voter roster: compare the voters now in the database with the keyed seal the application wrote as it built the roster.
    seal = get_roster_seal(election_id)
    promised = any(b.get('voters_sealed') for b in blocks)   # the chain says a seal existed when a ballot was cast
    roster_report = dict(empty)
    if seal is None:
        roster_report["roster_seal"] = "missing" if promised else "not_sealed"
    elif not verify_roster_seal(seal):
        roster_report["roster_seal"] = "invalid"
    else:
        sealed_tags = set(seal.get("tags", []))
        now_tags = {}
        for reg in current_voters:
            now_tags.setdefault(roster_tag(election_id, reg), []).append(reg)
        roster_report["voters_added"] = sorted(reg for tag, regs in now_tags.items() if tag not in sealed_tags for reg in regs)
        roster_report["voters_removed"] = len(sealed_tags - set(now_tags))
        roster_report["roster_seal"] = "changed" if (roster_report["voters_added"] or roster_report["voters_removed"]) else "ok"
    roster_breach = roster_report["roster_seal"] in ("missing", "invalid", "changed")

    def roster_text():
        s = roster_report["roster_seal"]
        if s == "changed":
            bits = []
            if roster_report["voters_added"]: bits.append(f"{len(roster_report['voters_added'])} voter(s) added outside the application ({', '.join(roster_report['voters_added'][:5])})")
            if roster_report["voters_removed"]: bits.append(f"{roster_report['voters_removed']} voter(s) removed")
            return "voter roster changed: " + "; ".join(bits)
        return {"missing": "voter roster seal is missing", "invalid": "voter roster seal does not verify"}[s]

    if not rows and not ledger_dict:
        if roster_breach:
            return False, "Integrity Breach! " + roster_text() + ".", roster_report
        return True, "No votes cast yet.", roster_report

    grouped = defaultdict(list)
    for t, c, r in rows: grouped[t].append((c, r))

    report = dict(roster_report)
    report["modified"], report["deleted"] = [], []

    # 1. Check for Modified Votes (In SQL, but hash doesn't match Ledger)
    for t, votes in grouped.items():
        if t in ledger_dict:
            recomputed = hashlib.sha256(json.dumps(votes, sort_keys=True).encode()).hexdigest()
            if recomputed != ledger_dict[t]:
                report["modified"].append(t)

    # 2. Check for Deleted/Suppressed Votes (In Ledger, but completely missing from SQL)
    for t in ledger_dict.keys():
        if t not in grouped:
            report["deleted"].append(t)

    # 3. Injected ballots: in SQL with no receipt at all
    report["injected"] = [t for t in grouped if t not in ledger_dict]

    # 4. Candidate names changed after votes were sealed
    sealed = {b['roster_hash'] for b in blocks if b.get('roster_hash')}
    report["roster_changed"] = bool(sealed) and sealed != {current_roster}

    # 5. Three-way reconciliation: voter flags, ballots and receipts must agree
    counts = {"voted_flags": int(voted_flags), "ballots": len(grouped), "receipts": len(ledger_dict)}
    if len(set(counts.values())) > 1:
        report["count_mismatch"] = counts

    is_valid = not (report["modified"] or report["deleted"] or report["injected"] or report["roster_changed"] or report["count_mismatch"] or roster_breach)
    total_anomalies = len(report["modified"]) + len(report["deleted"]) + len(report["injected"])

    if not is_valid:
        parts = []
        if total_anomalies: parts.append(f"{total_anomalies} ballot record(s) compromised")
        if report["roster_changed"]: parts.append("candidate names changed since voting")
        if report["count_mismatch"]: parts.append("voter flags, ballots and receipts disagree")
        if roster_breach: parts.append(roster_text())
        return False, "Integrity Breach! " + "; ".join(parts) + ".", report
    return True, "Relational DB perfectly matches immutable ledger.", report
