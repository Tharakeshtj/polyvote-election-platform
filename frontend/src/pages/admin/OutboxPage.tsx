import { useEffect, useState } from 'react';
import { Inbox, Mail, ShieldCheck, TriangleAlert } from 'lucide-react';
import { adminApi, errorMessage, type OutboxEntry } from '../../api';
import { CopyButton, EmptyState, FormError, PageLoading } from '../../components/ui';

type OtpStatus = Awaited<ReturnType<typeof adminApi.otpStatus>>;

export default function OutboxPage() {
  const [status, setStatus] = useState<OtpStatus | null>(null);
  const [rows, setRows] = useState<OutboxEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminApi.otpStatus().then(setStatus).catch((e) => setError(errorMessage(e)));
    const load = () => adminApi.otpOutbox().then(setRows).catch((e) => setError(errorMessage(e)));
    load();
    const t = window.setInterval(load, 3000);
    return () => window.clearInterval(t);
  }, []);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Mail outbox</h1>
          <p>Every verification code the system has issued. Codes appear here as plain text for ten minutes only and are never written to the database.</p>
        </div>
      </div>

      <FormError message={error} />
      <div className="stack">
        {status && (
          <div className={`callout ${status.required ? 'callout-ok' : 'callout-info'}`} role="status">
            {status.required ? <ShieldCheck /> : <TriangleAlert />}
            <div>
              <strong>{status.required ? 'Email verification is on.' : 'Email verification is off.'}</strong>{' '}
              <span className="muted">
                {status.required ? '' : 'Set OTP_REQUIRED=true in .env and restart the server to require it at sign-in. '}
                {status.smtp_configured ? `Real email is sent from ${status.sender} via ${status.smtp_host}.` : 'SMTP is not configured, so codes are shown here only (set SMTP_USER and SMTP_PASS in .env to send real email).'}
              </span>
            </div>
          </div>
        )}

        <div className="card">
          <div className="card-header">
            <h2>Recent codes</h2>
            <span className="subtle">Refreshes every few seconds</span>
          </div>
          {!rows && !error && <PageLoading />}
          {rows?.length === 0 && <EmptyState icon={<Inbox />} title="Nothing sent yet">A row appears when a voter signs in with the right password.</EmptyState>}
          {rows && rows.length > 0 && (
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Time</th><th>Election</th><th>Voter</th><th>Sent to</th><th>Code</th><th>Delivery</th></tr></thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={`${r.sent_at}-${i}`}>
                      <td className="num">{new Date(r.sent_at * 1000).toLocaleTimeString()}</td>
                      <td className="num">#{r.election_id}</td>
                      <td className="mono">{r.reg_no}</td>
                      <td className="mono"><span className="row" style={{ gap: 6 }}><Mail size={14} />{r.email}</span></td>
                      <td>
                        {r.code ? <span className="row" style={{ gap: 6 }}><code style={{ fontSize: 16, letterSpacing: 2 }}>{r.code}</code><CopyButton text={r.code} label="" /></span>
                          : <span className="subtle">{r.expired ? 'expired' : 'hidden'}</span>}
                      </td>
                      <td>
                        <span className={`label ${r.status === 'sent' ? 'label-success' : r.status.startsWith('failed') ? 'label-danger' : ''}`}>{r.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
