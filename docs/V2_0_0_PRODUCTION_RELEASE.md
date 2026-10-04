# EcoClassify DL — Production Release v2.0.0 (8-Class Unified System)

**Release Version**: `v2.0.0-8class`  
**Previous Baseline**: `v1.0.0-baseline` (commit `9a3dff3`)  
**Release Date**: 2026-10-04  
**Release Status**: **PRODUCTION ACTIVE**  
**Repository**: [EcoClassify-DL-AI-Powered-Waste-Classification-System](https://github.com/Tamannshaikh/EcoClassify-DL-AI-Powered-Waste-Classification-System.git)  

---

## 1. Release Overview

EcoClassify DL version **v2.0.0** promotes the unified **8-Class MobileNetV2 Deep Learning Model** into full production across backend and frontend systems. Building upon the frozen 6-class TrashNet baseline, v2.0.0 expands classification coverage to include two critical ecological waste streams:
1. **`biodegradable`** (organic compost, food scraps, peels, agricultural residues)
2. **`e_waste`** (electronics, printed circuit boards, batteries, electronic accessories)

The system delivers **89.08% overall test accuracy**, **87.81% Macro F1-score**, and **89.20% Weighted F1-score** while maintaining single-instance CPU inference, real-time explainability via Grad-CAM, SQLite history persistence, and full frontend visualization.

---

## 2. Frozen Baseline Reference & Preservation

The original 6-class production baseline remains fully preserved and recoverable:

* **Git Tag**: `v1.0.0-baseline`
* **Commit**: `9a3dff3`
* **Baseline Model SHA-256**: `41417f46364227d8556b225359c3f9be58d94983a177930e92fdf35ef4526911`
* **Local Safety Backup**: `artifacts/backup/v1.0.0-baseline/`
  * `waste_classifier.keras`
  * `class_names.json`
  * `model_metadata.json`
  * `metrics.json`

---

## 3. Production v2.0.0 Model Specification

* **Model File**: `artifacts/final/waste_classifier.keras`
* **Model Format**: Keras 3 SavedModel (`.keras`)
* **Framework**: TensorFlow 2.21.0 / Keras 3.15.1
* **Input Dimensions**: `(224, 224, 3)` RGB Normalized `[-1, 1]`
* **Output Dimensions**: `(None, 8)` Softmax Probabilities
* **Total Parameters**: 2,422,984
* **SHA-256 Hash**: `5d27f8c18886b56110d04d75885941482f17b33be60dd0a429a158f30c4717fa`

---

## 4. Unified 8-Class Dataset (`8class-v1.0`)

The training, validation, and test datasets were constructed from verified, non-corrupted source images with zero cross-split leakage:

* **Total Dataset Size**: 3,427 images
* **Split Allocation**:
  * **Train Set**: 2,399 images (70%)
  * **Validation Set**: 515 images (15%)
  * **Test Set**: 513 images (15%)
* **Cross-Split Duplicate Matches**: 0 exact, 0 near-duplicate matches.

---

## 5. Authoritative 8-Class Mapping & Prefixes

| Class Index | Class Name | Public ID Prefix | Target Count | Test Support | Disposal Bin Mapping |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `0` | **`biodegradable`** | `TB` | 450 | 67 | Green / Organics & Compost |
| `1` | **`cardboard`** | `TC` | 403 | 61 | Blue / Dry Recyclables |
| `2` | **`e_waste`** | `TE` | 450 | 67 | Purple / Dedicated E-Waste Drop-Off |
| `3` | **`glass`** | `TG` | 501 | 75 | Teal / Glass Recyclables |
| `4` | **`metal`** | `TM` | 410 | 61 | Grey / Metal Recyclables |
| `5` | **`paper`** | `TP` | 594 | 89 | Blue / Paper Recyclables |
| `6` | **`plastic`** | `TPL` | 482 | 73 | Yellow / Plastic Recyclables |
| `7` | **`trash`** | `TT` | 137 | 20 | Black / General Landfill |

---

## 6. Model Architecture & Training Summary

* **Backbone**: MobileNetV2 (ImageNet pre-trained weights).
* **Classification Head**:
  * `GlobalAveragePooling2D`
  * `Dense(128, activation="relu")`
  * `Dropout(rate=0.30)`
  * `Dense(8, activation="softmax")`
* **Two-Stage Training**:
  * **Stage 1 (Head Training)**: 18 epochs, learning rate $1\times 10^{-3}$, Adam optimizer with class-balanced weighting. Restored best checkpoint from **Epoch 13** (`val_loss = 0.3253`, `val_acc = 89.71%`).
  * **Stage 2 (Fine-Tuning)**: Top 30 MobileNetV2 layers unfrozen, 6 epochs, learning rate $1\times 10^{-5}$.
  * **Total Training Time**: 1,697.4 seconds (~28.3 minutes on CPU).

---

## 7. Quantitative Test Performance

Evaluated strictly once on the held-out test split ($N = 513$):

* **Overall Test Accuracy**: **89.08%**
* **Macro Precision**: **87.44%**
* **Macro Recall**: **88.51%**
* **Macro F1-Score**: **87.81%**
* **Weighted Precision**: **89.58%**
* **Weighted Recall**: **89.08%**
* **Weighted F1-Score**: **89.20%**

---

## 8. Per-Class Performance Breakdown

```
                       PREDICTED CLASS
             bio   card  ewst  glas  metl  papr  plas  trsh  | Total
True Class:
bio           67      0     0     0     0     0     0     0  |   67
card           0     56     0     0     0     3     1     1  |   61
ewst           0      0    66     0     1     0     0     0  |   67
glas           0      0     0    67     3     0     5     0  |   75
metl           0      0     0     8    50     0     0     3  |   61
papr           0      5     0     0     2    75     3     4  |   89
plas           0      0     0     9     4     0    60     0  |   73
trsh           0      0     0     0     3     1     0    16  |   20
------------------------------------------------------------------
Pred Total    67     61    66    84    63    79    69    24  |  513
```

| Class Name | Precision | Recall | F1-Score | Support | Rating |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `biodegradable` | **1.0000** | **1.0000** | **1.0000** | 67 | Perfect discrimination |
| `cardboard` | **0.9180** | **0.9180** | **0.9180** | 61 | Strong |
| `e_waste` | **1.0000** | **0.9851** | **0.9925** | 67 | Excellent |
| `glass` | **0.7976** | **0.8933** | **0.8428** | 75 | Robust |
| `metal` | **0.7937** | **0.8197** | **0.8065** | 61 | Robust |
| `paper` | **0.9494** | **0.8427** | **0.8929** | 89 | Strong |
| `plastic` | **0.8696** | **0.8219** | **0.8451** | 73 | Robust |
| `trash` | **0.6667** | **0.8000** | **0.7273** | 20 | Acceptable (Imbalance limited) |

---

## 9. CPU Latency Benchmark

* **Hardware Environment**: AMD64 Family 25 Model 124, Windows 11 (oneDNN CPU runtime)
* **Average Inference Latency**: **88.65 ms**
* **Median Latency**: **87.27 ms**
* **95th Percentile (P95)**: **98.29 ms**
* **Throughput**: **~11.3 FPS** (single-stream batch size 1)

---

## 10. Grad-CAM Explainability

* **Target Convolutional Layer**: `mobilenetv2_1.00_224::out_relu`
* **Compatibility**: Native support for 8-class classification head with automatic fallback for legacy architectures.
* **Verification**: Verified across all 8 classes with high spatial localization on salient item boundaries.

---

## 11. Backend & API Validation

* **Unit & Integration Tests (`pytest backend/tests/test_api.py`)**: **17 / 17 PASSED** (100%).
* **REST Endpoints Verified**:
  * `GET /api/v1/health` $\rightarrow$ Reports 8 classes, model loaded.
  * `GET /api/v1/model/info` $\rightarrow$ Metadata for v2.0.0.
  * `GET /api/v1/model/metrics` $\rightarrow$ 8-class per-class scores & 8x8 matrix.
  * `GET /api/v1/dataset/info` & `/dataset/classes` $\rightarrow$ 3,427 images across 8 classes.
  * `POST /api/v1/predict` $\rightarrow$ 8-class output distribution, correct category ID prefixes (`TB`, `TE`, `TPL`, etc.).
  * `POST /api/v1/predict/gradcam` $\rightarrow$ Base64 overlay generation.
  * `GET/DELETE /api/v1/predictions/{id}` $\rightarrow$ CRUD operations and image persistence.

---

## 12. Frontend Application Validation

* **Build Tool**: Vite + TypeScript + React 18.
* **Build Verification (`npm run build`)**: **0 TypeScript errors, 0 Vite build errors**.
* **Pages Updated**:
  * **Dashboard**: 8-class color-coded charts and KPI metrics.
  * **Prediction**: 8-class progress bars and specific disposal bin guidance.
  * **Dataset**: `8class-v1.0` metadata, 3,427 image counts, and split distributions.
  * **Performance**: 8-class confusion matrix, precision/recall/F1 metrics, and latency cards.
  * **Training**: Stage 1 & Stage 2 parameters and two-stage training curves.
  * **About / Settings**: 8-class system taxonomy.

---

## 13. End-to-End System Audit

* **Audit Script (`python scripts/e2e_full_system_test.py`)**: **7 / 7 SECTORS PASSED** (100% Success).
  1. Dataset Integrity: PASS
  2. Model Artifacts: PASS
  3. Core API Endpoints: PASS
  4. Real Predictions (All 8 Classes): PASS
  5. Grad-CAM Heatmaps: PASS
  6. SQLite History Persistence: PASS
  7. Security Boundaries & Exception Handling: PASS

---

## 14. Security & Cleanliness Validation

* **Zero Secrets / API Keys**: Verified.
* **Zero `.env` or Private Credentials Tracked**: Verified.
* **Zero Raw Dataset Files in Git**: Verified (`.gitignore` enforces isolation).
* **Zero Runtime SQLite Databases or Uploads Tracked**: Verified.
* **Zero Build Artifacts (`dist/`, `node_modules/`, `.venv/`) Tracked**: Verified.

---

## 15. Known Limitations & Operational Considerations

1. **`trash` Class Support**: The `trash` class contains 137 total images (20 in test), yielding an F1-score of `0.7273`. While class-weighted loss mitigates imbalance, false positives with composite metal or cardboard packaging remain.
2. **CPU Inference Latency**: Average CPU inference latency is `88.65 ms` (P95: `98.29 ms`), compared to `61.15 ms` in the 6-class baseline (+44.97% increase).
3. **Dataset Lineage & Domain Shift**: Images originate from TrashNet, BDWaste, and EWaste Image Dataset. Differences in photographic background characteristics may cause slight domain variance in real-world deployments.
4. **Metric Comparability**: The 8-class and 6-class performance metrics are evaluated on different label spaces and are not a 1:1 mathematical comparison.

---

## 16. Rollback Procedure

If operational rollback to the 6-class baseline (`v1.0.0-baseline`) is ever required:

```bash
# 1. Restore production artifacts from local backup
cp artifacts/backup/v1.0.0-baseline/* artifacts/final/

# 2. Or check out the baseline tag directly
git checkout v1.0.0-baseline -- artifacts/final/ backend/app/config.py backend/app/ml/model_config.py backend/app/routes/dataset.py

# 3. Verify baseline SHA-256
python -c "import hashlib; assert hashlib.sha256(open('artifacts/final/waste_classifier.keras','rb').read()).hexdigest() == '41417f46364227d8556b225359c3f9be58d94983a177930e92fdf35ef4526911'"
```

---

## 17. Release Git State

* **Branch**: `main`
* **Promoted Version Tag**: `v2.0.0-8class`
* **Permanent Baseline Tag**: `v1.0.0-baseline`
* **Remote Repository**: `origin` (`https://github.com/Tamannshaikh/EcoClassify-DL-AI-Powered-Waste-Classification-System.git`)
