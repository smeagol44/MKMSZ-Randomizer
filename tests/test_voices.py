"""The generic donor voice rule (Fighter recompiler plan, milestone 4)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import voices

MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")


@needs_mkt
def test_reproduces_sektors_accepted_voice_set() -> None:
    vs = voices.voice_set(Path(MKT).read_bytes(), 7)  # type: ignore[arg-type]
    # sektor_build v14-v17 (Runtime-confirmed): whooshes, face hits without the duplicate 63
    assert vs.category == {0: 416, 1: 417, 2: 62, 3: 64, 4: 62, 5: 64, 6: 126, 7: 127,
                           8: None, 9: None, 10: None, 11: None}  # fmt: skip


@needs_mkt
def test_reptile_voice_set() -> None:
    vs = voices.voice_set(Path(MKT).read_bytes(), 19)  # type: ignore[arg-type]
    assert vs.category == {0: 78, 1: 79, 2: 53, 3: 55, 4: 53, 5: 55, 6: 120, 7: 120,
                           8: 92, 9: 41, 10: None, 11: None}  # fmt: skip
