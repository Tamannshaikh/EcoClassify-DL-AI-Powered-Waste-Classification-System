"""
Class weight computation module for imbalanced TrashNet dataset.
"""
import sys
from pathlib import Path
from typing import Dict
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import TRAIN_DIR, CLASSES, CLASS_TO_IDX


def compute_training_class_weights(train_dir: Path = TRAIN_DIR) -> Dict[int, float]:
    """
    Computes balanced class weights using inverse frequency on actual training samples.
    formula: n_samples / (n_classes * np.bincount(y))
    """
    labels = []
    for cls in CLASSES:
        cls_path = train_dir / cls
        if cls_path.exists():
            count = len([f for f in cls_path.iterdir() if f.is_file()])
            labels.extend([CLASS_TO_IDX[cls]] * count)

    labels = np.array(labels)
    unique_classes = np.unique(labels)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=unique_classes,
        y=labels
    )
    class_weight_dict = {int(cls): float(round(w, 4)) for cls, w in zip(unique_classes, weights)}
    return class_weight_dict


if __name__ == "__main__":
    weights = compute_training_class_weights()
    print("Computed Class Weights:")
    for cls, idx in CLASS_TO_IDX.items():
        print(f"  {cls:<12} (class {idx}): {weights.get(idx, 1.0)}")
