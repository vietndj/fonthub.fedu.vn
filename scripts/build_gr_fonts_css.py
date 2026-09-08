#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_gr_fonts_css.py
Generates css/gr-fonts.css containing comprehensive @font-face rules
for all 1,036 GR woff2/otf/ttf files in the fonts/ directory.
Supports specific family names, display names, and GR/GT aliases.
"""

import os
import re
from pathlib import Path

ROOT = Path('/Users/vietmac/Documents/CODE/fedu-font')
FONTS_DIR = ROOT / 'fonts'
CSS_OUT = ROOT / 'css' / 'gr-fonts.css'
ROOT_OUT = ROOT / 'gr-fonts.css'

WEIGHT_MAP = [
    ('thinitalic', 100, True),
    ('thin', 100, False),
    ('hairlineitalic', 100, True),
    ('hairline', 100, False),
    ('airitalic', 100, True),
    ('air', 100, False),
    ('extralightitalic', 200, True),
    ('extralight', 200, False),
    ('ultralightitalic', 200, True),
    ('ultralight', 200, False),
    ('xlightitalic', 200, True),
    ('xlight', 200, False),
    ('lightitalic', 300, True),
    ('light', 300, False),
    ('bookitalic', 400, True),
    ('book', 400, False),
    ('regularitalic', 400, True),
    ('regular', 400, False),
    ('italic', 400, True),
    ('oblique', 400, True),
    ('mediumitalic', 500, True),
    ('medium', 500, False),
    ('semibolditalic', 600, True),
    ('semibold', 600, False),
    ('demibolditalic', 600, True),
    ('demibold', 600, False),
    ('bolditalic', 700, True),
    ('bold', 700, False),
    ('ultrabolditalic', 800, True),
    ('ultrabold', 800, False),
    ('extrabolditalic', 800, True),
    ('extrabold', 800, False),
    ('xbolditalic', 800, True),
    ('xbold', 800, False),
    ('heavyitalic', 800, True),
    ('heavy', 800, False),
    ('superitalic', 800, True),
    ('super', 800, False),
    ('blackitalic', 900, True),
    ('black', 900, False),
    ('posteritalic', 900, True),
    ('poster', 900, False),
    ('ultraitalic', 900, True),
    ('ultra', 900, False),
]

def parse_font_file(fname):
    ext = fname.split('.')[-1].lower()
    base = re.sub(r'\.(woff2|ttf|otf)$', '', fname, flags=re.IGNORECASE)
    
    # Determine style, weight, italic
    weight = 400
    is_italic = 'italic' in base.lower() or 'oblique' in base.lower() or 'slant' in base.lower()
    
    clean_lower = base.lower().replace('-', ' ').replace('_', ' ')
    for pattern, w, it in WEIGHT_MAP:
        if pattern in clean_lower:
            weight = w
            is_italic = it
            break
            
    # Determine family name and aliases
    aliases = [base]  # specific file base (e.g. GRSectraFine-Book)
    
    # GR Sectra
    if 'sectra' in base.lower():
        aliases.extend(['GR Sectra', 'GRSectra', 'GT Sectra', 'GTSectra', 'GT-Sectra', 'GR-Sectra'])
        if 'fine' in base.lower():
            aliases.extend(['GR Sectra Fine', 'GRSectraFine', 'GT Sectra Fine'])
        if 'display' in base.lower():
            aliases.extend(['GR Sectra Display', 'GRSectraDisplay', 'GT Sectra Display'])
            
    # GR Walsheim
    elif 'walsheim' in base.lower():
        aliases.extend(['GR Walsheim', 'GRWalsheim', 'GR Walsheim Pro', 'GRWalsheimPro', 'GT Walsheim', 'GTWalsheim', 'GT Walsheim Pro', 'GTWalsheimPro'])
        
    # GR America
    elif 'america' in base.lower():
        aliases.extend(['GR America', 'GRAmerica', 'GT America', 'GTAmerica'])
        
    # GR Alpina
    elif 'alpina' in base.lower():
        aliases.extend(['GR Alpina', 'GRAlpina', 'GT Alpina', 'GTAlpina'])
        
    # GR Super
    elif 'super' in base.lower():
        aliases.extend(['GR Super', 'GRSuper', 'GR Super Display', 'GRSuperDisplay', 'GT Super'])
        
    # GR Ultra
    elif 'ultra' in base.lower():
        aliases.extend(['GR Ultra', 'GRUltra', 'GT Ultra', 'GTUltra'])
        
    # GR Pantheon
    elif 'pantheon' in base.lower():
        aliases.extend(['GR Pantheon', 'GRPantheon', 'GT Pantheon', 'GTPantheon'])
        
    # Other GR fonts
    elif base.startswith('GR'):
        m = re.match(r'^GR([A-Z][a-z]+)', base)
        if m:
            core = m.group(1)
            aliases.extend([f'GR {core}', f'GR{core}', f'GT {core}', f'GT{core}'])

    return {
        'file': fname,
        'format': 'woff2' if ext == 'woff2' else ('opentype' if ext == 'otf' else 'truetype'),
        'weight': weight,
        'style': 'italic' if is_italic else 'normal',
        'aliases': list(dict.fromkeys(aliases))
    }

def main():
    print("Building css/gr-fonts.css ...")
    font_files = [f for f in os.listdir(FONTS_DIR) if f.startswith('GR') and f.endswith(('.woff2', '.otf', '.ttf'))]
    font_files.sort()
    print(f"Found {len(font_files)} GR font files.")
    
    rules = []
    rules.append("/* FEDU FONT — COMPLETE GR FONTS COLLECTION WEBFONTS (@font-face) */\n")
    
    for f in font_files:
        parsed = parse_font_file(f)
        for alias in parsed['aliases']:
            rule = f"""@font-face {{
  font-family: '{alias}';
  src: url('../fonts/{parsed['file']}') format('{parsed['format']}'),
       url('fonts/{parsed['file']}') format('{parsed['format']}');
  font-weight: {parsed['weight']};
  font-style: {parsed['style']};
  font-display: swap;
}}"""
            rules.append(rule)
            
    content = "\n".join(rules) + "\n"
    
    CSS_OUT.write_text(content, encoding='utf-8')
    ROOT_OUT.write_text(content, encoding='utf-8')
    print(f"Wrote {len(rules)} @font-face rules to {CSS_OUT} ({len(content)} bytes)")
    print(f"Copied to {ROOT_OUT}")

if __name__ == '__main__':
    main()
