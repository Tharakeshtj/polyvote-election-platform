import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, Circle, Dices, Mail } from 'lucide-react';
import { adminApi, errorMessage } from '../../../api';
import { Spinner, formatDate, outliers, useToast } from '../../../components/ui';
import type { TabProps } from './ElectionPage';

export default function OverviewTab({ election, reload }: TabProps) {
  const pct = election.voters ? Math.round((election.voted / election.voters) * 100) : 0;
  const base = `/admin/elections/${election.election_id}`;
  const s = election.status;
  // Same three counts the Results tab reconciles: ballots in DB, ledger receipts, voters marked voted.
  const off = outliers([election.ballots, election.ledger_receipts, election.voted]);

  const checklist = [
    { done: election.candidates.length >= 3, label: 'Add at least 3 candidates', to: `${base}/candidates`, hint: `${election.candidates.length} added` },
    { done: election.voters > 0, label: 'Register voters', to: `${base}/voters`, hint: `${election.voters} on roster` },
    { done: s !== 'NOMINATION', label: 'Open voting', hint: s === 'NOMINATION' ? 'Button at top right' : 'Done' },
    { done: s === 'CLOSED', label: 'Close voting', hint: s === 'VOTING' ? `${election.voted} of ${election.voters} voted` : s === 'CLOSED' ? 'Done' : 'After voting' },
    { done: false, label: 'Run the sweep and tally', to: `${base}/results`, hint: s === 'CLOSED' ? 'Ready' : 'Any time' },
  ];

  return (
    <div className="grid-2">
      <div className="stack">
        <section className="card" aria-labelledby="summary-h">
          <div className="card-header"><h2 id="summary-h">Summary</h2></div>
          <dl className="summary">
            <dt>Candidates</dt><dd>{election.candidates.length}</dd>
            <dt>Registered voters</dt><dd>{election.voters}</dd>
            <dt>Voted</dt>
            <dd>
              <div className="row" style={{ justifyContent: 'flex-end', gap: 10 }}>
                <div className="meter" style={{ flex: 1, minWidth: 40, maxWidth: 120 }}><span style={{ width: `${pct}%` }} /></div>
                <span style={{ whiteSpace: 'nowrap' }}>
                  <span style={off.has(2) ? { color: 'var(--attention)' } : undefined}>{election.voted}</span> <span className="subtle">({pct}%)</span>
                </span>
              </div>
            </dd>
            <dt>Ballots in database</dt><dd className={off.has(0) ? 'off' : undefined}>{election.ballots}</dd>
            <dt>Ledger receipts</dt><dd className={off.has(1) ? 'off' : undefined}>{election.ledger_receipts}</dd>
          </dl>
          {off.size > 0 && (
            <div className="card-foot">
              <div className="row" style={{ gap: 8, color: 'var(--attention)' }}>
                <AlertTriangle size={16} />
                <span>Counts don’t agree. <Link to={`${base}/results`}>Run the integrity sweep</Link></span>
              </div>
            </div>
          )}
        </section>

        <section className="card" aria-labelledby="details-h">
          <div className="card-header"><h2 id="details-h">Details</h2></div>
          <dl className="summary">
            <dt>Election ID</dt><dd className="mono">#{election.election_id}</dd>
            <dt>Contact</dt><dd><span className="row" style={{ justifyContent: 'flex-end', gap: 6 }}><Mail size={14} /> {election.admin_contact}</span></dd>
            <dt>Created</dt><dd>{formatDate(election.start_time)}</dd>
            <dt>Scheduled end</dt><dd>{formatDate(election.end_time)}</dd>
          </dl>
        </section>
      </div>

      <div className="stack">
        <section className="card" aria-labelledby="checklist-h">
          <div className="card-header"><h2 id="checklist-h">Checklist</h2></div>
          <div className="list">
            {checklist.map((c) => (
              <div key={c.label} className="list-row" style={{ justifyContent: 'space-between' }}>
                <span className="row" style={{ gap: 10 }}>
                  {c.done ? <CheckCircle2 size={16} color="var(--success)" aria-label="Done" /> : <Circle size={16} color="var(--text-3)" aria-label="To do" />}
                  {c.to ? <Link to={c.to} style={{ color: 'var(--text)', fontWeight: 500 }}>{c.label}</Link> : <span style={{ fontWeight: 500 }}>{c.label}</span>}
                </span>
                <span className="subtle">{c.hint}</span>
              </div>
            ))}
          </div>
        </section>
        {s === 'VOTING' && (
          <SimulateCard electionId={election.election_id} remaining={election.voters - election.voted} canSimulate={election.candidates.length >= 3} reload={reload} />
        )}
      </div>
    </div>
  );
}

function SimulateCard({ electionId, remaining, canSimulate, reload }: { electionId: number; remaining: number; canSimulate: boolean; reload: () => Promise<void> }) {
  const toast = useToast();
  const [count, setCount] = useState(20);
  const [busy, setBusy] = useState(false);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    try {
      const { cast } = await adminApi.simulate(electionId, count);
      toast('success', `Cast ${cast} simulated ballot${cast === 1 ? '' : 's'}.`);
      await reload();
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card" onSubmit={submit} aria-labelledby="sim-h">
      <div className="card-header">
        <h2 id="sim-h" className="section-title"><Dices /> Simulate ballots</h2>
        <span className="subtle">{remaining} yet to vote</span>
      </div>
      <div className="card-body stack-sm">
        <p className="muted">Casts random top-3 ballots for voters who haven’t voted, each sealed in the ledger like a real one.</p>
        <div className="row" style={{ gap: 8 }}>
          <input type="number" className="input num" min={1} max={1000} value={count} onChange={(e) => setCount(Number(e.target.value))} style={{ width: 96 }} aria-label="Ballots to simulate" />
          <button className="btn" disabled={busy || !canSimulate || remaining === 0 || count < 1}>
            {busy && <Spinner />} Simulate
          </button>
        </div>
        {!canSimulate && <span className="hint">Needs at least 3 candidates.</span>}
      </div>
    </form>
  );
}
