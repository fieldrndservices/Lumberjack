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
the ticks below. Subject to SOP-117 human review before it is authoritative.

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
- Limitation: does not prove the absence of the `Current VI's Path` primitive
  (no greppable token); Section 3 covers that by inspection.

## 3. Manual inspection checklist

VIs that build or consume an external path (open the diagram, confirm the root
comes from an input/config and no `Current VI's Path` / `This VI's Path` node is
present). Tick when confirmed.

Reference (sanctioned):

- [ ] `src/Support/Path/ResolveHostRoot.vi` — the only VI allowed to consult
  application context; uses `Application Directory` only in the dev-system
  fallback, never `Current VI's Path` (LMBR-T-057/058 exercise this).

Root-consuming path builders (root must arrive as an input, not be self-derived):

- [ ] `src/Support/File/BaseFolder.vi` — calendar subfolder built under the
  `rootFolder` input.
- [ ] `src/Core/Appenders/FileAppender.lvclass/OpenNewFile.vi` — file created
  under the `targetFolder` input.
- [ ] `src/Core/Appenders/FileAppender.lvclass/Prune.vi` — enumerates/deletes
  within a supplied folder.
- [ ] `src/Support/File/PruneSelection.vi` — operates on supplied file lists
  (`ExistingFiles`); computes no root.
- [ ] `src/Support/Config/Resolve.vi` — config file path from launch input;
  missing file is a non-fatal warning (5014), not a self-derived fallback.
- [ ] `src/Core/LogManager/LogManager.lvclass/ResolveConfig.vi` — wires host root
  + config path from inputs into the appenders.

String-level only (no external-path computation; spot-check for completeness):

- [ ] `src/Support/File/ISO8601FileName.vi` — returns a file *name* string, no
  root.
- [ ] `src/Support/File/IsFileNameSafe.vi` — character validation only.
- [ ] `src/Support/Config/Mapping/FileAppenderConfigDTOFromNative.vi`
- [ ] `src/Support/Config/Mapping/FileAppenderConfigFromDTO.vi`
- [ ] `src/Support/Config/Mapping/FileConfigDTOFromNative.vi`
- [ ] `src/Support/Config/Mapping/FileConfigFromDTO.vi`
- [ ] `src/Support/Config/ValidateFileAppenderConfigDTO.vi`
- [ ] `src/Support/Config/ValidateFileConfigDTO.vi`

## 4. Conclusion

When every box in Section 3 is ticked, SRS-LMBR-064's isolation clause is
confirmed by inspection: external-path computation is quarantined in
`ResolveHostRoot`, and no library VI self-derives an external path. Record the
reviewer and date here on sign-off (SOP-117).
