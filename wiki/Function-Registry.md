# Function registry

> **Scope:** This page is the canonical owner for **function semantics**: what a routine does, its relevant calling/behavioral meaning, evidence level, and stage/overlay scope where applicable.
>
> It does **not** own continuous allocation ranges or exact ROM patch guards/replacements. Those belong to [Memory and allocation map](Memory-and-Allocation-Map) and [Address and patch-site registry](Address-and-Patch-Site-Registry). [Address quick reference](Address-Quick-Reference) is derivative only.

Unless marked PS1, addresses are N64 USA Rev. 0. Overlay functions are stage-specific even when displayed as absolute VAs. A function that is patched may still appear here for semantics; the edit itself remains canonical in the patch-site registry.

## Global N64 functions

| Address | Function | Evidence | Notes |
|---:|---|---|---|
| `0x8000D0B8` | Debug stage-select menu | Runtime-confirmed | Production A-button title route |
| `0x8000322C` | Embedded image decompression dispatcher | Static-confirmed | Ordinary types come from header byte `+3`; exact header `0x05000000` is special-cased to fighter codec type 5. Type 4 dispatches to `0x80003428`; type 5 dispatches through `0x80003314` |
| `0x80003428` | Type-4 embedded image decoder | Static-confirmed | Separate control/token streams with a 1024-byte ring buffer; exact decode reproduced Water embedded Potion frames byte-for-byte against Fire external Potion payloads |
| `0x80003314` | Type-5 fighter-image wrapper | Static-confirmed | Resolves image-relative model/dictionary pointer, compressed stream at image `+0x0C`, packed dimensions, output arena pointer; calls `0x80065E00`; advances output by `align4(width) * align2(height)` |
| `0x80065E00` | Type-5 fighter-image decoder | Static-confirmed | Decodes native fighter data in 2-row x 4-pixel blocks from a per-image model/dictionary table; stock Sub-Zero frames use this path |
| `0x80015088` | Stage transition handler | Static-confirmed | Copies selection to current-stage state |
| `0x8001C528` | Presentation resource / palette-selector loader | Static/runtime-confirmed at known callers | Pickup manager calls it with record `+0x28` presentation pointer + 4. Separately, animation token-`0x0B` handler `0x80030974` calls it with fixed record `0x800B1A24`, `a1=0x100`, `a2=0`; on success the handler stores `(return - 0x80)` to the newly constructed actor `+0x9E` before insertion. This establishes the straight-Ice projectile's pre-insertion selector bind; broader internal resource semantics remain bounded to the traced callers. |
| `0x80024650` | Active actor-list insertion helper | Static-confirmed | Used by the Zap animation token-`0x0B` secondary-actor path after resource-backed construction |
| `0x800281A0` | Resource-entry resolver/actor setup wrapper | Static-confirmed | Receives pointer to one outer-selector entry, loads its file-relative descriptor offset, adds current stage resource base, then calls `0x80028128` |
| `0x8002830C` | Generic controller/process allocator/clone | Static-confirmed | Allocates a controller/process with supplied class/type and callback, links it into the controller list, and inherits current controller actor/animation/context fields; used by projectile bridge `0x8004CBC4` |
| `0x80028128` | Resource-backed actor constructor helper | Static-confirmed | Consumes direct descriptor pointer produced by `0x800281A0` |
| `0x8001BF70` | Gameplay HUD texture-slot initializer | Static-confirmed | Called six times from `0x8005BFB0` after image decode; initializes fixed HUD texture slots `0x11..0x16`; backing pointers are written through table base `0x800ED940`. v11's attempt to create independent fixed slot `0x17` with a second call is rejected: it rendered corrupted/noisy content despite intact stock HUD. |
| `0x8001C2B4` | Dynamic texture/screen-image allocator | Static-confirmed | Searches IDs `0x200..0x2FF`. New allocations round width up to 32 for backing capacity, populate the 16-byte record at `0x802E83F0 + id*0x10`, set `+0x0E = 1`, and publish `0x800ED940[id]`. Reuse may return an inactive capacity-compatible record without refreshing `+0x08`; stock callers therefore rewrite `record+0x08` with the current source-image width after allocation. |
| `0x8001E578` | Context-specific render family | Static-confirmed | Not a universal gameplay-HUD API |
| `0x8001F7A8` | Gameplay textured-node renderer | Static/runtime-confirmed | Used by the gameplay HUD queue. Node `+0x4A` is texture-slot ID; node `+0x4C` is palette selector. For the CI8 path the renderer reads slot-record `+0x08` and emits it as the RDP `SetTextureImage` DRAM image width, then loads the node's `+0x10/+0x12 .. +0x20/+0x22` source rectangle through load tile 7 and renders through tile 0. The stock Toasty-hook source node supplies S/T `0,0`, step `1,1`, and point-filter mode. Palette selector resolves through `0x80290A00 + id*8` and `0x802E73E0 + index*4` to a hardware-ready CI8 RGBA5551 TLUT. |
| `0x8001EAE4` | Render-node submit | Runtime-confirmed | Gameplay HUD queue; v08 confirms additional textured-node submission, and v09 runtime-confirms texture slot binding through node halfword `+0x4A` |
| `0x80017F80` | Actor motion/update integrator | Static-confirmed | Normal actor path (`+0xDC==0`) reads local velocity `+0x14/+0x18`, shifts `>>8`, rotates through actor orientation, and adds `3x` transformed components to fixed8 world position `+0x2C/+0x30/+0x34`; called once per gameplay movement/render loop at `0x80014258` |
| `0x8002018C` | Render-node allocator | Runtime-confirmed | Allocates `0x58`-byte node |
| `0x80028F3C` | Main player locomotion/state process | Static-confirmed | Normal horizontal state reads semantic input through controller `+0x638`, records active Left/Right at `+0x68C`, derives opposite-facing marker `+0x704`, and selects forward/backward locomotion |
| `0x80030178` | Forward locomotion setup | Static-confirmed | Loads fighter-specific forward movement parameters, sets movement state, and returns selector `1` for primary animation slot `0x01` |
| `0x80030208` | Backward locomotion setup | Static-confirmed | Loads fighter-specific backward movement parameters, sets movement state, and returns selector `2` for primary animation slot `0x02` |
| `0x8003188C` | Actor facing flip | Static-confirmed | Toggles actor `+0x8C bit 0x10` and runs native frame/setup helper `0x8001BDA0`; preferred facing primitive over a raw bit write |
| `0x8003D86C` | Native turn-action routine | Static-confirmed | Selects primary animation slot `0x03` (`turn`) and runs the stock turn-action sequence through the current controller; not intrinsically player-only |
| `0x8004A6E8` | Controller face-policy scanner | Static-confirmed | Scans controller classes `2..5` and returns `0x8000` if any located controller has `+0x6BC & 0x0200`, otherwise `0x4000`; exact higher-level gameplay name/caller remains unresolved |
| `0x80031D00` | Find nearest opponent controller | Static-confirmed | Scans the two opponent controller classes used by the player-facing helpers and returns the nearest X-distance candidate |
| `0x80031EF0` | Face opponent | Static-confirmed | Resolves desired side through `0x80031DDC` and calls `0x8003188C` only when actor facing differs |
| `0x8002B1EC` | Player horizontal-velocity helper | Static-confirmed | Writes actor `+0x14` and `+0x58`; corrected movement primitive |
| `0x8002E104` | Central XP award | Static-confirmed | Current XP at `0x8011200C` |
| `0x8002EC78`, `0x8002ECF4` | Player construction path | Static-confirmed | Not enemy loader |
| `0x8002FCDC` | Lower-level fighter allocator | Static-confirmed | Stores fighter type at actor `+0x78` |
| `0x80030974` | Animation control-token `0x0B` handler | Static-confirmed | Drives Zap/resource secondary-actor creation through `0x80034510`; captures the newly constructed actor at `+0x714`, restores the owner to `+0x6E0`, advances the animation cursor, calls `0x8001C528(0x800B1A24,0x100,0)`, stores `(return-0x80)` at actor `+0x9E`, copies `+0x714 -> +0x648`, then inserts the secondary actor with `0x80024650`. This separates constructor descriptor choice from the actor's pre-insertion presentation/palette selector. |
| `0x80031394` | Actor origin/facing/render-anchor aligner | Static-confirmed; unsafe v78 usage Runtime-confirmed | Copies owner `+0x2C/+0x30` to child; branches on child `+0x64 & 2`, may call `0x8003188C`, otherwise reads child render record `+0x7C` and adjusts X/Y by descriptor geometry. v78 direct use before the rocket descriptor hard-hung; prerequisite actor/descriptor state is unresolved. |
| `0x80031208` | Facing-aware local-XY to world-position adjustment | Static-confirmed | On fresh projectile path `+0xDC==0`, consumes signed whole local X/Y, mirrors X for flip bit `0x10`, rotates `(x,y,0)` by actor orientation with unity matrix scale, then adds integer world delta `<<8` to actor `+0x2C/+0x30/+0x34`; stock straight-Ice call `0x8004AFF8` supplies `+0x648`, the same staged actor later transferred from `+0x714` |
| `0x80032CD4` | Special-action callback installer | Static-confirmed | Installed top-level callback must transfer/nonreturn |
| `0x80034510` | Animation-stream resource actor creation helper | Static-confirmed | Consumes the resource entry following token `0x0B`, reaches `0x800281A0 -> 0x80028128`, and participates in staging a secondary actor while preserving the owner actor |
| `0x80038770` | Generic stage key/crystal pickup | Static-confirmed | Stage-dependent parameter mapping |
| `0x800388FC` | Potion pickup | Runtime-confirmed | Adds inventory ID `0x01` |
| `0x8003892C` | Shield pickup | Runtime-confirmed | Adds ID `0x06` |
| `0x8003895C` | Eye pickup | Static/runtime-confirmed | Adds ID `0x03` |
| `0x8003898C` | Formula pickup | Static/runtime-confirmed | Adds ID `0x02` |
| `0x800389BC` | Herbs pickup | Runtime-confirmed | Adds ID `0x04` |
| `0x800389EC` | Health urn pickup | Static/runtime-confirmed | Adds ID `0x05` |
| `0x80038A1C` | Extra-life urn pickup | Static-confirmed | Ordinary catalog callback |
| `0x80038A58` | Mana pickup | Static-confirmed | Native mana, distinct from Herbs despite legacy Lua substitution |
| `0x80038A90` | Strength urn pickup | Static-confirmed | Adds ID `0x0B` |
| `0x80038ACC` | Pickup manager | Static/runtime-confirmed | Production restore hook |
| `0x800490CC` | Shinnok Amulet pickup | Static-confirmed | Adds ID `0x23`; outside ordinary tables |
| `0x8004AA4C` | Special-action scheduler context-transfer shim | Static-confirmed | Dispatch table at `0x800A1050`; not a generic initializer |
| `0x8004AB84` | Complete ice-projectile action root | Static-confirmed | Includes special lock behavior |
| `0x8004AB0C` | Ice blue screen-tint process callback | Static-confirmed | Calls `0x80044964(0x80,0x80,0xC0,0x80,6)` then native process exit `0x80028564`. Separate from companion actor and projectile child processes. |
| `0x80060A3C -> 0x80060D14` | Ice companion-actor constructor / per-process update | Static-confirmed | Class-`0x100` helper allocates texture/palette, constructs and inserts two visible actors, advances and copies script frames; removes both and releases resources at `0x80060E20..44` before process exit. Parent staging coordinates/script/secondary pointer are inputs, so its spawn is not a pure visual switch. |
| `0x8004B82C` | Ice-projectile flight callback | Static-confirmed | Supersedes old player-action interpretation |
| `0x8004CBC4` | Projectile child-process bridge | Static-confirmed | Allocates a child through `0x8002830C` with class/tag `0x700`, copies parent/opponent context, binds parent `+0x714` to child actor `+0x6E0`, tags that actor `0x700`, and clears parent `+0x648`; parent `+0x714` is not cleared here |
| `0x8004CC14` | Projectile velocity/animation-rate setup helper | Static-confirmed | Writes facing-aware projectile actor `+0x14`, then calls `0x80031724` with the supplied rate; suitable as a setup primitive, not player propulsion and not yet established as the generic per-tick acceleration primitive |
| `0x8004CC50` | Generic projectile flight/collision loop | Static-confirmed | Latches child callback `+0x70C -> +0x680` once at entry; each iteration sleeps/updates animation, performs offscreen/lifetime checks, calls `+0x680` when nonzero, then resolves strike semantics through `0x8004CE6C/0x8004CF3C`; does not itself rewrite projectile actor `+0x14` velocity between callbacks |
| `0x8004CDF8` | Projectile actor/child process exit | Static-confirmed | Removes actor through `0x80028408/0x80024B00`, then terminates the active projectile process through `0x80028564`; reached on generic flight offscreen/lifetime paths. |
| `0x8004B524` | Ice parent special-action exit | Static-confirmed | Clears special lock `0x800BF308` and invokes `0x800328FC` on the current owner actor after parent recovery. |
| `0x8004CE6C` | Projectile strike-record resolver | Static-confirmed | Uses projectile fighter type plus supplied selector to resolve the target fighter strike table before dispatch |
| `0x8005BFB0` | Gameplay HUD function | Static/runtime-confirmed | Contains 13 submit calls |
| `0x800615D8` | Frontend fade/normalization | Static/runtime-confirmed | Preserved after logo bypass with argument `0x80` |
| `0x8006352C` | Auxiliary trigger-record spawner | Static-confirmed | Hardcodes fighter type `7` |
| `0x80064C18` | Native gameplay SFX wrapper | Static-confirmed | Indexes 10-byte descriptor table at `0x800A1730`; resolves raw sound ID and variation parameters, then calls `0x80080A88` |
| `0x80080A88` | Raw sound-ID playback entry | Static-confirmed | Selects a 16-byte runtime sound definition by raw ID and dispatches through `0x8007EC4C` |
| `0x8007EC4C` | Low-level sound-definition/voice allocator | Static-confirmed | Consumes resolved runtime sound definition and allocates/starts native audio voices |
| `0x80065D64` | Raw global-file loader | Runtime-confirmed | Used by native bootstrap |
| `0x80066360` | Cold arena initializer | Static-confirmed | Initializes both arena base/floor `0x800EECD0` and live bump cursor `0x80111ECC` to the stock hardcoded arena start, with initial boundary bookkeeping |
| `0x80066390` | Arena cursor reset | Static-confirmed | Copies persistent/reset arena base `0x800EECD0` into live bump cursor `0x80111ECC`; production bootstrap uses this after relocating the arena floor |
| `0x800663A8` | Arena base advance/set helper | Static-confirmed | Advances/sets the persistent arena base and then resets the live cursor to it; lifecycle/base management rather than a general allocator |
| `0x800663E0` | Arena hard-reset helper | Static-confirmed | Restores the arena base to the hardcoded initial floor, then resets the live cursor; fresh stage setup reaches this family |
| `0x80066410` | Arena next-payload peek | Static-confirmed | Returns `cursor + 8` without allocating; usable as a checkpoint compatible with `0x80066478` rewind semantics |
| `0x80066420` | Arena remaining-capacity query | Static-confirmed | Computes `(0x80290990 - cursor) >> 3`, i.e. remaining 8-byte units below the bump boundary |
| `0x8006643C` | Main arena bump allocator | Static-confirmed | Aligns request to 8 bytes, returns `old_cursor + 8`, advances the live cursor, and writes 8-byte allocation bookkeeping at the new cursor. No bounds check is performed internally. |
| `0x80066478` | Arena rewind helper | Static-confirmed | Sets live cursor to `pointer - 8`; rewinds the arena to the state before the referenced allocation/checkpoint |
| `0x8006648C` | Top-allocation rewind/reallocate helper | Static-confirmed | Rewinds with `0x80066478` and immediately allocates again through `0x8006643C`; no copy is performed |
| `0x80071500` | Ordinary-enemy command interpreter | Static-confirmed | Stream pointer from `0x800C11E4` |
| `0x800719F0` | Enemy spawn-parameter helper | Static-confirmed | Receives spawn index and type |
| `0x80071B20` | Shared enemy/fighter constructor | Static/runtime-confirmed | Uses resource slot table `0x800B14C0` |
| `0x80073CEC` | Alternate renderer-family entry | Static-confirmed | Calls `0x8001E578`; not universal HUD path |
| `0x80073E74` | Native text draw | Runtime-confirmed | Arbitrary custom RDRAM strings work |
| `0x80074084` | Text-width helper | Static/runtime-confirmed | Native font at `0x800B1E20` |
| `0x800741B4` | Inventory item count | Static-confirmed | Native ten-slot inventory |
| `0x80074FBC` | XP tier evaluator/clamp | Static-confirmed | Uses cap table `0x800A63FC` |
| `0x80075320` | Find first inventory item | Static-confirmed | Inventory helper |
| `0x80075448` | Insert inventory item | Runtime-confirmed | Called by fixed pickup callbacks |
| `0x80078A18` | Save loader XP restore | Static-confirmed | XP in save record `+0x7C` |
| `0x80078C40` | Title handoff after frontend flow | Static-confirmed | Called after fade normalization |
| `0x80079510` | Owning legal/logo/title routine | Static-confirmed | Contains two logo presentations |
| `0x800798A8` | Automatic stage-save flow | Static/runtime-confirmed | Generic routine remains intact |
| `0x8007AD00` | Stock inventory sanitizer | Runtime-confirmed/replaced | Production replaces with stage-key mask copy |
| `0x8007AD4C` | Stock default-inventory loader | Runtime-confirmed/replaced | Production reconstructs live window |

## Stage-overlay callbacks

| Address | Scope | Meaning |
|---:|---|---|
| `0x802F0EBC` | Fire | Three stage-icon awards, parameter `0..2` |
| `0x802F2CB4` | Wind | Circle/Triangle/Three Bars award callback |
| `0x802F2448` | Water | Triangle/Three Bars/Moon award callback |
| `0x802F52B0` | Earth | Square/Four Squares/Triangle award callback |
| `0x802EF178` | Bridge | Omega/Rings/Arrow award callback |

## PS1 counterparts

| Address | Meaning |
|---:|---|
| `0x8002A688` | Level selector |
| `0x80031E98` | Selector confirm path |
| `0x8003955C -> 0x80039A3C -> 0x80039B50 -> 0x80041BF0` | Enemy interpreter/spawn/constructor/allocation chain |
| `0x8004A920` | Glyph renderer |
| `0x8004ACD4` | Text renderer |
| `0x8004AEEC` | Text width |
| `0x8004C0B0` | Inventory insertion |
| `0x8005499C` | Pickup manager |
| `0x80090B94` | Save checksum |
| `0x80090BCC` | Save initialization |

See [N64–PS1 comparison](N64-PS1-Comparison) before transferring any concept between ports.


## Related canonical references

- [Core runtime and native payload](Core-Runtime-and-Address-Database) — bootstrap/payload call composition and lifecycle.
- [Memory and allocation map](Memory-and-Allocation-Map) — continuous ROM/RDRAM ownership and availability.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded edit sites, displaced/original words, and replacement effects.
- [Address quick reference](Address-Quick-Reference) — derivative orientation-only subset.
