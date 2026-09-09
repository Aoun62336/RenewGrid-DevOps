import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RecyclerSidebar from '../../components/layout/RecyclerSidebar';
import { recyclerAPI } from '../../services/api';

export default function InventoryManagement() {
  const navigate = useNavigate();
  const [inventory, setInventory] = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState('');

  const PAGE_SIZE = 10;

  useEffect(() => {
    const fetchInventory = async () => {
      setLoading(true);
      try {
        const res = await recyclerAPI.inventory(page, PAGE_SIZE);
        setInventory(res.items || []);
        setTotal(res.total || 0);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchInventory();
  }, [page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const statusBadge = (status) => {
    const map = {
      recycled:   { bg: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500', label: 'Recycled'   },
      completed:  { bg: 'bg-teal-100 text-teal-700',       dot: 'bg-teal-500',    label: 'Completed'  },
      in_stock:   { bg: 'bg-blue-100 text-blue-700',       dot: 'bg-blue-500',    label: 'In Stock'   },
      processing: { bg: 'bg-amber-100 text-amber-700',     dot: 'bg-amber-500',   label: 'Processing' },
    };
    const s = map[status?.toLowerCase()] ?? { bg: 'bg-slate-100 text-slate-600', dot: 'bg-slate-400', label: status };
    return (
      <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold w-fit ${s.bg}`}>
        <span className={`w-2 h-2 rounded-full ${s.dot}`} />
        {s.label}
      </div>
    );
  };

  return (
    <div className="bg-surface text-on-surface min-h-screen relative">
      <RecyclerSidebar />

      <main className="ml-64 min-h-screen">
        <header className="fixed top-0 right-0 w-[calc(100%-16rem)] h-16 bg-white/85 backdrop-blur-md shadow-sm z-40 flex items-center justify-between px-8">
          <h1 className="text-xl font-['Inter'] font-extrabold text-[#326669]">Inventory Management</h1>
          <button className="text-slate-500 hover:text-[#326669] transition-colors relative p-2 rounded-full hover:bg-primary/10">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
          </button>
        </header>

        <div className="pt-24 pb-12 px-8 space-y-8">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="col-span-1 md:col-span-2 bg-primary rounded-2xl p-6 shadow-xl relative overflow-hidden flex flex-col justify-between">
              <div className="z-10">
                <h3 className="text-white/80 font-medium text-sm uppercase tracking-widest">Total Processed Items</h3>
                <p className="text-white font-black text-4xl mt-2">
                  {total} <span className="text-lg font-normal opacity-70">items</span>
                </p>
              </div>
              <div className="z-10 mt-4">
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs text-white font-bold">Live from backend</span>
              </div>
              <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
            </div>
            <div className="bg-surface-bright rounded-2xl p-6 shadow-md border border-outline-variant flex flex-col justify-between">
              <div>
                <h3 className="text-on-surface-variant font-medium text-sm uppercase tracking-widest">Current Page</h3>
                <p className="text-primary font-black text-4xl mt-2">{page}/{totalPages || 1}</p>
              </div>
              <p className="text-xs text-on-surface-variant mt-2 font-medium">Showing {PAGE_SIZE} items per page</p>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl text-sm font-semibold">
              {error}
            </div>
          )}

          {/* Inventory Table */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-black tracking-tight text-primary">Processed Inventory</h2>
                <button
                  onClick={() => navigate('/recycler-dashboard')}
                  className="bg-white border-2 border-primary text-primary px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-primary/5 transition-all"
                >
                  Back to Dashboard
                </button>
              </div>

              <div className="bg-surface-bright rounded-2xl shadow-sm border border-outline-variant overflow-hidden">
                {loading ? (
                  <div className="flex items-center justify-center h-48">
                    <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
                  </div>
                ) : (
                  <table className="w-full text-left border-collapse">
                    <thead className="bg-surface-container">
                      <tr>
                        <th className="px-6 py-4 text-xs font-black text-primary uppercase tracking-widest">Pickup ID</th>
                        <th className="px-6 py-4 text-xs font-black text-primary uppercase tracking-widest">Description</th>
                        <th className="px-6 py-4 text-xs font-black text-primary uppercase tracking-widest">Weight</th>
                        <th className="px-6 py-4 text-xs font-black text-primary uppercase tracking-widest">Status</th>
                        <th className="px-6 py-4 text-xs font-black text-primary uppercase tracking-widest">Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant">
                      {inventory.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="px-6 py-12 text-center text-slate-400 text-sm">
                            No inventory items yet. Process collected waste to see items here.
                          </td>
                        </tr>
                      ) : inventory.map(item => (
                        <tr key={item.id} className="hover:bg-surface transition-colors">
                          <td className="px-6 py-5">
                            <span className="font-bold text-on-surface">#RG-{item.pickup_id}</span>
                          </td>
                          <td className="px-6 py-5 text-sm text-slate-600">
                            {item.item_description || 'E-Waste Item'}
                          </td>
                          <td className="px-6 py-5 font-medium">
                            {item.weight_kg != null ? `${item.weight_kg} kg` : '—'}
                          </td>
                          <td className="px-6 py-5">
                            {statusBadge(item.status)}
                          </td>
                          <td className="px-6 py-5 text-sm text-slate-400">
                            {new Date(item.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {/* Pagination */}
                <div className="px-6 py-4 bg-surface flex items-center justify-between text-xs font-bold text-on-surface-variant uppercase tracking-widest">
                  <span>Showing {Math.min(inventory.length, PAGE_SIZE)} of {total} items</span>
                  <div className="flex gap-2">
                    <button
                      disabled={page === 1}
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      className="w-8 h-8 rounded-lg flex items-center justify-center border border-outline-variant hover:bg-white transition-all disabled:opacity-40"
                    >
                      <span className="material-symbols-outlined text-sm">chevron_left</span>
                    </button>
                    <button
                      disabled={page >= totalPages}
                      onClick={() => setPage(p => p + 1)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center border border-outline-variant hover:bg-white transition-all disabled:opacity-40"
                    >
                      <span className="material-symbols-outlined text-sm">chevron_right</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Insights Panel */}
            <div className="lg:col-span-1">
              <div className="bg-surface-bright rounded-2xl p-8 shadow-2xl border border-outline-variant sticky top-24">
                <div className="mb-6">
                  <h2 className="text-xl font-black tracking-tight text-primary">Quick Stats</h2>
                  <p className="text-sm text-on-surface-variant mt-1">Based on your processed inventory.</p>
                </div>
                <div className="space-y-4">
                  {[
                    { label: 'Total Items',    val: total,   icon: 'inventory_2'  },
                    { label: 'Current Page',   val: `${page} / ${totalPages || 1}`, icon: 'pages' },
                    { label: 'Items on Page',  val: inventory.length, icon: 'list_alt' },
                  ].map((stat, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-surface rounded-xl">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary">{stat.icon}</span>
                        <span className="text-sm font-bold text-on-surface">{stat.label}</span>
                      </div>
                      <span className="text-sm font-black text-primary">{stat.val}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-8 p-4 bg-primary-container rounded-xl border border-outline-variant">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-primary">info</span>
                    <p className="text-xs font-medium text-primary">
                      All inventory is auto-populated when you complete the recycling process for a collected item.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Insights Banner */}
          <div className="bg-surface-container rounded-3xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 border border-outline-variant">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center">
                <span className="material-symbols-outlined text-3xl text-primary">analytics</span>
              </div>
              <div>
                <h3 className="text-xl font-black text-primary">Inventory Insights</h3>
                <p className="text-on-surface-variant text-sm font-medium">
                  {total > 0
                    ? `${total} items processed through your facility.`
                    : 'Start processing collected waste to see inventory insights.'}
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/processing-history')}
              className="bg-primary text-white px-8 py-3 rounded-xl font-bold text-sm shadow-lg hover:shadow-xl transition-all"
            >
              View Processing History
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
