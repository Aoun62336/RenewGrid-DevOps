import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import {
  restoreSession,
  getToken,
  getUser,
} from '../../services/api';

const ROLE_HOME = {
  user: '/user-dashboard',
  collector: '/collector-dashboard',
  recycler: '/dashboard',
  admin: '/admin-dashboard',
};

/**
 * ProtectedRoute — Wraps routes that require authentication.
 *
 * 1. Attempts to restore the session via the HttpOnly refresh cookie
 *    (silently calls /auth/refresh-token on page load).
 * 2. If restoration fails, redirects to /login.
 * 3. If the user's role doesn't match allowedRoles,
 *    redirects to that user's own dashboard.
 *
 * Unlike the previous component, this does NOT infer a valid session
 * from cached browser data — the backend verifies it.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const [state, setState] = useState({
    loading: true,
    user: null,
  });

  useEffect(() => {
    let active = true;

    restoreSession()
      .then((user) => {
        if (active) {
          setState({ loading: false, user });
        }
      })
      .catch(() => {
        if (active) {
          setState({ loading: false, user: null });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  if (state.loading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        role="status"
      >
        <p>Verifying your session…</p>
      </div>
    );
  }

  const user = state.user || getUser();

  if (!user || !getToken()) {
    return <Navigate to="/login" replace />;
  }

  const role = user.role?.toLowerCase();

  if (allowedRoles?.length && !allowedRoles.includes(role)) {
    return <Navigate to={ROLE_HOME[role] || '/'} replace />;
  }

  return children || <Outlet />;
}
