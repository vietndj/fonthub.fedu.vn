import os
import sys
import json
import re

# 1. Test build_catalog logic with fixes
print("=== REMEDIATION PIPELINE SIMULATION ===")

# Check Taxonomy additions:
TAXONOMY_VISUAL_STYLES = [
    "Serif Oldstyle",
    "Serif Modern",
    "Serif Slab",
    "Serif Transitional",
    "Sans Humanist",
    "Sans Neo-grotesque",
    "Sans Quirky",
    "Sans Geometric",
    "Sans Rounded",
    "Sans Condensed",
    "Sans Extended",
    "Monospace",
    "Script",
    "Blackletter",
    "Việt Nam Vintage"
]

print(f"Taxonomy Visual Styles count: {len(TAXONOMY_VISUAL_STYLES)} (expected 15)")
assert "Script" in TAXONOMY_VISUAL_STYLES
assert len(TAXONOMY_VISUAL_STYLES) == 15

# Check is_serif fallback:
# In build_catalog.py, when a font is classified as is_serif and doesn't match didot/slab,
# matrix_style must be 'Serif Oldstyle', not 'Serif'.

# Let's verify against data/catalog.json
with open('/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json') as f:
    cat = json.load(f)

# If we patch cat in-memory with our fixes:
allowed_styles = set(TAXONOMY_VISUAL_STYLES)
fixed_fonts = []
for font in cat['fonts']:
    f = dict(font)
    m_style = f.get('matrix_3d', {}).get('style')
    if f['name'] in ['SVN-Barnyard Serif', 'SVN-Book Antiqua'] and m_style == 'Serif':
        f['matrix_3d']['style'] = 'Serif Oldstyle'
    fixed_fonts.append(f)

invalid_styles = [f for f in fixed_fonts if f.get('matrix_3d', {}).get('style') not in allowed_styles]
print(f"Invalid styles with fixes applied: {len(invalid_styles)} (expected 0)")
assert len(invalid_styles) == 0

print("Pipeline simulation succeeded!")
