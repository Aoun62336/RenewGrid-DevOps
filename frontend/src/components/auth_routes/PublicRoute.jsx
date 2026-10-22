import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

import { restoreSession } from '../../services/api';

const ROLE_HOME = {
  user: '/user-dashboard',
  collector: '/collector-dashboard',
  recycler: '/dashboard',
  admin: '/admin-dashboard',
};

/**
 * PublicRoute — Wraps pages that should only be accessible when NOT logged in
 * (Login, Register, ForgotPassword, etc.).
 *
 * Silently attempts session restoration via the HttpOnly cookie.
 * If a valid session exists, redirects to the user's dashboard.
 */
export default function PublicRoute({ children }) {
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
    return null;
  }

  const role = state.user?.role?.toLowerCase();

  if (role) {
    return (
      <Navigate
        to={ROLE_HOME[role] || '/user-dashboard'}
        replace
      />
    );
  }

  return children;
}
