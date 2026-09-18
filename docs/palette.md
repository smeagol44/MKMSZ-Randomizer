# Sub-Zero outfit palette

The confirmed 64-color source palette begins at ROM `0x0078E16C`. Clothing uses
entries `0x21..0x3F`; grayscale/black and skin ranges are intentionally untouched.

The source words behave as BGR555-style values: red in bits 0..4, green in 5..9,
blue in 10..14, with bit 15 preserved.

`red` and `green` reproduce the exact channel swaps already confirmed in-game.
`hue`, named presets, and `rgb` preserve the original shading ramp. `seeded`
derives a hue from a namespaced SHA-256 seed, so cosmetic selection does not consume
the gameplay randomizer RNG stream.

```bash
mkmszr clean.z64 test-green.z64 --outfit green
mkmszr clean.z64 test-purple.z64 --outfit purple
mkmszr clean.z64 test-custom.z64 --outfit rgb --rgb FF4FA3
mkmszr clean.z64 test-seeded.z64 --seed BCBDBF --outfit seeded
```

All currently exposed browser color modes have now been visually tested in BizHawk:
red, green, purple, orange, yellow, cyan, pink, seed-derived hue, and custom RGB.
The recolored clothing renders correctly while preserving the intended shading ramp
and leaving skin/black clothing regions unaffected.

This validates the exposed transformation modes, not every possible arbitrary RGB
value or every hue in the continuous color space.
