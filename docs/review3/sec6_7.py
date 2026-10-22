"""Evaluation and comparative study."""
import ast
import re

from data import fig

LABEL = {'detected': 'Detected', 'detected_manual_only': 'Counters only', 'undetected': 'Not detected',
         'prevented': 'Prevented', 'not_prevented': 'Not prevented', 'passed': 'Passed', 'FAILED': 'Failed'}


def build(c, S):
    base, pat = S['bench']['baseline'], S['bench']['patched']
    tam = S['tamper']
    n_det = lambda k: sum(1 for t in tam if t[k] == 'detected')  # noqa: E731
    n_man = lambda k: sum(1 for t in tam if t[k] == 'detected_manual_only')  # noqa: E731
    n_und = lambda k: sum(1 for t in tam if t[k] == 'undetected')  # noqa: E731

    c.h1('6. Evaluation')
    c.h2('6.1 Method')
    c.p('We evaluate the system with an executable suite (`experiments/run_experiments.py`) rather than by argument. The suite copies the application '
        'into a temporary directory, so it never touches real data, uses the file ledger so it never touches Atlas, drives the real HTTP API through '
        'FastAPI\'s test client, and models a rogue administrator by editing the SQLite file and the ledger file directly, with foreign keys off, '
        'as a database console would. It has five groups:')
    c.bullet('**A. Database-level prevention** (' + str(len(S['prevention'])) + ' tests): statements that should be rejected by the schema.')
    c.bullet('**B. API abuse** (' + str(len(S['api_abuse'])) + ' tests): wrong passwords, injection, replay, cross-election ranks, concurrency.')
    c.bullet('**C. Tampering** (' + str(len(tam)) + ' scenarios): edits by someone with direct storage access, each followed by the three checks an auditor '
             'has: the integrity sweep, the chain verification, and the three headline counters shown in the administrator interface.')
    c.bullet('**D. Privacy structure**: an automated check that ballots cannot be linked to voters by schema.')
    c.bullet('**E. OTP** (' + str(len(S['otp'])) + ' tests) and **F. Benchmarks** at 100, 1,000 and 10,000 ballots.')
    c.p('Each tampering scenario is run twice. The **baseline** is the plain hash-chain design (plain SHA-256 chain, two-rule sweep) that represents the conventional approach [10]-[12]; it is the earlier version of PolyVote, checked out from version '
        'control and run unchanged. The **final** design is the current code with the keyed chain enabled. The attacker scripts never receive the key. A '
        'scenario counts as *Detected* if the sweep or the chain check reports it, as *Counters only* if the only evidence is a disagreement between the '
        'three counters that an officer would have to notice by eye, and as *Not detected* otherwise. Benchmarks are the median of three repeated runs. '
        'Tampering outcomes were identical across the repeated runs.')

    # ---- A
    c.h2('6.2 Prevention at the database layer')
    c.table(['ID', 'Attempt', 'Mechanism', 'Result'],
            [[t['id'], t['attack'], t['mechanism'], LABEL[t['outcome']]] for t in S['prevention']],
            [0.6, 5.5, 2.2, 1.7], 'Statements submitted directly to the election database.', 'tab:prev')
    c.p('Six of the seven statements are rejected by the engine with its own error message. The exception, A5, is informative: SQLite enforces foreign keys '
        'only on connections that enable the setting, and a console opened with default settings does not. A rogue administrator can therefore insert a '
        'ballot that references a candidate that does not exist. Application connections enable the setting, and the extended sweep reports such a ballot '
        'as injected because it has no receipt, but the finding is a reminder that a constraint is only as strong as the engine\'s enforcement. A '
        'server database where the setting cannot be disabled per connection, which is the intended move to Oracle or PostgreSQL, removes this gap [29].')

    # ---- B
    c.h2('6.3 Abuse through the API')
    c.table(['ID', 'Attempt', 'Expected', 'Result'],
            [[t['id'], t['attack'], t['expected'], LABEL[t['outcome']]] for t in S['api_abuse']],
            [0.7, 5.0, 3.0, 1.7], 'Requests made against the public API.', 'tab:api')
    c.p('All thirteen are refused. B11 is the one that depends on concurrency control: twenty browser sessions of the same voter, opened before any of them voted, '
        'submit at the same instant behind a barrier, and exactly one ballot is stored. The write lock and the `has_voted` check inside the transaction together prevent '
        'the race that would otherwise let several of them pass the check at once.')

    # ---- C
    c.h2('6.4 Tampering by someone with storage access')
    c.p('This is the central experiment. ' + c.ref('tab:tamper') + ' lists the thirteen scenarios and the outcome under each design, and ' + c.ref('fig:detect') + ' summarises them.')
    c.table(['ID', 'Scenario', 'Baseline (plain chain)', 'PolyVote (final)'],
            [[t['id'], t['attack'], LABEL[t['baseline']], LABEL[t['patched']]] for t in tam],
            [0.6, 6.3, 1.9, 1.9], 'Outcome of each tampering scenario under the two designs.', 'tab:tamper')
    c.figure(fig('detection.png'), 'Detection outcome per scenario: plain hash-chain baseline versus PolyVote.', 'fig:detect', 6.3)
    c.p('**In plain words.** Each square is one attack, C1 to C13. Green means PolyVote found it automatically, yellow means it was only visible if someone compared the numbers by eye, and red means it was not found. The top row is the plain hash-chain baseline (6 green) and the bottom row is PolyVote (12 green). The one red square left is C13, adding a fake voter to the roster, which we explain in Section 9.', after=8)
    c.p(f'Under the plain hash-chain baseline, {n_det("baseline")} of {len(tam)} scenarios were detected automatically, {n_man("baseline")} were visible only as counter '
        f'mismatches, and {n_und("baseline")} were not detected at all. Under the final design, {n_det("patched")} are detected automatically, none rely on the '
        f'counters, and {n_und("patched")} is not detected. The scenarios behave as follows.')
    c.bullet('**C1 to C4** (change, replace or delete ballots in the database): detected by both designs, because the sweep compares each ballot with its receipt. '
             'In C4 the attacker also clears a voted flag to hide the gap; the deleted ballot is still found.')
    c.bullet('**C5** (inject a ballot with no receipt) and **C9** (truncate the last ledger block): the baseline sweep looked only at ballots that had a receipt, so '
             'neither was flagged; both were visible only because the ballot and receipt counts differ. The new "injected" rule and the reconciliation rule '
             'detect both automatically.')
    c.bullet('**C6** (ballot stuffing: inject a ballot, forge its receipt, and set a spare voter\'s flag so all counters agree) and **C10** (alter a ballot and rebuild the '
             'whole chain consistently) were completely undetected by the baseline. They are exactly the attacks a plain hash chain cannot stop, because the attacker can '
             'recompute every hash. With the keyed chain the forged or rebuilt blocks fail verification at the first block whose hash the attacker could not compute.')
    c.bullet('**C7, C8** (edit or delete a block): detected by both, by the chain check.')
    c.bullet('**C11** (swap two candidates\' names after voting): undetected by the baseline because names were outside the sealed data; the sealed roster hash now reveals it.')
    c.bullet('**C12** (reset a voted flag so the voter can vote again): both ballots have valid receipts, so only the disagreement between flags, ballots and receipts exposes it. '
             'It was visible only to a careful reader in the baseline and is now reported by the sweep.')
    c.bullet('**C13** (add a ghost voter to the roster and vote as them through the API) remains undetected. The ballot is valid, sealed and counted; what is false is the '
             'voter\'s eligibility, and the system holds no independent record of the roster to compare with. Closing this requires a signed or externally recorded '
             'roster, which we list as future work. We report it rather than hide it.')

    # ---- F (OTP)
    c.h2('6.5 One-time-password verification')
    c.table(['ID', 'Test', 'Expected', 'Result'],
            [[t['id'], t['test'], t['expected'], LABEL[t['outcome']]] for t in S['otp']],
            [0.6, 4.4, 4.0, 1.4], 'Tests of the email one-time-code module.', 'tab:otptests')
    c.p('All fourteen pass. F1 and F2 establish the basic contract: a correct password alone yields no session and the challenge identifier is not accepted as a '
        'bearer token, while the correct code does open the ballot. F3 to F8 cover replay, guess limits, expiry, resend limits and the cap on codes per challenge. '
        'F10 and F14 are privacy properties: no plaintext code is stored in the verification database, and the election database has no email column. F13 injects '
        'an unreachable mail server and confirms sign-in is not blocked and the failure is logged. F4 initially failed and exposed the rollback defect described in Section 5.3.')

    # ---- D
    c.h2('6.6 Voter and ballot separation')
    p = S['privacy']
    c.table(['Check', 'Result'],
            [['Columns shared by `BALLOT_RANKS` and `VOTER_PARTICIPATION`, excluding `election_id`', 'none'],
             ['Fields stored in a ledger block', ', '.join(f'`{x}`' for x in p[1]['result'])],
             ['Voter email stored in the election database', 'no (F14)'],
             ['Voter identifier present in any ledger block', 'no']],
            [6, 4.5], 'Automated check of the voter/ballot separation.', 'tab:privacy')
    c.p('A new field, `roster_hash`, was added to ledger blocks in the final design. It is a hash of the candidate list and carries no information about any voter.')

    # ---- E bench
    c.h2('6.7 Performance')
    c.p('All benchmarks use synthetic elections with five candidates. Ballots are seeded directly into the database and the ledger so that large sizes can be built '
        'quickly; the timed operations are the real ones. Results are medians of three runs on a laptop.')
    rows = []
    for n in base:
        rows.append([f'{int(n):,}', f"{base[n]['cast_ms']} / {pat[n]['cast_ms']}", f"{base[n]['sweep_ms']} / {pat[n]['sweep_ms']}",
                     f"{base[n]['chain_verify_ms']} / {pat[n]['chain_verify_ms']}", f"{base[n]['tally_ms']} / {pat[n]['tally_ms']}",
                     f"{base[n]['receipt_lookup_ms']} / {pat[n]['receipt_lookup_ms']}", f"{base[n]['ledger_file_kb']:,}"])
    c.table(['Ballots', 'Cast (ms)', 'Sweep (ms)', 'Chain verify (ms)', 'Tally (ms)', 'Receipt lookup (ms)', 'File (KB)'], rows,
            [1.0, 1.5, 1.5, 1.7, 1.4, 1.8, 1.1],
            'File-ledger timings, baseline / PolyVote (median of three runs).', 'tab:bench', size=9)
    c.figure(fig('bench.png'), 'Cast latency and sweep time against ledger size (log scales).', 'fig:bench', 6.2)
    c.p('**In plain words.** The left graph shows how long it takes to cast one ballot as the ledger grows. The right graph shows how long the integrity check takes. Both scales are logarithmic, so each step to the right is ten times more ballots. The two lines (old and final design) sit almost on top of each other, which shows the extra protection costs very little time.', after=8)
    c.p('Three observations follow. First, every read-side operation grows linearly with the number of ballots, which is expected from a design that recomputes '
        'rather than caches: at 10,000 ballots the sweep takes about ' + f"{pat['10000']['sweep_ms']:.0f}" + ' ms and the tally about ' + f"{pat['10000']['tally_ms']:.0f}" +
        ' ms, which is acceptable for the target scale. Second, the extra checks and the HMAC add little: the sweep is roughly ' +
        f"{(pat['10000']['sweep_ms'] / base['10000']['sweep_ms'] - 1) * 100:.0f}" + '% slower and chain verification ' +
        f"{(pat['10000']['chain_verify_ms'] / base['10000']['chain_verify_ms'] - 1) * 100:.0f}" + '% slower at 10,000 ballots. Third, cast latency with the file ledger grows from '
        f"{base['100']['cast_ms']}" + ' ms at 100 ballots to ' + f"{base['10000']['cast_ms']:.0f}" + ' ms at 10,000, because each append rewrites the whole JSON file. '
        'That growth is the practical argument for a real document store.')
    m = S['mongo']
    c.table(['Ballots already in ledger', 'Append, median (ms)', 'Append, 90th percentile (ms)', 'Verify whole chain (ms)'],
            [[f'{int(n):,}', m[n]['append_ms_median'], m[n]['append_ms_p90'], f"{m[n]['verify_ms']:,.0f}"] for n in m],
            [2.6, 2.3, 2.9, 2.6], 'Ledger operations against MongoDB Atlas over a mobile hotspot (20 appends per row).', 'tab:mongo', size=9.5)
    c.p('Against Atlas, appending costs about ' + f"{m['1000']['append_ms_median']:.0f}" + ' ms whatever the chain length, because the append reads only the last block and inserts one document, '
        'so the cost is one or two network round trips. At small sizes the local file is faster, and the crossover is near ten thousand ballots on this '
        'network. The reasons to prefer Atlas are therefore not raw speed but flat growth, concurrency control through the unique index, and holding the ledger '
        'outside the machine that runs the application. Whole-chain verification reads every block over the network and grows with the chain, from about '
        f"{m['100']['verify_ms'] / 1000:.1f}" + ' s at 100 blocks to ' + f"{m['10000']['verify_ms'] / 1000:.1f}" + ' s at 10,000. A production system would verify incrementally from a trusted checkpoint.')

    # ---- UI evidence
    c.h2('6.8 Application outputs')
    c.p('The figures below are screenshots from the running application. Names and addresses are demonstration values.')
    c.figure(fig('voter_signin_qr.png'), 'Voter sign-in, with the scan-to-vote QR code for phone voting.', 'fig:signin', 5.4)
    c.figure(fig('voter_otp.png'), 'Second factor: the voter enters the six-digit code sent to the address on file.', 'fig:otpscreen', 4.4)
    c.figure(fig('admin_outbox.png'), 'Administrator Mail outbox: each code issued, its recipient and delivery status.', 'fig:outbox', 6.2)
    c.figure(fig('admin_voters_email.png'), 'Voters tab with the email column and the bulk plus-address tool.', 'fig:voters', 6.2)
    c.figure(fig('voter_ballot_desktop.png'), 'Ranking the ballot on a desktop.', 'fig:ballot', 6.2)
    c.figure_row([fig('voter_signin_mobile.png'), fig('voter_ballot_mobile.png')], 'The same flow on a phone-sized screen.', 'fig:mobile', 2.6)
    c.figure(fig('voter_receipt.png'), 'Receipt token and ledger block returned after the ballot is sealed.', 'fig:receipt', 4.6)
    c.figure(fig('admin_results_clean.png'), 'Results before tampering: sweep passed, instant-runoff rounds.', 'fig:results', 6.2)
    c.figure(fig('admin_sweep_tamper.png'), 'Sweep after one ballot was deleted and another injected: both are reported even though the three counters still read 46 / 46 / 46.', 'fig:sweeptamper', 6.2)
    c.figure(fig('admin_sweep_roster.png'), 'Sweep after two candidate names were swapped.', 'fig:sweeproster', 6.2)
    c.figure(fig('admin_ledger_tampered.png'), 'Audit ledger after a block was edited: the chain check fails.', 'fig:ledgertamper', 6.2)

    c.h2('6.9 Live demonstration')
    c.p('The final build, Sample PolyVote, has the email one-time code switched on and was demonstrated live in class. The demonstration went through the complete voter journey and it worked end to end. '
        + c.ref('tab:demo') + ' lists each step, what was shown and the screenshot that serves as evidence.')
    c.table(['Step', 'What was shown', 'Result', 'Evidence'],
            [['1', 'Officer adds voters and their email addresses', 'Roster with an Email column; emails stored in a separate database', c.ref('fig:voters')],
             ['2', 'Voter opens the vote page; QR code shown', 'Phone opens the ballot by scanning the QR code', c.ref('fig:signin') + ', ' + c.ref('fig:mobile')],
             ['3', 'Voter signs in with the correct password', 'No ballot yet: the page asks for the emailed code', c.ref('fig:otpscreen')],
             ['4', 'Code is issued and sent', 'Code appears in the Mail outbox and arrives by email', c.ref('fig:outbox')],
             ['5', 'Voter enters the code and ranks three candidates', 'Ballot screen opens only after the right code', c.ref('fig:ballot')],
             ['6', 'Voter casts the ballot', 'Receipt token and ledger block returned', c.ref('fig:receipt')],
             ['7', 'Officer closes the election, runs the sweep and counts', 'Sweep passes; instant-runoff rounds shown', c.ref('fig:results')],
             ['8', 'Tamper test: ballot deleted and another injected', 'Sweep names both even though the counters still match', c.ref('fig:sweeptamper')],
             ['9', 'A ledger block is edited', 'Chain check shows a red "tampered" banner', c.ref('fig:ledgertamper')]],
            [0.6, 3.6, 4.0, 1.9], 'Steps of the live demonstration and the evidence for each.', 'tab:demo', size=9)
    c.p('The screenshots in Figures ' + c.ref('fig:signin').split()[-1] + ' to ' + c.ref('fig:ledgertamper').split()[-1] + ' come from the same build that was demonstrated. They show the one-time code stopping a password-only sign-in, '
        'the QR code opening the ballot on a phone, the receipt after voting, and the sweep and chain check catching tampering.')

    c.h2('6.10 Threats to validity')
    c.bullet('**Synthetic workload.** Elections are generated; real turnout patterns and larger rosters might differ. We used up to 10,000 ballots, which exceeds any single election we target.')
    c.bullet('**One machine and one network.** Timings come from a laptop, and Atlas timings from a mobile hotspot, so absolute values will differ elsewhere. We report ratios and trends.')
    c.bullet('**Attacker models are ours.** Scenarios C1 to C13 are the attacks we thought of, expressed against our own design. They are not a complete catalogue, and an author tends to test what the design handles.')
    c.bullet('**The baseline is our own earlier version.** We did not run Helios, Belenios or the commercial systems, so the comparison with them in Section 7 is qualitative and based on their published designs.')
    c.bullet('**Detection depends on running the sweep.** The system detects tampering when the officer runs the checks; it does not prevent it or alert automatically.')

    # ------------------------------------------------------------------ 7
    c.h1('7. Comparative Study')
    c.p('PolyVote is a combination of parts, so we compare it part by part with the related projects and technologies that do the same job. For every part we show what the others offer, what PolyVote achieved in our tests, and '
        'where the proof is in this report. We separate two kinds of evidence. **Measured evidence** comes from our own tests and benchmarks (Section 6) and is exact. **Published evidence** comes from the papers and vendor pages in the reference list; '
        'we did not run those systems, so statements about them are only as strong as their sources.')
    c.h2('7.1 Method and verdict rule')
    c.bullet('**Seven parts:** integrity rules inside the database, voter/ballot separation, the audit ledger, voter authentication, vote counting, storage architecture, and access (phone, QR code, setup).')
    c.bullet('**Verdict rule:** we write *Better* only where a test or benchmark in this report shows it. We write *Comparable* where the mechanism matches the alternative, and *Not better* where the alternative is stronger. Nothing is claimed without a table or figure to point to.')
    c.bullet('**Baseline:** for the ledger part we also measure a plain hash-chain design (the conventional approach in [10]-[12]) with the same attacks, so the comparison there is measured, not argued.')

    def part(title, intro, rows, label, caption, verdict):
        c.h2(title)
        c.p(intro)
        c.table(['Compared with', 'What it offers (source)', 'PolyVote: proven result', 'Evidence'], rows, [2.1, 3.0, 3.6, 1.9], caption, label, size=8.5)
        c.p('**Verdict.** ' + verdict)

    part('7.2 Part 1: integrity rules inside the database',
         'The job: refuse a second vote, a bad rank or a ballot for a missing candidate.',
         [['Form tools and typical student apps', 'One vote per person depends on sign-in or application code; the owner or administrator can edit stored answers', '6 of 7 database statements rejected by the engine; 13 of 13 API abuse tests refused; 20 simultaneous casts stored exactly 1 ballot', c.ref('tab:prev') + ', ' + c.ref('tab:api')],
          ['Server database constraints and triggers [29], [30]', 'The same mechanisms, enforced on every connection', 'The same mechanisms (trigger, CHECK, UNIQUE, foreign key). Gap found: SQLite enforces foreign keys only when switched on per connection (test A5)', c.ref('tab:prev') + ', test A5']],
         'tab:cmp-int', 'Part 1 compared with related approaches.',
         '*Better* than apps that enforce the rule only in application code (measured). *Comparable* to server databases in mechanism; *not better* on foreign-key enforcement until a server database is used.')

    part('7.3 Part 2: voter and ballot separation',
         'The job: make sure nobody can look up who voted for whom.',
         [['Helios [1], Belenios [2]', 'Ballots are encrypted; privacy depends on the server and trustees', 'No column links a ballot to a voter (automated check found none); voter emails are in a separate database (test F14)', c.ref('tab:privacy') + ', test F14'],
          ['Commercial hosted voting', 'Storage design is not published', 'Cannot be compared; we show our own evidence only', c.ref('tab:privacy')]],
         'tab:cmp-priv', 'Part 2 compared with related systems.',
         '*Comparable* for a small election: privacy comes from how the data is stored, which we tested. *Not better* than encryption: a voter who shows their receipt token reveals their ballot to anyone with database access (Section 9).')

    part('7.4 Part 3: the audit ledger',
         'The job: prove afterwards that stored ballots were not edited, deleted or added.',
         [['Plain hash chain [10], [11] (our baseline)', 'Detects edits inside the log, but an attacker who can write the log can recompute it', f'Baseline found {n_det("baseline")} of {len(tam)} attacks automatically; a forged receipt (C6) and a consistent rewrite (C10) went unnoticed', c.ref('tab:tamper') + ', ' + c.ref('fig:detect')],
          ['Merkle-tree logs [12], [13]', 'Short proofs that an entry is in the log; heavier to build', f'PolyVote (keyed chain plus sweep) found {n_det("patched")} of {len(tam)}; C6 and C10 now caught. Whole-chain check reads every block: {m["10000"]["verify_ms"] / 1000:.1f} s at 10,000 blocks on Atlas', c.ref('tab:tamper') + ', ' + c.ref('tab:mongo')],
          ['Ledger databases such as SQL Ledger [26]', 'Verifiable history built into the database engine', f"Similar goal using MongoDB Atlas and a sweep; cost of the extra protection: sweep +{(pat['10000']['sweep_ms'] / base['10000']['sweep_ms'] - 1) * 100:.0f}% at 10,000 ballots", c.ref('tab:bench')],
          ['Blockchain voting [14]', 'Criticised for adding risk without solving core voting problems', 'PolyVote uses no blockchain; one keyed chain with the key kept outside the stores', 'Section 2.2']],
         'tab:cmp-led', 'Part 3 compared with related approaches.',
         '*Better* than a plain hash chain (measured: ' + f'{n_det("baseline")} to {n_det("patched")} of {len(tam)}' + '). Simpler than Merkle logs but *not better*: checking is linear in the chain length, and anyone holding the key can still forge blocks.')

    part('7.5 Part 4: voter authentication',
         'The job: make sure the person voting is the person whose password is used.',
         [['Password only (form tools, typical student apps)', 'A leaked or shared password is enough', 'A correct password alone gives no session; the emailed code is also needed (tests F1, F2)', c.ref('tab:otptests')],
          ['NIST guidance [31]', 'Recommends a second factor held by the user', '14 of 14 tests: replay refused, lock after 3 wrong codes, expiry, resend and rate limits', c.ref('tab:otptests')],
          ['Email and phone channels [36], [37]', 'Convenient, but only as strong as the mailbox or device', 'Same limit applies; a mail failure never blocks sign-in (test F13); code also visible in the admin outbox', c.ref('tab:otptests') + ', ' + c.ref('fig:outbox')],
          ['Hardware tokens and authenticator apps [32], [33]', 'A stronger second factor', 'Not implemented (future work)', 'Section 9']],
         'tab:cmp-auth', 'Part 4 compared with related approaches.',
         '*Better* than password-only sign-in (14 of 14 tests, and the tests also found and fixed a real defect, Section 5.3). *Not better* than hardware tokens.')

    part('7.6 Part 5: vote counting',
         'The job: produce a winner with majority support and show how it was reached.',
         [['Plurality tools (forms, many student apps)', 'The winner can lack majority support', 'Instant-runoff rounds with a full transcript; ties for last place are flagged', c.ref('fig:results')],
          ['Audit research for ranked ballots [15]-[18]', 'Margin computation and risk-limiting audits', 'Not implemented: PolyVote counts and reports, with no statistical audit', 'Section 9']],
         'tab:cmp-count', 'Part 5 compared with related approaches.',
         '*Better* than plurality counting on the same ballots (the rounds are shown). *Not better* than audit tools, which PolyVote does not offer.')

    part('7.7 Part 6: storage architecture',
         'The job: keep ballots, emails and the ledger in the right kind of store and keep it fast as it grows.',
         [['Single-file or single-store designs', 'Ledger and data live in one place', f"File ledger: cost of one cast grows from {base['100']['cast_ms']:.0f} ms to {base['10000']['cast_ms']:.0f} ms between 100 and 10,000 ballots", c.ref('tab:bench')],
          ['Polyglot persistence [21], [22]; shared multi-tenant schema [19], [20]', 'Different stores for different data; one schema for many tenants', f"MongoDB Atlas append about {m['1000']['append_ms_median']:.0f} ms at any size; several elections and organisations ran in one install in the tests", c.ref('tab:mongo') + ', tests B8, B13']],
         'tab:cmp-store', 'Part 6 compared with related approaches.',
         '*Better* than a single file ledger once ballots grow (crossover near 10,000); for a very small election the file is faster. Multiple tenants and stores were exercised in the tests.')

    part('7.8 Part 7: access and ease of running',
         'The job: let voters join easily from any device and let a small team run the election.',
         [['Estonian i-voting [6]', 'National ID card and installed software', 'A web page opened by scanning a QR code; nothing to install; demonstrated from a phone', c.ref('tab:demo') + ', ' + c.ref('fig:signin') + ', ' + c.ref('fig:mobile')],
          ['Voatz [7], Democracy Live [8]', 'Mobile or web voting products; independent analyses found serious vulnerabilities', 'PolyVote has had no independent security analysis; we ran 47 tests ourselves', c.ref('tab:prev') + ' to ' + c.ref('tab:otptests')],
          ['Helios [1]', 'Needs key set-up and audit participation', 'One command starts the system; set-up steps in Section 5.4', 'Section 5.4']],
         'tab:cmp-access', 'Part 7 compared with related systems.',
         '*Better* for a small team to run and for voters to join (demonstrated), with the caveat that internet voting in general remains contested [9].')

    c.h2('7.9 Side-by-side comparison with CRUD apps, form tools, SaaS and cryptographic systems')
    c.p('A typical student voting project is a CRUD application: one table of votes, one password per user and no audit trail. Form tools (such as Google Forms) and commercial hosted voting services (SaaS) are the other things people actually use for small elections, '
        'and Helios and Belenios are the cryptographic reference points. We compare PolyVote with all four, first with a measurement and then property by property.')
    c.p('**Measurement.** Eight of our thirteen tampering scenarios apply to every design because they only change stored votes or voter flags (C1 to C5, C11, C12, C13); the other five (C6 to C10) forge or edit ledger entries, which a CRUD app does not have. '
        'We scored each design on those eight using only the checks it has. A typical CRUD app can compare its voted flags with its ballot count. The plain hash-chain baseline adds a receipt per ballot and a two-rule sweep. PolyVote adds the keyed chain and five sweep rules.')
    shared = ['C1', 'C2', 'C3', 'C4', 'C5', 'C11', 'C12', 'C13']
    byid = {x['id']: x for x in tam}

    def crud_hit(i):
        mm = re.search(r"counts (\{[^}]*\})", byid[i]['baseline_detail'])
        cc = ast.literal_eval(mm.group(1))
        return cc['voted_flags'] != cc['ballots']
    crud = [i for i in shared if crud_hit(i)]
    plain = [i for i in shared if byid[i]['baseline'] == 'detected']
    final = [i for i in shared if byid[i]['patched'] == 'detected']
    c.table(['Design', 'Checks it has', f'Detected of the {len(shared)} shared scenarios', 'Which ones'],
            [['Typical CRUD app', 'Voted flags compared with the ballot count', f'{len(crud)} of {len(shared)}', ', '.join(crud)],
             ['Plain hash-chain baseline', 'Receipt per ballot, two-rule sweep, chain check', f'{len(plain)} of {len(shared)} automatically', ', '.join(plain)],
             ['PolyVote (final)', 'Keyed chain, five-rule sweep, roster seal', f'{len(final)} of {len(shared)} automatically', ', '.join(final)]],
            [2.3, 3.5, 2.6, 2.2], 'Measured detection on the scenarios that apply to every design.', 'tab:crud-measure', size=9)
    c.p('A CRUD app notices only the attacks that change a count (C3, C5, C12). It misses edited ballots (C1, C2), a deletion that is hidden by clearing a flag (C4), and renamed candidates (C11). '
        'The baseline catches edited and deleted ballots but not renamed candidates or ghost voters; PolyVote adds the roster seal and the extra rules. The one scenario nobody here catches is C13, a ghost voter added to the roster.')
    c.table(['Property', 'CRUD app', 'Form tools', 'Commercial SaaS', 'Helios / Belenios', 'PolyVote', 'PolyVote evidence'],
            [['Ranked-choice counting', 'No', 'No', 'Advertised', 'Varies', 'Yes', c.ref('fig:results')],
             ['Many organisations', 'No', 'No', 'Yes', 'Partly', 'Yes', 'Tests B8, B13'],
             ['One-vote rule in the database', 'Rare', 'No', 'Not documented', 'n/a (crypto)', 'Yes', c.ref('tab:prev') + ', test B11'],
             ['Voter/ballot separation', 'Rare', 'No', 'Not documented', 'Yes [1], [2]', 'Yes', c.ref('tab:privacy')],
             ['Tamper detection', 'Counts only (' + f'{len(crud)}' + f' of {len(shared)})', 'No', 'Vendor logs', 'Yes [1], [2]', f'{len(final)} of {len(shared)}', c.ref('tab:crud-measure')],
             ['Second factor at sign-in', 'Rare', 'Account login', 'Often email links', 'Credential email', 'Emailed OTP', c.ref('tab:otptests')],
             ['Scan-to-vote on a phone', 'No', 'No', 'Varies', 'No', 'Yes', c.ref('tab:demo')],
             ['Voter verifies ballot content', 'No', 'No', 'Varies', 'Yes [1], [2]', 'No', 'Section 9'],
             ['Open source, one command', 'Often', 'No', 'No', 'Yes', 'Yes', 'Section 5.4'],
             ['Cost for a small election', 'Free', 'Free', 'Paid per voter', 'Free, operations-heavy', 'Free', 'Section 4.10']],
            [2.2, 1.2, 1.1, 1.3, 1.5, 1.0, 1.4], 'Property comparison; entries for other systems come from published designs and vendor pages (marked "Varies" or "Not documented" where we could not confirm).', 'tab:systems', size=8)

    c.h2('7.10 Part-by-part summary')
    c.table(['Part', 'Compared with', 'PolyVote proven result', 'Evidence', 'Verdict'],
            [['1 Integrity rules', 'Form tools; server databases', '6/7 DB tests, 13/13 API tests, 1 of 20 simultaneous casts', c.ref('tab:prev') + ', ' + c.ref('tab:api'), 'Better than apps; comparable to server databases'],
             ['2 Voter/ballot separation', 'Helios, Belenios', 'No shared column; email in separate store', c.ref('tab:privacy'), 'Comparable; weaker than encryption'],
             ['3 Audit ledger', 'Plain hash chain; Merkle logs; ledger databases', f'{n_det("patched")} of {len(tam)} attacks found vs {n_det("baseline")} for plain chain', c.ref('tab:tamper'), 'Better than plain chain; simpler than Merkle logs'],
             ['4 Authentication', 'Password only; hardware tokens', '14 of 14 OTP tests', c.ref('tab:otptests'), 'Better than password only; weaker than tokens'],
             ['5 Counting', 'Plurality; audit tools', 'Instant-runoff transcript, ties flagged', c.ref('fig:results'), 'Better than plurality; no audit'],
             ['6 Storage', 'Single file ledger', f"Atlas about {m['1000']['append_ms_median']:.0f} ms flat vs file {base['10000']['cast_ms']:.0f} ms at 10,000", c.ref('tab:mongo'), 'Better at scale'],
             ['7 Access', 'National and mobile apps; Helios', 'QR on a phone; one-command start; live demo', c.ref('tab:demo'), 'Easier to run and join']],
            [1.7, 2.0, 3.0, 1.6, 2.3], 'Part-by-part comparison and verdicts.', 'tab:cmp-summary', size=8.5)

    c.h2('7.11 What is unusual about the combination')
    c.p('We looked for a small-election system that combines all seven parts and publishes test evidence for each. We found strong systems for individual parts (cryptographic verifiability, hosted convenience, tamper-evident logs), '
        'but none that combines ranked-choice counting, rules enforced inside the database, a keyed audit ledger in a separate store, an emailed second factor and phone voting in one install that anyone can run with one command, '
        'with test results for every claim. In that sense PolyVote is unusual. We cannot prove that no such system exists, so we state it as what we found, not as a guarantee.')

    c.h2('7.12 Conclusions drawn from the evidence')
    c.table(['#', 'Conclusion', 'Evidence', 'Limit'],
            [['C-1', 'PolyVote finds twice as many tampering attacks automatically as a plain hash chain.', f'{n_det("baseline")} to {n_det("patched")} of {len(tam)} attacks, identical across 3 runs ({c.ref("tab:tamper")})', 'Attacks are the ones we designed; one (C13) is still missed.'],
             ['C-1b', 'A typical CRUD voting app notices only the tampering that changes a count.', f'{len(crud)} of {len(shared)} shared scenarios ({c.ref("tab:crud-measure")})', 'The CRUD model is our reasoned minimal design, not a specific product.'],
             ['C-2', 'A keyed chain stops attacks that a plain hash chain cannot.', 'C6 and C10 undetected by the baseline, detected by PolyVote', 'Whoever holds the key can still forge.'],
             ['C-3', 'The sweep catches changes that the counters hide.', f'{c.ref("fig:sweeptamper")}: deletion plus injection kept counters at 46/46/46 yet both were named', 'Needs the officer to run the sweep.'],
             ['C-4', 'Email OTP makes a stolen password insufficient and resists guessing.', '14 of 14 tests (F1 to F14), including limits and replay', 'Email is a weaker factor than a hardware token.'],
             ['C-5', 'The extra protection costs little time.', f"Sweep +{(pat['10000']['sweep_ms'] / base['10000']['sweep_ms'] - 1) * 100:.0f}% at 10,000 ballots; Atlas append flat", 'Synthetic data on one laptop.'],
             ['C-6', 'The whole system works end to end, including on a phone.', c.ref('tab:demo') + ' and the live demonstration', 'Small demonstration group.'],
             ['C-7', 'PolyVote is not an end-to-end verifiable system.', 'Voter cannot check ballot content (Section 9)', 'Helios and Belenios are stronger on this one property.']],
            [0.6, 3.6, 3.7, 2.7], 'Conclusions, their evidence and their limits.', 'tab:conclusions', size=8.5)
    c.p('**Overall finding.** Part by part, PolyVote is better than the simpler alternatives on integrity rules, the audit ledger, authentication, counting, storage at scale and ease of access, comparable on voter privacy, and weaker than cryptographic systems on ballot verifiability. '
        'For small and medium elections that need ranked-choice results, tested tamper detection and a one-command setup, it is the better fit; it is not a substitute for cryptographic systems where the administrator cannot be trusted or voters must verify their own ballot content.')
