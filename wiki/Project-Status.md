# Project status

Last consolidated: 2026-09-20.

## Production pipeline

| System | Status | Evidence and limit |
|---|---|---|
| Clean-ROM validation and separate output | Production | Implementation/CI-confirmed; exact USA Rev. 0 hash only |
| Header checksum update | Production | Implementation/CI-confirmed |
| Compact eight-stage selector | Production | Runtime-confirmed A-button route; compact index maps to native `0,1,2,3,4,5,8,9` |
| 1 KiB arena reservation and native payload | Production | Runtime-confirmed load/execute; guarded bounds and tests |
| Ordinary-pickup persistence | Production beta | All eight stages runtime-confirmed at representative locations; all 84 are statically cataloged, not individually exhausted |
| Stage-local pickup randomization | Production beta | All 84 implemented and tested over 250 seeds; seed `TEST153` first Fire location predicted/rendered/awarded Shield; full run pending |
| Pickup-driven XP progression | Production beta | Diagnostic B runtime-confirmed V2 allocation, XP restore, 85/258 rewards, Temple -> Wind transition and title -> Fire retention; nine-reward/full-tier run pending |
| Four inventory boxes | Production beta | Runtime-confirmed switching, transition preservation, stage-key masking; Game Over/reset edge still pending |
| `BOX n OF 4` HUD text | Production | Runtime-confirmed native text path |
| Boot branding and seed phrase | Production | Guarded and CI-confirmed; phrase uses a dedicated deterministic namespace |
| Logo and selector-save bypasses | Production | Runtime-confirmed, legal screen and later/manual saves preserved |
| Outfit recoloring | Production | Runtime-confirmed palette modes; static TLUT source transform |
| Browser/CLI shared patch core | Production beta | CI builds/tests; release UX continues to mature |

## Confirmed proofs, not product features

| Proof | Result | Remaining work |
|---|---|---|
| Same-stage pickup substitution | Full identity tuple changes award and art | Generalized in current stage-local mode |
| Fire foreign Prison-key import | Relocated/expanded resource file plus dedicated callback works | Production resource planner, allocation policy, compatibility matrix |
| Prison extension-selector Potion coexistence | Out-of-stock-range selector resolves appended Water Potion bundle while vanilla Herbs remain resident and functional | Generalize into guarded production planner |
| Health urn external-to-embedded conversion | Runtime-confirmed: Proof H converted `0x28F..0x292` to self-contained native type-4 blocks; imported Urn of Vitality rendered/awarded correctly in Prison while vanilla Herbs remained correct | Generalized in the pure resource planner; production pipeline integration still gated |\n| Composed five-visual Prison import | Runtime-confirmed: Potion, Urn of Vitality, Formula, Eye and Shield all rendered/awarded correctly together through five extension selectors; untouched Herbs control also remained correct | Fortress half of the same stress ROM still pending; token/key callback path still separate |
| Fire ordinary enemy `0x0A -> 0x09` | Spawns and plays normally | Production policy and broader coverage |
| Temple monk imported into Fire | Model loads, enemy moves/fights/dies | Death/despawn presentation missing; arbitrary rosters unresolved |
| Temple XP progression proof | Three proof pickups plus one vanilla Herbs control established no-combat-XP and pickup-driven tiers | Generalized into the production Diagnostic B architecture; full nine-tier coverage and final art remain |
| Reverse Elbow host/action proof + genuine MKT import branch | v6 established repeatable scheduler/action stability; v08/A1.7 runtime-confirmed genuine SCCOMBO10; Sektor direct replacements through Jump Kick / Flip Kick / Flip Punch are runtime-confirmed; v20 remains the accumulated raw-resource failure boundary | Forward Flip, Back Flip, and High Hit are runtime-confirmed in v34; Low Hit remains pending because the tested enemy route did not provide a practical crouching-hit setup. v35 runtime-confirms Sweep Fall + Sweep Getup. v36 runtime-confirms Knockdown, v37 runtime-confirms normal Getup, and v39 runtime-confirms Stumble on the tested route. The broader v39 selector+Sektor composition is NOT globally confirmed: Prison initially renders correctly but catastrophically corrupts the scene/framebuffer at the first doorway/encounter-activation boundary. v40 keeps the same selector/helper composition but returns fighter file 0x87 to the much smaller v11 size 0x4D820; the same Prison doorway then works normally. v41 then keeps v40's exact reachable fighter content but pads file 0x87 with unreachable 0xFF tail bytes to exactly v39's 0x578BC size; Prison corrupts at the same doorway again. This runtime-confirms that loaded file-0x87 allocation footprint alone is sufficient to trigger the Prison failure at that size. No exact lower threshold is yet established. Low Hit remains pending. Storage/decoder architecture is now higher priority than further raw accumulation. Stock Sub-Zero fighter frames are static-confirmed to use native type-5 compression (`0x80003314 -> 0x80065E00`), distinct from rejected v13 type-4. v42 is runtime-confirmed: one genuine Sektor stance frame encoded into generated native type 5 is visually indistinguishable from the surrounding proven raw frames even under frame-by-frame inspection, and Prison's first doorway remains healthy. v43 compacts all five idle frames into native type 5 and shrinks file 0x87 from 0x4D820 to 0x49BAC; runtime-confirmed with clean frame-by-frame idle inspection, transitions, and Prison doorway behavior. v44 extends native type 5 to Idle + Walk F/B + Turn + Crouch and uses one shared dictionary across the seven physical walk frames. Runtime result: Idle/Walk F/B/Turn work, but Crouch hard-hangs before its first frame. Static audit found v44 packed Crouch shape records at unaligned offsets (+0x5037E and +0x51D81), so this is a rejected packing/alignment bug rather than evidence against type 5. v45 rebuilds the same composition with every referenced shape word-aligned; file 0x87 is 0x52740 versus raw v12's 0x620E0. Runtime-confirmed: Idle, Walk F/B, Turn, Crouch, repeated transitions, shared-Walk dictionary use, and Prison's first doorway all pass. v46 adds Crouch Turn/Block/Hit/Punch/Low Kick/High Kick plus Standing Block, uses encoder-v2 normal classes and transparent-run symbols, and contains 34 unique Sektor frames at file-0x87 size 0x56E78. Runtime: all animations, including Crouch Hit, work and Prison's first doorway survives; however Inventory hard-hangs only after crossing that Prison doorway. Inventory works before the door, and this failure has not been observed in other stages. This is treated as a Prison-specific post-door memory-pressure boundary. v47 keeps the exact same 34-frame/action set but reclaims file-local-unreferenced stock Sub-Zero frame storage for compressed image streams, shrinking file 0x87 to 0x52BC0. Runtime-confirmed on the Prison doorway -> Inventory route: the v46 post-door Inventory hang disappears. Fortress regression is now bounded: v47 (0x52BC0) and v45 (0x52740) both hang on the Mission Objective screen before stage music/gameplay, while v40 (0x4D820) loads Fortress normally and Inventory/moves work. This exonerates v47 reclamation as the onset. v48 is an exact allocation-footprint control: v40 reachable content with only inert 0xFF tail padding to v45's 0x52740 file-0x87 size. Runtime-confirmed: Fortress reproduces the same pre-music Mission Objective hang, proving loaded file-0x87 allocation footprint alone is sufficient to break Fortress at 0x52740. Exact lower threshold is not being pursued. v49/v50 are real-content locomotion controls using encoder-v2: v49 is 0x4E544 without stock-hole reuse; v50 is 0x4C320 with conservative file-local stock-hole reuse, below the known-good v40 footprint; runtime pending. Proof ROMs from v25 onward include the confirmed post-legal logo skip for faster iteration; v39 adds the compact selector but exposes a Prison-specific runtime failure at the first doorway boundary. Full-character composition still needs a storage solution |

## Latest runtime findings

The Temple XP proof is confirmed: combat does not award XP; collecting the proof rewards sets XP to `85` and then `258`; the second threshold activates the next tier; nothing is added to inventory; ordinary pickups and progression rewards coexist. The proof model appears pale blue-grey and Herbs-like. The desired final presentation is a bright-blue body with a bronze handle.

A first production-layout attempt was **Rejected / failed** on 2026-09-20: Temple reached the Mission Objective screen and loaded stage music, then hung just before gameplay appeared. Production was rolled back to runtime V1.

Follow-up Diagnostic A is **Runtime-confirmed**: with the progression stage-entry restore helper bypassed, the same V2 allocation and generated progression callbacks loaded Temple normally. XP 85 and 258 rewards worked, special-move tiers unlocked, combo EXPERIENCE stayed suppressed, combat awarded no XP, and normal/progression Herbs coexisted with identical Herbs graphics.

Diagnostic B then removed only the early tier-evaluator call from the restore helper. It is **Runtime-confirmed** through Temple completion, Temple -> Wind with XP 258/two moves retained, and title-menu -> Fire with the same XP/moves retained. The original hang is therefore attributed to calling the native tier evaluator too early during stage initialization. Production now uses Diagnostic B behavior: restore XP at stage entry, but evaluate tiers only when a progression pickup is collected.

The behavioral Reverse Elbow branch is now historical host-action evidence rather than the intended final implementation. Later v8.1-v8.3 tests established usable high-speed directional motion and a proof-only forced crossover, but also exposed collision/jitter and freeze/strike mismatches inherent to recreating donor behavior with native approximations. The project has pivoted to a genuine MKT→MKMSZ compatibility layer. The single-frame import branch then resolved descriptor endianness/order, palette isolation/opacity, raw-wrapper type, and CI row-stride conversion. **v08/A1.7 is runtime-confirmed:** Back → Forward + Low Kick renders the genuine MKT Rev. 2 SCCOMBO10 Reptile/male-ninja frame coherently inside MKMSZ, with the true 42x95 geometry, donor palette, 44-byte aligned row stride, and clean restoration of stock Sub-Zero. This establishes genuine foreign fighter-sprite transplantation for this MKT resource family.

## 1.0 required scope

The 1.0 randomizer is not considered complete with stage-local shuffling alone. Required before 1.0:

1. **Global cross-stage item randomization.** Items must be able to appear in other main stages, requiring a production resource-import/materialization planner rather than copying stage-local resource selectors verbatim.
2. **Global deterministic shuffling.** Keep the current stable seeded Fisher-Yates approach, but apply it to the global logical item pool rather than eight independent stage pools.
3. **Whole-run solvability validation.** Reject seeds whose progression graph cannot reach the required end-state. Use current stage/location requirements as source of truth; the legacy Lua fixed-point solver is a useful design reference but its location rules are stale/incomplete. Rejected attempts must be derived deterministically from the original seed plus an explicit attempt index, so regenerating the same seed always produces the same accepted layout even when several attempts are required.
4. **Randomizer HUD/UI.** At minimum expose the run information needed to play the seed: check progress, required Power Upgrades/current progression status, inventory-box/page state, and useful pickup feedback. The legacy Lua overlay is a reference for semantics, not a native renderer implementation.
5. **Run-resource lifecycle.** Determine and preserve HP, lives, and continues correctly across stage transitions and direct selector routes; define intended Game Over/new-run resets.
6. **Difficulty hard-lock.** Very Hard must be enforced as a run invariant rather than only selected as a startup default.
7. **Final runtime coverage.** Complete a representative full global seed, including all nine progression tiers and the major lifecycle boundaries.

Open Temple Map work: the legacy Lua global pool included the scripted Map as an 85th check. For 1.0, investigate separating the Map inventory reward from the Temple elevator/exit trigger so the elevator can still be raised correctly even when the Map item itself is shuffled elsewhere. Also prevent the Map item from being removed on the Temple -> Wind transition, which is stock behavior today.

## Pending priorities

1. Finish composed runtime validation of the pipeline-disconnected cross-stage resource planner: Prison is confirmed with five distinct simultaneous imports plus vanilla Herbs; Fortress in the same stress ROM is still pending. Then add destination-safe key/crystal award wrappers and run a guarded disposable integration proof before enabling global materialization in browser/CLI.
2. Replace stage-local generation with a global deterministic shuffle plus whole-run solver, including deterministic retry attempts and a deterministic per-seed required-Power-Upgrades target.
3. Build the native randomizer HUD around the finalized global-run state.
4. Resolve Temple Map trigger/item separation and cross-stage persistence; then HP/lives/continues persistence, Game Over/new-run reset, and Very Hard enforcement.
5. Run full-seed 1.0 validation.
6. Post-1.0: enemy randomization/resource compatibility, imported-enemy death/despawn, and Reverse Elbow.

## Explicit exclusions

Bosses and scripted encounters are not ordinary-enemy entries. The Temple Map is not an ordinary pickup and needs an explicit 1.0 inclusion decision if it is to become a global check. Zero resource slots are logical selectors, not free physical storage. PS1 addresses are not N64 addresses. Proof ROM patches and archive handoffs are not silently part of the product pipeline. Enemy randomization and Reverse Elbow are not 1.0 blockers.
