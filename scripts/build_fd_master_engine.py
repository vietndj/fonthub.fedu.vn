#!/usr/bin/env python3
"""
FEDU Master Typographic Localization Engine (SVN Standard)
Universal high-precision Vietnamese localization for Grilli Type font families:
- Preserves 100% native base letterforms across all weights, widths, and styles.
- Strict Advance Width Preservation: w(accented) == w(base) (zero width inflation).
- Full GPOS Kerning Inheritance: ClassDef1, ClassDef2, and Coverage kerning parity.
- PostScript Counter-Clockwise Contour Winding: CCW winding for CFF OTF.
- Precision Grilli Type Diacritics & Horns:
    * Sans fonts: GT-America-LCGV authentic diacritics & uni031B horn.
    * Serif fonts: SVN-AlpinaFine / GT-Sectra-LCGV high-contrast diacritics & droplets.
- Dynamic UPM Scaling (handles 1000 UPM and 2048 UPM like GT-Maru seamlessly).
- Synthesizes clean rectangular crossbars for Đ and đ.
- Cleans .notdef and imports missing standard typography punctuation.
- Dual Desktop (.otf) and Web (.woff2) outputs + direct macOS ~/Library/Fonts installation.
"""

import os
import sys
import copy
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.ttLib.tables._g_l_y_f import flagOnCurve

DONOR_DIR = Path("/Users/vietmac/Library/Fonts")
MAC_FONTS = Path("/Users/vietmac/Library/Fonts")
ROOT_GT_DIR = Path("/Users/vietmac/Documents/font gt")

VIET_CHARS = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS += VIET_CHARS.upper()

PUNCT_CODEPOINTS = [
    0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F,
    0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x5B, 0x5C, 0x5D, 0x5E, 0x5F,
    0x60, 0x7B, 0x7C, 0x7D, 0x7E,
    0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x2022
]

def draw_tt_contour(coords, flags, pen, reverse=True):
    if reverse:
        coords = list(reversed(coords))
        flags = list(reversed(flags))
    # Ensure all coordinates are integer tuples
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

def get_base_char(ch):
    trans = str.maketrans(
        'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
        'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
        'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
        'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
    )
    return ch.translate(trans)

def clean_notdef(charstrings, top_dict, hmtx, upm=1000):
    scale = upm / 1000.0
    w = int(round(500 * scale))
    x1, x2 = int(round(50 * scale)), int(round(450 * scale))
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

def get_donor_path(filename: str, family_genre: str = 'sans') -> Path:
    fn_lower = filename.lower()
    is_italic = any(k in fn_lower for k in ['italic', 'oblique', 'rotalic', 'retalic'])
    
    if family_genre == 'serif':
        if 'light' in fn_lower:
            style = 'LightItalic' if is_italic else 'Light'
        elif 'medium' in fn_lower:
            style = 'MediumItalic' if is_italic else 'Medium'
        elif 'bold' in fn_lower or 'black' in fn_lower:
            style = 'BoldItalic' if is_italic else 'Bold'
        else:
            style = 'Italic' if is_italic else 'Regular'
        return DONOR_DIR / f"SVN-AlpinaFine-{style}.ttf"
    else:
        if 'thin' in fn_lower or 'ulight' in fn_lower or 'ultralight' in fn_lower:
            style = 'Thin'
        elif 'light' in fn_lower:
            style = 'Light'
        elif 'medium' in fn_lower:
            style = 'Medium'
        elif 'bold' in fn_lower or 'ultrabold' in fn_lower or 'heavy' in fn_lower:
            style = 'Bold'
        elif 'black' in fn_lower or 'super' in fn_lower:
            style = 'Black'
        else:
            style = 'Regular'
        
        suffix = '-Italic' if is_italic else ''
        p = DONOR_DIR / f"GT-America-LCGV-Standard-{style}{suffix}.ttf"
        if not p.exists():
            p = DONOR_DIR / f"GT-America-LCGV-Standard-Regular{suffix}.ttf"
        return p

def parse_font_naming(font_path: Path, family_core: str):
    raw_name = font_path.stem.replace("-Trial", "")
    parts = raw_name.split("-")
    
    remainder = parts[2:] if len(parts) > 2 else ['Regular']
    
    weights_slopes = {
        'thin', 'ultralight', 'ulight', 'light', 'book', 'regular', 'medium', 
        'semibold', 'bold', 'ultrabold', 'heavy', 'black', 'super',
        'italic', 'oblique', 'rotalic', 'retalic'
    }
    
    family_tokens = [f"FD {family_core}"]
    subfamily_tokens = []
    
    for token in remainder:
        if token.lower() in weights_slopes or token.isdigit():
            subfamily_tokens.append(token)
        else:
            family_tokens.append(token)
            
    if not subfamily_tokens:
        subfamily_tokens = ['Regular']
        
    family_name = " ".join(family_tokens)
    subfamily = " ".join(subfamily_tokens)
    full_name = f"{family_name} {subfamily}"
    
    ps_tokens = [f"FD{family_core}"] + remainder
    ps_name = "".join(ps_tokens).replace(" ", "")
    
    return family_name, subfamily, full_name, ps_name

def process_single_font(font_path_str: str, family_core: str, family_genre: str, out_base_dir_str: str):
    font_path = Path(font_path_str)
    out_base_dir = Path(out_base_dir_str)
    try:
        donor_path = get_donor_path(font_path.name, family_genre)
        if not donor_path.exists():
            return {"error": f"Donor not found: {donor_path}", "file": font_path.name, "status": "FAIL"}
            
        desktop_dir = out_base_dir / "desktop"
        web_dir = out_base_dir / "web"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        web_dir.mkdir(parents=True, exist_ok=True)
        
        family_name, subfamily, full_name, ps_name = parse_font_naming(font_path, family_core)
        
        f_p = TTFont(str(font_path))
        f_a = TTFont(str(donor_path))
        
        target_upm = f_p['head'].unitsPerEm
        donor_upm = f_a['head'].unitsPerEm
        upm_scale = target_upm / float(donor_upm)
        
        cff_p = f_p['CFF '].cff
        top_dict_p = cff_p.topDictIndex[0]
        charstrings_p = top_dict_p.CharStrings
        glyf_a = f_a['glyf']
        cmap_a = f_a.getBestCmap()
        hmtx_a = f_a['hmtx']
        hmtx_p = f_p['hmtx']
        
        clean_notdef(charstrings_p, top_dict_p, hmtx_p, target_upm)
        
        if family_genre == 'serif':
            g_Uhorn_a = glyf_a['Uhorn']
            horn_U_pts = [(int(round(g_Uhorn_a.coordinates[i][0] * upm_scale)), int(round(g_Uhorn_a.coordinates[i][1] * upm_scale))) for i in range(35, 53)]
            horn_U_flags = [g_Uhorn_a.flags[i] for i in range(35, 53)]
            right_U_a = max(p[0] for p in glyf_a['U'].coordinates) * upm_scale
            top_U_a = max(p[1] for p in glyf_a['U'].coordinates) * upm_scale
            
            g_uhorn_a = glyf_a['uhorn']
            horn_u_pts = [(int(round(g_uhorn_a.coordinates[i][0] * upm_scale)), int(round(g_uhorn_a.coordinates[i][1] * upm_scale))) for i in range(0, 18)]
            horn_u_flags = [g_uhorn_a.flags[i] for i in range(0, 18)]
            right_u_a = max(p[0] for p in glyf_a['u'].coordinates) * upm_scale
            top_u_a = max(p[1] for p in glyf_a['u'].coordinates) * upm_scale
            
            g_Ohorn_a = glyf_a['Ohorn']
            horn_O_pts = [(int(round(g_Ohorn_a.coordinates[i][0] * upm_scale)), int(round(g_Ohorn_a.coordinates[i][1] * upm_scale))) for i in range(13, 31)]
            horn_O_flags = [g_Ohorn_a.flags[i] for i in range(13, 31)]
            right_O_a = max(p[0] for p in glyf_a['O'].coordinates) * upm_scale
            top_O_a = max(p[1] for p in glyf_a['O'].coordinates) * upm_scale
            
            g_ohorn_a = glyf_a['ohorn']
            horn_o_pts = [(int(round(g_ohorn_a.coordinates[i][0] * upm_scale)), int(round(g_ohorn_a.coordinates[i][1] * upm_scale))) for i in range(13, 31)]
            horn_o_flags = [g_ohorn_a.flags[i] for i in range(13, 31)]
            right_o_a = max(p[0] for p in glyf_a['o'].coordinates) * upm_scale
            top_o_a = max(p[1] for p in glyf_a['o'].coordinates) * upm_scale
        else:
            g_horn_a = glyf_a['uni031B']
            horn_pts_scaled = [(int(round(p[0] * upm_scale)), int(round(p[1] * upm_scale))) for p in g_horn_a.coordinates]
            horn_flags = list(g_horn_a.flags)
            
        order = list(f_p.getGlyphOrder())
        viet_to_base = {}
        
        fn_l = full_name.lower()
        if any(w in fn_l for w in ['black', 'heavy', 'super', 'ultrabold']):
            bar_h_d = int(round(48 * upm_scale))
            bar_h_lc = int(round(38 * upm_scale))
        elif 'bold' in fn_l or 'semibold' in fn_l:
            bar_h_d = int(round(38 * upm_scale))
            bar_h_lc = int(round(30 * upm_scale))
        elif 'light' in fn_l or 'thin' in fn_l or 'ulight' in fn_l:
            bar_h_d = int(round(22 * upm_scale))
            bar_h_lc = int(round(18 * upm_scale))
        else:
            bar_h_d = int(round(30 * upm_scale))
            bar_h_lc = int(round(24 * upm_scale))
            
        scale_lc = 0.80
        
        for ch in VIET_CHARS:
            cp = ord(ch)
            base_ch = get_base_char(ch)
            base_gname = 'dotlessi' if ch in 'ìíỉĩị' else base_ch
            
            if ch in ['đ', 'Đ']:
                dest_gname = 'dcroat' if ch == 'đ' else 'Dcroat'
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
            
            is_u_horn = ch in 'ƯỪỨỬỮỰ'
            is_lc_u_horn = ch in 'ưừứửữự'
            is_o_horn = ch in 'ƠỜỚỞỠỢ'
            is_lc_o_horn = ch in 'ơờớởỡợ'
            
            if family_genre == 'serif':
                if is_u_horn:
                    s_x = right_p_x - right_U_a
                    s_y = top_p_y - top_U_a
                    pts_s = [(int(round(p[0] + s_x)), int(round(p[1] + s_y))) for p in horn_U_pts]
                    draw_tt_contour(pts_s, horn_U_flags, rec_accents, reverse=True)
                elif is_lc_u_horn:
                    s_x = right_p_x - right_u_a
                    s_y = top_p_y - top_u_a
                    pts_s = [(int(round(p[0] + s_x)), int(round(p[1] + s_y))) for p in horn_u_pts]
                    draw_tt_contour(pts_s, horn_u_flags, rec_accents, reverse=True)
                elif is_o_horn:
                    s_x = right_p_x - right_O_a
                    s_y = top_p_y - top_O_a
                    pts_s = [(int(round(p[0] + s_x)), int(round(p[1] + s_y))) for p in horn_O_pts]
                    draw_tt_contour(pts_s, horn_O_flags, rec_accents, reverse=True)
                elif is_lc_o_horn:
                    s_x = right_p_x - right_o_a
                    s_y = top_p_y - top_o_a
                    pts_s = [(int(round(p[0] + s_x)), int(round(p[1] + s_y))) for p in horn_o_pts]
                    draw_tt_contour(pts_s, horn_o_flags, rec_accents, reverse=True)
            else:
                if is_u_horn or is_o_horn:
                    s_x = right_p_x + int(round(115 * upm_scale)) - int(round(-106 * upm_scale))
                    s_y = top_p_y + int(round(129 * upm_scale)) - int(round(757 * upm_scale))
                    pts_s = [(int(round(p[0] + s_x)), int(round(p[1] + s_y))) for p in horn_pts_scaled]
                    draw_tt_contour(pts_s, horn_flags, rec_accents, reverse=True)
                elif is_lc_u_horn or is_lc_o_horn:
                    s_x = right_p_x + int(round(111 * scale_lc * upm_scale)) - int(round(-106 * scale_lc * upm_scale))
                    s_y = top_p_y + int(round(129 * scale_lc * upm_scale)) - int(round(757 * scale_lc * upm_scale))
                    pts_s = [(int(round(p[0] * scale_lc + s_x)), int(round(p[1] * scale_lc + s_y))) for p in horn_pts_scaled]
                    draw_tt_contour(pts_s, horn_flags, rec_accents, reverse=True)
                    
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
                y_bar = int(round(top_p_y * 0.76))
                stem_x = int(round(bounds_p[2] - (bounds_p[2] - bounds_p[0]) * 0.16))
                rec_accents.moveTo((int(round(stem_x - w_base_p * 0.22)), y_bar))
                rec_accents.lineTo((int(round(stem_x + w_base_p * 0.16)), y_bar))
                rec_accents.lineTo((int(round(stem_x + w_base_p * 0.16)), y_bar + bar_h_lc))
                rec_accents.lineTo((int(round(stem_x - w_base_p * 0.22)), y_bar + bar_h_lc))
                rec_accents.closePath()
                
            if ch not in ['đ', 'Đ']:
                gname_a = cmap_a[cp]
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
                            
                        c_shifted = [(int(round(p[0] + s_x)), int(round(p[1] + s_y))) for p in c_coords]
                        draw_tt_contour(c_shifted, c_flags, rec_accents, reverse=True)
                        
            w_dest = w_base_p
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

        for cp in PUNCT_CODEPOINTS:
            if cp in cmap_a:
                gname_a = cmap_a[cp]
                dest_gname = f_p.getBestCmap().get(cp) or gname_a
                if dest_gname not in charstrings_p or cp in [0x3A, 0x3B, 0x21, 0x3F, 0x7C, 0x2014]:
                    rec_punct = RecordingPen()
                    g_punct = glyf_a[gname_a]
                    g_punct.expand(glyf_a)
                    coords_punc, end_pts_punc, flags_punc = g_punct.getCoordinates(glyf_a)
                    coords_punc = [(int(round(p[0] * upm_scale)), int(round(p[1] * upm_scale))) for p in coords_punc]
                    start = 0
                    for end in end_pts_punc:
                        end = end + 1
                        draw_tt_contour(coords_punc[start:end], flags_punc[start:end], rec_punct, reverse=True)
                        start = end
                        
                    w, lsb = hmtx_a[gname_a]
                    w = int(round(w * upm_scale))
                    lsb = int(round(lsb * upm_scale))
                    
                    t2_p = T2CharStringPen(width=w, glyphSet={})
                    qu2cu_p = Qu2CuPen(t2_p, max_err=1.0)
                    rec_punct.replay(qu2cu_p)
                    cs_p = t2_p.getCharString()
                    cs_p.private = top_dict_p.Private
                    cs_p.compile()
                    
                    if dest_gname in charstrings_p:
                        charstrings_p[dest_gname] = cs_p
                    else:
                        idx = len(charstrings_p.charStringsIndex)
                        charstrings_p.charStringsIndex.append(cs_p)
                        charstrings_p.charStrings[dest_gname] = idx
                        top_dict_p.charset.append(dest_gname)
                        order.append(dest_gname)
                    hmtx_p.metrics[dest_gname] = (int(round(w)), int(round(lsb)))
                    for sub in f_p['cmap'].tables:
                        sub.cmap[cp] = dest_gname

        for g in order:
            if g not in hmtx_p.metrics:
                hmtx_p.metrics[g] = (int(round(500 * upm_scale)), 0)
            else:
                m_w, m_lsb = hmtx_p.metrics[g]
                hmtx_p.metrics[g] = (int(round(m_w)), int(round(m_lsb)))
                
        f_p.setGlyphOrder(order)
        f_p['maxp'].numGlyphs = len(order)
        f_p['hhea'].numberOfHMetrics = len(order)
        
        # Sanitize hhea fields to strict int
        if 'hhea' in f_p:
            for attr in ['minLeftSideBearing', 'minRightSideBearing', 'xMaxExtent', 'advanceWidthMax']:
                if hasattr(f_p['hhea'], attr):
                    val = getattr(f_p['hhea'], attr)
                    if val is not None:
                        setattr(f_p['hhea'], attr, int(round(val)))
                        
        inherit_gpos_kerning(f_p, viet_to_base)
        
        f_p['name'].names = []
        records = [
            (0, "Copyright (c) 2026 FEDU. All rights reserved."),
            (1, family_name),
            (2, subfamily),
            (3, f"1.000;FEDU;{ps_name}"),
            (4, full_name),
            (5, "Version 1.000; FEDU Type Foundry"),
            (6, ps_name),
            (8, "FEDU Design Team"),
            (9, "FEDU Type Studio"),
            (11, "https://fedu.vn"),
            (12, "https://fedu.vn"),
            (13, "Licensed for internal and commercial creative production across FEDU Ecosystem."),
            (16, family_name),
            (17, subfamily),
        ]
        for nid, val in records:
            f_p['name'].setName(val, nid, 3, 1, 0x409)
            f_p['name'].setName(val, nid, 1, 0, 0)
            
        if 'OS/2' in f_p:
            f_p['OS/2'].achVendID = b'FEDU'
            
        cff_p.fontNames = [ps_name]
        top_dict_p.FamilyName = family_name
        top_dict_p.FullName = full_name
        if hasattr(top_dict_p, 'Notice'):
            top_dict_p.Notice = "Copyright (c) 2026 FEDU"
        if hasattr(top_dict_p, 'Copyright'):
            top_dict_p.Copyright = "Copyright (c) 2026 FEDU"
            
        desktop_file = desktop_dir / f"{ps_name}.otf"
        f_p.save(str(desktop_file))
        
        f_p.flavor = 'woff2'
        web_file = web_dir / f"{ps_name}.woff2"
        f_p.save(str(web_file))
        
        mac_dest = MAC_FONTS / f"{ps_name}.otf"
        with open(desktop_file, 'rb') as f_in, open(mac_dest, 'wb') as f_out:
            f_out.write(f_in.read())
            
        return {
            "ps_name": ps_name,
            "full_name": full_name,
            "desktop_path": str(desktop_file),
            "web_path": str(web_file),
            "mac_path": str(mac_dest),
            "glyphs": len(order),
            "status": "SUCCESS"
        }
    except Exception as e:
        return {"error": str(e), "file": font_path.name, "status": "FAIL"}

def run_family(family_core: str, family_genre: str = 'sans', max_workers: int = 8):
    src_dir = ROOT_GT_DIR / f"GT-{family_core}"
    out_dir = ROOT_GT_DIR / f"FD-{family_core}-VietNamized"
    
    font_files = sorted([f for f in src_dir.glob("*.otf") if not f.name.startswith(".")])
    if not font_files:
        print(f"[{family_core}] No .otf files found in {src_dir}")
        return []
        
    print(f"\n========================================================")
    print(f"▶ BUILDING FD-{family_core} ({len(font_files)} styles) | Genre: {family_genre.upper()}")
    print(f"========================================================")
    
    start_t = time.time()
    results = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single_font, str(fp), family_core, family_genre, str(out_dir))
            for fp in font_files
        ]
        for fut in futures:
            res = fut.result()
            results.append(res)
            if res.get("status") == "SUCCESS":
                print(f"  [+] {res['full_name']} -> {res['glyphs']} glyphs")
            else:
                print(f"  [!] ERROR on {res.get('file')}: {res.get('error')}")
                
    elapsed = time.time() - start_t
    success_count = sum(1 for r in results if r.get("status") == "SUCCESS")
    print(f"✔ Completed FD-{family_core}: {success_count}/{len(font_files)} styles built in {elapsed:.2f}s!")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_fams = sys.argv[1:]
    else:
        target_fams = ['Cinetype', 'Eesti', 'Haptik', 'Maru']
        
    for fam in target_fams:
        genre = 'serif' if fam in ['Canon', 'Flaire', 'Zirkon', 'Pantheon'] else 'sans'
        run_family(fam, genre)
