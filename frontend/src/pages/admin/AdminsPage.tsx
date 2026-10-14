import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { UserPlus } from 'lucide-react';
import { useAdminAuth } from '../../auth';
import { adminApi, errorMessage } from '../../api';
import { Avatar, PageLoading, Spinner, useToast } from '../../components/ui';

export default function AdminsPage() {
  const toast = useToast();
  const { username: me } = useAdminAuth();
  const [admins, setAdmins] = useState<string[] | null>(null);
  const [user, setUser] = useState('');
  const [pw, setPw] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    adminApi.admins().then(setAdmins).catch((e) => toast('error', errorMessage(e)));
  }, [toast]);
  useEffect(load, [load]);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    try {
      await adminApi.addAdmin(user, pw);
      toast('success', `Administrator ${user.trim()} created.`);
      setUser('');
      setPw('');
      load();
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
          <h1>Administrators</h1>
          <p className="muted">Administrators can manage every election on this PolyVote instance.</p>
        </div>
      </div>
      <div className="grid-2" style={{ gridTemplateColumns: 'minmax(0, 1.3fr) minmax(0, 1fr)' }}>
        <div className="card">
          <div className="card-header"><h2>Accounts</h2><span className="subtle">{admins?.length ?? '–'}</span></div>
          {!admins ? <PageLoading /> : (
            <div className="table-wrap">
              <table className="table">
                <tbody>
                  {admins.map((a) => (
                    <tr key={a}>
                      <td>
                        <div className="row">
                          <Avatar name={a} />
                          <span className="cell-title">{a}</span>
                          {a === me && <span className="label label-accent">You</span>}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        <form className="card" onSubmit={submit}>
          <div className="card-header"><h2 className="section-title"><UserPlus /> Add administrator</h2></div>
          <div className="card-body stack">
            <div className="field">
              <label htmlFor="nu">Username</label>
              <input id="nu" className="input" autoComplete="off" value={user} onChange={(e) => setUser(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="np">Password</label>
              <input id="np" type="password" className="input" autoComplete="new-password" value={pw} onChange={(e) => setPw(e.target.value)} />
            </div>
            <button className="btn btn-primary" disabled={busy || !user.trim() || !pw}>{busy && <Spinner />} Create administrator</button>
          </div>
        </form>
      </div>
    </>
  );
}
