/**
 * tests/m3_preview_challenger_test.js
 * Empirical Stress Test Harness by Milestone 3 Preview Challenger 2
 *
 * Covers:
 * 1. Slider Boundaries (Font Size 14-140px, Line Height 0.8-2.4, Kerning -0.05em to +0.30em)
 * 2. Text Transformations (none, uppercase, lowercase, titlecase) with Vietnamese Diacritics
 * 3. 134 Vietnamese Glyph Modal (67 lowercase, 67 uppercase, tab filtering verification)
 * 4. Google Drive 1-Click Family Download Links (100% of 361 cards, ?usp=sharing format)
 * 5. HTML & CSS Contract Verification
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const TypeTester = require('../js/type_tester.js');
const {
  TypeTesterMetrics,
  VIETNAMESE_LOWERCASE,
  VIETNAMESE_UPPERCASE,
  COMPLEX_VIETNAMESE_WORDS,
  DrivePackaging
} = require('./lib/engine.js');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
const findings = [];

function test(name, fn) {
  totalTests++;
  try {
    fn();
    passedTests++;
    console.log(`  ✔ PASS: ${name}`);
  } catch (err) {
    failedTests++;
    console.log(`  ✖ FAIL: ${name}`);
    console.log(`    Error: ${err.message}`);
    findings.push({ test: name, error: err.message });
  }
}

console.log('============================================================');
console.log(' M3 Challenger 2: Empirical Stress Test Suite');
console.log('============================================================\n');

// ---------------------------------------------------------------------------
// SECTION 1: Slider Boundaries & Input Clamping
// ---------------------------------------------------------------------------
console.log('▶ Area 1: Slider Boundaries (Font Size, Line Height, Kerning)');

test('1.1 Font Size Boundaries (14px - 140px, default 36px)', () => {
  const engine = new TypeTester.TypeTesterEngine();
  assert.strictEqual(engine.clampFontSize(14), 14, 'Min boundary 14px');
  assert.strictEqual(engine.clampFontSize(140), 140, 'Max boundary 140px');
  assert.strictEqual(engine.clampFontSize(36), 36, 'Default 36px preserved');
  assert.strictEqual(engine.clampFontSize(0), 14, 'Zero clamped to min 14');
  assert.strictEqual(engine.clampFontSize(-50), 14, 'Negative clamped to min 14');
  assert.strictEqual(engine.clampFontSize(13.9), 14, '13.9 clamped to min 14');
  assert.strictEqual(engine.clampFontSize(140.1), 140, '140.1 clamped to max 140');
  assert.strictEqual(engine.clampFontSize(9999), 140, 'Extreme overflow clamped to 140');
  assert.strictEqual(engine.clampFontSize(NaN), 36, 'NaN fallback to 36');
  assert.strictEqual(engine.clampFontSize('invalid'), 36, 'Invalid string fallback to 36');
  assert.strictEqual(engine.clampFontSize(null), 36, 'null fallback to 36');
  assert.strictEqual(engine.clampFontSize(undefined), 36, 'undefined fallback to 36');
});

test('1.2 Line Height Boundaries (0.80 - 2.40, default 1.20)', () => {
  const engine = new TypeTester.TypeTesterEngine();
  assert.strictEqual(engine.clampLineHeight(0.8), 0.8, 'Min line-height 0.8');
  assert.strictEqual(engine.clampLineHeight(2.4), 2.4, 'Max line-height 2.4');
  assert.strictEqual(engine.clampLineHeight(1.2), 1.2, 'Default line-height 1.2');
  assert.strictEqual(engine.clampLineHeight(0.79), 0.8, '0.79 clamped to 0.8');
  assert.strictEqual(engine.clampLineHeight(0.0), 0.8, '0.0 clamped to 0.8');
  assert.strictEqual(engine.clampLineHeight(-1.5), 0.8, 'Negative clamped to 0.8');
  assert.strictEqual(engine.clampLineHeight(2.41), 2.4, '2.41 clamped to 2.4');
  assert.strictEqual(engine.clampLineHeight(10.0), 2.4, '10.0 clamped to 2.4');
  assert.strictEqual(engine.clampLineHeight(1.33333), 1.33, 'Precision preserved to 2 decimals');
  assert.strictEqual(engine.clampLineHeight('bad'), 1.2, 'Malformed fallback to 1.2');
});

test('1.3 Kerning / Letter Spacing Boundaries (-0.05em to +0.30em, default 0.00em)', () => {
  const engine = new TypeTester.TypeTesterEngine();
  assert.strictEqual(engine.clampKerning(-0.05), -0.05, 'Min kerning -0.05');
  assert.strictEqual(engine.clampKerning(0.30), 0.30, 'Max kerning 0.30');
  assert.strictEqual(engine.clampKerning(0.0), 0.0, 'Default kerning 0.0');
  assert.strictEqual(engine.clampKerning(-0.051), -0.05, '-0.051 clamped to -0.05');
  assert.strictEqual(engine.clampKerning(-1.0), -0.05, 'Extreme negative clamped to -0.05');
  assert.strictEqual(engine.clampKerning(0.301), 0.30, '0.301 clamped to 0.30');
  assert.strictEqual(engine.clampKerning(5.0), 0.30, 'Extreme positive clamped to 0.30');
  assert.strictEqual(engine.clampKerning(0.125), 0.125, 'Precision preserved to 3 decimals');
  assert.strictEqual(engine.clampKerning('bad'), 0.0, 'Malformed fallback to 0.0');
});

test('1.4 HTML Slider Attribute Specifications Match Engine Boundaries', () => {
  const htmlContent = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

  // Font size slider
  const sizeMatch = htmlContent.match(/<input[^>]*id="font-size-slider"[^>]*>/);
  assert.ok(sizeMatch, 'font-size-slider exists in HTML');
  assert.ok(sizeMatch[0].includes('min="14"'), 'font-size slider min="14"');
  assert.ok(sizeMatch[0].includes('max="140"'), 'font-size slider max="140"');
  assert.ok(sizeMatch[0].includes('value="36"'), 'font-size slider value="36"');

  // Line height slider
  const lineMatch = htmlContent.match(/<input[^>]*id="line-height-slider"[^>]*>/);
  assert.ok(lineMatch, 'line-height-slider exists in HTML');
  assert.ok(lineMatch[0].includes('min="0.80"') || lineMatch[0].includes('min="0.8"'), 'line-height slider min="0.8"');
  assert.ok(lineMatch[0].includes('max="2.40"') || lineMatch[0].includes('max="2.4"'), 'line-height slider max="2.4"');
  assert.ok(lineMatch[0].includes('value="1.20"') || lineMatch[0].includes('value="1.2"'), 'line-height slider value="1.2"');

  // Kerning slider
  const kernMatch = htmlContent.match(/<input[^>]*id="kerning-slider"[^>]*>/);
  assert.ok(kernMatch, 'kerning-slider exists in HTML');
  assert.ok(kernMatch[0].includes('min="-0.050"') || kernMatch[0].includes('min="-0.05"'), 'kerning slider min="-0.05"');
  assert.ok(kernMatch[0].includes('max="0.300"') || kernMatch[0].includes('max="0.3"'), 'kerning slider max="0.3"');
  assert.ok(kernMatch[0].includes('value="0.000"') || kernMatch[0].includes('value="0"'), 'kerning slider value="0"');
});

// ---------------------------------------------------------------------------
// SECTION 2: Text Transformations with Vietnamese Diacritics
// ---------------------------------------------------------------------------
console.log('\n▶ Area 2: Text Transformations with Vietnamese Diacritics');

test('2.1 Uppercase preserves 100% of Vietnamese Diacritics', () => {
  const engine = new TypeTester.TypeTesterEngine();
  const sample = 'Bộ gõ Tiếng Việt có dấu: ă â đ ê ô ơ ư à ả ã á ạ';
  const transformed = engine.applyTransform(sample, 'uppercase');
  assert.strictEqual(transformed, 'BỘ GÕ TIẾNG VIỆT CÓ DẤU: Ă Â Đ Ê Ô Ơ Ư À Ả Ã Á Ạ');

  // Verify multi-tone complex words
  for (const word of COMPLEX_VIETNAMESE_WORDS) {
    const upper = engine.applyTransform(word, 'uppercase');
    assert.strictEqual(upper, word.toUpperCase(), `Uppercase of '${word}' must match standard toUpperCase()`);
  }
});

test('2.2 Lowercase preserves 100% of Vietnamese Diacritics', () => {
  const engine = new TypeTester.TypeTesterEngine();
  const sample = 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM — ĐỘC LẬP TỰ DO HẠNH PHÚC';
  const transformed = engine.applyTransform(sample, 'lowercase');
  assert.strictEqual(transformed, 'cộng hòa xã hội chủ nghĩa việt nam — độc lập tự do hạnh phúc');
});

test('2.3 Titlecase / Capitalize with Vietnamese Diacritics (Adversarial Check)', () => {
  const engine = new TypeTester.TypeTesterEngine();

  // Words beginning with Vietnamese non-ASCII characters or 'đ'
  const testWords = [
    { input: 'đồ họa', expected: 'Đồ Họa' },
    { input: 'ứng dụng', expected: 'Ứng Dụng' },
    { input: 'áo ấm', expected: 'Áo Ấm' },
    { input: 'việt nam', expected: 'Việt Nam' },
    { input: 'thưởng thức', expected: 'Thưởng Thức' }
  ];

  const failures = [];
  for (const item of testWords) {
    const res = engine.applyTransform(item.input, 'titlecase');
    if (res !== item.expected) {
      failures.push({ input: item.input, expected: item.expected, got: res });
    }
  }

  if (failures.length > 0) {
    throw new Error(
      `applyTransform(text, 'titlecase') corrupted Vietnamese text due to ASCII-only \\b(\\w) regex: ` +
      failures.map(f => `"${f.input}" -> got "${f.got}", expected "${f.expected}"`).join('; ')
    );
  }
});

test('2.4 CSS text-transform keyword validity in UI controls', () => {
  const htmlContent = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');
  // Check button data-transform="titlecase"
  const hasTitlecaseBtn = htmlContent.includes('data-transform="titlecase"');
  if (hasTitlecaseBtn) {
    // In CSS Text Module Level 3, "titlecase" is NOT a valid CSS text-transform keyword!
    // Valid values: none | capitalize | uppercase | lowercase | full-width | full-size-kana
    throw new Error(
      'index.html uses data-transform="titlecase", which sets CSS property --tester-text-transform: titlecase. ' +
      'In CSS specification, "titlecase" is an invalid text-transform keyword and is ignored by browsers (valid keyword is "capitalize").'
    );
  }
});

// ---------------------------------------------------------------------------
// SECTION 3: 134 Vietnamese Glyph Modal & Tabs
// ---------------------------------------------------------------------------
console.log('\n▶ Area 3: 134 Vietnamese Glyph Modal & Filtering');

test('3.1 Glyph Matrix contains exactly 134 Vietnamese Accented Characters', () => {
  const engine = new TypeTester.TypeTesterEngine();
  const groups = engine.getVietnameseGlyphs();

  let totalChars = 0;
  const allChars = [];
  groups.forEach(g => {
    totalChars += g.chars.length;
    allChars.push(...g.chars);
  });

  assert.strictEqual(totalChars, 134, `Expected exactly 134 characters in glyph modal, found ${totalChars}`);
  assert.strictEqual(new Set(allChars).size, 134, 'All 134 glyphs must be unique');

  const lowerChars = allChars.filter(c => c === c.toLowerCase() && c !== c.toUpperCase());
  const upperChars = allChars.filter(c => c === c.toUpperCase() && c !== c.toLowerCase());

  assert.strictEqual(lowerChars.length, 67, `Expected exactly 67 lowercase characters, found ${lowerChars.length}`);
  assert.strictEqual(upperChars.length, 67, `Expected exactly 67 uppercase characters, found ${upperChars.length}`);
  assert.strictEqual(lowerChars.length + upperChars.length, 134, 'Sum of lower and upper must be exactly 134');
});

test('3.2 Vietnamese Lower/Upper Glyph 1-to-1 Bijection Integrity', () => {
  const engine = new TypeTester.TypeTesterEngine();
  const groups = engine.getVietnameseGlyphs();
  const allChars = [];
  groups.forEach(g => allChars.push(...g.chars));

  const lowerSet = new Set(allChars.filter(c => c === c.toLowerCase() && c !== c.toUpperCase()));
  const upperSet = new Set(allChars.filter(c => c === c.toUpperCase() && c !== c.toLowerCase()));

  // For every lower character, its toUpperCase() must be in upperSet
  for (const l of lowerSet) {
    const u = l.toUpperCase();
    assert.ok(upperSet.has(u), `Uppercase pair of '${l}' (${u}) must exist in glyph matrix`);
  }

  // For every upper character, its toLowerCase() must be in lowerSet
  for (const u of upperSet) {
    const l = u.toLowerCase();
    assert.ok(lowerSet.has(l), `Lowercase pair of '${u}' (${l}) must exist in glyph matrix`);
  }
});

test('3.3 Glyph Modal Tab Filtering Implementation (Chữ Thường 67 vs Chữ Hoa 67)', () => {
  // Check app.js implementation of renderModalGlyphs()
  const appJs = fs.readFileSync(path.resolve(__dirname, '../js/app.js'), 'utf8');

  // Check how renderModalGlyphs handles activeGlyphTab === 'lower' and 'upper'
  const hasLowerTabLogic = appJs.includes("activeGlyphTab === 'lower'");
  const hasUpperTabLogic = appJs.includes("activeGlyphTab === 'upper'");

  if (!hasLowerTabLogic || !hasUpperTabLogic) {
    throw new Error(
      'app.js renderModalGlyphs() does not check for activeGlyphTab === "lower" or activeGlyphTab === "upper". ' +
      'Clicking the "Chữ Thường (67)" or "Chữ Hoa (67)" tabs always falls through to renderGlyphMap, ' +
      'which unconditionally displays all 134 characters without case filtering.'
    );
  }
});

// ---------------------------------------------------------------------------
// SECTION 4: Google Drive 1-Click Family Download Links
// ---------------------------------------------------------------------------
console.log('\n▶ Area 4: Google Drive 1-Click Family Download Links');

test('4.1 100% of 361 Font Cards in catalog.json have valid Google Drive URLs', () => {
  const catalog = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../data/catalog.json'), 'utf8'));
  const fonts = catalog.fonts || [];

  assert.strictEqual(fonts.length, 361, `Catalog must contain exactly 361 fonts, found ${fonts.length}`);

  const driveRegex = /^https:\/\/drive\.google\.com\/drive\/folders\/[A-Za-z0-9_-]+\?usp=sharing$/;
  const invalidFonts = [];

  fonts.forEach((font, idx) => {
    const url = font.drive_folder_url;
    if (!url || typeof url !== 'string' || !driveRegex.test(url)) {
      invalidFonts.push({ id: font.id, name: font.name, url: url });
    }
  });

  assert.strictEqual(
    invalidFonts.length,
    0,
    `All 361 fonts must have valid Google Drive URLs with ?usp=sharing, found ${invalidFonts.length} invalid`
  );
});

test('4.2 361 Distinct Family Subfolder URLs in catalog.json', () => {
  const catalog = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../data/catalog.json'), 'utf8'));
  const fonts = catalog.fonts || [];
  const urls = fonts.map(f => f.drive_folder_url);
  const uniqueUrls = new Set(urls);

  assert.strictEqual(
    uniqueUrls.size,
    361,
    `Each font family must have a dedicated distinct Drive folder URL, found ${uniqueUrls.size} distinct out of 361`
  );
});

test('4.3 data/drive_links.json Family Mappings Integrity', () => {
  const driveLinksData = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../data/drive_links.json'), 'utf8'));
  const links = driveLinksData.drive_links || {};
  const families = Object.keys(links);

  assert.strictEqual(families.length, 361, `drive_links must map exactly 361 families, found ${families.length}`);

  const driveRegex = /^https:\/\/drive\.google\.com\/drive\/folders\/[A-Za-z0-9_-]+\?usp=sharing$/;
  for (const [family, url] of Object.entries(links)) {
    assert.ok(
      driveRegex.test(url),
      `Family '${family}' URL '${url}' must match Drive public folder link format with ?usp=sharing`
    );
  }
});

test('4.4 Web Card Download Button HTML Anchor Contract in app.js', () => {
  const appJs = fs.readFileSync(path.resolve(__dirname, '../js/app.js'), 'utf8');

  // Verify button markup
  assert.ok(appJs.includes('class="btn-download-family"'), 'Card must render button with class btn-download-family');
  assert.ok(appJs.includes('target="_blank"'), 'Download link must specify target="_blank"');
  assert.ok(appJs.includes('rel="noopener noreferrer"'), 'Download link must specify rel="noopener noreferrer"');
  assert.ok(appJs.includes('href="\' + driveUrl + \'"'), 'Download link href must bind to driveUrl');
});

// ---------------------------------------------------------------------------
// SUMMARY
// ---------------------------------------------------------------------------
console.log('\n============================================================');
console.log(` SUMMARY: ${passedTests} passed, ${failedTests} failed out of ${totalTests} tests`);
console.log('============================================================\n');

if (findings.length > 0) {
  console.log('Empirical Findings / Discrepancies:');
  findings.forEach((f, i) => {
    console.log(` [Finding ${i + 1}] ${f.test}:`);
    console.log(`   ${f.error}\n`);
  });
}
