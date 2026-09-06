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
    fontLoadObserver: null
  };

  // DOM Cache
  var DOM = {};

  function cacheDOM() {
    DOM.html = document.documentElement;
    DOM.headerStatsBadge = document.getElementById('header-stats-badge');
    DOM.themeBtns = document.querySelectorAll('[data-theme-set]');

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
   * Updates global specimen preview text across all cards.
   */
  function broadcastPreviewText(text) {
    var cleanText = text !== undefined ? String(text) : '';
    App.typeTester.text = cleanText;

    var previewElements = DOM.fontGrid.querySelectorAll('.preview-text');
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
      var favs = localStorage.getItem('fonthub_favorites');
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
      localStorage.setItem('fonthub_favorites', JSON.stringify(favs));
      return isFav;
    } catch (e) {
      return false;
    }
  }

  /**
   * Resolves a human-readable font variant (e.g. 'Light', 'Book', 'BoldItalic', 'ExtraBold')
   * into valid CSS font-weight, font-style, and family fallbacks matching OS & webfont files.
   */
  function resolveVariantStyle(family, variantStr, category, files) {
    var raw = String(variantStr || 'Regular').trim();
    var lower = raw.toLowerCase();

    // 1. Determine fontStyle
    var isItalic = lower.includes('italic') || lower.includes('oblique') || lower.includes('slant');
    var fontStyle = isItalic ? 'italic' : 'normal';

    // 2. Determine numeric fontWeight
    var fontWeight = '400';
    if (lower.includes('thin') || lower.includes('hairline') || lower === '100' || lower === '100italic' || lower.includes('air')) {
      fontWeight = '100';
    } else if (lower.includes('extralight') || lower.includes('ultralight') || lower.includes('extra light') || lower.includes('ultra light') || lower === '200' || lower === '200italic') {
      fontWeight = '200';
    } else if (lower.includes('light') || lower === '300' || lower === '300italic') {
      fontWeight = '300';
    } else if (lower.includes('medium') || lower === '500' || lower === '500italic') {
      fontWeight = '500';
    } else if (lower.includes('semibold') || lower.includes('demibold') || lower.includes('semi bold') || lower.includes('demi bold') || lower === '600' || lower === '600italic') {
      fontWeight = '600';
    } else if (lower.includes('extrabold') || lower.includes('ultrabold') || lower.includes('heavy') || lower.includes('extra bold') || lower.includes('ultra bold') || lower === '800' || lower === '800italic') {
      fontWeight = '800';
    } else if (lower.includes('black') || lower.includes('poster') || lower.includes('ultra') || lower === '900' || lower === '900italic') {
      fontWeight = '900';
    } else if (lower.includes('bold') || lower === '700' || lower === '700italic') {
      fontWeight = '700';
    } else if (lower.includes('book') || lower.includes('regular') || lower.includes('normal') || lower.includes('roman') || lower === '400') {
      fontWeight = '400';
    }

    // 3. Fallback stack
    var fallbackStack = App.typeTester ? App.typeTester.getFallbackStack(category) : 'sans-serif';

    // 4. Style naming for OS Font Matching
    var cleanStyle = raw.replace(/[_-]/g, ' ').trim();
    var hyphenStyle = raw.replace(/\s+/g, '-').trim();

    var candidates = [
      "'" + family + " " + cleanStyle + "'",
      "'" + family + "-" + hyphenStyle + "'",
      "'" + family + " " + raw + "'",
      "'" + family + "-" + raw + "'",
      "'" + family + "'"
    ];

    // Check if matching file exists in font.files
    var matchedFilename = null;
    if (Array.isArray(files) && files.length > 0) {
      var found = files.find(function (f) {
        if (!f) return false;
        var fStyle = String(f.style || '').toLowerCase();
        var fName = String(f.filename || '').toLowerCase();
        return fStyle === lower || fName.includes(lower) || fName.includes(hyphenStyle.toLowerCase());
      });
      if (found && found.filename) {
        matchedFilename = found.filename;
        candidates.unshift("'" + matchedFilename.replace(/\.(ttf|otf|woff2)$/i, '') + "'");
      }
    }

    var combinedFamily = candidates.join(', ') + ', ' + fallbackStack;

    return {
      rawVariant: raw,
      fontWeight: fontWeight,
      fontStyle: fontStyle,
      fontFamily: combinedFamily,
      matchedFilename: matchedFilename
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

    var anatomy = font.anatomy || {};
    var contrast = anatomy.contrast || 'Medium';
    var axis = anatomy.axis || 'Vertical';
    var xHeight = anatomy.x_height || 'Medium';
    var aperture = anatomy.aperture || 'Balanced';

    var directorNotes = font.director_notes || 'Kiểu chữ tinh tế, cân bằng thị giác hoàn hảo.';

    var driveUrl = font.drive_folder_url || 'https://drive.google.com/drive/folders/1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao?usp=sharing';
    var downloadTooltip = 'Tải trọn bộ ' + escapeHTML(font.name) + ' (' + weightsCount + ' files zip)';

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

    // Build weight chips
    var weightChipsHTML = weights.map(function (w, idx) {
      var isActive = (idx === defaultWeightIdx);
      return '<button type="button" class="weight-chip' + (isActive ? ' active' : '') + '" data-weight="' + escapeHTML(w) + '">' + escapeHTML(w) + '</button>';
    }).join('');

    var isFav = isFontFavorite(font.id);

    return [
      '<article class="font-card" data-font-id="' + escapeHTML(font.id) + '" data-family="' + escapeHTML(font.family || font.name) + '" data-category="' + escapeHTML(category) + '">',
      '  <header class="card-header">',
      '    <div class="card-title-row">',
      '      <div class="title-with-fav">',
      '        <button type="button" class="btn-fav' + (isFav ? ' active' : '') + '" data-fav-id="' + escapeHTML(font.id) + '" title="Đánh dấu yêu thích">⭐️</button>',
      '        <h3 class="card-family-name">' + escapeHTML(font.name) + '</h3>',
      '        <button type="button" class="btn-copy-name" data-copy-name="' + escapeHTML(font.name) + '" title="Copy tên font">',
      '          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
      '        </button>',
      '      </div>',
      '      <span class="badge">' + weightsLabel + '</span>',
      '    </div>',
      '    <div class="card-designer-row">',
      '      <span>' + escapeHTML(font.designer || 'FEDU Studio') + '</span>',
      '      <span>•</span>',
      '      <span>' + escapeHTML(font.source || 'PDF & Drive') + '</span>',
      '    </div>',
      '    <div class="card-badges-row">',
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
      '      <blockquote class="director-quote">"' + escapeHTML(directorNotes) + '"</blockquote>',
      '    </div>',
      '  </details>',
      '  <footer class="card-footer">',
      '    <a href="' + driveUrl + '" class="btn-download-family" target="_blank" rel="noopener noreferrer" title="' + downloadTooltip + '">',
      '      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">',
      '        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>',
      '        <polyline points="7 10 12 15 17 10"/>',
      '        <line x1="12" y1="15" x2="12" y2="3"/>',
      '      </svg>',
      '      <span>Tải Trọn Bộ (.zip)</span>',
      '    </a>',
      '    <div class="secondary-actions">',
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
      DOM.resultsCount.textContent = total + ' / 361 font families';
    }

    if (total === 0) {
      if (DOM.emptyState) DOM.emptyState.classList.remove('hidden');
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
        }

        // Dynamically load font face if available on server
        if (resolved.matchedFilename && typeof FontFace !== 'undefined') {
          var fontFaceFamily = family + ' ' + resolved.rawVariant;
          var fontUrl = '../fonts/' + resolved.matchedFilename;
          if (!document.fonts.check('16px "' + fontFaceFamily + '"')) {
            var face = new FontFace(fontFaceFamily, 'url("' + fontUrl + '")', {
              weight: resolved.fontWeight,
              style: resolved.fontStyle
            });
            face.load().then(function (loaded) {
              document.fonts.add(loaded);
              if (preview) {
                preview.style.fontFamily = '"' + fontFaceFamily + '", ' + resolved.fontFamily;
              }
            }).catch(function () {});
          }
        }
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
   * Executes instant search and faceted filtering.
   */
  function applyFilters() {
    var startTime = performance.now();

    // 1. Search Query
    var searchResults = CatalogLoader.instantSearch(App.indexedFonts, App.activeFilters.searchQuery);

    // 2. Multi-Dimensional Filter
    var filterCriteria = {
      category: App.activeFilters.category,
      mood: App.activeFilters.mood,
      use_case: App.activeFilters.use_case,
      weight: App.activeFilters.weight,
      vietnamese_support: App.activeFilters.vietnamese_support
    };

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
  }

  /**
   * Clears all filters back to default state.
   */
  function clearAllFilters() {
    App.activeFilters = {
      searchQuery: '',
      category: 'all',
      mood: 'all',
      use_case: 'all',
      weight: 'all',
      vietnamese_support: true
    };

    if (DOM.searchInput) DOM.searchInput.value = '';
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
    showToast('Đã xóa bộ lọc, hiển thị toàn bộ 361 font');
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
      // Render standard character map
      App.typeTester.renderGlyphMap(DOM.glyphModalBody, App.activeModalFont, function (char, hex) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(char).then(function () {
            showToast('Đã copy ký tự \'' + char + '\' (U+' + hex + ')');
          });
        }
      });
    }
  }

  /**
   * Initializes event listeners across all interactive controls.
   */
  function bindEvents() {
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

      // Update header metrics
      if (DOM.headerStatsBadge && catalogData.summary) {
        DOM.headerStatsBadge.textContent = catalogData.summary.total_fonts + ' Families / ' +
          (catalogData.summary.drive_files_total ? catalogData.summary.drive_files_total.toLocaleString() : '1,070') + ' Fonts';
      }

      // Initial Filter & Render
      applyFilters();
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
