import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { adminApi, errorMessage } from '../../api';
import { FormError, Spinner, useToast } from '../../components/ui';

export default function NewElectionPage() {
  const toast = useToast();
  const navigate = useNavigate();
  const [org, setOrg] = useState('');
  const [contact, setContact] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { election_id } = await adminApi.createElection(org.trim(), contact.trim());
      toast('success', `Election created for ${org.trim()}.`);
      navigate(`/admin/elections/${election_id}/candidates`);
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  };

  return (
    <div style={{ maxWidth: 560 }}>
      <div className="crumbs"><Link to="/admin">Elections</Link><ChevronRight /> <span>New</span></div>
      <div className="page-head">
        <div>
          <h1>New election</h1>
          <p>It starts in the nominations phase, so you can add candidates and voters before anyone votes.</p>
        </div>
      </div>
      <form className="card" onSubmit={submit}>
        <div className="card-body stack">
          <div className="field">
            <label htmlFor="org">Organisation name</label>
            <input id="org" className="input" placeholder="Computer Science Society" value={org} onChange={(e) => setOrg(e.target.value)} autoFocus required />
          </div>
          <div className="field">
            <label htmlFor="contact">Lead officer email</label>
            <input id="contact" type="email" className="input" placeholder="officer@cs-society.org" value={contact} onChange={(e) => setContact(e.target.value)} required />
            <span className="hint">Shown to other administrators as the election’s contact.</span>
          </div>
          <FormError message={error} />
        </div>
        <div className="card-foot row" style={{ justifyContent: 'flex-end', gap: 8 }}>
          <Link to="/admin" className="btn">Cancel</Link>
          <button className="btn btn-primary" disabled={busy || !org.trim() || !contact.trim()}>{busy && <Spinner />} Create election</button>
        </div>
      </form>
    </div>
  );
}
