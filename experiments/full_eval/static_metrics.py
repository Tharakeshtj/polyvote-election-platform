"""Code, dependency, static-analysis, front-end and live-site measurements. Writes experiments/results/full/static.json.

    python experiments/full_eval/static_metrics.py
"""
import gzip
import json
import re
import ssl
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments' / 'results' / 'full'
OUT.mkdir(parents=True, exist_ok=True)
LIVE = 'https://polyvote-bacse202.onrender.com'
R = {'generated': time.strftime('%Y-%m-%d %H:%M:%S')}


def sh(cmd, cwd=ROOT, timeout=600):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str))
    return p.returncode, p.stdout, p.stderr


def tracked():
    return [Path(x) for x in sh(['git', 'ls-files'])[1].split('\n') if x]


# ---------------------------------------------------------------- lines of code
def loc():
    cats = {'Back end (Python)': 0, 'Front end (TypeScript/TSX)': 0, 'Styles (CSS)': 0, 'Experiments (Python)': 0, 'Document tooling (Python)': 0, 'Configuration and docs (Dockerfile, YAML, Markdown)': 0}
    files = Counter()
    for f in tracked():
        p = ROOT / f
        if not p.exists() or p.suffix.lower() in ('.png', '.pdf', '.docx', '.pptx', '.jpg', '.json', '.ico', '.svg', '.db', '.lock'):
            continue
        try:
            n = sum(1 for line in p.read_text(encoding='utf-8', errors='ignore').splitlines() if line.strip())
        except Exception:
            continue
        s = f.as_posix()
        if s.startswith('docs/'):
            key = 'Document tooling (Python)' if p.suffix == '.py' else 'Configuration and docs (Dockerfile, YAML, Markdown)'
        elif s.startswith('experiments/'):
            key = 'Experiments (Python)' if p.suffix == '.py' else 'Configuration and docs (Dockerfile, YAML, Markdown)'
        elif s.startswith('frontend/src') and p.suffix in ('.ts', '.tsx'):
            key = 'Front end (TypeScript/TSX)'
        elif p.suffix == '.css':
            key = 'Styles (CSS)'
        elif p.suffix == '.py' and not s.startswith('Sample'):
            key = 'Back end (Python)'
        elif p.suffix in ('.md', '.yaml', '.yml', '') or p.name == 'Dockerfile':
            key = 'Configuration and docs (Dockerfile, YAML, Markdown)'
        else:
            continue
        cats[key] += n
        files[key] += 1
    return {'lines': cats, 'files': dict(files), 'total_lines': sum(cats.values())}


# ---------------------------------------------------------------- structure counts
def structure():
    server = (ROOT / 'server.py').read_text(encoding='utf-8')
    routes = re.findall(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', server)
    vr = (ROOT / 'verification' / 'routes.py').read_text(encoding='utf-8') if (ROOT / 'verification' / 'routes.py').exists() else ''
    routes += re.findall(r'@\w+\.(get|post|put|delete|patch)\("([^"]+)"', vr)
    setup = (ROOT / 'setup_db.py').read_text(encoding='utf-8')
    otp = (ROOT / 'verification' / 'otp.py').read_text(encoding='utf-8')
    pages = [p for p in (ROOT / 'frontend' / 'src' / 'pages').rglob('*.tsx')]
    return {'api_routes': len(routes), 'api_routes_by_method': dict(Counter(m.upper() for m, _ in routes)),
            'election_tables': len(re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', setup)), 'election_triggers': len(re.findall(r'CREATE TRIGGER', setup)),
            'election_views': len(re.findall(r'CREATE VIEW', setup)), 'verification_tables': len(re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', otp)),
            'check_constraints': len(re.findall(r'CHECK', setup)), 'unique_or_pk': len(re.findall(r'UNIQUE|PRIMARY KEY', setup)),
            'foreign_keys': len(re.findall(r'FOREIGN KEY', setup)), 'frontend_pages': len(pages),
            'python_deps': [l.strip() for l in (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')],
            'npm_dependencies': json.loads((ROOT / 'frontend' / 'package.json').read_text(encoding='utf-8')).get('dependencies', {}),
            'npm_devdependencies': json.loads((ROOT / 'frontend' / 'package.json').read_text(encoding='utf-8')).get('devDependencies', {})}


# ---------------------------------------------------------------- complexity (radon)
def complexity():
    code, out, err = sh([sys.executable, '-m', 'radon', 'cc', '-s', '-j', 'server.py', 'election_core.py', 'audit_ledger.py', 'tally_engine.py', 'hosted_demo.py', 'seo.py', 'contact.py', 'verification'])
    if code != 0:
        return {'error': err[:200]}
    data = json.loads(out)
    items = [(f, b['name'], b['complexity'], b['rank']) for f, blocks in data.items() for b in blocks if isinstance(b, dict) and 'complexity' in b]
    ranks = Counter(i[3] for i in items)
    worst = sorted(items, key=lambda x: -x[2])[:8]
    mi_code, mi_out, _ = sh([sys.executable, '-m', 'radon', 'mi', '-j', 'server.py', 'election_core.py', 'audit_ledger.py', 'tally_engine.py', 'verification'])
    mi = json.loads(mi_out) if mi_code == 0 else {}
    return {'functions': len(items), 'mean_complexity': round(sum(i[2] for i in items) / len(items), 2), 'rank_counts': dict(ranks),
            'worst': [{'file': w[0], 'function': w[1], 'complexity': w[2], 'rank': w[3]} for w in worst],
            'maintainability_index': {k: round(v['mi'] if isinstance(v, dict) and 'mi' in v else float(v), 1) for k, v in mi.items() if isinstance(v, (int, float)) or (isinstance(v, dict) and 'mi' in v)}}


# ---------------------------------------------------------------- bandit
def bandit():
    code, out, err = sh([sys.executable, '-m', 'bandit', '-r', 'server.py', 'election_core.py', 'audit_ledger.py', 'tally_engine.py', 'hosted_demo.py', 'seo.py', 'contact.py', 'verification', '-f', 'json', '-q'])
    try:
        data = json.loads(out)
    except Exception:
        return {'error': (err or out)[:300]}
    res = data.get('results', [])
    return {'issues': len(res), 'by_severity': dict(Counter(r['issue_severity'] for r in res)), 'by_confidence': dict(Counter(r['issue_confidence'] for r in res)),
            'lines_scanned': data.get('metrics', {}).get('_totals', {}).get('loc'),
            'items': [{'test': r['test_id'], 'name': r['test_name'], 'severity': r['issue_severity'], 'confidence': r['issue_confidence'], 'file': r['filename'].replace(str(ROOT), '').lstrip('\\/'), 'line': r['line_number'], 'text': r['issue_text'][:140]} for r in res]}


def npm_audit():
    code, out, err = sh('npm audit --json', cwd=ROOT / 'frontend')
    try:
        d = json.loads(out)
        return {'vulnerabilities': d.get('metadata', {}).get('vulnerabilities', {}), 'dependencies': d.get('metadata', {}).get('dependencies', {})}
    except Exception:
        return {'error': (err or out)[:200]}


def pip_audit():
    out = {}
    for req in ('requirements-hosted.txt', 'requirements.txt'):
        code, o, err = sh([sys.executable, '-m', 'pip_audit', '-r', req, '-f', 'json'], timeout=300)
        try:
            d = json.loads(o)
            deps = d.get('dependencies', d)
            by = {x['name']: len(x.get('vulns', [])) for x in deps if x.get('vulns')}
            out[req] = {'packages_checked': len(deps), 'vulnerabilities': sum(by.values()), 'by_package': by,
                        'fix': {x['name']: sorted({f for v in x['vulns'] for f in v.get('fix_versions', [])})[:3] for x in deps if x.get('vulns')}}
        except Exception:
            out[req] = {'error': ((err or o) or 'pip-audit not available')[:200]}
    return out


# ---------------------------------------------------------------- front-end bundle
def bundle():
    dist = ROOT / 'frontend' / 'dist' / 'assets'
    if not dist.exists():
        return {'error': 'frontend/dist missing; run npm run build'}
    rows = []
    for f in sorted(dist.iterdir()):
        raw = f.read_bytes()
        rows.append({'file': f.name, 'kb': round(len(raw) / 1024, 1), 'gzip_kb': round(len(gzip.compress(raw, 6)) / 1024, 1)})
    js = [r for r in rows if r['file'].endswith('.js')]
    main = max(js, key=lambda r: r['kb'])
    return {'files': len(rows), 'total_kb': round(sum(r['kb'] for r in rows), 1), 'total_gzip_kb': round(sum(r['gzip_kb'] for r in rows), 1), 'main_js': main,
            'route_chunks': len(js) - 1, 'largest': sorted(rows, key=lambda r: -r['kb'])[:8]}


# ---------------------------------------------------------------- live site
def live():
    ctx = ssl.create_default_context()
    def get(path):
        t = time.perf_counter()
        req = urllib.request.Request(LIVE + path, headers={'User-Agent': 'polyvote-eval'})
        with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
            body = r.read()
            return r.status, dict(r.headers), len(body), (time.perf_counter() - t) * 1000
    out = {}
    try:
        s, h, n, ms = get('/')
        keys = ['content-security-policy', 'x-content-type-options', 'x-frame-options', 'referrer-policy', 'permissions-policy', 'strict-transport-security', 'cache-control']
        lower = {k.lower(): v for k, v in h.items()}
        out['headers'] = {k: lower.get(k) for k in keys}
        out['server'] = lower.get('server')
        out['first_request_ms'] = round(ms)
        times = [get('/api/health')[3] for _ in range(12)]
        out['health_ms'] = {'median': round(sorted(times)[len(times) // 2]), 'min': round(min(times)), 'max': round(max(times))}
        out['home_bytes'] = n
        out['tls'] = ssl.OPENSSL_VERSION
        out['api_config'] = json.loads(urllib.request.urlopen(LIVE + '/api/config', timeout=60).read())
    except Exception as ex:
        out['error'] = f'{type(ex).__name__}: {ex}'
    chk = ROOT / 'experiments' / 'results' / 'web_checklist_live.json'
    if chk.exists():
        res = json.loads(chk.read_text(encoding='utf-8'))['results']
        out['checklist'] = {'pass': sum(r['result'] == 'PASS' for r in res), 'na': sum(r['result'] == 'N/A' for r in res), 'fail': sum(r['result'] == 'FAIL' for r in res), 'items': res}
    return out


if __name__ == '__main__':
    for name, fn in (('loc', loc), ('structure', structure), ('complexity', complexity), ('bandit', bandit), ('npm_audit', npm_audit), ('pip_audit', pip_audit), ('bundle', bundle), ('live', live)):
        t = time.time()
        R[name] = fn()
        print(f'{name}: {time.time() - t:.1f}s', str(R[name])[:160])
    (OUT / 'static.json').write_text(json.dumps(R, indent=2, default=str), encoding='utf-8')
    print('wrote', OUT / 'static.json')
