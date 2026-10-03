# Final Live Demonstration Script

**Project**: AI-Powered Waste Classification System (EcoClassify DL)  
**Target Duration**: 5 to 10 minutes  
**Audience**: Examiners, Professors, and Peer Reviewers  

---

## Pre-Flight Checklist (1 Minute Before Demo)
1. **Terminal 1 (Backend)**: Ensure FastAPI is running on `http://127.0.0.1:8000`:
   ```powershell
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Terminal 2 (Frontend)**: Ensure Vite is running on `http://localhost:5173`:
   ```powershell
   cd frontend
   npm run dev
   ```
3. **Browser**: Open `http://localhost:5173` in full-screen mode.
4. **Test Samples Ready**: Keep folder `data/processed/test/` open for quick drag-and-drop.

---

## Step-by-Step Presentation Flow

### 1. Introduction & Dashboard (1.5 Minutes)
- **Action**: Display the **Dashboard (`/`)**.
- **Talking Points**:
  - Introduce the project: *"EcoClassify DL is an AI-powered waste classification system built with transfer learning to address recycling contamination."*
  - Point out the 4 KPI cards: **2,527 dataset images**, **6 standard classes**, **87.07% test accuracy**, and **85.14% Macro F1-score**.
  - Highlight the **TrashNet Class Distribution** chart rendered with Recharts.
  - Point out the active model badge: *"MobileNetV2 Transfer Learning running locally with sub-100ms CPU latency."*

### 2. Dataset Inventory & Leakage Audit (1 Minute)
- **Action**: Click **Dataset Info (`/dataset`)** in the sidebar.
- **Talking Points**:
  - Explain the 6 classes: Cardboard (403), Glass (501), Metal (410), Paper (594), Plastic (482), Trash (137).
  - Highlight the stratified **70% Train (1769), 15% Val (379), 15% Test (379)** split donut chart.
  - Explain the **group-aware duplicate isolation audit**: 3 cross-class duplicate pairs in the original Stanford TrashNet dataset were isolated strictly in `train/` to prevent test evaluation leakage.

### 3. Live Image Prediction & Grad-CAM (3 Minutes)
- **Action**: Navigate to **Image Prediction (`/predict`)**.
- **Demo Step A (Predict Real Test Image)**:
  - Drag and drop [`data/processed/test/plastic/plastic100.jpg`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/data/processed/test/plastic/plastic100.jpg) into the dropzone.
  - Click **"Run Deep Learning Classification"**.
  - Show the result: **Plastic (98.68% confidence, ~65ms latency)**.
  - Explain the full 6-class probability distribution bars.
  - Point out the dynamic **Disposal Guide** box for Plastic recycling.
- **Demo Step B (Explainability / Grad-CAM)**:
  - Toggle to the **"Grad-CAM Heatmap"** view.
  - Explain the visual attention overlay: *"Grad-CAM computes gradients across MobileNetV2's final convolutional layer (`out_relu`), showing that the neural network focuses specifically on the bottle contours and cap texture."*
- **Demo Step C (Second Test Sample - Metal/Paper)**:
  - Clear and upload a second sample (e.g., [`data/processed/test/paper/paper100.jpg`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/data/processed/test/paper/paper100.jpg)).
  - Run prediction and demonstrate instant classification (~98% Paper).

### 4. SQLite Prediction Audit History (1 Minute)
- **Action**: Navigate to **Prediction History (`/history`)**.
- **Talking Points**:
  - Show the persistent table populated with the live predictions just executed.
  - Click the **Eye icon** on a row to open the **Prediction Audit Record Modal** displaying stored 6-class probability distributions.
  - Click the **Trash icon** to delete a record and show real-time database synchronization.

### 5. Model Evaluation & Comparative Performance (1.5 Minutes)
- **Action**: Navigate to **Model Performance (`/performance`)** and then **Training & Models (`/training`)**.
- **Talking Points**:
  - Review the **6×6 Confusion Matrix Heatmap** and per-class precision/recall values.
  - In the Training Lab, highlight the empirical comparison:
    - Custom CNN Baseline: 259k params, 68.60% accuracy, 65.61% Macro F1.
    - MobileNetV2: 2.42M params, 87.07% accuracy, 85.14% Macro F1.
    - **+18.47% accuracy gain** and **~3.1× shorter training time**.

### 6. Settings, Security & Conclusion (1 Minute)
- **Action**: Navigate to **Settings (`/settings`)**.
- **Talking Points**:
  - Click **"Ping Backend"** to show live latency (~5-15 ms).
  - Summarize local security controls: 10MB limits, Pillow verification, strict CORS, and zero cloud data transmission.
  - Conclude: *"EcoClassify DL demonstrates a complete, production-ready, explainable AI pipeline for automated waste classification."*
  - Invite questions from examiners.
