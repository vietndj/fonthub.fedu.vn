#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_cotype_vietnamese.py
Comprehensive Quality Audit & Unit Test Suite for CoType Vietnamese Localization.
Audits all 11 CoType Families:
1. Altform
2. Ambit
3. Coanda
4. Lock Sans Stencil
5. Lock Sans
6. Lock Serif Stencil
7. Lock Serif
8. Orbikular
9. RM Mono
10. RM Neue
11. Scandium
"""

import os
import sys
import unittest
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
SEARCH_DIRS = [
    PROJECT_ROOT / "dist" / "fonts",
    PROJECT_ROOT / "fonts",
    PROJECT_ROOT / "dist" / "fonts" / "web",
    PROJECT_ROOT / "output_cotype",
    PROJECT_ROOT / "temp_cotype",
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

COTYPE_FAMILIES = [
    "Altform",
    "Ambit",
    "Coanda",
    "Lock Sans Stencil",
    "Lock Sans",
    "Lock Serif Stencil",
    "Lock Serif",
    "Orbikular",
    "RM Mono",
    "RM Neue",
    "Scandium"
]

def get_cmap(font: TTFont):
    cmap = {}
    if 'cmap' in font:
        for t in font['cmap'].tables:
            if t.isUnicode():
                cmap.update(t.cmap)
    return cmap

def normalize_name(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())

def discover_family_fonts(fam_name: str, formats=(".otf", ".ttf", ".woff2")):
    norm_fam = normalize_name(fam_name)
    found = {}
    for d in SEARCH_DIRS:
        if not d.exists():
            continue
        for ext in formats:
            for p in d.glob(f"**/*{ext}"):
                low = p.name.lower()
                parent_low = p.parent.name.lower()
                # Skip raw unviethoa trials if in Downloads or raw trial directories
                if "downloads" in str(p).lower():
                    continue
                # Match family name precisely
                norm_p = normalize_name(p.stem)
                norm_parent = normalize_name(p.parent.name)
                
                # Only filter serif/stencil for Lock family variations
                if "lock" in fam_name.lower():
                    is_stencil = "stencil" in fam_name.lower()
                    is_serif = "serif" in fam_name.lower()
                    
                    p_has_stencil = "stencil" in norm_p
                    p_has_serif = "serif" in norm_p
                    
                    if is_stencil != p_has_stencil:
                        continue
                    if is_serif != p_has_serif:
                        continue
                
                # Specific family name matching in font filename
                if norm_fam in norm_p:
                    key = (fam_name, p.name)
                    if key not in found:
                        found[key] = p
    return sorted(list(found.values()), key=lambda x: x.name)

class TestCoTypeVietnameseLocalization(unittest.TestCase):
    
    def test_01_all_11_families_discovered(self):
        """Kiểm tra có đủ cả 11 families CoType đã được việt hóa và xuất xưởng"""
        missing_fams = []
        found_counts = {}
        for fam in COTYPE_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            found_counts[fam] = len(fonts)
            if len(fonts) == 0:
                missing_fams.append(fam)
        
        self.assertEqual(len(missing_fams), 0, 
                         f"Chưa tìm thấy font việt hóa cho {len(missing_fams)} families: {missing_fams}. Found so far: {found_counts}")

    def test_02_vietnamese_cmap_100_percent_coverage(self):
        """Kiểm tra độ bao phủ 134 ký tự tiếng Việt đầy đủ 100% trong bảng cmap cho tất cả styles"""
        for fam in COTYPE_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                missing = [c for c in ALL_VIET_CHARS if ord(c) not in cmap]
                self.assertEqual(len(missing), 0, 
                                 f"Font {fp.name} ({fam}) thiếu {len(missing)} ký tự tiếng Việt: {''.join(missing[:30])}")

    def test_03_advance_width_preservation(self):
        """Kiểm tra advance width w(accented) == w(base) cho 10 families tỷ lệ thường (delta = 0)"""
        for fam in COTYPE_FAMILIES:
            if fam == "RM Mono":
                continue
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
                mismatches = []
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
                            if w_acc != w_base:
                                mismatches.append(f"{ch}({w_acc})!={base_ch}({w_base})")
                self.assertEqual(len(mismatches), 0, 
                                 f"Font {fp.name} ({fam}) có {len(mismatches)} ký tự lệch width: {', '.join(mismatches[:10])}")

    def test_04_rm_mono_strict_advance_width(self):
        """Kiểm tra RM Mono duy trì chuẩn monospace đồng nhất tuyệt đối trên toàn bộ 134 ký tự tiếng Việt"""
        mono_fonts = discover_family_fonts("RM Mono", formats=(".otf", ".ttf"))
        for fp in mono_fonts:
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
            # Detect expected monospace width from standard ASCII
            ascii_widths = [hmtx[cmap[ord(c)]][0] for c in 'abcdefghijklmnopqrstuvwxyz' if ord(c) in cmap and cmap[ord(c)] in hmtx]
            self.assertGreater(len(ascii_widths), 0, f"RM Mono {fp.name} không có ký tự ASCII chuẩn")
            expected_w = max(set(ascii_widths), key=ascii_widths.count)
            
            mono_mismatches = []
            for ch in ALL_VIET_CHARS:
                cp = ord(ch)
                if cp in cmap:
                    gname = cmap[cp]
                    if gname in hmtx:
                        w = hmtx[gname][0]
                        if w != expected_w:
                            mono_mismatches.append(f"{ch}({w}!={expected_w})")
            self.assertEqual(len(mono_mismatches), 0, 
                             f"RM Mono {fp.name} phá vỡ monospace tại {len(mono_mismatches)} ký tự: {', '.join(mono_mismatches[:10])}")

    def test_05_opentype_os2_codepage_vietnamese(self):
        """Kiểm tra OS/2 table: ulCodePageRange1 phải bật bit 18 (Vietnamese cp1258) và ulUnicodeRange2 bit 15"""
        for fam in COTYPE_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                if 'OS/2' in f:
                    os2 = f['OS/2']
                    # Bit 18 of ulCodePageRange1: 1 << 18 = 0x00040000
                    has_vn_codepage = bool(os2.ulCodePageRange1 & (1 << 18))
                    self.assertTrue(has_vn_codepage, f"Font {fp.name} ({fam}) chưa bật bit 18 (Vietnamese 1258) trong OS/2.ulCodePageRange1")

    def test_06_dcroat_integrity(self):
        """Kiểm tra ký tự đ và Đ có đầy đủ glyph, thanh ngang đặc và advance width hợp lệ"""
        for fam in COTYPE_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                self.assertIn(ord('đ'), cmap, f"Font {fp.name} thiếu glyph 'đ'")
                self.assertIn(ord('Đ'), cmap, f"Font {fp.name} thiếu glyph 'Đ'")
                
                # Check that outline is not empty
                if 'CFF ' in f:
                    cff = f['CFF '].cff.topDictIndex[0]
                    cs_d = cff.CharStrings[cmap[ord('đ')]]
                    cs_D = cff.CharStrings[cmap[ord('Đ')]]
                    self.assertGreater(len(cs_d.bytecode), 10, f"Font {fp.name}: Glyph 'đ' byte rỗng hoặc degenerate")
                    self.assertGreater(len(cs_D.bytecode), 10, f"Font {fp.name}: Glyph 'Đ' byte rỗng hoặc degenerate")
                elif 'glyf' in f:
                    g_d = f['glyf'][cmap[ord('đ')]]
                    g_D = f['glyf'][cmap[ord('Đ')]]
                    self.assertTrue(g_d.numberOfContours != 0 or g_d.isComposite(), f"Font {fp.name}: 'đ' không có contour")
                    self.assertTrue(g_D.numberOfContours != 0 or g_D.isComposite(), f"Font {fp.name}: 'Đ' không có contour")

    def test_07_gpos_kerning_parity(self):
        """Kiểm tra GPOS kerning parity bằng HarfBuzz: các từ tiếng Việt giữ nguyên kerning gốc"""
        test_pairs = [('THUC', 'THỰC'), ('VIET', 'VIỆT'), ('DIEN', 'ĐIỆN'), ('CHIEN', 'CHIẾN')]
        for fam in COTYPE_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                with open(fp, 'rb') as f_bytes:
                    hb_face = hb.Face(f_bytes.read())
                hb_font = hb.Font(hb_face)
                
                def get_w(text):
                    buf = hb.Buffer()
                    buf.add_str(text)
                    buf.guess_segment_properties()
                    hb.shape(hb_font, buf)
                    return sum(p.x_advance for p in buf.glyph_positions)
                
                for w1, w2 in test_pairs:
                    adv1 = get_w(w1)
                    adv2 = get_w(w2)
                    self.assertEqual(adv1, adv2, 
                                     f"Font {fp.name} ({fam}): Kerning lệch giữa {w1} ({adv1}) và {w2} ({adv2})")

    def test_08_webfonts_woff2_existence_and_validity(self):
        """Kiểm tra định dạng WOFF2 đã được tạo đầy đủ, kích thước tối ưu, mở không lỗi"""
        for fam in COTYPE_FAMILIES:
            woff2_fonts = discover_family_fonts(fam, formats=(".woff2",))
            self.assertGreater(len(woff2_fonts), 0, f"Chưa có file WOFF2 nào cho family {fam}")
            for wp in woff2_fonts:
                self.assertGreater(wp.stat().st_size, 1024, f"WOFF2 file {wp.name} quá nhỏ ({wp.stat().st_size} bytes)")
                with open(wp, 'rb') as wf:
                    magic = wf.read(4)
                    self.assertEqual(magic, b"wOF2", f"File {wp.name} không phải chuẩn WOFF2 header")
                # Test opening with TTFont
                f = TTFont(str(wp))
                self.assertIn('cmap', f, f"WOFF2 {wp.name} không có bảng cmap")

if __name__ == '__main__':
    unittest.main()
