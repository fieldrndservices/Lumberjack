# Error Code Registry: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Companion documents:** Build-Checklist (item 33), Class-Reference, Test-Strategy

**Status:** Draft, reconciliation in progress. Seeded from the Build-Checklist
item 33 plan; the "Impl?" and "Raised by (confirmed)" columns need verifying
against the actual VIs. SOP-117 review applies before this is authoritative.

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

Legend: **Impl?** = raised in code today (Y/N/?); **Test?** = exercised by a unit
test (Y/N).

---

## 2. Codes

| Offset | Code | Level | Raised by | Condition | Impl? | Test? |
|---|---|---|---|---|---|---|
| +0 | 5000 | Error | `ResolveHostRoot` | Host application path required in a built app (Application.Kind = Run Time System) | Y (in report) | N |
| +10 | 5010 | Error | `SeverityFromString` | Unknown Severity name | Y | N |
| +11 | 5011 | Error | `DropPolicyFromString` | Unknown DropPolicy name | Y | N |
| +12 | 5012 | Error | `FilterModeFromString` | Unknown FilterMode name | Y | N |
| +13 | 5013 | - | (unused) | No RelayModeFromString: RelayMode is not read from JSON (relay appenders are programmatic), so there is no name-to-enum conversion. Offset available. | - | - |
| +20 | 5020 | Error | `IsFileNameSafe` (via `Validate` / `CreateFileAppender`) | Illegal filesystem character in baseName/extension | Y | N |
| +21 | 5021 | Error | `CheckSchemaVersion` | Unsupported schemaVersion (not in accepted set) | Y | N |
| +22 | 5022 | Error | `ValidateAppenderConfigDTO` (queueBound); file validators for maxFileSize/maxFileCount | Bounded value not `-1` or positive | Y | N |
| +23 | 5023 | Error | `ValidateFilterDTO` | Routed level range out of order (levelMin/levelMax) | Y | N |
| +24 | 5024 | Error | `ValidateAppenderConfigDTO` (+ other DTO validators) | Empty appender id | Y | N |
| +25 | 5025 | Error | `ValidateAppenderConfigDTO` (+ other DTO validators) | Invalid DTO field type (structural dispatch default) | Y | N |
| +26 | 5026 | Error | `RelayAppender.OpenSink` | Relay resource invalid (message mode: consumer enqueuer invalid; queue mode: relay queue not obtained) | Y | N |
| +27 | 5027 | Warning | `LogManager.LaunchAppender` | Duplicate appender id ignored (ids stay unique) | Y | N |
| +28 | 5028 | Warning | `LogManager.ConfigureAppender` | Appender id not found | Y | N |
| +29 | 5029 | Warning | `Logger.ResolveLogger` | No wired instance and no process default (call is a no-op) | Y | N |
| +30 | 5030 | Error | `WaitForSnapshot` (via Initialize / RegisterAppender) | Expected Snapshot not confirmed within timeout (readiness or registration) | Y (Initialize + RegisterAppender both wired; Initialize confirmed both directions) | N |
| +31..39 | 5031-5039 | - | reserved | Reserved for other checks | - | - |

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
