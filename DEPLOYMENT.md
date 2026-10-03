# Deployment

## Local Windows Setup

### Prerequisites
- Windows 10/11
- Python 3.11
- Node.js 20+
- Git
- Optional NVIDIA GPU

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Training
Training should be executed separately from the prediction server.

Example:
```bash
python scripts/train.py --model mobilenetv2 --epochs 20 --batch-size 16
```

After training:
```text
artifacts/
└── models/
    ├── waste_classifier_mobilenetv2.keras
    └── class_names.json
```

## Inference
The backend loads the saved `.keras` model when it starts.

Do NOT retrain when the user uploads an image.

## Production
Frontend:
```bash
npm run build
```

Backend:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

For a student project, local deployment is sufficient.

## Environment Variables
Copy:
`.env.example` → `.env`

Never commit `.env`.

## Hardware Notes
The application must support CPU inference.

Recommended training strategy for a Ryzen 7 PC:
- Start with custom CNN.
- Train MobileNetV2 with frozen backbone.
- Use 16 batch size if memory is limited.
- Use early stopping.
- Reduce image size only when necessary.
- Save checkpoints.

If training becomes slow, use Google Colab for training while keeping the final saved model and web application locally. This is optional; the local inference application must still work.

## Deployment Verification
- Backend health works.
- Model loads.
- Frontend connects.
- Image upload works.
- Prediction works.
- Error handling works.
- No secrets are exposed.
