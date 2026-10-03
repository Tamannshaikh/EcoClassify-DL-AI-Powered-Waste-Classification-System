# Screenshot Checklist for Final Academic Report & Presentation

Use this checklist to capture high-resolution screenshots for the final thesis document, presentation slides, and project submission.

---

## 1. Application UI Screenshots (`http://localhost:5173`)

| # | Screen / State | Route | Recommended Dimensions | Key Features to Highlight |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Main Dashboard** | `/` | 1920×1080 | 4 KPI cards (87.07% accuracy, 2527 images), class distribution chart, active model card, recent predictions table. |
| **2** | **Image Upload (Idle State)** | `/predict` | 1920×1080 | Drag & drop dropzone, format tags (JPG/JPEG/PNG), Grad-CAM toggle checkbox. |
| **3** | **Prediction Result (Original Photo)** | `/predict` | 1920×1080 | Image preview, top class badge, 98%+ confidence score, inference latency, disposal guide, 6-class probability bars. |
| **4** | **Grad-CAM Activation Heatmap** | `/predict` | 1920×1080 | Base64 Jet colormap overlay highlighting object contours, model attention visualizer. |
| **5** | **Prediction Audit History** | `/history` | 1920×1080 | Paginated history table with timestamps, filenames, predicted classes, and action buttons. |
| **6** | **Prediction Detail Modal** | `/history` | 1920×1080 | Audit inspection modal showing UUID, original filename, and full 6-class probability distribution. |
| **7** | **Dataset Inventory Page** | `/dataset` | 1920×1080 | Recharts class distribution chart, 70/15/15 stratified split donut chart, class composition table. |
| **8** | **Model Evaluation & Metrics** | `/performance` | 1920×1080 | Per-class metric bar chart, 6×6 confusion matrix heatmap, CPU benchmark card. |
| **9** | **Training Lab Comparison** | `/training` | 1920×1080 | Side-by-side architecture comparison cards (Custom CNN vs MobileNetV2), +18.47% accuracy delta banner, comparison matrix. |
| **10** | **About System Page** | `/about` | 1920×1080 | Deep learning tech stack grid, architecture description, and Stanford TrashNet academic citation block. |
| **11** | **System Settings & Monitor** | `/settings` | 1920×1080 | Live FastAPI ping status (ms), model weights runtime information, client & server security diagnostics. |

---

## 2. Backend & Developer Tool Screenshots

| # | Component | URL / Tool | Key Features to Highlight |
| :-: | :--- | :--- | :--- |
| **12** | **FastAPI Swagger Docs** | `http://127.0.0.1:8000/docs` | Interactive OpenAPI documentation showing all `/api/v1` routes with request/response schemas. |
| **13** | **ReDoc API Documentation** | `http://127.0.0.1:8000/redoc` | Clean hierarchical API specification documentation. |
| **14** | **Pytest Test Execution** | Terminal (`pytest -v`) | All 16 unit and integration test cases passing with green status. |
| **15** | **E2E Integration Audit** | Terminal (`python e2e`) | Output of `scripts/e2e_full_system_test.py` showing all 7 audit sectors passed with 100% success. |
