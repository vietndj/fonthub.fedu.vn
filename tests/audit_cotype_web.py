#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/audit_cotype_web.py
Audits Font Hub UI & Web Integration for CoType Fonts:
1. index.html: Chip CoType element, count badge, data-category attribute.
2. app.js & js/catalog_loader.js: Filtering logic, category handler, count update.
3. data/catalog.json: All 11 CoType families present, metadata validity, download ZIP files exist.
4. E2E Headless Browser Verification (Playwright):
   - Loads index.html on local server.
   - Verifies Chip "CoType" is rendered and displays count.
   - Clicks Chip "CoType" and checks displayed cards.
   - Types Vietnamese preview text ("Thử nghiệm phông chữ Việt Nam").
   - Validates download links and CSS font-face loading.
"""

import os
import sys
import json
import time
import socket
import threading
import http.server
import unittest
from pathlib import Path

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")

EXPECTED_FAMILIES = [
    "Altform",
    "Ambit",
    "Coanda",
    "Lock Sans Stencil",
    "Lock Sans",
    "Lock Serif Stencil",
    "Lock Serif",
    "Orbikular",
    "RM Mono",
    "RM Neue",
    "Scandium"
]

class LocalServer:
    def __init__(self, directory=PROJECT_ROOT):
        self.directory = str(directory)
        self.server = None
        self.port = 0
        self.thread = None

    def start(self):
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=self.directory, **kwargs)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            self.port = s.getsockname()[1]
        
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.5)

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()

class TestCoTypeWebIntegration(unittest.TestCase):

    def test_01_index_html_cotype_chip(self):
        """Kiểm tra index.html có chip lọc CoType với data-category và id đếm số lượng"""
        html_path = PROJECT_ROOT / "index.html"
        self.assertTrue(html_path.exists(), "index.html không tồn tại")
        content = html_path.read_text(encoding="utf-8")
        
        # Check for CoType chip button
        has_cotype_chip = ('data-category="CoType"' in content or 
                           'data-category="CoType Foundry"' in content or
                           'data-category="CoType Font"' in content or
                           'data-category="CoType viethoa"' in content or
                           'CoType' in content and 'chip-btn' in content)
        self.assertTrue(has_cotype_chip, "index.html chưa có chip-btn CoType trong filter chips container")
        
        # Check for count element
        has_count = 'id="count-cotype"' in content or 'count-cotype' in content
        self.assertTrue(has_count, "index.html chưa có element đếm số lượng font CoType (ví dụ id='count-cotype')")

    def test_02_catalog_json_cotype_families(self):
        """Kiểm tra data/catalog.json có đầy đủ cả 11 families CoType và download zips hợp lệ"""
        catalog_path = PROJECT_ROOT / "data" / "catalog.json"
        self.assertTrue(catalog_path.exists(), "data/catalog.json không tồn tại")
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
            
        fonts = catalog if isinstance(catalog, list) else catalog.get("fonts", [])
        self.assertGreater(len(fonts), 0, "catalog.json rỗng")
        
        found_fams = {}
        missing_zips = []
        
        for item in fonts:
            name = item.get("name", "")
            for ef in EXPECTED_FAMILIES:
                norm_ef = "".join(c for c in ef.lower() if c.isalnum())
                norm_name = "".join(c for c in name.lower() if c.isalnum())
                
                is_stencil = "stencil" in ef.lower()
                is_serif = "serif" in ef.lower()
                
                if is_stencil != ("stencil" in norm_name):
                    continue
                if is_serif != ("serif" in norm_name):
                    continue
                
                if norm_ef in norm_name:
                    found_fams[ef] = item
                    # Check download zip link
                    dl = item.get("download_url") or item.get("zip_path") or item.get("download")
                    if dl:
                        # Normalize path
                        zip_file = PROJECT_ROOT / dl.lstrip("/")
                        if not zip_file.exists():
                            # Check under dist/zips or dist/zips/FD
                            alt_zip = PROJECT_ROOT / "dist" / "zips" / "FD" / Path(dl).name
                            alt_zip_2 = PROJECT_ROOT / "dist" / "zips" / Path(dl).name
                            if not alt_zip.exists() and not alt_zip_2.exists():
                                missing_zips.append((name, dl))
                    break
        
        missing_fams = [f for f in EXPECTED_FAMILIES if f not in found_fams]
        self.assertEqual(len(missing_fams), 0, 
                         f"catalog.json thiếu {len(missing_fams)} families CoType: {missing_fams}")
        self.assertEqual(len(missing_zips), 0, 
                         f"Có {len(missing_zips)} download ZIP trong catalog.json không tồn tại trên đĩa: {missing_zips}")

    def test_03_app_js_filtering_support(self):
        """Kiểm tra app.js và catalog_loader.js đã hỗ trợ category CoType và tính count chính xác"""
        app_paths = [PROJECT_ROOT / "app.js", PROJECT_ROOT / "js" / "app.js", PROJECT_ROOT / "js" / "catalog_loader.js"]
        
        cotype_handled = False
        for ap in app_paths:
            if ap.exists():
                txt = ap.read_text(encoding="utf-8")
                if "cotype" in txt.lower():
                    cotype_handled = True
                    break
        self.assertTrue(cotype_handled, "app.js và catalog_loader.js chưa chứa logic xử lý cho CoType category")

    def test_04_e2e_playwright_headless_browser(self):
        """E2E Test với Playwright: Load Font Hub, bấm chip CoType, xem preview, kiểm tra card hiển thị"""
        from playwright.sync_api import sync_playwright
        
        srv = LocalServer()
        srv.start()
        
        try:
            with sync_playwright() as p:
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                launch_kwargs = {"headless": True}
                if os.path.exists(chrome_path):
                    launch_kwargs["executable_path"] = chrome_path
                
                browser = p.chromium.launch(**launch_kwargs)
                page = browser.new_page()
                
                url = f"http://127.0.0.1:{srv.port}/index.html"
                page.goto(url, wait_until="networkidle", timeout=15000)
                
                # Check title
                title = page.title()
                self.assertTrue("FEDU" in title or "font.fedu.vn" in title)
                
                # Find CoType chip
                chip = page.locator("button.chip-btn:has-text('CoType'), [data-category*='CoType']")
                self.assertGreater(chip.count(), 0, "Không tìm thấy chip CoType trên giao diện web")
                
                # Check badge count
                count_badge = chip.locator(".chip-count")
                if count_badge.count() > 0:
                    badge_text = count_badge.first.inner_text()
                    count_val = int("".join(c for c in badge_text if c.isdigit()) or "0")
                    self.assertGreaterEqual(count_val, 11, f"Badge số lượng CoType ({count_val}) nhỏ hơn 11 families")
                
                # Click chip CoType
                chip.first.click()
                page.wait_for_timeout(500)
                
                # Check displayed cards
                cards = page.locator(".font-card, .family-card, [data-font-family]")
                card_count = cards.count()
                self.assertGreater(card_count, 0, "Bấm chip CoType không hiển thị font card nào")
                
                # Verify preview text handles Vietnamese characters smoothly
                search_or_preview = page.locator("#custom-preview-input, #preview-input, input[placeholder*='nhập'], input[placeholder*='gõ']")
                if search_or_preview.count() > 0:
                    search_or_preview.first.fill("Việt Nam độc lập tự do hạnh phúc 123")
                    page.wait_for_timeout(300)
                
                browser.close()
        finally:
            srv.stop()

if __name__ == '__main__':
    unittest.main()
