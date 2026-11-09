import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { NavItem, UserRole } from './models';
import { roleLabels } from './mock-data';
import { RoleService } from './core/role.service';

@Component({
  selector: 'app-root', standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  template: `
  <div class="app-frame" [class.sidebar-open]="mobileOpen" [class.login-mode]="currentUrl.startsWith('/login')">
    <aside class="sidebar">
      <a routerLink="/" class="brand-lockup flex items-center gap-3" aria-label="Zurika home">
        <span class="brand-symbol">Z</span><span class="brand-name">zurika<span>.</span></span>
      </a>
      <div class="workspace-caption">{{ workspaceCaption }}</div>
      <nav class="side-nav flex flex-col" aria-label="Main navigation">
        <a *ngFor="let item of visibleNav" [routerLink]="item.path" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: item.path === '/' }" class="side-link">
          <span class="side-icon">{{ item.icon }}</span><span>{{ item.label }}</span><span *ngIf="item.label === 'Claims Queue'" class="side-count">24</span>
        </a>
      </nav>
      <div class="sidebar-bottom">
        <a routerLink="/help" class="utility-link"><span>ⓘ</span> Help &amp; support</a>
        <a routerLink="/login" class="utility-link"><span>↪</span> Sign out</a>
        <div class="sidebar-footnote">Zurika · Motor insurance</div>
      </div>
    </aside>

    <div class="main-column">
      <header class="topbar flex items-center justify-between">
        <button type="button" class="mobile-toggle" aria-label="Open navigation" (click)="mobileOpen = !mobileOpen">☰</button>
        <div class="breadcrumbs"><span>Motor insurance</span><span class="crumb-slash">/</span><strong>{{ pageName }}</strong></div>
        <div class="topbar-actions flex items-center gap-3">
          <button class="bell-button" aria-label="Notifications">♧<i></i></button>
          <span class="topbar-divider"></span>
          <div class="user-summary"><strong>{{ displayName }}</strong><span>{{ roleLabel }}</span></div>
          <span class="user-avatar">{{ roleInitials }}</span>
          <label class="sr-only" for="role-preview">Preview user role</label>
          <select id="role-preview" class="role-preview" [value]="role" (change)="changeRole($event)" aria-label="Preview user role">
            <option value="client">Customer</option><option value="claims_officer">Claims Officer</option><option value="senior_officer">Senior Officer</option><option value="admin">Administrator</option>
          </select>
        </div>
      </header>

      <main class="content-area w-full flex-1"><router-outlet /></main>
      <footer class="app-footer"><span>© 2026 Zurika</span><span>Motor insurance claims, made clearer.</span></footer>
    </div>

    <div *ngIf="mobileOpen" class="mobile-scrim" (click)="mobileOpen = false">
      <aside class="mobile-drawer" (click)="$event.stopPropagation()">
        <div class="mobile-drawer-head"><span class="brand-name">zurika<span>.</span></span><button (click)="mobileOpen = false" aria-label="Close navigation">×</button></div>
        <a *ngFor="let item of visibleNav" [routerLink]="item.path" routerLinkActive="active" class="side-link" (click)="mobileOpen = false"><span class="side-icon">{{item.icon}}</span>{{item.label}}</a>
      </aside>
    </div>
  </div>`
})
export class AppComponent {
  role: UserRole = 'claims_officer';
  mobileOpen = false;
  currentUrl = '/';

  readonly navByRole: Record<UserRole, NavItem[]> = {
    client: [
      { label: 'Dashboard', path: '/', icon: '▦', roles: ['client'] },
      { label: 'File a Claim', path: '/claims/new', icon: '⊕', roles: ['client'] },
      { label: 'My Claims', path: '/claims', icon: '▤', roles: ['client'] }
    ],
    claims_officer: [
      { label: 'Dashboard', path: '/', icon: '▦', roles: ['claims_officer'] },
      { label: 'Claims Queue', path: '/claims', icon: '▤', roles: ['claims_officer'] },
      { label: 'Routing Rules', path: '/routing', icon: '⑂', roles: ['claims_officer'] }
    ],
    senior_officer: [
      { label: 'Dashboard', path: '/', icon: '▦', roles: ['senior_officer'] },
      { label: 'Claims Queue', path: '/claims', icon: '▤', roles: ['senior_officer'] },
      { label: 'Approvals', path: '/reviews', icon: '✓', roles: ['senior_officer'] },
      { label: 'Routing Rules', path: '/routing', icon: '⑂', roles: ['senior_officer'] },
      { label: 'Payouts', path: '/payouts', icon: '↗', roles: ['senior_officer'] },
      { label: 'Audit trail', path: '/audit', icon: '◷', roles: ['senior_officer'] }
    ],
    admin: [
      { label: 'Dashboard', path: '/', icon: '▦', roles: ['admin'] },
      { label: 'Claims', path: '/claims', icon: '▤', roles: ['admin'] },
      { label: 'Approvals', path: '/reviews', icon: '✓', roles: ['admin'] },
      { label: 'Payouts', path: '/payouts', icon: '↗', roles: ['admin'] },
      { label: 'Insurers', path: '/insurers', icon: '▣', roles: ['admin'] },
      { label: 'Team & access', path: '/team', icon: '♙', roles: ['admin'] },
      { label: 'Audit trail', path: '/audit', icon: '◷', roles: ['admin'] }
    ]
  };

  constructor(private roleService: RoleService, private router: Router) {
    this.role = this.roleService.role;
    this.currentUrl = this.router.url;
    this.router.events.pipe(filter(event => event instanceof NavigationEnd)).subscribe(event => {
      this.currentUrl = (event as NavigationEnd).urlAfterRedirects;
      this.mobileOpen = false;
    });
  }

  get visibleNav(): NavItem[] { return this.navByRole[this.role]; }
  get roleLabel(): string { return roleLabels[this.role]; }
  get workspaceCaption(): string {
    return this.role === 'client' ? 'CUSTOMER PORTAL' : this.role === 'admin' ? 'ADMINISTRATION' : this.role === 'senior_officer' ? 'SENIOR OFFICER WORKSPACE' : 'CLAIMS OFFICER WORKSPACE';
  }
  get displayName(): string {
    return this.role === 'client' ? 'Amina Patel' : this.role === 'admin' ? 'Belam Muia' : this.role === 'senior_officer' ? 'Sarah Adams' : 'Daniel Brooks';
  }
  get roleInitials(): string { return this.displayName.split(' ').map(part => part[0]).join(''); }
  get pageName(): string {
    const path = this.currentUrl.split('?')[0];
    if (path === '/') return 'Dashboard';
    if (path.includes('/claims/new')) return 'File a Claim';
    if (path.includes('/claims/')) return 'Claim review';
    if (path === '/claims') return this.role === 'client' ? 'My Claims' : 'Claims Queue';
    if (path === '/routing') return 'Routing Rules';
    if (path === '/reviews') return 'Approvals';
    return path.replace('/', '').replace('-', ' ').replace(/^./, c => c.toUpperCase());
  }
  changeRole(event: Event): void {
    this.role = (event.target as HTMLSelectElement).value as UserRole;
    this.roleService.setRole(this.role);
    if (this.role === 'client' && (this.currentUrl === '/routing' || this.currentUrl === '/reviews')) this.router.navigateByUrl('/');
  }
}
