import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, LogIn } from 'lucide-react';
import { useAdminAuth } from '../../auth';
import { errorMessage } from '../../api';
import { BrandMark, FormError, PageLoading, Spinner } from '../../components/ui';

export default function AdminLogin() {
  const { username, checking, login } = useAdminAuth();
  const navigate = useNavigate();
  const from = (useLocation().state as { from?: string } | null)?.from ?? '/admin';
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (checking) return <PageLoading />;
  if (username) return <Navigate to={from} replace />;

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(user, password);
      navigate(from, { replace: true });
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  };

  return (
    <div className="login-shell">
      <div className="stack" style={{ width: 'min(400px, 100%)' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }}><ArrowLeft /> Back to voting</Link>
        <form className="card login-card stack" onSubmit={submit}>
          <div className="stack-sm">
            <BrandMark />
            <h1 style={{ marginTop: 8 }}>Administrator sign in</h1>
            <p className="muted">Manage elections, rosters, results and the audit ledger.</p>
          </div>
          <div className="field">
            <label htmlFor="u">Username</label>
            <input id="u" className="input" autoFocus autoComplete="username" value={user} onChange={(e) => setUser(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="p">Password</label>
            <input id="p" type="password" className="input" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <FormError message={error} />
          <button className="btn btn-primary btn-lg btn-block" disabled={busy || !user || !password}>
            {busy ? <Spinner /> : <LogIn />}
            Sign in
          </button>
          <div className="demo-creds">
            Local demo credentials: <code>admin</code> / <code>admin123</code>
          </div>
        </form>
      </div>
    </div>
  );
}
