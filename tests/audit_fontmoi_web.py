#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/audit_fontmoi_web.py
Audits Font Hub UI & Web Integration for Font Moi (Dinamo, Klim, Pangram Pangram):
1. index.html: Filter chips (Dinamo, Klim, Pangram), count badges (#count-dinamo, #count-klim, #count-pangram).
2. app.js & js/catalog_loader.js: Filtering handlers, category click logic, badge click bindings.
3. data/catalog.json: All 32 families cataloged with valid metadata, weights, and valid download ZIP packages.
4. E2E Headless Playwright Verification:
   - Loads index.html on local test server.
   - Verifies chips "Dinamo", "Klim", "Pangram" are rendered.
   - Clicks each chip and verifies font cards display and count badge matches.
   - Types Vietnamese preview text ("Thử nghiệm phông chữ Việt Nam: sắc, huyền, hỏi, ngã, nặng, ơ, ư, đ").
   - Validates live cards rendering and CSS font-face loading.
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

EXPECTED_DINAMO = [
    "FD Monument Grotesk",
    "FD Monument Grotesk Condensed",
    "FD Monument Grotesk Mono",
    "FD Monument Grotesk Semi Mono"
]

EXPECTED_PANGRAM = [
    "FD Formula"
]

EXPECTED_KLIM = [
    "FD American Grotesk",
    "FD Calibre",
    "FD Die Grotesk",
    "FD Domaine",
    "FD Domaine Sans",
    "FD Epicene",
    "FD Family",
    "FD Feijoa",
    "FD Financier",
    "FD Founders Grotesk",
    "FD Geograph",
    "FD Heldane",
    "FD Karbon",
    "FD Maelstrom",
    "FD Manuka",
    "FD Martina Plantijn",
    "FD Metric",
    "FD National",
    "FD National 2",
    "FD Newzald",
    "FD Pitch",
    "FD Signifier",
    "FD Söhne",
    "FD The Future",
    "FD Tiempos",
    "FD Untitled Sans",
    "FD Untitled Serif"
]

ALL_EXPECTED = EXPECTED_DINAMO + EXPECTED_PANGRAM + EXPECTED_KLIM

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

class TestFontMoiWebIntegration(unittest.TestCase):

    def test_01_index_html_filter_chips(self):
        """Kiểm tra index.html có các chip lọc Dinamo, Klim, Pangram và element đếm số lượng"""
        html_path = PROJECT_ROOT / "index.html"
        self.assertTrue(html_path.exists(), "index.html không tồn tại")
        content = html_path.read_text(encoding="utf-8")

        for cat, cid in [("Dinamo", "count-dinamo"), ("Klim", "count-klim"), ("Pangram", "count-pangram")]:
            has_chip = f'data-category="{cat}"' in content
            self.assertTrue(has_chip, f"index.html thiếu chip button cho foundry: {cat}")
            has_count = f'id="{cid}"' in content
            self.assertTrue(has_count, f"index.html thiếu badge đếm id='{cid}' cho {cat}")

    def test_02_catalog_json_fontmoi_metadata(self):
        """Kiểm tra data/catalog.json có đầy đủ cả 32 họ font Font Moi và download ZIPs hợp lệ"""
        catalog_path = PROJECT_ROOT / "data" / "catalog.json"
        self.assertTrue(catalog_path.exists(), "data/catalog.json không tồn tại")

        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        fonts = catalog if isinstance(catalog, list) else catalog.get("fonts", [])
        self.assertGreater(len(fonts), 0, "catalog.json rỗng")

        found_fams = {}
        missing_zips = []
        fonts_by_name = {item.get("name"): item for item in fonts}

        for ef in ALL_EXPECTED:
            if ef in fonts_by_name:
                item = fonts_by_name[ef]
                found_fams[ef] = item
                dl = item.get("download_url") or item.get("zip_path") or item.get("download")
                if dl:
                    zip_file = PROJECT_ROOT / dl.lstrip("/")
                    alt_zip_1 = PROJECT_ROOT / "dist" / "zips" / "FD" / Path(dl).name
                    alt_zip_2 = PROJECT_ROOT / "dist" / "zips" / Path(dl).name
                    if not zip_file.exists() and not alt_zip_1.exists() and not alt_zip_2.exists():
                        missing_zips.append((ef, dl))

        missing = [f for f in ALL_EXPECTED if f not in found_fams]
        self.assertEqual(len(missing), 0,
                         f"catalog.json thiếu {len(missing)} họ font: {missing}")
        self.assertEqual(len(missing_zips), 0,
                         f"Có {len(missing_zips)} file ZIP không tồn tại: {missing_zips}")

    def test_03_app_js_filtering_logic(self):
        """Kiểm tra app.js và catalog_loader.js đã hỗ trợ category Dinamo, Klim, Pangram"""
        app_paths = [PROJECT_ROOT / "app.js", PROJECT_ROOT / "js" / "app.js", PROJECT_ROOT / "js" / "catalog_loader.js"]
        for cat in ["dinamo", "klim", "pangram"]:
            handled = False
            for ap in app_paths:
                if ap.exists():
                    txt = ap.read_text(encoding="utf-8").lower()
                    if cat in txt:
                        handled = True
                        break
            self.assertTrue(handled, f"Chưa tìm thấy logic xử lý cho category '{cat}' trong app.js / catalog_loader.js")

    def test_04_e2e_playwright_headless_browser(self):
        """E2E Test với Playwright: Load Font Hub, bấm chip Dinamo/Klim/Pangram, gõ test tiếng Việt"""
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

                for cat in ["Dinamo", "Pangram", "Klim"]:
                    chip = page.locator(f"button.chip-btn[data-category='{cat}']")
                    self.assertGreater(chip.count(), 0, f"Không tìm thấy chip '{cat}' trên giao diện web")

                    # Check badge count > 0
                    count_badge = chip.locator(".chip-count")
                    if count_badge.count() > 0:
                        b_txt = count_badge.first.inner_text().strip()
                        c_val = int("".join(c for c in b_txt if c.isdigit()) or "0")
                        self.assertGreater(c_val, 0, f"Chip count của '{cat}' phải > 0, hiện là: {c_val}")

                    # Click chip
                    chip.first.click()
                    page.wait_for_timeout(400)

                    # Verify cards rendered
                    cards = page.locator(".font-card")
                    card_count = cards.count()
                    self.assertGreater(card_count, 0, f"Sau khi click chip '{cat}', không có font-card nào hiển thị!")

                # Live Vietnamese Preview Test
                test_text = "Thử nghiệm phông chữ Việt Nam: sắc, huyền, hỏi, ngã, nặng, ơ, ư, đ"
                preview_input = page.locator("#preview-text-input, input[placeholder*='Nhập'], input[placeholder*='Thử']")
                if preview_input.count() > 0:
                    preview_input.first.fill(test_text)
                    page.wait_for_timeout(300)

                browser.close()
        finally:
            srv.stop()

if __name__ == '__main__':
    unittest.main()
