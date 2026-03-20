import type { ReactNode } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useAuthStore } from '../store/auth';

type ProtectedRouteProps = {
  children?: ReactNode;
  role?: 'admin' | 'operator' | 'user' | 'any';
};

export function ProtectedRoute({ children, role = 'any' }: ProtectedRouteProps) {
  const token = useAuthStore((state) => state.accessToken);
  const currentRole = useAuthStore((state) => state.user?.role ?? 'user');
  const location = useLocation();

  if (!token) {
    return <Navigate to='/login' state={{ from: location }} replace />;
  }

  if (role !== 'any') {
    const allowed =
      role === 'operator'
        ? currentRole === 'operator' || currentRole === 'admin'
        : currentRole === role;

    if (!allowed) {
      return <Navigate to='/' replace />;
    }
  }

  return children ? <>{children}</> : <Outlet />;
}


