import React, { useState, useRef, useEffect } from 'react';
import { Camera, RefreshCw, AlertCircle, CheckCircle, VideoOff, Info, Sparkles } from 'lucide-react';

export default function LiveCamera({ onFileSelected }) {
  const [step, setStep] = useState('guide'); // 'guide', 'camera', 'preview'
  const [stream, setStream] = useState(null);
  const [facingMode, setFacingMode] = useState('user'); // 'user' (front) or 'environment' (back)
  const [errorMsg, setErrorMsg] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Stop camera stream when component unmounts
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stream]);

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const startCamera = async (mode = facingMode) => {
    stopCamera();
    setErrorMsg(null);
    setStep('camera');

    const constraints = {
      video: {
        facingMode: mode,
        width: { ideal: 1080 },
        height: { ideal: 1080 },
        aspectRatio: 1
      },
      audio: false
    };

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error("Camera access failed:", err);
      setErrorMsg("Failed to access camera. Please ensure camera permissions are granted.");
      setStep('guide');
    }
  };

  const toggleCamera = () => {
    const nextMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(nextMode);
    if (step === 'camera') {
      startCamera(nextMode);
    }
  };

  const captureFrame = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      // Sync sizes
      const size = Math.min(video.videoWidth, video.videoHeight);
      canvas.width = size;
      canvas.height = size;

      // Center crop to a square
      const sx = (video.videoWidth - size) / 2;
      const sy = (video.videoHeight - size) / 2;

      ctx.drawImage(video, sx, sy, size, size, 0, 0, size, size);
      
      const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
      setCapturedImage(dataUrl);
      stopCamera();
      setStep('preview');
    }
  };

  const handleAnalyze = () => {
    if (capturedImage) {
      // Convert Data URL to file blob
      fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], "qyro_scan.jpg", { type: "image/jpeg" });
          onFileSelected(file);
        });
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    startCamera();
  };

  return (
    <div className="w-full max-w-lg mx-auto bg-white border border-slate-100 rounded-3xl shadow-xl overflow-hidden transition-all duration-300 relative">
      
      {/* Hidden Canvas for snapshooting */}
      <canvas ref={canvasRef} className="hidden" />

      {/* STEP 1: ELEGANT SCANNING GUIDE OVERLAY (Refinement 5) */}
      {step === 'guide' && (
        <div className="p-8 flex flex-col gap-6 animate-fade-in-up">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-brand-indigo/5 rounded-full flex items-center justify-center text-brand-indigo mx-auto mb-3">
              <Camera className="w-6 h-6 animate-pulse" />
            </div>
            <h2 className="text-xl font-extrabold text-slate-800 tracking-tight">Live Skin Scan Setup</h2>
            <p className="text-brand-muted text-xs">For maximum perceived accuracy and clinical usefulness, please follow the guidelines:</p>
          </div>

          <div className="bg-slate-50 border border-slate-100 rounded-2xl p-5 space-y-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-slate-800">Ensure good lighting</p>
                <p className="text-[11px] text-slate-400">Position yourself near a bright natural light or well-lit mirror.</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-slate-800">Keep face centered</p>
                <p className="text-[11px] text-slate-400">Align your face inside the target frame during the scan.</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-slate-800">Avoid heavy shadows</p>
                <p className="text-[11px] text-slate-400">Ensure smooth frontal lighting without harsh side shadows.</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-bold text-slate-800">Hold camera steady</p>
                <p className="text-[11px] text-slate-400">Minimize movement when clicking the shutter button.</p>
              </div>
            </div>
          </div>

          {errorMsg && (
            <div className="flex items-center gap-2 bg-rose-50 border border-rose-100 text-rose-600 text-xs px-4 py-3 rounded-xl">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <button 
            onClick={() => startCamera()}
            className="premium-button w-full flex items-center justify-center gap-2 hover:scale-[1.01] shadow-lg shadow-brand-indigo/10 py-3.5"
          >
            <Sparkles className="w-4 h-4" />
            Start Clinical Scan
          </button>
        </div>
      )}

      {/* STEP 2: LIVE CAMERA PREVIEW WITH CLINICAL MASK */}
      {step === 'camera' && (
        <div className="relative aspect-square w-full bg-slate-950 overflow-hidden flex items-center justify-center">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            className="w-full h-full object-cover transform -scale-x-100"
          />

          {/* Premium target alignment mask */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            {/* Dark vignette boundaries */}
            <div className="absolute inset-0 bg-black/40"></div>
            
            {/* Cutout circular scanning mask */}
            <div className="w-[70%] h-[70%] rounded-full border-2 border-brand-indigo/80 border-dashed bg-transparent shadow-[0_0_0_9999px_rgba(15,23,42,0.65)] relative flex items-center justify-center">
              {/* Target lines / bracket animations */}
              <div className="absolute inset-[-4px] border-[3px] border-transparent border-t-brand-indigo border-b-brand-indigo rounded-full animate-spin [animation-duration:10s]"></div>
              <span className="text-[9px] font-bold text-white bg-slate-800/80 border border-slate-700 px-2 py-1 rounded-full uppercase tracking-wider mb-auto mt-4 backdrop-blur-sm shadow-md">
                Align Skin Zone
              </span>
            </div>
          </div>

          {/* Top Controls Overlay */}
          <div className="absolute top-4 left-4 right-4 flex items-center justify-between z-20">
            <button 
              onClick={() => { stopCamera(); setStep('guide'); }}
              className="text-xs font-semibold text-white bg-slate-900/60 hover:bg-slate-900/80 border border-slate-700/40 px-3.5 py-2 rounded-xl backdrop-blur-md transition-colors"
            >
              Cancel
            </button>
            <button 
              onClick={toggleCamera}
              className="w-9 h-9 rounded-full bg-slate-900/60 hover:bg-slate-900/80 border border-slate-700/40 flex items-center justify-center text-white backdrop-blur-md transition-all duration-200"
              title="Switch Camera (Front/Back)"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {/* Bottom Capture Panel */}
          <div className="absolute bottom-6 left-0 right-0 flex justify-center z-20">
            <button 
              onClick={captureFrame}
              className="w-16 h-16 rounded-full border-4 border-white/60 bg-white hover:bg-slate-50 flex items-center justify-center shadow-2xl active:scale-95 transition-all duration-150"
            >
              <div className="w-12 h-12 rounded-full bg-brand-indigo/90 flex items-center justify-center text-white">
                <Camera className="w-5 h-5" />
              </div>
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: PREVIEW SNAPSHOT & CONFIRM ANALYSIS */}
      {step === 'preview' && capturedImage && (
        <div className="flex flex-col animate-fade-in-up">
          <div className="relative aspect-square w-full bg-slate-950 overflow-hidden flex items-center justify-center">
            <img 
              src={capturedImage} 
              alt="Skin Scan Snapshot" 
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 left-4">
              <span className="text-[9px] font-bold text-emerald-600 bg-emerald-50 border border-emerald-100 px-3 py-1.5 rounded-full uppercase tracking-wider shadow-sm backdrop-blur-sm">
                Scan Captured
              </span>
            </div>
          </div>

          {/* Review Actions Panel */}
          <div className="p-6 bg-slate-50 border-t border-slate-100 flex flex-col sm:flex-row gap-3">
            <button 
              onClick={handleRetake}
              className="flex-1 border border-slate-200 hover:border-slate-300 hover:bg-white text-slate-700 font-semibold py-3.5 rounded-2xl transition-all duration-200 text-sm shadow-sm"
            >
              Retake Scan
            </button>
            <button 
              onClick={handleAnalyze}
              className="flex-1 bg-brand-indigo hover:bg-brand-indigo/95 text-white font-semibold py-3.5 rounded-2xl transition-all duration-200 text-sm shadow-lg shadow-brand-indigo/10"
            >
              Analyze Scan
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
