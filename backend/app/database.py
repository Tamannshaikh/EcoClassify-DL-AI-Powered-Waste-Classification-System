import sqlite3
import json
import re
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from backend.app.config import (
    DB_PATH,
    CATEGORY_PREFIXES,
    PROJECT_ROOT,
    DATA_DIR,
    UPLOADS_DIR,
    PREDICTIONS_UPLOAD_DIR
)


def get_db_connection():
    """Returns a connection with Row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def migrate_legacy_records(conn: sqlite3.Connection):
    """
    Safely migrates any legacy UUID or non-category records to category-based IDs (TC1, TG1, TM1, etc.)
    and links to existing image files if available on disk.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(predictions)")
    cols = [r["name"] for r in cursor.fetchall()]
    if not cols:
        return

    cursor.execute("SELECT * FROM predictions ORDER BY id ASC")
    rows = cursor.fetchall()

    for row in rows:
        pred_id = row["prediction_id"]
        pred_class = (row["predicted_class"] or "trash").lower()
        prefix = CATEGORY_PREFIXES.get(pred_class, "TT")

        # Check if record is not in prefix+number format (e.g. UUID)
        if not re.match(rf"^{prefix}\d+$", str(pred_id)):
            cursor.execute("""
                INSERT INTO class_counters (class_name, last_id)
                VALUES (?, 1)
                ON CONFLICT(class_name) DO UPDATE SET last_id = last_id + 1
            """, (pred_class,))
            cursor.execute("SELECT last_id FROM class_counters WHERE class_name = ?", (pred_class,))
            c_row = cursor.fetchone()
            seq_num = c_row["last_id"] if c_row else 1
            new_id = f"{prefix}{seq_num}"

            orig_name = row["original_filename"]
            img_path = row["image_path"] if "image_path" in row.keys() else None

            target_filename = None
            # Try finding image in uploads, raw test images, or project root
            if img_path and (PROJECT_ROOT / img_path).is_file():
                ext = Path(img_path).suffix or ".jpg"
                target_filename = f"{new_id}{ext}"
                target_full = PREDICTIONS_UPLOAD_DIR / target_filename
                if str((PROJECT_ROOT / img_path).resolve()) != str(target_full.resolve()):
                    shutil.copy2(PROJECT_ROOT / img_path, target_full)
            elif orig_name:
                candidates = [
                    DATA_DIR / "raw" / "test_image" / orig_name,
                    UPLOADS_DIR / orig_name,
                    PROJECT_ROOT / orig_name
                ]
                for cand in candidates:
                    if cand.is_file():
                        ext = cand.suffix or ".png"
                        target_filename = f"{new_id}{ext}"
                        target_full = PREDICTIONS_UPLOAD_DIR / target_filename
                        shutil.copy2(cand, target_full)
                        break

            new_img_path = f"data/uploads/predictions/{target_filename}" if target_filename else None
            new_img_url = f"/api/v1/predictions/{new_id}/image" if target_filename else None

            cursor.execute("""
                UPDATE predictions
                SET prediction_id = ?,
                    filename = ?,
                    image_path = ?,
                    image_url = ?
                WHERE id = ?
            """, (
                new_id,
                target_filename or f"{new_id}.jpg",
                new_img_path,
                new_img_url,
                row["id"]
            ))


def init_db():
    """Initializes the database schema and performs non-destructive column migrations."""
    PREDICTIONS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Main predictions table
        cursor.execute("""
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
            )
        """)

        # 2. Concurrency-safe category sequence counter table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_counters (
                class_name TEXT PRIMARY KEY,
                last_id INTEGER NOT NULL DEFAULT 0
            )
        """)

        # 3. Non-destructive migration for existing tables missing image columns
        cursor.execute("PRAGMA table_info(predictions)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "image_path" not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN image_path TEXT")
        if "image_url" not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN image_url TEXT")

        # 4. Perform legacy record migration
        migrate_legacy_records(conn)

        # 5. Synchronize counters with any existing category IDs
        for class_name, prefix in CATEGORY_PREFIXES.items():
            cursor.execute("""
                SELECT prediction_id FROM predictions
                WHERE predicted_class = ? AND prediction_id LIKE ?
            """, (class_name, f"{prefix}%"))
            rows = cursor.fetchall()
            max_seq = 0
            for r in rows:
                match = re.match(rf"^{prefix}(\d+)$", str(r["prediction_id"]))
                if match:
                    max_seq = max(max_seq, int(match.group(1)))
            
            cursor.execute("""
                INSERT INTO class_counters (class_name, last_id)
                VALUES (?, ?)
                ON CONFLICT(class_name) DO UPDATE SET last_id = MAX(last_id, ?)
            """, (class_name.lower(), max_seq, max_seq))

        conn.commit()


def get_next_prediction_id(class_name: str) -> str:
    """
    Concurrency-safe atomic sequence generator per waste class.
    Returns prefix + incremented integer (e.g. TC1, TM2, TPL3).
    """
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
        seq_num = row["last_id"] if row else 1
        conn.commit()
        return f"{prefix}{seq_num}"


def save_prediction(
    prediction_id: str,
    filename: str,
    original_filename: str,
    predicted_class: str,
    confidence: float,
    probabilities: Dict[str, float],
    inference_time_ms: float,
    model_version: str,
    gradcam_generated: bool = False,
    image_path: Optional[str] = None,
    image_url: Optional[str] = None
) -> int:
    """Inserts a new prediction record into SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO predictions (
                prediction_id, filename, original_filename,
                predicted_class, confidence, probabilities_json,
                inference_time_ms, model_version, gradcam_generated,
                image_path, image_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction_id,
            filename,
            original_filename,
            predicted_class,
            confidence,
            json.dumps(probabilities),
            inference_time_ms,
            model_version,
            1 if gradcam_generated else 0,
            image_path,
            image_url,
            now_str
        ))
        conn.commit()
        return cursor.lastrowid


def get_predictions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Retrieves recent predictions sorted by created_at descending."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, prediction_id, filename, original_filename,
                   predicted_class, confidence, probabilities_json,
                   inference_time_ms, model_version, gradcam_generated,
                   image_path, image_url, created_at
            FROM predictions
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            img_url = r["image_url"] if "image_url" in r.keys() and r["image_url"] else f"/api/v1/predictions/{r['prediction_id']}/image"
            results.append({
                "id": r["id"],
                "prediction_id": r["prediction_id"],
                "filename": r["filename"],
                "original_filename": r["original_filename"],
                "predicted_class": r["predicted_class"],
                "confidence": round(r["confidence"], 4),
                "probabilities": json.loads(r["probabilities_json"]),
                "inference_time_ms": round(r["inference_time_ms"], 2),
                "model_version": r["model_version"],
                "gradcam_generated": bool(r["gradcam_generated"]),
                "image_path": r["image_path"] if "image_path" in r.keys() else None,
                "image_url": img_url,
                "created_at": r["created_at"]
            })
        return results


def get_total_prediction_count() -> int:
    """Returns total count of stored predictions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM predictions")
        row = cursor.fetchone()
        return row["count"] if row else 0


def get_prediction_by_id(prediction_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single prediction by its category string (e.g. TM7) or numeric ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if prediction_id.isdigit():
            cursor.execute("SELECT * FROM predictions WHERE id = ?", (int(prediction_id),))
        else:
            cursor.execute("SELECT * FROM predictions WHERE prediction_id = ?", (prediction_id,))
        row = cursor.fetchone()
        if not row:
            return None
        img_url = row["image_url"] if "image_url" in row.keys() and row["image_url"] else f"/api/v1/predictions/{row['prediction_id']}/image"
        return {
            "id": row["id"],
            "prediction_id": row["prediction_id"],
            "filename": row["filename"],
            "original_filename": row["original_filename"],
            "predicted_class": row["predicted_class"],
            "confidence": round(row["confidence"], 4),
            "probabilities": json.loads(row["probabilities_json"]),
            "inference_time_ms": round(row["inference_time_ms"], 2),
            "model_version": row["model_version"],
            "gradcam_generated": bool(row["gradcam_generated"]),
            "image_path": row["image_path"] if "image_path" in row.keys() else None,
            "image_url": img_url,
            "created_at": row["created_at"]
        }


def delete_prediction(prediction_id: str) -> bool:
    """Deletes a prediction record and removes its associated stored image from disk."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT image_path FROM predictions WHERE prediction_id = ? OR CAST(id AS TEXT) = ?",
            (str(prediction_id), str(prediction_id))
        )
        row = cursor.fetchone()
        
        # Delete image file safely if present
        if row and row["image_path"]:
            try:
                img_path = (PROJECT_ROOT / Path(row["image_path"])).resolve()
                if img_path.is_file():
                    img_path.unlink(missing_ok=True)
            except Exception:
                pass

        cursor.execute(
            "DELETE FROM predictions WHERE prediction_id = ? OR CAST(id AS TEXT) = ?",
            (str(prediction_id), str(prediction_id))
        )
        conn.commit()
        return cursor.rowcount > 0
