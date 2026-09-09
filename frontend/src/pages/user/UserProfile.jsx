import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import UserSidebar from '../../components/layout/UserSidebar';
import { useNavigate } from 'react-router-dom';
import { authAPI, BASE_URL } from '../../services/api';
import ProfileImageCropper from '../../components/common/ProfileImageCropper';

export default function UserProfile() {
  const navigate = useNavigate();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({ full_name: '', phone_number: '', address: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await authAPI.me();
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        phone_number: data.phone_number || '',
        address: data.address || ''
      });
    } catch {
      setError('Failed to load profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      const data = await authAPI.updateProfile(formData);
      setProfile(data);
      setSuccess('Profile updated successfully!');
    } catch (err) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout sidebar={UserSidebar} title="Profile / Settings">
      <div className="mb-8">
        <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Account</p>
        <h2 className="text-3xl font-black text-on-surface -tracking-tight">Profile & Settings</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-6">
          {/* Profile Info */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-outline-variant">
            <h3 className="text-lg font-bold text-on-surface mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary rounded-full"></span> Personal Information
            </h3>
            
            {error && <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-xl text-sm font-semibold border border-red-200">{error}</div>}
            {success && <div className="mb-6 p-4 bg-teal-50 text-teal-700 rounded-xl text-sm font-semibold border border-teal-200">{success}</div>}

            {loading ? (
              <div className="flex justify-center items-center py-12">
                <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
              </div>
            ) : (
              <form onSubmit={handleUpdate}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Full Name</label>
                    <input type="text" value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Email Address</label>
                    <input type="email" value={profile?.email} disabled className="w-full px-4 py-3 rounded-xl border border-outline-variant bg-surface text-slate-500 cursor-not-allowed" />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Phone Number</label>
                    <input type="tel" value={formData.phone_number} onChange={e => setFormData({...formData, phone_number: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Address</label>
                    <textarea rows={3} value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all resize-none" />
                  </div>
                </div>
                <button type="submit" disabled={saving} className="mt-6 px-8 py-3 bg-primary text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all disabled:opacity-70 flex items-center gap-2">
                  {saving && <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>}
                  Save Changes
                </button>
              </form>
            )}
          </div>
        </div>

        <div className="lg:col-span-4 space-y-6">
          {/* Profile Card */}
          <div className="bg-primary rounded-2xl p-6 text-white text-center shadow-xl relative overflow-hidden">
            <div className="relative z-10">
              <div className="mb-4">
                <ProfileImageCropper 
                  currentImage={profile?.profile_image ? (profile.profile_image.startsWith('http') ? profile.profile_image : `${BASE_URL}${profile.profile_image}`) : ''} 
                  onImageUpdated={(url) => setProfile(p => ({...p, profile_image: url}))}
                  size="w-24 h-24"
                />
              </div>

              <h3 className="text-xl font-black">{profile?.full_name || 'Loading...'}</h3>
              <p className="text-white/60 text-sm">Member since {profile ? new Date(profile.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '...'}</p>
              <div className="mt-4 p-4 bg-white/10 rounded-xl">
                <p className="text-xs text-white/60 font-bold uppercase tracking-widest">Role</p>
                <p className="text-xl font-black mt-1 capitalize">{profile?.role || '...'}</p>
              </div>
            </div>
            <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-white/5 rounded-full"></div>
          </div>

          {/* Security */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant">
            <h3 className="text-lg font-bold text-on-surface mb-4">Security</h3>
            <div className="space-y-3">
              <button
                onClick={() => navigate('/user/change-password')}
                className="w-full p-4 rounded-xl border border-outline-variant hover:border-primary hover:bg-primary/5 transition-all text-left flex items-center gap-3"
              >
                <span className="material-symbols-outlined text-primary">lock</span>
                <span className="text-sm font-bold text-on-surface">Change Password</span>
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="w-full p-4 rounded-xl border border-error/20 hover:border-error hover:bg-error/5 transition-all text-left flex items-center gap-3"
              >
                <span className="material-symbols-outlined text-error">delete</span>
                <span className="text-sm font-bold text-error">Delete Account</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Account Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 shadow-2xl w-full max-w-md">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="material-symbols-outlined text-red-500 text-3xl">warning</span>
            </div>
            <h3 className="text-xl font-black text-on-surface text-center mb-2">Delete Account</h3>
            <p className="text-slate-500 text-sm text-center mb-6">
              Are you sure you want to delete your account? This action is <strong className="text-red-500">permanent and irreversible</strong>. All your data and points will be lost.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 py-3 border border-outline-variant rounded-xl font-bold text-slate-600 hover:bg-surface transition-all"
              >
                Cancel
              </button>
              <button
                onClick={() => { setShowDeleteConfirm(false); navigate('/'); }}
                className="flex-1 py-3 bg-red-500 text-white rounded-xl font-bold hover:bg-red-600 transition-all shadow-lg hover:shadow-xl"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
