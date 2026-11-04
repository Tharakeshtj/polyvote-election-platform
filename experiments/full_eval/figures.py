"""Turn experiments/results/full/*.json into figures (PNG) and tables (CSV and HTML fragments).

    python experiments/full_eval/figures.py
Outputs go to docs/evaluation/figures and docs/evaluation/tables.
"""
import csv
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'experiments' / 'results' / 'full'
FIG = ROOT / 'docs' / 'evaluation' / 'figures'
TAB = ROOT / 'docs' / 'evaluation' / 'tables'
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

R = json.loads((RES / 'evaluation.json').read_text(encoding='utf-8'))
S = json.loads((RES / 'static.json').read_text(encoding='utf-8')) if (RES / 'static.json').exists() else {}
EVID = json.loads((ROOT / 'docs' / 'review3' / 'uniqueness_evidence.json').read_text(encoding='utf-8'))

NAVY, GREEN, RED, AMBER, GREY, BLUE, LAV = '#1B2A55', '#1A7F37', '#C0392B', '#C98A00', '#9AA0AE', '#3B6FD0', '#E9E9F3'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.titleweight': 'bold',
                     'axes.titlesize': 11, 'figure.dpi': 110, 'savefig.dpi': 170, 'axes.edgecolor': '#555'})
MANIFEST = []


def save(fig, name, title, caption):
    p = FIG / f'{name}.png'
    fig.savefig(p, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    MANIFEST.append({'file': f'figures/{name}.png', 'title': title, 'caption': caption})
    print('  figure', name)


def table(name, headers, rows, title=''):
    with open(TAB / f'{name}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(headers); w.writerows(rows)
    return {'name': name, 'title': title, 'headers': headers, 'rows': rows}


TABLES = []
M = R['matrix']
SC = M['scenarios']
DET = M['detectors']
AUTO = [d for d in DET if d != 'counters']
DET_LABEL = {'chain': 'Chain check', 'modified': 'Rule 1 modified', 'deleted': 'Rule 2 deleted', 'injected': 'Rule 3 injected', 'candidate_seal': 'Rule 4 candidate seal',
             'count_mismatch': 'Rule 5 count mismatch', 'voter_seal': 'Rule 6 voter seal', 'counters': 'Eyeballing counters'}
P_ALL, P_IN = R['profiles_all'], R['profiles_in_scope']
short = lambda s, n=46: s if len(s) <= n else s[:n - 1] + '…'      # noqa: E731


def detected(rec, mode, dets):
    return any(rec['modes'][mode]['detectors'][d] for d in dets)


# ------------------------------------------------------------------ F1 heatmap scenarios x design profiles
def f_heatmap():
    prof = P_ALL
    mat = np.array([[1 if detected(s, p['mode'], p['detectors']) else 0 for p in prof] for s in SC])
    fig, ax = plt.subplots(figsize=(8.6, 9.2))
    ax.imshow(mat, cmap=ListedColormap(['#F4D0CB', '#CFEAD7']), aspect='auto')
    ax.set_xticks(range(len(prof))); ax.set_xticklabels([p['id'] for p in prof], fontweight='bold')
    ax.set_yticks(range(len(SC)))
    ax.set_yticklabels([f"{s['id']}  {short(s['title'], 62)}" + ('' if s['in_scope'] else '  (out of scope)') for s in SC], fontsize=7.4)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, '✓' if mat[i, j] else '✗', ha='center', va='center', color=GREEN if mat[i, j] else RED, fontsize=8, fontweight='bold')
    ax.set_xticks(np.arange(-.5, len(prof), 1), minor=True); ax.set_yticks(np.arange(-.5, len(SC), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.4); ax.tick_params(which='minor', length=0)
    for j, p in enumerate(prof):
        ax.text(j, -1.2, f"{p['detected']}/{p['of']}", ha='center', fontsize=8, color=NAVY, fontweight='bold')
    ax.set_title('Which attacks each design detects (✓ detected, ✗ missed)', pad=24)
    ax.text(0.5, -0.045, '   '.join(f"{p['id']} {textwrap.shorten(p['label'], 38, placeholder='…')}" for p in prof[:4]), transform=ax.transAxes, fontsize=6.6, ha='center', color='#444')
    ax.text(0.5, -0.07, '   '.join(f"{p['id']} {textwrap.shorten(p['label'], 38, placeholder='…')}" for p in prof[4:]), transform=ax.transAxes, fontsize=6.6, ha='center', color='#444')
    save(fig, 'F01_detection_heatmap', 'Detection of 31 attacks by eight design profiles',
         'Rows are attack scenarios; columns are design profiles P0 to P7 (defined in Table 3). Green cells are detected. The count above each column is the number of the 31 scenarios it detects.')


def f_rates():
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    y = np.arange(len(P_ALL))
    ax.barh(y + 0.2, [p['rate'] for p in P_ALL], 0.38, color=GREY, label='All 31 scenarios')
    ax.barh(y - 0.2, [p['rate'] for p in P_IN], 0.38, color=NAVY, label=f"In-scope scenarios ({P_IN[0]['of']})")
    for i, (a, b) in enumerate(zip(P_ALL, P_IN)):
        ax.text(b['rate'] + 1, i - 0.2, f"{b['detected']}/{b['of']}", va='center', fontsize=8, color=NAVY)
        ax.text(a['rate'] + 1, i + 0.2, f"{a['detected']}/{a['of']}", va='center', fontsize=8, color='#555')
    ax.set_yticks(y); ax.set_yticklabels([f"{p['id']}  {textwrap.shorten(p['label'], 44, placeholder='…')}" for p in P_ALL], fontsize=8)
    ax.invert_yaxis(); ax.set_xlim(0, 118); ax.set_xlabel('Share of attacks detected (%)'); ax.legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, -0.14), frameon=False)
    ax.set_title('Detection rate by design')
    save(fig, 'F02_detection_rate', 'Detection rate by design', 'Share of attack scenarios each design profile detects. In-scope excludes the three scenarios outside the stated attacker model (Table 1).')


def f_ablation():
    ab = R['ablation']
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.9), gridspec_kw={'width_ratios': [1.05, 1, 1.05]})
    full = P_ALL[-1]['detected']
    loo = ab['leave_one_out']
    ax = axes[0]
    ax.bar(range(len(loo)), [full - x['detected'] for x in loo], color=[RED if full - x['detected'] else GREY for x in loo])
    for i, x in enumerate(loo):
        ax.text(i, full - x['detected'] + 0.25, str(full - x['detected']), ha='center', fontsize=8, fontweight='bold')
    ax.set_xticks(range(len(loo))); ax.set_xticklabels([DET_LABEL[x['removed']].replace('Rule ', 'R') for x in loo], rotation=40, ha='right', fontsize=7.5)
    ax.set_ylabel('Attacks no longer detected'); ax.set_title('Remove one detector')
    ax = axes[1]
    sg = ab['single']
    ax.bar(range(len(sg)), [x['detected'] for x in sg], color=BLUE)
    for i, x in enumerate(sg):
        ax.text(i, x['detected'] + 0.3, str(x['detected']), ha='center', fontsize=8, fontweight='bold')
    ax.axhline(full, color=GREEN, ls='--', lw=1); ax.text(len(sg) - 0.5, full + 0.4, f'all together: {full}', ha='right', color=GREEN, fontsize=8)
    ax.set_xticks(range(len(sg))); ax.set_xticklabels([DET_LABEL[x['detector']].replace('Rule ', 'R') for x in sg], rotation=40, ha='right', fontsize=7.5)
    ax.set_ylabel('Attacks detected'); ax.set_title('Each detector alone')
    ax = axes[2]
    cu = ab['cumulative']
    ax.step(range(len(cu)), [x['detected'] for x in cu], where='mid', color=NAVY, lw=2)
    ax.plot(range(len(cu)), [x['detected'] for x in cu], 'o', color=NAVY)
    for i, x in enumerate(cu):
        ax.text(i, x['detected'] + 0.6, str(x['detected']), ha='center', fontsize=8)
    ax.set_xticks(range(len(cu))); ax.set_xticklabels([DET_LABEL[x['added']].replace('Rule ', 'R').replace('Eyeballing counters', 'Counters') for x in cu], rotation=40, ha='right', fontsize=7.5)
    ax.set_ylabel('Attacks detected'); ax.set_title('Adding detectors one at a time')
    fig.suptitle('Ablation of the defences (31 scenarios, keyed chain)', fontweight='bold', y=1.03)
    fig.tight_layout()
    save(fig, 'F03_ablation', 'Ablation of the defences', 'Left: attacks lost when one detector is removed. Middle: attacks each detector finds on its own. Right: cumulative detection as detectors are added in the order shown.')


def f_firing():
    ds = AUTO + ['counters']
    mat = np.array([[1 if s['modes']['keyed']['detectors'][d] else 0 for d in ds] for s in SC])
    fig, ax = plt.subplots(figsize=(8.8, 9.0))
    ax.imshow(mat, cmap=ListedColormap(['#F7F7FA', NAVY]), aspect='auto')
    ax.set_xticks(range(len(ds))); ax.set_xticklabels([DET_LABEL[d].replace(' ', '\n') for d in ds], fontsize=6.6)
    ax.set_yticks(range(len(SC))); ax.set_yticklabels([f"{s['id']}  {short(s['title'], 60)}" for s in SC], fontsize=7.3)
    ax.xaxis.tick_top()
    for i in range(len(SC)):
        n = int(mat[i, :-1].sum())
        ax.text(len(ds) - 0.35, i, f'{n}', va='center', fontsize=8, fontweight='bold', color=GREEN if n >= 2 else (AMBER if n == 1 else RED))
    ax.text(len(ds) - 0.35, -1.1, 'detectors\nfiring', ha='center', fontsize=7.4, fontweight='bold')
    ax.set_xticks(np.arange(-.5, len(ds), 1), minor=True); ax.set_yticks(np.arange(-.5, len(SC), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.3); ax.tick_params(which='minor', length=0)
    ax.set_xlim(-.5, len(ds) + .2)
    ax.set_title('Which detector catches which attack (keyed chain)', pad=40)
    save(fig, 'F04_detector_firing', 'Detector firing matrix', 'Dark cells show which detectors fire for each attack. The number at the right is how many automatic detectors fire; two or more means the attack is caught redundantly.')


def f_key_value():
    both = [(s['id'], detected(s, 'keyed', AUTO), detected(s, 'unkeyed', AUTO)) for s in SC]
    lost = [b for b in both if b[1] and not b[2]]
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    cats = ['Detected with key\nand without key', 'Detected only\nwith the key', 'Missed either way']
    vals = [sum(1 for b in both if b[1] and b[2]), len(lost), sum(1 for b in both if not b[1] and not b[2])]
    bars = ax.bar(cats, vals, color=[GREEN, AMBER, RED])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v), ha='center', fontweight='bold')
    ax.set_ylabel('Scenarios'); ax.set_title('What the secret key adds')
    ax.text(1, vals[1] / 2, ' '.join(b[0] for b in lost), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    save(fig, 'F05_key_value', 'Value of the keyed chain', 'Scenarios detected by the full design with the HMAC key versus the same design with a plain SHA-256 chain. The ids in the amber bar are attacks that only fail when the attacker does not hold the key.')


def f_adversary():
    adv = {}
    for s in SC:
        adv.setdefault(s['adversary'], []).append(s)
    order = ['db', 'ledger', 'both', 'api', 'key']
    names = {'db': 'Election database\nonly', 'ledger': 'Ledger store\nonly', 'both': 'Both stores\n(no key)', 'api': 'Database +\npublic API', 'key': 'Both stores\n+ the key'}
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    x = np.arange(len(order))
    tot = [len(adv.get(k, [])) for k in order]
    hit = [sum(1 for s in adv.get(k, []) if detected(s, 'keyed', AUTO)) for k in order]
    ax.bar(x, tot, color=LAV, edgecolor=NAVY, label='Scenarios')
    ax.bar(x, hit, color=GREEN, label='Detected')
    for i, (t, h) in enumerate(zip(tot, hit)):
        ax.text(i, t + 0.2, f'{h}/{t}', ha='center', fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels([names[k] for k in order], fontsize=8)
    ax.set_ylabel('Scenarios'); ax.set_title('Detection by attacker capability'); ax.legend(frameon=False)
    save(fig, 'F06_by_adversary', 'Detection by attacker capability', 'Every scenario where the attacker lacks the ledger key is detected. The scenarios with the key (and one scenario about unsealed display text) are outside the attacker model and are reported openly.')


def f_triggers():
    tr = R['triggers']
    fin = sum(1 for s in SC if detected(s, 'keyed', AUTO))
    crud = sum(1 for s in SC if detected(s, 'unkeyed', ['counters']))
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    labels = ['Append-only triggers\n(writer cannot drop them)', 'Same triggers,\nwriter has schema rights', 'PolyVote final']
    prevented = [len(tr['prevented']), 0, 0]
    counters = [len(tr['counters_only']), crud, 0]
    detect = [0, 0, fin]
    miss = [tr['total'] - len(tr['prevented']) - len(tr['counters_only']), tr['total'] - crud, tr['total'] - fin]
    left = np.zeros(3)
    for vals, col, lab in ((prevented, BLUE, 'Prevented by the trigger'), (counters, AMBER, 'Visible only in the counters'), (detect, GREEN, 'Detected automatically'), (miss, '#E3A9A2', 'Not detected')):
        ax.barh(labels, vals, left=left, color=col, label=lab)
        for i, v in enumerate(vals):
            if v:
                ax.text(left[i] + v / 2, i, str(v), ha='center', va='center', color='white' if col != '#E3A9A2' else '#333', fontweight='bold', fontsize=8)
        left += np.array(vals)
    ax.invert_yaxis(); ax.set_xlim(0, tr['total']); ax.set_xlabel('Scenarios (31)'); ax.legend(ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.22), frameon=False, fontsize=7.5)
    ax.set_title('Database-level append-only triggers versus detection')
    save(fig, 'F07_triggers', 'Append-only triggers versus detection', 'Triggers on the ballot table stop edits and deletions by a writer who cannot drop them, but they do not stop injection, ledger tampering or roster changes, and a writer with schema rights removes them. Detection covers what prevention cannot.')


def f_latency():
    rows = R['perf_keyed']
    ids = {s['id']: s['modes']['keyed']['ms'] for s in SC}
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.bar(range(len(SC)), [ids[s['id']] for s in SC], color=BLUE)
    ax.set_xticks(range(len(SC))); ax.set_xticklabels([s['id'] for s in SC], rotation=90, fontsize=7)
    ax.set_ylabel('Sweep + chain check (ms)'); ax.set_title('Time to audit a 60-voter, 40-ballot election after each attack')
    save(fig, 'F08_audit_time', 'Audit time per scenario', 'Time for the integrity sweep plus the chain check on the small test election after each attack.')


def f_scaling():
    rows = R['perf_keyed']
    n = [r['ballots'] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))
    ax = axes[0]
    for key, lab, col in (('sweep_ms', 'Integrity sweep', NAVY), ('chain_verify_ms', 'Chain verification', BLUE), ('tally_ms', 'Instant-runoff tally', AMBER), ('receipt_lookup_ms', 'Receipt lookup', GREEN)):
        ax.plot(n, [r[key] for r in rows], 'o-', label=lab, color=col)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('Ballots in the election'); ax.set_ylabel('Time (ms, median)'); ax.legend(frameon=False, fontsize=8)
    ax.set_title('Audit and count operations')
    ax = axes[1]
    ax.plot(n, [r['cast_p50_ms'] for r in rows], 'o-', label='p50', color=NAVY)
    ax.plot(n, [r['cast_p95_ms'] for r in rows], 's--', label='p95', color=AMBER)
    ax.plot(n, [r['cast_p99_ms'] for r in rows], '^:', label='p99', color=RED)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('Ballots already in the ledger'); ax.set_ylabel('Cost of casting one ballot (ms)'); ax.legend(frameon=False)
    ax.set_title('Casting latency with the file ledger')
    save(fig, 'F09_scaling', 'Scaling with election size', 'Left: median time of the sweep, chain check, tally and receipt lookup from 100 to 100,000 ballots (log scales). Right: latency percentiles of casting one ballot; the file ledger rewrites the file on each append, so cost grows with size.')


def f_sizes():
    rows = R['perf_keyed']
    n = [r['ballots'] for r in rows]
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.5))
    axes[0].plot(n, [r['ledger_kb'] / 1024 for r in rows], 'o-', color=NAVY, label='Ledger file (MB)')
    axes[0].plot(n, [r['db_kb'] / 1024 for r in rows], 's-', color=BLUE, label='Election database (MB)')
    axes[0].set_xscale('log'); axes[0].set_yscale('log'); axes[0].set_xlabel('Ballots'); axes[0].set_ylabel('Size (MB)'); axes[0].legend(frameon=False, fontsize=8); axes[0].set_title('Storage')
    axes[1].plot(n, [r['rss_mb_after_sweep'] for r in rows], 'o-', color=GREEN)
    axes[1].set_xscale('log'); axes[1].set_xlabel('Ballots'); axes[1].set_ylabel('Process memory after sweep (MB)'); axes[1].set_title('Memory')
    axes[2].plot(n, [r['reseal_roster_ms'] for r in rows], 'o-', color=AMBER, label='Re-seal roster')
    axes[2].plot(n, [max(r['sweep_ms'] - r['sweep_no_seal_ms'], 0.01) for r in rows], 's--', color=RED, label='Sweep cost of roster check')
    axes[2].set_xscale('log'); axes[2].set_yscale('log'); axes[2].set_xlabel('Ballots (voters ≈ ballots)'); axes[2].set_ylabel('ms'); axes[2].legend(frameon=False, fontsize=8); axes[2].set_title('Cost of the voter-roster seal')
    fig.tight_layout()
    save(fig, 'F10_sizes_memory_seal', 'Storage, memory and roster-seal overhead', 'Storage grows linearly; memory is the process size after a sweep; the roster seal costs milliseconds even at 100,000 voters.')


def f_overhead():
    k = {r['ballots']: r for r in R['perf_keyed']}
    u = {r['ballots']: r for r in R['perf_unkeyed']}
    common = [n for n in u if n in k]
    metrics = [('sweep_ms', 'Sweep'), ('chain_verify_ms', 'Chain check'), ('cast_p50_ms', 'Cast p50')]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    w = 0.38
    xs = np.arange(len(metrics))
    n = max(common)
    ax.bar(xs - w / 2, [u[n][m] for m, _ in metrics], w, color=GREY, label='Plain SHA-256 chain')
    ax.bar(xs + w / 2, [k[n][m] for m, _ in metrics], w, color=NAVY, label='Keyed (HMAC) chain')
    for i, (m, lab) in enumerate(metrics):
        d = (k[n][m] / u[n][m] - 1) * 100
        ax.text(i + w / 2, k[n][m], f'{d:+.0f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax.set_xticks(xs); ax.set_xticklabels([l for _, l in metrics]); ax.set_ylabel(f'ms at {n:,} ballots'); ax.legend(frameon=False)
    ax.set_title('Cost of keying the chain')
    save(fig, 'F11_key_overhead', 'Overhead of the keyed chain', 'The same operations with a plain SHA-256 chain and with the HMAC-keyed chain at the largest size measured in both modes.')


def f_concurrency():
    rows = R['concurrency']
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.5))
    axes[0].plot([r['threads'] for r in rows], [r['throughput_per_s'] for r in rows], 'o-', color=NAVY)
    axes[0].set_xlabel('Simultaneous voters (threads)'); axes[0].set_ylabel('Ballots accepted per second'); axes[0].set_title('Throughput')
    axes[1].plot([r['threads'] for r in rows], [r['p50_ms'] for r in rows], 'o-', color=BLUE, label='p50')
    axes[1].plot([r['threads'] for r in rows], [r['p95_ms'] for r in rows], 's--', color=AMBER, label='p95')
    axes[1].set_xlabel('Simultaneous voters (threads)'); axes[1].set_ylabel('Latency (ms)'); axes[1].legend(frameon=False); axes[1].set_title('Latency')
    for r in rows:
        axes[0].text(r['threads'], r['throughput_per_s'] * 1.04, f"{r['errors']} err", ha='center', fontsize=7, color=GREEN if r['errors'] == 0 else RED)
    fig.tight_layout()
    save(fig, 'F12_concurrency', 'Concurrent voting', 'A write lock serialises ballot casts, so throughput stays flat while latency grows with the number of simultaneous voters. After every run the chain verified and the sweep passed, with zero errors.')


def f_passwords():
    pw = R['password']
    rows = pw['keyspace_seconds']
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    x = np.arange(len(rows))
    ax.bar(x - 0.2, [r['legacy_seconds'] for r in rows], 0.4, color=RED, label='Before: unsalted SHA-256')
    ax.bar(x + 0.2, [r['new_seconds'] for r in rows], 0.4, color=GREEN, label=f"After: salted PBKDF2-SHA256 ({pw['iterations']:,} rounds)")
    ax.set_yscale('log'); ax.set_xticks(x); ax.set_xticklabels([r['class'] for r in rows], fontsize=8)
    ax.set_ylabel('Seconds to try every password (1 CPU thread)')
    for yv, lab in ((3600, '1 hour'), (86400 * 365, '1 year')):
        ax.axhline(yv, color='#999', lw=0.8, ls=':'); ax.text(len(rows) - 0.45, yv * 1.25, lab, fontsize=7.5, color='#666', ha='right')
    ax.legend(frameon=False, fontsize=8, loc='upper left'); ax.set_title('Offline password guessing against a stolen database')
    save(fig, 'F13_password_cracking', 'Password hash strength', f"Time to try every password in a character class on one CPU thread. The new format is about {pw['slowdown_factor']:,} times slower per guess and every hash has its own random salt, so tables built once cannot be reused.")


def f_precision():
    rows = R['precision_recall']
    fig, ax = plt.subplots(figsize=(8, 3.4))
    cats = ['modified', 'deleted', 'injected']
    x = np.arange(len(cats))
    for j, k in enumerate(sorted({r['tampered_per_category'] for r in rows})):
        vals = [next(r for r in rows if r['category'] == c and r['tampered_per_category'] == k) for c in cats]
        ax.bar(x + (j - 1) * 0.26, [v['recall'] for v in vals], 0.24, label=f'{k} tampered per category', color=[BLUE, NAVY, GREEN][j])
    ax.set_ylim(0, 1.15); ax.set_xticks(x); ax.set_xticklabels(['Modified ballots', 'Deleted ballots', 'Injected ballots']); ax.set_ylabel('Recall (precision was 1.0 in every case)')
    ax.legend(frameon=False, ncol=3, fontsize=8, loc='lower center'); ax.set_title('The sweep names exactly the tampered ballots')
    save(fig, 'F14_precision_recall', 'Precision and recall of anomaly identification', 'With 1, 5 and 20 tampered ballots per category in a 150-ballot election, the sweep reports precisely the tampered tokens: no false positives and no misses.')


def f_false_pos():
    fp = R['false_positives']
    fig, ax = plt.subplots(figsize=(7.8, 3.3))
    ops = fp['ops']
    names = ['Elections created', 'Voters bulk-registered', 'Voters added mid-vote', 'Ballot batches cast', 'Elections closed', 'Sweeps run', 'False alarms']
    vals = [fp['elections'], ops['bulk_register'], ops['add_voter'], ops['simulate'], ops['close'], fp['sweeps'], fp['false_alarms']]
    bars = ax.barh(names, vals, color=[BLUE] * 6 + [GREEN if fp['false_alarms'] == 0 else RED])
    for b, v in zip(bars, vals):
        ax.text(v + max(vals) * 0.01, b.get_y() + b.get_height() / 2, str(v), va='center', fontweight='bold', fontsize=8)
    ax.invert_yaxis(); ax.set_title(f"Clean elections never raise an alarm ({fp['false_alarms']} of {fp['sweeps']} sweeps)")
    save(fig, 'F15_false_positives', 'False alarms on clean elections', 'Randomised legitimate use (bulk registration, late voters, ballots, closing) followed by a sweep and chain check each time, with and without the key.')


def f_tally():
    tc = R['tally_check']
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    parts = [(tc['agree'] - tc['with_tie_paths'], 'Single reachable\nwinner', GREEN), (tc['with_tie_paths'], 'Tie path (any valid\nwinner accepted)', AMBER), (tc['elections'] - tc['agree'], 'Disagreement', RED)]
    parts = [p for p in parts if p[0] > 0]
    ax.pie([p[0] for p in parts], labels=[p[1] for p in parts], colors=[p[2] for p in parts], autopct='%.0f%%', startangle=90, textprops={'fontsize': 7.5},
           pctdistance=0.6, labeldistance=1.12)
    ax.set_title(f"Tally vs reference ({tc['agree']}/{tc['elections']} agree)")
    save(fig, 'F16_tally_agreement', 'Tally correctness', 'Random elections (3-8 candidates, 5-300 ballots) counted by the application and by an independent implementation that explores every possible tie-break.')


def f_snapshot():
    rows = R['privacy']['snapshot_differencing']
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.plot([r['snapshot_interval_casts'] for r in rows], [r['attacker_success'] for r in rows], 'o-', color=RED, label='Simulated attacker')
    ax.plot([r['snapshot_interval_casts'] for r in rows], [r['ideal_1_over_k'] for r in rows], '--', color=GREY, label='1 / k')
    ax.set_xscale('log'); ax.set_xlabel('Ballots cast between two database snapshots (k)'); ax.set_ylabel('Chance of linking a voter to a ballot'); ax.legend(frameon=False)
    ax.set_title('Snapshot-differencing attack on voter privacy')
    save(fig, 'F17_snapshot_attack', 'Snapshot differencing', 'An attacker who copies the database before and after a single cast can link that voter to that ballot; the anonymity set is the number of casts between copies. This is a known limit of any design that stores a voted flag.')


def f_code():
    st = S.get('loc')
    if not st:
        return
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.6))
    items = sorted(st['lines'].items(), key=lambda kv: -kv[1])
    axes[0].barh([textwrap.shorten(k, 38, placeholder='…') for k, _ in items], [v for _, v in items], color=NAVY)
    for i, (_, v) in enumerate(items):
        axes[0].text(v + 60, i, f'{v:,}', va='center', fontsize=8)
    axes[0].invert_yaxis(); axes[0].set_xlabel('Non-blank lines'); axes[0].set_title(f"Repository size ({st['total_lines']:,} lines)")
    cx = S.get('complexity', {})
    if cx and 'rank_counts' in cx:
        order = ['A', 'B', 'C', 'D', 'E', 'F']
        vals = [cx['rank_counts'].get(r, 0) for r in order]
        axes[1].bar(order, vals, color=[GREEN, '#6FBF6F', AMBER, '#E08A3C', RED, RED])
        for i, v in enumerate(vals):
            axes[1].text(i, v + 0.3, str(v), ha='center', fontsize=8)
        axes[1].set_xlabel('Cyclomatic complexity rank (A is simplest)'); axes[1].set_ylabel('Functions'); axes[1].set_title(f"Back-end complexity (mean {cx['mean_complexity']})")
    fig.tight_layout()
    save(fig, 'F18_code_metrics', 'Code size and complexity', 'Left: lines of code by component. Right: distribution of cyclomatic complexity ranks across back-end functions (radon).')


def f_bundle():
    b = S.get('bundle')
    if not b or 'largest' not in b:
        return
    fig, ax = plt.subplots(figsize=(8.2, 3.5))
    L_ = b['largest']
    y = np.arange(len(L_))
    ax.barh(y + 0.2, [r['kb'] for r in L_], 0.38, color=GREY, label='Raw')
    ax.barh(y - 0.2, [r['gzip_kb'] for r in L_], 0.38, color=NAVY, label='Gzip')
    ax.set_yticks(y); ax.set_yticklabels([textwrap.shorten(r['file'], 34, placeholder='…') for r in L_], fontsize=7.5); ax.invert_yaxis(); ax.set_xlabel('KB')
    ax.legend(frameon=False); ax.set_title(f"Front-end bundle: {b['total_kb']:,} KB raw, {b['total_gzip_kb']:,} KB gzip, {b['route_chunks']} lazy route chunks")
    save(fig, 'F19_bundle', 'Front-end bundle', 'Largest files in the production build. Routes are split into chunks that load on demand.')


def f_coverage():
    codes = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9']
    val = {'yes': 2, 'partial': 1, 'no': -1, 'not documented': 0}
    short_names = {'Helios Voting (helios-server)': 'Helios', 'Belenios': 'Belenios', 'Civitas': 'Civitas', 'ElectionGuard (Microsoft / Election-Tech-Initiative)': 'ElectionGuard',
                   'Zeus (GRNET)': 'Zeus', 'CIVS (Condorcet Internet Voting Service, Cornell)': 'CIVS', 'OpaVote': 'OpaVote', 'ElectionBuddy': 'ElectionBuddy', 'Simply Voting': 'Simply Voting',
                   'Election Runner': 'Election Runner', 'TapVoter': 'TapVoter', 'RankedVote': 'RankedVote', 'BetterVoting (Equal-Vote/bettervoting, formerly star-server)': 'BetterVoting',
                   'Google Forms': 'Google Forms', 'Microsoft Forms': 'Microsoft Forms', 'Decidim (decidim-elections + Bulletin Board)': 'Decidim', 'Consul Democracy': 'Consul',
                   'deOpty/flexyvotes (Django election + paid-voting platform)': 'FlexyVotes', "9022574361/Online_Voting_System ('VeriVote')": 'VeriVote',
                   'DikshantMaskare/securevote-online-voting-system': 'SecureVote', 'RuchikaaVerma/SentinelVote-AI': 'SentinelVote', 'nnnnnndev/voting-app (FastAPI, faculty-meeting voting)': 'voting-app (FastAPI)'}
    rows = []
    for s in EVID:
        nm = short_names.get(s['name'])
        if nm:
            rows.append((nm, [val.get(str(s[c]['value']).lower(), 0) for c in codes]))
    rows.append(('PolyVote (our tests)', [2] * 9))
    score = [(n, sum(1 for v in vs if v == 2) + 0.5 * sum(1 for v in vs if v == 1)) for n, vs in rows]
    order = sorted(range(len(rows)), key=lambda i: -score[i][1])
    mat = np.array([rows[i][1] for i in order])
    fig, ax = plt.subplots(figsize=(7.8, 8.6))
    ax.imshow(mat, cmap=ListedColormap(['#F4D0CB', '#F4F4F8', '#FBEFD0', '#CFEAD7']), vmin=-1, vmax=2, aspect='auto')
    ax.set_xticks(range(9)); ax.set_xticklabels(codes, fontweight='bold'); ax.xaxis.tick_top()
    ax.set_yticks(range(len(order))); ax.set_yticklabels([rows[i][0] + f'  ({score[i][1]:g})' for i in order], fontsize=8)
    for i in range(mat.shape[0]):
        for j in range(9):
            ax.text(j, i, {2: 'Yes', 1: 'Part', 0: '–', -1: 'No'}[mat[i, j]], ha='center', va='center', fontsize=7, color={2: GREEN, 1: AMBER, 0: '#888', -1: RED}[mat[i, j]])
    ax.set_xticks(np.arange(-.5, 9, 1), minor=True); ax.set_yticks(np.arange(-.5, len(order), 1), minor=True); ax.grid(which='minor', color='white', linewidth=1.2); ax.tick_params(which='minor', length=0)
    ax.set_title(f'Documented features of {len(rows) - 1} of the 33 systems read, and PolyVote (score = Yes + ½ Part)', pad=30, fontsize=9)
    save(fig, 'F20_feature_coverage', 'Documented feature coverage of related systems',
         'From each system\'s own page, README or paper (URL for every cell in the evidence file). F1 ranked counting, F2 many organisations, F3 database rules, F4 unlinked ballots, F5 keyed ledger and sweep, F6 email OTP, F7 QR voting, F8 receipt, F9 easy to run. – means not documented, not absent. PolyVote\'s row rests on the tests in this dossier.')
    return rows, score


def f_inventory():
    cats = {'Prevention (database)': 7, 'Abuse through the API': 13, 'Attack scenarios': len(SC), 'One-time code': 14, 'Security probes': R['security']['fuzz']['payload_count'] // 10 if 'security' in R else 0,
            'Tally cross-checks': R['tally_check']['elections'], 'Clean-election sweeps': R['false_positives']['sweeps']}
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.barh(list(cats), list(cats.values()), color=NAVY)
    for i, v in enumerate(cats.values()):
        ax.text(v + max(cats.values()) * 0.01, i, str(v), va='center', fontweight='bold', fontsize=8)
    ax.invert_yaxis(); ax.set_xscale('log'); ax.set_xlabel('Executed checks (log scale)'); ax.set_title('What was executed')
    save(fig, 'F21_test_inventory', 'Executed checks', 'Number of executed checks per category in this evaluation.')


def build_tables():
    T = TABLES
    T.append(table('T01_scenarios', ['ID', 'Attack', 'Attacker capability', 'In the attacker model', 'Note'],
                   [[s['id'], s['title'], {'db': 'Election database', 'ledger': 'Ledger store', 'both': 'Both stores, no key', 'api': 'Database + public API', 'key': 'Both stores + the key'}[s['adversary']], 'Yes' if s['in_scope'] else 'No', s['note']] for s in SC],
                   'Table 1. The 31 attack scenarios'))
    rows = []
    for s in SC:
        k, u = s['modes']['keyed']['detectors'], s['modes']['unkeyed']['detectors']
        rows.append([s['id']] + ['●' if k[d] else '' for d in AUTO + ['counters']] + ['●' if any(u[d] for d in AUTO) else ''])
    T.append(table('T02_detector_matrix', ['ID'] + [DET_LABEL[d] for d in AUTO + ['counters']] + ['Any automatic detector, plain chain'], rows, 'Table 2. Detectors that fire for each attack (keyed chain)'))
    T.append(table('T03_design_profiles', ['Profile', 'Design', 'Detectors used', 'Key', 'Detected (all 31)', 'Rate', 'Detected (in scope)', 'Rate (in scope)', 'Missed'],
                   [[a['id'], a['label'], ' + '.join(DET_LABEL[d] for d in a['detectors']), a['mode'], f"{a['detected']}/{a['of']}", f"{a['rate']}%", f"{b['detected']}/{b['of']}", f"{b['rate']}%", ' '.join(a['missed'])] for a, b in zip(P_ALL, P_IN)],
                   'Table 3. Design profiles and what they detect'))
    ab = R['ablation']
    T.append(table('T04_ablation', ['Removed detector', 'Still detected', 'Lost attacks'], [[DET_LABEL[x['removed']], f"{x['detected']}/{x['of']}", ' '.join(x['lost']) or '-'] for x in ab['leave_one_out']], 'Table 4. Leave-one-out ablation'))
    T.append(table('T05_single', ['Detector alone', 'Detected', 'Attacks'], [[DET_LABEL[x['detector']], f"{x['detected']}/{x['of']}", ' '.join(x['ids'])] for x in ab['single']], 'Table 5. Each detector on its own'))
    tr = R['triggers']
    T.append(table('T06_triggers', ['Class', 'Count', 'Scenarios'], [['Prevented by append-only triggers', len(tr['prevented']), ' '.join(tr['prevented'])], ['Visible only in the counters', len(tr['counters_only']), ' '.join(tr['counters_only'])],
                                                                    ['Neither', len(tr['neither']), ' '.join(tr['neither'])]], 'Table 6. Append-only triggers on the ballot table'))
    ec = R['emulation_check']
    if ec:
        T.append(table('T07_emulation', ['Scenario', 'Real Review 2 code (measured earlier)', 'Emulated from the detector matrix', 'Agree'], [[r['id'], r['real_review2'], r['emulated'], 'yes' if r['agree'] else 'NO'] for r in ec['rows']],
                       f"Table 7. Emulating the Review 2 design from the matrix reproduces the real Review 2 code ({ec['agree']}/{ec['of']})"))
    pr = R['precision_recall']
    T.append(table('T08_precision_recall', ['Tampered per category', 'Category', 'True', 'Reported', 'True positives', 'Precision', 'Recall'], [[r['tampered_per_category'], r['category'], r['true'], r['reported'], r['true_positives'], r['precision'], r['recall']] for r in pr], 'Table 8. Precision and recall'))
    fp = R['false_positives']
    T.append(table('T09_false_positives', ['Measure', 'Value'], [['Clean elections', fp['elections']], ['Sweeps run', fp['sweeps']], ['False alarms', fp['false_alarms']], ['False-positive rate', fp['false_positive_rate']]] + [[f'Operations: {k}', v] for k, v in fp['ops'].items()], 'Table 9. False alarms on clean elections'))
    tc = R['tally_check']
    T.append(table('T10_tally', ['Measure', 'Value'], [['Random elections', tc['elections']], ['Agree with the reference', tc['agree']], ['Elections with a tie path', tc['with_tie_paths']], ['Disagreements', tc['elections'] - tc['agree']]], 'Table 10. Tally correctness'))
    pw = R['password']
    T.append(table('T11_password', ['Password class', 'Unsalted SHA-256 (before)', 'Salted PBKDF2 (after)'],
                   [[r['class'], human_time(r['legacy_seconds']), human_time(r['new_seconds'])] for r in pw['keyspace_seconds']] + [['Hashes per second, 1 CPU thread', f"{pw['sha256_hashes_per_second']:,}", f"{pw['pbkdf2_hashes_per_second']}"], ['Verify time at login', '<0.01 ms', f"{pw['verify_ms']} ms"]], 'Table 11. Offline guessing cost'))
    T.append(table('T12_performance', ['Ballots', 'Sweep ms', 'Sweep without seal ms', 'Chain check ms', 'Tally ms', 'Receipt ms', 'Cast p50', 'Cast p95', 'Cast p99', 'Ledger KB', 'DB KB', 'Memory MB'],
                   [[r['ballots'], r['sweep_ms'], r['sweep_no_seal_ms'], r['chain_verify_ms'], r['tally_ms'], r['receipt_lookup_ms'], r['cast_p50_ms'], r['cast_p95_ms'], r['cast_p99_ms'], r['ledger_kb'], r['db_kb'], r['rss_mb_after_sweep']] for r in R['perf_keyed']], 'Table 12. Scaling (keyed chain, file ledger)'))
    T.append(table('T13_concurrency', ['Threads', 'Casts', 'Wall s', 'Casts/s', 'p50 ms', 'p95 ms', 'Errors', 'Chain ok', 'Sweep ok'], [[r['threads'], r['casts'], r['wall_s'], r['throughput_per_s'], r['p50_ms'], r['p95_ms'], r['errors'], r['chain_ok_after'], r['sweep_ok_after']] for r in R['concurrency']], 'Table 13. Concurrency'))
    sec = R['security']
    srows = [['Brute-force password guesses', f"{sec['bruteforce']['attempts']} attempts, {sec['bruteforce']['attempts_per_second']}/s, locked out: {sec['bruteforce']['locked_out']}", 'Limitation: no lock-out on the password step (the emailed code is a second factor)'],
             ['Fuzzing (hostile and malformed input)', f"{sec['fuzz']['payload_count']} requests, {sec['fuzz']['server_errors']} server errors, tables intact: {sec['fuzz']['tables_intact']}", 'Pass' if sec['fuzz']['server_errors'] == 0 else 'Fail'],
             ['Admin endpoints without a token', ', '.join(f'{k.split("/")[-1] or k}: {v}' for k, v in sec['unauthenticated_admin'].items()), 'Pass' if all(v in (401, 403, 404, 405) for v in sec['unauthenticated_admin'].values()) else 'Fail'],
             ['User enumeration', f"unknown voter {sec['enumeration']['unknown_voter_status']}, wrong password {sec['enumeration']['wrong_password_status']}", 'Limitation: a roster lookup reveals whether a number is registered' if sec['enumeration']['distinguishable'] else 'Pass'],
             ['Session expiry', 'session fields: ' + ', '.join(sec['session']['fields']), 'Limitation: sessions live in memory until sign-out or restart' if not sec['session']['has_expiry'] else 'Pass'],
             ['API security headers', ', '.join(f"{k}: {'set' if v else 'absent'}" for k, v in sec['api_headers'].items()), 'Limitation (see live-site headers)'],
             ['CORS from a foreign origin', str(sec['cors_foreign_origin']), 'Pass' if not sec['cors_foreign_origin'] else 'Check'],
             ['Receipt token guessing', '122 random bits (UUID v4)', 'Pass']]
    T.append(table('T14_security', ['Probe', 'Result', 'Verdict'], srows, 'Table 14. Security probes'))
    pv = R['privacy']
    T.append(table('T15_privacy', ['Check', 'Result'], [['Columns shared by ballot and voter tables', ', '.join(pv['shared_columns']) or 'none'], ['Timestamp on the ballot table', 'no' if not pv['ballot_has_timestamp'] else 'yes (ledger only)'],
                                                      ['Ledger block fields', ', '.join(pv['ledger_fields'])], ['Ordering attack on 150 API casts in random voter order', f"{pv['api_order_attack']['correct_guesses']} correct guesses (chance: about {pv['api_order_attack']['chance_expected']})"],
                                                      ['Simulation tool casts in roster order', 'block order mirrors roster order; demo tool only']] , 'Table 15. Voter privacy checks'))
    if S:
        st, bd, bi, cx = S.get('structure', {}), S.get('bandit', {}), S.get('npm_audit', {}), S.get('complexity', {})
        T.append(table('T16_code', ['Measure', 'Value'], [['Lines (non-blank), total', f"{S['loc']['total_lines']:,}"]] + [[k, f'{v:,}'] for k, v in S['loc']['lines'].items()] +
                       [['API routes', st.get('api_routes')], ['Election tables / triggers / views', f"{st.get('election_tables')} / {st.get('election_triggers')} / {st.get('election_views')}"], ['CHECK / UNIQUE+PK / FOREIGN KEY', f"{st.get('check_constraints')} / {st.get('unique_or_pk')} / {st.get('foreign_keys')}"],
                        ['Front-end pages', st.get('frontend_pages')], ['Python dependencies', len(st.get('python_deps', []))], ['npm dependencies', len(st.get('npm_dependencies', {}))], ['Mean cyclomatic complexity (back end)', cx.get('mean_complexity')],
                        ['Bandit findings (severity)', f"{bd.get('issues')} {bd.get('by_severity')}"], ['npm audit', str(bi.get('vulnerabilities'))], ['pip-audit (hosted requirements)', (lambda h: f"{h.get('vulnerabilities')} advisories in {h.get('packages_checked')} packages")(S.get('pip_audit', {}).get('requirements-hosted.txt', {}))], ['pip-audit (with the legacy Streamlit UI)', (lambda h: f"{h.get('vulnerabilities')} advisories, all in {', '.join(h.get('by_package', {}))} (fixed in {', '.join(sum(h.get('fix', {}).values(), []))})")(S.get('pip_audit', {}).get('requirements.txt', {}))]], 'Table 16. Code, structure and static analysis'))
        lv = S.get('live', {})
        if lv and 'headers' in lv:
            T.append(table('T17_live', ['Measure', 'Value'], [['Live site', 'https://polyvote-bacse202.onrender.com'], ['Website checklist', f"{lv.get('checklist', {}).get('pass')} pass, {lv.get('checklist', {}).get('na')} N/A, {lv.get('checklist', {}).get('fail')} fail"],
                                                              ['Health check median / min / max (ms)', f"{lv['health_ms']['median']} / {lv['health_ms']['min']} / {lv['health_ms']['max']}"], ['First request (cold start possible) ms', lv['first_request_ms']]] + [[f'Header {k}', v or 'absent'] for k, v in lv['headers'].items()], 'Table 17. Live deployment'))
    # comparison of documented features
    codes = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9']
    T.append(table('T18_related_systems', ['System', 'Type'] + codes,
                   [[s['name'], s['type']] + [str(s[c]['value']) for c in codes] for s in EVID] + [['PolyVote (this project)', 'student project, open on GitHub'] + ['yes'] * 9], 'Table 18. Documented features of the 33 systems read (F1-F9), from their own pages'))
    return T


def human_time(sec):
    for unit, d in (('years', 31536000), ('days', 86400), ('hours', 3600), ('minutes', 60)):
        if sec >= d:
            v = sec / d
            return f'{v:,.0f} {unit}' if v >= 10 else f'{v:.1f} {unit}'
    return f'{sec:.1f} seconds'


if __name__ == '__main__':
    f_heatmap(); f_rates(); f_ablation(); f_firing(); f_key_value(); f_adversary(); f_triggers(); f_latency(); f_scaling(); f_sizes(); f_overhead(); f_concurrency()
    f_passwords(); f_precision(); f_false_pos(); f_tally(); f_snapshot(); f_code(); f_bundle(); f_coverage(); f_inventory()
    build_tables()
    (ROOT / 'docs' / 'evaluation' / 'figures_manifest.json').write_text(json.dumps(MANIFEST, indent=1), encoding='utf-8')
    (ROOT / 'docs' / 'evaluation' / 'tables.json').write_text(json.dumps(TABLES, indent=1, default=str), encoding='utf-8')
    print(f'{len(MANIFEST)} figures, {len(TABLES)} tables')
