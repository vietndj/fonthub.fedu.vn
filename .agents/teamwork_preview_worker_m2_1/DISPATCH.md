# Task Assignment: Milestone 2 Worker (Google Drive Family Packaging)

- **Role**: Milestone 2 Implementation Worker
- **Assigned Directory**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m2_1`
- **Mandatory Reading**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (MANDATORY: read first)
- **Scope Reference**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
- **Exclusive Write Ownership**:
  - `/Users/vietmac/Documents/CODE/fedu-font/scripts/organize_drive.py`
  - `/Users/vietmac/Documents/CODE/fedu-font/data/drive_links.json`
  - `/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json` (updating `drive_folder_url` fields)
  - Subagent working directory

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Milestone 2 Objectives & Requirements
1. Survey 2 Artifacts:
   - Blueprint & Script: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/proposed_organize_drive_fonts.py`
   - Mapping: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json` (361 families, 1,070 files)
   - Target Drive Folder ID: `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`
2. Implement production script `/Users/vietmac/Documents/CODE/fedu-font/scripts/organize_drive.py`:
   - Supports `--dry-run` (default) and `--execute`.
   - Uses `rclone` with remote `gdrive:` and `--drive-root-folder-id 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`.
   - Reorganizes the 1,070 files into 361 family subfolders using server-side moves (`rclone moveto` or rclone operations).
   - Generates `/Users/vietmac/Documents/CODE/fedu-font/data/drive_links.json` mapping each family name/id to its public Google Drive folder URL:
     `https://drive.google.com/drive/folders/<FOLDER_ID>?usp=sharing` (or folder path link).
   - Updates `drive_folder_url` in `/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json` so every family card has its specific public Drive URL.
3. Verification:
   - Verify that all 1,070 files are organized into their 361 family folders.
   - Verify that `data/drive_links.json` is created with 361 entries.
   - Run `python3 scripts/validate_catalog.py` to ensure catalog integrity.
   - Run `node tests/runner.js` to verify all 61 tests pass.
4. Deliver `handoff.md` with complete execution logs and verification evidence.

## 2026-09-06T06:26:10Z
You are teamwork_preview_worker_m2_1.
Your working directory is: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m2_1
Authoritative request file: /Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md (MANDATORY: you MUST read this file first).
Project Scope: /Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md
Assignment: /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_worker_m2_1/DISPATCH.md

Exclusive Write Ownership:
- /Users/vietmac/Documents/CODE/fedu-font/scripts/organize_drive.py
- /Users/vietmac/Documents/CODE/fedu-font/data/drive_links.json
- /Users/vietmac/Documents/CODE/fedu-font/data/catalog.json (sync drive links)
- Your working directory

Execute Milestone 2:
1. Implement scripts/organize_drive.py using the Survey 2 blueprint (/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/proposed_organize_drive_fonts.py and family_grouping_mapping.json).
2. Execute the organization on Google Drive folder 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao via rclone.
3. Generate data/drive_links.json and update drive_folder_url in data/catalog.json.
4. Run validate_catalog.py and node tests/runner.js to ensure 100% test pass.
5. Deliver handoff.md and notify parent upon completion.
