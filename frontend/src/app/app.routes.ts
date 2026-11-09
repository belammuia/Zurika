import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard.component';
import { ClaimsComponent } from './pages/claims.component';
import { ClaimDetailComponent } from './pages/claim-detail.component';
import { SubmitClaimComponent } from './pages/submit-claim.component';
import { WorkspaceComponent } from './pages/workspace.component';

export const routes: Routes = [
  { path: '', component: DashboardComponent, title: 'Dashboard · Zurika' },
  { path: 'login', component: WorkspaceComponent, data: { section: 'Welcome back' }, title: 'Sign in · Zurika' },
  { path: 'claims', component: ClaimsComponent, title: 'Claims · Zurika' },
  { path: 'claims/new', component: SubmitClaimComponent, title: 'File a claim · Zurika' },
  { path: 'claims/:id', component: ClaimDetailComponent, title: 'Claim details · Zurika' },
  { path: 'routing', component: WorkspaceComponent, data: { section: 'Routing Rules', description: 'Control how claims are prioritised and assigned.' }, title: 'Routing Rules · Zurika' },
  { path: 'reviews', component: WorkspaceComponent, data: { section: 'Approvals', description: 'Review escalated claims and record senior decisions.' }, title: 'Approvals · Zurika' },
  { path: 'payouts', component: WorkspaceComponent, data: { section: 'Payouts', description: 'Track approved settlements and payment progress.' }, title: 'Payouts · Zurika' },
  { path: 'documents', component: WorkspaceComponent, data: { section: 'Documents', description: 'Keep every claim document organised, accessible and accounted for.' }, title: 'Documents · Zurika' },
  { path: 'team', component: WorkspaceComponent, data: { section: 'Team & access', description: 'Manage staff, roles and insurer membership access.' }, title: 'Team · Zurika' },
  { path: 'insurers', component: WorkspaceComponent, data: { section: 'Insurers', description: 'Manage insurer organisations connected to Zurika.' }, title: 'Insurers · Zurika' },
  { path: 'audit', component: WorkspaceComponent, data: { section: 'Audit trail', description: 'A recorded history of important actions and claim decisions.' }, title: 'Audit trail · Zurika' },
  { path: 'settings', component: WorkspaceComponent, data: { section: 'Settings', description: 'Manage workspace preferences and account details.' }, title: 'Settings · Zurika' },
  { path: 'help', component: WorkspaceComponent, data: { section: 'Help & support', description: 'Get help with submitting and managing motor claims.' }, title: 'Help · Zurika' },
  { path: '**', redirectTo: '' }
];
