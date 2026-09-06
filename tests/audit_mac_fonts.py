#!/usr/bin/env python3
"""
tests/audit_mac_fonts.py
Kiểm thử thư mục font macOS (~/Library/Fonts/)

Tiêu chí nghiệm thu:
1. 5 họ font bảo tồn (acta, aeonik, walsheim, gt sectra, integral) CÒN NGUYÊN VẸN phiên bản cũ.
2. Các font mới GR và FD của các họ này và các họ khác đều đã được cài đặt thành công.
3. Các font SVN-* cũ khác (ngoài 5 họ trên) đã được dọn sạch 100%.
"""

import os
import sys
from pathlib import Path

MAC_FONTS_DIR = Path(os.path.expanduser("~/Library/Fonts"))

def run_mac_font_audit():
    print("=" * 65)
    print(" AUDIT THƯ MỤC FONT MÁY MAC (~/Library/Fonts/)")
    print("=" * 65)

    if not MAC_FONTS_DIR.exists():
        print(f"❌ LỖI: Thư mục {MAC_FONTS_DIR} không tồn tại!")
        return False

    all_files = [f.name for f in MAC_FONTS_DIR.iterdir() if f.is_file()]
    print(f"• Tổng số file font trong ~/Library/Fonts/: {len(all_files)}")

    # -------------------------------------------------------------
    # 1. Kiểm tra 5 họ font bảo tồn (phiên bản cũ nguyên vẹn)
    # -------------------------------------------------------------
    print("\n[KIỂM THỬ 1] 5 họ font bảo tồn (phiên bản cũ):")
    preserved_families = {
        "Acta (SVN-Acta)": [f for f in all_files if f.lower().startswith("svn-acta")],
        "Aeonik (SVN-Aeonik)": [f for f in all_files if f.lower().startswith("svn-aeonik")],
        "Walsheim (SVN-Walsheim)": [f for f in all_files if f.lower().startswith("svn-walsheim")],
        "GT Sectra (GT-Sectra)": [f for f in all_files if "sectra" in f.lower() and f.startswith("GT-")],
        "Integral CF (SVN-IntegralCF)": [f for f in all_files if f.lower().startswith("svn-integral")],
    }

    all_preserved_pass = True
    for fam_name, files in preserved_families.items():
        count = len(files)
        status = "✅ PASS" if count > 0 else "❌ FAIL"
        if count == 0:
            all_preserved_pass = False
        print(f"  - {fam_name:30}: {count:2} files -> {status}")

    # -------------------------------------------------------------
    # 2. Kiểm tra các font mới GR và FD
    # -------------------------------------------------------------
    print("\n[KIỂM THỬ 2] Cài đặt font mới GR và FD:")
    gr_files = [f for f in all_files if f.upper().startswith("GR") and f.lower().endswith((".ttf", ".otf"))]
    fd_files = [f for f in all_files if f.upper().startswith("FD") and f.lower().endswith((".ttf", ".otf"))]

    print(f"  - Font mới chuẩn GR (Grilli Type)  : {len(gr_files):4} files (Yêu cầu > 1000) -> {'✅ PASS' if len(gr_files) >= 1000 else '❌ FAIL'}")
    print(f"  - Font mới chuẩn FD (FEDU Phái Sinh): {len(fd_files):4} files (Yêu cầu > 1800) -> {'✅ PASS' if len(fd_files) >= 1800 else '❌ FAIL'}")

    # Kiểm tra biến thể GR/FD của 5 họ bảo tồn
    specific_checks = {
        "GR Walsheim": len([f for f in gr_files if "walsheim" in f.lower()]),
        "GR Sectra": len([f for f in gr_files if "sectra" in f.lower()]),
        "FD Acta": len([f for f in fd_files if "acta" in f.lower()]),
        "FD Aeonik": len([f for f in fd_files if "aeon" in f.lower()]),
        "FD Integral CF": len([f for f in fd_files if "integral" in f.lower()]),
    }

    all_specific_pass = True
    for fam_name, count in specific_checks.items():
        status = "✅ PASS" if count > 0 else "❌ FAIL"
        if count == 0:
            all_specific_pass = False
        print(f"    + Biến thể mới {fam_name:18}: {count:2} files -> {status}")

    # -------------------------------------------------------------
    # 3. Kiểm tra dọn sạch các font SVN-* khác ngoài 5 họ
    # -------------------------------------------------------------
    print("\n[KIỂM THỬ 3] Dọn sạch font SVN-* cũ khác (ngoài 5 họ):")
    svn_files = [f for f in all_files if f.lower().startswith("svn-")]
    preserved_svn_stems = ("svn-acta", "svn-aeonik", "svn-walsheim", "svn-integral")
    unauthorized_svn = [f for f in svn_files if not f.lower().startswith(preserved_svn_stems)]

    print(f"  - Tổng số file SVN-* còn lại     : {len(svn_files)}")
    print(f"  - Số file SVN-* thuộc 5 họ bảo tồn: {len(svn_files) - len(unauthorized_svn)}")
    print(f"  - Số file SVN-* trái phép khác    : {len(unauthorized_svn)} (Yêu cầu: 0)")

    if unauthorized_svn:
        print(f"  ❌ Phát hiện {len(unauthorized_svn)} font SVN trái phép:")
        for f in unauthorized_svn[:5]:
            print(f"     * {f}")
        clean_svn_pass = False
    else:
        print("  ✅ PASS: 100% font SVN ngoài 5 họ bảo tồn đã được dọn sạch tuyệt đối.")
        clean_svn_pass = True

    # -------------------------------------------------------------
    # TỔNG KẾT
    # -------------------------------------------------------------
    overall_pass = (
        all_preserved_pass and
        (len(gr_files) >= 1000) and
        (len(fd_files) >= 1800) and
        all_specific_pass and
        clean_svn_pass
    )

    print("\n" + "=" * 65)
    print(f"KẾT QUẢ KIỂM THỬ THƯ MỤC FONT MAC: {'✅ 100% PASS TOÀN BỘ' if overall_pass else '❌ PHÁT HIỆN LỖI'}")
    print("=" * 65 + "\n")

    return overall_pass

if __name__ == "__main__":
    success = run_mac_font_audit()
    sys.exit(0 if success else 1)
