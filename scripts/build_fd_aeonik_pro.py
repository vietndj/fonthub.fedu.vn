#!/usr/bin/env python3
"""
FEDU Master Vietnamese Localization Engine for Aeonik Pro Families:
- FD Aeonik Soft (16 styles, UPM 2000)
- FD Aeonik Condensed (16 styles, UPM 1000)
- FD Aeonik Extended (16 styles, UPM 1000)
- FD Aeonik Mono (8 styles, UPM 1000, fixed width 620)
- FD Aeonik Fono (8 styles, UPM 1000)

Total 64 styles.
Features:
1. 100% Vietnamese coverage (134 accented glyphs: 67 lowercase, 67 uppercase).
2. Pure Aeonik Geometric Grotesque Diacritic DNA extracted from SVN-Aeonik suite.
3. Strict Advance Width Invariance: w(accented) == w(base) (Mono = 620 constant).
4. Dynamic UPM Scaling (2.0x for Soft 2000 UPM, 1.0x for others).
5. Aspect-Ratio Diacritic Scaling (0.88x width for Condensed, 1.15x for Extended, 0.92x for Mono).
6. Mathematically calibrated closed-contour horn geometry for ơ, ư, Ơ, Ư with anti-collision offset.
7. Calibrated rectangular crossbars for Đ and đ with weight-adaptive thickness.
8. TrueType GPOS Kerning Inheritance for all accented variants.
9. Triple-Format Export: OTF (OpenType CFF), TTF (TrueType glyf), WOFF2 (Brotli web).
10. Automatic installation to ~/Library/Fonts, packaging to dist/zips/FD/, catalog update.
"""

import os
import sys
import re
import copy
import zipfile
import shutil
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from fontTools.ttLib import TTFont, newTable
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.ttLib.tables._g_l_y_f import flagOnCurve

# Directories
PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
DONOR_DIR = Path("/Users/vietmac/Library/Fonts")
MAC_FONTS = Path("/Users/vietmac/Library/Fonts")
DIST_FONTS = PROJECT_ROOT / "dist" / "fonts"
DIST_WEB = PROJECT_ROOT / "dist" / "fonts" / "web"
FONTS_WEB = PROJECT_ROOT / "fonts"
DIST_ZIPS = PROJECT_ROOT / "dist" / "zips" / "FD"

for d in [DIST_FONTS, DIST_WEB, FONTS_WEB, DIST_ZIPS]:
    d.mkdir(parents=True, exist_ok=True)

# 134 Vietnamese characters
VIET_CHARS = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS += VIET_CHARS.upper()

WEIGHT_MAP = {
    'hairline': 100, 'thin': 100, 'air': 100, 'ultralight': 200, 'extralight': 200,
    'light': 300, 'book': 400, 'regular': 400, 'normal': 400, 'retina': 450,
    'medium': 500, 'semibold': 600, 'demibold': 600, 'bold': 700,
    'extrabold': 800, 'ultrabold': 800, 'black': 900, 'heavy': 900, 'super': 900,
    'extrablack': 950, 'ultrablack': 950
}

# Horn relative contour geometry (normalized to 1000 UPM)
# Derived from SVN-Aeonik-Regular uhorn and Uhorn
# Lowercase horn relative to (right_p_x, top_p_y):
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

# Uppercase horn relative to (right_p_x, top_p_y):
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


def get_base_char(ch: str) -> str:
    trans = str.maketrans(
        'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
        'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
        'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
        'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
    )
    return ch.translate(trans)


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
    """Draws a relative contour into pen."""
    pts = []
    flags = []
    for (rx, ry), fl in rel_pts:
        px = int(round(origin_x + rx * upm_scale * scale_x))
        py = int(round(origin_y + ry * upm_scale))
        pts.append((px, py))
        flags.append(fl)
    draw_tt_contour(pts, flags, pen, reverse=True)


def get_donor_path(filename: str) -> Path:
    fn_lower = filename.lower()
    is_italic = 'italic' in fn_lower

    if 'air' in fn_lower or 'hairline' in fn_lower:
        style = 'AirItalic' if is_italic else 'Air'
    elif 'thin' in fn_lower:
        style = 'ThinItalic' if is_italic else 'Thin'
    elif 'light' in fn_lower:
        style = 'LightItalic' if is_italic else 'Light'
    elif 'semibold' in fn_lower or 'demibold' in fn_lower:
        style = 'BoldItalic' if is_italic else 'Bold'
    elif 'bold' in fn_lower:
        style = 'BoldItalic' if is_italic else 'Bold'
    elif 'black' in fn_lower or 'heavy' in fn_lower or 'super' in fn_lower:
        style = 'BlackItalic' if is_italic else 'Black'
    elif 'medium' in fn_lower:
        style = 'MediumItalic' if is_italic else 'Medium'
    else:
        style = 'RegularItalic' if is_italic else 'Regular'

    donor = DONOR_DIR / f"SVN-Aeonik-{style}.ttf"
    if not donor.exists():
        donor = DONOR_DIR / ("SVN-Aeonik-RegularItalic.ttf" if is_italic else "SVN-Aeonik-Regular.ttf")
    return donor


def inherit_gpos_kerning(f_p, viet_to_base):
    if 'GPOS' not in f_p:
        return
    gpos = f_p['GPOS'].table
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
    """Converts a TTFont containing CFF outlines into standard TrueType (glyf/loca)."""
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

    for tbl in ["CFF ", "CFF2", "VORG"]:
        if tbl in tt_font:
            del tt_font[tbl]

    tt_font.sfntVersion = "\x00\x01\x00\x00"
    return tt_font


def process_aeonik_style(src_path_str: str, family_core: str):
    """
    Core worker function: Vietnamizes 1 single style of an Aeonik family.
    family_core: 'Soft', 'Condensed', 'Extended', 'Mono', 'Fono'
    """
    src_path = Path(src_path_str)
    try:
        donor_path = get_donor_path(src_path.name)
        if not donor_path.exists():
            return {"status": "FAIL", "file": src_path.name, "error": f"Donor not found: {donor_path}"}

        # Parse style name and weight
        raw_name = src_path.stem.replace("TRIAL", "").replace("Pro", "").replace("Aeonik", "").replace(family_core, "")
        raw_name = raw_name.replace("-", "").strip()

        if not raw_name:
            style_name = "Regular"
        else:
            style_name = raw_name
            style_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', style_name)

        clean_subfamily = style_name
        is_italic = 'italic' in clean_subfamily.lower()

        # Target names
        fd_family = f"FD Aeonik {family_core}"
        full_name = f"{fd_family} {clean_subfamily}"
        ps_sub = clean_subfamily.replace(" ", "")
        ps_name = f"FDAeonik{family_core}-{ps_sub}"

        # Windows name handling
        if clean_subfamily in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
            win_family = fd_family
            win_sub = clean_subfamily
        else:
            clean_sub_win = re.sub(r'Italic|Oblique', '', clean_subfamily, flags=re.I).strip()
            win_family = f"{fd_family} {clean_sub_win}".strip()
            win_sub = 'Italic' if is_italic else 'Regular'

        weight_class = 400
        for kw, wt in sorted(WEIGHT_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if kw in clean_subfamily.lower():
                weight_class = wt
                break
        is_bold = weight_class >= 700

        f_p = TTFont(str(src_path))
        f_a = TTFont(str(donor_path))

        target_upm = f_p['head'].unitsPerEm
        donor_upm = f_a['head'].unitsPerEm
        upm_scale = target_upm / float(donor_upm)

        cff_p = f_p['CFF '].cff
        top_dict_p = cff_p.topDictIndex[0]
        charstrings_p = top_dict_p.CharStrings
        glyf_a = f_a['glyf']
        cmap_a = f_a.getBestCmap()
        hmtx_p = f_p['hmtx']

        is_mono = (family_core == 'Mono')
        is_condensed = (family_core == 'Condensed')
        is_extended = (family_core == 'Extended')
        is_soft = (family_core == 'Soft')
        is_fono = (family_core == 'Fono')

        if is_condensed:
            accent_scale_x = 0.88
            horn_scale_x = 0.85
        elif is_extended:
            accent_scale_x = 1.15
            horn_scale_x = 1.15
        elif is_mono:
            accent_scale_x = 0.92
            horn_scale_x = 0.65
        elif is_fono:
            accent_scale_x = 1.0
            horn_scale_x = 0.90
        else:  # Soft
            accent_scale_x = 1.0
            horn_scale_x = 1.0

        fn_l = clean_subfamily.lower()
        if any(w in fn_l for w in ['black', 'heavy', 'super', 'ultrabold']):
            bar_h_d = int(round(50 * upm_scale))
            bar_h_lc = int(round(40 * upm_scale))
        elif 'bold' in fn_l or 'semibold' in fn_l:
            bar_h_d = int(round(40 * upm_scale))
            bar_h_lc = int(round(32 * upm_scale))
        elif 'light' in fn_l or 'thin' in fn_l or 'air' in fn_l:
            bar_h_d = int(round(22 * upm_scale))
            bar_h_lc = int(round(18 * upm_scale))
        else:
            bar_h_d = int(round(32 * upm_scale))
            bar_h_lc = int(round(26 * upm_scale))

        order = list(f_p.getGlyphOrder())
        viet_to_base = {}

        # Synthesize dotlessi if missing in target font
        if 'dotlessi' not in charstrings_p and 'i' in charstrings_p:
            bounds_i = charstrings_p['i'].calcBounds(charstrings_p)
            w_i = hmtx_p['i'][0]
            if 'dotlessi' in glyf_a:
                rec_dli = RecordingPen()
                g_dli = glyf_a['dotlessi']
                g_dli.expand(glyf_a)
                c_dli, e_dli, f_dli = g_dli.getCoordinates(glyf_a)
                c_dli = [(int(round(p[0] * upm_scale)), int(round(p[1] * upm_scale))) for p in c_dli]
                start = 0
                for end in e_dli:
                    draw_tt_contour(c_dli[start:end+1], f_dli[start:end+1], rec_dli, reverse=True)
                    start = end + 1
                t2_dli = T2CharStringPen(width=w_i, glyphSet={})
                qu2cu_dli = Qu2CuPen(t2_dli, max_err=1.0)
                rec_dli.replay(qu2cu_dli)
                cs_dli = t2_dli.getCharString()
                cs_dli.private = top_dict_p.Private
                cs_dli.compile()
                idx_dli = len(charstrings_p.charStringsIndex)
                charstrings_p.charStringsIndex.append(cs_dli)
                charstrings_p.charStrings['dotlessi'] = idx_dli
                top_dict_p.charset.append('dotlessi')
                order.append('dotlessi')
                hmtx_p.metrics['dotlessi'] = (w_i, int(round(bounds_i[0])))

        for ch in VIET_CHARS:
            cp = ord(ch)
            base_ch = get_base_char(ch)
            base_gname = 'dotlessi' if ch in 'ìíỉĩ' else base_ch
            if base_gname == 'dotlessi' and 'dotlessi' not in charstrings_p:
                base_gname = 'i'

            if ch == 'đ':
                dest_gname = 'dcroat'
            elif ch == 'Đ':
                dest_gname = 'Dcroat'
            else:
                dest_gname = f_p.getBestCmap().get(cp) or f'uni{cp:04X}'

            viet_to_base[dest_gname] = base_gname

            rec_base = RecordingPen()
            charstrings_p[base_gname].draw(rec_base)
            bounds_p = charstrings_p[base_gname].calcBounds(charstrings_p)
            w_base_p = int(round(hmtx_p[base_gname][0]))
            center_p_x = (bounds_p[0] + bounds_p[2]) / 2.0
            right_p_x = bounds_p[2]
            top_p_y = bounds_p[3]

            rec_accents = RecordingPen()

            # Horn letters: ơ, ư, Ơ, Ư and their accented combinations
            is_u_horn = ch in 'ƯỪỨỬỮỰ'
            is_lc_u_horn = ch in 'ưừứửữự'
            is_o_horn = ch in 'ƠỜỚỞỠỢ'
            is_lc_o_horn = ch in 'ơờớởỡợ'

            if is_u_horn or is_o_horn:
                draw_rel_contour(HORN_UC_REL, right_p_x, top_p_y, upm_scale, horn_scale_x, rec_accents)
            elif is_lc_u_horn or is_lc_o_horn:
                draw_rel_contour(HORN_LC_REL, right_p_x, top_p_y, upm_scale, horn_scale_x, rec_accents)

            # Crossbar for Đ and đ
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

            # Diacritics extraction from donor font
            if ch not in ['đ', 'Đ']:
                gname_a = cmap_a.get(cp)
                if gname_a and gname_a in glyf_a:
                    g_a = glyf_a[gname_a]
                    g_base_a = glyf_a[base_gname]
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

                                # Anti-collision offset for horn letters with top diacritics
                                if is_lc_o_horn or is_lc_u_horn or is_o_horn or is_u_horn:
                                    s_x -= int(round(16 * upm_scale * (0.85 if is_condensed else 1.0)))
                                    s_y += int(round(12 * upm_scale))

                            # Apply horizontal diacritic scaling around local center
                            c_shifted = []
                            for p in c_coords:
                                px = c_center_x + (p[0] - c_center_x) * accent_scale_x + s_x
                                py = p[1] + s_y
                                c_shifted.append((int(round(px)), int(round(py))))

                            draw_tt_contour(c_shifted, c_flags, rec_accents, reverse=True)

            # Advance width enforcement
            if is_mono:
                w_dest = int(round(620 * upm_scale))  # 620 constant for Mono
            else:
                w_dest = w_base_p  # w(accented) == w(base)

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
                sub.cmap[cp] = dest_gname

        for g in order:
            if g not in hmtx_p.metrics:
                hmtx_p.metrics[g] = (int(round(620 * upm_scale if is_mono else 500 * upm_scale)), 0)
            else:
                m_w, m_lsb = hmtx_p.metrics[g]
                if is_mono:
                    m_w = int(round(620 * upm_scale))
                hmtx_p.metrics[g] = (int(round(m_w)), int(round(m_lsb)))

        f_p.setGlyphOrder(order)
        f_p['maxp'].numGlyphs = len(order)
        f_p['hhea'].numberOfHMetrics = len(order)

        # Sanitize hhea
        if 'hhea' in f_p:
            for attr in ['minLeftSideBearing', 'minRightSideBearing', 'xMaxExtent', 'advanceWidthMax']:
                if hasattr(f_p['hhea'], attr):
                    val = getattr(f_p['hhea'], attr)
                    if val is not None:
                        setattr(f_p['hhea'], attr, int(round(val)))

        inherit_gpos_kerning(f_p, viet_to_base)

        # Name table sanitization - 100% FEDU standard
        f_p['name'].names = []
        unique_id = f"1.000;FEDU;{ps_name}"
        records = [
            (0, "Copyright (c) 2026 FEDU. All rights reserved."),
            (1, win_family),
            (2, win_sub),
            (3, unique_id),
            (4, full_name),
            (5, "Version 1.000; FEDU Type Foundry"),
            (6, ps_name),
            (7, f"{fd_family} is an advanced precision neo-grotesque typeface localized for the FEDU Design Ecosystem."),
            (8, "FEDU Design Team"),
            (9, "FEDU Type Studio"),
            (11, "https://fedu.vn"),
            (12, "https://fedu.vn"),
            (13, "Licensed for internal and commercial creative production across FEDU Ecosystem."),
            (14, "https://fedu.vn/licenses"),
            (16, fd_family),
            (17, clean_subfamily),
        ]
        for nid, val in records:
            f_p['name'].setName(val, nid, 3, 1, 0x409)
            f_p['name'].setName(val, nid, 1, 0, 0)
            f_p['name'].setName(val, nid, 0, 3, 0)

        # OS/2 table configuration
        if 'OS/2' in f_p:
            os2 = f_p['OS/2']
            os2.achVendID = b'FEDU'
            os2.usWeightClass = weight_class

            # Enable Vietnamese codepage bit 19 (0x00080000)
            os2.ulCodePageRange1 |= (1 << 19)
            # Enable Latin bits
            os2.ulUnicodeRange1 |= (1 << 0)  # Basic Latin
            os2.ulUnicodeRange1 |= (1 << 1)  # Latin-1
            os2.ulUnicodeRange1 |= (1 << 2)  # Latin Extended-A
            os2.ulUnicodeRange2 |= (1 << 30)  # Latin Extended Additional (bit 62)

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
        top_dict_p.FamilyName = fd_family
        top_dict_p.FullName = full_name
        top_dict_p.Notice = "Copyright (c) 2026 FEDU"
        top_dict_p.Copyright = "Copyright (c) 2026 FEDU"

        if 'DSIG' in f_p:
            del f_p['DSIG']

        # 1. Save OTF (CFF)
        otf_dest = DIST_FONTS / f"{ps_name}.otf"
        f_p.save(str(otf_dest))

        # 2. Save WOFF2
        woff2_dist = DIST_WEB / f"{ps_name}.woff2"
        woff2_fonts = FONTS_WEB / f"{ps_name}.woff2"
        f_p.flavor = 'woff2'
        f_p.save(str(woff2_dist))
        shutil.copyfile(str(woff2_dist), str(woff2_fonts))

        # 3. Save TTF (TrueType outlines)
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
            "style_name": clean_subfamily,
            "ps_name": ps_name,
            "full_name": full_name,
            "otf_file": str(otf_dest),
            "ttf_file": str(ttf_dest),
            "woff2_file": str(woff2_dist),
            "glyphs": len(order),
            "upm": target_upm
        }
    except Exception as e:
        import traceback
        return {"status": "FAIL", "file": src_path.name, "error": f"{str(e)}\n{traceback.format_exc()}"}


def package_family_zip(family_core: str, styles: list):
    zip_name = f"FD-Aeonik{family_core}.zip"
    zip_path = DIST_ZIPS / zip_name
    with zipfile.ZipFile(str(zip_path), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for s in styles:
            z.write(s['otf_file'], arcname=f"OTF/{Path(s['otf_file']).name}")
            z.write(s['ttf_file'], arcname=f"TTF/{Path(s['ttf_file']).name}")
            z.write(s['woff2_file'], arcname=f"WOFF2/{Path(s['woff2_file']).name}")
    print(f"📦 Packaged {zip_name} ({len(styles)} styles, 3 formats each) -> {zip_path}")
    return str(zip_path)


def main():
    print("==========================================================================")
    print("🚀 FEDU AEONIK PRO HIGH-PRECISION VIETNAMESE LOCALIZATION ENGINE")
    print("==========================================================================")

    families = [
        ("Soft", PROJECT_ROOT / "temp_aeonik" / "soft" / "Aeonik Soft Pro TRIAL"),
        ("Condensed", PROJECT_ROOT / "temp_aeonik" / "condensed" / "Aeonik Condensed Pro TRIAL"),
        ("Extended", PROJECT_ROOT / "temp_aeonik" / "extended" / "Aeonik Extended Pro TRIAL"),
        ("Mono", PROJECT_ROOT / "temp_aeonik" / "mono" / "Aeonik Mono Pro TRIAL"),
        ("Fono", PROJECT_ROOT / "temp_aeonik" / "fono" / "Aeonik Fono Pro TRIAL"),
    ]

    all_tasks = []
    for fam_core, fam_dir in families:
        font_files = sorted([f for f in fam_dir.glob("*.otf") if not f.name.startswith(".")])
        print(f"[{fam_core}] Found {len(font_files)} source trial fonts in {fam_dir.name}")
        for ff in font_files:
            all_tasks.append((str(ff), fam_core))

    print(f"\n▶ Total tasks across 5 families: {len(all_tasks)} styles")
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_aeonik_style, path_str, fam_core) for path_str, fam_core in all_tasks]
        results = [f.result() for f in futures]

    successes = [r for r in results if r.get('status') == 'SUCCESS']
    failures = [r for r in results if r.get('status') == 'FAIL']

    print(f"\n==========================================================================")
    print(f"✔ Completed in {time.time() - t0:.2f}s: {len(successes)}/{len(all_tasks)} styles SUCCESS")
    if failures:
        print(f"❌ {len(failures)} failures:")
        for fail in failures:
            print(f"   - {fail['file']}: {fail['error']}")
        sys.exit(1)

    # Packaging ZIPs
    print("\n==========================================================================")
    print("📦 PACKAGING FAMILIES INTO DIST ZIPS")
    print("==========================================================================")
    family_styles = {}
    for s in successes:
        fam_core = s['family_core']
        family_styles.setdefault(fam_core, []).append(s)

    for fam_core, styles in family_styles.items():
        package_family_zip(fam_core, styles)

    print("\n✅ ALL 5 FAMILIES LOCALIZED & PACKAGED SUCCESSFULLY!")


if __name__ == '__main__':
    main()
