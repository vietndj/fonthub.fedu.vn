# -*- coding: utf-8 -*-
import json, os

print("Generating fedu_font_catalog_master.json and report.md...")

# We will read gdrive_1070_fonts.txt
with open('/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/gdrive_1070_fonts.txt', 'r', encoding='utf-8') as f:
    drive_list = [l.strip() for l in f if l.strip()]

print(f"Loaded {len(drive_list)} drive files.")
