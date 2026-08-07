# PR Notes: JSONLayout / Test Framework

**Branch:** `JSONLayout_test_framework_configreader_design`

**Base:** rebaselined onto `origin/main` after the RoutingLayer PR (#4) merged, so
this PR's diff is only the increment below, not a re-introduction of RoutingLayer.

**Scope note:** the ConfigReader design (the "configreader_design" in the branch
name) is **deferred to a follow-up PR**. This PR delivers JSONLayout and the test
framework.

**Status:** Draft. All entered descriptions and drafted test/code content remain
subject to SOP-117 human review before being treated as authoritative.

---

## 1. What this PR adds (increment over main)

### New files

Caraya test framework (8 unit tests, 43 assertions, all passing via `Test.vi`):

- `tests/Tests.lvlib` (friend of `Lumberjack.lvlib`)
- `tests/Test.vi` (suite runner)
- `tests/All Unit Tests.vi` (unit-tier aggregator)
- `tests/Unit/Severity - rank compare.vi` (5)
- `tests/Unit/Layout - CSV quoting.vi` (6)
- `tests/Unit/Filter - tag prefix.vi` (5)
- `tests/Unit/Filter - level range.vi` (6)
- `tests/Unit/Severity - name round trip.vi` (7)
- `tests/Unit/Layout - JSON escape string.vi` (7)
- `tests/Unit/Layout - ISO 8601 timestamp.vi` (3)
- `tests/Unit/Layout - JSON format.vi` (4)

New library VIs:

- `src/Support/JSON/JSONEscapeString.vi` (JSON string-literal escaper, community)
- `src/Support/Time/FormatTimeString.vi` (shared ISO 8601 timestamp helper,
  ms precision, Z/offset per useUTC)

Documentation:

- `docs/Doc-Terminal-Audit.md` (terminal + typedef description audit; complete)
- `docs/PR-Notes.md` (this file)

### In-place edits

- **`JSONLayout.Format` implemented** (was a stub): hand-assembled slog object
  (`time`, `level`, `msg`, then `sourceTag`/`originVI` omitted when empty),
  values via `JSONEscapeString`, timestamp via `FormatTimeString`, error-guarded,
  one line, no terminator.
- **`CSVLayout.Format` refactored** to call `FormatTimeString` instead of its
  inline timestamp code, so CSV and JSON render the same instant identically.
- **`RoutedFilterMatch.vi` implemented** (was a stub), via TDD against the
  `Filter - tag prefix` and `Filter - level range` tests.
- **Descriptions** across ~40 VIs and field/description updates on the config
  typedefs (native and DTO mirrors), including renaming the DTO `fileConfig` field
  to `file` to mirror the native side. Full inventory in `Doc-Terminal-Audit.md`
  sections 2 and 4.

---

## 2. Do not commit / gitignore

A `.gitignore` update is committed on this branch. It covers:

- `Lumberjack.dragon` (via `*.dragon`), plus `*.aliases` / `*.lvlps` /
  `*.UserState` / `.cache/`.
- Regenerable docs: `docs/HTMLReport/*.html`, `docs/HTMLReport/images/*.jpg`,
  `docs/*.docx`, `docs/*.pdf`.
- Build outputs: `*.lvlibp`, `*.vip`, `/builds/`.
- Caraya output: `tests/Test Results/*.txt`.

All flagged artifacts are ignored, and the previously-tracked report/doc artifacts
have been removed from tracking, so nothing is outstanding on the ignore front.

---

## 3. Reviewer note: LabVIEW binary churn

LabVIEW re-saves a VI's binary on open/recompile even with no semantic change, so a
raw file-diff of the branch overstates what changed. Use this document plus
`Doc-Terminal-Audit.md` as the review checklist for what actually changed, rather
than the binary diff.

---

## 4. Still open

- **Integration tier (next up this PR):** temp-root `SetUp` / `TearDown` fixtures
  (`tests/Support/`) and launched-actor tests (`tests/Integration/`), broadcast,
  register/unregister, relay delivery, rollover, flush-on-shutdown.
- **ConfigReader design (Design §4.5):** deferred to a follow-up PR.
- **`Support.lvlib` extraction:** Build-Checklist item 28a, a separate structural
  refactor to do before the project is considered done, not in this PR.
- **Optional additional unit tests:** CSV column order, tag `Sanitize`.
