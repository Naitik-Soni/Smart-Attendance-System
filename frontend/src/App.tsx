import { Navigate, Route, Routes } from 'react-router-dom';

import { AppShell } from './components/AppShell';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Toasts } from './components/Toasts';
import { useAuthStore } from './store/auth';
import { AdminPage } from './pages/AdminPage';
import { AdminPoliciesPage } from './pages/AdminPoliciesPage';
import { AdminCamerasPage } from './pages/AdminCamerasPage';
import { AdminOperatorsPage } from './pages/AdminOperatorsPage';
import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { OperatorEnrollmentPage } from './pages/OperatorEnrollmentPage';
import { OperatorScanPage } from './pages/OperatorScanPage';
import { OperatorUsersPage } from './pages/OperatorUsersPage';
import { SetupAdminPage } from './pages/SetupAdminPage';
import { UserPage } from './pages/UserPage';

function App() {
  return (
    <>
      <Routes>
        <Route path='/login' element={<LoginPage />} />
        <Route path='/setup-admin' element={<SetupAdminPage />} />
        <Route
          path='/'
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route index element={<RoleHomeRedirect />} />
          <Route path='admin' element={<ProtectedRoute role='admin'><Navigate to='/admin/overview' replace /></ProtectedRoute>} />
          <Route path='admin/overview' element={<ProtectedRoute role='admin'><AdminPage /></ProtectedRoute>} />
          <Route path='admin/operators' element={<ProtectedRoute role='admin'><AdminOperatorsPage /></ProtectedRoute>} />
          <Route path='admin/policies' element={<ProtectedRoute role='admin'><AdminPoliciesPage /></ProtectedRoute>} />
          <Route path='admin/cameras' element={<ProtectedRoute role='admin'><AdminCamerasPage /></ProtectedRoute>} />
          <Route path='operations/users' element={<ProtectedRoute role='operator'><OperatorUsersPage /></ProtectedRoute>} />
          <Route path='operations/enrollment' element={<ProtectedRoute role='operator'><OperatorEnrollmentPage /></ProtectedRoute>} />
          <Route path='operations/scan' element={<ProtectedRoute role='operator'><OperatorScanPage /></ProtectedRoute>} />
          <Route path='me' element={<ProtectedRoute role='user'><UserPage /></ProtectedRoute>} />
        </Route>
        <Route path='*' element={<NotFoundPage />} />
      </Routes>
      <Toasts />
    </>
  );
}

function RoleHomeRedirect() {
  const role = useAuthStore((state) => state.user?.role ?? 'user');

  if (role === 'admin') {
    return <Navigate to='/admin/overview' replace />;
  }

  if (role === 'operator') {
    return <Navigate to='/operations/users' replace />;
  }

  return <Navigate to='/me' replace />;
}

export default App;
