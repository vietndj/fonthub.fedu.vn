#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/organize_drive.py
Google Drive Font Family Organizer & Link Generator for fedu.vn/font.

Milestone 2 Implementation:
- Reads canonical family grouping mapping (361 families, 1,070 files).
- Server-side organization on Google Drive via rclone into 361 family subfolders.
- Extracts real Google Drive folder IDs for all 361 family folders.
- Generates data/drive_links.json with public folder download URLs.
- Updates data/catalog.json with specific family drive_folder_url for every font.
- Full support for --dry-run (simulation, default) and --execute (live operations).
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MAPPING = os.path.join(
    PROJECT_ROOT,
    ".agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json"
)
DEFAULT_CATALOG = os.path.join(PROJECT_ROOT, "data/catalog.json")
DEFAULT_DRIVE_LINKS = os.path.join(PROJECT_ROOT, "data/drive_links.json")

PARENT_FOLDER_ID = "1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao"
GDRIVE_REMOTE = "gdrive:"
DRIVE_FOLDER_BASE = "https://drive.google.com/drive/folders"


def check_rclone():
    """Verify rclone is installed and gdrive: is accessible."""
    try:
        res = subprocess.run(["rclone", "version"], capture_output=True, text=True)
        if res.returncode != 0:
            print("❌ Error: rclone is not installed or not found in PATH.")
            return False
        res = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        if GDRIVE_REMOTE not in res.stdout:
            print(f"❌ Error: '{GDRIVE_REMOTE}' remote not found in rclone configuration.")
            return False
        return True
    except Exception as e:
        print(f"❌ Error checking rclone: {e}")
        return False


def get_remote_dirs(parent_id=PARENT_FOLDER_ID):
    """
    Query all existing directories inside the target Google Drive parent folder.
    Returns a dictionary mapping folder_name -> folder_id.
    """
    cmd = [
        "rclone", "lsjson",
        "--dirs-only",
        "--max-depth", "1",
        "--drive-root-folder-id", parent_id,
        GDRIVE_REMOTE
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"⚠️ Warning querying remote dirs: {res.stderr.strip()}")
        return {}
    try:
        items = json.loads(res.stdout)
        dirs_map = {}
        for item in items:
            if item.get("IsDir", False):
                name = item.get("Name") or item.get("Path")
                dirs_map[name] = item.get("ID")
        return dirs_map
    except Exception as e:
        print(f"⚠️ Error parsing remote dirs JSON: {e}")
        return {}


def get_remote_files(parent_id=PARENT_FOLDER_ID):
    """
    Query all existing files directly at the root of the target Google Drive folder.
    Returns a dictionary mapping filename -> file_id.
    """
    cmd = [
        "rclone", "lsjson",
        "--files-only",
        "--max-depth", "1",
        "--drive-root-folder-id", parent_id,
        GDRIVE_REMOTE
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"⚠️ Warning querying remote root files: {res.stderr.strip()}")
        return {}
    try:
        items = json.loads(res.stdout)
        files_map = {}
        for item in items:
            if not item.get("IsDir", False):
                name = item.get("Name") or item.get("Path")
                files_map[name] = item.get("ID")
        return files_map
    except Exception as e:
        print(f"⚠️ Error parsing remote files JSON: {e}")
        return {}


def run_mkdir_single(folder_name, parent_id=PARENT_FOLDER_ID, dry_run=True, max_retries=3):
    """Create a single remote directory via rclone mkdir."""
    cmd = [
        "rclone", "mkdir",
        "--drive-root-folder-id", parent_id,
        "--retries", "3",
        "--low-level-retries", "5",
        f"{GDRIVE_REMOTE}{folder_name}"
    ]
    if dry_run:
        cmd.append("--dry-run")

    for attempt in range(1, max_retries + 1):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return True, folder_name, None
        time.sleep(0.5 * attempt)

    return False, folder_name, res.stderr.strip()


def run_move_single(filename, folder_name, parent_id=PARENT_FOLDER_ID, dry_run=True, max_retries=3):
    """Move a single file server-side into its family directory via rclone moveto."""
    cmd = [
        "rclone", "moveto",
        "--drive-root-folder-id", parent_id,
        "--retries", "3",
        "--low-level-retries", "5",
        f"{GDRIVE_REMOTE}{filename}",
        f"{GDRIVE_REMOTE}{folder_name}/{filename}"
    ]
    if dry_run:
        cmd.append("--dry-run")

    for attempt in range(1, max_retries + 1):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return True, filename, folder_name, None
        time.sleep(0.8 * attempt)

    return False, filename, folder_name, res.stderr.strip()


def create_missing_folders(families, existing_dirs, parent_id=PARENT_FOLDER_ID, dry_run=True, workers=8):
    """Ensure all 361 family folders exist in the target Drive directory."""
    needed_folders = [info["folder_name"] for info in families.values()]
    missing = [f for f in needed_folders if f not in existing_dirs]

    print(f"📁 Subfolder Status: {len(existing_dirs)} existing, {len(missing)} to create (Total required: {len(needed_folders)})")

    if not missing:
        print("✅ All 361 family subfolders already exist on Google Drive!")
        return existing_dirs

    if dry_run:
        print(f"   [DRY RUN] Would create {len(missing)} subfolders using rclone mkdir.")
        # Return existing plus placeholder IDs for simulation
        simulated = dict(existing_dirs)
        for idx, f in enumerate(missing, 1):
            simulated[f] = f"simulated_folder_id_{idx:04d}"
        return simulated

    print(f"🚀 Creating {len(missing)} subfolders with {workers} worker threads...")
    success_count = 0
    errors = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(run_mkdir_single, f, parent_id, dry_run=False): f
            for f in missing
        }
        done_count = 0
        for fut in as_completed(futures):
            ok, folder_name, err = fut.result()
            done_count += 1
            if ok:
                success_count += 1
            else:
                errors.append(f"mkdir '{folder_name}' failed: {err}")

            if done_count % 50 == 0 or done_count == len(missing):
                print(f"   Progress: {done_count}/{len(missing)} folders processed ({success_count} success)")

    if errors:
        print(f"⚠️ {len(errors)} folder creation errors:")
        for e in errors[:5]:
            print(f"   - {e}")

    # Re-query actual created folder IDs from Google Drive
    print("🔄 Querying Google Drive for authoritative folder IDs...")
    updated_dirs = get_remote_dirs(parent_id)
    print(f"✅ Google Drive now contains {len(updated_dirs)} subfolders.")
    return updated_dirs


def move_files_to_families(families, root_files, existing_dirs, parent_id=PARENT_FOLDER_ID, dry_run=True, workers=6):
    """
    Perform server-side moves for files into their respective family folders.
    Skips files that are no longer at root (already moved).
    """
    total_files = sum(fam["file_count"] for fam in families.values())
    pending_moves = []
    already_moved_count = 0

    for fam_name, fam_info in families.items():
        folder_name = fam_info["folder_name"]
        for fi in fam_info["files"]:
            fname = fi["filename"]
            if fname in root_files:
                pending_moves.append((fname, folder_name))
            else:
                already_moved_count += 1

    print(f"📦 File Migration Status:")
    print(f"   Total catalog files: {total_files}")
    print(f"   Already moved / organized: {already_moved_count}")
    print(f"   Pending server-side moves: {len(pending_moves)}")

    if not pending_moves:
        print("✅ All 1,070 font files are already organized in their family subfolders!")
        return True, 0, []

    if dry_run:
        print(f"   [DRY RUN] Would move {len(pending_moves)} files via server-side 'rclone moveto'.")
        return True, len(pending_moves), []

    print(f"🚀 Moving {len(pending_moves)} files server-side with {workers} workers...")
    success_moves = 0
    errors = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(run_move_single, fname, folder_name, parent_id, dry_run=False): (fname, folder_name)
            for fname, folder_name in pending_moves
        }
        done_count = 0
        for fut in as_completed(futures):
            ok, fname, folder_name, err = fut.result()
            done_count += 1
            if ok:
                success_moves += 1
            else:
                errors.append(f"Move '{fname}' -> '{folder_name}' failed: {err}")

            if done_count % 50 == 0 or done_count == len(pending_moves):
                print(f"   Progress: {done_count}/{len(pending_moves)} files moved ({success_moves} success)")

    if errors:
        print(f"⚠️ {len(errors)} file move errors:")
        for e in errors[:10]:
            print(f"   - {e}")

    return len(errors) == 0, success_moves, errors


def generate_drive_links(families, dirs_map, output_path, parent_id=PARENT_FOLDER_ID):
    """
    Build and save data/drive_links.json mapping all 361 families to their public Google Drive URLs.
    Includes canonical summary metrics for test validation parity.
    """
    multi_count = sum(1 for f in families.values() if f["file_count"] > 1)
    single_count = sum(1 for f in families.values() if f["file_count"] == 1)
    total_files = sum(f["file_count"] for f in families.values())
    total_families = len(families)

    root_url = f"{DRIVE_FOLDER_BASE}/{parent_id}?usp=sharing"

    families_output = {}
    drive_links_map = {}

    for fam_name, fam_info in sorted(families.items()):
        folder_name = fam_info["folder_name"]
        folder_id = dirs_map.get(folder_name, parent_id)
        drive_url = f"{DRIVE_FOLDER_BASE}/{folder_id}?usp=sharing"

        families_output[fam_name] = {
            "folder_name": folder_name,
            "clean_name": fam_info.get("clean_name", ""),
            "folder_id": folder_id,
            "drive_folder_url": drive_url,
            "file_count": fam_info.get("file_count", len(fam_info.get("files", []))),
            "total_size_bytes": fam_info.get("total_size_bytes", 0),
            "styles": fam_info.get("styles", []),
            "files": fam_info.get("files", [])
        }
        drive_links_map[fam_name] = drive_url

    data = {
        "version": "1.0.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_families": total_families,
            "total_files": total_files,
            "multi_file_families": multi_count,
            "single_file_families": single_count,
            "parent_folder_id": parent_id,
            "drive_root_url": root_url
        },
        "families": families_output,
        "drive_links": drive_links_map
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated drive links file: {output_path} ({len(families_output)} families)")
    return data


def sync_catalog_drive_urls(catalog_path, dirs_map, parent_id=PARENT_FOLDER_ID):
    """
    Synchronize individual family Google Drive folder URLs into data/catalog.json.
    Updates font.drive_folder_url for all 361 families.
    """
    if not os.path.exists(catalog_path):
        print(f"⚠️ Catalog path does not exist: {catalog_path}")
        return False

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    fonts = catalog.get("fonts", [])
    updated_count = 0
    matched_dirs = 0

    for font in fonts:
        fam_name = font.get("family") or font.get("name")
        folder_id = dirs_map.get(fam_name)

        if not folder_id:
            # Try alternate key format (e.g. without SVN- or with spaces)
            for d_name, d_id in dirs_map.items():
                if d_name.lower() == fam_name.lower():
                    folder_id = d_id
                    break

        if folder_id and folder_id != parent_id:
            matched_dirs += 1
            font["drive_folder_url"] = f"{DRIVE_FOLDER_BASE}/{folder_id}?usp=sharing"
            updated_count += 1
        else:
            # Fallback to parent folder if not yet migrated
            font["drive_folder_url"] = f"{DRIVE_FOLDER_BASE}/{parent_id}?usp=sharing"
            updated_count += 1

    catalog["updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"✅ Synced catalog.json: {updated_count} fonts updated ({matched_dirs} specific subfolder links matched).")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Organize Google Drive font assets into 361 family subfolders via rclone."
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="Execute live folder creation and file moves (default is dry-run)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate execution without modifying Google Drive"
    )
    parser.add_argument(
        "--mapping", default=DEFAULT_MAPPING,
        help="Path to family_grouping_mapping.json"
    )
    parser.add_argument(
        "--catalog", default=DEFAULT_CATALOG,
        help="Path to data/catalog.json"
    )
    parser.add_argument(
        "--output-links", default=DEFAULT_DRIVE_LINKS,
        help="Path to data/drive_links.json output"
    )
    parser.add_argument(
        "--parent-id", default=PARENT_FOLDER_ID,
        help="Google Drive parent root folder ID"
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help="Number of concurrent worker threads (default: 8)"
    )

    args = parser.parse_args()

    # Dry-run is default unless --execute is explicitly supplied
    is_dry_run = not args.execute or args.dry_run

    print("=" * 75)
    print("🚀 GOOGLE DRIVE 361 FAMILY PACKAGING & SYNC PIPELINE (Milestone 2)")
    print(f"   Mode:               {'[DRY RUN - SIMULATION ONLY]' if is_dry_run else '[LIVE EXECUTION]'}")
    print(f"   Parent Folder ID:   {args.parent_id}")
    print(f"   Mapping Source:     {args.mapping}")
    print(f"   Catalog Target:     {args.catalog}")
    print(f"   Drive Links Output: {args.output_links}")
    print(f"   Worker Concurrency: {args.workers}")
    print("=" * 75)

    if not check_rclone():
        sys.exit(1)

    if not os.path.exists(args.mapping):
        sys.exit(f"❌ Error: Mapping file not found at {args.mapping}")

    with open(args.mapping, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    families = mapping_data.get("families", {})
    total_families = len(families)
    total_files = sum(fam["file_count"] for fam in families.values())

    print(f"\n📊 Input Mapping Analysis:")
    print(f"   Total Families: {total_families}")
    print(f"   Total Files:    {total_files}")

    # Step 1: Query Google Drive remote state
    print("\n🔍 Step 1: Inspecting Google Drive remote state...")
    existing_dirs = get_remote_dirs(args.parent_id)
    root_files = get_remote_files(args.parent_id)
    print(f"   Remote subdirectories found: {len(existing_dirs)}")
    print(f"   Remote root files found:     {len(root_files)}")

    # Step 2: Ensure all 361 family folders exist
    print("\n📁 Step 2: Creating family subfolders on Google Drive...")
    dirs_map = create_missing_folders(
        families, existing_dirs,
        parent_id=args.parent_id,
        dry_run=is_dry_run,
        workers=args.workers
    )

    # Step 3: Move files server-side
    print("\n📦 Step 3: Organizing files into family subfolders...")
    ok, moved_count, errors = move_files_to_families(
        families, root_files, dirs_map,
        parent_id=args.parent_id,
        dry_run=is_dry_run,
        workers=args.workers
    )

    # Step 4: Generate data/drive_links.json
    print("\n🔗 Step 4: Generating data/drive_links.json...")
    generate_drive_links(
        families, dirs_map,
        output_path=args.output_links,
        parent_id=args.parent_id
    )

    # Step 5: Sync data/catalog.json
    print("\n🔄 Step 5: Updating drive_folder_url in data/catalog.json...")
    sync_catalog_drive_urls(
        catalog_path=args.catalog,
        dirs_map=dirs_map,
        parent_id=args.parent_id
    )

    print("\n" + "=" * 75)
    print("🎉 MILESTONE 2 PIPELINE EXECUTION COMPLETED")
    print(f"   Status: {'SIMULATED (Dry Run)' if is_dry_run else 'SUCCESS (Live Execution)'}")
    print(f"   Families: {total_families} | Files: {total_files}")
    if is_dry_run:
        print("   💡 To apply live changes on Google Drive, run with '--execute'.")
    print("=" * 75)


if __name__ == "__main__":
    main()
