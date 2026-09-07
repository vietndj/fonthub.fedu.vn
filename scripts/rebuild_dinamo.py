#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/rebuild_dinamo.py
Rebuilds the 64 styles of Dinamo to apply the exact advance width invariance fix for i-variants (ì, í, ỉ, ĩ).
Repacks the 4 Dinamo zips and FD-Dinamo-Collection.zip.
"""

import os
import sys
import zipfile
import multiprocessing
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_fd_fontmoi import (
    FONTMOI_DIR, DIST_FONTS, DIST_ZIPS_FD, SPECS, worker_task
)

def main():
    dinamo_zip = FONTMOI_DIR / "DINAMO Trial Fonts.zip"
    print(f"Reading Dinamo fonts from {dinamo_zip}...")
    tasks = []
    with zipfile.ZipFile(dinamo_zip, 'r') as zf:
        for fn in sorted(zf.namelist()):
            if fn.lower().endswith('.otf') and not fn.startswith('__MACOSX'):
                raw_bytes = zf.read(fn)
                parts = fn.split('/')
                subfam_dir = parts[1].replace('ABC ', '')
                fam_core = subfam_dir
                stem = parts[-1].replace('.otf', '')
                style = stem.split('-')[1].replace('Trial', '')
                if style == 'RegularItalic': style = 'Regular Italic'
                elif style == 'BoldItalic': style = 'Bold Italic'
                elif style == 'LightItalic': style = 'Light Italic'
                elif style == 'MediumItalic': style = 'Medium Italic'
                elif style == 'ThinItalic': style = 'Thin Italic'
                elif style == 'HeavyItalic': style = 'Heavy Italic'
                elif style == 'BlackItalic': style = 'Black Italic'
                elif style == 'UltraItalic': style = 'Ultra Italic'
                
                is_mono = 'mono' in fam_core.lower() and 'semi' not in fam_core.lower()
                is_serif = False
                tasks.append((raw_bytes, fam_core, style, "Dinamo", is_serif, is_mono, fam_core))

    print(f"Executing {len(tasks)} Dinamo styles with multiprocessing...")
    with multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), 8)) as pool:
        results = pool.map(worker_task, tasks)

    successes = [r for r in results if r.get("status") == "SUCCESS"]
    print(f"Successfully processed {len(successes)}/{len(tasks)} Dinamo styles.")

    # Repack individual family zips & master zip
    fam_styles = {}
    for r in successes:
        fam = r["family_core"]
        fam_styles.setdefault(fam, []).append(r)

    dinamo_all_files = []
    for fam_name, styles in fam_styles.items():
        spec = SPECS.get(fam_name)
        if not spec:
            continue
        slug = spec["slug"]
        zip_path = DIST_ZIPS_FD / f"FD-{slug}.zip"
        with zipfile.ZipFile(str(zip_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for s in styles:
                ps = s["ps_name"]
                otf_file = DIST_FONTS / f"{ps}.otf"
                ttf_file = DIST_FONTS / f"{ps}.ttf"
                if otf_file.exists():
                    z.write(str(otf_file), f"{ps}.otf")
                    dinamo_all_files.append((str(otf_file), f"OTF/{ps}.otf"))
                if ttf_file.exists():
                    z.write(str(ttf_file), f"{ps}.ttf")
                    dinamo_all_files.append((str(ttf_file), f"TTF/{ps}.ttf"))
        print(f"✓ Re-packed FD-{slug}.zip ({len(styles)} styles)")

    master_path = DIST_ZIPS_FD / "FD-Dinamo-Collection.zip"
    with zipfile.ZipFile(str(master_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, arcname in set(dinamo_all_files):
            z.write(fpath, arcname)
    print(f"✓ Re-packed FD-Dinamo-Collection.zip ({len(set(dinamo_all_files))} files)")

if __name__ == '__main__':
    main()
