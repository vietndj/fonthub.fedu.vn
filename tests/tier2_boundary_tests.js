/**
 * tests/tier2_boundary_tests.js
 * Tier 2: Boundary, Extreme & Vietnamese Diacritic Tests (>=5 tests per feature area)
 *
 * Verifies edge cases, extreme values, Vietnamese tone marks,
 * and adversarial inputs.
 */

const assert = require('assert');
const {
  resolveCatalog,
  TypeTesterMetrics,
  SearchEngine,
  removeVietnameseDiacritics,
  VIETNAMESE_LOWERCASE,
  VIETNAMESE_UPPERCASE,
  COMPLEX_VIETNAMESE_WORDS
} = require('./lib/engine');

function runTier2Tests(reporter) {
  reporter.startSuite('Tier 2: Boundary, Extreme & Vietnamese Diacritic Tests');

  const catalogResult = resolveCatalog();
  if (!catalogResult) {
    throw new Error('FATAL: Unable to resolve font catalog for Tier 2 tests.');
  }
  const fonts = catalogResult.data.fonts || [];

  // =========================================================================
  // T2.1: Boundary Font Size Metrics (5 tests)
  // =========================================================================

  reporter.test('T2.1.1: Exact Minimum Boundary 14px Invariance', () => {
    assert.strictEqual(TypeTesterMetrics.clampFontSize(14), 14);
    assert.strictEqual(TypeTesterMetrics.clampFontSize('14'), 14);
    assert.strictEqual(TypeTesterMetrics.clampFontSize('14px'), 14);
  });

  reporter.test('T2.1.2: Exact Maximum Boundary 140px Invariance', () => {
    assert.strictEqual(TypeTesterMetrics.clampFontSize(140), 140);
    assert.strictEqual(TypeTesterMetrics.clampFontSize('140'), 140);
    assert.strictEqual(TypeTesterMetrics.clampFontSize('140px'), 140);
  });

  reporter.test('T2.1.3: Sub-Minimum Underflow Clamping (<14px)', () => {
    assert.strictEqual(TypeTesterMetrics.clampFontSize(13.9), 14);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(0), 14);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(-50), 14);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(-Infinity), 14);
  });

  reporter.test('T2.1.4: Overflow Clamping (>140px)', () => {
    assert.strictEqual(TypeTesterMetrics.clampFontSize(140.1), 140);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(500), 140);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(99999), 140);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(Infinity), 140);
  });

  reporter.test('T2.1.5: Non-Numeric & Malformed Input Fallback', () => {
    assert.strictEqual(TypeTesterMetrics.clampFontSize(null), 36);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(undefined), 36);
    assert.strictEqual(TypeTesterMetrics.clampFontSize('abc'), 36);
    assert.strictEqual(TypeTesterMetrics.clampFontSize(''), 36);
    assert.strictEqual(TypeTesterMetrics.clampFontSize({}), 36);
  });

  // =========================================================================
  // T2.2: Extreme Kerning & Line-Height Bounds (5 tests)
  // =========================================================================

  reporter.test('T2.2.1: Kerning Boundaries (-0.05em and +0.30em)', () => {
    assert.strictEqual(TypeTesterMetrics.clampKerning(-0.05), -0.05);
    assert.strictEqual(TypeTesterMetrics.clampKerning(0.30), 0.30);
  });

  reporter.test('T2.2.2: Extreme Negative Kerning Clamping (-0.50em -> -0.05em)', () => {
    assert.strictEqual(TypeTesterMetrics.clampKerning(-0.051), -0.05);
    assert.strictEqual(TypeTesterMetrics.clampKerning(-0.50), -0.05);
    assert.strictEqual(TypeTesterMetrics.clampKerning(-10.0), -0.05);
  });

  reporter.test('T2.2.3: Extreme Positive Kerning Clamping (+1.0em -> +0.30em)', () => {
    assert.strictEqual(TypeTesterMetrics.clampKerning(0.301), 0.30);
    assert.strictEqual(TypeTesterMetrics.clampKerning(1.0), 0.30);
    assert.strictEqual(TypeTesterMetrics.clampKerning(5.0), 0.30);
  });

  reporter.test('T2.2.4: Line-Height Boundary Clamping (0.8 and 2.4)', () => {
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(0.8), 0.8);
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(2.4), 2.4);
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(0.0), 0.8);
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(10.0), 2.4);
  });

  reporter.test('T2.2.5: Decimal Precision Preservation in Metrics', () => {
    assert.strictEqual(TypeTesterMetrics.clampLineHeight(1.33333), 1.33);
    assert.strictEqual(TypeTesterMetrics.clampKerning(0.125), 0.125);
  });

  // =========================================================================
  // T2.3: Complex Vietnamese Tone Combinations & Unicode Norm (6 tests)
  // =========================================================================

  reporter.test('T2.3.1: Complex Vietnamese Multi-Tone Words Preservation', () => {
    for (const word of COMPLEX_VIETNAMESE_WORDS) {
      const bound = TypeTesterMetrics.applyTransform(word, 'none');
      assert.strictEqual(bound, word, `Multi-tone word '${word}' must retain 100% diacritic integrity`);
    }
  });

  reporter.test('T2.3.2: Uppercase Complex Diacritics Invariance', () => {
    const testCases = [
      { input: 'nghiêng', expected: 'NGHIÊNG' },
      { input: 'thưởng', expected: 'THƯỞNG' },
      { input: 'khuyến', expected: 'KHUYẾN' },
      { input: 'truyền', expected: 'TRUYỀN' },
      { input: 'đồ họa', expected: 'ĐỒ HỌA' }
    ];

    for (const { input, expected } of testCases) {
      assert.strictEqual(
        TypeTesterMetrics.applyTransform(input, 'uppercase'),
        expected,
        `Uppercase transformation of '${input}' must match '${expected}'`
      );
    }
  });

  reporter.test('T2.3.3: 67 Lowercase Vietnamese Characters Diacritic Normalization', () => {
    for (const ch of VIETNAMESE_LOWERCASE) {
      const norm = removeVietnameseDiacritics(ch);
      assert.ok(norm.length === 1, `Normalized form of '${ch}' must be 1 character, got '${norm}'`);
      assert.ok(/^[a-z]$/.test(norm), `Normalized form '${norm}' of '${ch}' must be standard ASCII [a-z]`);
    }
  });

  reporter.test('T2.3.4: 67 Uppercase Vietnamese Characters Diacritic Normalization', () => {
    for (const ch of VIETNAMESE_UPPERCASE) {
      const norm = removeVietnameseDiacritics(ch);
      assert.ok(norm.length === 1, `Normalized form of uppercase '${ch}' must be 1 character, got '${norm}'`);
      assert.ok(/^[a-z]$/i.test(norm), `Normalized form '${norm}' of uppercase '${ch}' must be standard ASCII`);
    }
  });

  reporter.test('T2.3.5: Unicode NFC vs NFD Equivalence in Search Matching', () => {
    // NFC (Precomposed) vs NFD (Decomposed)
    const nfcWord = 'Tiếng Việt'; // Precomposed
    const nfdWord = nfcWord.normalize('NFD'); // Decomposed into base + combining accents

    assert.notStrictEqual(nfcWord, nfdWord, 'NFC and NFD binary encodings must differ');
    assert.strictEqual(
      removeVietnameseDiacritics(nfcWord),
      removeVietnameseDiacritics(nfdWord),
      'Search normalizer must yield identical tokens for both NFC and NFD forms'
    );
  });

  reporter.test('T2.3.6: Special Vietnamese Letter "Đ" / "đ" Search Equivalence', () => {
    assert.strictEqual(removeVietnameseDiacritics('đường'), 'duong');
    assert.strictEqual(removeVietnameseDiacritics('ĐẠI HỌC'), 'dai hoc');
  });

  // =========================================================================
  // T2.4: Search & Filter Adversarial & Boundary Cases (6 tests)
  // =========================================================================

  reporter.test('T2.4.1: Empty & Whitespace Query Returns Complete Catalog', () => {
    const emptyResults = SearchEngine.instantSearch(fonts, '');
    assert.strictEqual(emptyResults.length, fonts.length, 'Empty search query must return all fonts');

    const whitespaceResults = SearchEngine.instantSearch(fonts, '     ');
    assert.strictEqual(whitespaceResults.length, fonts.length, 'Whitespace-only query must return all fonts');
  });

  reporter.test('T2.4.2: Non-Existent Visual Category Graceful Zero Results', () => {
    const results = SearchEngine.multiFilter(fonts, { category: 'QuantumHologramSerif' });
    assert.ok(Array.isArray(results), 'Must return an array');
    assert.strictEqual(results.length, 0, 'Non-existent category must yield 0 results without errors');
  });

  reporter.test('T2.4.3: Non-Existent Mood Graceful Zero Results', () => {
    const results = SearchEngine.multiFilter(fonts, { mood: 'CyberPsychoVibe' });
    assert.ok(Array.isArray(results), 'Must return an array');
    assert.strictEqual(results.length, 0, 'Non-existent mood must yield 0 results without errors');
  });

  reporter.test('T2.4.4: Regex Metacharacters in Search Sanitization', () => {
    const metaQueries = [
      '.*', '+', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|', '\\'
    ];

    for (const q of metaQueries) {
      assert.doesNotThrow(() => {
        const res = SearchEngine.instantSearch(fonts, q);
        assert.ok(Array.isArray(res));
      }, `Search query containing regex character '${q}' must not trigger RegExp compilation error`);
    }
  });

  reporter.test('T2.4.5: Script Injection & XSS Payloads in Search String', () => {
    const xssPayloads = [
      "<script>alert('xss')</script>",
      "'\"><img src=x onerror=alert(1)>",
      "javascript:/*--></title></style></textarea>*/<script>alert(1)</script>"
    ];

    for (const payload of xssPayloads) {
      const results = SearchEngine.instantSearch(fonts, payload);
      assert.ok(Array.isArray(results), 'XSS payload in search must evaluate safely to an array');
      assert.strictEqual(results.length, 0, 'XSS payloads should match 0 font names');
    }
  });

  reporter.test('T2.4.6: Null, Undefined, & Malformed Catalog Protection', () => {
    assert.deepStrictEqual(SearchEngine.instantSearch(null, 'test'), []);
    assert.deepStrictEqual(SearchEngine.instantSearch(undefined, 'test'), []);
    assert.deepStrictEqual(SearchEngine.instantSearch({}, 'test'), []);
    assert.deepStrictEqual(SearchEngine.multiFilter(null, {}), []);
    assert.deepStrictEqual(SearchEngine.multiFilter(undefined, {}), []);
  });
}

module.exports = { runTier2Tests };
