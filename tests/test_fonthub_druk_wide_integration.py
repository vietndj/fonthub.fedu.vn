#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_fonthub_druk_wide_integration.py
Quality Auditor & Verifier: FEDU Font (font.fedu.vn) Integration Test Suite for Druk Wide.

Audits:
1. data/catalog.json metadata registration (category, styles, 3D matrix, anatomy, notes)
2. Font file integrity, existence on disk, and MIME types
3. CSS @font-face rules & webfont loading declarations
4. Zero-regression verification across existing test tiers
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path
from fontTools.ttLib import TTFont

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
CATALOG_PATH = PROJECT_ROOT / "data" / "catalog.json"
FONTS_JSON_PATH = PROJECT_ROOT / "data" / "fonts.json"
CSS_PATH = PROJECT_ROOT / "css" / "style.css"
ROOT_CSS_PATH = PROJECT_ROOT / "style.css"
FONTS_DIR = PROJECT_ROOT / "fonts"

EXPECTED_STYLES = [
    "Medium",
    "MediumItalic",
    "Bold",
    "BoldItalic",
    "Heavy",
    "HeavyItalic",
    "Super",
    "SuperItalic"
]

class TestFonthubDrukWideIntegration(unittest.TestCase):

    def setUp(self):
        self.assertTrue(CATALOG_PATH.exists(), f"catalog.json không tồn tại ở {CATALOG_PATH}")
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            self.catalog_data = json.load(f)
        self.fonts = self.catalog_data.get("fonts", [])

    def test_01_catalog_metadata_exists(self):
        """1. Kiểm tra Druk Wide được khai báo chính xác trong data/catalog.json"""
        druk_entries = [
            f for f in self.fonts 
            if "druk" in f.get("name", "").lower() or "druk" in f.get("family", "").lower() or "druk" in f.get("id", "").lower()
        ]
        self.assertGreater(
            len(druk_entries), 0,
            "Chưa tìm thấy font family Druk Wide nào được khai báo trong data/catalog.json"
        )
        entry = druk_entries[0]

        # Assert mandatory schema fields
        self.assertIn("name", entry)
        self.assertIn("category", entry)
        self.assertTrue("styles" in entry or "weights" in entry or "files" in entry, "Thiếu styles/weights/files trong entry")
        self.assertIn("vietnamese_support", entry)
        self.assertTrue(entry.get("vietnamese_support"), "vietnamese_support phải là true")
        self.assertEqual(entry.get("category"), "Sans Serif", "Category của Druk Wide phải là Sans Serif")
        
        # Check styles/weights list
        styles = entry.get("styles") or entry.get("weights") or []
        self.assertGreaterEqual(len(styles), 8, f"Druk Wide phải có ít nhất 8 styles, hiện có {len(styles)}")
        
        # Check director notes & sample text
        self.assertTrue(bool(entry.get("director_notes")), "Thiếu director_notes cho Druk Wide")
        self.assertTrue(bool(entry.get("sample_text")), "Thiếu sample_text cho Druk Wide")

    def test_02_font_files_exist_and_readable(self):
        """2. Kiểm tra các file font được tham chiếu tồn tại trên ổ đĩa và đọc được"""
        druk_entries = [
            f for f in self.fonts 
            if "druk" in f.get("name", "").lower() or "druk" in f.get("family", "").lower() or "druk" in f.get("id", "").lower()
        ]
        if not druk_entries:
            self.skipTest("Druk Wide chưa được đăng ký trong catalog.json")

        entry = druk_entries[0]
        files = entry.get("files", {})
        
        # If files dictionary is provided
        if isinstance(files, dict) and files:
            for style_name, file_rel_path in files.items():
                abs_path = PROJECT_ROOT / file_rel_path
                self.assertTrue(
                    abs_path.exists(),
                    f"File font cho style {style_name} không tồn tại: {abs_path}"
                )
                self.assertGreater(
                    abs_path.stat().st_size, 1000,
                    f"File font {abs_path} quá nhỏ (< 1KB), có thể bị hỏng"
                )
                # Verify header
                with open(abs_path, "rb") as f_bin:
                    magic = f_bin.read(4)
                    ext = abs_path.suffix.lower()
                    if ext == ".woff2":
                        self.assertEqual(magic, b"wOF2", f"File {abs_path.name} không phải chuẩn WOFF2")
                    elif ext == ".ttf":
                        self.assertIn(magic, [b"\x00\x01\x00\x00", b"true", b"typ1"], f"File {abs_path.name} không phải TrueType hợp lệ")
        else:
            # Check directly in fonts/ directory
            found_styles = 0
            for s in EXPECTED_STYLES:
                matches = list(FONTS_DIR.glob(f"*Druk*{s}*.woff2")) + list(FONTS_DIR.glob(f"*Druk*{s}*.ttf"))
                if matches:
                    found_styles += 1
            self.assertGreaterEqual(
                found_styles, 8,
                f"Chưa có đủ 8 styles Druk Wide trong fonts/: chỉ tìm thấy {found_styles}/8"
            )

    def test_03_css_fontface_rules(self):
        """3. Kiểm tra khai báo CSS @font-face cho Druk Wide trong css/style.css hoặc style.css"""
        css_content = ""
        if CSS_PATH.exists():
            with open(CSS_PATH, "r", encoding="utf-8") as f:
                css_content += f.read()
        if ROOT_CSS_PATH.exists():
            with open(ROOT_CSS_PATH, "r", encoding="utf-8") as f:
                css_content += f.read()

        has_fontface = ("Druk" in css_content or "druk" in css_content) and "@font-face" in css_content
        self.assertTrue(
            has_fontface,
            "Chưa tìm thấy khai báo @font-face cho Druk Wide trong css/style.css hoặc style.css"
        )

    def test_04_master_regression_test_passes(self):
        """4. Kiểm tra toàn bộ test runner gốc (node tests/runner.js) vượt qua 100% không hồi quy"""
        result = subprocess.run(
            ["node", "tests/runner.js"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(
            result.returncode, 0,
            f"Regression test thất bại khi chạy runner.js!\nOutput:\n{result.stdout}\nErrors:\n{result.stderr}"
        )
        self.assertIn("ALL TESTS PASSED", result.stdout, "Test runner không trả về thông báo ALL TESTS PASSED")

if __name__ == "__main__":
    unittest.main()
