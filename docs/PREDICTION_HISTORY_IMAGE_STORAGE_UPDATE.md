# Prediction History & Stored Image System Update Report

**Project**: EcoClassify DL — AI-Powered Waste Classification System  
**Date**: 2026-10-04  
**Status**: VERIFIED & PRODUCTION READY  

---

## 1. Original Problem
During browser testing, the Prediction History page (`/history`) and Prediction Audit modals presented multiple issues:
1. The Prediction ID column and audit modal displayed raw 36-character UUID strings (e.g., `4e95ad8b-df98-4503-b5a0-7d2d77a01a79`).
2. The image column rendered a missing/empty icon rather than the actual analyzed image thumbnail.
3. The Prediction Audit Record modal did not display the analyzed image.
4. Analyzed images were not permanently stored on disk or linked to SQLite records.

---

## 2. Root Cause
* **Legacy UUID Schema**: Earlier iterations of the backend generated standard UUIDv4 tokens for logging records rather than class-prefixed sequence identifiers.
* **Missing Image Persistence Pipeline**: The prediction router processed uploaded images entirely in-memory via Pillow/NumPy without streaming a permanent copy into a dedicated uploads directory.
* **Database Columns Missing**: The SQLite database table lacked dedicated `image_path` and `image_url` fields, leaving stored records without persistent asset paths.
* **Backend Reload State**: Background FastAPI worker had an older in-memory router loaded before the dedicated image streaming endpoints were mounted.

---

## 3. Database Changes
* **Database File**: `data/waste_classification.db`
* **Table `predictions` Schema**:
  ```sql
  CREATE TABLE IF NOT EXISTS predictions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      prediction_id TEXT UNIQUE NOT NULL,
      filename TEXT NOT NULL,
      original_filename TEXT NOT NULL,
      predicted_class TEXT NOT NULL,
      confidence REAL NOT NULL,
      probabilities_json TEXT NOT NULL,
      inference_time_ms REAL NOT NULL,
      model_version TEXT NOT NULL,
      gradcam_generated INTEGER DEFAULT 0,
      image_path TEXT,
      image_url TEXT,
      created_at DATETIME NOT NULL
  );
  ```
* **Table `class_counters` Schema**:
  ```sql
  CREATE TABLE IF NOT EXISTS class_counters (
      class_name TEXT PRIMARY KEY,
      last_id INTEGER NOT NULL DEFAULT 0
  );
  ```
* **Unique & Atomic Integrity**: `prediction_id` has a `UNIQUE` constraint, and atomic sequences are tracked per class in `class_counters`.

---

## 4. ID Generation Mechanism
Category IDs use standard prefixes with class-independent counters:

| Waste Class | ID Prefix | Example Sequence | Disambiguation Note |
|---|---|---|---|
| **Cardboard** | `TC` | `TC1`, `TC2`, `TC3`... | Trash Cardboard |
| **Glass** | `TG` | `TG1`, `TG2`, `TG3`... | Trash Glass |
| **Metal** | `TM` | `TM1`, `TM2`, `TM3`... | Trash Metal |
| **Paper** | `TP` | `TP1`, `TP2`, `TP3`... | Trash Paper |
| **Plastic** | `TPL` | `TPL1`, `TPL2`, `TPL3`... | `TPL` disambiguates from Paper (`TP`) |
| **Trash** | `TT` | `TT1`, `TT2`, `TT3`... | Trash Residual |

Atomic SQLite query:
```python
def get_next_prediction_id(class_name: str) -> str:
    norm_class = class_name.lower()
    prefix = CATEGORY_PREFIXES.get(norm_class, "TPRED")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO class_counters (class_name, last_id)
            VALUES (?, 1)
            ON CONFLICT(class_name) DO UPDATE SET last_id = last_id + 1
        """, (norm_class,))
        cursor.execute("SELECT last_id FROM class_counters WHERE class_name = ?", (norm_class,))
        row = cursor.fetchone()
        conn.commit()
        return f"{prefix}{row['last_id']}"
```

---

## 5. Image Storage Mechanism
* **Storage Location**: `data/uploads/predictions/`
* **Safe Filename Generation**: Stored under `<prediction_id>.<ext>` (e.g., `TM1.png`, `TC4.jpg`, `TPL1.jpg`).
* **Validation**:
  - File extension check (`.jpg`, `.jpeg`, `.png`)
  - 10 MB maximum file size limit
  - Pillow structural verification to guard against corrupted files or embedded payloads
* **Persistence Guarantee**: Saved files survive prediction completion, browser refresh, frontend restart, and backend service restart.

---

## 6. API Changes
1. **POST `/api/v1/predict` & `/api/v1/predict/gradcam`**:
   - Saves uploaded image to `data/uploads/predictions/{prediction_id}{ext}`.
   - Returns `prediction_id`, `image_url` (`/api/v1/predictions/{prediction_id}/image`), and `image_path`.
2. **GET `/api/v1/predictions/{prediction_id}/image`**:
   - Validates prediction ID against SQLite database.
   - Resolves file path and enforces strict boundary containment within `PROJECT_ROOT`.
   - Returns `FileResponse` with `image/jpeg` or `image/png` (HTTP 200).
   - Returns HTTP 404 if prediction record or image does not exist.
3. **DELETE `/api/v1/predictions/{prediction_id}`**:
   - Deletes SQLite record.
   - Safely removes the associated image file from disk via `Path.unlink(missing_ok=True)`.

---

## 7. Frontend Changes
* **[`frontend/src/pages/HistoryPage.tsx`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/frontend/src/pages/HistoryPage.tsx)**:
  - Table renders category ID in bold monospace font.
  - Image column renders clean rounded thumbnail with `getFullImageUrl` resolving to backend origin `http://127.0.0.1:8000`.
  - Image error handler renders a graceful fallback icon if an image is genuinely missing.
  - Prediction Audit Record modal displays the full analyzed image at the top of the detail modal.
  - Custom in-app confirmation modal for record deletion.
* **[`frontend/src/pages/PredictionPage.tsx`](file:///c:/Users/Sajiya/Downloads/Waste_Classification_DL_System_COMPLETE/Waste_Classification_DL_System/frontend/src/pages/PredictionPage.tsx)**:
  - Displays `Logged to SQLite (ID: <prediction_id>)` upon successful inference.

---

## 8. Security Validation
* **Path Traversal Protection**: Relative paths are resolved against `PROJECT_ROOT` and verified with `full_path.relative_to(PROJECT_ROOT.resolve())`. Client cannot request arbitrary file paths.
* **File Upload Constraints**: 10 MB strict limit, extension whitelist, MIME check, and Pillow verification.
* **No Raw Client Filenames**: Files on disk use the sanitized prediction ID naming convention.

---

## 9. Existing-Record Migration
* The existing metal prediction record (`4e95ad8b-df98-4503-b5a0-7d2d77a01a79` for `Screenshot 2026-10-04 003728.png`, 99.51% confidence) was migrated:
  - Updated ID to **`TM1`**.
  - Located original image on disk (`data/raw/test_image/Screenshot 2026-10-04 003728.png`) and copied it to `data/uploads/predictions/TM1.png`.
  - Linked database record: `image_path = 'data/uploads/predictions/TM1.png'`, `image_url = '/api/v1/predictions/TM1/image'`.
  - Verified `GET /api/v1/predictions/TM1/image` returns HTTP 200 with 175 KB image payload.
  - Initialized `class_counters` table for `metal` = 1.

---

## 10. Tests
* **Pytest Test Suite**: `python -m pytest backend/tests/test_api.py -v` -> **17 / 17 passed (100%)**.
* **Frontend Production Build**: `npm run build` -> **0 TypeScript errors, build succeeded**.
* **E2E Full System Audit**: `python scripts/e2e_full_system_test.py` -> **7 / 7 sectors passed (100%)**.

---

## 11. Browser Verification
Tested interactively using `browser_subagent`:
1. Navigated to `http://127.0.0.1:5173/history`.
2. Verified all rows display human-readable category IDs (`TC4`, `TT1`, `TG5`, `TG4`, `TPL3`, `TP2`, `TM3`, `TC3`, `TG1`, `TP1`, `TPL1`, `TM1`). Zero raw UUIDs shown.
3. Verified table thumbnails display sharp rendered photos.
4. Opened Prediction Audit Modal for `TM1`: Header displayed `ID: TM1`, full metal photo rendered cleanly, probabilities accurate.
5. Opened Prediction Audit Modal for `TT1`: Header displayed `ID: TT1`, snack bag photo rendered cleanly, probabilities accurate.
6. Refreshed browser page: All records, IDs, and images persisted without degradation.
7. Uploaded a new image on `/predict`: Model generated `TC4`, which instantly appeared at the top of `/history`.

---

## 12. Files Changed
1. `backend/app/config.py` — Added `CATEGORY_PREFIXES`, `PREDICTIONS_UPLOAD_DIR` configuration.
2. `backend/app/database.py` — Added atomic `class_counters`, `migrate_legacy_records()`, `get_next_prediction_id()`, `image_path` tracking, safe file deletion.
3. `backend/app/routes/prediction.py` — Added persistent local image storage and category ID assignment.
4. `backend/app/routes/history.py` — Added `GET /api/v1/predictions/{id}/image` endpoint with path validation.
5. `backend/app/schemas.py` — Added `image_url` and `image_path` to Pydantic schemas.
6. `frontend/src/pages/HistoryPage.tsx` — Added thumbnail and full modal image display, fallback handlers, and delete confirmation modal.
7. `frontend/src/types/index.ts` — Updated TypeScript types for `PredictionResponse` and `PredictionHistoryItem`.
8. `README.md` — Updated Section 23 with Category IDs, image storage architecture, and class prefix reference table.
