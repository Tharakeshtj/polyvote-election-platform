import { useEffect, useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { EyeOff, ListOrdered, ReceiptText, Vote } from 'lucide-react';
import { errorMessage, publicApi, type PublicElection } from '../../api';
import { EmptyState, FormError, PageLoading, StatusBadge } from '../../components/ui';

export default function Landing() {
  const navigate = useNavigate();
  const [elections, setElections] = useState<PublicElection[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState('');

  useEffect(() => {
    publicApi.elections().then(setElections).catch((e) => setError(errorMessage(e)));
  }, []);

  const order = { VOTING: 0, NOMINATION: 1, CLOSED: 2 } as const;
  const sorted = elections && [...elections].sort((a, b) => order[a.status] - order[b.status] || b.election_id - a.election_id);
  const openCount = elections?.filter((e) => e.status === 'VOTING').length ?? 0;

  const checkReceipt = (ev: FormEvent) => {
    ev.preventDefault();
    if (token.trim()) navigate(`/verify?token=${encodeURIComponent(token.trim())}`);
  };

  return (
    <div className="medium">
      <header className="page-intro">
        <h1>Vote in an election</h1>
        <p>Sign in with your registration number, rank your top three candidates, and keep the receipt token you get at the end.</p>
      </header>

      <section className="card" aria-labelledby="elections-heading">
        <div className="card-header">
          <h2 id="elections-heading">Elections</h2>
          {elections && <span className="subtle">{openCount} open for voting</span>}
        </div>
        {error && <div className="card-body"><FormError message={error} /></div>}
        {!sorted && !error && <PageLoading rows={3} />}
        {sorted?.length === 0 && (
          <EmptyState icon={<Vote />} title="No elections yet">When an election officer sets one up, it will appear here.</EmptyState>
        )}
        {sorted?.map((e) => (
          <div key={e.election_id} className="election-row">
            <span className="er-status"><StatusBadge status={e.status} /></span>
            <div className="er-main">
              <strong>{e.org_name}</strong>
              <span className="subtle">Election #{e.election_id} · {e.candidates} candidate{e.candidates === 1 ? '' : 's'}</span>
            </div>
            {e.status === 'VOTING' ? (
              <Link to={`/vote/${e.election_id}`} className="btn btn-primary">Vote</Link>
            ) : (
              <span className="subtle">{e.status === 'NOMINATION' ? 'Not open yet' : 'Voting ended'}</span>
            )}
          </div>
        ))}
      </section>

      <form className="card card-pad stack-sm" style={{ marginTop: 16 }} onSubmit={checkReceipt}>
        <label htmlFor="receipt" className="label-text">Already voted? Check your receipt</label>
        <div className="row" style={{ gap: 8 }}>
          <input id="receipt" className="input input-mono" placeholder="Paste your receipt token" value={token} onChange={(e) => setToken(e.target.value)} />
          <button className="btn" disabled={!token.trim()}>Check</button>
        </div>
      </form>

      <section className="how" aria-label="How PolyVote handles your ballot">
        <div>
          <h3><ListOrdered /> Ranked ballots</h3>
          <p>You rank three candidates. If your first choice is eliminated, your vote moves to your next choice.</p>
        </div>
        <div>
          <h3><EyeOff /> Separate from your identity</h3>
          <p>Your registration number marks you as voted. The ballot itself is stored under an anonymous token.</p>
        </div>
        <div>
          <h3><ReceiptText /> A receipt you can check</h3>
          <p>Each ballot gets a sealed entry in a hash-chained ledger. Your token shows whether it's still counted.</p>
        </div>
      </section>
    </div>
  );
}
