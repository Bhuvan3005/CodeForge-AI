import { Navigate } from 'react-router-dom';
import { authStore } from '../lib/auth';
import type { ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * Wraps a route so unauthenticated users are redirected to /login.
 */
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!authStore.isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
