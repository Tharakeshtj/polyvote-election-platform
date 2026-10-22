# PolyVote: links, demo run-through and workflow

## Links
- **Public demo (free hosting):** https://polyvote-bacse202.onrender.com  (deploy steps in `DEPLOY.md`; the first visit after idle takes about a minute)
- **Source code:** https://github.com/Tharakeshtj/polyvote-election-platform
- **Guide to every page:** `/demo` on the app

## Workflow of one election
1. Officer creates the election (Admin, New election).
2. Adds candidates (only before voting opens).
3. Registers voters and their email addresses (Election, Voters).
4. Opens voting (Election, Overview).
5. Voter opens the vote page or scans the QR code and signs in with registration number and password.
6. The voter enters the 6-digit code received by email (demo: shown on screen).
7. The voter ranks three candidates, reviews, casts and keeps the receipt token.
8. Anyone checks the receipt (sealed in the ledger and counted).
9. Officer closes voting, runs the integrity sweep and counts the ballots.
10. Tamper test: edit or delete a ballot in DB Studio and run the sweep again.

## Three-minute tour of the public demo
1. Open the link. A "Demo mode" banner shows; click **Demo guide** to see every page.
2. **Vote**: sign in as `25BCE0025` / `vote123` (voters `25BCE0019` to `25BCE0030` have not voted).
3. Read the 6-digit code from the blue "Demo mode" box, enter it, rank three candidates, review, cast. Copy the receipt token.
4. **Check receipt**: paste the token; it is sealed and counted.
5. **Admin** (`admin` / `admin123` on the public demo): Election 1, **Results**, run the sweep (passes).
6. **DB Studio**: delete a ballot, run the sweep again: the deleted ballot is named. **Audit ledger**: chain intact. **Mail outbox**: every code issued.

## Class demo with real emailed codes (Sample PolyVote, on your laptop)
1. Double-click `Sample PolyVote\START_DEMO.bat -NoSeed` (once: `SET_GMAIL.bat` to connect a Gmail App Password).
2. New election, five candidates, bulk-register five voters, fill their emails (four default, one different), open voting.
3. Add two more voters by hand, each with their own email address.
4. Ballot simulation for the first four voters; vote for the other three from a phone by scanning the QR code. Each receives their own code by email.
5. Close, run the sweep and the count; edit one block in MongoDB Atlas and reload the Audit ledger to show the red "tampered" banner.
