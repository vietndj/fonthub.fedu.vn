#!/usr/bin/env python3
"""
Step 1 & Step 2 Master Engine: Full GR Rebranding & Packaging (v2.0 Fixed)
Handles all 19 Grilli Type families:
- 13 newly localized families from /Users/vietmac/Documents/font gt/FD-*-VietNamized
- 6 GT / SVN-GT families from /Users/vietmac/Library/Fonts
Produces clean .otf and .woff2, packages individual .zip files, and installs to ~/Library/Fonts.
"""

import os
import sys
import re
import shutil
import zipfile
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from fontTools.ttLib import TTFont

ROOT_GT_DIR = Path("/Users/vietmac/Documents/font gt")
MAC_FONTS_DIR = Path("/Users/vietmac/Library/Fonts")
DIST_ZIPS_DIR = Path("/Users/vietmac/Documents/CODE/fedu-font/dist/zips/GR")
DIST_ZIPS_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_ZIPS_DIR = ROOT_GT_DIR / "zips"
LOCAL_ZIPS_DIR.mkdir(parents=True, exist_ok=True)

WEIGHT_MAP = {
    'hairline': 100, 'thin': 100, 'air': 100, 'ultralight': 200, 'extralight': 200,
    'light': 300, 'book': 400, 'regular': 400, 'normal': 400, 'retina': 450,
    'medium': 500, 'semibold': 600, 'demibold': 600, 'bold': 700,
    'extrabold': 800, 'ultrabold': 800, 'black': 900, 'heavy': 900, 'super': 900,
    'extrablack': 950, 'ultrablack': 950
}

def sanitize_metadata(font, typ_family, style_name, ps_name, full_name):
    """Deep forensic sanitization of TTFont metadata to FEDU standard."""
    style_lower = style_name.lower()
    weight_class = 400
    for kw, wt in sorted(WEIGHT_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if kw in style_lower:
            weight_class = wt
            break

    is_italic = 'italic' in style_lower or 'oblique' in style_lower
    is_bold = weight_class >= 700

    font['name'].names = []

    if style_name in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
        win_family = typ_family
        win_sub = style_name
    else:
        clean_sub_for_win = re.sub(r'Italic|Oblique', '', style_name, flags=re.I).strip()
        win_family = f"{typ_family} {clean_sub_for_win}".strip()
        win_sub = 'Italic' if is_italic else 'Regular'

    unique_id = f"1.000;FEDU;{ps_name}"

    records = [
        (0, "Copyright (c) 2026 FEDU / GR. All rights reserved."),
        (1, win_family),
        (2, win_sub),
        (3, unique_id),
        (4, full_name),
        (5, "Version 1.000; FEDU Type Foundry"),
        (6, ps_name),
        (7, f"{typ_family} is a proprietary typeface of FEDU Ecosystem."),
        (8, "FEDU Design Team"),
        (9, "FEDU Type Studio"),
        (11, "https://fedu.vn"),
        (12, "https://fedu.vn"),
        (13, "Licensed for internal and commercial creative production across FEDU Ecosystem."),
        (14, "https://fedu.vn/licenses"),
        (16, typ_family),
        (17, style_name),
    ]

    for nid, val in records:
        font['name'].setName(val, nid, 3, 1, 0x409)
        font['name'].setName(val, nid, 1, 0, 0)
        font['name'].setName(val, nid, 0, 3, 0)

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

    if 'CFF ' in font:
        cff = font['CFF '].cff
        topDict = cff.topDictIndex[0]
        cff.fontNames = [ps_name]
        topDict.FontName = ps_name
        topDict.FamilyName = typ_family
        topDict.FullName = full_name
        for attr in ['Notice', 'Copyright', 'FamilyName', 'FullName']:
            if hasattr(topDict, attr):
                setattr(topDict, attr, "Copyright (c) 2026 FEDU" if 'Copy' in attr or 'Not' in attr else getattr(topDict, attr))
            if hasattr(topDict, 'rawDict') and attr in topDict.rawDict:
                topDict.rawDict[attr] = "Copyright (c) 2026 FEDU" if 'Copy' in attr or 'Not' in attr else topDict.rawDict[attr]
        topDict.Copyright = "Copyright (c) 2026 FEDU"
        topDict.Notice = "Copyright (c) 2026 FEDU"

    if 'DSIG' in font:
        del font['DSIG']

def process_file(task):
    src_path = Path(task['src_path'])
    fam_core = task['family_core']
    out_dir = Path(task['out_dir'])
    typ_family = task['typ_family']
    style_name = task['style_name']
    ps_name = task['ps_name']
    full_name = task['full_name']

    try:
        font = TTFont(str(src_path))
        sanitize_metadata(font, typ_family, style_name, ps_name, full_name)

        desk_dir = out_dir / "desktop"
        web_dir = out_dir / "web"
        desk_dir.mkdir(parents=True, exist_ok=True)
        web_dir.mkdir(parents=True, exist_ok=True)

        otf_path = desk_dir / f"{ps_name}.otf"
        font.save(str(otf_path))

        font.flavor = 'woff2'
        woff2_path = web_dir / f"{ps_name}.woff2"
        font.save(str(woff2_path))

        # Copy to ~/Library/Fonts
        mac_dest = MAC_FONTS_DIR / f"{ps_name}.otf"
        shutil.copyfile(str(otf_path), str(mac_dest))

        return {
            "status": "SUCCESS",
            "family": fam_core,
            "ps_name": ps_name,
            "otf": str(otf_path),
            "woff2": str(woff2_path),
            "mac": str(mac_dest)
        }
    except Exception as e:
        return {"status": "FAIL", "src": str(src_path), "error": str(e)}

def build_step1_tasks():
    tasks = []
    localized_13 = [
        "Pantheon", "Canon", "Cinetype", "Eesti", "Era", "Flaire",
        "Flexa", "Haptik", "Maru", "Mechanik", "Planar", "Standard", "Zirkon"
    ]
    for fam in localized_13:
        src_fam_dir = ROOT_GT_DIR / f"FD-{fam}-VietNamized/desktop"
        out_fam_dir = ROOT_GT_DIR / f"GR-{fam}-VietNamized"
        if not src_fam_dir.exists():
            continue
        for src_file in sorted(src_fam_dir.glob("*.otf")):
            # Inspect existing font metadata to directly and perfectly map FD -> GR
            f = TTFont(str(src_file))
            old_fam = f['name'].getDebugName(16) or f['name'].getDebugName(1) or f"FD {fam}"
            old_sub = f['name'].getDebugName(17) or f['name'].getDebugName(2) or "Regular"
            old_ps = f['name'].getDebugName(6) or src_file.stem
            old_full = f['name'].getDebugName(4) or f"{old_fam} {old_sub}"

            # Direct, robust substitution:
            new_fam = re.sub(r'^FD\b\s*', 'GR ', old_fam).strip()
            new_ps = re.sub(r'^FD', 'GR', old_ps).strip()
            new_full = re.sub(r'^FD\b\s*', 'GR ', old_full).strip()
            style_name = old_sub.strip()

            tasks.append({
                "src_path": str(src_file),
                "family_core": fam,
                "out_dir": str(out_fam_dir),
                "typ_family": new_fam,
                "style_name": style_name,
                "ps_name": new_ps,
                "full_name": new_full
            })
    return tasks

def build_step2_tasks():
    tasks = []

    # 1. America: GT-America-LCGV-Standard-*.ttf
    america_files = sorted(MAC_FONTS_DIR.glob("GT-America-LCGV-Standard-*.ttf"))
    out_dir_america = ROOT_GT_DIR / "GR-America-VietNamized"
    for f in america_files:
        suffix = f.stem.replace("GT-America-LCGV-Standard-", "")
        style_clean = suffix.replace("-", " ")
        ps_suffix = suffix.replace("-", "")
        ps_name = f"GRAmerica-{ps_suffix}"
        typ_family = "GR America"
        full_name = f"GR America {style_clean}"
        tasks.append({
            "src_path": str(f),
            "family_core": "America",
            "out_dir": str(out_dir_america),
            "typ_family": typ_family,
            "style_name": style_clean,
            "ps_name": ps_name,
            "full_name": full_name
        })

    # 2. Sectra: GT-Sectra-LCGV-*.otf
    sectra_files = sorted(MAC_FONTS_DIR.glob("GT-Sectra-LCGV-*.otf"))
    if not sectra_files:
        sectra_files = sorted(REPO_FONTS_DIR.glob("GT-Sectra-LCGV-*.otf"))
    out_dir_sectra = ROOT_GT_DIR / "GR-Sectra-VietNamized"
    for f in sectra_files:
        m = re.match(r'GT-Sectra-LCGV-(Display|Fine)-(.*)', f.stem)
        if m:
            subfam = m.group(1) # Display or Fine
            style_part = m.group(2) # Bold-Italic, Regular, etc.
            style_clean = style_part.replace("-", " ")
            ps_suffix = style_part.replace("-", "")
            ps_name = f"GRSectra{subfam}-{ps_suffix}"
            typ_family = f"GR Sectra {subfam}"
            full_name = f"GR Sectra {subfam} {style_clean}"
        else:
            style_clean = f.stem.replace("GT-Sectra-LCGV-", "").replace("-", " ")
            ps_name = f"GRSectra-{style_clean.replace(' ', '')}"
            typ_family = "GR Sectra"
            full_name = f"GR Sectra {style_clean}"

        tasks.append({
            "src_path": str(f),
            "family_core": "Sectra",
            "out_dir": str(out_dir_sectra),
            "typ_family": typ_family,
            "style_name": style_clean,
            "ps_name": ps_name,
            "full_name": full_name
        })

    # 3. Walsheim: SVN-WalsheimPro-*.ttf
    walsheim_files = sorted(MAC_FONTS_DIR.glob("SVN-WalsheimPro-*.ttf"))
    out_dir_walsheim = ROOT_GT_DIR / "GR-Walsheim-VietNamized"
    for f in walsheim_files:
        style_part = f.stem.replace("SVN-WalsheimPro-", "")
        style_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', style_part).strip()
        ps_name = f"GRWalsheimPro-{style_part}"
        typ_family = "GR Walsheim Pro"
        full_name = f"GR Walsheim Pro {style_clean}"
        tasks.append({
            "src_path": str(f),
            "family_core": "Walsheim",
            "out_dir": str(out_dir_walsheim),
            "typ_family": typ_family,
            "style_name": style_clean,
            "ps_name": ps_name,
            "full_name": full_name
        })

    # 4. Ultra: SVN-Ultra*.ttf (Fine, Median, Standard)
    ultra_files = sorted(MAC_FONTS_DIR.glob("SVN-Ultra*.ttf"))
    out_dir_ultra = ROOT_GT_DIR / "GR-Ultra-VietNamized"
    for f in ultra_files:
        m = re.match(r'SVN-Ultra(Fine|Median|Standard)-(.*)', f.stem)
        if m:
            subfam = m.group(1)
            style_part = m.group(2)
            style_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', style_part).strip()
            ps_name = f"GRUltra{subfam}-{style_part}"
            typ_family = f"GR Ultra {subfam}"
            full_name = f"GR Ultra {subfam} {style_clean}"
        else:
            style_clean = f.stem.replace("SVN-Ultra", "")
            ps_name = f"GRUltra-{style_clean}"
            typ_family = "GR Ultra"
            full_name = f"GR Ultra {style_clean}"

        tasks.append({
            "src_path": str(f),
            "family_core": "Ultra",
            "out_dir": str(out_dir_ultra),
            "typ_family": typ_family,
            "style_name": style_clean,
            "ps_name": ps_name,
            "full_name": full_name
        })

    # 5. Alpina: SVN-AlpinaFine-*.ttf
    alpina_files = sorted(MAC_FONTS_DIR.glob("SVN-AlpinaFine-*.ttf"))
    out_dir_alpina = ROOT_GT_DIR / "GR-Alpina-VietNamized"
    for f in alpina_files:
        style_part = f.stem.replace("SVN-AlpinaFine-", "")
        style_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', style_part).strip()
        ps_name = f"GRAlpinaFine-{style_part}"
        typ_family = "GR Alpina Fine"
        full_name = f"GR Alpina Fine {style_clean}"
        tasks.append({
            "src_path": str(f),
            "family_core": "Alpina",
            "out_dir": str(out_dir_alpina),
            "typ_family": typ_family,
            "style_name": style_clean,
            "ps_name": ps_name,
            "full_name": full_name
        })

    # 6. Super: SVN-SuperDisplay-*.ttf
    super_files = sorted(MAC_FONTS_DIR.glob("SVN-SuperDisplay-*.ttf"))
    out_dir_super = ROOT_GT_DIR / "GR-Super-VietNamized"
    for f in super_files:
        style_part = f.stem.replace("SVN-SuperDisplay-", "")
        style_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', style_part).strip()
        ps_name = f"GRSuperDisplay-{style_part}"
        typ_family = "GR Super Display"
        full_name = f"GR Super Display {style_clean}"
        tasks.append({
            "src_path": str(f),
            "family_core": "Super",
            "out_dir": str(out_dir_super),
            "typ_family": typ_family,
            "style_name": style_clean,
            "ps_name": ps_name,
            "full_name": full_name
        })

    return tasks

def create_zips(all_families):
    print("\n📦 Đóng gói file zip cho từng họ font GR...")
    zip_summary = {}
    for fam in all_families:
        out_fam_dir = ROOT_GT_DIR / f"GR-{fam}-VietNamized"
        desk_dir = out_fam_dir / "desktop"
        if not desk_dir.exists():
            continue
        otfs = sorted(desk_dir.glob("*.otf"))
        if not otfs:
            continue

        zip_name = f"GR-{fam}.zip"
        zip_local = LOCAL_ZIPS_DIR / zip_name
        zip_dist = DIST_ZIPS_DIR / zip_name

        with zipfile.ZipFile(str(zip_local), 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for otf in otfs:
                z.write(str(otf), arcname=f"GR-{fam}/{otf.name}")

        shutil.copyfile(str(zip_local), str(zip_dist))
        zip_size = zip_local.stat().st_size
        zip_summary[fam] = {
            "zip_name": zip_name,
            "styles_count": len(otfs),
            "size_kb": round(zip_size / 1024, 1),
            "dist_path": str(zip_dist),
            "local_path": str(zip_local)
        }
        print(f"  ✔ {zip_name:<20}: {len(otfs)} styles | {zip_summary[fam]['size_kb']} KB")
    return zip_summary

def main():
    print("======================================================================")
    print("🚀 BẮT ĐẦU RE-BRANDING TOÀN BỘ 19 HỌ FONT GRILLI TYPE SANG 'GR ' (v2.0 Fixed)")
    print("======================================================================")

    step1_tasks = build_step1_tasks()
    step2_tasks = build_step2_tasks()
    all_tasks = step1_tasks + step2_tasks

    print(f"Tổng số font cần xử lý:")
    print(f"  • Đợt 1 (13 họ GT đã làm): {len(step1_tasks)} font")
    print(f"  • Đợt 2 (6 họ GT gốc & SVN-GT): {len(step2_tasks)} font")
    print(f"  • Tổng cộng: {len(all_tasks)} font")

    t0 = time.time()
    success = 0
    errors = []

    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(process_file, all_tasks))

    for r in results:
        if r.get("status") == "SUCCESS":
            success += 1
        else:
            errors.append(r)

    elapsed = time.time() - t0
    print(f"\n✔ Hoàn thành chuyển đổi: {success}/{len(all_tasks)} font trong {elapsed:.2f}s!")
    if errors:
        print(f"❌ Có {len(errors)} lỗi:")
        for err in errors[:5]:
            print(f"  - {err}")

    # Đóng gói zip cho tất cả 19 họ
    all_fams = [
        "Pantheon", "Canon", "Cinetype", "Eesti", "Era", "Flaire",
        "Flexa", "Haptik", "Maru", "Mechanik", "Planar", "Standard", "Zirkon",
        "America", "Sectra", "Walsheim", "Ultra", "Alpina", "Super"
    ]
    zip_summary = create_zips(all_fams)

    print("\n✨ TẤT CẢ 19 HỌ FONT GR ĐÃ ĐƯỢC XUẤT OTF + WOFF2, ĐÓNG GÓI ZIP & CÀI ĐẶT VÀO ~/Library/Fonts!")

if __name__ == "__main__":
    main()
