import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

export default function Register() {
  const navigate = useNavigate();
  const [role, setRole] = useState('recycler');
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    
    const fullName = e.target.name.value;
    const email = e.target.email.value;
    const password = e.target.password.value;
    const confirmPassword = e.target['confirm-password'].value;

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      await authAPI.register({
        email,
        password,
        full_name: fullName,
        role: role.toLowerCase(),
      });
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white font-display text-slate-900 overflow-hidden h-screen w-full">
      <div className="flex h-full w-full">
        <div className="hidden lg:block lg:w-1/2 relative">
          <img
            className="absolute inset-0 w-full h-full object-cover"
            alt="High-quality professional image of a green tech facility with digital earth overlays"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDurGKv77xYFFNuCYNZQwMdPeoFiqbUtCxpvTwKoWDMN2m284WmnkMFKItlyImlgmQNY4XU-dEUZtZuhpRG9qc7us_wUAyQeGPOLN2c59LifPSF8MpJI-VFhPNfLp1ir9Xvje4TDOgLLYzuGDAO7n9aAfB5qNllPXt3MeoaFgPGAMCoEroljmWRvsxfh2D9L7QfLrdjEx6JpV7lbaATR2kKHk3ujZX3xnL_RE1ls0eC7qDQW3Pjs7-qhb3LZnh2VaEBNGdaeLAXdXNu"
          />
          <div className="absolute inset-0 bg-primary/40 mix-blend-multiply"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-primary/80 to-transparent"></div>
          <div className="absolute top-10 left-10 flex items-center gap-3 z-20 cursor-pointer" onClick={() => navigate('/')}>
            <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
              <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
            </div>
            <span className="text-2xl font-black tracking-tighter text-white">RenewGrid</span>
          </div>
          <div className="absolute bottom-20 left-12 right-12 z-20 text-white">
            <h2 className="text-4xl font-bold mb-4 leading-tight">Driving the Circular Economy through AI.</h2>
            <p className="text-lg text-primary-light/90 max-w-md">
              Join thousands of recyclers and collectors worldwide in managing the e-waste lifecycle responsibly.
            </p>
          </div>
        </div>
        <div className="w-full lg:w-1/2 flex flex-col items-center justify-center p-8 sm:p-12 lg:p-20 bg-white overflow-y-auto">
          <div className="w-full max-w-md fade-in-container">
            <div className="lg:hidden flex items-center gap-3 mb-8 cursor-pointer" onClick={() => navigate('/')}>
              <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
                <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
              </div>
              <span className="text-2xl font-black tracking-tighter text-[#326669]">RenewGrid</span>
            </div>
            <div className="mb-10">
              <h1 className="text-3xl font-extrabold text-slate-900 mb-2">Join RenewGrid</h1>
              <p className="text-slate-500">Choose your role to get started.</p>
            </div>
            <form className="space-y-6" onSubmit={handleRegister}>
              {error && (
                <div className="p-3 bg-red-100 text-red-700 border border-red-200 rounded-xl text-sm font-semibold">
                  {error}
                </div>
              )}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700">I am a...</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <div>
                    <input checked={role === 'recycler'} onChange={() => setRole('recycler')} className="hidden role-option" id="role-recycler" name="role" type="radio" value="recycler" />
                    <label
                      className="flex items-center justify-center py-2.5 px-3 border border-primary-light rounded-xl text-sm font-medium text-primary hover:bg-primary-light/30 cursor-pointer transition-all text-center"
                      htmlFor="role-recycler"
                    >
                      Recycler
                    </label>
                  </div>
                  <div>
                    <input checked={role === 'collector'} onChange={() => setRole('collector')} className="hidden role-option" id="role-collector" name="role" type="radio" value="collector" />
                    <label
                      className="flex items-center justify-center py-2.5 px-3 border border-primary-light rounded-xl text-sm font-medium text-primary hover:bg-primary-light/30 cursor-pointer transition-all text-center"
                      htmlFor="role-collector"
                    >
                      Collector
                    </label>
                  </div>
                  <div>
                    <input checked={role === 'user'} onChange={() => setRole('user')} className="hidden role-option" id="role-user" name="role" type="radio" value="user" />
                    <label
                      className="flex items-center justify-center py-2.5 px-3 border border-primary-light rounded-xl text-sm font-medium text-primary hover:bg-primary-light/30 cursor-pointer transition-all text-center"
                      htmlFor="role-user"
                    >
                      User
                    </label>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5" htmlFor="name">
                    Full Name
                  </label>
                  <input
                    className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400"
                    id="name"
                    name="name"
                    placeholder="Enter your full name"
                    type="text"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5" htmlFor="email">
                    Email Address
                  </label>
                  <input
                    className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400"
                    id="email"
                    name="email"
                    placeholder="example@renewgrid.com"
                    type="email"
                    required
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5" htmlFor="password">
                      Password
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 pr-12 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400"
                        id="password"
                        name="password"
                        placeholder="••••••••"
                        type={showPass ? 'text' : 'password'}
                        required
                        minLength="8"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPass(!showPass)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-primary transition-colors"
                      >
                        <span className="material-symbols-outlined text-xl">{showPass ? 'visibility_off' : 'visibility'}</span>
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1.5" htmlFor="confirm-password">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 pr-12 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400"
                        id="confirm-password"
                        name="confirm-password"
                        placeholder="••••••••"
                        type={showConfirm ? 'text' : 'password'}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirm(!showConfirm)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-primary transition-colors"
                      >
                        <span className="material-symbols-outlined text-xl">{showConfirm ? 'visibility_off' : 'visibility'}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <button
                className="w-full bg-primary hover:bg-primary/90 text-white py-4 rounded-xl font-bold text-lg shadow-xl shadow-primary/20 transition-all hover:scale-[1.01] active:scale-[0.99] mt-4 disabled:opacity-70 disabled:cursor-not-allowed"
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </button>
              <div className="text-center mt-8">
                <p className="text-slate-500 text-sm">
                  Already have an account?
                  <span onClick={() => navigate('/login')} className="text-primary font-bold hover:underline ml-1 cursor-pointer">
                    Login
                  </span>
                </p>
              </div>
            </form>
            <div className="mt-12 pt-8 border-t border-slate-100 flex flex-wrap justify-center gap-6 text-xs text-slate-400">
              <a className="hover:text-primary transition-colors" href="#">
                Privacy Policy
              </a>
              <a className="hover:text-primary transition-colors" href="#">
                Terms of Service
              </a>
              <a className="hover:text-primary transition-colors" href="#">
                Help Center
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
