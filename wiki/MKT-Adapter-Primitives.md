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

## Primitive coverage table

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
2. **Velocity/facing conversion policy** — normalize donor movement requests into MKMSZ-native values after explicit unit validation.
3. **No-repel gate** — implement the donor three-tick countdown at a narrow MKMSZ separation hook, without forced crossover or teleport behavior.
4. **Strike/reaction translator** — map donor geometry/damage/flags/reaction meaning to MKMSZ-native strike and victim-reaction primitives.
5. **Animation-control-token translator** — map donor animation callbacks/control tokens; visual-frame import alone is insufficient for scripts containing engine callbacks.
6. **Generic combo semantic mapper** — preserve proven normal-combo structure while resolving every game-local strike/reaction selector semantically and validating it.

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

Detailed v1-v8 Reverse Elbow history remains canonical in [Player actions and special moves](Player-Actions-and-Special-Moves). The old behavioral-recreation page remains historical until its own retirement task.

## Pending validation

The smallest useful next adapter research is to:

- locate the narrowest MKMSZ fighter-separation hook for the donor no-repel countdown;
- establish one exact donor victim-reaction translation without bypassing MKMSZ interruption/cleanup;
- validate a reusable donor phase runner against one bounded move rather than hardcoding a second choreography;
- expand combo translation only through semantically resolved reaction selectors;
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
