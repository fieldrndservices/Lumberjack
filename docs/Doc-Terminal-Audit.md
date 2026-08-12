# Terminal Description Audit: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Class-Reference, Build-Checklist (item 35), Design, SRS

**Status:** Draft. Description text entered in the VIs still requires SOP-117
human review before being treated as authoritative.

**Source:** Generated from `docs/HTMLReport/Lumberjack_Report.html`
(PrintLibraryToHTML export).

**Progress (as of the 2026-08-05 report):** the pre-barrier surface was COMPLETE.
Every real connector-pane data terminal carried a description; the only blanks
were non-terminal element/field labels (section 3).

**Re-audit (2026-08-08 report):** the synchronous-barrier work added new VIs and
typedefs and reshaped `Snapshot`, and it re-opened a set of description gaps and
stale (count-based) text. Section 5 listed the outstanding items.

**Resolved (2026-08-09 report):** COMPLETE again. All section 5 items were fixed
in the VIs and verified against the refreshed report, no blank real-data terminals
and no count-based text remain (`minEnqueuers`, `prior count`, `at least this`,
`enqueuer array`, `meeting the count`, and the vestigial `appenderEnqueuers` field
all scan to zero). Section 5 is retained below as a record of what was fixed.

---

## 1. Scope and summary

The scan classified blank descriptions into three buckets:

- **Dynamic-dispatch object terminals** (`<Class> in` / `<Class> out`) — 103.
  Excluded: DD object terminals do not need descriptions (project decision).
- **Unlabeled class-object terminals** (e.g. a bare `Layout` object) — 8.
  Excluded (same rationale).
- **Real data terminals** — all now described (section 2).

The `error in` / `error out` / `status` / `code` / `source` cluster terminals
already carry LabVIEW's standard boilerplate and are not counted.

---

## 2. Completed

All connector-pane data terminals have descriptions, across the Support/standalone
helpers and the class-member VIs:

- Support helpers: `CSVQuoteField` (`field`, `delimiter`), `SeverityString` /
  `SeverityFromString`, `DropPolicyString` / `DropPolicyFromString`,
  `FilterModeString` / `FilterModeFromString`, `RankCompare` (`Passes`),
  `RoutedFilterMatch` (`Accepted`), `BaseFolder`, `DefaultSourceTag`,
  `ISO8601FileName`, `IsFileNameSafe`, `Merge` (`JSONText`),
  `ProcessDefaultQueueName`, `ProcessVerbosityQueueName`, `GetProcessDefault`
  (`found`), `GetVerbosity` (`Found`), `PruneSelection` (`ExistingFiles`,
  `FilesToDelete`), `ResolveHostRoot`, `Sanitize` (`RawTag`, `CleanTag`),
  `CheckSchemaVersion` (`ValidSchemaVersions`, `schemaVersionIn`,
  `schemaVersionOut`, `CurrentSchemaVersion`).
- Layouts: `Format` `FormattedLine` on `Layout`, `CSVLayout`, `JSONLayout`,
  `TextLayout`.
- Appenders / manager / messages: `FileAppender.Init` (`FileAppenderConfig`),
  `FileAppender.OpenNewFile` (`targetFolder`), `Appender.GetID` (`ID`),
  `ConsoleAppender.Write` (`Bytes Written`), `LogManager.FindIndexByID`
  (`registry`, `index`, `found`), `LogManager.RemoveAppender` (`found`),
  `LogManager.ConfigureAppender` (`id`), `Send ConfigureAppenderMsg` (`id`),
  `Send UnregisterAppenderMsg` (`id`), `RelayAppender.Read relayQueue`
  (`relayQueue`).

---

## 3. Non-terminal report entries (intentionally not tracked)

The report still lists these as blank, but they are cluster fields or array
element labels, not connector-pane terminals, so they need no terminal
description:

- **`file`** — the `file` sub-cluster field inside `FileAppenderConfig` (a
  typedef field, not a connector-pane terminal). Now described, matching its
  `common` sibling. Done.
- **`RootFolder`** (x2) — the element label of the `ExistingFiles` and
  `FilesToDelete` Path arrays on `PruneSelection`. `PruneSelection` has no
  `RootFolder` input.
- **`schemaVersion`** — the element label of the `ValidSchemaVersions` array on
  `CheckSchemaVersion`, whose array control already carries the description.

---

## 4. Typedef descriptions (complete)

Separate pass over the type definitions (control descriptions and their cluster
fields), as of the 2026-08-05 report. **Complete:** all native clusters and DTO
mirrors are documented.

Fixed in this pass:

- `FileConfig.ctl` `file` field / `FileAppenderConfig` `file` sub-cluster: now
  described (matches its `common` sibling).
- `FileConfigDTO.ctl`: added the top-level control description ("String DTO mirror
  of FileConfig...").
- `FileAppenderConfigDTO.ctl`: the file sub-cluster field is now described, and
  renamed `fileConfig` to `file` so it lines up one-to-one with the native
  `FileAppenderConfig`.

Verified documented: `AppenderConfig`, `FileConfig`, `FileAppenderConfig`,
`Filter`, `LumberjackConfig`, `Statement`, `Severity`, `DropPolicy`, `RelayMode`,
`FilterMode`, `RegistryEntry`, `RelayAppenderConfig`, `Snapshot`, and the DTO
mirrors `AppenderConfigDTO`, `FilterDTO`, `FileConfigDTO`,
`FileAppenderConfigDTO`, `LumberjackConfigDTO`.

---

## 5. Outstanding after the synchronous-barrier work (2026-08-08 report)

New/changed VIs and typedefs from the barrier + shutdown + teardown work. Fix in
the VIs, then re-run the report to confirm. Grouped by kind of gap.

**Missing VI Documentation (VI has no description string):**

- `Logger.Shutdown` — no description; also `timeout ms` terminal blank. Describe:
  send framework Stop, wait on `stoppedNotifier` (bounded), 5032 on timeout, merge
  the manager's exit error, release both notifiers + clear process default.
- `ClearProcessDefault` — entirely undocumented (VI + terminals).
- `Logger.RegisterAppender` — no description (only `Logger in/out` shown). Describe
  the `IDPresent` registration barrier.
- `Logger.UnregisterAppender` — no VI description (the `id` terminal is described).
  Describe the `IDAbsent` barrier and the unknown-id benign no-op (+28).

**Stale (count-based) text left over from before the id-based redesign:**

- `Logger.WaitForSnapshot` — VI Documentation still says "at least `minEnqueuers`
  ... prior count + 1"; rewrite to the id predicate (`SnapshotWaitMode`:
  AnySnapshot / IDPresent / IDAbsent, `targetID`). Terminal fixes:
  - `targetID` description is the old minEnqueuers text ("count is at least this");
    should be "appender id to wait for; ignored for AnySnapshot."
  - `Context` description says "unknown name"; should be the barrier context spliced
    into the 5030 message. (Also reconcile casing/naming: `Context` vs `context`,
    `timeout_ms` vs `timeout ms`.)
  - `Snapshot` output: "first Snapshot meeting the count" -> "the Snapshot that
    satisfied the wait; valid only on the success path."
- `SnapshotHasID` — `id` input description is the old minEnqueuers text; should be
  "appender id to search for." Check the VI doc for a truncated leading character
  ("eturns whether ...").
- `LogManager.PostSnapshot` — description says "array of appender enqueuers from the
  registry"; now builds the `appenders` array of `RegistryEntry {id, enqueuer}`.
- `Snapshot.ctl` — top description says "the enqueuer array is the fan-out target
  list"; the field is now `appenders` (array of `RegistryEntry`). The `appenders`
  field itself is **blank**, and the `enqueuer` subfield carries a stale Actor
  Framework boilerplate description. Confirm no stale `appenderEnqueuers` field or
  description lingers.

**Blank fields:**

- `ManagerLaunchInputs.ctl` — `stoppedNotifier` field blank; the top-level control
  description is also blank (its siblings are described).

**Correctly documented (spot-checked, no action):** `SnapshotWaitMode.ctl`,
`RelayAppender.RelayQueueName`, `RegistryEntry.ctl`, `LogManager.RemoveAppender`,
`Logger.Initialize`, `Logger.Log`.

DD object terminals (`Logger in` / `Logger out`, `<Class> in/out`) remain
intentionally blank per the section 1 rule.

