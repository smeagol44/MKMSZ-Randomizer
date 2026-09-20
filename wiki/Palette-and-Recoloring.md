# Palette and recoloring

Sub-Zero's clean-ROM palette record begins at ROM `0x0078E168`; the 64 color entries begin at `0x0078E16C`. Clothing occupies indices `0x21..0x3F`.

Colors are BGR555 halfwords. Production preserves the high control/alpha bit and transforms only the five-bit color channels for the clothing range. Supported modes include vanilla, named presets, legacy red/green, seed-derived hue, explicit hue, and explicit RGB.

The active runtime TLUT was observed at `0x803BD410` in one proof, but that address is stage/timing dependent and must not replace the stable ROM source mapping. The source palette transformation is runtime-confirmed across multiple modes and covered by unit tests for bounds, channel conversion, determinism, and untouched entries.

Palette RNG is isolated from pickup and boot-phrase namespaces. Changing presentation options must not change item placement.
