"""Database helpers shared by the Streamlit app (app.py) and the REST API (server.py)."""
import hashlib
import json
import os
import sqlite3
from collections import defaultdict

from audit_ledger import get_ledger, clear_ledger

DB_PATH = 'polyvote_relational.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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

def check_election_integrity(election_id):
    conn = get_db()
    rows = conn.execute("SELECT ballot_token, candidate_id, preference_rank FROM BALLOT_RANKS WHERE election_id = ? ORDER BY ballot_token, preference_rank", (election_id,)).fetchall()
    conn.close()

    # Only pull ledger blocks for this specific election
    ledger_dict = {b['ballot_token']: b['vote_data_hash'] for b in get_ledger() if b.get('election_id') == election_id}

    if not rows and not ledger_dict:
        return True, "No votes cast yet.", {"modified": [], "deleted": []}

    grouped = defaultdict(list)
    for t, c, r in rows: grouped[t].append((c, r))

    report = {"modified": [], "deleted": []}

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

    is_valid = not (report["modified"] or report["deleted"])
    total_anomalies = len(report["modified"]) + len(report["deleted"])

    if not is_valid:
        return False, f"Integrity Breach! {total_anomalies} ballot record(s) compromised.", report
    return True, "Relational DB perfectly matches immutable ledger.", report
