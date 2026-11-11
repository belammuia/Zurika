import { useEffect, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { ClaimStatus, Priority } from '../types';

export function PageHeader({ eyebrow, title, subtitle, action }: { eyebrow?: string; title: string; subtitle?: string; action?: ReactNode }) {
  return <div className="page-heading-row"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1 className="page-title">{title}</h1>{subtitle && <p className="page-subtitle">{subtitle}</p>}</div>{action}</div>;
}

export function StatusPill({ status }: { status: ClaimStatus | string }) {
  const tone = status === 'Approved' || status === 'Paid' ? 'status-green' : status === 'Under review' || status === 'Assessment' || status === 'Processing' ? 'status-blue' : status === 'More info requested' || status === 'Submitted' || status === 'Pending' ? 'status-amber' : status === 'Rejected' || status === 'Failed' ? 'status-red' : 'status-muted';
  return <span className={`status-pill ${tone}`}>{status}</span>;
}

export function PriorityPill({ priority }: { priority: Priority | string }) {
  const tone = priority === 'High' || priority === 'Urgent' ? 'priority-red' : priority === 'Medium' ? 'priority-amber' : 'priority-muted';
  return <span className={`priority-pill ${tone}`}>{priority}</span>;
}

export function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  useEffect(() => {
    if (!message) return undefined;
    const timer = window.setTimeout(onClose, 4200);
    return () => window.clearTimeout(timer);
  }, [message, onClose]);
  if (!message) return null;
  return <div className="toast" role="status" onClick={onClose}>{message}<button type="button" aria-label="Dismiss">×</button></div>;
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <div className="empty-state"><strong>{title}</strong><p>{description}</p>{action}</div>;
}

export function ClaimTable({ rows, customer = false }: { rows: import('../types').ClaimRecord[]; customer?: boolean }) {
  return <div className="table-scroll"><table className={`data-table ${customer ? 'customer-table' : 'queue-table'}`}>
    {customer ? <>
      <thead><tr><th>Claim ID</th><th>Date submitted</th><th>Vehicle</th><th>Status</th><th /></tr></thead>
      <tbody>{rows.map(claim => <tr key={claim.id}><td><strong className="table-primary">{claim.id}</strong></td><td>{claim.submitted.split(' · ')[0]}</td><td><strong>{claim.registration}</strong><small>{claim.vehicle}</small></td><td><StatusPill status={claim.status} /></td><td><Link to={`/claims/${claim.id}`} className="text-link">View →</Link></td></tr>)}</tbody>
    </> : <>
      <thead><tr><th>Claim ID</th><th>Customer</th><th>Incident</th><th>Est. amount</th><th>Priority</th><th>Routed team</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
      <tbody>{rows.map(claim => <tr key={claim.id}><td><strong className="table-primary">{claim.id}</strong></td><td>{claim.claimant}</td><td>{claim.incidentType}</td><td>{importMoney(claim.amount)}</td><td><PriorityPill priority={claim.priority} /></td><td>{claim.queue}</td><td><StatusPill status={claim.status} /></td><td>{claim.incidentDate}</td><td><Link to={`/claims/${claim.id}`} className="text-link">Review →</Link></td></tr>)}</tbody>
    </>}
  </table></div>;
}

function importMoney(amount: number) {
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(amount);
}
