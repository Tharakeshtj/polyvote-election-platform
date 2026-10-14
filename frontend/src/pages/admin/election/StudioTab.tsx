import { useCallback, useEffect, useMemo, useState } from 'react';
import { Database, Save, Trash2, X } from 'lucide-react';
import { adminApi, errorMessage, type BallotRow, type Candidate, type Voter } from '../../../api';
import { EmptyState, PageLoading, shortHash, useToast } from '../../../components/ui';
import type { TabProps } from './ElectionPage';

interface StudioData { candidates: Candidate[]; voters: Voter[]; ballots: BallotRow[] }
const BALLOTS_PER_PAGE = 15;
const VOTERS_PER_PAGE = 20;
const ORDINAL = ['1st', '2nd', '3rd'];

export default function StudioTab({ election, reload }: TabProps) {
  const toast = useToast();
  const id = election.election_id;
  const [data, setData] = useState<StudioData | null>(null);

  const load = useCallback(() => {
    adminApi.studio(id).then(setData).catch((e) => toast('error', errorMessage(e)));
  }, [id, toast]);
  useEffect(load, [load]);

  const mutate = async (fn: () => Promise<unknown>, message: string) => {
    try {
      await fn();
      toast('success', message);
    } catch (e) {
      toast('error', errorMessage(e));
    }
    load();
    reload();
  };

  if (!data) return <PageLoading />;

  return (
    <div className="stack">
      <div className="callout callout-warn">
        <Database />
        <div>
          <strong>Tamper sandbox: simulated raw database access.</strong>
          <p className="muted">
            In production this screen wouldn't exist. It stands in for the direct access a DBA has through tools like pgAdmin or DBeaver.
            Edits apply immediately and bypass all app rules, which is exactly what the integrity sweep on the Results tab is meant to catch.
          </p>
        </div>
      </div>

      <CandidatesTable rows={data.candidates} onSave={(c, name, platform) =>
        mutate(() => adminApi.studioCandidate(id, c.candidate_id, name, platform), `Candidate #${c.candidate_id} updated.`)} />

      <VotersTable rows={data.voters}
        onSave={(v, reg) => mutate(() => adminApi.studioVoter(id, v.participation_id, reg), `Voter #${v.participation_id} updated.`)}
        onDrop={(v) => mutate(() => adminApi.studioDropVoter(id, v.participation_id), `${v.student_reg_no} dropped from the roster.`)} />

      <BallotsTable rows={data.ballots} candidates={data.candidates}
        onReassign={(b, cid) => mutate(() => adminApi.studioBallot(id, b.ballot_token, b.preference_rank, cid), 'Ballot rank reassigned.')}
        onDeleteRank={(b) => mutate(() => adminApi.studioDeleteRank(id, b.ballot_token, b.preference_rank), `Rank ${b.preference_rank} deleted.`)}
        onDeleteBallot={(token) => mutate(() => adminApi.studioDeleteBallot(id, token), 'Ballot deleted.')} />
    </div>
  );
}

function CandidatesTable({ rows, onSave }: { rows: Candidate[]; onSave: (c: Candidate, name: string, platform: string) => void }) {
  return (
    <div className="card">
      <div className="card-header">
        <h2><code>CANDIDATE</code> table</h2>
        <span className="subtle">Display names aren't covered by the ledger seal.</span>
      </div>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th style={{ width: 80 }}>ID</th><th>name</th><th>platform_statement</th><th /></tr></thead>
          <tbody>{rows.map((c) => <CandidateRow key={`${c.candidate_id}:${c.name}:${c.platform_statement}`} c={c} onSave={onSave} />)}</tbody>
        </table>
      </div>
    </div>
  );
}

function CandidateRow({ c, onSave }: { c: Candidate; onSave: (c: Candidate, name: string, platform: string) => void }) {
  const [name, setName] = useState(c.name);
  const [platform, setPlatform] = useState(c.platform_statement ?? '');
  const dirty = name !== c.name || platform !== (c.platform_statement ?? '');
  return (
    <tr>
      <td className="mono">{c.candidate_id}</td>
      <td><input className="input input-sm" value={name} onChange={(e) => setName(e.target.value)} aria-label="Candidate name" /></td>
      <td><input className="input input-sm" value={platform} onChange={(e) => setPlatform(e.target.value)} aria-label="Platform" /></td>
      <td className="num"><button className="btn btn-sm btn-primary" disabled={!dirty || !name.trim()} onClick={() => onSave(c, name, platform)}><Save /> Save</button></td>
    </tr>
  );
}

function VotersTable({ rows, onSave, onDrop }: { rows: Voter[]; onSave: (v: Voter, reg: string) => void; onDrop: (v: Voter) => void }) {
  const [page, setPage] = useState(0);
  const pages = Math.max(1, Math.ceil(rows.length / VOTERS_PER_PAGE));
  const visible = rows.slice(page * VOTERS_PER_PAGE, (page + 1) * VOTERS_PER_PAGE);
  return (
    <div className="card">
      <div className="card-header">
        <h2><code>VOTER_PARTICIPATION</code> table</h2>
        <span className="subtle">{rows.length} rows</span>
      </div>
      {rows.length === 0 ? <EmptyState icon={<Database />} title="No rows" /> : (
        <>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th style={{ width: 120 }}>participation_id</th><th>student_reg_no</th><th>has_voted</th><th /></tr></thead>
              <tbody>{visible.map((v) => <VoterRow key={`${v.participation_id}:${v.student_reg_no}`} v={v} onSave={onSave} onDrop={onDrop} />)}</tbody>
            </table>
          </div>
          {pages > 1 && (
            <div className="pager">
              <span>Page {page + 1} of {pages}</span>
              <div className="row" style={{ gap: 6 }}>
                <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
                <button className="btn btn-sm" disabled={page >= pages - 1} onClick={() => setPage(page + 1)}>Next</button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function VoterRow({ v, onSave, onDrop }: { v: Voter; onSave: (v: Voter, reg: string) => void; onDrop: (v: Voter) => void }) {
  const [reg, setReg] = useState(v.student_reg_no);
  return (
    <tr>
      <td className="mono">{v.participation_id}</td>
      <td><input className="input input-sm input-mono" value={reg} onChange={(e) => setReg(e.target.value)} aria-label="Registration number" style={{ maxWidth: 220 }} /></td>
      <td className="mono">{v.has_voted}</td>
      <td className="num">
        <div className="row" style={{ gap: 4, justifyContent: 'flex-end' }}>
          <button className="btn btn-sm" disabled={reg === v.student_reg_no || !reg.trim()} onClick={() => onSave(v, reg)}><Save /> Save</button>
          <button className="btn btn-sm btn-ghost icon-btn" aria-label={`Drop ${v.student_reg_no}`} title="DELETE row" onClick={() => onDrop(v)}><Trash2 /></button>
        </div>
      </td>
    </tr>
  );
}

function BallotsTable({ rows, candidates, onReassign, onDeleteRank, onDeleteBallot }: {
  rows: BallotRow[]; candidates: Candidate[];
  onReassign: (b: BallotRow, cid: number) => void; onDeleteRank: (b: BallotRow) => void; onDeleteBallot: (token: string) => void;
}) {
  const [page, setPage] = useState(0);
  const ballots = useMemo(() => {
    const map = new Map<string, BallotRow[]>();
    for (const r of rows) map.set(r.ballot_token, [...(map.get(r.ballot_token) ?? []), r]);
    return [...map.entries()];
  }, [rows]);
  const pages = Math.max(1, Math.ceil(ballots.length / BALLOTS_PER_PAGE));
  useEffect(() => { if (page >= pages) setPage(pages - 1); }, [page, pages]);
  const visible = ballots.slice(page * BALLOTS_PER_PAGE, (page + 1) * BALLOTS_PER_PAGE);

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2><code>BALLOT_RANKS</code> table</h2>
          <p className="subtle" style={{ marginTop: 2 }}>Voter identities are decoupled: ballots are keyed by an anonymous token.</p>
        </div>
        <span className="subtle">{ballots.length} ballots · {rows.length} rows</span>
      </div>
      {ballots.length === 0 ? <EmptyState icon={<Database />} title="No ballots cast" /> : (
        <>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>ballot_token</th><th>Ranks (candidate_id by preference_rank)</th><th /></tr></thead>
              <tbody>
                {visible.map(([token, ranks]) => (
                  <tr key={token}>
                    <td><code title={token}>{shortHash(token, 8)}</code></td>
                    <td>
                      <div className="ballot-ranks">
                        {ranks.map((b) => (
                          <div key={b.preference_rank} className="row" style={{ gap: 2 }}>
                            <select
                              className="select select-sm"
                              value={b.candidate_id}
                              onChange={(e) => onReassign(b, Number(e.target.value))}
                              aria-label={`Rank ${b.preference_rank} candidate`}
                            >
                              {candidates.map((c) => (
                                <option key={c.candidate_id} value={c.candidate_id}>{ORDINAL[b.preference_rank - 1]}: {c.name}</option>
                              ))}
                            </select>
                            <button className="btn btn-ghost icon-btn btn-sm" title="DELETE this rank row" aria-label={`Delete rank ${b.preference_rank}`} onClick={() => onDeleteRank(b)}><X /></button>
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="num">
                      <button className="btn btn-sm btn-ghost" onClick={() => onDeleteBallot(token)}><Trash2 /> Delete ballot</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {pages > 1 && (
            <div className="pager">
              <span>Page {page + 1} of {pages}</span>
              <div className="row" style={{ gap: 6 }}>
                <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
                <button className="btn btn-sm" disabled={page >= pages - 1} onClick={() => setPage(page + 1)}>Next</button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
