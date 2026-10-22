"""Status, limitations, conclusion, references, appendices."""
from pathlib import Path

from data import ROOT
from sec6_7 import LABEL


def build(c, S):
    tam = S['tamper']
    # ------------------------------------------------------------------ 8
    c.h1('8. Final Implementation Status')
    c.h2('8.1 What is implemented')
    c.p('Everything in the project plan is implemented and was exercised in the tests and the live demonstration. ' + c.ref('tab:status') + ' lists each component and the evidence.')
    c.table(
        ['Component', 'Status', 'Evidence'],
        [
            ['Normalised multi-tenant relational schema, constraints, trigger and views', 'Implemented', c.ref('tab:prev') + ', ' + c.ref('tab:rules')],
            ['Voter and admin web application (React and FastAPI), including QR-code voting', 'Implemented', c.ref('tab:demo') + ', ' + c.ref('fig:signin')],
            ['Instant-runoff counting with a round-by-round transcript', 'Implemented', c.ref('fig:results')],
            ['Keyed audit ledger in MongoDB Atlas with file fallback', 'Implemented', c.ref('tab:mongo') + ', ' + c.ref('fig:ledgertamper')],
            ['Integrity sweep with five rules', 'Implemented', c.ref('tab:tamper') + ', ' + c.ref('fig:sweeptamper')],
            ['Email one-time-code verification, voter emails and Mail outbox', 'Implemented', c.ref('tab:otptests') + ', ' + c.ref('fig:otpscreen') + ', ' + c.ref('fig:outbox')],
            ['Public HTTPS link: tunnel for live demos; Docker image and free cloud demo at https://polyvote-bacse202.onrender.com with a /demo guide to every page', 'Implemented', c.ref('tab:demo') + '; Section 4.10'],
            ['Executable test suite (47 scenarios) and benchmarks', 'Implemented', c.ref('tab:bench') + ', ' + c.ref('tab:conclusions')],
            ['Live demonstration with email OTP and QR voting', 'Done, worked end to end', c.ref('tab:demo')],
        ],
        [5.6, 1.9, 3.1], 'Implemented components and their evidence.', 'tab:status', size=9)
    c.h2('8.2 What was left out')
    c.p('The one deliberate substitution is the database engine. The plan named Oracle SQL with PL/SQL; we opted for SQLite for the relational layer. SQLite gives the same constraints, trigger and views that the project relies on, and the design is portable, '
        'but it has no PL/SQL stored procedures and no DCL roles, so those Oracle-specific features were not built. Two smaller extensions, several positions per election and a production-grade cloud deployment with persistent storage (the free demo host wipes its data on restart), are listed as future work in Section 9.')
    c.h2('8.3 Mapping to course outcomes')
    c.p('The mapping below follows our reading of the course outcomes for BACSE202 and should be adjusted to the official wording.')
    c.table(
        ['Outcome', 'Evidence in this report'],
        [
            ['Design a normalised relational schema with constraints', 'Section 4.2; ER diagram; rules table; prevention tests A1 to A7'],
            ['Use triggers, views and transactions for integrity', 'Sections 4.4 and 5.2; duplicate-vote trigger; atomic cast; concurrency test B11'],
            ['Apply database security and access separation', 'Sections 3, 4.3 and 4.8; voter/ballot separation; verification database; OTP tests'],
            ['Use a NoSQL store appropriately (polyglot persistence)', 'Sections 4.5 and 6.7; MongoDB Atlas ledger; benchmark against the file ledger'],
            ['Evaluate a design empirically and compare with alternatives', 'Sections 6 and 7; 47 scenarios; part-by-part comparison with related projects'],
            ['Communicate the work', 'This report, the review slides, the repository and the running public demonstration'],
        ],
        [4.4, 6.2], 'Course outcomes and where they are addressed.', 'tab:co', size=9.5)

    # ------------------------------------------------------------------ 9
    c.h1('9. Limitations and Future Work')
    c.table(
        ['Limitation', 'Why it matters', 'Direction'],
        [
            ['Host compromise or key theft (A6)', 'Whoever holds `LEDGER_KEY` and the stores can forge a consistent chain', 'Periodically publish the chain head to an external, append-only witness, in the manner of transparency logs [13]; keep the key in a managed secret store'],
            ['Roster injection (A7, scenario C13)', 'A ghost voter\'s ballot is valid and sealed', 'Commit the roster at registration close, with a signature or dual control; compare at sweep time'],
            ['Not end-to-end verifiable', 'A receipt shows a ballot is recorded and counted, not what it contains [38]', 'Add a cast-as-intended mechanism, or adopt a verifiable protocol where the threat model demands it [1], [2]'],
            ['Foreign keys depend on a per-connection setting (A5)', 'A console with default settings can insert dangling ballots', 'Move to Oracle or PostgreSQL, where constraints cannot be bypassed per connection [29]'],
            ['Passwords stored as plain SHA-256; default administrator password', 'Fast, unsalted hashes are weak against offline guessing [34], [35]; demo voters share a password', 'Use a salted, slow key-derivation function; force a password change on first login'],
            ['Email is a weak second factor', 'Whoever reads the mailbox passes the check [36], [37]', 'Offer an authenticator app (TOTP [33]) or a printed one-time slip as alternatives'],
            ['Receipt token links to the ballot content in the database', 'A voter who shows the token under duress reveals the ballot to anyone with database access', 'Encrypt ranks to a key not held by the database administrator'],
            ['IRV tie-breaking is arbitrary; no statistical audit', 'Close contests depend on an unprincipled rule [15], [16]', 'Define a published tie-break rule; add risk-limiting audit support'],
            ['Ledger append follows the database commit', 'A crash between them leaves a ballot with no receipt', 'The sweep detects it; a write-ahead outbox would remove it'],
            ['Single node, SQLite writer', 'Limits throughput and availability', 'A server database and a replicated service for larger elections'],
            ['Whole-chain verification reads every block', 'Verification time grows with the chain', 'Verify incrementally from a trusted checkpoint; Merkle structures [12]'],
            ['Oracle SQL not used', 'SQLite replaces Oracle SQL, so there are no PL/SQL procedures or DCL roles; several positions per election and a production-grade cloud deployment with persistent storage are also future work', 'Move the relational layer to Oracle with PL/SQL and roles, then deploy with persistent storage'],
        ],
        [3.0, 3.5, 4.2], 'Known limitations and planned work.', 'tab:limits', size=9)

    # ------------------------------------------------------------------ 10
    c.h1('10. Conclusion')
    c.p('PolyVote started as an election application whose integrity rested on trusting whoever could write to its database. This report shows how far that trust can '
        'be reduced using database features alone. Constraints and a trigger enforce one-person-one-vote and well-formed ballots in the engine; ballots and voters '
        'are stored without a linking column; a keyed hash-chained ledger in a separate document store seals each ballot; and a sweep that reconciles ballots, receipts, '
        'flags and the candidate roster exposes tampering. A second factor, a standalone emailed one-time code, addresses the weakness of password-only sign-in.')
    c.p(f'The evidence is executable. Of {len(tam)} tampering scenarios, a plain hash-chain baseline detected {sum(1 for t in tam if t["baseline"] == "detected")} automatically and the '
        f'final design detects {sum(1 for t in tam if t["patched"] == "detected")}. The two attacks a plain hash chain cannot stop, forging a receipt and rebuilding the chain, '
        'are caught once the chain is keyed. The cost is small: the sweep is about 14% slower at 10,000 ballots. One scenario, roster injection, is not detected, '
        'and we have said so, along with the other limits of a design that is not end-to-end verifiable.')
    c.p('We therefore claim a specific improvement: over a plain hash-chain design and over unprotected relational election applications, PolyVote substantially raises the '
        'cost of undetected tampering at the database layer and strengthens voter authentication, while remaining simple to run. We do not claim parity with cryptographic '
        'voting systems. The only planned feature left out is Oracle SQL with PL/SQL, because we opted for SQLite. Future work is the move to Oracle, an external witness for the chain head and a committed roster, is well defined and follows '
        'directly from the limitations reported here.')

    # ------------------------------------------------------------------ refs
    c.h1('References')
    refs = [r for r in Path(S['_refs']).read_text(encoding='utf-8').split('\n') if r.strip()]
    for r in refs:
        c.p(r, 'left', after=4, size=10.5)

    # ------------------------------------------------------------------ appendices
    c.page_break()
    c.h1('Appendix A: Schema Definitions')
    c.p('Election database (`setup_db.py`):', after=4)
    import re
    ddl = (ROOT / 'setup_db.py').read_text(encoding='utf-8').split("# 1. Base Tables")[1].split("conn.commit()")[0]
    ddl = re.sub(r'\n\s*\n+', '\n', ddl.replace("cursor.execute('''", '').replace("''')", '').replace('\r', ''))
    c.code(re.sub(r'\n    ', '\n', ddl).strip(), size=7.5)
    c.p('Verification database (`verification/otp.py`):', after=4)
    src = (ROOT / 'verification' / 'otp.py').read_text(encoding='utf-8')
    c.code(re.sub(r'\n\s*\n+', '\n', src.split("c.executescript('''")[1].split("''')")[0].replace('\r', '')).strip(), size=7.5)

    c.h1('Appendix B: REST Interface')
    c.table(
        ['Method and path', 'Who', 'Purpose'],
        [
            ['POST `/api/voter/login`', 'Voter', 'Check password; return a session, or an OTP challenge when verification is on'],
            ['POST `/api/voter/otp/verify`', 'Voter', 'Exchange challenge and code for a voting session'],
            ['POST `/api/voter/otp/resend`', 'Voter', 'Send a fresh code (rate-limited)'],
            ['GET, POST `/api/voter/ballot`', 'Voter', 'Fetch candidates; cast the ranked ballot'],
            ['GET `/api/receipts/{token}`', 'Public', 'Check that a ballot is sealed and counted'],
            ['GET `/api/elections`, `/api/config`, `/api/health`', 'Public', 'Open elections; public URL; ledger backend and sealing mode'],
            ['POST `/api/admin/login`', 'Admin', 'Administrator sign-in'],
            ['`/api/admin/elections` (GET, POST), `.../{id}`, `.../status`', 'Admin', 'Create, inspect and advance elections'],
            ['`.../candidates`, `.../candidates/seed`', 'Admin', 'Manage candidates (Nomination only)'],
            ['`.../voters`, `.../voters/bulk`', 'Admin', 'Manage the roster'],
            ['`.../contacts`, `.../contacts/fill`', 'Admin', 'Voter emails and bulk plus-address fill'],
            ['GET `/api/admin/otp/status`, `/api/admin/otp/outbox`', 'Admin', 'Verification settings; recent codes'],
            ['GET `.../integrity`, `.../tally`, `/api/admin/ledger`', 'Admin', 'Sweep, instant-runoff count, ledger and chain check'],
            ['`.../studio/*`', 'Admin', 'Simulated rogue-administrator edits for the tamper demonstration'],
        ],
        [5.0, 1.2, 4.6], 'Principal endpoints.', 'tab:endpoints', size=9)

    c.h1('Appendix C: Reproducing the Experiments')
    c.p('From the project directory, with Python 3.12 and the requirements installed:', after=4)
    c.code('''python experiments/run_experiments.py patched_r1     # final design (keyed chain on)
python experiments/run_experiments.py nokey          # final design, key off
python experiments/summarize.py                      # medians, summary.json, charts
python experiments/bench_mongo.py                    # Atlas append latency (needs MONGO_URI)''')
    c.p('The baseline was produced by pointing the same script at an earlier checkout with `EXP_SRC=<path>`. Each run writes `experiments/results/<tag>.json`. '
        'Runs use temporary copies of the application and never read or write the real database, ledger or `.env`.')

    c.h1('Appendix E: Demo Walkthrough and Workflow')
    c.p('**Public demo link:** `https://polyvote-bacse202.onrender.com` (free hosting: the first visit after idle can take about a minute). **Source code:** https://github.com/Tharakeshtj/polyvote-election-platform. The `/demo` page inside the application lists every page.', after=6)
    c.h2('E.1 Workflow of one election')
    c.table(['Step', 'Who', 'What happens', 'Where'],
            [['1', 'Officer', 'Creates the organisation and election', 'Admin, New election'],
             ['2', 'Officer', 'Adds candidates (only before voting opens)', 'Election, Candidates'],
             ['3', 'Officer', 'Registers voters and their email addresses', 'Election, Voters'],
             ['4', 'Officer', 'Opens voting', 'Election, Overview'],
             ['5', 'Voter', 'Opens the vote page (or scans the QR code), signs in with registration number and password', 'Vote page'],
             ['6', 'Voter', 'Enters the 6-digit code received by email', 'Vote page'],
             ['7', 'Voter', 'Ranks three candidates, reviews and casts; keeps the receipt token', 'Vote page'],
             ['8', 'Anyone', 'Checks that the receipt is sealed and counted', 'Check receipt'],
             ['9', 'Officer', 'Closes voting, runs the integrity sweep, counts the ballots', 'Election, Results'],
             ['10', 'Officer', 'Tamper test: edits or deletes a ballot in DB Studio, runs the sweep again', 'Election, DB Studio and Results']],
            [0.9, 1.2, 5.7, 3.0], 'Workflow of one election from set-up to audit.', 'tab:workflow', size=9)
    c.h2('E.2 Three-minute tour of the public demo')
    for s_ in ['Open the demo link and read the "Demo mode" banner; click **Demo guide** to see every page.',
               'Click **Vote** and sign in as `25BCE0025` with password `vote123` (voters `25BCE0019` to `25BCE0030` have not voted).',
               'Read the 6-digit code from the blue "Demo mode" box, type it in, rank three candidates, review and cast. Copy the receipt token.',
               'Open **Check receipt**, paste the token: the ballot is sealed in the ledger and counted.',
               'Open **Admin** (`admin` / `admin123` on the public demo only). Go to Election 1, **Results**, and run the sweep: it passes.',
               'In **DB Studio**, delete a ballot, return to Results and run the sweep again: the deleted ballot is named. Open **Audit ledger**: the chain is intact. Open **Mail outbox**: every code issued is listed.']:
        c.bullet(s_)
    c.h2('E.3 Class demonstration with real email codes')
    for s_ in ['Start the sample build with `START_DEMO.bat` and connect a Gmail App Password once with `SET_GMAIL.bat`.',
               'Create a new election, add five candidates, bulk-register five voters, and set their emails; open voting. Add two more voters by hand, each with their own email.',
               'Run the ballot simulation for the first four voters, then vote for the remaining three from a phone by scanning the QR code: each voter signs in, receives their own code by email, and casts.',
               'Close the election, run the sweep and the count, then edit one block in MongoDB Atlas and reload the Audit ledger to show the red "tampered" banner.']:
        c.bullet(s_)

    c.h1('Appendix D: Detail of Tampering Scenarios')
    c.table(
        ['ID', 'Scenario', 'Final design: evidence'],
        [[t['id'], t['attack'], t['patched_detail']] for t in tam],
        [0.6, 4.6, 5.6], 'Evidence recorded for each scenario under the final design.', 'tab:evidence', size=8)
    c.p('"flags" lists which checks fired: `sweep`, `chain`, or `counters`. "counts" are voted flags, ballots and receipts as seen by the administrator interface.', size=10.5)
