import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import CustomPopup from './components/common/CustomPopup';

// Routing Components
import PublicRoute from './components/auth_routes/PublicRoute';
import ProtectedRoute from './components/auth_routes/ProtectedRoute';

// Auth & Public Pages
import LandingPage from './pages/auth/LandingPage';
import Register from './pages/auth/Register';
import Login from './pages/auth/Login';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Recycler Panel
import Dashboard from './pages/recycler/Dashboard';
import WasteReceipt from './pages/recycler/WasteReceipt';
import ProcessingDecision from './pages/recycler/ProcessingDecision';
import AiRecommendation from './pages/recycler/AiRecommendation';
import InventoryManagement from './pages/recycler/InventoryManagement';
import ProcessingHistory from './pages/recycler/ProcessingHistory';
import RecyclerProfile from './pages/recycler/RecyclerProfile';
import RecyclerChangePassword from './pages/recycler/RecyclerChangePassword';
import CollectedWasteListing from './pages/recycler/CollectedWasteListing';

// User Panel
import UserDashboard from './pages/user/UserDashboard';
import UploadEwaste from './pages/user/UploadEwaste';
import AiPriceEstimation from './pages/user/AiPriceEstimation';
import SchedulePickup from './pages/user/SchedulePickup';
import TrackPickup from './pages/user/TrackPickup';
import QRDisplay from './pages/user/QRDisplay';
import RecyclingHistory from './pages/user/RecyclingHistory';
import RewardWallet from './pages/user/RewardWallet';
import UserProfile from './pages/user/UserProfile';
import UserChangePassword from './pages/user/UserChangePassword';
import ReviewRating from './pages/user/ReviewRating';

// Admin Panel
import AdminDashboard from './pages/admin/AdminDashboard';
import {
  UserManagement,
  CollectorManagement,
  WasteAssignment,
  RecyclerApproval,
  WasteAnalytics,
  RevenueTracking,
  CO2Analytics,
  PickupStatistics,
  AreaAnalytics,
  TrendForecasting,
  PricingRules,
  WasteUploads,
  Reports,
  AdminProfile,
  AddUser,
  AddCollector,
  AdminChangePassword,
  AssignRewardPoints,
} from './pages/admin/AdminPages';

// Collector Panel
import CollectorDashboard from './pages/collector/CollectorDashboard';
import {
  AssignedPickups,
  RouteOptimization,
  ScanQRCode,
  UploadProof,
  UpdateStatus,
  CollectorSettings,
} from './pages/collector/CollectorPages';
import CollectorAvailability from './pages/collector/CollectorAvailability';
import CollectorChangePassword from './pages/collector/CollectorChangePassword';
import CollectorReviews from './pages/collector/CollectorReviews';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
        <Route path="/reset-password" element={<PublicRoute><ResetPassword /></PublicRoute>} />

        {/* Recycler Dashboard Routes */}
        <Route element={<ProtectedRoute allowedRoles={['recycler']} />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/collected-waste-listing" element={<CollectedWasteListing />} />
          <Route path="/waste-receipt/:id" element={<WasteReceipt />} />
          <Route path="/waste-receipt" element={<WasteReceipt />} />
          <Route path="/ai-recommendation/:id" element={<AiRecommendation />} />
          <Route path="/ai-recommendation" element={<AiRecommendation />} />
          <Route path="/processing-decision/:id" element={<ProcessingDecision />} />
          <Route path="/processing-decision" element={<ProcessingDecision />} />
          <Route path="/inventory-management" element={<InventoryManagement />} />
          <Route path="/processing-history" element={<ProcessingHistory />} />
          <Route path="/recycler/profile" element={<RecyclerProfile />} />
          <Route path="/recycler/change-password" element={<RecyclerChangePassword />} />
        </Route>

        {/* User Dashboard Routes */}
        <Route element={<ProtectedRoute allowedRoles={['user']} />}>
          <Route path="/user-dashboard" element={<UserDashboard />} />
          <Route path="/user/upload-ewaste" element={<UploadEwaste />} />
          <Route path="/user/ai-price/:id" element={<AiPriceEstimation />} />
          <Route path="/user/schedule-pickup" element={<SchedulePickup />} />
          <Route path="/pickup/track" element={<TrackPickup />} />
          <Route path="/pickup/:id/track" element={<TrackPickup />} />
          <Route path="/pickup/:id/qr" element={<QRDisplay />} />
          <Route path="/user/recycling-history" element={<RecyclingHistory />} />
          <Route path="/user/reward-wallet" element={<RewardWallet />} />
          <Route path="/user/review-rating" element={<ReviewRating />} />
          <Route path="/user/profile" element={<UserProfile />} />
          <Route path="/user/change-password" element={<UserChangePassword />} />
        </Route>

        {/* Admin Dashboard Routes */}
        <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          <Route path="/admin/user-management" element={<UserManagement />} />
          <Route path="/admin/add-user" element={<AddUser />} />
          <Route path="/admin/collector-management" element={<CollectorManagement />} />
          <Route path="/admin/add-collector" element={<AddCollector />} />
          <Route path="/admin/waste-assignment" element={<WasteAssignment />} />
          <Route path="/admin/recycler-approval" element={<RecyclerApproval />} />
          <Route path="/admin/waste-analytics" element={<WasteAnalytics />} />
          <Route path="/admin/revenue-tracking" element={<RevenueTracking />} />
          <Route path="/admin/co2-analytics" element={<CO2Analytics />} />
          <Route path="/admin/pickup-statistics" element={<PickupStatistics />} />
          <Route path="/admin/area-analytics" element={<AreaAnalytics />} />
          <Route path="/admin/trend-forecasting" element={<TrendForecasting />} />
          <Route path="/admin/pricing-rules" element={<PricingRules />} />
          <Route path="/admin/waste-uploads" element={<WasteUploads />} />
          <Route path="/admin/reports" element={<Reports />} />
          <Route path="/admin/assign-reward-points" element={<AssignRewardPoints />} />
          <Route path="/admin/profile" element={<AdminProfile />} />
          <Route path="/admin/change-password" element={<AdminChangePassword />} />
        </Route>

        {/* Collector Dashboard Routes */}
        <Route element={<ProtectedRoute allowedRoles={['collector']} />}>
          <Route path="/collector-dashboard" element={<CollectorDashboard />} />
          <Route path="/collector/assigned-pickups" element={<AssignedPickups />} />
          <Route path="/collector/route-optimization" element={<RouteOptimization />} />
          <Route path="/collector/scan-qr" element={<ScanQRCode />} />
          <Route path="/collector/upload-proof" element={<UploadProof />} />
          <Route path="/collector/update-status" element={<UpdateStatus />} />
          <Route path="/collector/settings" element={<CollectorSettings />} />
          <Route path="/collector/availability" element={<CollectorAvailability />} />
          <Route path="/collector/change-password" element={<CollectorChangePassword />} />
          <Route path="/collector/reviews" element={<CollectorReviews />} />
        </Route>

        {/* Catch-all Route */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
      <Toaster position="top-right" />
      <CustomPopup />
    </Router>
  );
}
