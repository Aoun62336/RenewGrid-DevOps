import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [resending, setResending] = useState(false);

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (email) {
      setLoading(true);
      try {
        await authAPI.forgotPassword({ email });
        setSubmitted(true);
      } catch (err) {
        setError(err.message || 'Failed to send reset link.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleResend = () => {
    setResending(true);
    setTimeout(() => setResending(false), 2000);
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
              Secure Your Account<br />Easily
            </h2>
            <p className="text-lg text-white/80 max-w-md mb-8">
              We'll help you reset your password quickly and securely
              so you can continue managing your e-waste lifecycle
              across our PAN-India network.
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
            
            <div className="mb-8">
              <h1 className="text-2xl font-extrabold text-slate-900 mb-2">Forgot Password</h1>
              <p className="text-slate-500 text-sm leading-relaxed">
                Enter your registered email address to receive a password reset link.
              </p>
            </div>

            {submitted ? (
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="material-symbols-outlined text-green-500 text-3xl">check_circle</span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">Email Sent!</h3>
                <p className="text-slate-500 text-sm mb-6">
                  We've sent a password reset link to <strong>{email}</strong>. Please check your inbox.
                </p>
                <button
                  onClick={() => navigate('/login')}
                  className="w-full bg-primary hover:bg-primary/90 text-white py-3.5 rounded-xl font-bold text-base shadow-lg shadow-primary/20 transition-all hover:scale-[1.01] active:scale-[0.99] flex justify-center items-center gap-2"
                >
                  Back to Login
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                {error && (
                  <div className="p-3 bg-red-100 text-red-700 border border-red-200 rounded-xl text-sm font-semibold">
                    {error}
                  </div>
                )}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2" htmlFor="forgot-email">
                    Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <span className="material-symbols-outlined text-slate-400 text-xl">mail</span>
                    </div>
                    <input
                      className="w-full pl-12 pr-4 py-3.5 rounded-xl border border-slate-200 bg-white text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400 text-sm"
                      id="forgot-email"
                      name="email"
                      placeholder="example@renewgrid.com"
                      required
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                <button
                  className="w-full bg-primary hover:bg-primary/90 text-white py-3.5 rounded-xl font-bold text-base shadow-lg shadow-primary/20 transition-all hover:scale-[1.01] active:scale-[0.99] flex justify-center items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? 'Sending...' : 'Send Reset Link'}
                  {!loading && <span className="material-symbols-outlined text-[18px]">arrow_forward</span>}
                </button>
              </form>
            )}

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

            {/* Resend */}
            {!submitted && (
              <div className="text-center mt-4">
                <p className="text-xs text-slate-400">
                  Didn't receive the email?{' '}
                  <button
                    type="button"
                    onClick={handleResend}
                    className="font-bold text-slate-700 hover:text-primary hover:underline transition-all cursor-pointer bg-transparent border-none"
                  >
                    {resending ? 'Sending...' : 'Resend'}
                  </button>
                </p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-auto pt-10 text-center">
            <p className="text-xs text-slate-400">
              © 2024 RenewGrid. Circular Systems for a Greener Planet.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
