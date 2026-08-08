# PR Notes: JSONLayout / Test Framework / ConfigReader Design

**Branch:** `JSONLayout_test_framework_configreader_design`

**Base:** rebaselined onto `origin/main` after the RoutingLayer PR (#4) merged, so
this PR's diff is only the increment below, not a re-introduction of RoutingLayer.

**Scope note:** this PR covers JSONLayout, the test framework, and the ConfigReader
**design** (Design §4.5). The design write-up was started but is not yet finished
and stays in this PR. The ConfigReader *implementation* (Build-Checklist F1-F4)
remains post-1.0 backlog.

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
- `src/Public/Logger.lvclass/WaitForSnapshot.vi` (private): synchronous readiness
  barrier. Waits on the manager's Snapshot notifier until `appenderEnqueuers`
  count reaches `minEnqueuers` (or a bounded timeout → error 5030). Deadline-based
  loop (`deadline = start + timeout`; each iteration waits the remaining time),
  so total wait is bounded. Outputs a valid Snapshot only on the met path; on
  timeout, `error out` (5030) is the authoritative signal.

Test-support fixtures/helpers (`tests/Support/`):

- `Open Test Mgr.vi` — reduced to `Initialize` only (`enableDefaultFile=FALSE`):
  brings the manager to the "ready, empty" baseline and returns the logger. No
  longer registers an appender or creates a temp root (decoupled).
- `Register Relay Appender.vi` — Arrange helper: builds a queue-mode relay
  appender for a given `id` (optional `filter`/`queueBound` inputs; defaults
  Mirror/permissive and `-1`), registers it (blocks on `WaitForSnapshot`), and
  returns the named-queue refnum via `Read relayQueue` for the test to drain.
- `Close Test Mgr.vi`, `Setup - create temp root.vi`, `Tear Down - delete root
  temp.vi` — composed per test (relay-queue tests need no temp root).

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
- **`Logger.Initialize` wired to `WaitForSnapshot`** (readiness, `minEnqueuers=0`):
  returns only once the manager has posted its initial Snapshot, so the returned
  logger is ready to log. A manager that dies on entry never posts → `Initialize`
  returns 5030 (loud) instead of a dead-but-valid-looking logger. Confirmed both
  directions (`enableDefaultFile=FALSE` → clean; `=TRUE` empty-id default → 5030).
- **`Logger.RegisterAppender` wired to `WaitForSnapshot`** (`minEnqueuers=preCount+1`):
  reads the pre-count, sends, then blocks until the appender appears in a Snapshot,
  so callers can log to it deterministically. Whole peek/send/wait sequence sits
  inside the manager-enqueuer valid-refnum case; no-op passthrough (5029) otherwise.
  This replaced the flaky 1 s fixture delay.
- **`enableDefaultFile` validation gating** (5024 fix): `ValidateLumberjackConfigDTO`
  now gates the default-file validator chain on `enableDefaultFile`, so a disabled
  default file is neither resolved nor validated. Corrects the earlier silent
  manager death on an empty-id default config.
- **`Appender.GetID` promoted to public** (read-only id accessor; dissolves a
  friend-scope issue for `Logger`/tests rather than adding friend edges).

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

- **Integration tier (in progress):** fixtures/helpers built (`Open Test Mgr`,
  `Register Relay Appender`, temp-root setup/teardown). Passing on the decoupled
  fixture + helper: **Delivery - single appender** and **Broadcast - fan-out**
  (3 appenders, identical-payload + exactly-once asserts), both relay queue mode.
  Remaining launched-actor tests: register/unregister, relay message-mode,
  rollover, flush-on-shutdown.
- **ConfigReader design (Design §4.5):** started, not finished; to be completed in
  this PR before review. Design write-up only, the implementation (F1-F4) stays
  post-1.0 backlog.
- **`Support.lvlib` extraction:** Build-Checklist item 28a, a separate structural
  refactor to do before the project is considered done, not in this PR.
- **Optional additional unit tests:** CSV column order, tag `Sanitize`.
