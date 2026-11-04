# Extended-evaluation slides for the updated deck. Executed inside build_deck.py (shares its helpers and globals).
EVF = ROOT / 'docs' / 'evaluation'
X = json.loads((RES / 'full' / 'evaluation.json').read_text(encoding='utf-8'))
XP = {p['id']: p for p in X['profiles_all']}
XI = {p['id']: p for p in X['profiles_in_scope']}
XPERF = {r['ballots']: r for r in X['perf_keyed']}
XPW = X['password']
XFP, XTC = X['false_positives'], X['tally_check']

# ================================================================== extended evaluation: headline
s = slide('EXTENDED EVALUATION', 'Thirty-one attacks, and every in-scope one is detected')
for i, (big, lab) in enumerate([(f'{XI["P7"]["detected"]}/{XI["P7"]["of"]}', 'in-scope attacks detected by the final design'), (f'{XFP["false_alarms"]}/{XFP["sweeps"]}', 'false alarms on clean elections'),
                                (f'{XTC["agree"]}/{XTC["elections"]}', 'tallies match an independent count'), (f'{XPW["slowdown_factor"]:,.0f}x', 'slower password guessing than before')]):
    x = 0.5 + i * 2.27
    card(s, x, 1.2, 2.1, 1.45, fill=LAV)
    tb(s, x + 0.1, 1.28, 1.9, 0.6, big, size=22 if len(big) > 8 else 26, color=NAVY, bold=True)
    tb(s, x + 0.1, 1.95, 1.9, 0.65, lab, size=10, color=INK)
bullets(s, 0.5, 2.9, 9.0, 2.3, [('Changed in the system:', 'a keyed voter-roster seal (sweep rule 6) closes the ghost-voter gap C13, and passwords are now salted PBKDF2.'),
                                ('Changed in the evaluation:', '31 attacks, each run with and without the key; the detector that fires is recorded, so ablations and design comparisons come from one record.'),
                                ('Honest limit:', 'we wrote the attacks; two need the ledger key and one edits unsealed text, so three fall outside the stated attacker model and are reported anyway.')], size=11.5)
notes(s, f'After the first submission we widened the evaluation. The thirteen scenarios became thirty-one, covering ledger replay and reordering, roster attacks, rollbacks and key-holder insiders. Each attack runs once with the keyed chain and once with a plain chain, and we record which detector fires, '
         f'so every ablation and every comparison with another design is read from the same record rather than re-implemented. The final design detects all {XI["P7"]["of"]} scenarios inside the attacker model. Across {XFP["sweeps"]} sweeps of randomised clean elections there were no false alarms, and the tally matched an independent exhaustive count in '
         f'{XTC["agree"]} of {XTC["elections"]} random elections. Two system changes came out of this: a keyed seal over the voter roster, which closes the one gap we reported before, and salted password hashing. We wrote the attacks ourselves, and three are outside the stated model: two need the key and one edits unsealed text.')

# ================================================================== extended evaluation: detection by design
s = slide('DETECTION BY DESIGN', 'No single control is enough; the combination catches all')
fit_pic(s, EVF / 'figures' / 'F02_detection_rate.png', 0.5, 1.15, 5.9, 3.95, border=False)
bullets(s, 6.55, 1.3, 3.0, 3.8, [f'A typical CRUD app with an officer comparing counters: {XI["P0"]["detected"]} of {XI["P0"]["of"]}.', f'Plain chain with a receipt sweep (our Review 2 design): {XI["P3"]["detected"]} of {XI["P3"]["of"]}.',
                                 f'Plain chain with all six rules: {XI["P4"]["detected"]} of {XI["P4"]["of"]}. The key adds the rest.', f'Previous final design without the voter seal: {XI["P6"]["detected"]} of {XI["P6"]["of"]}.', f'Final design: {XI["P7"]["detected"]} of {XI["P7"]["of"]}.'], size=11, after=6)
notes(s, f'Each bar is a design built from the same record. A typical student voting app, where an officer compares the counters, detects {XI["P0"]["detected"]} of the {XI["P0"]["of"]} in-scope attacks. A plain hash chain with the receipt sweep, which is our Review 2 design, detects {XI["P3"]["detected"]}. '
         f'Adding all six sweep rules to a plain chain gets to {XI["P4"]["detected"]}; the remaining four are the attacks that forge or rebuild a chain, which only the key stops. Our design before the voter seal detected {XI["P6"]["detected"]}, and the final design detects all {XI["P7"]["detected"]}. '
         'The designs other than the last are emulated from the record and validated against the real Review 2 code on the first thirteen scenarios, where they agreed on thirteen of thirteen. Other people\'s products were not run.')

# ================================================================== extended evaluation: ablation
s = slide('ABLATION', 'Take any one defence away and something is missed')
fit_pic(s, EVF / 'figures' / 'F03_ablation.png', 0.5, 1.15, 9.0, 2.8, border=False)
bullets(s, 0.5, 4.05, 9.0, 1.2, [('Biggest losses:', 'chain check (7 attacks), voter seal (5), candidate seal (3).'), ('Rules 2 and 3:', 'lose nothing alone because the chain and counters also see those attacks, but they name the tampered ballots.'),
                                 ('Strongest single detector:', 'finds 10 of 31 on its own.')], size=11, after=3)
notes(s, 'Left panel: remove one detector from the final design and count the attacks that are no longer caught. The chain check matters most, with seven, then the voter seal with five and the candidate seal with three. Middle panel: each detector alone; the best finds ten of thirty-one. '
         'Right panel: add detectors one at a time. Removing rule two or rule three loses nothing, because the chain check and the counters also see those attacks, but we keep them because they say which ballots were tampered with. Most attacks are caught by more than one detector, which is the point.')

# ================================================================== extended evaluation: voter-roster seal
s = slide('VOTER-ROSTER SEAL', 'Closing the ghost-voter gap (C13)')
fit_pic(s, EVF / 'screenshots' / 'C13_sweep.png', 0.5, 1.2, 4.4, 1.35)
fit_pic(s, EVF / 'screenshots' / 'C17_sweep.png', 5.1, 1.2, 4.4, 1.35)
caption(s, 0.5, 2.6, 4.4, 'C13: a ghost voter added and used.')
caption(s, 5.1, 2.6, 4.4, 'C17: the seal forged without the key.')
bullets(s, 0.5, 3.0, 9.0, 2.2, [('Gap before:', 'a voter added to the roster by someone with database access could vote; the ballot was valid and nothing recorded the roster.'),
                                ('Fix:', 'the application seals the roster with one keyed tag per voter and a signature over the set, kept in the ledger store; sweep rule 6 recomputes them.'),
                                ('Also caught:', 'deleted or renamed voters, a deleted seal and a forged seal. Blocks record whether an election was sealed, so removing the seal is itself detected.'),
                                ('Limit:', 'an insider with the key can re-seal; older elections show "not sealed" instead of a false alarm.')], size=11, after=4)
notes(s, 'This is the gap we reported as the one undetected scenario. Someone with database access adds a ghost voter and votes as them. The ballot is valid and sealed; what is false is the voter\'s eligibility, and the system had no independent record of the roster. '
         'Now the application writes a keyed seal whenever it registers voters: one tag per voter and a signature over the set, kept in the ledger store with the key outside both stores. Sweep rule six recomputes them. The left screenshot is the ghost voter, the right is a seal forged without the key. '
         'Blocks also record whether the election was sealed, so deleting the seal is itself detected. An insider who holds the key can still re-seal, which is outside the model, and elections that predate the seal show not sealed rather than raising an alarm.')

# ================================================================== extended evaluation: accuracy, passwords, scale
s = slide('ACCURACY, PASSWORDS AND SCALE', 'No false alarms, a correct tally, and costs that stay small')
table(s, 0.5, 1.2, 9.0, ['Measure', 'Result'], [
    ['False alarms on clean elections', f'{XFP["false_alarms"]} in {XFP["sweeps"]} sweeps over {XFP["elections"]} randomised elections'],
    ['Tampered ballots named when 1, 5 or 20 per category are altered', 'Precision 1.0 and recall 1.0 in all nine cases'],
    ['Instant-runoff tally against an independent exhaustive count', f'{XTC["agree"]} of {XTC["elections"]} random elections agree ({XTC["with_tie_paths"]} had a tie path)'],
    ['Offline guessing against a stolen password table', f'about {XPW["slowdown_factor"]:,.0f} times slower; sign-in hashing about {XPW["verify_ms"]:.0f} ms'],
    ['Integrity sweep at 10,000 and 100,000 ballots', f'{XPERF[10000]["sweep_ms"]:.0f} ms and {XPERF[100000]["sweep_ms"] / 1000:.1f} s (keyed file ledger)'],
    ['One to sixteen simultaneous voters', f'no errors; chain and sweep intact after every run; up to {max(r["throughput_per_s"] for r in X["concurrency"]):.0f} casts per second'],
], [4.8, 4.2], size=10.5, row_h=0.5)
tb(s, 0.5, 4.8, 9.0, 0.5, 'Measured on one laptop with synthetic elections; trends matter more than the absolute times.', size=10, color=MUTED, italic=True)
notes(s, f'Four checks on whether the sweep can be trusted. First, false alarms: {XFP["sweeps"]} sweeps on randomised clean elections, none raised an alarm. Second, when we tamper with one, five or twenty ballots of each kind, the sweep names exactly those ballots. '
         f'Third, the tally matches an independent implementation that explores every tie-break in {XTC["agree"]} of {XTC["elections"]} elections. Fourth, passwords: salted PBKDF2 with six hundred thousand rounds makes each guess about {XPW["slowdown_factor"]:,.0f} times slower. '
         f'Scale: the sweep takes {XPERF[10000]["sweep_ms"]:.0f} milliseconds at ten thousand ballots and about {XPERF[100000]["sweep_ms"] / 1000:.0f} seconds at one hundred thousand. Sixteen simultaneous voters produced no errors. All of this is on one laptop with synthetic data.')

# ================================================================== extended evaluation: comparison
s = slide('COMPARISON WITH ALTERNATIVES', 'Against 33 systems, the combination is what differs')
fit_pic(s, EVF / 'figures' / 'F20_feature_coverage.png', 0.5, 1.12, 3.85, 4.1, border=False)
bullets(s, 4.55, 1.25, 5.0, 3.95, [('What we did:', 'read each system\'s own pages for nine features; "not documented" means we did not find it, not that it is absent. Other products were not run.'),
                                   ('What stands out:', 'in the strict form we use, none documents a keyed ledger with a reconciling sweep and published attack results, and none documents all of ranked counting, in-database rules, such a ledger and an emailed second factor.'),
                                   ('Where others are stronger:', 'Helios, Belenios and ElectionGuard let a voter verify the ballot and anyone verify the tally; a hostile administrator with our ledger key beats us and does not beat them. They also have years of public analysis.')], size=10.5, after=6)
notes(s, 'We compared PolyVote with thirty-three related systems using only what each project documents about itself, across nine features. The picture shows twenty-two of them by name. We are careful with the wording: not documented does not mean absent, and we did not run other products. '
         'What stands out is the combination: ranked-choice counting, rules enforced in the database, a keyed ledger with a reconciling sweep and published attack results, and an emailed second factor. We do not claim to be more secure than Helios, Belenios or ElectionGuard. '
         'They let a voter verify the ballot and anyone verify the tally. A hostile administrator who holds our ledger key defeats us, and does not defeat them. Our claim is cost and fit for small elections, with a result anyone can re-run.')
