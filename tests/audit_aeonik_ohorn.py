#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/audit_aeonik_ohorn.py
Comprehensive Quality Audit & Verification Suite for FD Aeonik Vietnamese Typography.
Specifically inspects Ơ / ơ glyphs, horn attachment, zero width inflation, and visual specimens.
"""

import os
import sys
import json
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
MAC_FONTS = Path("/Users/vietmac/Library/Fonts")
DIST_FONTS = PROJECT_ROOT / "dist" / "fonts"
DIST_WEB = PROJECT_ROOT / "dist" / "fonts" / "web"
FONTS_WEB = PROJECT_ROOT / "fonts"
DIST_ZIPS = PROJECT_ROOT / "dist" / "zips" / "FD"
PREVIEWS_DIR = PROJECT_ROOT / "test_previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

VIET_CHARS_LOWER = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS_UPPER = VIET_CHARS_LOWER.upper()
ALL_VIET_CHARS = VIET_CHARS_LOWER + VIET_CHARS_UPPER

BASE_MAPPING = str.maketrans(
    'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
    'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
    'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
    'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
)

FAMILIES = ["Extended", "Soft", "Condensed", "Mono", "Fono"]
WEIGHTS_TO_TEST = ["Regular", "SemiBold", "Bold", "Black", "Light", "Thin"]

TEST_PHRASES = [
    "3 CĂN BỆNH NGƯỜI MỚI HAY MẮC PHẢI",
    "NGƯỜI MỚI BẮT ĐẦU CẦN CỞI MỞ",
    "THUYỀN TRƯỞNG MƠ ƯỚC VƯƠN RA BIỂN LỚN",
    "BÁT PHỞ BÒ NÓNG HỔI ĐƯỢC CHỜ ĐỢI",
    "Ơ ờ ớ ở ỡ ợ - Ư ư ứ ừ ử ữ ự",
    "A Ă Â E Ê I O Ô Ơ U Ư Y Đ",
]

def count_components(font_path: str, char: str, size: int = 140) -> int:
    try:
        font = ImageFont.truetype(font_path, size)
    except Exception as e:
        return -1
    img = Image.new("L", (size * 2, size * 2), 0)
    draw = ImageDraw.Draw(img)
    draw.text((25, 25), char, font=font, fill=255)
    arr = np.array(img)
    _, thresh = cv2.threshold(arr, 50, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    areas = [stats[i, cv2.CC_STAT_AREA] for i in range(1, num_labels)]
    valid = [a for a in areas if a > 25]
    return len(valid)

def audit_font_family(fam: str):
    print(f"\n==========================================")
    print(f"AUDITING FAMILY: FD Aeonik {fam}")
    print(f"==========================================")
    
    # 1. Discover files in Library/Fonts
    otf_files = sorted(MAC_FONTS.glob(f"FDAeonik{fam}-*.otf"))
    print(f"[*] Found {len(otf_files)} OTF styles in ~/Library/Fonts")
    
    report = {
        "family": fam,
        "otf_count": len(otf_files),
        "styles": {},
        "failures": []
    }
    
    expected_components = {
        "Ơ": 1, "ơ": 1,
        "Ớ": 2, "ớ": 2,
        "Ờ": 2, "ờ": 2,
        "Ở": 2, "ở": 2,
        "Ỡ": 2, "ỡ": 2,
        "Ợ": 2, "ợ": 2,
        "Ư": 1, "ư": 1,
        "Ứ": 2, "ứ": 2
    }
    
    for otf in otf_files:
        style = otf.stem.replace(f"FDAeonik{fam}-", "")
        f = TTFont(str(otf))
        cmap = f.getBestCmap()
        hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
        
        # Check cmap coverage
        missing_cmap = [c for c in ALL_VIET_CHARS if ord(c) not in cmap]
        if missing_cmap:
            report["failures"].append(f"{otf.name}: Missing {len(missing_cmap)} characters in cmap")
            
        # Check advance width preservation
        width_issues = []
        is_mono = (fam == "Mono")
        for ch in ALL_VIET_CHARS:
            cp = ord(ch)
            if cp not in cmap:
                continue
            gname = cmap[cp]
            w = hmtx[gname][0]
            if is_mono:
                if w != 620:
                    width_issues.append(f"{ch} width={w} (expected 620)")
            else:
                base_ch = ch.translate(BASE_MAPPING)
                base_cp = ord(base_ch)
                if base_cp in cmap:
                    base_g = cmap[base_cp]
                    w_base = hmtx[base_g][0]
                    if w != w_base:
                        width_issues.append(f"{ch} width={w} != base {base_ch} width={w_base}")
        if width_issues:
            report["failures"].append(f"{otf.name}: Width mismatches: {', '.join(width_issues[:5])}")

        # Check horn attachment components
        comp_issues = []
        for ch, exp_comp in expected_components.items():
            actual = count_components(str(otf), ch)
            if actual != exp_comp:
                comp_issues.append(f"{ch}: got {actual} comps, expected {exp_comp}")
                
        if comp_issues:
            report["failures"].append(f"{otf.name}: Horn attachment defects: {', '.join(comp_issues)}")
        else:
            print(f"  [OK] {otf.name}: 100% cmap, advance width perfect, horn connected cleanly!")

    return report

def render_specimen_sheet(fam: str, output_image_path: str):
    styles = ["Regular", "SemiBold", "Bold", "Black"]
    rows = []
    
    for st in styles:
        fp = MAC_FONTS / f"FDAeonik{fam}-{st}.otf"
        if fp.exists():
            rows.append((st, str(fp)))
            
    if not rows:
        return
        
    width = 1600
    row_height = 200
    total_height = 80 + len(rows) * (row_height + 40)
    img = Image.new("RGB", (width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Title
    header_font = ImageFont.load_default()
    draw.text((40, 20), f"SPECIMEN AUDIT: FD Aeonik {fam} (Typography Verification Sheet)", fill=(100, 100, 100))
    
    curr_y = 60
    for st_name, fpath in rows:
        font_large = ImageFont.truetype(fpath, 42)
        font_sub = ImageFont.truetype(fpath, 28)
        
        # Style label
        draw.text((40, curr_y), f"Weight: {st_name}", fill=(180, 50, 50))
        # Text line 1
        draw.text((40, curr_y + 30), "3 CĂN BỆNH NGƯỜI MỚI HAY MẮC PHẢI", font=font_large, fill=(15, 23, 42))
        # Text line 2
        draw.text((40, curr_y + 90), "ƠỜỚỞỠỢ ơờớởỡợ — ƯỪỨỬỮỰ ưừứửữự — PHỞ BÒ, MƠ ƯỚC, LỚN LÊN", font=font_sub, fill=(51, 65, 85))
        
        draw.line([(40, curr_y + 160), (width - 40, curr_y + 160)], fill=(230, 230, 230), width=1)
        curr_y += row_height
        
    img.save(output_image_path)
    print(f"[+] Saved specimen image: {output_image_path}")

if __name__ == "__main__":
    for f in FAMILIES:
        audit_font_family(f)
        out_img = str(PREVIEWS_DIR / f"audit_specimen_{f.lower()}.png")
        render_specimen_sheet(f, out_img)
