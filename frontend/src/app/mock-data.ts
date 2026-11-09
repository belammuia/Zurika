import { ClaimRecord, UserRole } from './models';

export const roleLabels: Record<UserRole, string> = {
  client: 'Policyholder',
  claims_officer: 'Claims Officer',
  senior_officer: 'Senior Claims Officer',
  admin: 'Administrator'
};

export const claims: ClaimRecord[] = [
  {
    id: 'TC-2026-1048', claimant: 'Amina Patel', initials: 'AP', email: 'amina.patel@email.com',
    vehicle: '2022 Toyota Corolla', registration: 'CA 482-716', policyNumber: 'POL-2026-08421',
    incidentDate: '6 Oct 2026', incidentTime: '08:40', incidentType: 'Collision',
    location: 'Kenyatta Avenue, Nairobi',
    description: 'Another vehicle struck the front-left side of my car at the intersection of Kenyatta Avenue. The bumper and left headlight were damaged. My passenger sustained a minor wrist injury and received medical attention.',
    submitted: '7 Oct 2026 · 09:12', amount: 68500, status: 'More info requested', priority: 'High',
    queue: 'Injury/Theft', insurer: 'Zurika Motor Insurance', injury: true, thirdParty: true,
    policeReport: 'CAS 184/10/2026', officer: 'Daniel Brooks', officerTeam: 'Injury/Theft team',
    comments: 'Please upload the passenger’s medical note confirming the wrist injury so our team can complete the assessment.',
    photos: ['front-damage.jpg', 'side-view.jpg', 'incident-scene.jpg']
  },
  {
    id: 'TC-2026-1046', claimant: 'Lebo Nkosi', initials: 'LN', email: 'lebo.nkosi@email.com',
    vehicle: '2021 Mazda Demio', registration: 'KBX 291A', policyNumber: 'POL-2026-07731',
    incidentDate: '6 Oct 2026', incidentTime: '17:20', incidentType: 'Collision', location: 'Ngong Road, Nairobi',
    description: 'A vehicle changed lanes and damaged the passenger-side door.', submitted: '6 Oct 2026 · 16:40',
    amount: 22000, status: 'Under review', priority: 'High', queue: 'Injury/Theft', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: true, policeReport: 'CAS 179/10/2026', officer: 'Daniel Brooks', officerTeam: 'Injury/Theft team',
    comments: 'Evidence received. Assessment is in progress.', photos: ['side-view.jpg']
  },
  {
    id: 'TC-2026-1049', claimant: 'James Smith', initials: 'JS', email: 'james.smith@email.com',
    vehicle: '2019 Nissan Note', registration: 'KDA 509G', policyNumber: 'POL-2026-09012',
    incidentDate: '8 Oct 2026', incidentTime: '11:10', incidentType: 'Collision', location: 'Westlands, Nairobi',
    description: 'Damage to the rear bumper following a low-speed collision.', submitted: '8 Oct 2026 · 11:45',
    amount: 95000, status: 'Under review', priority: 'High', queue: 'Major Damage', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: true, policeReport: 'CAS 190/10/2026', officer: 'Sarah Adams', officerTeam: 'Major Damage team',
    comments: 'Repair estimate requested.', photos: ['front-damage.jpg']
  },
  {
    id: 'TC-2026-1053', claimant: 'Sarah Adams', initials: 'SA', email: 'sarah.adams@email.com',
    vehicle: '2018 Toyota Vitz', registration: 'KCY 117M', policyNumber: 'POL-2026-07210',
    incidentDate: '9 Oct 2026', incidentTime: '06:50', incidentType: 'Theft', location: 'Kilimani, Nairobi',
    description: 'Vehicle was reported stolen overnight.', submitted: '9 Oct 2026 · 07:35',
    amount: 220000, status: 'Submitted', priority: 'High', queue: 'Injury/Theft', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: false, policeReport: 'OB 044/09/10/2026', officer: 'Unassigned', officerTeam: 'Injury/Theft team',
    comments: 'Awaiting initial review.', photos: ['incident-scene.jpg']
  },
  {
    id: 'TC-2026-1042', claimant: 'Mia Jacobs', initials: 'MJ', email: 'mia.jacobs@email.com',
    vehicle: '2020 Honda Fit', registration: 'KDG 912P', policyNumber: 'POL-2026-08200',
    incidentDate: '5 Oct 2026', incidentTime: '14:10', incidentType: 'Vandalism', location: 'Kileleshwa, Nairobi',
    description: 'Side windows and mirrors were damaged while parked.', submitted: '5 Oct 2026 · 15:10',
    amount: 18000, status: 'Under review', priority: 'Medium', queue: 'Major Damage', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: false, policeReport: 'CAS 171/10/2026', officer: 'Daniel Brooks', officerTeam: 'Major Damage team',
    comments: 'Awaiting assessor notes.', photos: ['side-view.jpg']
  },
  {
    id: 'TC-2026-1050', claimant: 'Noah Williams', initials: 'NW', email: 'noah.williams@email.com',
    vehicle: '2022 Toyota Axio', registration: 'KDK 301Q', policyNumber: 'POL-2026-09020',
    incidentDate: '8 Oct 2026', incidentTime: '09:30', incidentType: 'Fire', location: 'Parklands, Nairobi',
    description: 'Engine bay sustained fire damage.', submitted: '8 Oct 2026 · 10:20',
    amount: 32000, status: 'Submitted', priority: 'Medium', queue: 'Major Damage', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: false, policeReport: 'CAS 188/10/2026', officer: 'Unassigned', officerTeam: 'Major Damage team',
    comments: 'Awaiting initial review.', photos: ['front-damage.jpg']
  },
  {
    id: 'TC-2026-1040', claimant: 'Ethan Naidoo', initials: 'EN', email: 'ethan.naidoo@email.com',
    vehicle: '2017 Subaru Impreza', registration: 'KDA 305B', policyNumber: 'POL-2026-07810',
    incidentDate: '5 Oct 2026', incidentTime: '18:20', incidentType: 'Collision', location: 'Mombasa Road, Nairobi',
    description: 'Minor scrape to rear side panel.', submitted: '5 Oct 2026 · 18:55',
    amount: 23500, status: 'Under review', priority: 'Low', queue: 'Minor Damage', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: false, policeReport: 'CAS 168/10/2026', officer: 'Daniel Brooks', officerTeam: 'Minor Damage team',
    comments: 'Review in progress.', photos: ['side-view.jpg']
  },
  {
    id: 'TC-2026-1052', claimant: 'Chloe Wilson', initials: 'CW', email: 'chloe.wilson@email.com',
    vehicle: '2015 Toyota Passo', registration: 'KCB 440X', policyNumber: 'POL-2026-09111',
    incidentDate: '9 Oct 2026', incidentTime: '12:00', incidentType: 'Collision', location: 'CBD, Nairobi',
    description: 'Minor damage to rear bumper.', submitted: '9 Oct 2026 · 12:35',
    amount: 8200, status: 'Submitted', priority: 'Low', queue: 'Minor Damage', insurer: 'Zurika Motor Insurance',
    injury: false, thirdParty: false, policeReport: 'CAS 194/10/2026', officer: 'Unassigned', officerTeam: 'Minor Damage team',
    comments: 'Awaiting initial review.', photos: ['incident-scene.jpg']
  }
];

export const routingRules = [
  { order: 1, condition: 'Injury = Yes', description: 'Always takes precedence over incident type and amount.', priority: 'High', team: 'Injury/Theft', enabled: true },
  { order: 2, condition: 'Incident type = Theft', description: 'Applies when no injury rule has matched.', priority: 'High', team: 'Injury/Theft', enabled: true },
  { order: 3, condition: 'Amount ≥ 50,000', description: 'Major damage; only when no injury or theft rule matches.', priority: 'High', team: 'Major Damage', enabled: true },
  { order: 4, condition: 'Incident type = Fire or Vandalism', description: 'Below threshold; specialist damage assessment.', priority: 'Medium', team: 'Major Damage', enabled: true },
  { order: 5, condition: 'Amount below 50,000', description: 'Remaining non-injury, non-theft collision claims.', priority: 'Low', team: 'Minor Damage', enabled: true },
  { order: 6, condition: 'Legacy: Amount ≥ 100,000', description: 'Disabled. Replaced by the major damage threshold above.', priority: 'High', team: 'Major Damage', enabled: false }
];

export const money = (amount: number) => new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(amount);
