#!/usr/bin/env python3
"""
Dataset Validation Script for TrashNet Waste Classification.

Validates:
- Folder existence and class naming
- Image counts, file extensions, and integrity
- Dimensions and duplicate checks
- Class balance calculation
- Strict rejection of invalid classes (e.g. 'organic')
"""

import sys
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from PIL import Image

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from configs.dataset_config import (
    RAW_DATA_DIR,
    EXPECTED_CLASSES,
    SUPPORTED_EXTENSIONS
)


def compute_file_hash(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file to check for exact duplicates."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_dataset(dataset_path: Path = RAW_DATA_DIR) -> bool:
    print("=" * 60)
    print("           TrashNet Dataset Validation Report")
    print("=" * 60)
    print(f"Dataset path : {dataset_path}")
    print(f"Absolute path: {dataset_path.resolve()}\n")

    # 1. Check root directory exists
    if not dataset_path.exists() or not dataset_path.is_dir():
        print(f"[FAIL] Dataset directory does not exist at {dataset_path}")
        return False

    # 2. Check class folders
    subdirs = [d.name for d in dataset_path.iterdir() if d.is_dir()]
    non_dir_files = [f.name for f in dataset_path.iterdir() if f.is_file()]

    print("--------------------------------------------------")
    print("Directory Structure & Classes")
    print("--------------------------------------------------")
    
    # Check for forbidden classes like 'organic'
    if "organic" in [d.lower() for d in subdirs]:
        print("[FAIL] Prohibited class 'organic' was detected! Must only use 'trash'.")
        return False

    # Check for exact class match
    missing_classes = set(EXPECTED_CLASSES) - set(subdirs)
    extra_classes = set(subdirs) - set(EXPECTED_CLASSES)

    for cls in EXPECTED_CLASSES:
        if cls in subdirs:
            print(f"  [OK] {cls}")
        else:
            print(f"  [MISSING] {cls}")

    if missing_classes:
        print(f"\n[FAIL] Missing required classes: {missing_classes}")
        return False

    if extra_classes:
        print(f"\n[WARN] Extra directories found: {extra_classes}")

    if non_dir_files:
        print(f"  [INFO] Non-directory files in root: {non_dir_files}")

    # 3. Validate image files per class
    print("\n--------------------------------------------------")
    print("Class Distribution & Image Integrity")
    print("--------------------------------------------------")

    class_counts = {}
    valid_images = []
    corrupted_images = []
    format_counts = Counter()
    dimension_counts = Counter()
    hash_to_files = defaultdict(list)
    unexpected_files = []

    for cls in EXPECTED_CLASSES:
        cls_dir = dataset_path / cls
        files = list(cls_dir.iterdir())
        cls_valid_count = 0
        
        for file in files:
            if file.is_dir():
                unexpected_files.append(str(file.relative_to(PROJECT_ROOT)))
                continue

            ext = file.suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                unexpected_files.append(str(file.relative_to(PROJECT_ROOT)))
                continue

            format_counts[ext] += 1

            # Check image readability and dimensions
            try:
                with Image.open(file) as img:
                    img.verify()  # Fast structural verification
                
                # Reopen to read dimensions & format (verify closes the file handle)
                with Image.open(file) as img:
                    width, height = img.size
                    img_format = img.format
                    mode = img.mode
                
                file_hash = compute_file_hash(file)
                hash_to_files[file_hash].append(file)
                dimension_counts[(width, height)] += 1
                
                valid_images.append({
                    "path": file,
                    "class": cls,
                    "width": width,
                    "height": height,
                    "format": img_format,
                    "mode": mode,
                    "hash": file_hash
                })
                cls_valid_count += 1

            except Exception as e:
                corrupted_images.append((file, str(e)))

        class_counts[cls] = cls_valid_count
        print(f"  {cls:<12}: {cls_valid_count:>5} images")

    total_valid = len(valid_images)
    total_corrupted = len(corrupted_images)
    total_files_checked = total_valid + total_corrupted

    print("\n--------------------------------------------------")
    print("Total Summary")
    print("--------------------------------------------------")
    print(f"Total Valid Images Checked : {total_valid}")
    print(f"Total Corrupted Images     : {total_corrupted}")
    print(f"Total Files Examined       : {total_files_checked}")

    if corrupted_images:
        print("\n[FAIL] Corrupted Files Detail:")
        for cf, err in corrupted_images:
            print(f"  - {cf.name}: {err}")

    # 4. Class Imbalance Analysis
    print("\n--------------------------------------------------")
    print("Class Imbalance Analysis")
    print("--------------------------------------------------")
    for cls in EXPECTED_CLASSES:
        cnt = class_counts[cls]
        pct = (cnt / total_valid * 100) if total_valid > 0 else 0
        bar = "=" * int(pct // 2)
        print(f"  {cls:<12}: {cnt:>5} ({pct:>5.2f}%)  |{bar}")

    # 5. Image Formats & Modes
    print("\n--------------------------------------------------")
    print("Image Extensions & Formats")
    print("--------------------------------------------------")
    for ext, count in format_counts.items():
        print(f"  {ext.upper():<10}: {count} files")

    # 6. Image Dimensions
    print("\n--------------------------------------------------")
    print("Image Dimensions Statistics")
    print("--------------------------------------------------")
    widths = [img["width"] for img in valid_images]
    heights = [img["height"] for img in valid_images]
    
    if widths and heights:
        print(f"  Width range  : Min {min(widths)}px, Max {max(widths)}px")
        print(f"  Height range : Min {min(heights)}px, Max {max(heights)}px")
        print("  Top 3 Dimensions:")
        for dim, count in dimension_counts.most_common(3):
            pct = (count / total_valid * 100)
            print(f"    - {dim[0]} x {dim[1]} : {count} images ({pct:.1f}%)")

    # 7. Duplicate Detection
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    print("\n--------------------------------------------------")
    print("Duplicate Detection (Exact Content Hash)")
    print("--------------------------------------------------")
    if duplicates:
        print(f"  [NOTE] Exact duplicate groups found: {len(duplicates)}")
        for h, files in list(duplicates.items())[:5]:
            print(f"    Hash {h[:10]}...: {[f.name for f in files]}")
    else:
        print("  [OK] No exact byte-duplicate files detected.")

    if unexpected_files:
        print("\n--------------------------------------------------")
        print(f"Unexpected / Non-image Files ({len(unexpected_files)}):")
        for uf in unexpected_files[:10]:
            print(f"  - {uf}")

    # Final verdict
    print("\n" + "=" * 60)
    passed = (
        total_valid == 2527 and
        total_corrupted == 0 and
        len(missing_classes) == 0 and
        "organic" not in subdirs
    )

    if passed:
        print("                 VALIDATION RESULT: PASS")
        print("=" * 60)
        return True
    else:
        print("                 VALIDATION RESULT: FAIL")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
