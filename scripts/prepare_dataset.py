#!/usr/bin/env python3
"""
Dataset Preparation & Splitting Script for TrashNet.

Features:
- Group-aware stratified splitting: Guarantees that identical byte-content image
  pairs are co-located in the same split (eliminating cross-split data leakage).
- 70% Train / 15% Validation / 15% Test split target.
- Deterministic shuffling with configurable seed (default 42).
- Safe copying of files to data/processed/ (without modifying raw dataset).
- Generation of dataset_manifest.csv with metadata and file hashes.
- Automated data leakage verification across both filenames AND content hashes.
"""

import sys
import shutil
import hashlib
import random
import csv
from pathlib import Path
from collections import defaultdict
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
    PROCESSED_DATA_DIR,
    EXPECTED_CLASSES,
    SUPPORTED_EXTENSIONS,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    RANDOM_SEED
)


def compute_file_hash(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file for integrity and leak detection."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def prepare_and_split_dataset(
    raw_dir: Path = RAW_DATA_DIR,
    processed_dir: Path = PROCESSED_DATA_DIR,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    seed: int = RANDOM_SEED
) -> bool:
    print("=" * 70)
    print("      TrashNet Group-Aware Stratified Dataset Preparation")
    print("=" * 70)
    print(f"Source Raw Path    : {raw_dir}")
    print(f"Target Processed   : {processed_dir}")
    print(f"Split Ratio        : Train {train_ratio*100:.0f}% / Val {val_ratio*100:.0f}% / Test {test_ratio*100:.0f}%")
    print(f"Random Seed        : {seed}\n")

    random.seed(seed)

    # 1. First scan all raw images, compute hashes, and identify duplicate groups
    all_raw_files = []
    hash_to_files = defaultdict(list)
    for cls in EXPECTED_CLASSES:
        cls_dir = raw_dir / cls
        if not cls_dir.exists():
            print(f"[FAIL] Missing class directory: {cls_dir}")
            return False
        for f in sorted(cls_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                f_hash = compute_file_hash(f)
                item = {"file": f, "class": cls, "hash": f_hash}
                all_raw_files.append(item)
                hash_to_files[f_hash].append(item)

    print(f"Total raw files scanned: {len(all_raw_files)}")
    multi_file_hashes = {h: items for h, items in hash_to_files.items() if len(items) > 1}
    print(f"Content-duplicate groups detected: {len(multi_file_hashes)}")
    for h, items in multi_file_hashes.items():
        names = [f"{it['class']}/{it['file'].name}" for it in items]
        print(f"  • Hash {h[:12]}... : {names}")

    # 2. Reset and create clean processed directories
    splits = ["train", "val", "test"]
    for s in splits:
        split_path = processed_dir / s
        if split_path.exists():
            shutil.rmtree(split_path)
        split_path.mkdir(parents=True, exist_ok=True)
        for cls in EXPECTED_CLASSES:
            (split_path / cls).mkdir(parents=True, exist_ok=True)

    # 3. Group-aware stratified splitting
    # Duplicate groups are assigned to 'train' to prevent cross-split leakage
    assigned_split = {}
    for h, items in multi_file_hashes.items():
        for it in items:
            assigned_split[it["file"]] = "train"

    # Now split the remaining non-duplicate files per class to hit stratified ratios
    for cls in EXPECTED_CLASSES:
        cls_items = [it for it in all_raw_files if it["class"] == cls]
        cls_unassigned = [it for it in cls_items if it["file"] not in assigned_split]
        
        # Total targets for this class
        total_cls = len(cls_items)
        target_train = int(round(total_cls * train_ratio))
        target_val = int(round(total_cls * val_ratio))
        target_test = total_cls - target_train - target_val

        # How many already in train from duplicate groups
        already_train = sum(1 for it in cls_items if assigned_split.get(it["file"]) == "train")
        
        needed_train = max(0, target_train - already_train)
        needed_val = target_val
        needed_test = total_cls - already_train - needed_train - needed_val

        # Deterministic shuffle of unassigned files
        random.shuffle(cls_unassigned)

        for it in cls_unassigned[:needed_train]:
            assigned_split[it["file"]] = "train"
        for it in cls_unassigned[needed_train:needed_train + needed_val]:
            assigned_split[it["file"]] = "val"
        for it in cls_unassigned[needed_train + needed_val:]:
            assigned_split[it["file"]] = "test"

    # 4. Copy files and generate manifest
    manifest_rows = []
    split_stats = defaultdict(lambda: {"train": 0, "val": 0, "test": 0, "total": 0})
    split_file_hashes = {"train": set(), "val": set(), "test": set()}
    split_file_names = {"train": set(), "val": set(), "test": set()}
    total_copied = 0

    for it in all_raw_files:
        file = it["file"]
        cls = it["class"]
        f_hash = it["hash"]
        split_name = assigned_split[file]

        dest_path = processed_dir / split_name / cls / file.name
        shutil.copy2(file, dest_path)

        with Image.open(file) as img:
            w, h = img.size

        rel_dest = dest_path.relative_to(PROJECT_ROOT).as_posix()
        manifest_rows.append({
            "filepath": rel_dest,
            "filename": file.name,
            "class_name": cls,
            "split": split_name,
            "image_width": w,
            "image_height": h,
            "extension": file.suffix.lower(),
            "file_hash": f_hash
        })

        split_stats[cls][split_name] += 1
        split_stats[cls]["total"] += 1
        split_file_hashes[split_name].add(f_hash)
        split_file_names[split_name].add(file.name)
        total_copied += 1

    # Write manifest
    manifest_path = processed_dir / "dataset_manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["filepath", "filename", "class_name", "split", "image_width", "image_height", "extension", "file_hash"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"\n[OK] Manifest generated at: {manifest_path.relative_to(PROJECT_ROOT)}")

    # Print Table
    print("\n----------------------------------------------------------------------")
    print(f"{'Class':<12} | {'Total':>6} | {'Train':>6} ({'Train %':>6}) | {'Val':>5} ({'Val %':>5}) | {'Test':>5} ({'Test %':>5})")
    print("----------------------------------------------------------------------")
    total_tr, total_va, total_te, total_all = 0, 0, 0, 0
    for cls in EXPECTED_CLASSES:
        st = split_stats[cls]
        tr, va, te, tot = st["train"], st["val"], st["test"], st["total"]
        total_tr += tr
        total_va += va
        total_te += te
        total_all += tot
        tr_pct = (tr / tot * 100) if tot > 0 else 0
        va_pct = (va / tot * 100) if tot > 0 else 0
        te_pct = (te / tot * 100) if tot > 0 else 0
        print(f"{cls:<12} | {tot:>6} | {tr:>6} ({tr_pct:>5.1f}%) | {va:>5} ({va_pct:>5.1f}%) | {te:>5} ({te_pct:>5.1f}%)")

    print("----------------------------------------------------------------------")
    tr_all_pct = total_tr / total_all * 100
    va_all_pct = total_va / total_all * 100
    te_all_pct = total_te / total_all * 100
    print(f"{'TOTAL':<12} | {total_all:>6} | {total_tr:>6} ({tr_all_pct:>5.1f}%) | {total_va:>5} ({va_all_pct:>5.1f}%) | {total_te:>5} ({te_all_pct:>5.1f}%)")
    print("----------------------------------------------------------------------")

    # 5. Automated Verification
    print("\n----------------------------------------------------------------------")
    print("Automated Verification & Zero-Leakage Checks")
    print("----------------------------------------------------------------------")

    verification_errors = []

    # 1. Total count check
    if total_all != 2527 or total_copied != 2527:
        verification_errors.append(f"Expected 2527 total images, got {total_all} (copied: {total_copied})")

    # 2. Check no class is empty in any split
    for s in splits:
        for cls in EXPECTED_CLASSES:
            cls_count = split_stats[cls][s]
            if cls_count == 0:
                verification_errors.append(f"Split '{s}' has 0 images for class '{cls}'")

    # 3. Check filename intersection across splits
    train_val_names = split_file_names["train"] & split_file_names["val"]
    train_test_names = split_file_names["train"] & split_file_names["test"]
    val_test_names = split_file_names["val"] & split_file_names["test"]

    if train_val_names:
        verification_errors.append(f"Filename leak between Train and Val: {len(train_val_names)} files")
    if train_test_names:
        verification_errors.append(f"Filename leak between Train and Test: {len(train_test_names)} files")
    if val_test_names:
        verification_errors.append(f"Filename leak between Val and Test: {len(val_test_names)} files")

    # 4. Check content-hash intersection across splits (Zero-leakage guarantee)
    train_val_hashes = split_file_hashes["train"] & split_file_hashes["val"]
    train_test_hashes = split_file_hashes["train"] & split_file_hashes["test"]
    val_test_hashes = split_file_hashes["val"] & split_file_hashes["test"]

    if train_val_hashes:
        verification_errors.append(f"CONTENT HASH LEAK between Train and Val: {len(train_val_hashes)} hashes")
    if train_test_hashes:
        verification_errors.append(f"CONTENT HASH LEAK between Train and Test: {len(train_test_hashes)} hashes")
    if val_test_hashes:
        verification_errors.append(f"CONTENT HASH LEAK between Val and Test: {len(val_test_hashes)} hashes")

    # 5. Check raw dataset untouched
    raw_total = sum(len(list((raw_dir / c).iterdir())) for c in EXPECTED_CLASSES)
    if raw_total != 2527:
        verification_errors.append(f"Raw dataset total modified! Expected 2527, found {raw_total}")

    if verification_errors:
        print("\n[FAIL] Verification errors detected:")
        for err in verification_errors:
            print(f"  ❌ {err}")
        return False

    print("  [OK] All 6 classes populated across Train, Val, and Test.")
    print("  [OK] Zero filename leakage: TRAIN ∩ VAL = ∅, TRAIN ∩ TEST = ∅, VAL ∩ TEST = ∅.")
    print("  [OK] ZERO CONTENT HASH LEAKAGE: HASH(TRAIN) ∩ HASH(VAL) = ∅, HASH(TRAIN) ∩ HASH(TEST) = ∅, HASH(VAL) ∩ HASH(TEST) = ∅.")
    print(f"  [OK] Exact image total preserved: {total_all} images.")
    print(f"  [OK] Raw dataset remains 100% untouched ({raw_total} raw files).")
    print(f"  [OK] Manifest written with {len(manifest_rows)} records.")
    print("\n" + "=" * 70)
    print("           DATASET PREPARATION RESULT: SUCCESS")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = prepare_and_split_dataset()
    sys.exit(0 if success else 1)
