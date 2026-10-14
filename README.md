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

## Design system

The frontend follows [Impeccable](https://impeccable.style/) (installed as a project skill in `.claude/skills/impeccable`, without its engine binary or hooks):

- `PRODUCT.md`: users, purpose and principles.
- `DESIGN.md` + `.impeccable/design.json`: the visual system (Vercel neutrals, GitHub Primer state colours, Geist type). Read these before changing UI.
- `.impeccable/briefs/app.md`: the direction contract the build was reviewed against.

## Streamlit UI (original)

```bash
python setup_db.py
streamlit run app.py
```
