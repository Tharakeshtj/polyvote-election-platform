# PolyVote: paper-ready results (4 November 2026)

All numbers come from `experiments/results/full/evaluation.json`. Re-run `experiments/full_eval/run_all.py` to regenerate.

## Headline numbers

- In-scope attacks detected by the final design: **28/28** (100.0%); all 31 scenarios: 28/31.
- Review 2 design (plain chain + receipt sweep): 11/31; CRUD with eyeballed counters: 11/31; plain chain only: 6/31; keyed chain only: 9/31; previous final design (no voter seal): 23/31.
- Append-only triggers on the ballot table prevent 8/31 against a writer who cannot drop them; a writer with schema rights removes them.
- False alarms on clean elections: 0 in 399 sweeps over 120 elections. Precision and recall 1.0 for modified, deleted and injected ballots (k = 1, 5, 20).
- Tally agrees with an independent exhaustive-tie-break implementation in 500/500 random elections (66 with a tie path).
- Password hash: PBKDF2-SHA256, 600,000 rounds, 16-byte salt; about 361,996x slower per guess than unsalted SHA-256; verification 477.5 ms.
- At 100,000 ballots: sweep 5,985 ms, chain check 2,731 ms, tally 2,689 ms; roster seal re-computation 1014.23 ms.
- Concurrency 1 to 16 threads: 0 errors; throughput 11.25 to 15.8 casts/s.

## Table: design profiles (copy into the paper)

| Profile | Design | Detected (31) | In scope |
|---|---|---|---|
| P0 | CRUD app: officer compares the counters | 11/31 | 11/28 |
| P1 | CRUD app + automatic count check | 10/31 | 10/28 |
| P2 | Plain hash chain only | 6/31 | 6/28 |
| P3 | Plain chain + receipt sweep (Review 2 design) | 11/31 | 11/28 |
| P4 | Plain chain + full sweep | 24/31 | 24/28 |
| P5 | Keyed chain only | 9/31 | 9/28 |
| P6 | Keyed chain + sweep rules 1-5 (previous final design) | 23/31 | 23/28 |
| P7 | PolyVote final (keyed chain + 6 sweep rules) | 28/31 | 28/28 |

## Table: ablation (leave one detector out)

| Removed | Still detected | Lost |
|---|---|---|
| chain | 21/31 | C6 C10 C19 C20 C21 C22 C27 |
| modified | 26/31 | C1 C2 |
| deleted | 28/31 | - |
| injected | 28/31 | - |
| candidate_seal | 25/31 | C11 C24 C25 |
| count_mismatch | 26/31 | C12 C26 |
| voter_seal | 23/31 | C13 C14 C15 C16 C17 |

## Suggested claim wording

- "Against 31 storage-level attack scenarios, the combination of a keyed hash chain, a reconciling sweep and a keyed voter-roster seal detected every attack by an adversary without the ledger key; no single control did."
- "Emulating the integrity mechanism of plain hash-chained designs on the same scenarios detected 6 of 31, and a typical CRUD application with manual count checking 11 of 31."
- "PolyVote does not provide end-to-end verifiability; voters can check that a ballot is recorded and counted but not its content."
