/**
 * tests/tier1_feature_tests.js
 * Tier 1: Feature Isolation Tests (>=5 tests per feature for F1, F2, F3, F4)
 *
 * Verifies core requirements R1, R2, R3, R4 in complete isolation
 * against authoritative specifications.
 */

const assert = require('assert');
const {
  resolveCatalog,
  resolveFamilyGrouping,
  TypeTesterMetrics,
  SearchEngine,
  DrivePackaging
} = require('./lib/engine');

function runTier1Tests(reporter) {
  reporter.startSuite('Tier 1: Feature Isolation Tests');

  const catalogResult = resolveCatalog();
  if (!catalogResult) {
    throw new Error('FATAL: Unable to resolve font catalog from data/catalog.json or survey artifacts.');
  }
  const catalog = catalogResult.data;
  const fonts = catalog.fonts || [];

  const familyGroupingResult = resolveFamilyGrouping();
  if (!familyGroupingResult) {
    throw new Error('FATAL: Unable to resolve family grouping from survey artifacts or data/drive_links.json.');
  }
  const familyGrouping = familyGroupingResult.data;

  // =========================================================================
  // F1: PDF Catalog & 3D Matrix Schema Verification (6 tests)
  // =========================================================================

  reporter.test('T1.F1.1: Verification of 4 Core Visual Sections in Catalog', () => {
    assert.ok(fonts.length >= 248, `Catalog should contain at least 248 fonts, found ${fonts.length}`);
    const sections = new Set(fonts.map(f => f.category || f.core_section));
    const sectionNames = Array.from(sections).join(', ');

    // Must cover Serif, Sans Serif, Monospace/Script/Blackletter, and Việt Nam Oldstyle / Vintage Sài Gòn
    assert.ok(sectionNames.includes('Serif'), 'Must contain Serif section');
    assert.ok(sectionNames.includes('Sans'), 'Must contain Sans Serif section');
    assert.ok(
      sectionNames.includes('Blackletter') || sectionNames.includes('Script') || sectionNames.includes('Monospace'),
      'Must contain Monospace / Script / Blackletter section'
    );
    assert.ok(
      sectionNames.includes('Việt Nam') || sectionNames.includes('Vintage') || sectionNames.includes('Sài Gòn'),
      'Must contain Việt Nam Oldstyle / Vintage Sài Gòn section'
    );
  });

  reporter.test('T1.F1.2: 3D Selection Matrix Completeness (Style, Mood, Use-Case)', () => {
    let validMatrixCount = 0;
    for (const font of fonts) {
      const style = font.matrix_3d?.style || font.matrix_visual || font.category || font.core_section;
      const mood = font.matrix_3d?.mood || font.matrix_mood;
      const useCase = font.matrix_3d?.use_case || font.matrix_application;

      assert.ok(style && style.length > 0, `Font ${font.name || font.id} missing 3D Style`);
      assert.ok(mood && mood.length > 0, `Font ${font.name || font.id} missing 3D Mood`);
      assert.ok(useCase && useCase.length > 0, `Font ${font.name || font.id} missing 3D Use Case`);
      validMatrixCount++;
    }
    assert.strictEqual(validMatrixCount, fonts.length, '100% of fonts must possess complete 3D Matrix attributes');
  });

  reporter.test('T1.F1.3: Typographic Anatomy Metadata Integrity', () => {
    // Check anatomy fields (contrast, axis, x_height, aperture)
    let anatomyCount = 0;
    for (const font of fonts) {
      const contrast = font.anatomy?.contrast || font.contrast;
      const axis = font.anatomy?.axis || font.axis;
      const xHeight = font.anatomy?.x_height || font.x_height;
      const aperture = font.anatomy?.aperture || font.aperture;

      if (contrast && axis && xHeight && aperture) {
        anatomyCount++;
      }
    }
    assert.ok(anatomyCount >= 240, `At least 240 fonts must have complete anatomy data, found ${anatomyCount}`);
  });

  reporter.test('T1.F1.4: Director Notes & Commentary Fidelity', () => {
    const sampleNotes = fonts
      .map(f => f.director_notes)
      .filter(notes => typeof notes === 'string' && notes.trim().length > 10);

    assert.ok(sampleNotes.length >= 200, `At least 200 fonts must have substantive director commentary, found ${sampleNotes.length}`);

    // Verify commentary does not have replacement glyph artifacts
    const corruptedNotes = sampleNotes.filter(n => n.includes('\uFFFD') || /\\u[0-9a-f]{4}/i.test(n));
    assert.strictEqual(corruptedNotes.length, 0, `Director notes must be free of corrupted glyph artifacts, found ${corruptedNotes.length}`);
  });

  reporter.test('T1.F1.5: Vietnamese Diacritic Support Status Flags', () => {
    const vnFlags = fonts.map(f => {
      if (typeof f.vietnamese_support === 'boolean') return f.vietnamese_support;
      if (f.vietnamese_status) {
        return f.vietnamese_status.startsWith('Supported');
      }
      return false;
    });

    const supportedCount = vnFlags.filter(Boolean).length;
    const unsupportedCount = vnFlags.filter(v => !v).length;

    assert.ok(supportedCount >= 200, `Most fonts (>200) should support Vietnamese diacritics, found ${supportedCount}`);
    if (fonts.length === 253) {
      assert.ok(unsupportedCount >= 5, `Non-supported fonts in raw PDF catalog must be accurately flagged, found ${unsupportedCount}`);
    } else {
      // In curated SVN drive catalog (361 fonts), all fonts are Vietnamese localized
      assert.ok(supportedCount >= 350, `All SVN font families must support Vietnamese diacritics, found ${supportedCount}`);
    }
  });

  reporter.test('T1.F1.6: Master Catalog Summary Metrics Sanity', () => {
    const ids = new Set(fonts.map(f => f.id || f.name));
    assert.strictEqual(ids.size, fonts.length, 'Every font in catalog must have a unique identifier');

    // Check sample phrase availability for preview rendering
    const withSampleText = fonts.filter(f => (f.sample_text || f.sample_phrase || '').length > 0);
    assert.ok(withSampleText.length >= 240, 'At least 240 fonts must specify a sample preview phrase');
  });

  // =========================================================================
  // F2: Type Tester Dynamic Font Rendering & Slider Metrics (6 tests)
  // =========================================================================

  reporter.test('T1.F2.1: Font Size Clamping Boundaries (14px - 140px)', () => {
    assert.strictEqual(TypeTesterMetrics.clampFontSize(14), 14, 'Min boundary 14px must be preserved');
    assert.strictEqual(TypeTesterMetrics.clampFontSize(140), 140, 'Max boundary 140px must be preserved');
    assert.strictEqual(TypeTesterMetrics.clampFontSize(5), 14, 'Values below 14 must be clamped to 14');
    assert.strictEqual(TypeTesterMetrics.clampFontSize(300), 140, 'Values above 140 must be clamped to 140');
    assert.strictEqual(TypeTesterMetrics.clampFontSize('invalid'), 36, 'Invalid non-numeric input must fallback to default 36px');
  });

  reporter.test('T1.F2.2: Line-Height Range Validation (0.8 - 2.4)', () => {
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(0.8), 0.8, 'Min line-height 0.8 preserved');
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(2.4), 2.4, 'Max line-height 2.4 preserved');
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(0.2), 0.8, 'Underflow line-height clamped to 0.8');
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(3.5), 2.4, 'Overflow line-height clamped to 2.4');
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(1.25), 1.25, 'Mid-range line-height preserved');
  });

  reporter.test('T1.F2.3: Letter-Spacing / Kerning Metrics (-0.05em to +0.30em)', () => {
    assert.strictEqual(TypeTesterMetrics.clampKerning(-0.05), -0.05, 'Min kerning -0.05em preserved');
    assert.strictEqual(TypeTesterMetrics.clampKerning(0.30), 0.30, 'Max kerning 0.30em preserved');
    assert.strictEqual(TypeTesterMetrics.clampKerning(-0.20), -0.05, 'Extreme negative kerning clamped');
    assert.strictEqual(TypeTesterMetrics.clampKerning(0.50), 0.30, 'Extreme positive kerning clamped');
    assert.strictEqual(TypeTesterMetrics.clampKerning(0.0), 0.0, 'Zero kerning preserved');
  });

  reporter.test('T1.F2.4: CSS @font-face Generation with WOFF2 & Swap', () => {
    const css = TypeTesterMetrics.generateFontFaceCSS(
      'SVN-Integral CF',
      'https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts/SVN-IntegralCF-Bold.woff2',
      '700',
      'normal'
    );

    assert.ok(css.includes("@font-face"), "CSS must contain @font-face rule");
    assert.ok(css.includes("font-family: 'SVN-Integral CF'"), "Must specify correct font-family name");
    assert.ok(css.includes("format('woff2')"), "Must specify format('woff2') for optimal web compression");
    assert.ok(css.includes("font-display: swap"), "Must declare font-display: swap for performance");
    assert.ok(css.includes("font-weight: 700"), "Must declare font-weight");
  });

  reporter.test('T1.F2.5: Text Case Transformations with Vietnamese Accents Preserved', () => {
    const sample = 'Bộ gõ Tiếng Việt có dấu';
    const upper = TypeTesterMetrics.applyTransform(sample, 'uppercase');
    const lower = TypeTesterMetrics.applyTransform(sample, 'lowercase');

    assert.strictEqual(upper, 'BỘ GÕ TIẾNG VIỆT CÓ DẤU', 'Uppercase must preserve all Vietnamese diacritics');
    assert.strictEqual(lower, 'bộ gõ tiếng việt có dấu', 'Lowercase must preserve all Vietnamese diacritics');
  });

  reporter.test('T1.F2.6: System Font Fallback Stacks per Category', () => {
    const serifFallback = TypeTesterMetrics.getFallbackStack('Serif');
    const sansFallback = TypeTesterMetrics.getFallbackStack('Sans Serif');
    const monoFallback = TypeTesterMetrics.getFallbackStack('Monospace');

    assert.ok(serifFallback.includes('serif'), 'Serif fallback must end with generic serif');
    assert.ok(sansFallback.includes('sans-serif'), 'Sans Serif fallback must end with generic sans-serif');
    assert.ok(monoFallback.includes('monospace'), 'Monospace fallback must end with generic monospace');
  });

  // =========================================================================
  // F3: Google Drive 361 Family Packaging & Link Validation (6 tests)
  // =========================================================================

  reporter.test('T1.F3.1: Drive File Accounting Parity (Exactly 1,070 Files)', () => {
    const totalFiles = familyGrouping.summary?.total_files;
    assert.strictEqual(totalFiles, 1070, `Google Drive asset inventory must account for exactly 1,070 files, found ${totalFiles}`);
  });

  reporter.test('T1.F3.2: 361 Distinct Family Subfolders Quantified', () => {
    const totalFamilies = familyGrouping.summary?.total_families;
    const familiesObj = familyGrouping.families || {};
    const familyKeysCount = Object.keys(familiesObj).length;

    assert.strictEqual(totalFamilies, 361, `Must group into exactly 361 families, found summary ${totalFamilies}`);
    assert.strictEqual(familyKeysCount, 361, `Families dictionary must contain exactly 361 family keys, found ${familyKeysCount}`);
  });

  reporter.test('T1.F3.3: Multi-File vs Single-File Family Distribution', () => {
    const multiCount = familyGrouping.summary?.multi_file_families;
    const singleCount = familyGrouping.summary?.single_file_families;

    assert.strictEqual(multiCount, 139, `Must have exactly 139 multi-file families, found ${multiCount}`);
    assert.strictEqual(singleCount, 222, `Must have exactly 222 single-file families, found ${singleCount}`);
    assert.strictEqual(multiCount + singleCount, 361, 'Multi + Single families must sum to 361');
  });

  reporter.test('T1.F3.4: Drive URL Format & Sharing Parameter Verification', () => {
    const validUrl = 'https://drive.google.com/drive/folders/1z1cX0IypiugwXD1vR0IlWySKXHt-7r4y?usp=sharing';
    const invalidUrl1 = 'https://drive.google.com/file/d/1z1cX0IypiugwXD1vR0IlWySKXHt-7r4y/view';
    const invalidUrl2 = 'ftp://drive.google.com/123';

    assert.ok(DrivePackaging.isValidDriveUrl(validUrl), 'Standard folder link with usp=sharing must be valid');
    assert.ok(!DrivePackaging.isValidDriveUrl(invalidUrl1), 'File link should not be mistaken for folder link');
    assert.ok(!DrivePackaging.isValidDriveUrl(invalidUrl2), 'Invalid protocol should be rejected');
  });

  reporter.test('T1.F3.5: Canonical SVN Family Naming Integrity', () => {
    const families = Object.keys(familyGrouping.families || {});
    // Check that majority of families use SVN- prefix
    const svnFamilies = families.filter(f => f.startsWith('SVN-'));
    assert.ok(svnFamilies.length >= 350, `At least 350 families must maintain SVN- prefix, found ${svnFamilies.length}`);

    // Check specific notable families exist (e.g. SVN-IntegralCF or SVN-Integral CF, SVN-Saol Standard)
    const hasIntegral = families.includes('SVN-IntegralCF') || families.includes('SVN-Integral CF');
    assert.ok(hasIntegral, 'Must contain SVN-IntegralCF family');
    assert.ok(families.includes('SVN-Saol Standard'), 'Must contain SVN-Saol Standard family');
  });

  reporter.test('T1.F3.6: Drive Parent Folder ID Anchor Consistency', () => {
    const parentId = familyGrouping.summary?.parent_folder_id;
    assert.strictEqual(
      parentId,
      '1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao',
      'Target parent folder ID must match the authoritative Google Drive root folder'
    );
  });

  // =========================================================================
  // F4: Instant Search & Multi-Filtering Logic (6 tests)
  // =========================================================================

  reporter.test('T1.F4.1: Instant Diacritic-Insensitive Search by Font Name', () => {
    const results = SearchEngine.instantSearch(fonts, 'acta');
    assert.ok(results.length >= 1, 'Search for "acta" should find at least SVN-Acta / Acta');
    assert.ok(results[0].name.toLowerCase().includes('acta'), 'First match should be Acta');
  });

  reporter.test('T1.F4.2: Diacritic-Insensitive Search Across Director Notes', () => {
    // "tuyen ngon" should match fonts with "tuyên ngôn" in mood or notes
    const results = SearchEngine.instantSearch(fonts, 'tuyen ngon');
    assert.ok(results.length >= 1, 'Search for "tuyen ngon" should match fonts with "tuyên ngôn"');
  });

  reporter.test('T1.F4.3: Visual Category Filter Isolation', () => {
    const serifResults = SearchEngine.multiFilter(fonts, { category: 'Serif' });
    assert.ok(serifResults.length >= 35, `Serif filter should return >=35 fonts, found ${serifResults.length}`);

    // All returned fonts must be Serif (and not Sans Serif)
    for (const f of serifResults) {
      const cat = (f.category || f.core_section || '').toLowerCase();
      assert.ok(cat.includes('serif') && !cat.includes('sans'), `Font ${f.name} in Serif filter must not be Sans Serif`);
    }
  });

  reporter.test('T1.F4.4: Brand Mood Filter Isolation (Luxury & Sang trọng)', () => {
    const luxuryResults = SearchEngine.multiFilter(fonts, { mood: 'Luxury & Sang trọng' });
    assert.ok(luxuryResults.length >= 10, `Luxury filter should return >=10 fonts, found ${luxuryResults.length}`);

    for (const f of luxuryResults) {
      const mood = f.matrix_3d?.mood || f.matrix_mood || '';
      assert.ok(mood.toLowerCase().includes('luxury'), `Font ${f.name} in Luxury filter should have Luxury mood`);
    }
  });

  reporter.test('T1.F4.5: Application Context Filter Isolation (Display / Headline)', () => {
    const displayResults = SearchEngine.multiFilter(fonts, { use_case: 'Display' });
    assert.ok(displayResults.length >= 50, `Display use-case should return >=50 fonts, found ${displayResults.length}`);
  });

  reporter.test('T1.F4.6: Multi-Criteria Intersection Filtering', () => {
    const results = SearchEngine.multiFilter(fonts, {
      category: 'Sans Serif',
      mood: 'Tech & Công nghệ',
      vietnamese_support: true
    });

    assert.ok(results.length >= 1, 'Should find at least 1 font matching Sans Serif + Tech Mood + Vietnamese support');
    for (const f of results) {
      const cat = (f.category || f.core_section || '').toLowerCase();
      const mood = (f.matrix_3d?.mood || f.matrix_mood || '').toLowerCase();
      assert.ok(cat.includes('sans'), `Font ${f.name} must be Sans Serif, found ${cat}`);
      assert.ok(mood.includes('tech'), `Font ${f.name} must be Tech mood, found ${mood}`);
    }
  });
}

module.exports = { runTier1Tests };
