"""
Model Information and Metrics Routes.
"""
import json
from fastapi import APIRouter, HTTPException
from backend.app.schemas import ModelInfoResponse, MetricsResponse
from backend.app.model_loader import ModelManager
from backend.app.config import EVALUATION_DIR

router = APIRouter(prefix="/model", tags=["Model"])


@router.get("/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Returns metadata and architectural information of the active model."""
    manager = ModelManager.get_instance()
    if not manager.is_loaded:
        raise HTTPException(status_code=503, detail={"code": "MODEL_UNAVAILABLE", "message": "Model not loaded"})

    meta = manager.metadata
    return ModelInfoResponse(
        model_name=meta.get("model_name", "MobileNetV2 (Transfer Learning)"),
        model_architecture=meta.get("model_architecture", "mobilenetv2"),
        framework=meta.get("framework", "TensorFlow / Keras"),
        input_shape=meta.get("input_shape", [224, 224, 3]),
        classes=manager.classes,
        num_classes=len(manager.classes),
        total_parameters=meta.get("total_parameters", 0),
        test_accuracy=meta.get("test_accuracy", 0.0),
        macro_precision=meta.get("macro_precision", 0.0),
        macro_recall=meta.get("macro_recall", 0.0),
        macro_f1=meta.get("macro_f1", 0.0),
        weighted_f1=meta.get("weighted_f1", 0.0),
        training_config=meta.get("training_config", {}),
        cpu_inference_benchmark=meta.get("cpu_inference_benchmark", None)
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_model_metrics():
    """Returns evaluation metrics, confusion matrix, and model comparison."""
    manager = ModelManager.get_instance()
    metrics = manager.metrics

    if not metrics:
        raise HTTPException(status_code=503, detail={"code": "METRICS_UNAVAILABLE", "message": "Metrics not found"})

    # Load comparison if available
    comparison_data = None
    comp_path = EVALUATION_DIR / "model_comparison.json"
    if comp_path.exists():
        try:
            with open(comp_path, "r", encoding="utf-8") as f:
                comparison_data = json.load(f)
        except Exception:
            pass

    return MetricsResponse(
        accuracy=metrics.get("accuracy", 0.0),
        macro_precision=metrics.get("macro_precision", 0.0),
        macro_recall=metrics.get("macro_recall", 0.0),
        macro_f1=metrics.get("macro_f1", 0.0),
        weighted_f1=metrics.get("weighted_f1", 0.0),
        per_class=metrics.get("per_class", {}),
        confusion_matrix=metrics.get("confusion_matrix", []),
        model_comparison=comparison_data
    )
