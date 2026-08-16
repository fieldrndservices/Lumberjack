# Test Strategy: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Lumberjack SRS (SRS-LMBR-001 .. 064), SDD, API and
Usage Guide, Message and Class Reference

**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose

This document defines how Lumberjack is verified: the test framework, the tiers
of tests, the seams the design exposes for testing, and a requirement-traceable
inventory of test cases. It is modeled on the predecessor Logger's test project
and extends it to cover Lumberjack's broader behavior.

### 1.2 Scope

Verification of the runtime library against the SRS. Build and packaging scripts
are out of scope except that the test suite must run from the project (as
Logger's did). This is a non-regulated project, so the intent is engineering
confidence and regression safety, not a formal V&V record; nonetheless tests are
traced to requirements so coverage gaps are visible.

---

## 2. Review of the predecessor's coverage

Logger's tests use Caraya (`Assert Equal`, `Assert Not Error`) with a
temporary-folder setup/teardown fixture.

| Logger test VI | Exercises |
|---|---|
| Create Statement Line with double quotes | CSV line formatting, RFC 4180 quoting of embedded quotes (pure utility) |
| Message with Double Quotes | end-to-end `Info` with quotes in the message |
| Tab Delimiter | configuring and applying a tab delimiter |
| Disable Default File | disable default file + unregister listener; no writes, no error |
| Support/Before File Logging | fixture: generate a temporary root folder |
| Support/After File Logging | fixture: clear errors |
| Toolkit.vi | Caraya suite aggregator |

Logger's coverage is narrow and formatting-centric. Untested, even for Logger's
own features: level/threshold filtering, broadcast to multiple listeners,
`Read Listener` consumption, file rollover by size, retention/pruning by count,
calendar folder tree, ISO 8601 naming, verbosity and CatchError, and
buffer/Maximum Messages behavior.

Two things are worth carrying forward: Caraya as the framework (continuity, and
it is a test-only dependency that ships with nothing, per SRS DEP-1), and the
temporary-folder fixture that keeps file tests isolated and repeatable.

---

## 3. Test approach

### 3.1 Framework

Caraya is retained. It matches Logger, and it stays test-only (not a runtime
dependency, SRS-LMBR-061, DEP-1). The native LabVIEW Unit Test Framework is a
viable alternative if the JKI dependency is to be dropped from the test tier as
well; the strategy below is framework-neutral and would port.

### 3.2 Two tiers

- **Unit tier (pure VIs, no actors).** Fast, deterministic, no launched actors
  and no real I/O beyond a temp folder. This tier carries the bulk of coverage
  because the design pushed decision logic (filtering, formatting, config
  resolution, path resolution, retention) into pure VIs rather than into actor
  loops.
- **Integration tier (launched actors).** Launches a LogManager with a capture
  appender, drives log calls, and asserts on delivered content. Used only where
  behavior is genuinely emergent from the actor topology (broadcast,
  register/unregister, flush-on-shutdown, relay delivery).

### 3.3 Test seams the design exposes

- **Pure VIs.** `Layout.Format`, `Filter` matching, config
  resolve/merge/validate, tag defaulting and dot-sanitization, severity rank
  comparison, ISO 8601 filename building, retention/prune selection, and
  drop-policy selection are all callable directly with no actor context. The CSV
  `Layout.Format` test is the direct descendant of Logger's Create Statement
  Line test.
- **Capture probe.** The relay appender in queue mode is a ready-made test
  probe: register it, drive log calls, then Dequeue or Flush its queue and
  assert exactly what was delivered, in what order, after which filters. A small
  dedicated Capture Appender test double is an alternative if a purpose-built
  probe is preferred.
- **Injectable Layout and Filter.** Because both are supplied to an appender at
  creation, a test can inject a trivial identity layout or a known filter to
  remove formatting and selection variance from an assertion.

To keep the pure-VI seam usable, the pure support helpers (`src/Support/`
Severity, Enum, Tag, File, Filter, and Config: rank comparison, enum name/string
conversion, tag defaulting and sanitization, ISO 8601 filename building,
base-folder computation, prune selection, routed-filter matching, and config
merge/validate/resolve with the native/DTO mappers) are scoped
**protected**, and the test library (`tests/Tests.lvlib`)
is declared a **friend** of `Lumberjack.lvlib`. That lets the unit tests call
these helpers directly while keeping them off the public (PPL-exported) surface,
so adopters still cannot. The stateful/constrained helpers, Store
(`SetProcessDefault`/`GetProcessDefault`) and Path (`ResolveHostRoot`), stay
**private** and are exercised through behavior rather than called directly.

### 3.4 Fixtures

- **Temp root fixture** (SetUp/TearDown): create a unique temporary root folder
  before file tests and delete it after, so file appenders never touch shared
  locations and runs are repeatable. This generalizes Logger's Before/After File
  Logging.
- **Manager fixture:** launch a LogManager with the default file disabled and
  exactly the appenders a test needs, then shut it down in TearDown, asserting a
  clean flush.
- **Default-file cleanup:** `Test.vi` deletes the default log file at suite start
  when its path input is empty (a non-empty path suppresses it), so a stale
  default file from a prior run can't pollute the suite. Complements the temp-root
  fixture (per-test file isolation) and the manager fixture (clean flush).

### 3.5 Determinism rule

Enqueue-to-delivery latency is explicitly non-deterministic (SRS-LMBR-053).
Therefore:

- No test asserts on timing, latency, or delivery order across different
  appenders.
- Integration tests drain-then-assert: shut down (or flush) so all queued
  statements are processed, then assert on the eventual delivered content.
- Concurrency and backpressure-under-load are verified by testing the
  drop-policy selection as a pure VI (deterministic) and asserting the synthetic
  drop-notice record appears, rather than by racing producer threads.
- Lifecycle transitions use the library's **synchronous confirmation barriers**
  (Design §5.11), not sleeps: `Open Test Mgr`/`Initialize` blocks on readiness,
  `Register Relay Appender`/`RegisterAppender` on the appender id appearing,
  `UnregisterAppender` on it leaving, and `Close Test Mgr`/`Shutdown` on the actor
  tree stopping. This is what makes drain-then-assert deterministic without timing
  guesses. (The one earlier 1 s fixture sleep was removed once these landed.)
- **Integration tests must run sequentially.** They share process-global state,
  the process-default logger/manager and the named relay queues, so running two at
  once cross-contaminates (a queue in one test receives another test's statement).
  `Close Test Mgr` tears down its manager and force-destroys its queues so the next
  sequential test starts clean. Unit tests are pure (no launched framework, no
  shared globals) and may run in parallel.

---

## 4. Test inventory

Tier is U (unit) or I (integration). Each case carries a stable case-level
**Test ID** (`LMBR-T-###`), the assertion intent, the requirements it covers,
and the VI(s) that implement it (`planned` where no VI is built yet).

The case-level Test ID is the unit of trace to the SRS. Within a VI, each
individual Caraya assert carries that case ID plus a suffix letter
(`LMBR-T-014-a`, `-b`, ...), so every assert is uniquely identified in the report
while still rolling up to one requirement. A case may be implemented across more
than one VI; its assert suffixes run continuously so no two asserts share an ID
(for example T-005 spans both JSON VIs, `-a..-d` in `Layout - JSON Format.vi`
and `-e..-k` in `Layout - JSON escape string.vi`). A single VI likewise holds
asserts from more than one case (for example `Layout - CSV quoting.vi` carries
T-002 quoting asserts and T-003 delimiter asserts). A requirement with no Test
ID is a coverage gap; a `planned` row is a case with no implementing VI yet. The
per-assert suffix map is maintained in `Test-ID-Assert-Checklist.md`.

**Assert-naming convention.** Each Caraya assert's name begins with its
hierarchical Test ID, e.g. `LMBR-T-014-c Level within band is accepted`. Caraya
writes each assert name into `tests/Test Results/LumberjackTestResults.txt` and
the HTML report, so the Test ID is the join key between a report line and this
matrix: every executed assert reports its own pass/fail under its own ID even
when several share one VI. IDs are assigned once and never reused, so a report
archived today still resolves against a future revision of this table.

### 4.1 Statement and layout

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-001 | CSV column order | fields emit as timestamp, level, sourceTag, originVI, message | U | 010, 012 | tests/Unit/Layout - CSV quoting.vi |
| LMBR-T-002 | CSV quote escaping | a message with quotes/delimiter/newline is RFC 4180 quoted | U | 012 | tests/Unit/Layout - CSV quoting.vi |
| LMBR-T-003 | CSV custom delimiter | tab delimiter applied; comma not quoted under tab (Logger parity) | U | 012 | tests/Unit/Layout - CSV quoting.vi |
| LMBR-T-004 | ISO 8601 timestamp | timestamp field matches ISO 8601 | U | 011 | tests/Unit/Layout - ISO 8601 timestamp.vi |
| LMBR-T-005 | JSON layout | one valid JSON object per statement, strings correctly escaped | U | 015 | tests/Unit/Layout - JSON Format.vi; tests/Unit/Layout - JSON escape string.vi |
| LMBR-T-006 | Statement fields | origin VI and source tag are distinct and both present | U | 010, 013 | planned |

### 4.2 Severity and filtering

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-007 | Rank compare | rank <= threshold passes, else dropped | U | 005, 006 | tests/Unit/Severity - rank compare.vi |
| LMBR-T-008 | Severity name round trip | severity name <-> rank round-trips for FATAL..TRACE | U | 005, 050a | tests/Unit/Severity - name round trip.vi |
| LMBR-T-009 | Threshold 0 | disables all logging | U | 006 | tests/Unit/Severity - rank compare.vi |
| LMBR-T-010 | Threshold 7+ | passes all levels | U | 006 | tests/Unit/Severity - rank compare.vi |
| LMBR-T-011 | Global coarse gate | statement above global threshold is not fanned out | U/I | 007 | tests/Integration/Filtering - global gate.vi |
| LMBR-T-012 | Per-appender threshold | appender writes only statements passing its own threshold | I | 009 | tests/Integration/Filtering - per-appender threshold.vi |
| LMBR-T-013 | Mirror mode | accepts everything above threshold | U | 026 | tests/Integration/Filtering - mirror mode.vi |
| LMBR-T-014 | Routed level range | accepts only within the inclusive rank band [levelMin, levelMax] (log4j LevelRangeFilter semantics: levelMin most severe, levelMax least severe) | U | 026 | tests/Unit/Filter - level range.vi |
| LMBR-T-015 | Routed single level | levelMin == levelMax accepts exactly that one level | U | 026 | tests/Unit/Filter - level range.vi |
| LMBR-T-016 | Tag prefix match | `app.db` matches `app.db` and `app.db.query`, not `app.database` (dot-boundary, via `RoutedFilterMatch`) | U | 027 | tests/Unit/Filter - tag prefix.vi |

### 4.3 Source tag

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-017 | Default tag | unset tag defaults to origin VI base name | U | 013, 017 | tests/Unit/Source tag - defaulting.vi |
| LMBR-T-018 | Dot sanitization | dots in a VI-derived default become single-node (no false hierarchy) | U | 013 | tests/Unit/Source tag - defaulting.vi |
| LMBR-T-019 | Explicit tag | supplied tag is used verbatim | I | 013 | tests/Integration/Source tag - explicit.vi |

### 4.4 Configuration

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-020 | Input baseline | launch inputs produce the effective config with no file | U | 044 | tests/Unit/Config - resolve.vi |
| LMBR-T-021 | JSON per-key merge | file overrides only the keys it sets; absent keys fall back | U | 046 | planned |
| LMBR-T-022 | Missing file | defined path, missing file, returns non-fatal warning, continues | U | 047 | tests/Unit/Config - resolve.vi |
| LMBR-T-023 | Invalid file | present but unparseable/invalid fails launch with a descriptive error | U | 048 | tests/Unit/Config - resolve.vi |
| LMBR-T-024 | Field validation | out-of-range threshold, bad enum, negative size each named in the error | U | 048 | tests/Unit/Config - validate.vi |
| LMBR-T-025 | Enum name membership | unknown Severity/DropPolicy/FilterMode name is rejected with the accepted set listed | U | 048 | tests/Unit/Severity - name round trip.vi; tests/Unit/Enum - DropPolicy and FilterMode.vi |
| LMBR-T-026 | Bounded values | maxFileSize/maxFileCount/queueBound accept -1 (unbounded) and positive; reject 0 and < -1 | U | 033, 034, 056 | tests/Unit/Config - validate.vi |
| LMBR-T-027 | Schema version | schemaVersion accepted by set membership; a non-member is rejected | U | 048 | tests/Unit/Config - validate.vi |
| LMBR-T-028 | Resolve once | effective config computed once at launch | U/I | 051 | planned |
| LMBR-T-060 | Enum name conversion | DropPolicy/FilterMode member name maps to the correct typed value (round-trip) | U | 050a | tests/Unit/Enum - DropPolicy and FilterMode.vi |
| LMBR-T-061 | DTO<->native round-trip | each config DTO<->native mapper pair round-trips a distinctive value with no field lost | U | 050a | tests/Unit/Config - DTO round trip.vi |

### 4.5 Appenders and broadcast

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-029 | Single appender delivery | a statement reaches the one registered appender | I | 019 | tests/Integration/Delivery - single appender.vi |
| LMBR-T-030 | Multi-appender broadcast | a statement reaches all registered appenders | I | 019, 028 | tests/Integration/Delivery - broadcast.vi |
| LMBR-T-031 | Register at runtime | a newly registered appender begins receiving | I | 020, 028 | tests/Integration/Registry - register at runtime.vi |
| LMBR-T-032 | Unregister at runtime | an unregistered appender stops receiving and flushes | I | 020 | tests/Integration/Registry - unregister silences appender.vi |
| LMBR-T-033 | Fault isolation | a stopped/faulted appender does not block delivery to others | I | 021 | tests/Integration/Fault Isolation - stopped appender.vi |
| LMBR-T-034 | Two files, distinct roots | mirror file and errors-only file receive the correct subsets | I | 032, 039, 040 | planned |

### 4.6 File mechanics

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-035 | ISO filename | each file name embeds an ISO 8601 timestamp (colons removed) | U/I | 035 | tests/Unit/ISO 8601 filename.vi |
| LMBR-T-036 | Base name prefix | non-empty baseName yields `baseName_<timestamp>.<ext>`; empty yields timestamp-only | U | 035 | tests/Unit/ISO 8601 filename.vi |
| LMBR-T-037 | Extension normalize | "csv" and ".csv" both yield one dot; empty extension yields no trailing dot | U | 035 | tests/Unit/ISO 8601 filename.vi |
| LMBR-T-038 | UTC frame agreement | within one appender, useUTC frames its file name, calendar folder, and layout line timestamp identically; appenders may differ (e.g. local console + UTC file) | U | 011, 035, 036 | tests/Unit/Layout - UTC frame agreement.vi |
| LMBR-T-039 | Rollover on size | exceeding max size opens a new file | I | 033 | planned |
| LMBR-T-040 | Retention prune | files beyond max count are pruned oldest-first; -1 keeps all | U/I | 034 | tests/Unit/Retention prune.vi |
| LMBR-T-041 | Per-series prune | files with different base names in one folder are pruned independently, not against each other | U | 034 | tests/Unit/Retention prune.vi |
| LMBR-T-042 | Calendar tree | files placed in dated sub-folders when enabled | I | 036 | planned |

### 4.7 Relay appender

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-043 | Message mode | accepted statements arrive at the consumer enqueuer | I | 024 | tests/Integration/Relay - Message Mode.vi |
| LMBR-T-044 | Queue mode | accepted statements are dequeueable from the exposed queue | I | 025 | planned |
| LMBR-T-045 | Filtered tap | a routed/threshold relay receives only its subset | I | 023, 026 | tests/Integration/Relay - filtered tap.vi |

### 4.8 Backpressure

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-046 | Unbounded default | no loss with an unbounded queue | U/I | 055 | planned |
| LMBR-T-047 | Drop-oldest | on a full bound, oldest is discarded, newest admitted | U | 057 | planned |
| LMBR-T-048 | Drop-newest | on a full bound, newest is discarded | U | 057 | planned |
| LMBR-T-049 | Level-aware | ERROR/FATAL never discarded; lower severities shed first | U | 057 | planned |
| LMBR-T-050 | No blocking | enqueue path returns without blocking when full | U | 058 | planned |
| LMBR-T-051 | Drop notice | discards produce a synthetic "N statements dropped" record | U/I | 059 | planned |

### 4.9 Lifecycle and error handling

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-052 | Shutdown flush | queued statements are written before stop completes | I | 002 | planned |
| LMBR-T-053 | Shutdown on error | shutdown flush/close runs even with an incoming error | I | 004 | planned |
| LMBR-T-054 | CatchError log | a caught error is logged at a derived severity | I | 041 | planned |
| LMBR-T-055 | Verbosity gate | dialog shown only at/above configured verbosity | U | 042 | planned |

### 4.10 PPL path safety

| Test ID | Case | Assertion | Tier | SRS | Implementing VI |
|---|---|---|---|---|---|
| LMBR-T-056 | Explicit root honored | a supplied root folder is used verbatim | U | 039, 064 | tests/Unit/Path - ResolveHostRoot.vi |
| LMBR-T-057 | Host-context default | empty root resolves against host app context, not the library path | U | 064 | tests/Unit/Path - ResolveHostRoot.vi |
| LMBR-T-058 | Built-app requires path | with no host path and Application.Kind = Run Time System, resolution faults with error 5000 (via injectable app kind seam); resolved root is Not A Path | U | 064 | tests/Unit/Path - ResolveHostRoot.vi |
| LMBR-T-059 | No self-derived paths | no library VI derives an external path from its own VI path | U (inspection) | 064 | docs/Path-Derivation-Audit.md |

---

## 5. Deliberately not unit-tested

- **Timing and latency:** excluded by the determinism rule (SRS-LMBR-053).
- **Cross-appender ordering:** not guaranteed once queues drain concurrently
  (SRS-LMBR-054); tests assert per-appender order only.
- **True concurrent-overload races:** approximated by pure drop-policy tests
  plus the drop-notice assertion, rather than by nondeterministic thread races.
- **Real disk-full / permission failures:** the config-vs-resource boundary
  (SRS-LMBR-049) is asserted by construction (invalid resource surfaces as the
  appender's launch error), with at most one opt-in test using a deliberately
  unwritable path.

---

## 6. Test organization

Mirrors Logger's layout, expanded:

```
tests/
  Tests.lvlib                     Caraya suite membership
  Unit/                           pure-VI tests (no actors)
    Layout - CSV quoting.vi
    Filter - tag prefix.vi
    Config - JSON merge.vi
    ...
  Integration/                    launched-actor tests
    Broadcast - multi appender.vi
    Relay - queue mode.vi
    File - rollover.vi
    ...
  Support/                        fixtures
    SetUp - temp root.vi
    TearDown - delete temp root.vi
    Launch test manager.vi
    Capture appender probe.vi
```

A `Test.vi` runner (as in Logger's Scripts library) executes the full suite.
Unit tests run without launching the framework; integration tests use the
manager and temp-root fixtures and always tear down with a clean shutdown
assertion.

---

## 7. Coverage summary

The strategy touches every requirement group in the SRS. Notably, the majority
of behavior lands in the deterministic unit tier because filtering, formatting,
configuration, retention, and path resolution were designed as pure VIs. The
integration tier is reserved for the genuinely emergent behaviors of the actor
topology: broadcast, runtime register/unregister, relay delivery, file rollover,
and flush-on-shutdown. This is a substantial expansion over Logger's
formatting-centric suite while keeping the fast, repeatable core that Logger
established.
