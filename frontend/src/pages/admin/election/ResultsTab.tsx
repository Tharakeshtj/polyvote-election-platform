import { useState } from 'react';
import { AlertTriangle, Info, Play, ShieldAlert, ShieldCheck, Trophy } from 'lucide-react';
import { adminApi, errorMessage, type IntegrityResult, type TallyResult } from '../../../api';
import { CopyButton, EmptyState, Spinner, outliers, shortHash, useToast } from '../../../components/ui';
import type { TabProps } from './ElectionPage';

export default function ResultsTab({ election }: TabProps) {
  const toast = useToast();
  const [sweep, setSweep] = useState<IntegrityResult | null>(null);
  const [tally, setTally] = useState<TallyResult | null>(null);
  const [busy, setBusy] = useState<'sweep' | 'tally' | null>(null);

  const run = async <T,>(kind: 'sweep' | 'tally', fn: () => Promise<T>, set: (v: T) => void) => {
    setBusy(kind);
    try {
      set(await fn());
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(null);
    }
  };

  const counts = [
    { label: 'Ballots in database', value: election.ballots },
    { label: 'Ledger receipts', value: election.ledger_receipts },
    { label: 'Voters marked as voted', value: election.voted },
  ];
  const off = outliers(counts.map((c) => c.value));
  const mismatch = off.size > 0;
  const anomalies = sweep ? sweep.modified.length + sweep.deleted.length : 0;

  return (
    <div className="stack">
      {election.status !== 'CLOSED' && (
        <div className="callout callout-info">
          <Info />
          <span>Voting {election.status === 'VOTING' ? 'is still open' : 'hasn’t started'}, so results here are provisional.</span>
        </div>
      )}

      <section className="card" aria-labelledby="sweep-h">
        <div className="card-header">
          <div>
            <h2 id="sweep-h">Integrity sweep</h2>
            <p className="subtle">Recomputes each sealed ballot from the database and compares it with its ledger receipt.</p>
          </div>
          <button className="btn btn-primary" disabled={busy !== null} onClick={() => run('sweep', () => adminApi.integrity(election.election_id), setSweep)}>
            {busy === 'sweep' ? <Spinner /> : <ShieldCheck />} Run sweep
          </button>
        </div>
        <div className="reconcile">
          {counts.map((c, i) => (
            <div key={c.label}>
              <div className="subtle">{c.label}</div>
              <div className={`v ${off.has(i) ? 'off' : ''}`}>{c.value}</div>
            </div>
          ))}
        </div>
        <div className="card-body stack">
          {mismatch && (
            <div className="callout callout-warn">
              <AlertTriangle />
              <span>These counts don’t agree. The sweep only checks ballots that have a ledger receipt, so a ballot added straight to the database won’t show up as an anomaly below.</span>
            </div>
          )}

          {!sweep && !mismatch && <p className="muted">Run the sweep to compare every sealed ballot with the database.</p>}
          {sweep && (anomalies === 0 ? (
            <div className="callout callout-ok" role="status">
              <ShieldCheck />
              <div>
                <strong>Sweep passed.</strong>{' '}
                {sweep.message === 'No votes cast yet.' ? 'No ballots have been cast yet.' : 'Every ledger receipt matches its ballot in the database.'}
              </div>
            </div>
          ) : (
            <div className="callout callout-danger" role="alert">
              <ShieldAlert />
              <div>
                <strong>Tampering detected.</strong> {anomalies} ballot{anomalies === 1 ? '' : 's'} no longer match their ledger receipt
                ({sweep.modified.length} modified, {sweep.deleted.length} deleted).
              </div>
            </div>
          ))}
        </div>
        {sweep && anomalies > 0 && (
              <div className="table-wrap" style={{ borderTop: '1px solid var(--border)' }}>
                <table className="table">
                  <thead><tr><th>Ballot token</th><th>Anomaly</th><th>What the ledger shows</th></tr></thead>
                  <tbody>
                    {sweep.modified.map((t) => (
                      <tr key={`m${t}`}>
                        <td><span className="row" style={{ gap: 6 }}><code>{shortHash(t, 8)}</code><CopyButton text={t} label="" /></span></td>
                        <td><span className="label label-danger">Modified</span></td>
                        <td className="muted">The ranks in the database differ from what was sealed.</td>
                      </tr>
                    ))}
                    {sweep.deleted.map((t) => (
                      <tr key={`d${t}`}>
                        <td><span className="row" style={{ gap: 6 }}><code>{shortHash(t, 8)}</code><CopyButton text={t} label="" /></span></td>
                        <td><span className="label label-danger">Deleted</span></td>
                        <td className="muted">A sealed ballot is missing from the database.</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
        )}
      </section>

      <section className="card" aria-labelledby="tally-h">
        <div className="card-header">
          <div>
            <h2 id="tally-h">Instant-runoff tally</h2>
            <p className="subtle">Eliminates the last-place candidate each round until one holds a majority of continuing ballots.</p>
          </div>
          <button className="btn" disabled={busy !== null} onClick={() => run('tally', () => adminApi.tally(election.election_id), setTally)}>
            {busy === 'tally' ? <Spinner /> : <Play />} Count ballots
          </button>
        </div>
        {!tally ? (
          <div className="card-body muted">Count the ballots to see the winner and each elimination round.</div>
        ) : tally.outcome === 'no_votes' ? (
          <EmptyState icon={<Trophy />} title="No ballots yet">Results appear once voters have cast ballots.</EmptyState>
        ) : (
          <>
            <div className="card-body">
              {tally.outcome === 'winner' ? (
                <div className="callout callout-ok" role="status">
                  <Trophy />
                  <div>
                    <strong>{tally.winner}</strong> {election.status === 'CLOSED' ? 'wins' : 'leads'} with a majority in round {tally.rounds.length}.
                    <div className="muted">
                      {tally.rounds.at(-1)!.rows[0].votes} of {tally.rounds.at(-1)!.rows.reduce((n, r) => n + r.votes, 0)} continuing ballots in the final round.
                    </div>
                  </div>
                </div>
              ) : (
                <div className="callout callout-warn"><AlertTriangle /><span>{tally.message}</span></div>
              )}
            </div>
            {tally.rounds.map((r) => {
              const max = Math.max(1, ...r.rows.map((x) => x.votes));
              const final = r.round === tally.rounds.length && tally.outcome === 'winner';
              return (
                <div key={r.round} className="round stack-sm">
                  <div className="spread">
                    <h3>Round {r.round}</h3>
                    {r.eliminated && <span className="label">{r.eliminated} eliminated</span>}
                    {final && <span className="label label-success">Majority reached</span>}
                  </div>
                  <div>
                    {r.rows.map((row, i) => (
                      <div key={row.candidate} className={`round-bar ${final && i === 0 ? 'lead' : ''} ${row.candidate === r.eliminated ? 'out' : ''}`}>
                        <span className="name" title={row.candidate}>{row.candidate}</span>
                        <span className="bar"><span style={{ width: `${(row.votes / max) * 100}%` }} /></span>
                        <span className="votes">{row.votes} <span className="subtle">{row.percentage}</span></span>
                      </div>
                    ))}
                  </div>
                  {r.tie_break && (
                    <p className="hint row" style={{ gap: 6 }}><AlertTriangle size={14} /> Tie for last place: the engine eliminated one by internal order, not by a rule.</p>
                  )}
                </div>
              );
            })}
          </>
        )}
      </section>
    </div>
  );
}
