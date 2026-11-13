"""Generic special-command lowering (fighter_import.commands)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mkmszr.fighter_import import commands as cmds
from mkmszr.fighter_import import components
from mkmszr.fighter_import import description as fd
from mkmszr.fighter_import.mipsdis import decode

MKT = os.environ.get("MKMSZR_MKT_ROM")
CLEAN = os.environ.get("MKMSZR_CLEAN_ROM")
needs_roms = pytest.mark.skipif(not (CLEAN and MKT), reason="needs MKMSZR_CLEAN_ROM and MKMSZR_MKT_ROM")
ARENA = 0xA01AF420


def _reptile():
    mkt, clean = Path(MKT).read_bytes(), Path(CLEAN).read_bytes()
    d = fd.load("reptile")
    moves, _ = components.load_programs("reptile")
    commands = cmds.donor_commands(mkt, moves, d.commands)
    own = {"elbow_dash": (5, 0xA01B0000, 0xA01B0010)}  # Ice Shatter has no record: own special
    return clean, commands, cmds.lower(clean, commands, set(d.remove_commands), ARENA, ARENA + 0x100, own)


@needs_roms
def test_host_tables_are_stock() -> None:
    clean = Path(CLEAN).read_bytes()
    for name, va in cmds.HOST_POWERS.items():
        rec = cmds.record_at(clean, va, cmds.VA_TO_ROM)
        assert rec[0:2] != b"\0\0" and 0x80000000 < int.from_bytes(rec[12:16], "big") < 0x80100000, name
    for table in cmds.HOST_TABLES:
        end = table.va + cmds.RECORD * table.capacity - cmds.VA_TO_ROM
        assert clean[end : end + 2] == b"\0\0", table.button  # sentinel after the last record
        lui, addiu = (int.from_bytes(clean[x - cmds.VA_TO_ROM : x - cmds.VA_TO_ROM + 4], "big") for x in table.load)
        assert ((lui & 0xFFFF) << 16) + ((addiu & 0xFFFF) ^ 0x8000) - 0x8000 == table.va


@needs_roms
def test_reptile_tables() -> None:
    _, commands, low = _reptile()
    by_name = {c.name: c for c in commands}
    assert by_name["forceball_fast"].held == by_name["forceball_slow"].held == 0x90
    assert by_name["elbow_dash"].calls == "ice_shatter"
    assert list(low.moved) == ["HP"] and low.moved["HP"] == ARENA
    acts = {b: [int.from_bytes(r[12:16], "big") for r in recs] for b, recs in low.tables.items()}
    assert acts["HP"] == [0x80049CB0, 0x80049C34, 0x8003CF8C, 0x80049BE8, 0x8004BD28]  # ff, acid, fs, spine, polar
    assert acts["LP"] == [0x80049CB0, 0x8003CF8C] and acts["HK"] == [0x8005A7B4]
    assert acts["LK"] == [0xA01B0010]  # Reverse Elbow (B,F + LK), its own special
    lk = low.tables["LK"][0]
    assert lk[4:12] == bytes.fromhex("00000005a01b0000") and lk[0x12:0x16] == bytes.fromhex("00090008")
    hp = low.tables["HP"]
    assert hp[1][0x12:0x16] == bytes.fromhex("00090009")  # Acid Spit: F,F (newest first)
    assert low.tables["HK"][0][0x12:0x16] == bytes.fromhex("00070006")  # Invisibility: U,D
    # Held-check stubs: both buttons -> the stock condition, else the parser from the next record.
    stub = int.from_bytes(hp[0][8:12], "big")
    code = [decode(int.from_bytes(low.stubs[i : i + 4], "big"), 0).text for i in range(0, len(low.stubs), 4)]
    assert stub == ARENA + 0x100 and "andi t0, t0, 0x90" in code[2]
    text = " ".join(code[:16])
    assert "addiu t9, t9, -23388" in text  # 0x8004A4A4, Directional Ice down's condition
    assert "lui a0, 0xA01B" in text and "addiu t9, t9, -24352" in text  # next record, parser 0x8004A0E0


@needs_roms
def test_install_writes_tables_and_repoints_hp(tmp_path: Path) -> None:
    clean, _, low = _reptile()
    rom = bytearray(clean) + bytearray(b"\xff" * 0x1000)
    cmds.install(rom, clean, low, len(clean), ARENA)
    assert rom[0xB1B68 + cmds.RECORD : 0xB1B6A + cmds.RECORD] == b"\0\0"  # LK: the elbow, then the sentinel
    hp_lui = 0x8003C88C - cmds.VA_TO_ROM
    assert rom[hp_lui + 2 : hp_lui + 4] == b"\xa0\x1b" and rom[hp_lui + 6 : hp_lui + 8] == b"\xf4\x20"
    assert rom[len(clean) : len(clean) + cmds.RECORD] == low.tables["HP"][0]


@needs_roms
def test_commandless_power_needs_its_own_special() -> None:
    mkt, clean = Path(MKT).read_bytes(), Path(CLEAN).read_bytes()
    d = fd.load("reptile")
    moves, _ = components.load_programs("reptile")
    commands = cmds.donor_commands(mkt, moves, d.commands)
    with pytest.raises(cmds.CommandError, match="own special"):
        cmds.lower(clean, commands, set(d.remove_commands), ARENA, ARENA + 0x100)


def test_description_rejects_bad_commands() -> None:
    import copy
    import json
    from importlib import resources

    raw = json.loads(resources.files("mkmszr.fighters").joinpath("reptile.json").read_text())
    for change, message in (
        (lambda d: d["commands"].update(acid_spit="ice_shower"), "commands"),
        (lambda d: d["commands"].update(invisibility="ice_blast"), "one move"),
        (lambda d: d.update(remove_commands=["ice_blast"]), "one move"),
        (lambda d: d.update(remove_commands=["slide"]), "remove_commands"),
    ):
        data = copy.deepcopy(raw)
        change(data)
        with pytest.raises(fd.DescriptionError, match=message):
            fd.validate(data)


@needs_roms
def test_rayden_lightning_goes_to_its_event_button() -> None:
    # The MKT record has masks 0xFC but sits only in the LP event (grid event 1): the move
    # program's buttons place it, and the host record carries them.
    clean, mkt = Path(CLEAN).read_bytes(), Path(MKT).read_bytes()  # type: ignore[arg-type]
    moves, _ = components.load_programs("rayden")
    found = cmds.donor_commands(mkt, moves, fd.load("rayden").commands)
    assert [(c.name, c.calls, c.buttons) for c in found] == [("lightning", "ice_blast", 0x80)]
    low = cmds.lower(clean, found, set(), 0xA01AF420, 0xA01AF520)
    lp = low.tables["LP"]
    assert len(lp) == 2 and lp[0][:4] == bytes.fromhex("00800080")
    assert all(len(low.tables[b]) == n for b, n in (("HP", 3), ("LK", 1), ("HK", 1)))
