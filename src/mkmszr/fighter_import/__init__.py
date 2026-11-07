"""MKT -> MKMSZ fighter importer ("recompiler") — Step 0 tooling.

Offline, read-only analysis and assembly primitives. Nothing here patches a ROM:

* :mod:`.script` — shared fighter animation-script grammar (MKT and MKMSZ
  dialects), phase-aware decoder, label-relocating assembler and verifier;
* :mod:`.mkmsz_fighter` — MKMSZ fighter file ``0x87`` model with byte-exact
  re-encoding;
* :mod:`.mkt_fighter` — MKT USA Rev. 2 donor reader (heaps, slot tables, frame
  records, special-move commands);
* :mod:`.translate` — rule-based donor-script fragment translation.
"""

from .mkmsz_fighter import FighterFile
from .mkt_fighter import MktRom
from .script import MKMSZ, MKT, Dialect, Insn, Operand, assemble, decode_region, verify
from .translate import CallbackRule, Policy, UnsupportedToken, translate_fragment

__all__ = [
    "MKMSZ",
    "MKT",
    "CallbackRule",
    "Dialect",
    "FighterFile",
    "Insn",
    "MktRom",
    "Operand",
    "Policy",
    "UnsupportedToken",
    "assemble",
    "decode_region",
    "translate_fragment",
    "verify",
]
