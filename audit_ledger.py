"""Hash-chained audit ledger.

Stored in MongoDB (collection `ledger`) when MONGO_URI is set and reachable,
otherwise in a local JSON file. The backend is chosen once at import time.
"""
import json
import hashlib
import hmac
import os
import threading
from datetime import datetime

LEDGER_FILE = 'mongo_audit_ledger.json'

# Read KEY=VALUE lines from a .env next to this file (real environment variables win).
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_path):
    with open(_env_path, encoding='utf-8-sig') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

MONGO_URI = os.environ.get('MONGO_URI', '').strip()
MONGO_DB = os.environ.get('MONGO_DB', 'polyvote')
GENESIS = "0" * 64

_file_lock = threading.Lock()
_coll = None
_backend_note = "json file"

if MONGO_URI:
    try:
        from pymongo import MongoClient, ASCENDING
        from pymongo.errors import DuplicateKeyError
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _client.admin.command('ping')
        _coll = _client[MONGO_DB]['ledger']
        _coll.create_index([('index', ASCENDING)], unique=True)
        _backend_note = f"mongodb ({MONGO_DB}.ledger)"
    except Exception as exc:
        _coll = None
        _backend_note = f"json file (MongoDB unreachable: {type(exc).__name__})"
        print(f"[audit_ledger] WARNING: {_backend_note}")


def backend_info():
    return {"backend": "mongodb" if _coll is not None else "json", "detail": _backend_note,
            "sealing": "hmac-sha256" if LEDGER_KEY else "sha256"}


def get_ledger():
    if _coll is not None:
        return list(_coll.find({}, {'_id': 0}).sort('index', 1))
    if not os.path.exists(LEDGER_FILE):
        return []
    with open(LEDGER_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_ledger(chain):
    """Replace the whole file ledger (JSON backend only)."""
    with open(LEDGER_FILE, 'w') as f:
        json.dump(chain, f, indent=4)


def clear_ledger():
    if _coll is not None:
        _coll.delete_many({})
    else:
        with _file_lock:
            save_ledger([])


# Optional secret that turns the chain into an HMAC chain. Keep it outside the database and the
# ledger store: someone who can only edit those cannot recompute a valid chain without it.
# Blocks up to LEGACY_UNTIL (written before the key existed) keep plain SHA-256.
LEDGER_KEY = os.environ.get('LEDGER_KEY', '').strip().encode()
LEGACY_UNTIL = int(os.environ.get('LEDGER_LEGACY_UNTIL', '0') or 0)


def _block_hash(index, block):
    data = json.dumps(block, sort_keys=True).encode()
    if LEDGER_KEY and index > LEGACY_UNTIL:
        return hmac.new(LEDGER_KEY, data, hashlib.sha256).hexdigest()
    return hashlib.sha256(data).hexdigest()


def _seal(election_id, ballot_token, ranked_payload, index, prev_hash, roster_hash=None):
    # Sort payload to ensure deterministic hashing
    payload_str = json.dumps(sorted(ranked_payload, key=lambda x: x[1]), sort_keys=True)
    block = {
        "index": index,
        "timestamp": datetime.now().isoformat(),
        "election_id": election_id,
        "ballot_token": ballot_token,
        "vote_data_hash": hashlib.sha256(payload_str.encode()).hexdigest(),
        "prev_hash": prev_hash,
    }
    if roster_hash:
        block["roster_hash"] = roster_hash
    block['curr_hash'] = _block_hash(index, block)
    return block


def append_ballot_receipt(election_id, ballot_token, ranked_payload, roster_hash=None):
    if _coll is not None:
        # The unique index on `index` makes a concurrent writer fail instead of forking the chain.
        for _ in range(5):
            last = _coll.find_one({}, {'_id': 0}, sort=[('index', -1)])
            block = _seal(election_id, ballot_token, ranked_payload,
                          (last['index'] + 1) if last else 1,
                          last['curr_hash'] if last else GENESIS, roster_hash)
            try:
                _coll.insert_one(dict(block))
                return block
            except DuplicateKeyError:
                continue
        raise RuntimeError("Could not append to ledger: too much write contention")

    with _file_lock:
        chain = get_ledger()
        block = _seal(election_id, ballot_token, ranked_payload, len(chain) + 1,
                      chain[-1]['curr_hash'] if chain else GENESIS, roster_hash)
        chain.append(block)
        save_ledger(chain)
        return block


def verify_chain_integrity():
    chain = get_ledger()
    if not chain:
        return True, "Ledger is empty."

    for i, curr_block in enumerate(chain):
        expected_prev = chain[i - 1]['curr_hash'] if i else GENESIS
        if curr_block['prev_hash'] != expected_prev:
            return False, f"Broken link at block {curr_block['index']}"

        temp_block = curr_block.copy()
        temp_block.pop('curr_hash', None)
        recalc_hash = _block_hash(curr_block['index'], temp_block)
        if not hmac.compare_digest(recalc_hash, str(curr_block.get('curr_hash'))):
            return False, f"Data tampered at block {curr_block['index']}"

    return True, "Chain intact. Cryptographic ledger is valid."
