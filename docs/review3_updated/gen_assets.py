"""Figures for the updated edition: the per-scenario detection chart (new results) and copies of the extended-evaluation figures and screenshots.

    python docs/review3_updated/gen_assets.py
"""
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'assets'
OUT.mkdir(exist_ok=True)
RES = ROOT / 'experiments' / 'results'

summary = json.loads((RES / 'summary.json').read_text(encoding='utf-8'))
pf = {x['id']: x for x in json.loads((RES / 'patched_final.json').read_text(encoding='utf-8'))['tamper']}
for t in summary['tamper']:
    t['patched'] = pf[t['id']]['outcome']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, ax = plt.subplots(figsize=(7.2, 2.6))
col = {'detected': '#2da44e', 'detected_manual_only': '#d4a72c', 'undetected': '#cf222e'}
for row, tag in enumerate(('baseline', 'patched')):
    for i, t in enumerate(summary['tamper']):
        ax.barh(row, 1, left=i, color=col[t[tag]], edgecolor='white')
        ax.text(i + .5, row, t['id'], ha='center', va='center', color='white', fontsize=7, fontweight='bold')
ax.set_yticks([0, 1])
ax.set_yticklabels(['Baseline', 'PolyVote (updated)'])
ax.set_xticks([])
ax.invert_yaxis()
for s in ax.spines.values():
    s.set_visible(False)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in col.values()], labels=['Detected automatically', 'Only visible in manual counters', 'Undetected'],
          loc='upper center', bbox_to_anchor=(.5, -0.05), ncol=3, frameon=False)
fig.tight_layout()
fig.savefig(OUT / 'detection.png', dpi=200)

EV = ROOT / 'docs' / 'evaluation'
for src, dst in (('figures/F01_detection_heatmap.png', 'ext_heatmap.png'), ('figures/F03_ablation.png', 'ext_ablation.png'), ('figures/F09_scaling.png', 'ext_scaling.png'),
                 ('figures/F13_password_cracking.png', 'ext_passwords.png'), ('figures/F20_feature_coverage.png', 'ext_coverage.png'),
                 ('screenshots/C13_sweep.png', 'ext_c13.png'), ('screenshots/C17_sweep.png', 'ext_c17.png'), ('figures/F12_concurrency.png', 'ext_concurrency.png')):
    shutil.copy(EV / src, OUT / dst)
print('assets written to', OUT)
