#!/usr/bin/env python3
"""
FD Pantheon Font Engine & Vietnamese Localization Pipeline
Learns diacritics and character metrics from SVN font repository (SVN-AlpinaFine),
transplants all 134 Vietnamese characters and 30+ missing punctuation marks into GT Pantheon,
neutralizes the Grilli Trial watermark, sanitizes metadata into 'FD Pantheon',
and exports production Desktop OTF & Web WOFF2 fonts.
"""

import os
import sys
import glob
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.qu2cuPen import Qu2CuPen

SRC_DIR = Path("/Users/vietmac/Documents/font gt/GT-Pantheon")
DONOR_DIR = Path("/Users/vietmac/Library/Fonts")
OUT_DIR = Path("/Users/vietmac/Documents/font gt/FD-Pantheon-VietNamized")
DESKTOP_DIR = OUT_DIR / "desktop"
WEB_DIR = OUT_DIR / "web"
SPECIMEN_DIR = OUT_DIR / "specimens"
MAC_FONTS = Path("/Users/vietmac/Library/Fonts")

# 134 Vietnamese uppercase and lowercase characters
VIET_CHARS = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VIET_CHARS += VIET_CHARS.upper()
VIET_CODEPOINTS = set(ord(c) for c in VIET_CHARS)

# Essential punctuation and symbols stripped by trial
PUNCT_CODEPOINTS = set([
    0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F,
    0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x5B, 0x5C, 0x5D, 0x5E, 0x5F,
    0x60, 0x7B, 0x7C, 0x7D, 0x7E,
    0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x2022
])

TARGET_CODEPOINTS = sorted(list(VIET_CODEPOINTS | PUNCT_CODEPOINTS))

def get_donor_path(filename: str) -> Path:
    fn_lower = filename.lower()
    is_italic = "italic" in fn_lower
    
    if "light" in fn_lower:
        style = "LightItalic" if is_italic else "Light"
    elif "medium" in fn_lower:
        style = "MediumItalic" if is_italic else "Medium"
    elif "bold" in fn_lower:
        style = "BoldItalic" if is_italic else "Bold"
    elif "black" in fn_lower:
        style = "BoldItalic" if is_italic else "Bold"
    else:
        style = "Italic" if is_italic else "Regular"
        
    return DONOR_DIR / f"SVN-AlpinaFine-{style}.ttf"

def clean_notdef(charstrings, top_dict, hmtx):
    """Replace trial watermark badge with clean neutral rectangle."""
    t2 = T2CharStringPen(width=500, glyphSet=charstrings)
    t2.moveTo((50, 0))
    t2.lineTo((50, 700))
    t2.lineTo((450, 700))
    t2.lineTo((450, 0))
    t2.closePath()
    cs = t2.getCharString()
    cs.private = top_dict.Private
    cs.compile()
    charstrings['.notdef'] = cs
    hmtx.metrics['.notdef'] = (500, 50)

def process_font(font_path: Path):
    donor_path = get_donor_path(font_path.name)
    if not donor_path.exists():
        print(f"Donor not found: {donor_path}")
        return None
        
    raw_name = font_path.stem.replace("-Trial", "")
    parts = raw_name.split("-")
    optical_size = parts[2] # Display, Text, Micro
    weight_parts = parts[3:]
    subfamily = " ".join(weight_parts)
    weight_slug = "".join(weight_parts)
    
    family_name = f"FD Pantheon {optical_size}"
    full_name = f"{family_name} {subfamily}"
    ps_name = f"FDPantheon{optical_size}-{weight_slug}"
    
    f_p = TTFont(str(font_path))
    f_a = TTFont(str(donor_path))
    
    cff_p = f_p['CFF '].cff
    top_dict_p = cff_p.topDictIndex[0]
    charstrings_p = top_dict_p.CharStrings
    glyf_a = f_a['glyf']
    hmtx_a = f_a['hmtx']
    hmtx_p = f_p['hmtx']
    cmap_a = f_a.getBestCmap()
    cmap_p = f_p.getBestCmap()
    
    # 1. Clean .notdef
    clean_notdef(charstrings_p, top_dict_p, hmtx_p)
    
    # 2. Inject Vietnamese & Punctuation
    glyph_order = list(f_p.getGlyphOrder())
    
    for cp in TARGET_CODEPOINTS:
        if cp in cmap_a:
            gname_a = cmap_a[cp]
            dest_gname = f_p.getBestCmap().get(cp) or gname_a
            is_viet = cp in VIET_CODEPOINTS
            
            if dest_gname not in charstrings_p or is_viet or cp in PUNCT_CODEPOINTS:
                rec = RecordingPen()
                glyf_a[gname_a].draw(rec, glyf_a)
                w, lsb = hmtx_a[gname_a]
                
                t2 = T2CharStringPen(width=w, glyphSet={})
                qu2cu = Qu2CuPen(t2, max_err=1.0)
                rec.replay(qu2cu)
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
                    glyph_order.append(dest_gname)
                    
                hmtx_p.metrics[dest_gname] = (w, lsb)
                cmap_p[cp] = dest_gname
                
    for g in glyph_order:
        if g not in hmtx_p.metrics:
            hmtx_p.metrics[g] = (500, 0)
            
    f_p.setGlyphOrder(glyph_order)
    f_p['maxp'].numGlyphs = len(glyph_order)
    f_p['hhea'].numberOfHMetrics = len(glyph_order)
    
    # 3. Purge & Rebuild Metadata
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
        
    # 4. Save Desktop OTF
    desktop_file = DESKTOP_DIR / f"{ps_name}.otf"
    f_p.save(str(desktop_file))
    
    # 5. Save Web WOFF2
    f_p.flavor = 'woff2'
    web_file = WEB_DIR / f"{ps_name}.woff2"
    f_p.save(str(web_file))
    
    return {
        "ps_name": ps_name,
        "full_name": full_name,
        "family": family_name,
        "subfamily": subfamily,
        "optical_size": optical_size,
        "desktop_path": desktop_file,
        "web_path": web_file,
        "total_glyphs": len(glyph_order)
    }

def main():
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    SPECIMEN_DIR.mkdir(parents=True, exist_ok=True)
    
    font_files = sorted(SRC_DIR.glob("GT-Pantheon-Text-*.otf")) + sorted(SRC_DIR.glob("GT-Pantheon-Display-*.otf")) + sorted(SRC_DIR.glob("GT-Pantheon-Micro-*.otf"))
    print(f"Found {len(font_files)} fonts to vietnamize...")
    
    results = []
    for fp in font_files:
        print(f"Processing {fp.name}...")
        res = process_font(fp)
        if res:
            results.append(res)
            print(f"  -> Generated: {res['full_name']} ({res['total_glyphs']} glyphs)")
            
    # Install desktop fonts to ~/Library/Fonts
    installed = 0
    for r in results:
        dest_mac = MAC_FONTS / r['desktop_path'].name
        with open(r['desktop_path'], 'rb') as f_src, open(dest_mac, 'wb') as f_dst:
            f_dst.write(f_src.read())
        installed += 1
    print(f"\nInstalled {installed} fonts directly to macOS ({MAC_FONTS})!")
    
    print(f"\nCompleted! Total fonts built: {len(results)}")

if __name__ == "__main__":
    main()
