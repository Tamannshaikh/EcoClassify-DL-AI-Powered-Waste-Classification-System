"""
Dataset and Project Configuration for Waste Classification DL System.
Portable configuration using pathlib for cross-platform support.
"""
from pathlib import Path

# Base Paths (relative to project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw" / "TrashNet"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure logs and data directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Dataset Definition (Source of Truth: TrashNet)
EXPECTED_CLASSES = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash"
]

# Split Configuration
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

RANDOM_SEED = 42

# Image Processing Specs
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
TARGET_IMAGE_SIZE_CNN = (128, 128)
TARGET_IMAGE_SIZE_MOBILENET = (224, 224)
