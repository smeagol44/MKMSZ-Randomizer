"""Rope-attachment presentation (player states P28/P29) for an imported fighter.

Stock Sub-Zero draws the attached states with token ``16`` (companion double frame,
``0x80030B6C``): each step binds a narrow arm frame (at most 24x64) on a companion actor
and a body frame on the player. The companion draws through the texture slot held at
player controller ``+0x6E8``, which the player constructor allocates small
(``0x8001C2B4(0x20, 0x40)`` at ``0x8002ED54``); the render pass uploads every bound frame
into it without a size check.

The Sektor takeover maps both operands of every pair to the same full-body fallback frame
(55x113 = ``0x18B8`` CI8 bytes), so on a rope the companion uploads ``0x8B8`` bytes past its
slot into the next texture storage. In production that is Toasty's head (composition v05,
Earth rope route, user save state 2026-11-10). The companion only repeated the owner's frame
on the same spot, so :func:`single_actor` rewrites each ``16, companion, owner`` triple as
``owner, 13, 13`` (token 13 is a no-op): the same frame on the same advance, the same script
offsets for the host's cursor checks (``0x8002FE90``), and no companion actor.

That is not enough (composition v06/v07, user report and RMG save state): stage overlay code
assumes the companion exists while the player hangs from a rope. Earth's rope-hit routine
``0x802F05F4`` (overlay) reads player controller ``+0x650`` and sets ``companion+0x64 |=
0x20`` without a null check, so a spike-trap hit on the rope stored to address ``0x64`` and
the game hung. :func:`transparent_companion` (composition v08) therefore keeps every token-16
pair and its owner frame and only points the companion operand at :func:`companion_frame`, an
8x8 fully transparent raw image: the companion exists as in stock, and its slot receives 64
bytes.
"""

from __future__ import annotations

TOKEN_COMPANION, TOKEN_NOP = 16, 13
# File-0x87 script offsets of the token-16 bodies: P28 +0x32C..+0x38B (eight pairs, then the
# loop at +0x38C), P29 +0x394..+0x3B7 (three pairs, then token 2 at +0x3B8).
ATTACHMENT_PAIRS = tuple(range(0x32C, 0x38C, 12)) + tuple(range(0x394, 0x3B8, 12))


def _word(data: bytes | bytearray, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def single_actor(
    data: bytes | bytearray, pairs: tuple[int, ...] = ATTACHMENT_PAIRS, nops_first: bool = False
) -> bytearray:
    """Return a copy of fighter file ``data`` with each companion pair drawn by the owner only.

    Every pair must still be a token-16 triple whose companion frame is the owner frame (the
    takeover's fallback); anything else is refused rather than silently dropping art.

    ``nops_first`` (composition v07) writes ``13, 13, owner`` instead: the no-ops run first
    in the same advance, so after every advance the cursor rests where token 16 left it (the
    start of the next triple), not one word in. False reproduces v55 / composition v06,
    which hung when a spike trap hit Sektor on the rope (user report)."""

    out = bytearray(data)
    for off in pairs:
        token, companion, owner = (_word(data, off + 4 * i) for i in range(3))
        if token != TOKEN_COMPANION:
            raise ValueError(f"no token-16 pair at +{off:#x}")
        if companion != owner:
            raise ValueError(f"companion frame differs from the owner at +{off:#x}")
        words = (TOKEN_NOP, TOKEN_NOP, owner) if nops_first else (owner, TOKEN_NOP, TOKEN_NOP)
        out[off : off + 12] = b"".join(v.to_bytes(4, "big") for v in words)
    return out


COMPANION_SIZE = (8, 8)  # px; raw CI8, every pixel index 0 (transparent)


def companion_frame(base: int) -> tuple[bytes, int]:
    """``(bytes, shape offset)`` of a transparent frame placed at file offset ``base``
    (4-aligned): the zero word every descriptor needs before it, the descriptor (image,
    size, anchor 0), the one-part shape and a raw type-0 image (header 0, then pixels)."""

    if base % 4:
        raise ValueError("unaligned companion frame")
    w, h = COMPANION_SIZE
    descriptor, shape, image = base + 4, base + 0x10, base + 0x18
    words = (0, image, (w << 16) | h, 0, descriptor, 0, 0)
    blob = b"".join(v.to_bytes(4, "big") for v in words) + bytes(w * h)
    return blob, shape


def transparent_companion(
    data: bytes | bytearray, shape: int, pairs: tuple[int, ...] = ATTACHMENT_PAIRS
) -> bytearray:
    """Return a copy of ``data`` whose token-16 pairs draw ``shape`` on the companion and keep
    their owner frame (same tokens, same offsets, same cursor positions as stock)."""

    out = bytearray(data)
    for off in pairs:
        token, companion, owner = (_word(data, off + 4 * i) for i in range(3))
        if token != TOKEN_COMPANION:
            raise ValueError(f"no token-16 pair at +{off:#x}")
        if companion != owner:
            raise ValueError(f"companion frame differs from the owner at +{off:#x}")
        out[off + 4 : off + 8] = shape.to_bytes(4, "big")
    return out
