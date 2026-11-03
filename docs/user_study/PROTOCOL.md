# PolyVote usability study: protocol

Status: draft for the guide's approval. Nothing here has been run; there are no results.

## 1. Purpose

The evaluation dossier measures detection, correctness and performance. It does not measure whether people can use the system. This study answers three questions:

1. **Voters:** can a first-time voter sign in, rank candidates, enter the emailed code, cast a ballot and understand the receipt, without help?
2. **Administrators:** can a first-time administrator create an election, add voters, close it, read the result and run the integrity check?
3. **Understanding of the integrity check:** after seeing a tampered election, do participants understand what the warning says and what to do?

## 2. Design

Within-session, task-based moderated test, about 25 minutes per person. No control group. Results are descriptive; with this sample size they are not claims of statistical significance.

| Group | Target n | Who |
|---|---|---|
| Voter | 12 to 15 | Students and staff who have never used PolyVote |
| Administrator | 5 to 8 | Club or class representatives who have organised any vote |

Recruit people who are not on the project team. Do not recruit the guide's own students for the guide's evaluation of them. Record year and prior voting-tool experience only; no names in the data.

## 3. Measures

Per task: completed without help (yes/no), completed with a hint (yes/no), time in seconds, number of wrong clicks or error messages, and the Single Ease Question (SEQ, 1 to 7).

After the session: the System Usability Scale (SUS, 10 items, score 0 to 100), three trust items (1 to 5), and two open questions.

Reported with n and ranges; SUS is read against the published benchmark of about 68 as an average score, and we say it is a rough benchmark.

## 4. Procedure

1. Read the consent form aloud; the participant signs or gives verbal consent that the moderator records on the data sheet (yes/no only).
2. Give the participant the demo link and the task cards (`TASKS.md`), one at a time. The moderator says nothing about how to do the task. Think-aloud is encouraged.
3. After each task, ask the SEQ.
4. After the last task, the participant fills in `QUESTIONNAIRE.md`.
5. Debrief and thank.

The moderator records time, help and errors on the data sheet (`data_template.csv`). If the participant is stuck for 2 minutes, give hint level 1 (point at the area); at 3 minutes, hint level 2 (say what to click) and mark the task as "with hint".

## 5. Setup

- Use the demo copy only (`https://polyvote-bacse202.onrender.com`), reset to the sample election before each participant (admin Settings, factory reset).
- Voters use the sample voter list and an email address of their own **only if** they agree; otherwise use the on-screen demo code, which the demo shows by design. Do not collect real email addresses in the data sheet.
- Admin tasks use the public demo admin account shown on the demo page. Participants never enter a real password anywhere.
- The first visit after idle takes about a minute on the free plan; open the site before the session starts.
- Screen recording only with explicit consent; otherwise take notes.

## 6. Ethics and data handling

- Participation is voluntary and can stop at any time without giving a reason.
- No personal data in the dataset: participant IDs P01, P02, ...; the consent record is kept separately from the data sheet.
- Before starting, get the guide's written approval, and check whether the institution requires an ethics or committee review for studies with human participants. We have not checked; do this first.
- Data are kept in this repository only as anonymous rows.

## 7. Analysis

`analyze.py` reads `tasks.csv` (columns as in `data_template.csv`) and `questionnaire.csv` (SUS items 1 to 10 and trust items T1 to T3 per participant) and prints completion rates, median and range of times, errors, SEQ means, SUS scores (with the standard scoring) and trust means, by group. It uses only the Python standard library.

## 8. What the study cannot show

- It does not show the system is usable by the general public; the sample is students and staff of one institution.
- It does not test coercion, vote selling or real-election stakes.
- Participants know they are being observed; times and errors will be better or worse than in real use.

## 9. Schedule (suggested)

| Step | Time |
|---|---|
| Guide's approval and ethics check | 1 to 3 days |
| Pilot with 2 people, fix the task cards | 1 day |
| Sessions | 3 to 5 days |
| Analysis and write-up (add as Section "User study" to the paper) | 2 days |
