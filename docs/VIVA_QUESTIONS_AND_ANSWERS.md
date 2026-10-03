# Viva Questions and Answers — Waste Classification Deep Learning Project

**Project Title**: AI-Powered Waste Classification System using Deep Learning  
**Application Name**: EcoClassify DL  

---

### Q1: What is the primary objective of this project?
**Answer**: The project aims to develop an end-to-end, local-first Deep Learning system to classify waste images into six standard recyclable categories (*Cardboard, Glass, Metal, Paper, Plastic, Trash*) with high accuracy and explainability (Grad-CAM), served via a FastAPI backend and React frontend.

---

### Q2: Which dataset was used, and what are its key statistics?
**Answer**: The benchmark **TrashNet** dataset collected by Gary Thung and Mindy Yang at Stanford University. It contains **2,527** RGB images (512×384) distributed across six classes: cardboard (403), glass (501), metal (410), paper (594), plastic (482), and trash (137).

---

### Q3: Why are there only six classes and no "organic" class?
**Answer**: The official TrashNet benchmark dataset only contains six defined classes (*cardboard, glass, metal, paper, plastic, trash*). Introducing an "organic" class without verified organic image samples would corrupt the academic integrity of the benchmark.

---

### Q4: What dataset splitting strategy was used, and why?
**Answer**: A stratified **70% train (1,769), 15% validation (379), and 15% test (379)** split was used. Stratification ensures each split preserves the exact class frequency proportions of the original dataset.

---

### Q5: What is data leakage, and how was it prevented in this project?
**Answer**: Data leakage occurs when test data (or duplicates of test data) contaminate the training set, leading to overly optimistic evaluations. During our Phase 2 audit, we identified 3 pairs of identical byte-duplicate images labeled with conflicting classes. We implemented a **group-aware split** that placed all duplicate pairs strictly inside the training set, guaranteeing 0% test contamination.

---

### Q6: What preprocessing steps were applied to input images?
**Answer**: Images were converted to RGB, resized using bilinear interpolation to $224 \times 224$ pixels, and normalized to $[-1, 1]$ using MobileNetV2's standard scaling formula ($x / 127.5 - 1.0$).

---

### Q7: What data augmentation techniques were used during training?
**Answer**: On-the-fly Keras preprocessing layers: horizontal flips, random rotations ($\pm 8\%$), random zooms ($\pm 8\%$), and small translations ($\pm 5\%$). Augmentation was applied exclusively to training batches to improve generalization and prevent overfitting.

---

### Q8: What was the architecture of the baseline Custom CNN?
**Answer**: A 4-block convolutional network (32 &rarr; 64 &rarr; 128 &rarr; 256 filters) with Batch Normalization, ReLU activations, MaxPooling2D ($2 \times 2$), Dropout ($0.25$), GlobalAveragePooling2D, a 256-unit Dense layer with Dropout ($0.5$), and a 6-unit Softmax output layer (Total: 259,526 parameters).

---

### Q9: Why was MobileNetV2 chosen as the transfer learning architecture?
**Answer**: MobileNetV2 offers high accuracy with a lightweight inverted residual bottleneck architecture ($2.42\text{M}$ parameters), making it ideal for real-time CPU inference (~61 ms) without requiring dedicated GPU acceleration.

---

### Q10: What is transfer learning, and how was it implemented?
**Answer**: Transfer learning leverages feature representations learned by a model pre-trained on a massive dataset (ImageNet). We froze the MobileNetV2 backbone to extract low-level edge and texture features, trained a new 6-class classification head, and subsequently fine-tuned the top 30 layers with a lower learning rate ($10^{-4}$).

---

### Q11: What is fine-tuning, and why is a lower learning rate necessary?
**Answer**: Fine-tuning unfreezes upper layers of the pre-trained backbone to adapt high-level feature extractors to the specific domain. A low learning rate ($10^{-4}$ or $10^{-5}$) is crucial to prevent "catastrophic forgetting" of the general pre-trained weights.

---

### Q12: How did MobileNetV2 perform compared to the baseline Custom CNN?
**Answer**:
- **Test Accuracy**: MobileNetV2 **87.07%** vs. CNN **68.60%** (+18.47 percentage points).
- **Macro F1-Score**: MobileNetV2 **85.14%** vs. CNN **65.61%** (+19.53 percentage points).
- **Training Duration**: MobileNetV2 **~8.36 min** vs. CNN **~25.91 min** (~3.1× shorter training duration).

---

### Q13: What loss function and optimizer were used?
**Answer**: Categorical Crossentropy loss paired with the **Adam** optimizer, utilizing an initial learning rate of $10^{-3}$ for head training and $10^{-4}$ for fine-tuning.

---

### Q14: What callbacks were utilized during model training?
**Answer**:
1. `EarlyStopping` (patience=7, monitor=`val_loss`, `restore_best_weights=True`) to prevent overfitting.
2. `ReduceLROnPlateau` (factor=0.5, patience=3) to decrease learning rate when validation loss plateaued.
3. `ModelCheckpoint` to save optimal weights.

---

### Q15: What is the difference between Accuracy, Precision, Recall, and F1-Score?
**Answer**:
- **Accuracy**: Fraction of all predictions that were correct ($TP + TN / Total$).
- **Precision**: Out of all items predicted as class $C$, how many were actually class $C$ ($TP / (TP + FP)$).
- **Recall**: Out of all actual items of class $C$, how many did the model find ($TP / (TP + FN)$).
- **F1-Score**: Harmonic mean of Precision and Recall ($2 \cdot (P \cdot R) / (P + R)$).

---

### Q16: Why is Macro F1 preferred over simple accuracy for imbalanced datasets?
**Answer**: Simple accuracy can be skewed by dominant classes (e.g., Paper with 594 samples vs. Trash with 137 samples). Macro F1 calculates the unweighted arithmetic mean of F1-scores across all classes, treating every class with equal importance regardless of size.

---

### Q17: Why did the "trash" class have lower recall (65.00%)?
**Answer**: The `trash` class is an inherently diverse residual category (containing miscellaneous broken ceramics, composites, and wrappers) and has the lowest sample support in TrashNet (only 137 total images, 20 test samples), making feature clustering more challenging.

---

### Q18: What is Grad-CAM, and why is it important in this project?
**Answer**: Gradient-weighted Class Activation Mapping (Grad-CAM) is an Explainable AI (XAI) technique. It calculates gradients of the predicted class score with respect to the final convolutional feature maps, producing a spatial heatmap overlay that visually highlights which image regions (e.g., can rim, bottle texture) guided the neural network's decision.

---

### Q19: Which layer was selected for Grad-CAM in MobileNetV2, and why?
**Answer**: The `out_relu` convolutional layer within the `mobilenetv2_1.00_224` backbone (output shape $7 \times 7 \times 1280$). The final convolutional layer contains the richest spatial and high-level semantic feature representations.

---

### Q20: Why was FastAPI chosen for the backend?
**Answer**: FastAPI provides asynchronous high-performance request handling, automatic OpenAPI/Swagger documentation generation, native Pydantic schema validation, and Python-native integration with TensorFlow and NumPy.

---

### Q21: How is the model loaded in the FastAPI backend?
**Answer**: Through an asynchronous lifespan context manager utilizing a singleton `ModelManager`. The model binary (`waste_classifier.keras`) is loaded into memory **once** on application startup and warmed up with a dummy tensor. It is never reloaded per prediction request.

---

### Q22: Does the backend retrain the model during inference?
**Answer**: No. Inference is strictly deterministic forward-pass evaluation using the static, pre-trained weights. Training occurs exclusively in offline batch training scripts.

---

### Q23: What database was used, and what does it store?
**Answer**: An embedded **SQLite** database (`data/waste_classification.db`). It stores prediction audit records: prediction UUID, filename, predicted class, confidence score, full 6-class probability distribution JSON, inference latency in ms, model version, and creation timestamp.

---

### Q24: What image validation and security checks are enforced?
**Answer**:
1. Client and server file size cap ($10\text{ MB}$).
2. Strict extension check (`.jpg`, `.jpeg`, `.png`).
3. Pillow image header and structure verification (rejecting corrupted files and code payloads).
4. Strict local CORS origins (`localhost:5173`, `127.0.0.1:5173`).
5. Safe random UUID-prefixed file naming.

---

### Q25: Why was React with Vite and TypeScript chosen for the frontend?
**Answer**: Vite provides instant hot module replacement (HMR) and rapid build times. TypeScript enforces static type safety across API response contracts, preventing runtime undefined property bugs.

---

### Q26: What charting library was used in the frontend?
**Answer**: **Recharts**, a modular React charting library built on SVG, used to render class distribution bar charts, dataset split donut charts, per-class metric bars, and the interactive $6 \times 6$ confusion matrix heatmap.

---

### Q27: How does the system handle real-time inference latency?
**Answer**: On standard consumer CPU hardware (AMD Ryzen 7), MobileNetV2 executes inference in approximately **61.15 ms**, enabling interactive web-based classification well within standard human real-time perception thresholds (<100 ms).

---

### Q28: How is the base64 Grad-CAM image transmitted from backend to frontend?
**Answer**: The backend blends the Jet colormap with the original image, encodes the output as a JPEG byte stream, converts it to a standard `data:image/jpeg;base64,...` data URI, and returns it within the JSON prediction response for direct rendering in an `<img>` tag.

---

### Q29: What are the primary limitations of the current system?
**Answer**:
1. Single-object assumption (TrashNet photos contain one centered object on a white background).
2. Class imbalance in the `trash` category.
3. Lack of bounding-box localization for multi-waste scenes.

---

### Q30: How would you expand this project in the future?
**Answer**:
1. Incorporate object detection models (YOLOv10 / Faster R-CNN) for multi-object segmentation on moving conveyor belts.
2. Quantize the model to 8-bit TFLite for deployment on edge devices (Raspberry Pi 5 / NVIDIA Jetson).
3. Expand waste categories to electronic waste (e-waste), hazardous items, and compostable organic food scraps.
