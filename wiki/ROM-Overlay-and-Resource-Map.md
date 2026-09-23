# Resource and overlay system

> **Scope:** This page is the canonical owner for MKMSZ's **global file-table architecture, raw/resource loading mechanisms, stage-overlay identity rules, resource-selector grammar, global-vs-stage-local resource semantics, and resource packaging rules** used by MKMSZR.
>
> It does **not** own literal ROM/RDRAM allocation intervals, cross-stage item-planner/proof chronology, or concrete per-stage pickup/resource records. Those belong respectively to [Memory and allocation map](Memory-and-Allocation-Map), [Global item materialization and solvability](Global-Item-Materialization-and-Solvability), and the eight [stage catalogs](Stage-Catalogs).

## Current conclusion

MKMSZ uses a global file table to locate/load file packages, but ordinary stage resources are interpreted through a **stage-local** resource file and selector table. These namespaces must not be conflated: a global file ID can identify a package across the game, while an ordinary pickup's `+0x24` selector is meaningful only against the resource file loaded for that stage.

The ordinary-pickup resource path is sufficiently decoded to explain current production behavior and the constraints consumed by the global materializer. The resource system establishes how selectors resolve, how embedded and externally backed resource records differ, and how stage/overlay identity must be qualified. The global materialization owner decides when and how those mechanisms are used for cross-stage randomization.

## Global file table and raw loading

The global file table begins at ROM `0x000A5010` / VA `0x800A4410`. Entries are 12 bytes, and file IDs are global identifiers into that table.

Two production-relevant examples are:

- file ID `0x1B`: the MKMSZR native payload source used by the proven bootstrap path;
- file ID `0x5E`: the normal title-screen image package.

The raw global-file loader at `0x80065D64` is synchronous in the runtime-confirmed native bootstrap path. Exact production ownership of the patched table entries and their backing ROM storage belongs to [Memory and allocation map](Memory-and-Allocation-Map); this page owns the file-table/loader relationship rather than declaring those bytes free or reusable.

Function-level semantics for `0x80065D64` and other helpers remain indexed in [Function registry](Function-Registry).

## Global versus stage-local resource identity

| Value / address kind | Scope | Rule |
|---|---|---|
| Global file ID | Global file table | Identifies a file/package entry. Do not reinterpret it as a stage-local selector. |
| Stage resource selector | Current stage resource file | Ordinary pickup `+0x24` is a word index into the currently loaded stage resource file. The same numeric selector can mean different things in another stage. |
| File-relative descriptor/data offset | One loaded resource file | Resolve relative to that file's runtime base. It is not a ROM offset or globally stable VA. |
| External resource/cache ID | Loader/package context | Numeric identity alone is not proof that the resource is resident or portable to another stage. |
| Stage-overlay VA | Loaded overlay + source artifact | The VA is not a global function identity; stage/source qualification is required. |
| Literal ROM/RDRAM interval | Allocation owner/lifecycle | Canonical ownership and availability belong to [Memory and allocation map](Memory-and-Allocation-Map). |

## Main-stage resource files

Each of the eight main gameplay stages has its own resource file and runtime-loaded base. Concrete file-table entries, stock ROM ranges, verified runtime bases, selector tables, pickup-to-selector usage, and decoded resource records remain canonical in the individual [stage catalogs](Stage-Catalogs).

This page intentionally does **not** duplicate the former eight-stage range/slot table. Stage-relative facts should be updated once, in the relevant stage catalog.

The current stage resource-file base used by the ordinary-pickup path is held at `0x802F82B8`. Stage-loading code writes the current loader/allocator result there before ordinary resource lookup consumes it. The pointed-to address and extent are dynamic and stage-dependent; their allocation classification belongs to the Memory Map.

## Outer selector table grammar

The first words of a stage resource file form a stage-local outer selector table. Occupied entries resolve to file-relative descriptors/structures. Depending on the resource, those structures may lead to:

- embedded-data bundles;
- external-resource/cache-ID backed records;
- zero-terminated lists;
- aliases;
- valid structures whose exact gameplay owner remains unresolved.

A zero outer-table word is only a **logical selector-capacity observation**. It does not reserve, expose, or prove free physical bytes in the file.

For ordinary pickups, record `+0x24` supplies the selector. The decoded lookup is:

```text
selector       = pickup_record[+0x24]
base           = *(0x802F82B8)
entry_ptr      = base + (selector << 2)
descriptor_ptr = base + *entry_ptr
```

At `0x80038BE4..0x80038C04`, the pickup manager computes the selected word and calls `0x800281A0`. That helper loads the selected file-relative descriptor offset, adds the current stage resource base, and calls `0x80028128` with the resulting direct descriptor pointer.

On this **ordinary-pickup** path, no stock selector-count/table-width check occurs before the selector is used as a 32-bit word index. Therefore a relocated/expanded resource file can technically place selector words beyond the original stock table and address them with:

```text
pickup +0x24 = appended_selector_entry_offset / 4
```

This is the resource-system basis for extension selectors. The disposable Proof D/F/H sequence, composed Prison/Fortress stress work, deduplication policy, and production-integration gates are deliberately owned by [Global item materialization and solvability](Global-Item-Materialization-and-Solvability). The confirmed ordinary-pickup behavior must not be generalized automatically to other resource consumers.

## Resource-record storage forms

The decoded ordinary resource records use two materially different data-location forms:

- **embedded form:** record `+0x04 = 0`; record `+0x08` is a stage-file-relative compressed-data offset;
- **external-resource-ID form:** record `+0x04` is a cache/resource ID; record `+0x08 = 0`.

An external resource ID is not a self-contained pointer and is not guaranteed to be portable between stages. Whether the referenced payload is available depends on the active package/cache context. Cross-stage failures and the successful external-to-embedded conversion proofs are recorded under [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).

For embedded images, the native path calls `0x8000322C`. Compression type 4 dispatches to `0x80003428`, whose decoder uses a 1024-byte ring buffer and separate MSB-first control/token streams. Static analysis established the native inclusive back-reference count as `low6 + 2`. These are resource loading/decoding mechanics; using them to manufacture imported destination bundles is materializer policy and remains outside this page.

## Title resource packaging — global file `0x5E`

Global file ID `0x5E` is the normal title-screen image package. The clean USA Rev. 0 package decodes to `0x61494` bytes.

The package uses the game's **MSB-first LZW-style stream**. A matching encoder/decoder pair is **Static-confirmed** by byte-exact stock decode/re-encode: decoding the stock package and re-encoding it yields the original compressed size `0x2F3E0` and round-trips to the same `0x61494` decoded bytes.

The accepted Candidate-B artwork recompresses to `0x2FD95` bytes, which is `0x9B5` larger than the stock slot. It therefore cannot safely remain in the original stock storage extent and requires relocation. The literal stock extent, production destination allocation, capacity, and build-dependent compressed endpoints remain canonical in [Memory and allocation map](Memory-and-Allocation-Map); this page records the package/codec mechanics only.
The accepted MKMSZR title path is **data-only**:

1. decode the existing `0x5E` package;
2. modify the six CI8 tile pixel regions used by the title art;
3. rasterize the configurable uppercase edition line into that same decoded image;
4. recompress the package losslessly;
5. repoint the global file-table entry to the generated `0x5E` package.

No title executable cave is required by the accepted path. The production high-ROM allocation, generated-file capacity, and build-dependent compressed endpoints are allocation facts owned by [Memory and allocation map](Memory-and-Allocation-Map).

The title palette descriptor is at ROM `0x000B3360`; the count word is followed by the 256-entry palette at `0x000B3364`. Offline reconstruction uses the verified BGR555 interpretation.

This page owns the **file/package mechanics**. Branding design, visual acceptance, and title-proof chronology belong to [Presentation and branding](Presentation-and-Branding).

## Overlay identity rules

Main stage overlays reuse a common runtime address region. The established main-stage overlay base is `0x802ECE30`, but that VA alone does not identify a unique function or byte owner.

Any overlay finding must include at least:

- platform/revision;
- loaded stage or overlay identity;
- source artifact/file when known;
- runtime VA;
- evidence scope.

A function observed at a VA in one stage must not be promoted to a globally resident function merely because another stage uses the same address range. Exact continuous ownership of the shared overlay region belongs to [Memory and allocation map](Memory-and-Allocation-Map), while stable function semantics belong to [Function registry](Function-Registry).

## Allocation and materialization boundaries

Resource mechanics do not establish allocation safety.

- A zero selector entry is not free file storage.
- A file-relative offset is not a ROM offset.
- A successful disposable resource relocation does not reserve that ROM range for production.
- Dynamic stage resource allocations do not imply a fixed free RDRAM interval.
- Appending selector/descriptor/data structures requires explicit bounded backing storage and updated file-table metadata.
- Runtime arena/headroom and composition with other production owners must be checked separately.

Literal interval ownership, proof conflicts, production capacity, and free/candidate/unknown classifications belong to [Memory and allocation map](Memory-and-Allocation-Map).

The following cross-stage concerns belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability), not this page:

- the global logical item pool and exact-visual materialization policy;
- destination-safe key/crystal award handling;
- extension-selector proof chronology;
- foreign-bundle rebasing and external-to-embedded proof history;
- deterministic resource deduplication/capacity planning;
- composed Prison/Fortress stress validation;
- deterministic global retries, solver behavior, required Power Upgrades, and the Temple Map question.

Concrete stage-relative selectors, records, resource IDs, file ranges, runtime bases, and per-stage capacity observations stay in the eight [stage catalogs](Stage-Catalogs).

## Resource-system invariants

1. **Global file IDs and stage-local selectors are different namespaces.**
2. **Stage selectors are meaningful only with the correct loaded stage resource file.**
3. **External resource IDs are context-dependent, not portable pointers.**
4. **Zero/unused-looking selector entries do not prove free payload bytes.**
5. **File-relative, ROM, RDRAM, and overlay-relative coordinates must be labeled explicitly.**
6. **Overlay VAs require stage/source identity.**
7. **Proof resource placement never becomes production allocation ownership by implication.**

## Related canonical pages

- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership, allocation classes, aliases, lifecycle, and conflicts.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — cross-stage planner, resource-import proof history, retries, solver, and current integration gates.
- [Stage catalogs](Stage-Catalogs) — all concrete stage-relative ordinary records and resource instances.
- [Data structures and encodings](Data-Structures-and-Encodings) — canonical stable record/structure/codec grammar outside the selector/loading rules owned here.
- [Function registry](Function-Registry) — canonical function semantics.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production ordinary-pickup behavior.
- [Presentation and branding](Presentation-and-Branding) — current title/legal branding behavior and visual evidence.
