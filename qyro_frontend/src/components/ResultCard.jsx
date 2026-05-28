import React from 'react';

export default function ResultCard({ title, icon: Icon, children, className = "", delayClass = "" }) {
  return (
    <div className={`premium-card p-6 md:p-8 animate-fade-in-up ${delayClass} ${className}`}>
      {title && (
        <div className="flex items-center gap-2.5 border-b border-slate-50 pb-4 mb-5">
          {Icon && <Icon className="w-4.5 h-4.5 text-brand-indigo" />}
          <h4 className="text-slate-800 font-semibold text-sm uppercase tracking-wider">{title}</h4>
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}
