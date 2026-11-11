import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../App';
import type { UserRole } from '../types';

export default function Login() {
  const [email, setEmail] = useState('daniel.brooks@zurika.co.ke');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState<UserRole>('claims_officer');
  const [notice, setNotice] = useState('');
  const navigate = useNavigate();
  const { setRole: setWorkspaceRole } = useWorkspace();

  function signIn(event: FormEvent) {
    event.preventDefault();
    if (!email.trim() || !password.trim()) { setNotice('Enter your email address and password to continue.'); return; }
    setWorkspaceRole(role);
    window.localStorage.setItem('zurika-role', role);
    navigate('/');
  }

  return <main className="login-screen">
    <form className="login-card" onSubmit={signIn}>
      <div className="login-brand"><span className="brand-symbol">Z</span><span className="brand-name">zurika<span>.</span></span></div>
      <div className="eyebrow">MOTOR INSURANCE CLAIMS</div>
      <h1>Welcome back</h1>
      <p className="login-lead">Sign in to your Zurika workspace.</p>
      <div className="login-label">Continue as</div>
      <div className="login-tabs">
        <button type="button" className={role === 'client' ? 'selected' : ''} onClick={() => setRole('client')}>Customer</button>
        <button type="button" className={role !== 'client' ? 'selected' : ''} onClick={() => setRole('claims_officer')}>Staff</button>
      </div>
      <span className="login-hint">{role === 'client' ? 'Access your policy, claims and documents.' : 'Access claims operations and assessment tools.'}</span>
      {role !== 'client' && <label className="field login-field"><span>Preview staff role</span><select value={role} onChange={event => setRole(event.target.value as UserRole)}><option value="claims_officer">Claims Officer</option><option value="senior_officer">Senior Claims Officer</option><option value="admin">Administrator</option></select></label>}
      <label className="field login-field"><span>Email address</span><input type="email" value={email} onChange={event => setEmail(event.target.value)} placeholder="you@example.com" autoComplete="username" /></label>
      <label className="field login-field"><span>Password</span><div className="password-field"><input type={showPassword ? 'text' : 'password'} value={password} onChange={event => setPassword(event.target.value)} autoComplete="current-password" /><button type="button" onClick={() => setShowPassword(value => !value)}>{showPassword ? 'Hide' : 'Show'}</button></div></label>
      <button type="button" className="forgot-link" onClick={() => setNotice('Password reset is not connected in this frontend prototype.')}>Forgot password?</button>
      {notice && <div className="login-notice" role="status">{notice}</div>}
      <button className="btn-primary login-submit" type="submit">Sign in</button>
      <div className="login-security">Protected access · Zurika Motor Insurance</div>
    </form>
  </main>;
}
