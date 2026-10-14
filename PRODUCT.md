# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Voters:** students on a university roster (registration numbers like `25BCE0001`). They cast one ranked ballot per election, on their own phones anywhere on campus or on laptops, usually once and in a hurry. They come back only to check a receipt.
- **Election officers (admins):** student-council or society officers who create an election, load candidates and the roster, open and close voting, then audit and announce the result. They work at laptops.
- **Audiences in a room:** results, the integrity sweep and the tamper demonstration are projected for a room (results announcements, project reviews).
- **Course evaluators:** PolyVote is also a DBMS course project. Graders watch the tamper-and-detect story live and must understand it within minutes.

## Product Purpose

Run small-organisation elections with ranked-choice (instant-runoff) ballots, where tampering with the stored votes is detectable. Success: a student can vote in under a minute on a phone; an officer can run an election end to end without help; anyone watching the audit can see whether the database still matches what voters cast.

## Positioning

Every ballot is sealed into a hash-chained receipt ledger kept apart from the relational database. The integrity sweep recomputes ballots from the database and compares them with the sealed receipts, so a database administrator who edits or deletes votes is caught. Voters keep a receipt token and can check it themselves.

## Operating Context

- Lifecycle per election: Nominations → Voting → Closed. Candidates are locked once voting opens.
- Voter flow: choose election → sign in with registration number and password → rank top 3 → confirm → receipt token → optional receipt check at `/verify`.
- Officer flow: create election → candidates (manual or demo seed) → roster (manual or bulk `25BCE####` with password `vote123`) → open voting → optional ballot simulation → close → integrity sweep → instant-runoff tally (round by round) → announce.
- "DB Studio" deliberately simulates a rogue DBA editing tables, to demonstrate the sweep.
- Multi-tenant: several organisations' elections live side by side under one set of administrators.

## Capabilities and Constraints

- Ranked ballots are exactly top-3 (fewer only when an election has fewer than 3 candidates); schema enforces ranks 1–3.
- Auth is local: default admin `admin` / `admin123`; sessions live in server memory.
- Stack: React + TypeScript (Vite) frontend in `frontend/`, FastAPI in `server.py`, SQLite + JSON ledger. The original Streamlit UI (`app.py`) still exists.
- Known, deliberately unfixed audit gaps (user decision, 2026-10-15): the sweep does not flag ballots inserted without a receipt, and candidate names are outside the seal. The UI surfaces count mismatches but must not claim more than the sweep proves.
- Ballots are not encrypted; copy must not say they are.

## Brand Commitments

- The name is **PolyVote**. No other binding brand assets.
- **Standing preference (chosen 2026-10-15):** the category standard, played straight. PolyVote should sit alongside **Vercel** and **GitHub** and meet their craft level: familiar product UI, no novelty world or quirk.

## Evidence on Hand

- Demo data only: seeded candidates (Arun Kumar, Bhavya Singh, Chaitanya Reddy, Diya Sharma, Eshaan Iyer) and simulated ballots. No real elections, users, testimonials, or institutional endorsements exist; do not invent any.

## Product Principles

1. Casting a vote is the one job that must never feel uncertain: every step says where you are and what happens next.
2. Show proof, not reassurance: integrity claims are always backed by a visible check the viewer can run.
3. Honest about limits: never claim encryption, certification, or detection the system does not perform.
4. Readable across a room: results and audits must survive a projector as well as a phone screen.
5. Officers move fast: lifecycle actions are obvious and guarded, and routine setup takes seconds.

## Accessibility & Inclusion

Voters use their own phones in varied light, and results are projected: keep WCAG AA contrast, large touch targets, full keyboard operation, and no meaning carried by colour alone.
