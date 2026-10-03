"""
Health Check Route.
"""
from fastapi import APIRouter
from backend.app.schemas import HealthResponse
from backend.app.model_loader import ModelManager

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns service health and model status."""
    manager = ModelManager.get_instance()
    return HealthResponse(
        status="ok",
        model_loaded=manager.is_loaded,
        model_name=manager.metadata.get("model_name", "MobileNetV2 (Transfer Learning)"),
        model_version=manager.model_version,
        classes=manager.classes
    )
