"""
Dataset Information and Metadata Routes.
"""
from fastapi import APIRouter
from backend.app.schemas import DatasetInfoResponse, ClassDistributionItem
from backend.app.config import PROJECT_ROOT

router = APIRouter(prefix="/dataset", tags=["Dataset"])

DATASET_METADATA = {
    "dataset_name": "EcoClassify 8-Class Unified Dataset (TrashNet + EWaste + BDWaste)",
    "dataset_version": "8class-v1.0",
    "total_images": 3427,
    "classes": [
        "biodegradable",
        "cardboard",
        "e_waste",
        "glass",
        "metal",
        "paper",
        "plastic",
        "trash"
    ],
    "class_distribution": [
        {"class_name": "biodegradable", "count": 450, "percentage": 13.13},
        {"class_name": "cardboard", "count": 403, "percentage": 11.76},
        {"class_name": "e_waste", "count": 450, "percentage": 13.13},
        {"class_name": "glass", "count": 501, "percentage": 14.62},
        {"class_name": "metal", "count": 410, "percentage": 11.96},
        {"class_name": "paper", "count": 594, "percentage": 17.33},
        {"class_name": "plastic", "count": 482, "percentage": 14.07},
        {"class_name": "trash", "count": 137, "percentage": 4.00}
    ],
    "splits": {
        "train": 2399,
        "val": 515,
        "test": 513,
        "total": 3427
    },
    "dimensions": "224 x 224 (Standardized RGB)"
}


@router.get("/info", response_model=DatasetInfoResponse)
async def get_dataset_info():
    """Returns dataset metadata, image counts, and class distributions."""
    return DatasetInfoResponse(
        dataset_name=DATASET_METADATA["dataset_name"],
        total_images=DATASET_METADATA["total_images"],
        classes=DATASET_METADATA["classes"],
        class_distribution=[
            ClassDistributionItem(**item) for item in DATASET_METADATA["class_distribution"]
        ],
        splits=DATASET_METADATA["splits"],
        dimensions=DATASET_METADATA["dimensions"]
    )


@router.get("/classes")
async def get_dataset_classes():
    """Returns the list of 6 waste classes and counts."""
    return {
        "classes": DATASET_METADATA["classes"],
        "counts": {item["class_name"]: item["count"] for item in DATASET_METADATA["class_distribution"]},
        "total": DATASET_METADATA["total_images"]
    }
