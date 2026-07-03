# Software Requirements Specification: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Predecessor:** Logger (non-AF, log4j-style LabVIEW library)

**Document type:** Software Requirements Specification (SRS)

**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose

This SRS specifies the requirements for **Lumberjack**, an Actor Framework (AF)
reimplementation of the existing **Logger** library for LabVIEW. It defines what
Lumberjack shall do, independent of how the VIs are implemented, so that
adopters and future maintainers have a single behavioral contract to build and
verify against.

### 1.2 Scope

Lumberjack provides application logging and error-handling for LabVIEW programs.
It accepts log statements from any part of an application, applies a coarse
global filter, and broadcasts surviving statements to one or more independent
sinks (file, console, network, custom). Each sink is an actor with its own
threshold and selection filter, so multiple sinks can run concurrently and
receive either a full mirror of the log stream or a routed subset. Multiple file
sinks may write to distinct files at the same time. The Actor Framework model
replaces Logger's internal queue-per-listener broadcast with one actor per sink,
so that a slow or failing sink cannot stall the caller or the other sinks.

This document is a *target* specification. Each requirement carries a lineage
tag showing its relationship to the as-built Logger:

- **[P] Preserved** — behavior carried over unchanged from Logger.
- **[C] Changed** — behavior that exists in Logger but is modified by the AF
  model.
- **[N] New** — behavior introduced by Lumberjack that Logger did not provide.

### 1.3 Definitions

| Term | Meaning |
|---|---|
| Statement | One log record: timestamp, level, origin, message. |
| Level / Severity | Ranked category of a statement (FATAL..TRACE). |
| Threshold | The global numeric level below which statements are discarded. |
| Appender | A sink that consumes statements (file, console, TCP, custom). In Lumberjack an appender is an actor. |
| Listener | Logger's term for an appender. Retained here only when referring to the old library. |
| Enqueuer | An AF message-queue reference held by a caller; the only handle used to send to an actor. |
| Source tag | A hierarchical, dot-separated logical category assigned to a statement for routing (log4j-style, e.g. `app.comms.tcp`). Defaults to the origin VI's base name when the caller supplies none. |
| PPL | Packed Project Library (.lvlibp): a single-file, compiled distribution of a LabVIEW project library. |
| Root actor | The top-level Lumberjack actor that owns configuration and launches appenders. |

### 1.4 References

- Logger source project (as-built), README and in-app Help (VI reference).
- Logger type definitions: `Severity.ctl`, `Tag.ctl`, `Statement.ctl`,
  `Configuration.ctl`.
- NI Actor Framework documentation.

---

## 2. Overall Description

### 2.1 Product perspective and lineage

Logger already implements an asynchronous broadcast internally: each registered
listener is given its own queue, and every surviving statement is enqueued to
all listener queues in receipt order. Lumberjack formalizes that design. The
queue-per-listener structure becomes one actor per appender, and the
enqueue-to-each-listener step becomes an AF message send to each appender's
enqueuer.

The engineering payoff follows from decoupling. In Logger the enqueue is
synchronous with respect to the internal manager; in Lumberjack the caller hands
off a message and returns immediately, and each appender drains its own queue on
its own thread. A file write that blocks on disk I/O therefore does not delay
the console appender, mirroring how Log4j 2 async loggers decouple the producing
thread from I/O via a ring buffer.

### 2.2 User characteristics

Adopters are LabVIEW developers integrating logging into an application. They
are assumed to be familiar with basic AF concepts (actors, messages, enqueuers)
at the level needed to launch the root actor and send log messages.

### 2.3 Assumptions and dependencies

- **ASM-1:** Configuration is supplied at launch via programmatic inputs,
  optionally overridden by a configuration file when a valid file path is
  provided (see 3.8). Runtime changes are applied via messages to the root
  actor.
- **ASM-2:** The NI Actor Framework is available in the target LabVIEW version.
  The minimum supported version is LabVIEW 2014 (see SRS-LMBR-062).
- **DEP-1:** Dependencies, by tier:
  - *Runtime:* NI Actor Framework only. Configuration JSON is parsed with native
    LabVIEW JSON primitives. No OpenG, no JKI State Machine, no third-party JSON
    library.
  - *Build / packaging:* VIPM for the VI Package build; optional VIPM Pro / VIPM
    API for automated builds.
  - *Test:* a unit-test framework (Caraya, or the native LabVIEW Unit Test
    Framework), test-only and not shipped in the library.
  - *Documentation:* Markdown (this document set). HTML Help Workshop is no
    longer required.

---

## 3. Specific Requirements

Notation: each requirement has an ID, a statement, and a lineage tag.

### 3.1 Lifecycle and instance management

- **SRS-LMBR-001 [C]** Lumberjack shall provide a launch operation that starts
  the root actor and returns the handle(s) needed to log. This replaces Logger's
  `Initialize`, which allocated internal buffers and the default file.
- **SRS-LMBR-002 [P]** Lumberjack shall provide a shutdown operation that
  flushes all pending statements to every appender, closes all files, and stops
  all appender actors before returning. Corresponds to Logger's `Shutdown`.
- **SRS-LMBR-003 [C]** The launch operation shall accept optional pre-allocation
  parameters (analogous to Logger's `Maximum Messages` and `Buffer Capacity`) so
  that memory can be bounded and pre-allocated for Real-Time / deterministic
  targets. See also SRS-LMBR-053.
- **SRS-LMBR-004 [N]** Shutdown shall be safe to call when a prior error is
  present on the error wire, completing its flush-and-close regardless (Logger's
  `Shutdown` had this property; it is stated explicitly here as a requirement).

### 3.2 Severity model and filtering

- **SRS-LMBR-005 [P]** Lumberjack shall define six severity levels with fixed
  numeric ranks: FATAL = 1, ERROR = 2, WARN = 3, INFO = 4, DEBUG = 5, TRACE = 6.
- **SRS-LMBR-006 [P]** A global threshold shall gate delivery: a threshold of 0
  disables all logging, and a threshold of 7 or higher passes all levels. A
  statement is delivered only if its rank is less than or equal to the
  threshold.
- **SRS-LMBR-007 [C]** Filtering shall be two-stage. Stage 1 is an optional
  global threshold applied on the caller side before broadcast: a statement
  whose rank exceeds the global threshold is not broadcast to any appender. This
  stage is a coarse volume-reducer only; a global threshold of 7 or higher (see
  SRS-LMBR-006) makes it a pass-through. Stage 2 is the per-appender threshold
  of SRS-LMBR-009, which is authoritative for what each sink actually writes.
- **SRS-LMBR-008 [P]** The global threshold shall be runtime-configurable
  (corresponds to Logger's `Configure Level`).
- **SRS-LMBR-009 [N]** Each appender shall have its own independently
  configurable level threshold, evaluated on receipt of a statement. An appender
  shall write a statement to its sink only if the statement passes that
  appender's threshold. Because this filter lives in the appender, callers
  remain decoupled from appender configuration and need not know any appender's
  threshold.

### 3.3 Logging statement

- **SRS-LMBR-010 [C]** A statement shall contain, at minimum: an ISO 8601
  timestamp, the level name, the source tag (SRS-LMBR-013), the name of the
  origin VI, and the user-supplied message. The origin VI (physical location)
  and the source tag (logical category) are distinct fields and both are
  retained.
- **SRS-LMBR-011 [P]** Timestamps shall be formatted per ISO 8601.
- **SRS-LMBR-012 [P]** The default file layout shall render a statement as a
  single delimited (CSV by default) line, with only the message field
  user-defined and the remaining fields, including the source tag, generated
  automatically.
- **SRS-LMBR-013 [N]** Each statement shall carry a source tag identifying its
  logical origin. The tag shall be a hierarchical, dot-separated string in the
  log4j style (for example, `app.comms.tcp`). When the caller does not supply a
  tag, it shall default to the base name of the origin VI with the file
  extension stripped, treated as a single-node tag.
- **SRS-LMBR-014 [P]** A statement shall be created and submitted even when an
  error is present on the incoming error wire (logging must not be suppressed by
  an upstream error).
- **SRS-LMBR-015 [N]** The statement-to-text mapping shall be encapsulated in a
  layout abstraction so that alternative layouts (e.g., JSON, plain text) can be
  provided without changing appenders.

### 3.4 Logging entry points

- **SRS-LMBR-016 [P]** Lumberjack shall provide one convenience logging
  operation per level: Trace, Debug, Info, Warn, Error, Fatal. Each creates a
  statement at its level and submits it subject to SRS-LMBR-007.
- **SRS-LMBR-017 [C]** Each convenience operation shall accept a user message
  string and an optional source tag, and shall generate all other statement
  fields automatically. When the source tag is not supplied, it shall default
  per SRS-LMBR-013, so the simple message-only call remains as simple as
  Logger's.

### 3.5 Appenders (listener model)

- **SRS-LMBR-018 [C]** Each appender shall be an independent actor that owns its
  own inbound message queue and its own sink resource. (Formalizes Logger's
  per-listener queue.)
- **SRS-LMBR-019 [P]** Surviving statements shall be broadcast to all currently
  registered appenders, in the order the statements were received.
- **SRS-LMBR-020 [P]** Appenders shall be registerable and unregisterable at
  runtime, each identified by a unique ID. Corresponds to Logger's
  `Register Listener` / `Unregister Listener`.
- **SRS-LMBR-021 [N]** A fault in one appender (blocked I/O, error, or stop)
  shall not prevent delivery of statements to other appenders, and shall not
  block the caller.
- **SRS-LMBR-022 [N]** Appenders shall process their queues concurrently, so
  that slow sink I/O in one appender does not delay another.
- **SRS-LMBR-023 [C]** Lumberjack shall provide a relay appender: a built-in
  appender type whose sink is the application rather than a file, giving
  application code programmatic access to the log stream. It corresponds to
  Logger's `Read Listener`, but being an appender it is subject to the common
  threshold (SRS-LMBR-009), selection filter (SRS-LMBR-026), and backpressure
  policy (SRS-LMBR-056, SRS-LMBR-057). It may therefore tap a filtered subset
  (for example, ERROR and above) rather than the entire stream, which
  `Read Listener` could not do.
- **SRS-LMBR-024 [N]** The relay appender's default delivery mode shall be
  message mode: each accepted statement is forwarded as a message to an
  application-supplied enqueuer. In this mode the consumer's own inbound queue
  is governed by the same backpressure policy as any appender, so a slow
  consumer degrades identically to a slow sink.
- **SRS-LMBR-025 [C]** The relay appender shall also provide a queue
  compatibility mode: it owns a LabVIEW queue and exposes the queue reference so
  application code can Dequeue or Flush statements, porting Logger's
  `Read Listener` and supporting consumption from non-actor code. This mode is
  poll-based and sits outside the AF message model; the consumer controls drain
  timing.
- **SRS-LMBR-026 [N]** Each appender shall have an independently configurable
  selection filter that determines which statements it accepts, selectable per
  appender between: (a) **mirror mode** — accept every statement that passes the
  appender's threshold (SRS-LMBR-009), producing a redundant full copy; and (b)
  **routed mode** — accept only a subset, filtered by level range and/or by
  source tag using hierarchical prefix matching (SRS-LMBR-013, SRS-LMBR-027).
- **SRS-LMBR-027 [N]** Routed-mode source-tag filtering shall use hierarchical
  prefix matching. Given a configured prefix P, a statement whose tag is T
  matches if T equals P, or T begins with P followed by the separator (that is,
  P or any descendant of P). For example, prefix `app.db` matches `app.db` and
  `app.db.query`, but not `app.database`.
- **SRS-LMBR-028 [N]** Multiple appenders of the same type shall be launchable
  and runnable concurrently, each independently configured (threshold, selection
  filter, and sink-specific settings). No global limit shall be imposed on the
  number of concurrent appenders other than available system resources.
- **SRS-LMBR-029 [N]** All appenders shall share a common configuration data
  structure, defined by the base appender type and inherited by every appender
  type. The common structure shall carry the fields every appender has: a unique
  appender ID, the level threshold (SRS-LMBR-009), and the selection filter mode
  and criteria (SRS-LMBR-026).
- **SRS-LMBR-030 [N]** Each concrete appender type shall extend the common
  configuration with its own type-specific fields (for example, the file
  appender adds root folder, maximum file size, maximum file count, extension,
  delimiter, and calendar-folder-tree enable). A type's own fields shall be
  owned and validated by that type, not by the root actor.
- **SRS-LMBR-031 [N]** Each appender shall be configured at the moment it is
  launched, through its own initialization, which applies the common fields
  (SRS-LMBR-029) and then the type-specific fields (SRS-LMBR-030). No central
  configuration list shall be required to create or configure appenders; the
  root actor shall handle every appender uniformly through the common base
  interface.

### 3.6 File appender

- **SRS-LMBR-032 [C]** Lumberjack shall provide a file appender type, and shall
  launch one default file appender at startup. Additional file appenders shall
  be launchable so that an application can write to multiple, distinct log files
  concurrently.
- **SRS-LMBR-033 [P]** Each file appender shall roll over to a new file when its
  current file exceeds a per-instance configurable maximum size (Logger's
  `Configure Maximum File Size`, now per instance).
- **SRS-LMBR-034 [P]** Each file appender shall retain at most a per-instance
  configurable maximum number of files, deleting the oldest on rollover; a value
  of 0 shall mean never delete (Logger's `Configure Maximum File Count`, now per
  instance).
- **SRS-LMBR-035 [P]** Every log file name shall include an ISO 8601 timestamp
  to prevent overwriting prior logs, regardless of folder organization.
- **SRS-LMBR-036 [P]** Each file appender shall optionally organize its files
  into a calendar-based folder hierarchy under its root folder, based on file
  creation date (Logger's `Configure Calendar Folder Tree`, now per instance).
- **SRS-LMBR-037 [P]** Each file appender shall support a per-instance
  configurable file extension and field delimiter (Logger's
  `Configure File Extension` / `Configure Delimiter`).
- **SRS-LMBR-038 [P]** The default file appender shall be disableable (Logger's
  `Disable Default File`).
- **SRS-LMBR-039 [C]** Each file appender shall have its own configurable root
  folder (Logger's `Configure Root Folder`, now per instance), so that distinct
  file appenders write to distinct locations.
- **SRS-LMBR-040 [N]** Each file appender's threshold (SRS-LMBR-009) and
  selection filter (SRS-LMBR-026) shall be configurable independently of every
  other appender, so that, for example, one file receives only ERROR-and-above
  while another receives a full TRACE-level mirror.

### 3.7 Error handling

- **SRS-LMBR-041 [P]** Lumberjack shall provide an error-catching operation that
  integrates with the LabVIEW General Error Handler to catch, log, clear, and
  optionally display errors (Logger's `Catch Error`).
- **SRS-LMBR-042 [P]** A verbosity setting shall determine whether an error
  dialog is shown to the user, based on error severity, independent of what is
  written to the log (Logger's `Configure Verbosity`).

### 3.8 Configuration

Configuration reaches Lumberjack from two sources at launch, plus runtime
messages thereafter.

- **SRS-LMBR-043 [C]** After launch, configuration operations (global threshold,
  per-appender threshold and filter, file size, file count, folder tree,
  extension, delimiter, root folder, verbosity, default-file enable) shall be
  applied at runtime by sending messages to the root actor, replacing Logger's
  synchronous Configure VIs. Applying configuration shall be safe relative to
  in-flight statements (ordering behavior specified in the SDD).
- **SRS-LMBR-044 [N]** The launch operation shall accept configuration inputs
  (the programmatic baseline) covering the global threshold and the default file
  appender's configuration. Additional appenders shall be constructed and
  configured programmatically, each through its own launch-time initialization
  (SRS-LMBR-031), rather than declared in a central list.
- **SRS-LMBR-045 [N]** The launch operation shall accept an optional
  configuration file path. When the path is defined and the file parses and
  validates against the expected schema, the file's values shall take precedence
  over the corresponding launch inputs.
- **SRS-LMBR-046 [N]** Precedence shall be per-setting: each value present in a
  valid config file overrides the matching launch input; any setting absent from
  the file shall fall back to the launch input value. This lets a file specify
  only the settings it wishes to change.
- **SRS-LMBR-047 [N]** When a config file path is defined but the file is
  **missing**, Lumberjack shall fall back to the launch inputs, complete launch,
  and return a non-fatal warning (LabVIEW warning convention: error-out status
  FALSE with a non-zero code) identifying the missing path. A missing optional
  config file shall not block application start.
- **SRS-LMBR-048 [N]** When a config file **is present but cannot be parsed or
  fails schema validation**, Lumberjack shall fail the launch with a descriptive
  error (error-out status TRUE) and shall not fall back. A malformed config
  cannot represent intended settings, and silently running on defaults would
  mask the fault. Because native JSON parsing reports only generic structural
  errors, field-level validation (required keys, value ranges, enumerations)
  shall be performed within Lumberjack so that the error message identifies the
  offending setting.
- **SRS-LMBR-049 [N]** SRS-LMBR-047 and SRS-LMBR-048 concern configuration
  parsing and schema validation only. Failure to realize a resource named by an
  otherwise valid configuration (for example, a root folder that cannot be
  created, or a path without write permission) is a launch error of the affected
  appender, reported through that appender, and is not a config-file failure.
- **SRS-LMBR-050 [N]** The configuration file, when provided, shall be JSON and
  shall carry the global settings and the default file appender's configuration.
  Because appenders are configured at their own launch (SRS-LMBR-031) and are
  not declared centrally, the file need not express a list of appenders. JSON is
  chosen for readable nested structure and because it keeps a future
  file-declared-appender option (a type-to-class factory reading an appender
  array) open without a format change. A developer adding appenders
  programmatically may source their values from the same file or elsewhere at
  their discretion.
- **SRS-LMBR-051 [N]** The resolved effective configuration (inputs merged with
  any valid file per SRS-LMBR-046) shall be the single configuration the root
  actor uses to launch appenders and establish thresholds and filters. The
  resolution shall occur once at launch.

### 3.9 Non-functional requirements

- **SRS-LMBR-052 [N]** A logging call shall return to the caller without waiting
  for any sink I/O to complete (asynchronous handoff).
- **SRS-LMBR-053 [C]** Enqueue-to-delivery latency through the AF message queue
  is not deterministic. Lumberjack shall not be used as the timing source for
  any fixed-rate control loop. Determinism-sensitive callers shall rely on
  pre-allocation (SRS-LMBR-003) to bound memory jitter, not on delivery timing.
- **SRS-LMBR-054 [P]** Within a single appender's queue, statements shall be
  delivered in the order received. (Cross-appender ordering is not guaranteed
  once queues drain concurrently — a consequence of SRS-LMBR-022.)
- **SRS-LMBR-055 [P]** Each appender's inbound queue shall be unbounded by
  default, matching Logger's default `Maximum Messages` of -1 (memory-limited).
  In this mode no statement is lost; the documented risk is unbounded memory
  growth if a sink is persistently slower than production.
- **SRS-LMBR-056 [C]** Each appender shall optionally be given a bounded queue
  capacity (maximum queued statements), configured per appender. This
  generalizes Logger's single global `Maximum Messages` to a per-appender
  setting and is the intended mode for Real-Time and embedded targets, where it
  also bounds memory and jitter (see SRS-LMBR-003, SRS-LMBR-053).
- **SRS-LMBR-057 [N]** When a bounded appender queue is full, the default policy
  shall be drop-oldest (ring buffer): the oldest queued statement is discarded
  to admit the newest, preserving the most recent events. Drop-newest and
  level-aware drop (shed lower-severity statements first, never discard ERROR or
  FATAL) shall be selectable alternatives, configured per appender.
- **SRS-LMBR-058 [N]** No backpressure policy shall block the producing caller.
  The asynchronous handoff of SRS-LMBR-052 shall hold under all queue
  conditions, so that a saturated or slow appender can never stall the caller
  or, via broadcast, the other appenders (SRS-LMBR-021). Blocking is explicitly
  excluded.
- **SRS-LMBR-059 [N]** Statement loss shall be observable. When statements are
  discarded under a bounded policy, the appender shall count the discards and
  surface them (for example, a synthetic "N statements dropped" record in that
  appender's own output) so that a gap in the log is visible rather than silent.
- **SRS-LMBR-060 [P]** Lumberjack shall be implemented entirely in LabVIEW (G)
  and shall run on any platform that runs the required LabVIEW version and Actor
  Framework.
- **SRS-LMBR-061 [C]** Lumberjack's only runtime dependency shall be the NI
  Actor Framework. Configuration JSON shall be parsed with LabVIEW's native JSON
  primitives (`Unflatten From JSON` / `Flatten To JSON`); no third-party JSON
  library shall be required. Logger's OpenG (Array/File) and JKI State Machine
  dependencies shall not be carried forward: native LabVIEW primitives shall
  provide file operations, and the Actor Framework run loop shall replace the
  JKI State Machine. Build, test, and documentation tooling are not runtime
  dependencies.
- **SRS-LMBR-062 [N]** The minimum supported LabVIEW version shall be 2014. This
  provides the native JSON primitives (introduced in 2013, adopted here with one
  version of margin) and satisfies the Actor Framework requirement (2012+).
- **SRS-LMBR-063 [N]** Lumberjack shall be buildable and distributable as a
  LabVIEW Packed Project Library (.lvlibp), in addition to source or VI Package
  distribution.
- **SRS-LMBR-064 [N]** Path resolution shall remain correct when Lumberjack
  executes from a Packed Project Library. The library shall not derive external
  resource locations from its own VI path (for example via `Current VI's Path`
  or `Application Directory`), because inside a PPL those resolve to a location
  that differs from the host application's directory. External paths, the file
  appender root folder and any relative configuration file path, shall be taken
  from launch inputs or configuration (SRS-LMBR-039, SRS-LMBR-045); where a
  default must be computed, it shall be based on the host application context,
  not the library's internal path.

---

## 4. Traceability Matrix

| Lumberjack requirement | Lineage | Logger origin |
|---|---|---|
| SRS-LMBR-001 | Changed | `Initialize` |
| SRS-LMBR-002 | Preserved | `Shutdown` |
| SRS-LMBR-003 | Changed | `Initialize` (Maximum Messages, Buffer Capacity) |
| SRS-LMBR-004 | New (made explicit) | `Shutdown` run-on-error behavior |
| SRS-LMBR-005 | Preserved | `Severity.ctl` / `Tag.ctl` |
| SRS-LMBR-006 | Preserved | `Configure Level` semantics |
| SRS-LMBR-007 | Changed | central filtering -> two-stage (global coarse + per-appender) |
| SRS-LMBR-008 | Preserved | `Configure Level` |
| SRS-LMBR-009 | New | per-appender threshold |
| SRS-LMBR-010..012 | Preserved / Changed | statement format + source tag, CSV layout |
| SRS-LMBR-013 | New | hierarchical source tag, defaults to origin VI |
| SRS-LMBR-014 | Preserved | statements created despite error in |
| SRS-LMBR-015 | New | layout abstraction |
| SRS-LMBR-016..017 | Preserved | Trace/Debug/Info/Warn/Error/Fatal VIs |
| SRS-LMBR-018 | Changed | per-listener queue -> appender actor |
| SRS-LMBR-019 | Preserved | broadcast in receipt order |
| SRS-LMBR-020 | Preserved | Register/Unregister Listener |
| SRS-LMBR-021..022 | New | fault isolation, concurrent drain |
| SRS-LMBR-023 | Changed | `Read Listener` -> relay appender (filterable) |
| SRS-LMBR-024 | New | message-mode delivery to app enqueuer |
| SRS-LMBR-025 | Changed | queue-mode compatibility port of `Read Listener` |
| SRS-LMBR-026 | New | per-appender selection filter (mirror / routed by level and tag) |
| SRS-LMBR-027 | New | hierarchical prefix tag matching |
| SRS-LMBR-028 | New | multiple concurrent appenders of same type |
| SRS-LMBR-029..030 | New | common appender config base + per-type extension |
| SRS-LMBR-031 | New | per-actor launch-time configuration, no central list |
| SRS-LMBR-032 | Changed | single file logger -> file appender type + multiple instances |
| SRS-LMBR-033..038 | Preserved | file config VIs, now per instance |
| SRS-LMBR-039 | Changed | `Configure Root Folder`, now per instance |
| SRS-LMBR-040 | New | independent per-file threshold and filter |
| SRS-LMBR-041..042 | Preserved | `Catch Error`, `Configure Verbosity` |
| SRS-LMBR-043 | Changed | Configure VIs -> runtime messages |
| SRS-LMBR-044..049 | New | launch inputs + optional JSON config file: precedence, merge, missing = warn/fallback, invalid = fail |
| SRS-LMBR-052 | New | async handoff |
| SRS-LMBR-053 | Changed | RT determinism guidance |
| SRS-LMBR-054 | Preserved | in-order per queue |
| SRS-LMBR-055 | Preserved | Maximum Messages = -1 default (unbounded) |
| SRS-LMBR-056 | Changed | Maximum Messages -> per-appender bound |
| SRS-LMBR-057 | New | drop-oldest default, selectable drop policies |
| SRS-LMBR-058 | New | blocking excluded, async holds under pressure |
| SRS-LMBR-059 | New | loss observability |
| SRS-LMBR-060 | Preserved | 100% G, portable |
| SRS-LMBR-061 | Changed | dependency set: AF only, native JSON, - OpenG, - JKI State Machine |
| SRS-LMBR-062 | New | minimum LabVIEW 2014 |
| SRS-LMBR-063 | New | PPL build / distribution |
| SRS-LMBR-064 | New | PPL-safe path resolution |

---

## 5. Open Items

None. All requirements are resolved. Remaining fine-grained decisions (tag
separator handling for VI names that contain dots, exact CSV column ordering,
JSON schema shape) are implementation details for the SDD, not open
requirements.
