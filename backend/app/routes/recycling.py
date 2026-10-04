"""
Recycling Center Finder API Routes.
"""
import logging
from fastapi import APIRouter, status
from backend.app.config import RECYCLING_PROVIDER, GOOGLE_MAPS_API_KEY
from backend.app.schemas import (
    RecyclingSearchRequest,
    RecyclingSearchResponse,
)
from backend.app.services.recycling.service import RecyclingCenterService

logger = logging.getLogger("routes.recycling")
router = APIRouter(tags=["Recycling"])


@router.post(
    "/recycling/search",
    response_model=RecyclingSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Nearby Recycling Centers",
    description=(
        "Search for verified recycling centers, e-waste drop-off hubs, composting units, "
        "and municipal collection points matching the specified waste category. "
        "Results are sorted ascending by approximate geographic (Haversine) distance."
    ),
)
async def search_recycling_centers(request: RecyclingSearchRequest):
    """
    Search for recycling facilities near given coordinates for a specified waste class.
    """
    service = RecyclingCenterService(
        preferred_provider=RECYCLING_PROVIDER,
        google_api_key=GOOGLE_MAPS_API_KEY,
    )
    return await service.search(request)
