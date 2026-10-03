# ML Specification

## 1. Objective
Classify waste images into six categories:
- cardboard
- glass
- metal
- paper
- plastic
- organic

## 2. Dataset
Use a publicly available labelled waste image dataset suitable for academic use. The exact dataset and license/source URL must be recorded in the final report.

Do not mix multiple datasets without documenting:
- source
- class mapping
- duplicate handling
- license
- total images

## 3. Data Split
Recommended:
- 70% training
- 15% validation
- 15% test

If the dataset already provides official splits, preserve them where appropriate.

Ensure there is no image duplication across splits.

## 4. Preprocessing
Custom CNN:
- Resize: 128x128
- RGB
- Normalize pixels to [0,1]

MobileNetV2:
- Resize: 224x224
- RGB
- Use `tf.keras.applications.mobilenet_v2.preprocess_input`

## 5. Data Augmentation
Training only:
- Random horizontal flip
- Small rotation
- Small translation
- Small zoom
- Optional contrast adjustment

Do not apply random augmentation to validation/test data.

## 6. Custom CNN Baseline
Example architecture:
Input
→ Conv2D(32)
→ ReLU
→ MaxPooling
→ Conv2D(64)
→ ReLU
→ MaxPooling
→ Conv2D(128)
→ ReLU
→ MaxPooling
→ GlobalAveragePooling
→ Dropout
→ Dense(128)
→ Dropout
→ Dense(6, softmax)

The exact architecture may be tuned after baseline training.

## 7. MobileNetV2
- Load ImageNet-pretrained MobileNetV2.
- Remove original classifier.
- Freeze backbone initially.
- Add GlobalAveragePooling2D.
- Add Dropout.
- Add Dense(6, softmax).
- Train classification head.
- Optional fine-tuning: unfreeze a small number of top backbone layers using a very small learning rate.

## 8. Loss
For integer labels:
`sparse_categorical_crossentropy`

## 9. Optimizer
Adam.

Initial learning rate:
- CNN: approximately 1e-3
- MobileNetV2 head: approximately 1e-3 or lower
- Fine-tuning: approximately 1e-5

Tune based on validation behavior.

## 10. Callbacks
Use:
- EarlyStopping(monitor=val_loss, patience=5, restore_best_weights=True)
- ReduceLROnPlateau(monitor=val_loss, patience=2)
- ModelCheckpoint(save_best_only=True)

## 11. Metrics
Report:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- Per-class performance

Use macro and weighted averages where useful.

## 12. Model Selection
Compare CNN and MobileNetV2 using:
- validation F1
- validation accuracy
- test F1
- test accuracy
- inference time
- model size

Do not fabricate a result before training.

## 13. Overfitting Control
- Data augmentation
- Dropout
- Early stopping
- Transfer learning
- Learning-rate scheduling
- Appropriate train/validation split

## 14. Model Export
Save:
- `.keras` model
- `class_names.json`
- `metrics.json`
- `training_history.json`

## 15. Explainability
Optional Grad-CAM:
- Select the final convolutional layer.
- Generate activation heatmap.
- Overlay heatmap on input image.
- Clearly label it as a model attention/activation visualization, not proof of causation.

## 16. Inference
The inference service must:
1. Load model once.
2. Validate image.
3. Preprocess exactly as training.
4. Predict.
5. Apply softmax if model does not already output probabilities.
6. Map indices using class_names.json.
7. Return sorted probabilities.

## 17. Reproducibility
Record:
- random seeds
- Python version
- TensorFlow version
- dataset source
- dataset size
- split
- class mapping
- hyperparameters
- model version
