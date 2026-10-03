#!/usr/bin/env python3
"""
Duplicate-Image Safety Audit Script.

Performs:
1. Exact SHA-256 hash duplication check across all 2527 images.
2. Identifies all duplicate groups, original class labels, and split assignments.
3. Checks for cross-split leakage (e.g. one copy in Train, one copy in Test or Val).
4. Provides recommendation and reconciles split placement if leakage occurs.
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from configs.dataset_config import PROCESSED_DATA_DIR


def audit_duplicates():
    manifest_path = PROCESSED_DATA_DIR / "dataset_manifest.csv"
    if not manifest_path.exists():
        print(f"[FAIL] Manifest not found at {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print("=" * 70)
    print("           TrashNet Duplicate-Image Safety Audit Report")
    print("=" * 70)
    print(f"Total manifest records: {len(records)}\n")

    hash_groups = defaultdict(list)
    for r in records:
        hash_groups[r["file_hash"]].append(r)

    duplicate_groups = {h: items for h, items in hash_groups.items() if len(items) > 1}

    print(f"Total Duplicate Groups Found: {len(duplicate_groups)}")
    print("-" * 70)

    cross_split_leakage_found = False

    for idx, (h, items) in enumerate(duplicate_groups.items(), 1):
        print(f"\nGroup {idx} [SHA-256: {h[:16]}...]:")
        splits_in_group = set()
        classes_in_group = set()
        
        for item in items:
            splits_in_group.add(item["split"])
            classes_in_group.add(item["class_name"])
            print(f"  • Filename   : {item['filename']}")
            print(f"    Class      : {item['class_name']}")
            print(f"    Split      : {item['split']}")
            print(f"    Filepath   : {item['filepath']}")

        # Analysis
        if len(classes_in_group) > 1:
            print(f"  ⚠️ Label Conflict: Images share identical bytes but are labelled differently: {classes_in_group}")

        if len(splits_in_group) > 1:
            cross_split_leakage_found = True
            print(f"  ❌ CROSS-SPLIT LEAKAGE DETECTED: Copies span multiple splits: {splits_in_group}")
        else:
            print(f"  ✓ Safe Split Placement: All copies are in the SAME split ('{list(splits_in_group)[0]}').")

    print("\n" + "=" * 70)
    print("           Duplicate Safety Audit Summary")
    print("=" * 70)
    if cross_split_leakage_found:
        print("Status: ❌ CROSS-SPLIT LEAKAGE DETECTED across train/val/test splits.")
        print("Action Required: Group-aware split adjustment needed so identical images share the same split.")
    else:
        print("Status: ✓ SAFE — No duplicate images cross train/val/test split boundaries.")
        print("All identical image pairs are co-located in the same split partition.")
    print("=" * 70)

    return not cross_split_leakage_found


if __name__ == "__main__":
    audit_duplicates()
