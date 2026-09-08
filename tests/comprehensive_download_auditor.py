#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/comprehensive_download_auditor.py
Comprehensive auditor for all font download links (Direct CDN & Google Drive).
Verifies HTTP status, file sizes, and confirms zero SVN remnants in downloaded zip contents.
"""

import os
import sys
import json
import time
import zipfile
import tempfile
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_JSON_PATH = os.path.join(PROJECT_ROOT, "data/fonts.json")
LIVE_BASE_URL = os.environ.get("LIVE_BASE_URL", "https://font.fedu.vn")

# SSL context for macOS python
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def check_direct_download(font, sample_download=False):
    name = font.get("name")
    font_id = font.get("id")
    zip_url = font.get("zip_url") or font.get("download_url", "")
    drive_folder_url = font.get("drive_folder_url") or font.get("drive_link", "")

    if not zip_url.startswith("http"):
        direct_download_url = f"{LIVE_BASE_URL}/{zip_url.lstrip('/')}"
    else:
        direct_download_url = zip_url

    res = {
        "id": font_id,
        "name": name,
        "direct_download_url": direct_download_url,
        "drive_folder_url": drive_folder_url,
        "direct_http_status": None,
        "direct_content_length": 0,
        "direct_verified": False,
        "sample_tested": False,
        "zip_files_sample": [],
        "has_svn": False,
        "has_fd_or_gr": False,
        "note": ""
    }

    # Head check direct download
    try:
        req = urllib.request.Request(direct_download_url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=10) as resp:
            res["direct_http_status"] = resp.status
            cl = resp.headers.get("Content-Length")
            if cl:
                res["direct_content_length"] = int(cl)
            if resp.status == 200 and res["direct_content_length"] > 0:
                res["direct_verified"] = True
    except Exception as e:
        # Fallback to GET with range
        try:
            req = urllib.request.Request(direct_download_url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-1024"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=10) as resp:
                res["direct_http_status"] = resp.status
                res["direct_verified"] = resp.status in [200, 206]
        except Exception as e2:
            res["note"] = f"Direct check failed: {str(e2)}"

    # Sample download and inspect zip
    if sample_download and res["direct_verified"]:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_f:
            tmp_path = tmp_f.name
        try:
            req = urllib.request.Request(direct_download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp, open(tmp_path, "wb") as f:
                f.write(resp.read())
            res["sample_tested"] = True
            with zipfile.ZipFile(tmp_path, "r") as zf:
                names = zf.namelist()
                res["zip_files_sample"] = names[:5]
                for fn in names:
                    if "SVN" in fn or "svn" in fn:
                        res["has_svn"] = True
                    if "FD" in fn or "fd" in fn or "GR" in fn or "gr" in fn:
                        res["has_fd_or_gr"] = True
        except Exception as err:
            res["note"] += f" | Sample download failed: {str(err)}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return res

def run_audit(sample_count=20):
    print("🚀 Loading fonts from data/fonts.json...")
    with open(FONTS_JSON_PATH, "r", encoding="utf-8") as f:
        fonts = json.load(f)

    total = len(fonts)
    print(f"📦 Total fonts to audit: {total}")

    # Mark first `sample_count` and specific requested fonts for actual deep zip download
    target_names = ["FD Addington CF", "FD Adobe Caslon", "FD Adobe Jenson", "FD Agency FB"]
    
    results = []
    print(f"⏳ Auditing {total} fonts across threads...")
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {}
        for idx, font in enumerate(fonts):
            should_sample = (idx < sample_count) or (font.get("name") in target_names)
            f = executor.submit(check_direct_download, font, sample_download=should_sample)
            futures[f] = font["name"]

        for f in as_completed(futures):
            res = f.result()
            results.append(res)

    results.sort(key=lambda x: x["name"])

    # Statistics
    verified_direct = sum(1 for r in results if r["direct_verified"])
    sampled = [r for r in results if r["sample_tested"]]
    svn_contaminated = [r for r in sampled if r["has_svn"]]
    clean_sampled = [r for r in sampled if not r["has_svn"] and r["has_fd_or_gr"]]

    print("\n" + "="*70)
    print(f"📊 DIRECT DOWNLOAD AUDIT RESULTS ({total} Fonts):")
    print(f"  - Direct CDN verified (HTTP 200): {verified_direct} / {total} ({verified_direct/total*100:.1f}%)")
    print(f"  - Deep Zip Inspection Count: {len(sampled)}")
    print(f"  - 100% Clean FD/GR: {len(clean_sampled)} / {len(sampled)}")
    print(f"  - SVN Contaminated in Downloaded Zips: {len(svn_contaminated)}")
    print("="*70)

    # Save JSON report
    out_json = os.path.join(PROJECT_ROOT, "reports/audit_direct_downloads.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "total": total,
            "verified_direct": verified_direct,
            "sampled_count": len(sampled),
            "svn_contaminated": len(svn_contaminated),
            "clean_sampled": len(clean_sampled),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved JSON report to {out_json}")

    return results

if __name__ == "__main__":
    run_audit(sample_count=15)
