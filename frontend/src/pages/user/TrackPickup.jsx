import React, { useState, useEffect } from 'react';
import { useSearchParams, useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/layout/DashboardLayout';
import UserSidebar from '../../components/layout/UserSidebar';
import { pickupAPI } from '../../services/api';

const STATUS_STEPS = [
  { key: 'PENDING',     label: 'Request Submitted',     icon: 'task_alt'       },
  { key: 'ASSIGNED',   label: 'Collector Assigned',     icon: 'person_add'     },
  { key: 'IN_PROGRESS',label: 'En Route to Location',   icon: 'local_shipping' },
  { key: 'COLLECTED',  label: 'Pickup Completed',       icon: 'check_circle'   },
  { key: 'PROCESSING', label: 'Processing at Recycler', icon: 'recycling'      },
  { key: 'COMPLETED',  label: 'Lifecycle Complete',     icon: 'verified'       },
];

export default function TrackPickup() {
  const { id: paramId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const pickupId = paramId || searchParams.get('id');

  const [tracking,  setTracking]  = useState(null);
  const [pickups,   setPickups]   = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState('');
  const [showPhoneModal, setShowPhoneModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);

  /* ── load pickups list + selected tracking ── */
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Load the user's pickup list for the sidebar panel
        const listRes = await pickupAPI.myRequests(1, 10);
        setPickups(listRes.items || []);

        // If a specific pickup ID is supplied, load tracking
        const targetId = pickupId || listRes.items?.[0]?.id;
        if (targetId) {
          const track = await pickupAPI.track(targetId);
          setTracking(track);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [pickupId]);

  /* ── compute current step index ── */
  const currentStepIdx = tracking
    ? STATUS_STEPS.findIndex(s => s.key === tracking.current_status)
    : -1;

  /* ── active pickup details ── */
  const activePickup = pickups.find(p => String(p.id) === String(tracking?.pickup_id)) || pickups[0];

  return (
    <DashboardLayout sidebar={UserSidebar} title="Track Pickup Status">
      <div className="mb-8">
        <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Live Tracking</p>
        <h2 className="text-3xl font-black text-on-surface -tracking-tight">Track Pickup Status</h2>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl text-sm font-semibold">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* ── Main tracking panel ── */}
          <div className="lg:col-span-8 space-y-6">
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-outline-variant">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-bold text-on-surface">
                    Request #{tracking?.pickup_id ?? activePickup?.id ?? '—'}
                  </h3>
                  <p className="text-sm text-slate-500">
                    {activePickup?.waste?.title ?? 'E-Waste Pickup'}
                    {activePickup?.final_collected_weight
                      ? ` — ${activePickup.final_collected_weight} kg`
                      : ''}
                  </p>
                </div>
                <span className="px-4 py-2 bg-primary text-white rounded-full text-xs font-black uppercase">
                  {tracking?.current_status?.replace('_', ' ') ?? 'Unknown'}
                </span>
              </div>

              {/* ── Progress Timeline ── */}
              <div className="relative pl-8 space-y-8">
                {STATUS_STEPS.map((step, i) => {
                  const histEntry = tracking?.timeline?.find(t => t.status === step.key);
                  const done = i <= currentStepIdx;
                  return (
                    <div key={step.key} className="relative flex items-start gap-4">
                      <div className={`absolute -left-8 top-0 w-8 h-8 rounded-full flex items-center justify-center z-10 ${
                        done ? 'bg-primary text-white' : 'bg-slate-100 text-slate-400'
                      }`}>
                        <span className="material-symbols-outlined text-sm">{step.icon}</span>
                      </div>
                      {i < STATUS_STEPS.length - 1 && (
                        <div className={`absolute -left-4 top-8 w-0.5 h-8 ${done ? 'bg-primary' : 'bg-slate-200'}`} />
                      )}
                      <div className="ml-4">
                        <p className={`text-sm font-bold ${done ? 'text-on-surface' : 'text-slate-400'}`}>
                          {step.label}
                        </p>
                        <p className="text-xs text-slate-400 mt-1">
                          {histEntry
                            ? new Date(histEntry.changed_at).toLocaleString()
                            : done ? 'Completed' : 'Pending'}
                        </p>
                        {histEntry?.note && (
                          <p className="text-xs text-slate-500 italic mt-0.5">{histEntry.note}</p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ── Collector Info ── */}
            {activePickup?.collector_id && (
              <div className="bg-white rounded-3xl p-6 shadow-sm border border-outline-variant">
                <h3 className="text-lg font-bold text-on-surface mb-4">Assigned Collector</h3>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-primary-container rounded-2xl flex items-center justify-center text-primary">
                      <span className="material-symbols-outlined text-2xl">person</span>
                    </div>
                    <div>
                      <p className="font-bold text-on-surface">Collector #{activePickup.collector_id}</p>
                      <p className="text-sm text-slate-500">ID: {activePickup.collector_id}</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowPhoneModal(true)}
                      className="w-12 h-12 bg-primary-container rounded-xl flex items-center justify-center text-primary hover:bg-primary hover:text-white transition-all"
                      title="Call Collector"
                    >
                      <span className="material-symbols-outlined">call</span>
                    </button>
                    <button
                      onClick={() => setShowEmailModal(true)}
                      className="w-12 h-12 bg-primary-container rounded-xl flex items-center justify-center text-primary hover:bg-primary hover:text-white transition-all"
                      title="Message Collector"
                    >
                      <span className="material-symbols-outlined">chat</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ── Sidebar ── */}
          <div className="lg:col-span-4 space-y-6">
            {/* Other requests */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant">
              <h3 className="text-lg font-bold text-on-surface mb-4">My Pickup Requests</h3>
              <div className="space-y-3">
                {pickups.slice(0, 5).map(req => (
                  <div
                    key={req.id}
                    onClick={() => navigate(`/pickup/${req.id}/track`)}
                    className={`block p-4 rounded-xl transition-all cursor-pointer ${
                      String(req.id) === String(tracking?.pickup_id)
                        ? 'bg-primary-container border border-primary'
                        : 'bg-surface hover:bg-primary-container/20'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-bold text-on-surface">#RG-{req.id}</p>
                      <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${
                        req.status === 'COMPLETED'  ? 'bg-teal-100 text-teal-700' :
                        req.status === 'CANCELLED'  ? 'bg-red-100 text-red-600'   :
                        'bg-primary text-white'
                      }`}>{req.status}</span>
                    </div>
                    <p className="text-xs text-slate-400">{req.address?.substring(0, 40)}…</p>
                  </div>
                ))}
                {pickups.length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-4">No pickup requests yet.</p>
                )}
              </div>
            </div>

            {/* Pickup summary */}
            {activePickup && (
              <div className="bg-gradient-to-br from-[#326669] to-[#1a4a4c] rounded-2xl p-6 text-white shadow-xl">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined">info</span>
                  Pickup Summary
                </h3>
                <div className="space-y-3">
                  {[
                    { label: 'Pickup ID',  val: `#RG-${activePickup.id}` },
                    { label: 'Status',     val: activePickup.status },
                    { label: 'Weight',     val: activePickup.final_collected_weight || activePickup.waste?.estimated_weight ? `${activePickup.final_collected_weight || activePickup.waste?.estimated_weight} kg` : 'TBD' },
                    { label: 'Expected Valuation', val: activePickup.final_price || activePickup.waste?.estimated_price ? `₹${(activePickup.final_price || activePickup.waste.estimated_price).toLocaleString()}` : 'Pending AI Assessment' },
                    { label: 'Scheduled',  val: activePickup.pickup_date ? new Date(activePickup.pickup_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Not set' },
                  ].map((item, i) => (
                    <div key={i} className="flex justify-between text-sm border-b border-white/10 pb-2 last:border-0">
                      <span className="text-white/60">{item.label}</span>
                      <span className="font-bold">{item.val}</span>
                    </div>
                  ))}
                  <button 
                    onClick={() => navigate(`/pickup/${activePickup.id}/qr`)}
                    className="w-full mt-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2"
                  >
                    <span className="material-symbols-outlined text-sm">qr_code_2</span> View QR Code
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Phone Modal */}
      {showPhoneModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-sm text-center">
            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="material-symbols-outlined text-teal-600 text-3xl">call</span>
            </div>
            <h3 className="text-xl font-black text-on-surface mb-1">Collector Phone</h3>
            <p className="text-slate-500 text-sm mb-4">Contact your assigned collector</p>
            <div className="bg-surface rounded-2xl py-4 px-6 mb-6">
              <p className="text-xl font-black text-primary">Contact via admin</p>
            </div>
            <button onClick={() => setShowPhoneModal(false)}
              className="w-full py-3 border border-outline-variant rounded-xl font-bold text-sm text-slate-600">
              Close
            </button>
          </div>
        </div>
      )}

      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-sm text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="material-symbols-outlined text-blue-600 text-3xl">mail</span>
            </div>
            <h3 className="text-xl font-black text-on-surface mb-1">Contact Collector</h3>
            <p className="text-slate-400 text-sm mb-4">Reach out through the platform</p>
            <button onClick={() => setShowEmailModal(false)}
              className="w-full py-3 border border-outline-variant rounded-xl font-bold text-sm text-slate-600">
              Close
            </button>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
