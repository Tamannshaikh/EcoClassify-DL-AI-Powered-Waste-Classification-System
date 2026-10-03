"""
Dataset Information and Metadata Routes.
"""
from fastapi import APIRouter
from backend.app.schemas import DatasetInfoResponse, ClassDistributionItem
from backend.app.config import PROJECT_ROOT

router = APIRouter(prefix="/dataset", tags=["Dataset"])

DATASET_METADATA = {
    "dataset_name": "TrashNet (Yang & Thung, Stanford)",
    "total_images": 2527,
    "classes": ["cardboard", "glass", "metal", "paper", "plastic", "trash"],
    "class_distribution": [
        {"class_name": "cardboard", "count": 403, "percentage": 15.95},
        {"class_name": "glass", "count": 501, "percentage": 19.83},
        {"class_name": "metal", "count": 410, "percentage": 16.22},
        {"class_name": "paper", "count": 594, "percentage": 23.51},
        {"class_name": "plastic", "count": 482, "percentage": 19.07},
        {"class_name": "trash", "count": 137, "percentage": 5.42}
    ],
    "splits": {
        "train": 1769,
        "val": 379,
        "test": 379,
        "total": 2527
    },
    "dimensions": "512 x 384 (100% uniform RGB)"
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
