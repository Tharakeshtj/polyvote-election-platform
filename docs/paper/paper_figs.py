"""Single-column figures (3.4 in wide) for the conference paper, drawn from experiments/results/full/evaluation.json.

    python docs/paper/paper_figs.py
"""
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'figs'
OUT.mkdir(exist_ok=True)
R = json.loads((ROOT / 'experiments' / 'results' / 'full' / 'evaluation.json').read_text(encoding='utf-8'))
NAVY, BLUE, GREY, RED, GREEN = '#1b2a55', '#3b6fd4', '#9aa0b4', '#c0392b', '#1e8449'
plt.rcParams.update({'font.family': 'serif', 'font.size': 7.5, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 220})

SHORT = {'P0': 'CRUD, counters by eye', 'P1': 'CRUD + count check', 'P2': 'Plain chain only', 'P3': 'Plain chain + receipt sweep',
         'P4': 'Plain chain + full sweep', 'P5': 'Keyed chain only', 'P6': 'Keyed chain + sweep 1-5', 'P7': 'PolyVote (final)'}


def detection():
    prof = R['profiles_in_scope']
    fig, ax = plt.subplots(figsize=(3.4, 2.35))
    y = range(len(prof))
    ax.barh(y, [p['rate'] for p in prof], color=[NAVY if p['id'] == 'P7' else GREY for p in prof], height=0.65)
    for i, p in enumerate(prof):
        ax.text(p['rate'] + 1.5, i, f"{p['detected']}/{p['of']}", va='center', fontsize=7)
    ax.set_yticks(list(y))
    ax.set_yticklabels([SHORT[p['id']] for p in prof], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 120)
    ax.set_xlabel('In-scope attacks detected (%)')
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / 'detection.png')
    plt.close(fig)


def ablation():
    loo = R['ablation']['leave_one_out']
    names = {'chain': 'Chain check', 'modified': 'Rule 1 modified', 'deleted': 'Rule 2 deleted', 'injected': 'Rule 3 injected',
             'candidate_seal': 'Rule 4 candidate seal', 'count_mismatch': 'Rule 5 count mismatch', 'voter_seal': 'Rule 6 voter seal'}
    full = max(x['detected'] for x in loo) if False else R['profiles_all'][-1]['detected']
    lost = [full - x['detected'] for x in loo]
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    ax.barh(range(len(loo)), lost, color=[RED if v else GREY for v in lost], height=0.65)
    for i, v in enumerate(lost):
        ax.text(v + 0.12, i, str(v), va='center', fontsize=7)
    ax.set_yticks(range(len(loo)))
    ax.set_yticklabels([names[x['removed']] for x in loo], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, max(lost) + 1)
    ax.set_xlabel('Attacks lost without this detector')
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / 'ablation.png')
    plt.close(fig)


def scaling():
    rows = R['perf_keyed']
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    for key, lab, c, m in (('sweep_ms', 'Integrity sweep', NAVY, 'o'), ('chain_verify_ms', 'Chain check', BLUE, 's'), ('tally_ms', 'Instant-runoff tally', GREEN, '^')):
        ax.plot([r['ballots'] for r in rows], [r[key] for r in rows], marker=m, ms=3.5, lw=1.2, color=c, label=lab)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Ballots in the election')
    ax.set_ylabel('Time (ms)')
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / 'scaling.png')
    plt.close(fig)


def architecture():
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(3.4, 2.45))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 72)
    ax.axis('off')

    def box(x, y, w, h, title, lines, fc, ec):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4,rounding_size=2', fc=fc, ec=ec, lw=1))
        ax.text(x + w / 2, y + h - 3, title, ha='center', va='top', fontsize=7, fontweight='bold')
        ax.text(x + w / 2, y + h - 9, chr(10).join(lines), ha='center', va='top', fontsize=5.8, color='#333')

    box(14, 50, 72, 20, 'Application (FastAPI + React)', ['sessions, roster, ballot casting', 'instant-runoff tally, integrity sweep, chain check'], '#eef1fb', NAVY)
    box(1, 14, 31, 28, 'Election DB', ['SQLite', 'triggers, CHECK,', 'UNIQUE, FK', 'ballots, roster'], '#e9f5ec', GREEN)
    box(34.5, 14, 31, 28, 'Verification DB', ['SQLite', 'emails, hashed', 'one-time codes,', 'mail log'], '#fdf3e0', '#b9770e')
    box(68, 14, 31, 28, 'Receipt ledger', ['MongoDB or file', 'HMAC-keyed hash', 'chain, roster seal'], '#f3e9fa', '#7d3c98')
    for x in (16.5, 50, 83.5):
        ax.annotate('', xy=(x, 43), xytext=(x, 49), arrowprops=dict(arrowstyle='<->', color='#555', lw=0.9))
    ax.add_patch(FancyBboxPatch((1, 1), 98, 8, boxstyle='round,pad=0.3,rounding_size=1.5', fc='#fdecea', ec=RED, lw=0.9))
    ax.text(50, 5, 'Secrets outside every store: ledger key, mail credentials, connection strings', ha='center', va='center', fontsize=5.8, color=RED)
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / 'architecture.png')
    plt.close(fig)


if __name__ == '__main__':
    architecture()
    detection()
    ablation()
    scaling()
    print('figures written to', OUT)
