#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/live_simulation_click.py
Simulates real user clicks on live https://fonthub.fedu.vn
Inspects download button URLs, downloads files, and analyzes zip contents.
"""

import os
import sys
import json
import time
import zipfile
import tempfile
import urllib.request
from playwright.sync_api import sync_playwright

SAMPLE_TARGET_FONTS = [
    "FD Addington CF",
    "FD Adobe Caslon",
    "FD Adobe Jenson",
    "FD Agency FB"
]

def run_live_click_audit():
    results = []
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("🚀 [AUDIT] Launching headless Chrome via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome_path,
            headless=True
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        page = context.new_page()

        print("🌐 [AUDIT] Navigating to https://fonthub.fedu.vn ...")
        page.goto("https://fonthub.fedu.vn", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # Inspect all font cards currently rendered
        for font_name in SAMPLE_TARGET_FONTS:
            print(f"\n🔍 [AUDIT] Testing font: '{font_name}'...")
            # Locate font card by card-family-name text
            card_locator = page.locator(f".font-card:has(.card-family-name:text-is('{font_name}'))").first
            
            # If not visible in initial page, search for it
            if card_locator.count() == 0:
                print(f"  -> Font card '{font_name}' not in initial view, searching in search box...")
                search_input = page.locator("#fontSearch, input[placeholder*='Tìm']").first
                search_input.fill(font_name)
                page.wait_for_timeout(1000)
                card_locator = page.locator(f".font-card:has(.card-family-name:text-is('{font_name}'))").first

            if card_locator.count() == 0:
                print(f"  ❌ Card not found for '{font_name}'!")
                results.append({
                    "font_name": font_name,
                    "found": False,
                    "error": "Card not found on live site"
                })
                continue

            # Find download button within card
            download_btn = card_locator.locator("a.btn-download-family").first
            href = download_btn.get_attribute("href")
            download_attr = download_btn.get_attribute("download")
            target_attr = download_btn.get_attribute("target")

            print(f"  -> Found download button:")
            print(f"     href: {href}")
            print(f"     download attribute: {download_attr}")
            print(f"     target attribute: {target_attr}")

            # Test downloading or resolving URL
            resolved_url = href
            if href and not href.startswith("http"):
                resolved_url = f"https://fonthub.fedu.vn/{href.lstrip('/')}"

            item_result = {
                "font_name": font_name,
                "found": True,
                "button_href": href,
                "resolved_url": resolved_url,
                "download_attr": download_attr,
                "target_attr": target_attr,
                "is_drive": "drive.google.com" in (href or ""),
                "is_direct_zip": (href or "").endswith(".zip") or bool(download_attr),
                "download_status": None,
                "file_size": 0,
                "zip_files": [],
                "has_svn_in_files": False,
                "has_fd_in_files": False
            }

            # Simulate real browser click with expect_download
            try:
                print(f"     👉 Simulating user CLICK on download button...")
                with page.expect_download(timeout=10000) as download_info:
                    download_btn.click()
                download = download_info.value
                download_path = f"/tmp/audit_{font_name.replace(' ', '_')}.zip"
                download.save_as(download_path)
                
                item_result["download_status"] = "SUCCESS_PLAYWRIGHT_CLICK"
                item_result["file_size"] = os.path.getsize(download_path)
                with zipfile.ZipFile(download_path, 'r') as zf:
                    file_list = zf.namelist()
                    item_result["zip_files"] = file_list
                    for fn in file_list:
                        if "SVN" in fn or "svn" in fn:
                            item_result["has_svn_in_files"] = True
                        if "FD" in fn or "fd" in fn:
                            item_result["has_fd_in_files"] = True
                print(f"     ✅ Successfully downloaded via click: {item_result['file_size']} bytes")
                print(f"     Files inside zip ({len(file_list)}): {file_list[:4]}")
                print(f"     SVN detected: {item_result['has_svn_in_files']} | FD detected: {item_result['has_fd_in_files']}")
                if os.path.exists(download_path):
                    os.remove(download_path)
            except Exception as click_err:
                print(f"     ⚠️ Playwright click download event warning: {click_err}")
                # Fallback to direct curl download
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_f:
                    tmp_zip_path = tmp_f.name
                try:
                    req = urllib.request.Request(resolved_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, context=ctx) as resp, open(tmp_zip_path, "wb") as out_f:
                        out_f.write(resp.read())
                    item_result["download_status"] = "SUCCESS_HTTP"
                    item_result["file_size"] = os.path.getsize(tmp_zip_path)
                    with zipfile.ZipFile(tmp_zip_path, 'r') as zf:
                        file_list = zf.namelist()
                        item_result["zip_files"] = file_list
                        for fn in file_list:
                            if "SVN" in fn or "svn" in fn:
                                item_result["has_svn_in_files"] = True
                            if "FD" in fn or "fd" in fn:
                                item_result["has_fd_in_files"] = True
                    print(f"     ✅ Downloaded via HTTP fallback: {item_result['file_size']} bytes")
                    print(f"     Files inside zip: {file_list[:4]}")
                except Exception as dl_err:
                    print(f"     ❌ Download error: {dl_err}")
                    item_result["download_status"] = f"ERROR: {str(dl_err)}"
                finally:
                    if os.path.exists(tmp_zip_path):
                        os.remove(tmp_zip_path)

            results.append(item_result)

        browser.close()

    print("\n" + "="*70)
    print("📊 [AUDIT SUMMARY] Live Simulation Results:")
    for r in results:
        print(f"\n- Font: {r['font_name']}")
        print(f"  Live Button href: {r.get('button_href')}")
        print(f"  Resolved URL: {r.get('resolved_url')}")
        print(f"  Download Status: {r.get('download_status')}")
        print(f"  Files inside: {r.get('zip_files')}")
        print(f"  Contains SVN: {r.get('has_svn_in_files')}")

    out_json = "reports/live_click_simulation_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Results saved to {out_json}")
    return results

if __name__ == "__main__":
    run_live_click_audit()
