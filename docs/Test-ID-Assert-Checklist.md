# Test ID Assert-Naming Checklist

**Purpose:** apply hierarchical `LMBR-T-###-x` Test IDs to every assert in the
built test VIs, so each assert's pass/fail surfaces under its own ID in
`tests/Test Results/LumberjackTestResults.txt` and the HTML report, while still
rolling up to the case-level Test ID that traces to the SRS (Test-Strategy §4).

**Status:** 101/101 built asserts tagged and passing (verified against the
2026-08-13 18:48 run), 0 failures, no duplicate IDs. Draft record, not a signed
verification artifact; still subject to SOP-117 human review before it is treated
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

### tests/Unit/Layout - CSV quoting.vi  (T-002, T-003 -> SRS-012)

VI Documentation line: `Implements LMBR-T-002, T-003 -> SRS-012. Assert-level IDs: Test-ID-Assert-Checklist.md.`

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

---

## Integration tier

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

101 asserts across 16 VIs, all tagged. Case IDs exercised: T-002, T-003, T-004,
T-005, T-007, T-008, T-009, T-010, T-014, T-015, T-016, T-017, T-018, T-025,
T-029, T-030, T-032, T-035, T-036, T-037, T-040, T-041, T-043, T-045. Every other
Test ID in Test-Strategy §4 is `planned` (no built VI). Two coverage gaps to keep
visible:

- **T-001 (CSV column order)** is `planned` — no current assert checks CSV field
  order.
- **T-013 (Mirror mode)** is `planned` — nothing yet asserts accept-all mirror
  mode above threshold.
