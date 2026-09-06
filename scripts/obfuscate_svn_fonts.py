#!/usr/bin/env python3
"""
FEDU Font Obfuscator & Anti-Detection Renaming Engine
Converts SVN fonts into proprietary 'FD' derivative fonts with:
1. Zero-trace metadata sanitization (Vendor ID: FEDU, Copyright: 2026 FEDU)
2. Vector micro-morphing (+0.6% X, +0.2% Y) defeating OCR & AI hash matching
3. Dual TTF/OTF and WOFF2 export
4. Multi-core high-speed parallel processing
5. Direct macOS installation for instant testing
"""

import os
import sys
import re
import copy
import hashlib
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

SCALE_X = 1.006
SCALE_Y = 1.002

WEIGHT_MAP = {
    'thin': 100,
    'hairline': 100,
    'air': 100,
    'ultralight': 200,
    'extralight': 200,
    'light': 300,
    'book': 400,
    'regular': 400,
    'normal': 400,
    'medium': 500,
    'semibold': 600,
    'demibold': 600,
    'bold': 700,
    'extrabold': 800,
    'ultrabold': 800,
    'black': 900,
    'heavy': 900,
    'extrablack': 950,
    'ultrablack': 950,
}

def clean_family_and_style(font, filepath):
    """
    Extracts and normalizes font family and style from TTFont or filename.
    Replaces SVN prefix with FD.
    """
    names = font['name']
    
    def get_record_string(name_id):
        for pid, eid, lid in [(3, 1, 0x409), (1, 0, 0), (0, 3, 0)]:
            rec = names.getName(name_id, pid, eid, lid)
            if rec:
                try:
                    return rec.toUnicode()
                except Exception:
                    pass
        return None

    typ_fam = get_record_string(16)
    win_fam = get_record_string(1)
    typ_sub = get_record_string(17)
    win_sub = get_record_string(2)

    raw_fam = typ_fam or win_fam or filepath.stem
    raw_sub = typ_sub or win_sub or 'Regular'

    # Strip SVN prefix
    clean_fam = re.sub(r'^[Ss][Vv][Nn][\s\-_]+', '', raw_fam).strip()

    # Detect if clean_fam ends with known weight and win_sub is just Regular/Italic
    for w in sorted(WEIGHT_MAP.keys(), key=len, reverse=True):
        w_title = w.capitalize()
        pattern = re.compile(rf'\b{w}\b', re.IGNORECASE)
        if pattern.search(clean_fam) and (raw_sub.lower() in ['regular', 'italic', '']):
            is_it = 'italic' in raw_sub.lower() or 'italic' in clean_fam.lower()
            clean_fam = pattern.sub('', clean_fam).strip()
            clean_fam = re.sub(r'\s+', ' ', clean_fam).strip()
            raw_sub = f"{w_title} Italic" if is_it else w_title
            break

    # Determine FD prefix
    if clean_fam.startswith('A ') or ' ' in clean_fam:
        fd_family = f"FD {clean_fam}"
    else:
        fd_family = f"FD{clean_fam}"

    # Determine weight class & style flags
    sub_lower = raw_sub.lower()
    is_italic = 'italic' in sub_lower or 'oblique' in sub_lower
    
    weight_class = 400
    for kw, wt in sorted(WEIGHT_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if kw in sub_lower:
            weight_class = wt
            break
            
    is_bold = weight_class >= 700

    return fd_family, raw_sub, weight_class, is_italic, is_bold

def morph_vectors_ttf(font):
    """Apply micro-morphing to TrueType glyf table."""
    glyf = font['glyf']
    hmtx = font['hmtx']
    for gname in font.getGlyphOrder():
        g = glyf[gname]
        if g.numberOfContours > 0:
            coords = g.coordinates
            for i in range(len(coords)):
                x, y = coords[i]
                coords[i] = (round(x * SCALE_X), round(y * SCALE_Y))
            g.recalcBounds(glyf)
        elif g.numberOfContours < 0:
            for comp in g.components:
                if hasattr(comp, 'x'):
                    comp.x = round(comp.x * SCALE_X)
                if hasattr(comp, 'y'):
                    comp.y = round(comp.y * SCALE_Y)
            g.recalcBounds(glyf)
        if gname in hmtx.metrics:
            w, lsb = hmtx.metrics[gname]
            hmtx.metrics[gname] = (round(w * SCALE_X), round(lsb * SCALE_X))

    head = font['head']
    head.xMin = round(head.xMin * SCALE_X)
    head.xMax = round(head.xMax * SCALE_X)
    head.yMin = round(head.yMin * SCALE_Y)
    head.yMax = round(head.yMax * SCALE_Y)

def morph_vectors_cff(font):
    """Apply micro-morphing to OpenType CFF table."""
    cff = font['CFF '].cff
    topDict = cff.topDictIndex[0]
    charStrings = topDict.CharStrings
    t = Transform(SCALE_X, 0, 0, SCALE_Y, 0, 0)
    hmtx = font['hmtx']
    for gname in font.getGlyphOrder():
        if gname in charStrings:
            cs = charStrings[gname]
            old_priv = getattr(cs, 'private', None)
            w = hmtx.metrics[gname][0] if gname in hmtx.metrics else 500
            new_w = round(w * SCALE_X)
            pen = T2CharStringPen(new_w, glyphSet=charStrings)
            trans_pen = TransformPen(pen, t)
            cs.draw(trans_pen)
            new_cs = pen.getCharString()
            if old_priv:
                new_cs.private = old_priv
            charStrings[gname] = new_cs
        if gname in hmtx.metrics:
            w, lsb = hmtx.metrics[gname]
            hmtx.metrics[gname] = (round(w * SCALE_X), round(lsb * SCALE_X))

    topDict.recalcFontBBox()
    head = font['head']
    head.xMin = round(head.xMin * SCALE_X)
    head.xMax = round(head.xMax * SCALE_X)
    head.yMin = round(head.yMin * SCALE_Y)
    head.yMax = round(head.yMax * SCALE_Y)

def sanitize_metadata(font, fd_family, style, weight_class, is_italic, is_bold):
    """Purges all original metadata and applies proprietary FEDU identity."""
    clean_sub = style.replace(' ', '')
    ps_fam = re.sub(r'[^a-zA-Z0-9]', '', fd_family)
    ps_name = f"{ps_fam}-{clean_sub}"
    full_name = f"{fd_family} {style}".strip()
    unique_id = f"1.000;FEDU;{ps_name}"

    # Purge name table
    font['name'].names = []

    # Windows GDI compatible family/subfamily for 4 standard styles
    if style in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
        win_family = fd_family
        win_sub = style
    else:
        win_family = f"{fd_family} {style.replace('Italic', '').strip()}"
        win_sub = 'Italic' if is_italic else 'Regular'

    records = [
        (0, "Copyright (c) 2026 FEDU. All rights reserved."),
        (1, win_family),
        (2, win_sub),
        (3, unique_id),
        (4, full_name),
        (5, "Version 1.000; FEDU Type Foundry"),
        (6, ps_name),
        (7, f"{fd_family} is a proprietary trademark of FEDU."),
        (8, "FEDU Design Team"),
        (9, "FEDU Design Team"),
        (11, "https://fedu.vn"),
        (12, "https://fedu.vn"),
        (13, "Licensed for internal and commercial use within FEDU Ecosystem."),
        (14, "https://fedu.vn/licenses"),
        (16, fd_family),
        (17, style),
    ]

    for name_id, val in records:
        # Platform 3 (Windows Unicode BMP)
        font['name'].setName(val, name_id, 3, 1, 0x409)
        # Platform 1 (Mac Roman)
        font['name'].setName(val, name_id, 1, 0, 0)
        # Platform 0 (Unicode)
        font['name'].setName(val, name_id, 0, 3, 0)

    # OS/2 table
    if 'OS/2' in font:
        os2 = font['OS/2']
        os2.achVendID = b'FEDU'
        os2.usWeightClass = weight_class
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

    # Synchronize head.macStyle to prevent validation warnings
    if 'head' in font:
        head = font['head']
        if is_bold:
            head.macStyle |= (1 << 0)
        else:
            head.macStyle &= ~(1 << 0)
        if is_italic:
            head.macStyle |= (1 << 1)
        else:
            head.macStyle &= ~(1 << 1)

    # CFF table metadata
    if 'CFF ' in font:
        cff = font['CFF '].cff
        topDict = cff.topDictIndex[0]
        topDict.FontName = ps_name
        for attr in ['Notice', 'Copyright', 'FamilyName', 'FullName']:
            if hasattr(topDict, attr):
                delattr(topDict, attr)
            if hasattr(topDict, 'rawDict') and attr in topDict.rawDict:
                del topDict.rawDict[attr]
        topDict.Copyright = "Copyright (c) 2026 FEDU"
        topDict.Notice = "Copyright (c) 2026 FEDU"
        topDict.FamilyName = fd_family
        topDict.FullName = full_name

    # Remove digital signature
    if 'DSIG' in font:
        del font['DSIG']

    return ps_name

def process_single_font(src_path, output_dir=None, install_mac=False, make_web=False):
    """Transforms a single font file into an obfuscated FD font."""
    src_path = Path(src_path)
    if output_dir:
        output_dir = Path(output_dir)

    try:
        font = TTFont(str(src_path))
        is_cff = 'CFF ' in font
        is_glyf = 'glyf' in font

        if not is_cff and not is_glyf:
            return None, "Unsupported outline format (no glyf or CFF table)"

        fd_family, style, weight_class, is_italic, is_bold = clean_family_and_style(font, src_path)

        # 1. Micro-morph vectors
        if is_glyf:
            morph_vectors_ttf(font)
        elif is_cff:
            morph_vectors_cff(font)

        # 2. Sanitize metadata
        ps_name = sanitize_metadata(font, fd_family, style, weight_class, is_italic, is_bold)

        # Determine extension
        ext = '.otf' if is_cff else '.ttf'
        dest_filename = f"{ps_name}{ext}"

        out_file = None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            out_file = output_dir / dest_filename
            font.save(str(out_file))

        # Install to Mac ~/Library/Fonts if requested
        installed_file = None
        if install_mac:
            mac_fonts = Path('/Users/vietmac/Library/Fonts')
            mac_fonts.mkdir(parents=True, exist_ok=True)
            installed_file = mac_fonts / dest_filename
            font.save(str(installed_file))

        # WOFF2
        web_file = None
        if make_web and output_dir:
            web_dir = output_dir / "web"
            web_dir.mkdir(parents=True, exist_ok=True)
            font.flavor = 'woff2'
            web_file = web_dir / f"{ps_name}.woff2"
            font.save(str(web_file))

        return {
            "src": str(src_path),
            "fd_family": fd_family,
            "style": style,
            "ps_name": ps_name,
            "weight_class": weight_class,
            "format": "OTF" if is_cff else "TTF",
            "dest_filename": dest_filename,
            "installed_file": str(installed_file) if installed_file else None,
            "web_file": str(web_file) if web_file else None,
        }, None
    except Exception as e:
        return None, f"Processing error: {e}"

def worker_task(args_tuple):
    fpath, out_dir, install_mac, make_web = args_tuple
    res, err = process_single_font(fpath, output_dir=out_dir, install_mac=install_mac, make_web=make_web)
    return fpath, res, err

def main():
    parser = argparse.ArgumentParser(description="FEDU Font Anti-Detection & Renaming Engine")
    parser.add_argument("--source", type=str, default="/Users/vietmac/Library/Fonts", help="Source folder of fonts")
    parser.add_argument("--output", type=str, default="/Users/vietmac/Documents/CODE/fedu-font/dist/fonts", help="Output directory")
    parser.add_argument("--families", type=str, default=None, help="Comma-separated list of family keywords (e.g. aeonik,acta,poppins)")
    parser.add_argument("--install", action="store_true", help="Install processed fonts directly to macOS ~/Library/Fonts")
    parser.add_argument("--web", action="store_true", help="Generate .woff2 web fonts as well")
    parser.add_argument("--all", action="store_true", help="Process ALL SVN fonts in source folder")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel worker processes")

    args = parser.parse_args()

    src_dir = Path(args.source)
    out_dir = Path(args.output) if args.output else None

    # Find SVN fonts
    all_fonts = list(src_dir.glob("*SVN*")) + list(src_dir.glob("*svn*"))
    all_fonts = [f for f in all_fonts if f.suffix.lower() in ['.ttf', '.otf']]
    all_fonts = sorted(list(set(all_fonts)))

    print(f"==================================================")
    print(f"  FEDU FONT OBFUSCATION & RENAMING ENGINE")
    print(f"==================================================")
    print(f"Found {len(all_fonts)} SVN font files in {src_dir}")

    # Filtering
    if args.families:
        filter_keywords = [k.strip().lower() for k in args.families.split(',')]
        selected_fonts = [f for f in all_fonts if any(kw in f.name.lower() for kw in filter_keywords)]
        print(f"Filtering by families: {filter_keywords} -> {len(selected_fonts)} matching files")
    elif args.all:
        selected_fonts = all_fonts
        print(f"Processing ALL {len(selected_fonts)} SVN fonts")
    else:
        default_keywords = ['aeonik', 'acta', 'poppins', 'gilroy', 'south dakota', 'a love of thunder', 'charter', 'proxima nova']
        selected_fonts = [f for f in all_fonts if any(kw in f.name.lower() for kw in default_keywords)]
        print(f"Using default test suite -> {len(selected_fonts)} files")

    if args.limit and args.limit > 0:
        selected_fonts = selected_fonts[:args.limit]
        print(f"Limited to first {len(selected_fonts)} files")

    if not selected_fonts:
        print("No fonts selected for processing. Exiting.")
        return

    num_workers = args.workers or max(1, (os.cpu_count() or 4))
    print(f"\nProcessing {len(selected_fonts)} fonts using {num_workers} parallel workers...")
    
    tasks = [(str(f), str(out_dir) if out_dir else None, args.install, args.web) for f in selected_fonts]
    
    processed_families = set()
    success_count = 0
    fail_count = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(worker_task, t): t for t in tasks}
        completed_count = 0
        total_tasks = len(tasks)
        
        for future in as_completed(futures):
            fpath_str, res, err = future.result()
            completed_count += 1
            f_name = Path(fpath_str).name
            
            if err:
                print(f"[{completed_count}/{total_tasks}] ❌ {f_name}: {err}")
                fail_count += 1
            else:
                processed_families.add(res['fd_family'])
                success_count += 1
                if completed_count % 50 == 0 or completed_count == total_tasks:
                    print(f"Progress: [{completed_count}/{total_tasks}] ({completed_count/total_tasks*100:.1f}%) | Success: {success_count} | Fail: {fail_count}")

    print(f"\n==================================================")
    print(f"  PROCESSING COMPLETED")
    print(f"==================================================")
    print(f"Total: {len(selected_fonts)} files | Success: {success_count} | Failed: {fail_count}")
    print(f"Total Distinct FD Families created: {len(processed_families)}")

    if args.install:
        print("\n🚀 All processed fonts installed directly to ~/Library/Fonts!")
        print("   Ready for immediate use in Figma, Photoshop, CapCut, Premiere, etc.")

if __name__ == "__main__":
    main()
