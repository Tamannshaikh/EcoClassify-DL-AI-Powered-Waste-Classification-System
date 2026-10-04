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


# ==========================================
# Recycling Center Finder Schemas
# ==========================================
from backend.app.services.recycling.constants import VALID_WASTE_TYPES
from pydantic import field_validator


class LocationCoords(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (-90 to +90)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (-180 to +180)")


class RecyclingSearchRequest(BaseModel):
    waste_type: str = Field(
        ...,
        description="One of the 8 production waste categories (e.g. plastic, e_waste, biodegradable)",
        json_schema_extra={"example": "plastic"}
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="User origin latitude (-90.0 to 90.0)",
        json_schema_extra={"example": 19.0760}
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="User origin longitude (-180.0 to 180.0)",
        json_schema_extra={"example": 72.8777}
    )
    radius_km: float = Field(
        default=10.0,
        ge=1.0,
        le=50.0,
        description="Search radius in kilometers (1.0 to 50.0)",
        json_schema_extra={"example": 10.0}
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Maximum number of results to return (1 to 20)",
        json_schema_extra={"example": 10}
    )

    @field_validator("waste_type")
    @classmethod
    def validate_waste_type(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in VALID_WASTE_TYPES:
            raise ValueError(
                f"Invalid waste type '{v}'. Supported types are: {', '.join(sorted(VALID_WASTE_TYPES))}"
            )
        return cleaned


class RecyclingCenterItem(BaseModel):
    id: str = Field(..., description="Unique identifier for the recycling facility")
    name: str = Field(..., description="Facility name")
    address: str = Field(..., description="Formatted postal address")
    latitude: float = Field(..., description="Facility latitude coordinate")
    longitude: float = Field(..., description="Facility longitude coordinate")
    distance_km: float = Field(..., description="Approximate straight-line distance in kilometers")
    maps_url: str = Field(..., description="Web URL to view the place on Google Maps")
    directions_url: str = Field(..., description="Universal deep link for turn-by-turn navigation")
    phone: Optional[str] = Field(None, description="Contact phone number if available")
    opening_hours: Optional[str] = Field(None, description="Operating hours summary if available")
    waste_categories_handled: Optional[List[str]] = Field(
        default=None,
        description="List of handled waste types if known"
    )
    source: str = Field(..., description="Provider source identifier (e.g. google_places, curated)")


class RecyclingSearchResponse(BaseModel):
    status: str = Field(..., description="Search status ('success' or 'no_results')")
    waste_type: str = Field(..., description="Queried waste category")
    location: LocationCoords = Field(..., description="User search origin coordinates")
    radius_km: float = Field(..., description="Search radius in kilometers applied")
    provider: str = Field(..., description="Active search provider ('google_places', 'curated', 'curated_fallback')")
    total_results: int = Field(..., description="Count of centers returned")
    results: List[RecyclingCenterItem] = Field(default_factory=list, description="Distance-sorted recycling centers (nearest first)")
    message: Optional[str] = Field(None, description="Informational message or guidance")
