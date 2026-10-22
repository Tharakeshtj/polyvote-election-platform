"""Loads experiment results and project facts used by the report so numbers are never typed by hand."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'docs' / 'review3_assets'
RES = ROOT / 'experiments' / 'results'


def load():
    S = json.loads((RES / 'summary.json').read_text(encoding='utf-8'))
    S['mongo'] = json.loads((RES / 'mongo_bench.json').read_text(encoding='utf-8'))
    S['loc'] = {}
    for name, pats in {
        'Backend (Python)': ['server.py', 'election_core.py', 'audit_ledger.py', 'tally_engine.py', 'setup_db.py', 'seed_data.py', 'migrate_ledger_to_mongo.py', 'verification/*.py'],
        'Frontend (TypeScript/TSX)': ['frontend/src/**/*.ts', 'frontend/src/**/*.tsx'],
        'Styles (CSS)': ['frontend/src/**/*.css'],
        'Experiments (Python)': ['experiments/*.py'],
    }.items():
        n = 0
        for pat in pats:
            for f in ROOT.glob(pat):
                n += sum(1 for _ in f.open(encoding='utf-8', errors='ignore'))
        S['loc'][name] = n
    return S


def fig(name):
    for sub in ('diagrams', 'screens'):
        p = ASSETS / sub / name
        if p.exists():
            return p
    p = RES / name
    if p.exists():
        return p
    stub = os.environ.get('FIG_STUB')          # layout testing only: stand-in images for figures not drawn yet
    if stub and (Path(stub) / name).exists():
        return Path(stub) / name
    raise FileNotFoundError(name)
