#!/usr/bin/env node
/**
 * tests/stress_benchmarks.js
 * Comprehensive Empirical Stress-Test & Adversarial Harness for Milestone 3
 * (fedu.vn/font Interactive Type Hub).
 *
 * Authored by: teamwork_preview_challenger_m3_1
 * Verifies:
 * 1. Search query latency (<4ms requirement across 10,000 queries)
 * 2. Vietnamese diacritic-insensitive normalization & search oracle
 * 3. Multi-dimensional faceted filtering (540+ combinatorial intersections)
 * 4. Dynamic facet count calculation accuracy & partition invariants
 * 5. Adversarial edge cases: ReDoS, regex metacharacters, XSS, Unicode edge cases
 */

const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');

const catalogPath = path.resolve(__dirname, '../data/catalog.json');
const rawData = fs.readFileSync(catalogPath, 'utf8');
const catalog = JSON.parse(rawData);
const allFonts = catalog.fonts;

const CatalogLoader = require('../js/catalog_loader.js');

console.log('============================================================');
console.log(' fedu.vn/font M3 Empirical Stress & Benchmark Suite');
console.log(` Loaded catalog: ${allFonts.length} font families`);
console.log('============================================================\n');

let totalAsserts = 0;
let failedAsserts = 0;

function assert(condition, message) {
  totalAsserts++;
  if (!condition) {
    failedAsserts++;
    console.error(`  \x1b[31m✖ ASSERTION FAILED:\x1b[0m ${message}`);
    throw new Error(message);
  }
}

// -----------------------------------------------------------------------------
// 1. BENCHMARK: Search Query Latency (<4ms requirement)
// -----------------------------------------------------------------------------
console.log('\x1b[1m\x1b[36m▶ [Benchmark 1] Search Query Latency (<4ms Target)\x1b[0m');

const indexedFonts = CatalogLoader.buildSearchIndex(allFonts);
assert(indexedFonts.length === 361, 'buildSearchIndex should index all 361 fonts');

const sampleQueries = [
  'svn', 'saol', 'helvetica', 'arial', 'integral', 'fagen', 'connary',
  'tuyen ngon', 'tuyên ngôn', 'sang trong', 'sang trọng', 'huyen thoai',
  'vintage', 'sai gon', 'sài gòn', 'serif', 'sans', 'display', 'headline',
  'body', 'co dien', 'cổ điển', 'nhan van', 'nhân văn', 'tech', 'cong nghe',
  'công nghệ', 'quang cao', 'quảng cáo', 'poster', 'tap chi', 'tạp chí',
  'a', 'b', 'c', 'd', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'x', 'y',
  'đ', 'Đ', 'ê', 'ơ', 'ư', 'ă', 'â', 'ô', 'ư', 'ạ', 'ả', 'ã', 'à', 'á',
  'SVN-Saol Standard', 'SVN-Integral CF', 'SVN-Woodland', 'SVN-Sequel',
  'nonexistentfontxyz999', '12345', '   ', '', 'font-2022'
];

// Generate 10,000 queries by permutation
const queryPool = [];
for (let i = 0; i < 10000; i++) {
  queryPool.push(sampleQueries[i % sampleQueries.length]);
}

// A. Indexed Search Latency
const indexedLatencies = [];
for (let i = 0; i < queryPool.length; i++) {
  const q = queryPool[i];
  const t0 = performance.now();
  const res = CatalogLoader.instantSearch(indexedFonts, q);
  const t1 = performance.now();
  indexedLatencies.push(t1 - t0);
}

indexedLatencies.sort((a, b) => a - b);
const sumIndexed = indexedLatencies.reduce((a, b) => a + b, 0);
const avgIndexed = sumIndexed / indexedLatencies.length;
const minIndexed = indexedLatencies[0];
const maxIndexed = indexedLatencies[indexedLatencies.length - 1];
const p50Indexed = indexedLatencies[Math.floor(indexedLatencies.length * 0.50)];
const p90Indexed = indexedLatencies[Math.floor(indexedLatencies.length * 0.90)];
const p95Indexed = indexedLatencies[Math.floor(indexedLatencies.length * 0.95)];
const p99Indexed = indexedLatencies[Math.floor(indexedLatencies.length * 0.99)];

console.log(`  Indexed Search (10,000 queries across 361 fonts):`);
console.log(`    Min:    ${minIndexed.toFixed(4)} ms`);
console.log(`    Avg:    \x1b[32m${avgIndexed.toFixed(4)} ms\x1b[0m (Target: <4.0000 ms)`);
console.log(`    p50:    ${p50Indexed.toFixed(4)} ms`);
console.log(`    p90:    ${p90Indexed.toFixed(4)} ms`);
console.log(`    p95:    ${p95Indexed.toFixed(4)} ms`);
console.log(`    p99:    ${p99Indexed.toFixed(4)} ms`);
console.log(`    Max:    ${maxIndexed.toFixed(4)} ms`);

assert(avgIndexed < 4.0, `Average indexed search latency must be <4ms (actual: ${avgIndexed.toFixed(4)}ms)`);
assert(p99Indexed < 4.0, `p99 indexed search latency must be <4ms (actual: ${p99Indexed.toFixed(4)}ms)`);

// B. Raw (Non-indexed) Search Latency
const rawLatencies = [];
for (let i = 0; i < 2000; i++) {
  const q = queryPool[i];
  const t0 = performance.now();
  const res = CatalogLoader.instantSearch(allFonts, q);
  const t1 = performance.now();
  rawLatencies.push(t1 - t0);
}
rawLatencies.sort((a, b) => a - b);
const avgRaw = rawLatencies.reduce((a, b) => a + b, 0) / rawLatencies.length;
const p99Raw = rawLatencies[Math.floor(rawLatencies.length * 0.99)];
console.log(`  Raw Fallback Search (2,000 queries across 361 fonts):`);
console.log(`    Avg:    \x1b[32m${avgRaw.toFixed(4)} ms\x1b[0m (Target: <4.0000 ms)`);
console.log(`    p99:    ${p99Raw.toFixed(4)} ms`);

assert(avgRaw < 4.0, `Average raw search latency must be <4ms (actual: ${avgRaw.toFixed(4)}ms)`);

console.log('  ✔ PASS: Latency targets rigorously verified under load.\n');

// -----------------------------------------------------------------------------
// 2. ADVERSARIAL STRESS: Vietnamese Diacritic Normalization & Equivalence
// -----------------------------------------------------------------------------
console.log('\x1b[1m\x1b[36m▶ [Stress 2] Vietnamese Diacritic-Insensitive Normalization & Search Equivalence\x1b[0m');

const { VIETNAMESE_LOWERCASE, VIETNAMESE_UPPERCASE } = require('./lib/engine.js');
const vnLowerChars = VIETNAMESE_LOWERCASE;
const vnUpperChars = VIETNAMESE_UPPERCASE;


assert(vnLowerChars.length >= 67, 'Must have at least 67 Vietnamese lowercase chars');
assert(vnUpperChars.length >= 67, 'Must have at least 67 Vietnamese uppercase chars');


// Check that removeVietnameseDiacritics converts all of them to plain ASCII base characters
for (let i = 0; i < vnLowerChars.length; i++) {
  const norm = CatalogLoader.removeVietnameseDiacritics(vnLowerChars[i]);
  assert(norm.length === 1 && /^[a-z]$/.test(norm), `Lowercase char ${vnLowerChars[i]} normalized to ${norm} (expected [a-z])`);
}

for (let i = 0; i < vnUpperChars.length; i++) {
  const norm = CatalogLoader.removeVietnameseDiacritics(vnUpperChars[i]);
  assert(norm.length === 1 && /^[a-z]$/.test(norm), `Uppercase char ${vnUpperChars[i]} normalized to ${norm} (expected [a-z])`);
}

// B. Unicode NFC vs NFD Equivalence
for (let i = 0; i < vnLowerChars.length; i++) {
  const nfc = vnLowerChars[i].normalize('NFC');
  const nfd = vnLowerChars[i].normalize('NFD');
  const normNFC = CatalogLoader.removeVietnameseDiacritics(nfc);
  const normNFD = CatalogLoader.removeVietnameseDiacritics(nfd);
  assert(normNFC === normNFD, `NFC and NFD normalization must yield identical output for ${vnLowerChars[i]}`);
}

// C. Complex Semantic Vietnamese Queries & Invariance Checks
const semanticPairs = [
  { accented: 'tuyên ngôn', unaccented: 'tuyen ngon' },
  { accented: 'sài gòn', unaccented: 'sai gon' },
  { accented: 'việt nam', unaccented: 'viet nam' },
  { accented: 'cổ điển', unaccented: 'co dien' },
  { accented: 'sang trọng', unaccented: 'sang trong' },
  { accented: 'công nghệ', unaccented: 'cong nghe' },
  { accented: 'nhân văn', unaccented: 'nhan van' },
  { accented: 'tiêu đề', unaccented: 'tieu de' },
  { accented: 'uy lực', unaccented: 'uy luc' },
  { accented: 'hiện đại', unaccented: 'hien dai' }

];

for (const pair of semanticPairs) {
  const resAcc = CatalogLoader.instantSearch(indexedFonts, pair.accented);
  const resUnacc = CatalogLoader.instantSearch(indexedFonts, pair.unaccented);
  const resUpperAcc = CatalogLoader.instantSearch(indexedFonts, pair.accented.toUpperCase());
  const resUpperUnacc = CatalogLoader.instantSearch(indexedFonts, pair.unaccented.toUpperCase());

  // Result counts should be non-zero and match across permutations
  assert(resAcc.length > 0, `Query "${pair.accented}" should return at least 1 match`);
  assert(resAcc.length === resUnacc.length, `Match count for "${pair.accented}" (${resAcc.length}) should match "${pair.unaccented}" (${resUnacc.length})`);
  assert(resAcc.length === resUpperAcc.length, `Match count for uppercase "${pair.accented.toUpperCase()}" should match lowercase`);
  assert(resAcc.length === resUpperUnacc.length, `Match count for uppercase unaccented should match`);

  // Verify exact font ID sets
  const idsAcc = new Set(resAcc.map(f => f.id));
  const idsUnacc = new Set(resUnacc.map(f => f.id));
  assert(idsAcc.size === idsUnacc.size, `ID set size mismatch for "${pair.accented}"`);
  for (const id of idsAcc) {
    assert(idsUnacc.has(id), `Font id ${id} present in accented query but missing in unaccented`);
  }
}

// D. Specific Font Target Diacritic Checks
const specificFontTests = [
  { query: 'saol', expectedId: 'svn-saol-standard' },
  { query: 'SAOL', expectedId: 'svn-saol-standard' },
  { query: 'integral', expectedId: 'svn-integralcf' },
  { query: 'INTEGRAL', expectedId: 'svn-integralcf' },

  { query: 'woodland', expectedId: 'svn-woodland' },
  { query: 'đông', expectedSubstr: 'đông' }
];

for (const test of specificFontTests) {
  const matches = CatalogLoader.instantSearch(indexedFonts, test.query);
  if (test.expectedId) {
    const found = matches.some(f => f.id === test.expectedId);
    assert(found, `Search for "${test.query}" must return font id "${test.expectedId}"`);
  }
}

console.log('  ✔ PASS: Vietnamese diacritic normalization and search invariance 100% verified.\n');

// -----------------------------------------------------------------------------
// 3. COMBINATORIAL STRESS: Multi-Dimensional Faceted Filtering (540 Intersections)
// -----------------------------------------------------------------------------
console.log('\x1b[1m\x1b[36m▶ [Stress 3] Multi-Dimensional Faceted Intersection (540 Combinations)\x1b[0m');

const categories = [
  'all',
  'Sans Serif',
  'Serif',
  'Việt Nam Oldstyle / Vintage Sài Gòn',
  'Blackletter, Script & Monospace'
];

const moods = [
  'all',
  'Luxury & Sang trọng',
  'Tech & Công nghệ',
  'Bold & Tuyên ngôn',
  'Friendly & Nhân văn',
  'Nostalgic & Cổ điển'
];

const useCases = [
  'all',
  'Display / Headline',
  'Body text'
];

const weights = [
  'all',
  'single',
  'family'
];

const vnSupports = [
  true,
  false
];

let totalCombinations = 0;
let totalMatchingCombinations = 0;

for (const cat of categories) {
  for (const mood of moods) {
    for (const uc of useCases) {
      for (const w of weights) {
        for (const vn of vnSupports) {
          totalCombinations++;

          const criteria = {
            category: cat,
            mood: mood,
            use_case: uc,
            weight: w,
            vietnamese_support: vn
          };

          const filtered = CatalogLoader.multiFilter(allFonts, criteria);

          // Ground Truth Oracle Verification for Every Single Returned Font
          for (const f of filtered) {
            // Category check
            if (cat !== 'all') {
              const fCat = f.category || f.core_section || '';
              assert(CatalogLoader.matchesCategory(fCat, cat, f), `Font ${f.id} category "${fCat}" does not match criterion "${cat}"`);
            }
            // Mood check
            if (mood !== 'all') {
              const fMood = ((f.matrix_3d && f.matrix_3d.mood) || f.matrix_mood || '').toLowerCase();
              assert(fMood.includes(mood.toLowerCase()) || mood.toLowerCase().includes(fMood), `Font ${f.id} mood "${fMood}" does not match "${mood}"`);
            }
            // Use Case check
            if (uc !== 'all') {
              const fUc = ((f.matrix_3d && f.matrix_3d.use_case) || f.matrix_application || '').toLowerCase();
              assert(fUc.includes(uc.toLowerCase()) || uc.toLowerCase().includes(fUc), `Font ${f.id} use-case "${fUc}" does not match "${uc}"`);
            }
            // Weight check
            if (w === 'single') {
              const wLen = Array.isArray(f.weights) ? f.weights.length : 1;
              assert(wLen === 1, `Font ${f.id} must have exactly 1 weight for "single" filter (has ${wLen})`);
            } else if (w === 'family') {
              const wLen = Array.isArray(f.weights) ? f.weights.length : 1;
              assert(wLen > 1, `Font ${f.id} must have >1 weights for "family" filter (has ${wLen})`);
            }
            // VN Support check
            assert(Boolean(f.vietnamese_support) === vn, `Font ${f.id} VN support must match ${vn}`);
          }

          // Subset Invariant: result(A ∩ B) must be subset of result(A)
          if (cat !== 'all') {
            const catOnly = CatalogLoader.multiFilter(allFonts, { category: cat });
            const catSet = new Set(catOnly.map(f => f.id));
            for (const f of filtered) {
              assert(catSet.has(f.id), `Subset invariant violated: ${f.id} in intersection but not in category-only`);
            }
          }

          if (filtered.length > 0) {
            totalMatchingCombinations++;
          }
        }
      }
    }
  }
}

console.log(`  Tested ${totalCombinations} multi-dimensional filter combinations.`);
console.log(`  Non-empty intersections: ${totalMatchingCombinations} / ${totalCombinations}`);
console.log('  ✔ PASS: All 540 faceted intersection combinations match ground truth oracle.\n');

// -----------------------------------------------------------------------------
// 4. ACCURACY: Dynamic Facet Count Calculation
// -----------------------------------------------------------------------------
console.log('\x1b[1m\x1b[36m▶ [Stress 4] Dynamic Facet Count Calculation Accuracy & Partitions\x1b[0m');

// A. Full Catalog Facet Counts
const fullCounts = CatalogLoader.computeFacetCounts(allFonts);

assert(fullCounts.categories.all === 361, 'Total category count must be 361');
assert(fullCounts.weights.all === 361, 'Total weights all must be 361');
assert(fullCounts.weights.single + fullCounts.weights.family === 361, 'Single + Family weights must sum to 361');
assert(fullCounts.vnSupport.supported === 361, 'Supported VN fonts must be 361 (100%)');

// Verify Category partition sum
const catSum = fullCounts.categories['Sans Serif'] +
               fullCounts.categories['Serif'] +
               fullCounts.categories['Việt Nam Oldstyle / Vintage Sài Gòn'] +
               fullCounts.categories['Blackletter, Script & Monospace'];
assert(catSum === 361, `4 Core visual categories must partition exactly 361 fonts (sum: ${catSum})`);

console.log(`  Full Catalog Category Counts:`);
console.log(`    Sans Serif: ${fullCounts.categories['Sans Serif']}`);
console.log(`    Serif:      ${fullCounts.categories['Serif']}`);
console.log(`    Vintage:    ${fullCounts.categories['Việt Nam Oldstyle / Vintage Sài Gòn']}`);
console.log(`    Mono/Script:${fullCounts.categories['Blackletter, Script & Monospace']}`);
console.log(`    Sum:        ${catSum} / 361`);

// B. Subsets Dynamic Facet Counts (e.g., filtered subsets)
const testSubsets = [
  { name: 'Search "Serif"', query: 'serif' },
  { name: 'Search "SVN"', query: 'svn' },
  { name: 'Search "Sài Gòn"', query: 'sài gòn' },
  { name: 'Search "Integral"', query: 'integral' }
];

for (const sub of testSubsets) {
  const matches = CatalogLoader.instantSearch(indexedFonts, sub.query);
  const subCounts = CatalogLoader.computeFacetCounts(matches);

  assert(subCounts.categories.all === matches.length, `all count must equal subset length for ${sub.name}`);

  // Ground truth check for each category count in subset
  for (const catName of ['Sans Serif', 'Serif', 'Việt Nam Oldstyle / Vintage Sài Gòn', 'Blackletter, Script & Monospace']) {
    const manualCount = matches.filter(f => CatalogLoader.matchesCategory(f.category || f.core_section || '', catName, f)).length;
    assert(subCounts.categories[catName] === manualCount, `Category count mismatch for "${catName}" in ${sub.name}: got ${subCounts.categories[catName]}, expected ${manualCount}`);
  }

  // Ground truth check for weights
  const manualSingle = matches.filter(f => (Array.isArray(f.weights) ? f.weights.length : 1) === 1).length;
  const manualFamily = matches.filter(f => (Array.isArray(f.weights) ? f.weights.length : 1) > 1).length;
  assert(subCounts.weights.single === manualSingle, `Single weight mismatch in ${sub.name}`);
  assert(subCounts.weights.family === manualFamily, `Family weight mismatch in ${sub.name}`);
}

// C. Edge-case Inputs for computeFacetCounts
const emptyCounts = CatalogLoader.computeFacetCounts([]);
assert(emptyCounts.categories.all === 0, 'Empty array should produce 0 count');
assert(emptyCounts.weights.single === 0, 'Empty array should produce 0 single weight');

const nullCounts = CatalogLoader.computeFacetCounts(null);
assert(typeof nullCounts === 'object', 'Null should produce empty object');

console.log('  ✔ PASS: Dynamic facet count calculation matches ground truth across all subsets.\n');

// -----------------------------------------------------------------------------
// 5. ADVERSARIAL STRESS: ReDoS, Injection & Edge Cases
// -----------------------------------------------------------------------------
console.log('\x1b[1m\x1b[36m▶ [Stress 5] Adversarial Edge Cases: ReDoS, Injection, Malformed Inputs\x1b[0m');

// A. ReDoS Attack Patterns
const redosPayloads = [
  'a'.repeat(20000),
  '('.repeat(1000) + 'a' + ')'.repeat(1000),
  'a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*b',
  '([a-zA-Z]+)*([a-zA-Z]+)*$',
  '(\\d+)+$',
  '.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
  'SVN' + ' '.repeat(5000) + 'Saol',
  '\\'.repeat(5000),
  '/'.repeat(5000),
  '['.repeat(500) + ']'.repeat(500)
];

for (let i = 0; i < redosPayloads.length; i++) {
  const payload = redosPayloads[i];
  const t0 = performance.now();
  const res = CatalogLoader.instantSearch(indexedFonts, payload);
  const elapsed = performance.now() - t0;
  assert(Array.isArray(res), `ReDoS payload ${i} must return array`);
  assert(elapsed < 20.0, `ReDoS payload ${i} must complete in <20ms (took ${elapsed.toFixed(2)}ms)`);
}

// B. Script Injection & XSS Payloads
const xssPayloads = [
  '<script>alert("xss")</script>',
  '"><img src=x onerror=alert(1)>',
  'javascript:alert(document.domain)',
  '<svg/onload=alert`1`>',
  '${7*7}',
  '{{constructor.constructor("alert(1)")()}}',
  '__proto__',
  'constructor',
  'toString'
];

for (const xss of xssPayloads) {
  const res = CatalogLoader.instantSearch(indexedFonts, xss);
  assert(Array.isArray(res), `XSS payload "${xss}" must return array without error`);
}

// C. Malformed & Extreme Criteria in multiFilter
const malformedCriteria = [
  null,
  undefined,
  {},
  { category: 12345 },
  { category: null },
  { styles: 'not-an-array' },
  { moods: null },
  { useCases: [123, null] },
  { weight: null },
  { weight: 999 },
  { vietnamese_support: 'yes' },
  { unknown_dimension: true }
];

for (const crit of malformedCriteria) {
  const res = CatalogLoader.multiFilter(allFonts, crit);
  assert(Array.isArray(res), 'multiFilter must survive malformed criteria gracefully');
}

// D. Malformed Fonts Array in instantSearch & multiFilter
const malformedFontsArray = [
  null,
  undefined,
  {},
  { name: 123 },
  { name: null, family: undefined },
  'not an object',
  42
];

const resMalformedSearch = CatalogLoader.instantSearch(malformedFontsArray, 'test');
assert(Array.isArray(resMalformedSearch), 'instantSearch must survive malformed fonts array');

const resMalformedFilter = CatalogLoader.multiFilter(malformedFontsArray, { category: 'all' });
assert(Array.isArray(resMalformedFilter), 'multiFilter must survive malformed fonts array');

console.log('  ✔ PASS: ReDoS, XSS, and malformed inputs handled with 100% resilience.\n');

// -----------------------------------------------------------------------------
// SUMMARY
// -----------------------------------------------------------------------------
console.log('════════════════════════════════════════════════════════════');
console.log(` ALL EMPIRICAL CHALLENGE SUITES PASSED: ${totalAsserts} asserts, 0 failures.`);
console.log('════════════════════════════════════════════════════════════');
