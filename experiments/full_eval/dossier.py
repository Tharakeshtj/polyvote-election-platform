"""Assemble the evaluation dossier (PDF + HTML) and the paper-ready results file from the measured data.

    python experiments/full_eval/dossier.py
"""
import base64
import io
import json
import platform
import textwrap
from html import escape
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
EV = ROOT / 'docs' / 'evaluation'
RES = ROOT / 'experiments' / 'results' / 'full'
R = json.loads((RES / 'evaluation.json').read_text(encoding='utf-8'))
S = json.loads((RES / 'static.json').read_text(encoding='utf-8')) if (RES / 'static.json').exists() else {}
UI = json.loads((RES / 'ui.json').read_text(encoding='utf-8')) if (RES / 'ui.json').exists() else {'shots': [], 'a11y': [], 'load': []}
TABLES = {t['name']: t for t in json.loads((EV / 'tables.json').read_text(encoding='utf-8'))}
FIGS = {Path(f['file']).stem: f for f in json.loads((EV / 'figures_manifest.json').read_text(encoding='utf-8'))}
CORE = json.loads((ROOT / 'experiments' / 'results' / 'patched_final.json').read_text(encoding='utf-8')) if (ROOT / 'experiments' / 'results' / 'patched_final.json').exists() else None
MONGO = json.loads((ROOT / 'experiments' / 'results' / 'mongo_bench.json').read_text(encoding='utf-8')) if (ROOT / 'experiments' / 'results' / 'mongo_bench.json').exists() else {}
EVID = json.loads((ROOT / 'docs' / 'review3' / 'uniqueness_evidence.json').read_text(encoding='utf-8'))

M = R['matrix']
SC = M['scenarios']
P = {p['id']: p for p in R['profiles_all']}
PI = {p['id']: p for p in R['profiles_in_scope']}
AB = R['ablation']
FP, PR, TC, PW = R['false_positives'], R['precision_recall'], R['tally_check'], R['password']
PK, PU, CC = R['perf_keyed'], R['perf_unkeyed'], R['concurrency']
n_in = PI['P7']['of']
DATE = '4 November 2026'
LIVE = 'https://polyvote-bacse202.onrender.com'
GIT = 'https://github.com/Tharakeshtj/polyvote-election-platform'


def b64(path, maxw=1500, q=82):
    im = Image.open(path)
    if im.mode in ('RGBA', 'P'):
        bg = Image.new('RGB', im.size, 'white'); bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').split()[3]); im = bg
    im = im.convert('RGB')
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


NUM = {'fig': 0, 'tab': 0, 'shot': 0}


def fig(key, maxh=None):
    f = FIGS.get(key)
    if not f:
        return ''
    NUM['fig'] += 1
    st = f' style="max-height:{maxh}mm"' if maxh else ''
    return f'<figure><img src="{b64(EV / f["file"], 1700, 86)}"{st}><figcaption><b>Figure {NUM["fig"]}.</b> {escape(f["title"])}. {escape(f["caption"])}</figcaption></figure>'


def tab(key, cls='', limit=None):
    t = TABLES.get(key)
    if not t:
        return ''
    NUM['tab'] += 1
    rows = t['rows'][:limit] if limit else t['rows']
    h = ''.join(f'<th>{escape(str(x))}</th>' for x in t['headers'])
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(c))}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tcap"><b>Table {NUM["tab"]}.</b> {escape(t["title"].split(". ", 1)[-1])}</div><table class="t {cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


def shot(sid, extra=''):
    s = next((x for x in UI['shots'] if x['id'] == sid), None)
    if not s or 'files' not in s:
        return ''
    NUM['shot'] += 1
    imgs = ''.join(f'<img src="{b64(EV / f, 1500, 80)}">' for f in s['files'])
    txt = ''
    return f'<figure class="shot"><div class="imgs">{imgs}</div><figcaption><b>Screenshot {NUM["shot"]}.</b> {escape(s["title"])}. {extra}</figcaption>{txt}</figure>'


def kv(rows):
    return '<table class="t kv">' + ''.join(f'<tr><th>{escape(str(k))}</th><td>{v}</td></tr>' for k, v in rows) + '</table>'


def box(title, text, kind='info'):
    return f'<div class="box {kind}"><b>{title}</b> {text}</div>'


CSS = '''
@page { size: A4; margin: 14mm 14mm 15mm 14mm; }
@page wide { size: A4 landscape; margin: 12mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 9.8pt; color: #1f2430; line-height: 1.42; }
h1 { font-size: 17pt; color: #1b2a55; margin: 0 0 6px; page-break-after: avoid; border-bottom: 2px solid #1b2a55; padding-bottom: 4px; }
h2 { font-size: 12.5pt; color: #1b2a55; margin: 15px 0 5px; page-break-after: avoid; }
h3 { font-size: 10.6pt; color: #1b2a55; margin: 10px 0 3px; page-break-after: avoid; }
p { margin: 4px 0; } ul { margin: 4px 0 4px 18px; padding: 0; } li { margin: 2px 0; }
.pb { page-break-before: always; } .wide { page: wide; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover h1 { font-size: 27pt; border: 0; margin-bottom: 2px; } .sub { font-size: 12.5pt; color: #444a5a; margin-bottom: 20px; }
.small { font-size: 8.6pt; color: #666a78; }
table.t { border-collapse: collapse; width: 100%; margin: 4px 0 8px; font-size: 8.2pt; table-layout: auto; }
table.t th { background: #1b2a55; color: #fff; text-align: left; padding: 3px 5px; font-weight: 600; }
table.t td { padding: 3px 5px; border-bottom: 1px solid #e3e5ee; vertical-align: top; overflow-wrap: break-word; }
table.t tr:nth-child(even) td { background: #f7f7fb; }
table.kv th { width: 34%; background: #eef0f7; color: #1b2a55; } table.kv td { background: #fff !important; }
.tcap { font-size: 8.8pt; color: #333; margin-top: 8px; }
figure { margin: 6px 0 9px; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; border: 1px solid #dcdce6; border-radius: 3px; } figcaption { font-size: 8.3pt; color: #555a68; margin-top: 2px; text-align: left; }
figure.shot .imgs img { width: 100%; margin-bottom: 3px; } .cap2 { font-size: 7.8pt; color: #7a7f8d; font-family: Consolas, monospace; text-align: left; }
.box { padding: 6px 10px; border-radius: 5px; margin: 7px 0; font-size: 9.3pt; page-break-inside: avoid; }
.box.info { background: #e8f3fb; border-left: 4px solid #3b8ed0; } .box.ok { background: #e3f6e8; border-left: 4px solid #2e9a52; } .box.warn { background: #fff4d6; border-left: 4px solid #d09a1a; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 8px 0; }
.card { border: 1.5px solid #1b2a55; border-radius: 8px; padding: 8px 10px; background: #f6f6fb; } .card .big { font-size: 20pt; font-weight: 700; color: #1b2a55; line-height: 1.1; } .card .lab { font-size: 8.4pt; color: #444; }
code { font-family: Consolas, monospace; background: #eef0f7; padding: 0 3px; border-radius: 3px; font-size: 8.6pt; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
'''


def fmt(n):
    return f'{n:,.0f}' if isinstance(n, (int, float)) and n >= 100 else (f'{n}' if n is not None else '-')


H = []
last = PK[-1]
first = PK[0]
mid = next((r for r in PK if r['ballots'] == 10000), PK[-1])
base_sweep = None
cc1 = next((c for c in CC if c['threads'] == 1), CC[0])
ccmax = CC[-1]

# ---------------------------------------------------------------- cover
H.append(f'''<div class="cover"><div class="small">BACSE202 · Database Systems · Fall Semester 2026</div><h1>PolyVote</h1>
<div class="sub">Evaluation dossier: measured evidence for the integrity, privacy, authentication and performance claims</div>
<p>Everything below was produced by executable scripts in the repository and can be re-run. Where a result comes from documentation rather than from a measurement, it is labelled as such.</p>
<div class="grid"><div class="card"><div class="big">{PI['P7']['detected']}/{n_in}</div><div class="lab">in-scope attacks detected by the final design</div></div>
<div class="card"><div class="big">{FP['false_alarms']}/{FP['sweeps']}</div><div class="lab">false alarms on clean elections</div></div>
<div class="card"><div class="big">{TC['agree']}/{TC['elections']}</div><div class="lab">tallies agreeing with an independent count</div></div>
<div class="card"><div class="big">{len(FIGS)}</div><div class="lab">figures, plus {len(TABLES)} tables and {sum(1 for s in UI['shots'] if 'files' in s)} screenshots</div></div></div>
<p class="small">Team: Tharakesharasu Thennarasu (25BCE2699), M Pavan Durga Karthik (25BCE2712), Shivam Malge (25BCE0386) · Guide: Dr. Katari Balakrishna · {DATE}<br>Live demo: {LIVE} · Source: {GIT}</p></div>''')

# ---------------------------------------------------------------- 1 summary
H.append('<h1 class="pb">1. Summary</h1>')
H.append(f'''<p>We attacked PolyVote with <b>31 scenarios</b> that a rogue database administrator, a ledger-store administrator, or both could carry out,
recorded <b>which individual detector fired</b> for each one, and derived the behaviour of other design choices from that single record. {n_in} scenarios are inside the stated attacker model
(someone with write access to the stores who does not hold the ledger key); three are outside it and are reported anyway.</p>''')
H.append(f'''<div class="grid">
<div class="card"><div class="big">{PI['P7']['rate']:.0f}%</div><div class="lab">in-scope detection, final design ({PI['P7']['detected']}/{n_in}); all 31: {P['P7']['detected']}/31</div></div>
<div class="card"><div class="big">{P['P3']['detected']}/31</div><div class="lab">detected by our own Review 2 design (plain chain + receipt sweep)</div></div>
<div class="card"><div class="big">{P['P0']['detected']}/31</div><div class="lab">detected by a typical CRUD app whose officer compares the counters</div></div>
<div class="card"><div class="big">{R['triggers']['prevented'].__len__()}/31</div><div class="lab">prevented by append-only triggers against a writer who cannot drop them</div></div></div>''')
H.append('<h2>Headline findings</h2><ul>')
H.append(f"<li><b>The combination matters.</b> No single defence is enough: the strongest single detector finds {max(x['detected'] for x in AB['single'])} of 31 on its own, while the full design finds {P['P7']['detected']}. Removing any one detector loses between {min(P['P7']['detected'] - x['detected'] for x in AB['leave_one_out'])} and {max(P['P7']['detected'] - x['detected'] for x in AB['leave_one_out'])} attacks (Figure 3).</li>")
H.append(f"<li><b>The secret key is what stops forged and rebuilt chains.</b> With a plain SHA-256 chain the final design would miss {', '.join(AB['unkeyed_final']['lost_vs_keyed'])}; with the HMAC key it catches them (Figure 5).</li>")
H.append(f"<li><b>The voter-roster seal closes the ghost-voter gap.</b> Before it, the design caught {P['P6']['detected']} of 31 and missed every roster attack (C13 to C17); with it, all of them are caught.</li>")
H.append(f"<li><b>Accuracy:</b> across {FP['sweeps']} sweeps of randomised clean elections there were {FP['false_alarms']} false alarms; when 1, 5 or 20 ballots per category were tampered, the sweep named exactly those ballots (precision and recall 1.0).</li>")
H.append(f"<li><b>Correctness:</b> the instant-runoff tally agreed with an independent implementation that explores every tie-break in {TC['agree']} of {TC['elections']} random elections.</li>")
H.append(f"<li><b>Passwords:</b> stored hashes are now salted and slowed (PBKDF2-SHA256, {PW['iterations']:,} rounds, about {PW['slowdown_factor']:,} times slower per guess than the unsalted SHA-256 they replace).</li>")
H.append(f"<li><b>Performance:</b> at {last['ballots']:,} ballots the sweep takes {last['sweep_ms']:,.0f} ms and the chain check {last['chain_verify_ms']:,.0f} ms; the roster seal adds {max(last['sweep_ms'] - last['sweep_no_seal_ms'], 0):.0f} ms. Casting one ballot costs {mid['cast_p50_ms']} ms at 10,000 ballots (median) with the file ledger.</li>")
H.append(f"<li><b>Concurrency:</b> up to {ccmax['threads']} simultaneous voters, {sum(c['errors'] for c in CC)} errors, and the chain and sweep were intact after every run.</li></ul>")
H.append(box('How to read the comparison.', 'PolyVote is not claimed to be stronger than the cryptographic end-to-end systems (Helios, Belenios, ElectionGuard) at proving what a ballot says. The claim is narrower and measured: among the designs we could test, only the combination used here detected every in-scope storage-level attack, and it does so at the cost, size and set-up effort of a small-election tool. Section 4 states where related systems are stronger.', 'info'))

# ---------------------------------------------------------------- 2 method
H.append('<h1 class="pb">2. Method</h1>')
H.append('<h2>2.1 System under test and attacker model</h2>')
H.append(f'''<p>PolyVote stores ballots and voters in an election database (SQLite), receipts in a hash-chained ledger (MongoDB Atlas, or a file here), and voter emails and one-time codes in a third store. The attacker model is the one in the report: a person with
<b>write access to one or both stores</b> (a rogue administrator) who <b>does not hold the ledger key</b> and cannot change the application. Three scenarios step outside it on purpose: two where the attacker holds the key (C28, C29), and one that edits display text that is not sealed (C23). They are included so the limits are on the record.</p>''')
H.append('<h2>2.2 Detectors</h2>')
H.append('''<ul><li><b>Chain check</b>: recompute every block's hash and link across the ledger.</li><li><b>Sweep rule 1 (modified)</b>, <b>2 (deleted)</b>, <b>3 (injected)</b>: compare each ballot in the database with its receipt.</li>
<li><b>Rule 4 (candidate seal)</b>: candidate names against the roster hash sealed in every block. <b>Rule 5 (count mismatch)</b>: voter flags, ballots and receipts must agree.</li>
<li><b>Rule 6 (voter seal, new)</b>: the voters now in the database against a keyed seal the application wrote as it built the roster, kept in the ledger store.</li><li><b>Counters</b>: an officer comparing the three counters by eye (not automatic).</li></ul>''')
H.append('<h2>2.3 One record, many designs</h2>')
H.append(f'''<p>Every scenario was run once with the keyed (HMAC) chain and once with a plain SHA-256 chain, and for each run we stored <i>which detectors fired</i> (Table 2). A <b>design profile</b> is a subset of detectors plus a key mode, so its detection is read from the record rather than re-implemented.
This makes ablations and design comparisons exactly like-for-like. To check the idea, we emulated our own Review 2 design (plain chain, receipt sweep) this way and compared it with the <b>real Review 2 code</b> run earlier on scenarios C1 to C13:
the two agreed on <b>{R['emulation_check']['agree']} of {R['emulation_check']['of']}</b> scenarios (Table 7).</p>''')
H.append(tab('T03_design_profiles', 'small'))
H.append('<h2>2.4 Environment and reproducibility</h2>')
H.append(kv([('Machine', escape(R['machine']['platform'])), ('Python', R['machine']['python']), ('Run date', R['generated']), ('Total run time', f"{R['seconds']} s"), ('Isolation', 'a throwaway copy of the application, its own database and ledger files; Atlas and the real data are never touched'),
             ('Commands', '<code>python experiments/full_eval/run_all.py</code>, <code>static_metrics.py</code>, <code>shots.py</code>, <code>figures.py</code>, <code>dossier.py</code>'), ('Raw data', '<code>experiments/results/full/*.json, *.csv</code>')]))

# ---------------------------------------------------------------- 3 results
H.append('<h1 class="pb">3. Results</h1><h2>3.1 Attack detection</h2>')
H.append(f"<p>The final design detected <b>{P['P7']['detected']} of 31</b> scenarios ({PI['P7']['detected']} of the {n_in} in scope). The three it did not detect are the two insider-with-key attacks and the unsealed platform text.</p>")
H.append(fig('F01_detection_heatmap'))
H.append(fig('F02_detection_rate'))
H.append('<div class="pb"></div>' + tab('T01_scenarios', 'small'))
H.append('<h2>3.2 Which detector catches what</h2>' + fig('F04_detector_firing') + '<p>Most attacks are caught by more than one detector; the ones caught by only one are the ones to watch if that detector is ever weakened.</p>')
H.append('<h2>3.3 Ablation</h2>' + fig('F03_ablation') + tab('T04_ablation') + tab('T05_single'))
H.append('<h2>3.4 What the key and the seal add</h2>' + fig('F05_key_value') + fig('F06_by_adversary'))
H.append('<h2>3.5 Prevention versus detection</h2>' + fig('F07_triggers') + tab('T06_triggers') + '<p>Append-only triggers are a useful first line (they stop edits and deletions by a limited writer) but they do not cover injection, the ledger store or the roster, and a writer with schema rights removes them. Detection and prevention are complementary; this design implements both (the database already carries a one-vote trigger and CHECK constraints, Section 3.8).</p>')
H.append('<h2>3.6 Accuracy of the sweep</h2>' + fig('F14_precision_recall') + fig('F15_false_positives') + tab('T08_precision_recall', 'small') + tab('T09_false_positives'))
H.append('<h2>3.7 Audit time</h2>' + fig('F08_audit_time'))

H.append('<h1 class="pb">3.8 Database rules, abuse of the API and the one-time code</h1>')
if CORE:
    prev = [r for r in CORE['prevention']]
    api = [r for r in CORE['api_abuse']]
    otp = [r for r in CORE['otp']]
    H.append(f"<p>From the core suite re-run on the final code: database-level prevention {sum(1 for r in prev if r['outcome'] == 'prevented')}/{len(prev)}, API abuse refused {sum(1 for r in api if r['outcome'] == 'prevented')}/{len(api)}, one-time-code tests passed {sum(1 for r in otp if r['outcome'] == 'passed')}/{len(otp)}.</p>")
    H.append(f'<div class="tcap"><b>Table.</b> Database-level prevention</div><table class="t"><thead><tr><th>ID</th><th>Attempt</th><th>Mechanism</th><th>Result</th><th>Database message</th></tr></thead><tbody>' + ''.join(f"<tr><td>{r['id']}</td><td>{escape(r['attack'])}</td><td>{escape(str(r['expected']))}</td><td>{r['outcome']}</td><td>{escape(str(r['detail'])[:90])}</td></tr>" for r in prev) + '</tbody></table>')
    H.append(f'<div class="tcap"><b>Table.</b> Abuse through the public API</div><table class="t"><thead><tr><th>ID</th><th>Attempt</th><th>Expected</th><th>Result</th><th>Detail</th></tr></thead><tbody>' + ''.join(f"<tr><td>{r['id']}</td><td>{escape(r['attack'])}</td><td>{escape(str(r['expected']))}</td><td>{r['outcome']}</td><td>{escape(str(r['detail']))}</td></tr>" for r in api) + '</tbody></table>')
    H.append(f'<div class="tcap"><b>Table.</b> Emailed one-time code</div><table class="t"><thead><tr><th>ID</th><th>Test</th><th>Expected</th><th>Result</th><th>Detail</th></tr></thead><tbody>' + ''.join(f"<tr><td>{r['id']}</td><td>{escape(r['attack'])}</td><td>{escape(str(r['expected']))}</td><td>{r['outcome']}</td><td>{escape(str(r['detail'])[:100])}</td></tr>" for r in otp) + '</tbody></table>')
    H.append(box('Note on one test.', 'The earlier version of test A3 (rank the same candidate twice) picked a candidate at random and so passed only when that candidate happened to be on the chosen ballot. It now uses a candidate that is on the ballot, which is the attack the test describes; the result (refused by the composite primary key) is unchanged, but the earlier pass was partly luck and we say so.', 'warn'))
    H.append(box('The one gap in this table.', 'A5: SQLite enforces foreign keys only on connections that turn them on. The application does; a default console does not, so a nonexistent candidate can be inserted from a default connection. The sweep reports it as an injected ballot; a server database removes the gap.', 'warn'))

H.append('<h2>3.9 Passwords</h2>' + fig('F13_password_cracking') + tab('T11_password'))
H.append(box('Why this changed.', 'In Review 2, passwords were stored as unsalted SHA-256, which an attacker who steals the database can reverse for common passwords almost instantly and with shared tables. They are now stored as <code>pbkdf2_sha256$rounds$salt$hash</code> with a random 16-byte salt per password. Existing rows still sign in and are re-stored in the new format on their next successful login. Verification uses a constant-time comparison.', 'ok'))
H.append(f"<p>Cost: a password check takes about {PW['verify_ms']} ms on the test laptop ({R['login_latency']['p50_ms']} ms median over complete sign-ins at {R['login_latency']['iterations']:,} rounds). The rounds can be tuned with <code>PASSWORD_HASH_ITERATIONS</code> for slower hosts.</p>")

H.append('<h2>3.10 Voter privacy</h2>' + fig('F17_snapshot_attack') + tab('T15_privacy'))
H.append('<h2>3.11 Tally correctness</h2>' + fig('F16_tally_agreement') + tab('T10_tally'))

H.append('<h1 class="pb">3.12 Performance and scaling</h1>')
H.append(fig('F09_scaling') + fig('F10_sizes_memory_seal') + tab('T12_performance', 'small'))
H.append(fig('F11_key_overhead') + fig('F12_concurrency') + tab('T13_concurrency'))
if MONGO:
    H.append('<h2>MongoDB Atlas ledger</h2>' + kv([(f'{n} ballots in the ledger', f"append median {v.get('append_ms_median')} ms, 90th percentile {v.get('append_ms_p90')} ms") for n, v in MONGO.items() if isinstance(v, dict)]) + '<p class="small">Measured earlier against a scratch database on Atlas over a mobile hotspot (experiments/bench_mongo.py).</p>')

H.append('<h2>3.13 Security probes</h2>' + tab('T14_security'))
H.append(box('Honest limitations found by the probes.', 'There is no lock-out on repeated wrong passwords (the emailed code is the second factor and the password hash is slow, but a lock-out is future work); sessions do not expire until sign-out or restart; the sign-in distinguishes an unknown registration number from a wrong password; and the API sets no security headers of its own. None of these affects the integrity results above; they are listed so a reader can weigh them.', 'warn'))

H.append('<h2>3.14 Front end, accessibility and live deployment</h2>')
if UI['a11y']:
    rows = ''.join(f"<tr><td>{escape(a['page'])}</td><td>{len(a['violations'])}</td><td>{', '.join(escape(f'{v['id']} ({v['impact']}, {v['nodes']})') for v in a['violations']) or '-'}</td><td>{a['rules_passed']}</td></tr>" for a in UI['a11y'])
    H.append(f'<div class="tcap"><b>Table.</b> Automated WCAG 2.1 A/AA checks (axe-core) on 13 pages</div><table class="t"><thead><tr><th>Page</th><th>Violations</th><th>Rules (impact, elements)</th><th>Rules passed</th></tr></thead><tbody>{rows}</tbody></table><p class="small">Automated checks find only part of the accessibility problems; they are evidence, not certification.</p>')
if UI['load']:
    rows = ''.join(f"<tr><td>{escape(a['page'])}</td><td>{a['first_contentful_paint_ms']}</td><td>{a['dom_content_loaded_ms']}</td><td>{a['load_ms']}</td><td>{a['js_transfer_kb']}</td></tr>" for a in UI['load'])
    H.append(f'<div class="tcap"><b>Table.</b> Page load on the local server (median of 5 loads, ms)</div><table class="t"><thead><tr><th>Page</th><th>First contentful paint</th><th>DOM loaded</th><th>Load</th><th>JS transferred KB</th></tr></thead><tbody>{rows}</tbody></table>')
H.append(fig('F19_bundle') + tab('T17_live'))
H.append('<h2>3.15 Code</h2>' + fig('F18_code_metrics') + tab('T16_code'))

# ---------------------------------------------------------------- 4 comparison
H.append('<h1 class="pb">4. Comparison with related systems</h1>')
H.append('<h2>4.1 What was measured and what was read</h2>')
H.append(f'''<p>We read <b>{len(EVID)} systems</b> (hosted services, open-source projects, research systems and independent security analyses) from their own pages, READMEs and papers; every cell of the feature matrix has a source URL in <code>docs/review3/uniqueness_evidence.md</code>.
We <b>did not run</b> those systems. What we could measure is the <i>integrity mechanism</i> each documents, by running the same attacks against the design class it belongs to (Section 2.3). The first column of Table 20 states the documented mechanism and the source of the classification.</p>''')
H.append(fig('F20_feature_coverage') + tab('T18_related_systems', 'small'))

closest = [
    ('FlexyVotes (Django, PostgreSQL)', 'Per-organisation SHA-256 hash-chained audit log in the same PostgreSQL database; append-only triggers on ballots and audit rows that refuse changes even from a raw SQL session; Merkle bulletin board and signed results; hashed single-use email OTP.', 'P2 plain chain, plus the append-only trigger class', f"{P['P2']['detected']}/31 (chain) and {len(R['triggers']['prevented'])}/31 prevented (triggers, limited writer)", 'The Merkle bulletin board and signed results are not emulated; they let verifiers detect ballot edits independently of the server.'),
    ('VeriVote (Node, React, MongoDB)', 'SHA-256 chain in MongoDB with an audit endpoint and a manual tamper demo.', 'P2 plain chain', f"{P['P2']['detected']}/31", 'Not emulated: its OTP and receipt hash.'),
    ('SecureVote, SentinelVote, Kuraone (student repositories)', 'A hash-linked ledger of votes.', 'P2 plain chain', f"{P['P2']['detected']}/31", 'Single instance; documentation only.'),
    ('BetterVoting', 'Audit log of administrator actions (sharing a link, revealing a ballot link); ballots stored with identity removed.', 'P0 counters (no integrity check of stored ballots is documented)', f"{P['P0']['detected']}/31 (counters by eye)", 'Its audit log records actions taken through the application, which database-level tampering bypasses.'),
    ('Google Forms, Microsoft Forms, typical CRUD apps', 'Responses in a table; no tamper evidence documented.', 'P0 CRUD, officer compares counters', f"{P['P0']['detected']}/31", ''),
    ('OpaVote, ElectionBuddy, Simply Voting, Election Runner, TapVoter', 'Vendor-run services with voter audit reports, raw-ballot downloads and receipt codes.', 'Not emulated', '-', 'The vendor holds the data; the integrity mechanisms are internal and not documented in enough detail to emulate.'),
    ('Helios, Belenios, ElectionGuard, Civitas, Zeus', 'End-to-end verifiable: ballots are encrypted and posted to a public bulletin board; voters and auditors can verify inclusion and the tally.', 'Different architecture', '-', 'A stored-ballot edit is detected by any voter who checks and by public audit; PolyVote detects it only through its own sweep. These systems are stronger on proving what a ballot says.'),
]
H.append('<h2>4.2 Documented integrity mechanisms mapped to measured design classes</h2>')
H.append('<table class="t small"><thead><tr><th>System</th><th>Documented mechanism</th><th>Closest measured class</th><th>Measured detection of the class</th><th>What this does not capture</th></tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(c)}</td>' for c in r) + '</tr>' for r in closest) + f"<tr><td><b>PolyVote final</b></td><td>Keyed hash chain in a separate store, six sweep rules, database rules, keyed roster seal.</td><td>P7</td><td><b>{P['P7']['detected']}/31 ({PI['P7']['detected']}/{n_in} in scope)</b></td><td>Cannot prove what a ballot says to the voter (not end-to-end verifiable).</td></tr></tbody></table>")
H.append(box('Reading this table fairly.', 'The classes are emulations of documented mechanisms, not the products. They show how far each <i>mechanism</i> goes against storage-level tampering. They say nothing about features outside that scope, and the products may have protections that are not documented.', 'warn'))
H.append('<h2>4.3 Where PolyVote stands</h2>')
H.append(f'''<ul>
<li><b>Combination of controls.</b> The documented systems each have part of what PolyVote combines: ranked counting and organisations (OpaVote, FlexyVotes, BetterVoting), database rules and append-only triggers (FlexyVotes), a hash-chained ledger (FlexyVotes, VeriVote and others), emailed one-time codes (FlexyVotes, SecureVote), QR sharing (TapVoter, BetterVoting). Across the {len(EVID)} systems we read, none documents all of them together; PolyVote adds a keyed chain in a separate store, a reconciling sweep with a keyed roster seal, QR scan-to-vote, and published executable attack results.</li>
<li><b>Measured coverage.</b> Against the same 31 attacks, the design classes of the closest projects detect {P['P2']['detected']} (plain chain) and prevent {len(R['triggers']['prevented'])} (append-only triggers) while PolyVote detects {P['P7']['detected']} ({PI['P7']['detected']} in scope).</li>
<li><b>Cost.</b> Free, open source, one command to run, runs on a laptop or a free hosting plan; the whole back end is about {S.get('loc', {}).get('lines', {}).get('Back end (Python)', 0):,} lines.</li></ul>''')
H.append('<h2>4.4 Where related systems are stronger</h2><ul><li><b>Verifiability of ballot content.</b> Helios, Belenios, ElectionGuard and Civitas let a voter confirm that the ballot recorded is the one they cast and let anyone audit the tally; PolyVote\'s receipt proves only that a ballot is recorded and counted.</li><li><b>Untrusted administrator.</b> Cryptographic systems keep working when the administrator is hostile; PolyVote assumes the key holder is honest.</li><li><b>Maturity.</b> Helios, Belenios and CIVS have years of use and public analysis; PolyVote has had none.</li><li><b>Append-only enforcement and a public bulletin board (FlexyVotes)</b> are stronger prevention and public-verification features than PolyVote\'s file or Atlas ledger.</li></ul>')

# ---------------------------------------------------------------- 5 screenshots
H.append('<h1 class="pb">5. The application under attack: screenshots</h1><p>Each attack below was applied to the files of a running copy of the app (keyed ledger, demo election with 30 voters and 18 ballots) and the sweep was run in the browser. The monospaced line under each image is the page text.</p>')
order = ['S00', 'C1', 'C3', 'C5', 'C6', 'C7', 'C9', 'C10', 'C11', 'C13', 'C14', 'C16', 'C17', 'C18', 'C26']
meaning = {'C1': 'Rule 1 (modified) names the ballot.', 'C3': 'Rule 2 (deleted) and the count check fire.', 'C5': 'Rule 3 (injected) and the count check fire.', 'C6': 'The forged receipt is not keyed, so the chain check fails at the forged block.',
           'C7': 'The chain check names the edited block.', 'C9': 'Truncation leaves ballots without receipts; the sweep reports them.', 'C10': 'A chain rebuilt without the key fails the keyed check.', 'C11': 'Rule 4: candidate names no longer match the sealed roster.',
           'C13': 'Rule 6 (new): a voter added behind the application is named.', 'C14': 'Rule 6: a removed voter is counted.', 'C16': 'Deleting the roster seal is itself detected.', 'C17': 'A seal forged without the key does not verify.', 'C18': 'Wiping the ledger leaves every ballot without a receipt.', 'C26': 'The count check fires: a flag without a ballot.'}
for sid in order:
    H.append(shot(sid, meaning.get(sid, '')))
H.append('<h2>Other views</h2><div class="two">' + ''.join(shot(x) for x in ('V_results', 'V_studio')) + '</div>')
H.append('<div class="two">' + ''.join(shot(x) for x in ('V_voters', 'V_outbox')) + '</div>')

# ---------------------------------------------------------------- 6 limits
H.append('<h1 class="pb">6. Threats to validity and limitations</h1>')
H.append('''<ul>
<li><b>We wrote the attacks.</b> The scenarios are ours, so the suite is biased towards what we thought of. We widened it from 13 to 31 and describe each in Table 1; independent review is needed.</li>
<li><b>Design classes are emulations.</b> Related systems were not run. The emulation approach was validated against our own real Review 2 code (13 of 13 agreement) but not against third-party products.</li>
<li><b>Out-of-model attackers.</b> An insider with the ledger key (C28, C29) is not detected; protecting against it needs an external witness for the chain head, a managed secret store, or both.</li>
<li><b>Unsealed text.</b> Candidate platform statements are not covered by the sealed roster hash (C23).</li>
<li><b>Voter privacy limits.</b> An attacker who copies the database before and after a single cast can link that voter to that ballot (Figure 17); the administrator's simulation tool casts in roster order (demo only).</li>
<li><b>Single machine, synthetic data.</b> Performance numbers come from one laptop; ledger measurements use the file backend, which rewrites the file on each append. The Atlas figures come from an earlier run on a mobile hotspot.</li>
<li><b>No user study yet.</b> Usability and delivery-time claims await the pilot election with real voters.</li>
<li><b>Known engineering gaps.</b> No lock-out on repeated wrong passwords, no session expiry, user enumeration at sign-in, no security headers on the API, SQLite foreign keys per connection (A5), single node.</li></ul>''')

# ---------------------------------------------------------------- 7 reproducibility and appendix
H.append('<h1 class="pb">7. Reproducibility</h1>')
H.append(kv([('Repository', GIT), ('Attack matrix and profiles', '<code>experiments/full_eval/engine.py</code>'), ('Security, privacy, accuracy, tally, passwords, scaling', '<code>experiments/full_eval/extras.py</code>'),
             ('Static analysis, bundle, live site', '<code>experiments/full_eval/static_metrics.py</code>'), ('Screenshots, accessibility, page load', '<code>experiments/full_eval/shots.py</code>'), ('Figures and tables', '<code>experiments/full_eval/figures.py</code>'),
             ('Core suite (prevention, API, one-time code)', '<code>experiments/run_experiments.py</code>'), ('Website checklist', '<code>experiments/web_checklist.py</code> (live: 18 pass, 3 not applicable, 0 fail)'),
             ('Related-systems evidence', '<code>docs/review3/uniqueness_evidence.md</code> and <code>.json</code> (a source URL for every cell)')]))
H.append('<div class="wide"><h1 class="pb">Appendix A. Full tables</h1>' + tab('T02_detector_matrix', 'small') + tab('T07_emulation', 'small') + '</div>')

html = f'<!doctype html><html><head><meta charset="utf-8"><title>PolyVote evaluation dossier</title><style>{CSS}</style></head><body>' + '\n'.join(H) + '</body></html>'
(EV / 'PolyVote_Evaluation_Dossier.html').write_text(html, encoding='utf-8')
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    pg = b.new_page()
    pg.set_content(html, wait_until='load')
    pg.pdf(path=str(EV / 'PolyVote_Evaluation_Dossier.pdf'), format='A4', print_background=True, prefer_css_page_size=True, display_header_footer=True, header_template='<span></span>',
           footer_template='<div style="font-size:8px;color:#777;width:100%;text-align:center;font-family:Arial">PolyVote evaluation dossier · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>', margin={'top': '14mm', 'bottom': '15mm', 'left': '14mm', 'right': '14mm'})
    b.close()

# ---------------------------------------------------------------- paper-ready results
md = [f'# PolyVote: paper-ready results ({DATE})', '', 'All numbers come from `experiments/results/full/evaluation.json`. Re-run `experiments/full_eval/run_all.py` to regenerate.', '',
      '## Headline numbers', '']
md += [f"- In-scope attacks detected by the final design: **{PI['P7']['detected']}/{n_in}** ({PI['P7']['rate']}%); all 31 scenarios: {P['P7']['detected']}/31.",
       f"- Review 2 design (plain chain + receipt sweep): {P['P3']['detected']}/31; CRUD with eyeballed counters: {P['P0']['detected']}/31; plain chain only: {P['P2']['detected']}/31; keyed chain only: {P['P5']['detected']}/31; previous final design (no voter seal): {P['P6']['detected']}/31.",
       f"- Append-only triggers on the ballot table prevent {len(R['triggers']['prevented'])}/31 against a writer who cannot drop them; a writer with schema rights removes them.",
       f"- False alarms on clean elections: {FP['false_alarms']} in {FP['sweeps']} sweeps over {FP['elections']} elections. Precision and recall 1.0 for modified, deleted and injected ballots (k = 1, 5, 20).",
       f"- Tally agrees with an independent exhaustive-tie-break implementation in {TC['agree']}/{TC['elections']} random elections ({TC['with_tie_paths']} with a tie path).",
       f"- Password hash: PBKDF2-SHA256, {PW['iterations']:,} rounds, 16-byte salt; about {PW['slowdown_factor']:,}x slower per guess than unsalted SHA-256; verification {PW['verify_ms']} ms.",
       f"- At {last['ballots']:,} ballots: sweep {last['sweep_ms']:,.0f} ms, chain check {last['chain_verify_ms']:,.0f} ms, tally {last['tally_ms']:,.0f} ms; roster seal re-computation {last['reseal_roster_ms']} ms.",
       f"- Concurrency 1 to {ccmax['threads']} threads: {sum(c['errors'] for c in CC)} errors; throughput {cc1['throughput_per_s']} to {ccmax['throughput_per_s']} casts/s.", '',
       '## Table: design profiles (copy into the paper)', '', '| Profile | Design | Detected (31) | In scope |', '|---|---|---|---|']
md += [f"| {a['id']} | {a['label']} | {a['detected']}/31 | {b['detected']}/{b['of']} |" for a, b in zip(R['profiles_all'], R['profiles_in_scope'])]
md += ['', '## Table: ablation (leave one detector out)', '', '| Removed | Still detected | Lost |', '|---|---|---|']
md += [f"| {x['removed']} | {x['detected']}/{x['of']} | {' '.join(x['lost']) or '-'} |" for x in AB['leave_one_out']]
md += ['', '## Suggested claim wording', '',
       '- "Against 31 storage-level attack scenarios, the combination of a keyed hash chain, a reconciling sweep and a keyed voter-roster seal detected every attack by an adversary without the ledger key; no single control did."',
       '- "Emulating the integrity mechanism of plain hash-chained designs on the same scenarios detected {0} of 31, and a typical CRUD application with manual count checking {1} of 31."'.format(P['P2']['detected'], P['P0']['detected']),
       '- "PolyVote does not provide end-to-end verifiability; voters can check that a ballot is recorded and counted but not its content."', '']
(EV / 'PAPER_RESULTS.md').write_text('\n'.join(md), encoding='utf-8')
print('dossier written:', EV / 'PolyVote_Evaluation_Dossier.pdf')
