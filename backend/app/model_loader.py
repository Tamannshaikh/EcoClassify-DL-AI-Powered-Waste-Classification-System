"""
Singleton Model and Metadata Loader.
Loads model into memory once at application startup.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import tensorflow as tf
from PIL import Image

from backend.app.config import (
    DEFAULT_MODEL_PATH,
    DEFAULT_CLASS_NAMES_PATH,
    DEFAULT_METADATA_PATH,
    DEFAULT_METRICS_PATH,
    MODEL_VERSION
)
from backend.app.ml.preprocessing import preprocess_single_image_for_inference

logger = logging.getLogger(__name__)


class ModelManager:
    _instance: Optional["ModelManager"] = None

    def __init__(self):
        self.model: Optional[tf.keras.Model] = None
        self.classes: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
        self.is_loaded: bool = False
        self.model_version: str = MODEL_VERSION

    @classmethod
    def get_instance(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

    def load_model(self) -> bool:
        """Loads trained Keras model, class names, metadata, and metrics."""
        try:
            if not DEFAULT_MODEL_PATH.exists():
                logger.error(f"Model file not found at {DEFAULT_MODEL_PATH}")
                return False

            logger.info(f"Loading model from {DEFAULT_MODEL_PATH}...")
            self.model = tf.keras.models.load_model(str(DEFAULT_MODEL_PATH))

            if DEFAULT_CLASS_NAMES_PATH.exists():
                with open(DEFAULT_CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
                    self.classes = json.load(f)
            else:
                self.classes = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

            if DEFAULT_METADATA_PATH.exists():
                with open(DEFAULT_METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

            if DEFAULT_METRICS_PATH.exists():
                with open(DEFAULT_METRICS_PATH, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)

            # Warmup prediction
            warmup_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)
            _ = self.model.predict(warmup_tensor, verbose=0)

            self.is_loaded = True
            logger.info("Model loaded and warmed up successfully.")
            return True

        except Exception as e:
            logger.exception(f"Failed to load model: {e}")
            self.is_loaded = False
            return False

    def predict(self, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Runs inference on a PIL image.
        Returns predicted class, confidence, and probability distribution for all 6 classes.
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model is not loaded. Call load_model() first.")

        arch = self.metadata.get("model_architecture", "mobilenetv2")
        input_tensor = preprocess_single_image_for_inference(pil_image, model_type=arch)

        raw_preds = self.model.predict(input_tensor, verbose=0)[0]

        probabilities = {}
        for idx, cls_name in enumerate(self.classes):
            probabilities[cls_name] = float(round(raw_preds[idx], 4))

        top_idx = int(np.argmax(raw_preds))
        predicted_class = self.classes[top_idx]
        confidence = float(round(raw_preds[top_idx], 4))

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "probabilities": probabilities,
            "raw_predictions": raw_preds
        }
