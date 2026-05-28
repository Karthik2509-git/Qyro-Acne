import time
import shutil
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config.settings import settings
from app.services.yolo_service import YOLOService
from app.services.image_preprocessing import validate_image_file, preprocess_image
from app.services.inference_service import execute_clinical_inference
from app.models.response_models import AnalyzeResponseModel

logger = logging.getLogger("qyro_backend")

router = APIRouter()

@router.get("/health", summary="API Service Health Check")
async def health_check():
    """
    Returns API health status and verifying YOLO Singleton initialization.
    """
    yolo = YOLOService.get_instance()
    model_loaded = yolo.model is not None
    
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "model_version": settings.APP_VERSION
    }

@router.post("/analyze", response_model=AnalyzeResponseModel, summary="Run skin photo hybrid inference")
async def analyze_photo(image: UploadFile = File(...)):
    """
    Upload clinical photo, pre-process, run prediction and calibrated reasoning layer, returning clean API JSONs.
    """
    start_time = time.time()
    
    # 1. Save upload temporarily
    temp_path = settings.UPLOAD_DIR / f"temp_{int(start_time)}_{image.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        logger.error(f"Failed to write uploaded file buffer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "UPLOAD_FAILURE",
                "message": "Failed to save file upload."
            }
        )
        
    try:
        # 2. Image Safety Validation
        validate_image_file(temp_path, image.filename)
        
        # 3. Image Preprocessing (Safe Resizing)
        preprocess_image(temp_path)
        
        # 4. Singelton YOLO Inference
        yolo = YOLOService.get_instance()
        yolo_result = yolo.predict(temp_path)
        
        # 5. Clinical Inference Reasoning Wrapper
        inference_result, raw_detections = execute_clinical_inference(yolo_result)
        
    except HTTPException as he:
        # Re-raise HTTPExceptions cleanly so our global handler catches them
        if temp_path.exists():
            temp_path.unlink()
        raise he
    except Exception as e:
        # Fallback to internal inference failure (500)
        logger.error(f"Unexpected exception during skin analysis pipeline: {e}")
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INFERENCE_FAILURE",
                "message": "An internal error occurred during clinical inference."
            }
        )
        
    # Remove temporary upload file
    if temp_path.exists():
        temp_path.unlink()
        
    # 6. Separate Clinical Report vs Technical Summary
    # Extract clinical outcomes
    acne_detected = inference_result.get("acne_detected", False)
    
    if acne_detected:
        severity = inference_result.get("severity_metrics", {}).get("severity_label", "Mild")
        pattern_analysis = inference_result.get("user_facing_flow", {}).get("step_3_pattern_analysis", [])
        skin_guidance = inference_result.get("user_facing_flow", {}).get("step_4_skin_guidance", [])
        consultation = inference_result.get("user_facing_flow", {}).get("step_5_consultation", [])
    else:
        # Reassurance override values
        severity = "Minimal"
        pattern_analysis = [inference_result.get("user_facing_flow", {}).get("step_3_pattern_analysis", "Subtle skin textures may be present.")]
        skin_guidance = inference_result.get("user_facing_flow", {}).get("step_4_skin_guidance", [])
        consultation = inference_result.get("user_facing_flow", {}).get("step_5_consultation", [])
        
    # Compile technical metadata
    lesions = inference_result.get("lesion_summary", {})
    active_lesions = {k: v for k, v in lesions.items() if v > 0}
    dominant_pattern = max(active_lesions, key=active_lesions.get).capitalize() if active_lesions else "None"
    
    detected_lesions = sum(lesions.values())
    peak_confidence = float(max([d["confidence"] for d in raw_detections])) if raw_detections else 0.0
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    return {
        "success": True,
        "processing_time_ms": processing_time_ms,
        "clinical_report": {
            "acne_detected": acne_detected,
            "severity": severity,
            "analysis_confidence": inference_result.get("confidence_level", "High"),
            "pattern_analysis": pattern_analysis,
            "skin_guidance": skin_guidance,
            "consultation": consultation
        },
        "technical_summary": {
            "detected_lesions": detected_lesions,
            "dominant_pattern": dominant_pattern,
            "peak_confidence": peak_confidence
        }
    }
