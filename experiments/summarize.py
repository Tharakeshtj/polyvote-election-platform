"""Combine experiments/results/*.json into summary.json and charts (medians across repeated runs)."""
import json
import statistics
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parent / 'results'


def runs(prefix):
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(R.glob(f'{prefix}_r*.json'))]


def outcomes(run, section):
    return {x['id']: x for x in run[section]}


def bench(rs):
    out = {}
    for n in rs[0]['bench']:
        out[n] = {k: round(statistics.median(r['bench'][n][k] for r in rs), 2)
                  for k in rs[0]['bench'][n] if isinstance(rs[0]['bench'][n][k], (int, float)) and not isinstance(rs[0]['bench'][n][k], bool)}
    return out


base, pat = runs('baseline'), runs('patched')
nokey = json.loads((R / 'nokey.json').read_text(encoding='utf-8'))
summary = {
    'runs': {'baseline': len(base), 'patched': len(pat)},
    'tamper': [
        {'id': i, 'attack': a['attack'], 'baseline': a['outcome'], 'patched': outcomes(pat[0], 'tamper')[i]['outcome'],
         'baseline_detail': a['detail'], 'patched_detail': outcomes(pat[0], 'tamper')[i]['detail']}
        for i, a in outcomes(base[0], 'tamper').items()],
    'prevention': [{'id': i, 'attack': a['attack'], 'mechanism': a['expected'], 'outcome': a['outcome'], 'detail': a['detail']} for i, a in outcomes(pat[0], 'prevention').items()],
    'api_abuse': [{'id': i, 'attack': a['attack'], 'expected': a['expected'], 'outcome': a['outcome'], 'detail': a['detail']} for i, a in outcomes(pat[0], 'api_abuse').items()],
    'otp': [{'id': i, 'test': a['attack'], 'expected': a['expected'], 'outcome': a['outcome'], 'detail': a['detail']} for i, a in outcomes(pat[0], 'otp').items()],
    'privacy': pat[0]['privacy'],
    'bench': {'baseline': bench(base), 'patched': bench(pat), 'patched_no_key': nokey['bench']},
}
(R / 'summary.json').write_text(json.dumps(summary, indent=2, default=str), encoding='utf-8')

# Consistency: outcomes identical across repeated runs
for tag, rs in (('baseline', base), ('patched', pat)):
    ref = {i: a['outcome'] for i, a in outcomes(rs[0], 'tamper').items()}
    for r in rs[1:]:
        assert {i: a['outcome'] for i, a in outcomes(r, 'tamper').items()} == ref, f'{tag} outcomes differ between runs'

det = lambda rs: sum(1 for a in outcomes(rs[0], 'tamper').values() if a['outcome'] == 'detected')  # noqa: E731
auto_or_manual = lambda rs: sum(1 for a in outcomes(rs[0], 'tamper').values() if a['outcome'] in ('detected', 'detected_manual_only'))  # noqa: E731
print('tamper detected automatically  baseline', det(base), 'patched', det(pat), 'of', len(outcomes(base[0], 'tamper')))
print('detected incl. manual counters baseline', auto_or_manual(base), 'patched', auto_or_manual(pat))
for k, v in summary['bench'].items():
    print(k, json.dumps(v))

# ---- charts
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
ns = sorted(int(n) for n in summary['bench']['baseline'])
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
for tag, style in (('baseline', 'o-'), ('patched', 's--')):
    ax[0].plot(ns, [summary['bench'][tag][str(n)]['cast_ms'] for n in ns], style, label=tag)
    ax[1].plot(ns, [summary['bench'][tag][str(n)]['sweep_ms'] for n in ns], style, label=tag)
for a, t in zip(ax, ('Cast latency (file ledger)', 'Integrity sweep time')):
    a.set_xscale('log'); a.set_yscale('log'); a.set_xlabel('ballots in ledger'); a.set_ylabel('ms (median)'); a.set_title(t); a.grid(alpha=.3); a.legend()
fig.tight_layout(); fig.savefig(R / 'bench.png', dpi=200)

fig, ax = plt.subplots(figsize=(7.2, 2.6))
labels = [t['id'] for t in summary['tamper']]
col = {'detected': '#2da44e', 'detected_manual_only': '#d4a72c', 'undetected': '#cf222e'}
for row, tag in enumerate(('baseline', 'patched')):
    for i, t in enumerate(summary['tamper']):
        ax.barh(row, 1, left=i, color=col[t[tag]], edgecolor='white')
        ax.text(i + .5, row, t['id'], ha='center', va='center', color='white', fontsize=7, fontweight='bold')
ax.set_yticks([0, 1]); ax.set_yticklabels(['Baseline', 'Patched']); ax.set_xticks([]); ax.invert_yaxis()
for s in ax.spines.values(): s.set_visible(False)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in col.values()], labels=['Detected automatically', 'Only visible in manual counters', 'Undetected'], loc='upper center', bbox_to_anchor=(.5, -0.05), ncol=3, frameon=False)
fig.tight_layout(); fig.savefig(R / 'detection.png', dpi=200)
print('charts written')
