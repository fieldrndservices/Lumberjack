# Error Code Registry: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Build-Checklist (item 33), Class-Reference, Test-Strategy

**Status:** Draft, reconciliation in progress. Seeded from the Build-Checklist
item 33 plan; the "Impl?" and "Raised by (confirmed)" columns need verifying
against the actual VIs. Review applies before this is authoritative.

---

## 1. Convention

- All Lumberjack codes are `LumberjackErrorBase + offset`, where
  `LumberjackErrorBase` is a single compile-time constant defaulting to **5000**.
- The block spans `Base .. Base+99` (5000-5099) and moves as a unit if an
  integrator relocates it to avoid collision with other libraries.
- Register every code in `errors/Lumberjack-errors.txt` so `General Error
  Handler` shows the message. Messages should name the offending value and, where
  relevant, list the valid members.
- Ideally raise all faults through one chokepoint helper (offset + context in →
  `Base + offset`), so codes can't drift out of this list again.
- **Source strings use a uniform `Lumberjack: <text>` prefix**, applied by the
  chokepoint helper, so faults are consistent and greppable. The runtime source
  adds context (the offending value, e.g. a path or name) after the prefix; the
  static description registered in `errors/Lumberjack-errors.txt` carries the
  general text.

Legend: **Impl?** = raised in code today (Y/N/?); **Test?** = exercised by a unit
test (Y/N).

---

## 2. Codes

| Offset | Code | Level | Raised by | Condition | Impl? | Test? |
|---|---|---|---|---|---|---|
| +0 | 5000 | Error | `ResolveHostRoot` | Host application path required in a built app (Application.Kind = Run Time System) | Y (in report) | Y (T-058, via injectable app kind) |
| +10 | 5010 | Error | `SeverityFromString` | Unknown Severity name | Y | N |
| +11 | 5011 | Error | `DropPolicyFromString` | Unknown DropPolicy name | Y | Y |
| +12 | 5012 | Error | `FilterModeFromString` | Unknown FilterMode name | Y | Y |
| +13 | 5013 | - | (unused) | No RelayModeFromString: RelayMode is not read from JSON (relay appenders are programmatic), so there is no name-to-enum conversion. Offset available. | - | - |
| +14 | 5014 | Warning | `Resolve` | Config file path defined but file not found; fell back to launch inputs (non-fatal). Source names the missing path (SRS-LMBR-047). | Y | Y |
| +20 | 5020 | Error | `IsFileNameSafe` (via `Validate` / `CreateFileAppender`) | Illegal filesystem character in baseName/extension | Y | Y |
| +21 | 5021 | Error | `CheckSchemaVersion` | Unsupported schemaVersion (not in accepted set) | Y | Y |
| +22 | 5022 | Error | `ValidateAppenderConfigDTO` (queueBound); file validators for maxFileSize/maxFileCount | Bounded value not `-1` or positive | Y | Y |
| +23 | 5023 | Error | `ValidateFilterDTO` | Routed level range out of order (levelMin/levelMax) | Y | Y |
| +24 | 5024 | Error | `ValidateAppenderConfigDTO` (+ other DTO validators) | Empty appender id | Y | Y |
| +25 | 5025 | Error | `ValidateAppenderConfigDTO` (+ other DTO validators) | Invalid DTO field type (structural dispatch default) | Y | N |
| +26 | 5026 | Error | `RelayAppender.OpenSink` | Relay resource invalid (message mode: consumer enqueuer invalid; queue mode: relay queue not obtained) | Y | N |
| +27 | 5027 | Warning | `LogManager.LaunchAppender` | Duplicate appender id ignored (ids stay unique) | Y | N |
| +28 | 5028 | Warning | `LogManager.ConfigureAppender` | Appender id not found | Y | N |
| +29 | 5029 | Warning | `Logger.ResolveLogger` | No wired instance and no process default (call is a no-op) | Y | N |
| +30 | 5030 | Error | `WaitForSnapshot` (via Initialize / RegisterAppender) | Expected Snapshot not confirmed within timeout (readiness or registration) | Y (Initialize + RegisterAppender both wired; Initialize confirmed both directions) | N |
| +31 | 5031 | - | reserved | Reserved for finer-grained register failure (to split out of 5030 later) | - | - |
| +32 | 5032 | Error | `Logger.Shutdown` (manager-stop barrier) | Manager (and nested appenders) did not stop within timeout | Y (Shutdown wired; happy path exercised by integration teardown) | N |
| +33..39 | 5033-5039 | - | reserved | Reserved for other checks | - | - |

---

## 3. Reconciliation notes (to resolve during the code review)

- **Confirm each `Impl?`** by finding where the code is actually raised in the
  VIs. The HTML report only surfaces codes mentioned in VI *descriptions*
  (5000 and the "5020-5039" range), not codes embedded in block-diagram error
  constants, so this pass has to be done against the VIs themselves.
- **`RelayModeFromString` (+13): resolved, dropped.** Confirmed no such VI, and
  none is needed: RelayMode is not read from JSON (relay appenders are created
  programmatically, Class-Reference 2.8), so there is no name-to-enum conversion
  to guard. Offset 5013 is left unused/available. Update item 33 to remove +13.
- **The "5020-5039" range** cited in the `Validate` description is looser than the
  per-offset assignments here; pin each validation code (5021-5025) to its
  specific check rather than a range, and note that 5030-5039 is reserved.
- **Codes raised but not listed:** if the code review turns up any code raised in
  a VI that isn't in the table above, add it here (that's exactly the drift this
  registry exists to catch).
- **Validation codes are shared across the `Validate*DTO` VIs.** Per-validator map
  (fill in as reviewed):
  - `ValidateAppenderConfigDTO`: 5022 (queueBound), 5024 (empty id), 5025 (invalid
    DTO type). Confirmed.
  - `ValidateFileAppenderConfigDTO`: 5025 only. Confirmed.
  - `ValidateFileConfigDTO`: 5022 (maxFileSize/maxFileCount), 5025. Confirmed.
  - `ValidateFilterDTO`: 5023 (routed level range), 5025. Confirmed.
  - `ValidateLumberjackConfigDTO`: 5025 only. Confirmed.
  - `CheckSchemaVersion`: 5021. Confirmed.

  One code, several sites is fine; just confirm every site uses the same number so
  none drifted.
- **Resolved:** the `maxFileSize`/`maxFileCount` bounded check (5022) lives in
  `ValidateFileConfigDTO` (not `ValidateFileAppenderConfigDTO`). All three bounded
  fields are covered by 5022.
- **Codes listed but not raised:** mark as planned/reserved so no one assumes
  they fire yet.
- **Source-prefix normalization (cleanup):** most raises use the `Lumberjack: `
  prefix (§1) but not all. Audit the existing fault sites and route them through
  the chokepoint helper so every source is uniform, the same kind of sweep as the
  terminal-description audit. Track to completion before submission.

---

## 4. Unit-test coverage

Goal: one test per code that deliberately triggers the fault and asserts the
specific code (via Caraya `Assert Error` on the expected code), so the fault
paths are exercised, not just the happy paths.

- Pure-VI faults (enum FromString unknown name, `IsFileNameSafe`,
  `CheckSchemaVersion`, `Validate` bounded/range/empty-id/DTO-type) are unit-tier:
  call the VI with the bad input, assert the specific code.
- Actor-path faults (`RelayAppender.OpenSink` +26, the +27/+28/+29 warnings) are
  integration-tier: drive the condition through the manager and assert the
  surfaced code.
- Fill the **Test?** column to Y as each is covered; a fully-Y table means every
  registered fault has a regression test.

---

## 5. Registered message strings

Text registered in `errors/Lumberjack-errors.txt` (shown by `General Error
Handler`). The static description carries the general text; the runtime `source`
adds the offending value after the `Lumberjack: ` prefix (§1). Drafts below for
review; `<<context>>` is the runtime value the chokepoint helper substitutes.
The static `errors/Lumberjack-errors.txt` description is this text with the
`<<context>>` clause generalized. `<...>` marks a placeholder to fill.

- **5000 (Error)** — host path required: `Lumberjack: host application path required; running as a built application with no host path supplied. Provide an explicit writable host path.`
- **5010 (Error)** — unknown Severity name: `Lumberjack: unknown Severity name "<<context>>". Expected one of OFF, FATAL, ERROR, WARN, INFO, DEBUG, TRACE, ALL.`
- **5011 (Error)** — unknown DropPolicy name: `Lumberjack: unknown DropPolicy name "<<context>>". Expected one of DropOldest, DropNewest, <level-aware member>.`
- **5012 (Error)** — unknown FilterMode name: `Lumberjack: unknown FilterMode name "<<context>>". Expected one of Mirror, Routed.`
- **5014 (Warning)** — config file not found: `Lumberjack: configuration file not found at "<<context>>"; using launch inputs (defaults). Non-fatal; a configuration file is optional.`
- **5020 (Error)** — illegal filename character: `Lumberjack: illegal filesystem character in "<<context>>". baseName and extension must not contain \ / : * ? " < > |.`
- **5021 (Error)** — unsupported schemaVersion: `Lumberjack: unsupported schemaVersion "<<context>>". Supported: <accepted set>.`
- **5022 (Error)** — bounded value invalid: `Lumberjack: bounded value <<context>> is invalid; must be -1 (unbounded) or a positive integer (0 and < -1 are not allowed).`
- **5023 (Error)** — routed level range out of order: `Lumberjack: routed level range out of order (<<context>>); levelMin must be at least as severe as levelMax.`
- **5024 (Error)** — empty appender id: `Lumberjack: appender id must not be empty.`
- **5025 (Error)** — invalid DTO field type: `Lumberjack: invalid configuration field type (<<context>>); unrecognized structure.`
- **5026 (Error)** — relay resource invalid: `Lumberjack: relay resource invalid (<<context>>); message mode requires a valid consumer enqueuer, queue mode requires an obtained relay queue.`
- **5027 (Warning)** — duplicate appender id: `Lumberjack: duplicate appender id "<<context>>" ignored; appender ids stay unique.`
- **5028 (Warning)** — appender id not found: `Lumberjack: appender id "<<context>>" not found; configure request ignored.`
- **5029 (Warning)** — no logger instance: `Lumberjack: no wired logger instance and no process default; the call is a no-op.`
- **5030 (Error)** — snapshot not confirmed: `Lumberjack: expected snapshot not confirmed within timeout (<<context>>).`
- **5032 (Error)** — manager did not stop: `Lumberjack: manager and nested appenders did not stop within the shutdown timeout.`

---

## 6. Source-prefix audit (cleanup)

Every raise site must set the error `source` with the `Lumberjack: <text>` prefix
(§1), ideally by routing through the one chokepoint helper. The runtime source is a
block-diagram constant, so this can't be verified from the HTML report, open each VI
and confirm. Tick when confirmed (or fixed); when all are ticked the §3
normalization item is resolved.

- [ ] Chokepoint helper prepends `Lumberjack: ` to every source it builds
- [ ] 5000 `ResolveHostRoot`
- [ ] 5010 `SeverityFromString`
- [ ] 5011 `DropPolicyFromString`
- [ ] 5012 `FilterModeFromString`
- [ ] 5014 `Resolve` (config file missing)
- [ ] 5020 `IsFileNameSafe`
- [ ] 5021 `CheckSchemaVersion`
- [ ] 5022 `ValidateAppenderConfigDTO`, `ValidateFileConfigDTO`
- [ ] 5023 `ValidateFilterDTO`
- [ ] 5024 `ValidateAppenderConfigDTO`
- [ ] 5025 DTO validators (invalid field type)
- [ ] 5026 `RelayAppender.OpenSink`
- [ ] 5027 `LogManager.LaunchAppender`
- [ ] 5028 `LogManager.ConfigureAppender`
- [ ] 5029 `Logger.ResolveLogger`
- [ ] 5030 `WaitForSnapshot`
- [ ] 5032 `Logger.Shutdown`
