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
* **Pick up an item** (host secondary 3, five frames; the pickup manager sets ``0x800C2558 =
  0x30C`` and player dispatch ``0x16`` at ``0x80038FB8``, and the main player process selects
  secondary 3 at ``0x80029D5C``): the first low punch from stance (host primary ``0x0F``,
  phase 1) as frames 1, 2, 2, 3, 3 (user design, 2026-11-10).
* **Grabbed by an enemy** (the host victim scripts: the ``+0x928`` family and the other
  scripts that position the player with token 10 relative to the grabber, plus the flip
  script ``+0xD78``): the host keeps its grab choreography (tokens, offsets, phase ends) and
  each stock Sub-Zero pose is translated by role. His five flip poses (primary ``0x2E``)
  become the donor's flip poses (MKT table 0 ``0x47``, phase 1, the poses every MKT "flipped
  by" animation uses), which the build must add to the fighter file; his knockdown, stumble,
  forward-flip and lying poses become the imported fighter's frames in the same host slot
  and phase, scaled by position (user design, 2026-11-10).

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
LOW_PUNCH, PICKUP = (0, 0x0F), (1, 0x03)
FLIPPED, STUMBLE, FORWARD_FLIP, BACK_FLIP, LYING = (0, 0x2E), (0, 0x20), (0, 0x1A), (0, 0x1B), (1, 0x09)
MKT_FLIPPED = 0x47  # MKT table-0 slot whose first phase is the fighter's flip poses
# Host roles for the victim poses, in priority order (first match wins).
VICTIM_ROLES = (KNOCKDOWN, STUMBLE, FORWARD_FLIP, BACK_FLIP, LYING)
VICTIM_TOKEN = 10  # position relative to the grabbing actor


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
    if later:
        return start, later[0]
    # A relocated script after every other script start (computed layout): it ends at the first
    # word that is neither a phase end, a token (with its operands) nor a frame record.
    p = start
    while p + 4 <= len(data):
        value = _word(data, p)
        if value == 0:
            p += 4
        elif MKMSZ.is_token(value):
            operands = len(MKMSZ.operands[value])
            if value == 6:
                operands += MKMSZ.callback_extra_words.get(_word(data, p + 4), 0)
            p += 4 * (1 + operands)
            if value == 1:
                break
        elif value % 4 == 0 and value + 8 <= len(data) and _word(data, value) == value + 8 and _word(data, value + 4) == 0:
            p += 4
        else:
            break
    if p == start:
        raise ValueError(f"slot {slot} has no script words")
    return start, p


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


def _scaled(values: list[int], k: int, n: int) -> int:
    """Element ``k`` of ``n`` positions spread over ``values`` (end points kept)."""

    return values[0] if n <= 1 else values[round(k * (len(values) - 1) / (n - 1))]


def _phases(data: bytes | bytearray, slot: tuple[int, int]) -> list[list[int]]:
    """Frame words of each phase of ``slot``'s script, up to a jump/stop or the next script."""

    start, end = slot_span(data, slot)
    phases, cur, p = [], [], start
    while p < end:
        value = _word(data, p)
        if value == 0:
            if cur:
                phases.append(cur)
            cur = []
            p += 4
            continue
        if MKMSZ.is_token(value):
            if value in (1, 2):
                break
            operands = len(MKMSZ.operands[value])
            if value == 6:
                operands += MKMSZ.callback_extra_words.get(_word(data, p + 4), 0)
            p += 4 * (1 + operands)
            continue
        cur.append(value)
        p += 4
    if cur:
        phases.append(cur)
    return phases


FRAME, TOKEN, OPERAND, END = "frame", "token", "operand", "end"


def _script_items(data: bytes | bytearray, start: int, end: int) -> list[tuple[int, int, str]]:
    """(offset, word, kind) for every word of the script in ``[start, end)``."""

    out, p = [], start
    while p < end:
        value = _word(data, p)
        if value == 0 or not MKMSZ.is_token(value):
            out.append((p, value, FRAME if value else END))
            p += 4
            continue
        operands = len(MKMSZ.operands[value])
        if value == 6:
            operands += MKMSZ.callback_extra_words.get(_word(data, p + 4), 0)
        out.append((p, value, TOKEN))
        out += [(p + 4 * k, _word(data, p + 4 * k), OPERAND) for k in range(1, 1 + operands)]
        p += 4 * (1 + operands)
    return out


def pickup(data: bytearray) -> None:
    """Secondary 3 (pick up an item) from the first low punch: frames 1, 2, 2, 3, 3."""

    punch = phase_frames(data, LOW_PUNCH, 1)
    if not punch:
        raise ValueError("host low punch has no first phase")
    positions = frame_positions(data, PICKUP)
    n = len(positions)
    _write(data, positions, [punch[min(len(punch) - 1, (k + 1) * len(punch) // n)] for k in range(n)])


def victim_scripts(stock: bytes | bytearray) -> list[tuple[int, int]]:
    """[start, end) of every stock script that shows the player being grabbed or flipped."""

    flips = set(phase_frames(stock, FLIPPED, 1))
    spans = []
    for start in _starts(stock):
        later = [o for o in _starts(stock) if o > start]
        if not later:
            continue
        items = _script_items(stock, start, later[0])
        if any(kind == TOKEN and w == VICTIM_TOKEN for _, w, kind in items) or any(
            kind == FRAME and w in flips for _, w, kind in items
        ):
            spans.append((start, later[0]))
    return spans


def victim(data: bytearray, stock: bytes | bytearray, flipped: list[int]) -> int:
    """Translate the stock victim poses of ``data`` (see the module notes); returns the number
    of frame words written. ``flipped`` are the imported fighter's flip-pose frame offsets."""

    if not flipped:
        raise ValueError("no flip poses")
    roles: dict[int, int] = {}
    stock_flips = phase_frames(stock, FLIPPED, 1)
    for k, frame in enumerate(stock_flips):
        roles.setdefault(frame, _scaled(flipped, k, len(stock_flips)))
    for slot in VICTIM_ROLES:
        for ours, theirs in zip(_phases(stock, slot), _phases(data, slot), strict=False):
            for k, frame in enumerate(ours):
                roles.setdefault(frame, _scaled(theirs, k, len(ours)))
    written = 0
    for start, end in victim_scripts(stock):
        for (p, word, kind), (q, now, _) in zip(
            _script_items(stock, start, end), _script_items(data, start, end), strict=True
        ):
            if p != q:
                raise ValueError(f"victim script 0x{start:X} changed layout")
            if kind != FRAME:
                if now != word:
                    raise ValueError(f"victim script word 0x{p:X} changed")
                continue
            if word not in roles:
                raise ValueError(f"victim pose 0x{word:X} at 0x{p:X} has no role")
            data[p : p + 4] = roles[word].to_bytes(4, "big")
            written += 1
    return written


def _write(out: bytearray, positions: list[int], values: list[int]) -> None:
    if not values:
        raise ValueError("no source frames")
    for k, p in enumerate(positions):
        out[p : p + 4] = values[min(k, len(values) - 1)].to_bytes(4, "big")


def apply(data: bytes | bytearray, long_fall: bool = True, *,
          stock: bytes | bytearray | None = None, flipped: list[int] | None = None) -> bytearray:
    """A copy of fighter file ``data`` with the slide, death and long-fall recipes applied,
    plus pickup and the victim poses when ``stock`` (the clean host file) and ``flipped`` (the
    imported flip-pose frames) are given."""

    out = bytearray(data)
    slide = frame_positions(out, SLIDE)
    if len(slide) != len(SLIDE_FRAMES):
        raise ValueError(f"host slide script has {len(slide)} frames, expected {len(SLIDE_FRAMES)}")
    _write(out, slide, [frames(data, slot)[k] for slot, k in SLIDE_FRAMES])
    _write(out, frame_positions(out, DEATH), phase_frames(data, KNOCKDOWN, 2))
    if long_fall:  # False reproduces Sektor builder v59
        _write(out, frame_positions(out, LONG_FALL), phase_frames(data, KNOCKDOWN, 1)[-1:])
    if stock is not None:
        pickup(out)
        victim(out, stock, flipped or [])
    return out
