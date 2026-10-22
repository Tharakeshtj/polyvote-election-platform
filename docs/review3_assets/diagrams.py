"""Regenerate the Review 3 diagrams into docs/review3_assets/diagrams/ (matplotlib only).

    python docs/review3_assets/diagrams.py
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent / 'diagrams'
OUT.mkdir(exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'
INK = '#1f2328'
PAL = {
    'blue': ('#eaf3ff', '#9ec5f4'), 'green': ('#eaf7ee', '#8fd0a1'), 'orange': ('#fff3e3', '#f0b86c'),
    'violet': ('#f0ecfd', '#b8a8ee'), 'grey': ('#f4f5f6', '#b5bac0'), 'pink': ('#fdeefb', '#e2a3da'),
    'red': ('#fdecec', '#e69a9a'), 'teal': ('#e7f7f4', '#86d2c4'),
}
WHITE = dict(boxstyle='round,pad=0.15', fc='white', ec='none')


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis('off')
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def box(ax, x, y, w, h, text='', color='blue', fs=7.5, bold=False, dashed=False, align='center', lw=1.1, z=2, rounded=True):
    fc, ec = PAL[color]
    style = 'round,pad=0,rounding_size=0.8' if rounded else 'square,pad=0'
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=lw, ls=(0, (4, 2)) if dashed else 'solid', zorder=z))
    if text:
        ha = 'center' if align == 'center' else 'left'
        tx = x + w / 2 if align == 'center' else x + 1.0
        ax.text(tx, y + h / 2, text, ha=ha, va='center', fontsize=fs, color=INK, fontweight='bold' if bold else 'normal', zorder=z + 1, linespacing=1.25)


def frame(ax, x, y, w, h, label, color='#7d838c', fs=6.8):
    ax.add_patch(Rectangle((x, y), w, h, fc='none', ec=color, lw=1.0, ls=(0, (5, 3)), zorder=1))
    ax.text(x + w / 2, y + 0.9, label, fontsize=fs, color=color, va='bottom', ha='center', style='italic', zorder=1)


def arrow(ax, p, q, label=None, lpos=0.5, dy=0.0, color=INK, fs=6.6, style='-|>', dashed=False, ha='center'):
    ax.annotate('', xy=q, xytext=p, zorder=4,
                arrowprops=dict(arrowstyle=style, color=color, lw=1.0, ls=(0, (4, 2)) if dashed else 'solid', shrinkA=0, shrinkB=0))
    if label:
        ax.text(p[0] + (q[0] - p[0]) * lpos, p[1] + (q[1] - p[1]) * lpos + dy, label, fontsize=fs, ha=ha, va='center', color=color, zorder=5, bbox=WHITE)


# ======================================================================= 1. architecture
def architecture():
    fig, ax = canvas(7.2, 5.4, (0, 100), (-1, 76))
    box(ax, 4, 66, 30, 8, 'Voter browser / phone\n(scans the QR code)', 'blue')
    box(ax, 66, 66, 30, 8, 'Admin browser\n(officer console)', 'blue')
    box(ax, 24, 52, 52, 8, 'Cloudflare quick tunnel  (public HTTPS address  ->  localhost:8000)', 'grey', fs=7.2)
    arrow(ax, (19, 66), (36, 60), None)
    arrow(ax, (81, 66), (64, 60), None)
    arrow(ax, (50, 52), (50, 46.5), None)
    # app
    box(ax, 4, 28, 76, 18, '', 'violet')
    ax.text(6, 43.6, 'FastAPI service  (server.py, also serves the React build)', fontsize=7.6, fontweight='bold', va='center')
    comps = [(6.5, 'Voter and admin\nREST endpoints\n(sessions, roster,\nballot cast)', 'blue'), (25, 'Verification\nrouter (email\none-time code,\noutbox)', 'orange'),
             (43.5, 'Instant-runoff\ntally engine', 'green'), (62, 'Integrity sweep\n+ chain check', 'red')]
    for x, t, col in comps:
        box(ax, x, 30.3, 16.5, 10.5, t, col, fs=6.5)
    box(ax, 84, 31, 14, 10, 'SMTP server\n(e.g. Gmail)\none-time codes', 'grey', fs=6.4)
    arrow(ax, (80, 36), (84, 36), None)
    # stores
    stores = [(4, 'Election database', 'blue', 'SQLite  polyvote_relational.db\nORGANIZATION, ELECTION, CANDIDATE,\nVOTER_PARTICIPATION, BALLOT_RANKS,\nADMIN_USERS; trigger, CHECK,\nUNIQUE, FK, views'),
              (36, 'Verification database', 'orange', 'SQLite  polyvote_verification.db\n(a separate file)\nVOTER_CONTACT, OTP_CHALLENGE,\nMAIL_LOG\nnever joined to ballots'),
              (68, 'Audit ledger', 'green', 'MongoDB Atlas collection  ledger\nunique index on block index\nHMAC-keyed hash chain\n(JSON file fallback)')]
    for x, title, col, body in stores:
        box(ax, x, 6.5, 28, 15, '', col)
        ax.text(x + 14, 19.2, title, fontsize=7.4, fontweight='bold', ha='center')
        ax.text(x + 14, 12.3, body, fontsize=6.0, ha='center', va='center', linespacing=1.3)
        arrow(ax, (x + 14, 28), (x + 14, 21.5), None, style='<|-|>')
    frame(ax, 2.5, 3.2, 31, 21, 'database admin can read and write', fs=6.2)
    frame(ax, 66.5, 3.2, 31, 21, 'ledger-store admin can read and write', fs=6.2)
    ax.text(50, 0.6, 'Application secrets are held outside every store (in .env):  MONGO_URI,  LEDGER_KEY,  SMTP credentials,  OTP_SECRET',
            fontsize=6.7, ha='center', style='italic', color='#9a3412', bbox=dict(boxstyle='round,pad=0.3', fc='#fff7ed', ec='#fdba74'))
    fig.savefig(OUT / 'architecture.png', dpi=300, facecolor='white')
    plt.close(fig)


# ======================================================================= 3. ER
def entity(ax, x, top, w, title, rows, color, dashed=False, row=2.3, head=2.9, fs=6.0):
    fc, ec = PAL[color]
    h = head + row * len(rows)
    ls = (0, (4, 2)) if dashed else 'solid'
    ax.add_patch(Rectangle((x, top - h), w, h, fc=fc, ec=ec, lw=1.2, ls=ls, zorder=2))
    ax.add_patch(Rectangle((x, top - head), w, head, fc=ec, ec=ec, lw=1.2, ls=ls, zorder=3, alpha=0.55))
    ax.text(x + w / 2, top - head / 2, title, ha='center', va='center', fontsize=6.6, fontweight='bold', color=INK, zorder=4)
    for i, (name, key) in enumerate(rows):
        y = top - head - row * (i + 1)
        ax.plot([x, x + w], [y + row, y + row], color=ec, lw=0.5, zorder=3)
        ax.text(x + 1.0, y + row / 2, name, va='center', fontsize=fs, color=INK, zorder=4)
        ax.text(x + w - 1.0, y + row / 2, key, va='center', ha='right', fontsize=fs - 0.4, color='#444', zorder=4)
    return {'l': x, 'r': x + w, 't': top, 'b': top - h, 'cx': x + w / 2}


def er():
    fig, ax = canvas(7.4, 5.4, (0, 120), (10, 97))
    frame(ax, 1, 22, 82, 74, 'Election database  (polyvote_relational.db)')
    frame(ax, 86, 22, 33, 74, 'Verification database  (a separate file)')
    org = entity(ax, 4, 91, 22, 'ORGANIZATION', [('org_id', 'PK'), ('org_name', 'NOT NULL'), ('admin_contact', '')], 'pink')
    ele = entity(ax, 36, 91, 24, 'ELECTION', [('election_id', 'PK'), ('org_id', 'FK'), ('status', 'NOM/VOT/CLS'), ('start_time', ''), ('end_time', '')], 'teal')
    entity(ax, 64, 91, 17, 'ADMIN_USERS', [('username', 'UNIQUE'), ('password_hash', '')], 'violet')
    cand = entity(ax, 4, 66, 24, 'CANDIDATE', [('candidate_id', 'PK'), ('election_id', 'FK'), ('name', 'NOT NULL'), ('platform_statement', '')], 'orange')
    vp = entity(ax, 52, 66, 29, 'VOTER_PARTICIPATION', [('participation_id', 'PK'), ('election_id', 'FK, UQ*'), ('student_reg_no', 'UQ*'), ('password_hash', ''), ('has_voted', 'CHECK 0/1')], 'blue')
    br = entity(ax, 4, 42, 28, 'BALLOT_RANKS', [('ballot_token', 'PK'), ('candidate_id', 'PK, FK'), ('election_id', 'FK'), ('preference_rank', 'CHECK 1-3')], 'green')
    led = entity(ax, 40, 44, 41, 'LEDGER_BLOCK  (JSON document in MongoDB)', [('index, timestamp', ''), ('election_id', ''), ('ballot_token', 'link, not FK'), ('vote_data_hash', 'SHA-256'), ('roster_hash', 'SHA-256'), ('prev_hash, curr_hash', 'HMAC chain')], 'grey', dashed=True)
    vc = entity(ax, 89, 91, 27, 'VOTER_CONTACT', [('election_id', 'PK'), ('reg_no', 'PK'), ('email', 'NOT NULL')], 'orange')
    oc = entity(ax, 89, 76, 27, 'OTP_CHALLENGE', [('challenge_id', 'PK'), ('election_id', ''), ('reg_no', ''), ('code_hash', 'HMAC'), ('created_at, expires_at', ''), ('last_sent_at, sends', ''), ('attempts', ''), ('state', 'open/used/locked')], 'teal')
    entity(ax, 89, 52, 27, 'MAIL_LOG', [('log_id', 'PK'), ('sent_at', ''), ('election_id, reg_no', ''), ('email', ''), ('status', '')], 'grey')

    def line(pts, dashed=False):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=INK, lw=0.9, ls=(0, (4, 2.5)) if dashed else 'solid', zorder=1)

    def lab(x, y, s, bold=True, fs=6.3):
        ax.text(x, y, s, fontsize=fs, ha='center', va='center', fontweight='bold' if bold else 'normal', zorder=6, bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none'))

    # ORGANIZATION 1:N ELECTION
    line([(org['r'], 87.5), (ele['l'], 87.5)])
    lab(org['r'] + 1.5, 89.3, '1'); lab(ele['l'] - 1.5, 89.3, 'N'); lab((org['r'] + ele['l']) / 2, 85.9, 'hosts', False, 5.8)
    # ELECTION 1:N CANDIDATE
    line([(ele['cx'] - 6, ele['b']), (ele['cx'] - 6, 71), (cand['cx'], 71), (cand['cx'], cand['t'])])
    lab(ele['cx'] - 6, ele['b'] - 1.5, '1'); lab(cand['cx'], cand['t'] + 1.5, 'N'); lab(27, 71, 'fields', False, 5.8)
    # ELECTION 1:N VOTER_PARTICIPATION
    line([(ele['cx'] + 6, ele['b']), (ele['cx'] + 6, 71), (vp['cx'], 71), (vp['cx'], vp['t'])])
    lab(ele['cx'] + 6, ele['b'] - 1.5, '1'); lab(vp['cx'], vp['t'] + 1.5, 'N'); lab(58, 71, 'registers', False, 5.8)
    # ELECTION 1:N BALLOT_RANKS
    line([(ele['l'] + 2, ele['b']), (ele['l'] + 2, 38.0), (br['r'], 38.0)])
    lab(ele['l'] + 2, ele['b'] - 1.5, '1'); lab(br['r'] + 1.8, 38.0 + 1.3, 'N'); lab(ele['l'] + 2, 56, 'records', False, 5.8)
    # CANDIDATE 1:N BALLOT_RANKS
    line([(cand['cx'] - 5, cand['b']), (cand['cx'] - 5, br['t'])])
    lab(cand['cx'] - 5, cand['b'] - 1.5, '1'); lab(cand['cx'] - 5, br['t'] + 1.5, 'N'); lab(cand['cx'] - 5, (cand['b'] + br['t']) / 2, 'ranked in', False, 5.8)
    # BALLOT_RANKS - LEDGER_BLOCK (dashed, logical)
    line([(br['r'], 34.0), (led['l'], 34.0)], dashed=True)
    lab(br['r'] + 1.8, 35.4, '1'); lab(led['l'] - 1.8, 35.4, '1'); lab((br['r'] + led['l']) / 2, 32.5, 'sealed by', False, 5.8)
    ax.text(66, 48.0, 'No column links ballots to voters', fontsize=6.4, ha='center', color='#9a3412', style='italic')
    # logical links to verification database
    line([(vp['r'], 63), (89, 86)], dashed=True)
    line([(vp['r'], 60), (89, 68)], dashed=True)
    ax.text(102.5, 30, 'Dashed links join on\n(election_id, reg_no);\nno foreign key across\nfiles, and nothing here\nreaches BALLOT_RANKS.', fontsize=5.9, ha='center', va='center', color='#444', linespacing=1.4)
    ax.text(60, 14, 'Solid line: foreign key.   Dashed: logical link to another store (not an FK).   PK primary key, FK foreign key, UQ unique, CHECK check rule.\n'
            '* UNIQUE (reg_no, election_id).  A trigger blocks marking a voter as voted twice.', fontsize=6.0, ha='center', va='center', color='#444', linespacing=1.5)
    fig.savefig(OUT / 'er.png', dpi=300, facecolor='white')
    plt.close(fig)


# ======================================================================= 4. OTP sequence
def otp_sequence():
    fig, ax = canvas(7.2, 5.0, (0, 100), (3, 80))
    names = ['Voter', 'React app', 'FastAPI', 'Verification\nstore', 'SMTP\n(Gmail)']
    xs = [11, 30, 52, 73, 90]
    for n, x in zip(names, xs):
        box(ax, x - 8, 73, 16, 6, n, 'blue', fs=7.2, bold=True)
        ax.plot([x, x], [5, 73], color='#9aa0a6', lw=0.9, ls=(0, (3, 3)), zorder=1)
    msgs = [
        (0, 1, 68, '1  enter reg. no. and password', False),
        (1, 2, 63.5, '2  POST /api/voter/login', False),
        (2, 3, 55, '4  new challenge: store HMAC(code), TTL 5 min', False),
        (2, 4, 50.5, '5  email the code (background thread)', False),
        (2, 1, 46, '6  {otp_required, challenge, email_hint}', 'back'),
        (4, 0, 41.5, "7  the code arrives in the voter's mailbox", 'back'),
        (0, 1, 37, '8  type the 6-digit code', False),
        (1, 2, 32.5, '9  POST /api/voter/otp/verify', False),
        (2, 3, 28, '10  constant-time compare; <= 3 attempts; single use', False),
        (2, 1, 23.5, '11  voting session token', 'back'),
        (1, 2, 19, '12  GET and POST /api/voter/ballot  (bearer token)', False),
    ]
    for a, b, y, text, kind in msgs:
        xa, xb = xs[a], xs[b]
        arrow(ax, (xa, y), (xb, y), None, dashed=(kind == 'back'))
        ax.text((xa + xb) / 2, y + 1.7, text, fontsize=6.5, ha='center', va='center', bbox=WHITE, zorder=5)
    box(ax, 38, 57.8, 28, 3.6, '3  check password and has_voted', 'violet', fs=6.4)
    arrow(ax, (xs[2], 63.5), (xs[2], 61.4), None)
    ax.text(50, 10.5, 'Limits:  resend 1 per 30 s and 5 per challenge;  5 challenges per voter per 15 min;  3 wrong guesses lock the code.\n'
            'A failed email send never blocks sign-in: the code is still shown in the administrator Mail outbox.',
            fontsize=6.4, ha='center', va='center', color='#9a3412', linespacing=1.4, bbox=dict(boxstyle='round,pad=0.4', fc='#fff7ed', ec='#fdba74'))
    fig.savefig(OUT / 'otp_sequence.png', dpi=300, facecolor='white')
    plt.close(fig)


# ======================================================================= 5. threat model
def threat_model():
    fig, ax = canvas(7.2, 4.3, (0, 100), (8.5, 66))
    cols = [(1, 6, 'ID'), (7, 25, 'Adversary'), (32, 29, 'Capability'), (61, 25, 'PolyVote response'), (86, 13, 'Status')]
    y = 61
    for x, w, t in cols:
        box(ax, x, y, w - 0.8, 4.2, t, 'grey', fs=7.2, bold=True, rounded=False)
    rows = [
        ('A1', 'Voter with a leaked or\nguessed password', 'Signs in as someone else', 'Emailed one-time code;\none-vote trigger', 'Prevented', 'green'),
        ('A2', 'Network observer', 'Reads or alters traffic', 'Out of scope beyond\nTLS at the tunnel', 'Not covered', 'red'),
        ('A3', 'Rogue database\nadministrator', 'Read/write on the election\ndatabase only', 'Integrity sweep: modified,\ndeleted, injected, mismatch', 'Detected', 'blue'),
        ('A4', 'Ledger-store\nadministrator', 'Read/write on the ledger\nstore only', 'HMAC hash chain; unique\nblock index', 'Detected', 'blue'),
        ('A5', 'Insider with both stores,\nno secrets', 'Edits both stores to\nmatch each other', 'Keyed chain + sweep catch\nforged receipts, rewrites', 'Detected', 'blue'),
        ('A6', 'Insider with both stores\nand the ledger key', 'Forges valid blocks', 'Needs external anchoring\n(future work)', 'Not covered', 'red'),
        ('A7', 'Roster injection through\nthe admin path', 'Adds a ghost voter, votes\nas them through the API', 'Needs a committed roster\n(future work)', 'Not covered', 'red'),
    ]
    rh = 7.3
    for i, (a, b, c, d, st, col) in enumerate(rows):
        y = 61 - 1.0 - rh * (i + 1)
        for (x, w, _), v in zip(cols[:4], [a, b, c, d]):
            box(ax, x, y, w - 0.8, rh - 0.9, v, 'violet' if x == 1 else 'grey', fs=6.5, bold=(x == 1), rounded=False, align='center' if x == 1 else 'left')
        box(ax, cols[4][0], y, cols[4][1] - 0.8, rh - 0.9, st, col, fs=6.7, bold=True, rounded=False)
    fig.savefig(OUT / 'threat_model.png', dpi=300, facecolor='white')
    plt.close(fig)


# ======================================================================= 6. cast flowchart
def diamond(ax, cx, cy, w, h, text, color='blue', fs=6.4):
    fc, ec = PAL[color]
    ax.add_patch(Polygon([(cx - w / 2, cy), (cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2)], closed=True, fc=fc, ec=ec, lw=1.1, zorder=2))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs, color=INK, zorder=3, linespacing=1.25)


def cast_transaction():
    fig, ax = canvas(6.4, 7.0, (0, 100), (0, 108))
    cx = 38
    steps = [
        ('d', 'Bearer token valid\nand a voter session?', 9, '401 / 403'),
        ('b', 'Take the process-wide WRITE_LOCK', 6, None),
        ('d', 'Election status\nis VOTING?', 9, '409'),
        ('d', 'Ranking valid: exact count, distinct,\ncandidates of this election?', 9, '422'),
        ('d', 'Voter has not\nalready voted?', 9, '409'),
        ('b', 'BEGIN\nUPDATE has_voted = 1  (trigger guards)\nINSERT ranked rows under a new random UUID\nCOMMIT', 12, None),
        ('b', 'Compute roster hash; append sealed block\nto the ledger  (index, prev_hash, HMAC)', 8, None),
        ('b', 'Invalidate the session', 6, None),
        ('b', 'Return receipt: ballot token, block index, block hash', 6, None),
    ]
    y = 105
    gap = 3.4
    prev = None
    for kind, text, h, fail in steps:
        top, mid, bot = y, y - h / 2, y - h
        if kind == 'd':
            diamond(ax, cx, mid, 58, h, text)
        else:
            box(ax, cx - 28, bot, 56, h, text, 'green' if '\n' in text or 'Return' in text or 'Invalidate' in text else 'violet', fs=6.4)
        if prev is not None:
            arrow(ax, (cx, prev), (cx, top), None)
            if steps[steps.index((kind, text, h, fail)) - 1][0] == 'd':
                ax.text(cx + 1.2, (prev + top) / 2, 'yes', fontsize=6.0, va='center')
        if fail:
            xr = cx + 29
            arrow(ax, (xr, mid), (xr + 8, mid), None)
            box(ax, xr + 8.5, mid - 2.4, 20, 4.8, f'reject  {fail}', 'red', fs=6.4)
        prev = bot
        y = bot - gap
    ax.text(84, 36, 'If the ledger is unreachable\nafter the commit, the ballot\nhas no receipt; the sweep\nreports it as injected.', fontsize=6.2, color='#9a3412', va='center', ha='center', style='italic')
    fig.savefig(OUT / 'cast_transaction.png', dpi=300, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    for fn in (architecture, er, otp_sequence, threat_model, cast_transaction):
        fn()
        print('drew', fn.__name__)
