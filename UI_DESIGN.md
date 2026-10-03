# UI Design

## Design Goal
Modern, clean AI dashboard suitable for a college Deep Learning mini-project.

Visual style:
- Dark sidebar
- Light main background
- White cards
- Indigo/blue primary accent
- Rounded cards
- Minimal animations
- Clear prediction result

## Navigation
1. Home / Predict
2. Dashboard
3. Dataset
4. Model Performance
5. Prediction History
6. About

Optional:
7. Training Lab

## Login
Fields:
- Email
- Password
- Login

For a student mini-project, authentication can be simple/local. Do not store real credentials in source code.

## Home / Prediction
Main elements:
- Drag & drop area
- Browse button
- Image preview
- Predict button
- Prediction result card
- Confidence
- Probability distribution
- Optional Grad-CAM

## Dashboard
KPI cards:
- Number of classes
- Test accuracy
- F1-score
- Model version

Charts:
- Class distribution
- Confusion matrix
- Training accuracy/loss

## Dataset
Show:
- Dataset name
- Number of images
- Number of classes
- Train/validation/test counts
- Class distribution

## Model Performance
Show:
- Model name
- Accuracy
- Precision
- Recall
- F1
- Training curves
- Confusion matrix
- Inference time

## Prediction History
Columns:
- Time
- Filename
- Prediction
- Confidence
- Model

## About
Explain:
- Problem
- Deep Learning approach
- Classes
- Dataset
- Limitations

## UI States
Every prediction screen must support:
- idle
- image selected
- predicting
- success
- invalid image
- backend unavailable
- model unavailable

## Accessibility
- Visible labels
- Keyboard navigation
- Focus states
- Text alternatives for important visual information
- Do not communicate prediction only through color
