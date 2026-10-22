# PolyVote

Ranked-choice (instant-runoff) elections with a hash-chained audit ledger that detects tampering in the relational database.

## Layout

| Path | What it is |
|---|---|
| `server.py` | FastAPI backend for the React app (`/api/...`); also serves the built frontend |
| `frontend/` | React + TypeScript + Vite frontend (voter booth + admin console) |
| `app.py` | Original Streamlit UI (still works, shares the same DB and ledger) |
| `election_core.py` | DB helpers shared by `app.py` and `server.py` (connection, hashing, integrity sweep, reset) |
| `audit_ledger.py` | Hash-chained receipt ledger (`mongo_audit_ledger.json`) |
| `tally_engine.py` | Instant-runoff tally |
| `setup_db.py` | Schema, trigger and views (run automatically by `server.py`) |

## Run the React app

Requires Python 3.12+ and Node.js 20+.

```bash
pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
python -m uvicorn server:app --port 8000
```

Open http://localhost:8000.

### Frontend development (hot reload)

Run the API (`python -m uvicorn server:app --port 8000 --reload`) in one terminal and `npm run dev` inside `frontend/` in another, then open http://localhost:5173. Vite proxies `/api` to port 8000.

## Local demo credentials

| Who | Login |
|---|---|
| Administrator | `admin` / `admin123` (created on first start) |
| Bulk-registered voters | `25BCE0001`, `25BCE0002`, ... / `vote123` |

Sessions are kept in server memory, so restarting the server signs everyone out.

## Demo walkthrough

1. **Admin → Elections → New election**, then **Candidates → Seed demo candidates** and **Voters → Register**.
2. **Open voting** (top right of the election page).
3. Vote as a student at http://localhost:8000/vote, and keep the receipt token. Or use **Overview → Simulate ballots**.
4. **DB Studio**: reassign or delete some ballots (this simulates a rogue DBA).
5. **Results & audit → Run sweep** flags the tampered ballots; **Calculate winner** shows the round-by-round tally.
6. **/verify** with the receipt token shows whether that ballot is still counted.

## Email one-time code (second factor)

Set `OTP_REQUIRED=true` in `.env` and a correct password is no longer enough: a 6-digit code is emailed to the voter's address (valid 5 minutes, one use, 3 guesses). Add voter emails on the **Voters** tab, and every code also appears under **Admin, Mail outbox**. For real email set `SMTP_USER` and `SMTP_PASS` (a Gmail App Password). Copy `.env.example` to `.env` for all settings. The `Sample PolyVote` demo copy and `DEMO_SCRIPT.md` show a ready class demo.

## Public demo link and guide

`Dockerfile` and `render.yaml` deploy a free public demo (HOSTED_DEMO seeds a demo election on every start; the one-time code is shown on screen because a public demo has no mailbox). The `/demo` page lists every page of the app with links and a three-minute tour. `DEPLOY.md` explains the free hosting steps and an optional real-email instance. The hosted demo link is listed in `docs/DEMO_WALKTHROUGH.md`.

## Tests and evidence

`python experiments/run_experiments.py <tag>` runs 47 scenarios (database rules, API abuse, tampering, one-time-code tests) plus benchmarks on a throwaway copy, and `python experiments/summarize.py` builds the tables and charts used in `docs/PolyVote_Review_III.docx`.

## Design system

The frontend follows a written design system:

- `DESIGN.md`: the visual system (Vercel neutrals, GitHub Primer state colours, Geist type). Read it before changing UI.

## Streamlit UI (original)

```bash
python setup_db.py
streamlit run app.py
```
