# Lumberjack

An Actor Framework logging library for LabVIEW: a log4j-style logger with
severity levels, pluggable appenders, per-appender filtering and routing, and
non-blocking asynchronous delivery. It is a redesign of the earlier
singleton "Logger" library on top of the NI Actor Framework.

**Status:** design complete; implementation in progress (see the build checklist).

## Requirements

- LabVIEW 2014 or newer (native JSON and the Actor Framework).
- NI Actor Framework (the only runtime dependency).
- Caraya, for the test suite only (not required at runtime).

## What it does

- Six severity levels (Fatal, Error, Warn, Info, Debug, Trace) with a global
  threshold and per-appender thresholds.
- Appenders are independent actors: file (rolling, retained), console, and a
  relay that hands statements back to your application.
- Two-stage filtering: a coarse global gate on the caller side, then an
  authoritative per-appender threshold and selection filter (mirror, or routed
  by level range and hierarchical source tag).
- Non-blocking delivery with optional bounded queues and drop policies.
- Singleton by default (log from anywhere with no handle) with an optional
  instance API.

## Quick start

Singleton style, three nodes:

1. `Initialize` at application start.
2. `Info`, `Error`, etc. anywhere, with a message string. No handle needed.
3. `Shutdown` at exit to flush and close.

See the API and Usage Guide for configuration, appenders, routing, and the
instance API.

## Repository layout

```
src/         the Lumberjack.lvlib and all classes, types, and support VIs
docs/        specification and guides (Markdown source; .docx are rendered)
examples/    runnable usage examples
tests/       Caraya unit and integration tests
Scripts/     build, package, and test runners
configs/     VI Package build spec
```

The full layout, element-to-path mapping, and packaging notes are in the
Design Document, section 8.

## Documentation

Markdown is the source of truth; the `.docx` files are rendered from it.

- Requirements: [`docs/Lumberjack-Requirements.md`](docs/Lumberjack-Requirements.md)
- Design: [`docs/Lumberjack-Design.md`](docs/Lumberjack-Design.md)
- API and usage: [`docs/Lumberjack-API-Guide.md`](docs/Lumberjack-API-Guide.md)
- Message and class reference: [`docs/Lumberjack-Class-Reference.md`](docs/Lumberjack-Class-Reference.md)
- Test strategy: [`docs/Lumberjack-Test-Strategy.md`](docs/Lumberjack-Test-Strategy.md)
- Build checklist: [`docs/Lumberjack-Build-Checklist.md`](docs/Lumberjack-Build-Checklist.md)

## Building and testing

- Build the packed library with `Scripts/Build PPL.vi`, the VI Package with
  `Scripts/Package.vi`, and a source distribution with `Scripts/Build.vi`.
- Run the test suite with `Scripts/Test.vi` (Caraya). Unit tests cover the pure
  VIs; integration tests use a relay-queue capture probe.

## Working with the source in git

LabVIEW files are marked binary in `.gitattributes` because git cannot safely
merge them. Use NI **LVCompare** and **LVMerge** to diff and merge VIs and
classes visually. Build outputs (`.lvlibp`, `.vip`) and LabVIEW caches are
ignored; see `.gitignore`.

## License

3-clause BSD. See [`docs/LICENSE.txt`](docs/LICENSE.txt). Change history is in
[`docs/CHANGELOG.md`](docs/CHANGELOG.md).
