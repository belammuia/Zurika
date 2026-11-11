import { createContext, useContext, useMemo, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { claimsSeed } from './data/mock-data';
import type { ClaimRecord, UserRole } from './types';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Claims from './pages/Claims';
import ClaimDetail from './pages/ClaimDetail';
import SubmitClaim from './pages/SubmitClaim';
import Workspace from './pages/Workspace';

interface WorkspaceContextValue {
  role: UserRole;
  setRole: Dispatch<SetStateAction<UserRole>>;
  claims: ClaimRecord[];
  setClaims: Dispatch<SetStateAction<ClaimRecord[]>>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function useWorkspace(): WorkspaceContextValue {
  const context = useContext(WorkspaceContext);
  if (!context) throw new Error('useWorkspace must be used inside the workspace provider.');
  return context;
}

function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<UserRole>(() => {
    const saved = window.localStorage.getItem('zurika-role');
    return saved === 'client' || saved === 'claims_officer' || saved === 'senior_officer' || saved === 'admin' ? saved : 'claims_officer';
  });
  const [claims, setClaims] = useState<ClaimRecord[]>(claimsSeed);
  const value = useMemo(() => ({ role, setRole, claims, setClaims }), [role, claims]);
  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="claims" element={<Claims />} />
        <Route path="claims/new" element={<SubmitClaim />} />
        <Route path="claims/:id" element={<ClaimDetail />} />
        <Route path="routing" element={<Workspace section="Routing Rules" />} />
        <Route path="reviews" element={<Workspace section="Approvals" />} />
        <Route path="payouts" element={<Workspace section="Payouts" />} />
        <Route path="documents" element={<Workspace section="Documents" />} />
        <Route path="team" element={<Workspace section="Team & access" />} />
        <Route path="insurers" element={<Workspace section="Insurers" />} />
        <Route path="audit" element={<Workspace section="Audit trail" />} />
        <Route path="settings" element={<Workspace section="Settings" />} />
        <Route path="help" element={<Workspace section="Help & support" />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return <WorkspaceProvider><AppRoutes /></WorkspaceProvider>;
}
