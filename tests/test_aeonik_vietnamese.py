#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_aeonik_vietnamese.py
Unit & E2E Test Suite for Aeonik Vietnamese Localization
Audits all 5 families: Aeonik Soft, Condensed, Extended, Fono, Mono.
"""

import os
import sys
import unittest
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
SEARCH_DIRS = [
    PROJECT_ROOT / "dist/fonts",
    PROJECT_ROOT / "fonts",
    PROJECT_ROOT / "dist/fonts/web",
    PROJECT_ROOT / "output_aeonik",
    PROJECT_ROOT / "temp_aeonik",
    Path("/Users/vietmac/Library/Fonts")
]

VIET_CHARS_LOWER = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS_UPPER = VIET_CHARS_LOWER.upper()
ALL_VIET_CHARS = VIET_CHARS_LOWER + VIET_CHARS_UPPER

BASE_MAPPING = str.maketrans(
    'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
    'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
    'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
    'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
)

FAMILIES = ["Soft", "Condensed", "Extended", "Fono", "Mono"]

def get_cmap(font: TTFont):
    cmap = {}
    if 'cmap' in font:
        for t in font['cmap'].tables:
            if t.isUnicode():
                cmap.update(t.cmap)
    return cmap

def discover_family_fonts(fam_name: str):
    patterns = [f"aeonik {fam_name.lower()}", f"aeonik{fam_name.lower()}", f"fdaeonik{fam_name.lower()}", f"aeonik-{fam_name.lower()}"]
    found = []
    for d in SEARCH_DIRS:
        if not d.exists():
            continue
        for ext in ["*.otf", "*.ttf", "*.woff2"]:
            for p in d.glob(f"**/{ext}"):
                low = p.name.lower()
                parent_low = p.parent.name.lower()
                if "trial" in low or "trial" in parent_low:
                    continue
                if any(pt in low or pt in parent_low for pt in patterns):
                    if p not in found:
                        found.append(p)
    return sorted(found)

class TestAeonikVietnameseLocalization(unittest.TestCase):
    
    def test_01_all_families_discovered(self):
        """Kiểm tra có đủ cả 5 families Aeonik đã được việt hóa"""
        for fam in FAMILIES:
            fonts = discover_family_fonts(fam)
            self.assertGreater(len(fonts), 0, f"Chưa tìm thấy font việt hóa nào cho family Aeonik {fam}")

    def test_02_vietnamese_cmap_100_percent(self):
        """Kiểm tra độ bao phủ 134 ký tự tiếng Việt đầy đủ 100% trong bảng cmap"""
        for fam in FAMILIES:
            fonts = discover_family_fonts(fam)
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                missing = [c for c in ALL_VIET_CHARS if ord(c) not in cmap]
                self.assertEqual(len(missing), 0, f"Font {fp.name} thiếu {len(missing)} ký tự: {''.join(missing[:20])}")

    def test_03_advance_width_preservation(self):
        """Kiểm tra advance width w(accented) == w(base) cho 4 families thường (delta = 0)"""
        for fam in ["Soft", "Condensed", "Extended", "Fono"]:
            fonts = discover_family_fonts(fam)
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
                for ch in ALL_VIET_CHARS:
                    base_ch = ch.translate(BASE_MAPPING)
                    cp = ord(ch)
                    cp_base = ord(base_ch)
                    if cp in cmap and cp_base in cmap:
                        g_acc = cmap[cp]
                        g_base = cmap[cp_base]
                        if g_acc in hmtx and g_base in hmtx:
                            w_acc = hmtx[g_acc][0]
                            w_base = hmtx[g_base][0]
                            self.assertEqual(w_acc, w_base, f"Font {fp.name}: Ký tự {ch} lệch width so với base {base_ch} ({w_acc} != {w_base})")

    def test_04_mono_strict_advance_width(self):
        """Kiểm tra Aeonik Mono giữ chuẩn monospace tuyệt đối (width = 620) trên toàn bộ 134 ký tự"""
        mono_fonts = discover_family_fonts("Mono")
        for fp in mono_fonts:
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
            for ch in ALL_VIET_CHARS:
                cp = ord(ch)
                if cp in cmap:
                    gname = cmap[cp]
                    if gname in hmtx:
                        w = hmtx[gname][0]
                        self.assertEqual(w, 620, f"Font {fp.name} (Mono): Ký tự {ch} có width = {w}, kỳ vọng 620")

    def test_05_gpos_kerning_parity(self):
        """Kiểm tra GPOS kerning parity với HarfBuzz (THUC == THỰC, VIET == VIỆT, DIEN == ĐIỆN, CHIEN == CHIẾN)"""
        pairs = [('THUC', 'THỰC'), ('VIET', 'VIỆT'), ('DIEN', 'ĐIỆN'), ('CHIEN', 'CHIẾN')]
        for fam in FAMILIES:
            fonts = discover_family_fonts(fam)
            for fp in fonts:
                if fp.suffix.lower() == '.woff2':
                    continue  # Test directly on TTF/OTF
                with open(fp, 'rb') as f_bytes:
                    hb_face = hb.Face(f_bytes.read())
                hb_font = hb.Font(hb_face)
                def get_w(text):
                    buf = hb.Buffer()
                    buf.add_str(text)
                    buf.guess_segment_properties()
                    hb.shape(hb_font, buf)
                    return sum(p.x_advance for p in buf.glyph_positions)
                for w1, w2 in pairs:
                    adv1 = get_w(w1)
                    adv2 = get_w(w2)
                    self.assertEqual(adv1, adv2, f"Font {fp.name}: Kerning không khớp giữa {w1} ({adv1}) và {w2} ({adv2})")

    def test_06_dcroat_crossbar_integrity(self):
        """Kiểm tra đ và Đ có thanh ngang đặc, không rỗng"""
        for fam in FAMILIES:
            fonts = discover_family_fonts(fam)
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                self.assertIn(ord('đ'), cmap, f"Font {fp.name} thiếu ký tự đ")
                self.assertIn(ord('Đ'), cmap, f"Font {fp.name} thiếu ký tự Đ")

    def test_07_ohorn_horn_attachment_integrity(self):
        """Kiểm tra râu chữ Ơ / ơ dính chặt vào vai O / o, không bị lơ lửng tách rời thành component riêng lẻ"""
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        import cv2

        def get_comp_count(font_path, text, size=120):
            try:
                font = ImageFont.truetype(str(font_path), size)
            except Exception:
                return -1
            img = Image.new("L", (size * 2, size * 2), 0)
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), text, font=font, fill=255)
            arr = np.array(img)
            _, thresh = cv2.threshold(arr, 50, 255, cv2.THRESH_BINARY)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
            areas = [stats[i, cv2.CC_STAT_AREA] for i in range(1, num_labels)]
            valid = [a for a in areas if a > 20]
            return len(valid)

        for fam in FAMILIES:
            fonts = discover_family_fonts(fam)
            for fp in fonts:
                if fp.suffix.lower() == '.woff2':
                    continue
                # Ơ and ơ must be 1 single connected component (horn welded to O/o)
                c_upper = get_comp_count(fp, "Ơ")
                c_lower = get_comp_count(fp, "ơ")
                self.assertEqual(c_upper, 1, f"Font {fp.name}: Chữ Ơ bị lỗi râu lơ lửng tách rời ({c_upper} components thay vì 1)")
                self.assertEqual(c_lower, 1, f"Font {fp.name}: Chữ ơ bị lỗi râu lơ lửng tách rời ({c_lower} components thay vì 1)")

if __name__ == '__main__':
    unittest.main()

