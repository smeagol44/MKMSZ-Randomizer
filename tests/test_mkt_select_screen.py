"""MKT Character Select screen decoder (web "Swap character" window).

Synthetic tests always run. ROM-backed tests run when ``MKMSZR_MKT_ROM`` names the MKT USA
Rev. 2 ROM; CI has no ROMs, so they are skipped there.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from mkmszr.donors import mkt_select_screen as css
from mkmszr.errors import RomValidationError

# Static evidence for these digests: the colour render matches the framebuffer of a user
# save state at MKT's select screen pixel for pixel, except the live overlays (selection
# box, P1 marker, preview, text) and the RDP dither on the two hidden cells.
RENDER_SHA256 = "a3226e2be5f585e630256980ba02470677657ec46a94e2f683948a1d456e3d0e"
ALL_COLOUR_SHA256 = "29cdb34b4694ecc15470aa938c2634b246152431f7f11bec7162debd67f0b3d1"


def test_packbits_runs_and_literals() -> None:
    # header: codec 0x14, 9 bytes; literal run of 3, repeat 0xAA x4, literal 2
    stream = bytes([0x14, 0, 0, 9, 2, 1, 2, 3, 0xFD, 0xAA, 1, 7, 8])
    assert css._packbits(stream, 0) == bytes([1, 2, 3, 0xAA, 0xAA, 0xAA, 0xAA, 7, 8])
    with pytest.raises(css.SelectScreenError):
        css._packbits(bytes([0x13, 0, 0, 1, 0, 0]), 0)


def test_rgba5551_and_gray() -> None:
    assert css._rgba(0x07C1) == (0, 255, 0, 255)
    assert css._rgba(0x07C0)[3] == 0  # alpha bit clear: transparent
    assert css._rgba(0xFFFF) == (255, 255, 255, 255)
    r, g, b, a = css._gray((255, 0, 0, 255))
    assert r == g == b == 76 and a == 255


def test_render_requires_the_supported_donor() -> None:
    with pytest.raises(RomValidationError):
        css.render(bytes(16))


MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")


@needs_mkt
def test_grid_layout_and_selectable_cells() -> None:
    out = css.render(Path(MKT).read_bytes())
    assert (out["width"], out["height"], len(out["rgba"])) == (320, 240, 320 * 240 * 4)
    cells = out["cells"]
    assert len(cells) == 28 and sum(c["hidden"] for c in cells) == 2
    assert {(c["column"], c["row"]) for c in cells} == {
        (c, r) for r in range(4) for c in range(6)
    } | {(c, 4) for c in range(1, 5)}
    selectable = [c for c in cells if c["fighter"]]
    assert [(c["name"], c["column"], c["row"], c["x"], c["y"]) for c in selectable] == [
        ("SEKTOR", 1, 3, 93, 149)
    ]
    assert hashlib.sha256(out["rgba"]).hexdigest() == RENDER_SHA256


@needs_mkt
def test_only_selectable_portraits_keep_colour() -> None:
    out = css.render(Path(MKT).read_bytes())
    rgba = out["rgba"]

    def colour_share(cell) -> float:
        coloured = total = 0
        # The bottom name plates cover the outer columns of the last row's end cells.
        for y in range(cell["y"] + 2, cell["y"] + 43):
            for x in range(cell["x"] + 10, cell["x"] + 22):
                r, g, b, _ = rgba[4 * (y * 320 + x) : 4 * (y * 320 + x) + 4]
                total += 1
                coloured += not (r == g == b)
        return coloured / total

    for cell in out["cells"]:
        share = colour_share(cell)
        assert share > 0.3 if cell["fighter"] else share == 0, cell["name"]
    colour = css.render(Path(MKT).read_bytes(), {i: "x" for i in range(32)})
    assert hashlib.sha256(colour["rgba"]).hexdigest() == ALL_COLOUR_SHA256
