# Folder Structure

```text
waste-classification-dl/
├── README.md
├── PROJECT_REQUIREMENTS.md
├── FEATURES.md
├── TECH_STACK.md
├── DATABASE_SCHEMA.md
├── DATA_DICTIONARY.md
├── ML_SPECIFICATION.md
├── UI_DESIGN.md
├── API_SPECIFICATION.md
├── FOLDER_STRUCTURE.md
├── TESTING_PLAN.md
├── DEPLOYMENT.md
├── CHANGELOG.md
├── AI_IMPLEMENTATION_ORDER.md
├── .env.example
├── UI_MOCKUPS.pdf
│
├── UI_MOCKUPS/
│   ├── README.md
│   ├── login.png
│   ├── dashboard.png
│   ├── prediction.png
│   ├── dataset.png
│   ├── model_performance.png
│   ├── prediction_history.png
│   ├── about.png
│   ├── training.png
│   └── settings.png
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── api/
│       ├── components/
│       ├── layouts/
│       ├── pages/
│       ├── hooks/
│       ├── routes/
│       ├── types/
│       ├── utils/
│       └── main.tsx
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ml/
│   │   │   ├── preprocessing.py
│   │   │   ├── dataset.py
│   │   │   ├── train_cnn.py
│   │   │   ├── train_mobilenet.py
│   │   │   ├── evaluate.py
│   │   │   └── inference.py
│   │   └── utils/
│   └── tests/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── artifacts/
│   ├── models/
│   ├── metrics/
│   ├── histories/
│   └── gradcam/
│
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_cnn_training.ipynb
│   ├── 03_mobilenet_training.ipynb
│   └── 04_evaluation.ipynb
│
└── scripts/
    ├── prepare_dataset.py
    ├── train.py
    └── evaluate.py
```

Never commit the full dataset, generated uploads, or large model artifacts unless intentionally required.
