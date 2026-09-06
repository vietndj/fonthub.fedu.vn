# -*- coding: utf-8 -*-
import json, re, os

print("Building catalog dataset...")

# Load Drive list
with open('/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_spec_miner_survey_1/gdrive_1070_fonts.txt', 'r', encoding='utf-8') as f:
    drive_files = [l.strip() for l in f if l.strip()]

def find_drive_matches(font_name):
    # normalize
    name_clean = re.sub(r'[^a-zA-Z0-9]', '', font_name).lower()
    matches = []
    # alias mapping for special cases
    alias = {
        'gtalpina': 'alpinafine',
        'gtsuper': 'superdisplay',
        'appareoblack': 'hcappareoblack',
        'appareoblackitalic': 'hcappareoblackitalic',
        '1785glcbaskerville': 'hc1785glcbaskerville',
        'broadwaycond': 'hcbroadwaycond',
        'radiantboldcond': 'hcradiantboldcond',
        'bauhaus93': 'hcbauhaus93',
        'belinda': 'hcbelinda',
        'culture': 'hcculture',
        'santoroscript': 'hcsantoroscript',
        'staykool': 'hcstaykool',
        'newyorkclean': 'hcnewyorkclean',
        'carlson': 'hccarlson',
        'carosello': 'hccarosello',
        'steakandcheesecond': 'hcsteakandcheesecondensed',
        'steakandcheeseslab': 'hcsteakandcheeseslab',
        'steakandcheesepen': 'hcsteakandcheesepen',
        'steakandcheese': 'hcsteakandcheese',
        'strenuous': 'hcstrenuous',
        'organgrinder': 'hcorgangrinder',
        'oldnewspapertypes': 'hcoldnewspapertypes',
        'oldstyleitalic': 'hcoldstyleitalic',
        'marvinvisions': 'hcmarvinvisions',
        'maturascriptcapitals': 'hcmaturascriptcapitals',
        'oilvarebase': 'hcoilvarebase',
        'oronteusfinaeus': 'hcoronteusfinaeus',
        'pacifico': 'hcpacifico',
        'quotescaps': 'hcquotescaps',
        'quotesscript': 'hcquotesscript',
        'readone': 'hcreadone',
        'rostrum': 'hcrostrum',
        'spot': 'hcspot',
        'spyroyal': 'hcspyroyal',
        'thepretender': 'hcthepretender',
        'transformacio': 'hctransformacio',
        'aerojonesnf': 'hcaerojonesnf',
        'alterner': 'hcalterner',
        'anasrustytypewriter': 'hcanasrustytypewriter',
        'anchorjack': 'hcanchorjack',
        'bernardmtcond': 'hcbernardmtcond',
        'bourbongrotesque': 'hcbourbongrotesque',
        'bragahuis': 'hcbragahuis',
        'builttitling': 'hcbuilttitling',
        'calvous': 'hccalvous',
        'colombosans': 'hccolombosans',
        'cubanosharp': 'hccubanosharp',
        'cyrene': 'hccyrene',
        'deftonestylus': 'hcdeftonestylus',
        'eastmarket': 'hceastmarket',
        'ekimmezunu': 'hcekimmezunu',
        'elixircircus': 'hcelixircircus',
        'elixirsans': 'hcelixirsans',
        'explorercondensed': 'hcexplorercondensed',
        'gibsonsone': 'hcgibsonsone',
        'gibsonstwo': 'hcgibsonstwo',
        'gneisenauette': 'hcgneisenauette',
        'gorod': 'hcgorod',
        'greengrove': 'hcgreengrove',
        'grindstonedisplay': 'hcgrindstonedisplay',
        'impossibilium': 'hcimpossibilium',
        'jungleadventurer': 'hcjungleadventurer',
        'justoldfashion': 'hcjustoldfashion',
        'kodiak': 'hckodiak',
        'lexington': 'hclexington'
    }
    search_key = alias.get(name_clean, name_clean)
    for df in drive_files:
        df_clean = re.sub(r'[^a-zA-Z0-9]', '', df).lower()
        if search_key in df_clean:
            matches.append(df)
    return matches

print("find_drive_matches ready.")
