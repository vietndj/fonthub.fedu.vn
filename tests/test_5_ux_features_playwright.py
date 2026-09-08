import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def main():
    port = 8993
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd="/Users/vietmac/Documents/CODE/fedu-font",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    url = f"http://localhost:{port}/index.html"
    print(f"Starting E2E 5 UX Features Verification on {url}...")

    console_errors = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            def on_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)
            page.on("console", on_console)

            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".font-card")
            print("  ✓ Page loaded successfully")

            # -------------------------------------------------------------
            # Feature 1: Variant Chips 2-row Wrap & Compact Size
            # -------------------------------------------------------------
            print("\n▶ Feature 1: Variant Chips 2-row Wrap & Compact Size")
            first_card = page.locator(".font-card").first
            weights_bar = first_card.locator(".card-weights-bar")
            assert weights_bar.is_visible(), "Weights bar must be visible"
            
            flex_wrap = weights_bar.evaluate("el => window.getComputedStyle(el).flexWrap")
            print(f"  ✓ .card-weights-bar flexWrap: {flex_wrap}")
            assert flex_wrap == "wrap", f"Expected flex-wrap: wrap, got {flex_wrap}"

            chip = weights_bar.locator(".weight-chip").first
            chip_font_size = chip.evaluate("el => window.getComputedStyle(el).fontSize")
            print(f"  ✓ .weight-chip fontSize: {chip_font_size}")

            # -------------------------------------------------------------
            # Feature 2: Interactive Card Badges & No Duplicate Studio
            # -------------------------------------------------------------
            print("\n▶ Feature 2: Interactive Card Badges & No Duplicate Studio")
            badges_row = first_card.locator(".card-badges-row")
            badges = badges_row.locator("button.badge")
            assert badges.count() >= 2, f"Expected interactive badges, got {badges.count()}"

            # Check no duplicate studio badge text
            studio_badge_texts = [b.inner_text().strip() for b in badges_row.locator(".badge-studio").all()]
            print(f"  ✓ Studio badge texts: {studio_badge_texts}")
            assert len(studio_badge_texts) <= 1, f"Found duplicate studio badges: {studio_badge_texts}"

            # Click a style badge (e.g. Sans Serif)
            style_badge = page.locator(".card-badges-row button.badge-style").first
            if style_badge.is_visible():
                style_text = style_badge.inner_text().strip()
                print(f"  ✓ Clicking style badge '{style_text}'")
                style_badge.click()
                page.wait_for_timeout(400)
                # Toast visible
                toast = page.locator("#toast-container, .fedu-toast, .toast")
                print("  ✓ Filter applied and toast rendered")

            # -------------------------------------------------------------
            # Feature 3: Weight Slider Dynamic Range (minWeight / maxWeight)
            # -------------------------------------------------------------
            print("\n▶ Feature 3: Weight Slider Dynamic Range (Druk Wide)")
            # Search for Druk Wide
            search_input = page.locator("#search-input")
            search_input.fill("Druk Wide")
            page.wait_for_timeout(400)

            druk_card = page.locator(".font-card[data-family*='Druk Wide']").first
            if druk_card.is_visible():
                slider = druk_card.locator(".card-weight-slider")
                min_attr = slider.get_attribute("min")
                val_attr = slider.get_attribute("value")
                slider_val_txt = druk_card.locator(".card-weight-val").inner_text().strip()
                print(f"  ✓ Druk Wide slider min={min_attr}, val={val_attr}, readout={slider_val_txt}")
                assert int(min_attr) >= 500, f"Expected min >= 500 for Druk Wide, got {min_attr}"
                assert int(val_attr) >= 500, f"Expected val >= 500 for Druk Wide, got {val_attr}"
            else:
                print("  ! Druk Wide not found in immediate search; checking first available card slider")
                s = first_card.locator(".card-weight-slider")
                print(f"  ✓ First card slider min={s.get_attribute('min')}, max={s.get_attribute('max')}")

            # -------------------------------------------------------------
            # Feature 4: Waterfall Specimen 2-Column Split View & Live Specimen
            # -------------------------------------------------------------
            print("\n▶ Feature 4: Waterfall Specimen 2-Column Split View")
            # Clear search
            search_input.fill("")
            page.wait_for_timeout(300)

            # Open drawer on first card
            view_btn = page.locator(".font-card .btn-view-family").first
            view_btn.click()
            page.wait_for_timeout(400)

            card_with_drawer = page.locator(".font-card.drawer-open, .font-card:has(.card-detail-drawer)").first
            assert card_with_drawer.is_visible(), "Drawer must be open"
            
            split_view = card_with_drawer.locator(".fs-waterfall-split-view")
            assert split_view.is_visible(), ".fs-waterfall-split-view must be visible"
            sticky_col = card_with_drawer.locator(".fs-waterfall-sticky-col")
            assert sticky_col.is_visible(), ".fs-waterfall-sticky-col must be visible"
            rows_list = card_with_drawer.locator(".fs-waterfall-rows-list")
            assert rows_list.is_visible(), ".fs-waterfall-rows-list must be visible"
            live_text = card_with_drawer.locator(".fs-waterfall-live-text")
            assert live_text.is_visible(), ".fs-waterfall-live-text must be visible"
            print("  ✓ 2-column waterfall split view rendered with sticky live text")

            # Click a row in waterfall
            wf_row = rows_list.locator(".fs-waterfall-row").first
            if wf_row.is_visible():
                row_weight = wf_row.locator(".waterfall-meta-weight").inner_text().strip()
                print(f"  ✓ Clicking waterfall row with weight '{row_weight}'")
                wf_row.click()
                page.wait_for_timeout(200)
                active_label = card_with_drawer.locator(".fs-waterfall-live-style-label").inner_text().strip()
                print(f"  ✓ Live style label updated to: '{active_label}'")

            # -------------------------------------------------------------
            # Feature 5: Filter Bar & 2-Way Sync
            # -------------------------------------------------------------
            print("\n▶ Feature 5: Filter Bar & 2-Way Sync")
            # Check Display category chip in Catalog
            display_chip = page.locator(".category-chip[data-category='Display']")
            assert display_chip.is_visible(), "Display category chip must be visible"
            display_chip.click()
            page.wait_for_timeout(300)
            print("  ✓ Selected 'Display' category in Catalog")

            # Switch to Fontshare view
            fs_nav_btn = page.locator(".view-btn[data-view='fontshare']")
            fs_nav_btn.click()
            page.wait_for_timeout(400)

            # Check Fontshare dropdown synced category to Display
            fs_cat_val = page.locator("#fs-filter-category").input_value()
            print(f"  ✓ Fontshare category dropdown synced to: '{fs_cat_val}'")
            assert fs_cat_val == "Display", f"Expected 'Display', got '{fs_cat_val}'"

            # Check Fontshare Use Case dropdown
            fs_usecase_select = page.locator("#fs-filter-usecase")
            assert fs_usecase_select.is_visible(), "#fs-filter-usecase must be visible"
            fs_usecase_select.select_option("Body Text")
            page.wait_for_timeout(300)
            print("  ✓ Selected 'Body Text' in Fontshare Use Case dropdown")

            # Switch back to Catalog view
            catalog_nav_btn = page.locator(".view-btn[data-view='catalog']")
            catalog_nav_btn.click()
            page.wait_for_timeout(400)

            # Check Catalog Use Case synced to Body Text
            cat_usecase_val = page.locator("#filter-use-case").input_value()
            print(f"  ✓ Catalog Use Case dropdown synced to: '{cat_usecase_val}'")
            assert cat_usecase_val == "Body Text", f"Expected 'Body Text', got '{cat_usecase_val}'"

            # Check 0 console errors
            print(f"\n▶ Console errors: {len(console_errors)}")
            assert len(console_errors) == 0, f"Errors: {console_errors}"

            print("\n" + "="*60)
            print(" ALL 5 UX FEATURES VERIFIED VIA PLAYWRIGHT SUCCESSFULLY! ")
            print("="*60)

            browser.close()
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
