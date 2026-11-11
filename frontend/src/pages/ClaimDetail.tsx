import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useWorkspace } from '../App';
import { money } from '../data/mock-data';
import type { ClaimStatus } from '../types';
import { PriorityPill, StatusPill, Toast } from '../components/ui';

export default function ClaimDetail() {
  const { id } = useParams();
  const { role, claims, setClaims } = useWorkspace();
  const claim = claims.find(record => record.id === id) ?? claims[0];
  const customer = role === 'client';
  const [comment, setComment] = useState('');
  const [toast, setToast] = useState('');
  const [showReassign, setShowReassign] = useState(false);
  const [assignedTo, setAssignedTo] = useState('Sarah Adams');

  if (!claim) return <div className="page-wrap"><div className="panel"><h1 className="panel-title">Claim not found</h1><Link to="/claims" className="text-link">Back to claims</Link></div></div>;

  function uploadNotice() { setToast('Document upload is a local prototype interaction. No file was sent to a server.'); }
  function updateClaim(status: ClaimStatus) {
    if (!comment.trim()) { setToast('Add an officer comment before recording this decision.'); return; }
    setClaims(current => current.map(item => item.id === claim.id ? { ...item, status, comments: comment.trim() } : item));
    setToast(`Claim ${claim.id} marked as ${status.toLowerCase()} in this prototype.`);
    setComment('');
  }
  function reassign() {
    if (!comment.trim()) { setToast('Add a reason before reassigning this claim.'); return; }
    setClaims(current => current.map(item => item.id === claim.id ? { ...item, officer: assignedTo, comments: comment.trim() } : item));
    setShowReassign(false);
    setToast(`Claim reassigned to ${assignedTo} in this prototype.`);
    setComment('');
  }

  return <div className="page-wrap">
    <Link to="/claims" className="back-link">← &nbsp; {customer ? 'My Claims' : 'Claims Queue'}</Link>
    <div className="claim-title-row"><div><h1 className="page-title">{claim.id}</h1><p className="page-subtitle">{claim.incidentType} · {claim.vehicle} · Submitted {claim.submitted}</p></div><StatusPill status={claim.status} /></div>
    {customer ? <>
      {claim.status === 'More info requested' && <div className="notice notice-warning"><span className="notice-icon">!</span><div><strong>More information requested</strong><p>Please upload the passenger's medical note by 12 Oct 2026. Your claim will continue once it is received.</p></div><button type="button" className="btn-primary small" onClick={uploadNotice}>⇧ &nbsp; Upload Additional Document</button></div>}
      <div className="detail-layout">
        <div className="detail-main">
          <section className="panel"><div className="panel-heading"><h2 className="panel-title">Claim summary</h2></div><div className="detail-grid">
            <DetailField label="Policy number" value={claim.policyNumber} /><DetailField label="Vehicle plate" value={claim.registration} /><DetailField label="Incident date & time" value={`${claim.incidentDate} · ${claim.incidentTime}`} /><DetailField label="Estimated damage (KSh)" value={money(claim.amount)} /><DetailField label="Location" value={claim.location} /><DetailField label="Police report" value={claim.policeReport} /><DetailField label="Injury involved" value={claim.injury ? 'Yes, passenger wrist injury' : 'No'} />
          </div><div className="detail-description"><span className="detail-label">Incident description</span><p>{claim.description}</p></div></section>
          <EvidencePanel claim={claim} onUpload={uploadNotice} />
          <section className="panel"><h2 className="panel-title">Officer comments</h2><div className="comment-card"><div className="comment-meta"><strong>{claim.officer} · Claims Officer</strong><span>8 Oct 2026 · 10:30</span></div><p>{claim.comments}</p></div></section>
        </div>
        <aside className="detail-aside"><ProgressPanel claim={claim} /><section className="panel"><h2 className="panel-title">Your claims officer</h2><div className="officer-card"><span className="officer-avatar">DB</span><div><strong>{claim.officer}</strong><span>{claim.officerTeam}</span></div></div><p className="panel-subtitle">For urgent assistance, call 0800 123 456 and quote your claim ID.</p></section></aside>
      </div>
    </> : <div className="staff-review-layout">
      <div className="detail-main">
        <section className="panel"><div className="panel-heading"><div><h2 className="panel-title">Claim details</h2><p className="panel-subtitle">Customer and insured vehicle</p></div></div><div className="detail-grid">
          <DetailField label="Customer" value={claim.claimant} /><DetailField label="Email" value={claim.email} /><DetailField label="Policy number" value={claim.policyNumber} /><DetailField label="Insured vehicle" value={claim.vehicle} /><DetailField label="Vehicle plate" value={claim.registration} /><DetailField label="Estimated damage (KSh)" value={money(claim.amount)} /><DetailField label="Incident date & time" value={`${claim.incidentDate} · ${claim.incidentTime}`} /><DetailField label="Incident type" value={claim.incidentType} /><DetailField label="Location" value={claim.location} /><DetailField label="Injury involved" value={claim.injury ? 'Yes' : 'No'} /><DetailField label="Police report" value={claim.policeReport} /><DetailField label="Third party involved" value={claim.thirdParty ? 'Yes' : 'No'} />
        </div></section>
        <section className="panel"><h2 className="panel-title">Incident description</h2><p className="long-description">{claim.description}</p></section>
        <EvidencePanel claim={claim} onUpload={uploadNotice} />
      </div>
      <aside className="review-aside">
        <section className="panel triage-panel"><div className="panel-heading"><h2 className="panel-title">Automated Triage Result</h2><span className="metric-icon">⑂</span></div><div className="triage-line"><span>Auto-assigned priority</span><PriorityPill priority={claim.priority} /></div><div className="triage-line"><span>Auto-routed team</span><strong>{claim.queue}</strong></div><div className="reason-box"><strong>WHY THIS CLAIM WAS ROUTED</strong><p>{claim.injury ? 'Injury reported. Injury takes precedence over amount-based rules.' : 'Claim was matched to the configured damage and amount routing rules.'} {money(claim.amount)} is {claim.amount >= 50000 ? 'above' : 'below'} the KSh 50,000 major damage threshold.</p></div><p className="matched-rule">Matched rule: Injury = {claim.injury ? 'Yes' : 'No'} · 7 Oct 2026, 09:12</p></section>
        <section className="panel action-panel"><h2 className="panel-title">Take action</h2><p className="panel-subtitle">Assigned to {claim.officer}</p><label className="field action-comment"><span>Officer comment <b>*</b></span><textarea rows={4} value={comment} onChange={event => setComment(event.target.value)} placeholder="Add a comment explaining your decision or the information required." /></label><p className="field-hint">Comments are visible to the customer. A reason is required for rejection or reassignment.</p><div className="action-pair"><button type="button" className="btn-primary" onClick={() => updateClaim('Approved')}>✓ &nbsp; Approve</button><button type="button" className="btn-danger" onClick={() => updateClaim('Rejected')}>× &nbsp; Reject</button></div><button type="button" className="btn-outline full-btn" onClick={() => updateClaim('More info requested')}>▤ &nbsp; Request More Info</button><button type="button" className="btn-outline full-btn" onClick={() => setShowReassign(value => !value)}>♙ &nbsp; Reassign</button>
          {showReassign && <div className="rule-editor mt-3"><label className="field"><span>Reassign to</span><select value={assignedTo} onChange={event => setAssignedTo(event.target.value)}><option>Sarah Adams</option><option>Daniel Brooks</option><option>Grace Wanjiku</option></select></label><button type="button" className="btn-primary small" onClick={reassign}>Confirm reassignment</button></div>}
          <p className="action-footnote">Every action is recorded in the claim history.</p></section>
        <section className="panel"><h2 className="panel-title">Latest activity</h2><div className="activity-entry"><span>8 Oct 2026 · 10:30 · {claim.officer}</span><strong>{claim.status}</strong><p>{claim.comments}</p></div></section>
      </aside>
    </div>}
    <Toast message={toast} onClose={() => setToast('')} />
  </div>;
}

function DetailField({ label, value }: { label: string; value: string }) { return <div><span className="detail-label">{label}</span><strong>{value}</strong></div>; }

function EvidencePanel({ claim, onUpload }: { claim: import('../types').ClaimRecord; onUpload: () => void }) {
  return <section className="panel"><div className="panel-heading"><div><h2 className="panel-title">{claim.photos.length ? 'Photos & documents' : 'Uploaded files'}</h2><p className="panel-subtitle">Evidence uploaded by {claim.claimant} · 7 Oct 2026</p></div><button type="button" className="btn-outline small" onClick={onUpload}>⇧ Upload</button></div><div className="photo-grid">{claim.photos.map(photo => <figure key={photo}><img src={`/assets/${photo}`} alt={photo} /><figcaption>{photo}</figcaption></figure>)}</div><div className="document-row"><span className="file-icon">PDF</span><div><strong>police-report.pdf</strong><span>PDF · 1.4 MB · 7 Oct 2026</span></div><button type="button" className="download-button" aria-label="Download police report" onClick={onUpload}>↓</button></div><div className="document-row"><span className="file-icon">PDF</span><div><strong>repair-estimate.pdf</strong><span>PDF · 840 KB · 7 Oct 2026</span></div><button type="button" className="download-button" aria-label="Download repair estimate" onClick={onUpload}>↓</button></div></section>;
}

function ProgressPanel({ claim }: { claim: import('../types').ClaimRecord }) {
  return <section className="panel"><h2 className="panel-title">Claim progress</h2><p className="panel-subtitle">Last updated 8 Oct 2026</p><div className="timeline claim-timeline"><div className="timeline-item done"><i>✓</i><div><strong>Submitted</strong><span>7 Oct 2026 · 09:12</span><p>Received and routed to {claim.queue}.</p></div></div><div className="timeline-item done"><i>✓</i><div><strong>Under Review</strong><span>8 Oct 2026 · 10:30</span><p>{claim.officer} reviewed the documents.</p><StatusPill status={claim.status} /></div></div><div className="timeline-item"><i>3</i><div><strong>Assessment</strong><span>Awaiting requested document</span><p>Damage and supporting evidence will be assessed.</p></div></div><div className="timeline-item"><i>4</i><div><strong>Decision</strong><span>Not started</span><p>You'll be notified of the outcome.</p></div></div></div></section>;
}
