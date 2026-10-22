"""PolyVote evaluation: prevention tests, API abuse tests, rogue-DBA tamper tests and benchmarks.

Runs against a throwaway copy of the application (never the real database or ledger) using the
JSON ledger backend, and writes experiments/results/<tag>.json.

    python experiments/run_experiments.py baseline
"""
import hashlib
import json
import os
import random
import shutil
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = sys.argv[1] if len(sys.argv) > 1 else 'run'
SIZES = [int(x) for x in os.environ.get('BENCH_SIZES', '100,1000,10000').split(',')]

os.environ['MONGO_URI'] = ''          # experiments use the file ledger so they never touch Atlas
os.environ['ADMIN_PASSWORD'] = ''
os.environ.pop('LEDGER_KEY', None)
if TAG.startswith('patched'):         # keyed chain on; the attacker scripts below never get this key
    os.environ['LEDGER_KEY'] = 'experiment-only-secret'
SB = Path(tempfile.mkdtemp(prefix='polyvote_exp_'))
SRC = Path(os.environ.get('EXP_SRC', ROOT))   # code under test; point at an older checkout to measure it
for f in SRC.glob('*.py'):
    shutil.copy(f, SB)
if (SRC / 'verification').exists():
    shutil.copytree(SRC / 'verification', SB / 'verification', ignore=shutil.ignore_patterns('__pycache__'))
(SB / 'frontend').mkdir()
os.chdir(SB)
sys.path.insert(0, str(SB))
random.seed(7)

import audit_ledger as L            # noqa: E402
import election_core as EC          # noqa: E402
import server                       # noqa: E402
import tally_engine                 # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

DB = 'polyvote_relational.db'
client = TestClient(server.app)
RESULTS = {'tag': TAG, 'prevention': [], 'api_abuse': [], 'tamper': [], 'privacy': [], 'otp': [], 'bench': {}}


# ------------------------------------------------------------------ helpers

def admin_headers():
    r = client.post('/api/admin/login', json={'username': 'admin', 'password': 'admin123'})
    return {'Authorization': f"Bearer {r.json()['token']}"}


H = admin_headers()


def raw(fk=False):
    c = sqlite3.connect(DB)
    if fk:
        c.execute('PRAGMA foreign_keys = ON')
    return c


def make_election(voters, ballots, name='Exp'):
    e = client.post('/api/admin/elections', json={'org_name': name, 'admin_contact': 'x@x'}, headers=H).json()['election_id']
    client.post(f'/api/admin/elections/{e}/candidates/seed', json={'count': 5}, headers=H)
    client.post(f'/api/admin/elections/{e}/voters/bulk', json={'count': voters}, headers=H)
    client.post(f'/api/admin/elections/{e}/status', json={'status': 'VOTING'}, headers=H)
    if ballots:
        client.post(f'/api/admin/elections/{e}/simulate', json={'count': ballots}, headers=H)
    return e


def voter_login(e, reg, pw='vote123', c=client):
    return c.post('/api/voter/login', json={'election_id': e, 'reg_no': reg, 'password': pw})


def cast(token, ranking, c=client):
    return c.post('/api/voter/ballot', json={'ranking': ranking}, headers={'Authorization': f'Bearer {token}'})


def cand_ids(e):
    with raw() as c:
        return [r[0] for r in c.execute('SELECT candidate_id FROM CANDIDATE WHERE election_id=? ORDER BY candidate_id', (e,))]


def snapshot(tag):
    d = SB / f'snap_{tag}'
    d.mkdir(exist_ok=True)
    shutil.copy(DB, d / DB)
    shutil.copy(L.LEDGER_FILE, d / L.LEDGER_FILE)
    return d


def restore(d):
    shutil.copy(d / DB, DB)
    shutil.copy(d / L.LEDGER_FILE, L.LEDGER_FILE)


def audit(e):
    ok_sweep, sweep_msg, report = EC.check_election_integrity(e)
    ok_chain, chain_msg = L.verify_chain_integrity()
    d = client.get(f'/api/admin/elections/{e}', headers=H).json()
    return {
        'sweep': not ok_sweep, 'chain': not ok_chain,
        'counters': not (d['voted'] == d['ballots'] == d['ledger_receipts']),
        'counts': {'voted_flags': d['voted'], 'ballots': d['ballots'], 'receipts': d['ledger_receipts']},
        'sweep_msg': sweep_msg, 'chain_msg': chain_msg,
    }


def verdict(a):
    if a['sweep'] or a['chain']:
        return 'detected'
    if a['counters']:
        return 'detected_manual_only'
    return 'undetected'


def plain_chain(blocks):
    """What an attacker without the application secret can rebuild: plain SHA-256 over every block."""
    prev = '0' * 64
    out = []
    for i, b in enumerate(blocks, start=1):
        nb = {k: v for k, v in b.items() if k != 'curr_hash'}
        nb['index'], nb['prev_hash'] = i, prev
        nb['curr_hash'] = hashlib.sha256(json.dumps(nb, sort_keys=True).encode()).hexdigest()
        out.append(nb)
        prev = nb['curr_hash']
    return out


def plain_block(blocks, e, token, payload):
    pstr = json.dumps(sorted(payload, key=lambda x: x[1]), sort_keys=True)
    nb = {'index': len(blocks) + 1, 'timestamp': '2026-10-22T00:00:00', 'election_id': e, 'ballot_token': token,
          'vote_data_hash': hashlib.sha256(pstr.encode()).hexdigest(),
          'prev_hash': blocks[-1]['curr_hash'] if blocks else '0' * 64}
    nb['curr_hash'] = hashlib.sha256(json.dumps(nb, sort_keys=True).encode()).hexdigest()
    return nb


def rec(section, id_, title, expected, outcome, detail):
    RESULTS[section].append({'id': id_, 'attack': title, 'expected': expected, 'outcome': outcome, 'detail': detail})
    print(f'  [{id_}] {outcome:<22} {title}')


# ------------------------------------------------------------------ A: database-level prevention

def run_prevention():
    print('A. Prevention at the database layer')
    e = make_election(10, 3)
    cands = cand_ids(e)
    with raw() as c:
        tok = c.execute('SELECT ballot_token FROM BALLOT_RANKS LIMIT 1').fetchone()[0]
        voted_pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE has_voted=1 LIMIT 1').fetchone()[0]
        any_pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION LIMIT 1').fetchone()[0]
        reg = c.execute('SELECT student_reg_no FROM VOTER_PARTICIPATION LIMIT 1').fetchone()[0]

    def attempt(id_, title, expected, sql, params=(), fk=True):
        c = raw(fk)
        try:
            c.execute(sql, params)
            c.commit()
            rec('prevention', id_, title, expected, 'not_prevented', 'statement succeeded')
        except sqlite3.Error as ex:
            rec('prevention', id_, title, expected, 'prevented', str(ex))
        finally:
            c.close()

    attempt('A1', 'Mark an already-voted voter as voted again', 'trigger',
            'UPDATE VOTER_PARTICIPATION SET has_voted=1 WHERE participation_id=?', (voted_pid,))
    attempt('A2', 'Insert a rank outside 1-3 (rank 4)', 'CHECK',
            'INSERT INTO BALLOT_RANKS VALUES (?,?,?,4)', (str(uuid.uuid4()), cands[0], e))
    attempt('A3', 'Rank the same candidate twice on one ballot', 'composite PK',
            'INSERT INTO BALLOT_RANKS VALUES (?,?,?,3)', (tok, cands[0], e))
    attempt('A4', 'Rank a candidate that does not exist (FK enforcement on)', 'FK',
            'INSERT INTO BALLOT_RANKS VALUES (?,?,?,1)', (str(uuid.uuid4()), 9999, e), fk=True)
    attempt('A5', 'Rank a nonexistent candidate from a default connection (FK pragma off)', 'FK',
            'INSERT INTO BALLOT_RANKS VALUES (?,?,?,1)', (str(uuid.uuid4()), 9999, e), fk=False)
    attempt('A6', 'Register the same reg. number twice in one election', 'UNIQUE',
            'INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?,?,?,0)', (e, reg, 'x'))
    attempt('A7', 'Set has_voted to an invalid value (2)', 'CHECK',
            'UPDATE VOTER_PARTICIPATION SET has_voted=2 WHERE participation_id=?', (any_pid,))


# ------------------------------------------------------------------ B: API abuse

def run_api_abuse():
    print('B. Abuse through the public API')
    e = make_election(40, 0)
    cands = cand_ids(e)
    other = make_election(5, 0, 'Other')
    other_cands = cand_ids(other)
    regs = [f'25BCE{n:04d}' for n in range(1, 41)]

    def status(r):
        return r.status_code

    r = voter_login(e, regs[0], 'wrong')
    rec('api_abuse', 'B1', 'Log in with a wrong password', 'rejected (401)', 'prevented' if status(r) == 401 else 'not_prevented', f'HTTP {status(r)}')
    r = voter_login(e, '25BCE9999')
    rec('api_abuse', 'B2', 'Log in with a reg. number not on the roster', 'rejected (404)', 'prevented' if status(r) == 404 else 'not_prevented', f'HTTP {status(r)}')
    r = voter_login(e, "' OR '1'='1' --", 'x')
    rec('api_abuse', 'B3', 'SQL injection in the reg. number field', 'rejected', 'prevented' if status(r) in (401, 404) else 'not_prevented', f'HTTP {status(r)}')

    tok = voter_login(e, regs[1]).json()['token']
    first = cast(tok, cands[:3])
    replay = cast(tok, cands[:3])
    rec('api_abuse', 'B4', 'Replay a session token after the ballot was cast', 'rejected (401)', 'prevented' if first.status_code == 200 and replay.status_code == 401 else 'not_prevented', f'cast {first.status_code}, replay {replay.status_code}')
    r = voter_login(e, regs[1])
    rec('api_abuse', 'B5', 'Log in again after voting', 'rejected (409)', 'prevented' if status(r) == 409 else 'not_prevented', f'HTTP {status(r)}')
    r = client.post('/api/voter/ballot', json={'ranking': cands[:3]})
    rec('api_abuse', 'B6', 'Cast a ballot with no session', 'rejected (401)', 'prevented' if status(r) == 401 else 'not_prevented', f'HTTP {status(r)}')
    vt = voter_login(e, regs[2]).json()['token']
    r = client.get('/api/admin/elections', headers={'Authorization': f'Bearer {vt}'})
    rec('api_abuse', 'B7', 'Use a voter token on an admin endpoint', 'rejected (403)', 'prevented' if status(r) == 403 else 'not_prevented', f'HTTP {status(r)}')
    r = cast(vt, other_cands[:3])
    rec('api_abuse', 'B8', "Rank another election's candidates", 'rejected (422)', 'prevented' if status(r) == 422 else 'not_prevented', f'HTTP {status(r)}')
    r = cast(vt, [cands[0], cands[0], cands[1]])
    rec('api_abuse', 'B9', 'Rank the same candidate twice via the API', 'rejected (422)', 'prevented' if status(r) == 422 else 'not_prevented', f'HTTP {status(r)}')
    r = cast(vt, cands[:2])
    rec('api_abuse', 'B10', 'Submit an incomplete ranking', 'rejected (422)', 'prevented' if status(r) == 422 else 'not_prevented', f'HTTP {status(r)}')

    # Concurrency: 20 sessions of the same voter cast at the same instant.
    sessions = [voter_login(e, regs[3]).json()['token'] for _ in range(20)]
    outcomes = []
    barrier = threading.Barrier(20)

    def worker(t):
        c = TestClient(server.app)
        barrier.wait()
        outcomes.append(cast(t, cands[:3], c).status_code)

    ts = [threading.Thread(target=worker, args=(t,)) for t in sessions]
    [t.start() for t in ts]
    [t.join() for t in ts]
    with raw() as c:
        n = c.execute('SELECT COUNT(DISTINCT ballot_token) FROM BALLOT_RANKS WHERE election_id=?', (e,)).fetchone()[0]
    # 1 ballot from B4 plus exactly 1 from the race.
    ok = outcomes.count(200) == 1 and n == 2
    rec('api_abuse', 'B11', '20 simultaneous casts from the same voter', 'exactly one accepted', 'prevented' if ok else 'not_prevented', f'{outcomes.count(200)} accepted, {n - 1} ballot rows for the voter')

    # Closed / nomination elections.
    client.post(f'/api/admin/elections/{e}/status', json={'status': 'CLOSED'}, headers=H)
    r = voter_login(e, regs[10])
    rec('api_abuse', 'B12', 'Log in after the election is closed', 'rejected (409)', 'prevented' if status(r) == 409 else 'not_prevented', f'HTTP {status(r)}')
    n2 = make_election(3, 0, 'Nom')
    client.post(f'/api/admin/elections/{n2}/status', json={'status': 'CLOSED'}, headers=H)
    r = client.post(f'/api/admin/elections/{e}/status', json={'status': 'VOTING'}, headers=H)
    rec('api_abuse', 'B13', 'Re-open a closed election', 'rejected (409)', 'prevented' if status(r) == 409 else 'not_prevented', f'HTTP {status(r)}')


# ------------------------------------------------------------------ C: rogue-DBA tampering

def run_tamper():
    print('C. Tampering by someone with direct storage access')
    e = make_election(60, 40)
    base = snapshot('tamper')
    a0 = audit(e)
    assert not (a0['sweep'] or a0['chain'] or a0['counters']), f'baseline not clean: {a0}'

    def tokens():
        with raw() as c:
            return [r[0] for r in c.execute('SELECT DISTINCT ballot_token FROM BALLOT_RANKS WHERE election_id=? ORDER BY ballot_token', (e,))]

    def case(id_, title, mutate):
        restore(base)
        detail = mutate() or ''
        a = audit(e)
        how = [k for k in ('sweep', 'chain', 'counters') if a[k]]
        rec('tamper', id_, title, 'detected', verdict(a), f"flags: {', '.join(how) or 'none'}; counts {a['counts']} {detail}".strip())

    cands = cand_ids(e)

    def c1():
        t = tokens()[0]
        with raw() as c:
            (a, _), (b, _) = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? AND preference_rank IN (1,2) ORDER BY preference_rank', (t,)).fetchall()
            c.execute('UPDATE BALLOT_RANKS SET preference_rank=2 WHERE ballot_token=? AND candidate_id=?', (t, a))
            c.execute('UPDATE BALLOT_RANKS SET preference_rank=1 WHERE ballot_token=? AND candidate_id=?', (t, b))
    case('C1', 'Swap the 1st and 2nd choice on one ballot', c1)

    def c2():
        t = tokens()[1]
        with raw() as c:
            used = {r[0] for r in c.execute('SELECT candidate_id FROM BALLOT_RANKS WHERE ballot_token=?', (t,))}
            new = next(x for x in cands if x not in used)
            c.execute('UPDATE BALLOT_RANKS SET candidate_id=? WHERE ballot_token=? AND preference_rank=1', (new, t))
    case('C2', 'Replace the first-choice candidate on one ballot', c2)

    def c3():
        with raw() as c:
            c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (tokens()[2],))
    case('C3', 'Delete one ballot', c3)

    def c4():
        with raw() as c:
            c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (tokens()[3],))
            pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=1 LIMIT 1', (e,)).fetchone()[0]
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=0 WHERE participation_id=?', (pid,))
    case('C4', 'Delete a ballot and clear a voted flag to hide the gap', c4)

    def inject_ballot(token):
        with raw() as c:
            c.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,?,?)', [(token, cid, e, r) for r, cid in enumerate(cands[:3], start=1)])
    case('C5', 'Inject a ballot with no receipt', lambda: inject_ballot(str(uuid.uuid4())))

    def c6():
        token = str(uuid.uuid4())
        inject_ballot(token)
        blocks = L.get_ledger()
        L.save_ledger(blocks + [plain_block(blocks, e, token, [(cid, r) for r, cid in enumerate(cands[:3], start=1)])])
        with raw() as c:
            pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=0 LIMIT 1', (e,)).fetchone()[0]
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=1 WHERE participation_id=?', (pid,))
    case('C6', 'Ballot stuffing: inject ballot, forge receipt, set a voted flag', c6)

    def c7():
        blocks = L.get_ledger()
        blocks[10]['vote_data_hash'] = 'f' * 64
        L.save_ledger(blocks)
    case('C7', 'Edit a ledger block without repairing the chain', c7)

    def c8():
        blocks = L.get_ledger()
        del blocks[15]
        L.save_ledger(blocks)
    case('C8', 'Delete a block from the middle of the ledger', c8)

    def c9():
        blocks = L.get_ledger()
        L.save_ledger(blocks[:-1])
    case('C9', 'Truncate the last block of the ledger', c9)

    def c10():
        c1()
        blocks = L.get_ledger()
        t = tokens()[0]
        with raw() as c:
            votes = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? ORDER BY preference_rank', (t,)).fetchall()
        for b in blocks:
            if b['ballot_token'] == t:
                b['vote_data_hash'] = hashlib.sha256(json.dumps(votes, sort_keys=True).encode()).hexdigest()
        L.save_ledger(plain_chain(blocks))
    case('C10', 'Change a ballot and rebuild the whole chain consistently (attacker has no secret key)', c10)

    def c11():
        with raw() as c:
            # Swap the two names so every ranking is attributed to the other candidate.
            a, b = [r[0] for r in c.execute('SELECT name FROM CANDIDATE WHERE candidate_id IN (?,?) ORDER BY candidate_id', (cands[0], cands[1]))]
            c.execute('UPDATE CANDIDATE SET name=? WHERE candidate_id=?', (b, cands[0]))
            c.execute('UPDATE CANDIDATE SET name=? WHERE candidate_id=?', (a, cands[1]))
    case('C11', 'Swap two candidates’ names after voting', c11)

    def c12():
        with raw() as c:
            pid, reg = c.execute('SELECT participation_id, student_reg_no FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=1 LIMIT 1', (e,)).fetchone()
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=0 WHERE participation_id=?', (pid,))
        t = voter_login(e, reg).json()['token']
        cast(t, cands[2:5])
    case('C12', 'Reset a voted flag, then let that voter cast a second ballot', c12)

    def c13():
        with raw() as c:
            c.execute('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?,?,?,0)', (e, '25BCE7777', EC.hash_pw('x')))
        t = voter_login(e, '25BCE7777', 'x').json()['token']
        cast(t, cands[:3])
    case('C13', 'Add a ghost voter to the roster and vote as them through the API', c13)


# ------------------------------------------------------------------ D: privacy structure

def run_privacy():
    print('D. Voter/ballot separation')
    with raw() as c:
        cols = [r[1] for r in c.execute('PRAGMA table_info(BALLOT_RANKS)')]
        vcols = [r[1] for r in c.execute('PRAGMA table_info(VOTER_PARTICIPATION)')]
    linking = [x for x in cols if x in vcols and x != 'election_id']
    RESULTS['privacy'].append({'check': 'Columns shared by BALLOT_RANKS and VOTER_PARTICIPATION (excluding election_id)', 'result': linking or 'none', 'columns_ballot': cols, 'columns_voter': vcols})
    blk = L.get_ledger()
    keys = sorted({k for b in blk for k in b})
    RESULTS['privacy'].append({'check': 'Fields stored in a ledger block', 'result': keys})
    print('  shared columns:', linking or 'none', '| ledger fields:', keys)


# ------------------------------------------------------------------ F: email OTP second factor

def run_otp():
    try:
        from verification import otp
    except ImportError:
        return
    print('F. Email OTP second factor')
    os.environ['SMTP_USER'] = os.environ['SMTP_PASS'] = ''   # outbox-only: no real email is sent
    os.environ['OTP_REQUIRED'] = '1'
    e = make_election(12, 0, 'OTP')
    cands = cand_ids(e)
    client.put(f'/api/admin/elections/{e}/contacts', json={'reg_no': '25BCE0001', 'email': 'demo@example.com'}, headers=H)
    client.post(f'/api/admin/elections/{e}/contacts/fill', json={'base_email': 'demo@example.com'}, headers=H)
    vdb = lambda: sqlite3.connect(otp.DB_FILE)   # noqa: E731

    def latest_code(reg):
        return next(x['code'] for x in otp.outbox() if x['reg_no'] == reg)

    def t(id_, title, expected, ok, detail=''):
        rec('otp', id_, title, expected, 'passed' if ok else 'FAILED', detail)

    # F1: password alone must not open a ballot session
    r = voter_login(e, '25BCE0002')
    body = r.json()
    no_session = 'token' not in body and body.get('otp_required') is True
    as_bearer = client.get('/api/voter/ballot', headers={'Authorization': f"Bearer {body.get('challenge')}"}).status_code
    t('F1', 'Correct password alone does not create a voting session', 'no token issued; challenge id is not a session', no_session and as_bearer == 401, f'login {r.status_code}, challenge used as bearer: {as_bearer}')

    # F2: correct code opens the session and the ballot works
    code = latest_code('25BCE0002')
    v = client.post('/api/voter/otp/verify', json={'challenge': body['challenge'], 'code': code})
    cast_status = cast(v.json().get('token'), cands[:3]).status_code if v.status_code == 200 else None
    t('F2', 'Correct emailed code unlocks the ballot', 'session issued, ballot accepted', v.status_code == 200 and cast_status == 200, f'verify {v.status_code}, cast {cast_status}')

    # F3: code is single-use
    again = client.post('/api/voter/otp/verify', json={'challenge': body['challenge'], 'code': code})
    t('F3', 'A used code cannot be replayed', 'rejected (410)', again.status_code == 410, f'HTTP {again.status_code}')

    # F4: three wrong guesses lock the challenge, even if the right code follows
    b4 = voter_login(e, '25BCE0003').json()
    right = latest_code('25BCE0003')
    wrong = '000000' if right != '000000' else '111111'
    codes = [client.post('/api/voter/otp/verify', json={'challenge': b4['challenge'], 'code': wrong}).status_code for _ in range(3)]
    late = client.post('/api/voter/otp/verify', json={'challenge': b4['challenge'], 'code': right}).status_code
    t('F4', 'Three wrong codes lock the challenge', '401, 401, 410 then the right code is refused', codes == [401, 401, 410] and late == 410, f'{codes}, then correct code: {late}')

    # F5: expiry
    b5 = voter_login(e, '25BCE0004').json()
    with vdb() as c:
        c.execute('UPDATE OTP_CHALLENGE SET expires_at = expires_at - 400 WHERE challenge_id = ?', (b5['challenge'],))
    r5 = client.post('/api/voter/otp/verify', json={'challenge': b5['challenge'], 'code': latest_code('25BCE0004')})
    t('F5', 'An expired code is refused', 'rejected (410)', r5.status_code == 410, f'HTTP {r5.status_code}')

    # F6/F7: resend cooldown, then a fresh code replaces the old one
    b6 = voter_login(e, '25BCE0005').json()
    old = latest_code('25BCE0005')
    quick = client.post('/api/voter/otp/resend', json={'challenge': b6['challenge']}).status_code
    with vdb() as c:
        c.execute('UPDATE OTP_CHALLENGE SET last_sent_at = last_sent_at - 60 WHERE challenge_id = ?', (b6['challenge'],))
    slow = client.post('/api/voter/otp/resend', json={'challenge': b6['challenge']}).status_code
    new = latest_code('25BCE0005')
    old_dead = client.post('/api/voter/otp/verify', json={'challenge': b6['challenge'], 'code': old}).status_code if old != new else 401
    t('F6', 'Resend is rate-limited to one per 30 seconds', 'immediate resend 429, later resend 200', quick == 429 and slow == 200, f'{quick} then {slow}')
    t('F7', 'A resent code invalidates the previous one', 'old code rejected', old_dead == 401, f'old code: HTTP {old_dead}')

    # F8: resend cap
    b8 = voter_login(e, '25BCE0006').json()
    last = None
    for _ in range(6):
        with vdb() as c:
            c.execute('UPDATE OTP_CHALLENGE SET last_sent_at = last_sent_at - 60 WHERE challenge_id = ?', (b8['challenge'],))
        last = client.post('/api/voter/otp/resend', json={'challenge': b8['challenge']}).status_code
    t('F8', 'A challenge allows at most 5 codes', 'sixth send refused (429)', last == 429, f'HTTP {last}')

    # F9: voter with no email on file
    with raw() as c:
        c.execute('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?,?,?,0)', (e, '25BCE5555', EC.hash_pw('pw')))
    r9 = voter_login(e, '25BCE5555', 'pw')
    t('F9', 'A voter with no email on file cannot proceed', '409 with a clear message', r9.status_code == 409, f'HTTP {r9.status_code}')

    # F10: codes are never stored in plaintext
    live = latest_code('25BCE0006')
    with vdb() as c:
        dump = ' '.join(str(x) for tbl in ('OTP_CHALLENGE', 'MAIL_LOG', 'VOTER_CONTACT') for row in c.execute(f'SELECT * FROM {tbl}') for x in row)
    t('F10', 'Plaintext codes are absent from the verification database', 'code not found in any table', live not in dump.split(), 'checked OTP_CHALLENGE, MAIL_LOG, VOTER_CONTACT')

    # F11: challenge-creation rate limit
    statuses = [voter_login(e, '25BCE0007').status_code for _ in range(7)]
    t('F11', 'Repeated sign-ins are rate-limited', 'sixth challenge in 15 min refused (429)', statuses.count(429) >= 1 and statuses[:5] == [200] * 5, f'{statuses}')

    # F12: code format
    sample = [otp._new_code() for _ in range(5000)]
    t('F12', 'Codes are 6 digits including leading zeros', 'all length 6, mostly distinct', all(len(c) == 6 and c.isdigit() for c in sample) and len(set(sample)) > 4900, f'{len(set(sample))} distinct of 5000')

    # F13: SMTP failure must not break sign-in
    os.environ.update({'SMTP_USER': 'x@example.com', 'SMTP_PASS': 'x', 'SMTP_HOST': '127.0.0.1', 'SMTP_PORT': '1'})
    r13 = voter_login(e, '25BCE0008')
    time.sleep(2.5)
    status13 = next((x['status'] for x in otp.outbox() if x['reg_no'] == '25BCE0008'), '')
    t('F13', 'A failed email send does not break sign-in', 'challenge still issued; failure logged; code stays in the outbox', r13.status_code == 200 and status13.startswith('failed'), f'login {r13.status_code}, mail status "{status13}"')
    os.environ['SMTP_USER'] = os.environ['SMTP_PASS'] = ''

    # F14: contact email lives outside the election database
    with raw() as c:
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        cols = [x[1] for tb in tables for x in c.execute(f'PRAGMA table_info({tb})')]
    t('F14', 'Voter email is not stored in the election database', 'no email column in any election table', 'email' not in cols, f'election tables: {sorted(tables)}')
    os.environ['OTP_REQUIRED'] = ''


# ------------------------------------------------------------------ E: benchmarks

def seed_bulk(n, extra_unvoted=30):
    """Fast seed: n ballots (+ n voters flagged) and a few unvoted voters, built directly in SQL and in memory."""
    EC.wipe_all_database_data()   # clears every table and the ledger; ids restart at 1
    conn = raw()
    conn.execute("INSERT INTO ORGANIZATION (org_name, admin_contact) VALUES ('Bench','b')")
    conn.execute("INSERT INTO ELECTION (org_id, status, start_time, end_time) VALUES (1,'VOTING',datetime('now'),datetime('now','+7 days'))")
    conn.executemany('INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (1,?,?)', [(f'C{i}', '') for i in range(1, 6)])
    pw = EC.hash_pw('vote123')
    conn.executemany('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (1,?,?,?)',
                     [(f'25BCE{i:05d}', pw, 1 if i <= n else 0) for i in range(1, n + extra_unvoted + 1)])
    chain, prev, rows = [], '0' * 64, []
    for i in range(1, n + 1):
        token = str(uuid.uuid4())
        payload = [(cid, r) for r, cid in enumerate(random.sample(range(1, 6), 3), start=1)]
        blk = L._seal(1, token, payload, i, prev)
        chain.append(blk)
        prev = blk['curr_hash']
        rows += [(token, cid, 1, r) for cid, r in payload]
    conn.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,?,?)', rows)
    conn.commit()
    conn.close()
    L.save_ledger(chain)
    return chain


def timed(fn, reps=3):
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        out = fn()
        ts.append((time.perf_counter() - t) * 1000)
    return round(statistics.median(ts), 2), out


def run_bench():
    print('E. Benchmarks (file ledger backend)')
    for n in SIZES:
        chain = seed_bulk(n)
        sweep_ms, _ = timed(lambda: EC.check_election_integrity(1))
        chain_ms, ok = timed(lambda: L.verify_chain_integrity())
        tally_ms, _ = timed(lambda: tally_engine.calculate_irv_winner(1), reps=2)
        tok = chain[n // 2]['ballot_token']
        rcpt_ms, _ = timed(lambda: client.get(f'/api/receipts/{tok}'), reps=5)
        casts = []
        for i in range(8):
            reg = f'25BCE{n + 1 + i:05d}'
            t = voter_login(1, reg).json()['token']
            s = time.perf_counter()
            r = cast(t, [1, 2, 3])
            casts.append((time.perf_counter() - s) * 1000)
            assert r.status_code == 200, r.text
        size_kb = round(os.path.getsize(L.LEDGER_FILE) / 1024, 1)
        RESULTS['bench'][str(n)] = {'cast_ms': round(statistics.median(casts), 2), 'sweep_ms': sweep_ms, 'chain_verify_ms': chain_ms,
                                     'tally_ms': tally_ms, 'receipt_lookup_ms': rcpt_ms, 'ledger_file_kb': size_kb, 'chain_ok': ok[0]}
        print(f'  N={n}: {RESULTS["bench"][str(n)]}')


if __name__ == '__main__':
    t0 = time.time()
    run_prevention()
    run_api_abuse()
    run_tamper()
    run_privacy()
    run_otp()
    run_bench()
    RESULTS['seconds'] = round(time.time() - t0, 1)
    out = ROOT / 'experiments' / 'results'
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{TAG}.json').write_text(json.dumps(RESULTS, indent=2, default=str), encoding='utf-8')
    print(f'\nWrote experiments/results/{TAG}.json in {RESULTS["seconds"]}s (sandbox: {SB})')
