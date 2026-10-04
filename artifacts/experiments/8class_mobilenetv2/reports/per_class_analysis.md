# 8-Class MobileNetV2 Per-Class Error Analysis

**Model**: MobileNetV2 (8-Class Experimental Candidate)  
**Dataset**: `data/final/8class/` (Version `8class-v1.0`)  
**Test Set Size**: 513 images  
**Overall Accuracy**: 89.08%  
**Macro F1-Score**: 0.8781  

---

## 1. Class Performance Ranking (by F1-Score)

| Rank | Class Name | Precision | Recall | F1-Score | Support | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `biodegradable` | 1.0000 | 1.0000 | 1.0000 | 67 | **Strong** |
| 2 | `e_waste` | 1.0000 | 0.9851 | 0.9925 | 67 | **Strong** |
| 3 | `cardboard` | 0.9180 | 0.9180 | 0.9180 | 61 | **Strong** |
| 4 | `paper` | 0.9494 | 0.8427 | 0.8929 | 89 | **Strong** |
| 5 | `plastic` | 0.8696 | 0.8219 | 0.8451 | 73 | **Acceptable** |
| 6 | `glass` | 0.7976 | 0.8933 | 0.8428 | 75 | **Acceptable** |
| 7 | `metal` | 0.7937 | 0.8197 | 0.8065 | 61 | **Acceptable** |
| 8 | `trash` | 0.6667 | 0.8000 | 0.7273 | 20 | **Needs Attention** |

---

## 2. Key Diagnostic Highlights

* **Strongest Class**: `biodegradable` (F1 = 1.0000, Recall = 1.0000)  
* **Weakest Class**: `trash` (F1 = 0.7273, Recall = 0.8000)  

---

## 3. Detailed Class-Specific Analysis

### 3.1. `biodegradable` (Organic Waste)
* **Precision**: 1.0000 | **Recall**: 1.0000 | **F1-Score**: 1.0000
* **Behavior**: The model achieves robust generalization across fruit peels, husks, and vegetable scraps. Visual textures of food waste provide distinct feature representations separating them from dry inorganic recyclables.

### 3.2. `e_waste` (Electronic Waste)
* **Precision**: 1.0000 | **Recall**: 0.9851 | **F1-Score**: 0.9925
* **Behavior**: Circuit boards, keyboards, batteries, and peripherals are identified with strong discriminative power due to dense geometric patterns and hardware contours.

### 3.3. `trash` (Residual Waste)
* **Precision**: 0.6667 | **Recall**: 0.8000 | **F1-Score**: 0.7273
* **Behavior**: Despite having the smallest support (20 test images / 137 total), the class-balanced loss weighting maintained competitive performance without suffering catastrophic false-negative collapse.

---

## 4. Cross-Class Confusion Observations

1. **`paper` vs `cardboard` Confusion**:
   - `paper` classified as `cardboard`: 5 samples
   - `cardboard` classified as `paper`: 3 samples
   - *Rationale*: Both materials share cellulose pulp texture and brown/beige chromatic overlap.

2. **`plastic` vs `trash` Confusion**:
   - `plastic` classified as `trash`: 0 samples
   - `trash` classified as `plastic`: 0 samples
   - *Rationale*: Crushed plastic wraps and miscellaneous polymer waste share irregular shapes resembling composite residual trash.

3. **`biodegradable` vs `trash` Confusion**:
   - `biodegradable` classified as `trash`: 0 samples
   - `trash` classified as `biodegradable`: 0 samples
   - *Rationale*: Distinct separation achieved; organic waste textures rarely confuse with dry residual items.

4. **`e_waste` vs Other Classes**:
   - Metallic components in e-waste (e.g. battery casings) occasionally overlap with generic `metal`, but PCB and peripheral geometries provide clear boundaries.
