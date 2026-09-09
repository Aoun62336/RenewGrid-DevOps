import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authAPI } from '../../services/api';

export default function ResetPassword() {
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Password validation
  const hasMinLength = newPassword.length >= 8;
  const hasSymbol = /[!@#$%^&*()_+\-={};':|,.<>?/\\]/.test(newPassword);
  const passwordsMatch = newPassword === confirmPassword && confirmPassword.length > 0;

  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!token) {
      setError('Invalid or missing reset token.');
      return;
    }

    if (hasMinLength && hasSymbol && passwordsMatch) {
      setLoading(true);
      try {
        await authAPI.resetPassword({ token, new_password: newPassword });
        setSubmitted(true);
        setTimeout(() => navigate('/login'), 2500);
      } catch (err) {
        setError(err.message || 'Failed to reset password.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="bg-white font-display text-slate-900 overflow-hidden min-h-screen w-full">
      <div className="flex min-h-screen w-full">

        {/* Left Panel - Image Section */}
        <div className="hidden lg:flex lg:w-[48%] relative flex-col justify-between">
          <img
            className="absolute inset-0 w-full h-full object-cover"
            alt="E-waste recycling warehouse facility"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDurGKv77xYFFNuCYNZQwMdPeoFiqbUtCxpvTwKoWDMN2m284WmnkMFKItlyImlgmQNY4XU-dEUZtZuhpRG9qc7us_wUAyQeGPOLN2c59LifPSF8MpJI-VFhPNfLp1ir9Xvje4TDOgLLYzuGDAO7n9aAfB5qNllPXt3MeoaFgPGAMCoEroljmWRvsxfh2D9L7QfLrdjEx6JpV7lbaATR2kKHk3ujZX3xnL_RE1ls0eC7qDQW3Pjs7-qhb3LZnh2VaEBNGdaeLAXdXNu"
          />
          <div className="absolute inset-0 bg-primary/50 mix-blend-multiply"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-primary/80 via-primary/30 to-primary/20"></div>

          {/* Logo */}
          <div className="absolute top-8 left-8 flex items-center gap-3 z-20 cursor-pointer" onClick={() => navigate('/')}>
            <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
              <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
            </div>
            <span className="text-2xl font-black tracking-tighter text-white">RenewGrid</span>
          </div>

          {/* Bottom Content */}
          <div className="relative z-20 mt-auto px-10 pb-10">
            <h2 className="text-4xl font-bold mb-4 leading-tight text-white">
              Reset Your Password<br />Securely
            </h2>
            <p className="text-lg text-white/80 max-w-md mb-8">
              Create a new password to regain access to your account
              and continue your sustainable journey.
            </p>

            {/* Trust Badge */}
            <div className="inline-flex items-center gap-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full py-2.5 px-5">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-primary-light border-2 border-white/30 flex items-center justify-center overflow-hidden">
                  <span className="material-symbols-outlined text-primary text-sm">person</span>
                </div>
                <div className="w-8 h-8 rounded-full bg-primary-light border-2 border-white/30 flex items-center justify-center overflow-hidden">
                  <span className="material-symbols-outlined text-primary text-sm">person</span>
                </div>
              </div>
              <span className="text-sm text-white font-medium">Trusted by 10,000+ recycling partners in India.</span>
            </div>
          </div>
        </div>

        {/* Right Panel - Form Section */}
        <div className="w-full lg:w-[52%] flex flex-col items-center justify-center p-8 sm:p-12 lg:p-16 bg-[#f0f4f4] relative">

          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8 cursor-pointer" onClick={() => navigate('/')}>
            <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
              <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
            </div>
            <span className="text-2xl font-black tracking-tighter text-[#326669]">RenewGrid</span>
          </div>

          {/* Form Card */}
          <div className="w-full max-w-md bg-white rounded-2xl shadow-xl shadow-slate-200/60 p-8 sm:p-10 fade-in-container">

            {submitted ? (
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
                  <span className="material-symbols-outlined text-green-500 text-3xl">check_circle</span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">Password Reset Successful!</h3>
                <p className="text-slate-500 text-sm mb-2">
                  Your password has been updated. Redirecting to login...
                </p>
                <div className="flex justify-center mt-4">
                  <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                </div>
              </div>
            ) : (
              <>
                <div className="mb-8 text-center">
                  <h1 className="text-2xl font-extrabold text-slate-900 mb-2">Reset Password</h1>
                  <p className="text-slate-500 text-sm leading-relaxed">
                    Enter your new password below to reset your account password.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                  {error && (
                    <div className="p-3 bg-red-100 text-red-700 border border-red-200 rounded-xl text-sm font-semibold">
                      {error}
                    </div>
                  )}
                  {/* New Password */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2" htmlFor="new-password">
                      New Password
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <span className="material-symbols-outlined text-slate-400 text-xl">lock</span>
                      </div>
                      <input
                        className="w-full pl-12 pr-12 py-3.5 rounded-xl border border-slate-200 bg-white text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400 text-sm"
                        id="new-password"
                        name="new-password"
                        placeholder="••••••••"
                        required
                        type={showNewPassword ? 'text' : 'password'}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-4 flex items-center cursor-pointer bg-transparent border-none"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        tabIndex={-1}
                      >
                        <span className="material-symbols-outlined text-slate-400 text-xl hover:text-slate-600 transition-colors">
                          {showNewPassword ? 'visibility_off' : 'visibility'}
                        </span>
                      </button>
                    </div>
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2" htmlFor="confirm-password">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <span className="material-symbols-outlined text-slate-400 text-xl">lock</span>
                      </div>
                      <input
                        className="w-full pl-12 pr-12 py-3.5 rounded-xl border border-slate-200 bg-white text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400 text-sm"
                        id="confirm-password"
                        name="confirm-password"
                        placeholder="••••••••"
                        required
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-4 flex items-center cursor-pointer bg-transparent border-none"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        tabIndex={-1}
                      >
                        <span className="material-symbols-outlined text-slate-400 text-xl hover:text-slate-600 transition-colors">
                          {showConfirmPassword ? 'visibility_off' : 'visibility'}
                        </span>
                      </button>
                    </div>
                    {confirmPassword.length > 0 && !passwordsMatch && (
                      <p className="text-xs text-red-500 mt-1.5 flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">error</span>
                        Passwords do not match
                      </p>
                    )}
                  </div>

                  {/* Password Requirements */}
                  <div className="flex items-center gap-6 py-1">
                    <div className="flex items-center gap-1.5">
                      <span className={`material-symbols-outlined text-[16px] ${hasMinLength ? 'text-green-500' : 'text-slate-300'}`}>
                        {hasMinLength ? 'check_circle' : 'radio_button_unchecked'}
                      </span>
                      <span className={`text-xs ${hasMinLength ? 'text-slate-700 font-medium' : 'text-slate-400'}`}>
                        8+ characters
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`material-symbols-outlined text-[16px] ${hasSymbol ? 'text-green-500' : 'text-slate-300'}`}>
                        {hasSymbol ? 'check_circle' : 'radio_button_unchecked'}
                      </span>
                      <span className={`text-xs ${hasSymbol ? 'text-slate-700 font-medium' : 'text-slate-400'}`}>
                        One symbol
                      </span>
                    </div>
                  </div>

                  <button
                    className={`w-full py-3.5 rounded-xl font-bold text-base shadow-lg transition-all flex justify-center items-center gap-2 ${
                      hasMinLength && hasSymbol && passwordsMatch && !loading
                        ? 'bg-primary hover:bg-primary/90 text-white shadow-primary/20 hover:scale-[1.01] active:scale-[0.99] cursor-pointer'
                        : 'bg-primary/50 text-white/80 cursor-not-allowed shadow-none'
                    }`}
                    type="submit"
                    disabled={!hasMinLength || !hasSymbol || !passwordsMatch || loading}
                  >
                    {loading ? 'Resetting...' : 'Reset Password'}
                    {!loading && <span className="material-symbols-outlined text-[18px]">arrow_forward</span>}
                  </button>
                </form>

                {/* Back to Login */}
                <div className="text-center mt-6 pt-4 border-t border-slate-100">
                  <button
                    onClick={() => navigate('/login')}
                    className="text-sm font-bold text-primary hover:underline transition-all inline-flex items-center gap-1.5 cursor-pointer bg-transparent border-none"
                  >
                    <span className="material-symbols-outlined text-[16px]">arrow_back</span>
                    Back to Login
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Footer */}
          <div className="mt-auto pt-10">
            <div className="flex flex-wrap justify-center gap-6 text-xs text-slate-400 mb-3">
              <a className="hover:text-primary transition-colors" href="#">Privacy Policy</a>
              <a className="hover:text-primary transition-colors" href="#">Terms of Service</a>
              <a className="hover:text-primary transition-colors" href="#">Security</a>
            </div>
            <p className="text-xs text-slate-400 text-center uppercase tracking-wider font-medium">
              © 2024 RenewGrid AI. Circular Economy Redefined.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
