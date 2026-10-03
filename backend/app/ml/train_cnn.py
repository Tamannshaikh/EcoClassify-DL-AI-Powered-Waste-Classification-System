#!/usr/bin/env python3
"""
Custom CNN Baseline Model Definition and Training Pipeline.
"""
import sys
import time
import json
from pathlib import Path
import tensorflow as tf

# Add project root to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import (
    INPUT_SHAPE,
    NUM_CLASSES,
    CNN_EPOCHS,
    CNN_INITIAL_LR,
    CNN_ARTIFACTS_DIR,
    EVALUATION_DIR,
    set_seed
)
from backend.app.ml.data_loader import load_datasets
from backend.app.ml.class_weights import compute_training_class_weights
from backend.app.ml.model_utils import (
    get_training_callbacks,
    save_training_history,
    plot_and_save_training_curves
)


def build_custom_cnn(input_shape=INPUT_SHAPE, num_classes=NUM_CLASSES) -> tf.keras.Model:
    """
    Builds a lightweight 4-block CNN architecture with integrated augmentation and scaling.
    """
    inputs = tf.keras.Input(shape=input_shape, name="input_image")

    # On-the-fly augmentation (active only during model.fit)
    x = tf.keras.layers.RandomFlip("horizontal", name="aug_flip")(inputs)
    x = tf.keras.layers.RandomRotation(0.08, name="aug_rotation")(x)
    x = tf.keras.layers.RandomZoom(0.08, name="aug_zoom")(x)
    
    # Rescale [0, 255] to [0, 1]
    x = tf.keras.layers.Rescaling(1.0 / 255.0, name="rescaling")(x)

    # Block 1
    x = tf.keras.layers.Conv2D(32, (3, 3), padding="same", name="conv1")(x)
    x = tf.keras.layers.BatchNormalization(name="bn1")(x)
    x = tf.keras.layers.ReLU(name="relu1")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), name="pool1")(x)

    # Block 2
    x = tf.keras.layers.Conv2D(64, (3, 3), padding="same", name="conv2")(x)
    x = tf.keras.layers.BatchNormalization(name="bn2")(x)
    x = tf.keras.layers.ReLU(name="relu2")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), name="pool2")(x)

    # Block 3
    x = tf.keras.layers.Conv2D(128, (3, 3), padding="same", name="conv3")(x)
    x = tf.keras.layers.BatchNormalization(name="bn3")(x)
    x = tf.keras.layers.ReLU(name="relu3")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), name="pool3")(x)

    # Block 4
    x = tf.keras.layers.Conv2D(128, (3, 3), padding="same", name="conv4")(x)
    x = tf.keras.layers.BatchNormalization(name="bn4")(x)
    x = tf.keras.layers.ReLU(name="relu4")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2), name="pool4")(x)

    # Classification Head
    x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout1")(x)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense1")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout2")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="custom_cnn_baseline")
    return model


def train_custom_cnn(epochs: int = CNN_EPOCHS, lr: float = CNN_INITIAL_LR) -> tf.keras.Model:
    set_seed(42)
    print("=" * 60)
    print("           Training Custom CNN Baseline Model")
    print("=" * 60)

    # Load data
    train_ds, val_ds, test_ds = load_datasets()
    class_weights = compute_training_class_weights()
    print(f"Loaded datasets. Applied class weights: {class_weights}")

    # Build model
    model = build_custom_cnn()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    model.summary()

    checkpoint_path = CNN_ARTIFACTS_DIR / "best_model.keras"
    callbacks = get_training_callbacks(checkpoint_path=checkpoint_path, patience_es=6, patience_lr=3)

    start_time = time.time()
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    duration = time.time() - start_time
    print(f"\n[OK] CNN Training finished in {duration:.2f} seconds ({duration/60:.2f} minutes).")

    # Save history and curves
    history_path = CNN_ARTIFACTS_DIR / "history.json"
    clean_hist = save_training_history(history, history_path)

    curve_path = EVALUATION_DIR / "cnn_training_curves.png"
    plot_and_save_training_curves(clean_hist, curve_path, title="Custom CNN Baseline")

    # Save training config
    config_dict = {
        "model_name": "Custom CNN Baseline",
        "epochs": len(clean_hist["loss"]),
        "batch_size": 16,
        "initial_lr": lr,
        "input_shape": list(INPUT_SHAPE),
        "training_duration_seconds": round(duration, 2),
        "final_train_loss": clean_hist["loss"][-1],
        "final_train_acc": clean_hist["accuracy"][-1],
        "best_val_loss": min(clean_hist["val_loss"]),
        "best_val_acc": max(clean_hist["val_accuracy"])
    }
    with open(CNN_ARTIFACTS_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)

    print(f"Artifacts saved in {CNN_ARTIFACTS_DIR}")
    return model


if __name__ == "__main__":
    train_custom_cnn()
