import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { UserRole } from '../models';

@Injectable({ providedIn: 'root' })
export class RoleService {
  private readonly currentRole = new BehaviorSubject<UserRole>('claims_officer');
  readonly role$ = this.currentRole.asObservable();
  get role(): UserRole { return this.currentRole.value; }
  setRole(role: UserRole): void { this.currentRole.next(role); }
}
