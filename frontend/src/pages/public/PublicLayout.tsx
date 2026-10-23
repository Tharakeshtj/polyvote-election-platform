import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import { publicApi } from '../../api';
import { BrandMark } from '../../components/ui';

export default function PublicLayout() {
  const [demo, setDemo] = useState(false);
  useEffect(() => { publicApi.config().then((c) => setDemo(c.hosted_demo)).catch(() => {}); }, []);
  return (
    <div className="public-shell">
      {demo && (
        <div style={{ background: 'var(--accent-soft, #eef2ff)', color: 'var(--text)', fontSize: 13, textAlign: 'center', padding: '6px 12px', borderBottom: '1px solid var(--border)' }}>
          <strong>Demo mode.</strong> Sample data that resets when the server restarts. <Link to="/demo">See the demo guide</Link>
        </div>
      )}
      <header className="topbar">
        <Link to="/" className="brand">
          <BrandMark />
          PolyVote
        </Link>
        <nav className="row" style={{ gap: 4 }} aria-label="Site">
          <NavLink to="/demo" className="btn btn-ghost btn-sm">Demo guide</NavLink>
          <NavLink to="/verify" className="btn btn-ghost btn-sm">Check receipt</NavLink>
          <Link to="/admin" className="btn btn-sm">Admin</Link>
        </nav>
      </header>
      <main className="public-main">
        <Outlet />
      </main>
      <footer className="public-foot">
        <nav aria-label="Footer" style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px', justifyContent: 'center', marginBottom: 6 }}>
          <Link to="/">Home</Link>
          <Link to="/demo">Demo guide</Link>
          <Link to="/verify">Check a receipt</Link>
          <Link to="/privacy">Privacy policy</Link>
          <Link to="/contact">Contact</Link>
          <a href="https://github.com/Tharakeshtj/polyvote-election-platform" target="_blank" rel="noreferrer">Source code</a>
        </nav>
        PolyVote · ranked-choice elections with a tamper-evident ballot ledger
      </footer>
    </div>
  );
}
