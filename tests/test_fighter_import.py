"""Tests for the Step 0 fighter importer tooling.

Synthetic tests always run. ROM-backed acceptance tests run when the supported
clean ROMs are supplied through ``MKMSZR_CLEAN_ROM`` (MKMSZ USA Rev. 0) and
``MKMSZR_MKT_ROM`` (MKT USA Rev. 2); they are skipped otherwise, because CI has no
ROMs.
"""

from __future__ import annotations

import hashlib
import os
from collections import Counter
from pathlib import Path

import pytest

from mkmszr.fighter_import import (
    MKMSZ,
    MKT,
    CallbackRule,
    FighterFile,
    Insn,
    MktRom,
    Operand,
    Policy,
    UnsupportedToken,
    assemble,
    decode_region,
    translate_fragment,
    verify,
)
from mkmszr.fighter_import.script import DecodeError
from mkmszr.rom import CLEAN_SHA256


def words(*values: int) -> bytes:
    return b"".join(v.to_bytes(4, "big") for v in values)


# ---------------------------------------------------------------- synthetic


def test_round_trip_and_phase_preservation() -> None:
    # Phase 1: frame, flip, frame, END; phase 2: callback 1 (+rate word), frame, loop.
    body = words(0x2000, 2, 0x2010, 0, 6, 1, 3, 0x2020, 1, 0x20)
    data = bytes(0x20) + body
    region = decode_region(data, 0x20, MKMSZ, end=0x20 + len(body))
    assert [i.op for i in region.insns].count("END") == 1
    assert region.insns[4] == Insn("TOKEN", 6, (Operand("raw", 1), Operand("raw", 3)))
    blob, _ = assemble(region.insns, region.labels, 0x20)
    assert blob == body


def test_label_relocation_after_insertion() -> None:
    body = words(0x2000, 0x2010, 1, 0x24)  # frame, frame, jump back to second frame
    region = decode_region(bytes(0x20) + body, 0x20, MKMSZ, end=0x30)
    insns = list(region.insns)
    labels = dict(region.labels)
    insns.insert(0, Insn("TOKEN", 2))  # insert a flip before everything
    labels = {name: index + 1 for name, index in labels.items()}
    blob, resolved = assemble(insns, labels, 0x20)
    assert blob == words(2, 0x2000, 0x2010, 1, 0x28)
    assert resolved["L_00024"] == 0x28
    verify(blob, 0x20, MKMSZ, frame_targets={0x2000, 0x2010})


def test_jump_into_operand_is_rejected() -> None:
    body = words(6, 1, 3, 1, 0x28)  # jump targets the callback's extra word
    with pytest.raises(DecodeError):
        decode_region(bytes(0x20) + body, 0x20, MKMSZ, end=0x34)


def test_dialects_differ_on_token_16_and_callback_words() -> None:
    body = words(16, 0x3000, 0x3004)
    assert decode_region(bytes(0x20) + body, 0x20, MKMSZ, end=0x2C).insns[0].token == 16
    # In MKT 16 is not a token, so the words are frames.
    assert [i.op for i in decode_region(bytes(0x20) + body, 0x20, MKT, end=0x2C).insns] == [
        "FRAME",
        "FRAME",
        "FRAME",
    ]
    # MKT callback 1 consumes no extra word.
    mkt = decode_region(bytes(0x20) + words(6, 1, 0x3000), 0x20, MKT, end=0x2C)
    assert [i.op for i in mkt.insns] == ["TOKEN", "FRAME"]


def test_translation_rules() -> None:
    # MKT: frame, footstep callback 8, Cyrax branch (ID 8), sound, palette, frame, loop.
    body = words(0x2000, 6, 8, 8, 8, 0x20, 7, 5, 13, 0x2010, 1, 0x20)
    region = decode_region(bytes(0x20) + body, 0x20, MKT, end=0x20 + len(body))
    policy = Policy(donor_fighter=7, callbacks={8: CallbackRule(None, reason="footstep")})
    fragment = translate_fragment(region, 0x20, policy)
    blob, _ = assemble(fragment.insns, fragment.labels, 0x100)
    assert blob == words(0x2000, 0x2010, 1, 0x100)
    assert len(fragment.dropped) == 4
    with pytest.raises(UnsupportedToken):
        translate_fragment(region, 0x20, Policy(donor_fighter=7))  # callback 8 unmapped
    with pytest.raises(ValueError):
        CallbackRule(2)  # MKMSZ callback 2 needs its SFX operand


# ---------------------------------------------------------------- ROM-backed


def _rom(variable: str, sha256: str) -> bytes:
    path = os.environ.get(variable)
    if not path or not Path(path).is_file():
        pytest.skip(f"{variable} not set")
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != sha256:
        pytest.skip(f"{variable} is not the supported ROM")
    return data


@pytest.fixture(scope="module")
def clean() -> bytes:
    return _rom("MKMSZR_CLEAN_ROM", CLEAN_SHA256)


@pytest.fixture(scope="module")
def mkt() -> MktRom:
    from mkmszr.donors.mkt_n64 import MKT_N64_REV2_SHA256

    return MktRom(_rom("MKMSZR_MKT_ROM", MKT_N64_REV2_SHA256))


def test_stock_file87_round_trip_is_byte_identical(clean: bytes) -> None:
    fighter = FighterFile.from_rom(clean)
    assert len(fighter.data) == 0x459E0
    assert fighter.encode() == fighter.data
    counts = Counter(i.token for i in fighter.region.insns if i.op == "TOKEN")
    assert set(counts) == {1, 2, 3, 5, 6, 10, 11, 16}
    assert fighter.slot(0, 0x2B).value == 0xEE8  # ordinary Run
    assert fighter.slot(0, 0x46) == fighter.slot(1, 0x05)  # table-0 alias rule


def test_sektor_donor_tables(mkt: MktRom) -> None:
    assert mkt.name(7) == "SEKTOR"
    assert mkt.heap(7) == (0x8881C0, 0x8E79B0)
    assert mkt.dictionary(7) == (0x906A90, 0x906B90)
    assert mkt.dictionary(19) == (0x6B8550, 0x6B8650)  # male-ninja dictionary
    assert mkt.table0(7)[0x4A] == 0x1444  # Run
    (rocket,) = mkt.frame_parts(7, 0x2668)  # ROCKETD1
    assert (rocket.width, rocket.height, rocket.anchor_x, rocket.anchor_y) == (39, 9, 26, 3)
    assert rocket.image == 0x49700 and rocket.codec == 16
    for fighter in range(32):  # every fighter heap decodes as a script region
        assert mkt.script_region(fighter).insns


def test_sektor_special_commands(mkt: MktRom) -> None:
    inline = {(h.event, c.right): c for h in mkt.handlers(7) for c in h.inline}
    assert inline[(1, (9, 9))].special_id == 9 and inline[(1, (9, 9))].target == 0x8007BF84
    assert inline[(1, (9, 8, 8))].special_id == 51
    assert inline[(0, (8, 7, 9))].special_id == 10 and inline[(0, (8, 7, 9))].mask == 0x10
    teleport = inline[(4, (9, 9))]
    assert teleport.mask == 0x40 and teleport.target == 0x80045050 and teleport.argument == 8
    reptile = mkt.record(0x800ACA5C)
    assert reptile.masks == (0x40, 0x40) and reptile.right == (9, 8)
    assert reptile.action == 0x8004F2C0


def test_sektor_run_translation_reproduces_v05_live_script(mkt: MktRom) -> None:
    """Donor Run -> MKMSZ Run equals the Runtime-confirmed v05 live script.

    v05 (SHA-256 3073bd0b...4f5363) stores the six RBRUN poses at file-0x87
    entries 0x495F0..0x4A0E8 followed by ``1, +0xEE8``. The frame map supplies
    those v05 entry offsets; the test checks pose order, callback removal and
    loop-label placement, not asset generation.
    """

    region = mkt.script_region(7)
    policy = Policy(donor_fighter=7, callbacks={8: CallbackRule(None, reason="footstep")})
    fragment = translate_fragment(region, 0x1444, policy)
    donor_frames = [0x2708, 0x271C, 0x2730, 0x2744, 0x2758, 0x276C]
    v05_entries = [0x495F0, 0x4981C, 0x49A3C, 0x49C3C, 0x49E8C, 0x4A0E8]
    frame_map = dict(zip(donor_frames, v05_entries, strict=True))
    blob, _ = assemble(fragment.insns, fragment.labels, 0xEE8, frame_map=frame_map.__getitem__)
    assert blob == words(*v05_entries, 1, 0xEE8)
    verify(blob, 0xEE8, MKMSZ, frame_targets=v05_entries)
    assert fragment.dropped == ["callback 8: footstep"]
