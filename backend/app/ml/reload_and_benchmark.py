#!/usr/bin/env python3
"""
Model Reload & CPU Inference Benchmark Verification Script.
"""
import sys
import time
import json
from pathlib import Path

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import numpy as np
from PIL import Image
import tensorflow as tf

# Add project root to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.model_config import (
    FINAL_ARTIFACTS_DIR,
    TEST_DIR,
    CLASSES
)
from backend.app.ml.preprocessing import preprocess_single_image_for_inference


def run_reload_and_benchmark():
    print("=" * 70)
    print("      Isolated Model Reload & CPU Inference Benchmark Test")
    print("=" * 70)

    model_path = FINAL_ARTIFACTS_DIR / "waste_classifier.keras"
    class_names_path = FINAL_ARTIFACTS_DIR / "class_names.json"
    metadata_path = FINAL_ARTIFACTS_DIR / "model_metadata.json"

    # 1. Verify files exist
    if not model_path.exists() or not class_names_path.exists():
        print(f"[FAIL] Exported model files missing from {FINAL_ARTIFACTS_DIR}")
        return False

    # 2. Reload Model and Class Names
    print("Step 1: Loading model and metadata from disk...")
    model = tf.keras.models.load_model(str(model_path))
    with open(class_names_path, "r", encoding="utf-8") as f:
        loaded_classes = json.load(f)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    arch = metadata.get("model_architecture", "mobilenetv2")
    print(f"  [OK] Model successfully reloaded: {metadata['model_name']}")
    print(f"  [OK] Classes ({len(loaded_classes)}): {loaded_classes}")

    # 3. Test on sample images from test directory
    sample_images = []
    for cls in CLASSES:
        cls_test_dir = TEST_DIR / cls
        files = list(cls_test_dir.iterdir())
        if files:
            sample_images.append((files[0], cls))

    print(f"\nStep 2: Testing single-image prediction on {len(sample_images)} test samples...")
    verification_passed = True
    latencies = []

    for img_path, true_cls in sample_images:
        with Image.open(img_path) as pil_img:
            input_tensor = preprocess_single_image_for_inference(pil_img, model_type=arch)

        # Measure latency
        t0 = time.perf_counter()
        preds = model.predict(input_tensor, verbose=0)[0]
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0
        latencies.append(latency_ms)

        pred_idx = int(np.argmax(preds))
        pred_cls = loaded_classes[pred_idx]
        confidence = float(preds[pred_idx])
        prob_sum = float(np.sum(preds))

        # Checks
        shape_ok = (preds.shape == (6,))
        sum_ok = (0.99 <= prob_sum <= 1.01)
        cls_ok = (pred_cls in loaded_classes)

        status_str = "PASS" if (shape_ok and sum_ok and cls_ok) else "FAIL"
        if status_str == "FAIL":
            verification_passed = False

        print(f"  [{status_str}] File: {img_path.name:<18} | True: {true_cls:<10} | Pred: {pred_cls:<10} | Conf: {confidence*100:>5.1f}% | ProbSum: {prob_sum:.4f} | Latency: {latency_ms:.1f}ms")

    # 4. CPU Benchmark Statistics
    print("\n----------------------------------------------------------------------")
    print("CPU Inference Benchmark Results")
    print("----------------------------------------------------------------------")
    # Warmup + 20 runs
    warmup_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)
    for _ in range(5):
        _ = model.predict(warmup_tensor, verbose=0)

    benchmark_times = []
    for img_path, _ in sample_images * 4:
        with Image.open(img_path) as pil_img:
            input_tensor = preprocess_single_image_for_inference(pil_img, model_type=arch)
        t0 = time.perf_counter()
        _ = model.predict(input_tensor, verbose=0)
        t1 = time.perf_counter()
        benchmark_times.append((t1 - t0) * 1000.0)

    avg_ms = float(np.mean(benchmark_times))
    min_ms = float(np.min(benchmark_times))
    max_ms = float(np.max(benchmark_times))
    p95_ms = float(np.percentile(benchmark_times, 95))

    print(f"  Average Inference Latency : {avg_ms:.2f} ms")
    print(f"  Minimum Inference Latency : {min_ms:.2f} ms")
    print(f"  Maximum Inference Latency : {max_ms:.2f} ms")
    print(f"  95th Percentile Latency   : {p95_ms:.2f} ms")
    print(f"  Throughput (approx)       : {1000.0 / avg_ms:.1f} FPS on CPU")

    # Save benchmark to final metadata
    metadata["cpu_inference_benchmark"] = {
        "avg_latency_ms": round(avg_ms, 2),
        "min_latency_ms": round(min_ms, 2),
        "max_latency_ms": round(max_ms, 2),
        "p95_latency_ms": round(p95_ms, 2),
        "approx_fps": round(1000.0 / avg_ms, 1)
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 70)
    if verification_passed:
        print("           MODEL RELOAD & BENCHMARK: PASS")
    else:
        print("           MODEL RELOAD & BENCHMARK: FAIL")
    print("=" * 70)
    return verification_passed


if __name__ == "__main__":
    success = run_reload_and_benchmark()
    sys.exit(0 if success else 1)
