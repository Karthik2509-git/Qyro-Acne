import React, { useState, useEffect } from 'react';

const STEPS = [
  "Preparing image",
  "Analyzing skin patterns",
  "Assessing severity",
  "Generating wellness guidance",
  "Preparing personalized report"
];

const WELLNESS_PHRASES = [
  "Analyzing texture patterns",
  "Reviewing skin characteristics",
  "Preparing calibrated guidance"
];

export default function ProgressSequencer({ onComplete }) {
  const [stepIndex, setStepIndex] = useState(0);
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [fadeState, setFadeState] = useState('in');

  useEffect(() => {
    // Thoughtful transitions (900-1100ms per step, calibrated to 1000ms)
    const stepDuration = 1000;
    
    const stepInterval = setInterval(() => {
      setFadeState('out');
      
      setTimeout(() => {
        setStepIndex((prevIndex) => {
          if (prevIndex === STEPS.length - 1) {
            clearInterval(stepInterval);
            if (onComplete) onComplete();
            return prevIndex;
          }
          setFadeState('in');
          return prevIndex + 1;
        });
      }, 150);
      
    }, stepDuration);

    // Rotate wellness phrases every 900ms independently to show depth
    const phraseInterval = setInterval(() => {
      setPhraseIndex((prev) => (prev + 1) % WELLNESS_PHRASES.length);
    }, 900);

    return () => {
      clearInterval(stepInterval);
      clearInterval(phraseInterval);
    };
  }, [onComplete]);

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="relative mb-6 flex items-center justify-center">
        {/* Animated breathing glow */}
        <div className="absolute w-20 h-20 rounded-full border border-brand-cyan/20 animate-ping opacity-50"></div>
        {/* Continuous loader */}
        <div className="w-14 h-14 rounded-full border-4 border-slate-50 border-t-brand-indigo animate-spin"></div>
      </div>
      
      <p className="text-brand-indigo text-[10px] font-bold tracking-widest uppercase mb-1.5">
        Clinical Assessment
      </p>
      
      {/* Primary transitioning step (Calibration 4) */}
      <h3 className={`text-slate-800 text-lg font-bold min-h-[28px] transition-all duration-200 ${
        fadeState === 'in' ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform -translate-y-0.5'
      }`}>
        {STEPS[stepIndex]}...
      </h3>
      
      {/* Dynamic Sub-phrase (Calibration 3) */}
      <p className="text-slate-400 text-xs mt-1 min-h-[16px] animate-pulse">
        {WELLNESS_PHRASES[phraseIndex]}
      </p>
      
      {/* Moving Soft Glow Progress Bar (Calibration 3) */}
      <div className="w-48 h-1 bg-slate-100 rounded-full overflow-hidden relative mt-6 mb-4">
        <div className="absolute top-0 bottom-0 left-0 bg-brand-indigo w-1/3 rounded-full animate-loading-glow"></div>
      </div>
      
      {/* Premium Step Dots */}
      <div className="flex gap-1.5 justify-center">
        {STEPS.map((_, idx) => (
          <div 
            key={idx} 
            className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
              idx === stepIndex ? 'w-4 bg-brand-indigo' : idx < stepIndex ? 'bg-brand-indigo/40' : 'bg-slate-200'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
