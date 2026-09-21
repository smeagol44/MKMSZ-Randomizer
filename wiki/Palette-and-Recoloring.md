# Palette and recoloring

Sub-Zero's clean-ROM palette record begins at ROM `0x0078E168`; the 64 color entries begin at `0x0078E16C`. Clothing occupies indices `0x21..0x3F`.

Colors are BGR555 halfwords. Production preserves the high control/alpha bit and transforms only the five-bit color channels for the clothing range. Supported modes include vanilla, named presets, legacy red/green, seed-derived hue, explicit hue, and explicit RGB.

The active runtime TLUT was observed at `0x803BD410` in one proof, but that address is stage/timing dependent and must not replace the stable ROM source mapping. The source palette transformation is runtime-confirmed across multiple modes and covered by unit tests for bounds, channel conversion, determinism, and untouched entries.

Palette RNG is isolated from pickup and boot-phrase namespaces. Changing presentation options must not change item placement.


## Sektor takeover: first Scorpion alternate palette (v60)

**Runtime-confirmed on 2026-09-21.**

The first visible `SCORPION` / fighter type `0x12` is a Sub-Zero-family actor using an alternate palette, not the separate genuine Undead Scorpion/type-`0x11` resource. Under the v59 Sektor takeover, the transplanted fighter images are 5-bpp and therefore use only palette indices `0..31`. The normal player palette had already been replaced with Sektor's native lower-32 TLUT, but the type-`0x12` alternate palette still contained the stock ninja colors, so the same Sektor pixels were interpreted through the wrong colors.

v60 (`MKMSZR_scorpion-cyrax-palette_common-proof_v60.z64`) is an in-place palette-only proof built directly from the runtime-confirmed v59 ROM. In the relocated file-`0x87` image used by this proof, the alternate palette's lower 32 entries are at file-relative `+0x458D0`, ROM `0xF858D0`. v60 replaces that 64-byte lower-half TLUT with a Cyrax-style Sektor palette: armor entries `1..15` use a yellow/gold ramp derived from MKMSZ's Scorpion yellow family, while Sektor's gray/black metal entries `16..31` are preserved exactly in the target palette.

Static scope verification:
- input v59 SHA-256: `b8b1ddfa964de4da86dc9598f99139f4c50ac066deaaf4ab5cd91fda63baf1cc`;
- output v60 SHA-256: `caebb133e7ea759e5f115d169fe84f00d4120caa6545373b28983fd8efde048b`;
- exactly 62 bytes differ, all inside the single 64-byte alternate-palette window;
- file `0x87` size is unchanged at `0x4E3FC`;
- recalculated CRC1/CRC2 remain `A6256DD8 / DB8E6E81` because this proof patch lies outside the CIC-6102 CRC-covered ROM range.

Runtime result: the user reported the first Scorpion renders correctly as the intended yellow/gold Cyrax-style robot. This confirms only that first type-`0x12` alternate-palette route; no claim is made here for Undead Scorpion/type-`0x11` or arbitrary enemy palettes.
