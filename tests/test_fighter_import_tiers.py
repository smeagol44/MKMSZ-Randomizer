"""Sektor R4 tiers and costs: payload conditions vs a model, stub charges, stock edits."""

from __future__ import annotations

import itertools

import pytest
from mips_eval import Machine

from mkmszr.fighter_import.actions import robo_tracker as trk
from mkmszr.fighter_import.actions import sektor_tiers as st
from mkmszr.fighter_import.mips import Assembler

BASE = 0xA0100000
ACTOR, CTRL, CUR = 0x80300000, 0x80310000, 0x80320000
RET = 0x80001000


def _store_half(m: Machine, address: int, value: int) -> None:
    word = m.load(address & ~3)
    shift = 16 if address & 2 == 0 else 0
    m.store(address & ~3, (word & ~(0xFFFF << shift)) | ((value & 0xFFFF) << shift))


def _machine(code: bytes, s: dict) -> Machine:
    m = Machine(code, BASE)
    m.store(st.PLAYER_ACTOR, ACTOR)
    m.store(st.PLAYER_CTRL, CTRL)
    m.store(st.CURRENT_CTRL, CUR)
    m.store(ACTOR + 0x18, s["vy"])
    m.store(ACTOR + 0x30, s["y"])
    m.store(ACTOR + 0xDC, s["dc"])
    m.store(CTRL + 0x6E0, ACTOR)
    m.store(CTRL + 0x6B4, s["floor"])
    _store_half(m, CTRL + 0x6B0, s["attach"])
    _store_half(m, CTRL + st.CTRL_ICE, s["ice"])
    _store_half(m, CUR + 0x6AA, s["action"])
    _store_half(m, st.SPECIAL_FLAG, s["flag"])
    m.store(st.CURRENT_XP, 1234)
    for gate, n in s["gates"].items():
        m.store(gate, st.SLTI_V0 | n)
    return m


def _run(m: Machine, entry: int, s: dict):
    calls = []
    m.regs[31], m.regs[29] = RET, 0x80200000
    pc = entry
    while True:
        stop = m.run(pc)
        if stop.kind != "call":
            return stop, calls
        calls.append(stop.target & 0x1FFFFFFF)
        if stop.target & 0x1FFFFFFF == st.F_FIND_CLASS & 0x1FFFFFFF:
            assert (m.regs[4], m.regs[5]) == (st.PROJECTILE_CLASS, 0xFFFF)
            m.regs[2] = s["projectile"]
        elif stop.target & 0x1FFFFFFF == st.F_TIER & 0x1FFFFFFF:
            assert m.regs[4] == 1234
            m.regs[2] = s["tier"]
        else:
            raise AssertionError(hex(stop.target))
        pc = stop.resume


def _model(s: dict, gate: int, cost: int) -> int:
    ok = (
        s["vy"] <= st.FALL_SPEED_LIMIT
        and not s["attach"]
        and not s["dc"]
        and s["ice"] >= cost
        and s["y"] >= s["floor"]
        and s["action"] != st.BUSY_ACTION
        and not s["projectile"]
        and not s["flag"]
        and s["tier"] >= s["gates"][gate]
    )
    return 0x8000 if ok else 0x4000


STATES = {
    "vy": (0, st.FALL_SPEED_LIMIT + 1),
    "attach": (0, 1),
    "dc": (0, 5),
    "ice": (0x1F, 0x30, 0x3F, 0x40, 0x5F, 0x60, 0xA6),
    "y": (0xC000, 0xB000),
    "action": (0, st.BUSY_ACTION),
    "projectile": (0, 0x80400000),
    "flag": (0, 1),
    "tier": (0, 3, 4, 6, 9),
}


@pytest.mark.parametrize(("label", "gate", "cost"), [
    ("tier_double", st.SHATTER_GATE, 0x30), ("tier_homing", st.AIR_ICE_GATE, 0x40)])  # fmt: skip
def test_gate_condition_matches_the_model(label: str, gate: int, cost: int) -> None:
    a = Assembler(BASE, cached_calls=True)
    labels = st.emit_conditions(a)
    assert label in labels.values()
    code = a.link()
    keys = list(STATES)
    count = 0
    for values in itertools.product(*(STATES[k] for k in keys)):
        s = dict(zip(keys, values), floor=0xC000)
        if sum(1 for k in ("vy", "attach", "dc", "action", "projectile", "flag") if s[k]) > 1:
            continue  # one refusal reason at a time keeps the sweep small
        for n in (4, 6):  # the shuffle may move either slot
            s["gates"] = {st.SHATTER_GATE: n, st.AIR_ICE_GATE: 10 - n}
            m = _machine(code, s)
            stop, _calls = _run(m, a.labels[label], s)
            assert stop.kind == "return" and stop.target == RET
            assert m.regs[2] == _model(s, gate, cost), s
            assert m.regs[29] == 0x80200000
            count += 1
    assert count == 980


def test_ground_condition_refuses_airborne_else_tail_calls_the_stock_condition() -> None:
    a = Assembler(BASE, cached_calls=True)
    st.emit_conditions(a)
    code = a.link()
    base = {
        "vy": 0,
        "attach": 0,
        "dc": 0,
        "ice": 0x20,
        "action": 0,
        "flag": 0,
        "floor": 0xC000,
        "gates": {},
    }
    m = _machine(code, dict(base, y=0xB000))
    stop, _ = _run(m, a.labels["tier_straight"], {})
    assert (stop.kind, stop.target, m.regs[2]) == ("return", RET, 0x4000)
    m = _machine(code, dict(base, y=0xC000))
    stop, _ = _run(m, a.labels["tier_straight"], {})
    assert stop.target == st.LP_ICE_CONDITION and m.regs[31] == RET  # ra intact


def test_stubs_charge_the_extra_cost_then_enter_the_ice_callback() -> None:
    ice_cb = 0x80049C34
    for extra in (None, st.EXTRA_COST):
        a = Assembler(BASE, cached_calls=True)
        trk.emit_command_stubs(a, ice_cb, 459, extra_costs=extra)
        a.label("play")
        a.jr_ra()
        a.nop()
        trk.emit_data(a, [0] * trk.DIRECTION_PARTS)
        code = a.link()
        for name, start in (("straight", 0xA6), ("double", 0xA6), ("homing", 0xA6)):
            m = Machine(code, BASE)
            m.store(st.CURRENT_CTRL, CTRL)
            _store_half(m, CTRL + st.CTRL_ICE, start)
            m.regs[31], m.regs[29] = RET, 0x80200000
            stop = m.run(a.labels["trk_cb_" + name])
            assert stop.target == ice_cb and m.regs[31] == RET
            taken = (extra or {}).get(name, 0)
            assert (m.load(CTRL + st.CTRL_ICE) & 0xFFFF) == start - taken, name
    assert st.EXTRA_COST == {"double": 0x10, "homing": 0x20}
    assert st.extra_costs(st.COSTS_V54) == {"double": 0x10, "homing": 0x40}


def _rom_with(words: dict[int, int]) -> bytes:
    rom = bytearray(0x100000)
    for off, word in words.items():
        rom[off : off + 4] = word.to_bytes(4, "big")
    return bytes(rom)


def test_stock_edits_follow_the_freeze_slot_and_guard_the_sites() -> None:
    words = {
        st.HK_RECORD_ROM: 0x00200020,
        st.SUPER_SLIDE_GATE_ROM: st.SLTI_V0 | 2,  # shuffled
        st.FREEZE_GATE_ROM: st.SLTI_V0 | 5,
        **{off: st.BNEZ_V0_6 for off in st.SHATTER_BRANCHES},
        **{off - 4: st.SLTI_V0 | 7 for off in st.SHATTER_BRANCHES},
    }
    edits = st.stock_edits(_rom_with(words))
    assert edits[st.SUPER_SLIDE_GATE_ROM] == (st.SLTI_V0 | 2, st.SLTI_V0 | 5)
    assert edits[st.HK_RECORD_ROM] == (0x00200020, 0x00000020)  # mask 0 ends the HK table
    assert all(edits[off] == (st.BNEZ_V0_6, st.BRANCH_6) for off in st.SHATTER_BRANCHES)
    with pytest.raises(ValueError):
        st.stock_edits(_rom_with({**words, st.SHATTER_BRANCHES[0]: 0}))
    with pytest.raises(ValueError):
        st.stock_edits(_rom_with({**words, st.FREEZE_GATE_ROM: 0x24020008}))


def test_records_take_the_tier_conditions() -> None:
    rec = trk.straight_record(0x80123456, 0x80200000)
    assert rec[8:12] == bytes.fromhex("80200000") and rec[12:16] == bytes.fromhex("80123456")
    assert trk.straight_record(1)[8:12] == trk.LP_ICE_CONDITION.to_bytes(4, "big")
    assert trk.double_record(1, 0x80200010)[8:12] == bytes.fromhex("80200010")
