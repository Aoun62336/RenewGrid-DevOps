import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import UserSidebar from '../../components/layout/UserSidebar';
import { usersAPI } from '../../services/api';

export default function RewardWallet() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    usersAPI.getRewards()
      .then(res => setData(res))
      .catch(err => console.error('Failed to load rewards:', err))
      .finally(() => setLoading(false));
  }, []);

  const totalPoints = data?.points ?? 0;
  const walletBalance = data?.wallet_balance ?? 0;
  const co2Saved = data?.co2_saved_kg ?? 0;
  const rewardHistory = data?.reward_history ?? [];
  const paymentHistory = data?.payment_history ?? [];
  const totalPaymentReceived = data?.total_payment_received ?? 0;

  return (
    <DashboardLayout sidebar={UserSidebar} title="Reward Wallet">
      <div className="space-y-8 pb-12">
        {/* Page Header */}
        <div>
          <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">My Earnings</p>
          <h2 className="text-3xl font-black text-on-surface -tracking-tight">Reward Wallet</h2>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'Reward Points', value: loading ? '—' : `${totalPoints.toLocaleString()} pts`, icon: 'hotel_class', color: 'text-primary', bg: 'bg-primary-container' },
            { label: 'Wallet Balance', value: loading ? '—' : `₹${walletBalance.toFixed(2)}`, icon: 'account_balance_wallet', color: 'text-amber-600', bg: 'bg-amber-50' },
            { label: 'Payments Received', value: loading ? '—' : `₹${totalPaymentReceived.toFixed(2)}`, icon: 'payments', color: 'text-teal-600', bg: 'bg-teal-50' },
          ].map((s, i) => (
            <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant flex items-center gap-5">
              <div className={`p-3 ${s.bg} rounded-xl ${s.color}`}>
                <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>{s.icon}</span>
              </div>
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{s.label}</p>
                <p className={`text-2xl font-black mt-0.5 ${s.color}`}>{s.value}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* ── SECTION 1: Reward Payment (from Recyclers) ─────────────────────── */}
          <div>
            <h3 className="text-xl font-bold text-on-surface mb-4 flex items-center gap-2">
              <span className="w-2 h-6 bg-teal-500 rounded-full"></span>
              Reward Payment
              <span className="ml-2 text-xs font-bold text-teal-600 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">From Recyclers</span>
            </h3>
            <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
              <div className="p-5 border-b border-outline-variant bg-teal-50/50 flex items-center justify-between">
                <p className="text-xs font-bold text-teal-700 uppercase tracking-widest">Monetary Payments</p>
                <span className="text-sm font-black text-teal-700">₹{totalPaymentReceived.toFixed(2)} Total</span>
              </div>
              {loading ? (
                <div className="p-8 text-center text-slate-400 text-sm">Loading...</div>
              ) : paymentHistory.length === 0 ? (
                <div className="p-10 text-center">
                  <span className="material-symbols-outlined text-4xl text-slate-200 mb-3 block">payments</span>
                  <p className="text-slate-400 text-sm">No payments received yet.</p>
                  <p className="text-slate-300 text-xs mt-1">Recyclers will pay you once your e-waste is processed.</p>
                </div>
              ) : (
                <div className="divide-y divide-outline-variant">
                  {paymentHistory.map((p, i) => (
                    <div key={i} className="p-5 flex items-center justify-between hover:bg-surface/50 transition-all">
                      <div className="flex items-center gap-4">
                        <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-teal-50 text-teal-600 border border-teal-100 shrink-0">
                          <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>payments</span>
                        </div>
                        <div>
                          <p className="font-bold text-on-surface text-sm">{p.waste_item || `Pickup #${p.pickup_id}`}</p>
                          <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mt-0.5">
                            {p.note ? `${p.note} · ` : ''}{p.received_at ? new Date(p.received_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : ''}
                          </p>
                        </div>
                      </div>
                      <span className="text-base font-black text-teal-600 bg-teal-50 px-4 py-1.5 rounded-full border border-teal-200">+₹{p.amount.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* ── SECTION 2: Reward Points (from Admin) ─────────────────────────── */}
          <div>
            <h3 className="text-xl font-bold text-on-surface mb-4 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary rounded-full"></span>
              Reward Points
              <span className="ml-2 text-xs font-bold text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">From Admin</span>
            </h3>
            <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
              <div className="p-5 border-b border-outline-variant bg-primary/5 flex items-center justify-between">
                <p className="text-xs font-bold text-primary uppercase tracking-widest">Eco Points</p>
                <span className="text-sm font-black text-primary">{totalPoints.toLocaleString()} pts · ₹{walletBalance.toFixed(2)}</span>
              </div>
              {loading ? (
                <div className="p-8 text-center text-slate-400 text-sm">Loading...</div>
              ) : rewardHistory.length === 0 ? (
                <div className="p-10 text-center">
                  <span className="material-symbols-outlined text-4xl text-slate-200 mb-3 block">hotel_class</span>
                  <p className="text-slate-400 text-sm">No reward points yet.</p>
                  <p className="text-slate-300 text-xs mt-1">Complete pickups to earn green points from the admin.</p>
                </div>
              ) : (
                <div className="divide-y divide-outline-variant">
                  {rewardHistory.map((r, i) => (
                    <div key={i} className="p-5 flex items-center justify-between hover:bg-surface/50 transition-all">
                      <div className="flex items-center gap-4">
                        <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-primary/5 text-primary border border-primary/10 shrink-0">
                          <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>hotel_class</span>
                        </div>
                        <div>
                          <p className="font-bold text-on-surface text-sm">Pickup #{r.pickup_id}</p>
                          <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mt-0.5">
                            CO₂ saved: {r.co2_saved_kg}kg &nbsp;·&nbsp; {r.earned_at ? new Date(r.earned_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : ''}
                          </p>
                        </div>
                      </div>
                      <span className="text-base font-black text-primary bg-primary/10 px-4 py-1.5 rounded-full border border-primary/20">+{r.points} pts</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* CO2 & Eco Impact */}
            <div className="mt-6 bg-gradient-to-br from-[#326669] to-teal-900 rounded-3xl p-6 text-white relative overflow-hidden shadow-xl">
              <span className="material-symbols-outlined absolute -right-4 -bottom-4 text-[100px] text-white/5 pointer-events-none">nature_people</span>
              <div className="relative z-10">
                <p className="text-xs font-bold uppercase tracking-widest text-white/60 mb-2">Your Environmental Impact</p>
                <p className="text-3xl font-black">{co2Saved.toFixed(1)} <span className="text-lg font-bold opacity-70">kg CO₂ Saved</span></p>
                <p className="text-white/60 text-sm mt-3">≈ {Math.round(co2Saved / 20)} trees planted equivalent</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </DashboardLayout>
  );
}
