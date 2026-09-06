#!/usr/bin/env python3
"""
scripts/convert_woff2.py
Automated Font Packaging, WOFF2 Compression & Typographic Anatomy Extractor
for fedu.vn/font Interactive Type Hub.

Features:
1. Converts TTF/OTF fonts to modern WOFF2 using fontTools & brotli.
2. Extracts family name, weight class, x-height, ascender/descender, and Vietnamese support.
3. Supports batch directory processing, filtering (e.g. 'SVN-*'), and dry-run preview.
4. Generates Cloudflare R2 CDN deployment URLs matching data/catalog.json.
5. Verifies 100% of all 134 Vietnamese accented characters (67 lowercase, 67 uppercase).

Usage:
    python3 scripts/convert_woff2.py font.ttf -o font.woff2
    python3 scripts/convert_woff2.py --dir ~/Library/Fonts --filter "SVN-*" -o ./fonts --extract-metadata
    python3 scripts/convert_woff2.py --help
"""

import os
import sys
import json
import glob
import argparse
from typing import Dict, List, Optional, Tuple, Any

try:
    from fontTools.ttLib import TTFont, woff2
    from fontTools import subset
except ImportError:
    print("Error: fonttools is required. Install via: pip install fonttools brotli", file=sys.stderr)
    sys.exit(1)

# All 134 Vietnamese accented characters (67 lowercase, 67 uppercase)
VIETNAMESE_ACCENTED_CHARS = [
    # A (lower & upper)
    'à', 'á', 'ả', 'ã', 'ạ', 'À', 'Á', 'Ả', 'Ã', 'Ạ',
    # Ă
    'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'Ă', 'Ằ', 'Ắ', 'Ẳ', 'Ẵ', 'Ặ',
    # Â
    'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'Â', 'Ầ', 'Ấ', 'Ẩ', 'Ẫ', 'Ậ',
    # E
    'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'È', 'É', 'Ẻ', 'Ẽ', 'Ẹ',
    # Ê
    'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'Ê', 'Ề', 'Ế', 'Ể', 'Ễ', 'Ệ',
    # I
    'ì', 'í', 'ỉ', 'ĩ', 'ị', 'Ì', 'Í', 'Ỉ', 'Ĩ', 'Ị',
    # O
    'ò', 'ó', 'ỏ', 'õ', 'ọ', 'Ò', 'Ó', 'Ỏ', 'Õ', 'Ọ',
    # Ô
    'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'Ô', 'Ồ', 'Ố', 'Ổ', 'Ỗ', 'Ộ',
    # Ơ
    'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'Ơ', 'Ờ', 'Ớ', 'Ở', 'Ỡ', 'Ợ',
    # U
    'ù', 'ú', 'ủ', 'ũ', 'ụ', 'Ù', 'Ú', 'Ủ', 'Ũ', 'Ụ',
    # Ư
    'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'Ư', 'Ừ', 'Ứ', 'Ử', 'Ữ', 'Ự',
    # Y
    'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'Ỳ', 'Ý', 'Ỷ', 'Ỹ', 'Ỵ',
    # Đ
    'đ', 'Đ'
]

CDN_BASE_URL = "https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts"


def extract_font_metadata(font: TTFont, file_path: str) -> Dict[str, Any]:
    """Extracts typography anatomy, names, and Vietnamese glyph support."""
    meta: Dict[str, Any] = {
        "file_name": os.path.basename(file_path),
        "family": "",
        "subfamily": "Regular",
        "full_name": "",
        "postscript_name": "",
        "weight_class": 400,
        "upm": 1000,
        "ascender": 800,
        "descender": -200,
        "x_height": None,
        "cap_height": None,
        "vietnamese_supported_count": 0,
        "vietnamese_fully_supported": False,
        "missing_vietnamese_chars": []
    }

    # 1. Parse name table
    if "name" in font:
        name_table = font["name"]
        for record in name_table.names:
            try:
                text = record.toUnicode()
                if record.nameID == 1 and not meta["family"]:
                    meta["family"] = text
                elif record.nameID == 2 and not meta["subfamily"]:
                    meta["subfamily"] = text
                elif record.nameID == 4 and not meta["full_name"]:
                    meta["full_name"] = text
                elif record.nameID == 6 and not meta["postscript_name"]:
                    meta["postscript_name"] = text
            except Exception:
                continue

    # 2. Parse head, hhea, OS/2 tables
    if "head" in font:
        meta["upm"] = font["head"].unitsPerEm
    if "hhea" in font:
        meta["ascender"] = font["hhea"].ascender
        meta["descender"] = font["hhea"].descender
    if "OS/2" in font:
        os2 = font["OS/2"]
        meta["weight_class"] = getattr(os2, "usWeightClass", 400)
        meta["x_height"] = getattr(os2, "sxHeight", None)
        meta["cap_height"] = getattr(os2, "sCapHeight", None)

    # 3. Check Vietnamese diacritic support via Best Cmap
    try:
        cmap = font.getBestCmap() or {}
        missing = [c for c in VIETNAMESE_ACCENTED_CHARS if ord(c) not in cmap]
        meta["vietnamese_supported_count"] = len(VIETNAMESE_ACCENTED_CHARS) - len(missing)
        meta["vietnamese_fully_supported"] = len(missing) == 0
        meta["missing_vietnamese_chars"] = missing
    except Exception:
        meta["vietnamese_fully_supported"] = False

    return meta


def convert_font_to_woff2(
    input_path: str,
    output_path: str,
    subset_vn: bool = False,
    dry_run: bool = False
) -> Tuple[bool, int, int, Optional[str]]:
    """Converts a font file to WOFF2, optionally applying Vietnamese subsetting."""
    try:
        in_size = os.path.getsize(input_path)
        if dry_run:
            return True, in_size, int(in_size * 0.28), None

        font = TTFont(input_path)

        if subset_vn:
            options = subset.Options()
            options.flavor = "woff2"
            options.desubroutinize = True

            unicodes = set(range(0x20, 0x7F))  # Basic ASCII
            for c in VIETNAMESE_ACCENTED_CHARS:
                unicodes.add(ord(c))
            # Typographic punctuation
            for p in ['“', '”', '‘', '’', '«', '»', '–', '—', '…', '•', '©', '®', '™', '₫', '€']:
                unicodes.add(ord(p))

            subsetter = subset.Subsetter(options=options)
            subsetter.populate(unicodes=unicodes)
            subsetter.subset(font)
        else:
            font.flavor = "woff2"

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        font.save(output_path)
        out_size = os.path.getsize(output_path)
        font.close()
        return True, in_size, out_size, None
    except Exception as e:
        return False, 0, 0, str(e)


def main():
    parser = argparse.ArgumentParser(description="fedu.vn/font WOFF2 Converter & Typography Packaging Utility")
    parser.add_argument("input", nargs="?", help="Input font file (.ttf, .otf) or directory")
    parser.add_argument("-o", "--output", help="Output WOFF2 file path or output directory")
    parser.add_argument("--dir", help="Directory containing fonts to batch convert")
    parser.add_argument("--filter", default="SVN-*", help="Glob filter for batch mode (e.g. 'SVN-*')")
    parser.add_argument("--subset", action="store_true", help="Subset to ASCII + 134 Vietnamese + typography quotes")
    parser.add_argument("--dry-run", action="store_true", help="Simulate conversion without writing files")
    parser.add_argument("--extract-metadata", action="store_true", help="Output typography anatomy JSON")
    parser.add_argument("--stats", action="store_true", default=True, help="Display compression statistics")

    args = parser.parse_args()

    # Determine files to process
    files_to_process = []
    if args.dir:
        expanded_dir = os.path.expanduser(args.dir)
        pattern = os.path.join(expanded_dir, f"{args.filter}.[to][tf][f]")
        files_to_process = glob.glob(pattern)
        # Also search recursively if nothing found at root level
        if not files_to_process:
            for root, _, filenames in os.walk(expanded_dir):
                for fname in filenames:
                    if fname.lower().endswith(('.ttf', '.otf')):
                        if not args.filter or args.filter == "*" or glob.fnmatch.fnmatch(fname, f"{args.filter}.*") or glob.fnmatch.fnmatch(fname, args.filter):
                            files_to_process.append(os.path.join(root, fname))
    elif args.input:
        in_path = os.path.expanduser(args.input)
        if os.path.isdir(in_path):
            for root, _, filenames in os.walk(in_path):
                for fname in filenames:
                    if fname.lower().endswith(('.ttf', '.otf')):
                        files_to_process.append(os.path.join(root, fname))
        elif os.path.isfile(in_path):
            files_to_process = [in_path]

    if not files_to_process:
        parser.print_help()
        print("\nNo font files located matching criteria.", file=sys.stderr)
        sys.exit(1)

    print(f"Located {len(files_to_process)} font file(s) for processing.")
    out_dir = os.path.expanduser(args.output) if args.output else "./fonts"

    total_in_bytes = 0
    total_out_bytes = 0
    metadata_records = []

    for idx, fpath in enumerate(files_to_process, start=1):
        fname = os.path.basename(fpath)
        base_name, _ = os.path.splitext(fname)
        out_path = os.path.join(out_dir, f"{base_name}.woff2") if (os.path.isdir(out_dir) or not args.output or not args.output.endswith('.woff2')) else out_dir

        if args.extract_metadata:
            try:
                font = TTFont(fpath)
                meta = extract_font_metadata(font, fpath)
                meta["woff2_target"] = out_path
                meta["cdn_url"] = f"{CDN_BASE_URL}/{base_name}.woff2"
                metadata_records.append(meta)
                font.close()
            except Exception as e:
                print(f"[{idx}/{len(files_to_process)}] Error reading {fname}: {e}", file=sys.stderr)

        success, in_b, out_b, err = convert_font_to_woff2(fpath, out_path, subset_vn=args.subset, dry_run=args.dry_run)
        if success:
            total_in_bytes += in_b
            total_out_bytes += out_b
            ratio = (out_b / in_b * 100) if in_b > 0 else 0
            mode_tag = "[SUBSET]" if args.subset else "[FULL]"
            print(f"[{idx}/{len(files_to_process)}] {mode_tag} {fname} -> {in_b/1024:.1f}KB -> {out_b/1024:.1f}KB ({ratio:.1f}%)")
        else:
            print(f"[{idx}/{len(files_to_process)}] FAILED {fname}: {err}", file=sys.stderr)

    if total_in_bytes > 0:
        saved_bytes = total_in_bytes - total_out_bytes
        total_ratio = total_out_bytes / total_in_bytes * 100
        print("\n" + "=" * 50)
        print("CONVERSION SUMMARY")
        print("=" * 50)
        print(f"Total Input:   {total_in_bytes / (1024*1024):.2f} MB")
        print(f"Total Output:  {total_out_bytes / (1024*1024):.2f} MB")
        print(f"Space Saved:   {saved_bytes / (1024*1024):.2f} MB ({100 - total_ratio:.1f}% reduction)")
        print("=" * 50)

    if args.extract_metadata and metadata_records:
        meta_file = "font_anatomy_catalog.json"
        with open(meta_file, "w", encoding="utf-8") as mf:
            json.dump(metadata_records, mf, ensure_ascii=False, indent=2)
        print(f"Wrote typographic anatomy for {len(metadata_records)} fonts to {meta_file}")


if __name__ == "__main__":
    main()
