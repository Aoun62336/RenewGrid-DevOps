import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import CollectorSidebar from '../../components/layout/CollectorSidebar';
import { collectorAPI } from '../../services/api';

export default function CollectorReviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    collectorAPI.getReviews()
      .then(data => setReviews(Array.isArray(data) ? data : []))
      .catch(err => console.error('Failed to load reviews', err))
      .finally(() => setLoading(false));
  }, []);

  // Calculate average rating
  const avgRating = reviews.length > 0 
    ? (reviews.reduce((acc, r) => acc + r.rating, 0) / reviews.length).toFixed(1)
    : 0;

  return (
    <DashboardLayout sidebar={CollectorSidebar} title="My Reviews">
      <div className="mb-8">
        <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Feedback</p>
        <h2 className="text-3xl font-black text-on-surface -tracking-tight">Customer Reviews</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-primary text-white rounded-2xl p-6 shadow-lg flex flex-col justify-center items-center">
          <span className="material-symbols-outlined text-4xl mb-2 text-amber-300" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
          <span className="text-4xl font-black">{avgRating}</span>
          <span className="text-sm font-medium mt-1 text-white/80">Average Rating</span>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant flex flex-col justify-center items-center">
          <span className="material-symbols-outlined text-3xl mb-2 text-primary">reviews</span>
          <span className="text-4xl font-black text-on-surface">{reviews.length}</span>
          <span className="text-sm font-bold text-slate-500 mt-1 uppercase tracking-widest">Total Reviews</span>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant flex flex-col justify-center items-center">
          <span className="material-symbols-outlined text-3xl mb-2 text-teal-500">thumb_up</span>
          <span className="text-4xl font-black text-on-surface">{reviews.filter(r => r.rating >= 4).length}</span>
          <span className="text-sm font-bold text-slate-500 mt-1 uppercase tracking-widest">Positive (4-5★)</span>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant flex flex-col justify-center items-center">
          <span className="material-symbols-outlined text-3xl mb-2 text-amber-500">sentiment_neutral</span>
          <span className="text-4xl font-black text-on-surface">{reviews.filter(r => r.rating < 4).length}</span>
          <span className="text-sm font-bold text-slate-500 mt-1 uppercase tracking-widest">Needs Improvement</span>
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-outline-variant overflow-hidden">
        <div className="px-8 py-6 border-b border-outline-variant">
          <h3 className="text-lg font-black text-on-surface">Recent Feedback</h3>
        </div>
        
        {loading ? (
          <div className="flex justify-center items-center h-48">
            <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
          </div>
        ) : reviews.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <span className="material-symbols-outlined text-5xl text-slate-300 mb-4">rate_review</span>
            <p className="text-slate-400 font-semibold text-lg">No reviews yet.</p>
            <p className="text-slate-400 text-sm mt-1 max-w-sm">Complete more pickups. Customers can leave a rating and review after their pickup is complete.</p>
          </div>
        ) : (
          <div className="divide-y divide-outline-variant">
            {reviews.map(r => (
              <div key={r.id} className="p-8 hover:bg-surface-bright transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                  <div>
                    <h4 className="font-bold text-on-surface text-lg">{r.user_name}</h4>
                    <p className="text-sm text-slate-500">Pickup #{r.pickup_id} • {new Date(r.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
                  </div>
                  <div className="flex items-center gap-1 bg-surface-container px-4 py-2 rounded-xl w-fit">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <span key={s} className={`material-symbols-outlined text-xl ${s <= r.rating ? 'text-amber-400' : 'text-slate-300'}`} style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                    ))}
                    <span className="ml-2 font-black text-on-surface">{r.rating}.0</span>
                  </div>
                </div>
                <div className="bg-surface p-6 rounded-2xl">
                  <p className="text-slate-700 leading-relaxed italic">"{r.comment || 'No comment provided.'}"</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
