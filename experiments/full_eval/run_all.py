"""Run the whole evaluation in one process and write experiments/results/full/evaluation.json.

    python experiments/full_eval/run_all.py
"""
import csv
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E     # noqa: E402
import extras as Z     # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'results' / 'full'
OUT.mkdir(parents=True, exist_ok=True)
R = {'generated': time.strftime('%Y-%m-%d %H:%M:%S'), 'machine': {'platform': platform.platform(), 'python': platform.python_version(),
                                                              'processor': platform.processor()}}
t0 = time.time()
step = lambda name: print(f'\n== {name} ({time.time() - t0:.0f}s)')   # noqa: E731

step('attack matrix (31 scenarios x 2 key modes)')
M = E.run_scenarios()
R['matrix'] = M
R['profiles_all'] = E.profile_table(M)
R['profiles_in_scope'] = E.profile_table(M, scope_only=True)
R['ablation'] = E.ablation(M)
R['emulation_check'] = E.validate_emulation(M)
step('append-only trigger class')
R['triggers'] = E.run_trigger_class(M)
step('security probes');            R['security'] = Z.run_security()
step('privacy');                    R['privacy'] = Z.run_privacy()
step('false positives');            R['false_positives'] = Z.run_false_positives(120)
step('precision and recall');       R['precision_recall'] = Z.run_precision_recall()
step('tally correctness');          R['tally_check'] = Z.run_tally_check(500)
step('password hashing');           R['password'] = Z.run_password_bench()
R['login_latency'] = Z.run_login_latency()
step('scaling, keyed');             R['perf_keyed'] = Z.run_perf(mode='keyed')
step('scaling, unkeyed (10,000)');  R['perf_unkeyed'] = Z.run_perf(sizes=(1000, 10000), mode='unkeyed')
step('concurrency');                R['concurrency'] = Z.run_concurrency()
R['seconds'] = round(time.time() - t0)
(OUT / 'evaluation.json').write_text(json.dumps(R, indent=2, default=str), encoding='utf-8')

# CSV exports for the paper
with open(OUT / 'attack_matrix.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id', 'scenario', 'adversary', 'in_scope'] + [f'{m}_{d}' for m in ('keyed', 'unkeyed') for d in E.DETECTORS])
    for s in M['scenarios']:
        w.writerow([s['id'], s['title'], s['adversary'], s['in_scope']] + [int(s['modes'][m]['detectors'][d]) for m in ('keyed', 'unkeyed') for d in E.DETECTORS])
with open(OUT / 'design_profiles.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['profile', 'design', 'key_mode', 'detectors', 'detected_all_31', 'rate_all', 'detected_in_scope', 'of_in_scope', 'rate_in_scope'])
    for a, b in zip(R['profiles_all'], R['profiles_in_scope']):
        w.writerow([a['id'], a['label'], a['mode'], '+'.join(a['detectors']), a['detected'], a['rate'], b['detected'], b['of'], b['rate']])
with open(OUT / 'performance.csv', 'w', newline='', encoding='utf-8') as f:
    rows = R['perf_keyed'] + R['perf_unkeyed']
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print(f"\nWrote {OUT / 'evaluation.json'} in {R['seconds']} s")
