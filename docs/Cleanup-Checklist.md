# Cleanup Checklist (before the next integration test)

Punch list from the 2026-08-08 doc review / HTML-report scan. Clear these, re-run
the report, then move on to the relay message-mode test. Source of the VI items:
`Doc-Terminal-Audit.md` §5. All description text remains SOP-117 draft until
reviewed.

---

## 1. VI descriptions missing entirely (write in LabVIEW)

- [ ] **`Logger.Shutdown`** — add VI Documentation (send framework Stop, wait on
  `stoppedNotifier`, error 5032 on timeout, merge exit error, release both
  notifiers, clear process default). Describe the `timeout ms` terminal.
- [ ] **`ClearProcessDefault`** — add VI Documentation + terminal descriptions.
- [ ] **`Logger.RegisterAppender`** — add VI Documentation (sends
  `RegisterAppenderMsg`, then `WaitForSnapshot(IDPresent, id)`; live on return).
- [ ] **`Logger.UnregisterAppender`** — add VI Documentation (`IDAbsent` barrier;
  unknown id is a benign immediate no-op, +28).

## 2. Stale (count-based) text to rewrite (id-based design)

- [ ] **`Logger.WaitForSnapshot`** — VI Documentation still says "at least
  `minEnqueuers` ... prior count + 1"; rewrite to the `SnapshotWaitMode` predicate
  (AnySnapshot / IDPresent / IDAbsent, `targetID`). Then:
  - [ ] `targetID` description (currently the old count text) -> "appender id to
    wait for; ignored for AnySnapshot."
  - [ ] `Context` description (currently "unknown name") -> the barrier context
    spliced into the 5030 message.
  - [ ] `Snapshot` output description -> "the Snapshot that satisfied the wait;
    valid only on the success path."
- [ ] **`SnapshotHasID`** — `id` input description (old count text) -> "appender id
  to search for." Check the VI doc for a truncated leading char ("eturns ...").
- [ ] **`LogManager.PostSnapshot`** — doc says "array of appender enqueuers from
  the registry"; now builds the `appenders` array of `RegistryEntry {id, enqueuer}`.
- [ ] **`Snapshot.ctl`** — top description says "the enqueuer array is the fan-out
  target list"; update to `appenders` (array of `RegistryEntry`).

## 3. Blank fields to fill

- [ ] **`Snapshot.ctl` `appenders`** field — no description; add it.
- [ ] **`Snapshot.ctl` `enqueuer`** subfield — carries stale Actor Framework
  boilerplate; replace with the intended meaning.
- [ ] **`ManagerLaunchInputs.ctl` `stoppedNotifier`** field — blank; add it.
- [ ] **`ManagerLaunchInputs.ctl`** top-level control description — blank; add it.

## 4. Naming / structure consistency

- [ ] Reconcile terminal naming to the `Doc-Standards` convention: `Context` vs
  `context`, `timeout_ms` vs `timeout ms` (pick one form, apply on
  `WaitForSnapshot` and `Shutdown`).
- [ ] Confirm `Snapshot.ctl` has only `appenders` (no leftover `appenderEnqueuers`
  field lingering from the reshape).
- [ ] Confirm scope promotions landed: `RelayAppender.RelayQueueName` public (used
  by `Release Relay Queues`), `Appender.GetID` public.

## 5. Verify + close out

- [ ] Re-run `PrintLibraryToHTML`; confirm §1-§3 cleared (0 real-data blanks, no
  count-based text) and flip `Doc-Terminal-Audit.md` back to COMPLETE.
- [ ] Run the suite: unit tests (parallel) + integration tests (**sequential**) ->
  all green.
- [ ] Commit.

---

## Already handled in this review (doc files, no action)

- `Class-Reference.md`: `Snapshot` cluster -> `appenders`/`RegistryEntry`; Logger
  & LogManager private data (`snapshotNotifier` + `stoppedNotifier`); Register /
  Unregister / Shutdown barrier descriptions; added `WaitForSnapshot`,
  `SnapshotHasID`, `ClearProcessDefault`; `PostSnapshot` and `Actor Core` fixed;
  FileAppender private data `fileConfig` -> `file`.
- `API-Guide.md`: ready-on-return `Initialize` (5030); synchronous Register /
  Unregister / Shutdown; Shutdown `timeout ms` + 5032.
- `Design.md`: `SnapshotEntry` -> `RegistryEntry`.
- `PR-Notes.md`: id-based barrier refresh, shutdown/5032, `Release Relay Queues`,
  register/unregister test, sequential-integration note.
- `Test-Strategy.md`: synchronous-barrier determinism rule + sequential-integration
  constraint.
- `Error-Codes.md`: 5030 and 5032 registered and marked implemented.

## Deferred (not blocking the next test)

- Fault-path unit tests (Error-Codes `Test?` column still N).
- `Support.lvlib` extraction (Build-Checklist 28a).
- ConfigReader design write-up (Design §4.5).
- Diagram source is SVG (Mermaid render blocked in sandbox); regenerate via
  `docs/diagrams/src/seqgen.py` + `blockgen.py` if edited.
