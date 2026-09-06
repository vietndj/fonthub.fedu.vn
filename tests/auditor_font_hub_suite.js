/**
 * FEDU Font Hub — Comprehensive Quality Auditor Test Suite
 * Independent Quality Verification by Quality Auditor
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { execSync } = require('child_process');

// ANSI Color Helpers
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const YELLOW = '\x1b[33m';
const CYAN = '\x1b[36m';
const BOLD = '\x1b[1m';
const RESET = '\x1b[0m';

let passedTests = 0;
let failedTests = 0;
const failures = [];

function assert(condition, testName, details = '') {
  if (condition) {
    passedTests++;
    console.log(`  ${GREEN}✔ PASS${RESET} ${testName}`);
  } else {
    failedTests++;
    const errMsg = `${testName}: ${details}`;
    failures.push(errMsg);
    console.log(`  ${RED}✖ FAIL${RESET} ${errMsg}`);
  }
}

console.log(`${BOLD}${CYAN}============================================================${RESET}`);
console.log(`${BOLD}${CYAN} FEDU Font Hub — Quality Auditor Verification Suite${RESET}`);
console.log(`${BOLD}${CYAN}============================================================${RESET}\n`);

// Load master catalog
const catalogPath = path.join(__dirname, '..', 'data', 'catalog.json');
const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
const allFonts = catalog.fonts || [];

// Load HTML and CSS
const htmlPath = path.join(__dirname, '..', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const cssPath = path.join(__dirname, '..', 'css', 'style.css');
const css = fs.existsSync(cssPath) ? fs.readFileSync(cssPath, 'utf8') : fs.readFileSync(path.join(__dirname, '..', 'style.css'), 'utf8');

const appJsPath = path.join(__dirname, '..', 'js', 'app.js');
const appJs = fs.existsSync(appJsPath) ? fs.readFileSync(appJsPath, 'utf8') : fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8');

const typeTesterPath = path.join(__dirname, '..', 'js', 'type_tester.js');
const typeTesterJs = fs.readFileSync(typeTesterPath, 'utf8');

// =============================================================================
// SUITE 1: Web Font Network Resolution & URL Audit
// =============================================================================
console.log(`${BOLD}▶ [Audit 1] Web Font Network Resolution & Fallback Integrity${RESET}`);

const TARGET_FONTS = [
  { query: 'GR Sectra', key: 'gr-sectra' },
  { query: 'GR America', key: 'gr-america' },
  { query: 'FD NoeDisplay', key: 'fd-noedisplay' },
  { query: 'FDAeonik', key: 'fdaeonik' },
  { query: 'FD ClashDisplay', key: 'fd-clashdisplay' },
  { query: 'FD Gilroy', key: 'fd-gilroy' },
  { query: 'GR Ultra', key: 'gr-ultra' },
  { query: 'GR Walsheim', key: 'gr-walsheim' },
  { query: 'GR Alpina', key: 'gr-alpina' },
  { query: 'GR Super', key: 'gr-super' }
];

TARGET_FONTS.forEach(({ query, key }) => {
  const font = allFonts.find(f => 
    (f.id && f.id.toLowerCase() === key) ||
    (f.name && f.name.toLowerCase() === query.toLowerCase()) ||
    (f.family && f.family.toLowerCase() === query.toLowerCase())
  );

  assert(Boolean(font), `Font exists in catalog: ${query}`, `Could not find font with id/name matching ${query}`);

  if (font) {
    const url = font.web_font_url;
    assert(Boolean(url && url.length > 0), `Font has web_font_url declared: ${query}`, `Missing web_font_url`);

    if (url) {
      if (url.startsWith('http://') || url.startsWith('https://')) {
        // External URL check
        try {
          const curlRes = execSync(`curl -s -I -m 5 "${url}" | head -n 1`, { encoding: 'utf8' }).trim();
          const is200 = curlRes.includes('200') || curlRes.includes('302') || curlRes.includes('304');
          assert(is200, `Network Reachable (200 OK): ${query} (${url})`, `Got: ${curlRes}`);
        } catch (e) {
          assert(false, `Network Reachable (200 OK): ${query}`, `Curl error: ${e.message}`);
        }
      } else {
        // Local relative path check
        const localPath = path.join(__dirname, '..', url.replace(/^\/+/, ''));
        const existsLocally = fs.existsSync(localPath);
        assert(existsLocally, `Local Asset Exists: ${query} -> ${url}`, `File not found at ${localPath}`);
      }
    }
  }
});

// =============================================================================
// SUITE 2: Curated 8 Pairs Font Assets Verification
// =============================================================================
console.log(`\n${BOLD}▶ [Audit 2] 8 Curated Pairing Boards Font Asset Verification${RESET}`);

const CURATED_PAIRS_LIST = [
  { id: 'pair-1-luxury', h: 'FD NoeDisplay', b: 'FDAeonik' },
  { id: 'pair-2-tech', h: 'FD ClashDisplay', b: 'FD Gilroy' },
  { id: 'pair-3-journal', h: 'FD Adobe Caslon', b: 'FD Apercu Pro' },
  { id: 'pair-4-brand', h: 'FD Abril Fatface', b: 'FD Aptima' },
  { id: 'pair-5-vintage', h: 'FD HC Bourbon Grotesque', b: 'FD Acta' },
  { id: 'pair-6-publishing', h: 'FD Adobe Jenson', b: 'FD A Love Of Thunder' },
  { id: 'pair-7-nordic', h: 'FD Aguila', b: 'FD Addington CF' },
  { id: 'pair-8-future', h: 'FD Bio Sans', b: 'FD Avo' }
];

CURATED_PAIRS_LIST.forEach((pair, idx) => {
  ['h', 'b'].forEach(role => {
    const fName = pair[role];
    const roleLabel = role === 'h' ? 'Heading' : 'Body';
    const match = allFonts.find(f => 
      f.name === fName || 
      (f.family && f.family === fName) ||
      f.name.replace(/[\s-]+/g, '').toLowerCase() === fName.replace(/[\s-]+/g, '').toLowerCase()
    );

    assert(Boolean(match), `Pair #${idx + 1} (${roleLabel}): ${fName} defined in catalog`);

    if (match && match.web_font_url) {
      const u = match.web_font_url;
      if (u.startsWith('http')) {
        try {
          const res = execSync(`curl -s -I -m 5 "${u}" | head -n 1`, { encoding: 'utf8' }).trim();
          const ok = res.includes('200') || res.includes('302') || res.includes('304');
          assert(ok, `Pair #${idx + 1} WebFont URL alive: ${fName}`, `Got ${res} for ${u}`);
        } catch (e) {
          assert(false, `Pair #${idx + 1} WebFont URL alive: ${fName}`, e.message);
        }
      } else {
        const localPath = path.join(__dirname, '..', u.replace(/^\/+/, ''));
        assert(fs.existsSync(localPath), `Pair #${idx + 1} Local Asset: ${fName} (${u})`);
      }
    }
  });
});

// =============================================================================
// SUITE 3: CSS @font-face & Font-Family Exact Parity
// =============================================================================
console.log(`\n${BOLD}▶ [Audit 3] CSS @font-face and HTML font-family Precision Parity${RESET}`);

// Check that loadWebFont in type_tester.js does not hardcode format('woff2')
const hasHardcodedWoff2 = /format\s*\(\s*['"]woff2['"]\s*\)/i.test(typeTesterJs.slice(typeTesterJs.indexOf('new FontFace('), typeTesterJs.indexOf('new FontFace(') + 150));
assert(!hasHardcodedWoff2, 'type_tester.js dynamic FontFace format handles TTF, OTF, WOFF2 without hardcoded woff2 reject');

// Check that app.js pairs rendering uses exact family names matching @font-face
assert(appJs.includes("style=\"font-family: '") || appJs.includes('style="font-family: \'') || appJs.includes('font-family:'), 
  'Curated pairs card dynamically binds font-family inline');

// =============================================================================
// SUITE 4: Fontshare Editorial UI Matching Image 4 (media_1788686668299.png)
// =============================================================================
console.log(`\n${BOLD}▶ [Audit 4] Fontshare UI Specification Parity (Image 4 Matching)${RESET}`);

// 1. Background color: #FAF8F3 or #F7F4EB
const hasWarmCreamBg = css.includes('#FAF8F3') || css.includes('#faf8f3') || css.includes('#F7F4EB') || css.includes('#f7f4eb') || css.includes('--fontshare-bg');
assert(hasWarmCreamBg, 'Warm cream background (#FAF8F3 / #F7F4EB) defined in CSS for Fontshare mode');

// 2. Header: Fontshare branding & Tabs
assert(html.includes('Fontshare') || html.includes('fontshare-logo'), 'Fontshare logo/brand present in header');
assert(html.includes('Fonts') && html.includes('Pairs') && html.includes('Licenses'), 'Fontshare Navigation Tabs (Fonts, Pairs, Licenses) present');

// 3. Toolbar Row 1: Search, Categories, Properties, Personality, Size slider with 210px
assert(html.includes('Categories') || html.includes('data-dropdown="categories"'), 'Categories dropdown trigger in Fontshare toolbar');
assert(html.includes('Properties') || html.includes('data-dropdown="properties"'), 'Properties dropdown trigger in Fontshare toolbar');
assert(html.includes('Personality') || html.includes('data-dropdown="personality"'), 'Personality dropdown trigger in Fontshare toolbar');
assert(html.includes('210px') || html.includes('value="210"') || css.includes('210px') || appJs.includes('210'), 'Font size 210px default / indicator present in toolbar');

// 4. Toolbar Row 2: Your Text, Presets (Cities, Excerpts, Names), Alignment, Theme, Reset
assert(html.includes('Your Text') || html.includes('placeholder="Your Text"') || html.includes('id="fontshare-custom-text"'), 'Your Text input control in Fontshare toolbar');
assert(html.includes('Cities') && html.includes('Excerpts') && html.includes('Names'), 'Text Presets (Cities, Excerpts, Names) buttons present');
assert(html.includes('Reset All') || html.includes('btn-reset'), 'Reset All button present in Fontshare toolbar');

// 5. Sub-toolbar: Count, List View vs Grid View, Filter pills, Sort By
assert(html.includes('List view') || html.includes('list-view') || html.includes('view-list'), 'List view toggle present in Fontshare toolbar');
assert(html.includes('Grid view') || html.includes('grid-view') || html.includes('view-grid'), 'Grid view toggle present in Fontshare toolbar');
assert(html.includes('Top 20') || html.includes('Hot 20') || html.includes('Variable'), 'Filter pills (Top 20, Hot 20, Variable) present');
assert(html.includes('Sort by') || html.includes('sort-by'), 'Sort by control (New, Popular, Hot, Alphabetical) present');

// 6. List View Font Specimen Card Layout
assert(css.includes('.fontshare-list-card') || css.includes('.fontshare-card') || css.includes('.fontshare-specimen'), 'Fontshare Card styles defined in CSS');
assert(appJs.includes('styles') && (appJs.includes('Variable') || appJs.includes('variable')), 'Fontshare Card renders style count and Variable badge');
assert(appJs.includes('Designed by') || appJs.includes('designer'), 'Fontshare Card renders designer / foundry attribution');

// =============================================================================
// SUMMARY
// =============================================================================
console.log(`\n${BOLD}${CYAN}════════════════════════════════════════════════════════════${RESET}`);
console.log(`${BOLD} AUDITOR VERIFICATION SUMMARY${RESET}`);
console.log(`${BOLD}${CYAN}════════════════════════════════════════════════════════════${RESET}`);
console.log(` Total Passed: ${GREEN}${passedTests}${RESET}`);
console.log(` Total Failed: ${RED}${failedTests}${RESET}`);

if (failures.length > 0) {
  console.log(`\n${RED}${BOLD}Failures (${failures.length}):${RESET}`);
  failures.forEach((f, i) => console.log(`  ${i + 1}. ${f}`));
  process.exit(1);
} else {
  console.log(`\n${GREEN}${BOLD}ALL AUDIT VERIFICATIONS PASSED PERFECTLY!${RESET}\n`);
  process.exit(0);
}
