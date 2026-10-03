# Project Requirements

## 1. Functional Requirements

### FR-01 Image Upload
The system shall allow a user to upload a waste image.

Supported formats:
- JPG/JPEG
- PNG
- WEBP

Default maximum file size:
- 10 MB

### FR-02 Image Preview
Before prediction, the UI shall display the uploaded image.

### FR-03 Image Validation
The backend shall validate:
- Extension/content type
- File size
- Readability
- Valid image dimensions

Invalid files must receive a clear error message.

### FR-04 Preprocessing
The inference pipeline shall:
1. Load image.
2. Convert to RGB.
3. Resize to the model's expected input size.
4. Apply the same normalization used during training.
5. Add batch dimension.

### FR-05 Prediction
The model shall return:
- Predicted class
- Confidence
- Probability for every class
- Model version
- Timestamp

### FR-06 Prediction History
Optional local history shall store recent predictions with:
- filename
- predicted class
- confidence
- timestamp
- model version

### FR-07 Model Analytics
The application shall display:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- Training/validation accuracy
- Training/validation loss

### FR-08 Grad-CAM
If enabled, the application shall generate a heatmap showing regions that contributed to the prediction.

### FR-09 Model Comparison
Development dashboard may compare:
- Custom CNN
- MobileNetV2

The final demo may use the selected model based on documented validation/test performance and practical runtime.

### FR-10 About Project
Display:
- Problem statement
- Classes
- Model used
- Dataset information
- Limitations

## 2. Non-Functional Requirements
- Local execution must be supported.
- Inference should be fast enough for interactive use.
- Model should be loaded once when backend starts.
- No training during prediction.
- Responsive UI.
- Clear loading/error/empty states.
- No hard-coded prediction results.
- Code should be modular.
- Configuration should use environment variables where applicable.

## 3. ML Acceptance Requirements
- No test images in training set.
- Reproducible split or documented dataset split.
- Class labels are consistent.
- Training and inference preprocessing are identical.
- Test metrics are generated from held-out test data.
- Model artifact can be loaded after application restart.

## 4. Security Requirements
- Validate uploaded file.
- Restrict file size.
- Store uploads in controlled directory.
- Do not execute uploaded files.
- Sanitize filenames.
- Do not expose server filesystem paths.
