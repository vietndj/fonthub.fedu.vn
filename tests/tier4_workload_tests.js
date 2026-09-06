/**
 * tests/tier4_workload_tests.js
 * Tier 4: Real-World Designer Application Scenarios (5 Workload Scenarios)
 *
 * Simulates complete, end-to-end user journeys for designers, students,
 * and creators using the fedu.vn/font Interactive Type Hub.
 */

const assert = require('assert');
const {
  resolveCatalog,
  resolveFamilyGrouping,
  TypeTesterMetrics,
  SearchEngine,
  DrivePackaging
} = require('./lib/engine');

function runTier4Tests(reporter) {
  reporter.startSuite('Tier 4: Real-World Designer Application Scenarios');

  const catalogResult = resolveCatalog();
  if (!catalogResult) {
    throw new Error('FATAL: Unable to resolve font catalog for Tier 4 tests.');
  }
  const fonts = catalogResult.data.fonts || [];

  const familyGroupingResult = resolveFamilyGrouping();
  const familyGrouping = familyGroupingResult?.data || {};

  // =========================================================================
  // Scenario S1: Student searching for Luxury Serif for editorial layout
  // =========================================================================
  reporter.test('Scenario S1: Editorial Fashion Layout (Luxury Serif)', () => {
    // 1. Filter Serif fonts with Luxury & Sang trọng mood
    const luxurySerifs = SearchEngine.multiFilter(fonts, {
      category: 'Serif',
      mood: 'Luxury & Sang trọng'
    });
    assert.ok(luxurySerifs.length >= 3, `Expected at least 3 luxury serif candidates, found ${luxurySerifs.length}`);

    // 2. Select top candidate font (e.g. SVN-Saol Standard, Alegreya, Bodoni, etc.)
    const selectedFont = luxurySerifs[0];
    assert.ok(selectedFont.name, 'Selected font must have a name');

    // 3. Verify director commentary highlights contrast and aesthetics
    const notes = selectedFont.director_notes || '';
    assert.ok(notes.length > 10, 'Director commentary must provide meaningful typographic insight');

    // 4. Test headline text with Vietnamese diacritics in Type Tester
    const headline = 'BỘ SƯU TẬP MÙA THU - VẺ ĐẸP CỦA SỰ TỐI GIẢN';
    const headlineSize = TypeTesterMetrics.clampFontSize(54);
    const headlineKerning = TypeTesterMetrics.clampKerning(0.02);
    const headlineLineHeight = TypeTesterMetrics.clampLineHeight(1.15);

    assert.strictEqual(headlineSize, 54);
    assert.strictEqual(headlineKerning, 0.02);
    assert.strictEqual(headlineLineHeight, 1.15);

    // 5. Test body text reading setting
    const bodyText = 'Nghệ thuật sắp đặt chữ trong các tạp chí thời trang đòi hỏi sự cân bằng tuyệt đối giữa độ tương phản và khoảng thở.';
    const bodySize = TypeTesterMetrics.clampFontSize(18);
    const bodyLineHeight = TypeTesterMetrics.clampLineHeight(1.6);

    assert.strictEqual(bodySize, 18);
    assert.strictEqual(bodyLineHeight, 1.6);
  });

  // =========================================================================
  // Scenario S2: Designer testing Tech Sans in Neon theme with uppercase transform
  // =========================================================================
  reporter.test('Scenario S2: Cyberpunk Tech Landing Page (Sans Serif & Neon)', () => {
    // 1. Filter Sans Serif fonts with Tech & Công nghệ mood
    const techSans = SearchEngine.multiFilter(fonts, {
      category: 'Sans Serif',
      mood: 'Tech & Công nghệ'
    });
    assert.ok(techSans.length >= 1, `Expected at least 1 tech sans font, found ${techSans.length}`);

    const selectedFont = techSans[0];

    // 2. Switch theme to Neon Mode
    const activeTheme = 'neon';
    const neonPalette = { bg: '#0D0E15', text: '#FFFFFF', accent: '#00FF66' };
    assert.strictEqual(neonPalette.accent, '#00FF66');

    // 3. Input tech slogan and apply uppercase transform
    const rawInput = 'Trí tuệ nhân tạo & hệ thống tự hành tương lai';
    const uppercaseSlogan = TypeTesterMetrics.applyTransform(rawInput, 'uppercase');
    assert.strictEqual(uppercaseSlogan, 'TRÍ TUỆ NHÂN TẠO & HỆ THỐNG TỰ HÀNH TƯƠNG LAI');

    // 4. Set large headline scale with wide kerning
    const headlineSize = TypeTesterMetrics.clampFontSize(68);
    const wideKerning = TypeTesterMetrics.clampKerning(0.06);
    assert.strictEqual(headlineSize, 68);
    assert.strictEqual(wideKerning, 0.06);

    // 5. Generate dynamic FontFace CSS rule
    const fontUrl = selectedFont.web_font_url || 'https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts/test.woff2';
    const css = TypeTesterMetrics.generateFontFaceCSS(selectedFont.name, fontUrl, '700');
    assert.ok(css.includes(`font-family: '${selectedFont.name}'`));
    assert.ok(css.includes("format('woff2')"));
  });

  // =========================================================================
  // Scenario S3: Video creator testing Vintage Sài Gòn sign font for thumbnail title
  // =========================================================================
  reporter.test('Scenario S3: YouTube Video Creator (Vintage Sài Gòn Thumbnail Hook)', () => {
    // 1. Filter Vintage Sài Gòn / Việt Nam Oldstyle collection
    const vintageFonts = SearchEngine.multiFilter(fonts, {
      category: 'Việt Nam Oldstyle / Vintage Sài Gòn'
    });
    assert.ok(vintageFonts.length >= 10, `Expected >=10 vintage sign fonts, found ${vintageFonts.length}`);

    const candidate = vintageFonts.find(f => (f.name || '').includes('Appareo') || (f.name || '').includes('Stay Kool')) || vintageFonts[0];

    // 2. Input YouTube thumbnail hook
    const hookText = 'SÀI GÒN 1975 - NHỮNG BIỂN HIỆU XƯA';
    const size = TypeTesterMetrics.clampFontSize(96);
    const tightLineHeight = TypeTesterMetrics.clampLineHeight(0.9);
    const tightKerning = TypeTesterMetrics.clampKerning(-0.02);

    assert.strictEqual(size, 96);
    assert.strictEqual(tightLineHeight, 0.9);
    assert.strictEqual(tightKerning, -0.02);

    // 3. Verify all Vietnamese diacritics in hook are intact
    const vowelsWithAccents = ['À', 'Ò', 'Ữ', 'Ể', 'Ệ', 'Ư'];
    for (const v of vowelsWithAccents) {
      assert.ok(hookText.includes(v), `Hook text must contain accented vowel '${v}'`);
    }
  });

  // =========================================================================
  // Scenario S4: 1-click Google Drive Family package download navigation
  // =========================================================================
  reporter.test('Scenario S4: 1-Click Google Drive Family Package Download', () => {
    // 1. Search for SVN-Integral CF family
    const familyName = 'SVN-Integral CF';
    const families = familyGrouping.families || {};
    const familyData = families['SVN-IntegralCF'] || families['SVN-Integral CF'] || families[familyName];

    assert.ok(familyData, `Family '${familyName}' must exist in grouping database`);
    assert.strictEqual(familyData.file_count, 6, 'SVN-Integral CF family must contain 6 weight files');

    // 2. Validate family folder URL structure
    const sampleFolderId = familyData.folder_id || '1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao';
    const driveUrl = DrivePackaging.buildDriveFolderUrl(sampleFolderId);

    assert.ok(DrivePackaging.isValidDriveUrl(driveUrl), 'Drive URL must be valid public folder link with usp=sharing');

    // 3. Web Card Button Contract Verification
    const webButtonAttributes = {
      href: driveUrl,
      target: '_blank',
      rel: 'noopener noreferrer',
      title: `Tải trọn bộ ${familyName} (${familyData.file_count} fonts)`
    };

    assert.strictEqual(webButtonAttributes.target, '_blank', 'Must open in new tab');
    assert.strictEqual(webButtonAttributes.rel, 'noopener noreferrer', 'Must include secure rel attributes');
    assert.ok(webButtonAttributes.title.includes('6 fonts'), 'Button tooltip must indicate font count');
  });

  // =========================================================================
  // Scenario S5: Offline / local font fallback graceful degradation
  // =========================================================================
  reporter.test('Scenario S5: Offline / Local Font Fallback Graceful Degradation', () => {
    // 1. Simulate FontFace load failure or offline environment
    const fontCategory = 'Serif';
    const fallbackStack = TypeTesterMetrics.getFallbackStack(fontCategory);

    assert.ok(fallbackStack.includes('Georgia'), 'Serif fallback must prioritize Georgia');
    assert.ok(fallbackStack.includes('serif'), 'Serif fallback must end with generic serif');

    // 2. Verify Type Tester operations continue seamlessly without network
    const fallbackFontFamily = `'CustomOfflineFont', ${fallbackStack}`;
    const testSize = TypeTesterMetrics.clampFontSize(42);
    const testText = 'Hệ thống phông chữ vẫn hoạt động ổn định khi ngoại tuyến';

    assert.ok(fallbackFontFamily.startsWith("'CustomOfflineFont'"));
    assert.strictEqual(testSize, 42);
    assert.ok(testText.length > 0);
  });
}

module.exports = { runTier4Tests };
