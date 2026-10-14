import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { ExternalLink, Link2, LogOut, Menu, Settings, Users, Vote } from 'lucide-react';
import { useAdminAuth } from '../../auth';
import { Avatar, BrandMark } from '../../components/ui';

export default function AdminLayout() {
  const { username, logout } = useAdminAuth();
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();
  useEffect(() => setOpen(false), [pathname]);

  return (
    <div className="admin-shell">
      <div className="mobile-bar">
        <button className="btn btn-ghost icon-btn" aria-label="Open menu" onClick={() => setOpen(true)}><Menu /></button>
        <span className="brand"><BrandMark /> PolyVote</span>
      </div>
      {open && <div className="scrim" onClick={() => setOpen(false)} />}

      <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Admin navigation">
        <Link to="/admin" className="brand"><BrandMark /> PolyVote <span className="label" style={{ marginLeft: 2 }}>Admin</span></Link>
        <NavLink to="/admin" end className={({ isActive }) => `nav-link ${isActive || pathname.startsWith('/admin/elections') ? 'active' : ''}`}>
          <Vote /> Elections
        </NavLink>
        <NavLink to="/admin/ledger" className="nav-link"><Link2 /> Audit ledger</NavLink>
        <div className="nav-label">System</div>
        <NavLink to="/admin/admins" className="nav-link"><Users /> Administrators</NavLink>
        <NavLink to="/admin/settings" className="nav-link"><Settings /> Settings</NavLink>
        <a href="/" target="_blank" rel="noreferrer" className="nav-link"><ExternalLink /> Voter site</a>

        <div className="sidebar-foot">
          <Avatar name={username ?? '?'} />
          <div className="who">
            <strong>{username}</strong>
            <span className="subtle">Administrator</span>
          </div>
          <button className="btn btn-ghost icon-btn" aria-label="Sign out" title="Sign out" onClick={logout}><LogOut /></button>
        </div>
      </aside>

      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}
