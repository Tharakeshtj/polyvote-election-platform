"""Ledger append latency against MongoDB Atlas at different chain lengths.

Uses a scratch database (polyvote_bench) that is dropped afterwards; the real `polyvote` database is not touched.
Needs MONGO_URI (from .env). Writes experiments/results/mongo_bench.json.
"""
import json
import os
import statistics
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ['MONGO_DB'] = 'polyvote_bench'
os.environ.pop('LEDGER_KEY', None)

import audit_ledger as L  # noqa: E402

if L.backend_info()['backend'] != 'mongodb':
    sys.exit(f"MongoDB not active: {L.backend_info()['detail']}")
assert L._coll.database.name == 'polyvote_bench'

SIZES = [100, 1000, 10000]
out = {}
try:
    for n in SIZES:
        L._coll.delete_many({})
        chain, prev = [], '0' * 64
        for i in range(1, n + 1):
            b = L._seal(1, str(uuid.uuid4()), [(1, 1), (2, 2), (3, 3)], i, prev)
            chain.append(b)
            prev = b['curr_hash']
        L._coll.insert_many([dict(b) for b in chain])
        times = []
        for _ in range(20):
            t = time.perf_counter()
            L.append_ballot_receipt(1, str(uuid.uuid4()), [(1, 1), (2, 2), (3, 3)])
            times.append((time.perf_counter() - t) * 1000)
        t = time.perf_counter()
        ok = L.verify_chain_integrity()[0]
        verify_ms = (time.perf_counter() - t) * 1000
        out[str(n)] = {'append_ms_median': round(statistics.median(times), 1), 'append_ms_p90': round(sorted(times)[int(len(times) * .9) - 1], 1),
                       'verify_ms': round(verify_ms, 1), 'chain_ok': ok}
        print(n, out[str(n)])
finally:
    L._coll.drop()   # the Atlas user may not drop databases, so remove the scratch collection
(ROOT / 'experiments' / 'results' / 'mongo_bench.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print('dropped scratch collection; wrote mongo_bench.json')
