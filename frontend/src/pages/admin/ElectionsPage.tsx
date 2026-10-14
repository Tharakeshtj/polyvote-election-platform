import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Vote } from 'lucide-react';
import { adminApi, errorMessage, type ElectionSummary } from '../../api';
import { EmptyState, FormError, PageLoading, StatusBadge } from '../../components/ui';

export default function ElectionsPage() {
  const navigate = useNavigate();
  const [elections, setElections] = useState<ElectionSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminApi.elections().then(setElections).catch((e) => setError(errorMessage(e)));
  }, []);

  const open = elections?.filter((e) => e.status === 'VOTING').length ?? 0;
  const go = (id: number) => navigate(`/admin/elections/${id}`);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Elections</h1>
          <p>Each organisation’s election moves through nominations, voting and close.</p>
        </div>
        <Link to="/admin/elections/new" className="btn btn-primary"><Plus /> New election</Link>
      </div>

      <FormError message={error} />

      <div className="card">
        <div className="card-header">
          <h2>{elections ? `${elections.length} election${elections.length === 1 ? '' : 's'}` : 'Elections'}</h2>
          {elections && elections.length > 0 && <span className="subtle">{open} open for voting</span>}
        </div>
        {!elections && !error && <PageLoading rows={3} />}
        {elections?.length === 0 && (
          <EmptyState icon={<Vote />} title="No elections yet">
            Create an election to add candidates and register voters.
            <div style={{ marginTop: 16 }}>
              <Link to="/admin/elections/new" className="btn btn-primary"><Plus /> New election</Link>
            </div>
          </EmptyState>
        )}
        {elections && elections.length > 0 && (
          <div className="table-wrap">
            <table className="table table-clickable">
              <thead>
                <tr>
                  <th>Organisation</th>
                  <th>Status</th>
                  <th className="num">Candidates</th>
                  <th style={{ minWidth: 200 }}>Turnout</th>
                  <th className="num">Ballots</th>
                </tr>
              </thead>
              <tbody>
                {elections.map((e) => {
                  const pct = e.voters ? Math.round((e.voted / e.voters) * 100) : 0;
                  return (
                    <tr key={e.election_id} tabIndex={0} onClick={() => go(e.election_id)} onKeyDown={(ev) => { if (ev.key === 'Enter') go(e.election_id); }}>
                      <td>
                        <Link to={`/admin/elections/${e.election_id}`} className="cell-title" onClick={(ev) => ev.stopPropagation()}>{e.org_name}</Link>
                        <div className="subtle">#{e.election_id} · {e.admin_contact}</div>
                      </td>
                      <td><StatusBadge status={e.status} /></td>
                      <td className="num">{e.candidates}</td>
                      <td>
                        <div className="row" style={{ gap: 10 }}>
                          <div className="meter" style={{ flex: 1 }}><span style={{ width: `${pct}%` }} /></div>
                          <span className="subtle num" style={{ minWidth: 76, textAlign: 'right' }}>{e.voted}/{e.voters} · {pct}%</span>
                        </div>
                      </td>
                      <td className="num">{e.ballots}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
