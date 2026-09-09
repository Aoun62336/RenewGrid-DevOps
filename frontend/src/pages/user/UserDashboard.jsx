import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import UserSidebar from '../../components/layout/UserSidebar';
import { pickupAPI, getUser } from '../../services/api';

export default function UserDashboard() {
  const navigate = useNavigate();
  const user     = getUser();

  const [stats,    setStats]    = useState({ total: 0, pending: 0, completed: 0, cancelled: 0, inProgress: 0 });
  const [pickups,  setPickups]  = useState([]);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await pickupAPI.myRequests(1, 20);
        const items = res.items || [];
        setPickups(items.slice(0, 5));
        setStats({
          total:      res.total || 0,
          pending:    items.filter(p => p.status === 'PENDING').length,
          inProgress: items.filter(p => ['ASSIGNED','IN_PROGRESS'].includes(p.status)).length,
          completed:  items.filter(p => p.status === 'COMPLETED').length,
          cancelled:  items.filter(p => p.status === 'CANCELLED').length,
        });
      } catch (err) { console.error('Dashboard load error:', err); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const statusColor = (s) => ({
    PENDING:     'bg-amber-100 text-amber-700 border border-amber-200',
    ASSIGNED:    'bg-blue-100 text-blue-700 border border-blue-200',
    IN_PROGRESS: 'bg-primary text-white',
    COLLECTED:   'bg-teal-100 text-teal-700 border border-teal-200',
    PROCESSING:  'bg-purple-100 text-purple-700 border border-purple-200',
    COMPLETED:   'bg-green-100 text-green-700 border border-green-200',
    CANCELLED:   'bg-red-100 text-red-650 border border-red-200',
  }[s] ?? 'bg-slate-100 text-slate-600');

  const statusIcon = (s) => ({
    PENDING:     'pending_actions',
    ASSIGNED:    'local_shipping',
    IN_PROGRESS: 'directions_run',
    COLLECTED:   'archive',
    PROCESSING:  'precision_manufacturing',
    COMPLETED:   'task_alt',
    CANCELLED:   'cancel',
  }[s] ?? 'inventory_2');

  const statusIconColors = (s) => ({
    PENDING:     'text-amber-500 bg-amber-50',
    ASSIGNED:    'text-blue-500 bg-blue-50',
    IN_PROGRESS: 'text-primary bg-primary-container/30',
    COLLECTED:   'text-teal-600 bg-teal-50',
    PROCESSING:  'text-purple-650 bg-purple-50',
    COMPLETED:   'text-green-600 bg-green-50',
    CANCELLED:   'text-red-500 bg-red-50',
  }[s] ?? 'text-slate-500 bg-slate-50');

  const completionRate = stats.total ? Math.round((stats.completed / stats.total) * 100) : 0;

  const metricCards = [
    { label: 'Total Requests',  val: stats.total,      icon: 'inventory_2',     color: 'text-primary', bg: 'bg-primary-container' },
    { label: 'Pending Request', val: stats.pending,    icon: 'pending_actions', color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: 'In Progress',     val: stats.inProgress, icon: 'local_shipping',  color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Recycle Done',    val: stats.completed,  icon: 'task_alt',        color: 'text-teal-600', bg: 'bg-teal-50', hasGauge: true },
    { label: 'Cancelled Requests', val: stats.cancelled,  icon: 'cancel',       color: 'text-red-600', bg: 'bg-red-50' },
  ];

  return (
    <div className="bg-surface text-on-surface min-h-screen relative">
      <UserSidebar />
      <main className="ml-64 min-h-screen bg-[#f6f7f7]">
        <header className="fixed top-0 right-0 w-[calc(100%-16rem)] h-16 bg-white/85 backdrop-blur-md shadow-sm z-40 flex items-center justify-between px-8">
          <h1 className="text-xl font-extrabold text-[#326669] tracking-tight">User Dashboard</h1>
          <button className="text-slate-500 hover:text-[#326669] transition-colors relative p-2 rounded-full hover:bg-primary/10">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
          </button>
        </header>

        <div className="pt-24 p-10 max-w-[1400px] mx-auto space-y-10">
          {/* Welcome Card with Gradient background */}
          <div className="bg-white rounded-3xl p-8 border border-outline-variant shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-8 -mr-8 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
            <div>
              <h2 className="text-4xl font-black text-slate-900 tracking-tight mb-2 leading-none">
                Welcome back, <span className="text-primary italic font-black">{user?.full_name?.split(' ')[0] ?? 'User'}!</span>
              </h2>
              <p className="text-slate-500 font-medium">Your circular e-waste journey is making a massive difference.</p>
            </div>
            <div className="flex gap-3 shrink-0">
              <button onClick={() => navigate('/user/profile')}
                className="px-6 py-3.5 bg-white border-2 border-primary text-primary hover:bg-primary/5 rounded-2xl font-bold flex items-center gap-2 transition-all">
                <span className="material-symbols-outlined">person_outline</span> View Profile
              </button>
              <button onClick={() => navigate('/user/upload-ewaste')}
                className="px-6 py-3.5 bg-primary hover:bg-[#285255] text-white rounded-2xl font-black flex items-center gap-2 shadow-lg shadow-primary/20 hover:scale-[1.01] active:scale-[0.99] transition-all">
                <span className="material-symbols-outlined" style={{fontVariationSettings:"'FILL' 1"}}>add_circle</span>
                Schedule Pickup
              </button>
            </div>
          </div>

          {/* Metric Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-6">
            {metricCards.map((m, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-outline-variant hover:shadow-lg hover:scale-[1.02] transition-all duration-300 flex flex-col justify-between group relative overflow-hidden">
                <div className="absolute top-0 right-0 -mt-2 -mr-2 w-12 h-12 bg-slate-50 rounded-full blur-md pointer-events-none"></div>
                <div>
                  <div className={`w-12 h-12 ${m.bg} ${m.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <span className="material-symbols-outlined">{m.icon}</span>
                  </div>
                  <p className="text-[10px] font-bold text-slate-450 uppercase tracking-widest leading-none">{m.label}</p>
                  {loading ? (
                    <div className="h-8 w-12 bg-slate-100 animate-pulse rounded mt-1.5" />
                  ) : (
                    <p className="text-3xl font-black text-slate-800 mt-1">{m.val}</p>
                  )}
                </div>
                {m.hasGauge && !loading && stats.total > 0 && (
                  <div className="mt-4 pt-2 border-t border-slate-50 flex items-center justify-between text-[10px] font-bold text-slate-400">
                    <span>Recycle Rate</span>
                    <span className="text-teal-600">{completionRate}%</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Recent Pickups list cards */}
          <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
            <div className="flex items-center justify-between px-8 py-6 border-b border-outline-variant">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Recent Pickup Requests</h3>
                <p className="text-xs text-slate-400 mt-0.5 font-medium font-display">Tracking history of your recycling points</p>
              </div>
              <button onClick={() => navigate('/user/recycling-history')}
                className="text-primary font-bold text-sm hover:underline flex items-center gap-1">
                View All <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-48">
                <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
              </div>
            ) : pickups.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center mb-4 border border-slate-100">
                  <span className="material-symbols-outlined text-3xl text-slate-350">inventory_2</span>
                </div>
                <p className="text-slate-500 font-bold">No pickup requests yet.</p>
                <p className="text-slate-400 text-xs mt-1">Ready to recycle? Request a dynamic e-waste pick up.</p>
                <button onClick={() => navigate('/user/upload-ewaste')}
                  className="mt-6 px-6 py-3 bg-primary hover:bg-[#285255] text-white rounded-xl font-bold text-sm shadow-md hover:scale-[1.01] transition-all">
                  Schedule Your First Pickup
                </button>
              </div>
            ) : (
              <div className="divide-y divide-outline-variant">
                {pickups.map(p => (
                  <div key={p.id} className="flex items-center justify-between px-8 py-5 hover:bg-slate-50/50 transition-colors cursor-pointer group"
                    onClick={() => navigate(`/pickup/${p.id}/track`)}>
                    <div className="flex items-center gap-4">
                      <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-slate-100/50 group-hover:scale-105 transition-transform duration-300 ${statusIconColors(p.status)}`}>
                        <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>
                          {statusIcon(p.status)}
                        </span>
                      </div>
                      <div>
                        <p className="font-bold text-slate-900 group-hover:text-primary transition-colors text-sm">Request #RG-{p.id}</p>
                        <p className="text-xs text-slate-400 mt-0.5 truncate max-w-xs sm:max-w-md">{p.address}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <span className="text-xs text-slate-405 font-medium hidden sm:inline-block">
                        {new Date(p.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                      </span>
                      <span className={`px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider ${statusColor(p.status)}`}>
                        {p.status?.replace('_', ' ')}
                      </span>
                      <span className="material-symbols-outlined text-slate-300 text-sm group-hover:text-primary transition-colors">chevron_right</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { label: 'Schedule Pickup',   icon: 'add_circle',       path: '/user/upload-ewaste', color: 'text-primary' },
              { label: 'Track Pickup',      icon: 'local_shipping',   path: '/pickup/track', color: 'text-blue-500' },
              { label: 'Recycling History', icon: 'history',          path: '/user/recycling-history', color: 'text-teal-600' },
              { label: 'My Profile',        icon: 'manage_accounts',  path: '/user/profile', color: 'text-slate-650' },
            ].map((a, i) => (
              <button key={i} onClick={() => navigate(a.path)}
                className="flex flex-col items-center gap-3 p-6 bg-white rounded-2xl border border-outline-variant hover:border-primary/40 hover:shadow-lg transition-all duration-300 group">
                <div className="w-12 h-12 bg-slate-50 group-hover:bg-primary group-hover:text-white rounded-xl flex items-center justify-center text-slate-500 transition-all duration-300 shadow-sm border border-slate-100">
                  <span className="material-symbols-outlined">{a.icon}</span>
                </div>
                <span className="text-sm font-bold text-slate-700 group-hover:text-primary transition-colors text-center">{a.label}</span>
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
