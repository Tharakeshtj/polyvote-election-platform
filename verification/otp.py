"""Email one-time-password second factor for voter sign-in.

Kept apart from the election schema: contacts, challenges and the mail log live in their own
SQLite file, so a voter's email address is never stored next to a ballot. Codes are random,
stored only as a keyed hash, expire quickly, allow few guesses and work once.
"""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import threading
import time
from collections import deque
from contextlib import contextmanager
from email.message import EmailMessage

DB_FILE = 'polyvote_verification.db'
CODE_DIGITS = 6
TTL_SECONDS = 300             # a code is valid for 5 minutes
MAX_ATTEMPTS = 3              # wrong guesses per code
MAX_SENDS = 5                 # codes per challenge (so resends cannot be used to keep guessing)
RESEND_AFTER = 30             # seconds between sends
MAX_CHALLENGES = 5            # new challenges per voter per 15 minutes
CHALLENGE_WINDOW = 900
OUTBOX_VISIBLE = 600          # the plaintext code stays visible in the admin outbox for 10 minutes at most

_SECRET = (os.environ.get('OTP_SECRET') or secrets.token_hex(32)).encode()
_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_lock = threading.Lock()
# Plaintext codes are held in memory only (never in the database) so the admin can read them during a demo.
_outbox: deque = deque(maxlen=200)


class OtpError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


def required() -> bool:
    return os.environ.get('OTP_REQUIRED', '').strip().lower() in ('1', 'true', 'yes', 'on')


def smtp_settings():
    user = os.environ.get('SMTP_USER', '').strip()
    pw = os.environ.get('SMTP_PASS', '').strip()
    return {
        'host': os.environ.get('SMTP_HOST', 'smtp.gmail.com').strip(),
        'port': int(os.environ.get('SMTP_PORT', '587') or 587),
        'user': user, 'password': pw,
        'sender': os.environ.get('SMTP_FROM', '').strip() or user,
        'configured': bool(user and pw),
    }


@contextmanager
def _conn():
    # Commit even when the caller raises afterwards (e.g. a wrong-code 401 must still record the attempt), then close.
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    try:
        yield c
    finally:
        c.commit()
        c.close()


def init():
    with _conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS VOTER_CONTACT (
            election_id INTEGER NOT NULL,
            reg_no TEXT NOT NULL,
            email TEXT NOT NULL,
            PRIMARY KEY (election_id, reg_no));
        CREATE TABLE IF NOT EXISTS OTP_CHALLENGE (
            challenge_id TEXT PRIMARY KEY,
            election_id INTEGER NOT NULL,
            reg_no TEXT NOT NULL,
            code_hash TEXT NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            last_sent_at REAL NOT NULL,
            sends INTEGER NOT NULL DEFAULT 1,
            attempts INTEGER NOT NULL DEFAULT 0,
            state TEXT NOT NULL DEFAULT 'open' CHECK (state IN ('open','used','locked')));
        CREATE TABLE IF NOT EXISTS MAIL_LOG (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_at REAL NOT NULL,
            election_id INTEGER NOT NULL,
            reg_no TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT NOT NULL);
        ''')


# ------------------------------------------------------------------ contacts

def valid_email(email: str) -> bool:
    return bool(_EMAIL.match(email.strip())) and len(email) <= 254


def set_contact(election_id: int, reg_no: str, email: str):
    email = email.strip()
    if not valid_email(email):
        raise OtpError(422, "That doesn't look like a valid email address.")
    with _conn() as c:
        c.execute('INSERT INTO VOTER_CONTACT (election_id, reg_no, email) VALUES (?,?,?) '
                  'ON CONFLICT(election_id, reg_no) DO UPDATE SET email = excluded.email', (election_id, reg_no.upper(), email))


def fill_plus_addresses(election_id: int, reg_nos: list[str], base_email: str) -> int:
    """you@gmail.com -> you+25BCE0001@gmail.com for every voter (all land in one inbox: handy for demos)."""
    base_email = base_email.strip()
    if not valid_email(base_email):
        raise OtpError(422, "Enter a valid base email address.")
    local, domain = base_email.rsplit('@', 1)
    local = local.split('+', 1)[0]
    with _conn() as c:
        c.executemany('INSERT INTO VOTER_CONTACT (election_id, reg_no, email) VALUES (?,?,?) '
                      'ON CONFLICT(election_id, reg_no) DO UPDATE SET email = excluded.email',
                      [(election_id, r.upper(), f'{local}+{r.lower()}@{domain}') for r in reg_nos])
    return len(reg_nos)


def contacts(election_id: int) -> dict[str, str]:
    with _conn() as c:
        return {r['reg_no']: r['email'] for r in c.execute('SELECT reg_no, email FROM VOTER_CONTACT WHERE election_id = ?', (election_id,))}


def mask(email: str) -> str:
    local, _, domain = email.partition('@')
    return f"{local[:1]}{'*' * max(len(local) - 1, 2)}@{domain}"


# ------------------------------------------------------------------ codes

def _hash(challenge_id: str, code: str) -> str:
    return hmac.new(_SECRET, f'{challenge_id}:{code}'.encode(), hashlib.sha256).hexdigest()


def _new_code() -> str:
    return str(secrets.randbelow(10 ** CODE_DIGITS)).zfill(CODE_DIGITS)


def _deliver(election_id: int, reg_no: str, email: str, code: str):
    """Queue the outbox entry now and send in the background so the page never waits on SMTP."""
    entry = {'ts': time.time(), 'election_id': election_id, 'reg_no': reg_no, 'email': email, 'code': code,
             'expires_at': time.time() + TTL_SECONDS, 'status': 'queued'}
    _outbox.appendleft(entry)
    cfg = smtp_settings()

    def log(status):
        entry['status'] = status
        with _conn() as c:
            c.execute('INSERT INTO MAIL_LOG (sent_at, election_id, reg_no, email, status) VALUES (?,?,?,?,?)',
                      (time.time(), election_id, reg_no, email, status))

    if not cfg['configured']:
        log('outbox only (SMTP not configured)')
        return

    def run():
        import smtplib
        import ssl
        msg = EmailMessage()
        msg['Subject'] = 'Your PolyVote verification code'
        msg['From'], msg['To'] = cfg['sender'], email
        msg.set_content(f'Your PolyVote verification code is {code}.\n\nIt expires in {TTL_SECONDS // 60} minutes and works once. '
                        f'If you did not try to vote, ignore this message.')
        try:
            with smtplib.SMTP(cfg['host'], cfg['port'], timeout=20) as s:
                s.starttls(context=ssl.create_default_context())
                s.login(cfg['user'], cfg['password'])
                s.send_message(msg)
            log('sent')
        except Exception as exc:  # delivery problems must never break sign-in; the outbox still has the code
            log(f'failed: {type(exc).__name__}')

    threading.Thread(target=run, daemon=True).start()


def demo_hint() -> bool:
    """Public hosted demo only (OTP_DEMO_HINT=true): show the code on the OTP screen because evaluators have no access to the demo mailboxes.
    Off by default; with it on the second factor is not a real factor, which the screen says plainly."""
    return os.environ.get('OTP_DEMO_HINT', '').strip().lower() in ('1', 'true', 'yes', 'on')


def _demo_extra(code: str) -> dict:
    return {'demo_code': code} if demo_hint() else {}


def start(election_id: int, reg_no: str) -> dict:
    reg_no = reg_no.upper()
    email = contacts(election_id).get(reg_no)
    if not email:
        raise OtpError(409, "No email address is on file for you. Ask the election officer to add one.")
    now = time.time()
    with _lock, _conn() as c:
        recent = c.execute('SELECT COUNT(*) FROM OTP_CHALLENGE WHERE election_id=? AND reg_no=? AND created_at > ?',
                           (election_id, reg_no, now - CHALLENGE_WINDOW)).fetchone()[0]
        if recent >= MAX_CHALLENGES:
            raise OtpError(429, "Too many verification attempts. Please wait a few minutes and try again.")
        c.execute("UPDATE OTP_CHALLENGE SET state='locked' WHERE election_id=? AND reg_no=? AND state='open'", (election_id, reg_no))
        cid, code = secrets.token_urlsafe(24), _new_code()
        c.execute('INSERT INTO OTP_CHALLENGE (challenge_id, election_id, reg_no, code_hash, created_at, expires_at, last_sent_at) VALUES (?,?,?,?,?,?,?)',
                  (cid, election_id, reg_no, _hash(cid, code), now, now + TTL_SECONDS, now))
    _deliver(election_id, reg_no, email, code)
    return {'challenge': cid, 'email_hint': mask(email), 'expires_in': TTL_SECONDS, 'resend_after': RESEND_AFTER, **_demo_extra(code)}


def _open_challenge(c, challenge_id: str):
    row = c.execute('SELECT * FROM OTP_CHALLENGE WHERE challenge_id = ?', (challenge_id,)).fetchone()
    if not row or row['state'] != 'open':
        raise OtpError(410, "This verification has ended. Please sign in again.")
    if time.time() > row['expires_at']:
        c.execute("UPDATE OTP_CHALLENGE SET state='locked' WHERE challenge_id=?", (challenge_id,))
        raise OtpError(410, "That code has expired. Please sign in again for a new one.")
    return row


def verify(challenge_id: str, code: str) -> tuple[int, str]:
    code = re.sub(r'\s', '', code or '')
    with _lock, _conn() as c:
        row = _open_challenge(c, challenge_id)
        if not hmac.compare_digest(row['code_hash'], _hash(challenge_id, code)):
            attempts = row['attempts'] + 1
            locked = attempts >= MAX_ATTEMPTS
            c.execute('UPDATE OTP_CHALLENGE SET attempts=?, state=? WHERE challenge_id=?', (attempts, 'locked' if locked else 'open', challenge_id))
            if locked:
                raise OtpError(410, "Too many wrong codes. Please sign in again.")
            raise OtpError(401, f"Incorrect code. {MAX_ATTEMPTS - attempts} attempt{'s' if MAX_ATTEMPTS - attempts != 1 else ''} left.")
        c.execute("UPDATE OTP_CHALLENGE SET state='used' WHERE challenge_id=?", (challenge_id,))
        return row['election_id'], row['reg_no']


def resend(challenge_id: str) -> dict:
    now = time.time()
    with _lock, _conn() as c:
        row = _open_challenge(c, challenge_id)
        wait = RESEND_AFTER - (now - row['last_sent_at'])
        if wait > 0:
            raise OtpError(429, f"Please wait {int(wait) + 1} seconds before asking for another code.")
        if row['sends'] >= MAX_SENDS:
            raise OtpError(429, "No more codes can be sent for this sign-in. Please sign in again later.")
        email = contacts(row['election_id']).get(row['reg_no'])
        code = _new_code()
        c.execute('UPDATE OTP_CHALLENGE SET code_hash=?, last_sent_at=?, sends=sends+1, attempts=0, expires_at=? WHERE challenge_id=?',
                  (_hash(challenge_id, code), now, now + TTL_SECONDS, challenge_id))
    _deliver(row['election_id'], row['reg_no'], email, code)
    return {'email_hint': mask(email), 'expires_in': TTL_SECONDS, 'resend_after': RESEND_AFTER, **_demo_extra(code)}


# ------------------------------------------------------------------ admin views

def outbox() -> list[dict]:
    now = time.time()
    return [{
        'sent_at': e['ts'], 'election_id': e['election_id'], 'reg_no': e['reg_no'], 'email': e['email'],
        'status': e['status'], 'code': e['code'] if now < e['expires_at'] and now - e['ts'] < OUTBOX_VISIBLE else None,
        'expired': now >= e['expires_at'],
    } for e in _outbox]


def status() -> dict:
    cfg = smtp_settings()
    return {'required': required(), 'smtp_configured': cfg['configured'], 'smtp_host': cfg['host'], 'sender': cfg['sender'] or None,
            'ttl_seconds': TTL_SECONDS, 'max_attempts': MAX_ATTEMPTS}
