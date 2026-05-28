import React, { useState } from 'react';
import { UploadCloud, Image as ImageIcon, ShieldCheck } from 'lucide-react';

export default function Dropzone({ onFileSelected }) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`dropzone-container p-10 md:p-12 flex flex-col items-center justify-center text-center transition-all duration-300 ${
        isDragOver 
          ? 'border-brand-indigo bg-brand-indigo/[0.02] scale-[1.02] shadow-xl shadow-brand-indigo/5' 
          : 'hover:border-brand-indigo/30 hover:shadow-lg hover:shadow-brand-indigo/[0.02] border-slate-200'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => document.getElementById('skin-file-input').click()}
    >
      <input 
        id="skin-file-input"
        type="file"
        accept="image/png, image/jpeg, image/jpg"
        className="hidden"
        onChange={handleFileInput}
      />
      <div className={`w-16 h-16 rounded-full flex items-center justify-center text-brand-indigo mb-5 transition-all duration-300 ${
        isDragOver ? 'bg-brand-indigo/10 scale-110' : 'bg-brand-indigo/5'
      }`}>
        <UploadCloud className="w-8 h-8" />
      </div>
      <p className="text-slate-800 font-bold mb-1 text-lg">Drag and drop your photo here</p>
      <p className="text-brand-muted text-sm mb-5">or click to browse from your device</p>
      
      {/* File constraints details (Calibration 2) */}
      <div className="text-[10px] font-semibold text-slate-400 bg-slate-50 border border-slate-100/50 px-3.5 py-2 rounded-full flex items-center gap-1.5 mb-5 uppercase tracking-wider">
        <ImageIcon className="w-3.5 h-3.5 text-slate-400" />
        JPG, JPEG, PNG up to 10MB
      </div>

      {/* Privacy Guarantee (Calibration 2) */}
      <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
        <span>Your image is analyzed securely and not stored.</span>
      </div>
    </div>
  );
}
