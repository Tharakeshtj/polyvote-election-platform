"""Turn the copied Review 3 report scripts into the updated edition. Every edit asserts that its target text exists exactly once.

    python docs/review3_updated/apply_updates.py     (run once on a fresh copy)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def patch(name, pairs):
    p = HERE / name
    s = p.read_text(encoding='utf-8')
    for old, new in pairs:
        assert s.count(old) == 1, (name, s.count(old), old[:70])
        s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')


patch('sec1_3.py', [
    ("a keyed (HMAC) ledger chain, a sealed candidate roster, an extended sweep, ",
     "a keyed (HMAC) ledger chain, a sealed candidate roster, a keyed voter-roster seal, salted PBKDF2 password storage, an extended six-rule sweep, "),
    ("rises from 6 of 13 to 12 of 13; the remaining '\n        'case, roster injection through the administrative path, is documented as a limitation. We compare",
     "rises from 6 of 13 to 13 of 13. A further evaluation (Section 6.11) with 31 storage-level scenarios detects all 28 that lie inside the stated attacker model, with no false alarms on 399 clean sweeps, '\n        'and reports the three that lie outside it. We compare"),
    ("['A7', 'Roster injection via the admin path', 'Adds a ghost voter, votes as them', 'Not covered; needs roster commitment'],",
     "['A7', 'Roster injection via the admin path', 'Adds a ghost voter, votes as them', 'Detected by the keyed voter-roster seal (rule 6), unless the attacker holds the key'],"),
    ("Verifying roster provenance is future work (A7).",
     "The keyed voter-roster seal detects later changes to the roster, but cannot tell whether the roster was right when it was sealed (A7)."),
    ("its passwords are stored with plain SHA-256, which does not follow that guidance (Section 9).",
     "its passwords were stored with plain SHA-256 in the first edition of this report; the updated build stores them with salted PBKDF2, which follows that guidance (Section 4.6)."),
])

patch('sec4_5.py', [
    ("the other three close gaps", "the other four close gaps"),
    ("            ['5. Count mismatch (new)', 'Flags, ballots and receipts disagree', 'Compare voted flags, distinct ballot tokens and blocks for the election'],\n",
     "            ['5. Count mismatch (new)', 'Flags, ballots and receipts disagree', 'Compare voted flags, distinct ballot tokens and blocks for the election'],\n"
     "            ['6. Voter roster changed (new)', 'A voter added, deleted or edited outside the application, or the seal removed or forged', 'Recompute a keyed HMAC tag for each voter and a signature over the set; compare with the seal kept in the ledger store'],\n"),
    ("finds edits inside the ledger, and the sweep finds edits to the database relative to a trusted ledger.')\n",
     "finds edits inside the ledger, and the sweep finds edits to the database relative to a trusted ledger.')\n"
     "    c.p('**Voter-roster seal (added after the first edition).** The first edition could not detect a ghost voter, a voter added to the roster by someone with database access who then votes as them, because the ballot is valid and the system held no independent record of the roster. '\n"
     "        'The application now writes a keyed seal whenever it registers voters: one HMAC tag per voter (registration number and election) and an HMAC signature over the set of tags, stored in the ledger store, with the key outside both stores. '\n"
     "        'Each later block records whether the election was sealed, so deleting the seal is itself detected. Rule 6 recomputes the tags from the database and compares them; a voter added, deleted or renamed outside the application, a deleted seal and a seal forged without the key are all reported. '\n"
     "        'A voter whom the officer genuinely adds after voting opens goes through the application, which re-seals. Elections created before the seal existed show the state \"not sealed\" rather than a false alarm.')\n"
     "    c.p('**Passwords (changed after the first edition).** Passwords are now stored as PBKDF2-HMAC-SHA256 with a random 16-byte salt and 600,000 rounds (`pbkdf2_sha256$rounds$salt$digest`). Older unsalted hashes still verify and are upgraded at the next successful sign-in; verification uses a constant-time comparison. '\n"
     "        'The measured effect is in Section 6.11.')\n"),
])

patch('sec6_7.py', [
    ("The top row is the plain hash-chain baseline (6 green) and the bottom row is PolyVote (12 green). The one red square left is C13, adding a fake voter to the roster, which we explain in Section 9.",
     "The top row is the plain hash-chain baseline (6 green) and the bottom row is PolyVote (13 green). C13, adding a ghost voter to the roster, was the one red square in the first edition of this report; the keyed voter-roster seal now detects it (Section 6.11)."),
    ("and {n_und(\"patched\")} is not detected.", "and {n_und(\"patched\")} are not detected."),
    ("    c.bullet('**C13** (add a ghost voter to the roster and vote as them through the API) remains undetected. The ballot is valid, sealed and counted; what is false is the '\n"
     "             'voter\\'s eligibility, and the system holds no independent record of the roster to compare with. Closing this requires a signed or externally recorded '\n"
     "             'roster, which we list as future work. We report it rather than hide it.')",
     "    c.bullet('**C13** (add a ghost voter to the roster and vote as them through the API) was undetected in the first edition: the ballot is valid, sealed and counted, and the system held no independent record of the roster. '\n"
     "             'The keyed voter-roster seal (rule 6, Section 4.6) now reports it, together with deleted or renamed voters and a deleted or forged seal. An insider who holds the ledger key can still re-seal; that case is outside the threat model (Section 9).')"),
    ("They are not a complete catalogue, and an author tends to test what the design handles.')",
     "They are not a complete catalogue, and an author tends to test what the design handles. Section 6.11 extends the set to 31 scenarios, but we wrote those too.')"),
    ("PolyVote adds the keyed chain and five sweep rules.", "PolyVote adds the keyed chain and six sweep rules."),
    ("'Keyed chain, five-rule sweep, roster seal'", "'Keyed chain, six-rule sweep, voter-roster seal'"),
    ("PolyVote adds the roster seal and the extra rules. The one scenario nobody here catches is C13, a ghost voter added to the roster.",
     "PolyVote adds the candidate seal, the extra rules and the keyed voter-roster seal, which catches ghost voters (C13)."),
    ("'PolyVote finds twice as many tampering attacks automatically as a plain hash chain.'",
     "'PolyVote finds more than twice as many tampering attacks automatically as a plain hash chain.'"),
    ("'Attacks are the ones we designed; one (C13) is still missed.'", "'Attacks are the ones we designed; the 31-scenario set in Section 6.11 is also ours.'"),
    ("    # ------------------------------------------------------------------ 7\n    c.h1('7. Comparative Study')",
     "    sec_ext.build(c, S)\n\n    # ------------------------------------------------------------------ 7\n    c.h1('7. Comparative Study')"),
])
s = (HERE / 'sec6_7.py').read_text(encoding='utf-8')
if 'import sec_ext' not in s:
    s = s.replace('\n\ndef build(c, S):', '\nimport sec_ext  # noqa: E402\n\n\ndef build(c, S):', 1)
    (HERE / 'sec6_7.py').write_text(s, encoding='utf-8')

patch('sec8_10.py', [
    ("['Integrity sweep with five rules'", "['Integrity sweep with six rules'"),
    ("            ['Roster injection (A7, scenario C13)', 'A ghost voter\\'s ballot is valid and sealed', 'Commit the roster at registration close, with a signature or dual control; compare at sweep time'],\n",
     "            ['Roster provenance (A7, scenario C13)', 'The voter-roster seal detects later changes, but cannot show that the roster was right when sealed, and an insider with the key can re-seal', 'Dual control or an external record when registration closes; publish the roster hash to a witness'],\n"),
    ("            ['Passwords stored as plain SHA-256; default administrator password', 'Fast, unsalted hashes are weak against offline guessing [34], [35]; demo voters share a password', 'Use a salted, slow key-derivation function; force a password change on first login'],\n",
     "            ['Default administrator password; demo voters share a password', 'Passwords are now salted PBKDF2 (first edition: plain SHA-256) [34], [35], but the public demo deliberately uses known passwords', 'Force a password change on first login in a real deployment'],\n"
     "            ['No account lock-out, no session expiry, login reveals whether a registration number exists, no security headers on API responses', 'Measured in the November 2026 probes (Section 6.11); the emailed code is a second factor but not a lock-out', 'Add lock-out with back-off, session expiry, uniform login errors and response headers'],\n"),
])

# data.py: use the new tamper results and the extended evaluation; look in assets/ first for regenerated figures
s = (HERE / 'data.py').read_text(encoding='utf-8')
if 'patched_final' not in s:
    s = s.replace("    S['mongo'] = json.loads((RES / 'mongo_bench.json').read_text(encoding='utf-8'))\n",
                  "    S['mongo'] = json.loads((RES / 'mongo_bench.json').read_text(encoding='utf-8'))\n"
                  "    pf = json.loads((RES / 'patched_final.json').read_text(encoding='utf-8'))\n"
                  "    new = {x['id']: x for x in pf['tamper']}\n"
                  "    for t in S['tamper']:\n"
                  "        t['patched'], t['patched_detail'] = new[t['id']]['outcome'], new[t['id']]['detail']\n"
                  "    S['ext'] = json.loads((RES / 'full' / 'evaluation.json').read_text(encoding='utf-8'))\n"
                  "    S['static'] = json.loads((RES / 'full' / 'static.json').read_text(encoding='utf-8'))\n"
                  "    S['pf'] = pf\n", 1)
    s = s.replace("    for sub in ('diagrams', 'screens'):\n        p = ASSETS / sub / name",
                  "    local = Path(__file__).resolve().parent / 'assets' / name\n    if local.exists():\n        return local\n    for sub in ('diagrams', 'screens'):\n        p = ASSETS / sub / name", 1)
    (HERE / 'data.py').write_text(s, encoding='utf-8')
print('updates applied')
