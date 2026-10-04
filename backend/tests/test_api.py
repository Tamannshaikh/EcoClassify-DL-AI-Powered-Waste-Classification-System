"""
Backend API Unit and Integration Tests.
Tests all endpoints: health, model info, dataset, predictions, Grad-CAM, and history.
"""
import io
import sys
from pathlib import Path
from PIL import Image
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.config import TEST_DIR


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["api_prefix"] == "/api/v1"


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert len(data["classes"]) == 8
    assert "biodegradable" in data["classes"]
    assert "e_waste" in data["classes"]
    assert "plastic" in data["classes"]
    assert "trash" in data["classes"]


def test_model_info_endpoint(client):
    response = client.get("/api/v1/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_architecture"] == "mobilenetv2"
    assert data["num_classes"] == 8
    assert data["test_accuracy"] > 0.80
    assert "classes" in data
    assert len(data["classes"]) == 8


def test_model_metrics_endpoint(client):
    response = client.get("/api/v1/model/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "accuracy" in data
    assert "macro_f1" in data
    assert "per_class" in data
    assert "confusion_matrix" in data
    assert len(data["confusion_matrix"]) == 8
    assert len(data["per_class"]) == 8


def test_dataset_info_endpoint(client):
    response = client.get("/api/v1/dataset/info")
    assert response.status_code == 200
    data = response.json()
    assert data["total_images"] == 3427
    assert len(data["class_distribution"]) == 8
    assert data["splits"]["train"] == 2399
    assert data["splits"]["val"] == 515
    assert data["splits"]["test"] == 513


def test_dataset_classes_endpoint(client):
    response = client.get("/api/v1/dataset/classes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["classes"]) == 8
    assert data["total"] == 3427


def test_predict_endpoint_real_image(client):
    # Find a real image from test set
    sample_file = list((TEST_DIR / "plastic").iterdir())[0]
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/predict",
        files={"file": (sample_file.name, file_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert data["predicted_class"] in [
        "biodegradable", "cardboard", "e_waste", "glass", "metal", "paper", "plastic", "trash"
    ]
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["probabilities"]) == 8
    assert abs(sum(data["probabilities"].values()) - 1.0) < 0.05
    assert data["inference_time_ms"] > 0


def test_predict_gradcam_endpoint(client):
    sample_file = list((TEST_DIR / "paper").iterdir())[0]
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/predict/gradcam",
        files={"file": (sample_file.name, file_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert data["gradcam_base64"] is not None
    assert data["gradcam_base64"].startswith("data:image/jpeg;base64,")


def test_predict_invalid_extension(client):
    fake_txt = io.BytesIO(b"Hello world, not an image.")
    response = client.post(
        "/api/v1/predict",
        files={"file": ("test.txt", fake_txt, "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_FILE_EXTENSION"


def test_predict_corrupted_image(client):
    fake_corrupted_jpg = io.BytesIO(b"This is not a real JPEG file content")
    response = client.post(
        "/api/v1/predict",
        files={"file": ("corrupt.jpg", fake_corrupted_jpg, "image/jpeg")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_IMAGE_FILE"


def test_docs_endpoints(client):
    response = client.get("/docs")
    assert response.status_code == 200
    response = client.get("/redoc")
    assert response.status_code == 200
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Smart Waste Classification System"


def test_predict_endpoint_png_image(client):
    img = Image.new("RGB", (224, 224), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/v1/predict",
        files={"file": ("test_synthetic.png", buf.getvalue(), "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] in [
        "biodegradable", "cardboard", "e_waste", "glass", "metal", "paper", "plastic", "trash"
    ]


def test_predict_empty_file(client):
    response = client.post(
        "/api/v1/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "EMPTY_FILE"


def test_predict_oversized_file(client):
    oversized_data = b"x" * (11 * 1024 * 1024)  # 11 MB > 10MB limit
    response = client.post(
        "/api/v1/predict",
        files={"file": ("oversized.jpg", oversized_data, "image/jpeg")}
    )
    assert response.status_code == 413
    data = response.json()
    assert data["detail"]["code"] == "FILE_TOO_LARGE"


def test_delete_nonexistent_prediction(client):
    response = client.delete("/api/v1/predictions/non-existent-uuid-99999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "NOT_FOUND"


def test_predict_category_id_and_image_storage(client):
    sample_file = list((TEST_DIR / "metal").iterdir())[0]
    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/predict",
        files={"file": ("test_metal.jpg", file_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    pred_id = data["prediction_id"]
    pred_class = data["predicted_class"]

    # Verify category prefix matches mapping
    from backend.app.config import CATEGORY_PREFIXES
    expected_prefix = CATEGORY_PREFIXES[pred_class.lower()]
    assert pred_id.startswith(expected_prefix)
    assert "image_url" in data
    assert data["image_url"] == f"/api/v1/predictions/{pred_id}/image"

    # Test image retrieval endpoint
    img_resp = client.get(f"/api/v1/predictions/{pred_id}/image")
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] in ["image/jpeg", "image/png"]
    assert len(img_resp.content) > 0

    # Test invalid prediction ID image retrieval
    bad_img_resp = client.get("/api/v1/predictions/INVALID_ID_999/image")
    assert bad_img_resp.status_code == 404

    # Test deletion removes image from disk
    del_resp = client.delete(f"/api/v1/predictions/{pred_id}")
    assert del_resp.status_code == 200

    # Verify image retrieval returns 404 after deletion
    post_del_img_resp = client.get(f"/api/v1/predictions/{pred_id}/image")
    assert post_del_img_resp.status_code == 404


def test_independent_category_counters(client):
    from backend.app.database import get_next_prediction_id
    
    # Generate sequential IDs for biodegradable (TB), e_waste (TE), cardboard (TC), glass (TG)
    tb1 = get_next_prediction_id("biodegradable")
    te1 = get_next_prediction_id("e_waste")
    tc1 = get_next_prediction_id("cardboard")
    tg1 = get_next_prediction_id("glass")
    tc2 = get_next_prediction_id("cardboard")
    tpl1 = get_next_prediction_id("plastic")

    assert tb1.startswith("TB")
    assert te1.startswith("TE")
    assert tc1.startswith("TC")
    assert tg1.startswith("TG")
    assert tc2.startswith("TC")
    assert tpl1.startswith("TPL")

    num_tc1 = int(tc1.replace("TC", ""))
    num_tc2 = int(tc2.replace("TC", ""))
    assert num_tc2 == num_tc1 + 1


