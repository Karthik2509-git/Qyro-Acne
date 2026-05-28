import React, { useState } from 'react';
import { Calendar, Clock, Video, CheckCircle, X } from 'lucide-react';

export default function TelehealthModal({ onClose }) {
  const [step, setStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState(null);

  const dates = ['Tomorrow', 'Wednesday', 'Thursday'];
  const times = ['09:00 AM', '11:30 AM', '02:00 PM', '04:15 PM'];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-brand-bg/80 backdrop-blur-sm animate-fade-in-up">
      <div className="relative w-full max-w-md bg-white border border-slate-100 rounded-3xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2 text-brand-indigo font-bold">
            <Video className="w-5 h-5" />
            Virtual Consultation
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {step === 1 ? (
            <div className="flex flex-col gap-6">
              <p className="text-slate-600 text-sm leading-relaxed">
                Connect with a certified dermatologist to review your Qyro analysis and establish a personalized treatment plan.
              </p>

              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" /> Select Day
                </h4>
                <div className="grid grid-cols-3 gap-2">
                  {dates.map((date) => (
                    <button
                      key={date}
                      onClick={() => setSelectedDate(date)}
                      className={`py-2 text-sm font-medium rounded-xl border transition-colors ${
                        selectedDate === date 
                          ? 'border-brand-indigo bg-brand-indigo/5 text-brand-indigo' 
                          : 'border-slate-200 text-slate-600 hover:border-slate-300'
                      }`}
                    >
                      {date}
                    </button>
                  ))}
                </div>
              </div>

              {selectedDate && (
                <div className="animate-fade-in-up">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <Clock className="w-4 h-4" /> Select Time
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {times.map((time) => (
                      <button
                        key={time}
                        onClick={() => setStep(2)}
                        className="py-2 text-sm font-medium rounded-xl border border-slate-200 text-slate-600 hover:border-brand-indigo hover:text-brand-indigo transition-colors"
                      >
                        {time}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6 text-center animate-fade-in-up">
              <div className="w-16 h-16 bg-emerald-50 text-emerald-500 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Session Confirmed</h3>
              <p className="text-slate-500 text-sm mb-6">
                Your virtual consultation is scheduled. We've sent a secure meeting link to your email.
              </p>
              <button 
                onClick={onClose}
                className="premium-button w-full"
              >
                Return to Dashboard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
