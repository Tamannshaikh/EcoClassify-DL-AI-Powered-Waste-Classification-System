# Testing Plan

## 1. Unit Tests
- Class-name mapping
- Image preprocessing
- Image validation
- Model loading
- Prediction output formatting
- Probability sorting
- Dataset counting
- Metric calculations

## 2. ML Tests
- Correct class count
- No test leakage
- Correct image shape
- Correct normalization
- Model output shape equals number of classes
- Probabilities sum approximately to 1
- Model loads after restart
- Same image produces stable prediction with deterministic inference

## 3. API Tests
- GET /health
- GET /model/info
- POST /predict with valid JPG
- POST /predict with PNG
- POST /predict with invalid file
- POST /predict with oversized file
- GET /model/metrics
- GET /predictions

## 4. Frontend Tests
- Upload button
- Drag/drop
- Image preview
- Predict button
- Loading state
- Result rendering
- Probability chart
- Error state
- Model unavailable state
- Responsive layout

## 5. Integration Tests
1. Start backend.
2. Load saved model.
3. Start frontend.
4. Upload image.
5. Frontend calls API.
6. Backend preprocesses image.
7. Model predicts.
8. UI displays result.

## 6. Performance Tests
Measure:
- Model load time
- Average CPU inference time
- Average GPU inference time if available
- Frontend response time

## 7. Acceptance Test
A clean local setup must be able to:
- install dependencies
- load a saved model
- open web UI
- upload a sample image
- return a prediction
- display confidence
- display model information
