# Stage catalogs

> **Scope:** This page is the shared index, legend, and schema owner for the eight MKMSZ main-stage catalogs. The child pages own concrete stage-relative pickup records, resource slots, resource-file mappings, decoded bundle/list records, and stage-specific evidence or unresolved questions.
>
> This page does **not** create a global resource-bundle catalog. Cross-stage logical planning/materialization belongs to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability); global file/loader/selector grammar belongs to [Resource and overlay system](ROM-Overlay-and-Resource-Map).

## Stage map and catalog index

The compact selector is MKMSZR's safe eight-entry menu index. The native ID is the value used by the game and by stage-qualified runtime logic.

| Compact selector | Native ID | Stage | Ordinary pickups | Catalog |
|---:|---:|---|---:|---|
| 0 | 0 | Temple | 4 | [Temple](Stage-Catalog-Temple) |
| 1 | 1 | Wind | 6 | [Wind](Stage-Catalog-Wind) |
| 2 | 2 | Water | 9 | [Water](Stage-Catalog-Water) |
| 3 | 3 | Earth | 20 | [Earth](Stage-Catalog-Earth) |
| 4 | 4 | Prison | 10 | [Prison](Stage-Catalog-Prison) |
| 5 | 5 | Fire | 16 | [Fire](Stage-Catalog-Fire) |
| 6 | 8 | Bridge | 10 | [Bridge](Stage-Catalog-Bridge) |
| 7 | 9 | Fortress | 9 | [Fortress](Stage-Catalog-Fortress) |
|  |  | **Total** | **84** |  |

The 84 count covers only ordinary `0x30`-byte pickup records. Scripted/special actors such as the Temple Map, boss/cutscene rewards, and Shinnok's Amulet are outside that count unless their owning system explicitly says otherwise.

## Shared catalog schema

Each normalized stage catalog uses the same information layers:

1. **Stage identity and evidence** — native/compact identity plus stage-bounded validation facts.
2. **File mapping** — the stage resource file's file-table entry, clean-ROM range/size, loader flag, verified runtime base, outer-table shape, and pickup count.
3. **Ordinary pickup records** — every concrete `0x30`-byte record for that stage.
4. **Pickup-to-resource usage** — the callback, parameter, selector slot, and presentation pointer used by each ordinary record.
5. **Outer resource slots** — every stock outer-table selector and its decoded format/user count.
6. **Recognized bundle/list records** — every conservatively recognized per-frame record in the stage resource file.
7. **Stage-specific notes, constraints, and pending questions** — facts that must not be generalized to another stage.
8. **Related owners** — links to global architecture/policy pages rather than copied global rules.

All eight stage pages now use this shared normalized schema. Their concrete tables remain authoritative stage-local data.

## Ordinary-pickup terminology

The stable ordinary-record grammar is canonically defined in [Data structures and encodings](Data-Structures-and-Encodings). Catalog tables reproduce the concrete bytes for each stage:

- each record is `0x30` bytes and values are big-endian;
- `+0x00..+0x0F` are destination position/metadata;
- `+0x10..+0x2B` are the seven-word ordinary-item identity slice used by the current stage-local randomizer;
- `+0x24` is a **stage-local resource selector**, not a globally portable resource ID;
- `+0x2C` is the collected flag and belongs to the destination location;
- `Token` and `Requires` are MKMSZR logic metadata, not native record bytes;
- unknown fields stay named by offset rather than receiving guessed semantics.

A stage catalog's `Pickup users` count refers only to its listed ordinary records. Zero ordinary users does not mean that no script, actor, effect, or other subsystem references the resource.

## File, resource, and overlay notation

- **ROM offsets/ranges** refer to bytes in the supported clean USA Rev. 0 `.z64` image. Stage `Resource ROM range` rows preserve the catalog's inclusive last-byte notation; `File size` is the exact byte count.
- **File-table entry ROM** is the ROM location of the file-table entry, not the resource payload itself.
- **Verified runtime base** is a KSEG0/RDRAM virtual address at which the stage resource file was byte-matched in the documented runtime capture. It is not interchangeable with a ROM offset.
- **Outer offset**, `Record`, embedded `Resource/data value`, and inferred embedded-data ends are **file-relative offsets** unless a row explicitly says `external-resource-id`.
- **External resource IDs** are loader/cache identifiers, not ROM offsets or RDRAM addresses and are not assumed portable across stages.
- **Overlay VAs are stage/source-qualified.** The same overlay VA can hold different stage content at different times; global overlay/load rules belong to [Resource and overlay system](ROM-Overlay-and-Resource-Map), and literal runtime-space ownership belongs to [Memory and allocation map](Memory-and-Allocation-Map).

## Outer slots and recognized records

The stage resource file begins with an outer selector table. Catalog slot rows use:

| Field | Meaning |
|---|---|
| Slot | Stock outer-table word index / stage-local selector |
| Outer offset | File-relative descriptor/list offset stored in that outer word; `0` means an empty logical selector |
| Format | Conservatively decoded representation, such as embedded bundle, external-ID bundle/list, or single-record pointer |
| Frames | Number of recognized records/frames for that slot |
| Pickup users | Number of ordinary pickup records in that stage whose `+0x24` selector uses the slot |

Recognized bundle/list rows use file-relative `Record` offsets. For `embedded-data`, the resource/data value is a file-relative payload offset and `Inferred end` is the next discovered model/data boundary used for cataloging. For `external-resource-id`, the value is an external ID and no embedded-data end is implied. Dimension words are preserved raw rather than reinterpreted beyond established structure knowledge.

## Evidence and status notation

The project-wide evidence labels are listed concisely on [Home](Home); [Research workflow](Research-Workflow) owns the methodology for applying them. In stage catalogs:

| Label | Stage-catalog meaning |
|---|---|
| **Runtime-confirmed** | Observed on the stated stage/route in game/emulator; never generalized beyond that route |
| **Static-confirmed** | Established from the clean ROM, source, Ghidra/static analysis, or byte-identical file decoding |
| **Implementation/CI-confirmed** | Established by the patcher/tests, without implying runtime observation |
| **Hypothesis / strong inference** | Supported but not confirmed; must remain visibly qualified |
| **Rejected / failed** | Tested/analyzed and unsuitable within the stated scope |
| **Pending** | Not yet resolved or validated |

The catalog tables are **Static-confirmed** unless a more specific row/section says otherwise. File-to-RDRAM byte matches and pickup/persistence tests are Runtime-confirmed only for their documented stage/route. Catalog completeness does not mean all 84 pickups have been individually collected in runtime testing.

## Shared safety and interpretation boundaries

These rules apply to all eight catalogs and are not repeated in normalized child pages:

- a zero outer-table entry is a free **logical selector** only; it is not proof of unused physical bytes in the original file;
- an occupied slot with no ordinary-pickup user remains protected until other actor/script/resource references are resolved;
- inferred embedded-data ends are analysis boundaries, not proof that trailing bytes are independently movable;
- foreign resources require bounded storage, loader/arena validation, guarded references, production-composition checks where applicable, and runtime testing;
- a stage-relative selector/resource conclusion must not be generalized to another stage;
- a proof-era resource placement or extension selector is not automatically a production allocation.

General extension-selector/materializer rules and proof chronology belong to [Global item materialization and solvability](Global-Item-Materialization-and-Solvability), not to the stage catalogs.

## Catalog completeness and lineage

Across the eight pages:

- all 84 ordinary records and every raw word are listed;
- production logic tokens/location requirements are shown alongside native bytes where applicable;
- all eight stage resource-file ROM ranges and verified runtime bases are recorded;
- every stock outer selector is classified as empty, recognized, or explicitly unknown/nonstandard;
- recognized bundle/list records preserve frame, descriptor offset, storage kind, data/resource value, inferred end where applicable, and dimension words.

The catalogs were generated from the preserved clean-ROM catalog artifacts and checked against the production pickup definitions in `src/mkmszr/data/pickups.py`. The Wiki reproduces the decoded tables so current technical facts do not depend on an external archive.

## Global owners and related references

- [Data structures and encodings](Data-Structures-and-Encodings) — canonical ordinary-record and stable structure grammar.
- [Resource and overlay system](ROM-Overlay-and-Resource-Map) — file table, loaders, overlay identity, selector/resource grammar, and packaging rules.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership, lifecycle, aliases, and proof/production allocation boundaries.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded ROM edit sites and expected bytes.
- [Pickups and stage-local randomization](Pickups-and-Item-Randomization) — current production same-stage pickup behavior.
- [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) — global pool/materializer/solver rules, extension-selector mechanism, and Temple Map policy question.
- [Persistence, inventory, and lifecycle](Persistence-Inventory-and-Lifecycle) — collected-state persistence, inventory masking, and run-lifecycle behavior.
- [Runtime validation status](Runtime-Validation-Status) — concise cross-domain runtime evidence matrix.
