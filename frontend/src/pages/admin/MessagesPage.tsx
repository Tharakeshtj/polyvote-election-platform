import { useEffect, useState } from 'react';
import { MessageSquare } from 'lucide-react';
import { adminApi, errorMessage, type ContactMessage } from '../../api';
import { EmptyState, FormError, PageLoading } from '../../components/ui';
import { usePageMeta } from '../../lib/meta';

export default function MessagesPage() {
  usePageMeta('Contact messages | PolyVote');
  const [rows, setRows] = useState<ContactMessage[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { adminApi.messages().then(setRows).catch((e) => setError(errorMessage(e))); }, []);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Contact messages</h1>
          <p>Messages sent through the public contact form, newest first.</p>
        </div>
      </div>
      <FormError message={error} />
      <div className="card">
        {!rows && !error && <PageLoading />}
        {rows?.length === 0 && <EmptyState icon={<MessageSquare />} title="No messages yet">Messages appear here when someone uses the contact form.</EmptyState>}
        {rows && rows.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Received</th><th>From</th><th>Message</th></tr></thead>
              <tbody>
                {rows.map((m) => (
                  <tr key={m.message_id}>
                    <td className="num">{new Date(m.received_at * 1000).toLocaleString()}</td>
                    <td><strong>{m.name}</strong><div className="subtle">{m.email}</div></td>
                    <td style={{ whiteSpace: 'pre-wrap' }}>{m.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
