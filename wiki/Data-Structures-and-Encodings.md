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
| `+0x14` | 4 | Callback parameter/flags. Low 15 bits are passed to the callback; bit `0x8000` is a destination-record activation gate consumed by the pickup manager and masked before callback dispatch. | Yes |
| `+0x18` | 4 | Native award callback | Yes |
| `+0x1C` | 4 | Collision extent A | Yes |
| `+0x20` | 4 | Collision extent B | Yes |
| `+0x24` | 4 | Stage-local resource selector | Yes |
| `+0x28` | 4 | Presentation descriptor | Yes |
| `+0x2C` | 4 | Collected flag | No; persisted separately |

The production identity is the contiguous 28-byte slice `+0x10..+0x2B`. Copying only callback/type is insufficient for correct art and behavior. There are exactly 84 ordinary records: Temple 4, Wind 6, Water 9, Earth 20, Prison 10, Fire 16, Bridge 10, Fortress 9.

**Bit-15 ownership (Static-confirmed, 2026-10-01):** pickup-manager setup reads raw `+0x14 & 0x8000` before actor activation, while callback dispatch at `0x800393BC..0x800393D0` masks the parameter with `0x7FFF`. Bridge stage scripts later clear this bit on dynamically activated Omega/Rings/Arrow/Health records, and Fortress boss reward activation uses the same record-level mechanism. Therefore bit 15 belongs to the **physical destination record**, not to the logical reward callback. A cross-stage materializer must preserve the destination's stock bit-15 state independently of the assigned reward.

## Persistence state V2 (`0x50` bytes)

Production V2 lives at `0x801AF7D0..0x801AF81F`.

| Offset | Meaning |
|---:|---|
| `+0x00` | Magic `MKSV` = `0x4D4B5356` |
| `+0x04` | Version `2` |
| `+0x08` | Total size `0x50` |
| `+0x0C` | Header size `0x20` |
| `+0x10` | Flags; bit `0x0001` = Temple scripted special check collected |
| `+0x14..+0x1F` | Lifecycle-v06 HP/reason/current-resource snapshots (specific fields/validation owned by the Persistence and Lifecycle page); no longer unused reserved storage |
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
| `+0x4C` | Reserved persistent-state word with temporary GAME SETTINGS editor use at `0x801AF81C` while editing; not free storage |

Fire's 19 manager ordinals translate to catalog bits as:

```text
[2, 5, 4, FF, FF, FF, 9, 14, 0, 1, 8, 11, 12, 3, 7, 6, 10, 13, 15]
```

`FF` ordinals `3`, `4`, and `5` are special type-4 records and intentionally excluded. Progression count/XP and the Temple scripted-check header flag are separate from these 84 ordinary-pickup persistence bits.

## Four-box inventory layout

| Address | Words | Meaning |
|---:|---:|---|
| `0x800A600C` | 10 | Live stock inventory window |
| `0x800A6048` | 10 | Box 1 backing |
| `0x800A6070` | 10 | Box 2 backing |
| `0x800A6098` | 10 | Box 3 backing |
| `0x800A60C0` | 10 | Box 4 backing |
| `0x800A60E8` | 1 | Active index bits `0..1`, input latch bit `0x0100`, and five durable GAME SETTINGS flags: `0x0200` TURN=LOCK, `0x0400` ATTACK=MODERN, `0x0800` SPECIALS=MODERN, `0x1000` JUMP=BUTTON, `0x2000` RUN=AUTO. Current accepted five-setting frontend replaces the old COMBOS label; see Persistence/Inventory lifecycle for prerequisite behavior. |
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
| controller `+0x68C` | Active horizontal semantic direction: `0x8000` Left or `0x2000` Right |
| controller `+0x680` | During normal walk setup, shadows the temporary `1`/`2` locomotion selector before `+0x6E4` becomes the animation cursor |
| fighter process `+0x6B2` | Signed halfword action/physics-in-progress state. Ordinary enemy `0x80071B20` zero-fills `+0x638..+0x6D7` before actor construction; `0x800321D0` clears it at entry, increments it before each sleep/animation iteration, then clears it at exit. `0x80032580`, `0x80033BB4`, `0x800341AC`, and other shared callbacks can set it to `1` for bounded loops. `0x8002B690` maps nonzero to `0x8000`, zero to `0x4000`; reaction transfer `0x8002E078/0x80032CD4` leaves this halfword intact. Its value is process-owned, not actor `+0x98` animation-root data. Ordinary slots `0x71..0x74` normalize to process classes `2..5`; the normal collision scan selects classes `2..4` as victims. A Slide reaction `0x2D` reaches `0x800321D0` on such a victim and creates a nonzero interval, although a later reaction-`0` overlap remains unproved. |
| controller `+0x6BC` bit `0x0200` | Shared fighter face-policy flag used by several host routines to conditionally face a nearest opponent; **not a universal boss bit** |
| controller `+0x6E0` | Current actor pointer |
| controller `+0x6E4` | Animation cursor; temporarily receives the forward/back selector immediately before animation selection |
| controller `+0x6FC` | Normal locomotion mode written as `1` by forward setup and `2` by backward setup |
| controller `+0x704` | In normal horizontal entry, direction-vs-facing mismatch: `0` means forward-compatible, `0x10` means requested direction opposes facing |
| actor `+0x78` | Fighter type |
| actor `+0x8C` bit `0x10` | Horizontal facing bit; clear corresponds to right-facing and set to left-facing in the normal locomotion classifier |

The ordinary player classifier at `0x80029200..0x800292C8` derives `+0x704` without searching for a target: Right stores the actor facing bit directly, while Left stores it XOR `0x10`. This makes the field a ready-made world-direction/facing mismatch signal for control-assist work.

## Stock floor regions

**Static-confirmed** (traced through `0x80024BA8` → `0x80025ED4`). A read-only probe that models these records is Runtime-confirmed bounded in Sektor composition proofs v03/v04 ([proof history](Sektor-Takeover-Proof-History#production-composition-sektor-builds-v50v53-composition-proofs-v01v04)).

The floors a fighter stands on are polylines held in a per-stage table:

| Item | Location / format |
|---|---|
| Count | word `0x80290998` |
| Records | pointer `*0x800C2568`, stride `0xB8` |
| Enabled | byte `0x801AE580[i]` per record |
| Base x / y / z | record words `+0x00` / `+0x04` / `+0x08` (world units) |
| Point count | record word `+0x0C` |
| Points | from `+0x10`, stride 8: `dx`, `dy` signed halfwords relative to the base |
| Flags | record word `+0x94`: `0x300` = shaping modes (not modelled by the probe); `0x800` = ledge region |

- **Match.** A record applies to an actor when `|z − base z| <= 0x80` and its x lies between the first and the last point. The floor there is `base y + dy` of the first point whose x exceeds the actor's x. y grows downward.
- **Effect.** The stock writes `floor << 8` to actor y `+0x30` and controller `+0x6B4`.
- **Controller `+0x6B4` values.** `0x7FBC00` means no floor below (written by `0x80024BA8` when nothing matched). `0x7D0000` is written while the fighter rises or is attached; an airborne target can still hold it a frame after crossing its floor.
- **Airborne crossing.** When controller `+0x6B2` or actor `+0x10` is non-zero, `0x80025ED4` lands the fighter by crossing, using the previous y `+0x3C`. A fighter already below the floor does not land.
- **Ledge branch.** For a falling fighter whose head passes a flag-`0x800` region's level, the ledge branch snaps the actor to the nearest region end (x and y), sets its floor, clears `+0x6B2`, plays sound `0x13` and installs `0x80025E48` through `0x80032CD4`. That routine requests player state 1 (controller `+0x6DC = 1`) and restarts the process at its live dispatch `0x80028F3C`. State 1 being the ledge hang is a strong inference (consistent with the observed hang), not traced.
- **Moving platforms.** These are a separate scan (`0x800258FC`), as are attach objects (`0x80026D40`).

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

**Static-confirmed (2026-11-09).** The jump table at `0x800A9FB8` gives the other types:
- type `2` (`0x8000339C`): run-length coding. The 24-bit little-endian size in header bytes `0..2` includes the header. A control byte `n >= 0` copies `n + 1` literal bytes; `n < 0` repeats the next byte `1 − n` times.
- type `4` (`0x80003428`): the 1024-byte ring at `0x802E7E20` is **not** cleared between images, and output byte `k` lands at ring index `(1 + k) & 0x3FF`. A self-contained encoding therefore only references bytes of the same image (distance at most 1024) and never uses ring index 0, which is the end token. `fighter_import.effects.encode_type4` follows this rule, and its output decodes identically from any stale ring (Implementation/CI-confirmed; Runtime-confirmed in Sektor rocket proofs v39–v41).
- types `1` and `3` return the output buffer without decoding.

Decoded output goes to a per-frame scratch cursor `0x800EEB8C`, which is reset each frame from `*0x80112014` (`0x802C1C00` in the gameplay setters, a buffer up to `0x802D0E34`) and advanced 4-aligned after each decode. Raw type 0 needs no scratch. The render pass `0x800185B8` writes the decoded pointer back into the actor's own frame record (`+0x7C`), not into the resource.

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

The Type-5 switch arm at `0x80003314` (inside the decoder dispatch function, not a separate function entry) resolves the table pointer and calls `0x80065E00`. The output arena reservation is `align4(width) * align2(height)`. A fighter's visible descriptor dimensions may remain unpadded while the type-5 backing buffer uses decoder-aligned dimensions.

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

## Fighter animation script grammar

**Static-confirmed (clean ROM disassembly, 2026-11-07).** Fighter animation scripts are interpreted by `0x800304C0`. The current controller is global `0x802ECE20`, its script cursor is controller `+0x6E4`, and the interpreted actor's resource base is actor `+0x98`. Fighter file `0x87` begins with primary table 0 (65 words at `+0x000`) and secondary table 1 at `+0x104`; selector `0x8002FE54` performs no bounds check, so table-0 index `0x41+n` aliases table-1 index `n`.

Scripts are big-endian 32-bit words. Each `0x800304C0` call consumes control words until it shows one frame or reaches a terminator:

- **`0`** — end of the current phase; returns `0x4002`. A terminator is **not necessarily the end of the physical script**. Host action code may keep advancing past it into later phases. For example, the stock Ice script at `+0xDA0` places token `0x0B` after a `0` terminator, and the Ice action consumes it with a later advance. Any rewrite must preserve the number and order of phases that the host action code consumes.
- **`1..16`** — control tokens, below.
- **any value above 16** — a frame-record offset relative to actor `+0x98`, bound through `0x8001BDA0`; returns `0x4001`.

| Token | Operand words | MKMSZ semantics |
|---:|---:|---|
| `1` | 1 | Jump: cursor = actor `+0x98` + operand; continue |
| `2` | 0 | Horizontal flip: `0x8003188C` toggles actor `+0x8C bit 0x10` and refreshes the frame |
| `3` | 1 | X offset: signed low halfword × 80/100 → `0x80031208(actor, x, 0)` |
| `4` | 1 | XY offset: signed high halfword × 80/100, signed low halfword × 85/100 → `0x80031208` |
| `5` | 1 | Show frame at base + operand through `0x8001BDA0`; returns `0x8001` (distinct from `0x4001`; consumer meaning Pending) |
| `6` | 1 (+ callback-owned) | Callback: index into the 9-entry pointer table at `0x8009F95C` (index `0` is a no-op). Callbacks 1 and 2 consume one additional word |
| `7` | 1 | Operand skipped (no effect) |
| `8` | 2 | Type-conditional jump: if operand 1 == actor `+0x78` (fighter type), cursor = base + operand 2; otherwise both are skipped |
| `9` | 0 | Vertical flip: `0x800318B8` toggles actor `+0x8C bit 0x20` and refreshes the frame |
| `10` | 1 | Partner-relative placement: sets actor `+0xF0=1`; X (high halfword × 80/100, mirrored when facing bit `0x10` is set) and Y (low halfword × 85/100) are placed relative to the actor at controller `+0x63C` |
| `11` | 1 | Secondary resource actor: `0x80030974` constructs a resource-backed actor from the operand entry (`0x80034510`), binds the **fixed Ice palette record `0x800B1A24`** through `0x8001C528`, stores it at controller `+0x714/+0x648`, copies owner position/facing/flags and inserts it through `0x80024650` |
| `12` | 0 | Helper step: make controller `+0x648` current at `+0x714`, align it to the owner through `0x80031394`, recursively run `0x800304C0` on it, restore `+0x6E0`; continue |
| `13` | 0 | No-op |
| `14` | 0 | As token 12, but returns `0x4001` (counts as the shown frame) |
| `15` | 1 | Operand skipped (no effect) |
| `16` | 2 | Companion double frame: ensures companion actor controller `+0x650` (created through `0x800245A4` when absent), copies owner colour/flags, binds the companion frame (operand 1) and the owner frame (operand 2); returns `0x4001` |

On entry, `0x800304C0` clears actor `+0xF0`. For the player actor, any first word other than token `16` hides an existing companion by setting companion `+0x64 bit 0x20`, unless global `0x8009F744` is set.

The callback table at `0x8009F95C`:

| Index | Function | Semantics |
|---:|---:|---|
| `1` | `0x80028BF4` | Consumes one word; its low halfword becomes animation period `+0x6A6` and countdown `+0x6A8` |
| `2` | `0x80028C18` | Consumes one word: gameplay SFX descriptor index for `0x80064C18`, with pan `0x7F` when facing bit `0x10` is clear, otherwise `0` |
| `3` / `4` | `0x800288E0` / `0x800288FC` | Set / clear actor `+0x64 bit 0x2000` |
| `5` / `6` | `0x8002891C` / `0x80028938` | Set / clear actor `+0x64 bit 0x20` |
| `7` | `0x80028958` | Actor `+0x2C -= 0x19000`; for actor type `0x0B` it then wraps the value by `±0x32000` into `[0x5D00, 0x333CB]` |
| `8` | `0x800289FC` | Spawns a class-`0x100` process at `0x80028A24` that builds a resource actor with a randomly chosen variant; identity Pending |
| `9` | `0x800289E0` | Set actor `+0x64 bit 0x100` |

Stock Sub-Zero file `0x87` uses only tokens `1, 2, 3, 5, 6, 10, 11, 16` and callback `1` in its script region `+0x1B0..+0xFF8`. The region decodes linearly with no undecodable words, and re-encoding it reproduces the file byte for byte (`src/mkmszr/fighter_import`). The region ends with code-referenced pointer words at `+0xFC4..+0xFD8` rather than scripts; for example, `+0xFD0` holds `+0xD90`, the rocket/Ice loop loaded by the projectile child. The MKT donor comparison of this grammar is owned by [MKT adapter primitives](MKT-Adapter-Primitives#animation-script-grammar-translation).

## Frame descriptor and the preceding word

**Static-confirmed (2026-11-09); the hazard is Runtime-confirmed (Sektor rocket proofs v35–v39).** A frame word in a script (any value above 16) is the offset of a **shape**: a zero-terminated list of descriptor offsets (one-part shapes are `{descriptor, 0}`). `0x8001BDA0(actor, shape pointer)` binds the first descriptor. A descriptor is three words relative to actor `+0x98`:

| Offset | Meaning |
|---:|---|
| `+0x0` | image offset (a typed image, see [Native image dispatch](#native-image-dispatch)) |
| `+0x4` | width (high halfword), height (low halfword) |
| `+0x8` | anchor x (high halfword), anchor y (low halfword) |

`0x8001BDA0` copies the image pointer and dimensions into the actor's frame record `+0x7C` and computes the anchors from the facing bits `+0x8C & 0x30`. With actor `+0x8C bit 0x40` set, it then reads **the word just before the descriptor**:
- **zero:** the frame uses the actor's texture slot `+0x9C`, and `+0xFA` is incremented, which requests a decode and upload by the render pass;
- **non-zero:** that word is used as the texture slot instead, with no decode request, and the slot record at `0x802E83F0 + word * 0x10` gets `+0x08 = align4(width)` and `+0x0A = height`.

Every stock descriptor checked is preceded by zero (the Ice and rocket entries, `+0x34A58` / `+0x4E6E4`). Generated data must keep that zero word: placing a descriptor straight after other data turns that data into a slot index. Sektor proof v35 put descriptors straight after type-4 images, and an image ending in token bytes `0x86000000` made the bind store into TLB-mapped space, a delayed hang.

## Dynamic gameplay texture-slot record

**Static-confirmed for the fields below.** Dynamic texture IDs `0x200..0x2FF` index 16-byte records at `0x802E83F0 + id*0x10`; backing pointers are stored separately at `0x800ED940[id]`.

| Offset | Meaning | Evidence |
|---:|---|---|
| `+0x00` | format/flags word used by `0x8001F7A8` to choose texture-load path. A fresh allocation writes `(*0x8009A5F0 << 5) | 0x80`. Bits `0x60` select the render mode: `0x8009F6F4[i]` (`0x404240` for all four) and alpha `0x8009F704[i]` = `0x80, 0xC0, 0x40, 0x20`. Bits `0x180 == 0x80` select the byte-copy upload (`0x800202CC`); any other value selects a nibble-swapping copy of `width/2` bytes per row | Static-confirmed |
| `+0x04` | backing-capacity width used by `0x8001C2B4` reuse-fit checks | Static-confirmed |
| `+0x06` | backing-capacity height used by reuse-fit checks | Static-confirmed |
| `+0x08` | current DRAM source-image width; consumed by `0x8001F7A8` when emitting RDP `SetTextureImage` | Static-confirmed |
| `+0x0A` | image/allocation height field; exact downstream ownership beyond allocator bookkeeping is not yet fully cataloged | Static-confirmed field write; semantics bounded |
| `+0x0C` | storage kind. A positive value marks reusable storage: the reuse path returns an inactive record only if `+0x0C > 0` and it fits. Zero marks stack storage: fresh allocation takes an inactive record with `+0x0C == 0` and does not set it | Static-confirmed (allocator and release paths) |
| `+0x0E` | active flag; `1` means active | Static-confirmed |

For a new dynamic allocation, `0x8001C2B4` rounds requested width up to 32 before allocating backing storage and initially writes that aligned width to both `+0x04` and `+0x08`. Its reuse path can return an inactive record whose `+0x04/+0x06` capacity is sufficient **without updating `+0x08`**. Stock image-building callers therefore rewrite `record+0x08` after allocation with the source image's actual DRAM row width. Toasty v23-v37 omitted that caller-owned initialization; see [Toasty visual research](Toasty-Visual-Research).

Fresh storage is taken top-down: `0x800BF2FC` holds the lowest live storage address (reset to `0x80400000` by stage setup `0x8001CA38`). A fresh allocation fails with `-1` if it would go below the texture bump pointer `0x801AE478`, but the bump side `0x8001BF70` has no bounds check against it. Release `0x8001C424` clears `+0x0E`. For stack storage (`+0x0C == 0`) that is the current lowest, it raises `0x800BF2FC` to the lowest remaining active stack storage above it, or to `0x80400000`. Freed storage elsewhere is reclaimed only when everything below it is released. The render pass `0x800185B8` sets `+0x08 = align4(width)` and `+0x0A = height` for each uploaded frame, so a slot must be sized for its largest frame.

**Overflow hazard (Runtime-confirmed through the Sektor composition v05 Toasty corruption).** Nothing limits an upload to the slot's capacity. A frame larger than the slot overwrites the storage allocated just before it, which sits at higher addresses because storage is handed out top-down. Every frame drawn through a slot, including a companion's, must fit that slot's `+0x04/+0x06` capacity ([R4 history](Sektor-Takeover-Proof-History#r4-gameplay-and-the-rope-companion-sektor-builds-v54v58-composition-proofs-v05v09)).
