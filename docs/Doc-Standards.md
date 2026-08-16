# Documentation Standards: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Purpose:** One source of truth for how VIs are documented, so descriptions
stay consistent and don't have to be reconstructed from memory each time.

**Status:** Draft. Content entered against this standard still passes SOP-117
human review before being treated as authoritative.

---

## 1. VI description template

Every non-trivial VI is described with the following sections, in this order.
Do **not** number them in the actual write-up; the numbering here is only for
reference.

- **Path** — repository path of the VI (e.g. `src/Public/Logger.lvclass/Shutdown.vi`).
- **Owning library** — the `.lvlib` / class that owns it, plus scope
  (public / community / protected / private) and any friend relationship.
- **VI Documentation** — the description shown in Context Help: what the VI does
  and why, in a few sentences. This is the text entered in the VI's own
  Documentation field. When written up for paste (e.g. in `Cleanup-Suggested-Text`),
  present it in a **literal/fenced code block with one line per paragraph** (no
  hard mid-sentence wraps), so it copies into the LabVIEW Documentation field
  without soft-wrap line breaks turning into literal newlines. LabVIEW does its own
  wrapping.
- **Connector Pane** — the terminals: inputs and outputs, with types. Note when
  the error cluster is present, and any deliberate omission (e.g. a pure helper
  with no error terminals).
- **Terminal Description and Tips** — see section 2.
- **Block Diagram** — how it works, left to right, at the level a reviewer needs
  to rebuild or verify it. Name the key nodes and the control/data flow.
- **Notes** — invariants, gotchas, ordering constraints, edge cases, and any
  SOP-117 review flag.

Test VIs (anything under `tests/` that runs Caraya asserts) follow the same
template and additionally obey the assert-naming standard in section 4.

---

## 2. Terminal Description and Tips

Each real connector-pane data terminal carries **two** things:

- **Description** — one line stating what the terminal carries (the text in the
  terminal's description field, shown in Context Help / the terminal detail).
- **Tip** — a short hover string (the tip strip shown when hovering the terminal
  on the connector pane). Briefer than the description; a phrase, not a sentence.

Present them as a small table:

| Terminal | Description | Tip |
|---|---|---|
| `queueIDList` | Appender ids whose relay queues should be destroyed; each mapped to a queue name via `RelayQueueName`. | Ids of relay queues to release |
| `error in` | Standard error cluster; cleared internally so teardown runs regardless of upstream failure. | Error in (cleared before loop) |
| `error out` | Standard error cluster; carries only genuine release errors. | Error out |

Conventions:

- **Dynamic-dispatch object terminals** (`<Class> in` / `<Class> out`) do **not**
  need descriptions or tips (project decision).
- **Unlabeled class-object terminals** (a bare object) are treated the same way.
- The **`error in` / `error out` / `status` / `code` / `source`** cluster carries
  LabVIEW's standard boilerplate; a short tip is fine but the standard boilerplate
  description need not be rewritten.
- Descriptions name the offending value or valid set where relevant (mirrors the
  error-message convention in `Error-Codes.md`).

---

## 3. Example (abridged)

`tests/Support/Release Relay Queues.vi` — `Tests.lvlib`, friend of `Lumberjack.lvlib`.

- **VI Documentation:** Test teardown helper. Force-destroys the named relay
  queues for a set of appender ids so no queue leaks into the process-global
  namespace between tests.
- **Connector Pane:** `queueIDList` (array of String), `error in` → `error out`.
- **Terminal Description and Tips:** as the table in section 2.
- **Block Diagram:** clear `error in`; For Loop over `queueIDList`;
  `RelayQueueName(id)` → `Obtain Queue` (element `Statement`, create = FALSE) →
  `Not A Refnum?` → release with force / skip; merge genuine errors.
- **Notes:** idempotent (create = FALSE + guard); force destroy clears namespace
  residue; must run after `Shutdown` confirms the tree stopped.

---

## 4. Test VI assert-naming standard

Applies to every VI under `tests/` that runs Caraya asserts. Its purpose is to
make each assert traceable from the run report back to a requirement, so a
`LumberjackTestResults.txt` line and the SRS resolve to each other.

- **Every assert name begins with a hierarchical Test ID:** the case-level ID
  (`LMBR-T-###`), a suffix letter, then the human-readable assertion, e.g.
  `LMBR-T-014-c Level within band is accepted`. Caraya writes the name into
  `tests/Test Results/LumberjackTestResults.txt` and the HTML report, so the
  Test ID is the join key from a report line to the `Test-Strategy.md` §4 matrix.
- **The case ID is the unit of trace.** The portion before the suffix maps to one
  SRS item (or set) in the §4 matrix; the suffix letter distinguishes the
  individual asserts within that case.
- **Suffixes are per case and run continuously, even across VIs.** A case
  implemented by two VIs keeps one letter sequence (e.g. T-005 is `-a..-d` in
  `Layout - JSON Format.vi` and `-e..-k` in `Layout - JSON escape string.vi`), so
  no two asserts ever share an ID. One VI may also carry asserts from more than
  one case (e.g. `Layout - CSV quoting.vi` holds T-002 and T-003 asserts).
- **Looped asserts compute the suffix; never hand-type it.** Derive the trailing
  letter from the iteration index: index into a 26-char constant `abc...z` with
  `String Subset`, or `97 + index -> U8 -> Byte Array To String`. For a nested
  loop the index is `outer * innerCount + inner`; for a flat loop, a running
  shift-register counter incremented once per assert.
- **Adding an assert:** append the next unused suffix under its case. **IDs are
  assigned once and never reused**, even if an assert is later deleted, so an
  archived report still resolves against a future revision of the matrix.
- **A new behavior with no case ID** first gets the next free `LMBR-T-###` row in
  the §4 matrix, traced to its SRS item, before its asserts are named.
- **Every assert gets a meaningful name.** Replace Caraya default names (e.g.
  `Assert Equal Value_Variant`) with a phrase stating what is checked.
- **Every assert specifies its inputs.** The VI description shall state, per
  assert, the exact input data terminal(s) of the VI-under-test that are
  exercised, the concrete value fed to each, and the expected result (return value
  or error code). A reviewer must be able to reconstruct each assert from the
  description alone, with no unstated inputs. Where asserts mutate a shared
  baseline, state the baseline once and then, per assert, only the single terminal
  and value that changes. Choose distinctive, non-default values so a pass-through
  or defaulting bug cannot satisfy a check spuriously. This per-assert input
  table/list is part of the Block Diagram section (section 1) for every test VI.
- **The VI Documentation field lists the case IDs the VI implements** and the SRS
  they trace to (e.g. "Implements LMBR-T-002, T-003 -> SRS-012"), and points to
  `Test-ID-Assert-Checklist.md`, which holds the full per-assert suffix map.

---

## 5. Companion documents

- `Error-Codes.md` — error code registry and message conventions.
- `Doc-Terminal-Audit.md` — audit of which terminals carry descriptions.
- `Test-Strategy.md` — test tiers and the requirement-traced inventory (§4
  matrix) that owns the case-level Test IDs.
- `Test-ID-Assert-Checklist.md` — per-assert hierarchical ID map for the built
  test VIs.
- `Design.md`, `Class-Reference.md`, `API-Guide.md` — architecture and API.
