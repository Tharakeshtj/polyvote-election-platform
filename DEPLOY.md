# Deploying PolyVote for free (permanent links)

Two services from the same GitHub repo, both on Render's free plan (Docker). `render.yaml` describes both.

| Service | URL form | Purpose | One-time code |
|---|---|---|---|
| `polyvote-demo` | `https://polyvote-demo.onrender.com` | Public demo for evaluators; `/demo` is a guide to every page | Shown on screen ("Demo mode"), no mailbox needed |
| `polyvote-live` | `https://polyvote-live.onrender.com` | Real emailed codes | Sent by email through an SMTP relay on port 2525 |

Render's free plan blocks outbound SMTP ports 25, 465 and 587, so Gmail's own SMTP cannot be used there. A relay that accepts port 2525 (Brevo, Mailgun, SendGrid) works with no code change because the app reads `SMTP_HOST` and `SMTP_PORT` from the environment.

## Deploy both (about 15 minutes)
1. Push this repo to GitHub (`main`).
2. render.com, sign up with GitHub.
3. **New, Blueprint**, pick this repo. Render reads `render.yaml` and proposes both services. Rename them if the URL name is taken.
4. Fill the prompted variables (they stay in Render, never in the repo):
   - `polyvote-demo`: `ADMIN_PASSWORD` optional. Leave empty to show `admin / admin123` in the guide, or set one to keep the admin console private.
   - `polyvote-live`: `ADMIN_PASSWORD` (set one), `DEMO_EMAIL` (your Gmail), and the three Brevo values below.
5. **Apply**. Each build takes 5 to 10 minutes. Open the URLs when they say Live.

## Brevo setup for real email (free, about 10 minutes)
1. brevo.com, create a free account and verify your email.
2. Senders and domains: add and verify your Gmail as a single sender (Brevo sends a link).
3. SMTP and API, then SMTP: copy your **login** (looks like `xxxx@smtp-brevo.com`) and create an **SMTP key**.
4. In Render, `polyvote-live`, Environment:
   - `SMTP_USER` = the Brevo login
   - `SMTP_PASS` = the SMTP key (not your Brevo password)
   - `SMTP_FROM` = the verified sender (your Gmail)
   - `DEMO_EMAIL` = your Gmail (codes go to `you+25bce0001@gmail.com` and so on, all arriving in your inbox)
5. Open `polyvote-live`, sign in as `25BCE0019` / `vote123`: the code arrives by email. In Admin, Mail outbox, the Delivery column should say `sent`. If it says `failed: ...`, the relay settings are wrong or the sender is not verified.

Mail from a free relay with a gmail.com sender can land in Spam; mention that to anyone testing.

## Limits of the free plan
- Sleeps after about 15 minutes idle; the next visit takes about a minute to wake.
- The disk is wiped on restart, so each start creates the demo election again (this is why `HOSTED_DEMO=true`).
- The hosted copies use the local file ledger, not MongoDB Atlas: with Atlas connected, every restart would clear the ledger collection. The Atlas version runs on your own machine.
- Factory reset is disabled on hosted demos.
- Anyone who can open the demo can cast votes and, if admin is public, edit data; it resets on restart.
