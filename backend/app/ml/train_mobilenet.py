#!/usr/bin/env python3
"""
MobileNetV2 Transfer Learning and Fine-Tuning Pipeline.
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
    MOBILENET_STAGE1_EPOCHS,
    MOBILENET_STAGE1_LR,
    MOBILENET_FINE_TUNE_EPOCHS,
    MOBILENET_FINE_TUNE_LR,
    MOBILENET_ARTIFACTS_DIR,
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


def build_mobilenetv2_model(input_shape=INPUT_SHAPE, num_classes=NUM_CLASSES) -> tf.keras.Model:
    """
    Builds MobileNetV2 transfer learning model with integrated augmentation and MobileNet preprocessing.
    """
    inputs = tf.keras.Input(shape=input_shape, name="input_image")

    # On-the-fly augmentation (active during training)
    x = tf.keras.layers.RandomFlip("horizontal", name="aug_flip")(inputs)
    x = tf.keras.layers.RandomRotation(0.08, name="aug_rotation")(x)
    x = tf.keras.layers.RandomZoom(0.08, name="aug_zoom")(x)
    
    # Preprocessing for MobileNetV2 (scales [0, 255] to [-1, 1])
    x = tf.keras.layers.Rescaling(scale=1.0 / 127.5, offset=-1.0, name="mobilenet_rescaling")(x)

    # ImageNet Pretrained Base
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout1")(x)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense1")(x)
    x = tf.keras.layers.Dropout(0.2, name="dropout2")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="mobilenetv2_waste_classifier")
    return model, base_model


def train_mobilenetv2(
    stage1_epochs: int = MOBILENET_STAGE1_EPOCHS,
    stage1_lr: float = MOBILENET_STAGE1_LR,
    fine_tune_epochs: int = MOBILENET_FINE_TUNE_EPOCHS,
    fine_tune_lr: float = MOBILENET_FINE_TUNE_LR
) -> tf.keras.Model:
    set_seed(42)
    print("=" * 60)
    print("      Training MobileNetV2 Transfer Learning Model")
    print("=" * 60)

    # Load data
    train_ds, val_ds, test_ds = load_datasets()
    class_weights = compute_training_class_weights()
    print(f"Loaded datasets. Applied class weights: {class_weights}")

    # Build model
    model, base_model = build_mobilenetv2_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=stage1_lr),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    model.summary()

    checkpoint_path = MOBILENET_ARTIFACTS_DIR / "best_model.keras"
    callbacks_stage1 = get_training_callbacks(checkpoint_path=checkpoint_path, patience_es=5, patience_lr=2)

    print("\n--- Stage 1: Training Custom Classification Head (Frozen Base) ---")
    start_time = time.time()
    history_stage1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=stage1_epochs,
        class_weight=class_weights,
        callbacks=callbacks_stage1,
        verbose=1
    )

    # Stage 2: Fine-Tuning top layers of MobileNetV2
    print("\n--- Stage 2: Fine-Tuning Top Layers of MobileNetV2 ---")
    base_model.trainable = True
    # Freeze all layers except the last 30 layers
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=fine_tune_lr),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    model.summary()

    callbacks_stage2 = get_training_callbacks(checkpoint_path=checkpoint_path, patience_es=4, patience_lr=2)
    initial_epoch = len(history_stage1.history["loss"])
    total_epochs = initial_epoch + fine_tune_epochs

    history_stage2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=total_epochs,
        initial_epoch=initial_epoch,
        class_weight=class_weights,
        callbacks=callbacks_stage2,
        verbose=1
    )

    total_duration = time.time() - start_time
    print(f"\n[OK] MobileNetV2 Training finished in {total_duration:.2f} seconds ({total_duration/60:.2f} minutes).")

    # Combine histories
    combined_history = {}
    for k in history_stage1.history.keys():
        combined_history[k] = [float(round(x, 5)) for x in history_stage1.history[k] + history_stage2.history[k]]

    # Save combined history and curves
    history_path = MOBILENET_ARTIFACTS_DIR / "history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(combined_history, f, indent=2)

    curve_path = EVALUATION_DIR / "mobilenetv2_training_curves.png"
    plot_and_save_training_curves(combined_history, curve_path, title="MobileNetV2 Transfer Learning")

    # Save config
    config_dict = {
        "model_name": "MobileNetV2 Transfer Learning",
        "stage1_epochs": initial_epoch,
        "total_epochs": len(combined_history["loss"]),
        "batch_size": 16,
        "stage1_lr": stage1_lr,
        "fine_tune_lr": fine_tune_lr,
        "input_shape": list(INPUT_SHAPE),
        "training_duration_seconds": round(total_duration, 2),
        "final_train_loss": combined_history["loss"][-1],
        "final_train_acc": combined_history["accuracy"][-1],
        "best_val_loss": min(combined_history["val_loss"]),
        "best_val_acc": max(combined_history["val_accuracy"])
    }
    with open(MOBILENET_ARTIFACTS_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)

    print(f"Artifacts saved in {MOBILENET_ARTIFACTS_DIR}")
    return model


if __name__ == "__main__":
    train_mobilenetv2()
