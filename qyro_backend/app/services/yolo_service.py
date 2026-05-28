import logging
from pathlib import Path
from ultralytics import YOLO
import torch

logger = logging.getLogger("qyro_backend")

class YOLOService:
    _instance = None
    model = None
    device = "cpu"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self, model_path: Path):
        if self.model is None:
            # Determine best available execution device
            if torch.cuda.is_available():
                self.device = 0  # GPU 0
                logger.info("CUDA GPU detected. Using GPU for fast clinical inference.")
            else:
                self.device = "cpu"
                logger.info("CUDA GPU not available. Falling back to CPU execution.")
                
            logger.info(f"Loading YOLOv11s model weights from: {model_path}")
            try:
                self.model = YOLO(str(model_path))
                logger.info("YOLOv11s model loaded successfully and cached.")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                raise e

    def predict(self, img_path: Path):
        if self.model is None:
            raise RuntimeError("YOLO model is not initialized. Initialize on startup first.")
            
        # Run prediction utilizing locked threshold configurations
        results = self.model.predict(
            source=str(img_path), 
            conf=0.15, 
            iou=0.45, 
            device=self.device, 
            verbose=False
        )
        return results[0]
