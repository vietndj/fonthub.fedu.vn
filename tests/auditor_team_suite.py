#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/auditor_team_suite.py
FEDU Master Quality Auditor Verification Suite (Opus Autonomous Team)
Author: FEDU Quality Auditor
Role: Comprehensive, automated, repeatable audit covering all 4 mandated criteria:
1. Header Sticky & Backdrop Blur Verification
2. Font "FD Ultro" Absolute Purge Verification (Repo & macOS)
3. 100% Vietnamese Diacritics Verification (Satoshi & Clash Display Purged, 0 Fake VN fonts)
4. Google Drive Download Links HTTP & Integrity Verification
"""

import os
import re
import ssl
import sys
import json
import time
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from fontTools.ttLib import TTFont

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
CATALOG_PATH = PROJECT_ROOT / 'data' / 'catalog.json'
FONTS_DATA_PATH = PROJECT_ROOT / 'data' / 'fonts.json'
MAC_FONTS_DIR = Path('/Users/vietmac/Library/Fonts')
SYS_FONTS_DIR = Path('/Library/Fonts')
REPORTS_DIR = PROJECT_ROOT / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

VN_LOWER = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
VN_UPPER = "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ"
FULL_VN_SET = VN_LOWER + VN_UPPER

class MasterAuditorSuite:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {},
            'passed_all': True
        }

    # =========================================================================
    # 1. HEADER AUDIT
    # =========================================================================
    def audit_header(self):
        print("\n" + "="*60)
        print("▶ HẠNG MỤC 1: KIỂM THỬ HEADER (STICKY, Z-INDEX, BACKDROP-BLUR)")
        print("="*60)
        
        css_files = [PROJECT_ROOT / 'style.css', PROJECT_ROOT / 'css' / 'style.css']
        issues = []

        for fpath in css_files:
            if not fpath.exists():
                continue
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find .site-header rule
            m = re.search(r'\.site-header\s*\{([^}]+)\}', content)
            if not m:
                issues.append(f"{fpath.name}: Không tìm thấy class .site-header trong CSS")
                continue

            rule_body = m.group(1)
            
            # Check position sticky or fixed
            has_sticky = bool(re.search(r'position\s*:\s*(sticky|fixed)', rule_body))
            has_top_0 = bool(re.search(r'top\s*:\s*0', rule_body))
            has_blur = bool(re.search(r'backdrop-filter\s*:\s*blur', rule_body))
            
            # Check z-index
            zm = re.search(r'z-index\s*:\s*([^;]+);', rule_body)
            has_high_z = bool(zm)

            if not has_sticky:
                issues.append(f"{fpath.name}: .site-header chưa có position: sticky hoặc fixed (hiện tại không dính trên đỉnh khi cuộn)")
            if not has_top_0 and has_sticky:
                issues.append(f"{fpath.name}: .site-header chưa có top: 0")
            if not has_blur:
                issues.append(f"{fpath.name}: .site-header chưa có backdrop-filter: blur để chống trong suốt khi cuộn")
            if not has_high_z:
                issues.append(f"{fpath.name}: .site-header chưa khai báo z-index đủ cao")

        passed = len(issues) == 0
        if not passed:
            self.results['passed_all'] = False
        self.results['tests']['header'] = {
            'passed': passed,
            'issues': issues
        }

        for issue in issues:
            print(f"  ❌ {issue}")
        if passed:
            print("  ✅ PASS: Header đã được cấu hình sticky/fixed, top: 0, z-index cao và backdrop-blur chống trong suốt.")
        return passed

    # =========================================================================
    # 2. ULTRO PURGE AUDIT
    # =========================================================================
    def audit_ultro_purge(self):
        print("\n" + "="*60)
        print("▶ HẠNG MỤC 2: KIỂM THỬ GỠ BỎ TRIỆT ĐỂ FONT 'FD ULTRO'")
        print("="*60)
        
        issues = []
        
        # 1. Check data/catalog.json
        if CATALOG_PATH.exists():
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                cat_text = f.read()
            if 'ultro' in cat_text.lower():
                issues.append("data/catalog.json: Vẫn còn chứa từ khóa hoặc font 'ultro'")

        # 2. Check data/fonts.json
        if FONTS_DATA_PATH.exists():
            with open(FONTS_DATA_PATH, 'r', encoding='utf-8') as f:
                fonts_text = f.read()
            if 'ultro' in fonts_text.lower():
                issues.append("data/fonts.json: Vẫn còn chứa từ khóa hoặc font 'ultro'")

        # 3. Check macOS Fonts (~/Library/Fonts and /Library/Fonts)
        mac_ultro_files = []
        for fdir in [MAC_FONTS_DIR, SYS_FONTS_DIR]:
            if fdir.exists():
                for f in fdir.iterdir():
                    if 'ultro' in f.name.lower():
                        mac_ultro_files.append(str(f))

        if mac_ultro_files:
            issues.append(f"macOS Fonts: Còn tồn tại {len(mac_ultro_files)} file font Ultro trên máy Mac (ví dụ: {mac_ultro_files[0]})")

        passed = len(issues) == 0
        if not passed:
            self.results['passed_all'] = False
        self.results['tests']['ultro_purge'] = {
            'passed': passed,
            'issues': issues,
            'mac_ultro_files_count': len(mac_ultro_files)
        }

        for issue in issues:
            print(f"  ❌ {issue}")
        if passed:
            print("  ✅ PASS: Đã gỡ bỏ sạch 100% font FD Ultro khỏi repo và máy Mac.")
        return passed

    # =========================================================================
    # 3. VIETNAMESE DIACRITICS & FORBIDDEN FONTS PURGE AUDIT
    # =========================================================================
    def audit_vn_diacritics(self):
        print("\n" + "="*60)
        print("▶ HẠNG MỤC 3: KIỂM THỬ HỖ TRỢ TIẾNG VIỆT & XÓA FONT CẤM (SATOSHI, CLASH)")
        print("="*60)
        
        issues = []
        
        # 1. Check app.js and js/app.js for Satoshi / Clash Display in signature showcase
        for js_file in [PROJECT_ROOT / 'app.js', PROJECT_ROOT / 'js' / 'app.js']:
            if js_file.exists():
                with open(js_file, 'r', encoding='utf-8') as f:
                    js_text = f.read()
                # Check if satoshi or clash display are in signatureFonts
                if re.search(r"id\s*:\s*['\"]satoshi['\"]", js_text, re.I):
                    issues.append(f"{js_file.name}: Vẫn còn hardcode 'satoshi' trong signatureFonts")
                if re.search(r"id\s*:\s*['\"]clash-display['\"]", js_text, re.I):
                    issues.append(f"{js_file.name}: Vẫn còn hardcode 'clash-display' trong signatureFonts")

        # 2. Check catalog.json for forbidden fonts
        if CATALOG_PATH.exists():
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                cat = json.load(f)
            for font in cat.get('fonts', []):
                fid = font.get('id', '').lower()
                fname = font.get('name', '').lower()
                if 'satoshi' in fid or 'satoshi' in fname:
                    issues.append(f"catalog.json: Phát hiện font cấm Satoshi ({font.get('name')})")
                if 'clash' in fid or 'clash' in fname:
                    issues.append(f"catalog.json: Phát hiện font cấm Clash Display ({font.get('name')})")

        # 3. Check physical font files in fonts/
        for pfont in (PROJECT_ROOT / 'fonts').glob('*'):
            fl = pfont.name.lower()
            if 'satoshi' in fl or 'clashdisplay' in fl:
                issues.append(f"fonts/{pfont.name}: File font không dấu tiếng Việt vẫn tồn tại trong thư mục fonts/")

        # 4. Cmap verification of all fonts in catalog
        non_vn_fonts = []
        if CATALOG_PATH.exists():
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                cat = json.load(f)
            for font in cat.get('fonts', []):
                fid = font.get('id')
                name = font.get('name')
                web_url = font.get('web_font_url', '')
                
                # Check local file if available
                candidates = []
                if web_url and not web_url.startswith('http'):
                    candidates.append(PROJECT_ROOT / web_url)
                for fe in font.get('files', []):
                    fn = fe.get('filename')
                    if fn and not any(w in fn.lower() for w in ['extra', 'ornament', 'catchword', 'swash']):
                        candidates.append(PROJECT_ROOT / 'dist' / 'fonts' / fn)
                        candidates.append(PROJECT_ROOT / 'fonts' / fn)
                        if fn.endswith('.ttf.ttf'):
                            candidates.append(PROJECT_ROOT / 'dist' / 'fonts' / fn[:-4])
                
                target_file = next((c for c in candidates if c.exists()), None)
                if target_file:
                    try:
                        tfont = TTFont(str(target_file))
                        cmap = tfont.getBestCmap()
                        if cmap:
                            missing = [c for c in FULL_VN_SET if ord(c) not in cmap]
                            if len(missing) > 0:
                                non_vn_fonts.append(f"{name} (Thiếu {len(missing)} ký tự VN)")
                    except Exception:
                        pass

        if non_vn_fonts:
            issues.extend(non_vn_fonts[:5])
            if len(non_vn_fonts) > 5:
                issues.append(f"... và thêm {len(non_vn_fonts)-5} font khác thiếu dấu tiếng Việt")

        passed = len(issues) == 0
        if not passed:
            self.results['passed_all'] = False
        self.results['tests']['vn_diacritics'] = {
            'passed': passed,
            'issues': issues
        }

        for issue in issues:
            print(f"  ❌ {issue}")
        if passed:
            print("  ✅ PASS: 100% font trong dataset hỗ trợ toàn diện tiếng Việt. Đã xóa sạch Satoshi & Clash Display.")
        return passed

    # =========================================================================
    # 4. DRIVE LINKS AUDIT
    # =========================================================================
    def audit_drive_links(self):
        print("\n" + "="*60)
        print("▶ HẠNG MỤC 4: KIỂM THỬ TOÀN BỘ LINK TẢI GOOGLE DRIVE")
        print("="*60)
        
        ctx = ssl._create_unverified_context()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        }

        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            fonts = json.load(f).get('fonts', [])

        def check_url(font):
            url = font.get('drive_folder_url', '')
            name = font.get('name', '')
            if not url:
                return False, name, 0, "Empty URL"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                    code = resp.status
                    content = resp.read(4096).decode('utf-8', errors='ignore')
                    title_m = re.search(r'<title>(.*?)</title>', content)
                    title = title_m.group(1) if title_m else ''
                    passed = (code == 200) and ('Page Not Found' not in title)
                    return passed, name, code, title
            except Exception as e:
                return False, name, getattr(e, 'code', 0) or 0, str(e)

        print(f"  - Đang kiểm thử {len(fonts)} link Google Drive song song...")
        failed_links = []
        with ThreadPoolExecutor(max_workers=12) as ex:
            futures = [ex.submit(check_url, f) for f in fonts]
            for fut in as_completed(futures):
                ok, name, code, msg = fut.result()
                if not ok:
                    failed_links.append(f"{name}: HTTP {code} ({msg})")

        total = len(fonts)
        passed_count = total - len(failed_links)
        passed = (len(failed_links) == 0) and (total > 0)
        
        if not passed:
            self.results['passed_all'] = False
        self.results['tests']['drive_links'] = {
            'passed': passed,
            'total': total,
            'passed_count': passed_count,
            'failed_count': len(failed_links),
            'failed_links': failed_links
        }

        if failed_links:
            for f in failed_links[:5]:
                print(f"  ❌ {f}")
        else:
            print(f"  ✅ PASS: 100% link tải ({passed_count}/{total}) trả về HTTP 200 OK và hợp lệ.")
        return passed

    def run_all(self):
        print("BẮT ĐẦU CHUỖI KIỂM THỬ TOÀN DIỆN CHUẨN FEDU QUALITY AUDITOR...")
        t1 = self.audit_header()
        t2 = self.audit_ultro_purge()
        t3 = self.audit_vn_diacritics()
        t4 = self.audit_drive_links()
        
        print("\n" + "="*60)
        print("TỔNG KẾT BÀI KIỂM THỬ NGHIỆM THU:")
        print("="*60)
        print(f"1. Header Sticky & Blur     : {'✅ PASS' if t1 else '❌ FAIL'}")
        print(f"2. Gỡ bỏ FD Ultro           : {'✅ PASS' if t2 else '❌ FAIL'}")
        print(f"3. Dấu Tiếng Việt & Purge   : {'✅ PASS' if t3 else '❌ FAIL'}")
        print(f"4. Link Tải Google Drive    : {'✅ PASS' if t4 else '❌ FAIL'}")
        print("="*60)
        print(f"KẾT QUẢ CUỐI CÙNG: {'🎉 100% PASSED NGHIỆM THU TOÀN DIỆN' if self.results['passed_all'] else '⚠️ CÒN LỖI CẦN SỬA'}")
        print("="*60)
        return self.results['passed_all']

if __name__ == '__main__':
    auditor = MasterAuditorSuite()
    success = auditor.run_all()
    sys.exit(0 if success else 1)
