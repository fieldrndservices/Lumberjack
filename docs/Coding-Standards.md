# Coding Standards: Lumberjack

**Project:** Lumberjack (Actor Framework logging library for LabVIEW)

**Purpose:** One source of truth for naming, casing, member scope, and diagram
house style, so conventions stay consistent and don't have to be reconstructed
from memory each time. Companion to `Doc-Standards.md` (which owns how VIs and
terminals are *documented*); this document owns how they are *named and scoped*.

**Status:** Draft. Content entered against this standard still passes SOP-117
human review before being treated as authoritative.

---

## 1. Naming and casing

- **Classes, VIs, typedefs:** PascalCase, with acronyms kept all-caps
  (`CSVLayout`, `JSONLayout`, `GetID`, `LogManager`).
- **Cluster and class private-data fields:** camelCase matching the JSON key
  (`dropPolicy`, `mode`, `defaultFileAppender`). A field whose type is a named
  typedef takes a camelCase role / JSON-key label, **not** the type name (e.g. a
  `FilterMode`-typed field is labeled `mode`, not `FilterMode`).
- **`scripts/` folder:** lowercase.
- **Connector-pane controls/indicators:** PascalCase, **except** LabVIEW standard
  terminals, which keep their stock labels (`error in`, `error out`, and other
  built-in controls/indicators).
- **Boolean outputs:** no trailing `?` (`accepted`, not `accepted?`).
- **Actor Framework enqueuer terminals:** `Enqueuer in` / `Enqueuer out`.

---

## 2. Enum tokens

- **Behavior enums** (`DropPolicy`, `FilterMode`, `RelayMode`): PascalCase members
  (`DropOldest`, `Mirror`, `Message`).
- **Severity members:** UPPERCASE (`OFF`, `FATAL`, `ERROR`, `WARN`, `INFO`,
  `DEBUG`, `TRACE`, `ALL`). The token doubles as the log-output level text, so its
  casing is user-visible.
- **Single source of truth:** the enum typedef is the one source of truth for a
  config token set. The `*FromString` / `*String` helpers read the enum directly
  rather than maintaining a parallel token list, so adding or renaming a member is
  a one-place change. Config files serialize enums by **member name**, not
  ordinal (see `Design.md` §4.2).

---

## 3. Member scope and accessors

- **Default scope is `protected`.** Class-data accessors and cross-class members
  are `protected`; a subclass reaches inherited protected members automatically.
- **`FRIEND` only where needed.** Add a `FRIEND` declaration only for a
  non-subclass caller that must reach an internal member (for example,
  `tests/Tests.lvlib` is a friend of `Lumberjack.lvlib` so unit tests can call the
  protected pure helpers). This keeps those members off the public PPL surface.
- **`community` scope is not used.**
- **Dynamic-dispatch VIs cannot be `community`-scoped.** Field accessors should be
  **static**, not DD.
- **Prefer accessor VIs over property nodes** for by-value class data.

The scope-to-path mapping and the API-boundary rationale live in `Design.md` §8;
this section is the actionable rule set.

---

## 4. Documentation

How VIs, typedefs, and terminals are documented (the description template, the
Description vs Tip split, and the test-VI assert-naming standard) is owned by
`Doc-Standards.md`. Two reminders that intersect with naming:

- Descriptions apply to the item itself (VI, class, typedef). Tips are a
  control/indicator property only; there is no per-VI Tip in LabVIEW.
- Provide a Description + Tip per connector-pane terminal where it warrants one,
  most valuable on public, adopter-facing VIs.

---

## 5. Diagram house style

Diagrams are **hand-authored SVG**, rasterized to PNG via `cairosvg` (not
matplotlib). Save the `.svg` source next to the `.png` in `diagrams/` so a figure
stays re-editable.

Palette (fill on background):

| Role | Fill / accent | Background |
|---|---|---|
| Control-plane / Logger | `#2e5a88` (blue) | `#eaf0f8` |
| Actors (LogManager, appenders) | `#3f7a4b` (green) | `#e8f2ea` |
| Persistence / store | `#b5651d` (orange) | `#fdf0e3` |
| Highlighted constraint | `#a64b4b` (red) | — |
| Text / edges | `#1f2937` (slate) | — |
| Secondary | `#6b7280` (gray) | — |
| Lifeline | `#b0b6bf` (gray) | — |
| Neutral fill | `#f2f4f7` | — |

Form:

- Font: Helvetica / Arial sans-serif.
- Rounded boxes (`rx ~7`); dashed lifelines.
- Solid arrowheads for calls; open / dashed for returns.
- Reference in Markdown as
  `![caption](diagrams/NAME.png){ width=X.Xin }`; the caption line is exempt from
  the 80-column rule.

Current figures: topology, hierarchy, config, hotpath, register, shutdown
(Figures 1–6), launch sequence (Figure 7), and barriers (Figure 8).

---

## 6. Companion documents

- `Doc-Standards.md` — VI/terminal documentation template and the test-VI
  assert-naming standard.
- `Design.md` — architecture, the scope-to-path table (§8), and config/enum
  serialization rationale (§4.2).
- `Error-Codes.md` — error-code registry and message conventions.
- `Test-Strategy.md`, `Test-ID-Assert-Checklist.md` — test tiers, the
  requirement-traced inventory, and the per-assert ID map.
