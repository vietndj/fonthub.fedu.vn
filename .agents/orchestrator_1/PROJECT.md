# Project: fedu.vn/font Interactive Type Hub

## Architecture
The system is an independent, zero-dependency static web application and automated asset distribution pipeline:
- **Frontend Architecture**: Pure HTML5, CSS3, Vanilla ES6+ JavaScript (<80 KB total payload, <350ms initial load time).
- **Data Layer**: Static `data/catalog.json` containing 361 font families, 253 curated PDF entries, full 3D Selection Matrix metadata, typography anatomy, Vietnamese character support, and Google Drive family folder links.
- **Typography Engine**: Dynamic on-demand web font loading via browser `FontFace` API + WOFF2 compressed fonts served via Cloudflare R2 CDN (`pub-447bd44dfdac4938912655c855b8631c.r2.dev`) with system fallback stacks.
- **Interactive Type Tester**: Real-time rendering engine supporting custom Vietnamese input, variable font sizing (14px - 140px), line-height (0.8 - 2.4), letter-spacing/kerning (-0.05em to +0.3em), alignment, uppercase/lowercase/titlecase transforms, 3 theme modes (Dark #121212, Light #FFFFFF, Neon Accent #00FF66), weight comparison, and glyph map.
- **Search & Filtering Engine**: Instant diacritic-insensitive search (<4ms) with multi-dimensional filtering across Visual Style, Brand Mood/Vibe, Application Context, and Weight.
- **Asset Distribution**: Google Drive root folder (`1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`) organized into 361 Family subfolders with inherited public viewing/downloading permissions, linked directly on each web card.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F01 | PDF Catalog Extraction | Extract all 20 pages of Font LIst 2022.pdf (253 entries, 4 core groups) | M1 | Survey / R1 |
| F02 | 3D Selection Matrix | 3-dimensional classification: Visual Style, Brand Mood, Use-Case Context | M1 | Survey / R1 |
| F03 | Typographic Anatomy | Contrast, Axis/Tilt, X-height, Aperture, Terminals for each font entry | M1 | Survey / R1 |
| F04 | Director Notes & Commentary | Designer observations and quotes from authoritative PDF document | M1 | Survey / R1 |
| F05 | Vietnamese Diacritic Verification | Check diacritics coverage (67 lower & upper chars) for all font entries | M1 | Survey / R1 |
| F06 | Master Catalog JSON Schema | Unified data structure linking PDF catalog, 361 GDrive families, local fonts | M1 | Survey / R1 |
| F07 | Google Drive 361 Family Subfolders | Automated creation of 361 subfolders inside Drive folder 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao | M2 | Survey / R3 |
| F08 | Server-Side File Migration | Move 1,070 flat font files into corresponding 361 Family subfolders (rclone moveto) | M2 | Survey / R3 |
| F09 | Public Folder Download Links | Inherit and verify public link sharing on all 361 Family folders | M2 | Survey / R3 |
| F10 | Drive Link Synchronization | Sync generated public Drive links into catalog.json for 1-click web download | M2 | Survey / R3 |
| F11 | Dynamic Web Font Engine | Load WOFF2 fonts on demand via browser FontFace API without OS installation | M3 | Survey / R2 |
| F12 | Live Vietnamese Input Tester | Real-time interactive text input supporting all Vietnamese accents | M3 | Survey / R2 |
| F13 | Type Tester Sliders | Fluid sliders for Size (14-140px), Line-height, and Kerning/Letter-spacing | M3 | Survey / R2 |
| F14 | Tri-Theme Visual Modes | Switch between Dark Mode (#121212), Light Mode (#FFFFFF), and Neon Accent | M3 | Survey / R2 |
| F15 | Weight & Glyph Explorer | Multi-weight variation switcher and character glyph map viewer | M3 | Survey / R2 |
| F16 | Instant Diacritic Search | Sub-4ms client-side search across font names, foundries, and director notes | M3 | Survey / R4 |
| F17 | Multi-Dimensional Filtering | Faceted filters by Visual Style, Brand Mood, Use-Case, and Vietnamese Support | M3 | Survey / R4 |
| F18 | Mobile-First Responsive UI | Grilli Type / Pangram Pangram aesthetic, responsive layout, <1s load time | M3 | Survey / R4 |
| F19 | 1-Click Family Download Button | Web card action linking directly to Google Drive Family folder | M3 | Survey / R3 & R4 |
| F20 | Opaque-Box E2E Test Suite | 4-Tier requirement-driven verification suite (Tiers 1-4) + TEST_READY.md | E2E Track | E2E Protocol |
| F21 | Final E2E Test Verification | 100% pass of all E2E test tiers + Phase 2 adversarial coverage hardening | M4 | Final Milestone |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | `m1_catalog_matrix` | Synthesize unified `data/catalog.json` with 253 PDF fonts + 361 GDrive families + 3D matrix + anatomy + VN support | Survey complete | DONE (data/catalog.json, build/validate scripts, Gate PASSED) |
| M2 | `m2_drive_packaging` | Reorganize 1,070 Google Drive files into 361 Family folders via rclone, verify public download links, sync to catalog | M1 | DONE (361 folders, 1,070 files moved, data/drive_links.json, catalog.json synced, Gate PASSED) |
| M3 | `m3_web_type_tester` | Implement standalone static web app (`index.html`, `app.js`, `style.css`), FontFace engine, Type Tester, multi-filter, themes | M1 | READY_FOR_DISPATCH |
| M4 | `m4_final_verification`| Pass 100% E2E test suite (Tiers 1-4) and adversarial coverage hardening (Tier 5) | M2, M3, TEST_READY | PLANNED |
| E2E| `e2e_testing_track` | Build standalone E2E test suite (Tiers 1-4) derived from user requirements, publish TEST_READY.md | Survey complete | DONE (TEST_READY.md, TEST_INFRA.md, 61/61 tests pass) |

## Interface Contracts
### M1 (`catalog_matrix`) ↔ M2 (`drive_packaging`) & M3 (`web_type_tester`)
- Target file: `/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json`
- Schema:
  ```json
  {
    "version": "1.0.0",
    "updated_at": "ISO-8601 string",
    "summary": {
      "total_fonts": 361,
      "pdf_curated_fonts": 253,
      "drive_files_total": 1070,
      "categories_count": 14
    },
    "fonts": [
      {
        "id": "svn-integral-cf",
        "name": "SVN-Integral CF",
        "family": "SVN-Integral CF",
        "designer": "Connary Fagen",
        "source": "PDF & Drive",
        "category": "Sans Serif",
        "subcategory": "Geometric Bold / Headline",
        "matrix_3d": {
          "style": "Sans Serif",
          "mood": "Bold & Tuyên ngôn",
          "use_case": "Display / Headline"
        },
        "anatomy": {
          "contrast": "Low",
          "axis": "Vertical",
          "x_height": "High",
          "aperture": "Tight"
        },
        "vietnamese_support": true,
        "director_notes": "Font tiêu đề tuyên ngôn mạnh mẽ, chữ in hoa cực kỳ uy lực.",
        "weights": ["Regular", "Medium", "DemiBold", "Bold", "ExtraBold", "Heavy"],
        "sample_text": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
        "web_font_url": "https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts/SVN-IntegralCF-Regular.woff2",
        "drive_folder_url": "https://drive.google.com/drive/folders/...?usp=sharing",
        "files_count": 6
      }
    ]
  }
  ```

### M2 (`drive_packaging`) ↔ M1/M3 (`catalog.json`)
- Input: `family_grouping_mapping.json` (361 families, 1,070 files)
- Operations: Server-side `rclone moveto` into `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao/<Family_Name>/`
- Output: `data/drive_links.json` mapping each family to its public Google Drive folder URL:
  `https://drive.google.com/drive/folders/<FOLDER_ID>?usp=sharing`

### M3 (`web_type_tester`) ↔ User / Client
- Entry point: `index.html` (pure static, runs on any local/HTTP server)
- Performance budget: Initial bundle < 100KB, time-to-interactive < 400ms
- Themes: `data-theme="dark"` (#121212), `data-theme="light"` (#F8F9FA), `data-theme="neon"` (#0D0E15 with #00FF66 accent)
- Type Tester parameters:
  - Font size: `14px` to `140px` (default 36px)
  - Line height: `0.8` to `2.4` (default 1.2)
  - Letter spacing: `-0.05em` to `+0.3em` (default 0em)
  - Text input: UTF-8 Vietnamese diacritics realtime binding

## Code Layout
```
/Users/vietmac/Documents/CODE/fedu-font/
├── index.html                  # Standalone Web Application entry point
├── css/
│   └── style.css               # Grilli Type / Pangram Pangram dark-mode stylesheet
├── js/
│   ├── app.js                  # Main application & filter controller
│   ├── type_tester.js          # Interactive FontFace & Type Tester engine
│   └── catalog_loader.js       # JSON loader & instant search engine
├── data/
│   ├── catalog.json            # Master 3D Font Catalog database
│   └── drive_links.json        # Google Drive family folder links mapping
├── scripts/
│   ├── build_catalog.py        # Catalog synthesis & validation script
│   ├── organize_drive.py       # Google Drive 361 family packager
│   └── convert_woff2.py        # Font compression & CDN deployment utility
├── tests/                      # E2E test suite (Dual Track)
│   ├── runner.js               # Standalone test runner
│   ├── tier1_feature_tests.js  # Feature isolation tests (>=5 per feature)
│   ├── tier2_boundary_tests.js # Boundary & Vietnamese diacritic tests
│   ├── tier3_pairwise_tests.js # Cross-feature combination tests
│   └── tier4_workload_tests.js # Real-world designer workflow tests
└── .agents/                    # Agent orchestration metadata only
```
