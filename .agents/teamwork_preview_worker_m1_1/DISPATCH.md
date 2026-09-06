# Task Assignment: Milestone 1 Worker (Catalog & 3D Matrix Implementation)

- **Role**: Milestone 1 Implementation Worker
- **Assigned Directory**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m1_1`
- **Mandatory Reading**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (MANDATORY: read first)
- **Scope Reference**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
- **Exclusive Write Ownership**:
  - `/Users/vietmac/Documents/CODE/fedu-font/data/` (e.g. `catalog.json`)
  - `/Users/vietmac/Documents/CODE/fedu-font/scripts/` (e.g. `build_catalog.py`, `validate_catalog.py`)
  - Subagent working directory: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m1_1/`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Input Artifacts
1. Survey 1 Spec Miner JSON: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/fedu_font_catalog_master.json` (253 PDF fonts, 4 core groups, 3D matrix tags, anatomy)
2. Survey 2 Explorer Mapping: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json` (361 families, 1,070 Drive files)
3. Survey 3 Architecture Report: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_3/report.md` (Local font inventory & WOFF2 metrics)

## Milestone Deliverables & Verification
1. Create `scripts/build_catalog.py` to synthesize the master `data/catalog.json`:
   - Combine all 361 font families with the 253 curated PDF fonts and local font metrics.
   - For every font family, populate:
     - `id`, `name`, `family`, `designer`, `category`, `subcategory`
     - `matrix_3d`: `style`, `mood`, `use_case`
     - `anatomy`: `contrast`, `axis`, `x_height`, `aperture`
     - `vietnamese_support`: boolean (true for all SVN fonts)
     - `director_notes`: designer commentary from PDF / expert analysis
     - `weights`: list of available weights/styles
     - `sample_text`: representative pangram or headline text in Vietnamese
     - `drive_folder_url`: placeholder or mapped Drive link
     - `files_count`: number of font files
   - Validate that `data/catalog.json` is valid JSON, non-empty, and contains 361 font families.
2. Create and run a verification script `scripts/validate_catalog.py`:
   - Verify 100% of entries have valid 3D matrix tags, valid anatomy, weights array, and Vietnamese sample texts.
3. Deliver `handoff.md` with build/test outputs and verification evidence.

## 2026-09-06T06:01:06Z
Received prompt: Milestone 1 execution. Master catalog synthesis at data/catalog.json, scripts/build_catalog.py, scripts/validate_catalog.py.

