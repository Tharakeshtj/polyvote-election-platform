"""PolyVote REST API backing the React frontend in frontend/.

Run from anywhere:  python -m uvicorn server:app --port 8000   (cwd = this folder)
Reuses the same SQLite DB, ledger, tally engine and integrity sweep as the Streamlit app.
"""
import os
import random
import re
import secrets
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path

# The DB and ledger use paths relative to the project folder; pin cwd so the API works from any launch dir.
os.chdir(Path(__file__).resolve().parent)

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from audit_ledger import append_ballot_receipt, backend_info, get_ledger, verify_chain_integrity
from election_core import check_election_integrity, get_db, hash_pw, init_admin_db, wipe_all_database_data
from setup_db import setup_database
from tally_engine import calculate_irv_winner

setup_database()
init_admin_db()

app = FastAPI(title="PolyVote API")

# Local, in-memory sessions: token -> {"role": "admin"|"voter", ...}. Restarting the server signs everyone out.
SESSIONS: dict[str, dict] = {}
# Serialises every write that touches the JSON ledger (FastAPI runs sync endpoints on a thread pool).
WRITE_LOCK = threading.Lock()

DEMO_CANDIDATES = [('Arun Kumar', 'Academics'), ('Bhavya Singh', 'Sports'), ('Chaitanya Reddy', 'Hostels'), ('Diya Sharma', 'Tech'), ('Eshaan Iyer', 'Environment')]
DEMO_VOTER_PASSWORD = 'vote123'
LIFECYCLE = {'NOMINATION': 'VOTING', 'VOTING': 'CLOSED'}


@contextmanager
def db():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def election_or_404(conn, election_id: int):
    row = conn.execute(
        "SELECT e.election_id, e.status, e.start_time, e.end_time, o.org_name, o.admin_contact "
        "FROM ELECTION e JOIN ORGANIZATION o ON e.org_id = o.org_id WHERE e.election_id = ?", (election_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Election not found.")
    return dict(row)


def require_status(election: dict, *allowed: str):
    if election['status'] not in allowed:
        raise HTTPException(409, f"Not allowed while the election is {election['status']}.")


def candidate_ids(conn, election_id: int) -> list[int]:
    return [r[0] for r in conn.execute("SELECT candidate_id FROM CANDIDATE WHERE election_id = ? ORDER BY candidate_id", (election_id,))]


# ---------------------------------------------------------------- auth

def current_session(authorization: str | None = Header(None)):
    token = (authorization or '').removeprefix('Bearer ').strip()
    session = SESSIONS.get(token)
    if not session:
        raise HTTPException(401, "Your session has expired. Please sign in again.")
    return token, session


def require_admin(auth=Depends(current_session)):
    if auth[1]['role'] != 'admin':
        raise HTTPException(403, "Administrator access required.")
    return auth[1]


def require_voter(auth=Depends(current_session)):
    if auth[1]['role'] != 'voter':
        raise HTTPException(403, "Voter session required.")
    return auth


class AdminLoginIn(BaseModel):
    username: str
    password: str


class VoterLoginIn(BaseModel):
    election_id: int
    reg_no: str
    password: str


@app.post("/api/admin/login")
def admin_login(body: AdminLoginIn):
    with db() as conn:
        row = conn.execute("SELECT password_hash FROM ADMIN_USERS WHERE username = ?", (body.username.strip(),)).fetchone()
    if not row or row[0] != hash_pw(body.password):
        raise HTTPException(401, "Invalid administrator credentials.")
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {'role': 'admin', 'username': body.username.strip()}
    return {'token': token, 'username': body.username.strip()}


@app.get("/api/admin/me")
def admin_me(admin=Depends(require_admin)):
    return {'username': admin['username']}


@app.post("/api/logout", status_code=204)
def logout(auth=Depends(current_session)):
    SESSIONS.pop(auth[0], None)


@app.post("/api/voter/login")
def voter_login(body: VoterLoginIn):
    reg_no = body.reg_no.strip().upper()
    with db() as conn:
        election = election_or_404(conn, body.election_id)
        if election['status'] == 'NOMINATION':
            raise HTTPException(409, "Voting hasn't opened for this election yet.")
        if election['status'] == 'CLOSED':
            raise HTTPException(409, "This election is closed.")
        row = conn.execute(
            "SELECT participation_id, password_hash, has_voted FROM VOTER_PARTICIPATION WHERE student_reg_no = ? AND election_id = ?",
            (reg_no, body.election_id),
        ).fetchone()
    if not row:
        raise HTTPException(404, "That registration number isn't on this election's roster.")
    if row['password_hash'] != hash_pw(body.password):
        raise HTTPException(401, "Incorrect password.")
    if row['has_voted']:
        raise HTTPException(409, "You have already voted in this election.")
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {'role': 'voter', 'participation_id': row['participation_id'], 'election_id': body.election_id, 'reg_no': reg_no}
    return {'token': token, 'reg_no': reg_no}


# ---------------------------------------------------------------- public + voter

@app.get("/api/elections")
def public_elections():
    with db() as conn:
        rows = conn.execute(
            "SELECT e.election_id, o.org_name, e.status, e.start_time, e.end_time, "
            "(SELECT COUNT(*) FROM CANDIDATE c WHERE c.election_id = e.election_id) AS candidates "
            "FROM ELECTION e JOIN ORGANIZATION o ON e.org_id = o.org_id ORDER BY e.election_id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/config")
def public_config():
    """Optional PUBLIC_URL (set in .env) lets the voter-page QR point at the public link even when opened on localhost."""
    return {'public_url': os.environ.get('PUBLIC_URL', '').strip().rstrip('/') or None}


@app.get("/api/health")
def health():
    return {'status': 'ok', 'ledger': backend_info()}


@app.get("/api/receipts/{ballot_token}")
def verify_receipt(ballot_token: str):
    block = next((b for b in get_ledger() if b.get('ballot_token') == ballot_token.strip()), None)
    if not block:
        return {'found': False}
    with db() as conn:
        org = conn.execute(
            "SELECT o.org_name FROM ELECTION e JOIN ORGANIZATION o ON e.org_id = o.org_id WHERE e.election_id = ?", (block['election_id'],)
        ).fetchone()
        in_tally = conn.execute("SELECT 1 FROM BALLOT_RANKS WHERE ballot_token = ? LIMIT 1", (block['ballot_token'],)).fetchone() is not None
    return {
        'found': True, 'block_index': block['index'], 'timestamp': block['timestamp'], 'election_id': block['election_id'],
        'org_name': org[0] if org else None, 'block_hash': block['curr_hash'], 'in_tally': in_tally,
    }


@app.get("/api/voter/ballot")
def voter_ballot(auth=Depends(require_voter)):
    session = auth[1]
    with db() as conn:
        election = election_or_404(conn, session['election_id'])
        cands = conn.execute(
            "SELECT candidate_id, name, platform_statement FROM CANDIDATE WHERE election_id = ? ORDER BY candidate_id", (session['election_id'],)
        ).fetchall()
    return {
        'reg_no': session['reg_no'], 'election': {'election_id': election['election_id'], 'org_name': election['org_name'], 'status': election['status']},
        'candidates': [dict(c) for c in cands], 'ranks_required': min(3, len(cands)),
    }


class BallotIn(BaseModel):
    ranking: list[int]


@app.post("/api/voter/ballot")
def cast_ballot(body: BallotIn, auth=Depends(require_voter)):
    token, session = auth
    e_id = session['election_id']
    with WRITE_LOCK, db() as conn:
        require_status(election_or_404(conn, e_id), 'VOTING')
        cands = candidate_ids(conn, e_id)
        need = min(3, len(cands))
        if len(body.ranking) != need or len(set(body.ranking)) != need or not set(body.ranking) <= set(cands):
            raise HTTPException(422, f"Rank exactly {need} different candidates.")
        voter = conn.execute("SELECT has_voted FROM VOTER_PARTICIPATION WHERE participation_id = ?", (session['participation_id'],)).fetchone()
        if not voter:
            raise HTTPException(403, "You are no longer on this election's roster.")
        if voter['has_voted']:
            raise HTTPException(409, "You have already voted in this election.")
        ballot_token = str(uuid.uuid4())
        payload = [(cid, rank) for rank, cid in enumerate(body.ranking, start=1)]
        conn.execute("UPDATE VOTER_PARTICIPATION SET has_voted = 1 WHERE participation_id = ?", (session['participation_id'],))
        conn.executemany(
            "INSERT INTO BALLOT_RANKS (ballot_token, candidate_id, election_id, preference_rank) VALUES (?, ?, ?, ?)",
            [(ballot_token, cid, e_id, rank) for cid, rank in payload],
        )
        conn.commit()
        block = append_ballot_receipt(e_id, ballot_token, payload)
    SESSIONS.pop(token, None)
    return {'ballot_token': ballot_token, 'block_index': block['index'], 'block_hash': block['curr_hash'], 'timestamp': block['timestamp']}


# ---------------------------------------------------------------- admin: elections

class ElectionIn(BaseModel):
    org_name: str = Field(min_length=1)
    admin_contact: str = Field(min_length=1)


class StatusIn(BaseModel):
    status: str


@app.get("/api/admin/elections")
def admin_elections(_=Depends(require_admin)):
    with db() as conn:
        rows = conn.execute(
            "SELECT e.election_id, o.org_name, o.admin_contact, e.status, e.start_time, e.end_time, "
            "(SELECT COUNT(*) FROM CANDIDATE c WHERE c.election_id = e.election_id) AS candidates, "
            "(SELECT COUNT(*) FROM VOTER_PARTICIPATION v WHERE v.election_id = e.election_id) AS voters, "
            "(SELECT COALESCE(SUM(has_voted), 0) FROM VOTER_PARTICIPATION v WHERE v.election_id = e.election_id) AS voted, "
            "(SELECT COUNT(DISTINCT ballot_token) FROM BALLOT_RANKS b WHERE b.election_id = e.election_id) AS ballots "
            "FROM ELECTION e JOIN ORGANIZATION o ON e.org_id = o.org_id ORDER BY e.election_id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/admin/elections")
def create_election(body: ElectionIn, _=Depends(require_admin)):
    with db() as conn:
        cur = conn.execute("INSERT INTO ORGANIZATION (org_name, admin_contact) VALUES (?, ?)", (body.org_name.strip(), body.admin_contact.strip()))
        cur.execute(
            "INSERT INTO ELECTION (org_id, status, start_time, end_time) VALUES (?, 'NOMINATION', datetime('now'), datetime('now', '+7 days'))",
            (cur.lastrowid,),
        )
        conn.commit()
        return {'election_id': cur.lastrowid}


@app.get("/api/admin/elections/{e_id}")
def election_detail(e_id: int, _=Depends(require_admin)):
    with db() as conn:
        election = election_or_404(conn, e_id)
        cands = conn.execute(
            "SELECT c.candidate_id, c.name, c.platform_statement, "
            "(SELECT COUNT(*) FROM BALLOT_RANKS b WHERE b.candidate_id = c.candidate_id AND b.preference_rank = 1) AS first_preferences "
            "FROM CANDIDATE c WHERE c.election_id = ? ORDER BY c.candidate_id", (e_id,)
        ).fetchall()
        voters, voted = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(has_voted), 0) FROM VOTER_PARTICIPATION WHERE election_id = ?", (e_id,)
        ).fetchone()
        ballots = conn.execute("SELECT COUNT(DISTINCT ballot_token) FROM BALLOT_RANKS WHERE election_id = ?", (e_id,)).fetchone()[0]
    receipts = sum(1 for b in get_ledger() if b.get('election_id') == e_id)
    return {**election, 'candidates': [dict(c) for c in cands], 'voters': voters, 'voted': voted, 'ballots': ballots, 'ledger_receipts': receipts}


@app.post("/api/admin/elections/{e_id}/status")
def advance_status(e_id: int, body: StatusIn, _=Depends(require_admin)):
    with db() as conn:
        election = election_or_404(conn, e_id)
        if LIFECYCLE.get(election['status']) != body.status:
            raise HTTPException(409, f"Can't move from {election['status']} to {body.status}.")
        if body.status == 'VOTING' and not candidate_ids(conn, e_id):
            raise HTTPException(409, "Add at least one candidate before opening voting.")
        conn.execute("UPDATE ELECTION SET status = ? WHERE election_id = ?", (body.status, e_id))
        conn.commit()
    return {'status': body.status}


# ---------------------------------------------------------------- admin: candidates

class CandidateIn(BaseModel):
    name: str = Field(min_length=1)
    platform_statement: str = ''


class CountIn(BaseModel):
    count: int = Field(ge=1, le=1000)


@app.post("/api/admin/elections/{e_id}/candidates")
def add_candidate(e_id: int, body: CandidateIn, _=Depends(require_admin)):
    with db() as conn:
        require_status(election_or_404(conn, e_id), 'NOMINATION')
        conn.execute("INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?, ?, ?)", (e_id, body.name.strip(), body.platform_statement.strip()))
        conn.commit()
    return {'ok': True}


@app.post("/api/admin/elections/{e_id}/candidates/seed")
def seed_candidates(e_id: int, body: CountIn, _=Depends(require_admin)):
    with db() as conn:
        require_status(election_or_404(conn, e_id), 'NOMINATION')
        existing = {r[0] for r in conn.execute("SELECT name FROM CANDIDATE WHERE election_id = ?", (e_id,))}
        fresh = [(e_id, n, s) for n, s in DEMO_CANDIDATES if n not in existing][:body.count]
        conn.executemany("INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?, ?, ?)", fresh)
        conn.commit()
    return {'added': len(fresh)}


@app.delete("/api/admin/elections/{e_id}/candidates/{c_id}", status_code=204)
def delete_candidate(e_id: int, c_id: int, _=Depends(require_admin)):
    with db() as conn:
        require_status(election_or_404(conn, e_id), 'NOMINATION')
        try:
            conn.execute("DELETE FROM CANDIDATE WHERE candidate_id = ? AND election_id = ?", (c_id, e_id))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, "This candidate already appears on ballots.")


# ---------------------------------------------------------------- admin: voters

class VoterIn(BaseModel):
    reg_no: str = Field(min_length=1)
    password: str = Field(min_length=1)


@app.get("/api/admin/elections/{e_id}/voters")
def list_voters(e_id: int, _=Depends(require_admin)):
    with db() as conn:
        election_or_404(conn, e_id)
        rows = conn.execute(
            "SELECT participation_id, student_reg_no, has_voted FROM VOTER_PARTICIPATION WHERE election_id = ? ORDER BY student_reg_no", (e_id,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/admin/elections/{e_id}/voters")
def add_voter(e_id: int, body: VoterIn, _=Depends(require_admin)):
    reg_no = body.reg_no.strip().upper()
    with db() as conn:
        require_status(election_or_404(conn, e_id), 'NOMINATION', 'VOTING')
        try:
            conn.execute(
                "INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?, ?, ?, 0)",
                (e_id, reg_no, hash_pw(body.password)),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, f"{reg_no} is already on the roster.")
    return {'reg_no': reg_no}


@app.post("/api/admin/elections/{e_id}/voters/bulk")
def bulk_register(e_id: int, body: CountIn, _=Depends(require_admin)):
    with db() as conn:
        require_status(election_or_404(conn, e_id), 'NOMINATION', 'VOTING')
        regs = [r[0] for r in conn.execute("SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id = ?", (e_id,))]
        # Continue after the highest existing demo number so deleted voters can't cause collisions.
        start = max((int(m.group(1)) for r in regs if (m := re.fullmatch(r'25BCE(\d{4})', r))), default=0) + 1
        pw = hash_pw(DEMO_VOTER_PASSWORD)
        conn.executemany(
            "INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?, ?, ?, 0)",
            [(e_id, f'25BCE{str(n).zfill(4)}', pw) for n in range(start, start + body.count)],
        )
        conn.commit()
    return {'added': body.count, 'first': f'25BCE{str(start).zfill(4)}', 'password': DEMO_VOTER_PASSWORD}


@app.post("/api/admin/elections/{e_id}/simulate")
def simulate_ballots(e_id: int, body: CountIn, _=Depends(require_admin)):
    with WRITE_LOCK, db() as conn:
        require_status(election_or_404(conn, e_id), 'VOTING')
        cands = candidate_ids(conn, e_id)
        if len(cands) < 3:
            raise HTTPException(409, "Simulation needs at least 3 candidates.")
        unvoted = [r[0] for r in conn.execute(
            "SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id = ? AND has_voted = 0 LIMIT ?", (e_id, body.count)
        )]
        if not unvoted:
            raise HTTPException(409, "Everyone on the roster has already voted.")
        receipts = []
        for pid in unvoted:
            token = str(uuid.uuid4())
            payload = [(cid, rank) for rank, cid in enumerate(random.sample(cands, 3), start=1)]
            conn.execute("UPDATE VOTER_PARTICIPATION SET has_voted = 1 WHERE participation_id = ?", (pid,))
            conn.executemany(
                "INSERT INTO BALLOT_RANKS (ballot_token, candidate_id, election_id, preference_rank) VALUES (?, ?, ?, ?)",
                [(token, cid, e_id, rank) for cid, rank in payload],
            )
            receipts.append((token, payload))
        conn.commit()
        for token, payload in receipts:
            append_ballot_receipt(e_id, token, payload)
    return {'cast': len(unvoted)}


# ---------------------------------------------------------------- admin: audit + results

@app.get("/api/admin/elections/{e_id}/integrity")
def integrity_sweep(e_id: int, _=Depends(require_admin)):
    with db() as conn:
        election_or_404(conn, e_id)
    is_valid, message, report = check_election_integrity(e_id)
    return {'valid': is_valid, 'message': message, **report}


@app.get("/api/admin/elections/{e_id}/tally")
def tally(e_id: int, _=Depends(require_admin)):
    with db() as conn:
        election_or_404(conn, e_id)
    message, logs = calculate_irv_winner(e_id)
    rounds = []
    for log in logs or []:
        rows = [{'candidate': r['Candidate'], 'votes': int(r['Votes']), 'percentage': r['Percentage']} for r in log['table'].to_dict('records')]
        lowest = min((r['votes'] for r in rows), default=0)
        rounds.append({
            'round': log['round'], 'rows': rows, 'eliminated': log['eliminated'],
            # The engine breaks ties for last place by dictionary order; surface that so it isn't mistaken for a real result.
            'tie_break': bool(log['eliminated']) and sum(r['votes'] == lowest for r in rows) > 1,
        })
    if not logs:
        outcome, winner = 'no_votes', None
    elif ' wins ' in message:
        outcome, winner = 'winner', rounds[-1]['rows'][0]['candidate']
    else:
        outcome, winner = 'exhausted', None
    return {'outcome': outcome, 'winner': winner, 'message': message, 'rounds': rounds}


@app.get("/api/admin/ledger")
def ledger(election_id: int | None = None, _=Depends(require_admin)):
    chain_ok, chain_message = verify_chain_integrity()
    blocks = [b for b in get_ledger() if election_id is None or b.get('election_id') == election_id]
    return {'chain_valid': chain_ok, 'chain_message': chain_message, 'blocks': blocks[::-1]}


# ---------------------------------------------------------------- admin: DB studio (simulated raw DBA access)

class CandidatePatch(BaseModel):
    name: str = Field(min_length=1)
    platform_statement: str = ''


class VoterPatch(BaseModel):
    reg_no: str = Field(min_length=1)


class BallotRef(BaseModel):
    ballot_token: str
    preference_rank: int


class BallotPatch(BallotRef):
    candidate_id: int


@app.get("/api/admin/elections/{e_id}/studio")
def studio(e_id: int, _=Depends(require_admin)):
    with db() as conn:
        election_or_404(conn, e_id)
        cands = conn.execute("SELECT candidate_id, name, platform_statement FROM CANDIDATE WHERE election_id = ? ORDER BY candidate_id", (e_id,)).fetchall()
        voters = conn.execute("SELECT participation_id, student_reg_no, has_voted FROM VOTER_PARTICIPATION WHERE election_id = ? ORDER BY participation_id", (e_id,)).fetchall()
        ballots = conn.execute(
            "SELECT ballot_token, candidate_id, preference_rank FROM BALLOT_RANKS WHERE election_id = ? ORDER BY ballot_token, preference_rank", (e_id,)
        ).fetchall()
    return {'candidates': [dict(r) for r in cands], 'voters': [dict(r) for r in voters], 'ballots': [dict(r) for r in ballots]}


@app.put("/api/admin/elections/{e_id}/studio/candidates/{c_id}")
def studio_edit_candidate(e_id: int, c_id: int, body: CandidatePatch, _=Depends(require_admin)):
    with db() as conn:
        conn.execute("UPDATE CANDIDATE SET name = ?, platform_statement = ? WHERE candidate_id = ? AND election_id = ?", (body.name, body.platform_statement, c_id, e_id))
        conn.commit()
    return {'ok': True}


@app.put("/api/admin/elections/{e_id}/studio/voters/{p_id}")
def studio_edit_voter(e_id: int, p_id: int, body: VoterPatch, _=Depends(require_admin)):
    with db() as conn:
        try:
            conn.execute("UPDATE VOTER_PARTICIPATION SET student_reg_no = ? WHERE participation_id = ? AND election_id = ?", (body.reg_no.strip(), p_id, e_id))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, f"Registration No. {body.reg_no} already exists in the roster.")
    return {'ok': True}


@app.delete("/api/admin/elections/{e_id}/studio/voters/{p_id}", status_code=204)
def studio_drop_voter(e_id: int, p_id: int, _=Depends(require_admin)):
    with db() as conn:
        conn.execute("DELETE FROM VOTER_PARTICIPATION WHERE participation_id = ? AND election_id = ?", (p_id, e_id))
        conn.commit()


@app.put("/api/admin/elections/{e_id}/studio/ballots")
def studio_edit_ballot(e_id: int, body: BallotPatch, _=Depends(require_admin)):
    with db() as conn:
        if body.candidate_id not in candidate_ids(conn, e_id):
            raise HTTPException(422, "Pick a candidate from this election.")
        try:
            conn.execute(
                "UPDATE BALLOT_RANKS SET candidate_id = ? WHERE ballot_token = ? AND preference_rank = ? AND election_id = ?",
                (body.candidate_id, body.ballot_token, body.preference_rank, e_id),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, "That candidate is already ranked elsewhere on this ballot.")
    return {'ok': True}


@app.post("/api/admin/elections/{e_id}/studio/ballots/delete")
def studio_delete_ballot_rank(e_id: int, body: BallotRef, _=Depends(require_admin)):
    with db() as conn:
        conn.execute("DELETE FROM BALLOT_RANKS WHERE ballot_token = ? AND preference_rank = ? AND election_id = ?", (body.ballot_token, body.preference_rank, e_id))
        conn.commit()
    return {'ok': True}


@app.delete("/api/admin/elections/{e_id}/studio/ballots/{ballot_token}", status_code=204)
def studio_delete_ballot(e_id: int, ballot_token: str, _=Depends(require_admin)):
    with db() as conn:
        conn.execute("DELETE FROM BALLOT_RANKS WHERE ballot_token = ? AND election_id = ?", (ballot_token, e_id))
        conn.commit()


# ---------------------------------------------------------------- admin: administrators + reset

class ResetIn(BaseModel):
    confirm: str


@app.get("/api/admin/admins")
def list_admins(_=Depends(require_admin)):
    with db() as conn:
        return [r[0] for r in conn.execute("SELECT username FROM ADMIN_USERS ORDER BY username")]


@app.post("/api/admin/admins")
def add_admin(body: AdminLoginIn, _=Depends(require_admin)):
    if not body.username.strip() or not body.password:
        raise HTTPException(422, "Username and password are required.")
    with db() as conn:
        try:
            conn.execute("INSERT INTO ADMIN_USERS (username, password_hash) VALUES (?, ?)", (body.username.strip(), hash_pw(body.password)))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, "That username already exists.")
    return {'username': body.username.strip()}


@app.post("/api/admin/reset")
def factory_reset(body: ResetIn, _=Depends(require_admin)):
    if body.confirm != 'RESET':
        raise HTTPException(422, "Type RESET to confirm.")
    with WRITE_LOCK:
        wipe_all_database_data()
    for token in [t for t, s in SESSIONS.items() if s['role'] == 'voter']:
        SESSIONS.pop(token, None)
    return {'ok': True}


# ---------------------------------------------------------------- built frontend (npm run build)

DIST = Path('frontend/dist')
if DIST.is_dir():
    app.mount('/assets', StaticFiles(directory=DIST / 'assets'), name='assets')

    @app.get('/{path:path}', include_in_schema=False)
    def spa(path: str):
        if path.startswith('api/'):
            raise HTTPException(404)
        file = DIST / path
        return FileResponse(file if path and file.is_file() else DIST / 'index.html')
