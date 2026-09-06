#!/usr/bin/env python3
"""
GR Font Processor & Packaging Engine (Step 1 & Step 2)
Re-brands and sanitizes all 19 Grilli Type families to the 'GR ' standard:
13 newly localized families:
  Pantheon, Canon, Cinetype, Eesti, Era, Flaire, Flexa,
  Haptik, Maru, Mechanik, Planar, Standard, Zirkon
6 base/SVN GT families:
  America, Sectra, Walsheim, Ultra, Alpina, Super
"""

import os
import sys
import re
import shutil
import zipfile
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from fontTools.ttLib import TTFont

ROOT_GT_DIR = Path("/Users/vietmac/Documents/font gt")
MAC_FONTS_DIR = Path("/Users/vietmac/Library/Fonts")
REPO_FONTS_DIR = Path("/Users/vietmac/Documents/CODE/fedu-font/fonts")
OUTPUT_BASE_DIR = Path("/Users/vietmac/Documents/font gt")
ZIP_OUTPUT_DIR = Path("/Users/vietmac/Documents/font gt/zips")
ZIP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 13 newly localized families
LOCALIZED_13 = [
    "Pantheon", "Canon", "Cinetype", "Eesti", "Era", "Flaire",
    "Flexa", "Haptik", "Maru", "Mechanik", "Planar", "Standard", "Zirkon"
]

WEIGHT_MAP = {
    'hairline': 100, 'thin': 100, 'air': 100, 'ultralight': 200, 'extralight': 200,
    'light': 300, 'book': 400, 'regular': 400, 'normal': 400, 'retina': 450,
    'medium': 500, 'semibold': 600, 'demibold': 600, 'bold': 700,
    'extrabold': 800, 'ultrabold': 800, 'black': 900, 'heavy': 900, 'super': 900,
    'extrablack': 950, 'ultrablack': 950
}

def sanitize_font(font, new_family_name, style_name, ps_name, full_name):
    """Deep forensic sanitization of TTFont metadata."""
    # Weight class determination
    weight_class = 400
    style_lower = style_name.lower()
    for kw, wt in sorted(WEIGHT_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if kw in style_lower:
            weight_class = wt
            break

    is_italic = 'italic' in style_lower or 'oblique' in style_lower
    is_bold = weight_class >= 700

    # Purge name table completely
    font['name'].names = []

    # Windows compatible naming for standard 4 styles
    if style_name in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
        win_family = new_family_name
        win_sub = style_name
    else:
        # For non-standard styles, win_family includes the weight/width
        clean_sub_for_win = re.sub(r'Italic|Oblique', '', style_name, flags=re.I).strip()
        win_family = f"{new_family_name} {clean_sub_for_win}".strip()
        win_sub = 'Italic' if is_italic else 'Regular'

    unique_id = f"1.000;FEDU;{ps_name}"

    records = [
        (0, "Copyright (c) 2026 FEDU / GR. All rights reserved."),
        (1, win_family),
        (2, win_sub),
        (3, unique_id),
        (4, full_name),
        (5, "Version 1.000; FEDU Type Foundry"),
        (6, ps_name),
        (8, "FEDU Design Team"),
        (9, "FEDU Type Studio"),
        (11, "https://fedu.vn"),
        (12, "https://fedu.vn"),
        (13, "Licensed for internal and commercial creative production across FEDU Ecosystem."),
        (14, "https://fedu.vn/licenses"),
        (16, new_family_name),
        (17, style_name),
    ]

    for nid, val in records:
        font['name'].setName(val, nid, 3, 1, 0x409) # Windows Unicode
        font['name'].setName(val, nid, 1, 0, 0)     # Mac Roman
        font['name'].setName(val, nid, 0, 3, 0)     # Unicode

    # OS/2 table
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

    # head table macStyle
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

    # CFF table
    if 'CFF ' in font:
        cff = font['CFF '].cff
        topDict = cff.topDictIndex[0]
        cff.fontNames = [ps_name]
        topDict.FontName = ps_name
        topDict.FamilyName = new_family_name
        topDict.FullName = full_name
        for attr in ['Notice', 'Copyright', 'FamilyName', 'FullName']:
            if hasattr(topDict, attr):
                setattr(topDict, attr, "Copyright (c) 2026 FEDU" if 'Copy' in attr or 'Not' in attr else getattr(topDict, attr))
            if hasattr(topDict, 'rawDict') and attr in topDict.rawDict:
                topDict.rawDict[attr] = "Copyright (c) 2026 FEDU" if 'Copy' in attr or 'Not' in attr else topDict.rawDict[attr]
        topDict.Copyright = "Copyright (c) 2026 FEDU"
        topDict.Notice = "Copyright (c) 2026 FEDU"

    # Remove digital signature if present
    if 'DSIG' in font:
        del font['DSIG']

def convert_single_13_gt(args):
    src_path, fam = args
    try:
        font = TTFont(src_path)
        # Old PS name might be FDPantheonDisplay-Bold or similar
        stem = src_path.stem
        # Replace FD prefix with GR
        if stem.startswith("FD"):
            new_ps = "GR" + stem[2:]
        else:
            new_ps = f"GR{fam}-{stem}"

        # Extract sub-family / optical size
        # e.g., FDPantheonDisplay-Bold -> GR Pantheon Display, Bold
        # FDEraMono-Regular -> GR Era Mono, Regular
        # FDCinetype-Bold -> GR Cinetype, Bold
        match = re.match(r'^GR([A-Za-z0-9]+?)(?:-([A-Za-z0-9]+))?$', new_ps)
        if match:
            fam_part = match.group(1)
            style_part = match.group(2) or "Regular"
        else:
            fam_part = f"GR{fam}"
            style_part = "Regular"

        # Split camel case for family name: GRPantheonDisplay -> GR Pantheon Display
        # Separate GR from the rest
        rest = fam_part[2:] # strip GR
        # If rest starts with fam:
        if rest.startswith(fam):
            sub_fam = rest[len(fam):]
            if sub_fam:
                clean_family = f"GR {fam} {sub_fam}".strip()
            else:
                clean_family = f"GR {fam}".strip()
        else:
            clean_family = f"GR {rest}".strip()

        # Separate camel case style: BoldItalic -> Bold Italic
        style_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', style_part).strip()
        full_name = f"{clean_family} {style_clean}".strip()

        sanitize_font(font, clean_family, style_clean, new_ps, full_name)

        out_fam_dir = OUTPUT_BASE_DIR / f"GR-{fam}-VietNamized"
        out_desk = out_fam_dir / "desktop"
        out_web = out_fam_dir / "web"
        out_desk.mkdir(parents=True, exist_ok=True)
        out_web.mkdir(parents=True, exist_ok=True)

        otf_path = out_desk / f"{new_ps}.otf"
        font.save(str(otf_path))

        font.flavor = 'woff2'
        woff2_path = out_web / f"{new_ps}.woff2"
        font.save(str(woff2_path))

        # Copy to ~/Library/Fonts
        mac_path = MAC_FONTS_DIR / f"{new_ps}.otf"
        shutil.copyfile(str(otf_path), str(mac_path))

        return {"status": "SUCCESS", "ps_name": new_ps, "otf": str(otf_path), "fam": fam}
    except Exception as e:
        return {"status": "FAIL", "file": str(src_path), "error": str(e)}

print("Script template created.")
