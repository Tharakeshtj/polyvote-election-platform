"""Cover, abstract, introduction, related work, threat model."""
from data import fig


def build(c, S):
    # ------------------------------------------------------------------ cover
    c.p('PolyVote', 'center', before=10, after=4, size=18, bold=True)
    c.p('A Multi-Tenant, Ranked-Choice Election Platform with a Tamper-Evident Audit Trail', 'center', after=18, size=12, italic=True)
    c.p('Project Review 3', 'center', after=12, size=15)
    c.p('Course: BACSE202 | Database Systems', 'center', after=0)
    c.p('Submitted by:', 'center', after=0)
    c.p('Tharakesharasu Thennarasu - 25BCE2699', 'center', after=0)
    c.p('M Pavan Durga Karthik - 25BCE2712', 'center', after=0)
    c.p('Shivam Malge - 25BCE0386', 'center', after=12)
    c.p('Faculty: Dr. Katari Balakrishna', 'center', after=18)

    c.p('Abstract', 'left', after=6, bold=True)
    c.p('Campus and organisational elections are usually run on a general-purpose database that the election officer, or anyone with '
        'database access, can edit without leaving a trace. PolyVote is a database-centric election platform that addresses this at the '
        'data layer. Relational constraints and a trigger enforce one vote per voter; the voter roster and the anonymous ballots are '
        'stored so that no column links them; every ballot is sealed in a hash-chained ledger kept in a separate document store '
        '(MongoDB Atlas); and an integrity sweep reconciles ballots, receipts and voter flags to expose tampering by someone with '
        'direct storage access. Ranked-choice (instant-runoff) tallying is built in, and one schema serves many organisations. This '
        'report presents the final system, with a keyed (HMAC) ledger chain, a sealed candidate roster, an extended sweep, a standalone '
        'email one-time-password module for voter authentication, a MongoDB Atlas ledger backend and public hosting. We evaluate the '
        'system with an executable suite of 47 scenarios (attacks, abuse cases and functional tests) and repeatable benchmarks. Against a conventional hash-chain-only baseline, '
        'the number of rogue-administrator tampering scenarios detected automatically rises from 6 of 13 to 12 of 13; the remaining '
        'case, roster injection through the administrative path, is documented as a limitation. We compare the design with published '
        'verifiable-voting systems and state precisely what it does and does not claim: it improves integrity enforcement and auditability '
        'at the database layer, but it is not an end-to-end verifiable cryptographic voting system. The final build, with the email one-time code and QR-code voting, was demonstrated live in class and completed the whole voter journey successfully; screenshots of that demonstration are included as proof. A free public demo is available at https://polyvote-bacse202.onrender.com.', after=8)
    c.p('**Keywords:** electronic voting, instant-runoff voting, database integrity, hash chain, HMAC, tamper-evident logging, polyglot '
        'persistence, MongoDB, multi-tenancy, one-time password.', 'justify', after=6)

    # ------------------------------------------------------------------ 1
    c.h1('1. Introduction')
    c.p('Elections for student councils, clubs, housing societies and professional bodies are rarely run on purpose-built, audited '
        'software. They are run on spreadsheets, survey forms or small web applications backed by a single relational database. In such '
        'a setup the person who administers the database is also the person who can change the outcome, and nothing in the system can '
        'show that a result has been altered. The literature on electronic voting has concentrated on cryptographic protocols that '
        'avoid trusting the server at all [1]-[5], and on the failures of deployed internet voting systems [6]-[9]. Between those two '
        'poles sits a large practical population of small elections for which cryptographic end-to-end verifiability is not available, '
        'yet where a much better job can be done simply by using the database properly.')
    c.p('PolyVote is our attempt at that middle ground. It treats the database as the place where election rules are enforced, rather '
        'than as a passive store behind application code, and it adds an independent, append-only audit trail that can be checked '
        'against the database after the fact.')
    c.h2('1.1 Problem statement')
    c.p('A conventional election application suffers from three weaknesses that a database course is well placed to address:')
    c.bullet('**Algorithmic deficiency.** Plurality counting can declare a winner who is opposed by most voters. Ranked-choice (instant-runoff) '
             'counting avoids that but is rarely implemented in small systems, and its rounds are hard to explain without a transcript.')
    c.bullet('**Structural rigidity.** Each election is built as a one-off schema. Reusing the platform for a second organisation means '
             'duplicating it, which multiplies the administrative surface.')
    c.bullet('**Database vulnerability.** Anyone with write access can modify, delete or insert ballots, reset a voter\'s "has voted" flag, '
             'or rename candidates, and a conventional application will not notice.')
    c.p('A fourth weakness is easy to overlook: sign-in relies on a single password, so a leaked or shared credential was '
        'enough to cast someone else\'s vote. The evaluators asked for a second factor, and this report responds with one.')
    c.h2('1.2 Contributions')
    c.p('This report documents the final design and implementation and makes the following contributions:')
    c.bullet('A **database-centric design** in which uniqueness, range, referential and one-vote rules are enforced by the schema and a trigger, '
             'and in which voter identity and ballot content are stored without any linking column (Sections 4.2 to 4.4).')
    c.bullet('A **keyed, hash-chained audit ledger** stored in MongoDB Atlas, with a sealed candidate roster and a file fallback. '
             'The chain can be extended only by a holder of the application secret (Section 4.5).')
    c.bullet('An **extended integrity sweep** that detects modified, deleted and injected ballots, renamed candidates and disagreement between '
             'voter flags, ballots and receipts (Section 4.6).')
    c.bullet('A **standalone email one-time-password module** with its own database, hashed single-use codes, expiry, attempt limits and rate '
             'limits, kept apart from the election data (Section 4.8).')
    c.bullet(f'A **reproducible evaluation**: {len(S["prevention"])} database-level prevention tests, {len(S["api_abuse"])} API abuse tests, '
             f'{len(S["tamper"])} tampering scenarios run against both a plain hash-chain baseline and the final design, {len(S["otp"])} OTP tests '
             'and benchmarks up to 10,000 ballots (Section 6).')
    c.bullet('A **scoped comparative study** against published verifiable-voting systems part by part against related projects, each verdict backed by our own test results, with explicit '
             'statements of what is not claimed (Section 7).')
    c.h2('1.3 Scope and non-goals')
    c.p('PolyVote targets small and medium elections whose officers are trusted to run the election but not trusted to leave no trace. It does not '
        'attempt coercion resistance, receipt-freeness against vote buyers, or protection against an adversary who controls the application '
        'host and its secrets. Those limits are discussed in Sections 3 and 9. PolyVote does not claim to compete with end-to-end verifiable '
        'systems on cryptographic strength; its claim is that, for the class of elections described, it removes the easiest and most likely '
        'attacks and makes the remaining ones detectable.')
    c.h2('1.4 Organisation')
    c.p('Section 2 reviews related work. Section 3 states the threat model and goals. Section 4 describes the design and Section 5 the '
        'implementation. Section 6 reports the evaluation, Section 7 the comparative study, Section 8 the final implementation status, '
        'Section 9 limitations and future work, and Section 10 concludes.')

    # ------------------------------------------------------------------ 2
    c.h1('2. Background and Related Work')
    c.h2('2.1 Verifiable electronic voting')
    c.p('Helios introduced web-based open-audit voting, in which ballots are encrypted in the browser and anyone can verify the published '
        'tally [1]. Belenios builds on a similar idea with stronger guarantees on eligibility and privacy [2], and Civitas adds coercion '
        'resistance at the cost of considerably more complex procedures [3]. Prêt à Voter [4] and Scantegrity II [5] aim at voter-verifiable '
        'paper-based elections, using randomised candidate orderings and confirmation codes respectively. These systems rest on cryptographic '
        'protocols and, in most cases, on trusted setup such as key ceremonies and independent trustees. They provide properties PolyVote does '
        'not: a voter can check that their ballot was recorded as intended without trusting the server. They also carry a procedural and '
        'operational burden that small organisations seldom accept.')
    c.h2('2.2 Deployed internet voting')
    c.p('Security analyses of deployed systems are sobering. The Estonian internet voting system, widely regarded as the most mature, was found '
        'to have significant weaknesses in its operational and procedural security [6]. Mobile and web voting products used in United States '
        'elections have been shown to contain vulnerabilities that could expose or alter votes [7], [8]. A National Academies study concluded that '
        'internet voting could not currently be secured [9], and Park et al. argue that blockchain-based voting, often proposed as a remedy, '
        'combines the problems of internet voting with new ones [14]. We take two lessons from this body of work. First, a design must state its '
        'threat model explicitly rather than advertise a technology. Second, claims about "immutable" ledgers must be examined: a ledger is '
        'only as trustworthy as the party who can write to it.')
    c.h2('2.3 Tamper-evident logging and ledger databases')
    c.p('Hash chaining for time-stamping was introduced by Haber and Stornetta [10], and Schneier and Kelsey showed how to build secure audit '
        'logs in which an attacker who compromises the logging machine cannot undetectably alter earlier entries [11]. Crosby and Wallach '
        'later gave efficient data structures for tamper-evident logging with logarithmic proofs [12], and Certificate Transparency applies '
        'Merkle trees to public logs [13]. In the database community, Snodgrass et al. studied tamper detection in audit logs [28] and Pavlou and '
        'Snodgrass the forensic analysis of database tampering [27]. Commercial and research ledger databases, such as SQL Ledger in Azure SQL '
        'Database, add cryptographically verifiable history to a relational engine [26]. PolyVote uses the simplest member of this family, a '
        'linear hash chain, and adds a keyed variant so that an attacker with access to the stored chain but not to the key cannot rebuild it.')
    c.h2('2.4 Ranked-choice voting and its auditing')
    c.p('Instant-runoff voting (IRV) eliminates the weakest candidate round by round until one holds a majority of continuing ballots. Its '
        'outcome can hinge on a small number of ballots, and computing how many ballots would have to change to alter it is a research '
        'problem in its own right [15], [17]. Risk-limiting audits for IRV have been developed [16], [18]. PolyVote does not implement a '
        'statistical audit. It provides a deterministic tally with a round-by-round transcript, and it flags the one source of arbitrariness in '
        'the algorithm, ties for last place, in the interface.')
    c.h2('2.5 Multi-tenancy and polyglot persistence')
    c.p('Aulbach et al. compare schema-mapping techniques for multi-tenant databases and show that a shared schema with a tenant identifier is '
        'the most economical approach [19], [20]. PolyVote follows that approach: one schema, with the organisation and election identifiers '
        'partitioning all data. Polyglot persistence, the use of different storage technologies for different kinds of data [21], [22], '
        'is a well-known response to the observation that no single data model fits all needs [23], [24]. PolyVote uses a relational store for '
        'rule-heavy transactional data and a document store for the append-only audit log.')
    c.h2('2.6 Database security and integrity enforcement')
    c.p('Bertino and Sandhu survey database security and list integrity constraints, access control and auditing as the foundations [25]. '
        'Declarative constraints and triggers are the standard mechanisms for enforcing integrity inside the engine [29], [30]. Their value for '
        'voting is that they apply to every client, including a database administrator\'s console, provided the engine is configured to '
        'enforce them. Section 6.2 shows one case where it is not, and discusses the consequence.')
    c.h2('2.7 Authentication factors')
    c.p('NIST SP 800-63B treats a memorised secret as one factor and requires a separate factor, such as a one-time code delivered to an '
        'authenticator the claimant controls, for higher assurance [31]. HOTP and TOTP define counter- and time-based one-time passwords [32], '
        '[33]. Email as an authentication channel is convenient but only as strong as the mailbox [37], and SMS or mobile channels have '
        'documented weaknesses [36]. Guidance on password storage recommends salted, slow key-derivation functions [34], [35]. PolyVote '
        'adds an emailed code as a second factor, and its passwords are stored with plain SHA-256, which does not follow that guidance (Section 9).')
    c.h2('2.8 Receipts and ballot secrecy')
    c.p('Voter receipts that prove a vote was counted without revealing its content were studied by Chaum [38]. Benaloh and Tuinstra '
        'showed that receipts must not allow a voter to prove how they voted if vote selling is to be resisted [39], and Juels et al. formalised '
        'coercion resistance [40]. PolyVote\'s receipt is deliberately weak in this respect: it proves that a ballot is recorded and still counted, '
        'but does not allow a voter to verify the ballot\'s content, and a voter who reveals the token reveals nothing about the ranks '
        'without database access. It is neither receipt-free in the strong sense nor verifiable end to end.')
    c.h2('2.9 Positioning')
    c.p('The systems above optimise for cryptographic assurance. The database literature offers tamper-evident structures but rarely applies '
        'them to a complete, usable election workflow. PolyVote occupies the gap: a complete multi-tenant ranked-choice application whose '
        'integrity story is built from database features, whose threats are enumerated, and whose claims are tested by an executable suite.')

    # ------------------------------------------------------------------ 3
    c.h1('3. Threat Model and Security Goals')
    c.h2('3.1 Assets')
    c.p('The assets to protect are (i) the correctness of the tally, (ii) the secrecy of each voter\'s ranking, (iii) the one-person-one-vote '
        'property, (iv) the eligibility of those who vote, and (v) the ability of an independent party to detect that any of these has been '
        'violated.')
    c.h2('3.2 Adversaries')
    c.p('We consider the adversaries in ' + c.ref('tab:adv') + '. They are ordered by capability. The first is addressed by authentication, '
        'the middle ones by the database and ledger design, and the last two mark the boundary of what the design claims.')
    c.table(
        ['ID', 'Adversary', 'Capability', 'Treatment'],
        [
            ['A1', 'Voter with a leaked or guessed password', 'Can sign in as someone else', 'Email one-time code; one-vote trigger'],
            ['A2', 'Network observer', 'Reads or alters traffic', 'Out of scope beyond TLS at the tunnel'],
            ['A3', 'Rogue database administrator', 'Read/write on the election database only', 'Integrity sweep detects'],
            ['A4', 'Ledger-store administrator', 'Read/write on the ledger store only', 'Hash chain with HMAC detects'],
            ['A5', 'Insider with both stores, no secrets', 'Edits both stores consistently', 'Keyed chain and sweep detect'],
            ['A6', 'Insider with both stores and the key', 'Can forge valid blocks', 'Not covered; needs external anchoring'],
            ['A7', 'Roster injection via the admin path', 'Adds a ghost voter, votes as them', 'Not covered; needs roster commitment'],
        ],
        [0.6, 3, 3.4, 3.2], 'Adversary model and how each adversary is treated.', 'tab:adv')
    c.figure(fig('threat_model.png'), 'Threat model overview: adversaries, capabilities and treatment.', 'fig:threat', 6.4)
    c.p('**In plain words.** Think of this table as a list of people who might try to cheat. Green means PolyVote stops them. Blue means PolyVote cannot always stop them but will catch them afterwards. Red means PolyVote does not protect against them yet. We show the red rows on purpose, so nobody is surprised later.', after=8)
    c.h2('3.3 Security goals')
    c.table(
        ['Goal', 'Statement', 'Mechanism'],
        [
            ['G1', 'No voter can vote twice', 'Trigger, `has_voted` CHECK, per-election UNIQUE roster, single-use sessions, write lock'],
            ['G2', 'Only rostered, verified voters vote', 'Roster lookup, password, emailed one-time code'],
            ['G3', 'Ballots are anonymous in storage', 'No column links `BALLOT_RANKS` to `VOTER_PARTICIPATION`; random ballot tokens'],
            ['G4', 'Malformed ballots are rejected', 'CHECK, composite PK, FK, API validation'],
            ['G5', 'Modification, deletion or insertion of stored ballots is detectable', 'Per-ballot ledger receipt, integrity sweep'],
            ['G6', 'The ledger cannot be silently rewritten by someone without the key', 'HMAC chain, unique block index, store separate from the database'],
            ['G7', 'Candidate attribution cannot be changed after voting', 'Roster hash sealed in each block'],
            ['G8', 'A voter can confirm their ballot is recorded and counted', 'Receipt token and public receipt check'],
        ],
        [0.7, 4, 5.5], 'Security goals and the mechanisms that serve them.', 'tab:goals')
    c.h2('3.4 Assumptions and non-goals')
    c.bullet('The application host and its environment secrets (`MONGO_URI`, `LEDGER_KEY`, `SMTP_PASS`) are not controlled by the adversary, except for A6.')
    c.bullet('A voter\'s mailbox is under that voter\'s control. Email is a weaker factor than a hardware token, and we say so.')
    c.bullet('The election officer chooses the roster honestly at registration. Verifying roster provenance is future work (A7).')
    c.bullet('We do not address coercion, vote selling, denial of service, or compromise of the voter\'s own device.')
