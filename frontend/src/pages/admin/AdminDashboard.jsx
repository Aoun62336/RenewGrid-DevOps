import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminSidebar from '../../components/layout/AdminSidebar';
import { adminAPI } from '../../services/api';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [users,    setUsers]    = useState([]);
  const [pickups,  setPickups]  = useState([]);
  const [reports,  setReports]  = useState(null);
  const [revenue,  setRevenue]  = useState(null);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ov, ur, pr, rp, rev] = await Promise.all([
          adminAPI.overview(),
          adminAPI.users({ page: 1, page_size: 5 }),
          adminAPI.pickups({ page: 1, page_size: 5 }),
          adminAPI.reports(),
          adminAPI.getRevenue(),
        ]);
        setOverview(ov);
        setUsers(ur.items  || []);
        setPickups(pr.items || []);
        setReports(rp);
        setRevenue(rev);
      } catch (err) { console.error('Dashboard load error:', err); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const Skeleton = ({ w = 'w-20', h = 'h-9' }) => (
    <div className={`${h} ${w} bg-slate-200 animate-pulse rounded`} />
  );

  const statusBadge = (s) => ({
    PENDING:     'bg-amber-100 text-amber-700',
    ASSIGNED:    'bg-blue-100 text-blue-700',
    IN_PROGRESS: 'bg-primary text-white',
    COLLECTED:   'bg-teal-100 text-teal-700',
    PROCESSING:  'bg-purple-100 text-purple-700',
    COMPLETED:   'bg-green-100 text-green-700',
    CANCELLED:   'bg-red-100 text-red-600',
  }[s] ?? 'bg-slate-100 text-slate-600');

  const roleBadge = (r) => ({
    admin:     'bg-red-100 text-red-700',
    collector: 'bg-blue-100 text-blue-700',
    recycler:  'bg-purple-100 text-purple-700',
    user:      'bg-teal-100 text-teal-700',
  }[r] ?? 'bg-slate-100 text-slate-600');

  const metricCards = [
    { label: 'Total Users',       val: overview ? (overview.total_users || 0) : undefined,              icon: 'group',          color: 'text-blue-500'   },
    { label: 'Total Pickups',     val: overview ? (overview.total_pickups || 0) : undefined,            icon: 'local_shipping', color: 'text-primary'    },
    { label: 'Completed Pickups', val: overview ? (overview.completed_pickups || 0) : undefined,        icon: 'task_alt',       color: 'text-green-500'  },
    { label: 'Total Waste',       val: overview ? (overview.total_waste_uploaded || 0) : undefined,     icon: 'inventory_2',    color: 'text-amber-500'  },
    { label: 'Total Revenue',     val: revenue ? `₹${revenue.total_revenue || 0}` : undefined, icon: 'payments',       color: 'text-indigo-500' },
    { label: 'This Month Rev.',   val: revenue ? `₹${revenue.this_month_revenue || 0}` : undefined, icon: 'calendar_today', color: 'text-rose-500' },
    { label: 'Waste Collected kg',val: reports ? (reports.total_waste_collected_kg || 0) : undefined,  icon: 'scale',          color: 'text-primary'    },
    { label: 'Pending Pickups',   val: reports ? (reports.pickups_by_status?.PENDING || 0) : undefined, icon: 'pending_actions', color: 'text-orange-500' },
  ];

  return (
    <div className="bg-surface text-on-surface min-h-screen relative">
      <AdminSidebar />

      <header className="fixed top-0 right-0 w-[calc(100%-16rem)] h-16 bg-white/85 backdrop-blur-md shadow-sm z-40 flex items-center justify-between px-8">
        <h1 className="text-xl font-extrabold text-[#326669]">Admin Dashboard</h1>
        <button className="text-slate-500 hover:text-[#326669] relative p-2 rounded-full hover:bg-primary/10">
          <span className="material-symbols-outlined">notifications</span>
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
        </button>
      </header>

      <main className="ml-64 pt-24 px-8 pb-12 min-h-screen">
        <div className="mb-10">
          <h2 className="text-4xl font-black tracking-tighter text-on-surface leading-none">System Dashboard</h2>
          <p className="text-on-surface-variant mt-2 font-medium">Real-time platform metrics for RenewGrid operations.</p>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
          {metricCards.map((m, i) => (
            <div key={i} className="bg-surface-bright rounded-2xl p-6 shadow-sm ring-1 ring-outline-variant hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-secondary-fixed rounded-xl">
                  <span className={`material-symbols-outlined ${m.color}`}>{m.icon}</span>
                </div>
              </div>
              <p className="text-on-surface-variant text-sm font-semibold tracking-wide uppercase">{m.label}</p>
              {loading || m.val === undefined
                ? <Skeleton />
                : <h3 className="text-3xl font-black text-on-surface mt-1">{m.val ?? 0}</h3>}
            </div>
          ))}
        </div>

        {/* Status breakdown */}
        {reports?.pickups_by_status && (
          <div className="bg-white rounded-3xl shadow-sm border border-outline-variant p-8 mb-10">
            <h3 className="text-lg font-black text-on-surface mb-6">Pickups by Status</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(reports.pickups_by_status).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between p-4 bg-surface rounded-xl">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${statusBadge(status)}`}>
                    {status.replace('_', ' ')}
                  </span>
                  <span className="text-xl font-black text-on-surface">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Recent Users */}
          <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
            <div className="flex items-center justify-between px-8 py-6 border-b border-outline-variant">
              <h3 className="text-lg font-black text-on-surface">Recent Users</h3>
              <button onClick={() => navigate('/admin/user-management')}
                className="text-primary font-bold text-sm hover:underline flex items-center gap-1">
                Manage All <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
            {loading ? (
              <div className="flex items-center justify-center h-40">
                <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
              </div>
            ) : (
              <div className="divide-y divide-outline-variant">
                {users.map(u => (
                  <div key={u.id} className="flex items-center justify-between px-8 py-4 hover:bg-surface transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-primary-container rounded-xl flex items-center justify-center text-primary text-sm font-black">
                        {u.full_name?.[0]?.toUpperCase()}
                      </div>
                      <div>
                        <p className="font-bold text-sm text-on-surface">{u.full_name}</p>
                        <p className="text-xs text-slate-400">{u.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${roleBadge(u.role)}`}>
                        {u.role}
                      </span>
                      <span className={`w-2 h-2 rounded-full ${u.is_active ? 'bg-green-500' : 'bg-red-400'}`} title={u.is_active ? 'Active' : 'Blocked'} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Pickups */}
          <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
            <div className="flex items-center justify-between px-8 py-6 border-b border-outline-variant">
              <h3 className="text-lg font-black text-on-surface">Recent Pickups</h3>
              <button onClick={() => navigate('/admin/waste-uploads')}
                className="text-primary font-bold text-sm hover:underline flex items-center gap-1">
                View All <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
            {loading ? (
              <div className="flex items-center justify-center h-40">
                <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
              </div>
            ) : (
              <div className="divide-y divide-outline-variant">
                {pickups.map(p => (
                  <div key={p.id} className="flex items-center justify-between px-8 py-4 hover:bg-surface transition-colors">
                    <div>
                      <p className="font-bold text-sm text-on-surface">#RG-{p.id}</p>
                      <p className="text-xs text-slate-400 truncate max-w-[200px]">{p.address}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${statusBadge(p.status)}`}>
                      {p.status?.replace('_', ' ')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Admin Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
          {[
            { label: 'User Management',    icon: 'manage_accounts', path: '/admin/user-management'  },
            { label: 'All Pickups',        icon: 'local_shipping',  path: '/admin/waste-uploads'      },
            { label: 'Assign Collectors',  icon: 'assignment_ind',  path: '/admin/waste-assignment' },
            { label: 'Reports',            icon: 'analytics',       path: '/admin/reports'          },
          ].map((a, i) => (
            <button key={i} onClick={() => navigate(a.path)}
              className="flex flex-col items-center gap-3 p-6 bg-white rounded-2xl border border-outline-variant hover:border-primary hover:shadow-lg transition-all group">
              <div className="w-12 h-12 bg-primary-container rounded-xl flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-all">
                <span className="material-symbols-outlined">{a.icon}</span>
              </div>
              <span className="text-sm font-bold text-on-surface text-center">{a.label}</span>
            </button>
          ))}
        </div>
      </main>
    </div>
  );
}
