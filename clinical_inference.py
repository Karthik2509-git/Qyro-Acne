"""
Qyro-Acne Phase 8: Hybrid Clinical Inference Engine

This script wraps the retrained YOLOv11s model outputs in a clinical reasoning layer,
generating structured, prototype-safe, and dermatologist-aligned wellness JSONs.
It implements the approved revisions:
1. "Pattern analysis suggests" wording
2. Dominant confidence wins (mixed confidence contradiction handling)
3. Severity normalization by bounding box image coverage %
4. Nutrition mapping by overall inflammatory burden
5. Calibrated dermatologist consultation triggers
6. Placeholder future-self pipeline architecture documentation

Usage:
    .venv\\Scripts\\python clinical_inference.py --image <image_path> [--output <json_output_path>]
"""

import os
import sys
import json
import argparse
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# Subclasses contiguously indexed 0-4
CLASS_NAMES = ['Blackhead', 'Whitehead', 'Papular', 'Purulent', 'Cystic']

## Upgraded Bbox Severity Weights (Patch 2)
SEVERITY_WEIGHTS = {
    0: 1.0,   # Blackhead
    1: 1.5,   # Whitehead
    2: 2.5,   # Papular (Upgraded from 2.0)
    3: 4.0,   # Purulent (Upgraded from 3.0)
    4: 6.0    # Cystic (Upgraded from 5.0)
}

def get_best_model_path():
    """Retrieve the retrained best weights path safely."""
    workspace_dir = Path(__file__).resolve().parent
    
    # Priority 1: qyro_yolo_v2-2 (most recent completed run)
    p1 = workspace_dir / "runs" / "qyro_yolo_v2-2" / "weights" / "best.pt"
    if p1.exists():
        return p1
        
    # Priority 2: qyro_yolo_v2
    p2 = workspace_dir / "runs" / "qyro_yolo_v2" / "weights" / "best.pt"
    if p2.exists():
        return p2
        
    # Priority 3: local PT weights
    p3 = workspace_dir / "yolo11s.pt"
    return p3

def parse_args():
    parser = argparse.ArgumentParser(description="Qyro Hybrid Clinical Inference Engine")
    parser.add_argument("--image", type=str, required=True,
                        help="Path to the raw clinical photo to analyze")
    parser.add_argument("--output", type=str, default=None,
                        help="Optional path to export the structured clinical JSON result")
    return parser.parse_args()

def analyze_skin(model, img_path):
    """Run YOLO inference and extract raw detections."""
    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(f"Source image not found: {img_path}")
        
    # Run YOLO prediction (internal confidence floor 0.15)
    results = model.predict(source=img_path, conf=0.15, iou=0.45, device=0, verbose=False)
    result = results[0]
    
    detections = []
    
    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        
        xyxy = box.xyxy[0].cpu().numpy()
        xywhn = box.xywhn[0].cpu().numpy()
        
        detections.append({
            "class_id": cls_id,
            "class_name": CLASS_NAMES[cls_id],
            "confidence": conf,
            "area_n": float(xywhn[2] * xywhn[3]),
            "box": [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
        })
        
    return detections

def process_clinical_inference(detections):
    """Orchestrate the reasoning layer over the raw YOLO detections."""
    total_detections = len(detections)
    
    # 1. Base Summary Calculations
    class_counts = {i: 0 for i in range(5)}
    class_confidences = {i: [] for i in range(5)}
    
    total_area_n = 0.0
    highest_conf = 0.0
    
    for d in detections:
        cls_id = d["class_id"]
        conf = d["confidence"]
        
        class_counts[cls_id] += 1
        class_confidences[cls_id].append(conf)
        total_area_n += d["area_n"]
        
        if conf > highest_conf:
            highest_conf = conf
            
    # Calculate base severity score
    base_severity = 0.0
    for cls_id, count in class_counts.items():
        base_severity += count * SEVERITY_WEIGHTS[cls_id]
        
    # Bbox Severity Area Normalization
    if total_area_n < 0.03:
        area_multiplier = 0.8   # Mild / sparse spread discount
    elif total_area_n <= 0.10:
        area_multiplier = 1.2   # Moderate spread multiplier
    else:
        area_multiplier = 1.5   # Widespread scale boost
        
    final_severity_score = float(round(base_severity * area_multiplier, 1))
    
    # ----------------------------------------------------
    # REFINEMENT 4 — CLOSE-UP NOSE SAFEGUARD
    # ----------------------------------------------------
    # If multiple blackhead detections cluster or dense comedonal pattern exists, 
    # we bypass reassurance to avoid missing nose blackheads in macro closeups.
    is_comedonal_cluster = (class_counts[0] >= 2) or (class_counts[0] + class_counts[1] >= 2)
    
    # ----------------------------------------------------
    # REFINEMENT 1 — STAGE 0 (MINIMAL / CLEAR SKIN) REASSURANCE PATH
    # ----------------------------------------------------
    is_reassurance_triggered = False
    if total_detections == 0 or (highest_conf < 0.35 and final_severity_score <= 6.0 and total_detections <= 2 and not is_comedonal_cluster):
        is_reassurance_triggered = True
        
        # Refinement 7 - Reasoning confidence level
        confidence_level = "High confidence stage assignment" if total_detections == 0 else "Low confidence / ambiguous"
        
        return {
            "acne_detected": False,
            "severity_metrics": {
                "severity_score": final_severity_score if total_detections > 0 else 0.0,
                "severity_label": "Stage 0",
                "severity_reasoning": "Skin appears generally under control."
            },
            "confidence_level": confidence_level,
            "possible_patterns": [
                "Skin appears generally under control."
            ],
            "lesion_summary": {CLASS_NAMES[i].lower(): class_counts[i] for i in range(5)},
            "wellness_guidance": {
                "nutrition_focus": ["General Wellness Focus", "Hydration Support"],
                "diet_guidance": {
                    "increase": ["consider increasing hydrating greens", "consider increasing water-rich fruits"],
                    "reduce": ["excessive refined sugar", "excessive processed foods"]
                },
                "skincare_focus": "Maintain consistent, barrier-friendly skincare habits."
            },
            "nutrition_nutrients": ["Vitamins A, C, E", "Zinc", "Water-soluble Fiber"],
            "nutrition_eat_more": ["consider increasing leafy greens", "consider increasing antioxidant-rich fruits", "consider increasing water-rich foods"],
            "nutrition_reduce": ["excessive refined sugar", "excessive ultra-processed foods"],
            "triage_recommendation": {
                "consultation_level": "Self-Care Guidance",
                "wording": "Maintain healthy, consistent skincare habits."
            },
            "user_facing_flow": {
                "step_1_detection": "Skin appears generally under control.",
                "step_2_severity": "Stage 0",
                "step_3_pattern_analysis": [
                    "Skin appears generally under control.",
                    "• No significant active acne characteristics observed.",
                    "• Maintain a consistent, gentle daily cleansing routine."
                ],
                "step_4_skin_guidance": [
                    "General wellness focus:",
                    "• consistent hydration",
                    "• barrier-friendly skincare",
                    "• consistent cleansing habits"
                ],
                "step_5_consultation": [
                    "• Maintain healthy skincare habits.",
                    "• This wellness guidance is educational and should not replace professional dermatological consultation."
                ]
            }
        }
        
    # ----------------------------------------------------
    # ACTIVE INFERENCE LOGIC (Acne Detected Path: Stages 1-4)
    # ----------------------------------------------------
    # Refinement 7 - Reasoning Confidence Level Mapping
    if highest_conf >= 0.60:
        confidence_level = "High confidence stage assignment"
        pattern_prefix = "Observed characteristics align with:"
    elif highest_conf >= 0.35:
        confidence_level = "Moderate confidence"
        pattern_prefix = "Pattern analysis suggests:"
    else:
        confidence_level = "Low confidence / ambiguous"
        pattern_prefix = "May show characteristics of:"
        
    # Calculate Subclass Weighted Scoring
    subclass_scores = {}
    for i in range(5):
        count = class_counts[i]
        if count > 0:
            mean_conf = np.mean(class_confidences[i])
            subclass_scores[i] = count * mean_conf * SEVERITY_WEIGHTS[i]
        else:
            subclass_scores[i] = 0.0
            
    active_classes_by_score = [(i, class_counts[i], max(class_confidences[i]), subclass_scores[i]) for i in range(5) if class_counts[i] > 0]
    active_classes_by_score.sort(key=lambda x: x[3], reverse=True)
    
    top_cls = active_classes_by_score[0][0]
    top_conf = active_classes_by_score[0][2]
    top_score = active_classes_by_score[0][3]
    
    if len(active_classes_by_score) >= 2:
        sec_cls = active_classes_by_score[1][0]
        sec_conf = active_classes_by_score[1][2]
        second_score = active_classes_by_score[1][3]
    else:
        sec_cls = None
        sec_conf = 0.0
        second_score = 0.0
        
    # ----------------------------------------------------
    # REFINEMENT 3 — DOMINANCE THRESHOLD & MIXED PATTERN
    # ----------------------------------------------------
    is_mixed_pattern = (sec_cls is not None) and (top_score < second_score * 1.15)
    
    # ----------------------------------------------------
    # WEIGHTED STAGE DETERMINATION (Phases 13A, 13B & Refinement 2)
    # ----------------------------------------------------
    cystic_count = class_counts[4]
    cystic_peak_conf = max(class_confidences[4]) if cystic_count > 0 else 0.0
    purulent_count = class_counts[3]
    purulent_peak_conf = max(class_confidences[3]) if purulent_count > 0 else 0.0
    papular_count = class_counts[2]
    
    total_inflammatory = papular_count + purulent_count + cystic_count
    
    # Robust Stage 4 Trigger: Cystic dominant AND significant activity
    is_cystic_heavy = (cystic_count >= 2) or (cystic_peak_conf >= 0.50) or (total_inflammatory >= 3)
    is_cystic_dominant = (top_cls == 4) and is_cystic_heavy
    
    # Robust Stage 3 Trigger (Refinement 2): Purulent count >= 2, or purulent peak >= 0.50, or papular + purulent mix, AND not Cystic dominant
    has_purulent_activity = (purulent_count >= 2) or (purulent_peak_conf >= 0.50) or (papular_count >= 1 and purulent_count >= 1)
    is_stage_3 = has_purulent_activity and (not is_cystic_dominant)
    
    # Stage 2 Trigger: Papular dominant or Cystic/Purulent fallback
    is_stage_2 = (not is_cystic_dominant) and (not is_stage_3) and (top_cls in [2, 4] or (top_cls == 3 and not is_stage_3))
    
    # Stage 1 Trigger: Comedonal dominant or only comedonal present
    is_stage_1 = (not is_cystic_dominant) and (not is_stage_3) and (not is_stage_2)
    
    if is_cystic_dominant:
        severity_label = "Stage 4"
        severity_reason = "Advanced inflammatory acne characteristics may be present with deep structural lesion activity."
        patient_wording = "Advanced inflammatory acne characteristics may be present."
    elif is_stage_3:
        severity_label = "Stage 3"
        severity_reason = "Active inflammatory acne patterns with visible purulent or pustular lesions."
        patient_wording = "Active inflammatory acne patterns may be present."
    elif is_stage_2:
        severity_label = "Stage 2"
        severity_reason = "Mild to moderate inflammatory acne characterized by reddish papular bumps."
        patient_wording = "Mild inflammatory acne characteristics may be observed."
    else:
        severity_label = "Stage 1"
        severity_reason = "Non-inflammatory comedonal pattern consisting of pore congestion, blackheads, or whiteheads."
        patient_wording = "Comedonal acne characteristics may be present."
        
    # Determine secondary pattern detail (incorporating Mixed Pattern Refinement 3 and Phase 13B Hybrids)
    if is_mixed_pattern:
        is_top_inflammatory = (top_cls >= 2)
        is_sec_inflammatory = (sec_cls >= 2) if sec_cls is not None else False
        
        if is_top_inflammatory and is_sec_inflammatory:
            secondary_wording = "Mixed inflammatory characteristics observed."
        elif (not is_top_inflammatory) and (not is_sec_inflammatory):
            secondary_wording = "Mixed comedonal characteristics observed."
        else:
            secondary_wording = "Mixed comedonal and inflammatory characteristics observed."
    else:
        if severity_label == "Stage 1" and (class_counts[0] > 0 and class_counts[1] > 0):
            secondary_wording = "oil congestion pattern."
        elif severity_label == "Stage 3" and (papular_count > 0 and purulent_count > 0):
            secondary_wording = "papular inflammation observed."
        elif severity_label == "Stage 4" and purulent_count > 0:
            secondary_wording = "soft consultation recommendation."
        else:
            secondary_wording = f"secondary {CLASS_NAMES[sec_cls].lower()} characteristics present." if sec_cls is not None else ""
            
    possible_patterns = [f"{pattern_prefix} {patient_wording}"]
    if secondary_wording:
        possible_patterns.append(f"Secondary: {secondary_wording}")
        
    # ----------------------------------------------------
    # REFINEMENT 6 — NUTRITION DATABASE AND DYNAMIC ENGINE
    # ----------------------------------------------------
    NUTRITION_DATABASE = {
        "Stage 1": {
            "nutrients": ["Zinc", "Omega-3", "Vitamin A", "Linoleic Acid", "Hydration factors"],
            "eat_more": ["consider increasing pumpkin seeds", "consider increasing walnuts", "consider increasing leafy greens", "consider increasing water-rich fruits like cucumber"],
            "reduce": ["excessive refined sugar", "high-glycemic processed snacks", "excessive dairy products"]
        },
        "Stage 2": {
            "nutrients": ["Omega-3 fatty acids", "Zinc", "Vitamin C", "Antioxidants", "Green tea catechins"],
            "eat_more": ["consider increasing berries", "consider increasing spinach", "consider increasing turmeric-infused meals", "consider increasing flaxseeds", "consider increasing green tea"],
            "reduce": ["excessive highly spicy processed foods", "refined sugars", "oily fast foods"]
        },
        "Stage 3": {
            "nutrients": ["Zinc", "Probiotics", "Vitamin E", "Omega-3", "Selenium"],
            "eat_more": ["consider increasing fermented foods like yogurt or kefir", "consider increasing almonds", "consider increasing avocados", "consider increasing rich leafy vegetables"],
            "reduce": ["refined white flour", "sugary desserts", "excessive greasy fried foods"]
        },
        "Stage 4": {
            "nutrients": ["Zinc", "Omega-3", "Vitamin D3", "Vitamin A", "Anti-inflammatory bioactives"],
            "eat_more": ["consider increasing lean plant-based proteins", "consider increasing zinc-rich seeds", "consider increasing healthy fats like olive oil", "consider increasing cruciferous vegetables like broccoli"],
            "reduce": ["whey protein isolates", "high-glycemic index foods", "excessive dairy products"]
        }
    }
    
    nutrients = NUTRITION_DATABASE[severity_label]["nutrients"]
    eat_more = NUTRITION_DATABASE[severity_label]["eat_more"]
    reduce_list = NUTRITION_DATABASE[severity_label]["reduce"]
    
    # ----------------------------------------------------
    # SMART GUIDANCE & SKINCARE ENGINE
    # ----------------------------------------------------
    SKINCARE_CATALOG = {
        "Stage 1": "Patterns may benefit from oil-balancing and gentle pore exfoliating routines, prioritizing hydration.",
        "Stage 2": "Patterns could respond well to soothing, non-comedogenic cleansers that protect the skin barrier and reduce friction.",
        "Stage 3": "Patterns could respond well to mild anti-inflammatory cleansers and barrier-repair creams, avoiding any physical scrubs.",
        "Stage 4": "Patterns may benefit from deeply soothing skin barrier protection using ultra-mild hydrating cleansers and avoiding active picking."
    }
    
    GUIDANCE_FOCUS = {
        "Stage 1": ["pore congestion management", "oil balance support", "gentle exfoliation", "optimal hydration"],
        "Stage 2": ["mild inflammatory control", "skin barrier protection", "gentle soothing skincare", "minimizing skin friction"],
        "Stage 3": ["active inflammation calming", "microbial balance support", "barrier repair care", "sanitizing pillowcases/screens"],
        "Stage 4": ["highly soothing barrier creams", "avoiding hot water face washes", "non-irritating hydration", "deep skin barrier protection"]
    }
    
    step_4_bullets = ["General wellness focus:"]
    for item in GUIDANCE_FOCUS[severity_label]:
        step_4_bullets.append(f"• {item}")
        
    nutrition_label = f"Clinical Staging: {severity_label} Wellness"
    nutrition_focus = [nutrition_label, f"Focus: {GUIDANCE_FOCUS[severity_label][0].capitalize()}"]
    if secondary_wording:
        nutrition_focus.append(f"Secondary: {secondary_wording.capitalize()}")
        
    skincare_focus = SKINCARE_CATALOG[severity_label]
    
    # Format Step 3 Wording for UI
    step_3_bullets = [pattern_prefix]
    step_3_bullets.append(f"• {patient_wording}")
    if secondary_wording:
        step_3_bullets.append(f"• Secondary: {secondary_wording}")
        
    # ----------------------------------------------------
    # CONSULTATION TRIAGE
    # ----------------------------------------------------
    if severity_label == "Stage 4":
        consultation_level = "Professional Consultation Recommended"
        triage_wording = "Professional dermatology consultation could be beneficial for deep cystic concerns."
    elif severity_label == "Stage 3":
        consultation_level = "Professional Consultation Recommended"
        triage_wording = "Professional dermatology consultation could be beneficial for active inflammatory lesions."
    elif severity_label == "Stage 2":
        consultation_level = "Monitor + Routine Skincare"
        triage_wording = "Consider standard routine adjustments and professional consultation if inflammatory patterns persist."
    else:
        consultation_level = "Self-Care Guidance"
        triage_wording = "Monitor skin progression weekly and support with gentle comedonal skincare."
        
    step_5_bullets = [
        f"• {triage_wording}",
        "• This wellness guidance is educational and should not replace professional dermatological consultation."
    ]
    
    # Output structure
    output_json = {
        "acne_detected": True,
        "severity_metrics": {
            "severity_score": final_severity_score,
            "severity_label": severity_label,
            "severity_reasoning": severity_reason
        },
        "confidence_level": confidence_level,
        "possible_patterns": possible_patterns,
        "lesion_summary": {CLASS_NAMES[i].lower(): class_counts[i] for i in range(5)},
        "wellness_guidance": {
            "nutrition_focus": nutrition_focus,
            "diet_guidance": {
                "increase": eat_more,
                "reduce": reduce_list
            },
            "skincare_focus": skincare_focus
        },
        "nutrition_nutrients": nutrients,
        "nutrition_eat_more": eat_more,
        "nutrition_reduce": reduce_list,
        "triage_recommendation": {
            "consultation_level": consultation_level,
            "wording": triage_wording
        },
        "user_facing_flow": {
            "step_1_detection": "Acne characteristics observed",
            "step_2_severity": severity_label,
            "step_3_pattern_analysis": step_3_bullets,
            "step_4_skin_guidance": step_4_bullets,
            "step_5_consultation": step_5_bullets
        }
    }
    return output_json

def main():
    args = parse_args()
    
    # 1. Initialize evaluation directories if needed
    init_folders()
    
    # 2. Get and load model weights
    model_path = get_best_model_path()
    print(f"Loading retrained YOLOv11s model from {model_path}...")
    try:
        model = YOLO(str(model_path))
    except Exception as e:
        print(f"Critical Error: Failed to load model weights: {e}")
        sys.exit(1)
        
    # 3. Process image
    img_path = Path(args.image)
    if not img_path.exists():
        print(f"Error: Target clinical photo not found: {args.image}")
        sys.exit(1)
        
    print(f"Running hybrid clinical inference on {img_path.name}...")
    try:
        detections = analyze_skin(model, img_path)
        inference_result = process_clinical_inference(detections)
        
        # Output JSON result
        json_output = json.dumps(inference_result, indent=2)
        print("\n=========================================================================")
        print("                        STRUCTURED CLINICAL INTERPRETATION               ")
        print("=========================================================================")
        print(json_output)
        print("=========================================================================\n")
        
        # Save output if path is specified
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w") as f:
                f.write(json_output)
            print(f"Structured clinical reasoning JSON successfully saved to {out_path}")
            
    except Exception as e:
        print(f"Error during skin analysis: {e}")
        sys.exit(1)

def init_folders():
    """Ensure evaluation directories exist."""
    eval_dir = Path(__file__).resolve().parent / "evaluation"
    for d in ["raw_images", "predictions", "failure_cases", "strong_cases"]:
        (eval_dir / d).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    main()
