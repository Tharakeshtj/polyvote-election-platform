"""System design and implementation."""
from data import fig


def build(c, S):
    c.h1('4. System Design')
    c.h2('4.1 Architecture')
    c.p('PolyVote is a single Python service built on FastAPI that exposes a REST interface and serves the React front end. Behind it are '
        'three stores, deliberately separated by what each is trusted with (' + c.ref('fig:arch') + '). The election database is a '
        'relational SQLite file that holds the roster, candidates and anonymous ballots. The verification database is a second SQLite file '
        'that holds voter email addresses and one-time-code challenges. The audit ledger is a MongoDB Atlas collection, with a local JSON '
        'file used when no connection string is configured. Secrets (database connection string, ledger key, SMTP credentials) live in '
        'environment variables, outside every store.')
    c.figure(fig('architecture.png'), 'Architecture of the final system with trust boundaries.', 'fig:arch', 6.4)
    c.p('**In plain words.** Read the picture from top to bottom. A voter\'s phone or the officer\'s browser talks to one program, the FastAPI service. That program keeps its information in three separate places: the ballots in one database, the voters\' email addresses and one-time codes in a second database, and the audit chain in MongoDB. They are kept apart so that someone who can open one of them cannot read or change the others. The secrets (database password, the key for the chain, the email password) are stored in a separate settings file that is not part of any database.', after=8)
    c.p('The separation matters for the threat model. An administrator of the election database cannot touch the ledger or the '
        'verification data, an administrator of the ledger store cannot touch ballots, and neither holds the secrets. Only the application '
        'host sees all three, which is why compromise of the host is outside the model (A6).')

    c.h2('4.2 Data model')
    c.p('The election schema has six tables (' + c.ref('fig:er') + '). `ORGANIZATION` hosts `ELECTION` rows, which own `CANDIDATE`, '
        '`VOTER_PARTICIPATION` and `BALLOT_RANKS` rows. `ADMIN_USERS` is a stand-alone table for officer sign-in. Multi-tenancy follows the '
        'shared-schema pattern [19]: all tenant data hangs off the election, and every query is scoped by `election_id`.')
    c.figure(fig('er.png'), 'Entity-relationship diagram: election database, verification database and ledger block.', 'fig:er', 6.4)
    c.p('**In plain words.** Each box is a table and each line shows how two tables are linked. The important point is what is missing: the ballot table has no line to the voter table, so nobody can look up who voted for whom. The dashed box is one block of the audit chain, and the right-hand frame is the separate database for emails and codes.', after=8)
    c.p('The rules the schema enforces are listed in ' + c.ref('tab:rules') + '. They are the first line of defence and apply to any client that '
        'speaks SQL, including an administrator console, provided foreign-key enforcement is switched on for the connection (Section 6.2).')
    c.table(
        ['Rule', 'Mechanism', 'Where'],
        [
            ['A voter cannot be marked as voted twice', '`BEFORE UPDATE OF has_voted` trigger raises ABORT when old and new are both 1', '`VOTER_PARTICIPATION`'],
            ['`has_voted` is 0 or 1', 'CHECK', '`VOTER_PARTICIPATION`'],
            ['One roster entry per voter per election', 'UNIQUE (`student_reg_no`, `election_id`)', '`VOTER_PARTICIPATION`'],
            ['A ballot ranks 1 to 3 choices', 'CHECK (`preference_rank` BETWEEN 1 AND 3)', '`BALLOT_RANKS`'],
            ['A candidate appears once per ballot', 'Composite PK (`ballot_token`, `candidate_id`)', '`BALLOT_RANKS`'],
            ['Ballots reference real candidates and elections', 'Foreign keys', '`BALLOT_RANKS`, `CANDIDATE`, `ELECTION`'],
            ['One verification record per voter contact', 'PK (`election_id`, `reg_no`)', '`VOTER_CONTACT`'],
            ['A challenge is open, used or locked', 'CHECK on `state`', '`OTP_CHALLENGE`'],
        ],
        [3.3, 4.8, 2.5], 'Integrity rules enforced inside the database engines.', 'tab:rules')

    c.h2('4.3 Separating the voter from the ballot')
    c.p('A ballot is stored under a random UUID, the ballot token, and the roster stores only whether a voter has voted. There is no '
        'column in `BALLOT_RANKS` that appears in `VOTER_PARTICIPATION`, other than the election identifier, and no timestamp on the roster '
        'row that could be matched to the order of ballots. A database administrator reading both tables can see that 45 voters voted and '
        'that 45 ballots exist, but not which ballot belongs to whom. The voter\'s email address is held in a different database again, keyed '
        'by registration number, so it cannot be joined to a ballot even if the election database is compromised. ' + c.ref('tab:privacy') +
        ' reports the automated check of this property.')

    c.h2('4.4 Casting a ballot')
    c.p('Casting is the only operation that touches all the structures, so it is serialised and transactional (' + c.ref('fig:cast') + '). '
        'After authentication the server takes a process-wide write lock, re-checks the election status, validates the ranking, and verifies '
        'that the voter has not already voted. In a single database transaction it sets `has_voted`, inserts the ranked rows under a new '
        'random token, and commits. It then computes the candidate roster hash, appends a sealed block to the ledger, invalidates the '
        'session and returns the token to the voter.')
    c.figure(fig('cast_transaction.png'), 'Flow of a ballot cast, with the failure exits.', 'fig:cast', 6.0)
    c.p('**In plain words.** Follow the arrows downward. Each diamond is a check, and if a check fails the vote is rejected (the red boxes on the right). Only a ballot that passes every check is saved, sealed in the audit chain and given a receipt.', after=8)
    c.p('The ledger append happens after the database commit. If the ledger were unreachable at that moment the ballot would exist without '
        'a receipt. The extended sweep detects exactly that situation (Section 4.6), and the receipt-lookup page shows a voter whether their '
        'token is present. A two-phase scheme that writes the receipt first would trade this for orphan receipts; we chose the variant that '
        'fails visibly.')

    c.h2('4.5 The audit ledger')
    c.p('Each ballot produces one block: its position in the chain (`index`), a timestamp, the election, the ballot token, `vote_data_hash`, '
        '`roster_hash`, the previous block\'s hash (`prev_hash`) and the block\'s own hash (`curr_hash`). `vote_data_hash` is the SHA-256 of '
        'the ordered (candidate, rank) pairs. `roster_hash` is the SHA-256 of the election\'s (candidate id, name) pairs at the time of '
        'the vote. `curr_hash` is computed over all other fields.')
    c.p('A conventional chain computes `curr_hash` with plain SHA-256 and no key. That makes the chain self-consistent but not authenticated: anyone who can write '
        'the ledger store can change a ballot\'s hash and then recompute every later block. The final design therefore computes `curr_hash` as '
        'HMAC-SHA-256 under a secret key (`LEDGER_KEY`) held outside the ledger and database. Verification recomputes each block with the same '
        'key and compares with a constant-time comparison. Blocks written before the key was introduced remain valid because the first '
        '`LEDGER_LEGACY_UNTIL` blocks are verified with plain SHA-256, which keeps old elections readable.')
    c.p('Two storage backends sit behind the same interface. With `MONGO_URI` set, blocks are documents in a MongoDB collection with a unique '
        'index on `index`. The unique index serves as a compare-and-swap: two concurrent appenders that compute the same next index cannot '
        'both insert, so the chain cannot fork. Without a connection string, blocks go to a local JSON file, protected by an in-process lock. '
        'The backend is chosen once at start-up and reported by `/api/health`.')

    c.h2('4.6 The integrity sweep')
    c.p('The sweep recomputes the state of an election from the database and compares it with the ledger. The first two rules are the basic checks; '
        'the other three close gaps the evaluation exposed in a basic sweep (' + c.ref('tab:sweep') + ').')
    c.table(
        ['Rule', 'Detects', 'How'],
        [
            ['1. Modified', 'A ballot whose ranks changed after sealing', 'Recompute SHA-256 of the ballot\'s ranks; compare with the block\'s `vote_data_hash`'],
            ['2. Deleted', 'A sealed ballot missing from the database', 'A block exists for a token that has no rows in `BALLOT_RANKS`'],
            ['3. Injected (new)', 'A ballot with no receipt', 'Rows exist in `BALLOT_RANKS` for a token with no block'],
            ['4. Roster changed (new)', 'Candidate names altered after voting', 'Current roster hash differs from the hash sealed in the blocks'],
            ['5. Count mismatch (new)', 'Flags, ballots and receipts disagree', 'Compare voted flags, distinct ballot tokens and blocks for the election'],
        ],
        [2.4, 3.6, 5.0], 'Rules applied by the integrity sweep.', 'tab:sweep')
    c.p('In addition, the chain check verifies every block\'s link and hash across the whole ledger. The two checks are complementary: the chain check '
        'finds edits inside the ledger, and the sweep finds edits to the database relative to a trusted ledger.')

    c.h2('4.7 Instant-runoff tally')
    c.p('The tally loads ballots as ordered lists of candidates and repeats three steps: count first preferences among continuing candidates, declare '
        'a winner if one holds more than half of the continuing ballots, otherwise eliminate the candidate with the fewest and transfer their ballots '
        'to the next surviving preference. Ballots that run out of preferences are exhausted. The engine returns a transcript of every round. '
        'Ties for last place are broken by candidate order, which is arbitrary; the interface marks any round where that happens so it is not mistaken '
        'for a principled result.')

    c.h2('4.8 Email one-time-password verification')
    c.p('A password alone no longer opens a ballot. When the OTP setting is enabled, a correct password produces a challenge instead of a session '
        '(' + c.ref('fig:otp') + '). The server generates a six-digit code with a cryptographically secure generator, stores only an HMAC of it, and '
        'emails the plain code from a background thread so the page never waits on the mail server. The voter enters the code, and only then does the '
        'server issue the voting session.')
    c.figure(fig('otp_sequence.png'), 'Sign-in with a one-time code: sequence of messages.', 'fig:otp', 6.3)
    c.p('**In plain words.** Time runs from top to bottom. The voter types a password, but the server does not let them in yet. It emails a 6-digit code and waits. Only when the voter types the right code does the server hand over the ballot. A stolen password alone is therefore not enough.', after=8)
    c.table(
        ['Parameter', 'Value', 'Purpose'],
        [
            ['Code', '6 digits, `secrets.randbelow`', 'Unpredictable; zero-padded'],
            ['Storage', 'HMAC-SHA-256 of `challenge:code` under a server secret', 'The database never holds a usable code'],
            ['Validity', '5 minutes', 'Limits the window for theft or guessing'],
            ['Guesses', '3 per code, then locked', 'About 3 in 10^6 chance per code'],
            ['Resends', '1 per 30 s, at most 5 per challenge', 'Resend cannot be used to keep guessing'],
            ['Challenges', '5 per voter per 15 minutes', 'Slows repeated password-then-guess attempts'],
            ['Use', 'Single use', 'A captured code cannot be replayed'],
            ['Delivery', 'SMTP over STARTTLS; failure logged, never blocks sign-in', 'The admin outbox still shows the code'],
        ],
        [1.8, 4.5, 4.3], 'Parameters of the one-time-code mechanism.', 'tab:otp')
    c.p('Voter addresses are entered per voter, or generated in bulk from one base mailbox using plus-addressing (`you+25bce0001@domain`), which lets a '
        'single inbox receive every code during a demonstration. Contacts, challenges and the mail log live in `polyvote_verification.db`, '
        'a different file from the election database. An administrator page, the Mail outbox, lists every code issued; plaintext codes are kept in '
        'memory only and are hidden after ten minutes.')

    c.h2('4.9 Election lifecycle and multi-tenancy')
    c.p('An election moves through Nomination, Voting and Closed, one step at a time and never backwards. Candidates may change only in Nomination, '
        'the roster may grow in Nomination and Voting, and ballots are accepted only in Voting. Because the lifecycle is stored in the database and '
        'enforced by the API, a closed election is read-only for voters. Many organisations share the platform; each election belongs to one organisation, '
        'and administrators see all of them, which is the model for a campus election office.')

    c.h2('4.10 Deployment and operation')
    c.p('The service runs from one command (`python -m uvicorn server:app --port 8000`) and serves the compiled front end from the same port. '
        'For the review it is exposed to the internet through a Cloudflare quick tunnel, which gives a temporary public HTTPS address without opening '
        'ports; the voter page shows a QR code for that address so a phone can open the ballot. The ledger is hosted on a free MongoDB Atlas cluster. All '
        'configuration is read from a git-ignored `.env` file (' + c.ref('tab:env') + '). We describe this honestly as public hosting from a laptop rather '
        'than cloud deployment: the tunnel address changes when it restarts, and the host must stay on.')
    c.p('For a link that does not depend on the laptop, the repository also builds as a Docker image (`Dockerfile`) and includes a Render blueprint (`render.yaml`) for a free public demo at `https://polyvote-bacse202.onrender.com`. On a free plan the service sleeps after about 15 minutes idle (the next visit takes about a minute) and its disk is wiped on every restart, so the demo seeds a fresh election at start-up. A public demo has no mailbox the visitor can open, so in demo mode the one-time code is shown on the screen, a banner says so, and factory reset is disabled. The `/demo` page lists every page of the application with a link and a one-line description, and gives a three-minute tour. A second blueprint (`render-live.example.yaml`) sends real emailed codes through an SMTP relay on port 2525, because the free plan blocks the usual mail ports.')
    c.table(
        ['Variable', 'Effect'],
        [
            ['`MONGO_URI`', 'Use MongoDB Atlas for the ledger (file fallback if unset or unreachable)'],
            ['`LEDGER_KEY`, `LEDGER_LEGACY_UNTIL`', 'Enable the keyed (HMAC) chain; number of earlier blocks that use plain SHA-256'],
            ['`OTP_REQUIRED`', 'Require the emailed code at voter sign-in'],
            ['`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`', 'Send real email; otherwise codes appear only in the admin outbox'],
            ['`PUBLIC_URL`', 'Address encoded in the voter-page QR code when opened on localhost'],
            ['`ADMIN_PASSWORD`', 'Replace the default administrator password'],
        ],
        [4, 6.6], 'Configuration read from the environment.', 'tab:env')

    # ------------------------------------------------------------------ 5
    c.h1('5. Implementation')
    c.h2('5.1 Technology and code size')
    c.p('The back end is Python 3.12 with FastAPI, SQLite through the standard library, pandas for the tally and `pymongo` for the ledger. The front end '
        'is React 19 with TypeScript, built by Vite. The Streamlit interface from Review 1 is retained for comparison. ' + c.ref('tab:loc') + ' lists the size of each part.')
    rows = [[k, f'{v:,}'] for k, v in S['loc'].items()]
    rows.append(['Total', f"{sum(S['loc'].values()):,}"])
    c.table(['Part', 'Lines'], rows, [6, 2], 'Source size (non-generated, including blank lines).', 'tab:loc')

    c.h2('5.2 Selected listings')
    c.p('The duplicate-vote trigger is the first line of defence for G1:')
    c.code('''CREATE TRIGGER trg_block_duplicate_vote
    BEFORE UPDATE OF has_voted ON VOTER_PARTICIPATION
    FOR EACH ROW
    WHEN OLD.has_voted = 1 AND NEW.has_voted = 1
    BEGIN
        SELECT RAISE(ABORT, 'DBMS Trigger Violation: Voter has already submitted a ballot.');
    END;''')
    c.p('The ledger keys its chain with an HMAC when a key is configured, and falls back to plain SHA-256 for legacy blocks:')
    c.code('''def _block_hash(index, block):
    data = json.dumps(block, sort_keys=True).encode()
    if LEDGER_KEY and index > LEGACY_UNTIL:
        return hmac.new(LEDGER_KEY, data, hashlib.sha256).hexdigest()
    return hashlib.sha256(data).hexdigest()''')
    c.p('Appending to the MongoDB ledger relies on the unique index on the block position, retrying if another writer won the slot:')
    c.code('''for _ in range(5):
    last = _coll.find_one({}, {'_id': 0}, sort=[('index', -1)])
    block = _seal(election_id, ballot_token, ranked_payload,
                  (last['index'] + 1) if last else 1,
                  last['curr_hash'] if last else GENESIS, roster_hash)
    try:
        _coll.insert_one(dict(block))
        return block
    except DuplicateKeyError:
        continue''')
    c.p('The sweep\'s three additions are short, because the data they need is already in hand:')
    c.code('''report["injected"] = [t for t in grouped if t not in ledger_dict]
sealed = {b['roster_hash'] for b in blocks if b.get('roster_hash')}
report["roster_changed"] = bool(sealed) and sealed != {current_roster}
counts = {"voted_flags": int(voted_flags), "ballots": len(grouped), "receipts": len(ledger_dict)}
if len(set(counts.values())) > 1:
    report["count_mismatch"] = counts''')
    c.p('Verifying a one-time code compares in constant time and records every failed attempt:')
    c.code('''if not hmac.compare_digest(row['code_hash'], _hash(challenge_id, code)):
    attempts = row['attempts'] + 1
    locked = attempts >= MAX_ATTEMPTS
    c.execute('UPDATE OTP_CHALLENGE SET attempts=?, state=? WHERE challenge_id=?',
              (attempts, 'locked' if locked else 'open', challenge_id))
    if locked:
        raise OtpError(410, "Too many wrong codes. Please sign in again.")
    raise OtpError(401, f"Incorrect code. {MAX_ATTEMPTS - attempts} attempts left.")''')

    c.h2('5.3 A defect found by the test suite')
    c.p('The first version of the OTP module passed its logic review but failed test F4 ("three wrong codes lock the challenge"). The cause was '
        'subtle: the attempt counter was updated inside a database context manager, and the handler then raised an HTTP error. The standard SQLite '
        'context manager rolls back when an exception leaves it, so every failed guess was recorded and then undone, and the attempt limit never took '
        'effect. A voter, or an attacker holding a password, could have guessed codes without limit. The fix is a small context manager that commits '
        'state changes before the exception propagates. We include this case because it shows the value of executable tests over review for security '
        'logic, and because the defect would not have been visible in normal use.')

    c.h2('5.4 Running the system')
    c.p('Setup is three steps: install the requirements and build the front end once, copy `.env.example` to `.env` and fill in the values needed, and start '
        'the server. Existing ledger entries can be copied to MongoDB with `migrate_ledger_to_mongo.py`, which refuses to overwrite a non-empty collection. '
        'The experiment suite (`experiments/run_experiments.py`) runs against a throwaway copy and never touches real data (Appendix C).')
