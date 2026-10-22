import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api, { getUser, BASE_URL } from '../../services/api';

const navItems = [
  { path: '/user-dashboard', icon: 'dashboard', label: 'Dashboard', filled: true },
  { path: '/user/upload-ewaste', icon: 'upload_file', label: 'Upload E-Waste' },
  { path: '/user/schedule-pickup', icon: 'calendar_today', label: 'Schedule Pickup' },
  { path: '/pickup/track', icon: 'local_shipping', label: 'Track Pickup Status' },
  { path: '/user/recycling-history', icon: 'history', label: 'Recycling History' },
  { path: '/user/reward-wallet', icon: 'account_balance_wallet', label: 'Reward Wallet' },
  { path: '/user/review-rating', icon: 'star_rate', label: 'Review & Rating' },
];

export default function UserSidebar({ isOpen, setIsOpen }) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser('user');
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
        className={`fixed left-0 top-0 h-full w-64 bg-[#326669] text-white z-50 flex flex-col transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
              <span className="material-symbols-outlined text-primary text-xl">recycling</span>
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

        <nav className="space-y-1">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all text-left ${
                isActive(item.path)
                  ? 'bg-[#D5E3EB] text-[#326669] font-bold'
                  : 'text-white/80 hover:bg-white/10'
              }`}
            >
              <span className="material-symbols-outlined" style={isActive(item.path) && item.filled ? { fontVariationSettings: "'FILL' 1" } : {}}>{item.icon}</span>
              <span className="text-sm">{item.label}</span>
            </button>
          ))}
          <div className="pt-6 mt-6 border-t border-white/10 space-y-1">
            <button
              onClick={() => navigate('/user/profile')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all text-left ${
                isActive('/user/profile') ? 'bg-[#D5E3EB] text-[#326669] font-bold' : 'text-white/80 hover:bg-white/10'
              }`}
            >
              <span className="material-symbols-outlined">settings</span>
              <span className="text-sm">Profile / Settings</span>
            </button>
            {/* <button
              onClick={() => navigate('/user/change-password')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all text-left ${
                isActive('/user/change-password') ? 'bg-[#D5E3EB] text-[#326669] font-bold' : 'text-white/80 hover:bg-white/10'
              }`}
            >
              <span className="material-symbols-outlined">lock_reset</span>
              <span className="text-sm">Change Password</span>
            </button> */}
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 text-white/80 hover:text-red-300 transition-all rounded-xl mt-2 text-left"
            >
              <span className="material-symbols-outlined">logout</span>
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </nav>
      </div>

      <div className="shrink-0 p-6 bg-[#264f51]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#D5E3EB] flex items-center justify-center overflow-hidden">
            {user?.profile_image ? (
              <img src={user.profile_image.startsWith('http') ? user.profile_image : `${BASE_URL}${user.profile_image}`} alt="Avatar" className="w-full h-full object-cover" />
            ) : user?.full_name ? (
              <span className="text-primary font-bold">{user.full_name.charAt(0).toUpperCase()}</span>
            ) : (
              <span className="material-symbols-outlined text-primary text-xl">person</span>
            )}
          </div>
          <div>
            <p className="text-xs font-bold text-white">{user?.full_name || 'User'}</p>
            <p className="text-[10px] text-white/60">Verified Member</p>
          </div>
        </div>
      </div>
    </aside>
    </>
  );
}
