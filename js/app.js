/**
 * js/app.js
 * Master Application Controller & Progressive Rendering Engine
 * for fedu.vn/font Interactive Type Hub.
 *
 * Coordinates:
 * - CatalogLoader: asynchronous catalog loading, sub-4ms instant search, faceted filter
 * - TypeTesterEngine: dynamic FontFace loading, metric clamping, IME composition, 134-glyph modal
 * - Tri-Theme Switcher: Dark (#121212), Light (#FFFFFF), Neon (#0D0E15 / #00FF66)
 * - Progressive Infinite Scroll: IntersectionObserver batching (24 cards per page)
 * - Single-Variable Batching: CSS custom properties updates for 60 FPS slider interactivity
 */

(function () {
  'use strict';

  // Application State
  var App = {
    catalog: null,
    allFonts: [],
    indexedFonts: [],
    filteredFonts: [],
    typeTester: null,

    activeFilters: {
      searchQuery: '',
      category: 'all',
      studio: 'all',
      mood: 'all',
      use_case: 'all',
      weight: 'all',
      vietnamese_support: true
    },

    pagination: {
      currentPage: 1,
      pageSize: 24,
      totalCount: 0
    },

    activeModalFont: null,
    activeGlyphTab: 'all-vn',
    intersectionObserver: null,
    fontLoadObserver: null,

    // Multi-View Architecture
    currentView: 'catalog',
    fontshareSearchQuery: '',
    fontshareState: {
      size: 210,
      text: '',
      preset: 'names',
      align: 'left',
      viewMode: 'list',
      category: 'all',
      studio: 'all',
      property: 'all',
      personality: 'all',
      pill: 'all',
      sort: 'popular'
    },
    fontsharePagination: {
      pool: [],
      renderedCount: 0,
      batchSize: 30,
      isLoading: false
    },
    fontshareObserver: null,
    pairState: {
      headingFont: null,
      bodyFont: null,
      headingSize: 54,
      bodySize: 17,
      lineHeight: 1.55,
      kerning: 0.00
    }
  };

  // DOM Cache
  var DOM = {};

  function cacheDOM() {
    DOM.html = document.documentElement;
    DOM.headerStatsBadge = document.getElementById('header-stats-badge');
    DOM.themeBtns = document.querySelectorAll('[data-theme-set]');

    // Multi-View controls
    DOM.viewBtns = document.querySelectorAll('[data-view]');
    DOM.catalogView = document.getElementById('catalog-view');
    DOM.fontshareView = document.getElementById('fontshare-view');
    DOM.pairView = document.getElementById('pair-view');

    // Fontshare View controls (Image 4)
    DOM.fontshareSearch = document.getElementById('fontshare-search');
    DOM.fontshareGrid = document.getElementById('fontshare-grid');
    DOM.fontshareShuffleBtn = document.getElementById('fontshare-shuffle-btn');
    DOM.fsFontsCount = document.getElementById('fs-fonts-count');
    DOM.fsTotalCount = document.getElementById('fs-total-count');
    DOM.fsFilterCategory = document.getElementById('fs-filter-category');
    DOM.fsFilterProperty = document.getElementById('fs-filter-property');
    DOM.fsFilterPersonality = document.getElementById('fs-filter-personality');
    DOM.fsSizeSlider = document.getElementById('fs-size-slider');
    DOM.fsSizeReadout = document.getElementById('fs-size-readout');
    DOM.fsCustomTextInput = document.getElementById('fs-custom-text-input');
    DOM.fsPresetBtns = document.querySelectorAll('.fs-preset-btn');
    DOM.fsAlignBtns = document.querySelectorAll('.fs-align-btn');
    DOM.fsThemeToggle = document.getElementById('fs-theme-toggle');
    DOM.fsResetBtn = document.getElementById('fs-reset-btn');
    DOM.fsViewModeBtns = document.querySelectorAll('.fs-view-mode-btn');
    DOM.fsPillBtns = document.querySelectorAll('.fs-pill-btn');
    DOM.fsSortBtns = document.querySelectorAll('.fs-sort-btn');
    DOM.fsScrollTopBtn = document.getElementById('fs-scroll-top-btn');
    DOM.fontshareSentinel = document.getElementById('fontshare-scroll-sentinel');
    DOM.fontshareEndMessage = document.getElementById('fontshare-end-message');
    DOM.fsEndCount = document.getElementById('fs-end-count');
    DOM.fsTabFonts = document.getElementById('fs-tab-fonts');
    DOM.fsTabPairs = document.getElementById('fs-tab-pairs');
    DOM.fsTabLicenses = document.getElementById('fs-tab-licenses');

    // Pair View controls
    DOM.pairHeadingSelect = document.getElementById('pair-heading-select');
    DOM.pairBodySelect = document.getElementById('pair-body-select');
    DOM.pairSwapBtn = document.getElementById('pair-swap-btn');
    DOM.pairRandomBtn = document.getElementById('pair-random-btn');
    DOM.pairDownloadBothBtn = document.getElementById('pair-download-both-btn');
    DOM.pairHeadingSize = document.getElementById('pair-heading-size');
    DOM.pairHeadingSizeVal = document.getElementById('pair-heading-size-val');
    DOM.pairBodySize = document.getElementById('pair-body-size');
    DOM.pairBodySizeVal = document.getElementById('pair-body-size-val');
    DOM.pairLineHeight = document.getElementById('pair-line-height');
    DOM.pairLineHeightVal = document.getElementById('pair-line-height-val');
    DOM.pairKerning = document.getElementById('pair-kerning');
    DOM.pairKerningVal = document.getElementById('pair-kerning-val');
    DOM.pairPreviewHeading = document.getElementById('pair-preview-heading');
    DOM.pairPreviewSubhead = document.getElementById('pair-preview-subhead');
    DOM.pairPreviewBody = document.getElementById('pair-preview-body');
    DOM.pairingAccordion = document.getElementById('pairing-accordion');
    DOM.pairingAccordionContent = document.getElementById('pairing-accordion-content');
    DOM.curatedPairsGrid = document.getElementById('curated-pairs-grid');

    // Type Tester Toolbar
    DOM.globalTextInput = document.getElementById('global-text-input');
    DOM.textClearBtn = document.getElementById('text-clear-btn');
    DOM.presetSelect = document.getElementById('preset-select');
    DOM.fontSizeSlider = document.getElementById('font-size-slider');
    DOM.fontSizeVal = document.getElementById('font-size-val');
    DOM.lineHeightSlider = document.getElementById('line-height-slider');
    DOM.lineHeightVal = document.getElementById('line-height-val');
    DOM.kerningSlider = document.getElementById('kerning-slider');
    DOM.kerningVal = document.getElementById('kerning-val');
    DOM.alignBtns = document.querySelectorAll('[data-align]');
    DOM.transformBtns = document.querySelectorAll('[data-transform]');
    DOM.btnResetTester = document.getElementById('btn-reset-tester');

    // Search & Filter
    DOM.searchInput = document.getElementById('search-input');
    DOM.searchLatency = document.getElementById('search-latency');
    DOM.resultsCount = document.getElementById('results-count');
    DOM.categoryChips = document.querySelectorAll('[data-category]');
    DOM.filterStudio = document.getElementById('filter-studio');
    DOM.fsFilterStudio = document.getElementById('fs-filter-studio');
    DOM.filterMood = document.getElementById('filter-mood');
    DOM.filterUseCase = document.getElementById('filter-use-case');
    DOM.filterWeight = document.getElementById('filter-weight');
    DOM.filterVnSupport = document.getElementById('filter-vn-support');
    DOM.btnClearFilters = document.getElementById('btn-clear-filters');

    // Counts
    DOM.countAll = document.getElementById('count-all');
    DOM.countSans = document.getElementById('count-sans');
    DOM.countSerif = document.getElementById('count-serif');
    DOM.countVintage = document.getElementById('count-vintage');
    DOM.countMonoScript = document.getElementById('count-mono-script');
    DOM.countGt = document.getElementById('count-gt');
    DOM.countCotype = document.getElementById('count-cotype');
    DOM.countDinamo = document.getElementById('count-dinamo');
    DOM.countKlim = document.getElementById('count-klim');
    DOM.countPangram = document.getElementById('count-pangram');
    DOM.countFav = document.getElementById('count-fav');
    DOM.chipFavorites = document.getElementById('chip-favorites');

    // Grid & Empty State
    DOM.fontGrid = document.getElementById('font-grid');
    DOM.emptyState = document.getElementById('empty-state');
    DOM.emptyResetBtn = document.getElementById('empty-reset-btn');
    DOM.scrollSentinel = document.getElementById('scroll-sentinel');

    // Modal
    DOM.glyphModal = document.getElementById('glyph-modal');
    DOM.glyphModalClose = document.getElementById('glyph-modal-close');
    DOM.glyphModalTitle = document.getElementById('glyph-modal-title');
    DOM.glyphModalSubtitle = document.getElementById('glyph-modal-subtitle');
    DOM.glyphModalTabs = document.querySelectorAll('[data-glyph-tab]');
    DOM.glyphModalBody = document.getElementById('glyph-modal-body');

    // Toast
    DOM.toastNotice = document.getElementById('toast-notice');
  }

  /**
   * Helper to escape HTML characters.
   */
  function escapeHTML(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * Shows a brief toast notification.
   */
  function showToast(message) {
    if (!DOM.toastNotice) return;
    DOM.toastNotice.textContent = message;
    DOM.toastNotice.classList.add('show');
    clearTimeout(DOM.toastTimeout);
    DOM.toastTimeout = setTimeout(function () {
      DOM.toastNotice.classList.remove('show');
    }, 2200);
  }

  /**
   * Applies Type Tester batching custom properties to the document root element.
   * Updates all cards synchronously at 60 FPS without layout thrashing.
   */
  function setFontSize(val) {
    var clamped = App.typeTester.clampFontSize(val);
    DOM.html.style.setProperty('--tester-font-size', clamped + 'px');
    if (DOM.fontSizeVal) DOM.fontSizeVal.textContent = clamped + 'px';
    if (DOM.fontSizeSlider) DOM.fontSizeSlider.value = clamped;

    // Synchronize all card size sliders smoothly
    if (DOM.fontGrid) {
      DOM.fontGrid.querySelectorAll('.card-size-slider').forEach(function (slider) {
        slider.value = clamped;
        var card = slider.closest('.font-card');
        var valDisplay = card ? card.querySelector('.card-size-val') : null;
        if (valDisplay) valDisplay.textContent = clamped + 'px';
      });
      DOM.fontGrid.querySelectorAll('.preview-text').forEach(function (p) {
        p.style.fontSize = '';
      });
    }
  }

  function setLineHeight(val) {
    var clamped = App.typeTester.clampLineHeight(val);
    DOM.html.style.setProperty('--tester-line-height', clamped);
    if (DOM.lineHeightVal) DOM.lineHeightVal.textContent = clamped.toFixed(2);
    if (DOM.lineHeightSlider) DOM.lineHeightSlider.value = clamped;
  }

  function setKerning(val) {
    var clamped = App.typeTester.clampKerning(val);
    DOM.html.style.setProperty('--tester-letter-spacing', clamped + 'em');
    if (DOM.kerningVal) DOM.kerningVal.textContent = (clamped >= 0 ? '+' : '') + clamped.toFixed(2) + 'em';
    if (DOM.kerningSlider) DOM.kerningSlider.value = clamped;
  }

  function setTextAlign(align) {
    align = align || 'left';
    DOM.html.style.setProperty('--tester-text-align', align);
    DOM.alignBtns.forEach(function (btn) {
      if (btn.getAttribute('data-align') === align) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  function setTextTransform(transform) {
    transform = transform || 'none';
    DOM.html.style.setProperty('--tester-text-transform', transform);
    DOM.transformBtns.forEach(function (btn) {
      if (btn.getAttribute('data-transform') === transform) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  /**
   * Updates global specimen preview text across all cards and waterfall rows.
   */
  function broadcastPreviewText(text) {
    var cleanText = text !== undefined ? String(text) : '';
    App.typeTester.text = cleanText;

    var previewElements = DOM.fontGrid ? DOM.fontGrid.querySelectorAll('.preview-text, .waterfall-sample-text') : [];
    previewElements.forEach(function (el) {
      if (cleanText.trim() === '') {
        var fallbackText = el.getAttribute('data-sample') || el.getAttribute('data-family') || 'Tiếng Việt';
        el.textContent = fallbackText;
      } else {
        el.textContent = cleanText;
      }
    });
  }

  /**
   * Resets Type Tester controls to default settings.
   */
  function resetTypeTester() {
    setFontSize(36);
    setLineHeight(1.20);
    setKerning(0.00);
    setTextAlign('left');
    setTextTransform('none');

    var defaultText = 'Cộng hòa Xã hội Chủ nghĩa Việt Nam';
    if (DOM.globalTextInput) DOM.globalTextInput.value = defaultText;
    if (DOM.presetSelect) DOM.presetSelect.value = '';
    broadcastPreviewText(defaultText);

    // Reset card weight sliders to 400 and close open waterfalls
    if (DOM.fontGrid) {
      DOM.fontGrid.querySelectorAll('.card-weight-slider').forEach(function (ws) {
        ws.value = 400;
        var card = ws.closest('.font-card');
        if (card) {
          var wv = card.querySelector('.card-weight-val');
          if (wv) wv.textContent = '400';
          var wf = card.querySelector('.card-waterfall-drawer');
          if (wf) wf.style.display = 'none';
          var btn = card.querySelector('.card-styles-toggle');
          if (btn) {
            btn.classList.remove('is-open');
            btn.setAttribute('aria-expanded', 'false');
          }
          card.classList.remove('is-waterfall-open');
        }
      });
    }

    showToast('Đã đặt lại Type Tester về mặc định');
  }

  /**
   * Swaps themes (Dark, Light, Neon).
   */
  function setTheme(theme) {
    DOM.html.setAttribute('data-theme', theme);
    DOM.themeBtns.forEach(function (btn) {
      if (btn.getAttribute('data-theme-set') === theme) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    try {
      localStorage.setItem('fedu_font_theme', theme);
    } catch (e) {}
  }

  /**
   * Favorites Storage Helper
   */
  function getFavorites() {
    try {
      var favs = localStorage.getItem('fedu_font_favorites') || localStorage.getItem('fonthub_favorites');
      return favs ? JSON.parse(favs) : [];
    } catch (e) {
      return [];
    }
  }

  function isFontFavorite(fontId) {
    var favs = getFavorites();
    return favs.indexOf(fontId) !== -1;
  }

  function toggleFontFavorite(fontId) {
    try {
      var favs = getFavorites();
      var idx = favs.indexOf(fontId);
      var isFav = false;
      if (idx === -1) {
        favs.push(fontId);
        isFav = true;
      } else {
        favs.splice(idx, 1);
        isFav = false;
      }
      localStorage.setItem('fedu_font_favorites', JSON.stringify(favs));
      localStorage.setItem('fonthub_favorites', JSON.stringify(favs));
      updateFacetCountBadges();
      if (App.activeFilters && App.activeFilters.category === 'favorites') {
        applyFilters();
      }
      return isFav;
    } catch (e) {
      return false;
    }
  }

  // In-memory dynamic font face cache to avoid duplicate network fetches
  var loadedDynamicFaces = new Set();
  var dynamicFacePromises = new Map();

  function loadVariantFontFace(fontObj, resolved, previewElement) {
    if (!resolved || !resolved.matchedFilename || typeof FontFace === 'undefined' || typeof document === 'undefined') {
      return Promise.resolve(null);
    }

    var fontUrl = 'fonts/' + resolved.matchedFilename;
    var ext = resolved.matchedFilename.split('.').pop().toLowerCase();
    var formatSpec = ext === 'woff2' ? " format('woff2')" : (ext === 'otf' ? " format('opentype')" : " format('truetype')");
    var fontSource = 'url("' + fontUrl + '")' + formatSpec;

    var family = (fontObj && (fontObj.family || fontObj.name)) || 'sans-serif';
    var specificFamily = resolved.specificFamily || resolved.matchedFilename.replace(/\.[^.]+$/, '');

    var cacheKey = resolved.matchedFilename + '__' + resolved.fontWeight + '__' + resolved.fontStyle;
    if (loadedDynamicFaces.has(cacheKey)) {
      return Promise.resolve(null);
    }
    if (dynamicFacePromises.has(cacheKey)) {
      return dynamicFacePromises.get(cacheKey);
    }

    var familiesToRegister = new Set([family, specificFamily]);
    if (family.startsWith('GR ')) {
      familiesToRegister.add(family.replace(/^GR /, 'GT '));
      familiesToRegister.add(family.replace(/\s+/g, ''));
    } else if (family.startsWith('GT ')) {
      familiesToRegister.add(family.replace(/^GT /, 'GR '));
      familiesToRegister.add(family.replace(/\s+/g, ''));
    }
    if (fontObj && fontObj.name) {
      familiesToRegister.add(fontObj.name);
      familiesToRegister.add(fontObj.name.replace(/\s+/g, ''));
    }

    var loadPromise = (async function () {
      try {
        var promises = [];
        familiesToRegister.forEach(function (famName) {
          try {
            var face = new FontFace(famName, fontSource, {
              weight: String(resolved.fontWeight || '400'),
              style: resolved.fontStyle || 'normal',
              display: 'swap'
            });
            document.fonts.add(face);
            promises.push(face.load());
          } catch (e) {}
        });

        await Promise.all(promises);
        loadedDynamicFaces.add(cacheKey);

        if (previewElement) {
          previewElement.style.fontFamily = resolved.fontFamily;
          previewElement.style.fontWeight = resolved.fontWeight;
          previewElement.style.fontStyle = resolved.fontStyle;
        }
      } catch (err) {
        console.warn('[FontHub] Failed dynamic font load for ' + resolved.matchedFilename + ':', err);
      } finally {
        dynamicFacePromises.delete(cacheKey);
      }
    })();

    dynamicFacePromises.set(cacheKey, loadPromise);
    return loadPromise;
  }

  /**
   * Resolves a human-readable font variant (e.g. 'Light', 'Book', 'BoldItalic', 'ExtraBold')
   * into valid CSS font-weight, font-style, and family fallbacks matching OS & webfont files.
   */
  function resolveVariantStyle(family, variantStr, category, files) {
    var raw = String(variantStr || 'Regular').trim();
    var lower = raw.toLowerCase().replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();

    // 1. Determine fontStyle (italic vs normal)
    var isItalic = lower.includes('italic') || lower.includes('oblique') || lower.includes('slant');
    var fontStyle = isItalic ? 'italic' : 'normal';

    // Base token without italic for weight matching
    var baseToken = lower.replace(/\b(italic|oblique|slant)\b/g, '').trim();

    // 2. Numeric weight lookup
    var fontWeight = '400';
    if (/\b(thin|hairline|100|air)\b/.test(baseToken)) {
      fontWeight = '100';
    } else if (/\b(ultralight|extra light|ultra light|extralight|200)\b/.test(baseToken)) {
      fontWeight = '200';
    } else if (/\b(light|300)\b/.test(baseToken)) {
      fontWeight = '300';
    } else if (/\b(medium|500)\b/.test(baseToken)) {
      fontWeight = '500';
    } else if (/\b(semibold|semi bold|demibold|demi bold|600)\b/.test(baseToken)) {
      fontWeight = '600';
    } else if (/\b(ultrabold|ultra bold|extrabold|extra bold|super|heavy|800)\b/.test(baseToken)) {
      fontWeight = '800';
    } else if (/\b(black|poster|ultra|900)\b/.test(baseToken)) {
      fontWeight = '900';
    } else if (/\b(bold|700)\b/.test(baseToken)) {
      fontWeight = '700';
    } else if (/\b(book|regular|normal|roman|400)\b/.test(baseToken) || baseToken === '') {
      fontWeight = '400';
    }

    // 3. Fallback stack
    var fallbackStack = App.typeTester ? App.typeTester.getFallbackStack(category) : 'sans-serif';

    // 4. Match file in files array with high accuracy
    var matchedFile = null;
    if (Array.isArray(files) && files.length > 0) {
      var bestScore = -1;
      for (var i = 0; i < files.length; i++) {
        var f = files[i];
        if (!f || !f.filename) continue;
        var fStyle = String(f.style || '').toLowerCase().replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();
        var fName = String(f.filename || '').toLowerCase();
        var fItalic = Boolean(f.is_italic) || fStyle.includes('italic') || fName.includes('italic');

        var score = 0;
        // Prefer clean non-double extension files
        if (!f.filename.includes('.ttf.ttf') && !f.filename.includes('.otf.otf')) {
          score += 20;
        }

        // Exact style match
        if (fStyle === lower) {
          score += 100;
        } else if (fStyle.replace(/\s+/g, '') === lower.replace(/\s+/g, '')) {
          score += 90;
        }

        // Exact weight match
        var fW = parseInt(f.weight, 10);
        if (fW && String(fW) === fontWeight) {
          score += 30;
        }

        // Italic match
        if (fItalic === isItalic) {
          score += 20;
        } else {
          score -= 50;
        }

        // Disambiguate light vs ultralight
        if (baseToken === 'light' && (fStyle.includes('ultra') || fStyle.includes('extra') || fName.includes('ultra') || fName.includes('extra'))) {
          score -= 60;
        }
        // Disambiguate bold vs ultrabold/semibold
        if (baseToken === 'bold' && (fStyle.includes('ultra') || fStyle.includes('extra') || fStyle.includes('semi') || fName.includes('ultra') || fName.includes('extra') || fName.includes('semi'))) {
          score -= 60;
        }
        // Disambiguate regular vs book
        if (baseToken === 'regular' && (fStyle.includes('book') && !lower.includes('book'))) {
          score -= 10;
        }
        if (baseToken === 'book' && fStyle.includes('book')) {
          score += 40;
        }

        if (score > bestScore) {
          bestScore = score;
          matchedFile = f;
        }
      }
    }

    if (matchedFile) {
      if (matchedFile.weight && parseInt(matchedFile.weight, 10) > 0) {
        var mw = parseInt(matchedFile.weight, 10);
        if (baseToken.includes('ultrabold') && mw === 400) {
          fontWeight = '800';
        } else {
          fontWeight = String(mw);
        }
      }
    }

    var cleanFamily = family.replace(/['"]/g, '').trim();
    var cleanStyle = raw.replace(/[_-]/g, ' ').trim();
    var hyphenStyle = raw.replace(/\s+/g, '-').trim();

    var specificFamily = matchedFile ? matchedFile.filename.replace(/\.(woff2|otf|ttf)$/i, '') : '';

    var candidates = [];
    if (specificFamily) {
      candidates.push("'" + specificFamily + "'");
    }
    candidates.push("'" + cleanFamily + "'");
    candidates.push("'" + cleanFamily.replace(/\s+/g, '') + "'");

    // Add GT/GR aliases
    if (cleanFamily.startsWith('GR ')) {
      candidates.push("'" + cleanFamily.replace(/^GR /, 'GT ') + "'");
      candidates.push("'" + cleanFamily.replace(/^GR /, 'GT ').replace(/\s+/g, '') + "'");
    } else if (cleanFamily.startsWith('GT ')) {
      candidates.push("'" + cleanFamily.replace(/^GT /, 'GR ') + "'");
      candidates.push("'" + cleanFamily.replace(/^GT /, 'GR ').replace(/\s+/g, '') + "'");
    }

    candidates.push("'" + cleanFamily + " " + cleanStyle + "'");
    candidates.push("'" + cleanFamily + "-" + hyphenStyle + "'");

    var combinedFamily = candidates.join(', ') + ', ' + fallbackStack;

    return {
      rawVariant: raw,
      fontWeight: fontWeight,
      fontStyle: fontStyle,
      fontFamily: combinedFamily,
      matchedFilename: matchedFile ? matchedFile.filename : null,
      specificFamily: specificFamily
    };
  }

  /**
   * Builds the HTML string for an individual font card.
   */
  function createFontCardHTML(font) {
    var weights = Array.isArray(font.weights) ? font.weights : ['Regular'];
    var weightsCount = weights.length;
    var weightsLabel = weightsCount > 1 ? weightsCount + ' styles' : '1 style';

    var currentText = (DOM.globalTextInput && DOM.globalTextInput.value.trim())
      ? DOM.globalTextInput.value
      : (font.sample_text || font.name || 'Cộng hòa Xã hội Chủ nghĩa Việt Nam');

    var styleBadge = font.matrix_3d && font.matrix_3d.style
      ? '<span class="badge badge-style">' + escapeHTML(font.matrix_3d.style) + '</span>' : '';
    var moodBadge = font.matrix_3d && font.matrix_3d.mood
      ? '<span class="badge badge-mood">' + escapeHTML(font.matrix_3d.mood) + '</span>' : '';
    var useBadge = font.matrix_3d && font.matrix_3d.use_case
      ? '<span class="badge badge-use">' + escapeHTML(font.matrix_3d.use_case) + '</span>' : '';

    var vnBadge = font.vietnamese_support
      ? '<span class="badge badge-vn" title="Hỗ trợ đầy đủ Tiếng Việt có dấu">VN Ready</span>'
      : '<span class="badge" style="opacity: 0.6;">Basic Latin</span>';

    var isGT = (typeof CatalogLoader !== 'undefined' && CatalogLoader.isGTFont)
      ? CatalogLoader.isGTFont(font)
      : (Boolean(font.is_gt) || (Array.isArray(font.tags) && font.tags.indexOf('GT Font') !== -1));

    var gtBadge = isGT
      ? '<button type="button" class="badge badge-gt" data-category="GT Font" title="Lọc phông chữ GR Font (FEDU)">GT Font</button>'
      : '';

    var isCoType = (typeof CatalogLoader !== 'undefined' && CatalogLoader.isCoTypeFont)
      ? CatalogLoader.isCoTypeFont(font)
      : (Boolean(font.is_cotype) || (Array.isArray(font.tags) && font.tags.indexOf('CoType') !== -1));

    var cotypeBadge = isCoType
      ? '<button type="button" class="badge badge-cotype" data-category="CoType" title="Lọc phông chữ CoType Foundry (FEDU)">CoType</button>'
      : '';

    var isDinamo = (typeof CatalogLoader !== 'undefined' && CatalogLoader.isDinamoFont)
      ? CatalogLoader.isDinamoFont(font)
      : (Boolean(font.is_dinamo) || (Array.isArray(font.tags) && font.tags.indexOf('Dinamo') !== -1));

    var dinamoBadge = isDinamo
      ? '<button type="button" class="badge badge-dinamo" data-category="Dinamo" title="Lọc phông chữ Dinamo Typefaces (FEDU)">Dinamo</button>'
      : '';

    var isKlim = (typeof CatalogLoader !== 'undefined' && CatalogLoader.isKlimFont)
      ? CatalogLoader.isKlimFont(font)
      : (Boolean(font.is_klim) || (Array.isArray(font.tags) && font.tags.indexOf('Klim') !== -1));

    var klimBadge = isKlim
      ? '<button type="button" class="badge badge-klim" data-category="Klim" title="Lọc phông chữ Klim Type Foundry (FEDU)">Klim</button>'
      : '';

    var isPangram = (typeof CatalogLoader !== 'undefined' && CatalogLoader.isPangramFont)
      ? CatalogLoader.isPangramFont(font)
      : (Boolean(font.is_pangram) || (Array.isArray(font.tags) && font.tags.indexOf('Pangram') !== -1));

    var pangramBadge = isPangram
      ? '<button type="button" class="badge badge-pangram" data-category="Pangram" title="Lọc phông chữ Pangram Pangram (FEDU)">Pangram</button>'
      : '';

    var studioName = font.studio || font.foundry || (isGT ? 'Grilli Type' : (isCoType ? 'CoType Foundry' : (isDinamo ? 'Dinamo' : (isKlim ? 'Klim Type Foundry' : (isPangram ? 'Pangram Pangram' : 'FEDU Type Studio')))));
    var studioBadge = '<button type="button" class="badge badge-studio" data-studio="' + escapeHTML(studioName) + '" title="Gom nhóm các font thuộc studio ' + escapeHTML(studioName) + '">🏢 ' + escapeHTML(studioName) + '</button>';

    var anatomy = font.anatomy || {};
    var contrast = anatomy.contrast || 'Medium';
    var axis = anatomy.axis || 'Vertical';
    var xHeight = anatomy.x_height || 'Medium';
    var aperture = anatomy.aperture || 'Balanced';

    var directorNotes = font.director_notes || 'Kiểu chữ tinh tế, cân bằng thị giác hoàn hảo.';
    var originBadge = '';
    var critiqueText = directorNotes;
    if (directorNotes.indexOf('📌 Nguồn gốc:') !== -1) {
      var noteParts = directorNotes.split('\n\n');
      originBadge = noteParts[0].trim();
      critiqueText = noteParts.slice(1).join('\n\n').trim();
    }

    var isGRFont = isGT || (font.id && font.id.startsWith('gr-'));
    var defaultDriveFolder = isGRFont
      ? 'https://drive.google.com/drive/folders/1aT81y72_QzEGJjEFWSEjC11iLLXdwkpO?usp=sharing'
      : 'https://drive.google.com/drive/folders/1mEkkjojZUZzBQYmcXnJoFIWM4QBc7u90?usp=sharing';
    var driveViewUrl = font.drive_view_url || font.drive_url || font.drive_link || defaultDriveFolder;
    var driveDownloadUrl = font.drive_download_url || font.download_url || font.zip_url || driveViewUrl;
    var downloadHref = driveDownloadUrl;
    var downloadTooltip = 'Tải trọn bộ ' + escapeHTML(font.name) + ' (' + weightsCount + ' styles)';

    var category = font.category || (font.matrix_3d && font.matrix_3d.style) || 'Sans Serif';

    // Find default weight index (prefer Regular, Book, Medium or first index)
    var defaultWeightIdx = 0;
    for (var wIdx = 0; wIdx < weights.length; wIdx++) {
      var wLower = String(weights[wIdx]).toLowerCase();
      if (wLower === 'regular' || wLower === 'book' || wLower === 'roman' || wLower === 'medium') {
        defaultWeightIdx = wIdx;
        break;
      }
    }
    var activeWeight = weights[defaultWeightIdx] || 'Regular';
    var initialResolved = resolveVariantStyle(font.family || font.name, activeWeight, category, font.files);
    var initialNumericWeight = parseInt(initialResolved.fontWeight, 10) || 400;
    var isVariable = Boolean(font.is_variable) || weightsCount >= 6;
    var currentSize = (DOM.fontSizeSlider ? DOM.fontSizeSlider.value : '36');

    // Build weight chips
    var weightChipsHTML = weights.map(function (w, idx) {
      var isActive = (idx === defaultWeightIdx);
      return '<button type="button" class="weight-chip' + (isActive ? ' active' : '') + '" data-weight="' + escapeHTML(w) + '">' + escapeHTML(w) + '</button>';
    }).join('');

    var isFav = isFontFavorite(font.id);

    // Build Waterfall rows HTML for this card
    var waterfallRowsHTML = '';
    if (weights.length > 1) {
      waterfallRowsHTML = weights.map(function (w) {
        var wResolved = resolveVariantStyle(font.family || font.name, w, category, font.files);
        return [
          '<div class="card-waterfall-row' + (w === activeWeight ? ' is-active' : '') + '" data-weight="' + escapeHTML(w) + '">',
          '  <div class="waterfall-meta">',
          '    <span class="waterfall-style-name">' + escapeHTML(w) + '</span>',
          '    <span class="waterfall-weight-tag">' + escapeHTML(wResolved.fontWeight) + '</span>',
          '  </div>',
          '  <div class="waterfall-sample-text" contenteditable="true" spellcheck="false" style="font-family: ' + wResolved.fontFamily + '; font-weight: ' + wResolved.fontWeight + '; font-style: ' + wResolved.fontStyle + ';">',
          '    ' + escapeHTML(currentText),
          '  </div>',
          '  <button type="button" class="waterfall-apply-btn" data-weight="' + escapeHTML(w) + '" title="Áp dụng style này cho card">Dùng style</button>',
          '</div>'
        ].join('');
      }).join('');
    } else {
      var scaleSteps = [
        { label: 'Display 72px', size: 72, text: currentText },
        { label: 'Title 48px', size: 48, text: currentText },
        { label: 'Subhead 32px', size: 32, text: currentText },
        { label: 'Body 20px', size: 20, text: currentText },
        { label: 'Caption 14px', size: 14, text: '0123456789 • ABCDEFGHIJKLMNOPQRSTUVWXYZ • abcdefghijklmnopqrstuvwxyz • ăâđêôơư' }
      ];
      waterfallRowsHTML = scaleSteps.map(function (step) {
        return [
          '<div class="card-waterfall-row scale-tier-row" data-size="' + step.size + '">',
          '  <div class="waterfall-meta">',
          '    <span class="waterfall-style-name">' + escapeHTML(step.label) + '</span>',
          '    <span class="waterfall-weight-tag">' + step.size + 'px</span>',
          '  </div>',
          '  <div class="waterfall-sample-text" contenteditable="true" spellcheck="false" style="font-family: ' + initialResolved.fontFamily + '; font-weight: ' + initialResolved.fontWeight + '; font-style: ' + initialResolved.fontStyle + '; font-size: ' + step.size + 'px;">',
          '    ' + escapeHTML(step.text),
          '  </div>',
          '</div>'
        ].join('');
      }).join('');
    }

    return [
      '<article class="font-card" data-font-id="' + escapeHTML(font.id) + '" data-family="' + escapeHTML(font.family || font.name) + '" data-category="' + escapeHTML(category) + '" data-studio="' + escapeHTML(studioName) + '">',
      '  <header class="card-header">',
      '    <div class="card-title-row">',
      '      <div class="title-with-fav">',
      '        <button type="button" class="btn-fav' + (isFav ? ' active' : '') + '" data-fav-id="' + escapeHTML(font.id) + '" title="Đánh dấu yêu thích">⭐️</button>',
      '        <h3 class="card-family-name">' + escapeHTML(font.name) + '</h3>',
      '        <button type="button" class="btn-copy-name" data-copy-name="' + escapeHTML(font.name) + '" title="Copy tên font">',
      '          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
      '        </button>',
      '        <span class="fs-card-cat-badge">' + escapeHTML(category) + '</span>',
      '      </div>',
      '      <div class="card-fs-controls">',
      '        <div class="fs-slider-control fs-weight-control" title="Kéo để đổi độ dày chữ (Font-Weight)">',
      '          <span class="fs-control-label">Weight</span>',
      '          <input type="range" class="card-weight-slider fs-range-slider" min="100" max="900" step="' + (isVariable ? '10' : '100') + '" value="' + initialNumericWeight + '" aria-label="Độ dày font">',
      '          <span class="fs-control-val card-weight-val">' + initialNumericWeight + '</span>',
      '        </div>',
      '        <div class="fs-slider-control fs-size-control" title="Kéo để đổi cỡ chữ riêng cho font này">',
      '          <span class="fs-control-label">Size</span>',
      '          <input type="range" class="card-size-slider fs-range-slider" min="14" max="140" step="1" value="' + currentSize + '" aria-label="Cỡ chữ font">',
      '          <span class="fs-control-val card-size-val">' + currentSize + 'px</span>',
      '        </div>',
      '        <button type="button" class="card-styles-toggle fs-styles-btn badge" data-action="toggle-card-waterfall" aria-expanded="false" title="Nhấp để bung toàn bộ styles dạng Waterfall">',
      '          <span class="fs-styles-count">' + weightsLabel + '</span>',
      '          <svg class="chevron-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>',
      '        </button>',
      '        <span class="fs-var-badge ' + (isVariable ? 'is-variable' : 'is-static') + '">' + (isVariable ? 'Variable' : 'Static') + '</span>',
      '      </div>',
      '    </div>',
      '    <div class="card-designer-row">',
      '      <span>' + escapeHTML(font.designer || 'FEDU Studio') + '</span>',
      '      <span>•</span>',
      '      <span>' + escapeHTML(font.source || 'PDF & Drive') + '</span>',
      '    </div>',
      '    <div class="card-badges-row">',
      '      ' + studioBadge,
      '      ' + gtBadge,
      '      ' + cotypeBadge,
      '      ' + dinamoBadge,
      '      ' + klimBadge,
      '      ' + pangramBadge,
      '      ' + styleBadge,
      '      ' + moodBadge,
      '      ' + useBadge,
      '      ' + vnBadge,
      '    </div>',
      '  </header>',
      '  <div class="card-specimen-wrap">',
      '    <div class="preview-text" contenteditable="true" spellcheck="false" data-family="' + escapeHTML(font.family || font.name) + '" data-sample="' + escapeHTML(font.sample_text || '') + '" style="font-family: ' + initialResolved.fontFamily + '; font-weight: ' + initialResolved.fontWeight + '; font-style: ' + initialResolved.fontStyle + ';">',
      '      ' + escapeHTML(currentText),
      '    </div>',
      '  </div>',
      '  <div class="card-weights-bar" aria-label="Các biến thể độ dày">',
      '    ' + weightChipsHTML,
      '  </div>',
      '  <div class="card-waterfall-drawer fs-waterfall-panel" style="display: none;">',
      '    <div class="fs-waterfall-panel-header">',
      '      <div class="fs-waterfall-title-row">',
      '        <span class="fs-waterfall-kicker">WATERFALL SPECIMEN</span>',
      '        <span class="fs-waterfall-subkicker">' + weights.length + ' ' + (weights.length > 1 ? 'Styles' : 'Size Scale') + '</span>',
      '      </div>',
      '      <span class="fs-waterfall-tip">Bấm vào dòng để áp dụng style trực tiếp vào card</span>',
      '    </div>',
      '    <div class="fs-waterfall-rows-list">',
      '      ' + waterfallRowsHTML,
      '    </div>',
      '  </div>',
      '  <details class="card-drawer">',
      '    <summary class="drawer-trigger">',
      '      <span>Thông số &amp; Nhận định Đạo diễn</span>',
      '      <span>▾</span>',
      '    </summary>',
      '    <div class="drawer-content">',
      '      <div class="anatomy-grid">',
      '        <div class="anatomy-item"><span class="label">Độ tương phản</span><span class="val">' + escapeHTML(contrast) + '</span></div>',
      '        <div class="anatomy-item"><span class="label">Trục nghiêng</span><span class="val">' + escapeHTML(axis) + '</span></div>',
      '        <div class="anatomy-item"><span class="label">X-Height</span><span class="val">' + escapeHTML(xHeight) + '</span></div>',
      '        <div class="anatomy-item"><span class="label">Độ mở</span><span class="val">' + escapeHTML(aperture) + '</span></div>',
      '      </div>',
      '      ' + (originBadge ? '<div class="font-origin-badge" title="Nguồn gốc phông chữ">' + escapeHTML(originBadge) + '</div>' : ''),
      '      <blockquote class="director-quote">"' + escapeHTML(critiqueText || directorNotes) + '"</blockquote>',
      '    </div>',
      '  </details>',
      '  <footer class="card-footer">',
      '    <a href="' + downloadHref + '" class="btn-download-family" target="_blank" rel="noopener noreferrer" title="' + downloadTooltip + '">',
      '      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">',
      '        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>',
      '        <polyline points="7 10 12 15 17 10"/>',
      '        <line x1="12" y1="15" x2="12" y2="3"/>',
      '      </svg>',
      '      <span>Tải Trọn Bộ (.zip)</span>',
      '    </a>',
      '    <div class="secondary-actions">',
      '      <a href="' + driveViewUrl + '" class="btn-icon-action btn-drive-link" target="_blank" rel="noopener noreferrer" title="Mở file trên Google Drive">Drive ↗</a>',
      '      <button type="button" class="btn-icon-action btn-open-glyphs" data-action="glyphs" title="Xem bảng ký tự &amp; dấu Tiếng Việt">Glyphs</button>',
      '      <button type="button" class="btn-icon-action btn-copy-css" data-action="copy-css" title="Copy mã @font-face CSS">CSS</button>',
      '    </div>',
      '  </footer>',
      '</article>'
    ].join('\n');
  }

  /**
   * Progressively renders batches of font cards into the DOM.
   */
  function renderGrid(append) {
    if (!append) {
      DOM.fontGrid.innerHTML = '';
      App.pagination.currentPage = 1;
    }

    var total = App.filteredFonts.length;
    App.pagination.totalCount = total;

    // Update Result Counts
    if (DOM.resultsCount) {
      DOM.resultsCount.textContent = total + ' / ' + (App.allFonts ? App.allFonts.length : 376) + ' font families';
    }

    if (total === 0) {
      if (DOM.emptyState) {
        DOM.emptyState.classList.remove('hidden');
        var emptyTitle = DOM.emptyState.querySelector('.empty-title');
        var emptyDesc = DOM.emptyState.querySelector('p');
        if (App.activeFilters && App.activeFilters.category === 'favorites') {
          if (emptyTitle) emptyTitle.textContent = 'Chưa có font yêu thích nào';
          if (emptyDesc) emptyDesc.textContent = 'Bạn chưa đánh dấu font nào. Hãy nhấn biểu tượng ngôi sao ⭐ trên bất kỳ thẻ font nào để lưu vào danh sách yêu thích!';
        } else {
          if (emptyTitle) emptyTitle.textContent = 'Không tìm thấy font phù hợp';
          if (emptyDesc) emptyDesc.textContent = 'Thử điều chỉnh từ khóa tìm kiếm hoặc xóa bớt các tiêu chí lọc.';
        }
      }
      if (DOM.scrollSentinel) DOM.scrollSentinel.style.display = 'none';
      return;
    } else {
      if (DOM.emptyState) DOM.emptyState.classList.add('hidden');
      if (DOM.scrollSentinel) DOM.scrollSentinel.style.display = 'block';
    }

    var start = (App.pagination.currentPage - 1) * App.pagination.pageSize;
    var end = Math.min(start + App.pagination.pageSize, total);
    var currentBatch = App.filteredFonts.slice(start, end);

    var fragment = document.createRange().createContextualFragment(
      currentBatch.map(createFontCardHTML).join('')
    );

    DOM.fontGrid.appendChild(fragment);

    // Attach card event listeners
    attachCardEvents();

    // Hide sentinel when all items rendered
    if (end >= total && DOM.scrollSentinel) {
      DOM.scrollSentinel.style.display = 'none';
    }

    // Lazy load web fonts for cards in current batch
    lazyLoadBatchFonts(currentBatch);
  }

  /**
   * Attaches event listeners for weight chips, copy CSS, copy name, favorite, and glyphs modal buttons.
   */
  function attachCardEvents() {
    // Weight switching with live CSS resolution
    DOM.fontGrid.querySelectorAll('.weight-chip:not([data-bound])').forEach(function (chip) {
      chip.setAttribute('data-bound', 'true');
      chip.addEventListener('click', function (e) {
        var card = chip.closest('.font-card');
        if (!card) return;
        var family = card.getAttribute('data-family');
        var weight = chip.getAttribute('data-weight');
        var fontId = card.getAttribute('data-font-id');
        var fontObj = App.allFonts.find(function (f) { return f.id === fontId || (f.family || f.name) === family; });
        var category = card.getAttribute('data-category') || (fontObj && fontObj.category) || 'Sans Serif';
        var files = fontObj ? fontObj.files : [];

        // Update active chip in card
        card.querySelectorAll('.weight-chip').forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');

        // Resolve exact CSS properties
        var resolved = resolveVariantStyle(family, weight, category, files);

        // Update card preview style IMMEDIATELY
        var preview = card.querySelector('.preview-text');
        if (preview) {
          preview.style.fontWeight = resolved.fontWeight;
          preview.style.fontStyle = resolved.fontStyle;
          preview.style.fontFamily = resolved.fontFamily;
          if (fontObj && (fontObj.is_variable || (fontObj.weights && fontObj.weights.length >= 6))) {
            preview.style.fontVariationSettings = "'wght' " + (parseInt(resolved.fontWeight, 10) || 400);
          }
        }

        // Sync card weight slider & display
        var numW = parseInt(resolved.fontWeight, 10) || 400;
        var wSlider = card.querySelector('.card-weight-slider');
        if (wSlider) wSlider.value = numW;
        var wVal = card.querySelector('.card-weight-val');
        if (wVal) wVal.textContent = numW;

        // Highlight matching row in waterfall drawer
        card.querySelectorAll('.card-waterfall-row').forEach(function (r) {
          if (r.getAttribute('data-weight') === weight) {
            r.classList.add('is-active');
          } else {
            r.classList.remove('is-active');
          }
        });

        // Eagerly pre-load font weight
        if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
          document.fonts.load(resolved.fontWeight + ' 36px "' + family + '"');
        }

        // Dynamically load font face if available on server
        if (resolved.matchedFilename && typeof FontFace !== 'undefined') {
          var fontFaceFamily = family;
          var fontUrl = 'fonts/' + resolved.matchedFilename;
          if (!document.fonts.check(resolved.fontWeight + ' 16px "' + fontFaceFamily + '"')) {
            var face = new FontFace(fontFaceFamily, 'url("' + fontUrl + '")', {
              weight: resolved.fontWeight,
              style: resolved.fontStyle
            });
            face.load().then(function (loaded) {
              document.fonts.add(loaded);
            }).catch(function () {});
          }
        }
      });
    });

    // Fontshare Weight Slider on Card (100 to 900)
    DOM.fontGrid.querySelectorAll('.card-weight-slider:not([data-bound])').forEach(function (slider) {
      slider.setAttribute('data-bound', 'true');
      slider.addEventListener('input', function () {
        var card = slider.closest('.font-card');
        if (!card) return;
        var val = parseInt(slider.value, 10);
        var valDisplay = card.querySelector('.card-weight-val');
        if (valDisplay) valDisplay.textContent = val;

        var family = card.getAttribute('data-family');
        var fontId = card.getAttribute('data-font-id');
        var fontObj = App.allFonts.find(function (f) { return f.id === fontId || (f.family || f.name) === family; });
        var category = card.getAttribute('data-category') || (fontObj && fontObj.category) || 'Sans Serif';
        var files = fontObj ? fontObj.files : [];
        var weights = fontObj && Array.isArray(fontObj.weights) ? fontObj.weights : [];
        var fallbackStack = App.typeTester ? App.typeTester.getFallbackStack(category) : 'sans-serif';

        var preview = card.querySelector('.preview-text');
        if (preview) {
          preview.style.fontWeight = val;
          preview.style.fontFamily = "'" + family + "', '" + family.replace(/\s+/g, '') + "', " + fallbackStack;
          if (fontObj && (fontObj.is_variable || weights.length >= 6)) {
            preview.style.fontVariationSettings = "'wght' " + val;
          }
        }

        if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
          document.fonts.load(val + ' 36px "' + family + '"');
        }

        // Snap to closest weight chip and activate it
        var closestWeight = null;
        var minDiff = 9999;
        var closestChip = null;

        var chips = card.querySelectorAll('.weight-chip');
        chips.forEach(function (chip) {
          var wName = chip.getAttribute('data-weight');
          var res = resolveVariantStyle(family, wName, category, files);
          var numW = parseInt(res.fontWeight, 10) || 400;
          var diff = Math.abs(numW - val);
          if (diff < minDiff) {
            minDiff = diff;
            closestWeight = wName;
            closestChip = chip;
          }
        });

        if (closestChip) {
          chips.forEach(function (c) { c.classList.remove('active'); });
          closestChip.classList.add('active');
        }

        if (closestWeight) {
          var resolved = resolveVariantStyle(family, closestWeight, category, files);
          if (preview) {
            preview.style.fontStyle = resolved.fontStyle;
          }
        }

        // Highlight active waterfall row
        card.querySelectorAll('.card-waterfall-row').forEach(function (r) {
          if (r.getAttribute('data-weight') === closestWeight) {
            r.classList.add('is-active');
          } else {
            r.classList.remove('is-active');
          }
        });
      });
    });

    // Fontshare Size Slider on Card (14 to 140)
    DOM.fontGrid.querySelectorAll('.card-size-slider:not([data-bound])').forEach(function (slider) {
      slider.setAttribute('data-bound', 'true');
      slider.addEventListener('input', function () {
        var card = slider.closest('.font-card');
        if (!card) return;
        var val = parseInt(slider.value, 10);
        var valDisplay = card.querySelector('.card-size-val');
        if (valDisplay) valDisplay.textContent = val + 'px';

        var preview = card.querySelector('.preview-text');
        if (preview) {
          preview.style.fontSize = val + 'px';
        }
      });
    });

    // Card Waterfall Toggle Button
    DOM.fontGrid.querySelectorAll('[data-action="toggle-card-waterfall"]:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var card = btn.closest('.font-card');
        if (!card) return;
        var drawer = card.querySelector('.card-waterfall-drawer');
        if (!drawer) return;

        var isOpen = drawer.style.display !== 'none';
        if (isOpen) {
          drawer.style.display = 'none';
          btn.classList.remove('is-open');
          btn.setAttribute('aria-expanded', 'false');
          card.classList.remove('is-waterfall-open');
        } else {
          drawer.style.display = 'block';
          btn.classList.add('is-open');
          btn.setAttribute('aria-expanded', 'true');
          card.classList.add('is-waterfall-open');
        }
      });
    });

    // Card Waterfall Row Click & Apply Button
    DOM.fontGrid.querySelectorAll('.card-waterfall-row:not([data-bound])').forEach(function (row) {
      row.setAttribute('data-bound', 'true');
      row.addEventListener('click', function (e) {
        if (e.target.classList.contains('waterfall-sample-text') && document.activeElement === e.target) {
          return;
        }
        var card = row.closest('.font-card');
        if (!card) return;
        var weightName = row.getAttribute('data-weight');
        if (!weightName) return;

        var chip = card.querySelector('.weight-chip[data-weight="' + weightName + '"]');
        if (chip) {
          chip.click();
        } else {
          var family = card.getAttribute('data-family');
          var fontId = card.getAttribute('data-font-id');
          var fontObj = App.allFonts.find(function (f) { return f.id === fontId || (f.family || f.name) === family; });
          var category = card.getAttribute('data-category') || (fontObj && fontObj.category) || 'Sans Serif';
          var files = fontObj ? fontObj.files : [];
          var resolved = resolveVariantStyle(family, weightName, category, files);
          var preview = card.querySelector('.preview-text');
          if (preview) {
            preview.style.fontWeight = resolved.fontWeight;
            preview.style.fontStyle = resolved.fontStyle;
            preview.style.fontFamily = resolved.fontFamily;
          }
          var numW = parseInt(resolved.fontWeight, 10) || 400;
          var wSlider = card.querySelector('.card-weight-slider');
          if (wSlider) wSlider.value = numW;
          var wVal = card.querySelector('.card-weight-val');
          if (wVal) wVal.textContent = numW;

          if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
            document.fonts.load(numW + ' 36px "' + family + '"');
          }
        }

        card.querySelectorAll('.card-waterfall-row').forEach(function (r) { r.classList.remove('is-active'); });
        row.classList.add('is-active');
      });
    });

    // Favorite Button
    DOM.fontGrid.querySelectorAll('.btn-fav:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var fontId = btn.getAttribute('data-fav-id');
        var isNowFav = toggleFontFavorite(fontId);
        if (isNowFav) {
          btn.classList.add('active');
          showToast('Đã thêm vào danh sách Yêu thích ⭐️');
        } else {
          btn.classList.remove('active');
          showToast('Đã bỏ khỏi Yêu thích');
        }
      });
    });

    // Copy Name Button
    DOM.fontGrid.querySelectorAll('.btn-copy-name:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var fontName = btn.getAttribute('data-copy-name');
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(fontName).then(function () {
            showToast('Đã sao chép: ' + fontName);
          });
        }
      });
    });

    // GT Font badge filter click
    DOM.fontGrid.querySelectorAll('.badge-gt:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var gtChip = document.querySelector('.chip-btn[data-category="GT Font"]');
        if (gtChip) {
          gtChip.click();
        } else {
          App.activeFilters.category = 'GT Font';
          applyFilters();
        }
      });
    });

    // CoType badge filter click
    DOM.fontGrid.querySelectorAll('.badge-cotype:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var cotypeChip = document.querySelector('.chip-btn[data-category="CoType"]');
        if (cotypeChip) {
          cotypeChip.click();
        } else {
          App.activeFilters.category = 'CoType';
          applyFilters();
        }
      });
    });

    // Dinamo badge filter click
    DOM.fontGrid.querySelectorAll('.badge-dinamo:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var chip = document.querySelector('.chip-btn[data-category="Dinamo"]');
        if (chip) {
          chip.click();
        } else {
          App.activeFilters.category = 'Dinamo';
          applyFilters();
        }
      });
    });

    // Klim badge filter click
    DOM.fontGrid.querySelectorAll('.badge-klim:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var chip = document.querySelector('.chip-btn[data-category="Klim"]');
        if (chip) {
          chip.click();
        } else {
          App.activeFilters.category = 'Klim';
          applyFilters();
        }
      });
    });

    // Pangram badge filter click
    DOM.fontGrid.querySelectorAll('.badge-pangram:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var chip = document.querySelector('.chip-btn[data-category="Pangram"]');
        if (chip) {
          chip.click();
        } else {
          App.activeFilters.category = 'Pangram';
          applyFilters();
        }
      });
    });

    // Glyphs modal button
    DOM.fontGrid.querySelectorAll('[data-action="glyphs"]:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function () {
        var card = btn.closest('.font-card');
        if (!card) return;
        var fontId = card.getAttribute('data-font-id');
        var fontObj = App.allFonts.find(function (f) { return f.id === fontId; });
        if (fontObj) {
          openGlyphModal(fontObj);
        }
      });
    });

    // Copy CSS button
    DOM.fontGrid.querySelectorAll('[data-action="copy-css"]:not([data-bound])').forEach(function (btn) {
      btn.setAttribute('data-bound', 'true');
      btn.addEventListener('click', function () {
        var card = btn.closest('.font-card');
        if (!card) return;
        var fontId = card.getAttribute('data-font-id');
        var fontObj = App.allFonts.find(function (f) { return f.id === fontId; });
        if (fontObj) {
          var cssRule = App.typeTester.generateFontFaceCSS(
            fontObj.name || fontObj.family,
            fontObj.web_font_url || 'https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts/' + fontObj.id + '.woff2'
          );
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(cssRule).then(function () {
              showToast('Đã sao chép CSS @font-face của ' + fontObj.name);
            });
          }
        }
      });
    });
  }

  /**
   * Lazy loads web font assets via FontFace API for fonts entering the viewport.
   */
  function lazyLoadBatchFonts(batch) {
    if (!batch || !Array.isArray(batch)) return;
    batch.forEach(function (font) {
      if (font.web_font_url) {
        var family = font.family || font.name;
        App.typeTester.loadWebFont(family, font.web_font_url).catch(function () {
          // Graceful fallback to category stack already declared inline
        });
      }
    });
  }

  /**
   * Populates the studio select dropdowns with available studios and font counts.
   */
  function populateStudioDropdowns() {
    var counts = CatalogLoader.computeFacetCounts(App.allFonts);
    if (!counts || !counts.studios) return;

    var sortedStudios = Object.keys(counts.studios).sort(function (a, b) {
      return counts.studios[b] - counts.studios[a];
    });

    if (DOM.filterStudio) {
      var currentVal = App.activeFilters.studio || DOM.filterStudio.value || 'all';
      var html = '<option value="all">🏢 Studio: Tất cả (' + App.allFonts.length + ')</option>';
      sortedStudios.forEach(function (st) {
        html += '<option value="' + escapeHTML(st) + '">' + escapeHTML(st) + ' (' + counts.studios[st] + ')</option>';
      });
      DOM.filterStudio.innerHTML = html;
      DOM.filterStudio.value = currentVal;
    }

    if (DOM.fsFilterStudio) {
      var fsVal = App.fontshareState.studio || DOM.fsFilterStudio.value || 'all';
      var fsHtml = '<option value="all">Studio: Tất cả ▾</option>';
      sortedStudios.forEach(function (st) {
        fsHtml += '<option value="' + escapeHTML(st) + '">' + escapeHTML(st) + ' (' + counts.studios[st] + ')</option>';
      });
      DOM.fsFilterStudio.innerHTML = fsHtml;
      DOM.fsFilterStudio.value = fsVal;
    }
  }

  /**
   * Executes instant search and faceted filtering.
   */
  function applyFilters() {
    var startTime = performance.now();

    // 1. Search Query
    var searchResults = CatalogLoader.instantSearch(App.indexedFonts, App.activeFilters.searchQuery);

    // 2. Multi-Dimensional Filter
    var filterCriteria = {
      category: App.activeFilters.category,
      studio: App.activeFilters.studio,
      mood: App.activeFilters.mood,
      use_case: App.activeFilters.use_case,
      weight: App.activeFilters.weight,
      vietnamese_support: App.activeFilters.vietnamese_support
    };

    if (App.activeFilters.category === 'favorites') {
      var favIds = getFavorites();
      searchResults = searchResults.filter(function (f) {
        return favIds.indexOf(f.id) !== -1;
      });
      filterCriteria.category = 'all';
    }

    App.filteredFonts = CatalogLoader.multiFilter(searchResults, filterCriteria);

    var elapsed = performance.now() - startTime;
    if (DOM.searchLatency) {
      DOM.searchLatency.textContent = elapsed < 1 ? '< 1ms' : (elapsed.toFixed(1) + 'ms');
    }

    // 3. Update Facet Count Badges
    updateFacetCountBadges();

    // 4. Render Grid from Page 1
    renderGrid(false);
  }

  /**
   * Computes live dynamic count badges.
   */
  function updateFacetCountBadges() {
    var counts = CatalogLoader.computeFacetCounts(App.allFonts);
    if (!counts || !counts.categories) return;

    if (DOM.countAll) DOM.countAll.textContent = counts.categories['all'] || 0;
    if (DOM.countSans) DOM.countSans.textContent = counts.categories['Sans Serif'] || 0;
    if (DOM.countSerif) DOM.countSerif.textContent = counts.categories['Serif'] || 0;
    if (DOM.countVintage) DOM.countVintage.textContent = counts.categories['Việt Nam Oldstyle / Vintage Sài Gòn'] || 0;
    if (DOM.countMonoScript) DOM.countMonoScript.textContent = counts.categories['Blackletter, Script & Monospace'] || 0;
    if (DOM.countGt) DOM.countGt.textContent = counts.categories['GT Font'] || 0;
    if (DOM.countCotype) DOM.countCotype.textContent = counts.categories['CoType'] || 0;
    if (DOM.countDinamo) DOM.countDinamo.textContent = counts.categories['Dinamo'] || 0;
    if (DOM.countKlim) DOM.countKlim.textContent = counts.categories['Klim'] || 0;
    if (DOM.countPangram) DOM.countPangram.textContent = counts.categories['Pangram'] || 0;
    if (DOM.countFav) DOM.countFav.textContent = getFavorites().length;
  }

  /**
   * Clears all filters back to default state.
   */
  function clearAllFilters() {
    App.activeFilters = {
      searchQuery: '',
      category: 'all',
      studio: 'all',
      mood: 'all',
      use_case: 'all',
      weight: 'all',
      vietnamese_support: true
    };
    App.fontshareState.studio = 'all';

    if (DOM.searchInput) DOM.searchInput.value = '';
    if (DOM.filterStudio) DOM.filterStudio.value = 'all';
    if (DOM.fsFilterStudio) DOM.fsFilterStudio.value = 'all';
    if (DOM.filterMood) DOM.filterMood.value = 'all';
    if (DOM.filterUseCase) DOM.filterUseCase.value = 'all';
    if (DOM.filterWeight) DOM.filterWeight.value = 'all';
    if (DOM.filterVnSupport) DOM.filterVnSupport.checked = true;

    DOM.categoryChips.forEach(function (btn) {
      if (btn.getAttribute('data-category') === 'all') {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    applyFilters();
    var count = (App.allFonts && App.allFonts.length) ? App.allFonts.length : 363;
    showToast('Đã xóa bộ lọc, hiển thị toàn bộ ' + count + ' font');
  }

  /**
   * Glyph Modal Controller
   */
  function openGlyphModal(font) {
    App.activeModalFont = font;
    if (DOM.glyphModalTitle) {
      DOM.glyphModalTitle.textContent = (font.name || font.family) + ' — Bảng Ký Tự & Dấu Tiếng Việt';
    }
    if (DOM.glyphModalSubtitle) {
      DOM.glyphModalSubtitle.textContent = (font.designer || 'FEDU Studio') + ' • 134 ký tự Tiếng Việt có dấu';
    }

    renderModalGlyphs();
    DOM.glyphModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeGlyphModal() {
    DOM.glyphModal.classList.remove('open');
    document.body.style.overflow = '';
  }

  function renderModalGlyphs() {
    if (!DOM.glyphModalBody || !App.activeModalFont) return;
    DOM.glyphModalBody.innerHTML = '';

    var family = App.activeModalFont.name || App.activeModalFont.family || 'sans-serif';

    if (App.activeGlyphTab === 'complex') {
      // Diagnostic Complex Multi-Tone Words Tab
      var words = App.typeTester.getComplexWords();
      var wordsSection = document.createElement('div');
      wordsSection.className = 'glyph-group';

      var title = document.createElement('div');
      title.className = 'glyph-group-title';
      title.textContent = '15 Từ Thử Nghiệm Dấu Xếp Tầng & Thanh Điệu Phức Tạp (Nhấp để copy)';
      wordsSection.appendChild(title);

      var grid = document.createElement('div');
      grid.style.display = 'flex';
      grid.style.flexWrap = 'wrap';
      grid.style.gap = '10px';

      words.forEach(function (word) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'weight-chip';
        btn.style.fontFamily = '\'' + family + '\', sans-serif';
        btn.style.fontSize = '1.25rem';
        btn.style.padding = '8px 16px';
        btn.textContent = word;
        btn.title = 'Nhấp để copy từ "' + word + '"';

        btn.addEventListener('click', function () {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(word).then(function () {
              showToast('Đã copy từ: "' + word + '"');
            });
          }
        });

        grid.appendChild(btn);
      });

      wordsSection.appendChild(grid);
      DOM.glyphModalBody.appendChild(wordsSection);
    } else {
      // Handle tab filtering for lowercase and uppercase
      var filterMode = 'all-vn';
      if (App.activeGlyphTab === 'lower') {
        filterMode = 'lower';
      } else if (App.activeGlyphTab === 'upper') {
        filterMode = 'upper';
      }

      // Render standard character map
      App.typeTester.renderGlyphMap(DOM.glyphModalBody, App.activeModalFont, function (char, hex) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(char).then(function () {
            showToast('Đã copy ký tự \'' + char + '\' (U+' + hex + ')');
          });
        }
      }, filterMode);
    }
  }

  /* ==========================================================================
     MULTI-VIEW ARCHITECTURE (Catalog, Fontshare, Pair)
     ========================================================================== */

  function switchView(viewName) {
    if (!viewName) viewName = 'catalog';
    App.currentView = viewName;

    // Update buttons
    if (DOM.viewBtns) {
      DOM.viewBtns.forEach(function (btn) {
        var isMatch = (btn.getAttribute('data-view') === viewName);
        btn.classList.toggle('active', isMatch);
        btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
      });
    }

    // Update view panels
    if (DOM.catalogView) DOM.catalogView.classList.toggle('hidden', viewName !== 'catalog');
    if (DOM.fontshareView) DOM.fontshareView.classList.toggle('hidden', viewName !== 'fontshare');
    if (DOM.pairView) DOM.pairView.classList.toggle('hidden', viewName !== 'pair');

    // Trigger specific view rendering
    if (viewName === 'fontshare') {
      renderFontshareView();
    } else if (viewName === 'pair') {
      initPairView();
    }

    // Sync URL hash
    try {
      if (history && history.replaceState) {
        history.replaceState(null, '', '#' + viewName);
      }
    } catch (e) { /* ignore */ }
  }

  /* ==========================================================================
     FONTSHARE WATERFALL & EDITORIAL SPECIMEN CONTROLLER (Image 4 Parity)
     ========================================================================== */

  var CITIES_PRESETS = ['Hà Nội', 'Tokyo', 'Paris', 'New York', 'Đà Nẵng', 'Berlin', 'Sài Gòn', 'London', 'Rome', 'Kyoto'];
  var EXCERPTS_PRESETS = [
    'Nghệ thuật chữ đồ họa thực chiến',
    'Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ màu.',
    'Kiến trúc dữ liệu & kỷ nguyên trí tuệ nhân tạo',
    'Vẻ đẹp vĩnh cửu của dấu ấn Typography Việt Nam',
    'Tối ưu hóa thuật toán và trải nghiệm người dùng'
  ];

  function renderFontshareCardHTML(font, idx, state) {
    var family = font.family || font.name;
    var weights = Array.isArray(font.weights) ? font.weights : [];
    var designer = font.designer || 'FEDU Type Foundry';
    var weightsCount = weights.length || (font.files_count || 1);
    var defaultDrive = (font.id && font.id.startsWith('gr-'))
      ? 'https://drive.google.com/drive/folders/1aT81y72_QzEGJjEFWSEjC11iLLXdwkpO?usp=sharing'
      : 'https://drive.google.com/drive/folders/1mEkkjojZUZzBQYmcXnJoFIWM4QBc7u90?usp=sharing';
    var driveView = font.drive_view_url || font.drive_url || font.drive_link || defaultDrive;
    var driveDown = font.drive_download_url || font.download_url || font.zip_url || driveView;
    var isVariable = font.is_variable || weightsCount >= 6;
    var sourceType = font.source_type || (font.license || 'Closed Source');
    var isFav = isFontFavorite(font.id);

    // Lazy load webfont for visible cards
    if (font.web_font_url) {
      App.typeTester.loadWebFont(family, font.web_font_url).catch(function () {});
    }

    // Resolve specimen text based on presets or custom input
    var specimenText = font.name;
    if (state.text && state.text.trim()) {
      specimenText = state.text.trim();
    } else if (state.preset === 'names') {
      specimenText = font.name;
    } else if (state.preset === 'cities') {
      specimenText = CITIES_PRESETS[idx % CITIES_PRESETS.length];
    } else if (state.preset === 'excerpts') {
      specimenText = EXCERPTS_PRESETS[idx % EXCERPTS_PRESETS.length];
    }

    var fallbackCategory = (font.category && font.category.toLowerCase().includes('serif') && !font.category.toLowerCase().includes('sans')) ? 'serif' : 'sans-serif';

    // Build waterfall rows for Fontshare card (dynamic for multi-style, 5 scale tiers for single style)
    var waterfallRowsHTML = '';
    if (weights.length > 1) {
      waterfallRowsHTML = weights.map(function (w) {
        var wResolved = resolveVariantStyle(family, w, fallbackCategory, font.files);
        return [
          '<div class="card-waterfall-row waterfall-row" data-weight="' + escapeHTML(w) + '">',
          '  <div class="waterfall-meta">',
          '    <span class="waterfall-style-name">' + escapeHTML(w) + '</span>',
          '    <span class="waterfall-weight-tag">' + escapeHTML(wResolved.fontWeight) + '</span>',
          '  </div>',
          '  <div class="waterfall-sample-text" contenteditable="true" spellcheck="false" style="font-family: ' + wResolved.fontFamily + '; font-weight: ' + wResolved.fontWeight + '; font-style: ' + wResolved.fontStyle + ';">',
          '    ' + escapeHTML(specimenText),
          '  </div>',
          '  <button type="button" class="waterfall-apply-btn" data-weight="' + escapeHTML(w) + '" title="Áp dụng style này cho card">Dùng style</button>',
          '</div>'
        ].join('');
      }).join('');
    } else {
      waterfallRowsHTML = [
        '<div class="card-waterfall-row waterfall-row"><span class="waterfall-size-tag">72px</span><div class="waterfall-text" contenteditable="true" spellcheck="false" style="font-size: 72px; font-weight: 700;">Việt Nam Độc Lập</div></div>',
        '<div class="card-waterfall-row waterfall-row"><span class="waterfall-size-tag">48px</span><div class="waterfall-text" contenteditable="true" spellcheck="false" style="font-size: 48px; font-weight: 600;">Nghệ thuật chữ đồ họa thực chiến</div></div>',
        '<div class="card-waterfall-row waterfall-row"><span class="waterfall-size-tag">32px</span><div class="waterfall-text" contenteditable="true" spellcheck="false" style="font-size: 32px; font-weight: 400;">Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ màu.</div></div>',
        '<div class="card-waterfall-row waterfall-row"><span class="waterfall-size-tag">20px</span><div class="waterfall-text" contenteditable="true" spellcheck="false" style="font-size: 20px; font-weight: 400;">Đường nét hài hòa, tinh tế, dấu thanh điệu chuẩn xác bảo toàn vẻ đẹp tiếng Việt có dấu.</div></div>',
        '<div class="card-waterfall-row waterfall-row"><span class="waterfall-size-tag">14px</span><div class="waterfall-text" contenteditable="true" spellcheck="false" style="font-size: 14px; font-weight: 400; letter-spacing: 0.05em;">0123456789 • ABCDEFGHIJKLMNOPQRSTUVWXYZ • abcdefghijklmnopqrstuvwxyz • ăâđêôơư</div></div>'
      ].join('');
    }

    var fsStudioName = font.studio || font.foundry || 'FEDU Type Studio';
    return [
      '<article class="fontshare-card fs-list-item" data-family="' + escapeHTML(family) + '" data-font-id="' + escapeHTML(font.id) + '" data-studio="' + escapeHTML(fsStudioName) + '">',
      '  <div class="fs-item-meta-top">',
      '    <div class="fs-item-title-group">',
      '      <h3 class="fs-item-name" style="font-family: \'' + escapeHTML(family) + '\', ' + fallbackCategory + ';">' + escapeHTML(font.name) + '</h3>',
      '      <button type="button" class="fs-star-btn ' + (isFav ? 'active' : '') + '" data-fav-id="' + escapeHTML(font.id) + '" aria-label="Favorite">' + (isFav ? '★' : '☆') + '</button>',
      '    </div>',
      '    <div class="fs-item-badges">',
      '      <button type="button" class="fs-pill-badge fs-studio-badge badge-studio" data-studio="' + escapeHTML(fsStudioName) + '" title="Gom nhóm font theo studio ' + escapeHTML(fsStudioName) + '">🏢 ' + escapeHTML(fsStudioName) + '</button>',
      '      <button type="button" class="fs-styles-badge card-styles-toggle" data-action="toggle-card-waterfall" aria-expanded="false">' + weightsCount + ' styles ▾</button>',
      '      <span class="fs-feature-badge">' + (isVariable ? 'Variable' : 'Static') + '</span>',
      '      <span class="fs-license-badge">' + escapeHTML(sourceType) + '</span>',
      '    </div>',
      '  </div>',
      '  <div class="fs-item-specimen-wrap">',
      '    <div class="fs-item-specimen preview-text" contenteditable="true" spellcheck="false" style="font-family: \'' + escapeHTML(family) + '\', ' + fallbackCategory + '; font-size: ' + state.size + 'px; text-align: ' + state.align + ';">',
      '      ' + escapeHTML(specimenText),
      '    </div>',
      '  </div>',
      '  <div class="fontshare-waterfall fs-waterfall-drawer card-waterfall-drawer" style="font-family: \'' + escapeHTML(family) + '\', ' + fallbackCategory + '; display: none;">',
      waterfallRowsHTML,
      '  </div>',
      '  <div class="fs-item-meta-bottom">',
      '    <span class="fs-designer">Designed by ' + escapeHTML(designer) + '</span>',
      '    <div class="fs-card-weight-ctrl" title="Độ dày font (Font Weight)">',
      '      <span class="fs-weight-icon" aria-hidden="true">W</span>',
      '      <input type="range" class="card-weight-slider fs-range-slider" min="100" max="900" step="100" value="400" aria-label="Độ dày font">',
      '      <span class="fs-weight-val">400</span>',
      '    </div>',
      '    <div class="fs-actions">',
      '      <button type="button" class="fs-btn-waterfall-toggle card-styles-toggle" data-action="toggle-waterfall" data-action-card="toggle-card-waterfall">Waterfall ▾</button>',
      '      <button type="button" class="btn-seg btn-glyph-trigger" data-glyph-font-id="' + escapeHTML(font.id) + '">Glyphs</button>',
      '      <a href="' + escapeHTML(driveView) + '" class="btn-seg btn-drive-link" target="_blank" rel="noopener noreferrer" title="Mở trên Google Drive">Drive ↗</a>',
      '      <a href="' + escapeHTML(driveDown) + '" class="fs-download-link" target="_blank" rel="noopener noreferrer">Tải ZIP</a>',
      '    </div>',
      '  </div>',
      '</article>'
    ].join('');
  }

  function updateFontshareSentinel(hasMore) {
    var sentinel = DOM.fontshareSentinel;
    var endMsg = DOM.fontshareEndMessage;
    var pagination = App.fontsharePagination;

    if (hasMore) {
      if (sentinel) sentinel.style.display = 'flex';
      if (endMsg) endMsg.style.display = 'none';
    } else {
      if (sentinel) sentinel.style.display = 'none';
      if (endMsg) {
        if (pagination && pagination.pool && pagination.pool.length > 0) {
          endMsg.style.display = 'block';
          if (DOM.fsEndCount) DOM.fsEndCount.textContent = pagination.pool.length;
        } else {
          endMsg.style.display = 'none';
        }
      }
    }
  }

  function checkSentinelInView() {
    var sentinel = DOM.fontshareSentinel;
    if (!sentinel || sentinel.style.display === 'none') return false;
    var rect = sentinel.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    return rect.top <= vh + 150;
  }

  function appendFontshareBatch() {
    if (!DOM.fontshareGrid) return;
    var pagination = App.fontsharePagination;
    if (!pagination || pagination.isLoading) return;
    if (pagination.renderedCount >= pagination.pool.length) {
      updateFontshareSentinel(false);
      return;
    }

    pagination.isLoading = true;
    var state = App.fontshareState;
    var start = pagination.renderedCount;
    var end = Math.min(start + pagination.batchSize, pagination.pool.length);
    var nextBatch = pagination.pool.slice(start, end);

    var html = nextBatch.map(function (font, i) {
      return renderFontshareCardHTML(font, start + i, state);
    }).join('');

    DOM.fontshareGrid.insertAdjacentHTML('beforeend', html);
    pagination.renderedCount = end;
    pagination.isLoading = false;

    var hasMore = pagination.renderedCount < pagination.pool.length;
    updateFontshareSentinel(hasMore);

    // Auto-fill viewport if screen height is larger than initial cards
    if (hasMore && checkSentinelInView()) {
      requestAnimationFrame(function () {
        appendFontshareBatch();
      });
    }
  }

  function renderFontshareView(options) {
    if (!DOM.fontshareGrid) return;

    var state = App.fontshareState;
    var query = (DOM.fontshareSearch ? DOM.fontshareSearch.value.trim() : '').toLowerCase();

    // Filter catalog fonts (strictly remove any non-Vietnamese, ultro or clash display fonts)
    var catalogFonts = App.allFonts.filter(function (f) {
      var n = (f.name || f.family || '').toLowerCase();
      var id = (f.id || '').toLowerCase();
      return n !== 'satoshi' && n !== 'clash display' && id !== 'fd-clashdisplay' && id !== 'fd-ultro' && !n.includes('ultro');
    });

    // Curated priority order for Fontshare showcase (100% Vietnamese FEDU typefaces):
    // GR Sectra, GR America, FD NoeDisplay, FDAeonik, FD Gilroy, FD Acta, GR Super, FD Walsheim Pro...
    var priorityIds = ['gr-sectra', 'gr-america', 'fd-noedisplay', 'fdaeonik', 'fd-gilroy', 'fd-acta', 'gr-super', 'fd-walsheim-pro'];
    var prioritized = [];
    priorityIds.forEach(function (pid) {
      var match = catalogFonts.find(function (f) { return f.id === pid; });
      if (match) prioritized.push(match);
    });
    var remaining = catalogFonts.filter(function (f) { return !priorityIds.includes(f.id); });

    var pool = prioritized.concat(remaining);

    // Search query filter
    if (query) {
      pool = pool.filter(function (f) {
        var n = (f.name || f.family || '').toLowerCase();
        var d = (f.designer || '').toLowerCase();
        var c = (f.category || '').toLowerCase();
        var s = (f.studio || f.foundry || '').toLowerCase();
        return n.indexOf(query) !== -1 || d.indexOf(query) !== -1 || c.indexOf(query) !== -1 || s.indexOf(query) !== -1;
      });
    }

    // Studio dropdown filter
    if (state.studio && state.studio !== 'all') {
      pool = pool.filter(function (f) {
        var s = (f.studio || f.foundry || '').toLowerCase();
        return s === state.studio.toLowerCase();
      });
    }

    // Category dropdown filter
    if (state.category && state.category !== 'all') {
      pool = pool.filter(function (f) {
        var c = (f.category || '').toLowerCase();
        if (state.category === 'GT Font') return (f.tags && f.tags.includes('GT Font')) || (f.name && (f.name.startsWith('GT') || f.name.startsWith('GR'))) || Boolean(f.is_gt);
        if (state.category === 'CoType') return (typeof CatalogLoader !== 'undefined' && CatalogLoader.isCoTypeFont) ? CatalogLoader.isCoTypeFont(f) : Boolean(f.is_cotype);
        if (state.category === 'Dinamo') return (typeof CatalogLoader !== 'undefined' && CatalogLoader.isDinamoFont) ? CatalogLoader.isDinamoFont(f) : Boolean(f.is_dinamo);
        if (state.category === 'Klim') return (typeof CatalogLoader !== 'undefined' && CatalogLoader.isKlimFont) ? CatalogLoader.isKlimFont(f) : Boolean(f.is_klim);
        if (state.category === 'Pangram') return (typeof CatalogLoader !== 'undefined' && CatalogLoader.isPangramFont) ? CatalogLoader.isPangramFont(f) : Boolean(f.is_pangram);
        if (state.category === 'Vintage') return c.includes('vintage') || (f.tags && f.tags.some(function (t) { return t.includes('Vintage'); }));
        if (state.category === 'Mono/Script') return c.includes('mono') || c.includes('script');
        return c.includes(state.category.toLowerCase());
      });
    }

    // Personality dropdown filter
    if (state.personality && state.personality !== 'all') {
      pool = pool.filter(function (f) {
        return f.matrix_3d && f.matrix_3d.mood === state.personality;
      });
    }

    // Quick Pills filter
    if (state.pill && state.pill !== 'all') {
      if (state.pill === 'top20') {
        pool = pool.slice(0, 20);
      } else if (state.pill === 'hot20') {
        pool = pool.slice(4, 24);
      } else if (state.pill === 'variable') {
        pool = pool.filter(function (f) { return f.is_variable || (f.weights && f.weights.length >= 6); });
      } else if (state.pill === 'originals') {
        pool = pool.filter(function (f) { return (f.designer && f.designer.includes('Indian Type Foundry')) || (f.tags && f.tags.includes('GT Font')); });
      } else if (state.pill === 'shortlisted') {
        var favs = getFavorites();
        pool = pool.filter(function (f) { return favs.indexOf(f.id) !== -1; });
      }
    }

    // Sort control
    if (state.sort === 'alphabetical') {
      pool.sort(function (a, b) { return a.name.localeCompare(b.name); });
    } else if (state.sort === 'new') {
      pool.sort(function (a, b) { return (b.files_count || 1) - (a.files_count || 1); });
    }

    // Update counter display in toolbar
    if (DOM.fsTotalCount) DOM.fsTotalCount.textContent = pool.length;
    if (DOM.fsFontsCount) DOM.fsFontsCount.textContent = pool.length;

    DOM.fontshareGrid.className = 'fontshare-specimens-container ' + (state.viewMode === 'grid' ? 'fontshare-grid-mode' : 'fontshare-list-mode');

    // Reset pagination state
    DOM.fontshareGrid.innerHTML = '';
    App.fontsharePagination = {
      pool: pool,
      renderedCount: 0,
      batchSize: 30,
      isLoading: false
    };

    if (pool.length === 0) {
      DOM.fontshareGrid.innerHTML = '<div style="padding: 60px; text-align: center; color: var(--fontshare-muted); font-size: 1.1rem;">' +
        'No fonts match the selected criteria. Try resetting filters.</div>';
      updateFontshareSentinel(false);
      return;
    }

    // Smooth scroll back to top if filter/search changed
    if (options && options.scrollToTop) {
      var topPos = DOM.fontshareGrid.getBoundingClientRect().top + window.pageYOffset - 120;
      if (window.scrollY > topPos + 100) {
        window.scrollTo({ top: Math.max(0, topPos), behavior: 'smooth' });
      }
    }

    // Render initial batch (30 fonts)
    appendFontshareBatch();
  }

  function initFontshareInfiniteScroll() {
    if (!DOM.fontshareSentinel) {
      DOM.fontshareSentinel = document.getElementById('fontshare-scroll-sentinel');
    }
    if (!DOM.fontshareEndMessage) {
      DOM.fontshareEndMessage = document.getElementById('fontshare-end-message');
    }
    if (!DOM.fsEndCount) {
      DOM.fsEndCount = document.getElementById('fs-end-count');
    }

    // Create sentinel element if missing in DOM
    if (!DOM.fontshareSentinel && DOM.fontshareGrid) {
      var sentinel = document.createElement('div');
      sentinel.id = 'fontshare-scroll-sentinel';
      sentinel.className = 'fontshare-sentinel';
      sentinel.setAttribute('aria-hidden', 'true');
      sentinel.innerHTML = '<div class="fontshare-loading-spinner"></div><span class="fontshare-loading-text">Đang tải thêm font...</span>';
      sentinel.style.display = 'none';
      DOM.fontshareGrid.parentNode.insertBefore(sentinel, DOM.fontshareGrid.nextSibling);
      DOM.fontshareSentinel = sentinel;
    }

    // Create end message if missing in DOM
    if (!DOM.fontshareEndMessage && DOM.fontshareGrid) {
      var endMsg = document.createElement('div');
      endMsg.id = 'fontshare-end-message';
      endMsg.className = 'fontshare-end-message';
      endMsg.innerHTML = '<div class="fs-end-badge">✦ ĐÃ HIỂN THỊ TOÀN BỘ <span id="fs-end-count">0</span> HỌ FONT ✦</div>';
      endMsg.style.display = 'none';
      if (DOM.fontshareSentinel) {
        DOM.fontshareSentinel.parentNode.insertBefore(endMsg, DOM.fontshareSentinel.nextSibling);
      } else {
        DOM.fontshareGrid.parentNode.insertBefore(endMsg, DOM.fontshareGrid.nextSibling);
      }
      DOM.fontshareEndMessage = endMsg;
      DOM.fsEndCount = document.getElementById('fs-end-count');
    }

    // IntersectionObserver with 400px bottom preloading rootMargin
    if ('IntersectionObserver' in window) {
      if (App.fontshareObserver) {
        App.fontshareObserver.disconnect();
      }
      App.fontshareObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            if (App.currentView === 'fontshare' && App.fontsharePagination && App.fontsharePagination.renderedCount < App.fontsharePagination.pool.length) {
              appendFontshareBatch();
            }
          }
        });
      }, {
        root: null,
        rootMargin: '400px 0px',
        threshold: 0.01
      });

      if (DOM.fontshareSentinel) {
        App.fontshareObserver.observe(DOM.fontshareSentinel);
      }
    }

    // Window scroll fallback listener
    window.addEventListener('scroll', function () {
      if (App.currentView !== 'fontshare') return;
      if (!App.fontsharePagination || App.fontsharePagination.isLoading) return;
      if (App.fontsharePagination.renderedCount >= App.fontsharePagination.pool.length) return;

      var sentinel = DOM.fontshareSentinel;
      if (!sentinel) return;

      var rect = sentinel.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight;
      if (rect.top <= vh + 500) {
        appendFontshareBatch();
      }
    }, { passive: true });
  }

  function initFontshareEvents() {
    // Delegated click listener on #fontshare-grid (Card buttons work on initial + dynamically loaded cards)
    if (DOM.fontshareGrid) {
      DOM.fontshareGrid.addEventListener('click', function (e) {
        // 1. Toggle Waterfall drawer (via button or styles badge)
        var waterfallBtn = e.target.closest('[data-action="toggle-waterfall"], [data-action-card="toggle-card-waterfall"], .fs-btn-waterfall-toggle, .fs-styles-badge, .card-styles-toggle');
        if (waterfallBtn) {
          e.preventDefault();
          var card = waterfallBtn.closest('.fontshare-card');
          if (!card) return;
          var waterfall = card.querySelector('.fs-waterfall-drawer, .card-waterfall-drawer');
          if (waterfall) {
            var isHidden = waterfall.style.display === 'none' || getComputedStyle(waterfall).display === 'none';
            waterfall.style.display = isHidden ? 'block' : 'none';
            waterfallBtn.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
            var actionBtn = card.querySelector('.fs-btn-waterfall-toggle');
            if (actionBtn) actionBtn.textContent = isHidden ? 'Ẩn Waterfall ▴' : 'Waterfall ▾';
          }
          return;
        }

        // 2. Open Glyph modal
        var glyphBtn = e.target.closest('.btn-glyph-trigger');
        if (glyphBtn) {
          e.preventDefault();
          var fontId = glyphBtn.getAttribute('data-glyph-font-id');
          var target = (App.fontsharePagination && App.fontsharePagination.pool.find(function (f) { return f.id === fontId; })) ||
                       App.allFonts.find(function (f) { return f.id === fontId; });
          if (target) openGlyphModal(target);
          return;
        }

        // 3. Favorite button
        var favBtn = e.target.closest('.fs-star-btn');
        if (favBtn) {
          e.preventDefault();
          var fontId = favBtn.getAttribute('data-fav-id');
          var isFav = toggleFontFavorite(fontId);
          favBtn.classList.toggle('active', isFav);
          favBtn.textContent = isFav ? '★' : '☆';
          return;
        }

        // 4. Waterfall row click on Fontshare card
        var row = e.target.closest('.card-waterfall-row, .waterfall-row');
        if (row && !e.target.closest('.waterfall-text') && !e.target.closest('input')) {
          var card = row.closest('.fontshare-card');
          if (!card) return;
          var weightName = row.getAttribute('data-weight');
          var family = card.getAttribute('data-family');
          var fontId = card.getAttribute('data-font-id');
          var fontObj = (App.fontsharePagination && App.fontsharePagination.pool.find(function (f) { return f.id === fontId; })) ||
                       App.allFonts.find(function (f) { return f.id === fontId || (f.family || f.name) === family; });
          var category = (fontObj && fontObj.category) || 'Sans Serif';
          var files = fontObj ? fontObj.files : [];
          var numW = 400;

          if (weightName) {
            var resolved = resolveVariantStyle(family, weightName, category, files);
            numW = parseInt(resolved.fontWeight, 10) || 400;
          } else {
            var tag = row.querySelector('.waterfall-weight-tag');
            if (tag && tag.textContent) {
              numW = parseInt(tag.textContent, 10) || 400;
            }
          }

          var specimen = card.querySelector('.fs-item-specimen') || card.querySelector('.preview-text');
          if (specimen) {
            var fallback = (category && category.toLowerCase().includes('serif') && !category.toLowerCase().includes('sans')) ? 'serif' : 'sans-serif';
            specimen.style.fontWeight = numW;
            specimen.style.fontFamily = "'" + family + "', '" + family.replace(/\s+/g, '') + "', " + fallback;
            if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
              document.fonts.load(numW + ' 36px "' + family + '"');
            }
          }

          var slider = card.querySelector('.card-weight-slider');
          if (slider) slider.value = numW;
          var readout = card.querySelector('.fs-weight-val, .card-weight-val');
          if (readout) readout.textContent = numW;

          card.querySelectorAll('.card-waterfall-row, .waterfall-row').forEach(function (r) {
            r.classList.toggle('is-active', r === row);
          });
          return;
        }
      });

      // Delegated input listener on #fontshare-grid (Card weight slider works on dynamically loaded cards)
      DOM.fontshareGrid.addEventListener('input', function (e) {
        var weightSlider = e.target.closest('.card-weight-slider');
        if (weightSlider) {
          var card = weightSlider.closest('.fontshare-card');
          if (!card) return;
          var val = parseInt(weightSlider.value, 10);
          var specimen = card.querySelector('.fs-item-specimen') || card.querySelector('.preview-text');
          var family = card.getAttribute('data-family');
          var fontId = card.getAttribute('data-font-id');
          var fontObj = (App.fontsharePagination && App.fontsharePagination.pool.find(function (f) { return f.id === fontId; })) ||
                       App.allFonts.find(function (f) { return f.id === fontId || (f.family || f.name) === family; });
          var category = (fontObj && fontObj.category) || 'Sans Serif';
          var fallback = (category && category.toLowerCase().includes('serif') && !category.toLowerCase().includes('sans')) ? 'serif' : 'sans-serif';

          if (specimen) {
            specimen.style.fontWeight = val;
            specimen.style.fontFamily = "'" + family + "', '" + family.replace(/\s+/g, '') + "', " + fallback;
            if (fontObj && (fontObj.is_variable || (fontObj.weights && fontObj.weights.length >= 6))) {
              specimen.style.fontVariationSettings = "'wght' " + val;
            }
          }
          var readout = card.querySelector('.fs-weight-val, .card-weight-val');
          if (readout) {
            readout.textContent = val;
          }

          if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
            document.fonts.load(val + ' 36px "' + family + '"');
          }

          // Sync waterfall active row
          var rows = card.querySelectorAll('.card-waterfall-row, .waterfall-row');
          var minDiff = 9999;
          var closestRow = null;
          rows.forEach(function (r) {
            var tag = r.querySelector('.waterfall-weight-tag');
            if (tag && tag.textContent) {
              var rw = parseInt(tag.textContent, 10);
              if (!isNaN(rw)) {
                var d = Math.abs(rw - val);
                if (d < minDiff) {
                  minDiff = d;
                  closestRow = r;
                }
              }
            }
          });
          if (closestRow) {
            rows.forEach(function (r) { r.classList.toggle('is-active', r === closestRow); });
          }
        }
      });

      // Delegated change listener on #fontshare-grid for completeness
      DOM.fontshareGrid.addEventListener('change', function (e) {
        var weightSlider = e.target.closest('.card-weight-slider');
        if (weightSlider) {
          var card = weightSlider.closest('.fontshare-card');
          if (!card) return;
          var val = parseInt(weightSlider.value, 10);
          var specimen = card.querySelector('.fs-item-specimen') || card.querySelector('.preview-text');
          var family = card.getAttribute('data-family');
          var fontId = card.getAttribute('data-font-id');
          var fontObj = (App.fontsharePagination && App.fontsharePagination.pool.find(function (f) { return f.id === fontId; })) ||
                       App.allFonts.find(function (f) { return f.id === fontId || (f.family || f.name) === family; });
          var category = (fontObj && fontObj.category) || 'Sans Serif';
          var fallback = (category && category.toLowerCase().includes('serif') && !category.toLowerCase().includes('sans')) ? 'serif' : 'sans-serif';

          if (specimen) {
            specimen.style.fontWeight = val;
            specimen.style.fontFamily = "'" + family + "', '" + family.replace(/\s+/g, '') + "', " + fallback;
            if (fontObj && (fontObj.is_variable || (fontObj.weights && fontObj.weights.length >= 6))) {
              specimen.style.fontVariationSettings = "'wght' " + val;
            }
          }
          var readout = card.querySelector('.fs-weight-val, .card-weight-val');
          if (readout) {
            readout.textContent = val;
          }

          if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
            document.fonts.load(val + ' 36px "' + family + '"');
          }
        }
      });
    }

    // 1. Search input
    if (DOM.fontshareSearch) {
      DOM.fontshareSearch.addEventListener('input', function () {
        renderFontshareView({ scrollToTop: true });
      });
    }

    // 2. Shuffle button
    if (DOM.fontshareShuffleBtn) {
      DOM.fontshareShuffleBtn.addEventListener('click', function () {
        App.allFonts.sort(function () { return 0.5 - Math.random(); });
        renderFontshareView({ scrollToTop: true });
        showToast('Đã xáo trộn danh sách font!');
      });
    }

    // 3. Dropdowns
    if (DOM.fsFilterCategory) {
      DOM.fsFilterCategory.addEventListener('change', function (e) {
        App.fontshareState.category = e.target.value;
        renderFontshareView({ scrollToTop: true });
      });
    }
    if (DOM.fsFilterProperty) {
      DOM.fsFilterProperty.addEventListener('change', function (e) {
        App.fontshareState.property = e.target.value;
        renderFontshareView({ scrollToTop: true });
      });
    }
    if (DOM.fsFilterPersonality) {
      DOM.fsFilterPersonality.addEventListener('change', function (e) {
        App.fontshareState.personality = e.target.value;
        renderFontshareView({ scrollToTop: true });
      });
    }

    // 4. Size slider
    if (DOM.fsSizeSlider) {
      DOM.fsSizeSlider.addEventListener('input', function (e) {
        var size = parseInt(e.target.value, 10);
        App.fontshareState.size = size;
        if (DOM.fsSizeReadout) DOM.fsSizeReadout.textContent = size + 'px ◂';
        var specimens = document.querySelectorAll('.fs-item-specimen');
        specimens.forEach(function (el) {
          el.style.fontSize = size + 'px';
        });
      });
    }

    // 5. Custom text input (Your Text)
    if (DOM.fsCustomTextInput) {
      DOM.fsCustomTextInput.addEventListener('input', function (e) {
        var text = e.target.value;
        App.fontshareState.text = text;
        if (text.trim()) {
          DOM.fsPresetBtns.forEach(function (b) { b.classList.remove('active'); });
        }
        var specimens = document.querySelectorAll('.fs-item-specimen');
        specimens.forEach(function (el) {
          var card = el.closest('.fontshare-card');
          var name = card ? (card.querySelector('.fs-item-name') ? card.querySelector('.fs-item-name').textContent : '') : '';
          el.textContent = text.trim() ? text : name;
        });
      });
    }

    // 6. Presets (Cities, Excerpts, Names)
    if (DOM.fsPresetBtns) {
      DOM.fsPresetBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          DOM.fsPresetBtns.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          var preset = btn.getAttribute('data-preset');
          App.fontshareState.preset = preset;
          App.fontshareState.text = '';
          if (DOM.fsCustomTextInput) DOM.fsCustomTextInput.value = '';
          renderFontshareView({ scrollToTop: true });
        });
      });
    }

    // 7. Alignment buttons
    if (DOM.fsAlignBtns) {
      DOM.fsAlignBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          DOM.fsAlignBtns.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          var align = btn.getAttribute('data-fs-align') || 'left';
          App.fontshareState.align = align;
          var specimens = document.querySelectorAll('.fs-item-specimen');
          specimens.forEach(function (el) {
            el.style.textAlign = align;
          });
        });
      });
    }

    // 8. Theme toggle
    if (DOM.fsThemeToggle) {
      DOM.fsThemeToggle.addEventListener('click', function () {
        var currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        var nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(nextTheme);
        showToast('Giao diện: ' + (nextTheme === 'dark' ? 'Dark Mode' : 'Light Mode'));
      });
    }

    // 9. Reset All button
    if (DOM.fsResetBtn) {
      DOM.fsResetBtn.addEventListener('click', function () {
        App.fontshareState = {
          size: 210,
          text: '',
          preset: 'names',
          align: 'left',
          viewMode: 'list',
          category: 'all',
          property: 'all',
          personality: 'all',
          pill: 'all',
          sort: 'popular'
        };
        if (DOM.fontshareSearch) DOM.fontshareSearch.value = '';
        if (DOM.fsCustomTextInput) DOM.fsCustomTextInput.value = '';
        if (DOM.fsSizeSlider) DOM.fsSizeSlider.value = 210;
        if (DOM.fsSizeReadout) DOM.fsSizeReadout.textContent = '210px ◂';
        if (DOM.fsFilterCategory) DOM.fsFilterCategory.value = 'all';
        if (DOM.fsFilterProperty) DOM.fsFilterProperty.value = 'all';
        if (DOM.fsFilterPersonality) DOM.fsFilterPersonality.value = 'all';
        DOM.fsPresetBtns.forEach(function (b) {
          b.classList.toggle('active', b.getAttribute('data-preset') === 'names');
        });
        DOM.fsAlignBtns.forEach(function (b) {
          b.classList.toggle('active', b.getAttribute('data-fs-align') === 'left');
        });
        DOM.fsViewModeBtns.forEach(function (b) {
          b.classList.toggle('active', b.getAttribute('data-fs-view') === 'list');
        });
        DOM.fsPillBtns.forEach(function (b) {
          b.classList.toggle('active', b.getAttribute('data-pill') === 'all');
        });
        DOM.fsSortBtns.forEach(function (b) {
          b.classList.toggle('active', b.getAttribute('data-sort') === 'popular');
        });
        renderFontshareView({ scrollToTop: true });
        showToast('Đã đặt lại bộ lọc Fontshare!');
      });
    }

    // 10. View Mode (List vs Grid)
    if (DOM.fsViewModeBtns) {
      DOM.fsViewModeBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          DOM.fsViewModeBtns.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          var view = btn.getAttribute('data-fs-view') || 'list';
          App.fontshareState.viewMode = view;
          renderFontshareView();
        });
      });
    }

    // 11. Filter pills
    if (DOM.fsPillBtns) {
      DOM.fsPillBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          DOM.fsPillBtns.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          var pill = btn.getAttribute('data-pill') || 'all';
          App.fontshareState.pill = pill;
          renderFontshareView({ scrollToTop: true });
        });
      });
    }

    // 12. Sort control
    if (DOM.fsSortBtns) {
      DOM.fsSortBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          DOM.fsSortBtns.forEach(function (b) { b.classList.remove('active'); });
          btn.classList.add('active');
          var sort = btn.getAttribute('data-sort') || 'popular';
          App.fontshareState.sort = sort;
          renderFontshareView({ scrollToTop: true });
        });
      });
    }

    // 13. Topbar navigation tabs
    if (DOM.fsTabFonts) {
      DOM.fsTabFonts.addEventListener('click', function () {
        DOM.fsTabFonts.classList.add('active');
        if (DOM.fsTabPairs) DOM.fsTabPairs.classList.remove('active');
      });
    }
    if (DOM.fsTabPairs) {
      DOM.fsTabPairs.addEventListener('click', function () {
        switchView('pair');
      });
    }
    if (DOM.fsTabLicenses) {
      DOM.fsTabLicenses.addEventListener('click', function () {
        showToast('Fontshare & FEDU Fonts: 100% Free & Commercial Ready!');
      });
    }

    // 14. Scroll to top button
    if (DOM.fsScrollTopBtn) {
      DOM.fsScrollTopBtn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
      window.addEventListener('scroll', function () {
        if (window.scrollY > 400) {
          DOM.fsScrollTopBtn.style.display = 'flex';
        } else {
          DOM.fsScrollTopBtn.style.display = 'none';
        }
      });
    }
  }

  /* ==========================================================================
     FONT PAIRING CONTROLLER (Dual-Font Playground + Accordion + 8 Boards)
     ========================================================================== */

  var CURATED_PAIRS = [
    {
      id: 'pair-1-luxury',
      style: 'Luxury & Thời Trang',
      headingFamily: 'FD NoeDisplay',
      headingCategory: 'Serif (Editorial Display)',
      bodyFamily: 'FD Aeonik',
      bodyCategory: 'Sans Serif (Geometric Clean)',
      headline: 'Nghệ Thuật Chế Tác Thượng Đẳng & Tinh Thần Đương Đại',
      subhead: 'Tương phản đỉnh cao giữa nét thanh đậm kịch tính của Serif và nhịp điệu phẳng tối giản của Sans Serif.',
      paragraph: 'Trong thế giới của sự xa hoa thầm lặng, từng đường cong và tỉ lệ hình học của con chữ phản chiếu triết lý tối giản vượt thời gian. Nét thanh mảnh của serif cổ điển khi song hành cùng sans hiện đại tạo nên chuẩn mực thị giác không thể hòa lẫn.',
      rationale: 'Serif kịch tính tạo điểm nhấn độc tôn giật tít, trong khi Sans hình học đảm bảo khối văn bản trong suốt, êm mắt khi đọc lướt.'
    },
    {
      id: 'pair-2-tech',
      style: 'Công Nghệ & Giao Diện Số',
      headingFamily: 'GR Sectra',
      headingCategory: 'Display Sharp Contemporary',
      bodyFamily: 'FD Gilroy',
      bodyCategory: 'Neo-Grotesk (UI Standard)',
      headline: 'Kiến Trúc Dữ Liệu & Kỷ Nguyên Trí Tuệ Nhân Tạo',
      subhead: 'Cặp đôi chuẩn mực Châu Âu hiện đại cho các sản phẩm công nghệ, SaaS và nền tảng số tiên phong.',
      paragraph: 'Giao diện sản phẩm số đòi hỏi tính chính xác tuyệt đối trong từng điểm ảnh. GR Sectra tạo ấn tượng thị giác dứt khoát ở tiêu đề, đồng hành cùng Gilroy dẫn dắt trải nghiệm đọc mượt mà qua hàng nghìn dòng dữ liệu và tài liệu kỹ thuật.',
      rationale: 'Năng lượng cơ học mạnh mẽ kết hợp cùng độ thoáng của x-height cao, chống mỏi mắt trên màn hình Retina.'
    },
    {
      id: 'pair-3-journal',
      style: 'Báo Chí & Tạp Chí Tri Thức',
      headingFamily: 'FD Adobe Caslon',
      headingCategory: 'Oldstyle Serif (Venetian Heritage)',
      bodyFamily: 'FD Apercu Pro',
      bodyCategory: 'Humanist Sans (Warm Modern)',
      headline: 'Dòng Chảy Văn Hóa & Nghệ Thuật Chữ Đồ Họa Việt',
      subhead: 'Âm hưởng học thuật trang trọng, bề thế dung hòa hoàn hảo cùng nét chữ không chân nhân văn, gần gũi.',
      paragraph: 'Một bài xã luận học thuật cần âm hưởng điềm đạm, trang trọng. Chân chữ cổ điển của Caslon tạo niềm tin vững chãi qua hàng thế kỷ, được làm tươi mới bởi nét chữ không chân Apercu Pro mềm mại, thanh thoát và tràn đầy năng lượng nhân văn.',
      rationale: 'Chân chữ cổ điển uy tín kết hợp nét chữ không chân hiện đại, duy trì độ tập trung tối đa cho người đọc văn học.'
    },
    {
      id: 'pair-4-brand',
      style: 'Tuyên Ngôn Thương Hiệu Đột Phá',
      headingFamily: 'FD Abril Fatface',
      headingCategory: 'Didone Display (Ultra Bold)',
      bodyFamily: 'FD Aptima',
      bodyCategory: 'Humanist Sans (Balanced Contrast)',
      headline: 'Định Hình Tương Lai Bằng Những Ý Tưởng Táo Bạo',
      subhead: 'Cú hích thị giác đầy uy lực ở tiêu đề được cân bằng bởi khối thân bài nhẹ nhàng, minh bạch.',
      paragraph: 'Khi thương hiệu cần một tuyên ngôn trực diện, Abril Fatface lập tức chiếm lĩnh toàn bộ không gian thị giác với độ tương phản cực đại. Aptima ở thân bài đóng vai trò điểm tựa trung tính, thanh khiết và chân phương, truyền tải trọn vẹn thông điệp.',
      rationale: 'Tương phản cực đoan (Maximum Contrast) giữa Display siêu đậm và Body thanh mảnh, tạo dấu ấn thị giác khó phai.'
    },
    {
      id: 'pair-5-vintage',
      style: 'Hoài Niệm Sài Gòn & Di Sản Phố Phường',
      headingFamily: 'FD HC Bourbon Grotesque',
      headingCategory: 'Vintage Display (Heritage)',
      bodyFamily: 'FD Acta',
      bodyCategory: 'Humanist Sans (Editorial Warm)',
      headline: 'Góc Phố Rêu Phong & Ký Ức Bảng Hiệu Sài Gòn Xưa',
      subhead: 'Khơi gợi phong vị hào sảng của các bảng hiệu vẽ tay thập niên 70 trong một bố cục hiện đại tinh tế.',
      paragraph: 'Những nét chữ vẽ tay hào sảng của Sài Gòn thập niên trước đem lại rung cảm hoài niệm thân thương. Acta ở phần thân bài nâng niu từng dòng hồi ức một cách tao nhã, ấm áp và thanh lịch, giữ trọn thanh âm bình dị của người Việt.',
      rationale: 'Gợi không khí hoài niệm của phố phường xưa nhưng văn bản vẫn thoáng đãng, ấm áp và sang trọng.'
    },
    {
      id: 'pair-6-publishing',
      style: 'Ấn Phẩm Sách & Văn Học Dài Kỳ',
      headingFamily: 'FD Adobe Jenson',
      headingCategory: 'Venetian Oldstyle (Renaissance)',
      bodyFamily: 'FD A Love Of Thunder',
      bodyCategory: 'Humanist Sans (Friendly Soft)',
      headline: 'Hương Thơm Của Giấy Mộc & Tình Yêu Với Sách',
      subhead: 'Bộ đôi truyền thống bảo vệ mắt tối ưu, mang vẻ đẹp hoài cổ của những trang bản thảo kinh điển.',
      paragraph: 'Đọc sách là hành trình nuôi dưỡng tâm hồn. Adobe Jenson mang vẻ đẹp thủ bản thời Phục Hưng với trục nghiêng mềm mại, kết hợp hài hòa cùng A Love Of Thunder phóng khoáng, giúp người đọc đắm chìm trong từng trang truyện dài.',
      rationale: 'Nét chữ giàu cảm xúc nhân văn, trục nghiêng hữu cơ tự nhiên, bảo vệ thị giác khi đọc các tác phẩm dài kỳ.'
    },
    {
      id: 'pair-7-nordic',
      style: 'Tối Giản Bắc Âu (Nordic Minimal — Đảo Ngược)',
      headingFamily: 'FD Aguila',
      headingCategory: 'Geometric Sans (Clean Modern)',
      bodyFamily: 'FD Addington CF',
      bodyCategory: 'Book Serif (Warm & Elegant)',
      headline: 'Vẻ Đẹp Thuần Khiết Của Công Năng & Ánh Sáng',
      subhead: 'Phá cách bằng việc đảo ngược truyền thống: Tiêu đề hình học sắc gọn, thân bài có chân ấm cúng.',
      paragraph: 'Táo bạo khi đảo ngược cấu trúc truyền thống: Tiêu đề phẳng và dứt khoát như kiến trúc bê tông trần Bắc Âu, trong khi đoạn văn thân bài lại nồng ấm, thân mật với các chân chữ uốn cong nhẹ nhàng của Addington CF, tạo nên sự giao thoa thị giác bất ngờ.',
      rationale: 'Đảo ngược vai trò: Tiêu đề dứt khoát hiện đại, thân bài có chân ấm áp, tạo nhịp điệu đọc mới mẻ.'
    },
    {
      id: 'pair-8-creative',
      style: 'Sáng Tạo & Cảm Xúc Nghệ Thuật',
      headingFamily: 'FD Recoleta',
      headingCategory: 'Soft Organic Serif (Playful)',
      bodyFamily: 'GR Alpina',
      bodyCategory: 'Modern Serif/Sans Hybrid',
      headline: 'Khơi Nguồn Cảm Hứng Từ Những Điều Giản Dị Nhất',
      subhead: 'Đường cong hữu cơ đầy cảm xúc hòa quyện cùng phong cách thiết kế đương đại của thế hệ sáng tạo trẻ.',
      paragraph: 'Đường cong tròn đầy đặn của Recoleta mang đến nguồn năng lượng vui tươi, ấm áp và giàu tính nghệ thuật. Khi kết hợp cùng sự chuẩn mực thanh nhã của Alpina, tổ hợp tạo nên bản sắc độc đáo cho các ấn phẩm sáng tạo và thương hiệu phong cách sống.',
      rationale: 'Đường cong mềm mại ở tiêu đề đem lại cảm giác thân thiện, độc đáo, kích thích tư duy nghệ thuật.'
    }
  ];

  function initPairView() {
    if (!DOM.pairHeadingSelect || !DOM.pairBodySelect) return;

    // Populate selects if empty
    if (DOM.pairHeadingSelect.options.length === 0) {
      populatePairSelects();
    }

    // Set initial pair if not set
    if (!App.pairState.headingFont || !App.pairState.bodyFont) {
      var defaultHeading = App.allFonts.find(function (f) {
        return f.name === 'FD NoeDisplay' || f.name === 'FD Adobe Caslon' || f.name === 'GR Pantheon' ||
          (f.category && f.category.indexOf('Serif') !== -1 && f.category.indexOf('Sans') === -1);
      });
      var defaultBody = App.allFonts.find(function (f) {
        return f.name === 'FD Aeonik' || f.name === 'FDAeonik' || f.name === 'FD Gilroy' || f.name === 'FD Aptima' ||
          (f.category && f.category.indexOf('Sans') !== -1);
      });

      App.pairState.headingFont = defaultHeading || App.allFonts[0];
      App.pairState.bodyFont = defaultBody || App.allFonts[1] || App.allFonts[0];

      if (App.pairState.headingFont && DOM.pairHeadingSelect) DOM.pairHeadingSelect.value = App.pairState.headingFont.id;
      if (App.pairState.bodyFont && DOM.pairBodySelect) DOM.pairBodySelect.value = App.pairState.bodyFont.id;
    }

    updatePairArticle();
    updatePairAccordion();
    renderCuratedPairs();
  }

  function populatePairSelects() {
    DOM.pairHeadingSelect.innerHTML = '';
    DOM.pairBodySelect.innerHTML = '';

    var serifs = [];
    var sans = [];
    var others = [];

    App.allFonts.forEach(function (f) {
      var cat = (f.category || '').toLowerCase();
      if (cat.indexOf('serif') !== -1 && cat.indexOf('sans') === -1) {
        serifs.push(f);
      } else if (cat.indexOf('sans') !== -1) {
        sans.push(f);
      } else {
        others.push(f);
      }
    });

    function appendGroup(select, label, fontList) {
      var optgroup = document.createElement('optgroup');
      optgroup.label = label;
      fontList.forEach(function (f) {
        var opt = document.createElement('option');
        opt.value = f.id;
        opt.textContent = f.name + ' (' + (f.category || 'Font') + ')';
        optgroup.appendChild(opt);
      });
      select.appendChild(optgroup);
    }

    // For Heading: recommend Serifs first
    appendGroup(DOM.pairHeadingSelect, '★ Khuyên dùng cho Tiêu đề: Serif (Có chân)', serifs);
    appendGroup(DOM.pairHeadingSelect, 'Sans Serif (Không chân)', sans);
    appendGroup(DOM.pairHeadingSelect, 'Display, Vintage & Script', others);

    // For Body: recommend Sans first
    appendGroup(DOM.pairBodySelect, '★ Khuyên dùng cho Thân bài: Sans Serif (Không chân)', sans);
    appendGroup(DOM.pairBodySelect, 'Serif (Có chân)', serifs);
    appendGroup(DOM.pairBodySelect, 'Display, Vintage & Script', others);
  }

  function updatePairArticle() {
    var headingFont = App.pairState.headingFont;
    var bodyFont = App.pairState.bodyFont;

    if (!headingFont || !bodyFont) return;

    // Load web fonts
    if (headingFont.web_font_url) App.typeTester.loadWebFont(headingFont.family || headingFont.name, headingFont.web_font_url);
    if (bodyFont.web_font_url) App.typeTester.loadWebFont(bodyFont.family || bodyFont.name, bodyFont.web_font_url);

    var hFamily = headingFont.family || headingFont.name;
    var bFamily = bodyFont.family || bodyFont.name;

    if (DOM.pairPreviewHeading) {
      DOM.pairPreviewHeading.style.fontFamily = '\'' + hFamily + '\', serif';
      DOM.pairPreviewHeading.style.fontSize = App.pairState.headingSize + 'px';
      DOM.pairPreviewHeading.style.letterSpacing = App.pairState.kerning + 'em';
    }

    if (DOM.pairPreviewSubhead) {
      DOM.pairPreviewSubhead.style.fontFamily = '\'' + bFamily + '\', sans-serif';
      DOM.pairPreviewSubhead.style.letterSpacing = App.pairState.kerning + 'em';
    }

    if (DOM.pairPreviewBody) {
      DOM.pairPreviewBody.style.fontFamily = '\'' + bFamily + '\', sans-serif';
      DOM.pairPreviewBody.style.fontSize = App.pairState.bodySize + 'px';
      DOM.pairPreviewBody.style.lineHeight = App.pairState.lineHeight;
      DOM.pairPreviewBody.style.letterSpacing = App.pairState.kerning + 'em';
    }

    // Update download link
    if (DOM.pairDownloadBothBtn) {
      DOM.pairDownloadBothBtn.href = headingFont.drive_download_url || headingFont.drive_view_url || headingFont.drive_folder_url || 'https://drive.google.com/drive/folders/1vybz5LwFasmy9kRGBVcX3tX6vYfEoi9j?usp=sharing';
      DOM.pairDownloadBothBtn.title = 'Tải ' + headingFont.name + ' và ' + bodyFont.name;
    }
  }

  function updatePairAccordion() {
    if (!DOM.pairingAccordionContent) return;

    var h = App.pairState.headingFont;
    var b = App.pairState.bodyFont;
    if (!h || !b) return;

    var hCat = h.category || 'Serif';
    var bCat = b.category || 'Sans Serif';
    var isSerifHeading = (hCat.toLowerCase().indexOf('serif') !== -1 && hCat.toLowerCase().indexOf('sans') === -1);
    var isSansBody = (bCat.toLowerCase().indexOf('sans') !== -1);

    var contrastNote = '';
    if (isSerifHeading && isSansBody) {
      contrastNote = 'Đây là <strong>chuẩn mực phối font kinh điển (Gold Standard)</strong>: Font có chân ' + escapeHTML(h.name) + ' đóng vai trò điểm neo thị giác đầy uy quyền cho tiêu đề, còn font không chân ' + escapeHTML(b.name) + ' với x-height thoáng và nét đều mang lại trải nghiệm đọc thân bài mượt mà, chống mỏi mắt.';
    } else if (!isSerifHeading && !isSansBody) {
      contrastNote = '<strong>Phá cách hiện đại (Reverse Pairing)</strong>: Tiêu đề dùng font không chân ' + escapeHTML(h.name) + ' tạo cảm giác dứt khoát, tối giản, kết hợp thân bài có chân ' + escapeHTML(b.name) + ' mang âm hưởng ấm cúng, sang trọng như sách in thủ bản.';
    } else {
      contrastNote = '<strong>Tổ hợp đồng điệu (Harmonic Pairing)</strong>: Hai họ font ' + escapeHTML(h.name) + ' và ' + escapeHTML(b.name) + ' bổ trợ lẫn nhau, tạo nên tính thống nhất cao trong ngôn ngữ thị giác.';
    }

    DOM.pairingAccordionContent.innerHTML = [
      '<div class="dynamic-analysis-box">',
      '  <div class="dynamic-analysis-title">',
      '    <span>✦ Đánh giá tổ hợp: ' + escapeHTML(h.name) + ' (Tiêu đề) + ' + escapeHTML(b.name) + ' (Thân bài)</span>',
      '  </div>',
      '  <div class="dynamic-analysis-text">' + contrastNote + '</div>',
      '</div>',
      '<div class="logic-cards-grid">',
      '  <div class="logic-card">',
      '    <span class="logic-card-tag">1. Tương Phản Hình Thái</span>',
      '    <h4 class="logic-card-title">Serif vs. Sans Serif</h4>',
      '    <p class="logic-card-desc">Chân chữ (serifs) và độ tương phản nét thanh/đậm tạo cảm xúc mạnh mẽ cho tiêu đề lớn. Nét chữ phẳng (sans) loại bỏ mọi chi tiết thừa, giúp mắt nhận diện nhanh các mặt chữ ở kích thước nhỏ (14-18px).</p>',
      '  </div>',
      '  <div class="logic-card">',
      '    <span class="logic-card-tag">2. Tỉ Lệ &amp; Nhịp Điệu</span>',
      '    <h4 class="logic-card-title">Cân Bằng X-Height &amp; Trục Đứng</h4>',
      '    <p class="logic-card-desc">Tỉ lệ chiều cao thân chữ thường (x-height) tương đương và trục đối xứng thẳng đứng (vertical stress) giúp ánh nhìn của độc giả chuyển mượt mà từ dòng tít giật xuống đoạn văn đầu tiên mà không bị gãy nhịp.</p>',
      '  </div>',
      '  <div class="logic-card">',
      '    <span class="logic-card-tag">3. Ngữ Cảnh Ứng Dụng</span>',
      '    <h4 class="logic-card-title">Nhận Diện &amp; Xuất Bản</h4>',
      '    <p class="logic-card-desc">Tối ưu cho thiết kế tạp chí editorial, website thương hiệu, trang đích (landing page) giáo dục và ấn phẩm truyền thông. Tiêu đề kể câu chuyện cảm xúc, thân bài truyền tải nội dung súc tích.</p>',
      '  </div>',
      '</div>'
    ].join('');
  }

  function renderCuratedPairs() {
    if (!DOM.curatedPairsGrid) return;

    DOM.curatedPairsGrid.innerHTML = CURATED_PAIRS.map(function (pair, idx) {
      var hFont = App.allFonts.find(function (f) { return f.name === pair.headingFamily; }) || { name: pair.headingFamily, drive_folder_url: '#' };
      var bFont = App.allFonts.find(function (f) { return f.name === pair.bodyFamily; }) || { name: pair.bodyFamily, drive_folder_url: '#' };

      if (hFont.web_font_url) App.typeTester.loadWebFont(hFont.family || hFont.name, hFont.web_font_url);
      if (bFont.web_font_url) App.typeTester.loadWebFont(bFont.family || bFont.name, bFont.web_font_url);

      var hFamily = hFont.family || hFont.name;
      var bFamily = bFont.family || bFont.name;
      var defaultPairDrive = 'https://drive.google.com/drive/folders/1vybz5LwFasmy9kRGBVcX3tX6vYfEoi9j?usp=sharing';
      var driveUrl = hFont.drive_download_url || hFont.drive_view_url || hFont.drive_folder_url || defaultPairDrive;

      return [
        '<article class="curated-card" data-pair-id="' + escapeHTML(pair.id) + '">',
        '  <div class="curated-card-top">',
        '    <div class="curated-card-badge-row">',
        '      <span class="curated-style-badge">#' + (idx + 1) + ' ' + escapeHTML(pair.style) + '</span>',
        '      <span class="curated-fonts-label">' + escapeHTML(pair.headingFamily) + ' + ' + escapeHTML(pair.bodyFamily) + '</span>',
        '    </div>',
        '    <div class="curated-specimen-box">',
        '      <div class="curated-headline" style="font-family: \'' + escapeHTML(hFamily) + '\', serif;">',
        '        ' + escapeHTML(pair.headline),
        '      </div>',
        '      <div class="curated-paragraph" style="font-family: \'' + escapeHTML(bFamily) + '\', sans-serif;">',
        '        ' + escapeHTML(pair.paragraph),
        '      </div>',
        '    </div>',
        '  </div>',
        '  <div class="curated-card-footer">',
        '    <button type="button" class="btn-apply-pair" data-load-pair="' + escapeHTML(pair.id) + '">',
        '      ✦ Thử trên Playground',
        '    </button>',
        '    <a href="' + driveUrl + '" class="btn-download-pair" target="_blank" rel="noopener noreferrer" title="Tải font">',
        '      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/></svg>',
        '      <span>Tải trọn bộ</span>',
        '    </a>',
        '  </div>',
        '</article>'
      ].join('');
    }).join('');

    // Attach "Apply to Playground" handlers
    DOM.curatedPairsGrid.querySelectorAll('[data-load-pair]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var pairId = btn.getAttribute('data-load-pair');
        applyCuratedPair(pairId);
      });
    });
  }

  function applyCuratedPair(pairId) {
    var pair = CURATED_PAIRS.find(function (p) { return p.id === pairId; });
    if (!pair) return;

    var hFont = App.allFonts.find(function (f) { return f.name === pair.headingFamily; });
    var bFont = App.allFonts.find(function (f) { return f.name === pair.bodyFamily; });

    if (hFont) {
      App.pairState.headingFont = hFont;
      if (DOM.pairHeadingSelect) DOM.pairHeadingSelect.value = hFont.id;
    }
    if (bFont) {
      App.pairState.bodyFont = bFont;
      if (DOM.pairBodySelect) DOM.pairBodySelect.value = bFont.id;
    }

    if (DOM.pairPreviewHeading) DOM.pairPreviewHeading.textContent = pair.headline;
    if (DOM.pairPreviewSubhead) DOM.pairPreviewSubhead.textContent = pair.subhead;
    if (DOM.pairPreviewBody) DOM.pairPreviewBody.innerHTML = '<p>' + escapeHTML(pair.paragraph) + '</p>';

    updatePairArticle();
    updatePairAccordion();

    // Scroll smoothly to playground
    if (DOM.pairView) {
      DOM.pairView.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    showToast('Đã nạp bảng phối mẫu: ' + pair.style);
  }

  function swapPairRoles() {
    var temp = App.pairState.headingFont;
    App.pairState.headingFont = App.pairState.bodyFont;
    App.pairState.bodyFont = temp;

    if (App.pairState.headingFont && DOM.pairHeadingSelect) {
      DOM.pairHeadingSelect.value = App.pairState.headingFont.id;
    }
    if (App.pairState.bodyFont && DOM.pairBodySelect) {
      DOM.pairBodySelect.value = App.pairState.bodyFont.id;
    }

    updatePairArticle();
    updatePairAccordion();
    showToast('Đã hoán đổi vai trò font Tiêu đề ⇄ Đoạn văn');
  }

  function randomizePair() {
    var serifs = App.allFonts.filter(function (f) {
      var cat = (f.category || '').toLowerCase();
      return cat.indexOf('serif') !== -1 && cat.indexOf('sans') === -1;
    });
    var sans = App.allFonts.filter(function (f) {
      var cat = (f.category || '').toLowerCase();
      return cat.indexOf('sans') !== -1;
    });

    if (serifs.length > 0) {
      var randSerif = serifs[Math.floor(Math.random() * serifs.length)];
      App.pairState.headingFont = randSerif;
      if (DOM.pairHeadingSelect) DOM.pairHeadingSelect.value = randSerif.id;
    }
    if (sans.length > 0) {
      var randSans = sans[Math.floor(Math.random() * sans.length)];
      App.pairState.bodyFont = randSans;
      if (DOM.pairBodySelect) DOM.pairBodySelect.value = randSans.id;
    }

    updatePairArticle();
    updatePairAccordion();
    showToast('Đã tạo cặp ngẫu nhiên: ' + App.pairState.headingFont.name + ' + ' + App.pairState.bodyFont.name);
  }

  /**
   * Initializes event listeners across all interactive controls.
   */
  function bindEvents() {
    // Multi-View switching
    if (DOM.viewBtns) {
      DOM.viewBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          switchView(btn.getAttribute('data-view'));
        });
      });
    }

    // Fontshare View controls (Image 4)
    initFontshareEvents();
    initFontshareInfiniteScroll();

    // Pair View font selectors & actions
    if (DOM.pairHeadingSelect) {
      DOM.pairHeadingSelect.addEventListener('change', function (e) {
        var found = App.allFonts.find(function (f) { return f.id === e.target.value; });
        if (found) {
          App.pairState.headingFont = found;
          updatePairArticle();
          updatePairAccordion();
        }
      });
    }
    if (DOM.pairBodySelect) {
      DOM.pairBodySelect.addEventListener('change', function (e) {
        var found = App.allFonts.find(function (f) { return f.id === e.target.value; });
        if (found) {
          App.pairState.bodyFont = found;
          updatePairArticle();
          updatePairAccordion();
        }
      });
    }
    if (DOM.pairSwapBtn) {
      DOM.pairSwapBtn.addEventListener('click', swapPairRoles);
    }
    if (DOM.pairRandomBtn) {
      DOM.pairRandomBtn.addEventListener('click', randomizePair);
    }

    // Pair Sliders
    if (DOM.pairHeadingSize) {
      DOM.pairHeadingSize.addEventListener('input', function (e) {
        App.pairState.headingSize = parseInt(e.target.value, 10);
        if (DOM.pairHeadingSizeVal) DOM.pairHeadingSizeVal.textContent = e.target.value + 'px';
        updatePairArticle();
      });
    }
    if (DOM.pairBodySize) {
      DOM.pairBodySize.addEventListener('input', function (e) {
        App.pairState.bodySize = parseInt(e.target.value, 10);
        if (DOM.pairBodySizeVal) DOM.pairBodySizeVal.textContent = e.target.value + 'px';
        updatePairArticle();
      });
    }
    if (DOM.pairLineHeight) {
      DOM.pairLineHeight.addEventListener('input', function (e) {
        App.pairState.lineHeight = parseFloat(e.target.value);
        if (DOM.pairLineHeightVal) DOM.pairLineHeightVal.textContent = parseFloat(e.target.value).toFixed(2);
        updatePairArticle();
      });
    }
    if (DOM.pairKerning) {
      DOM.pairKerning.addEventListener('input', function (e) {
        App.pairState.kerning = parseFloat(e.target.value);
        if (DOM.pairKerningVal) DOM.pairKerningVal.textContent = parseFloat(e.target.value).toFixed(2) + 'em';
        updatePairArticle();
      });
    }

    // Theme switching
    DOM.themeBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setTheme(btn.getAttribute('data-theme-set'));
      });
    });

    // Global text input with IME composition safety
    App.typeTester.bindIMEInput(DOM.globalTextInput, function (val) {
      broadcastPreviewText(val);
    });

    if (DOM.textClearBtn) {
      DOM.textClearBtn.addEventListener('click', function () {
        if (DOM.globalTextInput) {
          DOM.globalTextInput.value = '';
          broadcastPreviewText('');
          DOM.globalTextInput.focus();
        }
      });
    }

    // Preset quotes selector
    if (DOM.presetSelect) {
      DOM.presetSelect.addEventListener('change', function (e) {
        var val = e.target.value;
        if (val) {
          DOM.globalTextInput.value = val;
          broadcastPreviewText(val);
        }
      });
    }

    // Sliders
    if (DOM.fontSizeSlider) {
      DOM.fontSizeSlider.addEventListener('input', function (e) {
        setFontSize(e.target.value);
      });
    }

    if (DOM.lineHeightSlider) {
      DOM.lineHeightSlider.addEventListener('input', function (e) {
        setLineHeight(e.target.value);
      });
    }

    if (DOM.kerningSlider) {
      DOM.kerningSlider.addEventListener('input', function (e) {
        setKerning(e.target.value);
      });
    }

    // Align & Transform
    DOM.alignBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setTextAlign(btn.getAttribute('data-align'));
      });
    });

    DOM.transformBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setTextTransform(btn.getAttribute('data-transform'));
      });
    });

    if (DOM.btnResetTester) {
      DOM.btnResetTester.addEventListener('click', resetTypeTester);
    }

    // Search Input
    if (DOM.searchInput) {
      DOM.searchInput.addEventListener('input', function (e) {
        App.activeFilters.searchQuery = e.target.value;
        applyFilters();
      });
    }

    // Category Chips
    DOM.categoryChips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        DOM.categoryChips.forEach(function (c) { c.classList.remove('active'); });
        chip.classList.add('active');
        App.activeFilters.category = chip.getAttribute('data-category');
        applyFilters();
      });
    });

    // Secondary Filters
    if (DOM.filterStudio) {
      DOM.filterStudio.addEventListener('change', function (e) {
        var val = e.target.value;
        App.activeFilters.studio = val;
        App.fontshareState.studio = val;
        if (DOM.fsFilterStudio) DOM.fsFilterStudio.value = val;
        applyFilters();
        if (val !== 'all') {
          showToast('🏢 Đã gom nhóm font theo Studio: ' + val);
        }
      });
    }

    if (DOM.fsFilterStudio) {
      DOM.fsFilterStudio.addEventListener('change', function (e) {
        var val = e.target.value;
        App.fontshareState.studio = val;
        App.activeFilters.studio = val;
        if (DOM.filterStudio) DOM.filterStudio.value = val;
        renderFontshareView({ scrollToTop: true });
        applyFilters();
        if (val !== 'all') {
          showToast('🏢 Đã gom nhóm font theo Studio: ' + val);
        }
      });
    }

    // Global Click delegation for Studio badges on ANY card (.badge-studio, .fs-studio-badge, [data-studio])
    document.addEventListener('click', function (e) {
      var studioBtn = e.target.closest('.badge-studio, .fs-studio-badge, [data-studio]');
      if (studioBtn) {
        var studioName = studioBtn.getAttribute('data-studio');
        if (!studioName) return;
        e.preventDefault();
        e.stopPropagation();

        App.activeFilters.studio = studioName;
        App.fontshareState.studio = studioName;
        if (DOM.filterStudio) DOM.filterStudio.value = studioName;
        if (DOM.fsFilterStudio) DOM.fsFilterStudio.value = studioName;

        applyFilters();
        renderFontshareView({ scrollToTop: true });

        var targetSection = App.currentView === 'fontshare' ? DOM.fontshareView : DOM.fontGrid;
        if (targetSection) {
          targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        showToast('🏢 Đã gom nhóm font theo Studio: ' + studioName);
      }
    });

    if (DOM.filterMood) {
      DOM.filterMood.addEventListener('change', function (e) {
        App.activeFilters.mood = e.target.value;
        applyFilters();
      });
    }

    if (DOM.filterUseCase) {
      DOM.filterUseCase.addEventListener('change', function (e) {
        App.activeFilters.use_case = e.target.value;
        applyFilters();
      });
    }

    if (DOM.filterWeight) {
      DOM.filterWeight.addEventListener('change', function (e) {
        App.activeFilters.weight = e.target.value;
        applyFilters();
      });
    }

    if (DOM.filterVnSupport) {
      DOM.filterVnSupport.addEventListener('change', function (e) {
        App.activeFilters.vietnamese_support = e.target.checked ? true : null;
        applyFilters();
      });
    }

    if (DOM.btnClearFilters) {
      DOM.btnClearFilters.addEventListener('click', clearAllFilters);
    }

    if (DOM.emptyResetBtn) {
      DOM.emptyResetBtn.addEventListener('click', clearAllFilters);
    }

    // Modal
    if (DOM.glyphModalClose) {
      DOM.glyphModalClose.addEventListener('click', closeGlyphModal);
    }

    if (DOM.glyphModal) {
      DOM.glyphModal.addEventListener('click', function (e) {
        if (e.target === DOM.glyphModal) {
          closeGlyphModal();
        }
      });
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && DOM.glyphModal && DOM.glyphModal.classList.contains('open')) {
        closeGlyphModal();
      }
    });

    DOM.glyphModalTabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        DOM.glyphModalTabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        App.activeGlyphTab = tab.getAttribute('data-glyph-tab');
        renderModalGlyphs();
      });
    });

    // Setup Progressive Infinite Scroll via IntersectionObserver
    if (typeof IntersectionObserver !== 'undefined' && DOM.scrollSentinel) {
      App.intersectionObserver = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          var maxPage = Math.ceil(App.filteredFonts.length / App.pagination.pageSize);
          if (App.pagination.currentPage < maxPage) {
            App.pagination.currentPage++;
            renderGrid(true);
          }
        }
      }, {
        root: null,
        rootMargin: '300px',
        threshold: 0.05
      });

      App.intersectionObserver.observe(DOM.scrollSentinel);
    }
  }

  /**
   * Populates the Preset Quotes dropdown.
   */
  function populatePresets() {
    if (!DOM.presetSelect) return;
    var presets = App.typeTester.getPresetPhrases();
    presets.forEach(function (p) {
      var opt = document.createElement('option');
      opt.value = p.text;
      opt.textContent = p.label;
      DOM.presetSelect.appendChild(opt);
    });
  }

  /**
   * Main Application Entry Point
   */
  async function init() {
    cacheDOM();

    // Instantiate TypeTesterEngine
    App.typeTester = new TypeTester.TypeTesterEngine();

    // Check saved theme (default: light)
    try {
      var savedTheme = localStorage.getItem('fedu_font_theme');
      setTheme(savedTheme === 'dark' || savedTheme === 'neon' ? savedTheme : 'light');
    } catch (e) {
      setTheme('light');
    }

    // Populate preset dropdown
    populatePresets();

    // Bind event handlers
    bindEvents();

    // Load Catalog Data
    try {
      var catalogData = await CatalogLoader.fetchCatalog('data/catalog.json');
      App.catalog = catalogData;
      App.allFonts = catalogData.fonts || [];

      // Pre-index fonts for sub-4ms instant search
      App.indexedFonts = CatalogLoader.buildSearchIndex(App.allFonts);
      App.filteredFonts = App.allFonts.slice();

      // Populate studio filter dropdowns
      populateStudioDropdowns();

      // Update header metrics
      if (DOM.headerStatsBadge && catalogData.summary) {
        DOM.headerStatsBadge.textContent = catalogData.summary.total_fonts + ' Families / ' +
          (catalogData.summary.drive_files_total ? catalogData.summary.drive_files_total.toLocaleString() : '1,070') + ' Fonts';
      }

      // Initial Filter & Render
      applyFilters();

      // Check URL hash for initial view mode (#fontshare, #pair, or catalog)
      var hash = (window.location.hash || '').replace('#', '').toLowerCase();
      if (hash === 'fontshare' || hash === 'pair') {
        switchView(hash);
      } else {
        switchView('catalog');
      }

      // Eagerly pre-warm common static font weights for immediate canvas rendering
      if (typeof document !== 'undefined' && document.fonts && document.fonts.load) {
        ['FD Aeonik', 'FDAeonik', 'FD Gilroy', 'FDGilroy', 'GR Sectra', 'GRSectra'].forEach(function (f) {
          [100, 300, 400, 700, 900].forEach(function (w) {
            document.fonts.load(w + ' 36px "' + f + '"').catch(function () {});
          });
        });
      }
    } catch (err) {
      console.error('[fedu-font] Failed to load catalog.json:', err);
      if (DOM.fontGrid) {
        DOM.fontGrid.innerHTML = '<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-secondary);">' +
          'Không thể tải danh mục font: ' + escapeHTML(err.message) + '</div>';
      }
    }
  }

  // Start on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose App on window for debug/testing
  window.FeduFontApp = App;
})();
