# Task Assignment: E2E Test Writer (Dual Track Test Suite)

- **Role**: E2E Test Suite Creator (`teamwork_preview_test_writer`)
- **Assigned Directory**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_test_writer_e2e_1`
- **Mandatory Reading**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (MANDATORY: read first)
- **Scope Reference**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
- **Exclusive Write Ownership**:
  - `/Users/vietmac/Documents/CODE/fedu-font/tests/`
  - `/Users/vietmac/Documents/CODE/fedu-font/TEST_INFRA.md`
  - Subagent working directory: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_test_writer_e2e_1/`

## Mandatory Integrity Warning
DO NOT CHEAT. All tests must be authentic and genuinely verify requirements. DO NOT hardcode mock passes or create dummy verifications. Integrity violations WILL be detected and rejected.

## Objectives
Derive a comprehensive, opaque-box, requirement-driven test suite from `ORIGINAL_REQUEST.md`:
1. Document `TEST_INFRA.md` at project root using the standard test infrastructure template (Feature inventory, Test runner command, Methodology, Coverage goals).
2. Implement executable test scripts in `/Users/vietmac/Documents/CODE/fedu-font/tests/`:
   - `tests/runner.js` or `tests/run_e2e_tests.py`: Standalone test runner with clean console output and exit code 0 on pass.
   - **Tier 1 - Feature Coverage (>=5 per feature)**:
     - F1: PDF Catalog & 3D Matrix Schema verification (>=5 tests)
     - F2: Type Tester dynamic font rendering & slider metrics (>=5 tests)
     - F3: Google Drive 361 family folder packaging & link validation (>=5 tests)
     - F4: Instant search & multi-filtering logic (>=5 tests)
   - **Tier 2 - Boundary & Corner Cases (>=5 per feature)**:
     - Boundary font sizes (14px, 140px, negative kerning)
     - Complex Vietnamese tone combinations (`nghiêng`, `khuyến`, `thưởng`, `truyền`)
     - Empty query strings, non-existent filter tags, unicode normalization
   - **Tier 3 - Cross-Feature Combinations (Pairwise)**:
     - Search term + Category filter + Mood filter interaction
     - Type Tester text change + Theme change + Size slider
   - **Tier 4 - Real-World Application Scenarios (>=5 application scenarios)**:
     - S1: Student searching for Luxury Serif for editorial layout
     - S2: Designer testing Tech Sans in Neon theme with uppercase transform
     - S3: Video creator testing Vintage Sài Gòn sign font for thumbnail title
     - S4: 1-click Google Drive Family package download navigation
     - S5: Offline / local font fallback graceful degradation
3. When test suite is built and passing against initial data contracts, publish `/Users/vietmac/Documents/CODE/fedu-font/TEST_READY.md`.
4. Deliver `handoff.md` with complete test output logs.

## 2026-09-06T06:01:06Z
User Request received:
- Working directory: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_test_writer_e2e_1
- Authoritative request file: /Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md
- Project Scope: /Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md
- Assignment: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_test_writer_e2e_1/DISPATCH.md
- Exclusive Write Ownership: /Users/vietmac/Documents/CODE/fedu-font/tests/, /Users/vietmac/Documents/CODE/fedu-font/TEST_INFRA.md, /Users/vietmac/Documents/CODE/fedu-font/TEST_READY.md, working directory.
- Tasks:
  1. Create TEST_INFRA.md
  2. Build executable test suite in tests/ covering Tiers 1-4.
  3. Publish TEST_READY.md when ready.
  4. Deliver handoff.md with verification logs.
