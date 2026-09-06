#!/usr/bin/env python3
"""
scripts/validate_catalog.py
Master Font Catalog Integrity Verification Suite for fedu.vn/font.

Rigorously verifies data/catalog.json against all Milestone 1 requirements:
- Valid JSON format & schema compliance
- Exactly 361 font families
- Exact 1,070 Drive files accounting
- 253 PDF curated catalog preservation
- 100% population of 3D Selection Matrix (Style, Mood, Use Case)
- 100% population of Typographic Anatomy (Contrast, Axis, X-height, Aperture)
- 100% Vietnamese support confirmation and accented sample texts
- Non-empty director notes and unique kebab-case IDs
"""

import os
import sys
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(PROJECT_ROOT, "data/catalog.json")

# Mandatory taxonomy sets
VALID_MOODS = {
    "Luxury & Sang trọng",
    "Tech & Công nghệ",
    "Bold & Tuyên ngôn",
    "Friendly & Nhân văn",
    "Nostalgic & Cổ điển"
}

VALID_USE_CASES = {
    "Display / Headline",
    "Body Text",
    "Display & Body"
}

VALID_VISUAL_STYLES = {
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
    "Script",
    "Blackletter",
    "Việt Nam Vintage"
}

VIETNAMESE_ACCENT_REGEX = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ"
    r"ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ]"
)

def run_validation():
    print("=== Master Font Catalog Validation (Milestone 1) ===")
    errors = []
    warnings = []

    # 1. File existence
    if not os.path.exists(CATALOG_PATH):
        sys.exit(f"FAIL: Catalog file not found at {CATALOG_PATH}")

    file_size_kb = os.path.getsize(CATALOG_PATH) / 1024
    print(f"Checking catalog file: {CATALOG_PATH} ({file_size_kb:.1f} KB)")

    # 2. JSON parsing
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        sys.exit(f"FAIL: JSON parsing error in {CATALOG_PATH}: {e}")

    # 3. Top-level structure
    for key in ["version", "updated_at", "summary", "fonts", "matrix_taxonomy", "pdf_curated_catalog"]:
        if key not in data:
            errors.append(f"Missing top-level key: '{key}'")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)

    # 4. Summary verification
    summary = data.get("summary", {})
    total_fonts = summary.get("total_fonts")
    pdf_curated = summary.get("pdf_curated_fonts")
    drive_files = summary.get("drive_files_total")
    categories_cnt = summary.get("categories_count")

    if total_fonts != 361:
        errors.append(f"Summary total_fonts expected 361, got {total_fonts}")
    if pdf_curated != 253:
        errors.append(f"Summary pdf_curated_fonts expected 253, got {pdf_curated}")
    if drive_files != 1070:
        errors.append(f"Summary drive_files_total expected 1070, got {drive_files}")
    if categories_cnt != len(VALID_VISUAL_STYLES):
        errors.append(f"Summary categories_count expected {len(VALID_VISUAL_STYLES)}, got {categories_cnt}")

    # 5. Fonts list verification
    fonts = data.get("fonts", [])
    if len(fonts) != 361:
        errors.append(f"Expected exactly 361 families in 'fonts', got {len(fonts)}")

    pdf_catalog = data.get("pdf_curated_catalog", [])
    if len(pdf_catalog) != 253:
        errors.append(f"Expected exactly 253 entries in 'pdf_curated_catalog', got {len(pdf_catalog)}")

    # 6. Deep inspection of every font family
    seen_ids = set()
    seen_families = set()
    total_files_counted = 0
    pdf_drive_matched_count = 0
    vn_support_true_count = 0
    sample_text_vn_count = 0

    for idx, font in enumerate(fonts):
        font_id = font.get("id")
        fam_name = font.get("family")

        # ID checks
        if not font_id or not isinstance(font_id, str):
            errors.append(f"Font #{idx}: Missing or invalid 'id'")
        elif font_id in seen_ids:
            errors.append(f"Duplicate font id '{font_id}' at #{idx}")
        else:
            seen_ids.add(font_id)
            if not re.match(r"^[a-z0-9-]+$", font_id):
                errors.append(f"Font id '{font_id}' is not clean kebab-case")

        # Family checks
        if not fam_name or not isinstance(fam_name, str):
            errors.append(f"Font #{idx} ({font_id}): Missing 'family'")
        elif fam_name in seen_families:
            errors.append(f"Duplicate family '{fam_name}' at #{idx}")
        else:
            seen_families.add(fam_name)

        # Name checks
        if not font.get("name"):
            errors.append(f"Font #{idx} ({font_id}): Missing 'name'")

        # Designer
        designer = font.get("designer")
        if not designer or not isinstance(designer, str) or len(designer.strip()) == 0:
            errors.append(f"Font '{fam_name}': Empty or missing 'designer'")

        # Source
        source = font.get("source")
        if source not in ["PDF & Drive", "Drive Archive"]:
            errors.append(f"Font '{fam_name}': Invalid source '{source}'")
        if source == "PDF & Drive":
            pdf_drive_matched_count += 1

        # Category & Subcategory
        category = font.get("category")
        if not category:
            errors.append(f"Font '{fam_name}': Missing 'category'")
        subcategory = font.get("subcategory")
        if not subcategory:
            errors.append(f"Font '{fam_name}': Missing 'subcategory'")

        # 3D Selection Matrix
        matrix_3d = font.get("matrix_3d")
        if not isinstance(matrix_3d, dict):
            errors.append(f"Font '{fam_name}': 'matrix_3d' must be a dict")
        else:
            m_style = matrix_3d.get("style")
            m_mood = matrix_3d.get("mood")
            m_use = matrix_3d.get("use_case")

            if not m_style:
                errors.append(f"Font '{fam_name}': Missing matrix_3d.style")
            elif m_style not in VALID_VISUAL_STYLES:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.style '{m_style}'")
            if m_mood not in VALID_MOODS:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.mood '{m_mood}'")
            if m_use not in VALID_USE_CASES:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.use_case '{m_use}'")

        # Typographic Anatomy
        anatomy = font.get("anatomy")
        if not isinstance(anatomy, dict):
            errors.append(f"Font '{fam_name}': 'anatomy' must be a dict")
        else:
            for field in ["contrast", "axis", "x_height", "aperture"]:
                if not anatomy.get(field):
                    errors.append(f"Font '{fam_name}': Missing anatomy.{field}")

        # Vietnamese Support
        vn_sup = font.get("vietnamese_support")
        if vn_sup is not True:
            errors.append(f"Font '{fam_name}': 'vietnamese_support' must be True, got {vn_sup}")
        else:
            vn_support_true_count += 1

        # Director Notes
        notes = font.get("director_notes")
        if not notes or len(notes.strip()) < 20:
            errors.append(f"Font '{fam_name}': 'director_notes' too short or missing (<20 chars)")

        # Weights
        weights = font.get("weights")
        if not isinstance(weights, list) or len(weights) == 0:
            errors.append(f"Font '{fam_name}': 'weights' must be a non-empty list")

        # Sample Text
        sample = font.get("sample_text")
        if not sample or len(sample.strip()) < 5:
            errors.append(f"Font '{fam_name}': Missing or short 'sample_text'")
        else:
            if VIETNAMESE_ACCENT_REGEX.search(sample):
                sample_text_vn_count += 1
            else:
                errors.append(f"Font '{fam_name}': 'sample_text' lacks Vietnamese accents: '{sample}'")

        # Web Font URL
        wf_url = font.get("web_font_url")
        if not wf_url or not wf_url.startswith("http"):
            errors.append(f"Font '{fam_name}': Invalid 'web_font_url': '{wf_url}'")

        # Drive Folder URL
        df_url = font.get("drive_folder_url")
        if not df_url or not df_url.startswith("https://drive.google.com/"):
            errors.append(f"Font '{fam_name}': Invalid 'drive_folder_url': '{df_url}'")

        # Files Count & Files list
        f_count = font.get("files_count")
        files = font.get("files")
        if not isinstance(f_count, int) or f_count < 1:
            errors.append(f"Font '{fam_name}': Invalid 'files_count': {f_count}")
        elif not isinstance(files, list) or len(files) != f_count:
            errors.append(f"Font '{fam_name}': files_count ({f_count}) does not match len(files) ({len(files) if isinstance(files, list) else 'null'})")
        else:
            total_files_counted += f_count

    # 7. Total files cross-check
    if total_files_counted != 1070:
        errors.append(f"Sum of files_count across all families is {total_files_counted}, expected 1070")

    # 8. Report results
    print("\n--- Validation Metrics ---")
    print(f"Total Font Families Verified: {len(seen_families)} / 361")
    print(f"Total Drive Files Accounted: {total_files_counted} / 1070")
    print(f"PDF Curated Fonts Matched: {pdf_drive_matched_count} families")
    print(f"PDF Curated Catalog Preserved: {len(pdf_catalog)} entries")
    print(f"Vietnamese Support Confirmed: {vn_support_true_count} / 361 (100.0%)")
    print(f"Vietnamese Accented Samples: {sample_text_vn_count} / 361 (100.0%)")

    if errors:
        print(f"\n❌ VALIDATION FAILED with {len(errors)} errors:")
        for err in errors[:25]:
            print(f"  - {err}")
        if len(errors) > 25:
            print(f"  ... and {len(errors) - 25} more errors.")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED: 100% of checks satisfied. Master catalog is authoritative and complete.")
        return 0

if __name__ == "__main__":
    sys.exit(run_validation())
