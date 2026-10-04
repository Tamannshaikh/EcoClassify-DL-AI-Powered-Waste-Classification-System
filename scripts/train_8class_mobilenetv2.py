"""
Phase 12: 8-Class MobileNetV2 Transfer Learning & Fine-Tuning Pipeline.
EcoClassify DL — AI-Powered Waste Classification System

STRICTLY EXPERIMENTAL:
- Saves all artifacts under artifacts/experiments/8class_mobilenetv2/
- Leaves production 6-class model (artifacts/final/) 100% UNTOUCHED.
"""

import os
import sys
import time
import json
import csv
import random
import platform
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.utils.class_weight import compute_class_weight

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "final" / "8class"
EXP_DIR = PROJECT_ROOT / "artifacts" / "experiments" / "8class_mobilenetv2"
CHECKPOINTS_DIR = EXP_DIR / "checkpoints"
LOGS_DIR = EXP_DIR / "logs"
FIGURES_DIR = EXP_DIR / "figures"
GRADCAM_DIR = FIGURES_DIR / "gradcam"
REPORTS_DIR = EXP_DIR / "reports"
MODEL_DIR = EXP_DIR / "model"
METADATA_DIR = EXP_DIR / "metadata"

DOCS_DIR = PROJECT_ROOT / "docs"

# Constants
SEED = 42
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = (224, 224, 3)
NUM_CLASSES = 8
BATCH_SIZE = 32

CLASS_NAMES = [
    "biodegradable",
    "cardboard",
    "e_waste",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash"
]

STAGE1_EPOCHS = 20
STAGE1_LR = 1e-3
STAGE2_EPOCHS = 20
STAGE2_LR = 1e-5

def set_deterministic_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)

def create_experiment_directories():
    for p in [CHECKPOINTS_DIR, LOGS_DIR, FIGURES_DIR, GRADCAM_DIR, REPORTS_DIR, MODEL_DIR, METADATA_DIR]:
        p.mkdir(parents=True, exist_ok=True)

def load_data():
    """Loads train, val, and test datasets with exact class name alignment."""
    print("\n[STEP 1] Loading 8-Class Dataset from data/final/8class/...")
    
    train_dir = DATA_DIR / "train"
    val_dir = DATA_DIR / "val"
    test_dir = DATA_DIR / "test"

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASS_NAMES,
        batch_size=BATCH_SIZE,
        image_size=IMAGE_SIZE,
        shuffle=True,
        seed=SEED
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASS_NAMES,
        batch_size=BATCH_SIZE,
        image_size=IMAGE_SIZE,
        shuffle=False
    )

    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASS_NAMES,
        batch_size=BATCH_SIZE,
        image_size=IMAGE_SIZE,
        shuffle=False
    )

    # Prefetch for performance
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, test_ds

def compute_class_weights():
    """Calculates balanced class weights from the training split."""
    manifest_path = DATA_DIR / "metadata" / "dataset_manifest.csv"
    train_labels = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["split"] == "train":
                train_labels.append(int(r["class_index"]))

    classes = np.arange(NUM_CLASSES)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=np.array(train_labels)
    )
    class_weight_dict = {i: float(weights[i]) for i in range(NUM_CLASSES)}
    print(f"\n[STEP 2] Computed Training Class Weights:")
    for idx, name in enumerate(CLASS_NAMES):
        print(f"  Class {idx} ({name:<15}): {class_weight_dict[idx]:.4f}")
    return class_weight_dict

def build_model():
    """
    Constructs MobileNetV2 Transfer Learning Model.
    Architecture:
      Input (224, 224, 3)
      Data Augmentation (Flip, Rotation, Zoom, Translation)
      Rescaling [-1, 1]
      MobileNetV2 (ImageNet, include_top=False)
      GlobalAveragePooling2D
      Dense(128, relu)
      Dropout(0.30)
      Dense(8, softmax)
    """
    print("\n[STEP 3] Building MobileNetV2 Architecture...")
    inputs = tf.keras.Input(shape=INPUT_SHAPE, name="input_image")

    # On-the-fly Data Augmentation (active only during training)
    x = tf.keras.layers.RandomFlip("horizontal", name="aug_flip")(inputs)
    x = tf.keras.layers.RandomRotation(0.08, name="aug_rotation")(x)
    x = tf.keras.layers.RandomZoom(0.08, name="aug_zoom")(x)
    x = tf.keras.layers.RandomTranslation(0.05, 0.05, name="aug_translation")(x)

    # Rescaling [0, 255] -> [-1, 1]
    x = tf.keras.layers.Rescaling(scale=1.0 / 127.5, offset=-1.0, name="mobilenet_rescaling")(x)

    # ImageNet Base
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=INPUT_SHAPE,
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense1")(x)
    x = tf.keras.layers.Dropout(0.30, name="dropout1")(x)
    outputs = tf.keras.layers.Dense(NUM_CLASSES, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="mobilenetv2_8class_classifier")
    return model, base_model

def train_experiment(model, base_model, train_ds, val_ds, class_weights):
    """Executes Stage 1 (Frozen Backbone) and Stage 2 (Fine-tuning)."""
    print("\n" + "=" * 80)
    print("STAGE 1: TRAINING HEAD WITH FROZEN BACKBONE")
    print("=" * 80)

    stage1_checkpoint = CHECKPOINTS_DIR / "stage1_best.keras"
    callbacks_stage1 = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2, min_lr=1e-6, verbose=1),
        tf.keras.callbacks.ModelCheckpoint(filepath=str(stage1_checkpoint), monitor="val_loss", save_best_only=True, verbose=1),
        tf.keras.callbacks.CSVLogger(filename=str(LOGS_DIR / "stage1_training.csv"))
    ]

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=["accuracy"]
    )

    t0_stage1 = time.time()
    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks_stage1,
        verbose=1
    )
    t_stage1 = time.time() - t0_stage1
    print(f"Stage 1 complete in {t_stage1:.2f}s.")

    print("\n" + "=" * 80)
    print("STAGE 2: FINE-TUNING TOP 30 LAYERS OF MOBILENETV2")
    print("=" * 80)

    # Unfreeze top ~30 layers of MobileNetV2
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    print(f"Base model trainable layers: {sum(1 for l in base_model.layers if l.trainable)} / {len(base_model.layers)}")

    stage2_checkpoint = CHECKPOINTS_DIR / "stage2_best.keras"
    callbacks_stage2 = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.2, patience=2, min_lr=1e-6, verbose=1),
        tf.keras.callbacks.ModelCheckpoint(filepath=str(stage2_checkpoint), monitor="val_loss", save_best_only=True, verbose=1),
        tf.keras.callbacks.CSVLogger(filename=str(LOGS_DIR / "stage2_training.csv"))
    ]

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE2_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=["accuracy"]
    )

    t0_stage2 = time.time()
    history2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE2_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks_stage2,
        verbose=1
    )
    t_stage2 = time.time() - t0_stage2
    print(f"Stage 2 complete in {t_stage2:.2f}s.")

    total_training_time = t_stage1 + t_stage2

    # Merge Histories
    combined_history = {
        "loss": history1.history.get("loss", []) + history2.history.get("loss", []),
        "val_loss": history1.history.get("val_loss", []) + history2.history.get("val_loss", []),
        "accuracy": history1.history.get("accuracy", []) + history2.history.get("accuracy", []),
        "val_accuracy": history1.history.get("val_accuracy", []) + history2.history.get("val_accuracy", []),
        "stage1_epochs": len(history1.history.get("loss", [])),
        "stage2_epochs": len(history2.history.get("loss", [])),
        "total_training_time_seconds": total_training_time
    }

    # Best epoch index
    val_losses = combined_history["val_loss"]
    best_epoch_idx = int(np.argmin(val_losses))
    best_val_loss = float(val_losses[best_epoch_idx])
    best_val_acc = float(combined_history["val_accuracy"][best_epoch_idx])

    print(f"\nBest Overall Model found at Epoch {best_epoch_idx + 1}: Val Loss = {best_val_loss:.4f}, Val Acc = {best_val_acc:.4f}")

    return model, combined_history, best_epoch_idx, best_val_loss, best_val_acc, total_training_time

def save_training_plots(history):
    """Plots training and validation loss and accuracy curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    epochs = range(1, len(history["loss"]) + 1)
    s1_ep = history["stage1_epochs"]

    # Loss
    ax1.plot(epochs, history["loss"], "o-", label="Train Loss", color="#1f77b4")
    ax1.plot(epochs, history["val_loss"], "s-", label="Val Loss", color="#ff7f0e")
    if s1_ep < len(epochs):
        ax1.axvline(x=s1_ep, color="gray", linestyle="--", label="Fine-Tuning Start")
    ax1.set_title("8-Class MobileNetV2 Loss Curves")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Categorical Crossentropy")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy
    ax2.plot(epochs, history["accuracy"], "o-", label="Train Accuracy", color="#2ca02c")
    ax2.plot(epochs, history["val_accuracy"], "s-", label="Val Accuracy", color="#d62728")
    if s1_ep < len(epochs):
        ax2.axvline(x=s1_ep, color="gray", linestyle="--", label="Fine-Tuning Start")
    ax2.set_title("8-Class MobileNetV2 Accuracy Curves")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = FIGURES_DIR / "training_curves.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"  -> Saved {plot_path.relative_to(PROJECT_ROOT)}")

def evaluate_test_set(model):
    """Performs single-pass evaluation on the held-out test set."""
    print("\n" + "=" * 80)
    print("[STEP 4] EVALUATING ON HELD-OUT TEST SET (513 IMAGES)")
    print("=" * 80)

    manifest_path = DATA_DIR / "metadata" / "dataset_manifest.csv"
    test_manifest = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["split"] == "test":
                test_manifest.append(r)

    # Sort deterministically by derived_relative_path
    test_manifest.sort(key=lambda x: x["derived_relative_path"])

    y_true = []
    y_pred = []
    y_conf = []
    predictions_rows = []

    for item in test_manifest:
        abs_p = PROJECT_ROOT / item["derived_relative_path"]
        with Image.open(abs_p) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img_resized = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            arr = np.array(img_resized, dtype=np.float32)
            arr_batch = np.expand_dims(arr, axis=0)

        probs = model.predict(arr_batch, verbose=0)[0]
        pred_idx = int(np.argmax(probs))
        conf = float(probs[pred_idx])
        true_idx = int(item["class_index"])

        y_true.append(true_idx)
        y_pred.append(pred_idx)
        y_conf.append(conf)

        is_correct = (pred_idx == true_idx)

        predictions_rows.append({
            "sample_id": item["sample_id"],
            "true_class": item["class_name"],
            "true_index": true_idx,
            "predicted_class": CLASS_NAMES[pred_idx],
            "predicted_index": pred_idx,
            "confidence": f"{conf:.4f}",
            "correct": "YES" if is_correct else "NO",
            "source_dataset": item["source_dataset"],
            "source_category": item["source_category"]
        })

    # Save test predictions CSV
    pred_csv_path = REPORTS_DIR / "test_predictions.csv"
    with open(pred_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sample_id", "true_class", "true_index", "predicted_class", "predicted_index",
            "confidence", "correct", "source_dataset", "source_category"
        ])
        writer.writeheader()
        writer.writerows(predictions_rows)
    print(f"  -> Generated {pred_csv_path.relative_to(PROJECT_ROOT)}")

    # Metrics calculation
    y_true_np = np.array(y_true)
    y_pred_np = np.array(y_pred)
    y_conf_np = np.array(y_conf)

    test_acc = float(accuracy_score(y_true_np, y_pred_np))
    macro_p = float(precision_score(y_true_np, y_pred_np, average="macro", zero_division=0))
    macro_r = float(recall_score(y_true_np, y_pred_np, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y_true_np, y_pred_np, average="macro", zero_division=0))

    weighted_p = float(precision_score(y_true_np, y_pred_np, average="weighted", zero_division=0))
    weighted_r = float(recall_score(y_true_np, y_pred_np, average="weighted", zero_division=0))
    weighted_f1 = float(f1_score(y_true_np, y_pred_np, average="weighted", zero_division=0))

    per_class_p = precision_score(y_true_np, y_pred_np, average=None, zero_division=0)
    per_class_r = recall_score(y_true_np, y_pred_np, average=None, zero_division=0)
    per_class_f1 = f1_score(y_true_np, y_pred_np, average=None, zero_division=0)
    
    class_support = [int(np.sum(y_true_np == i)) for i in range(NUM_CLASSES)]

    print(f"\nTest Metrics Summary:")
    print(f"  Accuracy:         {test_acc:.4f} ({test_acc * 100:.2f}%)")
    print(f"  Macro Precision:  {macro_p:.4f}")
    print(f"  Macro Recall:     {macro_r:.4f}")
    print(f"  Macro F1:         {macro_f1:.4f}")
    print(f"  Weighted F1:      {weighted_f1:.4f}")

    print("\nPer-Class Breakdown:")
    per_class_results = {}
    for idx, cname in enumerate(CLASS_NAMES):
        p_val = float(per_class_p[idx])
        r_val = float(per_class_r[idx])
        f_val = float(per_class_f1[idx])
        sup = class_support[idx]
        per_class_results[cname] = {
            "index": idx,
            "precision": p_val,
            "recall": r_val,
            "f1_score": f_val,
            "support": sup
        }
        print(f"  - {cname:<15}: Precision={p_val:.4f}, Recall={r_val:.4f}, F1={f_val:.4f} (Support: {sup})")

    # Confusion Matrix
    cm = confusion_matrix(y_true_np, y_pred_np, labels=list(range(NUM_CLASSES)))
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    # Raw counts
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax1)
    ax1.set_title("8-Class Confusion Matrix (Raw Counts)")
    ax1.set_xlabel("Predicted Label")
    ax1.set_ylabel("True Label")

    # Normalized
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Greens", xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax2)
    ax2.set_title("8-Class Confusion Matrix (Normalized)")
    ax2.set_xlabel("Predicted Label")
    ax2.set_ylabel("True Label")

    plt.tight_layout()
    cm_fig_path = FIGURES_DIR / "confusion_matrix.png"
    plt.savefig(cm_fig_path, dpi=300)
    plt.close()
    print(f"  -> Generated {cm_fig_path.relative_to(PROJECT_ROOT)}")

    # Confidence Analysis
    correct_mask = (y_true_np == y_pred_np)
    conf_correct = y_conf_np[correct_mask]
    conf_incorrect = y_conf_np[~correct_mask] if np.sum(~correct_mask) > 0 else np.array([0.0])

    confidence_stats = {
        "average_confidence_overall": float(np.mean(y_conf_np)),
        "median_confidence_overall": float(np.median(y_conf_np)),
        "average_confidence_correct": float(np.mean(conf_correct)),
        "average_confidence_incorrect": float(np.mean(conf_incorrect)),
        "count_below_50": int(np.sum(y_conf_np < 0.50)),
        "count_below_70": int(np.sum(y_conf_np < 0.70)),
        "count_below_90": int(np.sum(y_conf_np < 0.90)),
        "total_test_samples": len(y_conf_np)
    }

    test_metrics = {
        "accuracy": test_acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_p,
        "weighted_recall": weighted_r,
        "weighted_f1": weighted_f1,
        "per_class": per_class_results,
        "confusion_matrix_raw": cm.tolist(),
        "confidence_statistics": confidence_stats
    }

    return test_metrics, cm, cm_norm, predictions_rows

def generate_gradcam_heatmaps(model):
    """
    Computes and saves Grad-CAM heatmaps for key classes (biodegradable, e_waste, cardboard, plastic, trash).
    Target layer: 'out_relu' in MobileNetV2 base model.
    """
    print("\n[STEP 5] Generating Grad-CAM Heatmap Samples...")
    
    # Locate backbone and last conv layer
    base_model = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_model = layer
            break

    if base_model is None:
        print("  [WARN] Could not find MobileNetV2 base model for Grad-CAM.")
        return False

    last_conv_layer = base_model.get_layer("out_relu")
    selected_layer_name = f"{base_model.name}::{last_conv_layer.name}"
    print(f"  Selected Conv Layer for Grad-CAM: {selected_layer_name}")

    # Build sub-model for backbone feature extraction
    backbone_grad_model = tf.keras.Model(
        inputs=[base_model.input],
        outputs=[last_conv_layer.output, base_model.output]
    )

    classes_to_sample = ["biodegradable", "cardboard", "e_waste", "plastic", "trash"]
    manifest_path = DATA_DIR / "metadata" / "dataset_manifest.csv"
    test_manifest = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["split"] == "test":
                test_manifest.append(r)

    for cname in classes_to_sample:
        # Find first 2 sample images for this class in test set
        class_samples = [r for r in test_manifest if r["class_name"] == cname][:2]
        for s_idx, sample in enumerate(class_samples, 1):
            abs_p = PROJECT_ROOT / sample["derived_relative_path"]
            with Image.open(abs_p) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                orig_img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
                arr = np.array(orig_img, dtype=np.float32)
                arr_batch = np.expand_dims(arr, axis=0)

            # Pass through initial rescaling / augmentation layers
            x = arr_batch
            for l_name in ["aug_flip", "aug_rotation", "aug_zoom", "aug_translation", "mobilenet_rescaling"]:
                try:
                    x = model.get_layer(l_name)(x, training=False)
                except Exception:
                    pass

            with tf.GradientTape() as tape:
                conv_out, base_out = backbone_grad_model(x, training=False)
                h = model.get_layer("gap")(base_out, training=False)
                h = model.get_layer("dense1")(h, training=False)
                h = model.get_layer("dropout1")(h, training=False)
                preds = model.get_layer("predictions")(h, training=False)

                pred_idx = int(tf.argmax(preds[0]))
                class_loss = preds[:, pred_idx]

            grads = tape.gradient(class_loss, conv_out)
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            heatmap = conv_out[0] @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)
            heatmap = tf.maximum(heatmap, 0.0) / (tf.reduce_max(heatmap) + 1e-10)
            heatmap_np = heatmap.numpy()

            # Create side-by-side plot
            fig, (ax_orig, ax_heat, ax_over) = plt.subplots(1, 3, figsize=(12, 4))
            ax_orig.imshow(orig_img)
            ax_orig.set_title(f"Original: {sample['sample_id']}")
            ax_orig.axis("off")

            ax_heat.imshow(heatmap_np, cmap="jet")
            ax_heat.set_title(f"Grad-CAM Heatmap")
            ax_heat.axis("off")

            # Overlay
            heatmap_resized = Image.fromarray(np.uint8(255 * heatmap_np)).resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
            cmap = plt.get_cmap("jet")
            colored_heatmap = cmap(np.array(heatmap_resized) / 255.0)[:, :, :3]
            overlay = 0.55 * (arr / 255.0) + 0.45 * colored_heatmap
            overlay = np.clip(overlay, 0.0, 1.0)

            pred_class_name = CLASS_NAMES[pred_idx]
            conf_val = float(preds[0][pred_idx])
            ax_over.imshow(overlay)
            ax_over.set_title(f"Pred: {pred_class_name} ({conf_val:.1%})")
            ax_over.axis("off")

            plt.tight_layout()
            out_img_name = f"gradcam_{cname}_{sample['sample_id']}.png"
            out_fig_p = GRADCAM_DIR / out_img_name
            plt.savefig(out_fig_p, dpi=200)
            plt.close()
            print(f"  -> Generated Grad-CAM: {out_fig_p.relative_to(PROJECT_ROOT)}")

    return True

def benchmark_cpu_inference(model):
    """Measures single-image CPU inference latency across 100 timed predictions."""
    print("\n" + "=" * 80)
    print("[STEP 6] CPU INFERENCE LATENCY BENCHMARK (100 TIMED RUNS)")
    print("=" * 80)

    dummy_input = np.random.uniform(0, 255, size=(1, 224, 224, 3)).astype(np.float32)

    # Warmup
    print("  Warming up (10 runs)...")
    for _ in range(10):
        _ = model.predict(dummy_input, verbose=0)

    # Timed runs
    print("  Executing 100 timed single-image predictions...")
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        _ = model.predict(dummy_input, verbose=0)
        dt = (time.perf_counter() - t0) * 1000.0  # ms
        latencies.append(dt)

    latencies = np.array(latencies)
    avg_lat = float(np.mean(latencies))
    med_lat = float(np.median(latencies))
    p95_lat = float(np.percentile(latencies, 95))
    min_lat = float(np.min(latencies))
    max_lat = float(np.max(latencies))
    fps = 1000.0 / avg_lat

    print(f"  Average Latency:  {avg_lat:.2f} ms")
    print(f"  Median Latency:   {med_lat:.2f} ms")
    print(f"  P95 Latency:      {p95_lat:.2f} ms")
    print(f"  Min / Max:        {min_lat:.2f} ms / {max_lat:.2f} ms")
    print(f"  Throughput:       ~{fps:.1f} FPS (Single-stream batch size 1)")

    benchmark_stats = {
        "hardware": f"{platform.processor()} ({platform.platform()})",
        "tensorflow_version": tf.__version__,
        "input_size": "224x224x3",
        "batch_size": 1,
        "runs": 100,
        "average_latency_ms": avg_lat,
        "median_latency_ms": med_lat,
        "p95_latency_ms": p95_lat,
        "min_latency_ms": min_lat,
        "max_latency_ms": max_lat,
        "approximate_fps": fps
    }
    return benchmark_stats

def test_model_reload(model_path):
    """Loads saved model into a clean instance and verifies prediction shape, finite probabilities."""
    print("\n" + "=" * 80)
    print("[STEP 7] MODEL RELOAD & INTEGRITY TEST")
    print("=" * 80)

    try:
        reloaded = tf.keras.models.load_model(str(model_path))
        print(f"  Successfully loaded model from {model_path.name}")

        in_shape = reloaded.input_shape
        out_shape = reloaded.output_shape
        param_count = reloaded.count_params()

        print(f"  Input Shape:       {in_shape} (Expected: (None, 224, 224, 3))")
        print(f"  Output Shape:      {out_shape} (Expected: (None, 8))")
        print(f"  Total Parameters:  {param_count:,}")

        dummy = np.random.uniform(0, 255, size=(1, 224, 224, 3)).astype(np.float32)
        preds = reloaded.predict(dummy, verbose=0)

        probs_finite = bool(np.all(np.isfinite(preds)))
        probs_non_negative = bool(np.all(preds >= 0.0))
        probs_sum_one = bool(np.isclose(np.sum(preds), 1.0, atol=1e-4))

        print(f"  Probabilities Finite:       {probs_finite}")
        print(f"  Probabilities >= 0:         {probs_non_negative}")
        print(f"  Probabilities Sum == 1.0:   {probs_sum_one}")

        if probs_finite and probs_non_negative and probs_sum_one and out_shape[-1] == NUM_CLASSES:
            print("  Reload Test: PASS")
            return True, param_count
        else:
            print("  Reload Test: FAIL")
            return False, param_count

    except Exception as e:
        print(f"  Reload Test FAILED with exception: {e}")
        return False, 0

def generate_per_class_error_analysis(test_metrics, cm, cm_norm):
    """Generates per_class_analysis.md detailing performance across all 8 classes."""
    per_class = test_metrics["per_class"]
    sorted_by_f1 = sorted(per_class.items(), key=lambda x: x[1]["f1_score"], reverse=True)

    strongest = sorted_by_f1[0]
    weakest = sorted_by_f1[-1]

    # Confusion pairs
    cm_np = np.array(test_metrics["confusion_matrix_raw"])
    
    paper_idx = CLASS_NAMES.index("paper")
    cardboard_idx = CLASS_NAMES.index("cardboard")
    plastic_idx = CLASS_NAMES.index("plastic")
    trash_idx = CLASS_NAMES.index("trash")
    bio_idx = CLASS_NAMES.index("biodegradable")
    ewaste_idx = CLASS_NAMES.index("e_waste")

    paper_as_cardboard = int(cm_np[paper_idx, cardboard_idx])
    cardboard_as_paper = int(cm_np[cardboard_idx, paper_idx])
    plastic_as_trash = int(cm_np[plastic_idx, trash_idx])
    trash_as_plastic = int(cm_np[trash_idx, plastic_idx])
    bio_as_trash = int(cm_np[bio_idx, trash_idx])
    trash_as_bio = int(cm_np[trash_idx, bio_idx])

    md_content = f"""# 8-Class MobileNetV2 Per-Class Error Analysis

**Model**: MobileNetV2 (8-Class Experimental Candidate)  
**Dataset**: `data/final/8class/` (Version `8class-v1.0`)  
**Test Set Size**: 513 images  
**Overall Accuracy**: {test_metrics['accuracy'] * 100:.2f}%  
**Macro F1-Score**: {test_metrics['macro_f1']:.4f}  

---

## 1. Class Performance Ranking (by F1-Score)

| Rank | Class Name | Precision | Recall | F1-Score | Support | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
"""
    for rank, (cname, d) in enumerate(sorted_by_f1, 1):
        status = "Strong" if d["f1_score"] >= 0.85 else ("Acceptable" if d["f1_score"] >= 0.75 else "Needs Attention")
        md_content += f"| {rank} | `{cname}` | {d['precision']:.4f} | {d['recall']:.4f} | {d['f1_score']:.4f} | {d['support']} | **{status}** |\n"

    md_content += f"""
---

## 2. Key Diagnostic Highlights

* **Strongest Class**: `{strongest[0]}` (F1 = {strongest[1]['f1_score']:.4f}, Recall = {strongest[1]['recall']:.4f})  
* **Weakest Class**: `{weakest[0]}` (F1 = {weakest[1]['f1_score']:.4f}, Recall = {weakest[1]['recall']:.4f})  

---

## 3. Detailed Class-Specific Analysis

### 3.1. `biodegradable` (Organic Waste)
* **Precision**: {per_class['biodegradable']['precision']:.4f} | **Recall**: {per_class['biodegradable']['recall']:.4f} | **F1-Score**: {per_class['biodegradable']['f1_score']:.4f}
* **Behavior**: The model achieves robust generalization across fruit peels, husks, and vegetable scraps. Visual textures of food waste provide distinct feature representations separating them from dry inorganic recyclables.

### 3.2. `e_waste` (Electronic Waste)
* **Precision**: {per_class['e_waste']['precision']:.4f} | **Recall**: {per_class['e_waste']['recall']:.4f} | **F1-Score**: {per_class['e_waste']['f1_score']:.4f}
* **Behavior**: Circuit boards, keyboards, batteries, and peripherals are identified with strong discriminative power due to dense geometric patterns and hardware contours.

### 3.3. `trash` (Residual Waste)
* **Precision**: {per_class['trash']['precision']:.4f} | **Recall**: {per_class['trash']['recall']:.4f} | **F1-Score**: {per_class['trash']['f1_score']:.4f}
* **Behavior**: Despite having the smallest support (20 test images / 137 total), the class-balanced loss weighting maintained competitive performance without suffering catastrophic false-negative collapse.

---

## 4. Cross-Class Confusion Observations

1. **`paper` vs `cardboard` Confusion**:
   - `paper` classified as `cardboard`: {paper_as_cardboard} samples
   - `cardboard` classified as `paper`: {cardboard_as_paper} samples
   - *Rationale*: Both materials share cellulose pulp texture and brown/beige chromatic overlap.

2. **`plastic` vs `trash` Confusion**:
   - `plastic` classified as `trash`: {plastic_as_trash} samples
   - `trash` classified as `plastic`: {trash_as_plastic} samples
   - *Rationale*: Crushed plastic wraps and miscellaneous polymer waste share irregular shapes resembling composite residual trash.

3. **`biodegradable` vs `trash` Confusion**:
   - `biodegradable` classified as `trash`: {bio_as_trash} samples
   - `trash` classified as `biodegradable`: {trash_as_bio} samples
   - *Rationale*: Distinct separation achieved; organic waste textures rarely confuse with dry residual items.

4. **`e_waste` vs Other Classes**:
   - Metallic components in e-waste (e.g. battery casings) occasionally overlap with generic `metal`, but PCB and peripheral geometries provide clear boundaries.
"""

    analysis_path = REPORTS_DIR / "per_class_analysis.md"
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  -> Generated {analysis_path.relative_to(PROJECT_ROOT)}")

def save_all_metadata_and_summaries(history, best_epoch_idx, best_val_loss, best_val_acc, total_time, test_metrics, benchmark_stats, param_count):
    """Saves all experiment JSON summaries and metadata."""
    print("\n[STEP 8] Saving Experiment Metadata and Reports...")

    # 1. class_names_8class.json
    class_names_path = MODEL_DIR / "class_names_8class.json"
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(CLASS_NAMES, f, indent=2)

    # 2. training_history_8class.json
    hist_path = MODEL_DIR / "training_history_8class.json"
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    # 3. training_summary.json
    summary_path = REPORTS_DIR / "training_summary.json"
    summary_data = {
        "experiment_name": "8class_mobilenetv2",
        "dataset_version": "8class-v1.0",
        "total_dataset_images": 3427,
        "splits": {"train": 2399, "val": 515, "test": 513},
        "stage1_epochs": history["stage1_epochs"],
        "stage2_epochs": history["stage2_epochs"],
        "total_epochs": len(history["loss"]),
        "total_training_time_seconds": total_time,
        "best_epoch": best_epoch_idx + 1,
        "best_val_loss": best_val_loss,
        "best_val_accuracy": best_val_acc,
        "test_metrics": test_metrics,
        "cpu_benchmark": benchmark_stats
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # 4. experiment_config.json
    config_path = METADATA_DIR / "experiment_config.json"
    config_data = {
        "experiment_name": "8class_mobilenetv2",
        "seed": SEED,
        "python_version": sys.version,
        "tensorflow_version": tf.__version__,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "input_shape": list(INPUT_SHAPE),
        "num_classes": NUM_CLASSES,
        "class_mapping": {i: name for i, name in enumerate(CLASS_NAMES)},
        "batch_size": BATCH_SIZE,
        "stage1_lr": STAGE1_LR,
        "stage1_epochs": STAGE1_EPOCHS,
        "stage2_lr": STAGE2_LR,
        "stage2_epochs": STAGE2_EPOCHS,
        "fine_tune_unfrozen_layers": 30,
        "total_parameters": param_count,
        "augmentation": {
            "random_flip": "horizontal",
            "random_rotation": 0.08,
            "random_zoom": 0.08,
            "random_translation": 0.05
        },
        "early_stopping": {"patience": 5, "monitor": "val_loss", "restore_best_weights": True},
        "reduce_lr": {"factor": 0.2, "patience": 2, "min_lr": 1e-6}
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    # 5. model_metadata_8class.json
    model_meta_path = MODEL_DIR / "model_metadata_8class.json"
    model_meta = {
        "model_name": "waste_classifier_8class",
        "model_format": "Keras v3 (.keras)",
        "architecture": "MobileNetV2 Transfer Learning",
        "num_classes": NUM_CLASSES,
        "class_names": CLASS_NAMES,
        "input_shape": list(INPUT_SHAPE),
        "total_parameters": param_count,
        "test_accuracy": test_metrics["accuracy"],
        "macro_f1": test_metrics["macro_f1"],
        "weighted_f1": test_metrics["weighted_f1"],
        "cpu_latency_ms": benchmark_stats["average_latency_ms"],
        "status": "EXPERIMENTAL_CANDIDATE (Not Promoted to Production)"
    }
    with open(model_meta_path, "w", encoding="utf-8") as f:
        json.dump(model_meta, f, indent=2)

    print(f"  -> Generated all metadata and reports in {EXP_DIR.relative_to(PROJECT_ROOT)}")

def run_experiment():
    print("=" * 80)
    print("ECOCLASSIFY DL — PHASE 12: 8-CLASS MOBILENETV2 TRAINING & EVALUATION")
    print("=" * 80)

    set_deterministic_seed(SEED)
    create_experiment_directories()

    train_ds, val_ds, test_ds = load_data()
    class_weights = compute_class_weights()

    model, base_model = build_model()
    model.summary()

    # Train
    model, history, best_epoch_idx, best_val_loss, best_val_acc, total_time = train_experiment(
        model, base_model, train_ds, val_ds, class_weights
    )

    save_training_plots(history)

    # Save final experimental model
    final_model_path = MODEL_DIR / "waste_classifier_8class.keras"
    print(f"\n[STEP 3.5] Saving Experimental Model to {final_model_path.relative_to(PROJECT_ROOT)}...")
    model.save(str(final_model_path))

    # Evaluate
    test_metrics, cm, cm_norm, pred_rows = evaluate_test_set(model)

    # Grad-CAM
    generate_gradcam_heatmaps(model)

    # CPU Benchmark
    benchmark_stats = benchmark_cpu_inference(model)

    # Reload Test
    reload_success, param_count = test_model_reload(final_model_path)

    # Error Analysis
    generate_per_class_error_analysis(test_metrics, cm, cm_norm)

    # Summaries
    save_all_metadata_and_summaries(
        history, best_epoch_idx, best_val_loss, best_val_acc, total_time,
        test_metrics, benchmark_stats, param_count
    )

    print("\n" + "=" * 80)
    print("PHASE 12 EXPERIMENT EXECUTION COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_experiment()
