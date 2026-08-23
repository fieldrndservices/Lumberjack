# Test ID Assert-Naming Checklist

**Purpose:** apply hierarchical `LMBR-T-###-x` Test IDs to every assert in the
built test VIs, so each assert's pass/fail surfaces under its own ID in
`tests/Test Results/LumberjackTestResults.txt` and the HTML report, while still
rolling up to the case-level Test ID that traces to the SRS (Test-Strategy §4).

**Status:** 148/148 built asserts tagged and passing (verified against the
2026-08-15 22:47 run), 0 failures, no duplicate IDs. `Path - ResolveHostRoot.vi`
(T-056/T-057/T-058) is now built and green via the injectable `app kind` seam,
so the whole pure-VI tier is complete. Remaining pure item is inspection-only:
T-059 (no self-derived paths). T-021 (ConfigReader backlog) and T-028
(resolve-once, integration) remain parked. Draft record, not a signed
verification artifact; still subject to review before it is treated
as authoritative.

**One cleanup nit remaining:** in `Relay - Message Mode.vi`, assert `-a` is
missing the space after the ID (report shows `LMBR-T-043-amsgmode-probe reached
the consumer`). Fix the name to `LMBR-T-043-a msgmode-probe reached the consumer`.

---

## How to apply (reference, for future asserts)

- Set each Caraya assert's **name** input to the full string below (the string
  Caraya writes to the report). Existing assert names are preserved; only the
  `LMBR-T-###-x` prefix is added, with a space after the suffix.
- Suffix letters are per case and run continuously even across VIs, so no two
  asserts share an ID (see T-005, which spans both JSON VIs).
- The case-level ID (before the suffix) traces to the SRS. Do not change it.
- **VI Documentation line:** each VI header below carries the line to paste into
  that VI's Documentation field (Doc-Standards §4), giving the reverse trace
  from the VI itself.

---

## Unit tier

### tests/Unit/Layout - CSV quoting.vi  (T-001, T-002, T-003 -> SRS-010, SRS-012)

VI Documentation line: `Implements LMBR-T-001, T-002, T-003 -> SRS-010, SRS-012. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-001-a CSV columns emit in order: timestamp, level, sourceTag, originVI, message`
- [x] `LMBR-T-002-a Plain field is not quoted`
- [x] `LMBR-T-002-b Embedded quote doubled and wrapped`
- [x] `LMBR-T-002-c Delimiter in field forces quoting`
- [x] `LMBR-T-002-d Newline forces quoting`
- [x] `LMBR-T-003-a Configured delimiter forces quoting`
- [x] `LMBR-T-003-b Comma not quoted when delimiter is Tab`

### tests/Unit/Layout - ISO 8601 timestamp.vi  (T-004 -> SRS-011)

VI Documentation line: `Implements LMBR-T-004 -> SRS-011. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-004-a Local instant renders its wall-clock`
- [x] `LMBR-T-004-b UTC instant formats with Z`
- [x] `LMBR-T-004-c Millisecond fraction rendered (.125)`

### tests/Unit/Layout - JSON Format.vi  (T-005 a-d -> SRS-015)

VI Documentation line: `Implements LMBR-T-005 (a-d) -> SRS-015. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-005-a Full statement emits all keys in order`
- [x] `LMBR-T-005-b Empty attributes are omitted`
- [x] `LMBR-T-005-c Message is JSON-escaped`
- [x] `LMBR-T-005-d Empty msg is still present`

### tests/Unit/Layout - JSON escape string.vi  (T-005 e-k -> SRS-015)

VI Documentation line: `Implements LMBR-T-005 (e-k) -> SRS-015. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-005-e Other control char becomes \u00xx`
- [x] `LMBR-T-005-f Newline becomes backslash-n`
- [x] `LMBR-T-005-g Backslash escaped before quote (ordering)`
- [x] `LMBR-T-005-h Plain string is just quoted`
- [x] `LMBR-T-005-i Double quote is escaped`
- [x] `LMBR-T-005-j Backslash is doubled`
- [x] `LMBR-T-005-k Empty string yields a pair of quotes`

### tests/Unit/Severity - rank compare.vi  (T-007, T-009, T-010 -> SRS-005/006)

VI Documentation line: `Implements LMBR-T-007, T-009, T-010 -> SRS-005, SRS-006. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-007-a Rank <= threshold passes (ERROR vs WARN)`
- [x] `LMBR-T-007-b Below threshold dropped (DEBUG vs INFO)`
- [x] `LMBR-T-007-c Equal-rank boundary passes (INFO vs INFO)`
- [x] `LMBR-T-009-a OFF threshold disables all (FATAL)`
- [x] `LMBR-T-010-a ALL threshold passes every level (TRACE)`

### tests/Unit/Severity - name round trip.vi  (T-008 -> SRS-005/050a; T-025 -> SRS-048)

VI Documentation line: `Implements LMBR-T-008 -> SRS-005, SRS-050a; LMBR-T-025 -> SRS-048. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-008-a Enum to name: FATAL`
- [x] `LMBR-T-008-b Enum to name: INFO`
- [x] `LMBR-T-008-c Enum to name: ALL (sentinel)`
- [x] `LMBR-T-008-d Name to enum: TRACE`
- [x] `LMBR-T-008-e Name to enum: OFF (sentinel)`
- [x] `LMBR-T-008-f Name to enum: FATAL`
- [x] `LMBR-T-025-a Unknown name faults`

### tests/Unit/Filter - tag prefix.vi  (T-016 -> SRS-027)

VI Documentation line: `Implements LMBR-T-016 -> SRS-027. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-016-a Tag shorter than prefix does not match`
- [x] `LMBR-T-016-b Exact tag matches`
- [x] `LMBR-T-016-c Sibling tag does not match (no dot boundary)`
- [x] `LMBR-T-016-d Empty prefix matches any`
- [x] `LMBR-T-016-e Child tag matches on dot boundary`

### tests/Unit/Filter - level range.vi  (T-014 -> SRS-026/027; T-015 -> SRS-026)

VI Documentation line: `Implements LMBR-T-014 -> SRS-026, SRS-027; LMBR-T-015 -> SRS-026. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-014-a In-band level with non-matching tag rejected (AND)`
- [x] `LMBR-T-014-b Level less severe than band is rejected`
- [x] `LMBR-T-014-c Level within band is accepted`
- [x] `LMBR-T-014-d Level more severe than band is rejected`
- [x] `LMBR-T-015-a Single-level band accepts that level`
- [x] `LMBR-T-015-b Single-level band rejects a more-severe level`

### tests/Unit/Source tag - defaulting.vi  (T-017, T-018 -> SRS-013, SRS-017)

VI Documentation line: `Implements LMBR-T-017, T-018 -> SRS-013, SRS-017. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-017-a "MyModule.vi" defaults to base name "MyModule" (.vi stripped)`
- [x] `LMBR-T-017-b "Logger" (no extension) returns "Logger" unchanged`
- [x] `LMBR-T-018-a "app.comms.tcp.vi" becomes single node "app_comms_tcp"`
- [x] `LMBR-T-018-b Sanitize: "a.b.c" RawTag becomes "a_b_c" CleanTag`
- [x] `LMBR-T-018-c Sanitize: dot-free "plain" is unchanged`

Note: T-019 (explicit tag verbatim) is not here — it has no pure seam and is
tracked as an integration case (SRS-013).

### tests/Unit/Retention prune.vi  (T-040, T-041 -> SRS-034)

VI Documentation line: `Implements LMBR-T-040, T-041 -> SRS-034. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-040-a Over limit selects the oldest beyond the count (5 files, max 3 -> 2 earliest)`
- [x] `LMBR-T-040-b At or under the limit selects nothing (3 files, max 3)`
- [x] `LMBR-T-040-c maxFileCount = -1 keeps all (empty selection)`
- [x] `LMBR-T-040-d Series across calendar sub-folders prunes oldest by path/timekey`
- [x] `LMBR-T-041-a Over-limit series prunes its own oldest only (app=4 + db=2, max 3)`
- [x] `LMBR-T-041-b Under-limit sibling series fully preserved (no db file selected)`

### tests/Unit/ISO 8601 filename.vi  (T-035, T-036, T-037 -> SRS-035)

VI Documentation line: `Implements LMBR-T-035, T-036, T-037 -> SRS-035. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-035-a Name embeds the ISO 8601 timestamp with colons removed`
- [x] `LMBR-T-035-b Two instants yield chronologically sortable names`
- [x] `LMBR-T-036-a Non-empty baseName yields "baseName_<timestamp>.<ext>"`
- [x] `LMBR-T-036-b Empty baseName yields timestamp-only name (no leading separator)`
- [x] `LMBR-T-037-a Extension "csv" yields exactly one dot`
- [x] `LMBR-T-037-b Extension ".csv" is normalized to one dot (not two)`
- [x] `LMBR-T-037-c Empty extension yields no trailing dot`

Note: `ISO8601FileName` returns the filename string only (confirmed); fixtures
feed known `(baseName, timestamp, extension)` and assert on the returned string.

Note: build `ExistingFiles` as synthetic Path constants (no files on disk).
Compare `FilesToDelete` as a set, or order the expected array by
(path, timekey, basename) to match PruneSelection's sort.

### tests/Unit/Config - validate.vi  (T-024, T-026, T-027 -> SRS-048, SRS-033/034/056)

VI Documentation line: `Implements LMBR-T-024, T-026, T-027 -> SRS-048, SRS-033/034/056. Assert-level IDs: Test-ID-Assert-Checklist.md.`

AppenderConfigDTO (baseline A -> ValidateAppenderConfigDTO):

- [x] `LMBR-T-026-a Valid AppenderConfigDTO validates clean, queueBound positive (baseline A)`
- [x] `LMBR-T-026-b queueBound = -1 accepted (no error)`
- [x] `LMBR-T-026-c queueBound 0 faults 5022`
- [x] `LMBR-T-026-d queueBound < -1 faults 5022`
- [x] `LMBR-T-024-a Empty appender id faults 5024`

FileConfigDTO (baseline F -> ValidateFileConfigDTO):

- [x] `LMBR-T-026-e Valid FileConfigDTO validates clean, no error (baseline F)`
- [x] `LMBR-T-026-f maxFileSize 0 faults 5022`
- [x] `LMBR-T-026-g maxFileCount 0 faults 5022`
- [x] `LMBR-T-024-c Illegal char in baseName faults 5020`
- [x] `LMBR-T-024-d Illegal char in extension faults 5020`

FilterDTO (baseline Fi -> ValidateFilterDTO):

- [x] `LMBR-T-024-e Valid routed band validates clean, levelMin at least as severe as levelMax (baseline Fi)`
- [x] `LMBR-T-024-b Routed band with levelMin less severe than levelMax faults 5023`

CheckSchemaVersion:

- [x] `LMBR-T-027-a Valid schemaVersion passes (no error)`
- [x] `LMBR-T-027-b Unknown schemaVersion faults 5021`

Note: each fault case captures and clears its expected error before the next
block (these tests generate errors on purpose) and asserts the specific
`error.code`. **Two independent baselines, one per validator, no composed
`FileAppenderConfigDTO`:** baseline A = valid `AppenderConfigDTO` via
`ValidateAppenderConfigDTO` (reused by queueBound `-026-b..d` and empty-id
`-024-a`); baseline F = valid `FileConfigDTO` via `ValidateFileConfigDTO` (reused by
the file bounds `-026-f`/`-026-g` and filename `-024-c`/`-024-d`). Each fault mutates
exactly one field of its baseline, so the fault is attributable to that field,
which is what makes the shared 5022 (and shared 5020) meaningful. baseline Fi = valid routed
`FilterDTO` via `ValidateFilterDTO` (`-024-e`), mutated to a reversed band for
`-024-b`. Level-range convention: `levelMin` is the most-severe bound (lower rank),
valid when `rank(levelMin) <= rank(levelMax)` (equal = single-level, valid); out of
order is strictly `rank(levelMin) > rank(levelMax)`, using valid severity names
(e.g. `levelMin`=DEBUG / `levelMax`=INFO) so the fault is 5023, not 5010. `-027`
uses `CheckSchemaVersion` directly. DTO field
types: `schemaVersion`/`id` strings, `queueBound`/`maxFileSize`/`maxFileCount`
numeric. Confirm the 5020 raise site: if `ValidateFileConfigDTO` does not run the
filename-safety check, point `-024-c`/`-024-d` at `IsFileNameSafe.vi` directly.

### tests/Unit/Config - resolve.vi  (T-020, T-022, T-023 -> SRS-044/047/048)

VI Documentation line: `Implements LMBR-T-020, T-022, T-023 -> SRS-044, SRS-047, SRS-048. Assert-level IDs: Test-ID-Assert-Checklist.md.`

Resolve (Resolve.vi):

- [x] `LMBR-T-020-a No config path: effective config equals the baseline inputs`
- [x] `LMBR-T-022-a Defined but missing path is non-fatal (status FALSE)`
- [x] `LMBR-T-022-b Missing path falls back to the baseline`
- [x] `LMBR-T-022-c Missing-path warning carries code 5014`
- [x] `LMBR-T-022-d Missing-path warning source names the missing path`
- [x] `LMBR-T-023-a Unparseable JSON file fails launch (status TRUE), no fallback`
- [x] `LMBR-T-023-b Unsupported schemaVersion file fails launch (status TRUE, 5021)`

Note: `-020`/`-022` need no files (empty path / a non-existent path); `-023` needs
real temp files (malformed JSON and schema-invalid JSON) via the temp-root fixture
(`Setup - create temp root` / `Tear Down - delete root temp`). Load-bearing claim is
warning vs fatal: `-022` is status FALSE (non-fatal, SRS-047), `-023` is status TRUE
(fatal, SRS-048). The missing-file warning and JSON-parse-failure codes are not in
Error-Codes.md, assert status FALSE/TRUE (+ non-zero for the warning), not a specific
50xx code, and flag those two for the registry. Capture and clear each expected
error. Confirm `Resolve.vi` terminals. T-028 (resolve-once) deferred to integration.
`-023-a` is a JSON **syntax** error (parse failure, native/LabVIEW code); `-023-b`
is valid JSON with an **unsupported `schemaVersion`** (out-of-set), failing at
`CheckSchemaVersion` with 5021, present-but-bad content, not a missing field
(default-fill can make a missing key pass validation).

**T-021 (JSON per-key merge, SRS-046) deferred to the ConfigReader backlog:** the
current `Merge` does a full-object overwrite (an empty value clobbers the baseline
rather than falling back), so partial-file / per-key precedence is not yet
achievable, it needs the presence mask (two-default diff). To be covered by a future
`Config - merge.vi` when that lands.

### tests/Unit/Enum - DropPolicy and FilterMode.vi  (T-060 -> SRS-050a; T-025 -> SRS-048)

VI Documentation line: `Implements LMBR-T-060 -> SRS-050a; LMBR-T-025 (DropPolicy, FilterMode) -> SRS-048. Assert-level IDs: Test-ID-Assert-Checklist.md.`

Round trip (FromString -> String, assert original name):

- [x] `LMBR-T-060-a DropPolicy "DropOldest" round-trips`
- [x] `LMBR-T-060-b DropPolicy "DropNewest" round-trips`
- [x] `LMBR-T-060-c DropPolicy level-aware member round-trips`
- [x] `LMBR-T-060-d FilterMode "Mirror" round-trips`
- [x] `LMBR-T-060-e FilterMode "Routed" round-trips`
- [x] `LMBR-T-060-f DropPolicy round-trips complete with no error (guards DropOldest ordinal-0 false pass)`
- [x] `LMBR-T-060-g FilterMode round-trips complete with no error (guards Mirror ordinal-0 false pass)`

Unknown name faults (capture and clear):

- [x] `LMBR-T-025-b DropPolicyFromString unknown name faults 5011`
- [x] `LMBR-T-025-c FilterModeFromString unknown name faults 5012`
- [x] `LMBR-T-025-d DropPolicy unknown-name source names the offending value and lists the accepted set`
- [x] `LMBR-T-025-e FilterMode unknown-name source names the offending value and lists the accepted set`

Note: round-trip form (name -> FromString -> String -> name) exercises both the
width-fixed FromString and the String direction in one assert, guarding the
I32-vs-U16 ordinal-0 bug. Confirm the DropPolicy level-aware member name for `-060-c`.
The **non-default** members (`DropNewest`, level-aware, `Routed`) are the real
catchers: their expected value differs from the ordinal-0 default, so a wrong value
or a silent error that leaves the default output both mismatch and fail. The
ordinal-0 members (`-060-a` DropOldest, `-060-d` Mirror) are vacuous on their own,
their expected value equals the default/failure output, so a no-error guard makes
them trustworthy by catching the error-skip-leaves-default case. One guard per enum
group, since the two ordinal-0 members sit in separate groups: `-060-f` DropPolicy
valid round-trips with no error (guards DropOldest), `-060-g` FilterMode valid
round-trips with no error (guards Mirror). Each sits on its group's error wire,
after that group's ordinal-0 round-trip.
T-025 spans two VIs (Severity - name round trip holds `-a`; these add `-b`..`-e`),
continuous suffixes. `-025-d`/`-025-e` are the context asserts: the fault source must
name the offending value and list the accepted set (T-025 "with the accepted set
listed", SRS-048). Check the source contains the bad name passed in and a known
valid member; if the runtime source shows the literal `<<context>>` placeholder
instead of the value, the token substitution isn't firing (fix at the chokepoint
helper) and these asserts correctly fail. Per Doc-Standards §4 the per-assert input
table lives in this VI's Block Diagram description.

### tests/Unit/Config - DTO round trip.vi  (T-061 -> SRS-050a)

VI Documentation line: `Implements LMBR-T-061 -> SRS-050a. Assert-level IDs: Test-ID-Assert-Checklist.md.`

Round trip (native -> FromNative -> DTO -> FromDTO -> native, assert equals original):

- [x] `LMBR-T-061-a FilterDTO round-trips (native == round-tripped)`
- [x] `LMBR-T-061-b AppenderConfigDTO round-trips`
- [x] `LMBR-T-061-c FileConfigDTO round-trips`
- [x] `LMBR-T-061-d FileAppenderConfigDTO round-trips`
- [x] `LMBR-T-061-e LumberjackConfigDTO round-trips`

Note: build each native cluster with distinctive non-default values (the T-020
baseline set) so a dropped/defaulted field mismatches. Because the expected value is
never the default, the value comparison alone catches drops and silent errors, no
ordinal-0-style coincidence, so no separate no-error guard is needed here. The
round-trip exercises the enum mappers (DropPolicy/FilterMode/Severity) and
Path<->String in situ; use canonical path values (absolute, no trailing slash) to
avoid Path/String normalization false-mismatches. Composite pairs (`-d`,`-e`) overlap
the leaves (`-a`/`-b`/`-c`) but isolate which mapper drops a field. Confirm mapper
terminal names. Per Doc-Standards §4 the per-assert input table lives in the Block
Diagram description.

### tests/Unit/Layout - UTC frame agreement.vi  (T-038 -> SRS-011/035/036)  — BUILT

VI Documentation line: `Implements LMBR-T-038 -> SRS-011, SRS-035, SRS-036. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-038-a Filename date matches layout timestamp date (useUTC=TRUE)`
- [x] `LMBR-T-038-b Calendar folder date matches layout timestamp date (useUTC=TRUE)`
- [x] `LMBR-T-038-c Filename date matches layout timestamp date (useUTC=FALSE)`
- [x] `LMBR-T-038-d Calendar folder date matches layout timestamp date (useUTC=FALSE)`

Note: three renderings from one instant, `FormatTimeString` (layout line), `ISO8601FileName`
(filename), `BaseFolder` (calendar folder, `calendarFolderTree=TRUE`); reduce each to
`YYYYMMDD` and compare filename and folder to the layout timestamp as the reference frame
(the layout frame is anchored by T-004). Two comparisons per useUTC lane, kept as separate
asserts (not one AND-ed "all three agree") so a failure names which rendering drifts.
Use a boundary instant near UTC midnight so UTC != local and a frame mismatch is
observable; on a UTC-set machine local == UTC so the lanes can't distinguish frames
(asserts still pass when correct). Confirm `FormatTimeString` / `ISO8601FileName` /
`BaseFolder` terminals (timestamp, useUTC; BaseFolder also rootFolder + calendarFolderTree).

### tests/Unit/Path - ResolveHostRoot.vi  (T-056, T-057, T-058 -> SRS-064/039)  — BUILT

VI Documentation line: `Implements LMBR-T-056, T-057, T-058 -> SRS-064, SRS-039. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-056-a Explicit host path is returned verbatim`
- [x] `LMBR-T-057-a Empty host path (dev system) resolves to Application Directory, not the library path`
- [x] `LMBR-T-058-a Built-app (RTS) with no host path faults with error 5000`
- [x] `LMBR-T-058-b Explicit path wins over RTS fault (returned verbatim, no error)`
- [x] `LMBR-T-058-c Resolved root is Not A Path when the 5000 fault is raised`

Decision (Draft): T-058 is made testable from the IDE by adding an
injectable `app kind` input to `ResolveHostRoot`, typedef enum `HostAppKind`
{`Auto`(0), `DevelopmentSystem`, `RunTimeSystem`}, default `Auto`. `Auto` reads
the real `Application.Kind` so existing (unwired) callers are unchanged; the test
wires `RunTimeSystem` to force the built-app branch. Decision order in the VI is
unchanged: explicit host path wins first, then RTS -> 5000, else Application
Directory. `-058-a` forces the fault; `-058-b` pins the precedence (explicit path
beats the RTS fault); `-058-c` pins the fail-closed contract (resolved root is Not
A Path on the 5000 fault, never the executable folder). `RunTimeSystem` is a distinctive non-default (Auto is
ordinal 0), so an unwired terminal cannot false-pass. SRS-064 still holds:
external-path computation stays isolated in this one VI and `app kind` is not a
path. T-059 (no self-derived paths) is an inspection item recorded in
`docs/Path-Derivation-Audit.md` (automated scan done, manual diagram ticks
pending); not a Caraya assert.

---

## Integration tier

### tests/Integration/Backpressure - unbounded no loss.vi  (T-046 -> SRS-055)  — BUILT

VI Documentation line: `Implements LMBR-T-046 -> SRS-055. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-046-a drained count = 100 (unbounded queue lost nothing)`
- [x] `LMBR-T-046-b first dequeued message = "u-000" (FIFO start)`
- [x] `LMBR-T-046-c last dequeued message = "u-099" (FIFO end; all present, in order)`

Note: copy T-044. Relay A queue mode, mirror, threshold ALL, queueBound -1 (unbounded).
enableDefaultFile FALSE, global ALL. For Loop x100 Log INFO `"u-000".."u-099"` (zero-
padded, sourceTag UNB), sequenced. Drain the exposed queue (loop dequeue w/ timeout,
count + capture first/last) until empty. `-046-a` count==100 (no loss), `-046-b` first
== u-000, `-046-c` last == u-099 (FIFO across the burst). Contrast to the bounded drop
tests (T-047+) where a full queue sheds by policy.

VI Documentation line: `Implements LMBR-T-044 -> SRS-025. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-044-a exposed queue 1st dequeue message = "qm-1"`
- [x] `LMBR-T-044-b exposed queue 2nd dequeue message = "qm-2"`
- [x] `LMBR-T-044-c exposed queue 3rd dequeue message = "qm-3"`
- [x] `LMBR-T-044-d exposed queue 4th dequeue times out (held exactly three, FIFO)`

Note: relay A queue mode, mirror, threshold ALL, queueBound -1 (unbounded). enable
DefaultFile FALSE, global ALL. Log `"qm-1"/"qm-2"/"qm-3"` (sourceTag QM) in order,
dequeue the exposed queue: a/b/c FIFO delivery, d empty-after (exactly three, no loss).
Direct SRS-025 test (the queue mode every relay probe uses).

BACKPRESSURE CLUSTER NOTE: drop-policy logic (T-047/048/049, SRS-057) was extracted
into the pure helper `src/Support/Backpressure/ApplyBackPressure.vi`
(`pending`, `incoming`, `queueBound`, `DropPolicy`, `worstSeverityIn` ->
`result`, `dropped`, `droppedStatement`, `worstSeverityOut`), so these are true U-tier
unit tests: build inputs, call the VI, assert outputs, no actors and no timing. The
`LevelAware` member and the memoized-floor fast-path are exercised directly, incl. the
-049-e oracle (fast-path vs forced scan). T-050 (no-blocking) / T-051 (drop notice)
still need a controlled integration overflow; approach TBD when we reach them.

### tests/Unit/Backpressure - drop-oldest.vi  (T-047 -> SRS-057)  — BUILT

VI Documentation line: `Implements LMBR-T-047 -> SRS-057. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-047-a dropped is TRUE`
- [x] `LMBR-T-047-b oldest is the dropped one (droppedStatement.message = "A")`
- [x] `LMBR-T-047-c bound preserved (result size = queueBound)`
- [x] `LMBR-T-047-d newest admitted at tail (result[2].message = "D")`
- [x] `LMBR-T-047-e ring shifted, second-oldest now head (result[0].message = "B")`
- [x] `LMBR-T-047-f room means append, no drop (dropped FALSE)`
- [x] `LMBR-T-047-g appended at tail (result size = 4, result[3].message = "D")`

Note: `DropPolicy = DropOldest`. Full case: `pending = ["A","B","C"]` (A oldest),
distinct non-default severities, `queueBound = 3`, `incoming = "D"`, `worstSeverityIn`
unused (OFF). Room case: same `pending`, `queueBound = 5`. Compare by `message`.
Room/append test is strict: append iff `queueBound < 0 OR pending size < queueBound`.

### tests/Unit/Backpressure - drop-newest.vi  (T-048 -> SRS-057)  — BUILT

VI Documentation line: `Implements LMBR-T-048 -> SRS-057. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-048-a dropped is TRUE`
- [x] `LMBR-T-048-b incoming is the dropped one (droppedStatement.message = "D")`
- [x] `LMBR-T-048-c buffer unchanged (result size = queueBound)`
- [x] `LMBR-T-048-d head preserved (result[0].message = "A")`
- [x] `LMBR-T-048-e tail preserved (result[2].message = "C")`
- [x] `LMBR-T-048-f room means append, no drop (dropped FALSE)`
- [x] `LMBR-T-048-g appended at tail (result size = 4, result[3].message = "D")`

Note: `DropPolicy = DropNewest`. Full case identical setup to T-047; drop-newest
rejects `incoming`, leaving `pending` intact. Room case appends as usual.

### tests/Unit/Backpressure - level-aware.vi  (T-049 -> SRS-057)  — BUILT

VI Documentation line: `Implements LMBR-T-049 -> SRS-057. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-049-a scenario A: oldest least-severe queued is the victim (droppedStatement.message = "d1")`
- [x] `LMBR-T-049-b scenario A: incoming admitted at tail (result[3].message = "i")`
- [x] `LMBR-T-049-c scenario A: bound preserved (Array Size(result) = 4)`
- [x] `LMBR-T-049-d scenario A: floor recomputed (worstSeverityOut = DEBUG)`
- [x] `LMBR-T-049-e scenario B: incoming at/below floor is dropped (droppedStatement.message = "t")`
- [x] `LMBR-T-049-f scenario B: buffer tail unchanged (result[3].message = "d2")`
- [x] `LMBR-T-049-g scenario B: buffer size unchanged (Array Size(result) = 4)`
- [x] `LMBR-T-049-h scenario C: all-protected, incoming dropped (droppedStatement.message = "f2")`
- [x] `LMBR-T-049-i scenario C: protected head intact (result[0].message = "f")`
- [x] `LMBR-T-049-j scenario C: buffer size unchanged (Array Size(result) = 3)`
- [x] `LMBR-T-049-k scenario D: non-protected is the victim, not the older ERROR (droppedStatement.message = "d")`
- [x] `LMBR-T-049-l scenario D: protected ERROR retained (result[0].message = "e")`
- [x] `LMBR-T-049-m oracle B: result sequence equal (fast-path = forced scan)`
- [x] `LMBR-T-049-n oracle B: droppedStatement.message equal (fast-path = forced scan)`
- [x] `LMBR-T-049-o oracle B: worstSeverityOut equal (fast-path = forced scan)`
- [x] `LMBR-T-049-p oracle tie: result sequence equal (fast-path = forced scan)`
- [x] `LMBR-T-049-q oracle tie: droppedStatement.message equal (fast-path = forced scan)`
- [x] `LMBR-T-049-r oracle tie: worstSeverityOut equal (fast-path = forced scan)`

Scenarios (DropPolicy = LevelAware; severity from `Statement.level`; protected =
`level <= ERROR`; floor = `TRACE`; tie-break: incoming loses ties, Design 5.7):
A `bufAD=[e:ERROR,d1:DEBUG,w:WARN,d2:DEBUG]` qb4 wSevIn=DEBUG incoming=i:INFO (a-d);
B same buf, incoming=t:TRACE, fast-path (e-g); C `[f:FATAL,e1:ERROR,e2:ERROR]` qb3
wSevIn=ERROR incoming=f2:FATAL (h-j); D `[e:ERROR,d:DEBUG]` qb2 wSevIn=DEBUG incoming=w:WARN
(k,l). Oracle (m-r): each vector is run twice, correct wSevIn vs `OFF`, and the three
outputs compared field-by-field (one assert each, no combined criteria). m-o = vector B
(below floor); p-r = tie vector `[td1:DEBUG,tw:WARN,td2:DEBUG]` qb3 incoming=td3:DEBUG
(qb must equal the buffer size so it is full and the tie engages). The
oracle is the V&V evidence the fast-path does not change SRS-057 behavior. One claim per
assert throughout.

### tests/Unit/Backpressure - no blocking.vi  (T-050 -> SRS-058)  — BUILT

VI Documentation line: `Implements LMBR-T-050 -> SRS-058. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-050-a sustained overflow never grows the buffer (Array Size(result) = queueBound every iteration)`
- [x] `LMBR-T-050-b every admission drops immediately (dropped? TRUE every iteration)`

Note: pure against `ApplyBackPressure`. `pending` full = `["s0","s1","s2"]`, `queueBound = 3`,
`DropPolicy = DropOldest`, `worstSeverityIn = OFF`. Loop N=10 admitting a new `incoming`,
feed `result` back as `pending`, AND-accumulate `(dropped? AND size==queueBound)`.
Demonstrates SRS-058: admission is synchronous and bounded (no wait, no growth), so the
caller never needs to block.

### tests/Unit/Backpressure - drop notice.vi  (T-051 -> SRS-059)  — a-d BUILT; -e (emission integration) pending

VI Documentation line: `Implements LMBR-T-051 -> SRS-059. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-051-a count rendered (BuildDropNotice(5).message = "dropped statement count = 5")`
- [x] `LMBR-T-051-b protected severity (level = ERROR)`
- [x] `LMBR-T-051-c reserved tag (sourceTag = "lumberjack.dropped")`
- [x] `LMBR-T-051-d count rendered for N=1 (message = "dropped statement count = 1")`
- [ ] `LMBR-T-051-e (integration) bounded appender that dropped emits a record with sourceTag "lumberjack.dropped"`

Note: needs a new pure VI `BuildDropNotice` (`src/Support/Backpressure`, `droppedCount ->
Statement`), extracted from `Actor Core` like `ApplyBackPressure`. Format: `message =
"dropped statement count = <N>"`, `level = ERROR` (protected, so level-aware never sheds
the notice), `sourceTag = "lumberjack.dropped"` (reserved `lumberjack.*` namespace).
`Actor Core` emits the notice **straight to the sink, bypassing `ApplyBackPressure`**, so
drop-oldest/newest can't discard it either. a-d are pure; -e is the one integration check.

### tests/Integration/Shutdown - flush.vi  (T-052 -> SRS-002)  — BUILT

VI Documentation line: `Implements LMBR-T-052 -> SRS-002. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-052-a all queued statements flushed (line count = 50)`
- [x] `LMBR-T-052-b FIFO start (first line contains "flush-01")`
- [x] `LMBR-T-052-c flushed through the last (last line contains "flush-50")`

Note: integration, validates the flush fence. Arrange: temp root; `Initialize` (global
ALL, `enableDefaultFile = FALSE`); `Register File Appender` (id "FA", threshold ALL,
**unbounded** `queueBound = -1`, temp root). Act: `Log` "flush-01".."flush-50" (sourceTag
FLUSH, INFO), then `Logger.Shutdown` (synchronous). Assert via `Read Log Lines`. Unbounded
= flush test, not drop. The fence writes all queued statements before flush/close/stop, so
`count = 50` proves no loss to a premature stop. `Clear Errors` at the test start (serial
isolation).

### tests/Integration/Shutdown - on error.vi  (T-053 -> SRS-004)  — BUILT

VI Documentation line: `Implements LMBR-T-053 -> SRS-004. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-053-a flush ran despite incoming error (line count = 50)`
- [x] `LMBR-T-053-b drain reached the last statement (last line contains "eflush-50")`
- [x] `LMBR-T-053-c incoming error preserved on error out (code 42)`

Note: integration, validates error-tolerant teardown. Arrange as T-052 (temp root;
`Initialize` global ALL, no default file; `Register File Appender` id "FA", threshold ALL,
unbounded, temp root; `Clear Errors` at top). Act: `Log` "eflush-01".."eflush-50" (sourceTag
EFLUSH, INFO); build a manufactured error (status TRUE, code 42, source "T-053 injected")
and wire it into **`Logger.Shutdown`'s `error in`**, called **directly** (not via
`Close test manager`, so we test Shutdown's own error handling). Branch `Shutdown`'s
`error out`: read `code` for `-053-c`, then **`Clear Errors`** before `Read Log Lines` /
asserts / `Delete Temp Root` (else the injected error gates the reads and marks the test
errored). If `-053-a` fails, `Shutdown` is error-gating its fence; fix = clear/branch the
incoming error so the shutdown sequence runs, then re-merge it into `error out`. Built:
the `Clear Errors` after `-053-c` is scoped to the injected code so isolation is
order-independent (does not ride the serial chain).

### tests/Integration/CatchError - log.vi  (T-054 -> SRS-041)  — BUILT

VI Documentation line: `Implements LMBR-T-054 -> SRS-041. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-054-a CatchError logged one statement (relay probe received a message)`
- [x] `LMBR-T-054-b logged message contains the caught error source ("T-054 injected")`
- [x] `LMBR-T-054-c level = ERROR`
- [x] `LMBR-T-054-d sourceTag begins with reserved "lumberjack."`
- [x] `LMBR-T-054-e CatchError error out cleared: status FALSE`
- [x] `LMBR-T-054-f CatchError error out cleared: code 0`
- [x] `LMBR-T-054-g dequeuer times out (exactly one statement logged)`

Note: integration. Arrange `Open Test Mgr` (enableDefaultFile FALSE) -> logger;
`Register Relay Appender` (id "cerr", Mirror, threshold ALL) -> capture queue;
`ConfigureVerbosity(OFF)` so GEH shows no dialog (log is independent of display,
SRS-042); `Clear Errors` at top. Act: manufactured error (status TRUE, code 42, source
"T-054 injected") through `Logger.CatchError`. Assert the captured Statement (`-a..-d`),
CatchError `error out` (`-e/-f`), and a second timed dequeue (`-g`). Teardown
`Close Test Mgr` + `Release Relay Queues`. `-d` checks the reserved `lumberjack.`
prefix (stable contract); tighten to an exact literal if CatchError stamps a fixed tag.

### tests/Unit/Verbosity - dialog gate.vi  (T-055 -> SRS-042)  — BUILT

VI Documentation line: `Implements LMBR-T-055 -> SRS-042. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-055-a verbosity ERROR, error FATAL -> dialogType 1 (shown, above threshold)`
- [x] `LMBR-T-055-b verbosity ERROR, error ERROR -> dialogType 1 (shown, at boundary, inclusive)`
- [x] `LMBR-T-055-c verbosity ERROR, error WARN  -> dialogType 0 (suppressed, below)`
- [x] `LMBR-T-055-d verbosity OFF,   error ERROR -> dialogType 0 (verbosity OFF suppresses all)`
- [x] `LMBR-T-055-e verbosity ALL,   error ERROR -> dialogType 1 (verbosity ALL shows all)`

Note: unit; pure `ShouldDisplay(errorSeverity, verbosity) -> dialogType` via `RankCompare`
(shown iff rank(errorSeverity) <= rank(verbosity)). Grid covers boundary (`-b`, inclusive),
above (`-a`), below (`-c`), and the OFF/ALL extremes. Assert the I32 `dialogType`, not a
boolean, so the 0/1 GEH mapping is covered.

VI Documentation line: `Implements LMBR-T-006 -> SRS-010, SRS-013. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-006-a delivered sourceTag = "app.comms.tcp" (explicit logical tag)`
- [x] `LMBR-T-006-b delivered originVI contains this VI's name (physical origin)`
- [x] `LMBR-T-006-c delivered originVI != sourceTag (distinct fields)`

Note: copy T-019 (single relay probe, explicit tag). enableDefaultFile FALSE, global
ALL, relay A queue/mirror/ALL. Capture This VI's Path -> name (thisVIName). Log INFO
`"fields-1"` with explicit sourceTag `"app.comms.tcp"` DIRECTLY on this VI's diagram
(so originVI = this test VI). Drain relayA, unbundle the Statement: `-006-a` sourceTag
verbatim, `-006-b` originVI CONTAINS thisVIName (substring, rename-safe, tolerant of
.vi suffix), `-006-c` originVI != sourceTag (proves they're separate fields, not one).
Distinct-when-explicit case; default-tag (sourceTag == originVI base name, SRS-013) is
the unit source-tag test.

VI Documentation line: `Implements LMBR-T-042 -> SRS-036. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-042-a log file is placed in a sub-folder of root (calendar folder created)`
- [x] `LMBR-T-042-b calendar folder date matches the file-name date (YYYYMMDD)`
- [x] `LMBR-T-042-c file contains "cal-1" (logging works through the calendar path)`

Note: copy T-034, one file appender FA (id fileCal, root, threshold ALL, mirror,
CSVLayout, calendarFolderTree TRUE, maxFileSize -1 no rollover, maxFileCount -1).
enableDefaultFile FALSE, global ALL. Log INFO `"cal-1"` (sourceTag CAL). Close (flush
fence) BEFORE List/Read. `-042-a` Strip Path(file) != root (a dated sub-folder exists;
contrast T-034/T-039 which used calendarFolderTree FALSE -> file directly in root).
`-042-b` reduce the sub-path (root+filename stripped) to digits and assert it contains
the YYYYMMDD extracted from the file NAME's ISO timestamp -- format-agnostic
(YYYY/MM/DD or YYYY-MM-DD) and midnight-safe (expected derived from the same instant,
per SRS-036 folder/name agreement). `-042-c` Read Log Lines has "cal-1". Tear Down must
recursively delete the nested folders. Integration counterpart to unit T-038.

VI Documentation line: `Implements LMBR-T-039 -> SRS-033. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-039-a size rollover produced more than one file`
- [x] `LMBR-T-039-b total lines across all files = 3 (no statement lost across rolls)`
- [x] `LMBR-T-039-c newest file contains "roll-03"`

NAME FIX PENDING: the built `-039-b` assert is still labeled "= 20" (stale from the
fast-version design) though it logs/asserts 3; rename it in the VI to "= 3" so the
report matches. Passes 4/4 individual runs + suite; hardened spaced-rollover design.

Note: SPACED-ROLLOVER design. Rolled file names are second-resolution ISO8601
timestamps, opened create-only, so two rollovers in the same second collide and fault
BY DESIGN (Design.md 5.5) -- a small maxFileSize + rapid logging (the old 20-fast-line
version) rolls sub-second and fails intermittently (passes only under highlight). So
force one roll per write but SPACE the writes across seconds: one file appender FA (id
fileR, root, threshold ALL, mirror, CSVLayout, calendarFolderTree FALSE, maxFileCount
-1, maxFileSize COMFORTABLY above one full line but below two, so roll-1 fits file A
WITHOUT rolling (no roll in the registration second) and roll-2/roll-3 each roll; pad
the message to a fixed width or measure a one-line file so the value is deterministic).
enableDefaultFile FALSE, global ALL. Log `"roll-1"`, Wait 2000 ms, `"roll-2"`, Wait
2000 ms, `"roll-3"` (sourceTag ROLL) -- the Waits MUST be strictly sequenced between
the Logs (error/logger wire or flat sequence) so each roll lands in a distinct second;
2 s margin swamps async/startup jitter. Close (flush fence) BEFORE List/Read. `-039-a`
count>=2 (loose: tolerates empty-first-file), `-039-b` total rows == 3 (no loss across
rolls), `-039-c` newest file (paths[last]) has roll-3. Depends on both the flush fence
and the currentFileSize increment fix. FUTURE ENHANCEMENT (PR-Notes 4): add a filename
sequence disambiguator so sub-second rollover is collision-proof, which would let this
revert to the simple fast (no-wait) version.

VI Documentation line: `Implements LMBR-T-034 -> SRS-032, SRS-039, SRS-040. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-034-a rootA produced exactly one log file`
- [x] `LMBR-T-034-b rootB produced exactly one log file`
- [x] `LMBR-T-034-c rootA file contains "line-info" (FA-A threshold ALL)`
- [x] `LMBR-T-034-d rootB file does not contain "line-info" (FA-B threshold WARN; no cross-contamination)`
- [x] `LMBR-T-034-e rootB file contains "line-warn"`

Note: first file-mechanics test; file fixture not relay probes. Two `Setup - create
temp root` -> rootA, rootB. `enableDefaultFile = FALSE`, `global threshold = ALL`.
Two `Register File Appender` from default FileAppenderConfig: FA-A (id fileA, root
rootA, threshold ALL, filter.mode Mirror, calendarFolderTree FALSE); FA-B (id
fileB, root rootB, threshold WARN, filter.mode Mirror, calendarFolderTree FALSE).
Set `maxFileSize = -1` and `maxFileCount = -1` on both (unbounded / keep-all) so
rollover is out of the picture; bad bounds (0) make the write path gate every write
and produce a 0-byte file (the native-config Register path bypasses 5022
validation). Match `List Log Files` extension to the config extension `"csv"` (no
dot). Log INFO `"line-info"` then WARN `"line-warn"`. MUST `Close test manager` (Shutdown flush/close) BEFORE `List Log
Files`/`Read Log Lines`. `-034-c`+`-034-d` are the root-isolation + independent-
threshold pair (INFO in A, absent from B). Two `Tear Down - delete root temp`.

VI Documentation line: `Implements LMBR-T-033 -> SRS-021. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-033-a relayA first delivered message = "iso-before" (both appenders healthy pre-fault)`
- [x] `LMBR-T-033-b relayA second delivered message = "iso-after" (delivery to healthy appender continues after B stopped)`
- [x] `LMBR-T-033-c Log("iso-after") returned within bound (caller not blocked by the faulted appender)`
- [x] `LMBR-T-033-d Log("iso-after") error out clean (fault not propagated to the caller)`

Verified against the user-reported 170-pass run; assert-text reconciliation and the
0-fail / no-dup grep to be re-confirmed when the results file re-syncs from OneDrive.

Note: new test-support VI `Stop Appender By Id.vi` (in Tests.lvlib, friend of
Lumberjack) reads B's `Message Enqueuer` from the `Snapshot` (RegistryEntry
{id, enqueuer}) and sends AF `Send Normal Stop`; B stays in the manager registry, so
the manager still broadcasts to a dead enqueuer. No production code change. Two relays
A/B (queue, mirror, ALL), `enableDefaultFile = FALSE`, `global threshold = ALL`. Log
`"iso-before"`, stop B, then log `"iso-after"` wrapped in Tick Count (elapsed) and
capture `error out`. `-033-b` is the isolation claim; `-033-c`/`-033-d` cover
caller-not-blocked (time + no error propagation). Log `"iso-after"` immediately after
the stop to bias toward broadcasting while B's dead enqueuer is still registered. This
stresses the manager broadcast loop; if it doesn't tolerate a per-appender enqueue
error, T-033 fails and surfaces a real SRS-021 defect. 500 ms bound is generous to
avoid flakiness.

VI Documentation line: `Implements LMBR-T-031 -> SRS-020, SRS-028. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-031-a relayA first delivered message = "reg-before" (baseline active before B existed)`
- [x] `LMBR-T-031-b relayA second delivered message = "reg-after" (A still receiving, SRS-028)`
- [x] `LMBR-T-031-c relayB first delivered message = "reg-after" (newly registered appender begins receiving)`
- [x] `LMBR-T-031-d relayB second dequeue times out (B did not retroactively receive "reg-before")`

Note: copy T-032 (unregister) run forward. `Open test manager` enableDefaultFile
FALSE, global ALL. Register A (baseline), log `"reg-before"`, then register B at
runtime and WAIT on the `IDPresent "relayB"` snapshot barrier before logging
`"reg-after"` (removes the registration race). `-031-c`/`-031-d` are the core claim:
B receives the post-registration statement and only that one. `-031-a`/`-031-b`
prove A is a live baseline throughout so a B failure isn't a dead manager.

VI Documentation line: `Implements LMBR-T-019 -> SRS-013. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-019-a relayA delivered message = "tag-explicit"`
- [x] `LMBR-T-019-b relayA delivered sourceTag = "app.comms.tcp" (explicit tag used verbatim)`

Note: copy T-029 (single-appender delivery). One relay `A`, mirror/ALL, `global
threshold = ALL`, `enableDefaultFile = FALSE`. Log INFO `"tag-explicit"` with the
`sourceTag` input explicitly wired to `"app.comms.tcp"`. The tag is hierarchical and
not the origin VI base name, so `-019-b` proves the supplied tag flows through
verbatim (dots preserved, not sanitized or regenerated); the default-tag path is
covered by the unit test. `-019-a` guards that `-019-b` reads a real delivered
element. Separate asserts (no AND) so "not delivered" vs "wrong tag" are distinct.

VI Documentation line: `Implements LMBR-T-013 -> SRS-026. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-013-a relayA first delivered message = "mir-error"`
- [x] `LMBR-T-013-b relayA second delivered message = "mir-warn"`
- [x] `LMBR-T-013-c relayA third dequeue timed out (below-threshold INFO dropped; mirror honors threshold)`

Note: one relay `A`, `FilterMode = Mirror`, `threshold = WARN`; `global threshold =
ALL` so stage-1 never interferes; `enableDefaultFile = FALSE`. Log across different
tags and passing levels to prove mirror is tag/band-agnostic (distinct from T-012's
threshold test): ERROR `"mir-error"`/app.alpha, WARN `"mir-warn"`/sys.beta (both
pass), then INFO `"mir-info"`/net.gamma (below WARN, dropped). `-013-c` asserts the
Dequeue `timed out?` boolean, pinning the "accepts everything *above threshold*"
clause of mirror mode.

### tests/Integration/Filtering - global gate.vi  (T-011 -> SRS-007)  — BUILT

VI Documentation line: `Implements LMBR-T-011 -> SRS-007. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-011-a relayA first delivered message = "glob-warn"`
- [x] `LMBR-T-011-b relayA second dequeue timed out (INFO blocked at stage 1; relayA received exactly one)`
- [x] `LMBR-T-011-c relayB first delivered message = "glob-warn"`
- [x] `LMBR-T-011-d relayB second dequeue timed out (INFO blocked at stage 1; relayB received exactly one)`

Note: copy the T-012 two-relay fixture; both relays `mode = mirror`, `threshold =
ALL` (open, so the global gate is the only discriminator). Set `global threshold =
WARN` at Initialize. Log WARN `"glob-warn"` then INFO `"glob-info"` (sourceTag
`"GLB"`). `-011-b`/`-011-d` are the defining claim: the INFO fails the caller-side
gate and reaches no appender (proven across both channels), which distinguishes a
global gate from the per-appender threshold. Relabel all four IDs immediately after
copying, and set thresholds to ALL (not INFO/WARN) so this is not a re-test of T-012.

### tests/Integration/Filtering - per-appender threshold.vi  (T-012 -> SRS-009)  — BUILT

VI Documentation line: `Implements LMBR-T-012 -> SRS-009. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-012-a relayA first delivered message = "thr-info"`
- [x] `LMBR-T-012-b relayA second delivered message = "thr-warn"`
- [x] `LMBR-T-012-c relayA third dequeue timed out (relayA received exactly two)`
- [x] `LMBR-T-012-d relayB first delivered message = "thr-warn" (INFO dropped by WARN threshold)`
- [x] `LMBR-T-012-e relayB third dequeue timed out (relayB received exactly one)`

Note: relay capture-probe fixture (same as T-030), `disable default file? = TRUE`,
no temp root. Two relay appenders, both `FilterMode = Mirror` so threshold is the
only discriminator; A threshold `INFO`, B threshold `WARN`. Log INFO `"thr-info"`
then WARN `"thr-warn"` (sourceTag `"THR"`). `-012-d`/`-012-e` prove B's threshold
discriminated (first delivered is the WARN, INFO dropped); `-012-b` proves A took
both. Use the T-030 timeout to avoid AF queue-latency false negatives (SRS-053).

### tests/Integration/Delivery - single appender.vi  (T-029 -> SRS-019)

VI Documentation line: `Implements LMBR-T-029 -> SRS-019. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-029-a Statement delivered within timeout`
- [x] `LMBR-T-029-b Delivered message matches`

### tests/Integration/Delivery - broadcast.vi  (T-030 -> SRS-019/028)

VI Documentation line: `Implements LMBR-T-030 -> SRS-019, SRS-028. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-030-a relayA element received`
- [x] `LMBR-T-030-b relayA msg = "broadcast-probe"`
- [x] `LMBR-T-030-c relayA level = "INFO"`
- [x] `LMBR-T-030-d relayA sourceTag = "BCAST"`
- [x] `LMBR-T-030-e Appender 'relayA' single delivery`
- [x] `LMBR-T-030-f relayB element received`
- [x] `LMBR-T-030-g relayB msg = "broadcast-probe"`
- [x] `LMBR-T-030-h relayB level = "INFO"`
- [x] `LMBR-T-030-i relayB sourceTag = "BCAST"`
- [x] `LMBR-T-030-j Appender 'relayB' single delivery`
- [x] `LMBR-T-030-k relayC element received`
- [x] `LMBR-T-030-l relayC msg = "broadcast-probe"`
- [x] `LMBR-T-030-m relayC level = "INFO"`
- [x] `LMBR-T-030-n relayC sourceTag = "BCAST"`
- [x] `LMBR-T-030-o Appender 'relayC' single delivery`

### tests/Integration/Registry - unregister silences appender.vi  (T-032 -> SRS-020)

VI Documentation line: `Implements LMBR-T-032 -> SRS-020. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-032-a relayA element received`
- [x] `LMBR-T-032-b relayA msg = "reg-before"`
- [x] `LMBR-T-032-c relayB element received`
- [x] `LMBR-T-032-d relayB msg = "reg-before"`
- [x] `LMBR-T-032-e relayC element received`
- [x] `LMBR-T-032-f relayC msg = "reg-before"`
- [x] `LMBR-T-032-g relayA element received (after unregister)`
- [x] `LMBR-T-032-h relayA msg = "reg-after"`
- [x] `LMBR-T-032-i relayC element received (after unregister)`
- [x] `LMBR-T-032-j relayC msg = "reg-after"`
- [x] `LMBR-T-032-k Appender 'relayB' Silent`
- [x] `LMBR-T-032-l Unknown-id unregister is a no-op`
- [x] `LMBR-T-032-m relayA msg = "reg-ghost"`
- [x] `LMBR-T-032-n relayC msg = "reg-ghost"`

### tests/Integration/Relay - Message Mode.vi  (T-043 -> SRS-024)

VI Documentation line: `Implements LMBR-T-043 -> SRS-024. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-043-a msgmode-probe reached the consumer`  *(fix missing space in VI)*
- [x] `LMBR-T-043-b Delivered value matches msgmode-probe`
- [x] `LMBR-T-043-c level = INFO`
- [x] `LMBR-T-043-d sourceTag = "MSG"`
- [x] `LMBR-T-043-e Dequeuer Timed Out (no further messages)`

### tests/Integration/Relay - filtered tap.vi  (T-045 -> SRS-023/026)

VI Documentation line: `Implements LMBR-T-045 -> SRS-023, SRS-026. Assert-level IDs: Test-ID-Assert-Checklist.md.`

- [x] `LMBR-T-045-a Statement delivered within timeout`
- [x] `LMBR-T-045-b INFO Dropped, WARN delivered`
- [x] `LMBR-T-045-c ERROR delivered`
- [x] `LMBR-T-045-d Queue empty`

---

## Coverage note

247 asserts across 44 VIs, all tagged. Case IDs exercised: T-001, T-002, T-003,
T-004, T-005, T-006, T-007, T-008, T-009, T-010, T-011, T-012, T-013, T-014, T-015,
T-016, T-017, T-018, T-019, T-020, T-022, T-023, T-024, T-025, T-026, T-027, T-029,
T-030, T-031, T-032, T-033, T-034, T-035, T-036, T-037, T-038, T-039, T-040, T-041,
T-042, T-043, T-044, T-045, T-046, T-047, T-048, T-049, T-050, T-051 (a-d), T-052, T-053, T-054, T-055, T-056, T-057, T-058, T-060, T-061.
The pure-VI tier is complete (T-059 is an inspection item recorded in
`docs/Path-Derivation-Audit.md`). Delivery & filtering cluster complete
(T-011/012/013/019/031/033). File mechanics cluster complete (T-006/034/039/042).
Backpressure drop-policy cluster complete: T-044 (queue mode), T-046 (unbounded),
and the pure `ApplyBackPressure` unit tests T-047 (drop-oldest), T-048 (drop-newest),
T-049 (level-aware, incl. the fast-path/scan oracle) all green. Remaining, `planned`
in Test-Strategy §4:

- **Backpressure:** T-050 (no-blocking) done. T-051 (drop notice) pure part
  `-a…d` done against `BuildDropNotice`. `-051-e` (the emission integration check)
  is **deferred to the post-PR bounded-backpressure follow-up** (bundled with the
  ConfigReader implementation): the bounded intake buffer/drain isn't built yet, so
  the appender is unbounded-only today. Decision primitives (`ApplyBackPressure`,
  `BuildDropNotice`) are done and tested; see PR-Notes §4.
- **Lifecycle:** T-052-T-055.
- **Parked:** T-021 (ConfigReader backlog), T-028 (resolve-once).
