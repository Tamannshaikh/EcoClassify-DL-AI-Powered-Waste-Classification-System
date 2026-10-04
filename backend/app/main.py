"""
FastAPI Backend Application Entry Point.
"""
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.config import APP_NAME, API_PREFIX, ALLOWED_ORIGINS
from backend.app.database import init_db
from backend.app.model_loader import ModelManager
from backend.app.routes import (
    health,
    model,
    prediction,
    history,
    dataset,
    recycling,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event: Initializes DB and loads ML model once on startup."""
    logger.info("Initializing SQLite database...")
    init_db()

    logger.info("Loading Deep Learning model...")
    manager = ModelManager.get_instance()
    success = manager.load_model()
    if success:
        logger.info(f"Model '{manager.metadata.get('model_name')}' ready for inference.")
    else:
        logger.warning("Model could not be loaded on startup. Check artifacts/final/")

    yield
    logger.info("Shutting down Waste Classification backend service.")


app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="AI-Powered Waste Classification System REST API using Deep Learning & MobileNetV2",
    lifespan=lifespan
)

# CORS Configuration: Local frontend origins only
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.encoders import jsonable_encoder

# Custom Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters.",
                "errors": jsonable_encoder(exc.errors())
            }
        }
    )


# Register API Routes with /api/v1 prefix
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(model.router, prefix=API_PREFIX)
app.include_router(prediction.router, prefix=API_PREFIX)
app.include_router(history.router, prefix=API_PREFIX)
app.include_router(dataset.router, prefix=API_PREFIX)
app.include_router(recycling.router, prefix=API_PREFIX)


@app.get("/")
async def root():
    return {
        "app": APP_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_prefix": API_PREFIX,
        "status": "online"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
