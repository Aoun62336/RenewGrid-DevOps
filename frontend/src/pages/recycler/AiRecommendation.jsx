import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import RecyclerSidebar from '../../components/layout/RecyclerSidebar';
import { recyclerAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function AiRecommendation() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPayModal, setShowPayModal] = useState(false);
  const [payAmount, setPayAmount] = useState('');
  const [payNote, setPayNote] = useState('');
  const [paymentSent, setPaymentSent] = useState(false);
  const [paying, setPaying] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      recyclerAPI.aiRecommend(id)
        .then(setData)
        .catch(err => toast.error("Error loading AI recommendation: " + err.message))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [id]);

  if (loading) {
    return (
      <div className="bg-surface min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="text-primary font-black uppercase tracking-widest text-xs">Neural Assessment Active...</p>
        </div>
      </div>
    );
  }

  if (!id) {
    return (
      <div className="bg-surface text-on-surface min-h-screen relative">
        <RecyclerSidebar />
        <main className="ml-64 pt-24 pb-12 px-8 min-h-screen">
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-8 text-center">
            <span className="material-symbols-outlined text-amber-600 text-5xl mb-4">inventory_2</span>
            <p className="text-amber-800 font-bold text-lg mb-4">No waste item selected for assessment.</p>
            <button onClick={() => navigate('/collected-waste-listing')} className="px-6 py-3 bg-amber-600 text-white font-bold rounded-xl shadow-lg">Go to Inventory</button>
          </div>
        </main>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-surface text-on-surface min-h-screen relative">
      <RecyclerSidebar />

      <header className="fixed top-0 right-0 w-[calc(100%-16rem)] h-16 bg-white/85 backdrop-blur-md shadow-sm z-40 flex items-center justify-between px-8">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-['Inter'] font-extrabold text-[#326669]">AI Decision Intelligence</h1>
        </div>
      </header>

      <main className="ml-64 pt-24 pb-12 px-8 min-h-screen">
        <section className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary text-xs font-black rounded-full mb-3 uppercase tracking-widest border border-primary/20">
              <span className="material-symbols-outlined text-xs">auto_awesome</span> Neural Engine v2.4
            </div>
            <h2 className="text-4xl font-black tracking-tighter text-on-surface mb-2">Automated Resource Assessment</h2>
            <p className="text-on-surface-variant text-lg font-medium leading-relaxed">
              Assessment for <span className="font-black text-primary">Upload #{id}</span>. Category: <span className="font-black text-primary uppercase text-sm tracking-widest">{data.category || 'N/A'}</span>
            </p>
          </div>
          <div className="flex gap-3 flex-wrap">
            <button onClick={() => navigate(`/processing-decision/${id}`)} className="px-8 py-4 bg-primary text-white font-black rounded-2xl shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-3">
              <span className="material-symbols-outlined">rocket_launch</span> Implement Recommendation
            </button>
            {paymentSent ? (
              <div className="px-6 py-4 bg-teal-100 text-teal-700 font-black rounded-2xl flex items-center gap-2">
                <span className="material-symbols-outlined">check_circle</span> Payment Sent
              </div>
            ) : (
              <button
                onClick={() => { setPayAmount(data.recommended_payment ? String(data.recommended_payment) : ''); setShowPayModal(true); }}
                className="px-8 py-4 bg-teal-600 text-white font-black rounded-2xl shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-3"
              >
                <span className="material-symbols-outlined">payments</span> Send Payment to User
              </button>
            )}
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-10">
          {/* Main Card */}
          <div className="lg:col-span-8 bg-white rounded-[2.5rem] shadow-sm border border-outline-variant overflow-hidden flex flex-col md:flex-row relative">
            <div className="absolute top-8 right-8">
                <div className="flex flex-col items-end">
                    <span className="text-[10px] font-black text-primary mb-1 uppercase tracking-widest">Confidence</span>
                    <div className="flex items-center gap-2">
                        <span className="text-4xl font-black text-primary">{data.confidence || 94}%</span>
                        <div className="w-10 h-1 h-full bg-primary/20 rounded-full overflow-hidden">
                            <div className="h-full bg-primary" style={{ width: `${data.confidence || 94}%` }}></div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-10 md:w-5/12 flex flex-col justify-center border-b md:border-b-0 md:border-r border-outline-variant bg-surface">
              <div className="w-20 h-20 bg-primary rounded-3xl flex items-center justify-center text-white mb-8 shadow-2xl shadow-primary/30">
                <span className="material-symbols-outlined text-5xl">psychology</span>
              </div>
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Primary Recommendation</h3>
              <p className="text-4xl font-black text-on-surface leading-tight mb-4">{data.recommended_action}</p>

              {/* ── AI PRICE DUALITY DISPLAY ── */}
              <div className="mt-4 pt-5 border-t border-outline-variant space-y-3">
                {data.user_estimated_price && (
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">User's AI Estimate</p>
                    <p className="text-xl font-black text-slate-500 line-through decoration-2">₹{data.user_estimated_price.toLocaleString()}</p>
                  </div>
                )}
                <div className="p-3 bg-primary/5 rounded-xl border border-primary/20">
                  <p className="text-[9px] font-black text-primary uppercase tracking-widest mb-0.5">Recycler Recommended Payment</p>
                  <p className="text-2xl font-black text-primary">
                    {data.recommended_payment ? `₹${data.recommended_payment.toLocaleString()}` : '—'}
                  </p>
                  {data.user_estimated_price && data.recommended_payment && (
                    <p className="text-[10px] text-primary/60 mt-0.5">
                      {data.recommended_payment > data.user_estimated_price ? '+' : ''}
                      {(((data.recommended_payment - data.user_estimated_price) / data.user_estimated_price) * 100).toFixed(1)}% vs user estimate
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="p-10 flex-1 flex flex-col justify-between">
              <div>
                  <h4 className="font-black text-on-surface text-lg mb-6 flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary">fact_check</span>
                      Core Reasoning
                  </h4>
                  <p className="text-slate-600 font-medium leading-relaxed text-sm mb-8">{data.reasoning || "Component structural integrity allows for high-yield material recovery or potential refurbishment based on detected electronic signatures."}</p>
                  
                  <div className="space-y-4">
                    {[
                        { icon: 'verified', title: 'Component Vitality', desc: 'Circuitry health estimated at 88%' },
                        { icon: 'monitoring', title: 'Market Demand', desc: 'High demand for recovered rare-earth magnets' },
                        { icon: 'eco', title: 'Carbon Credit Potential', desc: 'Estimated 2.4kg CO2 savings' }
                    ].map((item, idx) => (
                        <div key={idx} className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center text-primary shrink-0">
                                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                            </div>
                            <div>
                                <p className="text-sm font-bold text-on-surface leading-none mb-1">{item.title}</p>
                                <p className="text-xs text-slate-400">{item.desc}</p>
                            </div>
                        </div>
                    ))}
                  </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 bg-slate-900 rounded-[2.5rem] p-8 text-white shadow-xl relative overflow-hidden flex flex-col">
            <div className="absolute -right-12 -top-12 opacity-10">
              <span className="material-symbols-outlined text-[15rem]">diamond</span>
            </div>
            
            <div className="relative z-10">
              <h3 className="font-black text-2xl tracking-tight mb-8 flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary-light">layers</span>
                  Material Yield
              </h3>
              <div className="space-y-8">
                {data.materials?.map((m, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-xs font-black mb-3 uppercase tracking-widest">
                      <span className="text-white/60">{m.name}</span>
                      <span className="text-primary-light">{m.yield}</span>
                    </div>
                    <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-primary-light to-teal-400 rounded-full" style={{ width: `${m.pct}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-12 p-6 bg-white/5 rounded-3xl border border-white/10">
                  <p className="text-xs font-bold text-white/50 mb-1 uppercase tracking-widest">Weight Assessment</p>
                  <p className="text-2xl font-black">{data.weight || 'N/A'} kg</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between mb-8">
            <h3 className="text-2xl font-black text-on-surface flex items-center gap-3">
                <span className="material-symbols-outlined text-primary">inventory</span> 
                Component Breakdown
            </h3>
            <span className="px-4 py-1.5 bg-surface rounded-full text-[10px] font-black uppercase tracking-widest border border-outline-variant">Detected Parts: {data.components?.length || 0}</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {data.components?.map((c, i) => (
            <div key={i} className="bg-white p-6 rounded-[2rem] border border-outline-variant hover:shadow-2xl hover:-translate-y-1 transition-all group cursor-pointer">
              <div className="flex justify-between items-start mb-6">
                <div className="w-14 h-14 bg-surface rounded-2xl flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-all shadow-sm">
                  <span className="material-symbols-outlined text-2xl">{c.icon}</span>
                </div>
                <span className={`px-3 py-1 text-[9px] font-black rounded-full uppercase tracking-widest ${c.action === 'Refurbish' ? 'bg-primary text-white' : 'bg-slate-100 text-slate-600'}`}>{c.action}</span>
              </div>
              <h4 className="font-black text-on-surface text-lg mb-1">{c.name}</h4>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-6">S/N: {c.serial}</p>
              
              <div className="flex items-center justify-between pt-4 border-t border-outline-variant">
                <div className={`flex items-center gap-1.5 text-xs font-black ${c.health_icon === 'warning' ? 'text-error' : 'text-teal-600'}`}>
                  <span className="material-symbols-outlined text-[16px]">{c.health_icon}</span> {c.health}
                </div>
                <div className="text-[10px] font-black text-slate-400 uppercase">{c.value}</div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* ── Send Payment Modal ── */}
      {showPayModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-[2rem] p-8 w-full max-w-md shadow-2xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-teal-100 rounded-2xl flex items-center justify-center text-teal-600">
                <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>payments</span>
              </div>
              <div>
                <h3 className="text-xl font-black text-on-surface">Send Payment</h3>
                <p className="text-xs text-slate-400">Pickup #{id} — Amount will appear in user's Reward Wallet</p>
              </div>
            </div>

            {data.recommended_payment && (
              <div className="mb-5 p-4 bg-teal-50 rounded-xl border border-teal-200">
                <p className="text-xs font-bold text-teal-700 uppercase tracking-widest">AI Recommended Amount</p>
                <p className="text-2xl font-black text-teal-800">₹{data.recommended_payment.toLocaleString()}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-widest">Payment Amount (₹)</label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  value={payAmount}
                  onChange={e => setPayAmount(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-teal-100 bg-surface-bright focus:bg-white focus:border-teal-500 transition-all text-lg font-black"
                  placeholder="e.g. 2500.00"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-widest">Note (Optional)</label>
                <input
                  type="text"
                  value={payNote}
                  onChange={e => setPayNote(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-slate-100 bg-surface-bright focus:bg-white focus:border-teal-500 transition-all text-sm font-medium"
                  placeholder="e.g. Payment for laptop recycling"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() => setShowPayModal(false)}
                className="flex-1 py-3 bg-slate-100 text-slate-600 rounded-xl font-bold hover:bg-slate-200 transition-all"
              >Cancel</button>
              <button
                type="button"
                disabled={paying || !payAmount || parseFloat(payAmount) <= 0}
                onClick={async () => {
                  setPaying(true);
                  try {
                    await recyclerAPI.sendPayment(id, { amount: parseFloat(payAmount), note: payNote || null });
                    toast.success(`Payment of ₹${parseFloat(payAmount).toLocaleString()} sent successfully!`);
                    setPaymentSent(true);
                    setShowPayModal(false);
                  } catch (err) {
                    toast.error(err.message || 'Failed to send payment');
                  } finally { setPaying(false); }
                }}
                className="flex-1 py-3 bg-teal-600 text-white rounded-xl font-bold shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {paying ? <span className="animate-spin material-symbols-outlined text-sm">refresh</span> : <span className="material-symbols-outlined">payments</span>}
                {paying ? 'Sending...' : `Send ₹${parseFloat(payAmount || 0).toLocaleString()}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
