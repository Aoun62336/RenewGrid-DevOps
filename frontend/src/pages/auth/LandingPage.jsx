import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const stats = [
    { value: '50K+', label: 'Tons Recycled', icon: 'recycling' },
    { value: '12K+', label: 'Active Users', icon: 'group' },
    { value: '98.4%', label: 'Efficiency Rate', icon: 'speed' },
    { value: '45.8T', label: 'CO₂ Saved', icon: 'eco' },
  ];

  const features = [
    {
      icon: 'smart_toy',
      title: 'AI-Powered Sorting',
      desc: 'Our advanced AI algorithms classify and route e-waste for maximum material recovery and minimal environmental impact.',
    },
    {
      icon: 'local_shipping',
      title: 'Smart Pickup Scheduling',
      desc: 'Schedule pickups at your convenience. Our route optimization ensures fast, fuel-efficient collection.',
    },
    {
      icon: 'monitoring',
      title: 'Real-Time Analytics',
      desc: 'Track your environmental impact with live dashboards showing CO₂ offset, materials recovered, and more.',
    },
    {
      icon: 'workspace_premium',
      title: 'Reward Ecosystem',
      desc: 'Earn green points for every recycling action. Redeem rewards and climb the leaderboard.',
    },
    {
      icon: 'hub',
      title: 'Circular Supply Chain',
      desc: 'Connect recyclers, collectors, and users in a transparent, end-to-end circular economy network.',
    },
    {
      icon: 'verified_user',
      title: 'Compliance & Reporting',
      desc: 'Automated regulatory compliance reports and audit trails for complete peace of mind.',
    },
  ];

  const roles = [
    {
      icon: 'person',
      title: 'User',
      desc: 'Upload e-waste, schedule pickups, track status, and earn rewards for responsible recycling.',
      color: 'from-teal-500 to-cyan-600',
    },
    {
      icon: 'local_shipping',
      title: 'Collector',
      desc: 'Manage assigned pickups, optimize routes, scan QR codes, and upload proof of collection.',
      color: 'from-indigo-500 to-purple-600',
    },
    {
      icon: 'precision_manufacturing',
      title: 'Recycler',
      desc: 'Manage waste receipts, AI recommendations, processing decisions, and inventory tracking.',
      color: 'from-emerald-500 to-teal-600',
    },
  ];

  return (
    <div className="bg-white font-display text-slate-900 overflow-x-hidden">
      {/* Navbar */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-white/90 backdrop-blur-xl shadow-lg shadow-primary/5' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-10 flex items-center justify-between h-20">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
              <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
            </div>
            <span className={`text-2xl font-black tracking-tighter transition-colors ${scrolled ? 'text-[#326669]' : 'text-white'}`}>RenewGrid</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className={`text-sm font-semibold transition-colors hover:text-primary ${scrolled ? 'text-slate-600' : 'text-white/80'}`}>Features</a>
            <a href="#how-it-works" className={`text-sm font-semibold transition-colors hover:text-primary ${scrolled ? 'text-slate-600' : 'text-white/80'}`}>How It Works</a>
            <a href="#roles" className={`text-sm font-semibold transition-colors hover:text-primary ${scrolled ? 'text-slate-600' : 'text-white/80'}`}>Roles</a>
            <a href="#stats" className={`text-sm font-semibold transition-colors hover:text-primary ${scrolled ? 'text-slate-600' : 'text-white/80'}`}>Impact</a>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <button onClick={() => navigate('/login')} className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${scrolled ? 'text-primary border-2 border-primary hover:bg-primary/5' : 'text-white border-2 border-white/30 hover:bg-white/10'}`}>
              Login
            </button>
            <button onClick={() => navigate('/register')} className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-xl text-sm font-bold shadow-lg shadow-primary/30 hover:shadow-xl transition-all hover:scale-[1.02] active:scale-[0.98]">
              Get Started
            </button>
          </div>
          <button onClick={() => setMobileMenu(!mobileMenu)} className="md:hidden p-2">
            <span className={`material-symbols-outlined text-2xl ${scrolled ? 'text-slate-700' : 'text-white'}`}>{mobileMenu ? 'close' : 'menu'}</span>
          </button>
        </div>
        {/* Mobile Menu */}
        {mobileMenu && (
          <div className="md:hidden bg-white border-t border-slate-100 shadow-xl animate-in">
            <div className="p-6 space-y-4">
              <a href="#features" className="block text-sm font-semibold text-slate-700 hover:text-primary">Features</a>
              <a href="#how-it-works" className="block text-sm font-semibold text-slate-700 hover:text-primary">How It Works</a>
              <a href="#roles" className="block text-sm font-semibold text-slate-700 hover:text-primary">Roles</a>
              <a href="#stats" className="block text-sm font-semibold text-slate-700 hover:text-primary">Impact</a>
              <div className="flex gap-3 pt-4 border-t border-slate-100">
                <button onClick={() => navigate('/login')} className="flex-1 py-3 border-2 border-primary text-primary rounded-xl font-bold text-sm">Login</button>
                <button onClick={() => navigate('/register')} className="flex-1 py-3 bg-primary text-white rounded-xl font-bold text-sm">Get Started</button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0">
          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuBLhcw8D0Me5ahb6OBOq_a1bxTEgbVlA412uX1zmZGd9vSydz2hzL_5ZKiCGL5pcbcy2obb333xF8cbV6Lc9aUFjMCQ44x6TbPRaEkTB9AkS--VZrx06DTeE3rWY0cZm5gb3kIvQpKgciIQomOyR9ZyC-Dskk46L8KcJPAbDgiwfXafsZ2f_z-LHn9uOqi9LTFEXIirwSdf-nzCwlavA1qoO8btVaG0kmcSt9SjTSCHr1GKp6nA2tvpr5o3E6PMcORvn0ytS1HgmKDw"
            alt="E-waste recycling facility"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-[#1a4a4d]/95 via-[#326669]/80 to-teal-900/70"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(155,208,211,0.15),transparent_60%)]"></div>
        </div>
        {/* Floating particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-teal-400/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-400/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
          <div className="absolute top-1/2 left-1/3 w-48 h-48 bg-white/5 rounded-full blur-2xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-10 py-32 lg:py-40">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20 mb-8">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              <span className="text-xs font-bold text-white/90 uppercase tracking-widest">AI-Powered E-Waste Management</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black text-white leading-[1.05] tracking-tighter mb-8">
              Driving the <span className="italic text-transparent bg-clip-text bg-gradient-to-r from-teal-200 to-cyan-300">Circular Economy</span> through AI.
            </h1>
            <p className="text-lg md:text-xl text-white/70 max-w-xl leading-relaxed mb-12 font-medium">
              Join thousands of recyclers, collectors, and users worldwide. Manage the e-waste lifecycle responsibly with intelligent automation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => navigate('/register')}
                className="group px-10 py-5 bg-white text-primary rounded-2xl font-black text-lg shadow-2xl shadow-black/20 hover:shadow-3xl transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-3"
              >
                Start Recycling Now
                <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </button>
              <button
                onClick={() => navigate('/login')}
                className="px-10 py-5 border-2 border-white/30 text-white rounded-2xl font-bold text-lg hover:bg-white/10 hover:border-white/50 transition-all flex items-center justify-center gap-3"
              >
                <span className="material-symbols-outlined">login</span>
                Login to Dashboard
              </button>
            </div>
          </div>
        </div>
        {/* Scroll indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/40 animate-bounce">
          <span className="text-xs font-bold uppercase tracking-widest">Scroll</span>
          <span className="material-symbols-outlined">expand_more</span>
        </div>
      </section>

      {/* Stats Bar */}
      <section id="stats" className="relative z-10 -mt-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="bg-white rounded-3xl shadow-2xl shadow-primary/10 border border-primary/5 p-8 grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((s, i) => (
              <div key={i} className="text-center group">
                <div className="w-14 h-14 mx-auto bg-primary-container rounded-2xl flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-white transition-all text-primary">
                  <span className="material-symbols-outlined text-2xl">{s.icon}</span>
                </div>
                <p className="text-3xl font-black text-primary tracking-tight">{s.value}</p>
                <p className="text-sm font-semibold text-slate-500 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-32 bg-gradient-to-b from-white to-[#f6f7f7]">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-20">
            <span className="inline-block px-4 py-2 bg-primary/5 text-primary text-xs font-black uppercase tracking-widest rounded-full mb-6">Platform Features</span>
            <h2 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tighter mb-6">
              Everything You Need for <br className="hidden md:block" />
              <span className="text-primary">Sustainable Recycling</span>
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">
              RenewGrid combines cutting-edge AI with a robust circular economy platform to make e-waste management effortless and impactful.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f, i) => (
              <div key={i} className="group bg-white rounded-3xl p-8 shadow-sm border border-slate-100 hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-2 transition-all duration-500">
                <div className="w-16 h-16 bg-primary-container rounded-2xl flex items-center justify-center mb-6 group-hover:bg-primary group-hover:scale-110 transition-all duration-300">
                  <span className="material-symbols-outlined text-3xl text-primary group-hover:text-white transition-colors">{f.icon}</span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{f.title}</h3>
                <p className="text-slate-500 leading-relaxed font-medium">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-32 bg-[#f6f7f7]">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="text-center mb-20">
            <span className="inline-block px-4 py-2 bg-primary/5 text-primary text-xs font-black uppercase tracking-widest rounded-full mb-6">How It Works</span>
            <h2 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tighter mb-6">
              Simple 4-Step <span className="text-primary">Process</span>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: '01', icon: 'app_registration', title: 'Register', desc: 'Create your account and select your role — User, Recycler, or Admin.' },
              { step: '02', icon: 'cloud_upload', title: 'Upload E-Waste', desc: 'List your e-waste items with photos and descriptions for quick processing.' },
              { step: '03', icon: 'local_shipping', title: 'Schedule Pickup', desc: 'Choose a convenient time slot. Our AI optimizes collection routes.' },
              { step: '04', icon: 'stars', title: 'Earn Rewards', desc: 'Track your recycling impact and earn green points for every action.' },
            ].map((s, i) => (
              <div key={i} className="relative text-center group">
                <div className="relative z-10">
                  <div className="text-7xl font-black text-primary/5 mb-4 group-hover:text-primary/10 transition-colors">{s.step}</div>
                  <div className="w-20 h-20 mx-auto bg-white rounded-3xl shadow-lg border border-primary/10 flex items-center justify-center mb-6 group-hover:shadow-2xl group-hover:-translate-y-2 transition-all">
                    <span className="material-symbols-outlined text-3xl text-primary">{s.icon}</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{s.title}</h3>
                  <p className="text-slate-500 text-sm leading-relaxed font-medium">{s.desc}</p>
                </div>
                {i < 3 && (
                  <div className="hidden md:block absolute top-28 -right-4 w-8 text-primary/20">
                    <span className="material-symbols-outlined text-3xl">chevron_right</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section id="roles" className="py-32 bg-white relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-6 lg:px-10 relative z-10">
          <div className="text-center mb-20">
            <span className="inline-block px-4 py-2 bg-primary/5 text-primary text-xs font-black uppercase tracking-widest rounded-full mb-6">Tailored Dashboards</span>
            <h2 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tighter mb-6">
              Built for Every <span className="text-primary">Stakeholder</span>
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">
              Whether you're a user, collector, or recycler — RenewGrid delivers a purpose-built dashboard experience.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {roles.map((r, i) => (
              <div key={i} className="group relative rounded-3xl overflow-hidden">
                <div className={`absolute inset-0 bg-gradient-to-br ${r.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
                <div className="relative z-10 p-10 bg-white border-2 border-slate-100 rounded-3xl group-hover:bg-transparent group-hover:border-transparent transition-all duration-500">
                  <div className="w-16 h-16 bg-primary-container rounded-2xl flex items-center justify-center mb-8 group-hover:bg-white/20 transition-all">
                    <span className="material-symbols-outlined text-3xl text-primary group-hover:text-white transition-colors">{r.icon}</span>
                  </div>
                  <h3 className="text-2xl font-black text-slate-900 mb-4 group-hover:text-white transition-colors">{r.title}</h3>
                  <p className="text-slate-500 leading-relaxed font-medium mb-8 group-hover:text-white/80 transition-colors">{r.desc}</p>
                  <button
                    onClick={() => navigate('/register')}
                    className="px-6 py-3 bg-primary text-white rounded-xl font-bold text-sm shadow-lg hover:shadow-xl transition-all group-hover:bg-white group-hover:text-primary"
                  >
                    Get Started →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a4a4d] via-primary to-teal-700"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(155,208,211,0.2),transparent_60%)]"></div>
        <div className="absolute top-10 right-10 w-80 h-80 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 left-10 w-64 h-64 bg-teal-300/10 rounded-full blur-3xl"></div>
        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20 mb-8">
            <span className="material-symbols-outlined text-white text-sm">trending_up</span>
            <span className="text-xs font-bold text-white/90 uppercase tracking-widest">Join the Movement</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white tracking-tighter mb-8 leading-tight">
            Ready to Build a<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-200 to-cyan-300">Sustainable Future?</span>
          </h2>
          <p className="text-xl text-white/60 max-w-xl mx-auto mb-12 font-medium">
            Start your circular economy journey today. It takes less than 2 minutes to create your account.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/register')}
              className="group px-12 py-5 bg-white text-primary rounded-2xl font-black text-lg shadow-2xl hover:shadow-3xl transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-3"
            >
              Create Free Account
              <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-12 py-5 border-2 border-white/30 text-white rounded-2xl font-bold text-lg hover:bg-white/10 transition-all flex items-center justify-center gap-3"
            >
              <span className="material-symbols-outlined">login</span>
              Login
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 text-white py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div className="md:col-span-1">
              <div className="flex items-center gap-3 mb-6 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                <div className="relative w-10 h-10 flex items-center justify-center bg-white rounded-full shadow-lg logo-animate overflow-hidden">
                  <span className="material-symbols-outlined text-[#326669] text-xl">recycling</span>
                </div>
                <span className="text-2xl font-black tracking-tighter text-white">RenewGrid</span>
              </div>
              <p className="text-slate-400 text-sm leading-relaxed mb-6 font-medium">
                AI-powered e-waste management platform driving the circular economy forward.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-widest text-slate-400 mb-4">Platform</h4>
              <ul className="space-y-3">
                <li><a href="#features" className="text-sm text-slate-400 hover:text-white transition-colors font-medium">Features</a></li>
                <li><a href="#how-it-works" className="text-sm text-slate-400 hover:text-white transition-colors font-medium">How It Works</a></li>
                <li><a href="#roles" className="text-sm text-slate-400 hover:text-white transition-colors font-medium">Dashboards</a></li>
                <li><a href="#stats" className="text-sm text-slate-400 hover:text-white transition-colors font-medium">Impact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-widest text-slate-400 mb-4">Company</h4>
              <ul className="space-y-3">
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">About Us</a></li>
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">Careers</a></li>
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">Press</a></li>
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">Blog</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase tracking-widest text-slate-400 mb-4">Legal</h4>
              <ul className="space-y-3">
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">Privacy Policy</a></li>
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">Terms of Service</a></li>
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">Cookie Policy</a></li>
                <li><a className="text-sm text-slate-400 hover:text-white transition-colors font-medium" href="#">GDPR</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-500 font-medium">© 2026 RenewGrid. Building a circular economy together.</p>
            <div className="flex gap-6">
              <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Eco Guidelines</a>
              <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Support Center</a>
              <a className="text-slate-500 hover:text-primary transition-colors text-sm font-medium" href="#">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
