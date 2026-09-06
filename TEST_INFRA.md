# Test Infrastructure: fedu.vn/font Interactive Type Hub

## 1. Test Philosophy & Principles
The test suite for `fedu.vn/font Interactive Type Hub` is designed under the **Opaque-Box Requirement-Driven** philosophy:
- **Zero Mock Cheating**: Tests execute real validation against authoritative specifications, data models, and functional contracts. No tautological asserts or artificial passes.
- **Authoritative Expected Output**: Every assertion derives its expected outputs directly from `ORIGINAL_REQUEST.md`, `PROJECT.md`, `Font LIst - 2022.pdf`, and the verified Google Drive repository (`1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`).
- **Progressive Testability**: Tests support progressive verification — dynamically resolving target artifacts (`data/catalog.json`, `data/drive_links.json`, `index.html`) while maintaining independent reference oracles to test core algorithms (Type Tester sliders, diacritic normalizer, search indexing, drive URL generation).
- **Zero Heavy Dependencies**: Built with native modern Node.js (v26+) without requiring heavy browser binaries or complex npm installation, enabling instant sub-second CI/CD execution and local developer verification.

---

## 2. Test Architecture

```
/Users/vietmac/Documents/CODE/fedu-font/
├── TEST_INFRA.md                 # Test architecture & feature coverage inventory (this document)
├── TEST_READY.md                 # Published test execution readiness report
└── tests/
    ├── runner.js                 # Standalone master CLI test runner
    ├── lib/
    │   └── engine.js             # Core specification reference engine & validation helpers
    ├── tier1_feature_tests.js    # Tier 1: Isolated feature requirements (>=5 per feature)
    ├── tier2_boundary_tests.js   # Tier 2: Boundary, extremes & Vietnamese tone combinations
    ├── tier3_pairwise_tests.js   # Tier 3: Pairwise cross-feature interactions
    └── tier4_workload_tests.js   # Tier 4: End-to-end real-world designer workflows
```

---

## 3. Feature Inventory & Coverage Mapping

| Feature ID | Requirement Source | Description | Test Tier | Test Count | Status |
|------------|-------------------|-------------|-----------|------------|--------|
| **F01 / R1** | ORIGINAL_REQUEST.md § R1 | PDF Catalog Extraction (20 pages, 253 entries, 4 sections) | Tier 1 (F1) | 6 | Active |
| **F02 / R1** | ORIGINAL_REQUEST.md § R1 | 3D Selection Matrix (Style, Mood, Use-case) | Tier 1 (F1) | 6 | Active |
| **F03 / R1** | ORIGINAL_REQUEST.md § R1 | Typographic Anatomy & Metadata Schema | Tier 1 (F1) | 5 | Active |
| **F04 / R1** | ORIGINAL_REQUEST.md § R1 | Director Notes & Commentary Integrity | Tier 1 (F1) | 5 | Active |
| **F05 / R1** | ORIGINAL_REQUEST.md § R1 | Vietnamese Diacritic Verification (67 glyphs) | Tier 1 & 2 | 8 | Active |
| **F06 / R1** | PROJECT.md § M1 Contract | Master Catalog JSON Schema & Consistency | Tier 1 (F1) | 6 | Active |
| **F07 / R3** | ORIGINAL_REQUEST.md § R3 | Google Drive 361 Family Subfolder Structure | Tier 1 (F3) | 6 | Active |
| **F08 / R3** | ORIGINAL_REQUEST.md § R3 | 1,070 Font Files Completeness & Parity | Tier 1 (F3) | 6 | Active |
| **F09 / R3** | ORIGINAL_REQUEST.md § R3 | Public Folder Link & 1-Click Download URLs | Tier 1 (F3) | 6 | Active |
| **F10 / R3** | PROJECT.md § M2 Contract | Drive Links Synchronization to Web Cards | Tier 1 & 3 | 6 | Active |
| **F11 / R2** | ORIGINAL_REQUEST.md § R2 | Dynamic Web Font Engine & CSS FontFace | Tier 1 (F2) | 6 | Active |
| **F12 / R2** | ORIGINAL_REQUEST.md § R2 | Real-time Vietnamese Input Tester Binding | Tier 1 & 2 | 6 | Active |
| **F13 / R2** | ORIGINAL_REQUEST.md § R2 | Fluid Sliders (Size 14-140px, Kerning, Line-height) | Tier 1 & 2 | 8 | Active |
| **F14 / R2** | ORIGINAL_REQUEST.md § R2 | Tri-Theme Visual Modes (Dark, Light, Neon) | Tier 1 & 3 | 5 | Active |
| **F15 / R2** | ORIGINAL_REQUEST.md § R2 | Weight Explorer & Glyphs | Tier 1 (F2) | 5 | Active |
| **F16 / R4** | ORIGINAL_REQUEST.md § R4 | Instant Diacritic-Insensitive Search (<4ms) | Tier 1 (F4) | 6 | Active |
| **F17 / R4** | ORIGINAL_REQUEST.md § R4 | Multi-Dimensional Filtering (Category, Mood, Weight) | Tier 1 (F4) | 6 | Active |
| **F18 / R4** | ORIGINAL_REQUEST.md § R4 | Responsive Static Web Layout Structure | Tier 1 & 4 | 5 | Active |
| **F19 / R3&R4**| ORIGINAL_REQUEST.md § R3/R4 | 1-Click Family Download Web Button Navigation | Tier 1 & 4 | 5 | Active |
| **F20** | E2E Testing Protocol | 4-Tier Standalone Test Suite & Test Runner | Meta-Test | 1 | Active |

---

## 4. Test Tier Breakdown & Methodology

### Tier 1: Feature Coverage (Isolation)
Tests each core requirement independently against authoritative specifications:
- **T1.F1: Catalog & Schema (R1)**:
  - Verifies presence of all 4 core groups (Serif, Sans Serif, Monospace/Script/Blackletter, Vintage Sài Gòn).
  - Validates 3D Matrix dimensions (Visual Style: 14 categories; Mood: 5 profiles; Application: Display vs Body).
  - Asserts typographic anatomy fields: contrast, axis, x_height, aperture.
  - Verifies presence of director commentary notes.
  - Verifies Vietnamese support status and sample text.
  - Verifies JSON structure compliance with PROJECT.md schema.
- **T1.F2: Type Tester Engine (R2)**:
  - Font size clamping logic (min 14px, max 140px).
  - Line-height range and step validation (0.8 to 2.4).
  - Letter-spacing/kerning metric validation (-0.05em to +0.3em).
  - FontFace CSS `@font-face` declaration generation for WOFF2.
  - Reactive text transformation (uppercase, lowercase, original).
  - Weight switching model across available variants.
- **T1.F3: Google Drive 361 Family Packaging (R3)**:
  - File count verification: exactly 1,070 font files mapped without duplicates or orphans.
  - Family count verification: exactly 361 families (139 multi-file, 222 single-file).
  - Valid Google Drive folder URL generation (`https://drive.google.com/drive/folders/<id>?usp=sharing`).
  - Family naming canonicalization (stripping weight tokens, prefixing `SVN-`).
  - Folder file distribution consistency.
- **T1.F4: Search & Multi-Filtering (R4)**:
  - Instant search across font names, designer/foundry, and director notes.
  - Diacritic-insensitive matching (e.g. `tuyen ngon` matches `Tuyên ngôn`).
  - Visual category filtering.
  - Mood & vibe filtering (e.g. `Luxury & Sang trọng`, `Tech & Công nghệ`).
  - Use-case filtering (`Display / Headline`, `Body text`).
  - Combined intersection filtering.

### Tier 2: Boundary, Extreme & Vietnamese Diacritic Cases
- **Boundary Metrics**:
  - Size boundary tests at 14px and 140px; out-of-bound inputs clamped to valid ranges.
  - Kerning boundary tests at -0.05em and +0.3em.
  - Line-height boundary tests at 0.8 and 2.4.
- **Vietnamese Complex Diacritics**:
  - Compound accents and tone marks: `nghiêng`, `khuyến`, `thưởng`, `truyền`, `hoằng`, `quế`.
  - Uppercase complex diacritics: `THƯỞNG`, `NGHIÊNG`, `KHUYẾN`, `ĐỒ HỌA`.
  - Unicode normalization: NFC vs NFD equivalence handling.
- **Input Edge Cases**:
  - Empty query strings, whitespace-only strings ("   ").
  - Special characters and symbols (`#`, `@`, `%`, `&`, `!`, `<script>`).
  - Non-existent category or mood filters gracefully yielding empty list (`[]`).
  - Missing or optional fields gracefully handled without runtime exceptions.

### Tier 3: Cross-Feature Interactions (Pairwise Combinations)
Tests the interaction between multiple independent features when active simultaneously:
- **Search + Category Filter + Mood Filter**: Verifies accurate compound intersection filtering.
- **Type Tester Text Input + Theme Switch + Font Sizing**: Verifies style rule synchronization when theme is updated while typing and resizing.
- **Search Term + Empty Category Intersection**: Verifies graceful zero-match state display.
- **Category Filter + 1-Click Drive Link Resolution**: Verifies that filtered results maintain valid Google Drive download URLs.
- **Vietnamese Support Filter + Display Use-Case**: Verifies subsetting of fonts matching both display context and confirmed Vietnamese diacritic support.
- **Weight Switcher + FontFace Generator + Kerning Slider**: Verifies weight changes update font-weight rule while preserving active letter spacing.

### Tier 4: Real-World Designer Application Scenarios
Simulates realistic end-to-end workflows of designers and learners:
- **Scenario S1: Editorial Fashion Layout**: Designer searches for a Luxury Serif font, verifies Vietnamese support, tests custom headline with Vietnamese accents, adjusts font size to 54px, switches to Dark Mode, and retrieves the Google Drive zip link.
- **Scenario S2: Cyberpunk / Tech Landing Page**: Developer filters by Sans Serif and Tech mood, switches to Neon Accent theme, inputs uppercase tech slogan, increases kerning to +0.08em, and verifies FontFace CSS rule.
- **Scenario S3: YouTube Video Creator / Thumbnail Hook**: Creator seeks a Vintage Sài Gòn sign font for a video thumbnail, enters title "SÀI GÒN XƯA 1975", verifies diacritic rendering, sets size 96px, line-height 0.9, and verifies family download availability.
- **Scenario S4: Bulk Resource Download**: Student navigates directly to SVN-Integral CF family card, verifies 6 family weights are listed, confirms 1-click download button links to verified public Google Drive folder.
- **Scenario S5: Graceful Degradation & Network Fallback**: When web font CDN is unreachable, verifies typography engine applies appropriate system font fallbacks (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`) without breaking UI layout.

---

## 5. Test Runner & CLI Execution

### Command
```bash
# Run all tiers (Tier 1 to Tier 4)
node tests/runner.js

# Run specific tier
node tests/runner.js --tier=1
node tests/runner.js --tier=2
node tests/runner.js --tier=3
node tests/runner.js --tier=4

# Run with verbose logs
node tests/runner.js --verbose
```

### Exit Codes
- `0`: All tests passed successfully.
- `1`: One or more test assertions failed.
- `2`: Fatal error (missing test dependencies or unhandled rejection).
