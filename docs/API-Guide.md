# API and Usage Guide: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Lumberjack SRS (SRS-LMBR-001 .. 064), Lumberjack SDD

**Audience:** LabVIEW developers adding logging to an application

**Status:** Draft

---

## 1. About this guide

Lumberjack is written in LabVIEW (G), so its API is a set of VIs. This guide
describes each public VI by its connector pane (inputs and outputs) and
behavior, and gives worked wiring recipes. Because block diagrams cannot be
shown in text, recipes are given as ordered steps that map to the wires you
would drop.

Conventions used below:

- *(opt)* marks an optional input; unwired, it takes the stated default.
- Every VI has standard `error in` / `error out`; these are noted only where
  behavior deviates from the standard.
- Severity ranks are fixed: FATAL 1, ERROR 2, WARN 3, INFO 4, DEBUG 5, TRACE 6.
  A threshold passes a statement whose rank is less than or equal to it.
  Threshold 0 disables all logging; 7 or higher passes everything.

### 1.1 Two calling styles

Lumberjack supports both, and they interoperate:

- **Singleton (default).** `Initialize` stores the created logger in a
  process-scoped location. The per-level VIs, unwired, use that default, so you
  can log from any VI without threading a handle. This matches the original
  Logger's ergonomics.
- **Instance.** `Initialize` also returns a `Logger` object. Wire it into
  `logger in` on any VI to target that specific instance. Use this for tests or
  for running more than one independent logger.

Everywhere below, `logger in` is *(opt)*: unwired uses the process default,
wired uses the instance.

### 1.2 Naming and migration

Verbs mirror the original Logger (`Initialize`, `Trace`..`Fatal`, `Shutdown`,
`CatchError`), modernized where it improves clarity. The main modernizations:
listeners are now **appenders**; the global `Configure` file settings are now
**per-appender** configuration set when you create an appender. A full mapping
is in section 11.

---

## 2. Quick start (singleton)

Log to the default file with three nodes:

1. `Initialize` at application start. Leave inputs at defaults to get a single
   CSV file appender under a default folder.
2. Anywhere in your code, drop `Info` and wire a message string. No handle
   needed.
3. `Shutdown` at application exit to flush and close.

```
[Initialize] ---> ... your app ... ---> [Shutdown]
                     |
                  [Info "Pump started"]
                  [Error "Valve timeout"]
```

@TODO - Include a VI snippet/PNG when available

That is the entire minimum. Everything else is optional configuration and
additional appenders.

---

## 3. Lifecycle VIs

### 3.1 Initialize

Starts the LogManager, resolves configuration, launches the default file
appender, and posts the initial snapshot. Establishes the process-default logger
and returns an instance.

- **Inputs:**
  - `global threshold` *(opt, default INFO=4)*: stage-1 coarse threshold
    (SRS-LMBR-007, 012).
  - `default file config` *(opt)*: a FileAppender config for the default file
    (base name, root folder, max size, max count, extension, delimiter, calendar
    tree, UTC). Defaults give a CSV file with calendar folders and size-based
    rollover.
  - `disable default file?` *(opt, default FALSE)*: when TRUE, no default file
    appender is launched (SRS-LMBR-038).
  - `config file path` *(opt)*: JSON configuration file (section 6). When
    supplied and valid, its values override the inputs per key.
  - `host application path` *(opt)*: the host application's directory, used to
    resolve relative paths safely under a PPL (section 10, SRS-LMBR-064).
    Required when running as a built application (see below).
- **Outputs:**
  - `logger out`: the `Logger` instance (also stored as the process default).
  - `error out`: carries a non-fatal **warning** if a supplied config file path
    was missing (SRS-LMBR-047); a fatal **error** if the file was present but
    invalid (SRS-LMBR-048); or a fatal **error 5000** if a relative or empty log
    root must be resolved but no `host application path` was supplied while
    running as a built application (SRS-LMBR-064, section 12).

### 3.2 Shutdown

Stops the LogManager, which flushes and closes every appender.

- **Inputs:** `logger in` *(opt)*.
- **Behavior:** runs its flush-and-close even if `error in` carries an error
  (SRS-LMBR-004).

---

## 4. Logging VIs

One VI per level: `Trace`, `Debug`, `Info`, `Warn`, `Error`, `Fatal`. All share
the same pane.

- **Inputs:**
  - `message`: the user text (the only user-defined field; the rest are
    generated).
  - `source tag` *(opt)*: a hierarchical dot-separated category, e.g.
    `app.comms.tcp`. Unwired, it defaults to the calling VI's base name
    (SRS-LMBR-013, 017).
  - `logger in` *(opt)*.
- **Behavior:** reads the current snapshot, applies the global threshold
  locally, and if the statement passes, builds it (timestamp, level, sourceTag,
  originVI, message) and fans it out to every registered appender. Returns
  without waiting for any sink I/O (SRS-LMBR-052). The statement is created even
  if `error in` carries an error (SRS-LMBR-014).

Example (routed logging from a comms module):

```
[Info  message="link up"  source tag="app.comms.tcp"]
[Error message="timeout"   source tag="app.comms.tcp"]
```

---

## 5. Global configuration VIs

### 5.1 ConfigureLevel

Sets the global (stage-1) threshold at runtime (SRS-LMBR-008).

- **Inputs:** `threshold`, `logger in` *(opt)*.
- **Behavior:** posts an updated snapshot; takes effect for statements evaluated
  after the call.

### 5.2 ConfigureVerbosity

Sets the severity at or above which `CatchError` shows an error dialog,
independent of what is logged (SRS-LMBR-042).

- **Inputs:** `verbosity`, `logger in` *(opt)*.

---

## 6. Configuration file (JSON)

`Initialize` optionally reads a JSON file whose values override the launch
inputs per key (SRS-LMBR-045, 046, 050). The file carries global settings and
the default file appender only; additional appenders are added in code (section
7).

```json
{
  "schemaVersion": 1,
  "globalThreshold": "INFO",
  "defaultFileAppender": {
    "common": {
      "id": "default-file",
      "threshold": "INFO",
      "filter": { "mode": "Mirror" },
      "queueBound": -1,
      "dropPolicy": "DropOldest"
    },
    "rootFolder": "",
    "baseName": "",
    "maxFileSize": 10485760,
    "maxFileCount": 10,
    "extension": "csv",
    "delimiter": ",",
    "calendarFolderTree": true,
    "useUTC": true
  }
}
```

Behavior of the path:

- **Missing file** at a supplied path: launch continues on the inputs and
  returns a non-fatal warning (SRS-LMBR-047).
- **Present but invalid** (unparseable or fails validation): launch fails with a
  descriptive error naming the offending setting (SRS-LMBR-048).
- An empty `rootFolder` means "compute the default from the host application
  context" (section 10).

---

## 7. Appender VIs

Appenders are created and configured as objects, then registered. The manager
launches a registered appender and adds it to the broadcast. This keeps appender
configuration with the appender type.

### 7.1 Create a FileAppender

`CreateFileAppender` returns a configured (not yet launched) appender object.

- **Inputs:** `id`, `threshold` *(opt, default = inherit sensible)*, `filter`
  *(opt, default mirror)*, `base name` *(opt, "")*, `root folder`,
  `max file size` *(opt)*, `max file count` *(opt, -1 = keep all)*, `extension`
  *(opt, "csv")*, `delimiter` *(opt, ",")*, `calendar folder tree?` *(opt)*,
  `use UTC?` *(opt)*, `queue bound` *(opt, -1 = unbounded)*,
  `drop policy` *(opt, drop-oldest)*, `layout` *(opt, CSV)*.
- **Output:** `appender out` (an Appender object).

### 7.2 Create a ConsoleAppender

`CreateConsoleAppender` returns a console sink. Same common inputs (`id`,
`threshold`, `filter`, backpressure, `layout`); no file-specific fields.

### 7.3 Create a RelayAppender

`CreateRelayAppender` returns an appender whose sink is your application
(SRS-LMBR-023).

- **Inputs:** common config, plus `mode` (message or queue).
  - Message mode: `consumer enqueuer` (your actor's enqueuer). Each accepted
    statement is sent to it as a `LogStatementMsg` (SRS-LMBR-024).
  - Queue mode: no extra input; the VI also returns `relay queue out`, a queue
    refnum you Dequeue or Flush (SRS-LMBR-025).
- **Output:** `appender out`, and `relay queue out` when in queue mode.

### 7.4 Register / Unregister

- `RegisterAppender`: inputs `appender in`, `logger in` *(opt)*. Launches the
  appender as a nested actor, adds it to the broadcast, posts the updated
  snapshot. Callers pick it up on their next log call (SRS-LMBR-020, 028).
- `UnregisterAppender`: inputs `id`, `logger in` *(opt)*. Removes it from the
  snapshot first, then stops it (it flushes and closes on stop).

### 7.5 Reconfigure at runtime

`ConfigureAppender`: inputs `id`, `config delta`, `logger in` *(opt)*. Forwards
the change to the target appender; it takes effect for statements that appender
processes after the message (SRS-LMBR-043, and the ordering note in SDD 5.9).

### 7.6 Selection filter

The `filter` input is a small config:

- `mode`: **mirror** (accept everything above the appender threshold) or
  **routed**.
- Routed criteria: `level range` (min/max rank) and/or `tag prefix`.
- Tag matching is hierarchical prefix (SRS-LMBR-027): prefix `app.db` matches
  `app.db` and `app.db.query`, not `app.database`.

Helpers: `MakeMirrorFilter` and `MakeRoutedFilter (level range, tag prefix)`
build the cluster for you.

---

## 8. Reading the log stream (relay appender)

To consume statements in your own code, register a relay appender.

**Message mode (recommended, actor consumers):**

1. In your consuming actor, create a message class it understands, or accept
   `LogStatementMsg` directly.
2. `CreateRelayAppender` with `mode = message` and `consumer enqueuer` = your
   actor's enqueuer; set a `filter` to tap only what you want (for example a
   routed filter with level range ERROR..FATAL).
3. `RegisterAppender`. Your actor now receives each accepted statement as a
   message.

**Queue mode (non-actor consumers):**

1. `CreateRelayAppender` with `mode = queue`; keep `relay queue out`.
2. `RegisterAppender`.
3. In your consumer loop, Dequeue (or Flush) from `relay queue out`.

Because the relay is an appender, its threshold and filter apply, so you can
subscribe to just ERROR-and-above or just one source-tag subtree rather than the
whole stream.

---

## 9. Source tags and routing (worked examples)

### 9.1 Two files: full mirror plus errors-only

```
Initialize (default file = full mirror, threshold TRACE=6 on that file)

errAppender = CreateFileAppender(
    id="errors", root folder="...\errors",
    filter = MakeMirrorFilter,       threshold = ERROR (2))
RegisterAppender(errAppender)
```

The default file receives everything; `errors` receives only ERROR and FATAL
because its own threshold is 2 (SRS-LMBR-009, 040).

### 9.2 Route a subsystem to its own file

```
commsAppender = CreateFileAppender(
    id="comms", root folder="...\comms",
    filter = MakeRoutedFilter(level range = TRACE..FATAL, tag prefix = "app.comms"))
RegisterAppender(commsAppender)
```

Then log with tags:

```
Info(message="link up", source tag="app.comms.tcp")   -> lands in comms + any mirror files
Info(message="ui refresh", source tag="app.ui")        -> mirror files only, not comms
```

### 9.3 Relay ERROR-and-above to a UI actor

```
relay = CreateRelayAppender(
    mode = message, consumer enqueuer = <UI actor enqueuer>,
    filter = MakeRoutedFilter(level range = FATAL..ERROR, tag prefix = ""))
RegisterAppender(relay)
```

The UI actor receives only ERROR and FATAL statements as messages.

---

## 10. Layouts

A layout formats a statement into text (SRS-LMBR-015). Set it per appender via
the `layout` input.

- `CreateCSVLayout` *(default)*: columns are
  `timestamp, level, sourceTag, originVI, message`, delimiter per file
  appender, RFC 4180 quoting (SDD 5.4).
- `CreateJSONLayout`: one JSON object per statement.
- `CreateTextLayout`: a human-readable line.

Unwired, appenders use CSV.

---

## 11. Error handling

`CatchError` integrates with the LabVIEW General Error Handler to catch, log,
clear, and optionally display an error (SRS-LMBR-041).

- **Inputs:** `error in`, `logger in` *(opt)*.
- **Behavior:** logs the error (at a severity derived from the error), and shows
  a dialog only if the error's severity meets the configured verbosity (section
  5.2). Cleared errors do not propagate on `error out`.

---

## 12. Using Lumberjack from a Packed Project Library

When your application loads Lumberjack from a `.lvlibp`, do not rely on the
library to guess where to write logs (SRS-LMBR-064). Two habits keep paths
correct:

- Pass an explicit `root folder` to each file appender (or in the config file),
  rather than depending on a default.
- If you use relative paths or an empty `rootFolder` default, wire
  `host application path` into `Initialize` so defaults resolve against your
  application's directory, not a location inside the PPL.

When running as a **built application**, wiring `host application path` is not
just advisable but required for the relative/empty-root case: `Initialize`
returns a fatal **error 5000** if it must resolve such a root and no host path
was supplied. This is deliberate, in a built app the executable folder is often
read-only (Program Files under UAC), so Lumberjack refuses to guess rather than
write somewhere that silently fails. In the development system it falls back to
the application directory, so the error only surfaces in a deployed build.

Lumberjack itself never derives external paths from its own VI location.

---

## 13. Migration from Logger

| Logger | Lumberjack | Notes |
|---|---|---|
| `Initialize` | `Initialize` | Adds config-file path, host-app path, default-file config, disable-default-file. |
| `Trace`..`Fatal` | `Trace`..`Fatal` | Adds optional `source tag`; `logger in` optional. |
| `Shutdown` | `Shutdown` | Same flush-and-close semantics. |
| `ConfigureLevel` | `ConfigureLevel` | Now the stage-1 global threshold. |
| `ConfigureVerbosity` | `ConfigureVerbosity` | Unchanged in intent. |
| `Configure Maximum File Size/Count`, `Root Folder`, `File Extension`, `Delimiter`, `Calendar Folder Tree` | inputs to `CreateFileAppender` | Now per-appender, set at creation, not global. |
| `Disable Default File` | `disable default file?` input on `Initialize` | Folded into launch. |
| `Register Listener` / `Unregister Listener` | `RegisterAppender` / `UnregisterAppender` | Listener renamed appender; now filterable. |
| `Read Listener` | `CreateRelayAppender` (queue mode) + Dequeue | Or message mode for actor consumers. |
| `CatchError`, `MaskErrors` | `CatchError`, `MaskErrors` | Unchanged in intent. |

Behavioral changes to note: filtering is two-stage (global coarse plus
per-appender authoritative); multiple files with independent thresholds and
filters are supported; delivery is asynchronous and non-blocking; and dropped
statements under a bounded queue are surfaced as a synthetic record rather than
lost silently.

---

## 14. Full example: RT-friendly, two files, one relay

```
cfg = default file config (root=<app>\logs, calendar tree on, max size 10 MB, max count 20)
logger = Initialize(global threshold = INFO, default file config = cfg,
                    host application path = <app dir>)

# errors-only second file, bounded for an RT target, level-aware drop
err = CreateFileAppender(id="errors", root folder=<app>\logs\errors,
        filter = MakeMirrorFilter, threshold = ERROR,
        queue bound = 4096, drop policy = level-aware)
RegisterAppender(err)

# tap ERROR+ to the UI
relay = CreateRelayAppender(mode=message, consumer enqueuer=<UI>,
        filter = MakeRoutedFilter(level range = FATAL..ERROR, tag prefix=""))
RegisterAppender(relay)

# elsewhere, no handle needed (singleton)
Info("startup complete")
Error("sensor fault", source tag="app.sensors.mfc")

# at exit
Shutdown()
```
