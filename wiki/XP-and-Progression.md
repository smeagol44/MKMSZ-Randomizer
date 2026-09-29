# XP and progression

XP progression is a production feature built from the runtime-confirmed Temple proof and Diagnostic B lifecycle validation. The full nine-tier generated-run coverage is still pending.

## Native XP system

| Purpose | Address |
|---|---:|
| Current XP | `0x8011200C` |
| Central award function | `0x8002E104` / ROM `0x2ED04` |
| Direct store sites | `0x800540E8`, `0x80057160`, `0x8005722C` |
| Tier evaluator/clamp | `0x80074FBC` / ROM `0x75BBC` |
| Signed cap table | `0x800A63FC` / ROM `0xA6FFC` |
| Save-load restore | `0x80078A18`; save record `+0x7C` |

The confirmed thresholds are:

| Tier reached | XP |
|---:|---:|
| 1 | 85 |
| 2 | 258 |
| 3 | 834 |
| 4 | 1410 |
| 5 | 2323 |
| 6 | 3315 |
| 7 | 4503 |
| 8 | 5911 |
| 9 | 7354 |

The final value corrects a legacy Lua comment that said `7345`; the actual `0x1CBA` value is `7354`.

## Temple bounded proof

The disposable proof changed Temple ordinary Herbs #1, #3, and #4 into progression pickups while leaving Herbs #2 completely vanilla as a brown control. Only the first two progression pickups needed to be collected to validate the core behavior. Runtime results:

- defeating enemies, kills, and combos did **not** award XP;
- the combo `HITS` message remained while the `EXPERIENCE` line was removed;
- first tested progression pickup set XP to `85`;
- second tested progression pickup set XP to `258`;
- the second threshold activated the next expected special-move tier;
- progression pickups added nothing to inventory;
- the untouched Herbs control remained a normal inventory Herbs pickup;
- normal and progression pickups coexisted and were visually distinguishable;
- Temple displayed max XP `20000`.

The experimental progression model is pale blue-grey and visually Herbs-like. The intended final presentation is a bright-blue Herbs body while retaining the bronze/gold-looking handle. That visual refinement is separate from the confirmed progression logic.

## Power-order shuffle proof — 2026-09-27

**Runtime-confirmed, bounded proof.** The power-order experiment establishes that native XP thresholds, actual move eligibility, and the native Power Ups presentation order can be decoupled from the vanilla ability order.

- v01 swapped only the first two gameplay gates: Slide became tier 1 / 85 XP and ground Ice Blast became tier 2 / 258 XP. Runtime testing confirmed Slide was the first usable power, but the Power Ups screen still displayed the vanilla Ice Blast-first order. That mismatch established that gameplay eligibility and Power Ups presentation are separate mechanisms.
- v02 kept the successful gameplay-gate swap and also swapped the first two entries in both native Power Ups presentation tables: the icon strip and the move-help/detail pointer order. Disposable ROM `MKMSZR_power-order_temple_proof_v02.z64` has SHA-256 `272befa1eaa5f04f44aadc176b4c497d76a5d2e4a73e1e4f623d72ae35692384`, CRC1/CRC2 `52329D77 / 6999CADF`; builder SHA-256 is `b29c2ab0edab3ee18cf2dbb7583dc15551a4f6939af188954aeb0d7a026ff2e4`.
- At 85 XP the user observed **Slide usable, Ice Blast unavailable, one Power Ups icon, and that icon was Slide**.
- In two separate runs, collecting different progression-pickup locations while at 85 XP advanced to 258 XP and unlocked **Ice Blast second**; the Power Ups screen also displayed Ice Blast second.
- A subsequent progression pickup advanced to 834 XP and displayed a third power icon while preserving Slide first and Ice Blast second. The screenshot evidence SHA-256 is `5899955c98aeaa5ef5709324e69ccd7feeed175de5c11554b8e73f1207525b07`. Execution of the third ability was not separately reported, so this is UI/progression evidence for tier 3 rather than an exhaustive tier-3 action test.

Temple Herbs labels in the stage catalog are **ROM/storage order, not stage-traversal order**. More importantly, the proof callback does not assign a threshold to a physical Herbs location: it advances from the current XP value to the next native threshold. The repeated 85 -> 258 result from different progression-pickup locations confirms the intended location-independent progression semantics on those tested routes.

**Production direction, user-approved:** expose power-order randomization as an optional setting. When disabled, preserve the vanilla nine-slot order exactly. When enabled, seed the nine power-tier slots independently and deterministically while leaving the native XP threshold sequence itself unchanged. The same generated slot order must drive both gameplay eligibility and the native Power Ups icon/help presentation.

The shuffled order has exactly one semantic constraint and no additional hidden ordering rules:

- **Ice Shatter** must appear after at least one freezing-enabling Power Up: **Ice Blast**, **Directional Ice** (the native slot that includes Directional Ice Up/Down), or **Air Ice Blast**.

**Slide and Super Slide are independent for shuffle ordering.** Either may be awarded first; production must not impose a Slide-before-Super-Slide dependency.

The power-order generator must use its own deterministic namespace and bounded explicit retry/validation so rejected constrained permutations cannot perturb other RNG domains.

**v04 generalized proof — Runtime-confirmed, 2026-09-27.** A bounded standalone Temple proof exercised all nine remapped gameplay gates and both native Power Ups presentation tables using the order **Freeze on Contact -> Air Ice Blast -> Super Slide -> Ice Shatter -> Slide -> Ice Clone -> Directional Ice -> Ice Blast -> Polar Blast**. The user reported the tested progression worked perfectly. This specifically confirms that Super Slide may precede Slide and that Ice Shatter can follow Air Ice Blast as its freezing prerequisite.

The same proof started Temple at 85 XP with its first power already awarded. Static review identifies this as a **proof-harness bug, not production progression behavior**: the standalone bootstrap loaded the proof payload and immediately executed the progression callback at stage initialization. The production XP path does not enter its pickup award callback from bootstrap; it restores persistent XP separately and awards a new tier only from a selected progression pickup callback. Do not reproduce the v04 bootstrap behavior in product integration.

The shared product implementation now reuses the production XP lifecycle and adds the power-order remap as a separate final patch stage. Runtime mechanism is confirmed; repository CI and normal-product deployment remain the integration gates.

## Build-time progression choices

**Implementation/static-confirmed candidate; runtime Pending for the new choices.** The shared builder now exposes **Powers as pickups**, default ON. ON retains the established nine generated Herbs callback replacements, disables normal combat XP, suppresses the combo EXPERIENCE display, raises main-stage caps, and restores persistent pickup-awarded XP at stage entry without calling the unsafe tier evaluator there. OFF omits that entire patch stage: generated Herbs keep their normal callback and stock combat XP stores, combo display, stage caps, and four-box manager resume remain in place. This is a ROM-build setting, not an in-game switch. The independent **Shuffle Power Progression** option can remap gameplay/UI power order in either mode; normal-XP plus shuffled order has not been runtime-tested.

The Fortress final-fight gate is separate from the source of XP. Raw stage overlay file `0x9E` has stock `slti v1,v1,0x13EC` at VA `0x802EF49C` / ROM `0xC299C`, comparing current XP to **5100**. That falls between native tier thresholds 7 (`4503`) and 8 (`5911`): pickup mode needs its eighth reward, but normal XP can pass at 5100 before tier 8. **Vanilla** preserves the exact stock XP requirement and does not claim an exact tier count. **Custom** accepts an integer `0..9`, and **Seed** deterministically selects `0..9` from independent `MKMSZR:REQUIRED-POWERS:V1\0`; both change only that guarded comparison immediate. Count `0` compares against XP `0`; counts `1..9` compare against the matching native tier thresholds. The selected setting and threshold are reported after the build. Static patch composition does not yet establish final-fight runtime behavior for every count, especially `0` or normal-XP mode.

## Production semantics

With Powers as pickups ON, the production mode has exactly nine rewards and uses a dedicated RNG namespace. Each reward advances to the next native threshold rather than adding an arbitrary fixed amount. A custom award callback avoids inventory insertion, evaluates/clamps the native tier, and caps at the ninth value. A separate stage-init helper restores persistent XP without evaluating tiers at that boundary.

Normal ordinary-pickup randomization remains independent of progression selection and count/XP state. Acquisition still marks the physical ordinary location as collected; progression count/XP use separate words and progression selection uses its own RNG namespace.

## Production allocation and state

Production does not reuse the disposable proof cave. Runtime V2 keeps its established first-1-KiB layout inside the current 16 KiB reservation, partitioned as:

- reloadable payload code: `0x801AF420..0x801AF7CF` (0x3B0 bytes);
- persistent state: `0x801AF7D0..0x801AF81F` (0x50 bytes).

The 2026-09-23 full-composition rainbow proof Runtime-confirmed this larger code/smaller state repartition within the original first 1 KiB. The 2026-09-24 production reservation expansion leaves those addresses unchanged and adds a separate 15 KiB pool after `0x801AF820`. XP still uses state `+0x40/+0x44`; the optional rainbow phase uses `+0x48`.

Progression uses state `+0x40` for acquired reward count and `+0x44` for persistent XP, separate from the 84 ordinary-pickup persistence bits at `+0x20..+0x3C`.

Nine rewards are selected only after the ordinary 84-location layout is finalized, using the independent domain `MKMSZR:PROGRESSION:HERBS:V1\0`. Only generated Herbs locations are eligible and only their callback word is replaced, so the ordinary shuffle is not perturbed and no foreign resource import is required.

The acquisition callback advances to the next threshold, stores count/XP, writes current XP, and calls native tier evaluator `0x80074FBC` at the safe pickup-acquisition point. It does not add an inventory item.

At stage initialization, production restores the persistent XP value and then performs the existing four-box reconstruction. It deliberately **does not** call the native tier evaluator there.


## Failed productionization attempt — 2026-09-20

**Rejected / failed:** the first attempted production integration (runtime-layout V2) was merged before manual runtime validation and was immediately rolled back.

The attempted layout expanded the reloadable payload from `0x200` to `0x300` bytes and moved persistent state from `0x801AF620` to `0x801AF720`, then added a progression restore call at the pickup-manager stage reconstruction boundary.

Manual Temple validation failed before gameplay became visible:

- the Mission Objective screen completed;
- Temple music loaded;
- the game then hung as the stage was about to be displayed;
- no progression pickup was collected, so the failure occurs before the new pickup callback is exercised.

At that point the exact failing component was not established. The leading candidates were the new stage-entry progression restore path and the V2 code/state repartition itself. Diagnostic A and B below subsequently isolated the stage-init tier-evaluator call.

The web/CLI pipeline was temporarily restored to the previously runtime-confirmed V1 allocation during that investigation. Diagnostic B later established the accepted V2 production behavior.

### Historical validation lesson

The failed integration passed static/CI composition checks but hung at a native stage-init boundary. Disposable Diagnostic A and B supplied the missing runtime evidence. This demonstrates the limit of CI as evidence for game-state-dependent behavior.


## Diagnostic A runtime isolation — 2026-09-20

**Runtime-confirmed:** disposable Diagnostic A using seed `BCBDBF` loaded Temple normally and exercised the production-style V2 progression generation/callback path without the new progression stage-entry restore helper.

Observed:
- Temple reached normal gameplay with no hang;
- first generated progression Herbs awarded XP 85 and unlocked the first progression special move;
- enemy combos showed `HITS` only, with no `EXPERIENCE` text;
- combos and enemy kills awarded no XP;
- the second Herbs was a normal Herbs pickup;
- the third Herbs awarded XP 258 and unlocked the second progression special move;
- all three Herbs used the same ordinary Herbs graphics;
- no other issue was observed during this bounded test.

Diagnostic A differs from the failed production integration at the stage-entry resume sequence only: the failed build JALs the progression restore helper, while Diagnostic A JALs the pre-existing four-box load/mask wrapper directly. V2 allocation, progression callbacks, reward generation, XP-store suppression, combo-text suppression and cap edits are otherwise unchanged.

Therefore the V2 repartition and pickup callback path are no longer implicated by this bounded route. The failure is isolated to the progression restore-helper path executed during pickup-manager stage initialization.

## Diagnostic B runtime confirmation — 2026-09-20

**Runtime-confirmed:** Diagnostic B removed only the tier-evaluator call from the stage-entry restore helper while keeping persistent-XP restoration and the normal four-box reconstruction.

Observed with seed `BCBDBF`:

- Temple loaded normally;
- first and third generated progression Herbs reached XP 85 and 258 and unlocked the first two special-move tiers;
- Temple completed normally;
- Wind loaded with XP still at 258 and both unlocked moves retained;
- after quitting to the title menu and entering Fire directly, XP remained 258 and both moves were still available;
- no issue was detected on this bounded route.

This isolates the original hang to invoking native tier evaluator `0x80074FBC` during pickup-manager stage initialization. That call is **Rejected / failed at stage-init timing**. The evaluator remains valid and runtime-confirmed on the progression-pickup acquisition path.

Diagnostic B behavior is the production design.

## Remaining limits

- All nine generated progression rewards are implementation/CI-confirmed, but a full nine-tier runtime run is still pending.
- Production progression pickups currently retain ordinary Herbs graphics. Bright-blue Herbs body with a bronze/gold-looking handle remains a visual refinement.
- Game Over/new-run reset behavior remains pending as part of the shared MKMSZR lifecycle work.


## Required-Power-Upgrades implementation implications

The canonical 1.0 solvability requirement, including the selected Vanilla / Custom / Seed Power Upgrades gate, is R3 in [1.0 requirements and roadmap](1.0-Requirements-and-Roadmap). This page owns the native XP/progression behavior and the implementation constraints that requirement must preserve.

Implementation implications for the progression subsystem:

- Seed mode's required-count generator must use its own deterministic namespace and remain independent of rejected global-layout attempts;
- the whole-run solver and native randomizer HUD consume the required-count result, but their normative product behavior remains owned by the Roadmap and their respective implementation pages;
- each collected progression reward must preserve the current Runtime-confirmed native threshold behavior.

The build-time Custom/Seed range is now `0..9`; the global solver and HUD must still consume this mode-specific requirement. Their completion rules and normal-XP reachability remain Pending, as tracked by the Roadmap and [Global item materialization and solvability](Global-Item-Materialization-and-Solvability).
