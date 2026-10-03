# Final Project Report Content

**Title**: AI-Powered Waste Classification System using Deep Learning and Convolutional Neural Networks  
**Domain**: Computer Vision, Deep Learning, Environmental Informatics  
**Application Branding**: EcoClassify DL  

---

## 1. Abstract
Urban municipal solid waste management faces severe sorting inefficiencies and recycling stream contamination. This project presents **EcoClassify DL**, an autonomous, local-first Deep Learning vision system capable of categorizing waste items into six standard TrashNet categories (*Cardboard, Glass, Metal, Paper, Plastic, Trash*). We developed and compared two convolutional neural network architectures: a baseline Custom CNN trained from scratch (259,526 parameters) and a transfer learning architecture utilizing a pre-trained MobileNetV2 backbone (2,422,726 parameters). The MobileNetV2 model achieved **87.07% test accuracy** and **85.14% Macro F1-score**, outperforming the baseline by **+18.47 percentage points**. To provide model interpretability, Gradient-weighted Class Activation Mapping (Grad-CAM) was integrated to visualize the spatial regions influencing classification. The model is served via an asynchronous FastAPI backend paired with a local SQLite audit database and an interactive React + TypeScript frontend.

---

## 2. Introduction
Rapid urbanization and consumer consumption generate billions of tons of solid waste annually. Traditional sorting relies heavily on manual labor, leading to high operational costs, health hazards, and high contamination rates that render recyclable batches unusable. Automated image-based waste classification utilizing Deep Learning provides an effective solution to automate sorting at disposal bins and recycling recovery facilities.

---

## 3. Problem Statement
Manual waste segregation is error-prone due to visual similarities between different materials (e.g., clear plastic vs. glass, laminated paper vs. cardboard). Standard machine learning approaches with hand-crafted features struggle with texture variations, lighting fluctuations, and object deformation. A robust Deep Learning vision pipeline is required to extract invariant spatial representations, provide high classification confidence, explain predictions visually, and run with sub-100ms inference latency on standard consumer hardware.

---

## 4. Project Objectives
1. Validate and preprocess the benchmark **TrashNet** dataset without data leakage.
2. Establish a Custom CNN baseline architecture trained from scratch.
3. Construct a transfer learning pipeline utilizing MobileNetV2 with ImageNet weights and top-layer fine-tuning.
4. Integrate Gradient-weighted Class Activation Mapping (Grad-CAM) for visual explainability.
5. Deploy a high-performance, asynchronous REST API using FastAPI.
6. Implement persistent SQLite prediction audit logging.
7. Build a responsive, user-friendly React + TypeScript dashboard.
8. Perform rigorous end-to-end integration and security testing.

---

## 5. Literature Review & Theoretical Background
Early waste classification literature explored feature descriptors like SIFT, HOG, and color histograms combined with Support Vector Machines (SVMs). The landmark TrashNet benchmark by Gary Thung and Mindy Yang (Stanford University, 2016) demonstrated that Convolutional Neural Networks significantly outperform shallow classifiers on raw waste imagery. Modern transfer learning architectures like MobileNetV2 introduce inverted residual blocks and linear bottlenecks, dramatically reducing memory bandwidth and computational FLOPs while retaining deep feature representations suitable for embedded and edge applications.

---

## 6. Dataset Analysis & Inventory
The project utilizes the Stanford **TrashNet** dataset containing **2,527** RGB images:
- `cardboard`: 403 images (15.95%)
- `glass`: 501 images (19.83%)
- `metal`: 410 images (16.22%)
- `paper`: 594 images (23.51%)
- `plastic`: 482 images (19.07%)
- `trash`: 137 images (5.42%)

All images possess uniform 512×384 dimensions with zero corrupted files.

---

## 7. Methodology
The development workflow followed a rigorous phased lifecycle:
1. **Dataset Audit**: Validation of image channels, headers, and SHA-256 duplicate detection.
2. **Stratified Splitting**: 70% Train, 15% Validation, 15% Test with group-aware duplicate isolation.
3. **Data Augmentation**: Realistic geometric perturbations applied during training only.
4. **Baseline Modeling**: Custom CNN architecture training.
5. **Transfer Learning**: MobileNetV2 feature extraction and fine-tuning.
6. **Quantitative Evaluation**: Multi-class confusion matrix, precision, recall, and Macro F1.
7. **Explainability**: Grad-CAM implementation targeting the `out_relu` convolutional layer.
8. **Deployment**: FastAPI backend, SQLite database, and React UI.

---

## 8. Data Preprocessing & Leakage Prevention
During the Phase 2 dataset audit, 3 exact cross-class byte duplicate pairs were identified (e.g., `glass115.jpg` and `metal91.jpg` possessing identical SHA-256 hashes). To eliminate data leakage and evaluation contamination, a **group-aware stratified splitting algorithm** was designed, ensuring duplicate groups were placed strictly within the training set. Input images are resized to 224×224 bilinear and normalized to the $[-1, 1]$ interval.

---

## 9. Custom CNN Baseline Architecture
The baseline model consists of 4 convolutional blocks:
- **Block 1**: Conv2D (32 filters, 3×3) + BatchNorm + ReLU + MaxPooling2D (2×2) + Dropout (0.25)
- **Block 2**: Conv2D (64 filters, 3×3) + BatchNorm + ReLU + MaxPooling2D (2×2) + Dropout (0.25)
- **Block 3**: Conv2D (128 filters, 3×3) + BatchNorm + ReLU + MaxPooling2D (2×2) + Dropout (0.25)
- **Block 4**: Conv2D (256 filters, 3×3) + BatchNorm + ReLU + MaxPooling2D (2×2) + Dropout (0.25)
- **Classification Head**: GlobalAveragePooling2D + Dense (256, ReLU) + Dropout (0.5) + Dense (6, Softmax)
- **Total Parameters**: 259,526 trainable parameters.

---

## 10. MobileNetV2 Architecture & Inverted Residuals
MobileNetV2 utilizes depthwise separable convolutions combined with inverted residual blocks. Each block expands the input channel depth via a 1×1 convolution, applies a 3×3 depthwise convolution with ReLU6, and projects back with a linear 1×1 bottleneck. Shortcut residual connections connect bottlenecks where input and output dimensions match, facilitating gradient flow and preventing gradient degradation during training.

---

## 11. Transfer Learning & Fine-Tuning Strategy
1. **Feature Extraction Phase**: The MobileNetV2 backbone is initialized with pre-trained ImageNet weights with backbone layers frozen ($trainable=False$). A custom dense classification head (GlobalAveragePooling2D + Dropout(0.3) + Dense(128, ReLU) + Dropout(0.2) + Dense(6, Softmax)) is trained for 15 epochs with learning rate $\alpha = 10^{-3}$.
2. **Fine-Tuning Phase**: The top 30 layers of the MobileNetV2 backbone are unfrozen and trained jointly with the head using a reduced learning rate $\alpha = 10^{-4}$ for 15 additional epochs with Early Stopping and ReduceLROnPlateau callbacks.

---

## 12. Model Evaluation & Performance Metrics
Evaluated on the 379 held-out test images:
- **Test Accuracy**: **87.07%** (330 / 379 correct)
- **Macro Precision**: **86.23%**
- **Macro Recall**: **84.44%**
- **Macro F1-Score**: **85.14%**
- **Weighted F1-Score**: **87.00%**
- **Inference Latency**: ~61.15 ms average per image on CPU.

---

## 13. Confusion Matrix Analysis
The 6×6 test confusion matrix reveals strong diagonal concentration:
- `cardboard`: 54/61 correct (88.52% recall)
- `glass`: 63/75 correct (84.00% recall)
- `metal`: 55/61 correct (90.16% recall)
- `paper`: 80/89 correct (89.89% recall)
- `plastic`: 65/73 correct (89.04% recall)
- `trash`: 13/20 correct (65.00% recall)

Minor confusions occur between transparent plastic bottles and glass containers due to specular reflections, and between paper and thin cardboard due to shared cellulose textures.

---

## 14. Explainable AI: Grad-CAM Implementation
Gradient-weighted Class Activation Mapping computes gradients of the target class score $y^c$ with respect to feature map activations $A^k$ of the final convolutional layer (`out_relu`):
$$\alpha_k^c = \frac{1}{Z} \sum_i \sum_j \frac{\partial y^c}{\partial A_{i,j}^k}$$
$$L_{\text{Grad-CAM}}^c = \text{ReLU}\left( \sum_k \alpha_k^c A^k \right)$$
The resulting coarse 2D heatmap is normalized, bilinearly interpolated to the original image dimensions, and overlaid using the Matplotlib Jet colormap to highlight salient discriminatory regions.

---

## 15. Backend REST API Architecture (FastAPI)
The backend service (`backend/app/main.py`) provides asynchronous REST endpoints:
- `GET /api/v1/health`: Server and model lifecycle status.
- `GET /api/v1/model/info`: Architecture parameters, test accuracy, and CPU benchmarks.
- `GET /api/v1/model/metrics`: Confusion matrix and per-class metrics.
- `GET /api/v1/dataset/info`: Total image counts, split allocations, and class breakdown.
- `POST /api/v1/predict`: Single image classification with 6-class probability distribution.
- `POST /api/v1/predict/gradcam`: Inference + Base64 encoded Grad-CAM overlay.
- `GET /api/v1/predictions`: Paginated SQLite audit log.
- `DELETE /api/v1/predictions/{id}`: Single prediction record deletion.

---

## 16. Frontend Single-Page Application (React + TypeScript)
Built with React 19, Vite, TypeScript, and Tailwind CSS v4, the dashboard comprises 8 distinct views:
- **Dashboard**: System KPIs, class distribution charts, recent predictions.
- **Image Prediction**: Drag & drop upload, probability distribution, Grad-CAM toggle, disposal advice.
- **Prediction History**: Paginated audit table with probability detail modal and deletion.
- **Dataset Inventory**: Recharts visualizations of split ratios and class composition.
- **Model Performance**: Confusion matrix heatmap, per-class bar charts, latency metrics.
- **Training Lab**: Comparative metrics matrix between CNN and MobileNetV2.
- **About**: Architectural diagrams, tech stack, and Stanford citations.
- **Settings**: Live backend connection ping and security diagnostics.

---

## 17. Database Design & Persistence (SQLite)
Predictions are persisted to `data/waste_classification.db` in the `predictions` table, tracking unique UUIDs, original filenames, predicted classes, confidence scores, full 6-class probability JSON strings, inference latencies, and creation timestamps.

---

## 18. Security Controls & Error Handling
1. **Client & Server Upload Bounds**: 10MB maximum file size limit.
2. **MIME & Extension Whitelisting**: Restricted strictly to `.jpg`, `.jpeg`, `.png`.
3. **Pillow Header Validation**: Corrupted bytes rejected prior to inference.
4. **CORS Restrictions**: Bound strictly to local development ports.
5. **Sanitized Error Responses**: Standardized JSON error payloads without stack trace exposure.

---

## 19. Quantitative Results & Comparison Summary
- **Baseline Custom CNN**: 259k params, 68.60% accuracy, 65.61% Macro F1, 25.91 min training.
- **Final MobileNetV2**: 2.42M params, 87.07% accuracy, 85.14% Macro F1, 8.36 min training.
- **Empirical Gains**: **+18.47 percentage points** accuracy gain, **+19.53 percentage points** Macro F1 gain, and **~3.1× shorter measured training time**.

---

## 20. Limitations
1. **Dataset Scope**: TrashNet contains single objects photographed on clean white backgrounds; real-world conveyor belts often contain overlapping multi-object waste.
2. **Trash Class Support**: The `trash` category has lower sample representation (137 images) compared to `paper` (594 images), leading to a lower class recall of 65.00%.
3. **Conflicting Annotations**: 3 cross-class exact duplicate pairs present in the original dataset require group-aware isolation.

---

## 21. Future Scope
1. **Multi-Object Detection**: Integrate YOLOv10 or Faster R-CNN for localized bounding-box multi-object waste detection.
2. **Edge Hardware Deployment**: Quantize MobileNetV2 to 8-bit TFLite for deployment on Raspberry Pi 5 or NVIDIA Jetson Nano robotic sorting arms.
3. **Domain Expansion**: Broaden dataset classes to include e-waste, hazardous batteries, and compostable organic waste.

---

## 22. Conclusion
The EcoClassify DL system successfully demonstrates an end-to-end, reproducible, and explainable deep learning pipeline for waste classification. Transfer learning via MobileNetV2 provides high classification accuracy (87.07%) and low inference latency (~61.15 ms), making it well-suited for automated waste sorting applications.

---

## 23. References
1. Thung, G., & Yang, M. (2016). *Classification of Trash for Recyclability Status*. CS 229 Project Report, Stanford University.
2. Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C. (2018). *MobileNetV2: Inverted Residuals and Linear Bottlenecks*. CVPR, 4510-4520.
3. Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). *Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization*. ICCV, 618-626.
