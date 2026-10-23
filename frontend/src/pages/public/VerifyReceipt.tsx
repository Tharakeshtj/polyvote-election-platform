import { useEffect, useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, SearchCheck, XCircle } from 'lucide-react';
import { errorMessage, publicApi, type Receipt } from '../../api';
import { FormError, Spinner, formatDate } from '../../components/ui';
import { Breadcrumbs } from '../../components/Breadcrumbs';
import { usePageMeta } from '../../lib/meta';

export default function VerifyReceipt() {
  usePageMeta('Check your ballot receipt | PolyVote', 'Paste your receipt token to see whether your ballot is sealed in the audit ledger and still counted.');
  const [params, setParams] = useSearchParams();
  const [token, setToken] = useState(params.get('token') ?? '');
  const [result, setResult] = useState<Receipt | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const check = async (value: string) => {
    if (!value.trim()) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await publicApi.receipt(value));
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    const initial = params.get('token');
    if (initial) check(initial);
  }, []);

  const submit = (ev: FormEvent) => {
    ev.preventDefault();
    setParams(token.trim() ? { token: token.trim() } : {}, { replace: true });
    check(token);
  };

  return (
    <div className="medium">
      <Breadcrumbs items={[{ label: 'Home', to: '/' }, { label: 'Check receipt' }]} />
      <header className="page-intro">
        <h1>Check a receipt</h1>
        <p>Paste the token you got after voting to confirm your ballot is in the ledger and still part of the count.</p>
      </header>

      <form className="card card-pad stack-sm" onSubmit={submit}>
        <label htmlFor="token" className="label-text">Receipt token</label>
        <div className="row" style={{ gap: 8 }}>
          <input
            id="token" className="input input-mono" placeholder="9c0cf1e0-5409-45ac-9a97-e488dceef03a" autoFocus
            value={token} onChange={(e) => setToken(e.target.value)}
          />
          <button className="btn btn-primary" disabled={busy || !token.trim()}>
            {busy ? <Spinner /> : <SearchCheck />}
            Check
          </button>
        </div>
        <FormError message={error} />
      </form>

      {result && !result.found && (
        <div className="callout callout-danger" style={{ marginTop: 16 }}>
          <XCircle />
          <div>
            <strong>No ledger entry matches this token.</strong>
            <p className="muted">Check for typos. A token is 36 characters, including the dashes.</p>
          </div>
        </div>
      )}

      {result?.found && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-body stack">
            <div className={`callout ${result.in_tally ? 'callout-ok' : 'callout-warn'}`}>
              {result.in_tally ? <CheckCircle2 /> : <AlertTriangle />}
              <div>
                <strong>{result.in_tally ? 'Recorded and counted.' : 'Recorded, but missing from the count.'}</strong>
                <p className="muted">
                  {result.in_tally
                    ? 'The ledger holds a sealed receipt for this ballot, and the ballot is present in the election database.'
                    : 'The ledger proves this ballot was cast, but it no longer appears in the database. Report this to the election officers.'}
                </p>
              </div>
            </div>
            <dl className="kv">
              <dt>Election</dt><dd>{result.org_name ?? '—'} <span className="subtle">#{result.election_id}</span></dd>
              <dt>Ledger block</dt><dd className="mono">#{result.block_index}</dd>
              <dt>Recorded</dt><dd>{formatDate(result.timestamp)}</dd>
              <dt>Block hash</dt><dd className="mono">{result.block_hash}</dd>
            </dl>
          </div>
        </div>
      )}
    </div>
  );
}
