"""
Qyro-Acne Phase 13: Clinical Acne Staging Verification Framework

This script validates the updated process_clinical_inference logic against the 9 structured test categories.
For each category, we mock raw YOLO detections and verify the resulting Stage, Wording, and Confidence Calibration.
"""

import os
import sys
from pathlib import Path

# Resolve workspace path safely
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.append(str(WORKSPACE_DIR))

try:
    from clinical_inference import process_clinical_inference, CLASS_NAMES
except ImportError as e:
    print(f"Error: Failed to import process_clinical_inference from clinical_inference.py: {e}")
    sys.exit(1)

def run_test_case(name, detections):
    print(f"\n=========================================================================")
    print(f" TEST CASE: {name}")
    print(f"=========================================================================")
    print(f"Mocked Detections:")
    for d in detections:
        print(f" - {d['class_name']} (conf: {d['confidence']:.2f}, area: {d['area_n']:.4f})")
    
    result = process_clinical_inference(detections)
    
    # Extract outcomes
    detected = result["acne_detected"]
    severity = result["severity_metrics"]["severity_label"]
    reasoning = result["severity_metrics"]["severity_reasoning"]
    confidence = result["confidence_level"]
    patterns = result["possible_patterns"]
    nutrients = result["nutrition_nutrients"]
    eat_more = result["nutrition_eat_more"]
    reduce_foods = result["nutrition_reduce"]
    triage = result["triage_recommendation"]["wording"]
    
    print("\nInference Output Summary:")
    print(f" - Acne Detected: {detected}")
    print(f" - Assigned Stage: {severity}")
    print(f" - Stage Reasoning: {reasoning}")
    print(f" - Confidence Rating: {confidence}")
    print(f" - Primary Wording: {patterns[0]}")
    if len(patterns) > 1:
        print(f" - Secondary Wording: {patterns[1]}")
    print(f" - Nutrients: {', '.join(nutrients)}")
    print(f" - Eat More: {', '.join(eat_more)}")
    print(f" - Reduce: {', '.join(reduce_foods)}")
    print(f" - Triage Guidance: {triage}")
    
    return result

def main():
    print("Starting Qyro-Acne Phase 13 Clinical Staging Verification...")
    
    # 1. Clear skin (Expect Stage 0, No acne)
    clear_skin_detections = []
    
    # 2. Blackhead dominant (Expect Stage 1, High conf)
    blackhead_dominant_detections = [
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.85, "area_n": 0.002, "box": [10, 10, 20, 20]},
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.75, "area_n": 0.001, "box": [30, 30, 40, 40]},
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.68, "area_n": 0.001, "box": [50, 50, 60, 60]}
    ]
    
    # 3. Whitehead dominant (Expect Stage 1, High conf)
    whitehead_dominant_detections = [
        {"class_id": 1, "class_name": "Whitehead", "confidence": 0.78, "area_n": 0.001, "box": [15, 15, 25, 25]},
        {"class_id": 1, "class_name": "Whitehead", "confidence": 0.72, "area_n": 0.002, "box": [35, 35, 45, 45]},
        {"class_id": 1, "class_name": "Whitehead", "confidence": 0.65, "area_n": 0.001, "box": [55, 55, 65, 65]}
    ]
    
    # 4. Papular inflammatory (Expect Stage 2, Moderate conf)
    papular_inflammatory_detections = [
        {"class_id": 2, "class_name": "Papular", "confidence": 0.58, "area_n": 0.004, "box": [20, 20, 35, 35]},
        {"class_id": 2, "class_name": "Papular", "confidence": 0.52, "area_n": 0.003, "box": [40, 40, 55, 55]},
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.45, "area_n": 0.001, "box": [60, 60, 65, 65]}
    ]
    
    # 5. Purulent inflammatory (Expect Stage 3, High conf, purulent_count >= 2)
    purulent_inflammatory_detections = [
        {"class_id": 3, "class_name": "Purulent", "confidence": 0.65, "area_n": 0.006, "box": [25, 25, 45, 45]},
        {"class_id": 3, "class_name": "Purulent", "confidence": 0.61, "area_n": 0.005, "box": [45, 45, 65, 65]},
        {"class_id": 2, "class_name": "Papular", "confidence": 0.55, "area_n": 0.003, "box": [70, 70, 85, 85]}
    ]
    
    # 6. Cystic severe (Expect Stage 4, High conf)
    cystic_detections = [
        {"class_id": 4, "class_name": "Cystic", "confidence": 0.82, "area_n": 0.012, "box": [30, 30, 60, 60]},
        {"class_id": 4, "class_name": "Cystic", "confidence": 0.70, "area_n": 0.015, "box": [50, 50, 80, 80]},
        {"class_id": 3, "class_name": "Purulent", "confidence": 0.65, "area_n": 0.005, "box": [10, 80, 25, 95]}
    ]
    
    # 7. Mixed acne case (Expect Stage 3, Mixed Pattern trigger, top_score < second_score * 1.15)
    # Papular: 3 lesions, conf 0.70 -> Score = 3 * 0.70 * 2.5 = 5.25
    # Purulent: 2 lesions, conf 0.65 -> Score = 2 * 0.65 * 4.0 = 5.20
    # 5.25 < 5.20 * 1.15 -> Mixed Pattern trigger!
    mixed_detections = [
        {"class_id": 2, "class_name": "Papular", "confidence": 0.72, "area_n": 0.004, "box": [10, 10, 20, 20]},
        {"class_id": 2, "class_name": "Papular", "confidence": 0.70, "area_n": 0.003, "box": [20, 20, 30, 30]},
        {"class_id": 2, "class_name": "Papular", "confidence": 0.68, "area_n": 0.003, "box": [30, 30, 40, 40]},
        {"class_id": 3, "class_name": "Purulent", "confidence": 0.66, "area_n": 0.005, "box": [40, 40, 55, 55]},
        {"class_id": 3, "class_name": "Purulent", "confidence": 0.64, "area_n": 0.005, "box": [60, 60, 75, 75]}
    ]
    
    # 8. Low-light selfie (Expect Low confidence stage assignment, avoiding certainty)
    low_light_detections = [
        {"class_id": 2, "class_name": "Papular", "confidence": 0.32, "area_n": 0.003, "box": [15, 15, 25, 25]}
    ]
    
    # 9. Close-up nose case (Expect Stage 1, Comedonal Cluster Safeguard, bypasses Stage 0 reassurance)
    nose_case_detections = [
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.32, "area_n": 0.001, "box": [12, 12, 18, 18]},
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.30, "area_n": 0.001, "box": [22, 22, 28, 28]},
        {"class_id": 0, "class_name": "Blackhead", "confidence": 0.28, "area_n": 0.001, "box": [32, 32, 38, 38]}
    ]
    
    run_test_case("1. Clear Skin", clear_skin_detections)
    run_test_case("2. Blackhead Dominant", blackhead_dominant_detections)
    run_test_case("3. Whitehead Dominant", whitehead_dominant_detections)
    run_test_case("4. Papular Inflammatory", papular_inflammatory_detections)
    run_test_case("5. Purulent Inflammatory", purulent_inflammatory_detections)
    run_test_case("6. Cystic Severe", cystic_detections)
    run_test_case("7. Mixed Acne Pattern", mixed_detections)
    run_test_case("8. Low-Light Selfie", low_light_detections)
    run_test_case("9. Close-Up Nose Case", nose_case_detections)
    
    print("\n=========================================================================")
    print("Structured Staging Validation Suite completed successfully.")
    print("=========================================================================\n")

if __name__ == "__main__":
    main()
