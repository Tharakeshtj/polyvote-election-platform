# PolyVote uniqueness evidence (compiled 2026-10-23)

Scope: 33 systems compared against PolyVote features F1-F9. Every cell below was taken from the project's own page, README, docs or paper (URL recorded per cell in the sources section and in `uniqueness_evidence.json`). Where I could not read the project's own page the cell says "not documented" (ND) and the note says why. "Not documented" means I did not find it on the pages I read; it does not prove absence.

## Feature key

| Code | PolyVote feature |
|---|---|
| F1 | Ranked-choice / instant-runoff counting with a round-by-round transcript |
| F2 | Many organisations/elections on one install (multi-tenant) |
| F3 | Integrity rules enforced inside the relational database (trigger, CHECK, UNIQUE, FK) so a direct SQL client cannot double-vote |
| F4 | Ballots stored with no column linking them to voters; voter emails in a separate database |
| F5 | Tamper-evident audit ledger (HMAC-keyed hash chain) in a separate document store (MongoDB), with an integrity sweep reconciling ballots, receipts, voter flags and candidate list, plus an executable attack test-suite with published results |
| F6 | Emailed one-time-password second factor at voter sign-in (hashed single-use codes, expiry, attempt/rate limits) |
| F7 | QR-code scan-to-vote on a phone via a public HTTPS link and web app (no app install) |
| F8 | Voter receipt token to check a ballot is recorded and counted (not end-to-end verifiable) |
| F9 | One-command local run, free hosting, open source (GitHub) |

Cell codes: **Y** = documented as present, **P** = partially documented (the note says which part is missing), **N** = documented as absent or the documented design uses a different mechanism, **ND** = not documented on the pages read.

Important: F5 in full (HMAC key + separate document store + four-way reconciliation sweep + published attack results) is deliberately strict, so most systems get at best P on it. F1-F9 values for PolyVote itself are the user's claims and were not re-verified here.

## Comparison table

| # | System | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Helios Voting (helios-server) | N | ND | ND | P | P | ND | ND | Y | P |
| 2 | Belenios | P | P | ND | P | P | P | ND | Y | P |
| 3 | Civitas | P | ND | ND | P | P | N | ND | Y | ND |
| 4 | ElectionGuard (Microsoft / Election-Tech-Initiative) | ND | ND | ND | P | P | ND | ND | ND | P |
| 5 | Zeus (GRNET) | P | P | ND | ND | P | ND | ND | ND | P |
| 6 | Verificatum (vmn mix-net libraries) | ND | ND | ND | ND | ND | ND | ND | ND | ND |
| 7 | Vocdoni (vocdoni-node) | ND | ND | ND | ND | ND | ND | ND | ND | P |
| 8 | Aragon (aragon/client, Aragon 1) | ND | ND | ND | ND | ND | ND | ND | ND | ND |
| 9 | CIVS (Condorcet Internet Voting Service, Cornell) | P | P | ND | P | ND | P | ND | Y | Y |
| 10 | OpaVote | Y | P | ND | ND | ND | P | ND | ND | P |
| 11 | ElectionBuddy | P | P | ND | P | P | P | P | ND | P |
| 12 | Simply Voting | ND | P | ND | P | ND | ND | ND | Y | ND |
| 13 | Election Runner | ND | ND | ND | ND | ND | P | ND | ND | P |
| 14 | TapVoter | P | P | ND | P | P | P | P | Y | P |
| 15 | RankedVote | P | P | ND | ND | ND | P | ND | ND | N |
| 16 | BetterVoting (Equal-Vote/bettervoting, formerly star-server) | P | Y | ND | P | P | P | P | Y | Y |
| 17 | Google Forms | ND | ND | ND | P | ND | N | ND | ND | P |
| 18 | Microsoft Forms | P | ND | ND | P | ND | N | ND | P | ND |
| 19 | Voatz (mobile voting app) - USENIX Security 2020 analysis | ND | ND | ND | ND | P | ND | ND | ND | N |
| 20 | Democracy Live OmniBallot - USENIX Security 2021 analysis | ND | ND | ND | N | ND | ND | ND | ND | N |
| 21 | Decidim (decidim-elections + Bulletin Board) | ND | P | ND | ND | P | ND | ND | P | P |
| 22 | Consul Democracy | N | ND | ND | ND | P | P | ND | ND | Y |
| 23 | deOpty/flexyvotes (Django election + paid-voting platform) | Y | Y | Y | P | P | Y | N | Y | P |
| 24 | nnnnnndev/voting-app (FastAPI, faculty-meeting voting) | P | N | ND | P | ND | ND | ND | P | P |
| 25 | 9022574361/Online_Voting_System ('VeriVote') | ND | ND | P | P | P | P | ND | Y | P |
| 26 | DikshantMaskare/securevote-online-voting-system | ND | N | ND | ND | P | Y | ND | ND | P |
| 27 | RuchikaaVerma/SentinelVote-AI | ND | ND | P | N | P | ND | ND | ND | P |
| 28 | d-kanishka/Secure_Voting_System | N | ND | N | N | ND | N | N | ND | P |
| 29 | Prakhar-Pandey20/Online-Voting-System-otp-version | ND | ND | P | N | ND | P | ND | ND | ND |
| 30 | jevk/RCVElectionSystem | P | ND | ND | ND | ND | ND | ND | ND | P |
| 31 | dryairship/online-election-manager | ND | ND | ND | ND | ND | P | ND | ND | P |
| 32 | Dharanibalan45/Online-Voting-Platform | ND | ND | ND | ND | ND | P | ND | ND | ND |
| 33 | Lervez5/Kuraone | ND | ND | ND | ND | P | ND | ND | ND | N |

Rows 1-8 are verifiable/research/blockchain systems, 9-18 are commercial or free web services (incl. CIVS, BetterVoting, Google/Microsoft Forms), 19-20 are independent analyses of Voatz and Democracy Live, 21-22 are civic platforms (Decidim, Consul), 23-33 are student/hobby repositories (row 23, deOpty/flexyvotes, is the nearest match found). Row order follows the JSON file.

## Search log (what I actually tried)

Tools: the WebSearch and WebFetch tools, plus unauthenticated calls to `api.github.com/search/repositories` and `api.github.com/repos/...` (for stars, language, `pushed_at`) and raw.githubusercontent.com for files in one repository. GitHub code search was not used (it requires authentication).

Web searches (WebSearch):
1. Helios Voting system open-source verifiable online elections features
2. Belenios verifiable voting system Condorcet Schulze STV features
3. Civitas coercion-resistant electronic voting Cornell paper
4. ElectionGuard Microsoft github end-to-end verifiable
5. CIVS Condorcet Internet Voting Service Cornell
6. OpaVote ranked choice voting security features two-factor
7. BetterVoting STAR voting ranked choice voter id one-time email authentication ballot receipt documentation
8. docs.bettervoting.com Voter Authentication Modes (restricted to docs.bettervoting.com, bettervoting.com)
9. Helios voting does not support ranked choice instant runoff only approval select up to questions (no useful result)
10. Google Forms limit to 1 response sign in required one response per person (support.google.com only)
11. Microsoft Forms ranking question type only one response per person record name (support.microsoft.com only)
12. Security Analysis of the Democracy Live Online Voting System Specter Koppel Weitzner OmniBallot
13. Decidim elections module end-to-end verifiable Bulletin Board voting documentation
14. Consul Democracy voting module documentation polls booth verification
15. rcv.cloud ranked choice voting online features (rcv.cloud itself returned nothing; surfaced RankedVote, pyrcv, OpenRCV, DemoChoice)
16. Zeus election system GRNET open source e-voting STV ranked
17. open source voting app github instant-runoff multi-organization email OTP hash-chained audit log QR code vote anonymous ballots (extended mode) - this is the query that surfaced deOpty/flexyvotes
18. github e-voting "hash chain" "audit" "OTP" "MongoDB" PostgreSQL ballots unlinked voters student election
19. self-hosted ranked choice voting app open source organisations elections voters email github
20. online voting QR code scan to vote on phone email one-time code ranked choice student council election platform (surfaced TapVoter, Quick Vote Online)
21. github voting system "trigger" prevent double vote database level "append-only" ballots audit log HMAC chain MongoDB
22. Election Runner features ranked choice voter authentication audit (nothing about the product; homepage fetched directly)
23. Decidim Elections component end-to-end verifiable voting verification code multiple organizations (docs.decidim.org, github.com only)

GitHub repository searches (api.github.com/search/repositories, sorted by stars): "ranked choice voting web app"; "instant runoff voting flask"; "instant runoff voting django" (0 hits); "instant runoff voting fastapi"; "instant runoff voting"; "ranked choice voting election django" (0); "ranked choice voting fastapi"; "e-voting hash chain audit log"; "e-voting otp email"; "secure voting system database triggers"; "online voting system flask otp"; "voting system mongodb audit hash chain" (0); "online voting system hash chain blockchain python flask" (0); "voting system tamper-evident audit log hash chain" (0); "voting system HMAC audit ledger" (0); "student election voting system QR code"; "e-voting system mongodb audit"; "voting system anonymous ballot separate database receipt" (0); "college election voting system ranked choice" (0); "e-voting postgresql trigger one vote per voter" (0). The GitHub search is keyword-literal, so multi-word queries often return 0 or a handful of hits.

Pages fetched directly (WebFetch) include: github.com READMEs for helios-server, electionguard, vocdoni-node, aragon/client, civs, bettervoting, decidim-secure_elections, consuldemocracy, verificatum, flexyvotes and the other hobby repos; helios INSTALL.md, FAQ and landing page; belenios.org; civs1.civs.us and its sec_priv page; opavote.com, /help, two blog posts; electionbuddy.com/features; simplyvoting.com; electionrunner.com; tapvoter.com (two pages); rankedvote.co (two pages); zeus.grnet.gr (two pages); docs.bettervoting.com (voter-authentication, is_my_vote_secret, after_you_vote, security_options, counting_and_results); Google and Microsoft help pages; two USENIX abstract pages; docs.consuldemocracy.org voting page; electionguard.vote. For FlexyVotes I also downloaded and read README.md, docs/DATABASE.md, docs/TESTING.md, core/audit.py, core/otp.py, core/crypto.py, elections/tally.py and core/db_router.py.

Fetch failures worth knowing: gitlab.inria.fr (Belenios repo) blocked by a bot wall; civs.cs.cornell.edu failed TLS validation (used civs1.civs.us); cornell.edu Civitas pages failed certificate checks and the eCommons PDF returned HTML, so the Civitas paper was read from a PDF copy hosted at web.eecs.umich.edu (via curl + pdftotext); docs.decidim.org pages returned 404; documentation.helios.vote does not resolve; MIT's Voatz PDF was unreadable (abstract used); vocdoni.io returned only a title.

## Verdict: is there any project like this?

1. **Individually, every PolyVote feature exists somewhere.** Ranked/IRV counting with rounds (OpaVote, TapVoter, FlexyVotes, BetterVoting lists RCV), multi-tenant (FlexyVotes, BetterVoting teams, ElectionBuddy sub-groups), DB-level rules and triggers (FlexyVotes), unlinked ballots (FlexyVotes, CIVS, BetterVoting docs), hash-chained audit logs (FlexyVotes, VeriVote, SecureVote, SentinelVote, Kuraone), hashed expiring OTP with attempt limits (FlexyVotes, SecureVote), QR-based key/link distribution (TapVoter, BetterVoting, ElectionBuddy mailings), receipts (many).
2. **A close match exists and must be named: deOpty/flexyvotes** (https://github.com/deOpty/flexyvotes, Django 6/PostgreSQL, created 2026-08-10, latest commit 2026-10-23). Reading its README, DATABASE.md and code, it documents multi-tenant organisations, IRV/STV with per-round data, partial-unique-index and PL/pgSQL append-only triggers that block even raw SQL sessions, ballot rows with no voter FK, a per-organisation SHA-256 hash-chained audit log verified every 6 hours, hashed (HMAC) single-use email OTP with expiry, attempt limits and rate limits, a per-voter ballot tracker, a Merkle bulletin board and signed results. It is larger in scope than PolyVote (paid voting, billing, fraud scoring). It has no licence file I could find and 0 stars.
3. **What FlexyVotes does not document relative to F1-F9:** QR scan-to-vote (F7: QR only for event ticket check-in); an HMAC-keyed chain (its chain is plain SHA-256); a separate document store (everything is in one PostgreSQL); voter emails in a separate database (they are encrypted in the same DB); a reconciliation sweep across ballots/receipts/voter flags/candidates; published attack-test results (it has 204 tests including tamper/race/trigger tests but I found no published attack table); free hosting and an open-source licence.
4. **No system found documents all of F3 + F5 + F6 + F7 together.** FlexyVotes covers F3, F6 and a weaker F5 but not F7. TapVoter/BetterVoting/ElectionBuddy mention QR but with single-use keys or links, no DB-level rules and no hash-chain ledger. The F5 strict form (HMAC chain in a separate MongoDB with four-way reconciliation and published attacks) was not documented by anything I found; the nearest MongoDB hash-chain with an audit endpoint is 9022574361/Online_Voting_System, which uses a plain SHA-256 chain and a manual tamper demo.
5. **Compared with the verifiable systems (Helios, Belenios, Civitas, ElectionGuard, Zeus), PolyVote is weaker on cryptographic guarantees**: none of F1-F9 gives end-to-end verifiability, and its F8 receipt is explicitly not E2E. Those systems are not close on features but they are the correct benchmark for integrity claims, and a claim of being "more secure" than them would not be supportable.
6. **Honest summary:** the combination F3+F5(strict)+F6+F7 was not found in my search, but a very near neighbour (FlexyVotes) was found, so "unique" or "no similar project exists" is not supportable; "a free, small-election tool combining X, Y and Z that I could not find elsewhere in this search" is.

### Closest three matches and what each lacks

| Rank | Project | Covers | Lacks relative to F1-F9 |
|---|---|---|---|
| 1 | deOpty/flexyvotes (github.com/deOpty/flexyvotes) | F1 (IRV/STV, per-round data), F2, F3 (triggers + partial unique), F4 mostly, F5 partly, F6, F8 | F7; HMAC key on chain; separate document store; separate voter-email DB; reconciliation sweep; published attack results; licence/free hosting (F9 partial) |
| 2 | 9022574361/Online_Voting_System "VeriVote" (github.com/9022574361/Online_Voting_System) | F5 partly (SHA-256 chain in MongoDB + chain-audit endpoint + tamper demo), F4 partly (ballots without voter identity), F6 partly (email OTP, rate limits), F8 (receipt hash) | F1 (no ranked counting), F2, F3 (no triggers/CHECK/FK), HMAC, reconciliation sweep, automated attack suite, F7, one-command run, licence |
| 3 | BetterVoting (github.com/Equal-Vote/bettervoting, bettervoting.com) | F1 (RCV listed; rounds unverified), F2 (organisations/teams), F4 partly (identity stripped before publishing), F7 partly (QR share), F8 (email receipt), F9 (AGPL, free) | F3 (not documented), F5 (only an admin-action audit log), F6 (unique emailed links; docs mention no OTP/2FA), reconciliation, attack suite |

Honourable mentions: TapVoter (commercial, IRV, single-use keys via QR poster/email, receipt codes, public audit log, free tier; closed source, no DB-level or hash-chain claims); DikshantMaskare/securevote (hashed OTP with expiry and attempt limits + hash-linked ledger + Railway deploy; no ranking, single-instance by design); nnnnnndev/voting-app (IRV, two-store separation, HMAC voter receipts; JSON storage, Entra ID sign-in).

### Limits of this search

- Search tools: WebSearch (US-only, summarised results), WebFetch (a small model summarises each page, so details can be dropped or mis-summarised), and the unauthenticated GitHub repository-search API (keyword-literal, 60 requests/hour, no code search).
- Not searched or not reachable: GitHub code search, GitLab/Gitee/Bitbucket, SourceForge, app stores, Devpost/Kaggle, private repositories, non-English repositories, forks that renamed everything, and commercial products' internal implementation. Many student repositories are never indexed by a keyword search.
- Several queries returned 0 repositories, which reflects the search method, not proof that nothing exists.
- I judged documentation, not running behaviour (except that I read FlexyVotes code excerpts). A README claim is not a guarantee that code does it, and silence is not proof of absence.
- Snapshots (stars, last update) are as of 2026-10-23 via the GitHub API.

## What a skeptical evaluator could object to

1. "You found FlexyVotes in one lucky query; there are likely more." True - the search is not exhaustive; the correct claim is "not found in this search", not "does not exist".
2. "F5 is defined so narrowly that only PolyVote can match it." The strict definition (HMAC key + separate MongoDB + four-way sweep + published attack results) is what makes it distinctive; the underlying idea (hash-chained append-only log) is common (FlexyVotes, VeriVote, SecureVote, SentinelVote, Kuraone). Present it as a combination, not a first.
3. "An HMAC chain and a separate store help only if the key and the second store are outside the attacker's reach." If the same app server holds both the HMAC key and the Mongo credentials, an attacker with app compromise can rewrite both. The benefit is against a database-only attacker or a SQL insider; that should be stated, and ideally tested (the attack suite is the evidence).
4. "DB-level constraints are standard practice, not an innovation." Agreed; FlexyVotes does the same and more (append-only triggers). The claim to make is that PolyVote tests them from a direct SQL client, if its published results show that.
5. "Documented is not implemented, and ND is not 'no'." Cells are based on what I could read; commercial products may do more than their marketing pages say, and some pages (Decidim bulletin board, Zeus technical docs, Belenios repo, Vocdoni docs) were not readable.
6. "OTP and QR flows exist in commercial tools you did not test." TapVoter, ElectionBuddy and others have single-use keys, optional phone confirmation and QR mailings; I could not see their OTP internals (hashing, expiry), so F6 and F7 for commercial tools are P/ND by lack of documentation, not proof they lack them.
7. "Receipt token is weak compared with E2E verifiability." Yes - Helios, Belenios, ElectionGuard and FlexyVotes' Merkle bulletin board offer stronger verification than a receipt; PolyVote should not compare itself on that axis.
8. "Student-project repos with 0 stars are not real competition, yet one of them (FlexyVotes) is the closest." Stars do not measure feature overlap; FlexyVotes also has no licence, so it is not reusable by default, but it does show the feature set is reachable by one developer in about two months.
9. "Free hosting and one-command run are marketing, not engineering." True; they matter for the small-election audience (TapVoter, BetterVoting and CIVS also offer free hosted use), so they are not unique.
10. "Dates and star counts will change." All snapshots are from 2026-10-23.

## Sources and per-cell evidence

### 1. Helios Voting (helios-server)
- Page: https://github.com/benadida/helios-server
- Type: open-source, verifiable (E2E) | Stack: Python/Django + JavaScript; PostgreSQL, RabbitMQ/Celery | Stars/users: 926 GitHub stars; hosted at vote.heliosvoting.org | Last update: 2026-08-15 (GitHub API pushed_at)
- F1 = no: https://raw.githubusercontent.com/benadida/helios-server/master/helios/models.py
- F2 = not documented: https://vote.heliosvoting.org/faq
- F3 = not documented: https://github.com/benadida/helios-server/blob/master/INSTALL.md
- F4 = partial: https://vote.heliosvoting.org/
- F5 = partial: https://vote.heliosvoting.org/faq
- F6 = not documented: https://vote.heliosvoting.org/
- F7 = not documented: https://vote.heliosvoting.org/faq
- F8 = yes: https://vote.heliosvoting.org/faq
- F9 = partial: https://github.com/benadida/helios-server/blob/master/INSTALL.md
- Notes: F1 'no' is inferred from code: Election.one_question_winner in helios/models.py picks winners by raw vote count (result_type absolute/relative); no ranked/IRV code seen in that file; docs do not mention ranked ballots. F4: landing page says votes are private (cryptographic secrecy, not schema-level unlinking). F5: public ballot tracker + 'open-audit' verifiability, not a keyed hash chain/reconciliation sweep. F6: landing page lists GitHub/Google login only; FAQ does not cover voter auth. F9: Apache-2.0; install needs Postgres 12+, RabbitMQ, Python 3.13, uv (about 9 steps), so not one command; free hosted instance not verified as free.

### 2. Belenios
- Page: https://www.belenios.org/
- Type: open-source, verifiable (E2E), hosted platform + self-host | Stack: OCaml (AGPL-3.0); GitHub mirror glondu/belenios | Stars/users: >1,400 elections/yr in 2020-21 (Cortier, Gaudry, Glondu paper via search snippet); GitHub mirror 156 stars | Last update: 2026-10-16 (GitHub mirror pushed_at); belenios.org release notes through 2024
- F1 = partial: https://www.belenios.org/
- F2 = partial: https://www.belenios.org/
- F3 = not documented: https://www.belenios.org/
- F4 = partial: https://www.belenios.org/
- F5 = partial: https://www.belenios.org/
- F6 = partial: https://www.belenios.org/
- F7 = not documented: https://www.belenios.org/
- F8 = yes: https://www.belenios.org/
- F9 = partial: https://www.belenios.org/
- Notes: F1: release notes document ranking/preferential ballots with Condorcet-Schulze (1.17) and STV (2.2); IRV and round transcripts not documented. F2: public voting platform where anyone can set up an election; multi-tenant architecture not stated. F4: cryptographic secrecy, ballots appear on public ballot box tied to voter credential (not DB-level separation). F5: public verifiable ballot box; 2.0 note describes chaining of election events; no HMAC key, separate document store, reconciliation sweep or attack suite documented. F6: 1.16 note: default voter authentication is an email with a short code at voting time; hashing/expiry/limits not documented. F8: 'voters can check that their ballots have been received', 'every voter can check that her vote has been counted'. gitlab.inria.fr page was blocked by Anubis bot wall so repo README was not read. License AGPL-3.0 per release note (2016-07-25).

### 3. Civitas
- Page: https://research.cs.cornell.edu/civitas
- Type: research prototype (coercion-resistant, verifiable) | Stack: Jif/Java (JifE), academic prototype | Stars/users: n/a (academic); S&P 2008 + Cornell TR 2007-2081 | Last update: Technical report revised 2008
- F1 = partial: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F2 = not documented: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F3 = not documented: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F4 = partial: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F5 = partial: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F6 = no: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F7 = not documented: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F8 = yes: https://web.eecs.umich.edu/~bchandra/courses/papers/Clarkson_Civitas.pdf
- F9 = not documented: https://research.cs.cornell.edu/civitas
- Notes: Read from pdftotext of the 2008 paper (the Cornell eCommons PDF returned an HTML error to curl). Paper: prototype supports plurality, approval and ranked ballots (ranked ballots introduce covert channels for coercion); tally method for ranking not described as IRV. Voters authenticate with anonymous credentials from registration tellers (not email OTP). Bulletin board + universal/voter verifiability. Source-code availability and licence not verified (cornell.edu cert error on fetch).

### 4. ElectionGuard (Microsoft / Election-Tech-Initiative)
- Page: https://github.com/Election-Tech-Initiative/electionguard
- Type: open-source SDK for E2E verifiable elections | Stack: C++ core + Python reference (electionguard-python); MIT | Stars/users: 878 GitHub stars (169 for electionguard-python) | Last update: 2026-06-10 (GitHub API pushed_at)
- F1 = not documented: https://github.com/Election-Tech-Initiative/electionguard
- F2 = not documented: https://github.com/Election-Tech-Initiative/electionguard
- F3 = not documented: https://github.com/Election-Tech-Initiative/electionguard
- F4 = partial: https://github.com/Election-Tech-Initiative/electionguard
- F5 = partial: https://github.com/Election-Tech-Initiative/electionguard
- F6 = not documented: https://github.com/Election-Tech-Initiative/electionguard
- F7 = not documented: https://www.electionguard.vote/
- F8 = not documented: https://www.electionguard.vote/
- F9 = partial: https://www.electionguard.vote/
- Notes: An SDK for vendors, not a ready voting website; README says homomorphic encryption, end-to-end verification and ballot-comparison audit support. Ranked choice, multi-election, voter authentication and ballot tracking codes were not mentioned on the pages fetched (not the same as absent in the code or spec). MIT licence, 'no fee for using ElectionGuard' per electionguard.vote.

### 5. Zeus (GRNET)
- Page: https://zeus.grnet.gr/
- Type: open-source, verifiable, hosted service (Greek research network) | Stack: Python/Django fork of Helios (per search snippet only; not verified on own page) | Stars/users: claims >10,000 polls / 1.56M voters on homepage (self-reported; older pages cite 700-830 elections) | Last update: not verified
- F1 = partial: https://zeus.grnet.gr/
- F2 = partial: https://zeus.grnet.gr/zeus/landing
- F3 = not documented: https://zeus.grnet.gr/
- F4 = not documented: https://zeus.grnet.gr/zeus/landing
- F5 = partial: https://zeus.grnet.gr/
- F6 = not documented: https://zeus.grnet.gr/
- F7 = not documented: https://zeus.grnet.gr/
- F8 = not documented: https://zeus.grnet.gr/
- F9 = partial: https://zeus.grnet.gr/zeus/landing
- Notes: Homepage lists party lists, score voting or STV and 'verifiable elections with one or more polls'. Landing page says open source and free for voters. Mixnet/anonymity details are only in the JETS paper (search result), not fetched. Source repository not fetched.

### 6. Verificatum (vmn mix-net libraries)
- Page: https://github.com/verificatum
- Type: open-source cryptographic libraries (mix-net) | Stack: Java, JavaScript, C | Stars/users: n/a | Last update: not verified
- F1 = not documented: https://github.com/verificatum
- F2 = not documented: https://github.com/verificatum
- F3 = not documented: https://github.com/verificatum
- F4 = not documented: https://github.com/verificatum
- F5 = not documented: https://github.com/verificatum
- F6 = not documented: https://github.com/verificatum
- F7 = not documented: https://github.com/verificatum
- F8 = not documented: https://github.com/verificatum
- F9 = not documented: https://github.com/verificatum
- Notes: Libraries only (verificatum-vmn, vjsc, ...); the org profile shows no end-user voting application, so F1-F9 are not applicable to the library itself. Included only because the brief asked for it.

### 7. Vocdoni (vocdoni-node)
- Page: https://github.com/vocdoni/vocdoni-node
- Type: open-source blockchain (Vochain) voting protocol | Stack: Go; AGPL-3.0 | Stars/users: 92 GitHub stars | Last update: 2026-10-19 (GitHub API pushed_at)
- F1 = not documented: https://github.com/vocdoni/vocdoni-node
- F2 = not documented: https://github.com/vocdoni/vocdoni-node
- F3 = not documented: https://github.com/vocdoni/vocdoni-node
- F4 = not documented: https://github.com/vocdoni/vocdoni-node
- F5 = not documented: https://github.com/vocdoni/vocdoni-node
- F6 = not documented: https://github.com/vocdoni/vocdoni-node
- F7 = not documented: https://github.com/vocdoni/vocdoni-node
- F8 = not documented: https://github.com/vocdoni/vocdoni-node
- F9 = partial: https://github.com/vocdoni/vocdoni-node
- Notes: README documents purpose, Go 1.23 and AGPL-3.0 only; voting types, auth and receipts are in separate developer docs that were not fetched (vocdoni.io page returned only a title). The Decidim Vocdoni module README (github.com/vocdoni/decidim-secure_elections) mentions an optional per-election 'second-factor challenge' but does not describe types.

### 8. Aragon (aragon/client, Aragon 1)
- Page: https://github.com/aragon/client
- Type: open-source DAO / blockchain governance app | Stack: JavaScript; AGPL-3.0 | Stars/users: 824 GitHub stars | Last update: 2026-03-26 (GitHub API pushed_at)
- F1 = not documented: https://github.com/aragon/client
- F2 = not documented: https://github.com/aragon/client
- F3 = not documented: https://github.com/aragon/client
- F4 = not documented: https://github.com/aragon/client
- F5 = not documented: https://github.com/aragon/client
- F6 = not documented: https://github.com/aragon/client
- F7 = not documented: https://github.com/aragon/client
- F8 = not documented: https://github.com/aragon/client
- F9 = not documented: https://github.com/aragon/client
- Notes: README describes creating and managing decentralized organisations on Ethereum; no voting mechanism documented on the page, so all features are 'not documented'. Token-weighted DAO voting is a different problem space.

### 9. CIVS (Condorcet Internet Voting Service, Cornell)
- Page: https://civs1.civs.us/
- Type: free hosted service + open-source (MIT) software | Stack: Perl CGI (github.com/andrewcmyers/civs, MIT) | Stars/users: 96 GitHub stars; 'tens of thousands of polls' over ~20 years (Cornell paper, via search snippet) | Last update: 2026-08-21 (GitHub API pushed_at)
- F1 = partial: https://civs1.civs.us/
- F2 = partial: https://civs1.civs.us/
- F3 = not documented: https://civs1.civs.us/sec_priv.html
- F4 = partial: https://civs1.civs.us/sec_priv.html
- F5 = not documented: https://civs1.civs.us/sec_priv.html
- F6 = partial: https://civs1.civs.us/sec_priv.html
- F7 = not documented: https://civs1.civs.us/
- F8 = yes: https://civs1.civs.us/sec_priv.html
- F9 = yes: https://github.com/andrewcmyers/civs
- Notes: F1: ranked ballots with Condorcet and a proportional-representation mode; IRV and round transcripts not documented on pages read. F2: any supervisor can create polls on the hosted service. F4: voter e-mail addresses erased once the election begins; ballots stored under a hash of the receipt. F5: security page states no separate audit process (only the voter receipt). F6: private polls give each voter a unique emailed key (hash of email + authorization key + server private key; only hashes stored) - single-use emailed key, but no second factor/expiry/attempt limits documented. The www civs.cs.cornell.edu host failed TLS validation in the fetch tool, so civs1.civs.us (same service) was used.

### 10. OpaVote
- Page: https://www.opavote.com/
- Type: commercial/freemium SaaS | Stack: closed SaaS (Google-hosted per vendor blog) | Stars/users: customers: nonprofits, student groups, parties (vendor/FairVote statements) | Last update: vendor blog 2017-12; site current
- F1 = yes: https://www.opavote.com/
- F2 = partial: https://www.opavote.com/help
- F3 = not documented: https://www.opavote.com/
- F4 = not documented: https://blog.opavote.com/2017/12/opavote-security-practices.html
- F5 = not documented: https://www.opavote.com/
- F6 = partial: https://blog.opavote.com/2017/12/opavote-security-practices.html
- F7 = not documented: https://www.opavote.com/
- F8 = not documented: https://www.opavote.com/help
- F9 = partial: https://www.opavote.com/
- Notes: Homepage: plurality, STV, IRV, Condorcet, approval, Borda; 'step-by-step explanation' of each count. Voters get single-use secret email links (128-bit code per vendor blog) and on-site single-use codes; blog says 2FA applies to the admin account, not voters. Raw ballots downloadable for recount (not a tamper-evident ledger). Free up to 25 voters/10 candidates. Open source: not mentioned.

### 11. ElectionBuddy
- Page: https://www.electionbuddy.com/features/
- Type: commercial SaaS | Stack: closed SaaS | Stars/users: free tier up to 20 voters | Last update: site current
- F1 = partial: https://www.electionbuddy.com/features/
- F2 = partial: https://www.electionbuddy.com/features/
- F3 = not documented: https://www.electionbuddy.com/features/
- F4 = partial: https://www.electionbuddy.com/features/
- F5 = partial: https://www.electionbuddy.com/features/
- F6 = partial: https://www.electionbuddy.com/features/
- F7 = partial: https://www.electionbuddy.com/features/
- F8 = not documented: https://www.electionbuddy.com/features/
- F9 = partial: https://www.electionbuddy.com/features/
- Notes: Lists preferential ballot and STV but no round-by-round tallies; sub-group management and multiple admins; each voter gets a single-use personal voting key, optional second password or phone confirmation (OTP/email code not named); states votes cannot be linked to voters (claim, no mechanism); voter audit report and independent verification; QR codes only on mailed postcards; no per-voter receipt documented; open source not mentioned.

### 12. Simply Voting
- Page: https://www.simplyvoting.com/
- Type: commercial SaaS | Stack: closed SaaS | Stars/users: not documented | Last update: site current
- F1 = not documented: https://www.simplyvoting.com/
- F2 = partial: https://www.simplyvoting.com/
- F3 = not documented: https://www.simplyvoting.com/
- F4 = partial: https://www.simplyvoting.com/
- F5 = not documented: https://www.simplyvoting.com/
- F6 = not documented: https://www.simplyvoting.com/
- F7 = not documented: https://www.simplyvoting.com/
- F8 = yes: https://www.simplyvoting.com/
- F9 = not documented: https://www.simplyvoting.com/
- Notes: Homepage: several ongoing elections selectable by voters; 'each vote is encrypted to ensure anonymity'; admin chooses a voter authentication method (types not named); receipt issued after voting and receipt codes in downloadable vote file. Ranked ballots, QR, audit and open source not mentioned on the homepage.

### 13. Election Runner
- Page: https://www.electionrunner.com/
- Type: commercial SaaS | Stack: closed SaaS | Stars/users: free up to 20 voters | Last update: site current
- F1 = not documented: https://www.electionrunner.com/
- F2 = not documented: https://www.electionrunner.com/
- F3 = not documented: https://www.electionrunner.com/
- F4 = not documented: https://www.electionrunner.com/
- F5 = not documented: https://www.electionrunner.com/
- F6 = partial: https://www.electionrunner.com/
- F7 = not documented: https://www.electionrunner.com/
- F8 = not documented: https://www.electionrunner.com/
- F9 = partial: https://www.electionrunner.com/
- Notes: Homepage only: unique Voter ID + Voter Key, one vote each, optional email notice, import from CSV/Excel, SSL and 256-bit encryption. Voting methods, audit, receipts, QR not stated on this page (not verified elsewhere).

### 14. TapVoter
- Page: https://tapvoter.com/
- Type: commercial/freemium SaaS aimed at student councils | Stack: closed SaaS | Stars/users: not documented | Last update: site current
- F1 = partial: https://tapvoter.com/use-cases/school-board-election/
- F2 = partial: https://tapvoter.com/use-cases/school-board-election/
- F3 = not documented: https://tapvoter.com/
- F4 = partial: https://tapvoter.com/use-cases/school-board-election/
- F5 = partial: https://tapvoter.com/
- F6 = partial: https://tapvoter.com/
- F7 = partial: https://tapvoter.com/use-cases/school-board-election/
- F8 = yes: https://tapvoter.com/use-cases/school-board-election/
- F9 = partial: https://tapvoter.com/
- Notes: Closest commercial match for the student-council use case: Ranked Choice (IRV), STAR, Approval; each eligible voter gets a single-use key that can be distributed through a QR code on a poster or school email lists (QR distributes the key; scan-to-vote flow and HTTPS link details not described); ballots 'carry no voter identity'; Audit Center can void/restore a ballot by receipt code and a public transparency log lists receipt codes; CAPTCHA; several elections can run at once. Free tier (unlimited elections up to 10,000 voters, Pro $4.99/mo). Open source and DB-level rules not mentioned. No emailed OTP second factor documented (keys are single-use, emailed as a Pro perk).

### 15. RankedVote
- Page: https://rankedvote.co/
- Type: commercial SaaS (ranked-choice only) | Stack: closed SaaS (Civic Tech Field Guide: not open source) | Stars/users: not documented | Last update: site current
- F1 = partial: https://rankedvote.co/
- F2 = partial: https://rankedvote.co/program
- F3 = not documented: https://rankedvote.co/
- F4 = not documented: https://rankedvote.co/
- F5 = not documented: https://rankedvote.co/
- F6 = partial: https://rankedvote.co/
- F7 = not documented: https://rankedvote.co/
- F8 = not documented: https://rankedvote.co/
- F9 = no: https://civictech.guide/projects/rankedvote
- Notes: Page says elimination and redistribution repeat automatically and non-unique votes can be filtered; team accounts with roles. Auth, receipts, audit, QR not on pages read. F9 'no' rests on a Civic Tech Field Guide statement surfaced in search (page itself not fetched).

### 16. BetterVoting (Equal-Vote/bettervoting, formerly star-server)
- Page: https://github.com/Equal-Vote/bettervoting
- Type: open-source (AGPL-3.0) + free hosted service bettervoting.com | Stack: TypeScript; docker-compose in repo | Stars/users: 74 GitHub stars | Last update: 2026-10-22 (GitHub API pushed_at)
- F1 = partial: https://bettervoting.com/
- F2 = yes: https://bettervoting.com/
- F3 = not documented: https://docs.bettervoting.com/contributions/developers/6_voter_authentication_modes.html
- F4 = partial: https://docs.bettervoting.com/help/is_my_vote_secret.html
- F5 = partial: https://docs.bettervoting.com/help/security_options.html
- F6 = partial: https://docs.bettervoting.com/contributions/developers/6_voter_authentication_modes.html
- F7 = partial: https://bettervoting.com/
- F8 = yes: https://docs.bettervoting.com/help/after_you_vote.html
- F9 = yes: https://github.com/Equal-Vote/bettervoting
- Notes: Closest OPEN-SOURCE operating product for 'free, small elections, RCV'. Homepage lists voting methods including ranked-choice (instant-runoff), email/ID-list/one-time-code voter authentication (homepage wording), ballot receipts, QR code sharing, auditing, organisation/team support, free and open source. Docs are narrower: six auth modes (email list = BetterVoting emails each voter a unique link; ID list; open modes via cookie/Keycloak/IP) and the developer page and Security Options page explicitly mention no OTP/2FA, so the homepage 'one-time codes' is probably single-use links (not verified). 'Is My Vote Secret?': identifying info removed before ballots are published, random order, ballot ID in anonymised data. Audit log tracks admin sharing of a voter's link and revealing the voter/ballot link; vendor says more auditing is planned. Receipt = email link to your own ballot. Round-by-round RCV output and DB-level constraints not verified. QR on homepage is for sharing the election link, not a scan-to-vote flow documented in docs.

### 17. Google Forms
- Page: https://support.google.com/docs/answer/2839588
- Type: commercial free general-purpose forms | Stack: closed SaaS | Stars/users: n/a | Last update: help page current
- F1 = not documented: https://support.google.com/docs/answer/2839588
- F2 = not documented: https://support.google.com/docs/answer/2839588
- F3 = not documented: https://support.google.com/docs/answer/2839588
- F4 = partial: https://support.google.com/docs/answer/2839588
- F5 = not documented: https://support.google.com/docs/answer/2839588
- F6 = no: https://support.google.com/docs/answer/2839588
- F7 = not documented: https://support.google.com/docs/answer/2839588
- F8 = not documented: https://support.google.com/docs/answer/2839588
- F9 = partial: https://support.google.com/docs/answer/2839588
- Notes: 'Limit to 1 response' requires Google sign-in; usernames not recorded unless email collection is on. No ranking question type, tally, audit or receipt mentioned on that page (not proof of absence elsewhere in Google docs). Free to use but not open source.

### 18. Microsoft Forms
- Page: https://support.microsoft.com/en-us/office/create-a-form-with-microsoft-forms-4ffb64cc-7d5d-402f-b82e-b1d49418fd9d
- Type: commercial general-purpose forms (part of Microsoft 365) | Stack: closed SaaS | Stars/users: n/a | Last update: help page current
- F1 = partial: https://support.microsoft.com/en-us/office/create-a-form-with-microsoft-forms-4ffb64cc-7d5d-402f-b82e-b1d49418fd9d
- F2 = not documented: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F3 = not documented: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F4 = partial: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F5 = not documented: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F6 = no: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F7 = not documented: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F8 = partial: https://support.microsoft.com/en-us/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665
- F9 = not documented: https://support.microsoft.com/en-us/office/create-a-form-with-microsoft-forms-4ffb64cc-7d5d-402f-b82e-b1d49418fd9d
- Notes: A Ranking question type exists ('More question types'), but no ranked-choice/IRV tallying is documented; 'One response per person' and 'Record name' are org-only settings; verification codes/OTP and audit log not mentioned in the settings article; respondents can request a PDF/email receipt of their answers. Not open source.

### 19. Voatz (mobile voting app) - USENIX Security 2020 analysis
- Page: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- Type: commercial proprietary mobile voting app (independent analysis) | Stack: closed (Android/iOS app) | Stars/users: used in West Virginia 2018 midterms and others | Last update: analysis 2020
- F1 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F2 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F3 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F4 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F5 = partial: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F6 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F7 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F8 = not documented: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- F9 = no: https://www.usenix.org/conference/usenixsecurity20/presentation/specter
- Notes: Abstract: Voatz claims a permissioned blockchain, mixnet and biometrics/hardware keys; authors report 'no public formal description of Voatz's security model' and found vote-alteration/exposure flaws. F5 'partial' = claimed blockchain only, publicly unverified. The full MIT PDF was unreadable to the fetch tool, so only the abstract was used.

### 20. Democracy Live OmniBallot - USENIX Security 2021 analysis
- Page: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- Type: commercial proprietary online ballot delivery/return (independent analysis) | Stack: closed web platform | Stars/users: used in Delaware, New Jersey (halted per paper) and others | Last update: analysis 2021
- F1 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F2 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F3 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F4 = no: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F5 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F6 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F7 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F8 = not documented: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- F9 = no: https://www.usenix.org/conference/usenixsecurity21/presentation/specter-security
- Notes: Abstract: client sends voter identity, ballot selections and browser fingerprint to the vendor, which the authors say jeopardises the secret ballot (so F4 'no'); 'simplistic' integrity model vulnerable to malware and insiders; no audit, blockchain or receipt mentioned.

### 21. Decidim (decidim-elections + Bulletin Board)
- Page: https://github.com/decidim/decidim
- Type: open-source civic participation platform (AGPL-3.0) | Stack: Ruby on Rails | Stars/users: 1,833 GitHub stars | Last update: 2026-10-23 (GitHub API pushed_at)
- F1 = not documented: https://github.com/vocdoni/decidim-secure_elections
- F2 = partial: https://docs.decidim.org/bulletin-board/develop/manual/decidim-integration/elections-component
- F3 = not documented: https://github.com/vocdoni/decidim-secure_elections
- F4 = not documented: https://github.com/vocdoni/decidim-secure_elections
- F5 = partial: https://docs.decidim.org/bulletin-board/develop/manual/decidim-integration/elections-component
- F6 = not documented: https://github.com/vocdoni/decidim-secure_elections
- F7 = not documented: https://github.com/vocdoni/decidim-secure_elections
- F8 = partial: https://docs.decidim.org/bulletin-board/develop/manual/decidim-integration/elections-component
- F9 = partial: https://github.com/decidim/decidim
- Notes: NOT independently verified: docs.decidim.org bulletin-board pages returned HTTP 404 on direct fetch; the claims come from a web-search summary of those pages (Elections component for end-to-end verifiable elections; Bulletin Board = separate public append-only log, ElectionGuard-based per another page; 'connected instance is used by all organizations'). Vocdoni's decidim-secure_elections README (fetched) says it is an optional layer over upstream decidim-elections that 'sends ballots to the Vocdoni voting network instead of the Decidim database'. Ranked choice not mentioned.

### 22. Consul Democracy
- Page: https://github.com/consuldemocracy/consuldemocracy
- Type: open-source civic participation platform (AGPL-3.0) | Stack: Ruby on Rails | Stars/users: ~1.6k GitHub stars (README page); API: 1,554 | Last update: 2026-10-22 (GitHub API pushed_at)
- F1 = no: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F2 = not documented: https://github.com/consuldemocracy/consuldemocracy
- F3 = not documented: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F4 = not documented: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F5 = partial: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F6 = partial: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F7 = not documented: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F8 = not documented: https://docs.consuldemocracy.org/docs_general/participation-processes/voting
- F9 = yes: https://github.com/consuldemocracy/consuldemocracy
- Notes: Voting module 'only includes closed answers', results aggregated, voting limited to verified users; poll-officer recount compared with platform-recorded votes. Ranked ballots not mentioned (F1 'no' = module documented as closed-answer only). Multitenancy not mentioned in README.

### 23. deOpty/flexyvotes (Django election + paid-voting platform)
- Page: https://github.com/deOpty/flexyvotes
- Type: student/hobby-scale open repo (single developer, created 2026-08-10) - NEAREST MATCH FOUND | Stack: Python 3.12 / Django 6.0, PostgreSQL 16, Redis, Celery | Stars/users: 0 stars, 0 forks (53 commits per README page) | Last update: 2026-10-23 (latest commit; created 2026-08-10)
- F1 = yes: https://raw.githubusercontent.com/deOpty/flexyvotes/main/elections/tally.py
- F2 = yes: https://github.com/deOpty/flexyvotes
- F3 = yes: https://raw.githubusercontent.com/deOpty/flexyvotes/main/docs/DATABASE.md
- F4 = partial: https://raw.githubusercontent.com/deOpty/flexyvotes/main/docs/DATABASE.md
- F5 = partial: https://raw.githubusercontent.com/deOpty/flexyvotes/main/core/audit.py
- F6 = yes: https://raw.githubusercontent.com/deOpty/flexyvotes/main/core/otp.py
- F7 = no: https://github.com/deOpty/flexyvotes
- F8 = yes: https://github.com/deOpty/flexyvotes
- F9 = partial: https://github.com/deOpty/flexyvotes
- Notes: I read README plus docs/DATABASE.md, docs/TESTING.md, core/audit.py, core/otp.py, core/crypto.py, elections/tally.py. F1: README 'ranked (IRV for 1 seat, STV for several)'; tally.py builds a per-round list (round number, tallies, exhausted, eliminated, surplus) stored in the result - UI display of rounds not verified. F2: 'Multi-tenant organizations', per-organization audit chain, roles scoped to org/election. F3: DATABASE.md: partial unique index one_consumed_authorization_per_voter, unique token_hash, unique (chain,seq), voter-id uniqueness, plus PL/pgSQL BEFORE UPDATE/DELETE append-only trigger on core_auditevent and elections_ballot that 'raises insufficient_privilege, even from pgAdmin or a raw SQL session'. CHECK constraints not mentioned; a direct-SQL double-vote test is not documented, but mechanisms are strong. F4: elections_ballot has 'No voter FK, no token, no timestamp'; ballots sealed with per-election X25519 keys (optional k-of-n trustees); but voters, emails (encrypted columns + HMAC blind index) live in the SAME PostgreSQL database - no separate store. F5: audit log is a per-organisation SHA-256 linked list (core/audit.py uses plain sha256_hex, not HMAC), in PostgreSQL (not a separate document store), 'verified every 6 hours'; no cross-store reconciliation sweep of ballots/receipts/voter flags/candidates found; 204 tests incl. tamper, race, trigger tests but no published attack results table; Merkle-tree bulletin board and Ed25519-signed results/config snapshots are extra. F6: core/otp.py stores keyed-HMAC code hash (OTPChallenge: code_hash, attempts/max_attempts, expires_at, consumed_at), per-hour issue rate limit, constant-time compare; README lists email OTP, SMS OTP, SSO, LDAP, TOTP, passkeys. F7: README mentions QR only for the carried-over event ticketing check-in, not voting. F8: 'Ballot tracker per voter' + Merkle bulletin board inclusion proofs + offline verifier tools/verify_election.py (stronger than a plain receipt). F9: docker compose up --build documented; no LICENSE file (raw URL 404) and README shows none, so licence = not documented; deployment docs target AWS, no free-hosting claim. Project also bundles paid voting (Paystack), billing, fraud scoring - much larger scope than PolyVote.

### 24. nnnnnndev/voting-app (FastAPI, faculty-meeting voting)
- Page: https://github.com/nnnnnndev/voting-app
- Type: student/hobby repo (departmental tool) | Stack: Python / FastAPI; local JSON storage (SharePoint planned); MIT | Stars/users: 0 stars | Last update: 2026-05-19 (pushed_at)
- F1 = partial: https://github.com/nnnnnndev/voting-app
- F2 = no: https://github.com/nnnnnndev/voting-app
- F3 = not documented: https://github.com/nnnnnndev/voting-app
- F4 = partial: https://github.com/nnnnnndev/voting-app
- F5 = not documented: https://github.com/nnnnnndev/voting-app
- F6 = not documented: https://github.com/nnnnnndev/voting-app
- F7 = not documented: https://github.com/nnnnnndev/voting-app
- F8 = partial: https://github.com/nnnnnndev/voting-app
- F9 = partial: https://github.com/nnnnnndev/voting-app
- Notes: README: 'instant-runoff ranked-choice with sequential multi-seat IRV' (no round transcript mentioned); built for one department (others told to fork); 'two-store separation between voter receipts and ballot contents' and a voter-receipt HMAC in app/anonymity.py (but storage is local JSON, not a relational DB); sign-in through Microsoft Entra ID with a dev bypass flag; MIT; run needs venv + pip + .env + uvicorn.

### 25. 9022574361/Online_Voting_System ('VeriVote')
- Page: https://github.com/9022574361/Online_Voting_System
- Type: student/hobby repo | Stack: Node.js/Express + React (Vite); MongoDB | Stars/users: 0 stars | Last update: 2026-09-26 (pushed_at)
- F1 = not documented: https://github.com/9022574361/Online_Voting_System
- F2 = not documented: https://github.com/9022574361/Online_Voting_System
- F3 = partial: https://github.com/9022574361/Online_Voting_System
- F4 = partial: https://github.com/9022574361/Online_Voting_System
- F5 = partial: https://github.com/9022574361/Online_Voting_System
- F6 = partial: https://github.com/9022574361/Online_Voting_System
- F7 = not documented: https://github.com/9022574361/Online_Voting_System
- F8 = yes: https://github.com/9022574361/Online_Voting_System
- F9 = partial: https://github.com/9022574361/Online_Voting_System
- Notes: README: votes stored in a VoteBlock collection 'without voter identity'; SHA-256 chain currentHash = SHA256(index+electionId+candidateId+timestamp+previousHash) in MongoDB (no HMAC key); 'Run Chain Audit' endpoint checks the whole chain; 'Simulate Tamper' demo button (manual, no automated attack suite); one-vote via hasVoted map + unique constraints (no triggers/CHECK/FK); OTP via Nodemailer with route rate limits (hashing/expiry/attempt caps not documented); receipt SHA-256 hash verifiable at GET /api/votes/receipt/:hash; two terminals to run; no licence; 'Built for Academic Evaluation & Security Demonstration'. Closest repo to the MongoDB-hash-chain idea of F5.

### 26. DikshantMaskare/securevote-online-voting-system
- Page: https://github.com/DikshantMaskare/securevote-online-voting-system
- Type: student/hobby repo | Stack: Python 3.12 / Flask / SQLite / Jinja2 | Stars/users: 0 stars | Last update: 2026-09-05 (pushed_at)
- F1 = not documented: https://github.com/DikshantMaskare/securevote-online-voting-system
- F2 = no: https://github.com/DikshantMaskare/securevote-online-voting-system
- F3 = not documented: https://github.com/DikshantMaskare/securevote-online-voting-system
- F4 = not documented: https://github.com/DikshantMaskare/securevote-online-voting-system
- F5 = partial: https://github.com/DikshantMaskare/securevote-online-voting-system
- F6 = yes: https://github.com/DikshantMaskare/securevote-online-voting-system
- F7 = not documented: https://github.com/DikshantMaskare/securevote-online-voting-system
- F8 = not documented: https://github.com/DikshantMaskare/securevote-online-voting-system
- F9 = partial: https://github.com/DikshantMaskare/securevote-online-voting-system
- Notes: README: 'Hashed OTP storage with expiry, resend cooldown, and attempt limits' (F6 yes); 'hash-linked vote ledger with startup integrity validation' (no HMAC, MongoDB, sweep or attack suite documented); design 'intentionally limited to one application instance' (F2 no); 'A voter hash and encrypted ballot are written to a hash-linked block' (suggests voter linkage, F4 not documented); Dockerfile for Railway (hosting documented, free tier not stated); unittest suite without detail; licence not shown.

### 27. RuchikaaVerma/SentinelVote-AI
- Page: https://github.com/RuchikaaVerma/SentinelVote-AI
- Type: student/hobby repo | Stack: Python backend + HTML/JS; MongoDB | Stars/users: 0 stars | Last update: 2026-03-20 (pushed_at)
- F1 = not documented: https://github.com/RuchikaaVerma/SentinelVote-AI
- F2 = not documented: https://github.com/RuchikaaVerma/SentinelVote-AI
- F3 = partial: https://github.com/RuchikaaVerma/SentinelVote-AI
- F4 = no: https://github.com/RuchikaaVerma/SentinelVote-AI
- F5 = partial: https://github.com/RuchikaaVerma/SentinelVote-AI
- F6 = not documented: https://github.com/RuchikaaVerma/SentinelVote-AI
- F7 = not documented: https://github.com/RuchikaaVerma/SentinelVote-AI
- F8 = not documented: https://github.com/RuchikaaVerma/SentinelVote-AI
- F9 = partial: https://github.com/RuchikaaVerma/SentinelVote-AI
- Notes: README: 'Double vote prevention ... enforced at DB level' (constraint type not named); one MongoDB with users/votes/audit_chain/sessions and votes keyed by user_id (so ballots ARE linked to voters, F4 no); SHA-256 chain with previous block hash in audit_chain (no HMAC/sweep/attack suite); face recognition and behavioural biometrics instead of email OTP; docker compose optional; licence not shown.

### 28. d-kanishka/Secure_Voting_System
- Page: https://github.com/d-kanishka/Secure_Voting_System
- Type: student/hobby repo | Stack: Python (Flask) + React; MIT | Stars/users: 0 stars | Last update: 2026-01-30 (pushed_at)
- F1 = no: https://github.com/d-kanishka/Secure_Voting_System
- F2 = not documented: https://github.com/d-kanishka/Secure_Voting_System
- F3 = no: https://github.com/d-kanishka/Secure_Voting_System
- F4 = no: https://github.com/d-kanishka/Secure_Voting_System
- F5 = not documented: https://github.com/d-kanishka/Secure_Voting_System
- F6 = no: https://github.com/d-kanishka/Secure_Voting_System
- F7 = no: https://github.com/d-kanishka/Secure_Voting_System
- F8 = not documented: https://github.com/d-kanishka/Secure_Voting_System
- F9 = partial: https://github.com/d-kanishka/Secure_Voting_System
- Notes: README: per-candidate tally only (no ranking), TOTP second factor (email only for password reset), one-time token bound to user and election, 'has_voted' application logic rather than DB constraints, 'audit logging' without hash chain, QR only for TOTP provisioning, MIT licence, multi-step run. 'No' values reflect what the README states or implies; items README is silent on are marked no only where it names a different mechanism.

### 29. Prakhar-Pandey20/Online-Voting-System-otp-version
- Page: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- Type: student/hobby repo | Stack: Python / Django (email OTP 2FA) | Stars/users: 0 stars | Last update: 2026-06-05 (pushed_at)
- F1 = not documented: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F2 = not documented: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F3 = partial: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F4 = no: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F5 = not documented: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F6 = partial: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F7 = not documented: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F8 = not documented: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- F9 = not documented: https://github.com/Prakhar-Pandey20/Online-Voting-System-otp-version
- Notes: README: unique email + ForeignKey constraints (Django ORM), Votes table has a ForeignKey to the Voter (so ballots are linked, F4 no), email OTP stored as plain string field with a request counter (hashing/expiry not documented), blockchain mirroring only as a future idea, multi-step setup, no licence shown.

### 30. jevk/RCVElectionSystem
- Page: https://github.com/jevk/RCVElectionSystem
- Type: student/hobby repo (gaming community) | Stack: Python/Flask + Waitress; HTML/JS | Stars/users: 0 stars | Last update: 2026-06-15 (pushed_at)
- F1 = partial: https://github.com/jevk/RCVElectionSystem
- F2 = not documented: https://github.com/jevk/RCVElectionSystem
- F3 = not documented: https://github.com/jevk/RCVElectionSystem
- F4 = not documented: https://github.com/jevk/RCVElectionSystem
- F5 = not documented: https://github.com/jevk/RCVElectionSystem
- F6 = not documented: https://github.com/jevk/RCVElectionSystem
- F7 = not documented: https://github.com/jevk/RCVElectionSystem
- F8 = not documented: https://github.com/jevk/RCVElectionSystem
- F9 = partial: https://github.com/jevk/RCVElectionSystem
- Notes: README: implements instant-runoff voting with candidates eliminated in rounds and votes redistributed (no transcript mentioned); no database, configured via settings.json; run via application.py/waitress; no licence shown.

### 31. dryairship/online-election-manager
- Page: https://github.com/dryairship/online-election-manager
- Type: student project (IIT Kanpur course ESC101A) | Stack: Go (gin) + MongoDB; client-side crypto (SJCL per topics); MIT | Stars/users: 20 stars | Last update: 2021-07-26 (pushed_at)
- F1 = not documented: https://github.com/dryairship/online-election-manager
- F2 = not documented: https://github.com/dryairship/online-election-manager
- F3 = not documented: https://github.com/dryairship/online-election-manager
- F4 = not documented: https://github.com/dryairship/online-election-manager
- F5 = not documented: https://github.com/dryairship/online-election-manager
- F6 = partial: https://github.com/dryairship/online-election-manager
- F7 = not documented: https://github.com/dryairship/online-election-manager
- F8 = not documented: https://github.com/dryairship/online-election-manager
- F9 = partial: https://github.com/dryairship/online-election-manager
- Notes: README: 'cryptographically secure portal', voters/ceo collections, 'Send authcodes to all the voters (TODO: Add details)'; docker-compose deployment; MIT. Algorithms not named in README body. Inactive since 2021.

### 32. Dharanibalan45/Online-Voting-Platform
- Page: https://github.com/Dharanibalan45/Online-Voting-Platform
- Type: student/hobby repo | Stack: TypeScript/Node/Express/React + MongoDB | Stars/users: 0 stars | Last update: 2026-10-15 (pushed_at)
- F1 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F2 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F3 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F4 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F5 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F6 = partial: https://github.com/Dharanibalan45/Online-Voting-Platform
- F7 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F8 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- F9 = not documented: https://github.com/Dharanibalan45/Online-Voting-Platform
- Notes: README: 6-digit email OTP, 2-minute expiry, resend, attempt limiting (hashing not documented); duplicate-vote prevention listed without mechanism; AuditLogs mentioned without hash chaining; multi-step run; no licence shown.

### 33. Lervez5/Kuraone
- Page: https://github.com/Lervez5/Kuraone
- Type: student/hobby-scale repo (proprietary notice) | Stack: Django + React/Vite, MySQL | Stars/users: 1 star | Last update: 2026-05-09 (pushed_at)
- F1 = not documented: https://github.com/Lervez5/Kuraone
- F2 = not documented: https://github.com/Lervez5/Kuraone
- F3 = not documented: https://github.com/Lervez5/Kuraone
- F4 = not documented: https://github.com/Lervez5/Kuraone
- F5 = partial: https://github.com/Lervez5/Kuraone
- F6 = not documented: https://github.com/Lervez5/Kuraone
- F7 = not documented: https://github.com/Lervez5/Kuraone
- F8 = not documented: https://github.com/Lervez5/Kuraone
- F9 = no: https://github.com/Lervez5/Kuraone
- Notes: README: 'hash-chained audit log for tamper detection' (no HMAC, sweep or attack suite documented); 'make start' one command to build/start/migrate/seed; footer says 'All rights reserved. Private and Confidential' so not open source.
