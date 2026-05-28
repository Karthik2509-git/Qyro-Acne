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
    
    # Upgraded Severity Labels & Thresholds (Patch 2)
    if final_severity_score <= 6.0:
        severity_label = "Mild"
        severity_reason = "Minimal non-inflammatory or early-stage lesions observed on the skin surface."
    elif final_severity_score <= 15.0:
        severity_label = "Moderate"
        severity_reason = "Moderate mix of non-inflammatory and inflammatory lesions observed, showing visible spread."
    else:
        severity_label = "Severe"
        severity_reason = "Widespread distribution of active, deep, or highly inflammatory characteristics."
        
    # ----------------------------------------------------
    # PATCH 1 & 5 — ACNE CERTAINTY GATE & REASSURANCE PATH
    # ----------------------------------------------------
    is_reassurance_triggered = False
    if total_detections == 0 or (highest_conf < 0.35 and final_severity_score <= 6.0 and total_detections <= 2):
        is_reassurance_triggered = True
        return {
            "acne_detected": False,
            "severity_metrics": {
                "severity_score": final_severity_score if total_detections > 0 else 0.0,
                "severity_label": "Minimal",
                "severity_reasoning": "Skin appears clear or generally under control with no significant active lesions."
            },
            "confidence_level": "High" if total_detections == 0 else "Low",
            "possible_patterns": [
                "Skin appears clear or generally under control."
            ],
            "lesion_summary": {CLASS_NAMES[i].lower(): class_counts[i] for i in range(5)},
            "wellness_guidance": {
                "nutrition_focus": ["General Wellness Focus", "Hydration"],
                "diet_guidance": {
                    "increase": ["Hydrating foods", "Balanced vitamins"],
                    "reduce": ["Excess processed foods"]
                },
                "skincare_focus": "Maintain your regular gentle skin cleansing routine."
            },
            "triage_recommendation": {
                "consultation_level": "Self-Care Guidance",
                "wording": "Continue maintaining healthy skincare habits."
            },
            "user_facing_flow": {
                "step_1_detection": "Skin appears clear or generally under control.",
                "step_2_severity": "Minimal",
                "step_3_pattern_analysis": "Subtle skin textures may be present.",
                "step_4_skin_guidance": [
                    "General wellness focus:",
                    "• hydration",
                    "• barrier-friendly skincare",
                    "• consistent skincare habits"
                ],
                "step_5_consultation": [
                    "• Continue maintaining healthy skincare habits."
                ]
            }
        }
        
    # ----------------------------------------------------
    # ACTIVE INFERENCE LOGIC (Acne Detected Path)
    # ----------------------------------------------------
    # Patch 5 - Confidence Level Logic
    if highest_conf >= 0.60:
        confidence_level = "High"
    elif highest_conf >= 0.35:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"
        
    # Determine dominant & secondary active classes sorted by count desc, then peak confidence desc
    active_classes = []
    for i in range(5):
        count = class_counts[i]
        if count > 0:
            peak_conf = max(class_confidences[i])
            active_classes.append((i, count, peak_conf))
    active_classes.sort(key=lambda x: (x[1], x[2]), reverse=True)
    
    top_cls = active_classes[0][0]
    top_conf = active_classes[0][2]
    sec_cls = active_classes[1][0] if len(active_classes) >= 2 else None
    sec_conf = active_classes[1][2] if len(active_classes) >= 2 else 0.0
    
    # 2. Uncertainty & Contradiction Handling (Dominant Confidence Wins)
    possible_patterns = []
    if sec_cls is not None:
        # Dominant rule: Is top class >25% stronger than the second class?
        if top_conf >= 1.25 * sec_conf:
            possible_patterns.append(
                f"Pattern analysis suggests: Predominantly {CLASS_NAMES[top_cls]} characteristics "
                f"with mild {CLASS_NAMES[sec_cls].lower()} tendency."
            )
        else:
            possible_patterns.append(
                f"Pattern analysis suggests: Co-dominant {CLASS_NAMES[top_cls]} and "
                f"{CLASS_NAMES[sec_cls].lower()} characteristics."
            )
    else:
        possible_patterns.append(f"Pattern analysis suggests: Predominantly {CLASS_NAMES[top_cls]} characteristics.")
        
    # ----------------------------------------------------
    # PATCH 3 — SMART GUIDANCE VARIATION ENGINE
    # ----------------------------------------------------
    GUIDANCE_FOCUS = {
        0: ["oil balance", "gentle pore care", "hydration"],                             # Blackhead
        1: ["gentle exfoliation awareness", "hydration", "pore maintenance"],             # Whitehead
        2: ["anti-inflammatory nutrition", "skin barrier support", "gentle skincare"],    # Papular
        3: ["inflammation calming", "avoid irritation", "skin barrier repair"],          # Purulent
        4: ["avoid irritation", "anti-inflammatory focus", "dermatologist consultation awareness"] # Cystic
    }
    
    # Blend top 2 dominant classes for step_4_skin_guidance
    blended_items = []
    top_items = GUIDANCE_FOCUS[top_cls]
    sec_items = GUIDANCE_FOCUS[sec_cls] if sec_cls is not None else []
    
    for i in range(max(len(top_items), len(sec_items))):
        if i < len(top_items) and top_items[i] not in blended_items:
            blended_items.append(top_items[i])
        if i < len(sec_items) and sec_items[i] not in blended_items:
            blended_items.append(sec_items[i])
            
    # Format Step 4 guidance bullets
    step_4_bullets = ["General wellness focus:"]
    for item in blended_items[:5]:
        step_4_bullets.append(f"• {item}")
        
    # Outer wellness guidance elements
    # 1. Base Nutrition Focus Name (Generalized by Burden)
    inflammatory_count = class_counts[2] + class_counts[3] + class_counts[4]
    if inflammatory_count <= 2 and severity_label == "Mild":
        nutrition_label = "Vitamin Balance & Hydration"
    elif inflammatory_count <= 5 or severity_label == "Moderate":
        nutrition_label = "Moderate Inflammatory Support"
    else:
        nutrition_label = "Anti-inflammatory Diet Emphasis"
        
    nutrition_focus = [nutrition_label, f"Focus: {GUIDANCE_FOCUS[top_cls][0].capitalize()}"]
    if sec_cls is not None:
        nutrition_focus.append(f"Secondary: {GUIDANCE_FOCUS[sec_cls][0].capitalize()}")
        
    # 2. Diet Increase/Reduce Catalog
    DIET_CATALOG = {
        0: { # Blackhead
            "increase": ["Zinc-rich seeds", "Hydrating greens"],
            "reduce": ["Highly processed oily foods", "Excess dairy"]
        },
        1: { # Whitehead
            "increase": ["Hydrating mineral water", "Antioxidant fruits"],
            "reduce": ["Deep-fried processed fast food"]
        },
        2: { # Papular
            "increase": ["Antioxidant-rich berries", "Omega-3 fatty acids"],
            "reduce": ["Refined sugars", "High-glycemic dairy"]
        },
        3: { # Purulent
            "increase": ["Green tea", "Turmeric/Anti-inflammatory spices"],
            "reduce": ["High-glycemic index foods", "Refined sugars"]
        },
        4: { # Cystic
            "increase": ["Omega-3 fatty acids", "Antioxidants", "Leafy green vegetables"],
            "reduce": ["Refined sugars", "Dairy whey protein", "Highly processed foods"]
        }
    }
    
    increase_diet = list(dict.fromkeys(DIET_CATALOG[top_cls]["increase"] + (DIET_CATALOG[sec_cls]["increase"] if sec_cls is not None else [])))
    reduce_diet = list(dict.fromkeys(DIET_CATALOG[top_cls]["reduce"] + (DIET_CATALOG[sec_cls]["reduce"] if sec_cls is not None else [])))
    
    # 3. Skincare Wording Focus
    SKINCARE_CATALOG = {
        0: "Recommend standard salicylic-friendly gentle skincare to dissolve sebum and clear pores.",
        1: "Focus on gentle skin renewal cleansers. Hydrate to support clear pore structure.",
        2: "Use gentle, non-comedogenic anti-inflammatory cleansers. Avoid physical face scrubs.",
        3: "Use mild, anti-inflammatory barrier cleansers. Avoid active scrub ingredients or peeling agents.",
        4: "Focus strictly on skin barrier protection with ultra-mild hydrating cleansers. Avoid physical face scrubs."
    }
    skincare_focus = SKINCARE_CATALOG[top_cls]

    # ----------------------------------------------------
    # PATCH 4 — DETECTION WORDING CALIBRATION
    # ----------------------------------------------------
    step_3_bullets = ["Pattern analysis suggests:"]
    for cls_id, count, peak_conf in active_classes:
        if peak_conf >= 0.60:
            step_3_bullets.append(f"• Predominantly {CLASS_NAMES[cls_id]} characteristics")
        elif peak_conf >= 0.35:
            step_3_bullets.append(f"• Mild {CLASS_NAMES[cls_id]} characteristics")
        else:
            step_3_bullets.append(f"• Possible {CLASS_NAMES[cls_id]} tendency")
            
    # ----------------------------------------------------
    # PATCH 5 & 8D — CONSULTATION TRIAGE (Soften trigger)
    # ----------------------------------------------------
    avg_cystic_conf = np.mean(class_confidences[4]) if len(class_confidences[4]) > 0 else 0.0
    is_cystic_heavy = (class_counts[4] >= 2 and avg_cystic_conf > 0.45)
    is_purulent_heavy = (class_counts[3] + class_counts[4] > 5)
    
    if severity_label == "Severe" or is_cystic_heavy or is_purulent_heavy:
        consultation_level = "Professional Consultation Recommended"
        consultation_wording = "A professional consultation with a certified dermatologist is recommended for a personalized treatment plan."
    elif severity_label == "Moderate":
        consultation_level = "Monitor + Routine Skincare"
        consultation_wording = "Routine skincare and weekly skin progression tracking is recommended."
    else:
        consultation_level = "Self-Care Guidance"
        consultation_wording = "Standard self-care skincare guidelines are appropriate for this skin pattern."
        
    step_5_bullets = [
        "• Monitor weekly.",
        "• Consider professional consultation if inflammation persists."
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
                "increase": increase_diet,
                "reduce": reduce_diet
            },
            "skincare_focus": skincare_focus
        },
        "triage_recommendation": {
            "consultation_level": consultation_level,
            "wording": consultation_wording
        },
        "user_facing_flow": {
            "step_1_detection": "Acne detected",
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
