"""Build docs/PolyVote_Review3.pptx: the Review 3 extension of the Review 2 deck (same template, 31 slides, speaker notes on each).

    python docs/review3/build_deck.py
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REVIEW2 = ROOT / 'docs' / 'PolyVote_Review2.pptx'
OUT = ROOT / 'docs' / 'PolyVote_Review3.pptx'
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


# ------------------------------------------------------------------ keep the title and thank-you slides, drop the rest
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)
for el in ids[1:-1]:
    prs.part.drop_rel(el.rId)
    sldIdLst.remove(el)
title_slide, thanks_slide = prs.slides[0], prs.slides[1]
from pptx.opc.packuri import PackURI  # noqa: E402
thanks_slide.part.partname = PackURI('/ppt/slides/slide90.xml')   # keep new slide part names from colliding with it
set_runs_text(by_name(title_slide, 26), ['Review 3 · Final Project Review · Guide: Dr. Katari Balakrishna'])
set_runs_text(by_name(title_slide, 28), [FOOT.format(n=1)])
notes(title_slide,
      'Good morning, sir, and everyone. This is Review 3, the final review of PolyVote, our ranked-choice election platform with a tamper-evident audit trail. '
      'Review 1 presented the design and Review 2 showed the working system. Today we show the completed system: a MongoDB Atlas ledger, a keyed hash chain, '
      'a second authentication factor using emailed one-time codes, public hosting, and an evaluation that tests our claims instead of asserting them. '
      'We will also show a short live demonstration of the version with email verification switched on.')

N = [1]


def slide(kicker, title):
    N[0] += 1
    s = new_slide()
    frame(s, kicker, title, N[0])
    return s


# ================================================================== 2 where we stand
s = slide('REVIEW 3 · WHERE WE STAND', 'What we submitted, what we built, what is new today')
cards = [('SUBMITTED', 'Reviews 1 and 2', 'Design, schema, ER and data-flow diagrams, literature; then a working React + FastAPI system, instant-runoff tally, hash-chained receipts and a live tamper test.'),
         ('FEEDBACK', 'At Review 2', 'Confirm the voter with a second factor (OTP or face ID); finish MongoDB and hosting; show that the design is an improvement, not just a build.'),
         ('NEW TODAY', 'This review', 'Atlas ledger, keyed chain, extended sweep, emailed one-time code, public link and QR, and 47 executable test scenarios with benchmarks.')]
for i, (tg, head, body) in enumerate(cards):
    x = 0.5 + i * 3.09
    card(s, x, 1.2, 2.83, 2.5)
    chip(s, x + 0.2, 1.34, tg)
    tb(s, x + 0.2, 1.72, 2.45, 0.28, head, size=15, color=NAVY, bold=True)
    tb(s, x + 0.2, 2.08, 2.45, 1.5, body, size=12, color=INK)
card(s, 0.5, 3.88, 9.0, 1.2, fill=LAV)
tb(s, 0.75, 3.96, 1.7, 0.7, '~85%', size=40, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
tb(s, 0.75, 4.64, 1.9, 0.3, 'of the planned scope', size=11, color=MUTED)
tb(s, 2.8, 4.02, 6.5, 1.0, [[('Up from 75% at Review 2. ', {'bold': True, 'color': NAVY}), ('This is our own estimate. Still open by choice: Oracle with PL/SQL and roles, the POSITION entity, and a true cloud platform.', {})],
                              [('', {})],
                              [('Today: ', {'bold': True, 'color': NAVY}), ('recap, new features, evidence, comparison, limits, publication plan.', {})]], size=12, color=INK, after=2)
notes(s, 'A quick map of where we are. Review 1 was the design; Review 2 was the working system at about seventy-five percent. At the end of Review 2 we received three pieces of feedback: add a second factor to confirm that the person voting is the person whose credentials are used, '
         'finish the MongoDB and hosting items, and show that the design is genuinely better rather than just built. Today answers all three. We now estimate about eighty-five percent completion, which is our own estimate; '
         'what remains open is deliberate: Oracle with PL/SQL and roles, the POSITION entity and a true cloud platform.')

# ================================================================== 2b picking up from Review 2
s = slide('PICKING UP FROM REVIEW 2', 'Review 2 left a short list; two new features lead it')
card(s, 0.5, 1.2, 3.4, 3.8)
chip(s, 0.7, 1.34, 'REVIEW 2 ENDED WITH')
bullets(s, 0.7, 1.75, 3.0, 3.2, ['About 75% of the scope built and demonstrated.', 'Open: MongoDB Atlas, hosting, injected-ballot detection.', 'Faculty feedback: confirm the voter with a second factor.', 'Deferred on purpose: Oracle with PL/SQL, POSITION entity.'], size=11)
card(s, 4.1, 1.2, 2.6, 3.8, fill=LAV)
chip(s, 4.3, 1.34, 'NEW: EMAIL OTP')
tb(s, 4.3, 1.75, 2.2, 3.2, [[('A correct password is no longer enough.', {'bold': True, 'color': NAVY})], [('A 6-digit code is emailed to the voter, valid 5 minutes, one use, 3 guesses.', {})], [('', {})], [('Answers the Review 2 comment.', {'italic': True, 'color': MUTED})]], size=11, color=INK, after=4)
card(s, 6.9, 1.2, 2.6, 3.8, fill=LAV)
chip(s, 7.1, 1.34, 'NEW: QR VOTING')
tb(s, 7.1, 1.75, 2.2, 3.2, [[('Scan, sign in, vote.', {'bold': True, 'color': NAVY})], [('The vote page shows a QR code for the public link, so any phone opens the ballot in seconds.', {})], [('', {})], [('Works with the emailed code on the same phone.', {'italic': True, 'color': MUTED})]], size=11, color=INK, after=4)
notes(s, 'We pick up exactly where Review 2 ended. At Review 2 we were at about seventy-five percent, with MongoDB Atlas, hosting and injected-ballot detection still open, and the faculty comment that we should confirm the person voting is the person whose credentials are used. '
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

# ================================================================== 4 what changed
s = slide('WHAT CHANGED SINCE REVIEW 2', 'Six changes, each tied to a weakness we could measure')
items = [('Ledger in MongoDB Atlas', 'Unique block index, file fallback, migration script, health endpoint'),
         ('Keyed hash chain', 'Blocks sealed with HMAC-SHA-256 under an external key'),
         ('Sealed candidate roster', 'Each block carries a hash of the candidate list'),
         ('Extended integrity sweep', 'Injected ballots, roster change, flag/ballot/receipt mismatch'),
         ('Email one-time code', 'Standalone module, own database, hashed single-use codes'),
         ('Public link + QR + tests', 'Tunnel hosting, scan-to-vote, 47 executable scenarios')]
for i, (h, d) in enumerate(items):
    x, y = 0.5 + (i % 3) * 3.09, 1.25 + (i // 3) * 1.85
    card(s, x, y, 2.83, 1.65)
    chip(s, x + 0.2, y + 0.14, f'{i + 1}', w=0.34)
    tb(s, x + 0.2, y + 0.52, 2.45, 0.35, h, size=13, color=NAVY, bold=True)
    tb(s, x + 0.2, y + 0.92, 2.45, 0.7, d, size=11, color=INK)
tb(s, 0.5, 5.0, 9.0, 0.3, 'Everything else from Review 2 (schema, trigger, tally engine, admin console, DB Studio) is unchanged and still passes.', size=10.5, color=MUTED, italic=True)
notes(s, 'Six changes. One, the ledger moved from a local JSON file to MongoDB Atlas. Two, the hash chain is now keyed with HMAC, so rebuilding it needs a secret. Three, each block also seals a hash of the candidate list. '
         'Four, the integrity sweep gained three rules. Five, the emailed one-time code. Six, public hosting with a QR code, and the executable test suite. Everything else from Review 2 is unchanged and still passes its tests.')

# ================================================================== 5 status
s = slide('PROJECT STATUS', 'About 85% done; the open items are the ones we deferred on purpose')
table(s, 0.5, 1.2, 9.0, ['Item', 'Review 2', 'Now'], [
    ['Multi-tenant normalised schema', 'Done', 'Done'], ['Complex queries, views, trigger', 'Done', 'Done'],
    ['Application integration (React + FastAPI)', 'Done', 'Done'], ['Polyglot persistence (document store)', 'Partly', 'Done: MongoDB Atlas'],
    ['Tamper detection', 'Done', 'Done: extended and keyed'], ['Voter second factor', 'Suggested', 'Done: email one-time code'],
    ['Comparative study and evaluation', 'Not started', 'Done: 47 scenarios'], ['Live deployment', 'Not started', 'Partly: public link, not a cloud platform'],
    ['DCL roles and PL/SQL procedures (Oracle)', 'Planned', 'Not started'], ['POSITION entity', 'Deferred', 'Not started'],
], [4.6, 1.6, 3.4], size=10, row_h=0.34)
notes(s, 'Honest status. On the seven core features we score five and a half of seven, about seventy-nine percent, up from sixty-four. Polyglot persistence is complete and deployment has started. '
         'Counting the second factor, the comparative study and the evaluation, we estimate about eighty-five percent overall. The three open items are Oracle with PL/SQL and DCL roles, the POSITION entity, and a true cloud platform. '
         'They were deferred deliberately, and the code is structured so the Oracle move is a migration, not a rewrite.')

# ================================================================== 6 threat model
s = slide('THREAT MODEL', 'Who the attacker is, and who we do not stop')
fit_pic(s, ASSETS / 'diagrams' / 'threat_model.png', 0.5, 1.15, 9.0, 3.7, border=False)
caption(s, 0.5, 4.88, 9.0, 'Detected means found by an auditor running the checks, not blocked in real time.')
notes(s, 'A security claim means nothing without a threat model, so we start there. Seven adversaries, ordered by capability. A voter with a leaked password is stopped by the emailed code. A rogue database administrator and a ledger-store administrator are detected by the sweep and the keyed chain. '
         'An insider with both stores but no secrets is detected, because they cannot recompute the keyed chain. Three are not covered: a network observer, beyond the tunnel\'s encryption; an insider who also holds the key; and roster injection through the admin path. '
         'We say so now rather than have it found later.')

# ================================================================== 7 goals
s = slide('SECURITY GOALS', 'Eight goals, each with a mechanism we can test')
table(s, 0.5, 1.2, 9.0, ['Goal', 'Statement', 'Mechanism'], [
    ['G1', 'No voter can vote twice', 'Trigger, CHECK, unique roster, single-use session, write lock'],
    ['G2', 'Only rostered, verified voters vote', 'Roster lookup, password, emailed code'],
    ['G3', 'Ballots are anonymous in storage', 'No linking column; random ballot tokens'],
    ['G4', 'Malformed ballots are rejected', 'CHECK, composite key, foreign key, API validation'],
    ['G5', 'Edits, deletions, insertions are detectable', 'Per-ballot receipt and integrity sweep'],
    ['G6', 'Ledger cannot be silently rewritten without the key', 'HMAC chain, unique index, separate store'],
    ['G7', 'Candidate attribution is fixed after voting', 'Roster hash sealed in every block'],
    ['G8', 'A voter can confirm their ballot is counted', 'Receipt token and public receipt check'],
], [0.7, 4.2, 5.1], size=10.5, row_h=0.43)
notes(s, 'Eight goals, each with the mechanism that serves it and, later, the test that checks it. One vote per voter; only verified, rostered voters; anonymity in storage; malformed ballots rejected; detectability of edits, deletions and insertions; '
         'a ledger that cannot be silently rewritten without the key; candidate names fixed after voting; and a receipt that lets a voter confirm their ballot is recorded and counted.')

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

# ================================================================== 10 casting
s = slide('CASTING A BALLOT', 'One serialised, transactional path touches every structure')
fit_pic(s, ASSETS / 'diagrams' / 'cast_transaction.png', 0.5, 1.1, 3.9, 4.2, border=False)
bullets(s, 4.7, 1.3, 4.8, 3.8, [('Serialised:', 'a write lock plus the voted flag, checked inside the transaction.'), ('Atomic:', 'flag and ballot rows commit together or not at all.'),
                                 ('Anonymous:', 'the ballot is stored under a random token.'), ('Sealed:', 'then a block with the ranks hash and roster hash joins the ledger.'),
                                 ('Fails visibly:', 'if the ledger is down after commit, the sweep reports a ballot with no receipt.')], size=12)
notes(s, 'Casting a ballot is the one path that touches everything, so it is serialised. After authentication the server takes a write lock, checks the election is open, validates the ranking and confirms the voter has not voted. '
         'In one transaction it sets the voted flag and inserts the ranked rows under a random token. Then it appends a sealed block to the ledger and invalidates the session. '
         'The ledger append happens after the commit; if the ledger were unreachable at that instant, the ballot would exist without a receipt, and the sweep reports exactly that. We chose the variant that fails visibly.')

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

# ================================================================== 15 OTP design
s = slide('EMAIL ONE-TIME CODE · DESIGN', 'Small choices that make it hold up')
table(s, 0.5, 1.2, 5.6, ['Choice', 'Value'], [
    ['Code', '6 digits from a secure generator'], ['Stored as', 'HMAC of challenge and code'], ['Valid for', '5 minutes, single use'],
    ['Guesses', '3 per code, then locked'], ['Resend', '1 per 30 s, 5 per challenge'], ['Challenges', '5 per voter per 15 min'],
    ['Delivery', 'SMTP; failure never blocks sign-in'], ['Where emails live', 'Separate database'],
], [1.7, 3.9], size=10, row_h=0.4)
fit_pic(s, crop_center('voter_otp.png'), 6.35, 1.2, 3.15, 3.3)
tb(s, 6.35, 4.55, 3.15, 0.5, 'The voter sees only a masked address.', size=10, color=MUTED, italic=True, align=PP_ALIGN.CENTER)
notes(s, 'The choices that make it hold up. Codes come from a cryptographically secure generator, so they are unpredictable. Only an HMAC of the code is stored, so the database never holds a usable code. A code lasts five minutes, works once, and allows three guesses. '
         'Resends are limited, and so are new challenges per voter, so a resend cannot be used to keep guessing. Emails live in their own database. A test found a real bug here, which we will show in the evaluation.')

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

# ================================================================== 26 comparison
s = slide('COMPARISON WITH EXISTING SYSTEMS', 'Different design points, different guarantees')
table(s, 0.5, 1.2, 9.0, ['System', 'Main assurance', 'Voter verifies', 'Burden'], [
    ['Helios, Belenios', 'Encrypted ballots; publicly verifiable tally', 'Yes (recorded as cast)', 'Moderate'],
    ['Civitas, Prêt à Voter, Scantegrity II', 'Verifiable; some coercion-resistant', 'Yes', 'High'],
    ['Estonian i-voting', 'National cryptographic system; analysed weaknesses', 'Partial', 'High'],
    ['Commercial mobile or web voting', 'Vendor trust; analyses found vulnerabilities', 'No', 'Low'],
    ['PolyVote', 'Database rules; keyed audit ledger; reconciling sweep', 'Recorded and counted, not content', 'Low'],
], [2.6, 3.4, 1.9, 1.1], size=10, row_h=0.52)
tb(s, 0.5, 4.5, 9.0, 0.7, 'Based on the published designs; we did not run these systems. PolyVote is not a substitute where a hostile administrator is the main concern; it targets elections where cryptographic voting is impractical.', size=11, color=MUTED, italic=True)
notes(s, 'How we compare. These systems optimise cryptographic assurance: Helios and Belenios give a publicly verifiable tally with encrypted ballots; Civitas and the paper-based systems add coercion resistance or voter verification; Estonia is a national system whose analysis found real weaknesses; '
         'and commercial mobile voting products have had serious vulnerabilities reported. We sit at the low-burden end: database rules, a keyed ledger and a reconciling sweep. We did not run these systems; the comparison is from their published designs. '
         'We are not a substitute where a hostile administrator is the main concern. We target the many elections where cryptographic voting is impractical.')

# ================================================================== comparative study
s = slide('COMPARATIVE STUDY · SCOPE', 'We compared PolyVote with five kinds of similar systems')
kinds = [('Cryptographic', 'Helios, Belenios, Civitas', 'Encrypted, publicly verifiable tallies'), ('Commercial SaaS', 'ElectionBuddy, OpaVote, Simply Voting', 'Hosted elections, vendor trust'),
         ('General forms', 'Google Forms, Microsoft Forms', 'Quick polls, owner can edit results'), ('Typical student apps', 'CRUD voting projects', 'One table, one password, no audit'),
         ('National systems', 'Estonian i-voting', 'ID-card based, large infrastructure')]
for i, (h, ex, d) in enumerate(kinds):
    x, y = 0.5 + (i % 3) * 3.09, 1.2 + (i // 3) * 1.75
    card(s, x, y, 2.83, 1.55)
    tb(s, x + 0.2, y + 0.12, 2.45, 0.3, h, size=13, color=NAVY, bold=True)
    tb(s, x + 0.2, y + 0.5, 2.45, 0.45, ex, size=10.5, color=INK, bold=True)
    tb(s, x + 0.2, y + 0.95, 2.45, 0.55, d, size=10, color=MUTED)
card(s, 6.68, 2.95, 2.83, 1.55, fill=LAV)
tb(s, 6.88, 3.05, 2.45, 1.4, [[('How', {'bold': True, 'color': NAVY})], [('Published designs and vendor pages, ten properties, and our own executable tests for PolyVote. We did not run the other systems.', {'size': 10})]], size=11, color=INK, after=3)
tb(s, 0.5, 4.75, 9.0, 0.5, 'The question is not "who has the strongest cryptography" but "which system makes a small election both easy to run and hard to tamper with undetected".', size=11, color=NAVY, bold=True)
notes(s, 'The comparative study. We grouped similar systems into five kinds: the cryptographic research systems like Helios and Belenios; commercial hosted services such as ElectionBuddy, OpaVote and Simply Voting; general form tools such as Google Forms; the typical student voting project, which is a single table with one password; and national systems such as Estonia. '
         'We compared them on ten properties using their published designs and vendor pages, and for PolyVote using our own executable tests. We did not run the other systems ourselves. The question we ask is not who has the strongest cryptography, because the research systems win that, but which system makes a small election both easy to run and hard to tamper with undetected.')

s = slide('COMPARATIVE STUDY · FEATURES', 'Where PolyVote stands on ten properties')
Y, N_, P = 'Yes', 'No', 'Partly'
table(s, 0.4, 1.1, 9.2, ['Property', 'Student app', 'Forms tools', 'Commercial SaaS', 'Helios / Belenios', 'PolyVote'], [
    ['Ranked-choice (instant-runoff) built in', N_, N_, 'Advertised', 'Varies', Y],
    ['Many organisations on one install', N_, N_, Y, P, Y],
    ['One-vote rule enforced inside the database', 'Rare', N_, 'Not documented', 'n/a (crypto)', Y],
    ['Voter and ballot stored with no linking column', 'Rare', N_, 'Not documented', Y, Y],
    ['Tamper detection with published test evidence', N_, N_, 'Vendor logs', Y, 'Yes (47 tests)'],
    ['Second factor at sign-in', 'Rare', 'Account login', 'Often email links', 'Credential email', 'Emailed OTP'],
    ['Scan-to-vote on a phone', N_, N_, 'Varies', N_, Y],
    ['Voter verifies own ballot content', N_, N_, 'Varies', Y, 'Recorded, counted'],
    ['Open source, one-command run', 'Often', N_, N_, Y, Y],
    ['Cost to run a small election', 'Free', 'Free', 'Paid per voter', 'Free, ops-heavy', 'Free'],
], [3.1, 1.1, 1.2, 1.5, 1.4, 1.3], size=8.5, row_h=0.32, header_size=9, head_h=0.34)
tb(s, 0.4, 4.85, 9.2, 0.45, 'Entries for other systems come from their published designs and vendor pages, not our testing; "Varies" and "Not documented" mean we could not confirm. PolyVote\'s column is backed by the tests in this deck.', size=8.5, color=MUTED, italic=True)
notes(s, 'Here is the feature comparison. Read it row by row. PolyVote has ranked-choice counting built in, serves many organisations from one install, enforces the one-vote rule inside the database engine, stores voters and ballots with no linking column, '
         'and is the only entry with published test evidence for tamper detection: forty-seven scenarios. It adds a second factor with an emailed code, and scan-to-vote on a phone. '
         'The honest rows are the cryptographic systems: they let a voter verify their ballot, which we do not; we show only that a ballot is recorded and counted. For the other systems the entries come from their published designs and vendor pages, and where we could not confirm something we wrote varies or not documented rather than guess.')

s = slide('COMPARATIVE STUDY · WHAT IS UNIQUE', 'Five things we found together nowhere else')
uniq = [('1', 'Integrity inside the database', 'Trigger, CHECK, unique and foreign keys refuse bad votes before any application code runs.'),
        ('2', 'Keyed ledger in a separate store', 'HMAC chain in MongoDB Atlas with a sealed candidate roster: rebuilding it needs a key.'),
        ('3', 'Three separate stores', 'Ballots, voter emails and the ledger never share a database or a join.'),
        ('4', 'OTP plus QR on any phone', 'Emailed code with strict limits, and a QR code that opens the ballot.'),
        ('5', 'Evidence, not claims', 'An executable suite attacks the old and the final design; automatic detection rose from 6 to 12 of 13.')]
for i, (n, h, d) in enumerate(uniq):
    y = 1.2 + i * 0.76
    card(s, 0.5, y, 9.0, 0.68, radius=0.12)
    chip(s, 0.68, y + 0.2, n, w=0.34)
    tb(s, 1.2, y + 0.08, 2.8, 0.5, h, size=12, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, 4.1, y + 0.08, 5.2, 0.52, d, size=10.5, color=INK, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'What is unique. We are careful with this word: it means we did not find these five things together in one small-election system, not that no one has done any of them. '
         'One, integrity inside the database: the engine itself refuses a second vote, a bad rank, or a ballot for a missing candidate. Two, the keyed ledger in a separate MongoDB store with a sealed candidate roster, so rebuilding the chain needs a secret key. '
         'Three, three separate stores for ballots, voter emails and the ledger, so no join can link an email to a ballot. Four, an emailed one-time code plus a QR code that opens the ballot on any phone. '
         'Five, evidence: an executable suite attacks both the old and the final design, and automatic detection rose from six to twelve of thirteen scenarios.')

s = slide('COMPARATIVE STUDY · VERDICT', 'Best for small elections, not a Helios replacement')
card(s, 0.5, 1.2, 4.4, 3.2)
chip(s, 0.7, 1.34, 'PolyVote IS THE BETTER FIT WHEN')
bullets(s, 0.7, 1.75, 4.0, 2.6, ['A club, council or class needs ranked-choice results.', 'Someone must be able to run it in an afternoon, free.', 'You need proof that edits and deletions are caught.', 'Voters should confirm themselves by email and vote from a phone.'], size=11)
card(s, 5.1, 1.2, 4.4, 3.2)
chip(s, 5.3, 1.34, 'CHOOSE HELIOS / BELENIOS WHEN')
bullets(s, 5.3, 1.75, 4.0, 2.6, ['The administrator itself cannot be trusted.', 'Voters must verify their own ballot content.', 'Coercion or vote selling is a real threat.', 'A public cryptographic audit is required.'], size=11)
card(s, 0.5, 4.55, 9.0, 0.55, fill=LAV)
tb(s, 0.7, 4.6, 8.6, 0.45, 'Our claim: for the elections it targets, PolyVote is simpler to run, enforces more inside the database, and is the only one here with tested evidence.', size=11, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'The verdict. For the problem we target, small and medium elections such as clubs, councils and classes, PolyVote is the better fit: it gives ranked-choice results, runs in an afternoon for free, proves that edits and deletions are caught, and confirms voters by email on any phone. '
         'The cryptographic systems are the better choice when the administrator cannot be trusted, when voters must verify their own ballot content, when coercion is a threat, or when a public cryptographic audit is required. We say this openly because it makes the claim credible. '
         'Our claim is that for the elections we target, PolyVote is simpler to run, enforces more inside the database, and is the only system in this comparison with tested evidence.')

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

# ================================================================== 29-30 conferences (from research)
# Curated from docs/review3/conferences_open.md (re-checked on each venue's official page on 2026-10-23; recheck before paying)
s = slide('OPEN FOR SUBMISSION TODAY · BY FEE', 'Venues still accepting papers, cheapest first')
table(s, 0.4, 1.1, 9.2, ['#', 'Venue', 'Submit by', 'Student fee', 'Where', 'IEEE/Springer indexing', 'Fit'], [
    ['1', 'Confluence 2027', '4 Dec 2026', 'INR 8,000 + GST', 'Noida, India', 'Submitted for IEEE Xplore', 'Good'],
    ['2', 'INDIACom-2027', '7 Dec 2026', 'INR 8,000 + GST', 'New Delhi, India', 'IEEE approval pending', 'Good'],
    ['3', 'IEM-ICDC 2027', '10 Dec 2026', 'INR 8,000', 'Kolkata, India', 'Springer awaited; 10+ pages', 'Stretch'],
    ['4', 'ICRCICN 2027', '30 Nov 2026', 'INR 8,500', 'Kalyani, India (hybrid)', 'IEEE record 73691; conditional', 'Stretch'],
    ['5', 'ICESICSC-2027', '30 Oct 2026', 'INR 9,000', 'Bhubaneswar, India', 'Says published by IEEE', 'Good'],
    ['6', 'i-PACT 2027 (VIT)', '31 May 2027', 'INR 12,000', 'Vellore, India', 'Recommended to IEEE', 'Stretch'],
    ['7', 'ISDFS 2027', '31 Jan 2027', 'USD 500 (~INR 47,000)', 'San Jose, USA (online ok)', 'Submitted for IEEE Xplore', 'Stretch'],
    ['8', 'ICISSP 2027', '29 Oct 2026', 'EUR 640 (~INR 68,000)', 'Valletta, Malta', 'Submitted for evaluation', 'Good'],
    ['9', 'DATA 2027', '16 Feb / 25 Mar', 'EUR 640 (~INR 68,000)', 'Rome, Italy', 'Not confirmed', 'Good'],
    ['10', 'ICEIS 2027', '17 Nov / 21 Dec', 'EUR 680 (~INR 72,000)', 'Rome, Italy', 'Submitted for evaluation', 'Good'],
], [0.3, 1.7, 1.2, 1.7, 1.8, 2.0, 0.6], size=8.5, row_h=0.33, header_size=9, head_h=0.34)
tb(s, 0.4, 4.85, 9.2, 0.45, 'Fees are per accepted paper and excluding travel, GST and bank charges; INR is approximate at 22 Oct 2026 rates. No venue has yet confirmed indexing; "submitted for" is a plan, not a result.', size=9, color=MUTED, italic=True)
notes(s, 'These are the venues we found that are still accepting papers today, sorted by the student author fee. The cheapest are Indian conferences at about eight to nine thousand rupees: Confluence at Amity Noida, closing the fourth of December; INDIACom in New Delhi, closing the seventh of December, with a six page limit; IEM-ICDC in Kolkata; ICRCICN at Kalyani; and ICESICSC at KIIT Bhubaneswar, which closes on the thirtieth of October. '
         'i-PACT is at VIT Vellore in September 2027 for twelve thousand rupees. The international ones cost fifty to seventy-five thousand rupees before travel. The important caveat is the last column: none of these venues has confirmed indexing yet. Every one says submitted for, proposed, or approval awaited, so they are plans, not results, and indexing should be checked on the publisher\'s site before paying. '
         'Fees are normally paid after acceptance, and are approximate in rupees.')

s = slide('OPEN FOR SUBMISSION TODAY · BY LOCATION', 'India first, then online-capable, then abroad')
cols3 = [('INDIA', [('Noida:', 'Confluence, 4 Dec'), ('New Delhi:', 'INDIACom, 7 Dec; ICICC, 30 Oct'), ('Kolkata and Kalyani:', 'IEM-ICDC, 10 Dec; ICRCICN, 30 Nov'),
                    ('Bhubaneswar:', 'ICESICSC, 30 Oct (7 days left)'), ('Vellore:', 'i-PACT, 31 May 2027'), ('Also:', 'Asansol, Chennai, Goa, Salem (fees not verified)')]),
         ('ONLINE-CAPABLE', [('ISDFS 2027:', 'San Jose, online allowed'), ('ICDAM-2027:', 'London, online fee GBP 150'), ('ICRCICN, ICESICSC:', 'hybrid in India'),
                             ('ICDF2C 2027:', 'New York, hybrid'), ('Note:', 'no open venue is online-only; online still pays the full fee')]),
         ('ABROAD', [('Malta:', 'ICISSP, Valletta'), ('Italy:', 'ICEIS and DATA, Rome'), ('Spain:', 'ICEDEG (e-democracy), Tarragona'), ('Sweden:', 'IFIP SEC, Linkoping'),
                     ('UK, USA, Japan:', 'ACNS, ISDFS, CSP'), ('Not included:', 'travel and visa costs')])]
for i, (head, its) in enumerate(cols3):
    x = 0.5 + i * 3.09
    card(s, x, 1.2, 2.83, 3.85)
    chip(s, x + 0.2, 1.34, head, w=1.7 if len(head) > 8 else None)
    bullets(s, x + 0.2, 1.75, 2.5, 3.2, [(a_, b_) for a_, b_ in its], size=10, after=4)
notes(s, 'The same list grouped by where the conference is held. Most of the cheap options are in India, so travel is domestic: Noida, New Delhi, Kolkata and Kalyani, Bhubaneswar, and i-PACT on our own campus in Vellore. '
         'No open venue is online-only, but ISDFS in San Jose, ICDAM in London, and two of the Indian ones offer an online or hybrid option; online presentation usually still costs the full registration fee. '
         'Abroad, the strongest topical fits are ICISSP in Malta, ICEIS and DATA in Rome, and ICEDEG on e-democracy in Spain. Travel and visa costs are not in any of the fees we quote.')

s = slide('RECOMMENDED SUBMISSION ORDER', 'One venue at a time: dual submission is not allowed')
table(s, 0.5, 1.2, 9.0, ['Step', 'Venue', 'Submit by', 'Decision', 'Why this order'], [
    ['1', 'ICISSP 2027 (Malta)', '29 Oct 2026', '4 Dec 2026', 'Best topical fit open now; EUR 640 plus travel'],
    ['2a', 'INDIACom-2027 (Delhi)', '7 Dec 2026', '8 Feb 2027', 'Cheap India fallback if step 1 fails; IEEE not confirmed'],
    ['2b', 'Confluence 2027 (Noida)', '4 Dec 2026', '25 Dec 2026', 'Alternative to 2a if you want a fast answer'],
    ['3', 'ICEIS, IFIP SEC or ICDF2C', '15-21 Dec 2026', 'mid-Feb 2027', 'Better-quality fallbacks; higher fees and travel'],
    ['4', 'ISDFS 2027 (online ok)', '31 Jan 2027', '15 Feb 2027', 'IEEE-submitted, USD 500, can present online'],
    ['5', 'ICEDEG or DATA/SECRYPT', 'Feb-Mar 2027', 'Apr-May 2027', 'Best audience; the highest cost'],
], [0.6, 2.3, 1.4, 1.3, 3.4], size=9.5, row_h=0.46)
tb(s, 0.5, 4.5, 9.0, 0.75, [[('Before submitting: ', {'bold': True, 'color': NAVY}), ('check the publisher\'s page, remove author names where double-blind, follow each venue\'s AI-disclosure rule, and recheck the deadline. Journals cost USD 2,000 to 3,000 in fees: only as a later extended version.', {})]], size=10.5)
notes(s, 'The recommended order, remembering that we cannot submit to two venues at the same time. ICISSP closes on the twenty-ninth of October, so it is first if we can adapt the paper to their template in time; the decision arrives on the fourth of December. '
         'If that fails, INDIACom or Confluence are the cheap Indian options; pick one, not both. Confluence gives the fastest answer, by the twenty-fifth of December, but the deadline is the same day as the ICISSP decision. '
         'Then ICEIS, IFIP SEC or ICDF2C as better-quality fallbacks, ISDFS in January with online presentation, and ICEDEG or DATA in the spring. Before submitting: verify the publisher on its own page, remove author names for double-blind venues, follow each venue\'s AI-disclosure policy, and recheck the deadline, because dates move.')

s = slide('ROOMMATE LIST: REALITY CHECK', 'The venues are real; "easy" is not supported')
card(s, 0.5, 1.2, 4.4, 3.8)
chip(s, 0.7, 1.34, 'HOLDS UP')
bullets(s, 0.7, 1.75, 4.0, 3.2, [('ICRTAC:', 'real, VIT Chennai SCOPE, 9th edition 10-11 Dec 2026, but closed: the page shows no late route.'), ('ICSCAN:', 'real; the 7th edition ran in June 2026.'),
                                  ('i-PACT:', 'real, at VIT Vellore in Sep 2027, but it is a power-engineering conference.'), ('E-Vote-ID:', 'real and the best topical fit.'),
                                  ('DASFAA / ICDE demo tracks:', 'exist, but are competitive.')], size=10.5)
card(s, 5.1, 1.2, 4.4, 3.8)
chip(s, 5.3, 1.34, 'COULD NOT BE SUPPORTED')
bullets(s, 5.3, 1.75, 4.0, 3.2, [('"75% acceptance":', 'no venue publishes it; ICRTAC 2024 took 36 of 315 papers, about 11%.'), ('"Springer" for ICRTAC:', 'only the 2024 edition; 2026 says IEEE Xplore, subject to review.'),
                                  ('ICSCAN / ICCCNT "IEEE":', 'not confirmed on the official sites.'), ('ViTECoN:', 'no current call found.'),
                                  ('"Fast to accept":', 'very short reviews are a warning sign, not a feature.')], size=10.5)
notes(s, 'We also checked the list your roommates found. The venues are real. ICRTAC is run by VIT Chennai SCOPE and its ninth edition is on the tenth and eleventh of December, but its paper deadline passed in August. ICSCAN held its seventh edition in June. i-PACT is real but is a power-engineering conference. E-Vote-ID is real and the best topical match. '
         'What we could not support is the claim that these are easy or have seventy-five percent acceptance: no venue publishes such a figure, and the numbers we found point the other way, for example ICRTAC 2024 accepted thirty-six of three hundred and fifteen papers, about eleven percent. '
         'Also, ICRTAC 2026 says IEEE Xplore, not Springer, and IEEE sponsorship for ICSCAN and ICCCNT is not confirmed on their official sites. A very fast acceptance is a warning sign, so we recommend choosing on fit and verified indexing.')

s = slide('PUBLICATION PLAN', 'What we claim, how we choose, and what to submit first')
card(s, 0.5, 1.2, 4.4, 3.7)
chip(s, 0.7, 1.34, 'OUR CLAIM')
bullets(s, 0.7, 1.75, 4.0, 3.1, [('Yes:', 'a database-centric design that raises the cost of undetected tampering, with executable evidence and a stated threat model.'),
                                  ('No:', 'parity with end-to-end verifiable voting systems.'),
                                  ('Paper:', 'a 5-page IEEE-style paper and a 37-page report are ready.'), ('Next:', 'tighten for the chosen venue\'s template and page limit.')], size=11)
card(s, 5.1, 1.2, 4.4, 3.7)
chip(s, 5.3, 1.34, 'CHOOSING A VENUE')
bullets(s, 5.3, 1.75, 4.0, 3.1, ['Check indexing on the publisher or Scopus page, not the conference page.', 'Be wary of very short reviews, vague organisers, and fees without a proceedings publisher.',
                                  'Start with a good-fit venue, keep a backup, and treat stretch venues as upside.', 'Follow each venue\'s policy on disclosing AI assistance in writing or coding.'], size=11)
notes(s, 'The plan. Our claim is specific: a database-centric design that raises the cost of undetected tampering, supported by executable evidence and a stated threat model. We do not claim parity with end-to-end verifiable systems. '
         'A short IEEE-style paper and the long report are ready. For choosing a venue, check indexing on the publisher or Scopus rather than on the conference page, be wary of very short review cycles and fees without a named proceedings publisher, '
         'and start with a good-fit venue with a backup. Finally, follow each venue\'s policy on disclosing AI assistance in writing or coding.')

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
    [('github.com/Tharakeshtj/polyvote-election-platform', {'size': 11})], [('', {})],
    [('Run it: ', {'bold': True, 'color': NAVY}), ('python -m uvicorn server:app --port 8000', {'font': 'Consolas', 'size': 10})],
    [('Demo copy: ', {'bold': True, 'color': NAVY}), ('Sample PolyVote, with email verification on', {})],
    [('Reports: ', {'bold': True, 'color': NAVY}), ('Review 3 report (37 pages) and IEEE-style paper', {})]], size=12, color=INK, after=3)
notes(thanks_slide, 'Thank you. To summarise: PolyVote now enforces election rules in the database, seals every ballot in a keyed ledger on MongoDB Atlas, confirms voters with an emailed one-time code, runs publicly, and is evaluated by an executable suite that shows '
                    'automatic detection of tampering rising from six to twelve of thirteen scenarios, with the remaining gaps stated openly. The code, the long report and the short paper are available, and we are happy to take questions or run any part of the demonstration again.')
el = prs.slides._sldIdLst[1]
prs.slides._sldIdLst.remove(el)
prs.slides._sldIdLst.append(el)

prs.save(str(OUT))
print('wrote', OUT, '| slides', len(prs.slides))
