"""Tests for the importer's effect component (no ROM needed)."""

from __future__ import annotations

import random

from mips_eval import Machine

from mkmszr.fighter_import import effects, host
from mkmszr.fighter_import.mips import Assembler

BASE = 0xA01AF000


def _decode_type4_with_ring(block: bytes, ring: bytearray) -> bytes:
    """The native decoder (0x80003428) with a given starting ring."""

    token = 4 + int.from_bytes(block[4:8], "little")
    control_pos, mask, out, index = 9, 0x80, bytearray(), 1
    control = block[8]
    while True:
        if control & mask:
            value = block[token]
            token += 1
            out.append(value)
            ring[index] = value
            index = (index + 1) & 0x3FF
        else:
            src = (block[token] << 2) | (block[token + 1] >> 6)
            count = (block[token + 1] & 0x3F) + 2
            token += 2
            if src == 0:
                return bytes(out)
            for k in range(count):
                value = ring[(src + k) & 0x3FF]
                out.append(value)
                ring[index] = value
                index = (index + 1) & 0x3FF
        mask >>= 1
        if not mask:
            mask, control = 0x80, block[control_pos]
            control_pos += 1


def test_type4_encoder_is_history_independent_and_compresses() -> None:
    rng = random.Random(5)
    for raw in (
        bytes(3000),
        bytes(rng.choice((0, 0, 0, 3, 7)) for _ in range(5000)),
        bytes(rng.randrange(32) for _ in range(2500)),
        b"\x05" * 1100 + bytes(range(200)) * 6,
    ):
        block = effects.encode_type4(raw)
        assert block[3] == 4 and int.from_bytes(block[:3], "little") == len(block)
        for _ in range(3):  # a stale ring from earlier images must not matter
            ring = bytearray(rng.randrange(256) for _ in range(1024))
            assert _decode_type4_with_ring(block, ring) == raw
    assert len(effects.encode_type4(bytes(3000))) < 120


def _art(compressed: bool) -> effects.EffectArt:
    frames = (
        effects.EffectFrame(5, 3, 2, 1, bytes(range(24))),
        effects.EffectFrame(9, 4, 4, 2, bytes(48)),
    )
    return effects.EffectArt(frames, (0x8001, 0xFFFF), compressed)


def test_layout_records() -> None:
    def u32(data: bytes, off: int) -> int:
        return int.from_bytes(data[off - 0x46000 : off - 0x46000 + 4], "big")

    for compressed in (False, True):
        art = _art(compressed)
        placed = effects.layout(art, 0x46000)
        data = placed.data
        assert art.slot_size == (9, 4) and len(data) % 4 == 0
        assert u32(data, placed.palette) == 64
        shapes = [u32(data, placed.script + 4 * i) for i in range(3)]
        assert shapes[2] == 0
        for shape, frame in zip(shapes, art.frames, strict=False):
            assert shape % 4 == 0 and u32(data, shape + 4) == 0
            desc = u32(data, shape)
            image = u32(data, desc)
            assert u32(data, desc + 4) == (frame.width << 16) | frame.height
            assert u32(data, desc + 8) == (frame.anchor_x << 16) | frame.anchor_y
            assert data[image - 0x46000 + 3] == (4 if compressed else 0)


def _effect_payload() -> tuple[Assembler, effects.EffectLayout]:
    art = _art(True)
    placed = effects.layout(art, 0x46000)
    a = Assembler(BASE)
    effects.emit_spawn(a)
    effects.emit_process(a)
    effects.emit_descriptor(a, "fx_desc", placed, art, ticks_per_frame=2, reserve=3)
    return a, placed


def _free_list(m: Machine, head: int, count: int, at: int) -> None:
    nxt = 0
    for i in range(count):
        node = at + 0x1000 * i
        m.store(node, nxt)
        nxt = node
    m.store(head, nxt)


def test_spawn_copies_source_state_and_respects_pool_reserve() -> None:
    a, _ = _effect_payload()
    actor, child = 0x80310000, 0x80320000
    for free_procs, spawned in ((3, True), (2, False)):
        m = Machine(a.link(), BASE)
        _free_list(m, effects.PROCESS_FREE_LIST, free_procs, 0x80500000)
        _free_list(m, effects.OBJECT_FREE_LIST, 5, 0x80600000)
        for off, value in ((0x2C, 0x12345), (0x30, 0x6789A), (0x34, 0xBCD)):
            m.store(actor + off, value)
        m.store(actor + 0xAC, 0x00010002)  # +0xAC / +0xAE
        m.store(actor + 0xB0, 0x00030000)
        m.store(actor + 0x5C, 0x00070000)
        m.regs[4:8] = [actor, a.labels["fx_desc"], (-38) & 0xFFFFFFFF, 0xFFFF]
        m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
        calls = []
        stop = m.run(a.labels["fx_spawn"])
        while stop.kind == "call":
            calls.append(((stop.target & 0x1FFFFFFF) | 0x80000000, m.regs[4], m.regs[5]))
            m.regs[2] = child
            stop = m.run(stop.resume)
        assert stop.target == 0x8004CD18 and m.regs[29] == 0x80200000
        if not spawned:
            assert calls == []
            continue
        assert calls == [(effects.F_PROCESS_CREATE, 0x100, a.labels["fx_process"])]
        assert [m.load(child + f) for f in (0x6F4, 0x6F8, 0x6FC)] == [0x12345, 0x6789A, 0xBCD]
        assert m.load(child + effects.FX_DESCRIPTOR) == a.labels["fx_desc"]
        assert m.load(child + effects.FX_ROT_AC_AE) == 0x00010002
        assert m.load(child + effects.FX_ROT_B0_LAYER) == 0x00030007
        assert m.load(child + effects.FX_SUBLAYER_DX) == 0xFFFFFFDA


def test_process_lifecycle() -> None:
    a, placed = _effect_payload()
    m = Machine(a.link(), BASE)
    ctrl, actor, file_base = 0x80300000, 0x80310000, 0x80400000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(effects.FILE87_BASE_PTR, file_base)
    for off, value in (
        (effects.FX_X, 0x1000),
        (effects.FX_Y, 0x2000),
        (effects.FX_Z, 0x3000),
        (effects.FX_DESCRIPTOR, a.labels["fx_desc"]),
        (effects.FX_ROT_AC_AE, 0x00110022),
        (effects.FX_ROT_B0_LAYER, 0x00330002),
        (effects.FX_SUBLAYER_DX, 0x0005FFDA),
    ):
        m.store(ctrl + off, value)
    script = file_base + placed.script
    m.store(script, 0x46100)
    m.store(script + 4, 0x46200)
    m.store(script + 8, 0)
    m.regs[29] = ctrl + 0x628
    log = []
    stop = m.run(a.labels["fx_process"])
    while stop.kind == "call":
        target = stop.target & 0x1FFFFFFF
        args = tuple(m.regs[4:8])
        log.append((target | 0x80000000, args))
        if target == effects.F_SLOT_ACQUIRE & 0x1FFFFFFF:
            m.regs[2] = 0x205
        elif target == effects.F_PALETTE_BIND & 0x1FFFFFFF:
            m.regs[2] = 0x93
        elif target == effects.F_ACTOR_CONSTRUCT & 0x1FFFFFFF:
            m.regs[2] = actor
            m.store(ctrl + host.CTRL_ACTOR, actor)
        elif target == effects.F_ANIM_ADVANCE & 0x1FFFFFFF:
            m.store(ctrl + 0x6E4, m.load(ctrl + 0x6E4) + 4)
        elif target == effects.F_PROCESS_EXIT & 0x1FFFFFFF:
            break
        stop = m.run(stop.resume)
    names = [t for t, _ in log]
    assert names == [
        effects.F_SLOT_ACQUIRE,
        effects.F_PALETTE_BIND,
        effects.F_ACTOR_CONSTRUCT,
        host.F_OFFSET,
        effects.F_ACTOR_INSERT,
        effects.F_ANIM_ADVANCE,
        host.F_SLEEP,
        effects.F_ANIM_ADVANCE,
        host.F_SLEEP,
        effects.F_ACTOR_REMOVE,
        host.F_SLEEP,
        effects.F_SLOT_RELEASE,
        effects.F_PROCESS_EXIT,
    ]
    args = dict(log[:5])
    assert args[effects.F_SLOT_ACQUIRE][:2] == (9, 4)
    assert args[effects.F_PALETTE_BIND][:3] == (file_base + placed.palette, 0x100, 0)
    assert args[effects.F_ACTOR_CONSTRUCT] == (script, 0, file_base, 1)
    assert args[host.F_OFFSET][:3] == (actor, 0xFFFFFFDA, 0)
    assert args[effects.F_ACTOR_INSERT][:2] == (actor, effects.ACTOR_LIST)
    assert [a for t, a in log if t == host.F_SLEEP] == [(2, *log[6][1][1:])] * 2 + [
        (2, *log[10][1][1:])
    ]
    assert log[11][1][0] == 0x205  # the acquired slot is released
    halves = {off: m.load(actor + off) for off in (0x9C, 0xAC, 0xB0, 0x5C, 0xEC, 0x8C)}
    assert halves[0x9C] >> 16 == 0x205 and halves[0x9C] & 0xFFFF == 0x13  # slot, palette - 0x80
    assert halves[0xAC] == 0x00110022 and halves[0xB0] >> 16 == 0x33
    assert halves[0x5C] >> 16 == 2 and halves[0xEC] >> 16 == 5 and halves[0x8C] >> 16 == 0x40
    assert [m.load(actor + f) for f in (0x2C, 0x30, 0x34)] == [0x1000, 0x2000, 0x3000]
    assert m.load(actor + 0x64) == 0x2002 and m.load(actor + 0xD8) == 0x6C
    assert m.load(ctrl + 0x6E4) == script + 8


def test_process_without_texture_slot_exits() -> None:
    a, _ = _effect_payload()
    m = Machine(a.link(), BASE)
    ctrl = 0x80300000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + effects.FX_DESCRIPTOR, a.labels["fx_desc"])
    stop = m.run(a.labels["fx_process"])
    assert stop.target & 0x1FFFFFFF == effects.F_SLOT_ACQUIRE & 0x1FFFFFFF
    m.regs[2] = 0xFFFFFFFF
    stop = m.run(stop.resume)
    assert stop.target & 0x1FFFFFFF == effects.F_PROCESS_EXIT & 0x1FFFFFFF
