# Fighter recompiler — move components

> **Scope:** milestone 2 of the [Fighter recompiler plan](Fighter-Recompiler-Plan) (progress: [status](Fighter-Recompiler-Status)). It is the **component catalogue**: the engine-neutral vocabulary that move programs are written in, with each component's meaning, parameters, units, ending and MKMSZ lowering. It also records the **host references** checked for reuse (MKMSZ Quan Chi's projectile, the Eye item). Donor readings stay in [MKT move readings](Fighter-Recompiler-MKT-Moves); the host action ABI stays in [Player actions and special moves](Player-Actions-and-Special-Moves).
>
> **Evidence:** catalogue and programs are Implementation/CI-confirmed (`fighter_import/components.py`, `tests/test_fighter_components.py`). Host references are Static-confirmed (clean MKMSZ USA Rev. 0, 2026-11-11). Lowerings marked *existing* reuse runtime-validated Sektor code; *planned* lowerings have no runtime evidence yet.
>
> **Status: draft for owner review** (milestone 2 task 7).

## Move programs

A move program is data (`src/mkmszr/fighters/moves/<fighter>.json`, format 1):

- **command:** `buttons` (mask), `tokens` (newest first, as facing right: `9` toward, `8` away, `7` down), `window` (ticks), `src`, and optional `conditions` (below);
- **steps:** a list of components with their parameters;
- **gaps:** what the vocabulary cannot yet express, each naming the move.

`components.validate_programs` checks every step against the catalogue and rejects unknown components, unknown or missing parameters, bad units, unknown reactions and missing provenance.

**Provenance (owner decision 2026-11-11).** Every parameter carries its source in the step's `src` map:

- `"MKT 0x…"`: the donor instruction or data word;
- `"host"` or `"host 0x…"`: an MKMSZ fact;
- `"owner"`: an owner decision.

**Units.**

| Unit | Meaning | Host conversion |
|---|---|---|
| ticks | donor process ticks (MKT runs at 60 Hz) | host runs at 30 Hz; the per-component rule is in the lowering column |
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
| `repeat` | Loop | `count`, `steps` | after `count` | backend loop |
| `animate` | Select a body animation | `anim`, `rate`, `until`: `phase_end` (play it out) / `running` (rate-gated, advanced by the host each tick) / `manual` (advanced by `next_frame`) | per `until` | *existing*: cursor + `animation_rate_init` / `animation_advance`; `phase_end` via `0x80031070` |
| `pose` | Show one frame | `anim` (with `offset`) | at once | *existing*: set cursor + advance |
| `next_frame` | Advance one step | — | at once | *existing*: `animation_advance` `0x800304C0` |
| `finish` | Play the current animation out | `rate` | phase end | native `0x80031070` |
| `face` / `flip` | Turn to the opponent / mirror | — | at once | *existing*: `face_opponent` `0x80031EF0`; flip *new* |
| `velocity` | Set motion along the facing | `x`, `y?` | at once | *existing*: actor `+0x14` (`0x8002B1EC`) after calibration |
| `stop` | Zero motion | — | at once | *existing*: `0x8002B1C0` |
| `jump` | Ballistic motion | `x`, `y`, `gravity`, `until`: `landing` / `below_screen` / `surface` | per `until` | *existing* (teleport): adapter-integrated arc |
| `shake` | Jitter in place | `dx`, `dy`, `count`, `ticks` | after `count` | *existing*: `0x80031208` offsets |
| `pass_through` | No fighter repulsion | `ticks` | after the time | **gap**: host equivalent of MKT `sans_repell_3` not located |
| `relocate` | Reappear by the opponent | `to`: `behind_opponent`, `dx`, `dy?` | at once | *existing* (teleport): copy target position + `0x80031208` + face |
| `sound` | Play a sound | `sound` | at once | *existing*: isolated host chain |
| `effect` | Start a shared effect | `effect`, `at?` | at once | *existing*: MKT-art effect process |
| `strike` | Body hit check over a window | `strike`, `ticks`, `skip?`, `every_tick?`, `only_if?` (`opponent_settled` / `rising`), `on_hit`, `on_block?` | after `ticks`, or on contact | *existing*: KSEG0 strike record + `0x8002BA04` (`host.strike`); reaction by meaning (below) |
| `projectile` | Spawn a projectile (the move continues) | `art`, `offset`, `speed`, `rate`, `strike`, `accel?`, `cap?`, `hum?`, `trail?`, `checks?`, `homing?`, `impact` | the move: at once; the projectile: on contact or offscreen | **planned generic projectile** ([below](#generic-projectile-lowering-planned)) |
| `stealth` | Enemies lose track of the fighter | `ticks` | after the time | native Eye effect ([below](#eye-item)) |
| `stamp` | Record "used now" for a cooldown | `key` | at once | *new*: a per-player tick word (allocation needed) |

**Victim reactions** (strike `reaction` / `blocked_reaction` are meanings; the backend maps each to a host reaction):

| Meaning | Donor | Host |
|---|---|---|
| `elbow_hold` | MKT `0x74`: grounded victim held about 20 ticks, airborne rejected | Pending |
| `launch` | MKT `0x24`: damaging launch, flight and landing | Pending |
| `knockback_arc` | MKT `0x71` (forceball): victim action `0x625`, thrown back on an arc (`do_jump(-0x2CCCC, -0x6CCCC, 0x5199)`) | Pending |
| `acid_stagger` | MKT `0x72` (acid): victim action `0x626`, staggers back; details Pending | Pending |
| `rocket_stumble` | MKT rocket reaction → `zap_stumble` | *existing* (Sektor rocket) |
| `uppercut` | teleport strike | host reaction `0x08` (*existing*) |
| `blocked`, `none` | stock blocked reaction / no reaction | — |

**Command conditions:** `buttons_held` (mask held exactly), `holding_away`, `cooldown` (`key`, `ticks`), `projectiles_below` (`count`) and `opponent_state` (donor guards whose meaning is still Pending, kept as text).

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
   - **Difference from Reptile's forceball:** Reptile's ball stops on contact and plays its impact frames, and his victim is thrown back on an arc (`knockback_arc`). These are behaviour, so they come from Reptile's program; only the host mechanics are reused.
   - **Sound:** `2` every 8 ticks.
   - **End:** `actor_offscreen` `0x80035088(actor, 200)`, then `actor_list_remove`, `dynamic_texture_release` and `process_exit`.

The same build-and-collide pattern is used by the armed grunts (`0x80043EB0`) and by 26 other enemy projectile sites. The player's own Ice child (`0x8004CC58`) uses the same `0x8004CF3C` dispatch with type 4, whose strike table is `0x800AF484`.

**Who a projectile can hit (Static-confirmed).** At `0x8002BB40` the collision core reads the attacking controller's class (`+0x6D8`). Class `1` (the player) and class `0x700` (player projectiles; Ice's child is started with that class by `0x8004CBC4`) take the enemy-victim scan at `0x8002CAE4`. Every other class, including Quan Chi's `0x800` child, takes the player-target path. A player projectile must therefore run as class `0x700`.

### Generic projectile lowering (planned)

From the reference above, the generic projectile can be built from native parts without patching the Ice root:

1. **Child process.** Started with `controller_clone_alloc(0x700, child)`: class `0x700`, as Ice uses, so that it hits enemies (Quan Chi's `0x800` would hit the player). The child code is generated by the backend from the `projectile` component.
2. **Build.** `projectile_build` with **type 4**, an imported secondary slot in file `0x87` that holds the MKT art, and its palette offset.
   - This needs one guarded data edit: `0x800A0324[4] = 0x80291C10`. That global is the player's file-`0x87` base pointer, stored when the file loads.
   - The table's only reader is `0x80046F74`, and the type-4 entry is 0 in stock (both test-checked).
3. **Motion, sound and lifetime.** Velocity from the component; `hum` and `trail` as above; `actor_offscreen` for the lifetime.
4. **Hit trigger.** `projectile_collision_dispatch` with a **new selector** whose record is added to the player strike table `0x800AF484`. Ice reaches strike records through the same table. Table capacity and selector choice are Pending.
5. **Impact.** Impact animation, sound and effect, then remove, release and exit.

Runtime proof is needed first (plan rules: guarded disposable proof, then bounded manual test).

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

**Fit with Reptile.** MKT invisibility sets object flag `0x20`, and what that flag does is Pending. The MKMSZ equivalent is **stealth from enemy AI plus a dark tint**, not full invisibility. Lowering `stealth` = call `0x80072584` and start `0x80072644` exactly as the Inventory does. The duration is then the Eye's 1200 ticks; a different duration needs a copied timer.

## Owner review

Answers to the milestone 2 task 7 questions (owner, 2026-11-11):

1. **Component list:** accepted; it grows as later fighters need. A new component is added to this page and to `components.py` with a test, not through a plan amendment.
2. **Invisibility:** lowered to the Eye's stealth with the Eye's 1200-tick duration for now. Later idea (deferred, not decided): keep it on while it drains the mana meter instead of a fixed time.
3. **Generic projectile direction:** under discussion (alternatives and risks given to the owner).
4. **Quan Chi move:** confirmed. If it turns out unlike Reptile's, the Quan Chi code reference is dropped.
