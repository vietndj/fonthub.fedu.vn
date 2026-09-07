#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safely injects 'studio' field into each font in data/catalog.json and data/fonts.json
without altering or deleting any existing fields (especially 'files').
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "catalog.json"
FONTS_PATH = ROOT / "data" / "fonts.json"

def resolve_studio(font):
    fid = font.get("id", "").lower()
    name = font.get("name", "").lower()
    family = font.get("family", "").lower()
    designer = font.get("designer", "")
    source = font.get("source", "")
    foundry = font.get("foundry", "")
    tags = " ".join(font.get("tags", [])) if isinstance(font.get("tags"), list) else str(font.get("tags", ""))
    
    # 1. Grilli Type
    if fid.startswith("gr-") or "grilli" in designer.lower() or "grilli" in source.lower() or "grilli" in tags.lower() or "gt " in name:
        return "Grilli Type"
        
    # 2. Klim Type Foundry
    if "klim" in designer.lower() or "klim" in source.lower() or "klim" in foundry.lower() or font.get("is_klim"):
        return "Klim Type Foundry"
        
    # 3. Dinamo
    if "dinamo" in designer.lower() or "dinamo" in source.lower() or "dinamo" in foundry.lower() or font.get("is_dinamo") or any(k in fid for k in ["monument-grotesk", "whyte", "diatype", "arizona", "favorit"]):
        return "Dinamo"
        
    # 4. Pangram Pangram
    if "pangram" in designer.lower() or "pangram" in source.lower() or "pangram" in foundry.lower() or font.get("is_pangram") or any(k in fid for k in ["editorial-new", "woodland", "neue-montreal", "right-grotesk", "agrandir", "hatton", "cirka", "formula"]):
        return "Pangram Pangram"
        
    # 5. CoType Foundry
    if fid.startswith("co-") or "cotype" in designer.lower() or "cotype" in source.lower() or "cotype" in foundry.lower() or fid.startswith("fdaeonik"):
        return "CoType Foundry"
        
    # Sharp Type
    if any(k in fid for k in ["sharp-grotesk", "ogg", "centra", "beatrice", "ayer"]) or "sharp type" in designer.lower():
        return "Sharp Type"
        
    # Commercial Type
    if any(k in fid for k in ["canela", "druk", "graphik", "publico"]) or "commercial type" in designer.lower() or "commercial type" in source.lower():
        return "Commercial Type"
        
    # Swiss Typefaces
    if any(k in fid for k in ["suisse", "sangbleu", "euclid"]) or "swiss typefaces" in designer.lower():
        return "Swiss Typefaces"
        
    # Schick Toikka
    if any(k in fid for k in ["saol", "noe-display", "lyon"]) or "schick toikka" in designer.lower():
        return "Schick Toikka"
        
    # Displaay
    if any(k in fid for k in ["reckless", "roobert", "timmons"]) or "displaay" in designer.lower():
        return "Displaay"
        
    # Colophon Foundry
    if any(k in fid for k in ["apercu", "castledown", "mabry", "basis-grotesque"]) or "colophon" in designer.lower():
        return "Colophon Foundry"
        
    # Lineto
    if any(k in fid for k in ["circular", "akkurat", "brown", "replica"]) or "lineto" in designer.lower():
        return "Lineto"
        
    # Hoefler & Co
    if any(k in fid for k in ["gotham", "chronicle", "archer", "mercury", "knockout"]) or "hoefler" in designer.lower():
        return "Hoefler & Co"
        
    # Connary Fagen
    if "connary" in designer.lower() or fid.endswith("-cf") or "-cf-" in fid:
        return "Connary Fagen"
        
    # Radomir Tinkov
    if "gilroy" in fid or "radomir" in designer.lower():
        return "Radomir Tinkov"
        
    # Mark Simonson Studio
    if "proxima" in fid or "simonson" in designer.lower():
        return "Mark Simonson Studio"
        
    # Indian Type Foundry
    if any(k in fid for k in ["satoshi", "clash-display", "general-sans", "cabinet-grotesk", "ranade"]) or "indian type" in designer.lower():
        return "Indian Type Foundry"
        
    # Designer pattern matching
    if designer:
        des = designer.strip()
        m = re.match(r"^([A-Za-z0-9\s&]+)\s*\([^)]+\)$", des)
        if m:
            candidate = m.group(1).strip()
            if candidate in ["TypeTogether", "Adobe Originals", "ITC", "Linotype", "Latinotype", "Monotype", "Bitstream", "URW", "Berthold"]:
                return candidate
        m2 = re.search(r"\((Latinotype|TypeTogether|Linotype|Monotype|ITC|Font Bureau|Dalton Maag|Hoefler|House Industries)\)", des, re.I)
        if m2:
            return m2.group(1)
            
        if any(w in des.lower() for w in ["studio", "studios", "foundry", "type", "creative", "collective", "lab", "typefaces"]):
            clean_des = re.sub(r"\s*/\s*FEDU Type Studio.*$", "", des, flags=re.I).strip()
            if clean_des.lower() in ["fedu type foundry", "fedu type studio"]:
                return "FEDU Type Foundry"
            if clean_des.lower() == "maulanacreative":
                return "Maulana Creative"
            if clean_des and len(clean_des) < 30:
                return clean_des
                
        for ind in ["Santi Rey", "Maulana Creative", "Sarid Ezra", "Set Sail Studios", "Nicky Laatz", "Emil Bertell", "Dhan Studio", "Sam Parrett", "Ian Barnard"]:
            if ind.lower() in des.lower():
                return ind

    if foundry and foundry not in ["None", "null", ""]:
        return foundry
        
    if designer and designer not in ["FEDU Type Foundry", "FEDU Type Studio", "Drive Archive", ""]:
        clean_des = re.sub(r"\s*/\s*FEDU Type Studio.*$", "", designer, flags=re.I).strip()
        if clean_des and len(clean_des) <= 25 and "(" not in clean_des:
            return clean_des

    return "FEDU Type Foundry"

def main():
    print("Injecting studio metadata...")
    # 1. Update data/catalog.json
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    for font in catalog.get("fonts", []):
        font["studio"] = resolve_studio(font)
        
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"✓ Updated {len(catalog.get('fonts', []))} fonts in {CATALOG_PATH}")

    # 2. Update data/fonts.json
    with open(FONTS_PATH, "r", encoding="utf-8") as f:
        fonts = json.load(f)
        
    for font in fonts:
        font["studio"] = resolve_studio(font)
        
    with open(FONTS_PATH, "w", encoding="utf-8") as f:
        json.dump(fonts, f, ensure_ascii=False, indent=2)
    print(f"✓ Updated {len(fonts)} fonts in {FONTS_PATH}")

if __name__ == "__main__":
    main()
