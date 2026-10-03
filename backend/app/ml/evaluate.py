#!/usr/bin/env python3
"""
Model Evaluation and Objective Comparison Script.

Evaluates both Custom CNN and MobileNetV2 on the unseen TEST set.
Generates confusion matrices, per-class metrics, and comparison reports.
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
import tensorflow as tf

# Add project root to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import (
    CLASSES,
    CNN_ARTIFACTS_DIR,
    MOBILENET_ARTIFACTS_DIR,
    EVALUATION_DIR
)
from backend.app.ml.data_loader import load_datasets
from backend.app.ml.model_utils import (
    evaluate_model_on_dataset,
    plot_and_save_confusion_matrix
)


def evaluate_both_models():
    print("=" * 70)
    print("      TrashNet Deep Learning Model Test Evaluation & Comparison")
    print("=" * 70)

    # 1. Load test dataset
    _, _, test_ds = load_datasets()

    # 2. Evaluate Custom CNN Baseline
    cnn_model_path = CNN_ARTIFACTS_DIR / "best_model.keras"
    if not cnn_model_path.exists():
        print(f"[FAIL] CNN model not found at {cnn_model_path}")
        return False

    print(f"\n--- 1. Evaluating Custom CNN Baseline on Test Set ---")
    cnn_model = tf.keras.models.load_model(str(cnn_model_path))
    cnn_metrics, y_true_cnn, y_pred_cnn, y_probs_cnn = evaluate_model_on_dataset(
        cnn_model, test_ds, class_names=CLASSES
    )

    cnn_cm = np.array(cnn_metrics["confusion_matrix"])
    plot_and_save_confusion_matrix(
        cnn_cm, CLASSES,
        EVALUATION_DIR / "cnn_confusion_matrix.png",
        title="Custom CNN Baseline - Test Confusion Matrix"
    )
    with open(CNN_ARTIFACTS_DIR / "test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(cnn_metrics, f, indent=2)

    print(f"  Accuracy       : {cnn_metrics['accuracy'] * 100:.2f}%")
    print(f"  Macro F1-Score : {cnn_metrics['macro_f1'] * 100:.2f}%")
    print(f"  Weighted F1    : {cnn_metrics['weighted_f1'] * 100:.2f}%")

    # 3. Evaluate MobileNetV2 Transfer Learning
    mobilenet_model_path = MOBILENET_ARTIFACTS_DIR / "best_model.keras"
    if not mobilenet_model_path.exists():
        print(f"[FAIL] MobileNetV2 model not found at {mobilenet_model_path}")
        return False

    print(f"\n--- 2. Evaluating MobileNetV2 Transfer Learning on Test Set ---")
    mobilenet_model = tf.keras.models.load_model(str(mobilenet_model_path))
    mb_metrics, y_true_mb, y_pred_mb, y_probs_mb = evaluate_model_on_dataset(
        mobilenet_model, test_ds, class_names=CLASSES
    )

    mb_cm = np.array(mb_metrics["confusion_matrix"])
    plot_and_save_confusion_matrix(
        mb_cm, CLASSES,
        EVALUATION_DIR / "mobilenetv2_confusion_matrix.png",
        title="MobileNetV2 - Test Confusion Matrix"
    )
    with open(MOBILENET_ARTIFACTS_DIR / "test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(mb_metrics, f, indent=2)

    print(f"  Accuracy       : {mb_metrics['accuracy'] * 100:.2f}%")
    print(f"  Macro F1-Score : {mb_metrics['macro_f1'] * 100:.2f}%")
    print(f"  Weighted F1    : {mb_metrics['weighted_f1'] * 100:.2f}%")

    # 4. Model Comparison
    comparison = {
        "models": {
            "custom_cnn": {
                "name": "Custom CNN Baseline",
                "accuracy": cnn_metrics["accuracy"],
                "macro_precision": cnn_metrics["macro_precision"],
                "macro_recall": cnn_metrics["macro_recall"],
                "macro_f1": cnn_metrics["macro_f1"],
                "weighted_f1": cnn_metrics["weighted_f1"],
                "per_class": cnn_metrics["per_class"]
            },
            "mobilenetv2": {
                "name": "MobileNetV2 Transfer Learning",
                "accuracy": mb_metrics["accuracy"],
                "macro_precision": mb_metrics["macro_precision"],
                "macro_recall": mb_metrics["macro_recall"],
                "macro_f1": mb_metrics["macro_f1"],
                "weighted_f1": mb_metrics["weighted_f1"],
                "per_class": mb_metrics["per_class"]
            }
        },
        "selected_model": "mobilenetv2" if mb_metrics["macro_f1"] >= cnn_metrics["macro_f1"] else "custom_cnn",
        "dataset_duplicate_notes": "The 3 cross-class byte duplicate pairs (glass/metal, glass/plastic) were co-located in the training set to prevent evaluation leakage."
    }

    with open(EVALUATION_DIR / "model_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)

    # 5. Generate Markdown Comparison Report
    md_report = f"""# Model Performance Comparison Report

## Summary Table

| Metric | Custom CNN Baseline | MobileNetV2 (Transfer Learning) | Winner |
| :--- | :---: | :---: | :---: |
| **Test Accuracy** | {cnn_metrics['accuracy']*100:.2f}% | {mb_metrics['accuracy']*100:.2f}% | **{'MobileNetV2' if mb_metrics['accuracy'] >= cnn_metrics['accuracy'] else 'Custom CNN'}** |
| **Macro Precision** | {cnn_metrics['macro_precision']*100:.2f}% | {mb_metrics['macro_precision']*100:.2f}% | **{'MobileNetV2' if mb_metrics['macro_precision'] >= cnn_metrics['macro_precision'] else 'Custom CNN'}** |
| **Macro Recall** | {cnn_metrics['macro_recall']*100:.2f}% | {mb_metrics['macro_recall']*100:.2f}% | **{'MobileNetV2' if mb_metrics['macro_recall'] >= cnn_metrics['macro_recall'] else 'Custom CNN'}** |
| **Macro F1-Score** | {cnn_metrics['macro_f1']*100:.2f}% | {mb_metrics['macro_f1']*100:.2f}% | **{'MobileNetV2' if mb_metrics['macro_f1'] >= cnn_metrics['macro_f1'] else 'Custom CNN'}** |
| **Weighted F1-Score** | {cnn_metrics['weighted_f1']*100:.2f}% | {mb_metrics['weighted_f1']*100:.2f}% | **{'MobileNetV2' if mb_metrics['weighted_f1'] >= cnn_metrics['weighted_f1'] else 'Custom CNN'}** |

---

## Per-Class Breakdown (Test Set)

### Custom CNN Baseline:
| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
"""
    for cls in CLASSES:
        c = cnn_metrics["per_class"][cls]
        md_report += f"| **{cls}** | {c['precision']*100:.2f}% | {c['recall']*100:.2f}% | {c['f1_score']*100:.2f}% | {c['support']} |\n"

    md_report += f"""
### MobileNetV2 (Transfer Learning):
| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
"""
    for cls in CLASSES:
        m = mb_metrics["per_class"][cls]
        md_report += f"| **{cls}** | {m['precision']*100:.2f}% | {m['recall']*100:.2f}% | {m['f1_score']*100:.2f}% | {m['support']} |\n"

    md_report += f"""
---

## Dataset Ambiguity Note
The TrashNet dataset contains 3 pairs of identical byte-duplicate images labelled under different classes (glass ↔ metal, glass ↔ plastic). These pairs were co-located strictly in the training partition, guaranteeing clean, uncontaminated test and validation evaluation sets.
"""

    with open(EVALUATION_DIR / "model_comparison.md", "w", encoding="utf-8") as f:
        f.write(md_report)

    print(f"\n[OK] Model evaluation completed. Comparison written to {EVALUATION_DIR / 'model_comparison.md'}")
    return True


if __name__ == "__main__":
    evaluate_both_models()
