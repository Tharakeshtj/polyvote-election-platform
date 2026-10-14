import { useEffect, useState } from 'react';
import { Link2, ShieldAlert, ShieldCheck } from 'lucide-react';
import { adminApi, errorMessage, type ElectionSummary, type LedgerBlock } from '../../api';
import { EmptyState, FormError, PageLoading, formatDate, shortHash } from '../../components/ui';

const PAGE = 50;

export default function LedgerPage() {
  const [elections, setElections] = useState<ElectionSummary[]>([]);
  const [electionId, setElectionId] = useState<number | undefined>();
  const [data, setData] = useState<{ chain_valid: boolean; chain_message: string; blocks: LedgerBlock[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shown, setShown] = useState(PAGE);

  useEffect(() => { adminApi.elections().then(setElections).catch(() => {}); }, []);
  useEffect(() => {
    setData(null);
    setShown(PAGE);
    adminApi.ledger(electionId).then(setData).catch((e) => setError(errorMessage(e)));
  }, [electionId]);

  const names = new Map(elections.map((e) => [e.election_id, e.org_name]));

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Audit ledger</h1>
          <p>One receipt per ballot. Each entry includes the previous entry’s hash, so editing any entry breaks the chain after it.</p>
        </div>
        <select className="select" style={{ width: 'auto', minWidth: 220 }} value={electionId ?? ''} onChange={(e) => setElectionId(e.target.value ? Number(e.target.value) : undefined)} aria-label="Filter by election">
          <option value="">All elections</option>
          {elections.map((e) => <option key={e.election_id} value={e.election_id}>{e.org_name} (#{e.election_id})</option>)}
        </select>
      </div>

      <FormError message={error} />
      <div className="stack">
        {data && (
          <div className={`callout ${data.chain_valid ? 'callout-ok' : 'callout-danger'}`} role="status">
            {data.chain_valid ? <ShieldCheck /> : <ShieldAlert />}
            <div><strong>{data.chain_message}</strong> <span className="muted">Checked across the whole ledger.</span></div>
          </div>
        )}

        <div className="card">
          <div className="card-header">
            <h2>{data ? `${data.blocks.length} receipt${data.blocks.length === 1 ? '' : 's'}` : 'Receipts'}</h2>
            <span className="subtle">Newest first</span>
          </div>
          {!data && !error && <PageLoading />}
          {data?.blocks.length === 0 && <EmptyState icon={<Link2 />} title="No receipts yet">Entries appear here as ballots are cast.</EmptyState>}
          {data && data.blocks.length > 0 && (
            <>
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th className="num">#</th>
                      <th>Recorded</th>
                      <th>Election</th>
                      <th>Ballot token</th>
                      <th>Vote hash</th>
                      <th>Previous → block hash</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.blocks.slice(0, shown).map((b) => (
                      <tr key={b.index}>
                        <td className="num mono">{b.index}</td>
                        <td style={{ whiteSpace: 'nowrap' }}>{formatDate(b.timestamp)}</td>
                        <td>{names.get(b.election_id) ?? `#${b.election_id}`}</td>
                        <td><code title={b.ballot_token}>{shortHash(b.ballot_token, 8)}</code></td>
                        <td><code title={b.vote_data_hash}>{shortHash(b.vote_data_hash, 8)}</code></td>
                        <td style={{ whiteSpace: 'nowrap' }}>
                          <code className="muted" title={b.prev_hash}>{shortHash(b.prev_hash, 6)}</code> → <code title={b.curr_hash}>{shortHash(b.curr_hash, 6)}</code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {shown < data.blocks.length && (
                <div className="pager">
                  <span>Showing {shown} of {data.blocks.length}</span>
                  <button className="btn btn-sm" onClick={() => setShown(shown + PAGE)}>Show {Math.min(PAGE, data.blocks.length - shown)} more</button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
