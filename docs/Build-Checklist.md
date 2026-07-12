# Build Checklist: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Lumberjack SRS, SDD, API and Usage Guide, Message and
Class Reference, Test Strategy

**Status:** Draft

**How to use:** Items are ordered so that every one depends only on items above
it. The next unchecked box is always safe to start, and building this way never
leaves a broken terminal behind you. Parentheticals name the direct dependencies
or the reason for the position.

---

## Phase 0 - Shell

- [x] 1. Create `Lumberjack.lvproj` in LabVIEW 2014; add a blank
      `Lumberjack.lvlib` as the namespace root; add the Actor Framework as the
      one runtime dependency. (Container first, so nothing added later needs
      renaming or relinking.)

## Phase 1 - Leaf typedefs

- [x] 2. `Severity` enum. (No dependencies; referenced by nearly everything, so
      first.)
- [x] 3. `DropPolicy`, `RelayMode`, `FilterMode` enums. (Standalone.)
- [x] 4. `Statement` cluster. (Severity.)
- [x] 5. `Filter` cluster. (Severity, FilterMode.)

## Phase 2 - Layout

- [x] 6. `Layout.lvclass` abstract, with `Format` (DD). (Statement.)
- [x] 7. `CSVLayout`, `JSONLayout`, `TextLayout`, each overriding `Format`.
      (Layout, Statement.)

## Phase 3 - Config typedefs

- [x] 8. `AppenderConfig`. (Severity, Filter, DropPolicy, Layout.)
- [x] 9. `FileAppenderConfig`, `RelayAppenderConfig`. (AppenderConfig; plus
      RelayMode and Enqueuer for the relay.)
- [x] 10. `LumberjackConfig`. (Severity, FileAppenderConfig.)
- [x] 11. `Snapshot`. (Severity, Enqueuer.)

## Phase 4 - Pure support VIs

*Unit tests (Caraya) can begin as soon as each VI here exists.*

- [x] 12. Severity helpers: `RankCompare` (`src/Support/Severity`).
      (`LevelString` is renamed `SeverityString` and relocated to
      `src/Support/Enum/` with the enum round-trip set, see R5.)
- [x] 13. Tag helpers: `DefaultSourceTag`, `Sanitize`.
- [x] 14. File helpers: `ISO8601FileName`, `BaseFolder`, `PruneSelection`
      (`PruneSelection` groups files by baseName, then keeps the newest
      maxFileCount per group, so different series in one folder never prune
      against each other; `maxFileCount = -1` keeps all, see R7).
- [x] 15. Path helper: `ResolveHostRoot`. (The only place allowed to compute
      external paths.)
- [x] 15a. `IsFileNameSafe` (community, `src/Support/File/`): checks a filename
      component; empty is safe, dots are legal, illegal set is
      `< > : " / \ | ? *` and control chars. Faults directly with config error
      +20 (5020) on an illegal value, taking a context input
      (`baseName`/`extension`) so the message names the field. Shared by the
      launch (`Validate`) and runtime (`CreateFileAppender`) paths.
- [x] 16. Config: `Merge` (Unflatten From JSON, baseline DTO as default) and
      `Validate` operate on the string DTO; `Resolve` maps the validated DTO to
      the native `LumberjackConfig` (names to enums, `String To Path`) and
      resolves paths. `schemaVersion` is a String in canonical `00.00.01`
      form; `CheckSchemaVersion.vi` owns the accepted set, faults on a
      non-member (message lists the accepted set), and exposes the current
      version the baseline DTO stamps so a file omitting the key reads as
      current. `Validate` delegates the schemaVersion step to it. `Validate`
      decomposes into per-DTO validators (`ValidateFilterDTO`,
      `ValidateAppenderConfigDTO`, `ValidateFileAppenderConfigDTO`,
      `ValidateLumberjackConfigDTO`), each checking its scalars and delegating
      nested clusters, chained on the error wire so the first bad field stops
      the rest. The runtime path (`CreateFileAppender`) reuses the individual
      field checks (`IsFileNameSafe`, bounded values, routed range), not the DTO
      validators, since its inputs are already typed.
      (DTO mirror types + enum lookups, R4/R5; native JSON.)

## Phase 5 - Appender base, message, concretes

*Integration tests via a console or relay-queue capture probe can begin once the
concretes exist, before the manager or facade.*

- [x] 17. `Appender.lvclass` (Actor subclass): `InitCommon`, `GetID`,
      `HandleStatement`, abstract `OpenSink`/`Write`/`CloseSink` (DD),
      `Actor Core`. (Phases 1-3.)
- [x] 18. `LogStatementMsg`: payload `Statement`; `Do.vi` calls
      `Appender:HandleStatement`. (Statement, Appender.)
- [x] 19. `ConsoleAppender`: sink overrides. (Appender; simplest concrete,
      build first.)
- [x] 20. `FileAppender`: sink overrides, `OpenNewFile`, `Prune` (lists only its
      own `baseName_*` files before calling `PruneSelection`, so it never
      touches another appender's logs). Trusts `baseName`/`extension` are
      already safe (checked via `IsFileNameSafe` at Validate/creation, item
      15a). The size-rollover check has a `maxFileSize == -1` early-out (no
      size rollover); `0` never reaches here (rejected by Validate).
      (Appender, FileAppenderConfig, Phase-4 file helpers.)
- [x] 21. `RelayAppender`: `Write` sends `LogStatementMsg` or enqueues,
      `GetRelayQueue`. (Appender, RelayAppenderConfig, LogStatementMsg.)
- [ ] 21a. Backpressure increment (DEFERRED to a follow-up PR, not in the
      AppenderDevelopment PR). Goal: bounded memory under sustained overload
      with a drop policy, without unbounded queue growth. The earlier Option B
      sketch (separate bounded buffer in `Appender` private data, drained by a
      parallel loop in `Actor Core`) is to be RECONSIDERED before building: it
      duplicates the AF queue's own producer/consumer machinery and adds a
      second concurrent loop. A simpler design to evaluate first is a
      bounded-enqueue-with-drop at send time (track each appender's in-flight
      backlog; when it reaches `queueBound`, apply `dropPolicy` and
      `EmitDropNotice` instead of enqueuing), keeping `HandleStatement -> Write`
      synchronous and leaving `Actor Core` unchanged. Decide the design in the
      follow-up. `queueBound = -1` bypasses backpressure. (Appender,
      LogStatementMsg; SRS-LMBR-055-059.)

## Phase 6 - Root actor and control messages

- [ ] 22. `LogManager.lvclass`: `ResolveConfig`, `LaunchAppender`,
      `PostSnapshot`, `Actor Core` (launch default FileAppender, post initial
      Snapshot), `HandleStop`. (Appender/FileAppender, Snapshot, Config VIs.)
- [ ] 23. Control messages: `RegisterAppender`, `UnregisterAppender`,
      `SetGlobalThreshold`, `ConfigureAppender`, `Configure`. (Their `Do.vi`
      call LogManager and Appender methods, so after both.)

## Phase 7 - Facade and singleton

- [ ] 24. `Logger.lvclass` data (Notifier + manager enqueuer) and `Log.vi` (read
      Snapshot, stage-1 gate, build Statement, fan out LogStatementMsg).
      (Snapshot, Statement, LogStatementMsg.)
- [ ] 25. Store: `SetProcessDefault`, `GetProcessDefault`. (Logger type from
      item 24.)
- [ ] 26. `Initialize` (launch LogManager, create Notifier, post initial
      Snapshot, store default) and `Shutdown`. (LogManager, Store.)
- [ ] 27. Logger control wrappers: `ConfigureLevel`, `ConfigureVerbosity`,
      `Register`/`Unregister`/`ConfigureAppender`, `CatchError`. (Phase-6
      messages.)
- [ ] 28. The six level VIs `Trace`, `Debug`, `Info`, `Warn`, `Error`, `Fatal`,
      each wrapping `Log.vi` with a fixed level. (Log.vi.)

## Phase 8 - Surface and packaging

- [ ] 29. Curated palette `.mnu` files (Action-Status, Appenders, Configure,
      Data, Utility).
- [ ] 30. `examples/`: Simple, Two Files, Routed by tag, Relay to UI actor.
- [ ] 31. Finalize `tests/` (Unit began at Phase 4, Integration at Phase 5);
      wire the `Test.vi` runner.
- [ ] 32. `scripts`: `Build PPL`, `Package`, `Build` (source dist).
- [ ] 33. Fault code mapping: express every Lumberjack error code as
      `LumberjackErrorBase + offset`, where `LumberjackErrorBase` is a single
      compile-time constant defaulting to 5000. The block spans
      `Base .. Base+99` and moves as a unit if an integrator relocates it to
      avoid collision with other libraries in the same process (compile-time
      keeps the error-text file valid; regenerate that file for a changed
      base). Assigned offsets: +0 (ResolveHostRoot, host path required in a
      built app); +10..13 (`SeverityFromString` / `DropPolicyFromString` /
      `FilterModeFromString` / `RelayModeFromString`, unknown name); +20
      (illegal filename character in baseName/extension, raised by
      `Validate`/`CreateFileAppender` from `IsFileNameSafe`); +21 (unsupported
      schemaVersion, `CheckSchemaVersion`); +22 (bounded value invalid:
      maxFileSize/maxFileCount/queueBound must be -1 or positive); +23 (routed
      filter level range out of order); +24 (empty appender id); +25 (invalid
      DTO field type, structural dispatch default); +26 (`RelayAppender`
      resource invalid at `OpenSink`: message mode requires a valid consumer
      enqueuer, queue mode requires an obtained relay queue); +27..39 reserved
      for other checks. Register the block in an error-text file
      (`errors/Lumberjack-errors.txt`) so `General Error Handler` shows the
      message; messages should name the offending value and list the valid
      members. Keep `Base+99` within the 5000-9999 user range for any chosen
      base.

---

**Test milestones**

- [ ] After Phase 4: all pure logic (layout formatting, filter matching, config
      merge/validate, tag and path resolution, retention selection) is
      unit-testable.
- [ ] After Phase 5: an appender can be launched with a capture probe to verify
      delivery, threshold, and filter before the manager and facade exist.
- [ ] After Phase 7: end-to-end singleton and instance calling styles verified.

---

## Rework from the config-as-data + native-typedef (Option B / P1) decisions

Config typedefs stay **native** (real enums, `Path`, data only, no
objects/refnums/DVRs). A separate string **DTO mirror** is the JSON unflatten
target and merge currency; `Resolve` maps DTO to native. These touch built
items.

- [x] R1. AppenderConfig (item 8): remove the `layout` (Layout object) field;
      config carries only data. The appender constructs its Layout at InitCommon
      (default `CSVLayout` from `delimiter`; programmatic injection via
      `CreateFileAppender`'s `layout` input).
- [x] R2. RelayAppenderConfig (item 9): remove the `consumerEnqueuer` (Enqueuer)
      field; it is supplied at appender creation and held in private data.
- [x] R3. Confirm the native config typedefs carry only data and stay native (no
      field-type flips): Filter (item 5) native enums; FileAppenderConfig
      (item 9) `rootFolder` stays `Path`; LumberjackConfig (item 10)
      `globalThreshold` stays `Severity`.
- [x] R4. Add the string DTO mirror typedefs: `FilterDTO`, `AppenderConfigDTO`,
      `FileAppenderConfigDTO`, `LumberjackConfigDTO` (every enum as a name
      string, every `Path` as a string, otherwise 1:1 with native config). These
      are the `Unflatten From JSON` target and the merge currency.
- [x] R5. Add enum-name lookups (pure, community) in `src/Support/Enum/`:
      name-to-enum `SeverityFromString`, `DropPolicyFromString`,
      `FilterModeFromString` (map DTO to native), and enum-to-name for building
      the baseline DTO from typed launch inputs: rename `LevelString` to
      `SeverityString` and move it here, and add `DropPolicyString` and
      `FilterModeString`. Unknown name returns a descriptive error.
- [x] R6. Sweep every native config cluster for non-data types; none may remain.
      The DTO mirror holds only strings/numbers/booleans.
- [x] R7. Bounded-value convention (`-1` = unbounded, `0` invalid, positive =
      limit) for `maxFileSize`, `maxFileCount`, `queueBound`: make the fields
      signed (`I64`/`I32`/`I32`), and change `PruneSelection`'s keep-all
      early-out from `maxFileCount == 0` to `== -1` (item 14, built). `Validate`
      rejects `0` and values below `-1`; the size-rollover check gains a
      `maxFileSize == -1` early-out (item 20).

Conversion location is settled: `Merge`/`Validate` operate on the DTO;
`Resolve` maps DTO to native; `CreateFileAppender` takes typed inputs.

---

## Future / backlog (post-1.0)

These are deferred enhancements, not part of the initial build, and they sit on
the configuration-input side (parsing config at Initialize), not the layout
side (formatting log output). See the note below.

- [ ] F1. `ConfigReader` strategy: an abstract reader (parse a file into a
      LumberjackConfig override), with the current native-JSON path refactored
      into a `JSONConfigReader`; select the reader by file extension in
      `Resolve`. Readers parse straight to the config cluster plus a presence
      mask (not to a JSON string); `Merge` then becomes cluster-over-cluster
      (baseline, override, mask) instead of baseline-over-JSON-text, so the
      per-key override no longer depends on the JSON-only default-value trick.
      Keep `Resolve` the only place that reads a file as text so this refactor
      stays localized. (Item 16.)
- [ ] F2. `INIConfigReader` (native Config File VIs) and `XMLConfigReader`
      (native LabVIEW XML). (F1.)
- [ ] F3. `YAMLConfigReader` - needs a third-party YAML library, so revisit
      the zero-runtime-dependency stance (SRS DEP-1) before committing. (F1.)
- [ ] F4. Optional `LayoutKind` enum (CSV/JSON/Text) as a pure-data config field
      plus a one-VI factory (enum -> instantiate the matching Layout subclass)
      called at `InitCommon`, so JSON can select the layout without putting a
      class object in the config. Enum is serializable; the object is still
      constructed, not deserialized. (Pairs with F1.)

Note: configuration-file formats are read on input to build LumberjackConfig;
they are not Layout subclasses (layouts format log output). A JSON config file
and the JSONLayout are unrelated. The JSON-facing config is pure data (no class
objects, refnums, or DVRs); the appender constructs its Layout from data fields
at InitCommon, and programmatic layout injection stays a code path. Enums are
serialized by member name (string), which is what lets the future INI/YAML/XML
readers converge on the same name-to-enum lookup instead of each handling
ordinals or numeric typing.
