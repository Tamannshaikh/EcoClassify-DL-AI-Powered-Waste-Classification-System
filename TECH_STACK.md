# Tech Stack

## Deep Learning
- Python 3.11 recommended
- TensorFlow 2.x / Keras
- NumPy
- Pillow
- scikit-learn
- Matplotlib

## Optional
- OpenCV
- tensorflow-addons only if genuinely needed
- Grad-CAM utility/library if compatible with selected TensorFlow version

## Backend
- FastAPI
- Uvicorn
- Pydantic

## Frontend
- React
- Vite
- TypeScript
- Tailwind CSS
- Axios
- Recharts

## Development
- VS Code
- Git
- GitHub
- Python virtual environment

## Local Hardware Strategy
The project is designed to be runnable on a Ryzen 7 HP Victus-class Windows PC.

Recommended:
- Custom CNN for lightweight baseline
- MobileNetV2 for primary transfer-learning model
- 128x128 input for custom CNN
- 224x224 input for MobileNetV2
- Batch size 16 or 32 depending on RAM/GPU
- Early stopping
- ReduceLROnPlateau
- Model checkpointing

If an NVIDIA GPU is available, TensorFlow GPU support can be used where compatible. The project must still have a CPU-compatible inference path.

## Why MobileNetV2
MobileNetV2 offers a strong transfer-learning baseline while keeping computational requirements substantially lower than large architectures such as ResNet152 or EfficientNet-Large.
