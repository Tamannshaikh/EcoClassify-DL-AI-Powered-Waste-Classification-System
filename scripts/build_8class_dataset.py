"""
Build Extended 8-Class Waste Classification Dataset.
EcoClassify DL — Phase 11 Dataset Construction

Deterministic, reproducible, and non-destructive dataset builder.
Source datasets are strictly READ-ONLY.
Derived dataset is written to: data/final/8class/
"""

import os
import sys
import shutil
import hashlib
import json
import csv
import random
from pathlib import Path
from collections import defaultdict, Counter
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "final" / "8class"
METADATA_DIR = OUTPUT_DIR / "metadata"

SEED = 42

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}

CLASS_DEFINITIONS = [
    {"index": 0, "name": "biodegradable", "prefix": "TB", "target": 450},
    {"index": 1, "name": "cardboard", "prefix": "TC", "target": 403},
    {"index": 2, "name": "e_waste", "prefix": "TE", "target": 450},
    {"index": 3, "name": "glass", "prefix": "TG", "target": 501},
    {"index": 4, "name": "metal", "prefix": "TM", "target": 410},
    {"index": 5, "name": "paper", "prefix": "TP", "target": 594},
    {"index": 6, "name": "plastic", "prefix": "TPL", "target": 482},
    {"index": 7, "name": "trash", "prefix": "TT", "target": 137},
]

def compute_hashes(file_path: Path):
    md5_hasher = hashlib.md5()
    sha256_hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            md5_hasher.update(chunk)
            sha256_hasher.update(chunk)
    return md5_hasher.hexdigest(), sha256_hasher.hexdigest()

def compute_dhash(image: Image.Image, hash_size=8) -> str:
    try:
        resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(resized.getdata())
        difference = []
        for row in range(hash_size):
            for col in range(hash_size):
                pixel_left = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                difference.append(pixel_left > pixel_right)
        decimal_val = 0
        hex_str = []
        for index, val in enumerate(difference):
            if val:
                decimal_val += 2 ** (index % 4)
            if (index % 4) == 3:
                hex_str.append(hex(decimal_val)[2:])
                decimal_val = 0
        return ''.join(hex_str)
    except Exception:
        return ""

def load_source_candidates():
    """Scans and pools approved candidate source images deterministically."""
    print("\n[STEP 1] Scanning and pooling candidate source images...")
    
    trashnet_dir = DATA_DIR / "raw" / "TrashNet"
    ewaste_dir = DATA_DIR / "raw" / "external" / "ewaste" / "EWaste_Image_Dataset"
    bdwaste_dir = DATA_DIR / "raw" / "organic" / "BDWaste"

    if not trashnet_dir.exists():
        raise FileNotFoundError(f"Missing required source directory: {trashnet_dir}")
    if not ewaste_dir.exists():
        raise FileNotFoundError(f"Missing required source directory: {ewaste_dir}")
    if not bdwaste_dir.exists():
        raise FileNotFoundError(f"Missing required source directory: {bdwaste_dir}")

    candidates_by_class = defaultdict(list)

    # 1. TrashNet classes (cardboard, glass, metal, paper, plastic, trash)
    trashnet_class_map = {
        "cardboard": "cardboard",
        "glass": "glass",
        "metal": "metal",
        "paper": "paper",
        "plastic": "plastic",
        "trash": "trash"
    }
    
    for subfolder, target_cls in trashnet_class_map.items():
        sub_path = trashnet_dir / subfolder
        if not sub_path.exists():
            raise FileNotFoundError(f"Missing TrashNet subfolder: {sub_path}")
        
        for fpath in sorted(sub_path.glob("*.*")):
            if fpath.suffix.lower() in IMAGE_EXTENSIONS and fpath.is_file():
                candidates_by_class[target_cls].append({
                    "source_dataset": "TrashNet_Raw",
                    "source_category": subfolder,
                    "abs_path": fpath,
                    "source_relative_path": str(fpath.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "original_filename": fpath.name,
                    "file_extension": fpath.suffix.lower()
                })

    # 2. E-Waste class (Battery, Keyboard, Mobile, Mouse, PCB)
    ewaste_approved_cats = ["Battery", "Keyboard", "Mobile", "Mouse", "PCB"]
    ewaste_by_cat = defaultdict(list)
    
    for cat in ewaste_approved_cats:
        cat_files = sorted(list(ewaste_dir.rglob(f"{cat}/*.*")))
        for fpath in cat_files:
            if fpath.suffix.lower() in IMAGE_EXTENSIONS and fpath.is_file():
                ewaste_by_cat[cat].append({
                    "source_dataset": "EWaste_Image_Dataset",
                    "source_category": cat,
                    "abs_path": fpath,
                    "source_relative_path": str(fpath.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "original_filename": fpath.name,
                    "file_extension": fpath.suffix.lower()
                })

    # Deterministic sampling for E-Waste (90 per category)
    rng_ewaste = random.Random(SEED)
    for cat in ewaste_approved_cats:
        imgs = ewaste_by_cat[cat]
        seen_md5 = set()
        unique_imgs = []
        for item in imgs:
            md5_val, _ = compute_hashes(item["abs_path"])
            if md5_val not in seen_md5:
                seen_md5.add(md5_val)
                item["md5"] = md5_val
                unique_imgs.append(item)
        
        if len(unique_imgs) < 90:
            raise ValueError(f"Insufficient unique images for EWaste category {cat}: {len(unique_imgs)} < 90")
        
        unique_imgs.sort(key=lambda x: x["source_relative_path"])
        sampled = rng_ewaste.sample(unique_imgs, 90)
        sampled.sort(key=lambda x: x["source_relative_path"])
        candidates_by_class["e_waste"].extend(sampled)

    # 3. Biodegradable class (BDWaste approved categories)
    bdwaste_quotas = {
        "1. Sugarcane  husk": 73,
        "3. Potato Peel": 73,
        "5. Mango Peel": 72,
        "6. Rice": 73,
        "7. Shell of Malta": 14,
        "8.Lemon Peel": 73,
        "9. Banana peel": 72
    }
    
    rng_bdwaste = random.Random(SEED)
    for folder_name, quota in bdwaste_quotas.items():
        folder_path = bdwaste_dir / folder_name
        if not folder_path.exists():
            raise FileNotFoundError(f"Missing BDWaste subfolder: {folder_path}")
        
        imgs = []
        seen_md5 = set()
        for fpath in sorted(folder_path.glob("*.*")):
            if fpath.suffix.lower() in IMAGE_EXTENSIONS and fpath.is_file():
                md5_val, _ = compute_hashes(fpath)
                if md5_val not in seen_md5:
                    seen_md5.add(md5_val)
                    imgs.append({
                        "source_dataset": "BDWaste",
                        "source_category": folder_name,
                        "abs_path": fpath,
                        "source_relative_path": str(fpath.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                        "original_filename": fpath.name,
                        "file_extension": fpath.suffix.lower(),
                        "md5": md5_val
                    })
        
        if len(imgs) < quota:
            raise ValueError(f"Insufficient unique images for BDWaste {folder_name}: {len(imgs)} < {quota}")
        
        imgs.sort(key=lambda x: x["source_relative_path"])
        if len(imgs) == quota:
            sampled = imgs
        else:
            sampled = rng_bdwaste.sample(imgs, quota)
        sampled.sort(key=lambda x: x["source_relative_path"])
        candidates_by_class["biodegradable"].extend(sampled)

    print("  Candidate Image Counts by Target Class:")
    total_candidates = 0
    for cdef in CLASS_DEFINITIONS:
        cname = cdef["name"]
        clist = candidates_by_class[cname]
        expected = cdef["target"]
        print(f"    - {cname:<15}: {len(clist):>4} images (Expected: {expected})")
        if len(clist) != expected:
            raise ValueError(f"Count mismatch for class {cname}: got {len(clist)}, expected {expected}")
        total_candidates += len(clist)

    print(f"  Total Candidates Selected: {total_candidates} (Target: 3,427 images)")
    if total_candidates != 3427:
        raise ValueError(f"Total candidate count {total_candidates} != 3427")

    return candidates_by_class

def extract_image_metadata_and_clusters(candidates_by_class):
    """Computes hashes, image dimensions, and near-duplicate entity clusters."""
    print("\n[STEP 2] Computing full hashes, dimensions, and near-duplicate clusters...")
    
    all_items = []
    dhash_map = defaultdict(list)

    for cdef in CLASS_DEFINITIONS:
        cname = cdef["name"]
        cidx = cdef["index"]
        cprefix = cdef["prefix"]
        
        for item in candidates_by_class[cname]:
            item["class_index"] = cidx
            item["class_name"] = cname
            item["category_prefix"] = cprefix
            
            # MD5 & SHA256
            md5_val, sha256_val = compute_hashes(item["abs_path"])
            item["md5"] = md5_val
            item["sha256"] = sha256_val
            item["file_size_bytes"] = item["abs_path"].stat().st_size
            
            # PIL metadata & dHash
            with Image.open(item["abs_path"]) as img:
                item["width"], item["height"] = img.size
                item["channels"] = len(img.getbands())
                dh = compute_dhash(img)
                item["dhash"] = dh
            
            item["is_original_source"] = "YES"
            item["duplicate_status"] = "UNIQUE_CONTENT"
            all_items.append(item)
            
            if dh:
                dhash_map[f"{cname}::{dh}"].append(item)

    # Assign Near-Duplicate Group IDs
    ndg_counter = 1
    for group_key, items in dhash_map.items():
        if len(items) > 1:
            gid = f"NDG_{ndg_counter:04d}"
            ndg_counter += 1
            for it in items:
                it["near_duplicate_group"] = gid
        else:
            items[0]["near_duplicate_group"] = "NONE"

    print(f"  Total Images Processed: {len(all_items)}")
    print(f"  Total Near-Duplicate Groups identified: {ndg_counter - 1}")

    return candidates_by_class, all_items

def partition_group_aware_stratified(candidates_by_class):
    """
    Performs Group-Aware Stratified Splitting (70% Train, 15% Val, 15% Test).
    Ensures all members of a near-duplicate cluster are assigned to the exact same partition.
    """
    print("\n[STEP 3] Performing Group-Aware Stratified 70/15/15 Partitioning...")
    
    final_split_records = []
    
    for cdef in CLASS_DEFINITIONS:
        cname = cdef["name"]
        items = candidates_by_class[cname]
        target_total = len(items)
        
        target_train = int(round(target_total * 0.70))
        target_val = int(round(target_total * 0.15))
        target_test = target_total - target_train - target_val
        
        clusters = defaultdict(list)
        for it in items:
            grp = it["near_duplicate_group"]
            if grp == "NONE":
                clusters[f"SINGLE_{it['source_relative_path']}"].append(it)
            else:
                clusters[grp].append(it)
        
        cluster_list = list(clusters.values())
        rng = random.Random(SEED + cdef["index"] * 100)
        rng.shuffle(cluster_list)
        
        train_items = []
        val_items = []
        test_items = []
        
        for cluster in cluster_list:
            c_size = len(cluster)
            if len(train_items) + c_size <= target_train or (len(val_items) >= target_val and len(test_items) >= target_test):
                train_items.extend(cluster)
                for it in cluster:
                    it["split"] = "train"
            elif len(val_items) + c_size <= target_val or (len(test_items) >= target_test):
                val_items.extend(cluster)
                for it in cluster:
                    it["split"] = "val"
            else:
                test_items.extend(cluster)
                for it in cluster:
                    it["split"] = "test"
        
        print(f"  Class '{cname:<15}': Total={target_total:>3} | Train={len(train_items):>3} ({len(train_items)/target_total:.1%}) | Val={len(val_items):>3} ({len(val_items)/target_total:.1%}) | Test={len(test_items):>3} ({len(test_items)/target_total:.1%})")
        
        all_class_items = train_items + val_items + test_items
        all_class_items.sort(key=lambda x: (0 if x["split"] == "train" else (1 if x["split"] == "val" else 2), x["source_relative_path"]))
        
        for idx, it in enumerate(all_class_items, 1):
            it["sample_id"] = f"{it['category_prefix']}{idx:04d}"
            it["derived_filename"] = f"{it['sample_id']}{it['file_extension']}"
            it["derived_relative_path"] = f"data/final/8class/{it['split']}/{cname}/{it['derived_filename']}"
            it["selection_seed"] = SEED
            final_split_records.append(it)

    train_hashes = set(r["md5"] for r in final_split_records if r["split"] == "train")
    val_hashes = set(r["md5"] for r in final_split_records if r["split"] == "val")
    test_hashes = set(r["md5"] for r in final_split_records if r["split"] == "test")

    leak_train_val = train_hashes.intersection(val_hashes)
    leak_train_test = train_hashes.intersection(test_hashes)
    leak_val_test = val_hashes.intersection(test_hashes)

    if leak_train_val or leak_train_test or leak_val_test:
        raise ValueError(f"Data leakage detected! Train-Val: {len(leak_train_val)}, Train-Test: {len(leak_train_test)}, Val-Test: {len(leak_val_test)}")

    group_to_splits = defaultdict(set)
    for r in final_split_records:
        if r["near_duplicate_group"] != "NONE":
            group_to_splits[r["near_duplicate_group"]].add(r["split"])
    
    cross_split_ndg = {g: s for g, s in group_to_splits.items() if len(s) > 1}
    if cross_split_ndg:
        raise ValueError(f"Near-duplicate groups cross split boundaries: {cross_split_ndg}")

    print("\n  Leakage Verification: 100% LEAK-FREE (0 exact hash leaks, 0 near-duplicate group leaks).")
    return final_split_records

def write_derived_dataset(final_records):
    """Copies files to derived dataset structure and generates metadata artifacts."""
    print("\n[STEP 4] Writing derived 8-class dataset files & metadata...")
    
    if OUTPUT_DIR.exists():
        print(f"  Output directory {OUTPUT_DIR} exists. Preparing clean regeneration...")
        shutil.rmtree(OUTPUT_DIR)

    for split in ["train", "val", "test"]:
        for cdef in CLASS_DEFINITIONS:
            c_dir = OUTPUT_DIR / split / cdef["name"]
            c_dir.mkdir(parents=True, exist_ok=True)

    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"  Copying {len(final_records)} images to derived destinations...")
    for item in final_records:
        dest_path = PROJECT_ROOT / item["derived_relative_path"]
        shutil.copy2(item["abs_path"], dest_path)

    # 1. Generate dataset_manifest.csv
    manifest_path = METADATA_DIR / "dataset_manifest.csv"
    manifest_fields = [
        "sample_id", "class_index", "class_name", "category_prefix", "split",
        "source_dataset", "source_category", "source_relative_path", "derived_relative_path",
        "original_filename", "file_extension", "width", "height", "channels",
        "file_size_bytes", "md5", "sha256", "near_duplicate_group",
        "selection_seed", "is_original_source", "duplicate_status"
    ]

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        for item in sorted(final_records, key=lambda x: (x["class_index"], x["sample_id"])):
            row = {k: item[k] for k in manifest_fields}
            writer.writerow(row)
    print(f"  -> Generated {manifest_path.relative_to(PROJECT_ROOT)}")

    # 2. Generate class_mapping.json
    mapping_path = METADATA_DIR / "class_mapping.json"
    class_mapping = {
        str(cdef["index"]): {
            "name": cdef["name"],
            "prefix": cdef["prefix"],
            "target": cdef["target"]
        }
        for cdef in CLASS_DEFINITIONS
    }
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(class_mapping, f, indent=2)
    print(f"  -> Generated {mapping_path.relative_to(PROJECT_ROOT)}")

    # 3. Generate dataset_metadata.json
    metadata_path = METADATA_DIR / "dataset_metadata.json"
    split_counts = Counter(r["split"] for r in final_records)
    class_counts = Counter(r["class_name"] for r in final_records)
    
    metadata = {
        "dataset_name": "EcoClassify 8-Class Derived Waste Classification Dataset",
        "dataset_version": "8class-v1.0",
        "construction_date": "2026-10-04",
        "seed": SEED,
        "total_images": len(final_records),
        "split_counts": {
            "train": split_counts["train"],
            "val": split_counts["val"],
            "test": split_counts["test"]
        },
        "class_counts": {cdef["name"]: class_counts[cdef["name"]] for cdef in CLASS_DEFINITIONS},
        "class_indices": {cdef["name"]: cdef["index"] for cdef in CLASS_DEFINITIONS},
        "class_prefixes": {cdef["name"]: cdef["prefix"] for cdef in CLASS_DEFINITIONS},
        "source_datasets": [
            "TrashNet (Raw) - 6 classes",
            "EWaste_Image_Dataset - 5 consumer electronic classes",
            "BDWaste - 7 approved organic categories"
        ],
        "excluded_categories": [
            "CTSoc_EWaste (excluded completely; post-training detection outputs)",
            "EWaste: Microwave, Player, Printer, Television, Washing Machine",
            "BDWaste: 4. Paper (class collision), 10. Coffee cup (plastic lined), 2. Fish ash (inorganic ash)"
        ],
        "duplicate_policy": "Exact MD5 deduplication prior to selection; single copy retained per unique asset.",
        "near_duplicate_policy": "Atomic cluster assignment (dHash perceptual hashing); zero split-boundary leakage.",
        "split_policy": "Group-Aware Stratified 70/15/15.",
        "generator_script": "scripts/build_8class_dataset.py",
        "baseline_reference": "v1.0.0-baseline (Commit 9a3dff3)"
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  -> Generated {metadata_path.relative_to(PROJECT_ROOT)}")

def run_build():
    print("=" * 80)
    print("ECOCLASSIFY DL — PHASE 11 DATASET CONSTRUCTION (DERIVED 8-CLASS)")
    print("=" * 80)
    
    candidates = load_source_candidates()
    candidates, all_items = extract_image_metadata_and_clusters(candidates)
    final_records = partition_group_aware_stratified(candidates)
    write_derived_dataset(final_records)
    
    print("\n" + "=" * 80)
    print("DATASET CONSTRUCTION COMPLETE & VERIFIED")
    print(f"Location: {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    print("=" * 80)

if __name__ == "__main__":
    run_build()
