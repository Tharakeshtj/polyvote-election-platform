"""Screenshots of the real application under attack, plus accessibility and page-load measurements.

Starts a throwaway copy of the app (demo seed, keyed ledger) on port 8041, applies each attack to ITS files, runs the sweep in the
browser and saves the result. Writes docs/evaluation/screenshots/*.png and experiments/results/full/ui.json.

    python experiments/full_eval/shots.py
"""
import hashlib
import json
import os
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'evaluation' / 'screenshots'
RES = ROOT / 'experiments' / 'results' / 'full'
OUT.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)
PORT = 8041
BASE = f'http://127.0.0.1:{PORT}'
KEY = 'experiment-only-secret'
SB = Path(tempfile.mkdtemp(prefix='polyvote_shots_'))
IGNORE = shutil.ignore_patterns('.git', 'node_modules', '__pycache__', 'Sample PolyVote', 'PSOSM_Exam_Prep', 'docs', 'experiments', '.env', '*.db', '*.log', 'mongo_audit_ledger.json', 'roster_seals.json')
shutil.copytree(ROOT, SB / 'app', ignore=IGNORE)
APP = SB / 'app'
DB, LEDGER, SEALS = APP / 'polyvote_relational.db', APP / 'mongo_audit_ledger.json', APP / 'roster_seals.json'

env = dict(os.environ, HOSTED_DEMO='true', OTP_REQUIRED='', OTP_DEMO_HINT='', LEDGER_KEY=KEY, PASSWORD_HASH_ITERATIONS='1000', MONGO_URI='', ADMIN_PASSWORD='')
server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'server:app', '--port', str(PORT)], cwd=APP, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        urllib.request.urlopen(BASE + '/api/health', timeout=2)
        break
    except Exception:
        time.sleep(1)
else:
    server.kill()
    sys.exit('server did not start')

BASEDIR = SB / 'base'
BASEDIR.mkdir()
for f in (DB, LEDGER, SEALS):
    shutil.copy(f, BASEDIR / f.name)


def restore():
    for f in (DB, LEDGER, SEALS):
        if (BASEDIR / f.name).exists():
            shutil.copy(BASEDIR / f.name, f)
        elif f.exists():
            f.unlink()


def call(path, method='GET', body=None, token=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type': 'application/json', **({'Authorization': 'Bearer ' + token} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b'null')
    except urllib.error.HTTPError as e:
        return {'error': e.code}


def db():
    return sqlite3.connect(DB)


def tokens():
    with db() as c:
        return [r[0] for r in c.execute('SELECT DISTINCT ballot_token FROM BALLOT_RANKS WHERE election_id=1 ORDER BY ballot_token')]


def cands():
    with db() as c:
        return [r[0] for r in c.execute('SELECT candidate_id FROM CANDIDATE WHERE election_id=1 ORDER BY candidate_id')]


def blocks():
    return json.loads(LEDGER.read_text())


def save_blocks(b):
    LEDGER.write_text(json.dumps(b, indent=4))


def rebuild(b):
    prev, out = '0' * 64, []
    for i, x in enumerate(b, 1):
        nb = {k: v for k, v in x.items() if k != 'curr_hash'}
        nb['index'], nb['prev_hash'] = i, prev
        nb['curr_hash'] = hashlib.sha256(json.dumps(nb, sort_keys=True).encode()).hexdigest()
        out.append(nb)
        prev = nb['curr_hash']
    return out


def ghost(reg):
    with db() as c:
        c.execute('INSERT INTO VOTER_PARTICIPATION (election_id, student_reg_no, password_hash, has_voted) VALUES (1,?,?,0)', (reg, 'x'))
    # sign in as the ghost through the API: its stored hash must verify, so store a real one
    import importlib
    sys.path.insert(0, str(APP))
    ec = importlib.import_module('election_core')
    with db() as c:
        c.execute('UPDATE VOTER_PARTICIPATION SET password_hash=? WHERE student_reg_no=?', (ec.hash_pw('ghostpw', iterations=1000), reg))
    t = call('/api/voter/login', 'POST', {'election_id': 1, 'reg_no': reg, 'password': 'ghostpw'})['token']
    call('/api/voter/ballot', 'POST', {'ranking': cands()[:3]}, t)


# ---------------------------------------------------------------- the attacks to photograph
def m_c1():
    t = tokens()[0]
    with db() as c:
        (a, _), (b, _) = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? AND preference_rank IN (1,2) ORDER BY preference_rank', (t,)).fetchall()
        c.execute('UPDATE BALLOT_RANKS SET preference_rank=2 WHERE ballot_token=? AND candidate_id=?', (t, a))
        c.execute('UPDATE BALLOT_RANKS SET preference_rank=1 WHERE ballot_token=? AND candidate_id=?', (t, b))


def m_c3():
    with db() as c:
        c.execute('DELETE FROM BALLOT_RANKS WHERE ballot_token=?', (tokens()[2],))


def m_c5():
    t = str(uuid.uuid4())
    with db() as c:
        c.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,1,?)', [(t, cid, r) for r, cid in enumerate(cands()[:3], 1)])


def m_c6():
    t = str(uuid.uuid4())
    m_c5_with(t)
    b = blocks()
    nb = {'index': len(b) + 1, 'timestamp': '2026-11-04T00:00:00', 'election_id': 1, 'ballot_token': t,
          'vote_data_hash': hashlib.sha256(json.dumps(sorted([(cid, r) for r, cid in enumerate(cands()[:3], 1)], key=lambda z: z[1]), sort_keys=True).encode()).hexdigest(), 'prev_hash': b[-1]['curr_hash']}
    nb['curr_hash'] = hashlib.sha256(json.dumps(nb, sort_keys=True).encode()).hexdigest()
    save_blocks(b + [nb])


def m_c5_with(t):
    with db() as c:
        c.executemany('INSERT INTO BALLOT_RANKS VALUES (?,?,1,?)', [(t, cid, r) for r, cid in enumerate(cands()[:3], 1)])


def m_c7():
    b = blocks(); b[10]['vote_data_hash'] = 'f' * 64; save_blocks(b)


def m_c9():
    save_blocks(blocks()[:-1])


def m_c10():
    m_c1()
    t = tokens()[0]
    with db() as c:
        votes = c.execute('SELECT candidate_id, preference_rank FROM BALLOT_RANKS WHERE ballot_token=? ORDER BY preference_rank', (t,)).fetchall()
    b = blocks()
    for x in b:
        if x['ballot_token'] == t:
            x['vote_data_hash'] = hashlib.sha256(json.dumps(votes, sort_keys=True).encode()).hexdigest()
    save_blocks(rebuild(b))


def m_c11():
    cs = cands()
    with db() as c:
        a, b = [r[0] for r in c.execute('SELECT name FROM CANDIDATE WHERE candidate_id IN (?,?) ORDER BY candidate_id', (cs[0], cs[1]))]
        c.execute('UPDATE CANDIDATE SET name=? WHERE candidate_id=?', (b, cs[0]))
        c.execute('UPDATE CANDIDATE SET name=? WHERE candidate_id=?', (a, cs[1]))


def m_c13():
    ghost('25BCE7777')


def m_c14():
    with db() as c:
        c.execute('DELETE FROM VOTER_PARTICIPATION WHERE participation_id=(SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=1 AND has_voted=0 LIMIT 1)')


def m_c16():
    if SEALS.exists():
        SEALS.unlink()
    ghost('25BCE7778')


def m_c17():
    with db() as c:
        regs = [r[0] for r in c.execute('SELECT student_reg_no FROM VOTER_PARTICIPATION WHERE election_id=1')] + ['25BCE7779']
    tags = sorted({hashlib.sha256(f'voter|1|{r}'.encode()).hexdigest()[:32] for r in regs})
    rec = {'election_id': 1, 'version': 99, 'count': len(tags), 'tags': tags, 'updated': '2026-11-04T00:00:00'}
    rec['signature'] = hashlib.sha256(b'roster|' + json.dumps(rec, sort_keys=True).encode()).hexdigest()
    SEALS.write_text(json.dumps({'1': rec}))
    ghost('25BCE7779')


def m_c18():
    save_blocks([])


def m_c26():
    with db() as c:
        c.execute('UPDATE VOTER_PARTICIPATION SET has_voted=1 WHERE participation_id=(SELECT participation_id FROM VOTER_PARTICIPATION WHERE election_id=1 AND has_voted=0 LIMIT 1)')


SHOTS = [
    ('S00', 'Clean election: sweep passes and the chain is intact', lambda: None, True),
    ('C1', 'C1 Swap the 1st and 2nd choice on one ballot', m_c1, False),
    ('C3', 'C3 Delete one ballot', m_c3, False),
    ('C5', 'C5 Inject a ballot with no receipt', m_c5, False),
    ('C6', 'C6 Ballot stuffing with a forged plain-hash receipt', m_c6, True),
    ('C7', 'C7 Edit a ledger block', m_c7, True),
    ('C9', 'C9 Truncate the last ledger block', m_c9, False),
    ('C10', 'C10 Rebuild the whole chain without the key', m_c10, True),
    ('C11', 'C11 Swap two candidates\' names after voting', m_c11, False),
    ('C13', 'C13 Ghost voter added behind the application and used to vote', m_c13, False),
    ('C14', 'C14 Delete an unvoted voter from the roster', m_c14, False),
    ('C16', 'C16 Delete the roster seal, then add a ghost voter', m_c16, False),
    ('C17', 'C17 Forge the roster seal without the key', m_c17, False),
    ('C18', 'C18 Wipe the whole ledger', m_c18, True),
    ('C26', 'C26 Mark an unvoted voter as voted with no ballot', m_c26, False),
]

UI = {'shots': [], 'a11y': [], 'load': []}
VIEW = {'width': 1360, 'height': 900}
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    ctx = b.new_context(viewport=VIEW, device_scale_factor=1.5, color_scheme='light')
    pg = ctx.new_page()
    pg.goto(BASE + '/admin/login', wait_until='networkidle')
    pg.fill('#u', 'admin'); pg.fill('#p', 'admin123'); pg.keyboard.press('Enter')
    pg.wait_for_url(lambda u: u.rstrip('/').endswith('/admin'), timeout=20000)

    def sweep_shot(name):
        pg.goto(BASE + '/admin/elections/1/results', wait_until='networkidle')
        pg.get_by_role('button', name='Run sweep').first.click()
        pg.wait_for_timeout(1800)
        sec = pg.locator('section[aria-labelledby="sweep-h"]')
        sec.screenshot(path=str(OUT / f'{name}_sweep.png'))
        return pg.inner_text('section[aria-labelledby="sweep-h"]')[:600].replace('\n', ' | ')

    def ledger_shot(name):
        pg.goto(BASE + '/admin/ledger', wait_until='networkidle')
        pg.wait_for_timeout(900)
        pg.screenshot(path=str(OUT / f'{name}_ledger.png'), clip={'x': 0, 'y': 0, 'width': VIEW['width'], 'height': 470})
        return pg.inner_text('main')[:260].replace('\n', ' | ') if pg.locator('main').count() else pg.inner_text('body')[100:360].replace('\n', ' | ')

    for sid, title, mutate, with_ledger in SHOTS:
        restore()
        try:
            mutate()
            text = sweep_shot(sid)
            lt = ledger_shot(sid) if with_ledger else None
            UI['shots'].append({'id': sid, 'title': title, 'sweep_text': text, 'ledger_text': lt, 'files': [f'screenshots/{sid}_sweep.png'] + ([f'screenshots/{sid}_ledger.png'] if with_ledger else [])})
            print('  shot', sid, '|', text[:110])
        except Exception as ex:
            UI['shots'].append({'id': sid, 'title': title, 'error': f'{type(ex).__name__}: {ex}'[:200]})
            print('  FAILED', sid, ex)
    restore()

    # a few more views of the clean app
    for name, path, kw in (('V_results', '/admin/elections/1/results', {}), ('V_studio', '/admin/elections/1/studio', {}), ('V_outbox', '/admin/outbox', {}), ('V_elections', '/admin', {}), ('V_voters', '/admin/elections/1/voters', {})):
        pg.goto(BASE + path, wait_until='networkidle'); pg.wait_for_timeout(700)
        if name == 'V_results':
            pg.get_by_role('button', name='Run sweep').first.click(); pg.wait_for_timeout(1200)
            pg.get_by_role('button', name='Count ballots').first.click(); pg.wait_for_timeout(1500)
        pg.screenshot(path=str(OUT / f'{name}.png'), full_page=(name in ('V_results',)))
        UI['shots'].append({'id': name, 'title': name, 'files': [f'screenshots/{name}.png']})

    # voter pages, desktop and phone
    for name, path in (('V_home', '/'), ('V_vote', '/vote/1'), ('V_verify', '/verify'), ('V_demo', '/demo'), ('V_privacy', '/privacy'), ('V_contact', '/contact')):
        pg.goto(BASE + path, wait_until='networkidle'); pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / f'{name}.png'), full_page=name in ('V_demo', 'V_privacy'))
    phone = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, color_scheme='light').new_page()
    for name, path in (('M_home', '/'), ('M_vote', '/vote/1'), ('M_verify', '/verify')):
        phone.goto(BASE + path, wait_until='networkidle'); phone.wait_for_timeout(500)
        phone.screenshot(path=str(OUT / f'{name}.png'))

    # accessibility with axe-core and page-load timings (this machine, local server)
    axe_dir = SB / 'axe'
    axe_dir.mkdir()
    subprocess.run('npm install axe-core --prefix "%s" --silent' % axe_dir, shell=True, capture_output=True, timeout=240)
    axe_js = axe_dir / 'node_modules' / 'axe-core' / 'axe.min.js'
    pages = [('Home', '/', False), ('Vote sign-in', '/vote/1', False), ('Check receipt', '/verify', False), ('Demo guide', '/demo', False), ('Privacy', '/privacy', False), ('Contact', '/contact', False),
             ('Admin sign-in', '/admin/login', False), ('Elections', '/admin', True), ('Voters', '/admin/elections/1/voters', True), ('Results', '/admin/elections/1/results', True), ('DB Studio', '/admin/elections/1/studio', True),
             ('Audit ledger', '/admin/ledger', True), ('Mail outbox', '/admin/outbox', True)]
    for name, path, authed in pages:
        c2 = ctx if authed else b.new_context(viewport=VIEW)
        p2 = c2.new_page()
        p2.goto(BASE + path, wait_until='networkidle'); p2.wait_for_timeout(600)
        if axe_js.exists():
            p2.add_script_tag(path=str(axe_js))
            r = p2.evaluate('axe.run(document, {runOnly:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}).then(r => ({v: r.violations.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help})), passes: r.passes.length, incomplete: r.incomplete.length}))')
            UI['a11y'].append({'page': name, 'path': path, 'violations': r['v'], 'rules_passed': r['passes'], 'incomplete': r['incomplete']})
        p2.close()
    # load timing: 5 loads per page, medians
    for name, path, authed in pages[:7]:
        rows = []
        for _ in range(5):
            p3 = b.new_context(viewport=VIEW).new_page()
            p3.goto(BASE + path, wait_until='load')
            p3.wait_for_timeout(500)
            m = p3.evaluate('''() => { const n = performance.getEntriesByType('navigation')[0]; const f = performance.getEntriesByName('first-contentful-paint')[0];
                return {dcl: n.domContentLoadedEventEnd, load: n.loadEventEnd, fcp: f ? f.startTime : null, transfer: n.transferSize, js: performance.getEntriesByType('resource').filter(r => r.name.endsWith('.js')).reduce((a, r) => a + (r.transferSize || 0), 0)} }''')
            rows.append(m); p3.close()
        med = lambda k: round(statistics.median([r[k] for r in rows if r[k] is not None]) , 1) if any(r[k] is not None for r in rows) else None   # noqa: E731
        UI['load'].append({'page': name, 'path': path, 'dom_content_loaded_ms': med('dcl'), 'load_ms': med('load'), 'first_contentful_paint_ms': med('fcp'), 'js_transfer_kb': round((med('js') or 0) / 1024, 1)})
    b.close()

server.kill()
(RES / 'ui.json').write_text(json.dumps(UI, indent=2), encoding='utf-8')
print('wrote', RES / 'ui.json', len(list(OUT.glob('*.png'))), 'screenshots')
