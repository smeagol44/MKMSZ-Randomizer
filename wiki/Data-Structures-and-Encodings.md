# Data structures and encodings

> **Scope:** This page is the canonical owner for stable, version-independent record layouts, structure grammar, target codecs, and encoding constraints. Donor-fighter descriptors, palette conversion, Sektor encoder benchmarks, supplemental donor history, and fighter-resource packing belong to [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

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

## Persistence state V2 (`0x50` bytes)

Production V2 lives at `0x801AF7D0..0x801AF81F`.

| Offset | Meaning |
|---:|---|
| `+0x00` | Magic `MKSV` = `0x4D4B5356` |
| `+0x04` | Version `2` |
| `+0x08` | Total size `0x50` |
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
| `+0x48` | Rainbow phase word; used only by the `rainbow` outfit mode |
| `+0x4C` | Reserved |

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
| `0x800A60E8` | 1 | Active index, input latch, and GAME SETTINGS bits: `0x0200` TURN=LOCK, `0x0400` COMBOS=ASSIST, `0x0800` SPECIALS=MODERN, `0x1000` JUMP=BUTTON |
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

## Player locomotion controller/actor fields

**Static-confirmed for the normal player locomotion path.** These offsets are fields in reusable engine structures, so meanings below are lifecycle-qualified rather than universal labels for every process.

| Structure / offset | Locomotion meaning |
|---|---|
| controller `+0x638` | Pointer to semantic input; player construction stores `0x800BF2EE` here |
| controller `+0x650` | Token-`0x10` companion actor pointer for paired animation; set on creation, retained when the actor is parked through actor `+0x64 bit 0x20`, and reused when the bit is cleared by the next token. Fresh player-controller initialization zeros this field; stage-wide teardown remains unresolved. |
| controller `+0x68C` | Active horizontal semantic direction: `0x8000` Left or `0x2000` Right |
| controller `+0x680` | During normal walk setup, shadows the temporary `1`/`2` locomotion selector before `+0x6E4` becomes the animation cursor |
| controller `+0x6BC` bit `0x0200` | Shared fighter face-policy flag used by several host routines to conditionally face a nearest opponent; **not a universal boss bit** |
| controller `+0x6E0` | Current actor pointer |
| controller `+0x6E4` | Animation cursor; temporarily receives the forward/back selector immediately before animation selection |
| controller `+0x6E8` | Texture-slot ID copied to token-`0x10` companion actor `+0x9C`; no separate slot allocation was found in that token path. |
| controller `+0x6FC` | Normal locomotion mode written as `1` by forward setup and `2` by backward setup |
| controller `+0x704` | In normal horizontal entry, direction-vs-facing mismatch: `0` means forward-compatible, `0x10` means requested direction opposes facing |
| actor `+0x78` | Fighter type |
| actor `+0x8C` bit `0x10` | Horizontal facing bit; clear corresponds to right-facing and set to left-facing in the normal locomotion classifier |

The ordinary player classifier at `0x80029200..0x800292C8` derives `+0x704` without searching for a target: Right stores the actor facing bit directly, while Left stores it XOR `0x10`. This makes the field a ready-made world-direction/facing mismatch signal for control-assist work.

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

## Native image dispatch

**Static-confirmed.** MKMSZ image decoder `0x8000322C` selects the compression type from header byte `+3` (the low byte of the big-endian header word), masked with `0x3F`.

- Type `0` is raw and returns `src + 4`; a type-0 wrapper therefore requires the low header byte to remain zero.
- Fighter type `5` uses exact header `0x05000000` and dispatches through `0x80003314 -> 0x80065E00`.
- Type `5` is distinct from ordinary embedded-image type `4`.

Donor-specific source codecs and conversion pipelines are documented in [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

## Native fighter image type 5

**Static-confirmed; generated fighter use is Runtime-confirmed on bounded Sektor proof routes.** Stock Sub-Zero fighter frames in global file ID `0x87` predominantly use native image type `5`.

The type-5 wrapper is:

| Offset | Meaning |
|---:|---|
| `+0x00` | Exact header `0x05000000` |
| `+0x04` | Signed image-relative pointer to the type-5 model/dictionary table |
| `+0x08` | Packed decode dimensions, high 16 bits height / low 16 bits width |
| `+0x0C` | Compressed bitstream |

`0x80003314` resolves the table pointer and calls `0x80065E00`. The output arena reservation is `align4(width) * align2(height)`. A fighter's visible descriptor dimensions may remain unpadded while the type-5 backing buffer uses decoder-aligned dimensions.

The table begins with `u16 rows_per_block` and `u16 model_count`, followed by 104-byte model entries. Stock Sub-Zero's main table at file-`0x87` offset `+0x14AC` begins `0002 0004`: two rows per block and four models. A model contains:

- a pattern-table relative offset;
- bits per pixel;
- 13 normal-code extra-bit counts;
- three zero-run extra-bit counts;
- 13 pattern-index bases;
- three zero-run bases.

The decoder consumes the stream MSB-first. The first 6 bits select the model. Each output unit is a `rows_per_block x 4` pixel block; stock fighter data uses two rows, so ordinary blocks are `2x4` pixels. A 4-bit symbol below 13 selects a normal pattern-index class. Symbols `13..15` encode transparent-block runs. Generated streams use the zero-run relation `zero_base + extra + 1` blocks. Pattern entries store the block's palette indices packed at the selected model's bit depth.

### Stable generation and packing constraints

- Multiple model records may point to the same physical pattern table while retaining independent normal-class widths/bases and transparent-run classes. The model selector, not physical dictionary duplication, defines the entropy model.
- Generated fighter shapes must begin on a 4-byte boundary. Unaligned generated shape records are known unsafe.
- MKMSZR generated-fighter encoders currently require every normal-pattern class width to satisfy `normal_bits >= 1`. Zero-bit normal classes are not established as native-decoder-safe; the guarded requirement is intentionally stronger than the software decoder alone requires.
- For lossless generated assets, the build independently decodes every emitted stream and requires exact equality with the selected aligned indexed-pixel target buffer before writing the proof ROM.
- Decode dimensions, visible fighter dimensions, and source-row storage pitch are separate concepts and must not be conflated.

Sektor-specific encoder benchmarks, donor conversion history, palette binding, proof-version storage results, and whole-resource packing policy are owned by [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

## Dynamic gameplay texture-slot record

**Static-confirmed for the fields below.** Dynamic texture IDs `0x200..0x2FF` index 16-byte records at `0x802E83F0 + id*0x10`; backing pointers are stored separately at `0x800ED940[id]`.

| Offset | Meaning | Evidence |
|---:|---|---|
| `+0x00` | format/flags word used by `0x8001F7A8` to choose texture-load path | Static-confirmed |
| `+0x04` | backing-capacity width used by `0x8001C2B4` reuse-fit checks | Static-confirmed |
| `+0x06` | backing-capacity height used by reuse-fit checks | Static-confirmed |
| `+0x08` | current DRAM source-image width; consumed by `0x8001F7A8` when emitting RDP `SetTextureImage` | Static-confirmed |
| `+0x0A` | image/allocation height field; exact downstream ownership beyond allocator bookkeeping is not yet fully cataloged | Static-confirmed field write; semantics bounded |
| `+0x0C` | reuse/lifecycle field; exact semantic name Pending | Static-confirmed as part of allocator reuse eligibility |
| `+0x0E` | active flag; `1` means active | Static-confirmed |

For a new dynamic allocation, `0x8001C2B4` rounds requested width up to 32 before allocating backing storage and initially writes that aligned width to both `+0x04` and `+0x08`. Its reuse path can return an inactive record whose `+0x04/+0x06` capacity is sufficient **without updating `+0x08`**. Stock image-building callers therefore rewrite `record+0x08` after allocation with the source image's actual DRAM row width. Toasty v23-v37 omitted that caller-owned initialization; see [Toasty visual research](Toasty-Visual-Research).
