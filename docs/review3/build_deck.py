"""Build docs/PolyVote_Review3_Final.pptx: the Review 3 deck, picking up from Review 2 (same template, 45 slides, speaker notes on each).

    python docs/review3/build_deck.py
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REVIEW2 = ROOT / 'docs' / 'PolyVote_Review2.pptx'
OUT = ROOT / 'docs' / 'PolyVote_Review3_Final.pptx'
ASSETS = ROOT / 'docs' / 'review3_assets'
RES = ROOT / 'experiments' / 'results'
SPDIR = Path(os.environ.get('DECK_HELPERS', r'C:\Users\thenn\AppData\Local\Temp\claude\C--Mini-Desktop-PolyVote-Project\74acc99f-9563-4979-a9c2-b0aefeecec0c\scratchpad\scripts\build_deck.py'))

# Reuse the Review 2 helper functions (text boxes, cards, tables, frame) without re-running its slide edits.
src = SPDIR.read_text(encoding='utf-8').split('# ================================================================== edit existing slides')[0]
sys.argv = ['x', str(REVIEW2), str(OUT), str(ASSETS / 'screens'), str(ASSETS / 'diagrams' / 'er.png')]
exec(compile(src, 'deck_helpers', 'exec'), globals())
FOOT = 'BACSE202 – Database Systems | Review 3 | Fall Semester 2026 · Slide {n}'

S = json.loads((RES / 'summary.json').read_text(encoding='utf-8'))
M = json.loads((RES / 'mongo_bench.json').read_text(encoding='utf-8'))
tam = S['tamper']
b, p = S['bench']['baseline'], S['bench']['patched']
nd = lambda k: sum(1 for t in tam if t[k] == 'detected')  # noqa: E731
from PIL import Image  # noqa: E402


def fit_pic(slide, path, x, y, w, h, border=True):
    """Place an image inside the box (x, y, w, h), keeping its aspect ratio and centring it."""
    with Image.open(path) as im:
        iw, ih = im.size
    sc = min(w / iw, h / ih)
    pw, ph = iw * sc, ih * sc
    pc = slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))
    if border:
        pc.line.color.rgb = BORDER
        pc.line.width = Pt(1)
    return pc


def crop_center(name, x0=0.27, x1=0.73):
    out = ASSETS / 'screens' / '_crop'
    out.mkdir(exist_ok=True)
    dst = out / name
    with Image.open(ASSETS / 'screens' / name) as im:
        w, h = im.size
        im.crop((int(w * x0), 0, int(w * x1), h)).save(dst)
    return dst


def bullets(slide, x, y, w, h, items, size=12, after=5):
    paras = []
    for it in items:
        if isinstance(it, tuple):
            paras.append([('•  ', {'color': NAVY, 'bold': True}), (it[0], {'bold': True, 'color': NAVY}), (' ' + it[1], {})])
        else:
            paras.append([('•  ', {'color': NAVY, 'bold': True}), (it, {})])
    return tb(slide, x, y, w, h, paras, size=size, color=INK, after=after)


def caption(slide, x, y, w, text, size=9.5):
    return tb(slide, x, y, w, 0.3, text, size=size, color=MUTED, italic=True, align=PP_ALIGN.CENTER)


def crop_box(name, x0, y0, x1, y1, tag):
    out = ASSETS / 'screens' / '_crop'
    out.mkdir(exist_ok=True)
    dst = out / f'{tag}_{name}'
    with Image.open(ASSETS / 'screens' / name) as im:
        w, h = im.size
        im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1))).save(dst)
    return dst


C_Y, C_P, C_N = RGBColor(0xD7, 0xF0, 0xDD), RGBColor(0xFB, 0xEE, 0xCF), RGBColor(0xF8, 0xD9, 0xD5)


def compare_slide(kicker, title, rows, strip, notes_text, widths=(2.0, 5.6, 1.4), row_h=0.46, size=9.5, strip_y=None):
    s = slide(kicker, title)
    table(s, 0.5, 1.15, 9.0, ['System', 'What its own page, README or paper documents', 'Match'], rows, list(widths), size=size, header_size=9.5, row_h=row_h, head_h=0.32)
    y = strip_y or (1.15 + 0.32 + row_h * len(rows) + 0.15)
    card(s, 0.5, y, 9.0, 5.2 - y, fill=LAV)
    tb(s, 0.7, y + 0.08, 8.6, 5.2 - y - 0.12, strip, size=10, color=INK, after=3)
    notes(s, notes_text)
    return s


# ------------------------------------------------------------------ keep every Review 2 slide; its thank-you slide moves to the end
R2_COUNT = len(prs.slides)
title_slide, thanks_slide = prs.slides[0], prs.slides[R2_COUNT - 1]
from pptx.opc.packuri import PackURI  # noqa: E402
thanks_slide.part.partname = PackURI('/ppt/slides/slide90.xml')   # keep new slide part names from colliding with it
set_runs_text(by_name(title_slide, 26), ['Reviews 2 and 3 · Final Project Review · Guide: Dr. Katari Balakrishna'])
set_runs_text(by_name(title_slide, 28), [FOOT.format(n=1)])
notes(title_slide,
      'Good morning, sir, and everyone. This deck has two parts: slides 2 to 20 are the Review 2 presentation, and from slide 21 we continue with Review 3. This is Review 3, the final review of PolyVote, our ranked-choice election platform with a tamper-evident audit trail. '
      'Review 1 presented the design and Review 2 showed the working system. Today we show the completed system: a MongoDB Atlas ledger, a keyed hash chain, '
      'a second authentication factor using emailed one-time codes, public hosting, and an evaluation that tests our claims instead of asserting them. '
      'We will also show a short live demonstration of the version with email verification switched on.')

N = [R2_COUNT - 1]


def slide(kicker, title):
    N[0] += 1
    s = new_slide()
    frame(s, kicker, title, N[0])
    return s


# ================================================================== 2b picking up from Review 2
s = slide('PICKING UP FROM REVIEW 2', 'Review 2 left a short list; two new features lead it')
card(s, 0.5, 1.2, 3.4, 3.8)
chip(s, 0.7, 1.34, 'REVIEW 2 ENDED WITH')
bullets(s, 0.7, 1.75, 3.0, 3.2, ['A working system built and demonstrated.', 'Open: MongoDB Atlas, hosting, injected-ballot detection.', 'Faculty feedback: confirm the voter with a second factor.', 'Deferred on purpose: Oracle with PL/SQL, POSITION entity.'], size=11)
card(s, 4.1, 1.2, 2.6, 3.8, fill=LAV)
chip(s, 4.3, 1.34, 'NEW: EMAIL OTP')
tb(s, 4.3, 1.75, 2.2, 3.2, [[('A correct password is no longer enough.', {'bold': True, 'color': NAVY})], [('A 6-digit code is emailed to the voter, valid 5 minutes, one use, 3 guesses.', {})], [('', {})], [('Answers the Review 2 comment.', {'italic': True, 'color': MUTED})]], size=11, color=INK, after=4)
card(s, 6.9, 1.2, 2.6, 3.8, fill=LAV)
chip(s, 7.1, 1.34, 'NEW: QR VOTING')
tb(s, 7.1, 1.75, 2.2, 3.2, [[('Scan, sign in, vote.', {'bold': True, 'color': NAVY})], [('The vote page shows a QR code for the public link, so any phone opens the ballot in seconds.', {})], [('', {})], [('Works with the emailed code on the same phone.', {'italic': True, 'color': MUTED})]], size=11, color=INK, after=4)
notes(s, 'We pick up exactly where Review 2 ended. At Review 2 we had a working system, with MongoDB Atlas, hosting and injected-ballot detection still open, and the faculty comment that we should confirm the person voting is the person whose credentials are used. '
         'Two new features lead this review. First, the emailed one-time code: a correct password is no longer enough, because a six-digit code goes to the voter\'s email, valid for five minutes, usable once, with three guesses. '
         'Second, QR voting: the vote page shows a QR code for the public link, so any phone can open the ballot in seconds, and the same phone can receive the emailed code. The rest of the deck shows how they work, the evidence, and how this compares with similar systems.')

# ================================================================== 3 feedback -> response
s = slide('RESPONSE TO FEEDBACK', 'Each Review 2 comment has a concrete answer')
table(s, 0.5, 1.2, 9.0, ['Comment at Review 2', 'What we did', 'Evidence'], [
    ['Confirm the voter: OTP or face ID', 'Emailed one-time code after the password; separate verification database; admin outbox', '14 of 14 OTP tests pass'],
    ['Finish MongoDB', 'Ledger now in MongoDB Atlas, unique-index concurrency control, file fallback, migration script', '25 blocks migrated; live health endpoint'],
    ['Host it online', 'Public HTTPS link through a tunnel; QR code on the voter page for phones', 'Cast a ballot from a phone'],
    ['Prove it is better', '47-scenario executable suite run on the Review 2 design and the final design', f'{nd("baseline")} of 13 to {nd("patched")} of 13 attacks caught'],
    ['Weak spots we knew about', 'Injected ballots, forged receipts, rewritten chains, renamed candidates', 'Each has a test and a fix'],
], [3, 4.5, 2.5], size=10.5, row_h=0.62)
tb(s, 0.5, 4.75, 9.0, 0.5, 'Where we say "future work", it is because the design needs something we cannot add honestly in one semester, and we say what.', size=11, color=MUTED, italic=True)
notes(s, 'This slide is the direct response to the Review 2 comments. The second factor became an emailed one-time code with its own database and fourteen passing tests. MongoDB is done and live on Atlas. '
         'Hosting is a public HTTPS link with a QR code, so a phone can vote. And to prove the design is better, we built a forty-seven scenario suite and ran it against both the Review 2 design and the final one. '
         'The weaknesses we knew about, such as injected ballots, forged receipts and renamed candidates, each have a test and a fix. Where we still say future work, we explain why.')

# ================================================================== 6 threat model
s = slide('THREAT MODEL', 'Who the attacker is, and who we do not stop')
fit_pic(s, ASSETS / 'diagrams' / 'threat_model.png', 0.5, 1.15, 9.0, 3.7, border=False)
caption(s, 0.5, 4.88, 9.0, 'Detected means found by an auditor running the checks, not blocked in real time.')
notes(s, 'A security claim means nothing without a threat model, so we start there. Seven adversaries, ordered by capability. A voter with a leaked password is stopped by the emailed code. A rogue database administrator and a ledger-store administrator are detected by the sweep and the keyed chain. '
         'An insider with both stores but no secrets is detected, because they cannot recompute the keyed chain. Three are not covered: a network observer, beyond the tunnel\'s encryption; an insider who also holds the key; and roster injection through the admin path. '
         'We say so now rather than have it found later.')

# ================================================================== 8 architecture
s = slide('FINAL ARCHITECTURE', 'Three stores, separated by what each is trusted with')
fit_pic(s, ASSETS / 'diagrams' / 'architecture.png', 0.5, 1.15, 6.0, 4.1, border=False)
bullets(s, 6.7, 1.3, 2.9, 3.8, [('Election DB:', 'roster, candidates, anonymous ballots.'), ('Verification DB:', 'emails and one-time codes, a separate file, never joined to ballots.'),
                                 ('Ledger:', 'MongoDB Atlas, HMAC chain.'), ('Secrets:', 'in .env, outside every store.'),
                                 'An administrator of one store cannot touch the others.'], size=11.5)
notes(s, 'The architecture. One FastAPI service that also serves the React app, exposed through a tunnel. Behind it three stores. The election database holds the roster, candidates and anonymous ballots. '
         'The verification database is a separate file that holds voter emails and one-time-code challenges, and it is never joined to ballots. The ledger is a MongoDB Atlas collection. Secrets live in an environment file outside all three. '
         'The point of the separation is that an administrator of one store cannot touch the others; only the application host sees all three, which is why host compromise is outside our model.')

# ================================================================== 9 ER
s = slide('DATA MODEL', 'Data model: election, ledger and verification stores')
fit_pic(s, ASSETS / 'diagrams' / 'er.png', 0.4, 1.15, 6.6, 4.1, border=False)
bullets(s, 7.1, 1.3, 2.5, 3.8, ['Shared multi-tenant schema, scoped by election.', 'No column links a ballot to a voter.', 'Candidate roster hash sealed in the ledger.', 'Emails live in a different file; no key reaches ballots.', 'Trigger, CHECK, UNIQUE, FK enforce the rules.'], size=11)
notes(s, 'The updated ER diagram. The left frame is the election database, unchanged in structure from Review 2 apart from what it protects. The dashed box is a ledger block, a JSON document linked to a ballot by its token, not by a foreign key. '
         'The right frame is new: the verification database with voter contacts, challenges and a mail log. Notice there is deliberately no line from it to the ballot table. A voter\'s email can never be joined to a ballot.')

# ================================================================== 11 keyed ledger
s = slide('KEYED AUDIT LEDGER', 'Keyed chain: rebuilding it needs the secret key')
for i, (idx, hs) in enumerate([(1, 'vote_data_hash\nroster_hash'), (2, 'vote_data_hash\nroster_hash'), (3, 'vote_data_hash\nroster_hash')]):
    x = 0.5 + i * 2.2
    card(s, x, 1.25, 1.95, 1.5)
    tb(s, x + 0.12, 1.32, 1.7, 0.25, f'Block {idx}', size=11, color=NAVY, bold=True)
    tb(s, x + 0.12, 1.62, 1.75, 0.5, [[('ballot_token, ' + hs.split(chr(10))[0] + ',', {'font': 'Consolas', 'size': 7.5})], [(hs.split(chr(10))[1] + ', prev_hash', {'font': 'Consolas', 'size': 7.5})]], size=8)
    label_shape(s, x + 0.12, 2.25, 1.7, 0.4, 'curr_hash = HMAC(key, block)', size=8, color=NAVY, fill=CHIP, bold=True)
    if i < 2:
        arrow(s, x + 1.95, 2.0, x + 2.2, 2.0)
tb(s, 7.2, 1.3, 2.3, 1.4, [[('prev_hash', {'font': 'Consolas', 'bold': True, 'color': NAVY, 'size': 10}), (' links each block to the one before it.', {})]], size=10.5)
bullets(s, 0.5, 3.0, 9.0, 2.2, [('Review 2:', 'curr_hash was plain SHA-256. An attacker who can write the store can edit a ballot and recompute every later hash.'),
                                 ('Final:', 'curr_hash is HMAC-SHA-256 under LEDGER_KEY, held outside the database and the ledger store. Without the key the rebuilt chain fails verification.'),
                                 ('Roster hash:', 'every block also seals the candidate list, so renaming candidates after voting is detected.'),
                                 ('Backward compatible:', 'blocks written before the key existed still verify (LEDGER_LEGACY_UNTIL).'),
                                 ('Limit:', 'whoever holds the key can still forge blocks; that needs an external witness (future work).')], size=11.5)
notes(s, 'This is the key idea of the integrity story. Each block holds the ranks hash, the roster hash, the previous block\'s hash and its own hash. In Review 2 the block hash was plain SHA-256, so someone who could write the store could change a ballot and recompute every later hash. '
         'The chain was consistent but not authenticated. Now the block hash is an HMAC under a secret key held outside both stores. An attacker without the key can rebuild a chain, but it fails verification at the first block. '
         'Older blocks still verify. The limit is stated on the slide: whoever holds the key can still forge, which needs an external witness.')

# ================================================================== 12 sweep
s = slide('INTEGRITY SWEEP', 'Five rules compare the database with the ledger')
table(s, 0.5, 1.2, 9.0, ['Rule', 'Detects', 'How', 'New?'], [
    ['1  Modified', 'A ballot whose ranks changed', 'Recompute ranks hash; compare with the receipt', 'Review 2'],
    ['2  Deleted', 'A sealed ballot missing from the database', 'Receipt exists with no ballot rows', 'Review 2'],
    ['3  Injected', 'A ballot with no receipt', 'Ballot rows exist with no block', 'New'],
    ['4  Roster changed', 'Candidate names altered after voting', 'Current roster hash differs from the sealed hash', 'New'],
    ['5  Count mismatch', 'Flags, ballots, receipts disagree', 'Compare the three counts for the election', 'New'],
], [1.7, 2.7, 3.7, 0.9], size=10.5, row_h=0.55)
tb(s, 0.5, 4.5, 9.0, 0.7, [[('Plus the chain check: ', {'bold': True, 'color': NAVY}), ('recompute every block\'s link and hash across the whole ledger. The chain check finds edits inside the ledger; the sweep finds edits to the database.', {})]], size=11.5)
notes(s, 'The sweep recomputes the state of an election from the database and compares it with the ledger. Rules one and two were in Review 2. Rule three finds a ballot in the database that has no receipt. Rule four compares the current candidate names with the sealed hash. '
         'Rule five compares voter flags, ballots and receipts. The chain check, which verifies every block, is separate and complementary: it finds edits inside the ledger, while the sweep finds edits to the database.')

# ================================================================== 13 mongo
s = slide('MONGODB ATLAS LEDGER', 'A real document store with its own concurrency control')
bullets(s, 0.5, 1.25, 5.3, 3.9, [('Collection:', 'each block is one document in polyvote.ledger.'), ('Unique index on block index:', 'two writers cannot both claim the next slot, so the chain cannot fork.'),
                                  ('Append cost:', 'reads only the last block and inserts one document, so it does not grow with the chain.'), ('Fallback:', 'no connection string, or Atlas unreachable, and it uses the local file; /api/health shows which.'),
                                  ('Migration:', 'a script copies the old blocks and verifies the chain; it refuses to overwrite a non-empty collection.'), ('Secrets:', 'the connection string lives in .env, never in the code or the repository.')], size=11.5)
card(s, 6.1, 1.3, 3.4, 3.7, fill=LAV)
tb(s, 6.3, 1.4, 3.0, 0.3, 'Live health check', size=12, color=NAVY, bold=True)
tb(s, 6.3, 1.8, 3.0, 1.0, [[('{"backend":"mongodb",', {'font': 'Consolas', 'size': 9})], [(' "detail":"mongodb', {'font': 'Consolas', 'size': 9})], [('   (polyvote.ledger)",', {'font': 'Consolas', 'size': 9})], [(' "sealing":"hmac-sha256"}', {'font': 'Consolas', 'size': 9})]], size=9)
tb(s, 6.3, 3.0, 3.0, 1.9, 'Editing any block in Atlas (for example a vote_data_hash) makes the Audit ledger page show "Data tampered at block N".', size=11, color=INK)
notes(s, 'MongoDB. Each block is a document in a collection with a unique index on the block position. That index is our compare-and-swap: two simultaneous writers cannot both take the same slot, so the chain cannot fork. '
         'Appending reads only the last block and inserts one document, so the cost does not grow with the chain. If no connection string is set, or Atlas is unreachable, the system falls back to the local file, and the health endpoint says which backend is active. '
         'A migration script moved our existing blocks and verified the chain. The connection string lives only in the environment file.')

# ================================================================== 14 OTP flow
s = slide('EMAIL ONE-TIME CODE', 'A correct password no longer opens a ballot on its own')
fit_pic(s, ASSETS / 'diagrams' / 'otp_sequence.png', 0.5, 1.15, 9.0, 4.05, border=False)
notes(s, 'The second factor. The voter enters the registration number and password. If they are right, the server does not issue a session; it issues a challenge, generates a six-digit code, stores only a keyed hash of it, and emails the code from a background thread so the page never waits on the mail server. '
         'The voter types the code, the server compares it in constant time, checks the attempt count and the single-use flag, and only then issues the voting session. A failed email never blocks sign-in because the code is also visible in the administrator outbox.')

# ================================================================== 16 voter experience
s = slide('THE VOTER EXPERIENCE', 'Sign in, confirm by code, rank, and keep a receipt')
shots = [('voter_signin_qr.png', '1  Sign in (QR for phones)'), ('voter_otp.png', '2  Enter the emailed code'), ('voter_ballot_desktop.png', '3  Rank three choices'), ('voter_receipt.png', '4  Receipt token')]
for i, (f, cap) in enumerate(shots):
    x = 0.45 + i * 2.28
    fit_pic(s, crop_center(f) if f != 'voter_ballot_desktop.png' else ASSETS / 'screens' / f, x, 1.25, 2.15, 3.3)
    tb(s, x, 4.62, 2.15, 0.4, cap, size=10, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
notes(s, 'This is what a voter sees. One: sign in with registration number and password; the QR code lets a phone open the same ballot. Two: the new step, the code sent to the address on file. '
         'Three: rank three candidates in order; there is a review step before the irreversible cast. Four: the receipt token and the ledger block number. The token shows that a ballot is recorded and counted; it does not reveal how anyone voted.')

# ================================================================== 17 phone + hosting
s = slide('PHONE VOTING AND HOSTING', 'Phone voting, a public link, and an honest account')
fit_pic(s, ASSETS / 'screens' / 'voter_signin_mobile.png', 0.5, 1.2, 1.7, 3.6)
fit_pic(s, ASSETS / 'screens' / 'voter_ballot_mobile.png', 2.3, 1.2, 1.7, 3.6)
bullets(s, 4.3, 1.3, 5.2, 3.8, [('How:', 'a Cloudflare quick tunnel gives a temporary public HTTPS address; the vote page shows a QR code for it.'), ('Works from any network;', 'tested casting a real ballot from a phone.'),
                                 ('What it is not:', 'cloud deployment. The laptop must stay on, and the address changes when the tunnel restarts.'),
                                 ('Why we say so:', 'a true cloud platform with Oracle is the next step.'),
                                 ('Safe by default:', 'secrets stay in .env; the repository holds only .env.example.')], size=11.5)
notes(s, 'Hosting. We expose the service through a Cloudflare quick tunnel, which gives a temporary public HTTPS address without opening ports. The voter page shows a QR code for it, so a phone scans and votes; we cast a real ballot from a phone this way. '
         'To be precise, this is public hosting from a laptop, not cloud deployment: the laptop has to stay on and the address changes when the tunnel restarts. A real cloud platform is part of the Oracle migration planned next. The repository contains only a template for the environment file, never the secrets.')

# ================================================================== 18 live demo
s = slide('LIVE DEMO · SAMPLE POLYVOTE', 'The same system with email verification switched on')
steps = [('1', 'Admin', 'Voters have emails; Mail outbox open'), ('2', 'Sign in', 'Password right, still no ballot'), ('3', 'Code', 'Read it from the outbox or inbox'), ('4', 'Vote', 'Rank, cast, get the receipt'),
         ('5', 'Seal', 'Receipt check; new block in Atlas'), ('6', 'Tamper', 'DB Studio edit; sweep names it'), ('7', 'Ledger', 'Edit a block in Atlas; chain breaks')]
for i, (n, h, d) in enumerate(steps):
    x, y = 0.5 + (i % 4) * 2.27, 1.25 + (i // 4) * 1.7
    card(s, x, y, 2.1, 1.5)
    chip(s, x + 0.15, y + 0.12, n, w=0.34)
    tb(s, x + 0.15, y + 0.5, 1.8, 0.3, h, size=13, color=NAVY, bold=True)
    tb(s, x + 0.15, y + 0.85, 1.8, 0.6, d, size=10.5, color=INK)
card(s, 7.3, 2.95, 2.1, 1.5, fill=LAV)
tb(s, 7.45, 3.05, 1.85, 1.35, [[('Safety net', {'bold': True, 'color': NAVY})], [('Every code also appears in the outbox, so a slow email cannot stall the demo.', {'size': 10})]], size=11, color=INK, after=3)
tb(s, 0.5, 4.8, 9.0, 0.4, 'Separate copy: its own database, its own Atlas collection, port 8001; START_DEMO resets it in about 20 seconds.', size=10.5, color=MUTED, italic=True)
notes(s, 'Now a short live demonstration, on a separate copy of the project we call Sample PolyVote. It is identical except that email verification is switched on, and it has its own database and its own Atlas collection so it cannot disturb the main system. '
         'The flow: show the admin view with voter emails and the outbox; sign in as a voter, and note that the right password is not enough; take the code from the outbox, or from the inbox if mail is configured; rank and cast; check the receipt and show the new block in Atlas. '
         'Then the tamper test: edit a ballot in DB Studio and run the sweep, and edit a block in Atlas to show the chain breaking. If email is slow, the code is always in the outbox.')

# ================================================================== 19 evaluation method
s = slide('HOW WE EVALUATED', '47 executable scenarios, old design versus final')
groups = [('7', 'DB prevention', 'Statements the schema should reject'), ('13', 'API abuse', 'Wrong password, injection, replay, races'), ('13', 'Tampering', 'Edits by someone with storage access'), ('14', 'One-time code', 'Replay, expiry, limits, failure'), ('3', 'Benchmark sizes', '100, 1,000, 10,000 ballots')]
for i, (n, h, d) in enumerate(groups):
    x = 0.5 + i * 1.82
    card(s, x, 1.25, 1.68, 1.9)
    tb(s, x + 0.1, 1.35, 1.5, 0.6, n, size=30, color=NAVY, bold=True)
    tb(s, x + 0.1, 1.98, 1.5, 0.3, h, size=11, color=NAVY, bold=True)
    tb(s, x + 0.1, 2.3, 1.5, 0.8, d, size=9.5, color=INK)
bullets(s, 0.5, 3.4, 9.0, 1.8, ['A throwaway copy of the app is driven through the real API; a "rogue administrator" edits the database and ledger files directly.',
                                'Baseline: the Review 2 design, checked out and run unchanged. Attacker scripts never receive the ledger key.',
                                'Outcome per attack: detected by the sweep or chain, visible only in counters, or not detected. Benchmarks are medians of three runs.'], size=11.5)
notes(s, 'To prove the design is better we built a suite instead of arguing. Forty-seven scenarios: seven database-level prevention tests, thirteen API abuse tests, thirteen tampering scenarios, and fourteen one-time-code tests, plus benchmarks at one hundred, one thousand and ten thousand ballots. '
         'The suite runs on a throwaway copy, drives the real API, and plays the rogue administrator by editing the database and ledger files directly. The baseline is the Review 2 design, run unchanged, and the attacker scripts never see the ledger key. '
         'We repeat each run three times; the outcomes were identical every time.')

# ================================================================== 20 prevention
s = slide('PREVENTION RESULTS', 'Prevention results: one gap taught us something')
table(s, 0.5, 1.2, 9.0, ['Attempt', 'Stopped by', 'Result'], [
    ['Second vote by the same voter', 'Trigger', 'Prevented'], ['Rank 4 on a 1–3 ballot', 'CHECK', 'Prevented'], ['Same candidate ranked twice', 'Composite key', 'Prevented'],
    ['Duplicate roster entry', 'UNIQUE', 'Prevented'], ['Wrong password, SQL injection, replayed session', 'API', 'Prevented'], ['20 simultaneous casts by one voter', 'Lock + transaction', 'Exactly one accepted'],
    ['Nonexistent candidate from a default console', 'FK (off by default in SQLite)', 'Not prevented'],
], [4.6, 2.6, 1.8], size=10.5, row_h=0.37)
tb(s, 0.5, 4.55, 9.0, 0.7, [[('The gap: ', {'bold': True, 'color': RED}), ('SQLite enforces foreign keys only on connections that enable it. The application does; a console with default settings does not. A server database removes this, which is part of the Oracle move.', {})]], size=11)
notes(s, 'The prevention results. Six of seven database statements are rejected by the engine with its own error message, and all thirteen API abuse tests are refused, including twenty simultaneous casts by one voter of which exactly one is stored. '
         'The one gap is instructive: SQLite enforces foreign keys only on connections that turn the setting on. Our application does; a console opened with default settings does not. So a rogue administrator can insert a ballot for a candidate that does not exist. '
         'The sweep reports it as injected, but the lesson is that a constraint is only as strong as the engine\'s enforcement, which is one reason for the move to a server database.')

# ================================================================== 21 tampering results
s = slide('TAMPERING RESULTS', f'Automatic detection rises from {nd("baseline")} of 13 to {nd("patched")} of 13')
fit_pic(s, RES / 'detection.png', 0.5, 1.2, 9.0, 2.45, border=False)
for i, (big, lab, col) in enumerate([(f'{nd("baseline")}/13', 'Review 2 design: detected automatically', RED), (f'{nd("patched")}/13', 'Final design: detected automatically', GREEN), ('1', 'Still undetected: roster injection (C13)', AMBER)]):
    x = 0.5 + i * 3.09
    card(s, x, 3.85, 2.83, 1.2, fill=LAV)
    tb(s, x + 0.15, 3.9, 1.3, 0.8, big, size=28, color=col, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x + 1.5, 3.95, 1.25, 1.0, lab, size=10, color=INK, anchor=MSO_ANCHOR.MIDDLE)
notes(s, f'The central result. Thirteen scenarios of tampering by someone with direct storage access. Under the Review 2 design, {nd("baseline")} are detected automatically, three are visible only if an officer compares the counters by eye, and four are not detected at all. '
         f'Under the final design, {nd("patched")} are detected automatically, none depend on the counters, and one is not detected: adding a ghost voter to the roster and voting as them. We report that one openly. The detection bar shows each scenario, colour-coded.')

# ================================================================== 22 sweep in action
s = slide('SWEEP IN ACTION', 'A deletion and an injection hide in the counts')
fit_pic(s, ASSETS / 'screens' / 'admin_sweep_tamper.png', 0.5, 1.2, 5.6, 3.6)
fit_pic(s, ASSETS / 'screens' / 'admin_ledger_tampered.png', 6.3, 1.2, 3.2, 2.1)
bullets(s, 6.3, 3.4, 3.2, 1.9, ['Left: counters read 46 / 46 / 46, yet the sweep reports 1 deleted and 1 without a receipt.', 'Above: one edited block breaks the chain.'], size=10.5)
notes(s, 'Here is why counters alone are not enough. On the left, one ballot was deleted and another injected, so the counters still read forty-six, forty-six, forty-six and look perfectly healthy. The sweep nevertheless names both ballots, one deleted and one without a receipt. '
         'On the right, a single edited block makes the audit ledger page show a red banner: data tampered at block twenty.')

# ================================================================== 23 attacks plain chains miss
s = slide('WHY THE KEY MATTERS', 'Six scenarios the Review 2 design missed')
lab = {'detected': 'Detected', 'detected_manual_only': 'Counters only', 'undetected': 'Not detected'}
pick = ['C5', 'C6', 'C9', 'C10', 'C11', 'C12']
desc = {'C5': 'Inject a ballot with no receipt', 'C6': 'Ballot stuffing: inject, forge receipt, set a flag', 'C9': 'Truncate the last ledger block', 'C10': 'Alter a ballot and rebuild the whole chain',
        'C11': 'Swap two candidates\' names after voting', 'C12': 'Reset a voted flag, vote again'}
fix = {'C5': 'Injected-ballot rule', 'C6': 'Keyed chain', 'C9': 'Reconciliation rule', 'C10': 'Keyed chain', 'C11': 'Sealed roster hash', 'C12': 'Reconciliation rule'}
byid = {t['id']: t for t in tam}
table(s, 0.5, 1.2, 9.0, ['ID', 'Scenario', 'Review 2', 'Final', 'What closed it'],
      [[i, desc[i], lab[byid[i]['baseline']], lab[byid[i]['patched']], fix[i]] for i in pick], [0.6, 3.9, 1.4, 1.2, 1.9], size=10.5, row_h=0.42)
tb(s, 0.5, 4.6, 9.0, 0.6, [[('Key point: ', {'bold': True, 'color': NAVY}), ('C6 and C10 defeat any chain that is only hashed, because the attacker recomputes the hashes. With the HMAC key they fail at the first block the attacker cannot compute.', {})]], size=11.5)
notes(s, 'Six scenarios the old design missed or only half caught. A ballot injected without a receipt, and a truncated ledger, were visible only in the counters; the new injected-ballot and reconciliation rules catch them. Renaming candidates after voting was invisible; the sealed roster hash catches it. '
         'The two serious ones are ballot stuffing with a forged receipt and a consistent rewrite of the whole chain. Both were completely undetected, because a plain hash chain lets an attacker recompute every hash. With the key, the forged or rebuilt blocks fail verification.')

# ================================================================== 24 OTP tests
s = slide('ONE-TIME CODE TESTS', '14 of 14 pass, and the suite caught a real defect on the way')
bullets(s, 0.5, 1.25, 4.6, 3.9, ['Password alone gives no session; the challenge id is not a token.', 'Right code opens the ballot; a used code cannot be replayed.', 'Three wrong codes lock the challenge, even if the right code follows.',
                                  'Expired codes, rapid resends and a sixth code are refused.', 'No email on file: clear refusal.', 'Plaintext codes are absent from the database.', 'A failed mail server does not block sign-in.', 'No email column exists in the election database.'], size=11)
card(s, 5.3, 1.3, 4.2, 3.6, fill=LAV)
tb(s, 5.5, 1.4, 3.8, 0.3, 'The defect', size=13, color=RED, bold=True)
tb(s, 5.5, 1.8, 3.8, 3.0, 'Test F4 first failed. The wrong-guess counter was saved inside a database context, and the request then raised an error. SQLite rolls back when an exception leaves the context, so every failed guess was recorded and then undone: unlimited guessing. The fix commits state before the error propagates. Review would not have found it; the test did.', size=11, color=INK)
notes(s, 'All fourteen one-time-code tests pass: no session from a password alone, replay refused, three wrong guesses lock the challenge, expiry, resend limits, privacy of stored codes, and resilience to a failed mail server. '
         'But it did not start that way. Test F4 failed. The attempt counter was updated inside a database context manager and the handler then raised an HTTP error; SQLite rolls back when an exception leaves the context, so every failed guess was recorded and then undone, which meant unlimited guessing. '
         'We fixed it by committing before the error propagates. It is a good argument for executable tests over review for security logic.')

# ================================================================== 25 performance
s = slide('PERFORMANCE', 'Checks are cheap; the file ledger is the one that grows')
fit_pic(s, RES / 'bench.png', 0.5, 1.2, 5.4, 2.2, border=False)
table(s, 0.5, 3.55, 5.4, ['Ballots', 'Cast ms (file)', 'Sweep ms', 'Atlas append ms'], [
    ['100', f"{b['100']['cast_ms']:.0f}", f"{p['100']['sweep_ms']:.0f}", f"{M['100']['append_ms_median']:.0f}"],
    ['1,000', f"{b['1000']['cast_ms']:.0f}", f"{p['1000']['sweep_ms']:.0f}", f"{M['1000']['append_ms_median']:.0f}"],
    ['10,000', f"{b['10000']['cast_ms']:.0f}", f"{p['10000']['sweep_ms']:.0f}", f"{M['10000']['append_ms_median']:.0f}"]], [1.1, 1.5, 1.2, 1.6], size=10, row_h=0.36)
bullets(s, 6.2, 1.3, 3.3, 3.8, [f"Sweep at 10,000 ballots: {p['10000']['sweep_ms']:.0f} ms, about {(p['10000']['sweep_ms'] / b['10000']['sweep_ms'] - 1) * 100:.0f}% slower than before.", f"File ledger: a cast grows from {b['100']['cast_ms']:.0f} to {b['10000']['cast_ms']:.0f} ms because each append rewrites the file.",
                                 f"Atlas: about {M['1000']['append_ms_median']:.0f} ms at any size (network round trip).", 'The file is faster when small; Atlas wins on flat growth, concurrency control and living off-machine.'], size=10.5)
notes(s, f'Performance. The keyed chain and the three extra rules cost little: the sweep at ten thousand ballots takes about {p["10000"]["sweep_ms"]:.0f} milliseconds, roughly {(p["10000"]["sweep_ms"] / b["10000"]["sweep_ms"] - 1) * 100:.0f} percent slower than before. '
         f'The file ledger is the one that grows: a cast goes from about {b["100"]["cast_ms"]:.0f} milliseconds at a hundred ballots to {b["10000"]["cast_ms"]:.0f} at ten thousand, because every append rewrites the whole file. '
         f'Against Atlas an append costs about {M["1000"]["append_ms_median"]:.0f} milliseconds at any size, which is mostly network time on a mobile hotspot. So Atlas is not about raw speed at small sizes; it is about flat growth, concurrency control, and holding the ledger off the application machine.')

# ================================================================== comparative study (feature by feature, with sources)
MATRIX = [('Helios', 'N - - P P - - Y P'), ('Belenios', 'P P - P P P - Y P'), ('OpaVote', 'Y P - - - P - - P'), ('ElectionBuddy', 'P P - P P P P - P'),
          ('TapVoter', 'P P - P P P P Y P'), ('BetterVoting', 'P Y - P P P P Y Y'), ('Google Forms', '- - - P - N - - P'),
          ('FlexyVotes', 'Y Y Y P P Y N Y P'), ('VeriVote', '- - P P P P - Y P'), ('SecureVote', '- N - - P Y - - P'), ('PolyVote (our tests)', 'Y Y Y Y Y Y Y Y Y')]
s = slide('COMPARATIVE STUDY · COVERAGE MATRIX', 'Coverage matrix: who documents which feature')
x0, y0, cw, rh = 0.5, 1.12, 0.64, 0.3
label_shape(s, x0, y0, 2.4, rh, 'System', size=9, color=WHITE, fill=NAVY, bold=True, align=PP_ALIGN.LEFT, rounded=False)
for j in range(9):
    label_shape(s, x0 + 2.4 + j * cw, y0, cw - 0.04, rh, f'F{j + 1}', size=9, color=WHITE, fill=NAVY, bold=True, rounded=False)
for i, (nm, codes) in enumerate(MATRIX):
    y = y0 + (i + 1) * rh + 0.03
    last = i == len(MATRIX) - 1
    label_shape(s, x0, y, 2.4, rh - 0.04, nm, size=9, color=NAVY, fill=LAV if not last else CHIP, bold=True, align=PP_ALIGN.LEFT, rounded=False)
    for j, cd in enumerate(codes.split()):
        fill, col, txt = {'Y': (C_Y, GREEN, 'Yes'), 'P': (C_P, AMBER, 'Part'), 'N': (C_N, RED, 'No'), '-': (LAV, MUTED, '–')}[cd]
        label_shape(s, x0 + 2.4 + j * cw, y, cw - 0.04, rh - 0.04, txt, size=8.5, color=col, fill=fill, bold=True, rounded=False)
tb(s, 8.75, 1.12, 0.8, 3.2, [[('Yes', {'bold': True, 'color': GREEN})], [('documented', {'size': 8})], [('', {})], [('Part', {'bold': True, 'color': AMBER})], [('partly', {'size': 8})], [('', {})], [('No', {'bold': True, 'color': RED})], [('absent', {'size': 8})], [('', {})], [('–', {'bold': True, 'color': MUTED})], [('not documented', {'size': 8})]], size=10, color=INK)
tb(s, 0.5, 4.85, 9.0, 0.4, '33 systems read, 11 shown. F1 ranked counting · F2 many organisations · F3 database rules · F4 unlinked ballots · F5 keyed ledger and sweep · F6 email OTP · F7 QR voting · F8 receipt · F9 easy to run. '
   'Other rows: documentation we read. F5 is judged strictly (keyed chain, separate store, reconciling sweep, published attack results), so most systems score Part.', size=8.5, color=MUTED, italic=True)
notes(s, 'This matrix shows eleven of the thirty-three systems against the nine features. Green means documented, amber partly, red documented as absent, and a dash means we found nothing on the pages we read, which is not the same as absent. '
         'The bottom row is PolyVote, and it is all green only because those are the cells our own tests back. Read the other rows for what they show: FlexyVotes is nearly as complete and is the closest project we found; it is missing QR voting and has a weaker form of the ledger. '
         'BetterVoting covers many features but not database rules or a ledger of ballots. The cryptographic systems, Helios and Belenios, score amber on most of these because they solve the problem differently, with encryption. '
         'Feature five is judged strictly, which is why most rows are amber there. Nothing in the matrix says PolyVote is better overall; it says that one free small-election tool documenting every column is not something we found.')

compare_slide('FEATURES 3-4 · DATABASE RULES AND UNLINKED BALLOTS', 'Database rules and unlinked ballots', [
    ['FlexyVotes (GitHub)', 'Unique indexes and append-only triggers that block even raw SQL; ballot rows carry no voter key. Voters and encrypted emails share one PostgreSQL database.', 'F3 Yes · F4 Part'],
    ['VeriVote (GitHub)', 'Ballots stored without voter identity; triggers, CHECK and foreign-key rules are not documented.', 'F3 Part · F4 Part'],
    ['CIVS (Cornell)', 'Voter emails are erased once the election begins; ballots are stored under a hash of the receipt.', 'F3 – · F4 Part'],
    ['Helios, Belenios', 'Secrecy comes from encryption, not from a schema with no linking column; ballots sit on a public ballot box.', 'F3 – · F4 Part'],
    ['Democracy Live (USENIX 2021)', 'The authors report voter identity, selections and a browser fingerprint sent to the vendor.', 'F4 No']],
    [[('PolyVote: ', {'bold': True, 'color': NAVY}), ('6 of 7 direct SQL attempts refused by the engine, 13 of 13 API abuses refused, exactly 1 of 20 simultaneous casts accepted. An automated check finds no column shared by ballots and voters; emails live in a separate file.', {})],
     [('Verdict: ', {'bold': True, 'color': NAVY}), ('FlexyVotes is stronger on database rules (append-only triggers). Our known gap is the one attempt not refused: SQLite foreign keys apply per connection.', {})]],
    'Features three and four. FlexyVotes is the strongest comparison here: its unique indexes and append-only triggers refuse changes even from a raw SQL session, and its ballot rows have no voter key, although voters and encrypted emails live in the same PostgreSQL database. '
    'VeriVote stores ballots without identity but documents no database rules. CIVS erases voter emails once the election begins. Helios and Belenios get secrecy from encryption rather than from the schema. And the independent analysis of Democracy Live reported voter identity being sent to the vendor. '
    'For PolyVote, six of seven direct SQL attempts are refused, all thirteen API abuses are refused, and one of twenty simultaneous casts is accepted. An automated check finds no column shared by ballots and voters, and emails live in a separate file. '
    'We say plainly that FlexyVotes is stronger on database rules, and that our one miss is SQLite foreign keys, which apply per connection.')

compare_slide('FEATURE 5 · TAMPER-EVIDENT LEDGER', 'Tamper-evident ledgers: where a keyed chain differs', [
    ['FlexyVotes (GitHub)', 'SHA-256 chain per organisation inside PostgreSQL, verified every 6 hours; Merkle bulletin board; 204 tests, no published attack table.', 'F5 Part'],
    ['VeriVote (GitHub)', 'SHA-256 chain in MongoDB with an audit endpoint and a manual tamper demo; no HMAC key, no reconciliation.', 'F5 Part'],
    ['SecureVote (GitHub)', 'Hash-linked ledger with hashed one-time codes; no ranking; a single instance by design.', 'F5 Part'],
    ['BetterVoting (GitHub)', 'Audit log covers administrator actions (sharing a link, revealing a ballot link), not a chain of ballots.', 'F5 Part'],
    ['Helios, Belenios', 'A public, cryptographically verifiable ballot box: a stronger guarantee by a different mechanism.', 'F5 Part'],
    ['Voatz (USENIX 2020)', 'Claims a blockchain; the analysis found no public formal description and reported flaws.', 'F5 Part']],
    [[('PolyVote: ', {'bold': True, 'color': NAVY}), (f'an HMAC-keyed chain in a separate MongoDB store, a five-rule sweep and a published attack suite. {nd("patched")} of 13 attacks caught against {nd("baseline")} of 13 for the plain-chain design, the same in 3 runs; C6 and C10 only fail with the key.', {})],
     [('Verdict: ', {'bold': True, 'color': NAVY}), ('better than a plain chain against someone who can write to the database. Not a match for cryptographic verification, and whoever holds the key can still forge.', {})]],
    f'Feature five, the audit ledger. Hash-chained logs are common: FlexyVotes keeps one per organisation in PostgreSQL and verifies it every six hours, VeriVote keeps one in MongoDB, SecureVote has a hash-linked ledger, and BetterVoting has an audit log of administrator actions. '
    f'Helios and Belenios use a public verifiable ballot box, which is a stronger guarantee by a different mechanism, and Voatz claimed a blockchain that analysts could not verify. What we did not find documented elsewhere is the combination of a keyed chain, a separate store, a sweep that reconciles ballots, receipts, flags and candidates, and published attack results. '
    f'In our suite that combination catches {nd("patched")} of thirteen attacks against {nd("baseline")} for a plain chain, identical across three runs. The limit: whoever holds the key can still forge, and cryptographic systems remain stronger on verification.', row_h=0.4, size=9)

compare_slide('FEATURES 6-7 · SECOND FACTOR AND QR VOTING', 'Emailed codes exist elsewhere; so does QR sharing', [
    ['FlexyVotes (GitHub)', 'Keyed-hash one-time code with expiry, attempt limit and hourly rate limit; QR only for event ticket check-in.', 'F6 Yes · F7 No'],
    ['SecureVote (GitHub)', 'Hashed one-time code with expiry and attempt limits.', 'F6 Yes'],
    ['VeriVote (GitHub)', 'Email one-time code with rate limits.', 'F6 Part'],
    ['BetterVoting', 'A unique emailed link per voter; docs mention no one-time code or 2FA; a QR code shares the election link.', 'F6 Part · F7 Part'],
    ['TapVoter', 'Single-use key handed out by QR poster or email; no emailed second-factor code documented.', 'F6 Part · F7 Part'],
    ['Belenios', 'Default voter login is an emailed short code at voting time; hashing, expiry and limits not documented.', 'F6 Part']],
    [[('PolyVote: ', {'bold': True, 'color': NAVY}), ('password plus an emailed six-digit code (hashed, 5 minutes, single use, 3 guesses, resend limits). 14 of 14 tests pass, and one real defect (unlimited guesses) was found and fixed. A QR code on the vote page opens the ballot on any phone; a real ballot was cast from one.', {})],
     [('Verdict: ', {'bold': True, 'color': NAVY}), ('F6 alone is not unique: FlexyVotes and SecureVote have it too. What we did not find documented is a scan-to-vote QR flow together with an emailed code.', {})]],
    'Features six and seven. Emailed one-time codes are not new: FlexyVotes and SecureVote hash the code and limit attempts, VeriVote rate-limits it, and Belenios sends a short code by default. BetterVoting and TapVoter use single-use links or keys, and both share them by QR. '
    'PolyVote adds a six-digit code, hashed, valid five minutes, single use, three guesses, with resend limits, and fourteen of fourteen tests pass, including the one that found a real defect. A QR code on the vote page opens the ballot on any phone, and we cast a real ballot from one. '
    'So feature six alone is not unique. The combination of scan-to-vote with an emailed code is what we did not find documented elsewhere, and we say so in those words.', row_h=0.4, size=9)

s = slide('COMPARATIVE STUDY · CLOSEST PROJECTS', 'The three closest projects, and what each lacks')
table(s, 0.5, 1.12, 9.0, ['Closest project (source)', 'What it has', 'What we found it does not document'], [
    ['FlexyVotes, Django and PostgreSQL (github.com/deOpty/flexyvotes)', 'Many organisations; instant-runoff and STV; triggers that block raw SQL; ballots with no voter key; hash-chained audit log; hashed single-use email OTP',
     'QR scan-to-vote; an HMAC-keyed chain; a separate document store and email database; a reconciling sweep; published attack results'],
    ['VeriVote, Node, React and MongoDB (github.com/9022574361/Online_Voting_System)', 'SHA-256 chain in MongoDB with an audit endpoint; ballots without voter identity; email OTP with rate limits; receipt hash',
     'Ranked counting; many organisations; database rules; HMAC key; reconciliation; automated attack suite'],
    ['BetterVoting (github.com/Equal-Vote/bettervoting)', 'Ranked-choice voting; teams; QR sharing; receipts; free and open source (AGPL)',
     'Database-enforced rules; a ledger of ballots (its audit log covers admin actions); one-time-code factor; reconciliation and attack tests']],
    [2.7, 3.3, 3.0], size=9, header_size=9.5, row_h=0.85, head_h=0.32)
card(s, 0.5, 4.2, 9.0, 1.0, fill=LAV)
tb(s, 0.7, 4.27, 8.6, 0.9, [[('What we claim: ', {'bold': True, 'color': NAVY}), ('every single feature exists somewhere, so PolyVote is not the first or the only one. We found no free small-election tool documenting all of them together. ', {}),
                              ('What we do not claim: ', {'bold': True, 'color': NAVY}), ('to be more secure than Helios, Belenios or ElectionGuard. Limits: GitHub code search and non-English repositories were not covered.', {})]], size=10, color=INK)
notes(s, 'The three closest projects. FlexyVotes, a Django and PostgreSQL project created in August, is the nearest: it has many organisations, instant-runoff and STV, triggers that block raw SQL, ballots with no voter key, a hash-chained audit log and hashed email codes. '
         'We did not find in it QR scan-to-vote, an HMAC-keyed chain, a separate document store or email database, a sweep that reconciles ballots, receipts, flags and candidates, or published attack results. '
         'VeriVote has a SHA-256 chain in MongoDB with an audit endpoint and email codes, but no ranked counting, organisations or database rules. BetterVoting has ranked-choice, teams, QR sharing and receipts, but no database rules, ballot ledger or one-time code. '
         'So our claim is narrow and checkable: every feature exists somewhere, and we found no free small-election tool documenting all of them together. We do not claim to be more secure than the cryptographic systems. The search had limits, which we state.')

s = slide('COMPARATIVE STUDY · VERDICT', 'Best for small elections, not a Helios replacement')
card(s, 0.5, 1.2, 4.4, 3.2)
chip(s, 0.7, 1.34, 'PolyVote IS A GOOD FIT WHEN')
bullets(s, 0.7, 1.75, 4.0, 2.6, ['A club, council or class needs ranked-choice results.', 'Someone must be able to run it in an afternoon, free.', 'You need proof that edits and deletions are caught.', 'Voters should confirm themselves by email and vote from a phone.'], size=11)
card(s, 5.1, 1.2, 4.4, 3.2)
chip(s, 5.3, 1.34, 'CHOOSE HELIOS / BELENIOS WHEN')
bullets(s, 5.3, 1.75, 4.0, 2.6, ['The administrator itself cannot be trusted.', 'Voters must verify their own ballot content.', 'Coercion or vote selling is a real threat.', 'A public cryptographic audit is required.'], size=11)
card(s, 0.5, 4.55, 9.0, 0.55, fill=LAV)
tb(s, 0.7, 4.6, 8.6, 0.45, 'Our claim: for small elections, PolyVote adds database-level rules and tested tamper detection to an easy setup. It is not the strongest on verifiability.', size=10.5, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'The verdict. For the problem we target, small and medium elections such as clubs, councils and classes, PolyVote is a good fit: ranked-choice results, an afternoon to set up, free to run, proof that edits and deletions are caught, and voters who confirm by email and can vote from a phone. '
         'The cryptographic systems are the better choice when the administrator cannot be trusted, when voters must verify their own ballot content, when coercion is a threat, or when a public cryptographic audit is required. We say this openly because it makes the claim credible. '
         'Our claim is modest: for small elections PolyVote adds database-level rules and tested tamper detection to an easy setup, and it is not the strongest on verifiability.')

# ================================================================== 27 before/after
s = slide('REVIEW 2 DESIGN VERSUS FINAL DESIGN', 'What improved, measured')
table(s, 0.5, 1.2, 9.0, ['Measure', 'Review 2', 'Final'], [
    ['Tampering detected automatically', f'{nd("baseline")} of 13', f'{nd("patched")} of 13'], ['Forged receipt or chain rewrite', 'Undetected', 'Detected (key)'],
    ['Candidate renaming', 'Undetected', 'Detected (sealed roster)'], ['Voter authentication', 'Password', 'Password + emailed code'],
    ['Ledger storage', 'Local file', 'MongoDB Atlas'], ['Ledger append at 10,000 ballots', f"{b['10000']['cast_ms']:.0f} ms (file, whole cast)", f"~{M['1000']['append_ms_median']:.0f} ms (Atlas, flat)"],
    ['Sweep at 10,000 ballots', f"{b['10000']['sweep_ms']:.0f} ms", f"{p['10000']['sweep_ms']:.0f} ms"], ['Access', 'Local only', 'Public link + QR'],
], [4.0, 2.7, 2.3], size=10.5, row_h=0.42)
notes(s, 'The summary of improvements over our own Review 2 design. Automatic detection of tampering rises from six to twelve of thirteen. Forged receipts, rebuilt chains and renamed candidates move from undetected to detected. Authentication goes from password only to password plus an emailed code. '
         'The ledger moves to Atlas, and the system becomes publicly reachable. The cost is small: the sweep at ten thousand ballots goes from about one hundred and twenty-nine to about one hundred and forty-seven milliseconds.')

# ================================================================== website checklist
WC = json.loads((RES / 'web_checklist.json').read_text(encoding='utf-8'))['results']
npass, nna, nfail = (sum(r['result'] == k for r in WC) for k in ('PASS', 'N/A', 'FAIL'))
s = slide('THE WEB PAGE · LAUNCH CHECKLIST', f'Website launch checklist: {npass} pass, {nna} N/A, {nfail} fail')
colr = {'PASS': GREEN, 'N/A': AMBER, 'FAIL': RED}
for k, chunk in enumerate((WC[:11], WC[11:])):
    tb(s, 0.5 + k * 2.95, 1.15, 2.85, 3.7, [[(f"{r['result']:<4} ", {'bold': True, 'color': colr[r['result']], 'font': 'Consolas', 'size': 8.5}), (r['item'], {})] for r in chunk], size=10.5, color=INK, after=7)
fit_pic(s, ASSETS / 'screens' / 'web_home.png', 6.45, 1.15, 3.05, 1.9)
fit_pic(s, ASSETS / 'screens' / 'web_404.png', 6.45, 3.15, 3.05, 1.9)
tb(s, 0.5, 4.85, 5.8, 0.45, 'N/A: HTTPS (a local run; the host provides it), WebP (no raster images in the pages), Google Analytics and Search Console (need the owner\'s own IDs).', size=8.5, color=MUTED, italic=True)
notes(s, f'A friend shared a launch checklist for websites, and we turned it into an automated check. The script experiments/web_checklist.py tests a running copy of the site against twenty-one items and prints pass, fail or not applicable with the evidence. Result on a local run of the current code: {npass} pass, {nna} not applicable, {nfail} fail. '
         'The pass items include a pre-rendered page shell with one heading and unique title and description for each page, robots.txt and a sitemap, canonical tags, a link-preview image, a custom 404 page, 301 redirects, lazy-loaded routes, structured data for the organisation and breadcrumbs, a privacy policy, and a contact form that stores messages and ignores bots. '
         'The four not-applicable items are HTTPS, because a local run is plain http and the hosting provider supplies it; WebP, because the pages have no raster images; and Google Analytics and Search Console, which need the owner\'s own identifiers and are built in but switched off. '
         'To be exact, the page shell is pre-rendered HTML that the React app then replaces; it is not full server-side rendering. We will rerun the same script against the public link after the next deploy.')

# ================================================================== privacy and ethics
s = slide('PRIVACY AND ETHICS', 'Privacy and ethics: what is stored, and where')
table(s, 0.5, 1.12, 5.5, ['Data', 'Where it lives', 'Stored as'], [
    ['Registration number', 'Election database', 'Roster entry'],
    ['Password', 'Election database', 'SHA-256 hash only'],
    ['Email address', 'Verification database (separate file)', 'Never stored with ballots'],
    ['One-time code', 'Verification database', 'Keyed hash only; 5 min, one use'],
    ['Your ballot', 'Election database', 'Random token; no voter column'],
    ['Receipt block', 'Audit ledger', 'Token and hash of the ranks'],
    ['Contact message', 'Verification database', 'Admins only']],
    [1.5, 2.2, 1.8], size=9, header_size=9.5, row_h=0.43, head_h=0.3)
card(s, 6.2, 1.12, 3.3, 3.95, fill=LAV)
chip(s, 6.38, 1.24, 'ETHICS AND LIMITS')
bullets(s, 6.38, 1.62, 3.0, 3.4, [('Sample data:', 'the demo uses sample voters and resets on restart.'), ('Officers see more:', 'the roster, emails and an outbox that lists codes for ten minutes. We kept it so a demo never stalls; a real election should switch it off.'),
                                   ('Receipts:', 'prove a ballot is counted, not its content.'), ('No tracking:', 'no tracking cookies; analytics is off unless the operator enables it.'),
                                   ('Not for binding votes:', 'no independent review yet; passwords use plain SHA-256.')], size=9.5, after=3)
tb(s, 0.5, 4.62, 5.5, 0.6, 'The ballot table and the voter table share no column, so the database cannot say who cast which ballot. A person with direct file access could read ballots, but not link them to people.', size=10, color=NAVY, bold=True)
notes(s, 'Privacy and ethics, taken from our own privacy page. The table shows where each piece of data lives. The registration number and a password hash are in the election database. The voter\'s email address is in a separate verification database and is never stored with ballots. '
         'The one-time code is stored only as a keyed hash and lasts five minutes. The ballot is stored under a random token with no voter column, and the receipt block holds the token and a hash of the ranks. Contact messages are readable by administrators only. '
         'The ethical points we want to be upfront about. The demo uses sample data and resets when the server restarts. Election officers can see the roster, the emails and an outbox that lists codes for ten minutes; we kept the outbox so a live demo never stalls on a slow email, and a real election should switch it off. '
         'A receipt shows a ballot is counted but not what it says, though anyone holding both the token and database access could see that one ballot. There are no tracking cookies. And this is a course project with no independent security review and plain SHA-256 password hashing, so it is not for binding elections yet.')

# ================================================================== 28 limits + future
s = slide('LIMITATIONS AND FUTURE WORK', 'What we do not claim, and what comes next')
table(s, 0.5, 1.2, 9.0, ['Limitation', 'Direction'], [
    ['Insider with key and both stores can forge (A6)', 'Publish the chain head to an external witness; managed secret store'],
    ['Roster injection is not detected (A7)', 'Committed or signed roster, checked at sweep time'],
    ['Not end-to-end verifiable; receipt shows recorded, not content', 'Cast-as-intended mechanism, or a verifiable protocol if needed'],
    ['Passwords stored as plain SHA-256; default admin login', 'Salted, slow hashing; forced first-login change'],
    ['Email is a weak second factor', 'Authenticator app (TOTP) or printed one-time slip'],
    ['IRV ties broken arbitrarily; no statistical audit', 'Published tie rule; risk-limiting audit'],
    ['SQLite foreign keys are per connection; single node', 'Oracle or PostgreSQL with PL/SQL, roles; cloud platform'],
], [4.6, 4.4], size=10, row_h=0.46)
notes(s, 'What we do not claim. An insider holding the key and both stores can still forge a chain; the remedy is an external witness for the chain head. Roster injection is not detected; we need a committed roster. We are not end-to-end verifiable. '
         'Passwords are stored with plain SHA-256, which we know should be a salted slow hash. Email is a weak factor compared with an authenticator app. Ties in instant-runoff are broken arbitrarily. And SQLite is a single-node engine with per-connection foreign keys, so the planned move to Oracle with PL/SQL and roles also fixes that.')

# ================================================================== glossary
s = slide('GLOSSARY', 'Glossary in plain words')
GL = [('Hash', 'A fixed-length fingerprint of data. Change one character and the fingerprint changes completely.'),
      ('HMAC', 'A hash made with a secret key, so only someone holding the key can produce a valid one.'),
      ('Hash chain', 'Each record stores the previous record\'s hash, so editing one breaks every later link.'),
      ('Ledger, block', 'The append-only list of receipts; one block for each ballot.'),
      ('Instant-runoff', 'Rank candidates; last place drops out each round and its ballots move on, until someone has a majority.'),
      ('OTP', 'One-time password: a short code that works once and expires.'),
      ('Roster hash', 'A fingerprint of the candidate list, sealed into every block.'),
      ('Receipt token', 'A random code that shows a ballot is recorded. It does not show the vote.'),
      ('Trigger, CHECK, UNIQUE', 'Rules the database enforces itself, even against direct SQL.'),
      ('Integrity sweep', 'Recomputes the election from the database and compares it with the ledger.'),
      ('Polyglot persistence', 'Different kinds of database for different jobs: SQLite and MongoDB here.'),
      ('Multi-tenant', 'Many organisations share one install, each with its own elections.')]
for k in range(2):
    table(s, 0.5 + k * 4.65, 1.12, 4.35, ['Term', 'In plain words'], [[a_, b_] for a_, b_ in GL[k * 6:(k + 1) * 6]], [1.2, 3.15], size=9, header_size=9.5, row_h=0.62, head_h=0.3)
notes(s, 'A glossary for anyone new to these words. A hash is a fingerprint of data. An HMAC is a hash made with a secret key, so only the key holder can produce a valid one. A hash chain links records so that editing one breaks all later links. The ledger is the append-only list of receipts, one block per ballot. '
         'Instant-runoff is the counting method: rank candidates, and each round the last-place candidate drops out and their ballots move to their next choice until someone has a majority. An OTP is a one-time password, a short code that works once and expires. '
         'The roster hash is a fingerprint of the candidate list sealed into every block. The receipt token shows a ballot is recorded but not how it voted. Triggers, CHECK and UNIQUE constraints are rules the database enforces itself. '
         'The integrity sweep recomputes the election from the database and compares it with the ledger. Polyglot persistence means using different databases for different jobs, and multi-tenant means many organisations share one install.')

# ================================================================== evidence map
s = slide('EVIDENCE', 'Evidence: where every claim can be checked')
table(s, 0.5, 1.12, 9.0, ['Claim in this deck', 'How it was produced', 'Where to look'], [
    [f'Tampering caught: {nd("baseline")} of 13 (old), {nd("patched")} of 13 (final)', 'Executable suite, 3 identical runs', 'experiments/results/summary.json, detection.png'],
    ['Database refuses bad votes (6 of 7; 13 of 13; 1 of 20)', 'Direct SQL and API tests', 'experiments/run_experiments.py'],
    ['14 of 14 one-time-code tests', 'Tests F1 to F14 on a throwaway copy', 'experiments/run_experiments.py'],
    [f"Sweep +{(p['10000']['sweep_ms'] / b['10000']['sweep_ms'] - 1) * 100:.0f}% at 10,000 ballots; Atlas append flat", 'Benchmarks, median of 3 runs', 'bench.png, mongo_bench.json'],
    [f'Website checklist {npass} / {nna} / {nfail}', 'Automated check of 21 items', 'experiments/web_checklist.py, web_checklist.json'],
    ['What 33 other systems offer', 'Their own pages, READMEs, papers; a URL for every cell', 'docs/review3/uniqueness_evidence.md'],
    ['Closest projects and their gaps', 'FlexyVotes code and docs read directly', 'docs/review3/uniqueness_evidence.md']],
    [3.4, 2.9, 2.7], size=9, header_size=9.5, row_h=0.41, head_h=0.3)
card(s, 0.5, 4.6, 9.0, 0.6, fill=LAV)
tb(s, 0.7, 4.65, 8.6, 0.5, [[('Search method: ', {'bold': True, 'color': NAVY}), ('23 web queries, 20 GitHub repository searches, 33 systems, on 23 October 2026. ', {}), ('Not covered: ', {'bold': True, 'color': NAVY}), ('GitHub code search, non-English and private repositories, commercial internals.', {})]], size=10, color=INK)
notes(s, 'This is the back-up slide for any question that starts with how do you know. Each claim in the deck maps to something that can be rerun or opened. The tampering numbers come from the executable suite, run three times with identical outcomes. The prevention and one-time-code results come from the same experiments script. '
         'The benchmark numbers are medians of three runs, with the Atlas figures from a separate script. The website checklist is an automated script with its output saved. And everything we say about other systems comes from their own pages, READMEs and papers, with a URL for every cell in the evidence file. '
         'The search method and its limits are at the bottom: twenty-three web queries, twenty GitHub repository searches, thirty-three systems, on the twenty-third of October, without GitHub code search or non-English and private repositories.')

# ================================================================== 29-30 conferences (from research)
# India only, host institution in the NIRF top 100 (India Rankings 2025). Source: docs/review3/conferences_nirf.md, checked 2026-10-23.
s = slide('INDIA ONLY · NIRF TOP-100 HOSTS · OPEN TODAY', 'India only, NIRF top-100 hosts, cheapest first')
table(s, 0.4, 1.08, 9.2, ['#', 'Venue', 'Host university (NIRF 2025 rank)', 'Submit by', 'Student fee, INR', 'Held', 'Indexing'], [
    ['1', 'SCES-2027', 'MNNIT Allahabad, Prayagraj (Engineering 62)', '15 Nov 2026*', '5,900 incl. GST', '12-14 Mar 2027', 'Claimed'],
    ['2', 'IEEE COEP CON 2027', 'COEP Technological Univ., Pune (Engineering 90)', '31 Mar 2027', '6,000†', '4-6 Jun 2027', 'Claimed'],
    ['3', 'IEEE SANKALP 2027', 'ABV-IIITM, Gwalior (Engineering 96)', '30 Nov 2026', '7,000', '9-11 Apr 2027', 'IEEE record #73342 shown'],
    ['4', 'ICESICSC-2027', 'KIIT, Bhubaneswar (Overall 27)', '30 Oct 2026', '9,000', '20-21 Feb 2027', 'Claimed'],
    ['5', 'Confluence 2027', 'Amity University, Noida (Overall 37)', '4 Dec 2026', '9,440 incl. GST', '21-22 Jan 2027', 'IEEE record #71526 shown'],
    ['6', 'INDIACom-2027', 'BVICAM, Bharati Vidyapeeth, New Delhi (parent only, University 59)', '7 Dec 2026', '9,440 incl. GST', '7-9 Apr 2027', 'Claimed'],
    ['7', 'i-PACT 2027', 'VIT, Vellore (Overall 21)', '31 May 2027', '12,000', '2-3 Sep 2027', 'Claimed'],
    ['8', 'ICICC-2027', 'Shaheed Sukhdev College, Univ. of Delhi (parent only, Overall 15)', '30 Oct 2026', '13,000', '5-6 Feb 2027', 'Claimed (LNNS "approved")']],
    [0.3, 1.45, 2.85, 1.0, 1.15, 1.15, 1.5], size=8, header_size=8.5, row_h=0.4, head_h=0.3)
tb(s, 0.4, 4.7, 9.2, 0.6, '*Page marks the date tentative.  †Fee read from a flattened table.  "IEEE record shown" means a record number is on the official page, not checked on the IEEE site; nothing here is confirmed for IEEE Xplore. Also qualify, but off-topic or no published fee: ICSEAMS (Amrita), ICCIDS (SSN), PerCom work-in-progress (BITS Pilani Goa), NCC (IISc). Dropped, host not in the top 100: ICRCICN, IEM-ICDC, iConCISE, ICPCSN.', size=8, color=MUTED, italic=True)
notes(s, 'We narrowed the list to conferences held in India and hosted by an institution in the NIRF top one hundred, using the 2025 India Rankings, which are the latest published; a 2026 edition has not been released, so ranks could change. '
         'The cheapest is SCES at Motilal Nehru National Institute in Prayagraj, about five thousand nine hundred rupees. SANKALP at the IIIT in Gwalior costs seven thousand and shows an IEEE record number. ICESICSC at KIIT closes on the thirtieth of October. Confluence at Amity Noida is nine thousand four hundred and forty with tax and also shows an IEEE record number. '
         'INDIACom and ICICC are borderline, because only the parent university is ranked, not the institute or college that hosts. i-PACT is on our own campus at VIT. '
         'Indexing: a record number on an official page is not confirmation of IEEE Xplore, and every other venue only claims it. We dropped ICRCICN, IEM-ICDC, iConCISE and ICPCSN because their hosts are not in the top one hundred.')

s = slide('RECOMMENDED SUBMISSION ORDER', 'One venue at a time: dual submission is not allowed')
table(s, 0.5, 1.2, 9.0, ['Step', 'Venue', 'Host university', 'Submit by', 'Why this order'], [
    ['1', 'IEEE SANKALP 2027', 'ABV-IIITM Gwalior', '30 Nov 2026', 'IEEE record number shown; security and distributed-database tracks; INR 7,000'],
    ['2', 'Confluence 2027', 'Amity University, Noida', '4 Dec 2026', 'IEEE record number shown; INR 9,440; fast decision'],
    ['3', 'ICESICSC-2027', 'KIIT, Bhubaneswar', '30 Oct 2026', 'Closes in 7 days; only if the paper already fits their template'],
    ['4', 'INDIACom-2027', 'BVICAM, Bharati Vidyapeeth', '7 Dec 2026', 'Borderline host: only the parent university is ranked'],
    ['5', 'i-PACT 2027', 'VIT, Vellore', '31 May 2027', 'Our own campus, but a power-engineering conference']],
    [0.6, 1.9, 2.1, 1.2, 3.2], size=9.5, row_h=0.5)
tb(s, 0.5, 4.2, 9.0, 1.0, [[('Before submitting: ', {'bold': True, 'color': NAVY}), ('check the IEEE site for each record number, recheck the deadline and the NIRF edition (a 2026 list may be published), remove author names where double-blind, and follow each venue\'s AI-disclosure rule. Journals cost USD 2,000 to 3,000 in fees: only as a later extended version.', {})]], size=10.5)
notes(s, 'The recommended order within the India and NIRF filter, remembering that we cannot submit to two venues at the same time. SANKALP at the IIIT in Gwalior is first: it shows an IEEE record number, has security and distributed-database tracks, and costs seven thousand rupees. '
         'Confluence at Amity Noida is second, also with an IEEE record number. ICESICSC at KIIT closes on the thirtieth of October, so it is only realistic if the paper already fits its template. INDIACom is borderline because only the parent university is ranked. i-PACT is on our own campus but is a power-engineering conference. '
         'Before submitting, verify each record number on the IEEE site, recheck deadlines and the NIRF edition, remove author names for double-blind venues, and follow each venue\'s AI-disclosure policy.')

# ================================================================== project conclusion
s = slide('PROJECT CONCLUSION', 'Planned versus delivered')
table(s, 0.5, 1.1, 9.0, ['Item planned at Reviews 1 and 2', 'Status', 'Note'], [
    ['Multi-tenant normalised schema, views, trigger', 'Delivered', 'On SQLite'],
    ['Instant-runoff tally and admin console', 'Delivered', 'Round-by-round results'],
    ['Hash-chained receipts and integrity sweep', 'Delivered, extended', 'Keyed chain, five sweep rules'],
    ['MongoDB ledger', 'Delivered', 'Atlas, with a file fallback'],
    ['Second factor for the voter', 'Delivered', 'Emailed one-time code'],
    ['Public hosting and phone voting', 'Delivered', 'Public link, QR code, free hosted demo configured'],
    ['Comparative study and evaluation', 'Delivered', '47 test scenarios; 33 systems read'],
    ['True cloud platform', 'Partly', 'Free-tier hosting only; no managed cloud database'],
    ['Oracle with PL/SQL procedures and DCL roles', 'Left out', 'SQLite kept; the path is on the next slide'],
    ['POSITION entity', 'Left out', 'Deferred']],
    [4.1, 1.7, 3.2], size=9.5, header_size=9.5, row_h=0.37, head_h=0.32)
notes(s, 'The conclusion. Against what we planned at Reviews one and two: the multi-tenant schema with views and the trigger, the instant-runoff tally and admin console, the hash-chained receipts and integrity sweep, now keyed and with five rules, the MongoDB Atlas ledger, a second factor for the voter, '
         'public hosting with phone voting, and the comparative study with forty-seven test scenarios are all delivered. A true cloud platform is only partly done: we have free-tier hosting configured but no managed cloud database. '
         'Two items were left out: Oracle with PL/SQL procedures and DCL roles, because we kept SQLite, and the POSITION entity, which was deferred. The next slide explains why we chose SQLite and how Oracle would be possible.')

s = slide('WHY SQLITE · AND THE PATH TO ORACLE', 'Why SQLite, and how Oracle is possible')
card(s, 0.5, 1.2, 4.4, 3.35)
chip(s, 0.7, 1.34, 'WHY WE CHOSE SQLITE')
bullets(s, 0.7, 1.75, 4.0, 2.8, [('Nothing to install:', 'one file, no server; anyone runs it on a laptop or free hosting with one command.'),
                                  ('Repeatable tests:', 'the evaluation copies the database file into a throwaway sandbox, so all 47 scenarios rerun the same way.'),
                                  ('Cost and time:', 'Oracle needs a licence or cloud account and set-up that a semester project and a hotspot demo cannot rely on.'),
                                  ('Trade-off we accept:', 'foreign keys only where switched on, one node, no roles.')], size=10.5, after=4)
card(s, 5.1, 1.2, 4.4, 3.35, fill=LAV)
chip(s, 5.3, 1.34, 'HOW ORACLE WOULD FIT')
bullets(s, 5.3, 1.75, 4.0, 2.8, [('Schema:', 'the 5 tables, 1 trigger and 2 views sit in one file; turn AUTOINCREMENT into identity columns and the trigger into PL/SQL.'),
                                  ('Driver:', 'database calls are in a handful of modules; swap sqlite3 for python-oracledb and change the placeholders.'),
                                  ('Add what SQLite lacks:', 'GRANT-based roles and PL/SQL procedures; foreign keys always on, which closes the one gap our tests found.'),
                                  ('Unchanged:', 'the MongoDB ledger, the one-time-code module and the React app.')], size=10.5, after=4)
card(s, 0.5, 4.7, 9.0, 0.45, fill=LAV)
tb(s, 0.7, 4.73, 8.6, 0.4, 'This is the planned path, not a result: we have not run it on Oracle.', size=10.5, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'Why SQLite, and how Oracle is possible. We chose SQLite because there is nothing to install, it is one file, anyone can run the project with one command on a laptop or free hosting, and our evaluation copies that file into a throwaway sandbox so the forty-seven scenarios rerun identically. '
         'Oracle would need a licence or a cloud account and a set-up that a semester project and a demo over a mobile hotspot cannot rely on. The trade-offs we accept are that foreign keys apply only on connections that switch them on, that it is a single node, and that there are no roles. '
         'Moving to Oracle is a migration rather than a redesign. The schema is five tables, one trigger and two views in a single file, so AUTOINCREMENT becomes identity columns and the trigger becomes a PL/SQL trigger. The database calls are in a handful of modules, so we would swap the sqlite3 driver for python-oracledb and change the placeholders. '
         'Then we would add what SQLite lacks, GRANT-based roles and PL/SQL procedures, with foreign keys always on, which closes the one gap our tests found. The MongoDB ledger, the one-time-code module and the React app would not change. To be clear, this is the planned path and we have not run it on Oracle.')

# Review 2 roadmap slide: say plainly what happened to its open items
s20 = prs.slides[R2_COUNT - 2]
def copy_fill(src, dst):
    from copy import deepcopy
    sp_src, sp_dst = src._element.spPr, dst._element.spPr
    for tag in ('a:solidFill', 'a:noFill', 'a:gradFill', 'a:ln'):
        for el in sp_dst.findall(qn(tag)):
            sp_dst.remove(el)
    for tag in ('a:solidFill', 'a:noFill', 'a:gradFill', 'a:ln'):
        for el in sp_src.findall(qn(tag)):
            sp_dst.append(deepcopy(el))


chip1, chip2, chip3 = by_name(s20, 169), by_name(s20, 173), by_name(s20, 177)
copy_fill(chip1, chip2)
set_runs_text(chip2, ['REVIEW 2 · DONE'])
set_runs_text(by_name(s20, 174), ['Working implementation with live outputs and a tamper demonstration.'])
set_runs_text(chip3, ['REVIEW 3 · NOW'])
set_runs_text(by_name(s20, 178), ['This is the final review: MongoDB Atlas, emailed code, public hosting, evaluation and comparison with existing systems.'])
set_runs_text(by_name(s20, 180), ['Delivered · ', 'MongoDB Atlas ledger, emailed one-time code, public link and QR voting', 'Evidence · ', '47 test scenarios and a comparison with 33 systems', 'Left out · ', 'Oracle with PL/SQL and DCL roles, and the POSITION entity (SQLite kept)'])
notes(s20, 'Looking at the three reviews together. Review 1 presented the design and Review 2 presented the working implementation with live outputs and a tamper demonstration; both are done. '
           'This is Review 3, the final review. We delivered the MongoDB Atlas ledger, the emailed one-time code, public hosting with phone voting, a 47-scenario evaluation and a comparison with 33 existing systems. '
           'Oracle with PL/SQL procedures and DCL roles, and the POSITION entity, were left out, and SQLite was kept; the conclusion slides at the end explain why and how Oracle would be possible.')

# slide 2: Review 1 done, Review 2 done, Review 3 now
s2 = prs.slides[1]
S2 = {sh.name: sh for sh in s2.shapes}
set_runs_text(S2['Kicker'], ['WHERE WE STAND · FINAL REVIEW'])
set_runs_text(S2['Title'], ['Reviews 1 and 2 are done; this is Review 3'])
set_runs_text(S2['Rounded Rectangle 6'], ['DONE'])
set_runs_text(S2['TextBox 7'], ['Review 1'])
set_runs_text(S2['Rounded Rectangle 10'], ['DONE'])
set_runs_text(S2['TextBox 11'], ['Review 2'])
set_runs_text(S2['TextBox 12'], ['A working system: React voter booth and admin console, FastAPI service, SQLite schema with trigger and views, instant-runoff tally, hash-chained receipts and a live tamper test.'])
set_runs_text(S2['Rounded Rectangle 14'], ['NOW'])
set_runs_text(S2['TextBox 15'], ['Review 3 · final review'])
set_runs_text(S2['TextBox 16'], ['MongoDB Atlas ledger, emailed one-time code and QR voting, public hosting, a 47-scenario evaluation and a comparison with existing systems.'])
set_runs_text(S2['TextBox 18'], ['Done'])
set_runs_text(S2['TextBox 19'], ['Reviews 1 and 2'])
hint = S2['TextBox 20']
set_runs_text(hint, ['We did not use Oracle: ', 'SQLite stood in for it throughout (see the conclusion slides).'])
for para in list(hint.text_frame.paragraphs)[1:]:
    para._p.getparent().remove(para._p)
notes(s2, 'A short recap of where we stand. Review 1 is done: we presented the design, the relational schema and ER diagram, the security approach, the literature review and a planned architecture on Oracle, MongoDB and Streamlit. '
          'Review 2 is done: a working system with a React voter booth and admin console, a FastAPI service, a SQLite schema with trigger and views, the instant-runoff tally, hash-chained receipts and a live tamper test. '
          'Review 3, this one, is the final review: the MongoDB Atlas ledger, the emailed one-time code with QR voting, public hosting, a 47-scenario evaluation and a comparison with existing systems. '
          'One thing to flag early: we did not use Oracle. SQLite stood in for it throughout, and the conclusion slides at the end explain why and how Oracle would fit.')

# ================================================================== thank-you slide to the end
set_runs_text(by_name(thanks_slide, 189), ['PROJECT CONCLUSION · REVIEW 3'])
N[0] += 1
set_runs_text(by_name(thanks_slide, 191), [FOOT.format(n=N[0])])
for sh in list(thanks_slide.shapes):
    if sh.name in ('TextBox 192', 'TextBox 193'):
        sh._element.getparent().remove(sh._element)
tb(thanks_slide, 0.38, 1.75, 5.6, 0.3, 'Questions and discussion', size=16, color=INK, bold=True)
tb(thanks_slide, 0.38, 2.25, 5.6, 2.2, [
    [('Source code and documents', {'bold': True, 'color': NAVY})],
    [('github.com/Tharakeshtj/polyvote-election-platform', {'size': 11})]], size=12, color=INK, after=3)
notes(thanks_slide, 'Thank you. To summarise: PolyVote now enforces election rules in the database, seals every ballot in a keyed ledger on MongoDB Atlas, confirms voters with an emailed one-time code, runs publicly, and is evaluated by an executable suite that shows '
                    'automatic detection of tampering rising from six to twelve of thirteen scenarios, with the remaining gaps stated openly. The code and documents are on GitHub, and we are happy to take questions or run any part of the demonstration again.')
el = prs.slides._sldIdLst[R2_COUNT - 1]
prs.slides._sldIdLst.remove(el)
prs.slides._sldIdLst.append(el)

prs.save(str(OUT))
print('wrote', OUT, '| slides', len(prs.slides))
