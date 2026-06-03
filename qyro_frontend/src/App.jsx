import React, { useState } from 'react';
import { Sparkles, BarChart, Heart, Stethoscope, ChevronDown, Check, HelpCircle, ShieldCheck, Video, Apple, Ban, Activity, Camera, Upload } from 'lucide-react';
import { API_URL } from './config/api';
import Dropzone from './components/Dropzone';
import ProgressSequencer from './components/ProgressSequencer';
import ResultCard from './components/ResultCard';
import MetricMeter from './components/MetricMeter';
import SafeErrorPopup from './components/SafeErrorPopup';
import TelehealthModal from './components/TelehealthModal';
import LiveCamera from './components/LiveCamera';

export default function App() {
  const [view, setView] = useState('landing'); // 'landing', 'loading', 'results'
  const [selectedFile, setSelectedFile] = useState(null);
  const [showTechnical, setShowTechnical] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [showTelehealth, setShowTelehealth] = useState(false);
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'camera'

  const handleFileSelected = async (file) => {
    setSelectedFile(file);
    setView('loading');
    
    const formData = new FormData();
    formData.append('image', file);
    
    const t0 = Date.now();
    
    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      // Calibrated 3-second minimal loading sequence to feel thoughtful (Calibration 4)
      const elapsed = Date.now() - t0;
      const remaining = Math.max(0, 3000 - elapsed);
      
      setTimeout(() => {
        if (response.ok && data.success) {
          setAnalysisData(data);
          setView('results');
        } else {
          // Backend custom error payload mapping (Calibration 6)
          const errorDetail = data.error || { message: "We couldn't analyze this image. Please capture a clear, well-lit photo of your skin." };
          setView('landing');
          setErrorMsg(errorDetail.message);
        }
      }, remaining);
      
    } catch (err) {
      console.error("API error during analysis:", err);
      // Timeout/fallback safety net
      setTimeout(() => {
        setView('landing');
        setErrorMsg("Server communication failed. Please check your connection and try again.");
      }, 1000);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setAnalysisData(null);
    setShowTechnical(false);
    setView('landing');
  };

  // Launch mock demo case directly (helps in offline / UI testing)
  const handleLaunchMock = () => {
    setView('loading');
    setTimeout(() => {
      setAnalysisData({
        "success": true,
        "processing_time_ms": 1240,
        "clinical_report": {
          "acne_detected": true,
          "severity": "Stage 2",
          "analysis_confidence": "Moderate confidence",
          "pattern_analysis": [
            "Pattern analysis suggests:",
            "• Mild inflammatory acne characteristics may be observed.",
            "• Secondary: Mixed inflammatory characteristics observed."
          ],
          "skin_guidance": [
            "General wellness focus:",
            "• mild inflammatory control",
            "• skin barrier protection",
            "• gentle soothing skincare",
            "• minimizing skin friction"
          ],
          "consultation": [
            "• Consider standard routine adjustments and professional consultation if inflammatory patterns persist.",
            "• This wellness guidance is educational and should not replace professional dermatological consultation."
          ],
          "nutrition_nutrients": ["Omega-3 fatty acids", "Zinc", "Vitamin C", "Antioxidants", "Green tea catechins"],
          "nutrition_eat_more": ["consider increasing berries", "consider increasing spinach", "consider increasing turmeric-infused meals", "consider increasing flaxseeds", "consider increasing green tea"],
          "nutrition_reduce": ["excessive highly spicy processed foods", "refined sugars", "oily fast foods"]
        },
        "technical_summary": {
          "detected_lesions": 5,
          "dominant_pattern": "Papular",
          "peak_confidence": 0.78
        }
      });
      setView('results');
    }, 3000);
  };

  // Launch mock clear reassurance skin case
  const handleLaunchClearMock = () => {
    setView('loading');
    setTimeout(() => {
      setAnalysisData({
        "success": true,
        "processing_time_ms": 642,
        "clinical_report": {
          "acne_detected": false,
          "severity": "Stage 0",
          "analysis_confidence": "High confidence stage assignment",
          "pattern_analysis": [
            "Skin appears generally under control.",
            "• No significant active acne characteristics observed.",
            "• Maintain a consistent, gentle daily cleansing routine."
          ],
          "skin_guidance": [
            "General wellness focus:",
            "• consistent hydration",
            "• barrier-friendly skincare",
            "• consistent cleansing habits"
          ],
          "consultation": [
            "• Maintain healthy, consistent skincare habits.",
            "• This wellness guidance is educational and should not replace professional dermatological consultation."
          ],
          "nutrition_nutrients": ["Vitamins A, C, E", "Zinc", "Water-soluble Fiber"],
          "nutrition_eat_more": ["consider increasing leafy greens", "consider increasing antioxidant-rich fruits", "consider increasing water-rich foods"],
          "nutrition_reduce": ["excessive refined sugar", "excessive ultra-processed foods"]
        },
        "technical_summary": {
          "detected_lesions": 2,
          "dominant_pattern": "Papular",
          "peak_confidence": 0.32
        }
      });
      setView('results');
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-brand-bg flex flex-col justify-between select-none relative overflow-x-hidden">
      {/* Dynamic ambient soft radial glow behind hero (Calibration 1) */}
      {view === 'landing' && (
        <div className="absolute top-[-25%] left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-brand-indigo/5 rounded-full blur-[140px] pointer-events-none z-0"></div>
      )}

      {/* Header navbar */}
      <header className="sticky top-0 z-40 bg-white/60 backdrop-blur-md border-b border-slate-100/50 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <span 
            onClick={handleReset}
            className="text-xl font-bold tracking-tight text-slate-800 flex items-center gap-1.5 cursor-pointer"
          >
            <div className="w-7 h-7 rounded-lg bg-brand-indigo flex items-center justify-center text-white font-black text-sm">Q</div>
            qyro
          </span>
          
          <span className="text-[10px] font-bold text-brand-indigo bg-brand-indigo/5 border border-brand-indigo/10 px-3 py-1.5 rounded-full uppercase tracking-wider">
            AI Skin Analysis
          </span>
        </div>
      </header>

      {/* Main viewport Container (Calibration 8) */}
      <main className="flex-grow max-w-2xl w-full mx-auto px-6 py-10 md:py-14 flex flex-col justify-center z-10">
        
        {/* VIEW 1: LANDING & UPLOAD */}
        {view === 'landing' && (
          <div className="flex flex-col gap-10 md:gap-12 animate-fade-in-up">
            {/* Hero (Calibration 1) */}
            <div className="text-center space-y-4">
              <h1 className="text-slate-800 text-4xl md:text-5.5xl font-extrabold tracking-tight leading-tight">
                Understand your skin. <span className="text-brand-indigo">Smarter.</span>
              </h1>
              <p className="text-brand-muted text-sm md:text-base max-w-lg mx-auto leading-relaxed px-2">
                Calibrated AI skin insights designed for clarity, guidance, and healthier routines.
              </p>
            </div>

            {/* Premium Tabs to switch Upload vs Live Scan */}
            <div className="flex justify-center gap-3 max-w-xs mx-auto mb-6">
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold border transition-all duration-300 cursor-pointer ${
                  activeTab === 'upload'
                    ? 'bg-brand-indigo text-white border-brand-indigo shadow-md shadow-brand-indigo/15 scale-[1.02]'
                    : 'bg-white text-slate-500 border-slate-200/60 hover:border-slate-300/80 hover:text-slate-700'
                }`}
              >
                <Upload className="w-3.5 h-3.5" />
                Upload Photo
              </button>
              <button
                onClick={() => setActiveTab('camera')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold border transition-all duration-300 cursor-pointer ${
                  activeTab === 'camera'
                    ? 'bg-brand-indigo text-white border-brand-indigo shadow-md shadow-brand-indigo/15 scale-[1.02]'
                    : 'bg-white text-slate-500 border-slate-200/60 hover:border-slate-300/80 hover:text-slate-700'
                }`}
              >
                <Camera className="w-3.5 h-3.5" />
                Take Live Scan
              </button>
            </div>

            {/* Luxurious upload zone / Live Camera capture */}
            <div className="w-full max-w-lg mx-auto">
              {activeTab === 'upload' ? (
                <Dropzone onFileSelected={handleFileSelected} />
              ) : (
                <LiveCamera onFileSelected={handleFileSelected} />
              )}
            </div>
            
            {/* Mock Trigger controls for validation & testing */}
            <div className="flex flex-wrap items-center justify-center gap-2 text-xs text-brand-muted mt-2">
              <span>Try Examples:</span>
              <button 
                onClick={handleLaunchMock}
                className="text-brand-indigo font-semibold bg-brand-indigo/5 hover:bg-brand-indigo/10 px-2.5 py-1.5 rounded-lg transition-colors"
              >
                Active Acne Mock
              </button>
              <button 
                onClick={handleLaunchClearMock}
                className="text-emerald-600 font-semibold bg-emerald-50 hover:bg-emerald-100 px-2.5 py-1.5 rounded-lg transition-colors"
              >
                Clear Skin Reassurance Mock
              </button>
              <button 
                onClick={() => setErrorMsg("Unsupported file format. Please upload JPG, JPEG, or PNG.")}
                className="text-rose-500 font-semibold bg-rose-50 hover:bg-rose-100 px-2.5 py-1.5 rounded-lg transition-colors"
              >
                Format Error Mock
              </button>
            </div>
          </div>
        )}

        {/* VIEW 2: LOADING PROGRESS */}
        {view === 'loading' && (
          <div className="bg-white border border-slate-100 rounded-3xl shadow-sm p-6 max-w-md w-full mx-auto animate-fade-in-up">
            <ProgressSequencer onComplete={() => {}} />
          </div>
        )}

        {/* VIEW 3: RESULTS DASHBOARD (Calibration 4 & 5) */}
        {view === 'results' && analysisData && (
          <div className="flex flex-col gap-6 w-full animate-fade-in-up">
            {/* Header reset controls */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Report Output</span>
              <button 
                onClick={handleReset}
                className="text-xs font-semibold text-brand-indigo hover:underline"
              >
                Analyze Another
              </button>
            </div>

            {/* 1. Skin Status Card (Calibration 5) */}
            <ResultCard delayClass="delay-75">
              <div className="flex items-start gap-4">
                {/* Reassurance visual check illustration (Calibration 5) */}
                {!analysisData.clinical_report.acne_detected && (
                  <div className="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-500 flex-shrink-0">
                    <Sparkles className="w-6 h-6 animate-pulse" />
                  </div>
                )}
                <div className="flex-grow flex flex-col gap-1.5">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Assessment Outcome</span>
                  <h2 className="text-slate-800 text-xl md:text-2.5xl font-bold tracking-tight">
                    {analysisData.clinical_report.acne_detected ? "Active Acne Pattern Detected" : "Skin appears generally under control."}
                  </h2>
                  <p className="text-brand-muted text-xs leading-relaxed mt-0.5">
                    {analysisData.clinical_report.acne_detected 
                      ? "Calibrated reasoning layers identified structural characteristics on the skin surface. Below is your clinical-grade wellness guidance."
                      : "Consistency matters. Keep supporting healthy skin habits. Maintain your regular cleansing and hydration routine."}
                  </p>
                </div>
              </div>
            </ResultCard>

            {/* 2. Severity Meter Card */}
            <ResultCard title="Severity Score Index" icon={BarChart} delayClass="delay-100">
              <div className="flex flex-col gap-1">
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-slate-800 text-3xl font-extrabold tracking-tight">
                    {analysisData.clinical_report.severity}
                  </span>
                  <span className="text-slate-400 text-xs font-medium">
                    (Score: {analysisData.technical_summary.detected_lesions}.0)
                  </span>
                </div>
                <MetricMeter severity={analysisData.clinical_report.severity} score={analysisData.technical_summary.detected_lesions * 2.0} />
              </div>
            </ResultCard>

            {/* 3. Pattern Analysis Card */}
            <ResultCard title="Pattern Suggestion Analysis" icon={Sparkles} delayClass="delay-150">
              <div className="flex flex-col gap-4">
                <p className="text-slate-800 font-semibold text-sm">
                  {analysisData.clinical_report.pattern_analysis[0] || "Pattern analysis suggests:"}
                </p>
                <div className="flex flex-col gap-3 pl-1.5">
                  {/* Handle list of strings vs reassuring string */}
                  {Array.isArray(analysisData.clinical_report.pattern_analysis) ? (
                    analysisData.clinical_report.pattern_analysis.slice(1).map((pattern, idx) => (
                      <div key={idx} className="flex items-start gap-2.5 text-slate-600 text-sm leading-relaxed">
                        <div className="w-1.5 h-1.5 rounded-full bg-brand-indigo mt-2 flex-shrink-0" />
                        <span>{pattern.replace("• ", "")}</span>
                      </div>
                    ))
                  ) : (
                    <div className="flex items-start gap-2.5 text-slate-600 text-sm leading-relaxed">
                      <div className="w-1.5 h-1.5 rounded-full bg-brand-indigo mt-2 flex-shrink-0" />
                      <span>{analysisData.clinical_report.pattern_analysis}</span>
                    </div>
                  )}
                </div>
              </div>
            </ResultCard>

            {/* 4. Skin Guidance Card */}
            <ResultCard title="Skin Guidance & Wellness" icon={Heart} delayClass="delay-200">
              <div className="flex flex-col gap-4">
                <p className="text-slate-800 font-semibold text-sm">
                  {analysisData.clinical_report.skin_guidance[0] || "General wellness focus:"}
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-1">
                  {analysisData.clinical_report.skin_guidance.slice(1).map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2.5 bg-slate-50/50 border border-slate-200/40 p-3 rounded-2xl text-slate-700 text-sm hover:shadow-sm transition-all duration-300">
                      <div className="w-5 h-5 rounded-full bg-brand-indigo/10 flex items-center justify-center text-brand-indigo flex-shrink-0">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                      <span className="capitalize">{item.replace("• ", "")}</span>
                    </div>
                  ))}
                </div>
              </div>
            </ResultCard>

            {/* 4.5. Nutrition Engine Dashboard Cards */}
            {analysisData.clinical_report.nutrition_nutrients && (
              <div className="flex flex-col gap-6 border-t border-slate-100/50 pt-5 mt-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-brand-indigo bg-brand-indigo/5 border border-brand-indigo/10 px-3.5 py-1.5 rounded-full uppercase tracking-wider">
                    Clinical Nutrition & Wellness Guidance
                  </span>
                </div>
                
                {/* Nutrients Card */}
                <ResultCard title="Nutrients Your Skin May Need" icon={Activity} delayClass="delay-225">
                  <div className="flex flex-wrap gap-2.5 pt-1">
                    {analysisData.clinical_report.nutrition_nutrients.map((nutrient, idx) => (
                      <span 
                        key={idx} 
                        className="px-4 py-2 bg-indigo-50/70 text-indigo-700 font-semibold text-xs rounded-2xl border border-indigo-100 hover:scale-105 hover:bg-indigo-50 hover:shadow-md transition-all duration-200 cursor-default shadow-sm"
                      >
                        {nutrient}
                      </span>
                    ))}
                  </div>
                </ResultCard>

                {/* Foods to Eat More */}
                <ResultCard title="Foods to Eat More" icon={Apple} delayClass="delay-250">
                  <div className="flex flex-wrap gap-2.5 pt-1">
                    {analysisData.clinical_report.nutrition_eat_more.map((food, idx) => (
                      <span 
                        key={idx} 
                        className="px-4 py-2 bg-emerald-50/70 text-emerald-700 font-semibold text-xs rounded-2xl border border-emerald-100 hover:scale-105 hover:bg-emerald-50 hover:shadow-md transition-all duration-200 cursor-default shadow-sm capitalize"
                      >
                        {food}
                      </span>
                    ))}
                  </div>
                </ResultCard>

                {/* Foods to Reduce */}
                <ResultCard title="Foods to Reduce/Avoid" icon={Ban} delayClass="delay-275">
                  <div className="flex flex-wrap gap-2.5 pt-1">
                    {analysisData.clinical_report.nutrition_reduce.map((food, idx) => (
                      <span 
                        key={idx} 
                        className="px-4 py-2 bg-rose-50/70 text-rose-700 font-semibold text-xs rounded-2xl border border-rose-100 hover:scale-105 hover:bg-rose-50 hover:shadow-md transition-all duration-200 cursor-default shadow-sm capitalize"
                      >
                        {food}
                      </span>
                    ))}
                  </div>
                </ResultCard>
              </div>
            )}

            {/* 5. Consultation Card */}
            <ResultCard title="Consultation Triage" icon={Stethoscope} delayClass="delay-300">
              <div className="flex flex-col gap-4">
                <div className="flex flex-col gap-3">
                  {analysisData.clinical_report.consultation.map((bullet, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-slate-600 text-sm leading-relaxed pl-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-brand-cyan mt-2 flex-shrink-0" />
                      <span>{bullet.replace("• ", "")}</span>
                    </div>
                  ))}
                </div>
                
                {/* Telehealth Call-to-action */}
                <div className="pt-3 border-t border-slate-50 mt-1">
                  <button 
                    onClick={() => setShowTelehealth(true)}
                    className="w-full flex items-center justify-center gap-2 bg-slate-50 hover:bg-brand-indigo/5 text-brand-indigo font-semibold text-sm py-3 rounded-xl transition-all duration-300 border border-slate-100 hover:border-brand-indigo/20 shadow-sm"
                  >
                    <Video className="w-4 h-4" />
                    Book Virtual Consultation
                  </button>
                </div>
              </div>
            </ResultCard>

            {/* 6. Technical Telemetry collapsed (Calibration 6) */}
            <div className="border border-slate-100 rounded-3xl bg-white overflow-hidden transition-all duration-300 animate-fade-in-up delay-300">
              <button 
                onClick={() => setShowTechnical(!showTechnical)}
                className="w-full flex items-center justify-between px-6 py-4 text-slate-500 hover:text-slate-700 transition-colors"
              >
                <span className="text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <HelpCircle className="w-3.5 h-3.5" />
                  Technical details
                </span>
                <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${showTechnical ? 'transform rotate-180' : ''}`} />
              </button>
              
              {showTechnical && (
                <div className="px-6 pb-6 pt-2 border-t border-slate-50 bg-slate-50/50">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                    <div>
                      <p className="text-slate-400 font-medium mb-0.5">Lesions count</p>
                      <p className="text-slate-700 font-bold text-sm">{analysisData.technical_summary.detected_lesions}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 font-medium mb-0.5">Dominant subclass</p>
                      <p className="text-slate-700 font-bold text-sm">{analysisData.technical_summary.dominant_pattern}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 font-medium mb-0.5">Peak confidence</p>
                      <p className="text-slate-700 font-bold text-sm">{(analysisData.technical_summary.peak_confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-slate-400 font-medium mb-0.5">Backend latency</p>
                      <p className="text-slate-700 font-bold text-sm">{analysisData.processing_time_ms}ms</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Reset button */}
            <button 
              onClick={handleReset}
              className="premium-button mt-6 w-full max-w-xs mx-auto text-center"
            >
              Analyze Another Photo
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-100 py-6 px-6 bg-white/50 text-center text-xs text-slate-400">
        <p>© 2026 Qyro skin-health platform. Calibrated AI Insights.</p>
      </footer>

      {/* Global Error popup */}
      {errorMsg && (
        <SafeErrorPopup 
          message={errorMsg} 
          onClose={() => setErrorMsg(null)} 
        />
      )}

      {/* Telehealth Modal */}
      {showTelehealth && (
        <TelehealthModal onClose={() => setShowTelehealth(false)} />
      )}
    </div>
  );
}
