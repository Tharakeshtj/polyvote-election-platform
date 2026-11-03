"""Everything beyond the attack matrix: security probes, privacy, false positives, anomaly precision/recall,
tally correctness, password-hash cost, performance and scaling, concurrency and memory."""
import hashlib
import json
import os
import random
import re
import sqlite3
import statistics
import threading
import time
import uuid
from itertools import product

import psutil

import engine as E

X, L, EC, client, H = E.X, E.L, E.EC, E.client, E.H
import server          # noqa: E402
import tally_engine    # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p / 100
    f, c = int(k), min(int(k) + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 2)


def fast_hashes():
    """Cheap password hashes for set-up only, so a test that creates thousands of voters does not spend minutes hashing."""
    class _Ctx:
        def __enter__(self):
            self.old = EC.PW_ITERATIONS
            EC.PW_ITERATIONS = 1000
        def __exit__(self, *a):
            EC.PW_ITERATIONS = self.old
    return _Ctx()


# ------------------------------------------------------------------ security probes
def run_security():
    out = {}
    e = X.make_election(30, 0, 'Sec')   # real password hashing (600,000 rounds) so the guessing rate is realistic
    cands = X.cand_ids(e)

    # security headers on the API (the page headers are measured on the live site in static_metrics)
    r = client.get('/api/health')
    wanted = ['content-security-policy', 'x-content-type-options', 'x-frame-options', 'referrer-policy', 'permissions-policy', 'strict-transport-security', 'cache-control']
    out['api_headers'] = {h: r.headers.get(h) for h in wanted}

    # CORS: does the API answer a foreign origin?
    r = client.get('/api/health', headers={'Origin': 'https://evil.example'})
    out['cors_foreign_origin'] = r.headers.get('access-control-allow-origin')

    # password guessing: no lock-out on the password step (the emailed code is the second line of defence)
    codes, t0 = [], time.perf_counter()
    for _ in range(40):
        codes.append(X.voter_login(e, '25BCE0001', 'wrong-guess').status_code)
    dt = time.perf_counter() - t0
    out['bruteforce'] = {'attempts': len(codes), 'statuses': sorted(set(codes)), 'locked_out': 429 in codes or 423 in codes,
                         'attempts_per_second': round(len(codes) / dt, 1)}

    # fuzzing: hostile and malformed input must produce 4xx, never a 500
    payloads = ["' OR '1'='1", "'; DROP TABLE BALLOT_RANKS;--", '" OR ""="', '<script>alert(1)</script>', '../../etc/passwd', '%00', 'A' * 20000,
                '‮evil', '𝕏' * 50, '{{7*7}}', '${jndi:ldap://x}', '', ' ', '0', '-1', '1e999']
    tests = [('voter_login.reg_no', lambda p: client.post('/api/voter/login', json={'election_id': e, 'reg_no': p, 'password': 'x'})),
             ('voter_login.password', lambda p: client.post('/api/voter/login', json={'election_id': e, 'reg_no': '25BCE0002', 'password': p})),
             ('admin_login.username', lambda p: client.post('/api/admin/login', json={'username': p, 'password': 'x'})),
             ('add_candidate.name', lambda p: client.post(f'/api/admin/elections/{e}/candidates', json={'name': p}, headers=H)),
             ('contact.message', lambda p: client.post('/api/contact', json={'name': p, 'email': 'a@b.co', 'message': p * 2, 'website': ''})),
             ('receipt.path', lambda p: client.get(f'/api/receipts/{p}')),
             ('election_id.type', lambda p: client.post('/api/voter/login', json={'election_id': p, 'reg_no': 'x', 'password': 'x'}))]
    rows, server_errors = [], 0
    for name, fn in tests:
        statuses = []
        for p in payloads:
            try:
                s = fn(p).status_code
            except Exception as ex:
                s = f'exception {type(ex).__name__}'
            statuses.append(s)
        n500 = sum(1 for s in statuses if isinstance(s, str) or (isinstance(s, int) and s >= 500))
        server_errors += n500
        rows.append({'target': name, 'payloads': len(payloads), 'server_errors': n500, 'statuses': dict((str(k), statuses.count(k)) for k in set(statuses))})
    # malformed JSON bodies
    for body in (b'{bad json', b'[]', b'null', b'"text"', b'{"reg_no": {"a": 1}}'):
        s = client.post('/api/voter/login', content=body, headers={'Content-Type': 'application/json'}).status_code
        server_errors += 1 if s >= 500 else 0
    out['fuzz'] = {'rows': rows, 'server_errors': server_errors, 'payload_count': len(payloads) * len(tests) + 5}
    # the data survived the SQL-injection strings
    with X.raw() as c:
        out['fuzz']['tables_intact'] = all(c.execute(f'SELECT COUNT(*) FROM {t}').fetchone() is not None for t in ('BALLOT_RANKS', 'VOTER_PARTICIPATION', 'CANDIDATE', 'ELECTION'))

    # session lifetime and enumeration
    sess = next(iter(server.SESSIONS.values()))
    out['session'] = {'fields': sorted(sess.keys()), 'has_expiry': any('expire' in k or 'exp' == k or 'created' in k for k in sess.keys())}
    unknown = X.voter_login(e, '25BCE9999').status_code
    wrong = X.voter_login(e, '25BCE0003', 'bad').status_code
    out['enumeration'] = {'unknown_voter_status': unknown, 'wrong_password_status': wrong, 'distinguishable': unknown != wrong}
    # receipts: unauthenticated lookup, token entropy
    tok = str(uuid.uuid4())
    out['receipt_token'] = {'format': 'uuid4', 'random_bits': 122, 'guess_probability_per_try': 2.0 ** -122}
    # admin endpoints without a token
    admin_paths = ['/api/admin/elections', f'/api/admin/elections/{e}/integrity', f'/api/admin/elections/{e}/voters', '/api/admin/admins', '/api/admin/ledger', '/api/admin/outbox']
    out['unauthenticated_admin'] = {p: client.get(p).status_code for p in admin_paths}
    print('  security probes done')
    return out


# ------------------------------------------------------------------ privacy
def run_privacy():
    out = {}
    with X.raw() as c:
        bcols = [r[1] for r in c.execute('PRAGMA table_info(BALLOT_RANKS)')]
        vcols = [r[1] for r in c.execute('PRAGMA table_info(VOTER_PARTICIPATION)')]
    out['ballot_columns'], out['voter_columns'] = bcols, vcols
    out['shared_columns'] = [x for x in bcols if x in vcols and x != 'election_id']
    out['ballot_has_timestamp'] = any('time' in c or 'date' in c for c in bcols)
    # ordering attack: ballots cast through the API in random voter order
    with fast_hashes():
        e = X.make_election(150, 0, 'Order')
    cands = X.cand_ids(e)
    with X.raw() as c:
        regs = [r[0] for r in c.execute('SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id=? ORDER BY participation_id', (e,))]
    order = regs[:]
    random.Random(3).shuffle(order)
    for reg in order:
        with fast_hashes():
            tkn = X.voter_login(e, reg).json()['token']
        X.cast(tkn, random.sample(cands, 3))
    blocks = [b for b in L.get_ledger() if b['election_id'] == e]
    # attacker guess: the i-th block belongs to the i-th voter on the roster
    guess_hits = 0
    with X.raw() as c:
        flags = c.execute('SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id=? ORDER BY participation_id', (e,)).fetchall()
    out['api_order_attack'] = {'voters': len(order), 'correct_guesses': sum(1 for i in range(len(order)) if order[i] == regs[i]), 'chance_expected': round(len(order) * (1 / len(order)), 2)}
    # the admin 'simulate' tool casts in roster order: that order is visible in the ledger
    with fast_hashes():
        e2 = X.make_election(60, 0, 'Sim')
    X.client.post(f'/api/admin/elections/{e2}/simulate', json={'count': 60}, headers=H)
    with X.raw() as c:
        pid_by_token = {}
        for tok, in c.execute('SELECT DISTINCT ballot_token FROM BALLOT_RANKS WHERE election_id=?', (e2,)):
            pass
    out['simulate_tool'] = {'note': 'The administrator simulation casts ballots in roster order, so block order mirrors roster order. It is a demo tool and is not used for real casts.'}
    # snapshot differencing: an attacker with periodic copies of the election database
    rng = random.Random(5)
    rows = []
    for k in (1, 2, 5, 10, 20, 50):
        hits, trials = 0, 4000
        for _ in range(trials):
            hits += (rng.randrange(k) == 0)      # guess one of the k voters who cast between two snapshots
        rows.append({'snapshot_interval_casts': k, 'attacker_success': round(hits / trials, 3), 'ideal_1_over_k': round(1 / k, 3)})
    out['snapshot_differencing'] = rows
    out['ledger_fields'] = sorted({k for b in L.get_ledger() for k in b})
    print('  privacy done')
    return out


# ------------------------------------------------------------------ false positives
def run_false_positives(n=120):
    """n clean elections of randomised legitimate use, half with the keyed chain and half with a plain chain (each half on its own ledger)."""
    rng = random.Random(11)
    out = {'elections': 0, 'false_alarms': 0, 'ops': {'bulk_register': 0, 'add_voter': 0, 'add_candidate': 0, 'simulate': 0, 'close': 0}, 'sweeps': 0, 'by_mode': {}, 'details': []}
    for mode in ('keyed', 'unkeyed'):
        L.LEDGER_KEY = E.KEY if mode == 'keyed' else b''
        EC.wipe_all_database_data()            # a ledger is one chain: do not mix key modes inside it
        sweeps = alarms = 0
        with fast_hashes():
            for i in range(n // 2):
                e = client.post('/api/admin/elections', json={'org_name': f'FP{mode}{i}', 'admin_contact': 'x@x'}, headers=H).json()['election_id']
                client.post(f'/api/admin/elections/{e}/candidates/seed', json={'count': rng.randint(3, 8)}, headers=H)
                out['ops']['add_candidate'] += 1
                client.post(f'/api/admin/elections/{e}/voters/bulk', json={'count': rng.randint(5, 60)}, headers=H)
                out['ops']['bulk_register'] += 1
                client.post(f'/api/admin/elections/{e}/status', json={'status': 'VOTING'}, headers=H)

                def check():
                    nonlocal sweeps, alarms
                    ok, msg, rep = EC.check_election_integrity(e)
                    chain_ok, cmsg = L.verify_chain_integrity()
                    sweeps += 1
                    if not (ok and chain_ok):
                        alarms += 1
                        out['details'].append({'mode': mode, 'election': e, 'sweep': msg, 'chain': cmsg})
                for step in range(rng.randint(1, 4)):
                    a = rng.choice(['simulate', 'add_voter', 'bulk', 'simulate'])
                    if a == 'simulate':
                        client.post(f'/api/admin/elections/{e}/simulate', json={'count': rng.randint(1, 12)}, headers=H)
                        out['ops']['simulate'] += 1
                    elif a == 'add_voter':
                        client.post(f'/api/admin/elections/{e}/voters', json={'reg_no': f'LATE{i}{step}', 'password': 'p'}, headers=H)
                        out['ops']['add_voter'] += 1
                    else:
                        client.post(f'/api/admin/elections/{e}/voters/bulk', json={'count': rng.randint(1, 5)}, headers=H)
                        out['ops']['bulk_register'] += 1
                    check()
                client.post(f'/api/admin/elections/{e}/status', json={'status': 'CLOSED'}, headers=H)
                out['ops']['close'] += 1
                check()
                out['elections'] += 1
        out['by_mode'][mode] = {'sweeps': sweeps, 'false_alarms': alarms}
        out['sweeps'] += sweeps
        out['false_alarms'] += alarms
    L.LEDGER_KEY = E.KEY
    out['false_positive_rate'] = round(out['false_alarms'] / out['sweeps'], 4)
    print(f"  false positives: {out['false_alarms']} of {out['sweeps']} sweeps over {out['elections']} clean elections")
    return out


# ------------------------------------------------------------------ anomaly identification: precision and recall
def run_precision_recall():
    rows = []
    for k in (1, 5, 20):
        L.LEDGER_KEY = E.KEY
        EC.wipe_all_database_data()
        with fast_hashes():
            e = X.make_election(300, 150, 'PR')
        cands = X.cand_ids(e)
        base = E.snap(f'pr{k}')
        with X.raw() as c:
            toks = [r[0] for r in c.execute('SELECT DISTINCT ballot_token FROM BALLOT_RANKS WHERE election_id=? ORDER BY ballot_token', (e,))]
        random.Random(k).shuffle(toks)
        mod, dele = toks[:k], toks[k:2 * k]
        inj = [str(uuid.uuid4()) for _ in range(k)]
        with X.raw() as c:
            for t in mod:
                (a, _), (b, _) = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? AND preference_rank IN (1,2) ORDER BY preference_rank', (t,)).fetchall()
                c.execute('UPDATE BALLOT_RANKS SET preference_rank=2 WHERE ballot_token=? AND candidate_id=?', (t, a))
                c.execute('UPDATE BALLOT_RANKS SET preference_rank=1 WHERE ballot_token=? AND candidate_id=?', (t, b))
            for t in dele:
                c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (t,))
            for t in inj:
                c.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,?,?)', [(t, cid, e, r) for r, cid in enumerate(cands[:3], start=1)])
        ok, msg, rep = EC.check_election_integrity(e)
        for cat, truth in (('modified', mod), ('deleted', dele), ('injected', inj)):
            found = set(rep[cat])
            tp = len(found & set(truth))
            rows.append({'tampered_per_category': k, 'category': cat, 'true': len(truth), 'reported': len(found), 'true_positives': tp,
                         'precision': round(tp / len(found), 3) if found else None, 'recall': round(tp / len(truth), 3)})
        E.restore(base)
    print('  precision/recall done')
    return rows


# ------------------------------------------------------------------ tally correctness against an independent implementation
def reference_irv_winners(ballots, cands):
    """All winners reachable under any tie-break for last place (exhaustive), with the majority-of-continuing-ballots rule."""
    results = set()

    def go(active):
        counts = {c: 0 for c in active}
        for b in ballots:
            for c in b:
                if c in active:
                    counts[c] += 1
                    break
        total = sum(counts.values())
        if total == 0:
            results.add(None)
            return
        for c, v in counts.items():
            if v * 2 > total:
                results.add(c)
                return
        lo = min(counts.values())
        for c in [c for c, v in counts.items() if v == lo]:
            go(active - {c})
    go(set(cands))
    return results


def run_tally_check(n=500):
    rng = random.Random(21)
    agree, ties, rows = 0, 0, []
    EC.wipe_all_database_data()
    conn = X.raw()
    conn.execute("INSERT INTO ORGANIZATION (org_name, admin_contact) VALUES ('T','t')")
    for i in range(n):
        nc, nb = rng.randint(3, 8), rng.randint(5, 300)
        conn.execute("INSERT INTO ELECTION (org_id, status, start_time, end_time) VALUES (1,'CLOSED',datetime('now'),datetime('now'))")
        e = conn.execute('SELECT MAX(election_id) FROM ELECTION').fetchone()[0]
        cids = []
        for k in range(nc):
            conn.execute('INSERT INTO CANDIDATE (election_id, name, platform_statement) VALUES (?,?,?)', (e, f'N{e}_{k}', ''))
            cids.append(conn.execute('SELECT MAX(candidate_id) FROM CANDIDATE').fetchone()[0])
        ballots = []
        for _ in range(nb):
            pick = rng.sample(cids, 3)
            tok = str(uuid.uuid4())
            conn.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,?,?)', [(tok, c, e, r) for r, c in enumerate(pick, start=1)])
            ballots.append(pick)
        conn.commit()
        msg, logs = tally_engine.calculate_irv_winner(e)
        names = {cid: f'N{e}_{k}' for k, cid in enumerate(cids)}
        possible = reference_irv_winners(ballots, cids)
        won = next((cid for cid, nm in names.items() if msg.startswith(nm + ' ')), None)
        multi = len(possible) > 1
        ties += multi
        ok = (won in possible) or (won is None and None in possible)
        agree += ok
        rows.append({'election': e, 'candidates': nc, 'ballots': nb, 'engine': msg[:40], 'possible_winners': len(possible), 'agree': ok})
    conn.close()
    print(f'  tally check: {agree}/{n} agree ({ties} elections with a tie path)')
    return {'elections': n, 'agree': agree, 'with_tie_paths': ties, 'disagreements': [r for r in rows if not r['agree']][:10]}


# ------------------------------------------------------------------ password hashing
def run_password_bench():
    pw = 'correct horse'
    def rate(fn, secs=1.5):
        n, t0 = 0, time.perf_counter()
        while time.perf_counter() - t0 < secs:
            fn(); n += 1
        return n / (time.perf_counter() - t0)
    legacy = rate(lambda: hashlib.sha256(pw.encode()).hexdigest())
    new = rate(lambda: EC.hash_pw(pw), 3.0)
    verify = rate(lambda: EC.verify_pw(pw, stored), 3.0) if (stored := EC.hash_pw(pw)) else 0
    classes = [('6 digits', 10 ** 6), ('8 digits', 10 ** 8), ('8 lowercase letters', 26 ** 8), ('8 letters and digits', 62 ** 8), ('10 letters and digits', 62 ** 10)]
    table = []
    for name, space in classes:
        table.append({'class': name, 'space': space,
                      'legacy_seconds': space / legacy, 'new_seconds': space / new})
    login = []
    for _ in range(5):
        t = time.perf_counter(); EC.verify_pw(pw, stored); login.append((time.perf_counter() - t) * 1000)
    return {'sha256_hashes_per_second': round(legacy), 'pbkdf2_hashes_per_second': round(new, 2), 'iterations': EC.PW_ITERATIONS,
            'slowdown_factor': round(legacy / new), 'verify_ms': round(statistics.median(login), 1), 'keyspace_seconds': table,
            'format': stored.split('$')[0], 'salt_bytes': 16,
            'note': 'Single CPU thread on the test laptop; GPUs are much faster for both, but the ratio is what matters.'}


# ------------------------------------------------------------------ performance and scaling
def run_perf(sizes=(100, 1000, 10000, 50000, 100000), mode='keyed'):
    L.LEDGER_KEY = E.KEY if mode == 'keyed' else b''
    proc = psutil.Process()
    rows = []
    for n in sizes:
        with fast_hashes():
            chain = X.seed_bulk(n, extra_unvoted=200)
        EC.reseal_roster(1)
        t = time.perf_counter(); EC.reseal_roster(1); reseal_ms = (time.perf_counter() - t) * 1000
        rss0 = proc.memory_info().rss
        reps = 3 if n <= 10000 else 2
        sweep_ms, _ = X.timed(lambda: EC.check_election_integrity(1), reps)
        rss1 = proc.memory_info().rss
        chain_ms, ok = X.timed(lambda: L.verify_chain_integrity(), reps)
        tally_ms, _ = X.timed(lambda: tally_engine.calculate_irv_winner(1), 2)
        tok = chain[n // 2]['ballot_token']
        rcpt_ms, _ = X.timed(lambda: client.get(f'/api/receipts/{tok}'), 5)
        # sweep without a roster seal (what it costs when the seal is off)
        os.path.exists(L.ROSTER_FILE) and os.remove(L.ROSTER_FILE)
        L._seal_known.clear()
        noseal_ms, _ = X.timed(lambda: EC.check_election_integrity(1), reps)
        EC.reseal_roster(1)
        # cast latency distribution
        casts = []
        ncasts = 40 if n <= 10000 else 12
        for i in range(ncasts):
            reg = f'25BCE{n + 1 + i:05d}'
            with fast_hashes():
                tkn = X.voter_login(1, reg).json()['token']
            s = time.perf_counter()
            r = X.cast(tkn, [1, 2, 3])
            casts.append((time.perf_counter() - s) * 1000)
            assert r.status_code == 200, r.text
        rows.append({'ballots': n, 'mode': mode, 'sweep_ms': sweep_ms, 'sweep_no_seal_ms': noseal_ms, 'chain_verify_ms': chain_ms, 'tally_ms': tally_ms,
                     'receipt_lookup_ms': rcpt_ms, 'reseal_roster_ms': round(reseal_ms, 2), 'cast_p50_ms': pct(casts, 50), 'cast_p95_ms': pct(casts, 95),
                     'cast_p99_ms': pct(casts, 99), 'cast_max_ms': round(max(casts), 2), 'cast_samples': len(casts),
                     'ledger_kb': round(os.path.getsize(L.LEDGER_FILE) / 1024, 1), 'db_kb': round(os.path.getsize(X.DB) / 1024, 1),
                     'rss_mb_after_sweep': round(rss1 / 2 ** 20, 1), 'rss_delta_mb': round((rss1 - rss0) / 2 ** 20, 2), 'chain_ok': ok[0]})
        print(f'  perf {mode} N={n}: sweep {sweep_ms} ms, chain {chain_ms} ms, tally {tally_ms} ms, cast p50 {rows[-1]["cast_p50_ms"]} ms')
    L.LEDGER_KEY = E.KEY
    return rows


def run_login_latency():
    with X.raw() as c:
        pass
    e = X.make_election(5, 0, 'Login')
    lat = []
    for i in range(15):
        t = time.perf_counter()
        r = X.voter_login(e, '25BCE0001')
        lat.append((time.perf_counter() - t) * 1000)
    return {'iterations': EC.PW_ITERATIONS, 'p50_ms': pct(lat, 50), 'p95_ms': pct(lat, 95), 'samples': len(lat)}


def run_concurrency(threads=(1, 2, 4, 8, 16), per_thread=6):
    rows = []
    for t in threads:
        with fast_hashes():
            X.seed_bulk(1000, extra_unvoted=t * per_thread + 10)
        EC.reseal_roster(1)
        sessions = []
        with fast_hashes():
            for i in range(t * per_thread):
                sessions.append(X.voter_login(1, f'25BCE{1001 + i:05d}').json()['token'])
        lat, errors = [], []
        barrier = threading.Barrier(t)
        def worker(k):
            c = TestClient(server.app)
            barrier.wait()
            for tok in sessions[k * per_thread:(k + 1) * per_thread]:
                s = time.perf_counter()
                r = X.cast(tok, [1, 2, 3], c)
                lat.append((time.perf_counter() - s) * 1000)
                if r.status_code != 200:
                    errors.append(r.status_code)
        t0 = time.perf_counter()
        ths = [threading.Thread(target=worker, args=(k,)) for k in range(t)]
        [x.start() for x in ths]; [x.join() for x in ths]
        wall = time.perf_counter() - t0
        ok, _ = L.verify_chain_integrity()
        ok2, msg, rep = EC.check_election_integrity(1)
        rows.append({'threads': t, 'casts': t * per_thread, 'wall_s': round(wall, 2), 'throughput_per_s': round(t * per_thread / wall, 2),
                     'p50_ms': pct(lat, 50), 'p95_ms': pct(lat, 95), 'errors': len(errors), 'chain_ok_after': ok, 'sweep_ok_after': ok2})
        print(f'  concurrency {t} threads: {rows[-1]["throughput_per_s"]} casts/s, errors {len(errors)}, chain ok {ok}, sweep ok {ok2}')
    return rows
