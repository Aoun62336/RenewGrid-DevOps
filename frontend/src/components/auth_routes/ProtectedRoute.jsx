import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { isTokenValid } from '../../utils/auth';

const ROLE_HOME = {
  user:      '/user-dashboard',
  collector: '/collector-dashboard',
  recycler:  '/dashboard',
  admin:     '/admin-dashboard',
};

/**
 * ProtectedRoute — Wraps routes that require authentication.
 *
 * 1. Finds a role with both a valid (non-expired) token AND stored user data.
 * 2. If the token is expired, clears it so the user gets redirected to login.
 * 3. If a valid session exists but the role doesn't match allowedRoles,
 *    redirects to that user's own dashboard.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const rolesToCheck = allowedRoles?.length > 0
    ? allowedRoles
    : ['admin', 'recycler', 'collector', 'user'];

  let activeRole = null;
  let userStr = null;
  let token = null;

  // First pass: check specifically requested roles
  for (const r of rolesToCheck) {
    const t = localStorage.getItem(`${r}_access_token`);
    const u = localStorage.getItem(r);
    if (t && u) {
      if (!isTokenValid(t)) {
        // Expired — clean up
        localStorage.removeItem(`${r}_access_token`);
        localStorage.removeItem(`${r}_refresh_token`);
        localStorage.removeItem(r);
        continue;
      }
      token = t;
      userStr = u;
      activeRole = r;
      break;
    }
  }

  // Second pass: if no matching role found, check ALL roles
  // (e.g., a recycler hitting /admin-dashboard — redirect to their home)
  if (!activeRole) {
    for (const r of ['admin', 'recycler', 'collector', 'user']) {
      const t = localStorage.getItem(`${r}_access_token`);
      const u = localStorage.getItem(r);
      if (t && u) {
        if (!isTokenValid(t)) {
          localStorage.removeItem(`${r}_access_token`);
          localStorage.removeItem(`${r}_refresh_token`);
          localStorage.removeItem(r);
          continue;
        }
        token = t;
        userStr = u;
        activeRole = r;
        break;
      }
    }
  }

  // No valid session found → send to login
  if (!token || !userStr || !activeRole) {
    return <Navigate to="/login" replace />;
  }

  let user;
  try {
    user = JSON.parse(userStr);
  } catch {
    // Corrupted data
    localStorage.removeItem(`${activeRole}_access_token`);
    localStorage.removeItem(`${activeRole}_refresh_token`);
    localStorage.removeItem(activeRole);
    return <Navigate to="/login" replace />;
  }

  const role = user.role?.toLowerCase();

  // Wrong role for this route → redirect to their own dashboard
  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to={ROLE_HOME[role] ?? '/'} replace />;
  }

  return children ? children : <Outlet />;
}
