export type UserRole = 'client' | 'claims_officer' | 'senior_officer' | 'admin';
export type ClaimStatus = 'Submitted' | 'Under review' | 'More info requested' | 'Assessment' | 'Approved' | 'Rejected' | 'Closed';
export type Priority = 'High' | 'Medium' | 'Low';
export interface ClaimRecord {
  id: string;
  claimant: string;
  initials: string;
  email: string;
  vehicle: string;
  registration: string;
  policyNumber: string;
  incidentDate: string;
  incidentTime: string;
  incidentType: string;
  location: string;
  description: string;
  submitted: string;
  amount: number;
  status: ClaimStatus;
  priority: Priority;
  queue: string;
  insurer: string;
  injury: boolean;
  thirdParty: boolean;
  policeReport: string;
  officer: string;
  officerTeam: string;
  comments: string;
  photos: string[];
}
export interface NavItem { label: string; path: string; icon: string; roles: UserRole[]; }
