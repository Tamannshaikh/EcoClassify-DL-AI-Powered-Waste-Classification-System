# Model Performance Comparison Report

## Summary Table

| Metric | Custom CNN Baseline | MobileNetV2 (Transfer Learning) | Winner |
| :--- | :---: | :---: | :---: |
| **Test Accuracy** | 68.60% | 87.07% | **MobileNetV2** |
| **Macro Precision** | 68.00% | 86.23% | **MobileNetV2** |
| **Macro Recall** | 69.23% | 84.44% | **MobileNetV2** |
| **Macro F1-Score** | 65.61% | 85.14% | **MobileNetV2** |
| **Weighted F1-Score** | 68.94% | 87.00% | **MobileNetV2** |

---

## Per-Class Breakdown (Test Set)

### Custom CNN Baseline:
| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **cardboard** | 85.25% | 85.25% | 85.25% | 61 |
| **glass** | 72.50% | 38.67% | 50.43% | 75 |
| **metal** | 76.92% | 65.57% | 70.80% | 61 |
| **paper** | 71.96% | 86.52% | 78.57% | 89 |
| **plastic** | 74.60% | 64.38% | 69.12% | 73 |
| **trash** | 26.79% | 75.00% | 39.47% | 20 |

### MobileNetV2 (Transfer Learning):
| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **cardboard** | 88.52% | 88.52% | 88.52% | 61 |
| **glass** | 88.73% | 84.00% | 86.30% | 75 |
| **metal** | 84.62% | 90.16% | 87.30% | 61 |
| **paper** | 90.91% | 89.89% | 90.40% | 89 |
| **plastic** | 83.33% | 89.04% | 86.09% | 73 |
| **trash** | 81.25% | 65.00% | 72.22% | 20 |

---

## Dataset Ambiguity Note
The TrashNet dataset contains 3 pairs of identical byte-duplicate images labelled under different classes (glass ↔ metal, glass ↔ plastic). These pairs were co-located strictly in the training partition, guaranteeing clean, uncontaminated test and validation evaluation sets.
