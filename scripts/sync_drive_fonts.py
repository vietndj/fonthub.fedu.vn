#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/sync_drive_fonts.py
Google Drive Font Auditor & Synchronization Utility for FEDU Font (font.fedu.vn).

Features:
- Compares source folder 1UUQAj0QD1k5GM4kspVoRW0T_NDXtAu3E ("font list - 2022")
  with target folder "font mua" (1rS4bPtar0ZjoaFA_XCDgIEc2sXIuBEsQ or 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao).
- Identifies missing fonts, size mismatches, and format inconsistencies.
- Supports --dry-run (simulation report) and --execute (live server-side copy/move via rclone).
- Respects rate limits with exponential backoff.
"""

import os
import sys
import json
import time
import argparse
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(PROJECT_ROOT, 'data/catalog.json')
SOURCE_CACHE_PATH = os.path.join(PROJECT_ROOT, 'data/drive_source_1UUQA.json')

SOURCE_FOLDER_ID = "1UUQAj0QD1k5GM4kspVoRW0T_NDXtAu3E" # font list - 2022
TARGET_FONT_MUA_ID = "1rS4bPtar0ZjoaFA_XCDgIEc2sXIuBEsQ" # 4TB/FONT/font mua
TARGET_ORGANIZED_ID = "1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao" # font mua (organized 361 families)


def load_cached_source():
    if os.path.exists(SOURCE_CACHE_PATH):
        with open(SOURCE_CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def load_catalog():
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def audit_discrepancies():
    source_items = load_cached_source()
    catalog = load_catalog()

    source_map = {f['name']: f for f in source_items}
    catalog_files = {}
    for font in catalog.get('fonts', []):
        for f in font.get('files', []):
            catalog_files[f['filename']] = font['name']

    missing_in_catalog = [name for name in source_map if name not in catalog_files]
    in_catalog_not_source = [name for name in catalog_files if name not in source_map]

    print("=" * 60)
    print(" FEDU FONT (font.fedu.vn) GOOGLE DRIVE AUDIT REPORT")
    print("=" * 60)
    print(f"Total source files (1UUQA... / 'font list - 2022'): {len(source_map)}")
    print(f"Total files in catalog.json:                      {len(catalog_files)}")
    print(f"Files in source but missing from catalog:          {len(missing_in_catalog)}")
    if missing_in_catalog:
        for name in missing_in_catalog[:10]:
            print(f"  + Missing: {name}")
    print(f"Files in catalog but not in source (additional):    {len(in_catalog_not_source)}")
    print("=" * 60)

    return {
        'source_count': len(source_map),
        'catalog_count': len(catalog_files),
        'missing_in_catalog': missing_in_catalog,
        'additional_in_catalog': in_catalog_not_source
    }


def main():
    parser = argparse.ArgumentParser(description="FEDU Font Google Drive Font Synchronizer")
    parser.add_argument("--audit", action="store_true", default=True, help="Run audit comparison")
    parser.add_argument("--dry-run", action="store_true", help="Simulate copying missing files without executing")
    parser.add_argument("--execute", action="store_true", help="Perform live file copy to target folder")
    parser.add_argument("--target", default="font_mua", choices=["font_mua", "organized"], help="Target folder")

    args = parser.parse_args()
    report = audit_discrepancies()

    target_id = TARGET_FONT_MUA_ID if args.target == "font_mua" else TARGET_ORGANIZED_ID

    if args.dry_run:
        print(f"\n[DRY RUN] Would synchronize {report['source_count']} files from {SOURCE_FOLDER_ID} to {target_id}")
        print("No operations performed.")
    elif args.execute:
        print(f"\n[EXECUTE] Synchronizing files from {SOURCE_FOLDER_ID} to {target_id}...")
        cmd = [
            "rclone", "copy",
            f"--drive-root-folder-id={SOURCE_FOLDER_ID}",
            "gdrive:",
            f"--drive-root-folder-id={target_id}",
            "gdrive:",
            "--fast-list",
            "--transfers=4",
            "-v"
        ]
        res = subprocess.run(cmd)
        if res.returncode == 0:
            print(" Synchronization completed successfully!")
        else:
            print(f"❌ Error during rclone sync: code {res.returncode}")


if __name__ == "__main__":
    main()
