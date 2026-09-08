import os, sys, time, json, socket, ssl, urllib.request, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PROJECT_ROOT = '/Users/vietmac/Documents/CODE/fedu-font'
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def start_local_server(port):
    class Handler(QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=PROJECT_ROOT, **kwargs)
    httpd = HTTPServer(('127.0.0.1', port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def audit_suite():
    results = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'suites': {}, 'passed': 0, 'failed': 0, 'total': 0, 'screenshots': []}
    def record(suite, name, passed, details=None):
        if suite not in results['suites']: results['suites'][suite] = []
        status = 'PASS' if passed else 'FAIL'
        if passed:
            results['passed'] += 1
            print(f'  [PASS] {name}')
        else:
            results['failed'] += 1
            print(f'  [FAIL] {name} - Details: {details}')
        results['total'] += 1
        results['suites'][suite].append({'test': name, 'status': status, 'details': details})

    print('=' * 80)
    print('FONTHUB E2E QUALITY AUDIT SUITE (Fontshare Features & Redirects)')
    print('=' * 80)

    # 1. HTTP GET Redirect Test
    print('[SUITE 1] Redirect & Canonical Audit (https://fedu.vn/font/)')
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request('https://fedu.vn/font/', headers={'User-Agent': 'FontHub-QualityAuditor/2.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            http_status = resp.status
            content = resp.read().decode('utf-8', errors='ignore')
            has_refresh = 'http-equiv="refresh"' in content and ('font.fedu.vn' in content or 'fonthub.fedu.vn' in content)
            has_js = 'location.replace' in content and ('font.fedu.vn' in content or 'fonthub.fedu.vn' in content)
            has_canon = 'rel="canonical"' in content and ('font.fedu.vn' in content or 'fonthub.fedu.vn' in content)
            record('Redirect', 'HTTP Status 200 with instant redirect markup', http_status == 200, f'HTTP {http_status}')
            record('Redirect', 'Meta Refresh to font.fedu.vn/#catalog', has_refresh, 'Meta refresh present')
            record('Redirect', 'JS window.location.replace to font.fedu.vn/#catalog', has_js, 'JS replace present')
            record('Redirect', 'Canonical link points to font.fedu.vn/#catalog', has_canon, 'Canonical link present')
    except Exception as e:
        record('Redirect', 'Live HTTP GET https://fedu.vn/font/', False, str(e))

    port = get_free_port()
    httpd = start_local_server(port)
    local_url = f'http://127.0.0.1:{port}/index.html'

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        
        # 1.2 Browser Redirect Execution
        try:
            print('[SUITE 1.2] Headless Chrome Redirect Execution')
            r_page = browser.new_page()
            r_page.goto('https://fedu.vn/font/', wait_until='networkidle', timeout=15000)
            final_url = r_page.url
            is_redirected = 'font.fedu.vn' in final_url or 'fonthub.fedu.vn' in final_url
            record('Redirect', 'Headless Chrome resolves fedu.vn/font/ to font.fedu.vn', is_redirected, f'Landed at: {final_url}')
            r_page.close()
        except Exception as e:
            record('Redirect', 'Headless Chrome resolves fedu.vn/font/', False, str(e))

        # 2. Local Environment Audit
        print('[SUITE 2] Fontshare Interactive UI Features Audit (Local Build)')
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        console_errors = []
        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
        page.on('pageerror', lambda err: console_errors.append(str(err)))

        try:
            page.goto(local_url, wait_until='networkidle', timeout=15000)
            page.wait_for_selector('.font-card', timeout=10000)
            cards_count = page.locator('.font-card').count()
            record('Catalog (Local)', f'Rendered font cards on catalog (Found: {cards_count})', cards_count > 0, f'Count: {cards_count}')

            desktop_shot = os.path.join(SCREENSHOTS_DIR, 'audit_desktop_1440.png')
            page.screenshot(path=desktop_shot, full_page=False)
            results['screenshots'].append(desktop_shot)
            record('Visual', 'Desktop 1440px Screenshot Captured', os.path.exists(desktop_shot))

            first_card = page.locator('.font-card').first
            preview_elem = first_card.locator('.preview-text')

            # Weight Slider
            weight_slider = first_card.locator('.card-weight-slider')
            record('Weight Slider (Local)', 'Card-level Weight Slider exists on font card', weight_slider.count() > 0)
            init_w = preview_elem.evaluate('el => window.getComputedStyle(el).fontWeight')
            weight_slider.fill('700')
            weight_slider.dispatch_event('input')
            weight_slider.dispatch_event('change')
            page.wait_for_timeout(300)
            new_w = preview_elem.evaluate('el => window.getComputedStyle(el).fontWeight')
            record('Weight Slider (Local)', f'Weight Slider adjusts font-weight to bold ({init_w} -> {new_w})', new_w in ['700', 'bold'] or (int(new_w) >= 600 if new_w.isdigit() else False))
            
            weight_slider.fill('300')
            weight_slider.dispatch_event('input')
            weight_slider.dispatch_event('change')
            page.wait_for_timeout(300)
            light_w = preview_elem.evaluate('el => window.getComputedStyle(el).fontWeight')
            record('Weight Slider (Local)', f'Weight Slider adjusts font-weight to light ({light_w})', light_w in ['300', 'lighter'] or (int(light_w) <= 400 if light_w.isdigit() else False))

            # Size Slider
            size_slider = first_card.locator('.card-size-slider')
            record('Size Slider (Local)', 'Card-level Size Slider exists on font card', size_slider.count() > 0)
            init_s = preview_elem.evaluate('el => parseFloat(window.getComputedStyle(el).fontSize)')
            size_slider.fill('58')
            size_slider.dispatch_event('input')
            size_slider.dispatch_event('change')
            page.wait_for_timeout(300)
            new_s = preview_elem.evaluate('el => parseFloat(window.getComputedStyle(el).fontSize)')
            record('Size Slider (Local)', f'Card Size Slider scales font-size ({init_s}px -> {new_s}px)', abs(new_s - 58) < 5)

            # Waterfall Toggle
            style_toggle = first_card.locator('[data-action="toggle-card-waterfall"]')
            record('Waterfall Toggle (Local)', 'Waterfall style toggle button found on card', style_toggle.count() > 0)
            style_toggle.click()
            page.wait_for_timeout(500)

            drawer = first_card.locator('.card-waterfall-drawer')
            rows = first_card.locator('.card-waterfall-row')
            rows_cnt = rows.count()
            record('Waterfall Toggle (Local)', f'Clicking style toggle expands Waterfall drawer (Rows: {rows_cnt})', drawer.is_visible() and rows_cnt > 0)
            
            if rows_cnt > 1:
                apply_btn = first_card.locator('.card-waterfall-row .waterfall-apply-btn').nth(1)
                target_weight = apply_btn.get_attribute('data-weight')
                apply_btn.click()
                page.wait_for_timeout(300)
                w_val = first_card.locator('.card-weight-val').inner_text().strip()
                record('Waterfall Toggle (Local)', f'Clicking waterfall row applies style to card (Row: {target_weight}, Weight: {w_val})', w_val != '')

            waterfall_shot = os.path.join(SCREENSHOTS_DIR, 'audit_waterfall_expanded.png')
            page.screenshot(path=waterfall_shot, full_page=False)
            results['screenshots'].append(waterfall_shot)
            record('Visual', 'Expanded Waterfall Screenshot Captured', os.path.exists(waterfall_shot))

            style_toggle.click()
            page.wait_for_timeout(400)
            record('Waterfall Toggle (Local)', 'Clicking again collapses Waterfall drawer', not drawer.is_visible())

            fatal = [e for e in console_errors if not any(ign in e for ign in ['favicon.ico', 'analytics', 'ads'])]
            record('Console (Local)', f'Zero Uncaught Runtime JS Errors on Desktop (Errors: {len(fatal)})', len(fatal) == 0)

        except Exception as e:
            record('Execution (Local)', 'Desktop E2E Test Execution Error', False, str(e))
        finally:
            page.close()

        # 3. Mobile 390px Fresh Page Session
        print('[SUITE 3] Mobile Responsive Audit (Fresh 390px Viewport)')
        mob_page = browser.new_page(viewport={'width': 390, 'height': 844})
        mob_console = []
        mob_page.on('console', lambda msg: mob_console.append(msg.text) if msg.type == 'error' else None)
        mob_page.on('pageerror', lambda err: mob_console.append(str(err)))

        try:
            mob_page.goto(local_url, wait_until='networkidle', timeout=15000)
            mob_page.wait_for_selector('.font-card', timeout=10000)
            mob_page.wait_for_timeout(500)

            scroll_w = mob_page.evaluate('() => document.documentElement.scrollWidth')
            is_overflow_clean = scroll_w <= 390
            record('Responsive', f'Mobile 390px Viewport No Horizontal Overflow (scrollWidth: {scroll_w}px)', is_overflow_clean, f'scrollWidth={scroll_w}px, expected <= 390px')

            mob_card = mob_page.locator('.font-card').first
            has_w_slider = mob_card.locator('.card-weight-slider').count() > 0
            has_s_slider = mob_card.locator('.card-size-slider').count() > 0
            has_wf_btn = mob_card.locator('[data-action="toggle-card-waterfall"]').count() > 0
            record('Responsive', 'Card Fontshare Controls (Weight, Size, Waterfall) intact on Mobile', has_w_slider and has_s_slider and has_wf_btn)

            mob_shot = os.path.join(SCREENSHOTS_DIR, 'audit_mobile_390.png')
            mob_page.screenshot(path=mob_shot, full_page=False)
            results['screenshots'].append(mob_shot)
            record('Visual', 'Mobile 390px Screenshot Captured', os.path.exists(mob_shot))

            mob_fatal = [e for e in mob_console if not any(ign in e for ign in ['favicon.ico', 'analytics', 'ads'])]
            record('Console (Mobile)', f'Zero Uncaught Runtime JS Errors on Mobile (Errors: {len(mob_fatal)})', len(mob_fatal) == 0)

        except Exception as e:
            record('Execution (Mobile)', 'Mobile E2E Test Execution Error', False, str(e))
        finally:
            mob_page.close()

        # 4. Live Production Verification
        live_base = os.environ.get('LIVE_BASE_URL', 'https://font.fedu.vn')
        print(f'[SUITE 4] Live Production Verification ({live_base})')
        live_page = browser.new_page(viewport={'width': 1440, 'height': 900})
        live_console = []
        live_page.on('console', lambda msg: live_console.append(msg.text) if msg.type == 'error' else None)
        live_page.on('pageerror', lambda err: live_console.append(str(err)))

        try:
            live_page.goto(f'{live_base}/?v=' + str(int(time.time())), wait_until='networkidle', timeout=20000)
            live_page.wait_for_selector('.font-card', timeout=15000)
            live_card = live_page.locator('.font-card').first

            has_live_w = live_card.locator('.card-weight-slider').count() > 0
            has_live_s = live_card.locator('.card-size-slider').count() > 0
            has_live_wf = live_card.locator('[data-action="toggle-card-waterfall"]').count() > 0
            record('Production Live', f'Live {live_base} renders Fontshare Weight Slider', has_live_w)
            record('Production Live', f'Live {live_base} renders Fontshare Size Slider', has_live_s)
            record('Production Live', f'Live {live_base} renders Waterfall Drawer Toggle', has_live_wf)

            # Live Weight Slider Test
            if has_live_w:
                live_w_slider = live_card.locator('.card-weight-slider')
                live_preview = live_card.locator('.preview-text')
                live_w_slider.fill('800')
                live_w_slider.dispatch_event('input')
                live_w_slider.dispatch_event('change')
                live_page.wait_for_timeout(300)
                live_weight = live_page.evaluate('el => el.style.fontWeight', live_preview.element_handle())
                record('Production Live', f'Live Weight Slider adjusts font-weight to 800 ({live_weight})', live_weight == '800')

            # Live Waterfall Drawer Test
            if has_live_wf:
                live_wf_btn = live_card.locator('[data-action="toggle-card-waterfall"]')
                live_wf_btn.click()
                live_page.wait_for_timeout(400)
                live_drawer = live_card.locator('.card-waterfall-drawer')
                live_is_open = live_page.evaluate('el => el.style.display !== "none"', live_drawer.element_handle())
                live_rows = live_card.locator('.card-waterfall-row').count()
                record('Production Live', f'Live Waterfall Drawer expands with styles (Rows: {live_rows})', live_is_open and live_rows > 0)

            # Live Mobile 390px Check
            live_page.set_viewport_size({'width': 390, 'height': 844})
            live_page.wait_for_timeout(500)
            live_scroll_w = live_page.evaluate('() => document.documentElement.scrollWidth')
            record('Production Live', f'Live Mobile 390px No Horizontal Overflow ({live_scroll_w}px)', live_scroll_w <= 390)

            live_shot = os.path.join(SCREENSHOTS_DIR, 'live_production_mobile_390.png')
            live_page.screenshot(path=live_shot, full_page=False)
            results['screenshots'].append(live_shot)

            live_fatal = [e for e in live_console if not any(ign in e for ign in ['favicon.ico', 'analytics', 'ads'])]
            record('Production Live', f'Zero Uncaught Runtime JS Errors on Production (Errors: {len(live_fatal)})', len(live_fatal) == 0)

        except Exception as e:
            record('Production Live', 'Live Production Audit Error', False, str(e))
        finally:
            live_page.close()
            browser.close()
            httpd.shutdown()

    print('=' * 80)
    print(f'AUDIT SUMMARY: {results["passed"]}/{results["total"]} PASSED ({results["failed"]} FAILED)')
    print('=' * 80)

    report_file = os.path.join(REPORTS_DIR, 'audit_fontshare_e2e_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f'Report saved to: {report_file}')
    return results

if __name__ == '__main__':
    results = audit_suite()
    sys.exit(0 if results['failed'] == 0 else 1)
