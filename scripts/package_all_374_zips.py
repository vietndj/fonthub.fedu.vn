#!/usr/bin/env python3
"""
scripts/package_all_374_zips.py
Ensure every single one of the 374 fonts in catalog.json has its own distinct,
dedicated .zip archive containing exclusively clean FD/GR font files.
"""

import json
import re
import os
import zipfile
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
CATALOG_PATH = PROJECT_ROOT / "data/catalog.json"
FONTS_JSON_PATH = PROJECT_ROOT / "data/fonts.json"
DIST_FONTS_DIR = PROJECT_ROOT / "dist/fonts"
DIST_ZIPS_FD = PROJECT_ROOT / "dist/zips/FD"
DIST_ZIPS_GR = PROJECT_ROOT / "dist/zips/GR"

DIST_ZIPS_FD.mkdir(parents=True, exist_ok=True)
DIST_ZIPS_GR.mkdir(parents=True, exist_ok=True)

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    catalog_data = json.load(f)

fonts = catalog_data["fonts"]
print(f"Loaded {len(fonts)} fonts from catalog.json")

# Map of all available font files in dist/fonts
all_font_files = list(DIST_FONTS_DIR.glob("*.*"))
print(f"Available font files in dist/fonts: {len(all_font_files)}")

# Build an index for fast matching
# normalized lowercase filename -> Path
file_index = {}
for p in all_font_files:
    # Key 1: exact stem lowercase without spaces or hyphens
    norm = re.sub(r'[^a-zA-Z0-9]', '', p.stem).lower()
    file_index[norm] = p

packaged_count = 0
unmatched_fonts = []

for font in fonts:
    fid = font["id"]
    name = font["name"]
    is_gr = fid.startswith("gr-") or name.startswith("GR ")
    
    # Target zip dir
    zip_dir = DIST_ZIPS_GR if is_gr else DIST_ZIPS_FD
    prefix = "GR" if is_gr else "FD"
    
    # Generate clean zip filename
    clean_name = re.sub(r'^(GR|FD)\s+', '', name).strip()
    slug_name = re.sub(r'[^a-zA-Z0-9]+', '', clean_name)
    zip_filename = f"{prefix}-{slug_name}.zip"
    zip_path = zip_dir / zip_filename
    
    # Find matching font files for this font family
    matching_files = []
    
    # 1. Check if font['files'] lists specific files
    if font.get("files") and isinstance(font["files"], list):
        for file_info in font["files"]:
            fname = file_info.get("filename") or file_info.get("source_filename") or ""
            norm_fname = re.sub(r'[^a-zA-Z0-9]', '', Path(fname).stem).lower()
            # Try to match
            if norm_fname in file_index:
                matching_files.append(file_index[norm_fname])
            else:
                # Try partial match
                for norm_key, p in file_index.items():
                    if norm_fname in norm_key or norm_key in norm_fname:
                        matching_files.append(p)
                        break

    # 2. If no files found from font['files'], search by name/family
    if not matching_files:
        norm_family = re.sub(r'[^a-zA-Z0-9]', '', clean_name).lower()
        for p in all_font_files:
            stem_norm = re.sub(r'[^a-zA-Z0-9]', '', p.stem).lower()
            if is_gr:
                if stem_norm.startswith("gr") and norm_family in stem_norm:
                    matching_files.append(p)
            else:
                if stem_norm.startswith("fd") and norm_family in stem_norm:
                    matching_files.append(p)

    # 3. If still not matched, check existing zip file if it already exists
    existing_zip = font.get("zip_url")
    if not matching_files and existing_zip and os.path.exists(existing_zip):
        # Already has a zip file
        zip_path = (PROJECT_ROOT / existing_zip).resolve()
        zip_filename = zip_path.name
    elif matching_files:
        # Deduplicate
        matching_files = list(dict.fromkeys(matching_files))
        # Write clean zip
        with zipfile.ZipFile(str(zip_path), "w", compression=zipfile.ZIP_DEFLATED) as z:
            for p in matching_files:
                arcname = f"{prefix}-{clean_name}/{p.name}"
                z.write(str(p), arcname=arcname)
        packaged_count += 1
    else:
        unmatched_fonts.append((fid, name))

    # Update font record
    rel_zip_path = str(zip_path.relative_to(PROJECT_ROOT))
    font["zip_filename"] = zip_filename
    font["zip_url"] = rel_zip_path
    font["download_url"] = rel_zip_path

print(f"Packaged {packaged_count} fonts into unique zips.")
if unmatched_fonts:
    print(f"⚠️ Unmatched ({len(unmatched_fonts)}):", unmatched_fonts[:10])
else:
    print("✅ All 374 fonts successfully matched and packaged!")

# Save updated catalog.json
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(catalog_data, f, indent=2, ensure_ascii=False)

# Save updated fonts.json
fonts_json_data = catalog_data["fonts"]
with open(FONTS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(fonts_json_data, f, indent=2, ensure_ascii=False)

print("Saved updated catalog.json and fonts.json!")
