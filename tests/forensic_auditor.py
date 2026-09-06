#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FEDU Quality Auditor — Master Forensic & Verification Suite
Author: FEDU Quality Auditor (Opus Autonomous Team)
Role: Comprehensive forensic verification of font renaming, metadata sanitization,
      macOS installation, Google Drive links, and FontHub catalog integrity.
"""

import os
import sys
import re
import json
import time
from pathlib import Path
from fontTools.ttLib import TTFont

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
DOCS_GT_DIR = Path('/Users/vietmac/Documents/font gt')
MAC_FONTS_DIR = Path('/Users/vietmac/Library/Fonts')
CATALOG_PATH = PROJECT_ROOT / 'data' / 'catalog.json'
DRIVE_LINKS_PATH = PROJECT_ROOT / 'data' / 'drive_links.json'
REPORTS_DIR = PROJECT_ROOT / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

GT_ORIGINAL_13 = [
    'Canon', 'Cinetype', 'Eesti', 'Era', 'Flaire', 'Flexa',
    'Haptik', 'Maru', 'Mechanik', 'Pantheon', 'Planar', 'Standard', 'Zirkon'
]
GT_EXTENDED_6 = [
    'America', 'Sectra', 'Walsheim', 'Ultra', 'Alpina', 'Super'
]
ALL_GT_19 = GT_ORIGINAL_13 + GT_EXTENDED_6

GT_FORBIDDEN_KEYWORDS = [
    'grilli type', 'grillitype', 'trial', 'svn', 'styleno.1', 
    'license agreement', 'all rights reserved. grilli'
]

FD_FORBIDDEN_KEYWORDS = [
    'svn', 'styleno.1', 'trial'
]

class ForensicAuditor:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'gt_metadata_audit': {},
            'fd_metadata_audit': {},
            'macos_install_audit': {},
            'drive_audit': {},
            'fonthub_catalog_audit': {},
            'summary': {
                'gt_total_audited': 0,
                'gt_pass': 0,
                'gt_fail': 0,
                'fd_total_audited': 0,
                'fd_pass': 0,
                'fd_fail': 0,
                'mac_gr_count': 0,
                'mac_fd_count': 0,
                'mac_corrupt_count': 0,
                'drive_total_checked': 0,
                'drive_valid': 0,
                'fonthub_gt_covered': 0,
                'fonthub_reviews_present': 0
            }
        }

    def audit_font_metadata(self, font_path, expected_prefix='GR'):
        issues = []
        meta = {}
        try:
            font = TTFont(str(font_path))
        except Exception as e:
            return False, [f'Unparseable font file: {e}'], {}

        if 'OS/2' in font:
            vend_id = font['OS/2'].achVendID
            meta['achVendID'] = vend_id
            if expected_prefix == 'GR' and vend_id in ['GT  ', 'GRIF', 'NONE', 'TRIAL']:
                issues.append(f"OS/2 achVendID contains forbidden vendor: '{vend_id}'")
            elif expected_prefix == 'FD' and vend_id in ['SVN ', 'NONE']:
                issues.append(f"OS/2 achVendID contains forbidden vendor: '{vend_id}'")

        name_records = {}
        forbidden_kws = GT_FORBIDDEN_KEYWORDS if expected_prefix == 'GR' else FD_FORBIDDEN_KEYWORDS
        
        for record in font['name'].names:
            nid = record.nameID
            try:
                val = record.toUnicode()
            except Exception:
                continue
            name_records[nid] = val
            val_lower = val.lower()

            for kw in forbidden_kws:
                if kw in val_lower:
                    issues.append(f"NameID {nid} contains forbidden keyword '{kw}': '{val}'")

            if nid == 1:
                meta['family_name'] = val
                if not val.startswith(f'{expected_prefix} ') and not val.startswith(f'{expected_prefix}-') and val != expected_prefix:
                    issues.append(f"NameID 1 (Family) does not start with '{expected_prefix} ': '{val}'")
            elif nid == 4:
                meta['full_name'] = val
                if not val.startswith(f'{expected_prefix} ') and not val.startswith(f'{expected_prefix}-') and not val.startswith(expected_prefix):
                    issues.append(f"NameID 4 (Full Name) does not start with '{expected_prefix}': '{val}'")
            elif nid == 6:
                meta['ps_name'] = val
                if not val.startswith(expected_prefix):
                    issues.append(f"NameID 6 (PostScript Name) does not start with '{expected_prefix}': '{val}'")
            elif nid == 16:
                meta['typo_family'] = val
                if not val.startswith(f'{expected_prefix} ') and not val.startswith(f'{expected_prefix}-'):
                    issues.append(f"NameID 16 (Typo Family) does not start with '{expected_prefix} ': '{val}'")

        meta['name_records'] = name_records

        if 'CFF ' in font:
            top = font['CFF '].cff.topDictIndex[0]
            cff_fontname = getattr(top, 'FontName', '')
            cff_familyname = getattr(top, 'FamilyName', '')
            cff_fullname = getattr(top, 'FullName', '')
            meta['cff_fontname'] = cff_fontname
            meta['cff_familyname'] = cff_familyname
            meta['cff_fullname'] = cff_fullname

            for kw in forbidden_kws:
                if kw in str(cff_fontname).lower() or kw in str(cff_familyname).lower() or kw in str(cff_fullname).lower():
                    issues.append(f"CFF Table contains forbidden keyword '{kw}'")

        is_clean = (len(issues) == 0)
        return is_clean, issues, meta

    def audit_gt_directory(self):
        print('\n' + '='*60)
        print('▶ [AUDIT 1] Forensic Audit 19 GT Families (Prefix GR & Clean Metadata)')
        print('='*60)

        possible_dirs = [
            DOCS_GT_DIR,
            PROJECT_ROOT / 'dist' / 'fonts' / 'GR',
            PROJECT_ROOT / 'fonts',
            MAC_FONTS_DIR
        ]

        found_gr_files = {}
        for base_dir in possible_dirs:
            if not base_dir.exists():
                continue
            for f in base_dir.glob('**/*'):
                if f.is_file() and f.suffix.lower() in ['.otf', '.ttf']:
                    if f.name.startswith('GR') or f.name.startswith('GR-') or f.name.startswith('GR '):
                        found_gr_files[f.name] = f

        print(f'Total GR font files discovered: {len(found_gr_files)}')
        
        family_stats = {}
        for fam in ALL_GT_19:
            family_stats[fam] = {'styles': 0, 'pass': 0, 'fail': 0, 'issues': [], 'files': []}

        for fname, fpath in sorted(found_gr_files.items()):
            matched_fam = None
            for fam in ALL_GT_19:
                if fam.lower() in fname.lower():
                    matched_fam = fam
                    break
            
            is_clean, issues, meta = self.audit_font_metadata(fpath, expected_prefix='GR')
            self.results['summary']['gt_total_audited'] += 1

            if is_clean:
                self.results['summary']['gt_pass'] += 1
            else:
                self.results['summary']['gt_fail'] += 1

            if matched_fam:
                family_stats[matched_fam]['styles'] += 1
                family_stats[matched_fam]['files'].append(fname)
                if is_clean:
                    family_stats[matched_fam]['pass'] += 1
                else:
                    family_stats[matched_fam]['fail'] += 1
                    family_stats[matched_fam]['issues'].extend(issues)
            
            self.results['gt_metadata_audit'][fname] = {
                'clean': is_clean,
                'issues': issues,
                'meta': meta,
                'path': str(fpath)
            }

        for fam, stats in family_stats.items():
            status = '✅ PASS' if stats['fail'] == 0 and stats['styles'] > 0 else ('⏳ PENDING/BUILDING' if stats['styles'] == 0 else '❌ FAIL')
            print(f"  • Family GR {fam:<12}: {stats['styles']:>3} styles | {stats['pass']} clean | {stats['fail']} issues -> {status}")
            if stats['issues']:
                for iss in stats['issues'][:3]:
                    print(f'      [!] {iss}')

        return family_stats

    def audit_macos_installed_fonts(self):
        print('\n' + '='*60)
        print('▶ [AUDIT 2] macOS Installation Audit (~/Library/Fonts/)')
        print('='*60)

        gr_fonts = []
        fd_fonts = []
        corrupted = []
        ps_names = {}

        for f in MAC_FONTS_DIR.glob('*'):
            if not f.is_file() or f.suffix.lower() not in ['.ttf', '.otf']:
                continue

            name = f.name
            is_gr = name.startswith('GR') or name.startswith('GR-') or name.startswith('GR ')
            is_fd = name.startswith('FD') or name.startswith('FD-') or name.startswith('FD ')

            if not (is_gr or is_fd):
                continue

            size = f.stat().st_size
            if size == 0:
                corrupted.append((name, '0-byte file'))
                continue

            try:
                font = TTFont(str(f))
                num_glyphs = font['maxp'].numGlyphs
                if num_glyphs == 0:
                    corrupted.append((name, 'Zero glyphs'))
                    continue

                ps_name = font['name'].getName(6, 3, 1) or font['name'].getName(6, 1, 0)
                ps_str = ps_name.toUnicode() if ps_name else name
                
                if ps_str in ps_names:
                    prev_f = ps_names[ps_str]
                    if prev_f != name:
                        pass
                else:
                    ps_names[ps_str] = name

                if is_gr:
                    gr_fonts.append(name)
                else:
                    fd_fonts.append(name)

            except Exception as e:
                corrupted.append((name, f'Parse error: {e}'))

        self.results['summary']['mac_gr_count'] = len(gr_fonts)
        self.results['summary']['mac_fd_count'] = len(fd_fonts)
        self.results['summary']['mac_corrupt_count'] = len(corrupted)

        print(f'  • GR fonts installed in macOS : {len(gr_fonts)}')
        print(f'  • FD fonts installed in macOS : {len(fd_fonts)}')
        print(f'  • Corrupted / 0-byte fonts    : {len(corrupted)}')
        if corrupted:
            for c in corrupted[:5]:
                print(f'      ❌ {c[0]}: {c[1]}')

        self.results['macos_install_audit'] = {
            'gr_count': len(gr_fonts),
            'fd_count': len(fd_fonts),
            'corrupt_count': len(corrupted),
            'corrupted_files': corrupted
        }

    def audit_drive_links(self):
        print('\n' + '='*60)
        print('▶ [AUDIT 3] Google Drive Upload & Download Links Audit')
        print('='*60)

        drive_data = {}
        if DRIVE_LINKS_PATH.exists():
            try:
                drive_data = json.loads(DRIVE_LINKS_PATH.read_text(encoding='utf-8'))
            except Exception as e:
                print(f'Error loading drive_links.json: {e}')

        total_checked = 0
        valid_links = 0
        link_issues = []

        families = drive_data.get('families', {})
        for fam_name, fam_info in families.items():
            total_checked += 1
            folder_url = fam_info.get('drive_folder_url', '')
            zip_url = fam_info.get('zip_download_url', '')
            
            url_to_test = zip_url or folder_url
            if not url_to_test:
                link_issues.append((fam_name, 'No drive or zip URL'))
                continue

            if 'drive.google.com' in url_to_test:
                valid_links += 1
            else:
                link_issues.append((fam_name, f'Invalid drive URL format: {url_to_test}'))

        self.results['summary']['drive_total_checked'] = total_checked
        self.results['summary']['drive_valid'] = valid_links

        print(f'  • Total families with Drive entries : {total_checked}')
        print(f'  • Valid Google Drive link format    : {valid_links}')
        print(f'  • Link issues encountered           : {len(link_issues)}')
        if link_issues:
            for iss in link_issues[:5]:
                print(f'      [!] {iss[0]}: {iss[1]}')

    def audit_fonthub_catalog(self):
        print('\n' + '='*60)
        print('▶ [AUDIT 4] FontHub Web Interface & Catalog Data Audit')
        print('='*60)

        if not CATALOG_PATH.exists():
            print(f'❌ Catalog file not found at: {CATALOG_PATH}')
            return

        try:
            catalog = json.loads(CATALOG_PATH.read_text(encoding='utf-8'))
        except Exception as e:
            print(f'❌ Failed to parse catalog.json: {e}')
            return

        fonts = catalog.get('fonts', [])
        print(f'  • Total fonts declared in catalog: {len(fonts)}')

        gt_covered = []
        fonts_with_review = []
        fonts_with_zip = []

        for f in fonts:
            name = f.get('name', '')
            categories = f.get('category', '') or f.get('categories', [])
            tags = f.get('tags', [])
            
            is_gt = False
            if isinstance(categories, list):
                if any('gt' in c.lower() for c in categories):
                    is_gt = True
            elif 'gt' in str(categories).lower():
                is_gt = True

            if any('gt' in t.lower() for t in tags):
                is_gt = True

            is_one_of_19 = any(gt_fam.lower() in name.lower() for gt_fam in ALL_GT_19)

            if is_gt or is_one_of_19:
                gt_covered.append(name)

            review = (f.get('director_notes') or
                      f.get('director_review') or 
                      f.get('typography_critique') or 
                      f.get('director_verdict') or 
                      f.get('nhan_dinh_dao_dien') or
                      f.get('critique'))
            if review and len(str(review).strip()) > 20:
                fonts_with_review.append(name)

            zip_url = f.get('download_url') or f.get('zip_url') or f.get('drive_link') or f.get('drive_url')
            if zip_url and 'drive.google.com' in str(zip_url):
                fonts_with_zip.append(name)

        # Check for forbidden copyright traces in entire catalog
        catalog_str = json.dumps(catalog).lower()
        forbidden_in_cat = [kw for kw in ['grilli type', 'styleno.1'] if kw in catalog_str]

        self.results['summary']['fonthub_gt_covered'] = len(gt_covered)
        self.results['summary']['fonthub_reviews_present'] = len(fonts_with_review)

        print(f'  • GT/GR fonts identified/tagged in catalog : {len(gt_covered)}')
        print(f'  • Fonts with "Director Review" critique     : {len(fonts_with_review)}')
        print(f'  • Fonts with direct Drive download link     : {len(fonts_with_zip)}')
        print(f'  • Forbidden traces in catalog (Grilli/SVN)  : {forbidden_in_cat if forbidden_in_cat else "0 (CLEAN)"}')

    def run_all(self):
        gt_stats = self.audit_gt_directory()
        self.audit_macos_installed_fonts()
        self.audit_drive_links()
        self.audit_fonthub_catalog()
        
        json_out = REPORTS_DIR / 'forensic_audit_latest.json'
        json_out.write_text(json.dumps(self.results, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'\n✔ Full Audit data saved to: {json_out}')
        return self.results

if __name__ == '__main__':
    auditor = ForensicAuditor()
    auditor.run_all()
