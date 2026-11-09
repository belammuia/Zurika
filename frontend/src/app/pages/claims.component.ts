import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { claims, money } from '../mock-data';
import { RoleService } from '../core/role.service';
import { ClaimRecord, ClaimStatus, UserRole } from '../models';

@Component({
  selector: 'app-claims', standalone: true, imports: [CommonModule, RouterLink, FormsModule],
  template: `
  <div class="page-wrap">
    <div class="page-heading-row"><div><h1 class="page-title">{{role === 'client' ? 'My Claims' : role === 'admin' ? 'All Claims' : 'Claims Queue'}}</h1><p class="page-subtitle">{{role === 'client' ? 'Search your claims and follow their progress, from submission to decision.' : 'Review automatically prioritised claims and their assigned teams.'}}</p></div><a *ngIf="role === 'client'" routerLink="/claims/new" class="btn-primary">＋ &nbsp; File a New Claim</a><button *ngIf="role !== 'client'" class="btn-outline" (click)="notice='A queue export has been prepared in this prototype.'">⇩ &nbsp; Export queue</button></div>

    <section class="panel queue-panel">
      <div class="queue-summary"><div><h2>{{role === 'client' ? 'All claims' : 'Open claims'}}</h2><p>{{role === 'client' ? '7 claims · 3 active · 1 awaiting documents' : filtered.length + ' open · Sorted by priority, then oldest first'}}</p></div></div>
      <div class="filter-bar">
        <label class="search-wrap"><span>⌕</span><input [(ngModel)]="search" [placeholder]="role === 'client' ? 'Search claim ID or vehicle' : 'Search claim ID or customer'" aria-label="Search claims"></label>
        <select class="filter-select" [(ngModel)]="statusFilter"><option value="All">Status: All statuses</option><option>Submitted</option><option>Under review</option><option>More info requested</option><option>Approved</option><option>Rejected</option><option>Closed</option></select>
        <select *ngIf="role !== 'client'" class="filter-select" [(ngModel)]="priorityFilter"><option value="All">Priority: All</option><option>High</option><option>Medium</option><option>Low</option></select>
        <select *ngIf="role !== 'client'" class="filter-select" [(ngModel)]="teamFilter"><option value="All">Team: All teams</option><option>Injury/Theft</option><option>Major Damage</option><option>Minor Damage</option></select>
        <select class="filter-select date-filter" [(ngModel)]="dateFilter"><option value="All">Date: All time</option><option>October 2026</option><option>September 2026</option></select>
        <button class="text-button" (click)="resetFilters()">Reset filters</button>
      </div>
      <div class="table-scroll"><table class="data-table queue-table" *ngIf="role !== 'client'; else customerTable">
        <thead><tr><th>Claim ID</th><th>Customer</th><th>Incident</th><th>Est. amount</th><th>Priority ↕</th><th>Routed team</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
        <tbody><tr *ngFor="let claim of filtered"><td><strong class="table-primary">{{claim.id}}</strong></td><td>{{claim.claimant}}</td><td>{{claim.incidentType}}</td><td>{{money(claim.amount)}}</td><td><span class="priority-pill" [ngClass]="priorityClass(claim.priority)">{{claim.priority}}</span></td><td>{{claim.queue}}</td><td><span class="status-pill" [ngClass]="statusClass(claim.status)">{{claim.status}}</span></td><td>{{claim.incidentDate}}</td><td><a [routerLink]="['/claims', claim.id]" class="text-link">Review →</a></td></tr><tr *ngIf="filtered.length === 0"><td colspan="9" class="empty-row">No claims match these filters.</td></tr></tbody>
      </table>
      <ng-template #customerTable><table class="data-table"><thead><tr><th>Claim ID</th><th>Date submitted</th><th>Vehicle</th><th>Status</th><th>Action</th></tr></thead><tbody><tr *ngFor="let claim of filtered"><td><strong class="table-primary">{{claim.id}}</strong></td><td>{{claim.submitted.split(' · ')[0]}}</td><td><strong>{{claim.registration}}</strong><small>{{claim.vehicle}}</small></td><td><span class="status-pill" [ngClass]="statusClass(claim.status)">{{claim.status}}</span></td><td><a [routerLink]="['/claims', claim.id]" class="text-link">View →</a></td></tr><tr *ngIf="filtered.length === 0"><td colspan="5" class="empty-row">No claims match your search.</td></tr></tbody></table></ng-template>
      </div>
      <div class="table-footer"><span>Showing {{filtered.length}} of {{role === 'client' ? '7' : '24'}} claims · Amounts in KSh</span><div class="pagination"><button disabled>Previous</button><button class="selected">1</button><button>2</button><button>3</button><button>Next</button></div></div>
    </section>
    <p class="page-footnote" *ngIf="role !== 'client'">Priority and routed team are assigned automatically. Claims officers can reassign a claim with a recorded reason.</p>
    <p class="page-footnote" *ngIf="role === 'client'">Need to add evidence? Open a claim to see requested documents and officer comments.</p>
    <div *ngIf="notice" class="toast" (click)="notice=''">{{notice}} <button aria-label="Dismiss">×</button></div>
  </div>`
})
export class ClaimsComponent {
  role: UserRole;
  search = '';
  statusFilter = 'All';
  priorityFilter = 'All';
  teamFilter = 'All';
  dateFilter = 'All';
  notice = '';
  money = money;
  constructor(private roleService: RoleService) { this.role = this.roleService.role; this.roleService.role$.subscribe(role => this.role = role); }
  get filtered(): ClaimRecord[] {
    return claims.filter(claim => {
      const searchMatch = `${claim.id} ${claim.claimant} ${claim.vehicle} ${claim.registration}`.toLowerCase().includes(this.search.toLowerCase());
      const statusMatch = this.statusFilter === 'All' || claim.status === this.statusFilter;
      const priorityMatch = this.role === 'client' || this.priorityFilter === 'All' || claim.priority === this.priorityFilter;
      const teamMatch = this.teamFilter === 'All' || claim.queue === this.teamFilter;
      const dateMatch = this.dateFilter === 'All' || (this.dateFilter === 'October 2026' && claim.incidentDate.includes('Oct 2026')) || (this.dateFilter === 'September 2026' && claim.incidentDate.includes('Sep 2026'));
      return searchMatch && statusMatch && priorityMatch && teamMatch && dateMatch;
    });
  }
  resetFilters(): void { this.search = ''; this.statusFilter = 'All'; this.priorityFilter = 'All'; this.teamFilter = 'All'; this.dateFilter = 'All'; }
  statusClass(status: ClaimStatus): string { return status === 'Approved' ? 'status-green' : status === 'Under review' || status === 'Assessment' ? 'status-blue' : status === 'More info requested' || status === 'Submitted' ? 'status-amber' : status === 'Rejected' ? 'status-red' : 'status-muted'; }
  priorityClass(priority: string): string { return priority === 'High' ? 'priority-red' : priority === 'Medium' ? 'priority-amber' : 'priority-muted'; }
}
