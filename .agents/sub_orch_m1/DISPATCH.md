# Task Assignment: Sub-Orchestrator for Milestone 1 (Catalog & 3D Matrix Synthesis)

- **Role**: Sub-Orchestrator (M1: `m1_catalog_matrix`)
- **Assigned Directory**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/sub_orch_m1`
- **Mandatory Reading**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (MANDATORY: read first)
- **Scope Reference**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
- **Survey Artifacts to Integrate**:
  1. `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/fedu_font_catalog_master.json` (253 PDF fonts, 4 core groups, 3D matrix tags, anatomy)
  2. `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json` (361 families, 1,070 Drive files)
  3. `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_3/report.md` (Local font inventory & WOFF2 metrics)

## Milestone Objective
Implement the complete, authoritative `data/catalog.json` database and its build script `scripts/build_catalog.py`:
1. Merge the 253 curated PDF fonts with the 361 Google Drive families and 1,046 local font files.
2. Populate the 3D Selection Matrix for every single family:
   - Visual Style: Serif, Sans Serif, Monospace, Script, Vintage
   - Brand Mood/Vibe: Luxury & Sang trọng, Tech & Công nghệ, Bold & Tuyên ngôn, Friendly & Nhân văn, Nostalgic & Cổ điển
   - Application Context: Display / Headline vs Body Text
3. Ensure every entry contains: ID, Name, Family, Designer, Subcategory, Anatomy (Contrast, Axis, X-height, Aperture), Vietnamese Support status, Director Notes, Weights, Sample Text, and Web Font URL placeholders.
4. Execute `scripts/build_catalog.py` to output valid, formatted `/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json`.
5. Run full Explorer -> Worker -> Reviewer -> Challenger -> Auditor verification cycle.
