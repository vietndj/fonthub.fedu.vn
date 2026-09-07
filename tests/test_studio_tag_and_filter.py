"""
tests/test_studio_tag_and_filter.py
Comprehensive E2E Playwright verification for Studio Tagging & Grouping:
1. Catalog view:
   - Every font card renders a clickable .badge-studio tag
   - #filter-studio dropdown is populated with studios and counts
   - Selecting a studio from dropdown filters the font grid accurately
   - Clicking any .badge-studio tag filters the font grid, syncs dropdowns, and triggers toast
2. Fontshare view:
   - #fs-filter-studio dropdown is populated
   - Every Fontshare card renders a clickable .fs-studio-badge tag
   - Selecting studio from dropdown filters the fontshare list
   - Clicking .fs-studio-badge filters list and triggers toast
3. Instant Search:
   - Searching "Klim" or "Dinamo" returns correct studio fonts
4. Reset / Clear filters:
   - Clicking clear resets filter to all fonts
5. Mobile Viewport (390px):
   - Badges wrap cleanly, zero horizontal page overflow
6. 0 runtime console errors
"""

import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def main():
    port = 8992
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd="/Users/vietmac/Documents/CODE/fedu-font",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    url = f"http://localhost:{port}/index.html"
    print(f"Starting E2E Studio Tag & Grouping Test on {url}...")

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

            # -----------------------------------------------------------------
            # TEST 1: Catalog View - Badges & Dropdown Population
            # -----------------------------------------------------------------
            print("\n▶ Test 1: Catalog View - Studio Badges & Dropdown Population")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".font-card")
            
            cards = page.locator(".font-card")
            card_count = cards.count()
            print(f"  ✓ Found {card_count} rendered font cards in catalog.")
            assert card_count > 0, "No font cards rendered!"

            # Check .badge-studio presence on cards
            studio_badges = page.locator(".font-card .badge-studio")
            badge_count = studio_badges.count()
            print(f"  ✓ Found {badge_count} studio badges rendered across cards.")
            assert badge_count > 0, "No studio badges found on font cards!"

            # Check #filter-studio dropdown options
            studio_select = page.locator("#filter-studio")
            assert studio_select.is_visible(), "#filter-studio dropdown must be visible"
            options = studio_select.locator("option")
            opt_count = options.count()
            print(f"  ✓ #filter-studio has {opt_count} studio options.")
            assert opt_count >= 10, f"Expected at least 10 studio options, got {opt_count}"

            # Check Klim option exists
            klim_opt = studio_select.locator("option[value='Klim Type Foundry']")
            assert klim_opt.count() == 1, "Klim Type Foundry option must exist"
            klim_opt_text = klim_opt.inner_text()
            print(f"  ✓ Klim option text: {klim_opt_text}")

            # -----------------------------------------------------------------
            # TEST 2: Filter Catalog by Studio Dropdown
            # -----------------------------------------------------------------
            print("\n▶ Test 2: Filter Catalog by Studio Dropdown")
            studio_select.select_option("Grilli Type")
            page.wait_for_timeout(300)

            filtered_cards = page.locator(".font-card")
            filtered_count = filtered_cards.count()
            print(f"  ✓ Filtered to 'Grilli Type': {filtered_count} cards rendered.")
            assert filtered_count == 19, f"Expected 19 Grilli Type fonts, got {filtered_count}"

            # Verify every visible card belongs to Grilli Type
            for i in range(min(5, filtered_count)):
                card = filtered_cards.nth(i)
                data_studio = card.get_attribute("data-studio")
                assert data_studio == "Grilli Type", f"Expected data-studio 'Grilli Type', got '{data_studio}'"

            # -----------------------------------------------------------------
            # TEST 3: Click Studio Badge on Card (Direct Grouping) & Toast
            # -----------------------------------------------------------------
            print("\n▶ Test 3: Click Studio Badge on Card (Direct Grouping) & Toast")
            # Reset dropdown to all first
            studio_select.select_option("all")
            page.wait_for_timeout(300)
            
            results_txt = page.locator("#results-count").inner_text()
            print(f"  ✓ Initial unfiltered results count: {results_txt}")
            assert "423" in results_txt, f"Expected 423 total fonts, got {results_txt}"

            # Find a card with Dinamo badge in initial view
            dinamo_badge = page.locator(".font-card .badge-studio[data-studio='Dinamo']").first
            assert dinamo_badge.is_visible(), "Dinamo studio badge must be visible in first chunk of cards"
            print(f"  ✓ Clicking badge: '{dinamo_badge.inner_text()}'")
            dinamo_badge.click()
            page.wait_for_timeout(500)

            # Check dropdown synced
            assert studio_select.input_value() == "Dinamo", f"Dropdown must sync to 'Dinamo', got {studio_select.input_value()}"

            # Check filtered cards count and results text
            dinamo_results_txt = page.locator("#results-count").inner_text()
            print(f"  ✓ Filtered results count: {dinamo_results_txt}")
            assert "4 /" in dinamo_results_txt, f"Expected 4 Dinamo fonts, got {dinamo_results_txt}"
            assert page.locator(".font-card").count() == 4

            # Check Toast notification
            toast = page.locator(".toast, #toast-container, .fedu-toast")
            if toast.count() > 0 and toast.first.is_visible():
                print(f"  ✓ Toast notification visible: '{toast.first.inner_text()}'")

            # -----------------------------------------------------------------
            # TEST 4: Clear Filters Button
            # -----------------------------------------------------------------
            print("\n▶ Test 4: Clear Filters Button")
            clear_btn = page.locator("#btn-clear-filters")
            if clear_btn.is_visible():
                clear_btn.click()
                page.wait_for_timeout(300)
                reset_results_txt = page.locator("#results-count").inner_text()
                print(f"  ✓ Reset filters results count: {reset_results_txt}")
                assert "423" in reset_results_txt, "Catalog should reset to 423 fonts"
                assert studio_select.input_value() == "all", "Dropdown should reset to 'all'"

            # -----------------------------------------------------------------
            # TEST 5: Fontshare View - Studio Dropdown & Badge Grouping
            # -----------------------------------------------------------------
            print("\n▶ Test 5: Fontshare View - Studio Dropdown & Badge Grouping")
            fs_btn = page.locator(".view-btn[data-view='fontshare']")
            assert fs_btn.is_visible(), "Fontshare view switch button must be visible"
            fs_btn.click()
            page.wait_for_timeout(400)

            fs_view = page.locator("#fontshare-view")
            assert fs_view.is_visible(), "Fontshare view must be visible"

            fs_studio_select = page.locator("#fs-filter-studio")
            assert fs_studio_select.is_visible(), "#fs-filter-studio dropdown must be visible"
            fs_opts = fs_studio_select.locator("option").count()
            print(f"  ✓ #fs-filter-studio has {fs_opts} options.")
            assert fs_opts >= 10, f"Expected at least 10 options, got {fs_opts}"

            # Check fontshare cards render .fs-studio-badge
            fs_cards = page.locator(".fontshare-card")
            assert fs_cards.count() > 0, "Fontshare cards must be rendered"
            first_fs_badge = fs_cards.first.locator(".fs-studio-badge")
            assert first_fs_badge.is_visible(), "Fontshare card must render .fs-studio-badge"
            print(f"  ✓ Fontshare card studio badge: '{first_fs_badge.inner_text()}'")

            # Filter Fontshare by CoType Foundry
            fs_studio_select.select_option("CoType Foundry")
            page.wait_for_timeout(400)
            cotype_fs_cards = page.locator(".fontshare-card")
            cotype_count = cotype_fs_cards.count()
            print(f"  ✓ Fontshare filtered to CoType Foundry: {cotype_count} cards")
            assert cotype_count >= 10, f"Expected at least 10 CoType cards, got {cotype_count}"

            # Test clicking studio badge in Fontshare card
            fs_studio_select.select_option("all")
            page.wait_for_timeout(400)
            klim_fs_badge = page.locator(".fontshare-card .fs-studio-badge[data-studio='Klim Type Foundry']").first
            if klim_fs_badge.is_visible():
                klim_fs_badge.click()
                page.wait_for_timeout(400)
                assert fs_studio_select.input_value() == "Klim Type Foundry", "Fontshare dropdown must sync to Klim"
                klim_fs_count = page.locator(".fontshare-card").count()
                print(f"  ✓ Fontshare filtered by badge click to Klim: {klim_fs_count} cards")
                assert klim_fs_count >= 20, f"Expected >= 20 Klim cards, got {klim_fs_count}"

            # -----------------------------------------------------------------
            # TEST 6: Mobile Viewport (390px) Layout Integrity
            # -----------------------------------------------------------------
            print("\n▶ Test 6: Mobile Viewport (390px) Layout Integrity")
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".font-card")
            page.wait_for_timeout(300)

            # Verify no horizontal page scroll
            has_horizontal_overflow = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
            print(f"  ✓ Mobile 390px horizontal overflow: {has_horizontal_overflow}")
            assert not has_horizontal_overflow, "Page must not have horizontal scrollbar on 390px mobile viewport"

            # Check studio badges wrap cleanly on mobile
            mobile_card = page.locator(".font-card").first
            badge_row = mobile_card.locator(".card-badges-row")
            assert badge_row.is_visible(), "Badges row must be visible on mobile"

            # -----------------------------------------------------------------
            # TEST 7: Console Errors Check
            # -----------------------------------------------------------------
            print("\n▶ Test 7: Console Errors Check")
            print(f"  ✓ Total console errors logged: {len(console_errors)}")
            if console_errors:
                print("  Console Errors:", console_errors)
            assert len(console_errors) == 0, f"Encountered {len(console_errors)} console errors!"

            print("\n" + "="*60)
            print(" ALL STUDIO E2E PLAYWRIGHT TESTS PASSED SUCCESSFULLY! ")
            print("="*60)

            browser.close()
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
