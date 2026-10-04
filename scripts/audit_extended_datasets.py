"""
Comprehensive Non-Destructive Extended 8-Class Dataset Audit Script.
Audits TrashNet, EWaste_Image_Dataset, CTSoc_EWaste, and BDWaste.
Generates CSV reports and metrics for documentation.
DOES NOT MODIFY, MOVE, RENAME, OR DELETE ANY FILE.
"""
import os
import sys
import hashlib
import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
from PIL import Image

# Setup directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "dataset_audit"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}

def compute_md5(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_dhash(image: Image.Image, hash_size=8) -> str:
    """Computes difference hash (dHash) for near-duplicate detection."""
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

def run_audit():
    print("=" * 70)
    print("STARTING EXTENDED 8-CLASS DATASET AUDIT (READ-ONLY)")
    print("=" * 70)

    # 1. Identify dataset sources
    sources = {
        "TrashNet_Raw": DATA_DIR / "raw" / "TrashNet",
        "TrashNet_Processed_Train": DATA_DIR / "processed" / "train",
        "TrashNet_Processed_Val": DATA_DIR / "processed" / "val",
        "TrashNet_Processed_Test": DATA_DIR / "processed" / "test",
        "EWaste_Image_Dataset_Train": DATA_DIR / "raw" / "external" / "ewaste" / "EWaste_Image_Dataset" / "train",
        "EWaste_Image_Dataset_Val": DATA_DIR / "raw" / "external" / "ewaste" / "EWaste_Image_Dataset" / "val",
        "EWaste_Image_Dataset_Test": DATA_DIR / "raw" / "external" / "ewaste" / "EWaste_Image_Dataset" / "test",
        "CTSoc_EWaste_DatasetPrep": DATA_DIR / "raw" / "external" / "ewaste" / "CTSoc_EWaste" / "ctsoc-ewaste-main" / "dataset" / "dataset-preparation",
        "CTSoc_EWaste_Results": DATA_DIR / "raw" / "external" / "ewaste" / "CTSoc_EWaste" / "ctsoc-ewaste-main" / "results",
        "BDWaste_Organic": DATA_DIR / "raw" / "organic" / "BDWaste"
    }

    all_files_records = []
    md5_to_records = defaultdict(list)
    dhash_to_records = defaultdict(list)
    corrupted_files = []
    non_image_files = []

    inventory_stats = defaultdict(lambda: {
        "total_files": 0,
        "valid_images": 0,
        "corrupted": 0,
        "non_image": 0,
        "total_size_bytes": 0,
        "extensions": Counter(),
        "color_modes": Counter(),
        "dimensions": Counter(),
        "widths": [],
        "heights": []
    })

    print("\n[STEP 1] Scanning and analyzing all file assets across dataset roots...")

    for src_name, src_path in sources.items():
        if not src_path.exists():
            print(f"  [WARN] Path does not exist: {src_path}")
            continue

        for root, dirs, files in os.walk(src_path):
            for fname in files:
                fpath = Path(root) / fname
                rel_path = fpath.relative_to(PROJECT_ROOT)
                file_ext = fpath.suffix.lower()
                file_size = fpath.stat().st_size
                
                # Derive class/category from subfolder relative to source
                sub_rel = fpath.relative_to(src_path)
                category = sub_rel.parts[0] if len(sub_rel.parts) > 1 else "root"

                stat_key = (src_name, category)
                stats = inventory_stats[stat_key]
                stats["total_files"] += 1
                stats["total_size_bytes"] += file_size
                stats["extensions"][file_ext] += 1

                if file_ext not in IMAGE_EXTENSIONS:
                    stats["non_image"] += 1
                    non_image_files.append({
                        "source": src_name,
                        "category": category,
                        "path": str(rel_path),
                        "size_bytes": file_size,
                        "reason": "Non-image extension"
                    })
                    continue

                # Validate image reading
                try:
                    md5_hash = compute_md5(fpath)
                    with Image.open(fpath) as img:
                        img.verify()
                    
                    with Image.open(fpath) as img:
                        width, height = img.size
                        mode = img.mode
                        dhash = compute_dhash(img)

                    stats["valid_images"] += 1
                    stats["color_modes"][mode] += 1
                    stats["dimensions"][(width, height)] += 1
                    stats["widths"].append(width)
                    stats["heights"].append(height)

                    record = {
                        "source": src_name,
                        "category": category,
                        "filename": fname,
                        "relative_path": str(rel_path),
                        "extension": file_ext,
                        "size_bytes": file_size,
                        "width": width,
                        "height": height,
                        "mode": mode,
                        "md5": md5_hash,
                        "dhash": dhash
                    }
                    all_files_records.append(record)
                    md5_to_records[md5_hash].append(record)
                    if dhash:
                        dhash_to_records[dhash].append(record)

                except Exception as e:
                    stats["corrupted"] += 1
                    corrupted_files.append({
                        "source": src_name,
                        "category": category,
                        "path": str(rel_path),
                        "size_bytes": file_size,
                        "error": str(e)
                    })

    print(f"  -> Total records analyzed: {len(all_files_records)}")
    print(f"  -> Corrupted images: {len(corrupted_files)}")
    print(f"  -> Non-image files: {len(non_image_files)}")

    # 2. Duplicate Analysis
    print("\n[STEP 2] Running Exact & Perceptual Duplicate Audits...")
    exact_duplicates = []
    for md5_val, recs in md5_to_records.items():
        if len(recs) > 1:
            sources_involved = list(set(r["source"] for r in recs))
            categories_involved = list(set(f"{r['source']}::{r['category']}" for r in recs))
            exact_duplicates.append({
                "type": "EXACT_MD5",
                "hash": md5_val,
                "count": len(recs),
                "sources": "; ".join(sources_involved),
                "categories": "; ".join(categories_involved),
                "paths": "; ".join(r["relative_path"] for r in recs)
            })

    # Near-duplicates (dHash identical, but different MD5)
    near_duplicates = []
    for dh_val, recs in dhash_to_records.items():
        unique_md5s = set(r["md5"] for r in recs)
        if len(unique_md5s) > 1:
            sources_involved = list(set(r["source"] for r in recs))
            categories_involved = list(set(f"{r['source']}::{r['category']}" for r in recs))
            near_duplicates.append({
                "type": "NEAR_DHASH",
                "hash": dh_val,
                "count": len(recs),
                "distinct_md5_count": len(unique_md5s),
                "sources": "; ".join(sources_involved),
                "categories": "; ".join(categories_involved),
                "paths": "; ".join(r["relative_path"] for r in recs)
            })

    print(f"  -> Exact duplicate hash groups: {len(exact_duplicates)}")
    print(f"  -> Near-duplicate hash groups: {len(near_duplicates)}")

    # 3. Check Split Leakage for EWaste_Image_Dataset
    print("\n[STEP 3] Auditing EWaste_Image_Dataset Split Leakage...")
    ewaste_train_hashes = set(r["md5"] for r in all_files_records if r["source"] == "EWaste_Image_Dataset_Train")
    ewaste_val_hashes = set(r["md5"] for r in all_files_records if r["source"] == "EWaste_Image_Dataset_Val")
    ewaste_test_hashes = set(r["md5"] for r in all_files_records if r["source"] == "EWaste_Image_Dataset_Test")

    leak_train_val = ewaste_train_hashes.intersection(ewaste_val_hashes)
    leak_train_test = ewaste_train_hashes.intersection(ewaste_test_hashes)
    leak_val_test = ewaste_val_hashes.intersection(ewaste_test_hashes)

    print(f"  -> EWaste Train-Val Exact Leaks: {len(leak_train_val)}")
    print(f"  -> EWaste Train-Test Exact Leaks: {len(leak_train_test)}")
    print(f"  -> EWaste Val-Test Exact Leaks: {len(leak_val_test)}")

    # Check Processed TrashNet Split Leakage
    tn_train_hashes = set(r["md5"] for r in all_files_records if r["source"] == "TrashNet_Processed_Train")
    tn_val_hashes = set(r["md5"] for r in all_files_records if r["source"] == "TrashNet_Processed_Val")
    tn_test_hashes = set(r["md5"] for r in all_files_records if r["source"] == "TrashNet_Processed_Test")

    tn_leak_tr_val = tn_train_hashes.intersection(tn_val_hashes)
    tn_leak_tr_ts = tn_train_hashes.intersection(tn_test_hashes)
    tn_leak_val_ts = tn_val_hashes.intersection(tn_test_hashes)

    print(f"  -> TrashNet Processed Train-Val Exact Leaks: {len(tn_leak_tr_val)}")
    print(f"  -> TrashNet Processed Train-Test Exact Leaks: {len(tn_leak_tr_ts)}")
    print(f"  -> TrashNet Processed Val-Test Exact Leaks: {len(tn_leak_val_ts)}")

    # 4. Generate CSV: extended_dataset_inventory.csv
    inventory_csv_path = ARTIFACTS_DIR / "extended_dataset_inventory.csv"
    with open(inventory_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Source", "Category", "TotalFiles", "ValidImages", "CorruptedImages", "NonImageFiles",
            "TotalSizeBytes", "TotalSizeMB", "Extensions", "ColorModes", "MinDimensions", "MaxDimensions", "MostCommonDimensions"
        ])
        for (src_name, cat), stats in sorted(inventory_stats.items()):
            ext_str = "; ".join(f"{k}:{v}" for k, v in stats["extensions"].items())
            modes_str = "; ".join(f"{k}:{v}" for k, v in stats["color_modes"].items())
            
            min_dim = f"{min(stats['widths'])}x{min(stats['heights'])}" if stats['widths'] else "N/A"
            max_dim = f"{max(stats['widths'])}x{max(stats['heights'])}" if stats['widths'] else "N/A"
            common_dim = stats["dimensions"].most_common(1)[0][0] if stats["dimensions"] else "N/A"
            common_dim_str = f"{common_dim[0]}x{common_dim[1]}" if isinstance(common_dim, tuple) else "N/A"
            
            size_mb = round(stats["total_size_bytes"] / (1024 * 1024), 2)

            writer.writerow([
                src_name, cat, stats["total_files"], stats["valid_images"], stats["corrupted"], stats["non_image"],
                stats["total_size_bytes"], size_mb, ext_str, modes_str, min_dim, max_dim, common_dim_str
            ])
    print(f"\n  [SAVED] {inventory_csv_path}")

    # 5. Generate CSV: duplicate_report.csv
    duplicate_csv_path = ARTIFACTS_DIR / "duplicate_report.csv"
    with open(duplicate_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Hash", "Occurrences", "Sources", "Categories", "FilePaths"])
        for d in exact_duplicates:
            writer.writerow([d["type"], d["hash"], d["count"], d["sources"], d["categories"], d["paths"]])
        for d in near_duplicates:
            writer.writerow([d["type"], d["hash"], d["count"], d["sources"], d["categories"], d["paths"]])
    print(f"  [SAVED] {duplicate_csv_path}")

    # 6. Generate CSV: proposed_8class_mapping.csv
    proposed_mapping_path = ARTIFACTS_DIR / "proposed_8class_mapping.csv"
    proposed_mappings = [
        # TrashNet Existing 6 Classes
        {"TargetClass": "cardboard", "Source": "TrashNet_Raw", "SourceCategory": "cardboard", "AvailableCount": 403, "Action": "INCLUDE", "Rationale": "Original TrashNet class, verified high quality"},
        {"TargetClass": "glass", "Source": "TrashNet_Raw", "SourceCategory": "glass", "AvailableCount": 501, "Action": "INCLUDE", "Rationale": "Original TrashNet class, verified high quality"},
        {"TargetClass": "metal", "Source": "TrashNet_Raw", "SourceCategory": "metal", "AvailableCount": 410, "Action": "INCLUDE", "Rationale": "Original TrashNet class, verified high quality"},
        {"TargetClass": "paper", "Source": "TrashNet_Raw", "SourceCategory": "paper", "AvailableCount": 594, "Action": "INCLUDE", "Rationale": "Original TrashNet class, verified high quality"},
        {"TargetClass": "plastic", "Source": "TrashNet_Raw", "SourceCategory": "plastic", "AvailableCount": 482, "Action": "INCLUDE", "Rationale": "Original TrashNet class, verified high quality"},
        {"TargetClass": "trash", "Source": "TrashNet_Raw", "SourceCategory": "trash", "AvailableCount": 137, "Action": "INCLUDE", "Rationale": "Original TrashNet residual class"},
        
        # E-Waste Candidates (EWaste_Image_Dataset)
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Battery", "AvailableCount": 300, "Action": "INCLUDE_BALANCED", "Rationale": "High-impact hazardous electronic component"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Mobile", "AvailableCount": 300, "Action": "INCLUDE_BALANCED", "Rationale": "Ubiquitous consumer electronics"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Mouse", "AvailableCount": 300, "Action": "INCLUDE_BALANCED", "Rationale": "Standard peripheral e-waste"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Keyboard", "AvailableCount": 300, "Action": "INCLUDE_BALANCED", "Rationale": "Standard peripheral e-waste"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "PCB", "AvailableCount": 300, "Action": "INCLUDE_BALANCED", "Rationale": "Distinctive internal electronic circuitry"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Microwave", "AvailableCount": 300, "Action": "EXCLUDE_OR_SAMPLE", "Rationale": "Large appliance; sample subset if needed"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Player", "AvailableCount": 300, "Action": "EXCLUDE_OR_SAMPLE", "Rationale": "Consumer media device; sample subset if needed"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Printer", "AvailableCount": 300, "Action": "EXCLUDE_OR_SAMPLE", "Rationale": "Office electronics; sample subset if needed"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Television", "AvailableCount": 300, "Action": "EXCLUDE_OR_SAMPLE", "Rationale": "Large screen display; sample subset if needed"},
        {"TargetClass": "e_waste", "Source": "EWaste_Image_Dataset", "SourceCategory": "Washing Machine", "AvailableCount": 300, "Action": "EXCLUDE_OR_SAMPLE", "Rationale": "Bulky white-goods appliance"},
        
        # CTSoc E-Waste Candidates
        {"TargetClass": "e_waste", "Source": "CTSoc_EWaste", "SourceCategory": "dataset-preparation", "AvailableCount": 8, "Action": "EXCLUDE", "Rationale": "Small non-representative sample set (8 images)"},
        {"TargetClass": "e_waste", "Source": "CTSoc_EWaste", "SourceCategory": "results", "AvailableCount": 47, "Action": "EXCLUDE", "Rationale": "Detection bounding box outputs, loss curves, and evaluation charts (not raw training images)"},

        # BDWaste Organic Candidates
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Banana peel", "AvailableCount": 123, "Action": "INCLUDE", "Rationale": "Archetypal organic food waste"},
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Potato Peel", "AvailableCount": 130, "Action": "INCLUDE", "Rationale": "Common household vegetable waste"},
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Mango Peel", "AvailableCount": 121, "Action": "INCLUDE", "Rationale": "Standard organic fruit waste"},
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Lemon Peel", "AvailableCount": 125, "Action": "INCLUDE", "Rationale": "Standard citrus organic waste"},
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Shell of Malta", "AvailableCount": 126, "Action": "INCLUDE", "Rationale": "Citrus / fruit peel organic waste"},
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Rice", "AvailableCount": 127, "Action": "INCLUDE", "Rationale": "Staple leftover cooked/uncooked organic food"},
        {"TargetClass": "biodegradable", "Source": "BDWaste", "SourceCategory": "Sugarcane husk", "AvailableCount": 125, "Action": "INCLUDE", "Rationale": "Fibrous agricultural plant biomass waste"},
        
        # BDWaste Categories that MUST be EXCLUDED from Biodegradable
        {"TargetClass": "paper", "Source": "BDWaste", "SourceCategory": "4. Paper", "AvailableCount": 124, "Action": "EXCLUDE_FROM_ORGANIC", "Rationale": "Paper is already a primary dry recyclable class in TrashNet (must not contaminate organic class)"},
        {"TargetClass": "trash", "Source": "BDWaste", "SourceCategory": "10. Coffee cup", "AvailableCount": 126, "Action": "EXCLUDE_FROM_ORGANIC", "Rationale": "Disposable coffee cups feature polyethylene/plastic linings and are non-compostable composite items"},
        {"TargetClass": "trash", "Source": "BDWaste", "SourceCategory": "2. Fish ash", "AvailableCount": 125, "Action": "EXCLUDE_FROM_ORGANIC", "Rationale": "Incinerated mineral ash residue is inorganic / inert, not compostable raw organic matter"}
    ]

    with open(proposed_mapping_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetClass", "Source", "SourceCategory", "AvailableCount", "Action", "Rationale"])
        writer.writeheader()
        writer.writerows(proposed_mappings)
    print(f"  [SAVED] {proposed_mapping_path}")

    # Summary metrics
    summary = {
        "TrashNet_Raw_Total": sum(stats["valid_images"] for (src, cat), stats in inventory_stats.items() if src == "TrashNet_Raw"),
        "TrashNet_Raw_By_Class": {cat: stats["valid_images"] for (src, cat), stats in inventory_stats.items() if src == "TrashNet_Raw"},
        "EWaste_Image_Dataset_Total": sum(stats["valid_images"] for (src, cat), stats in inventory_stats.items() if "EWaste_Image_Dataset" in src),
        "BDWaste_Total": sum(stats["valid_images"] for (src, cat), stats in inventory_stats.items() if src == "BDWaste_Organic"),
        "CTSoc_EWaste_Total": sum(stats["valid_images"] for (src, cat), stats in inventory_stats.items() if "CTSoc_EWaste" in src),
        "Total_Corrupted": len(corrupted_files),
        "Total_Non_Image": len(non_image_files),
        "Exact_Duplicate_Groups": len(exact_duplicates),
        "Near_Duplicate_Groups": len(near_duplicates)
    }

    print("\n" + "=" * 70)
    print("EXTENDED DATASET AUDIT SUMMARY:")
    print("=" * 70)
    print(json.dumps(summary, indent=2))
    print("=" * 70)

if __name__ == "__main__":
    run_audit()
