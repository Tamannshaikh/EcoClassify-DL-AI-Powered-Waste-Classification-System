"""
Phase 7: Comprehensive Full System Integration, End-to-End Testing & QA Script.
Tests dataset integrity, model artifacts, backend endpoints, 6-class real predictions,
Grad-CAM explainability, SQLite persistence, and security controls.
"""
import sys
import json
import time
from pathlib import Path
import numpy as np
import tensorflow as tf
from PIL import Image
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.config import (
    DATA_DIR,
    PROCESSED_DIR,
    TRAIN_DIR,
    VAL_DIR,
    TEST_DIR,
    FINAL_ARTIFACTS_DIR,
    DEFAULT_MODEL_PATH,
    DEFAULT_CLASS_NAMES_PATH,
    DEFAULT_METADATA_PATH,
    DEFAULT_METRICS_PATH,
    DB_PATH,
)

CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

def test_full_system():
    results = {}
    print("=" * 75)
    print("PHASE 7 — FULL SYSTEM INTEGRATION & END-TO-END QA AUDIT")
    print("=" * 75)

    # -------------------------------------------------------------
    # 1. DATASET INTEGRITY VERIFICATION
    # -------------------------------------------------------------
    print("\n[STEP 1] Verifying Dataset Integrity & Splits...")
    raw_dir = DATA_DIR / "raw" / "TrashNet"
    raw_counts = {}
    total_raw = 0
    for cls in CLASSES:
        cls_dir = raw_dir / cls
        assert cls_dir.exists(), f"Missing raw directory: {cls_dir}"
        count = len(list(cls_dir.glob("*.jpg")))
        raw_counts[cls] = count
        total_raw += count

    assert total_raw == 2527, f"Expected 2527 raw images, found {total_raw}"
    print(f"  Raw TrashNet Images: {total_raw} across 6 classes: {raw_counts}")

    # Check processed splits
    train_count = sum(len(list((TRAIN_DIR / c).glob("*.jpg"))) for c in CLASSES)
    val_count = sum(len(list((VAL_DIR / c).glob("*.jpg"))) for c in CLASSES)
    test_count = sum(len(list((TEST_DIR / c).glob("*.jpg"))) for c in CLASSES)

    assert train_count == 1769, f"Expected 1769 train images, got {train_count}"
    assert val_count == 379, f"Expected 379 val images, got {val_count}"
    assert test_count == 379, f"Expected 379 test images, got {test_count}"
    assert train_count + val_count + test_count == 2527

    print(f"  Processed Splits: Train={train_count} (70%), Val={val_count} (15%), Test={test_count} (15%)")
    print("  -> PASS: Dataset integrity & split counts 100% verified.")
    results["dataset_integrity"] = "PASS"

    # -------------------------------------------------------------
    # 2. MODEL ARTIFACT VERIFICATION
    # -------------------------------------------------------------
    print("\n[STEP 2] Verifying Final Model Artifacts...")
    assert DEFAULT_MODEL_PATH.exists(), f"Model file missing: {DEFAULT_MODEL_PATH}"
    assert DEFAULT_CLASS_NAMES_PATH.exists(), "class_names.json missing"
    assert DEFAULT_METADATA_PATH.exists(), "model_metadata.json missing"
    assert DEFAULT_METRICS_PATH.exists(), "metrics.json missing"

    with open(DEFAULT_CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
        loaded_classes = json.load(f)
    assert loaded_classes == CLASSES, f"Mismatch in class names: {loaded_classes}"

    with open(DEFAULT_METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["test_accuracy"] >= 0.87
    assert meta["macro_f1"] >= 0.85
    assert meta["total_parameters"] == 2422726

    print(f"  Loaded Model Architecture: {meta['model_architecture']} ({meta['total_parameters']:,} parameters)")
    print(f"  Recorded Test Accuracy: {meta['test_accuracy']*100:.2f}%, Macro F1: {meta['macro_f1']*100:.2f}%")
    print("  -> PASS: Final model artifacts verified.")
    results["model_artifacts"] = "PASS"

    # -------------------------------------------------------------
    # 3. BACKEND & API TESTS WITH TESTCLIENT
    # -------------------------------------------------------------
    with TestClient(app) as client:
        print("\n[STEP 3] Testing Core API Endpoints...")
        # 3a. Health
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        health = res.json()
        assert health["status"] == "ok"
        assert health["model_loaded"] is True
        assert health["classes"] == CLASSES
        print("  GET /api/v1/health -> 200 OK (Model loaded & ready)")

        # 3b. Model Info
        res = client.get("/api/v1/model/info")
        assert res.status_code == 200
        info = res.json()
        assert info["num_classes"] == 6
        print("  GET /api/v1/model/info -> 200 OK")

        # 3c. Model Metrics
        res = client.get("/api/v1/model/metrics")
        assert res.status_code == 200
        metrics = res.json()
        assert len(metrics["confusion_matrix"]) == 6
        print("  GET /api/v1/model/metrics -> 200 OK")

        # 3d. Dataset Info & Classes
        res = client.get("/api/v1/dataset/info")
        assert res.status_code == 200
        assert res.json()["total_images"] == 2527
        res2 = client.get("/api/v1/dataset/classes")
        assert res2.status_code == 200
        assert res2.json()["total"] == 2527
        print("  GET /api/v1/dataset/info & /dataset/classes -> 200 OK")
        results["api_core"] = "PASS"

        # -------------------------------------------------------------
        # 4. REAL PREDICTIONS ACROSS ALL 6 TEST CLASSES
        # -------------------------------------------------------------
        print("\n[STEP 4] Executing Real Inference on All 6 Test Classes...")
        prediction_records = []
        latencies = []

        for cls in CLASSES:
            test_cls_dir = TEST_DIR / cls
            test_files = list(test_cls_dir.glob("*.jpg"))
            assert len(test_files) > 0, f"No test files found for {cls}"
            sample_file = test_files[0]

            with open(sample_file, "rb") as f:
                img_bytes = f.read()

            t0 = time.perf_counter()
            res = client.post("/api/v1/predict", files={"file": (sample_file.name, img_bytes, "image/jpeg")})
            t1 = time.perf_counter()

            assert res.status_code == 200, f"Predict failed for {cls}: {res.text}"
            data = res.json()

            # Assertions on response structure
            assert data["predicted_class"] in CLASSES
            assert 0.0 <= data["confidence"] <= 1.0
            assert len(data["probabilities"]) == 6
            prob_sum = sum(data["probabilities"].values())
            assert abs(prob_sum - 1.0) < 0.05
            assert data["inference_time_ms"] > 0

            elapsed_ms = (t1 - t0) * 1000.0
            latencies.append(data["inference_time_ms"])
            prediction_records.append({
                "true_class": cls,
                "file": sample_file.name,
                "predicted": data["predicted_class"],
                "confidence": data["confidence"],
                "inference_ms": data["inference_time_ms"],
                "prediction_id": data["prediction_id"]
            })

            print(f"  [{cls.upper():<9}] Image: {sample_file.name:<16} -> Predicted: {data['predicted_class']:<9} (Confidence: {data['confidence']*100:.2f}%, Latency: {data['inference_time_ms']} ms)")

        avg_lat = np.mean(latencies)
        print(f"  Average Model CPU Inference Latency: {avg_lat:.2f} ms")
        print("  -> PASS: All 6 classes classified with authentic 6-class probability distribution.")
        results["prediction_6_classes"] = "PASS"

        # -------------------------------------------------------------
        # 5. GRAD-CAM END-TO-END VERIFICATION
        # -------------------------------------------------------------
        print("\n[STEP 5] Testing Grad-CAM Activation Heatmap Generation...")
        grad_sample = list((TEST_DIR / "glass").glob("*.jpg"))[0]
        with open(grad_sample, "rb") as f:
            glass_bytes = f.read()

        t0 = time.perf_counter()
        res_grad = client.post("/api/v1/predict/gradcam", files={"file": (grad_sample.name, glass_bytes, "image/jpeg")})
        t1 = time.perf_counter()

        assert res_grad.status_code == 200
        grad_res = res_grad.json()
        assert grad_res["gradcam_base64"] is not None
        assert grad_res["gradcam_base64"].startswith("data:image/jpeg;base64,")
        print(f"  Grad-CAM Image: {grad_sample.name} -> Class: {grad_res['predicted_class']}, Confidence: {grad_res['confidence']*100:.2f}%")
        print(f"  Base64 Payload Length: {len(grad_res['gradcam_base64'])} chars, E2E Latency: {(t1-t0)*1000:.2f} ms")
        print("  -> PASS: Grad-CAM overlay generated successfully.")
        results["gradcam"] = "PASS"

        # -------------------------------------------------------------
        # 6. SQLITE PREDICTION HISTORY VERIFICATION
        # -------------------------------------------------------------
        print("\n[STEP 6] Testing SQLite History Persistence...")
        res_hist = client.get("/api/v1/predictions?limit=10")
        assert res_hist.status_code == 200
        hist_data = res_hist.json()
        assert hist_data["total"] >= len(prediction_records)
        print(f"  Total Persisted Predictions in SQLite: {hist_data['total']}")

        # Retrieve single prediction detail
        test_pred_id = prediction_records[0]["prediction_id"]
        res_single = client.get(f"/api/v1/predictions/{test_pred_id}")
        assert res_single.status_code == 200
        single = res_single.json()
        assert single["prediction_id"] == test_pred_id
        assert len(single["probabilities"]) == 6
        print(f"  Retrieved Detail for ID {test_pred_id[:8]}... -> Verified 6 probabilities in SQLite.")

        # Delete one record and confirm 404
        del_target = prediction_records[-1]["prediction_id"]
        res_del = client.delete(f"/api/v1/predictions/{del_target}")
        assert res_del.status_code == 200
        res_verify_del = client.get(f"/api/v1/predictions/{del_target}")
        assert res_verify_del.status_code == 404
        print(f"  Deleted Record ID {del_target[:8]}... -> Confirmed deletion with 404 on subsequent lookup.")
        print("  -> PASS: SQLite database CRUD lifecycle fully operational.")
        results["sqlite_history"] = "PASS"

        # -------------------------------------------------------------
        # 7. SECURITY CONTROLS & ERROR HANDLING
        # -------------------------------------------------------------
        print("\n[STEP 7] Testing Security Boundaries & Exception Handling...")
        # 7a. Invalid extension (.txt)
        r1 = client.post("/api/v1/predict", files={"file": ("malicious.txt", b"plain text", "text/plain")})
        assert r1.status_code == 400
        assert r1.json()["detail"]["code"] == "INVALID_FILE_EXTENSION"

        # 7b. Corrupted JPEG
        r2 = client.post("/api/v1/predict", files={"file": ("corrupt.jpg", b"INVALID_RAW_BYTES_XYZ", "image/jpeg")})
        assert r2.status_code == 400
        assert r2.json()["detail"]["code"] == "INVALID_IMAGE_FILE"

        # 7c. Oversized file (11MB)
        r3 = client.post("/api/v1/predict", files={"file": ("huge.jpg", b"0" * (11 * 1024 * 1024), "image/jpeg")})
        assert r3.status_code == 413
        assert r3.json()["detail"]["code"] == "FILE_TOO_LARGE"

        # 7d. Empty file
        r4 = client.post("/api/v1/predict", files={"file": ("empty.jpg", b"", "image/jpeg")})
        assert r4.status_code == 400
        assert r4.json()["detail"]["code"] == "EMPTY_FILE"

        # 7e. Delete non-existent ID
        r5 = client.delete("/api/v1/predictions/nonexistent-id-0000")
        assert r5.status_code == 404
        assert r5.json()["detail"]["code"] == "NOT_FOUND"

        print("  Verified: Invalid extension (400), Corrupted image (400), Oversized file (413), Empty file (400), Nonexistent ID (404).")
        print("  -> PASS: All security and validation rules enforced cleanly.")
        results["security_error_handling"] = "PASS"

    print("\n" + "=" * 75)
    print("PHASE 7 INTEGRATION AUDIT: ALL 7 AUDIT SECTORS PASSED (100% SUCCESS)")
    print("=" * 75)
    return results

if __name__ == "__main__":
    test_full_system()
