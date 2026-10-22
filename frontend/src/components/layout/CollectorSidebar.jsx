import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api, { getUser, BASE_URL } from '../../services/api';

const navItems = [
  { path: '/collector-dashboard', icon: 'dashboard', label: 'Dashboard' },
  { path: '/collector/assigned-pickups', icon: 'local_shipping', label: 'Assigned Pickups' },
  { path: '/collector/route-optimization', icon: 'route', label: 'Route Optimization' },
  { path: '/collector/scan-qr', icon: 'qr_code_scanner', label: 'Scan QR Code' },
  { path: '/collector/upload-proof', icon: 'upload_file', label: 'Upload Proof' },
  { path: '/collector/update-status', icon: 'sync_alt', label: 'Update Status' },
  { path: '/collector/availability', icon: 'calendar_month', label: 'Availability' },
  { path: '/collector/reviews', icon: 'star', label: 'My Reviews' },
];

export default function CollectorSidebar({ isOpen, setIsOpen }) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser('collector');
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
        className={`h-screen w-64 fixed left-0 top-0 border-r-0 bg-[#326669] dark:bg-slate-900 shadow-xl flex flex-col py-6 z-50 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
      <div className="px-6 mb-8 flex items-center justify-between">
        <div className="flex flex-col gap-2 cursor-pointer" onClick={() => navigate('/')}>
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
              <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
            </div>
            <span className="text-2xl font-black tracking-tighter text-white">RenewGrid</span>
          </div>
        </div>
        {/* Close button for mobile */}
        <button 
          className="md:hidden text-white/80 hover:text-white"
          onClick={() => setIsOpen(false)}
        >
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mx-2 my-1 font-['Inter'] font-medium text-sm tracking-tight transition-all duration-200 active:scale-95 text-left ${
              isActive(item.path) ? 'bg-white/10 text-white' : 'text-white/70 hover:text-white hover:bg-white/5'
            }`}
            style={{ width: 'calc(100% - 16px)' }}
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="mt-auto border-t border-white/10 pt-4 space-y-1 pb-24">
        <button
          onClick={() => navigate('/collector/settings')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mx-2 my-1 font-['Inter'] font-medium text-sm tracking-tight transition-all duration-200 text-left ${
            isActive('/collector/settings') ? 'bg-white/10 text-white' : 'text-white/70 hover:text-white hover:bg-white/5'
          }`}
          style={{ width: 'calc(100% - 16px)' }}
        >
          <span className="material-symbols-outlined">settings</span>
          Profile / Settings
        </button>

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-white/70 hover:text-white hover:bg-white/5 rounded-lg mx-2 my-1 font-['Inter'] font-medium text-sm tracking-tight transition-all duration-200 text-left"
          style={{ width: 'calc(100% - 16px)' }}
        >
          <span className="material-symbols-outlined">logout</span>
          Logout
        </button>
      </div>

      <div className="absolute bottom-0 left-0 w-full p-6 bg-[#264f51]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#D5E3EB] flex items-center justify-center overflow-hidden">
            {user?.profile_image ? (
              <img src={user.profile_image.startsWith('http') ? user.profile_image : `${BASE_URL}${user.profile_image}`} alt="Avatar" className="w-full h-full object-cover" />
            ) : user?.full_name ? (
              <span className="text-[#326669] font-bold">{user.full_name.charAt(0).toUpperCase()}</span>
            ) : (
              <span className="material-symbols-outlined text-[#326669] text-xl">person</span>
            )}
          </div>
          <div>
            <p className="text-xs font-bold text-white">{user?.full_name || 'Collector'}</p>
            <p className="text-[10px] flex items-center gap-1 text-white/60">
              <span className={`w-2 h-2 rounded-full ${user?.is_available ? 'bg-green-400' : 'bg-red-400'}`}></span>
              {user?.is_available ? 'Available' : 'Unavailable'}
            </p>
          </div>
        </div>
      </div>
    </aside>
    </>
  );
}
