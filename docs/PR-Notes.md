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

Caraya test framework (11 unit tests, 61 assertions, all passing via `Test.vi`):

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
- `tests/Unit/Source tag - defaulting.vi` (5)
- `tests/Unit/Retention prune.vi` (6)
- `tests/Unit/ISO 8601 filename.vi` (7)

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
- **`PruneSelection` per-base-name retention off-by-one fixed:** the running
  counter that reset on each base-name change was misaligned at the group
  boundary, so when one base-name series in a folder sat at or under its
  `maxFileCount`, it suppressed pruning of the *other* series sharing that folder,
  the over-limit series never shed its oldest file. Field effect: two series in
  one root with the later-sorted one under its limit meant retention silently did
  nothing and that folder grew unbounded (SRS-LMBR-034). Caught by the new
  `Retention prune` unit test at `LMBR-T-041-a` (app=4 + db=2, max 3 → expected
  the oldest `app` file, got an empty selection); the single-series and
  both-over-limit cases had masked it. Fixed by making each group's over-limit
  decision local and letting `FilesToDelete` accumulate unconditionally.
- **`PruneSelection` UTC-from-dashes heuristic removed (retention parse fix):**
  the reorganization step inferred whether a file name's timestamp was UTC or
  local from a dash pattern in the name, and that heuristic mis-read the `timekey`
  when the name's dash layout differed, so grouping and age-ordering collapsed and
  every over-limit group returned an empty selection, retention silently did
  nothing (SRS-LMBR-034). Surfaced once the `Retention prune` fixtures were built
  to match the real `ISO8601FileName` output: `LMBR-T-040-a`, `-040-d`, and
  `-041-a` went red with empty results while the empty-expecting cases stayed
  green. Fixed in `PruneSelection` so `timekey` extraction no longer depends on the
  dash pattern; the timezone frame is an appender property (`useUTC`), not
  something to reverse-engineer from the rendered name, so the timekey is treated
  as an opaque sortable token.
- **`IsFileNameSafe` special-character detection wired backwards (fix):** the
  Case selector on `Match Regular Expression`'s "offset past match" output used
  cases `0` / `1..Default`, but that output is `-1` when no special character is
  found (safe) and `>= 1` on a match (unsafe), and is never `0` (it is the index
  past a non-empty match). So the no-match (safe) and match (unsafe) inputs both
  fell into the same branch and the safe/unsafe verdict stopped tracking the input,
  filesystem-safety checking for `baseName`/`extension` was effectively disabled,
  so 5020 did not reliably fire. Rewired the selector to `-1` (no special
  character, safe) vs `Default` (match found, unsafe). Found during Config-validate
  test prep; `LMBR-T-024-c`/`-024-d` regression-cover it once built.
- **`DropPolicyFromString` always returned `DropOldest` (fix):** the lookup found
  the correct index into the enum's `Strings[]` array, but the index-to-enum
  conversion never set the enum value, so every input resolved to the ordinal-0
  member (`DropOldest`) regardless of the name. Effect: a config specifying
  `DropNewest` or the level-aware policy was silently coerced to `DropOldest`, so
  the per-appender backpressure policy from configuration did not take effect
  (SRS-LMBR-057), the wrong statements get discarded under a saturated bounded
  queue. Root cause: `Type Cast` is a byte-width reinterpret and `DropPolicy` is
  U16, while `Search 1D Array` returns I32; casting the 4-byte int into the 2-byte
  enum misreads the bytes and lands on ordinal 0. Fixed by converting the index
  I32 -> U16 (the enum's representation) before `Type Cast` to `DropPolicy`. `FilterModeFromString` had the identical I32-vs-U16 bug and was fixed the same way.
  Found by inspection; there is no DropPolicy/FilterMode name-round-trip test yet
  (only Severity has one, T-008), so both were unguarded, a round-trip test
  (`LMBR-T-060`) is being added to close that.
- **Resolve fataled on a missing config file (SRS-047 fix):** with a defined but
  non-existent config path, `Resolve` let LabVIEW error 7 (file not found) escape
  as a fatal error (`status` TRUE), which would block launch. The path gate lacked
  a working validity check, most LabVIEW existence primitives throw error 7 on a
  missing path instead of returning a clean FALSE, so the check itself produced the
  fatal. Added an error-tolerant is-valid-path check so a defined-but-missing path
  now returns a non-fatal warning (`status` FALSE) and falls back to the launch
  inputs, per SRS-LMBR-047 ("a missing optional config file shall not block
  application start"). Present-but-invalid stays fatal (SRS-048). Caught by
  `Config - resolve` test `LMBR-T-022-a`.
- **`enableDefaultFile` validation gating** (5024 fix): `ValidateLumberjackConfigDTO`
  now gates the default-file validator chain on `enableDefaultFile`, so a disabled
  default file is neither resolved nor validated. Corrects the earlier silent
  manager death on an empty-id default config.
- **`Appender.GetID` promoted to public** (read-only id accessor; dissolves a
  friend-scope issue for `Logger`/tests rather than adding friend edges).
- **`Test.vi` default-file cleanup:** `Test.vi` (suite runner) now deletes the
  default log file before the run when its **path input is empty**; a non-empty
  path input suppresses the delete. This clears a stale default file so the suite
  starts clean and runs are repeatable, and a missing file is a no-op.
- **Relay appender threshold not exposed on the creation surface (SRS-009 gap,
  fixed):** the per-appender level `threshold` is a common field populated by
  `Appender.InitCommon` from `AppenderConfig`, and `CreateFileAppender` surfaces
  it, but the relay's registration surface did not, so a relay could only ever run
  at its default cutoff. Receipt-time filtering itself worked; the value was just
  unreachable, so SRS-LMBR-009 ("each appender shall have its own independently
  configurable level threshold") was not fully met for relays. Added an optional
  `threshold` (`Severity`, default `ALL`) input that bundles into the
  `AppenderConfig` fed to `InitCommon`; default `ALL` preserves the behavior of
  relays created before the input existed (T-030/032/045 unaffected). Caught by the
  new `Filtering - per-appender threshold` test `LMBR-T-012` (SRS-009).
- **Shutdown was not a true flush barrier (SRS-002/004, fixed):** two root causes,
  both surfaced by the first file test `LMBR-T-034`. File appenders buffer to disk
  and commit at `CloseSink`, so an early `Shutdown` return produced 0-byte files at
  full speed while highlight execution masked it, and across the serial suite each
  test handed a not-fully-stopped tree to the next.
  1. The shutdown timeout constant defaulted to **-1**, which collapsed the
     `deadline = start + timeout` math to an already-expired deadline, so
     `WaitForStopped` skipped the wait entirely. Fixed: positive default (5000 ms).
  2. `LogManager.Actor Core` posted `stoppedNotifier` immediately after the AF
     Call Parent node. Launch Nested Actor auto-stops the appenders when the manager
     stops, but the parent's Actor Core does **not** block until the children finish
     stopping, so the notifier fired before the appenders ran `CloseSink`. Fixed:
     after Call Parent, poll `Read Auto-stop Nested Actor Count` to 0 (5 ms interval;
     unbounded, with the caller's `Shutdown` timeout as the backstop), then post
     `stoppedNotifier`. Because each appender's `CloseSink` runs before it drops out
     of the count, count==0 means every sink has flushed and closed. `Shutdown` is
     now a real barrier; single-test and serial-suite both pass.
  Also confirmed `CloseSink` guards the close with `Not A Refnum?` (safe no-op on the
  error-exit path).
- **T-034 file-config defects (found building the first file test):**
  - Default `FileAppenderConfig` carried invalid `maxFileSize`/`maxFileCount` (`0`),
    which gated the write path and produced 0-byte files. Tests must set `-1`/`-1`.
    Follow-ups: verify the size-rollover check special-cases `-1` as unbounded (not
    `size >= -1`, which rolls every write), and note the native-config `Register File
    Appender` path bypasses the DTO 5022 validation that would reject bad bounds.
  - A raw default `FileAppenderConfig` carries a **base `Layout`**, not a
    `CSVLayout`, so `Format` (DD must-override) emitted empty lines. The test must
    supply a `CSVLayout`; `Register File Appender` should default it, mirroring
    `CreateFileAppender`.
  - SRS-037: `FileAppender.Init` stamps `useUTC` but not the delimiter, so a
    configured non-comma delimiter never reaches the layout (masked by the comma
    default). Stamp `file.delimiter` via the `CSVLayout:Write delimiter` accessor.

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
- **Shutdown drain latency (next-pass optimization):** now that `Shutdown` correctly
  waits for every nested appender to stop and flush (the count-poll fix), the serial
  suite runs noticeably longer, which suggests some appenders are slow to stop. The
  poll interval is already 5 ms, so the latency is in the appenders' own stop path
  (likely a blocking wait in the intake/backpressure loop before the stop is
  handled). Deferred to a later pass; correctness is not affected.
- **5030 masks a failed default-file appender startup (diagnosability gap):** when
  `enableDefaultFile = TRUE` but the default FileAppender cannot open its sink (no
  writable root / host path resolved), the failure surfaces as a generic 5030
  readiness-timeout rather than a descriptive file/path error, so the operator
  cannot distinguish "manager did not start" from "log file could not be created."
  Surfaced while building `LMBR-T-011` (a default file was mistakenly enabled in the
  relay-only fixture). Consider surfacing the appender's open error directly, or a
  finer error code, when the file-mechanics cluster (T-034/039/042) is built. No
  code change yet; the readiness barrier behaves correctly, only the reported cause
  is coarse.
- **Doc-Terminal-Audit re-opened:** the barrier/shutdown VIs introduced
  description gaps and stale count-based text; see `Doc-Terminal-Audit.md` §5 for
  the fix list to clear before submitting.
- **ConfigReader design (Design §4.5):** started, not finished; to be completed in
  this PR before review. Design write-up only, the implementation (F1-F4) stays
  post-1.0 backlog. Consequently **per-key / partial-file merge (SRS-LMBR-046) is
  not yet implemented**: the current `Merge` does a full-object overwrite (an empty
  value clobbers the baseline rather than falling back). Its presence mask
  (two-default diff) and the `LMBR-T-021` per-key-merge test are deferred with the
  ConfigReader work; `Config - resolve.vi` covers only the no-file / missing /
  invalid paths (T-020/022/023) for now.
- **`Support.lvlib` extraction:** Build-Checklist item 28a, a separate structural
  refactor to do before the project is considered done, not in this PR.
- **Optional additional unit tests:** CSV column order, tag `Sanitize`.
