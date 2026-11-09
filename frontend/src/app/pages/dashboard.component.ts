import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { claims, money } from '../mock-data';
import { RoleService } from '../core/role.service';
import { ClaimStatus, UserRole } from '../models';

@Component({
  selector: 'app-dashboard', standalone: true, imports: [CommonModule, RouterLink],
  template: `
  <section class="page-wrap">
    <ng-container *ngIf="role === 'client'; else staffDashboard">
      <div class="page-heading-row">
        <div><div class="eyebrow">FRIDAY, 9 OCTOBER 2026</div><h1 class="page-title">Good morning, Amina</h1><p class="page-subtitle">Here's the latest on your motor claims.</p></div>
        <a routerLink="/claims/new" class="btn-primary"><span>＋</span> File a New Claim</a>
      </div>
      <div class="metric-grid three">
        <article class="metric-card"><div class="metric-top"><span>Active Claims</span><span class="metric-icon">▣</span></div><div class="metric-value">3</div><div class="metric-foot">Claims currently being processed</div></article>
        <article class="metric-card"><div class="metric-top"><span>Approved</span><span class="metric-icon">✓</span></div><div class="metric-value">2</div><div class="metric-foot">Approved claims this year</div></article>
        <article class="metric-card"><div class="metric-top"><span>Pending Documents</span><span class="metric-icon">▤</span></div><div class="metric-value">1</div><div class="metric-foot">One claim needs your attention</div></article>
      </div>
      <div class="notice notice-warning"><span class="notice-icon">!</span><div><strong>A document is needed for TC-2026-1048</strong><p>Daniel Brooks requested a medical note on 8 October. Upload it to keep your claim moving.</p></div><a routerLink="/claims/TC-2026-1048" class="btn-outline small">View claim</a></div>
      <section class="panel table-panel">
        <div class="panel-heading"><div><h2 class="panel-title">Recent Claims</h2><p class="panel-subtitle">Your five most recent claims</p></div><a routerLink="/claims" class="text-link">View all claims</a></div>
        <div class="table-scroll"><table class="data-table customer-table"><thead><tr><th>Claim ID</th><th>Date submitted</th><th>Vehicle</th><th>Status</th><th></th></tr></thead><tbody>
          <tr *ngFor="let claim of customerClaims"><td><strong class="table-primary">{{claim.id}}</strong></td><td>{{claim.submitted.split(' · ')[0]}}</td><td><strong>{{claim.registration}}</strong><small>{{claim.vehicle}}</small></td><td><span class="status-pill" [ngClass]="statusClass(claim.status)">{{claim.status}}</span></td><td><a [routerLink]="['/claims', claim.id]" class="text-link">View →</a></td></tr>
        </tbody></table></div>
        <div class="table-footer"><span>Showing 1–5 of 7 claims</span><span>Updated today at 08:30</span></div>
      </section>
      <div class="policy-footer">◈ &nbsp; Policy POL-2026-08421 · 2022 Toyota Corolla · CA 482-716 · Cover active until 31 Dec 2026</div>
    </ng-container>

    <ng-template #staffDashboard>
      <ng-container *ngIf="role === 'claims_officer'; else seniorOrAdmin">
        <div class="page-heading-row">
          <div><div class="eyebrow">FRIDAY, 9 OCTOBER 2026</div><h1 class="page-title">Good morning, Daniel</h1><p class="page-subtitle">Your team's workload at a glance. Start with the claims that need attention.</p></div>
          <a routerLink="/claims" class="btn-primary">→ &nbsp; Open claims queue</a>
        </div>
        <div class="metric-grid four">
          <article class="metric-card"><div class="metric-top"><span>New Claims</span><span class="metric-icon">▱</span></div><div class="metric-value">8</div><div class="metric-foot">Awaiting first review</div></article>
          <article class="metric-card"><div class="metric-top"><span>High Priority</span><span class="metric-icon">⚑</span></div><div class="metric-value">6</div><div class="metric-foot">Across all open claims</div></article>
          <article class="metric-card"><div class="metric-top"><span>In Review</span><span class="metric-icon">▤</span></div><div class="metric-value">12</div><div class="metric-foot">Assigned and being assessed</div></article>
          <article class="metric-card"><div class="metric-top"><span>Closed Today</span><span class="metric-icon">▣</span></div><div class="metric-value">4</div><div class="metric-foot">Completed on 9 October</div></article>
        </div>
        <div class="dashboard-split">
          <section class="panel priority-panel"><div class="panel-heading"><div><h2 class="panel-title">Claims by priority</h2><p class="panel-subtitle">Open workload · All teams</p></div></div>
            <div class="bar-chart"><div class="bar-col"><span>6</span><div class="bar red" style="height:112px"></div><small>High</small></div><div class="bar-col"><span>10</span><div class="bar amber" style="height:166px"></div><small>Medium</small></div><div class="bar-col"><span>8</span><div class="bar slate" style="height:137px"></div><small>Low</small></div></div>
            <div class="panel-note">24 open claims · Automatically assigned by routing rules</div>
          </section>
          <section class="panel assigned-panel"><div class="panel-heading"><div><h2 class="panel-title">Assigned to Me</h2><p class="panel-subtitle">3 claims · Injury/Theft &amp; Major Damage</p></div><span class="soft-count">3 open</span></div>
            <div class="assigned-item" *ngFor="let claim of assignedClaims"><div><strong>{{claim.id}} · {{claim.claimant}}</strong><span>{{claim.incidentType}} · {{money(claim.amount)}} · {{claim.queue}}</span><div class="tag-row"><span class="priority-pill" [ngClass]="priorityClass(claim.priority)">{{claim.priority}}</span><span class="status-pill" [ngClass]="statusClass(claim.status)">{{claim.status}}</span></div></div><a [routerLink]="['/claims',claim.id]" class="text-link">Review</a></div>
          </section>
        </div>
        <section class="panel insight-panel"><strong>A clear path for every claim</strong><p>Triage keeps the right work with the right team.</p><span>8 new + 12 in review + 4 awaiting information = 24 open claims. Injury and theft cases take precedence over damage amount rules.</span></section>
      </ng-container>
    </ng-template>

    <ng-template #seniorOrAdmin>
      <div class="page-heading-row"><div><div class="eyebrow">CLAIMS OPERATIONS</div><h1 class="page-title">{{role === 'admin' ? 'Workspace overview' : 'Good morning, Sarah'}}</h1><p class="page-subtitle">{{role === 'admin' ? 'A clear view of claims, settlements and insurer operations.' : 'Monitor escalations, decisions and the work requiring senior attention.'}}</p></div><a routerLink="/reviews" class="btn-primary">{{role === 'admin' ? 'View operations' : 'Review approvals →'}}</a></div>
      <div class="metric-grid four">
        <article class="metric-card"><div class="metric-top"><span>{{role === 'admin' ? 'Total Claims' : 'Escalated Claims'}}</span><span class="metric-icon">▤</span></div><div class="metric-value">{{role === 'admin' ? '248' : '12'}}</div><div class="metric-foot">Across all active teams</div></article>
        <article class="metric-card"><div class="metric-top"><span>Awaiting Decision</span><span class="metric-icon">◷</span></div><div class="metric-value">9</div><div class="metric-foot">Need senior review</div></article>
        <article class="metric-card"><div class="metric-top"><span>Approved This Month</span><span class="metric-icon">✓</span></div><div class="metric-value">84</div><div class="metric-foot">Decisions completed</div></article>
        <article class="metric-card"><div class="metric-top"><span>Pending Payouts</span><span class="metric-icon">↗</span></div><div class="metric-value">6</div><div class="metric-foot">Ready for settlement</div></article>
      </div>
      <div class="dashboard-split">
        <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Senior review required</h2><p class="panel-subtitle">Escalations and decisions waiting for approval</p></div><a routerLink="/reviews" class="text-link">View queue</a></div>
          <div class="assigned-item" *ngFor="let claim of seniorClaims"><div><strong>{{claim.id}} · {{claim.claimant}}</strong><span>{{claim.incidentType}} · {{money(claim.amount)}} · {{claim.queue}}</span><div class="tag-row"><span class="priority-pill" [ngClass]="priorityClass(claim.priority)">{{claim.priority}} priority</span><span class="status-pill" [ngClass]="statusClass(claim.status)">{{claim.status}}</span></div></div><a [routerLink]="['/claims',claim.id]" class="text-link">Review</a></div>
        </section>
        <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Settlement overview</h2><p class="panel-subtitle">Payout activity this month</p></div></div><div class="settlement-total">KES 2,840,500</div><p class="panel-subtitle">Total settled · October 2026</p><div class="settlement-row"><span>Awaiting payment</span><strong>KES 468,000</strong></div><div class="settlement-row"><span>Processing</span><strong>KES 192,500</strong></div><div class="settlement-row"><span>Reconciliation required</span><strong class="text-red">1 payout</strong></div><a routerLink="/payouts" class="text-link block mt-4">Open payouts →</a></section>
      </div>
    </ng-template>
  </section>`
})
export class DashboardComponent {
  role: UserRole;
  money = money;
  customerClaims = claims.slice(0, 5);
  assignedClaims = claims.filter(c => c.officer === 'Daniel Brooks').slice(0, 3);
  seniorClaims = claims.filter(c => c.priority === 'High').slice(0, 4);
  constructor(private roleService: RoleService) { this.role = this.roleService.role; this.roleService.role$.subscribe(role => this.role = role); }
  statusClass(status: ClaimStatus): string {
    return status === 'Approved' ? 'status-green' : status === 'Under review' || status === 'Assessment' ? 'status-blue' : status === 'More info requested' || status === 'Submitted' ? 'status-amber' : status === 'Rejected' ? 'status-red' : 'status-muted';
  }
  priorityClass(priority: string): string { return priority === 'High' ? 'priority-red' : priority === 'Medium' ? 'priority-amber' : 'priority-muted'; }
}
