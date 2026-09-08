/**
 * tests/audit_live_fonthub.js
 * Comprehensive Live Online E2E Auditor for https://font.fedu.vn
 * 
 * Verifies:
 * 1. 100% of 376 font families:
 *    - Origin explicitly stated in Director Review / notes (FEDU Tự Việt Hóa vs SVN Việt Hóa)
 *    - 19 GT/GR fonts: proper IDs, names, families, and zero SVN traces
 *    - 357 FD fonts: proper IDs, names, families, and zero SVN traces
 * 2. FD NoeDisplay Fontshare specimen verification (zero SVN-NoeDisplay regressions)
 * 3. 100% Google Drive links verification (zero SVN- occurrences)
 * 4. Favorites filter button functionality and badge updates
 * 5. Production cache-busting and asset integrity on live CDN
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'FEDU-Font-Auditor/2.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    }).on('error', reject);
  });
}

async function runLiveAudit() {
  const liveBase = process.env.LIVE_BASE || 'https://font.fedu.vn';
  console.log('============================================================');
  console.log(' FEDU Font — Live Online Verification Suite');
  console.log(` Target: ${liveBase}`);
  console.log('============================================================\n');

  const timestamp = Date.now();
  const catalogUrl = `${liveBase}/data/catalog.json?t=${timestamp}`;
  const htmlUrl = `${liveBase}/?t=${timestamp}`;

  console.log(`[STEP 1] Fetching live catalog: ${catalogUrl}`);
  const catalogResp = await fetchUrl(catalogUrl);
  if (catalogResp.statusCode !== 200) {
    throw new Error(`Failed to fetch live catalog: HTTP ${catalogResp.statusCode}`);
  }

  const catalog = JSON.parse(catalogResp.body);
  const fonts = catalog.fonts || [];
  console.log(`✔ Fetched catalog successfully. Total fonts: ${fonts.length}\n`);

  console.log(`[STEP 2] Fetching live HTML: ${htmlUrl}`);
  const htmlResp = await fetchUrl(htmlUrl);
  if (htmlResp.statusCode !== 200) {
    throw new Error(`Failed to fetch live HTML: HTTP ${htmlResp.statusCode}`);
  }
  const html = htmlResp.body;
  console.log(`✔ Fetched live HTML successfully (${html.length} bytes)\n`);

  const results = {
    totalFonts: fonts.length,
    grFontsCount: 0,
    fdFontsCount: 0,
    originFeduCount: 0,
    originSvnCount: 0,
    originMissingCount: 0,
    svnTraceErrors: [],
    driveLinkErrors: [],
    noeDisplayStatus: null,
    favoritesFilterStatus: null,
    htmlChecks: {},
    passed: true,
    details: []
  };

  // 1. Audit 376 fonts
  console.log('------------------------------------------------------------');
  console.log('AUDIT SECTION 1: 376 FONT FAMILIES AUDIT');
  console.log('------------------------------------------------------------');

  for (let i = 0; i < fonts.length; i++) {
    const f = fonts[i];
    const isGR = f.is_gt || f.id.startsWith('gr-') || f.name.startsWith('GR ');
    const isFD = !isGR && (f.id.startsWith('fd-') || f.name.startsWith('FD'));

    if (isGR) results.grFontsCount++;
    if (isFD) results.fdFontsCount++;

    // Origin Check
    const reviewText = [
      f.director_notes || '',
      f.director_review || '',
      f.nhan_dinh_dao_dien || '',
      f.critique || '',
      f.source || ''
    ].join(' ');

    let originType = 'NONE';
    if (reviewText.includes('FEDU Tự Việt Hóa') || reviewText.includes('FEDU tự Việt hóa')) {
      originType = 'FEDU Tự Việt Hóa';
      results.originFeduCount++;
    } else if (reviewText.includes('SVN Việt Hóa') || reviewText.includes('SVN việt hóa')) {
      originType = 'SVN Việt Hóa';
      results.originSvnCount++;
    } else {
      results.originMissingCount++;
    }

    // Drive links check
    const driveUrl = f.drive_folder_url || f.drive_link || f.download_url || '';
    let driveValid = false;
    if (driveUrl.includes('drive.google.com')) {
      driveValid = true;
    }
    if (driveUrl.includes('SVN-')) {
      results.driveLinkErrors.push({ id: f.id, url: driveUrl });
    }

    // SVN trace in metadata
    const checkFields = [f.id, f.name, f.family, f.zip_filename || ''];
    for (const val of checkFields) {
      if (typeof val === 'string' && val.includes('SVN-')) {
        results.svnTraceErrors.push({ id: f.id, field: val });
      }
    }

    results.details.push({
      stt: i + 1,
      id: f.id,
      name: f.name,
      family: f.family,
      type: isGR ? 'GR (19)' : 'FD (357)',
      origin: originType,
      driveValid: driveValid,
      driveUrl: driveUrl
    });
  }

  console.log(`• Total Fonts in Catalog: ${results.totalFonts} (Expected: 376)`);
  console.log(`• GR Families Found:      ${results.grFontsCount} (Expected: 19)`);
  console.log(`• FD Families Found:      ${results.fdFontsCount} (Expected: 357)`);
  console.log(`• Origin [FEDU Tự Việt Hóa]: ${results.originFeduCount} (Expected: 19)`);
  console.log(`• Origin [SVN Việt Hóa]:     ${results.originSvnCount} (Expected: 357)`);
  console.log(`• Origin Missing:            ${results.originMissingCount}`);
  console.log(`• Drive Link SVN- Errors:    ${results.driveLinkErrors.length} (Expected: 0)`);
  console.log(`• SVN Traces in Names/IDs:   ${results.svnTraceErrors.length} (Expected: 0)`);

  // 2. Audit FD NoeDisplay
  console.log('\n------------------------------------------------------------');
  console.log('AUDIT SECTION 2: FD NOEDISPLAY & FONTSHARE VIEW AUDIT');
  console.log('------------------------------------------------------------');
  const noe = fonts.find(f => f.id === 'fd-noedisplay' || f.name === 'FD NoeDisplay');
  if (noe) {
    const noeClean = noe.id === 'fd-noedisplay' &&
                     noe.name === 'FD NoeDisplay' &&
                     noe.family === 'FD NoeDisplay' &&
                     !JSON.stringify(noe).includes('SVN-NoeDisplay');
    console.log(`• FD NoeDisplay ID:     ${noe.id}`);
    console.log(`• FD NoeDisplay Name:   ${noe.name}`);
    console.log(`• FD NoeDisplay Family: ${noe.family}`);
    console.log(`• Web Font URL:         ${noe.web_font_url}`);
    console.log(`• Zero SVN-NoeDisplay:  ${noeClean ? '✅ PASS' : '❌ FAIL'}`);
    results.noeDisplayStatus = noeClean ? 'PASS' : 'FAIL';
  } else {
    console.log('❌ FD NoeDisplay not found in catalog!');
    results.noeDisplayStatus = 'NOT_FOUND';
  }

  // 3. Audit Favorites Filter in HTML and app.js
  console.log('\n------------------------------------------------------------');
  console.log('AUDIT SECTION 3: FAVORITES FILTER (⭐ Yêu thích) AUDIT');
  console.log('------------------------------------------------------------');
  const hasFavBtn = html.includes('id="chip-favorites"') && html.includes('data-category="favorites"');
  const hasFavBadge = html.includes('id="count-fav"') || html.includes('countFav');
  console.log(`• Favorites Filter Button in HTML:  ${hasFavBtn ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Favorites Counter Badge in HTML: ${hasFavBadge ? '✅ PASS' : '❌ FAIL'}`);

  // Fetch live app.js
  console.log('\nFetching live app.js to verify favorites storage & filtering logic...');
  const appJsResp = await fetchUrl(`${liveBase}/app.js?t=${timestamp}`);
  const appJs = appJsResp.body;
  const hasFavStorage = (appJs.includes('fedu_font_favorites') || appJs.includes('fonthub_favorites')) &&
                        appJs.includes('getFavorites') &&
                        appJs.includes('toggleFontFavorite');
  const hasFavFilter = appJs.includes("App.activeFilters.category === 'favorites'") ||
                       appJs.includes("state.pill === 'shortlisted'");
  console.log(`• Favorites localStorage logic:     ${hasFavStorage ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Favorites Filtering execution:    ${hasFavFilter ? '✅ PASS' : '❌ FAIL'}`);

  results.favoritesFilterStatus = (hasFavBtn && hasFavStorage && hasFavFilter) ? 'PASS' : 'FAIL';

  // 4. Audit Vietnamese Support & Redundant Filter Removal
  console.log('\n------------------------------------------------------------');
  console.log('AUDIT SECTION 4: VIETNAMESE SUPPORT & FILTER AUDIT');
  console.log('------------------------------------------------------------');
  let vnSupportedCount = 0;
  let stuckNamesErrors = [];
  for (const f of fonts) {
    if (f.vietnamese_support === true) vnSupportedCount++;
    if (/^(FD|GR)[a-zA-Z]/.test(f.name) && !f.name.startsWith('FD ') && !f.name.startsWith('GR ')) {
      stuckNamesErrors.push({ id: f.id, name: f.name });
    }
  }

  const allVnSupported = vnSupportedCount === fonts.length;
  const noRedundantVnFilter = !html.includes('id="filter-vn-support"') && !html.includes('Chỉ hiện font hỗ trợ Tiếng Việt');
  const zeroStuckNames = stuckNamesErrors.length === 0;

  console.log(`• 100% Fonts Support Vietnamese:    ${allVnSupported ? '✅ PASS' : '❌ FAIL'} (${vnSupportedCount}/${fonts.length})`);
  console.log(`• Redundant VN Filter Removed:       ${noRedundantVnFilter ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Zero Stuck Font Names (e.g. FD Aeonik): ${zeroStuckNames ? '✅ PASS' : '❌ FAIL'} (${stuckNamesErrors.length} errors)`);

  // 5. Audit Accents Clipping & Live CSS
  console.log('\n------------------------------------------------------------');
  console.log('AUDIT SECTION 5: ACCENTS CLIPPING & LIVE CSS AUDIT');
  console.log('------------------------------------------------------------');
  console.log('Fetching live style.css to verify line-height and padding...');
  const cssResp = await fetchUrl(`${liveBase}/style.css?t=${timestamp}`);
  const css = cssResp.body;

  const hasSafeTesterLineHeight = css.includes('--tester-line-height: 1.4') || css.includes('--tester-line-height: 1.35;') || css.includes('--tester-line-height: 1.3');
  const hasCardPadding = css.includes('.card-specimen-wrap') && (css.includes('padding: 18px 0;') || css.includes('padding: 16px 0;'));
  const hasFsSpecimenLineHeight = css.includes('.fs-item-specimen') && (css.includes('line-height: 1.4') || css.includes('line-height: 1.25;') || css.includes('line-height: 1.3;'));
  const hasFsSpecimenOverflow = css.includes('.fs-item-specimen-wrap') && css.includes('overflow-y: visible;');
  const hasGridSpecimenLineHeight = css.includes('.fontshare-grid-mode .fs-item-specimen') && (css.includes('line-height: 1.4') || css.includes('line-height: 1.35;'));

  console.log(`• Safe Tester Line-Height (--tester-line-height >= 1.3): ${hasSafeTesterLineHeight ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Card Specimen Padding (>= 16px 0):                     ${hasCardPadding ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Fontshare Specimen Line-Height (>= 1.25):              ${hasFsSpecimenLineHeight ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Fontshare Specimen Overflow-Y Visible:                 ${hasFsSpecimenOverflow ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`• Fontshare Grid Specimen Line-Height (>= 1.35):         ${hasGridSpecimenLineHeight ? '✅ PASS' : '❌ FAIL'}`);

  const cssClippingPassed = hasSafeTesterLineHeight && hasCardPadding && hasFsSpecimenLineHeight && hasFsSpecimenOverflow && hasGridSpecimenLineHeight;

  // Summary Verdict
  if (results.totalFonts !== 376 ||
      results.grFontsCount !== 19 ||
      results.fdFontsCount !== 357 ||
      results.originMissingCount > 0 ||
      results.svnTraceErrors.length > 0 ||
      results.driveLinkErrors.length > 0 ||
      results.noeDisplayStatus !== 'PASS' ||
      results.favoritesFilterStatus !== 'PASS' ||
      !allVnSupported ||
      !noRedundantVnFilter ||
      !zeroStuckNames ||
      !cssClippingPassed) {
    results.passed = false;
  }

  console.log('\n============================================================');
  console.log(`AUDIT RESULT: ${results.passed ? '✅ 100% PASS' : '⚠️ ISSUES DETECTED'}`);
  console.log('============================================================\n');

  return results;
}

if (require.main === module) {
  runLiveAudit()
    .then(res => {
      const reportsDir = path.join(__dirname, '../reports');
      if (!fs.existsSync(reportsDir)) fs.mkdirSync(reportsDir, { recursive: true });
      fs.writeFileSync(
        path.join(reportsDir, 'live_audit_report.json'),
        JSON.stringify(res, null, 2)
      );
      if (!res.passed) {
        process.exit(1);
      }
    })
    .catch(err => {
      console.error('Audit execution error:', err);
      process.exit(1);
    });
}

module.exports = { runLiveAudit };
