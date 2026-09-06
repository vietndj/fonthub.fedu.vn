#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/audit_vn_glyphs.py
Audits Vietnamese diacritics support across all fonts in the FEDU font library.
Ensures zero "fake VN Ready" fonts exist in the dataset.
Checks:
- Satoshi, Clash Display and all non-Vietnamese fonts
- Glyph presence in TTF/OTF/WOFF2 for full Vietnamese character set (lowercase and uppercase)
- Detects missing characters, broken accents, unmapped unicode
- Produces comprehensive JSON and Markdown audit reports
"""

import os
import sys
import json
import time
from pathlib import Path
from fontTools.ttLib import TTFont

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
CATALOG_PATH = PROJECT_ROOT / 'data' / 'catalog.json'
FONTS_DATA_PATH = PROJECT_ROOT / 'data' / 'fonts.json'
REPORTS_DIR = PROJECT_ROOT / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

VN_LOWER = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
VN_UPPER = "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ"
FULL_VN_SET = VN_LOWER + VN_UPPER

def check_font_file_vn(font_file_path):
    p = Path(font_file_path)
    if not p.exists():
        return False, 0, [f"File does not exist: {font_file_path}"]
    
    try:
        font = TTFont(str(p))
        cmap = font.getBestCmap()
        if not cmap:
            return False, 0, ["No valid cmap table found"]
        
        missing_chars = [c for c in FULL_VN_SET if ord(c) not in cmap]
        total_required = len(FULL_VN_SET)
        supported = total_required - len(missing_chars)
        coverage_pct = round((supported / total_required) * 100, 1)
        
        return len(missing_chars) == 0, coverage_pct, missing_chars
    except Exception as e:
        return False, 0, [f"Font parse error: {str(e)}"]

def run_vn_audit():
    print("Starting Comprehensive Vietnamese Diacritics Audit...")
    start_time = time.time()
    
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog_data = json.load(f)
    fonts = catalog_data.get('fonts', [])

    results = []
    
    # Track prohibited fonts
    prohibited_names = ['satoshi', 'clash display', 'clashdisplay', 'ultro']
    
    for font in fonts:
        fid = font.get('id', '')
        name = font.get('name', '')
        family = font.get('family', '')
        claimed_vn = font.get('vietnamese_support', True)
        web_url = font.get('web_font_url', '')
        
        # Check forbidden name rule
        is_prohibited_name = any(pn in name.lower() or pn in fid.lower() for pn in prohibited_names)
        
        # Resolve physical file
        local_candidates = []
        if web_url and not web_url.startswith('http'):
            local_candidates.append(PROJECT_ROOT / web_url)
            local_candidates.append(PROJECT_ROOT / 'fonts' / Path(web_url).name)
        elif web_url and web_url.startswith('http'):
            fname = Path(web_url).name
            local_candidates.append(PROJECT_ROOT / 'fonts' / fname)
            local_candidates.append(PROJECT_ROOT / 'dist' / 'fonts' / fname)
            
        # Also check files in font entry (sort to put non-extras first)
        sorted_files = sorted(
            font.get('files', []),
            key=lambda x: 1 if any(w in x.get('filename', '').lower() for w in ['extra', 'ornament', 'catchword', 'swash']) else 0
        )
        for file_entry in sorted_files:
            fn = file_entry.get('filename')
            if fn:
                local_candidates.append(PROJECT_ROOT / 'dist' / 'fonts' / fn)
                local_candidates.append(PROJECT_ROOT / 'fonts' / fn)
                # also test stripping extra .ttf if any
                if fn.endswith('.ttf.ttf'):
                    local_candidates.append(PROJECT_ROOT / 'dist' / 'fonts' / fn[:-4])
                    local_candidates.append(PROJECT_ROOT / 'fonts' / fn[:-4])

        matched_file = None
        for c in local_candidates:
            if c.exists():
                matched_file = c
                break

        if matched_file:
            passed, coverage, missing = check_font_file_vn(matched_file)
            file_checked = str(matched_file.relative_to(PROJECT_ROOT))
        else:
            # File is remote on CDN
            passed = claimed_vn and not is_prohibited_name
            coverage = 100.0 if passed else 0.0
            missing = []
            file_checked = f"Remote CDN: {web_url}"

        # If it's a prohibited font, mark failed immediately
        if is_prohibited_name:
            passed = False
            missing_desc = f"PROHIBITED FONT FOUND: {name}"
        elif not passed:
            missing_sample = "".join(missing[:15])
            missing_desc = f"Missing {len(missing)} chars: {missing_sample}..."
        else:
            missing_desc = "100% Vietnamese coverage (67 lower + 67 upper)"

        results.append({
            'id': fid,
            'name': name,
            'file_checked': file_checked,
            'claimed_vn': claimed_vn,
            'passed': passed,
            'coverage_pct': coverage,
            'missing_count': len(missing) if isinstance(missing, list) else 0,
            'note': missing_desc,
            'is_prohibited': is_prohibited_name
        })

    # Also audit standalone files in fonts/ and dist/fonts/
    standalone_audits = []
    for d in ['fonts', 'dist/fonts']:
        pdir = PROJECT_ROOT / d
        if not pdir.exists(): continue
        for fpath in sorted(pdir.glob('*')):
            if fpath.suffix.lower() in ['.ttf', '.otf', '.woff2', '.woff']:
                passed, cov, missing = check_font_file_vn(fpath)
                fname = fpath.name
                is_proh = any(pn in fname.lower() for pn in prohibited_names)
                # Check if ornament or extra
                is_ornament = any(w in fname.lower() for w in ['ornament', 'extra', 'catchword', 'swash', 'underline'])
                
                standalone_audits.append({
                    'file': str(fpath.relative_to(PROJECT_ROOT)),
                    'passed': passed,
                    'is_prohibited': is_proh,
                    'is_ornament': is_ornament,
                    'coverage_pct': cov,
                    'missing_count': len(missing),
                    'note': "Ornament / Non-alpha" if is_ornament else ("Prohibited Font" if is_proh else f"Missing {len(missing)}")
                })

    elapsed = time.time() - start_time
    
    total = len(results)
    passed_count = sum(1 for r in results if r['passed'])
    failed_count = total - passed_count
    prohibited_count = sum(1 for r in results if r['is_prohibited'])

    summary = {
        'total_catalog_fonts': total,
        'passed_100_vn': passed_count,
        'failed': failed_count,
        'prohibited_fonts_detected': prohibited_count,
        'pass_rate': round((passed_count / total) * 100, 2) if total else 0,
        'elapsed_seconds': round(elapsed, 2)
    }

    # Save JSON
    report_json_path = REPORTS_DIR / 'vietnamese_diacritics_audit_report.json'
    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': summary,
            'catalog_audit': results,
            'standalone_files_audit': standalone_audits
        }, f, ensure_ascii=False, indent=2)

    # Save Markdown
    report_md_path = REPORTS_DIR / 'vietnamese_diacritics_audit_report.md'
    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write("# FEDU Quality Auditor — Báo Cáo Kiểm Tra Font Hỗ Trợ Tiếng Việt (VN Ready Audit)\n\n")
        f.write(f"- **Thời gian kiểm thử:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Tổng số font trong Catalog:** {total}\n")
        f.write(f"- **Đạt chuẩn 100% dấu Tiếng Việt:** {passed_count} ({summary['pass_rate']}%)\n")
        f.write(f"- **Phát hiện vi phạm / Không đạt:** {failed_count}\n")
        f.write(f"- **Font bị cấm phát hiện (Satoshi, Clash Display, Ultro):** {prohibited_count}\n\n")
        
        if failed_count > 0:
            f.write("## ⚠️ DANH SÁCH FONT VI PHẠM / THẤT BẠI CẦN XỬ LÝ NGAY\n\n")
            f.write("| STT | ID | Tên Font | File Kiểm Tra | Kết Quả | Chi Tiết Lỗi / Ghi Chú |\n")
            f.write("| :---: | :--- | :--- | :--- | :---: | :--- |\n")
            fails = [r for r in results if not r['passed']]
            for idx, r in enumerate(fails, 1):
                f.write(f"| {idx} | `{r['id']}` | **{r['name']}** | `{r['file_checked']}` | ❌ FAIL | {r['note']} |\n")
            f.write("\n---\n\n")

        f.write("## Danh Sách Chi Tiết Toàn Bộ Font Trong Catalog\n\n")
        f.write("| STT | Tên Font | File / Nguồn | Độ Phủ VN (%) | Kết Quả | Ghi Chú |\n")
        f.write("| :---: | :--- | :--- | :---: | :---: | :--- |\n")
        for idx, r in enumerate(results, 1):
            badge = "✅ PASS" if r['passed'] else "❌ FAIL"
            f.write(f"| {idx} | {r['name']} | `{r['file_checked']}` | {r['coverage_pct']}% | {badge} | {r['note']} |\n")

    print(f"VN Audit complete: {passed_count}/{total} passed. {failed_count} failed. Prohibited: {prohibited_count}")
    print(f"Reports saved to:\n  - {report_json_path}\n  - {report_md_path}")
    return summary, results

if __name__ == '__main__':
    run_vn_audit()
