# Data structures and encodings

## Ordinary pickup record (`0x30` bytes)

| Offset | Size | Meaning | Randomized? |
|---:|---:|---|---|
| `+0x00` | 4 | X position | No |
| `+0x04` | 4 | Y position | No |
| `+0x08` | 4 | Z position | No |
| `+0x0C` | 4 | Location metadata | No |
| `+0x10` | 4 | Type/behavior | Yes |
| `+0x14` | 4 | Callback parameter/flags | Yes |
| `+0x18` | 4 | Native award callback | Yes |
| `+0x1C` | 4 | Collision extent A | Yes |
| `+0x20` | 4 | Collision extent B | Yes |
| `+0x24` | 4 | Stage-local resource selector | Yes |
| `+0x28` | 4 | Presentation descriptor | Yes |
| `+0x2C` | 4 | Collected flag | No; persisted separately |

The production identity is the contiguous 28-byte slice `+0x10..+0x2B`. Copying only callback/type is insufficient for correct art and behavior. There are exactly 84 ordinary records: Temple 4, Wind 6, Water 9, Earth 20, Prison 10, Fire 16, Bridge 10, Fortress 9.

## Persistence state V2 (`0x100` bytes)

Production V2 lives at `0x801AF720..0x801AF81F`.

| Offset | Meaning |
|---:|---|
| `+0x00` | Magic `MKSV` = `0x4D4B5356` |
| `+0x04` | Version `2` |
| `+0x08` | Total size `0x100` |
| `+0x0C` | Header size `0x20` |
| `+0x10` | Flags |
| `+0x14..+0x1F` | Reserved |
| `+0x20` | Temple ordinary-pickup bitset |
| `+0x24` | Wind |
| `+0x28` | Water |
| `+0x2C` | Earth |
| `+0x30` | Prison |
| `+0x34` | Fire |
| `+0x38` | Bridge |
| `+0x3C` | Fortress |
| `+0x40` | Progression rewards acquired, 0..9 |
| `+0x44` | Persistent progression XP |
| `+0x48..+0xFF` | Reserved |

Fire's 19 manager ordinals translate to catalog bits as:

```text
[2, 5, 4, FF, FF, FF, 9, 14, 0, 1, 8, 11, 12, 3, 7, 6, 10, 13, 15]
```

`FF` ordinals `3`, `4`, and `5` are special type-4 records and intentionally excluded. Progression count/XP are separate from these 84 ordinary-pickup persistence bits.

## Four-box inventory layout

| Address | Words | Meaning |
|---:|---:|---|
| `0x800A600C` | 10 | Live stock inventory window |
| `0x800A6048` | 10 | Box 1 backing |
| `0x800A6070` | 10 | Box 2 backing |
| `0x800A6098` | 10 | Box 3 backing |
| `0x800A60C0` | 10 | Box 4 backing |
| `0x800A60E8` | 1 | Active index and input latch |
| `0x800A60EC` | 1 | `MKBX` magic |

Empty stock slots use `0xFFFFFFFF`. Foreign-stage keys appear in the live window as item `0x08` only; the true item remains in backing storage.

## Key-to-stage mapping

| IDs | Origin stage |
|---|---|
| `0x0D` | Temple Map |
| `0x0E..0x10` | Wind |
| `0x11..0x13` | Earth |
| `0x14..0x16` | Water |
| `0x17..0x19` | Fire |
| `0x1A..0x1C` | Prison |
| `0x1D..0x1F` | Bridge |
| `0x20..0x22` | Fortress crystals |
| `0x23` | Shinnok Amulet; special pickup path |
| `0x24` | Tablet; rejected as a safe mask because it is consumable |

## Ordinary-enemy stream

Streams are big-endian 32-bit words, terminated by `0x0000FFFF`, and dispatched for opcodes `0..9` by table `0x800AD7A0`. Common spawn opcodes `0`, `1`, and `9` occupy `0x1C` bytes:

| Offset | Meaning |
|---:|---|
| `+0x00` | Opcode |
| `+0x04` | Raw X; stored as `-(value << 8)` at process `+0x714` |
| `+0x08` | Raw Y; stored as `-(value << 8)` at process `+0x718` |
| `+0x0C` | Raw Z; stored as `value << 8` at process `+0x6F4` |
| `+0x10` | Low 16-bit fighter type; process `+0x6FC` |
| `+0x14` | Low 16-bit remaining/spawn quota |
| `+0x18` | Low signed 16-bit activation/proximity mode |

Opcode `6` is `0x20` bytes: a mask at `+0x04` is tested against `0x802C1140`, then the same six fields occupy `+0x08..+0x1C`. The stream record ordinal indexes eight-byte state at `0x801AE720 + ordinal*8`. Opcodes `3`, `4`, `7`, and `8` set concurrency/count, cooldown, auxiliary `+0x704`, and flag `+0x6F8`; opcode `5` exits. Complete gameplay names for opcodes `1`, `2`, and `9` remain unresolved.

## Auxiliary trigger record (`0x3C` bytes)

The stage overlay scans these at `0x801114F4`, count `0x802E8228`. Center/edge coordinates are at `+0x00/+0x04/+0x08`, extents at `+0x0C/+0x10`, state at `+0x14`, flags/opcode at `+0x18`, and subtype arguments from `+0x1C`. They are activation/script volumes, not the primary ordinary-enemy list.

## Native UI render node (`0x58` bytes)

The node is 22 words. Four vertex X/Y pairs occur at `+0x08/+0x0A`, `+0x18/+0x1A`, `+0x28/+0x2A`, and `+0x38/+0x3A`; per-vertex RGBA words are at `+0x14`, `+0x24`, `+0x34`, and `+0x44`. Allocation is `0x8002018C` and submission is `0x8001EAE4`.

## BGR555 palettes

N64 source colors are 16-bit BGR555 values with a preserved high control/alpha bit. Sub-Zero's 64-color source TLUT begins at ROM `0x78E16C`; clothing entries are indices `0x21..0x3F`. Those indices define the mapped clothing-transform range; other palettes require independent mappings.


## Native fighter image type 5

**Static-confirmed.** Stock Sub-Zero fighter frames in global file ID `0x87` predominantly use a dedicated native fighter codec selected by exact image header `0x05000000`. This is distinct from ordinary embedded-image type 4 and explains why the rejected v13 pickup-style type-4 fighter experiment was not a faithful stock-fighter storage path.

The type-5 wrapper is:

| Offset | Meaning |
|---:|---|
| `+0x00` | exact header `0x05000000` |
| `+0x04` | signed image-relative pointer to the type-5 model/dictionary table |
| `+0x08` | packed decode dimensions, high 16 bits height / low 16 bits width |
| `+0x0C` | compressed bitstream |

`0x80003314` resolves the table pointer and calls `0x80065E00`. The output arena reservation is `align4(width) * align2(height)`.

The table begins with `u16 rows_per_block` and `u16 model_count`, followed by 104-byte model entries. Stock Sub-Zero's main table at file-0x87 offset `+0x14AC` begins `0002 0004`: 2 rows per block and four models. A model contains a pattern-table relative offset, bits-per-pixel, 13 normal-code extra-bit counts, three zero-run extra-bit counts, 13 pattern-index bases, and three zero-run bases.

The decoder consumes the stream MSB-first. The first 6 bits select the model. Each output unit is a `rows_per_block x 4` pixel block; stock fighter data uses two rows, so ordinary blocks are 2x4 pixels. A 4-bit symbol below 13 selects a normal pattern-index class; symbols 13..15 encode transparent block runs. Pattern entries store the 2x4 pixel indices packed at the selected model's bit depth.

This format is now the preferred compact-storage target for Sektor.

Generated Sektor encoder v2 is **Implementation-confirmed** to use more of the native grammar: nontransparent 2x4 patterns are frequency-ordered into multiple normal classes using stock-compatible extra-bit/base tables, while symbols `13..15` encode transparent-block runs as `zero_base + extra + 1` blocks. The build independently decodes every emitted stream and requires exact equality with the donor-decoded aligned pixel buffer before a proof ROM is written. v46 is the first runtime-pending composition using these wider generated-code paths. A simple offline proof encoder can use a one-model, 5-bits-per-pixel dictionary because the imported Sektor palette indices are `0..31`. Runtime validation of such generated type-5 data is still pending.


### Stock Sub-Zero Type-5 recompression benchmark

**Static/implementation-confirmed.** The clean USA Rev 0 file ID `0x87` contains 341 stock Type-5 fighter frames sharing the table at file offset `+0x14AC`. Their Type-5-owned region runs from the shared table through the final frame at `+0x41684`.

The 341 frames decode to exactly **1,418,312 raw indexed-pixel bytes**. Stock Midway storage for the same corpus is:

- shared table/dictionaries: **112,636 bytes**;
- padded compressed streams: **139,068 bytes**;
- shape/descriptor/wrapper overhead: **10,912 bytes**;
- total: **262,616 bytes** (`0x401D8`), equivalent to about **5.4007x** reduction versus the decoded pixels.

The project encoder-v2 strategy was then generalized to the stock four-model arrangement and run on the exact same decoded pixels. The benchmark preserves each frame's stock model assignment and each stock model's normal/zero-run class widths, but rebuilds frequency-ordered dictionaries containing only patterns actually used by the 341-frame corpus. Result:

- generated shared table/dictionaries: **111,878 bytes**;
- generated padded compressed streams: **139,008 bytes**;
- identical shape/descriptor/wrapper overhead: **10,912 bytes**;
- generated total: **261,798 bytes** (`0x3FEA6`), about **5.4176x** reduction.

The generated result is **818 bytes (0.311%) smaller than stock Midway** for the exact same decoded artwork. Stream coding itself is essentially at parity: generated streams use only 466 fewer bits across all 341 frames. Most of the measured win comes from omitting 128 stock dictionary patterns not used by this scanned Type-5 corpus.

This benchmark does **not** mean the current Sektor resource layout is already globally optimal. The Sektor proof builders still partition frames into multiple generated dictionaries/tables for bounded integration, so duplicate patterns and per-group model overhead remain. The benchmark instead shows that the native Type-5 grammar and encoder-v2 coding strategy are no longer the main compression gap. The remaining high-value work is model/dictionary grouping, cross-animation pattern sharing, dead-stock reclamation, and whole-resource packing.

Reproducible tool: `tools/benchmark_type5_encoder.py`.


### Shared-dictionary multi-model packing

**Static/implementation-confirmed in v54.** Type-5 model records do not require distinct physical pattern arrays. Multiple model records may use the same pattern-table relative offset while carrying independent normal-class widths/bases and transparent-run classes. The first 6 stream bits select the entropy model; pattern indices then resolve through that model's bases into the shared physical dictionary.

The optimized Sektor v54 uses **16 model records over one shared 5-bpp dictionary**. Splitting the 129 inherited v53 frames into smaller entropy groups reduces stream bits enough to retain seven flattened Throw keyframes while keeping file ID `0x87 = 0x4E154`, below the runtime-confirmed Fortress-working v49 footprint. Independent software decode verifies every emitted frame against its exact source pixels. This is a packing optimization only; it does not alter the Type-5 pixel grammar or visible artwork.


### Type-5 zero-bit normal-class compatibility boundary

**Strong inference from v54 runtime failure; guarded in v55.** v54 Sweep Fall hard-hung after its second visible pose. Static tracing places the next pose in the first generated model on that action path whose normal-pattern class table contains a **0-bit** width. Stock/runtime-confirmed generated layouts had not established zero-bit normal classes as native-decoder-safe.

v55 therefore treats `normal_bits >= 1` as a compatibility requirement for generated fighter Type-5 models. Its optimizer searches class widths from 1 through 16 bits and asserts the constraint across all 52 emitted model records. This is deliberately stronger than the software decoder requires. The causal link remains a strong inference until v55 Sweep Fall is runtime-tested successfully.

### PS1 MKT POVBQ supplemental conversion

**Static/implementation-confirmed in v55.** PS1 MKT `CHARS1/ROBOT.DAT` stores the ordinary robot Run bank through the POVBQ path rather than the N64 fighter representation. v55 decodes the required PS1 frames offline, using their 12-byte descriptors, padded width, palette ID, shared POVBQ table, 6-bit model selector, seven normal symbols, and two transparent-run symbols. The decoded indexed pixels are then palette-converted and encoded into MKMSZ native Type-5; PS1 compressed bytes are never copied directly into N64 resources.

For the six even Run poses absent from MKT N64, the final shared Sektor dictionary requires only **18 supplemental 2x4 patterns**. After those are admitted, the palette-converted PS1 target buffers are represented exactly: zero color-space RMSE and 100% exact opaque indices. v55's final shared dictionary contains 40,595 patterns and is addressed by 52 Type-5 entropy models.
