# Final Experimental Results & Evaluation Summary

**Project Title**: AI-Powered Waste Classification System using Deep Learning  
**Dataset**: TrashNet (*2,527 images across 6 classes*)  
**Evaluation Date**: Verified across Phases 1–7

---

## 1. Dataset Partition Summary

| Partition | Image Count | Percentage | Integrity Status |
| :--- | :---: | :---: | :---: |
| **Training Set** | 1,769 | 70.0% | 100% verified (contains duplicate isolation groups) |
| **Validation Set** | 379 | 15.0% | 100% verified (leak-free) |
| **Test Set** | 379 | 15.0% | 100% verified (leak-free) |
| **Total** | **2,527** | **100.0%** | **0 corrupted images** |

---

## 2. Quantitative Model Comparison

| Evaluation Metric | Custom CNN Baseline | MobileNetV2 Transfer Learning | Empirical Performance Delta |
| :--- | :---: | :---: | :---: |
| **Model Parameters** | 259,526 | 2,422,726 | 9.3× parameter capacity |
| **Test Accuracy** | **68.60%** | **87.07%** | **+18.47 percentage points** |
| **Macro Precision** | **68.00%** | **86.23%** | **+18.23 percentage points** |
| **Macro Recall** | **69.23%** | **84.44%** | **+15.21 percentage points** |
| **Macro F1-Score** | **65.61%** | **85.14%** | **+19.53 percentage points** |
| **Weighted F1-Score** | **68.94%** | **87.00%** | **+18.06 percentage points** |
| **CPU Training Duration** | ~25.91 min | ~8.36 min | **~3.1× shorter measured training time** |
| **Avg CPU Inference Latency** | ~42.1 ms | ~61.15 ms | Both sub-100ms real-time capable |

---

## 3. MobileNetV2 Per-Class Evaluation Breakdown

Evaluated on 379 held-out test samples:

| Class Name | Test Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Cardboard** | 61 | 88.52% | 88.52% | **88.52%** |
| **Glass** | 75 | 88.73% | 84.00% | **86.30%** |
| **Metal** | 61 | 84.62% | 90.16% | **87.30%** |
| **Paper** | 89 | 90.91% | 89.89% | **90.40%** |
| **Plastic** | 73 | 83.33% | 89.04% | **86.09%** |
| **Trash** | 20 | 81.25% | 65.00% | **72.22%** |
| **Macro Average** | **379** | **86.23%** | **84.44%** | **85.14%** |
| **Weighted Average**| **379** | **87.34%** | **87.07%** | **87.00%** |

---

## 4. Quality Assurance & System Verification Results

- **Backend Pytest Test Suite**: **16 / 16 Passed (100%)**
- **Full E2E System Integration Audit**: **7 / 7 Sectors Passed (100%)**
- **Frontend TypeScript / Vite Build**: **0 errors, 0 warnings**
- **Database CRUD & Lifecycle**: **100% verified**
- **Grad-CAM Generation**: **100% operational on `out_relu` convolutional layer**
