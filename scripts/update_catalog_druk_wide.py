#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update data/catalog.json and data/fonts.json with FD Druk Wide
"""

import json
from pathlib import Path

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
CATALOG_PATH = PROJECT_ROOT / "data" / "catalog.json"
FONTS_JSON_PATH = PROJECT_ROOT / "data" / "fonts.json"
MAPPING_PATH = PROJECT_ROOT / "data" / "font_download_mapping.json"

DRUK_WIDE_META = {
    "id": "fd-druk-wide",
    "name": "FD Druk Wide",
    "family": "FD Druk Wide",
    "designer": "Berton Hasebe / FEDU Type Studio",
    "source": "Commercial Type (FEDU Vietnamese Localization)",
    "foundry": "Commercial Type",
    "category": "Sans Serif",
    "subcategory": "Sans Display Extended Ultra-Wide",
    "is_dinamo": false if False else False,
    "is_klim": False,
    "is_pangram": False,
    "tags": [
        "Commercial Type",
        "Display",
        "Extended",
        "Sans Serif",
        "Ultra Wide",
        "FEDU Type",
        "Universal Standard",
        "Vietnamese"
    ],
    "matrix_3d": {
        "style": "Sans Display Extended Ultra-Wide",
        "mood": "Massive, Bold & Tuyên ngôn",
        "use_case": "Display & Headline"
    },
    "anatomy": {
        "contrast": "Low to Medium",
        "axis": "Vertical Grotesque",
        "x_height": "High (540 UPM)",
        "aperture": "Tight / Semi-closed"
    },
    "vietnamese_support": True,
    "vietnamese_status": "Supported (100% - 134/134 glyphs)",
    "director_notes": "📌 Nguồn gốc: Commercial Type (FEDU Việt Hóa Chuẩn Typographic Engine)\n\nKiệt tác Sans-Serif mở rộng cực đại (Extended Display) của nhà thiết kế Berton Hasebe, ban đầu được đặt hàng riêng cho Bloomberg Businessweek. Druk Wide sở hữu các đường nét ngang bành trướng mãnh liệt, cấu trúc chữ nhật cô đặc, độ dày nét khổng lồ từ Medium đến Super, tạo nên uy lực thị giác choáng ngợp trên các tiêu đề báo chí, poster quảng cáo và bìa tạp chí đương đại.",
    "weights": [
        "Medium",
        "Medium Italic",
        "Bold",
        "Bold Italic",
        "Heavy",
        "Heavy Italic",
        "Super",
        "Super Italic"
    ],
    "sample_text": "BẢN LĨNH KIẾN TRÚC VÀ UY LỰC THỊ GIÁC BÀNH TRƯỚNG MÃNH LIỆT",
    "zip_filename": "FD-DrukWide.zip",
    "zip_path": "dist/zips/FD/FD-DrukWide.zip",
    "download_url": "dist/zips/FD/FD-DrukWide.zip",
    "web_font_url": "fonts/FDDrukWide-Bold.woff2",
    "director_review": "Kiệt tác Sans-Serif mở rộng cực đại (Extended Display) của nhà thiết kế Berton Hasebe, ban đầu được đặt hàng riêng cho Bloomberg Businessweek. Druk Wide sở hữu các đường nét ngang bành trướng mãnh liệt, cấu trúc chữ nhật cô đặc, độ dày nét khổng lồ từ Medium đến Super, tạo nên uy lực thị giác choáng ngợp trên các tiêu đề báo chí, poster quảng cáo và bìa tạp chí đương đại.",
    "critique": "Kiệt tác Sans-Serif mở rộng cực đại (Extended Display) của nhà thiết kế Berton Hasebe, ban đầu được đặt hàng riêng cho Bloomberg Businessweek. Druk Wide sở hữu các đường nét ngang bành trướng mãnh liệt, cấu trúc chữ nhật cô đặc, độ dày nét khổng lồ từ Medium đến Super, tạo nên uy lực thị giác choáng ngợp trên các tiêu đề báo chí, poster quảng cáo và bìa tạp chí đương đại.",
    "nhan_dinh_dao_dien": "Kiệt tác Sans-Serif mở rộng cực đại (Extended Display) của nhà thiết kế Berton Hasebe, ban đầu được đặt hàng riêng cho Bloomberg Businessweek. Druk Wide sở hữu các đường nét ngang bành trướng mãnh liệt, cấu trúc chữ nhật cô đặc, độ dày nét khổng lồ từ Medium đến Super, tạo nên uy lực thị giác choáng ngợp trên các tiêu đề báo chí, poster quảng cáo và bìa tạp chí đương đại.",
    "typography_critique": "Kiệt tác Sans-Serif mở rộng cực đại (Extended Display) của nhà thiết kế Berton Hasebe, ban đầu được đặt hàng riêng cho Bloomberg Businessweek. Druk Wide sở hữu các đường nét ngang bành trướng mãnh liệt, cấu trúc chữ nhật cô đặc, độ dày nét khổng lồ từ Medium đến Super, tạo nên uy lực thị giác choáng ngợp trên các tiêu đề báo chí, poster quảng cáo và bìa tạp chí đương đại."
}

def update_catalog():
    print("Updating catalog.json and fonts.json...")
    
    # 1. catalog.json
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    fonts_list = catalog.get('fonts', [])
    existing_idx = next((i for i, fn in enumerate(fonts_list) if fn.get('id') == DRUK_WIDE_META['id']), None)
    if existing_idx is not None:
        fonts_list[existing_idx] = DRUK_WIDE_META
        print(f"Updated existing entry in catalog.json at index {existing_idx}")
    else:
        fonts_list.insert(0, DRUK_WIDE_META)
        print(f"Inserted new entry into catalog.json (Total fonts: {len(fonts_list)})")
        
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    # 2. fonts.json
    with open(FONTS_JSON_PATH, 'r', encoding='utf-8') as f:
        fonts_json = json.load(f)
        
    if isinstance(fonts_json, list):
        f_idx = next((i for i, fn in enumerate(fonts_json) if fn.get('id') == DRUK_WIDE_META['id']), None)
        if f_idx is not None:
            fonts_json[f_idx] = DRUK_WIDE_META
            print(f"Updated existing entry in fonts.json at index {f_idx}")
        else:
            fonts_json.insert(0, DRUK_WIDE_META)
            print(f"Inserted new entry into fonts.json (Total fonts: {len(fonts_json)})")
    with open(FONTS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(fonts_json, f, indent=2, ensure_ascii=False)
        
    # 3. font_download_mapping.json
    if MAPPING_PATH.exists():
        with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        if 'fonts' in mapping and isinstance(mapping['fonts'], list):
            f_map = next((item for item in mapping['fonts'] if item.get('id') == DRUK_WIDE_META['id']), None)
            zip_p = PROJECT_ROOT / DRUK_WIDE_META['zip_path']
            size_mb = round(zip_p.stat().st_size / (1024 * 1024), 2) if zip_p.exists() else 0.64
            map_entry = {
                "index": len(mapping['fonts']) + 1,
                "id": DRUK_WIDE_META['id'],
                "name": DRUK_WIDE_META['name'],
                "zip_filename": DRUK_WIDE_META['zip_filename'],
                "size_mb": size_mb,
                "drive_view_url": "",
                "drive_download_url": DRUK_WIDE_META['download_url'],
                "status": "PASS"
            }
            if f_map is None:
                mapping['fonts'].append(map_entry)
                mapping['total_fonts'] = len(mapping['fonts'])
                with open(MAPPING_PATH, 'w', encoding='utf-8') as f:
                    json.dump(mapping, f, indent=2, ensure_ascii=False)
                print(f"Added mapping entry to font_download_mapping.json")

    print("Catalog update completed successfully!")

if __name__ == '__main__':
    update_catalog()
