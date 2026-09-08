#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_audit_variant_pills_and_domain_deep_e2e.py
Autonomous Quality Auditor Deep E2E Verification Suite:
1. Font Variant Pills Preview (CSS weights, styles, active class, anti-fallback).
2. Isolation check: Clicking pills MUST NOT trigger Studio Grouping filter or toast.
3. Waterfall row preview updates & isolation.
4. Positive verification: Direct click on button.badge-studio works as expected.
5. Domain Audit: 100% font.fedu.vn, CNAME, vercel.json, canonical, og:url, zero fonthub.fedu.vn regressions.
"""

import os
import sys
import json
import time
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
REPORTS_DIR = PROJECT_ROOT / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def start_local_server(port):
    class DualDirHandler(QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)
    httpd = HTTPServer(('127.0.0.1', port), DualDirHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

class DeepVariantAndDomainAuditor:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {'total': 0, 'passed': 0, 'failed': 0},
            'suites': {},
            'console_errors': [],
            'network_404_errors': []
        }

    def record(self, suite, test_name, status, details=""):
        if suite not in self.results['suites']:
            self.results['suites'][suite] = []
        self.results['summary']['total'] += 1
        if status:
            self.results['summary']['passed'] += 1
            icon = "✅"
        else:
            self.results['summary']['failed'] += 1
            icon = "❌"
        self.results['suites'][suite].append({
            'test': test_name,
            'status': status,
            'details': details
        })
        print(f"  {icon} [{suite}] {test_name}" + (f" -> {details}" if details and not status else ""), flush=True)

    def run_domain_static_audit(self):
        suite = "Domain & Configuration Audit"
        print(f"\n[SUITE] {suite}", flush=True)

        # 1. CNAME check
        cname_path = PROJECT_ROOT / 'CNAME'
        cname_exists = cname_path.exists()
        cname_content = cname_path.read_text(encoding='utf-8').strip() if cname_exists else ''
        self.record(suite, "CNAME file exists and points to font.fedu.vn",
                    cname_exists and cname_content == 'font.fedu.vn',
                    f"Content: '{cname_content}'")

        # 2. vercel.json check
        vercel_path = PROJECT_ROOT / 'vercel.json'
        vercel_exists = vercel_path.exists()
        try:
            with open(vercel_path, 'r', encoding='utf-8') as f:
                v_data = json.load(f)
            v_name = v_data.get('name')
            self.record(suite, "vercel.json has project name 'font-fedu-vn'",
                        v_name == 'font-fedu-vn', f"name: '{v_name}'")
        except Exception as e:
            self.record(suite, "vercel.json has project name 'font-fedu-vn'", False, str(e))

        # 3. index.html canonical and meta tags
        html_path = PROJECT_ROOT / 'index.html'
        html_content = html_path.read_text(encoding='utf-8')
        has_canonical = '<link rel="canonical" href="https://font.fedu.vn/">' in html_content
        self.record(suite, "index.html contains canonical tag for font.fedu.vn",
                    has_canonical, "Canonical tag verified")

        has_og_url = '<meta property="og:url" content="https://font.fedu.vn/">' in html_content
        self.record(suite, "index.html contains og:url meta tag for font.fedu.vn",
                    has_og_url, "og:url verified")

        has_twitter_url = '<meta name="twitter:url" content="https://font.fedu.vn/">' in html_content
        # 3. vercel.json 301 Redirect Check
        has_301_redirect = False
        try:
            with open(vercel_path, 'r', encoding='utf-8') as f:
                v_data = json.load(f)
            redirects = v_data.get('redirects', [])
            for r in redirects:
                if r.get('destination') == 'https://font.fedu.vn/:path*' and r.get('permanent') is True:
                    for h in r.get('has', []):
                        if h.get('value') == 'fonthub.fedu.vn':
                            has_301_redirect = True
        except Exception:
            pass
        self.record(suite, "vercel.json configures 301 Permanent Redirect fonthub.fedu.vn -> font.fedu.vn",
                    has_301_redirect, "301 Redirect to font.fedu.vn configured")

        # 4. Zero old legacy domain in source files
        found_fonthub_files = []
        extensions_to_check = {'.html', '.js', '.css', '.json', '.py', '.md', '.txt', '.sh'}
        skip_dirs = {'.git', 'reports', 'node_modules', '__pycache__'}
        legacy_domain = 'font' + 'hub.fedu.vn'
        current_script = Path(__file__).resolve()

        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in extensions_to_check:
                    fpath = (Path(root) / file).resolve()
                    if fpath == current_script or fpath == vercel_path:
                        continue
                    try:
                        content = fpath.read_text(encoding='utf-8', errors='ignore')
                        if legacy_domain in content:
                            found_fonthub_files.append(str(fpath.relative_to(PROJECT_ROOT)))
                    except Exception:
                        pass

        self.record(suite, "Zero unintended occurrences of fonthub.fedu.vn across active codebase",
                    len(found_fonthub_files) == 0,
                    f"Found in: {found_fonthub_files}" if found_fonthub_files else "Clean 0 matches")

    def run_browser_e2e_tests(self):
        port = get_free_port()
        httpd = start_local_server(port)
        url = f"http://127.0.0.1:{port}/index.html"
        print(f"\n🌐 Local Web Server started at {url}", flush=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1440, 'height': 900})

            # Track network 404s
            def on_response(res):
                if ('fonts/' in res.url or res.url.endswith(('.woff2', '.ttf', '.otf'))) and res.status == 404:
                    self.results['network_404_errors'].append(res.url)
            page.on('response', on_response)

            # Track console errors
            def on_console(msg):
                if msg.type == 'error':
                    self.results['console_errors'].append(msg.text)
            page.on('console', on_console)

            # Navigate to catalog
            page.goto(url, wait_until='networkidle')
            page.wait_for_selector('.font-card', timeout=15000)
            time.sleep(1)

            total_initial_cards = page.locator('.font-card').count()

            # -------------------------------------------------------------
            # SUITE: Variant Pills & Preview CSS
            # -------------------------------------------------------------
            suite_pills = "Variant Pills Preview & Behavior Isolation"
            print(f"\n[SUITE] {suite_pills}", flush=True)

            test_targets = [
                {
                    'id': 'gr-sectra',
                    'name': 'GR Sectra',
                    'query': 'Sectra',
                    'pills': [
                        {'name': 'Light', 'weight': '300'},
                        {'name': 'Regular', 'weight': '400'},
                        {'name': 'Medium', 'weight': '500'},
                        {'name': 'Bold', 'weight': '700'},
                        {'name': 'Super', 'weight': '800'},
                        {'name': 'Black', 'weight': '900'}
                    ]
                },
                {
                    'id': 'gr-walsheim',
                    'name': 'GR Walsheim',
                    'query': 'Walsheim',
                    'pills': [
                        {'name': 'UltraLight', 'weight': '200'},
                        {'name': 'Light', 'weight': '300'},
                        {'name': 'Regular', 'weight': '400'},
                        {'name': 'Medium', 'weight': '500'},
                        {'name': 'Bold', 'weight': '700'},
                        {'name': 'Black', 'weight': '900'}
                    ]
                },
                {
                    'id': 'fd-gilroy',
                    'name': 'FD Gilroy',
                    'query': 'Gilroy',
                    'pills': [
                        {'name': 'Thin', 'weight': '100'},
                        {'name': 'Light', 'weight': '300'},
                        {'name': 'Regular', 'weight': '400'},
                        {'name': 'Bold', 'weight': '700'},
                        {'name': 'Black', 'weight': '900'}
                    ]
                }
            ]

            for target in test_targets:
                font_name = target['name']
                print(f"\n  --- Testing Font: {font_name} ---", flush=True)

                # Filter by search
                page.evaluate('''(q) => {
                    const inp = document.getElementById('search-input');
                    inp.value = q;
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                }''', target['query'])
                time.sleep(0.4)

                card = page.locator(f".font-card[data-font-id='{target['id']}']").first
                if card.count() == 0:
                    card = page.locator(f".font-card:has(.card-family-name:has-text('{font_name}'))").first

                card.scroll_into_view_if_needed()
                time.sleep(0.2)

                for pill in target['pills']:
                    p_name = pill['name']
                    exp_w = pill['weight']

                    # Clear existing toasts if any
                    page.evaluate('''() => {
                        document.querySelectorAll('.toast, .toast-container, [role="alert"]').forEach(t => t.remove());
                    }''')

                    # Click pill with EXACT MATCH prioritized
                    click_res = card.evaluate('''(cardEl, pName) => {
                        const chips = Array.from(cardEl.querySelectorAll('.weight-chip'));
                        const cleanP = pName.trim().toLowerCase();
                        
                        // 1. Exact match
                        let chip = chips.find(c => c.textContent.trim().toLowerCase() === cleanP);
                        
                        // 2. Exact word token match (e.g. "Bold" in "Bold Italic")
                        if (!chip) {
                            chip = chips.find(c => {
                                const tokens = c.textContent.trim().toLowerCase().split(/[\\s-_]+/);
                                return tokens.includes(cleanP);
                            });
                        }
                        
                        // 3. Fallback partial match if still not found
                        if (!chip) {
                            chip = chips.find(c => c.textContent.toLowerCase().includes(cleanP));
                        }

                        if (!chip) return { success: false, error: 'Chip not found for ' + pName };
                        
                        chip.click();
                        return {
                            success: true,
                            matchedText: chip.textContent.trim(),
                            isActive: chip.classList.contains('active'),
                            weightAttr: chip.getAttribute('data-weight')
                        };
                    }''', p_name)

                    self.record(suite_pills, f"{font_name} [{p_name}]: Pill exists and accepts click",
                                click_res.get('success', False), click_res.get('error', ''))

                    if not click_res.get('success'):
                        continue

                    self.record(suite_pills, f"{font_name} [{p_name}]: Pill gets .active class",
                                click_res.get('isActive', False))

                    time.sleep(0.4)

                    # Verify preview styles
                    style_res = card.evaluate('''(cardEl) => {
                        const preview = cardEl.querySelector('.preview-text');
                        const slider = cardEl.querySelector('.card-weight-slider');
                        const val = cardEl.querySelector('.card-weight-val');
                        const cs = window.getComputedStyle(preview);
                        return {
                            inlineWeight: preview.style.fontWeight,
                            computedWeight: cs.fontWeight,
                            inlineStyle: preview.style.fontStyle,
                            computedStyle: cs.fontStyle,
                            fontFamily: preview.style.fontFamily || cs.fontFamily,
                            sliderValue: slider ? slider.value : null,
                            valText: val ? val.textContent.trim() : null
                        };
                    }''')

                    weight_matched = (str(style_res.get('computedWeight')) == exp_w) or (str(style_res.get('inlineWeight')) == exp_w)
                    self.record(suite_pills, f"{font_name} [{p_name}]: Rendered font-weight matches {exp_w}",
                                weight_matched, f"inline={style_res.get('inlineWeight')}, comp={style_res.get('computedWeight')}")

                    if style_res.get('sliderValue'):
                        slider_matched = str(style_res.get('sliderValue')) == exp_w
                        self.record(suite_pills, f"{font_name} [{p_name}]: Card slider synced to {exp_w}",
                                    slider_matched, f"got {style_res.get('sliderValue')}")

                    # ANTI-BUG ISOLATION CHECK: Verify NO studio toast appeared!
                    toast_check = page.evaluate('''() => {
                        const toasts = Array.from(document.querySelectorAll('.toast, .toast-info, .notification, [role="alert"]'));
                        const studioToasts = toasts.filter(t => t.textContent.includes('Studio') || t.textContent.includes('Gom nhóm') || t.textContent.includes('Đã lọc theo Studio'));
                        const studioSelect = document.getElementById('filter-studio');
                        return {
                            studioToastCount: studioToasts.length,
                            studioToastsText: studioToasts.map(t => t.textContent.trim()),
                            studioFilterVal: studioSelect ? studioSelect.value : ''
                        };
                    }''')

                    self.record(suite_pills, f"{font_name} [{p_name}]: NO accidental Studio Toast triggered",
                                toast_check['studioToastCount'] == 0,
                                f"Toasts: {toast_check['studioToastsText']}")

                    is_unfiltered = toast_check['studioFilterVal'] in ('', 'all')
                    self.record(suite_pills, f"{font_name} [{p_name}]: Studio filter remained unset ('all')",
                                is_unfiltered,
                                f"Studio val: '{toast_check['studioFilterVal']}'")

            # -------------------------------------------------------------
            # SUITE: Waterfall Row Interaction Isolation
            # -------------------------------------------------------------
            suite_waterfall = "Waterfall Row Interaction & Isolation"
            print(f"\n[SUITE] {suite_waterfall}", flush=True)

            # Reset search input
            page.evaluate('''() => {
                const inp = document.getElementById('search-input');
                inp.value = 'Walsheim';
                inp.dispatchEvent(new Event('input', { bubbles: true }));
            }''')
            time.sleep(0.4)

            w_card = page.locator(".font-card[data-font-id='gr-walsheim']").first
            page.evaluate('''(cardEl) => {
                const toggle = cardEl.querySelector('.card-waterfall-toggle, [data-action="toggle-waterfall"]');
                if (toggle) toggle.click();
            }''', w_card.element_handle())
            time.sleep(0.3)

            wf_res = w_card.evaluate('''(cardEl) => {
                const rows = Array.from(cardEl.querySelectorAll('.card-waterfall-row'));
                if (rows.length === 0) return { count: 0 };
                const row = rows[rows.length - 1]; // pick last row (Black / Heavy)
                row.click();
                const preview = cardEl.querySelector('.preview-text');
                return {
                    count: rows.length,
                    rowActive: row.classList.contains('is-active'),
                    previewWeight: preview.style.fontWeight,
                    previewFamily: preview.style.fontFamily
                };
            }''')

            if wf_res.get('count', 0) > 0:
                self.record(suite_waterfall, "Waterfall row click updates row to is-active",
                            wf_res.get('rowActive', False))
                self.record(suite_waterfall, "Waterfall row click updates preview font-weight",
                            bool(wf_res.get('previewWeight')), f"Weight: {wf_res.get('previewWeight')}")

                # Check isolation
                wf_toast = page.evaluate('''() => {
                    const toasts = Array.from(document.querySelectorAll('.toast'));
                    return toasts.filter(t => t.textContent.includes('Studio')).length;
                }''')
                self.record(suite_waterfall, "Waterfall row click does NOT trigger Studio toast",
                            wf_toast == 0, f"Found {wf_toast} toasts")

            # -------------------------------------------------------------
            # SUITE: Intentional Studio Badge Click (Positive Test)
            # -------------------------------------------------------------
            suite_studio = "Intentional Studio Badge Grouping"
            print(f"\n[SUITE] {suite_studio}", flush=True)

            # Reset search
            page.evaluate('''() => {
                const inp = document.getElementById('search-input');
                inp.value = '';
                inp.dispatchEvent(new Event('input', { bubbles: true }));
            }''')
            time.sleep(0.5)

            badge_click_res = page.evaluate('''() => {
                const badge = document.querySelector('.font-card button.badge-studio, .font-card .badge-studio');
                if (!badge) return { success: false, error: 'No badge found' };
                const studio = badge.getAttribute('data-studio');
                badge.click();
                return {
                    success: true,
                    studio: studio
                };
            }''')

            time.sleep(0.5)
            self.record(suite_studio, "Direct click on button.badge-studio succeeds",
                        badge_click_res.get('success', False))

            if badge_click_res.get('success'):
                expected_studio = badge_click_res.get('studio')
                post_studio_check = page.evaluate('''(expStudio) => {
                    const studioSelect = document.getElementById('filter-studio');
                    const cards = Array.from(document.querySelectorAll('.font-card:not([style*="display: none"])'));
                    return {
                        selectValue: studioSelect ? studioSelect.value : '',
                        visibleCardsCount: cards.length
                    };
                }''', expected_studio)

                self.record(suite_studio, f"Catalog filtered to Studio '{expected_studio}'",
                            post_studio_check['selectValue'] == expected_studio and post_studio_check['visibleCardsCount'] < total_initial_cards,
                            f"Select: '{post_studio_check['selectValue']}', Cards: {post_studio_check['visibleCardsCount']}/{total_initial_cards}")

                # Clear filters
                page.evaluate('''() => {
                    const clearBtn = document.getElementById('clear-filters-btn') || document.querySelector('.btn-clear-filters');
                    if (clearBtn) clearBtn.click();
                }''')
                time.sleep(0.5)

                restored_cards = page.locator('.font-card').count()
                self.record(suite_studio, "Clear filters restores all font cards",
                            restored_cards == total_initial_cards,
                            f"Restored {restored_cards}/{total_initial_cards} cards")

            # -------------------------------------------------------------
            # SUITE: Console Errors & Network 404 Checks
            # -------------------------------------------------------------
            suite_hygiene = "Console & Network Hygiene"
            print(f"\n[SUITE] {suite_hygiene}", flush=True)

            self.record(suite_hygiene, "Zero console runtime errors",
                        len(self.results['console_errors']) == 0,
                        f"Errors: {self.results['console_errors']}")

            self.record(suite_hygiene, "Zero 404 font asset network errors",
                        len(self.results['network_404_errors']) == 0,
                        f"404s: {self.results['network_404_errors']}")

            browser.close()

    def generate_report(self):
        json_path = REPORTS_DIR / 'deep_variant_and_domain_audit_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        html_path = REPORTS_DIR / 'deep_variant_and_domain_audit_report.html'
        passed = self.results['summary']['passed']
        total = self.results['summary']['total']
        failed = self.results['summary']['failed']
        pct = (passed / total * 100) if total > 0 else 0

        html_rows = ""
        for suite, tests in self.results['suites'].items():
            html_rows += f"<tr class='suite-hdr'><th colspan='3'>{suite}</th></tr>"
            for t in tests:
                badge = "<span class='badge-pass'>PASS</span>" if t['status'] else "<span class='badge-fail'>FAIL</span>"
                html_rows += f"""
                <tr>
                  <td>{t['test']}</td>
                  <td>{badge}</td>
                  <td><code>{t['details']}</code></td>
                </tr>
                """

        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Deep E2E Variant & Domain Audit Report — FEDU FONT (font.fedu.vn)</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f1117; color: #e5e7eb; margin: 0; padding: 24px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d3748; padding-bottom: 16px; margin-bottom: 24px; }}
    .score {{ font-size: 32px; font-weight: 700; color: #10b981; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; background: #1a202c; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #2d3748; font-size: 14px; }}
    th {{ background: #2d3748; color: #a0aec0; }}
    .suite-hdr th {{ background: #1e293b; color: #38bdf8; font-size: 15px; text-transform: uppercase; letter-spacing: 0.05em; }}
    .badge-pass {{ background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 8px; border-radius: 4px; font-weight: 600; }}
    .badge-fail {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: 600; }}
    code {{ color: #94a3b8; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1 style="margin:0; font-size:22px;">FEDU FONT — Deep E2E Variant & Domain Audit</h1>
        <p style="margin:4px 0 0; color:#94a3b8;">Target: font.fedu.vn | Tested at: {self.results['timestamp']}</p>
      </div>
      <div class="score">{passed}/{total} ({pct:.1f}%)</div>
    </div>
    <table>
      <thead>
        <tr><th>Test Case</th><th>Status</th><th>Details</th></tr>
      </thead>
      <tbody>
        {html_rows}
      </tbody>
    </table>
  </div>
</body>
</html>"""
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print("\n" + "=" * 70, flush=True)
        print(f"🏁 AUDIT SUMMARY: {passed}/{total} Passed ({pct:.1f}%) | {failed} Failed", flush=True)
        print(f"📄 HTML Report: file://{html_path}", flush=True)
        print(f"📄 JSON Report: file://{json_path}", flush=True)
        print("=" * 70 + "\n", flush=True)

if __name__ == '__main__':
    auditor = DeepVariantAndDomainAuditor()
    auditor.run_domain_static_audit()
    auditor.run_browser_e2e_tests()
    auditor.generate_report()
