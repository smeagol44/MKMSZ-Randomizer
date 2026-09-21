# Runtime validation status

This matrix states the narrowest claim supported by evidence. “Runtime-confirmed” never means exhaustive unless the scope says so.

| Domain | Runtime-confirmed scope | Static/CI scope | Not yet established |
|---|---|---|---|
| Selector | A-button title route; all eight compact destinations | Guards, table, range, mapper | Intermittent Start shortcut is not production |
| Arena/bootstrap | Reserved block loads and executes | Both arena sites, file-table entry, hook/stub bounds | Expansion beyond the 1 KiB contract |
| Pickup persistence | At least one ordinary pickup in every stage; multiple Fire records; Temple completion | All 84 records and bit mappings | Every record individually; Game Over reset |
| Pickup randomization | `TEST153` first Fire location became predicted Shield and behaved normally | All 84 identities; deterministic namespaces; 250-seed access-model tests | Full seeded playthrough; broad arbitrary-layout runtime coverage |
| Four-box inventory | Switching, live/backing copies, transition survival, foreign-key masking | Input/remap hooks and lifecycle routines | Every save/load/Game Over edge |
| Native UI | Arbitrary custom text and persistent box indicator | Node structure, hook, string/cave guards | General textured-image API |
| Flow bypasses | Logos skipped; selector entry avoids only immediate auto-save | Exact owning routine and branch guards | No known open item |
| Palette | Multiple modes visibly recolor clothing | 64-entry source TLUT and BGR555 transform | Dynamic non-Sub-Zero palettes |
| Enemy substitution | Fire `0x0A -> 0x09`; imported Temple monk in Fire | Stream formats, constructor/resource tables | Death presentation; arbitrary mixes; bosses |
| XP progression | Temple proof: three progression pickups plus one vanilla Herbs control, first two tested at `85` and `258`; no combat/kill/combo XP, tier advance, no inventory award, coexistence. Diagnostic B (`BCBDBF`): V2 allocation and XP-only restore, Temple -> Wind and title -> Fire retention of XP 258/two moves | Central award, direct stores, cap table, save field, V2 storage, deterministic nine-reward generation | Final art, full nine-tier run, Game Over/new-run reset |
| Reverse Elbow / MKT port | v6 host-action lifecycle repeats without global hang; v08/A1.7 renders genuine SCCOMBO10; Sektor direct replacements through Jump Kick / Flip Kick / Flip Punch are runtime-confirmed clean; v26 confirms Low-Punch chain/crossover behavior, v27 confirms the exact 13-word Standing Low Kick, v28 confirms the exact 13-word Standing High Kick, v29 confirms Knee, v30 confirms Sweep, v31 confirms Roundhouse, v32 confirms Jump, and v33 confirms all three aerial attacks; v20 remains the accumulated raw-size failure case | v27 redirects slot 0x12 to an appended exact retail script and keeps file 0x87 at 0x58944; v28 does the same for slot 0x11 High Kick and keeps file 0x87 at 0x588BC. v25+ proof ROMs use the runtime-confirmed post-legal logo bypass | v34 runtime-confirms Forward Flip, Back Flip, and High Hit; Low Hit remains pending because the tested route did not expose a practical crouching-hit case. v35 runtime-confirms Sweep Fall + Sweep Getup; v36 runtime-confirms Knockdown; v37 runtime-confirms normal Getup; v39 runtime-confirms Stumble on the tested route. v39 Prison is a runtime-confirmed failure: initial room renders correctly, then the scene/framebuffer catastrophically corrupts at the first doorway/encounter activation. v40 uses the same selector/helper composition with file 0x87 reduced to v11 size 0x4D820, and the same Prison doorway works normally. v41 restores only the file-0x87 allocation size to 0x578BC by appending unreachable 0xFF tail bytes; the same Prison doorway corrupts again. Runtime-confirmed: allocation footprint alone is sufficient to trigger the failure at 0x578BC. Exact lower threshold remains unknown. v42 runtime-confirms generated native type-5 storage for one genuine Sektor stance frame with no visible difference from raw and no Prison-door regression. v43 compacts all five idle frames, reduces file 0x87 to 0x49BAC, and is runtime-confirmed clean including Prison's first doorway. v44 runtime-confirms compressed Walk F/B and Turn plus shared-Walk dictionary use, but Crouch hard-hangs before frame 1 because its generated shape records were not 4-byte aligned; this packing bug is rejected. v45 corrects alignment for the same locomotion composition at file 0x87 size 0x52740 and is runtime-confirmed clean, including repeated Crouch transitions and Prison's first doorway. v46 runtime-confirms all 34 compressed Sektor frames/actions, including Crouch Hit, and Prison's first doorway itself survives. New failure boundary: after crossing that Prison doorway, opening Inventory hard-hangs; Inventory works before the door and the failure has not been observed in other stages so far. v47 preserves the exact v46 action/content set while relocating most compressed image streams into 42 file-local-unreferenced stock Sub-Zero frame intervals, reducing file 0x87 to 0x52BC0. Runtime-confirmed: Prison first doorway followed by Inventory now works, isolating v46's Inventory hang as memory/headroom-sensitive on that route. Fortress regression is now bounded: v45 (0x52740) and v47 (0x52BC0) both hang on Mission Objective before music/gameplay; v40 (0x4D820) loads Fortress normally. v47 reclamation is therefore not the onset. v48 pads v40 with unreachable 0xFF bytes to exactly 0x52740 and runtime-confirms the same pre-music Fortress hang: file-0x87 allocation footprint alone is sufficient to fail Fortress at that size. Exact lower threshold is not required. v49 (real locomotion, no stock-hole reuse) is 0x4E544; v50 (same locomotion with conservative stock-hole reuse) is 0x4C320, below working v40. Both are runtime-confirmed in Fortress: stage music/gameplay load normally and Inventory opens normally. This confirms Type-5 locomotion and the conservative locomotion-hole reclamation strategy are Fortress-safe on the tested route. v51 keeps the full 34-frame v46/v47 action set while merging the same already-proved dead intervals into five contiguous reclaimed regions; file 0x87 becomes 0x5100C. Runtime: Prison first doorway + Inventory passes, but Fortress still hangs on Mission Objective; this time stage music starts before the hang, indicating later initialization progress than v45/v47/v48. v52 is an exact-size control based on working v49: only inert tail padding raises file 0x87 from 0x4E544 to 0x5100C; runtime pending. Low Hit remains pending; prioritize compact fighter storage/encoder work |
| PS1 | No new runtime test in this consolidation | Executable/resource/save/pickup/enemy mappings | Fire type substitution, UI hook, playable Scorpion moves |

## Runtime environment lineage

Historical N64 proof runs used BizHawk `2.11.1`, Ares64, CPU emulation `1`, and P1 controller `2` where explicitly recorded. State-specific observations remain bound to their ROM and save-state identity. The Wiki reproduces conclusions and exact addresses, while hashes and original captures remain historical provenance.

## Production vs proof

“Production” requires current guarded code and tests. “Proof” may intentionally use a temporary cave, a one-off record edit, or a narrow replacement. For example, the Temple XP result is runtime-confirmed but its cave conflicts with production, and the Temple-monk import proves resource residency but lacks the monk's normal death presentation.


### v53 common-animation takeover

**Runtime-confirmed.** Fortress, Prison, Inventory, representative common actions, and demo movies all pass without hangs. Expected remaining gaps are placeholder/unported animation states.

v53 removes the proof palette helper and restores the stock frame-setup path, stock arena start `0x801AF420`, zero file-ID `0x1B` entry, and unused helper bootstrap/payload state. Sektor colors become the native player palette by replacing the lower 32 entries of the stock 64-entry TLUT; upper 32 stock entries remain valid fallback colors.

The proof ports 33 common primary slots through `0x22` (all except Victory `0x0D` and Elbow/Combo `0x10`) using 129 unique Sektor frames. Unported/rare states retain stock control scripts but all 413 remaining direct stock-Type5 shape references are redirected to one safe Sektor stance shape. The complete stock 341-frame Type-5 corpus is therefore reclaimed.

Two shared 5-bpp Type-5 models use stock model-0 class geometry with 19,939 and 15,869 patterns. 118 Sektor frames fit inside the reclaimed stock Type-5 region and 11 overflow into the relocated file tail. File `0x87 = 0x473D8`, leaving `0x716C` bytes relative to the runtime-confirmed Fortress-working v49 size `0x4E544`.

Primary runtime gates: Fortress stage load + Inventory; Prison first doorway + Inventory; representative movement/ground/aerial/fall/recovery actions; observe rare/unported states only for bounded placeholder behavior.


### v54 expanded takeover

**Partially runtime-tested; superseded by v55 for Run / Sweep Fall / Throw presentation.**

Final disposable proof: `MKMSZR_mkt-sektor-run-combo-throw_common-proof_v54.z64`.

Identity:
- SHA-256 `7f11e7e462a8e9a5fb028a62e5281989480dd3eb19bdc5d281241113caf1876a`;
- CRC1/CRC2 `A6256DA8 / 9F9B13D5`;
- file ID `0x87 = 0x4E154`;
- `0x3F0` bytes below the runtime-confirmed Fortress-working v49 footprint `0x4E544`.

v54 adds six genuine Sektor Run frames while preserving MKMSZ's native run loop and omitting MKT's footstep callback. Primary `0x10` keeps MKMSZ's exact 17-word four-segment Elbow/Combo grammar and replaces only its 13 visual positions with ten genuine `RBELBOCOMBO` poses.

The Throw interpretation is corrected: MKMSZ's attacker Throw body at `+0x8F8` is 12 words with nine visual positions `[0,1,3,4,5,6,7,9,10]`. Later shape references previously counted as extra Throw frames belong to the adjacent reaction/flip block at `+0x928` and are left outside Throw ownership.

Sektor's longer slave-arm throw is downsampled into seven exact offline-flattened mechanical-arm composites:
`+0x2318,+0x2340,+0x237C,+0x2390,+0x23B8,+0x23CC,+0x2408`,
with genuine `RBSTANCE7` at entry/exit. MKT codec 15 is decoded offline; the MKT slave-animation ABI is not imported.

The generated corpus totals 152 frames: 129 inherited v53 + 6 Run + 10 Combo + 7 Throw keyframes. One shared 5-bpp dictionary is addressed by 16 entropy-model records; independent software decode checks every frame byte-for-byte against its exact source pixels. The optional v53 cross-check verifies all 129 inherited frames against the runtime-confirmed v53 ROM.

Runtime test matrix:
- Run;
- full Elbow/Combo;
- Grab/Throw;
- Fortress -> gameplay -> Inventory;
- Prison -> first doorway -> Inventory.



Runtime result for v54 on 2026-09-21:
- **Run mapping failed semantically:** ordinary Run still displayed the stance fallback, while the imported six-pose cycle appeared during Push. Static correction: `+0x1B0` is Push; the actual twelve-visual Run loop is `+0xEE8`.
- **Sweep Fall failed:** gameplay/emulation hard-hung after the second visible pose. Static correlation: the next frame is the first one assigned to a v54 Type-5 model containing a 0-bit normal class. This is a strong causal inference, not yet runtime-confirmed as the sole cause.
- **Throw mostly worked:** grab/throw gameplay and composite geometry were usable, but the mechanical arm rendered red because codec-15 indices were interpreted through the body palette, and the arm choreography appeared one native MKMSZ visual tick ahead of the actual grab.

### v55 Run / Sweep-Fall / Throw repair

**Partially runtime-confirmed; Run failed visually; Sweep Fall still pending.**

Disposable proof: `MKMSZR_sektor-run-sweep-throw_common-proof_v55.z64`.

Identity:
- SHA-256 `13dd4c9247bf4b1154d3b7563412333c6e21f68569155f742e683fbc29635ebc`;
- CRC1/CRC2 `A624ABE8 / 48D2A010`;
- file ID `0x87 = 0x4D0A4`;
- `0x14A0` (5,280 bytes) below runtime-confirmed Fortress-working v49 `0x4E544`.

v55 keeps the v54 Combo content but repairs the three observed problem areas. The true MKMSZ Run loop at `+0xEE8` contains twelve distinct visuals. Odd Sektor poses `RBRUN1/3/5/7/9/11` come from MKT N64; the six even poses come from PS1 MKT `CODE/ROBOT.BIN +0x140C` / `CHARS1/ROBOT.DAT`, which preserves the full twelve-frame run that N64 cut. Push remains a separate seven-visual loop at `+0x1B0`.

The six PS1-derived even poses are decoded from PS1 POVBQ, palette-converted into the native Sektor TLUT, and re-encoded as MKMSZ Type-5. Shared-dictionary optimization needs only 18 supplemental 2x4 patterns; the converted PS1 targets are reproduced exactly (`VQ_RMSE = 0`, 100% exact opaque pixels).

All 52 generated Type-5 model records now require every normal class width to be at least 1 bit. Throw's seven flattened arm phases use the genuine MKT `MECARM_P` gray-metal ramp mapped as `1->17, 2->19, 3->20, 4->22, 5->24, 6->25, 7->26`. The nine attacker slots are shifted to `stance, stance, arm1..arm7`, delaying visuals by one native MKMSZ slot without changing victim/gameplay timing.

Two clean builds are byte-identical. Independent structural audit confirms the 12 distinct Run shape roots, separate 7-frame Push loop, one-slot Throw shift, stock Throw separators, 52 Type-5 models with minimum normal width 1 bit, and the exact file-table footprint. The builder additionally round-trips all 158 emitted Type-5 frames and optionally verifies all 129 inherited v53 frames byte-for-byte.

Runtime test matrix:
- ordinary Run: all twelve poses, no stance fallback;
- Push: still animates separately and remains stable;
- Sweep Fall + Sweep Getup: specifically reproduce the former hard-hang route;
- Grab/Throw: gray arm and one-tick visual sync correction;
- full Elbow/Combo regression;
- Fortress -> gameplay -> Inventory;
- Prison -> first doorway -> Inventory.

Runtime result on 2026-09-21:
- Grab/Throw: **Runtime-confirmed** on the tested route. Mechanical arm color now reads as metal/gray and the one-slot visual delay feels synchronized; user described the result as “perfect” and “awesome.”
- Fortress -> gameplay -> Inventory: **Runtime-confirmed pass**.
- Prison -> first doorway -> Inventory: **Runtime-confirmed pass**.
- Run: **Runtime-confirmed failure**. Odd N64 poses render, but every PS1-derived even pose collapses to a few tiny artifacts. Static postmortem found the PS1 POVBQ emitter failed to advance its destination pointer by four pixels after each 2x4 block; all blocks overwrote the same four-column strip.
- Full combo: gameplay reaches **6 hits**, but at least one middle impact uses an incorrect/neutral visual; visual mapping remains incomplete.
- Sweep Fall + Sweep Getup: still pending a v55 runtime result.


### v56 corrected PS1 Run decode

**Static/implementation-confirmed; runtime pending.**

Disposable proof: `MKMSZR_sektor-run-decode_common-proof_v56.z64`.

Identity:
- SHA-256 `eea8d47b4ed2fb94be891724097a97c74c94bff4703cd6f66a5bc5da25d892c0`;
- CRC1/CRC2 `A6256A28 / 73BE34AB`;
- file ID `0x87 = 0x4E414`;
- `0x130` (304 bytes) below runtime-confirmed Fortress-working v49 `0x4E544`.

v56 changes only the six PS1-derived even Run poses relative to v55. The PS1 POVBQ output pointer now advances by four pixels after each 2x4 vector, matching the independent decoder implementation for all six donor frames. A separate cross-check also requires each corrected source frame to occupy more than 30 nonzero columns, specifically rejecting the v55 four-column overwrite failure.

The corrected full-body PS1 frames add much more real pattern content than v55's malformed strips. To stay under the known Fortress-safe footprint, v56 uses 256 representative supplemental patterns with exact transparency masks and 64 Type-5 entropy models. The six even poses are therefore a bounded visual approximation rather than lossless: color-space RMSE ~4.504 in 5-bit RGB units and 36.3% exact opaque indices, while pose geometry and transparency silhouettes remain exact. The final shared dictionary has 40,833 patterns.

Two independent clean builds are byte-identical and builder-side Type-5 round-trip passes for all 158 emitted frames.

Runtime test matrix:
- ordinary Run: verify twelve full-body poses with no tiny-artifact frames;
- Push regression;
- Grab/Throw regression;
- full Combo regression (known missing middle visual remains expected);
- Sweep Fall + Sweep Getup;
- Fortress -> gameplay -> Inventory;
- Prison -> first doorway -> Inventory.


Runtime result on 2026-09-21:
- ordinary Run: **Runtime-confirmed visual failure**. N64-derived odd poses are clean; PS1-derived even poses render as heavily speckled/checkerboard full-body frames.
- Sweep Fall -> Sweep Getup: **Runtime-confirmed pass** on the tested route; the former hard hang is gone.
- Grab/Throw: **Runtime-confirmed pass**; remains visually/timing-correct.
- Fortress -> gameplay -> Inventory: **Runtime-confirmed pass**.
- Prison -> first doorway -> Inventory: **Runtime-confirmed pass**.

Postmortem: v56 fixed the four-column output-cursor bug, but the resulting PS1 Run source itself still decodes with corrupted-looking internal pixel/color structure. The earlier “PS1 ideal” comparison was only the output of that same unverified pipeline, not ground truth. Rendering PS1 odd Run poses with their native PS1 palette shows the same speckling even before N64 conversion. Therefore the PS1 POVBQ Run donor path is **Rejected / unresolved**, and further Type-5/VQ tuning against those buffers is not meaningful.


### v58 stride-corrected full Run

**Runtime-confirmed on 2026-09-21 for ordinary Run.**

Disposable proof: `MKMSZR_sektor-run-stride_common-proof_v58.z64`.

- SHA-256 `bc15eed845b9d97c785acf828e593d5683d6a8f905bfb475b751160774d973e2`
- CRC1/CRC2 `A6256DD8 / DB8E6E81`
- file `0x87 = 0x4E3FC`, leaving `0x148` bytes relative to runtime-confirmed Fortress-working v49 `0x4E544`

v58 corrects the v57 ROBO8 source-row bug by reading Midway WIMP images with `align4(xsize)` source pitch. The final `+0xEE8` Run loop contains twelve distinct Sektor poses. Builder-side Type-5 round-trip and two-build reproducibility checks pass. Runtime result: the user reported that Running works perfectly; the former diagonal/slashed even-frame corruption is gone.


### v59 complete Combo visuals

**Runtime-confirmed on 2026-09-21 for the Combo presentation fix.**

Disposable proof: `MKMSZR_sektor-full-combo_common-proof_v59.z64`.

- SHA-256 `b8b1ddfa964de4da86dc9598f99139f4c50ac066deaaf4ab5cd91fda63baf1cc`
- CRC1/CRC2 `A6256DD8 / DB8E6E81`
- file `0x87 = 0x4E3FC`, unchanged from v58

v59 preserves the six-hit combo gameplay/control records byte-for-byte and keeps the primary `0x10` four-segment `RBELBOCOMBO` visual grammar. Static tracing showed the remaining neutral/missing middle visuals came from late Knee segments selected by the existing combo chain. Six late Knee shape references are redirected to already-resident Sektor Spin-Kick/Knee frames, with intervening controls/separators unchanged. No new frame assets or file-0x87 growth are introduced.

Runtime result: the user reported v59 works perfectly. This closes the known missing middle-Combo visual defect. v58 remains the runtime-confirmed full-Run baseline; no unrelated v59 routes are newly claimed as re-tested.
