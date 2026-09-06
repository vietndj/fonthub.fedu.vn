# Comprehensive Investigation & Worker Remediation Plan: Milestone 1 Hardening

- **Author Agent**: `teamwork_preview_explorer_m1_fix_1`
- **Target Role / Recipient**: `teamwork_preview_worker_m1_fix_1` (Worker) & `parent` (Orchestrator)
- **Target Milestone**: Milestone 1 (`m1_catalog_matrix`)
- **Authority Documents**:
  - Request: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (Mandatory specs R1-R4)
  - Project Scope: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
  - Challenger 2 Report: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_challenger_m1_2/handoff.md`
  - Reviewer 1 Report: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_reviewer_m1_1/handoff.md` § Finding 1
- **Date**: 2026-09-06T06:17:00Z

---

## 1. Executive Summary & Root Cause Analysis

Empirical investigation confirmed all four defect findings reported by Challenger 2 and Reviewer 1:

| Defect # | Module | Manifestation | Root Cause | Impact |
|---|---|---|---|---|
| **D1** | `scripts/build_catalog.py`<br>`data/catalog.json` | 27 fonts have unregistered `matrix_3d.style` (25 `"Script"`, 2 `"Serif"`) | 1) `"Script"` omitted from `TAXONOMY_VISUAL_STYLES`.<br>2) `is_serif` fallback sets raw `"Serif"` instead of `"Serif Oldstyle"`.<br>3) `validate_catalog.py` lacks visual style membership check. | Schema desynchronization; 3D Matrix taxonomy contract violation. |
| **D2** | `scripts/build_catalog.py`<br>`data/catalog.json` | 16 lowercase characters (notably basic `e` and `è`, plus `ằ, ẵ, ặ, ẫ, ễ, ỉ, ĩ, ỏ, õ, ũ, ử, ỳ, ỹ, ỵ`) and 46 uppercase characters missing across entire catalog preview texts | `SAMPLE_TEXTS_POOL` in `build_catalog.py` contains only 25 short phrases lacking comprehensive vowel/tone coverage. | Visual Type Tester cannot preview font rendering for missing Vietnamese diacritic glyphs. |
| **D3** | `tests/lib/engine.js` | Filtering for `category: "Monospace"` returns 25 handwritten cursive `Script` fonts | `matchesCategory` groups `mono`, `script`, and `blackletter` into a single compound condition, matching `category: "Blackletter, Script & Monospace"`. | False-positive category search results; breaks typography isolation. |
| **D4** | `tests/lib/engine.js` | Unhandled `TypeError: targetCategory.toLowerCase is not a function` when filtering with non-string criteria (e.g. `{ category: 123, mood: null }`) | `multiFilter` and `matchesCategory` invoke `.toLowerCase()` without verifying `typeof value === 'string'`. | Engine crash on malformed queries or unexpected frontend filter state. |

---

## 2. Worker Remediation Plan: Exact Code Changes

### Fix 1: Taxonomy Synchronization & Strict Validation

#### Target File 1.1: `scripts/build_catalog.py`

**Change 1.1.A — Add `"Script"` to `TAXONOMY_VISUAL_STYLES` (Lines 54–69)**:
```python
<<<< BEFORE
# Visual Style Dimension (14 standard matrix visual styles)
TAXONOMY_VISUAL_STYLES = [
    "Serif Oldstyle",
    "Serif Modern",
    "Serif Slab",
    "Serif Transitional",
    "Sans Humanist",
    "Sans Neo-grotesque",
    "Sans Quirky",
    "Sans Geometric",
    "Sans Rounded",
    "Sans Condensed",
    "Sans Extended",
    "Monospace",
    "Blackletter",
    "Việt Nam Vintage"
]
====
# Visual Style Dimension (15 standard matrix visual styles)
TAXONOMY_VISUAL_STYLES = [
    "Serif Oldstyle",
    "Serif Modern",
    "Serif Slab",
    "Serif Transitional",
    "Sans Humanist",
    "Sans Neo-grotesque",
    "Sans Quirky",
    "Sans Geometric",
    "Sans Rounded",
    "Sans Condensed",
    "Sans Extended",
    "Monospace",
    "Script",
    "Blackletter",
    "Việt Nam Vintage"
]
>>>>
```

**Change 1.1.B — Fix `is_serif` fallback in `infer_font_classification` (Lines 344–366)**:
```python
<<<< BEFORE
    elif is_serif:
        category = "Serif"
        matrix_style = "Serif"
        if any(k in combined_name for k in ["didot", "bodoni", "modern", "encorpada", "miller", "glamour"]):
            subcategory = "Serif Modern Didone"
            mood = "Luxury & Sang trọng"
            contrast = "Very High"
            axis = "Vertical"
            aperture = "Tight"
        elif any(k in combined_name for k in ["slab", "claren", "egyptian", "rockwell"]):
            subcategory = "Serif Slab / Heavy Terminals"
            mood = "Bold & Tuyên ngôn"
            contrast = "Low"
            axis = "Vertical"
            aperture = "Open"
        else:
            subcategory = "Serif Oldstyle / Book Classic"
            mood = "Nostalgic & Cổ điển"
            contrast = "Medium"
            axis = "Tilted"
            aperture = "Moderate"

        use_case = "Display & Body" if len(styles) >= 6 else ("Body Text" if len(styles) >= 4 else "Display / Headline")
====
    elif is_serif:
        category = "Serif"
        matrix_style = "Serif Oldstyle"
        if any(k in combined_name for k in ["didot", "bodoni", "modern", "encorpada", "miller", "glamour"]):
            subcategory = "Serif Modern Didone"
            matrix_style = "Serif Modern"
            mood = "Luxury & Sang trọng"
            contrast = "Very High"
            axis = "Vertical"
            aperture = "Tight"
        elif any(k in combined_name for k in ["slab", "claren", "egyptian", "rockwell"]):
            subcategory = "Serif Slab / Heavy Terminals"
            matrix_style = "Serif Slab"
            mood = "Bold & Tuyên ngôn"
            contrast = "Low"
            axis = "Vertical"
            aperture = "Open"
        else:
            subcategory = "Serif Oldstyle / Book Classic"
            matrix_style = "Serif Oldstyle"
            mood = "Nostalgic & Cổ điển"
            contrast = "Medium"
            axis = "Tilted"
            aperture = "Moderate"

        use_case = "Display & Body" if len(styles) >= 6 else ("Body Text" if len(styles) >= 4 else "Display / Headline")
>>>>
```

#### Target File 1.2: `scripts/validate_catalog.py`

**Change 1.2.A — Add `VALID_VISUAL_STYLES` constant (Insert around Line 35)**:
```python
<<<< BEFORE
VALID_USE_CASES = {
    "Display / Headline",
    "Body Text",
    "Display & Body"
}
====
VALID_USE_CASES = {
    "Display / Headline",
    "Body Text",
    "Display & Body"
}

VALID_VISUAL_STYLES = {
    "Serif Oldstyle",
    "Serif Modern",
    "Serif Slab",
    "Serif Transitional",
    "Sans Humanist",
    "Sans Neo-grotesque",
    "Sans Quirky",
    "Sans Geometric",
    "Sans Rounded",
    "Sans Condensed",
    "Sans Extended",
    "Monospace",
    "Script",
    "Blackletter",
    "Việt Nam Vintage"
}
>>>>
```

**Change 1.2.B — Update summary `categories_count` validation (Lines 87–88)**:
```python
<<<< BEFORE
    if categories_cnt != 14:
        errors.append(f"Summary categories_count expected 14, got {categories_cnt}")
====
    if categories_cnt != len(VALID_VISUAL_STYLES):
        errors.append(f"Summary categories_count expected {len(VALID_VISUAL_STYLES)}, got {categories_cnt}")
>>>>
```

**Change 1.2.C — Add strict `m_style in VALID_VISUAL_STYLES` assertion (Lines 162–168)**:
```python
<<<< BEFORE
            if not m_style:
                errors.append(f"Font '{fam_name}': Missing matrix_3d.style")
            if m_mood not in VALID_MOODS:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.mood '{m_mood}'")
            if m_use not in VALID_USE_CASES:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.use_case '{m_use}'")
====
            if not m_style:
                errors.append(f"Font '{fam_name}': Missing matrix_3d.style")
            elif m_style not in VALID_VISUAL_STYLES:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.style '{m_style}'")
            if m_mood not in VALID_MOODS:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.mood '{m_mood}'")
            if m_use not in VALID_USE_CASES:
                errors.append(f"Font '{fam_name}': Invalid matrix_3d.use_case '{m_use}'")
>>>>
```

---

### Fix 2: Complete Vietnamese Diacritic Coverage in `SAMPLE_TEXTS_POOL`

#### Target File: `scripts/build_catalog.py`

**Change 2.1 — Replace `SAMPLE_TEXTS_POOL` (Lines 137–173)** with the following 40 culturally resonant sentences, engineered with pool sizes (10, 8, 6, 8, 8) that ensure 100% index coverage across all 361 font families, containing all 73 lowercase and all 73 uppercase Vietnamese characters:

```python
SAMPLE_TEXTS_POOL = {
    "Bold & Tuyên ngôn": [
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM — ĐỘC LẬP TỰ DO HẠNH PHÚC",
        "BẢN LĨNH TIÊN PHONG BỨT PHÁ MỌI GIỚI HẠN VÀ CHINH PHỤC ĐỈNH CAO NGHỆ THUẬT",
        "KIẾN TẠO CHUẨN MỰC MỚI VÀ NỀN TẢNG ỔN ĐỊNH BẰNG SỨC MẠNH CÔNG NGHỆ TIÊN TIẾN",
        "KHẲNG ĐỊNH ĐẲNG CẤP THƯƠNG HIỆU VIỆT VỚI Ý CHÍ THẲNG TIẾN VÀO KỶ NGUYÊN SỐ",
        "NGẪM NGHĨ KỸ CÀNG VỀ MỸ THUẬT, LỄ HỘI VÀ BẢN SẮC DÂN TỘC TRUYỀN THỐNG",
        "GIỮ GÌN CHỮ VIẾT TỈ MỈ RÕ RÀNG TRONG TỪNG NÉT VẼ ĐỒ HỌA CHUYÊN NGHIỆP",
        "ẴM BỒNG TRẺ THƠ VƯỢT VŨ BÃO VÀ GIÓ XOÁY NGHIỆT NGÃ ĐỂ ĐẾN BẾN BỜ BÌNH YÊN",
        "DÙ GẶP GIAN NAN, KỴ BINH VÀ CHIẾN MÃ VƯỢT ĐÈO DỐC HIỂM TRỞ ĐẬP TAN CẰN CỖI",
        "BẢO VỆ MẸ HIỀN VÀ EM BÉ NHỎ DƯỚI LÁ CỜ ĐỎ THẮM TRONG HOÀN CẢNH NGẶT NGHÈO",
        "LỊCH SỬ GHI DẤU KỲ TÍCH VẺ VANG KHI TOÀN DÂN CỞI MỞ ĐỠ ĐẦU NỀN VĂN MINH MỚI"
    ],
    "Luxury & Sang trọng": [
        "Vẻ đẹp thuần khiết vượt thời gian của nghệ thuật chữ và tinh hoa văn hóa",
        "Tôn vinh đẳng cấp thượng lưu trong từng đường nét chạm khắc tỉ mỉ và tinh tế",
        "Nghệ sĩ ngẫm nghĩ về những nét vẽ mềm mại, quyến rũ và diễm lệ của đóa hoa đỗ quyên",
        "Không gian tĩnh lặng nâng niu từng trải nghiệm thẩm mỹ đỉnh cao của giới quý tộc",
        "Bản hòa ca êm dịu giữa kỹ nghệ chế tác thủ công và phong cách kiến trúc hoàng gia",
        "Vợ chàng kỵ sĩ bỡ ngỡ bước vào lâu đài lộng lẫy uy nghiêm giữa màn sương sớm",
        "Nét chữ thanh thoát được chau chuốt kỹ càng, gìn giữ trọn vẹn hồn cốt xưa",
        "Ánh sáng huyền ảo soi rọi từng góc nhỏ, gợi mở xúc cảm thăng hoa thuần khiết"
    ],
    "Tech & Công nghệ": [
        "Hệ thống trí tuệ nhân tạo và tương lai số hóa toàn diện thúc đẩy đổi mới sáng tạo",
        "Tối ưu hóa thuật toán và trải nghiệm người dùng với tốc độ xử lý siêu phân tán",
        "Đội ngũ kỹ sư nỗ lực giải quyết các bài toán kỹ thuật ngặt nghèo trong kỷ nguyên số",
        "Cấu trúc vi mạch và mã nguồn mở vận hành trơn tru ngay cả dưới áp lực tải nặng",
        "Dữ liệu lớn được phân tích rõ ràng, hỗ trợ việc ra quyết định chính xác và nhanh chóng",
        "Mỗi dòng lệnh đều được kiểm thử kỹ lưỡng, đảm bảo an toàn thông tin và bảo mật đa lớp"
    ],
    "Friendly & Nhân văn": [
        "Nụ cười rạng rỡ chào đón ngày mới bình an, ấm áp và tràn đầy năng lượng yêu thương",
        "Người mẹ trẻ ẵm con thơ dạo bước trên hè phố rực rỡ sắc hoa đỏ thắm",
        "Bữa cơm chiều đầm ấm có tiếng cười ríu rít của đàn trẻ nhỏ bên cạnh ông bà",
        "Bác làm vườn cặm cụi chăm sóc từng luống rau xanh mướt mát sau cơn mưa rào",
        "Mỗi trang sách mở ra chân trời mới tươi sáng, nuôi dưỡng tâm hồn nhân ái bao la",
        "Lời ru ngọt ngào của mẹ nâng niu giấc ngủ bé thơ suốt những năm tháng êm đềm",
        "Gia đình sum vầy bên tách chè sen thơm ngát, cùng sẻ chia buồn vui cuộc sống",
        "Sự cảm thông sâu sắc và tình cảm đằm thắm là chiếc cầu nối gắn kết mọi trái tim"
    ],
    "Nostalgic & Cổ điển": [
        "Hà Nội ba mươi sáu phố phường rêu phong cổ kính, nét vẽ biển hiệu vương vấn hoài niệm",
        "Ngõ nhỏ quanh co rợp bóng cây xanh, gợi nhớ tiếng còi tàu sớm và hương hoa sữa nồng nàn",
        "Chiếc xe đạp cũ chở đầy cúc họa mi lướt qua hè phố vắng trong chiều mưa bay lất phất",
        "Người nghệ nhân già tỉ mỉ ngồi nắn nót từng con chữ trên trang giấy dó thô mộc",
        "Cuốn sách cổ nhuốm màu thời gian vẫn giữ nguyên nét mực trang nhã thanh lịch",
        "Tiếng chuông chùa ngân vang trầm mặc giữa không gian tĩnh mịch của buổi hoàng hôn",
        "Ký ức về một thời kỳ hào hoa trên phố biển xưa được tái hiện qua từng bức ảnh đen trắng",
        "Dáng vẻ trầm mặc của mái ngói âm dương trải qua bao thăng trầm dâu bể cuộc đời"
    ]
}
```

---

### Fix 3: Engine Type Safety & Monospace vs Script Isolation

#### Target File: `tests/lib/engine.js`

**Change 3.1 — Upgrade `matchesCategory` (Lines 70–93)**:
```javascript
<<<< BEFORE
function matchesCategory(fontCategory, targetCategory) {
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
  return fc === tc || fc.split(/[\s,/]+/).some(token => token === tc);
}
====
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
>>>>
```

**Change 3.2 — Harden `SearchEngine.multiFilter` with strict type guards (Lines 212–262)**:
```javascript
<<<< BEFORE
  multiFilter(fonts, criteria = {}) {
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
  }
====
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
>>>>
```

---

## 3. Step-by-Step Execution Sequence for Worker

Worker should execute the following 4 sequential steps:

1. **Step 1: Apply code changes to `scripts/build_catalog.py`**:
   - Add `"Script"` to `TAXONOMY_VISUAL_STYLES`.
   - Update `SAMPLE_TEXTS_POOL` with the 40 verified sentences.
   - Fix `is_serif` fallback to set `matrix_style = "Serif Oldstyle"`.

2. **Step 2: Apply code changes to `scripts/validate_catalog.py`**:
   - Define `VALID_VISUAL_STYLES` (15 styles).
   - Assert `m_style in VALID_VISUAL_STYLES`.
   - Update `categories_cnt` validation to `len(VALID_VISUAL_STYLES)`.

3. **Step 3: Apply code changes to `tests/lib/engine.js`**:
   - Update `matchesCategory` to accept `font` context and isolate Monospace from Script.
   - Add string/object type guards across all `multiFilter` criteria.

4. **Step 4: Re-build catalog and execute verification pipeline**:
   ```bash
   python3 scripts/build_catalog.py
   python3 scripts/validate_catalog.py
   node tests/runner.js
   ```

---

## 4. Verification Commands & Acceptance Criteria

Worker and Reviewer must independently verify that:

1. **Taxonomy Schema Check**:
   ```bash
   node -e "
   const fs = require('fs');
   const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
   const allowed = new Set(cat.matrix_taxonomy.visual_styles);
   const invalid = cat.fonts.filter(f => !allowed.has(f.matrix_3d?.style));
   console.log('Invalid styles count:', invalid.length);
   if (invalid.length !== 0) process.exit(1);
   "
   ```
   **Expected**: `Invalid styles count: 0`.

2. **Complete Vietnamese Diacritic Coverage Check**:
   ```bash
   node -e "
   const fs = require('fs');
   const { VIETNAMESE_LOWERCASE, VIETNAMESE_UPPERCASE } = require('./tests/lib/engine');
   const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
   const allText = cat.fonts.map(f => f.sample_text).join(' ');
   const missingLower = VIETNAMESE_LOWERCASE.filter(ch => !allText.includes(ch));
   const missingUpper = VIETNAMESE_UPPERCASE.filter(ch => !allText.includes(ch));
   console.log('Missing lowercase count:', missingLower.length);
   console.log('Missing uppercase count:', missingUpper.length);
   if (missingLower.length !== 0 || missingUpper.length !== 0) process.exit(1);
   "
   ```
   **Expected**: `Missing lowercase count: 0`, `Missing uppercase count: 0`.

3. **Monospace vs Script Filter Isolation Check**:
   ```bash
   node -e "
   const { SearchEngine } = require('./tests/lib/engine');
   const fs = require('fs');
   const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
   const mono = SearchEngine.multiFilter(cat.fonts, { category: 'Monospace' });
   const script = SearchEngine.multiFilter(cat.fonts, { category: 'Script' });
   console.log('Monospace count:', mono.length);
   console.log('Script count:', script.length);
   if (mono.length !== 0 || script.length !== 25) process.exit(1);
   "
   ```
   **Expected**: `Monospace count: 0`, `Script count: 25`.

4. **Engine Type Safety Check**:
   ```bash
   node -e "
   const { SearchEngine } = require('./tests/lib/engine');
   const fs = require('fs');
   const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
   const res = SearchEngine.multiFilter(cat.fonts, { category: 123, mood: null, weight: {} });
   console.log('Safely executed with malformed criteria. Result length:', res.length);
   if (res.length !== cat.fonts.length) process.exit(1);
   "
   ```
   **Expected**: `Safely executed with malformed criteria. Result length: 361`.

5. **Full E2E Test Suite**:
   ```bash
   node tests/runner.js
   ```
   **Expected**: 61/61 passed, 0 failed (exit code 0).
