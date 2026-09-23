# Player actions and special moves

> **Scope:** This page owns the **MKMSZ host-side action/control ABI**: special-action descriptor and installer semantics, scheduler/context transfer, player movement/animation/strike primitives, callback lifetime and cleanup rules, and durable host-side findings from the Reverse Elbow proof line.
>
> Donor choreography, donor move phases, MKT strike/reaction meanings, no-repel semantics, combo translation, and reusable donor -> MKMSZ mappings are canonical in [MKT adapter primitives](MKT-Adapter-Primitives). The old URL is retained only as a historical supersession stub at [Foreign moves and Reptile](Foreign-Moves-and-Reptile).

## Low Kick descriptor and special-action path

```text
semantic Low Kick 0x80014C60
-> event-4 handler 0x8003C94C
-> descriptor parser 0x8004A0E0
-> matcher 0x80049E60
-> transfer dispatcher 0x80049D14
-> installer 0x80032CD4
```

The Low Kick table is RAM `0x800B0F68` / ROM `0xB1B68`. It has two active `0x2C`-byte records, followed by a zero `u16` sentinel at `0x800B0FC0`. Unrelated data begins eight bytes later, so adding a third record in place is unsafe; an added descriptor must use relocated owned storage.

| Offset | Type | MKMSZ host meaning |
|---:|---|---|
| `+0x00/+0x02` | two `u16` | Legal semantic-button masks |
| `+0x04` | `u32` | Transfer selector; stock implemented values 0 and 1 |
| `+0x08` | pointer | Optional no-argument condition |
| `+0x0C` | pointer | No-argument action/process callback |
| `+0x10` | `u16` | Input-history window |
| `+0x12..+0x1C` | six `u16` | Facing-right tokens, zero-terminated |
| `+0x1E..+0x2A` | seven `u16` | Facing-left tokens, zero-terminated |

Direction tokens are `8=Left` and `9=Right`. The Reverse Elbow proof used the semantic command **Back -> Forward + Low Kick**: facing right `8,9,0`, facing left `9,8,0`, with window `0x10`. The donor reason for that command and the donor move choreography belong to [MKT adapter primitives](MKT-Adapter-Primitives).

## Host action primitives

| Address | Correct MKMSZ meaning |
|---:|---|
| `0x8002B1EC` | Player velocity helper; writes player actor `+0x14` and `+0x58` |
| `0x8002B1C0` | Stop/clear linear motion |
| `0x80031D00` | Find nearest opponent controller |
| `0x80031EF0` | Face opponent |
| `0x8002FE54` | Select animation `(table,index)` |
| `0x800304C0` | Advance animation |
| `0x8004CF3C` | Fighter strike dispatch |
| `0x8002BA04` | Collision/damage/reaction core |
| `0x80028794` | Process sleep |
| `0x800328FC` | Exit action / restore control |
| `0x8004AA4C` | Scheduler context-transfer shim using table `0x800A1050` |
| `0x8004AB84` | Complete ice-projectile action root |
| `0x80030974` | Animation token-`0x0B` secondary-resource actor handler |
| `0x80031208` | Facing-aware actor-relative XY adjustment |
| `0x8004CBC4` | Projectile child-process bridge; binds staged secondary actor into a new child controller/process |
| `0x8004CC50` | Generic projectile flight/collision loop |
| `0x8004CE6C` | Projectile strike-record resolver |
| `0x800BF308` | Special-action lock; native action roots set it |

`0x8004B82C` is the ice-projectile flight callback. `0x8004CC14` is projectile setup that writes a projectile actor's `+0x14` and selects animation. Neither is the player propulsion helper. The older recommendation to use `0x8004CC14` for player movement is **Rejected / failed**.

The current process/controller pointer is at effective address `0x802ECE20`, not `0x802FCE20`.

Function-level semantics are indexed in [Function registry](Function-Registry); this page owns how the helpers compose into the host action lifecycle.

## Projectile actor/process host ABI

The v63-v70 Sektor missile work and follow-up static trace expose a target-native projectile split that should be reused by donor adapters rather than treating Ice Blast as one monolithic move.

**Static-confirmed target composition:**

```text
animation token 0x0B
-> 0x80030974
-> 0x80034510
-> 0x800281A0 -> 0x80028128   ; resource-backed secondary actor
-> stage actor in controller +0x714/+0x648
-> 0x80024650                  ; insert actor

0x80031208(actor, dx, dy)      ; facing-aware relative placement

0x8004CBC4(callback)
-> 0x8002830C(class 0x700, callback)
-> copy parent/opponent context
-> child +0x6E0 = parent staged actor +0x714
-> tag/clear staging state
```

This establishes distinct host primitives for **resource actor creation**, **relative placement**, and **child projectile process creation**. The exact function meanings remain indexed in [Function registry](Function-Registry); donor-side semantics and the reusable adapter vocabulary remain in [MKT adapter primitives](MKT-Adapter-Primitives).

The projectile collision/strike path is likewise separate from Ice freeze presentation: `0x8004CC50` drives the generic projectile loop, `0x8004CE6C` resolves a fighter-local strike record from the supplied selector, and `0x8004CF3C -> 0x8002BA04` reaches the normal target strike/collision core. A donor strike index is still **not** portable numerically.

### Resolved player animation cursor

The current controller/process animation cursor is `+0x6E4`. v69 is **Runtime-confirmed** for one narrow use: after the stock special helper completes, temporarily redirecting `+0x6E4` to the imported chest script, advancing once through `0x800304C0`, and restoring the cursor displays the genuine chest-open frame on the player without hanging.

That runtime result proves the host cursor/update mechanism only. It does not make a one-frame post-helper injection the final donor-animation runner.


## Installer, scheduler, and context-transfer semantics

`0x80032CD4` installs a top-level special-action callback. In the observed installed context, the callback begins with `$ra` equal to the callback entry. A normal `jr ra` therefore re-enters the callback instead of returning to an ordinary caller.

`0x8004AA4C` is not a generic action initializer. It transfers scheduler context according to selector table `0x800A1050`. Stock selectors `0..2` are defined. The stable Reverse Elbow v6 proof used a deliberately added selector-3 bridge as a **proof-specific controlled extension**; that does not make selector 3 a stock ABI entry or a production allocation.

A native special action also needs the target action-lock/cleanup conventions. The successful host-side proof set `0x800BF308`, kept its loops bounded, and exited through native scheduler/control restoration.

## Callback lifetime and cleanup rules

These are durable host-side safety constraints:

- an installed top-level action callback must not simply return normally;
- every movement/contact wait loop must be bounded;
- action exit must transfer through the native scheduler/cleanup path or an equivalently proven target-native path;
- the native special-action lock must be established/preserved where the action path requires it;
- interruption/contact branches are lifecycle paths and must reach cleanup, not just switch animation;
- one observed state byte is not enough to prove an action is still active after interruption.

These rules come from both successful and failed bounded proofs and are applicable to later donor-adapter work regardless of the specific move choreography.

## Durable Reverse Elbow host-side findings

The Reverse Elbow experiments are useful here only for what they established about MKMSZ's host action system.

| Finding | Evidence / implication |
|---|---|
| Early movement interpretation used projectile setup as propulsion | **Rejected / failed.** `0x8004CC14` is projectile setup; `0x8002B1EC` is the player velocity helper. |
| Experimental victim callback could hard-hang on contact | **Rejected / failed.** Victim/contact work must not be added before its callback/lifetime semantics are understood. |
| v3 hung immediately with or without an enemy | **Rejected / failed.** Later analysis explains this as installed-callback `jr ra` self-reentry. |
| v5 omitted native special lock `0x800BF308` | **Rejected / failed** as a complete lifecycle model; omission is a strong host-side hang risk. |
| v6 used selector-3 bridge + lock + player velocity + bounded loops + native restore | **Runtime-confirmed** stable lifecycle baseline; repeatable without whole-game hang on the tested route. |
| v7 added strike `0x14` and a Y-distance gate | The Y gate behaved as intended against a jumping enemy; no abnormal jumping-enemy contact was observed on that bounded test. |
| v8 attempted velocity `0xD0000`, locomotion index `controller+0x6E6`, per-tick reapply, forced-X crossover `+0x3800`, and expanded diagnostics | **Not confirmed as an improvement.** Runtime testing still showed slow movement/no pass-through; attacks could cancel forward motion while the displayed `L 1` state stayed unchanged; expanded HUD diagnostics were absent. These parameters are preserved as failed-proof reproduction data, not accepted movement values. |

The durable conclusion is the **v6 lifecycle model**, not the v8 movement behavior. Direct player-velocity measurement remains the clean way to separate movement calibration from pass-through, victim-hold, and strike behavior.

The old forced-X crossover attempt is not a reusable host primitive and is not accepted donor behavior. Donor-side pass-through/no-repel semantics are documented in [MKT adapter primitives](MKT-Adapter-Primitives).

## Current host-side boundaries

Established:

- descriptor parsing/matching and special-action installation path;
- bounded scheduler sleep/context transfer primitives;
- player velocity/stop/facing helpers;
- animation select/advance helpers and the resolved controller animation cursor at `+0x6E4`;
- resource-backed secondary-actor construction, facing-aware relative actor placement, and projectile child-process binding;
- generic projectile collision/strike resolution path;
- strike dispatch and collision/reaction entry points;
- native action lock and exit/control restoration;
- callback self-reentry hazard and bounded cleanup requirement.

Not established here:

- a production-ready generic donor action runner;
- generic donor velocity-unit conversion;
- a generic no-repel shim;
- arbitrary donor victim-reaction translation;
- donor animation control-token translation;
- a production-ready generic wrapper that composes the identified projectile actor/process primitives with donor callback/state/effect semantics.

Those translation-layer gaps are tracked in [MKT adapter primitives](MKT-Adapter-Primitives).

## Related pages

- [MKT adapter primitives](MKT-Adapter-Primitives) — canonical donor choreography and donor -> MKMSZ semantic translation.
- [MKT to MKMSZ compatibility layer](MKT-to-MKMSZ-Compatibility-Layer) — accepted genuine-port strategy and compatibility contract.
- [Foreign moves and Reptile](Foreign-Moves-and-Reptile) — historical supersession stub for the retired behavioral-recreation page.
- [Function registry](Function-Registry) — flat canonical function semantics.
- [Address and patch-site registry](Address-and-Patch-Site-Registry) — exact guarded patch sites.
- [Memory and allocation map](Memory-and-Allocation-Map) — literal ownership/allocation and proof-vs-production boundaries.
