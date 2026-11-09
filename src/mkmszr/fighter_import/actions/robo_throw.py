"""Sektor's throw sounds (MKT ``robo1_slam``) on the MKMSZ player throw.

Donor (arcade MK3 ``MKSLAM.ASM`` lineage; MKT USA Rev. 2 N64 tables): ``robo1_slam`` =
``body_slam_init`` (``grab_voice``: voice group 3) and ``ochar_sound 0`` (arm OUT), the
grab animation, ``ochar_sound 1`` (arm THROW) before the throw with the victim, then
``ochar_sound 2`` (arm IN) on the transfer to the thrown reaction, while the arm retracts.

Host (stock MKMSZ USA Rev. 0, player throw ``0x8005BC8C``): it plays player voice category
11 at the grab (``0x80064B00(0x0B, ...)`` at ``0x8005BCD4``; the only other category-11
callers are the grab paths ``0x8003D048`` and ``0x80040654``), runs the grab phase
(``0x80034578`` at ``0x8005BD58``), switches to the victim and runs the throw phase
(``0x80034578`` at ``0x8005BDC8``, attacker controller in ``s0``), restores the attacker
and finishes through ``0x8005BB84`` (``0x8005BDF8``). Three call sites go to payload
wrappers that play the donor sounds when the thrower is the player, then continue to
the stock call with its arguments intact; anyone else's throw is unchanged.

The stock ``jal`` sites enter the payload through its cached KSEG0 alias (a ``jal``
cannot reach KSEG1). This is the reviewed exception of the raw-loaded code contract
(Wiki ``Memory-and-Allocation-Map``): the wrappers and the ``play`` routine they call
only execute payload code (no payload loads or stores), and file ``0x1B`` is
byte-identical on every load.
"""

from __future__ import annotations

from .. import host
from ..host import hi, lo
from ..mips import Assembler

GRAB_VOICE_GROUP = 3
ARM_OUT, ARM_THROW, ARM_IN = 0, 1, 2  # robot ochar sounds

F_VOICE = 0x80064B00
F_PHASE = 0x80034578
F_THROW_END = 0x8005BB84

SITES = {
    0x8005BCD4: 0x0C0192C0,  # jal 0x80064B00 (category 11; delay: sra a2, v0, 24)
    0x8005BDC8: 0x0C00D15E,  # jal 0x80034578 (throw phase; delay: sw v0, 0x64(a0))
    0x8005BDF8: 0x0C016EE1,  # jal 0x8005BB84 (finish; delay: sw a1, 0x63C(v1))
}


def _jal(target: int) -> int:
    return (3 << 26) | ((target >> 2) & 0x03FFFFFF)


def patches(grab: int, throw: int, release: int) -> dict[int, int]:
    return {0x8005BCD4: _jal(grab), 0x8005BDC8: _jal(throw), 0x8005BDF8: _jal(release)}


def _player_ctrl(a: Assembler, out: str) -> None:
    a.lui(out, hi(host.PLAYER_CTRL))
    a.lw(out, lo(host.PLAYER_CTRL), out)


def _emit_wrapper(
    a: Assembler, label: str, events: tuple[int, ...], thrower: str, stock: int, player: str
) -> None:
    """Play ``events`` if ``thrower`` (``"current"`` or a callee-saved register) is the
    player's controller, then tail-jump to ``stock`` with a0-a3 and ra unchanged."""

    a.label(label)
    _player_ctrl(a, "t0")
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


def emit_wrappers(
    a: Assembler, grab_events: tuple[int, ...], throw_event: int, release_event: int,
    player: str = "play",
) -> None:  # fmt: skip
    """``throw_grab`` / ``throw_throw`` / ``throw_release`` (host event numbers)."""

    _emit_wrapper(a, "throw_grab", grab_events, "current", F_VOICE, player)
    _emit_wrapper(a, "throw_throw", (throw_event,), "s0", F_PHASE, player)
    _emit_wrapper(a, "throw_release", (release_event,), "current", F_THROW_END, player)
