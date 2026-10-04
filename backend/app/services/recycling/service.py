"""
Recycling Center Finder Orchestration Service.

Manages provider selection, geodesic search dispatch, fallback handling,
and structured response construction.
"""
import logging
from typing import Optional
from backend.app.schemas import (
    LocationCoords,
    RecyclingSearchRequest,
    RecyclingSearchResponse,
)
from backend.app.services.recycling.providers.curated import CuratedRecyclingProvider
from backend.app.services.recycling.providers.google_places import GooglePlacesProvider

logger = logging.getLogger("recycling.service")


class RecyclingCenterService:
    """
    Orchestration service with automatic live provider fallback.
    """

    def __init__(
        self,
        preferred_provider: str = "curated",
        google_api_key: Optional[str] = None,
    ):
        self.preferred_provider = preferred_provider.lower().strip()
        self.google_api_key = google_api_key or ""
        self.curated_provider = CuratedRecyclingProvider()
        self.google_provider = (
            GooglePlacesProvider(api_key=self.google_api_key)
            if self.google_api_key
            else None
        )

    async def search(self, request: RecyclingSearchRequest) -> RecyclingSearchResponse:
        """
        Execute proximity search across configured providers with seamless fallback.
        """
        results = []
        active_provider = self.preferred_provider
        message = None

        # Attempt Google Places if requested and configured
        if self.preferred_provider == "google" and self.google_provider:
            try:
                results = await self.google_provider.search(
                    latitude=request.latitude,
                    longitude=request.longitude,
                    waste_type=request.waste_type,
                    radius_km=request.radius_km,
                    limit=request.limit,
                )
                active_provider = "google_places"
            except Exception as exc:
                logger.warning(
                    f"Google Places search encountered an error ({type(exc).__name__}). Falling back to curated directory."
                )
                results = await self.curated_provider.search(
                    latitude=request.latitude,
                    longitude=request.longitude,
                    waste_type=request.waste_type,
                    radius_km=request.radius_km,
                    limit=request.limit,
                )
                active_provider = "curated_fallback"
                message = "Live provider unavailable. Showing curated regional facilities."
        else:
            # Default curated provider
            results = await self.curated_provider.search(
                latitude=request.latitude,
                longitude=request.longitude,
                waste_type=request.waste_type,
                radius_km=request.radius_km,
                limit=request.limit,
            )
            active_provider = "curated"

        # Construct status and final message
        status_str = "success" if results else "no_results"
        if not results and not message:
            message = f"No recycling centers were found within {request.radius_km:.1f} km. Try expanding your search radius."

        return RecyclingSearchResponse(
            status=status_str,
            waste_type=request.waste_type,
            location=LocationCoords(
                latitude=request.latitude, longitude=request.longitude
            ),
            radius_km=request.radius_km,
            provider=active_provider,
            total_results=len(results),
            results=results,
            message=message,
        )
