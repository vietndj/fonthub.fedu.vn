const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const stylePath = path.join(ROOT, 'style.css');
const cssStylePath = path.join(ROOT, 'css', 'style.css');
const fontsDir = path.join(ROOT, 'fonts');

const diskFiles = fs.readdirSync(fontsDir).filter(f => !fs.statSync(path.join(fontsDir, f)).isDirectory());

const stylesList = [
  { s: "ThinItalic", w: 100, i: true },
  { s: "Thin", w: 100, i: false },
  { s: "HairlineItalic", w: 100, i: true },
  { s: "Hairline", w: 100, i: false },
  { s: "AirItalic", w: 100, i: true },
  { s: "Air", w: 100, i: false },
  { s: "ExtraLightItalic", w: 200, i: true },
  { s: "ExtraLight", w: 200, i: false },
  { s: "UltraLightItalic", w: 200, i: true },
  { s: "UltraLight", w: 200, i: false },
  { s: "XLightItalic", w: 200, i: true },
  { s: "XLight", w: 200, i: false },
  { s: "LightItalic", w: 300, i: true },
  { s: "Light", w: 300, i: false },
  { s: "BookItalic", w: 400, i: true },
  { s: "Book", w: 400, i: false },
  { s: "RegularItalic", w: 400, i: true },
  { s: "Regular", w: 400, i: false },
  { s: "Italic", w: 400, i: true },
  { s: "MediumItalic", w: 500, i: true },
  { s: "Medium", w: 500, i: false },
  { s: "SemiBoldItalic", w: 600, i: true },
  { s: "SemiBold", w: 600, i: false },
  { s: "DemiboldItalic", w: 600, i: true },
  { s: "Demibold", w: 600, i: false },
  { s: "BoldItalic", w: 700, i: true },
  { s: "Bold", w: 700, i: false },
  { s: "ExtraBoldItalic", w: 800, i: true },
  { s: "ExtraBold", w: 800, i: false },
  { s: "XBoldItalic", w: 800, i: true },
  { s: "XBold", w: 800, i: false },
  { s: "HeavyItalic", w: 800, i: true },
  { s: "Heavy", w: 800, i: false },
  { s: "SuperItalic", w: 800, i: true },
  { s: "Super", w: 800, i: false },
  { s: "BlackItalic", w: 900, i: true },
  { s: "Black", w: 900, i: false },
  { s: "PosterItalic", w: 900, i: true },
  { s: "Poster", w: 900, i: false },
  { s: "UltraItalic", w: 900, i: true },
  { s: "Ultra", w: 900, i: false }
];

function parseDiskFile(f) {
  if (!/\.(woff2|otf|ttf)$/i.test(f)) return null;
  const ext = f.split('.').pop().toLowerCase();
  const base = f.replace(/\.(woff2|ttf|otf)$/i, '');
  let stem = base;
  let info = { s: 'Regular', w: 400, i: false };

  if (base.includes('-')) {
    const d = base.lastIndexOf('-');
    stem = base.substring(0, d);
    const rawS = base.substring(d + 1);
    const found = stylesList.find(item => item.s.toLowerCase() === rawS.toLowerCase());
    if (found) info = found;
    else info = { s: rawS, w: 400, i: rawS.toLowerCase().includes('italic') };
  } else {
    for (const item of stylesList) {
      if (base.endsWith(item.s)) {
        stem = base.substring(0, base.length - item.s.length);
        info = item;
        break;
      }
    }
  }
  return { file: f, ext, base, stem, style: info.s, weight: info.w, isItalic: info.i };
}

const parsedFiles = diskFiles.map(parseDiskFile).filter(Boolean);

function generateFamilyCSS(familyNames, fileStemPatterns) {
  const matched = parsedFiles.filter(pf => {
    return fileStemPatterns.some(pat => {
      if (typeof pat === 'string') return pf.stem === pat || pf.stem.toLowerCase() === pat.toLowerCase();
      if (pat instanceof RegExp) return pat.test(pf.stem) || pat.test(pf.base);
      return false;
    });
  });

  const keyMap = {};
  matched.forEach(m => {
    const key = `${m.weight}_${m.isItalic}`;
    if (!keyMap[key] || (keyMap[key].ext !== 'woff2' && m.ext === 'woff2')) {
      keyMap[key] = m;
    }
  });

  const sorted = Object.values(keyMap).sort((a, b) => {
    if (a.weight !== b.weight) return a.weight - b.weight;
    return a.isItalic ? 1 : -1;
  });

  let out = '';
  familyNames.forEach(fam => {
    out += `\n/* ==========================================================================\n   @font-face for ${fam}\n   ========================================================================== */\n`;
    sorted.forEach(m => {
      const format = m.ext === 'woff2' ? 'woff2' : (m.ext === 'otf' ? 'opentype' : 'truetype');
      out += `@font-face {
  font-family: '${fam}';
  src: url('../fonts/${m.file}') format('${format}'),
       url('fonts/${m.file}') format('${format}');
  font-weight: ${m.weight};
  font-style: ${m.isItalic ? 'italic' : 'normal'};
  font-display: swap;
}\n`;
    });
  });

  return out;
}

// 1. Core typefaces
const aeonikCSS = generateFamilyCSS(['FD Aeonik', 'FDAeonik'], ['FDAeonik']);
const gilroyCSS = generateFamilyCSS(['FD Gilroy', 'FDGilroy'], ['FDGilroy']);
const sectraCSS = generateFamilyCSS(['GR Sectra', 'GRSectra', 'GT Sectra', 'GTSectra'], ['GRSectraDisplay', 'GRSectraFine', 'GTSectra', /Sectra/i]);
const actaCSS = generateFamilyCSS(['FD Acta', 'FDActa'], ['FDActa']);

// 2. CoType Families
const cotypeDefs = [
  { names: ['FD Aeonik Soft'], stems: ['FDAeonikSoft'] },
  { names: ['FD Aeonik Condensed'], stems: ['FDAeonikCondensed'] },
  { names: ['FD Aeonik Extended'], stems: ['FDAeonikExtended'] },
  { names: ['FD Aeonik Mono'], stems: ['FDAeonikMono'] },
  { names: ['FD Aeonik Fono'], stems: ['FDAeonikFono'] },
  { names: ['FD Altform'], stems: ['FDAltform'] },
  { names: ['FD Ambit'], stems: ['FDAmbit'] },
  { names: ['FD Coanda'], stems: ['FDCoanda'] },
  { names: ['FD Lock Sans Stencil'], stems: ['FDLockSansStencil'] },
  { names: ['FD Lock Sans'], stems: ['FDLockSans'] },
  { names: ['FD Lock Serif Stencil'], stems: ['FDLockSerifStencil'] },
  { names: ['FD Lock Serif'], stems: ['FDLockSerif'] },
  { names: ['FD Orbikular'], stems: ['FDOrbikular'] },
  { names: ['FDRM Mono', 'FD RM Mono'], stems: ['FDRMMono'] },
  { names: ['FDRM Neue', 'FD RM Neue'], stems: ['FDRMNeue'] },
  { names: ['FD Scandium'], stems: ['FDScandium'] },
  { names: ['FD Druk Wide', 'FDDrukWide'], stems: ['FDDrukWide'] }
];

let cotypeCSS = '';
cotypeDefs.forEach(cd => {
  cotypeCSS += generateFamilyCSS(cd.names, cd.stems);
});

let css = fs.readFileSync(stylePath, 'utf8');

// Replace Core typefaces section
const coreStartMarker = '/* ==========================================================================\n   FEDU FONTHUB — CORE TYPEFACES & LOCAL WEBFONTS (@font-face)\n   ========================================================================== */';
const coreEndMarker = '/* 9. Curated Pairs 3-8 Webfonts */';

const coreIdx = css.indexOf(coreStartMarker);
const coreEndIdx = css.indexOf(coreEndMarker);

if (coreIdx !== -1 && coreEndIdx !== -1) {
  const replacementCore = [
    coreStartMarker,
    '\n',
    sectraCSS,
    aeonikCSS,
    gilroyCSS,
    actaCSS,
    '\n'
  ].join('');
  css = css.substring(0, coreIdx) + replacementCore + css.substring(coreEndIdx);
  console.log('Successfully replaced Core Typefaces section in CSS!');
}

// Replace CoType section (from start marker to end of file)
let ctIdx = css.indexOf('/* FD Aeonik Families (Soft, Condensed, Extended, Mono, Fono) */');
if (ctIdx === -1) {
  ctIdx = css.indexOf('/* ==========================================================================\n   COTYPE TYPEFACES FULL MULTI-WEIGHT WEBFONTS\n   ========================================================================== */');
}

if (ctIdx !== -1) {
  const badgeStart = css.indexOf('/* CoType Foundry Category Chip & Badge */', ctIdx);
  let badgeBlock = '';
  if (badgeStart !== -1) {
    const afterBadge = css.indexOf('/* CoType Webfonts @font-face declarations */', badgeStart);
    if (afterBadge !== -1) {
      badgeBlock = css.substring(badgeStart, afterBadge);
    }
  }

  const replacementCoType = [
    '/* ==========================================================================\n   COTYPE TYPEFACES FULL MULTI-WEIGHT WEBFONTS\n   ========================================================================== */\n',
    badgeBlock,
    '\n',
    cotypeCSS,
    '\n'
  ].join('');

  css = css.substring(0, ctIdx) + replacementCoType;
  console.log('Successfully replaced CoType section in CSS!');
}

// Write to style.css and css/style.css
fs.writeFileSync(stylePath, css, 'utf8');
fs.writeFileSync(cssStylePath, css, 'utf8');
console.log('Updated style.css and css/style.css successfully!');
