# EcoClassify DL — React Frontend

AI-Powered Waste Classification System UI built with React, Vite, TypeScript, and Tailwind CSS.

## Architecture

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4 + Vanilla CSS Design System
- **Routing**: React Router DOM (Single Page Application)
- **State & API**: Axios with centralized `apiService` layer
- **Data Visualization**: Recharts (PieChart, BarChart, Custom Matrix Heatmap)
- **Icons**: Lucide React

## Pages

1. **Dashboard** (`/`): Real-time KPI cards, TrashNet class distribution chart, quick actions, model status, and recent SQLite predictions.
2. **Image Prediction** (`/predict`): Drag & drop image uploader (JPG/PNG <= 10MB), real-time MobileNetV2 inference, 6-class probability distribution, Grad-CAM attention heatmap overlay, and material disposal guidance.
3. **Prediction History** (`/history`): Paginated SQLite audit table, single prediction detail modal, and delete functionality.
4. **Dataset Information** (`/dataset`): TrashNet 2,527 dataset inventory, 70/15/15 stratified split charts, class composition, and duplicate isolation audit.
5. **Model Performance** (`/performance`): Quantitative evaluation metrics (Accuracy 87.07%, Macro F1 85.14%), per-class metrics chart, and interactive 6x6 test confusion matrix.
6. **Training & Models** (`/training`): Comparative analysis of Baseline Custom CNN vs. Final MobileNetV2 with performance deltas and training pipeline configurations.
7. **About System** (`/about`): Deep learning vision platform architecture, full-stack technologies, and Stanford TrashNet academic citations.
8. **Settings** (`/settings`): Backend API connection ping, active model metadata, and client-side security parameters.

## Development & Execution

```bash
# 1. Install dependencies
npm install

# 2. Run local development server
npm run dev

# 3. Build production bundle
npm run build
```

## Environment Configuration

Create `.env` file from `.env.example`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```
