import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api, { getUser, BASE_URL } from '../../services/api';

// Recycler nav: Collected Waste Listing → Waste Receipt → AI Recommendation → Processing Decision → Inventory → History
const navItems = [
  { path: '/dashboard', icon: 'dashboard', label: 'Dashboard' },
  { path: '/collected-waste-listing', icon: 'inventory_2', label: 'Collected Waste' },
  { path: '/waste-receipt', icon: 'receipt_long', label: 'Waste Receipt' },
  { path: '/ai-recommendation', icon: 'psychology', label: 'AI Recommendation' },
  { path: '/processing-decision', icon: 'gavel', label: 'Processing Decision' },
  { path: '/inventory-management', icon: 'warehouse', label: 'Inventory Management' },
  { path: '/processing-history', icon: 'history', label: 'Processing History' },
];

export default function RecyclerSidebar({ isOpen, setIsOpen }) {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser('recycler');
  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    try {
      await api.auth.logout();
    } catch (e) {
      console.error('Logout failed:', e);
    } finally {
      navigate('/');
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
        className={`h-screen w-64 fixed left-0 top-0 bg-[#326669] dark:bg-slate-900 border-r border-white/10 dark:border-slate-800 shadow-xl flex flex-col py-6 px-4 z-50 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
      <div className="mb-10 px-2 flex items-center justify-between">
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
      <nav className="flex-1 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-left ${
              isActive(item.path)
                ? 'bg-white/10 text-white font-bold border-l-4 border-white'
                : 'text-white/70 hover:text-white hover:bg-white/5'
            }`}
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span className="font-['Inter'] font-medium text-sm tracking-tight">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="pt-6 border-t border-white/10 space-y-1 mt-auto pb-24">
        <button
          onClick={() => navigate('/recycler/profile')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-left ${
            isActive('/recycler/profile') ? 'bg-white/10 text-white font-bold' : 'text-white/70 hover:text-white hover:bg-white/5'
          }`}
        >
          <span className="material-symbols-outlined">settings</span>
          <span className="font-['Inter'] font-medium text-sm tracking-tight">Profile / Settings</span>
        </button>
        {/* <button
          onClick={() => navigate('/recycler/change-password')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-left ${
            isActive('/recycler/change-password') ? 'bg-white/10 text-white font-bold' : 'text-white/70 hover:text-white hover:bg-white/5'
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">lock_reset</span>
          <span className="font-['Inter'] text-[15px] font-medium tracking-tight">Change Password</span>
        </button> */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/70 hover:text-white hover:bg-white/5 transition-all duration-200 text-left"
        >
          <span className="material-symbols-outlined">logout</span>
          <span className="font-['Inter'] font-medium text-sm tracking-tight">Logout</span>
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
            <p className="text-xs font-bold text-white">{user?.full_name || 'Recycler'}</p>
            <p className="text-[10px] text-white/60">Verified Partner</p>
          </div>
        </div>
      </div>
    </aside>
    </>
  );
}
