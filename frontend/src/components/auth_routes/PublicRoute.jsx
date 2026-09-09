import React from 'react';
import { Navigate } from 'react-router-dom';

import { isTokenValid } from '../../utils/auth';

const ROLE_HOME = {
  user:      '/user-dashboard',
  collector: '/collector-dashboard',
  recycler:  '/dashboard',
  admin:     '/admin-dashboard',
};

/**
 * PublicRoute — Wraps pages that should only be accessible when NOT logged in
 * (Login, Register, ForgotPassword, etc.).
 *
 * If the user has a valid (non-expired) token, redirect them to their dashboard.
 * If the token exists but is expired, clear it and let the user through.
 */
export default function PublicRoute({ children }) {
  const roles = ['admin', 'recycler', 'collector', 'user'];

  for (const role of roles) {
    const token = localStorage.getItem(`${role}_access_token`);
    const userStr = localStorage.getItem(role);

    if (token && userStr) {
      // Check if token is actually still valid
      if (!isTokenValid(token)) {
        // Token expired — clean up and let user log in again
        localStorage.removeItem(`${role}_access_token`);
        localStorage.removeItem(`${role}_refresh_token`);
        localStorage.removeItem(role);
        continue;
      }

      try {
        const user = JSON.parse(userStr);
        const r = user.role?.toLowerCase();
        return <Navigate to={ROLE_HOME[r] ?? '/user-dashboard'} replace />;
      } catch {
        // Corrupted data — clear it
        localStorage.removeItem(`${role}_access_token`);
        localStorage.removeItem(`${role}_refresh_token`);
        localStorage.removeItem(role);
      }
    }
  }

  return children;
}
