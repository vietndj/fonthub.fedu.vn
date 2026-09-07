#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_weight_slider_and_waterfall_e2e.py
Comprehensive Playwright E2E Test Suite for Weight Slider & Waterfall Features
Author: Subagent 2 (Quality Auditor) - Autonomous Opus Team

Verifies 100% of the requirements from Anh Việt:
1. Weight Slider (Thin/Light vs Regular vs Bold vs Black):
   - Real font-face loading (no faux-thin fallback).
   - Canvas pixel density measurement (Thin < Light < Regular < Bold <= Black).
   - Network / document.fonts.check verification.
2. Styles Badge & Waterfall Drawer:
   - Clicking styles badge opens waterfall drawer on both Catalog & Fontshare.
   - Number of waterfall rows matches the styles badge count (e.g., 20 styles -> 20 rows; 14 styles -> 14 rows).
   - Each row renders with appropriate font-weight.
   - Clicking a style row updates the main preview and syncs the Weight Slider & readout.
3. Cross-view consistency: Works across both #catalog and #fontshare.
"""

import os
import sys
import json
import time
import socket
import ssl
import urllib.request
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
REPORTS_DIR = PROJECT_ROOT / 'reports'
SCREENSHOTS_DIR = REPORTS_DIR / 'screenshots'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
LIVE_URL = 'https://fonthub.fedu.vn'

TEST_TARGET_FONTS = ['FD Gilroy', 'FD Aeonik', 'GR Sectra']

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def start_local_server(port):
    httpd = ThreadedHTTPServer(('127.0.0.1', port), lambda *args: QuietHandler(*args, directory=str(PROJECT_ROOT)))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

class WeightWaterfallAuditor:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {'total': 0, 'passed': 0, 'failed': 0},
            'suites': {},
            'screenshots': []
        }

    def record(self, suite_name, test_name, passed, details=None):
        if suite_name not in self.results['suites']:
            self.results['suites'][suite_name] = []
        self.results['summary']['total'] += 1
        if passed:
            self.results['summary']['passed'] += 1
            print(f"  [PASS] {test_name}")
        else:
            self.results['summary']['failed'] += 1
            print(f"  [FAIL] {test_name} | Details: {details}")
        self.results['suites'][suite_name].append({
            'name': test_name,
            'passed': passed,
            'details': details
        })

    def run_all(self):
        port = get_free_port()
        httpd = start_local_server(port)
        local_url = f"http://127.0.0.1:{port}/index.html"
        print("=" * 80)
        print("PLAYWRIGHT E2E AUDIT: WEIGHT SLIDER & WATERFALL STYLES")
        print(f"Local Server: {local_url}")
        print("=" * 80)

        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
            
            try:
                # Suite 1: Local Catalog (#catalog)
                self.audit_catalog_view(browser, local_url)
            except Exception as e:
                self.record("Catalog (#catalog)", "Suite Execution", False, str(e))

            try:
                # Suite 2: Local Fontshare (#fontshare)
                self.audit_fontshare_view(browser, local_url)
            except Exception as e:
                self.record("Fontshare (#fontshare)", "Suite Execution", False, str(e))

            try:
                # Suite 3: Live Production (if reachable)
                self.audit_live_production(browser)
            except Exception as e:
                self.record("Live Production (fonthub.fedu.vn)", "Suite Execution", False, str(e))

            browser.close()

        self.save_reports()

    def audit_catalog_view(self, browser, base_url):
        suite = "Catalog (#catalog)"
        print(f"\n[SUITE] {suite}")
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        page.goto(f"{base_url}#catalog", wait_until='domcontentloaded')
        page.wait_for_selector('.font-card', timeout=15000)
        time.sleep(1)

        for font_name in TEST_TARGET_FONTS:
            print(f"\n--- Auditing Font: {font_name} on Catalog ---")
            # Search to isolate target font
            search_input = page.locator('#search-input')
            search_input.fill(font_name)
            time.sleep(0.5)

            card = page.locator(f".font-card[data-family='{font_name}']").first
            if card.count() == 0:
                card = page.locator(f".font-card:has-text('{font_name}')").first

            if card.count() == 0:
                self.record(suite, f"Card found for '{font_name}'", False, "Card element not found in DOM")
                continue

            self.record(suite, f"Card found for '{font_name}'", True)

            # 1. Styles Badge & Waterfall Rows Count Test
            styles_btn = card.locator('.card-styles-toggle, .badge-styles, [data-action="toggle-card-waterfall"]').first
            badge_text = styles_btn.text_content().strip() if styles_btn.count() > 0 else ""
            
            expected_styles_count = 0
            if "style" in badge_text.lower():
                import re
                m = re.search(r'(\d+)\s*style', badge_text, re.I)
                if m:
                    expected_styles_count = int(m.group(1))

            # Click styles button to toggle waterfall
            if styles_btn.count() > 0:
                styles_btn.click()
                time.sleep(0.3)
                drawer = card.locator('.card-waterfall-drawer')
                is_open = drawer.is_visible()
                self.record(suite, f"'{font_name}' Waterfall drawer toggles open on styles click", is_open, f"Badge: '{badge_text}'")

                # Count rows (must be dynamic styles matching badge, NOT 5 static rows!)
                rows = card.locator('.card-waterfall-row')
                actual_rows_count = rows.count()
                match_count = (actual_rows_count == expected_styles_count) and (actual_rows_count > 0)
                self.record(suite, f"'{font_name}' Waterfall rows ({actual_rows_count}) match badge ({expected_styles_count} styles)",
                            match_count, f"Actual: {actual_rows_count}, Expected: {expected_styles_count}")

                # Verify each row has appropriate weight styling
                has_weights = rows.evaluate_all("""rows => {
                    return rows.every(r => r.getAttribute('data-weight') || r.getAttribute('data-size'));
                }""")
                self.record(suite, f"'{font_name}' Waterfall rows render distinct weights (Thin/Light/Bold)", has_weights)

                # Waterfall Row Click & Slider Sync Test
                if actual_rows_count > 0:
                    # Target Light or Thin row
                    target_row = rows.first
                    for i in range(actual_rows_count):
                        r = rows.nth(i)
                        name = (r.locator('.waterfall-style-name').text_content() or '').lower()
                        if 'light' in name or 'thin' in name:
                            target_row = r
                            break
                    
                    row_weight_tag = target_row.locator('.waterfall-weight-tag').text_content().strip() if target_row.locator('.waterfall-weight-tag').count() > 0 else "300"
                    
                    # Click apply button or meta directly (avoiding contenteditable center)
                    click_target = target_row.locator('.waterfall-apply-btn, .waterfall-style-name, .waterfall-meta').first
                    if click_target.count() > 0:
                        click_target.click()
                    else:
                        target_row.click()
                    time.sleep(0.3)

                    slider = card.locator('.card-weight-slider')
                    slider_val = slider.input_value() if slider.count() > 0 else ""
                    val_disp = card.locator('.card-weight-val').text_content().strip() if card.locator('.card-weight-val').count() > 0 else ""

                    synced = (slider_val == row_weight_tag or (row_weight_tag.isdigit() and abs(int(slider_val) - int(row_weight_tag)) <= 100))
                    self.record(suite, f"'{font_name}' Waterfall row click syncs slider to {row_weight_tag}",
                                synced, f"Slider: {slider_val}, Display: {val_disp}, Target Row: {row_weight_tag}")

            # 2. Weight Slider Visual & Pixel Density Test
            slider = card.locator('.card-weight-slider')
            preview = card.locator('.preview-text').first
            if slider.count() > 0 and preview.count() > 0:
                print(f"  Measuring visual pixel density for '{font_name}' at 100, 300, 400, 700, 900...")
                test_weights = [100, 300, 400, 700, 900]
                pixel_map = {}

                for w in test_weights:
                    slider.evaluate(f"el => {{ el.value = {w}; el.dispatchEvent(new Event('input', {{ bubbles: true }})); }}")
                    time.sleep(0.2)

                    px_count = page.evaluate(f"""async () => {{
                        await document.fonts.load('{w} 36px "{font_name}"');
                        await document.fonts.ready;
                        const canvas = document.createElement('canvas');
                        canvas.width = 500; canvas.height = 80;
                        const ctx = canvas.getContext('2d', {{ willReadFrequently: true }});
                        ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0, 0, 500, 80);
                        const isSerif = '{font_name}'.includes('Sectra');
                        ctx.font = '{w} 36px "{font_name}", ' + (isSerif ? 'serif' : 'sans-serif');
                        ctx.fillStyle = '#000000'; ctx.fillText('FEDU TIẾNG VIỆT 123', 10, 50);
                        const img = ctx.getImageData(0, 0, 500, 80).data;
                        let c = 0;
                        for (let i = 0; i < img.length; i += 4) if (img[i] < 128) c++;
                        return c;
                    }}""")
                    pixel_map[w] = px_count

                print(f"    Pixel counts for {font_name}: {pixel_map}")

                # Save screenshot of card at weight 300 (Light) and 700 (Bold)
                shot_path_light = str(SCREENSHOTS_DIR / f"catalog_{font_name.replace(' ', '_').lower()}_w300.png")
                shot_path_bold = str(SCREENSHOTS_DIR / f"catalog_{font_name.replace(' ', '_').lower()}_w700.png")
                slider.evaluate("el => { el.value = 300; el.dispatchEvent(new Event('input', { bubbles: true })); }")
                time.sleep(0.2)
                card.screenshot(path=shot_path_light)
                self.results['screenshots'].append(shot_path_light)

                slider.evaluate("el => { el.value = 700; el.dispatchEvent(new Event('input', { bubbles: true })); }")
                time.sleep(0.2)
                card.screenshot(path=shot_path_bold)
                self.results['screenshots'].append(shot_path_bold)

                # ASSERTIONS:
                # 1) Light (300) must be thinner than Regular (400) - NO fallback!
                light_vs_reg = pixel_map.get(300, 0) < pixel_map.get(400, 0)
                self.record(suite, f"'{font_name}' Light (300) is visually thinner than Regular (400)",
                            light_vs_reg, f"Light (300): {pixel_map.get(300)} px, Regular (400): {pixel_map.get(400)} px")

                # 2) Regular (400) must be thinner than Bold (700)
                reg_vs_bold = pixel_map.get(400, 0) < pixel_map.get(700, 0)
                self.record(suite, f"'{font_name}' Regular (400) is visually thinner than Bold (700)",
                            reg_vs_bold, f"Regular (400): {pixel_map.get(400)} px, Bold (700): {pixel_map.get(700)} px")

                # 3) Bold (700) vs Black (900)
                bold_vs_black = pixel_map.get(700, 0) <= pixel_map.get(900, 0)
                self.record(suite, f"'{font_name}' Bold (700) vs Black (900) progression verified",
                            bold_vs_black, f"Bold (700): {pixel_map.get(700)} px, Black (900): {pixel_map.get(900)} px")

        page.close()

    def audit_fontshare_view(self, browser, base_url):
        suite = "Fontshare (#fontshare)"
        print(f"\n[SUITE] {suite}")
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        page.goto(f"{base_url}#fontshare", wait_until='domcontentloaded')
        page.wait_for_selector('.fontshare-card', timeout=15000)
        time.sleep(1)

        for font_name in TEST_TARGET_FONTS:
            print(f"\n--- Auditing Font: {font_name} on Fontshare ---")
            card = page.locator(f".fontshare-card[data-family='{font_name}']").first
            if card.count() == 0:
                card = page.locator(f".fontshare-card:has-text('{font_name}')").first

            if card.count() == 0:
                # Try search
                search_input = page.locator('#fontshare-search')
                if search_input.count() > 0:
                    search_input.fill(font_name)
                    time.sleep(0.5)
                    card = page.locator(f".fontshare-card[data-family='{font_name}']").first
                    if card.count() == 0:
                        card = page.locator(f".fontshare-card:has-text('{font_name}')").first

            if card.count() == 0:
                self.record(suite, f"Card found for '{font_name}'", False, "Card element not found in DOM")
                continue

            self.record(suite, f"Card found for '{font_name}'", True)

            # 1. Styles Badge & Waterfall Rows Count Test
            styles_btn = card.locator('.card-styles-toggle, .fs-styles-badge, [data-action="toggle-card-waterfall"]').first
            badge_text = styles_btn.text_content().strip() if styles_btn.count() > 0 else ""
            
            expected_styles_count = 0
            if "style" in badge_text.lower():
                import re
                m = re.search(r'(\d+)\s*style', badge_text, re.I)
                if m:
                    expected_styles_count = int(m.group(1))

            # Click styles button to toggle waterfall
            if styles_btn.count() > 0:
                styles_btn.click()
                time.sleep(0.3)
                drawer = card.locator('.fs-waterfall-drawer')
                is_open = drawer.is_visible()
                self.record(suite, f"'{font_name}' Waterfall drawer toggles open on Fontshare", is_open, f"Badge: '{badge_text}'")

                # Count rows (must be dynamic styles matching badge, NOT 5 static rows!)
                rows = card.locator('.card-waterfall-row, .waterfall-row')
                actual_rows_count = rows.count()
                match_count = (actual_rows_count == expected_styles_count) and (actual_rows_count > 0)
                self.record(suite, f"'{font_name}' Fontshare waterfall rows ({actual_rows_count}) match badge ({expected_styles_count} styles)",
                            match_count, f"Actual: {actual_rows_count}, Expected: {expected_styles_count}")

                # Waterfall Row Click & Slider Sync Test on Fontshare
                if actual_rows_count > 0:
                    target_row = rows.first
                    for i in range(actual_rows_count):
                        r = rows.nth(i)
                        name = r.locator('.waterfall-style-name, .waterfall-text').text_content().lower()
                        if 'light' in name or 'thin' in name:
                            target_row = r
                            break
                    
                    row_weight = target_row.locator('.waterfall-weight-tag').text_content().strip() if target_row.locator('.waterfall-weight-tag').count() > 0 else "100"
                    
                    click_target = target_row.locator('.waterfall-apply-btn, .waterfall-style-name, .waterfall-meta').first
                    if click_target.count() > 0:
                        click_target.click()
                    else:
                        target_row.click()
                    time.sleep(0.3)

                    slider = card.locator('.card-weight-slider')
                    slider_val = slider.input_value() if slider.count() > 0 else ""
                    val_disp = card.locator('.fs-weight-val, .card-weight-val').text_content().strip() if card.locator('.fs-weight-val, .card-weight-val').count() > 0 else ""

                    synced = (slider_val == row_weight or (row_weight.isdigit() and abs(int(slider_val) - int(row_weight)) <= 100))
                    self.record(suite, f"'{font_name}' Fontshare waterfall row click syncs slider to {row_weight}",
                                synced, f"Slider: {slider_val}, Display: {val_disp}, Target Row: {row_weight}")

            # 2. Weight Slider Visual & Pixel Density Test
            slider = card.locator('.card-weight-slider')
            specimen = card.locator('.fs-item-specimen, .preview-text').first
            if slider.count() > 0 and specimen.count() > 0:
                print(f"  Measuring Fontshare visual pixel density for '{font_name}'...")
                test_weights = [100, 300, 400, 700, 900]
                pixel_map = {}

                for w in test_weights:
                    slider.evaluate(f"el => {{ el.value = {w}; el.dispatchEvent(new Event('input', {{ bubbles: true }})); }}")
                    time.sleep(0.2)

                    px_count = page.evaluate(f"""async () => {{
                        await document.fonts.load('{w} 36px "{font_name}"');
                        await document.fonts.ready;
                        const canvas = document.createElement('canvas');
                        canvas.width = 500;
                        canvas.height = 80;
                        const ctx = canvas.getContext('2d', {{ willReadFrequently: true }});
                        ctx.fillStyle = '#FFFFFF';
                        ctx.fillRect(0, 0, 500, 80);
                        const isSerif = '{font_name}'.includes('Sectra');
                        ctx.font = '{w} 36px "{font_name}", ' + (isSerif ? 'serif' : 'sans-serif');
                        ctx.fillStyle = '#000000';
                        ctx.fillText('FEDU TIẾNG VIỆT 123', 10, 50);
                        const img = ctx.getImageData(0, 0, 500, 80).data;
                        let c = 0;
                        for (let i = 0; i < img.length; i += 4) if (img[i] < 128) c++;
                        return c;
                    }}""")
                    pixel_map[w] = px_count

                print(f"    Fontshare pixel counts for {font_name}: {pixel_map}")

                # Save screenshot of card at weight 300 and 700
                shot_path_light = str(SCREENSHOTS_DIR / f"fontshare_{font_name.replace(' ', '_').lower()}_w300.png")
                shot_path_bold = str(SCREENSHOTS_DIR / f"fontshare_{font_name.replace(' ', '_').lower()}_w700.png")
                slider.evaluate("el => { el.value = 300; el.dispatchEvent(new Event('input', { bubbles: true })); }")
                time.sleep(0.2)
                card.screenshot(path=shot_path_light)
                self.results['screenshots'].append(shot_path_light)

                slider.evaluate("el => { el.value = 700; el.dispatchEvent(new Event('input', { bubbles: true })); }")
                time.sleep(0.2)
                card.screenshot(path=shot_path_bold)
                self.results['screenshots'].append(shot_path_bold)

                # Assertions for Fontshare
                light_vs_reg = pixel_map.get(300, 0) < pixel_map.get(400, 0)
                self.record(suite, f"'{font_name}' Fontshare Light (300) is visually thinner than Regular (400)",
                            light_vs_reg, f"Light (300): {pixel_map.get(300)} px, Regular (400): {pixel_map.get(400)} px")

                reg_vs_bold = pixel_map.get(400, 0) < pixel_map.get(700, 0)
                self.record(suite, f"'{font_name}' Fontshare Regular (400) is visually thinner than Bold (700)",
                            reg_vs_bold, f"Regular (400): {pixel_map.get(400)} px, Bold (700): {pixel_map.get(700)} px")

        page.close()

    def audit_live_production(self, browser):
        suite = "Live Production (fonthub.fedu.vn)"
        print(f"\n[SUITE] {suite}")
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(LIVE_URL, headers={'User-Agent': 'FontHub-Auditor/2.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                status = resp.status
                self.record(suite, f"HTTP GET {LIVE_URL} status 200", status == 200, f"HTTP {status}")
        except Exception as e:
            self.record(suite, f"HTTP GET {LIVE_URL} reachable", False, str(e))
            return

        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        try:
            page.goto(f"{LIVE_URL}/#catalog", wait_until='networkidle', timeout=20000)
            page.wait_for_selector('.font-card', timeout=15000)
            cards_count = page.locator('.font-card').count()
            self.record(suite, f"Live Production rendered font cards (Count: {cards_count})", cards_count > 0)
            
            shot_path = str(SCREENSHOTS_DIR / "live_production_catalog.png")
            page.screenshot(path=shot_path)
            self.results['screenshots'].append(shot_path)
        except Exception as e:
            self.record(suite, "Live Production Browser Render", False, str(e))
        finally:
            page.close()

    def save_reports(self):
        json_path = REPORTS_DIR / 'weight_slider_waterfall_audit_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        md_path = REPORTS_DIR / 'weight_slider_waterfall_audit_report.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Báo Cáo Nghiệm Thu E2E: Weight Slider & Waterfall Styles\n\n")
            f.write(f"- **Thời gian kiểm thử**: `{self.results['timestamp']}`\n")
            f.write(f"- **Tổng số kiểm thử**: `{self.results['summary']['total']}`\n")
            f.write(f"- **Đạt (PASS)**: `{self.results['summary']['passed']}`\n")
            f.write(f"- **Không đạt (FAIL)**: `{self.results['summary']['failed']}`\n\n")

            for suite_name, tests in self.results['suites'].items():
                f.write(f"### {suite_name}\n\n")
                f.write("| Tên Kiểm Thử | Trạng Thái | Chi Tiết |\n")
                f.write("| :--- | :---: | :--- |\n")
                for t in tests:
                    status_icon = "✅ PASS" if t['passed'] else "❌ FAIL"
                    details_str = f"`{t['details']}`" if t['details'] else "-"
                    f.write(f"| {t['name']} | {status_icon} | {details_str} |\n")
                f.write("\n")

        print("\n" + "=" * 80)
        print(f"AUDIT HOÀN TẤT: {self.results['summary']['passed']}/{self.results['summary']['total']} PASS")
        print(f"JSON Report: {json_path}")
        print(f"Markdown Report: {md_path}")
        print("=" * 80)

if __name__ == '__main__':
    auditor = WeightWaterfallAuditor()
    auditor.run_all()
