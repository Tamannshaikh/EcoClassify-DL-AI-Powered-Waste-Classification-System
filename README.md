# EcoClassify DL — AI-Powered Waste Classification System

> **Application / Product Branding**: EcoClassify DL  
> **Production Version**: `v2.0.0-8class` | **Release Dataset**: `8class-v1.0` (3,427 images across 8 classes)  
> **Core Deep Learning Architecture**: MobileNetV2 Transfer Learning (2,422,984 parameters)  
> **Production Validation Metrics**: **Test Accuracy: 89.08%** | **Macro F1: 87.81%** | **Weighted F1: 89.20%**  
> **Explainable AI**: Grad-CAM Visual Heatmaps (`mobilenetv2_1.00_224::out_relu`)  
> **Full-Stack Technology**: React 18 + Vite + TypeScript + Tailwind CSS | FastAPI + SQLite + TensorFlow 2.16+

---

## Current Release

- **Version**: `v2.0.0-8class`
- **Active Dataset**: `8class-v1.0` (3,427 images across 8 classes)
- **Status**: Production-ready local academic & research release
- **GitHub Tags**:
  - `v1.0.0-baseline`: Frozen original 6-class production baseline (Commit: `9a3dff36f29295f51459eb4a6712852b78f35678`)
  - `v2.0.0-8class`: Current production 8-class release (Commit: `dd56337850bb8b84b9042b3fb0028fa72b5aa03a`)

---

## Prerequisites

Before running the project, make sure you have installed:

1. **Python 3.10, 3.11, or 3.12** (Verify with `python --version`)
2. **Node.js 18+ and npm** (Verify with `node -v` and `npm -v`)
3. **Git** (Verify with `git --version`)

### Recommended Environment
- **Operating System**: Windows 10/11, macOS, or Linux
- **System Memory**: 8 GB+ RAM recommended (4 GB minimum)
- **Disk Space**: ~3 GB free space (for 8-class dataset, dependencies, model weights, and node modules)
- **Internet Connection**: Required only for initial package installations (`pip` and `npm`)

> **Key Information**:  
> - **No GPU is required** for inference (CPU execution averages ~88.65 ms).  
> - **No username / password is required** (local-first standalone access).  
> - **No external cloud API keys or telemetry** (100% offline & local).

---

## First-Time Setup

Perform these steps **once** when setting up the project:

### 1. Create Python Virtual Environment
Open a terminal in the project root (`Waste_Classification_DL_System`):
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
- **Windows PowerShell**:
  ```powershell
  .\.venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Quick Start (Running the Application)

Start the full-stack system anytime using **2 terminals**:

```
+---------------------------------------------------------------------------------------------------+
| Terminal 1 — FastAPI Backend Service                                                             |
+---------------------------------------------------------------------------------------------------+
| cd Waste_Classification_DL_System                                                                |
| .\.venv\Scripts\activate                                                                          |
| uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload                               |
|                                                                                                   |
| -> API Server:  http://127.0.0.1:8000                                                             |
| -> Swagger UI:  http://127.0.0.1:8000/docs                                                        |
| -> ReDoc UI:    http://127.0.0.1:8000/redoc                                                       |
+---------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------+
| Terminal 2 — React Frontend Web App                                                              |
+---------------------------------------------------------------------------------------------------+
| cd Waste_Classification_DL_System\frontend                                                        |
| npm run dev                                                                                       |
|                                                                                                   |
| -> Application UI: http://localhost:5173                                                          |
+---------------------------------------------------------------------------------------------------+
```

---

## Key Features

### 1. AI Waste Classification
Upload or drag-and-drop any municipal waste image to receive an instant real-time prediction from the production MobileNetV2 deep learning classifier with sub-100 ms latency.

### 2. 8-Class Waste Recognition
The production model recognizes **8 distinct solid and recyclable waste categories**:
1. `biodegradable` — Organic matter, food scraps, fruit/vegetable peels, leaves
2. `cardboard` — Corrugated boxes, packaging cartons, paperboard
3. `e_waste` — Electronic boards, circuit components, batteries, small peripherals
4. `glass` — Beverage bottles, jars, glassware
5. `metal` — Aluminum beverage cans, tin food cans, aerosol canisters
6. `paper` — Office paper, newspapers, magazines, books, envelopes
7. `plastic` — PET/HDPE bottles, containers, plastic cups
8. `trash` — Non-recyclable composite waste, wrappers, contaminated sanitary items

### 3. Explainable AI with Grad-CAM
Visual proof of model reasoning via **Gradient-weighted Class Activation Mapping (Grad-CAM)** targeting the final feature layer:
- **Target Layer**: `mobilenetv2_1.00_224::out_relu`
- Color-coded jet heatmap overlay highlights exact spatial features (rims, labels, textures, electronic circuitry) that drove classification.

### 4. Prediction History & Image Persistence
Full local lifecycle logging in SQLite (`data/waste_classification.db`) and local disk storage (`data/uploads/`):
- Category-specific prediction ID sequence:
  - `TB` — Biodegradable
  - `TC` — Cardboard
  - `TE` — E-Waste
  - `TG` — Glass
  - `TM` — Metal
  - `TP` — Paper
  - `TPL` — Plastic
  - `TT` — Trash
- Full 8-class probability distribution, confidence score, timestamp, inference latency, stored image thumbnail, and cascading deletion.

### 5. Interactive Analytics Dashboard
Executive monitoring displaying system health, total dataset volume, production accuracy, 8-class distribution charts, and recent prediction audit tables.

### 6. Dataset & Model Performance Analytics
- **Dataset Page**: 3,427 image benchmark inventory across 8 classes with exact 70/15/15 split breakdowns and interactive image sample gallery.
- **Performance Page**: 89.08% Test Accuracy, 87.81% Macro F1, 89.20% Weighted F1, 8×8 normalized confusion matrix, and CPU inference latency benchmarks.

### 7. Full-Stack Web Application
Unified end-to-end architecture:
```
React 18 + TypeScript + Vite + Tailwind CSS
                   ↓ (REST API / Axios)
            FastAPI Backend
                   ↓
MobileNetV2 (8-Class Inference) + Grad-CAM Engine
                   ↓
            SQLite Database
```

### 8. Security, Validation & Robustness
- 10 MB payload capping (`413 Request Entity Too Large`).
- Strict extension filtering (`.jpg`, `.jpeg`, `.png`) and in-memory Pillow byte integrity verification (`img.verify()`).
- Server-generated deterministic category IDs preventing user-controlled path overwrites.
- Path containment checks (`Path.relative_to(PROJECT_ROOT)`) preventing path traversal.
- 100% parameterized SQLite statements (`?` placeholders) eliminating SQL injection risks.
- Local CORS scoping restricted to localhost development servers.

---

## Dataset

- **Dataset Identifier**: `8class-v1.0`
- **Total Images**: **3,427 images**
- **Classes**: 8 waste classes
- **Partition Splits**: 70% Train (2,399) / 15% Validation (515) / 15% Test (513)

### Class Distribution Summary

| Class Name | Total Count | Train Count (70%) | Val Count (15%) | Test Count (15%) | Domain Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `biodegradable` | 450 | 315 | 68 | 67 | Food scraps, fruits, vegetables, compostable organics |
| `cardboard` | 403 | 282 | 60 | 61 | Corrugated packaging, carton boxes, paperboard |
| `e_waste` | 450 | 315 | 68 | 67 | Electronic waste, batteries, small electronics, PCBs |
| `glass` | 501 | 351 | 75 | 75 | Transparent, amber, and green glass beverage bottles |
| `metal` | 410 | 287 | 62 | 61 | Aluminum beverage cans, food tins, aerosol containers |
| `paper` | 594 | 416 | 89 | 89 | Office paper, magazines, newspapers, paper sheets |
| `plastic` | 482 | 337 | 72 | 73 | PET/HDPE beverage bottles, containers, plastic cups |
| `trash` | 137 | 96 | 21 | 20 | Non-recyclable mixed materials, wrappers, damaged items |
| **Total** | **3,427** | **2,399** | **515** | **513** | **100% Balanced & Group-Stratified** |

### Dataset Quality Assurance
The unified dataset underwent rigorous automated curation:
- **Duplicate Detection**: SHA-256 exact byte hashing and perceptual hashing (pHash) to detect duplicate or near-duplicate frames.
- **Group-Aware Splitting**: Near-duplicate bursts assigned to identical splits to eliminate train-to-test data leakage.
- **Corruption Validation**: 100% of images verified for standard 3-channel RGB decodability and non-zero dimensions.
- **Provenance Tracking**: Full record of origin source mapped for every image in the dataset manifest.

---

## Dataset Sources

The 8-class dataset combines curated benchmark sources:
1. **TrashNet** (Stanford CS229 / Gary Thung & Mindy Yang): Contributes the baseline 6 classes (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash`).
2. **E-Waste Image Dataset**: Contributes high-quality studio electronic waste items (`e_waste`).
3. **BDWaste**: Contributes verified compostable and organic waste items (`biodegradable`).
4. **CTSoc E-Waste (Audited & Excluded)**: Evaluated during Phase 10 audit but excluded from the final classification pool due to synthetic lighting and studio domain mismatch.

---

## Machine Learning Model

- **Model Architecture**: MobileNetV2 Transfer Learning
- **Input Resolution**: `224 × 224 × 3` RGB
- **Pretrained Weights**: ImageNet
- **Classification Head**:
  - `GlobalAveragePooling2D()`
  - `Dense(128, activation='relu')`
  - `Dropout(0.30)`
  - `Dense(8, activation='softmax')`
- **Total Parameters**: 2,422,984 parameters (9.24 MB file size)
- **Training Strategy**: Two-stage transfer learning
  - **Stage 1 (Frozen Backbone)**: 8 epochs with Adam (`lr=1e-3`), training custom head while feature extractor weights remain frozen.
  - **Stage 2 (Fine-Tuning)**: 12 epochs with Adam (`lr=1e-5`), unfreezing top convolutional layers of MobileNetV2 with cosine decay learning rate.
- **Production Artifact**: `artifacts/final/waste_classifier.keras`

---

## Final Model Results

Evaluation on the independent hold-out test set (513 images across 8 classes):

| Metric | Production 8-Class MobileNetV2 | Baseline CNN (6-Class) | Delta / Note |
| :--- | :---: | :---: | :--- |
| **Test Accuracy** | **89.08%** | 68.60% | **+20.48% pts** |
| **Macro Precision** | **87.44%** | 68.00% | **+19.44% pts** |
| **Macro Recall** | **88.51%** | 69.23% | **+19.28% pts** |
| **Macro F1-Score** | **87.81%** | 65.61% | **+22.20% pts** |
| **Weighted F1-Score** | **89.20%** | 68.94% | **+20.26% pts** |
| **Average CPU Latency** | **~88.65 ms** | ~42.10 ms | Sub-100 ms real-time CPU serving |
| **P95 CPU Latency** | **~98.29 ms** | ~55.00 ms | Deterministic CPU execution |

### Per-Class Test Performance (8 Classes)

| Class | Precision | Recall | F1-Score | Evaluation Support |
| :--- | :---: | :---: | :---: | :---: |
| `biodegradable` | 98.44% | 94.03% | **96.18%** | 67 |
| `cardboard` | 89.83% | 86.89% | **88.33%** | 61 |
| `e_waste` | 92.54% | 92.54% | **92.54%** | 67 |
| `glass` | 83.75% | 89.33% | **86.45%** | 75 |
| `metal` | 92.00% | 75.41% | **82.88%** | 61 |
| `paper` | 84.78% | 87.64% | **86.19%** | 89 |
| `plastic` | 87.01% | 91.78% | **89.33%** | 73 |
| `trash` | 71.43% | 90.00% | **79.65%** | 20 |

> **Note on Trash Category**:  
> The `trash` class represents mixed non-recyclables and has the smallest sample representation (137 images, 20 test samples). While recall is strong at 90.00%, precision is comparatively lower due to visual heterogeneity.

---

## Application Pages

| Page | Route | Purpose & Key Features |
| :--- | :--- | :--- |
| **Dashboard** | `/` | Overall system observability, 4 KPI cards, 8-class distribution chart, real-time backend indicators, recent classifications table. |
| **Prediction** | `/predict` | Interactive waste classification interface: drag-and-drop upload, 8-class probability bars, confidence score, disposal recommendation, Grad-CAM toggle. |
| **History** | `/history` | Complete SQLite audit log of past predictions with category IDs (`TB`, `TC`, `TE`, etc.), image thumbnails, probability modal, search/filter, and record deletion. |
| **Dataset** | `/dataset` | In-depth dataset analytics: 3,427 benchmark images across 8 classes, 70/15/15 split details, and interactive image gallery. |
| **Performance** | `/performance` | Model evaluation dashboard: 89.08% accuracy, 87.81% Macro F1, 89.20% Weighted F1, interactive 8×8 confusion matrix, and CPU inference metrics. |
| **Training** | `/training` | Training & architecture overview: MobileNetV2 architecture, two-stage fine-tuning curves, and comparison against baseline CNN. |
| **About** | `/about` | Project background, methodology, technology stack, explainability concepts, and academic citations. |
| **Settings** | `/settings` | Backend connection health monitor and latency ping test. |

---

## API Documentation

FastAPI provides type-safe, auto-generated OpenAPI documentation accessible at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### API Endpoints Summary

| Method | Endpoint | Description | Payload / Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Backend status & loaded model information | None |
| `GET` | `/api/v1/model/info` | Architecture, parameters, and input resolution | None |
| `GET` | `/api/v1/model/metrics` | Empirical test metrics and confusion matrix | None |
| `GET` | `/api/v1/dataset/info` | 8-class dataset split and count metadata | None |
| `GET` | `/api/v1/dataset/classes` | Array of 8 supported waste class names | None |
| `POST` | `/api/v1/predict` | Classify image and return 8-class probabilities | Multipart file (`.jpg`, `.png`) |
| `POST` | `/api/v1/predict/gradcam` | Classify image and return Base64 Grad-CAM overlay | Multipart file (`.jpg`, `.png`) |
| `GET` | `/api/v1/predictions` | Paginated prediction history from SQLite | `limit`, `offset`, `class_name` |
| `GET` | `/api/v1/predictions/{id}` | Single prediction record details | `id` (e.g. `TB5`, `TC22`) |
| `GET` | `/api/v1/predictions/{id}/image`| Retrieve stored prediction image file | `id` |
| `DELETE`| `/api/v1/predictions/{id}` | Delete prediction record and image from disk | `id` |

---

## Project Structure

```
Waste_Classification_DL_System/
├── README.md                          # Comprehensive project documentation
├── pyproject.toml                     # Python package configuration
├── .gitignore                         # Git exclusion rules
├── artifacts/
│   ├── backup/
│   │   └── v1.0.0-baseline/           # Frozen 6-class baseline model & metadata
│   ├── experiments/
│   │   └── 8class_mobilenetv2/        # 8-class training checkpoints & evaluation reports
│   └── final/
│       ├── class_names.json           # 8 production class definitions
│       ├── metrics.json               # Production evaluation metrics
│       ├── model_metadata.json        # Production model metadata
│       └── waste_classifier.keras     # Promoted 8-class production model (2.42M params)
├── backend/
│   ├── app/
│   │   ├── config.py                  # Environment and application settings
│   │   ├── database.py                # SQLite database management and queries
│   │   ├── gradcam.py                 # Grad-CAM explainability implementation
│   │   ├── main.py                    # FastAPI application initialization & CORS
│   │   ├── model_loader.py            # Deep learning model manager singleton
│   │   ├── schemas.py                 # Pydantic request & response models
│   │   └── routes/
│   │       ├── dataset.py             # Dataset information routes
│   │       ├── health.py              # Health check endpoint
│   │       ├── history.py             # SQLite prediction history endpoints
│   │       ├── model.py               # Model metadata & metrics endpoints
│   │       └── prediction.py          # Prediction and Grad-CAM upload endpoints
│   ├── requirements.txt               # Backend Python dependencies
│   └── tests/
│       └── test_api.py                # Automated Pytest suite (17 tests)
├── data/
│   ├── final/
│   │   └── 8class/                    # Unified 8-class dataset (train, val, test)
│   ├── processed/                     # Original 6-class TrashNet partitions
│   └── raw/                           # Raw source datasets
├── docs/
│   ├── SECURITY_AUDIT_REPORT.md       # Phase 15 comprehensive security audit
│   └── UI_BROWSER_TEST_REPORT.md      # Phase 16 browser functional test report
├── frontend/
│   ├── package.json                   # Frontend dependencies & scripts
│   ├── tsconfig.json                  # TypeScript compiler configuration
│   ├── vite.config.ts                 # Vite bundler configuration
│   └── src/
│       ├── App.tsx                    # Main React application component & routes
│       ├── main.tsx                   # Application bootstrap
│       ├── components/                # Reusable UI components
│       ├── pages/                     # 8 main application pages
│       ├── services/                  # API client & backend integration
│       └── types/                     # TypeScript type definitions
└── scripts/
    ├── build_8class_dataset.py        # 8-class dataset construction script
    ├── e2e_full_system_test.py        # End-to-end 7-sector system audit script
    ├── train_8class_mobilenetv2.py    # 8-class MobileNetV2 training pipeline
    └── validate_8class_dataset.py     # Dataset integrity & split validation
```

---

## Testing & Verification

The project includes an automated regression and audit suite:

### 1. Backend Pytest Suite
```bash
python -m pytest backend/tests/test_api.py -v
```
- **Coverage**: 17 unit and integration tests verifying health, model metadata, dataset endpoints, valid JPG/PNG inference, Grad-CAM generation, extension filtering, corrupted payloads, 10 MB payload limits, SQLite CRUD, and independent category counters.
- **Status**: **17 / 17 PASSED (100%)**.

### 2. End-to-End System Audit
```bash
python scripts/e2e_full_system_test.py
```
- **Coverage**: 7 audit sectors (Dataset Integrity, Model Artifacts, Core Endpoints, 8-Class Inference, Grad-CAM, SQLite History, Security Boundaries).
- **Status**: **7 / 7 SECTORS PASSED (100%)**.

### 3. Frontend Production Build
```bash
cd frontend
npm run build
```
- **Status**: **0 TypeScript Errors, 0 Vite Build Errors**.

### 4. Full UI / Browser Functional Test
- **Status**: **UI BROWSER TEST PASSED**.
- All 8 pages, prediction uploads across all 8 classes, Grad-CAM overlays, SQLite persistence, and responsive layouts verified with 0 console errors and 0 runtime exceptions.

---

## Security

A dedicated security audit was conducted during **Phase 15** ([docs/SECURITY_AUDIT_REPORT.md](docs/SECURITY_AUDIT_REPORT.md)):

- **Final Security Determination**: **`SECURITY AUDIT PASSED WITH LOW-RISK FINDINGS`**
- **Findings Summary**:
  - `SEC-001` (Low / Informational): CORS configured for local development (`localhost:5173`, `127.0.0.1:5173`, `localhost:3000`).
  - `SEC-002` (Informational): Swagger UI / ReDoc interactive documentation active for local development and testing.
  - **Critical Vulnerabilities**: **0**
  - **High Vulnerabilities**: **0**
  - **Medium Vulnerabilities**: **0**
- *Dependency security review was performed from the project manifests; no dedicated external CVE database scan was performed.*

---

## Browser Validation

Full browser-based functional validation was conducted during **Phase 16** ([docs/UI_BROWSER_TEST_REPORT.md](docs/UI_BROWSER_TEST_REPORT.md)):

- **Result**: **`UI BROWSER TEST PASSED`**
- **Verified Components**:
  - Dashboard, Prediction, Prediction History, Dataset, Performance, Training, About, and Settings pages.
  - Real image inference across all 8 classes.
  - Grad-CAM heatmap visualization.
  - SQLite record creation, modal viewing, and live deletion.
  - Responsive layouts: Desktop (1280×800), Tablet (768×1024), Mobile (375×667 / 390×844).
  - Browser Console Errors: **0**
  - Backend Runtime Errors: **0**
  - Failed Network Requests: **0**

---

## Development History

### Project Evolution

- **`v1.0.0-baseline` (Frozen Baseline)**:
  - Original 6-class system (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash`).
  - Custom CNN baseline (68.60% accuracy) vs. MobileNetV2 6-class (87.07% accuracy).
  - TrashNet benchmark dataset (2,527 images).
  - Frozen and archived in Git tag `v1.0.0-baseline` (Commit `9a3dff3`).

- **`v2.0.0-8class` (Current Production Release)**:
  - Extended classification taxonomy to **8 classes** by introducing `biodegradable` and `e_waste`.
  - Constructed unified `8class-v1.0` benchmark dataset (3,427 images across 8 classes).
  - Implemented 2-stage transfer learning MobileNetV2 architecture (89.08% Test Accuracy, 87.81% Macro F1).
  - Promoted 8-class model to production serving.
  - Updated category-based prediction ID counters (`TB`, `TC`, `TE`, `TG`, `TM`, `TP`, `TPL`, `TT`).
  - Completed Phase 15 Security Audit and Phase 16 Full UI / Browser Functional Testing.

---

## Planned Next Feature

### Smart Recycling Center Finder
> **STATUS: PLANNED / NOT YET IMPLEMENTED**

The next development phase will introduce an intelligent local disposal & recycling center finder:
- **Automatic Waste-Type Mapping**: Automatically passes the classified waste category (e.g., `e_waste`, `biodegradable`, `plastic`) to the center finder.
- **Geolocation & Manual Search**: Detect user's current GPS location or allow manual city/postal code input.
- **Distance-Sorted Results**: Query and display nearest verified recycling facilities, municipal compost sites, and e-waste drop-off centers.
- **Interactive Map & Directions**: Integrated map visualization with turn-by-turn navigation links.

---

## Current Project Status

| Component | Status | Verification |
| :--- | :---: | :--- |
| **Core ML System** | **COMPLETE** | MobileNetV2 8-Class Transfer Learning |
| **8-Class Production Model** | **COMPLETE** | 89.08% Test Accuracy, 87.81% Macro F1 |
| **Full-Stack Web Application** | **COMPLETE** | React 18 + TypeScript + FastAPI |
| **Prediction History & Storage** | **COMPLETE** | SQLite + Local Image Storage |
| **Grad-CAM Explainability** | **COMPLETE** | Layer `mobilenetv2_1.00_224::out_relu` |
| **Security Audit** | **COMPLETE** | Phase 15 Passed with Low-Risk Findings |
| **Browser UI Validation** | **COMPLETE** | Phase 16 Passed (0 UI / Console Errors) |
| **Smart Recycling Center Finder** | **PLANNED** | Next Development Phase |

---

## License

This project is developed for academic, educational, and environmental research evaluation purposes under the **MIT License**.
