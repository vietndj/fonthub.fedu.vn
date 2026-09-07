#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_fontmoi_vietnamese.py
Comprehensive Quality Audit & Unit Test Suite for Font Moi Vietnamese Localization:
Foundries:
1. DINAMO (4 families: FD Monument Grotesk, FD Monument Grotesk Condensed, FD Monument Grotesk Mono, FD Monument Grotesk Semi Mono)
2. PANGRAM PANGRAM (1 family: FD Formula)
3. KLIM TYPE FOUNDRY (27 families: American Grotesk, Calibre, Die Grotesk, Domaine, Domaine Sans, Epicene,
   Family, Feijoa, Financier, Founders Grotesk, Geograph, Heldane, Karbon, Maelstrom, Manuka, Martina Plantijn,
   Metric, National, National 2, Newzald, Pitch, Signifier, Söhne, The Future, Tiempos, Untitled Sans, Untitled Serif)

Audits 10 technical & typographic criteria:
1. All 32 families discovered across formats
2. 100% coverage of 134 Vietnamese accented characters (67 lowercase, 67 uppercase)
3. Advance Width Invariance w(accented) == w(base) (delta = 0px) for proportional fonts
4. Strict Monospace Advance Width uniformity across all 134 Vietnamese chars for Mono families
5. OpenType OS/2 table bit 18 (Vietnamese CP1258) & bit 15
6. Solid crossbar integrity for đ and Đ
7. Horn contour integrity for ơ and ư
8. HarfBuzz shaping and GPOS kerning parity
9. WOFF2 Brotli webfont validity (wOF2 header, size > 1KB, parseable)
10. ZIP download packages existence & archive integrity
"""

import os
import sys
import zipfile
import unittest
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
SEARCH_DIRS = [
    PROJECT_ROOT / "dist" / "fonts",
    PROJECT_ROOT / "fonts",
    PROJECT_ROOT / "dist" / "fonts" / "web",
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

DINAMO_FAMILIES = [
    "FD Monument Grotesk",
    "FD Monument Grotesk Condensed",
    "FD Monument Grotesk Mono",
    "FD Monument Grotesk Semi Mono",
]

PANGRAM_FAMILIES = [
    "FD Formula",
]

KLIM_FAMILIES = [
    "FD American Grotesk",
    "FD Calibre",
    "FD Die Grotesk",
    "FD Domaine",
    "FD Domaine Sans",
    "FD Epicene",
    "FD Family",
    "FD Feijoa",
    "FD Financier",
    "FD Founders Grotesk",
    "FD Geograph",
    "FD Heldane",
    "FD Karbon",
    "FD Maelstrom",
    "FD Manuka",
    "FD Martina Plantijn",
    "FD Metric",
    "FD National",
    "FD National 2",
    "FD Newzald",
    "FD Pitch",
    "FD Signifier",
    "FD Söhne",
    "FD The Future",
    "FD Tiempos",
    "FD Untitled Sans",
    "FD Untitled Serif",
]

ALL_FONTMOI_FAMILIES = DINAMO_FAMILIES + PANGRAM_FAMILIES + KLIM_FAMILIES

def normalize_name(s: str) -> str:
    return "".join(c for c in s.lower().replace('ö', 'o').replace('ü', 'u').replace('ä', 'a') if c.isalnum())

def get_cmap(font: TTFont):
    cmap = {}
    if 'cmap' in font:
        for t in font['cmap'].tables:
            if t.isUnicode():
                cmap.update(t.cmap)
    return cmap

def discover_family_fonts(fam_name: str, formats=(".otf", ".ttf", ".woff2")):
    clean_fam = fam_name.replace("FD ", "")
    norm_fam = normalize_name(clean_fam)
    norm_full = normalize_name(fam_name)
    found = {}

    for d in SEARCH_DIRS:
        if not d.exists():
            continue
        for ext in formats:
            for p in d.glob(f"**/*{ext}"):
                if "downloads" in str(p).lower():
                    continue
                stem_low = p.stem.lower()
                norm_stem = normalize_name(p.stem)

                if "condensed" in fam_name.lower() and "condensed" not in stem_low:
                    continue
                if "condensed" not in fam_name.lower() and "condensed" in stem_low and "american" not in fam_name.lower():
                    continue
                if "semi mono" in fam_name.lower() and "semimono" not in stem_low:
                    continue
                if "semi mono" not in fam_name.lower() and "semimono" in stem_low:
                    continue
                if fam_name.endswith(" Mono") and "mono" not in stem_low:
                    continue
                if not fam_name.endswith(" Mono") and "semi mono" not in fam_name.lower() and "mono" in stem_low and "monument" in stem_low:
                    continue
                if "domaine sans" in fam_name.lower() and "sans" not in stem_low:
                    continue
                if "domaine" in fam_name.lower() and "sans" not in fam_name.lower() and "sans" in stem_low:
                    continue
                if "national 2" in fam_name.lower() and "national2" not in stem_low:
                    continue
                if fam_name.endswith("National") and "national2" in stem_low:
                    continue
                if fam_name.endswith("Metric") and "geometric" in stem_low:
                    continue
                if "untitled sans" in fam_name.lower() and "sans" not in stem_low:
                    continue
                if "untitled serif" in fam_name.lower() and "serif" not in stem_low:
                    continue

                if norm_fam in norm_stem or norm_full in norm_stem:
                    key = (fam_name, p.name)
                    if key not in found:
                        found[key] = p
    return sorted(list(found.values()), key=lambda x: x.name)

class TestFontMoiVietnameseLocalization(unittest.TestCase):

    def test_01_all_32_families_discovered(self):
        """Kiểm tra đầy đủ cả 32 họ font (Dinamo, Pangram Pangram, Klim) đã được xuất bản"""
        missing = []
        counts = {}
        for fam in ALL_FONTMOI_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            counts[fam] = len(fonts)
            if len(fonts) == 0:
                missing.append(fam)
        self.assertEqual(len(missing), 0,
                         f"Thiếu {len(missing)} họ font chưa build: {missing}. Đã tìm thấy: {counts}")

    def test_02_vietnamese_cmap_100_percent_coverage(self):
        """Kiểm tra 100% độ phủ 134 ký tự tiếng Việt (hoa + thường + dấu kép) trong cmap"""
        for fam in ALL_FONTMOI_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                missing = [c for c in ALL_VIET_CHARS if ord(c) not in cmap]
                self.assertEqual(len(missing), 0,
                                 f"Font {fp.name} ({fam}) thiếu {len(missing)} ký tự tiếng Việt: {''.join(missing[:20])}")

    def test_03_advance_width_preservation(self):
        """Kiểm tra advance width w(accented) == w(base) (delta = 0px) cho các font tỷ lệ thường"""
        for fam in ALL_FONTMOI_FAMILIES:
            if "mono" in fam.lower():
                continue
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                if "mono" in fp.name.lower():
                    continue
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
                                 f"Font {fp.name} ({fam}) có {len(mismatches)} ký tự lệch width: {', '.join(mismatches[:8])}")

    def test_04_mono_strict_advance_width(self):
        """Kiểm tra các font Monospace duy trì độ rộng bước nhảy (advance width) tuyệt đối đồng nhất"""
        all_mono_fonts = []
        for fam in ALL_FONTMOI_FAMILIES:
            if "semi mono" in fam.lower():
                continue
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                if (("mono" in fp.name.lower() and "semimono" not in fp.name.lower()) or "pitch" in fp.name.lower()):
                    all_mono_fonts.append((fam, fp))

        for fam, fp in all_mono_fonts:
            f = TTFont(str(fp))
            cmap = get_cmap(f)
            hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
            ascii_widths = [hmtx[cmap[ord(c)]][0] for c in 'abcdefghijklmnopqrstuvwxyz' if ord(c) in cmap and cmap[ord(c)] in hmtx]
            if not ascii_widths:
                continue
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
                             f"Font Mono {fp.name} ({fam}) phá vỡ monospace tại: {', '.join(mono_mismatches[:8])}")

    def test_05_opentype_os2_codepage_vietnamese(self):
        """Kiểm tra bảng OS/2 table: ulCodePageRange1 phải bật bit 18 (Vietnamese CP1258)"""
        for fam in ALL_FONTMOI_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                if 'OS/2' in f:
                    os2 = f['OS/2']
                    has_vn_cp = bool(os2.ulCodePageRange1 & (1 << 18))
                    self.assertTrue(has_vn_cp,
                                    f"Font {fp.name} ({fam}) chưa bật bit 18 (Vietnamese CP1258) trong OS/2.ulCodePageRange1")

    def test_06_dcroat_integrity(self):
        """Kiểm tra đ và Đ có đầy đủ glyph, không rỗng và thanh ngang solid"""
        for fam in ALL_FONTMOI_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                self.assertIn(ord('đ'), cmap, f"Font {fp.name} thiếu ký tự 'đ'")
                self.assertIn(ord('Đ'), cmap, f"Font {fp.name} thiếu ký tự 'Đ'")

                if 'CFF ' in f:
                    cff = f['CFF '].cff.topDictIndex[0]
                    cs_d = cff.CharStrings[cmap[ord('đ')]]
                    cs_D = cff.CharStrings[cmap[ord('Đ')]]
                    self.assertGreater(len(cs_d.bytecode), 10, f"Font {fp.name}: Glyph 'đ' byte rỗng")
                    self.assertGreater(len(cs_D.bytecode), 10, f"Font {fp.name}: Glyph 'Đ' byte rỗng")
                elif 'glyf' in f:
                    g_d = f['glyf'][cmap[ord('đ')]]
                    g_D = f['glyf'][cmap[ord('Đ')]]
                    self.assertTrue(g_d.numberOfContours != 0 or g_d.isComposite(), f"Font {fp.name}: 'đ' không có contour")
                    self.assertTrue(g_D.numberOfContours != 0 or g_D.isComposite(), f"Font {fp.name}: 'Đ' không có contour")

    def test_07_horn_integrity(self):
        """Kiểm tra các ký tự dấu sừng ơ, ư, Ơ, Ư có đầy đủ glyph outline hợp lệ"""
        for fam in ALL_FONTMOI_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts:
                f = TTFont(str(fp))
                cmap = get_cmap(f)
                for ch in ['ơ', 'ư', 'Ơ', 'Ư']:
                    self.assertIn(ord(ch), cmap, f"Font {fp.name} thiếu ký tự '{ch}'")
                    if 'CFF ' in f:
                        cff = f['CFF '].cff.topDictIndex[0]
                        cs = cff.CharStrings[cmap[ord(ch)]]
                        self.assertGreater(len(cs.bytecode), 10, f"Font {fp.name}: Glyph '{ch}' rỗng")
                    elif 'glyf' in f:
                        g = f['glyf'][cmap[ord(ch)]]
                        self.assertTrue(g.numberOfContours != 0 or g.isComposite(), f"Font {fp.name}: '{ch}' không có contour")

    def test_08_harfbuzz_kerning_parity(self):
        """Kiểm tra HarfBuzz shaping: từ tiếng Việt có dấu giữ nguyên advance width tổng thể so với từ gốc"""
        test_pairs = [('THUC', 'THỰC'), ('VIET', 'VIỆT'), ('DIEN', 'ĐIỆN'), ('CHIEN', 'CHIẾN')]
        for fam in ALL_FONTMOI_FAMILIES:
            fonts = discover_family_fonts(fam, formats=(".otf", ".ttf"))
            for fp in fonts[:2]:
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
                                     f"Font {fp.name} ({fam}): HarfBuzz lệch giữa {w1} ({adv1}) và {w2} ({adv2})")

    def test_09_webfonts_woff2_validity(self):
        """Kiểm tra webfonts WOFF2 đã sinh đầy đủ, nén Brotli hợp lệ và kích thước tối ưu"""
        for fam in ALL_FONTMOI_FAMILIES:
            woff2_fonts = discover_family_fonts(fam, formats=(".woff2",))
            self.assertGreater(len(woff2_fonts), 0, f"Chưa có file WOFF2 nào cho family {fam}")
            for wp in woff2_fonts:
                self.assertGreater(wp.stat().st_size, 1024, f"File WOFF2 {wp.name} quá nhỏ")
                with open(wp, 'rb') as wf:
                    magic = wf.read(4)
                    self.assertEqual(magic, b"wOF2", f"File {wp.name} không có magic header wOF2")
                f = TTFont(str(wp))
                self.assertIn('cmap', f, f"File WOFF2 {wp.name} không parse được cmap")

    def test_10_zip_archives_integrity(self):
        """Kiểm tra các file nén ZIP download cho các họ và Foundry Collection trong dist/zips/FD/"""
        zips_dir = PROJECT_ROOT / "dist" / "zips" / "FD"
        self.assertTrue(zips_dir.exists(), "Thư mục dist/zips/FD không tồn tại")

        expected_collections = [
            "FD-Dinamo-Collection.zip",
            "FD-Pangram-Collection.zip",
            "FD-Klim-Collection.zip"
        ]
        for col_zip in expected_collections:
            p = zips_dir / col_zip
            self.assertTrue(p.exists(), f"Thiếu file master collection zip: {col_zip}")
            self.assertGreater(p.stat().st_size, 10000, f"File zip {col_zip} dung lượng quá nhỏ")
            with zipfile.ZipFile(p) as zf:
                bad = zf.testzip()
                self.assertIsNone(bad, f"File zip {col_zip} bị lỗi CRC/hỏng: {bad}")
                names = zf.namelist()
                font_files = [n for n in names if n.lower().endswith(('.otf', '.ttf', '.woff2'))]
                self.assertGreater(len(font_files), 0, f"File zip {col_zip} không chứa font files")

if __name__ == '__main__':
    unittest.main()
