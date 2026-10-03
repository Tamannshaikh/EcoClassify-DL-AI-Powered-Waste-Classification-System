# API Specification

**Base URL**: `http://127.0.0.1:8000/api/v1`

---

## 1. Health & Status
### `GET /api/v1/health`
Returns backend service health, model loading status, and registered classes.

**Response (`200 OK`)**:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "MobileNetV2 (Transfer Learning)",
  "model_version": "v1.0",
  "classes": ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
}
```

---

## 2. Model Metadata & Metrics
### `GET /api/v1/model/info`
Returns architectural metadata, parameter counts, and test accuracy.

**Response (`200 OK`)**:
```json
{
  "model_name": "MobileNetV2 (Transfer Learning)",
  "model_architecture": "mobilenetv2",
  "framework": "TensorFlow / Keras",
  "input_shape": [224, 224, 3],
  "classes": ["cardboard", "glass", "metal", "paper", "plastic", "trash"],
  "num_classes": 6,
  "total_parameters": 2422726,
  "test_accuracy": 0.8707,
  "macro_precision": 0.8623,
  "macro_recall": 0.8444,
  "macro_f1": 0.8514,
  "weighted_f1": 0.8700,
  "training_config": {
    "epochs_completed": 30,
    "fine_tuned": true,
    "optimizer": "adam"
  },
  "cpu_inference_benchmark": {
    "average_inference_ms": 61.15,
    "min_inference_ms": 52.34,
    "max_inference_ms": 84.12,
    "p95_inference_ms": 65.34,
    "test_runs": 100
  }
}
```

### `GET /api/v1/model/metrics`
Returns comprehensive evaluation metrics, per-class breakdown, and 6x6 test confusion matrix.

**Response (`200 OK`)**:
```json
{
  "accuracy": 0.8707,
  "macro_precision": 0.8623,
  "macro_recall": 0.8444,
  "macro_f1": 0.8514,
  "weighted_f1": 0.8700,
  "per_class": {
    "cardboard": {"precision": 0.8852, "recall": 0.8852, "f1_score": 0.8852, "support": 61},
    "glass": {"precision": 0.8873, "recall": 0.8400, "f1_score": 0.8630, "support": 75},
    "metal": {"precision": 0.8462, "recall": 0.9016, "f1_score": 0.8730, "support": 61},
    "paper": {"precision": 0.9091, "recall": 0.8989, "f1_score": 0.9040, "support": 89},
    "plastic": {"precision": 0.8333, "recall": 0.8904, "f1_score": 0.8609, "support": 73},
    "trash": {"precision": 0.8125, "recall": 0.6500, "f1_score": 0.7222, "support": 20}
  },
  "confusion_matrix": [
    [54, 1, 1, 3, 2, 0],
    [1, 63, 2, 1, 8, 0],
    [0, 2, 55, 1, 3, 0],
    [3, 0, 1, 80, 4, 1],
    [3, 4, 1, 0, 65, 0],
    [0, 1, 5, 1, 0, 13]
  ]
}
```

---

## 3. Dataset Information
### `GET /api/v1/dataset/info`
Returns total dataset counts, class distributions, and 70/15/15 stratified splits.

**Response (`200 OK`)**:
```json
{
  "dataset_name": "TrashNet (Yang & Thung, Stanford)",
  "total_images": 2527,
  "classes": ["cardboard", "glass", "metal", "paper", "plastic", "trash"],
  "class_distribution": [
    {"class_name": "cardboard", "count": 403, "percentage": 15.95},
    {"class_name": "glass", "count": 501, "percentage": 19.83},
    {"class_name": "metal", "count": 410, "percentage": 16.22},
    {"class_name": "paper", "count": 594, "percentage": 23.51},
    {"class_name": "plastic", "count": 482, "percentage": 19.07},
    {"class_name": "trash", "count": 137, "percentage": 5.42}
  ],
  "splits": {"train": 1769, "val": 379, "test": 379, "total": 2527},
  "dimensions": "512 x 384 (100% uniform RGB)"
}
```

### `GET /api/v1/dataset/classes`
Returns the 6 class names and raw image frequencies.

---

## 4. Deep Learning Prediction & Grad-CAM
### `POST /api/v1/predict`
Accepts multipart image upload (`file`) and returns predicted class and all 6 probabilities.

**Response (`200 OK`)**:
```json
{
  "prediction_id": "70b4dbfc-2b57-40ab-a66e-e48e7788b60c",
  "filename": "70b4dbfc-2b57-40ab-a66e-e48e7788b60c_plastic100.jpg",
  "predicted_class": "plastic",
  "confidence": 0.9868,
  "probabilities": {
    "cardboard": 0.0000,
    "glass": 0.0098,
    "metal": 0.0000,
    "paper": 0.0001,
    "plastic": 0.9868,
    "trash": 0.0032
  },
  "inference_time_ms": 65.19,
  "model_version": "v1.0",
  "gradcam_base64": null
}
```

### `POST /api/v1/predict/gradcam`
Executes classification and generates a Base64-encoded Grad-CAM activation heatmap overlay.

**Response (`200 OK`)**:
Same schema as `/predict` with `gradcam_base64` populated with `data:image/jpeg;base64,...`.

---

## 5. Prediction History (SQLite)
### `GET /api/v1/predictions`
Returns paginated list of stored predictions sorted by `created_at DESC`.

**Query Parameters**:
- `limit` (default: 50, min: 1, max: 200)
- `offset` (default: 0)

### `GET /api/v1/predictions/{id}`
Retrieves a single prediction by its UUID string or numeric ID.

### `DELETE /api/v1/predictions/{id}`
Deletes a prediction record from SQLite. Returns `HTTP 404` if not found.

---

## 6. Standard Error Format
```json
{
  "detail": {
    "code": "INVALID_IMAGE_FILE",
    "message": "Uploaded file is corrupted or not a valid readable image."
  }
}
```

**HTTP Status Codes**:
- `200 OK`: Request succeeded.
- `400 Bad Request`: Invalid file format, corrupted image, or empty upload.
- `404 Not Found`: Record not found.
- `413 Content Too Large`: Payload exceeds maximum size limit (10MB).
- `422 Unprocessable Entity`: Parameter validation error.
- `503 Service Unavailable`: Deep learning model not loaded.
