import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState('user');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const email    = e.target.email.value;
    const password = e.target.password.value;

    try {
      // authAPI.login saves tokens to localStorage automatically
      const data = await authAPI.login({ email, password });
      const userRole = data.user.role.toLowerCase();

      if (userRole === 'recycler')  navigate('/dashboard');
      else if (userRole === 'collector') navigate('/collector-dashboard');
      else if (userRole === 'user')      navigate('/user-dashboard');
      else if (userRole === 'admin')     navigate('/admin-dashboard');
      else navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-surface text-on-surface min-h-screen relative">
      <div className="absolute top-4 left-4 z-[9999]">
        <button onClick={() => navigate('/')} className="bg-primary hover:bg-primary/90 text-white font-bold py-2 px-4 rounded-xl shadow-lg transition-all flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">arrow_back</span> Return to Home
        </button>
      </div>
      
<div className="flex h-full w-full">

<div className="hidden lg:block lg:w-1/2 relative">
<img className="absolute inset-0 w-full h-full object-cover" data-alt="High-quality professional image of a green tech facility with digital earth overlays" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDurGKv77xYFFNuCYNZQwMdPeoFiqbUtCxpvTwKoWDMN2m284WmnkMFKItlyImlgmQNY4XU-dEUZtZuhpRG9qc7us_wUAyQeGPOLN2c59LifPSF8MpJI-VFhPNfLp1ir9Xvje4TDOgLLYzuGDAO7n9aAfB5qNllPXt3MeoaFgPGAMCoEroljmWRvsxfh2D9L7QfLrdjEx6JpV7lbaATR2kKHk3ujZX3xnL_RE1ls0eC7qDQW3Pjs7-qhb3LZnh2VaEBNGdaeLAXdXNu"/>
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
<p className="text-lg text-primary-light/90 max-w-md">Join thousands of recyclers and collectors worldwide in managing the e-waste lifecycle responsibly.</p>
</div>
</div>

<div className="w-full lg:w-1/2 flex flex-col items-center justify-center p-8 sm:p-12 lg:p-20 bg-white dark:bg-background-dark overflow-y-auto">
<div className="w-full max-w-md fade-in-container">
<div className="lg:hidden flex items-center gap-3 mb-8 cursor-pointer" onClick={() => navigate('/')}>
  <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
    <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
  </div>
  <span className="text-2xl font-black tracking-tighter text-[#326669]">RenewGrid</span>
</div>
<div className="mb-10 text-center lg:text-left">
<h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mb-2">Welcome Back</h1>
<p className="text-slate-500 dark:text-gray-400">Securely log in to manage your e-waste lifecycle.</p>
</div>
<div className="mb-6">
<label className="block text-sm font-semibold text-slate-700 dark:text-gray-300 mb-2">Login as</label>
<div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
{['user', 'recycler', 'collector', 'admin'].map((r) => (
<button key={r} type="button" onClick={() => setRole(r)} className={`py-2.5 px-3 border rounded-xl text-sm font-medium cursor-pointer transition-all text-center capitalize ${role === r ? 'bg-primary text-white border-primary' : 'border-primary/20 text-primary hover:bg-primary/5'}`}>{r}</button>
))}
</div>
</div>
<form onSubmit={handleLogin} className="space-y-6">
{error && (
  <div className="p-3 bg-red-100 text-red-700 border border-red-200 rounded-xl text-sm font-semibold">
    {error}
  </div>
)}
<div>
<label className="block text-sm font-semibold text-slate-700 dark:text-gray-300 mb-1.5" htmlFor="email">Email Address</label>
<input className="w-full px-4 py-3 rounded-xl border border-primary-light dark:border-gray-700 bg-white dark:bg-gray-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400" id="email" name="email" placeholder="example@renewgrid.com" required="" type="email"/>
</div>
<div>
<div className="flex items-center justify-between mb-1.5">
<label className="block text-sm font-semibold text-slate-700 dark:text-gray-300" htmlFor="password">Password</label>
<span onClick={() => navigate('/forgot-password')} className="text-sm font-bold text-primary hover:underline transition-all cursor-pointer">Forgot Password?</span>
</div>
<div className="relative">
<input className="w-full px-4 py-3 pr-12 rounded-xl border border-primary-light dark:border-gray-700 bg-white dark:bg-gray-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-primary transition-all placeholder:text-slate-400" id="password" name="password" placeholder="••••••••" required="" type={showPassword ? 'text' : 'password'}/>
<button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-primary transition-colors">
<span className="material-symbols-outlined text-xl">{showPassword ? 'visibility_off' : 'visibility'}</span>
</button>
</div>
</div>
<button className="w-full bg-primary hover:bg-primary/90 text-white py-4 rounded-xl font-bold text-lg shadow-xl shadow-primary/20 transition-all hover:scale-[1.01] active:scale-[0.99] mt-4 flex justify-center items-center gap-2 capitalize disabled:opacity-70 disabled:cursor-not-allowed" type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : `Login as ${role}`}
                    {!isLoading && <span className="material-symbols-outlined text-[20px]">login</span>}
</button>
<div className="text-center mt-8">
<p className="text-slate-500 dark:text-gray-400 text-sm">
                        Don't have an account? 
                        <span onClick={() => navigate('/register')} className="text-primary font-bold hover:underline ml-1 cursor-pointer">Register Now</span>
</p>
</div>
</form>
<div className="mt-12 pt-8 border-t border-slate-100 dark:border-gray-800 flex flex-wrap justify-center gap-6 text-xs text-slate-400 uppercase tracking-widest font-semibold">
<a className="hover:text-primary transition-colors" href="#">Privacy</a>
<a className="hover:text-primary transition-colors" href="#">Terms</a>
<a className="hover:text-primary transition-colors" href="#">Support</a>
</div>
</div>
</div>
</div>
<div className="fixed bottom-6 right-6">
<button className="w-12 h-12 bg-white dark:bg-gray-800 border border-primary-light dark:border-gray-700 rounded-full shadow-xl flex items-center justify-center text-primary dark:text-white transition-transform hover:scale-110 active:scale-95" onClick={() => document.documentElement.classList.toggle('dark')}>
<span className="material-symbols-outlined">dark_mode</span>
</button>
</div>

    </div>
  );
}
