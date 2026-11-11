import { useMemo, useState, type ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { money } from '../data/mock-data';
import { useWorkspace } from '../App';
import { PageHeader } from '../components/ui';

interface FormState {
  vehicle: string;
  registration: string;
  policyNumber: string;
  incidentType: string;
  incidentDate: string;
  incidentTime: string;
  location: string;
  estimatedCost: string;
  description: string;
  policeReport: string;
  thirdParty: string;
  injury: string;
}

const initialForm: FormState = {
  vehicle: '2022 Toyota Corolla', registration: 'CA 482-716', policyNumber: 'POL-2026-08421',
  incidentType: 'Collision', incidentDate: '2026-10-06', incidentTime: '08:40', location: 'Kenyatta Avenue, Nairobi',
  estimatedCost: '68500', description: '', policeReport: '', thirdParty: 'Yes', injury: 'No',
};

export default function SubmitClaim() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormState>(initialForm);
  const [files, setFiles] = useState<string[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();
  const { setClaims } = useWorkspace();
  const estimated = Number(form.estimatedCost) || 0;
  const canContinue = useMemo(() => step === 1 ? Boolean(form.incidentType && form.incidentDate && form.location && form.description.trim() && estimated > 0) : step === 2 ? files.length > 0 : true, [step, form, estimated, files.length]);
  const update = (key: keyof FormState, value: string) => setForm(current => ({ ...current, [key]: value }));

  function submit() {
    const id = 'TC-2026-1054';
    setClaims(current => [{
      id, claimant: 'Amina Patel', initials: 'AP', email: 'amina.patel@email.com', vehicle: form.vehicle, registration: form.registration,
      policyNumber: form.policyNumber, incidentDate: new Date(`${form.incidentDate}T00:00:00`).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
      incidentTime: form.incidentTime, incidentType: form.incidentType, location: form.location, description: form.description,
      submitted: 'Today · Just now', amount: estimated, status: 'Submitted', priority: form.injury === 'Yes' ? 'High' : estimated >= 50000 ? 'High' : 'Medium',
      queue: form.injury === 'Yes' ? 'Injury/Theft' : estimated >= 50000 ? 'Major Damage' : 'Minor Damage', insurer: 'Zurika Motor Insurance',
      injury: form.injury === 'Yes', thirdParty: form.thirdParty === 'Yes', policeReport: form.policeReport || 'Pending', officer: 'Unassigned',
      officerTeam: 'Claims team', comments: 'Your claim has been received and is awaiting initial review.', photos: [],
    }, ...current]);
    setSubmitted(true);
  }

  if (submitted) return <div className="page-wrap"><div className="success-card"><div className="success-mark">✓</div><div className="eyebrow">CLAIM SUBMITTED</div><h1 className="page-title">Your claim is on its way</h1><p className="page-subtitle">We've received your claim. Our team will review your information and contact you if anything else is needed.</p><div className="success-claim-id">TC-2026-1054</div><div className="success-meta"><div><span>Vehicle</span><strong>{form.registration}</strong></div><div><span>Estimated amount</span><strong>{money(estimated)}</strong></div><div><span>Submitted</span><strong>Today, just now</strong></div></div><div className="success-divider" /><div className="success-next"><strong>What happens next?</strong><p>A claims officer will review your evidence and contact you if more information is needed. Track every update in My Claims.</p></div><Link to="/claims" className="btn-primary">View my claims →</Link></div></div>;

  return <div className="page-wrap">
    <div className="submit-heading"><PageHeader title="File a Claim" subtitle="Tell us what happened. We'll guide you through the process." /></div>
    <div className="stepper-card"><div className="step-track"><div className={`step ${step >= 1 ? 'current' : ''}`}><span className={step > 1 ? 'complete' : ''}>{step > 1 ? '✓' : '1'}</span><strong>Incident details</strong></div><i /><div className={`step ${step >= 2 ? 'current' : ''}`}><span className={step > 2 ? 'complete' : ''}>{step > 2 ? '✓' : '2'}</span><strong>Vehicle &amp; evidence</strong></div><i /><div className={`step ${step >= 3 ? 'current' : ''}`}><span>3</span><strong>Review &amp; submit</strong></div></div></div>
    <div className="submit-columns">
      <section className="panel form-panel">
        {step === 1 && <>
          <div className="form-intro"><h2 className="panel-title">Tell us about the incident</h2><p className="panel-subtitle">Start with when and where the incident happened.</p></div>
          <div className="form-grid">
            <Field label="Type of incident" required><select value={form.incidentType} onChange={e => update('incidentType', e.target.value)}><option>Collision</option><option>Theft</option><option>Fire</option><option>Vandalism</option><option>Weather damage</option><option>Other</option></select></Field>
            <Field label="Date of incident" required><input type="date" value={form.incidentDate} onChange={e => update('incidentDate', e.target.value)} /></Field>
            <Field label="Approximate time" required><input type="time" value={form.incidentTime} onChange={e => update('incidentTime', e.target.value)} /></Field>
            <Field label="Incident location" required full><input value={form.location} onChange={e => update('location', e.target.value)} placeholder="Street, area, town or landmark" /></Field>
            <Field label="Estimated damage (KSh)" required><input type="number" min="0" value={form.estimatedCost} onChange={e => update('estimatedCost', e.target.value)} /></Field>
            <Field label="Police abstract / OB number"><input value={form.policeReport} onChange={e => update('policeReport', e.target.value)} placeholder="e.g. OB 123/06/10/2026" /></Field>
            <Field label="Was another party involved?"><select value={form.thirdParty} onChange={e => update('thirdParty', e.target.value)}><option>Yes</option><option>No</option></select></Field>
            <Field label="Was anyone injured?"><select value={form.injury} onChange={e => update('injury', e.target.value)}><option>No</option><option>Yes</option></select></Field>
            <Field label="Describe what happened" required full><textarea rows={5} value={form.description} onChange={e => update('description', e.target.value)} placeholder="Include the events leading up to the incident and the damage caused." /></Field>
          </div>
        </>}
        {step === 2 && <>
          <div className="form-intro"><h2 className="panel-title">Vehicle &amp; supporting evidence</h2><p className="panel-subtitle">Confirm the insured vehicle and attach evidence to support your claim.</p></div>
          <div className="form-grid">
            <Field label="Insured vehicle" required><select value={form.vehicle} onChange={e => update('vehicle', e.target.value)}><option>2022 Toyota Corolla</option><option>2020 Honda Fit</option><option>2018 Toyota Vitz</option></select></Field>
            <Field label="Vehicle registration" required><input value={form.registration} onChange={e => update('registration', e.target.value)} /></Field>
            <Field label="Policy number" required full><input value={form.policyNumber} onChange={e => update('policyNumber', e.target.value)} /></Field>
          </div>
          <div className="upload-section-head"><div><h3 className="panel-title">Photos and documents</h3><p className="panel-subtitle">Upload clear images of the damage, incident scene and supporting documents.</p></div><span className="soft-count">JPG, PNG or PDF</span></div>
          <label className="upload-box"><input type="file" multiple accept="image/*,.pdf" onChange={event => setFiles(Array.from(event.target.files ?? []).map(file => file.name))} /><span className="upload-symbol">↑</span><strong>Choose files or drag them here</strong><small>Maximum 10 MB per file</small></label>
          {files.length > 0 && <div className="upload-preview">{files.map(file => <span className="file-chip" key={file}>▧ {file}</span>)}</div>}
          <div className="guidance-panel"><span className="guidance-icon">i</span><div><strong>Helpful evidence to include</strong><p>Photos from multiple angles, police abstract, repair estimate, medical notes (where applicable) and details of any third party involved.</p></div></div>
        </>}
        {step === 3 && <>
          <div className="form-intro"><h2 className="panel-title">Review your claim</h2><p className="panel-subtitle">Make sure the information below is accurate before submitting.</p></div>
          <div className="review-summary-card"><div className="summary-head"><strong>Incident details</strong><button type="button" className="text-link" onClick={() => setStep(1)}>Edit</button></div><div className="detail-grid"><Detail label="Incident type" value={form.incidentType} /><Detail label="Date & time" value={`${form.incidentDate} · ${form.incidentTime}`} /><Detail label="Location" value={form.location} /><Detail label="Estimated damage" value={money(estimated)} /></div><p className="long-description">{form.description}</p></div>
          <div className="review-summary-card"><div className="summary-head"><strong>Vehicle &amp; evidence</strong><button type="button" className="text-link" onClick={() => setStep(2)}>Edit</button></div><div className="detail-grid"><Detail label="Vehicle" value={form.vehicle} /><Detail label="Registration" value={form.registration} /><Detail label="Policy number" value={form.policyNumber} /><Detail label="Evidence files" value={`${files.length} file(s) attached`} /></div>{files.map(file => <span className="file-chip" key={file}>▧ {file}</span>)}</div>
          <label className="declaration"><input type="checkbox" defaultChecked /> <span>I confirm that the information provided is accurate and complete to the best of my knowledge.</span></label>
        </>}
        <div className="form-actions"><button type="button" className="btn-outline" onClick={() => step === 1 ? navigate('/claims') : setStep(value => value - 1)}>{step === 1 ? 'Cancel' : '← Back'}</button><button type="button" className="btn-primary" disabled={!canContinue} onClick={() => step < 3 ? setStep(value => value + 1) : submit()}>{step < 3 ? 'Continue →' : 'Submit claim →'}</button></div>
        <p className="autosave-note">Your progress is kept in this browser while you complete the form.</p>
      </section>
      <aside className="submit-aside"><section className="panel"><h2 className="panel-title">Your policy</h2><p className="panel-subtitle">Active motor insurance cover</p><div className="settlement-total">POL-2026-08421</div><div className="settlement-row"><span>Insured vehicle</span><strong>CA 482-716</strong></div><div className="settlement-row"><span>Cover type</span><strong>Comprehensive</strong></div><div className="settlement-row"><span>Valid until</span><strong>31 Dec 2026</strong></div></section><section className="panel"><h2 className="panel-title">Need help?</h2><p className="help-copy">Our claims support team can guide you through the process.</p><strong className="help-copy">0800 123 456</strong><p className="panel-subtitle">Monday–Friday, 8:00 AM–5:00 PM</p></section></aside>
    </div>
  </div>;
}

function Field({ label, required, full, children }: { label: string; required?: boolean; full?: boolean; children: ReactNode }) {
  return <label className={`field ${full ? 'full' : ''}`}><span>{label} {required && <b>*</b>}</span>{children}</label>;
}
function Detail({ label, value }: { label: string; value: string }) { return <div><span className="detail-label">{label}</span><strong>{value}</strong></div>; }
