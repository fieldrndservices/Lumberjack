# Build Checklist: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)
**Companion documents:** Lumberjack SRS, SDD, API and Usage Guide, Message and Class Reference, Test Strategy
**Status:** Draft

**How to use:** Items are ordered so that every one depends only on items above it. The next unchecked box is always safe to start, and building this way never leaves a broken terminal behind you. Parentheticals name the direct dependencies or the reason for the position.

---

## Phase 0 - Shell

- [ ] 1. Create `Lumberjack.lvproj` in LabVIEW 2014; add a blank `Lumberjack.lvlib` as the namespace root; add the Actor Framework as the one runtime dependency. (Container first, so nothing added later needs renaming or relinking.)

## Phase 1 - Leaf typedefs

- [ ] 2. `Severity` enum. (No dependencies; referenced by nearly everything, so first.)
- [ ] 3. `Drop Policy`, `Relay Mode`, `Filter Mode` enums. (Standalone.)
- [ ] 4. `Statement` cluster. (Severity.)
- [ ] 5. `Filter` cluster. (Severity, Filter Mode.)

## Phase 2 - Layout

- [ ] 6. `Layout.lvclass` abstract, with `Format` (DD). (Statement.)
- [ ] 7. `CSV Layout`, `JSON Layout`, `Text Layout`, each overriding `Format`. (Layout, Statement.)

## Phase 3 - Config typedefs

- [ ] 8. `Appender Config`. (Severity, Filter, Drop Policy, Layout.)
- [ ] 9. `File Appender Config`, `Relay Appender Config`. (Appender Config; plus Relay Mode and Enqueuer for the relay.)
- [ ] 10. `Lumberjack Config`. (Severity, File Appender Config.)
- [ ] 11. `Snapshot`. (Severity, Enqueuer.)

## Phase 4 - Pure support VIs

*Unit tests (Caraya) can begin as soon as each VI here exists.*

- [ ] 12. Severity helpers: `Rank Compare`, `Level String`.
- [ ] 13. Tag helpers: `Default Source Tag`, `Sanitize`.
- [ ] 14. File helpers: `ISO 8601 File Name`, `Base Folder`, `Prune selection`.
- [ ] 15. Path helper: `Resolve Host Root`. (The only place allowed to compute external paths.)
- [ ] 16. Config: `Merge` (Unflatten From JSON, baseline as default), `Validate`, `Resolve`. (Lumberjack Config, native JSON.)

## Phase 5 - Appender base, message, concretes

*Integration tests via a console or relay-queue capture probe can begin once the concretes exist, before the manager or facade.*

- [ ] 17. `Appender.lvclass` (Actor subclass): `Init Common`, `Get ID`, `Handle Statement`, abstract `Open Sink`/`Write`/`Close Sink` (DD), `Actor Core`. (Phases 1-3.)
- [ ] 18. `Log Statement Msg`: payload `Statement`; `Do.vi` calls `Appender:Handle Statement`. (Statement, Appender.)
- [ ] 19. `Console Appender`: sink overrides. (Appender; simplest concrete, build first.)
- [ ] 20. `File Appender`: sink overrides, `Open New File`, `Prune`. (Appender, File Appender Config, Phase-4 file helpers.)
- [ ] 21. `Relay Appender`: `Write` sends `Log Statement Msg` or enqueues, `Get Relay Queue`. (Appender, Relay Appender Config, Log Statement Msg.)

## Phase 6 - Root actor and control messages

- [ ] 22. `Log Manager.lvclass`: `Resolve Config`, `Launch Appender`, `Post Snapshot`, `Actor Core` (launch default File Appender, post initial Snapshot), `Handle Stop`. (Appender/File Appender, Snapshot, Config VIs.)
- [ ] 23. Control messages: `Register Appender`, `Unregister Appender`, `Set Global Threshold`, `Configure Appender`, `Configure`. (Their `Do.vi` call Log Manager and Appender methods, so after both.)

## Phase 7 - Facade and singleton

- [ ] 24. `Logger.lvclass` data (Notifier + manager enqueuer) and `Log.vi` (read Snapshot, stage-1 gate, build Statement, fan out Log Statement Msg). (Snapshot, Statement, Log Statement Msg.)
- [ ] 25. Store: `Set Process Default`, `Get Process Default`. (Logger type from item 24.)
- [ ] 26. `Initialize` (launch Log Manager, create Notifier, post initial Snapshot, store default) and `Shutdown`. (Log Manager, Store.)
- [ ] 27. Logger control wrappers: `Configure Level`, `Configure Verbosity`, `Register`/`Unregister`/`Configure Appender`, `Catch Error`. (Phase-6 messages.)
- [ ] 28. The six level VIs `Trace`, `Debug`, `Info`, `Warn`, `Error`, `Fatal`, each wrapping `Log.vi` with a fixed level. (Log.vi.)

## Phase 8 - Surface and packaging

- [ ] 29. Curated palette `.mnu` files (Action-Status, Appenders, Configure, Data, Utility).
- [ ] 30. `examples/`: Simple, Two Files, Routed by tag, Relay to UI actor.
- [ ] 31. Finalize `tests/` (Unit began at Phase 4, Integration at Phase 5); wire the `Test.vi` runner.
- [ ] 32. `Scripts`: `Build PPL`, `Package`, `Build` (source dist).

---

**Test milestones**

- [ ] After Phase 4: all pure logic (layout formatting, filter matching, config merge/validate, tag and path resolution, retention selection) is unit-testable.
- [ ] After Phase 5: an appender can be launched with a capture probe to verify delivery, threshold, and filter before the manager and facade exist.
- [ ] After Phase 7: end-to-end singleton and instance calling styles verified.
