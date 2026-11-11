import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useWorkspace } from '../App';
import { money } from '../data/mock-data';
import type { ClaimStatus } from '../types';
import { PageHeader, PriorityPill, StatusPill } from '../components/ui';

export default function Claims() {
  const { role, claims } = useWorkspace();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('All');
  const [priority, setPriority] = useState('All');
  const [team, setTeam] = useState('All');
  const [date, setDate] = useState('All');
  const customer = role === 'client';
  const visibleClaims = useMemo(() => claims.filter(claim => {
    const matchesSearch = `${claim.id} ${claim.claimant} ${claim.vehicle} ${claim.registration}`.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = status === 'All' || claim.status === status;
    const matchesPriority = customer || priority === 'All' || claim.priority === priority;
    const matchesTeam = team === 'All' || claim.queue === team;
    const matchesDate = date === 'All' || (date === 'October 2026' && claim.incidentDate.includes('Oct 2026')) || (date === 'September 2026' && claim.incidentDate.includes('Sep 2026'));
    return matchesSearch && matchesStatus && matchesPriority && matchesTeam && matchesDate && (!customer || claim.claimant === 'Amina Patel');
  }), [claims, search, status, priority, team, date, customer]);

  function resetFilters() { setSearch(''); setStatus('All'); setPriority('All'); setTeam('All'); setDate('All'); }

  return <div className="page-wrap">
    <PageHeader title={customer ? 'My Claims' : role === 'admin' ? 'All Claims' : 'Claims Queue'} subtitle={customer ? 'Search your claims and follow their progress, from submission to decision.' : 'Review automatically prioritised claims and their assigned teams.'} action={customer ? <Link to="/claims/new" className="btn-primary">＋ &nbsp; File a New Claim</Link> : <button className="btn-outline" type="button" onClick={() => window.alert('Queue export prepared in this local prototype.')}>⇩ &nbsp; Export queue</button>} />
    <section className="panel queue-panel">
      <div className="queue-summary"><div><h2>{customer ? 'All claims' : 'Open claims'}</h2><p>{customer ? '7 claims · 3 active · 1 awaiting documents' : `${visibleClaims.length} displayed · Sorted by priority, then oldest first`}</p></div></div>
      <div className="filter-bar">
        <label className="search-wrap"><span>⌕</span><input value={search} onChange={event => setSearch(event.target.value)} placeholder={customer ? 'Search claim ID or vehicle' : 'Search claim ID or customer'} aria-label="Search claims" /></label>
        <select className="filter-select" value={status} onChange={event => setStatus(event.target.value)}><option value="All">Status: All statuses</option>{(['Submitted', 'Under review', 'More info requested', 'Assessment', 'Approved', 'Rejected', 'Closed'] as ClaimStatus[]).map(value => <option key={value}>{value}</option>)}</select>
        {!customer && <select className="filter-select" value={priority} onChange={event => setPriority(event.target.value)}><option value="All">Priority: All</option><option>High</option><option>Medium</option><option>Low</option></select>}
        {!customer && <select className="filter-select" value={team} onChange={event => setTeam(event.target.value)}><option value="All">Team: All teams</option><option>Injury/Theft</option><option>Major Damage</option><option>Minor Damage</option></select>}
        <select className="filter-select date-filter" value={date} onChange={event => setDate(event.target.value)}><option value="All">Date: All time</option><option>October 2026</option><option>September 2026</option></select>
        <button type="button" className="text-button" onClick={resetFilters}>Reset filters</button>
      </div>
      <div className="table-scroll">
        {customer ? <table className="data-table customer-table"><thead><tr><th>Claim ID</th><th>Date submitted</th><th>Vehicle</th><th>Status</th><th>Action</th></tr></thead><tbody>
          {visibleClaims.map(claim => <tr key={claim.id}><td><strong className="table-primary">{claim.id}</strong></td><td>{claim.submitted.split(' · ')[0]}</td><td><strong>{claim.registration}</strong><small>{claim.vehicle}</small></td><td><StatusPill status={claim.status} /></td><td><Link to={`/claims/${claim.id}`} className="text-link">View →</Link></td></tr>)}
          {!visibleClaims.length && <tr><td colSpan={5} className="empty-row">No claims match your filters.</td></tr>}
        </tbody></table> : <table className="data-table queue-table"><thead><tr><th>Claim ID</th><th>Customer</th><th>Incident</th><th>Est. amount</th><th>Priority ↕</th><th>Routed team</th><th>Status</th><th>Date</th><th>Action</th></tr></thead><tbody>
          {visibleClaims.map(claim => <tr key={claim.id}><td><strong className="table-primary">{claim.id}</strong></td><td>{claim.claimant}</td><td>{claim.incidentType}</td><td>{money(claim.amount)}</td><td><PriorityPill priority={claim.priority} /></td><td>{claim.queue}</td><td><StatusPill status={claim.status} /></td><td>{claim.incidentDate}</td><td><Link to={`/claims/${claim.id}`} className="text-link">Review →</Link></td></tr>)}
          {!visibleClaims.length && <tr><td colSpan={9} className="empty-row">No claims match your filters.</td></tr>}
        </tbody></table>}
      </div>
      <div className="table-footer"><span>Showing {visibleClaims.length} of {customer ? '7' : '24'} claims · Amounts in KSh</span><div className="pagination"><button type="button" disabled>Previous</button><button type="button" className="selected">1</button><button type="button">2</button><button type="button">3</button><button type="button">Next</button></div></div>
    </section>
    <p className="page-footnote">{customer ? 'Need to add evidence? Open a claim to see requested documents and officer comments.' : 'Priority and routed team are assigned automatically. Claims officers can reassign a claim with a recorded reason.'}</p>
  </div>;
}
