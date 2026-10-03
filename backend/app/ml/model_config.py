"""
Central Model and Training Configuration.
Cross-platform pathlib paths and hyperparameter settings for Waste Classification.
"""
from pathlib import Path
import os
import random
import numpy as np
import tensorflow as tf

# Resolve Project Paths
ML_DIR = Path(__file__).resolve().parent
APP_DIR = ML_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
TRAIN_DIR = PROCESSED_DIR / "train"
VAL_DIR = PROCESSED_DIR / "val"
TEST_DIR = PROCESSED_DIR / "test"

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
CNN_ARTIFACTS_DIR = ARTIFACTS_DIR / "cnn"
MOBILENET_ARTIFACTS_DIR = ARTIFACTS_DIR / "mobilenetv2"
EVALUATION_DIR = ARTIFACTS_DIR / "evaluation"
FINAL_ARTIFACTS_DIR = ARTIFACTS_DIR / "final"

# Ensure all artifact directories exist
for d in [CNN_ARTIFACTS_DIR, MOBILENET_ARTIFACTS_DIR, EVALUATION_DIR, FINAL_ARTIFACTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Ground-truth classes (alphabetical matching folder structure)
CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
NUM_CLASSES = len(CLASSES)
CLASS_TO_IDX = {cls: idx for idx, cls in enumerate(CLASSES)}
IDX_TO_CLASS = {idx: cls for idx, cls in enumerate(CLASSES)}

# Hyperparameters
RANDOM_SEED = 42
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = (224, 224, 3)
BATCH_SIZE = 16

# Training Hyperparameters
CNN_EPOCHS = 25
CNN_INITIAL_LR = 1e-3

MOBILENET_STAGE1_EPOCHS = 12
MOBILENET_STAGE1_LR = 1e-3
MOBILENET_FINE_TUNE_EPOCHS = 10
MOBILENET_FINE_TUNE_LR = 1e-5


def set_seed(seed: int = RANDOM_SEED):
    """Set global seeds for reproducibility across Python, NumPy, and TensorFlow."""
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
