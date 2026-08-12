# Cleanup: Suggested Description Text

Ready-to-paste VI Documentation and terminal Description/Tip text for the items in
`Cleanup-Checklist.md` §1-§3, in the `Doc-Standards.md` format. VI Documentation is
given in a literal code block (single line per paragraph) so it pastes into the
LabVIEW Documentation field without soft-wrap line breaks. DD object terminals
(`Logger in/out`, `<Class> in/out`) stay blank; the `error in/out` cluster keeps
LabVIEW's standard boilerplate. All text is SOP-117 draft, review before use.

---

## Logger.Shutdown

**VI Documentation:**

```
Stops the logging system and blocks until it is fully down. Sends the framework Stop to the LogManager, then waits on stoppedNotifier until the manager and all nested appenders have stopped (each having flushed and closed its sink). Runs its stop even if error in carries an error (SRS-LMBR-004). On a clean stop, merges the manager's exit error into error out; if the tree does not stop within timeout ms, returns error 5032. Releases both notifiers and clears the process-default logger before returning. Because it is synchronous, on return it is safe to reclaim application-owned resources such as relay queues. Control plane; not on the logging hot path.
```

| Terminal | Description | Tip |
|---|---|---|
| `timeout ms` | Max time to wait for the actor tree to stop before returning error 5032. Defaults to the shutdown constant. | Stop-wait budget (ms); 5032 on expiry |

---

## ClearProcessDefault

**VI Documentation:**

```
Clears the process-default Logger so ResolveLogger returns no instance until the next Initialize. Called by Shutdown during teardown so a stale default does not outlive the manager it referenced. Idempotent: clearing when no default is set is a no-op.
```

(Terminals: `error in/out` standard. Add descriptions for any data terminals it
actually exposes.)

---

## Logger.RegisterAppender

**VI Documentation:**

```
Registers a constructed, configured appender with the running logger and blocks until it is live. Sends RegisterAppenderMsg to the LogManager (which launches the appender as a nested actor and posts an updated Snapshot), then blocks on WaitForSnapshot(IDPresent, id) until the appender's id appears in a Snapshot, so the next Log reaches it (SRS-LMBR-020, 028). The id is read from the appender's common config (GetID). No-op passthrough if no logger resolves (+29). Control plane; not on the hot path.
```

(Terminals: `appender in` is a class object, DD/blank; `Logger in/out` DD/blank;
`error in/out` standard.)

---

## Logger.UnregisterAppender

**VI Documentation:**

```
Removes an appender from the running logger and blocks until it is gone. Sends UnregisterAppenderMsg(id) to the LogManager (which removes the registry entry, posts a Snapshot without that id, then stops the appender so it flushes and closes), then blocks on WaitForSnapshot(IDAbsent, id) until the id is absent from a Snapshot. Unregistering an id that was never registered is a benign no-op that returns immediately (the +28 warning is raised in the manager). Control plane; not on the hot path.
```

| Terminal | Description | Tip |
|---|---|---|
| `id` | Id of the appender to remove; must match the id it was registered with. | Appender id to unregister |

---

## Logger.WaitForSnapshot

**VI Documentation:**

```
Blocks until the manager's published Snapshot satisfies the selected condition, or the timeout expires; makes control-plane operations synchronous without sleeps. SnapshotWaitMode selects the condition: AnySnapshot (any Snapshot received = manager readiness, used by Initialize), IDPresent (an appender with targetID appears = registration confirmed, used by RegisterAppender), IDAbsent (no appender with targetID remains = unregistration confirmed, or the id was never present, used by UnregisterAppender). Uses a deadline computed once (deadline = start + timeout), each wait consuming the remaining time, so the total wait is bounded. Outputs a valid Snapshot only on the success path; on timeout returns error 5030 with the caller context. Control plane; not on the hot path.
```

| Terminal | Description | Tip |
|---|---|---|
| `notifier` | The Snapshot notifier the manager posts to (`snapshotNotifier`). | Snapshot notifier to watch |
| `mode` (`SnapshotWaitMode`) | Condition to wait for: `AnySnapshot`, `IDPresent`, or `IDAbsent`. | Wait condition |
| `targetID` | Appender id the `IDPresent`/`IDAbsent` conditions test for; ignored for `AnySnapshot`. | Appender id to wait for |
| `timeout ms` | Max wait before giving up; expiry returns error 5030. | Wait budget (ms); 5030 on expiry |
| `context` | Caller context spliced into the 5030 message so a timeout names the operation (e.g. `Appender 'x' registration`). | Context for 5030 message |
| `snapshot` (out) | The Snapshot that satisfied the condition; valid only when `error out` is clean. | Satisfying Snapshot (valid on success) |

---

## SnapshotHasID

**VI Documentation:**

```
Returns whether an appender with the given id is present in a published Snapshot. Scans the Snapshot's appenders array for an exact id match and short-circuits on the first hit. Used by WaitForSnapshot to evaluate the IDPresent/IDAbsent conditions, and available to tests asserting registry membership. Pure: no state, no side effects.
```

| Terminal | Description | Tip |
|---|---|---|
| `snapshot` | The published Snapshot to search; its `appenders` array is scanned. | Snapshot to search |
| `id` | The appender id to look for (exact, case-sensitive match). | Appender id to find |
| `found` | TRUE if an appender with this id is present; FALSE otherwise (including an empty Snapshot). | TRUE if id present |

---

## LogManager.PostSnapshot

**VI Documentation:**

```
Builds the current Snapshot (globalThreshold from the resolved config, and the appenders array from the registry, one RegistryEntry {id, enqueuer} per registered appender) and posts it to the shared notifier via Send Notification. Callers read this Snapshot non-destructively on the hot path. Called after any change to the threshold or appender set: initial launch, register, unregister, and threshold change. The LogManager is the sole poster of the notifier (SRS-LMBR-052, SDD 2.1).
```

---

## Snapshot.ctl

**Control description:**

```
The Notifier payload the LogManager broadcasts to callers (SDD 2.1, 2.3). Read by every caller on the log hot path: globalThreshold gates stage-1, and the appenders array is the fan-out target list. The LogManager is the sole poster; callers only read (Get Notifier Status), so reads are concurrent and non-destructive. Internal type, not part of the public API.
```

| Field | Description | Tip |
|---|---|---|
| `globalThreshold` | (keep existing Severity description) | Stage-1 coarse threshold |
| `appenders` | Array of `RegistryEntry {id, enqueuer}`, one per registered appender. The hot path fans out over each entry's enqueuer; barriers (`WaitForSnapshot`) key on the id so a specific appender's presence/absence is observable (SDD 5.11). | Fan-out targets (id + enqueuer) |

(`id`/`enqueuer` subfield descriptions come from `RegistryEntry.ctl`. Confirm the
vestigial `appenderEnqueuers` field is removed.)

---

## ManagerLaunchInputs.ctl

**Control description:**

```
The launch inputs the Logger stamps into the LogManager before Launch (via SetLaunchInputs). Bundled into one cluster so the connector pane stays within terminal limits and new inputs are a typedef edit. Consumed once at startup; the running state lives in the manager's resolved config and private data thereafter.
```

| Field | Description | Tip |
|---|---|---|
| `stoppedNotifier` | The shared Notifier (error cluster) the manager fires at Actor Core exit, after all nested appenders have stopped. Held by the Logger so `Shutdown` can block until the tree is down; must be set before the manager is launched. | Stopped signal (fired at exit) |

(Other fields, `initialGlobalThreshold`, `hostApplicationPath`, `configFilePath`,
`snapshotNotifier`, are already described.)
