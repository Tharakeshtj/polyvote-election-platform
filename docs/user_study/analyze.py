"""Summarise the usability study. Standard library only.

    python docs/user_study/analyze.py tasks.csv questionnaire.csv

tasks.csv columns:          participant,group,task,completed,hint_level,seconds,errors,seq
questionnaire.csv columns:  participant,group,sus1..sus10,t1,t2,t3   (SUS items 1-5, trust items 1-5)

A task counts as "unaided" when completed = 1 and hint_level = 0.
"""
import csv
import statistics as st
import sys
from collections import defaultdict


def sus_score(items):
    """Standard SUS: odd items score (x - 1), even items score (5 - x), sum times 2.5."""
    return sum((x - 1) if i % 2 == 0 else (5 - x) for i, x in enumerate(items)) * 2.5


def rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fmt(vals):
    return f'median {st.median(vals):.0f}, range {min(vals):.0f} to {max(vals):.0f}' if vals else 'no data'


def tasks(path):
    by = defaultdict(list)
    for r in rows(path):
        by[(r['group'], r['task'])].append(r)
    print('TASKS')
    print(f"{'group':<14}{'task':<6}{'n':>3}{'done':>6}{'unaided':>9}  {'seconds':<30}{'errors':>7}{'SEQ':>6}")
    for (g, t), rs in sorted(by.items()):
        n = len(rs)
        done = sum(int(r['completed']) for r in rs)
        un = sum(1 for r in rs if int(r['completed']) and int(r['hint_level']) == 0)
        secs = [float(r['seconds']) for r in rs if r['seconds']]
        errs = sum(int(r['errors'] or 0) for r in rs)
        seq = [float(r['seq']) for r in rs if r['seq']]
        print(f"{g:<14}{t:<6}{n:>3}{done:>4}/{n:<2}{un:>5}/{n:<3} {fmt(secs):<30}{errs:>7}{(st.mean(seq) if seq else float('nan')):>6.1f}")


def questionnaire(path):
    by = defaultdict(list)
    for r in rows(path):
        items = [int(r[f'sus{i}']) for i in range(1, 11)]
        by[r['group']].append((sus_score(items), [int(r[k]) for k in ('t1', 't2', 't3')]))
    print('\nSUS AND TRUST')
    for g, v in sorted(by.items()):
        scores = [s for s, _ in v]
        sd = st.stdev(scores) if len(scores) > 1 else 0.0
        print(f'{g}: n={len(v)}  SUS mean {st.mean(scores):.1f} (sd {sd:.1f}, range {min(scores):.1f} to {max(scores):.1f}); '
              f'trust means T1 {st.mean(t[0] for _, t in v):.1f}, T2 {st.mean(t[1] for _, t in v):.1f}, T3 {st.mean(t[2] for _, t in v):.1f}')
    print('SUS about 68 is the usual rough benchmark for an average system; with this n it is a rough read, not a test.')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    tasks(sys.argv[1])
    questionnaire(sys.argv[2])
