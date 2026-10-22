import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api, { getUser, BASE_URL } from '../../services/api';

const navItems = [
  { path: '/admin-dashboard', icon: 'dashboard', label: 'Dashboard' },
  { path: '/admin/user-management', icon: 'group', label: 'User Management' },
  { path: '/admin/collector-management', icon: 'local_shipping', label: 'Collector Management' },
  { path: '/admin/waste-assignment', icon: 'assignment_ind', label: 'Waste Assignment' },
  { path: '/admin/recycler-approval', icon: 'verified', label: 'Recycler Approval' },
  { path: '/admin/waste-analytics', icon: 'analytics', label: 'Waste Analytics' },
  { path: '/admin/revenue-tracking', icon: 'payments', label: 'Revenue Tracking' },
  { path: '/admin/co2-analytics', icon: 'eco', label: 'CO2 Analytics' },
  { path: '/admin/pickup-statistics', icon: 'assessment', label: 'Pickup Statistics' },
  { path: '/admin/area-analytics', icon: 'map', label: 'Area Analytics' },
  { path: '/admin/trend-forecasting', icon: 'query_stats', label: 'Trend Forecasting' },
  { path: '/admin/pricing-rules', icon: 'rule', label: 'Pricing Rules' },
  { path: '/admin/waste-uploads', icon: 'cloud_upload', label: 'Waste Uploads' },
  { path: '/admin/reports', icon: 'description', label: 'Reports' },
];

export default function AdminSidebar({ isOpen, setIsOpen }) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser('admin');
  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    try {
      await api.auth.logout();
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Server logout failed:', error);
      alert('Could not securely log out. Please try again.');
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`fixed left-0 top-0 h-full w-64 z-50 bg-teal-900 shadow-xl flex flex-col py-6 space-y-1 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
      <div className="px-6 mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
          <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
            <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
          </div>
          <span className="text-2xl font-black tracking-tighter text-white">RenewGrid</span>
        </div>
        {/* Close button for mobile */}
        <button 
          className="md:hidden text-white/80 hover:text-white"
          onClick={() => setIsOpen(false)}
        >
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>
      <nav className="flex-1 space-y-1 px-2 overflow-y-auto">
        {navItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-all text-left ${
              isActive(item.path) ? 'bg-teal-700/50 text-white font-medium' : 'text-teal-100/70 hover:text-white hover:bg-teal-800/40'
            }`}
          >
            <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="px-2 pt-4 border-t border-teal-800/50 mt-auto mb-0 pb-24">
        <button
          onClick={() => navigate('/admin/profile')}
          className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-all text-left ${
            isActive('/admin/profile') ? 'bg-teal-700/50 text-white' : 'text-teal-100/70 hover:text-white hover:bg-teal-800/40'
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">person</span>
          <span>Profile / Settings</span>
        </button>
        <button
          onClick={handleLogout}
          className="w-full text-teal-100/70 hover:text-red-300 hover:bg-teal-800/40 px-4 py-2 flex items-center space-x-3 rounded-lg transition-all text-left mt-2"
        >
          <span className="material-symbols-outlined text-[20px]">logout</span>
          <span>Logout</span>
        </button>
      </div>

      <div className="absolute bottom-0 left-0 w-full p-6 bg-[#264f51]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#D5E3EB] flex items-center justify-center font-bold text-[#326669] overflow-hidden">
            {user?.profile_image ? (
              <img src={user.profile_image.startsWith('http') ? user.profile_image : `${BASE_URL}${user.profile_image}`} alt="Avatar" className="w-full h-full object-cover" />
            ) : user?.full_name ? (
              user.full_name.charAt(0).toUpperCase()
            ) : (
              <span className="material-symbols-outlined text-[#326669] text-xl">person</span>
            )}
          </div>
          <div>
            <p className="text-xs font-bold text-white">{user?.full_name || 'Super Admin'}</p>
            <p className="text-[10px] text-white/60">{user?.email || 'admin@renewgrid.com'}</p>
          </div>
        </div>
      </div>
    </aside>
    </>
  );
}
