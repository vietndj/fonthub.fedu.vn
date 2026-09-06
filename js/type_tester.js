/**
 * js/type_tester.js
 * Interactive FontFace Engine & Type Tester Controller
 * for fedu.vn/font Interactive Type Hub.
 *
 * Implements:
 * - Dynamic browser FontFace API loading & in-memory Promise cache deduplication
 * - Parametric boundary clamping matching tests/lib/engine.js (14-140px, 0.8-2.4, -0.05-0.30em)
 * - Diacritic-preserving text transformations (uppercase, lowercase, titlecase)
 * - Category system font fallback stacks (Serif, Sans Serif, Monospace, Script, Vintage)
 * - Complete 134 Vietnamese accented glyph map & modal controller
 * - IME composition handling for Vietnamese input methods (Telex/VNI)
 *
 * Zero external dependencies. Browser & Node.js isomorphic.
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.TypeTester = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // Complete 134 Vietnamese Accented Character Matrix (67 lowercase, 67 uppercase)
  var VIETNAMESE_LOWERCASE = [
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

  var VIETNAMESE_UPPERCASE = [
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

  var COMPLEX_VIETNAMESE_WORDS = [
    'nghiêng', 'khuyến', 'thưởng', 'truyền', 'hoằng',
    'quế', 'phượng', 'chuộng', 'nguyện', 'ngưỡng',
    'THƯỞNG', 'NGHIÊNG', 'KHUYẾN', 'TRUYỀN', 'ĐỒ HỌA'
  ];

  var PRESET_PHRASES = [
    {
      id: 'proclamation',
      label: 'Tiêu đề Quốc gia (All Caps)',
      text: 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM'
    },
    {
      id: 'pangram',
      label: 'Pangram Tiếng Việt (29 chữ cái)',
      text: 'Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ nguyên màu.'
    },
    {
      id: 'stacked',
      label: 'Kiểm tra dấu xếp tầng (Double Diacritics)',
      text: 'Thưởng thức vẻ đẹp huyền bí của chữ quốc ngữ qua từng con chữ uốn lượn sắc sảo.'
    },
    {
      id: 'headline',
      label: 'Display & Headline Tuyên ngôn',
      text: 'THỰC CHIẾN NGHỆ THUẬT CHỮ ĐỒ HỌA VIỆT NAM'
    },
    {
      id: 'cadence',
      label: 'Âm hưởng thanh điệu nhẹ nhàng',
      text: 'Hà Nội mùa thu lá vàng rơi lãng đãng bên hồ gươm phẳng lặng.'
    },
    {
      id: 'matrix',
      label: 'Bảng dấu nguyên âm toàn diện',
      text: 'ăằắẳẵặ âầấẩẫậ êềếểễệ ôồốổỗộ ơờớởỡợ ưừứửữự đĐ'
    },
    {
      id: 'numbers',
      label: 'Số & Ký tự tiền tệ',
      text: '0123456789 • 95.000.000 ₫ • §±€$¥'
    }
  ];

  /**
   * Metric Clamping Engine matching tests/lib/engine.js TypeTesterMetrics
   */
  var Metrics = {
    MIN_FONT_SIZE: 14,
    MAX_FONT_SIZE: 140,
    DEFAULT_FONT_SIZE: 36,

    MIN_LINE_HEIGHT: 0.8,
    MAX_LINE_HEIGHT: 2.4,
    DEFAULT_LINE_HEIGHT: 1.2,

    MIN_KERNING: -0.05,
    MAX_KERNING: 0.30,
    DEFAULT_KERNING: 0.0,

    clampFontSize: function (val) {
      var num = parseFloat(val);
      if (isNaN(num)) return this.DEFAULT_FONT_SIZE;
      return Math.max(this.MIN_FONT_SIZE, Math.min(this.MAX_FONT_SIZE, Math.round(num)));
    },

    clampLineHeight: function (val) {
      var num = parseFloat(val);
      if (isNaN(num)) return this.DEFAULT_LINE_HEIGHT;
      var clamped = Math.max(this.MIN_LINE_HEIGHT, Math.min(this.MAX_LINE_HEIGHT, num));
      return parseFloat(clamped.toFixed(2));
    },

    clampKerning: function (val) {
      var num = parseFloat(val);
      if (isNaN(num)) return this.DEFAULT_KERNING;
      var clamped = Math.max(this.MIN_KERNING, Math.min(this.MAX_KERNING, num));
      return parseFloat(clamped.toFixed(3));
    },

    applyTransform: function (text, transform) {
      if (!text || typeof text !== 'string') return '';
      switch (transform) {
        case 'uppercase':
          return text.toUpperCase();
        case 'lowercase':
          return text.toLowerCase();
        case 'titlecase':
        case 'capitalize':
          return text.replace(/\b(\w)/g, function (m) { return m.toUpperCase(); });
        default:
          return text;
      }
    },

    generateFontFaceCSS: function (family, webFontUrl, weight, style) {
      weight = weight || 'normal';
      style = style || 'normal';
      if (!family || !webFontUrl) return '';
      return '@font-face {\n  font-family: \'' + family + '\';\n  src: url(\'' + webFontUrl + '\') format(\'woff2\');\n  font-weight: ' + weight + ';\n  font-style: ' + style + ';\n  font-display: swap;\n}';
    },

    getFallbackStack: function (category) {
      if (!category) {
        return "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
      }
      var cat = category.toLowerCase();
      if (cat.includes('serif') && !cat.includes('sans')) {
        return "Georgia, Cambria, 'Times New Roman', Times, serif";
      }
      if (cat.includes('mono')) {
        return "'SF Mono', Monaco, 'Courier New', Courier, monospace";
      }
      if (cat.includes('script')) {
        return "'Brush Script MT', 'Apple Chancery', cursive";
      }
      if (cat.includes('vintage') || cat.includes('sài gòn') || cat.includes('oldstyle')) {
        return "Georgia, 'Palatino Linotype', Palatino, serif";
      }
      return "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    }
  };

  /**
   * TypeTesterEngine Class
   */
  function TypeTesterEngine(config) {
    this.config = Object.assign({
      defaultFontSize: Metrics.DEFAULT_FONT_SIZE,
      minFontSize: Metrics.MIN_FONT_SIZE,
      maxFontSize: Metrics.MAX_FONT_SIZE,
      defaultLineHeight: Metrics.DEFAULT_LINE_HEIGHT,
      minLineHeight: Metrics.MIN_LINE_HEIGHT,
      maxLineHeight: Metrics.MAX_LINE_HEIGHT,
      defaultKerning: Metrics.DEFAULT_KERNING,
      minKerning: Metrics.MIN_KERNING,
      maxKerning: Metrics.MAX_KERNING,
      defaultTheme: 'dark'
    }, config || {});

    // In-memory font cache & promise deduplication
    this.loadedFaces = new Map();
    this.loadingPromises = new Map();

    // Active state
    this.text = 'Cộng hòa Xã hội Chủ nghĩa Việt Nam';
    this.fontSize = this.config.defaultFontSize;
    this.lineHeight = this.config.defaultLineHeight;
    this.kerning = this.config.defaultKerning;
    this.textAlign = 'left';
    this.textTransform = 'none';
    this.currentTheme = this.config.defaultTheme;

    // Event hooks
    this.listeners = {
      fontLoading: [],
      fontLoaded: [],
      fontError: [],
      metricsChanged: []
    };
  }

  TypeTesterEngine.prototype.on = function (event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  };

  TypeTesterEngine.prototype.emit = function (event, data) {
    if (this.listeners[event]) {
      for (var i = 0; i < this.listeners[event].length; i++) {
        try {
          this.listeners[event][i](data);
        } catch (e) {
          console.error('[TypeTester] Event listener error:', e);
        }
      }
    }
  };

  TypeTesterEngine.prototype.clampFontSize = function (val) {
    return Metrics.clampFontSize(val);
  };

  TypeTesterEngine.prototype.clampLineHeight = function (val) {
    return Metrics.clampLineHeight(val);
  };

  TypeTesterEngine.prototype.clampKerning = function (val) {
    return Metrics.clampKerning(val);
  };

  TypeTesterEngine.prototype.applyTransform = function (text, transform) {
    return Metrics.applyTransform(text, transform);
  };

  TypeTesterEngine.prototype.getFallbackStack = function (category) {
    return Metrics.getFallbackStack(category);
  };

  TypeTesterEngine.prototype.generateFontFaceCSS = function (family, webFontUrl, weight, style) {
    return Metrics.generateFontFaceCSS(family, webFontUrl, weight, style);
  };

  TypeTesterEngine.prototype.getCacheKey = function (family, weight, style) {
    weight = weight || '400';
    style = style || 'normal';
    return String(family).trim() + '__' + weight + '__' + style;
  };

  /**
   * Dynamic Web Font Loader via browser FontFace API with deduplication cache.
   */
  TypeTesterEngine.prototype.loadWebFont = async function (family, webFontUrl, weight, style) {
    weight = weight || '400';
    style = style || 'normal';

    if (!family || !webFontUrl) {
      return null;
    }

    var cacheKey = this.getCacheKey(family, weight, style);

    // 1. Check in-memory cache
    if (this.loadedFaces.has(cacheKey)) {
      return this.loadedFaces.get(cacheKey);
    }

    // 2. Check in-flight promise deduplication
    if (this.loadingPromises.has(cacheKey)) {
      return await this.loadingPromises.get(cacheKey);
    }

    // 3. Check browser FontFaceSet
    if (typeof document !== 'undefined' && document.fonts && document.fonts.check) {
      try {
        var isAvailable = document.fonts.check(weight + ' 16px \'' + family + '\'');
        if (isAvailable) {
          var registeredFace = { family: family, weight: weight, style: style, status: 'loaded' };
          this.loadedFaces.set(cacheKey, registeredFace);
          return registeredFace;
        }
      } catch (e) {
        // ignore check failure, proceed to load
      }
    }

    this.emit('fontLoading', { family: family, weight: weight, style: style });

    var self = this;
    var loadPromise = (async function () {
      try {
        if (typeof FontFace === 'undefined' || typeof document === 'undefined') {
          // Headless / Node.js test environment mock
          var mockFace = { family: family, weight: weight, style: style, status: 'loaded' };
          self.loadedFaces.set(cacheKey, mockFace);
          return mockFace;
        }

        var fontFace = new FontFace(
          family,
          'url(\'' + webFontUrl + '\') format(\'woff2\')',
          {
            weight: String(weight),
            style: style,
            display: 'swap'
          }
        );

        document.fonts.add(fontFace);
        var loadedFace = await fontFace.load();
        self.loadedFaces.set(cacheKey, loadedFace);
        self.emit('fontLoaded', { family: family, weight: weight, style: style, fontFace: loadedFace });
        return loadedFace;
      } catch (err) {
        console.warn('[TypeTester] Failed to load web font ' + family + ' (' + webFontUrl + '):', err);
        self.emit('fontError', { family: family, weight: weight, style: style, error: err });
        throw err;
      } finally {
        self.loadingPromises.delete(cacheKey);
      }
    })();

    this.loadingPromises.set(cacheKey, loadPromise);
    return await loadPromise;
  };

  /**
   * Sets up IME composition protection on an input element to prevent vowel glitching.
   */
  TypeTesterEngine.prototype.bindIMEInput = function (inputElement, onCommit) {
    if (!inputElement) return;
    var isComposing = false;

    inputElement.addEventListener('compositionstart', function () {
      isComposing = true;
    });

    inputElement.addEventListener('compositionend', function (e) {
      isComposing = false;
      if (typeof onCommit === 'function') {
        onCommit(e.target.value);
      }
    });

    inputElement.addEventListener('input', function (e) {
      if (!isComposing && typeof onCommit === 'function') {
        onCommit(e.target.value);
      }
    });
  };

  /**
   * Returns curated preset phrases for testing.
   */
  TypeTesterEngine.prototype.getPresetPhrases = function () {
    return PRESET_PHRASES;
  };

  /**
   * Returns categorized Vietnamese glyphs.
   */
  TypeTesterEngine.prototype.getVietnameseGlyphs = function () {
    return [
      { group: 'A', chars: ['à', 'á', 'ả', 'ã', 'ạ', 'À', 'Á', 'Ả', 'Ã', 'Ạ'] },
      { group: 'Ă', chars: ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'Ă', 'Ằ', 'Ắ', 'Ẳ', 'Ẵ', 'Ặ'] },
      { group: 'Â', chars: ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'Â', 'Ầ', 'Ấ', 'Ẩ', 'Ẫ', 'Ậ'] },
      { group: 'E', chars: ['è', 'é', 'ẻ', 'ẽ', 'ẹ', 'È', 'É', 'Ẻ', 'Ẽ', 'Ẹ'] },
      { group: 'Ê', chars: ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'Ê', 'Ề', 'Ế', 'Ể', 'Ễ', 'Ệ'] },
      { group: 'I', chars: ['ì', 'í', 'ỉ', 'ĩ', 'ị', 'Ì', 'Í', 'Ỉ', 'Ĩ', 'Ị'] },
      { group: 'O', chars: ['ò', 'ó', 'ỏ', 'õ', 'ọ', 'Ò', 'Ó', 'Ỏ', 'Õ', 'Ọ'] },
      { group: 'Ô', chars: ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'Ô', 'Ồ', 'Ố', 'Ổ', 'Ỗ', 'Ộ'] },
      { group: 'Ơ', chars: ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'Ơ', 'Ờ', 'Ớ', 'Ở', 'Ỡ', 'Ợ'] },
      { group: 'U', chars: ['ù', 'ú', 'ủ', 'ũ', 'ụ', 'Ù', 'Ú', 'Ủ', 'Ũ', 'Ụ'] },
      { group: 'Ư', chars: ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'Ư', 'Ừ', 'Ứ', 'Ử', 'Ữ', 'Ự'] },
      { group: 'Y', chars: ['ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'Ỳ', 'Ý', 'Ỷ', 'Ỹ', 'Ỵ'] },
      { group: 'Đ', chars: ['đ', 'Đ'] }
    ];
  };

  TypeTesterEngine.prototype.getComplexWords = function () {
    return COMPLEX_VIETNAMESE_WORDS;
  };

  /**
   * Renders the interactive 134-glyph grid inside container.
   */
  TypeTesterEngine.prototype.renderGlyphMap = function (container, font, onSelectGlyph) {
    if (!container) return;
    container.innerHTML = '';

    var family = font ? (font.name || font.family) : 'sans-serif';
    var glyphGroups = this.getVietnameseGlyphs();

    glyphGroups.forEach(function (groupData) {
      var section = document.createElement('div');
      section.className = 'glyph-group';

      var title = document.createElement('div');
      title.className = 'glyph-group-title';
      title.textContent = 'Nhóm ' + groupData.group + ' (' + groupData.chars.length + ' ký tự)';
      section.appendChild(title);

      var grid = document.createElement('div');
      grid.className = 'glyph-grid';

      groupData.chars.forEach(function (char) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'glyph-cell';
        btn.style.fontFamily = '\'' + family + '\', sans-serif';
        btn.textContent = char;
        var codeHex = char.charCodeAt(0).toString(16).toUpperCase();
        while (codeHex.length < 4) codeHex = '0' + codeHex;
        btn.title = char + ' (U+' + codeHex + ') — Nhấp để copy';

        btn.addEventListener('click', function () {
          if (typeof onSelectGlyph === 'function') {
            onSelectGlyph(char, codeHex);
          }
        });

        grid.appendChild(btn);
      });

      section.appendChild(grid);
      container.appendChild(section);
    });
  };

  // Expose module APIs
  return {
    TypeTesterEngine: TypeTesterEngine,
    Metrics: Metrics,
    TypeTesterMetrics: Metrics,
    VIETNAMESE_LOWERCASE: VIETNAMESE_LOWERCASE,
    VIETNAMESE_UPPERCASE: VIETNAMESE_UPPERCASE,
    COMPLEX_VIETNAMESE_WORDS: COMPLEX_VIETNAMESE_WORDS,
    PRESET_PHRASES: PRESET_PHRASES
  };
});
