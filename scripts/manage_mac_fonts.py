#!/usr/bin/env python3
"""
scripts/manage_mac_fonts.py
Mac Font Library Manager & Autonomous Installer
1. Scans ~/Library/Fonts
2. Strictly preserves the 5 historical families (Acta, Aeonik, Walsheim, Sectra, Integral)
3. Deletes any legacy SVN/GT fonts not in the 5 preserved families
4. Installs 100% of GR fonts (19 families) and FD fonts (357 families)
5. Installs both legacy and new FD/GR variants of the 5 preserved families side-by-side
"""

import os
import sys
import shutil
from pathlib import Path

MAC_FONTS = Path(os.path.expanduser('~/Library/Fonts'))
REPO_FONTS = Path('/Users/vietmac/Documents/CODE/fedu-font/fonts')
DIST_FONTS = Path('/Users/vietmac/Documents/CODE/fedu-font/dist/fonts')
GT_ROOT = Path('/Users/vietmac/Documents/font gt')

PRESERVED_KEYWORDS = ['acta', 'aeonick', 'aeonik', 'walsheim', 'sectra', 'intergal', 'integral']

def is_preserved(filename: str) -> bool:
    fn = filename.lower()
    return any(k in fn for k in PRESERVED_KEYWORDS)

def main():
    print("======================================================================")
    print("🚀 BẮT ĐẦU QUẢN LÝ VÀ ĐỒNG BỘ FONT HỆ THỐNG MAC (~/Library/Fonts)")
    print("======================================================================")

    # Step 1: Scan current fonts in ~/Library/Fonts
    all_current = [f for f in MAC_FONTS.iterdir() if f.is_file() and not f.name.startswith('.')]
    print(f"Tổng số file font hiện tại trong ~/Library/Fonts: {len(all_current)}")

    # Step 2: Clean legacy SVN/GT fonts that are NOT in the 5 preserved families
    deleted_count = 0
    for f in all_current:
        fn_lower = f.name.lower()
        is_svn = 'svn' in fn_lower
        is_gt = fn_lower.startswith('gt') or '-gt-' in fn_lower or '_gt_' in fn_lower
        
        if (is_svn or is_gt) and not is_preserved(f.name):
            print(f"  🗑️ Xóa font cũ không thuộc diện bảo tồn: {f.name}")
            try:
                f.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"    Lỗi khi xóa {f.name}: {e}")

    print(f"✔ Đã dọn dẹp {deleted_count} font cũ không thuộc diện bảo tồn.")

    # Step 3: Find and install old preserved versions of the 5 families from projects / downloads
    print("\n🔍 Đang tìm kiếm các file font cũ của 5 họ bảo tồn (Acta, Aeonik, Walsheim, Sectra, Integral)...")
    search_dirs = ['/Users/vietmac/Documents', '/Users/vietmac/Downloads']
    found_old_fonts = {}

    for sdir in search_dirs:
        for root, dirs, files in os.walk(sdir):
            if '.git' in root or 'node_modules' in root:
                continue
            for f in files:
                fl = f.lower()
                if not (fl.endswith('.ttf') or fl.endswith('.otf')):
                    continue
                if is_preserved(f):
                    # Check if it's an old naming convention (SVN-*, GT-*, etc.)
                    if 'svn' in fl or 'gt-' in fl or 'gt_' in fl or not (fl.startswith('fd') or fl.startswith('gr')):
                        if f not in found_old_fonts:
                            found_old_fonts[f] = os.path.join(root, f)

    print(f"Tìm thấy {len(found_old_fonts)} file font bảo tồn cũ. Đang cài đặt vào ~/Library/Fonts...")
    restored_preserved = 0
    for fname, fpath in found_old_fonts.items():
        dest = MAC_FONTS / fname
        if not dest.exists():
            try:
                shutil.copyfile(fpath, str(dest))
                restored_preserved += 1
            except Exception as e:
                print(f"  Lỗi cài đặt {fname}: {e}")

    print(f"✔ Đã cài đặt/bảo tồn {len(found_old_fonts)} file font cũ (đã thêm mới {restored_preserved} file).")

    # Step 4: Install all new GR fonts (19 families)
    print("\n📦 Đang cài đặt toàn bộ font GR mới (19 họ)...")
    gr_sources = list(GT_ROOT.glob('GR-*-VietNamized/desktop/*.*')) + [f for f in REPO_FONTS.glob('GR*.*') if f.suffix.lower() in ['.ttf', '.otf']]
    installed_gr = 0
    for gf in gr_sources:
        dest = MAC_FONTS / gf.name
        if not dest.exists():
            try:
                shutil.copyfile(str(gf), str(dest))
                installed_gr += 1
            except Exception as e:
                print(f"  Lỗi cài đặt {gf.name}: {e}")

    print(f"✔ Đã đồng bộ {len(gr_sources)} font GR (cài mới {installed_gr} file).")

    # Step 5: Install all new FD fonts (357 families)
    print("\n📦 Đang cài đặt toàn bộ font FD mới (357 họ)...")
    fd_sources = list(DIST_FONTS.glob('FD*.*')) + [f for f in REPO_FONTS.glob('FD*.*') if f.suffix.lower() in ['.ttf', '.otf']]
    installed_fd = 0
    for ff in fd_sources:
        dest = MAC_FONTS / ff.name
        if not dest.exists():
            try:
                shutil.copyfile(str(ff), str(dest))
                installed_fd += 1
            except Exception as e:
                print(f"  Lỗi cài đặt {ff.name}: {e}")

    print(f"✔ Đã đồng bộ {len(fd_sources)} font FD (cài mới {installed_fd} file).")

    # Step 6: Final Verification Audit
    final_fonts = [f for f in MAC_FONTS.iterdir() if f.is_file() and not f.name.startswith('.')]
    gr_count = len([f for f in final_fonts if f.name.startswith('GR')])
    fd_count = len([f for f in final_fonts if f.name.startswith('FD')])
    preserved_count = len([f for f in final_fonts if is_preserved(f.name)])
    
    print("\n======================================================================")
    print("📊 KẾT QUẢ NGHIỆM THU CÀI ĐẶT FONT TRÊN MAC:")
    print(f"  - Tổng số file font trong ~/Library/Fonts: {len(final_fonts)}")
    print(f"  - Font hệ GR mới (19 họ): {gr_count} files")
    print(f"  - Font hệ FD mới (357 họ): {fd_count} files")
    print(f"  - Font thuộc 5 họ bảo tồn (cả cũ & mới song song): {preserved_count} files")
    print("======================================================================")

if __name__ == '__main__':
    main()
