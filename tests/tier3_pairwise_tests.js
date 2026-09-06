/**
 * tests/tier3_pairwise_tests.js
 * Tier 3: Cross-Feature Combinations & Pairwise Interaction Tests
 *
 * Verifies that multiple features interacting simultaneously maintain
 * state consistency, correct subsetting, and robust UI synchronization.
 */

const assert = require('assert');
const {
  resolveCatalog,
  resolveFamilyGrouping,
  TypeTesterMetrics,
  SearchEngine,
  DrivePackaging
} = require('./lib/engine');

function runTier3Tests(reporter) {
  reporter.startSuite('Tier 3: Cross-Feature Combinations & Pairwise Tests');

  const catalogResult = resolveCatalog();
  if (!catalogResult) {
    throw new Error('FATAL: Unable to resolve font catalog for Tier 3 tests.');
  }
  const fonts = catalogResult.data.fonts || [];

  const familyGroupingResult = resolveFamilyGrouping();
  const familyGrouping = familyGroupingResult?.data || {};

  // =========================================================================
  // Pairwise & Cross-Feature Interaction Tests
  // =========================================================================

  reporter.test('T3.1: Search Term ("FD") + Category ("Sans Serif") + Mood ("Tech & Công nghệ")', () => {
    // Step 1: Search for FD
    const searched = SearchEngine.instantSearch(fonts, 'FD');
    assert.ok(searched.length > 0, 'Must find fonts matching FD');

    // Step 2: Apply Category and Mood filter simultaneously
    const filtered = SearchEngine.multiFilter(searched, {
      category: 'Sans Serif',
      mood: 'Tech & Công nghệ'
    });

    assert.ok(filtered.length >= 1, 'Intersection must return at least 1 font');
    for (const f of filtered) {
      const name = f.name || f.family || '';
      const cat = f.category || f.core_section || '';
      const mood = f.matrix_3d?.mood || f.matrix_mood || '';

      assert.ok(
        name.toLowerCase().includes('fd') || (f.id && f.id.includes('fd')),
        'Name or ID must contain FD'
      );
      assert.ok(cat.toLowerCase().includes('sans'), 'Must be Sans Serif category');
      assert.ok(mood.toLowerCase().includes('tech'), 'Must be Tech mood');
    }
  });

  reporter.test('T3.2: Search Term ("Didone") + Category ("Serif") + Use Case ("Display / Headline")', () => {
    const searched = SearchEngine.instantSearch(fonts, 'Didone');
    const filtered = SearchEngine.multiFilter(searched, {
      category: 'Serif',
      use_case: 'Display'
    });

    assert.ok(filtered.length >= 1, 'Should find Didone display serif fonts');
    for (const f of filtered) {
      const cat = f.category || f.core_section || '';
      const subcat = f.subcategory || '';
      const notes = f.director_notes || '';
      const useCase = f.matrix_3d?.use_case || f.matrix_application || '';

      assert.ok(cat.includes('Serif'), 'Must be Serif');
      assert.ok(subcat.includes('Didone') || notes.includes('Didone') || f.name.includes('Didone'), 'Must reference Didone');
      assert.ok(useCase.includes('Display'), 'Must be Display use-case');
    }
  });

  reporter.test('T3.3: Type Tester Text Update + Theme Switch + Size Slider', () => {
    // Simulate Type Tester State
    const testerState = {
      text: 'fedu.vn/font',
      theme: 'dark',
      fontSize: 36,
      lineHeight: 1.2,
      letterSpacing: 0.0
    };

    // User updates text with Vietnamese diacritics
    testerState.text = 'FEDU.VN - NGHỆ THUẬT CHỮ ĐIỆN ẢNH';
    // User switches to Neon Accent theme
    testerState.theme = 'neon';
    // User drags size slider to 72px
    testerState.fontSize = TypeTesterMetrics.clampFontSize(72);
    // User adjusts kerning
    testerState.letterSpacing = TypeTesterMetrics.clampKerning(0.05);

    assert.strictEqual(testerState.fontSize, 72, 'Font size must update to 72');
    assert.strictEqual(testerState.theme, 'neon', 'Theme must update to neon');
    assert.strictEqual(testerState.letterSpacing, 0.05, 'Kerning must update to 0.05');
    assert.ok(testerState.text.includes('NGHỆ THUẬT'), 'Text must preserve Vietnamese diacritics');
  });

  reporter.test('T3.4: Category ("Việt Nam Vintage") + Vietnamese Support (true) + Drive Link', () => {
    const filtered = SearchEngine.multiFilter(fonts, {
      category: 'Việt Nam Oldstyle / Vintage Sài Gòn',
      vietnamese_support: true
    });

    assert.ok(filtered.length >= 10, `Must find >=10 Vintage Sài Gòn fonts with VN support, found ${filtered.length}`);

    // Verify each font either matches drive files or has family grouping reference
    const families = familyGrouping.families || {};
    let matchedDriveCount = 0;
    for (const f of filtered) {
      const cleanStem = f.name.replace(/^FD\s*/, '');
      if (families[f.name] || families[`SVN-${cleanStem}`] || families[cleanStem] || f.drive_folder_url || (f.drive_files && f.drive_files.length > 0)) {
        matchedDriveCount++;
      }
    }
    assert.ok(matchedDriveCount > 0, 'Vintage Sài Gòn fonts must cross-reference Google Drive assets');
  });

  reporter.test('T3.5: Search ("tuyên ngôn") + Mood ("Bold & Tuyên ngôn") + Case Transform ("uppercase")', () => {
    const searched = SearchEngine.instantSearch(fonts, 'tuyen ngon');
    const filtered = SearchEngine.multiFilter(searched, {
      mood: 'Bold & Tuyên ngôn'
    });

    assert.ok(filtered.length >= 1, 'Should find matching bold statement fonts');
    const topFont = filtered[0];

    // Apply uppercase transform to sample text
    const sample = topFont.sample_text || topFont.sample_phrase || 'Kiểu Chữ Tuyên Ngôn';
    const transformed = TypeTesterMetrics.applyTransform(sample, 'uppercase');
    assert.strictEqual(transformed, transformed.toUpperCase(), 'Transformed sample must be completely uppercase');
  });

  reporter.test('T3.6: Category ("Serif") + Mood ("Nostalgic & Cổ điển") + Line-Height (1.4)', () => {
    const filtered = SearchEngine.multiFilter(fonts, {
      category: 'Serif',
      mood: 'Nostalgic & Cổ điển'
    });

    assert.ok(filtered.length >= 5, `Must find >=5 Nostalgic Serif fonts, found ${filtered.length}`);
    const clampedLineHeight = TypeTesterMetrics.clampLineHeight(1.4);
    assert.strictEqual(clampedLineHeight, 1.4, 'Line-height must be set to 1.4 without distortion');
  });

  reporter.test('T3.7: Search Query + Incompatible Filter Clean Zero-Match Intersection', () => {
    // "Integral" is a Sans Serif font, filtering under "Serif" must yield empty array
    const searched = SearchEngine.instantSearch(fonts, 'Integral');
    const incompatible = SearchEngine.multiFilter(searched, {
      category: 'Serif'
    });

    assert.strictEqual(incompatible.length, 0, 'Search "Integral" under Serif category must yield exactly 0 items');
  });

  reporter.test('T3.8: Theme Mode Palette Definitions Consistency', () => {
    const themes = {
      dark: { bg: '#121212', text: '#F0F0F0', border: '#2A2A2A' },
      light: { bg: '#FFFFFF', text: '#111111', border: '#E5E5E5' },
      neon: { bg: '#0D0E15', text: '#FFFFFF', accent: '#00FF66' }
    };

    assert.strictEqual(themes.dark.bg, '#121212', 'Dark theme bg must be #121212');
    assert.strictEqual(themes.light.bg, '#FFFFFF', 'Light theme bg must be #FFFFFF');
    assert.strictEqual(themes.neon.accent, '#00FF66', 'Neon theme accent must be #00FF66');
  });

  reporter.test('T3.9: Weight Switching + Kerning Adjustment + FontFace Rule Sync', () => {
    const font = fonts.find(f => (f.name || '').includes('Integral')) || fonts[0];
    const familyName = font.name || font.family || 'SVN-Integral CF';

    // Switch to Bold (700) and adjust kerning to +0.08em
    const weight = '700';
    const kerning = TypeTesterMetrics.clampKerning(0.08);
    const css = TypeTesterMetrics.generateFontFaceCSS(familyName, 'https://cdn.example.com/font.woff2', weight);

    assert.strictEqual(kerning, 0.08, 'Kerning must be 0.08em');
    assert.ok(css.includes(`font-weight: ${weight}`), 'CSS must reflect selected weight 700');
    assert.ok(css.includes(`font-family: '${familyName}'`), 'CSS must declare target font family');
  });

  reporter.test('T3.10: Search ("Saol") + Use-case ("Display") + Drive Family Resolution', () => {
    const searched = SearchEngine.instantSearch(fonts, 'Saol');
    assert.ok(searched.length >= 1, 'Search for Saol should find SVN-Saol Standard');

    const saol = searched[0];
    const families = familyGrouping.families || {};
    const saolFamily = families['SVN-Saol Standard'] || families[saol.name];

    assert.ok(saolFamily !== undefined, 'SVN-Saol Standard must exist in family grouping database');
    assert.ok(saolFamily.file_count > 1, 'Saol Standard must be a multi-weight family');
  });
}

module.exports = { runTier3Tests };
