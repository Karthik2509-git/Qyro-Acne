"""
Qyro-Acne Phase 4: Baseline YOLOv11s Training Script

This script trains a baseline YOLO11s model on the cleaned Roboflow dataset.
It is configured for safety on laptop GPUs (RTX 5050, 8GB VRAM) and incorporates
pre-flight diagnostics, absolute path anchoring, error handling, and metric summaries.

Usage:
    python train_yolo_baseline.py
"""

import os
import sys
import time
import logging
import random
from pathlib import Path
import numpy as np
import torch
from ultralytics import YOLO

# Anchor paths relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent

# 1. Setup Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(SCRIPT_DIR / "yolo_baseline_training.log"), mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger("QyroYOLO")

def preflight_check():
    """Run a pre-flight environment check to ensure GPU/CUDA suitability."""
    logger.info("=== PRE-FLIGHT ENVIRONMENT CHECK ===")
    
    python_ver = sys.version.replace('\n', ' ')
    logger.info(f"Python Version: {python_ver}")
    logger.info(f"PyTorch Version: {torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    logger.info(f"CUDA Available: {cuda_available}")
    
    if not cuda_available or "+cpu" in torch.__version__:
        logger.error("CRITICAL ERROR: CUDA is not available to PyTorch or a CPU-only PyTorch build is active.")
        logger.error("Please ensure you are running the script in the CUDA-enabled environment.")
        logger.error("Refer to docs/implementation_plan.md for installation instructions.")
        sys.exit(1)
        
    device_name = torch.cuda.get_device_name(0)
    vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    logger.info(f"Detected GPU: {device_name}")
    logger.info(f"GPU VRAM: {vram_total:.2f} GB")
    logger.info(f"CUDA Build Version: {torch.version.cuda}")
    logger.info("====================================\n")

def set_seeds(seed=42):
    """Set seeds for reproducibility across random, numpy, and torch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        # Enable autotuner benchmark for faster training speed
        torch.backends.cudnn.benchmark = True
    logger.info(f"Reproducibility seeds set to {seed}")

def main():
    # Run environment verification first
    preflight_check()
    
    logger.info("Starting Qyro-Acne YOLOv11s Baseline Training Setup...")
    
    # Set reproducibility seeds
    set_seeds(42)
    
    # 3. Define Approved Config Parameters (anchored relative to script)
    dataset_yaml = str(SCRIPT_DIR / "datasets" / "cleaned" / "roboflow_detection" / "data.yaml")
    project_dir = str(SCRIPT_DIR / "runs")
    
    epochs = 100
    patience = 20
    imgsz = 640
    batch_size = 8  # Safe default to prevent CUDA OOM
    workers = 4
    
    logger.info(f"Dataset configuration path: {dataset_yaml}")
    logger.info(f"Output directory path: {project_dir}")
    logger.info(f"Configuration: imgsz={imgsz}, batch={batch_size}, epochs={epochs}, patience={patience}")
    
    # 4. Initialize YOLOv11s Model
    logger.info("Initializing YOLO11s model weights...")
    try:
        model = YOLO("yolo11s.pt")
    except Exception as e:
        logger.error(f"Failed to load model weights: {e}")
        sys.exit(1)
        
    # Track execution time
    start_time = time.time()
    
    # 5. Train with Graceful Failure Handling for CUDA OOM
    try:
        logger.info("Beginning model training...")
        results = model.train(
            data=dataset_yaml,
            epochs=epochs,
            patience=patience,
            imgsz=imgsz,
            batch=batch_size,
            optimizer="auto",  # Automatically chooses SGD for this iteration volume
            amp=True,          # Mixed precision calculations
            workers=workers,
            cache=False,       # Read from disk to preserve system RAM
            device=0,          # CUDA GPU device 0
            seed=42,           # Model training seed
            project=project_dir, # Save results in the absolute 'runs/' directory
            name="qyro_yolo_baseline_v1",  # Saved subdirectory name
            exist_ok=True,     # Overwrite if exists to prevent multiple redundant run folders
            
            # Clinically Safe Augmentations
            fliplr=0.5,
            flipud=0.0,
            degrees=10.0,
            scale=0.1,
            translate=0.1,
            hsv_h=0.015,
            hsv_s=0.1,
            hsv_v=0.1,
            
            # Disabled/Risky Augmentations
            mosaic=0.0,
            mixup=0.0
        )
        
        elapsed_time = time.time() - start_time
        logger.info("Baseline training completed successfully!")
        logger.info(f"Total training time: {elapsed_time / 60:.2f} minutes")
        
        # 6. Report and Log Final Validation Metrics safely
        logger.info("Fetching final validation metrics...")
        metrics = getattr(results, "results_dict", {})
        
        logger.info("==========================================")
        logger.info("       FINAL BASELINE METRIC SUMMARY       ")
        logger.info("==========================================")
        logger.info(f"Precision (B):  {metrics.get('metrics/precision(B)', 0.0):.4f}")
        logger.info(f"Recall (B):     {metrics.get('metrics/recall(B)', 0.0):.4f}")
        logger.info(f"mAP50 (B):      {metrics.get('metrics/mAP50(B)', 0.0):.4f}")
        logger.info(f"mAP50-95 (B):   {metrics.get('metrics/mAP50-95(B)', 0.0):.4f}")
        logger.info(f"Saved Directory: runs/qyro_yolo_baseline_v1/")
        logger.info("==========================================")
        
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        err_msg = str(e)
        if "out of memory" in err_msg.lower() or isinstance(e, torch.cuda.OutOfMemoryError):
            logger.error("CRITICAL ERROR: CUDA Out of Memory (OOM) encountered during training!")
            logger.error("======================================================================")
            logger.error("The RTX 5050 GPU ran out of VRAM using batch=8.")
            logger.error("RECOMMENDED ACTION: Re-run the script with a reduced batch size: batch=4.")
            logger.error("======================================================================")
            sys.exit(1)
        else:
            logger.error(f"An unexpected runtime error occurred: {e}")
            raise e
    except Exception as e:
        logger.error(f"Training was interrupted by an unexpected exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
