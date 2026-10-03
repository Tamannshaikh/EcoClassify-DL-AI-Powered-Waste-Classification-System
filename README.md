# AI-Powered Waste Classification System

> **Application / Product Branding**: EcoClassify DL  
> **Core Model**: MobileNetV2 Transfer Learning (2,422,726 parameters) | **Test Accuracy**: 87.07% | **Macro F1**: 85.14%  
> **Dataset**: TrashNet (2,527 images across 6 classes) | **Explainability**: Grad-CAM Visual Heatmaps  
> **Tech Stack**: React 19 + Vite + TypeScript + Tailwind CSS | FastAPI + SQLite + TensorFlow 2.16+

---

## Prerequisites

Before running the project, make sure you have installed:

1. **Python 3.10, 3.11, or 3.12** (Verify with `python --version`)
2. **Node.js 18+ and npm** (Verify with `node -v` and `npm -v`)
3. **Git** (Optional, if cloning from GitHub)

### Recommended Environment
- **Operating System**: Windows 10/11, macOS, or Linux
- **System Memory**: 8 GB+ RAM recommended (4 GB minimum)
- **Disk Space**: ~2 GB free space (for dataset, dependencies, and model weights)
- **Internet Connection**: Required only for first-time dependency downloads (`pip` and `npm`)

> **Key Information**:  
> - **No GPU is required** for inference (CPU execution is ~61.15 ms).  
> - **No username / password is required** to run or use the application.  
> - **No external cloud API key is required** (100% offline & local).

---

## First-Time Setup

Perform these steps **once** when setting up the project for the first time:

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
pip install -r backend\requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Quick Start (Every Subsequent Run)

Once the first-time setup is complete, start the project anytime using **2 terminals**:

```
+---------------------------------------------------------------------------------------------------+
| Terminal 1 — Backend API Service                                                                 |
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
| -> Application: http://localhost:5173                                                             |
+---------------------------------------------------------------------------------------------------+
```

---

## Quick Troubleshooting

### Backend does not start
1. Make sure the virtual environment is activated:
   ```powershell
   .\.venv\Scripts\activate
   ```
2. Verify Python version (`python --version` -> Python 3.10+).
3. Reinstall dependencies if required:
   ```bash
   pip install -r backend\requirements.txt
   ```

### Frontend does not start
From the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```

### Frontend says the backend is unavailable
Make sure **Terminal 1** is actively running the FastAPI server:
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Then verify backend health in your browser: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health).

### Port 8000 is already in use
Stop the existing process using port 8000, or launch on another port:
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload
```

### Port 5173 is already in use
Vite will automatically detect an in-use port and choose the next available one (e.g., `5174`). Open the exact local URL displayed in **Terminal 2**.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Why We Created This Project](#2-why-we-created-this-project)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Key Features](#5-key-features)
6. [How the System Works](#6-how-the-system-works)
7. [System Architecture](#7-system-architecture)
8. [Complete Tech Stack](#8-complete-tech-stack)
9. [Dataset](#9-dataset)
10. [Waste Classes](#10-waste-classes)
11. [Machine Learning Approach](#11-machine-learning-approach)
12. [Why MobileNetV2?](#12-why-mobilenetv2)
13. [Model Performance & Comparison](#13-model-performance--comparison)
14. [Project Folder Structure](#14-project-folder-structure)
15. [Prerequisites](#15-prerequisites)
16. [Installation](#16-installation)
17. [Environment Setup](#17-environment-setup)
18. [Running the Project](#18-running-the-project)
19. [How to Use the Application](#19-how-to-use-the-application)
20. [Dashboard](#20-dashboard)
21. [Waste Prediction Flow](#21-waste-prediction-flow)
22. [Grad-CAM Explainability](#22-grad-cam-explainability)
23. [Prediction History](#23-prediction-history)
24. [Dataset Information Page](#24-dataset-information-page)
25. [Model Performance Page](#25-model-performance-page)
26. [Training Information Page](#26-training-information-page)
27. [API Documentation](#27-api-documentation)
28. [API Endpoints](#28-api-endpoints)
29. [Testing & Verification](#29-testing--verification)
30. [Security & Safety](#30-security--safety)
31. [Authentication](#31-authentication)
32. [Troubleshooting](#32-troubleshooting)
33. [Important Commands Reference](#33-important-commands-reference)
34. [Dataset Limitations](#34-dataset-limitations)
35. [Future Scope](#35-future-scope)
36. [Results Summary](#36-results-summary)
37. [Academic Information](#37-academic-information)
38. [Credits & Citation](#38-credits--citation)
39. [License](#39-license)

---

## 1. Project Overview

The **AI-Powered Waste Classification System** (branded as **EcoClassify DL**) is a deep learning web application engineered to classify municipal and household solid waste images into six recyclable and non-recyclable categories: `cardboard`, `glass`, `metal`, `paper`, `plastic`, and `trash`. 

The system couples a transfer-learned **MobileNetV2** convolutional neural network with **Grad-CAM (Gradient-weighted Class Activation Mapping)** visual explainability, a **FastAPI** backend service, a local **SQLite** history store, and a modern **React 19 + TypeScript + Tailwind CSS** user interface.

---

## 2. Why We Created This Project

Municipal solid waste sorting remains one of the largest operational bottlenecks in environmental recycling programs worldwide:
- **Manual Sorting Hazards**: Human operators face repetitive strain, chemical exposures, sharp objects, and unsanitary conditions.
- **High Contamination Rates**: Cross-contamination in recycling bins ruins recyclable batches, sending reusable materials directly to landfills.
- **Need for Explainability**: Black-box AI models reduce user and operator trust. Providing visual heatmaps demonstrating *why* an item was classified as glass or plastic creates transparency and educational feedback.

---

## 3. Problem Statement

Manual visual identification of municipal waste is error-prone, labor-intensive, and unscalable. Machine learning solutions must be lightweight enough to operate on resource-constrained commodity hardware while maintaining high classification precision across visually heterogeneous waste materials.

---

## 4. Objectives

1. **Develop an Accurate Classifier**: Train a deep convolutional neural network achieving >85% test accuracy on the benchmark TrashNet dataset.
2. **Optimize for Edge & CPU Latency**: Ensure the model executes in under 100 ms on standard CPU hardware without requiring dedicated GPUs.
3. **Provide Model Interpretability**: Implement layer-level Grad-CAM saliency mapping over final convolutional feature maps (`out_relu`).
4. **Deliver a Full-Stack Local Web Platform**: Build an interactive, responsive, local-first dashboard with real-time inference, multi-class probability visualizer, persistent history, and performance analytics.
5. **Guarantee Reproducibility & Zero Leakage**: Establish a group-aware split preventing identical content from crossing training and testing splits.

---

## 5. Key Features

- **Real-Time 6-Class Inference**: Sub-70 ms average inference with full multi-class probability distributions.
- **Grad-CAM Visual Heatmaps**: Color-coded saliency maps highlighting exact visual features (rims, labels, textures) that informed the classification.
- **Persistent Prediction History**: Full SQLite CRUD logging of all predictions, confidence ratings, timestamps, and model versions.
- **Interactive Analytics Dashboard**: Live metrics, class distribution charts, confusion matrices, and empirical CNN vs. MobileNetV2 comparisons.
- **Local-First & Privacy-Preserving**: Complete offline execution on localhost; zero external cloud dependencies or third-party telemetry.
- **Rigorous Input Validation**: 10 MB payload limits, MIME/extension whitelisting, and in-memory Pillow image structure verification.

---

## 6. How the System Works

```
User (Web Browser)
  ↓
React 19 + TypeScript Frontend
  ↓ (Uploads image via HTTP POST multipart/form-data)
FastAPI REST Backend
  ↓
File Validation & Security Check (Extension, MIME, Pillow verify, 10MB limit)
  ↓
Image Preprocessing (Resize to 224x224 RGB, Mobilenet normalization)
  ↓
MobileNetV2 Model (Loaded once at backend startup — NOT retrained on requests)
  ↓
6-Class Softmax Probability Distribution & Top Prediction
  ↓
SQLite Database (Logs timestamp, prediction_id, filename, confidence, probabilities)
  ↓
Optional Grad-CAM Engine (Backpropagates gradients to 'out_relu' layer)
  ↓
Base64-Encoded Heatmap Overlay Payload
  ↓
Interactive Visualization Rendered in React UI
```

> **IMPORTANT ARCHITECTURAL FACT**:  
> The deep learning model is **NOT** retrained every time a user uploads an image or requests a classification. The pre-trained and fine-tuned `waste_classifier.keras` artifact is loaded **once into memory at backend startup** (via a singleton `ModelManager`) and serves instantaneous forward-pass inferences for all subsequent requests.

---

## 7. System Architecture

```
+--------------------------------------------------------------------------+
|                             PRESENTATION LAYER                           |
|                       React 19 + TypeScript + Vite                       |
|   +---------------+  +----------------+  +--------------+  +---------+   |
|   | DashboardPage |  | PredictionPage |  | HistoryPage  |  | Dataset |   |
|   +---------------+  +----------------+  +--------------+  +---------+   |
|   +---------------+  +----------------+  +--------------+  +---------+   |
|   |  Performance  |  |  TrainingPage  |  |  AboutPage   |  | Settings|   |
|   +---------------+  +----------------+  +--------------+  +---------+   |
+--------------------------------------------------------------------------+
                                     |  HTTP REST (Axios / Fetch)
                                     v
+--------------------------------------------------------------------------+
|                              API BACKEND LAYER                           |
|                          FastAPI (Uvicorn Async)                         |
|   +-------------------+  +-------------------+  +--------------------+   |
|   | /api/v1/predict   |  | /predict/gradcam  |  | /api/v1/history    |   |
|   +-------------------+  +-------------------+  +--------------------+   |
|   +-------------------+  +-------------------+  +--------------------+   |
|   | /api/v1/model     |  | /api/v1/dataset   |  | /api/v1/health     |   |
|   +-------------------+  +-------------------+  +--------------------+   |
+--------------------------------------------------------------------------+
         |                                           |
         v                                           v
+-----------------------+                 +--------------------------------+
|     STORAGE LAYER     |                 |       DEEP LEARNING CORE       |
|    SQLite Database    |                 |   TensorFlow 2.16+ / Keras 3   |
|  data/waste_classi... |                 |  artifacts/final/waste_classi..|
|  - Predictions Log    |                 |  - MobileNetV2 (2.42M params)  |
|  - Probabilities JSON |                 |  - Grad-CAM Explainer Engine   |
+-----------------------+                 +--------------------------------+
```

---

## 8. Complete Tech Stack

### Frontend
- **Framework**: React 19 (`react`, `react-dom`)
- **Language**: TypeScript (`tsc`)
- **Bundler & Dev Server**: Vite 8
- **Styling**: Tailwind CSS v4 (`@tailwindcss/postcss`, `postcss`, `autoprefixer`)
- **Routing**: React Router v7 (`react-router-dom`)
- **HTTP Client**: Axios
- **Data Visualization**: Recharts (Confusion matrices, probability bar charts, class distribution)
- **Icons**: Lucide React

### Backend & API
- **Framework**: FastAPI (Async ASGI)
- **ASGI Server**: Uvicorn with standard workers
- **Data Validation & Schemas**: Pydantic v2
- **File Upload Handling**: `python-multipart`
- **Database**: SQLite 3 (Standard Python library with connection pooling and row factories)

### Machine Learning & Preprocessing
- **Deep Learning Framework**: TensorFlow 2.16+ / Keras 3.x
- **Computer Vision**: Pillow (PIL), Matplotlib, OpenCV-compatible color processing
- **Numerical Processing**: NumPy, Pandas
- **Evaluation & Metrics**: Scikit-Learn (Classification report, confusion matrix, macro/weighted F1)
- **Explainability**: Grad-CAM (Target layer: `out_relu`)

### Testing & Tooling
- **Backend Unit Testing**: Pytest 9.x, AnyIO, AsyncIO
- **Integration Testing**: Custom End-to-End System Audit script (`scripts/e2e_full_system_test.py`)
- **Version Control**: Git

---

## 9. Dataset

The system is trained and benchmarked on the academic **TrashNet** dataset:
- **Total Images**: 2,527 images
- **Color Space**: 3-Channel RGB
- **Original Dimensions**: 512 × 384 pixels
- **Format**: JPEG
- **Data Split Ratio**: 70% Train / 15% Validation / 15% Test
  - **Train Partition**: 1,769 images
  - **Validation Partition**: 379 images
  - **Test Partition**: 379 images
- **Leakage Prevention**: Group-aware stratified splitting based on SHA-256 duplicate content audits to guarantee identical content never crosses splits.

---

## 10. Waste Classes

The project strictly operates across **exactly 6 waste categories**:

| # | Class Name | Dataset Count | Train Count | Val Count | Test Count | Description |
| :-: | :--- | :-: | :-: | :-: | :-: | :--- |
| 1 | `cardboard` | 403 | 282 | 60 | 61 | Corrugated boxes, packaging cartons, paperboard |
| 2 | `glass` | 501 | 351 | 75 | 75 | Transparent, amber, and green glass beverage bottles and jars |
| 3 | `metal` | 410 | 287 | 62 | 61 | Aluminum beverage cans, tin food cans, aerosol containers |
| 4 | `paper` | 594 | 416 | 89 | 89 | Office paper, newspaper, magazines, envelopes, books |
| 5 | `plastic` | 482 | 337 | 72 | 73 | PET/HDPE bottles, food containers, disposable cups |
| 6 | `trash` | 137 | 96 | 21 | 20 | Non-recyclable composite waste, wrappers, damaged items |

> **NOTE ON DATASET INTEGRITY**:  
> There is **NO "organic" class** in this project. The active model, dataset, and backend routes support exclusively the 6 standard TrashNet classes.

---

## 11. Machine Learning Approach

The ML pipeline incorporates a rigorous two-stage transfer learning protocol:
1. **Data Preprocessing**: Images are resized to `224 × 224 × 3`, scaled to `[-1.0, 1.0]` using MobileNetV2 normalization formulas.
2. **Data Augmentation**: Random horizontal flipping, rotation (`±15°`), zoom (`±10%`), and contrast adjustments during training.
3. **Class Balancing**: Balanced heuristic class weights computed via `N / (num_classes * count_c)` to handle the minority `trash` category (137 samples).
4. **Stage 1 (Feature Extraction)**: Base MobileNetV2 frozen with ImageNet weights; train only the custom classification head (`GlobalAveragePooling2D` -> `Dense(256, ReLU)` -> `Dropout(0.4)` -> `Dense(6, Softmax)`) with Adam (`lr=1e-3`).
5. **Stage 2 (Fine-Tuning)**: Unfreeze top 30 convolutional layers of MobileNetV2; train with fine learning rate (`lr=1e-5`) and early stopping.

---

## 12. Why MobileNetV2?

MobileNetV2 was selected as the final production model based on empirical experimentation against a 4-stage Custom CNN baseline:
- **Inverted Residuals & Linear Bottlenecks**: Allows efficient gradient propagation across high-dimensional feature manifolds while minimizing memory footprint.
- **Depthwise Separable Convolutions**: Factorizes standard convolutions into lightweight spatial filtering and 1×1 pointwise channel combinations, reducing compute by 8×.
- **Empirical Superiority**: Achieved **+18.47 percentage points higher accuracy** and **+19.53 percentage points higher Macro F1** compared to the custom CNN baseline.
- **High CPU Efficiency**: Averages ~61.15 ms latency per image on standard CPU hardware (~16.4 FPS), satisfying real-time deployment constraints.

---

## 13. Model Performance & Comparison

| Metric | Custom CNN Baseline | MobileNetV2 (Selected Model) | Improvement (Delta) |
| :--- | :---: | :---: | :---: |
| **Architecture** | 4-Stage Conv2D + Dropout | Depthwise Separable Conv (Transfer Learning) | Optimized Inverted Residuals |
| **Total Parameters** | 259,526 | **2,422,726** | +2,163,200 |
| **Test Accuracy** | 68.60% | **87.07%** | **+18.47% pts** |
| **Macro Precision** | 68.00% | **86.23%** | **+18.23% pts** |
| **Macro Recall** | 69.23% | **84.44%** | **+15.21% pts** |
| **Macro F1-Score** | 65.61% | **85.14%** | **+19.53% pts** |
| **Weighted F1-Score**| 68.94% | **87.00%** | **+18.06% pts** |
| **Training Duration**| ~25.91 min | **~8.36 min** | **~3.1× shorter measured training time** |
| **CPU Inference Latency**| ~42.1 ms | **~61.15 ms** | Real-time capable (<65 ms) |

### Per-Class Test Performance (MobileNetV2)
- **`cardboard`**: Precision 92.1%, Recall 95.1%, F1-Score **93.5%**
- **`glass`**: Precision 84.6%, Recall 88.0%, F1-Score **86.3%**
- **`metal`**: Precision 85.5%, Recall 77.0%, F1-Score **81.0%**
- **`paper`**: Precision 89.2%, Recall 93.3%, F1-Score **91.2%**
- **`plastic`**: Precision 88.2%, Recall 82.2%, F1-Score **85.1%**
- **`trash`**: Precision 77.8%, Recall 70.0%, F1-Score **73.7%**

---

## 14. Project Folder Structure

```
Waste_Classification_DL_System/
├── .env.example
├── .gitignore
├── README.md
├── artifacts/
│   ├── cnn_baseline/
│   │   ├── confusion_matrix.png
│   │   ├── metrics.json
│   │   └── training_history.png
│   ├── final/
│   │   ├── class_names.json
│   │   ├── metrics.json
│   │   ├── model_metadata.json
│   │   └── waste_classifier.keras
│   └── mobilenet/
│       ├── confusion_matrix.png
│       ├── metrics.json
│       └── training_history.png
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── model_loader.py
│   │   ├── schemas.py
│   │   ├── ml/
│   │   │   ├── class_weights.py
│   │   │   ├── data_loader.py
│   │   │   ├── evaluate.py
│   │   │   ├── export_final_model.py
│   │   │   ├── gradcam.py
│   │   │   ├── model_config.py
│   │   │   ├── model_utils.py
│   │   │   ├── preprocessing.py
│   │   │   ├── reload_and_benchmark.py
│   │   │   ├── train_cnn.py
│   │   │   └── train_mobilenet.py
│   │   └── routes/
│   │       ├── dataset.py
│   │       ├── health.py
│   │       ├── history.py
│   │       ├── model.py
│   │       └── prediction.py
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       └── test_api.py
├── configs/
│   ├── cnn_config.yaml
│   ├── dataset_config.yaml
│   └── mobilenet_config.yaml
├── data/
│   ├── dataset_manifest.csv
│   ├── processed/
│   │   ├── test/ (379 images across 6 classes)
│   │   ├── train/ (1769 images across 6 classes)
│   │   └── val/ (379 images across 6 classes)
│   └── raw/
│       └── TrashNet/ (2527 images across 6 classes)
├── docs/
│   ├── API_SPECIFICATION.md
│   ├── ARCHITECTURE.md
│   ├── DATASET_CARD.md
│   ├── FEATURES.md
│   ├── FINAL_DEMO_SCRIPT.md
│   ├── FINAL_PROJECT_REPORT_CONTENT.md
│   ├── FINAL_RESULTS.md
│   ├── FINAL_SECURITY_AUDIT.md
│   ├── ML_SPECIFICATION.md
│   ├── ROADMAP.md
│   ├── SCREENSHOT_CHECKLIST.md
│   ├── UI_DESIGN.md
│   └── VIVA_QUESTIONS_AND_ANSWERS.md
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── index.css
│       ├── main.tsx
│       ├── api/
│       │   └── client.ts
│       ├── components/
│       │   ├── Navbar.tsx
│       │   └── layout/
│       │       └── Layout.tsx
│       ├── pages/
│       │   ├── AboutPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── DatasetPage.tsx
│       │   ├── HistoryPage.tsx
│       │   ├── PerformancePage.tsx
│       │   ├── PredictionPage.tsx
│       │   ├── SettingsPage.tsx
│       │   └── TrainingPage.tsx
│       └── types/
│           └── index.ts
├── scripts/
│   ├── duplicate_audit.py
│   ├── e2e_full_system_test.py
│   ├── regenerate_manifest.py
│   ├── test_gradcam.py
│   └── verify_dataset.py
└── UI_MOCKUPS/
    ├── UI_MOCKUP_1_DASHBOARD.md
    ├── UI_MOCKUP_2_PREDICT_FLOW.md
    └── UI_MOCKUP_3_HISTORY_EXPORT.md
```

---

## 15. Prerequisites

Before installing the project, verify that your local environment meets these requirements:
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Python 3.10, 3.11, or 3.12
- **Node.js**: Node.js 18+ (Node 20+ recommended)
- **Package Manager**: `npm` (comes with Node.js)
- **RAM**: Minimum 4 GB (8 GB recommended for local deep learning models)
- **Disk Space**: ~2 GB free disk space (includes dataset, Python packages, model weights, and node modules)

---

## 16. Installation

### 1. Python Environment Setup
Open a terminal in the project root directory:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows PowerShell:
.\.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Frontend Dependencies Setup
Open a second terminal or navigate to the frontend folder:

```bash
cd frontend
npm install
cd ..
```

---

## 17. Environment Setup

Copy `.env.example` to create a local `.env` configuration if you wish to adjust default ports or upload parameters:

```bash
cp .env.example .env
```

Default settings in `.env.example`:
```ini
APP_ENV=development
APP_NAME=Smart Waste Classification System
API_PREFIX=/api/v1
HOST=127.0.0.1
PORT=8000
FRONTEND_URL=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000/api/v1
MAX_UPLOAD_SIZE_MB=10
DATABASE_URL=sqlite:///../data/waste_classification.db
```

> **NOTE ON CREDENTIALS**:  
> No secret passwords, API keys, or cloud access tokens are required for this local academic project.

---

## 18. Running the Project

You normally require **two active terminal windows**:

### Terminal 1 — Backend Service
```bash
cd Waste_Classification_DL_System
.\.venv\Scripts\activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API**: `http://127.0.0.1:8000`
- **Swagger Interactive Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc API Documentation**: `http://127.0.0.1:8000/redoc`

### Terminal 2 — Frontend Application
```bash
cd Waste_Classification_DL_System\frontend
npm run dev
```
- **Web User Interface**: `http://localhost:5173`

### Optional Terminal 3 — Testing & Verification
When validating the codebase or preparing for academic evaluation:
```bash
cd Waste_Classification_DL_System
.\.venv\Scripts\activate

# Run backend unit tests
python -m pytest backend/tests/test_api.py -v

# Run full system E2E audit
python scripts/e2e_full_system_test.py
```

---

## 19. How to Use the Application

1. Open your web browser and navigate to `http://localhost:5173`.
2. Use the top navigation bar to explore the application:
   - **Dashboard**: View system health, live model metrics, and quick action cards.
   - **Classify**: Upload or drag-and-drop an image of a waste item.
   - **History**: View, search, filter, and manage previous classification logs.
   - **Dataset**: Explore TrashNet class distributions, sample images, and split ratios.
   - **Performance**: View confusion matrices, classification reports, and per-class precision/recall metrics.
   - **Training**: Review empirical training history and the Custom CNN vs. MobileNetV2 ablation study.
   - **About**: Read project background, objectives, and academic methodology.
   - **Settings**: Check backend connection status and system configuration parameters.

---

## 20. Dashboard

The Dashboard provides high-level system observability:
- **System Health Card**: Real-time status indicator connecting to `/api/v1/health`.
- **Model Card**: Displays the active model name (`MobileNetV2 (Transfer Learning)`), version (`v1.0`), and parameter count (`2,422,726`).
- **Empirical Metrics**: Displays the measured test accuracy (`87.07%`), Macro F1 (`85.14%`), and CPU inference latency (`~61.15 ms`).
- **Quick Links**: Fast navigation to classification, dataset statistics, and prediction history.

---

## 21. Waste Prediction Flow

1. Navigate to the **Classify (Prediction)** page.
2. Select or drag-and-drop a waste image (`.jpg`, `.jpeg`, `.png`, max 10 MB).
3. Toggle the **Grad-CAM Explainability** checkbox if visual heatmap analysis is desired.
4. Click **Classify Waste Item**.
5. View the instant results:
   - **Predicted Category Badge**: Highlighted waste category (e.g., `plastic`, `cardboard`).
   - **Confidence Score**: Percentage confidence calculated from the softmax output layer.
   - **Inference Latency**: Real CPU execution time measured in milliseconds (typically 50–70 ms).
   - **Probability Distribution**: Full 6-bar horizontal breakdown of all class probabilities.

---

## 22. Grad-CAM Explainability

**Gradient-weighted Class Activation Mapping (Grad-CAM)** provides visual proof of why the convolutional network made its decision:
- **Target Convolutional Layer**: Backpropagates gradients into the `out_relu` activation layer of MobileNetV2.
- **Heatmap Generation**: Computes channel-wise importance weights $\alpha_k^c$ via global average pooling of gradients, applies ReLU to focus only on positive features, and scales the activation intensity.
- **Overlay Display**: Applies a color jet map over the original image and returns it as a Base64 payload, highlighting item rims, transparency, paper textures, or metallic sheen.

---

## 23. Prediction History & Audit

- **Category-Based Prediction IDs**: Every prediction receives a human-readable, category-based sequence ID with independent class counters (e.g., `TC1`, `TG1`, `TM1`, `TP1`, `TPL1`, `TT1`).
- **Persistent Local Image Storage**: The exact image that was analyzed is saved locally in `data/uploads/predictions/<prediction_id>.<ext>`.
- **SQLite Database Persistence**: SQLite stores prediction metadata, full probability distributions, and the relative image path in `data/waste_classification.db`.
- **History Table Thumbnails**: The Prediction History page displays the actual analyzed image thumbnail in the image column.
- **Prediction Audit Records**: The audit modal displays the full analyzed image alongside the complete 6-class probability distribution and original filename.
- **Persistence Across Restarts**: Stored images and category IDs survive browser refresh, frontend restart, and backend server restarts.
- **Safe Cascading Deletion**: Deleting a prediction record from the audit log removes both its database entry and its associated stored image from disk safely.

### Class Prefix Mapping

| Class | Prefix | Example |
|---|---|---|
| Cardboard | TC | TC1 |
| Glass | TG | TG1 |
| Metal | TM | TM1 |
| Paper | TP | TP1 |
| Plastic | TPL | TPL1 |
| Trash | TT | TT1 |

---

## 24. Dataset Information Page

- **Total Dataset Size**: 2,527 images.
- **Distribution Table**: Breakdown across all 6 classes (`cardboard`: 403, `glass`: 501, `metal`: 410, `paper`: 594, `plastic`: 482, `trash`: 137).
- **Split Visualizer**: Train (70%, 1,769 images), Validation (15%, 379 images), Test (15%, 379 images).
- **Class Characteristics**: Recyclability status and visual properties for each category.

---

## 25. Model Performance Page

- **Macro & Weighted Metrics**: Precision (86.23%), Recall (84.44%), Macro F1 (85.14%), Weighted F1 (87.00%).
- **Interactive Confusion Matrix**: Normalized and raw confusion matrix visualization highlighting accurate predictions along the diagonal.
- **Per-Class Breakdown Table**: Precision, recall, and F1-score for each category.

---

## 26. Training Information Page

- **Ablation Comparison**: Side-by-side comparison of the Custom CNN Baseline vs. MobileNetV2.
- **Training Progression**: Loss and accuracy curves over the 17 fine-tuning epochs.
- **Hyperparameter Specifications**: Learning rates (`1e-3` stage 1, `1e-5` stage 2), batch size (`16`), optimizer (`Adam`), loss function (`CategoricalCrossentropy`).

---

## 27. API Documentation

The backend exposes a fully documented, type-safe REST API built with FastAPI. All endpoints return standardized JSON responses and include input schema validation via Pydantic.

Interactive documentation interfaces:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc UI**: `http://127.0.0.1:8000/redoc`

---

## 28. API Endpoints

| Method | Endpoint | Description | Request Payload / Params | Response Summary |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health & model readiness | None | Status, model loaded boolean, uptime |
| `GET` | `/api/v1/model/info` | Active model architecture & params | None | Name, architecture, parameter count, input shape |
| `GET` | `/api/v1/model/metrics` | Empirical evaluation benchmarks | None | Test accuracy, macro F1, weighted F1, latency |
| `GET` | `/api/v1/dataset/info` | TrashNet split & distribution data | None | Total count, split counts, class distribution |
| `GET` | `/api/v1/dataset/classes` | List of supported waste classes | None | Array of 6 class names |
| `POST` | `/api/v1/predict` | Single waste image classification | Multipart file upload | Predicted class, confidence, probabilities, latency |
| `POST` | `/api/v1/predict/gradcam` | Classification with Grad-CAM overlay | Multipart file upload | Prediction + Base64 Grad-CAM heatmap overlay |
| `GET` | `/api/v1/predictions` | Paginated prediction history list | `limit` (1–200), `offset` (>=0) | Total count and array of prediction items |
| `GET` | `/api/v1/predictions/{id}` | Single prediction record lookup | `id` (UUID or integer ID) | Complete prediction record details |
| `DELETE` | `/api/v1/predictions/{id}` | Delete prediction from SQLite | `id` (UUID or integer ID) | Success message or HTTP 404 |

---

## 29. Testing & Verification

The project includes an automated test suite verifying model loading, API responses, validation boundaries, and full-system data flows:

### 1. Backend Pytest Suite
```bash
python -m pytest backend/tests/test_api.py -v
```
- **Verified**: 16 unit and integration test cases covering health, model info, dataset metadata, real image inference across PNG/JPG formats, Grad-CAM generation, extension checks, corrupted file handling, 10 MB payload capping, and SQLite CRUD lifecycle.
- **Current Status**: **16 / 16 PASSED**.

### 2. Frontend Production Build & TypeScript Verification
```bash
cd frontend && npm run build
```
- **Verified**: Type safety across all TSX components and clean production asset bundling via Vite.
- **Current Status**: **0 TypeScript Errors, 0 Vite Build Errors**.

### 3. Full System End-to-End Audit
```bash
python scripts/e2e_full_system_test.py
```
- **Verified**: 7/7 audit sectors covering dataset integrity, model loading, REST endpoints, real image inference across all 6 classes, Grad-CAM generation, SQLite persistence, and security exception handling.
- **Current Status**: **7 / 7 SECTORS PASSED (100% Success)**.

---

## 30. Security & Safety

The application implements practical security safeguards suited for a local academic deployment:
- **Strict File Extension Whitelisting**: Accepts only `.jpg`, `.jpeg`, and `.png` files.
- **MIME & Structure Validation**: Employs Pillow's `img.verify()` to block corrupted or spoofed payloads before tensor conversion.
- **Maximum Upload Ceiling**: Caps incoming request size at 10 MB (returns HTTP 413 if exceeded).
- **In-Memory Streaming**: Image bytes are processed via `io.BytesIO` and never executed as scripts on disk.
- **Safe Identifier Generation**: Uploaded files receive UUID v4 prefixes to prevent filesystem path collisions and overwrites.
- **Path Traversal Protection**: All filesystem references are built using Python's `pathlib.Path` relative to the workspace root.
- **SQL Injection Prevention**: 100% of SQLite queries utilize parameterized statements (`?` placeholders).
- **Restricted CORS Policy**: Restricts cross-origin requests exclusively to local loopback origins (`localhost:5173`, `127.0.0.1:5173`, `localhost:3000`, `127.0.0.1:3000`).
- **Structured Error Envelopes**: API exceptions return clean JSON payloads (`detail.code`, `detail.message`) without leaking internal Python tracebacks or environment variables.

---

## 31. Authentication

**This project does not require user authentication.**

No username or password is required to:
- Start or access the backend API
- Start or access the React frontend
- Upload images or receive classifications
- Generate Grad-CAM heatmaps
- View prediction history or delete records
- Inspect dataset and model metrics

The application operates locally on your machine and persists prediction history directly into a local SQLite database file.

---

## 32. Troubleshooting

### Issue 1: `Port 8000 or 5173 is already in use`
- **Resolution**: Free the port or specify an alternative port:
  - Backend: `uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload`
  - Frontend: `npm run dev -- --port 5174`

### Issue 2: `Model file not found on startup`
- **Resolution**: Verify that `artifacts/final/waste_classifier.keras` exists. If missing, ensure the submission package was fully extracted.

### Issue 3: `TensorFlow GPU Warning on Windows`
- **Explanation**: TensorFlow >= 2.11 does not natively support GPU on Windows without WSL2. The warning is informational; the model runs smoothly and deterministically on standard CPU cores in ~61.15 ms.

### Issue 4: `ModuleNotFoundError in Python`
- **Resolution**: Verify your virtual environment is active (`.\.venv\Scripts\activate`) and reinstall requirements:
  ```bash
  pip install -r backend/requirements.txt
  ```

---

## 33. Important Commands Reference

```bash
# 1. Start Backend API Server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start Frontend Development Server
cd frontend && npm run dev

# 3. Build Frontend for Production
cd frontend && npm run build

# 4. Run Pytest Test Suite
python -m pytest backend/tests/test_api.py -v

# 5. Run Full System End-to-End Integration Audit
python scripts/e2e_full_system_test.py

# 6. Run Dataset Split Verification
python scripts/verify_dataset.py

# 7. Run Duplicate Image Hash Audit
python scripts/duplicate_audit.py
```

---

## 34. Dataset Limitations

1. **Controlled Studio Conditions**: TrashNet images were captured under artificial lighting against uniform white backgrounds. Real-world municipal sorting facilities feature complex, cluttered backgrounds and variable illumination.
2. **Minority Class Imbalance**: The `trash` category contains only 137 samples (5.4% of dataset) compared to 594 in `paper`, resulting in higher variance for mixed waste items.
3. **Identical Content Pairs**: A SHA-256 byte audit identified 3 duplicate content pairs in the raw dataset. These were isolated using group-aware splitting to guarantee zero data leakage across train/val/test partitions.

---

## 35. Future Scope

- **Edge Deployment & Quantization**: Convert the model to INT8 TensorFlow Lite (`.tflite`) or ONNX Web for client-side in-browser inference without server roundtrips.
- **Multi-Object Detection**: Integrate YOLOv8 or Faster R-CNN to localize and classify multiple waste objects in a single scene.
- **Expanded Category Taxonomies**: Extend the dataset to incorporate organic/compostable waste, electronic waste (e-waste), hazardous chemicals, and textiles.
- **Mobile Application Wrapper**: Package the frontend with React Native or Capacitor for real-time camera-based waste sorting on smartphones.

---

## 36. Results Summary

```
================================================================================
                    FINAL EMPIRICAL EVALUATION SUMMARY                          
================================================================================
  Selected Model Architecture : MobileNetV2 (Transfer Learning)
  Total Parameters            : 2,422,726 (2.42M)
  Test Accuracy               : 87.07%
  Macro Precision             : 86.23%
  Macro Recall                : 84.44%
  Macro F1-Score              : 85.14%
  Weighted F1-Score           : 87.00%
  Average CPU Inference       : ~61.15 ms (~16.4 FPS)
  Accuracy Gain over Baseline : +18.47 percentage points
  Macro F1 Gain over Baseline : +19.53 percentage points
  Training Efficiency Gain    : ~3.1× shorter measured training time
  Backend Pytest Pass Rate    : 16 / 16 (100%)
  Frontend Build Errors       : 0 TypeScript / 0 Vite errors
  E2E System Audit Status     : 7 / 7 Sectors Passed (100% Success)
  Final Security Status       : PASS (0 Critical / 0 High Vulnerabilities)
================================================================================
```

---

## 37. Academic Information

- **Project Title**: AI-Powered Waste Classification System using Deep Learning
- **Application Branding**: EcoClassify DL
- **Domain**: Computer Vision, Deep Learning, Environmental Informatics, Full-Stack Web Engineering
- **Evaluation Benchmark**: TrashNet (Gary Thung & Mindy Yang, Stanford University)
- **Primary Deliverables**: Trained Keras Model, REST API Backend, SQLite History, React 19 Frontend, Grad-CAM Explainer, Complete Academic Documentation Suite.

---

## 38. Credits & Citation

### Dataset Citation
If utilizing this dataset or project for research, please cite the original TrashNet creators:

```bibtex
@article{thung2016trashnet,
  title={Classification of Trash for Recyclability Status},
  author={Thung, Gary and Yang, Mindy},
  journal={CS229 Project Report, Stanford University},
  year={2016}
}
```

### Framework & Model Citations
- **MobileNetV2**: Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C. (2018). *MobileNetV2: Inverted Residuals and Linear Bottlenecks*. CVPR 2018.
- **Grad-CAM**: Selvaraju, R. R., Cogswell, M., Das, A., Vedaldi, A., Parikh, D., & Batra, D. (2017). *Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization*. ICCV 2017.

---

## 39. License

This project is developed for academic and research evaluation purposes under the **MIT License**.
