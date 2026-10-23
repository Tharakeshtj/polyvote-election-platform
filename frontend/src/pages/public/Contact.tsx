import { useState, type FormEvent } from 'react';
import { CheckCircle2, Send } from 'lucide-react';
import { Breadcrumbs } from '../../components/Breadcrumbs';
import { errorMessage, publicApi } from '../../api';
import { FormError, Spinner } from '../../components/ui';
import { usePageMeta } from '../../lib/meta';

export default function Contact() {
  usePageMeta('Contact PolyVote', 'Send a message to the PolyVote team about the project, a bug or an election you want to run.');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [website, setWebsite] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await publicApi.contact({ name, email, message, website });
      setSent(true);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="narrow">
      <Breadcrumbs items={[{ label: 'Home', to: '/' }, { label: 'Contact' }]} />
      <header className="page-intro">
        <h1>Contact us</h1>
        <p>Questions about the project, a bug to report, or an election you would like to run? Send a message and the team will see it in the admin console.</p>
      </header>
      {sent ? (
        <div className="callout callout-ok" role="status">
          <CheckCircle2 />
          <div><strong>Message sent.</strong> Thank you. We will reply to the address you gave.</div>
        </div>
      ) : (
        <form className="card" onSubmit={submit}>
          <div className="card-body stack">
            <div className="field">
              <label htmlFor="c-name">Your name</label>
              <input id="c-name" className="input" required maxLength={100} autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="c-email">Email address</label>
              <input id="c-email" type="email" className="input" required maxLength={254} autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="c-msg">Message</label>
              <textarea id="c-msg" className="input" required minLength={10} maxLength={2000} rows={6} value={message} onChange={(e) => setMessage(e.target.value)} />
              <span className="hint">{message.length} / 2000</span>
            </div>
            {/* Honeypot: hidden from people and screen readers; bots tend to fill it in. */}
            <div aria-hidden="true" style={{ position: 'absolute', left: '-9999px', height: 0, overflow: 'hidden' }}>
              <label htmlFor="c-web">Website</label>
              <input id="c-web" tabIndex={-1} autoComplete="off" value={website} onChange={(e) => setWebsite(e.target.value)} />
            </div>
            <FormError message={error} />
            <button className="btn btn-primary" disabled={busy || !name.trim() || !email.trim() || message.trim().length < 10}>
              {busy ? <Spinner /> : <Send />} Send message
            </button>
          </div>
          <div className="card-foot subtle">We store your name, email and message only to answer you. See the <a href="/privacy">privacy policy</a>.</div>
        </form>
      )}
    </div>
  );
}
