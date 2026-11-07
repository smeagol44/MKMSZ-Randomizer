"""Fighter animation-script grammar, decoder, assembler and verifier.

MKT N64 (``do_next_a9_frame`` 0x8000D408) and MKMSZ N64 (0x800304C0) share one
script grammar lineage: big-endian words, ``0`` ends a phase, small values are
control tokens, and every larger value is a frame-record offset relative to the
fighter resource base. The dialects differ only in their token range and in
which operands a token or callback consumes.

The decoder turns a script region into a list of :class:`Insn` whose jump
operands are symbolic labels, so a region can be re-assembled byte for byte or
re-laid out after an edit (jump targets are recomputed from labels). Phases are
preserved as explicit ``END`` instructions: host action code may keep advancing
past a terminator, so a terminator is never treated as the end of the region.

Canonical documentation: Wiki ``Data-Structures-and-Encodings`` (Fighter
animation script grammar) and ``MKT-Adapter-Primitives`` (Animation script
grammar translation).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

OperandKind = Literal["raw", "label", "frame"]

# Operand kinds per token. "label" = base-relative jump target inside the script
# region; "frame" = base-relative frame/resource entry outside it; "raw" = value.
_COMMON_OPERANDS: dict[int, tuple[OperandKind, ...]] = {
    1: ("label",),  # jump
    2: (),  # horizontal flip
    3: ("raw",),  # X offset (signed low halfword)
    4: ("raw",),  # XY offset (signed halfwords)
    5: ("frame",),  # frame without wait
    6: ("raw",),  # callback index
    7: ("raw",),  # MKT: sound; MKMSZ: skipped
    8: ("raw", "label"),  # jump if fighter ID/type == operand
    9: (),  # vertical flip
    10: ("raw",),  # partner/opponent-relative placement
    11: ("frame",),  # create helper object/actor from an entry
    12: (),  # helper step
    13: (),  # MKT: next-frame palette; MKMSZ: no-op
    14: (),  # helper step counted as frame
    15: ("raw",),  # MKT: sound pair; MKMSZ: skipped
}


@dataclass(frozen=True)
class Dialect:
    """Token grammar of one engine."""

    name: str
    max_token: int
    operands: Mapping[int, tuple[OperandKind, ...]]
    # Callback index -> number of extra raw words the callback consumes.
    callback_extra_words: Mapping[int, int] = field(default_factory=dict)

    def is_token(self, value: int) -> bool:
        return 1 <= value <= self.max_token


MKMSZ = Dialect(
    name="mkmsz",
    max_token=16,
    operands={**_COMMON_OPERANDS, 16: ("frame", "frame")},  # companion + owner frame
    callback_extra_words={1: 1, 2: 1},  # 1: set rate, 2: play SFX
)

MKT = Dialect(name="mkt", max_token=15, operands=dict(_COMMON_OPERANDS))


@dataclass(frozen=True)
class Operand:
    kind: OperandKind | Literal["data"]
    value: int | str  # int for raw/frame/data; label name for label

    def __repr__(self) -> str:  # compact test/debug output
        return f"{self.kind}:{self.value if isinstance(self.value, str) else hex(self.value)}"


@dataclass(frozen=True)
class Insn:
    """One decoded script unit.

    ``op`` is ``"END"`` (phase terminator), ``"FRAME"`` (show a frame), ``"TOKEN"``
    (control token ``token``) or ``"DATA"`` (a word inside the region that is a
    pointer to another script position, e.g. an embedded script-pointer table).
    """

    op: Literal["END", "FRAME", "TOKEN", "DATA"]
    token: int = 0
    operands: tuple[Operand, ...] = ()


def insn_size(insn: Insn) -> int:
    """Size of an instruction in 32-bit words."""

    if insn.op == "TOKEN":
        return 1 + len(insn.operands)
    return 1


def label_name(offset: int) -> str:
    return f"L_{offset:05X}"


@dataclass
class Region:
    """A decoded script region of a fighter resource."""

    dialect: Dialect
    start: int
    end: int
    insns: list[Insn]
    labels: dict[str, int]  # label -> index into insns (decode-time layout)
    offsets: list[int]  # decode-time offset of each insn

    def label_at(self, offset: int) -> str:
        name = label_name(offset)
        if name not in self.labels:
            raise ValueError(f"offset 0x{offset:X} is not an instruction boundary")
        return name

    def index_of(self, offset: int) -> int:
        return self.labels[self.label_at(offset)]


class DecodeError(ValueError):
    pass


def _be32(data: bytes | bytearray | memoryview, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def decode_region(
    data: bytes | bytearray,
    start: int,
    dialect: Dialect,
    *,
    end: int | None = None,
    base: int = 0,
) -> Region:
    """Decode a script region linearly.

    ``data[base:]`` is the fighter resource; offsets are resource-relative. If
    ``end`` is omitted, decoding stops at the lowest frame offset referenced so
    far (frame records follow the scripts in every observed resource).
    """

    if start % 4:
        raise DecodeError("script region must be word aligned")
    raw: list[tuple[int, str, int, list[tuple[OperandKind | str, int]]]] = []
    limit = end if end is not None else len(data) - base
    lowest_frame = limit
    p = start
    while p < min(limit, lowest_frame):
        value = _be32(data, base + p)
        if value == 0:
            raw.append((p, "END", 0, []))
            p += 4
            continue
        if dialect.is_token(value):
            kinds = list(dialect.operands[value])
            words = [_be32(data, base + p + 4 + 4 * i) for i in range(len(kinds))]
            ops: list[tuple[OperandKind | str, int]] = list(zip(kinds, words, strict=True))
            if value == 6:
                for i in range(dialect.callback_extra_words.get(words[0], 0)):
                    ops.append(("raw", _be32(data, base + p + 8 + 4 * i)))
            for kind, word in ops:
                if kind == "frame" and word > dialect.max_token:
                    lowest_frame = min(lowest_frame, word) if end is None else lowest_frame
            raw.append((p, "TOKEN", value, ops))
            p += 4 * (1 + len(ops))
            continue
        if start <= value < p:
            # A word pointing back into already-decoded script code: an embedded
            # pointer (e.g. a script-pointer table). Forward pointers cannot be told
            # apart from the first frame record and are treated as frames.
            raw.append((p, "DATA", 0, [("data", value)]))
        else:
            raw.append((p, "FRAME", 0, [("frame", value)]))
            if end is None:
                lowest_frame = min(lowest_frame, value)
        p += 4
    region_end = p
    offsets = [entry[0] for entry in raw]
    labels = {label_name(off): i for i, off in enumerate(offsets)}

    insns: list[Insn] = []
    for off, op, token, ops in raw:
        operands = []
        for kind, word in ops:
            if kind == "label" or (kind == "data" and label_name(word) in labels):
                if label_name(word) not in labels:
                    raise DecodeError(
                        f"jump at 0x{off:X} targets 0x{word:X}, not an instruction boundary"
                    )
                operands.append(Operand("label", label_name(word)))
            else:
                operands.append(Operand(kind, word))  # type: ignore[arg-type]
        insns.append(Insn(op, token, tuple(operands)))  # type: ignore[arg-type]
    return Region(dialect, start, region_end, insns, labels, offsets)


def layout(insns: Sequence[Insn], labels: Mapping[str, int], start: int) -> dict[str, int]:
    """Assign an offset to every label for a contiguous assembly at ``start``."""

    offset = start
    positions: list[int] = []
    for insn in insns:
        positions.append(offset)
        offset += 4 * insn_size(insn)
    return {name: positions[index] for name, index in labels.items()}


def assemble(
    insns: Sequence[Insn],
    labels: Mapping[str, int],
    start: int,
    *,
    frame_map: Callable[[int | str], int] | None = None,
    external_labels: Mapping[str, int] | None = None,
) -> tuple[bytes, dict[str, int]]:
    """Assemble instructions at resource offset ``start``.

    Labels resolve to their new offsets; ``external_labels`` supplies targets
    outside this block. ``frame_map`` translates symbolic or donor frame values.
    Returns the bytes and the resolved label table.
    """

    addresses = layout(insns, labels, start)
    resolved = {**(external_labels or {}), **addresses}
    out = bytearray()
    for insn in insns:
        if insn.op == "TOKEN":
            out += insn.token.to_bytes(4, "big")
        elif insn.op == "END":
            out += b"\0\0\0\0"
        for operand in insn.operands:
            if operand.kind == "label":
                value = resolved[str(operand.value)]
            elif operand.kind == "frame":
                value = frame_map(operand.value) if frame_map else int(operand.value)
            else:
                value = int(operand.value)
            out += (value & 0xFFFFFFFF).to_bytes(4, "big")
    return bytes(out), resolved


def verify(
    blob: bytes,
    start: int,
    dialect: Dialect,
    *,
    expected_phases: int | None = None,
    frame_targets: Iterable[int] | None = None,
) -> Region:
    """Re-decode an assembled block and check its structural invariants.

    ``blob`` is placed at resource offset ``start``. Checks that it decodes to the
    exact length, that every jump lands on an instruction boundary (enforced by
    the decoder), optionally that the phase-terminator count matches and that every
    frame operand is one of ``frame_targets``.
    """

    buffer = bytes(start) + blob
    region = decode_region(buffer, start, dialect, end=start + len(blob))
    if region.end != start + len(blob):
        raise DecodeError("assembled block does not decode to its own length")
    if expected_phases is not None:
        phases = sum(1 for insn in region.insns if insn.op == "END")
        if phases != expected_phases:
            raise DecodeError(f"phase count {phases} != expected {expected_phases}")
    if frame_targets is not None:
        allowed = set(frame_targets)
        for insn in region.insns:
            for operand in insn.operands:
                if operand.kind == "frame" and int(operand.value) not in allowed:
                    raise DecodeError(f"unresolved frame reference 0x{int(operand.value):X}")
    return region
