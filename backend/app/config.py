"""
Application Configuration using pathlib for cross-platform portability.
"""
from pathlib import Path
import os

# Project root resolution
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
TRAIN_DIR = PROCESSED_DIR / "train"
VAL_DIR = PROCESSED_DIR / "val"
TEST_DIR = PROCESSED_DIR / "test"

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
FINAL_ARTIFACTS_DIR = ARTIFACTS_DIR / "final"
EVALUATION_DIR = ARTIFACTS_DIR / "evaluation"

# Upload and Database directories
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_UPLOAD_DIR = UPLOADS_DIR / "predictions"
PREDICTIONS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "waste_classification.db"

# Category-based Prediction ID Prefixes
CATEGORY_PREFIXES = {
    "biodegradable": "TB",
    "cardboard": "TC",
    "e_waste": "TE",
    "glass": "TG",
    "metal": "TM",
    "paper": "TP",
    "plastic": "TPL",
    "trash": "TT"
}

# Model paths
DEFAULT_MODEL_PATH = FINAL_ARTIFACTS_DIR / "waste_classifier.keras"
DEFAULT_CLASS_NAMES_PATH = FINAL_ARTIFACTS_DIR / "class_names.json"
DEFAULT_METADATA_PATH = FINAL_ARTIFACTS_DIR / "model_metadata.json"
DEFAULT_METRICS_PATH = FINAL_ARTIFACTS_DIR / "metrics.json"

# API & Server Settings
APP_NAME = "Smart Waste Classification System"
API_PREFIX = "/api/v1"
MODEL_VERSION = "v2.0"
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 10))
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Security: Allowed MIME types and extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/jpg"}

# CORS Origins for local frontend
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Smart Recycling Center Finder Settings
RECYCLING_PROVIDER = os.getenv("RECYCLING_PROVIDER", "curated")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
DEFAULT_SEARCH_RADIUS_KM = float(os.getenv("DEFAULT_SEARCH_RADIUS_KM", "10.0"))
MAX_SEARCH_RADIUS_KM = float(os.getenv("MAX_SEARCH_RADIUS_KM", "50.0"))
DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))
MAX_SEARCH_LIMIT = int(os.getenv("MAX_SEARCH_LIMIT", "20"))
