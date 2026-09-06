# Task Assignment: Milestone 3 Worker

- **Role**: Milestone 3 Web Type Tester & UI Implementation Worker
- **Assigned Directory**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m3_1`
- **Authoritative Request File**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (MANDATORY: you MUST read this file first)
- **Project Scope**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
- **Milestone under Implementation**: M3 (`m3_web_type_tester`)

## Architectural Blueprints (MANDATORY READING)
You have three detailed technical specifications prepared by the exploration team:
1. **UI/UX & Design System**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_m3_1/report.md`
2. **Typography Engine & WOFF2**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_m3_2/report.md`
3. **Search & Filter Engine**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_m3_3/report.md`

## Exclusive Write Ownership
You have exclusive write ownership over:
- `/Users/vietmac/Documents/CODE/fedu-font/index.html`
- `/Users/vietmac/Documents/CODE/fedu-font/css/style.css`
- `/Users/vietmac/Documents/CODE/fedu-font/js/app.js`
- `/Users/vietmac/Documents/CODE/fedu-font/js/type_tester.js`
- `/Users/vietmac/Documents/CODE/fedu-font/js/catalog_loader.js`
- `/Users/vietmac/Documents/CODE/fedu-font/scripts/convert_woff2.py`
- Your working directory

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Milestone 3 Execution Steps
1. **Implement `scripts/convert_woff2.py`**:
   - Production utility using `fontTools.ttLib.woff2` and `brotli` to convert TTF/OTF fonts to WOFF2.
   - Batch conversion and metadata extraction capabilities.
2. **Implement `index.html`**:
   - Standalone zero-dependency HTML5 entry point.
   - Header with brand title "fedu.vn/font", font count metrics, theme switcher (Dark, Light, Neon), and view toggles.
   - Sticky frosted Type Tester controls toolbar:
     - Real-time text input (UTF-8 Vietnamese diacritics with `compositionstart`/`compositionend` handling).
     - Preset quotes quick selector (Pangram tiếng Việt, Tiêu đề tuyên ngôn, Đoạn văn nhận diện, v.v.).
     - Fluid sliders: Size (14px - 140px, default 36px), Line-height (0.8 - 2.4, default 1.2), Kerning (-0.05em to +0.30em, default 0em).
     - Alignment toggles (left, center, right), Text transform buttons (none, uppercase, lowercase, titlecase), Reset button.
   - Search & Faceted Filter Bar:
     - Instant search input with clear button and sub-4ms indicator.
     - Faceted filter dropdowns / chips for: 4 Core Sections, Visual Style (15 styles), Brand Mood (7 moods), Application Context (5 contexts), Weight (Single vs Family), Vietnamese Support.
     - Active filter tags and "Clear all" button.
   - Font Grid Container with progressive infinite scroll (`IntersectionObserver`, 24 cards/batch).
   - Dynamic Font Card template:
     - Family name, designer/foundry, source badges, 3D Matrix tags (Style, Mood, Use-Case).
     - In-place editable specimen preview responsive to global sliders.
     - Weight chips switcher and Vietnamese support indicator.
     - 1-click "Tải Trọn Bộ Family (.zip)" button linking to `drive_folder_url` with `target="_blank" rel="noopener noreferrer"`.
     - "Bảng Ký Tự" button opening Glyph Explorer modal.
   - Vietnamese Glyph Map Modal:
     - Full 134 Vietnamese accented characters (67 lowercase, 67 uppercase) + A-Z + 0-9 + punctuation.
     - 1-click copy-to-clipboard for each glyph and complex multi-tone diagnostic test words.
3. **Implement `css/style.css`**:
   - Grilli Type / Pangram Pangram dark-mode aesthetic (#121212 background, 1px micro-borders #282828, crisp typography).
   - Complete CSS Custom Properties for all 3 themes (`[data-theme="dark"]`, `[data-theme="light"]`, `[data-theme="neon"]`).
   - Single-variable CSS property batching (`--preview-size`, `--preview-line-height`, `--preview-letter-spacing`, `--preview-align`, `--preview-transform`) for 60 FPS slider reactivity.
   - Mobile-first responsive layout (collapsible filters, stacked toolbar, responsive cards).
4. **Implement `js/type_tester.js`**:
   - Native `FontFace` API dynamic loader with in-memory Promise deduplication (`Map`).
   - Clamping metrics logic, IME composition handling, and 5 category system fallback stacks.
   - Glyph modal population and copy logic.
5. **Implement `js/catalog_loader.js`**:
   - Asynchronous fetch and parsing of `data/catalog.json`.
   - Pre-computed `searchComposite` sub-4ms instant search engine with Unicode NFD diacritic stripping and `đ`/`Đ` mapping.
   - Multi-dimensional faceted filter engine with dynamic count badge calculation.
6. **Implement `js/app.js`**:
   - Main controller tying together catalog loader, search, filters, Type Tester, theme switcher, and progressive rendering.
7. **Verify Everything**:
   - Run `python3 scripts/validate_catalog.py`.
   - Run `node tests/runner.js` verifying 61/61 tests pass with zero regressions.
   - Verify all files are cleanly formatted, zero dependencies, valid HTML/CSS/JS.
8. Deliver `handoff.md` with complete implementation and verification details, then notify parent.

## 2026-09-06T07:18:25Z
<USER_REQUEST>
You are teamwork_preview_worker_m3_1.
Your working directory is: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m3_1
Authoritative request file: /Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md (MANDATORY: you MUST read this file first).
Project Scope: /Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md
Assignment: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m3_1/DISPATCH.md

Architectural Blueprints:
1. UI/UX: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_m3_1/report.md
2. Font Engine: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_m3_2/report.md
3. Search & Filter: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_m3_3/report.md

Exclusive Write Ownership:
- /Users/vietmac/Documents/CODE/fedu-font/index.html
- /Users/vietmac/Documents/CODE/fedu-font/css/style.css
- /Users/vietmac/Documents/CODE/fedu-font/js/app.js
- /Users/vietmac/Documents/CODE/fedu-font/js/type_tester.js
- /Users/vietmac/Documents/CODE/fedu-font/js/catalog_loader.js
- /Users/vietmac/Documents/CODE/fedu-font/scripts/convert_woff2.py
- Your working directory

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Execute Milestone 3:
1. Implement scripts/convert_woff2.py (WOFF2 font converter and metadata extractor using fontTools/brotli).
2. Implement index.html (Pure standalone zero-dependency HTML5 with Grilli/Pangram dark aesthetic, sticky frosted Type Tester toolbar, search/filters, font card grid, and 134-glyph modal).
3. Implement css/style.css (Tri-theme custom properties for Dark, Light, Neon, single-variable batching for 60 FPS sliders, responsive layouts).
4. Implement js/type_tester.js (FontFace dynamic loader with deduplication cache, metric clamping, IME composition handling, fallback stacks, glyph modal).
5. Implement js/catalog_loader.js (Async catalog fetch, sub-4ms instant search with diacritic normalization, multi-dimensional faceted filtering with dynamic counts).
6. Implement js/app.js (Main controller coordinating catalog, search, filters, Type Tester, themes, and progressive infinite scroll).
7. Run validate_catalog.py and node tests/runner.js verifying 61/61 tests pass.
8. Deliver handoff.md and notify parent upon completion.
</USER_REQUEST>
