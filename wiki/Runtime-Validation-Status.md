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

**Static/implementation-confirmed; runtime pending.**

v54 adds:
- MKMSZ native run-loop visuals replaced with the six genuine Sektor Run poses from MKT primary `0x4A`, repeated across MKMSZ's 12 visual run ticks while preserving the stock loop command;
- primary `0x10` Elbow/Combo mapped to the exact 36-word MKT retail animation grammar and genuine donor frames;
- primary `0x23` Throw/Grab visuals mapped to genuine Sektor throw poses while preserving MKMSZ's native 12-word throw control grammar and avoiding MKT throw callbacks.

MKT codec 15 is now statically decoded from the public-source `uncompress_8` format (8-color RLE) and its throw frames are re-encoded to MKMSZ native Type-5. The complete v54 corpus has 154 unique Sektor frames, 35 mapped primary slots, and the explicit run-loop replacement.

Storage uses four shared Type-5 models. The eight codec-15 throw frames use a dedicated 3-bpp model; other Sektor art remains 5-bpp. Per-model normal class widths are optimized from actual pattern frequencies while preserving the native 13 normal symbols and three zero-run symbols.

File `0x87 = 0x508E4`. This is below the known failing `0x5100C` Fortress footprint by only `0x728`, so no safety claim is made. Primary gate: Fortress -> gameplay -> Inventory. Secondary gates: run; Elbow/Combo sequence; Grab/Throw; Prison doorway -> Inventory.
