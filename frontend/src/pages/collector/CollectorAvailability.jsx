import React, { useState } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import CollectorSidebar from '../../components/layout/CollectorSidebar';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const SLOT_TYPES = ['Standard', 'Express', 'Bulk', 'Residential', 'Commercial'];
const SLOT_DURATIONS = ['30 mins', '1 hour', '1.5 hours', '2 hours', '3 hours'];

const defaultSlot = () => ({ start: '09:00', end: '11:00', type: 'Standard', duration: '1 hour' });

export default function CollectorAvailability() {
  const [schedule, setSchedule] = useState(
    DAYS.reduce((acc, day) => ({
      ...acc,
      [day]: { enabled: day !== 'Sunday', slots: day !== 'Sunday' ? [defaultSlot()] : [] }
    }), {})
  );
  const [saved, setSaved] = useState(false);

  const toggleDay = (day) => {
    setSchedule(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        enabled: !prev[day].enabled,
        slots: !prev[day].enabled ? [defaultSlot()] : prev[day].slots,
      }
    }));
  };

  const addSlot = (day) => {
    if (schedule[day].slots.length >= 3) return;
    setSchedule(prev => ({
      ...prev,
      [day]: { ...prev[day], slots: [...prev[day].slots, defaultSlot()] }
    }));
  };

  const removeSlot = (day, idx) => {
    setSchedule(prev => ({
      ...prev,
      [day]: { ...prev[day], slots: prev[day].slots.filter((_, i) => i !== idx) }
    }));
  };

  const updateSlot = (day, idx, field, value) => {
    setSchedule(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        slots: prev[day].slots.map((s, i) => i === idx ? { ...s, [field]: value } : s)
      }
    }));
  };

  const handleSubmit = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const enabledCount = DAYS.filter(d => schedule[d].enabled).length;
  const totalSlots = DAYS.reduce((sum, d) => sum + schedule[d].slots.length, 0);

  return (
    <DashboardLayout sidebar={CollectorSidebar} title="Availability Management">
      <div className="mb-8">
        <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Schedule</p>
        <h2 className="text-3xl font-black text-on-surface -tracking-tight">Availability Management</h2>
      </div>

      {saved && (
        <div className="mb-6 flex items-center gap-3 p-4 bg-teal-50 border border-teal-200 rounded-xl text-teal-700">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
          <p className="text-sm font-bold">Availability schedule saved successfully!</p>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          { label: 'Active Days', value: enabledCount, icon: 'calendar_today', unit: `of ${DAYS.length} days` },
          { label: 'Total Slots', value: totalSlots, icon: 'schedule', unit: 'time slots' },
          { label: 'Days Off', value: DAYS.length - enabledCount, icon: 'event_busy', unit: 'unavailable' },
        ].map((s, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant">
            <div className="p-3 bg-primary-container rounded-xl text-primary w-fit mb-4">
              <span className="material-symbols-outlined">{s.icon}</span>
            </div>
            <p className="text-3xl font-black text-on-surface">{s.value}</p>
            <p className="text-sm font-bold text-on-surface mt-1">{s.label}</p>
            <p className="text-xs text-slate-400">{s.unit}</p>
          </div>
        ))}
      </div>

      {/* Day Schedules */}
      <div className="space-y-4">
        {DAYS.map((day) => {
          const dayData = schedule[day];
          const isWeekend = day === 'Saturday' || day === 'Sunday';
          return (
            <div
              key={day}
              className={`bg-white rounded-2xl border transition-all ${dayData.enabled ? 'border-primary/20 shadow-sm' : 'border-outline-variant opacity-60'}`}
            >
              {/* Day Header */}
              <div className="flex items-center justify-between p-5 border-b border-outline-variant">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-black text-sm ${dayData.enabled ? 'bg-primary text-white' : 'bg-surface text-slate-400'}`}>
                    {day.slice(0, 2)}
                  </div>
                  <div>
                    <p className="font-bold text-on-surface">{day}</p>
                    {isWeekend && <p className="text-xs text-slate-400">Weekend</p>}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-slate-400">
                    {dayData.enabled ? `${dayData.slots.length} slot${dayData.slots.length !== 1 ? 's' : ''}` : 'Day off'}
                  </span>
                  {/* Toggle Switch */}
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={dayData.enabled}
                      onChange={() => toggleDay(day)}
                      className="sr-only peer"
                    />
                    <div className="w-12 h-6 bg-slate-200 peer-focus:ring-2 peer-focus:ring-primary/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-primary after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                  </label>
                </div>
              </div>

              {/* Slots */}
              {dayData.enabled && (
                <div className="p-5 space-y-3">
                  {dayData.slots.map((slot, idx) => (
                    <div key={idx} className="flex flex-wrap items-center gap-3 p-4 bg-surface rounded-xl border border-outline-variant">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 bg-primary-container text-primary rounded-full flex items-center justify-center text-xs font-black">{idx + 1}</span>
                      </div>
                      {/* Start Time */}
                      <div className="flex flex-col min-w-[110px]">
                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Start Time</label>
                        <input
                          type="time"
                          value={slot.start}
                          onChange={(e) => updateSlot(day, idx, 'start', e.target.value)}
                          className="px-3 py-2 rounded-lg border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
                        />
                      </div>
                      {/* End Time */}
                      <div className="flex flex-col min-w-[110px]">
                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">End Time</label>
                        <input
                          type="time"
                          value={slot.end}
                          onChange={(e) => updateSlot(day, idx, 'end', e.target.value)}
                          className="px-3 py-2 rounded-lg border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
                        />
                      </div>
                      {/* Slot Type */}
                      <div className="flex flex-col min-w-[140px]">
                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Type</label>
                        <select
                          value={slot.type}
                          onChange={(e) => updateSlot(day, idx, 'type', e.target.value)}
                          className="px-3 py-2 rounded-lg border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
                        >
                          {SLOT_TYPES.map(t => <option key={t}>{t}</option>)}
                        </select>
                      </div>
                      {/* Duration */}
                      <div className="flex flex-col min-w-[130px]">
                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Slot Duration</label>
                        <select
                          value={slot.duration}
                          onChange={(e) => updateSlot(day, idx, 'duration', e.target.value)}
                          className="px-3 py-2 rounded-lg border border-outline-variant text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-white"
                        >
                          {SLOT_DURATIONS.map(d => <option key={d}>{d}</option>)}
                        </select>
                      </div>
                      {/* Remove */}
                      {dayData.slots.length > 1 && (
                        <button
                          onClick={() => removeSlot(day, idx)}
                          className="p-2 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-all ml-auto"
                          title="Remove slot"
                        >
                          <span className="material-symbols-outlined text-xl">remove_circle</span>
                        </button>
                      )}
                    </div>
                  ))}
                  {/* Add Slot */}
                  {dayData.slots.length < 3 && (
                    <button
                      onClick={() => addSlot(day)}
                      className="flex items-center gap-2 text-sm font-bold text-primary hover:text-primary/80 transition-all py-2 px-3 rounded-lg hover:bg-primary/5"
                    >
                      <span className="material-symbols-outlined text-sm">add_circle</span>
                      Add Slot {dayData.slots.length < 2 ? `(${3 - dayData.slots.length} more allowed)` : ''}
                    </button>
                  )}
                  {dayData.slots.length >= 3 && (
                    <p className="text-xs text-slate-400 px-3">Maximum 3 slots per day reached.</p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Submit */}
      <div className="mt-8 flex justify-end gap-4">
        <button
          onClick={() => {
            setSchedule(DAYS.reduce((acc, day) => ({
              ...acc,
              [day]: { enabled: day !== 'Sunday', slots: day !== 'Sunday' ? [defaultSlot()] : [] }
            }), {}));
          }}
          className="px-8 py-3 border border-outline-variant rounded-xl font-bold text-slate-600 hover:bg-surface transition-all"
        >
          Reset to Default
        </button>
        <button
          onClick={handleSubmit}
          className="px-10 py-4 bg-primary text-white rounded-xl font-bold text-base shadow-xl shadow-primary/20 hover:shadow-2xl transition-all hover:scale-[1.01] active:scale-[0.99] flex items-center gap-2"
        >
          <span className="material-symbols-outlined">save</span>
          Save Availability
        </button>
      </div>
    </DashboardLayout>
  );
}
