#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/audit_font_pills_visual_e2e.py
Quality Auditor Automated E2E Test Suite for Font Style Pills, Webfont Loading & Visual Verification.

Covers:
1. Local HTTP server connection (zero external server dependency).
2. Playwright Headless Chrome automation with high-DPI viewport.
3. Font Card discovery & Style Pill interaction (GR Sectra, GR Walsheim, GR America, FD Gilroy, etc.).
4. Style activation, computed styles (font-family, font-weight, font-style).
5. Dynamic font loading verification (Network 200 vs 404, FontFaceSet, canvas metrics diff against system fallbacks).
6. High-resolution visual screenshots for each style pill.
7. HTML & JSON reporting for autonomous audit sign-off.
"""

import os
import sys
import json
import time
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
REPORTS_DIR = PROJECT_ROOT / 'reports'
SCREENSHOTS_DIR = REPORTS_DIR / 'screenshots' / 'style_pills'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

TARGET_FONTS_TO_AUDIT = [
    {
        'id': 'gr-sectra',
        'query': 'Sectra',
        'display_name': 'GR Sectra',
        'category': 'Serif',
        'expected_family_token': 'Sectra',
        'pill_tests': [
            {'style': 'Light', 'expected_weight': '300', 'style_type': 'normal'},
            {'style': 'Book', 'expected_weight': '400', 'style_type': 'normal'},
            {'style': 'Regular', 'expected_weight': '400', 'style_type': 'normal'},
            {'style': 'Medium', 'expected_weight': '500', 'style_type': 'normal'},
            {'style': 'Bold', 'expected_weight': '700', 'style_type': 'normal'},
            {'style': 'Super', 'expected_weight': '800', 'style_type': 'normal'},
            {'style': 'Black', 'expected_weight': '900', 'style_type': 'normal'}
        ]
    },
    {
        'id': 'gr-walsheim',
        'query': 'Walsheim',
        'display_name': 'GR Walsheim',
        'category': 'Sans Serif',
        'expected_family_token': 'Walsheim',
        'pill_tests': [
            {'style': 'UltraLight', 'expected_weight': '200', 'style_type': 'normal'},
            {'style': 'Light', 'expected_weight': '300', 'style_type': 'normal'},
            {'style': 'Regular', 'expected_weight': '400', 'style_type': 'normal'},
            {'style': 'Medium', 'expected_weight': '500', 'style_type': 'normal'},
            {'style': 'Bold', 'expected_weight': '700', 'style_type': 'normal'},
            {'style': 'Black', 'expected_weight': '900', 'style_type': 'normal'}
        ]
    },
    {
        'id': 'gr-america',
        'query': 'GR America',
        'display_name': 'GR America',
        'category': 'Sans Serif',
        'expected_family_token': 'America',
        'pill_tests': [
            {'style': 'UltraLight', 'expected_weight': '200', 'style_type': 'normal'},
            {'style': 'Light', 'expected_weight': '300', 'style_type': 'normal'},
            {'style': 'Regular', 'expected_weight': '400', 'style_type': 'normal'},
            {'style': 'Medium', 'expected_weight': '500', 'style_type': 'normal'},
            {'style': 'Bold', 'expected_weight': '700', 'style_type': 'normal'},
            {'style': 'Black', 'expected_weight': '900', 'style_type': 'normal'}
        ]
    },
    {
        'id': 'fd-gilroy',
        'query': 'Gilroy',
        'display_name': 'FD Gilroy',
        'category': 'Sans Serif',
        'expected_family_token': 'Gilroy',
        'pill_tests': [
            {'style': 'Thin', 'expected_weight': '100', 'style_type': 'normal'},
            {'style': 'Light', 'expected_weight': '300', 'style_type': 'normal'},
            {'style': 'Regular', 'expected_weight': '400', 'style_type': 'normal'},
            {'style': 'Bold', 'expected_weight': '700', 'style_type': 'normal'},
            {'style': 'Black', 'expected_weight': '900', 'style_type': 'normal'}
        ]
    }
]

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

class FontPillsAuditor:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {'total': 0, 'passed': 0, 'failed': 0},
            'network_errors_404': [],
            'successful_font_loads': [],
            'fonts_audited': {},
            'screenshots': []
        }

    def record(self, font_name, test_name, passed, details=None):
        if font_name not in self.results['fonts_audited']:
            self.results['fonts_audited'][font_name] = []
        self.results['summary']['total'] += 1
        if passed:
            self.results['summary']['passed'] += 1
            print(f"    ✅ [PASS] {test_name}")
        else:
            self.results['summary']['failed'] += 1
            print(f"    ❌ [FAIL] {test_name} | Details: {details}")
        self.results['fonts_audited'][font_name].append({
            'name': test_name,
            'passed': passed,
            'details': details
        })

    def run(self):
        port = get_free_port()
        httpd = start_local_server(port)
        local_url = f"http://127.0.0.1:{port}/index.html"

        print("=" * 80)
        print("🎯 FEDU QUALITY AUDITOR: FONT STYLE PILLS & VISUAL RENDERING SUITE")
        print(f"🌐 Local Server: {local_url}")
        print(f"📸 Screenshot Output: {SCREENSHOTS_DIR}")
        print("=" * 80)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROME_PATH,
                headless=True,
                args=['--no-sandbox', '--disable-gpu', '--font-render-hinting=medium']
            )
            context = browser.new_context(
                viewport={'width': 1600, 'height': 1000},
                device_scale_factor=2
            )
            page = context.new_page()

            # Listen to network requests/responses
            page.on('response', lambda res: self.handle_response(res))

            # Navigate
            print("\n⏳ [1/4] Navigating to Font Hub Catalog...")
            page.goto(local_url, wait_until='domcontentloaded')
            page.wait_for_selector('.font-card', timeout=15000)
            time.sleep(1.5)

            # Audit each target font
            for target in TARGET_FONTS_TO_AUDIT:
                font_name = target['display_name']
                print(f"\n" + "-" * 60)
                print(f"🔍 [AUDIT FONT] {font_name} (ID: {target['id']})")
                print("-" * 60)

                # Search to isolate card
                search_input = page.locator('#search-input')
                search_input.fill('')
                search_input.fill(target['query'])
                time.sleep(0.8)

                # Locate card
                card = page.locator(f".font-card[data-font-id='{target['id']}']").first
                if card.count() == 0:
                    card = page.locator(f".font-card:has(.card-family-name:has-text('{target['display_name']}'))").first

                if card.count() == 0:
                    self.record(font_name, f"Card Presence for {font_name}", False, f"Card not found for query {target['query']}")
                    continue

                self.record(font_name, f"Card Presence for {font_name}", True)

                # Scroll card into viewport
                card.scroll_into_view_if_needed()
                time.sleep(0.3)

                preview_el = card.locator('.preview-text')

                # Test each style pill
                for pill_info in target['pill_tests']:
                    style_name = pill_info['style']
                    exp_weight = pill_info['expected_weight']
                    print(f"  👉 Testing Style Pill: '{style_name}' (Expect weight: {exp_weight})...")

                    # Locate chip
                    chip = card.locator(f".weight-chip:has-text('{style_name}')").first
                    if chip.count() == 0:
                        # Check waterfall drawer if not visible as chip
                        waterfall_btn = card.locator('.card-styles-toggle, [data-action="toggle-card-waterfall"]').first
                        if waterfall_btn.count() > 0:
                            waterfall_btn.click()
                            time.sleep(0.3)
                        row = card.locator(f".card-waterfall-row[data-weight='{style_name}']").first
                        if row.count() > 0:
                            apply_btn = row.locator('.waterfall-apply-btn, .waterfall-sample-text').first
                            apply_btn.click()
                            time.sleep(0.5)
                        else:
                            self.record(font_name, f"Pill/Style found: {style_name}", False, "Neither weight chip nor waterfall row found")
                            continue
                    else:
                        chip.click()
                        time.sleep(0.6)

                    # Evaluate in-browser DOM & Computed Styles
                    audit_data = page.evaluate('''(args) => {
                        const [cardId, styleName, expWeight, familyToken] = args;
                        const card = document.querySelector(`.font-card[data-font-id="${cardId}"]`);
                        if (!card) return { error: 'Card not found in DOM' };
                        const preview = card.querySelector('.preview-text');
                        if (!preview) return { error: 'Preview text not found' };

                        const cs = window.getComputedStyle(preview);
                        const activeChip = card.querySelector(`.weight-chip.active`);
                        const activeChipText = activeChip ? activeChip.textContent.trim() : null;

                        // Check FontFace in document.fonts
                        const fontList = Array.from(document.fonts).map(f => ({
                            family: f.family,
                            weight: f.weight,
                            style: f.style,
                            status: f.status
                        }));

                        // Canvas anti-fallback measurement
                        const testStr = 'Typography Việt Nam Đẹp Đẽ 1234';
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        
                        // 1. Measure with system fallback
                        ctx.font = `${expWeight} 36px Times New Roman, serif`;
                        const timesWidth = ctx.measureText(testStr).width;

                        ctx.font = `${expWeight} 36px Arial, sans-serif`;
                        const arialWidth = ctx.measureText(testStr).width;

                        // 2. Measure with computed font
                        ctx.font = `${cs.fontWeight} 36px ${cs.fontFamily}`;
                        const customWidth = ctx.measureText(testStr).width;

                        return {
                            inlineWeight: preview.style.fontWeight,
                            inlineFamily: preview.style.fontFamily,
                            computedWeight: cs.fontWeight,
                            computedFamily: cs.fontFamily,
                            activeChipText: activeChipText,
                            timesWidth: timesWidth,
                            arialWidth: arialWidth,
                            customWidth: customWidth,
                            isDistinctFromTimes: Math.abs(customWidth - timesWidth) > 2.0,
                            isDistinctFromArial: Math.abs(customWidth - arialWidth) > 2.0,
                            loadedFontsCount: fontList.filter(f => f.status === 'loaded').length
                        };
                    }''', [target['id'], style_name, exp_weight, target['expected_family_token']])

                    if 'error' in audit_data:
                        self.record(font_name, f"Style [{style_name}] Execution", False, audit_data['error'])
                        continue

                    # 1. Check weight match
                    comp_w = str(audit_data['computedWeight'])
                    inline_w = str(audit_data['inlineWeight'])
                    weight_matched = (comp_w == exp_weight) or (inline_w == exp_weight)
                    self.record(
                        font_name,
                        f"Weight matching for '{style_name}' (Exp: {exp_weight}, Got inline={inline_w}, comp={comp_w})",
                        weight_matched,
                        f"Expected {exp_weight} but got computed {comp_w}"
                    )

                    # 2. Check family inclusion
                    comp_f = audit_data['computedFamily']
                    family_matched = target['expected_family_token'].lower() in comp_f.lower() or target['expected_family_token'].lower() in audit_data['inlineFamily'].lower()
                    self.record(
                        font_name,
                        f"Font-Family inclusion for '{style_name}' ({target['expected_family_token']} in stack)",
                        family_matched,
                        f"Family token '{target['expected_family_token']}' missing from '{comp_f}'"
                    )

                    # 3. Check anti-fallback (rendered glyph metrics distinct from standard system fonts)
                    is_distinct = audit_data['isDistinctFromTimes'] and audit_data['isDistinctFromArial']
                    self.record(
                        font_name,
                        f"Anti-Fallback Metric Check for '{style_name}' (Custom width={audit_data['customWidth']:.1f}px vs Arial={audit_data['arialWidth']:.1f}px / Times={audit_data['timesWidth']:.1f}px)",
                        is_distinct,
                        "Metrics match system fallback - font may not have rendered"
                    )

                    # 4. Capture High-Resolution Screenshot of the Card
                    slug_font = target['id']
                    slug_style = style_name.lower().replace(' ', '_')
                    ss_path = SCREENSHOTS_DIR / f"{slug_font}_{slug_style}.png"
                    try:
                        card.screenshot(path=str(ss_path))
                        self.results['screenshots'].append({
                            'font': font_name,
                            'style': style_name,
                            'path': str(ss_path),
                            'rel_path': f"screenshots/style_pills/{ss_path.name}",
                            'weight': comp_w,
                            'family': comp_f
                        })
                    except Exception as ss_err:
                        print(f"      ⚠️ Failed to capture screenshot: {ss_err}")

            browser.close()

        # Generate Reports
        self.generate_reports()

    def handle_response(self, res):
        url = res.url
        status = res.status
        if 'fonts/' in url or url.endswith(('.woff2', '.ttf', '.otf', '.woff')):
            if status == 404:
                self.results['network_errors_404'].append({'url': url, 'status': status})
                print(f"  🚨 [404 NOT FOUND] {url}")
            elif status == 200:
                self.results['successful_font_loads'].append({'url': url, 'status': status})

    def generate_reports(self):
        json_path = REPORTS_DIR / 'font_pills_audit_report.json'
        html_path = REPORTS_DIR / 'font_pills_audit_report.html'

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # Build Visual HTML Report
        total = self.results['summary']['total']
        passed = self.results['summary']['passed']
        failed = self.results['summary']['failed']
        pass_pct = (passed / total * 100) if total > 0 else 0
        err_404_count = len(self.results['network_errors_404'])

        cards_html = ""
        for ss in self.results['screenshots']:
            cards_html += f"""
            <div class="gallery-card">
              <div class="gallery-header">
                <span class="gallery-font">{ss['font']}</span>
                <span class="gallery-style">{ss['style']} ({ss['weight']})</span>
              </div>
              <div class="gallery-img-wrap">
                <img src="{ss['rel_path']}" alt="{ss['font']} - {ss['style']}" loading="lazy"/>
              </div>
              <div class="gallery-footer">
                <code>{ss['family'][:45]}...</code>
              </div>
            </div>
            """

        table_rows = ""
        for font_name, tests in self.results['fonts_audited'].items():
            for t in tests:
                badge = '<span class="badge pass">PASS</span>' if t['passed'] else '<span class="badge fail">FAIL</span>'
                details = t['details'] or 'OK'
                table_rows += f"""
                <tr>
                  <td><strong>{font_name}</strong></td>
                  <td>{t['name']}</td>
                  <td>{badge}</td>
                  <td><small>{details}</small></td>
                </tr>
                """

        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Quality Auditor Report — Font Style Pills & Visual Rendering</title>
  <style>
    :root {{
      --bg: #0d0f12;
      --card-bg: #161920;
      --border: #262c38;
      --text: #f0f3f8;
      --text-muted: #8892b0;
      --accent: #00E599;
      --fail: #ff4d6d;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 30px;
      line-height: 1.5;
    }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px 0; font-size: 26px; }}
    .meta {{ color: var(--text-muted); font-size: 14px; margin-bottom: 24px; }}
    .stats-row {{ display: flex; gap: 16px; margin-bottom: 30px; }}
    .stat-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      padding: 16px 22px;
      border-radius: 8px;
      flex: 1;
    }}
    .stat-val {{ font-size: 28px; font-weight: 700; color: var(--accent); }}
    .stat-val.fail {{ color: var(--fail); }}
    .stat-label {{ font-size: 12px; text-transform: uppercase; color: var(--text-muted); }}

    .section-title {{ font-size: 20px; margin: 30px 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}

    .gallery-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }}
    .gallery-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .gallery-header {{
      padding: 10px 14px;
      background: rgba(255,255,255,0.02);
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      font-size: 13px;
    }}
    .gallery-font {{ font-weight: 600; color: #fff; }}
    .gallery-style {{ color: var(--accent); }}
    .gallery-img-wrap img {{
      width: 100%;
      height: auto;
      display: block;
      border-bottom: 1px solid var(--border);
    }}
    .gallery-footer {{ padding: 8px 12px; font-size: 11px; color: var(--text-muted); }}

    table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }}
    th {{ background: rgba(255,255,255,0.03); color: var(--text-muted); }}
    .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; }}
    .badge.pass {{ background: rgba(0,229,153,0.15); color: #00E599; }}
    .badge.fail {{ background: rgba(255,77,109,0.15); color: #ff4d6d; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Quality Auditor Report — Font Style Pills & Visual Verification</h1>
    <div class="meta">Execution Date: {self.results['timestamp']} • Local Chrome E2E Engine</div>

    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-val">{passed} / {total}</div>
        <div class="stat-label">Tests Passed ({pass_pct:.1f}%)</div>
      </div>
      <div class="stat-box">
        <div class="stat-val {'fail' if failed > 0 else ''}">{failed}</div>
        <div class="stat-label">Tests Failed</div>
      </div>
      <div class="stat-box">
        <div class="stat-val {'fail' if err_404_count > 0 else ''}">{err_404_count}</div>
        <div class="stat-label">Font 404 Errors</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">{len(self.results['successful_font_loads'])}</div>
        <div class="stat-label">Successful Font Loads (200 OK)</div>
      </div>
    </div>

    <div class="section-title">Visual Specimen Proof Gallery ({len(self.results['screenshots'])} Screenshots)</div>
    <div class="gallery-grid">
      {cards_html}
    </div>

    <div class="section-title">Detailed Test Assertion Breakdown</div>
    <table>
      <thead>
        <tr>
          <th>Font Family</th>
          <th>Assertion Scope</th>
          <th>Status</th>
          <th>Details / Metrics</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print("\n" + "=" * 80)
        print("🏁 AUDIT RUN COMPLETE")
        print(f"📊 Passed: {passed}/{total} ({pass_pct:.1f}%) | Failed: {failed} | 404 Errors: {err_404_count}")
        print(f"📄 HTML Report: file://{html_path}")
        print(f"📄 JSON Report: file://{json_path}")
        print("=" * 80)

if __name__ == '__main__':
    auditor = FontPillsAuditor()
    auditor.run()
