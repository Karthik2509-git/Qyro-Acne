import React from 'react';

export default function MetricMeter({ severity, score }) {
  const sevLower = severity ? severity.toLowerCase() : '';

  // Snapped percentages for clean visual presentation across the 5 client stages
  let percentage = 10;
  if (sevLower.includes('stage 1') || sevLower === 'stage 1') {
    percentage = 32.5;
  } else if (sevLower.includes('stage 2') || sevLower === 'stage 2') {
    percentage = 55;
  } else if (sevLower.includes('stage 3') || sevLower === 'stage 3') {
    percentage = 77.5;
  } else if (sevLower.includes('stage 4') || sevLower === 'stage 4') {
    percentage = 100;
  } else if (sevLower.includes('minimal') || sevLower.includes('stage 0') || sevLower === 'stage 0') {
    percentage = 10;
  } else {
    // Score based fallback
    percentage = Math.min(100, Math.max(0, (score / 24.0) * 100));
  }

  const getSeverityStyle = () => {
    if (sevLower.includes('stage 1') || sevLower === 'stage 1') {
      return { color: 'text-cyan-500', bg: 'bg-cyan-500', border: 'border-cyan-500' };
    } else if (sevLower.includes('stage 2') || sevLower === 'stage 2') {
      return { color: 'text-sky-500', bg: 'bg-sky-500', border: 'border-sky-500' };
    } else if (sevLower.includes('stage 3') || sevLower === 'stage 3') {
      return { color: 'text-brand-indigo', bg: 'bg-brand-indigo', border: 'border-brand-indigo' };
    } else if (sevLower.includes('stage 4') || sevLower === 'stage 4') {
      return { color: 'text-purple-600', bg: 'bg-purple-600', border: 'border-purple-600' };
    } else {
      return { color: 'text-emerald-500', bg: 'bg-emerald-500', border: 'border-emerald-500' };
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
      <div className="flex justify-between text-[9px] md:text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-1">
        <span className={sevLower.includes('minimal') || sevLower.includes('0') ? 'text-emerald-500 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Stage 0</span>
        <span className={sevLower.includes('1') ? 'text-cyan-500 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Stage 1</span>
        <span className={sevLower.includes('2') ? 'text-sky-500 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Stage 2</span>
        <span className={sevLower.includes('3') ? 'text-brand-indigo font-bold scale-[1.05]' : 'scale-90 transition-all'}>Stage 3</span>
        <span className={sevLower.includes('4') ? 'text-purple-600 font-bold scale-[1.05]' : 'scale-90 transition-all'}>Stage 4</span>
      </div>
    </div>
  );
}

