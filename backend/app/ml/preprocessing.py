"""
Image Preprocessing and Data Augmentation Pipelines.
Provides distinct normalization for CNN and MobileNetV2 models.
"""
import sys
from pathlib import Path
from typing import Tuple
import numpy as np
import tensorflow as tf
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import IMAGE_SIZE


def get_data_augmentation_layer() -> tf.keras.Sequential:
    """
    Creates a moderate on-the-fly Keras augmentation layer for training only.
    Preserves realistic waste features while enhancing generalization.
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal", name="aug_random_flip"),
        tf.keras.layers.RandomRotation(0.08, fill_mode="reflect", name="aug_random_rotation"),
        tf.keras.layers.RandomZoom(0.08, fill_mode="reflect", name="aug_random_zoom"),
        tf.keras.layers.RandomTranslation(0.05, 0.05, fill_mode="reflect", name="aug_random_translation"),
    ], name="data_augmentation")


def preprocess_cnn(image: tf.Tensor, label: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    Standard [0, 1] normalization for Custom CNN baseline.
    """
    image = tf.cast(image, tf.float32) / 255.0
    return image, label


def preprocess_mobilenet(image: tf.Tensor, label: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    ImageNet MobileNetV2 preprocessing (scales pixel values to [-1, 1]).
    """
    image = tf.cast(image, tf.float32)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return image, label


def preprocess_single_image_for_inference(
    img: Image.Image,
    model_type: str = "mobilenetv2",
    target_size: Tuple[int, int] = IMAGE_SIZE
) -> np.ndarray:
    """
    Preprocesses a PIL Image for inference.
    Returns a batch array with shape (1, height, width, 3) in [0, 255] range as float32.
    The model's internal Rescaling layer will handle the normalization appropriately.
    """
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    img = img.resize(target_size, Image.Resampling.BILINEAR)
    img_array = np.array(img, dtype=np.float32)
    return np.expand_dims(img_array, axis=0)
