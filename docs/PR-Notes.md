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
- `src/Public/Logger.lvclass/WaitForSnapshot.vi` (private): synchronous barrier
  on the Snapshot notifier. Blocks until a predicate over the Snapshot holds, or a
  bounded deadline expires (error 5030). Predicate via `SnapshotWaitMode`:
  `AnySnapshot` (readiness), `IDPresent` (a `targetID` appears), `IDAbsent` (a
  `targetID` is gone / never present). Id-based, not count-based, so it's robust to
  ordering/concurrency and needs no pre-count. Deadline loop
  (`deadline = start + timeout`, each wait consumes the remaining time). Outputs a
  valid Snapshot only on the met path.
- `src/Public/Logger.lvclass/SnapshotHasID.vi` (private): pure predicate, scans a
  Snapshot's `appenders` array for an exact id; short-circuits on match. Used by
  `WaitForSnapshot` for the `IDPresent`/`IDAbsent` modes.
- `src/TypeDefs/SnapshotWaitMode.ctl`: enum (`AnySnapshot`/`IDPresent`/`IDAbsent`)
  selecting the barrier condition.
- `src/TypeDefs/ManagerLaunchInputs.ctl`: bundles the manager launch inputs
  (threshold, host/config paths, `snapshotNotifier`, `stoppedNotifier`) into one
  cluster, so `SetLaunchInputs` doesn't run out of connector-pane terminals.
- `src/Public/Logger.lvclass/ClearProcessDefault.vi`: clears the process-default
  logger (used by `Shutdown`).

Test-support fixtures/helpers (`tests/Support/`):

- `Open Test Mgr.vi` — reduced to `Initialize` only (`enableDefaultFile=FALSE`):
  brings the manager to the "ready, empty" baseline and returns the logger. No
  longer registers an appender or creates a temp root (decoupled).
- `Register Relay Appender.vi` — Arrange helper: builds a queue-mode relay
  appender for a given `id` (optional `filter`/`queueBound` inputs; defaults
  Mirror/permissive and `-1`), registers it (blocks on `WaitForSnapshot`), and
  returns the named-queue refnum via `Read relayQueue` for the test to drain.
- `Close Test Mgr.vi` — synchronous `Shutdown`, then force-destroys the test's
  relay queues via `Release Relay Queues`.
- `Release Relay Queues.vi` — takes `queueIDList` (array of String), obtains each
  named queue (`RelayQueueName`, `Statement`, create=FALSE) and force-destroys it;
  missing queue is a no-op (clears error 1100). Keeps the process-global namespace
  clean between tests.
- `Setup - create temp root.vi`, `Tear Down - delete root temp.vi` — composed per
  test (relay-queue tests need no temp root).

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
- **`Snapshot` reshaped to carry ids:** the fan-out array is now `appenders`, an
  array of `RegistryEntry {id, enqueuer}` (was a bare enqueuer array), so barriers
  can key on a specific appender's presence/absence. `Log`'s fan-out unbundles
  `.enqueuer`; `PostSnapshot` builds the array from the registry.
- **`Logger.Initialize` wired to `WaitForSnapshot`** (`AnySnapshot` readiness):
  returns only once the manager has posted its initial Snapshot, so the returned
  logger is ready to log. A manager that dies on entry never posts → `Initialize`
  returns 5030 (loud) instead of a dead-but-valid-looking logger. Confirmed both
  directions (`enableDefaultFile=FALSE` → clean; `=TRUE` empty-id default → 5030).
- **`Logger.RegisterAppender` wired to `WaitForSnapshot`** (`IDPresent`, `targetID`
  = the appender id from `GetID`): sends, then blocks until that id appears in a
  Snapshot, so callers can log to it deterministically. No pre-count. Sits inside
  the manager-enqueuer valid-refnum case; no-op passthrough (5029) otherwise.
  Replaced the flaky 1 s fixture delay.
- **`Logger.UnregisterAppender` wired to `WaitForSnapshot`** (`IDAbsent`): sends,
  then blocks until the id is gone. Unknown id is a benign immediate no-op
  (`IDAbsent` already satisfied), no false timeout.
- **`Logger.Shutdown` made synchronous** via a second notifier: the manager fires
  `stoppedNotifier` (error cluster) at `Actor Core` exit, after AF has stopped the
  nested appenders. `Shutdown` sends Stop, waits (bounded → error **5032**), merges
  the exit error, releases both notifiers, and clears the process default. This is
  what lets teardown safely reclaim application-owned relay queues after stop.
- **`RelayAppender.RelayQueueName` promoted to public** so test teardown can derive
  queue names from the one source of truth.
- **`Appender.HandleStatement` routed-filter bug fixed:** the Routed branch called
  `RoutedFilterMatch` but the `Statement` input was not wired, so it always judged a
  default record and effectively passed everything (Mirror was unaffected since it
  skips the filter). Wired the Statement through; the routed level band + tag now
  gate correctly. Caught by the `Relay - filtered tap` integration test (the
  `RoutedFilterMatch` unit tests passed because the predicate itself was correct;
  only the shipped caller was mis-wired).
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
  `Register Relay Appender`, `Release Relay Queues`, temp-root setup/teardown).
  Passing: **Delivery - single appender**, **Broadcast - fan-out**, **Registry -
  unregister silences appender** (incl. the unknown-id no-op), **Relay - message
  mode** (via a standalone queue-mode consumer, `Launch Consumer Relay`), and
  **Relay - filtered tap** (Routed band drops out-of-band levels). **Integration
  tests must run sequentially** (they share process-global state: the default logger
  and named relay queues); unit tests run parallel. Remaining launched-actor tests:
  file mechanics (two files, rollover, calendar tree), fault isolation, per-appender
  threshold, shutdown flush / shutdown-on-error, CatchError.
- **Doc-Terminal-Audit re-opened:** the barrier/shutdown VIs introduced
  description gaps and stale count-based text; see `Doc-Terminal-Audit.md` §5 for
  the fix list to clear before submitting.
- **ConfigReader design (Design §4.5):** started, not finished; to be completed in
  this PR before review. Design write-up only, the implementation (F1-F4) stays
  post-1.0 backlog.
- **`Support.lvlib` extraction:** Build-Checklist item 28a, a separate structural
  refactor to do before the project is considered done, not in this PR.
- **Optional additional unit tests:** CSV column order, tag `Sanitize`.
