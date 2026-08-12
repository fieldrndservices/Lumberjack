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

## 4. Companion documents

- `Error-Codes.md` — error code registry and message conventions.
- `Doc-Terminal-Audit.md` — audit of which terminals carry descriptions.
- `Design.md`, `Class-Reference.md`, `API-Guide.md` — architecture and API.
