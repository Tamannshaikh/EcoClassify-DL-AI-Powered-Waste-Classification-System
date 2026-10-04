"""
Google Places API (New) Provider Implementation.

Uses Places API (New) Text Search with strict field masking,
timeout bounds, and geodesic distance sorting.
"""
import logging
import httpx
from typing import List, Optional
from backend.app.schemas import RecyclingCenterItem
from backend.app.services.recycling.constants import WASTE_SEARCH_TEMPLATES
from backend.app.services.recycling.distance import haversine_distance_km
from backend.app.services.recycling.providers.base import BaseRecyclingProvider

logger = logging.getLogger("recycling.google_places")


class GooglePlacesProvider(BaseRecyclingProvider):
    """
    Google Places API (New) integration provider.
    """

    SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 4.0):
        self.api_key = api_key or ""
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "google_places"

    async def search(
        self,
        latitude: float,
        longitude: float,
        waste_type: str,
        radius_km: float,
        limit: int,
    ) -> List[RecyclingCenterItem]:
        if not self.api_key:
            raise ValueError("Google Maps API key is not configured.")

        # Resolve search query templates for waste category
        templates = WASTE_SEARCH_TEMPLATES.get(
            waste_type, ["recycling center", "waste collection center"]
        )
        query = templates[0]

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.location,places.googleMapsUri,places.nationalPhoneNumber,"
                "places.regularOpeningHours"
            ),
        }

        payload = {
            "textQuery": query,
            "locationBias": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": min(radius_km * 1000.0, 50000.0),
                }
            },
            "maxResultCount": min(limit, 20),
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.SEARCH_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        raw_places = data.get("places", [])
        results: List[RecyclingCenterItem] = []

        for place in raw_places:
            loc = place.get("location", {})
            dest_lat = loc.get("latitude")
            dest_lng = loc.get("longitude")

            if dest_lat is None or dest_lng is None:
                continue

            dist = haversine_distance_km(latitude, longitude, dest_lat, dest_lng)

            # Name and address extraction
            display_name = place.get("displayName", {}).get("text", "Recycling Center")
            address = place.get("formattedAddress", "Address unavailable")

            # Maps & Directions URLs
            maps_url = place.get("googleMapsUri") or (
                f"https://www.google.com/maps/search/?api=1&query={dest_lat},{dest_lng}"
            )
            directions_url = (
                f"https://www.google.com/maps/dir/?api=1"
                f"&origin={latitude},{longitude}"
                f"&destination={dest_lat},{dest_lng}"
                f"&travelmode=driving"
            )

            # Hours formatting
            opening_hours = None
            regular_hours = place.get("regularOpeningHours", {})
            if "weekdayDescriptions" in regular_hours and regular_hours["weekdayDescriptions"]:
                opening_hours = regular_hours["weekdayDescriptions"][0]

            phone = place.get("nationalPhoneNumber")

            item = RecyclingCenterItem(
                id=place.get("id", f"gp_{len(results)+1}"),
                name=display_name,
                address=address,
                latitude=dest_lat,
                longitude=dest_lng,
                distance_km=dist,
                maps_url=maps_url,
                directions_url=directions_url,
                phone=phone,
                opening_hours=opening_hours,
                waste_categories_handled=[waste_type],
                source="google_places",
            )
            results.append(item)

        # Sort strictly ascending by distance
        results.sort(key=lambda x: x.distance_km)

        return results[:limit]
