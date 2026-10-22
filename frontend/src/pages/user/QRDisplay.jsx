import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/layout/DashboardLayout';
import UserSidebar from '../../components/layout/UserSidebar';
import { pickupAPI } from '../../services/api';

export default function QRDisplay() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [qrUrl, setQrUrl] = useState(null);
  const [manualCode, setManualCode] = useState('');
  const [expiresAt, setExpiresAt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchQR = async () => {
      try {
        const credentials = await pickupAPI.qr(id);
        setQrUrl(credentials.image_data_url);
        setManualCode(credentials.manual_code);
        setExpiresAt(credentials.expires_at);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (id) fetchQR();
  }, [id]);

  const handleDownload = () => {
    if (qrUrl) {
      const link = document.createElement('a');
      link.href = qrUrl;
      link.download = `pickup_${id}_qr.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(manualCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <DashboardLayout sidebar={UserSidebar} title="Pickup QR Code">
      <div className="mb-8">
        <button onClick={() => navigate(-1)} className="text-primary font-bold text-sm hover:underline flex items-center gap-1 mb-4">
          <span className="material-symbols-outlined text-sm">arrow_back</span> Back to Tracking
        </button>
        <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Handoff</p>
        <h2 className="text-3xl font-black text-on-surface -tracking-tight">Scan for Pickup</h2>
      </div>

      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-3xl p-8 shadow-sm border border-outline-variant text-center">
          <h3 className="text-xl font-black text-on-surface mb-2">Request #{id}</h3>
          <p className="text-sm text-slate-500 mb-8">Show this QR code to your collector when they arrive.</p>

          {loading ? (
            <div className="flex items-center justify-center h-64 border-2 border-dashed border-slate-200 rounded-2xl">
              <span className="material-symbols-outlined animate-spin text-primary text-4xl">progress_activity</span>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-64 border-2 border-red-100 rounded-2xl bg-red-50 text-red-600 p-6">
              <span className="material-symbols-outlined text-4xl mb-2">error</span>
              <p className="font-bold text-center">{error}</p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="inline-block p-4 bg-white border-4 border-primary/20 rounded-3xl shadow-lg">
                <img src={qrUrl} alt="Pickup QR Code" className="w-64 h-64 object-contain" />
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                <p className="text-xs text-slate-500 mb-2 font-medium">MANUAL ENTRY CODE</p>
                <div className="flex items-center justify-center gap-2">
                  <span className="font-mono font-bold text-sm break-all text-primary">{manualCode || 'Unavailable'}</span>
                  <button onClick={handleCopy} className="text-slate-400 hover:text-primary transition-colors">
                    <span className="material-symbols-outlined text-sm">{copied ? 'check' : 'content_copy'}</span>
                  </button>
                </div>
              </div>
              
              <p className="text-xs text-slate-500">Valid until {expiresAt ? new Date(expiresAt).toLocaleTimeString() : '—'}. Reload this page for a new code after expiration.</p>
              <button
                onClick={handleDownload}
                className="w-full py-4 bg-primary text-white rounded-xl font-bold text-lg shadow-xl shadow-primary/20 hover:shadow-2xl transition-all hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined">download</span> Download QR
              </button>
            </div>
          )}
        </div>

        {/* Amber Manual Fallback Card */}
        <div className="mt-4 bg-amber-50 border border-amber-200 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="material-symbols-outlined text-amber-600">keyboard</span>
            <h3 className="text-sm font-black text-amber-800 uppercase tracking-wider">QR Not Scanning?</h3>
          </div>
          <p className="text-xs text-amber-700 mb-4 leading-relaxed">
            If your collector can't scan the QR code, share this manual code with them. They can type it directly in their app under <strong>"Or Enter Code Manually"</strong>.
          </p>
          <div className="flex items-center gap-3">
            <div className="flex-1 bg-white border-2 border-amber-300 rounded-xl px-5 py-3 text-center select-all">
              <span className="text-2xl font-black tracking-widest text-amber-800 font-mono">{manualCode || 'Unavailable'}</span>
            </div>
            <button
              onClick={handleCopy}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl font-bold text-sm transition-all ${
                copied ? 'bg-teal-500 text-white' : 'bg-amber-500 text-white hover:bg-amber-600 active:scale-95'
              }`}
            >
              <span className="material-symbols-outlined text-sm">{copied ? 'check_circle' : 'content_copy'}</span>
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <p className="text-[10px] text-amber-600 mt-3 text-center font-medium">
            The pickup number alone cannot verify a handoff.
          </p>
        </div>

        <div className="mt-4 bg-primary/5 rounded-2xl p-6 border border-primary/10">
          <h3 className="text-sm font-bold text-primary mb-2 flex items-center gap-2">
            <span className="material-symbols-outlined">info</span> How it works
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            The collector will scan this QR code or enter the manual code to verify your pickup and start the collection process. Ensure your items are ready before they arrive.
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}
