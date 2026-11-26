"""Described fighters built generically (fighter_import.fighter_build), milestone 4 step 5 / 5."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import fighter_build as fb

CLEAN, MKT = os.environ.get("MKMSZR_CLEAN_ROM"), os.environ.get("MKMSZR_MKT_ROM")
needs_roms = pytest.mark.skipif(not (CLEAN and MKT), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM")
# The owner-accepted Reptile specials proof v22 (v21 + help text): its fighter file, and its
# payload (linked at fb.LINK_VA) plus one fix since: the throw helper ends when a hit
# interrupts the throw (composition v01 report; v22's payload was
# deb21523c9bf69800bcdb03f793bedda0e95655b78696954e809b031df8b34c8, reproduced byte for byte
# before the fix).
V22_PAYLOAD_SHA256 = "bdff766ee9a94fd7d2c869029f9167ca89066db0497d81727a395a2737a12a2b"
# Second fix since: the forceballs' knockback reaction morphs the victim first, as the stock
# launch reaction does (composition v02 crash on a Temple MONK3). Without the morph the build
# still reproduces V22_PAYLOAD_SHA256.
PAYLOAD_SHA256 = "9b8f6f00e04dd1889dd41550b4edf8a6801d5c8442fbdf17f1e5d89b3b51f1d6"
V22_FILE87_SHA256 = "71bf66f35be7a6fe4c65cfddd318e30a83b892693cfe6dd0bb806ef8733a32be"


@pytest.fixture(scope="module")
def roms() -> tuple[bytes, bytes]:
    return Path(CLEAN).read_bytes(), Path(MKT).read_bytes()


@needs_roms
def test_generic_build_reproduces_the_accepted_reptile(roms: tuple[bytes, bytes]) -> None:
    built = fb.build(*roms, "reptile")
    assert hashlib.sha256(built.payload).hexdigest() == PAYLOAD_SHA256
    assert hashlib.sha256(built.file87).hexdigest() == V22_FILE87_SHA256
    assert built.selectors == {"forceball_fast": 3, "forceball_slow": 4, "acid_spit": 5, "elbow_dash": 6,
                               "invisibility": 7}  # fmt: skip
    assert sorted(built.reactions.values()) == [0x23, 0x2B, 0x4C]


@needs_roms
def test_reptile_production_placement(roms: tuple[bytes, bytes]) -> None:
    clean, mkt = roms
    made = fb.production(clean, mkt, "reptile")
    m = made.manifest
    assert len(made.rom) == fb.OUTPUT_SIZE
    assert m["slack"] > 0 and m["jal_sites"] == {}
    assert len(m["refs"]) == 17  # transfer 3-7, reactions 0x23/0x2B/0x4C, LP/LK/HK records, HP pointer
    assert (fb.FIXED_VA & ~0x20000000) + m["fixed_len"] <= fb.POOL_END
    assert fb.TAIL[0] == m["file87_rom"] and m["samples_end"] <= fb.TAIL[1]
    stock = (0x748920, 0x748920 + 0x459E0)  # Sub-Zero's file and the proof scratch stay clean
    assert made.rom[stock[0] : stock[1]] == clean[stock[0] : stock[1]]
    assert made.rom[fb.SCRATCH_ROM : fb.SCRATCH_ROM + fb.PAYLOAD_LIMIT] == clean[fb.SCRATCH_ROM : fb.SCRATCH_ROM + fb.PAYLOAD_LIMIT]
    hp_lui, hp_low = (int.from_bytes(made.rom[o : o + 4], "big") for o in (0x3D48C, 0x3D490))
    assert (hp_lui & 0xFFFF, hp_low) == (0xA01B, 0x8C8430F0)  # the HP table through the pointer word


@needs_roms
def test_without_the_morph_the_build_is_the_accepted_one(roms: tuple[bytes, bytes],
                                                         monkeypatch: pytest.MonkeyPatch) -> None:  # fmt: skip
    from mkmszr.fighter_import import lower_projectile as lp

    spec = {k: v for k, v in lp.REACTION_LOWERING["knockback_arc"].items() if k != "morph"}
    monkeypatch.setitem(lp.REACTION_LOWERING, "knockback_arc", spec)
    assert hashlib.sha256(fb.build(*roms, "reptile").payload).hexdigest() == V22_PAYLOAD_SHA256


@needs_roms
def test_rayden_torpedo_flight_frames_and_carry(roms: tuple[bytes, bytes]) -> None:
    """Specials proof v03: the torpedo plays slot 0's two phases and holds the flat frame (MKT
    0x2100); its strike selects the carry reaction, whose table entry is the payload routine."""

    from mkmszr.fighter_import import lower_projectile as lp

    clean, _ = roms
    built = fb.build(*roms, "rayden")
    body = fb.body_build.build_body(fb.fd.load("rayden"), clean, roms[1], fb.body_build.Extras())
    at, n = body.script_offsets[0x40], body.script_words[0x40]
    words = [int.from_bytes(built.file87[at + 4 * i : at + 4 * i + 4], "big") for i in range(n)]
    assert n == 6 and words[2] == words[5] == 0  # two phases of two frames, nothing borrowed
    slot = built.reactions["torpedo_carry"]
    (_, records), = built.report["strike_records"]
    assert records[0][1][8] == slot  # the strike's reaction byte
    entry = lp.REACTION_TABLE - 0x7FFFF400 + 4 * slot
    target = int.from_bytes(built.rom[entry : entry + 4], "big")
    assert built.link_va <= target < built.link_va + len(built.payload)
    # MKT's 26-tick window (13 host ticks; the owner's 40 of v05-v08 dropped in v09: pure MKT);
    # no Ice cost for a movement ability (owner rule; Ice Clone's slot would charge 0x60);
    # Lightning keeps Ice Blast's 0x20
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    assert 0x2413000D in ws and 0x24130014 not in ws  # addiu s3, zero, 13
    # v13 (owner save state): the lightning burst is placed by MKT's flip alone (one facing
    # toggle); impact_mirror mirrors its frames in the art instead (v10-v12 flipped the actor
    # back, mirroring it around an anchor outside its box); the torpedo's three jumps (bounce,
    # bounce, drop) take the air map
    assert ws.count(0x012A4826) == 1  # xor t1, t1, t2 (the facing bit)
    assert ws.count(0x2739B05C) == 5  # input map: two begins without a turn, three jumps
    # v11-v12 (owner screenshots, Wind): the burst goes to the enemy hit (the player's +0x640,
    # set by the collision core), at its whole position: path, path position, x, z; v15: the
    # bolt's own height kept (impact_keep_y), not the enemy's feet
    i = next(k for k, w in enumerate(ws) if w == 0x8D081AC0 and ws[k + 1] == 0x8D080640)
    copies = [w for w in ws[i : i + 20] if (w >> 16) == 0x8D09]  # lw t1, field(t0)
    assert [w & 0xFFFF for w in copies] == [0xDC, 0xE0, 0x2C, 0x34]
    assert 0x2529FFA0 not in ws and 0x2529FFE0 in ws  # addiu t1, t1, -0x60 / -0x20


@needs_roms
def test_a_pose_past_its_script_is_refused(roms: tuple[bytes, bytes], monkeypatch: pytest.MonkeyPatch) -> None:
    from mkmszr.fighter_import import components

    real = components.load_programs

    def with_bad_pose(name: str):
        moves, gaps = real(name)
        for m in moves:
            if m.name == "torpedo":
                m.steps.insert(5, {"op": "pose", "anim": {"table": 1, "slot": 0, "offset": 6}})
        return moves, gaps

    monkeypatch.setattr(components, "load_programs", with_bad_pose)
    with pytest.raises(fb.BuildError, match="past the 6 words"):
        fb.build(*roms, "rayden")


@needs_roms
def test_impact_mirror_uses_one_axis_for_the_animation(roms: tuple[bytes, bytes]) -> None:
    """v15 (owner): every impact frame mirrors around the same anchor-relative column, so the
    frames keep their places relative to each other (v14's per-frame cores made them jump)."""

    from mkmszr.fighter_import import lower_projectile as lp
    from mkmszr.fighter_import.body_build import Donor

    donor = Donor(roms[1], 24)
    rels = list(dict.fromkeys(lp.donor_part(donor, {"table": 0, "slot": 67, "part": 4}).frames))
    axis = lp.mirror_axis(donor, rels)
    for rel in rels:
        f = donor.frame(rel)
        w, stride = f["w"], f["stride"]
        plain, mirrored = lp._frame(donor, rel, 32), lp._frame(donor, rel, 32, axis)
        for y in range(f["eh"]):
            row = plain.indices[y * stride : y * stride + w]
            assert mirrored.indices[y * stride : y * stride + w] == row[::-1]
        # column c sat at c - x; its mirror lands at 2 * axis - (c - x)
        for c in (0, w - 1):
            assert (w - 1 - c) - mirrored.anchor_x == 2 * axis - (c - plain.anchor_x)


@needs_roms
def test_shock_stagger_starts_the_blink_then_the_stumble(roms: tuple[bytes, bytes]) -> None:
    """v16 (owner: MKT staggers and blinks cyan): the lightning's reaction entry starts the blink
    helper (process 0x100) and goes on into the lifted host stumble."""

    from mkmszr.fighter_import import lower_projectile as lp

    built = fb.build(*roms, "rayden")
    slot = built.reactions["projectile (0, 67, 3)"]
    o = lp.REACTION_TABLE - 0x7FFFF400 + 4 * slot
    entry = int.from_bytes(built.rom[o : o + 4], "big")
    k = (entry - built.link_va) // 4
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    head = ws[k : k + 30]
    assert 0x24040100 in head  # addiu a0, zero, 0x100: the blink process
    assert 0xAC5006F4 in head  # sw s0, 0x6F4(v0): the victim's controller as its argument
    assert any((w >> 26) == 2 for w in head)  # j: on into the stumble, as the reaction itself


@needs_roms
def test_somersault_anchors_move_to_the_body(roms: tuple[bytes, bytes]) -> None:
    """v16 (owner: a mid-air turn shifted Rayden): his somersault anchors move 21 px; Reptile's
    (2 px off) stay."""

    clean, mkt = roms
    for name, expected in (("rayden", ["SOMERSAULT slot 0x1A: anchors moved 21 px to the body's centre"]),
                           ("reptile", [])):  # fmt: skip
        body = fb.body_build.build_body(fb.fd.load(name), clean, mkt, fb.body_build.Extras())
        assert [line for line in body.log if "SOMERSAULT" in line] == expected
