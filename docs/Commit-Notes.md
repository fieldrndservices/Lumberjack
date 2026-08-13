# Commit Notes (working tracker)

Running list of changes **since the last commit**, so commit messages are accurate.
Workflow: I append each change here as we make it; when you commit, we move the
list under "Recent commits" and clear "Uncommitted." This file is a working aid,
gitignore it if you don't want it tracked.

---

## Uncommitted (since last commit)

- Tests/Support: file-mechanics test infrastructure -
  `Register File Appender.vi` (arrange a FileAppender from a `FileAppenderConfig`,
  register + `IDPresent` barrier; returns id, no queue), `List Log Files.vi`
  (recursive glob by extension, sorted, error-guarded), `Read Log Lines.vi`
  (read a file to non-empty records, EOL-normalized, error-guarded).

---

## Recent commits

### 2026-08-11 - Id-based Snapshot barriers, synchronous shutdown, relay tests + routed-filter fix

- Library: Snapshot -> `appenders` (RegistryEntry {id, enqueuer}); id-based
  `WaitForSnapshot` (`SnapshotWaitMode` + `SnapshotHasID`, 5030); Initialize /
  Register / Unregister re-pointed; synchronous `Shutdown` (`stoppedNotifier`,
  5032, `ClearProcessDefault`, `ManagerLaunchInputs`); `HandleStatement`
  routed-filter wire fix; `enableDefaultFile` validation gating; `GetID` /
  `RelayQueueName` public.
- Tests: integration (sequential) register/unregister, message mode
  (`Launch Consumer Relay`), filtered tap; `Register Relay Appender`,
  `Release Relay Queues`; `Close Test Mgr` unconditional teardown.
- Docs: Design §5.11 barriers + Snapshot ids + relay lifecycle + gating; 6 diagrams
  regenerated (SVG/py source committed); Class-Reference, API-Guide, PR-Notes,
  Test-Strategy, Error-Codes, Doc-Standards, Doc-Terminal-Audit updated; VI
  description cleanup.
