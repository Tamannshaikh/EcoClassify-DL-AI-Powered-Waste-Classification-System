# AI Implementation Order

This is the authoritative implementation sequence for an AI coding assistant.

## Before Coding
Read all:
1. README.md
2. PROJECT_REQUIREMENTS.md
3. FEATURES.md
4. TECH_STACK.md
5. DATABASE_SCHEMA.md
6. DATA_DICTIONARY.md
7. ML_SPECIFICATION.md
8. UI_DESIGN.md
9. API_SPECIFICATION.md
10. FOLDER_STRUCTURE.md
11. TESTING_PLAN.md
12. DEPLOYMENT.md
13. UI_MOCKUPS.pdf

Use these documents as the source of truth.

## Phase 1 — Repository Setup
Create:
- frontend
- backend
- data
- artifacts
- notebooks
- scripts
- tests

Create `.gitignore` and `.env.example`.

Acceptance:
Repository opens cleanly and dependencies can be installed.

## Phase 2 — Dataset Preparation
Implement:
- dataset inspection
- class discovery
- duplicate detection where practical
- train/validation/test split
- class distribution report
- class_names.json generation

Acceptance:
Prepared dataset has no accidental split leakage.

## Phase 3 — Custom CNN
Implement:
- preprocessing
- augmentation
- CNN model
- training script
- callbacks
- checkpoint
- evaluation
- training curves
- confusion matrix

Acceptance:
CNN model can be saved and loaded.

## Phase 4 — MobileNetV2
Implement:
- ImageNet backbone
- classification head
- frozen-backbone training
- optional fine-tuning
- evaluation
- model export

Acceptance:
MobileNetV2 can be loaded for inference.

## Phase 5 — Model Registry
Store:
- model version
- architecture
- class mapping
- input size
- metrics
- artifact path

Acceptance:
Backend knows which model is active.

## Phase 6 — Backend
Implement:
- FastAPI
- configuration
- model loader
- image validation
- preprocessing
- inference
- prediction response
- health endpoint
- metrics endpoint

Acceptance:
`POST /api/v1/predict` returns real model output.

## Phase 7 — Prediction History
Implement SQLite/local persistence.
Store:
- filename
- prediction
- confidence
- probabilities
- model version
- timestamp

Acceptance:
History survives backend restart.

## Phase 8 — Frontend
Implement in this order:
1. App shell
2. Home/Prediction
3. Dashboard
4. Dataset
5. Model Performance
6. Prediction History
7. About
8. Training Lab (optional)

Use UI_MOCKUPS as visual reference.

## Phase 9 — Grad-CAM
Implement only after normal inference is stable.

Acceptance:
Grad-CAM is optional and must never break normal prediction.

## Phase 10 — Testing
Run:
- unit tests
- API tests
- integration tests
- frontend tests
- ML tests

## Phase 11 — Performance and Hardening
- Load model once.
- Validate uploads.
- Limit file size.
- Sanitize filenames.
- Improve inference latency.
- Add useful error messages.
- Add loading/empty/error states.

## Phase 12 — Final Academic Package
Generate:
- dataset description
- architecture diagram
- model comparison
- accuracy/loss graphs
- confusion matrix
- classification report
- screenshots
- limitations
- future scope
- final README

## AI Coding Rules
- Do not fabricate accuracy.
- Do not hard-code prediction results.
- Do not retrain on every prediction.
- Do not use test images for training.
- Do not change class mapping after training without retraining/relabeling.
- Always save the preprocessing configuration with the model.
- Keep CPU-compatible inference.
- Keep MobileNetV2 as the practical transfer-learning option.
- Do not add unnecessary heavy models.
- Keep each phase runnable before moving to the next.
