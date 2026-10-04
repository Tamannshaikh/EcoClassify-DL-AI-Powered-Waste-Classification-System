# Extended 8-Class Dataset Audit & Feasibility Report

**Project**: EcoClassify DL — AI-Powered Waste Classification System  
**Audit Phase**: Dataset Discovery, Inventory, Duplicate Analysis & 8-Class Feasibility  
**Date**: 2026-10-04  
**Status**: READ-ONLY AUDIT COMPLETE (Awaiting User Approval — Zero Data/Model Modifications)

---

## 1. Executive Summary

This audit evaluates the feasibility of extending the current production **6-class TrashNet system** (`cardboard`, `glass`, `metal`, `paper`, `plastic`, `trash`) to an **8-class waste classification system** with the addition of:
1. `e_waste` (Electronic waste items & hazardous components)
2. `biodegradable` (Compostable organic food, fruit, and agricultural waste)

All operations during this audit were strictly **read-only**. No models were trained or modified, no datasets were merged or altered, and no files were moved or deleted.

---

## 2. Actual Dataset Paths & Discovery

The audit discovered the following dataset sources in the local workspace:

| Source Name | Exact File System Path | Role / Content |
| :--- | :--- | :--- |
| **TrashNet Raw** | `data/raw/TrashNet/` | Baseline 6-class dataset (2,527 images) |
| **TrashNet Processed** | `data/processed/{train,val,test}/` | Current 70/15/15 leakage-free baseline splits |
| **E-Waste Image Dataset** | `data/raw/external/ewaste/EWaste_Image_Dataset/{train,val,test}/` | 10 electronic waste categories (3,000 images) |
| **CTSoc E-Waste** | `data/raw/external/ewaste/CTSoc_EWaste/ctsoc-ewaste-main/` | Supplementary Indian-context repo (57 images/results) |
| **BDWaste (Organic)** | `data/raw/organic/BDWaste/` | 10 organic/municipal waste categories (1,252 images) |

---

## 3. Dataset Inventory by Source & Class

A total of **9,363 physical image assets** were scanned and verified across all raw sources and processed baseline copies:

### 3.1. Raw / External Source Image Assets (6,836 images)

| Source Dataset | Sub-Category / Class | Total Files | Valid Images | Corrupted | Non-Image | Total Size (MB) | Format | Dominant Dimensions |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TrashNet Raw** | `cardboard` | 403 | 403 | 0 | 0 | 44.88 | JPG | 512x384 (RGB) |
| **TrashNet Raw** | `glass` | 501 | 501 | 0 | 0 | 56.40 | JPG | 512x384 (RGB) |
| **TrashNet Raw** | `metal` | 410 | 410 | 0 | 0 | 45.22 | JPG | 512x384 (RGB) |
| **TrashNet Raw** | `paper` | 594 | 594 | 0 | 0 | 66.82 | JPG | 512x384 (RGB) |
| **TrashNet Raw** | `plastic` | 482 | 482 | 0 | 0 | 54.12 | JPG | 512x384 (RGB) |
| **TrashNet Raw** | `trash` | 137 | 137 | 0 | 0 | 15.34 | JPG | 512x384 (RGB) |
| **EWaste Dataset** | `Battery` (train/val/test) | 300 | 300 | 0 | 0 | 28.65 | JPG | Various (RGB) |
| **EWaste Dataset** | `Keyboard` (train/val/test) | 300 | 300 | 0 | 0 | 31.42 | JPG | Various (RGB) |
| **EWaste Dataset** | `Microwave` (train/val/test) | 300 | 300 | 0 | 0 | 29.80 | JPG | Various (RGB) |
| **EWaste Dataset** | `Mobile` (train/val/test) | 300 | 300 | 0 | 0 | 27.15 | JPG | Various (RGB) |
| **EWaste Dataset** | `Mouse` (train/val/test) | 300 | 300 | 0 | 0 | 26.90 | JPG | Various (RGB) |
| **EWaste Dataset** | `PCB` (train/val/test) | 300 | 300 | 0 | 0 | 34.20 | JPG | Various (RGB) |
| **EWaste Dataset** | `Player` (train/val/test) | 300 | 300 | 0 | 0 | 28.50 | JPG | Various (RGB) |
| **EWaste Dataset** | `Printer` (train/val/test) | 300 | 300 | 0 | 0 | 30.10 | JPG | Various (RGB) |
| **EWaste Dataset** | `Television` (train/val/test) | 300 | 300 | 0 | 0 | 29.40 | JPG | Various (RGB) |
| **EWaste Dataset** | `Washing Machine` (train/val/test) | 300 | 300 | 0 | 0 | 32.10 | JPG | Various (RGB) |
| **CTSoc EWaste** | `dataset-prep` / `results` | 57 | 57 | 0 | 0 | 8.45 | PNG/JPG | 640x480 / Charts |
| **BDWaste** | `1. Sugarcane  husk` | 125 | 125 | 0 | 0 | 18.20 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `2. Fish ash` | 125 | 125 | 0 | 0 | 17.85 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `3. Potato Peel` | 130 | 130 | 0 | 0 | 19.40 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `4. Paper` | 125 | 124 | 0 | 1 (`47.pg`) | 18.10 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `5. Mango Peel` | 121 | 121 | 0 | 0 | 17.50 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `6. Rice` | 127 | 127 | 0 | 0 | 18.90 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `7. Shell of Malta` | 126 | 126 | 0 | 0 | 18.70 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `8.Lemon Peel` | 125 | 125 | 0 | 0 | 18.30 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `9. Banana peel` | 123 | 123 | 0 | 0 | 17.95 | JPG | 1080x1920 (RGB) |
| **BDWaste** | `10. Coffee  cup` | 126 | 126 | 0 | 0 | 18.60 | JPG | 1080x1920 (RGB) |
| **Subtotal** | **Raw Sources** | **6,837** | **6,836** | **0** | **1** | — | — | — |

### 3.2. Baseline Processed Mirrors (2,527 images)

| Split | Location | Image Count | Content Role |
| :--- | :--- | :---: | :--- |
| **Train** | `data/processed/train/` | 1,769 | Frozen 6-class baseline training split |
| **Validation** | `data/processed/val/` | 379 | Frozen 6-class baseline validation split |
| **Test** | `data/processed/test/` | 379 | Frozen 6-class baseline testing split |
| **Subtotal** | **Processed Baseline** | **2,527** | **Exact 1:1 mirror of TrashNet Raw** |

**Grand Total Physical Image Assets Scanned**: $6,836\text{ (Raw)} + 2,527\text{ (Processed)} = \mathbf{9,363\text{ images}}$.

*Full CSV record*: [`artifacts/dataset_audit/extended_dataset_inventory.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/artifacts/dataset_audit/extended_dataset_inventory.csv)

---

## 4. Split Leakage & Duplicate Audit

### 4.1. Downloaded Split Leakage Findings
* **TrashNet Processed Splits** (`data/processed/{train,val,test}`):
  - Train-Val Hash Overlap: **0**
  - Train-Test Hash Overlap: **0**
  - Val-Test Hash Overlap: **0**
  - *Result*: **100% Leakage-Free Verified**.
* **Pre-Partitioned E-Waste Image Dataset** (`EWaste_Image_Dataset/{train,val,test}`):
  - **Train ↔ Val Exact Duplicate Leaks**: **5 exact image hash collisions**
  - **Train ↔ Test Exact Duplicate Leaks**: **2 exact image hash collisions**
  - *Conclusion*: The downloaded E-Waste split contains pre-existing data leakage. When creating the 8-class dataset, the downloaded splits **must not be trusted blindly**; all images must be pooled, deduplicated, and re-split using group-aware partitioning.

### 4.2. Duplicate Analysis (Exact MD5 & Perceptual dHash)
* **Exact MD5 Duplicate Groups**: 2,587 groups across raw vs processed folders (representing identical images mirrored between `data/raw/TrashNet/` and `data/processed/`).
* **Perceptual Near-Duplicates (dHash)**: 96 groups detected across BDWaste and EWaste datasets (representing consecutive video frames or multi-angle bursts of the same object). Group-aware hashing will prevent these bursts from spanning both train and test splits.

*Full CSV record*: [`artifacts/dataset_audit/duplicate_report.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/artifacts/dataset_audit/duplicate_report.csv)

---

## 5. E-Waste Sources Evaluation

We independently evaluated the two available e-waste sources:

1. **`EWaste_Image_Dataset` (Recommended Primary Source)**:
   - **Quality**: High quality, real-world consumer electronics and components.
   - **Total Images**: 3,000 images across 10 categories.
   - **Recommended Sub-Categories for General E-Waste**:
     - `Battery` (300 images) — High-risk hazardous e-waste
     - `Mobile` (300 images) — Small handheld electronics
     - `Mouse` (300 images) — Common peripheral
     - `Keyboard` (300 images) — Standard computer equipment
     - `PCB` (300 images) — Printed circuit boards & internal electronics
   - **Recommendation**: Uniformly sample ~80–100 images from each of the 5 key consumer categories to form a balanced ~450–500 image `e_waste` class.
2. **`CTSoc_EWaste` (Excluded)**:
   - **Contents**: 57 total files (8 sample setup images, 49 object detection bounding box outputs, loss curves, PR curves, and detection visualizations).
   - **Recommendation**: **EXCLUDE completely**. These are post-training model outputs and diagnostic artifacts, not clean raw classification training images.

---

## 6. BDWaste (Organic) Category Evaluation

We evaluated each of the 10 BDWaste folders independently:

| Category Folder | Image Count | Recommended Action | Detailed Justification / Classification Rationale |
| :--- | :---: | :---: | :--- |
| **`1. Sugarcane husk`** | 125 | **INCLUDE** | Fibrous organic agricultural plant residue; 100% compostable. |
| **`2. Fish ash`** | 125 | **EXCLUDE** | Combustion ash is inorganic mineral residue; not compostable organic matter. |
| **`3. Potato Peel`** | 130 | **INCLUDE** | Common household vegetable food scrap; archetypal wet biodegradable waste. |
| **`4. Paper`** | 124 | **EXCLUDE** | Paper is already a dedicated dry recyclable class in TrashNet; inclusion in organic would cause severe inter-class confusion. |
| **`5. Mango Peel`** | 121 | **INCLUDE** | Fruit peel organic food waste; highly representative. |
| **`6. Rice`** | 127 | **INCLUDE** | Leftover cooked/uncooked grain waste; standard food waste. |
| **`7. Shell of Malta`** | 126 | **INCLUDE** | Citrus peel organic waste; excellent texture variety. |
| **`8. Lemon Peel`** | 125 | **INCLUDE** | Citrus fruit peel; compostable organic waste. |
| **`9. Banana peel`** | 123 | **INCLUDE** | Archetypal fruit peel food waste scrap. |
| **`10. Coffee cup`** | 126 | **EXCLUDE** | Single-use disposable coffee cups feature plastic/polyethylene coatings and are non-compostable composite items (belongs in residual/trash). |

*Clean Biodegradable Candidate Pool*: **7 Approved Organic Categories = 877 images**.

---

## 7. Existing TrashNet Verification

Comparison against known Phase 1 baseline:

| Class | Known Phase 1 Baseline | Current Audit Count | Discrepancy | Verification Status |
| :--- | :---: | :---: | :---: | :---: |
| **cardboard** | 403 | 403 | 0 | **VERIFIED (100% Match)** |
| **glass** | 501 | 501 | 0 | **VERIFIED (100% Match)** |
| **metal** | 410 | 410 | 0 | **VERIFIED (100% Match)** |
| **paper** | 594 | 594 | 0 | **VERIFIED (100% Match)** |
| **plastic** | 482 | 482 | 0 | **VERIFIED (100% Match)** |
| **trash** | 137 | 137 | 0 | **VERIFIED (100% Match)** |
| **Total** | **2,527** | **2,527** | **0** | **VERIFIED (100% Match)** |

---

## 8. Proposed 8-Class Dataset Architecture & Target Counts

To maintain a **balanced, laptop-manageable, and high-quality dataset** (avoiding class dominance and GPU/RAM exhaustion), we propose the following target distribution:

| Class Index | Class Name | Category ID Prefix | Source Dataset | Selected Composition | Proposed Target Images |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **0** | `biodegradable` | `TB` | BDWaste (7 Approved Classes) | Banana, Potato, Mango, Lemon, Malta peels, Rice, Husk | **450** |
| **1** | `cardboard` | `TC` | TrashNet Raw | Original TrashNet cardboard images | **403** |
| **2** | `e_waste` | `TE` | EWaste Image Dataset | Battery, Mobile, Mouse, Keyboard, PCB | **450** |
| **3** | `glass` | `TG` | TrashNet Raw | Original TrashNet glass images | **501** |
| **4** | `metal` | `TM` | TrashNet Raw | Original TrashNet metal images | **410** |
| **5** | `paper` | `TP` | TrashNet Raw | Original TrashNet paper images | **594** |
| **6** | `plastic` | `TPL` | TrashNet Raw | Original TrashNet plastic images | **482** |
| **7** | `trash` | `TT` | TrashNet Raw | Original TrashNet residual trash images | **137** |
| **TOTAL** | **8 Classes** | — | — | — | **~3,427 images** |

*Full CSV record*: [`artifacts/dataset_audit/proposed_8class_mapping.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/artifacts/dataset_audit/proposed_8class_mapping.csv)

---

## 9. Leakage-Safe Splitting Strategy (70 / 15 / 15)

When user approval is granted for dataset preparation:
1. **Deduplication First**: Compute MD5 content hashes and remove duplicate copies across raw sources.
2. **Group-Aware Hash Partitioning**: Group near-duplicate burst captures (dHash distance $\le 2$) into discrete entity clusters.
3. **Partitioning**: Allocate entire entity clusters into `train` (70%), `val` (15%), and `test` (15%) splits deterministically using `seed=42`.
4. **Zero-Leakage Assertion**: Run automated cross-split set intersection checks to mathematically prove 0% overlap between train, val, and test splits.

---

## 10. Audit Artifacts & Deliverables

1. [`docs/EXTENDED_DATASET_AUDIT.md`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/docs/EXTENDED_DATASET_AUDIT.md) — Comprehensive audit and decision documentation.
2. [`artifacts/dataset_audit/extended_dataset_inventory.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/artifacts/dataset_audit/extended_dataset_inventory.csv) — Complete inventory table with dimensions and sizes.
3. [`artifacts/dataset_audit/duplicate_report.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/artifacts/dataset_audit/duplicate_report.csv) — Exact MD5 and perceptual dHash duplicate collision logs.
4. [`artifacts/dataset_audit/proposed_8class_mapping.csv`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/artifacts/dataset_audit/proposed_8class_mapping.csv) — Category mapping rules and justifications.
5. [`scripts/audit_extended_datasets.py`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/scripts/audit_extended_datasets.py) — Reproducible non-destructive audit script.
