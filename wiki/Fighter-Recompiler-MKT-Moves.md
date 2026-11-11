# Fighter recompiler — MKT move readings

> **Scope:** milestone 3 of the [Fighter recompiler plan](Fighter-Recompiler-Plan) (progress: [status](Fighter-Recompiler-Status)). It owns the **reading aid** (how MKT special-move code is read), the **registry of MKT routines** it uses, and the **readings** of Reptile's and Sektor's specials. These are donor facts (MKT USA Rev. 2 N64); the engine-neutral meaning of each move goes to the component catalogue (milestone 2), and the MKMSZ side stays in [Player actions and special moves](Player-Actions-and-Special-Moves). Sektor's move code is frozen legacy; its detailed readings stay in [MKT adapter primitives](MKT-Adapter-Primitives).
>
> **Evidence:** everything here is **Static-confirmed** from clean MKT USA Rev. 2 (2026-11-10), unless marked Hypothesis or Pending. No runtime claims.

## Reading aid

Code: `src/mkmszr/fighter_import/mipsdis.py` (MIPS III decoder, no dependencies), `reading.py` (readings) and `mkt_registry.py` (registry). Tests: `tests/test_fighter_reading.py`.

```bash
python -m mkmszr.fighter_import.reading --mkt-rom MKT.z64 --fighter 19
```

```bash
python -m mkmszr.fighter_import.reading --mkt-rom MKT.z64 0x80079B68
```

What a reading does:

- **Extent.** From the entry to the `jr ra` (or tail `j`) after which no branch of the routine lands.
- **Constants.** Forward dataflow over the routine's control flow (delay slots and branch-likely forms included; registers meet by intersection at merges). Constant `a0..a3` are shown at every call, and constant-address loads and stores are named.
- **Names.** Calls and globals are named from the registry. Every call the registry does not name is printed as `UNKNOWN`. Nothing is named by guess.
- **Dispatchers.** A constant `a0` passed to an engine dispatcher is resolved to the routine it reaches:
  - `do_special` `0x80076F70` → table `0x800AB140` (56 entries, `context_jump`);
  - `do_body_propell` `0x80045050` → table `0x800A80D0` (40 entries, `context_jump`);
  - `do_quick_special` `0x80072020` → table `0x800AAF00` (32 entries, called, then `reaction_exit`).
- **Child code.** Routine addresses that a routine passes as arguments or stores (child processes, flight callbacks) are followed like calls.
- **Fighter view.** `fighter_moves(mkt, id)` reads every command in the fighter's event handlers ([command format](MKT-Adapter-Primitives#special-move-command-translation)). Commands whose action is shared by more than half the roster (finishers and similar) are listed but not read.
- **Stops.** A reading stops at registry routines of kind `engine`; it follows `move` routines (a fighter's own bodies) and anything unnamed, down to depth 6.

**Done-criterion check (2026-11-10):** every Reptile command reads with **no unknown call** (38 routines), and every Sektor command reads with no unknown call at the move-body level (test-enforced, ROM-backed).

## Registry

`mkt_registry.REGISTRY` maps an address to a name, arguments, effect, evidence and kind (`engine`, `move` or `global`). It includes the names already established in [MKT adapter primitives](MKT-Adapter-Primitives) and adds the ones below, all read in this task.

| Address | Name | Arguments → effect |
|---|---|---|
| `0x8000D1A4` | `skip_frame` | animation cursor (process `+0x41C`) past the next zero word |
| `0x8000D244` | `find_last_frame` | cursor to the last frame of the current part |
| `0x8000D9CC` | `animate_table1` | `(ticks, slot)`: `get_char_ani(1, slot)`, then `mframew(ticks)` |
| `0x8000DA0C` | `ani_frame_at_t0` | `(offset, slot)`: `get_char_ani(0, slot)`, skip `offset` words, show that frame |
| `0x8000DAC4` | `ani_frame_at` | the same with table 1 |
| `0x8000E374` | `flip_single` | toggle object facing (`+0x50 ^ 0x10`) and rebind the frame |
| `0x8003DB80` | `player_word_store` | `(object, value)` → `0x80169984` (player 1) or `0x80169C58` (player 2); meaning **Pending** |
| `0x8003E0F8` | `holding_side` | `proc_word_test(process, 0x8000` if the opponent is to the right, else `0x2000)`; **Hypothesis:** "holding away from the opponent" |
| `0x8003E13C` | `proc_word_test` | `0x8000` when the halfword at `*(process +0x3B8)` has a mask bit |
| `0x8003E2A0` | `strike_box_check` | `(object, strike, x, y, w, h)`: strike check with an explicit box; details **Pending** |
| `0x8004A444` | `slide_recover` | stand-up frames, then `stamp_tick(0x80156A48)` and `reaction_exit` |
| `0x8004EA64` | `buttons_held` | `(object, mask_p1, mask_p2)`: `0x8000` when held buttons `& 0xFC` equal the mask |
| `0x8004EB28` | `held_buttons` | held buttons of the object's player (`0x8014C374` / `0x8014C376`) |
| `0x8004FDDC` | `command_transfer` | `(mode, action)`: start a matched command |
| `0x800504A0` | `init_special_face` | `stop_me`, `face_opponent`, object flags `|= 4`, then special-start steps |
| `0x8005A69C` | `process_suicide` | end the current process (inference: control never returns) |
| `0x8006CDCC` | `opponent_unsettled` | `0x8000` while the opponent has y velocity or is off its ground line |
| `0x8006CF48` | `wait_opponent` | sleep while opponent action ≠ `0x610` and `opponent_unsettled` |
| `0x8006D010` / `0x8006D7E0` | `stamp_tick` / `ticks_since` | per-player time stamps on `0x8012C6A4`; never stamped reads as `0x780` |
| `0x8006D228` | `opponent_to_right` | own x < opponent x |
| `0x8006D674` | `shake_object` | `(object, dx, dy, count, ticks)` |
| `0x8006D9E8` | `match_me_to_opponent` | `match_ani_points(opponent, self)` |
| `0x8007EEB4` | `begin_special` | `(mode, action, flip, object)`: mode 0 `init_special_face`; 1 sets action then `init_special`; 2 `init_special`; `flip == 1` → `flip_single` |
| `0x8007F27C` | `proj_set_xvel` | `(object, speed, ticks)`: facing-aware x velocity and animation rate |
| `0x8007F5C0` | `opponent16_proc_check` | fighter-16-specific check; meaning **Pending** |
| `0x8007F75C` | `proj_delete` | release the projectile object and palette, end the process |
| `0x8007F7A8` | `proj_set_strike` | process `+0x3B8` = strike table `0x800AFDB0[fighter][index]` |

Globals: `0x8014C31C` current process (`+0x418` object, `+0x3BC` opponent object, `+0x3C0` opponent process, `+0x3F6` action); `0x8012C6A4` tick counter (inference); `0x8016994C` / `0x80169BF4` player-1 / player-2 objects (inference); `0x8014C3B8` strike flag (meaning Pending).

**Strike record** (`0x10` bytes, from `strike_box_check` and the [elbow-dash records](MKT-Adapter-Primitives#strike-and-reaction-translation)): box `x, y, w, h` (4 × u16); u16 reactions (high byte = victim reaction, table `0x800A8AE0`; low byte = blocked reaction, table `0x800A8D28`); u16 damage (high byte = damage, low byte = block damage); u16 `1`; u16 `0`.

## Reptile (MKT fighter 19)

Commands. Masks are button bits; tokens are newest first and as facing right. `0x40` is Low Kick (cross-checked); the other button names are lineage **Hypothesis**: `0x80` LP, `0x10` HP, `0x20` HK, `0x08` Block. Token `9` = toward, `8` = away, `7` = Down; `6` = Up is **Hypothesis**.

| Command (event, mask, tokens) | Condition | Action → body | Move |
|---|---|---|---|
| 0/1, `0x90` (LP+HP), `9,9` (F,F) | `forceball_fast_ok` | `0x8004F9A4` → special `0x28` → `0x80079A5C` | forceball, speed `0x59999` |
| 0/1, `0x90`, `8,8` (B,B) | `forceball_slow_ok` | `0x8004F8E4` → special `0x22` → `0x80079AB4` | forceball, speed `0x26666` |
| 0, `0x10` (HP), `9,9` (F,F), window `0x12` | none | `0x8004F904` → special `0x23` → `0x80079800` | acid spit |
| 3, `0x20` (HK), `7,6` | none | `0x8004EC20` → quick `0x1B` → `0x80073918` | invisibility |
| 1/2/4, `0xC8` (LP+LK+Block chord), no tokens | `slide_ok` | `0x8004F260` → propell `0x15` → `0x8004A294` | slide (shared with fighter 21) |
| 4, `0x40` (LK), `9,8` (B,F) | none | `0x8004F2C0` → propell `0x17` → `0x800467D0` | elbow dash ([reading](MKT-Adapter-Primitives#reverse-elbow-donor-command-and-historical-proof-selection)) |

Shared roster-wide records (finishers etc.): actions `0x8001A148`, `0x8001A1A0`, `0x80015C00`, `0x80028ED8`, `0x8002701C`, `0x80052044`, `0x8004EC80`; not read.

Units below are raw donor values. Velocities are 16.16 fixed point per process tick (as in the rocket calibration); ticks are process ticks.

### Forceballs

- **Body** (`0x80079A5C` fast / `0x80079AB4` slow; they differ only in speed and stamp):
  1. `stamp_tick(stamp, self)`; stamps `0x80156BA0` (fast) and `0x80156B58` (slow), one u16 per player.
  2. `begin_special(1, action 0x22, 0, self)`.
  3. `forceball_launch(speed)`.
- **`forceball_launch`** `0x80079B0C`:
  1. `animate_table1(3, 5)`: throw pose, table 1 slot 5, 3 ticks per frame.
  2. `proj_process(forceball_proc)`; the child's `+0x440` = speed.
  3. Sleep 8, `mframew(4)`, `reaction_exit`.
- **`forceball_proc`** `0x80079B68`:
  1. `get_char_ani(1, 5)`, `find_part(3)`: the ball frames are part 3 of slot 5.
  2. `proj_set_xvel(self, speed, 3)`.
  3. Flight callback `forceball_hum` (`ft_sound(0x12)` every 3 ticks).
  4. `proj_flight(self, strike 0x11)`.
  5. On return: velocity zeroed, `ft_sound(5)`, part 4 of slot 5 (impact) at 3 ticks per frame, `proj_delete`.
- **Strike `0x11`** (`0x800B03CC`): box `(99, 44, 47, 61)`, reaction `0x71` / blocked `0x01`, damage 18 / block 2.
- **The ball object and its palette (2026-11-11).**
  - The throw animation (table 1 slot 5, part 1) creates the ball: script token 11 builds a helper object from frame `0x2FD4`, whose descriptor carries palette `0x800BECE4`. The later part-1 frames (`0x3000`, `0x3028`, `0x3050`) show it growing in the hand.
  - `proj_process` hands the parent's `+0x440` object to the child (`+0x418`), and the flight frames (part 3) carry no palette of their own, so the ball flies with `0x800BECE4`. Part 4 rebinds the impact palette `0x800BEBD0` (token 13).
  - Evidence: Static-confirmed from the script, plus an MKT save state (palette table `0x8015DA78` holds both palettes; the ball object `0x8014C3F0` is in its impact frames at Reptile's height). Owner-confirmed by eye in projectile proofs v04–v06.
- **Victim arc (reaction `0x71`):** `do_jump(-0x2CCCC, -0x6CCCC, 0x5199)`, whose x goes through `0x8006EBB0` (sign chosen by `opponent_to_right`). The victim is launched **toward Reptile**. The owner compared both directions at runtime (proofs v02/v03); the static sign reading had suggested "away" and was wrong.
- **Condition `forceball_cooldown`** `0x8005281C`. It fails (`0x4000`) in any of these cases:
  - fewer than 96 ticks since this variant's stamp;
  - the opponent object's fighter id (`+0x38`) is `0x1F`;
  - opponent process `+0x408 >= 4`.

  Otherwise it returns `buttons_held(0x90, 0x90)`.

### Acid spit

- **Body** `0x80079800`:
  1. `begin_special(1, action 0x23, 0, self)`, `ft_sound(8)`.
  2. `animate_table1(3, 6)`.
  3. `proj_process(acid_proc)`.
  4. Action `0x604`, sleep `0x1F`, `mframew(4)`, `reaction_exit`.
- **`acid_proc`** `0x80079880`:
  1. `proj_set_strike(0x12)`, `get_char_ani(1, 6)`, `find_part(3)`.
  2. Two **arc steps** (`acid_arc_step`). Each step: next frame, sleep 2, `strike_box_check(self, 0x12, x, 0x17, 0x29, 0x0A)`, first with x = `0x4B`, then with x = `0x78`. On contact it goes to `acid_impact`, unless `opponent16_proc_check` passes.
  3. Then `proj_set_xvel(self, 0x66666, 3)`, no callback, `proj_flight(self, 0x12)` and `acid_impact`.
- **`acid_impact`** `0x80079920`:
  1. Stop, action `0x500`, `get_char_ani(1, 7)`.
  2. `create_fx(0x2F)`.
  3. `match_me_to_opponent`, `flip_single`, `multi_adjust_xy(self, -153, 0)`.
  4. Slot 6 part 4 at 3 ticks per frame, then `proj_delete`.
- **Art and palette (2026-11-11, Static-confirmed):**
  - Slot 6 holds the whole move: part 1 is the throw, whose token 11 creates the mouth helper `0x315C` with pose 4; part 2 is the retract; part 3 is the flight (`315C`, `3188` for the two arc steps, then the loop `31B0 31C4`); part 4 is the splash, 8 frames, anchors x −83…−142.
  - Slot 7 holds bare object descriptors (9×9 droplets, palette `0x800BEC14`): `create_fx(0x2F)`'s art, not the splash. The move program's impact had slot 7 and is corrected to slot 6 part 4, with the `adjust` (−153, 0) and the sizzle (the attacker's fighter sound `0x10`, played by reaction `0x72`).
  - The helper `0x315C` binds palette `0x800BEC14`: acid's palette, as `0x800BECE4` is the forceball's.
- **Reaction `0x72`** (`0x800547C8`):
  - victim action `0x626`;
  - plays the attacker's fighter sound `0x10` (`0x80005810`);
  - calls `0x80057538(0, 0x80057790, 0, 0)` (a per-tick victim effect, Pending);
  - sleeps 2, sets `+0x420 = 0x26666`, then `0x80057F94`. `0x80057F94` is the same stumble tail as `zap_stumble` (Sektor's rocket, push `0x33333`).
- **Strike `0x12`** (`0x800B03EC`): box `(193, 27, 64, 12)`, reaction `0x72` / blocked `0x01`, damage 15 / block 4.

### Invisibility

**Body** `0x80073918`, called by `do_quick_special(0x1B)`:

1. Action `0x30C`, `init_special`, `animate_table1(2, 1)`.
2. `create_fx(0x1E)`, `ft_sound(9)`.
3. Sleep 10.
4. Object flags (`+0x24`): clear `0x10`, set `0x20`.
5. `reaction_exit`.

The routine only sets the flag. What flag `0x20` does while set (drawing, AI, how Reptile reappears) is read elsewhere and is **Pending** (next step of task 3 / the Eye comparison in milestone 2).

### Slide

**Body** `0x8004A294` (propell `0x15`; fighters 19 and 21):

1. Action `0x210`, `init_special`.
2. `towards_x_vel(0x66666)`; fighter 21 uses `0x8CCCC`.
3. `get_char_ani(1, 2)` at 4 ticks per frame, `ft_sound(6)`.
4. A 28-tick loop (sleep 1, `next_anirate`). The first 8 ticks have no strike check; each of the remaining 20 runs `strike_check_a0` with per-fighter strike-table entry `0x10`.
5. **On contact** with `strike_flag` clear:
   - `ani_frame_at(2, 2)`;
   - `player_word_store(self, xvel / 2)`;
   - sleep 3, `stop_me`, `wait_opponent`, `slide_recover`.
6. **At the end of the loop**, or on contact with `strike_flag` set (meaning Pending): `stop_me`, object flags clear `0x08` and set `0x04`, action `0x613`, sleep 22, `slide_recover`.

**Condition** `slide_ok`: `holding_side` (Hypothesis: away), then `buttons_held(0xC8, 0xC8)`.

`slide_recover` stamps `0x80156A48`; no slide condition reads it (reader **Pending**).

### Elbow dash

Already read in [MKT adapter primitives](MKT-Adapter-Primitives#reverse-elbow-donor-command-and-historical-proof-selection) (`prop_do_reptile_dash` `0x800467D0`, strikes `0x15`/`0x16`). This task adds:

- the recovery `dash_recover` `0x80047118`:
  1. action `0x61F`, `stop_me`;
  2. run frame `ani_frame_at_t0(3, 0x4A)`;
  3. `shake_object(self, 4, 0, 4, 3)`;
  4. `reaction_exit`;
- `opponent_unsettled`, used while the dash waits on the victim.

### What this changes in the owner's expectations

These are static donor facts. The host-side comparisons (MKMSZ Quan Chi forceball, Eye item) are milestone 2 task 5.

- **Acid spit** is a normal projectile with one addition: two close-range box checks during the spit animation before flight.
- **Forceballs:**
  - one routine with two speeds;
  - a per-variant 96-tick cooldown;
  - a looping flight sound;
  - impact frames from the same animation slot.

  Reusing MKMSZ Quan Chi's forceball as a **code/gameplay reference** fits. The art and sounds come from MKT (owner, 2026-11-10).
- **Invisibility** is a flag set by a short body. The behaviour lives in the flag's readers, so the Eye comparison needs those readers first.
- **Slide:** the shared ninja slide. Sub-Zero's native slide is the host match.
- **Elbow dash:** the only move with no host counterpart, as expected.

## Sektor (MKT fighter 7)

Commands: straight rocket (`do_robo_zap` `0x8007BF84`), double rocket (`0x8007BFC8`), homing rocket (`do_robo_zap2` `0x8007BF38`) and teleport (`command_transfer(1, …)` → propell 8 → `0x80048368`). All read with no unknown calls at the move-body level. Their detailed readings, translations and runtime history are in [MKT adapter primitives](MKT-Adapter-Primitives) (rocket and teleport sections) and stay frozen legacy.

## Provenance convention

**Accepted by the owner (2026-11-11).** Every value in a move program carries the donor address it was read from (`"MKT 0x800799B0"`); a value with no donor origin carries `"host"` (`"host 0x…"`) or `"owner"`. The program validator rejects a value with no source ([components](Fighter-Recompiler-Components#move-programs)).
