import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { roleLabels } from '../data/mock-data';
import { useWorkspace } from '../App';
import type { NavItem, UserRole } from '../types';

const navByRole: Record<UserRole, NavItem[]> = {
  client: [
    { label: 'Dashboard', path: '/', icon: '▦' },
    { label: 'File a Claim', path: '/claims/new', icon: '⊕' },
    { label: 'My Claims', path: '/claims', icon: '▤' },
  ],
  claims_officer: [
    { label: 'Dashboard', path: '/', icon: '▦' },
    { label: 'Claims Queue', path: '/claims', icon: '▤' },
    { label: 'Routing Rules', path: '/routing', icon: '⑂' },
  ],
  senior_officer: [
    { label: 'Dashboard', path: '/', icon: '▦' },
    { label: 'Claims Queue', path: '/claims', icon: '▤' },
    { label: 'Approvals', path: '/reviews', icon: '✓' },
    { label: 'Routing Rules', path: '/routing', icon: '⑂' },
    { label: 'Payouts', path: '/payouts', icon: '↗' },
    { label: 'Audit trail', path: '/audit', icon: '◷' },
  ],
  admin: [
    { label: 'Dashboard', path: '/', icon: '▦' },
    { label: 'Claims', path: '/claims', icon: '▤' },
    { label: 'Approvals', path: '/reviews', icon: '✓' },
    { label: 'Payouts', path: '/payouts', icon: '↗' },
    { label: 'Insurers', path: '/insurers', icon: '▣' },
    { label: 'Team & access', path: '/team', icon: '♙' },
    { label: 'Audit trail', path: '/audit', icon: '◷' },
  ],
};

const roleNames: Record<UserRole, string> = {
  client: 'Amina Patel',
  claims_officer: 'Daniel Brooks',
  senior_officer: 'Sarah Adams',
  admin: 'Belam Muia',
};

function SideNavigation({ close }: { close?: () => void }) {
  const { role } = useWorkspace();
  const items = navByRole[role];
  const workspaceCaption = role === 'client' ? 'CUSTOMER PORTAL' : role === 'admin' ? 'ADMINISTRATION' : role === 'senior_officer' ? 'SENIOR OFFICER WORKSPACE' : 'CLAIMS OFFICER WORKSPACE';
  return (
    <>
      <NavLink to="/" className="brand-lockup" aria-label="Zurika home" onClick={close}>
        <span className="brand-symbol">Z</span><span className="brand-name">zurika<span>.</span></span>
      </NavLink>
      <div className="workspace-caption">{workspaceCaption}</div>
      <nav className="side-nav" aria-label="Main navigation">
        {items.map(item => (
          <NavLink key={item.path} to={item.path} end={item.path === '/'} className={({ isActive }) => `side-link ${isActive ? 'active' : ''}`} onClick={close}>
            <span className="side-icon">{item.icon}</span><span>{item.label}</span>
            {item.label === 'Claims Queue' && <span className="side-count">24</span>}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <NavLink to="/help" className="utility-link" onClick={close}><span>ⓘ</span> Help &amp; support</NavLink>
        <NavLink to="/login" className="utility-link" onClick={close}><span>↪</span> Sign out</NavLink>
        <div className="sidebar-footnote">Zurika · Motor insurance</div>
      </div>
    </>
  );
}

export default function Layout() {
  const { role, setRole } = useWorkspace();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const path = location.pathname;
  const pageName = path === '/' ? 'Dashboard' : path.startsWith('/claims/new') ? 'File a Claim' : path.startsWith('/claims/') ? 'Claim details' : path === '/claims' ? (role === 'client' ? 'My Claims' : 'Claims Queue') : path.split('/')[1].replace('-', ' ').replace(/^./, c => c.toUpperCase());
  const userName = roleNames[role];
  const initials = userName.split(' ').map(part => part[0]).join('');

  function changeRole(nextRole: UserRole) {
    setRole(nextRole);
    window.localStorage.setItem('zurika-role', nextRole);
    if (nextRole === 'client' && ['/routing', '/reviews', '/payouts', '/audit', '/team', '/insurers'].includes(path)) navigate('/');
  }

  return (
    <div className="app-frame">
      <aside className="sidebar"><SideNavigation /></aside>
      <div className="main-column">
        <header className="topbar">
          <button type="button" className="mobile-toggle" aria-label="Open navigation" onClick={() => setMobileOpen(true)}>☰</button>
          <div className="breadcrumbs"><span>Motor insurance</span><span className="crumb-slash">/</span><strong>{pageName}</strong></div>
          <div className="topbar-actions">
            <button className="bell-button" type="button" aria-label="Notifications">♧<i /></button>
            <span className="topbar-divider" />
            <div className="user-summary"><strong>{userName}</strong><span>{roleLabels[role]}</span></div>
            <span className="user-avatar">{initials}</span>
            <label className="sr-only" htmlFor="role-preview">Preview user role</label>
            <select id="role-preview" className="role-preview" value={role} onChange={event => changeRole(event.target.value as UserRole)}>
              <option value="client">Customer</option><option value="claims_officer">Claims Officer</option><option value="senior_officer">Senior Officer</option><option value="admin">Administrator</option>
            </select>
          </div>
        </header>
        <main className="content-area w-full flex-1"><Outlet /></main>
        <footer className="app-footer"><span>© 2026 Zurika</span><span>Motor insurance claims, made clearer.</span></footer>
      </div>
      {mobileOpen && <div className="mobile-scrim" role="presentation" onClick={() => setMobileOpen(false)}><aside className="mobile-drawer" onClick={event => event.stopPropagation()}><div className="mobile-drawer-head"><span className="brand-name">zurika<span>.</span></span><button type="button" onClick={() => setMobileOpen(false)} aria-label="Close navigation">×</button></div><SideNavigation close={() => setMobileOpen(false)} /></aside></div>}
    </div>
  );
}
