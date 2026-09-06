# Task Assignment: E2E Testing Track Orchestrator

- **Role**: E2E Testing Orchestrator (`e2e_testing_track`)
- **Assigned Directory**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/sub_orch_e2e`
- **Mandatory Reading**: `/Users/vietmac/Documents/CODE/fedu-font/ORIGINAL_REQUEST.md` (MANDATORY: read first)
- **Scope Reference**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/orchestrator_1/PROJECT.md`

## Mission & Scope
As the E2E Testing Orchestrator, design and implement an independent, opaque-box, requirement-driven test suite for the `fedu.vn/font Interactive Type Hub` project.
1. Create `TEST_INFRA.md` at `/Users/vietmac/Documents/CODE/fedu-font/.agents/sub_orch_e2e/TEST_INFRA.md` (and copy/link to project root) documenting test philosophy, runner architecture, and feature checklist.
2. Design test cases across the 4 systematic tiers:
   - **Tier 1: Feature Coverage (>=5 per feature)**: Test each requirement (R1 data completeness, R2 interactive type tester, R3 Drive packaging & links, R4 search & filters) in isolation.
   - **Tier 2: Boundary & Corner Cases (>=5 per feature)**: Extreme font sizes (14px, 140px, negative kerning), complex Vietnamese diacritics (Hội, Thưởng, Khuyến, Nghiêng), empty search queries, non-existent categories.
   - **Tier 3: Cross-Feature Interactions (Pairwise)**: Search + Category filter + Mood filter + Type Tester text change simultaneously.
   - **Tier 4: Real-World Workload Scenarios (>=5 scenarios)**: End-to-end designer workflows (e.g., finding a high-contrast Luxury Serif font for a fashion headline, testing Vietnamese accents, switching to Dark Mode, clicking Drive download).
3. Build the test runner (e.g. `tests/runner.js` or Python test runner) runnable via CLI without heavy browser dependencies (e.g. Node.js with JSDOM / headless test runner or Python tests for data & HTML/DOM).
4. When test suite is ready and verified, publish `TEST_READY.md` summarizing total test counts and execution command.
