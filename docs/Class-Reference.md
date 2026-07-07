# Message and Class Reference: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Lumberjack SRS (SRS-LMBR-001 .. 064), Lumberjack SDD,
Lumberjack API and Usage Guide

**Status:** Draft

---

## 1. About this reference

This document lists every type definition, class, and message in Lumberjack,
with private data, member VIs, scopes, and dynamic-dispatch status. It is the
implementation-facing companion to the SDD.

Notation:

- **Scope**: `public`, `community`, `protected`, `private` (LabVIEW member
  access scopes).
- **Dispatch**: `static` (normal) or **DD** (dynamic dispatch). *(must
  override)* marks an abstract DD member a subclass is required to implement;
  *(override)* marks a member that overrides a parent.
- Severity ranks are fixed: FATAL 1, ERROR 2, WARN 3, INFO 4, DEBUG 5, TRACE 6.

---

## 2. Type definitions (data)

These are typedef controls, not classes. They cross the API boundary and the
JSON boundary, so they are plain data.

### 2.1 Severity (enum)
Values, in rank order: `FATAL (1)`, `ERROR (2)`, `WARN (3)`, `INFO (4)`,
`DEBUG (5)`, `TRACE (6)`. The numeric rank is used for threshold comparison
(SRS-LMBR-005, 006).

### 2.2 Statement (cluster)
One log record (SRS-LMBR-010).

| Field | Type | Notes |
|---|---|---|
| timestamp | Timestamp | ISO 8601 when formatted (SRS-LMBR-011) |
| level | Severity | the statement's rank |
| sourceTag | String | hierarchical, dot-separated; defaults to originVI base name (SRS-LMBR-013) |
| originVI | String | physical emitting VI name (kept distinct from sourceTag) |
| message | String | the only user-defined field |

### 2.3 Filter (cluster)
Per-appender selection filter (SRS-LMBR-026, 027).

| Field | Type | Notes |
|---|---|---|
| mode | FilterMode enum (`mirror`, `routed`) | mirror accepts all above threshold |
| levelMin / levelMax | Severity | routed level range |
| tagPrefix | String | routed hierarchical prefix; empty = any |

### 2.4 DropPolicy (enum)
`dropOldest` (default), `dropNewest`, `levelAware` (SRS-LMBR-057).

### 2.5 RelayMode (enum)
`message` (default), `queue` (SRS-LMBR-024, 025).

### 2.6 AppenderConfig (cluster, common)
The common configuration shared by every appender (SRS-LMBR-029). Composed
(nested) into each type-specific config.

| Field | Type | Notes |
|---|---|---|
| id | String | unique appender ID |
| threshold | Severity | per-appender authoritative threshold (SRS-LMBR-009) |
| filter | Filter | selection filter |
| queueBound | U32 | 0 = unbounded (SRS-LMBR-055, 056) |
| dropPolicy | DropPolicy | applies when bounded (SRS-LMBR-057) |
| layout | Layout | formatting strategy (SRS-LMBR-015) |

### 2.7 FileAppenderConfig (cluster)
`AppenderConfig` (nested as `common`) plus: `baseName` (String, opt),
`rootFolder` (Path), `maxFileSize` (U64), `maxFileCount` (U32, 0 = keep all),
`extension` (String), `delimiter` (String), `calendarFolderTree` (Bool),
`useUTC` (Bool) (SRS-LMBR-030, 032-040).

`baseName` is an optional filename prefix (empty = timestamp-only names).
`useUTC` selects the time frame (UTC vs local) for the file name, the calendar
folder, and the layout's timestamp column together, so all three agree.

`delimiter` is a formatting concern owned by the layout; the file appender feeds
this value into the `CSVLayout` it constructs, so it is not an independent
setting (SDD 5.4).

### 2.8 RelayAppenderConfig (cluster)
`AppenderConfig` plus: `mode` (RelayMode) and, for message mode,
`consumerEnqueuer` (Enqueuer).

### 2.9 LumberjackConfig (cluster)
The `Initialize` / JSON boundary object (SRS-LMBR-050).

| Field | Type |
|---|---|
| schemaVersion | U16 |
| globalThreshold | Severity |
| defaultFileAppender | FileAppenderConfig |

### 2.10 Snapshot (cluster)
The Notifier payload broadcast to callers (SDD 2.1).

| Field | Type | Notes |
|---|---|---|
| globalThreshold | Severity | stage-1 coarse threshold |
| appenderEnqueuers | Array of Enqueuer | current broadcast targets |

---

## 3. Classes

### 3.1 Logger.lvclass
By-value caller facade. Wraps the shared references and provides the public API.
Not an actor.

- **Inherits:** LabVIEW Object.
- **Private data:** `notifier` (Notifier refnum for the Snapshot),
  `managerEnqueuer` (Enqueuer to the LogManager).

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| Initialize | public | static | Launch the LogManager, resolve config, launch the default file appender, post the initial Snapshot; return the instance and store it as the process default. |
| Log | public | static | Core log: resolve instance, read Snapshot, apply stage-1 threshold, build Statement, fan out to enqueuers. |
| Trace / Debug / Info / Warn / Error / Fatal | public | static | Thin wrappers over `Log` at a fixed level (SRS-LMBR-016). |
| ConfigureLevel | public | static | Post an updated Snapshot with a new global threshold (SRS-LMBR-008). |
| ConfigureVerbosity | public | static | Set the dialog-verbosity for CatchError (SRS-LMBR-042). |
| RegisterAppender | public | static | Send `RegisterAppenderMsg` to the manager. |
| UnregisterAppender | public | static | Send `UnregisterAppenderMsg`. |
| ConfigureAppender | public | static | Send `ConfigureAppenderMsg`. |
| CatchError | public | static | General-error-handler integration; log and optionally display (SRS-LMBR-041). |
| Shutdown | public | static | Send framework Stop to the manager (SRS-LMBR-002). |
| Resolve Logger | private | static | Return the wired instance or fetch the process default (singleton support, SDD 2.4). |

### 3.2 LogManager.lvclass
Root actor; owns the control plane and is the sole poster of the Snapshot.

- **Inherits:** Actor.lvclass.
- **Private data:** `notifier` (Snapshot Notifier), `registry` (array of {id,
  Enqueuer, Appender-nested-actor handle}), `globalThreshold`, resolved
  `LumberjackConfig`.

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| Actor Core | protected | override | On entry: resolve config, launch default file appender, post initial Snapshot. Then run the framework message loop. |
| ResolveConfig | private | static | Merge launch inputs with the JSON file (native Unflatten with baseline as default value); validate; produce effective config (SRS-LMBR-044-051). |
| LaunchAppender | private | static | Launch an Appender object as a nested actor, capture its enqueuer, add to registry. |
| PostSnapshot | private | static | Send the current {threshold, enqueuer array} to the Notifier. |
| HandleStop | protected | override | Stop all nested appenders (each flushes and closes), then stop (SRS-LMBR-002, 004). |

### 3.3 Appender.lvclass (abstract)
Base actor for all sinks. Implements the shared receipt logic; delegates sink
specifics to subclasses (SRS-LMBR-018).

- **Inherits:** Actor.lvclass.
- **Private data:** `AppenderConfig` (common fields), `droppedCount` (U64),
  plus an internal bounded intake buffer when `queueBound > 0`.

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| InitCommon | protected | static | Set the common private data from an `AppenderConfig` (called by each subclass init, SRS-LMBR-031). |
| GetID | community | static | Return the appender ID (used by the manager's registry/unregister). |
| HandleStatement | protected | static | Apply the appender threshold then the Filter; if accepted, format via `layout` and call `Write`; enforce backpressure on intake (SRS-LMBR-009, 026, 055-059). |
| OpenSink | protected | **DD** *(must override)* | Open the sink resource on actor startup. |
| Write | protected | **DD** *(must override)* | Write one formatted, accepted line to the sink. |
| CloseSink | protected | **DD** *(must override)* | Flush and close the sink on stop. |
| Configure | protected | **DD** | Apply a config delta to common fields; subclasses override to extend for type-specific fields (SRS-LMBR-043). |
| Actor Core | protected | override | Call `OpenSink` on entry and `CloseSink` on exit around the framework loop; drain the bounded intake per drop policy. |
| EmitDropNotice | private | static | Write a synthetic "N statements dropped" record when discards have occurred (SRS-LMBR-059). |

### 3.4 FileAppender.lvclass
Writes statements to rolling, retained log files.

- **Inherits:** Appender.lvclass.
- **Private data:** `FileAppenderConfig` fields, `currentFileRefnum`,
  `currentFileSize`, `currentFolder`.

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| Init | public | static | Set file-specific fields, then call parent `InitCommon` (SRS-LMBR-031). |
| OpenSink | protected | override | Create the base (and calendar) folder; open the first ISO 8601-named file (SRS-LMBR-035, 036). |
| Write | protected | override | Append the line; roll over if the size limit is exceeded, then prune to the retention limit (SRS-LMBR-033, 034). |
| CloseSink | protected | override | Flush and close the current file. |
| Configure | protected | override | Extend base Configure with file-specific fields (per-instance, SRS-LMBR-039, 040). |
| OpenNewFile | private | static | Open a new timestamped file and reset the size counter. |
| Prune | private | static | List this appender's own `baseName_*` files across the root (and any calendar sub-folders), then delete oldest beyond `maxFileCount` via `PruneSelection` (grouped per base name); 0 = keep all. |

### 3.5 ConsoleAppender.lvclass
Writes formatted lines to the console/standard output.

- **Inherits:** Appender.lvclass.
- **Private data:** none beyond common.

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| Init | public | static | Set console fields (none beyond common), then call parent `InitCommon`. |
| OpenSink | protected | override | No-op (console always available). |
| Write | protected | override | Print the formatted line. |
| CloseSink | protected | override | No-op. |

### 3.6 RelayAppender.lvclass
Delivers accepted statements to the application (SRS-LMBR-023).

- **Inherits:** Appender.lvclass.
- **Private data:** `mode` (RelayMode), `consumerEnqueuer` (message mode),
  owned `relayQueue` refnum (queue mode).

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| Init | public | static | Set mode and mode-specific fields, then call parent `InitCommon`; in queue mode create and expose the queue. |
| GetRelayQueue | public | static | Return the owned queue refnum (queue mode, SRS-LMBR-025). |
| OpenSink | protected | override | Queue mode: obtain the queue. Message mode: validate the enqueuer. |
| Write | protected | override | Message mode: send `LogStatementMsg` to `consumerEnqueuer` (SRS-LMBR-024). Queue mode: enqueue the Statement. |
| CloseSink | protected | override | Queue mode: release the owned queue. |

### 3.7 Layout.lvclass (abstract)
Stateless formatting strategy (SRS-LMBR-015). By-value, not an actor.

- **Inherits:** LabVIEW Object.

| Member | Scope | Dispatch | Description |
|---|---|---|---|
| Format | public | **DD** *(must override)* | Convert a `Statement` to a `String`. |

### 3.8 CSVLayout.lvclass
- **Inherits:** Layout.lvclass. **Private data:** `delimiter`.
- `Format` *(override)*: emit `timestamp, level, sourceTag, originVI, message`
  with RFC 4180 quoting (SDD 5.4). Default layout (SRS-LMBR-012).

### 3.9 JSONLayout.lvclass
- **Inherits:** Layout.lvclass.
- `Format` *(override)*: emit one JSON object per statement.

### 3.10 TextLayout.lvclass
- **Inherits:** Layout.lvclass.
- `Format` *(override)*: emit a human-readable single line.

---

## 4. Messages

All extend `Message.lvclass` and override `Do.vi`. Each has an auto-generated
`Send <name>.vi` convenience method. Payload is the message's private data.

### 4.1 LogStatementMsg (data plane)
- **Direction:** caller (via `Logger.Log`) to each appender enqueuer.
- **Payload:** `Statement`.
- **Do.vi:** call the receiving `Appender`'s `HandleStatement` (threshold,
  filter, format, write) (SRS-LMBR-019).

### 4.2 RegisterAppenderMsg (control plane)
- **Direction:** caller to LogManager.
- **Payload:** a constructed, pre-configured `Appender` object.
- **Do.vi:** `LaunchAppender`, add to registry, `PostSnapshot` (SRS-LMBR-020,
  028).

### 4.3 UnregisterAppenderMsg (control plane)
- **Direction:** caller to LogManager.
- **Payload:** appender `id` (String).
- **Do.vi:** post an updated Snapshot without that enqueuer, then send framework
  Stop to the appender and remove it from the registry (SDD 5.8).

### 4.4 SetGlobalThresholdMsg (control plane)
- **Direction:** caller to LogManager.
- **Payload:** `threshold` (Severity).
- **Do.vi:** update `global threshold`, `PostSnapshot` (SRS-LMBR-008).

### 4.5 ConfigureAppenderMsg (control plane)
- **Direction:** caller to LogManager to a specific appender.
- **Payload:** target `id` (String) plus a `config delta`.
- **Do.vi (manager):** look up the target enqueuer and forward a `ConfigureMsg`
  (SRS-LMBR-043).

### 4.6 ConfigureMsg (manager to appender)
- **Direction:** LogManager to one appender.
- **Payload:** `config delta`.
- **Do.vi:** call the appender's `Configure` (base plus any subclass override),
  effective for statements dequeued after (SDD 5.9).

### 4.7 Stop (framework)
The Actor Framework `Stop Msg` is used unchanged. On the LogManager it triggers
`HandleStop` (stop all appenders); on an appender it triggers `CloseSink` via
the `Actor Core` exit path (SRS-LMBR-002, 004).

---

## 5. Traceability (element to SRS)

| Element | Satisfies |
|---|---|
| Severity, Statement | 005, 010, 011, 013 |
| Filter, DropPolicy | 026, 027, 057 |
| AppenderConfig, File/Relay Config | 029, 030, 032-040 |
| LumberjackConfig, Snapshot | 044-051 |
| Logger.lvclass | 002, 008, 016, 017, 041, 042 |
| LogManager.lvclass | 001, 002, 004, 020, 043, 044-051 |
| Appender.lvclass | 009, 015, 018, 026, 055-059 |
| FileAppender.lvclass | 032-040 |
| RelayAppender.lvclass | 023-025 |
| Layout classes | 012, 015 |
| LogStatementMsg | 019, 052 |
| Register / UnregisterAppenderMsg | 020, 021, 028 |
| SetGlobalThresholdMsg | 008 |
| ConfigureAppender / ConfigureMsg | 043 |
