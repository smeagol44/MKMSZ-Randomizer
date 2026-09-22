# Experiments, failures, and superseded findings

Failures are retained because they define safety boundaries and prevent repeated dead ends.

## Address and interpretation corrections

| Earlier conclusion | Current conclusion | Why it changed |
|---|---|---|
| Current process global `0x802FCE20` | Effective address `0x802ECE20` | `0xCE20` is a signed low immediate paired with `lui 0x802F` |
| `0x8004CC14` propels the player | Projectile setup helper | It writes the projectile actor `+0x14`; confirmed player helper `0x8002B1EC` writes actor `+0x14/+0x58` |
| `0x8004B82C` is a player action | Ice-projectile flight callback | Caller/data-flow analysis identifies projectile ownership |
| `0x8004AA4C` is a generic initializer | Scheduler context-transfer shim | Selector dispatch table `0x800A1050` and native call sites show transfer semantics |
| A special callback may `jr ra` | Installed top-level callback must transfer/nonreturn | Installer enters it with `$ra` equal to callback entry; return self-reenters |
| XP final threshold `7345` | `7354` | Actual halfword/value is `0x1CBA` |

## Pickup/resource failures

| Attempt | Result | Durable lesson |
|---|---|---|
| Change callback/type only | Award or art could change independently/incompletely | Move complete identity `+0x10..+0x2B` |
| Copy Prison key into Fire without resource import | Item absent/unusable | `+0x24` is stage-local; foreign bundle must be resident |
| Treat zero outer slot as storage | Rejected | Zero is selector capacity, not physical bytes |
| Reuse occupied no-pickup slot | Rejected without global reference trace | Other actors/scripts may own it |
| Global pickup pool before import planner | Deferred | Stage-local production scope is the safe boundary |

## Enemy failures

| Attempt | Result | Durable lesson |
|---|---|---|
| Fire type `0x0A -> 0x01` without Temple resource | Freeze at spawn | Constructor dereferences type-specific resource slot |
| Add Temple file after all stock Fire allocations | Would exceed arena by `0x3098` | Use bounded replacement or redesign allocation |
| Imported monk proof | Fighter works, normal death/despawn presentation absent | Residency/constructor success is not complete compatibility |
| Apply ordinary policy to bosses | Rejected | Boss/state branches carry custom resources, process IDs, scripts, and transitions |

## UI failures

- Direct framebuffer drawing was unstable.
- A candidate universal sprite renderer was context-specific.
- General helper abstraction failed where inline allocation/submission worked.
- Textured-image rendering remains unproven; native text is the stable production path.
- Early proof diagnostics used legal-screen string storage that production later assigned; the final box wrapper uses a guarded dedicated region.
- **Toasty visual v01**: automatic HUD-cycle proof produced no visible image. Because it had no independent marker, it does not distinguish wrapper execution from texture-slot allocation, file loading, palette binding, or `0x80073CEC` context suitability. Do not repeat unchanged; next proof must add a proven text/quad diagnostic and isolate one variable at a time.
- **Toasty visual v02**: the `V02 WRAPPER OK` native-text marker is runtime-confirmed visible during gameplay, while the Toasty image remains absent. Wrapper/hook execution is therefore exonerated; continue downstream with texture-slot allocation/state first, one variable at a time. Toasty audio v03 remains independently runtime-confirmed and must not be reworked as part of this diagnosis.
- **Toasty visual v03**: persistent `V03 SLOT FAIL`, but the same proof also removed all normal game music/SFX. Treat the diagnostic as intrusive/rejected for allocator attribution; the slot result is not clean evidence against `0x8001C2B4`. Return to the v02-known-good diagnostic footprint before isolating allocator success again.
- **Toasty visual v06**: wrapping raw loader `0x80065D64` and extending into standalone selector-cave tail `0x9A720..0x9A753` caused a Mission Objective + music hang before gameplay. Reject this diagnostic; do not infer loader success/failure from it. Subsequent load checks must leave the stock loader call untouched and avoid that cave tail.
- **Toasty visual v07**: even with the stock raw-loader call restored exactly, adding a post-load helper call reproduced the same Mission Objective + music hang. Reject helper-based load instrumentation on this route; no loader conclusion is accepted. Preserved UI evidence also shows `0x80073CEC -> 0x8001E578` is not a universal gameplay renderer, so the v01-v05 renderer assumption is superseded. Continue with the actual textured gameplay-HUD node family instead.

## Reverse Elbow failures

| Version/approach | Failure |
|---|---|
| v1 | Minimal movement, incomplete animation, facing/input misunderstanding |
| v2 | Correct mirrored command, but contact could hard-hang through experimental victim callback |
| v3 | Immediate hang regardless of enemy; normal return self-reentered top-level callback |
| v4/v5 | Incomplete scheduler/action-root emulation; v5 omitted special lock `0x800BF308` |
| v7 | Pass-through behavior not established; only bounded lifecycle/Y gating improved |
| v8 | Intended 4x speed, per-tick velocity, forced crossover, and expanded HUD were not observed; attacking still stops motion |

Stable baseline is v6's selector-3 scheduler bridge, lock, correct player velocity helper, bounded loops, and native restore. Experiments that change one observable at a time can distinguish movement, interaction, and diagnostic failures.

## Flow and inventory rejections

- Start-button selector shortcut was intermittent; only A-button route is production.
- Broad boot-routine deletion was rejected because fade/title normalization must run.
- Global save disabling was rejected; the accepted implementation uses the native selector one-shot flag.
- Tablet `0x24` was rejected as key placeholder because it is consumable; Glass `0x08` is made inert instead.
- Auto-spill/global inventory scan is intentionally outside the accepted four-box design.

## Proof/production allocation conflicts

Historical proof offsets are evidence, not allocations. The Temple XP proof and foreign-key callback use temporary caves that conflict with current production owners. Their old runtime results do not establish compatibility with a new layout; reallocation and validation of the changed composition are separate technical work.


## XP productionization failure

| Attempt | Result | Durable lesson |
|---|---|---|
| Runtime V2 XP production integration | Temple music loaded, then game hung immediately before the stage became visible; no progression pickup had executed | Static/CI evidence alone did not establish native allocation/stage-init safety |
| V2 repartition + progression stage-entry restore combined in one production step | Failure source became ambiguous between the repartition and the new restore path | Disposable tests changing one runtime-critical variable at a time can isolate the cause |

The initial isolation plan tested the V2 allocation/reward callback **without** the progression stage-entry restore hook. Stage-load success would implicate the restore path; a continued hang would leave repartition/state relocation implicated. Diagnostic A and B below resolved this investigation.


### XP Diagnostic A follow-up

| Attempt | Result | Durable lesson |
|---|---|---|
| Diagnostic A: failed production build with only the progression stage-entry JAL redirected back to the existing four-box load/mask wrapper | Temple loaded and played normally; progression rewards at 85/258 worked; no combat XP; no EXPERIENCE combo text | V2 allocation and reward callback path are viable on the tested Temple route; failure is inside the progression restore-helper path |
| Restore-helper review | The helper calls native tier evaluator `0x80074FBC` before normal stage gameplay is visible | The evaluator call became the next bounded suspect, subsequently isolated by Diagnostic B |


### XP Diagnostic B resolution

| Attempt | Result | Durable lesson |
|---|---|---|
| Diagnostic B: restore persistent XP but omit native tier evaluator during stage initialization | Temple loaded; XP 85/258 rewards unlocked moves; Temple -> Wind retained XP/moves; title -> Fire retained XP/moves | Stage-entry XP restore is safe; native tier state already established at acquisition persists across tested routes |
| Native tier evaluator `0x80074FBC` called from progression stage-init restore | Earlier production build hung before gameplay display | **Rejected at this timing**. The accepted design calls the evaluator on the runtime-confirmed progression-pickup acquisition path |

Diagnostic B supersedes the failed restore-helper design and is the accepted production behavior.


## Global item materialization correction

| Attempt / interpretation | Result | Durable lesson |
|---|---|---|
| Use destination pickup graphics and change only the logical award callback | Rejected before runtime promotion | Violates the 1.0 requirement that a randomized pickup visually match the item it contains |
| Treat foreign-resource importing as optional polish | Superseded | Exact cross-stage model/resource materialization is core 1.0 infrastructure |
| Keep the logical-item catalog separate from physical materialization | Retained | Useful for shuffle/solver semantics, but every accepted placement must still materialize the randomized item's real visual/resource identity |

The disposable destination-shell diagnostic is a rejected alternative, not a required validation step or production direction.
