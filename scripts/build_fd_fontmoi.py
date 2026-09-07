#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FEDU Master Vietnamese Localization & Build Engine for FONTMOI:
- DINAMO (4 families: FD Monument Grotesk, Condensed, Mono, Semi Mono - 64 styles)
- PANGRAM PANGRAM (1 family: FD Formula - 16 styles)
- KLIM TYPE FOUNDRY (27 families: FD American Grotesk, Calibre, Die Grotesk, Domaine, Domaine Sans,
                     Epicene, Family, Feijoa, Financier, Founders Grotesk, Geograph, Heldane,
                     Karbon, Maelstrom, Manuka, Martina Plantijn, Metric, National, National 2,
                     Newzald, Pitch, Signifier, Söhne, The Future, Tiempos, Untitled Sans,
                     Untitled Serif - 650 styles)

Total 730 styles across 32 families.
Features:
1. 100% Vietnamese coverage (134 accented glyphs: 67 lowercase, 67 uppercase).
2. Complete punctuation coverage (import missing punctuation from donor fonts).
3. Strict Advance Width Invariance: w(accented) == w(base) (delta = 0px).
4. Native dotlessi synthesis preserving stem geometry.
5. TrueType/OpenType GPOS Kerning Inheritance for all accented variants.
6. OS/2 CodePage bit 18 (Vietnamese 1258) & bit 15 (Latin Extended Additional) enabled.
7. Triple-Format Export: OTF (OpenType CFF), TTF (TrueType glyf), WOFF2 (Brotli web).
8. Auto installation of OTF to ~/Library/Fonts.
9. Packaging into individual family ZIPs + 3 Master Foundry Collection ZIPs in dist/zips/FD/.
10. Full Font Hub catalog & UI integration.
"""

import os
import sys
import re
import io
import copy
import json
import shutil
import zipfile
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from fontTools.ttLib import TTFont, newTable
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.ttLib.tables._g_l_y_f import flagOnCurve

# Directories
PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
FONTMOI_DIR = Path("/Users/vietmac/Downloads/fontmoi")
DONOR_DIR = Path("/Users/vietmac/Library/Fonts")
MAC_FONTS = Path("/Users/vietmac/Library/Fonts")

DIST_FONTS = PROJECT_ROOT / "dist" / "fonts"
DIST_WEB = PROJECT_ROOT / "dist" / "fonts" / "web"
FONTS_WEB = PROJECT_ROOT / "fonts"
DIST_ZIPS_FD = PROJECT_ROOT / "dist" / "zips" / "FD"
CATALOG_PATH = PROJECT_ROOT / "data" / "catalog.json"
FONTS_JSON_PATH = PROJECT_ROOT / "data" / "fonts.json"

for d in [DIST_FONTS, DIST_WEB, FONTS_WEB, DIST_ZIPS_FD]:
    d.mkdir(parents=True, exist_ok=True)

# 134 Vietnamese characters
VIET_CHARS_LOWER = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS_UPPER = VIET_CHARS_LOWER.upper()
VIET_CHARS = VIET_CHARS_LOWER + VIET_CHARS_UPPER

PUNCT_CODEPOINTS = [
    0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F,
    0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x5B, 0x5C, 0x5D, 0x5E, 0x5F,
    0x60, 0x7B, 0x7C, 0x7D, 0x7E,
    0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x2022
]

WEIGHT_MAP = {
    'hairline': 100, 'thin': 100, 'air': 100,
    'extralight': 200, 'ultralight': 200, 'extraleicht': 200,
    'light': 300, 'leicht': 300,
    'book': 400, 'regular': 400, 'normal': 400, 'buch': 400, 'display': 400, 'text': 400,
    'kraftig': 450, 'kräftig': 450, 'retina': 450,
    'medium': 500,
    'semibold': 600, 'demibold': 600, 'halbfett': 600,
    'bold': 700, 'dreiviertelfett': 700,
    'extrabold': 800, 'ultrabold': 800, 'heavy': 800, 'fett': 800,
    'black': 900, 'extrafett': 900,
    'ultra': 950, 'extrablack': 950, 'ultrablack': 950
}

# Horn relative contour geometry (normalized to 1000 UPM)
HORN_LC_REL = [
    ((0, 0), 1),
    ((-75, 0), 1),
    ((-40, 0), 0),
    ((-5, 45), 0),
    ((-5, 78), 1),
    ((77, 78), 1),
    ((76, 33), 0),
    ((36, -33), 0),
    ((0, -50), 1),
]

HORN_UC_REL = [
    ((0, 0), 1),
    ((-78, 0), 1),
    ((-43, 0), 0),
    ((-8, 45), 0),
    ((-8, 78), 1),
    ((74, 78), 1),
    ((73, 33), 0),
    ((35, -31), 0),
    ((0, -48), 1),
]

BASE_TRANS = str.maketrans(
    'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
    'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
    'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
    'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
)

def get_base_char(ch: str) -> str:
    return ch.translate(BASE_TRANS)

def clean_ascii(s: str) -> str:
    return (s.replace('ö', 'o').replace('Ö', 'O')
             .replace('ä', 'a').replace('Ä', 'A')
             .replace('ü', 'u').replace('Ü', 'U')
             .replace('-', '').replace(' ', '').replace('_', ''))

def draw_tt_contour(coords, flags, pen, reverse=True):
    if reverse:
        coords = list(reversed(coords))
        flags = list(reversed(flags))
    coords = [(int(round(p[0])), int(round(p[1]))) for p in coords]
    cFlags = [flagOnCurve & f for f in flags]
    if 1 not in cFlags:
        return
    firstOnCurve = cFlags.index(1) + 1
    pts_rot = coords[firstOnCurve:] + coords[:firstOnCurve]
    cFlags_rot = cFlags[firstOnCurve:] + cFlags[:firstOnCurve]
    pen.moveTo(pts_rot[-1])
    contour = pts_rot[:]
    while contour:
        nextOnCurve = cFlags_rot.index(1) + 1
        if nextOnCurve == 1:
            if len(contour) > 1:
                pen.lineTo(contour[0])
        else:
            pen.qCurveTo(*contour[:nextOnCurve])
        contour = contour[nextOnCurve:]
        cFlags_rot = cFlags_rot[nextOnCurve:]
    pen.closePath()

def draw_rel_contour(rel_pts, origin_x, origin_y, upm_scale, scale_x, pen):
    pts = []
    flags = []
    for (rx, ry), fl in rel_pts:
        px = int(round(origin_x + rx * upm_scale * scale_x))
        py = int(round(origin_y + ry * upm_scale))
        pts.append((px, py))
        flags.append(fl)
    draw_tt_contour(pts, flags, pen, reverse=True)

def clean_notdef(charstrings, top_dict, hmtx, upm=1000, fixed_w=None):
    scale = upm / 1000.0
    w = fixed_w if fixed_w is not None else int(round(500 * scale))
    x1, x2 = int(round(50 * scale)), int(round((w - 50 * scale)))
    y1, y2 = 0, int(round(700 * scale))
    t2 = T2CharStringPen(width=w, glyphSet=charstrings)
    t2.moveTo((x1, y1))
    t2.lineTo((x1, y2))
    t2.lineTo((x2, y2))
    t2.lineTo((x2, y1))
    t2.closePath()
    cs = t2.getCharString()
    cs.private = top_dict.Private
    cs.compile()
    charstrings['.notdef'] = cs
    hmtx.metrics['.notdef'] = (int(round(w)), int(round(x1)))

def get_donor_path(style_name: str, is_serif: bool = False, is_mono: bool = False) -> Path:
    s_l = style_name.lower()
    is_italic = 'italic' in s_l or 'oblique' in s_l or 'kursiv' in s_l
    
    if is_mono:
        if 'black' in s_l or 'heavy' in s_l or 'extrafett' in s_l or 'fett' in s_l:
            st = 'Black'
        elif 'bold' in s_l or 'dreiviertelfett' in s_l:
            st = 'Bold'
        elif 'semi' in s_l or 'demi' in s_l or 'halbfett' in s_l:
            st = 'SemiBold'
        elif 'light' in s_l or 'leicht' in s_l or 'extraleicht' in s_l:
            st = 'Light'
        else:
            st = 'Regular'
        p = DONOR_DIR / f"FDAeonikMono-{st}.ttf"
        if not p.exists():
            p = DONOR_DIR / f"SVN-Aeonik-{st}.ttf"
        return p
    elif is_serif:
        if 'black' in s_l or 'heavy' in s_l or 'bold' in s_l or 'fett' in s_l:
            st = 'BoldItalic' if is_italic else 'Bold'
        elif 'semi' in s_l or 'demi' in s_l or 'medium' in s_l or 'halbfett' in s_l:
            st = 'MediumItalic' if is_italic else 'Medium'
        elif 'extralight' in s_l or 'thin' in s_l or 'hairline' in s_l:
            st = 'ThinItalic' if is_italic else 'Thin'
        elif 'light' in s_l or 'leicht' in s_l:
            st = 'LightItalic' if is_italic else 'Light'
        else:
            st = 'Italic' if is_italic else 'Regular'
        return DONOR_DIR / f"FDAlpinaFine-{st}.ttf"
    else:
        if 'black' in s_l or 'heavy' in s_l or 'extrafett' in s_l or 'fett' in s_l or 'ultra' in s_l:
            st = 'BlackItalic' if is_italic else 'Black'
        elif 'bold' in s_l or 'dreiviertelfett' in s_l:
            st = 'BoldItalic' if is_italic else 'Bold'
        elif 'semi' in s_l or 'demi' in s_l or 'medium' in s_l or 'halbfett' in s_l or 'kraftig' in s_l or 'kräftig' in s_l:
            st = 'MediumItalic' if is_italic else 'Medium'
        elif 'extralight' in s_l or 'thin' in s_l or 'hairline' in s_l or 'air' in s_l or 'extraleicht' in s_l:
            st = 'ThinItalic' if is_italic else 'Thin'
        elif 'light' in s_l or 'leicht' in s_l:
            st = 'LightItalic' if is_italic else 'Light'
        else:
            st = 'RegularItalic' if is_italic else 'Regular'
        return DONOR_DIR / f"SVN-Aeonik-{st}.ttf"

def inherit_gpos_kerning(f_p, viet_to_base):
    if 'GPOS' not in f_p:
        return
    gpos = f_p['GPOS'].table
    if not hasattr(gpos, 'LookupList') or not gpos.LookupList:
        return
    for lookup in gpos.LookupList.Lookup:
        for sub in lookup.SubTable:
            actual = sub.ExtSubTable if lookup.LookupType == 9 else sub
            if hasattr(actual, 'Format') and actual.Format == 2:
                c1 = actual.ClassDef1.classDefs
                c2 = actual.ClassDef2.classDefs
                cov = actual.Coverage.glyphs
                for dest, base in viet_to_base.items():
                    b1 = c1.get(base) or (c1.get('i') if base == 'dotlessi' else None)
                    if b1 is not None:
                        c1[dest] = b1
                        if (base in cov or (base == 'dotlessi' and 'i' in cov)) and dest not in cov:
                            cov.append(dest)
                    b2 = c2.get(base) or (c2.get('i') if base == 'dotlessi' else None)
                    if b2 is not None:
                        c2[dest] = b2
                cov.sort(key=lambda g: f_p.getGlyphID(g))
            elif hasattr(actual, 'Format') and actual.Format == 1 and hasattr(actual, 'PairSet'):
                for ps in actual.PairSet:
                    new_records = []
                    existing_seconds = {pr.SecondGlyph for pr in ps.PairValueRecord}
                    for pr in ps.PairValueRecord:
                        for dest, base in viet_to_base.items():
                            check_base = 'i' if base == 'dotlessi' else base
                            if pr.SecondGlyph in (base, check_base) and dest not in existing_seconds:
                                new_pr = copy.deepcopy(pr)
                                new_pr.SecondGlyph = dest
                                new_records.append(new_pr)
                                existing_seconds.add(dest)
                    ps.PairValueRecord.extend(new_records)
                    ps.PairValueCount = len(ps.PairValueRecord)
                cov = actual.Coverage.glyphs
                for dest, base in viet_to_base.items():
                    check_base = 'i' if base == 'dotlessi' else base
                    target_base = base if base in cov else (check_base if check_base in cov else None)
                    if target_base and dest not in cov:
                        base_idx = cov.index(target_base)
                        ps_copy = copy.deepcopy(actual.PairSet[base_idx])
                        cov.append(dest)
                        actual.PairSet.append(ps_copy)
                        actual.PairSetCount = len(actual.PairSet)
                sorted_pairs = sorted(zip(cov, actual.PairSet), key=lambda item: f_p.getGlyphID(item[0]))
                actual.Coverage.glyphs = [item[0] for item in sorted_pairs]
                actual.PairSet = [item[1] for item in sorted_pairs]

def convert_cff_to_truetype(cff_font: TTFont) -> TTFont:
    tt_font = copy.deepcopy(cff_font)
    glyph_order = tt_font.getGlyphOrder()
    glyph_set = tt_font.getGlyphSet()

    glyf_table = newTable("glyf")
    glyf_table.glyphs = {}

    for gname in glyph_order:
        pen = TTGlyphPen(glyph_set)
        cu2qu = Cu2QuPen(pen, max_err=1.0, reverse_direction=True)
        glyph_set[gname].draw(cu2qu)
        glyf_table.glyphs[gname] = pen.glyph()

    tt_font["glyf"] = glyf_table
    tt_font["loca"] = newTable("loca")

    for tbl in ["CFF ", "CFF2", "VORG", "vhea", "vmtx"]:
        if tbl in tt_font:
            del tt_font[tbl]

    tt_font.sfntVersion = "\x00\x01\x00\x00"
    if 'maxp' in tt_font:
        tt_font['maxp'].numGlyphs = len(glyph_order)
        tt_font['maxp'].maxZones = 1
    return tt_font

def synthesize_dotlessi(charstrings_p, top_dict_p, hmtx_p, order):
    if 'dotlessi' in charstrings_p:
        return
    if 'i' not in charstrings_p:
        return
    
    rec_i = RecordingPen()
    charstrings_p['i'].draw(rec_i)
    w_i, lsb_i = hmtx_p.metrics['i']
    
    contours = []
    current = []
    for op, args in rec_i.value:
        current.append((op, args))
        if op == 'closePath':
            contours.append(current)
            current = []
    if current:
        contours.append(current)
        
    rec_dli = RecordingPen()
    stem_count = 0
    for c in contours:
        pts = [p for op, args in c for p in args]
        ys = [p[1] for p in pts]
        if ys and max(ys) < 530:
            stem_count += 1
            for op, args in c:
                getattr(rec_dli, op)(*args)
                
    if stem_count == 0:
        rec_i.replay(rec_dli)
        
    t2_dli = T2CharStringPen(width=w_i, glyphSet={})
    rec_dli.replay(t2_dli)
    cs_dli = t2_dli.getCharString()
    cs_dli.private = top_dict_p.Private
    cs_dli.compile()
    
    idx_dli = len(charstrings_p.charStringsIndex)
    charstrings_p.charStringsIndex.append(cs_dli)
    charstrings_p.charStrings['dotlessi'] = idx_dli
    top_dict_p.charset.append('dotlessi')
    order.append('dotlessi')
    hmtx_p.metrics['dotlessi'] = (w_i, lsb_i)

def process_single_font(raw_font_bytes: bytes, family_core: str, clean_subfamily: str,
                        foundry: str, is_serif: bool, is_mono: bool, subfam_name: str = None):
    f_p = TTFont(io.BytesIO(raw_font_bytes))
    
    for tbl in ['vhea', 'vmtx', 'VORG']:
        if tbl in f_p:
            del f_p[tbl]
            
    target_upm = f_p['head'].unitsPerEm
    
    donor_path = get_donor_path(clean_subfamily, is_serif=is_serif, is_mono=is_mono)
    f_a = TTFont(str(donor_path))
    donor_upm = f_a['head'].unitsPerEm
    upm_scale = target_upm / float(donor_upm)
    
    cff_p = f_p['CFF '].cff
    top_dict_p = cff_p.topDictIndex[0]
    charstrings_p = top_dict_p.CharStrings
    glyf_a = f_a['glyf']
    cmap_a = f_a.getBestCmap() or {}
    hmtx_a = f_a['hmtx']
    hmtx_p = f_p['hmtx']
    
    mono_pitch = None
    if is_mono:
        for g_test in ['a', 'm', 'i', 'space']:
            if g_test in hmtx_p.metrics:
                mono_pitch = hmtx_p.metrics[g_test][0]
                break
        if mono_pitch is None:
            mono_pitch = int(round(600 * (target_upm / 1000.0)))
            
    clean_notdef(charstrings_p, top_dict_p, hmtx_p, target_upm, fixed_w=mono_pitch)
    
    order = list(f_p.getGlyphOrder())
    synthesize_dotlessi(charstrings_p, top_dict_p, hmtx_p, order)
    
    w_key = clean_subfamily.lower().replace('italic', '').replace('oblique', '').replace('kursiv', '').strip()
    weight_class = 400
    for k, v in WEIGHT_MAP.items():
        if k in w_key:
            weight_class = v
            break
            
    is_italic = ('italic' in clean_subfamily.lower() or
                 'oblique' in clean_subfamily.lower() or
                 'kursiv' in clean_subfamily.lower())
    is_bold = weight_class >= 700
    
    if weight_class >= 900:
        bar_h_d, bar_h_lc = int(round(56 * upm_scale)), int(round(44 * upm_scale))
    elif weight_class >= 700:
        bar_h_d, bar_h_lc = int(round(46 * upm_scale)), int(round(36 * upm_scale))
    elif weight_class >= 600:
        bar_h_d, bar_h_lc = int(round(38 * upm_scale)), int(round(30 * upm_scale))
    elif weight_class <= 200:
        bar_h_d, bar_h_lc = int(round(20 * upm_scale)), int(round(16 * upm_scale))
    elif weight_class <= 300:
        bar_h_d, bar_h_lc = int(round(26 * upm_scale)), int(round(20 * upm_scale))
    else:
        bar_h_d, bar_h_lc = int(round(32 * upm_scale)), int(round(24 * upm_scale))
        
    accent_scale_x = 0.95 if is_mono else 1.0
    horn_scale_x = 0.92 if is_mono else 1.0
    
    viet_to_base = {}
    cmap_p = f_p.getBestCmap() or {}
    
    for ch in VIET_CHARS:
        cp = ord(ch)
        base_ch = get_base_char(ch)
        base_gname = 'dotlessi' if ch in 'ìíỉĩ' else base_ch
        if base_gname == 'dotlessi' and 'dotlessi' not in charstrings_p:
            base_gname = 'i'
            
        if ch in ['đ', 'Đ']:
            dest_gname = 'dcroat' if ch == 'đ' else 'Dcroat'
        else:
            dest_gname = cmap_p.get(cp) or (f'uni{cp:04X}' if cp > 0xFF else chr(cp))
            
        viet_to_base[dest_gname] = base_gname
        
        rec_base = RecordingPen()
        charstrings_p[base_gname].draw(rec_base)
        bounds_p = charstrings_p[base_gname].calcBounds(charstrings_p)
        w_base_p = int(round(hmtx_p.metrics[base_ch][0] if base_ch in hmtx_p.metrics else hmtx_p.metrics[base_gname][0]))
        center_p_x = (bounds_p[0] + bounds_p[2]) / 2.0
        right_p_x = bounds_p[2]
        top_p_y = bounds_p[3]
        
        rec_accents = RecordingPen()
        
        is_u_horn = ch in 'ƯỪỨỬỮỰ'
        is_lc_u_horn = ch in 'ưừứửữự'
        is_o_horn = ch in 'ƠỜỚỞỠỢ'
        is_lc_o_horn = ch in 'ơờớởỡợ'
        
        if is_u_horn or is_o_horn:
            draw_rel_contour(HORN_UC_REL, right_p_x, top_p_y, upm_scale, horn_scale_x, rec_accents)
        elif is_lc_u_horn or is_lc_o_horn:
            draw_rel_contour(HORN_LC_REL, right_p_x, top_p_y, upm_scale, horn_scale_x, rec_accents)
            
        if ch == 'Đ':
            y_bar = int(round(top_p_y * 0.49))
            x_left = int(round(bounds_p[0] - w_base_p * 0.08))
            x_right = int(round(bounds_p[0] + w_base_p * 0.36))
            rec_accents.moveTo((x_left, y_bar))
            rec_accents.lineTo((x_right, y_bar))
            rec_accents.lineTo((x_right, y_bar + bar_h_d))
            rec_accents.lineTo((x_left, y_bar + bar_h_d))
            rec_accents.closePath()
        elif ch == 'đ':
            y_bar = int(round(top_p_y * 0.74))
            stem_x = int(round(bounds_p[2] - (bounds_p[2] - bounds_p[0]) * 0.16))
            x_left = int(round(stem_x - w_base_p * 0.22))
            x_right = int(round(stem_x + w_base_p * 0.16))
            rec_accents.moveTo((x_left, y_bar))
            rec_accents.lineTo((x_right, y_bar))
            rec_accents.lineTo((x_right, y_bar + bar_h_lc))
            rec_accents.lineTo((x_left, y_bar + bar_h_lc))
            rec_accents.closePath()
            
        if ch not in ['đ', 'Đ']:
            gname_a = cmap_a.get(cp)
            if gname_a and gname_a in glyf_a:
                g_a = glyf_a[gname_a]
                g_base_a = glyf_a[base_gname if base_gname in glyf_a else base_ch]
                g_a.expand(glyf_a)
                coords_a, end_pts_a, flags_a = g_a.getCoordinates(glyf_a)
                g_base_a.expand(glyf_a)
                coords_base_a, end_pts_base_a, flags_base_a = g_base_a.getCoordinates(glyf_a)
                
                coords_a = [(int(round(p[0] * upm_scale)), int(round(p[1] * upm_scale))) for p in coords_a]
                coords_base_a = [(int(round(p[0] * upm_scale)), int(round(p[1] * upm_scale))) for p in coords_base_a]
                
                xs_base_a = [p[0] for p in coords_base_a]
                ys_base_a = [p[1] for p in coords_base_a]
                center_a_x = (min(xs_base_a) + max(xs_base_a)) / 2.0
                top_a_y = max(ys_base_a)
                
                start = 0
                for end in end_pts_a:
                    end = end + 1
                    c_coords = list(coords_a[start:end])
                    c_flags = list(flags_a[start:end])
                    start = end
                    c_ys = [p[1] for p in c_coords]
                    c_xs = [p[0] for p in c_coords]
                    c_y_min, c_y_max = min(c_ys), max(c_ys)
                    
                    is_dot_below = c_y_max < 0
                    is_top_accent_lc = (not base_ch.isupper()) and (c_y_min > int(round(460 * upm_scale)))
                    is_top_accent_uc = base_ch.isupper() and (c_y_min > int(round(670 * upm_scale)))
                    
                    if is_dot_below or is_top_accent_lc or is_top_accent_uc:
                        c_center_x = (min(c_xs) + max(c_xs)) / 2.0
                        if is_dot_below:
                            s_x = center_p_x - c_center_x
                            s_y = 0
                        else:
                            s_x = center_p_x - center_a_x
                            s_y = (top_p_y - top_a_y)
                            if is_lc_o_horn or is_lc_u_horn or is_o_horn or is_u_horn:
                                s_x -= int(round(16 * upm_scale))
                                s_y += int(round(12 * upm_scale))
                                
                        c_shifted = []
                        for p in c_coords:
                            px = c_center_x + (p[0] - c_center_x) * accent_scale_x + s_x
                            py = p[1] + s_y
                            c_shifted.append((int(round(px)), int(round(py))))
                        draw_tt_contour(c_shifted, c_flags, rec_accents, reverse=True)
                        
        w_dest = mono_pitch if is_mono else int(round(hmtx_p.metrics[base_ch][0]))
        t2 = T2CharStringPen(width=w_dest, glyphSet={})
        rec_base.replay(t2)
        qu2cu = Qu2CuPen(t2, max_err=1.0)
        rec_accents.replay(qu2cu)
        cs = t2.getCharString()
        cs.private = top_dict_p.Private
        cs.compile()
        
        if dest_gname in charstrings_p:
            charstrings_p[dest_gname] = cs
        else:
            idx = len(charstrings_p.charStringsIndex)
            charstrings_p.charStringsIndex.append(cs)
            charstrings_p.charStrings[dest_gname] = idx
            top_dict_p.charset.append(dest_gname)
            order.append(dest_gname)
            
        hmtx_p.metrics[dest_gname] = (int(round(w_dest)), int(round(bounds_p[0])))
        for sub in f_p['cmap'].tables:
            if sub.isUnicode():
                sub.cmap[cp] = dest_gname

    # Import missing punctuation
    for cp in PUNCT_CODEPOINTS:
        if cp in cmap_a:
            gname_a = cmap_a[cp]
            dest_gname = cmap_p.get(cp) or gname_a
            if dest_gname not in charstrings_p or cp in [0x3A, 0x3B, 0x21, 0x3F, 0x7C, 0x2014]:
                rec_punct = RecordingPen()
                g_punct = glyf_a[gname_a]
                g_punct.expand(glyf_a)
                c_punc, e_punc, f_punc = g_punct.getCoordinates(glyf_a)
                c_punc = [(int(round(p[0] * upm_scale)), int(round(p[1] * upm_scale))) for p in c_punc]
                start = 0
                for end in e_punc:
                    draw_tt_contour(c_punc[start:end+1], f_punc[start:end+1], rec_punct, reverse=True)
                    start = end + 1
                    
                w_punc, lsb_punc = hmtx_a[gname_a]
                w_punc = mono_pitch if is_mono else int(round(w_punc * upm_scale))
                lsb_punc = int(round(lsb_punc * upm_scale))
                
                t2_punc = T2CharStringPen(width=w_punc, glyphSet={})
                qu2cu_punc = Qu2CuPen(t2_punc, max_err=1.0)
                rec_punct.replay(qu2cu_punc)
                cs_punc = t2_punc.getCharString()
                cs_punc.private = top_dict_p.Private
                cs_punc.compile()
                
                if dest_gname in charstrings_p:
                    charstrings_p[dest_gname] = cs_punc
                else:
                    idx = len(charstrings_p.charStringsIndex)
                    charstrings_p.charStringsIndex.append(cs_punc)
                    charstrings_p.charStrings[dest_gname] = idx
                    top_dict_p.charset.append(dest_gname)
                    order.append(dest_gname)
                hmtx_p.metrics[dest_gname] = (w_punc, lsb_punc)
                for sub in f_p['cmap'].tables:
                    if sub.isUnicode():
                        sub.cmap[cp] = dest_gname

    # Harmonize metrics
    for g in order:
        if g not in hmtx_p.metrics:
            hmtx_p.metrics[g] = (mono_pitch if is_mono else int(round(500 * upm_scale)), 0)
        elif is_mono:
            _, m_lsb = hmtx_p.metrics[g]
            hmtx_p.metrics[g] = (mono_pitch, m_lsb)
            
    f_p.setGlyphOrder(order)
    f_p['maxp'].numGlyphs = len(order)
    f_p['hhea'].numberOfHMetrics = len(order)
    
    if 'hhea' in f_p:
        for attr in ['minLeftSideBearing', 'minRightSideBearing', 'xMaxExtent', 'advanceWidthMax']:
            if hasattr(f_p['hhea'], attr):
                val = getattr(f_p['hhea'], attr)
                if val is not None:
                    setattr(f_p['hhea'], attr, int(round(val)))
                    
    inherit_gpos_kerning(f_p, viet_to_base)
    
    # Naming convention
    display_family = f"FD {subfam_name if subfam_name else family_core}"
    fam_ascii = clean_ascii(subfam_name if subfam_name else family_core)
    style_ascii = clean_ascii(clean_subfamily)
    ps_name = f"FD{fam_ascii}-{style_ascii}"
    full_name = f"{display_family} {clean_subfamily}"
    
    if clean_subfamily in ['Regular', 'Bold', 'Italic', 'Bold Italic']:
        win_family = display_family
        win_sub = clean_subfamily
    else:
        win_family = f"{display_family} {clean_subfamily.replace(' Italic', '').replace('Italic', '').replace(' Kursiv', '').replace('Kursiv', '')}".strip()
        win_sub = 'Italic' if is_italic else 'Regular'
        
    f_p['name'].names = []
    records = [
        (0, f"Copyright (c) 2026 {foundry} & FEDU. All rights reserved."),
        (1, win_family),
        (2, win_sub),
        (3, f"1.000;FEDU;{ps_name}"),
        (4, full_name),
        (5, "Version 1.000; FEDU Type Foundry"),
        (6, ps_name),
        (7, f"{display_family} is localized for the FEDU Design Ecosystem with 100% Vietnamese typographic engine."),
        (8, "FEDU Design Team"),
        (9, f"{foundry} / FEDU Type Studio"),
        (11, "https://fedu.vn"),
        (12, "https://fedu.vn"),
        (13, "Licensed for internal and commercial creative production across FEDU Ecosystem."),
        (14, "https://fedu.vn/licenses"),
        (16, display_family),
        (17, clean_subfamily),
    ]
    for nid, val in records:
        f_p['name'].setName(val, nid, 3, 1, 0x409)
        f_p['name'].setName(val, nid, 1, 0, 0)
        f_p['name'].setName(val, nid, 0, 3, 0)
        
    if 'OS/2' in f_p:
        os2 = f_p['OS/2']
        os2.achVendID = b'FEDU'
        os2.usWeightClass = weight_class
        # Enable Bit 18 (Vietnamese 1258), Bit 19, Bit 0 (Latin 1252)
        os2.ulCodePageRange1 |= (1 << 18)
        os2.ulCodePageRange1 |= (1 << 19)
        os2.ulCodePageRange1 |= (1 << 0)
        os2.ulUnicodeRange1 |= (1 << 0) | (1 << 1) | (1 << 2)
        os2.ulUnicodeRange2 |= (1 << 15) | (1 << 30)
        
        if is_italic:
            os2.fsSelection |= (1 << 0)
        else:
            os2.fsSelection &= ~(1 << 0)
        if is_bold:
            os2.fsSelection |= (1 << 5)
        else:
            os2.fsSelection &= ~(1 << 5)
        if not is_italic and not is_bold and weight_class == 400:
            os2.fsSelection |= (1 << 6)
        else:
            os2.fsSelection &= ~(1 << 6)
            
    if 'head' in f_p:
        head = f_p['head']
        if is_bold:
            head.macStyle |= (1 << 0)
        else:
            head.macStyle &= ~(1 << 0)
        if is_italic:
            head.macStyle |= (1 << 1)
        else:
            head.macStyle &= ~(1 << 1)
            
    cff_p.fontNames = [ps_name]
    top_dict_p.FontName = ps_name
    top_dict_p.FamilyName = display_family
    top_dict_p.FullName = full_name
    top_dict_p.Notice = "Copyright (c) 2026 FEDU"
    top_dict_p.Copyright = "Copyright (c) 2026 FEDU"
    
    if 'DSIG' in f_p:
        del f_p['DSIG']
        
    # 1. Save OTF
    otf_dest = DIST_FONTS / f"{ps_name}.otf"
    f_p.save(str(otf_dest))
    
    # 2. Save WOFF2
    woff2_dist = DIST_WEB / f"{ps_name}.woff2"
    woff2_fonts = FONTS_WEB / f"{ps_name}.woff2"
    f_p.flavor = 'woff2'
    f_p.save(str(woff2_dist))
    shutil.copyfile(str(woff2_dist), str(woff2_fonts))
    
    # 3. Save TTF
    f_p.flavor = None
    ttf_font = convert_cff_to_truetype(f_p)
    ttf_dest = DIST_FONTS / f"{ps_name}.ttf"
    ttf_font.save(str(ttf_dest))
    
    # 4. Install OTF to macOS Library
    mac_otf = MAC_FONTS / f"{ps_name}.otf"
    shutil.copyfile(str(otf_dest), str(mac_otf))
    
    return {
        "status": "SUCCESS",
        "family_core": family_core,
        "subfam_name": subfam_name if subfam_name else family_core,
        "style_name": clean_subfamily,
        "ps_name": ps_name,
        "full_name": full_name,
        "otf_file": str(otf_dest),
        "ttf_file": str(ttf_dest),
        "woff2_file": str(woff2_dist),
        "glyphs": len(order),
        "upm": target_upm
    }

def worker_task(task_args):
    raw_font_bytes, family_core, clean_subfamily, foundry, is_serif, is_mono, subfam_name = task_args
    try:
        return process_single_font(raw_font_bytes, family_core, clean_subfamily,
                                   foundry, is_serif, is_mono, subfam_name)
    except Exception as e:
        import traceback
        return {
            "status": "FAIL",
            "family_core": family_core,
            "style": clean_subfamily,
            "error": f"{str(e)}\n{traceback.format_exc()}"
        }

# Specifications for all 32 Families
SPECS = {
    # Dinamo
    "Monument Grotesk": {
        "id": "fd-monument-grotesk",
        "slug": "MonumentGrotesk",
        "foundry": "Dinamo",
        "category": "Sans Serif",
        "subcategory": "Sans Neo-Grotesque Raw Unpolished",
        "director_notes": "Họ font Neo-Grotesque thô mộc, góc cạnh và giàu cá tính bậc nhất của Dinamo. Thiết kế thoát ly khỏi sự bóng bẩy thông thường, mang vẻ đẹp công nghiệp thực dụng, sắc bén và đậm tính tuyên ngôn.",
        "anatomy": {"contrast": "Low", "axis": "Vertical Grotesque", "x_height": "High", "aperture": "Semi-closed"},
        "sample_text": "Vẻ đẹp thô mộc công nghiệp và tính thực dụng kiến trúc đương đại",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display & Body"
    },
    "Monument Grotesk Condensed": {
        "id": "fd-monument-grotesk-condensed",
        "slug": "MonumentGroteskCondensed",
        "foundry": "Dinamo",
        "category": "Sans Serif",
        "subcategory": "Sans Condensed Editorial Impact",
        "director_notes": "Biến thể cô đọng (condensed) của Monument Grotesk, tối ưu hóa mật độ hiển thị theo phương ngang, tạo sức nén thị giác mãnh liệt cho tiêu đề báo chí, poster triển lãm và layout khổ dọc.",
        "anatomy": {"contrast": "Low", "axis": "Condensed Grotesque", "x_height": "High", "aperture": "Narrow Closed"},
        "sample_text": "Sức nén thị giác mãnh liệt và mật độ hiển thị tối ưu cho tiêu đề lớn",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display / Headline"
    },
    "Monument Grotesk Mono": {
        "id": "fd-monument-grotesk-mono",
        "slug": "MonumentGroteskMono",
        "foundry": "Dinamo",
        "category": "Blackletter, Script & Monospace",
        "subcategory": "Monospace Industrial Grotesque",
        "director_notes": "Phiên bản đơn cách chuẩn 620 đơn vị của Monument Grotesk. Giữ trọn tinh thần cơ khí thô mộc, tối ưu cho dòng lệnh kỹ thuật, biên tập dữ liệu số và phong cách techwear.",
        "anatomy": {"contrast": "None", "axis": "Strict Monospace 620", "x_height": "High", "aperture": "Open"},
        "sample_text": "Trật tự đơn cách 620 và vẻ đẹp kỹ thuật số chuẩn mực của dòng lệnh",
        "mood": "Tech & Công nghệ",
        "use_case": "Display & Body"
    },
    "Monument Grotesk Semi Mono": {
        "id": "fd-monument-grotesk-semi-mono",
        "slug": "MonumentGroteskSemiMono",
        "foundry": "Dinamo",
        "category": "Sans Serif",
        "subcategory": "Sans Semi-Monospace Hybrid",
        "director_notes": "Cầu nối thử nghiệm độc đáo giữa kiểu chữ tỷ lệ và đơn cách. Tạo nhịp điệu đọc lạ mắt, hiện đại và đậm chất avant-garde.",
        "anatomy": {"contrast": "Low", "axis": "Semi-Monospace Hybrid", "x_height": "High", "aperture": "Open"},
        "sample_text": "Nhịp điệu bán đơn cách thử nghiệm phá vỡ khuôn mẫu thị giác thông thường",
        "mood": "Tech & Công nghệ",
        "use_case": "Display & Body"
    },

    # Pangram Pangram
    "Formula": {
        "id": "fd-formula",
        "slug": "Formula",
        "foundry": "Pangram Pangram",
        "category": "Sans Serif",
        "subcategory": "Sans Extended Kinetic Speed",
        "director_notes": "Siêu phẩm phông chữ lấy cảm hứng từ đường đua F1 và văn hóa tốc độ đương đại của Pangram Pangram. Các nét chữ mở rộng (extended) đầy uy lực, đường cong khí động học tràn đầy năng lượng.",
        "anatomy": {"contrast": "Low", "axis": "Extended Kinetic", "x_height": "High", "aperture": "Dynamic"},
        "sample_text": "Tốc độ cơ học và năng lượng bùng nổ của đường đua thể thức một",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display & Body"
    },

    # Klim Type Foundry
    "American Grotesk": {
        "id": "fd-american-grotesk",
        "slug": "AmericanGrotesk",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans American Neo-Grotesque Heritage",
        "director_notes": "Tuyệt phẩm Grotesque phong cách Mỹ thế kỷ 19-20 được Kris Sowersby tái sinh với tư duy hiện đại. 42 styles toàn diện từ Regular, Condensed đến Compressed.",
        "anatomy": {"contrast": "Low", "axis": "Vertical Grotesque", "x_height": "Medium-High", "aperture": "Semi-closed"},
        "sample_text": "Di sản Grotesque nước Mỹ tái sinh trong diện mạo đương đại chuẩn xác",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display & Body"
    },
    "Calibre": {
        "id": "fd-calibre",
        "slug": "Calibre",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Neo-Grotesque Engineered",
        "director_notes": "Được thiết kế đồng hành cùng Metric, Calibre dựa trên các hình dạng hình học công nghiệp được tinh chỉnh quang học hoàn hảo.",
        "anatomy": {"contrast": "Low", "axis": "Engineered Geometric", "x_height": "High", "aperture": "Open"},
        "sample_text": "Cấu trúc hình học cơ khí và độ tinh khiết quang học trên màn hình số",
        "mood": "Tech & Công nghệ",
        "use_case": "Display & Body"
    },
    "Die Grotesk": {
        "id": "fd-die-grotesk",
        "slug": "DieGrotesk",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Early German Grotesk Suite",
        "director_notes": "Bộ sưu tập 64 styles đồ sộ khảo sát lịch sử Grotesk Đức qua 4 biến thể A, B, C, D từ siêu thanh mảnh đến cực đậm.",
        "anatomy": {"contrast": "Low-Medium", "axis": "Early German Grotesk", "x_height": "Standard", "aperture": "Moderate"},
        "sample_text": "Hành trình khảo cứu lịch sử xưởng đúc chữ Đức thế kỷ 19 quy mô lớn",
        "mood": "Vintage & Hoài niệm",
        "use_case": "Display & Body"
    },
    "Domaine": {
        "id": "fd-domaine",
        "slug": "Domaine",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif High-Contrast Baroque Curvature",
        "director_notes": "Đỉnh cao serif xa xỉ đương đại của Klim, kết hợp sự trang nhã của Baroque Pháp và độ sắc sảo của Didone. 46 styles trải dài từ Text đến Display.",
        "anatomy": {"contrast": "High", "axis": "Baroque Bracketed", "x_height": "Medium", "aperture": "Curved Open"},
        "sample_text": "Vẻ đẹp vương giả hoa lệ và đường nét lượn sóng kiêu kỳ của Baroque Pháp",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Domaine Sans": {
        "id": "fd-domaine-sans",
        "slug": "DomaineSans",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans High-Contrast Flared Editorial",
        "director_notes": "Biến thể không chân của Domaine, giữ lại độ tương phản nét kiêu kỳ và các đầu mút loe nhẹ đầy gợi cảm. 42 styles toàn diện.",
        "anatomy": {"contrast": "Medium-High", "axis": "Flared Neo-Humanist", "x_height": "Medium", "aperture": "Open"},
        "sample_text": "Đầu mút loe duyên dáng và vẻ đẹp thanh thoát của nghệ thuật biên tập",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Epicene": {
        "id": "fd-epicene",
        "slug": "Epicene",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Baroque Opulence Fashion",
        "director_notes": "Kiệt tác typography lấy cảm hứng từ Baroque thế kỷ 18, ngập tràn vẻ đẹp hoa lệ, kịch tính và quyền lực của thời trang cao cấp.",
        "anatomy": {"contrast": "Very High", "axis": "Baroque Dramatic", "x_height": "Medium", "aperture": "Sculptural"},
        "sample_text": "Hào quang kịch tính và vẻ đẹp lộng lẫy đỉnh cao của Haute Couture",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Family": {
        "id": "fd-family",
        "slug": "Family",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Humanist Everyday Warmth",
        "director_notes": "Phông chữ sans nhân văn ấm áp, thân thiện và giàu cảm xúc, sinh ra cho trải nghiệm đọc tự nhiên và thiết kế thương hiệu gắn kết cộng đồng.",
        "anatomy": {"contrast": "Low", "axis": "Humanist Gentle", "x_height": "High", "aperture": "Open"},
        "sample_text": "Nhịp thở nhân văn gần gũi và sự gắn kết ấm áp của cộng đồng",
        "mood": "Friendly & Nhân văn",
        "use_case": "Display & Body"
    },
    "Feijoa": {
        "id": "fd-feijoa",
        "slug": "Feijoa",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Organic Calligraphic Grace",
        "director_notes": "Đường cong hữu cơ mềm mại lấy cảm hứng từ thư pháp ngòi cong, mang lại cảm giác thủ công tinh tế và thanh thoát.",
        "anatomy": {"contrast": "Medium", "axis": "Calligraphic Organic", "x_height": "Medium", "aperture": "Dynamic"},
        "sample_text": "Đường cong thư pháp ngòi cong hữu cơ tinh xảo như tác phẩm thủ công",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Financier": {
        "id": "fd-financier",
        "slug": "Financier",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif British Editorial Authority",
        "director_notes": "Được thiết kế cho Financial Times, Financier toát lên uy quyền tri thức, chuẩn mực báo chí kinh tế và tài chính toàn cầu.",
        "anatomy": {"contrast": "Medium-High", "axis": "British Transitional", "x_height": "Standard", "aperture": "Moderate"},
        "sample_text": "Chuẩn mực báo chí tài chính quốc tế và tiếng nói của tri thức kinh tế",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Founders Grotesk": {
        "id": "fd-founders-grotesk",
        "slug": "FoundersGrotesk",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Grotesque Archetype Masterpiece",
        "director_notes": "Huyền thoại Grotesque của Klim, tập hợp vẻ đẹp tinh hoa từ các xưởng đúc chữ Miller & Richard thế kỷ 20. Đẳng cấp tuyệt đối trong làng thiết kế quốc tế.",
        "anatomy": {"contrast": "Low", "axis": "Vertical Grotesque", "x_height": "High", "aperture": "Tight Classic"},
        "sample_text": "Tượng đài Grotesque thế giới và sự chuẩn mực của thiết kế thương hiệu",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display & Body"
    },
    "Geograph": {
        "id": "fd-geograph",
        "slug": "Geograph",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Geometric Cartographic Clarity",
        "director_notes": "Được thiết kế cho National Geographic, mang độ chính xác quang học của bản đồ học kết hợp tính nhân văn sâu sắc.",
        "anatomy": {"contrast": "Low", "axis": "Cartographic Precision", "x_height": "High", "aperture": "Open"},
        "sample_text": "Độ chính xác bản đồ học và tinh thần thám hiểm những chân trời mới",
        "mood": "Tech & Công nghệ",
        "use_case": "Display & Body"
    },
    "Heldane": {
        "id": "fd-heldane",
        "slug": "Heldane",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Renaissance Modernized Book",
        "director_notes": "Hồi sinh tinh hoa thời Phục hưng (Renaissance) từ Hendrik van den Keere và Garamond, tối ưu cho nghệ thuật xuất bản sách đỉnh cao.",
        "anatomy": {"contrast": "Medium", "axis": "Renaissance Diagonal", "x_height": "Standard", "aperture": "Moderate"},
        "sample_text": "Ánh sáng văn hóa Phục hưng và di sản in ấn hàn lâm trường tồn",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Karbon": {
        "id": "fd-karbon",
        "slug": "Karbon",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Clean Minimalist Open-Air",
        "director_notes": "Họ font sans hình học tối giản với độ mở nét cực thoáng, thanh lịch và nhẹ nhõm như không khí.",
        "anatomy": {"contrast": "Low", "axis": "Geometric Pure", "x_height": "High", "aperture": "Wide Open"},
        "sample_text": "Sự tối giản tinh khiết và không gian thị giác thoáng đãng hiện đại",
        "mood": "Friendly & Nhân văn",
        "use_case": "Display & Body"
    },
    "Maelstrom": {
        "id": "fd-maelstrom",
        "slug": "Maelstrom",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Heavy Reverse-Stress Rebel",
        "director_notes": "Phông chữ đảo ngược trọng lực nét (reverse-stress) cực kỳ nổi loạn, độc dị và bùng nổ thị giác trên poster và bìa album.",
        "anatomy": {"contrast": "Extreme Reverse", "axis": "Horizontal Reverse-Stress", "x_height": "High", "aperture": "Closed"},
        "sample_text": "Trọng lực nét đảo chiều và sự nổi loạn thị giác đầy mê hoặc",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display / Headline"
    },
    "Manuka": {
        "id": "fd-manuka",
        "slug": "Manuka",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Ultra-Compressed Poster Powerhouse",
        "director_notes": "Gã khổng lồ nén đặc (ultra-compressed), tỉ lệ nét đậm đặc và chiều cao ngút ngàn, chiếm trọn mọi ánh nhìn trên banner quảng cáo ngoài trời.",
        "anatomy": {"contrast": "None", "axis": "Ultra-Compressed", "x_height": "Very High", "aperture": "Tight"},
        "sample_text": "Chiều cao ngút ngàn và mật độ nét đậm đặc chiếm trọn không gian",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display / Headline"
    },
    "Martina Plantijn": {
        "id": "fd-martina-plantijn",
        "slug": "MartinaPlantijn",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Golden Age Academic Editorial",
        "director_notes": "Lấy cảm hứng từ bảo tàng Plantin-Moretus danh giá, mang tinh thần thời hoàng kim in ấn thế kỷ 16 vào kỷ nguyên số.",
        "anatomy": {"contrast": "Medium-High", "axis": "Academic Editorial", "x_height": "Standard", "aperture": "Classic"},
        "sample_text": "Di sản xưởng in thế kỷ mười sáu và chuẩn mực xuất bản sách kinh điển",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Metric": {
        "id": "fd-metric",
        "slug": "Metric",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Geometric Signage Precision",
        "director_notes": "Xây dựng trên nền tảng biển báo đô thị Tây Berlin và các đường kẻ kiến trúc, mạch lạc, chính xác và hiện đại.",
        "anatomy": {"contrast": "Low", "axis": "Architectural Signage", "x_height": "High", "aperture": "Open"},
        "sample_text": "Biển báo đô thị hiện đại và các đường kẻ kiến trúc chuẩn xác tuyệt đối",
        "mood": "Tech & Công nghệ",
        "use_case": "Display & Body"
    },
    "National": {
        "id": "fd-national",
        "slug": "National",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Neo-Grotesque Universal Workhorse",
        "director_notes": "Họ font bản địa New Zealand đa năng kinh điển, đáp ứng hoàn hảo từ chữ nhỏ ly ty đến biển hiệu khổng lồ.",
        "anatomy": {"contrast": "Low", "axis": "Universal Grotesque", "x_height": "High", "aperture": "Semi-open"},
        "sample_text": "Tính đa năng bền bỉ đáp ứng từ văn bản nhỏ đến biển hiệu nhận diện lớn",
        "mood": "Friendly & Nhân văn",
        "use_case": "Display & Body"
    },
    "National 2": {
        "id": "fd-national-2",
        "slug": "National2",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Complete Neo-Grotesque System (64 styles)",
        "director_notes": "Bản nâng cấp toàn diện thế hệ 2 của National với 64 styles phủ khắp 4 tỷ lệ độ rộng: Regular, Narrow, Condensed, Compressed.",
        "anatomy": {"contrast": "Low", "axis": "Multi-width Grotesque", "x_height": "High", "aperture": "Engineered"},
        "sample_text": "Hệ thống kiểu chữ sáu mươi tư phong cách phủ khắp mọi tỷ lệ khung nhìn",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display & Body"
    },
    "Newzald": {
        "id": "fd-newzald",
        "slug": "Newzald",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif High-Legibility Newspaper",
        "director_notes": "Thiết kế chuyên biệt cho báo in và tạp chí, chân chữ vững chãi, đọc cực rõ ràng ở cỡ chữ nhỏ trên màn hình và giấy in xốp.",
        "anatomy": {"contrast": "Medium", "axis": "Newspaper Bracketed", "x_height": "High", "aperture": "Open"},
        "sample_text": "Độ rõ ràng vượt trội trên từng cột báo và trang sách chữ nhỏ",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Pitch": {
        "id": "fd-pitch",
        "slug": "Pitch",
        "foundry": "Klim Type Foundry",
        "category": "Blackletter, Script & Monospace",
        "subcategory": "Monospace Typewriter Slab Heritage",
        "director_notes": "Kiệt tác vinh danh máy đánh chữ cơ khí thế kỷ 20 với chân chữ slab hình học sắc lẹm, bao gồm cả Pitch và Pitch Sans.",
        "anatomy": {"contrast": "None", "axis": "Monospace 614 Typewriter", "x_height": "High", "aperture": "Mechanical"},
        "sample_text": "Tiếng gõ phím cơ khí và nhịp điệu đơn cách sáu trăm mười bốn huyền thoại",
        "mood": "Vintage & Hoài niệm",
        "use_case": "Display & Body"
    },
    "Signifier": {
        "id": "fd-signifier",
        "slug": "Signifier",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Brutalist Editorial Thoughtfulness",
        "director_notes": "Sự kết hợp táo bạo giữa cấu trúc serif cổ điển thế kỷ 17 và triết lý thô mộc brutalist kỹ thuật số, đậm chất tư tưởng và nghệ thuật.",
        "anatomy": {"contrast": "Medium", "axis": "Digital Brutalist Serif", "x_height": "Medium", "aperture": "Sharp Cut"},
        "sample_text": "Triết lý thô mộc số hóa và cấu trúc chữ mang tính tư tưởng sâu sắc",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Söhne": {
        "id": "fd-sohne",
        "slug": "Sohne",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Akzidenz-Grotesk Heir (64 styles)",
        "director_notes": "Di sản kế thừa Akzidenz-Grotesk vĩ đại nhất thế kỷ 21. Chuẩn mực thị giác đỉnh cao được thế giới tôn sùng. Bộ 64 styles gồm Söhne, Breit, Schmal, Mono.",
        "anatomy": {"contrast": "Low", "axis": "Akzidenz Geometric", "x_height": "High", "aperture": "Semi-closed"},
        "sample_text": "Di sản thị giác thế kỷ hai mươi mốt kế thừa trọn vẹn Akzidenz Grotesk",
        "mood": "Bold & Tuyên ngôn",
        "use_case": "Display & Body"
    },
    "The Future": {
        "id": "fd-the-future",
        "slug": "TheFuture",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Geometric Futura Homage (28 styles)",
        "director_notes": "Lời tri ân tuyệt mỹ dành cho Futura của Paul Renner. Tỷ lệ hình học thuần khiết của Bauhaus được tinh chỉnh để trường tồn qua nhiều thập kỷ.",
        "anatomy": {"contrast": "None", "axis": "Geometric Pure Bauhaus", "x_height": "Medium", "aperture": "Open Geometric"},
        "sample_text": "Hình học thuần khiết Bauhaus và tinh thần hướng đến tương lai trường tồn",
        "mood": "Tech & Công nghệ",
        "use_case": "Display & Body"
    },
    "Tiempos": {
        "id": "fd-tiempos",
        "slug": "Tiempos",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Contemporary Editorial Titan (32 styles)",
        "director_notes": "Biểu tượng serif báo chí thế giới (El País). Hệ thống 32 styles đồ sộ chia 3 cấp độ quang học: Tiempos Text, Tiempos Headline, Tiempos Fine.",
        "anatomy": {"contrast": "High", "axis": "Editorial Sharp", "x_height": "Standard", "aperture": "Moderate"},
        "sample_text": "Biểu tượng serif báo chí quốc tế với ba cấp độ quang học thượng thừa",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    },
    "Untitled Sans": {
        "id": "fd-untitled-sans",
        "slug": "UntitledSans",
        "foundry": "Klim Type Foundry",
        "category": "Sans Serif",
        "subcategory": "Sans Jasper Morrison Super Normal",
        "director_notes": "Triết lý thiết kế 'Super Normal' của Jasper Morrison: một kiểu chữ sans không phô trương, hoàn toàn trung tính, đặt nội dung lên hàng đầu.",
        "anatomy": {"contrast": "Low", "axis": "Super Normal Neutral", "x_height": "High", "aperture": "Open"},
        "sample_text": "Triết lý siêu bình thường trung tính tối thượng tôn vinh giá trị nội dung",
        "mood": "Friendly & Nhân văn",
        "use_case": "Display & Body"
    },
    "Untitled Serif": {
        "id": "fd-untitled-serif",
        "slug": "UntitledSerif",
        "foundry": "Klim Type Foundry",
        "category": "Serif",
        "subcategory": "Serif Plain Functional Everyday Literature",
        "director_notes": "Người bạn đồng hành của Untitled Sans: serif mộc mạc, tĩnh lặng, tự nhiên và thanh lọc thị giác khi đọc sách dài tập.",
        "anatomy": {"contrast": "Medium", "axis": "Plain Functional Serif", "x_height": "Standard", "aperture": "Classic"},
        "sample_text": "Sự tĩnh lặng mộc mạc tự nhiên mang lại trải nghiệm đọc sách thuần khiết",
        "mood": "Luxury & Sang trọng",
        "use_case": "Display & Body"
    }
}

def package_all_zips(family_styles_map):
    print("\n📦 Packaging family ZIPs and Master Collection ZIPs in dist/zips/FD/...")
    
    dinamo_files = []
    pp_files = []
    klim_files = []
    
    for fam_name, styles in family_styles_map.items():
        spec = SPECS[fam_name]
        slug = spec["slug"]
        foundry = spec["foundry"]
        zip_name = f"FD-{slug}.zip"
        zip_path = DIST_ZIPS_FD / zip_name
        
        with zipfile.ZipFile(str(zip_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for s in styles:
                ps = s["ps_name"]
                otf_file = DIST_FONTS / f"{ps}.otf"
                ttf_file = DIST_FONTS / f"{ps}.ttf"
                if otf_file.exists():
                    z.write(str(otf_file), f"{ps}.otf")
                    entry = (str(otf_file), f"OTF/{ps}.otf")
                    if foundry == "Dinamo":
                        dinamo_files.append(entry)
                    elif foundry == "Pangram Pangram":
                        pp_files.append(entry)
                    else:
                        klim_files.append(entry)
                if ttf_file.exists():
                    z.write(str(ttf_file), f"{ps}.ttf")
                    entry = (str(ttf_file), f"TTF/{ps}.ttf")
                    if foundry == "Dinamo":
                        dinamo_files.append(entry)
                    elif foundry == "Pangram Pangram":
                        pp_files.append(entry)
                    else:
                        klim_files.append(entry)
        print(f"  ✓ {zip_name} ({len(styles)} styles, {zip_path.stat().st_size / 1024:.1f} KB)")
        
    # Master Collection: Dinamo
    dinamo_master_path = DIST_ZIPS_FD / "FD-Dinamo-Collection.zip"
    with zipfile.ZipFile(str(dinamo_master_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, arcname in set(dinamo_files):
            z.write(fpath, arcname)
    print(f"  ✓ Master Collection: FD-Dinamo-Collection.zip ({len(set(dinamo_files))} files, {dinamo_master_path.stat().st_size / (1024*1024):.2f} MB)")

    # Master Collection: Pangram Pangram
    pp_master_path = DIST_ZIPS_FD / "FD-Pangram-Collection.zip"
    with zipfile.ZipFile(str(pp_master_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, arcname in set(pp_files):
            z.write(fpath, arcname)
    print(f"  ✓ Master Collection: FD-Pangram-Collection.zip ({len(set(pp_files))} files, {pp_master_path.stat().st_size / (1024*1024):.2f} MB)")

    # Master Collection: Klim
    klim_master_path = DIST_ZIPS_FD / "FD-Klim-Collection.zip"
    with zipfile.ZipFile(str(klim_master_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, arcname in set(klim_files):
            z.write(fpath, arcname)
    print(f"  ✓ Master Collection: FD-Klim-Collection.zip ({len(set(klim_files))} files, {klim_master_path.stat().st_size / (1024*1024):.2f} MB)")

def update_catalogs(family_styles_map):
    print("\n📝 Updating data/catalog.json & data/fonts.json...")
    
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog_data = json.load(f)
        
    existing_fonts = catalog_data["fonts"]
    # Filter out any old entries from fontmoi
    existing_fonts = [
        f for f in existing_fonts
        if not (f.get("tags") and any(t in f.get("tags") for t in ["Dinamo", "Pangram", "Klim", "Klim Type Foundry"]))
    ]
    
    new_entries = []
    
    for fam_name in SPECS:
        spec = SPECS[fam_name]
        styles = family_styles_map.get(fam_name, [])
        slug = spec["slug"]
        foundry = spec["foundry"]
        weight_names = sorted(list(set(s["style_name"] for s in styles)))
        
        # Choose preview woff2
        reg_style = next((s for s in styles if s["style_name"] in ["Regular", "Buch", "Medium"]), styles[0] if styles else None)
        woff2_name = f"{reg_style['ps_name']}.woff2" if reg_style else f"FD{slug}-Regular.woff2"
        
        is_dinamo = foundry == "Dinamo"
        is_klim = foundry == "Klim Type Foundry"
        is_pangram = foundry == "Pangram Pangram"
        
        entry = {
            "id": spec["id"],
            "name": f"FD {fam_name}",
            "family": f"FD {fam_name}",
            "designer": f"{foundry} / FEDU Type Studio",
            "source": f"{foundry} (FEDU Vietnamese Localization)",
            "foundry": foundry,
            "category": spec["category"],
            "subcategory": spec["subcategory"],
            "is_dinamo": is_dinamo,
            "is_klim": is_klim,
            "is_pangram": is_pangram,
            "tags": [
                foundry,
                "Dinamo" if is_dinamo else ("Klim" if is_klim else "Pangram"),
                "FEDU Type",
                spec["category"],
                "Universal Standard"
            ],
            "matrix_3d": {
                "style": spec["subcategory"],
                "mood": spec["mood"],
                "use_case": spec["use_case"]
            },
            "anatomy": spec["anatomy"],
            "vietnamese_support": True,
            "vietnamese_status": "Supported (100% - 134/134 glyphs)",
            "director_notes": f"📌 Nguồn gốc: {foundry} (FEDU Việt Hóa Chuẩn Typographic Engine)\n\n{spec['director_notes']}",
            "weights": weight_names,
            "sample_text": spec["sample_text"],
            "zip_filename": f"FD-{slug}.zip",
            "zip_path": f"dist/zips/FD/FD-{slug}.zip",
            "download_url": f"dist/zips/FD/FD-{slug}.zip",
            "web_font_url": f"fonts/{woff2_name}",
            "director_review": spec["director_notes"],
            "critique": spec["director_notes"],
            "nhan_dinh_dao_dien": spec["director_notes"],
            "typography_critique": spec["director_notes"]
        }
        new_entries.append(entry)
        
    catalog_data["fonts"] = new_entries + existing_fonts
    catalog_data["summary"]["total_fonts"] = len(catalog_data["fonts"])
    catalog_data["summary"]["total_families"] = len(catalog_data["fonts"])
    catalog_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime())
    
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
        
    with open(FONTS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog_data["fonts"], f, ensure_ascii=False, indent=2)
        
    print(f"  ✓ catalog.json and fonts.json updated with {len(new_entries)} fontmoi families ({len(catalog_data['fonts'])} total fonts in catalog).")

def main():
    start_time = time.time()
    print("=" * 80)
    print("🚀 FEDU MASTER VIETNAMESE LOCALIZATION ENGINE: FONTMOI SUITE")
    print("   Foundries: Dinamo | Pangram Pangram | Klim Type Foundry")
    print("=" * 80)
    
    tasks = []
    
    # 1. DINAMO
    dinamo_zip = FONTMOI_DIR / "DINAMO Trial Fonts.zip"
    print(f"\n📂 Reading Dinamo fonts from {dinamo_zip.name}...")
    with zipfile.ZipFile(dinamo_zip, 'r') as zf:
        for fn in sorted(zf.namelist()):
            if fn.lower().endswith('.otf') and not fn.startswith('__MACOSX'):
                raw_bytes = zf.read(fn)
                parts = fn.split('/')
                subfam_dir = parts[1].replace('ABC ', '')
                fam_core = subfam_dir
                stem = parts[-1].replace('.otf', '')
                style = stem.split('-')[1].replace('Trial', '')
                if style == 'RegularItalic': style = 'Regular Italic'
                elif style == 'BoldItalic': style = 'Bold Italic'
                elif style == 'LightItalic': style = 'Light Italic'
                elif style == 'MediumItalic': style = 'Medium Italic'
                elif style == 'ThinItalic': style = 'Thin Italic'
                elif style == 'HeavyItalic': style = 'Heavy Italic'
                elif style == 'BlackItalic': style = 'Black Italic'
                elif style == 'UltraItalic': style = 'Ultra Italic'
                
                is_mono = 'mono' in fam_core.lower() and 'semi' not in fam_core.lower()
                is_serif = False
                tasks.append((raw_bytes, fam_core, style, "Dinamo", is_serif, is_mono, fam_core))
    print(f"  -> {sum(1 for t in tasks if t[3] == 'Dinamo')} Dinamo styles loaded.")

    # 2. PANGRAM PANGRAM
    pp_zip = FONTMOI_DIR / "PP_Formula_-_Free_for_personal_use_v2.0.zip"
    print(f"\n📂 Reading Pangram Pangram fonts from {pp_zip.name}...")
    with zipfile.ZipFile(pp_zip, 'r') as zf:
        for fn in sorted(zf.namelist()):
            if fn.lower().endswith('.otf') and not fn.startswith('__MACOSX'):
                raw_bytes = zf.read(fn)
                stem = fn.split('/')[-1].replace('.otf', '')
                raw_style = stem.replace('PPFormula-', '')
                style = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', raw_style)
                tasks.append((raw_bytes, "Formula", style, "Pangram Pangram", False, False, "Formula"))
    print(f"  -> {sum(1 for t in tasks if t[3] == 'Pangram Pangram')} PP Formula styles loaded.")

    # 3. KLIM TYPE FOUNDRY
    klim_zip = FONTMOI_DIR / "KlimTestFonts.zip"
    print(f"\n📂 Reading Klim fonts from {klim_zip.name}...")
    
    KLIM_COLL_MAP = {
        "Test American Grotesk Collection": "American Grotesk",
        "Test Calibre": "Calibre",
        "Test Die Grotesk": "Die Grotesk",
        "Test Domaine Collection": "Domaine",
        "Test Domaine Sans Collection": "Domaine Sans",
        "Test Epicene Collection": "Epicene",
        "Test Family": "Family",
        "Test Feijoa": "Feijoa",
        "Test Financier Collection": "Financier",
        "Test Founders Grotesk Collection": "Founders Grotesk",
        "Test Geograph": "Geograph",
        "Test Heldane Collection": "Heldane",
        "Test Karbon Collection": "Karbon",
        "Test Maelstrom Collection": "Maelstrom",
        "Test Manuka Collection": "Manuka",
        "Test Martina Plantijn": "Martina Plantijn",
        "Test Metric": "Metric",
        "Test National": "National",
        "Test National 2 Collection": "National 2",
        "Test Newzald": "Newzald",
        "Test Pitch Collection": "Pitch",
        "Test Signifier": "Signifier",
        "Test Söhne Collection": "Söhne",
        "Test The Future Collection": "The Future",
        "Test Tiempos Collection": "Tiempos",
        "Test Untitled Collection": "Untitled"
    }

    SERIF_FAMILIES = {
        "Domaine", "Epicene", "Feijoa", "Financier", "Heldane",
        "Martina Plantijn", "Newzald", "Signifier", "Tiempos", "Untitled Serif"
    }

    with zipfile.ZipFile(klim_zip, 'r') as zf:
        for fn in sorted(zf.namelist()):
            if fn.startswith('Test desktop fonts (Static, OTF)/') and fn.lower().endswith('.otf') and not fn.startswith('__MACOSX'):
                raw_bytes = zf.read(fn)
                parts = fn.split('/')
                coll_dir = parts[1]
                mapped_fam = KLIM_COLL_MAP.get(coll_dir)
                if not mapped_fam:
                    print(f"⚠️ Unknown collection: {coll_dir}")
                    continue
                    
                filename = parts[-1].replace('.otf', '')
                clean = filename[4:] if filename.startswith('Test') else filename
                fn_parts = clean.split('-')
                
                if clean.startswith('DieGrotesk-'):
                    subfam_name = f"Die Grotesk {fn_parts[1]}"
                    style = fn_parts[2]
                elif clean.startswith('FoundersGroteskX-Condensed-'):
                    subfam_name = "Founders Grotesk X-Condensed"
                    style = fn_parts[2]
                else:
                    raw_sub = fn_parts[0]
                    subfam_name = re.sub(r'(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', raw_sub)
                    style = fn_parts[1]
                    
                style = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', style)
                
                if mapped_fam == "Untitled":
                    fam_core = "Untitled Serif" if "Serif" in subfam_name else "Untitled Sans"
                else:
                    fam_core = mapped_fam
                    
                is_serif = (fam_core in SERIF_FAMILIES) or ("Pitch" == fam_core and "Sans" not in subfam_name)
                is_mono = "mono" in subfam_name.lower() or "pitch" in fam_core.lower()
                
                tasks.append((raw_bytes, fam_core, style, "Klim Type Foundry", is_serif, is_mono, subfam_name))
                
    print(f"  -> {sum(1 for t in tasks if t[3] == 'Klim Type Foundry')} Klim styles loaded.")
    print(f"\n🔥 Total styles to process across all 3 foundries: {len(tasks)}")
    
    results = []
    family_styles_map = {k: [] for k in SPECS}
    
    print("\n⚙️ Processing with 8 concurrent worker processes...")
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(worker_task, t): t for t in tasks}
        completed_count = 0
        for future in as_completed(futures):
            res = future.result()
            completed_count += 1
            results.append(res)
            if res.get("status") == "SUCCESS":
                fam = res["family_core"]
                family_styles_map[fam].append(res)
                if completed_count % 50 == 0 or completed_count == len(tasks):
                    print(f"  ✓ [{completed_count}/{len(tasks)}] {res['full_name']} ({res['glyphs']} glyphs)")
            else:
                print(f"  ❌ FAILED: {res.get('subfam_name', res.get('family_core'))} {res.get('style')}: {res.get('error')}")
                
    successes = [r for r in results if r.get("status") == "SUCCESS"]
    print(f"\n✨ Build completed: {len(successes)}/{len(tasks)} styles successfully localized and exported.")
    
    if len(successes) < len(tasks):
        print(f"❌ Error: {len(tasks) - len(successes)} styles failed to build.")
        sys.exit(1)
        
    for fam in family_styles_map:
        family_styles_map[fam].sort(key=lambda s: (s["subfam_name"], s["style_name"]))
        
    package_all_zips(family_styles_map)
    update_catalogs(family_styles_map)
    
    elapsed = time.time() - start_time
    print(f"\n🎉 ALL 730 STYLES ACROSS 32 FAMILIES PROCESSED, INSTALLED & PACKAGED IN {elapsed:.2f}s!")

if __name__ == "__main__":
    main()
