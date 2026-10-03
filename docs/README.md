# Smart Waste Classification System

## 1. Project Overview
Smart Waste Classification is a Deep Learning mini-project that classifies an uploaded waste image into a predefined waste category.

The primary objective is to demonstrate an end-to-end Deep Learning workflow:
- Dataset preparation
- Image preprocessing
- Data augmentation
- CNN training
- Transfer learning comparison
- Model evaluation
- Model saving/loading
- Image prediction
- Web-based inference UI
- Analytics and model performance visualization

The system is designed to run locally on a normal Windows PC. Training must be practical on CPU and faster when an NVIDIA GPU is available.

## 2. Recommended Waste Classes
MVP classes:
1. cardboard
2. glass
3. metal
4. paper
5. plastic
6. organic

The class list must be configurable so the implementation can adapt to the selected dataset.

## 3. Main User Workflow
1. Open the application.
2. Upload or drag-and-drop a waste image.
3. Validate file type and size.
4. Resize and normalize the image.
5. Run the saved Deep Learning model.
6. Display predicted class.
7. Display confidence/probability.
8. Display all class probabilities.
9. Optionally show Grad-CAM heatmap.
10. Store prediction history locally if enabled.

## 4. Deep Learning Approach
Two model modes are planned:

### Model A — Lightweight CNN
A custom CNN demonstrates the fundamentals:
- Convolution
- ReLU
- Max Pooling
- Batch Normalization where useful
- Dropout
- Dense layer
- Softmax output

### Model B — Transfer Learning
Recommended primary production/demo model:
- MobileNetV2 with ImageNet weights
- Input size: 224x224
- Frozen backbone initially
- Small classification head
- Optional fine-tuning of the last layers

MobileNetV2 is intentionally selected because the project should remain practical on a local Ryzen 7 laptop/desktop and does not require a large GPU.

## 5. Expected Application Modules
- Home / Prediction
- Model Performance
- Dataset Information
- Prediction History
- About / Project Information
- Optional Training page for development only

## 6. Recommended Technology
Frontend:
- React + Vite
- TypeScript
- Tailwind CSS

Backend:
- Python
- FastAPI

Deep Learning:
- TensorFlow / Keras
- NumPy
- Pillow
- scikit-learn
- Matplotlib

Optional:
- OpenCV
- Grad-CAM implementation

## 7. Local-First Requirement
The project must work without an internet connection after dependencies, dataset, model, and application files have been installed locally.

Important:
- Training is performed offline/local.
- The trained `.keras` model is saved.
- Prediction loads the saved model.
- The application must NOT retrain every time a user uploads an image.

## 8. Model Artifact
Recommended:
`artifacts/models/waste_classifier_mobilenetv2.keras`

Also save:
- class_names.json
- preprocessing configuration
- model metrics
- training history

## 9. Example Prediction
Input:
`plastic_bottle.jpg`

Output:
```text
Prediction: Plastic
Confidence: 96.4%

Plastic      96.4%
Glass         1.4%
Paper         0.9%
Metal         0.7%
Cardboard     0.4%
Organic       0.2%
```

These values are illustrative only. The application must show actual model results.

## 10. Important Academic Requirement
The project must clearly document:
- Dataset source
- Number of images
- Class distribution
- Train/validation/test split
- Image preprocessing
- Augmentation
- Model architecture
- Hyperparameters
- Training curves
- Confusion matrix
- Precision
- Recall
- F1-score
- Test accuracy
- Limitations

## 11. Documentation
See the remaining files in this repository for detailed requirements and implementation instructions.
