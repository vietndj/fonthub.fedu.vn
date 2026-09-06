/**
 * tests/lib/engine.js
 * Authoritative specification reference engine and validation utilities
 * for fedu.vn/font Interactive Type Hub.
 *
 * Derived strictly from:
 * - ORIGINAL_REQUEST.md (Requirements R1, R2, R3, R4)
 * - PROJECT.md (Milestones M1-M4, Code Layout, Interface Contracts)
 */

const fs = require('fs');
const path = require('path');

// 67 Vietnamese characters with diacritics (lower + upper + d/Đ)
const VIETNAMESE_LOWERCASE = [
  'a', 'à', 'á', 'ả', 'ã', 'ạ',
  'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ',
  'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ',
  'e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ',
  'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ',
  'i', 'ì', 'í', 'ỉ', 'ĩ', 'ị',
  'o', 'ò', 'ó', 'ỏ', 'õ', 'ọ',
  'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ',
  'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ',
  'u', 'ù', 'ú', 'ủ', 'ũ', 'ụ',
  'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự',
  'y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ',
  'đ'
];

const VIETNAMESE_UPPERCASE = [
  'A', 'À', 'Á', 'Ả', 'Ã', 'Ạ',
  'Ă', 'Ằ', 'Ắ', 'Ẳ', 'Ẵ', 'Ặ',
  'Â', 'Ầ', 'Ấ', 'Ẩ', 'Ẫ', 'Ậ',
  'E', 'È', 'É', 'Ẻ', 'Ẽ', 'Ẹ',
  'Ê', 'Ề', 'Ế', 'Ể', 'Ễ', 'Ệ',
  'I', 'Ì', 'Í', 'Ỉ', 'Ĩ', 'Ị',
  'O', 'Ò', 'Ó', 'Ỏ', 'Õ', 'Ọ',
  'Ô', 'Ồ', 'Ố', 'Ổ', 'Ỗ', 'Ộ',
  'Ơ', 'Ờ', 'Ớ', 'Ở', 'Ỡ', 'Ợ',
  'U', 'Ù', 'Ú', 'Ủ', 'Ũ', 'Ụ',
  'Ư', 'Ừ', 'Ứ', 'Ử', 'Ữ', 'Ự',
  'Y', 'Ỳ', 'Ý', 'Ỷ', 'Ỹ', 'Ỵ',
  'Đ'
];

// Complex multi-tone Vietnamese words common in typography / editorial design
const COMPLEX_VIETNAMESE_WORDS = [
  'nghiêng', 'khuyến', 'thưởng', 'truyền', 'hoằng',
  'quế', 'phượng', 'chuộng', 'nguyện', 'ngưỡng',
  'THƯỞNG', 'NGHIÊNG', 'KHUYẾN', 'TRUYỀN', 'ĐỒ HỌA'
];

/**
 * Remove Vietnamese diacritics for fast sub-4ms indexing and search
 */
function removeVietnameseDiacritics(str) {
  if (!str || typeof str !== 'string') return '';
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[đĐ]/g, m => (m === 'đ' ? 'd' : 'D'))
    .toLowerCase()
    .trim();
}

/**
 * Robust category matcher that prevents 'serif' from falsely matching 'sans serif'
 */
function matchesCategory(fontCategory, targetCategory, font = null) {
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
  return fc === tc || fc.split(/[\s,/]+/).some(token => token === tc);
}

/**
 * Type Tester Metric Clamping & Calculation Model
 * Derived from ORIGINAL_REQUEST.md § R2 and PROJECT.md § M3
 */
const TypeTesterMetrics = {
  MIN_FONT_SIZE: 14,
  MAX_FONT_SIZE: 140,
  DEFAULT_FONT_SIZE: 36,

  MIN_LINE_HEIGHT: 0.8,
  MAX_LINE_HEIGHT: 2.4,
  DEFAULT_LINE_HEIGHT: 1.2,

  MIN_KERNING: -0.05,
  MAX_KERNING: 0.30,
  DEFAULT_KERNING: 0.0,

  clampFontSize(val) {
    const num = parseFloat(val);
    if (isNaN(num)) return this.DEFAULT_FONT_SIZE;
    return Math.max(this.MIN_FONT_SIZE, Math.min(this.MAX_FONT_SIZE, Math.round(num)));
  },

  clampLineHeight(val) {
    const num = parseFloat(val);
    if (isNaN(num)) return this.DEFAULT_LINE_HEIGHT;
    const clamped = Math.max(this.MIN_LINE_HEIGHT, Math.min(this.MAX_LINE_HEIGHT, num));
    return parseFloat(clamped.toFixed(2));
  },

  clampKerning(val) {
    const num = parseFloat(val);
    if (isNaN(num)) return this.DEFAULT_KERNING;
    const clamped = Math.max(this.MIN_KERNING, Math.min(this.MAX_KERNING, num));
    return parseFloat(clamped.toFixed(3));
  },

  applyTransform(text, transform) {
    if (!text || typeof text !== 'string') return '';
    switch (transform) {
      case 'uppercase':
        return text.toUpperCase();
      case 'lowercase':
        return text.toLowerCase();
      case 'titlecase':
      case 'capitalize':
        return text.replace(/\b(\w)/g, m => m.toUpperCase());
      default:
        return text;
    }
  },

  generateFontFaceCSS(family, webFontUrl, weight = 'normal', style = 'normal') {
    if (!family || !webFontUrl) return '';
    return `@font-face {\n  font-family: '${family}';\n  src: url('${webFontUrl}') format('woff2');\n  font-weight: ${weight};\n  font-style: ${style};\n  font-display: swap;\n}`;
  },

  getFallbackStack(category) {
    switch (category) {
      case 'Serif':
        return "Georgia, Cambria, 'Times New Roman', Times, serif";
      case 'Monospace':
        return "'SF Mono', Monaco, 'Courier New', Courier, monospace";
      case 'Script':
        return "'Brush Script MT', 'Apple Chancery', cursive";
      case 'Sans Serif':
      default:
        return "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    }
  }
};

/**
 * Search & Filtering Engine
 * Derived from ORIGINAL_REQUEST.md § R4 and PROJECT.md § Architecture
 */
const SearchEngine = {
  instantSearch(fonts, query) {
    if (!Array.isArray(fonts)) return [];
    if (!query || typeof query !== 'string' || query.trim() === '') {
      return fonts;
    }

    const normalizedQuery = removeVietnameseDiacritics(query);
    const rawQueryLower = query.toLowerCase().trim();

    return fonts.filter(font => {
      const name = font.name || font.family || '';
      const designer = font.designer || font.foundry_designer || '';
      const notes = font.director_notes || '';
      const category = font.category || font.core_section || '';
      const subcategory = font.subcategory || '';
      const mood = font.matrix_3d?.mood || font.matrix_mood || '';
      const driveFiles = Array.isArray(font.drive_files) ? font.drive_files.join(' ') : '';

      const normalizedName = removeVietnameseDiacritics(name);
      const normalizedDesigner = removeVietnameseDiacritics(designer);
      const normalizedNotes = removeVietnameseDiacritics(notes);
      const normalizedSubcat = removeVietnameseDiacritics(subcategory);
      const normalizedMood = removeVietnameseDiacritics(mood);
      const normalizedDrive = removeVietnameseDiacritics(driveFiles);

      // Support both diacritic-insensitive and raw substring matches
      return (
        normalizedName.includes(normalizedQuery) ||
        normalizedDesigner.includes(normalizedQuery) ||
        normalizedNotes.includes(normalizedQuery) ||
        normalizedSubcat.includes(normalizedQuery) ||
        normalizedMood.includes(normalizedQuery) ||
        normalizedDrive.includes(normalizedQuery) ||
        name.toLowerCase().includes(rawQueryLower) ||
        notes.toLowerCase().includes(rawQueryLower) ||
        mood.toLowerCase().includes(rawQueryLower)
      );
    });
  },

  multiFilter(fonts, criteria = {}) {
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
  }
};

/**
 * Drive Packaging & Link Specification
 * Derived from ORIGINAL_REQUEST.md § R3
 */
const DrivePackaging = {
  PARENT_FOLDER_ID: '1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao',
  TOTAL_FILES_TARGET: 1070,
  TOTAL_FAMILIES_TARGET: 361,

  isValidDriveUrl(url) {
    if (!url || typeof url !== 'string') return false;
    const regex = /^https:\/\/drive\.google\.com\/drive\/folders\/[A-Za-z0-9_-]+(\?usp=sharing)?$/;
    return regex.test(url);
  },

  buildDriveFolderUrl(folderId) {
    if (!folderId) return '';
    return `https://drive.google.com/drive/folders/${folderId}?usp=sharing`;
  }
};

/**
 * Path Resolver for progressive testability
 */
function resolveCatalog() {
  const rootCatalog = path.resolve(__dirname, '../../data/catalog.json');
  if (fs.existsSync(rootCatalog)) {
    try {
      const content = JSON.parse(fs.readFileSync(rootCatalog, 'utf8'));
      return { path: rootCatalog, source: 'data/catalog.json', data: content };
    } catch (e) {
      // ignore parse error, fallback
    }
  }

  // Fallback to Survey 1 master catalog
  const survey1Catalog = path.resolve(__dirname, '../../.agents/teamwork_preview_spec_miner_survey_1/fedu_font_catalog_master.json');
  if (fs.existsSync(survey1Catalog)) {
    const content = JSON.parse(fs.readFileSync(survey1Catalog, 'utf8'));
    return { path: survey1Catalog, source: 'survey1_fedu_font_catalog_master.json', data: content };
  }

  return null;
}

function resolveFamilyGrouping() {
  const survey2Mapping = path.resolve(__dirname, '../../.agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json');
  if (fs.existsSync(survey2Mapping)) {
    const content = JSON.parse(fs.readFileSync(survey2Mapping, 'utf8'));
    return { path: survey2Mapping, source: 'survey2_family_grouping_mapping.json', data: content };
  }

  const rootDriveLinks = path.resolve(__dirname, '../../data/drive_links.json');
  if (fs.existsSync(rootDriveLinks)) {
    const content = JSON.parse(fs.readFileSync(rootDriveLinks, 'utf8'));
    return { path: rootDriveLinks, source: 'data/drive_links.json', data: content };
  }

  return null;
}

module.exports = {
  VIETNAMESE_LOWERCASE,
  VIETNAMESE_UPPERCASE,
  COMPLEX_VIETNAMESE_WORDS,
  removeVietnameseDiacritics,
  matchesCategory,
  TypeTesterMetrics,
  SearchEngine,
  DrivePackaging,
  resolveCatalog,
  resolveFamilyGrouping
};
