import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { adminApi, adminToken, UNAUTHORIZED_EVENT } from './api';
import { PageLoading } from './components/ui';

interface AdminAuth {
  username: string | null;
  checking: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AdminAuth | null>(null);

export function AdminAuthProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState<string | null>(null);
  const [checking, setChecking] = useState(() => adminToken.get() !== null);

  useEffect(() => {
    if (!adminToken.get()) return;
    adminApi.me()
      .then((me) => setUsername(me.username))
      .catch(() => adminToken.clear())
      .finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    const onExpired = () => { adminToken.clear(); setUsername(null); };
    window.addEventListener(UNAUTHORIZED_EVENT, onExpired);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onExpired);
  }, []);

  const login = useCallback(async (user: string, password: string) => {
    const res = await adminApi.login(user, password);
    adminToken.set(res.token);
    setUsername(res.username);
  }, []);

  const logout = useCallback(async () => {
    await adminApi.logout();
    adminToken.clear();
    setUsername(null);
  }, []);

  return <AuthContext.Provider value={{ username, checking, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAdminAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAdminAuth must be used inside AdminAuthProvider');
  return ctx;
}

export function RequireAdmin({ children }: { children: ReactNode }) {
  const { username, checking } = useAdminAuth();
  const location = useLocation();
  if (checking) return <PageLoading />;
  if (!username) return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}
