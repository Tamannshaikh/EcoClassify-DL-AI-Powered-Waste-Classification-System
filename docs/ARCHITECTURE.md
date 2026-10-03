# System Architecture Document

## 1. High-Level Architecture Overview

The **AI-Powered Waste Classification System** is engineered as a local-first, full-stack Deep Learning vision platform. It combines a trained MobileNetV2 convolutional neural network, a high-throughput asynchronous FastAPI REST backend, a lightweight local SQLite persistence layer, and a responsive React single-page dashboard.

```
+-------------------------------------------------------------------------------+
|                                 USER CLIENT                                   |
|   +-----------------------------------------------------------------------+   |
|   |                      React + TypeScript Frontend                      |   |
|   |   (Vite, Tailwind CSS, React Router, Recharts, Lucide React Icons)    |   |
|   +-----------------------------------+-----------------------------------+   |
+---------------------------------------|---------------------------------------+
                                        | HTTP (REST API / Multipart)
                                        v
+-------------------------------------------------------------------------------+
|                            FASTAPI BACKEND SERVER                             |
|   +-----------------------------------------------------------------------+   |
|   |  Routes: /health, /model/*, /dataset/*, /predict, /predict/gradcam    |   |
|   |  Pydantic V2 Request & Response Validation, CORS Middleware           |   |
|   +-----------------------------------+-----------------------------------+   |
|                                       |                                       |
|                  +--------------------+--------------------+                  |
|                  |                                         |                  |
|                  v                                         v                  |
|   +-----------------------------+           +-----------------------------+   |
|   |   Singleton ModelManager    |           |   SQLite Database Layer     |   |
|   |   - In-memory MobileNetV2   |           |   - predictions table       |   |
|   |   - Warmup Inference        |           |   - Full probabilities JSON |   |
|   |   - Grad-CAM Engine         |           |   - Created timestamps      |   |
|   +--------------+--------------+           +--------------+--------------+   |
+------------------|-----------------------------------------|------------------+
                   |                                         |
                   v                                         v
+---------------------------------------+ +-------------------------------------+
|        ARTIFACTS & ML WEIGHTS         | |         PERSISTENT STORAGE          |
|  - waste_classifier.keras (23.8 MB)   | |  - data/waste_classification.db     |
|  - class_names.json                   | |  - data/processed/ (train/val/test) |
|  - model_metadata.json & metrics.json | |  - data/raw/TrashNet/               |
+---------------------------------------+ +-------------------------------------+
```

---

## 2. Detailed Data Flow Pipelines

### A. Real-Time Prediction Pipeline (`POST /api/v1/predict`)
```
1. User selects/drops waste photo in React UI
   ↓
2. Client-side validation (Size <= 10MB, Format in [.jpg, .jpeg, .png])
   ↓
3. Multipart file dispatched via Axios to POST /api/v1/predict
   ↓
4. FastAPI Backend Validations:
   - File extension check
   - Payload byte size boundary (<10MB)
   - Pillow structure header validation & RGB conversion
   ↓
5. Deterministic Preprocessing:
   - Resize to 224×224 bilinear
   - Scale to [-1, 1] using MobileNetV2 normalizer
   ↓
6. Singleton Model Inference:
   - Single forward pass through MobileNetV2 in memory
   - Softmax output across 6 classes
   ↓
7. SQLite Audit Logging:
   - Insert record (UUID, predicted_class, confidence, probabilities_json, latency)
   ↓
8. Return JSON response to Client
```

### B. Grad-CAM Explainability Pipeline (`POST /api/v1/predict/gradcam`)
```
1. Client requests Grad-CAM enabled classification
   ↓
2. Backend runs forward pass through MobileNetV2
   ↓
3. Extract convolutional feature activations from 'out_relu' (7x7x1280)
   ↓
4. Calculate gradients of predicted class logit with respect to feature maps (tf.GradientTape)
   ↓
5. Compute channel-wise global average pooled gradients (alpha weights)
   ↓
6. Compute weighted linear combination of feature maps & apply ReLU
   ↓
7. Normalize heatmap to [0, 1] & resize to original image dimensions
   ↓
8. Apply Matplotlib 'Jet' colormap & blend with original image (alpha=0.45)
   ↓
9. Encode resulting image as Base64 JPEG Data URI
   ↓
10. Transmit Base64 payload alongside class predictions to React Frontend
```

---

## 3. SQLite Database Schema

```sql
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    predicted_class TEXT NOT NULL,
    confidence REAL NOT NULL,
    probabilities_json TEXT NOT NULL,
    inference_time_ms REAL NOT NULL,
    model_version TEXT NOT NULL,
    gradcam_generated INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL
);
```
