import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function SafeErrorPopup({ message, onClose }) {
  return (
    <div className="fixed inset-0 bg-slate-900/30 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-100 rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl flex flex-col items-center text-center animate-fade-in-up">
        <div className="w-14 h-14 rounded-full bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-500 mb-5">
          <AlertCircle className="w-7 h-7" />
        </div>
        
        <h3 className="text-slate-800 font-bold text-lg mb-2">We couldn't analyze this photo</h3>
        <p className="text-slate-500 text-sm mb-6 leading-relaxed">{message}</p>
        
        <button 
          onClick={onClose}
          className="premium-button w-full flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Try Another Photo
        </button>
      </div>
    </div>
  );
}
