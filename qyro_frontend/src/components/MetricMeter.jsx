import React from 'react';

export default function MetricMeter({ severity, score }) {
  // Calibrate score max for percentage calculation (0 to 24 baseline)
  const scoreMax = 24.0;
  const percentage = Math.min(100, Math.max(0, (score / scoreMax) * 100));

  const getSeverityStyle = () => {
    switch (severity.toLowerCase()) {
      case 'minimal':
        return { color: 'text-emerald-500', bg: 'bg-emerald-500', border: 'border-emerald-500' };
      case 'mild':
        return { color: 'text-cyan-500', bg: 'bg-cyan-500', border: 'border-cyan-500' };
      case 'moderate':
        return { color: 'text-brand-indigo', bg: 'bg-brand-indigo', border: 'border-brand-indigo' };
      case 'severe':
        return { color: 'text-indigo-950', bg: 'bg-indigo-950', border: 'border-indigo-950' };
      default:
        return { color: 'text-brand-indigo', bg: 'bg-brand-indigo', border: 'border-brand-indigo' };
    }
  };

  const style = getSeverityStyle();

  return (
    <div className="flex flex-col w-full">
      {/* Visual Progress Bar */}
      <div className="relative h-2 bg-slate-100 rounded-full w-full mb-8 mt-4">
        <div 
          className={`h-full rounded-full transition-all duration-1000 ${style.bg} opacity-20`} 
          style={{ width: `${percentage}%` }}
        />
        {/* Glow Slider Thumb */}
        <div 
          className={`absolute top-1/2 -translate-y-1/2 w-4.5 h-4.5 rounded-full bg-white border-[3px] ${style.border} shadow-md transition-all duration-1000`}
          style={{ left: `calc(${percentage}% - 9px)` }}
        >
          {/* Inner core */}
          <div className="w-full h-full rounded-full animate-pulse opacity-40"></div>
        </div>
      </div>
      
      {/* Label anchors */}
      <div className="flex justify-between text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-1">
        <span className={severity.toLowerCase() === 'minimal' ? 'text-emerald-500 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Minimal</span>
        <span className={severity.toLowerCase() === 'mild' ? 'text-cyan-500 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Mild</span>
        <span className={severity.toLowerCase() === 'moderate' ? 'text-brand-indigo font-bold scale-[1.05]' : 'scale-90 transition-all'}>Moderate</span>
        <span className={severity.toLowerCase() === 'severe' ? 'text-indigo-950 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Severe</span>
      </div>
    </div>
  );
}
