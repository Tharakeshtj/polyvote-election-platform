"""Draws frontend/public/og.png (1200x630), the link-preview image used in Open Graph and Twitter tags.  python frontend/make_og.py"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

out = Path(__file__).resolve().parent / 'public'
out.mkdir(exist_ok=True)
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor='#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 63); ax.axis('off')
ax.add_patch(FancyBboxPatch((8, 40), 10, 10, boxstyle='round,pad=0,rounding_size=2.2', fc='#ffffff', ec='none'))
ax.plot([10.6, 12.4, 15.6], [44.8, 42.6, 47.2], color='#0a0a0a', lw=5, solid_capstyle='round', solid_joinstyle='round')
ax.text(21, 45, 'PolyVote', color='white', fontsize=44, fontweight='bold', va='center', family='DejaVu Sans')
ax.text(8, 31, 'Ranked-choice elections with a\ntamper-evident ballot ledger', color='white', fontsize=34, va='center', linespacing=1.25, family='DejaVu Sans')
for i, label in enumerate(['Rules enforced in the database', 'Keyed audit ledger', 'Emailed one-time code']):
    x = 8 + i * 37
    ax.add_patch(FancyBboxPatch((x, 9), 35, 7, boxstyle='round,pad=0,rounding_size=1.6', fc='#1c1c1c', ec='#3a3a3a', lw=1.2))
    ax.text(x + 17.5, 12.5, label, color='#e5e5e5', fontsize=15, ha='center', va='center', family='DejaVu Sans')
fig.savefig(out / 'og.png', dpi=100, facecolor='#0a0a0a')
print('wrote', out / 'og.png')
