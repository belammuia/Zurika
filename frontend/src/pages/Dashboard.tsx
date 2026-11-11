import { Link } from 'react-router-dom';
import { useWorkspace } from '../App';
import { money } from '../data/mock-data';
import { ClaimTable, PageHeader, PriorityPill, StatusPill } from '../components/ui';

function Metric({ label, value, foot, icon }: { label: string; value: string; foot: string; icon: string }) {
  return <article className="metric-card"><div className="metric-top"><span>{label}</span><span className="metric-icon">{icon}</span></div><div className="metric-value">{value}</div><div className="metric-foot">{foot}</div></article>;
}

export default function Dashboard() {
  const { role, claims } = useWorkspace();
  const ownClaims = claims.filter(claim => claim.claimant === 'Amina Patel');
  const assigned = claims.filter(claim => claim.officer === 'Daniel Brooks').slice(0, 3);

  if (role === 'client') {
    return <div className="page-wrap">
      <PageHeader eyebrow="FRIDAY, 9 OCTOBER 2026" title="Good morning, Amina" subtitle="Here's the latest on your motor claims." action={<Link to="/claims/new" className="btn-primary"><span>＋</span> File a New Claim</Link>} />
      <div className="metric-grid three">
        <Metric label="Active Claims" value="3" foot="Claims currently being processed" icon="▣" />
        <Metric label="Approved" value="2" foot="Approved claims this year" icon="✓" />
        <Metric label="Pending Documents" value="1" foot="One claim needs your attention" icon="▤" />
      </div>
      <div className="notice notice-warning"><span className="notice-icon">!</span><div><strong>A document is needed for TC-2026-1048</strong><p>Daniel Brooks requested a medical note on 8 October. Upload it to keep your claim moving.</p></div><Link to="/claims/TC-2026-1048" className="btn-outline small">View claim</Link></div>
      <section className="panel table-panel">
        <div className="panel-heading"><div><h2 className="panel-title">Recent Claims</h2><p className="panel-subtitle">Your five most recent claims</p></div><Link to="/claims" className="text-link">View all claims</Link></div>
        <ClaimTable rows={(ownClaims.length ? ownClaims : claims).slice(0, 5)} customer />
        <div className="table-footer"><span>Showing 1–5 of 7 claims</span><span>Updated today at 08:30</span></div>
      </section>
      <div className="policy-footer">◈ &nbsp; Policy POL-2026-08421 · 2022 Toyota Corolla · CA 482-716 · Cover active until 31 Dec 2026</div>
    </div>;
  }

  if (role === 'claims_officer') {
    return <div className="page-wrap">
      <PageHeader eyebrow="FRIDAY, 9 OCTOBER 2026" title="Good morning, Daniel" subtitle="Your team's workload at a glance. Start with the claims that need attention." action={<Link to="/claims" className="btn-primary">→ &nbsp; Open claims queue</Link>} />
      <div className="metric-grid four">
        <Metric label="New Claims" value="8" foot="Awaiting first review" icon="▱" />
        <Metric label="High Priority" value="6" foot="Across all open claims" icon="⚑" />
        <Metric label="In Review" value="12" foot="Assigned and being assessed" icon="▤" />
        <Metric label="Closed Today" value="4" foot="Completed on 9 October" icon="▣" />
      </div>
      <div className="dashboard-split">
        <section className="panel priority-panel"><div className="panel-heading"><div><h2 className="panel-title">Claims by priority</h2><p className="panel-subtitle">Open workload · All teams</p></div></div>
          <div className="bar-chart">
            <div className="bar-col"><span>6</span><div className="bar red" style={{ height: 112 }} /><small>High</small></div>
            <div className="bar-col"><span>10</span><div className="bar amber" style={{ height: 166 }} /><small>Medium</small></div>
            <div className="bar-col"><span>8</span><div className="bar slate" style={{ height: 137 }} /><small>Low</small></div>
          </div>
          <div className="panel-note">24 open claims · Automatically assigned by routing rules</div>
        </section>
        <section className="panel assigned-panel"><div className="panel-heading"><div><h2 className="panel-title">Assigned to Me</h2><p className="panel-subtitle">3 claims · Injury/Theft &amp; Major Damage</p></div><span className="soft-count">3 open</span></div>
          {assigned.map(claim => <div className="assigned-item" key={claim.id}><div><strong>{claim.id} · {claim.claimant}</strong><span>{claim.incidentType} · {money(claim.amount)} · {claim.queue}</span><div className="tag-row"><PriorityPill priority={claim.priority} /><StatusPill status={claim.status} /></div></div><Link to={`/claims/${claim.id}`} className="text-link">Review</Link></div>)}
        </section>
      </div>
      <section className="panel insight-panel"><strong>A clear path for every claim</strong><p>Triage keeps the right work with the right team.</p><span>8 new + 12 in review + 4 awaiting information = 24 open claims. Injury and theft cases take precedence over damage amount rules.</span></section>
    </div>;
  }

  const senior = role === 'senior_officer';
  return <div className="page-wrap">
    <PageHeader eyebrow="CLAIMS OPERATIONS" title={senior ? 'Good morning, Sarah' : 'Workspace overview'} subtitle={senior ? 'Monitor escalations, decisions and the work requiring senior attention.' : 'A clear view of claims, settlements and insurer operations.'} action={<Link to={senior ? '/reviews' : '/payouts'} className="btn-primary">{senior ? 'Review approvals →' : 'View operations →'}</Link>} />
    <div className="metric-grid four">
      <Metric label={senior ? 'Escalated Claims' : 'Total Claims'} value={senior ? '12' : '248'} foot="Across all active teams" icon="▤" />
      <Metric label="Awaiting Decision" value="9" foot="Need senior review" icon="◷" />
      <Metric label="Pending Payouts" value="7" foot="Approved, not yet settled" icon="↗" />
      <Metric label="Settled This Month" value="42" foot="Successfully disbursed" icon="✓" />
    </div>
    <div className="dashboard-split">
      <section className="panel"><div className="panel-heading"><div><h2 className="panel-title">Claims requiring attention</h2><p className="panel-subtitle">Escalated or awaiting a decision</p></div><Link className="text-link" to="/reviews">View approvals</Link></div>
        {claims.filter(claim => claim.priority === 'High').slice(0, 3).map(claim => <div className="assigned-item" key={claim.id}><div><strong>{claim.id} · {claim.claimant}</strong><span>{claim.queue} · {money(claim.amount)}</span><div className="tag-row"><PriorityPill priority={claim.priority} /><StatusPill status={claim.status} /></div></div><Link to={`/claims/${claim.id}`} className="text-link">Review</Link></div>)}
      </section>
      <section className="panel"><div className="panel-heading"><div><h2 className="panel-title">Settlement overview</h2><p className="panel-subtitle">October 2026 · Motor claims</p></div></div>
        <div className="settlement-total">KSh 4,820,500</div><p className="panel-subtitle">Total amount disbursed this month</p>
        <div className="settlement-row"><span>M-Pesa payouts</span><strong>KSh 2,140,500</strong></div>
        <div className="settlement-row"><span>Bank transfers</span><strong>KSh 2,680,000</strong></div>
        <div className="settlement-row"><span>Awaiting settlement</span><strong>7 payouts</strong></div>
        <Link to="/payouts" className="text-link">Open payout management →</Link>
      </section>
    </div>
    <section className="panel table-panel mt-4"><div className="panel-heading"><div><h2 className="panel-title">Latest claims</h2><p className="panel-subtitle">Recently submitted across all teams</p></div><Link to="/claims" className="text-link">View all claims</Link></div><ClaimTable rows={claims.slice(0, 4)} /></section>
  </div>;
}
