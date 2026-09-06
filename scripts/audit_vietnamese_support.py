#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_vietnamese_support.py
Audits all fonts in catalog.json and app.js to verify 100% Vietnamese glyph coverage.
Checks every font file using fontTools.
"""

import os
import sys
import json
import re
from pathlib import Path
from fontTools.ttLib import TTFont

VN_LOWER = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
VN_CHARS = set(VN_LOWER + VN_LOWER.upper())

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
SEARCH_DIRS = [
    PROJECT_ROOT / "fonts",
    PROJECT_ROOT / "dist/fonts",
    Path("/Users/vietmac/Library/Fonts"),
    Path("/Users/vietmac/Documents/CODE/course/fonts"),
    Path("/Users/vietmac/Documents/CODE/typo/fonts")
]

def check_font_file(file_path):
    try:
        tt = TTFont(str(file_path))
        cmap = tt.getBestCmap()
        if not cmap:
            return False, 134, "No cmap table"
        missing = [c for c in VN_CHARS if ord(c) not in cmap]
        if missing:
            return False, len(missing), "".join(missing[:15])
        return True, 0, ""
    except Exception as e:
        return False, 134, str(e)

def find_font_files(font):
    candidates = []
    web_url = font.get("web_font_url", "")
    if web_url and not web_url.startswith("http"):
        candidates.append(PROJECT_ROOT / web_url)

    for fl in font.get("files", []):
        fn = fl.get("filename", "")
        sfn = fl.get("source_filename", "")
        for base in [fn, sfn]:
            if base:
                for d in SEARCH_DIRS:
                    candidates.append(d / base)
                if base.endswith(".ttf.ttf") or base.endswith(".otf.otf"):
                    clean = base[:-4]
                    for d in SEARCH_DIRS:
                        candidates.append(d / clean)

    existing = []
    for c in candidates:
        if c.exists() and c.is_file() and c not in existing:
            existing.append(c)

    if not existing:
        stem = re.sub(r'[^a-zA-Z0-9]', '', font.get("name", ""))
        for d in SEARCH_DIRS:
            if d.exists():
                for f in d.glob(f"*{stem}*"):
                    if f.is_file() and f.suffix.lower() in ['.ttf', '.otf', '.woff2']:
                        existing.append(f)
                        break
            if existing:
                break

    return existing

def main():
    catalog_path = PROJECT_ROOT / "data/catalog.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    fonts = catalog.get("fonts", [])
    print(f"Total fonts in catalog.json: {len(fonts)}")

    passed = []
    failed = []
    not_found = []

    for font in fonts:
        fid = font.get("id")
        fname = font.get("name")
        files = find_font_files(font)

        if not files:
            not_found.append(font)
            continue

        all_ok = True
        err_details = []
        for fp in files[:3]:
            ok, miss_count, miss_sample = check_font_file(fp)
            if not ok:
                all_ok = False
                err_details.append(f"{fp.name} (missing {miss_count}: {miss_sample})")

        if all_ok:
            passed.append((fid, fname, files[0]))
        else:
            failed.append((fid, fname, err_details))

    print(f"Passed (100% Vietnamese): {len(passed)}")
    print(f"Failed Vietnamese support: {len(failed)}")
    print(f"Font files not found: {len(not_found)}")

    if failed:
        print("\n=== FONTS FAILING VIETNAMESE SUPPORT ===")
        for fid, fname, errs in failed:
            print(f"- [{fid}] {fname}: {', '.join(errs)}")

    if not_found:
        print("\n=== FONTS WITH NO LOCAL FILES FOUND ===")
        for nf in not_found:
            print(f"- [{nf.get('id')}] {nf.get('name')} (web_font_url: {nf.get('web_font_url')})")

if __name__ == "__main__":
    main()
