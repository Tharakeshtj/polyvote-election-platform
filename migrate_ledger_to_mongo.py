"""One-off: copy the local JSON ledger into MongoDB (needs MONGO_URI), then verify the chain there."""
import json
import os
import sys

import audit_ledger as L  # also loads .env

if not os.environ.get('MONGO_URI'):
    sys.exit("Set MONGO_URI first (in .env or the environment).")

if L.backend_info()['backend'] != 'mongodb':
    sys.exit(f"MongoDB not active: {L.backend_info()['detail']}")
if not os.path.exists(L.LEDGER_FILE):
    sys.exit(f"{L.LEDGER_FILE} not found.")

with open(L.LEDGER_FILE) as f:
    blocks = json.load(f)
if L.get_ledger():
    sys.exit("MongoDB ledger is not empty; refusing to overwrite.")
if blocks:
    L._coll.insert_many([dict(b) for b in blocks])
print(f"Copied {len(blocks)} blocks.", L.verify_chain_integrity())
