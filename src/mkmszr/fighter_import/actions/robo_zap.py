"""Sektor's straight rocket (MKT ``do_robo_zap`` / ``rocket1_proc``) on the MKMSZ host.

The rocket is built by re-hosting stock Ice Blast and swapping donor behaviour in one
piece at a time (Wiki ``MKT-Adapter-Primitives``, "Importer direction"). The host is a
lifted copy of the stock Ice root (:mod:`..lifter`); every behavioural change is a
declared word patch on that copy, checked against the stock word it replaces, so the
stock root (still used by Sub-Zero's up/down Ice) is never touched.

Donor facts are MKT USA Rev. 2 N64 retail values (not the arcade source lineage).
"""

from __future__ import annotations

from ..host import F_OFFSET, UNITS_PER_TEXEL
from ..lifter import LiftError, LiftResult
from ..mips import REG

# Stock MKMSZ Ice host (USA Rev. 0)
ICE_CALLBACK_SRC, ICE_CALLBACK_END = 0x80049C34, 0x80049C84  # LP record action
ICE_CALLBACK_GROUND_SELECTOR = 0x80049C70  # 'move a0, zero' -> transfer selector
ICE_ROOT_SRC, ICE_ROOT_END = 0x8004AB84, 0x8004B1D0  # transfer selector 0 (all Ice modes)

# Donor: retail placement of the rocket relative to Sektor, in sprite pixels (source
# adjust_xy_a5(SCX(7), SCY(45))). The host helper takes world units: x UNITS_PER_TEXEL.
# (v72/v24 passed the pixel values unscaled: half the distance, too high and inward.)
PLACEMENT = (5, 38)


def _addiu(rt: str, imm: int) -> int:
    return (0x09 << 26) | (REG[rt] << 16) | (imm & 0xFFFF)


def _jal(target: int) -> int:
    return (3 << 26) | ((target >> 2) & 0x03FFFFFF)


# Stock words at the root's projectile placement call:
#   0x80031208(+0x648 actor, (s16)s2, (s16)s3), s2/s3 = per-mode stock offsets.
PLACEMENT_SITE = {
    0x8004AFF0: 0x00122C00,  # sll a1, s2, 16
    0x8004AFF4: 0x00052C03,  # sra a1, a1, 16
    0x8004AFFC: 0x00133400,  # sll a2, s3, 16
    0x8004B000: _jal(F_OFFSET),
    0x8004B004: 0x00063403,  # sra a2, a2, 16 (delay slot)
}


def placement_patches(dx: int = PLACEMENT[0], dy: int = PLACEMENT[1]) -> dict[int, int]:
    """Root patches: place the projectile at donor pixel offset ``(dx, dy)``.

    Converted to host world units; the host helper applies facing.
    """

    dx, dy = dx * UNITS_PER_TEXEL, dy * UNITS_PER_TEXEL
    for value in (dx, dy):
        if not -0x8000 <= value < 0x8000:
            raise ValueError("placement offsets are signed 16-bit whole units")
    return {
        0x8004AFF0: _addiu("a1", dx),
        0x8004AFF4: 0,
        0x8004AFFC: _addiu("a2", dy),
        0x8004B004: 0,
    }


# Every stock word a rocket patch may replace, by VA (lifted callback and root).
STOCK_WORDS = {ICE_CALLBACK_GROUND_SELECTOR: 0x00002021, **PLACEMENT_SITE}  # move a0, zero


def check_stock(result: LiftResult) -> None:
    """Each patch in a lift report must replace a documented stock word, unchanged."""

    for va, (old, _new) in result.patched.items():
        if va not in STOCK_WORDS:
            raise LiftError(f"undocumented rocket patch site {va:#x}")
        if old != STOCK_WORDS[va]:
            raise LiftError(
                f"stock word at {va:#x} is {old:#010x}, expected {STOCK_WORDS[va]:#010x}"
            )


# ---- Chest open / hold / close (MKZAP.ASM robo_open_chest_fast, sleep 0x20, robo_close_chest)
# Donor robot secondary animation slot 0: RBCHEST1, RBCHEST2. MKT (60 Hz): open with
# mframew 4 ticks/frame (2 if the opponent is reacting: not modelled yet), rocket created,
# hold 0x20, close with backwards_ani 4 ticks/frame, then the action ends.
CHEST_FRAMES = (0x29A0, 0x29B4)  # robot heap offsets: RBCHEST1, RBCHEST2

# Stock Zap script (fighter file 0x87, animation slot 0x24) as the lifted root plays it on
# the parent (host ticks): phase 1 (+0xDA0..+0xDB0) at 2 ticks/frame via 0x80030E98(3);
# sleep 2; token 0x0B (+0xDB8, constructor +0xDBC) creates the projectile; sleep 2 in
# 0x8004B584; the projectile process starts; recovery frames +0xDCC..+0xDE0 with sleeps
# 2, 2, 3, 4, 5, 5 (root 0x8004B108..0x8004B1A0, or 0x8004B650.. on a point-blank hit).
ZAP_SCRIPT = 0xDA0
ZAP_TOKEN = 0xDB8
ZAP_RECOVERY = (0xDCC, 0xDD0, 0xDD4, 0xDD8, 0xDDC, 0xDE0)


def chest_script_words(open1: int, open2: int) -> dict[int, int]:
    """Zap script words (file offset -> word) for the chest open, hold and close.

    Phase 1 becomes RBCHEST1, RBCHEST2 (2 + 2 ticks, donor 4 + 4 at 60 Hz), then jumps
    to the unchanged token so the projectile hooks keep their offsets. From projectile
    creation RBCHEST2 holds 2 + 2 + 2 + 3 + 4 + 5 = 18 ticks (donor 32 + 4) and the last
    recovery frame shows RBCHEST1 (closing).
    """

    words = {
        ZAP_SCRIPT: open1,
        ZAP_SCRIPT + 4: open2,
        ZAP_SCRIPT + 8: 0,  # end of phase 1
        ZAP_SCRIPT + 0xC: 1,  # jump
        ZAP_SCRIPT + 0x10: ZAP_TOKEN,
        ZAP_SCRIPT + 0x14: 0,  # unreachable
    }
    for pos in ZAP_RECOVERY[:-1]:
        words[pos] = open2
    words[ZAP_RECOVERY[-1]] = open1
    return words


# Root patch: the last recovery frame (RBCHEST1, closing) holds 2 ticks (donor 4), not 5.
CLOSE_HOLD_SITE = {0x8004B1A0: 0x24040005}  # addiu a0, zero, 5 (sleep delay slot)


def close_patches(ticks: int = 2) -> dict[int, int]:
    return {0x8004B1A0: _addiu("a0", ticks)}


STOCK_WORDS.update(CLOSE_HOLD_SITE)
