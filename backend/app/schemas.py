"""
Pydantic Schemas for API Request and Response Validation.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    model_loaded: bool = Field(..., json_schema_extra={"example": True})
    model_name: str = Field(..., json_schema_extra={"example": "MobileNetV2 (Transfer Learning)"})
    model_version: str = Field(..., json_schema_extra={"example": "v1.0"})
    classes: List[str]


class ModelInfoResponse(BaseModel):
    model_name: str
    model_architecture: str
    framework: str
    input_shape: List[int]
    classes: List[str]
    num_classes: int
    total_parameters: int
    test_accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_f1: float
    training_config: Dict[str, Any]
    cpu_inference_benchmark: Optional[Dict[str, Any]] = None


class PerClassMetric(BaseModel):
    precision: float
    recall: float
    f1_score: float
    support: int


class MetricsResponse(BaseModel):
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_f1: float
    per_class: Dict[str, PerClassMetric]
    confusion_matrix: List[List[int]]
    model_comparison: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    prediction_id: str
    filename: str
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    inference_time_ms: float
    model_version: str
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    gradcam_base64: Optional[str] = None


class PredictionHistoryItem(BaseModel):
    id: int
    prediction_id: str
    filename: str
    original_filename: str
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    inference_time_ms: float
    model_version: str
    gradcam_generated: bool
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    created_at: str


class PredictionHistoryListResponse(BaseModel):
    total: int
    predictions: List[PredictionHistoryItem]


class ClassDistributionItem(BaseModel):
    class_name: str
    count: int
    percentage: float


class DatasetInfoResponse(BaseModel):
    dataset_name: str
    total_images: int
    classes: List[str]
    class_distribution: List[ClassDistributionItem]
    splits: Dict[str, int]
    dimensions: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    detail: ErrorDetail
