"""Contact form: validated, rate-limited, stored in the verification database file (never with ballots)."""
import re
import sqlite3
import threading
import time
from collections import defaultdict, deque

from verification import otp

_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_hits: dict[str, deque] = defaultdict(deque)
_lock = threading.Lock()
LIMIT, WINDOW = 5, 3600          # five messages per visitor per hour


class ContactError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


def init():
    c = sqlite3.connect(otp.DB_FILE)
    c.execute('''CREATE TABLE IF NOT EXISTS CONTACT_MESSAGE (
                 message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 received_at REAL NOT NULL,
                 name TEXT NOT NULL,
                 email TEXT NOT NULL,
                 message TEXT NOT NULL)''')
    c.commit()
    c.close()


def submit(visitor: str, name: str, email: str, message: str, honeypot: str = '') -> bool:
    if honeypot:                     # bots fill hidden fields; pretend success and store nothing
        return True
    name, email, message = name.strip(), email.strip(), message.strip()
    if not (1 <= len(name) <= 100):
        raise ContactError(422, 'Please enter your name (up to 100 characters).')
    if not _EMAIL.match(email) or len(email) > 254:
        raise ContactError(422, 'Please enter a valid email address.')
    if not (10 <= len(message) <= 2000):
        raise ContactError(422, 'Your message should be between 10 and 2000 characters.')
    now = time.time()
    with _lock:
        q = _hits[visitor]
        while q and q[0] < now - WINDOW:
            q.popleft()
        if len(q) >= LIMIT:
            raise ContactError(429, 'Too many messages from this connection. Please try again later.')
        q.append(now)
    c = sqlite3.connect(otp.DB_FILE)
    c.execute('INSERT INTO CONTACT_MESSAGE (received_at, name, email, message) VALUES (?,?,?,?)', (now, name, email, message))
    c.commit()
    c.close()
    return True


def recent(limit: int = 100) -> list[dict]:
    c = sqlite3.connect(otp.DB_FILE)
    c.row_factory = sqlite3.Row
    rows = [dict(r) for r in c.execute('SELECT message_id, received_at, name, email, message FROM CONTACT_MESSAGE ORDER BY message_id DESC LIMIT ?', (limit,))]
    c.close()
    return rows
