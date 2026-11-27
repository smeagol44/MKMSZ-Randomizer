"""A donor fighter's own throw sounds on the host player throw (SMRE step 3, reusable).

MKT starts each fighter's throw from the per-fighter table :data:`THROW_TABLE` (indexed by MKT
fighter id; Static-confirmed: every entry opens with ``slam_init`` ``0x80042698``). The routine
runs the grab animation (``slam_grab`` ``0x80042668``), waits for the throw (``0x80075774``),
gives the victim its thrown routine (``slam_transfer`` ``0x80042580``) and recovers. Some
fighters play their own sounds (``ft_sound``) between these steps: Sektor's ``0x80042498``
plays 0 (arm out) at the grab, 1 (arm throw) before the throw and 2 (arm in) after the
transfer, as the arcade ``robo1_slam``. Reptile's and Rayden's play none. MKT's grab voice (every
fighter, voice group 3) is not played (owner, 2026-11-27: grab sounds dropped for now).

:func:`read` sorts the routine's ``ft_sound`` calls (one level of its own callees followed)
into ``grab`` (before the grab animation), ``throw`` (before the transfer) and ``release``.
:func:`emit_hooks` writes payload wrappers for the three host sites of the player throw
``0x8005BC8C``, as Sektor's runtime-confirmed legacy build (proof v41): each plays its sounds
when the thrower is the player, then continues to the stock call with its arguments intact.
"""

from __future__ import annotations

from . import host, reading
from .host import hi, lo
from .mips import Assembler

THROW_TABLE = 0x800A7ED8  # MKT per-fighter throw routines (slam), by fighter id
FT_SOUND = 0x80005760
SLAM_GRAB = 0x80042668  # (phase): the throw animation (table 0 slot 0x23) to that phase
SLAM_TRANSFER = 0x80042580  # (routine): the victim's thrown routine
STAGES = ("grab", "throw", "release")
# MKT's throw start 0x80042878 also plays the grab voice (0x80004FE4(3): voice group 3) for every
# fighter; the builds leave it out for now (owner, 2026-11-27).

# Host player throw 0x8005BC8C: site VA -> (stock word, the routine it calls). Grab: the grab
# voice (category 11); throw: the throw phase with the victim (attacker controller in s0);
# release: the finish.
F_VOICE, F_PHASE, F_FINISH = 0x80064B00, 0x80034578, 0x8005BB84
SITES = {
    "grab": (0x8005BCD4, 0x0C0192C0, F_VOICE, "current"),
    "throw": (0x8005BDC8, 0x0C00D15E, F_PHASE, "s0"),
    "release": (0x8005BDF8, 0x0C016EE1, F_FINISH, "current"),
}


def _u32(mkt: bytes, va: int) -> int:
    return int.from_bytes(mkt[va - 0x80000000 : va - 0x80000000 + 4], "big")


def read(mkt: bytes, fighter: int) -> dict[str, list[int]]:
    """``{"grab": [...], "throw": [...], "release": [...]}``: the donor fighter sound numbers
    its MKT throw routine plays at each stage (empty lists for a fighter with none)."""

    entry = _u32(mkt, THROW_TABLE + 4 * fighter)
    out: dict[str, list[int]] = {s: [] for s in STAGES}
    stage = 0

    def walk(routine: int, depth: int) -> None:
        nonlocal stage
        for call in reading.read(mkt, routine).calls:
            if call.target == FT_SOUND:
                if call.args[0] is None:
                    raise ValueError(f"throw 0x{entry:08X}: ft_sound with an unread number at 0x{call.pc:08X}")
                out[STAGES[stage]].append(call.args[0])
            elif call.target == SLAM_GRAB:
                stage = max(stage, 1)
            elif call.target == SLAM_TRANSFER:
                stage = 2
            elif depth == 0 and call.target is not None and call.target >> 24 == 0x80 and call.target not in _ENGINE:
                walk(call.target, 1)  # a shared throw body (Reptile's 0x80040274)

    walk(entry, 0)
    return out


_ENGINE = {0x80042698, 0x80075774, 0x80042898, 0x8005A88C, 0x8000E59C, 0x8006CA4C}


def emit_hooks(a: Assembler, sounds: dict[str, tuple[int, ...]], player: str = "play") -> dict[str, str]:
    """A wrapper per stage with host sound events; returns stage -> label."""

    labels = {}
    for stage in STAGES:
        events = sounds.get(stage, ())
        if not events:
            continue
        _, _, stock, thrower = SITES[stage]
        label = f"throw_hook_{stage}"
        labels[stage] = label
        a.label(label)
        a.lui("t0", hi(host.PLAYER_CTRL))
        a.lw("t0", lo(host.PLAYER_CTRL), "t0")
        if thrower == "current":
            a.lui("t1", hi(host.CURRENT_CTRL))
            a.lw("t1", lo(host.CURRENT_CTRL), "t1")
        else:
            a.move("t1", thrower)
        a.bne("t0", "t1", label + "_stock")
        a.addiu("sp", "sp", -0x20)
        a.sw("ra", 0x1C, "sp")
        for k, reg in enumerate(("a0", "a1", "a2", "a3")):
            a.sw(reg, 0x0C + 4 * k, "sp")
        for event in events:
            host.play_sound(a, event, player)
        for k, reg in enumerate(("a0", "a1", "a2", "a3")):
            a.lw(reg, 0x0C + 4 * k, "sp")
        a.lw("ra", 0x1C, "sp")
        a.addiu("sp", "sp", 0x20)
        a.label(label + "_stock")
        a.lui("t9", hi(stock))
        a.addiu("t9", "t9", lo(stock))
        a.jr("t9")
        a.nop()
    return labels
