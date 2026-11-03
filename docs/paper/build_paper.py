"""Build docs/paper/PolyVote_Conference_Paper.docx: a two-column IEEE-style conference paper from the full evaluation.

    python docs/paper/paper_figs.py
    python docs/paper/build_paper.py
Numbers come from experiments/results/full/evaluation.json; references from docs/review3/references.json (all verified).
"""
import json
import re
from pathlib import Path

import docx
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R = json.loads((ROOT / 'experiments' / 'results' / 'full' / 'evaluation.json').read_text(encoding='utf-8'))
U = json.loads((ROOT / 'docs' / 'review3' / 'uniqueness_evidence.json').read_text(encoding='utf-8'))
OUT = HERE / 'PolyVote_Conference_Paper.docx'
FONT = 'Times New Roman'

ids = [r['id'] for r in json.loads((ROOT / 'docs' / 'review3' / 'references.json').read_text(encoding='utf-8'))]
ieee = [re.sub(r'^\[\d+\]\s*', '', ln) for ln in (ROOT / 'docs' / 'review3' / 'references_ieee.txt').read_text(encoding='utf-8').split('\n') if ln.strip()]
assert len(ids) == len(ieee)
TEXT = dict(zip(ids, ieee))
cited = []


def cite(m):
    nums = []
    for k in (x.strip() for x in m.group(1).split(',')):
        if k not in TEXT:
            raise KeyError(k)
        if k not in cited:
            cited.append(k)
        nums.append(cited.index(k) + 1)
    return '[' + ', '.join(str(n) for n in sorted(nums)) + ']'


doc = docx.Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(0.9)
sec.left_margin = sec.right_margin = Inches(0.625)
st = doc.styles['Normal']
st.font.name, st.font.size = FONT, Pt(10)
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)


def runs(p, text, size=10, bold=False, italic=False):
    text = re.sub(r'\{([^}]+)\}', cite, text)
    for tok in re.split(r'(\*\*.+?\*\*|`.+?`|\*[^*\s][^*]*?\*)', text):
        if not tok:
            continue
        b, i, mono = bold, italic, False
        if tok.startswith('**'):
            tok, b = tok[2:-2], True
        elif tok.startswith('`'):
            tok, mono = tok[1:-1], True
        elif tok.startswith('*') and len(tok) > 2:
            tok, i = tok[1:-1], True
        r = p.add_run(tok)
        r.font.name = 'Consolas' if mono else FONT
        r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas' if mono else FONT)
        r.font.size = Pt(size - 1.5 if mono else size)
        r.bold, r.italic = b or None, i or None


def para(text, align='justify', size=10, before=0, after=4, bold=False, italic=False, indent=True, keep_next=False):
    p = doc.add_paragraph()
    p.alignment = {'justify': WD_ALIGN_PARAGRAPH.JUSTIFY, 'center': WD_ALIGN_PARAGRAPH.CENTER, 'left': WD_ALIGN_PARAGRAPH.LEFT}[align]
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.0
    if indent and align == 'justify':
        pf.first_line_indent = Inches(0.17)
    pf.keep_with_next = keep_next or None
    runs(p, text, size, bold, italic)
    return p


def h1(text):
    return para(text.upper(), 'center', 10, before=7, after=3, indent=False, keep_next=True)


def h2(text):
    return para(text, 'left', 10, before=3, after=2, italic=True, indent=False, keep_next=True)


def set_columns(section, n, space=0.25):
    sectPr = section._sectPr
    for el in sectPr.findall(qn('w:cols')):
        sectPr.remove(el)
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'), str(n))
    cols.set(qn('w:space'), str(int(space * 1440)))
    sectPr.append(cols)


def figure(path, caption, width=3.3):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(3), Pt(1)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(width))
    para(caption, 'center', 8, after=5, indent=False)


def table(headers, rows, widths, caption, size=8):
    para(caption, 'center', 8, before=3, after=2, indent=False, keep_next=True)
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = 1
    for ri, row in enumerate([headers] + rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri].cells[ci]
            cell.width = Inches(widths[ci])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            runs(p, str(val), size, bold=(ri == 0))
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


# ------------------------------------------------------------------ numbers
PA = {p['id']: p for p in R['profiles_all']}
PI = {p['id']: p for p in R['profiles_in_scope']}
N = len(R['matrix']['scenarios'])
fin, prev, r2, crud, plain, keyed1 = PA['P7'], PA['P6'], PA['P3'], PA['P0'], PA['P2'], PA['P5']
loo = {x['removed']: x for x in R['ablation']['leave_one_out']}
best_single = max(x['detected'] for x in R['ablation']['single'])
perf = {r['ballots']: r for r in R['perf_keyed']}
pw, fp, tc, ll, cc = R['password'], R['false_positives'], R['tally_check'], R['login_latency'], R['concurrency']
pr = R['precision_recall']
assert fin['detected'] == 28 and PI['P7']['detected'] == 28 and N == 31
assert tc['agree'] == tc['elections'] and fp['false_alarms'] == 0 and R['emulation_check']['agree'] == 13


def lost(k):
    return fin['detected'] - loo[k]['detected']


def n_yes(code):
    return sum(1 for s in U if (s[code]['value'] if isinstance(s[code], dict) else eval(s[code])['value']) == 'yes')


def n_partial(code):
    return sum(1 for s in U if (s[code]['value'] if isinstance(s[code], dict) else eval(s[code])['value']) == 'partial')


# ------------------------------------------------------------------ title block
para('PolyVote: Making Silent Database Tampering Detectable in Small Ranked-Choice Elections', 'center', 20, after=6, indent=False)
para('Tharakesharasu Thennarasu, M Pavan Durga Karthik and Shivam Malge', 'center', 11, after=0, indent=False)
para('Vellore Institute of Technology, School of Computer Science and Engineering', 'center', 10, after=0, indent=False, italic=True)
para('Faculty guide: Dr. Katari Balakrishna', 'center', 10, after=6, indent=False, italic=True)

abstract = (
    '**Abstract**—Student bodies, clubs and departments run elections on spreadsheets, form tools or small web applications in which one administrator '
    'can edit the database without leaving a trace. End-to-end verifiable systems {adida2008, cortier2019} remove that trust but need key ceremonies and trustees that small organisations will not operate. '
    'We present PolyVote, an open-source instant-runoff voting platform that makes silent edits detectable using ordinary database features: '
    'rules enforced inside the relational engine, an HMAC-keyed hash-chained receipt ledger in a separate store, a keyed seal over the voter roster, '
    'and an integrity sweep that reconciles ballots, receipts, voter flags and rosters and names the tampered records. '
    f'We attack the system with {N} storage-level scenarios, run once against a keyed and once against a plain chain, and record which detector fires; '
    'ablations and comparisons with other designs are then read from that single record. '
    f'Against an attacker with write access to the stores but not the ledger key, the final design detects {PI["P7"]["detected"]} of {PI["P7"]["of"]} in-scope scenarios, '
    f'against {PI["P3"]["detected"]} for a plain chain with a receipt sweep, {PI["P0"]["detected"]} for a conventional application whose officer compares counters, and {PI["P6"]["detected"]} for our previous design. '
    f'Over {fp["sweeps"]} sweeps of randomised clean elections there were no false alarms, and the tally agreed with an independent exhaustive implementation in {tc["agree"]} of {tc["elections"]} random elections. '
    'The system is not end-to-end verifiable, assumes an honest key holder and has not been evaluated with users; we state these limits.')
p = para(abstract, 'justify', 9, after=4, indent=False)
for r in p.runs:
    r.italic = False
para('**Index Terms**—electronic voting, instant-runoff voting, tamper-evident logging, HMAC, hash chain, database integrity, audit.', 'justify', 9, after=5, indent=False)

new = doc.add_section(WD_SECTION.CONTINUOUS)
set_columns(new, 2)

# ------------------------------------------------------------------ I
h1('I. Introduction')
para('Most elections are small: a student council, a society, a class representative. They are run on whatever is at hand, usually a single database that its administrator can change. '
     'Research on electronic voting has concentrated on protocols that avoid trusting the server {adida2008, cortier2019, clarkson2008, ryan2009, chaum2009} and on the failures of deployed internet voting {springall2014, specter2020, specter2021, nasem2018}. '
     'Between these lies a large population of small elections for which a cryptographic system is impractical, yet where a good deal can be achieved with the database itself.')
para('We ask a narrow question: *what is the cheapest design that makes silent edits by someone with database access detectable?* '
     'Our contributions are: (1) a three-store design in which ballots, receipts and voter contact data are held apart, with election rules enforced by the engine; '
     '(2) an integrity sweep with six reconciliation rules and a keyed voter-roster seal, which closed a ghost-voter gap that we found in an earlier version; '
     '(3) a detector-level evaluation method in which each attack is run once and ablations and design comparisons are read from the same record; and '
     f'(4) measurements of detection, false alarms, tally correctness, password cost, scaling to 100,000 ballots and concurrency, with the attack scripts, raw data and a documentation survey of {len(U)} related systems released with the code.')

# ------------------------------------------------------------------ II
h1('II. Related Work')
para('Helios {adida2008} and Belenios {cortier2019} give a verifiable tally with encrypted ballots; Civitas {clarkson2008} adds coercion resistance; Prêt à Voter {ryan2009} and Scantegrity II {chaum2009} target paper-based verification. '
     'Analyses of deployed systems found serious weaknesses in Estonian internet voting {springall2014} and in mobile and web products {specter2020, specter2021}, and a National Academies study advised against internet voting for now {nasem2018}; blockchain voting adds further problems {park2021}. '
     'PolyVote does not compete with these on assurance; it targets the settings in which they are not used.')
para('Hash chaining for time-stamping {haber1991} and for secure audit logs {schneier1999} underlies tamper-evident logging {crosby2009, rfc6962}. '
     'In databases, work covers tamper detection in audit logs {snodgrass2004}, forensic analysis of tampering {pavlou2008} and ledger tables in a commercial engine {antonopoulos2021}. '
     'Instant-runoff outcomes can hinge on few ballots, which motivates auditing {magrino2011, blom2019}. '
     'Our difference is the combination: the chain is keyed, it is reconciled against a relational store and a roster seal, and the whole is evaluated by attack.')

# ------------------------------------------------------------------ III
h1('III. System Design')
para('PolyVote is one FastAPI service with a React front end and three stores, separated by what each is trusted with (Fig. 1). '
     'The **election database** (SQLite) holds organisations, elections, candidates, the roster and ranked ballot rows. The **receipt ledger** (MongoDB Atlas or a local file) holds one sealed block per ballot. '
     'A **verification database** holds voter email addresses, hashed one-time codes and a mail log. The secrets (ledger key, SMTP credentials) live outside all three.')
figure(HERE / 'figs' / 'architecture.png', 'Fig. 1. Architecture: three stores, with secrets held outside all of them.', 3.3)
h2('A. Rules enforced by the engine')
para('A trigger aborts a second update of the voted flag; CHECK constraints bound flags and ranks; a composite key prevents ranking a candidate twice; registration numbers are unique per election; foreign keys tie rows together {aulbach2008}. '
     'A ballot is stored under a random token and no column links it to a voter. Casting is serialised: the server re-checks the election state, sets the flag and inserts the ranked rows in one transaction, then appends the receipt. '
     'A failure between the two leaves a ballot with no receipt, which the sweep reports; we chose the variant that fails visibly. Counting is instant-runoff.')
h2('B. Keyed receipt ledger')
para('Each ballot yields a block holding its index, election, token, a hash of the ranked choices, a hash of the candidate list, a roster hash, the previous hash and its own hash. '
     'The block hash is HMAC-SHA-256 under a key held outside both stores, so an attacker who can write the ledger but lacks the key cannot rebuild a consistent chain, which a plain hash chain permits. '
     'A unique index on the block position stops two writers from forking the chain.')
h2('C. Integrity sweep and roster seal')
para('The sweep applies six rules: (1) a ballot whose recomputed hash differs from its receipt is *modified*; (2) a receipt with no ballot is *deleted*; (3) a ballot with no receipt is *injected*; '
     '(4) candidate names that differ from the hash sealed in every block are *renamed*; (5) the three counters (voters marked as voted, ballots, receipts) must agree; '
     'and (6) the voters in the database must match a keyed seal of the roster, one HMAC tag per voter and a signature over the set, written by the application and kept in the ledger store. '
     'Rule 6 detects voters added, deleted or edited outside the application, and the blocks record whether the election was sealed, so deleting the seal is itself detected. A separate chain check recomputes every block hash and link.')
h2('D. Authentication')
para('Passwords are stored as PBKDF2-HMAC-SHA256 with a random 16-byte salt and 600,000 rounds {nist800132, owasp_pwd}; older unsalted hashes verify once and are upgraded at the next sign-in. '
     'After the password, a six-digit code is emailed, stored only as a hash, valid for five minutes, single use, limited to three guesses and rate-limited per voter {nist80063b4}. Email is only as strong as the mailbox {garfinkel2003}.')

# ------------------------------------------------------------------ IV
h1('IV. Threat Model')
para('The attacker has write access to the election database, the ledger store, or both, and does **not** hold the ledger key: a rogue database administrator, a ledger-store administrator, or an insider with both stores but no secrets. '
     'Three of the 31 scenarios are deliberately outside this model and are reported anyway: two in which the attacker holds the key, and one that edits a candidate\'s platform text, which is not sealed. '
     'We do not claim protection against a malicious key holder, a compromised application host, coercion, vote selling, denial of service or malware on a voter\'s device.')

# ------------------------------------------------------------------ V
h1('V. Evaluation Method')
para(f'**Scenarios.** We wrote {N} attacks (C1 to C{N}) at the storage level: swapping or replacing choices, deleting, injecting or stuffing ballots, editing, deleting, truncating, wiping, replaying and reordering ledger blocks, rebuilding a whole chain, '
     'renaming candidates, resetting voted flags, adding, deleting or renaming voters, forging or deleting the roster seal, and rolling a store back to an older backup. '
     'Each runs against a throwaway copy of the application, so neither Atlas nor real data is touched.')
table(['Attack family', 'IDs', 'Caught by'],
      [['Edit a ballot', 'C1, C2', 'rule 1'],
       ['Delete or inject a ballot', 'C3 to C5', 'rules 2, 3; counters'],
       ['Forge receipt, rebuild chain, erase a vote', 'C6, C10, C27', 'chain check (needs key)'],
       ['Tamper with ledger blocks', 'C7 to C9, C18 to C22', 'chain check; rules 2, 3'],
       ['Roll a store back to a backup', 'C30, C31', 'rules 2, 3; counters'],
       ['Reset or fake voted flags', 'C12, C26', 'rule 5'],
       ['Change the candidate list', 'C11, C24, C25', 'rule 4'],
       ['Ghost, deleted or renamed voters; roster seal', 'C13 to C17', 'rule 6'],
       ['Outside the model (key holder; platform text)', 'C23, C28, C29', 'not detected']],
      [1.85, 0.85, 0.7], 'TABLE I. The 31 attack scenarios by family, and what catches them in the final design.', size=7.5)
para('**Detector-level record.** Every scenario is run once with the keyed chain and once with a plain SHA-256 chain, and we record which detectors fire (chain check, rules 1 to 6, and an officer comparing counters by eye). '
     'A *design profile* is a subset of detectors plus a key mode, so its detection is read from the record, not re-implemented. '
     f'To validate the idea, we emulated our earlier plain-chain design this way and compared it with the real earlier code on C1 to C13: the two agreed on {R["emulation_check"]["agree"]} of 13.')
para('**Other measurements.** Randomised clean elections for false alarms; sweeps after tampering 1, 5 and 20 ballots per category for precision and recall; 500 random elections for tally correctness against an independent implementation; '
     'timing from 100 to 100,000 ballots; one to 16 simultaneous voters; password-guessing cost; and probes for abuse of the API and voter privacy. '
     f'Competing systems were **not** run: we read the documentation of {len(U)} of them and place their documented mechanisms in the nearest measured design class.')

# ------------------------------------------------------------------ VI
h1('VI. Results')
h2('A. Detection')
table(['Design (detectors, key)', f'All {N}', 'In scope (28)'],
      [['CRUD application, officer compares counters', f'{crud["detected"]}', f'{PI["P0"]["detected"]}'],
       ['Plain chain only', f'{plain["detected"]}', f'{PI["P2"]["detected"]}'],
       ['Plain chain + receipt sweep (our Review 2 design)', f'{r2["detected"]}', f'{PI["P3"]["detected"]}'],
       ['Plain chain + all six rules', f'{PA["P4"]["detected"]}', f'{PI["P4"]["detected"]}'],
       ['Keyed chain only', f'{keyed1["detected"]}', f'{PI["P5"]["detected"]}'],
       ['Keyed chain + rules 1 to 5 (previous design)', f'{prev["detected"]}', f'{PI["P6"]["detected"]}'],
       ['**Keyed chain + six rules (PolyVote)**', f'**{fin["detected"]}**', f'**{PI["P7"]["detected"]}**']],
      [2.35, 0.45, 0.6], 'TABLE II. Attack scenarios detected by each design.', size=8)
para(f'The final design detects {fin["detected"]} of {N} scenarios, which is all {PI["P7"]["of"]} that lie within the threat model (Table II, Fig. 2). No single control is enough: the strongest detector alone finds {best_single}. '
     f'The key matters: with a plain chain the same six rules would miss four in-scope attacks, those that forge or rebuild a chain that anyone can recompute. '
     f'Append-only triggers on the ballot table prevent {len(R["triggers"]["prevented"])} of {N} against a writer who cannot drop them, but they do not stop injection, ledger tampering or roster changes, and a writer with schema rights removes them.')
figure(HERE / 'figs' / 'detection.png', 'Fig. 2. Share of in-scope attack scenarios detected by each design.', 3.3)
h2('B. Ablation')
para(f'Removing the chain check loses {lost("chain")} attacks, the voter seal {lost("voter_seal")}, the candidate seal {lost("candidate_seal")}, '
     f'the count rule {lost("count_mismatch")} and the modified-ballot rule {lost("modified")} (Fig. 3). '
     'Removing rule 2 or rule 3 loses none, because the chain and counters also see those attacks; they remain because they name the records. '
     f'The roster seal is what closes the ghost-voter attack: the previous design caught {prev["detected"]} of {N} and missed every roster attack.')
figure(HERE / 'figs' / 'ablation.png', 'Fig. 3. Attacks lost when one detector is removed from the final design.', 3.3)
h2('C. Accuracy and correctness')
para(f'Across {fp["sweeps"]} sweeps over {fp["elections"]} randomised clean elections (bulk registration, late voters, ballots, closing) there were {fp["false_alarms"]} false alarms. '
     'When 1, 5 or 20 ballots were modified, deleted or injected, the sweep named exactly those ballots: precision and recall were 1.0 in all nine cases. '
     f'The tally agreed with an independent implementation that explores every tie-break in {tc["agree"]} of {tc["elections"]} elections of 3 to 8 candidates and 5 to 300 ballots ({tc["with_tie_paths"]} had a tie path).')
h2('D. Passwords')
para(f'Moving from unsalted SHA-256 to salted PBKDF2 makes each offline guess about {pw["slowdown_factor"]:,.0f} times slower and prevents precomputed tables. '
     f'A sign-in takes a median {ll["p50_ms"]:.0f} ms of hashing; the round count is configurable for slower hosts.')
h2('E. Performance')
table(['Ballots', 'Sweep', 'Chain', 'Tally', 'Cast p50'],
      [[f'{b:,}', f'{perf[b]["sweep_ms"]:,.0f}', f'{perf[b]["chain_verify_ms"]:,.0f}', f'{perf[b]["tally_ms"]:,.0f}', f'{perf[b]["cast_p50_ms"]:,.0f}'] for b in (100, 1000, 10000, 100000)],
      [0.7, 0.6, 0.6, 0.6, 0.7], 'TABLE III. Median time in ms with the keyed file ledger.', size=8)
para(f'Audit and tally grow roughly linearly (Fig. 4). At 10,000 ballots, typical of a large campus election, the sweep takes {perf[10000]["sweep_ms"]:.0f} ms; at 100,000 it takes {perf[100000]["sweep_ms"] / 1000:.1f} s. '
     'With the file ledger the cost of casting grows with the ledger because each append rewrites the file; against MongoDB Atlas over a mobile hotspot an append took about 140 ms regardless of length. '
     f'With 1 to 16 simultaneous voters there were no errors and the chain and sweep were intact after every run (up to {max(c["throughput_per_s"] for c in cc):.0f} casts per second on a laptop).')
figure(HERE / 'figs' / 'scaling.png', 'Fig. 4. Audit time against election size (log scales).', 3.3)
h2('F. Abuse and privacy probes')
para('All 13 abuse attempts through the public API were refused, including twenty simultaneous casts by one voter, of which exactly one was stored; six of seven attempts to break the rules from a database console were rejected by the engine, '
     'the exception being a dangling candidate reference because SQLite enforces foreign keys per connection (the sweep reports it). '
     'The ballot and voter tables share no column other than the election; an ordering attack on 150 casts recovered no voter. '
     'An attacker with two database copies and one cast in between links a voter to a ballot with probability one over the number of casts, a known limit of any design that stores a voted flag.')

# ------------------------------------------------------------------ VII
h1('VII. Comparison with Related Systems')
table(['Capability (documented by the system)', 'Yes', 'Partial'],
      [['F1 Ranked choice with round-by-round transcript', n_yes('F1'), n_partial('F1')],
       ['F3 Integrity rules inside the relational database', n_yes('F3'), n_partial('F3')],
       ['F5 Keyed tamper-evident ledger, reconciling sweep, published attacks', n_yes('F5'), n_partial('F5')],
       ['F6 Emailed one-time code at sign-in', n_yes('F6'), n_partial('F6')],
       ['F8 Voter receipt', n_yes('F8'), n_partial('F8')]],
      [2.4, 0.4, 0.5], f'TABLE IV. Documentation survey of {len(U)} systems (the rest: not documented or absent).', size=8)
para(f'Of {len(U)} systems whose own pages we read, none documents all of F1, F3, F5 and F6, and none documents F5 in the strict sense used here. '
     '"Not documented" means we did not find it, not that it is absent. This is a statement about documentation, not about the products.')
para('Where related systems are stronger is the substance. Helios, Belenios and ElectionGuard let a voter check that the recorded ballot is the one cast and let anyone check the tally; PolyVote\'s receipts show only that a ballot is recorded and counted. '
     'A hostile administrator who holds the ledger key defeats PolyVote and does not defeat them. Those systems have years of use and public analysis; PolyVote has none. '
     'Its claim is cost and fit: free, open source, one command to run, and a detection result that anyone can re-run.')

# ------------------------------------------------------------------ VIII
h1('VIII. Limitations and Threats to Validity')
para('The 31 attacks were written by the authors, so the in-scope result shows coverage of the attacks we thought of, not of all attacks; an independently written list is future work. '
     'Competing designs are placed in measured classes from documentation, not run. An insider with the ledger key and both stores can forge a consistent chain; publishing the chain head to an external witness {rfc6962} would address this. '
     'There is no account lock-out, no session expiry, the login reveals whether a registration number exists, and API responses carry no security headers. '
     'Receipts do not prove content {chaum2004}. The file ledger is slow at 100,000 ballots. Timings come from one laptop. '
     'One early prevention test was flaky and was fixed; we disclose it. No user study has been run, so we make no usability claim.')

h1('IX. Reproducibility and Future Work')
para('Every number in this paper is produced by scripts in the repository: `run_all.py` runs the 31 scenarios in both key modes, the ablation and the design profiles; `extras.py` runs the accuracy, correctness, password, performance and concurrency measurements; '
     '`static_metrics.py` and `shots.py` record code, dependency and interface measurements. A full run takes under ten minutes on a laptop and writes JSON and CSV files from which the tables and figures are drawn. '
     'The attack scenarios operate on a throwaway copy of the application, so a reader can add their own without touching a real election.')
para('Four extensions would most strengthen the evidence. First, an attack list written by people who did not build the system. Second, an external witness that receives the chain head, which would extend detection to a key holder {rfc6962}. '
     'Third, account lock-out, session expiry and response headers, which the probes show are missing. Fourth, a task-based usability study with voters and administrators; we have prepared a protocol, consent form, task cards and a standard System Usability Scale analysis, but no participant has yet been tested.')

h1('X. Conclusion')
para(f'A keyed receipt chain, a reconciling sweep and a keyed roster seal let a small organisation detect silent edits by a database administrator at modest cost. No single control sufficed: the combination detected all {PI["P7"]["of"]} in-scope attacks, '
     f'the plain chain with a receipt sweep {PI["P3"]["detected"]}, and a conventional application {PI["P0"]["detected"]}, with no false alarms on clean elections. '
     'We do not offer end-to-end verifiability and we do not claim that the attack list is complete. '
     'Code, attack scripts, raw results, 21 figures and a 32-page dossier are at https://github.com/Tharakeshtj/polyvote-election-platform; a demo runs at https://polyvote-bacse202.onrender.com.')

# ------------------------------------------------------------------ refs
h1('References')
for i, k in enumerate(cited, start=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Inches(0.3), Inches(-0.3)
    p.paragraph_format.space_after, p.paragraph_format.line_spacing = Pt(1), 1.0
    runs(p, f'[{i}] ' + TEXT[k].replace('{', '').replace('}', ''), 7.5)

cp = doc.core_properties
cp.author, cp.title, cp.comments, cp.last_modified_by = 'Tharakesharasu Thennarasu, M Pavan Durga Karthik, Shivam Malge', 'PolyVote: Making Silent Database Tampering Detectable in Small Ranked-Choice Elections', '', ''
doc.save(str(OUT))
print('wrote', OUT, '| cited', len(cited))
