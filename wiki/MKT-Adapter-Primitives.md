# MKT adapter primitives

> **Scope:** This page owns reusable **donor -> MKMSZ semantic translation** for MKT-derived fighter actions and combo behavior. It explains what donor operations mean and how those meanings map onto established MKMSZ host primitives.
>
> It does **not** own the MKMSZ host action ABI; that remains canonical in [Player actions and special moves](Player-Actions-and-Special-Moves). Fighter image/codec/palette/storage conversion remains canonical in [MKT fighter asset translation](MKT-Fighter-Asset-Translation). Version-by-version Sektor history is canonical in [Sektor takeover proof history](Sektor-Takeover-Proof-History).

## Current conclusion

The accepted MKT -> MKMSZ direction is a **source-level compatibility adapter**, not direct relocation of MKT retail instructions and not behavioral imitation.

The reusable unit is a donor semantic such as yield, movement, facing, animation selection/advance, strike/reaction, temporary no-repel, combo-graph traversal, control transfer, or cleanup. Preserve donor phase ordering, loop counts, movement intent, animation choice, hit/block/timeout branches, strike geometry/damage, and victim-reaction meaning where current evidence supports them. Translate engine-facing operations onto MKMSZ-native helpers and layouts.

Current evidence supports the architecture, but not every category has a complete generic adapter function. Generic no-repel handling, generic victim-reaction translation, donor animation-control-token translation, and a production-ready donor action runner remain incomplete.

## Evidence boundary

Current donor findings are tied primarily to:

- **MKT USA Rev. 2 N64**, SHA-256 `30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb`;
- **MKMSZ USA Rev. 0 N64**, SHA-256 `9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6`.

The public MKT source lineage is useful for symbolic intent; retail-binary findings establish the concrete donor routines/data below. PS1 MKT and preserved Midway source assets are supplemental donor evidence only. Their addresses and binary layouts do not transfer to MKMSZ N64 without explicit translation.

Runtime confirmation is bounded to the tested route. A working Sektor or Reverse Elbow proof does not establish a universal adapter for arbitrary MKT actions.

## Translation model

The compatibility layer separates three concerns:

1. **Donor intent** — the donor control-flow phase, movement/animation request, strike record, reaction meaning, or combo edge.
2. **Semantic adapter** — a narrow operation such as sleep, face opponent, set horizontal velocity, select/advance animation, strike, no-repel, or exit action.
3. **MKMSZ host ABI** — the actual target helper, controller/actor field, scheduler transfer, action lock, and cleanup contract.

Only layer 2 belongs here. Layer 3 is canonical in [Player actions and special moves](Player-Actions-and-Special-Moves) and [Function registry](Function-Registry).

Numeric equality is not semantic compatibility. A donor function address, process-field offset, strike index, reaction selector, animation callback token, or heap pointer must not be transplanted merely because the target has a similar-looking number or record.

## Reverse Elbow donor command and historical proof selection

Reverse Elbow was chosen as the first bounded foreign-move probe because it was genuinely absent from MKMSZ while avoiding the additional projectile/effect dependencies of Acid Spit, Force Ball, Invisibility, and similar specials. Slide was not a useful first donor proof because MKMSZ already has a native Slide. This is historical proof-selection rationale, not a current product requirement.

Source-lineage material identifies the Reptile Low Kick special descriptor as ground-only, with no extra-condition callback, an input-history window of `0x10`, and mirrored direction tokens. Its semantic command is therefore **Back -> Forward + Low Kick**. The symbolic recognition/dispatch chain is:

```text
Reptile Low Kick close handler
-> secret-move search
-> facing-aware history match
-> restricted transfer
-> do_reptile_dash
-> body-propell action PROP_REP_DASH
```

| Donor symbol | Value | Meaning |
|---|---:|---|
| `PROP_REP_DASH` | `0x17` | Body-propell action selector |
| `ACT_REPTILE_DASH` | `0x216` | Fighter action/state |
| `ANIM_REP_DASH` | `0x0B` in animation table 2 | Return animation |

The donor choreography is a bounded phase machine:

```text
set Reptile dash action
-> use ordinary run animation
-> accelerate toward opponent
-> first strike/contact 0x15
-> continue through the victim under temporary no-repel
-> stop / brief pause
-> face opponent
-> select ANIM_REP_DASH
-> accelerate back
-> return strike/contact 0x16
-> stop
-> recover / exit
```

Source lineage also shows the male-ninja family sharing generic movement/reaction machinery, strike tables, and animation heaps while retaining character-specific IDs and close/special handlers. That supported selective semantic adaptation rather than copying an entire donor binary. Exact retail closure, strike records, no-repel state, and frame provenance are documented below and in [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

## Retail provenance / exact reference addresses

These coordinates are preserved as **retail MKT USA Rev. 2 donor provenance** for the semantic conclusions on this page. They are not MKMSZ addresses and must not be transplanted numerically into the target engine.

### Reverse Elbow closure

```text
do_reptile_dash          0x8004F2C0
-> do_body_propell       0x80045050, selector 0x17
-> prop_do_reptile_dash  0x800467D0
-> reptile_dash_hit      0x80046910
```

| Donor item | Retail address |
|---|---:|
| propell table | `0x800A80D0` |
| slot `0x17` | `0x800A812C -> 0x800467D0` |
| `init_special` | `0x80050420` |
| `get_char_ani` | `0x8000F910` |
| `do_next_a9_frame` | `0x8000D408` |
| `mframew` | `0x8000DB98` |
| `towards_x_vel` | `0x8006EC00` |
| `process_sleep` | `0x8005A88C` |
| `sans_repell_3` | `0x8006C7FC` |
| `strike_check_a0` | `0x8003E620` |
| `stop_me` | `0x8003DB54` |
| `face_opponent` | `0x8006D1CC` |
| `reaction_exit` | `0x8004C13C` |
| `context_jump` | `0x80080A84` |

### Pass-through / no-repel provenance

- signed halfword `f_norepell`: `0x802475E4`;
- central fighter-repel process: `0x80070A08`.

The semantic remains the three-tick repulsion-suppression countdown described below; these coordinates preserve where that conclusion came from.

### Strike / reaction provenance

- Reptile `nj_strikes` table: `0x800B0208`;
- strike `0x15` record: `0x800B041C`;
- strike `0x16` record: `0x800B042C`;
- reaction `0x74` handler `r_reptile_dash`: `0x800546A0`;
- reaction `0x24` handler `r_jax_dash`: `0x80055838`.

The exact record bytes and semantic translation rules remain in [Strike and reaction translation](#strike-and-reaction-translation).

### Cross-engine ABI field map

The field offsets below are the exact retail/target references that motivated the compatibility boundary. Numeric offsets are **engine-local**, not portable ABI.

| Engine / structure | Offset | Meaning |
|---|---:|---|
| MKT PROCESS | `+0x418` | `pa8` |
| MKT PROCESS | `+0x41C` | animation cursor |
| MKT PROCESS | `+0x3F6` | action |
| MKT OBJECT | `+0x0C` | X velocity |
| MKT OBJECT | `+0x14` | X position |
| MKT OBJECT | `+0x58` | heap |
| MKT OBJECT | `+0x5C` | dictionary |
| MKMSZ controller | `+0x6E0` | actor |
| MKMSZ controller | `+0x6E4` | animation cursor |
| MKMSZ actor | `+0x98` | resource base |
| MKMSZ actor | `+0x74` | shape |
| MKMSZ actor | `+0x7C` | render record |

## Scheduler, yield, and control transfer

### Donor semantics

The Reverse Elbow retail closure uses:

- `process_sleep` for bounded yields;
- `context_jump` / action transfer to leave the current donor process path;
- a body-propell action selector to enter the move-specific action root.

The move is a bounded phase machine: outward scan, contact continuation, pause, facing change, return animation/hit scan, recovery, exit.

### MKMSZ translation

MKMSZ has established host-side equivalents for process sleep, special-action callback installation, scheduler context transfer through the native selector bridge, native action lock, and native exit/control restoration. Exact helper addresses and host contracts remain owned by [Player actions and special moves](Player-Actions-and-Special-Moves).

A critical target lifecycle rule is already established: a top-level callback installed through the MKMSZ special-action path **must not simply return normally**. A normal return can re-enter the callback because of the installed return context. The successful Reverse Elbow lifecycle instead uses bounded execution plus scheduler/native cleanup.

**Coverage:** **Partial adapter.** Host primitives exist and the v6 Reverse Elbow lifecycle is Runtime-confirmed stable, but no generic production adapter yet accepts an arbitrary donor action graph and performs all entry/yield/exit composition.

## Movement

Reverse Elbow uses donor helpers equivalent to move toward the opponent, stop movement, and face the opponent. Its outward and return phases are repeated bounded movement loops, not a teleport or one fixed-position write.

MKMSZ has established native primitives for player horizontal velocity, stop/clear motion, finding the nearest opponent, and facing the opponent. Their exact ABI remains in [Player actions and special moves](Player-Actions-and-Special-Moves).

The old proof-only forced-X crossover is **not** donor behavior. That shortcut attempted to force the attacker across the victim instead of composing normal motion with temporary repulsion suppression.

**Coverage:** **Primitive coverage exists; generic calibration is incomplete.** A general donor velocity conversion layer still needs explicit per-engine unit/facing validation rather than assuming donor constants are directly writable target values.

## Animation selection and advance

The Reverse Elbow closure uses donor operations equivalent to selecting a character animation, advancing animation frames, and playing a bounded sequence. The return animation is:

```text
SCCOMBO10
SCCOMBO11
SCCOMBO12
0
SCCOMBO11
SCCOMBO10
0
```

The animation/frame **concept** transfers, but donor heap-relative pointers and encoded image streams do not.

MKMSZ has established native helpers for animation selection and advance. Imported visual resources must first be translated into MKMSZ-compatible assets; descriptor dimensions, pointer bases, codecs, palettes, row pitch, Type-5 generation, and storage belong to [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

Animation-script control words are also engine semantics. The Sektor Sweep proof is a useful boundary: donor visual frames transferred, while the proof deliberately preserved MKMSZ-native Sweep control words rather than copying a donor callback token numerically.

**Coverage:** **Frame/animation primitives covered; generic script-token translator missing.** Plain visual frame sequences are well-supported. Donor callback/control tokens require explicit semantic mapping.

## Strike and reaction translation

MKT strike numbers are donor-table indices, **not MKMSZ strike IDs**.

For Reptile Reverse Elbow:

| Donor index | Exact donor record | Semantic role |
|---:|---|---|
| `0x15` | `002b 0009 0022 006e 7400 0000 0001 0000` | First contact: box `(43,9,34,110)`, reaction `0x74`, zero damage |
| `0x16` | `0044 000b 0027 003c 2400 0d03 0001 0000` | Return hit: box `(68,11,39,60)`, reaction `0x24`, damage 13 / block 3 |

The donor reaction meanings are semantic, not portable numbers:

- reaction `0x74` is a Reptile-specific grounded victim hold; airborne victims are rejected and grounded victims are held for roughly 20 ticks before normal exit;
- reaction `0x24` is a generic damaging launch/flight/landing reaction.

A real adapter therefore translates **geometry, damage/block behavior, flags, and victim-reaction meaning**. It must not reuse donor indices `0x15`, `0x16`, `0x74`, or `0x24` as if MKMSZ shared those numeric meanings.

MKMSZ has native strike dispatch and collision/damage/reaction machinery; its exact ABI remains in [Player actions and special moves](Player-Actions-and-Special-Moves).

**Coverage:** **Partial adapter.** Target strike dispatch exists and bounded Sektor combo work confirms that reaction translation can fix otherwise catastrophic behavior. A general donor-reaction -> MKMSZ-reaction map remains missing.

## No-repel semantic

MKT's `sans_repell_3` does **not** teleport the attacker.

Retail evidence shows that it sets signed halfword `f_norepell` to `3`. The central fighter-separation process decrements the value once per separation tick. While it remains nonzero, normal super-close forced velocities and per-player anti-overlap corrections are skipped.

Minimum donor semantic:

```text
no_repel_ticks = 3

each native separation tick:
    if no_repel_ticks != 0:
        no_repel_ticks--
        bypass fighter-repulsion corrections
```

Reverse Elbow refreshes this state during its outward/contact continuation so ordinary motion can carry the attacker through the opponent.

**Coverage:** **Donor semantic Static-confirmed; target generic shim Pending.** The narrowest MKMSZ fighter-separation hook for an equivalent three-tick gate has not yet been established.

## Combo-record translation

The Sektor v61/v62 proof establishes a reusable rule beyond Reverse Elbow strike translation.

At the tested scope, MKT and MKMSZ share a compatible **normal-combo record grammar** closely enough to transfer record structure/layout, option chaining, button IDs, direction requirements, timing, and attacker animation selectors whose semantics are already mapped.

The high byte of the combo strike/reaction field is still a **game-local semantic selector**.

### v61 failure lesson

v61 copied donor selector `0x02` directly for long-combo knockback finishers. The attacker graph and animations ran and the uppercut-style branch worked, but the long branch caused catastrophic world/background rendering corruption.

This is **Rejected / failed** evidence against raw selector-number transplantation.

### v62 correction

v62 changed only the three affected reaction-selector bytes from `0x02` to the MKMSZ-native/proven selector `0x04`, preserving the button graph, attacker animation selectors, pointers, and input requirements. The tested combo route then became Runtime-confirmed.

The already-working `0x0504` uppercut entry remained unchanged. That is a positive **bounded coincidence**, not evidence that all selector values are cross-game compatible.

### Compatibility rule

For every donor combo edge:

1. preserve the portable record/control structure where verified;
2. identify the donor reaction meaning;
3. choose an MKMSZ-native reaction with the intended gameplay meaning;
4. validate the translated selector in a bounded proof.

Numeric equality alone is insufficient.

## Cleanup and action lifecycle

Donor actions assume donor process/object layouts and cleanup conventions. MKMSZ uses different controller/actor fields, scheduler state, action lock, and native control restoration.

Reusable target-side lessons from the Reverse Elbow proof line are:

- install the special action through the native target action path;
- set/preserve the native special-action lock as required;
- keep movement/contact loops bounded;
- do not let an installed top-level callback fall through to an ordinary return;
- leave through scheduler/native cleanup rather than ad-hoc state writes;
- treat interruption/contact paths as lifecycle branches, not merely animation changes.

The failed v3 self-reentry and incomplete v5 lifecycle remain in [Player actions and special moves](Player-Actions-and-Special-Moves). This page keeps only their reusable adapter lesson.

**Coverage:** **Known target lifecycle primitives; generic action runner Pending.**


## Sektor straight-missile translation

The v63-v70 line establishes why Sektor's straight missile should be treated as the first **generic projectile-adapter validation case**, not as an Ice-Blast recreation. Full proof chronology and artifact identities remain in [Sektor takeover proof history](Sektor-Takeover-Proof-History); donor asset/codec/storage details remain in [MKT fighter asset translation](MKT-Fighter-Asset-Translation).

### Donor `do_robo_zap`

Source-lineage `do_robo_zap` performs this setup choreography:

```text
zap_init_special_act(act_robo_zap)
rocket1_proc -> child program
robo_open_chest_fast
setup_proj_obj
projectile z-order = behind owner
adjust_xy(7,45) relative to Sektor/facing
create_proj_proc(rocket1_proc)
i_am_a_sitting_duck
sleep 0x20
robo_close_chest
```

Semantic translation:

| Donor operation | Meaning | MKMSZ-side adapter status |
|---|---|---|
| `zap_init_special_act` | establish grounded special-action ownership, face opponent, disable ordinary control/blocking, mark special state | **Partial adapter:** target lifecycle/lock/cleanup primitives are established, but no generic donor special-entry wrapper exists |
| `robo_open_chest_fast` | play donor chest-open firing presentation; frame count depends on opponent reaction state | **Partial:** player animation cursor/control is established; generic timed donor animation playback and opponent-state query remain to be wrapped |
| `setup_proj_obj` | create a projectile/resource actor before the child process exists | **Target primitive identified; generic wrapper Pending** |
| set `ozval = 0` | projectile presentation layer behind owner | **Translation required**; donor z/layer semantics are engine-local |
| `adjust_xy(7,45)` | owner-relative, facing-aware chest placement | **Target primitive identified; coordinate calibration Pending** |
| `create_proj_proc(rocket1_proc)` | create child process and bind projectile actor plus owner/opponent context | **Target primitive identified; generic wrapper Pending** |
| `i_am_a_sitting_duck` | attacker enters projectile recovery/locked state | **Partial:** target action lock/recovery exists; semantic wrapper Pending |
| `sleep 0x20` | hold/recovery interval | **Covered primitive** |
| `robo_close_chest` | reverse/close presentation then leave the action | **Partial:** animation/cleanup primitives exist; generic reverse/recovery composition Pending |

The source-lineage donor values `(7,45)` are **donor-space data**. Retail MKT USA Rev. 2 N64 applies its platform scaling before the shipped straight-rocket path: the corresponding retail placement is `(+5,+38)`. The same source-vs-retail distinction applies to flight constants: source-lineage `0x40000/0x70000` initial speed and `0xE0000` cap become retail N64 `0x33333/0x59999` and `0xB3333`. Preserve the donor semantics and the provenance of each numeric space; do not substitute ad-hoc target pixel shifts. v70's hardcoded target-space spawn correction is therefore rejected as an adapter strategy even though it was useful as a diagnostic.

### Donor `rocket1_proc`

The straight-rocket child process is semantically:

```text
bind projectile PID/ownership
play robot projectile sound
select robot rocket animation family
find animation part 4   ; horizontal/flat rocket
initial speed = 0x70000 if opponent reacting else 0x40000
animation rate = 3
smoke counter = 0
strike semantic = donor 0x12
projectile_flight_call(rocket1_flight_call)
rocket_explode_fx
```

The per-tick `rocket1_flight_call`:
- emits smoke on the donor cadence;
- increases horizontal speed by **1/16 of current speed per tick**;
- caps magnitude at `0x0E0000`;
- reapplies projectile velocity through the donor facing-aware velocity helper;
- returns to the generic projectile-flight loop.

This means acceleration, cap, animation-part selection, smoke cadence, strike meaning, and explosion are donor program/data semantics. The adapter should preserve them and translate only the engine-facing operations.

### Target projectile actor/process primitives

**Static-confirmed.** The clean MKMSZ Ice/Zap path separates projectile actor creation from projectile process creation, which is structurally compatible with the donor split.

Target resource-actor creation:
- primary Zap animation slot `0x24` contains control token `0x0B`;
- token `0x0B` dispatches to `0x80030974`;
- that path calls `0x80034510`, which consumes the following resource entry and reaches the established resource-backed actor constructor `0x800281A0 -> 0x80028128`;
- the constructor temporarily installs the new actor in current controller/process `+0x6E0`;
- `0x80030974` captures that new actor at `+0x714`, restores the owner actor to `+0x6E0`, then copies `+0x714 -> +0x648`; at completion of the token handler, `+0x648 == +0x714 == secondary actor`;
- `0x80024650` inserts that secondary actor into the active actor list.

The two staging fields have different lifetimes despite aliasing the same actor at the projectile handoff. `+0x648` is the stable secondary-actor working/staging pointer used by the stock Zap setup path. `+0x714` is an active/transfer pointer that can be temporarily repurposed. The straight-Ice action saves `+0x714`, overwrites it while creating helper context, then restores it before projectile placement; `+0x648` remains the secondary actor throughout. The generic helper at `0x800302D4` independently reinforces this relationship by copying `+0x648 -> +0x714`.

Target relative placement:
- `0x80031208(actor, x_adjust, y_adjust)` applies facing-aware actor-relative displacement by negating the X adjustment when the actor is horizontally flipped;
- in the stock straight-Ice setup, call site `0x8004AFF8 -> 0x8004B000` passes parent `+0x648` as the actor;
- the same path subsequently uses parent `+0x714` as the temporary current actor for projectile animation, confirming that placement and animation target the same staged secondary actor.

#### Exact `0x80031208` coordinate contract

**Static-confirmed.** For a freshly created token-`0x0B` projectile, `0x800245A4` zero-initializes the complete `0x118`-byte actor and the creation path does not set actor `+0xDC` before placement, so the normal `+0xDC == 0` branch of `0x80031208` is the projectile path.

Its effective contract on that path is:

```text
input:
    actor
    signed local x offset
    signed local y offset

if actor horizontal-flip bit 0x10:
    local_x = -local_x

local = { local_x, local_y, 0 }
world_delta = actor-local rotation * local

actor +0x2C += world_delta.x << 8
actor +0x30 += world_delta.y << 8
actor +0x34 += world_delta.z << 8
```

The input offsets are effectively signed 16-bit whole-coordinate values. The helper rebuilds a pure rotation transform from actor orientation `+0xAC/+0xAE/+0xB0`; it explicitly zeroes the transform translation terms before converting the matrix to floats. The fixed rotation matrix uses `0x1000 == 1.0`, and the conversion path multiplies by `1/4096`, so there is **no hidden positional scale factor** in this helper. Numerous target routines read actor `+0x2C/+0x30` with arithmetic `>> 8` before pixel-scale distance tests; `0x80031208` performs the inverse `<< 8` when adding its transformed integer offsets. The target position fields are therefore 8-fractional-bit fixed-point, while the placement arguments are whole local position units.

The horizontal mirror is already part of the helper. A translator must pass the donor signed X semantic and must **not** pre-negate it for facing.

For Sektor's straight rocket, MKT source lineage defines:

```c
adjust_xy_a5(projectile, SCX(7), SCY(45));
```

with N64 donor factors `SCF_X=80` and `SCF_Y=85`. Integer conversion therefore produces the shipped donor-local values:

```text
SCX(7)  = 5
SCY(45) = 38
```

MKT `multi_adjust_xy` mirrors X internally and adds Y directly. A follow-up source+retail trace explicitly rejects an X/Y-swap hypothesis:

- `adjust_xy_a5(_obj,_x,_y)` is a macro for `multi_adjust_xy(_obj,_x,_y)`;
- `multi_adjust_xy(OBJECT *obj, short xadj, short yadj)` adds/subtracts **argument 2** to `obj->oxpos.u.intpos` according to `M_FLIPH`, and adds **argument 3** directly to `obj->oypos.u.intpos`;
- in MKT USA Rev. 2 retail, `make_rocket` loads `a1=5`, `a2=38` before calling retail `multi_adjust_xy` at `0x8000DD3C`;
- retail `0x8000DD3C` sign-extends `a1/a2`, applies `a1` to the object's X-position halfword and `a2` to its Y-position halfword.

Therefore the donor pair really is semantic **X=+5, Y=+38**; it is not `(+38,+5)`.

The corresponding MKMSZ **offset operation** is:

```text
0x80031208(projectile, +5, +38)
```

or, at the adapter level, `place_relative(projectile, 5, 38)`. Do **not** pass source-space `(7,45)`, do not swap the axes, and do not apply the MKT 80%/85% scale a second time. On a neutral target orientation the helper contributes exactly `(+5 << 8, +38 << 8, 0)`; on rotated MKMSZ stage geometry it rotates the same local displacement into world XYZ.

**Important base-origin qualification:** this proves the argument order and offset units, not that the complete donor and target projectile-creation paths establish the same pre-offset origin. MKT `setup_proj_obj -> get_proj_obj_m` calls `match_ani_points(owner, projectile)` **before** `adjust_xy_a5(+5,+38)`. Thus donor spawn semantics are:

```text
projectile = create_projectile()
match_projectile_animation_origin_to_owner()
adjust_projectile_origin(+5,+38)
```

The current MKMSZ proof piggybacks on the stock Ice secondary-actor creation/alignment before applying `0x80031208(+5,+38)`. Equivalence of that **pre-adjust base alignment** to MKT `match_ani_points` has not yet been proven. This is now the primary static explanation to investigate for the remaining visible chest-origin mismatch; changing the proven `(+5,+38)` argument order is not supported.

The imported `ROCKETD1` descriptor itself preserves donor geometry `39x9` and donor anchor `(+26,+3)` in the proof builder, so a simple lost/swapped rocket descriptor anchor is also not currently supported. v72 remains Runtime-confirmed for stable mirrored placement, but it does not by itself prove full donor-equivalent visible spawn alignment.

Target projectile-process creation:
- `0x8004CBC4(callback)` allocates a child controller/process through `0x8002830C` with class/tag `0x700`;
- it copies relevant parent/opponent context;
- it binds child actor `+0x6E0` to the parent's staged secondary actor at `+0x714`;
- it tags that actor with `0x700` and clears parent `+0x648`; it does not clear parent `+0x714`.

**Static-confirmed correction after v71:** the `+0x648` actor passed to `0x80031208` and the `+0x714` actor promoted by `0x8004CBC4` are the same projectile/secondary actor on the stock straight-Ice path. The earlier hypothesis that the v71 placement edit accidentally moved a different Ice helper actor is rejected.

The reusable target vocabulary is therefore:

```text
actor = create_resource_actor(resource_entry)
place_relative(actor, owner, donor_x, donor_y)
process = start_projectile_process(actor, translated_program)
```

This is the intended basis for Sektor missile, Acid Spit, spear/net-style projectiles, and similar donor moves. It is **not** a claim that all such moves are already compatible; strike semantics, effects, palette binding, interruption, cleanup, and donor callback behavior remain translation-specific.

### Projectile velocity integration and cadence

**Static-confirmed target integration; cadence externally corroborated.** The normal MKMSZ actor-motion path is not numerically equivalent to MKT's object velocity integration.

MKT uses a 16.16 `POS` type and the object-display/update loop performs:

```text
oxpos.pos += oxvel.pos
oypos.pos += oyvel.pos
```

once per nominal 60 Hz game/display loop. Thus donor `oxvel.pos = 0x10000` represents one donor local position unit per donor tick.

For a normal freshly-created MKMSZ projectile (`actor +0xDC == 0`), the actor update loop at `0x80017F80` does the following for local X velocity `actor +0x14`:

```text
local_x = actor->xvel >> 8
local_y = actor->yvel >> 8
world_v = rotate_by_actor_orientation(local_x, local_y, 0)

actor->world_x_fixed8 += 3 * world_v.x
actor->world_y_fixed8 += 3 * world_v.y
actor->world_z_fixed8 += 3 * world_v.z
```

The `x3` is literal in the clean ROM: each transformed component is shifted left by 8 and then combined as `(value >> 7) + (value >> 8)`, i.e. `2*component + component`. Position fields `+0x2C/+0x30/+0x34` are 8-fractional-bit world coordinates. The low eight bits of the velocity field are therefore discarded before integration.

The main loop calls `0x80017F80` once at `0x80014258` and later waits at `0x80014280` until counter `0x802FCD44 >= 2`; `0x80015950` increments that counter. This is consistent with the game's observed 30 Hz rendering/movement cadence. Independent frame-step/TAS observations likewise report MKMSZ rendering and ordinary movement at 30 fps while some button/input paths are 60 fps. MKT's N64 game loop is nominally 60 Hz.

If one additionally assumes **one donor local position unit equals one MKMSZ world unit**, the integrator/cadence math gives the conditional field conversion:

```text
target_velocity = donor_velocity * 2 / 3
```

because two donor 60 Hz motion integrations must equal one target 30 Hz integration whose numeric velocity contributes `3x` per target update. v72 proved that direct `(+5,+38)` placement is stable and plausibly located, but it did **not** prove universal 1:1 donor-local-to-target-world scale.

For the straight rocket's steady-state constants this gives:

| Donor retail value | Constant-speed target equivalent |
|---:|---:|
| normal start `0x33333` | `0x22222` |
| reacting start `0x59999` | approximately `0x3BBBB` |
| cap `0xB3333` | `0x77777` |

These direct `2/3` values are correct for **constant velocity**, but an accelerating donor program requires temporal resampling as well. Donor `rocket1_flight_call` applies `v += v >> 4` once per 60 Hz donor tick; the v73 target callback applies it only once per approximately 30 Hz target tick. That halves the exponential-update cadence. At the same time, v73 writes the unconverted donor numeric values into MKMSZ, making the instantaneous target field about 1.5x the constant-speed equivalent. This combination explains why v73 can visibly accelerate yet still feel unlike MKT.

A faithful 60 Hz donor-to-30 Hz target translator should preserve donor-space velocity state and fold **two donor motion intervals** into each target motion interval. For donor magnitudes `d0,d1,...`, where `step(d)=min(d+(d>>4), donor_cap)`, the first target interval should represent donor displacement `d0+d1` and therefore use approximately:

```text
host_v0 = (d0 + d1) / 3
retain donor state = d1
```

Each later target callback should advance two donor substeps:

```text
d2 = step(retained)
d3 = step(d2)
host_v = (d2 + d3) / 3
retain donor state = d3
```

At the donor cap this converges to host `0x77777`. For the normal straight-rocket launch, `d0=0x33333`, `d1=0x36666`, so the first pair-averaged host field is `0x23333`, not simply `0x22222`.

This pairwise resampler is a **Static-derived temporal adapter policy**. v74 Runtime-confirms that the folded cadence path is stable and comparative 60-fps video supports its timing: MKT advances every captured frame, v74 usually every two, while both reach late-speed plateau in roughly 0.3-0.35 s. However, v74 also demonstrates that the 1:1 spatial-unit assumption is incomplete: its late normalized visible speed is only about half the donor's on the tested route. The adapter therefore needs a separate donor-local -> target-world spatial scale in addition to the 60->30 Hz temporal resampler.

### v69-v75 runtime boundary

- **v69 Runtime-confirmed:** current controller/process `+0x6E4` can be temporarily redirected after the stock helper and advanced once through `0x800304C0` to display the genuine chest-open frame on the player without hanging.
- **v70 Partially Runtime-confirmed:** the genuine horizontal rocket frame reaches the live projectile and travels, but stock Ice helper clones/tint remain, spawn placement is wrong, and the observed flight does not reproduce donor acceleration.
- **v71 Rejected / failed:** a combined placement/movement revision hard-hangs 1-3 frames after input; later tracing isolates a semantic misuse of `0x8004CC14`.
- **v72 Runtime-confirmed placement proof:** direct local `(+5,+38)` placement spawns near Sektor and mirrors correctly in both facings while leaving the inherited constant-speed flight and Ice tint unchanged.
- **v73 Runtime-confirmed acceleration behavior / calibration Pending:** a child callback that mutates only projectile actor `+0x14` produces visible stable acceleration with no hang. The proof uses donor-retail `0x33333` start, `v += v >> 4`, and `0xB3333` cap, but exact cross-engine velocity-unit equivalence remains unproven.
- **v74 Runtime-confirmed cadence-resampler stability / spatial calibration Pending:** folded two-donor-substep timing remains stable. Comparative donor/target video measures MKT late flight at about 2.13 screen-widths/s versus about 1.08 for v74; the target magnitude is under-scaled by roughly 2x on this tested route even though ramp timing is similar.

- **v75 Runtime-confirmed bounded magnitude calibration:** host velocity start `0x46666` and cap `0xEEEEE` preserve the folded cadence and double only magnitude relative to v74. User reported that it feels good and did not hang. This does not establish a universal scale.

The durable lesson is not “tune the Ice projectile until it looks like Sektor.” The accepted direction is to compose the target primitives above under donor `do_robo_zap/rocket1_proc` semantics.


## Primitive coverage table

### Straight missile: end-to-end static reconciliation (2026-09-24)

**Evidence:** disassembly of clean MKT USA Rev. 2 (`30efdbe2…`) and MKMSZ USA Rev. 0 (`9c18254a…`), the exact v75 proof (`e77b334f…`), v76–v79 builders, the Runtime-observed v80 constructor proof, and the guarded v81 first-render builder. Addresses in the left column are **MKT retail VAs**; those in the right column are **MKMSZ VAs**. This is static evidence except where a proof route is explicitly labeled Runtime-confirmed. MKT's source names below are resolved against the retail call chain; source-space constants must not replace retail N64 values.

| Donor operation / ownership | Exact donor evidence | MKMSZ/v75 primitive and boundary |
|---|---|---|
| `do_proj_robo_zap -> rzap3` entry | `0x8007BF84` enters `0x8007C068` with child `0x8007C100` and mode 0. `0x8007C068` calls `0x8007CE70` (special/open), `0x8007C00C` (create/place), `0x8007F860` (recovery), sleeps `0x20`, then `0x8007CECC` and `0x8004C13C` (close/exit). It can create/place a second projectile on its reaction branch after a ten-tick sleep. | Ice action `0x8004AB84` acquires special lock `0x800BF308=1`, selects native animation with `0x80030E98`, sleeps, then advances the owner at `0x8004AEDC` and `0x8004B0F4..0x8004B194`; `0x8004B524` clears lock and calls `0x800328FC` to restore control. v75's `0x8009A1A0` displays **one** genuine chest frame and restores `+0x6E4` immediately; stock Ice animation then continues. Open/hold/close and reacting-opponent branch are **untranslated**. |
| Create projectile and first descriptor | `make_rocket` `0x8007C00C` calls `0x8007F7EC`/`0x8007F014` to create the projectile object; `rocket1_proc` `0x8007C100` selects robot animation `0x43`, part 4 via `0x8000D1F4`, then sets the projectile visual/animation before flight. | Native token `0x0B -> 0x80030974 -> 0x80034510 -> 0x800281A0/0x80028128` constructs/stages the resource actor, then performs a **separate palette/resource bind** through `0x8001C528` before `0x80024650` inserts it. Primary slot `0x24` roots at file-`0x87 +0xDA0`; the live constructor token is `+0xDB8` with operand `+0xDBC`. v75 uses Ice entry `+0x34A58`; v80 changed only this operand to genuine rocket entry `+0x4E6E4` and ran without a material visible improvement. v75's later parent wrapper binds `actor+0x98+0xD90` after insertion. The child `0x8004B82C` is **not a remaining Ice-descriptor rebind**: exact v75 has file-`0x87 +0xFD0 = +0xD90`, and `+0xD90` is already the genuine rocket loop. Therefore the remaining first-render boundary is the constructor **plus its pre-insertion palette transaction**, not the child cursor. |
| Position and image origin | Donor creation calls `match_ani_points(owner, projectile)` inside `0x8007F7EC`, then `0x8000DD3C(projectile,+5,+38)` at `0x8007C048`; it also sets projectile `ozval=0` at `0x8007C040`. The imported first horizontal descriptor is `39x9`, anchor `(+26,+3)`. | Token `0x0B` copies owner positions and facing to the staged actor (`0x80030A0C..0x80030A54`); stock Ice additionally writes actor-local geometry `+0x4C/+0x50/+0x54` before `0x80031208` at `0x8004B000`. v75 changes only the local displacement to `(+5,+38)`, Runtime-confirmed to spawn/mirror stably. Donor matched-image origin, target actor origin, descriptor anchor, and target `+0x4C/+0x50` are **four distinct quantities**. v77's `ownerY+3` did not fix visible placement. v78's direct `0x80031394` composition hard-hung: that helper copies world position but also reads child render record `+0x7C` and can invoke `0x8003188C` when child flags/facing demand it. Its safe preconditions at this seam are unresolved. Target z/layer mapping remains unresolved. |
| Palette | Donor `0x8007F75C` binds a projectile-local palette via `0x80001730` with `0x80156A70` (rocket palette source); explosion also uses its own effect resource. | After `0x80034510` returns the new actor, `0x80030974` calls `0x8001C528(0x800B1A24,0x100,0)` and stores `(return - 0x80)` to new actor `+0x9E` **before actor insertion**. This fixed stock record is independent of the constructor resource operand, explaining why v80's descriptor-only change could leave the first visible projectile Ice-blue. v75 later overwrites `actor+0x9E=0` in its parent first-frame wrapper, after insertion. v81 keeps the stock allocation/refcount call but path-scopes its returned selector to `0` for the live `+0xDB8/+0xDBC` transaction before insertion; runtime validation is Pending. `+0x80` active-handle and destruction semantics remain to be traced. |
| Blue helper actors and screen tint | The MKT rocket routine has no Ice companion-actor pair or blue screen tint in this chain. | Ice parent saves original `+0x714/+0x6E4`, installs temporary global actor/script state (`+0x714=0x80291C10`, `+0x6E4=0xF88`, `+0x718=6`), snapshots owner coordinates into globals, then starts **two separate class `0x100` processes** at `0x8004AE68/84`. `0x80060A3C` allocates a palette/texture, constructs a resource-backed companion actor, inserts **both** it and the staging actor into the render list, updates the pair from its own script through `0x80060D14`, removes both and releases palette/texture at `0x80060E20..44`, then exits. This accounts for the two blue Sektor-like companions. `0x8004AB0C` calls `0x80044964` for blue screen tint and `0x80028564` for process exit; it creates no actor. The blue first projectile frame is a **third, separately owned** image (the Ice descriptor above). These are Ice-only semantics, but helper teardown and parent staging cannot be removed by NOPing creation. |
| Child ownership | Donor `0x8007F014` creates a projectile process with owner/opponent context and object at process `+0x418`; `make_rocket` later calls `0x8007F014` with child `0x8007C100`. | `0x8004CBC4(callback)` calls `0x8002830C` with class `0x700`, copies `+0x63C/+0x640`, binds **parent `+0x714`** to child `+0x6E0`, sets actor tag `+0x72=0x700`, clears parent `+0x648`, and **does not clear `+0x714`**. Parent temporarily switches `+0x6E0` to the secondary for its first frame and restores the owner before handoff. Generic adapter must capture the correct staged actor and preserve this transfer/cleanup, with its own callback and strike selector. |
| Flight and sound | `rocket1_proc` `0x8007C100` plays projectile sound (`0x80005760(3)`), sets animation part 4/rate 3, chooses retail reacting/normal starts `0x59999/0x33333`, sets strike `0x12`, and enters `0x8007F2C8` with callback `0x8007C1E0`. Callback uses `0x8007C7C8` for smoke cadence, advances velocity by `v>>4`, caps at `0xB3333` and calls facing-aware `0x8007F27C`. | v75 inherits Ice SFX. Its child passes `0x13` to generic `0x8004CC50`, installs child `+0x70C` callback which the loop latches into `+0x680`, and mutates only actor `+0x14` per ~30 Hz tick. Its two-donor-tick recurrence and bounded 2x magnitude are Runtime-confirmed **for the tested route**, not universal unit conversion. Initial `0x8004CC14` is setup (also resets animation rate), never a per-tick velocity setter. Generic SFX mapping and reacting-start branch remain missing. |
| Smoke/effects | Donor generic flight `0x8007F2C8` invokes `0x8007C1E0` each iteration; that callback calls `0x8007C7C8`, which toggles process `+0x3D4` and creates an effect on alternate calls. | Ice `0x8004CC50` performs sleep, animation/update, offscreen checks and contact; it does **not** supply rocket smoke. Need an adapter-owned counter and resource-backed effect/spawn/expiry contract. Do not treat the two Ice companions as donor smoke. |
| Collision, damage and reaction | `0x8007F2C8` calls donor `0x8003E620` with a fighter/selector-local strike record; contact returns `0x8000` and enters `0x8007F440` for impact handling, while offscreen and miss take their own exit branches. Donor selector `0x12` and its victim reaction must be decoded by meaning. | Child `0x8004CC50` resolves fighter-type-local selector `0x13` through `0x8004CE6C`, calls `0x8004CF3C -> 0x8002BA04`, and continues only on target status `0x4000`. Fighter type 4 selector `0x13` points to `0x800AF634` (ROM `0xB0234`): stock reaction `0x2C` freeze, block `0x05`, damage `0/0`. v75 therefore still freezes on contact. v79 alters several fields at once; its `0x04`, `20/2` values are **candidates**, not established equivalence to donor rocket damage/reaction. |
| Explosion, cleanup, control | After `0x8007F2C8` returns, `rocket1_proc` calls `0x8007C9F0`, which starts an effect process and transfers impact coordinates; `0x8007F75C` has object resource/palette related calls whose exact release roles still require tracing. Donor parent closes chest and exits independently of projectile flight. | Ice generic `0x8004CDF8` removes actor via `0x80028408/0x80024B00` and terminates child with `0x80028564` on offscreen/lifetime paths; child post-flight return in `0x8004B9CC..0x8004BA38` transfers its scheduler callback to `0x8004BB64`. The parent restores owner `+0x6E0`, executes recovery, clears lock via `0x8004B524`, and calls native exit. There is **no donor-equivalent rocket explosion** in v75. Child, companion pair, tint process and parent have distinct owners/exit paths. |

**Hang attribution boundary.** The helper at `0x80060A3C` is an allocating actor/texture process with a script-driven cleanup, not a harmless visual call. Removing its spawn changes actor-list entries and release ownership while parent state is still arranged for that process. v65/v66 also changed the player animation runner, projectile setup, placement and helper composition; v67 restored only one helper; they cannot isolate a single hang cause. v78 alone proves `0x80031394` is unsafe **in that shim at that lifecycle seam**, not which precondition or clobber caused its hang. v79 changed chest cursor/length, sleep times, palette, tint, and strike together; its hard hang cannot isolate any one of them. The v79 eight repeated chest frames face one initial wrapper advance, one prelaunch advance, and seven postlaunch advances: the last reads the terminator; `0x800304C0` returns native completion `0x4002` on zero and the parent does not inspect that result. This is a bounded static finding, **not** a demonstrated hang cause. Keep the v75 bytes immutable while tracing or testing each boundary.

**Adapter contract:** `begin_special(owner)`; `create_resource_actor(rocket_entry, projectile_palette)` as one guarded pre-insertion transaction; `bind_origin(owner, actor, donor_anchor_semantic)` without calling an unqualified `0x80031394`; `place_local(actor,+5,+38)`; `start_child(actor, owner/opponent, rocket_program)` through the `+0x714 -> +0x6E0` transfer; `flight_tick(child_state)` with paired donor cadence; `strike(semantic_record)` and explicit `on_hit/on_offscreen`; `spawn_smoke/explosion` with independent effect ownership; `end_child`; `end_parent` after chest recovery. The constructor operand is now resolved, but v80 shows descriptor replacement alone is insufficient. The current bounded v81 gate tests the paired descriptor/palette first-render transaction while preserving v75 helper, placement, child, flight, collision and cleanup machinery. After that, the distinct remaining placement seam is donor `match_ani_points`/image-origin translation; do not return to arbitrary Y/pixel tuning or re-edit the already-rocket `+0xFD0 -> +0xD90` child cursor.

**Resolved constructor operand (Static-confirmed; v80 Runtime-observed negative presentation result):** exact v75 fighter file `0x87` primary animation slot `0x24` points to `+0xDA0`. Its first token `0x0B` is at `+0xDB8` and its consumed operand is `+0xDBC = +0x34A58`; `+0x34A58 -> +0x34A60` is the Ice-derived entry. Imported rocket `+0x4E6E4 -> +0x4E6EC` uses the same outer-entry/descriptor grammar. The later `0x0B,+0x34A58` pairs at `+0xE00/+0xE04`, `+0xE50/+0xE54`, and `+0xEAC/+0xEB0` are separate later stream sites and were not changed by the latest v80 proof. Latest v80 changed only relocated ROM `0xF40DBC: 00034A58 -> 0004E6E4`; it remained visibly Ice-derived, which led to the pre-insertion palette bind above.

| Donor primitive / semantic | Donor evidence | MKMSZ semantic target | Coverage | Canonical detail |
|---|---|---|---|---|
| process sleep / bounded yield | `process_sleep` | Native process sleep | **Covered primitive** | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| action/context transfer | body-propell action + `context_jump` | Special-action installer + scheduler selector bridge | **Partial adapter** | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| action lock | donor action ownership | Native special-action lock | **Covered primitive** | [Player actions and special moves](Player-Actions-and-Special-Moves) |
| move toward opponent | `towards_x_vel` | Native player horizontal velocity | **Covered primitive; calibration needed** | Player Actions |
| stop movement | `stop_me` | Native stop/clear motion | **Covered primitive** | Player Actions |
| face opponent | `face_opponent` | Native find/face-opponent helpers | **Covered primitive** | Player Actions |
| select animation | `get_char_ani` | Native animation selection | **Covered primitive** | Player Actions |
| advance animation | `do_next_a9_frame` / playback | Native animation advance | **Covered primitive** | Player Actions |
| donor frame/texture resource | donor heap-relative descriptors/codecs | Rebuilt MKMSZ descriptors + native storage | **Covered asset path for proven formats** | [MKT fighter asset translation](MKT-Fighter-Asset-Translation) |
| projectile resource actor creation | `setup_proj_obj` / donor projectile object | resource-backed secondary actor path via token `0x0B`, `0x80030974 -> 0x80034510 -> 0x800281A0/0x80028128` | **Target primitive identified; wrapper Pending** | This page + Function Registry |
| owner-relative placement | `adjust_xy_a5` | facing-aware actor displacement `0x80031208` | **Runtime-confirmed at Sektor v72 scope** | This page + Function Registry |
| projectile child process | `create_proj_proc` | `0x8004CBC4 -> 0x8002830C` child controller/process binding | **Target primitive identified; wrapper Pending** | This page + Function Registry |
| projectile flight callback | `projectile_flight_call(callback)` | MKMSZ projectile loop `0x8004CC50`: child `+0x70C` is latched into `+0x680` and invoked once per flight iteration before strike resolution | **Runtime-confirmed callback/cadence and bounded magnitude through v75; universal spatial scale Pending** | This page + Player Actions |
| projectile per-tick state | donor `p_store*` fields | adapter-owned child-process scratch/state | **Missing generic ABI** | This page |
| projectile effect | `rocket_smoke`, `rocket_explode_fx` | target-native effect/SFX semantics | **Missing generic effect translation** | This page |
| animation callback/control token | donor script callback semantics | Equivalent MKMSZ-native control token/callback | **Missing generic translator** | This page |
| strike check | donor strike index + record | Native strike dispatch with translated semantics | **Partial adapter** | This page + Player Actions |
| victim reaction | donor selector/function | MKMSZ-native semantically equivalent reaction | **Missing generic map** | This page |
| no-repel | `sans_repell_3` / three-tick countdown | Narrow target separation bypass | **Missing generic shim** | This page |
| normal combo record | donor combo graph | MKMSZ normal-combo graph | **Runtime-confirmed at v62 scope** | This page + Sektor mapping |
| combo reaction-selector high byte | donor game-local selector | MKMSZ selector chosen by meaning | **Translation required** | This page |
| normal action exit | donor action/reaction exit | Native exit/control restore | **Covered primitive; composition partial** | Player Actions |

“Covered primitive” means an appropriate target mechanism is established. It does **not** mean arbitrary donor code can call it without an adapter or that the complete donor move is production-integrated.

## Known missing generic adapter functions

1. **Donor action-phase runner** — express donor phase ordering, sleeps, branch-on-contact, timeout, facing changes, and guaranteed native cleanup without rewriting scheduler glue per move.
2. **Projectile actor/process wrapper** — expose the now-identified target actor creation, relative placement, child-process binding, owner/opponent context, and cleanup as a reusable adapter API instead of replaying Ice choreography.
3. **Projectile callback/state ABI** — callback dispatch itself is now identified: `0x8004CC50` latches child `+0x70C -> +0x680` at entry and calls `+0x680` once per flight iteration after sleep/animation/offscreen checks and before strike resolution. Generic adapter-owned scratch/state beyond that dispatch contract remains Pending.
4. **Velocity/facing conversion policy** — target integrator semantics and 60 Hz -> 30 Hz temporal resampling are established; v74 comparative runtime evidence showed a separate donor-local -> target-world spatial scale was required. v75 Runtime-confirms a bounded 2x host-magnitude calibration on its tested route; universality is Pending.
5. **Projectile effect/palette translation** — bind projectile-local palette semantics and map donor smoke/explosion/SFX effects without inheriting Ice presentation.
6. **No-repel gate** — implement the donor three-tick countdown at a narrow MKMSZ separation hook, without forced crossover or teleport behavior.
7. **Strike/reaction translator** — map donor geometry/damage/flags/reaction meaning to MKMSZ-native strike and victim-reaction primitives.
8. **Animation-control-token translator** — map donor animation callbacks/control tokens; visual-frame import alone is insufficient for scripts containing engine callbacks.
9. **Generic combo semantic mapper** — preserve proven normal-combo structure while resolving every game-local strike/reaction selector semantically and validating it.

These are design gaps, not permission to invent target semantics. Each becomes covered only when the MKMSZ-side behavior is established and validated at the appropriate scope.

## Rejected and superseded adapter approaches

The following failures remain reusable architectural evidence:

- **Behavioral imitation as the end goal:** superseded by faithful donor control/data preservation with narrow target translation.
- **Direct retail-instruction relocation:** rejected as a general strategy because process/object layouts, scheduler ABI, globals, table semantics, heaps, and resource formats differ.
- **Forced-X crossover:** rejected as a substitute for donor pass-through; donor behavior is ordinary motion plus temporary repulsion suppression.
- **Raw numeric strike/reaction reuse:** rejected; donor strike IDs and reaction selectors are table-local semantics.
- **Normal return from an installed MKMSZ special-action callback:** rejected by the v3 self-reentry failure.
- **Projectile setup used as player propulsion:** superseded by the corrected native player-velocity helper.
- **Omitting native lifecycle state such as the special-action lock:** rejected by the unstable early proof path.
- **Blind copying of donor animation callback/control words:** rejected by the ABI boundary; keep target-native control words until donor token meaning is explicitly translated.
- **v70 Ice-path tuning as the final missile implementation:** superseded. Hardcoded target-space spawn shifts and a grafted acceleration callback did not reproduce donor placement/flight and left Ice helper/palette behavior visible. Preserve donor `do_robo_zap/rocket1_proc` semantics over generic target projectile primitives instead.

Detailed v1-v8 Reverse Elbow history remains canonical in [Player actions and special moves](Player-Actions-and-Special-Moves). The old behavioral-recreation page remains historical until its own retirement task.

## Pending validation

The smallest useful next adapter research is to:

- turn the identified MKMSZ projectile actor/process primitives into a minimal generic `create_projectile / place_relative / start_projectile` adapter contract;
- validate that contract with Sektor's donor `do_robo_zap -> rocket1_proc` ordering before adding explosion/damage polish;
- preserve v75's Runtime-confirmed bounded cadence/magnitude as the current flight control while establishing a reusable spatial-unit policy;
- map projectile-local palette/effect/strike semantics without inheriting Ice behavior;
- locate the narrowest MKMSZ fighter-separation hook for the donor no-repel countdown;
- establish one exact donor victim-reaction translation without bypassing MKMSZ interruption/cleanup;
- keep every proof allocation separate from production-owned space.

These are post-1.0 research items unless the current roadmap changes.

## Related pages

- [MKT compatibility overview](MKT-to-MKMSZ-Compatibility-Layer) — accepted strategy, compatibility contract, and routing.
- [Player actions and special moves](Player-Actions-and-Special-Moves) — canonical MKMSZ host action/scheduler/control ABI and Reverse Elbow host proof history.
- [MKT fighter asset translation](MKT-Fighter-Asset-Translation) — donor fighter descriptors, codecs, palettes, Type-5 generation, and resource packing.
- [Sub-Zero to Sektor animation mapping](Sub-Zero-to-Sektor-Animation-Mapping) — slot mapping and current Sektor coverage.
- [Sektor takeover proof history](Sektor-Takeover-Proof-History) — versioned vNN chronology, proof identities, runtime results, supersession, and proof-specific allocations.
- [Function registry](Function-Registry) — canonical target function meanings.
- [Memory and allocation map](Memory-and-Allocation-Map) — production/proof ownership boundaries; successful proof caves are not reusable allocations.
