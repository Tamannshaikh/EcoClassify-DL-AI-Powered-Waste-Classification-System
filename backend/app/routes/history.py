from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from backend.app.schemas import PredictionHistoryListResponse, PredictionHistoryItem
from backend.app.database import (
    get_predictions,
    get_total_prediction_count,
    get_prediction_by_id,
    delete_prediction
)
from backend.app.config import PROJECT_ROOT, PREDICTIONS_UPLOAD_DIR

router = APIRouter(prefix="/predictions", tags=["History"])


@router.get("", response_model=PredictionHistoryListResponse)
async def list_predictions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Returns list of recent predictions with pagination."""
    items = get_predictions(limit=limit, offset=offset)
    total = get_total_prediction_count()
    return PredictionHistoryListResponse(total=total, predictions=items)


@router.get("/{id}/image")
async def get_prediction_image(id: str):
    """Retrieves the stored analyzed image for a prediction record safely."""
    item = get_prediction_by_id(id)
    if not item or not item.get("image_path"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "IMAGE_NOT_FOUND", "message": f"Image for prediction '{id}' not found."}
        )

    raw_path = Path(item["image_path"])
    full_path = (PROJECT_ROOT / raw_path).resolve()

    # Enforce path containment within approved PREDICTIONS_UPLOAD_DIR or PROJECT_ROOT
    try:
        full_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN_PATH", "message": "Access denied."}
        )

    if not full_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "IMAGE_NOT_FOUND", "message": f"Image file for prediction '{id}' not found on server."}
        )

    suffix = full_path.suffix.lower()
    media_type = "image/png" if suffix == ".png" else "image/jpeg"
    return FileResponse(path=full_path, media_type=media_type)


@router.get("/{id}", response_model=PredictionHistoryItem)
async def get_single_prediction(id: str):
    """Retrieves a single prediction record by ID."""
    item = get_prediction_by_id(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Prediction '{id}' not found."}
        )
    return item


@router.delete("/{id}")
async def remove_prediction(id: str):
    """Deletes a prediction record from history and removes associated image file."""
    success = delete_prediction(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Prediction '{id}' not found."}
        )
    return {"status": "success", "message": f"Prediction '{id}' deleted."}
