import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { claims, money } from '../mock-data';
import { ClaimRecord, ClaimStatus, UserRole } from '../models';
import { RoleService } from '../core/role.service';

@Component({
  selector: 'app-claim-detail', standalone: true, imports: [CommonModule, RouterLink, FormsModule],
  template: `
  <div class="page-wrap">
    <a routerLink="/claims" class="back-link">← &nbsp; {{ role === 'client' ? 'My Claims' : 'Claims Queue' }}</a>
    <div class="claim-title-row"><div><h1 class="page-title">{{claim.id}}</h1><p class="page-subtitle">{{claim.incidentType}} · {{claim.vehicle}} · Submitted {{claim.submitted}}</p></div><span class="status-pill" [ngClass]="statusClass(claim.status)">{{claim.status}}</span></div>

    <ng-container *ngIf="role === 'client'; else officerReview">
      <div class="notice notice-warning" *ngIf="claim.status === 'More info requested'"><span class="notice-icon">!</span><div><strong>More information requested</strong><p>Please upload the passenger's medical note by 12 Oct 2026. Your claim will continue once it is received.</p></div><button class="btn-primary small" (click)="uploadNotice()">⇧ &nbsp; Upload Additional Document</button></div>
      <div class="detail-layout">
        <div class="detail-main">
          <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Claim summary</h2></div></div><div class="detail-grid"><div><span class="detail-label">Policy number</span><strong>{{claim.policyNumber}}</strong></div><div><span class="detail-label">Vehicle plate</span><strong>{{claim.registration}}</strong></div><div><span class="detail-label">Incident date &amp; time</span><strong>{{claim.incidentDate}} · {{claim.incidentTime}}</strong></div><div><span class="detail-label">Estimated damage (KSh)</span><strong>{{money(claim.amount)}}</strong></div><div><span class="detail-label">Location</span><strong>{{claim.location}}</strong></div><div><span class="detail-label">Police report</span><strong>{{claim.policeReport}}</strong></div><div><span class="detail-label">Injury involved</span><strong>{{claim.injury ? 'Yes, passenger wrist injury' : 'No'}}</strong></div></div><div class="detail-description"><span class="detail-label">Incident description</span><p>{{claim.description}}</p></div></section>
          <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Uploaded files</h2><p class="panel-subtitle">3 photos and 2 documents · Submitted 7 Oct 2026</p></div><button class="btn-outline small" (click)="uploadNotice()">⇧ Upload</button></div><div class="photo-grid"><figure *ngFor="let photo of claim.photos"><img [src]="'assets/' + photo" [alt]="photo"><figcaption>{{photo}}</figcaption></figure></div><div class="document-row"><span class="file-icon">PDF</span><div><strong>police-report.pdf</strong><span>PDF · 1.4 MB · 7 Oct 2026</span></div><button class="download-button">↓</button></div><div class="document-row"><span class="file-icon">PDF</span><div><strong>repair-estimate.pdf</strong><span>PDF · 840 KB · 7 Oct 2026</span></div><button class="download-button">↓</button></div></section>
          <section class="panel"><h2 class="panel-title">Officer comments</h2><div class="comment-card"><div class="comment-meta"><strong>{{claim.officer}} · Claims Officer</strong><span>8 Oct 2026 · 10:30</span></div><p>{{claim.comments}}</p></div></section>
        </div>
        <aside class="detail-aside"><section class="panel"><h2 class="panel-title">Claim progress</h2><p class="panel-subtitle">Last updated 8 Oct 2026</p><div class="timeline claim-timeline"><div class="timeline-item done"><i>✓</i><div><strong>Submitted</strong><span>7 Oct 2026 · 09:12</span><p>Received and routed to {{claim.queue}}.</p></div></div><div class="timeline-item done"><i>✓</i><div><strong>Under Review</strong><span>8 Oct 2026 · 10:30</span><p>{{claim.officer}} requested a medical note.</p><span class="status-pill status-amber">More info requested</span></div></div><div class="timeline-item"><i>3</i><div><strong>Assessment</strong><span>Awaiting requested document</span><p>Damage and injury evidence will be assessed.</p></div></div><div class="timeline-item"><i>4</i><div><strong>Decision</strong><span>Not started</span><p>You'll be notified of the outcome.</p></div></div></div></section><section class="panel"><h2 class="panel-title">Your claims officer</h2><div class="officer-card"><span class="officer-avatar">DB</span><div><strong>{{claim.officer}}</strong><span>{{claim.officerTeam}}</span></div></div><p class="panel-subtitle">For urgent assistance, call 0800 123 456 and quote your claim ID.</p></section></aside>
      </div>
    </ng-container>

    <ng-template #officerReview>
      <div class="staff-review-layout">
        <div class="detail-main">
          <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Claim details</h2><p class="panel-subtitle">Customer and insured vehicle</p></div></div><div class="detail-grid"><div><span class="detail-label">Customer</span><strong>{{claim.claimant}}</strong></div><div><span class="detail-label">Email</span><strong>{{claim.email}}</strong></div><div><span class="detail-label">Policy number</span><strong>{{claim.policyNumber}}</strong></div><div><span class="detail-label">Insured vehicle</span><strong>{{claim.vehicle}}</strong></div><div><span class="detail-label">Vehicle plate</span><strong>{{claim.registration}}</strong></div><div><span class="detail-label">Estimated damage (KSh)</span><strong>{{money(claim.amount)}}</strong></div><div><span class="detail-label">Incident date &amp; time</span><strong>{{claim.incidentDate}} · {{claim.incidentTime}}</strong></div><div><span class="detail-label">Incident type</span><strong>{{claim.incidentType}}</strong></div><div><span class="detail-label">Location</span><strong>{{claim.location}}</strong></div><div><span class="detail-label">Injury involved</span><strong>{{claim.injury ? 'Yes' : 'No'}}</strong></div><div><span class="detail-label">Police report</span><strong>{{claim.policeReport}}</strong></div><div><span class="detail-label">Third party involved</span><strong>{{claim.thirdParty ? 'Yes' : 'No'}}</strong></div></div></section>
          <section class="panel"><h2 class="panel-title">Incident description</h2><p class="long-description">{{claim.description}}</p></section>
          <section class="panel"><div class="panel-heading"><div><h2 class="panel-title">Photos &amp; documents</h2><p class="panel-subtitle">Evidence uploaded by {{claim.claimant}} · 7 Oct 2026</p></div></div><div class="photo-grid"><figure *ngFor="let photo of claim.photos"><img [src]="'assets/' + photo" [alt]="photo"><figcaption>{{photo}}</figcaption></figure></div><div class="document-row"><span class="file-icon">PDF</span><div><strong>police-report.pdf</strong><span>PDF · 1.4 MB · 7 Oct 2026</span></div><button class="download-button">↓</button></div><div class="document-row"><span class="file-icon">PDF</span><div><strong>repair-estimate.pdf</strong><span>PDF · 840 KB · 7 Oct 2026</span></div><button class="download-button">↓</button></div></section>
        </div>
        <aside class="review-aside">
          <section class="panel triage-panel"><div class="panel-heading"><h2 class="panel-title">Automated Triage Result</h2><span class="metric-icon">⑂</span></div><div class="triage-line"><span>Auto-assigned priority</span><span class="priority-pill priority-red">{{claim.priority}}</span></div><div class="triage-line"><span>Auto-routed team</span><strong>{{claim.queue}}</strong></div><div class="reason-box"><strong>WHY THIS CLAIM WAS ROUTED</strong><p>{{claim.injury ? 'Injury reported + amount above threshold. Injury takes precedence over amount-based rules.' : 'Claim was matched to the configured damage and amount routing rules.'}} {{money(claim.amount)}} is {{claim.amount >= 50000 ? 'above' : 'below'}} the KSh 50,000 major damage threshold.</p></div><p class="matched-rule">Matched rule: Injury = {{claim.injury ? 'Yes' : 'No'}} · 7 Oct 2026, 09:12</p></section>
          <section class="panel action-panel"><h2 class="panel-title">Take action</h2><p class="panel-subtitle">Assigned to {{claim.officer}}</p><label class="field action-comment"><span>Officer comment <b>*</b></span><textarea rows="4" [(ngModel)]="comment" placeholder="Add a comment explaining your decision or the information required."></textarea></label><p class="field-hint">Comments are visible to the customer. A reason is required for rejection or reassignment.</p><div class="action-pair"><button class="btn-primary" (click)="act('Approved')">✓ &nbsp; Approve</button><button class="btn-danger" (click)="act('Rejected')">× &nbsp; Reject</button></div><button class="btn-outline full-btn" (click)="act('More info requested')">▤ &nbsp; Request More Info</button><button class="btn-outline full-btn" (click)="reassign()">♙ &nbsp; Reassign</button><p class="action-footnote">Every action is recorded in the claim history.</p></section>
          <section class="panel"><h2 class="panel-title">Latest activity</h2><div class="activity-entry"><span>8 Oct 2026 · 10:30 · {{claim.officer}}</span><strong>{{claim.status}}</strong><p>{{claim.comments}}</p></div></section>
        </aside>
      </div>
    </ng-template>
    <div *ngIf="toast" class="toast" (click)="toast = ''">{{toast}} <button aria-label="Dismiss">×</button></div>
  </div>`
})
export class ClaimDetailComponent {
  claim: ClaimRecord = claims[0];
  role: UserRole;
  comment = '';
  toast = '';
  money = money;
  constructor(route: ActivatedRoute, private roleService: RoleService) {
    const id = route.snapshot.paramMap.get('id');
    this.claim = claims.find(record => record.id === id) ?? claims[0];
    this.role = roleService.role;
    this.roleService.role$.subscribe(role => this.role = role);
  }
  statusClass(status: ClaimStatus): string { return status === 'Approved' ? 'status-green' : status === 'Under review' || status === 'Assessment' ? 'status-blue' : status === 'More info requested' || status === 'Submitted' ? 'status-amber' : status === 'Rejected' ? 'status-red' : 'status-muted'; }
  uploadNotice(): void { this.toast = 'Document upload is a local prototype interaction. No file was sent to a server.'; }
  act(status: ClaimStatus): void {
    if (!this.comment.trim()) { this.toast = 'Add an officer comment before recording this decision.'; return; }
    this.claim.status = status;
    this.claim.comments = this.comment.trim();
    this.toast = `Claim ${this.claim.id} marked as ${status.toLowerCase()} in this prototype.`;
  }
  reassign(): void {
    if (!this.comment.trim()) { this.toast = 'Add a reason before reassigning this claim.'; return; }
    this.claim.officer = 'Sarah Adams';
    this.claim.comments = this.comment.trim();
    this.toast = 'Claim reassigned to Sarah Adams in this prototype.';
  }
}
