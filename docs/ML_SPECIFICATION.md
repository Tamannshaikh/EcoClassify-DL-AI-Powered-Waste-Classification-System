# Machine Learning Specification

## 1. Objective
Classify waste images into six standard recyclable categories:
- `cardboard`
- `glass`
- `metal`
- `paper`
- `plastic`
- `trash` (residual / non-recyclable)

---

## 2. Dataset
- **Dataset**: TrashNet (Gary Thung & Mindy Yang, Stanford University)
- **Total Images**: 2,527 images
- **Image Format**: JPEG, 512×384 uniform RGB
- **Integrity**: 100% verified (0 corrupted images)
- **Duplicate Isolation**: 3 cross-class SHA-256 duplicate pairs (`glass115/metal91`, `glass176/plastic152`, `glass389/plastic332`) isolated strictly within the training set to prevent evaluation leakage.

---

## 3. Data Partitioning (70 / 15 / 15 Stratified Split)
- **Train Set**: 1,769 images (70%)
- **Validation Set**: 379 images (15%)
- **Test Set**: 379 images (15%)

---

## 4. Preprocessing & Normalization
- **Resolution**: Resized to 224×224 RGB via Bilinear Interpolation.
- **Normalization**: Pixel scaling to $[-1, 1]$ via `tf.keras.applications.mobilenet_v2.preprocess_input` embedded within the model pipeline.
- **Inference**: Deterministic evaluation without test-time augmentation.

---

## 5. Model Architectures & Empirical Comparison

### Model A: Custom CNN (Baseline)
- **Structure**: 4 convolutional blocks (32 &rarr; 64 &rarr; 128 &rarr; 256 filters) with Batch Normalization, MaxPooling2D, Dropout, Dense (256 units), Softmax.
- **Parameters**: 259,526
- **Test Accuracy**: **68.60%**
- **Macro Precision**: 68.00%
- **Macro Recall**: 69.23%
- **Macro F1-Score**: **65.61%**
- **Weighted F1-Score**: 68.94%
- **Training Duration**: ~25.91 min
- **Inference Latency**: ~42.1 ms

### Model B: MobileNetV2 (Selected Final Production Model)
- **Structure**: ImageNet pre-trained MobileNetV2 inverted residual backbone + GlobalAveragePooling2D + Dropout (0.3 & 0.2) + Dense (128 units) + Dense (6, Softmax).
- **Parameters**: 2,422,726
- **Test Accuracy**: **87.07%** *(+18.47 percentage points vs. Baseline)*
- **Macro Precision**: **86.23%** *(+18.23 percentage points vs. Baseline)*
- **Macro Recall**: **84.44%** *(+15.21 percentage points vs. Baseline)*
- **Macro F1-Score**: **85.14%** *(+19.53 percentage points vs. Baseline)*
- **Weighted F1-Score**: **87.00%** *(+18.06 percentage points vs. Baseline)*
- **Training Duration**: ~8.36 min *(~3.1× shorter measured training time)*
- **Inference Latency**: ~61.15 ms CPU average

---

## 6. Training Configuration & Hyperparameters
- **Loss**: Categorical Crossentropy
- **Optimizer**: Adam (Initial $lr=10^{-3}$, fine-tuning $lr=10^{-4}$)
- **Batch Size**: 32
- **Callbacks**:
  - `EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)`
  - `ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6)`
  - `ModelCheckpoint(filepath=..., save_best_only=True)`

---

## 7. Explainability (Grad-CAM)
- **Target Layer**: `mobilenetv2_1.00_224` &rarr; `out_relu` (Final 7×7 convolutional feature maps).
- **Technique**: Channel-wise gradient pooling via `tf.GradientTape` for predicted class logit, normalized ReLU heatmap, and Jet colormap overlay.

---

## 8. Exported Model Artifacts
Stored under `artifacts/final/`:
- `waste_classifier.keras` (23.8 MB trained binary)
- `class_names.json`
- `model_metadata.json`
- `metrics.json`
