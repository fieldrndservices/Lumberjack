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
merge/validate/resolve with the native/DTO mappers) are scoped **community**,
and the test library (`tests/Tests.lvlib`)
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

---

## 4. Test inventory

Tier is U (unit) or I (integration). Each case lists the assertion intent and
the requirements it covers.

### 4.1 Statement and layout

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| CSV column order | fields emit as timestamp, level, sourceTag, originVI, message | U | 010, 012 |
| CSV quote escaping | a message with quotes/delimiter/newline is RFC 4180 quoted | U | 012 |
| CSV custom delimiter | tab delimiter applied (Logger parity) | U | 012 |
| ISO 8601 timestamp | timestamp field matches ISO 8601 | U | 011 |
| JSON layout | one valid JSON object per statement | U | 015 |
| Statement fields | origin VI and source tag are distinct and both present | U | 010, 013 |

### 4.2 Severity and filtering

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Rank compare | rank <= threshold passes, else dropped | U | 005, 006 |
| Threshold 0 | disables all logging | U | 006 |
| Threshold 7+ | passes all levels | U | 006 |
| Global coarse gate | statement above global threshold is not fanned out | U/I | 007, 012 |
| Per-appender threshold | appender writes only statements passing its own threshold | I | 009 |
| Mirror mode | accepts everything above threshold | U | 026 |
| Routed level range | accepts only within the inclusive rank band [levelMin, levelMax] (log4j LevelRangeFilter semantics: levelMin most severe, levelMax least severe) | U | 026 |
| Routed single level | levelMin == levelMax accepts exactly that one level | U | 026 |
| Tag prefix match | `app.db` matches `app.db` and `app.db.query`, not `app.database` (dot-boundary, via `RoutedFilterMatch`) | U | 027 |

### 4.3 Source tag

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Default tag | unset tag defaults to origin VI base name | U | 013, 017 |
| Dot sanitization | dots in a VI-derived default become single-node (no false hierarchy) | U | 013 |
| Explicit tag | supplied tag is used verbatim | U | 013 |

### 4.4 Configuration

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Input baseline | launch inputs produce the effective config with no file | U | 044 |
| JSON per-key merge | file overrides only the keys it sets; absent keys fall back | U | 046 |
| Missing file | defined path, missing file, returns non-fatal warning, continues | U | 047 |
| Invalid file | present but unparseable/invalid fails launch with a descriptive error | U | 048 |
| Field validation | out-of-range threshold, bad enum, negative size each named in the error | U | 048 |
| Enum name membership | unknown Severity/DropPolicy/FilterMode name is rejected with the accepted set listed | U | 048 |
| Bounded values | maxFileSize/maxFileCount/queueBound accept -1 (unbounded) and positive; reject 0 and < -1 | U | 033, 034, 056 |
| Schema version | schemaVersion accepted by set membership; a non-member is rejected | U | 048 |
| Resolve once | effective config computed once at launch | U/I | 051 |

### 4.5 Appenders and broadcast

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Single appender delivery | a statement reaches the one registered appender | I | 019 |
| Multi-appender broadcast | a statement reaches all registered appenders | I | 019, 028 |
| Register at runtime | a newly registered appender begins receiving | I | 020, 028 |
| Unregister at runtime | an unregistered appender stops receiving and flushes | I | 020 |
| Fault isolation | a stopped/faulted appender does not block delivery to others | I | 021 |
| Two files, distinct roots | mirror file and errors-only file receive the correct subsets | I | 032, 039, 040 |

### 4.6 File mechanics

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| ISO filename | each file name embeds an ISO 8601 timestamp (colons removed) | U/I | 035 |
| Base name prefix | non-empty baseName yields `baseName_<timestamp>.<ext>`; empty yields timestamp-only | U | 035 |
| Extension normalize | "csv" and ".csv" both yield one dot; empty extension yields no trailing dot | U | 035 |
| UTC frame agreement | useUTC selects one frame for file name, calendar folder, and timestamp column together | U | 011, 035, 036 |
| Rollover on size | exceeding max size opens a new file | I | 033 |
| Retention prune | files beyond max count are pruned oldest-first; -1 keeps all | U/I | 034 |
| Per-series prune | files with different base names in one folder are pruned independently, not against each other | U | 034 |
| Calendar tree | files placed in dated sub-folders when enabled | I | 036 |

### 4.7 Relay appender

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Message mode | accepted statements arrive at the consumer enqueuer | I | 024 |
| Queue mode | accepted statements are dequeueable from the exposed queue | I | 025 |
| Filtered tap | a routed/threshold relay receives only its subset | I | 023, 026 |

### 4.8 Backpressure

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Unbounded default | no loss with an unbounded queue | U/I | 055 |
| Drop-oldest | on a full bound, oldest is discarded, newest admitted | U | 057 |
| Drop-newest | on a full bound, newest is discarded | U | 057 |
| Level-aware | ERROR/FATAL never discarded; lower severities shed first | U | 057 |
| No blocking | enqueue path returns without blocking when full | U | 058 |
| Drop notice | discards produce a synthetic "N statements dropped" record | U/I | 059 |

### 4.9 Lifecycle and error handling

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Shutdown flush | queued statements are written before stop completes | I | 002 |
| Shutdown on error | shutdown flush/close runs even with an incoming error | I | 004 |
| CatchError log | a caught error is logged at a derived severity | I | 041 |
| Verbosity gate | dialog shown only at/above configured verbosity | U | 042 |

### 4.10 PPL path safety

| Case | Assertion | Tier | SRS |
|---|---|---|---|
| Explicit root honored | a supplied root folder is used verbatim | U | 039, 064 |
| Host-context default | empty root resolves against host app context, not the library path | U | 064 |
| Built-app requires path | with no host path and Application.Kind = Run Time System, resolution faults with error 5000 | U | 064 |
| No self-derived paths | no library VI derives an external path from its own VI path | U (inspection) | 064 |

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
