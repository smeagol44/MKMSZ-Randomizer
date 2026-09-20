# MKT to MKMSZ compatibility layer

This page owns the current **genuine donor-port** direction for bringing Mortal Kombat Trilogy N64 fighter behavior/resources into Mortal Kombat Mythologies: Sub-Zero N64.

The older behavioral-recreation page is retained as history at [Foreign moves and Reptile](Foreign-Moves-and-Reptile), whose title is marked **(Old)**. The MKMSZ host-action ABI and proof history remain current in [Player actions and special moves](Player-Actions-and-Special-Moves).

## Goal and evidence boundary

The target is not to imitate an MKT move with vaguely similar MKMSZ parts. The target is a source-level compatibility/porting layer that preserves donor control flow and donor data wherever practical, translating only engine-facing interfaces.

Current donor evidence is tied to:

- **MKT USA Rev. 2 N64**, 0xC00000 bytes, SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb`;
- **MKMSZ USA Rev. 0 N64**, SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`.

The public `Zoltan45/mktrilogy` source tree is a symbolic guide. Exact addresses/data below are retail-binary findings from the supplied Rev. 2 ROM unless marked otherwise.

## Strategy decision

**Recommended: faithful source-level port through an MKMSZ adapter.**

Preserve:

- donor phase ordering and loop counts;
- donor movement constants;
- donor animation scripts and frame resources;
- donor strike geometry/damage/reaction records;
- donor victim-reaction semantics;
- donor no-repel behavior;
- donor hit/block/timeout/recovery branches.

Translate:

- MKT PROCESS/OBJECT field accesses to MKMSZ layouts;
- MKT scheduler/action entry to the proven MKMSZ selector/action bridge;
- MKT helper calls to semantically equivalent MKMSZ helpers;
- missing engine semantics through narrow compatibility shims;
- donor texture codecs into a target-consumable representation without redrawing the graphics.

Direct relocation of retail instructions is **not** the current strategy. The two games' process/object layouts, globals, scheduler ABI, strike/reaction tables, heap bases, and texture codecs differ enough that binary rewriting would require move-specific semantic annotations and would effectively be a more fragile source-level port.

## Reverse Elbow retail closure

Retail path:

```text
do_reptile_dash       0x8004F2C0
-> do_body_propell    0x80045050, selector 0x17
-> prop_do_reptile_dash 0x800467D0
-> reptile_dash_hit   0x80046910
```

Supporting entries in this closure include:

| Donor item | Retail address |
|---|---:|
| propell table | `0x800A80D0` |
| table[0x17] | `0x800A812C -> 0x800467D0` |
| init_special | `0x80050420` |
| get_char_ani | `0x8000F910` |
| do_next_a9_frame | `0x8000D408` |
| mframew | `0x8000DB98` |
| towards_x_vel | `0x8006EC00` |
| process_sleep | `0x8005A88C` |
| sans_repell_3 | `0x8006C7FC` |
| strike_check_a0 | `0x8003E620` |
| stop_me | `0x8003DB54` |
| face_opponent | `0x8006D1CC` |
| reaction_exit | `0x8004C13C` |
| context_jump | `0x80080A84` |

The retail move uses an initial run/contact scan for up to 16 ticks. On successful first contact it continues past the victim for 14 ticks with no-repel refreshed, stops, waits 6 ticks, faces the opponent, plays the first half of the return animation, moves back toward the opponent, scans for the second hit for up to 20 ticks, stops, waits 20 ticks, plays the recovery half of the animation, and exits.

## Real pass-through semantic

MKT does **not** teleport the attacker through the victim.

`sans_repell_3` sets signed halfword `f_norepell` at `0x802475E4` to 3. The central repel process at `0x80070A08` decrements it once per separation tick. While the resulting working value is nonzero, the normal super-close forced velocities and per-player anti-overlap velocity corrections are skipped.

Minimum compatibility semantic:

```text
no_repel_ticks = 3
each native separation tick:
    if no_repel_ticks != 0:
        no_repel_ticks--
        bypass fighter repulsion corrections
```

Reverse Elbow refreshes this state during the outward/contact continuation. The old proof-only forced-X crossover is not the donor behavior and is no longer the intended architecture.

## Donor strikes and reactions

MKT strike numbers are donor-table indices, **not MKMSZ strike IDs**.

Reptile uses `nj_strikes` at `0x800B0208`.

| Donor index | STRKTBL | Exact record | Meaning |
|---:|---:|---|---|
| `0x15` | `0x800B041C` | `002b 0009 0022 006e 7400 0000 0001 0000` | first contact; box (43,9,34,110), reaction `0x74`, zero damage |
| `0x16` | `0x800B042C` | `0044 000b 0027 003c 2400 0d03 0001 0000` | return hit; box (68,11,39,60), reaction `0x24`, damage 13 / block 3 |

Reaction dispatch:

- selector `0x74` -> `r_reptile_dash` at `0x800546A0`: reject airborne victim, otherwise approximately 20 ticks of held stance/reaction, then normal exit;
- selector `0x24` -> `r_jax_dash` at `0x80055838`: generic damaging launch/reaction with sound, shake, flight, and landing.

A real port translates these **records and semantics**. Reusing numeric MKMSZ strike 0x15/0x16 is explicitly rejected.

## Exact return-animation resource

MKT male-ninja table 2 begins at donor heap offset `0x168`. Slot `0x0B` points to heap offset `0x664`.

Retail script at ROM `0x629F04..0x629F1F`:

```text
SCCOMBO10
SCCOMBO11
SCCOMBO12
0
SCCOMBO11
SCCOMBO10
0
```

Exact frame records:

| Frame | Record ROM | Geometry | Donor texture offset |
|---|---:|---|---:|
| SCCOMBO10 | `0x62BB40..0x62BB53` | 95x42, (+15,-19) | `0x282C4` |
| SCCOMBO11 | `0x62BB54..0x62BB67` | 102x50, (+15,-13) | `0x28724` |
| SCCOMBO12 | `0x62BB68..0x62BB7B` | 106x82, (+25,-8) | `0x28BE4` |

The frame grammar is conceptually compatible with MKMSZ: heap-relative shape list -> 12-byte descriptor -> texture offset/geometry. Offsets must be rebuilt for the target resource base.

## Texture conversion boundary

The donor streams are not byte-consumable by MKMSZ:

| Frame | Donor stream ROM | Donor codec | Decoded size | Decoded SHA-256 |
|---|---:|---:|---:|---|
| 10 | `0x651B64..0x651FC3` | 22 | `0x1054` | `62cecad0f400fc6b88cf3236c83000ed1fa7f6ec42c5eaadb55dfaca8e44b3ff` |
| 11 | `0x651FC4..0x652482` | 22 | `0x14B8` | `9ce4770a2062d8f990e602c69e367143a1a088c7bba26780b344ca36fc7d1ea1` |
| 12 | `0x652484..0x652A0A` | 24 | `0x22C8` | `d8c7104ac6bbe31e494ef5b06d37c32f5b565b1dc88dbc92ff4ea7939957074c` |

Codecs 22/24 decode deterministically to 5-bit palette indices `0..31`. They use the exact 0x100-byte male-ninja dictionary at ROM `0x6B8550..0x6B864F`.

MKMSZ decoder `0x8000322C` accepts types 0-5. Static recheck of the clean target shows type 0 returns `src+4` directly, so the current genuine-import plan is:

```text
actual MKT codec-22/24 bytes
-> exact donor decoder
-> exact decoded indexed bytes
-> MKMSZ type-0/raw wrapper
-> existing MKMSZ frame/render path
```

This is deterministic format conversion, not redrawing or behavioral recreation.

## Palette

MKT Reptile primary palette record is ROM `0xBE864..0xBE8A7`: u32 count 32 followed by 32 big-endian RGBA5551 colors. The move does not switch palettes.

MKMSZ Sub-Zero's source palette is a 64-entry RGBA5551 container. For the disposable A1 proof, donor entries 0..31 are copied into the existing Sub-Zero palette container while preserving its 64-entry count. This is a proof-only binding method; a general compatibility layer still needs an isolated dynamic palette/resource binding design.

## ABI incompatibility

Direct donor field accesses are unsafe.

Relevant retail MKT offsets include PROCESS `+0x418 = pa8`, `+0x41C = animation cursor`, `+0x3F6 = action`, and OBJECT `+0x0C = X velocity`, `+0x14 = X position`, `+0x58 = heap`, `+0x5C = dictionary`.

Relevant MKMSZ evidence instead uses controller `+0x6E0 = actor`, `+0x6E4 = animation cursor`, actor `+0x98 = resource base`, `+0x74 = shape`, `+0x7C = render record`, and different motion/position offsets.

This is why a compatibility adapter is required even when donor control flow is preserved.

## Genuine-import proof branch

The old behavioral Reverse Elbow v6-v8.3 branch is frozen as a host-action proof. It established scheduler/action entry, yielding, player propulsion, action locking, and safe cleanup, but its forced crossover/native-strike substitutions are not the desired donor implementation.

### Proof A1 — SCCOMBO10 single frame

**Implementation-confirmed; runtime pending.**

A disposable ROM has been built from the verified clean MKMSZ input. It:

- expands the proof-only reserved prefix to 0x2000 bytes;
- loads file ID `0x1B` from ROM `0xF10000..0xF11FFF`;
- keeps the runtime-confirmed selector-3 special-action bridge;
- on Back -> Forward + Low Kick, temporarily points actor resource base `+0x98` to an imported resource block;
- uses the genuine decoded SCCOMBO10 bytes and donor geometry;
- wraps the donor pixel stream as MKMSZ type-0/raw;
- uses the exact donor Reptile palette entries 0..31 in the target palette container;
- calls target frame setup `0x8001BDA0`;
- holds the frame for 60 ticks;
- restores the stock resource base and native control.

A1 deliberately contains **no movement, strike, collision, victim reaction, no-repel shim, or Reverse Elbow choreography**. It tests only foreign-resource rendering.

Output identity:

- SHA-256 `4fd1af63d4e25bde0ef5aa30dc8116755c60931701f855fa2126206a6c52ae7b`;
- CRC1/CRC2 `00165F37 / CF51079E`.

### Proof A2

If A1 renders correctly, import the full genuine donor sequence:

```text
10 -> 11 -> 12 -> 11 -> 10
```

with donor timing/geometry and isolated restoration.

### Later proofs

After genuine animation rendering is runtime-confirmed:

1. translate donor strike record 0x15 and victim reaction 0x74;
2. add the real no-repel countdown/gate;
3. port donor outward run/contact loop;
4. translate donor strike 0x16 and reaction 0x24;
5. assemble the exact retail phase ordering;
6. broaden the adapter only when a second foreign move demonstrates reusable semantics.

## Current uncertainties

Pending runtime/static questions are intentionally narrow:

- whether MKMSZ type-0 consumes the decoded donor column-major one-byte index stream exactly as wrapped;
- whether the proof-only 32-entry donor palette substitution binds with the expected colors;
- the narrowest MKMSZ fighter-separation hook for a three-tick no-repel gate;
- the best native victim-action primitives for exact donor reactions without bypassing interruption/cleanup.

Do not spend effort polishing the old forced-crossover imitation while these genuine-port proofs are pending.
