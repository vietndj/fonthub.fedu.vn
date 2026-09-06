# Handoff Report: Diacritic & Typographic Adversarial Challenge (Milestone 1)

- **Agent**: `teamwork_preview_challenger_m1_2`
- **Role**: Empirical Challenger (critic, specialist)
- **Target Milestone**: Milestone 1 (`m1_catalog_matrix`)
- **Scope & Specs**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md`, `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`
- **Date**: 2026-09-06T06:11:00Z
- **Verdict**: **REJECT**

---

## 1. Observation

### Observation 1.1: Schema Taxonomy Desynchronization (`matrix_taxonomy.visual_styles` vs `fonts[].matrix_3d.style`)
In `/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json`:
- `matrix_taxonomy.visual_styles` declares exactly 14 official visual styles:
  ```json
  "visual_styles": [
    "Serif Oldstyle", "Serif Modern", "Serif Slab", "Serif Transitional",
    "Sans Humanist", "Sans Neo-grotesque", "Sans Quirky", "Sans Geometric",
    "Sans Rounded", "Sans Condensed", "Sans Extended",
    "Monospace", "Blackletter", "Việt Nam Vintage"
  ]
  ```
- However, querying the actual distribution of `matrix_3d.style` across all 361 font families in `data/catalog.json` reveals:
  ```
  Sans Humanist: 174
  Việt Nam Vintage: 39
  Sans Geometric: 30
  Script: 25              <-- UNREGISTERED STYLE (NOT in matrix_taxonomy.visual_styles)
  Serif Modern: 19
  Sans Condensed: 15
  Serif Oldstyle: 12
  Serif Slab: 9
  Serif Transitional: 8
  Sans Neo-grotesque: 8
  Sans Rounded: 7
  Sans Extended: 7
  Sans Quirky: 6
  Serif: 2               <-- UNREGISTERED STYLE (NOT in matrix_taxonomy.visual_styles)
  Monospace: 0           <-- 0 FONTS (Declared in taxonomy, but completely empty)
  Blackletter: 0         <-- 0 FONTS (Declared in taxonomy, but completely empty)
  ```
- Two specific font families have corrupted/un-subcategorized `matrix_3d.style`:
  - `SVN-Barnyard Serif`: `subcategory: "Serif Oldstyle / Book Classic"`, but `matrix_3d.style: "Serif"`.
  - `SVN-Book Antiqua`: `subcategory: "Serif Oldstyle / Book Classic"`, but `matrix_3d.style: "Serif"`.
  Code origin in `/Users/vietmac/Documents/CODE/fedu-font/scripts/build_catalog.py`, line 346:
  ```python
  345:     elif is_serif:
  346:         category = "Serif"
  347:         matrix_style = "Serif"
  ```
- In `/Users/vietmac/Documents/CODE/fedu-font/scripts/build_catalog.py`, lines 325-327:
  ```python
  325:     elif is_script:
  326:         category = "Blackletter, Script & Monospace"
  327:         matrix_style = "Script"
  ```
  `matrix_style` is hardcoded to `"Script"`, but `"Script"` was omitted from `TAXONOMY_VISUAL_STYLES` (lines 54-69).
- In `/Users/vietmac/Documents/CODE/fedu-font/scripts/validate_catalog.py`, lines 162-168:
  ```python
  162:             if not m_style:
  163:                 errors.append(f"Font '{fam_name}': Missing matrix_3d.style")
  164:             if m_mood not in VALID_MOODS:
  165:                 errors.append(f"Font '{fam_name}': Invalid matrix_3d.mood '{m_mood}'")
  166:             if m_use not in VALID_USE_CASES:
  167:                 errors.append(f"Font '{fam_name}': Invalid matrix_3d.use_case '{m_use}'")
  ```
  The validator validates `m_mood in VALID_MOODS` and `m_use in VALID_USE_CASES`, but **never validates `m_style in TAXONOMY_VISUAL_STYLES`**, allowing invalid visual styles to pass validation silently.

### Observation 1.2: Incomplete Vietnamese Diacritic Coverage in `sample_text`
- Evaluated all 361 fonts in `data/catalog.json` against the standard 67 lowercase and 67 uppercase Vietnamese character sets (defined in `/Users/vietmac/Documents/CODE/fedu-font/tests/lib/engine.js`, lines 15-45).
- In `data/catalog.json`, each font's `sample_text` is drawn from a 25-phrase pool (`SAMPLE_TEXTS_POOL` in `scripts/build_catalog.py`, lines 137-173).
- Test execution command:
  ```bash
  node -e "
  const fs = require('fs');
  const { VIETNAMESE_LOWERCASE, VIETNAMESE_UPPERCASE } = require('./tests/lib/engine');
  const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
  const allSampleTexts = cat.fonts.map(f => f.sample_text).join(' ');
  const missingLower = VIETNAMESE_LOWERCASE.filter(ch => !allSampleTexts.includes(ch));
  const missingUpper = VIETNAMESE_UPPERCASE.filter(ch => !allSampleTexts.includes(ch));
  console.log('Missing lower:', missingLower);
  console.log('Missing upper count:', missingUpper.length);
  "
  ```
- Verbatim result:
  ```
  Missing lower: [ 'ằ', 'ẵ', 'ặ', 'ẫ', 'e', 'è', 'ễ', 'ỉ', 'ĩ', 'ỏ', 'õ', 'ũ', 'ử', 'ỳ', 'ỹ', 'ỵ' ]
  Missing upper count: 46
  ```
- **Crucial finding**: The basic lowercase vowel `'e'` and `'è'` are **100% missing** from every sample text in the entire 361-font catalog (`allSampleTexts.includes('e') === false`).
- 16 lowercase characters and 46 uppercase characters have zero representation across the entire catalog's preview texts.

### Observation 1.3: False-Positive Category Matches in `matchesCategory`
In `/Users/vietmac/Documents/CODE/fedu-font/tests/lib/engine.js`, lines 87-89:
```javascript
  if (tc.includes('mono') || tc.includes('script') || tc.includes('blackletter')) {
    return fc.includes('mono') || fc.includes('script') || fc.includes('blackletter');
  }
```
- When running `SearchEngine.multiFilter(cat.fonts, { category: 'Monospace' })`, it returns 25 results, all of which are Calligraphic Script fonts (e.g., `SVN-Barnyard Script`, `SVN-Boutique Script`, `SVN-Dancing script`).
- Users filtering by "Monospace" or "Blackletter" are presented with handwritten cursive script fonts due to overly coarse category grouping.

### Observation 1.4: Unhandled TypeError in `multiFilter` on Non-String Inputs
In `/Users/vietmac/Documents/CODE/fedu-font/tests/lib/engine.js`:
- Line 73: `const tc = targetCategory.toLowerCase().trim();` (in `matchesCategory`)
- Line 227: `const targetMood = criteria.mood.toLowerCase();`
- Line 237: `const targetUseCase = criteria.use_case.toLowerCase();`
- Line 256: `if (!weights.some(w => w.toLowerCase().includes(criteria.weight.toLowerCase())))`
- Test execution with non-string criteria:
  ```bash
  node -e "
  const { SearchEngine } = require('./tests/lib/engine');
  SearchEngine.multiFilter([], { category: 123 });
  "
  ```
- Verbatim error:
  ```
  TypeError: targetCategory.toLowerCase is not a function
      at matchesCategory (/Users/vietmac/Documents/CODE/fedu-font/tests/lib/engine.js:73:27)
  ```

### Observation 1.5: E2E Test Suite Status
- Test command: `node tests/runner.js`
- Result: 61 passed, 0 failed (78ms).
- Latency Benchmark: 1,000 calls of `instantSearch` across 361 fonts executed in 2,229ms (avg 2.229ms per query, satisfying the <4ms budget).
- Unicode Normalization: 100% of strings in `data/catalog.json` are NFC normalized (0 non-NFC strings). NFC vs NFD query parity demonstrated 0 mismatches across all 134/146 Vietnamese characters.

---

## 2. Logic Chain

1. **Premise 1 (Taxonomy Contract)**: According to `PROJECT.md` § Interface Contracts and `data/catalog.json` § `matrix_taxonomy.visual_styles`, the catalog must adhere to a well-defined 3D Selection Matrix taxonomy of 14 visual styles.
2. **Inference 1**: `catalog.json` violates its own taxonomy contract by populating `matrix_3d.style` with `"Script"` (25 fonts) and `"Serif"` (2 fonts), neither of which exists in `matrix_taxonomy.visual_styles`, while simultaneously leaving `"Monospace"` and `"Blackletter"` with 0 fonts (Observation 1.1).
3. **Premise 2 (Diacritic Completeness)**: `ORIGINAL_REQUEST.md` § R1 & R2, `PROJECT.md` § F05, and `DISPATCH.md` demand verification of complete 67 lowercase and 67 uppercase Vietnamese character diacritic coverage.
4. **Inference 2**: The current `SAMPLE_TEXTS_POOL` in `scripts/build_catalog.py` completely lacks the letter `'e'`, the letter `'è'`, 14 other lowercase accented letters, and 46 uppercase accented letters (Observation 1.2). Therefore, users and automated visual tests cannot evaluate font diacritic rendering for these characters using the catalog preview texts.
5. **Premise 3 (Semantic Filter Accuracy)**: A category filter must return fonts matching the requested classification.
6. **Inference 3**: Filtering by "Monospace" returns calligraphic cursive script fonts (Observation 1.3), corrupting user expectations and search semantics.
7. **Premise 4 (Runtime Robustness)**: Pure static web engines must never crash on malformed inputs.
8. **Inference 4**: `SearchEngine.multiFilter` throws unhandled TypeErrors when given non-string criteria values (Observation 1.4).
9. **Conclusion**: While E2E tests pass their own assertions, the underlying data and classification logic contain regressions and schema violations that must be resolved before proceeding to UI integration (Milestone 3).

---

## 3. Caveats

- **Cloudflare R2 Binary Font Files**: Web font binary files hosted on Cloudflare R2 (`pub-447bd44dfdac4938912655c855b8631c.r2.dev`) were not parsed at the binary TrueType/OpenType table level in this review because local font binary inspection was completed in Milestone 1 Survey.
- **Drive Font Inventory Reality**: The original Google Drive folder (`1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`) legitimately does not contain standalone SVN Monospace or Blackletter font families. The 6 Monospace and 2 Blackletter fonts from the 2022 PDF are listed in `pdf_curated_catalog`, but have `drive_files: []`. The taxonomy should either explicitly designate `Script` as an official 15th visual style or clarify that Monospace/Blackletter are PDF-curated only.

---

## 4. Conclusion

**Verdict: REJECT**

Milestone 1 (`m1_catalog_matrix`) cannot be approved in its current state. The following actionable remediations are required:

1. **Harmonize Visual Style Taxonomy**:
   - In `scripts/build_catalog.py`:
     - Add `"Script"` to `TAXONOMY_VISUAL_STYLES` (or reclassify the 25 script fonts appropriately).
     - Fix `is_serif` logic so `SVN-Barnyard Serif` and `SVN-Book Antiqua` receive `matrix_style = "Serif Oldstyle"` instead of the raw string `"Serif"`.
     - Re-run `python3 scripts/build_catalog.py` to regenerate `data/catalog.json`.
2. **Add Strict Taxonomy Validation**:
   - In `scripts/validate_catalog.py`, assert `m_style in VALID_VISUAL_STYLES` so unregistered styles can never slip through.
3. **Upgrade `sample_text` Diacritic Coverage**:
   - Update `SAMPLE_TEXTS_POOL` in `scripts/build_catalog.py` so that the preview texts collectively cover all 67 lowercase and 67 uppercase Vietnamese characters (including missing letters `e`, `è`, `ằ`, `ẵ`, `ặ`, `ẫ`, `ễ`, `ỉ`, `ĩ`, `ỏ`, `õ`, `ũ`, `ử`, `ỳ`, `ỹ`, `ỵ` and uppercase variants).
4. **Harden `SearchEngine.multiFilter` Type Safety**:
   - In `tests/lib/engine.js` (and upcoming `js/catalog_loader.js`), check `typeof criteria.field === 'string'` before invoking `.toLowerCase()`.
5. **Differentiate Script vs Monospace in `matchesCategory`**:
   - Separate `mono`, `script`, and `blackletter` branches so filtering for Monospace does not return Script fonts.

---

## 5. Verification Method

### 5.1 Project Test Suite
```bash
node tests/runner.js
```
Expected: 61/61 tests pass.

### 5.2 Taxonomy Alignment Check
```bash
node -e "
const fs = require('fs');
const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
const allowed = new Set(cat.matrix_taxonomy.visual_styles);
const invalid = cat.fonts.filter(f => !allowed.has(f.matrix_3d?.style));
console.log('Invalid matrix_3d.style fonts count:', invalid.length);
if (invalid.length > 0) {
  console.log('Sample invalid styles:', invalid.slice(0, 5).map(f => f.name + ': ' + f.matrix_3d?.style));
  process.exit(1);
}
"
```
Condition for approval: `Invalid matrix_3d.style fonts count: 0`.

### 5.3 Complete Diacritic Coverage Check
```bash
node -e "
const fs = require('fs');
const { VIETNAMESE_LOWERCASE } = require('./tests/lib/engine');
const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
const allText = cat.fonts.map(f => f.sample_text).join(' ');
const missing = VIETNAMESE_LOWERCASE.filter(ch => !allText.includes(ch));
console.log('Missing lowercase diacritics in sample_text:', missing);
if (missing.length > 0) process.exit(1);
"
```
Condition for approval: `Missing lowercase diacritics in sample_text: []`.

### 5.4 MultiFilter Type Safety Check
```bash
node -e "
const { SearchEngine } = require('./tests/lib/engine');
const fs = require('fs');
const cat = JSON.parse(fs.readFileSync('data/catalog.json', 'utf8'));
const res = SearchEngine.multiFilter(cat.fonts, { category: 123, mood: null, weight: {} });
console.log('Returned array safely:', Array.isArray(res));
"
```
Condition for approval: Outputs `Returned array safely: true` without throwing `TypeError`.
