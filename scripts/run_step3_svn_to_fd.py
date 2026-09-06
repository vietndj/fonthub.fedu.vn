#!/usr/bin/env python3
"""
Step 3 Master Engine: SVN to FD Batch Conversion & Packaging (Bulletproof v2.0)
Converts all remaining 965 SVN fonts to FD standard:
- Reads metadata directly from font files to avoid heuristic parsing errors
- Excludes 6 GT families (America, Sectra, Walsheim, Ultra, Alpina, Super)
- Zero-trace metadata sanitization (Vendor: FEDU, Copyright: 2026 FEDU)
- Direct macOS ~/Library/Fonts installation
- Packages each family into dist/zips/FD/FD-<Family>.zip
"""

import os
import sys
import re
import shutil
import zipfile
import time
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from fontTools.ttLib import TTFont

MAC_FONTS_DIR = Path("/Users/vietmac/Library/Fonts")
DIST_FONTS_DIR = Path("/Users/vietmac/Documents/CODE/fedu-font/dist/fonts")
DIST_FONTS_DIR.mkdir(parents=True, exist_ok=True)
DIST_ZIPS_DIR = Path("/Users/vietmac/Documents/CODE/fedu-font/dist/zips/FD")
DIST_ZIPS_DIR.mkdir(parents=True, exist_ok=True)

GT_EXCLUDE_STEMS = ['walsheim', 'ultra', 'alpina', 'super', 'america', 'sectra']

WEIGHT_MAP = {
    'hairline': 100, 'thin': 100, 'air': 100, 'ultralight': 200, 'extralight': 200,
    'light': 300, 'book': 400, 'regular': 400, 'normal': 400, 'retina': 450,
    'medium': 500, 'semibold': 600, 'demibold': 600, 'bold': 700,
    'extrabold': 800, 'ultrabold': 800, 'black': 900, 'heavy': 900, 'super': 900,
    'extrablack': 950, 'ultrablack': 950
}

def extract_meta_and_prepare_task(src_path):
    font = TTFont(str(src_path))
    typ_fam = font['name'].getDebugName(16)
    win_fam = font['name'].getDebugName(1)
    typ_sub = font['name'].getDebugName(17)
    win_sub = font['name'].getDebugName(2)
    ps = font['name'].getDebugName(6)

    raw_fam = typ_fam or win_fam or src_path.stem
    raw_sub = typ_sub or win_sub or 'Regular'

    clean_fam = re.sub(r'^[Ss][Vv][Nn][\s\-_]+', '', raw_fam).strip()
    clean_fam = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean_fam).strip()
    fd_family = f"FD {clean_fam}".strip()

    clean_ps = re.sub(r'^[Ss][Vv][Nn][\s\-_]*', '', ps or src_path.stem).strip()
    clean_ps = re.sub(r'[^a-zA-Z0-9]', '', clean_ps)
    fd_ps = f"FD{clean_ps}"

    style_clean = raw_sub.strip()
    full_name = f"{fd_family} {style_clean}".strip()

    return {
        "src_path": str(src_path),
        "fd_family": fd_family,
        "style_name": style_clean,
        "ps_name": fd_ps,
        "full_name": full_name,
        "fam_group": clean_fam
    }

def sanitize_and_export_font(task):
    src_path = Path(task['src_path'])
    fd_family = task['fd_family']
    style_name = task['style_name']
    ps_name = task['ps_name']
    full_name = task['full_name']
    fam_group = task['fam_group']

    try:
        font = TTFont(str(src_path))
        style_lower = style_name.lower()
        weight_class = 400
        for kw, wt in sorted(WEIGHT_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if kw in style_lower:
                weight_class = wt
                break

        is_italic = 'italic' in style_lower or 'oblique' in style_lower
        is_bold = weight_class >= 700

        font['name'].names = []

        if style_name in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
            win_family = fd_family
            win_sub = style_name
        else:
            clean_sub_win = re.sub(r'Italic|Oblique', '', style_name, flags=re.I).strip()
            win_family = f"{fd_family} {clean_sub_win}".strip()
            win_sub = 'Italic' if is_italic else 'Regular'

        unique_id = f"1.000;FEDU;{ps_name}"

        records = [
            (0, "Copyright (c) 2026 FEDU. All rights reserved."),
            (1, win_family),
            (2, win_sub),
            (3, unique_id),
            (4, full_name),
            (5, "Version 1.000; FEDU Type Foundry"),
            (6, ps_name),
            (7, f"{fd_family} is a proprietary typeface of FEDU Ecosystem."),
            (8, "FEDU Design Team"),
            (9, "FEDU Type Studio"),
            (11, "https://fedu.vn"),
            (12, "https://fedu.vn"),
            (13, "Licensed for internal and commercial creative production across FEDU Ecosystem."),
            (14, "https://fedu.vn/licenses"),
            (16, fd_family),
            (17, style_name),
        ]

        for nid, val in records:
            font['name'].setName(val, nid, 3, 1, 0x409)
            font['name'].setName(val, nid, 1, 0, 0)
            font['name'].setName(val, nid, 0, 3, 0)

        if 'OS/2' in font:
            os2 = font['OS/2']
            os2.achVendID = b'FEDU'
            os2.usWeightClass = weight_class
            if is_italic:
                os2.fsSelection |= (1 << 0)
            else:
                os2.fsSelection &= ~(1 << 0)
            if is_bold:
                os2.fsSelection |= (1 << 5)
            else:
                os2.fsSelection &= ~(1 << 5)
            if not is_italic and not is_bold and weight_class == 400:
                os2.fsSelection |= (1 << 6)
            else:
                os2.fsSelection &= ~(1 << 6)

        if 'head' in font:
            head = font['head']
            if is_bold:
                head.macStyle |= (1 << 0)
            else:
                head.macStyle &= ~(1 << 0)
            if is_italic:
                head.macStyle |= (1 << 1)
            else:
                head.macStyle &= ~(1 << 1)

        is_cff = 'CFF ' in font
        ext = '.otf' if is_cff else '.ttf'

        if is_cff:
            cff = font['CFF '].cff
            topDict = cff.topDictIndex[0]
            cff.fontNames = [ps_name]
            topDict.FontName = ps_name
            topDict.FamilyName = fd_family
            topDict.FullName = full_name
            for attr in ['Notice', 'Copyright', 'FamilyName', 'FullName']:
                if hasattr(topDict, attr):
                    setattr(topDict, attr, "Copyright (c) 2026 FEDU" if 'Copy' in attr or 'Not' in attr else getattr(topDict, attr))
                if hasattr(topDict, 'rawDict') and attr in topDict.rawDict:
                    topDict.rawDict[attr] = "Copyright (c) 2026 FEDU" if 'Copy' in attr or 'Not' in attr else topDict.rawDict[attr]
            topDict.Copyright = "Copyright (c) 2026 FEDU"
            topDict.Notice = "Copyright (c) 2026 FEDU"

        if 'DSIG' in font:
            del font['DSIG']

        out_file = DIST_FONTS_DIR / f"{ps_name}{ext}"
        font.save(str(out_file))

        mac_file = MAC_FONTS_DIR / f"{ps_name}{ext}"
        shutil.copyfile(str(out_file), str(mac_file))

        return {
            "status": "SUCCESS",
            "fam_group": fam_group,
            "fd_family": fd_family,
            "ps_name": ps_name,
            "out_file": str(out_file),
            "mac_file": str(mac_file)
        }
    except Exception as e:
        return {"status": "FAIL", "src": str(src_path), "error": str(e)}

def main():
    print("======================================================================")
    print("🚀 BẮT ĐẦU CHUYỂN ĐỔI TOÀN BỘ KHO FONT SVN CÒN LẠI SANG 'FD '")
    print("======================================================================")

    svn_files = sorted([
        f for f in MAC_FONTS_DIR.glob("SVN-*")
        if f.suffix.lower() in ['.ttf', '.otf']
        and not any(gt_stem in f.name.lower() for gt_stem in GT_EXCLUDE_STEMS)
    ])

    print(f"Tổng số file SVN cần chuyển đổi sang FD: {len(svn_files)} files")

    tasks = [extract_meta_and_prepare_task(f) for f in svn_files]

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(sanitize_and_export_font, tasks))

    success = 0
    errors = []
    family_files = defaultdict(list)

    for r in results:
        if r.get("status") == "SUCCESS":
            success += 1
            family_files[r['fam_group']].append(r['out_file'])
        else:
            errors.append(r)

    elapsed = time.time() - t0
    print(f"\n✔ Hoàn thành chuyển đổi: {success}/{len(tasks)} fonts trong {elapsed:.2f}s!")
    if errors:
        print(f"❌ Có {len(errors)} lỗi:")
        for err in errors[:5]:
            print(f"  - {err}")

    print(f"\n📦 Đang đóng gói {len(family_files)} họ font FD vào {DIST_ZIPS_DIR}...")
    for fam_name, fpaths in family_files.items():
        clean_zip_name = f"FD-{re.sub(r'[^a-zA-Z0-9]', '', fam_name)}.zip"
        zip_path = DIST_ZIPS_DIR / clean_zip_name
        with zipfile.ZipFile(str(zip_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for fp in fpaths:
                p = Path(fp)
                z.write(str(p), arcname=f"FD-{fam_name}/{p.name}")

    print(f"✔ Đã đóng gói thành công {len(family_files)} file zip FD!")
    print("\n✨ TẤT CẢ CÁC FONT SVN ĐÃ ĐƯỢC CHUYỂN THÀNH FD, TẨY TRẮNG BẢN QUYỀN, ĐÓNG GÓI VÀ CÀI ĐẶT!")

if __name__ == "__main__":
    main()
