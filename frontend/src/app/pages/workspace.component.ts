import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { claims, money, routingRules } from '../mock-data';

@Component({
  selector: 'app-workspace', standalone: true, imports: [CommonModule, RouterLink, FormsModule],
  template: `
  <div class="page-wrap workspace-wrap">
    <ng-container *ngIf="section === 'Welcome back'; else normalWorkspace">
      <div class="login-screen"><div class="login-card"><div class="login-brand"><span class="brand-symbol">Z</span><span class="brand-name">zurika<span>.</span></span></div><h1>Welcome back</h1><p class="login-lead">Sign in to file, track or manage motor claims.</p><div class="login-label">Sign in as</div><div class="login-tabs"><button [class.selected]="loginRole==='Customer'" (click)="loginRole='Customer'">Customer</button><button [class.selected]="loginRole==='Claims Officer'" (click)="loginRole='Claims Officer'">Claims Officer</button></div><small class="login-hint">Policyholders use Customer. Staff use Claims Officer.</small><label class="field login-field"><span>Email address</span><input type="email" [(ngModel)]="email" placeholder="amina.patel@email.com"></label><label class="field login-field"><span>Password</span><div class="password-field"><input [type]="showPassword ? 'text' : 'password'" [(ngModel)]="password" placeholder="Enter your password"><button type="button" (click)="showPassword=!showPassword">{{showPassword ? 'Hide' : 'Show'}}</button></div></label><button class="forgot-link" (click)="notice='Password reset instructions would be sent by the connected authentication service.'">Forgot password</button><button class="btn-primary login-submit" (click)="signIn()">→ &nbsp; Sign in as {{loginRole}}</button><div class="login-security">♙ &nbsp; Secure access · Your policy and claims information stays private</div><p *ngIf="notice" class="login-notice">{{notice}}</p></div></div>
    </ng-container>

    <ng-template #normalWorkspace>
      <ng-container *ngIf="section === 'Routing Rules'; else otherWorkspace">
        <div class="page-heading-row"><div><h1 class="page-title">Routing Rules</h1><p class="page-subtitle">Control how new motor claims are prioritised and assigned to teams.</p></div><button class="btn-primary" (click)="showRuleEditor = !showRuleEditor">＋ &nbsp; Add Rule</button></div>
        <div class="notice notice-info"><span class="notice-icon">ⓘ</span><div><strong>First matching enabled rule wins</strong><p>Rules run from top to bottom. Injury routing comes first, followed by theft, major damage and other damage rules. Changes apply to new claims only.</p></div></div>
        <section *ngIf="showRuleEditor" class="panel rule-editor"><div class="panel-heading"><h2 class="panel-title">{{editingRuleIndex === null ? 'Add routing rule' : 'Edit routing rule'}}</h2><button class="icon-close" (click)="closeRuleEditor()">×</button></div><div class="form-grid"><label class="field"><span>Condition</span><input [(ngModel)]="ruleForm.condition" placeholder="e.g. Amount ≥ 50,000"></label><label class="field"><span>Priority</span><select [(ngModel)]="ruleForm.priority"><option>High</option><option>Medium</option><option>Low</option></select></label><label class="field"><span>Routed team</span><select [(ngModel)]="ruleForm.team"><option>Injury/Theft</option><option>Major Damage</option><option>Minor Damage</option><option>Manual Review</option></select></label><label class="field"><span>Description</span><input [(ngModel)]="ruleForm.description" placeholder="Explain when the rule applies"></label></div><div class="form-actions"><button class="btn-outline" (click)="closeRuleEditor()">Cancel</button><button class="btn-primary" (click)="saveRule()">Save rule</button></div></section>
        <section class="panel rule-panel"><div class="panel-heading"><div><h2 class="panel-title">Triage &amp; routing</h2><p class="panel-subtitle">{{enabledRuleCount}} enabled rules · Evaluated in the order shown · Amounts in KSh</p></div></div><div class="table-scroll"><table class="data-table routing-table"><thead><tr><th>Order</th><th>Condition</th><th>Priority</th><th>Routed team</th><th>Enabled</th><th>Action</th></tr></thead><tbody><tr *ngFor="let rule of rules; let i=index"><td>{{rule.order}}</td><td><strong class="table-primary">{{rule.condition}}</strong><small>{{rule.description}}</small></td><td><span class="priority-pill" [ngClass]="priorityClass(rule.priority)">{{rule.priority}}</span></td><td>{{rule.team}}</td><td><button class="toggle-switch" [class.on]="rule.enabled" [attr.aria-label]="(rule.enabled ? 'Disable' : 'Enable') + ' rule ' + rule.order" (click)="rule.enabled=!rule.enabled"><i></i></button><small class="toggle-label">{{rule.enabled ? 'On' : 'Off'}}</small></td><td><button class="text-link" (click)="editRule(i)">Edit</button></td></tr></tbody></table></div><p class="rule-footnote">If no enabled rule matches, send the claim to manual triage. Missing injury or amount data must never default to Low priority.</p></section>
        <section class="panel routing-examples"><h2 class="panel-title">Routing examples</h2><p><strong>Injury = Yes</strong> → High priority → Injury/Theft team</p><p><strong>Amount below 50,000</strong> → Low priority → Minor Damage team</p><p class="panel-subtitle">The amount example applies only after earlier rules are excluded. TC-2026-1048 has an injury and KSh 68,500 damage; Injury/Theft wins over Major Damage.</p></section>
      </ng-container>
    </ng-template>

    <ng-template #otherWorkspace>
      <div class="page-heading-row"><div><h1 class="page-title">{{section}}</h1><p class="page-subtitle">{{description}}</p></div><button class="btn-outline" *ngIf="section!=='Audit trail'" (click)="notice='This action is available in the frontend prototype.'">{{section==='Payouts' ? '⇩ Export payouts' : '＋ Add new'}}</button></div>
      <ng-container [ngSwitch]="section">
        <ng-container *ngSwitchCase="'Payouts'">
          <div class="metric-grid three"><article class="metric-card"><div class="metric-top"><span>Pending</span><span class="metric-icon">◷</span></div><div class="metric-value">6</div><div class="metric-foot">Awaiting processing</div></article><article class="metric-card"><div class="metric-top"><span>Processing</span><span class="metric-icon">↗</span></div><div class="metric-value">3</div><div class="metric-foot">Payment in progress</div></article><article class="metric-card"><div class="metric-top"><span>Paid this month</span><span class="metric-icon">✓</span></div><div class="metric-value">57</div><div class="metric-foot">KES 2,840,500 settled</div></article></div>
          <section class="panel table-panel"><div class="panel-heading"><div><h2 class="panel-title">Recent payouts</h2><p class="panel-subtitle">Approved claims and settlement status</p></div></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Payout ID</th><th>Claim ID</th><th>Beneficiary</th><th>Amount</th><th>Method</th><th>Destination</th><th>Status</th><th></th></tr></thead><tbody><tr *ngFor="let p of payoutRows"><td><strong>{{p.id}}</strong></td><td>{{p.claim}}</td><td>{{p.name}}</td><td>{{money(p.amount)}}</td><td>{{p.method}}</td><td>{{p.destination}}</td><td><span class="status-pill" [ngClass]="p.status==='Paid'?'status-green':p.status==='Processing'?'status-blue':p.status==='Unknown'?'status-red':'status-amber'">{{p.status}}</span></td><td><button class="text-link" (click)="notice='Payout details opened in prototype.'">View</button></td></tr></tbody></table></div></section>
          <div class="notice notice-info"><span class="notice-icon">ⓘ</span><div><strong>Settlement method</strong><p>Claims up to KSh 250,000 are prepared for M-Pesa. Higher-value settlements are routed through bank transfer.</p></div></div>
        </ng-container>
        <ng-container *ngSwitchCase="'Approvals'">
          <div class="metric-grid three"><article class="metric-card"><div class="metric-top"><span>Awaiting decision</span><span class="metric-icon">◷</span></div><div class="metric-value">9</div><div class="metric-foot">Requires senior review</div></article><article class="metric-card"><div class="metric-top"><span>Approved today</span><span class="metric-icon">✓</span></div><div class="metric-value">4</div><div class="metric-foot">Decisions completed</div></article><article class="metric-card"><div class="metric-top"><span>Escalated</span><span class="metric-icon">⚑</span></div><div class="metric-value">3</div><div class="metric-foot">Specialist attention</div></article></div>
          <section class="panel table-panel"><div class="panel-heading"><div><h2 class="panel-title">Approval queue</h2><p class="panel-subtitle">Claims requiring a senior decision</p></div></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Claim ID</th><th>Customer</th><th>Routed team</th><th>Estimated amount</th><th>Priority</th><th>Status</th><th>Action</th></tr></thead><tbody><tr *ngFor="let c of claims"><td><strong>{{c.id}}</strong></td><td>{{c.claimant}}</td><td>{{c.queue}}</td><td>{{money(c.amount)}}</td><td><span class="priority-pill" [ngClass]="priorityClass(c.priority)">{{c.priority}}</span></td><td><span class="status-pill status-amber">{{c.status}}</span></td><td><a [routerLink]="['/claims',c.id]" class="text-link">Review →</a></td></tr></tbody></table></div></section>
        </ng-container>
        <ng-container *ngSwitchCase="'Documents'">
          <section class="panel table-panel"><div class="panel-heading"><div><h2 class="panel-title">Document register</h2><p class="panel-subtitle">Evidence submitted against motor claims</p></div></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Document</th><th>Claim ID</th><th>Type</th><th>Uploaded by</th><th>Date uploaded</th><th>Status</th><th></th></tr></thead><tbody><tr *ngFor="let d of documents"><td><strong>{{d.name}}</strong><small>{{d.size}}</small></td><td>{{d.claim}}</td><td>{{d.type}}</td><td>{{d.owner}}</td><td>{{d.date}}</td><td><span class="status-pill" [ngClass]="d.status==='Verified'?'status-green':'status-amber'">{{d.status}}</span></td><td><button class="download-button">↓</button></td></tr></tbody></table></div></section>
        </ng-container>
        <ng-container *ngSwitchCase="'Team & access'">
          <section class="panel table-panel"><div class="panel-heading"><div><h2 class="panel-title">Team members</h2><p class="panel-subtitle">Manage staff access and insurer membership roles.</p></div><button class="btn-primary small" (click)="showMemberForm=!showMemberForm">＋ Add member</button></div><div *ngIf="showMemberForm" class="inline-editor"><label class="field"><span>Member email</span><input [(ngModel)]="memberEmail" placeholder="name@insurer.com"></label><label class="field"><span>Role</span><select [(ngModel)]="memberRole"><option>Claims Officer</option><option>Senior Claims Officer</option><option>Insurer Admin</option></select></label><button class="btn-primary small" (click)="addMember()">Invite member</button></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Availability</th><th>Status</th></tr></thead><tbody><tr *ngFor="let m of team"><td><strong>{{m.name}}</strong></td><td>{{m.email}}</td><td>{{m.role}}</td><td>{{m.availability}}</td><td><span class="status-pill status-green">Active</span></td></tr></tbody></table></div></section>
        </ng-container>
        <ng-container *ngSwitchCase="'Insurers'">
          <section class="panel table-panel"><div class="panel-heading"><div><h2 class="panel-title">Insurer organisations</h2><p class="panel-subtitle">Insurers connected to the Zurika claims platform</p></div><button class="btn-primary small" (click)="notice='Insurer setup is represented here as a prototype.'">＋ Add insurer</button></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Insurer</th><th>Organisation code</th><th>Members</th><th>Active claims</th><th>Status</th></tr></thead><tbody><tr *ngFor="let i of insurers"><td><strong>{{i.name}}</strong></td><td>{{i.code}}</td><td>{{i.members}}</td><td>{{i.claims}}</td><td><span class="status-pill status-green">Active</span></td></tr></tbody></table></div></section>
        </ng-container>
        <ng-container *ngSwitchCase="'Audit trail'">
          <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Recent activity</h2><p class="panel-subtitle">Recorded actions across claims and payouts</p></div><button class="btn-outline small" (click)="notice='Audit export prepared in the prototype.'">⇩ Export log</button></div><div class="audit-list"><div *ngFor="let a of audit" class="audit-row"><span class="audit-dot"></span><div><strong>{{a.action}}</strong><p>{{a.detail}}</p><span>{{a.actor}} · {{a.date}}</span></div><span class="audit-ref">{{a.reference}}</span></div></div></section>
        </ng-container>
        <ng-container *ngSwitchDefault>
          <section class="panel"><h2 class="panel-title">{{section}} workspace</h2><p class="panel-subtitle">{{description}} This is a local frontend prototype.</p></section>
        </ng-container>
      </ng-container>
    </ng-template>
    <div *ngIf="notice" class="toast" (click)="notice=''">{{notice}} <button aria-label="Dismiss">×</button></div>
  </div>`
})
export class WorkspaceComponent {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  section = 'Workspace'; description = ''; icon = '▤'; notice = '';
  loginRole = 'Customer'; email = 'amina.patel@email.com'; password = 'password123'; showPassword = false;
  showRuleEditor = false; editingRuleIndex: number | null = null;
  ruleForm = { condition: '', description: '', priority: 'High', team: 'Major Damage' };
  rules = routingRules.map(rule => ({ ...rule }));
  showMemberForm = false; memberEmail = ''; memberRole = 'Claims Officer';
  money = money; claims = claims;
  payoutRows = [
    { id: 'PAY-2026-0284', claim: 'TC-2026-1039', name: 'Grace Wanjiku', amount: 125000, method: 'M-Pesa', destination: '+254 712 ••• 482', status: 'Paid' },
    { id: 'PAY-2026-0283', claim: 'TC-2026-1036', name: 'Peter Kamau', amount: 68000, method: 'M-Pesa', destination: '+254 722 ••• 110', status: 'Processing' },
    { id: 'PAY-2026-0282', claim: 'TC-2026-1029', name: 'Faith Njeri', amount: 310000, method: 'Bank', destination: 'Absa · •••• 2914', status: 'Pending' },
    { id: 'PAY-2026-0281', claim: 'TC-2026-1024', name: 'David Mwangi', amount: 48000, method: 'M-Pesa', destination: '+254 701 ••• 651', status: 'Unknown' }
  ];
  documents = [
    { name: 'police-report.pdf', size: '1.4 MB', claim: 'TC-2026-1048', type: 'Police abstract', owner: 'Amina Patel', date: '7 Oct 2026', status: 'Verified' },
    { name: 'repair-estimate.pdf', size: '840 KB', claim: 'TC-2026-1048', type: 'Repair estimate', owner: 'Amina Patel', date: '7 Oct 2026', status: 'Verified' },
    { name: 'medical-note.pdf', size: '—', claim: 'TC-2026-1048', type: 'Medical report', owner: 'Amina Patel', date: 'Requested', status: 'Requested' },
    { name: 'vehicle-photos.zip', size: '7.2 MB', claim: 'TC-2026-1046', type: 'Damage photos', owner: 'Lebo Nkosi', date: '6 Oct 2026', status: 'Verified' }
  ];
  team = [
    { name: 'Daniel Brooks', email: 'daniel.brooks@zurika.co.ke', role: 'Claims Officer', availability: 'Available' },
    { name: 'Sarah Adams', email: 'sarah.adams@zurika.co.ke', role: 'Senior Claims Officer', availability: 'Busy' },
    { name: 'Mia Jacobs', email: 'mia.jacobs@zurika.co.ke', role: 'Claims Officer', availability: 'Available' }
  ];
  insurers = [
    { name: 'Zurika Motor Insurance', code: 'ZURIKA-001', members: 18, claims: 124 },
    { name: 'Turaco Insurance', code: 'TURACO-014', members: 9, claims: 64 },
    { name: 'Britam General Insurance', code: 'BRITAM-008', members: 12, claims: 60 }
  ];
  audit = [
    { action: 'More information requested', detail: 'Medical note requested for claim TC-2026-1048.', actor: 'Daniel Brooks', date: '8 Oct 2026 · 10:30', reference: 'TC-2026-1048' },
    { action: 'Claim automatically routed', detail: 'Priority High · Injury/Theft team.', actor: 'Zurika routing engine', date: '7 Oct 2026 · 09:12', reference: 'TC-2026-1048' },
    { action: 'Payout marked as processing', detail: 'M-Pesa settlement initiated.', actor: 'Payments service', date: '7 Oct 2026 · 08:45', reference: 'PAY-2026-0283' }
  ];
  constructor() { this.route.data.subscribe(data => { this.section = String(data['section'] ?? 'Workspace'); this.description = String(data['description'] ?? ''); this.icon = String(data['icon'] ?? '▤'); }); }
  signIn(): void { this.router.navigateByUrl('/'); }
  closeRuleEditor(): void { this.showRuleEditor = false; this.editingRuleIndex = null; this.ruleForm = { condition: '', description: '', priority: 'High', team: 'Major Damage' }; }
  editRule(index: number): void { const r = this.rules[index]; this.editingRuleIndex = index; this.ruleForm = { condition: r.condition, description: r.description, priority: r.priority, team: r.team }; this.showRuleEditor = true; }
  saveRule(): void {
    if (!this.ruleForm.condition.trim()) { this.notice = 'Add a condition before saving the rule.'; return; }
    if (this.editingRuleIndex === null) this.rules.push({ order: this.rules.length + 1, ...this.ruleForm, enabled: true });
    else this.rules[this.editingRuleIndex] = { ...this.rules[this.editingRuleIndex], ...this.ruleForm };
    this.closeRuleEditor(); this.notice = 'Routing rule saved locally. Existing claims are not changed.';
  }
  addMember(): void { if (!this.memberEmail.trim()) { this.notice = 'Enter an email address to invite a member.'; return; } this.team.push({ name: this.memberEmail.split('@')[0], email: this.memberEmail, role: this.memberRole, availability: 'Available' }); this.memberEmail = ''; this.showMemberForm = false; this.notice = 'Team member added to this prototype.'; }
  get enabledRuleCount(): number { return this.rules.filter(rule => rule.enabled).length; }
  priorityClass(priority: string): string { return priority === 'High' ? 'priority-red' : priority === 'Medium' ? 'priority-amber' : 'priority-muted'; }
}
