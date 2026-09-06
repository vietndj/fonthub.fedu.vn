# -*- coding: utf-8 -*-
import json, os, re

from make_dataset_p1 import serif_fonts
from make_dataset_p2 import serif_pages_4_5_6_7
from make_dataset_p3 import sans_fonts
from make_dataset_p4 import sans_pages_11_to_16
from make_dataset_p5 import blackletter_mono_vintage

all_fonts = serif_fonts + serif_pages_4_5_6_7 + sans_fonts + sans_pages_11_to_16 + blackletter_mono_vintage
print(f"Total fonts assembled: {len(all_fonts)}")

# Load Drive files
with open('/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/gdrive_1070_fonts.txt', 'r', encoding='utf-8') as f:
    drive_list = [l.strip() for l in f if l.strip()]

with open('make_catalog.py', 'r', encoding='utf-8') as f:
    # get_drive definition
    pass

from make_catalog import get_drive

matched_count = 0
for idx, font in enumerate(all_fonts):
    font['id'] = f"fedu-font-{idx+1:03d}-" + re.sub(r'[^a-zA-Z0-9]+', '-', font['name'].lower()).strip('-')
    matches = get_drive(font['name'])
    font['drive_files'] = matches
    if matches:
        matched_count += 1

print(f"Total matched to Drive files: {matched_count}/{len(all_fonts)}")

# Write to JSON
master_catalog = {
    "metadata": {
        "title": "FEDU Font Hub Master Catalog - Bóc Tách Toàn Diện 'Font LIst - 2022.pdf'",
        "author": "Nguyễn Đức Việt (#learnforwork, fb.com/vietndj)",
        "source_document": "/Users/vietmac/Downloads/Font LIst - 2022.pdf",
        "total_pages": 20,
        "total_font_entries": len(all_fonts),
        "unique_font_names": len(set(f['name'].lower() for f in all_fonts)),
        "core_sections": [
            "Serif",
            "Sans Serif",
            "Blackletter, Script & Monospace",
            "Việt Nam Oldstyle / Vintage Sài Gòn"
        ],
        "subcategories_count": 18,
        "google_drive_source_folder": "https://drive.google.com/drive/folders/1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao",
        "google_drive_folder_id": "1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao",
        "total_google_drive_files": len(drive_list),
        "generation_timestamp": "2026-09-06T05:58:00Z"
    },
    "matrix_rules": {
        "dimension_1_visual": [
            "Serif Oldstyle",
            "Serif Modern",
            "Serif Slab",
            "Serif Transitional",
            "Sans Humanist",
            "Sans Neo-grotesque",
            "Sans Quirky",
            "Sans Geometric",
            "Sans Rounded",
            "Sans Condensed",
            "Sans Extended",
            "Monospace",
            "Blackletter",
            "Việt Nam Vintage"
        ],
        "dimension_2_mood": [
            "Luxury & Sang trọng",
            "Tech & Công nghệ",
            "Bold & Tuyên ngôn",
            "Friendly & Nhân văn",
            "Nostalgic & Cổ điển"
        ],
        "dimension_3_application": [
            "Display / Headline",
            "Body Text",
            "Display & Body"
        ]
    },
    "fonts": all_fonts
}

with open('/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/fedu_font_catalog_master.json', 'w', encoding='utf-8') as f:
    json.dump(master_catalog, f, ensure_ascii=False, indent=2)

print("Saved fedu_font_catalog_master.json successfully.")
