import { StrictMode, Suspense, lazy } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './styles.css';
import { AdminAuthProvider, RequireAdmin } from './auth';
import { PageLoading, ToastProvider } from './components/ui';
import PublicLayout from './pages/public/PublicLayout';
import Landing from './pages/public/Landing';

// Public pages used less often and the whole admin console load on demand, so the first visit downloads less code.
const VoteFlow = lazy(() => import('./pages/public/VoteFlow'));
const VerifyReceipt = lazy(() => import('./pages/public/VerifyReceipt'));
const DemoGuide = lazy(() => import('./pages/public/DemoGuide'));
const Privacy = lazy(() => import('./pages/public/Privacy'));
const Contact = lazy(() => import('./pages/public/Contact'));
const NotFound = lazy(() => import('./pages/public/NotFound'));
const AdminLogin = lazy(() => import('./pages/admin/AdminLogin'));
const AdminLayout = lazy(() => import('./pages/admin/AdminLayout'));
const ElectionsPage = lazy(() => import('./pages/admin/ElectionsPage'));
const NewElectionPage = lazy(() => import('./pages/admin/NewElectionPage'));
const ElectionPage = lazy(() => import('./pages/admin/election/ElectionPage'));
const LedgerPage = lazy(() => import('./pages/admin/LedgerPage'));
const OutboxPage = lazy(() => import('./pages/admin/OutboxPage'));
const MessagesPage = lazy(() => import('./pages/admin/MessagesPage'));
const AdminsPage = lazy(() => import('./pages/admin/AdminsPage'));
const SettingsPage = lazy(() => import('./pages/admin/SettingsPage'));

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <AdminAuthProvider>
          <Suspense fallback={<div className="narrow"><PageLoading rows={2} /></div>}>
            <Routes>
              <Route element={<PublicLayout />}>
                <Route index element={<Landing />} />
                <Route path="vote/:electionId" element={<VoteFlow />} />
                <Route path="verify" element={<VerifyReceipt />} />
                <Route path="demo" element={<DemoGuide />} />
                <Route path="privacy" element={<Privacy />} />
                <Route path="contact" element={<Contact />} />
                <Route path="*" element={<NotFound />} />
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
                <Route path="messages" element={<MessagesPage />} />
                <Route path="admins" element={<AdminsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Routes>
          </Suspense>
        </AdminAuthProvider>
      </ToastProvider>
    </BrowserRouter>
  </StrictMode>,
);
