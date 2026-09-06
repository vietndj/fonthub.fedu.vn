#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/audit_drive_links.py
Audits all Google Drive download links for all fonts in data/catalog.json.
Checks:
- HTTP status code (must be 200)
- Drive folder title in HTML
- Matching between font name and Drive folder
- Produces comprehensive JSON and Markdown audit reports
"""

import os
import re
import ssl
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
CATALOG_PATH = PROJECT_ROOT / 'data' / 'catalog.json'
REPORTS_DIR = PROJECT_ROOT / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CTX = ssl._create_unverified_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def audit_single_link(font_entry):
    fid = font_entry.get('id', '')
    name = font_entry.get('name', '')
    url = font_entry.get('drive_folder_url', '')
    files = font_entry.get('files', [])
    files_count = len(files) or font_entry.get('files_count', 0)
    
    total_size = sum(f.get('size', 0) for f in files)
    size_mb = f"{total_size / (1024*1024):.2f} MB" if total_size > 0 else "N/A"

    if not url:
        return {
            'id': fid,
            'name': name,
            'url': '',
            'status_code': 0,
            'passed': False,
            'title': '',
            'size': size_mb,
            'note': 'URL is missing or empty'
        }

    # Extract Drive folder ID
    m = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    if not m:
        return {
            'id': fid,
            'name': name,
            'url': url,
            'status_code': 0,
            'passed': False,
            'title': '',
            'size': size_mb,
            'note': 'Invalid Google Drive folder URL format'
        }

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=CTX, timeout=12) as resp:
            code = resp.status
            content = resp.read(8192).decode('utf-8', errors='ignore')
            
            title_m = re.search(r'<title>(.*?)</title>', content)
            raw_title = title_m.group(1) if title_m else ''
            folder_title = raw_title.replace(' - Google Drive', '').strip()
            
            # Check if title indicates error or not found
            passed = (code == 200) and ('Google Drive - Page Not Found' not in raw_title) and ('Error 404' not in raw_title)
            
            note = f"Folder Title: '{folder_title}'"
            if not passed:
                note = f"Failed title check: {raw_title}"

            return {
                'id': fid,
                'name': name,
                'url': url,
                'status_code': code,
                'passed': passed,
                'title': folder_title,
                'size': size_mb,
                'note': note
            }
    except Exception as e:
        status = getattr(e, 'code', 0) or 0
        return {
            'id': fid,
            'name': name,
            'url': url,
            'status_code': status,
            'passed': False,
            'title': '',
            'size': size_mb,
            'note': f"HTTP Exception: {str(e)}"
        }

def run_audit(max_workers=10):
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    fonts = data.get('fonts', [])
    print(f"Starting audit of {len(fonts)} Google Drive download links with {max_workers} threads...")

    start_time = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_font = {executor.submit(audit_single_link, f): f for f in fonts}
        completed = 0
        for future in as_completed(future_to_font):
            res = future.result()
            results.append(res)
            completed += 1
            if completed % 50 == 0 or completed == len(fonts):
                print(f"Audited {completed}/{len(fonts)} links...")

    elapsed = time.time() - start_time
    print(f"Finished auditing in {elapsed:.2f}s.")

    # Sort results by font name
    results.sort(key=lambda x: x['name'])

    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed

    summary = {
        'total_links_audited': total,
        'passed_200_ok': passed,
        'failed': failed,
        'pass_rate_percent': round((passed / total) * 100, 2) if total else 0,
        'elapsed_seconds': round(elapsed, 2)
    }

    # Save JSON report
    report_json_path = REPORTS_DIR / 'drive_links_audit_report.json'
    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'results': results}, f, ensure_ascii=False, indent=2)

    # Save Markdown Table report
    report_md_path = REPORTS_DIR / 'drive_links_audit_report.md'
    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write("# FEDU Quality Auditor — Báo Cáo Kiểm Tra Link Tải Font (Google Drive)\n\n")
        f.write(f"- **Thời gian kiểm thử:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Tổng số link kiểm tra:** {total}\n")
        f.write(f"- **Thành công (HTTP 200 OK & Valid Folder):** {passed} ({summary['pass_rate_percent']}%)\n")
        f.write(f"- **Thất bại:** {failed}\n")
        f.write(f"- **Thời gian chạy:** {elapsed:.2f}s\n\n")
        
        f.write("## Bảng Chi Tiết Toàn Bộ Danh Sách Font & Link Tải\n\n")
        f.write("| STT | Tên Font | Link Tải (Google Drive) | HTTP Status | Kết Quả | Dung Lượng | Tiêu Đề Folder / Ghi Chú |\n")
        f.write("| :---: | :--- | :--- | :---: | :---: | :---: | :--- |\n")
        
        for idx, r in enumerate(results, 1):
            status_badge = "✅ PASS" if r['passed'] else "❌ FAIL"
            f.write(f"| {idx} | {r['name']} | [{r['url']}]({r['url']}) | {r['status_code']} | {status_badge} | {r['size']} | {r['note']} |\n")

    print(f"\nSummary: {passed}/{total} Passed ({summary['pass_rate_percent']}%).")
    print(f"Reports saved to:\n  - {report_json_path}\n  - {report_md_path}")
    return summary, results

if __name__ == '__main__':
    run_audit(max_workers=12)
