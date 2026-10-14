import { Link, NavLink, Outlet } from 'react-router-dom';
import { BrandMark } from '../../components/ui';

export default function PublicLayout() {
  return (
    <div className="public-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <BrandMark />
          PolyVote
        </Link>
        <nav className="row" style={{ gap: 4 }} aria-label="Site">
          <NavLink to="/verify" className="btn btn-ghost btn-sm">Check receipt</NavLink>
          <Link to="/admin" className="btn btn-sm">Admin</Link>
        </nav>
      </header>
      <main className="public-main">
        <Outlet />
      </main>
      <footer className="public-foot">PolyVote · ranked-choice elections with a tamper-evident ballot ledger</footer>
    </div>
  );
}
