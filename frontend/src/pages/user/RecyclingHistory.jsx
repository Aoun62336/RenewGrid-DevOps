import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import UserSidebar from '../../components/layout/UserSidebar';
import { pickupAPI } from '../../services/api';

const ITEMS_PER_PAGE = 10;

export default function RecyclingHistory() {
  const [history, setHistory] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const loadHistory = useCallback(async (page = 1, fd = '', td = '') => {
    setLoading(true);
    try {
      const params = { status: 'COMPLETED', page, page_size: ITEMS_PER_PAGE };
      if (fd) params.from_date = fd;
      if (td) params.to_date = td;
      const data = await pickupAPI.myRequests(params);
      setHistory(data.items || data || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadHistory(1); }, [loadHistory]);

  const handleFilter = () => {
    setCurrentPage(1);
    loadHistory(1, fromDate, toDate);
  };

  const handleReset = () => {
    setSearch('');
    setFromDate('');
    setToDate('');
    setCurrentPage(1);
    loadHistory(1);
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  // Client-side search filter (on loaded page)
  const filtered = search
    ? history.filter(h =>
        String(h.id).includes(search) ||
        (h.address || '').toLowerCase().includes(search.toLowerCase())
      )
    : history;

  return (
    <DashboardLayout sidebar={UserSidebar} title="Recycling History">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Activity Log</p>
          <h2 className="text-3xl font-black text-on-surface -tracking-tight">Recycling History</h2>
        </div>
        <button className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-bold flex items-center gap-2">
          <span className="material-symbols-outlined text-sm">download</span> Export
        </button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {[
          { label: 'Pickups Completed', value: total, icon: 'task_alt' },
          { label: 'CO₂ Saved (est.)', value: `${(total * 8.2).toFixed(1)} kg`, icon: 'eco' },
          { label: 'Points Earned (est.)', value: total * 150, icon: 'stars' },
        ].map((s, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant hover:shadow-lg transition-all">
            <div className="w-12 h-12 bg-primary-container rounded-xl flex items-center justify-center mb-4 text-primary">
              <span className="material-symbols-outlined">{s.icon}</span>
            </div>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{s.label}</p>
            <p className="text-2xl font-black text-on-surface mt-1">{loading ? '—' : s.value}</p>
          </div>
        ))}
      </div>

      {/* Filter Section */}
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-outline-variant mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Search</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">search</span>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by ID or address..."
                className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              />
            </div>
          </div>
          <div className="min-w-[150px]">
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">From Date</label>
            <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
          </div>
          <div className="min-w-[150px]">
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">To Date</label>
            <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
          </div>
          <div className="flex gap-2">
            <button onClick={handleFilter}
              className="px-5 py-2.5 bg-primary text-white rounded-xl text-sm font-bold flex items-center gap-2 hover:bg-primary/90 transition-all shadow-sm">
              <span className="material-symbols-outlined text-sm">filter_list</span> Filter
            </button>
            <button onClick={handleReset}
              className="px-5 py-2.5 border border-outline-variant bg-white rounded-xl text-sm font-bold text-slate-600 flex items-center gap-2 hover:bg-surface transition-all">
              <span className="material-symbols-outlined text-sm">close</span> Reset
            </button>
          </div>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-surface text-primary text-[10px] uppercase tracking-widest font-black">
              <tr>
                <th className="px-6 py-4">Request ID</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Address</th>
                <th className="px-6 py-4">Weight (kg)</th>
                <th className="px-6 py-4">Valuation</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-400 text-sm">Loading...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-400 text-sm">No completed pickups found.</td></tr>
              ) : filtered.map((h, i) => (
                <tr key={i} className="hover:bg-surface/50 transition-colors cursor-pointer">
                  <td className="px-6 py-5 font-bold text-on-surface">#{h.id}</td>
                  <td className="px-6 py-5 text-sm text-slate-500">
                    {h.pickup_date ? new Date(h.pickup_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : h.created_at ? new Date(h.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}
                  </td>
                  <td className="px-6 py-5 text-sm text-on-surface">{h.address || '—'}</td>
                  <td className="px-6 py-5 text-sm text-slate-600">{h.final_collected_weight || h.waste?.estimated_weight ? `${h.final_collected_weight || h.waste?.estimated_weight} kg` : '—'}</td>
                  <td className="px-6 py-5 text-sm font-bold text-primary">
                    {h.final_price || h.waste?.estimated_price 
                      ? `₹${(h.final_price || h.waste.estimated_price).toLocaleString()}` 
                      : <span className="text-slate-400 italic font-normal text-[10px]">Pending AI Assessment</span>}
                  </td>
                  <td className="px-6 py-5">
                    <span className="px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-[10px] font-black uppercase">{h.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 flex items-center justify-between border-t border-outline-variant">
            <p className="text-xs text-slate-500">Page {currentPage} of {totalPages} ({total} records)</p>
            <div className="flex items-center gap-1">
              <button onClick={() => { setCurrentPage(p => Math.max(1, p - 1)); loadHistory(currentPage - 1, fromDate, toDate); }} disabled={currentPage === 1} className="w-8 h-8 flex items-center justify-center rounded-lg border border-outline-variant hover:bg-surface transition-all disabled:opacity-40">
                <span className="material-symbols-outlined text-sm">chevron_left</span>
              </button>
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
                <button key={p} onClick={() => { setCurrentPage(p); loadHistory(p, fromDate, toDate); }} className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-bold transition-all ${p === currentPage ? 'bg-primary text-white' : 'hover:bg-surface border border-outline-variant'}`}>{p}</button>
              ))}
              <button onClick={() => { setCurrentPage(p => Math.min(totalPages, p + 1)); loadHistory(currentPage + 1, fromDate, toDate); }} disabled={currentPage === totalPages} className="w-8 h-8 flex items-center justify-center rounded-lg border border-outline-variant hover:bg-surface transition-all disabled:opacity-40">
                <span className="material-symbols-outlined text-sm">chevron_right</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
