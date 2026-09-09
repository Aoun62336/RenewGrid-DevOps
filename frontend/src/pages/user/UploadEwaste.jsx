import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/layout/DashboardLayout';
import UserSidebar from '../../components/layout/UserSidebar';
import { wasteAPI } from '../../services/api';

export default function UploadEwaste() {
  const navigate = useNavigate();
  const [dragActive, setDragActive] = useState(false);
  const [previews, setPreviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [recentUploads, setRecentUploads] = useState([]);
  const fileInputRef = useRef(null);
  const formRef = useRef(null);

  useEffect(() => {
    fetchRecentUploads();
  }, []);

  const fetchRecentUploads = async () => {
    try {
      const res = await wasteAPI.myUploads(1, 5);
      setRecentUploads(res.items || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    if (previews.length === 0) {
      setError('Please upload at least one image.');
      return;
    }

    const formData = new FormData(formRef.current);
    
    // Append images
    previews.forEach((file) => {
      formData.append('images', file);
    });

    setLoading(true);
    try {
      const res = await wasteAPI.upload(formData);
      setSuccessMsg('E-Waste uploaded successfully! Analyzing with AI...');
      formRef.current.reset();
      setPreviews([]);
      fetchRecentUploads();
      
      // Navigate to AI price estimation after a short delay
      setTimeout(() => {
        navigate(`/user/ai-price/${res.id}`);
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to upload e-waste.');
    } finally {
      setLoading(false);
    }
  };
  const handleFiles = (files) => {
    const newFiles = Array.from(files);
    setPreviews(prev => {
      const combined = [...prev, ...newFiles];
      return combined.slice(0, 5); // Limit to max 5
    });
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const onDragLeave = () => setDragActive(false);

  const onDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const onFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index) => {
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <DashboardLayout sidebar={UserSidebar} title="Upload E-Waste">
      <div className="mb-8">
        <p className="text-primary font-bold tracking-widest text-xs uppercase mb-1">Submit New Item</p>
        <h2 className="text-3xl font-black text-on-surface -tracking-tight">Upload E-Waste for Recycling</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-8">
          {/* Enhanced Upload Zone */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-outline-variant">
            <h3 className="text-lg font-bold text-on-surface mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary rounded-full"></span> Item Images
            </h3>
            
            <div
              className={`rounded-3xl border-2 border-dashed py-24 px-10 text-center transition-all cursor-pointer ${
                dragActive ? 'border-primary bg-primary/10' : 'border-primary/20 hover:border-primary/40 hover:bg-slate-50'
              }`}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={onFileChange} 
                accept="image/*" 
                multiple 
                className="hidden" 
              />
              <div className="w-24 h-24 mx-auto bg-primary-container rounded-full flex items-center justify-center mb-6 shadow-sm">
                <span className="material-symbols-outlined text-primary text-5xl">cloud_upload</span>
              </div>
              <h3 className="text-2xl font-bold text-on-surface mb-3">Drag & Drop Images</h3>
              <p className="text-slate-500 mb-8 max-w-md mx-auto leading-relaxed">
                Add up to 5 clear photos of your item (JPG, PNG, HEIC — max 10MB per file). Click anywhere in this box or use the button below.
              </p>
              <button 
                type="button" 
                className="px-10 py-4 bg-primary text-white text-lg rounded-xl font-bold shadow-lg hover:shadow-xl transition-all pointer-events-none"
              >
                Browse Files
              </button>
            </div>

            {/* Image Previews displaying below browse button area */}
            {previews.length > 0 && (
              <div className="mt-6">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-bold text-slate-700">Uploaded Previews ({previews.length}/5)</p>
                  {previews.length >= 5 && <span className="text-xs font-bold text-red-500">Maximum files reached</span>}
                </div>
                <div className="flex flex-wrap gap-4">
                  {previews.map((file, idx) => (
                    <div key={idx} className="relative w-28 h-28 rounded-xl border border-outline-variant shadow-sm overflow-hidden group bg-surface flex items-center justify-center">
                      {/* Image Preview Thumbnail */}
                      <img 
                        src={URL.createObjectURL(file)} 
                        alt="Preview" 
                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                      />
                      {/* Dark overlay on hover */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      
                      {/* Remove Button */}
                      <button 
                        type="button"
                        onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                        className="absolute top-2 right-2 w-7 h-7 bg-white text-red-500 hover:text-white hover:bg-red-500 rounded-full flex justify-center items-center opacity-0 group-hover:opacity-100 transition-all shadow-md active:scale-95"
                      >
                        <span className="material-symbols-outlined text-sm font-bold">close</span>
                      </button>

                       {/* File label */}
                       <div className="absolute bottom-0 inset-x-0 bg-black/60 text-white text-[9px] font-medium px-2 py-1 truncate pointer-events-none">
                         {file.name}
                       </div>
                    </div>
                  ))}
                  
                  {/* Empty Slot Placeholder if under 5 */}
                  {previews.length < 5 && (
                    <div 
                       onClick={() => fileInputRef.current?.click()}
                       className="w-28 h-28 rounded-xl border-2 border-dashed border-outline-variant flex flex-col items-center justify-center text-slate-400 hover:text-primary hover:border-primary/40 hover:bg-surface transition-all cursor-pointer"
                    >
                       <span className="material-symbols-outlined mb-1">add_photo_alternate</span>
                       <span className="text-[10px] font-bold uppercase">Add More</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Item Details Form */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-outline-variant">
            <h3 className="text-lg font-bold text-on-surface mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary rounded-full"></span> Item Details
            </h3>
            
            {error && <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-xl text-sm font-semibold border border-red-200">{error}</div>}
            {successMsg && <div className="mb-6 p-4 bg-teal-50 text-teal-700 rounded-xl text-sm font-semibold border border-teal-200">{successMsg}</div>}

            <form ref={formRef} onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-slate-700 mb-2">Item Title</label>
                <input name="title" required type="text" placeholder="e.g., Old Dell Inspiron Laptop" className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Item Category</label>
                <select name="category" required className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all bg-white">
                  <option value="">Select category...</option>
                  <option>Laptops & Computers</option>
                  <option>Mobile Phones</option>
                  <option>Monitors & Displays</option>
                  <option>Printers & Peripherals</option>
                  <option>Circuit Boards</option>
                  <option>Batteries</option>
                  <option>Mixed Electronics</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Condition</label>
                <select name="condition" className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all bg-white">
                  <option value="">Select condition...</option>
                  <option>Working</option>
                  <option>Partially Working</option>
                  <option>Non-functional</option>
                  <option>Damaged</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Estimated Weight (kg)</label>
                <input name="estimated_weight" required type="number" step="0.001" min="0" placeholder="e.g., 2.5" className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Quantity</label>
                <input name="quantity" required type="number" min="1" defaultValue="1" placeholder="e.g., 1" className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-slate-700 mb-2">Description</label>
                <textarea name="description" rows={3} placeholder="Provide any additional details about the item..." className="w-full px-4 py-3 rounded-xl border border-primary-light focus:ring-2 focus:ring-primary focus:border-primary transition-all resize-none" />
              </div>
              <div className="md:col-span-2 mt-2">
                <button type="submit" disabled={loading} className="w-full py-4 bg-primary text-white rounded-xl font-bold text-lg shadow-xl shadow-primary/20 hover:shadow-2xl transition-all hover:scale-[1.01] active:scale-[0.99] flex justify-center items-center gap-2 disabled:opacity-70">
                  {loading ? (
                    <><span className="material-symbols-outlined animate-spin">progress_activity</span> Uploading...</>
                  ) : (
                    <><span className="material-symbols-outlined">upload</span> Submit E-Waste</>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="lg:col-span-4 space-y-6">
          <div className="bg-primary rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
            <div className="relative z-10">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined">tips_and_updates</span> Upload Guidelines
              </h3>
              <ul className="space-y-3 text-sm text-white/80 leading-relaxed">
                <li className="flex items-start gap-2"><span className="material-symbols-outlined text-sm mt-0.5">check_circle</span>Take clear photos from multiple angles for accurate assessment.</li>
                <li className="flex items-start gap-2"><span className="material-symbols-outlined text-sm mt-0.5">check_circle</span>Include brand and model info if possible in the description.</li>
                <li className="flex items-start gap-2"><span className="material-symbols-outlined text-sm mt-0.5">check_circle</span>Accurately estimate weight to help collectors optimize routes.</li>
                <li className="flex items-start gap-2"><span className="material-symbols-outlined text-sm mt-0.5">check_circle</span>Please securely erase/remove your personal data before submission.</li>
              </ul>
            </div>
            <span className="material-symbols-outlined absolute -right-4 -bottom-4 text-[120px] text-white/5 pointer-events-none">photo_camera</span>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-outline-variant">
            <h3 className="text-lg font-bold text-on-surface mb-4">Recent Uploads</h3>
            <div className="space-y-3">
              {recentUploads.length === 0 ? (
                <p className="text-sm text-slate-400">No uploads yet.</p>
              ) : (
                recentUploads.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-surface transition-all cursor-pointer border border-transparent hover:border-outline-variant">
                    <div>
                      <p className="text-sm font-bold text-on-surface">{item.title}</p>
                      <p className="text-xs text-slate-400">{new Date(item.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
                    </div>
                    <span className="px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-[10px] font-black uppercase tracking-wider">
                      Uploaded
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
