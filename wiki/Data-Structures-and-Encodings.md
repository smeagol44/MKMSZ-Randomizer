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

N64 source colors are 16-bit BGR555 values with a preserved high control/alpha bit. Sub-Zero's 64-color source TLUT begins at ROM `0x78E16C`; clothing entries are indices `0x21..0x3F`. Transform only those indices unless a different palette has been independently mapped.
