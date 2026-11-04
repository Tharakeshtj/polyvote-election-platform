"""Section 6.11: extended evaluation added in the updated edition. Numbers are read from experiments/results/full/ and docs/evaluation/tables.json."""
import json
from pathlib import Path

import data

fig = data.fig
ROOT = data.ROOT
T = {t['name']: t for t in json.loads((ROOT / 'docs' / 'evaluation' / 'tables.json').read_text(encoding='utf-8'))}


def build(c, S):
    U = json.loads((ROOT / 'docs' / 'review3' / 'uniqueness_evidence.json').read_text(encoding='utf-8'))

    def n_yes(code):
        return sum(1 for x in U if (x[code]['value'] if isinstance(x[code], dict) else eval(x[code])['value']) == 'yes')

    E, ST = S['ext'], S['static']
    PA = {p['id']: p for p in E['profiles_all']}
    PI = {p['id']: p for p in E['profiles_in_scope']}
    sc = E['matrix']['scenarios']
    fp, tc, pw = E['false_positives'], E['tally_check'], E['password']
    perf = {r['ballots']: r for r in E['perf_keyed']}

    c.h2('6.11 Extended evaluation (updated edition, November 2026)')
    c.p('The first edition of this report evaluated 13 tampering scenarios and found one it could not detect (C13, a ghost voter). This updated edition changes the system in two ways and widens the evaluation. '
        '**Changes to the system:** a keyed voter-roster seal and sweep rule 6 close the C13 gap (Section 4.6), and passwords are stored with salted PBKDF2 instead of plain SHA-256. '
        '**Changes to the evaluation:** 31 scenarios instead of 13, each run once under a keyed and once under a plain chain with a record of which detector fires; ablations and comparisons with other designs read from that record; and measurements of accuracy, correctness, passwords, scaling, concurrency, security probes and code quality. '
        'The first edition, as submitted, is unchanged. Everything below is reproducible with `experiments/full_eval/run_all.py`, and a 32-page dossier with 21 figures, 18 tables and 20 screenshots is in `docs/evaluation/`.')

    c.h3('6.11.1 Method')
    c.p('**Attacker model.** The attacker has write access to the election database, the ledger store or both, and does not hold the ledger key. Three scenarios are deliberately outside this model and are reported anyway: two in which the attacker holds the key (C28, C29) and one that edits a candidate\'s platform text, which is not sealed (C23).')
    c.p('**Detector record.** Each scenario runs against a throwaway copy of the application. The record stores which of eight detectors fired: the chain check, sweep rules 1 to 6, and an officer comparing counters by eye. A design profile is a subset of detectors plus a key mode, so the behaviour of other designs is read from the record rather than re-implemented. '
        f'To validate this, the first edition\'s design was emulated from the record and compared with the real first-edition code on C1 to C13: they agreed on {E["emulation_check"]["agree"]} of 13.')
    c.table(['ID', 'Attack', 'In the model', 'Detectors that fire (final design)'],
            [[s['id'], s['title'], 'Yes' if s['in_scope'] else 'No', ', '.join(k.replace('_', ' ') for k, v in s['modes']['keyed']['detectors'].items() if v and k != 'counters') or ('none' if not s['in_scope'] else 'counters only')] for s in sc],
            [0.6, 5.2, 1.0, 3.4], 'The 31 attack scenarios and what detects them in the final design.', 'tab:ext-scen', size=8.5)

    c.h3('6.11.2 Detection by design')
    rows = [[p['id'], p['label'], f'{p["detected"]} of {p["of"]}', f'{PI[p["id"]]["detected"]} of {PI[p["id"]]["of"]}'] for p in E['profiles_all']]
    c.table(['Profile', 'Design', 'All 31', 'In the model (28)'], rows, [0.8, 5.6, 1.2, 1.6], 'Attack scenarios detected by each design profile.', 'tab:ext-profiles', size=9)
    c.p(f'The final design detects all {PI["P7"]["of"]} scenarios inside the attacker model (and {PA["P7"]["detected"]} of 31 overall). The first edition\'s design detects {PA["P6"]["detected"]} of 31, a plain chain with a receipt sweep {PA["P3"]["detected"]}, '
        f'and a conventional application whose officer compares counters {PA["P0"]["detected"]}. With a plain SHA-256 chain, the same six rules would detect {PA["P4"]["detected"]} of 31, so the key is what stops forged and rebuilt chains. '
        f'Append-only database triggers prevent {len(E["triggers"]["prevented"])} of 31 against a writer who cannot drop them, but they do not stop injection, ledger tampering or roster changes, and a writer with schema rights removes them.')
    c.figure(fig('ext_heatmap.png'), 'Which of the 31 attacks each of the eight design profiles detects (green) or misses (red).', 'fig:ext-heat', 5.2)

    c.h3('6.11.3 Ablation')
    c.table(['Detector removed from the final design', 'Still detected', 'Attacks lost'], [list(r) for r in T['T04_ablation']['rows']], [3.6, 1.4, 4.0], 'Leave-one-out ablation (31 scenarios, keyed chain).', 'tab:ext-ablation', size=9)
    c.figure(fig('ext_ablation.png'), 'Ablation of the defences: attacks lost when one detector is removed, attacks each detector finds alone, and cumulative detection.', 'fig:ext-ablation', 6.3)
    c.p('No single detector is enough: the strongest alone finds 10 of 31. Removing rule 2 or rule 3 loses nothing, because the chain check and counters also see those attacks, but the rules are kept because they name the tampered ballots.')

    c.h3('6.11.4 Accuracy and correctness')
    c.p(f'Across {fp["sweeps"]} sweeps over {fp["elections"]} randomised clean elections (bulk registration, late voters, ballots, closing) there were {fp["false_alarms"]} false alarms. '
        'When 1, 5 or 20 ballots in each category were modified, deleted or injected, the sweep named exactly those ballots: precision and recall were 1.0 in all nine cases. '
        f'The instant-runoff tally agreed with an independent implementation that explores every tie-break in {tc["agree"]} of {tc["elections"]} random elections of 3 to 8 candidates and 5 to 300 ballots ({tc["with_tie_paths"]} had a tie path).')

    c.h3('6.11.5 Passwords')
    c.table(['Password class', 'Unsalted SHA-256 (before)', 'Salted PBKDF2 (after)'], [list(r) for r in T['T11_password']['rows']], [3.0, 3.0, 3.0], 'Time to try every password in a class on one CPU thread.', 'tab:ext-pw', size=9)
    c.p(f'Each offline guess is about {pw["slowdown_factor"]:,.0f} times slower, and every hash has its own random salt, so precomputed tables cannot be reused. Verification takes about {pw["verify_ms"]:.0f} ms; the round count is configurable (`PASSWORD_HASH_ITERATIONS`) for slower hosts.')
    c.figure(fig('ext_passwords.png'), 'Offline guessing cost before and after the change.', 'fig:ext-pw', 5.4)

    c.h3('6.11.6 Performance and concurrency')
    c.table(['Ballots', 'Sweep (ms)', 'Sweep without voter seal (ms)', 'Chain check (ms)', 'Tally (ms)', 'Cast p50 (ms)'],
            [[f'{b:,}', f'{perf[b]["sweep_ms"]:,.0f}', f'{perf[b]["sweep_no_seal_ms"]:,.0f}', f'{perf[b]["chain_verify_ms"]:,.0f}', f'{perf[b]["tally_ms"]:,.0f}', f'{perf[b]["cast_p50_ms"]:,.0f}'] for b in sorted(perf)],
            [1.0, 1.2, 1.9, 1.4, 1.1, 1.3], 'Median times with the keyed file ledger, 100 to 100,000 ballots.', 'tab:ext-perf', size=9)
    c.p(f'Audit and tally grow roughly linearly. At 10,000 ballots the sweep takes {perf[10000]["sweep_ms"]:.0f} ms and at 100,000 it takes {perf[100000]["sweep_ms"] / 1000:.1f} s; the voter seal accounts for a minority of that. '
        'The file ledger rewrites the file on every append, so casting slows as the ledger grows; MongoDB Atlas appends stay flat (see the Atlas benchmark earlier in this section). '
        f'With one to 16 simultaneous voters there were no errors, and the chain and sweep were intact after every run (up to {max(r["throughput_per_s"] for r in E["concurrency"]):.0f} casts per second on a laptop). '
        'The timings in this table were taken on a busier machine than the first edition\'s benchmarks, so the two sets of figures should be compared as trends, not exact values.')
    c.figure(fig('ext_scaling.png'), 'Audit time against election size (left) and cost of casting one ballot with the file ledger (right), log scales.', 'fig:ext-scaling', 6.3)

    c.h3('6.11.7 Security probes and privacy')
    c.table(['Probe', 'Result', 'Verdict'], [list(r) for r in T['T14_security']['rows']], [2.4, 4.6, 3.0], 'Probes of the running application.', 'tab:ext-sec', size=8.5)
    c.table(['Privacy check', 'Result'], [list(r) for r in T['T15_privacy']['rows']], [3.0, 6.0], 'Voter privacy checks.', 'tab:ext-priv', size=8.5)
    c.p('The probes found real gaps that we have not fixed and list as limitations: no lock-out on the password step, a login response that distinguishes an unknown registration number from a wrong password, no session expiry, and no security headers on API responses. '
        'An attacker with two database copies and one cast in between links a voter to a ballot with probability one over the number of casts, a known limit of any design that stores a voted flag.')
    c.figure_row([fig('ext_c13.png'), fig('ext_c17.png')], 'Sweep after a ghost voter was added and used (C13, left) and after the roster seal was forged without the key (C17, right).', 'fig:ext-shots', 3.1)

    c.h3('6.11.8 Code and dependencies')
    c.p(f'The repository has about {ST["loc"]["total_lines"]:,} non-blank lines of code and documentation, {ST["structure"]["api_routes"]} API routes and {ST["complexity"]["functions"]} analysed functions with a mean cyclomatic complexity of {ST["complexity"]["mean_complexity"]}. '
        f'The security linter reports {ST["bandit"]["issues"]} findings ({ST["bandit"]["by_severity"].get("MEDIUM", 0)} medium, {ST["bandit"]["by_severity"].get("LOW", 0)} low). '
        f'The front-end dependency audit reports {ST["npm_audit"]["vulnerabilities"]["total"]} known vulnerabilities; the hosted Python requirements report {ST["pip_audit"]["requirements-hosted.txt"]["vulnerabilities"]}. '
        f'The legacy desktop requirements report {ST["pip_audit"]["requirements.txt"]["vulnerabilities"]} advisories, all in an image library used only by the old Streamlit interface, which the hosted service does not install.')

    c.h3('6.11.9 Comparison with related systems')
    c.p('We read the documentation of 33 related systems and recorded nine features (Section 7). Only %d system documents in-database integrity rules and %d document an emailed one-time code; in the strict form used here, none documents a keyed tamper-evident ledger with a reconciling sweep and published attack results, and none documents the combination of ranked-choice counting, in-database rules, such a ledger and an emailed second factor. '
        '"Not documented" means we did not find it, not that it is absent, and the competing products were not run: they are placed in the nearest measured design class from their documentation.' % (n_yes('F3'), n_yes('F6')))
    c.figure(fig('ext_coverage.png'), 'Documented feature coverage of 22 of the systems, and PolyVote.', 'fig:ext-coverage', 5.0)
    c.p('**Where related systems are stronger.** Helios, Belenios and ElectionGuard let a voter check that the recorded ballot is the one cast and let anyone check the tally; PolyVote\'s receipts show only that a ballot is recorded and counted. '
        'A hostile administrator who holds the ledger key defeats PolyVote and does not defeat them. They also have years of use and public analysis. PolyVote\'s claim is cost and fit: free, open source, one command to run and a detection result that anyone can re-run.')

    c.h3('6.11.10 Limits of the extended evaluation')
    c.bullet('The 31 scenarios were written by the authors, so the 28 of 28 result shows coverage of the attacks we thought of, not of all attacks. An independently written attack list is future work.')
    c.bullet('Competing designs are emulated classes from documentation, not products run under test.')
    c.bullet('One early prevention test (A3) was flaky and was fixed; the earlier pass was partly luck, and the dossier says so.')
    c.bullet('No user study has been run. A protocol, consent form, task cards and analysis script are prepared in `docs/user_study/`, but no participant has been tested, so no usability claim is made.')
