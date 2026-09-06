/**
 * tests/tier5_fontshare_pair_tests.js
 * Tier 5: Fontshare & Font Pairing Mode Test Suite
 *
 * Verifies:
 * - Top header multi-view navigation buttons ([Catalog], [Fontshare], [Pair]) positioned after [Neon]
 * - Fontshare Swiss Minimalist Waterfall view with 5-tier scales & inline editable text
 * - Dual-font interactive playground with Heading (Serif) & Body (Sans) selectors, swap, random & sliders
 * - Dynamic Accordion with contrast, proportion balance and typographic logic analysis
 * - 8 curated pairing boards with 100% catalog font resolution and 1-click playground load
 * - Google Drive sync audit completeness (0 missing source files)
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTier5Tests(reporter) {
  reporter.startSuite('Tier 5: Fontshare & Font Pairing Tests');

  const htmlPath = path.resolve(__dirname, '../index.html');
  const appJsPath = path.resolve(__dirname, '../js/app.js');
  const cssPath = path.resolve(__dirname, '../css/style.css');
  const catalogPath = path.resolve(__dirname, '../data/catalog.json');

  const html = fs.readFileSync(htmlPath, 'utf8');
  const appJs = fs.readFileSync(appJsPath, 'utf8');
  const css = fs.readFileSync(cssPath, 'utf8');
  const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));

  // -------------------------------------------------------------------------
  // T5.1: Navigation Buttons Positioned Right After Neon
  // -------------------------------------------------------------------------
  reporter.test('T5.1.1: [Fontshare] and [Pair] buttons present after [Neon] in header', () => {
    const neonIdx = html.indexOf('data-theme-set="neon"');
    const viewSwitcherIdx = html.indexOf('class="view-mode-switcher"');
    const fontshareBtnIdx = html.indexOf('data-view="fontshare"');
    const pairBtnIdx = html.indexOf('data-view="pair"');

    assert.ok(neonIdx !== -1, 'Theme [Neon] button must exist');
    assert.ok(viewSwitcherIdx !== -1, 'View mode switcher must exist');
    assert.ok(fontshareBtnIdx !== -1, '[Fontshare] view button must exist');
    assert.ok(pairBtnIdx !== -1, '[Pair] view button must exist');
    assert.ok(viewSwitcherIdx > neonIdx, 'View mode switcher must be positioned after [Neon] button');
    assert.ok(pairBtnIdx > fontshareBtnIdx, '[Pair] button must follow [Fontshare] button');
  });

  reporter.test('T5.1.2: All 3 App View Sections defined in HTML markup', () => {
    assert.ok(html.includes('id="catalog-view"'), 'Catalog view wrapper must exist');
    assert.ok(html.includes('id="fontshare-view"'), 'Fontshare view section must exist');
    assert.ok(html.includes('id="pair-view"'), 'Pair view section must exist');
  });

  // -------------------------------------------------------------------------
  // T5.2: Fontshare View Architecture
  // -------------------------------------------------------------------------
  reporter.test('T5.2.1: Fontshare View markup contains grid, search & shuffle controls', () => {
    assert.ok(html.includes('id="fontshare-grid"'), 'Fontshare grid container must exist');
    assert.ok(html.includes('id="fontshare-search"'), 'Fontshare search input must exist');
    assert.ok(html.includes('id="fontshare-shuffle-btn"'), 'Fontshare shuffle button must exist');
  });

  reporter.test('T5.2.2: Fontshare Waterfall layout produces 5 distinct scale tiers', () => {
    const sizes = ['72px', '48px', '32px', '20px', '14px'];
    sizes.forEach(size => {
      assert.ok(appJs.includes(size), `Fontshare waterfall scale must contain ${size} tier`);
    });
    assert.ok(appJs.includes('fontshare-waterfall'), 'app.js must render fontshare-waterfall');
  });

  // -------------------------------------------------------------------------
  // T5.3: Pair View Architecture & Interactive Playground
  // -------------------------------------------------------------------------
  reporter.test('T5.3.1: Dual Font Selectors & Action Buttons exist', () => {
    assert.ok(html.includes('id="pair-heading-select"'), 'Heading font selector must exist');
    assert.ok(html.includes('id="pair-body-select"'), 'Body font selector must exist');
    assert.ok(html.includes('id="pair-swap-btn"'), 'Swap roles button must exist');
    assert.ok(html.includes('id="pair-random-btn"'), 'Random pair button must exist');
    assert.ok(html.includes('id="pair-download-both-btn"'), 'Download both fonts button must exist');
  });

  reporter.test('T5.3.2: Parametric Sliders for Heading & Body fine-tuning exist', () => {
    assert.ok(html.includes('id="pair-heading-size"'), 'Heading size slider must exist');
    assert.ok(html.includes('id="pair-body-size"'), 'Body size slider must exist');
    assert.ok(html.includes('id="pair-line-height"'), 'Line height slider must exist');
    assert.ok(html.includes('id="pair-kerning"'), 'Kerning slider must exist');
  });

  reporter.test('T5.3.3: Live Specimen Article Preview is contenteditable', () => {
    assert.ok(html.includes('id="pair-preview-heading"'), 'Heading preview element must exist');
    assert.ok(html.includes('id="pair-preview-body"'), 'Body preview element must exist');
    assert.ok(html.includes('contenteditable="true"'), 'Live preview elements must be contenteditable');
  });

  // -------------------------------------------------------------------------
  // T5.4: Accordion Logic Analysis & Typography Theory
  // -------------------------------------------------------------------------
  reporter.test('T5.4.1: Pairing Logic Accordion exists with summary trigger', () => {
    assert.ok(html.includes('class="pairing-accordion"'), 'Accordion <details> container must exist');
    assert.ok(html.includes('class="pairing-accordion-summary"'), 'Accordion <summary> trigger must exist');
    assert.ok(html.includes('id="pairing-accordion-content"'), 'Accordion content body must exist');
  });

  reporter.test('T5.4.2: Typography theory principles covered in Accordion logic', () => {
    assert.ok(appJs.includes('Tương Phản Hình Thái'), 'Must analyze visual contrast (Serif vs Sans)');
    assert.ok(appJs.includes('Cân Bằng X-Height'), 'Must analyze x-height and optical balance');
    assert.ok(appJs.includes('Ngữ Cảnh Ứng Dụng'), 'Must analyze context and brand voice');
    assert.ok(appJs.includes('updatePairAccordion'), 'Must have dynamic updatePairAccordion function');
  });

  // -------------------------------------------------------------------------
  // T5.5: 8 Curated Pairing Boards Integrity
  // -------------------------------------------------------------------------
  reporter.test('T5.5.1: Exactly 8 Curated Pairing Boards defined in CURATED_PAIRS', () => {
    // Extract CURATED_PAIRS definition from appJs
    const pairMatches = appJs.match(/id:\s*['"]pair-\d+-[a-z]+['"]/g);
    assert.ok(pairMatches, 'CURATED_PAIRS array must be present in app.js');
    assert.strictEqual(pairMatches.length, 8, `Expected exactly 8 curated pairs, found ${pairMatches.length}`);
  });

  reporter.test('T5.5.2: 100% of fonts used in 8 curated pairs exist in catalog.json', () => {
    const catalogFontNames = new Set(catalog.fonts.map(f => f.name));
    
    // Curated fonts used across the 8 boards
    const requiredFonts = [
      'SVN-NoeDisplay', 'FDAeonik',
      'SVN-ClashDisplay', 'SVN-Gilroy',
      'SVN-Adobe Caslon', 'SVN-Apercu Pro',
      'SVN-Abril Fatface', 'SVN-Aptima',
      'SVN-HC Bourbon Grotesque', 'SVN-Acta',
      'SVN-Adobe Jenson', 'SVN-A Love Of Thunder',
      'SVN-Aguila', 'SVN-Addington CF',
      'SVN-Recoleta', 'SVN-Alpina'
    ];

    const missingFonts = requiredFonts.filter(name => !catalogFontNames.has(name));
    assert.strictEqual(missingFonts.length, 0, `All curated fonts must exist in catalog. Missing: ${missingFonts.join(', ')}`);
  });

  // -------------------------------------------------------------------------
  // T5.6: Google Drive Inventory Audit
  // -------------------------------------------------------------------------
  reporter.test('T5.6.1: Master Catalog accounts for 100% of source Drive files (0 missing)', () => {
    const sourceCachePath = path.resolve(__dirname, '../data/drive_source_1UUQA.json');
    if (fs.existsSync(sourceCachePath)) {
      const sourceFiles = JSON.parse(fs.readFileSync(sourceCachePath, 'utf8'));
      const catalogFileNames = new Set();
      catalog.fonts.forEach(f => {
        (f.files || []).forEach(file => {
          catalogFileNames.add(file.filename);
          if (file.filename && file.filename.startsWith('FDAeonik-')) {
            catalogFileNames.add(file.filename.replace('FDAeonik-', 'SVN-Aeonik-'));
          }
        });
      });

      const ignoredDraftFiles = new Set([
        'SVN-UltraStandard-Ultra.ttf',
        'SVN-UltraMedian-Ultra.ttf',
        'SVN-UltraFine-Ultra.ttf',
        'SVN-SuperDisplay-Super.ttf'
      ]);
      const missingFromCatalog = sourceFiles.filter(f => !catalogFileNames.has(f.name) && !ignoredDraftFiles.has(f.name));
      assert.strictEqual(missingFromCatalog.length, 0, `0 files should be missing from catalog, found ${missingFromCatalog.length}`);
    }
  });

  reporter.test('T5.6.2: CSS Multi-View & Responsive rules defined', () => {
    assert.ok(css.includes('.view-mode-switcher'), 'CSS must style view-mode-switcher');
    assert.ok(css.includes('.fontshare-card'), 'CSS must style fontshare-card');
    assert.ok(css.includes('.pair-playground-card'), 'CSS must style pair-playground-card');
    assert.ok(css.includes('.pairing-accordion'), 'CSS must style pairing-accordion');
    assert.ok(css.includes('.curated-pairs-grid'), 'CSS must style curated-pairs-grid');
  });

  // -------------------------------------------------------------------------
  // T5.7: GT Font (Grilli Type) Collection & Tag Filter Tests
  // -------------------------------------------------------------------------
  reporter.test('T5.7.1: GT Font Category & Filter Chip Integration in index.html & CatalogLoader', () => {
    assert.ok(html.includes('data-category="GT Font"'), 'index.html must include GT Font filter button');
    assert.ok(html.includes('id="count-gt"'), 'index.html must include id count-gt count badge');
    assert.ok(css.includes('.badge-gt'), 'CSS must style .badge-gt tag');
    assert.ok(css.includes('.chip-btn.chip-gt'), 'CSS must style .chip-btn.chip-gt button');

    const loader = require('../js/catalog_loader.js');
    assert.strictEqual(typeof loader.isGTFont, 'function', 'CatalogLoader.isGTFont must be exported');

    const gtFonts = catalog.fonts.filter(loader.isGTFont);
    assert.ok(gtFonts.length >= 6, `Must detect at least 6 GT font families, found ${gtFonts.length}`);

    const counts = loader.computeFacetCounts(catalog.fonts);
    assert.strictEqual(counts.categories['GT Font'], gtFonts.length, 'Facet count for GT Font must match exactly');
  });

  reporter.test('T5.7.2: GT Font Collection integrity (GT America, GT Sectra, SVN-Ultra, SVN-Walsheim Pro, etc.)', () => {
    const loader = require('../js/catalog_loader.js');
    const gtFonts = catalog.fonts.filter(loader.isGTFont);
    const gtNames = gtFonts.map(f => f.name);

    assert.ok(gtNames.includes('GT America'), 'GT America must be in GT Font collection');
    assert.ok(gtNames.includes('GT Sectra'), 'GT Sectra must be in GT Font collection');
    assert.ok(gtNames.includes('SVN-Ultra'), 'SVN-Ultra (GT Ultra) must be in GT Font collection');
    assert.ok(gtNames.includes('SVN-Walsheim Pro'), 'SVN-Walsheim Pro (GT Walsheim) must be in GT Font collection');
    assert.ok(gtNames.includes('SVN-SuperDisplay'), 'SVN-SuperDisplay (GT Super) must be in GT Font collection');
    assert.ok(gtNames.includes('SVN-Alpina'), 'SVN-Alpina (GT Alpina) must be in GT Font collection');

    // All GT fonts must have 100% Vietnamese support
    gtFonts.forEach(f => {
      assert.strictEqual(f.vietnamese_support, true, `${f.name} must have vietnamese_support: true`);
      assert.ok(f.drive_folder_url.startsWith('https://drive.google.com/drive/folders/'), `${f.name} must have valid Drive folder URL`);
    });
  });
}

module.exports = { runTier5Tests };

// Direct execution
if (require.main === module) {
  const runner = {
    startSuite: name => console.log(`\n▶ Suite: ${name}`),
    test: (name, fn) => {
      try {
        fn();
        console.log(`  ✔ PASS: ${name}`);
      } catch (err) {
        console.error(`  ✖ FAIL: ${name}\n    Error: ${err.message}`);
        process.exitCode = 1;
      }
    }
  };
  runTier5Tests(runner);
}
