"""MKT -> MKMSZ animation-script translation (one script fragment at a time).

Rules (Wiki ``MKT-Adapter-Primitives`` -> Animation script grammar translation):

* tokens 1, 2, 3, 4, 5, 9, 12, 14, frames and ``0`` are identical in both
  grammars; jumps become labels and frames go through the caller's frame map;
* token 6 (callback) indices are game-local and are translated only through an
  explicit :class:`CallbackRule`; an unmapped callback is an error;
* token 8 (fighter-ID branch) is folded at import time for the known donor ID;
* tokens 7/15 (donor sound) and 13 (next-frame palette) are dropped unless a
  policy maps them; MKMSZ ignores or no-ops them anyway;
* tokens 10 and 11 need dedicated adapters (partner placement, helper actor
  palette ownership) and are rejected here.

Translation never copies a donor callback index numerically. The caller is also
responsible for fitting the result into the host slot's phase layout.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .script import MKMSZ, Insn, Operand, Region, label_name


class UnsupportedToken(ValueError):
    pass


@dataclass(frozen=True)
class CallbackRule:
    """Translation of one donor callback: drop it, or emit an MKMSZ callback."""

    target: int | None  # MKMSZ callback index, or None to drop
    extra_words: tuple[int, ...] = ()
    reason: str = ""

    def __post_init__(self) -> None:
        if self.target is not None:
            expected = MKMSZ.callback_extra_words.get(self.target, 0)
            if len(self.extra_words) != expected:
                raise ValueError(
                    f"MKMSZ callback {self.target} takes {expected} extra word(s), "
                    f"got {len(self.extra_words)}"
                )


@dataclass(frozen=True)
class Policy:
    donor_fighter: int
    callbacks: Mapping[int, CallbackRule] = field(default_factory=dict)
    drop_sound_tokens: bool = True
    drop_palette_token: bool = True


@dataclass
class Fragment:
    insns: list[Insn]
    labels: dict[str, int]
    root: str
    dropped: list[str]


def fragment(region: Region, root: int) -> tuple[int, int]:
    """Instruction index range [first, last] from ``root`` to the first END or jump."""

    first = region.index_of(root)
    index = first
    while True:
        insn = region.insns[index]
        if insn.op == "END" or (insn.op == "TOKEN" and insn.token == 1):
            return first, index
        index += 1
        if index >= len(region.insns):
            raise ValueError("script fragment runs past the decoded region")


def translate_fragment(region: Region, root: int, policy: Policy) -> Fragment:
    """Translate the donor fragment starting at ``root`` into MKMSZ instructions."""

    if region.dialect.name != "mkt":
        raise ValueError("translate_fragment expects an MKT-dialect region")
    first, last = fragment(region, root)
    inside = {label_name(region.offsets[i]) for i in range(first, last + 1)}
    out: list[Insn] = []
    labels: dict[str, int] = {}
    dropped: list[str] = []
    for index in range(first, last + 1):
        name = label_name(region.offsets[index])
        insn = region.insns[index]
        # A label points at the next emitted instruction (dropped units are skipped).
        labels[name] = len(out)
        if insn.op in ("END", "FRAME"):
            out.append(insn)
            continue
        if insn.op == "DATA":
            raise UnsupportedToken(f"embedded data word at 0x{region.offsets[index]:X}")
        token = insn.token
        if token in (1, 2, 3, 4, 5, 9, 12, 14):
            for operand in insn.operands:
                if operand.kind == "label" and operand.value not in inside:
                    raise UnsupportedToken(
                        f"jump at 0x{region.offsets[index]:X} leaves the fragment"
                    )
            out.append(insn)
        elif token == 6:
            index_value = int(insn.operands[0].value)
            rule = policy.callbacks.get(index_value)
            if rule is None:
                raise UnsupportedToken(f"donor callback {index_value} has no translation rule")
            if rule.target is None:
                dropped.append(f"callback {index_value}: {rule.reason or 'dropped'}")
            else:
                operands = (Operand("raw", rule.target),) + tuple(
                    Operand("raw", w) for w in rule.extra_words
                )
                out.append(Insn("TOKEN", 6, operands))
        elif token == 8:
            fighter, target = insn.operands
            if int(fighter.value) == policy.donor_fighter:
                if target.value not in inside:
                    raise UnsupportedToken("folded fighter branch leaves the fragment")
                out.append(Insn("TOKEN", 1, (target,)))
            else:
                dropped.append(f"fighter-{int(fighter.value)} branch folded away")
        elif token in (7, 15) and policy.drop_sound_tokens:
            dropped.append(f"sound token {token} dropped")
        elif token == 13 and policy.drop_palette_token:
            dropped.append("next-frame palette token dropped")
        else:
            raise UnsupportedToken(f"donor token {token} requires a dedicated adapter")
    root_label = label_name(root)
    return Fragment(out, labels, root_label, dropped)
