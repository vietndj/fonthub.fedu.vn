#!/usr/bin/env node
/**
 * tests/runner.js
 * Master Standalone CLI Test Runner for fedu.vn/font Interactive Type Hub.
 *
 * Runs all 4 test tiers (T1-T4) with zero external dependencies.
 * Usage:
 *   node tests/runner.js
 *   node tests/runner.js --tier=1
 *   node tests/runner.js --tier=2
 *   node tests/runner.js --tier=3
 *   node tests/runner.js --tier=4
 *   node tests/runner.js --verbose
 */

const process = require('process');
const { runTier1Tests } = require('./tier1_feature_tests');
const { runTier2Tests } = require('./tier2_boundary_tests');
const { runTier3Tests } = require('./tier3_pairwise_tests');
const { runTier4Tests } = require('./tier4_workload_tests');

class TestReporter {
  constructor(verbose = false) {
    this.verbose = verbose;
    this.currentSuite = '';
    this.results = [];
    this.suiteResults = {};
    this.startTime = Date.now();
  }

  startSuite(name) {
    this.currentSuite = name;
    if (!this.suiteResults[name]) {
      this.suiteResults[name] = { total: 0, passed: 0, failed: 0, tests: [] };
    }
    console.log(`\n\x1b[1m\x1b[36m▶ Suite: ${name}\x1b[0m`);
  }

  test(name, fn) {
    const suite = this.suiteResults[this.currentSuite];
    suite.total++;
    const testStart = Date.now();

    try {
      fn();
      const duration = Date.now() - testStart;
      suite.passed++;
      this.results.push({ suite: this.currentSuite, name, status: 'PASS', duration });
      console.log(`  \x1b[32m✔ PASS\x1b[0m \x1b[90m[${duration}ms]\x1b[0m ${name}`);
    } catch (err) {
      const duration = Date.now() - testStart;
      suite.failed++;
      this.results.push({ suite: this.currentSuite, name, status: 'FAIL', duration, error: err });
      console.log(`  \x1b[31m✖ FAIL\x1b[0m \x1b[90m[${duration}ms]\x1b[0m ${name}`);
      console.log(`    \x1b[31mError: ${err.message}\x1b[0m`);
      if (this.verbose && err.stack) {
        console.log(`    \x1b[90m${err.stack.split('\n').slice(1, 4).join('\n    ')}\x1b[0m`);
      }
    }
  }

  summary() {
    const totalTime = Date.now() - this.startTime;
    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;

    console.log('\n' + '═'.repeat(60));
    console.log('\x1b[1mTEST EXECUTION SUMMARY\x1b[0m');
    console.log('═'.repeat(60));

    for (const [suiteName, stats] of Object.entries(this.suiteResults)) {
      totalTests += stats.total;
      totalPassed += stats.passed;
      totalFailed += stats.failed;

      const icon = stats.failed === 0 ? '\x1b[32m✔' : '\x1b[31m✖';
      console.log(
        ` ${icon} \x1b[1m${suiteName}\x1b[0m: ${stats.passed}/${stats.total} passed ` +
        (stats.failed > 0 ? `(\x1b[31m${stats.failed} failed\x1b[0m)` : '')
      );
    }

    console.log('─'.repeat(60));
    const allPassed = totalFailed === 0;
    const finalColor = allPassed ? '\x1b[32m' : '\x1b[31m';
    const finalStatus = allPassed ? 'ALL TESTS PASSED' : 'TESTS FAILED';

    console.log(
      `${finalColor}\x1b[1m${finalStatus}\x1b[0m: ${totalPassed} passed, ${totalFailed} failed of ${totalTests} total tests (${totalTime}ms)`
    );
    console.log('═'.repeat(60) + '\n');

    return allPassed;
  }
}

function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes('--verbose') || args.includes('-v');

  let targetTier = null;
  for (const arg of args) {
    if (arg.startsWith('--tier=')) {
      targetTier = parseInt(arg.split('=')[1], 10);
    } else if (arg === '-t' && args[args.indexOf(arg) + 1]) {
      targetTier = parseInt(args[args.indexOf(arg) + 1], 10);
    }
  }

  console.log('\x1b[1m\x1b[35m============================================================\x1b[0m');
  console.log('\x1b[1m\x1b[35m fedu.vn/font Interactive Type Hub — E2E Test Suite\x1b[0m');
  console.log('\x1b[1m\x1b[35m============================================================\x1b[0m');

  const reporter = new TestReporter(verbose);

  try {
    if (!targetTier || targetTier === 1) {
      runTier1Tests(reporter);
    }
    if (!targetTier || targetTier === 2) {
      runTier2Tests(reporter);
    }
    if (!targetTier || targetTier === 3) {
      runTier3Tests(reporter);
    }
    if (!targetTier || targetTier === 4) {
      runTier4Tests(reporter);
    }

    const success = reporter.summary();
    process.exit(success ? 0 : 1);
  } catch (fatalErr) {
    console.error('\n\x1b[31mFATAL TEST EXECUTION ERROR:\x1b[0m', fatalErr);
    process.exit(2);
  }
}

if (require.main === module) {
  main();
}
