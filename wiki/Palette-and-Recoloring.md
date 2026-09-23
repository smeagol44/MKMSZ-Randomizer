# Palette and recoloring

> **Scope:** This page owns MKMSZR's production player-outfit recoloring behavior, the stable MKMSZ palette/TLUT facts needed by that product feature, and the current palette-configuration boundaries.
>
> Donor-fighter palette conversion and actor-specific palette compatibility are canonical in [MKT fighter asset translation](MKT-Fighter-Asset-Translation). Version-specific Sektor palette proofs, including v60, are canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current production behavior

Sub-Zero's guarded clean-ROM palette record begins at ROM `0x0078E168`; the 64 color entries begin at `0x0078E16C`. The production recolor changes only the clothing range, palette indices `0x21..0x3F`.

MKMSZ source colors are BGR555 halfwords. Production preserves the high control/alpha bit and transforms only the five-bit color channels for the clothing entries. Entries outside the configured clothing range remain untouched.

Supported product modes are:

- vanilla;
- named presets;
- legacy red/green;
- seed-derived hue;
- explicit hue;
- explicit RGB.

The source-palette transformation is **Runtime-confirmed** across multiple modes. Unit coverage checks bounds, channel conversion, determinism, and preservation of untouched entries.

## Stable palette / TLUT boundary

The clean-ROM source palette is the stable patching reference. An active runtime TLUT was observed at `0x803BD410` in one proof, but that runtime address is stage/timing dependent and must not replace the stable ROM mapping.

The production recolor is therefore a guarded source-data transformation, not a claim that one fixed runtime TLUT address is globally valid.

Donor-fighter work has established additional palette-binding rules for imported 5-bpp assets and alternate actor palettes. Those conclusions do not redefine the production recolor contract and are maintained in [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

## Configuration and determinism boundaries

Palette RNG is isolated from pickup and boot-phrase namespaces. Changing presentation/recolor options must not change item placement.

The current product feature configures the normal player outfit. It does not claim a general per-actor palette allocator, automatic conversion of arbitrary donor palettes, or coverage of every alternate/enemy palette route. Those are separate compatibility problems.

## Safety constraints

- Transform only the guarded supported-ROM source palette and the configured clothing indices.
- Preserve the source word's high control/alpha bit.
- Do not treat a runtime TLUT address observed in one route as a stable global patch site.
- Do not reuse donor palette words directly without the explicit donor-to-MKMSZ channel/order conversion owned by the fighter-asset adapter.
- Presentation RNG changes must remain isolated from gameplay/randomizer RNG namespaces.

## Related pages

- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) — donor palette conversion, binding, whole-character TLUT strategy, and stable alternate-palette compatibility conclusions.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — version-specific Sektor palette proof evidence, including v60 identities, patch window, route, and bounded runtime result.
- [Data structures and encodings](Data-Structures-and-Encodings) — normative image/codec structures.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and proof-vs-production allocation boundaries.
