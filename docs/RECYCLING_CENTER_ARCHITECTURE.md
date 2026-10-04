# Smart Recycling Center Finder — Architecture Proposal

**Project:** EcoClassify DL — AI-Powered Waste Classification System  
**Feature Phase:** Phase 18A — Research & Architecture Design  
**Document Version:** v1.0.0-draft  
**Target Release:** v2.1.0-recycling  
**Author:** AI & Full-Stack Systems Architecture Team  
**Status:** PROPOSED & REVIEWED (NON-DESTRUCTIVE / PRE-IMPLEMENTATION)  

---

## 1. Feature Objective

The **Smart Recycling Center Finder** is an intelligent downstream extension to the EcoClassify DL system. Following the automatic deep learning classification of an uploaded waste item (e.g. `plastic`, `e_waste`, `biodegradable`), the user is provided with a contextual action button:

$$\text{Prediction Result Card} \longrightarrow \mathbf{[ \text{ ♻ Find Nearby Recycling Center } ]}$$

The system identifies verified, category-appropriate municipal waste collection points, authorized e-waste drop-off facilities, composting stations, and scrap recyclers located nearest to the user's geographic location. The finder ranks results in ascending order of proximity (nearest first), provides approximate distance metrics, and delivers one-click deep links for visual map inspection and GPS navigation.

---

## 2. User Flow

```
+-------------------------------------------------------------------------------+
| 1. Waste Prediction Flow                                                     |
| User uploads waste image -> MobileNetV2 classifies as 'e_waste' (98.4%)      |
| Result Card displays: [ ♻ Find Nearby Recycling Center ]                      |
+-------------------------------------------------------------------------------+
                                       ↓ (Click Action)
+-------------------------------------------------------------------------------+
| 2. Recycling Center Finder Interface                                          |
| Modal / Dedicated Drawer opens with AI-predicted class 'e_waste' preselected |
| User retains option to change waste category via an 8-class dropdown          |
+-------------------------------------------------------------------------------+
                                       ↓
+-------------------------------------------------------------------------------+
| 3. Location Resolution                                                       |
| Option A: [ 📍 Use My Current Location ] (Browser Geolocation API)           |
| Option B: [ 🔍 Enter Manual Location ] (Area / City / Pincode / Landmark)    |
+-------------------------------------------------------------------------------+
                                       ↓
+-------------------------------------------------------------------------------+
| 4. Backend Query & Distance Sorting                                          |
| React sends POST /api/v1/recycling/search to FastAPI backend                  |
| Backend proxies query to Places Engine + applies category-tailored keywords  |
| Backend computes Haversine distance from origin to all returned centers       |
| Centers sorted ascending: Nearest Center first                                |
+-------------------------------------------------------------------------------+
                                       ↓
+-------------------------------------------------------------------------------+
| 5. Proximity Ranked Results List                                             |
| 1. Navi Mumbai E-Waste Hub — 1.2 km away [View on Map] [Get Directions]       |
| 2. Vashi Electronics Recycling — 2.4 km away [View on Map] [Get Directions]   |
| 3. Thane District Scrap & E-Waste Point — 4.8 km away                         |
+-------------------------------------------------------------------------------+
```

---

## 3. Supported Waste Types

The finder natively maps to all **8 production classes** of the EcoClassify DL system:

| Waste Category | AI Predicted Class | Specialized Center Search Keywords | Primary Facility Archetype |
| :--- | :--- | :--- | :--- |
| **Biodegradable** | `biodegradable` | `organic waste composting center OR wet waste collection OR bio-methanation plant` | Municipal composting facility, community gardens, organic waste processors |
| **Cardboard** | `cardboard` | `cardboard recycling center OR paper packaging scrap recycler` | Paper mill collection points, authorized cardboard balers, paper recycling hubs |
| **E-Waste** | `e_waste` | `e-waste recycling center OR electronic waste drop-off OR authorized e-waste dismantler` | Certified e-waste collection bins, electronic recyclers, authorized drop-off kiosks |
| **Glass** | `glass` | `glass recycling facility OR glass bottle scrap dealer` | Glass manufacturing cullet collectors, municipal glass collection bays |
| **Metal** | `metal` | `scrap metal recycling center OR aluminum can collection OR scrap dealer` | Metal scrap aggregators, aluminum recycling depots, kabadiwala networks |
| **Paper** | `paper` | `paper recycling center OR waste paper collection unit` | Shredding services, paper recyclers, municipal dry waste sorting centers |
| **Plastic** | `plastic` | `plastic recycling center OR plastic waste collection facility OR dry waste center` | Plastic scrap recyclers, PET collection centers, municipal dry waste sorting centers |
| **Trash** | `trash` | `municipal waste management center OR waste transfer station OR dry waste collection` | Local municipal ward waste transfer stations, municipal collection points |

---

## 4. Location Strategy

The system accommodates two distinct user location modes without enforcing mandatory tracking:

### Mode A: Browser Geolocation API (`navigator.geolocation`)
1. User clicks **"Use My Current Location"**.
2. Browser displays native location permission prompt (`navigator.geolocation.getCurrentPosition()`).
3. If allowed, client retrieves high-precision WGS84 coordinates: `latitude` (float) and `longitude` (float).
4. Coordinates are transmitted directly in the search payload to the backend.
5. If permission is denied or times out, the UI gracefully falls back to Mode B with a non-intrusive prompt.

### Mode B: Manual Location Input (Geocoding Resolution)
1. User types an area, city, landmark, or Indian Postal Index Number (Pincode) into a text box:
   - Examples: `Vashi, Navi Mumbai`, `400703`, `Andheri East, Mumbai`, `Sector 17, Vashi`, `Thane West`.
2. The input is forwarded to the backend.
3. The backend resolves the text query into geographic coordinates using a Geocoding service (Google Geocoding API or OpenStreetMap Nominatim), or executes a direct Text Search query anchored to the specified location text.
4. Ensures full functionality for desktop users without GPS hardware or privacy-conscious users.

---

## 5. Provider Comparison

| Provider | Nearby Search | Distance Sorting | Map Deep Link | Directions Deep Link | API Key Required | Cost / Free Tier | India & Mumbai Coverage | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Google Places API (New)** | Excellent (`searchText`, `searchNearby`) | Supported (or via Haversine) | Native (`googleMapsUri`) | Native Google Maps URL | Yes (Google Cloud) | Pay-as-you-go with per-SKU monthly free allotments | **Highest (Extensive real-time coverage across Mumbai, Navi Mumbai, Thane, and Indian metros)** | **PRIMARY RECOMMENDED** |
| **OpenStreetMap / Overpass API** | Moderate (`amenity=recycling`) | Manual (Haversine) | OSM Link | External OSRM | No | 100% Free / Open Source | **Low / Sparse** (Informal scrap dealers & e-waste points rarely tagged in OSM in India) | **FALLBACK / DEMO ADAPTER** |
| **Mapbox Search API** | Good (`categorysearch`) | Manual (Haversine) | Mapbox Map | Mapbox Directions | Yes (Mapbox) | Free tier: 50,000 requests/month | Moderate (Strong POI coverage, but specialized Indian scrap/e-waste hubs weaker than Google) | Secondary Alternative |
| **TomTom Search API** | Moderate | Manual (Haversine) | TomTom Map | TomTom Routing | Yes (TomTom) | Free tier: 2,500 daily requests | Moderate (POI data lower density in residential Indian wards) | Secondary Alternative |

---

## 6. Recommended Provider & Architectural Pattern

### Primary Recommendation: **Google Places API (New) via Server-Side Proxy**

**Reasons:**
1. **Unrivaled Coverage in India:** Google Maps contains the most comprehensive database of authorized e-waste collection centers (e.g. Karo Sambhav, CPCB authorized drop-offs), municipal dry waste sorting centers (K-East, N-Ward, etc.), scrap recyclers (*raddiwalas* / metal dealers), and composting stations across Mumbai, Navi Mumbai, and surrounding regions.
2. **Rich Metadata:** Returns verified entity names, formatted addresses, precise latitude/longitude, business status, national phone numbers, operating hours, and canonical `googleMapsUri` links.
3. **Field Masking Cost Control:** Places API (New) supports `X-Goog-FieldMask` headers (e.g., `places.displayName,places.formattedAddress,places.location,places.googleMapsUri`), reducing API overhead and billing tier requirements.

### Architecture Pattern: **Pluggable Provider Adapter with Mock Fallback**
To ensure the project remains **100% functional in academic evaluation and offline environments** even if the evaluator has not configured a Google Cloud API key:
- **`GooglePlacesProvider`**: Active when `RECYCLING_PROVIDER=google` and `GOOGLE_MAPS_API_KEY` is set in `.env`.
- **`MockCuratedProvider`**: Active when `RECYCLING_PROVIDER=mock` or when no API key is provided. Returns verified real-world recycling centers across Mumbai / Navi Mumbai / Pune / Delhi benchmarks, guaranteeing immediate, zero-cost out-of-the-box evaluation.

---

## 7. Waste-Type Search Strategy

To prevent generic or irrelevant results, the backend translates the selected waste class into domain-targeted search queries:

```python
WASTE_SEARCH_TEMPLATES = {
    "biodegradable": ["organic waste composting center", "wet waste processing plant", "compost facility"],
    "cardboard": ["cardboard recycling center", "paper and packaging scrap dealer", "recycling center"],
    "e_waste": ["e-waste collection center", "electronic waste recycling facility", "e-waste drop off point"],
    "glass": ["glass recycling center", "scrap glass bottle collection point", "scrap dealer"],
    "metal": ["scrap metal recycling center", "metal scrap dealer", "aluminum recycling facility"],
    "paper": ["paper recycling center", "waste paper collection center", "scrap paper dealer"],
    "plastic": ["plastic recycling center", "plastic waste collection center", "dry waste sorting facility"],
    "trash": ["municipal dry waste collection center", "waste transfer station", "municipal waste facility"]
}
```

### Result Disclaimer & Transparency
Because municipal collection policies vary by municipal ward and center operational hours, the UI will prominently display:
> *"Search results are ranked by proximity and waste-category relevance. Please contact or verify accepted material guidelines with the facility prior to dropping off hazardous or bulky items."*

---

## 8. Distance Calculation Strategy

### Selected Approach: **Server-Side Haversine Formula with Ascending Ranking**

1. **Formula:**
   The great-circle distance $d$ between the user coordinates $(\phi_1, \lambda_1)$ and the recycling center $(\phi_2, \lambda_2)$ is computed on the backend using the Haversine formula:
   $$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
   $$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$
   $$d = R \cdot c \quad (\text{where Earth radius } R = 6,371\text{ km})$$

2. **Why Haversine for Initial Sorting?**
   - **Zero Latency & Zero Cost:** Computes in $<0.1$ ms with zero external API calls or routing fees.
   - **Labeling Accuracy:** Clearly formatted and displayed in the UI as `~1.4 km away (approx. straight-line)`.
   - **Road Routing Handoff:** Accurate turn-by-turn driving distance and live traffic conditions are seamlessly delegated to the user's native mapping application when clicking **"Get Directions"**.

---

## 9. Directions & Map Strategy

Rather than requiring an expensive embedded Google Maps JavaScript SDK (which increases bundle size and API costs), the system generates standardized, universal deep links:

### 1. View on Map Link:
```
https://www.google.com/maps/search/?api=1&query={destination_latitude},{destination_longitude}&query_place_id={place_id}
```
*Directly opens the facility card in Google Maps / Apple Maps / OpenStreetMap.*

### 2. Get Directions Link:
```
https://www.google.com/maps/dir/?api=1&origin={user_latitude},{user_longitude}&destination={dest_latitude},{dest_longitude}&travelmode=driving
```
*Launches turn-by-turn live navigation from the user's current or selected origin to the recycling center.*

---

## 10. Backend Architecture

The feature will reside within dedicated, modular backend components without altering existing prediction routes:

```
backend/app/
├── services/
│   └── recycling_finder/
│       ├── __init__.py
│       ├── base_provider.py      # Abstract Provider Interface
│       ├── google_places.py      # Google Places API (New) Implementation
│       ├── mock_provider.py      # Fallback / Zero-Config Curated Provider
│       ├── distance.py           # Haversine distance calculator
│       └── service.py            # Main Finder Orchestrator & Cache
└── routes/
    └── recycling.py              # New FastAPI router for recycling endpoints
```

### Key Architectural Traits:
1. **Secret Isolation:** `GOOGLE_MAPS_API_KEY` is loaded strictly on the backend via `backend/app/config.py`. The React client never receives or stores API tokens.
2. **In-Memory Query Cache:** Responses for identical `(waste_type, rounded_lat, rounded_lng)` pairs are cached in-memory for 1 hour to prevent redundant external API hits.
3. **Rate Limiting & Timeouts:** External HTTP requests enforce a strict 4.0-second timeout with fallback error handling.

---

## 11. Proposed API Contract

### Proposed Endpoint: `POST /api/v1/recycling/search`

#### Request Payload Schema:
```json
{
  "waste_type": "e_waste",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "location_name": "Navi Mumbai, Maharashtra",
  "radius_km": 15.0,
  "limit": 10
}
```

#### Response Payload Schema (HTTP 200 OK):
```json
{
  "status": "success",
  "waste_type": "e_waste",
  "origin": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "display_name": "Navi Mumbai, Maharashtra"
  },
  "search_radius_km": 15.0,
  "total_results": 3,
  "provider": "google_places",
  "results": [
    {
      "id": "rc_001",
      "name": "Navi Mumbai Authorized E-Waste Collection Hub",
      "address": "Sector 19A, Vashi, Navi Mumbai, Maharashtra 400703",
      "latitude": 19.0772,
      "longitude": 72.9981,
      "distance_km": 1.25,
      "waste_categories_handled": ["e_waste", "metal"],
      "phone": "+91 22 2789 0000",
      "opening_hours": "Mon-Sat: 09:00 AM - 06:00 PM",
      "maps_url": "https://www.google.com/maps/search/?api=1&query=19.0772,72.9981",
      "directions_url": "https://www.google.com/maps/dir/?api=1&origin=19.0760,72.8777&destination=19.0772,72.9981&travelmode=driving"
    }
  ],
  "disclaimer": "Proximity and relevance are estimated. Please verify accepted material guidelines before visiting."
}
```

---

## 12. Frontend Architecture

The frontend implementation will introduce modular React components:

```
frontend/src/
├── components/
│   └── recycling/
│       ├── RecyclingCenterModal.tsx     # Main interactive finder modal
│       ├── CenterCard.tsx               # Individual center proximity card
│       ├── LocationSelector.tsx         # GPS trigger + manual text input
│       └── WasteTypeSelector.tsx        # 8-class dropdown selector
└── services/
    └── recyclingService.ts             # Typed API integration client
```

---

## 13. UI/UX Proposal

### 1. Trigger on Prediction Page
Below the classification confidence badge and disposal recommendation:
```
+------------------------------------------------------------------+
|  Predicted: Plastic (98.6%) | Recyclable | Blue Bin               |
|                                                                  |
|  [ ♻ Find Nearby Recycling Centers for Plastic ]                 |
+------------------------------------------------------------------+
```

### 2. Finder Modal Layout
- **Header:** "Find a Recycling Facility" with active category icon.
- **Top Bar:** 
  - Waste Category Selector (8 options, defaults to prediction result).
  - Location Selector: `[ 📍 Current Location ]` or `[ 🔍 Enter city / pincode ]`.
- **Search Radius Slider:** 5 km / 10 km / 25 km / 50 km.
- **Results List:** Clean cards showing center name, distance badge (`1.2 km away`), address, opening hours, and action buttons:
  - `[ 🗺 View on Map ]` (Secondary button)
  - `[ 🚗 Get Directions ]` (Primary emerald gradient button)

---

## 14. Error & Edge States Handling

| Error Scenario | User Interface Experience & Messaging |
| :--- | :--- |
| **Location Permission Denied** | Displays a non-intrusive alert: *"Location access was denied. Please enter your area, city, or pincode below to search."* Automatically focuses manual input field. |
| **Invalid / Unresolved Manual Location** | *"Unable to locate 'xyz'. Please try entering a valid city name, landmark, or 6-digit postal code (e.g. 400703)."* |
| **No Centers Found Within Radius** | *"No specialized recycling centers found within 10 km. Try expanding your search radius to 25 km or selecting a broader waste category."* |
| **External API Rate Limit / Quota Exceeded** | Backend automatically falls back to curated regional facilities and displays an informative banner: *"Showing curated benchmark facilities for your region."* |
| **Network Disconnected** | *"Unable to connect to recycling directory service. Please check your internet connection and try again."* |

---

## 15. Privacy & Data Minimization

1. **No Location Logging:** Geographic coordinates are used strictly in-memory during the request lifecycle. User location is **never persisted in SQLite database tables or logs**.
2. **Ephemeral Client State:** Geolocation coordinates are stored in React component state only while the modal is open.
3. **Zero Third-Party Trackers:** No client-side Google Maps JavaScript scripts or advertising trackers are embedded in the frontend bundle.

---

## 16. Cost & Quota Analysis

| Provider / Service | Free Tier / Allocation | Estimated Cost Beyond Free Tier | Notes for Academic Deployment |
| :--- | :--- | :--- | :--- |
| **Google Places API (New) — Text Search** | Per-SKU free allotment (up to 5,000 monthly calls on free tier) | ~$32.00 per 1,000 requests (without enterprise fields) | Zero cost during academic testing when bounded by field masking. |
| **Mock Curated Adapter** | 100% Free (Internal) | $0.00 | Always active as a zero-cost, zero-setup default. |
| **OpenStreetMap Nominatim** | Free (max 1 req/sec) | $0.00 | Strictly subject to OSM acceptable use policy. |

---

## 17. Environment Configuration Reference

The future implementation will configure backend `.env` variables cleanly:

```ini
# Recycling Center Finder Configuration (Optional - Defaults to 'mock' if key is omitted)
RECYCLING_PROVIDER=mock
GOOGLE_MAPS_API_KEY=
DEFAULT_SEARCH_RADIUS_KM=15.0
MAX_SEARCH_RESULTS=10
```

> **SECURITY DIRECTIVE:** No real Google Maps API keys are stored in source code. If an API key is supplied by a deployment administrator, it resides exclusively in the uncommitted `.env` file.

---

## 18. Implementation Plan (Future Phases)

To maintain strict project stability and regression integrity, future development is decomposed into discrete phases:

- **Phase 18B — Backend Services & Adapter**: Create `backend/app/services/recycling_finder/` (abstract provider, mock provider, Google Places provider, distance calculator) and register `POST /api/v1/recycling/search`.
- **Phase 18C — Frontend Components & State**: Build `RecyclingCenterModal`, `CenterCard`, `LocationSelector`, and `recyclingService.ts`.
- **Phase 18D — Full-Stack Integration**: Wire the prediction result card to the recycling finder modal on the Prediction page.
- **Phase 18E — Automated Tests & Security Audit**: Add pytest test cases covering location payloads, fallback providers, and input validation.
- **Phase 18F — Documentation & Tagging**: Update API documentation and user guide.

---

## 19. Risks & Limitations

1. **Informal Sector Representation:** In India, a significant portion of recyclable waste is processed by informal scrap collectors (*kabadiwalas*). While official centers are mapped, hyper-local individual collectors may not possess registered Google Maps listings.
2. **Opening Hours Variance:** Municipal dry waste centers may alter operating hours during public holidays. The user interface explicitly reminds users to call ahead for bulk drop-offs.
3. **API Key Dependency:** Cloud APIs require an active network connection. The fallback mock adapter guarantees the system never appears broken in offline demonstrations.

---

## 20. Final Architecture Recommendation

The proposed **Server-Side Proxy Architecture with Google Places (Primary) and Mock Curated Provider (Fallback)** is recommended as the optimal design for the EcoClassify DL system. It provides the highest data quality and relevance for Indian metropolitan centers while guaranteeing 100% offline testability, zero frontend key exposure, and complete preservation of the existing production model and dataset.

---
*Architecture document prepared for Phase 18A review.*
