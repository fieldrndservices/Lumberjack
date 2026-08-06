# PR Notes: JSONLayout / Test Framework / ConfigReader Design

**Branch:** `JSONLayout_test_framework_configreader_design`

**Intended base:** stacked on `RoutingLayer_Facade_Singleton_Implementation`.
Merge the RoutingLayer PR first, then rebaseline this branch onto the updated
`main` so this PR's diff is only the increment below (not a re-introduction of the
RoutingLayer work).

**Status:** Draft. All entered descriptions and drafted test/code content remain
subject to SOP-117 human review before being treated as authoritative.

---

## 1. What this PR adds (increment over RoutingLayer)

### New files (reliable, these paths do not exist in RoutingLayer)

Caraya test framework:

- `tests/Tests.lvlib` (friend of `Lumberjack.lvlib`)
- `tests/Test.vi` (suite runner)
- `tests/All Unit Tests.vi` (unit-tier aggregator)
- `tests/Unit/Severity - rank compare.vi` (5 assertions)
- `tests/Unit/Layout - CSV quoting.vi` (6 assertions)
- `tests/Unit/Filter - tag prefix.vi` (5 assertions)
- `tests/Unit/Filter - level range.vi` (6 assertions)
- `tests/Unit/Severity - name round trip.vi` (7 assertions)

Documentation:

- `docs/Doc-Terminal-Audit.md` (terminal + typedef description audit; complete)

Five unit tests, 29 assertions, all passing through `Test.vi`.

### In-place edits

- **Logic:** `src/Support/Filter/RoutedFilterMatch.vi` implemented (was a stub),
  via TDD against `Filter - tag prefix` and `Filter - level range`.
- **Descriptions:** terminal descriptions across ~40 VIs and field/description
  updates on the config typedefs (native and DTO mirrors), including renaming the
  DTO `fileConfig` field to `file` to mirror the native side. The exact inventory
  of every terminal and typedef touched is in `Doc-Terminal-Audit.md` sections 2
  and 4.

---

## 2. Do not commit / gitignore

A `.gitignore` update is committed on this branch. It now covers:

- `Lumberjack.dragon` (via `*.dragon`), plus `*.aliases` / `*.lvlps` /
  `*.UserState` / `.cache/`.
- Regenerable docs: `docs/HTMLReport/*.html`, `docs/HTMLReport/images/*.jpg`,
  `docs/*.docx`, `docs/*.pdf`.
- Build outputs: `*.lvlibp`, `*.vip`, `/builds/`.

- Caraya output: `tests/Test Results/*.txt`.

All flagged artifacts are now ignored, and the previously-tracked report/doc
artifacts have been removed from tracking (`git ls-files` shows none remaining),
so nothing is outstanding on the ignore front.

---

## 3. Reviewer note: LabVIEW binary churn

A git file-diff of this branch against the RoutingLayer tip flags ~315 files
(essentially the whole library), because LabVIEW re-saves a VI's binary on every
open or recompile even with no semantic change. That diff is therefore not a
usable change list. Use this document plus `Doc-Terminal-Audit.md` as the review
checklist for what actually changed, rather than the raw binary diff.

---

## 4. Still open for this branch's scope (not in this increment)

- **`JSONLayout.Format` is still a STUB.** Needs the `JSONEscapeString` helper and
  the hand-assembled slog-shaped `Format`, per Build-Checklist item 7. This is the
  headline JSONLayout deliverable and is not yet done.
- **Integration tier not started.** Temp-root `SetUp` / `TearDown` fixtures and any
  launched-actor tests (`tests/Integration/`, `tests/Support/`).
- **ConfigReader design (Design §4.5) not addressed** this session (the
  "configreader_design" part of the branch name).
- **Optional additional unit tests:** CSV column order, tag `Sanitize`.
