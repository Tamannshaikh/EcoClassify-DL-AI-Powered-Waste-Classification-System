"""
Unit and Integration Tests for Smart Recycling Center Finder.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.recycling.distance import haversine_distance_km
from backend.app.services.recycling.constants import VALID_WASTE_TYPES
from backend.app.services.recycling.providers.curated import CuratedRecyclingProvider
from backend.app.services.recycling.providers.google_places import GooglePlacesProvider
from backend.app.services.recycling.service import RecyclingCenterService
from backend.app.schemas import RecyclingSearchRequest

client = TestClient(app)


# 1. Haversine Distance Unit Test
def test_haversine_distance_calculation():
    # Distance between Mumbai CST (18.9400, 72.8353) and Vashi (19.0770, 72.9980) ~22.8 km
    dist = haversine_distance_km(18.9400, 72.8353, 19.0770, 72.9980)
    assert 20.0 < dist < 26.0
    # Zero distance for identical points
    assert haversine_distance_km(19.0760, 72.8777, 19.0760, 72.8777) == 0.0


# 2. Valid Search for Core Classes (Plastic, E-Waste, Biodegradable)
def test_search_valid_plastic():
    payload = {
        "waste_type": "plastic",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "radius_km": 25.0,
        "limit": 5,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["waste_type"] == "plastic"
    assert len(data["results"]) > 0
    assert data["results"][0]["distance_km"] <= 25.0
    assert "https://www.google.com/maps/dir/" in data["results"][0]["directions_url"]


def test_search_valid_e_waste():
    payload = {
        "waste_type": "e_waste",
        "latitude": 19.0772,
        "longitude": 72.9981,
        "radius_km": 15.0,
        "limit": 5,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["waste_type"] == "e_waste"
    assert len(data["results"]) > 0
    assert "e_waste" in data["results"][0]["waste_categories_handled"]


def test_search_valid_biodegradable():
    payload = {
        "waste_type": "biodegradable",
        "latitude": 19.0834,
        "longitude": 73.0162,
        "radius_km": 10.0,
        "limit": 5,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["waste_type"] == "biodegradable"
    assert len(data["results"]) > 0


# 3. Test All 8 Supported Production Classes
@pytest.mark.parametrize("waste_class", sorted(VALID_WASTE_TYPES))
def test_all_8_waste_classes_accepted(waste_class):
    payload = {
        "waste_type": waste_class,
        "latitude": 19.0760,
        "longitude": 72.8777,
        "radius_km": 50.0,
        "limit": 5,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["waste_type"] == waste_class


# 4. Input Validation & Error Handling Tests
def test_invalid_waste_type_rejected():
    payload = {
        "waste_type": "unsupported_category",
        "latitude": 19.0760,
        "longitude": 72.8777,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 422


def test_invalid_latitude_rejected():
    payload = {
        "waste_type": "plastic",
        "latitude": 95.0,  # Invalid (>90)
        "longitude": 72.8777,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 422


def test_invalid_longitude_rejected():
    payload = {
        "waste_type": "plastic",
        "latitude": 19.0760,
        "longitude": -195.0,  # Invalid (<-180)
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 422


def test_invalid_radius_bounds_rejected():
    # Negative radius
    res1 = client.post(
        "/api/v1/recycling/search",
        json={"waste_type": "plastic", "latitude": 19.0, "longitude": 72.0, "radius_km": -5.0},
    )
    assert res1.status_code == 422

    # Zero radius
    res2 = client.post(
        "/api/v1/recycling/search",
        json={"waste_type": "plastic", "latitude": 19.0, "longitude": 72.0, "radius_km": 0.0},
    )
    assert res2.status_code == 422

    # Excessively large radius (> 50 km)
    res3 = client.post(
        "/api/v1/recycling/search",
        json={"waste_type": "plastic", "latitude": 19.0, "longitude": 72.0, "radius_km": 150.0},
    )
    assert res3.status_code == 422


def test_invalid_limit_bounds_rejected():
    # Limit > 20
    res = client.post(
        "/api/v1/recycling/search",
        json={"waste_type": "plastic", "latitude": 19.0, "longitude": 72.0, "limit": 50},
    )
    assert res.status_code == 422


# 5. Distance Sorting Verification (Nearest Center First)
def test_distance_sorting_ascending():
    payload = {
        "waste_type": "plastic",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "radius_km": 50.0,
        "limit": 10,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    results = response.json()["results"]
    distances = [r["distance_km"] for r in results]
    assert distances == sorted(distances)


# 6. Empty Results Handling
def test_empty_results_handling():
    # Query point in remote ocean coordinates where no regional centers exist
    payload = {
        "waste_type": "e_waste",
        "latitude": 0.0,
        "longitude": 0.0,
        "radius_km": 5.0,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_results"
    assert data["total_results"] == 0
    assert data["results"] == []
    assert "No recycling centers were found" in data["message"]


# 7. Curated Provider Direct Unit Test
@pytest.mark.asyncio
async def test_curated_provider_direct():
    provider = CuratedRecyclingProvider()
    results = await provider.search(
        latitude=19.0772,
        longitude=72.9981,
        waste_type="e_waste",
        radius_km=20.0,
        limit=5,
    )
    assert len(results) > 0
    assert results[0].source == "curated"
    assert results[0].distance_km >= 0.0


# 8. Google Provider Mocked Integration & Error Handling
@pytest.mark.asyncio
async def test_google_provider_mocked_success():
    provider = GooglePlacesProvider(api_key="test_dummy_key")
    mock_payload = {
        "places": [
            {
                "id": "mock_p1",
                "displayName": {"text": "Mock Live E-Waste Center"},
                "formattedAddress": "123 Green Way, Mumbai",
                "location": {"latitude": 19.0800, "longitude": 72.8800},
                "googleMapsUri": "https://maps.google.com/?cid=123",
                "nationalPhoneNumber": "022 1234 5678",
                "regularOpeningHours": {"weekdayDescriptions": ["Mon-Fri: 9am-5pm"]},
            }
        ]
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_payload
        mock_response.raise_for_status = lambda: None
        mock_post.return_value = mock_response

        results = await provider.search(
            latitude=19.0760,
            longitude=72.8777,
            waste_type="e_waste",
            radius_km=10.0,
            limit=5,
        )

        assert len(results) == 1
        assert results[0].name == "Mock Live E-Waste Center"
        assert results[0].source == "google_places"
        assert results[0].phone == "022 1234 5678"


@pytest.mark.asyncio
async def test_service_google_timeout_fallback():
    # When Google provider fails or times out, service falls back to Curated
    service = RecyclingCenterService(
        preferred_provider="google", google_api_key="test_dummy_key"
    )

    with patch.object(
        service.google_provider, "search", side_effect=Exception("Connection Timeout")
    ):
        req = RecyclingSearchRequest(
            waste_type="e_waste",
            latitude=19.0772,
            longitude=72.9981,
            radius_km=25.0,
            limit=5,
        )
        response = await service.search(req)

        assert response.provider == "curated_fallback"
        assert len(response.results) > 0
        assert "Live provider unavailable" in response.message


# 9. Directions and Map URL Format Verification
def test_directions_url_format():
    payload = {
        "waste_type": "metal",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "radius_km": 30.0,
        "limit": 2,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert "origin=19.076,72.8777" in item["directions_url"]
    assert "destination=" in item["directions_url"]
    assert "travelmode=driving" in item["directions_url"]
    assert item["maps_url"].startswith("https://")


# 10. No Secret Key in Response Payload
def test_no_secret_keys_in_payload():
    payload = {
        "waste_type": "plastic",
        "latitude": 19.0760,
        "longitude": 72.8777,
    }
    response = client.post("/api/v1/recycling/search", json=payload)
    text = response.text
    assert "api_key" not in text.lower()
    assert "secret" not in text.lower()
