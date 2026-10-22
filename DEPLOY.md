# Deploying PolyVote for free (permanent link)

`render.yaml` deploys the public demo on Render's free plan, built from the `Dockerfile`:

**https://polyvote-bacse202.onrender.com** (appears once the service is created; the first visit after idle takes about a minute)

## Deploy the public demo (about 10 minutes, browser only)
1. Sign in at render.com with GitHub.
2. **New, Blueprint**, choose `Tharakeshtj/polyvote-election-platform`, branch `main`. Render reads `render.yaml` and proposes one service, `polyvote-bacse202`.
3. **Apply**. The first build takes 5 to 10 minutes. When it says **Live**, open the link above and click **Demo guide**.

No secrets are needed: in demo mode the one-time code is shown on the screen, factory reset is disabled, and the admin console uses `admin` / `admin123` (set an `ADMIN_PASSWORD` environment variable in Render to keep it private).

## Optional: a second instance with real emailed codes
Render's free plan blocks outbound SMTP ports 25, 465 and 587, so Gmail's own SMTP cannot be used there. A relay that accepts port 2525 (Brevo, Mailgun, SendGrid) works with no code change because the app reads `SMTP_HOST` and `SMTP_PORT` from the environment. `render-live.example.yaml` has the service block.

1. brevo.com, create a free account and verify your email.
2. Senders and domains: add and verify your Gmail as a single sender (Brevo sends a link).
3. SMTP and API, then SMTP: copy your **login** (looks like `xxxx@smtp-brevo.com`) and create an **SMTP key**.
4. Add the service block from `render-live.example.yaml` to `render.yaml`, push, and in Render fill: `SMTP_USER` (Brevo login), `SMTP_PASS` (SMTP key, not your Brevo password), `SMTP_FROM` (the verified sender), `DEMO_EMAIL` (your Gmail; codes go to `you+25bce0001@gmail.com` and so on) and `ADMIN_PASSWORD`.
5. Open the live URL and sign in as `25BCE0019` / `vote123`; the code arrives by email. In Admin, Mail outbox, the Delivery column should say `sent`; if it says `failed: ...`, the relay settings are wrong or the sender is not verified. Mail from a free relay with a gmail.com sender can land in Spam.

## Limits of the free plan
- Sleeps after about 15 minutes idle; the next visit takes about a minute to wake.
- The disk is wiped on restart, so each start creates the demo election again (this is why `HOSTED_DEMO=true`).
- The hosted copies use the local file ledger, not MongoDB Atlas: with Atlas connected, every restart would clear the ledger collection. The Atlas version runs on your own machine.
- Factory reset is disabled on hosted demos. Anyone who opens the demo can vote; it resets on restart.
