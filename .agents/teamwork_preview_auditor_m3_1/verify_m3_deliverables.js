/**
 * verify_m3_deliverables.js
 * Independent Forensic Audit Test of js/type_tester.js, js/catalog_loader.js,
 * index.html, and css/style.css.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '../..');
const catalogPath = path.join(ROOT_DIR, 'data/catalog.json');
const catalogData = JSON.parse(fs.readFileSync(catalogPath, 'utf-8'));
const fonts = catalogData.fonts;

const TypeTester = require(path.join(ROOT_DIR, 'js/type_tester.js'));
const CatalogLoader = require(path.join(ROOT_DIR, 'js/catalog_loader.js'));

console.log('Loaded TypeTester and CatalogLoader directly from js/');
console.log(`Catalog contains ${fonts.length} fonts.`);

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✔ PASS: ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✖ FAIL: ${name} -> ${err.message}`);
    failed++;
  }
}

// -------------------------------------------------------------
// 1. Metric Clamping in js/type_tester.js
// -------------------------------------------------------------
console.log('\n--- Checking js/type_tester.js Metrics ---');
const Metrics = TypeTester.Metrics;

test('FontSize min clamp (14px)', () => {
  assert.strictEqual(Metrics.clampFontSize(10), 14);
  assert.strictEqual(Metrics.clampFontSize(14), 14);
  assert.strictEqual(Metrics.clampFontSize(0), 14);
  assert.strictEqual(Metrics.clampFontSize(-50), 14);
});

test('FontSize max clamp (140px)', () => {
  assert.strictEqual(Metrics.clampFontSize(200), 140);
  assert.strictEqual(Metrics.clampFontSize(140), 140);
  assert.strictEqual(Metrics.clampFontSize(9999), 140);
});

test('FontSize default fallback for invalid inputs', () => {
  assert.strictEqual(Metrics.clampFontSize('abc'), 36);
  assert.strictEqual(Metrics.clampFontSize(null), 36);
});

test('LineHeight bounds (0.8 - 2.4)', () => {
  assert.strictEqual(Metrics.clampLineHeight(0.5), 0.8);
  assert.strictEqual(Metrics.clampLineHeight(0.8), 0.8);
  assert.strictEqual(Metrics.clampLineHeight(3.5), 2.4);
  assert.strictEqual(Metrics.clampLineHeight(1.25), 1.25);
  assert.strictEqual(Metrics.clampLineHeight('invalid'), 1.2);
});

test('Kerning bounds (-0.05em to +0.30em)', () => {
  assert.strictEqual(Metrics.clampKerning(-0.5), -0.05);
  assert.strictEqual(Metrics.clampKerning(-0.05), -0.05);
  assert.strictEqual(Metrics.clampKerning(0.8), 0.30);
  assert.strictEqual(Metrics.clampKerning(0.15), 0.15);
  assert.strictEqual(Metrics.clampKerning('invalid'), 0.0);
});

test('Text transformations with Vietnamese diacritics', () => {
  const sample = 'Cộng hòa Xã hội Chủ nghĩa Việt Nam';
  assert.strictEqual(
    Metrics.applyTransform(sample, 'uppercase'),
    'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM'
  );
  assert.strictEqual(
    Metrics.applyTransform(sample, 'lowercase'),
    'cộng hòa xã hội chủ nghĩa việt nam'
  );
  assert.strictEqual(
    Metrics.applyTransform('nguyễn văn việt', 'titlecase'),
    'Nguyễn Văn Việt'
  );
});

test('Fallback stacks per category', () => {
  assert.ok(Metrics.getFallbackStack('Serif').includes('Georgia'));
  assert.ok(Metrics.getFallbackStack('Sans Serif').includes('apple-system'));
  assert.ok(Metrics.getFallbackStack('Monospace').includes('SF Mono') || Metrics.getFallbackStack('Monospace').includes('Courier'));
  assert.ok(Metrics.getFallbackStack('Script').includes('cursive') || Metrics.getFallbackStack('Script').includes('Script'));
});

// -------------------------------------------------------------
// 2. TypeTesterEngine
// -------------------------------------------------------------
console.log('\n--- Checking TypeTesterEngine instance & cache ---');
const engine = new TypeTester.TypeTesterEngine();

test('TypeTesterEngine instance initialization', () => {
  assert.strictEqual(engine.fontSize, 36);
  assert.strictEqual(engine.lineHeight, 1.2);
  assert.strictEqual(engine.kerning, 0.0);
});

test('loadWebFont in headless Node environment', async () => {
  const res = await engine.loadWebFont('SVN-Test', 'https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts/test.woff2', '400', 'normal');
  assert.ok(res);
  assert.strictEqual(res.family, 'SVN-Test');
  assert.strictEqual(res.status, 'loaded');

  // Verify caching
  const cached = engine.loadedFaces.get(engine.getCacheKey('SVN-Test', '400', 'normal'));
  assert.strictEqual(cached, res);
});

// -------------------------------------------------------------
// 3. CatalogLoader Search & Diacritics
// -------------------------------------------------------------
console.log('\n--- Checking js/catalog_loader.js Search & Indexing ---');

test('Diacritic removal handles all accents and đ/Đ', () => {
  assert.strictEqual(CatalogLoader.removeVietnameseDiacritics('Cộng hòa Xã hội'), 'cong hoa xa hoi');
  assert.strictEqual(CatalogLoader.removeVietnameseDiacritics('Đồ Họa & Điện Ảnh'), 'do hoa & dien anh');
  assert.strictEqual(CatalogLoader.removeVietnameseDiacritics('ƯỚC MƠ & THƯỞNG'), 'uoc mo & thuong');
});

test('Category discrimination (Serif vs Sans Serif)', () => {
  assert.strictEqual(CatalogLoader.matchesCategory('Serif', 'Serif'), true);
  assert.strictEqual(CatalogLoader.matchesCategory('Sans Serif', 'Serif'), false);
  assert.strictEqual(CatalogLoader.matchesCategory('Sans Serif', 'Sans Serif'), true);
  assert.strictEqual(CatalogLoader.matchesCategory('Serif', 'Sans Serif'), false);
  assert.strictEqual(CatalogLoader.matchesCategory('Việt Nam Oldstyle / Vintage Sài Gòn', 'Việt Nam Oldstyle / Vintage Sài Gòn'), true);
  assert.strictEqual(CatalogLoader.matchesCategory('Blackletter, Script & Monospace', 'Blackletter, Script & Monospace'), true);
});

test('Instant search performance benchmark (<4ms target)', () => {
  const indexedFonts = CatalogLoader.buildSearchIndex(fonts);
  assert.strictEqual(indexedFonts.length, 361);

  const queries = ['SVN', 'integral', 'didone', 'tuyên ngôn', 'sang trọng', 'connary', 'vintage', 'sài gòn'];
  for (const q of queries) {
    const t0 = process.hrtime.bigint();
    const res = CatalogLoader.instantSearch(indexedFonts, q);
    const t1 = process.hrtime.bigint();
    const durationMs = Number(t1 - t0) / 1e6;
    assert.ok(durationMs < 4.0, `Search for "${q}" took ${durationMs.toFixed(3)}ms (expected < 4ms)`);
    assert.ok(res.length > 0, `Search for "${q}" should return results`);
  }
});

test('Search ReDoS and Regex Metacharacter Immunity', () => {
  const indexedFonts = CatalogLoader.buildSearchIndex(fonts);
  const hostileQueries = [
    '((((a+)+)+)+)$',
    '[a-z]*.*.*.*',
    '\\.\\*\\?\\+\\[\\^\\$',
    '<script>alert(1)</script>',
    'SVN-*(?='
  ];

  for (const q of hostileQueries) {
    const t0 = process.hrtime.bigint();
    const res = CatalogLoader.instantSearch(indexedFonts, q);
    const t1 = process.hrtime.bigint();
    const durationMs = Number(t1 - t0) / 1e6;
    assert.ok(durationMs < 10.0, `Hostile query "${q}" took ${durationMs.toFixed(3)}ms (ReDoS vulnerability!)`);
    assert.ok(Array.isArray(res));
  }
});

// -------------------------------------------------------------
// 4. Multi-Faceted Filtering
// -------------------------------------------------------------
console.log('\n--- Checking Multi-Faceted Filtering ---');

test('Filter by Category "Serif"', () => {
  const res = CatalogLoader.multiFilter(fonts, { category: 'Serif' });
  assert.ok(res.length > 0);
  assert.ok(res.every(f => (f.category || '').toLowerCase().includes('serif') && !(f.category || '').toLowerCase().includes('sans')));
});

test('Filter by Category "Sans Serif"', () => {
  const res = CatalogLoader.multiFilter(fonts, { category: 'Sans Serif' });
  assert.ok(res.length > 0);
  assert.ok(res.every(f => (f.category || '').toLowerCase().includes('sans')));
});

test('Filter by Mood "Luxury & Sang trọng"', () => {
  const res = CatalogLoader.multiFilter(fonts, { mood: 'Luxury & Sang trọng' });
  assert.ok(res.length > 0);
  assert.ok(res.every(f => (f.matrix_3d?.mood || f.matrix_mood || '').includes('Luxury') || (f.matrix_3d?.mood || f.matrix_mood || '').includes('Sang trọng')));
});

test('Filter by Use Case "Display / Headline"', () => {
  const res = CatalogLoader.multiFilter(fonts, { use_case: 'Display / Headline' });
  assert.ok(res.length > 0);
  assert.ok(res.every(f => (f.matrix_3d?.use_case || f.matrix_application || '').includes('Display')));
});

test('Filter by Vietnamese Support (true)', () => {
  const res = CatalogLoader.multiFilter(fonts, { vietnamese_support: true });
  assert.strictEqual(res.length, 361);
});

test('Compute Facet Counts accuracy', () => {
  const counts = CatalogLoader.computeFacetCounts(fonts);
  assert.strictEqual(counts.categories['all'], 361);
  assert.ok(counts.categories['Serif'] > 0);
  assert.ok(counts.categories['Sans Serif'] > 0);
  assert.ok(counts.categories['Việt Nam Oldstyle / Vintage Sài Gòn'] > 0);
  assert.ok(counts.categories['Blackletter, Script & Monospace'] > 0);
  assert.strictEqual(counts.vnSupport['supported'], 361);
});

console.log('\n' + '='.repeat(50));
console.log(`INDEPENDENT AUDIT TESTS: ${passed} PASSED, ${failed} FAILED`);
console.log('='.repeat(50));

if (failed > 0) {
  process.exit(1);
}
