# Phase 11 — Final 8-Class Dataset Construction & Audit Report

**Project**: EcoClassify DL — AI-Powered Waste Classification System  
**Phase**: 11 Final 8-Class Dataset Construction (Reproducible / Non-Destructive / No Model Training)  
**Date**: 2026-10-04  
**Status**: **SUCCESS — DATASET CONSTRUCTED & FULLY VALIDATED**  
**Output Path**: `data/final/8class/`  

---

## 1. Dataset Objective & Overview

The objective of Phase 11 is the reproducible, deterministic, and non-destructive construction of the derived **8-class waste classification dataset** for EcoClassify DL. This dataset expands the system's categorization capabilities from the initial 6 classes (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash`) to 8 comprehensive waste streams by incorporating:
1. `biodegradable` (Compostable organic fruit, vegetable, grain, and agricultural scraps)
2. `e_waste` (High-priority consumer electronics, circuit boards, and battery waste)

> [!IMPORTANT]
> **Data Protection & Integrity Mandate**:
> * **The original raw datasets remain completely untouched**.
> * **The frozen 6-class production baseline (`v1.0.0-baseline`, commit `9a3dff3`) remains 100% intact and unaltered**.
> * **Zero model training or parameter modifications occurred during this phase**.
> * **The derived dataset is cleanly quarantined under `data/final/8class/`** and ignored by Git.

---

## 2. Baseline Protection & Git Reference

* **Baseline Git Tag**: `v1.0.0-baseline`
* **Baseline Commit**: `9a3dff3` (`Initial baseline: 6-class waste classification system`)
* **Branch**: `main`
* **Frozen Baseline Status**: 100% Frozen & Untouched (17/17 backend regression tests passing).
* **Isolation**: The derived dataset resides strictly in `data/final/8class/` and does not overwrite `data/raw/` or `data/processed/`.

---

## 3. Source Datasets & Source-to-Class Mapping

The derived 8-class dataset was constructed deterministically from the following source repositories:

| Target Class Index | Target Class Name | Category Prefix | Source Dataset | Source Sub-Categories Used | Target Images Selected |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **0** | `biodegradable` | `TB` | `data/raw/organic/BDWaste/` | `1. Sugarcane  husk` (73)<br>`3. Potato Peel` (73)<br>`5. Mango Peel` (72)<br>`6. Rice` (73)<br>`7. Shell of Malta` (14)<br>`8.Lemon Peel` (73)<br>`9. Banana peel` (72) | **450** |
| **1** | `cardboard` | `TC` | `data/raw/TrashNet/cardboard/` | All 403 original TrashNet images | **403** |
| **2** | `e_waste` | `TE` | `data/raw/external/ewaste/EWaste_Image_Dataset/` | `Battery` (90)<br>`Keyboard` (90)<br>`Mobile` (90)<br>`Mouse` (90)<br>`PCB` (90) | **450** |
| **3** | `glass` | `TG` | `data/raw/TrashNet/glass/` | All 501 original TrashNet images | **501** |
| **4** | `metal` | `TM` | `data/raw/TrashNet/metal/` | All 410 original TrashNet images | **410** |
| **5** | `paper` | `TP` | `data/raw/TrashNet/paper/` | All 594 original TrashNet images | **594** |
| **6** | `plastic` | `TPL` | `data/raw/TrashNet/plastic/` | All 482 original TrashNet images | **482** |
| **7** | `trash` | `TT` | `data/raw/TrashNet/trash/` | All 137 original TrashNet images | **137** |
| **TOTAL** | **8 Classes** | — | — | **Deterministic Improved Balance** | **3,427** |

---

## 4. Excluded Categories & Architectural Rationale

To maintain extreme dataset purity and eliminate inter-class label ambiguities, the following source categories were strictly excluded:

1. **`CTSoc_EWaste` (Excluded completely)**: Contains 57 files consisting of post-training bounding-box detection plots, loss graphs, and evaluation results. These are not clean classification samples.
2. **`EWaste_Image_Dataset` Exclusions**: `Microwave`, `Player`, `Printer`, `Television`, `Washing Machine` were excluded to keep the `e_waste` category tightly focused on high-frequency small consumer electronics, computer peripherals, batteries, and printed circuit boards.
3. **`BDWaste/4. Paper` (Excluded)**: Excluded because paper is already a dedicated dry recyclable class in TrashNet. Including paper in biodegradable would cause severe inter-class confusion.
4. **`BDWaste/10. Coffee  cup` (Excluded)**: Single-use paper coffee cups contain polyethylene plastic linings, making them non-compostable composite items.
5. **`BDWaste/2. Fish ash` (Excluded)**: Combustion ash is inorganic mineral residue, not compostable organic food or plant matter.

---

## 5. Selection, Deduplication & Near-Duplicate Protection

### 5.1. Exact Content Hash Deduplication
Prior to final selection, all candidates were scanned for MD5 and SHA-256 hash collisions:
* All 450 `e_waste` images were sampled from strictly unique MD5 hashes (90 unique images per 5 categories).
* In `BDWaste/7. Shell of Malta`, where 116 duplicated copies of 14 images existed, strict deduplication was enforced to retain all 14 unique images with 0 duplicates.
* Across all 3,427 derived images, **every single image corresponds to a unique source file (0 duplicate content)**.

### 5.2. Atomic Near-Duplicate Group Allocation
The audit identified perceptual near-duplicate clusters (video burst frames of peeling fruit or multi-angle captures of electronics):
* All images sharing an identical dHash perceptual signature were clustered into atomic entity groups (`NDG_0001` through `NDG_0020`).
* **Atomic Partitioning Rule**: Every entity group was allocated entirely to a single partition (100% Train OR 100% Val OR 100% Test).
* **Result**: **0 near-duplicate group leaks** cross the train, validation, or test split boundaries.

---

## 6. Group-Aware Stratified 70 / 15 / 15 Split Methodology

The final partitioning was performed using group-aware greedy stratification with `SEED = 42`:

| Target Class Index | Class Name | Category Prefix | Total Images | Train Split (70.0%) | Validation Split (15.0%) | Test Split (15.0%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **0** | `biodegradable` | `TB` | 450 | 315 (70.0%) | 68 (15.1%) | 67 (14.9%) |
| **1** | `cardboard` | `TC` | 403 | 282 (70.0%) | 60 (14.9%) | 61 (15.1%) |
| **2** | `e_waste` | `TE` | 450 | 315 (70.0%) | 68 (15.1%) | 67 (14.9%) |
| **3** | `glass` | `TG` | 501 | 351 (70.1%) | 75 (15.0%) | 75 (15.0%) |
| **4** | `metal` | `TM` | 410 | 287 (70.0%) | 62 (15.1%) | 61 (14.9%) |
| **5** | `paper` | `TP` | 594 | 416 (70.0%) | 89 (15.0%) | 89 (15.0%) |
| **6** | `plastic` | `TPL` | 482 | 337 (69.9%) | 72 (14.9%) | 73 (15.1%) |
| **7** | `trash` | `TT` | 137 | 96 (70.1%) | 21 (15.3%) | 20 (14.6%) |
| **TOTAL** | **8 Classes** | — | **3,427** | **2,399 (70.00%)** | **515 (15.03%)** | **513 (14.97%)** |

---

## 7. Sample ID Formatting & Metadata Structure

### 7.1. Deterministic Sample ID Standard
Each sample was assigned a unique, non-colliding, deterministic identifier:
* `biodegradable`: `TB0001` – `TB0450`
* `cardboard`: `TC0001` – `TC0403`
* `e_waste`: `TE0001` – `TE0450`
* `glass`: `TG0001` – `TG0501`
* `metal`: `TM0001` – `TM0410`
* `paper`: `TP0001` – `TP0594`
* `plastic`: `TPL0001` – `TPL0482`
* `trash`: `TT0001` – `TT0137`

### 7.2. Metadata Files Generated
1. [`data/final/8class/metadata/dataset_manifest.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/data/final/8class/metadata/dataset_manifest.csv): Comprehensive 21-column traceability manifest recording relative source paths, derived relative paths, dimensions, channels, MD5, SHA-256, near-duplicate group IDs, and split assignments.
2. [`data/final/8class/metadata/class_mapping.json`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/data/final/8class/metadata/class_mapping.json): Explicit integer index to class name, prefix, and target count mapping.
3. [`data/final/8class/metadata/dataset_metadata.json`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/data/final/8class/metadata/dataset_metadata.json): Complete dataset provenance, policies, and configuration metadata.

---

## 8. Physical File Integrity & Leakage Audit Results

The independent validation script (`scripts/validate_8class_dataset.py`) performed a comprehensive check across all 3,427 images:

```
================================================================================
VALIDATING EXTENDED 8-CLASS DATASET (data/final/8class/)
================================================================================

[CHECK 1] Validating Directory & Metadata Structure...
  [PASS] All split and class directories and metadata files exist.

[CHECK 2] Validating Manifest and Class Mapping Content...
  Total records in manifest: 3427

[CHECK 3] Verifying Physical File Integrity and Pillow Readability...
  Physical images found: 3427
  [PASS] All 3427 images successfully opened & verified with Pillow (Corrupted: 0).

[CHECK 4] Verifying Class Totals and Split Distribution...
  - Class 'biodegradable  ':  450 / 450 target
  - Class 'cardboard      ':  403 / 403 target
  - Class 'e_waste        ':  450 / 450 target
  - Class 'glass          ':  501 / 501 target
  - Class 'metal          ':  410 / 410 target
  - Class 'paper          ':  594 / 594 target
  - Class 'plastic        ':  482 / 482 target
  - Class 'trash          ':  137 / 137 target

  Split Breakdown:
  - Train:      2399 (70.00%)
  - Validation:  515 (15.03%)
  - Test:        513 (14.97%)
  - Total:      3427 (100.0%)

[CHECK 5] Running Exact & Near-Duplicate Leakage Audit...
  Exact Duplicate Cross-Split Leaks: 0
  Near-Duplicate Cross-Split Leaks:  0
  Unique Source References:          3427 / 3427

================================================================================
ALL VALIDATION CHECKS PASSED PERFECTLY (100% LEAKAGE-FREE & CONSISTENT)
================================================================================
```

---

## 9. Backend Regression Protection

To guarantee that adding the new dataset did not affect the existing 6-class production system, the backend test suite was executed:
* **Command**: `python -m pytest backend/tests/test_api.py -v`
* **Result**: **17 / 17 tests passed (100%) in 14.07s**.
* **Zero regressions detected**.

---

## 10. Reproducibility Instructions

To reproduce the exact dataset construction from scratch:

```bash
# 1. Build the derived 8-class dataset
python scripts/build_8class_dataset.py

# 2. Run independent validation
python scripts/validate_8class_dataset.py

# 3. Run regression tests
python -m pytest backend/tests/test_api.py -v
```

---

## 11. Known Limitations & Recommendations for Phase 12 Training

1. **Trash Class Imbalance**: The residual `trash` class contains 137 genuine images compared to ~450 images for other classes. This was intentionally preserved to prevent synthetic artifacts. During Phase 12 model training, **Class-Balanced Loss Weighting** ($\text{weight}_c \propto 1/N_c$) or **Focal Loss** ($\gamma=2.0$) should be utilized alongside dynamic online data augmentation.
2. **Organic Background Variety**: The BDWaste organic dataset consists predominantly of close-up countertop and cutting-board photography. Transfer learning with MobileNetV2 pretrained on ImageNet combined with color jitter, random rotations, and scaling will ensure robust generalization.
