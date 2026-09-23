# Experiments, failures, and superseded findings

> **Scope:** This page is the cross-domain index of durable **Rejected / failed** and superseded findings. It records only enough detail to identify the attempted path, observed failure, reusable lesson, and canonical page containing the full evidence.
>
> It is **not** a proof-history page. Version chronology, artifact hashes, complete routes, and extended diagnostics stay with the owning domain.

Keep an entry here when the negative result establishes a safety constraint, rules out an architectural assumption, explains why an approach was abandoned, provides a meaningful negative control, or prevents expensive work from being repeated.

## Address, action, and lifecycle corrections

| Attempt / scope | Observed failure or correction | What it established | Detailed owner |
|---|---|---|---|
| Treat current-process global as `0x802FCE20` | Address interpretation was wrong | Signed low immediate `0xCE20` paired with `lui 0x802F` yields effective address `0x802ECE20` | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Use `0x8004CC14` as player propulsion | Movement model was based on projectile setup | `0x8004CC14` owns projectile setup; player velocity uses `0x8002B1EC` | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Treat `0x8004B82C` as a player action | Caller/data flow contradicted the interpretation | It is the ice-projectile flight callback | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Treat `0x8004AA4C` as a generic initializer | Later selector analysis showed scheduler transfer semantics | Action adapters must preserve target scheduler/context-transfer behavior | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Return normally from a top-level callback installed by the special-action path | Reverse Elbow v3 immediately self-reentered/hung | Installed callbacks must transfer through proven scheduler/native cleanup rather than ordinary `jr ra` | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Reverse Elbow v5 omitted native special lock `0x800BF308` | Lifecycle model remained unstable/incomplete | Native action-lock state is part of the host action contract | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| XP final threshold read as 7345 | Value was misread | Canonical value is `0x1CBA = 7354` | [XP and progression](XP-and-Progression) |

## Pickup, resource, and materialization failures

| Attempt / scope | Observed failure | What it established | Detailed owner |
|---|---|---|---|
| Change pickup callback/type only | Award and art could diverge or change incompletely | Ordinary pickup identity must move as the complete `+0x10..+0x2B` slice | [Pickups and item randomization](Pickups-and-Item-Randomization) |
| Copy Prison key into Fire without importing its resource | Foreign item was absent/unusable | Pickup `+0x24` is stage-local; the foreign bundle must be resident | [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Treat a zero outer resource slot as physical storage | Rejected before production use | Zero selector capacity is not evidence of free backing bytes | [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Reuse an occupied no-pickup slot without a global reference trace | Rejected as unsafe | Non-pickup actors/scripts may still own the slot | [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Build the global pickup pool before the import/materialization planner | Deferred as an unsafe ordering | Stage-local production was the bounded safe scope until destination resources could be materialized | [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |
| Destination-shell visual with logical award only | Rejected before runtime promotion | 1.0 requires the pickup visual/resource identity to match the randomized item | [Global item materialization and solvability](Global-Item-Materialization-and-Solvability) |

## Enemy-randomization failures

| Attempt / scope | Observed failure | What it established | Detailed owner |
|---|---|---|---|
| Fire enemy type `0x0A -> 0x01` without Temple resource | Freeze at spawn | Constructor dereferences a type-specific resource slot; type substitution alone is insufficient | [Enemy randomization](Enemy-Randomization) |
| Add Temple file after all stock Fire allocations | Would exceed the observed arena by `0x3098` | Foreign-enemy residency needs bounded replacement/reallocation, not append-after-stock | [Enemy randomization](Enemy-Randomization) |
| Imported monk proof | Fighter functioned, but normal death/despawn presentation was absent | Residency + constructor success is not complete enemy compatibility | [Enemy randomization](Enemy-Randomization) |
| Apply ordinary-enemy policy to bosses/minibosses | Rejected | Boss/state branches carry custom resources, process IDs, scripts, and transitions | [Enemy randomization](Enemy-Randomization) |

## UI and Toasty diagnostic failures

| Attempt / scope | Observed failure | What it established | Detailed owner |
|---|---|---|---|
| Direct framebuffer drawing | Unstable | Native HUD/textured-node systems are the supported rendering direction | [Native HUD and UI](Native-HUD-and-UI) |
| Treat `0x80073CEC -> 0x8001E578` as a universal gameplay sprite renderer | Toasty diagnostics did not support the assumption | Renderer/context conclusions must come from the actual textured gameplay-HUD node family | [Toasty visual research](Toasty-Visual-Research) |
| Toasty visual v01 without an independent marker | No visible image and no clean attribution | A negative visual proof needs an independent known-good execution marker | [Toasty visual research](Toasty-Visual-Research) |
| Toasty visual v03 allocator diagnostic | Persistent slot failure coincided with loss of normal music/SFX | The instrumentation was intrusive; its slot result is not clean allocator evidence | [Toasty visual research](Toasty-Visual-Research) |
| Toasty visual v06 raw-loader wrapper extending into selector-cave tail `0x9A720..0x9A753` | Mission Objective + music hang before gameplay | Do not wrap the stock raw loader or reuse that proof-cave tail for this diagnostic | [Toasty visual research](Toasty-Visual-Research) |
| Toasty visual v07 post-load helper instrumentation | Reproduced the Mission Objective + music hang with the stock loader call restored | Helper-based load instrumentation on that route is rejected; it does not prove loader success/failure | [Toasty visual research](Toasty-Visual-Research) |
| Toasty visual v11 independent fixed-slot `0x17` allocation through a second `0x8001BF70` call | Noisy/multicolored clone instead of the known-good control | Reject that fixed-slot allocation recipe; later diagnostics must isolate slot identity without assuming it | [Toasty visual research](Toasty-Visual-Research) |

The earlier blanket statement that textured-image rendering was unproven is superseded: later Toasty work confirms the image/texture path at its documented bounded scope. The rejected entries above remain useful only for the diagnostic paths they rule out.

## Reverse Elbow and MKT-adapter failures

| Attempt / scope | Observed failure | What it established | Detailed owner |
|---|---|---|---|
| Reverse Elbow v1-v2 early behavioral recreation | Minimal movement/incomplete presentation; experimental victim callback could hard-hang on contact | Separate host lifecycle, movement calibration, victim semantics, and donor semantics instead of changing them together | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Reverse Elbow v3 ordinary return | Immediate hang with or without an enemy | Callback self-reentry is a host lifecycle hazard, not an enemy-contact issue | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Reverse Elbow v4-v5 incomplete scheduler/action-root emulation | Unstable/incomplete action lifecycle | Native scheduler transfer, lock, bounded loops, and cleanup are required together | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Reverse Elbow v8: velocity `0xD0000`, locomotion index `controller+0x6E6`, per-tick reapply, forced crossover `+0x3800` | Intended speed/pass-through was not observed; attacks could stop motion; expanded diagnostics were absent | These exact parameters are failed-proof reproduction data, not accepted movement values | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| Forced-X crossover as donor pass-through | Did not reproduce donor behavior | MKT pass-through is ordinary movement plus temporary three-tick repulsion suppression, not a teleport/fixed-position write | [MKT adapter primitives](MKT-Adapter-Primitives) |
| Direct retail-instruction relocation as a general port strategy | Rejected architecturally | PROCESS/OBJECT layouts, scheduler ABI, tables, heaps, callbacks, and resource formats are engine-local | [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer) |
| Reuse donor strike/reaction numbers as target numbers | Sektor v61 long combo caused catastrophic world/background corruption when selector `0x02` was copied numerically | Translate reaction meaning into MKMSZ-native semantics; numeric equality is not compatibility | [MKT adapter primitives](MKT-Adapter-Primitives), [Sektor takeover proof history](Sektor-Takeover-Proof-History) |
| Copy donor animation callback/control words blindly | Rejected by the cross-engine ABI boundary | Visual frames may transfer while callback/control tokens require explicit semantic mapping | [MKT adapter primitives](MKT-Adapter-Primitives) |

## Fighter-asset and Sektor proof failures

| Attempt / scope | Observed failure | What it established | Detailed owner |
|---|---|---|---|
| Use zero-filled-looking ROM `[0xA1308,0xA1544)` as a Sektor helper cave | Input-specific hard hangs | The range contains live action/dispatch records; zero bytes are semantic data, not free space | [Sektor takeover proof history](Sektor-Takeover-Proof-History), [Memory and allocation map](Memory-and-Allocation-Map) |
| Sektor v20 accumulated raw-resource growth | Whole-scene corruption before Crouch Low Kick was selected | The failure was a composition/resource-pressure boundary, not evidence against that animation mapping | [Sektor takeover proof history](Sektor-Takeover-Proof-History) |
| Sektor v44 generated shapes at unaligned offsets such as `+0x5037E` and `+0x51D81` | Immediate crouch hard-hang before a frame appeared | Generated shape records must be 4-byte aligned for target word loads | [Sektor takeover proof history](Sektor-Takeover-Proof-History), [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Tight-pack donor/WIMP rows as `width * height` | Diagonal/slashed frames | Preserve source row pitch `align4(width)`; visible width is not storage stride | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Put decoded byte lengths such as `0x00000FEA` / `0x00001054` into an MKMSZ image wrapper | Target interpreted the header as type 0 | Target wrapper type is encoded in header byte `+3 & 0x3F`; decoded length is not a raw-wrapper type declaration | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| Copy MKT codec 22/24/15 streams directly into MKMSZ | Rejected as an asset path | Decode donor formats offline, translate palette/geometry, then generate target-native assets | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| PS1-derived Sektor Run interpretation used by v55/v56 | Imported even poses were malformed | That PS1 pixel interpretation is rejected; preserved Midway/WIMP source plus calibrated target conversion became the successful bounded route | [MKT fighter asset translation](MKT-Fighter-Asset-Translation), [Sektor takeover proof history](Sektor-Takeover-Proof-History) |
| Treat Sektor v62 standalone combo continuation `[0x9AD90,0x9ADA0)` as reusable production space | It overlaps production bootstrap composite `[0x9AD84,0x9AF20)` | Runtime success of a proof does not make its allocation production-safe | [Sektor takeover proof history](Sektor-Takeover-Proof-History), [Memory and allocation map](Memory-and-Allocation-Map) |

## Flow, inventory, and run-lifecycle rejections

| Attempt / scope | Observed failure / rejection | What it established | Detailed owner |
|---|---|---|---|
| Start-button selector shortcut | Intermittent | Production selector uses the A-button route | [Stage flow and selector](Stage-Flow-and-Selector) |
| Broad boot-routine deletion | Rejected | Fade/title normalization still has to run | [Stage flow and selector](Stage-Flow-and-Selector) |
| Disable saving globally | Rejected | Selector-only suppression uses the native one-shot flag; normal post-stage saving remains | [Stage flow and selector](Stage-Flow-and-Selector) |
| Tablet `0x24` as foreign-key placeholder | Consumable | Use inert Glass `0x08` for LIVE masking instead | [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) |
| Auto-spill/global inventory scan | Intentionally rejected design | Four boxes remain explicit backing stores with controlled switching; no hidden global scan | [Persistence, inventory and lifecycle](Persistence-Inventory-and-Lifecycle) |

## XP productionization failure

| Attempt / scope | Observed failure | What it established | Detailed owner |
|---|---|---|---|
| V2 production integration with stage-entry progression restore calling native tier evaluator `0x80074FBC` | Temple music loaded, then the game hung before gameplay became visible | Static/CI success did not establish stage-init timing safety | [XP and progression](XP-and-Progression) |
| V2 repartition and restore-helper behavior changed together | Failure source was initially ambiguous | Runtime-critical variables need isolated disposable diagnostics | [XP and progression](XP-and-Progression) |
| Diagnostic A: keep V2 allocation/reward path but redirect only the progression stage-entry JAL back to the existing load/mask wrapper | Temple loaded and progression pickups at 85/258 worked, but combat XP path was absent by design | V2 allocation/reward path was viable on the tested route; the restore helper was the bounded suspect | [XP and progression](XP-and-Progression) |
| Diagnostic B: restore persistent XP at stage entry but omit the tier evaluator there | Temple/Wind/title->Fire routes retained XP and unlocked moves | **Accepted correction:** restore XP at stage entry; evaluate tiers only on the Runtime-confirmed progression-pickup acquisition path | [XP and progression](XP-and-Progression) |

## Allocation rule

Historical proof offsets are evidence, not reusable allocations. A proof-only cave, zero-filled region, or successful standalone footprint does not become production-safe without current ownership analysis and validation of the composed layout.

Canonical allocation ownership is [Memory and allocation map](Memory-and-Allocation-Map). Feature-specific proof details remain on their owning pages.
