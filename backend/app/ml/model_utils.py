"""
Model Utility Functions: Callbacks, Evaluation, Plotting, and Metrics Serialization.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support
)
import tensorflow as tf

from backend.app.ml.model_config import CLASSES, NUM_CLASSES


def get_training_callbacks(
    checkpoint_path: Path,
    patience_es: int = 5,
    patience_lr: int = 3
) -> List[tf.keras.callbacks.Callback]:
    """
    Standard robust training callbacks:
    - ModelCheckpoint (save best weights)
    - EarlyStopping (restore best weights)
    - ReduceLROnPlateau (decay learning rate on plateau)
    """
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_path),
            monitor="val_loss",
            mode="min",
            save_best_only=True,
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            mode="min",
            patience=patience_es,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            mode="min",
            factor=0.2,
            patience=patience_lr,
            min_lr=1e-6,
            verbose=1
        )
    ]
    return callbacks


def save_training_history(history: tf.keras.callbacks.History, save_path: Path) -> Dict[str, Any]:
    """Saves Keras history dictionary to JSON with float conversion."""
    clean_history = {}
    for k, v in history.history.items():
        clean_history[k] = [float(round(x, 5)) for x in v]
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(clean_history, f, indent=2)
    return clean_history


def plot_and_save_training_curves(
    history_dict: Dict[str, List[float]],
    save_path: Path,
    title: str = "Training Curves"
) -> None:
    """Plots and saves loss and accuracy curves."""
    epochs = range(1, len(history_dict["loss"]) + 1)
    
    plt.figure(figsize=(12, 5))

    # Loss plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs, history_dict["loss"], "b-o", label="Train Loss")
    if "val_loss" in history_dict:
        plt.plot(epochs, history_dict["val_loss"], "r--s", label="Val Loss")
    plt.title(f"{title} - Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Accuracy plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs, history_dict["accuracy"], "b-o", label="Train Accuracy")
    if "val_accuracy" in history_dict:
        plt.plot(epochs, history_dict["val_accuracy"], "r--s", label="Val Accuracy")
    plt.title(f"{title} - Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()


def evaluate_model_on_dataset(
    model: tf.keras.Model,
    dataset: tf.data.Dataset,
    class_names: List[str] = CLASSES
) -> Dict[str, Any]:
    """
    Comprehensive evaluation returning:
    - accuracy, macro/weighted precision, recall, F1
    - per-class breakdown
    - raw and normalized confusion matrix
    """
    y_true = []
    y_pred_probs = []

    for images, labels in dataset:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy())
        y_pred_probs.extend(preds)

    y_true = np.array(y_true)
    y_pred_probs = np.array(y_pred_probs)
    y_pred = np.argmax(y_pred_probs, axis=1)

    acc = float(accuracy_score(y_true, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_weight, r_weight, f1_weight, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    
    p_class, r_class, f1_class, support_class = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)

    per_class_metrics = {}
    for idx, cls in enumerate(class_names):
        per_class_metrics[cls] = {
            "precision": float(round(p_class[idx], 4)),
            "recall": float(round(r_class[idx], 4)),
            "f1_score": float(round(f1_class[idx], 4)),
            "support": int(support_class[idx])
        }

    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    
    metrics = {
        "accuracy": float(round(acc, 4)),
        "macro_precision": float(round(p_macro, 4)),
        "macro_recall": float(round(r_macro, 4)),
        "macro_f1": float(round(f1_macro, 4)),
        "weighted_f1": float(round(f1_weight, 4)),
        "per_class": per_class_metrics,
        "confusion_matrix": cm.tolist()
    }

    return metrics, y_true, y_pred, y_pred_probs


def plot_and_save_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    save_path: Path,
    title: str = "Confusion Matrix"
) -> None:
    """Plots and saves confusion matrix heatmap."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names
    )
    plt.title(title, fontsize=14, pad=12)
    plt.xlabel("Predicted Class", fontsize=12)
    plt.ylabel("True Class", fontsize=12)
    plt.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()
