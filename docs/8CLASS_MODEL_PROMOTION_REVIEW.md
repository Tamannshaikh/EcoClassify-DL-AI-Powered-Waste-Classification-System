# EcoClassify DL — Phase 13: 8-Class Model Review & Promotion Readiness Audit

**Document Status**: Official Promotion Readiness Audit  
**Project**: EcoClassify DL — AI-Powered Waste Classification System  
**Baseline Status**: Production 6-Class Model Frozen (`v1.0.0-baseline`, commit `9a3dff3`)  
**Audit Date**: 2026-10-04  
**Promotion Review Verdict**: **READY FOR PROMOTION REVIEW** (No production changes performed)  

---

## 1. Executive Summary

This audit performs an independent, read-only verification of the experimental 8-class MobileNetV2 candidate model trained during Phase 12. Every artifact, training epoch, test prediction, metric calculation, confusion matrix entry, Grad-CAM visualization, CPU benchmark, and model reload assertion was independently verified against disk artifacts and raw predictions.

The production 6-class baseline remains strictly frozen and verified intact.

---

## 2. Production Baseline Integrity

* **Baseline Git Tag**: `v1.0.0-baseline`
* **Baseline Commit**: `9a3dff3`
* **Production Model Path**: `artifacts/final/waste_classifier.keras`
* **Expected SHA-256**: `41417f46364227d8556b225359c3f9be58d94983a177930e92fdf35ef4526911`
* **Actual SHA-256**: `41417f46364227d8556b225359c3f9be58d94983a177930e92fdf35ef4526911`
* **Integrity Status**: **PASS** (Zero modifications, 100% byte-for-byte identical).

---

## 3. Experimental Candidate Specification

* **Candidate Model Path**: `artifacts/experiments/8class_mobilenetv2/model/waste_classifier_8class.keras`
* **Dataset Version**: `8class-v1.0` (Total 3,427 images; Train: 2,399, Val: 515, Test: 513)
* **Target Classes (0–7)**: `biodegradable`, `cardboard`, `e_waste`, `glass`, `metal`, `paper`, `plastic`, `trash`
* **Architecture**: MobileNetV2 (ImageNet weights, input 224x224x3) $\rightarrow$ GAP $\rightarrow$ Dense(128, ReLU) $\rightarrow$ Dropout(0.30) $\rightarrow$ Dense(8, Softmax)
* **Total Parameters**: 2,422,984

---

## 4. Artifact Existence & Integrity Verification

| Artifact Name | Location | Size | Status |
| :--- | :--- | :---: | :---: |
| **Model Weights** | `artifacts/experiments/8class_mobilenetv2/model/waste_classifier_8class.keras` | 23.86 MB | **PASS** |
| **Class Names Mapping** | `artifacts/experiments/8class_mobilenetv2/model/class_names_8class.json` | 115 B | **PASS** |
| **Model Metadata** | `artifacts/experiments/8class_mobilenetv2/model/model_metadata_8class.json` | 619 B | **PASS** |
| **Training History** | `artifacts/experiments/8class_mobilenetv2/model/training_history_8class.json` | 2.61 KB | **PASS** |
| **Training Summary Report** | `artifacts/experiments/8class_mobilenetv2/reports/training_summary.json` | 4.10 KB | **PASS** |
| **Test Predictions CSV** | `artifacts/experiments/8class_mobilenetv2/reports/test_predictions.csv` | 31.17 KB | **PASS** |
| **Per-Class Analysis** | `artifacts/experiments/8class_mobilenetv2/reports/per_class_analysis.md` | 3.19 KB | **PASS** |
| **Confusion Matrix Figure** | `artifacts/experiments/8class_mobilenetv2/figures/confusion_matrix.png` | 405 KB | **PASS** |
| **Training Curves Figure** | `artifacts/experiments/8class_mobilenetv2/figures/training_curves.png` | 274 KB | **PASS** |
| **Grad-CAM Visualizations** | `artifacts/experiments/8class_mobilenetv2/figures/gradcam/` (10 PNGs) | ~2.3 MB | **PASS** |
| **Experiment Config** | `artifacts/experiments/8class_mobilenetv2/metadata/experiment_config.json` | 1.12 KB | **PASS** |

---

## 5. Training History & Discrepancy Resolution

### 5.1. History Trajectory
* **Stage 1 (Head Training)**: 18 epochs executed.
  * Starting: Epoch 1 (`loss = 1.0698`, `val_loss = 0.4990`, `val_acc = 83.11%`).
  * Best Validation Loss: **Epoch 13** (`loss = 0.1743`, `val_loss = 0.325262`, `val_acc = 89.7087%`).
  * Stage 1 Final Epoch: Epoch 18 (`val_loss = 0.327624`, `val_acc = 90.0971%`).
* **Stage 2 (Top 30 Layers Fine-Tuning)**: 6 epochs executed.
  * Epoch 1: `val_loss = 0.328921`, `val_acc = 90.0971%`.
  * Epochs 2–6: `val_loss` increased to `0.3421`, triggering early stopping.

### 5.2. Discrepancy Resolution
* **Audit Finding**: Early stopping and model checkpointing strictly monitored `val_loss` with `restore_best_weights=True`.
* **Resolution**: Epoch 13 achieved the lowest validation loss (`0.3253`) across the entire training run with `89.71%` validation accuracy. Later epochs (Epochs 16–18 and Stage 2 Epoch 1) achieved slightly higher validation accuracy (`90.10%` to `90.29%`), but had higher validation loss (`0.3271` to `0.3289`). The checkpointing logic correctly restored the weights from **Epoch 13**.

---

## 6. Independent Test Metric Recomputation

All 513 test sample predictions in `test_predictions.csv` were independently evaluated using scikit-learn:

| Metric | Reported Value | Independently Recomputed | Difference | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Overall Accuracy** | 89.0838% | **89.0838%** | 0.0000% | **PASS** |
| **Macro Precision** | 0.874363 | **0.874363** | 0.000000 | **PASS** |
| **Macro Recall** | 0.885091 | **0.885091** | 0.000000 | **PASS** |
| **Macro F1-Score** | 0.878117 | **0.878117** | 0.000000 | **PASS** |
| **Weighted Precision** | 0.895788 | **0.895788** | 0.000000 | **PASS** |
| **Weighted Recall** | 0.890838 | **0.890838** | 0.000000 | **PASS** |
| **Weighted F1-Score** | 0.892002 | **0.892002** | 0.000000 | **PASS** |

---

## 7. Per-Class Metrics Breakdown

| Index | Class Name | Precision | Recall | F1-Score | Support | Status Rating |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `0` | **`biodegradable`** | 1.0000 | 1.0000 | 1.0000 | 67 | Strong / Perfect |
| `1` | **`cardboard`** | 0.9180 | 0.9180 | 0.9180 | 61 | Strong |
| `2` | **`e_waste`** | 1.0000 | 0.9851 | 0.9925 | 67 | Strong / Excellent |
| `3` | **`glass`** | 0.7976 | 0.8933 | 0.8428 | 75 | Robust |
| `4` | **`metal`** | 0.7937 | 0.8197 | 0.8065 | 61 | Robust |
| `5` | **`paper`** | 0.9494 | 0.8427 | 0.8929 | 89 | Strong |
| `6` | **`plastic`** | 0.8696 | 0.8219 | 0.8451 | 73 | Robust |
| `7` | **`trash`** | 0.6667 | 0.8000 | 0.7273 | 20 | Warning / Limited Support |

---

## 8. Confusion Matrix Verification

Independent matrix verification from `test_predictions.csv`:

* **Dimensions**: 8 $\times$ 8
* **Row Sums (Ground Truth Support)**: `[67, 61, 67, 75, 61, 89, 73, 20]` $\rightarrow$ Sum = 513 (**Verified**)
* **Column Sums (Model Predictions)**: `[67, 61, 66, 84, 63, 79, 69, 24]` $\rightarrow$ Sum = 513 (**Verified**)

### Recomputed Confusion Matrix:
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

### Verified Error Patterns:
1. `Metal` $\rightarrow$ `Glass`: 8 samples
2. `Plastic` $\rightarrow$ `Glass`: 9 samples
3. `Glass` $\rightarrow$ `Plastic`: 5 samples
4. `Paper` $\rightarrow$ `Cardboard`: 5 samples
5. `Trash` $\rightarrow$ `Metal`: 3 samples
6. `Trash` $\rightarrow$ `Paper`: 1 sample

---

## 9. Dataset & Test Set Integrity

* **Total Test Samples**: 513 images
* **Split Contamination**: 0 samples from train or val appear in test
* **Hash Collisions**: 0 exact MD5 duplicate matches across splits
* **Perceptual Similarity**: 0 near-duplicate matches across splits

---

## 10. Domain & Source Considerations

* **`biodegradable` (BDWaste)**: 100% of test samples (67/67) originate from BDWaste categories (e.g. Sugarcane husk, Lemon peel, Potato peel). The perfect metric (F1 = 1.0000) reflects strong distinct biological features, but constitutes a **source-domain limitation** regarding how well it generalizes to complex, mixed-background household waste.
* **`e_waste` (EWaste Image Dataset)**: 100% of test samples (67/67) originate from PCB, battery, and peripheral categories. High F1 (0.9925) is supported by distinct geometric features.
* **Original 6 Classes (TrashNet)**: All 379 samples retain full TrashNet lineage without cross-contamination.

---

## 11. Grad-CAM Review

* **Target Convolutional Layer**: `mobilenetv2_1.00_224::out_relu`
* **Artifacts Inspected**:
  * `gradcam_biodegradable_TB0384.png` / `TB0385.png`: Clear focus on organic textures.
  * `gradcam_e_waste_TE0384.png` / `TE0385.png`: High salience on solder points and integrated circuits.
  * `gradcam_cardboard_TC0343.png` / `TC0344.png`: Activations on planar cardboard box surfaces.
  * `gradcam_plastic_TPL0410.png` / `TPL0411.png`: Activations on bottle bodies and polymer reflections.
  * `gradcam_trash_TT0118.png` / `TT0119.png`: Salience across composite residual items.
* **Verdict**: **PASS** (Semantically plausible activation fields).

---

## 12. CPU Latency Benchmark Verification

* **Benchmark Protocol**: 10 warm-up runs, 100 timed single-image predictions on CPU (AMD64, batch size = 1).
* **Candidate Measured Latency**:
  * Average Latency: **88.65 ms**
  * Median Latency: **87.27 ms**
  * P95 Latency: **98.29 ms**
  * Min / Max: **79.75 ms / 109.00 ms**
* **Comparison with 6-Class Baseline (61.15 ms average)**:
  * Latency Delta: $+27.50\text{ ms}$
  * Percentage Increase: **$+44.97\%$**
* **Assessment**: The latency increase is within acceptable limits for single-image web inference (<100 ms average), but should be documented as an operational trade-off.

---

## 13. Model Reload Verification

* **Loaded File**: `artifacts/experiments/8class_mobilenetv2/model/waste_classifier_8class.keras`
* **Input Shape**: `(None, 224, 224, 3)`
* **Output Shape**: `(None, 8)`
* **Parameter Count**: `2,422,984`
* **Integrity Invariants**:
  * Output shape for single sample: `(1, 8)`
  * Finite probabilities: `True`
  * Non-negative probabilities: `True`
  * Probability sum: `1.0` ($\pm 10^{-6}$)
* **Reload Status**: **PASS**

---

## 14. 6-Class Baseline vs 8-Class Candidate Comparison

> [!IMPORTANT]
> Because label spaces differ (6 classes vs 8 classes), raw metrics are not a strict apples-to-apples comparison.

| Metric | 6-Class Baseline (`v1.0.0`) | 8-Class Candidate | Comparison / Note |
| :--- | :---: | :---: | :--- |
| **Classes Supported** | 6 | **8** | Adds `biodegradable` & `e_waste` |
| **Total Dataset Size** | 2,527 | **3,427** | +35.6% dataset expansion |
| **Test Set Support** | 379 | **513** | +134 test samples |
| **Accuracy** | 87.07% | **89.08%** | +2.01% |
| **Macro F1-Score** | 85.14% | **87.81%** | +2.67% |
| **Weighted F1-Score** | 87.00% | **89.20%** | +2.20% |
| **CPU Average Latency** | **61.15 ms** | 88.65 ms | +44.97% latency increase |
| **Parameter Count** | **2,422,726** | 2,422,984 | +258 parameters (Head expansion) |
| **New Classes F1** | N/A | **`bio`: 1.0000, `e_waste`: 0.9925** | High practical utility |

---

## 15. Strengths & Opportunities

1. **Broadened Ecological Scope**: Covers vital municipal waste categories (`biodegradable` and `e_waste`), significantly expanding sorting utility.
2. **Superior Classification Power**: Achieves **89.08% accuracy** and **87.81% macro F1** across 8 classes.
3. **Preserved Clean Architecture**: Maintains MobileNetV2 architecture with identical input dimensions and efficient parameter footprint (2.42M parameters).

---

## 16. Limitations & Warnings

1. **`trash` Class Performance (WARN)**: Precision is 66.67% (F1 = 0.7273) due to small class support (20 test samples).
2. **CPU Inference Latency (WARN)**: Latency increased from 61.15 ms to 88.65 ms (+44.97%), though still under 100 ms.
3. **Source-Domain Variance (NOTE)**: `biodegradable` images from BDWaste may show slight distribution shift when deployed on non-studio backgrounds.

---

## 17. Promotion Readiness Criteria Scorecard

| Criterion | Evaluation Dimension | Status | Notes |
| :---: | :--- | :---: | :--- |
| **A** | Dataset integrity & zero corruption | **PASS** | 3,427 clean images verified |
| **B** | Cross-split test leakage | **PASS** | 0 exact, 0 near-duplicate cross-split leaks |
| **C** | Test metric reproducibility | **PASS** | 100% exact numerical match |
| **D** | Per-class performance stability | **PASS** | 7/8 classes achieve F1 $\ge 0.80$ |
| **E** | Trash class performance | **WARN** | F1 = 0.7273 due to 137 total support |
| **F** | New-class performance | **PASS** | `bio` F1 = 1.0000, `e_waste` F1 = 0.9925 |
| **G** | Confusion matrix verification | **PASS** | 8x8 verified, row sums match support |
| **H** | Grad-CAM compatibility | **PASS** | Target layer verified |
| **I** | CPU inference latency | **WARN** | 88.65 ms average (+44.97% over baseline) |
| **J** | Model reload integrity | **PASS** | Verified shape (1, 8), sum = 1.0 |
| **K** | Backend API regression | **PASS** | 17/17 pytest tests passed |
| **L** | E2E integration regression | **PASS** | 7/7 audit sectors passed |
| **M** | Production compatibility | **PASS** | Standard Keras format & architecture |

---

## 18. Final Recommendation

### Promotion Status: **READY FOR PROMOTION REVIEW**

The 8-class MobileNetV2 candidate model is **recommended for formal promotion review**. All artifacts, logs, evaluation scripts, and verification metrics have been fully audited and are reproducible.

*Production Promotion Action*: **NOT PERFORMED**.  
*Production Baseline Status*: **FROZEN & PROTECTED**.
