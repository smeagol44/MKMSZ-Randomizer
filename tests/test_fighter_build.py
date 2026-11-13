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
