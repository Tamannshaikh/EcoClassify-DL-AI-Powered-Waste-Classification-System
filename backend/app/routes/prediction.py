"""
Waste Image Prediction Routes.
Handles single image classification, image storage, and optional Grad-CAM explainability.
"""
import io
import time
from pathlib import Path
from typing import Tuple
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.app.schemas import PredictionResponse
from backend.app.model_loader import ModelManager
from backend.app.database import save_prediction, get_next_prediction_id
from backend.app.ml.gradcam import create_gradcam_overlay
from backend.app.config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_UPLOAD_BYTES,
    MAX_UPLOAD_SIZE_MB,
    PREDICTIONS_UPLOAD_DIR
)

router = APIRouter(tags=["Prediction"])


async def validate_and_read_image(file: UploadFile) -> Tuple[Image.Image, bytes, str]:
    """Validates file extension, size, image integrity, and returns PIL Image and raw bytes."""
    # 1. Extension check
    file_ext = Path(file.filename or "upload.jpg").suffix.lower()
    if not file_ext or file_ext not in ALLOWED_EXTENSIONS:
        if file_ext == ".jpeg":
            file_ext = ".jpg"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_FILE_EXTENSION",
                    "message": f"Unsupported file extension '{file_ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}"
                }
            )

    # 2. Read bytes and check size
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File size exceeds maximum allowed limit of {MAX_UPLOAD_SIZE_MB}MB."
            }
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "EMPTY_FILE",
                "message": "Uploaded file is empty."
            }
        )

    # 3. Pillow Image verification
    try:
        image_stream = io.BytesIO(contents)
        with Image.open(image_stream) as img:
            img.verify()  # Check structure
        
        # Re-open for actual processing
        image = Image.open(io.BytesIO(contents))
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image, contents, file_ext
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_IMAGE_FILE",
                "message": "Uploaded file is corrupted or not a valid readable image."
            }
        )


@router.post("/predict", response_model=PredictionResponse)
async def predict_waste(file: UploadFile = File(...)):
    """Predicts waste class, saves uploaded image locally, and returns category-based ID."""
    manager = ModelManager.get_instance()
    if not manager.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "MODEL_NOT_READY", "message": "Deep learning model is not loaded yet."}
        )

    pil_image, raw_bytes, file_ext = await validate_and_read_image(file)

    # Measure inference
    t0 = time.perf_counter()
    pred_result = manager.predict(pil_image)
    t1 = time.perf_counter()
    inference_ms = float(round((t1 - t0) * 1000.0, 2))

    # Category-based prediction ID
    pred_class = pred_result["predicted_class"]
    pred_id = get_next_prediction_id(pred_class)
    
    # Store analyzed image locally with safe ID filename
    stored_filename = f"{pred_id}{file_ext}"
    target_image_path = PREDICTIONS_UPLOAD_DIR / stored_filename
    try:
        with open(target_image_path, "wb") as f:
            f.write(raw_bytes)
    except Exception:
        # Fallback to saving via PIL
        try:
            pil_image.save(target_image_path)
        except Exception:
            pass

    rel_image_path = f"data/uploads/predictions/{stored_filename}"
    image_url = f"/api/v1/predictions/{pred_id}/image"

    # Save to SQLite
    try:
        save_prediction(
            prediction_id=pred_id,
            filename=stored_filename,
            original_filename=file.filename or "unknown.jpg",
            predicted_class=pred_class,
            confidence=pred_result["confidence"],
            probabilities=pred_result["probabilities"],
            inference_time_ms=inference_ms,
            model_version=manager.model_version,
            gradcam_generated=False,
            image_path=rel_image_path,
            image_url=image_url
        )
    except Exception:
        pass

    return PredictionResponse(
        prediction_id=pred_id,
        filename=stored_filename,
        predicted_class=pred_class,
        confidence=pred_result["confidence"],
        probabilities=pred_result["probabilities"],
        inference_time_ms=inference_ms,
        model_version=manager.model_version,
        image_url=image_url,
        image_path=rel_image_path,
        gradcam_base64=None
    )


@router.post("/predict/gradcam", response_model=PredictionResponse)
async def predict_waste_with_gradcam(file: UploadFile = File(...)):
    """Predicts waste class, saves uploaded image locally, and generates Grad-CAM heatmap."""
    manager = ModelManager.get_instance()
    if not manager.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "MODEL_NOT_READY", "message": "Deep learning model is not loaded yet."}
        )

    pil_image, raw_bytes, file_ext = await validate_and_read_image(file)

    # Inference
    t0 = time.perf_counter()
    pred_result = manager.predict(pil_image)
    t1 = time.perf_counter()
    inference_ms = float(round((t1 - t0) * 1000.0, 2))

    # Category-based prediction ID
    pred_class = pred_result["predicted_class"]
    pred_id = get_next_prediction_id(pred_class)

    # Store analyzed image locally with safe ID filename
    stored_filename = f"{pred_id}{file_ext}"
    target_image_path = PREDICTIONS_UPLOAD_DIR / stored_filename
    try:
        with open(target_image_path, "wb") as f:
            f.write(raw_bytes)
    except Exception:
        try:
            pil_image.save(target_image_path)
        except Exception:
            pass

    rel_image_path = f"data/uploads/predictions/{stored_filename}"
    image_url = f"/api/v1/predictions/{pred_id}/image"

    # Grad-CAM heatmap
    gradcam_b64 = None
    try:
        top_idx = manager.classes.index(pred_class)
        gradcam_b64 = create_gradcam_overlay(pil_image, manager.model, pred_index=top_idx)
    except Exception:
        pass

    # Save to SQLite
    try:
        save_prediction(
            prediction_id=pred_id,
            filename=stored_filename,
            original_filename=file.filename or "unknown.jpg",
            predicted_class=pred_class,
            confidence=pred_result["confidence"],
            probabilities=pred_result["probabilities"],
            inference_time_ms=inference_ms,
            model_version=manager.model_version,
            gradcam_generated=(gradcam_b64 is not None),
            image_path=rel_image_path,
            image_url=image_url
        )
    except Exception:
        pass

    return PredictionResponse(
        prediction_id=pred_id,
        filename=stored_filename,
        predicted_class=pred_class,
        confidence=pred_result["confidence"],
        probabilities=pred_result["probabilities"],
        inference_time_ms=inference_ms,
        model_version=manager.model_version,
        image_url=image_url,
        image_path=rel_image_path,
        gradcam_base64=gradcam_b64
    )
