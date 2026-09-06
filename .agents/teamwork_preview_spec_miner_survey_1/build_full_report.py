# -*- coding: utf-8 -*-
import json, re, os

print("Starting generation of comprehensive survey report and JSON master catalog...")

# Let's load pages_data.json
with open('/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/pages_data.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Also load drive font files
with open('/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/gdrive_1070_fonts.txt', 'r', encoding='utf-8') as f:
    drive_files = [line.strip() for line in f if line.strip()]

def get_drive_matches(font_name):
    # Find matching font files in Google Drive
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', font_name).lower()
    matches = []
    for df in drive_files:
        clean_df = re.sub(r'[^a-zA-Z0-9]', '', df).lower()
        if clean_name in clean_df:
            matches.append(df)
    return matches

print("Helper functions ready.")
