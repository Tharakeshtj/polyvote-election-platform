import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import './styles.css';
import { AdminAuthProvider, RequireAdmin } from './auth';
import { ToastProvider } from './components/ui';
import PublicLayout from './pages/public/PublicLayout';
import Landing from './pages/public/Landing';
import VoteFlow from './pages/public/VoteFlow';
import VerifyReceipt from './pages/public/VerifyReceipt';
import DemoGuide from './pages/public/DemoGuide';
import AdminLogin from './pages/admin/AdminLogin';
import AdminLayout from './pages/admin/AdminLayout';
import ElectionsPage from './pages/admin/ElectionsPage';
import NewElectionPage from './pages/admin/NewElectionPage';
import ElectionPage from './pages/admin/election/ElectionPage';
import LedgerPage from './pages/admin/LedgerPage';
import OutboxPage from './pages/admin/OutboxPage';
import AdminsPage from './pages/admin/AdminsPage';
import SettingsPage from './pages/admin/SettingsPage';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <AdminAuthProvider>
          <Routes>
            <Route element={<PublicLayout />}>
              <Route index element={<Landing />} />
              <Route path="vote" element={<Navigate to="/" replace />} />
              <Route path="vote/:electionId" element={<VoteFlow />} />
              <Route path="verify" element={<VerifyReceipt />} />
              <Route path="demo" element={<DemoGuide />} />
            </Route>
            <Route path="admin/login" element={<AdminLogin />} />
            <Route
              path="admin"
              element={
                <RequireAdmin>
                  <AdminLayout />
                </RequireAdmin>
              }
            >
              <Route index element={<ElectionsPage />} />
              <Route path="elections/new" element={<NewElectionPage />} />
              <Route path="elections/:id/:tab?" element={<ElectionPage />} />
              <Route path="ledger" element={<LedgerPage />} />
              <Route path="outbox" element={<OutboxPage />} />
              <Route path="admins" element={<AdminsPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AdminAuthProvider>
      </ToastProvider>
    </BrowserRouter>
  </StrictMode>,
);
