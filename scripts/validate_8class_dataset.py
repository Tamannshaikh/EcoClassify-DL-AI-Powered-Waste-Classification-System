"""
Comprehensive Independent Validation Script for Extended 8-Class Dataset.
EcoClassify DL — Phase 11 Dataset Validation

Validates dataset structure, image readability, hash uniqueness, leakage freedom,
and manifest integrity. Exits with 0 on success, non-zero on failure.
"""

import os
import sys
import hashlib
import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "final" / "8class"
METADATA_DIR = OUTPUT_DIR / "metadata"

EXPECTED_CLASSES = {
    0: {"name": "biodegradable", "prefix": "TB", "target": 450},
    1: {"name": "cardboard", "prefix": "TC", "target": 403},
    2: {"name": "e_waste", "prefix": "TE", "target": 450},
    3: {"name": "glass", "prefix": "TG", "target": 501},
    4: {"name": "metal", "prefix": "TM", "target": 410},
    5: {"name": "paper", "prefix": "TP", "target": 594},
    6: {"name": "plastic", "prefix": "TPL", "target": 482},
    7: {"name": "trash", "prefix": "TT", "target": 137},
}

EXPECTED_TOTAL = 3427

def compute_md5(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_dataset():
    print("=" * 80)
    print("VALIDATING EXTENDED 8-CLASS DATASET (data/final/8class/)")
    print("=" * 80)

    errors = []

    # 1. Directory Structure Checks
    print("\n[CHECK 1] Validating Directory & Metadata Structure...")
    if not OUTPUT_DIR.exists():
        errors.append(f"Output directory does not exist: {OUTPUT_DIR}")
        print(f"  [FAIL] Missing {OUTPUT_DIR}")
        return False

    for split in ["train", "val", "test"]:
        split_dir = OUTPUT_DIR / split
        if not split_dir.exists():
            errors.append(f"Missing split directory: {split_dir}")
        for cdef in EXPECTED_CLASSES.values():
            cdir = split_dir / cdef["name"]
            if not cdir.exists():
                errors.append(f"Missing class directory: {cdir}")

    manifest_path = METADATA_DIR / "dataset_manifest.csv"
    metadata_path = METADATA_DIR / "dataset_metadata.json"
    mapping_path = METADATA_DIR / "class_mapping.json"

    if not manifest_path.exists():
        errors.append(f"Missing manifest file: {manifest_path}")
    if not metadata_path.exists():
        errors.append(f"Missing metadata file: {metadata_path}")
    if not mapping_path.exists():
        errors.append(f"Missing class mapping file: {mapping_path}")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    print("  [PASS] All split and class directories and metadata files exist.")

    # 2. Manifest & Class Mapping Validation
    print("\n[CHECK 2] Validating Manifest and Class Mapping Content...")
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    for idx_str, cinfo in mapping_data.items():
        idx = int(idx_str)
        exp = EXPECTED_CLASSES[idx]
        if cinfo["name"] != exp["name"] or cinfo["prefix"] != exp["prefix"] or cinfo["target"] != exp["target"]:
            errors.append(f"Class mapping mismatch for index {idx}: {cinfo} vs {exp}")

    manifest_records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        manifest_records = list(reader)

    print(f"  Total records in manifest: {len(manifest_records)}")
    if len(manifest_records) != EXPECTED_TOTAL:
        errors.append(f"Manifest total records {len(manifest_records)} != {EXPECTED_TOTAL}")

    # 3. Physical File Integrity & Image Readability
    print("\n[CHECK 3] Verifying Physical File Integrity and Pillow Readability...")
    physical_files = []
    for split in ["train", "val", "test"]:
        for cdef in EXPECTED_CLASSES.values():
            cdir = OUTPUT_DIR / split / cdef["name"]
            for img_file in cdir.glob("*.*"):
                if img_file.is_file():
                    physical_files.append(img_file)

    print(f"  Physical images found: {len(physical_files)}")
    if len(physical_files) != EXPECTED_TOTAL:
        errors.append(f"Physical file count {len(physical_files)} != expected {EXPECTED_TOTAL}")

    # Verify each image
    corrupted_count = 0
    class_counts = Counter()
    split_counts = Counter()
    source_dataset_counts = Counter()
    sample_ids = set()
    md5_to_splits = defaultdict(set)
    ndg_to_splits = defaultdict(set)
    source_paths = set()

    for idx, rec in enumerate(manifest_records):
        derived_rel = rec["derived_relative_path"]
        abs_img_path = PROJECT_ROOT / derived_rel

        if not abs_img_path.exists():
            errors.append(f"File listed in manifest does not exist: {derived_rel}")
            continue

        # Sample ID uniqueness
        sid = rec["sample_id"]
        if sid in sample_ids:
            errors.append(f"Duplicate sample_id in manifest: {sid}")
        sample_ids.add(sid)

        # Class & prefix consistency
        cname = rec["class_name"]
        cprefix = rec["category_prefix"]
        cidx = int(rec["class_index"])
        exp = EXPECTED_CLASSES[cidx]
        if exp["name"] != cname or exp["prefix"] != cprefix:
            errors.append(f"Sample {sid} class metadata mismatch: index {cidx}, name {cname}, prefix {cprefix}")

        # Pillow readability
        try:
            with Image.open(abs_img_path) as img:
                img.verify()
            with Image.open(abs_img_path) as img:
                w, h = img.size
                ch = len(img.getbands())
                if w <= 0 or h <= 0 or ch <= 0:
                    errors.append(f"Invalid dimensions for {derived_rel}: {w}x{h} ({ch} channels)")
        except Exception as e:
            corrupted_count += 1
            errors.append(f"Corrupted image {derived_rel}: {str(e)}")

        # Track stats
        class_counts[cname] += 1
        split_counts[rec["split"]] += 1
        source_dataset_counts[rec["source_dataset"]] += 1

        # Track hashes and sources
        actual_md5 = compute_md5(abs_img_path)
        if actual_md5 != rec["md5"]:
            errors.append(f"MD5 hash mismatch for {derived_rel}: manifest={rec['md5']}, actual={actual_md5}")

        md5_to_splits[actual_md5].add(rec["split"])
        
        ndg = rec["near_duplicate_group"]
        if ndg != "NONE":
            ndg_to_splits[ndg].add(rec["split"])

        src_rel = rec["source_relative_path"]
        if src_rel in source_paths:
            errors.append(f"Duplicate source reference in dataset: {src_rel}")
        source_paths.add(src_rel)

    print(f"  [PASS] All {len(manifest_records)} images successfully opened & verified with Pillow (Corrupted: {corrupted_count}).")

    # 4. Class Distribution & Split Totals
    print("\n[CHECK 4] Verifying Class Totals and Split Distribution...")
    for idx, exp in EXPECTED_CLASSES.items():
        cname = exp["name"]
        cnt = class_counts[cname]
        expected_cnt = exp["target"]
        print(f"  - Class '{cname:<15}': {cnt:>4} / {expected_cnt} target")
        if cnt != expected_cnt:
            errors.append(f"Class count mismatch for '{cname}': got {cnt}, expected {expected_cnt}")

    print(f"\n  Split Breakdown:")
    print(f"  - Train:      {split_counts['train']:>4} ({split_counts['train']/EXPECTED_TOTAL:.2%})")
    print(f"  - Validation: {split_counts['val']:>4} ({split_counts['val']/EXPECTED_TOTAL:.2%})")
    print(f"  - Test:       {split_counts['test']:>4} ({split_counts['test']/EXPECTED_TOTAL:.2%})")
    print(f"  - Total:      {sum(split_counts.values()):>4} (100.0%)")

    # 5. Leakage Verification
    print("\n[CHECK 5] Running Exact & Near-Duplicate Leakage Audit...")
    exact_leak_groups = {h: s for h, s in md5_to_splits.items() if len(s) > 1}
    print(f"  Exact Duplicate Cross-Split Leaks: {len(exact_leak_groups)}")
    if exact_leak_groups:
        errors.append(f"Exact duplicate hashes cross split boundaries: {len(exact_leak_groups)} groups")

    near_dup_leak_groups = {g: s for g, s in ndg_to_splits.items() if len(s) > 1}
    print(f"  Near-Duplicate Cross-Split Leaks:  {len(near_dup_leak_groups)}")
    if near_dup_leak_groups:
        errors.append(f"Near-duplicate groups cross split boundaries: {len(near_dup_leak_groups)} groups")

    print(f"  Unique Source References:          {len(source_paths)} / {EXPECTED_TOTAL}")
    if len(source_paths) != EXPECTED_TOTAL:
        errors.append(f"Source uniqueness violation: {len(source_paths)} != {EXPECTED_TOTAL}")

    # Summary
    print("\n" + "=" * 80)
    if errors:
        print(f"VALIDATION FAILED WITH {len(errors)} ERRORS:")
        for e in errors[:20]:
            print(f"  - {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        return False
    else:
        print("ALL VALIDATION CHECKS PASSED PERFECTLY (100% LEAKAGE-FREE & CONSISTENT)")
        print("=" * 80)
        return True

if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
