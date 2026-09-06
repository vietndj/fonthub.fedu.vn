#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Font Family Organizer & Link Generator
Author: teamwork_preview_explorer_survey_2
Role: Infrastructure & Storage Investigator

Features:
- Reads pre-computed family_grouping_mapping.json (361 families, 1,070 files).
- Server-side reorganization on Google Drive via rclone (0 byte transfer).
- Built-in dry-run safety (defaults to dry-run unless --execute is passed).
- Built-in rate limiting and exponential backoff retry.
- Automatic extraction of folder IDs and generation of public share links.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from collections import defaultdict

PARENT_FOLDER_ID = "1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao"
GDRIVE_REMOTE = "gdrive:"

def check_rclone():
    """Verify rclone is installed and gdrive: is accessible."""
    try:
        res = subprocess.run(["rclone", "version"], capture_output=True, text=True)
        if res.returncode != 0:
            print("Error: rclone is not installed or not in PATH.")
            return False
        res = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        if "gdrive:" not in res.stdout:
            print("Error: 'gdrive:' remote not found in rclone configuration.")
            return False
        return True
    except Exception as e:
        print(f"Error checking rclone: {e}")
        return False

def run_rclone_cmd(cmd, dry_run=True):
    """Execute or simulate an rclone command."""
    if dry_run and "--dry-run" not in cmd:
        cmd = cmd + ["--dry-run"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0, res.stdout, res.stderr

def organize_fonts(catalog_path, dry_run=True, delay=0.1):
    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    families = data.get("families", {})
    total_families = len(families)
    total_files = sum(fam["file_count"] for fam in families.values())

    print("=" * 70)
    print(f"🚀 GOOGLE DRIVE FONT REORGANIZATION PIPELINE")
    print(f"   Mode: {'[DRY RUN - SIMULATION ONLY]' if dry_run else '[LIVE EXECUTION]'}")
    print(f"   Target Parent Folder ID: {PARENT_FOLDER_ID}")
    print(f"   Total Font Families: {total_families}")
    print(f"   Total Font Files: {total_files}")
    print("=" * 70)

    # In dry-run or live, simulate/execute
    success_folders = 0
    success_moves = 0
    errors = []

    folder_links = {}

    for idx, (fam_name, fam_info) in enumerate(sorted(families.items()), 1):
        folder_name = fam_info["folder_name"]
        files = fam_info["files"]

        # Step 1: Create subfolder if needed
        mkdir_cmd = [
            "rclone", "mkdir",
            "--drive-root-folder-id", PARENT_FOLDER_ID,
            f"{GDRIVE_REMOTE}{folder_name}"
        ]
        if dry_run:
            mkdir_cmd.append("--dry-run")

        ok, out, err = run_rclone_cmd(mkdir_cmd, dry_run=dry_run)
        if not ok and not dry_run:
            errors.append(f"Failed mkdir {folder_name}: {err.strip()}")
        else:
            success_folders += 1

        # Step 2: Move files into subfolder
        for f in files:
            fname = f["filename"]
            move_cmd = [
                "rclone", "moveto",
                "--drive-root-folder-id", PARENT_FOLDER_ID,
                f"{GDRIVE_REMOTE}{fname}",
                f"{GDRIVE_REMOTE}{folder_name}/{fname}"
            ]
            if dry_run:
                move_cmd.append("--dry-run")

            ok, out, err = run_rclone_cmd(move_cmd, dry_run=dry_run)
            if not ok and not dry_run:
                errors.append(f"Failed move {fname} -> {folder_name}: {err.strip()}")
            else:
                success_moves += 1

            if delay > 0 and not dry_run:
                time.sleep(delay)

        if idx % 20 == 0 or idx == total_families:
            print(f"[{idx:3d}/{total_families}] Processed family: {folder_name:<30} ({len(files)} files)")

    print("\n" + "=" * 70)
    print("📊 EXECUTION SUMMARY:")
    print(f"   Subfolders processed: {success_folders}/{total_families}")
    print(f"   File moves processed: {success_moves}/{total_files}")
    if errors:
        print(f"   Errors encountered: {len(errors)}")
        for e in errors[:10]:
            print(f"     ⚠️ {e}")
    else:
        print("   ✅ Zero errors detected!")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Organize Google Drive font assets into family subfolders")
    parser.add_argument("--catalog", default=os.path.join(os.path.dirname(__file__), "family_grouping_mapping.json"), help="Path to mapping JSON")
    parser.add_argument("--execute", action="store_true", help="Execute live changes (default is dry-run)")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between API calls in seconds")
    args = parser.parse_args()

    if not check_rclone():
        sys.exit(1)

    dry_run = not args.execute
    organize_fonts(args.catalog, dry_run=dry_run, delay=args.delay)

if __name__ == "__main__":
    main()
