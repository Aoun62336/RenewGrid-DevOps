/**
 * api.js — Centralised API client for RenewGrid frontend.
 *
 * Usage:
 *   import api from '../services/api';
 *   const data = await api.login({ email, password });
 */

const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();

export const BASE_URL = configuredApiUrl
  ? configuredApiUrl.replace(/\/+$/, '')
  : '';

// ─── Authentication session state ──────────────────────────────────────────

// Access credentials exist only in memory, never browser storage.
let accessToken = null;
let sessionUser = null;
let refreshPromise = null;

const ROLES = ['admin', 'recycler', 'collector', 'user'];

function storeSession(data) {
  accessToken = data.access_token;
  sessionUser = data.user;

  const role = data.user.role.toLowerCase();

  // Remove any credentials left by earlier RenewGrid versions.
  for (const item of ROLES) {
    localStorage.removeItem(`${item}_access_token`);
    localStorage.removeItem(`${item}_refresh_token`);
  }

  // Only non-secret profile information is cached for UI compatibility.
  localStorage.setItem(role, JSON.stringify(data.user));

  return data.user;
}

export const getActiveRole = () => {
  return sessionUser?.role?.toLowerCase() || 'user';
};

export const getToken = () => accessToken;

export const getUser = (role = getActiveRole()) => {
  if (
    sessionUser &&
    sessionUser.role?.toLowerCase() === role
  ) {
    return sessionUser;
  }
  // Fallback: cached profile info (not a credential).
  return JSON.parse(localStorage.getItem(role) || 'null');
};

export const clearAuth = () => {
  accessToken = null;
  sessionUser = null;

  for (const role of ROLES) {
    localStorage.removeItem(`${role}_access_token`);
    localStorage.removeItem(`${role}_refresh_token`);
    localStorage.removeItem(role);
  }
};

export const clearAllAuth = clearAuth;

const forceLogout = () => {
  clearAllAuth();
  window.location.replace('/login');
};

async function attemptTokenRefresh() {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const response = await fetch(
      `${BASE_URL}/auth/refresh-token`,
      {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      }
    );

    if (!response.ok) {
      throw new Error('Session expired or revoked.');
    }

    const data = await response.json();
    storeSession(data);
    return data;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

export async function restoreSession() {
  if (accessToken && sessionUser) {
    return sessionUser;
  }

  const data = await attemptTokenRefresh();
  return data.user;
}

import toast from 'react-hot-toast';

async function executeRequest(
  method,
  path,
  body = null,
  multipart = false,
  isRetry = false,
) {
  const headers = {
    'X-Requested-With': 'XMLHttpRequest',
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (!multipart) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    credentials: 'same-origin',
    body: body
      ? (multipart ? body : JSON.stringify(body))
      : null,
  });

  if (
    response.status === 401 &&
    !isRetry &&
    !path.startsWith('/auth/login') &&
    !path.startsWith('/auth/refresh-token')
  ) {
    try {
      await attemptTokenRefresh();
      return executeRequest(method, path, body, multipart, true);
    } catch {
      forceLogout();
      throw new Error('Session expired. Please log in again.');
    }
  }

  let data;
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const message = typeof data.detail === 'string'
      ? data.detail
      : JSON.stringify(data.detail ?? data);
    throw new Error(message || 'API request failed.');
  }

  return data;
}

async function request(method, path, body = null, multipart = false) {
  const isQuery = method === 'GET';
  
  const promise = executeRequest(method, path, body, multipart);

  if (isQuery) {
    // Only show error toasts for GET requests to avoid spamming success/loading toasts
    promise.catch((err) => {
      // Don't double-toast session expiry — it's already handled in executeRequest
      if (!err.message?.includes('Session expired')) {
        toast.error(`Failed: ${err.message}`);
      }
    });
  } else {
    // Determine dynamic success message based on path
    let successMsg = 'Done!';
    if (path.includes('/auth/login')) successMsg = 'Login successful!';
    else if (path.includes('/auth/register')) successMsg = 'Registration successful!';
    else if (path.includes('/auth/logout')) successMsg = 'Logged out successfully.';
    else if (path.includes('/auth/update-profile')) successMsg = 'Profile updated successfully.';
    else if (path.includes('/auth/change-password')) successMsg = 'Password changed successfully.';
    else if (path.includes('/auth/forgot-password')) successMsg = 'Reset link sent.';
    else if (path.includes('/auth/reset-password')) successMsg = 'Password reset successfully.';
    else if (path.includes('/collector/accept')) successMsg = 'Pickup accepted!';
    else if (path.includes('/collector/reject')) successMsg = 'Pickup rejected.';
    else if (path.includes('/collector/collect')) successMsg = 'Marked as collected.';
    else if (path.includes('/collector/handover')) successMsg = 'Handed over successfully.';
    else if (path.includes('/recycler/process')) successMsg = 'Processing started.';
    else if (path.includes('/recycler/update-status')) successMsg = 'Status updated.';

    // Use a toast promise for mutating API calls (POST, PUT, DELETE, PATCH)
    toast.promise(promise, {
      loading: `Processing…`,
      success: successMsg,
      error: (err) => err.message?.includes('Session expired') ? 'Session expired — logging out.' : `Failed: ${err.message}`,
    });
  }

  return promise;
}

// ─── Convenience methods ────────────────────────────────────────────────────
const get  = (path)        => request('GET',  path);
const post = (path, body, multipart = false) => request('POST', path, body, multipart);
const put  = (path, body)  => request('PUT',  path, body);
const patch = (path, body) => request('PATCH', path, body);
const del  = (path)        => request('DELETE', path);

// ═══════════════════════════════════════════════════════════════════════════
//  AUTH MODULE   /auth/*
// ═══════════════════════════════════════════════════════════════════════════
export const authAPI = {
  /** POST /auth/register */
  register: (body) => post('/auth/register', body),

  /** POST /auth/login — stores session in memory + HttpOnly cookie */
  login: async ({ email, password }) => {
    const data = await post('/auth/login', { email, password });
    storeSession(data);
    return data;
  },

  /** GET /auth/me */
  me: () => get('/auth/me'),

  /** PUT /auth/update-profile */
  updateProfile: (body) => put('/auth/update-profile', body),

  /** POST /auth/change-password — revokes sessions server-side, forces re-login */
  changePassword: async (body) => {
    const result = await post('/auth/change-password', body);
    clearAllAuth();
    window.location.replace('/login');
    return result;
  },

  /** POST /auth/forgot-password */
  forgotPassword: (body) => post('/auth/forgot-password', body),

  /** POST /auth/reset-password */
  resetPassword: (body) => post('/auth/reset-password', body),

  /** POST /auth/refresh-token — uses HttpOnly cookie, rotates credential */
  refreshToken: async () => {
    return attemptTokenRefresh();
  },

  /** POST /auth/logout — revokes session server-side */
  logout: async () => {
    await post('/auth/logout');
    clearAllAuth();
  },

  /** DELETE /auth/delete-account */
  deleteAccount: async () => {
    const result = await del('/auth/delete-account');
    clearAllAuth();
    window.location.replace('/login');
    return result;
  },

  /** POST /auth/upload-profile-image  (multipart) */
  uploadProfileImage: (file) => {
    const fd = new FormData();
    fd.append('file', file);
    return post('/auth/upload-profile-image', fd, true);
  },
};

// ═══════════════════════════════════════════════════════════════════════════
//  WASTE MODULE   /waste/*
// ═══════════════════════════════════════════════════════════════════════════
export const wasteAPI = {
  /**
   * POST /waste/upload  (multipart)
   * @param {FormData} formData — must include: title, category, estimated_weight, images[]
   */
  upload: (formData) => post('/waste/upload', formData, true),

  /** GET /waste/my-uploads?page=&page_size= */
  myUploads: (page = 1, pageSize = 10) =>
    get(`/waste/my-uploads?page=${page}&page_size=${pageSize}`),

  /** GET /waste/{waste_id} */
  getById: (wasteId) => get(`/waste/${wasteId}`),
};

// ═══════════════════════════════════════════════════════════════════════════
//  PICKUP MODULE   /pickup/*
// ═══════════════════════════════════════════════════════════════════════════
export const pickupAPI = {
  /** POST /pickup/create */
  create: (body) => post('/pickup/create', body),

  /**
   * GET /pickup/my-requests
   * @param {object|number} paramsOrPage — params object { status, page, page_size, from_date, to_date }
   *   or legacy positional page number (backwards compat)
   * @param {number} [pageSize] — legacy positional page_size (backwards compat)
   */
  myRequests: (paramsOrPage = {}, pageSize = 10) => {
    const params = (typeof paramsOrPage === 'object' && paramsOrPage !== null)
      ? paramsOrPage
      : { page: paramsOrPage, page_size: pageSize };
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ''))
    ).toString();
    return get(`/pickup/my-requests${q ? '?' + q : ''}`);
  },

  /** GET /pickup/{pickup_id} */
  getById: (pickupId) => get(`/pickup/${pickupId}`),

  /** PUT /pickup/cancel/{pickup_id} */
  cancel: (pickupId) => put(`/pickup/cancel/${pickupId}`),

  /** GET /pickup/track/{pickup_id} */
  track: (pickupId) => get(`/pickup/track/${pickupId}`),

  /** GET /pickup/qr/{pickup_id} */
  qr: (pickupId) => get(`/pickup/qr-credentials/${pickupId}`),

  /** POST /pickup/review/{pickup_id} */
  submitReview: (pickupId, body) => post(`/pickup/review/${pickupId}`, body),

  /** GET /pickup/reviews?pickup_id= */
  reviews: (pickupId) => {
    const q = pickupId ? `?pickup_id=${pickupId}` : '';
    return get(`/pickup/reviews${q}`);
  },
};

// ═══════════════════════════════════════════════════════════════════════════
//  COLLECTOR MODULE   /collector/*
// ═══════════════════════════════════════════════════════════════════════════
export const collectorAPI = {
  verifyQr: (code) => post('/collector/verify-qr', { code }),
  /** GET /collector/pickups?page=&page_size= */
  myPickups: (page = 1, pageSize = 10) =>
    get(`/collector/pickups?page=${page}&page_size=${pageSize}`),

  /** PUT /collector/accept/{pickup_id} */
  accept: (pickupId) => put(`/collector/accept/${pickupId}`),

  /** PUT /collector/reject/{pickup_id} */
  reject: (pickupId, reason) => put(`/collector/reject/${pickupId}`, { reason }),

  /** PUT /collector/collect/{pickup_id} */
  collect: (pickupId) => put(`/collector/collect/${pickupId}`),

  /** PUT /collector/handover/{pickup_id} */
  handover: (pickupId) => put(`/collector/handover/${pickupId}`),

  /** PUT /collector/update-weight/{pickup_id} */
  updateWeight: (pickupId, body) => put(`/collector/update-weight/${pickupId}`, body),

  /**
   * POST /collector/upload-proof/{pickup_id}  (multipart)
   * @param {number} pickupId
   * @param {FormData} formData — must include: image file, optional notes
   */
  uploadProof: (pickupId, formData) =>
    post(`/collector/upload-proof/${pickupId}`, formData, true),

  /** GET /collector/reviews */
  getReviews: () => get('/collector/reviews'),
};

// ═══════════════════════════════════════════════════════════════════════════
//  RECYCLER MODULE   /recycler/*
// ═══════════════════════════════════════════════════════════════════════════
export const recyclerAPI = {
  /** GET /recycler/assigned-waste */
  assignedWaste: (page = 1, pageSize = 10) =>
    get(`/recycler/assigned-waste?page=${page}&page_size=${pageSize}`),

  /** POST /recycler/process/{pickup_id} */
  startProcessing: (pickupId, body) => post(`/recycler/process/${pickupId}`, body),

  /** PUT /recycler/update-status/{pickup_id} */
  updateStatus: (pickupId, body) => put(`/recycler/update-status/${pickupId}`, body),

  /** GET /recycler/inventory */
  inventory: (page = 1, pageSize = 10) =>
    get(`/recycler/inventory?page=${page}&page_size=${pageSize}`),

  /** GET /recycler/history */
  myHistory: (page = 1, pageSize = 20) =>
    get(`/recycler/history?page=${page}&page_size=${pageSize}`),

  /** GET /recycler/processing-record/{id} */
  getProcessingRecord: (id) => get(`/recycler/processing-record/${id}`),

  /** POST /recycler/ai-recommend/{id} */
  aiRecommend: (id) => post(`/recycler/ai-recommend/${id}`),

  /** POST /recycler/send-payment/{pickup_id} */
  sendPayment: (pickupId, body) => post(`/recycler/send-payment/${pickupId}`, body),

  /** GET /recycler/my-payments */
  getMyPayments: (page = 1, pageSize = 20) => get(`/recycler/my-payments?page=${page}&page_size=${pageSize}`),
};

// ═══════════════════════════════════════════════════════════════════════════
//  USERS MODULE   /users/*
// ═══════════════════════════════════════════════════════════════════════════
export const usersAPI = {
  /** GET /users/rewards */
  getRewards: () => get('/users/rewards'),
};

// ═══════════════════════════════════════════════════════════════════════════
//  ADMIN MODULE   /admin/*
// ═══════════════════════════════════════════════════════════════════════════
export const adminAPI = {
  /** GET /admin/dashboard/overview (alias of getOverview — kept for AdminDashboard.jsx) */
  overview: () => get('/admin/dashboard/overview'),

  /** GET /admin/users?page=&page_size=&role=&is_active= */
  users: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/admin/users${q ? '?' + q : ''}`);
  },

  /** PUT /admin/block-user/{user_id} */
  blockUser: (userId) => put(`/admin/block-user/${userId}`),

  /** PUT /admin/unblock-user/{user_id} */
  unblockUser: (userId) => put(`/admin/unblock-user/${userId}`),

  /** Pricing Rules CRUD */

  /** Forecast */
  getForecast: () => get('/admin/forecast'),

  /** GET /admin/pickups?page=&page_size=&status= */
  pickups: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/admin/pickups${q ? '?' + q : ''}`);
  },

  /** GET /admin/waste-uploads */
  wasteUploads: (page = 1, pageSize = 20) =>
    get(`/admin/waste-uploads?page=${page}&page_size=${pageSize}`),

  /** GET /admin/reports */
  reports: () => get('/admin/reports'),

  /** POST /admin/create-user */
  createUser: (body) => post('/admin/create-user', body),

  /** PUT /admin/assign-pickup/{pickup_id} */
  assignPickup: (pickupId, body) => put(`/admin/assign-pickup/${pickupId}`, body),

  /** PUT /admin/update-user/{id} */
  updateUser: (id, body) => put(`/admin/update-user/${id}`, body),

  /** DELETE /admin/delete-user/{id} */
  deleteUser: (id) => del(`/admin/delete-user/${id}`),

  /** PUT /admin/update-user/{id} (alias of updateUser — kept for collector management in AdminPages.jsx) */
  updateCollector: (id, body) => put(`/admin/update-user/${id}`, body),

  /** DELETE /admin/delete-user/{id} (alias of deleteUser — kept for collector management in AdminPages.jsx) */
  deleteCollector: (id) => del(`/admin/delete-user/${id}`),

  /** PATCH /admin/recyclers/{id}/status */
  updateRecyclerStatus: (id, body) => patch(`/admin/recyclers/${id}/status`, body),

  /** GET /admin/dashboard/overview */
  getOverview: () => get('/admin/dashboard/overview'),

  /** GET /admin/analytics */
  getAnalytics: () => get('/admin/analytics'),

  /** GET /admin/revenue */
  getRevenue: () => get('/admin/revenue'),

  /** GET /admin/payments (Revenue Tracking) */
  getPayments: (page = 1, pageSize = 20) => get(`/admin/payments?page=${page}&page_size=${pageSize}`),

  /** GET /admin/completed-jobs (for reward point assignment) */
  getCompletedJobs: (page = 1, pageSize = 20) => get(`/admin/completed-jobs?page=${page}&page_size=${pageSize}`),

  /** POST /admin/assign-reward-points */
  assignRewardPoints: (body) => post('/admin/assign-reward-points', body),

  /** Pricing rules */
  getPricingRules: () => get('/admin/pricing-rules'),
  createPricingRule: (body) => post('/admin/pricing-rules', body),
  updatePricingRule: (id, body) => put(`/admin/pricing-rules/${id}`, body),
  deletePricingRule: (id) => del(`/admin/pricing-rules/${id}`),
};

// ═══════════════════════════════════════════════════════════════════════════
//  NOTIFICATIONS MODULE   /notifications/*
// ═══════════════════════════════════════════════════════════════════════════
export const notificationsAPI = {
  /** GET /notifications/me */
  getMyNotifications: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/notifications/me${q ? '?' + q : ''}`);
  },

  /** PATCH /notifications/{id}/read */
  markAsRead: (id) => patch(`/notifications/${id}/read`),
};

// ═══════════════════════════════════════════════════════════════════════════
//  SYSTEM   /roles   /status-types   /config
// ═══════════════════════════════════════════════════════════════════════════
export const systemAPI = {
  /** GET /roles */
  roles: () => get('/roles'),

  /** GET /status-types */
  statusTypes: () => get('/status-types'),

  /** GET /config */
  config: () => get('/config'),

  /** GET /pricing-rates */
  pricingRates: () => get('/pricing-rates'),
};

// Default export bundles all modules
const api = { auth: authAPI, waste: wasteAPI, pickup: pickupAPI,
              collector: collectorAPI, recycler: recyclerAPI,
              users: usersAPI, admin: adminAPI, notifications: notificationsAPI,
              system: systemAPI };
export default api;
