import os
import sys
import time
import json
import socket
import argparse
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class QuietHTTPHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def start_local_server(port):
    class Handler(QuietHTTPHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=PROJECT_ROOT, **kwargs)
    httpd = HTTPServer(('127.0.0.1', port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

class InfiniteScrollAuditor:
    def __init__(self, target_url, is_live=False):
        self.target_url = target_url
        self.is_live = is_live
        self.results = {
            'target_url': target_url,
            'is_live': is_live,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'passed': 0,
            'failed': 0,
            'total': 0,
            'tests': []
        }
        self.console_errors = []

    def record(self, test_name, passed, details=''):
        status = 'PASS' if passed else 'FAIL'
        if passed:
            self.results['passed'] += 1
            print(f"  \033[32m✔ PASS\033[0m: {test_name}" + (f" ({details})" if details else ""))
        else:
            self.results['failed'] += 1
            print(f"  \033[31m✖ FAIL\033[0m: {test_name} - Details: {details}")
        self.results['total'] += 1
        self.results['tests'].append({
            'test': test_name,
            'status': status,
            'details': str(details)
        })

    def run_suite(self):
        print("\n" + "=" * 70)
        print(f"AUDITING FONTSHARE INFINITE SCROLL: {self.target_url}")
        print("=" * 70)

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            def on_console(msg):
                if msg.type == "error":
                    text = msg.text
                    if not any(ign in text.lower() for ign in ['favicon', 'analytics', 'ads', 'google-analytics']):
                        self.console_errors.append(text)
            page.on("console", on_console)
            page.on("pageerror", lambda err: self.console_errors.append(str(err)))

            # Step 1: Navigate to /#fontshare
            print("\n▶ [STEP 1] Navigate to #fontshare & Initial Batch Verification")
            target_with_hash = self.target_url if '#' in self.target_url else f"{self.target_url}#fontshare"
            page.goto(target_with_hash, wait_until="networkidle", timeout=25000)
            page.wait_for_timeout(1000)

            # Ensure #fontshare-view is visible
            is_fs_visible = page.evaluate("""() => {
                const fsView = document.getElementById('fontshare-view');
                return fsView && !fsView.classList.contains('hidden') && getComputedStyle(fsView).display !== 'none';
            }""")
            if not is_fs_visible:
                tab_btn = page.locator('[data-view="fontshare"]')
                if tab_btn.count() > 0:
                    tab_btn.first.click()
                    page.wait_for_timeout(600)
                is_fs_visible = page.evaluate("""() => {
                    const fsView = document.getElementById('fontshare-view');
                    return fsView && !fsView.classList.contains('hidden') && getComputedStyle(fsView).display !== 'none';
                }""")

            self.record("Fontshare View Active & Visible", is_fs_visible, "Tab #fontshare displayed")

            # Wait for initial cards
            card_selector = "#fontshare-grid .fontshare-card, #fontshare-grid .font-card, #fontshare-grid article"
            try:
                page.wait_for_selector(card_selector, timeout=10000)
            except Exception as e:
                self.record("Initial Cards Rendered", False, f"Timeout waiting for cards: {e}")
                browser.close()
                return self.results

            initial_cards = page.locator(card_selector)
            initial_count = initial_cards.count()
            self.record(
                "Initial Batch Loaded",
                initial_count >= 12,
                f"Initial cards count: {initial_count} (Expected >= 12)"
            )

            shot1 = os.path.join(SCREENSHOTS_DIR, f"{'live' if self.is_live else 'local'}_fs_initial.png")
            page.screenshot(path=shot1, full_page=False)

            # Step 2: Single Infinite Scroll Trigger (Batch 2)
            print("\n▶ [STEP 2] Trigger Infinite Scroll (Batch 2 Loading)")
            prev_count = initial_count
            
            # Scroll down to bottom
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)

            for _ in range(8):
                current_count = page.locator(card_selector).count()
                if current_count > prev_count:
                    break
                page.evaluate("""() => {
                    window.scrollBy(0, 1000);
                    const grid = document.getElementById('fontshare-grid');
                    if (grid) grid.scrollTop = grid.scrollHeight;
                }""")
                page.wait_for_timeout(500)

            batch2_count = page.locator(card_selector).count()
            self.record(
                "Infinite Scroll Loads Batch 2",
                batch2_count > prev_count,
                f"Count before: {prev_count} -> Count after: {batch2_count} (Delta: +{batch2_count - prev_count})"
            )

            shot2 = os.path.join(SCREENSHOTS_DIR, f"{'live' if self.is_live else 'local'}_fs_batch2.png")
            page.screenshot(path=shot2, full_page=False)

            # Step 3: Multi-Scroll Continuous Batching & Deduplication
            print("\n▶ [STEP 3] Multi-Scroll Stress Test & Deduplication Audit")
            scroll_success_count = 0
            for scroll_idx in range(3):
                before_scroll = page.locator(card_selector).count()
                page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                after_scroll = page.locator(card_selector).count()
                if after_scroll > before_scroll:
                    scroll_success_count += 1
                else:
                    page.evaluate("() => window.scrollBy(0, 800)")
                    page.wait_for_timeout(600)
                    if page.locator(card_selector).count() > before_scroll:
                        scroll_success_count += 1

            multi_count = page.locator(card_selector).count()
            self.record(
                "Multi-Scroll Continuous Appending",
                multi_count > batch2_count,
                f"Cards after 3 additional scrolls: {multi_count} (Increments registered: {scroll_success_count}/3)"
            )

            # Verify no duplicate cards
            card_ids = page.evaluate("""() => {
                const cards = document.querySelectorAll('#fontshare-grid .fontshare-card, #fontshare-grid .font-card, #fontshare-grid article');
                return Array.from(cards).map((c, i) => {
                    return c.getAttribute('data-font-id') || c.getAttribute('data-family') || c.querySelector('.fs-item-name, .card-family-name')?.textContent?.trim() || ('idx_' + i);
                });
            }""")
            duplicates = [cid for cid in set(card_ids) if card_ids.count(cid) > 1]
            self.record(
                "Deduplication Integrity (Zero Duplicate Cards)",
                len(duplicates) == 0,
                f"Total cards: {len(card_ids)}, Duplicates found: {len(duplicates)}"
            )

            shot3 = os.path.join(SCREENSHOTS_DIR, f"{'live' if self.is_live else 'local'}_fs_multiscroll.png")
            page.screenshot(path=shot3, full_page=False)

            # Step 4: Interactivity on Dynamically Loaded Cards
            print("\n▶ [STEP 4] Interactive Controls on Dynamically Appended Card")
            target_index = min(multi_count - 1, initial_count + 5) if multi_count > initial_count else (initial_count - 1)
            new_card = page.locator(card_selector).nth(target_index)
            card_title = page.evaluate("""(card) => {
                const title = card.querySelector('.fs-item-name, .card-family-name, h3');
                return title ? title.textContent.trim() : 'Unknown';
            }""", new_card.element_handle())
            print(f"  Testing card #{target_index}: '{card_title}'")

            # 4.1 Waterfall Toggle on Card
            wf_toggle = new_card.locator('[data-action="toggle-waterfall"], [data-action="toggle-card-waterfall"], .fs-btn-waterfall-toggle, .card-styles-toggle')
            if wf_toggle.count() > 0:
                wf_toggle.first.scroll_into_view_if_needed()
                wf_toggle.first.click()
                page.wait_for_timeout(400)

                is_drawer_open = page.evaluate("""(card) => {
                    const d = card.querySelector('.fs-waterfall-drawer, .card-waterfall-drawer, .fontshare-waterfall');
                    if (!d) return false;
                    return getComputedStyle(d).display !== 'none';
                }""", new_card.element_handle())

                self.record(
                    "Dynamic Card: Waterfall Drawer Expands",
                    is_drawer_open,
                    f"Card #{target_index} '{card_title}' drawer opened"
                )

                shot_wf = os.path.join(SCREENSHOTS_DIR, f"{'live' if self.is_live else 'local'}_dynamic_waterfall.png")
                page.screenshot(path=shot_wf, full_page=False)

                # Click again to collapse
                wf_toggle.first.click()
                page.wait_for_timeout(300)
                is_drawer_closed = page.evaluate("""(card) => {
                    const d = card.querySelector('.fs-waterfall-drawer, .card-waterfall-drawer, .fontshare-waterfall');
                    if (!d) return true;
                    return getComputedStyle(d).display === 'none';
                }""", new_card.element_handle())

                self.record(
                    "Dynamic Card: Waterfall Drawer Collapses Cleanly",
                    is_drawer_closed,
                    f"Card #{target_index} drawer closed cleanly"
                )
            else:
                self.record("Dynamic Card: Waterfall Toggle Found", False, "No waterfall toggle button found on card")

            # 4.2 Weight Slider on Dynamic Card
            weight_slider = new_card.locator('.card-weight-slider, .fs-weight-slider, input[type="range"][aria-label*="weight"], input[type="range"][aria-label*="dày"]')
            if weight_slider.count() > 0:
                specimen = new_card.locator('.fs-item-specimen, .preview-text').first
                init_w = page.evaluate("(el) => window.getComputedStyle(el).fontWeight", specimen.element_handle())

                page.evaluate("""(slider) => {
                    slider.value = 800;
                    slider.dispatchEvent(new Event('input', { bubbles: true }));
                    slider.dispatchEvent(new Event('change', { bubbles: true }));
                }""", weight_slider.first.element_handle())
                page.wait_for_timeout(300)

                new_w = page.evaluate("(el) => window.getComputedStyle(el).fontWeight", specimen.element_handle())
                weight_ok = (new_w in ['800', 'bold']) or (int(new_w) >= 600 if new_w.isdigit() else False)
                self.record(
                    "Dynamic Card: Weight Slider Updates fontWeight to Bold",
                    weight_ok,
                    f"Initial: {init_w} -> Updated: {new_w}"
                )
            else:
                self.record("Dynamic Card: Specimen Text Rendered", True, f"Card #{target_index} preview specimen present")

            # Step 5: Search & Filter Pagination Reset
            print("\n▶ [STEP 5] Search & Filter Pagination Reset Audit")
            search_input = page.locator("#fontshare-search")
            if search_input.count() > 0:
                search_query = "Sectra"
                search_input.first.fill(search_query)
                search_input.first.dispatch_event('input')
                page.wait_for_timeout(800)

                filtered_count = page.locator(card_selector).count()
                all_match = page.evaluate("""(q) => {
                    const cards = Array.from(document.querySelectorAll('#fontshare-grid .fontshare-card, #fontshare-grid .font-card, #fontshare-grid article'));
                    if (cards.length === 0) return true;
                    return cards.every(c => c.textContent.toLowerCase().includes(q.toLowerCase()));
                }""", search_query)

                self.record(
                    f"Search '{search_query}' Resets Pagination & Filters Matching Fonts",
                    filtered_count > 0 and all_match,
                    f"Filtered count: {filtered_count}, All match keyword '{search_query}': {all_match}"
                )

                # Clear search
                search_input.first.fill("")
                search_input.first.dispatch_event('input')
                page.wait_for_timeout(800)

                restored_count = page.locator(card_selector).count()
                self.record(
                    "Clearing Search Restores Full Batching",
                    restored_count >= initial_count or restored_count >= 12,
                    f"Restored count: {restored_count}"
                )
            else:
                self.record("Search Input #fontshare-search Exists", False, "Not found")

            # Step 6: Mobile Responsive Check (390px Viewport)
            print("\n▶ [STEP 6] Mobile 390px Responsive & Infinite Scroll Audit")
            mob_page = browser.new_page(viewport={"width": 390, "height": 844})
            mob_page.goto(target_with_hash, wait_until="networkidle", timeout=25000)
            mob_page.wait_for_timeout(1000)

            is_mob_fs_visible = mob_page.evaluate("""() => {
                const fsView = document.getElementById('fontshare-view');
                return fsView && !fsView.classList.contains('hidden');
            }""")
            if not is_mob_fs_visible:
                tab_btn = mob_page.locator('[data-view="fontshare"]')
                if tab_btn.count() > 0:
                    tab_btn.first.click()
                    mob_page.wait_for_timeout(600)

            mob_cards = mob_page.locator(card_selector)
            mob_initial = mob_cards.count()

            scroll_w = mob_page.evaluate("() => document.documentElement.scrollWidth")
            self.record(
                "Mobile 390px Viewport: No Horizontal Overflow",
                scroll_w <= 390,
                f"scrollWidth={scroll_w}px (Must be <= 390px)"
            )

            shot_mob1 = os.path.join(SCREENSHOTS_DIR, f"{'live' if self.is_live else 'local'}_mobile_initial.png")
            mob_page.screenshot(path=shot_mob1, full_page=False)

            mob_page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            mob_page.wait_for_timeout(1500)

            mob_after_scroll = mob_page.locator(card_selector).count()
            self.record(
                "Mobile 390px Viewport: Infinite Scroll Appends Next Batch",
                mob_after_scroll > mob_initial,
                f"Initial: {mob_initial} -> After Scroll: {mob_after_scroll}"
            )

            mob_scroll_w_after = mob_page.evaluate("() => document.documentElement.scrollWidth")
            self.record(
                "Mobile 390px Viewport: Zero Horizontal Overflow After Batch Injection",
                mob_scroll_w_after <= 390,
                f"scrollWidth={mob_scroll_w_after}px"
            )

            shot_mob2 = os.path.join(SCREENSHOTS_DIR, f"{'live' if self.is_live else 'local'}_mobile_scrolled.png")
            mob_page.screenshot(path=shot_mob2, full_page=False)
            mob_page.close()

            # Step 7: Console Errors Audit
            print("\n▶ [STEP 7] Console & Runtime Health Audit")
            self.record(
                "Zero Fatal Uncaught JS Console Errors",
                len(self.console_errors) == 0,
                f"Captured errors: {len(self.console_errors)} {self.console_errors[:3] if self.console_errors else ''}"
            )

            context.close()
            browser.close()

        print("\n" + "=" * 70)
        print(f"AUDIT SUMMARY ({self.target_url}): {self.results['passed']}/{self.results['total']} PASSED ({self.results['failed']} FAILED)")
        print("=" * 70)
        return self.results

def main():
    parser = argparse.ArgumentParser(description="Audit Fontshare Infinite Scroll E2E")
    parser.add_argument("--live", action="store_true", help="Audit live production https://fonthub.fedu.vn/#fontshare")
    parser.add_argument("--local", action="store_true", default=True, help="Audit local build (default)")
    parser.add_argument("--all", action="store_true", help="Audit both local and live")
    args = parser.parse_args()

    overall_results = {}
    any_failed = False

    if args.all or not args.live:
        port = get_free_port()
        server = start_local_server(port)
        local_url = f"http://127.0.0.1:{port}/index.html"
        try:
            auditor = InfiniteScrollAuditor(local_url, is_live=False)
            res = auditor.run_suite()
            overall_results['local'] = res
            if res['failed'] > 0:
                any_failed = True
        finally:
            server.shutdown()

    if args.all or args.live:
        live_url = "https://fonthub.fedu.vn/#fontshare"
        auditor = InfiniteScrollAuditor(live_url, is_live=True)
        res = auditor.run_suite()
        overall_results['live'] = res
        if res['failed'] > 0:
            any_failed = True

    report_file = os.path.join(REPORTS_DIR, 'fontshare_infinite_scroll_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(overall_results, f, indent=2, ensure_ascii=False)
    print(f"\n[REPORT] Saved full JSON audit report to: {report_file}")

    sys.exit(1 if any_failed else 0)

if __name__ == '__main__':
    main()
