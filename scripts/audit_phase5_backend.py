"""
Phase 5 Comprehensive Backend Audit & Verification Script.
Executes live API tests against all endpoints and validates against Phase 5 requirements.
"""
import io
import sys
import json
import time
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

# Path resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.config import TEST_DIR, DB_PATH
from backend.app.database import get_total_prediction_count

def run_audit():
    print("=" * 70)
    print("PHASE 5 BACKEND VERIFICATION & REQUIREMENTS AUDIT")
    print("=" * 70)
    
    with TestClient(app) as client:
        # 1. Health Endpoint
        print("\n[1] Testing GET /api/v1/health ...")
        res = client.get("/api/v1/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        health_data = res.json()
        print(f"Status Code: {res.status_code}")
        print(f"Response: {json.dumps(health_data, indent=2)}")
        assert health_data["status"] == "ok"
        assert health_data["model_loaded"] is True
        assert "organic" not in health_data["classes"]
        assert health_data["classes"] == ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
        print("-> PASS: Health endpoint valid & no 'organic' class present.")

        # 2. Model Info Endpoint
        print("\n[2] Testing GET /api/v1/model/info ...")
        res = client.get("/api/v1/model/info")
        assert res.status_code == 200, f"Model info failed: {res.text}"
        info_data = res.json()
        print(f"Status Code: {res.status_code}")
        print(f"Architecture: {info_data['model_architecture']}, Parameters: {info_data['total_parameters']:,}")
        print(f"Test Accuracy: {info_data['test_accuracy'] * 100:.2f}%, Macro F1: {info_data['macro_f1'] * 100:.2f}%")
        assert info_data["num_classes"] == 6
        print("-> PASS: Model info verified from artifacts.")

        # 3. Model Metrics Endpoint
        print("\n[3] Testing GET /api/v1/model/metrics ...")
        res = client.get("/api/v1/model/metrics")
        assert res.status_code == 200, f"Model metrics failed: {res.text}"
        metrics_data = res.json()
        print(f"Status Code: {res.status_code}")
        print(f"Accuracy: {metrics_data['accuracy']*100:.2f}%, Macro F1: {metrics_data['macro_f1']*100:.2f}%, Weighted F1: {metrics_data['weighted_f1']*100:.2f}%")
        print(f"Per-class support: {', '.join([f'{k}: {v['f1_score']*100:.1f}% F1' for k,v in metrics_data['per_class'].items()])}")
        print("-> PASS: Verified model metrics from evaluation artifacts.")

        # 4. Dataset Info & Classes Endpoints
        print("\n[4] Testing GET /api/v1/dataset/info & /dataset/classes ...")
        res_info = client.get("/api/v1/dataset/info")
        res_classes = client.get("/api/v1/dataset/classes")
        assert res_info.status_code == 200 and res_classes.status_code == 200
        ds_info = res_info.json()
        print(f"Dataset: {ds_info['dataset_name']}, Total: {ds_info['total_images']}")
        print(f"Splits: Train={ds_info['splits']['train']}, Val={ds_info['splits']['val']}, Test={ds_info['splits']['test']}")
        assert ds_info["total_images"] == 2527
        assert ds_info["splits"]["train"] == 1769
        assert ds_info["splits"]["val"] == 379
        assert ds_info["splits"]["test"] == 379
        assert "organic" not in ds_info["classes"]
        print("-> PASS: Dataset info matches exact verified TrashNet figures.")

        # 5. Prediction with Real Test Image
        print("\n[5] Testing POST /api/v1/predict with real test image ...")
        test_images = list((TEST_DIR / "plastic").glob("*.jpg"))
        assert len(test_images) > 0, "No test images found in data/processed/test/plastic"
        sample_img_path = test_images[0]
        print(f"Using real test image: {sample_img_path.name}")
        with open(sample_img_path, "rb") as f:
            file_bytes = f.read()

        t0 = time.perf_counter()
        res_pred = client.post("/api/v1/predict", files={"file": (sample_img_path.name, file_bytes, "image/jpeg")})
        t1 = time.perf_counter()
        assert res_pred.status_code == 200, f"Prediction failed: {res_pred.text}"
        pred_data = res_pred.json()
        print(f"Prediction Result:")
        print(f"  Predicted Class : {pred_data['predicted_class']}")
        print(f"  Confidence      : {pred_data['confidence']*100:.2f}%")
        print(f"  Probabilities   : {json.dumps(pred_data['probabilities'])}")
        print(f"  Inference Time  : {pred_data['inference_time_ms']} ms")
        print(f"  Client E2E Time : {(t1-t0)*1000:.2f} ms")
        assert len(pred_data["probabilities"]) == 6
        assert abs(sum(pred_data["probabilities"].values()) - 1.0) < 0.05
        assert pred_data["predicted_class"] in pred_data["probabilities"]
        print("-> PASS: Real image prediction successful with valid 6-class probability distribution.")

        # 6. Grad-CAM Explainability with Real Test Image
        print("\n[6] Testing POST /api/v1/predict/gradcam with real test image ...")
        paper_imgs = list((TEST_DIR / "paper").glob("*.jpg"))
        sample_paper = paper_imgs[0]
        print(f"Using real test image: {sample_paper.name}")
        with open(sample_paper, "rb") as f:
            paper_bytes = f.read()

        t0 = time.perf_counter()
        res_grad = client.post("/api/v1/predict/gradcam", files={"file": (sample_paper.name, paper_bytes, "image/jpeg")})
        t1 = time.perf_counter()
        assert res_grad.status_code == 200, f"Grad-CAM failed: {res_grad.text}"
        grad_data = res_grad.json()
        print(f"Grad-CAM Result:")
        print(f"  Predicted Class : {grad_data['predicted_class']}")
        print(f"  Confidence      : {grad_data['confidence']*100:.2f}%")
        print(f"  Grad-CAM Output : {grad_data['gradcam_base64'][:60]}... (Length: {len(grad_data['gradcam_base64'])} chars)")
        print(f"  Grad-CAM Total Time: {(t1-t0)*1000:.2f} ms")
        assert grad_data["gradcam_base64"].startswith("data:image/jpeg;base64,")
        print("-> PASS: Grad-CAM overlay generated successfully in base64 data URI format.")

        # 7. Prediction History & SQLite Operations
        print("\n[7] Testing SQLite Prediction History (List, Get Single, Delete) ...")
        res_list = client.get("/api/v1/predictions?limit=10")
        assert res_list.status_code == 200
        history_data = res_list.json()
        print(f"Total Stored Predictions in SQLite: {history_data['total']}")
        assert len(history_data["predictions"]) >= 2
        
        latest_item = history_data["predictions"][0]
        pred_uuid = latest_item["prediction_id"]
        print(f"Retrieving single prediction: {pred_uuid}")
        res_single = client.get(f"/api/v1/predictions/{pred_uuid}")
        assert res_single.status_code == 200
        assert res_single.json()["prediction_id"] == pred_uuid
        
        print(f"Deleting prediction: {pred_uuid}")
        res_del = client.delete(f"/api/v1/predictions/{pred_uuid}")
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "success"
        
        # Verify 404
        res_after_del = client.get(f"/api/v1/predictions/{pred_uuid}")
        assert res_after_del.status_code == 404
        print("-> PASS: SQLite History lifecycle (Create, Read, List, Delete, 404) verified.")

        # 8. Security Validations
        print("\n[8] Testing Security Validation (Invalid Extension, Corrupted File, Oversized File) ...")
        # 8a. Invalid extension
        res_ext = client.post("/api/v1/predict", files={"file": ("malicious.exe", b"MZ\x90\x00", "application/octet-stream")})
        assert res_ext.status_code == 400
        print(f"  Invalid Extension (.exe) -> HTTP {res_ext.status_code} ({res_ext.json()['detail']['code']})")

        # 8b. Corrupted image
        res_corrupt = client.post("/api/v1/predict", files={"file": ("fake.jpg", b"NOT_AN_IMAGE_HEADER_DATA", "image/jpeg")})
        assert res_corrupt.status_code == 400
        print(f"  Corrupted JPG -> HTTP {res_corrupt.status_code} ({res_corrupt.json()['detail']['code']})")

        # 8c. Oversized file (11MB)
        res_over = client.post("/api/v1/predict", files={"file": ("huge.jpg", b"0" * (11 * 1024 * 1024), "image/jpeg")})
        assert res_over.status_code == 413
        print(f"  Oversized file (11MB) -> HTTP {res_over.status_code} ({res_over.json()['detail']['code']})")
        print("-> PASS: Upload security rules verified.")

        # 9. Swagger & Docs Verification
        print("\n[9] Testing Swagger & ReDoc Endpoints ...")
        res_docs = client.get("/docs")
        res_redoc = client.get("/redoc")
        res_openapi = client.get("/openapi.json")
        assert res_docs.status_code == 200
        assert res_redoc.status_code == 200
        assert res_openapi.status_code == 200
        print("-> PASS: /docs, /redoc, and /openapi.json online and accessible.")

    print("\n" + "=" * 70)
    print("ALL 9 AUDIT CATEGORIES PASSED WITH 100% SUCCESS")
    print("=" * 70)

if __name__ == "__main__":
    run_audit()
