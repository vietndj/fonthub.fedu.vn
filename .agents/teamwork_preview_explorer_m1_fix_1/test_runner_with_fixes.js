const assert = require('assert');
// Test all test suites with proposed engine fixes applied
const fs = require('fs');
const path = require('path');

// Read current engine.js
let engineCode = fs.readFileSync('/Users/vietmac/Documents/CODE/fedu-font/tests/lib/engine.js', 'utf8');

// Apply proposed matchesCategory fix
const oldMatchesCat = `function matchesCategory(fontCategory, targetCategory) {
  if (!fontCategory || !targetCategory) return false;
  const fc = fontCategory.toLowerCase().trim();
  const tc = targetCategory.toLowerCase().trim();

  if (tc === 'all') return true;

  // Serif vs Sans Serif discrimination
  if (tc === 'serif') {
    return fc.includes('serif') && !fc.includes('sans');
  }
  if (tc.includes('sans')) {
    return fc.includes('sans');
  }
  if (tc.includes('vintage') || tc.includes('sài gòn') || tc.includes('oldstyle')) {
    return fc.includes('vintage') || fc.includes('sài gòn') || fc.includes('oldstyle');
  }
  if (tc.includes('mono') || tc.includes('script') || tc.includes('blackletter')) {
    return fc.includes('mono') || fc.includes('script') || fc.includes('blackletter');
  }

  // Exact or word boundary match for custom / unknown categories
  return fc === tc || fc.split(/[\\s,/]+/).some(token => token === tc);
}`;

const newMatchesCat = `function matchesCategory(fontCategory, targetCategory, font = null) {
  if (!fontCategory || !targetCategory) return false;
  if (typeof fontCategory !== 'string' || typeof targetCategory !== 'string') return false;
  const fc = fontCategory.toLowerCase().trim();
  const tc = targetCategory.toLowerCase().trim();

  if (tc === 'all') return true;

  // Serif vs Sans Serif discrimination
  if (tc === 'serif') {
    return fc.includes('serif') && !fc.includes('sans');
  }
  if (tc.includes('sans')) {
    return fc.includes('sans');
  }
  if (tc.includes('vintage') || tc.includes('sài gòn') || tc.includes('oldstyle')) {
    return fc.includes('vintage') || fc.includes('sài gòn') || fc.includes('oldstyle');
  }

  // Monospace vs Script vs Blackletter isolation
  const fontStyle = (font?.matrix_3d?.style || font?.matrix_visual || '').toLowerCase();
  const fontSubcat = (font?.subcategory || '').toLowerCase();

  if (tc.includes('mono')) {
    if (fontStyle) return fontStyle.includes('mono');
    if (fontSubcat) return fontSubcat.includes('mono');
    return fc.includes('mono') && !fc.includes('script') && !fc.includes('blackletter');
  }
  if (tc.includes('script')) {
    if (fontStyle) return fontStyle.includes('script');
    if (fontSubcat) return fontSubcat.includes('script');
    return fc.includes('script');
  }
  if (tc.includes('blackletter') || tc.includes('fraktur')) {
    if (fontStyle) return fontStyle.includes('blackletter');
    if (fontSubcat) return fontSubcat.includes('blackletter') || fontSubcat.includes('fraktur');
    return fc.includes('blackletter') || fc.includes('fraktur');
  }

  // Broad composite category (e.g. "Blackletter, Script & Monospace")
  if (tc.includes('blackletter') && tc.includes('script') && tc.includes('mono')) {
    return fc.includes('mono') || fc.includes('script') || fc.includes('blackletter');
  }

  // Exact or word boundary match for custom / unknown categories
  return fc === tc || fc.split(/[\\s,/]+/).some(token => token === tc);
}`;

// Apply proposed multiFilter fix
const oldMultiFilter = `  multiFilter(fonts, criteria = {}) {
    if (!Array.isArray(fonts)) return [];

    return fonts.filter(font => {
      // 1. Category / Visual style filter
      if (criteria.category && criteria.category !== 'all') {
        const fontCat = font.category || font.core_section || '';
        if (!matchesCategory(fontCat, criteria.category)) {
          return false;
        }
      }

      // 2. Mood / Vibe filter (from 3D Matrix)
      if (criteria.mood && criteria.mood !== 'all') {
        const mood = (font.matrix_3d?.mood || font.matrix_mood || '').toLowerCase();
        const targetMood = criteria.mood.toLowerCase();
        if (!mood.includes(targetMood) && !targetMood.includes(mood)) {
          return false;
        }
      }

      // 3. Use-case filter (from 3D Matrix)
      if (criteria.use_case && criteria.use_case !== 'all') {
        const useCase = (font.matrix_3d?.use_case || font.matrix_application || '').toLowerCase();
        const targetUseCase = criteria.use_case.toLowerCase();
        if (!useCase.includes(targetUseCase) && !targetUseCase.includes(useCase)) {
          return false;
        }
      }

      // 4. Vietnamese Support flag
      if (typeof criteria.vietnamese_support === 'boolean') {
        const isSupported = typeof font.vietnamese_support === 'boolean'
          ? font.vietnamese_support
          : (font.vietnamese_status && font.vietnamese_status.startsWith('Supported'));
        if (isSupported !== criteria.vietnamese_support) {
          return false;
        }
      }

      // 5. Weight filter
      if (criteria.weight && criteria.weight !== 'all') {
        const weights = font.weights || [];
        if (!weights.some(w => w.toLowerCase().includes(criteria.weight.toLowerCase()))) {
          return false;
        }
      }

      return true;
    });
  }`;

const newMultiFilter = `  multiFilter(fonts, criteria = {}) {
    if (!Array.isArray(fonts)) return [];
    if (!criteria || typeof criteria !== 'object') return fonts;

    return fonts.filter(font => {
      if (!font || typeof font !== 'object') return false;

      // 1. Category / Visual style filter
      if (typeof criteria.category === 'string' && criteria.category !== 'all') {
        const fontCat = font.category || font.core_section || '';
        if (!matchesCategory(fontCat, criteria.category, font)) {
          return false;
        }
      }

      // 2. Mood / Vibe filter (from 3D Matrix)
      if (typeof criteria.mood === 'string' && criteria.mood !== 'all') {
        const mood = (font.matrix_3d?.mood || font.matrix_mood || '').toLowerCase();
        const targetMood = criteria.mood.toLowerCase();
        if (!mood.includes(targetMood) && !targetMood.includes(mood)) {
          return false;
        }
      }

      // 3. Use-case filter (from 3D Matrix)
      if (typeof criteria.use_case === 'string' && criteria.use_case !== 'all') {
        const useCase = (font.matrix_3d?.use_case || font.matrix_application || '').toLowerCase();
        const targetUseCase = criteria.use_case.toLowerCase();
        if (!useCase.includes(targetUseCase) && !targetUseCase.includes(useCase)) {
          return false;
        }
      }

      // 4. Vietnamese Support flag
      if (typeof criteria.vietnamese_support === 'boolean') {
        const isSupported = typeof font.vietnamese_support === 'boolean'
          ? font.vietnamese_support
          : (typeof font.vietnamese_status === 'string' && font.vietnamese_status.startsWith('Supported'));
        if (isSupported !== criteria.vietnamese_support) {
          return false;
        }
      }

      // 5. Weight filter
      if (typeof criteria.weight === 'string' && criteria.weight !== 'all') {
        const weights = Array.isArray(font.weights) ? font.weights : [];
        const targetWeight = criteria.weight.toLowerCase();
        if (!weights.some(w => typeof w === 'string' && w.toLowerCase().includes(targetWeight))) {
          return false;
        }
      }

      return true;
    });
  }`;

assert.ok(engineCode.includes(oldMatchesCat), "Old matchesCategory must be found");
assert.ok(engineCode.includes(oldMultiFilter), "Old multiFilter must be found");

engineCode = engineCode.replace(oldMatchesCat, newMatchesCat);
engineCode = engineCode.replace(oldMultiFilter, newMultiFilter);

// Write to temporary engine module in our agent directory
fs.writeFileSync(path.join(__dirname, 'mock_engine.js'), engineCode);
console.log("Mock engine created successfully!");
