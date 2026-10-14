import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bomb } from 'lucide-react';
import { adminApi, errorMessage } from '../../api';
import { Modal, Spinner, useToast } from '../../components/ui';

export default function SettingsPage() {
  const toast = useToast();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState('');
  const [busy, setBusy] = useState(false);

  const reset = async () => {
    setBusy(true);
    try {
      await adminApi.reset();
      toast('success', 'All election data and the ledger were wiped.');
      setOpen(false);
      navigate('/admin');
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Settings</h1>
          <p className="muted">System-wide maintenance for this PolyVote instance.</p>
        </div>
      </div>

      <div className="card danger-box">
        <div className="card-header"><h2 style={{ color: 'var(--danger)' }}>Danger zone</h2></div>
        <div className="card-body spread">
          <div style={{ maxWidth: 560 }}>
            <strong style={{ fontWeight: 500 }}>Factory reset</strong>
            <p className="muted" style={{ marginTop: 2 }}>
              Deletes every organisation, election, candidate, voter and ballot, and empties the audit ledger. Administrator accounts are kept.
            </p>
          </div>
          <button className="btn btn-danger" onClick={() => { setTyped(''); setOpen(true); }}><Bomb /> Factory reset</button>
        </div>
      </div>

      <Modal
        open={open}
        onClose={() => !busy && setOpen(false)}
        title="Wipe all election data?"
        tone="danger"
        icon={<Bomb />}
        footer={
          <>
            <button className="btn" onClick={() => setOpen(false)} disabled={busy}>Cancel</button>
            <button className="btn btn-danger" disabled={busy || typed !== 'RESET'} onClick={reset}>{busy && <Spinner />} Wipe everything</button>
          </>
        }
      >
        <div className="stack-sm">
          <p>This can't be undone. The audit ledger will be emptied too, so past receipts can no longer be verified.</p>
          <label htmlFor="confirm-reset" className="subtle">Type <strong>RESET</strong> to confirm</label>
          <input id="confirm-reset" className="input input-mono" value={typed} onChange={(e) => setTyped(e.target.value)} autoComplete="off" />
        </div>
      </Modal>
    </>
  );
}
