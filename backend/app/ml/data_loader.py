"""
Data Loader using tf.data for high-performance CPU data streaming.
"""
import sys
from pathlib import Path
from typing import Tuple
import tensorflow as tf

# Add project root to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import (
    TRAIN_DIR,
    VAL_DIR,
    TEST_DIR,
    IMAGE_SIZE,
    BATCH_SIZE,
    CLASSES,
    RANDOM_SEED
)


def load_datasets(
    batch_size: int = BATCH_SIZE,
    image_size: Tuple[int, int] = IMAGE_SIZE
) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    """
    Builds optimized tf.data.Dataset pipelines for train, val, and test.
    Loads RGB images at 224x224. Prefetches for CPU efficiency.
    """
    train_ds = tf.keras.utils.image_dataset_from_directory(
        directory=str(TRAIN_DIR),
        labels="inferred",
        label_mode="int",
        class_names=CLASSES,
        color_mode="rgb",
        batch_size=batch_size,
        image_size=image_size,
        shuffle=True,
        seed=RANDOM_SEED
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        directory=str(VAL_DIR),
        labels="inferred",
        label_mode="int",
        class_names=CLASSES,
        color_mode="rgb",
        batch_size=batch_size,
        image_size=image_size,
        shuffle=False
    )

    test_ds = tf.keras.utils.image_dataset_from_directory(
        directory=str(TEST_DIR),
        labels="inferred",
        label_mode="int",
        class_names=CLASSES,
        color_mode="rgb",
        batch_size=batch_size,
        image_size=image_size,
        shuffle=False
    )

    # Enable prefetching for smooth CPU pipeline
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds, test_ds


if __name__ == "__main__":
    train_ds, val_ds, test_ds = load_datasets()
    print("Data loaders verified.")
    for x, y in train_ds.take(1):
        print(f"Batch shape: {x.shape}, labels: {y.shape}")
