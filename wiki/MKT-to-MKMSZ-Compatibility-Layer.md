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
| SCCOMBO10 | `0x62BB40..0x62BB53` | **42x95**, (+15,-19) | `0x282C4` |
| SCCOMBO11 | `0x62BB54..0x62BB67` | **50x102**, (+15,-13) | `0x28724` |
| SCCOMBO12 | `0x62BB68..0x62BB7B` | **82x106**, (+25,-8) | `0x28BE4` |

The frame grammar is conceptually compatible with MKMSZ: heap-relative shape list -> 12-byte descriptor -> texture offset/geometry. Offsets must be rebuilt for the target resource base.

### Corrected dimension ordering

The earlier retail handoff and A1.1/A1.3 notes mislabeled the packed MKT size word as X:Y. This is **superseded**.

MKT N64 is built with `ENDIAN=1`. Its `XYTYPE` is physically:

```c
struct {
    int16_t ypos;
    int16_t xpos;
};
```

Therefore SCCOMBO10's packed word `0x005F002A` means **height 95, width 42**. SCCOMBO11 is 50x102 and SCCOMBO12 is 82x106.

The decoded stream lengths independently prove the correction:

- frame 10: `0x1054 = 95 * (42+2)`;
- frame 11: `0x14B8 = 102 * (50+2)`;
- frame 12: `0x22C8 = 106 * (82+2)`.

Static recheck of MKMSZ `0x8001BDA0` shows the target uses the first size halfword as X/width during horizontal-flip math and the second as Y/height. The adapter must therefore swap the size halfwords when converting an MKT frame descriptor: donor Y:X -> target X:Y.

## Texture conversion boundary

The donor streams are not byte-consumable by MKMSZ:

| Frame | Donor stream ROM | Donor codec | Decoded size | Decoded SHA-256 |
|---|---:|---:|---:|---|
| 10 | `0x651B64..0x651FC3` | 22 | `0x1054` | `62cecad0f400fc6b88cf3236c83000ed1fa7f6ec42c5eaadb55dfaca8e44b3ff` |
| 11 | `0x651FC4..0x652482` | 22 | `0x14B8` | `9ce4770a2062d8f990e602c69e367143a1a088c7bba26780b344ca36fc7d1ea1` |
| 12 | `0x652484..0x652A0A` | 24 | `0x22C8` | `d8c7104ac6bbe31e494ef5b06d37c32f5b565b1dc88dbc92ff4ea7939957074c` |

Codecs 22/24 decode deterministically to 5-bit palette indices `0..31`. They use the exact 0x100-byte male-ninja dictionary at ROM `0x6B8550..0x6B864F`.

The donor decoded SCCOMBO10 buffer is row-major with two transparent padding columns per row: `95 * 44 = height * align4(width)`. MKT's retail renderer aligns source width to four bytes, so the first 42 bytes of each 44-byte row are visible pixels and the last two are padding. Runtime proof v08 establishes that MKMSZ's target render path requires the same 4-byte-aligned CI row stride for this imported frame. Removing those two bytes and tightly packing 42-byte rows produces a deterministic staircase/shear; preserving 44-byte rows renders the coherent donor fighter.

MKMSZ decoder `0x8000322C` accepts types 0-5. Static recheck of the clean target shows that the compression type is read from **header byte +3** (the low byte of the big-endian word), masked with `0x3F`; type 0 returns `src+4` directly. Therefore a type-0 wrapper must keep that low byte zero. Writing a raw byte length such as `0x00000FEA` or `0x00001054` into the header is invalid and routes away from type 0.

The current genuine-import plan is:

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

A1/A1.1 established that copying those words into Sub-Zero's stock source palette is **not** an acceptable binding design. A1.1 runtime footage showed ordinary Sub-Zero frames inheriting donor colors.

Static target tracing now identifies the native isolated palette path:

| Target item | Address / field | Meaning |
|---|---:|---|
| palette find/allocate | `0x8001C528` | Finds or allocates a cached palette from a source pointer; native callers receive handles in the `0x140..0x23F` family |
| actor palette selector | actor `+0x9E` | Stores palette handle minus `0x80` |
| frame setup | `0x8001BDA0` | Resolves the selector through the palette-slot table and binds the active handle to actor `+0x80` |
| palette release | `0x8001C64C` | Native refcount/release path; native callers pass `actor+0x9E + 0x80` |
| source-to-hardware upload | `0x8001D9B4..0x8001DA58` | Converts source BGR555 to hardware RGBA5551; source word zero becomes transparent |

Therefore the compatibility-layer palette conversion is now:

```text
MKT RGBA5551 donor palette
-> preserve exact 5-bit RGB channels
-> convert to MKMSZ BGR555 source words
-> donor alpha=0 becomes source zero
-> allocate temporary native MKMSZ palette
-> bind only the imported actor/frame
-> restore stock selector and release the temporary handle
```

This is the design used by proof A1.2/v03. Runtime testing confirmed that this isolated binding preserves stock Sub-Zero colors before and after the imported frame.

## ABI incompatibility

Direct donor field accesses are unsafe.

Relevant retail MKT offsets include PROCESS `+0x418 = pa8`, `+0x41C = animation cursor`, `+0x3F6 = action`, and OBJECT `+0x0C = X velocity`, `+0x14 = X position`, `+0x58 = heap`, `+0x5C = dictionary`.

Relevant MKMSZ evidence instead uses controller `+0x6E0 = actor`, `+0x6E4 = animation cursor`, actor `+0x98 = resource base`, `+0x74 = shape`, `+0x7C = render record`, and different motion/position offsets.

This is why a compatibility adapter is required even when donor control flow is preserved.

## Genuine-import proof branch

The old behavioral Reverse Elbow v6-v8.3 branch is frozen as a host-action proof. It established scheduler/action entry, yielding, player propulsion, action locking, and safe cleanup, but its forced crossover/native-strike substitutions are not the desired donor implementation.

### Proof A1 — SCCOMBO10 single frame

**Runtime-confirmed genuine foreign-sprite import.**

Proof v08 / A1.7 is the first successful runtime rendering of a genuine MKT fighter frame inside MKMSZ. On **Back -> Forward + Low Kick**, MKMSZ displays the actual MKT Rev. 2 SCCOMBO10 Reptile/male-ninja frame, using the donor pixel indices and donor Reptile palette through deterministic format conversion, then restores stock Sub-Zero correctly.

This confirms all of the following for this resource family:

- the selector-3 custom action can safely swap the actor to a foreign resource block and restore it;
- MKT codec-22/24 indexed fighter graphics can be decoded deterministically;
- MKT packed frame dimensions are Y:X and must be converted to MKMSZ X:Y;
- SCCOMBO10 is **42x95**, anchors **(+15,-19)**;
- the donor CI buffer uses a 4-byte-aligned row pitch: **44 bytes per 42-pixel row**;
- MKMSZ must receive that aligned stride; tightly packed 42-byte rows produce the rejected v07 staircase/shear;
- MKT RGBA5551 palette colors can be converted to MKMSZ BGR555 source words;
- donor opaque black must remain nonzero in the target source palette;
- a temporary native MKMSZ palette can be allocated/bound/released without contaminating Sub-Zero's stock palette.

Proof lineage:

**A1 direct:** wrong 95x42 interpretation produced a stable striped rectangle. **Rejected / failed.**

**A1.1:** transposed 95x44 data produced a recognizable but absurdly horizontal fighter. **Rejected / failed** because MKT Y:X dimensions were read backwards.

**A1.2 / v03:** isolated donor-palette ownership was runtime-confirmed; stock Sub-Zero remained correct before/after. Opaque black was still incorrectly transparent.

**A1.3 / v04:** opaque-black conversion corrected, but superseded before runtime testing by the dimension-order correction.

**A1.4/A1.5 / v05-v06:** sparse/confetti output. **Rejected / failed** because the supposed raw-length word changed the MKMSZ compression-type byte and left type 0.

**A1.6 / v07:** valid type-0 and true 42x95 descriptor produced an upright but progressively sheared/stair-stepped image. **Rejected / failed** as a tightly-packed-row conversion; it established the remaining problem as row stride.

**A1.7 / v08:** preserves **44-byte rows = 42 visible CI pixels + 2 padding bytes** while retaining the true 42x95 descriptor, isolated palette, opaque-black mapping, and valid type-0 wrapper. The user runtime test shows a coherent upright Reptile fighter frame with correct stock Sub-Zero restoration. **Runtime-confirmed.**

v08 identity:

- file: `MKMSZR_mkt-scc10-import_global_proof_v08.z64`;
- SHA-256 `1ea40452cdf6e8866b48544fc57f27b065dace75fa0416d52fb4987db61f936d`;
- CRC1/CRC2 `70135E41 / BB4C161F`.

This is a **genuine donor import**, not a redraw or behavioral approximation: the visible fighter art is derived from the actual MKT retail texture stream and palette, with only deterministic codec/palette/descriptor/stride conversion required by the target engine.

### Proof A2

If A1 renders correctly, import the full genuine donor sequence:

```text
10 -> 11 -> 12 -> 11 -> 10
```

with donor timing/geometry and isolated restoration.

### Cross-character generalization proof — Sektor idle

**Genuine Sektor stance rendering is runtime-confirmed; transition-safe replacement remains pending.**

This proof tests whether the resource adapter generalizes beyond the male-ninja/Reptile family by replacing only MKMSZ Sub-Zero's native idle/stance with the genuine MKT Rev. 2 **Sektor** idle.

Retail donor facts:

- MKT fighter `FT_ROBO1 = 7` is Sektor; robot heap base is donor ROM `0x8881C0`;
- robot dictionary is the exact 0x100-byte block at ROM `0x906A90`;
- primary Sektor palette `R1PAL1_P` is the 32-color record at ROM `0x0BC12C`;
- `BHRDROB_P` at ROM `0x0BD798` is a separate red robot head/cut-up palette and is **not** the stance palette;
- retail table-0/index-0 stance dispatcher is heap `+0x1D4`;
- the retail CUT_FRAME build uses `RBSTANCE1 -> 3 -> 5 -> 7 -> 9 -> ANI_JUMP`; the even-numbered source stance frames are not part of the retail idle loop;
- retail stance speed for `FT_ROBO1` is 8;
- all five retail stance frames are codec 22 and independently obey `decoded_size = height * align4(width)`;
- the retail stance shapes are already single flattened image records, so this proof does not require generic multipart/composite rendering.

Exact imported frames:

| Frame | Geometry | Anchor | Donor texture ROM |
|---|---:|---:|---:|
| RBSTANCE1 | 55x113 | (+26,-8) | `0x88B6AC` |
| RBSTANCE3 | 50x113 | (+22,-8) | `0x88BD5C` |
| RBSTANCE5 | 53x113 | (+21,-8) | `0x88C3FC` |
| RBSTANCE7 | 58x113 | (+26,-8) | `0x88CAD0` |
| RBSTANCE9 | 57x113 | (+27,-8) | `0x88D194` |

Target facts used by the proof:

- Sub-Zero's N64 character resource is global file ID `0x87`, clean ROM `0x748920..0x78E2FF`;
- its table-0/index-0 stock stance pointer is resource `+0x2EC`;
- the stock MKMSZ stance script uses command `1` + self-offset for looping, matching the donor animation grammar needed here;
- target fighter type `4` is Sub-Zero at actor `+0x78`;
- target frame setup `0x8001BDA0` resolves the palette selector at actor `+0x9E` and writes the resolved active palette handle to actor `+0x80`.

#### v01 — genuine Sektor rendering confirmed, transition cleanup failed

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v01.z64`

Runtime result reported by the user:

- standing neutral visibly renders Sektor "in all its glory";
- the genuine five-frame Sektor stance is therefore **Runtime-confirmed** in MKMSZ;
- leaving idle can show a single corrupted/weird transition frame;
- attempting to crouch from Sektor idle caused a whole-emulator/game hard hang immediately after Down was pressed.

The donor decoding, dimensions, row stride, palette choice, and idle-script resource are therefore not the current failure. The failure is at the idle-exit ownership/lifecycle boundary.

Static re-audit found a concrete v01 defect:

1. v01 saved/restored actor palette selector `+0x9E`;
2. it did **not** save/restore the resolved active palette handle at actor `+0x80`;
3. on a non-idle selection it restored `+0x9E` and released the temporary Sektor palette immediately;
4. until native frame setup rebound a stock palette, actor `+0x80` could still refer to the released donor palette slot.

That is a real use-after-release window and is consistent with both the one-frame corruption and crouch hang. The structural defect is **Static-confirmed**; it remains a **strong inference** that this is the complete runtime cause until the corrected proof is tested.

#### v02 — active-handle restoration fix

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v02.z64`

Identity:

- SHA-256 `d5df6193d6b942664ff02367037e55f58683a439d11f4926646c71ddd46a182c`;
- CRC1/CRC2 `35B9266E / F0DB463F`.

v02 is built from the clean supported target ROM. The imported Sektor resource block is byte-for-byte identical to v01. The isolated change is palette-transition bookkeeping:

- save stock selector `actor+0x9E`;
- save stock active palette handle `actor+0x80`;
- on idle exit restore **both** fields;
- only then release the temporary donor palette;
- retain donor idle speed 8 only while the Sektor idle binding is active.

**Rejected / failed as a complete fix; donor rendering remains runtime-confirmed.**

Further user runtime testing showed the same single-frame corruption and hard hangs. The trigger is selective rather than simply "any animation change": block, punches, kicks, turning, walking backward, and ordinary jumping can work, while crouching, walking forward, and adding forward drift during an already-running jump can hard-hang immediately. The supplied 12.7-second capture is especially constraining because the final failure occurs after a stock jump is already visibly underway; adding forward movement freezes the game without a visible animation change first.

The capture also shows the transient corrupt frame when returning from stock actions to Sektor idle (approximately 4.5 s and 7.0 s in that recording). This narrows that artifact separately to the idle-entry presentation boundary.

#### v03 — restore the stock resource table; redirect only the idle cursor

Static re-audit found a stronger structural problem in v01/v02. The relocated Sub-Zero resource was copied intact except that its actual table-0/index-0 word was permanently changed from stock `+0x2EC` to appended Sektor script `+0x459E0`. This means the proof globally replaced the resource's stance entry, rather than limiting the foreign animation to the `select_animation(0,0)` call. Static target code contains resource-table reads outside `0x8002FE54`, so a permanent table mutation can affect stock state/locomotion code even when no visibly new animation has been selected.

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v03.z64`

Identity:

- SHA-256 `222fb08985f30f78b2628e74ea24b21c2ac26701f4bc81450be574a21be908ca`;
- CRC1/CRC2 `40543A98 / EE1442F8`.

v03 is built from the clean supported ROM and keeps the donor frames/palette/timing identical to v02. Its isolated change is:

- the relocated first `0x459E0` bytes of Sub-Zero's resource are byte-for-byte identical to the clean stock file, including table-0/index-0 = `+0x2EC`;
- the appended Sektor data remains outside that stock range;
- only an exact Sub-Zero idle request `(table 0,index 0)`, while the isolated donor palette is owned by the same actor, writes controller `+0x6E4 = resource_base + 0x459E0`;
- all non-idle calls continue through the stock `select_animation` tail and all other resource-table consumers see stock data.

**Rejected / failed as a hang fix; donor rendering remains runtime-confirmed.**

The user repeated the same forward, airborne-forward, crouch, safe-action, and transition tests. v03 behaved **exactly like v02**, including hard hangs at the same failing inputs and the same transient corrupt frame. Therefore permanently replacing the table-0/index-0 word was not the cause of the hang.

This negative result materially narrows the failure: the common foreign state that remains during Sektor idle is the **live animation cursor itself**, which v03 still redirected from the native Sub-Zero stance region into the appended Sektor script. Static target code snapshots, compares, and advances controller `+0x6E4` directly in several helpers outside simple `select_animation` calls, so cursor locality/lifecycle is now the leading hypothesis.

#### v04 — native cursor location with foreign frame pointers + diagnostic HUD

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v04.z64`

Identity:

- SHA-256 `295480a5596dd9c6a09be3dbc7899c3d6c2b6a1e0c2193c0624834a7ef3ee385`;
- CRC1/CRC2 `36AD42FB / 615A2E42`.

v04 keeps the relocated Sub-Zero resource table unchanged and no longer redirects `controller+0x6E4` to appended script `+0x459E0`. Instead, it preserves the native table-0/index-0 target and native cursor location at resource `+0x2EC`, replacing only the first seven words of that native idle script with:

```text
Sektor RBSTANCE1 shape
Sektor RBSTANCE3 shape
Sektor RBSTANCE5 shape
Sektor RBSTANCE7 shape
Sektor RBSTANCE9 shape
command 1
self +0x2EC
```

All other bytes in the original `0x459E0`-byte Sub-Zero resource are unchanged. The appended donor shapes, raw CI buffers, converted Sektor palette, and donor idle rate 8 remain the same as the earlier proofs.

v04 also adds proof-only native HUD instrumentation through the already runtime-confirmed gameplay text path. The bottom readout is:

`P# C# L# X#`

where the digits encode donor-palette ownership, whether the live animation cursor is inside the native idle-script range, the low nibble of controller locomotion state, and the low nibble of normalized action input. This instrumentation is diagnostic only and is not a product UI design.

**Rejected / failed before gameplay; cursor hypothesis not tested.**

The user reported that v04 reached the Mission Objective display, stage music began, and then the game/emulator hung before gameplay appeared. Because v04 introduced both the native-cursor experiment and a new diagnostic HUD wrapper at the same time, this result is confounded and does **not** establish whether the native-cursor strategy is valid.

Static re-audit found that the v04 diagnostic wrapper read controller/actor state from the gameplay HUD path without first proving that a live player context existed. The Mission Objective flow can execute that HUD path before normal gameplay control is established, so the diagnostic code is a **strong candidate** for the pre-game hang. This is not runtime-confirmed as the sole cause until an otherwise-identical no-HUD build is tested.

Historical context from the earlier Reverse Elbow/Reptile proof is important here: a separate diagnostic path was already runtime-confirmed during gameplay, displaying forms such as `IN XXXXXXXX L0 P0 A00` through the native HUD/text path and surviving repeated special activations. Future instrumentation should reuse that proven pattern rather than the unguarded v04 wrapper.

#### v05 — v04 cursor experiment with diagnostic HUD removed

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v05.z64`

Identity:

- SHA-256 `8be8bf1e1aa066483043c528623c8f7ff08c40042d786a5d62ef97a2ac1dd5e9`;
- CRC1/CRC2 `BFDA3A1F / 1142C1A6`.

v05 is byte-for-byte v04 except for removal of the proof-only diagnostic HUD hook/wrapper/string and the resulting header CRC change. It therefore preserves the intended v04 animation experiment unchanged:

- native Sub-Zero table-0/index-0 still points to resource `+0x2EC`;
- the live animation cursor remains in that native idle-script region;
- only the first five idle-frame pointers plus the native loop command/self-offset are replaced to render the genuine Sektor stance;
- donor palette ownership and idle rate remain as in the earlier proofs.

**Rejected / failed as a hang fix; stage-start isolation succeeded.**

The user confirmed that v05 enters gameplay normally, proving the v04 pre-game Mission Objective hang came from the added diagnostic HUD rather than the native-cursor experiment. Once gameplay begins, however, v05 behaves like v02/v03: Sektor idle renders, but forward movement, crouch, and airborne forward drift still hard-hang at the same points. The native-cursor-at-`+0x2EC` hypothesis is therefore **Rejected / failed** as the cause of the gameplay hang.

This result leaves a smaller set of implementation pieces common to all failing Sektor builds: resource relocation/foreign shape use, temporary palette ownership/select-animation wrapper, proof state storage, and the donor-rate hook.

#### v06 — remove only the donor animation-rate hook

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v06.z64`

Identity:

- SHA-256 `06b1eb0d3a964d2b42f4ba8006a646c700fde08ab97700a3082001c8471e06da`;
- CRC1/CRC2 `4753AA06 / DACEC518`.

v06 is byte-for-byte v05 except for restoring the clean stock bytes at ROM `0x32324..0x3232B` / VA `0x80031724..0x8003172B`, removing the proof's animation-rate interception entirely. Sektor therefore runs at MKMSZ's stock cadence rather than donor rate 8. No imported frame, resource, palette, select-animation, or state-storage bytes changed.

**Rejected / failed as a hang fix.**

The user reported that v06 still hard-hangs on the same forward movement, crouch, and airborne-forward inputs. Therefore the donor animation-rate hook is **not** the cause of the gameplay hang.

At this point the persistent one-frame corruption on animation transitions can no longer be treated as confidently cosmetic. The strongest common remaining suspect is the temporary donor-palette/select-animation wrapper and its render-state transition, which is also the code path most directly associated with the visible corrupt transition frame.

#### v07 — remove dynamic donor palette handling entirely

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v07.z64`

Identity:

- SHA-256 `aa989a2dc74fa577245c3d9895d2471035ad7cb9544b62487e4a8f8d85c2a8f8`;
- CRC1/CRC2 `3884563E / AF3FDC3B`.

v07 is byte-for-byte v06 except for restoring the clean stock first two instructions of target `select_animation` at ROM `0x30A54..0x30A5B` / VA `0x8002FE54..0x8002FE5B`. This completely bypasses the Sektor proof's dynamic palette wrapper and temporary owner/selector state while preserving the native-cursor idle script and imported Sektor frame resources.

Expected presentation: the genuine Sektor stance geometry/animation should still render, but with Sub-Zero's stock palette, so colors may be wrong. That visual degradation is intentional.

**Rejected / failed as a hang fix; palette presentation cause separated from hang cause.**

The user confirmed that v07 still hard-hangs on the same forward movement, crouch, and airborne-forward inputs. The visible result changed substantially: all five Sektor stance frames now render with wrong/corrupted colors under Sub-Zero's stock palette. This establishes that the dynamic donor-palette path is required for correct Sektor presentation, but it is **not** the cause of the hard hang.

This also separates the symptoms: the transition/frame color corruption is palette/render-state related, while the input-specific hard hang persists without any Sektor palette wrapper execution.

#### Corrected false-cave finding

Static re-audit found a more fundamental proof error common to v01-v07. The helper was placed at ROM `0xA1308..0xA1543` / VA `0x800A0708..0x800A0943` because the clean bytes were zero. That region is **not unowned free space**.

A live pointer table begins at ROM `0xA15C4` / VA `0x800A09C4` and points to twelve 0x78-byte records:

```text
0  0x800A049C  callback +0x10 = 0x8003C870
1  0x800A0514  callback +0x10 = 0x8003C9B4
2  0x800A058C  callback +0x10 = 0x8003C984
3  0x800A0604  callback +0x10 = 0x8003C848
4  0x800A067C  callback +0x10 = 0x8003C94C
5  0x800A0424  callback +0x10 = 0x8003C7E8
6  0x800A06F4  callback +0x10 = 0x8003C7F0
7  0x800A076C  stock record is all zero
8  0x800A07E4  stock record is all zero
9  0x800A085C  stock record is all zero
10 0x800A08D4  stock record is all zero
11 0x800A094C  stock record is all zero
```

The Sektor helper overwrote most of zero records 7-10 and part of the surrounding record area with executable instructions. Zero bytes here are therefore **semantic data, not a code cave**. An input/action scan that expects those records to remain zero can observe nonzero garbage fields or bogus callback values. This is a strong static explanation for why only selected inputs hard-hang.

This supersedes every earlier statement treating `0x800A0708..` as free proof storage.

#### v08 — restore the false cave to exact stock data

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v08.z64`

Identity:

- SHA-256 `d842c51bf1253ccd0fece0f255e804a4077907aa55fc759fb54b61dde6b1d9be`;
- CRC1/CRC2 `C2435AAC / EBC131C0`.

v08 is byte-for-byte v07 except for restoring ROM `0xA1308..0xA1543` to the clean ROM's exact stock zero-filled record data and recalculating the header CRC. Because v07 already restored the stock `select_animation` entry and removed the rate hook, no Sektor helper code is needed for this test.

Active Sektor changes remaining in v08 are therefore only:

- relocated/expanded file ID `0x87`;
- native idle script frame pointers changed to the five appended genuine Sektor shapes;
- appended donor frame/texture data.

The palette remains intentionally stock Sub-Zero, so Sektor is expected to look color-corrupted exactly as in v07.

**Runtime-confirmed.**

The user confirmed that v08 no longer hard-hangs: forward movement, crouch, and airborne forward drift all work. The Sektor stance still renders with intentionally wrong colors because the donor palette wrapper remains disabled.

Because v08 differs from v07 only by restoring the falsely claimed cave to its exact stock zero-filled dispatch records (plus header CRC), this establishes the root cause of the input-specific hard hangs as the overwritten live action/dispatch data. The failure is therefore **Runtime-confirmed**, not merely inferred.

The durable safety rule is: ROM `0xA1308..` / VA `0x800A0708..` is not generic free space. In particular, the zero-filled 0x78-byte records referenced by the live table at VA `0x800A09C4` are semantic dispatch data and must remain stock unless deliberately decoded and modified.

#### v09 — re-home palette helper into owned reserved runtime memory

Disposable proof:

`MKMSZR_mkt-sektor-idle_subzero-swap_proof_v09.z64`

Identity:

- SHA-256 `8d702002ef5b5ac8b8a9289e7b4f059ad92fd28c64a425bb240d86a6b6bf0829`;
- CRC1/CRC2 `2A920945 / 02213D28`.

v09 is built from the runtime-confirmed v08 behavior and reintroduces only the corrected dynamic Sektor palette path in explicitly owned proof memory:

- the existing 1 KiB arena reservation `0x801AF420..0x801AF81F` is enabled through the current proven two-site reservation;
- file ID `0x1B` loads a bounded 0x300-byte proof payload from ROM `0xF10000` to RDRAM `0x801AF420`;
- the existing runtime-confirmed stage-load bootstrap loads that payload before gameplay;
- the palette helper is at `0x801AF440`;
- its temporary state is at `0x801AF700`, inside the same explicitly reserved proof payload;
- target `select_animation` redirects only its first two instructions to that owned helper, which then resumes at stock `0x8002FE5C`;
- the false cave `0x800A0708..` remains byte-for-byte stock;
- the donor animation-rate hook remains disabled, so this proof uses MKMSZ's stock idle cadence.

The helper retains the corrected v02 palette bookkeeping: save stock selector and active palette handle, allocate/bind the genuine Sektor palette for exact idle selection, restore both stock fields before release on exit.

**Implementation/static-confirmed; runtime pending.**

Primary success criterion: Sektor regains correct red/black donor colors while forward movement, crouch, airborne forward drift, attacks, blocking, turning, and jumping remain stable. The previously observed single-frame transition artifact may still remain; v09 intentionally does not change its ordering so palette re-homing is tested independently.

A separate instrumentation note remains: the earlier Reverse Elbow/Reptile branch already runtime-confirmed a gameplay-safe diagnostic HUD through the native gameplay HUD/text path. Future Sektor instrumentation should reuse that proven pattern rather than the rejected v04 unguarded wrapper.

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

- import and runtime-confirm the complete donor `SCCOMBO10 -> 11 -> 12 -> 11 -> 10` sequence using the now-confirmed frame-conversion rules;
- confirm those rules on SCCOMBO11 (50x102) and SCCOMBO12 (82x106), including their row strides and codec-24 conversion;
- identify the narrowest MKMSZ fighter-separation hook for a three-tick no-repel gate;
- identify the best native victim-action primitives for exact donor reactions without bypassing interruption/cleanup.

Do not spend effort polishing the old forced-crossover imitation while these genuine-port proofs are pending.
