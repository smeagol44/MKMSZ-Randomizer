"""Registry of MKMSZ (N64 USA Rev. 0) host routines and globals for the reading aid.

The host counterpart of :mod:`.mkt_registry` (Fighter recompiler plan, milestone 2 task 5). It
names only routines this project has read; the authoritative identities stay in the Wiki
``Function-Registry`` and the ``smeagol44/MKMSZ-Ghidra`` metadata. Main-segment VAs only
(ROM offset = VA - 0x7FFFF400); stage-overlay code needs its own mapping.
"""

from __future__ import annotations

from .mkt_registry import MktRoutine
from .reading import Engine

_F = "Wiki Function-Registry"
_C = "Wiki Fighter-Recompiler-Components (static reading)"
_H = "fighter_import.host (runtime-validated teleport proofs)"


def _e(name: str, args: str, effect: str, evidence: str = _C) -> MktRoutine:
    return MktRoutine(name, args, effect, evidence, "engine")


def _m(name: str, effect: str, evidence: str = _C) -> MktRoutine:
    return MktRoutine(name, "", effect, evidence, "move")


def _g(name: str, effect: str, evidence: str = _C) -> MktRoutine:
    return MktRoutine(name, "", effect, evidence, "global")


REGISTRY: dict[int, MktRoutine] = {
    # -- engine (names from Function-Registry / MKMSZ-Ghidra where they exist) ---------------
    0x8001C2B4: _e(
        "dynamic_texture_alloc", "a0 = w, a1 = h", "allocate a dynamic texture slot", _F
    ),
    0x8001C424: _e("dynamic_texture_release", "a0 = handle", "release a dynamic texture slot", _F),
    0x8001C528: _e(
        "presentation_resource_load",
        "a0 = palette, a1 = count, a2 = mode",
        "load a palette/presentation resource",
        _F,
    ),
    0x800281A0: _e(
        "resource_entry_actor_setup",
        "a0 = entry, a3 = 1",
        "construct an actor from a resource entry",
        _F,
    ),
    0x80064FA4: _e(
        "actor_sound_pan", "", "screen-projected pan of the current actor for gameplay sounds"
    ),
    0x80030378: _e(
        "select_primary_phase2",
        "a0 = primary slot",
        "fighter_select_animation(0, slot), then move the cursor past the first phase",
    ),
    0x80031070: _e(
        "animate_to_phase_end",
        "a0 = ticks per frame",
        "advance the animation, sleeping a0 ticks per step, until the phase ends",
    ),
    0x80024650: _e(
        "actor_list_insert", "a0 = actor, a1 = list", "insert an actor into an actor list", _F
    ),
    0x80024B00: _e(
        "actor_list_remove", "a0 = actor, a1 = list", "remove an actor from an actor list", _F
    ),
    0x80028564: _e("process_exit", "", "end the current process", _F),
    0x80028794: _e("process_sleep", "a0 = ticks", "sleep the current process", _F),
    0x8002830C: _e(
        "controller_clone_alloc", "a0 = class, a1 = routine", "start a child process", _F
    ),
    0x8002BA04: _e(
        "strike_collision",
        "a0 = strike record, a1 = 0",
        "collision core entry: 0x8000 on contact, 0x4000 otherwise",
        _H,
    ),
    0x8002B1C0: _e("actor_stop", "", "stop the current actor", _H),
    0x8002B1EC: _e("player_set_horizontal_velocity", "", "horizontal velocity", _F),
    0x8002FE54: _e(
        "fighter_select_animation", "a0 = table, a1 = slot", "select a fighter animation", _F
    ),
    0x800304C0: _e("animation_advance", "a0 = actor", "advance the animation script one step", _F),
    0x80031724: _e("animation_rate_init", "a0 = ticks", "set the animation rate", _F),
    0x8003174C: _e("animation_rate_advance", "", "rate-gated animation advance", _F),
    0x80031EF0: _e("face_opponent", "", "turn to face the nearest opponent", _F),
    0x80035088: _e(
        "actor_offscreen",
        "a0 = actor, a1 = margin",
        "1 when the actor has left the screen by more than the margin in its direction of travel",
    ),
    0x80046F74: _e(
        "projectile_actor_build",
        "a0 = type, a1 = secondary slot, a2 = +0xD8, a3 = texture w, "
        "stack: texture h, out handle, palette offset",
        "build a projectile actor from secondary animation slot a1 of the fighter file "
        "*0x800A0324[type], palette at that file + offset, at the owner's position",
    ),
    0x80047160: _e(
        "projectile_build",
        "as projectile_actor_build",
        "copy the owner's position to the child controller, then projectile_actor_build",
    ),
    0x8004CE6C: _e(
        "projectile_resolve_strike",
        "a0 = selector",
        "controller +0x638 = strike table 0x800AF340[type][selector]",
        _F,
    ),
    0x8004CF3C: _e(
        "projectile_collision_dispatch",
        "a0 = actor, a1 = selector",
        "strike_collision(0x800AF340[actor type][selector], 0)",
        _F,
    ),
    0x80064C18: _e(
        "gameplay_sfx_wrapper", "a0 = sound descriptor, a1, a2 = pan", "play a gameplay sound", _F
    ),
    0x80072584: _e(
        "eye_use",
        "",
        "Eye item use: player controller +0x6BC |= 0x1000, actor +0x8C |= 0x4000, +0x64 |= 0x2000, "
        "colour +0xFC/+0xFE/+0x100 = 32 (also the attached actor +0x650), 0x800A5FA0 |= 1, "
        "0x802ECCC6 |= 1",
    ),
    0x80072644: _e(
        "eye_timer",
        "",
        "sleep 1200 ticks, then undo eye_use (colour back to 128), clear 0x800A5FA0 bit 0, exit",
    ),
    0x80005D74: _e(
        "ai_lose_player",
        "",
        "enemy AI branch taken while the player has +0x6BC & 0x1000: idle for a random 47..110 ticks",
    ),
    # -- Quan Chi (fighter type 0x1B, fighter file 0x93) -------------------------------------
    0x800498A8: _m(
        "quanchi_projectile_action",
        "secondary animation slot 2 in four steps, child process quanchi_projectile, sleep 40",
    ),
    0x80049668: _m(
        "quanchi_projectile",
        "projectile: sound 0x12, build from secondary slot 3, speed 6.0 px/tick, collision selector "
        "0x11 each tick, bounce away on contact, sound 2 every 8 ticks, ends offscreen (margin 200)",
    ),
    # -- globals ------------------------------------------------------------------------------
    0x802ECE20: _g("current_controller", "running controller (+0x6E0 actor, +0x640 opponent)", _F),
    0x802C1AC0: _g("player_controller", "player controller pointer", _F),
    0x80291C10: _g(
        "player_file_base", "file 0x87 (player fighter file) base, stored when the file is loaded"
    ),
    0x800A0324: _g(
        "type_fighter_file_table",
        "per-type pointer to the fighter-file base global; type 4 (player) "
        "is 0; only reader projectile_actor_build",
    ),
    0x800AF340: _g("type_strike_table", "per-type strike-record tables (type 4: 0x800AF484)", _F),
    0x800A6268: _g("item_use_table", "item-use handlers by item id (3: eye_use)", _F),
    0x800A5FA0: _g("item_effects", "active item effect bits (bit 0: Eye); cleared at stage start"),
}

MKMSZ = Engine("MKMSZ", REGISTRY, {}, 0x7FFFF400)
