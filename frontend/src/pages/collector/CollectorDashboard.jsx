import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CollectorSidebar from '../../components/layout/CollectorSidebar';
import { collectorAPI, getUser } from '../../services/api';

export default function CollectorDashboard() {
  const navigate = useNavigate();
  const user     = getUser();

  const [pickups,  setPickups]  = useState([]);
  const [stats,    setStats]    = useState({ total: 0, pending: 0, inProgress: 0, collected: 0 });
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res   = await collectorAPI.myPickups(1, 50);
        const items = res.items || [];
        setPickups(items.slice(0, 6));
        setStats({
          total:      res.total || 0,
          pending:    items.filter(p => p.status === 'ASSIGNED').length,
          inProgress: items.filter(p => p.status === 'IN_PROGRESS').length,
          collected:  items.filter(p => p.status === 'COLLECTED').length,
        });
      } catch (err) { console.error('Dashboard load error:', err); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const statusBadge = (s) => {
    const map = {
      ASSIGNED:    'bg-blue-50 text-blue-700 border border-blue-200',
      IN_PROGRESS: 'bg-amber-50 text-amber-700 border border-amber-200',
      COLLECTED:   'bg-emerald-50 text-emerald-700 border border-emerald-200',
      CANCELLED:   'bg-red-50 text-red-600 border border-red-200',
    };
    return map[s] ?? 'bg-slate-50 text-slate-600 border border-slate-200';
  };

  return (
    <div className="bg-[#f8fafc] text-slate-900 min-h-screen relative font-sans">
      <CollectorSidebar />

      <header className="fixed top-0 right-0 w-[calc(100%-16rem)] h-20 bg-white/70 backdrop-blur-xl border-b border-slate-200 z-40 flex items-center justify-between px-10">
        <h1 className="text-2xl font-black text-slate-800">Collector Dashboard</h1>
        <div className="flex items-center gap-4">
          <button className="text-slate-400 hover:text-primary transition-all relative p-3 rounded-full hover:bg-slate-100">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-white animate-pulse" />
          </button>
        </div>
      </header>

      <main className="ml-64 pt-28 pb-16 px-10">
        {/* Welcome Gradient Banner */}
        <div className="relative overflow-hidden bg-gradient-to-r from-primary to-[#2a5557] rounded-3xl p-10 mb-10 text-white shadow-xl shadow-primary/20">
          <div className="relative z-10">
            <p className="font-bold tracking-widest text-xs uppercase opacity-80 mb-2">Welcome Back</p>
            <h2 className="text-4xl font-black tracking-tight">
              Hello, {user?.full_name?.split(' ')[0] ?? 'Collector'}!
            </h2>
            <p className="mt-2 text-white/80 max-w-lg">Ready to make a difference today? Here's an overview of your active pickup schedule.</p>
          </div>
          <div className="absolute right-0 top-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        </div>

        {/* Stats */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
          {[
            { label: 'Total Assigned', val: stats.total, icon: 'local_shipping', color: 'text-primary' },
            { label: 'Pending', val: stats.pending, icon: 'pending_actions', color: 'text-blue-600' },
            { label: 'In Progress', val: stats.inProgress, icon: 'directions_car', color: 'text-amber-600' },
            { label: 'Collected', val: stats.collected, icon: 'check_circle', color: 'text-emerald-600' },
          ].map((m, i) => (
            <div key={i} className="group bg-white rounded-3xl p-7 shadow-sm border border-slate-100 hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5 transition-all duration-300">
              <div className={`text-4xl mb-4 ${m.color} transition-transform group-hover:scale-110`}>
                <span className="material-symbols-outlined text-4xl">{m.icon}</span>
              </div>
              {loading ? (
                <div className="h-10 w-16 bg-slate-100 animate-pulse rounded" />
              ) : (
                <span className="block text-4xl font-black text-slate-800">{String(m.val).padStart(2,'0')}</span>
              )}
              <span className="block text-sm font-semibold text-slate-500 mt-1 uppercase tracking-wider">{m.label}</span>
            </div>
          ))}
        </section>

        {/* Recent Pickups Table */}
        <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="flex items-center justify-between px-8 py-6 border-b border-slate-50">
            <h3 className="text-xl font-black text-slate-800">Recent Assignments</h3>
            <button onClick={() => navigate('/collector/assigned-pickups')}
              className="text-primary font-bold text-sm bg-primary/5 px-4 py-2 rounded-full hover:bg-primary/10 transition-colors">
              View All
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-48">
              <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
            </div>
          ) : pickups.length === 0 ? (
            <div className="text-center py-20 text-slate-400 font-medium">No pending pickups. Excellent work!</div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50/50">
                  {['ID','Location','Scheduled','Status',''].map(h => (
                    <th key={h} className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {pickups.map(p => (
                  <tr key={p.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="px-8 py-6 font-bold text-slate-700">#{p.id}</td>
                    <td className="px-8 py-6 text-sm text-slate-600 font-medium">{p.address}</td>
                    <td className="px-8 py-6 text-sm text-slate-500">
                      {p.pickup_date ? new Date(p.pickup_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) : 'Flexible'}
                    </td>
                    <td className="px-8 py-6">
                      <span className={`px-3 py-1 rounded-lg text-[11px] font-bold uppercase tracking-wide ${statusBadge(p.status)}`}>
                        {p.status?.replace('_',' ')}
                      </span>
                    </td>
                    <td className="px-8 py-6 text-right">
                      <button onClick={() => navigate(`/collector/assigned-pickups?id=${p.id}`)}
                        className="text-slate-300 hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">arrow_forward</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-10">
          {[
            { label: 'Assigned', icon: 'assignment', path: '/collector/assigned-pickups' },
            { label: 'Proof', icon: 'upload_file', path: '/collector/upload-proof' },
            { label: 'Reviews', icon: 'star', path: '/collector/reviews' },
            { label: 'Profile', icon: 'settings', path: '/collector/settings' },
          ].map((a, i) => (
            <button key={i} onClick={() => navigate(a.path)}
              className="flex flex-col items-center justify-center gap-4 p-8 bg-white rounded-3xl border border-slate-100 shadow-sm hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-1 transition-all">
              <div className="w-14 h-14 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-white transition-colors">
                <span className="material-symbols-outlined">{a.icon}</span>
              </div>
              <span className="text-sm font-bold text-slate-700">{a.label}</span>
            </button>
          ))}
        </div>
      </main>
    </div>
  );
}
