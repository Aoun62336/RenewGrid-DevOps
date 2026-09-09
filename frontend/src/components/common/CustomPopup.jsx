import React, { useState, useEffect } from 'react';

let alertCallback = null;
let confirmCallback = null;

export const customAlert = (message, type = 'info') => {
  return new Promise((resolve) => {
    alertCallback = { message, type, resolve };
    if (triggerRender) triggerRender();
  });
};

export const customConfirm = (message) => {
  return new Promise((resolve) => {
    confirmCallback = { message, resolve };
    if (triggerRender) triggerRender();
  });
};

let triggerRender = null;

export default function CustomPopup() {
  const [alertState, setAlertState] = useState(null);
  const [confirmState, setConfirmState] = useState(null);

  useEffect(() => {
    triggerRender = () => {
      setAlertState(alertCallback);
      setConfirmState(confirmCallback);
    };
  }, []);

  if (!alertState && !confirmState) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-[2rem] p-8 w-full max-w-sm shadow-2xl relative">
        {alertState && (
          <>
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${alertState.type === 'error' ? 'bg-red-100 text-red-500' : 'bg-primary-container text-primary'}`}>
              <span className="material-symbols-outlined text-3xl">
                {alertState.type === 'error' ? 'error' : 'info'}
              </span>
            </div>
            <h3 className="text-xl font-black text-center text-on-surface mb-2">Notification</h3>
            <p className="text-center text-slate-600 mb-8 font-medium">{alertState.message}</p>
            <button 
              onClick={() => {
                const resolve = alertState.resolve;
                alertCallback = null;
                setAlertState(null);
                resolve();
              }}
              className="w-full py-4 bg-primary text-white rounded-xl font-bold hover:shadow-lg transition-all">
              Okay
            </button>
          </>
        )}

        {confirmState && (
          <>
            <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 bg-amber-100 text-amber-500">
              <span className="material-symbols-outlined text-3xl">warning</span>
            </div>
            <h3 className="text-xl font-black text-center text-on-surface mb-2">Are you sure?</h3>
            <p className="text-center text-slate-600 mb-8 font-medium">{confirmState.message}</p>
            <div className="flex gap-3">
              <button 
                onClick={() => {
                  const resolve = confirmState.resolve;
                  confirmCallback = null;
                  setConfirmState(null);
                  resolve(false);
                }}
                className="flex-1 py-3 bg-slate-100 text-slate-600 rounded-xl font-bold hover:bg-slate-200 transition-all">
                Cancel
              </button>
              <button 
                onClick={() => {
                  const resolve = confirmState.resolve;
                  confirmCallback = null;
                  setConfirmState(null);
                  resolve(true);
                }}
                className="flex-1 py-3 bg-red-500 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all">
                Confirm
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
