# Path-Derivation Audit (LMBR-T-059)

**Requirement:** SRS-LMBR-064. No library VI shall derive an external resource
location from its own VI path (for example via `Current VI's Path`), because
inside a Packed Project Library that resolves to a location that differs from the
host application's directory. All external paths shall come from launch inputs or
configuration; all external-path computation shall be isolated in one VI
(`ResolveHostRoot`).

**Test ID:** LMBR-T-059 (inspection, not a Caraya assert). This document is the
audit record.

**Status:** Draft. Automated pass complete; manual diagram confirmation pending
the ticks below. Subject to review before it is treated as authoritative.

---

## 1. Method

Two passes, because neither alone is sufficient:

- **Automated string scan.** `strings` over every `src/**/*.vi`, searching for
  `Current VI's Path`, `This VI's Path`, `VI's Path`, and `Application Directory`.
  This reliably catches subVI-based derivation (subVI names are stored as linkage
  strings) and any `Application Directory` use, but `Current VI's Path` is a
  primitive with no stored label, so a null result there is necessary, not
  sufficient.
- **Manual diagram inspection.** Open the block diagram of each VI that builds or
  consumes an external path and confirm the root originates from an input
  terminal or configuration, never from a self-location primitive.

## 2. Automated finding

- Only `src/Support/Path/ResolveHostRoot.vi` references application context, via
  its `Application Directory.vi` subVI. That is the one sanctioned host-context
  source, in the one VI permitted to compute an external base path.
- No other `src` VI carries a readable self-location or application-context
  string.
- Re-scan (2026-08-23): the only `Current VI's Path` match in any `src` VI is the
  phrase inside `ResolveHostRoot.vi`'s own Documentation string ("Never derives a
  path from a Lumberjack VI's own location (no Current VI's Path)"), confirmed by
  inspection to be prose, not a diagram node. So the primitive remains
  non-greppable, and the scan can false-positive on descriptions that name it;
  §3 manual inspection is the real check for the primitive's absence. No `src` VI
  outside `ResolveHostRoot` carries any self-location or application-context string.

## 3. Manual inspection checklist

VIs that build or consume an external path (open the diagram, confirm the root
comes from an input/config and no `Current VI's Path` / `This VI's Path` node is
present). Tick when confirmed.

Reference (sanctioned):

- [x] `src/Support/Path/ResolveHostRoot.vi` — the only VI allowed to consult
  application context. If `HostApplicationPath` is supplied it is routed through; a
  built application (Application.Kind = Run Time System) without it returns error
  5000; the development system falls back to `Application Directory`. The root is
  never derived from this VI's own path (LMBR-T-057/058 exercise this). Confirmed by
  inspection: no `Current VI's Path` node on the diagram. The `Current VI's Path`
  phrase the re-scan matched is inside this VI's own Documentation string
  ("...no Current VI's Path..."), affirming non-use, not a node.

Root-consuming path builders (root must arrive as an input, not be self-derived):

- [x] `src/Support/File/BaseFolder.vi` — calendar subfolder built under the
  `rootFolder` input. Confirmed: rootFolder arrives on an input terminal.
- [x] `src/Core/Appenders/FileAppender.lvclass/OpenNewFile.vi` — file created
  under the `targetFolder` input. Confirmed.
- [x] `src/Core/Appenders/FileAppender.lvclass/Prune.vi` — enumerates/deletes
  within a supplied folder. Confirmed.
- [x] `src/Support/File/PruneSelection.vi` — operates on supplied file lists
  (`ExistingFiles`); computes no root. Confirmed: no path derivation.
- [x] `src/Support/Config/Resolve.vi` — config file path from launch input;
  missing file is a non-fatal warning (5014), not a self-derived fallback. Confirmed.
- [x] `src/Core/LogManager/LogManager.lvclass/ResolveConfig.vi` — wires host root
  + config path from inputs into the appenders. Confirmed.

String-level only (no external-path computation; spot-check for completeness):

- [x] `src/Support/File/ISO8601FileName.vi` — returns a file *name* string, no
  root. Confirmed: builds a string only.
- [x] `src/Support/File/IsFileNameSafe.vi` — character validation only. Confirmed.
- [x] `src/Support/Config/Mapping/FileAppenderConfigDTOFromNative.vi`
- [x] `src/Support/Config/Mapping/FileAppenderConfigFromDTO.vi`
- [x] `src/Support/Config/Mapping/FileConfigDTOFromNative.vi`
- [x] `src/Support/Config/Mapping/FileConfigFromDTO.vi`
- [x] `src/Support/Config/ValidateFileAppenderConfigDTO.vi`
- [x] `src/Support/Config/ValidateFileConfigDTO.vi`

(All DTO/native mapping and validation VIs carry path fields as plain strings, no
path computation, confirmed 2026-08-23.)

## 4. Conclusion

When every box in Section 3 is ticked, SRS-LMBR-064's isolation clause is
confirmed by inspection: external-path computation is quarantined in
`ResolveHostRoot`, and no library VI self-derives an external path.

All Section 3 boxes are ticked (2026-08-23). External-path computation is
quarantined in `ResolveHostRoot` (dev-system `Application Directory`, otherwise the
`HostApplicationPath` input); every other listed VI receives its root/folder as an
input or unbundled config field, and no `Current VI's Path` node exists on any
diagram. SRS-LMBR-064's isolation clause is confirmed by inspection.

Reviewed by: Dan (dallis@veli.co) — 2026-08-23. (Confirm the reviewer name as you
want it recorded for the sign-off.)
