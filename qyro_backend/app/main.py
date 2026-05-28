import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.services.yolo_service import YOLOService
from app.api.routes import router

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("qyro_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load YOLO Singleton model ONCE on server startup
    logger.info("Initializing Qyro Backend Inference API v0.1 Lifespan hooks.")
    try:
        yolo = YOLOService.get_instance()
        yolo.load_model(settings.MODEL_PATH)
    except Exception as e:
        logger.critical(f"Server failed to initialize YOLO model weights on startup: {e}")
        raise e
    yield
    logger.info("Shutdown sequence complete. Releasing resources.")

app = FastAPI(
    title="Qyro Backend Inference API",
    description="REST API wrapper for the prototype-stable YOLOv2 + Hybrid Clinical Inference Acne detector.",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS Middleware (Frontend-friendly production practice)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router prefixes
app.include_router(router, prefix="/api/v1", tags=["Analysis Endpoint"])

# Global Exception Interceptor for standard API failure consistency (Refinement 3)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_detail = exc.detail
    if not isinstance(error_detail, dict):
        error_detail = {
            "code": "INTERNAL_ERROR",
            "message": str(exc.detail)
        }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_detail.get("code", "INTERNAL_ERROR"),
                "message": error_detail.get("message", "An unexpected error occurred.")
            }
        }
    )

# Capture validation errors (e.g. missing files, incorrect fields)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_FAILED",
                "message": "Invalid request payload. Ensure file key is named 'image'."
            }
        }
    )

# Catch-all unexpected python/backend exception handler (Safety net)
@app.exception_handler(Exception)
async def catch_all_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system error captured: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred."
            }
        }
    )
