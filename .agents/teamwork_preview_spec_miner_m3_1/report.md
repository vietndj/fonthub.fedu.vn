# Technical Specification: Milestone 3 UI/UX Design System & Interactive Type Tester

**Project**: `fedu.vn/font Interactive Type Hub`  
**Agent**: `teamwork_preview_spec_miner_m3_1`  
**Milestone**: M3 (`m3_web_type_tester`)  
**Date**: 2026-09-06  
**Status**: SPECIFICATION COMPLETE & AUTHORITATIVE  

---

## 1. Executive Summary & Aesthetic Manifesto

The `fedu.vn/font Interactive Type Hub` user interface is engineered to set a new benchmark for Vietnamese typography platforms. Moving decisively beyond legacy desktop-bound font catalogs and bloated framework architectures, `fedu.vn/font` adopts an **Ultra-Lightweight Editorial Brutalist / Swiss Modern Type Foundry Aesthetic**, drawing direct design lineage from premier international foundries: **Grilli Type** (precision micro-metrics, functional information density) and **Pangram Pangram** (high-contrast dark mode, architectural typography, interactive kinetic specimen sliders).

### Core Architectural Pillars
1. **Zero-Dependency Native Runtime**: Built strictly with semantic HTML5, CSS3 Custom Properties, and Vanilla ES6+ JavaScript. Total CSS/JS bundle payload strictly capped under **80 KB** (uncompressed) / **25 KB** (gzipped), ensuring instantaneous Time-to-Interactive (<350ms) across all devices.
2. **Tri-Theme Visual System**: Native CSS variables powering three distinct environmental modes:
   - **Dark Mode (`#121212`)**: Master studio foundry environment with high-contrast neutral surfaces and subtle 1px micro-borders.
   - **Light Mode (`#FFFFFF`)**: Clean editorial paper aesthetic for testing long-form readability and print contrast.
   - **Neon Accent Mode (`#0D0E15` / `#00FF66`)**: High-energy terminal/cyberpunk aesthetic for bold display, UI/UX, and tech headline evaluation.
3. **Single-Variable Batching Engine**: Fluid slider controls (Size 14-140px, Line-height 0.8-2.4, Kerning -0.05em to +0.30em) bind directly to root CSS custom properties. Dragging a slider updates 361 font cards simultaneously at a locked **60 FPS** without triggering individual DOM reflow loops.
4. **Authentic Vietnamese Typographic Respect**: Complete, dedicated support for all 134 Vietnamese accented characters (upper & lower), robust IME composition handling (Telex/VNI), complex multi-tone test suites, and interactive character-level glyph inspection.

---

## 2. Technical UI Architecture & Layout Structure

```
+----------------------------------------------------------------------------------------------------+
|  TOP UTILITY BAR: [fedu.vn/font] [Status: 361 Families / 1,070 Fonts] [Theme Toggle: Dark|Light|Neon] |
+----------------------------------------------------------------------------------------------------+
|  STICKY GLOBAL TYPE TESTER TOOLBAR (Frosted Backdrop Blur)                                         |
|  [ Live Text Input: "Khám phá vẻ đẹp Typo fedu.vn/font"               ] [Quotes ▾]                 |
|  Size: [---●--------] 36px  |  LH: [----●-------] 1.20  |  Kern: [--●---------] 0.00em             |
|  Align: [L][C][R][J]  |  Case: [Aa][AA][aa][Abc]  |  Reset [↺]                                     |
+----------------------------------------------------------------------------------------------------+
|  FACETED FILTER & SEARCH BAR                                                                       |
|  [🔍 Tìm kiếm tên font, designer, nhận định... (sub-4ms)]                                         |
|  Category: [Tất cả (361)] [Serif (62)] [Sans Serif (184)] [Vintage (58)] [Mono/Script (57)]       |
|  Mood: [Luxury & Sang trọng] [Tech & Công nghệ] [Bold & Tuyên ngôn] [Friendly] [Nostalgic]        |
|  Use-Case: [Display / Headline] [Body Text] | VN Ready: [☑ Chỉ hiện font hỗ trợ Tiếng Việt]       |
+----------------------------------------------------------------------------------------------------+
|  DYNAMIC FONT SPECIMEN GRID (1 col mobile, 2 col tablet, 3 col desktop / 1 col full specimen)      |
|  +-------------------------------------+  +-------------------------------------+                  |
|  | SVN-Integral CF       [6 styles][VN] |  | SVN-Saol Standard     [8 styles][VN]|                  |
|  | Connary Fagen • Display / Headline   |  | Schick Toikka • Luxury & Sang trọng |                  |
|  |-------------------------------------|  |-------------------------------------|                  |
|  | PREVIEW SPECIMEN (Live Reactive):   |  | PREVIEW SPECIMEN (Live Reactive):   |                  |
|  | NGHỆ THUẬT CHỮ ĐIỆN ẢNH             |  | Vẻ Đẹp Cổ Điển Tinh Tế             |                  |
|  |-------------------------------------|  |-------------------------------------|                  |
|  | [Regular][Demi][Bold*][Extra][Heavy]|  | [Light][Regular*][Medium][Bold]     |                  |
|  | Anatomy: Contrast Low | Axis Vert   |  | Anatomy: Contrast High | Axis Vert  |                  |
|  | Notes: "Font tiêu đề cực kỳ uy lực" |  | Notes: "Serif tân cổ điển sắc sảo"  |                  |
|  |-------------------------------------|  |-------------------------------------|                  |
|  | [⬇ Tải Trọn Bộ Family (.zip)]       |  | [⬇ Tải Trọn Bộ Family (.zip)]       |                  |
|  | [🔣 Bảng Ký Tự]   [📋 Copy CSS]     |  | [🔣 Bảng Ký Tự]   [📋 Copy CSS]     |                  |
|  +-------------------------------------+  +-------------------------------------+                  |
+----------------------------------------------------------------------------------------------------+
|  MODAL: VIETNAMESE GLYPH EXPLORER (Triggered on Demand)                                            |
+----------------------------------------------------------------------------------------------------+
```

### Responsive Breakpoints Specification
- **Mobile (<768px)**:
  - Grid: `grid-template-columns: 1fr;` (single-column card feed).
  - Floating Toolbar: Compact two-row layout. Sliders collapse into an expandable accordion or horizontal overflow scroll.
  - Padding: Container gutter `16px`.
- **Tablet (768px - 1199px)**:
  - Grid: `grid-template-columns: repeat(2, 1fr);` (two-column card grid) or optional full-width specimen toggle.
  - Floating Toolbar: Single pinned row with flex wrapping for controls.
  - Padding: Container gutter `24px`.
- **Desktop (>=1200px)**:
  - Grid: `grid-template-columns: repeat(3, 1fr);` for catalog view, with 1-column toggle for editorial wide specimen reading.
  - Floating Toolbar: Pinned sticky header with all metrics, text transform, alignment, and presets visible.
  - Padding: Container max-width `1440px`, gutter `32px`.

---

## 3. Design Tokens & CSS Custom Properties Specification

The design tokens are categorized into global semantic variables and theme-specific palettes declared on `html[data-theme="..."]`.

```css
/* ==========================================================================
   Global Baseline Tokens (Typography, Metrics, Z-Index)
   ========================================================================== */
:root {
  /* Typography Stacks */
  --font-display: 'SVN-Integral CF', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-body: 'SVN-Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

  /* Type Tester Live Custom Properties (Manipulated by Sliders in Real-Time) */
  --tester-font-size: 36px;
  --tester-line-height: 1.2;
  --tester-letter-spacing: 0.00em;
  --tester-text-align: left;
  --tester-text-transform: none;

  /* Layout Dimensions */
  --header-height: 64px;
  --toolbar-height: 60px;
  --card-radius: 8px;
  --badge-radius: 4px;
  --modal-radius: 12px;

  /* Transitions */
  --transition-fast: 120ms cubic-bezier(0.16, 1, 0.3, 1);
  --transition-normal: 200ms cubic-bezier(0.16, 1, 0.3, 1);

  /* Z-Index Layers */
  --z-base: 1;
  --z-sticky-toolbar: 100;
  --z-modal-backdrop: 900;
  --z-modal-dialog: 1000;
  --z-toast: 1100;
}

/* ==========================================================================
   Theme 1: Dark Mode (Default / Grilli-Pangram Master Studio)
   ========================================================================== */
html[data-theme="dark"],
:root {
  --bg-primary: #121212;
  --bg-surface: #1A1A1A;
  --bg-elevated: #242424;
  --bg-hover: #2E2E2E;
  
  --text-primary: #F5F5F7;
  --text-secondary: #A1A1A6;
  --text-tertiary: #6E6E73;
  --text-inverse: #121212;

  --border-subtle: #282828;
  --border-strong: #3D3D3D;
  --border-focus: #F5F5F7;

  --accent-primary: #FFFFFF;
  --accent-hover: #E5E5E5;
  --accent-text: #121212;
  --accent-focus-ring: rgba(255, 255, 255, 0.25);

  --badge-bg: #222222;
  --badge-text: #D1D1D6;
  --badge-border: #333333;
  --badge-vn-bg: #112818;
  --badge-vn-text: #4EFA87;

  --slider-track: #2C2C2E;
  --slider-fill: #F5F5F7;
  --slider-thumb: #FFFFFF;

  --toolbar-bg: rgba(18, 18, 18, 0.85);
  --modal-overlay: rgba(0, 0, 0, 0.80);
  --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

/* ==========================================================================
   Theme 2: Light Mode (Clean Architectural Editorial)
   ========================================================================== */
html[data-theme="light"] {
  --bg-primary: #FFFFFF;
  --bg-surface: #F8F9FA;
  --bg-elevated: #FFFFFF;
  --bg-hover: #F1F3F5;

  --text-primary: #111111;
  --text-secondary: #555555;
  --text-tertiary: #888888;
  --text-inverse: #FFFFFF;

  --border-subtle: #E5E5E5;
  --border-strong: #CCCCCC;
  --border-focus: #111111;

  --accent-primary: #111111;
  --accent-hover: #333333;
  --accent-text: #FFFFFF;
  --accent-focus-ring: rgba(0, 0, 0, 0.18);

  --badge-bg: #EEEEEE;
  --badge-text: #333333;
  --badge-border: #E0E0E0;
  --badge-vn-bg: #E6F8ED;
  --badge-vn-text: #0E853C;

  --slider-track: #E2E4E8;
  --slider-fill: #111111;
  --slider-thumb: #111111;

  --toolbar-bg: rgba(255, 255, 255, 0.88);
  --modal-overlay: rgba(0, 0, 0, 0.50);
  --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

/* ==========================================================================
   Theme 3: Neon Accent Mode (Cyberpunk / Terminal Tech)
   ========================================================================== */
html[data-theme="neon"] {
  --bg-primary: #0D0E15;
  --bg-surface: #141622;
  --bg-elevated: #1C1F30;
  --bg-hover: #252A42;

  --text-primary: #E0E6ED;
  --text-secondary: #8B95A5;
  --text-tertiary: #525D70;
  --text-inverse: #0D0E15;

  --border-subtle: #23283E;
  --border-strong: #363E5E;
  --border-focus: #00FF66;

  --accent-primary: #00FF66;
  --accent-hover: #26FF7D;
  --accent-text: #0D0E15;
  --accent-focus-ring: rgba(0, 255, 102, 0.30);
  --accent-glow: 0 0 16px rgba(0, 255, 102, 0.35);

  --badge-bg: #13241B;
  --badge-text: #00FF66;
  --badge-border: #1B452D;
  --badge-vn-bg: #13241B;
  --badge-vn-text: #00FF66;

  --slider-track: #1C2333;
  --slider-fill: #00FF66;
  --slider-thumb: #00FF66;

  --toolbar-bg: rgba(13, 14, 21, 0.88);
  --modal-overlay: rgba(5, 6, 10, 0.85);
  --card-shadow: 0 4px 24px rgba(0, 255, 102, 0.08);
}
```

---

## 4. Interactive Type Tester Controls & Slider Mechanics

### A. Slider Metric Specifications & Clamping Bounds
Every numeric parameter has mathematically enforced boundaries to guarantee typographic stability:

| Parameter | Selector ID | Min Bound | Max Bound | Default | Step | CSS Unit | Clamping Logic |
|---|---|---|---|---|---|---|---|
| **Font Size** | `#size-slider` | `14` | `140` | `36` | `1` | `px` | `Math.max(14, Math.min(140, Math.round(Number(val))))` (NaN falls back to 36) |
| **Line-Height** | `#lh-slider` | `0.80` | `2.40` | `1.20` | `0.05` | unitless | `parseFloat(Math.max(0.8, Math.min(2.4, Number(val))).toFixed(2))` |
| **Kerning / Tracking** | `#kerning-slider` | `-0.050` | `+0.300` | `0.000` | `0.01` | `em` | `parseFloat(Math.max(-0.05, Math.min(0.30, Number(val))).toFixed(3))` |

### B. High-Performance CSS Variable Batching
To eliminate jank when sliding on a page displaying 361 font cards:
```javascript
// High-performance batching: update CSS custom properties on the root element
const root = document.documentElement;

function setTypeTesterSize(val) {
  const clamped = TypeTesterMetrics.clampFontSize(val);
  root.style.setProperty('--tester-font-size', `${clamped}px`);
  document.getElementById('size-value').textContent = `${clamped}px`;
}

function setTypeTesterLineHeight(val) {
  const clamped = TypeTesterMetrics.clampLineHeight(val);
  root.style.setProperty('--tester-line-height', clamped);
  document.getElementById('lh-value').textContent = clamped.toFixed(2);
}

function setTypeTesterKerning(val) {
  const clamped = TypeTesterMetrics.clampKerning(val);
  root.style.setProperty('--tester-letter-spacing', `${clamped}em`);
  document.getElementById('kerning-value').textContent = `${clamped >= 0 ? '+' : ''}${clamped.toFixed(2)}em`;
}
```

### C. Live Text Input & Vietnamese IME Composition Handling
Typing Vietnamese characters using Telex (e.g. `w`, `s`, `f`, `r`, `x`, `j`) or VNI generates intermediate composition events. If an event listener immediately transforms or splits text while composition is active, vowels get corrupted:
```javascript
let isComposing = false;
const input = document.getElementById('global-preview-input');

input.addEventListener('compositionstart', () => {
  isComposing = true;
});

input.addEventListener('compositionend', (e) => {
  isComposing = false;
  broadcastPreviewText(e.target.value);
});

input.addEventListener('input', (e) => {
  if (!isComposing) {
    broadcastPreviewText(e.target.value);
  }
});
```

### D. Preset Vietnamese Quotes Selector
A curated list of presets tailored to various design evaluation needs:
1. **Headline Impact**: `"CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"`
2. **Vietnamese Pangram**: `"Dòng sông lặng lẽ tràn đầy tình yêu và nỗi nhớ thương sâu thẳm"`
3. **Typography Philosophy**: `"Vẻ đẹp của kiểu chữ nằm ở sự cân bằng giữa hình khối và khoảng trống"`
4. **Editorial Fashion**: `"BỘ SƯU TẬP MÙA THU - VẺ ĐẸP CỦA SỰ TỐI GIẢN"`
5. **Cyberpunk Tech**: `"TRÍ TUỆ NHÂN TẠO & HỆ THỐNG TỰ HÀNH TƯƠNG LAI"`
6. **Vintage Sài Gòn**: `"SÀI GÒN 1975 - NHỮNG BIỂN HIỆU XƯA"`
7. **Numeric & Currency**: `"0123456789 • 95.000.000 ₫ • §±€$¥"`

### E. Text Case & Alignment Controls
- **Alignment Buttons**: Left (`text-align: left`), Center (`center`), Right (`right`), Justify (`justify`).
- **Transform Buttons**:
  - `Aa` (Original): `text-transform: none;`
  - `AA` (Uppercase): `text-transform: uppercase;` (using Unicode-aware uppercase logic)
  - `aa` (Lowercase): `text-transform: lowercase;`
  - `Abc` (Capitalize / Title Case): `text-transform: capitalize;`

---

## 5. Dynamic Font Card Component Specification

### A. Card DOM Anatomy
```html
<article class="font-card" data-font-id="svn-integral-cf" data-category="Sans Serif" data-mood="Bold & Tuyên ngôn">
  <!-- Card Header -->
  <header class="font-card__header">
    <div class="font-card__title-group">
      <h3 class="font-card__family">SVN-Integral CF</h3>
      <p class="font-card__designer">Connary Fagen <span class="bullet">•</span> PDF & Drive</p>
    </div>
    <div class="font-card__badges">
      <span class="badge badge--weight">6 styles</span>
      <span class="badge badge--vn" title="Hỗ trợ đầy đủ Tiếng Việt có dấu">VN Ready</span>
      <span class="badge badge--style">Sans Geometric</span>
    </div>
  </header>

  <!-- Interactive Specimen Area -->
  <div class="font-card__specimen-wrap">
    <div 
      class="font-card__specimen" 
      contenteditable="true" 
      spellcheck="false"
      style="font-family: 'SVN-Integral CF', sans-serif;"
    >
      CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
    </div>
  </div>

  <!-- Weights Variation Switcher -->
  <div class="font-card__weights-bar" aria-label="Biến thể độ dày">
    <button class="weight-chip" data-weight="400">Regular</button>
    <button class="weight-chip" data-weight="500">Medium</button>
    <button class="weight-chip" data-weight="600">DemiBold</button>
    <button class="weight-chip active" data-weight="700">Bold</button>
    <button class="weight-chip" data-weight="800">ExtraBold</button>
    <button class="weight-chip" data-weight="900">Heavy</button>
  </div>

  <!-- Metadata & Commentary Drawer -->
  <details class="font-card__drawer">
    <summary class="drawer-trigger">
      <span>Thông số & Nhận định Đạo diễn</span>
      <svg class="chevron" width="12" height="12" viewBox="0 0 12 12"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
    </summary>
    <div class="drawer-content">
      <div class="anatomy-grid">
        <div class="anatomy-item"><span class="label">Độ tương phản</span><span class="val">Low</span></div>
        <div class="anatomy-item"><span class="label">Trục nghiêng</span><span class="val">Vertical</span></div>
        <div class="anatomy-item"><span class="label">X-Height</span><span class="val">High</span></div>
        <div class="anatomy-item"><span class="label">Độ mở (Aperture)</span><span class="val">Tight</span></div>
      </div>
      <blockquote class="director-quote">
        "Font tiêu đề tuyên ngôn mạnh mẽ, chữ in hoa cực kỳ uy lực."
      </blockquote>
    </div>
  </details>

  <!-- Card Action Footer -->
  <footer class="font-card__footer">
    <a 
      class="btn-download-family" 
      href="https://drive.google.com/drive/folders/1...usp=sharing" 
      target="_blank" 
      rel="noopener noreferrer" 
      title="Tải trọn bộ SVN-Integral CF (6 fonts)"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      <span>Tải Trọn Bộ Family (.zip)</span>
    </a>

    <div class="secondary-actions">
      <button class="btn-icon btn-glyph" title="Xem bảng ký tự & glyphs" data-action="open-glyph-map">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M15 3v18"/><path d="M3 9h18"/><path d="M3 15h18"/></svg>
        <span>Glyphs</span>
      </button>
      <button class="btn-icon btn-copy-css" title="Copy mã @font-face CSS" data-action="copy-css">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        <span>CSS</span>
      </button>
    </div>
  </footer>
</article>
```

### B. Font Card State & Interaction Rules
1. **In-place ContentEditable**: Clicking directly on the specimen allows typing in-place. Changes are localized to that card unless user clicks "Áp dụng cho toàn bộ thẻ".
2. **Weight Switcher Reactivity**: Clicking a `.weight-chip` updates that card's `font-weight` style and triggers dynamic FontFace loading for that specific WOFF2 weight file via `type_tester.js`.
3. **1-Click Download Contract**: The download link MUST point to `font.drive_folder_url` (with `?usp=sharing`), strictly including `target="_blank"` and `rel="noopener noreferrer"`.

---

## 6. Vietnamese Glyph Map Modal Specification

The Glyph Map modal provides an exhaustive interactive inspection tool for the font's character support, with an emphasis on Vietnamese accent fidelity.

```
+------------------------------------------------------------------------------------------+
|  MODAL HEADER: SVN-Integral CF — Bảng Ký Tự & Dấu Tiếng Việt                          [✕] |
|  Foundry: Connary Fagen | Tổng số: 134 ký tự Tiếng Việt + 26 chữ cái cơ bản + số         |
+------------------------------------------------------------------------------------------+
|  TAB BAR:                                                                                |
|  [★ Tất Cả Tiếng Việt (134)] [Chữ Thường (67)] [Chữ Hoa (67)] [Từ Phức Tạp] [Số & Dấu]   |
+------------------------------------------------------------------------------------------+
|  GLYPH GRID (Rendered in target font at 36px):                                           |
|  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+          |
|  | a  |  | à  |  | á  |  | ả  |  | ã  |  | ạ  |  | ă  |  | ằ  |  | ắ  |  | ẳ  |  ...      |
|  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+          |
|  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+          |
|  | A  |  | À  |  | Á  |  | Ả  |  | Ã  |  | Ạ  |  | Ă  |  | Ằ  |  | Ắ  |  | Ẳ  |  ...      |
|  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+  +----+          |
+------------------------------------------------------------------------------------------+
|  BOTTOM BAR: [Hover: "ể" • Unicode: U+1EBB]  |  [Nhấp vào ký tự để Copy vào Clipboard]  |
+------------------------------------------------------------------------------------------+
```

### Complete Vietnamese Unicode Glyph Inventory (134 Characters)

#### Lowercase (67 Characters)
`a`, `à`, `á`, `ả`, `ã`, `ạ`, `ă`, `ằ`, `ắ`, `ẳ`, `ẵ`, `ặ`, `â`, `ầ`, `ấ`, `ẩ`, `ẫ`, `ậ`, `e`, `è`, `é`, `ẻ`, `ẽ`, `ẹ`, `ê`, `ề`, `ế`, `ể`, `ễ`, `ệ`, `i`, `ì`, `í`, `ỉ`, `ĩ`, `ị`, `o`, `ò`, `ó`, `ỏ`, `õ`, `ọ`, `ô`, `ồ`, `ố`, `ổ`, `ỗ`, `ộ`, `ơ`, `ờ`, `ớ`, `ở`, `ỡ`, `ợ`, `u`, `ù`, `ú`, `ủ`, `ũ`, `ụ`, `ư`, `ừ`, `ứ`, `ử`, `ữ`, `ự`, `y`, `ỳ`, `ý`, `ỷ`, `ỹ`, `ỵ`, `đ`.

#### Uppercase (67 Characters)
`A`, `À`, `Á`, `Ả`, `Ã`, `Ạ`, `Ă`, `Ằ`, `Ắ`, `Ẳ`, `Ẵ`, `Ặ`, `Â`, `Ầ`, `Ấ`, `Ẩ`, `Ẫ`, `Ậ`, `E`, `È`, `É`, `Ẻ`, `Ẽ`, `Ẹ`, `Ê`, `Ề`, `Ế`, `Ể`, `Ễ`, `Ệ`, `I`, `Ì`, `Í`, `Ỉ`, `Ĩ`, `Ị`, `O`, `Ò`, `Ó`, `Ỏ`, `Õ`, `Ọ`, `Ô`, `Ồ`, `Ố`, `Ổ`, `Ỗ`, `Ộ`, `Ơ`, `Ờ`, `Ớ`, `Ở`, `Ỡ`, `Ợ`, `U`, `Ù`, `Ú`, `Ủ`, `Ũ`, `Ụ`, `Ư`, `Ừ`, `Ứ`, `Ử`, `Ữ`, `Ự`, `Y`, `Ỳ`, `Ý`, `Ỷ`, `Ỹ`, `Ỵ`, `Đ`.

#### Complex Tone Diagnostic Words Tab
Contains real-world challenging words testing stacked diacritics, horn positioning, and acute/hook accents:
`nghiêng`, `khuyến`, `thưởng`, `truyền`, `hoằng`, `quế`, `phượng`, `chuộng`, `nguyện`, `ngưỡng`, `THƯỞNG`, `NGHIÊNG`, `KHUYẾN`, `TRUYỀN`, `ĐỒ HỌA`.

### Modal Interaction Logic
1. **Focus Trap & Keyboard Accessibility**:
   - Pressing `Escape` closes the modal immediately.
   - Tab key is trapped within modal interactive elements.
   - Background scrolling is locked (`body { overflow: hidden; }`).
2. **1-Click Copy-to-Clipboard**:
   - Clicking any glyph cell triggers `navigator.clipboard.writeText(char)`.
   - Displays a brief toast animation: `"Đã copy ký tự 'ể' (U+1EBB)"`.

---

## 7. Performance Budget & Runtime Constraints

| Metric | Budget Target | Implementation Mechanism |
|---|---|---|
| **Total CSS Payload** | `< 20 KB` | Pure native CSS, no Tailwind/Bootstrap bloat, shared design tokens |
| **Total JS Payload** | `< 30 KB` | Pure ES6+ modules (`app.js`, `type_tester.js`, `catalog_loader.js`) |
| **Data Payload** | `< 120 KB` (gzipped) | Normalized JSON structure in `data/catalog.json` |
| **Time to Interactive (TTI)** | `< 350 ms` | Asynchronous catalog fetch with inline fallback skeleton |
| **Slider Drag Performance** | `60 FPS` | Single CSS root variable update via `setProperty` |
| **Search Query Latency** | `< 4 ms` | Pre-normalized diacritic search cache in memory |

---

## 8. Authoritative Features Discovered Table

## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Architecture | Zero-Dependency Static Hub | Pure HTML5/CSS3/Vanilla JS web app running without Node runtime or build server | Browser HTTP request | Rendered type hub DOM (<80KB payload) | Graceful fallback to offline cached data | ORIGINAL_REQUEST.md § R4 |
| 2 | Design System | Grilli/Pangram Editorial Dark Theme | Primary dark mode aesthetic (#121212) with micro-borders and high contrast | `data-theme="dark"` attribute | Dark palette CSS variables applied to DOM | Fallback to dark if theme undefined | ORIGINAL_REQUEST.md § R4 & DISPATCH.md |
| 3 | Design System | Architectural Light Theme | High-contrast clean paper aesthetic (#FFFFFF) for editorial print evaluation | `data-theme="light"` attribute | Light palette CSS variables applied to DOM | Preserves active text and slider values | ORIGINAL_REQUEST.md § R2 & DISPATCH.md |
| 4 | Design System | Neon Accent Cyberpunk Theme | Terminal tech mode (#0D0E15 with #00FF66 accent) for digital display testing | `data-theme="neon"` attribute | Neon palette CSS variables + glow filters applied | Preserves active text and slider values | ORIGINAL_REQUEST.md § R2 & DISPATCH.md |
| 5 | Type Tester | Global Sticky Frosted Toolbar | Pinned header bar providing synchronized control over all 361 font cards | Scroll position, user interactions | Sticky DOM header with backdrop-filter: blur(12px) | Degrades to solid background on legacy browsers | DISPATCH.md & PROJECT.md |
| 6 | Type Tester | Live Vietnamese Text Input | Interactive text input field dynamically binding to all font card specimens | Raw text string, Vietnamese IME keystrokes | Synchronized specimen text across all cards | Handles empty string with default fallback | ORIGINAL_REQUEST.md § R2 |
| 7 | Type Tester | IME Composition Protection | Protects Vietnamese Telex/VNI uncommitted keystrokes from broken mid-word splits | `compositionstart`, `compositionend` events | Emits text only on finished syllable composition | Prevents vowel dropping or tone glitching | tests/tier2_boundary_tests.js |
| 8 | Type Tester | Fluid Font Size Slider | Smooth slider scaling font sizes from 14px to 140px | Slider position or numeric input (14-140) | Updates `--tester-font-size` CSS variable | Clamps values <14 to 14, >140 to 140; NaN falls back to 36 | ORIGINAL_REQUEST.md § R2 & tests/lib/engine.js |
| 9 | Type Tester | Line-Height Metric Slider | Adjusts vertical spacing between lines from 0.8 to 2.4 | Slider value (0.80 - 2.40) | Updates `--tester-line-height` CSS variable | Clamps values <0.8 to 0.8, >2.4 to 2.4; preserves 2 decimals | tests/lib/engine.js & PROJECT.md |
| 10 | Type Tester | Kerning / Letter-Spacing Slider | Adjusts character tracking from -0.05em to +0.30em | Slider value (-0.050 - +0.300) | Updates `--tester-letter-spacing` CSS variable | Clamps <-0.05 to -0.05, >0.30 to 0.30; preserves 3 decimals | tests/lib/engine.js & PROJECT.md |
| 11 | Type Tester | Text Alignment Segmented Control | Real-time text alignment switcher (Left, Center, Right, Justify) | Click event on alignment button [L, C, R, J] | Updates `--tester-text-align` CSS variable | Default left alignment on invalid selection | ORIGINAL_REQUEST.md § R2 |
| 12 | Type Tester | Vietnamese-Aware Text Transform | Transforms text case while preserving all Vietnamese compound diacritics | Select case: Uppercase, Lowercase, Title Case, None | Sets `--tester-text-transform` with unicode normalization | Accented characters (e.g. Ệ, Ợ, Đ) never corrupt | tests/tier1_feature_tests.js |
| 13 | Type Tester | Preset Vietnamese Quotes Dropdown | One-click selection of 7 curated Vietnamese test phrases | Select change event | Fills input and updates specimens | Restores previous custom text if cancelled | User workflow analysis |
| 14 | Font Card | Responsive Card Anatomy | Minimalist card with header, badges, preview area, drawer, and footer | Font metadata object from catalog.json | Semantic `<article>` card component | Missing optional fields render empty without error | DISPATCH.md & PROJECT.md |
| 15 | Font Card | 3D Matrix Badges | Visual pill badges for Visual Style, Brand Mood, and Use-case | `font.matrix_3d` or `matrix_*` fields | Rendered colored badge elements | Graceful fallback to category if 3D matrix empty | ORIGINAL_REQUEST.md § R1 |
| 16 | Font Card | Vietnamese Support Status Badge | Prominent badge indicating confirmed Vietnamese diacritics support | `font.vietnamese_support` boolean | Green "VN Ready" badge | Muted indicator if support is false | ORIGINAL_REQUEST.md § R1 & tests/tier1_feature_tests.js |
| 17 | Font Card | In-Card ContentEditable Specimen | Direct in-place editing of individual card preview text | User typing directly inside specimen div | Updates local card text in real time | Disables rich text pasting via plaintext-only | font-manager reference code |
| 18 | Font Card | Multi-Weight Variant Switcher | Clickable weight chips for families with multiple font files | Click on weight chip (e.g. Regular, Bold, Heavy) | Switches card font-weight & loads matching WOFF2 | Preserves active kerning and line-height | ORIGINAL_REQUEST.md § R2 & tests/tier3_pairwise_tests.js |
| 19 | Font Card | Typographic Anatomy & Notes Drawer | Collapsible details drawer showing contrast, axis, x-height, aperture, notes | Click on `<details>` summary | Smoothly reveals anatomy grid and director quote | Collapsed by default to maintain high grid density | ORIGINAL_REQUEST.md § R1 |
| 20 | Font Card | 1-Click Family Drive Download Button | Prominent CTA button opening Google Drive family folder | Click on download button | Opens public folder in new tab with `?usp=sharing` | Warns if drive_folder_url missing | ORIGINAL_REQUEST.md § R3 |
| 21 | Glyph Modal | Vietnamese Glyph Map Dialog | Full-screen accessible modal displaying complete Vietnamese character map | Click "Glyphs" button on card | Opens accessible dialog with 134 accented characters | Closes on Escape, overlay click, or close button | DISPATCH.md & tests/lib/engine.js |
| 22 | Glyph Modal | Unicode Tooltip & 1-Click Copy | Displays character name & hex codepoint; copies character to clipboard | Hover or click on glyph cell | Copies character to clipboard + displays toast alert | Falls back gracefully if clipboard API blocked | User UX exploration |
| 23 | Glyph Modal | Complex Multi-Tone Diagnostic Suite | Dedicated tab testing 15 challenging multi-tone Vietnamese words | Tab selection | Renders complex words at 32px | Immediately flags overlapping accent glyphs | tests/lib/engine.js COMPLEX_VIETNAMESE_WORDS |
| 24 | Typography | Fallback Stack Categorization | System font fallback stacks when WOFF2 is loading or offline | Font category string (Serif, Sans, Mono, Script) | Category-specific system font CSS string | Universal fallback to sans-serif | tests/lib/engine.js getFallbackStack |
| 25 | Performance | Single-Variable CSS Batching | Batches slider modifications into root custom properties | Input event on sliders | Synchronous 60fps rendering across 361 cards | Prevents DOM layout thrashing | Modern browser rendering optimization |

---

## 9. Authoritative Edge Cases Table

## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Font Size Slider | Input value `5` (below minimum 14px) | Automatically clamped to `14px`; slider thumb snaps to minimum boundary; text remains legible. |
| 2 | Font Size Slider | Input value `350` (above maximum 140px) | Automatically clamped to `140px`; prevents card overflow or UI breaking. |
| 3 | Font Size Slider | Malformed input (e.g. `NaN`, `"abc"`, `null`) | Gracefully falls back to default size `36px` without throwing runtime errors. |
| 4 | Line-Height Slider | Underflow input `0.2` (below minimum 0.8) | Clamped to `0.80`; prevents text lines from collapsing onto each other. |
| 5 | Line-Height Slider | Overflow input `4.5` (above maximum 2.4) | Clamped to `2.40`; limits vertical spacing to maintain sensible proportions. |
| 6 | Kerning Slider | Extreme negative kerning `-0.50em` | Clamped to `-0.050em`; prevents glyphs from colliding and becoming unreadable. |
| 7 | Kerning Slider | Extreme positive kerning `+1.00em` | Clamped to `+0.300em`; prevents extreme word fragmentation. |
| 8 | Vietnamese IME | User typing `t-h-u-o-w-n-g-f` in rapid Telex mode | `compositionstart` suppresses instant DOM splitting; final string `"thưởng"` renders cleanly with correct hook and tone. |
| 9 | Text Transform | Uppercase transform on complex word `"nghiêng"` | Transformed to `"NGHIÊNG"`; circumflex accent on `Ê` remains perfectly positioned. |
| 10 | Text Transform | Case transformation on letter `"đ"` and `"Đ"` | Correctly maps `đ` -> `Đ` in uppercase and `Đ` -> `đ` in lowercase (standard `toLowerCase()` can fail in some locales). |
| 11 | Unicode Normalization | Mixed NFC and NFD strings (e.g. `o` + `\u0300` vs `ò`) | Normalized via `.normalize('NFC')` before rendering and comparison; no visual duplicate accents. |
| 12 | Live Text Input | Empty string `""` or whitespace-only `"   "` | Card specimen displays default font name or sample phrase rather than collapsing to 0 height. |
| 13 | Specimen Rendering | Very long continuous word without spaces (e.g. 50 characters) | Specimen container applies `word-break: break-word; overflow-wrap: anywhere;` to prevent breaking card borders. |
| 14 | Rapid Slider Dragging | Mouse drag generating 100+ events per second | Updates root CSS custom property directly; browser compositor handles rendering at native 60fps without lag. |
| 15 | Theme Switcher | Switching theme while Glyph Modal is actively open | Modal inherits CSS variables instantly via CSS cascade; text and background invert cleanly without closing modal. |
| 16 | Network Resilience | WOFF2 font fails to load (offline or CDN 404) | Typography engine applies designated category fallback stack (`Serif` -> Georgia; `Sans` -> system-ui) cleanly. |
| 17 | Multi-Weight Families | Font with only 1 file (e.g. Regular only) | Weight bar renders single disabled chip or hides gracefully, preventing dead-clicks. |
| 18 | Drive Download Link | `drive_folder_url` is missing or invalid | Button is rendered disabled with tooltip `"Đang cập nhật link tải"`, preventing navigation to broken URLs. |
| 19 | Security / XSS | User pastes `<script>alert('XSS')</script>` into preview | Treated strictly as plain text (`textContent` or sanitized value); script never executes. |
| 20 | Mobile Viewport | Device width 320px (iPhone SE / small screens) | Sticky toolbar shifts to compact layout; sliders utilize full width; buttons wrap cleanly without horizontal scroll. |
