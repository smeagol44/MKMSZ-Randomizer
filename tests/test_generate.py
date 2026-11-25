"""Move-program generator (fighter_import.decompile / generate): owner decision 2026-11-25.

The accepted hand-written programs are the expected outputs. A move the generator reproduces is
pinned as identical; for the others the remaining difference is pinned, so every change to it is
deliberate (a new rule, or a decided MKT-vs-accepted difference)."""

from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path

import pytest

from mkmszr.fighter_import import decompile as dc
from mkmszr.fighter_import import generate as gen

MKT = os.environ.get("MKMSZR_MKT_ROM")
needs_mkt = pytest.mark.skipif(not MKT, reason="needs MKMSZR_MKT_ROM")


@pytest.fixture(scope="module")
def mkt() -> bytes:
    return Path(MKT).read_bytes()


def accepted(fighter: str, move: str) -> list[dict]:
    doc = json.loads(resources.files("mkmszr.fighters.moves").joinpath(f"{fighter}.json").read_text("utf-8"))
    return next(m for m in doc["moves"] if m["name"] == move)["steps"]


def changed(diff: list[str]) -> list[str]:
    return [line for line in diff[2:] if line[:1] in "+-"]


@needs_mkt
def test_decompile_structures_the_torpedo(mkt: bytes) -> None:
    stmts = dc.decompile(mkt, 0x800450D4)
    loops = [s for s in stmts if s.kind == "loop"]
    assert len(loops) == 1
    window = loops[0]
    assert "proc+0x444" in str(window.cond)  # counted down from 0x1A
    calls = [s.target for s in window.body if s.kind == "call"]
    assert calls[:2] == [0x8005A88C, 0x8003E620]  # sleep 1, strike_check_a0
    hit = next(s for s in window.body if s.kind == "if")
    assert [s.target for s in hit.then if s.kind == "call"] == [0x800452C4]  # the carry


@needs_mkt
def test_decompile_folds_a_known_argument(mkt: bytes) -> None:
    """Rayden's lightning routine serves both commands: argument 0 (D,F) and 1 (D,B)."""

    for arg, action in ((0, 0x2B), (1, 0x31)):
        stmts = dc.decompile(mkt, 0x80077DF8, (arg,))
        first = stmts[0]
        assert first.kind == "if" and first.cond.const() == arg
        branch = first.then if arg else first.other
        assert branch[0].kind == "call" and branch[0].args[1].const() == action


@needs_mkt
@pytest.mark.parametrize(
    ("fighter", "fid", "move", "entry", "args"),
    [("reptile", 19, "elbow_dash", 0x800467D0, ())],
)
def test_generated_equals_accepted(mkt: bytes, fighter: str, fid: int, move: str, entry: int, args: tuple) -> None:
    g = gen.Generator(mkt, fid).move(entry, args)
    assert gen.compare(g.steps, accepted(fighter, move)) == []
    assert g.unknown == []


@needs_mkt
def test_invisibility_differs_by_the_owner_length_only(mkt: bytes) -> None:
    g = gen.Generator(mkt, 19).move(0x80073918)
    assert changed(gen.compare(g.steps, accepted("reptile", "invisibility"))) == [
        '-stealth {"ticks":1200}',
        "+stealth {}",
    ]


@needs_mkt
def test_lightning_differs_by_the_projectile_only(mkt: bytes) -> None:
    g = gen.Generator(mkt, 24).move(0x8004FA44)  # the command's own entry (do_special 0x2E)
    diff = changed(gen.compare(g.steps, accepted("rayden", "lightning")))
    assert len(diff) == 1 and diff[0].startswith("-projectile ")
    assert any("projectile process" in u for u in g.unknown)


@needs_mkt
def test_torpedo_differences_from_the_accepted_program_are_pinned(mkt: bytes) -> None:
    """What MKT does that the accepted torpedo does not (owner to decide, 2026-11-25): a random
    start sound 10-12 (the hand reading said 9-11), the speed from the second phase, and after the
    carry or a block Rayden bounces back (slot 0x1A, do_jump(0x33333, -0x6CCCD, 0x5199))."""

    g = gen.Generator(mkt, 24).move(0x8004F3A0)
    assert changed(gen.compare(g.steps, accepted("rayden", "torpedo"))) == [
        '-sound {"sound":{"fighter":9}}',
        '+sound {"sound":{"fighter":10}}',
        '+velocity {"x":524288}',
        '-velocity {"x":524288}',
        "-    stop {}",
        '+    pose {"anim":{"offset":1,"slot":26,"table":0}}',
        '+    jump {"gravity":20889,"until":"landing","x":209715,"y":-445644}',
        "+    end {}",
        "-    stop {}",
        '+    pose {"anim":{"offset":1,"slot":26,"table":0}}',
        '+    jump {"gravity":20889,"until":"landing","x":209715,"y":-445644}',
        "+    end {}",
    ]
    assert any("10..12" in n for n in g.notes)


def test_canonical_ignores_provenance_and_number_spelling() -> None:
    a = [{"op": "sleep", "ticks": 36, "src": {"ticks": "MKT 0x80077F08"}}]
    b = [{"op": "sleep", "ticks": "0x24"}]
    assert gen.compare(a, b) == []
