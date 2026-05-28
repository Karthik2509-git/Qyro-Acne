import os
import argparse
import csv
import shutil
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO

# Classes shifted from 1-5 to contiguously 0-4
CLASS_NAMES = ['Blackhead', 'Whitehead', 'Papular', 'Purulent', 'Cystic']

def get_best_model_path():
    """Retrieve the active retrained weights path, falling back robustly."""
    workspace_dir = Path(__file__).resolve().parent.parent
    
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

def init_folders():
    """Programmatically initialize the qualitative validation directory layout."""
    eval_dir = Path(__file__).resolve().parent.parent / "evaluation"
    subdirs = ["raw_images", "predictions", "failure_cases", "strong_cases"]
    
    folders = {}
    for d in subdirs:
        p = eval_dir / d
        p.mkdir(parents=True, exist_ok=True)
        folders[d] = p
        
    return eval_dir, folders

def parse_args():
    parser = argparse.ArgumentParser(description="Qyro-Acne Phase 7A Real-World Model Validation")
    parser.add_argument("--input", type=str, default="evaluation/raw_images",
                        help="Path to input image file or directory containing raw clinical photos")
    parser.add_argument("--conf", type=float, default=0.25,
                        help="Default confidence threshold for predictions (default: 0.25)")
    parser.add_argument("--iou", type=float, default=0.45,
                        help="Default IoU threshold for Non-Maximum Suppression (default: 0.45)")
    parser.add_argument("--class-filter", type=str, default="0,1,2,3,4",
                        help="Comma-separated class indices to keep (default: '0,1,2,3,4')")
    parser.add_argument("--save-annotated", action="store_true", default=True,
                        help="Save prediction images with bounding boxes drawn")
    parser.add_argument("--conf-sweep", type=str, default=None,
                        help="Comma-separated list of confidence thresholds to run sweep analysis")
    return parser.parse_args()

def process_single_image(model, img_path, conf_threshold, iou_threshold, class_filter_list):
    """Run model inference on a single image and return detailed prediction structures."""
    # Source image dimensions
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    h_img, w_img = img.shape[:2]
    
    # Run YOLO prediction
    results = model.predict(source=img_path, conf=conf_threshold, iou=iou_threshold, device=0, verbose=False)
    result = results[0]
    
    predictions = []
    
    # Image level metrics initialization
    image_summary = {
        "image_name": img_path.name,
        "total_detections": 0,
        "highest_confidence": 0.0,
        "dominant_class": "None",
        "blackhead_count": 0,
        "whitehead_count": 0,
        "papular_count": 0,
        "purulent_count": 0,
        "cystic_count": 0,
        "possible_false_positive": False
    }
    
    class_counts = {i: 0 for i in range(5)}
    
    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        
        # Apply class-specific filters
        if cls_id not in class_filter_list:
            continue
            
        # Parse boundary boxes (normalized & absolute)
        xyxy = box.xyxy[0].cpu().numpy()
        xywhn = box.xywhn[0].cpu().numpy()
        w_box_n, h_box_n = xywhn[2], xywhn[3]
        area_box_n = w_box_n * h_box_n
        
        xmin, ymin, xmax, ymax = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
        
        # 1. False Positive Skin Filter (Confidence < 0.25 and BBox Area > 12% image area)
        is_false_positive = False
        if conf < 0.25 and area_box_n > 0.12:
            is_false_positive = True
            image_summary["possible_false_positive"] = True
            
        class_counts[cls_id] += 1
        image_summary["total_detections"] += 1
        
        if conf > image_summary["highest_confidence"]:
            image_summary["highest_confidence"] = conf
            
        predictions.append({
            "cls_id": cls_id,
            "class_name": CLASS_NAMES[cls_id],
            "confidence": conf,
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
            "area_n": area_box_n,
            "is_false_positive": is_false_positive
        })
        
    # Summarize image-level details
    if image_summary["total_detections"] > 0:
        image_summary["blackhead_count"] = class_counts[0]
        image_summary["whitehead_count"] = class_counts[1]
        image_summary["papular_count"] = class_counts[2]
        image_summary["purulent_count"] = class_counts[3]
        image_summary["cystic_count"] = class_counts[4]
        
        # Determine dominant class
        active_counts = {CLASS_NAMES[i]: class_counts[i] for i in range(5) if class_counts[i] > 0}
        if active_counts:
            image_summary["dominant_class"] = max(active_counts, key=active_counts.get)
            
    return predictions, image_summary, result

def run_standard_evaluation(model, img_files, conf, iou, class_filter, folders):
    """Run qualitative validation at a fixed confidence and write detailed CSV logs."""
    report_path = folders["predictions"].parent / "evaluation_report.csv"
    print(f"Initializing standard validation. Outputting manifest to {report_path}...")
    
    headers = [
        "image_name", "bbox_index", "class_id", "class_name", "confidence",
        "xmin", "ymin", "xmax", "ymax", "total_detections", "highest_confidence",
        "dominant_class", "blackhead_count", "whitehead_count", "papular_count",
        "purulent_count", "cystic_count", "possible_false_positive"
    ]
    
    with open(report_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        total_detections_all = 0
        total_images_flagged = 0
        
        for img_path in img_files:
            process_res = process_single_image(model, img_path, conf, iou, class_filter)
            if not process_res:
                continue
                
            predictions, summary, result = process_res
            total_detections_all += summary["total_detections"]
            if summary["possible_false_positive"]:
                total_images_flagged += 1
                
            # Log bounding boxes to CSV
            if len(predictions) == 0:
                # No detections: write single background row
                writer.writerow([
                    img_path.name, "", "", "", "", "", "", "", "",
                    0, 0.0, "None", 0, 0, 0, 0, 0, "False"
                ])
            else:
                for idx, p in enumerate(predictions):
                    writer.writerow([
                        img_path.name, idx, p["cls_id"], p["class_name"], f"{p['confidence']:.4f}",
                        f"{p['xmin']:.1f}", f"{p['ymin']:.1f}", f"{p['xmax']:.1f}", f"{p['ymax']:.1f}",
                        summary["total_detections"], f"{summary['highest_confidence']:.4f}",
                        summary["dominant_class"], summary["blackhead_count"], summary["whitehead_count"],
                        summary["papular_count"], summary["purulent_count"], summary["cystic_count"],
                        "True" if summary["possible_false_positive"] else "False"
                    ])
                    
            # Draw and save annotated images
            pred_save_path = folders["predictions"] / img_path.name
            annotated_img = result.plot(labels=True, conf=True)
            cv2.imwrite(str(pred_save_path), annotated_img)
            
            # Copy to sorting case folders
            if summary["possible_false_positive"]:
                # Programmatically copy false positive skin flags to failure cases
                shutil.copy2(pred_save_path, folders["failure_cases"] / img_path.name)
                print(f"  [SKIN FP FLAG] Large low-confidence box in {img_path.name}. Copied to failure_cases/.")
            elif summary["highest_confidence"] >= 0.80:
                # Copy high confidence to strong cases
                shutil.copy2(pred_save_path, folders["strong_cases"] / img_path.name)
                
        print(f"\nStandard validation run completed:")
        print(f"  - Images Evaluated: {len(img_files)}")
        print(f"  - Total Predicted Lesions: {total_detections_all}")
        print(f"  - Images Flagged with Large FP Skin Boxes: {total_images_flagged}")

def run_confidence_sweep(model, img_files, sweep_thresholds, iou, class_filter, folders):
    """Run comparative confidence sweeps and export stats to confidence_sweep_report.csv."""
    sweep_report_path = folders["predictions"].parent / "confidence_sweep_report.csv"
    print(f"Initializing Confidence Sweep analysis. Exporting comparison report to {sweep_report_path}...")
    
    headers = [
        "conf_threshold", "total_images_processed", "total_detections",
        "average_detections_per_image", "total_blackheads", "total_whiteheads",
        "total_papules", "total_purulents", "total_cysts", "flagged_false_positives"
    ]
    
    sweep_results = []
    
    for t in sweep_thresholds:
        stats = {
            "total_detections": 0,
            "blackheads": 0,
            "whiteheads": 0,
            "papules": 0,
            "purulents": 0,
            "cysts": 0,
            "flagged_fp": 0
        }
        
        for img_path in img_files:
            process_res = process_single_image(model, img_path, t, iou, class_filter)
            if not process_res:
                continue
            predictions, summary, _ = process_res
            
            stats["total_detections"] += summary["total_detections"]
            stats["blackheads"] += summary["blackhead_count"]
            stats["whiteheads"] += summary["whitehead_count"]
            stats["papules"] += summary["papular_count"]
            stats["purulents"] += summary["purulent_count"]
            stats["cysts"] += summary["cystic_count"]
            
            if summary["possible_false_positive"]:
                stats["flagged_fp"] += 1
                
        avg_det = stats["total_detections"] / max(1, len(img_files))
        
        sweep_results.append([
            f"{t:.2f}", len(img_files), stats["total_detections"], f"{avg_det:.2f}",
            stats["blackheads"], stats["whiteheads"], stats["papules"],
            stats["purulents"], stats["cysts"], stats["flagged_fp"]
        ])
        
    # Write to CSV
    with open(sweep_report_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(sweep_results)
        
    # Display comparison table in console
    print("\n=========================================================================")
    print("                      CONFIDENCE SWEEP COMPARATIVE AUDIT                 ")
    print("=========================================================================")
    print("Conf | Images | Total BBoxes | Avg BBoxes | Blackheads | Whiteheads | FPs")
    print("-----|--------|--------------|------------|------------|------------|----")
    for r in sweep_results:
        print(f"{r[0]:4s} | {r[1]:6d} | {r[2]:12d} | {r[3]:10s} | {r[4]:10d} | {r[5]:10d} | {r[9]:3d}")
    print("=========================================================================\n")

def main():
    args = parse_args()
    
    # 1. Initialize folders
    eval_dir, folders = init_folders()
    
    # 2. Get and load model weights
    model_path = get_best_model_path()
    print(f"Loading retrained YOLOv11s model from {model_path}...")
    try:
        model = YOLO(str(model_path))
    except Exception as e:
        print(f"Critical Error: Failed to load model weights: {e}")
        return
        
    # 3. Resolve input image list
    input_path = Path(args.input)
    if not input_path.exists():
        # If running in planning/default mode and raw_images is empty, print warning and exit
        print(f"Auditing Input Path: '{input_path}' is empty or does not exist.")
        print(f"Drop raw clinical photos into '{folders['raw_images']}' and rerun the script.")
        return
        
    img_files = []
    if input_path.is_file():
        if input_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            img_files.append(input_path)
    else:
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"]:
            img_files.extend(list(input_path.glob(ext)))
            
    if not img_files:
        print(f"No clinical images found under input path: '{input_path}'.")
        print(f"Drop clinical photos (.jpg, .png) into '{folders['raw_images']}' and rerun.")
        return
        
    # Parse class filter list
    class_filter = [int(x) for x in args.class_filter.split(",")]
    
    # 4. Check Sweep Mode
    if args.conf_sweep:
        sweep_thresholds = [float(x.strip()) for x in args.conf_sweep.split(",")]
        run_confidence_sweep(model, img_files, sweep_thresholds, args.iou, class_filter, folders)
    else:
        run_standard_evaluation(model, img_files, args.conf, args.iou, class_filter, folders)

if __name__ == "__main__":
    main()
