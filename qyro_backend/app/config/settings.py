import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = Path("c:/Users/KARTHIK V/OneDrive/Desktop/Qyro-Acne")

class Settings:
    # API info
    APP_VERSION: str = "v0.1-qyro-prototype"
    
    # Model configuration
    # Prefer local workspace retrained weights, fallback to base dir
    MODEL_PATH: Path = WORKSPACE_DIR / "runs" / "qyro_yolo_v2-2" / "weights" / "best.pt"
    if not MODEL_PATH.exists():
        MODEL_PATH = WORKSPACE_DIR / "runs" / "qyro_yolo_v2" / "weights" / "best.pt"
    if not MODEL_PATH.exists():
        MODEL_PATH = WORKSPACE_DIR / "yolo11s.pt"
        
    # File upload configurations
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png"}

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
