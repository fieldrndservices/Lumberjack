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

- [x] 12. Severity helpers: `RankCompare`, `LevelString`.
- [x] 13. Tag helpers: `DefaultSourceTag`, `Sanitize`.
- [x] 14. File helpers: `ISO8601FileName`, `BaseFolder`, `PruneSelection`
      (`PruneSelection` groups files by baseName, then keeps the newest
      maxFileCount per group, so different series in one folder never prune
      against each other).
- [x] 15. Path helper: `ResolveHostRoot`. (The only place allowed to compute
      external paths.)
- [ ] 16. Config: `Merge` (Unflatten From JSON, baseline as default),
      `Validate`, `Resolve`. (LumberjackConfig, native JSON.)

## Phase 5 - Appender base, message, concretes

*Integration tests via a console or relay-queue capture probe can begin once the
concretes exist, before the manager or facade.*

- [ ] 17. `Appender.lvclass` (Actor subclass): `InitCommon`, `GetID`,
      `HandleStatement`, abstract `OpenSink`/`Write`/`CloseSink` (DD),
      `Actor Core`. (Phases 1-3.)
- [ ] 18. `LogStatementMsg`: payload `Statement`; `Do.vi` calls
      `Appender:HandleStatement`. (Statement, Appender.)
- [ ] 19. `ConsoleAppender`: sink overrides. (Appender; simplest concrete,
      build first.)
- [ ] 20. `FileAppender`: sink overrides, `OpenNewFile`, `Prune` (lists only its
      own `baseName_*` files before calling `PruneSelection`, so it never
      touches another appender's logs). (Appender, FileAppenderConfig, Phase-4
      file helpers.)
- [ ] 21. `RelayAppender`: `Write` sends `LogStatementMsg` or enqueues,
      `GetRelayQueue`. (Appender, RelayAppenderConfig, LogStatementMsg.)

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

---

**Test milestones**

- [ ] After Phase 4: all pure logic (layout formatting, filter matching, config
      merge/validate, tag and path resolution, retention selection) is
      unit-testable.
- [ ] After Phase 5: an appender can be launched with a capture probe to verify
      delivery, threshold, and filter before the manager and facade exist.
- [ ] After Phase 7: end-to-end singleton and instance calling styles verified.

---

## Future / backlog (post-1.0)

These are deferred enhancements, not part of the initial build, and they sit on
the configuration-input side (parsing config at Initialize), not the layout
side (formatting log output). See the note below.

- [ ] F1. `ConfigReader` strategy: an abstract reader (parse a file into a
      LumberjackConfig override), with the current native-JSON path refactored
      into a `JSONConfigReader`; select the reader by file extension in
      `Resolve`. (Item 16.)
- [ ] F2. `INIConfigReader` (native Config File VIs) and `XMLConfigReader`
      (native LabVIEW XML). (F1.)
- [ ] F3. `YAMLConfigReader` - needs a third-party YAML library, so revisit
      the zero-runtime-dependency stance (SRS DEP-1) before committing. (F1.)

Note: configuration-file formats are read on input to build LumberjackConfig;
they are not Layout subclasses (layouts format log output). A JSON config file
and the JSONLayout are unrelated.
