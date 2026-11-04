"""Turn the copied deck script into the updated edition. Every edit asserts that its target text exists exactly once.

    python docs/review3_updated/apply_deck_updates.py     (run once on a fresh copy)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = HERE / 'build_deck.py'
s = p.read_text(encoding='utf-8')


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


# results come from the re-run of the final design; the baseline is unchanged
rep("tam = S['tamper']\n",
    "tam = S['tamper']\n_pf = {x['id']: x for x in json.loads((RES / 'patched_final.json').read_text(encoding='utf-8'))['tamper']}\nfor _t in tam:\n    _t['patched'], _t['patched_detail'] = _pf[_t['id']]['outcome'], _pf[_t['id']]['detail']\n")
rep("fit_pic(s, RES / 'detection.png', 0.5, 1.2, 9.0, 2.45, border=False)", "fit_pic(s, HERE / 'assets' / 'detection.png', 0.5, 1.2, 9.0, 2.45, border=False)")
rep("('1', 'Still undetected: roster injection (C13)', AMBER)]", "('0', 'Undetected: C13 is now caught by the voter-roster seal', GREEN)]")
rep("none depend on the counters, and one is not detected: adding a ghost voter to the roster and voting as them. We report that one openly. The detection bar shows each scenario, colour-coded.')",
    "none depend on the counters, and none is missed. The first edition of this deck reported one miss, C13, adding a ghost voter to the roster and voting as them; the keyed voter-roster seal closes it, and the next slides show the wider evaluation. The detection bar shows each scenario, colour-coded.')")
rep("Three are not covered: a network observer, beyond the tunnel\\'s encryption; an insider who also holds the key; and roster injection through the admin path. '",
    "Two are not covered: a network observer, beyond the tunnel\\'s encryption, and an insider who also holds the key. Roster injection through the admin path is now detected by the keyed voter-roster seal. '")

# sweep slide: six rules
rep("'Five rules compare the database with the ledger'", "'Six rules compare the database with the ledger'")
rep("    ['5  Count mismatch', 'Flags, ballots, receipts disagree', 'Compare the three counts for the election', 'New'],\n], [1.7, 2.7, 3.7, 0.9], size=10.5, row_h=0.55)",
    "    ['5  Count mismatch', 'Flags, ballots, receipts disagree', 'Compare the three counts for the election', 'New'],\n    ['6  Voter roster changed', 'Voter added, deleted or edited outside the app; seal removed or forged', 'Recompute a keyed tag per voter and a signature over the set', 'Updated'],\n], [1.9, 2.7, 3.5, 0.9], size=10, row_h=0.46)")
rep("tb(s, 0.5, 4.5, 9.0, 0.7, [[('Plus the chain check: '", "tb(s, 0.5, 4.6, 9.0, 0.7, [[('Plus the chain check: '")
rep("Rule five compares voter flags, ballots and receipts. The chain check", "Rule five compares voter flags, ballots and receipts. Rule six, added after the first submission, recomputes a keyed seal over the voter roster so a ghost voter is caught. The chain check")

rep("a five-rule sweep and a published attack suite. {nd(\"patched\")} of 13 attacks caught against {nd(\"baseline\")} of 13 for the plain-chain design, the same in 3 runs; C6 and C10 only fail with the key.",
    "a six-rule sweep and a published attack suite. {nd(\"patched\")} of 13 attacks caught against {nd(\"baseline\")} of 13 for the plain-chain design (baseline identical in 3 runs); C6 and C10 only fail with the key.")
rep("rises from six to twelve of thirteen. Forged receipts", "rises from six to thirteen of thirteen. Forged receipts")
rep("ledger moves to Atlas, and the system becomes publicly reachable. The cost is small: the sweep at ten thousand ballots goes from about one hundred and twenty-nine to about one hundred and forty-seven milliseconds.",
    "ledger moves to Atlas, and the system becomes publicly reachable. The cost is small: the sweep at ten thousand ballots goes from about one hundred and twenty-nine to about one hundred and forty-seven milliseconds in the original measurement; the extended evaluation re-measures it with the voter seal.")
rep("['Candidate renaming', 'Undetected', 'Detected (sealed roster)'],", "['Candidate renaming', 'Undetected', 'Detected (sealed roster)'], ['Ghost voter added to the roster', 'Undetected', 'Detected (voter seal)'],")
rep("['Password', 'Election database', 'SHA-256 hash only'],", "['Password', 'Election database', 'Salted PBKDF2 hash only'],")
rep("('Not for binding votes:', 'no independent review yet; passwords use plain SHA-256.')", "('Not for binding votes:', 'no independent review yet; passwords are salted PBKDF2.')")
rep("no independent security review and plain SHA-256 password hashing, so it is not for binding elections yet.", "no independent security review, so it is not for binding elections yet. Passwords are now salted PBKDF2, upgraded from plain SHA-256 after the first submission.")
rep("    ['Roster injection is not detected (A7)', 'Committed or signed roster, checked at sweep time'],",
    "    ['Roster provenance: the seal catches later changes, not a wrong roster at sealing; a key holder can re-seal (A7)', 'Dual control or an external record when registration closes'],")
rep("    ['Passwords stored as plain SHA-256; default admin login', 'Salted, slow hashing; forced first-login change'],",
    "    ['Default admin login; no lock-out, session expiry or API security headers', 'Forced first-login change; lock-out with back-off; session expiry; response headers'],\n    ['No user study yet', 'Task-based usability test; protocol and analysis script are prepared'],")
rep("], [4.6, 4.4], size=10, row_h=0.46)\nnotes(s, 'What we do not claim.", "], [4.6, 4.4], size=9.5, row_h=0.4)\nnotes(s, 'What we do not claim.")
rep("Roster injection is not detected; we need a committed roster. We are not end-to-end verifiable. '", "The roster seal catches later changes to the voter roster but not a wrong roster at sealing, and a key holder can re-seal. We are not end-to-end verifiable. '")
rep("'Passwords are stored with plain SHA-256, which we know should be a salted slow hash. Email is a weak factor", "'Passwords are now salted PBKDF2; the public demo still uses known passwords on purpose, and there is no lock-out or session expiry. We have not run a user study. Email is a weak factor")
rep("'Keyed chain, five sweep rules'", "'Keyed chain, six sweep rules'")
rep("'47 test scenarios; 33 systems read'", "'47 tests, then 31 attacks and a comparison with 33 systems'")
rep("now keyed and with five rules, the MongoDB Atlas ledger", "now keyed and with six rules, the MongoDB Atlas ledger")
rep("backed by a five-rule integrity sweep. '", "backed by a six-rule integrity sweep. '")
rep("'independently of application logic, backed by a five-rule integrity sweep.')", "'independently of application logic, backed by a six-rule integrity sweep.')")
rep("automatic detection of tampering rising from six to twelve of thirteen scenarios, with the remaining gaps stated openly.", "automatic detection of tampering rising from six to thirteen of thirteen scenarios, and all twenty-eight in-scope attacks in the wider thirty-one scenario evaluation, with the remaining limits stated openly.")
rep("'Executable suite, 3 identical runs'", "'Executable suite; baseline identical in 3 runs, final design re-run'")
rep("'47 test scenarios and a comparison with 33 systems'", "'47 tests, 31 attacks and a comparison with 33 systems'")

# new slides after the tampering-results slide
marker = "# ================================================================== 22 sweep in action"
rep(marker, "exec(compile((HERE / 'deck_ext.py').read_text(encoding='utf-8'), 'deck_ext', 'exec'), globals())\n\n" + marker)
p.write_text(s, encoding='utf-8')
print('deck updates applied')
