"""Move components and move programs (Fighter recompiler plan, milestone 2).

A **move program** is data: a command (how the move is entered) plus a list of steps, each a
**component** from :data:`COMPONENTS` with engine-neutral parameters. The MKT reading
(milestone 3) produces programs; the MKMSZ backend lowers them. The Wiki page
``Fighter-Recompiler-Components`` is the catalogue (meaning, parameters, units, ending, host
lowering); this module is its machine-checked form.

Units (engine-neutral, anchored on donor values and the documented calibrations):

* ``ticks``: donor process ticks (MKT runs at 60 Hz).
* ``px``: donor pixels; ``vel``: donor 16.16 pixels per tick; ``accel``: 16.16 per tick².
  The backend converts motion with the standard-jump calibration (:mod:`.physics`).
* ``anim``: a donor animation ``{"table": 0|1, "slot": n}`` plus optional ``part`` (1-based)
  and ``offset`` (script words); the body builder imports the frames it names.
* ``sound``: ``{"fighter": n}`` (the donor fighter sound table entry) or ``{"shared": n}``.
* ``effect``: ``{"mkt_fx": n}`` (donor shared effect index).
* ``strike``: ``{"box": [x, y, w, h], "damage": n, "block_damage": n, "reaction": name,
  "blocked_reaction": name}``; reactions are meanings from :data:`REACTIONS`.

Provenance (owner decision 2026-11-11): every parameter of every step names its source in the
step's ``src`` map: ``"MKT 0x8004F9AC"`` (the donor instruction or data word), ``"host"`` or
``"host 0x..."`` (an MKMSZ fact) or ``"owner"`` (an owner decision). Integers may be written as
hex strings. :func:`validate_programs` raises :class:`ProgramError` listing every problem.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib import resources
from typing import Any

FORMAT = 1
SRC = re.compile(r"^(MKT 0x[0-9A-F]{8}|host( 0x[0-9A-F]{8})?|owner)$")

# Victim reactions by meaning. The donor id is provenance; the backend maps each meaning to a
# host reaction (Wiki MKT-Adapter-Primitives, "Strike and reaction translation").
REACTIONS = {
    "none": "no victim reaction",
    "elbow_hold": "MKT 0x74: grounded victim held about 20 ticks; airborne victims rejected",
    "launch": "MKT 0x24: generic damaging launch, flight and landing",
    "knockback_arc": "MKT 0x71: victim thrown back on an arc (x -0x2CCCC, y -0x6CCCC, gravity 0x5199)",
    "acid_stagger": "MKT 0x72: victim staggers back (+0x420 = 0x26666); details Pending",
    "rocket_stumble": "MKT r_rocket -> zap_stumble: stumble back",
    "uppercut": "teleport strike: host uppercut reaction 0x08 (runtime-confirmed teleport)",
    "blocked": "the stock blocked reaction",
}

# Command conditions (checked when the command matches).
CONDITIONS = {
    "buttons_held": "the listed buttons are held exactly (mask)",
    "holding_away": "the stick is held away from the opponent (Hypothesis on the MKT side)",
    "cooldown": "at least `ticks` since `key` was stamped for this player",
    "opponent_state": "opponent-state guard read from the donor; meaning Pending (see Wiki)",
    "projectiles_below": "fewer than `count` live projectiles of this fighter",
}

# op -> {param: kind}; a trailing "?" marks an optional parameter.
COMPONENTS: dict[str, dict[str, str]] = {
    # control
    "begin": {"action_mkt": "int", "face": "bool", "stop": "bool"},
    "end": {},
    "sleep": {"ticks": "ticks"},
    "wait": {"until": "enum:opponent_settled"},
    "repeat": {"count": "int", "steps": "steps"},
    # animation
    "animate": {"anim": "anim", "rate": "ticks", "until": "enum:phase_end|running|manual"},
    "pose": {"anim": "anim"},
    "finish": {"rate": "ticks"},
    "next_frame": {},
    "face": {},
    "flip": {},
    # motion
    "velocity": {"x": "vel", "y?": "vel"},
    "stop": {},
    "jump": {
        "x": "vel",
        "y": "vel",
        "gravity": "accel",
        "until": "enum:landing|below_screen|surface",
    },
    "shake": {"dx": "px", "dy": "px", "count": "int", "ticks": "ticks"},
    "pass_through": {"ticks": "ticks"},
    "relocate": {"to": "enum:behind_opponent", "dx": "px", "dy?": "px"},
    # presentation
    "sound": {"sound": "sound"},
    "effect": {"effect": "effect", "at?": "enum:self|opponent"},
    # combat
    "strike": {
        "strike": "strike",
        "ticks": "ticks",
        "skip?": "ticks",
        "every_tick?": "steps",
        "only_if?": "enum:opponent_settled|rising",
        "on_hit": "steps",
        "on_block?": "steps",
    },
    "projectile": {
        "art": "anim",
        "offset": "pxpair",
        "speed": "vel",
        "rate": "ticks",
        "strike": "strike",
        "accel?": "vel",
        "cap?": "vel",
        "hum?": "hum",
        "trail?": "trail",
        "checks?": "boxes",
        "homing?": "homing",
        "impact": "impact",
    },
    # state
    "stealth": {"ticks": "ticks"},
    "stamp": {"key": "str"},
}

KINDS_INT = {"int", "ticks", "px", "vel", "accel"}


class ProgramError(ValueError):
    pass


@dataclass(frozen=True)
class Move:
    name: str
    command: dict[str, Any]
    steps: list[dict[str, Any]]


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"-?0x[0-9A-Fa-f]+|-?\d+", value):
        return int(value, 0)
    return None


def _check_value(kind: str, value: Any, where: str, errors: list[str]) -> None:
    def need(cond: bool, what: str) -> None:
        if not cond:
            errors.append(f"{where}: {what}")

    if kind in KINDS_INT:
        need(_int(value) is not None, f"expected an integer ({kind})")
    elif kind == "bool":
        need(isinstance(value, bool), "expected true/false")
    elif kind == "str":
        need(isinstance(value, str) and bool(value), "expected a name")
    elif kind.startswith("enum:"):
        need(value in kind[5:].split("|"), f"expected one of {kind[5:]}")
    elif kind == "anim":
        need(isinstance(value, dict) and value.get("table") in (0, 1), "anim needs table 0 or 1")
        if isinstance(value, dict):
            need(_int(value.get("slot")) is not None, "anim needs a slot")
            need(set(value) <= {"table", "slot", "part", "offset"}, "anim has unknown keys")
    elif kind == "sound":
        need(isinstance(value, dict) and len(value) == 1 and set(value) <= {"fighter", "shared"},
             "sound is {fighter: n} or {shared: n}")  # fmt: skip
    elif kind == "effect":
        need(isinstance(value, dict) and set(value) == {"mkt_fx"}, "effect is {mkt_fx: n}")
    elif kind == "strike":
        ok = isinstance(value, dict) and set(value) == {
            "box", "damage", "block_damage", "reaction", "blocked_reaction"}  # fmt: skip
        need(ok, "strike needs box, damage, block_damage, reaction, blocked_reaction")
        if ok:
            need(len(value["box"]) == 4, "strike box is [x, y, w, h]")
            for r in ("reaction", "blocked_reaction"):
                need(value[r] in REACTIONS, f"unknown reaction {value[r]!r}")
    elif kind == "pxpair":
        need(isinstance(value, list) and len(value) == 2, "expected [x, y] in px")
    elif kind == "hum":
        need(isinstance(value, dict) and set(value) == {"sound", "every"}, "hum is {sound, every}")
    elif kind == "trail":
        need(
            isinstance(value, dict) and set(value) == {"effect", "every"},
            "trail is {effect, every}",
        )
    elif kind == "boxes":
        need(isinstance(value, list) and all(isinstance(b, dict) and set(b) == {"box", "after"}
             for b in value), "checks are [{box, after}]")  # fmt: skip
    elif kind == "homing":
        need(isinstance(value, dict) and set(value) == {"aim_dy", "speed", "explode_within"},
             "homing is {aim_dy, speed, explode_within}")  # fmt: skip
    elif kind == "impact":
        need(isinstance(value, dict) and "end" in value and set(value) <= {
            "anim", "rate", "sound", "effect", "at", "end", "bounce"}, "impact keys")  # fmt: skip
    elif kind == "steps":
        need(isinstance(value, list), "expected a list of steps")
    else:  # pragma: no cover - catalogue error
        errors.append(f"{where}: unknown kind {kind}")


def validate_steps(steps: Any, where: str, errors: list[str]) -> None:
    if not isinstance(steps, list):
        errors.append(f"{where}: steps must be a list")
        return
    for i, step in enumerate(steps):
        here = f"{where}[{i}]"
        if not isinstance(step, dict) or step.get("op") not in COMPONENTS:
            errors.append(
                f"{here}: unknown component {step.get('op') if isinstance(step, dict) else step!r}"
            )
            continue
        spec = COMPONENTS[step["op"]]
        names = {k.rstrip("?"): k for k in spec}
        src = step.get("src", {})
        given = set(step) - {"op", "src"}
        for extra in sorted(given - set(names)):
            errors.append(f"{here} {step['op']}: unknown parameter {extra}")
        for name, key in names.items():
            if name not in step:
                if not key.endswith("?"):
                    errors.append(f"{here} {step['op']}: missing {name}")
                continue
            kind = spec[key]
            _check_value(kind, step[name], f"{here} {step['op']}.{name}", errors)
            if kind == "steps":
                validate_steps(step[name], f"{here}.{name}", errors)
            elif not SRC.match(str(src.get(name, ""))):
                errors.append(f"{here} {step['op']}.{name}: missing or malformed src")


def validate_programs(doc: Any) -> list[Move]:
    errors: list[str] = []
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        raise ProgramError(f"move programs need format {FORMAT}")
    moves: list[Move] = []
    for i, m in enumerate(doc.get("moves", [])):
        where = f"moves[{i}] {m.get('name', '?')}"
        cmd = m.get("command", {})
        for key in ("buttons", "tokens", "window", "src"):
            if key not in cmd:
                errors.append(f"{where}: command needs {key}")
        for cond in cmd.get("conditions", []):
            if cond.get("kind") not in CONDITIONS:
                errors.append(f"{where}: unknown condition {cond.get('kind')!r}")
            elif not SRC.match(str(cond.get("src", ""))):
                errors.append(f"{where}: condition {cond['kind']} needs src")
        validate_steps(m.get("steps"), f"{where} steps", errors)
        moves.append(Move(m.get("name", ""), cmd, m.get("steps", [])))
    if not moves:
        errors.append("no moves")
    for gap in doc.get("gaps", []):
        if not {"move", "what"} <= set(gap):
            errors.append(f"gap entry needs move and what: {gap}")
    if errors:
        raise ProgramError("; ".join(errors))
    return moves


def load_programs(fighter: str) -> tuple[list[Move], list[dict[str, str]]]:
    text = resources.files("mkmszr.fighters.moves").joinpath(f"{fighter}.json").read_text("utf-8")
    doc = json.loads(text)
    return validate_programs(doc), doc.get("gaps", [])


def components_used(moves: list[Move]) -> set[str]:
    used: set[str] = set()

    def walk(steps: list[dict[str, Any]]) -> None:
        for s in steps:
            used.add(s["op"])
            for key, kind in COMPONENTS[s["op"]].items():
                if kind == "steps" and key.rstrip("?") in s:
                    walk(s[key.rstrip("?")])

    for m in moves:
        walk(m.steps)
    return used
