import React from 'react';

/**
 * Reusable password input field with visibility toggle.
 * Defined outside any render function to avoid React hook/state reset issues.
 */
export default function PasswordField({ id, label, value, show, onToggle, onChange, placeholder }) {
  return (
    <div className="relative group">
      <label className="block text-sm font-bold text-slate-700 mb-2 tracking-wide">{label}</label>
      <div className="relative">
        <input
          id={id}
          type={show ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required
          className="w-full px-5 py-4 pr-12 rounded-2xl border-2 border-primary/10 bg-surface-bright shadow-sm focus:bg-white focus:ring-4 focus:ring-primary/10 focus:border-primary transition-all text-slate-800 placeholder:text-slate-400 font-medium"
        />
        <button
          type="button"
          onClick={onToggle}
          className="absolute right-4 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-primary hover:bg-primary/5 transition-all outline-none"
        >
          <span className="material-symbols-outlined text-[20px]">{show ? 'visibility_off' : 'visibility'}</span>
        </button>
      </div>
    </div>
  );
}
