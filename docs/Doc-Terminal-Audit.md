# Terminal Description Audit: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Class-Reference, Build-Checklist (item 35), Design, SRS

**Status:** Draft. Description text entered in the VIs still requires SOP-117
human review before being treated as authoritative.

**Source:** Generated from `docs/HTMLReport/Lumberjack_Report.html`
(PrintLibraryToHTML export).

**Progress (as of the 2026-08-05 report):** COMPLETE. Every real connector-pane
data terminal now carries a description. The only blank entries left in the
report are non-terminal element/field labels (section 3), which do not need
their own terminal descriptions.

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

