import logging
from pathlib import Path
from PIL import Image
from fastapi import HTTPException, status
from app.config.settings import settings

logger = logging.getLogger("qyro_backend")

def validate_image_file(file_path: Path, filename: str):
    """
    Perform deep validation of uploaded image including:
    1. Extension/Format validation
    2. File size validation
    3. Structural corruption validation using PIL
    """
    # 1. Extension validation
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected upload: unsupported extension '{ext}' in file {filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "UNSUPPORTED_IMAGE_TYPE",
                "message": "Unsupported image format. Please upload JPG, JPEG, or PNG."
            }
        )
        
    # 2. File size validation
    file_size = file_path.stat().st_size
    if file_size > settings.MAX_FILE_SIZE:
        logger.warning(f"Rejected upload: file size {file_size} exceeds limit in {filename}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "IMAGE_TOO_LARGE",
                "message": "Image file size exceeds the maximum limit of 10MB."
            }
        )
        
    # 3. Pillow-based deep integrity check
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify image integrity
    except Exception as e:
        logger.warning(f"Rejected upload: image is corrupted or invalid. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_IMAGE",
                "message": "Image is corrupted or unreadable."
            }
        )

def preprocess_image(file_path: Path):
    """
    Safe aspect-ratio aware resizing to ensure model efficiency on giant files.
    """
    MAX_DIM = 1024
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if width > MAX_DIM or height > MAX_DIM:
                img.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
                img.save(file_path)
                logger.info(f"Resized large image {file_path.name} from {width}x{height} to {img.width}x{img.height}")
    except Exception as e:
        logger.error(f"Image preprocessing failed for {file_path.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_IMAGE",
                "message": "Failed to process image file."
            }
        )
