const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const fontsDir = path.join(ROOT, 'fonts');
const catalogPath = path.join(ROOT, 'data', 'catalog.json');
const fontsPath = path.join(ROOT, 'data', 'fonts.json');

const diskFiles = fs.readdirSync(fontsDir).filter(f => !fs.statSync(path.join(fontsDir, f)).isDirectory());

const stylesList = [
  { s: "ThinItalic", w: 100, i: true, label: "Thin Italic" },
  { s: "Thin", w: 100, i: false, label: "Thin" },
  { s: "HairlineItalic", w: 100, i: true, label: "Hairline Italic" },
  { s: "Hairline", w: 100, i: false, label: "Hairline" },
  { s: "AirItalic", w: 100, i: true, label: "Air Italic" },
  { s: "Air", w: 100, i: false, label: "Air" },
  { s: "ExtraLightItalic", w: 200, i: true, label: "ExtraLight Italic" },
  { s: "ExtraLight", w: 200, i: false, label: "ExtraLight" },
  { s: "UltraLightItalic", w: 200, i: true, label: "UltraLight Italic" },
  { s: "UltraLight", w: 200, i: false, label: "UltraLight" },
  { s: "XLightItalic", w: 200, i: true, label: "XLight Italic" },
  { s: "XLight", w: 200, i: false, label: "XLight" },
  { s: "LightItalic", w: 300, i: true, label: "Light Italic" },
  { s: "Light", w: 300, i: false, label: "Light" },
  { s: "BookItalic", w: 400, i: true, label: "Book Italic" },
  { s: "Book", w: 400, i: false, label: "Book" },
  { s: "RegularItalic", w: 400, i: true, label: "Regular Italic" },
  { s: "Regular", w: 400, i: false, label: "Regular" },
  { s: "Italic", w: 400, i: true, label: "Italic" },
  { s: "MediumItalic", w: 500, i: true, label: "Medium Italic" },
  { s: "Medium", w: 500, i: false, label: "Medium" },
  { s: "SemiBoldItalic", w: 600, i: true, label: "SemiBold Italic" },
  { s: "SemiBold", w: 600, i: false, label: "SemiBold" },
  { s: "DemiboldItalic", w: 600, i: true, label: "DemiBold Italic" },
  { s: "Demibold", w: 600, i: false, label: "DemiBold" },
  { s: "BoldItalic", w: 700, i: true, label: "Bold Italic" },
  { s: "Bold", w: 700, i: false, label: "Bold" },
  { s: "ExtraBoldItalic", w: 800, i: true, label: "ExtraBold Italic" },
  { s: "ExtraBold", w: 800, i: false, label: "ExtraBold" },
  { s: "XBoldItalic", w: 800, i: true, label: "XBold Italic" },
  { s: "XBold", w: 800, i: false, label: "XBold" },
  { s: "HeavyItalic", w: 800, i: true, label: "Heavy Italic" },
  { s: "Heavy", w: 800, i: false, label: "Heavy" },
  { s: "SuperItalic", w: 800, i: true, label: "Super Italic" },
  { s: "Super", w: 800, i: false, label: "Super" },
  { s: "BlackItalic", w: 900, i: true, label: "Black Italic" },
  { s: "Black", w: 900, i: false, label: "Black" },
  { s: "PosterItalic", w: 900, i: true, label: "Poster Italic" },
  { s: "Poster", w: 900, i: false, label: "Poster" },
  { s: "UltraItalic", w: 900, i: true, label: "Ultra Italic" },
  { s: "Ultra", w: 900, i: false, label: "Ultra" }
];

function parseFile(f) {
  const ext = f.split('.').pop().toLowerCase();
  if (!['woff2', 'otf', 'ttf'].includes(ext)) return null;
  const base = f.replace(/\.(woff2|ttf|otf)$/i, '');
  let stem = base;
  let styleInfo = { s: 'Regular', w: 400, i: false, label: 'Regular' };

  if (base.includes('-')) {
    const d = base.lastIndexOf('-');
    stem = base.substring(0, d);
    const rawS = base.substring(d + 1);
    const found = stylesList.find(item => item.s.toLowerCase() === rawS.toLowerCase());
    if (found) styleInfo = found;
    else styleInfo = { s: rawS, w: 400, i: rawS.toLowerCase().includes('italic'), label: rawS };
  } else {
    for (const item of stylesList) {
      if (base.endsWith(item.s)) {
        stem = base.substring(0, base.length - item.s.length);
        styleInfo = item;
        break;
      }
    }
  }
  return { file: f, ext, base, stem, style: styleInfo.label, weight: styleInfo.w, isItalic: styleInfo.i };
}

const parsedDisk = diskFiles.map(parseFile).filter(Boolean);

function getDiskFilesForFont(font) {
  const fNorm = font.name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
  const idNorm = (font.id || '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();

  let webStem = '';
  if (font.web_font_url) {
    const base = font.web_font_url.replace(/^fonts\//, '').replace(/\.(woff2|ttf|otf)$/i, '');
    const d = base.lastIndexOf('-');
    webStem = (d !== -1 ? base.substring(0, d) : base).replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
  }

  // Exact matching first
  let matched = parsedDisk.filter(pd => {
    const sNorm = pd.stem.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
    if (sNorm === fNorm || sNorm === idNorm) return true;
    if (webStem && sNorm === webStem) return true;
    if ((fNorm.startsWith('gr') || fNorm.startsWith('gt')) && sNorm.startsWith(fNorm)) return true;
    return false;
  });

  if (matched.length === 0) {
    matched = parsedDisk.filter(pd => {
      const sNorm = pd.stem.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
      return sNorm.startsWith(fNorm) || fNorm.startsWith(sNorm);
    });
  }

  // Deduplicate by style, prefer woff2
  const byStyle = {};
  matched.forEach(m => {
    if (!byStyle[m.style] || (byStyle[m.style].ext !== 'woff2' && m.ext === 'woff2')) {
      byStyle[m.style] = m;
    }
  });

  const list = Object.values(byStyle);
  list.sort((a, b) => {
    if (a.weight !== b.weight) return a.weight - b.weight;
    if (a.isItalic !== b.isItalic) return a.isItalic ? 1 : -1;
    return a.style.localeCompare(b.style);
  });
  return list;
}

function processCatalog(catalog) {
  let enrichedCount = 0;
  catalog.fonts.forEach(font => {
    const diskList = getDiskFilesForFont(font);
    if (diskList.length > 0) {
      enrichedCount++;
      // Map to files array format
      font.files = diskList.map(df => {
        return {
          filename: df.file,
          style: df.style,
          weight: df.weight,
          ext: df.ext,
          is_italic: df.isItalic,
          size: fs.statSync(path.join(fontsDir, df.file)).size
        };
      });
      font.weights = diskList.map(df => df.style);
      font.files_count = diskList.length;

      // Ensure web_font_url points to a regular or first available woff2
      const reg = diskList.find(d => d.style === 'Regular' && d.ext === 'woff2') ||
                  diskList.find(d => d.ext === 'woff2') ||
                  diskList[0];
      if (reg) {
        font.web_font_url = 'fonts/' + reg.file;
      }
    } else {
      // Clean up double extensions if any
      if (Array.isArray(font.files)) {
        font.files.forEach(f => {
          if (f.filename) {
            f.filename = f.filename.replace(/\.otf\.otf$/i, '.otf').replace(/\.ttf\.ttf$/i, '.ttf');
          }
        });
      }
      if (!Array.isArray(font.weights) || font.weights.length === 0) {
        font.weights = ['Regular'];
      }
    }
  });
  console.log(`Enriched ${enrichedCount} / ${catalog.fonts.length} fonts in catalog.`);
}

const catalogData = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
processCatalog(catalogData);
fs.writeFileSync(catalogPath, JSON.stringify(catalogData, null, 2), 'utf8');

const fontsData = JSON.parse(fs.readFileSync(fontsPath, 'utf8'));
if (Array.isArray(fontsData)) {
  const dummy = { fonts: fontsData };
  processCatalog(dummy);
  fs.writeFileSync(fontsPath, JSON.stringify(dummy.fonts, null, 2), 'utf8');
} else {
  processCatalog(fontsData);
  fs.writeFileSync(fontsPath, JSON.stringify(fontsData, null, 2), 'utf8');
}

console.log('Successfully updated data/catalog.json and data/fonts.json!');
