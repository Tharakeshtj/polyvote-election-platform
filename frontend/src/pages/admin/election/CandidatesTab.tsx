import { useState, type FormEvent } from 'react';
import { Lock, Plus, Sparkles, Trash2, UserSquare2 } from 'lucide-react';
import { adminApi, errorMessage, type Candidate } from '../../../api';
import { Avatar, ConfirmDialog, EmptyState, Spinner, useToast } from '../../../components/ui';
import type { TabProps } from './ElectionPage';

export default function CandidatesTab({ election, reload }: TabProps) {
  const toast = useToast();
  const editable = election.status === 'NOMINATION';
  const [name, setName] = useState('');
  const [platform, setPlatform] = useState('');
  const [busy, setBusy] = useState<'add' | 'seed' | 'delete' | null>(null);
  const [removing, setRemoving] = useState<Candidate | null>(null);
  const showVotes = election.status !== 'NOMINATION';
  const maxFirst = Math.max(1, ...election.candidates.map((c) => c.first_preferences));

  const run = async (kind: 'add' | 'seed' | 'delete', fn: () => Promise<string>) => {
    setBusy(kind);
    try {
      toast('success', await fn());
      await reload();
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(null);
    }
  };

  const add = (ev: FormEvent) => {
    ev.preventDefault();
    run('add', async () => {
      await adminApi.addCandidate(election.election_id, name, platform);
      setName('');
      setPlatform('');
      return `${name} added to the ballot.`;
    });
  };

  return (
    <div className="grid-2" style={{ gridTemplateColumns: editable ? 'minmax(0, 1.4fr) minmax(0, 1fr)' : '1fr' }}>
      <div className="card">
        <div className="card-header">
          <h2>On the ballot</h2>
          <span className="subtle">{election.candidates.length} candidate{election.candidates.length === 1 ? '' : 's'}</span>
        </div>
        {election.candidates.length === 0 ? (
          <EmptyState icon={<UserSquare2 />} title="No candidates yet">Add candidates manually or seed the demo list.</EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  {showVotes && <th style={{ minWidth: 160 }}>1st preferences</th>}
                  {editable && <th />}
                </tr>
              </thead>
              <tbody>
                {election.candidates.map((c) => (
                  <tr key={c.candidate_id}>
                    <td>
                      <div className="row">
                        <Avatar name={c.name} />
                        <div>
                          <span className="cell-title">{c.name}</span>
                          <div className="subtle">{c.platform_statement || 'No platform statement'} · ID {c.candidate_id}</div>
                        </div>
                      </div>
                    </td>
                    {showVotes && (
                      <td>
                        <div className="row" style={{ gap: 10 }}>
                          <div className="meter neutral" style={{ flex: 1 }}><span style={{ width: `${(c.first_preferences / maxFirst) * 100}%` }} /></div>
                          <span className="num" style={{ minWidth: 28, textAlign: 'right' }}>{c.first_preferences}</span>
                        </div>
                      </td>
                    )}
                    {editable && (
                      <td className="num">
                        <button className="btn btn-ghost icon-btn" aria-label={`Remove ${c.name}`} onClick={() => setRemoving(c)}><Trash2 /></button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {editable ? (
        <div className="stack">
          <form className="card" onSubmit={add}>
            <div className="card-header"><h2>Add a candidate</h2></div>
            <div className="card-body stack">
              <div className="field">
                <label htmlFor="cn">Full name</label>
                <input id="cn" className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Priya Menon" />
              </div>
              <div className="field">
                <label htmlFor="cp">Platform</label>
                <input id="cp" className="input" value={platform} onChange={(e) => setPlatform(e.target.value)} placeholder="One line voters will see" />
              </div>
              <button className="btn btn-primary" disabled={!name.trim() || busy !== null}>{busy === 'add' ? <Spinner /> : <Plus />} Add candidate</button>
            </div>
          </form>
          <div className="card card-pad stack-sm">
            <h2 className="section-title"><Sparkles /> Demo candidates</h2>
            <p className="muted">Adds up to 5 sample candidates (skips any already on the ballot).</p>
            <button
              className="btn" style={{ alignSelf: 'flex-start' }} disabled={busy !== null}
              onClick={() => run('seed', async () => {
                const { added } = await adminApi.seedCandidates(election.election_id, 5);
                return added ? `Added ${added} demo candidate${added === 1 ? '' : 's'}.` : 'All demo candidates are already on the ballot.';
              })}
            >
              {busy === 'seed' && <Spinner />} Seed demo candidates
            </button>
          </div>
        </div>
      ) : (
        <div className="callout callout-info" style={{ gridColumn: '1 / -1', order: -1 }}>
          <Lock />
          <span>The ballot is locked because voting has {election.status === 'VOTING' ? 'opened' : 'ended'}. Candidate names can still be corrected in DB Studio.</span>
        </div>
      )}

      <ConfirmDialog
        open={removing !== null}
        busy={busy === 'delete'}
        tone="danger"
        title={`Remove ${removing?.name}?`}
        confirmLabel="Remove candidate"
        body={<p>They'll be taken off the ballot. You can add them again before voting opens.</p>}
        onCancel={() => setRemoving(null)}
        onConfirm={() => {
          const c = removing!;
          run('delete', async () => {
            await adminApi.deleteCandidate(election.election_id, c.candidate_id);
            return `${c.name} removed.`;
          }).then(() => setRemoving(null));
        }}
      />
    </div>
  );
}
