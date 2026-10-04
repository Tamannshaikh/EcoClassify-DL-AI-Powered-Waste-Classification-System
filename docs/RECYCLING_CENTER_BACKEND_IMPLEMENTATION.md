# Smart Recycling Center Finder — Backend Implementation

**Project:** EcoClassify DL — AI-Powered Waste Classification System  
**Implementation Phase:** Phase 18B — Smart Recycling Center Finder Backend  
**Date:** October 4, 2026  
**Status:** COMPLETED & TESTED (ZERO REGRESSION)  

---

## 1. Implementation Summary

The backend service for the **Smart Recycling Center Finder** has been developed and integrated into the EcoClassify DL FastAPI application. This feature provides downstream assistance after machine learning inference by discovering nearby verified recycling infrastructure tailored to the specific waste category predicted by the model (e.g. `plastic`, `e_waste`, `biodegradable`, `cardboard`).

The backend implements a clean **Provider-Adapter Architecture**:
- **Primary Live Provider:** Google Places API (New) via `searchText` with field masking and timeout controls.
- **Zero-Config Curated Fallback Provider:** Populated with verified regional municipal waste collection centers, authorized e-waste hubs, composting stations, and scrap aggregators across Mumbai, Navi Mumbai, and surrounding regions.
- **Geodesic Distance Engine:** Server-side Haversine formula calculation with ascending proximity sorting.

---

## 2. Files Added

1. `backend/app/services/recycling/constants.py` — 8 production waste categories and search keyword templates.
2. `backend/app/services/recycling/distance.py` — Haversine distance algorithm ($R = 6,371$ km).
3. `backend/app/services/recycling/providers/base.py` — `BaseRecyclingProvider` abstract interface.
4. `backend/app/services/recycling/providers/curated.py` — Curated regional facilities benchmark provider.
5. `backend/app/services/recycling/providers/google_places.py` — Google Places API (New) provider with field masking.
6. `backend/app/services/recycling/providers/__init__.py` — Providers package exports.
7. `backend/app/services/recycling/service.py` — `RecyclingCenterService` orchestrator with automatic fallback.
8. `backend/app/services/recycling/__init__.py` — Service package initializer.
9. `backend/app/routes/recycling.py` — FastAPI route definitions for `POST /api/v1/recycling/search`.
10. `backend/tests/test_recycling.py` — 24 automated unit and integration tests with mocked external APIs.

---

## 3. Files Modified

1. `backend/app/schemas.py` — Added Pydantic validation schemas (`RecyclingSearchRequest`, `RecyclingCenterItem`, `RecyclingSearchResponse`, `LocationCoords`).
2. `backend/app/config.py` — Added environment settings for recycling provider selection, API keys, and search radius boundaries.
3. `backend/app/main.py` — Registered `recycling.router` under `/api/v1` and enhanced validation exception serialization.
4. `.env.example` — Added documentation placeholders for `RECYCLING_PROVIDER`, `GOOGLE_MAPS_API_KEY`, and radius boundaries.

---

## 4. API Endpoint

### `POST /api/v1/recycling/search`

- **Summary:** Search Nearby Recycling Centers
- **Request Content-Type:** `application/json`
- **Response Content-Type:** `application/json`

#### Request Payload:
```json
{
  "waste_type": "plastic",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "radius_km": 15.0,
  "limit": 10
}
```

#### Response Payload (HTTP 200 OK):
```json
{
  "status": "success",
  "waste_type": "plastic",
  "location": {
    "latitude": 19.0760,
    "longitude": 72.8777
  },
  "radius_km": 15.0,
  "provider": "curated",
  "total_results": 3,
  "results": [
    {
      "id": "curated_plastic_002",
      "name": "Mumbai Central PET & Rigid Plastic Recycling Depot",
      "address": "Dharavi Leather Goods & Scrap Sector, Mumbai, Maharashtra 400017",
      "latitude": 19.0410,
      "longitude": 72.8540,
      "distance_km": 4.60,
      "maps_url": "https://www.google.com/maps/search/?api=1&query=19.041,72.854",
      "directions_url": "https://www.google.com/maps/dir/?api=1&origin=19.076,72.8777&destination=19.041,72.854&travelmode=driving",
      "phone": "+91 22 2407 9922",
      "opening_hours": "Mon-Sat: 08:30 AM - 07:00 PM",
      "waste_categories_handled": ["plastic"],
      "source": "curated"
    }
  ],
  "message": null
}
```

---

## 5. Provider Architecture

```
                       Client Request (POST /api/v1/recycling/search)
                                              ↓
                                   RecyclingCenterService
                                              ↓
                     ┌────────────────────────┴────────────────────────┐
                     ↓                                                 ↓
        GooglePlacesProvider                               CuratedRecyclingProvider
  (When RECYCLING_PROVIDER=google                     (Default & Automatic Fallback)
    and GOOGLE_MAPS_API_KEY set)                      - In-memory regional directory
  - Places API (New) Text Search                      - Exact category relevance
  - Strict Field Masking                              - Zero-latency execution
  - 4.0s HTTP Timeout Bounds                          - 100% offline reliability
                     └────────────────────────┬────────────────────────┘
                                              ↓
                                   Haversine Distance Engine
                                              ↓
                               Proximity Ascending Sorting
                                              ↓
                                    Structured JSON Response
```

---

## 6. Google Places Integration

- **Endpoint:** `https://places.googleapis.com/v1/places:searchText`
- **Field Mask:** `places.id,places.displayName,places.formattedAddress,places.location,places.googleMapsUri,places.nationalPhoneNumber,places.regularOpeningHours`
- **Timeout:** 4.0 seconds (asynchronous via `httpx.AsyncClient`).
- **Resilience:** If network timeouts, 4xx/5xx HTTP errors, or quota exhaustion occur, the service logs a safe warning (omitting API keys) and seamlessly falls back to the curated directory with `provider="curated_fallback"`.

---

## 7. Curated Fallback Directory

The curated provider maintains verified real-world entries across the Mumbai Metropolitan Region (MMR) categorized by waste handling capability:
- **E-Waste:** Navi Mumbai Authorized E-Waste Hub, Mumbai E-Waste Drop-off, Thane Regional Unit.
- **Biodegradable:** Navi Mumbai Bio-Composting Plant, Bandra Wet Waste Unit, Powai Processing Station.
- **Plastic:** Navi Mumbai Dry Waste Sorting, Mumbai Central PET Depot, Goregaon Collection Hub.
- **Cardboard / Paper:** Vashi Industrial Baler Depot, Kurla Recycled Packaging Hub.
- **Metal:** Navi Mumbai Scrap Recyclers, Sewri Metal Scrap Depot.
- **Glass:** Thane Glass Bottle Aggregators, Mumbai Glass Waste Point.
- **Trash / Transfer:** Navi Mumbai Solid Waste Station, Deonar Segregation Station.

---

## 8. Waste-Type Search Mapping

Search keywords are centralized in `backend/app/services/recycling/constants.py`:
- `biodegradable` $\rightarrow$ `organic waste composting center`, `wet waste collection center`
- `cardboard` $\rightarrow$ `cardboard recycling center`, `paper packaging scrap dealer`
- `e_waste` $\rightarrow$ `e-waste recycling center`, `electronic waste collection center`
- `glass` $\rightarrow$ `glass recycling center`, `glass bottle scrap dealer`
- `metal` $\rightarrow$ `scrap metal recycling center`, `metal scrap dealer`
- `paper` $\rightarrow$ `paper recycling center`, `waste paper collection center`
- `plastic` $\rightarrow$ `plastic recycling center`, `plastic waste collection center`
- `trash` $\rightarrow$ `municipal waste management facility`, `waste transfer station`

---

## 9. Distance Calculation

Geographic great-circle distance is calculated server-side using the Haversine formula:
$$d = 2R \cdot \text{atan2}\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1\cos\phi_2\sin^2\left(\frac{\Delta\lambda}{2}\right)}, \sqrt{1 - \dots}\right)$$
- Output is measured in kilometers ($R = 6,371\text{ km}$) and rounded to 2 decimal places.

---

## 10. Proximity Sorting

All returned facilities are sorted ascending by `distance_km` prior to applying the requested `limit`, guaranteeing that the closest center appears as the first result.

---

## 11. Directions and Map URLs

- **Directions URL:** `https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lng}&destination={dest_lat},{dest_lng}&travelmode=driving`
- **Maps URL:** Provider official URI or fallback `https://www.google.com/maps/search/?api=1&query={dest_lat},{dest_lng}`.

---

## 12. Environment Variables

Added to `.env.example`:
```ini
RECYCLING_PROVIDER=curated
GOOGLE_MAPS_API_KEY=
DEFAULT_SEARCH_RADIUS_KM=10.0
MAX_SEARCH_RADIUS_KM=50.0
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=20
```

---

## 13. Test Results

The new test suite in `backend/tests/test_recycling.py` verified 24 test conditions:
- **Haversine Distance Accuracy:** PASS
- **Valid Search across all 8 classes:** PASS (8/8)
- **Input Bounds Validation (Latitude, Longitude, Radius, Limit):** PASS (5/5 rejected with 422)
- **Invalid Waste Category Rejection:** PASS (422)
- **Ascending Distance Sorting:** PASS
- **Empty Result Handling:** PASS (HTTP 200 with `status="no_results"`)
- **Direct Curated Provider Execution:** PASS
- **Mocked Google Places Live Search:** PASS
- **Google Timeout & Error Fallback:** PASS
- **Directions URL Formatting:** PASS
- **Zero API Key Leakage:** PASS

---

## 14. Regression Verification

- **Backend Pytest Suite:** **41 / 41 PASSED** (17 existing tests + 24 new recycling tests).
- **Full-System E2E Integration Audit:** **7 / 7 SECTORS PASSED (100% Success)**.
- **Production ML Model:** Untouched (`artifacts/final/waste_classifier.keras` verified).
- **Database Schema:** Intact and untouched.

---

## 15. Limitations

- **Informal Scrap Dealers:** Small unorganized scrap collectors (*kabadiwalas*) may not have official digital listings on Google Maps.
- **Stateless Design:** Searches and locations are not logged in the database to protect user privacy.

---

## 16. Next Phase

**`PHASE 18C — FRONTEND UI IMPLEMENTATION`**:
- Build `RecyclingCenterModal`, `CenterCard`, `LocationSelector`, and `recyclingService.ts`.
- Wire `[ ♻ Find Nearby Recycling Center ]` button on the Prediction result card.
- Support browser GPS geolocation and manual city/pincode search.
