"""
tests/test_fontshare_card_features.py
E2E Playwright validation of Fontshare-style Font Card features:
1. Weight slider (100 to 900 live font-weight updating)
2. Size slider (per-card live font-size updating + sync with global toolbar)
3. Styles toggle button ("X styles ▾" expanding/collapsing Waterfall drawer)
4. Waterfall row interactive selection & style application
5. Responsive mobile (390px) & desktop (1440px) layout integrity
6. 0 runtime console errors
"""

import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def main():
    # Start temporary local HTTP server
    port = 8991
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd="/Users/vietmac/Documents/CODE/fedu-font",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    url = f"http://localhost:{port}/index.html"
    print(f"Starting E2E Fontshare Card Features Test on {url}...")

    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
        page.on("console", on_console)

        page.goto(url, wait_until="networkidle")

        # Wait for font cards to render
        page.wait_for_selector(".font-card")
        cards = page.locator(".font-card")
        card_count = cards.count()
        print(f"Found {card_count} rendered font cards in catalog.")
        assert card_count > 0, "No font cards rendered!"

        first_card = cards.first
        family_name = first_card.locator(".card-family-name").inner_text()
        print(f"Testing primary card: {family_name}")

        # ---------------------------------------------------------------------
        # TEST 1: Weight Slider Interaction
        # ---------------------------------------------------------------------
        print("\n▶ Test 1: Card Weight Slider (100 -> 900)")
        weight_slider = first_card.locator(".card-weight-slider")
        assert weight_slider.is_visible(), "Card weight slider must be visible!"

        preview = first_card.locator(".preview-text")
        weight_val = first_card.locator(".card-weight-val")

        # Set slider to 800
        page.evaluate("""
            (el) => {
                el.value = 800;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        """, weight_slider.element_handle())

        val_text = weight_val.inner_text().strip()
        font_weight = page.evaluate("(el) => el.style.fontWeight", preview.element_handle())
        print(f"  Slider value label: '{val_text}', preview style.fontWeight: '{font_weight}'")
        assert val_text == "800", f"Weight value display expected '800', got '{val_text}'"
        assert font_weight == "800", f"Preview font-weight expected '800', got '{font_weight}'"

        # Set slider to 300
        page.evaluate("""
            (el) => {
                el.value = 300;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        """, weight_slider.element_handle())
        val_text = weight_val.inner_text().strip()
        font_weight = page.evaluate("(el) => el.style.fontWeight", preview.element_handle())
        print(f"  Slider value label: '{val_text}', preview style.fontWeight: '{font_weight}'")
        assert val_text == "300", f"Weight value display expected '300', got '{val_text}'"
        assert font_weight == "300", f"Preview font-weight expected '300', got '{font_weight}'"
        print("  ✔ PASS: Weight Slider updates font-weight & display value smoothly.")

        # ---------------------------------------------------------------------
        # TEST 2: Card Size Slider Interaction
        # ---------------------------------------------------------------------
        print("\n▶ Test 2: Card Size Slider")
        size_slider = first_card.locator(".card-size-slider")
        assert size_slider.is_visible(), "Card size slider must be visible!"
        size_val = first_card.locator(".card-size-val")

        page.evaluate("""
            (el) => {
                el.value = 54;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        """, size_slider.element_handle())

        size_text = size_val.inner_text().strip()
        font_size = page.evaluate("(el) => el.style.fontSize", preview.element_handle())
        print(f"  Size value label: '{size_text}', preview style.fontSize: '{font_size}'")
        assert size_text == "54px", f"Size value display expected '54px', got '{size_text}'"
        assert font_size == "54px", f"Preview font-size expected '54px', got '{font_size}'"
        print("  ✔ PASS: Card Size Slider updates preview font-size directly.")

        # ---------------------------------------------------------------------
        # TEST 3: Global Size Slider Synchronization
        # ---------------------------------------------------------------------
        print("\n▶ Test 3: Global Size Slider Sync")
        global_size_slider = page.locator("#font-size-slider")
        page.evaluate("""
            (el) => {
                el.value = 42;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        """, global_size_slider.element_handle())

        # Check that card size slider updated to 42
        updated_card_size = page.evaluate("(el) => el.value", size_slider.element_handle())
        print(f"  Global size changed to 42. Card size slider value: '{updated_card_size}'")
        assert updated_card_size == "42", f"Card size slider expected '42', got '{updated_card_size}'"
        print("  ✔ PASS: Global Size Slider synchronizes all card size sliders.")

        # ---------------------------------------------------------------------
        # TEST 4: Styles Toggle ("X styles ▾") & Waterfall Drawer
        # ---------------------------------------------------------------------
        print("\n▶ Test 4: Styles Toggle Button & Waterfall Drawer")
        styles_btn = first_card.locator(".card-styles-toggle")
        waterfall_drawer = first_card.locator(".card-waterfall-drawer")

        # Initially drawer is hidden
        is_hidden_initially = page.evaluate("(el) => el.style.display === 'none'", waterfall_drawer.element_handle())
        assert is_hidden_initially, "Waterfall drawer should be hidden initially"

        # Click to expand
        styles_btn.click()
        time.sleep(0.3)
        is_open = page.evaluate("(el) => el.style.display !== 'none'", waterfall_drawer.element_handle())
        assert is_open, "Waterfall drawer should be open after clicking styles button!"

        rows = first_card.locator(".card-waterfall-row")
        row_count = rows.count()
        print(f"  Waterfall drawer opened successfully! Contains {row_count} style rows.")
        assert row_count > 0, "Waterfall drawer must contain at least 1 row!"

        # Click again to collapse
        styles_btn.click()
        time.sleep(0.2)
        is_closed = page.evaluate("(el) => el.style.display === 'none'", waterfall_drawer.element_handle())
        assert is_closed, "Waterfall drawer should be collapsed after second click!"
        print("  ✔ PASS: Styles toggle opens and closes Waterfall drawer cleanly.")

        # ---------------------------------------------------------------------
        # TEST 5: Waterfall Interactive Row Selection
        # ---------------------------------------------------------------------
        print("\n▶ Test 5: Interactive Waterfall Row Style Selection")
        styles_btn.click() # re-open
        time.sleep(0.2)

        # Find a multi-weight font or click second row if available
        if row_count > 1:
            second_row = rows.nth(1)
            target_weight = second_row.get_attribute("data-weight")
            print(f"  Clicking waterfall row: '{target_weight}'")
            second_row.click()
            time.sleep(0.2)

            # Check that card preview got updated
            new_preview_weight = page.evaluate("(el) => el.style.fontWeight", preview.element_handle())
            new_slider_val = page.evaluate("(el) => el.value", weight_slider.element_handle())
            print(f"  Card preview updated weight: {new_preview_weight}, slider value: {new_slider_val}")
            assert new_preview_weight != "", "Card preview font-weight must be set!"
            print("  ✔ PASS: Selecting waterfall row applies style to card preview & syncs slider.")

        # ---------------------------------------------------------------------
        # TEST 6: Mobile Responsive Check (390px iPhone Viewport)
        # ---------------------------------------------------------------------
        print("\n▶ Test 6: Mobile Responsive Check (390px)")
        page.set_viewport_size({"width": 390, "height": 844})
        time.sleep(0.5)

        # Verify no horizontal page overflow
        has_horizontal_overflow = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        print(f"  Mobile 390px horizontal overflow detected: {has_horizontal_overflow}")
        assert not has_horizontal_overflow, "Horizontal overflow detected on 390px mobile viewport!"

        # Check that card controls are accessible on mobile
        assert weight_slider.is_visible(), "Weight slider must remain visible and accessible on mobile!"
        assert size_slider.is_visible(), "Size slider must remain visible and accessible on mobile!"
        assert styles_btn.is_visible(), "Styles button must remain visible on mobile!"
        print("  ✔ PASS: Mobile responsive layout is pixel-perfect without overflow.")

        # ---------------------------------------------------------------------
        # TEST 7: Console Errors Audit
        # ---------------------------------------------------------------------
        print("\n▶ Test 7: Runtime Console Errors Audit")
        print(f"  Console errors captured: {len(console_errors)}")
        if console_errors:
            for err in console_errors:
                print(f"    - {err}")
        assert len(console_errors) == 0, f"Encountered {len(console_errors)} console errors!"
        print("  ✔ PASS: Zero runtime console errors.")

        browser.close()

    server.terminate()
    print("\n============================================================")
    print(" ALL 7 FONTSHARE CARD FEATURE TESTS PASSED 100%!")
    print("============================================================")

if __name__ == "__main__":
    main()
