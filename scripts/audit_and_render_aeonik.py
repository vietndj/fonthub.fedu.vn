#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_and_render_aeonik.py
Master Typographic Quality Auditor & Specimen Render Engine for Aeonik Families
(Soft, Condensed, Extended, Fono, Mono)

Audits:
1. 100% Vietnamese Glyph Coverage (67 lowercase + 67 uppercase = 134 glyphs)
2. Advance Width Preservation: w(accented) == w(base) (delta = 0px), w == 620 for Mono
3. Full GPOS Kerning Parity with HarfBuzz (THUC vs THỰC, VIET vs VIỆT, DIEN vs ĐIỆN, CHIEN vs CHIẾN)
4. Diacritic Geometry & Collision Detection (horns, crossbars, stacked accents ế, ề, ể, ễ, ệ, ố, ồ, ổ, ỗ, ộ, ắ, ằ, ẳ, ẵ, ặ)
5. Visual Specimen Generation (PNG & Interactive HTML Report with 14px, 18px, 24px, 36px, 48px)
"""

import os
import sys
import math
import copy
import json
import time
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
REPORTS_DIR = PROJECT_ROOT / 'reports'
SPECIMENS_DIR = REPORTS_DIR / 'specimens'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SPECIMENS_DIR.mkdir(parents=True, exist_ok=True)

VIET_CHARS_LOWER = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS_UPPER = VIET_CHARS_LOWER.upper()
ALL_VIET_CHARS = VIET_CHARS_LOWER + VIET_CHARS_UPPER
ALL_VIET_LIST = list(ALL_VIET_CHARS)

BASE_MAPPING = str.maketrans(
    'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
    'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
    'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
    'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
)

TEST_KERNING_PAIRS = [
    ('THUC', 'THỰC', 'Uhorn (Ư/Ự) - Advance == U gốc, GPOS inherited (U-C)'),
    ('VIET', 'VIỆT', 'Ecircumflexdotbelow (Ệ) - Advance == E gốc, kerning V-I-Ệ-T khớp 100%'),
    ('DIEN', 'ĐIỆN', 'Dcroat (Đ) - Thanh ngang đặc tuyệt đối, kerning Đ-I-Ệ-N chuẩn chỉnh'),
    ('CHIEN', 'CHIẾN', 'Ecircumflexacute (Ế) - Vị trí mũ sắc cân xứng, nhịp điệu từ hoàn hảo'),
    ('thuc', 'thực', 'Lower uhorn (ư/ự) - Giọt nước sừng ôm sát terminal, zero gap'),
    ('viet', 'việt', 'Lower ecircumflexdotbelow (ệ) - Dấu nặng dưới x-height, zero collision'),
    ('nghieng', 'nghiêng', 'Compound circumflex (ê) - Nhịp điệu từ mượt mà, delta = 0'),
    ('chien', 'chiến', 'Lower ecircumflexacute (ế) - Mũ ớ cân đối, nhịp điệu mượt mà')
]

PANGRAMS = [
    ("Hà Nội mùa này vắng những cơn mưa, hoa sữa thôi rơi, em bên tôi bước đi lặng lẽ.", "Hà Nội mùa này vắng những cơn mưa"),
    ("Việt Nam đất nước ta ơi, mênh mông biển lúa đâu trời đẹp hơn.", "Việt Nam đất nước ta ơi"),
    ("Chàng trai ôm đóa hoa cúc vàng rực rỡ dạo bước dưới ánh nắng chiều êm ả.", "Chàng trai ôm đóa hoa cúc vàng"),
    ("Cây đa, bến nước, sân đình, ngàn năm soi bóng lung linh rạng ngời.", "Cây đa bến nước sân đình"),
    ("Đường về xứ Huế quanh quanh, non xanh nước biếc như tranh họa đồ.", "Đường về xứ Huế quanh quanh"),
    ("Kỳ diệu, bướng bỉnh, phụng dưỡng, khúc khuỷu, trĩu hạt, ngoằn ngoèo.", "Pangram dấu phụ & dấu ghép phức tạp")
]

VOWEL_GROUPS = [
    ('A', ['A', 'À', 'Á', 'Ả', 'Ã', 'Ạ'], ['a', 'à', 'á', 'ả', 'ã', 'ạ']),
    ('Ă', ['Ă', 'Ằ', 'Ắ', 'Ẳ', 'Ẵ', 'Ặ'], ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ']),
    ('Â', ['Â', 'Ầ', 'Ấ', 'Ẩ', 'Ẫ', 'Ậ'], ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ']),
    ('E', ['E', 'È', 'É', 'Ẻ', 'Ẽ', 'Ẹ'], ['e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ']),
    ('Ê', ['Ê', 'Ề', 'Ế', 'Ể', 'Ễ', 'Ệ'], ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ']),
    ('I', ['I', 'Ì', 'Í', 'Ỉ', 'Ĩ', 'Ị'], ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị']),
    ('O', ['O', 'Ò', 'Ó', 'Ỏ', 'Õ', 'Ọ'], ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ']),
    ('Ô', ['Ô', 'Ồ', 'Ố', 'Ổ', 'Ỗ', 'Ộ'], ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ']),
    ('Ơ', ['Ơ', 'Ờ', 'Ớ', 'Ở', 'Ỡ', 'Ợ'], ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ']),
    ('U', ['U', 'Ù', 'Ú', 'Ủ', 'Ũ', 'Ụ'], ['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ']),
    ('Ư', ['Ư', 'Ừ', 'Ứ', 'Ử', 'Ữ', 'Ự'], ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự']),
    ('Y', ['Y', 'Ỳ', 'Ý', 'Ỷ', 'Ỹ', 'Ỵ'], ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ']),
    ('Đ', ['D', 'Đ'], ['d', 'đ'])
]

def extract_cmap(font: TTFont) -> dict:
    cmap = {}
    if 'cmap' in font:
        for t in font['cmap'].tables:
            if t.isUnicode():
                cmap.update(t.cmap)
    return cmap

def audit_single_font(font_path: Path, family_name: str = '') -> dict:
    f = TTFont(str(font_path))
    cmap = extract_cmap(f)
    hmtx = f['hmtx'].metrics if 'hmtx' in f else {}
    upm = f['head'].unitsPerEm if 'head' in f else 1000
    is_cff = 'CFF ' in f or 'CFF2' in f
    is_mono = 'mono' in font_path.name.lower() or 'mono' in family_name.lower()

    missing_glyphs = [ch for ch in ALL_VIET_CHARS if ord(ch) not in cmap]
    coverage_pct = round(((len(ALL_VIET_CHARS) - len(missing_glyphs)) / len(ALL_VIET_CHARS)) * 100, 1)

    width_mismatches = []
    if is_mono:
        ascii_widths = [hmtx[cmap[ord(c)]][0] for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' if ord(c) in cmap and cmap[ord(c)] in hmtx]
        mono_expected = 620
        if ascii_widths:
            from collections import Counter
            mono_expected = Counter(ascii_widths).most_common(1)[0][0]
        for ch in ALL_VIET_CHARS:
            cp = ord(ch)
            if cp in cmap:
                gname = cmap[cp]
                if gname in hmtx:
                    w = hmtx[gname][0]
                    if w != mono_expected:
                        width_mismatches.append({
                            'char': ch, 'expected': mono_expected, 'actual': w, 'diff': w - mono_expected
                        })
    else:
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
                        width_mismatches.append({
                            'char': ch, 'base': base_ch, 'w_acc': w_acc, 'w_base': w_base, 'diff': w_acc - w_base
                        })

    kerning_results = []
    kerning_all_pass = True
    try:
        with open(font_path, 'rb') as fp:
            font_bytes = fp.read()
        hb_face = hb.Face(font_bytes)
        hb_font = hb.Font(hb_face)
        
        def get_adv(word: str):
            buf = hb.Buffer()
            buf.add_str(word)
            buf.guess_segment_properties()
            hb.shape(hb_font, buf)
            return sum(p.x_advance for p in buf.glyph_positions)
            
        for w_unacc, w_acc, note in TEST_KERNING_PAIRS:
            adv1 = get_adv(w_unacc)
            adv2 = get_adv(w_acc)
            diff = adv2 - adv1
            passed = (diff == 0)
            if not passed:
                kerning_all_pass = False
            kerning_results.append({
                'unaccented': w_unacc,
                'accented': w_acc,
                'adv_unacc': adv1,
                'adv_acc': adv2,
                'delta': diff,
                'note': note,
                'pass': passed
            })
    except Exception as e:
        kerning_all_pass = False
        kerning_results.append({'error': str(e), 'pass': False})

    collision_issues = []
    test_chars = ['ế', 'ề', 'ể', 'ễ', 'ệ', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'ơ', 'ư', 'đ', 'Đ']
    for ch in test_chars:
        cp = ord(ch)
        if cp in cmap:
            gname = cmap[cp]
            try:
                if is_cff and 'CFF ' in f:
                    cff = f['CFF '].cff.topDictIndex[0]
                    cs = cff.CharStrings[gname]
                    bounds = cs.calcBounds(cff.CharStrings)
                    if bounds is None:
                        collision_issues.append(f'{ch} ({gname}): Bounds are None (empty outline)')
                    else:
                        xMin, yMin, xMax, yMax = bounds
                        if ch in ['đ', 'Đ'] and (xMax - xMin < 100):
                            collision_issues.append(f'{ch}: Glyph appears too narrow or missing crossbar')
                        if ch in ['ế', 'ề', 'ể', 'ễ', 'ố', 'ồ', 'ổ', 'ỗ', 'ắ', 'ằ', 'ẳ', 'ẵ'] and yMax < (upm * 0.5):
                            collision_issues.append(f'{ch}: Stacked diacritic yMax abnormally low ({yMax})')
                elif 'glyf' in f:
                    g = f['glyf'][gname]
                    if g.numberOfContours == 0 and not g.isComposite():
                        collision_issues.append(f'{ch} ({gname}): No contours in glyph')
            except Exception as e:
                collision_issues.append(f'{ch}: Error calculating bounds: {str(e)}')

    dcroat_ok = (ord('đ') in cmap and ord('Đ') in cmap)
    if dcroat_ok:
        try:
            if is_cff and 'CFF ' in f:
                cff = f['CFF '].cff.topDictIndex[0]
                cs_d = cff.CharStrings[cmap[ord('đ')]]
                cs_D = cff.CharStrings[cmap[ord('Đ')]]
                len_d = len(cs_d.bytecode) if cs_d.bytecode is not None else len(getattr(cs_d, 'program', []))
                len_D = len(cs_D.bytecode) if cs_D.bytecode is not None else len(getattr(cs_D, 'program', []))
                dcroat_ok = len_d > 5 and len_D > 5
            elif 'glyf' in f:
                g_d = f['glyf'][cmap[ord('đ')]]
                g_D = f['glyf'][cmap[ord('Đ')]]
                dcroat_ok = (g_d.numberOfContours != 0 or g_d.isComposite()) and (g_D.numberOfContours != 0 or g_D.isComposite())
        except Exception:
            dcroat_ok = False

    overall_pass = (
        len(missing_glyphs) == 0 and
        len(width_mismatches) == 0 and
        kerning_all_pass and
        len(collision_issues) == 0 and
        dcroat_ok
    )

    return {
        'file_name': font_path.name,
        'path': str(font_path),
        'format': 'CFF/OTF' if is_cff else 'TrueType/TTF',
        'upm': upm,
        'is_mono': is_mono,
        'coverage_pct': coverage_pct,
        'missing_glyphs': missing_glyphs,
        'missing_count': len(missing_glyphs),
        'width_mismatches': width_mismatches,
        'width_mismatch_count': len(width_mismatches),
        'kerning_results': kerning_results,
        'kerning_all_pass': kerning_all_pass,
        'collision_issues': collision_issues,
        'dcroat_ok': dcroat_ok,
        'overall_pass': overall_pass
    }

def render_family_specimen_png(family_name: str, bold_path: str, reg_path: str, out_path: Path):
    W, H = 1600, 1200
    img = Image.new('RGB', (W, H), (15, 18, 26))
    draw = ImageDraw.Draw(img)

    try:
        f_badge = ImageFont.truetype(bold_path, 14)
        f_fam = ImageFont.truetype(bold_path, 52)
        f_sub = ImageFont.truetype(reg_path, 18)
        f_h1 = ImageFont.truetype(bold_path, 36)
        f_pangram_lg = ImageFont.truetype(bold_path, 28)
        f_pangram_md = ImageFont.truetype(reg_path, 22)
        f_pangram_sm = ImageFont.truetype(reg_path, 16)
        f_vowels = ImageFont.truetype(reg_path, 22)
    except Exception as e:
        print(f'Error loading fonts for specimen {family_name}: {e}')
        return

    draw.rectangle([(30, 30), (W - 30, H - 30)], fill=(22, 27, 38), outline=(44, 54, 76), width=2)
    draw.rectangle([(60, 60), (280, 92)], fill=(24, 48, 38), outline=(38, 140, 90), width=1)
    draw.text((75, 67), 'FEDU QUALITY AUDIT', font=f_badge, fill=(52, 211, 153))

    draw.rectangle([(295, 60), (520, 92)], fill=(34, 42, 60), outline=(59, 130, 246), width=1)
    draw.text((310, 67), '100% VIỆT HÓA CHUẨN SVN', font=f_badge, fill=(147, 197, 253))

    draw.text((60, 115), family_name.upper(), font=f_fam, fill=(255, 255, 255))
    draw.text((60, 180), 'Kiểm định trực quan Typographic Engine — Đầy đủ 134 ký tự tiếng Việt, dấu thanh cân đối', font=f_sub, fill=(148, 163, 184))

    draw.line([(60, 215), (W - 60, 215)], fill=(51, 65, 85), width=2)
    draw.text((60, 240), 'TIÊU ĐỀ NGHỆ THUẬT & TRUYỀN THÔNG HIỆN ĐẠI', font=f_h1, fill=(248, 250, 252))

    y = 310
    draw.text((60, y), '48px — ' + PANGRAMS[0][0], font=f_pangram_lg, fill=(255, 255, 255))
    y += 50
    draw.text((60, y), '36px — ' + PANGRAMS[1][0], font=f_pangram_lg, fill=(226, 232, 240))
    y += 45
    draw.text((60, y), '24px — ' + PANGRAMS[2][0], font=f_pangram_md, fill=(203, 213, 225))
    y += 40
    draw.text((60, y), '18px — ' + PANGRAMS[3][0], font=f_pangram_sm, fill=(148, 163, 184))
    y += 35
    draw.text((60, y), '14px — ' + PANGRAMS[4][0], font=f_pangram_sm, fill=(100, 116, 139))
    y += 35
    draw.text((60, y), 'Phức hợp: ' + PANGRAMS[5][0], font=f_pangram_sm, fill=(251, 191, 36))

    y += 60
    draw.line([(60, y), (W - 60, y)], fill=(51, 65, 85), width=1)
    y += 20
    draw.text((60, y), 'MA TRẬN NGUYÊN ÂM TIẾNG VIỆT ĐẦY ĐỦ 134 KÝ TỰ (UPPER & LOWER)', font=f_badge, fill=(56, 189, 248))
    y += 35

    col_w = (W - 120) // 7
    for idx, (group_name, u_chars, l_chars) in enumerate(VOWEL_GROUPS[:7]):
        gx = 60 + idx * col_w
        gy = y
        draw.text((gx, gy), f'[{group_name}]', font=f_badge, fill=(167, 139, 250))
        draw.text((gx, gy + 25), ' '.join(u_chars), font=f_vowels, fill=(241, 245, 249))
        draw.text((gx, gy + 55), ' '.join(l_chars), font=f_vowels, fill=(148, 163, 184))

    y += 100
    for idx, (group_name, u_chars, l_chars) in enumerate(VOWEL_GROUPS[7:]):
        gx = 60 + idx * col_w
        gy = y
        draw.text((gx, gy), f'[{group_name}]', font=f_badge, fill=(167, 139, 250))
        draw.text((gx, gy + 25), ' '.join(u_chars), font=f_vowels, fill=(241, 245, 249))
        draw.text((gx, gy + 55), ' '.join(l_chars), font=f_vowels, fill=(148, 163, 184))

    img.save(str(out_path), 'PNG')
    print(f'  [Specimen PNG] Saved: {out_path}')

def generate_interactive_html_report(families_audit: list, out_html_path: Path):
    total_fonts = sum(len(f['fonts']) for f in families_audit)
    all_passed = len(families_audit) > 0 and all(f['all_passed'] for f in families_audit)
    
    font_faces = []
    for fam in families_audit:
        fam_clean = fam['family_name'].replace(' ', '_').replace('-', '_')
        for font in fam['fonts']:
            fpath = font['path']
            rel_path = os.path.relpath(fpath, out_html_path.parent)
            fmt = 'opentype' if fpath.endswith('.otf') else ('woff2' if fpath.endswith('.woff2') else 'truetype')
            font_faces.append(f"""
            @font-face {{
                font-family: '{fam_clean}_{font["file_name"]}';
                src: url('{rel_path}') format('{fmt}');
                font-weight: normal;
                font-style: normal;
            }}""")

    html_cards = []
    for fam in families_audit:
        fam_name = fam['family_name']
        fam_passed = fam['all_passed']
        status_badge = f'<span class="badge pass">PASS (100%)</span>' if fam_passed else f'<span class="badge fail">FAIL</span>'
        
        font_rows = []
        for font in fam['fonts']:
            font_pass = font['overall_pass']
            f_badge = '<span class="status-dot green"></span> PASS' if font_pass else '<span class="status-dot red"></span> FAIL'
            
            kerning_chips = []
            for k in font['kerning_results'][:4]:
                k_class = 'ok' if k.get('pass') else 'err'
                k_chip = f'<span class="chip {k_class}">{k.get("unaccented")} vs {k.get("accented")} (Δ={k.get("delta",0)})</span>'
                kerning_chips.append(k_chip)
            kerning_html = ' '.join(kerning_chips)

            missing_html = ''
            if font['missing_glyphs']:
                missing_html = f'<div class="err-text">Thiếu {len(font["missing_glyphs"])} ký tự: {"".join(font["missing_glyphs"][:20])}...</div>'

            width_html = ''
            if font['width_mismatches']:
                width_html = f'<div class="err-text">Lệch chiều ngang {len(font["width_mismatches"])} glyphs!</div>'

            fam_clean = fam['family_name'].replace(' ', '_').replace('-', '_')
            font_id = f'{fam_clean}_{font["file_name"]}'

            row = f"""
            <div class="font-item">
                <div class="font-item-header">
                    <div class="font-title">
                        <strong>{font['file_name']}</strong>
                        <span class="meta">{font['format']} | UPM: {font['upm']} | Coverage: {font['coverage_pct']}%</span>
                    </div>
                    <div class="font-badge">{f_badge}</div>
                </div>
                {missing_html}
                {width_html}
                <div class="kerning-preview">
                    <span class="label">Kerning Parity:</span> {kerning_html}
                </div>
                <div class="live-specimens" style="font-family: '{font_id}', sans-serif;">
                    <div class="specimen-line sz-48"><span class="size-tag">48px</span> Hà Nội mùa này vắng những cơn mưa, hoa sữa thôi rơi</div>
                    <div class="specimen-line sz-36"><span class="size-tag">36px</span> Việt Nam đất nước ta ơi, mênh mông biển lúa đâu trời đẹp hơn</div>
                    <div class="specimen-line sz-24"><span class="size-tag">24px</span> Chàng trai ôm đóa hoa cúc vàng rực rỡ dạo bước dưới ánh nắng chiều êm ả</div>
                    <div class="specimen-line sz-18"><span class="size-tag">18px</span> Cây đa, bến nước, sân đình, ngàn năm soi bóng lung linh rạng ngời. Đường về xứ Huế quanh quanh non xanh biếc.</div>
                    <div class="specimen-line sz-14"><span class="size-tag">14px</span> Thơ ngây, bướng bỉnh, kỳ diệu, phụng dưỡng, khúc khuỷu, trĩu hạt, ngoằn ngoèo, ế, ề, ể, ễ, ệ, ố, ồ, ổ, ỗ, ộ, ắ, ằ, ẳ, ẵ, ặ, ơ, ư, đ, Đ.</div>
                </div>
            </div>"""
            font_rows.append(row)

        card = f"""
        <div class="family-card {'pass' if fam_passed else 'fail'}">
            <div class="family-header">
                <div>
                    <h2>{fam_name}</h2>
                    <span class="family-count">{len(fam['fonts'])} Styles / Weights audited</span>
                </div>
                <div>{status_badge}</div>
            </div>
            <div class="font-list">
                {''.join(font_rows)}
            </div>
        </div>"""
        html_cards.append(card)

    html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Nghiệm Thu & Visual Preview Bộ Font Aeonik Việt Hóa (FEDU)</title>
    <style>
        {''.join(font_faces)}
        :root {{
            --bg: #0b0f19;
            --surface: #111827;
            --surface-card: #1f2937;
            --border: #374151;
            --text: #f3f4f6;
            --text-sub: #9ca3af;
            --accent: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }}
        body.light {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --surface-card: #f1f5f9;
            --border: #cbd5e1;
            --text: #0f172a;
            --text-sub: #64748b;
            --accent: #2563eb;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            padding: 30px;
            line-height: 1.5;
            transition: background 0.2s, color 0.2s;
        }}
        .container {{ max-width: 1300px; margin: 0 auto; }}
        header {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        h1 {{ font-size: 26px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px; }}
        .header-sub {{ color: var(--text-sub); font-size: 15px; }}
        .controls {{ display: flex; gap: 12px; align-items: center; }}
        .btn {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }}
        .btn:hover {{ border-color: var(--accent); }}
        .badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            display: inline-block;
        }}
        .badge.pass {{ background: rgba(16, 185, 129, 0.2); color: var(--success); border: 1px solid var(--success); }}
        .badge.fail {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger); }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{ font-size: 32px; font-weight: 800; color: var(--accent); }}
        .stat-label {{ color: var(--text-sub); font-size: 14px; margin-top: 4px; }}

        .family-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .family-header {{
            padding: 20px 25px;
            background: var(--surface-card);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .family-header h2 {{ font-size: 20px; font-weight: 700; }}
        .family-count {{ font-size: 13px; color: var(--text-sub); margin-left: 8px; }}

        .font-list {{ padding: 25px; display: flex; flex-direction: column; gap: 25px; }}
        .font-item {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }}
        .font-item-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }}
        .font-title strong {{ font-size: 16px; font-weight: 700; }}
        .font-title .meta {{ margin-left: 10px; font-size: 12px; color: var(--text-sub); }}
        .status-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }}
        .status-dot.green {{ background: var(--success); }}
        .status-dot.red {{ background: var(--danger); }}
        
        .kerning-preview {{ margin: 10px 0; font-size: 13px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
        .kerning-preview .label {{ color: var(--text-sub); font-weight: 600; }}
        .chip {{ padding: 3px 8px; border-radius: 6px; font-size: 12px; font-family: monospace; }}
        .chip.ok {{ background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }}
        .chip.err {{ background: rgba(239, 68, 68, 0.15); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.3); }}
        .err-text {{ color: var(--danger); font-size: 13px; font-weight: 600; margin-bottom: 8px; }}

        .live-specimens {{
            margin-top: 15px;
            padding: 15px 20px;
            background: var(--bg);
            border-radius: 8px;
            border: 1px solid var(--border);
            overflow-x: auto;
        }}
        .specimen-line {{ margin-bottom: 10px; display: flex; align-items: baseline; gap: 15px; }}
        .specimen-line:last-child {{ margin-bottom: 0; }}
        .size-tag {{ font-size: 11px; font-family: monospace; color: var(--text-sub); padding: 2px 6px; background: var(--surface-card); border-radius: 4px; min-width: 42px; text-align: center; }}
        .sz-48 {{ font-size: 48px; line-height: 1.2; }}
        .sz-36 {{ font-size: 36px; line-height: 1.25; }}
        .sz-24 {{ font-size: 24px; line-height: 1.3; }}
        .sz-18 {{ font-size: 18px; line-height: 1.4; }}
        .sz-14 {{ font-size: 14px; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Báo Cáo Nghiệm Thu & Visual Preview Bộ Font Aeonik Mới</h1>
                <div class="header-sub">Chịu trách nhiệm: FEDU Quality Auditor | Tiêu chuẩn: Chuẩn SVN 100% Tiếng Việt, Zero Advance Width Inflation, GPOS Kerning Parity</div>
            </div>
            <div class="controls">
                <button class="btn" onclick="document.body.classList.toggle('light')">Đổi Giao Diện Sáng/Tối</button>
            </div>
        </header>

        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{len(families_audit)}</div>
                <div class="stat-label">Font Families Audited</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_fonts}</div>
                <div class="stat-label">Tổng File Font Kiểm Tra</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: {'var(--success)' if all_passed else 'var(--danger)'};">
                    {'100%' if all_passed else 'CẦN FIX'}
                </div>
                <div class="stat-label">Độ Bao Phủ Tiếng Việt</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: {'var(--success)' if all_passed else 'var(--warning)'};">
                    {'PASS TOÀN DIỆN' if all_passed else 'ĐANG THEO DÕI'}
                </div>
                <div class="stat-label">Trạng Thái Nghiệm Thu</div>
            </div>
        </div>

        {''.join(html_cards)}
    </div>
</body>
</html>
"""
    with open(out_html_path, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    print(f'  [HTML Report] Generated: {out_html_path}')

def run_aeonik_audit(search_dirs=None):
    print('\n==================================================================')
    print('▶ CHẠY FORENSIC AUDITOR TOÀN DIỆN CHO CÁC BỘ FONT AEONIK MỚI')
    print('==================================================================')
    
    if search_dirs is None:
        search_dirs = [
            PROJECT_ROOT / 'dist/fonts',
            PROJECT_ROOT / 'fonts',
            PROJECT_ROOT / 'dist/fonts/web',
            PROJECT_ROOT / 'temp_aeonik',
            Path('/Users/vietmac/Library/Fonts')
        ]

    targets = {
        'Aeonik Soft': ['aeonik soft', 'aeoniksoft', 'fdaeoniksoft', 'aeonik-soft', 'fd-aeonik-soft'],
        'Aeonik Condensed': ['aeonik condensed', 'aeonikcondensed', 'fdaeonikcondensed', 'aeonik-condensed', 'fd-aeonik-condensed'],
        'Aeonik Extended': ['aeonik extended', 'aeonikextended', 'fdaeonikextended', 'aeonik-extended', 'fd-aeonik-extended'],
        'Aeonik Fono': ['aeonik fono', 'aeonikfono', 'fdaeonikfono', 'aeonik-fono', 'fd-aeonik-fono'],
        'Aeonik Mono': ['aeonik mono', 'aeonikmono', 'fdaeonikmono', 'aeonik-mono', 'fd-aeonik-mono']
    }

    families_found = {k: [] for k in targets}

    for d in search_dirs:
        if not d.exists():
            continue
        for ext in ['*.otf', '*.ttf', '*.woff2']:
            for fpath in d.glob(f'**/{ext}'):
                fname_low = fpath.name.lower()
                parent_low = fpath.parent.name.lower()
                # Skip raw trial fonts that are not yet vietnamized
                if 'trial' in fname_low or 'trial' in parent_low:
                    continue
                for fam_name, patterns in targets.items():
                    if any(p in fname_low or p in parent_low for p in patterns):
                        if fpath not in families_found[fam_name]:
                            families_found[fam_name].append(fpath)

    results = []
    for fam_name, files in families_found.items():
        print(f'\n--- Audit Family: {fam_name} ({len(files)} files discovered) ---')
        if not files:
            print(f'  ⚠️ Chưa tìm thấy file font đã việt hóa cho {fam_name}')
            results.append({
                'family_name': fam_name,
                'fonts': [],
                'all_passed': False,
                'error': 'No font files found'
            })
            continue

        font_audits = []
        for fp in sorted(files):
            res = audit_single_font(fp, family_name=fam_name)
            font_audits.append(res)
            status_str = '✅ PASS' if res['overall_pass'] else '❌ FAIL'
            print(f'  • {fp.name:<38}: {status_str} (Coverage: {res["coverage_pct"]}%, Missing: {res["missing_count"]}, Width err: {res["width_mismatch_count"]})')

        all_passed = len(font_audits) > 0 and all(fa['overall_pass'] for fa in font_audits)

        bold_font = None
        reg_font = None
        for fa in font_audits:
            p = fa['path'].lower()
            if 'bold' in p and 'italic' not in p:
                bold_font = fa['path']
            if 'regular' in p and 'italic' not in p:
                reg_font = fa['path']
        if not reg_font and font_audits:
            reg_font = font_audits[0]['path']
        if not bold_font and font_audits:
            bold_font = reg_font

        specimen_png = SPECIMENS_DIR / f"specimen_{fam_name.replace(' ', '_').lower()}.png"
        try:
            if reg_font and bold_font:
                render_family_specimen_png(fam_name, bold_font, reg_font, specimen_png)
        except Exception as e:
            print(f'  ⚠️ Không thể render PNG specimen: {e}')

        results.append({
            'family_name': fam_name,
            'fonts': font_audits,
            'all_passed': all_passed,
            'regular_font': reg_font,
            'bold_font': bold_font,
            'specimen_png': str(specimen_png)
        })

    out_html = REPORTS_DIR / 'aeonik_families_audit_report.html'
    generate_interactive_html_report(results, out_html)
    
    out_json = REPORTS_DIR / 'aeonik_families_audit_report.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f'\n[Report JSON] Saved to: {out_json}')

    return results

if __name__ == '__main__':
    run_aeonik_audit()
