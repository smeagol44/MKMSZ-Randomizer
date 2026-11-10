"""Registry of MKT (N64 USA Rev. 2) engine routines, move routines and globals.

Used by :mod:`.reading` to annotate donor code (Fighter recompiler plan, milestone 3). Each entry
gives a name (the MKT arcade-source name where the Wiki already established it, otherwise a
descriptive name), the arguments, the effect and the evidence. Evidence is Static-confirmed unless
it says "inference". ``kind`` is ``engine`` (shared routine: a reading stops there), ``move`` (a
fighter's move body: readings follow into it) or ``global`` (a data address).

The Wiki page ``Fighter-Recompiler-MKT-Moves`` documents the readings that use it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MktRoutine:
    name: str
    args: str = ""
    effect: str = ""
    evidence: str = ""
    kind: str = "engine"

    @property
    def follow(self) -> bool:
        return self.kind == "move"


_W = "Wiki MKT-Adapter-Primitives"
_M = "Wiki Fighter-Recompiler-MKT-Moves (static reading)"


def _e(name: str, args: str = "", effect: str = "", evidence: str = _W) -> MktRoutine:
    return MktRoutine(name, args, effect, evidence, "engine")


def _m(name: str, effect: str, evidence: str = _M) -> MktRoutine:
    return MktRoutine(name, "", effect, evidence, "move")


def _g(name: str, effect: str, evidence: str = _M) -> MktRoutine:
    return MktRoutine(name, "", effect, evidence, "global")


REGISTRY: dict[int, MktRoutine] = {
    # -- sound ------------------------------------------------------------------------------
    0x8000518C: _e(
        "run_footstep_sound", "", "random one of four sounds from group table 0x800A1A3C"
    ),
    0x800052CC: _e("random_group_sound", "", "random sound from a two-entry group"),
    0x800054A8: _e("triple_sound", "a0 = entry", "sound from table 0x800A1AA8 with position pan"),
    0x80005760: _e("ft_sound", "a0 = entry", "per-fighter sound: table 0x800A1ED4[fighter][entry]"),
    # -- animation --------------------------------------------------------------------------
    0x8000D1A4: _e(
        "skip_frame", "", "advance the animation cursor (+0x41C) past the next zero word", _M
    ),
    0x8000D1F4: _e(
        "find_part", "a0 = part n", "move the animation cursor to part n of the current animation"
    ),
    0x8000D244: _e(
        "find_last_frame", "", "move the animation cursor to the last frame of the current part", _M
    ),
    0x8000D2A4: _e("frame_bind", "", "bind a frame to an object"),
    0x8000D408: _e(
        "do_next_a9_frame", "", "advance the current object's animation script one step"
    ),
    0x8000D9CC: _e(
        "animate_table1", "a0 = ticks, a1 = slot", "get_char_ani(1, slot) then mframew(ticks)", _M
    ),
    0x8000DA0C: _e(
        "ani_frame_at_t0",
        "a0 = word offset, a1 = slot",
        "get_char_ani(0, slot), skip a0 words of the script, show that frame",
        _M,
    ),
    0x8000DAC4: _e(
        "ani_frame_at",
        "a0 = word offset, a1 = slot",
        "get_char_ani(1, slot), skip a0 words of the script, show that frame",
        _M,
    ),
    0x8000DB98: _e(
        "mframew", "a0 = ticks", "advance the animation each a0 ticks until the phase ends"
    ),
    0x8000DD3C: _e(
        "multi_adjust_xy", "a0 = object, a1 = dx, a2 = dy", "facing-aware position offset"
    ),
    0x8000DD94: _e("match_ani_points", "a0 = from, a1 = to", "copy position and facing"),
    0x8000E13C: _e("init_anirate", "a0 = ticks per frame", "set the animation rate"),
    0x8000E184: _e("next_anirate", "", "rate-gated animation advance"),
    0x8000E374: _e(
        "flip_single",
        "a0 = object",
        "toggle the facing bit (+0x50 ^ 0x10) and rebind the frame",
        _M,
    ),
    0x8000F910: _e(
        "get_char_ani", "a0 = table, a1 = slot", "select an animation of the current fighter"
    ),
    0x80081C4C: _e(
        "image_decode", "", "image codec dispatcher", "Wiki MKT-Fighter-Asset-Translation"
    ),
    # -- effects ----------------------------------------------------------------------------
    0x8002A820: _e("create_fx", "a0 = effect index", "start a shared effect (table 0x800A5590)"),
    0x8002E448: _e("rocket_puff", "", "rocket smoke puff effect"),
    0x8002EA38: _e("dave_explode", "", "explosion effect"),
    # -- movement, strikes, control -----------------------------------------------------------
    0x8003DB54: _e("stop_me", "a0 = object", "zero velocity"),
    0x8003DB80: _e(
        "player_word_store",
        "a0 = object, a1 = value",
        "write a1 to 0x80169984 (player-1 object) or 0x80169C58 (player-2 object); meaning Pending",
        _M,
    ),
    0x8003E0F8: _e(
        "holding_side",
        "a0 = process",
        "proc_word_test(a0, 0x8000 if the opponent is to the right else 0x2000); Hypothesis: "
        "holding away from the opponent (the slide is documented as Back + LP+LK+BL)",
        _M,
    ),
    0x8003E13C: _e(
        "proc_word_test",
        "a0 = process, a1 = mask",
        "0x8000 when the halfword at *(process +0x3B8) & mask, else 0x4000",
        _M,
    ),
    0x8003E2A0: _e(
        "strike_box_check",
        "a0 = object, a1 = strike index, a2 = x, a3 = y, stack = w, h",
        "strike check with an explicit box (x/y facing-aware); 0x8000 on contact; strike table "
        "0x800AFDB0[fighter][a1]; details Pending",
        _M,
    ),
    0x8003E620: _e("strike_check_a0", "a0 = strike", "fighter strike check against the opponent"),
    0x80045050: _e(
        "do_body_propell",
        "a0 = propell selector",
        "context_jump to table 0x800A80D0[a0] (40 entries)",
    ),
    0x80047118: _e(
        "dash_recover",
        "a0 = object",
        "dash_stop, ani_frame_at_t0(3, 0x4A), shake_object(object, 4, 0, 4, 3), reaction_exit",
        _M,
    ),
    0x8004716C: _e("dash_stop", "", "action +0x3F6 = 0x61F, object flags |= 4, stop_me", _M),
    0x80048564: _e("teleport_flight_callback", "", "flight callback: strike check while rising"),
    0x8004859C: _e(
        "teleport_strike_check", "", "action 0x622, fighter strike through strike_check_a0"
    ),
    0x80048368: _m("prop_robo_teleport", "robot teleport uppercut body (propell 8)", _W),
    0x8004BEB0: _e("command_table_parser", "a0 = record table", "match 0x2C records and dispatch"),
    0x8004BFD4: _e("inline_matcher", "a0 = mask, a1 = mask, a2 = table", "compact sequence check"),
    0x8004C13C: _e("reaction_exit", "", "end the action, back to the fighter's normal control"),
    0x8004A444: _e(
        "slide_recover",
        "a0 = object",
        "ani_frame_at(1, 2), sleep 4, ani_frame_at(0, 2), sleep 4, stamp_tick(0x80156A48), reaction_exit",
        _M,
    ),
    0x8004EA64: _e(
        "buttons_held",
        "a0 = object, a1 = player-1 mask, a2 = player-2 mask",
        "0x8000 when the object's held buttons & 0xFC equal the mask, else 0x4000",
        _M,
    ),
    0x8004EB28: _e(
        "held_buttons",
        "a0 = object",
        "held buttons & 0xFC of the object's player (0x8014C374/76)",
        _M,
    ),
    0x8004FDDC: _e(
        "command_transfer",
        "a0 = mode, a1 = action",
        "start a matched command (see command_table_parser)",
        _M,
    ),
    0x80050420: _e("init_special", "a0 = object", "special-move start"),
    0x800504A0: _e(
        "init_special_face",
        "a0 = object",
        "stop_me, face_opponent, object flags |= 4, then the init_special steps",
        _M,
    ),
    0x8005A88C: _e("process_sleep", "a0 = ticks", "sleep the current process"),
    0x8005A69C: _e(
        "process_suicide", "", "end the current process (inference: control never returns)", _M
    ),
    0x8006C7FC: _e("sans_repell_3", "", "three-tick no-repel"),
    0x8006C9C0: _e("rough_distance", "", "approximate distance max + min/2"),
    0x8006D010: _e(
        "stamp_tick",
        "a0 = per-player pair, a1 = object",
        "store the tick counter 0x8012C6A4 in the caller's player slot (+0x30 == 1: first)",
        _M,
    ),
    0x8006CF48: _e(
        "wait_opponent",
        "",
        "sleep 1 per tick while opponent action != 0x610 and 0x8006CDCC returns 0x8000",
        _M,
    ),
    0x8006CDCC: _e(
        "opponent_unsettled",
        "",
        "0x8000 when the opponent's y velocity != 0 or its y != opponent process +0x3F8, else 0x4000",
        _M,
    ),
    0x8006C3B0: _e(
        "reset_fighter_state",
        "",
        "clear process action fields (+0x3F6, +0x3FE, +0x402..+0x408) and object flags; create_fx 0xD "
        "when +0x408 >= 2; field meanings Pending",
        _M,
    ),
    0x8006CD44: _e("proc_flag1", "", "0x8000 when current process +0x3FA & 1, else 0x4000", _M),
    0x8006D1CC: _e("face_opponent", "", "turn to face the opponent"),
    0x8006D228: _e(
        "opponent_to_right", "a0 = process", "0x8000 when own x < the opponent's x, else 0x4000", _M
    ),
    0x8006D674: _e(
        "shake_object",
        "a0 = object, a1 = dx, a2 = dy, a3 = count, stack = ticks",
        "count times: offset by (dx, dy), sleep, offset back, sleep",
        _M,
    ),
    0x8006D7E0: _e(
        "ticks_since",
        "a0 = per-player pair, a1 = object",
        "tick counter minus the player's stamp; 0x780 if never stamped",
        _M,
    ),
    0x8006D9E8: _e(
        "match_me_to_opponent",
        "",
        "match_ani_points(opponent object +0x3BC, own object +0x418)",
        _M,
    ),
    0x8006EC00: _e(
        "towards_x_vel", "a0 = process, a1 = object, a2 = speed", "set x velocity toward the facing"
    ),
    0x8006EC50: _e("do_jump", "a0 = object, a1 = x vel, a2 = y vel, a3 = gravity", "standard jump"),
    0x80070A08: _e("fighter_repel_proc", "", "central fighter-repel process"),
    0x80072020: _e(
        "do_quick_special",
        "a0 = index",
        "call table 0x800AAF00[a0] (32 entries) as a subroutine, then reaction_exit",
        _M,
    ),
    0x80076E48: _e(
        "teleport_land", "", "landing: action 0x304, triple_sound(0x18), get_char_ani(0, 0x16)"
    ),
    0x80076F30: _e("land_reset", "", "0x8003DA3C(object, 0x800A7DCC) then reset_fighter_state", _M),
    0x80076F70: _e(
        "do_special", "a0 = special id", "context_jump to special table 0x800AB140[id] (56 entries)"
    ),
    0x80080A84: _e("context_jump", "", "switch the running process context"),
    0x8007EEB4: _e(
        "begin_special",
        "a0 = mode, a1 = action, a2 = flip, a3 = object",
        "mode 0: init_special_face; 1: action +0x3F6 = a1 then init_special; 2: init_special; "
        "a2 == 1: flip_single",
        _M,
    ),
    # -- projectiles --------------------------------------------------------------------------
    0x8007F014: _e(
        "proj_process",
        "a0 = child routine",
        "create a projectile process (owner/opponent context, object at +0x418)",
    ),
    0x8007F27C: _e(
        "proj_set_xvel",
        "a0 = object, a1 = speed, a2 = ticks per frame",
        "facing-aware x velocity (negated when +0x50 & 0x10) and init_anirate(a2)",
        _M,
    ),
    0x8007F2C8: _e(
        "proj_flight", "a0 = object, a1 = strike index", "projectile flight loop with strike checks"
    ),
    0x8007F5C0: _e(
        "opponent16_proc_check",
        "",
        "0x8000 when the opponent is fighter 16 and a process with id 0x11F owns the opponent object; "
        "meaning Pending",
        _M,
    ),
    0x8007F75C: _e(
        "proj_delete",
        "a0 = object",
        "release the projectile object and its palette, then process_suicide",
        _M,
    ),
    0x8007F7A8: _e(
        "proj_set_strike",
        "a0 = strike index",
        "process +0x3B8 = per-fighter strike table 0x800AFDB0[fighter][a0]",
        _M,
    ),
    0x8007F7EC: _e(
        "proj_object", "", "create the projectile object and match_ani_points to the owner"
    ),
    0x8007F860: _e("proj_recover", "", "attacker recovery after a projectile"),
    # -- Sektor (frozen legacy; readings in MKT-Adapter-Primitives) -----------------------------
    0x80057B08: _e("r_rocket", "", "rocket reaction (victim)"),
    0x80057BEC: _e("zap_stumble", "", "stumble reaction"),
    0x8007BF38: _m("do_robo_zap2", "Sektor homing rocket action", _W),
    0x8007BF84: _m("do_robo_zap", "Sektor straight rocket action", _W),
    0x8007BFC8: _m("do_robo_zap_double", "Sektor double rocket action (rzap3 mode 1)", _W),
    0x8007C00C: _e("make_rocket", "", "create the rocket projectile"),
    0x8007C068: _e(
        "rzap3", "a0 = child proc, a1 = mode", "rocket action: open, create, recover, close"
    ),
    0x8007C100: _e("rocket1_proc", "", "straight rocket process"),
    0x8007C25C: _e("rocket2_proc", "", "homing rocket process"),
    0x8007C4AC: _e("rocket_hunt", "", "homing steering"),
    0x8007C7C8: _e("rocket_smoke", "", "smoke trail cadence"),
    0x8007CA34: _e("point_rocket", "", "rocket direction animation from velocity"),
    0x8007CE70: _e("robo_chest_open", "", "special start + chest open"),
    0x8007CECC: _e("robo_chest_close", "", "chest close"),
    # -- Reptile (fighter 19) -----------------------------------------------------------------
    0x8004A294: _m("do_slide", "ninja slide body (propell 0x15)"),
    0x800467D0: _m("prop_do_reptile_dash", "Reptile elbow dash body (propell 0x17)", _W),
    0x80046910: _e("reptile_dash_hit", "", "elbow dash strike handling"),
    0x800546A0: _e("r_reptile_dash", "", "victim reaction 0x74"),
    0x80055838: _e("r_jax_dash", "", "victim reaction 0x24"),
    0x80073918: _m("reptile_invisibility", "Reptile invisibility body (quick special 0x1B)"),
    0x80079800: _m("reptile_acid_spit", "Reptile acid spit body (special 0x23)"),
    0x80079880: _m("acid_proc", "acid spit projectile process"),
    0x800799C8: _m("acid_arc_step", "acid spit arc: one animation step, sleep 2, strike box check"),
    0x80079920: _m("acid_impact", "acid spit impact on the opponent"),
    0x80079A5C: _m("reptile_forceball_fast", "Reptile forceball, speed 0x59999 (special 0x28)"),
    0x80079AB4: _m("reptile_forceball_slow", "Reptile forceball, speed 0x26666 (special 0x22)"),
    0x80079B0C: _m("forceball_launch", "forceball throw: animation, projectile process, recovery"),
    0x80079B68: _m("forceball_proc", "forceball projectile process"),
    0x80079C30: _m("forceball_hum", "forceball flight callback: ft_sound 0x12 every 3 ticks"),
    0x800527D4: _m("forceball_fast_ok", "condition: forceball_cooldown(0x80156BA0)"),
    0x800527F8: _m("forceball_slow_ok", "condition: forceball_cooldown(0x80156B58)"),
    0x8005281C: _e(
        "forceball_cooldown",
        "a0 = per-player pair",
        "fails (0x4000) within 96 ticks of the last stamp or by opponent state; see the Wiki",
        _M,
    ),
    0x80052938: _m("slide_ok", "condition: 0x8003E0F8(current_proc) then buttons_held(0xC8, 0xC8)"),
    0x80052908: _e("forceball_buttons", "", "buttons_held(0x90, 0x90)", _M),
    0x80052978: _e("slide_buttons", "", "buttons_held(0xC8, 0xC8)", _M),
    0x80156A48: _g("slide_stamp", "per-player u16 pair: tick of the last slide"),
    # -- globals ------------------------------------------------------------------------------
    0x8014C31C: _g(
        "current_proc",
        "pointer to the running process (+0x418 object, +0x3BC opponent object, "
        "+0x3C0 opponent process, +0x3F6 action)",
    ),
    0x8012C6A4: _g(
        "tick_counter", "u16 time base for stamp_tick / ticks_since (inference: game tick)"
    ),
    0x80156BA0: _g("forceball_fast_stamp", "per-player u16 pair: tick of the last fast forceball"),
    0x80156B58: _g("forceball_slow_stamp", "per-player u16 pair: tick of the last slow forceball"),
    0x8016994C: _g(
        "player1_object", "player-1 fighter object (inference from the paired 0x80169BF4 tests)"
    ),
    0x80169BF4: _g("player2_object", "player-2 fighter object (inference)"),
    0x8014C3B8: _g("strike_flag", "set by the strike box check; meaning Pending"),
}
