#!/usr/bin/env python3
"""
Final Model Exporter.
Exports selected best model and metadata to artifacts/final/
"""
import sys
import shutil
import json
from pathlib import Path

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import tensorflow as tf

# Add project root to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import (
    CLASSES,
    INPUT_SHAPE,
    RANDOM_SEED,
    CNN_ARTIFACTS_DIR,
    MOBILENET_ARTIFACTS_DIR,
    EVALUATION_DIR,
    FINAL_ARTIFACTS_DIR
)


def export_final_model():
    print("=" * 70)
    print("           Exporting Final Selected Model & Metadata")
    print("=" * 70)

    comparison_path = EVALUATION_DIR / "model_comparison.json"
    if not comparison_path.exists():
        print(f"[FAIL] Evaluation comparison not found at {comparison_path}. Run evaluate.py first.")
        return False

    with open(comparison_path, "r", encoding="utf-8") as f:
        comparison = json.load(f)

    selected = comparison["selected_model"]
    print(f"Selected Model based on evaluation: '{selected}'")

    if selected == "mobilenetv2":
        source_model_path = MOBILENET_ARTIFACTS_DIR / "best_model.keras"
        source_config_path = MOBILENET_ARTIFACTS_DIR / "config.json"
        source_metrics_path = MOBILENET_ARTIFACTS_DIR / "test_metrics.json"
        model_name = "MobileNetV2 (Transfer Learning)"
    else:
        source_model_path = CNN_ARTIFACTS_DIR / "best_model.keras"
        source_config_path = CNN_ARTIFACTS_DIR / "config.json"
        source_metrics_path = CNN_ARTIFACTS_DIR / "test_metrics.json"
        model_name = "Custom CNN Baseline"

    # Copy best model to final
    target_model_path = FINAL_ARTIFACTS_DIR / "waste_classifier.keras"
    shutil.copy2(source_model_path, target_model_path)
    print(f"  [OK] Model binary exported: {target_model_path.relative_to(PROJECT_ROOT)}")

    # Class names
    class_names_path = FINAL_ARTIFACTS_DIR / "class_names.json"
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(CLASSES, f, indent=2)
    print(f"  [OK] Class names exported: {class_names_path.relative_to(PROJECT_ROOT)}")

    # Metrics
    with open(source_metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)
    final_metrics_path = FINAL_ARTIFACTS_DIR / "metrics.json"
    with open(final_metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"  [OK] Metrics exported: {final_metrics_path.relative_to(PROJECT_ROOT)}")

    # Load model to count parameters
    loaded_model = tf.keras.models.load_model(str(target_model_path))
    total_params = int(loaded_model.count_params())

    # Metadata
    with open(source_config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    metadata = {
        "model_name": model_name,
        "model_architecture": selected,
        "framework": f"TensorFlow {tf.__version__} / Keras {tf.keras.__version__}",
        "input_shape": list(INPUT_SHAPE),
        "classes": CLASSES,
        "num_classes": len(CLASSES),
        "total_parameters": total_params,
        "dataset_split": {
            "train": 1769,
            "val": 379,
            "test": 379,
            "total": 2527
        },
        "test_accuracy": metrics_data["accuracy"],
        "macro_precision": metrics_data["macro_precision"],
        "macro_recall": metrics_data["macro_recall"],
        "macro_f1": metrics_data["macro_f1"],
        "weighted_f1": metrics_data["weighted_f1"],
        "random_seed": RANDOM_SEED,
        "training_config": cfg
    }

    metadata_path = FINAL_ARTIFACTS_DIR / "model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  [OK] Model metadata exported: {metadata_path.relative_to(PROJECT_ROOT)}")

    print("=" * 70)
    print("           Final Model Export Complete")
    print("=" * 70)
    return True


if __name__ == "__main__":
    export_final_model()
