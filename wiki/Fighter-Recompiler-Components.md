# Fighter recompiler — move components

> **Scope:** milestone 2 of the [Fighter recompiler plan](Fighter-Recompiler-Plan) (progress: [status](Fighter-Recompiler-Status)). It is the **component catalogue**: the engine-neutral vocabulary that move programs are written in, with each component's meaning, parameters, units, ending and MKMSZ lowering. It also records the **host references** checked for reuse (MKMSZ Quan Chi's projectile, the Eye item). Donor readings stay in [MKT move readings](Fighter-Recompiler-MKT-Moves); the host action ABI stays in [Player actions and special moves](Player-Actions-and-Special-Moves).
>
> **Evidence:** catalogue and programs are Implementation/CI-confirmed (`fighter_import/components.py`, `tests/test_fighter_components.py`). Host references are Static-confirmed (clean MKMSZ USA Rev. 0, 2026-11-11). Lowerings marked *existing* reuse runtime-validated Sektor code; *planned* lowerings have no runtime evidence yet.
>
> **Status: draft for owner review** (milestone 2 task 7).

## Move programs

A move program is data (`src/mkmszr/fighters/moves/<fighter>.json`, format 1):

- **command:** `buttons` (mask), `tokens` (newest first, as facing right: `9` toward, `8` away, `7` down), `window` (ticks), `src`, and optional `conditions` (below); `release: true` (MKT's button-release tables, High Punch only so far: the record goes into a release table run by the HP release event, Rayden's Shocker, specials proof v25);
- **steps:** a list of components with their parameters;
- **movement** (optional, `true`/`false`): a movement ability. The build charges it no Ice unless the fighter description's `costs` names a cost (owner rule, 2026-11-24; [Amendment 1](Fighter-Recompiler-Amendment-1));
- **grab** (optional, `true`/`false`): a grab (Rayden's Shocker). The build charges twice Ice Blast's Ice (`0x40`) unless the description's `costs` names a cost (owner rule, 2026-11-26);
- **gaps:** what the vocabulary cannot yet express, each naming the move.

`components.validate_programs` checks every step against the catalogue and rejects unknown components, unknown or missing parameters, bad units, unknown reactions and missing provenance.

**Provenance (owner decision 2026-11-11).** Every parameter carries its source in the step's `src` map:

- `"MKT 0x…"`: the donor instruction or data word;
- `"host"` or `"host 0x…"`: an MKMSZ fact;
- `"owner"`: an owner decision.

**Units.**

| Unit | Meaning | Host conversion |
|---|---|---|
| ticks | donor process ticks | **one host tick per MKT process tick** for animation frames and sound cadence (owner observation, projectile proofs v05 → v06; same factor as the Sektor smoke-puff observation, proofs v35–v41). Motion keeps the accepted rocket conversion (`physics.fold_donor_speeds`); the owner finds the rocket speed slightly off but not by a factor of two (revisit later) |
| px | donor pixels | 2 world units per pixel (`host.UNITS_PER_TEXEL`) |
| vel / accel | donor 16.16 pixels per tick (per tick²) | standard-jump calibration (`physics.convert_velocity` / `convert_acceleration`) |
| anim | `{table, slot, part?, offset?}` in the donor fighter's animation tables | the body builder imports the named frames into the fighter file |
| sound | `{fighter: n}` (donor fighter sound table) or `{shared: n}` | donor sample installed on an isolated host chain (`sound.install`) |
| effect | `{mkt_fx: n}` (donor shared effect) | MKT-art effect process (`effects.emit_spawn`) |

## Components

| Component | Meaning | Parameters | Ends | MKMSZ lowering |
|---|---|---|---|---|
| `begin` | Start a special | `action_mkt` (provenance), `face`, `stop` | at once | *existing*: `special_begin` `0x80049F90` (stop, face, busy input map), lock `0x800BF308`, host action id |
| `end` | Return control | — | the move | *existing*: exit action `0x800328FC` |
| `sleep` | Wait | `ticks` | after the time | *existing*: `process_sleep` `0x80028794` |
| `wait` | Wait for a state | `until`: `opponent_settled` | when true | *new* (host opponent-state check to be found) |
| `repeat` | Loop | `count`, `steps` | after `count` | backend loop. A per-tick loop (its body under one host tick) scales its count with the fighter's donor ticks. From Rayden specials proof v28, a body that sleeps at least one host tick keeps MKT's count, and its sleeps are rounded on the running total (MKT 3-tick frames at 2 donor ticks per host tick: 2, 1, 2, 1, …), so both the frame count and the time are MKT's (`_timed_repeat`). |
| `animate` | Select a body animation | `anim`, `rate`, `until`: `phase_end` (play it out) / `running` (rate-gated, advanced by the host each tick) / `manual` (advanced by `next_frame`) | per `until` | *existing*: cursor + `animation_rate_init` / `animation_advance`; `phase_end` via `0x80031070` A table-0 animation with no secondary script plays the body's own primary slot (host primary *k* = MKT table-0 index *k*), selected from table 0 (Rayden's teleport reappear = his getup, v24). |
| `pose` | Show one frame | `anim` (with `offset`) | at once | *existing*: set cursor + advance |
| `next_frame` | Advance one step | — | at once | *existing*: `animation_advance` `0x800304C0` |
| `finish` | Play the current animation out | `rate` | phase end | native `0x80031070` |
| `face` / `flip` | Turn to the opponent / mirror | — | at once | *existing*: `face_opponent` `0x80031EF0`; flip *new* `flip` lowers to the host's turn `0x8003188C` (Rayden's reversed lightning, specials proof v20); the description's `turn_back` turns a move's `face` steps into `flip` (owner). |
| `velocity` | Set motion along the facing | `x`, `y?` | at once | *existing*: actor `+0x14` (`0x8002B1EC`) after calibration |
| `stop` | Zero motion | — | at once | *existing*: `0x8002B1C0` |
| `jump` | Ballistic motion | `x`, `y`, `gravity`, `until`: `landing` / `below_screen` / `surface` | per `until` | *existing* (teleport): adapter-integrated arc. `until: landing` lowers to the stock jump `0x800321D0` (converted velocities and gravity, rate and animation kept); it counts the airborne ticks and returns on landing (Rayden's torpedo drop, specials proof v02, Pending). It clears controller `+0x70C` first, as every stock caller does: the jump calls a non-zero `+0x70C` every air tick (v02 hang, fixed in v03). Optional `rate` (donor ticks): the stock jump steps the current animation at it each air tick (Rayden's bounce flip, v09); without it the animation is kept. With the tuning `air_control` it installs the straight-air input map `0x8009FA00` first, so the stock jump's Left/Right steering works (the busy map turns it off; Rayden v07) |
| `shake` | Jitter in place | `dx`, `dy`, `count`, `ticks` | after `count` | *existing*: `0x80031208` offsets |
| `shake_screen` | Screen shake (MKT `0x8002A750`) | `amplitude` (px), `count`, `ticks` | at once (a process runs it) | *new* (Rayden torpedo, specials proof v09): a payload process (id `0x15`, as the host's shakes) moves the host's vertical camera offset `0x8009A928` by the amplitude and flips its sign every `ticks`, `count` times, then zeroes it. Pending |
| `hover` | Level flight: no gravity, no vertical motion | — | until the next motion step | *new* (Rayden torpedo, specials proof v02): actor gravity `+0x10` and y velocity `+0x18` set to 0; controller `+0x6B2` counts up so the per-tick floor check `0x80024BA8` does not install the stock fall (from v05 every tick, also at floor height: over a ledge no floor region matches). Pending Since generator step 4 the backend adds it for moves tuned `airborne` (after the begin, first on each tick of hit windows and carries; `fighter_build.with_hover`), not the program. |
| `carry` | Fly on with the victim held in front (MKT torpedo `0x800452C4`) | `ticks`, `every_tick` | until the victim nears a wall or `ticks` pass | *new* (Rayden torpedo, specials proof v03): sets a payload word shared with the victim's `torpedo_carry` reaction, runs `every_tick` (hover, pass-through) and sleeps a tick while the word is set, then clears it. Pending |
| `pass_through` | No fighter repulsion | `ticks` | after the time | **gap**: host equivalent of MKT `sans_repell_3` not located. In specials proof v15 (skipped) the dash stopped at the victim. v16: clear actor `+0x8C` bit `0x1000` (as stock Freeze on Contact, `0x80034740` / `0x80034658`) and re-apply the speed each tick; `end` sets the bit again. Runtime-confirmed together (Reptile v16). The bit only turns the stage lighting on (Rayden specials proof v17), so the speed is what lets him through (inference) |
| `relocate` | Reappear by the opponent | `to`: `behind_opponent`, `dx` (px past it), `dy?` | at once | Generic since Rayden specials proof v23: the subroutine `lower_special.emit_relocate_routine`, Sektor's runtime-confirmed teleport reposition (nearest enemy in range 592 on the same path, its floor or his own, wall room, floor probe with near-side and own-x fallbacks, snap to the probed floor, cornered enemy nudged, face it); the move's condition refuses with no enemy in range (`target_range`). MKT chooses the side by the arena edges; the host by the room. Sektor's own build still uses its legacy module. Pending (Rayden) |
| `afterimage` | A copy of the fighter left where he stands, playing an animation | `anim`, `rate` | the animation's frames × rate | *new* (Rayden's teleport, MKT `0x8006DA14` + process `0x80045854`; specials proof v23): `lower_projectile.emit_afterimage_spawn` keeps his place and facing in the process's words, then an effect-class process (`0x15`, so specials stay free) builds an actor from his (projectile builder, art placed from his donor frames, in the palette its first frame names, else his body palette; drawn at his own `+0xD8`), shows it for frames × rate host ticks, removes it (v24). Pending |
| `sound` | Play a sound | `sound`: `{fighter: n}`, `{fighter: n, random: k}` (one of n..n+k-1, evenly) or `{shared: n}` | at once | *existing*: isolated host chain per donor sound; `random` picks through the per-thousand gate `0x80016008` (Rayden torpedo, specials proof v08; MKT `ft_sound(randu(k) + n - 1)`) A donor sound event with more than one track (Rayden's Shocker sound 5, MKT event `0x205`) takes one chain per track, its tracks retargeted to the chains' patches, in one host event read from the sample area (specials proof v27; [Sounds and music](Sounds-and-Music#multi-track-donor-sounds-2026-11-26)). A stream the port cannot read is left out and reported (`report["unported_sounds"]`; v25–v26 did that for sound 5). A move whose description skips its sounds takes no chains for them. |
| `effect` | Start a shared effect | `effect`, `at?` | at once | *existing*: MKT-art effect process. `lower_special.emit_action(effects=...)` starts one through `fx_spawn_xy`; `effects.mkt_animation_art` reads a shared MKT `create_fx` animation (Reptile's invisibility fire, specials proof v19) |
| `strike` | Body hit check over a window | `strike`, `ticks`, `skip?`, `every_tick?`, `only_if?` (`opponent_settled` / `rising`), `on_hit`, `on_block?` | after `ticks`, or on contact | *existing*: KSEG0 strike record + `0x8002BA04` (`host.strike`); reaction by meaning (below) |
| `projectile` | Spawn a projectile (the move continues) | `art`, `offset`, `speed`, `rate`, `strike`, `accel?`, `cap?`, `hum?`, `trail?`, `checks?`, `homing?`, `wrap?`, `impact` | the move: at once; the projectile: on contact or offscreen | **planned generic projectile** ([below](#generic-projectile-lowering-planned)) |
| `stealth` | Enemies lose track of the fighter | — (the length is the description's Ice-paid timer, `specials.<move>.stealth`; the program's `ticks` was never lowered and is gone since generator step 4) | after the time | native Eye effect ([below](#eye-item)): `lower_special.emit_stealth_start` / `emit_stealth_timer` (Reptile specials proof v18, Pending) |
| `stamp` | Record "used now" for a cooldown | `key` | at once | *new*: a per-player tick word (allocation needed) Since Rayden specials proof v23 it is lowered for moves **without a projectile** whose command has a `cooldown` condition: the stamp sets a word and starts a process (`lower_special.emit_cooldown`) that clears it after the cooldown (donor ticks scaled); the condition refuses while it is set. Projectile moves keep the host one-projectile rule (Reptile's accepted forceballs unchanged). |

**Victim reactions** (strike `reaction` / `blocked_reaction` are meanings; the backend maps each to a host reaction):

| Meaning | Donor | Host |
|---|---|---|
| `torpedo_carry` | MKT torpedo `0x800452C4`: the victim carried along until a wall or the end, then thrown back toward the attacker (x `0x33333`, y `-0x6CCCD`, gravity `0x5199`) | `lower_special.emit_carry_reaction`: the victim morphs (`0x800572C4`, `0x80057478`), stop, the first frame of root `0x1E`, then each tick it is held at a grab point in front of the player (v04: 72 px ahead at his y, tunable as `specials.<move>.carry`; no gravity or y speed, previous y moved, airborne counter counting every tick (v05; v04 counted it only above the floor and a ground carry fell at a ledge), so no landing, fall or ledge grab while held) while the attacker's `carry` word is set; it clears the word when its room to the wall ahead (`0x80034C8C`) is under 20 px, or ends after 24 ticks, then runs the lifted knockback as its release (`lower_projectile.REACTION_LOWERING["torpedo_carry_release"]`): from v08 with no push and no lift, so the victim falls from where it was held and gets up, as MKT's `0x8005391C` (v03–v07 threw it with `do_jump(0x33333, -0x6CCCD, 0x5199)`, which is Rayden's own bounce misread). Spare reaction entry `0x2B` (Rayden specials proof v03). Pending |
| `shock_stagger` | MKT `0x80` (`0x800539A8`): the victim pushed back at `0x26666`, its slot `0x20` twice with its cyan shock palette | `lower_projectile.REACTION_LOWERING["shock_stagger"]`: Acid Spit's lifted host stumble (the same push, the victim's root `0x20`) entered through `emit_blink_start`, which starts `emit_blink`: the victim's vertex colours (`+0xA0..+0xAB`, stage lighting paused) alternate cyan / its own every 4 ticks, 8 times (host enemies have no MKT palettes; v17 every 2, owner: half speed). Rayden's lightning (specials proofs v16–v18). Runtime-confirmed (bounded): stagger (v17), blink rate (v18, owner: "finally good") |
| `shock_stagger_toward` | MKT `0x81` (`0x80053A48`): as `0x80`, the victim pushed towards the attacker (`towards_x_vel`; the reversed bolt comes from behind) | `REACTION_LOWERING["shock_stagger_toward"]`: `shock_stagger` with the push negated. Rayden's reversed lightning (specials proof v20). Pending |
| `shock_hold` | MKT Shocker `0x80073228` (victim routine `0x8005A1B8`): the victim held while shocked, ±4 px every 3 donor ticks, its shock palette on and off 8 times, then dropped (`0x80058728`) | `lower_special.emit_shock_hold_reaction`: the victim morphs (as `torpedo_carry`), stops, shows root `0x20`'s first frame, starts a cyan blink process (`lower_projectile.emit_blink`, 16 changes every 3 host ticks), is held at its height for 96 donor ticks (no gravity, airborne counter counting) with a 4 px jiggle every 3 donor ticks, then runs the lifted knockdown (`torpedo_carry_release`). From specials proof v27 it turns to face him and is held at his hands each tick: MKT `0x800733F8` (match_ani_points, flip_single, then the per-victim offset of table `0x800AAF8C`; the common entry dx −44, dy −13, then dy − 8) puts the victim's anchor 44 px in front of his and 21 px up. v25–v26 left it where the strike found it. Spare reaction byte `0x4E` (Rayden specials proof v25). Pending |
| `elbow_hold` | MKT `0x74`: grounded victim held about 20 ticks, airborne rejected | `lower_special.emit_hold_reaction`: the stock hit reaction `0x80054B20`'s preamble (with its airborne handler), stop, the first hit pose (slot `0x1C`), still for 20 donor ticks, exit; no voices. From v16 it keeps the victim's current frame, as MKT does; v15's hit pose read as a hit. From v17 it skips the stock hit effect `0x800504C4` (blood). Supplied in a spare reaction entry (byte `0x4C`, specials proof v15). Pending |
| `launch` | MKT `0x24`: damaging launch, flight and landing | The stock roundhouse's reaction `0x0C` (owner after v15, where the uppercut `0x08` was used). Pending (v16) |
| `knockback_arc` | MKT `0x71` (forceball): victim action `0x625`, launched on an arc **toward the attacker** (`do_jump(-0x2CCCC, -0x6CCCC, 0x5199)` through `0x8006EBB0`; direction from the owner's comparison of proofs v02/v03, not from the static sign reading) | Lifted copy of host `0x25` (`0x80057C14`) with the converted MKT arc `0x800321D0(-0x3B73B, -0x90623, 0x5A3C)` and without its stock hit sound (Runtime-confirmed bounded, proof v06). From composition v03 it first calls the stock victim morphs `0x800572C4` and `0x80057478`, as the stock launch `0x0C` does. Without them, a two-file enemy (Temple MONK3) played its unfilled root `0x1E` and crashed the game (composition v02, owner's save state). Pending |
| `acid_stagger` | MKT `0x72` (acid): victim action `0x626`, staggers back. Host (2026-11-11): the lifted Fire spiked-rod trap stumble that Sektor's rocket was accepted with (`0x80051280`), without its 8-tick pause, push `0x56666 × 0x26666 / 0x33333 = 0x40CCC` (`lower_projectile`, kind `stumble`) | Pending (specials proof v10) |
| `rocket_stumble` | MKT rocket reaction → `zap_stumble` | *existing* (Sektor rocket) |
| `uppercut` | teleport strike | host reaction `0x08` (*existing*) |
| `blocked`, `none` | stock blocked reaction / no reaction | — |

**Command conditions:** `buttons_held` (mask held exactly), `holding_away`, `cooldown` (`key`, `ticks`; from proof v30 a stamp of the 60 Hz clock written by the move's `stamp` step, refused until `ticks` have passed, MKT's own count; v23–v29 a word cleared by a timer process), `held_for` (`ticks`: the button held at least this long before its release, MKT `ticks_since` of the press stamp; lowered to a stamp of the 60 Hz clock `0x802E7DC0` by the High Punch press wrapper, its age compared at the release (from Rayden specials proof v30; v25–v29 counted in a process whose running flag a stock process kill could leave stuck)), `projectiles_below` (`count`) and `opponent_state` (donor guards whose meaning is still Pending, kept as text).

## Coverage

| Fighter | Programs | Components used | Gaps listed |
|---|---|---|---|
| Reptile | forceball fast, forceball slow, acid spit, invisibility, slide, elbow dash | 20 of 23 | 6 (opponent-state guard, acid reaction, acid fighter-16 exception, invisibility flag readers, slide strike record, strike flag) |
| Sektor | straight, double and homing rocket, teleport uppercut (data only; the code stays frozen legacy) | 11 | 6 (chest sequences, rocket strike record, direction art and smoke offsets, homing phases and crosshair, teleport provenance granularity, velocity lead) |

Sektor's gaps are the robot-specific parts of his rockets; they would become projectile parameters (`direction_art`, `phases`, `marker`) if a later fighter needs them.

## Host references

### Quan Chi's projectile

MKMSZ Quan Chi is enemy type `0x1B` (fighter file `0x93`; [Test Characters record 22](Enemy-Randomization#static-fighter-type-names-relevant-to-the-ordinary-pool)).

**AI action lists.** His action lists are entry `0x1B` of the four distance-band tables `0x800A32B4`, `0x800A34C8`, `0x800A370C` and `0x800A3948`.

**The projectile.** The only self-moving projectile among his actions is `0x800498A8` → child process `0x80049668`. The owner confirmed it is the move he meant (2026-11-11): on a hit **the target is knocked back**.

1. **Action** `0x800498A8`:
   - secondary animation slot 2, four steps at 4 ticks;
   - starts the child (class `0x800`, `0x8002830C`);
   - sleeps 40, then recovers.
2. **Child** `0x80049668`. The steps below are what to reuse:
   - **Creation:**
     - sound `0x12` with the actor's pan;
     - `projectile_build` `0x80047160(type, secondary slot 3, …, palette 0x372F8)` draws the projectile from **his own fighter file**;
     - x offset ±`0x4600` by facing, z −`0x1000`.
   - **Motion:** x velocity ±`0x60000` (6.0 px/tick); host integration.
   - **Hit trigger:** `projectile_collision_dispatch` `0x8004CF3C(actor, 0x11)` every tick until the first contact. It uses the type's strike table `0x800AF340[type]` and the collision core `0x8002BA04`.
   - **Strike record** (type `0x1B` selector `0x11`, `0x800B08F4`): box `(88, 8, 64, 44)`, reaction `0x39` / blocked `0x01`, damage 28 / block 4.
   - **On contact:**
     - **Unblocked:** the victim takes host reaction `0x39` (`0x80058F9C`): primary slot `0x20`, pushed back through `0x80032734` with `0x30000`, then stops. This is the "launch" the owner sees. The ball flies on without further hits.
     - **Blocked:** the collision core sets `0x802ECD88 = 1` on its blocked paths, and only then the ball deflects (`vx = -vx/4`, `vy = -4.0`, gravity `0xA000`).
   - **Difference from Reptile's forceball:** Reptile's ball stops on contact and plays its impact frames, and his victim is launched on an arc toward him (`knockback_arc`). These are behaviour, so they come from Reptile's program; only the host mechanics are reused.
   - **Sound:** `2` every 8 ticks.
   - **End:** `actor_offscreen` `0x80035088(actor, 200)`, then `actor_list_remove`, `dynamic_texture_release` and `process_exit`.

The same build-and-collide pattern is used by the armed grunts (`0x80043EB0`) and by 26 other enemy projectile sites. The player's own Ice child (`0x8004CC58`) uses the same `0x8004CF3C` dispatch with type 4, whose strike table is `0x800AF484`.

**Who a projectile can hit (Static-confirmed).** At `0x8002BB40` the collision core reads the attacking controller's class (`+0x6D8`). Class `1` (the player) and class `0x700` (player projectiles; Ice's child is started with that class by `0x8004CBC4`) take the enemy-victim scan at `0x8002CAE4`. Every other class, including Quan Chi's `0x800` child, takes the player-target path. A player projectile must therefore run as class `0x700`.

### Generic projectile lowering

**Runtime-confirmed bounded (owner, proof v06, 2026-11-11):** Sub-Zero (clean ROM) throws Reptile's MKT forceball on `F,F + LK`; it looks, sounds, hits and launches like MKT's. Builders in `Experimental/FighterRecompilerProofs/` (v01–v06), each reproducible from the clean ROMs.

**Backend v1 (Implementation/CI-confirmed):** `fighter_import/lower_projectile.py` lowers a move program's `projectile` step:
- **Art:** `donor_part` reads the MKT script part (frames, loop, and the token-13 palette); `place_art` lays out the type-4 frames, the 64-colour palette record and the frame scripts in the fighter file.
- **Sounds:** `install_sounds` hosts the donor samples.
- **Strike and reaction:** `strike_record` builds the record; `REACTION_LOWERING` maps the reaction meaning, with the arc converted.
- **Code:** `emit_spawn`, `emit_process` and `emit_data`.

Proof v07 builds the projectile from `reptile.json` (`forceball_fast`) through this module and is **byte-identical to v06** (`tests/test_lower_projectile.py`, ROM-backed).

The native path, without patching the Ice root:

1. **Child process.** `controller_clone_alloc(0x700, child)`: class `0x700`, as Ice uses, so it hits enemies (Quan Chi's `0x800` would hit the player). The parent copies its opponent links (`+0x63C`, `+0x640`) into the child and clears `+0x638`, as `0x8004CBC4` does.
2. **Build.** `projectile_build` `0x80047160` with **type 4** (read from the cloned owner actor), a file-`0x87` table-1 slot holding the art, a dynamic texture of the largest frame, `+0xD8 = 0x46`, and the palette record offset. Guarded data edit `0x800A0324[4] = 0x80291C10` (the table's only reader is `0x80046F74`). The actor tag `+0x72` is set to `0x700`, as Ice's.
3. **Placement.** Owner's position, then `0x80031208(actor, dx, dy)`. For this actor, `+dy` moves the ball **down**. Reptile's forceball needs (−60, −72) world units (owner calibration; the MKT frame anchors alone left it too far and too low). No z shift (Quan Chi's −`0x1000` moved it toward the camera).
4. **Motion.** Facing-signed x velocity (controller `+0x700 == 0x10`: negative); donor `0x59999` → host `0x77776`.
5. **Animation.** `fighter_select_animation(1, slot)` then `animation_advance` each tick; the frame script holds each donor frame for its donor rate in host ticks (one host tick per MKT tick).
6. **Hit trigger.** Each tick, `0x8002BA04(record, 0)` with a KSEG0 strike record (current record also stored at `+0x638`). Box from MKT verbatim; reaction and blocked reaction by meaning. The box is `(x, y, w, h)` donor px with `x` the **front edge** and `w` reaching back toward the attacker (`0x8002BD58`: facing right, x − w .. x; facing left, −x .. −x + w; scaled 0.9; Static-confirmed, and the Shocker's v25 box (0, 0, 61, 120) lay behind Rayden in the owner's test). A box made by hand from a range check takes `x` = the range. A strike marked `unblockable` (a grab: MKT checks no block) sets bit `0x0002` of the record's `+0xC` flags, which the block test `0x80034888` reads as "cannot be blocked" (Rayden's Shocker, specials proof v27).
7. **Sound.** Donor samples in isolated host chains (`sound.install`), played by event: the hum at its donor cadence, the impact on contact.
8. **Ending.** On contact: stop, impact frames, then remove (`0x80024B00`), release the texture (`0x8001C424`) and `process_exit`. Otherwise `0x80035088(actor, 200)` ends it offscreen.

**Art and palette.** MKT frames as type-4 images with one 64-colour palette record: the forceball's flight palette `0x800BECE4` (indices 0–31) and impact palette `0x800BEBD0` (32–63). In MKT the ball is created by the throw animation (token 11 from frame `0x2FD4`, whose descriptor carries `0x800BECE4`) and keeps that palette in flight. Reptile's body palette is the wrong one (proofs v02–v03).

**Proof-only infrastructure** (not production allocations; [memory map](Memory-and-Allocation-Map#proof-only-allocations-generic-projectile-v01v06-2026-11-11)): the teleport proofs' v6 payload arena widened to 2 KiB, file `0x87` relocated and enlarged at ROM `0xF20000`, table-1 slots `0x0D`/`0x12`, samples at `0xF70000` in host chains 335/336, the lifted reaction in dummy reaction slot `0x2B`. Production placement goes through the fighter file and fixed loader (milestone 5).

### Special actions (milestone 4 step 3, 2026-11-11)

`fighter_import.lower_special` turns a move program into a host special in the slot of the Sub-Zero power it replaces.

- **Condition:** `emit_gate_condition` is the logic of Sektor's runtime-accepted missile conditions, made generic. It requires:
  - ground only, not grabbed, not busy;
  - no live class-`0x700` projectile and no special lock. With `alive=(labels)`, only the projectiles that set those words block it (`emit_process(alive=label)` sets its word while it lives). Reptile's fast and slow forceballs may then coexist (specials proof v11, Pending);
  - the replaced power's Ice cost;
  - the replaced power's tier, read at run time from its stock gate instruction (`GATES`), so the power-order shuffle still applies.
- **Action:** `emit_action` is entered through the Ice-root selector table (`0x8004AA4C`, selectors 3+). It runs the steps `begin` (`face=False`: the stock special start `0x80049F90` without its `face_opponent` call, specials proof v11), `animate` (a donor animation copied into a host secondary slot by `body.secondary_scripts`), `projectile`, `sleep`, `finish` and `end`. `stamp` (MKT cooldown) is not lowered yet.
- **Command:** `commands.lower(..., overrides)` points the command record at the new condition and the action thunk. A power with no command record (Ice Shatter, `commands.COMMANDLESS_POWERS`) can be taken only with such an override.
- **Body moves (specials proof v15, Reverse Elbow):**
  - New steps: `velocity` (donor speed converted, signed by the facing bit, `0x8002B1EC`), `stop`, `face`, `pose`, `next_frame`, `animate` with `until: manual`, `repeat` and `shake`.
  - `strike` is a hit window. Each tick it runs the step's `every_tick` steps, then the collision core with a KSEG0 strike record. A contact with the blocked flag `0x802ECD88` set takes `on_block`, any other contact takes `on_hit`. After the window it continues.
  - `end` stops a move that set a speed before it exits.
  - Records are placed by `emit_strike_data`. Reactions come from `STOCK_REACTIONS`, or from the builder for spare entries.
- **Footsteps (specials proof v17):** a manually advanced animation can carry the donor's footstep callback (MKT token 6, callback 8). `donor_footsteps` reads the frames it precedes, and `emit_action(footsteps=...)` plays host events there, alternating, while `next_frame` steps run.
- **Generic build (milestone 5, 2026-11-12):** `fighter_import.fighter_build` lowers every special of a described fighter from its move programs and the description's `specials` tuning, allocating selectors, reaction entries and sound chains from pools. `production` adds the relocatable-blob placement. Reptile's accepted specials come out byte-identical.
- **Timing:** MKT's logic runs at 60 ticks a second and the host's at 30 (`physics`). `emit_action(donor_ticks=2)` halves donor sleeps, windows, repeat counts and animation rates, and advances per-tick frames twice. The accepted forceballs keep `donor_ticks=1`. The owner halved Acid Spit's recovery by hand (v11), which agrees with the 2:1 ratio.
- **Projectile:** backend v1. `place_art(at=...)` can now write the art into the fighter file's free body tail, so the file keeps its stock size and place (Sektor proof v47's heap-neutral rule). `emit_process(prefix=...)` lets several projectiles share one payload.

First use: Reptile specials proofs v01–v03 (forceballs).

- **Acid Spit (specials proof v10):**
  - **Close-range checks:** extra strike records with the donor boxes, checked after each of the first frames before flight (`emit_process`).
  - **Impact at the opponent:** move to the opponent, flip, offset by the donor `adjust`. The flip mirrored Reptile's splash on the host (v10), so `Lowered.impact_flip` can drop it (v11). MKT's objects share the fighters' ground y, but a host projectile is raised by its offset, so the splash keeps the projectile's own y (`impact_keep_y`, v14). Taking the opponent's y drew it about 36 px below the hit. `impact.follow: "opponent"` (MKT's burst copies the opponent's velocity every tick, `0x800781F0`): the impact keeps its offset from the victim (path position, x, y, z) every tick (Rayden specials proof v17). A donor frame shared by the flight and the impact is drawn once per part (v17: Rayden's `0x2024`). Since Reptile specials proof v23, `impact_at_hit`, `impact_mirror` (with MKT's flip) and `impact_keep_y` are on by default for every "at opponent" impact (`fighter_build.impact_mirror`; Runtime-confirmed bounded: Rayden's lightning, Reptile's Acid Spit). `wrap: {cooldown}` (MKT's reversed-lightning flight callback `0x80078070`): the first time the projectile leaves the screen it is mirrored across the camera's vertical centre plane (`lower_projectile.emit_screen_mirror`), so it re-enters past the opposite edge; for `cooldown` ticks the flight keeps it, then it ends at its next exit (specials proof v20, Pending). Owner calibration `specials.<move>.projectile.impact_toward_px` moves the impact that many pixels toward the attacker (Rayden: 6, v18).
  - **Stumble reactions:** lifted at their place in the payload (`lift_stumble`).
  - **Virtual art entries:** the host has only four empty table-1 slots. Scripts are reached by cursor offset, and `projectile_actor_build` takes an index whose `0x104 + 4·index` word sits in the art (`fighter_select_animation` truncates the index to 16 bits, so it is not used there).
  - **Virtual body scripts:** `body.secondary_scripts` keys `0x40–0x7F`.
  - **Box on the drawn art (specials proof v13, Hypothesis until runtime-tested):**
    - The host collision core puts a strike box at the actor's y − `0xD8` world units. Box values are scaled ×0.9 and doubled, so 1 box unit is 1.8 world units, and y grows downward. The facing bit mirrors x (Static-confirmed, `0x8002CE24..0x8002D0E0`).
    - MKT's boxes assume MKT's own origin. Acid Spit's 12-unit box (y 27..39) sat above the drawn spit (92..97) and missed (v10, v12a/b).
    - `drawn_band` maps a part's looping frames to box space (anchor y + row, 2 world units per pixel). `centre_on_art` moves the strike box and the checks by one shift that centres the box on that band.
    - The forceball's accepted box overlaps its band and is not moved.
    - **Victim side (Static-confirmed, `0x8002CC88..0x8002CD2C`):**
      - The enemy's vertical extent is its current frame's rectangle, read from actor `+0x7C`: top = y − frame `+0xE`, bottom = top + frame `+0x6`, then + `0x6C` − actor `+0xD8` (`0x8003147C`, `0x800314AC`). Its x extent comes from frame `+0xC` (`0x800314F0`, `0x80031520`).
      - Any transparent rows inside that rectangle count, so an enemy can be hit above its visible head.
      - With strike-record `+0xC` bit 0 set (the stock records and ours), `0x8002E2C0` narrows the victim's x range by 3/16 of its width on each side (6/16 when its actor `+0x78` is 0). This only affects horizontal reach.
      - Owner, v13: an enemy on a lower floor was hit while the spit was drawn above his head. Pending: compare with a stock projectile at the same spot.
- **Throw helper:** MKT's token 11 creates a helper object from a frame, and tokens 12/14 step it, one helper frame per body frame. The frame after a helper step is the helper's, not a body pose. `lower_projectile.donor_helper` reads it, and `place_art(helper=...)` adds its frames and script. `emit_helper` is the process `emit_action(helper=...)` starts with the throw. It follows the owner's body (cursor in the throw script) rather than a clock; clocked versions drifted (specials proofs v03–v07). It goes at the launch through a handover (`emit_helper_handover`), because of the v04 crash: the forming ball and the flying ball were on screen together. The hypothesis was that two type-4 projectile objects must not coexist. Two stock projectiles coexist in Sektor's Double Missile (v46, Runtime-confirmed), so the cause is still open. Specials proof v11 lets two forceballs coexist (Pending). Reptile's forceball (the ball forming in his hands) is the first use, Pending (specials proof v08).

### Eye item

The Eye (item `0x03`) uses `0x80072584` (item-use table `0x800A6268`). The Inventory then starts the timer process `0x80072644` (class `0x100`).

- **Effect:**
  - player controller `+0x6BC |= 0x1000`: enemy AI routines check this bit and run `0x80005D74`, which idles them for 47–110 ticks;
  - actor colour `+0xFC/+0xFE/+0x100 = 32` (normal 128), so the fighter is drawn dark, and so is the attached actor `+0x650`;
  - actor flags `+0x8C |= 0x4000`, `+0x64 |= 0x2000`;
  - effect bits `0x800A5FA0 |= 1`, `0x802ECCC6 |= 1`.
- **End:**
  - after 1200 ticks the timer restores everything (colour back to 128);
  - stage start clears the bits;
  - the routine at `0x80053528` also clears the effect.

**Lowering (Reptile specials proof v18; v19 paid over time):** `emit_stealth_start` calls `0x80072584`, clears the request bit `0x802ECCC6` that the Inventory would turn into its own timer (`0x80073BD0..0x80073C04`), bumps a generation word and starts the timer process from `emit_stealth_timer`. From v19 that process takes `drain` Ice every `period` ticks (owner: stealth is paid over time) and undoes the effect, as the stock timer `0x80072644` does, when the meter cannot pay. It stops quietly when the generation is no longer its own or the stealth bit is already clear. If no process is free, the effect is undone at once rather than left without an end. Any victim reaction runs `0x80053520`, which ends the player's stealth (`0x80053594..0x800535F8`); this is stock Eye behaviour.

**Fit with Reptile.** MKT invisibility sets object flag `0x20`, and what that flag does is Pending. The MKMSZ equivalent is **stealth from enemy AI plus a dark tint**, not full invisibility. Lowering `stealth` = call `0x80072584` and start `0x80072644` exactly as the Inventory does. The duration is then the Eye's 1200 ticks; a different duration needs a copied timer.

## Owner review

Answers to the milestone 2 task 7 questions (owner, 2026-11-11):

1. **Component list:** accepted; it grows as later fighters need. A new component is added to this page and to `components.py` with a test, not through a plan amendment.
2. **Invisibility:** lowered to the Eye's stealth with the Eye's 1200-tick duration for now. Later idea (deferred, not decided): keep it on while it drains the mana meter instead of a fixed time.
3. **Generic projectile direction:** under discussion (alternatives and risks given to the owner).
4. **Quan Chi move:** confirmed. If it turns out unlike Reptile's, the Quan Chi code reference is dropped.
