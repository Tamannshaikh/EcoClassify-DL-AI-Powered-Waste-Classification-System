# Smart Recycling Center Finder — Frontend Implementation

**EcoClassify DL — AI-Powered Waste Classification System**  
**Phase:** Phase 18C — Frontend Implementation & Integration  
**Production Release Version:** `v2.0.0-8class`  
**Dataset Reference:** `8class-v1.0`  

---

## 1. Implementation Summary

In Phase 18C, the frontend user interface for the **Smart Recycling Center Finder** was built and seamlessly integrated into EcoClassify DL without altering the underlying deep learning model, training dataset, or existing prediction lifecycle.

The frontend communicates exclusively with the backend service at `POST /api/v1/recycling/search`. Zero external Google API keys or third-party secrets are embedded in or exposed to the client browser.

---

## 2. UI Entry Point

- **Location:** Integrated directly on the **Prediction Result Card** (`frontend/src/pages/PredictionPage.tsx`).
- **Trigger:** A dedicated action card `[ ♻️ Find Nearby Centers ]` is rendered immediately following inference.
- **Context-Aware Preselection:**
  - The classified class name is automatically passed to the finder modal.
  - Examples:
    - Prediction: `plastic` $\rightarrow$ Finder auto-selects **Plastic**.
    - Prediction: `e_waste` $\rightarrow$ Finder auto-selects **E-Waste**.
    - Prediction: `biodegradable` $\rightarrow$ Finder auto-selects **Biodegradable**.
- **Preservation:** The prediction flow, confidence scores, probability distributions, and Grad-CAM explainability remain 100% intact and undisturbed.

---

## 3. Location Handling

The frontend provides two distinct location resolution mechanisms compliant with user privacy:

1. **Browser Geolocation API (`navigator.geolocation`)**:
   - Explicit user click on `[ 📍 Use My Current Location ]` triggers permission request.
   - Geolocation is **never** requested automatically on page load.
   - Captured coordinates (`latitude`, `longitude`) are held strictly in temporary React component state during the active session.
   - No location data is stored in `localStorage`, cookies, or SQLite history.
   - Permission denial (`PERMISSION_DENIED`) and timeouts are handled with user-friendly alerts advising fallback selection.

2. **Curated Regional Hub Presets & Custom Coordinates**:
   - 1-click preset pills for major metropolitan areas (e.g., *Navi Mumbai (Vashi)*, *Mumbai (Andheri)*, *Thane West*, *Pune*, *Delhi NCR*, *Bengaluru*).
   - Expandable custom coordinate inputs (`Latitude`, `Longitude`) for testing and manual entry.

---

## 4. Waste Type Selection

- Supports all **8 production classes**:
  - `Biodegradable` $\rightarrow$ `biodegradable`
  - `Cardboard` $\rightarrow$ `cardboard`
  - `E-Waste` $\rightarrow$ `e_waste`
  - `Glass` $\rightarrow$ `glass`
  - `Metal` $\rightarrow$ `metal`
  - `Paper` $\rightarrow$ `paper`
  - `Plastic` $\rightarrow$ `plastic`
  - `Trash` $\rightarrow$ `trash`
- Users can switch waste types at any time in the modal dropdown, instantly refreshing facility recommendations.

---

## 5. Backend Integration

- Extended existing API service (`frontend/src/services/api.ts`):
  ```typescript
  searchRecyclingCenters(payload: RecyclingSearchRequest): Promise<RecyclingSearchResponse>
  ```
- Strict TypeScript schemas (`frontend/src/types/index.ts`):
  - `LocationCoords`
  - `RecyclingSearchRequest`
  - `RecyclingCenterItem`
  - `RecyclingSearchResponse`
- Uniform error handling through `extractErrorMessage(err)` with user-friendly alerts.

---

## 6. Results UI

- **Proximity Sort:** Displays facilities in ascending order of geographic distance (guaranteed by backend Haversine computation).
- **Nearest Highlight:** Visually badges the closest facility with `⭐ Nearest Facility` and a subtle highlight.
- **Card Elements:**
  - Facility Name (e.g., *Vashi Dry Waste & Plastic Recycling Depot*)
  - Proximity badge: `"Approx. X.X km away"` (no driving time or road distance claimed)
  - Full postal address
  - Contact phone number (clickable `tel:` link)
  - Operational opening hours
  - Action buttons: `[ View on Map ]` and `[ Get Directions ]`

---

## 7. Maps / Directions

- **Deep Links:** Uses the backend-generated, sanitized URLs:
  - `maps_url`: Navigates to Google Maps query with facility coordinates and title.
  - `directions_url`: Opens Google Maps directions with origin coordinates $\rightarrow$ destination coordinates.
- **Security:** Links opened in new tabs using `rel="noopener noreferrer"`.

---

## 8. Loading States

- Buttons disable during active network requests.
- Spinner animation displays with context message: `"Scanning for verified <waste_type> recycling facilities within <radius> km..."`.
- Debouncing and disabled state prevent duplicate concurrent requests.

---

## 9. Error States

- **No Facilities Found:** Clean empty state offering a 1-click `"Expand Search Radius to 50 km"` action.
- **Permission Denied / Timeout:** Informative warning banner with recommendations.
- **API Failure:** Catches 400, 422, 429, 500 status codes with clear feedback.

---

## 10. Responsive Design

- **Desktop (1280x800+):** Multi-column control layout, spacious result cards.
- **Tablet (768x1024):** Adaptive grid columns, full-width touch targets.
- **Mobile (375x667 / 390x844):** Single-column stacked layout, scrollable dialog, zero horizontal overflow.

---

## 11. Accessibility

- Keyboard support: `Escape` key closes the dialog.
- Click-outside overlay dismisses modal.
- Standard HTML `<label>` elements linked to form controls.
- Accessible ARIA labels on icon buttons.

---

## 12. Files Added

1. `frontend/src/components/RecyclingCenterModal.tsx` — Modal dialog component for recycling search, location picker, and result presentation.
2. `docs/RECYCLING_CENTER_FRONTEND_IMPLEMENTATION.md` — This implementation documentation.

---

## 13. Files Modified

1. `frontend/src/types/index.ts` — Added TypeScript interfaces for recycling center requests and responses.
2. `frontend/src/services/api.ts` — Added `searchRecyclingCenters()` API method.
3. `frontend/src/pages/PredictionPage.tsx` — Integrated the Recycling Center CTA card, modal state management, and 8-class descriptive copy.

---

## 14. Testing Results

### Backend Unit & Integration Tests:
- `backend/tests/test_api.py`: **17/17 PASS**
- `backend/tests/test_recycling.py`: **24/24 PASS**
- **Total Pytest Suite:** **41/41 PASS**

### End-to-End System Audit:
- `scripts/e2e_full_system_test.py`: **7/7 SECTORS PASS (100% SUCCESS)**
  - 8-Class Dataset Integrity
  - Model Artifacts
  - Core API Endpoints
  - 8-Class Real Image Inference
  - Grad-CAM Heatmap Generation
  - SQLite History Lifecycle
  - Security & Exception Handling

### Frontend Build & Lint:
- `npm run build`: **PASS (0 errors, clean Vite production bundle)**
- `npm run lint`: **PASS (0 errors)**

---

## 15. Browser Test Results

| Feature Verified | Result | Notes |
| :--- | :--- | :--- |
| Prediction Result CTA | PASS | Appears immediately post-classification |
| Predicted Class Preselected | PASS | `plastic`, `e_waste`, `biodegradable`, etc. auto-selected |
| Manual Waste Switching | PASS | All 8 classes selectable via dropdown |
| Geolocation Permission Flow | PASS | User-prompted on button click; no auto-request |
| Regional Presets | PASS | 1-click coordinates for Navi Mumbai, Mumbai, Pune, etc. |
| Search Integration | PASS | Dispatches to `POST /api/v1/recycling/search` |
| Result Cards & Nearest Badge | PASS | Closest facility marked with `⭐ Nearest Facility` |
| Distance Display | PASS | Formatted as `"Approx. X.XX km away"` |
| Maps & Directions Links | PASS | Opens verified Google Maps URLs with `noopener noreferrer` |
| Empty Results Handling | PASS | Displays radius expansion CTA |
| Console Health | PASS | 0 uncaught exceptions or network leakage |

---

## 16. Known Limitations

- In demo/offline mode (`RECYCLING_PROVIDER=curated`), search results are provided by curated facility hubs across major urban centers.
- Real-time facility operating status and dynamic waste capacity should be verified by the user before physical visits.

---

## 17. Next Phase

**PHASE 18D — FULL INTEGRATION TEST + POLISH**
- Final system-wide end-to-end integration testing.
- UI/UX polish across all viewports.
- Verification before repository release.
