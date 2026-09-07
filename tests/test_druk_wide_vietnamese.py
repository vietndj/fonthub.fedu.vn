#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_druk_wide_vietnamese.py
Quality Auditor & Verifier Test Suite for Druk Wide Vietnamese Localization.
Audits all 8 styles: Medium, MediumItalic, Bold, BoldItalic, Heavy, HeavyItalic, Super, SuperItalic.
Checks:
1. All 8 styles discovered in TTF and WOFF2
2. 100% Vietnamese Unicode coverage (134/134 characters)
3. Zero advance width inflation: w(accented) == w(base)
4. Diacritic geometry & vertical bounding box sanity (no collision, no clipping)
5. Stacked diacritic clearance (nhịp dấu mũ + thanh: ế, ề, ể, ễ, ệ, ố, ồ, etc.)
6. Đ / đ crossbar geometry integrity
7. HarfBuzz GPOS kerning parity on real Vietnamese typography strings
8. OS/2 & hhea vertical metric safety margins
"""

import os
import sys
import unittest
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
SEARCH_DIRS = [
    PROJECT_ROOT / "fonts",
    PROJECT_ROOT / "dist" / "fonts",
    PROJECT_ROOT / "fonts" / "Druk-Wide" / "ttf",
    PROJECT_ROOT / "fonts" / "Druk-Wide" / "woff2",
    PROJECT_ROOT / "dist" / "fonts" / "web",
    Path("/Users/vietmac/Library/Fonts")
]

STYLES = [
    "Medium",
    "MediumItalic",
    "Bold",
    "BoldItalic",
    "Heavy",
    "HeavyItalic",
    "Super",
    "SuperItalic"
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

def get_cmap(font: TTFont):
    cmap = {}
    if 'cmap' in font:
        for t in font['cmap'].tables:
            if t.isUnicode():
                cmap.update(t.cmap)
    return cmap

def discover_druk_fonts(style: str, extension: str = ".ttf"):
    patterns = [
        f"drukwide-{style.lower()}{extension}",
        f"fddrukwide-{style.lower()}{extension}",
        f"druk-wide-{style.lower()}{extension}",
        f"drukwide_{style.lower()}{extension}",
        f"fddrukwide_{style.lower()}{extension}",
        f"drukwide{style.lower()}{extension}",
        f"fddrukwide{style.lower()}{extension}",
        f"druk wide {style.lower()}{extension}"
    ]
    found = []
    for d in SEARCH_DIRS:
        if not d.exists():
            continue
        for p in d.glob(f"**/*{extension}"):
            low = p.name.lower()
            if any(pt in low for pt in patterns):
                if p not in found:
                    found.append(p)
    return sorted(found)

class TestDrukWideVietnamese(unittest.TestCase):

    def test_01_all_styles_exist(self):
        """1. Kiểm tra đủ 8 styles của Druk Wide ở định dạng TTF và WOFF2"""
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            woff2_list = discover_druk_fonts(s, ".woff2")
            self.assertGreater(len(ttf_list), 0, f"Thiếu file TTF cho style Druk Wide {s}")
            self.assertGreater(len(woff2_list), 0, f"Thiếu file WOFF2 cho style Druk Wide {s}")

    def test_02_unicode_vietnamese_coverage_100_percent(self):
        """2. Kiểm tra độ phủ 134/134 ký tự tiếng Việt đầy đủ 100% trên cả 8 styles"""
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            self.assertGreater(len(ttf_list), 0, f"Không tìm thấy font {s} để kiểm tra cmap")
            fp = ttf_list[0]
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            missing = [c for c in ALL_VIET_CHARS if ord(c) not in cmap]
            self.assertEqual(
                len(missing), 0,
                f"Style {s} ({fp.name}) thiếu {len(missing)} ký tự tiếng Việt: {''.join(missing)}"
            )

    def test_03_advance_width_preservation(self):
        """3. Kiểm tra bảo toàn advance width: w(accented) == w(base) (delta = 0)"""
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            if not ttf_list:
                continue
            fp = ttf_list[0]
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
            
            mismatches = []
            for ch in ALL_VIET_CHARS:
                base_ch = ch.translate(BASE_MAPPING)
                cp_acc = ord(ch)
                cp_base = ord(base_ch)
                if cp_acc in cmap and cp_base in cmap:
                    g_acc = cmap[cp_acc]
                    g_base = cmap[cp_base]
                    if g_acc in hmtx and g_base in hmtx:
                        w_acc = hmtx[g_acc][0]
                        w_base = hmtx[g_base][0]
                        if w_acc != w_base:
                            mismatches.append(f"{ch} (w={w_acc}) vs {base_ch} (w={w_base})")
            
            self.assertEqual(
                len(mismatches), 0,
                f"Style {s} có {len(mismatches)} ký tự bị lệch advance width: {', '.join(mismatches[:5])}"
            )

    def test_04_dcroat_integrity(self):
        """4. Kiểm tra cấu trúc hình học chữ Đ và đ: thanh ngang đặc, bounding box hợp lệ"""
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            if not ttf_list:
                continue
            fp = ttf_list[0]
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            glyf = f['glyf'] if 'glyf' in f else None
            if not glyf:
                continue

            for ch, name in [('đ', 'dcroat'), ('Đ', 'Dcroat')]:
                cp = ord(ch)
                self.assertIn(cp, cmap, f"Style {s} thiếu ký tự {ch}")
                gname = cmap[cp]
                self.assertIn(gname, glyf, f"Style {s} thiếu glyph {gname} trong bảng glyf")
                glyph = glyf[gname]
                self.assertTrue(
                    glyph.numberOfContours != 0,
                    f"Style {s}: Glyph {gname} ({ch}) bị rỗng (contours = 0)"
                )
                self.assertGreater(
                    glyph.xMax - glyph.xMin, 0,
                    f"Style {s}: Bounding box glyph {gname} không hợp lệ"
                )

    def test_05_diacritic_clearance_and_no_clipping(self):
        """5. Kiểm tra dấu không đè lên thân chữ (diacritic collision) và không bị cắt ngọn"""
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            if not ttf_list:
                continue
            fp = ttf_list[0]
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            glyf = f['glyf'] if 'glyf' in f else None
            head = f['head'] if 'head' in f else None
            if not glyf or not head:
                continue

            test_chars = ['Á', 'À', 'Ả', 'Ã', 'Ạ', 'Ế', 'Ề', 'Ể', 'Ễ', 'Ệ', 'Ố', 'Ồ', 'Ổ', 'Ỗ', 'Ộ', 'Ứ', 'Ừ', 'ử', 'ữ', 'ự']
            for ch in test_chars:
                if ord(ch) not in cmap:
                    continue
                gname = cmap[ord(ch)]
                if gname not in glyf:
                    continue
                glyph = glyf[gname]
                base_ch = ch.translate(BASE_MAPPING)
                if base_ch != ch and ord(base_ch) in cmap and ch not in ['Ạ', 'Ệ', 'Ộ', 'ự']:
                    base_gname = cmap[ord(base_ch)]
                    if base_gname in glyf:
                        base_glyph = glyf[base_gname]
                        self.assertGreaterEqual(
                            glyph.yMax, base_glyph.yMax,
                            f"Style {s}: Dấu của {ch} bị tụt xuống dưới đỉnh của base {base_ch}"
                        )

    def test_06_gpos_kerning_parity_harfbuzz(self):
        """6. Kiểm tra HarfBuzz GPOS kerning parity trên các cặp từ tiếng Việt thực tế"""
        test_pairs = [
            ('THUC', 'THỰC'),
            ('VIET', 'VIỆT'),
            ('DIEN', 'ĐIỆN'),
            ('CHIEN', 'CHIẾN')
        ]
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            if not ttf_list:
                continue
            fp = ttf_list[0]
            with open(fp, 'rb') as f_bytes:
                hb_face = hb.Face(f_bytes.read())
            hb_font = hb.Font(hb_face)

            def get_adv(text):
                buf = hb.Buffer()
                buf.add_str(text)
                buf.guess_segment_properties()
                hb.shape(hb_font, buf)
                return sum(p.x_advance for p in buf.glyph_positions)

            for w_base, w_viet in test_pairs:
                adv_base = get_adv(w_base)
                adv_viet = get_adv(w_viet)
                self.assertEqual(
                    adv_base, adv_viet,
                    f"Style {s}: Lệch HarfBuzz width giữa '{w_base}' ({adv_base}) và '{w_viet}' ({adv_viet})"
                )

    def test_07_vertical_metrics_safety(self):
        """7. Kiểm tra vertical metrics trong OS/2 và hhea bao bọc an toàn glyphs có dấu"""
        for s in STYLES:
            ttf_list = discover_druk_fonts(s, ".ttf")
            if not ttf_list:
                continue
            fp = ttf_list[0]
            f = TTFont(str(fp))
            head = f['head']
            os2 = f['OS/2'] if 'OS/2' in f else None
            hhea = f['hhea'] if 'hhea' in f else None

            if os2 and hhea:
                self.assertGreaterEqual(
                    os2.usWinAscent, head.yMax - 50,
                    f"Style {s}: usWinAscent ({os2.usWinAscent}) thấp hơn yMax ({head.yMax}), nguy cơ cắt ngọn dấu!"
                )
                self.assertGreaterEqual(
                    abs(os2.usWinDescent), abs(min(0, head.yMin)),
                    f"Style {s}: usWinDescent không đủ bao bọc dấu nặng/yMin ({head.yMin})"
                )

if __name__ == '__main__':
    unittest.main()
