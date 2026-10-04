# EcoClassify DL — AI-Powered Waste Classification System

> **Application / Product Branding**: EcoClassify DL  
> **Production Version**: `v2.0.0-8class` | **Release Dataset**: `8class-v1.0` (3,427 images across 8 classes)  
> **Core Deep Learning Architecture**: MobileNetV2 Transfer Learning (2,422,984 parameters)  
> **Production Validation Metrics**: **Test Accuracy: 89.08%** | **Macro F1: 87.81%** | **Weighted F1: 89.20%**  
> **Explainable AI**: Grad-CAM Visual Heatmaps (`mobilenetv2_1.00_224::out_relu`)  
> **Full-Stack Technology**: React + Vite + TypeScript + Tailwind CSS | FastAPI + SQLite + TensorFlow 2.16+
> **Repository**: [https://github.com/Tamannshaikh/EcoClassify-DL-AI-Powered-Waste-Classification-System](https://github.com/Tamannshaikh/EcoClassify-DL-AI-Powered-Waste-Classification-System)

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
> - **No external cloud API keys required for core classification** (local-first standalone operation).

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

## Core Features

1. **AI Waste Classification**: Upload or drag-and-drop any municipal waste photo to receive an instant real-time prediction from the production MobileNetV2 classifier with sub-100 ms latency.
2. **8-Class Waste Recognition**: Recognizes 8 distinct solid and recyclable waste categories: `biodegradable`, `cardboard`, `e_waste`, `glass`, `metal`, `paper`, `plastic`, and `trash`.
3. **Explainable AI with Grad-CAM**: Visual proof of model reasoning via Gradient-weighted Class Activation Mapping targeting the final feature layer (`mobilenetv2_1.00_224::out_relu`).
4. **Prediction History & Image Persistence**: Full local audit logging in SQLite (`data/waste_classification.db`) and disk storage (`data/uploads/`) with custom category ID prefixes (`TB`, `TC`, `TE`, `TG`, `TM`, `TP`, `TPL`, `TT`).
5. **Interactive Analytics Dashboard**: System observability showing health status, dataset volume, model accuracy, 8-class distribution chart, and recent prediction tables.
6. **Dataset & Model Performance Analytics**: Dedicated analytics pages featuring 3,427-image partition breakdowns, 8×8 normalized confusion matrix, per-class metrics, and CPU latency benchmarks.
7. **Full-Stack Web Application**: Local-first responsive web application built with React 18, TypeScript, Vite, Tailwind CSS, Lucide icons, and FastAPI.
8. **Security, Validation & Robustness**: Comprehensive multi-layer input validation, 10 MB payload limits, magic-byte MIME and Pillow verification, parameterized SQLite queries, and path traversal protection.
9. **Smart Recycling Center Finder**: Context-aware nearby recycling center search integrated directly into the classification workflow with geospatial distance sorting and dual-provider support.

---

## Smart Recycling Center Finder

Users can search for nearby recycling facilities based on the selected waste category and geographic location.

### Features
- **AI-Predicted Waste Type Automatically Selected**: Automatically preselects the classified waste category upon opening the finder from the prediction result.
- **Manual Selection from All 8 Waste Categories**: Dropdown selector allowing instant search for any of the 8 supported waste classes.
- **Browser-Based Current Location**: One-click geolocation request via `navigator.geolocation` triggered solely upon user action.
- **Configurable Search Radius**: Select search ranges of 1, 2, 5, 10, 20, or 50 km.
- **Nearest-First Sorting**: Facilities sorted ascending by approximate geographic distance.
- **Haversine Geographic Distance**: Server-side calculation of exact distance in kilometers (`"Approx. X.XX km away"`).
- **Google Places Provider**: Integration with Google Places API for real-world facility search when an API key is configured.
- **Curated Regional Fallback Provider**: Built-in curated regional hubs database ensuring 100% functionality without external API keys.
- **Google Maps Links**: Direct links to view facility coordinates on Google Maps.
- **Directions Links**: Direct deep-links for turn-by-turn driving/transit directions.
- **Responsive Modal Interface**: Clean, accessible modal dialog with smooth transitions and keyboard (Escape) close support.
- **Empty-Result Handling**: Helpful empty states with one-click radius expansion to 50 km.
- **API Error Handling**: Stable, single-render error alerts without automatic infinite retry loops.
- **No Persistent Location Tracking**: Ephemeral client-side state; user coordinates are never stored in the database.

### Important Location Limitation
> **Notice**: Free-text location names such as 'Vashi, Navi Mumbai' are not currently geocoded automatically. Arbitrary text geocoding would require an external geocoding provider and is outside the current project scope.
>
> Supported location workflows:
> - **Browser current location** (via `navigator.geolocation`)
> - **Regional hub presets** (Navi Mumbai, Mumbai, Thane, Bandra, Turbhe, Pune, Delhi NCR, Bengaluru)
> - **Custom latitude/longitude coordinates**

### Recycling Architecture
```
Frontend (RecyclingCenterModal.tsx)
        ↓ POST /api/v1/recycling/search
FastAPI Route (routes/recycling.py)
        ↓
Recycling Center Service (services/recycling/service.py)
        ├── Primary: Google Places Provider (services/recycling/providers/google_places.py)
        └── Fallback: Curated Regional Provider (services/recycling/providers/curated.py)
        ↓
Server-Side Haversine Distance Calculation & Ascending Distance Sorting
```

- **Backend Endpoint**: `POST /api/v1/recycling/search`
- **Server-Side Distance Calculation**: Uses the Haversine spherical formula for precise proximity ranking.
- **Provider Fallback**: If the Google Places API is disabled or unconfigured, the service transparently serves curated regional centers.
- **Zero Location Persistence**: Coordinates are processed in-memory and never written to database tables or logs.
- **Secure Secret Handling**: API keys remain strictly server-side in `.env` and are never exposed to the client.

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

### Dataset Sources
1. **TrashNet** (Stanford CS229 / Gary Thung & Mindy Yang): Contributes baseline 6 classes (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash`).
2. **E-Waste Image Dataset**: Contributes high-quality electronic waste items (`e_waste`).
3. **BDWaste**: Contributes verified compostable and organic waste items (`biodegradable`).
4. **CTSoc E-Waste (Audited & Excluded)**: Evaluated during Phase 10 audit but excluded due to synthetic studio domain mismatch.

---

## Machine Learning Model

- **Model Architecture**: MobileNetV2 Transfer Learning
- **Input Resolution**: `224 × 224 × 3` RGB
- **Pretrained Backbone**: MobileNetV2 (ImageNet)
- **Classification Head**:
  - `GlobalAveragePooling2D()`
  - `Dense(128, activation='relu')`
  - `Dropout(0.30)`
  - `Dense(8, activation='softmax')`
- **Total Parameters**: 2,422,984 parameters (9.24 MB file size)
- **Production Artifact**: `artifacts/final/waste_classifier.keras`
- **Model SHA-256 Checksum**: `5d27f8c18886b56110d04d75885941482f17b33be60dd0a429a158f30c4717fa`
- **Explainability**: Supported via Grad-CAM targeting layer `mobilenetv2_1.00_224::out_relu`

### Production Evaluation Results (513 Hold-Out Test Images)

| Metric | Production 8-Class MobileNetV2 | Baseline CNN (6-Class) | Delta / Note |
| :--- | :---: | :---: | :--- |
| **Test Accuracy** | **89.08%** | 68.60% | **+20.48% pts** |
| **Macro Precision** | **87.44%** | 68.00% | **+19.44% pts** |
| **Macro Recall** | **88.51%** | 69.23% | **+19.28% pts** |
| **Macro F1-Score** | **87.81%** | 65.61% | **+22.20% pts** |
| **Weighted F1-Score** | **89.20%** | 68.94% | **+20.26% pts** |
| **Average CPU Latency** | **~88.65 ms** | ~42.10 ms | Sub-100 ms real-time CPU serving |
| **P95 CPU Latency** | **~98.29 ms** | ~55.00 ms | Deterministic CPU execution |

### Per-Class Test Metrics (8 Classes)

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

---

## Application Pages

| Page | Route | Purpose & Key Features |
| :--- | :--- | :--- |
| **Dashboard** | `/` | Overall system observability, 4 KPI cards, 8-class distribution chart, real-time backend indicators, recent classifications table. |
| **Prediction** | `/predict` | Interactive waste classification interface: drag-and-drop upload, 8-class probability bars, confidence score, disposal recommendation, Grad-CAM toggle, and integrated Smart Recycling Center Finder. |
| **History** | `/history` | Complete SQLite audit log of past predictions with category IDs (`TB`, `TC`, `TE`, etc.), image thumbnails, probability modal, search/filter, and record deletion. |
| **Dataset** | `/dataset` | In-depth dataset analytics: 3,427 benchmark images across 8 classes, 70/15/15 split details, and interactive image gallery. |
| **Performance** | `/performance` | Model evaluation dashboard: 89.08% accuracy, 87.81% Macro F1, 89.20% Weighted F1, interactive 8×8 confusion matrix, and CPU inference metrics. |
| **Training** | `/training` | Training & architecture overview: MobileNetV2 architecture, two-stage fine-tuning curves, and comparison against baseline CNN. |
| **About** | `/about` | Project background, methodology, technology stack, explainability concepts, and academic citations. |
| **Settings** | `/settings` | Backend connection health monitor and latency ping test. |

---

## API Endpoints

FastAPI provides type-safe, auto-generated OpenAPI documentation accessible at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **Frontend App**: `http://localhost:5173`

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
| `POST` | `/api/v1/recycling/search` | Search nearby recycling centers by waste type and location | JSON body (`waste_type`, `latitude`, `longitude`, `radius_km`, `limit`) |

---

## Technology Stack

- **Frontend**:
  - React 19 / React Router
  - TypeScript
  - Vite
  - Tailwind CSS
  - Axios
  - Recharts
  - Lucide React Icons
- **Backend**:
  - Python 3.10+
  - FastAPI
  - Pydantic v2
  - SQLite (with standard parameterization)
  - Uvicorn
- **Machine Learning & Data Science**:
  - TensorFlow 2.16+ / Keras
  - MobileNetV2 (ImageNet Transfer Learning)
  - Scikit-learn
  - NumPy
  - Pandas
  - Pillow (PIL)
  - Grad-CAM Explainability Engine
- **Infrastructure & Development Tools**:
  - Git & GitHub
  - Pytest
  - Local-first architecture

---

## Security

A comprehensive security review was performed on the full-stack architecture:

- **No Hardcoded Secrets**: All configuration values and API keys are loaded via environment variables; `.env` is strictly excluded in `.gitignore`.
- **Upload Validation**: File uploads are capped at 10 MB with strict MIME-type and extension validation (`.jpg`, `.jpeg`, `.png`).
- **Pillow Integrity Verification**: Uploaded images undergo in-memory byte validation (`img.verify()`) to prevent image parser exploit attacks.
- **SQL Parameterization**: 100% of SQLite database queries use parameter placeholders (`?`), preventing SQL injection.
- **Path Traversal Protection**: Controlled image file saving and containment checks (`Path.resolve().relative_to(UPLOAD_DIR)`) prevent arbitrary file overwrite or retrieval.
- **Standardized Error Handling**: Detailed internal exceptions are mapped to standard sanitized error payloads without leaking server stack traces.
- **Local CORS Scoping**: Cross-Origin Resource Sharing is scoped specifically to local frontend development origins (`http://localhost:5173`, `http://127.0.0.1:5173`).
- **Server-Side API Key Isolation**: External provider keys (e.g., Google Maps API key) remain strictly within the backend service and are never transmitted to the browser client.
- *Dependency security review was performed from the project manifests; no dedicated external CVE database scanner was performed.*

---

## Testing & Verification

The project includes an automated test suite across backend, recycling service, and end-to-end workflows:

- **Backend Core Tests**: **17 / 17 PASSED** (`pytest backend/tests/test_api.py`)
- **Recycling Service Tests**: **24 / 24 PASSED** (`pytest backend/tests/test_recycling.py`)
- **Full Pytest Suite**: **42 / 42 PASSED** (`pytest backend/tests/`)
- **End-to-End System Audit**: **7 / 7 SECTORS PASSED** (`python scripts/e2e_full_system_test.py`)
- **Frontend Production Build**: **PASS** (`tsc -b && vite build` — 0 errors)
- **Browser Functional Testing**: **PASS** (0 console errors, 0 runtime exceptions)
- **Security Verification**: **PASS** (Input sanitization, CORS restrictions, SQL parameterization verified)
- **Model Checksum Verified**: SHA-256 `5d27f8c18886b56110d04d75885941482f17b33be60dd0a429a158f30c4717fa`
- **Dataset Volume**: 3,427 images across 8 classes (unchanged and preserved)

---

## Project Status

- **Production Release**: `v2.0.0-8class`
- **Status**: **Feature-complete and validated**

### Implemented Capabilities
- 8-Class waste classification taxonomy
- MobileNetV2 transfer learning with 89.08% test accuracy
- Grad-CAM visual heatmap explainability
- Prediction history logging with SQLite & thumbnail persistence
- Interactive analytics dashboard and KPI metrics
- Dataset and model performance analytics pages
- Smart Recycling Center Finder with geospatial proximity sorting
- Dual-provider recycling architecture (Google Places + Curated Regional fallback)
- Responsive frontend interface
- Multi-layer security validation
- 100% passing automated test suite (42/42 tests)
- Full browser validation with 0 console errors

### Known Limitation
- Free-text location geocoding is not currently implemented.

---

## Future Roadmap

Possible future enhancements for subsequent releases include:
- External geocoding provider integration for arbitrary free-text location queries
- Additional regional and international recycling provider integrations
- Exploration of additional waste sub-categories
- Model quantization (INT8/TFLite) for further reduced CPU latency
- Cloud containerization and production hosting configurations

---

## License

This project is developed for academic, educational, and environmental research evaluation purposes under the **MIT License**.
