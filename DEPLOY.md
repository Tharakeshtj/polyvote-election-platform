# Deploying the PolyVote demo (free, permanent link)

The public demo is the **same code as the project**, built from the `Dockerfile` and run on Render's free plan:

**https://polyvote-bacse202.onrender.com** (the first visit after idle takes about a minute)

Only the environment settings differ (see `render.yaml`). Data is separate: whatever visitors do on the demo stays on the demo,
and nothing there reaches the project, its database or its ledger.

## 1. Create the service (about 10 minutes, browser only)
1. Sign in at render.com with GitHub.
2. **New, Blueprint**, choose `Tharakeshtj/polyvote-election-platform`, branch `main`. Render reads `render.yaml` and proposes one service, `polyvote-bacse202`.
3. **Apply**. The first build takes 5 to 10 minutes. When it says **Live**, open the link above and click **Demo guide**.

Without any secrets the demo already works: sample election, the one-time code shown on screen, admin login `admin` / `admin123`
(set `ADMIN_PASSWORD` to keep it private). The admin **Settings, Factory reset** restores the sample election.

## 2. Keep the demo in step with the project
`autoDeploy: true` in `render.yaml` redeploys on every push to `main`. If the service was created by hand instead of from the
Blueprint, open the service in Render, **Settings, Build & Deploy, Auto-Deploy: On Commit**.

## 3. Real emailed codes on the demo
Render's free plan blocks outbound SMTP ports 25, 465 and 587, so Gmail's own SMTP cannot be used there. A relay that accepts
port 2525 (Brevo, Mailgun, SendGrid) works, because the app reads `SMTP_HOST` and `SMTP_PORT` from the environment.

1. brevo.com, create a free account and verify your email.
2. Senders and domains: add and verify your Gmail as a single sender (Brevo sends a link).
3. SMTP and API, then SMTP: copy your **login** (looks like `xxxx@smtp-brevo.com`) and create an **SMTP key**.
4. In Render, the service, **Environment**: set `SMTP_USER` (Brevo login), `SMTP_PASS` (the SMTP key, not your Brevo password),
   `SMTP_FROM` (the verified sender) and optionally `DEMO_EMAIL` (your Gmail; seeded voters' codes go to `you+25bce0001@gmail.com` and so on).
5. Save. Open the live link and sign in as a voter; the code is emailed and is also shown on screen. In Admin, **Mail outbox**,
   the Delivery column says `sent`; `failed: ...` means the relay settings or the sender are wrong. Mail from a free relay with a
   gmail.com sender can land in Spam.

Because the admin console on the demo is open to anyone, real email is limited: at most `OTP_DAILY_EMAIL_CAP` (100) emails a day
and 6 per address per hour. Over the limit the code is still shown on screen; the Mail outbox says `skipped`.

## 4. The same ledger as the project (MongoDB Atlas, keyed chain)
In the service's **Environment**: `MONGO_URI` (your Atlas connection string), `MONGO_DB=polyvote_demo` (already in `render.yaml`;
a separate database, so a demo restart only clears `polyvote_demo.ledger` and never your project's ledger) and `LEDGER_KEY`
(a new secret, not the project's). In Atlas, **Network Access** must allow Render (add `0.0.0.0/0` for a student project). The
health check at `/api/health` then shows `mongodb` and `hmac-sha256`.

## Limits of the free plan
- Sleeps after about 15 minutes idle; the next visit takes about a minute to wake.
- The disk is wiped on restart, so each start creates the sample election again (this is why `HOSTED_DEMO=true`).
- Everyone who opens the demo shares the same data until it restarts or an officer uses Factory reset.
