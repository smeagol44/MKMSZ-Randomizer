# Function registry

Unless marked PS1, addresses are N64 USA Rev. 0. Overlay functions are stage-specific even when displayed as absolute VAs.

## Global N64 functions

| Address | Function | Evidence | Notes |
|---:|---|---|---|
| `0x8000D0B8` | Debug stage-select menu | Runtime-confirmed | Production A-button title route |
| `0x8000322C` | Embedded image decompression dispatcher | Static-confirmed | Ordinary types come from header byte `+3`; exact header `0x05000000` is special-cased to fighter codec type 5. Type 4 dispatches to `0x80003428`; type 5 dispatches through `0x80003314` |
| `0x80003428` | Type-4 embedded image decoder | Static-confirmed | Separate control/token streams with a 1024-byte ring buffer; exact decode reproduced Water embedded Potion frames byte-for-byte against Fire external Potion payloads |
| `0x80003314` | Type-5 fighter-image wrapper | Static-confirmed | Resolves image-relative model/dictionary pointer, compressed stream at image `+0x0C`, packed dimensions, output arena pointer; calls `0x80065E00`; advances output by `align4(width) * align2(height)` |
| `0x80065E00` | Type-5 fighter-image decoder | Static-confirmed | Decodes native fighter data in 2-row x 4-pixel blocks from a per-image model/dictionary table; stock Sub-Zero frames use this path |
| `0x80015088` | Stage transition handler | Static-confirmed | Copies selection to current-stage state |
| `0x80015B54` | Resume after four-box input hook | Implementation-confirmed | Common configured-control convergence |
| `0x8001C528` | Pickup presentation loader | Static/runtime-confirmed | Called from pickup manager with record `+0x28` presentation pointer + 4; not the `+0x24` resource-selector lookup |
| `0x800281A0` | Resource-entry resolver/actor setup wrapper | Static-confirmed | Receives pointer to one outer-selector entry, loads its file-relative descriptor offset, adds current stage resource base, then calls `0x80028128` |
| `0x80028128` | Resource-backed actor constructor helper | Static-confirmed | Consumes direct descriptor pointer produced by `0x800281A0` |
| `0x8001BF70` | Gameplay HUD texture-slot initializer | Static-confirmed | Called six times from `0x8005BFB0` after image decode; initializes fixed HUD texture slots `0x11..0x16`; backing pointers are written through table base `0x800ED940`. v11's attempt to create independent fixed slot `0x17` with a second call is rejected: it rendered corrupted/noisy content despite intact stock HUD. |
| `0x8001C2B4` | Dynamic texture/screen-image allocator | Static-confirmed | Searches IDs `0x200..0x2FF`; successful allocation initializes the 16-byte slot record at `0x802E83F0 + id*0x10`, sets active halfword `+0x0E = 1`, records backing pointer in `0x800ED940[id]`, and returns the ID; failure returns `-1` |
| `0x8001E578` | Context-specific render family | Static-confirmed | Not a universal gameplay-HUD API |
| `0x8001EAE4` | Render-node submit | Runtime-confirmed | Gameplay HUD queue; v08 confirms additional textured-node submission, and v09 runtime-confirms texture slot binding through node halfword `+0x4A` |
| `0x8002018C` | Render-node allocator | Runtime-confirmed | Allocates `0x58`-byte node |
| `0x8002B1EC` | Player horizontal-velocity helper | Static-confirmed | Writes actor `+0x14` and `+0x58`; corrected movement primitive |
| `0x8002E104` | Central XP award | Static-confirmed | Current XP at `0x8011200C` |
| `0x8002EC78`, `0x8002ECF4` | Player construction path | Static-confirmed | Not enemy loader |
| `0x8002FCDC` | Lower-level fighter allocator | Static-confirmed | Stores fighter type at actor `+0x78` |
| `0x80032CD4` | Special-action callback installer | Static-confirmed | Installed top-level callback must transfer/nonreturn |
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
| `0x80039418` | Pickup collected-flag store site | Static/runtime-confirmed | Production capture hook |
| `0x800490CC` | Shinnok Amulet pickup | Static-confirmed | Adds ID `0x23`; outside ordinary tables |
| `0x8004AA4C` | Special-action scheduler context-transfer shim | Static-confirmed | Dispatch table at `0x800A1050`; not a generic initializer |
| `0x8004AB84` | Complete ice-projectile action root | Static-confirmed | Includes special lock behavior |
| `0x8004B82C` | Ice-projectile flight callback | Static-confirmed | Supersedes old player-action interpretation |
| `0x8004CC14` | Projectile setup helper | Static-confirmed | Writes projectile actor `+0x14`; not player propulsion |
| `0x8005BFB0` | Gameplay HUD function | Static/runtime-confirmed | Contains 13 submit calls |
| `0x800615D8` | Frontend fade/normalization | Static/runtime-confirmed | Preserved after logo bypass with argument `0x80` |
| `0x8006352C` | Auxiliary trigger-record spawner | Static-confirmed | Hardcodes fighter type `7` |
| `0x80064C18` | Native gameplay SFX wrapper | Static-confirmed | Indexes 10-byte descriptor table at `0x800A1730`; resolves raw sound ID and variation parameters, then calls `0x80080A88` |\n| `0x80080A88` | Raw sound-ID playback entry | Static-confirmed | Selects a 16-byte runtime sound definition by raw ID and dispatches through `0x8007EC4C` |\n| `0x8007EC4C` | Low-level sound-definition/voice allocator | Static-confirmed | Consumes resolved runtime sound definition and allocates/starts native audio voices |\n| `0x80065D64` | Raw global-file loader | Runtime-confirmed | Used by native bootstrap |
| `0x80066390` | Arena synchronization helper | Implementation-confirmed | Bootstrap call |
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
