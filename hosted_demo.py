"""Seeds a ready-to-use demo election when a hosted instance starts with an empty database (HOSTED_DEMO=true).

Hosting platforms with a free plan often give the app a fresh, empty disk after every restart. The ledger and the
database must start together, so the ledger is cleared before the demo data is created.
"""
import os
import random
import uuid

from audit_ledger import append_ballot_receipt, clear_ledger
from election_core import get_db, hash_pw, roster_hash
from verification import otp

CANDIDATES = [('Arun Kumar', 'Academics'), ('Bhavya Singh', 'Sports'), ('Chaitanya Reddy', 'Hostels'), ('Diya Sharma', 'Tech'), ('Eshaan Iyer', 'Environment')]


def enabled() -> bool:
    return os.environ.get('HOSTED_DEMO', '').strip().lower() in ('1', 'true', 'yes', 'on')


def seed_if_empty(voters: int = 30, prevote: int = 18) -> bool:
    conn = get_db()
    try:
        if conn.execute('SELECT COUNT(*) FROM ELECTION').fetchone()[0]:
            return False
        clear_ledger()
        otp.init()
        org = conn.execute('INSERT INTO ORGANIZATION (org_name, admin_contact) VALUES (?, ?)',
                           ('VIT Student Council Election 2026', 'electoral.officer@vit.example')).lastrowid
        e = conn.execute("INSERT INTO ELECTION (org_id, status, start_time, end_time) VALUES (?, 'VOTING', datetime('now'), datetime('now', '+30 days'))", (org,)).lastrowid
        conn.executemany('INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?, ?, ?)', [(e, n, p) for n, p in CANDIDATES])
        pw = hash_pw('vote123')
        regs = [f'25BCE{i:04d}' for i in range(1, voters + 1)]
        conn.executemany('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?, ?, ?, 0)', [(e, r, pw) for r in regs])
        conn.commit()
        otp.fill_plus_addresses(e, regs, os.environ.get('DEMO_EMAIL', 'demo@example.com'))

        cands = [r[0] for r in conn.execute('SELECT candidate_id FROM CANDIDATE WHERE election_id = ? ORDER BY candidate_id', (e,))]
        rh = roster_hash(conn, e)
        pids = [r[0] for r in conn.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id = ? ORDER BY participation_id LIMIT ?', (e, prevote))]
        for pid in pids:
            token = str(uuid.uuid4())
            payload = [(cid, rank) for rank, cid in enumerate(random.sample(cands, 3), start=1)]
            conn.execute('UPDATE VOTER_PARTICIPATION SET has_voted = 1 WHERE participation_id = ?', (pid,))
            conn.executemany('INSERT INTO BALLOT_RANKS (ballot_token, candidate_id, election_id, preference_rank) VALUES (?, ?, ?, ?)',
                             [(token, cid, e, rank) for cid, rank in payload])
            conn.commit()
            append_ballot_receipt(e, token, payload, rh)
        return True
    finally:
        conn.close()
