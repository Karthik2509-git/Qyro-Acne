import sys
import logging
from pathlib import Path

# Resolve workspace path safely
WORKSPACE_DIR = Path("c:/Users/KARTHIK V/OneDrive/Desktop/Qyro-Acne")
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.append(str(WORKSPACE_DIR))

try:
    from clinical_inference import process_clinical_inference, CLASS_NAMES
except ImportError as e:
    logging.error(f"Failed to import from clinical_inference.py: {e}")
    raise e

logger = logging.getLogger("qyro_backend")

def extract_yolo_detections(yolo_result):
    """
    Extract boxes, normalized areas, and confidences into dictionaries matching clinical_inference expectations.
    """
    detections = []
    for box in yolo_result.boxes:
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

def execute_clinical_inference(yolo_result):
    """
    Runs detections through the locked clinical reasoning layer.
    """
    detections = extract_yolo_detections(yolo_result)
    inference_result = process_clinical_inference(detections)
    return inference_result, detections
