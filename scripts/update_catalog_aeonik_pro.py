#!/usr/bin/env python3
"""
Update data/catalog.json and data/fonts.json with the 5 newly localized Aeonik Pro families:
1. FD Aeonik Soft (16 styles)
2. FD Aeonik Condensed (16 styles)
3. FD Aeonik Extended (16 styles)
4. FD Aeonik Mono (8 styles)
5. FD Aeonik Fono (8 styles)
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
CATALOG_PATH = PROJECT_ROOT / "data" / "catalog.json"
FONTS_JSON_PATH = PROJECT_ROOT / "data" / "fonts.json"
DIST_FONTS = PROJECT_ROOT / "dist" / "fonts"
DIST_ZIPS = PROJECT_ROOT / "dist" / "zips" / "FD"

FAMILIES_META = [
    {
        "core": "Soft",
        "id": "fdaeoniksoft",
        "name": "FD Aeonik Soft",
        "family": "FD Aeonik Soft",
        "category": "Sans Serif",
        "subcategory": "Sans Rounded Geometric",
        "matrix_3d": {"style": "Sans Rounded", "mood": "Thân thiện & Công nghệ", "use_case": "Display & UI"},
        "anatomy": {"contrast": "Low", "axis": "Rounded Neo-Geometric", "x_height": "High", "aperture": "Open"},
        "director_notes": "📌 Phiên bản Soft bo tròn đỉnh nét (Rounded Neo-Grotesque) độc quyền FEDU, cân bằng giữa vẻ công nghệ sắc sảo và sự thân thiện hiện đại.",
        "sample_text": "Trải nghiệm giao diện mềm mại với đường nét hình học bo tròn tinh tế và hiện đại",
        "styles": [
            "Air", "AirItalic", "Thin", "ThinItalic", "Light", "LightItalic",
            "Regular", "RegularItalic", "Medium", "MediumItalic",
            "SemiBold", "SemiBoldItalic", "Bold", "BoldItalic", "Black", "BlackItalic"
        ]
    },
    {
        "core": "Condensed",
        "id": "fdaeonikcondensed",
        "name": "FD Aeonik Condensed",
        "family": "FD Aeonik Condensed",
        "category": "Sans Serif",
        "subcategory": "Sans Condensed Geometric",
        "matrix_3d": {"style": "Sans Condensed", "mood": "Mạnh mẽ & Hiện đại", "use_case": "Headline & Poster"},
        "anatomy": {"contrast": "Low", "axis": "Condensed Neo-Geometric", "x_height": "High", "aperture": "Compact"},
        "director_notes": "📌 Phiên bản Condensed thu hẹp bề ngang tối ưu cho tiêu đề hiển thị, poster và bảng tin công nghệ cần tiết kiệm diện tích mà vẫn giữ độ tác động thị giác mạnh mẽ.",
        "sample_text": "Tiết kiệm không gian hiển thị tối đa với cấu trúc ký tự nén chặt chẽ sắc nét",
        "styles": [
            "Air", "AirItalic", "Thin", "ThinItalic", "Light", "LightItalic",
            "Regular", "RegularItalic", "Medium", "MediumItalic",
            "SemiBold", "SemiBoldItalic", "Bold", "BoldItalic", "Black", "BlackItalic"
        ]
    },
    {
        "core": "Extended",
        "id": "fdaeonikextended",
        "name": "FD Aeonik Extended",
        "family": "FD Aeonik Extended",
        "category": "Sans Serif",
        "subcategory": "Sans Extended Geometric",
        "matrix_3d": {"style": "Sans Extended", "mood": "Đẳng cấp & Vững chãi", "use_case": "Branding & Hero Title"},
        "anatomy": {"contrast": "Low", "axis": "Extended Neo-Geometric", "x_height": "High", "aperture": "Wide"},
        "director_notes": "📌 Phiên bản Extended mở rộng bề ngang bề thế, vững chãi, cực kỳ ấn tượng cho các video headline, key visual và branding hiện đại.",
        "sample_text": "Mở rộng tầm nhìn kiến trúc chữ với tỷ lệ bề ngang ấn tượng và hiện đại",
        "styles": [
            "Air", "AirItalic", "Thin", "ThinItalic", "Light", "LightItalic",
            "Regular", "RegularItalic", "Medium", "MediumItalic",
            "SemiBold", "SemiBoldItalic", "Bold", "BoldItalic", "Black", "BlackItalic"
        ]
    },
    {
        "core": "Mono",
        "id": "fdaeonikmono",
        "name": "FD Aeonik Mono",
        "family": "FD Aeonik Mono",
        "category": "Monospace",
        "subcategory": "Tech Monospace",
        "matrix_3d": {"style": "Monospace", "mood": "Lập trình & Kỹ thuật", "use_case": "Code & Data Visual"},
        "anatomy": {"contrast": "None", "axis": "Geometric Monospaced", "x_height": "High", "aperture": "Open"},
        "director_notes": "📌 Phiên bản Monospace chuẩn hình học độ rộng cố định (advance width 620), chuyên dụng cho giao diện lập trình, coding visual, thông số kỹ thuật và data visualization.",
        "sample_text": "const system = new HighPrecisionTypographyEngine({ monospace: true, width: 620 });",
        "styles": ["Air", "Thin", "Light", "Regular", "Medium", "SemiBold", "Bold", "Black"]
    },
    {
        "core": "Fono",
        "id": "fdaeonikfono",
        "name": "FD Aeonik Fono",
        "family": "FD Aeonik Fono",
        "category": "Sans Serif",
        "subcategory": "Tech Semi-Monospace",
        "matrix_3d": {"style": "Tech Grotesque", "mood": "Kỹ thuật số & Tương lai", "use_case": "Display & Interface"},
        "anatomy": {"contrast": "Low", "axis": "Hybrid Tech Grotesque", "x_height": "High", "aperture": "Open"},
        "director_notes": "📌 Phiên bản Fono phong cách kỹ thuật số lai ghép (hybrid tech grotesque), mang linh hồn viễn thông, audio synthesizer và retro-future aesthetics.",
        "sample_text": "Hệ thống tổng hợp tín hiệu âm thanh và điều chế tần số sóng kỹ thuật số",
        "styles": ["Air", "Thin", "Light", "Regular", "Medium", "SemiBold", "Bold", "Black"]
    }
]

def build_entry(meta):
    core = meta["core"]
    zip_path = DIST_ZIPS / f"FD-Aeonik{core}.zip"
    zip_size = zip_path.stat().st_size if zip_path.exists() else 0
    
    files = []
    for st in meta["styles"]:
        ps_name = f"FDAeonik{core}-{st}"
        ttf_p = DIST_FONTS / f"{ps_name}.ttf"
        size = ttf_p.stat().st_size if ttf_p.exists() else 0
        files.append({
            "filename": f"{ps_name}.ttf",
            "style": st,
            "ext": "ttf",
            "size": size,
            "source_filename": f"{ps_name}.ttf"
        })
        
    entry = {
        "id": meta["id"],
        "name": meta["name"],
        "family": meta["family"],
        "designer": "FEDU Type Foundry",
        "source": "CoType & FEDU Studio",
        "category": meta["category"],
        "subcategory": meta["subcategory"],
        "matrix_3d": meta["matrix_3d"],
        "anatomy": meta["anatomy"],
        "vietnamese_support": True,
        "director_notes": meta["director_notes"],
        "weights": meta["styles"],
        "sample_text": meta["sample_text"],
        "web_font_url": f"fonts/FDAeonik{core}-Regular.woff2",
        "files_count": len(files),
        "files": files,
        "director_review": meta["director_notes"],
        "critique": meta["director_notes"],
        "nhan_dinh_dao_dien": meta["director_notes"],
        "typography_critique": meta["director_notes"],
        "zip_filename": f"FD-Aeonik{core}.zip",
        "zip_size_bytes": zip_size
    }
    return entry

def update_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    existing_ids = {f.get("id"): i for i, f in enumerate(catalog["fonts"])}
    
    added = 0
    updated = 0
    for meta in FAMILIES_META:
        entry = build_entry(meta)
        fid = entry["id"]
        if fid in existing_ids:
            catalog["fonts"][existing_ids[fid]] = entry
            updated += 1
        else:
            catalog["fonts"].append(entry)
            added += 1
            
    catalog["summary"]["total_families"] = len(catalog["fonts"])
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"✔ Updated catalog.json: {added} added, {updated} updated. Total families: {len(catalog['fonts'])}")

def update_fonts_json():
    with open(FONTS_JSON_PATH, "r", encoding="utf-8") as f:
        fonts_data = json.load(f)
        
    # fonts.json is a list of font families
    if isinstance(fonts_data, list):
        existing_ids = {f.get("id"): i for i, f in enumerate(fonts_data)}
        added = 0
        updated = 0
        for meta in FAMILIES_META:
            entry = build_entry(meta)
            fid = entry["id"]
            if fid in existing_ids:
                fonts_data[existing_ids[fid]] = entry
                updated += 1
            else:
                fonts_data.append(entry)
                added += 1
        with open(FONTS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(fonts_data, f, indent=2, ensure_ascii=False)
        print(f"✔ Updated fonts.json: {added} added, {updated} updated. Total families: {len(fonts_data)}")

if __name__ == "__main__":
    update_catalog()
    update_fonts_json()
