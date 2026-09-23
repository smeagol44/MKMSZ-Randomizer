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

## Rainbow runtime proof

**Runtime-confirmed on 2026-09-23; proof-only, not yet a product mode.**

Disposable full-composition proof:

- file: `MKMSZR_rainbow-outfit_full-proof_v01.z64`;
- SHA-256: `4f9aff72c3f81d20e7f3d8f3e59f07cff8f7c6e5a1c0ce81d1a1bbb91ab92060`;
- CRC1/CRC2: `E0AD24EF / 4993529C`;
- seed: `RAINBOW64`.

The proof composes the current production randomizer systems while excluding Sektor and unrelated proof-only experiments. The user reported the requested manual rainbow/regression test worked successfully.

The rainbow path keeps the established clothing boundary: only palette indices `0x21..0x3F` vary. It precomputes 64 full BGR555 palettes distributed around the hue wheel; every non-clothing entry is preserved exactly from the stock Sub-Zero palette in every generated palette.

Unlike the production static recolor, the proof is a runtime palette feature. It hooks native fighter frame setup at `0x8001BDA0`, applies only to normal Sub-Zero fighter type `4`, and uses the native palette allocation/refcount path so the actor is rebound coherently before the prior palette handle is released. This deliberately avoids treating the route-specific observed TLUT address `0x803BD410` as a stable global write target.

Proof-only composition details:

- the existing 1 KiB MKMSZR reservation remains `0x801AF420..0x801AF81F`, but is repartitioned for this artifact as `0x3B0` bytes of code plus `0x50` bytes of state;
- rainbow phase state uses proof state offset `+0x48`;
- the rainbow helper occupies cached `0x801AF700` / uncached `0xA01AF700`, size `0xCC`;
- clean Sub-Zero file `0x87` is relocated byte-for-byte to ROM `0xF20000..0xF679DF`, then extended with the 64-palette bank; final file size is `0x479E0`.

This runtime result establishes feasibility and the tested composition only. It does **not** by itself promote the proof repartition or high-ROM relocation to production ownership. Browser/CLI exposure remains pending a guarded production integration.

## Related pages

- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) — donor palette conversion, binding, whole-character TLUT strategy, and stable alternate-palette compatibility conclusions.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — version-specific Sektor palette proof evidence, including v60 identities, patch window, route, and bounded runtime result.
- [Data structures and encodings](Data-Structures-and-Encodings) — normative image/codec structures.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ROM/RDRAM ownership and proof-vs-production allocation boundaries.
