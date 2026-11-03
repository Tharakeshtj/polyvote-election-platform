"""Evaluation engine: 31 attack scenarios, per-detector firing, design profiles and ablations.

Every scenario runs against a throwaway copy of the application (the sandbox made by run_experiments), once with the keyed
ledger chain ("keyed") and once with a plain SHA-256 chain ("unkeyed"). For each run we record WHICH detector fired:

    chain            hash-chain verification of the whole ledger
    modified         sweep rule 1: ballot ranks differ from the sealed hash
    deleted          sweep rule 2: a sealed ballot is missing from the database
    injected         sweep rule 3: a ballot has no receipt
    candidate_seal   sweep rule 4: candidate names differ from the sealed roster hash
    count_mismatch   sweep rule 5: voter flags, ballots and receipts disagree
    voter_seal       sweep rule 6: the voter roster differs from the keyed roster seal
    counters         an officer comparing the three counters by eye (not automatic)

A "design profile" is a subset of detectors (plus a key mode). Detection under a profile is read off the matrix, so ablations
and design-class comparisons need no extra runs and are exactly comparable.
"""
import hashlib
import json
import shutil
import sqlite3
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys                                    # noqa: E402
sys.path.insert(0, str(HERE.parent))
sys.argv = ['run_experiments', 'patched_full']   # run_experiments reads argv: a 'patched' tag enables the keyed chain
import run_experiments as X                   # noqa: E402,F401  (builds the sandbox, client, helpers)

L, EC, client, H = X.L, X.EC, X.client, X.H
KEY = b'experiment-only-secret'
DETECTORS = ['chain', 'modified', 'deleted', 'injected', 'candidate_seal', 'count_mismatch', 'voter_seal', 'counters']
AUTOMATIC = [d for d in DETECTORS if d != 'counters']
ROSTER = L.ROSTER_FILE


# ------------------------------------------------------------------ snapshots
def snap(tag):
    d = X.SB / f'evsnap_{tag}'
    d.mkdir(exist_ok=True)
    shutil.copy(X.DB, d / X.DB)
    shutil.copy(L.LEDGER_FILE, d / L.LEDGER_FILE)
    if Path(ROSTER).exists():
        shutil.copy(ROSTER, d / ROSTER)
    return d


def restore(d):
    shutil.copy(d / X.DB, X.DB)
    shutil.copy(d / L.LEDGER_FILE, L.LEDGER_FILE)
    if (d / ROSTER).exists():
        shutil.copy(d / ROSTER, ROSTER)
    elif Path(ROSTER).exists():
        Path(ROSTER).unlink()
    L._seal_known.clear()


# ------------------------------------------------------------------ audit with per-detector output
def audit_full(e):
    t0 = time.perf_counter()
    ok, msg, rep = EC.check_election_integrity(e)
    ok_chain, chain_msg = L.verify_chain_integrity()
    ms = (time.perf_counter() - t0) * 1000
    d = client.get(f'/api/admin/elections/{e}', headers=H).json()
    det = {
        'chain': not ok_chain,
        'modified': bool(rep['modified']),
        'deleted': bool(rep['deleted']),
        'injected': bool(rep['injected']),
        'candidate_seal': bool(rep['roster_changed']),
        'count_mismatch': bool(rep['count_mismatch']),
        'voter_seal': rep.get('roster_seal') in ('changed', 'missing', 'invalid'),
        'counters': not (d['voted'] == d['ballots'] == d['ledger_receipts']),
    }
    return {'detectors': det, 'sweep_msg': msg, 'chain_msg': chain_msg, 'ms': round(ms, 2),
            'counts': {'voted_flags': d['voted'], 'ballots': d['ballots'], 'receipts': d['ledger_receipts']},
            'anomalies': {'modified': len(rep['modified']), 'deleted': len(rep['deleted']), 'injected': len(rep['injected']),
                          'voters_added': list(rep.get('voters_added', [])), 'voters_removed': rep.get('voters_removed', 0),
                          'roster_seal': rep.get('roster_seal')}}


# ------------------------------------------------------------------ attacker helpers
def rebuild_chain(blocks, keyed):
    """Recompute prev_hash and curr_hash for every block. keyed=True is an attacker who holds the ledger key."""
    prev, out = '0' * 64, []
    for i, b in enumerate(blocks, start=1):
        nb = {k: v for k, v in b.items() if k != 'curr_hash'}
        nb['index'], nb['prev_hash'] = i, prev
        if keyed:
            nb['curr_hash'] = L._block_hash(i, nb)
        else:
            nb['curr_hash'] = hashlib.sha256(json.dumps(nb, sort_keys=True).encode()).hexdigest()
        out.append(nb)
        prev = nb['curr_hash']
    return out


def plain_roster_seal(e, regs):
    """A roster seal built without the key (plain SHA-256), as an attacker who only reads the code could write it."""
    tags = sorted({hashlib.sha256(f'voter|{e}|{r}'.encode()).hexdigest()[:32] for r in regs})
    rec = {'election_id': e, 'version': 99, 'count': len(tags), 'tags': tags, 'updated': '2026-11-04T00:00:00'}
    rec['signature'] = hashlib.sha256(b'roster|' + json.dumps(rec, sort_keys=True).encode()).hexdigest()
    return rec


# ------------------------------------------------------------------ building an election in a key mode
def build(mode, voters=60, ballots=40, early=20):
    L.LEDGER_KEY = KEY if mode == 'keyed' else b''
    EC.wipe_all_database_data()
    e = X.make_election(voters, early, name=f'Eval-{mode}')
    early_snap = snap(f'{mode}_early')
    client.post(f'/api/admin/elections/{e}/simulate', json={'count': ballots - early}, headers=H)
    return e, snap(f'{mode}_base'), early_snap


class Ctx:
    def __init__(self, mode):
        self.mode = mode
        self.e, self.base, self.early = build(mode)
        self.cands = X.cand_ids(self.e)

    def tokens(self):
        with X.raw() as c:
            return [r[0] for r in c.execute('SELECT DISTINCT ballot_token FROM BALLOT_RANKS WHERE election_id=? ORDER BY ballot_token', (self.e,))]

    def inject(self, token):
        with X.raw() as c:
            c.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,?,?)', [(token, cid, self.e, r) for r, cid in enumerate(self.cands[:3], start=1)])


# ------------------------------------------------------------------ the 31 scenarios
# adversary: who can do it. 'db' = election database, 'ledger' = ledger store, 'both' = both stores, 'api' = also uses the public API,
# 'key' = also holds the ledger key (outside the stated attacker model, reported so the limit is on the record).
def scenarios():
    S = []

    def add(id_, title, adversary, in_scope, fn, note=''):
        S.append({'id': id_, 'title': title, 'adversary': adversary, 'in_scope': in_scope, 'fn': fn, 'note': note})

    def c1(x):
        t = x.tokens()[0]
        with X.raw() as c:
            (a, _), (b, _) = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? AND preference_rank IN (1,2) ORDER BY preference_rank', (t,)).fetchall()
            c.execute('UPDATE BALLOT_RANKS SET preference_rank=2 WHERE ballot_token=? AND candidate_id=?', (t, a))
            c.execute('UPDATE BALLOT_RANKS SET preference_rank=1 WHERE ballot_token=? AND candidate_id=?', (t, b))
    add('C1', 'Swap the 1st and 2nd choice on one ballot', 'db', True, c1)

    def c2(x):
        t = x.tokens()[1]
        with X.raw() as c:
            used = {r[0] for r in c.execute('SELECT candidate_id FROM BALLOT_RANKS WHERE ballot_token=?', (t,))}
            c.execute('UPDATE BALLOT_RANKS SET candidate_id=? WHERE ballot_token=? AND preference_rank=1', (next(k for k in x.cands if k not in used), t))
    add('C2', 'Replace the first-choice candidate on one ballot', 'db', True, c2)

    def c3(x):
        with X.raw() as c:
            c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (x.tokens()[2],))
    add('C3', 'Delete one ballot', 'db', True, c3)

    def c4(x):
        with X.raw() as c:
            c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (x.tokens()[3],))
            pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=1 LIMIT 1', (x.e,)).fetchone()[0]
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=0 WHERE participation_id=?', (pid,))
    add('C4', 'Delete a ballot and clear a voted flag to hide the gap', 'db', True, c4)
    add('C5', 'Inject a ballot with no receipt', 'db', True, lambda x: x.inject(str(uuid.uuid4())))

    def c6(x):
        token = str(uuid.uuid4())
        x.inject(token)
        blocks = L.get_ledger()
        pstr = json.dumps(sorted([(cid, r) for r, cid in enumerate(x.cands[:3], start=1)], key=lambda z: z[1]), sort_keys=True)
        nb = {'index': len(blocks) + 1, 'timestamp': '2026-11-04T00:00:00', 'election_id': x.e, 'ballot_token': token,
              'vote_data_hash': hashlib.sha256(pstr.encode()).hexdigest(), 'prev_hash': blocks[-1]['curr_hash']}
        nb['curr_hash'] = hashlib.sha256(json.dumps(nb, sort_keys=True).encode()).hexdigest()
        L.save_ledger(blocks + [nb])
        with X.raw() as c:
            pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=0 LIMIT 1', (x.e,)).fetchone()[0]
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=1 WHERE participation_id=?', (pid,))
    add('C6', 'Ballot stuffing: inject ballot, forge a plain-hash receipt, set a voted flag', 'both', True, c6)

    def c7(x):
        b = L.get_ledger(); b[10]['vote_data_hash'] = 'f' * 64; L.save_ledger(b)
    add('C7', 'Edit a ledger block without repairing the chain', 'ledger', True, c7)

    def c8(x):
        b = L.get_ledger(); del b[15]; L.save_ledger(b)
    add('C8', 'Delete a block from the middle of the ledger', 'ledger', True, c8)
    add('C9', 'Truncate the last block of the ledger', 'ledger', True, lambda x: L.save_ledger(L.get_ledger()[:-1]))

    def c10(x):
        c1(x)
        t = x.tokens()[0]
        with X.raw() as c:
            votes = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? ORDER BY preference_rank', (t,)).fetchall()
        blocks = L.get_ledger()
        for b in blocks:
            if b['ballot_token'] == t:
                b['vote_data_hash'] = hashlib.sha256(json.dumps(votes, sort_keys=True).encode()).hexdigest()
        L.save_ledger(rebuild_chain(blocks, keyed=False))
    add('C10', 'Change a ballot and rebuild the whole chain (attacker has no key)', 'both', True, c10)

    def c11(x):
        with X.raw() as c:
            a, b = [r[0] for r in c.execute('SELECT name FROM CANDIDATE WHERE candidate_id IN (?,?) ORDER BY candidate_id', (x.cands[0], x.cands[1]))]
            c.execute('UPDATE CANDIDATE SET name=? WHERE candidate_id=?', (b, x.cands[0]))
            c.execute('UPDATE CANDIDATE SET name=? WHERE candidate_id=?', (a, x.cands[1]))
    add('C11', 'Swap two candidates\' names after voting', 'db', True, c11)

    def c12(x):
        with X.raw() as c:
            pid, reg = c.execute('SELECT participation_id, student_reg_no FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=1 LIMIT 1', (x.e,)).fetchone()
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=0 WHERE participation_id=?', (pid,))
        X.cast(X.voter_login(x.e, reg).json()['token'], x.cands[2:5])
    add('C12', 'Reset a voted flag, then let that voter cast a second ballot', 'api', True, c12)

    def ghost(x, reg='25BCE7777'):
        with X.raw() as c:
            c.execute('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?,?,?,0)', (x.e, reg, EC.hash_pw('x', iterations=1000)))
        X.cast(X.voter_login(x.e, reg, 'x').json()['token'], x.cands[:3])
    add('C13', 'Add a ghost voter to the roster and vote as them through the API', 'api', True, ghost)

    def c14(x):
        with X.raw() as c:
            c.execute('DELETE FROM VOTER_PARTICIPATION WHERE participation_id=(SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=0 LIMIT 1)', (x.e,))
    add('C14', 'Delete an unvoted voter from the roster (disenfranchise)', 'db', True, c14)

    def c15(x):
        with X.raw() as c:
            c.execute("UPDATE VOTER_PARTICIPATION SET student_reg_no='25BCE8888' WHERE participation_id=(SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=0 LIMIT 1)", (x.e,))
    add('C15', 'Rename an unvoted voter\'s registration number', 'db', True, c15)

    def c16(x):
        if Path(ROSTER).exists():
            Path(ROSTER).unlink()
        ghost(x, '25BCE7778')
    add('C16', 'Delete the roster seal, then add a ghost voter and vote', 'both', True, c16)

    def c17(x):
        with X.raw() as c:
            regs = [r[0] for r in c.execute('SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id=?', (x.e,))] + ['25BCE7779']
        Path(ROSTER).write_text(json.dumps({str(x.e): plain_roster_seal(x.e, regs)}), encoding='utf-8')
        ghost(x, '25BCE7779')
    add('C17', 'Forge the roster seal without the key, then add a ghost voter and vote', 'both', True, c17)
    add('C18', 'Wipe the whole ledger', 'ledger', True, lambda x: L.save_ledger([]))

    def c19(x):
        b = L.get_ledger(); dup = dict(b[4]); b.append(dup); L.save_ledger(b)
    add('C19', 'Append a copy of an existing ledger block (replay a receipt)', 'ledger', True, c19)

    def c20(x):
        b = L.get_ledger(); b[6], b[7] = b[7], b[6]; L.save_ledger(b)
    add('C20', 'Swap two ledger blocks (reorder)', 'ledger', True, c20)

    def c21(x):
        b = L.get_ledger(); b[12]['timestamp'] = '1999-01-01T00:00:00'; L.save_ledger(b)
    add('C21', 'Edit the timestamp of a ledger block', 'ledger', True, c21)

    def c22(x):
        c1(x)
        t = x.tokens()[0]
        with X.raw() as c:
            votes = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? ORDER BY preference_rank', (t,)).fetchall()
        blocks = L.get_ledger()
        for b in blocks:
            if b['ballot_token'] == t:
                b['vote_data_hash'] = hashlib.sha256(json.dumps(votes, sort_keys=True).encode()).hexdigest()
        L.save_ledger(blocks)   # edited block, chain not repaired
    add('C22', 'Change a ballot and its block hash but leave the chain unrepaired', 'both', True, c22)

    def c23(x):
        with X.raw() as c:
            c.execute("UPDATE CANDIDATE SET platform_statement='We will cancel all exams' WHERE candidate_id=?", (x.cands[0],))
    add('C23', 'Edit a candidate\'s platform statement', 'db', False, c23, 'Not covered by design: only the candidate id and name are sealed.')

    def c24(x):
        with X.raw() as c:
            c.execute("INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?, 'Late Entry', '')", (x.e,))
    add('C24', 'Add a candidate after voting', 'db', True, c24)

    def c25(x):
        with X.raw() as c:   # foreign keys are off on a default connection, so a candidate with ballots can be deleted
            c.execute('DELETE FROM CANDIDATE WHERE candidate_id=?', (x.cands[4],))
    add('C25', 'Delete a candidate row after voting (foreign keys off)', 'db', True, c25)

    def c26(x):
        with X.raw() as c:
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=1 WHERE participation_id=(SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=0 LIMIT 1)', (x.e,))
    add('C26', 'Mark an unvoted voter as voted with no ballot (disenfranchise)', 'db', True, c26)

    def c27(x):
        t = x.tokens()[5]
        with X.raw() as c:
            c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (t,))
            pid = c.execute('SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=? AND has_voted=1 LIMIT 1', (x.e,)).fetchone()[0]
            c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=0 WHERE participation_id=?', (pid,))
        L.save_ledger(rebuild_chain([b for b in L.get_ledger() if b['ballot_token'] != t], keyed=False))
    add('C27', 'Erase a vote completely: delete the ballot, its block and the flag, rebuild the chain', 'both', True, c27)

    def c28(x):
        c1(x)
        t = x.tokens()[0]
        with X.raw() as c:
            votes = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? ORDER BY preference_rank', (t,)).fetchall()
        blocks = L.get_ledger()
        for b in blocks:
            if b['ballot_token'] == t:
                b['vote_data_hash'] = hashlib.sha256(json.dumps(votes, sort_keys=True).encode()).hexdigest()
        L.save_ledger(rebuild_chain(blocks, keyed=True))
    add('C28', 'Insider WITH the ledger key: change a ballot and rebuild the chain with the key', 'key', False, c28, 'Outside the attacker model: needs the secret key.')

    def c29(x):
        ghost_tok = str(uuid.uuid4())
        with X.raw() as c:
            c.execute('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (?,?,?,1)', (x.e, '25BCE7780', 'x'))
            c.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,?,?)', [(ghost_tok, cid, x.e, r) for r, cid in enumerate(x.cands[:3], start=1)])
        blocks = L.get_ledger()
        payload = [(cid, r) for r, cid in enumerate(x.cands[:3], start=1)]
        new = L._seal(x.e, ghost_tok, payload, len(blocks) + 1, blocks[-1]['curr_hash'], EC.roster_hash(sqlite3.connect(X.DB), x.e), True)
        L.save_ledger(blocks + [new])
        EC.reseal_roster(x.e)
    add('C29', 'Insider WITH the key: add a ghost voter and ballot, forge the receipt, re-seal the roster', 'key', False, c29, 'Outside the attacker model: needs the secret key.')

    def c30(x):
        L.save_ledger(json.loads((x.early / L.LEDGER_FILE).read_text()))
    add('C30', 'Roll the ledger store back to an older backup', 'ledger', True, c30)

    def c31(x):
        shutil.copy(x.early / X.DB, X.DB)
    add('C31', 'Roll the election database back to an older backup', 'db', True, c31)
    return S


# ------------------------------------------------------------------ run everything in both key modes
def run_scenarios():
    out = {'scenarios': [], 'detectors': DETECTORS}
    ctxs = {m: Ctx(m) for m in ('keyed', 'unkeyed')}
    for m, x in ctxs.items():
        a0 = audit_full(x.e)
        assert not any(a0['detectors'].values()), f'{m} baseline election is not clean: {a0}'
        out.setdefault('clean_baseline', {})[m] = a0
    for sc in scenarios():
        rec = {'id': sc['id'], 'title': sc['title'], 'adversary': sc['adversary'], 'in_scope': sc['in_scope'], 'note': sc['note'], 'modes': {}}
        for m, x in ctxs.items():
            restore(x.base)
            L.LEDGER_KEY = KEY if m == 'keyed' else b''
            try:
                sc['fn'](x)
                err = None
            except Exception as ex:   # an attack script that cannot run is a finding, not a crash
                err = f'{type(ex).__name__}: {ex}'
            a = audit_full(x.e)
            a['error'] = err
            rec['modes'][m] = a
        k = rec['modes']['keyed']['detectors']
        print(f"  [{sc['id']:<3}] keyed: {','.join(d for d in AUTOMATIC if k[d]) or ('counters only' if k['counters'] else 'NONE'):<36} {sc['title'][:70]}")
        out['scenarios'].append(rec)
    for x in ctxs.values():
        restore(x.base)
    L.LEDGER_KEY = KEY
    return out


# ------------------------------------------------------------------ design profiles and ablations (computed from the matrix)
PROFILES = [
    # (id, label, key mode, detectors, note)
    ('P0', 'CRUD app: officer compares the counters', 'unkeyed', ['counters'], 'A typical student voting project: one ballot table and voted flags.'),
    ('P1', 'CRUD app + automatic count check', 'unkeyed', ['count_mismatch'], 'The same counters checked by code.'),
    ('P2', 'Plain hash chain only', 'unkeyed', ['chain'], 'SHA-256 chain with no key (VeriVote-class, and our Review 1 design).'),
    ('P3', 'Plain chain + receipt sweep (Review 2 design)', 'unkeyed', ['chain', 'modified', 'deleted'], 'Our own Review 2 design.'),
    ('P4', 'Plain chain + full sweep', 'unkeyed', ['chain', 'modified', 'deleted', 'injected', 'candidate_seal', 'count_mismatch', 'voter_seal'], 'Everything except the key.'),
    ('P5', 'Keyed chain only', 'keyed', ['chain'], 'HMAC chain, no sweep.'),
    ('P6', 'Keyed chain + sweep rules 1-5 (previous final design)', 'keyed', ['chain', 'modified', 'deleted', 'injected', 'candidate_seal', 'count_mismatch'], 'Our design before the roster seal was added.'),
    ('P7', 'PolyVote final (keyed chain + 6 sweep rules)', 'keyed', AUTOMATIC, 'Everything in this project.'),
]


def detected(rec, mode, dets):
    d = rec['modes'][mode]['detectors']
    return any(d[x] for x in dets)


def profile_table(res, scope_only=False):
    rows = []
    for pid, label, mode, dets, note in PROFILES:
        sc = [r for r in res['scenarios'] if r['in_scope'] or not scope_only]
        hit = [r['id'] for r in sc if detected(r, mode, dets)]
        rows.append({'id': pid, 'label': label, 'mode': mode, 'detectors': dets, 'note': note,
                     'detected': len(hit), 'of': len(sc), 'rate': round(100 * len(hit) / len(sc), 1), 'ids': hit,
                     'missed': [r['id'] for r in sc if r['id'] not in hit]})
    return rows


def ablation(res):
    full = [r for r in res['scenarios']]
    base = {r['id'] for r in full if detected(r, 'keyed', AUTOMATIC)}
    out = {'leave_one_out': [], 'single': [], 'cumulative': [], 'unkeyed_final': None}
    for d in AUTOMATIC:
        rest = [x for x in AUTOMATIC if x != d]
        lost = sorted(base - {r['id'] for r in full if detected(r, 'keyed', rest)}, key=lambda s: int(s[1:]))
        out['leave_one_out'].append({'removed': d, 'detected': len(base) - len(lost), 'of': len(full), 'lost': lost})
    for d in AUTOMATIC:
        hit = sorted({r['id'] for r in full if detected(r, 'keyed', [d])}, key=lambda s: int(s[1:]))
        out['single'].append({'detector': d, 'detected': len(hit), 'of': len(full), 'ids': hit})
    order = ['counters', 'chain', 'modified', 'deleted', 'injected', 'count_mismatch', 'candidate_seal', 'voter_seal']
    have = []
    for d in order:
        have.append(d)
        out['cumulative'].append({'added': d, 'detected': sum(1 for r in full if detected(r, 'keyed', have)), 'of': len(full)})
    unk = {r['id'] for r in full if detected(r, 'unkeyed', AUTOMATIC)}
    out['unkeyed_final'] = {'detected': len(unk), 'of': len(full), 'lost_vs_keyed': sorted(base - unk, key=lambda s: int(s[1:]))}
    return out


# ------------------------------------------------------------------ the append-only trigger class
def run_trigger_class(res):
    """Append-only triggers on the ballot table (the DB-level control some systems rely on), against a writer who cannot drop them."""
    x = Ctx('keyed')
    L.LEDGER_KEY = KEY

    def install():
        with X.raw() as c:
            c.executescript('''
                CREATE TRIGGER IF NOT EXISTS ev_no_update BEFORE UPDATE ON BALLOT_RANKS BEGIN SELECT RAISE(ABORT, 'append-only table'); END;
                CREATE TRIGGER IF NOT EXISTS ev_no_delete BEFORE DELETE ON BALLOT_RANKS BEGIN SELECT RAISE(ABORT, 'append-only table'); END;''')
    out = []
    for sc in scenarios():
        restore(x.base)
        install()
        prevented, err = False, None
        try:
            sc['fn'](x)
        except sqlite3.Error as ex:
            import gc
            gc.collect()
            prevented, err = True, str(ex)
        except Exception as ex:
            err = f'{type(ex).__name__}: {ex}'
        a = audit_full(x.e)
        out.append({'id': sc['id'], 'prevented': prevented, 'counters': a['detectors']['counters'], 'detected_by_counters_only': a['detectors']['counters'] and not prevented, 'error': err})
    restore(x.base)
    stopped = [r['id'] for r in out if r['prevented']]
    counters = [r['id'] for r in out if not r['prevented'] and r['counters']]
    return {'prevented': stopped, 'counters_only': counters, 'neither': [r['id'] for r in out if r['id'] not in stopped + counters],
            'total': len(out), 'rows': out}


def validate_emulation(res):
    """Compare the emulated Review 2 design (profile P3) with the real Review 2 code measured earlier on C1-C13."""
    p = HERE.parent / 'results' / 'baseline_r1.json'
    if not p.exists():
        return None
    real = {r['id']: r['outcome'] for r in json.loads(p.read_text(encoding='utf-8'))['tamper']}
    rows, agree = [], 0
    for r in res['scenarios']:
        if r['id'] in real:
            emu = 'detected' if detected(r, 'unkeyed', ['chain', 'modified', 'deleted']) else ('detected_manual_only' if r['modes']['unkeyed']['detectors']['counters'] else 'undetected')
            same = emu == real[r['id']]
            agree += same
            rows.append({'id': r['id'], 'real_review2': real[r['id']], 'emulated': emu, 'agree': same})
    return {'rows': rows, 'agree': agree, 'of': len(rows)}
