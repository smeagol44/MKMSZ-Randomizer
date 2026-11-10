"""Generic host animations built from an imported fighter's common MKT animations.

MKT fighters share their basic animation set (stance, duck, duck turn, duck low kick,
knockdown, jump, ...; table-0 indices are the same for every fighter), and the importer
maps them onto the MKMSZ player slots of the same meaning. Some MKMSZ player states have
no MKT counterpart; these recipes fill them from that common set, so they work for any
imported MKT fighter (user design, 2026-11-10):

* **Slide / Super Slide** (host secondary 2, shared with secondary 1; played by Slide
  ``0x80059FF0`` and Super Slide ``0x8005A5C0`` through ``0x8002FE54(1, 2)``): duck frame 1,
  duck-turn frame 1, duck-low-kick frame 3. Only ninjas have a slide in MKT.
* **Death** (host primary ``0x2A``; the main player death branch ``0x80029034`` selects it
  when health reaches zero, then state ``0x502``): the knockdown sequence of host primary
  ``0x1E`` (its fall-back and landing phases), in order, the last (lying) frame held for the
  remaining frame words.
* **Falling to death** (host secondary 8, Sub-Zero's long-fall loop; a pit fall first plays the
  knockdown, primary ``0x1E``, then selects ``0x8002FE54(1, 8)``, traced from a user save state
  on Water): the last frame of the knockdown's fall-back phase, held (user design).

Each recipe rewrites only the frame words of the target slot's script (tokens, operands,
callback words and phase ends stay), reading the source frames from the already imported
host slots. A slot's script spans up to the next script any table entry points at.
"""

from __future__ import annotations

from .mkmsz_fighter import TABLE0_COUNT, TABLE1_COUNT, TABLE1_OFFSET
from .script import MKMSZ

DUCK, DUCK_TURN, DUCK_LOW_KICK, KNOCKDOWN, DEATH = (
    (0, 0x04),
    (0, 0x05),
    (0, 0x0A),
    (0, 0x1E),
    (0, 0x2A),
)
SLIDE = (1, 0x02)
LONG_FALL = (1, 0x08)
SLIDE_FRAMES = ((DUCK, 0), (DUCK_TURN, 0), (DUCK_LOW_KICK, 2))  # (slot, frame index)


def _word(data: bytes | bytearray, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def _starts(data: bytes | bytearray) -> list[int]:
    offs = [_word(data, 4 * i) for i in range(TABLE0_COUNT)]
    offs += [_word(data, TABLE1_OFFSET + 4 * i) for i in range(TABLE1_COUNT)]
    return sorted({o for o in offs if o})


def slot_span(data: bytes | bytearray, slot: tuple[int, int]) -> tuple[int, int]:
    table, index = slot
    start = _word(data, 4 * index if table == 0 else TABLE1_OFFSET + 4 * index)
    if not start:
        raise ValueError(f"slot {slot} has no script")
    later = [o for o in _starts(data) if o > start]
    if not later:
        raise ValueError(f"slot {slot} is the last script; its end is unknown")
    return start, later[0]


def frame_positions(data: bytes | bytearray, slot: tuple[int, int]) -> list[int]:
    """File offsets of the frame words of ``slot``'s script, in order."""

    start, end = slot_span(data, slot)
    out, p = [], start
    while p < end:
        value = _word(data, p)
        if value == 0:
            p += 4
            continue
        if MKMSZ.is_token(value):
            operands = len(MKMSZ.operands[value])
            if value == 6:
                operands += MKMSZ.callback_extra_words.get(_word(data, p + 4), 0)
            p += 4 * (1 + operands)
            continue
        out.append(p)
        p += 4
    return out


def frames(data: bytes | bytearray, slot: tuple[int, int]) -> list[int]:
    return [_word(data, p) for p in frame_positions(data, slot)]


def phase_frames(data: bytes | bytearray, slot: tuple[int, int], phases: int) -> list[int]:
    """The frames of the first ``phases`` phases of ``slot``'s script (a source sequence:
    other slots may point into it, e.g. host secondary 9 at the knockdown's lying phase)."""

    table, index = slot
    p = _word(data, 4 * index if table == 0 else TABLE1_OFFSET + 4 * index)
    out, ends = [], 0
    while ends < phases:
        value = _word(data, p)
        if value == 0:
            ends += 1
            p += 4
            continue
        if MKMSZ.is_token(value):
            if value == 1:  # a jump ends the sequence
                break
            operands = len(MKMSZ.operands[value])
            if value == 6:
                operands += MKMSZ.callback_extra_words.get(_word(data, p + 4), 0)
            p += 4 * (1 + operands)
            continue
        out.append(value)
        p += 4
    return out


def _write(out: bytearray, positions: list[int], values: list[int]) -> None:
    if not values:
        raise ValueError("no source frames")
    for k, p in enumerate(positions):
        out[p : p + 4] = values[min(k, len(values) - 1)].to_bytes(4, "big")


def apply(data: bytes | bytearray, long_fall: bool = True) -> bytearray:
    """A copy of fighter file ``data`` with the slide, death and long-fall recipes applied."""

    out = bytearray(data)
    slide = frame_positions(out, SLIDE)
    if len(slide) != len(SLIDE_FRAMES):
        raise ValueError(f"host slide script has {len(slide)} frames, expected {len(SLIDE_FRAMES)}")
    _write(out, slide, [frames(data, slot)[k] for slot, k in SLIDE_FRAMES])
    _write(out, frame_positions(out, DEATH), phase_frames(data, KNOCKDOWN, 2))
    if long_fall:  # False reproduces Sektor builder v59
        _write(out, frame_positions(out, LONG_FALL), phase_frames(data, KNOCKDOWN, 1)[-1:])
    return out
