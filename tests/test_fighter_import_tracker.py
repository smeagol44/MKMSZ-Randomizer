"""R3 heat-seeking rocket: generated MIPS checked against the donor reference model."""

from __future__ import annotations

import random

from mips_eval import Machine, Stop

from mkmszr.fighter_import import effects, host
from mkmszr.fighter_import.actions import robo_tracker as trk
from mkmszr.fighter_import.actions import robo_zap
from mkmszr.fighter_import.mips import Assembler

BASE = 0xA01AF000
MASK = 0xFFFFFFFF


def _s(v: int) -> int:
    return v - (1 << 32) if v & 0x80000000 else v


def _payload(spawn_returns: bool = False) -> Assembler:
    a = Assembler(BASE)
    host.emit_sound_player(a)
    trk.emit_hunt(a)
    trk.emit_direction(a)
    trk.emit_targeting(a)
    trk.emit_callback(a, smoke="fx_smoke", explosion="fx_expl", boom_event=177)
    if spawn_returns:  # fx_spawn returns; v0 records that it ran
        a.label("fx_spawn")
        a.jr_ra()
        a.li("v0", 0x5A)
    a.label("fx_spawn_xy")  # stand-ins: record the arguments
    if not spawn_returns:
        a.label("fx_spawn")
    a.raw(0x0000000D)  # break: stops the evaluator
    trk.emit_data(a, [0x1000 + 0x40 * i for i in range(8)])
    a.label("fx_smoke")
    a.label("fx_expl")
    return a


def test_direction_matches_point_rocket() -> None:
    a = _payload()
    m = Machine(a.link(), BASE)
    rng = random.Random(3)
    cases = [(0, -1), (0, 5), (5, 0), (-5, 0), (1, 1), (7, -2), (2, -7), (-0x50000, 0x10)]
    cases += [(rng.randint(-0x60000, 0x60000), rng.randint(-0x60000, 0x60000)) for _ in range(300)]
    for vx, vy in cases:
        m.regs[4], m.regs[5], m.regs[31] = vx & MASK, vy & MASK, 0x80001000
        assert m.run(a.labels["trk_direction"]).target == 0x80001000
        assert m.regs[2] == trk.direction(vx, vy), (vx, vy)


def test_hunt_matches_the_donor_model() -> None:
    a = _payload()
    rng = random.Random(7)
    ctrl, rocket, opp_ctrl, opp = 0x80300000, 0x80310000, 0x80320000, 0x80330000
    nears = 0
    for k in range(400):
        m = Machine(a.link(), BASE)
        vx, vy = rng.randint(-0x50000, 0x50000), rng.randint(-0x50000, 0x50000)
        rx, ry = rng.randint(0, 0x100000), rng.randint(0x8000, 0x60000)
        if k % 4 == 0:  # close to the aim point (opponent + AIM_Y px below)
            ox = rx + rng.randint(-0x1800, 0x1800)
            oy = ry - (trk.AIM_Y << 9) + rng.randint(-0x1800, 0x1800)
        else:
            ox, oy = rx + rng.randint(-0x40000, 0x40000), ry + rng.randint(-0x20000, 0x20000)
        # displacement of the earlier donor steps of this host tick (16.16 px)
        ex, ey = (
            (0, 0) if k % 2 else (rng.randint(-0x60000, 0x60000), rng.randint(-0x60000, 0x60000))
        )
        m.regs[16], m.regs[17], m.regs[31] = ctrl, rocket, 0x80001000
        m.regs[18], m.regs[19] = (ex + vx) & MASK, (ey + vy) & MASK
        m.store(a.labels["trk_aim"], opp_ctrl)
        m.store(opp_ctrl + host.CTRL_ACTOR, opp)
        for actor, x, y in ((rocket, rx, ry), (opp, ox, oy)):
            m.store(actor + host.ACTOR_X, x)
            m.store(actor + host.ACTOR_Y, y)
        m.store(ctrl + trk.VX, vx & MASK)
        m.store(ctrl + trk.VY, vy & MASK)
        assert m.run(a.labels["trk_hunt"]).target == 0x80001000
        dx = ((ox - rx) >> 9) - (ex >> 16)
        dy = ((oy - ry) >> 9) - (ey >> 16) + trk.AIM_Y
        if trk.near(dx, dy):
            nears += 1
            assert m.regs[2] == 1 and m.regs[3] == opp
            assert (_s(m.load(ctrl + trk.VX)), _s(m.load(ctrl + trk.VY))) == (vx, vy)
        else:
            assert m.regs[2] == 0
            got = (_s(m.load(ctrl + trk.VX)), _s(m.load(ctrl + trk.VY)))
            assert got == trk.hunt(vx, vy, dx, dy)
    assert 10 < nears < 100


def test_near_matches_rocket_hunt() -> None:
    assert trk.near(0, 0) and trk.near(5, 0) and trk.near(-4, 3) and trk.near(0, -5)
    assert not trk.near(6, 0) and not trk.near(4, 4) and not trk.near(-3, -5)


FIND = trk.F_FIND_CLASS & 0x1FFFFFFF


def _call(m: Machine, stop: Stop, enemies: dict[int, int]) -> Stop:
    """Resume past an outside call; ``0x80028510(class)`` answers from ``enemies``."""

    if stop.target & 0x1FFFFFFF == FIND:
        m.regs[2] = enemies.get(m.regs[4], 0)
    return m.run(stop.resume)


def _run_callback(
    m: Machine, a: Assembler, enemies: dict[int, int] | None = None
) -> tuple[list[tuple[int, ...]], bool]:
    """One callback call: (calls made other than the class scan, broke at fx_spawn)."""

    calls = []
    m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
    try:
        stop = m.run(a.labels["trk_callback"])
        while stop.kind == "call":
            if stop.target & 0x1FFFFFFF != FIND:
                calls.append((stop.target & 0x1FFFFFFF, *m.regs[4:8]))
            stop = _call(m, stop, enemies or {})
    except NotImplementedError:  # the break at fx_spawn
        return calls + [("spawn", *m.regs[4:8])], True
    assert stop.target == 0x8004CD18 and m.regs[29] == 0x80200000
    return calls, False


def test_callback_runs_the_phases_and_drives_the_rocket() -> None:
    a = _payload()
    m = Machine(a.link(), BASE)
    ctrl, rocket, file_base = 0x80300000, 0x80310000, 0x80400000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, rocket)
    m.store(robo_zap.FILE87_BASE_PTR, file_base)
    m.store(ctrl + trk.VX, trk.START_SPEED)
    m.store(ctrl + trk.PHASE, trk.PHASE_TICKS[0] - 2 * robo_zap.CHILD_START_TICKS)
    m.store(ctrl + trk.DIR, 3)
    vx, vy, phase, count = trk.START_SPEED, 0, 0, 4
    # no opponent: the hunt leaves the velocity alone, so the model is the phase table
    for tick in range(14):
        spawns_xy = []
        m.regs[16:21] = [0x11, 0x22, 0x33, 0x44, 0x55]
        # stop at the smoke spawn, then resume past it as if it returned
        m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
        try:
            stop = m.run(a.labels["trk_callback"])
            while stop.kind == "call":
                stop = _call(m, stop, {})
        except NotImplementedError:
            spawns_xy.append(tuple(m.regs[4:8]))
        sx = sy = 0
        for _ in range(2):
            sx, sy = sx + vx, sy + vy
            if phase == 1:
                vy -= trk.CLIMB
            if phase < 2:
                count -= 1
                if count == 0:
                    phase += 1
                    count = trk.PHASE_TICKS[1] if phase == 1 else 0
        assert _s(m.load(ctrl + trk.VX)) == vx and _s(m.load(ctrl + trk.VY)) == vy, tick
        assert _s(m.load(rocket + host.ACTOR_XVEL)) == trk.host_velocity(sx)
        assert _s(m.load(rocket + host.ACTOR_YVEL)) == trk.host_velocity(sy)
        d = trk.direction(vx, vy)
        assert m.load(ctrl + trk.DIR) == d
        if d != 3:
            assert m.load(ctrl + host.CTRL_SCRIPT_CURSOR) == file_base + 0x1000 + 0x40 * d
        assert spawns_xy and spawns_xy[0][0] == rocket
        assert spawns_xy[0][2] == trk.smoke_offsets()[d]  # unflipped
        assert spawns_xy[0][1] == a.labels["fx_smoke"]
    assert phase == 2 and vy < 0  # climbed, now hunting


def test_callback_flips_and_mirrors_smoke_for_negative_x() -> None:
    a = _payload()
    m = Machine(a.link(), BASE)
    ctrl, rocket = 0x80300000, 0x80310000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, rocket)
    m.store(ctrl + trk.VX, (-trk.START_SPEED) & MASK)
    m.store(ctrl + trk.PHASE, 4)
    m.store(ctrl + trk.DIR, 3)
    m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
    stop = m.run(a.labels["trk_callback"])
    while stop.kind == "call" and stop.target & 0x1FFFFFFF == FIND:
        stop = _call(m, stop, {})
    assert stop.kind == "call" and stop.target & 0x1FFFFFFF == trk.F_FLIP & 0x1FFFFFFF
    assert m.regs[4] == rocket
    m.store(rocket + 0x8C, 0x10 << 16)  # what the flip did
    try:
        m.run(stop.resume)
        raise AssertionError("no smoke")
    except NotImplementedError:
        packed = m.regs[6]
    dx = _s(packed << 16 & MASK) >> 16
    assert dx == -(_s(trk.smoke_offsets()[3] << 16 & MASK) >> 16) and packed >> 16 == 0


def test_callback_explodes_on_the_last_loop_call() -> None:
    a = _payload()
    m = Machine(a.link(), BASE)
    ctrl, rocket = 0x80300000, 0x80310000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, rocket)
    m.store(ctrl + trk.TICKS, trk.LOOP_CALLS - 1)
    calls, broke = _run_callback(m, a)
    assert broke and calls[-1] == ("spawn", rocket, a.labels["fx_expl"], 0, effects.FRONT_SUBLAYER)
    sounds = [c for c in calls if c[0] == host.F_RAW_SOUND & 0x1FFFFFFF]
    assert sounds and sounds[0][1] == 177


def test_hp_record_and_command_stubs() -> None:
    rec = trk.descriptor_record(0xA01B1234)
    assert len(rec) == 0x2C and rec[:4] == bytes.fromhex("00100010")
    assert rec[0x08:0x10] == bytes.fromhex("8004A304A01B1234")
    assert rec[0x10:0x12] == bytes.fromhex("003C")
    assert rec[0x12:0x1A] == bytes.fromhex("0008000700090000")
    assert rec[0x1E:0x26] == bytes.fromhex("0009000700080000")
    # the stock LP Ice Blast record with F,F in place of D,F (and the teleport's window)
    stock_lp = bytes.fromhex(
        "00800080000000018004a30480049c340014000900070000000000000000000800070000000000000000"
    )
    lp = trk.straight_record(0xA01B1234)
    assert len(lp) == 0x2C and lp[:0x0C] == stock_lp[:0x0C]
    assert lp[0x0C:0x12] == bytes.fromhex("A01B12340018")
    assert lp[0x12:0x1E] == bytes.fromhex("000900090000000000000000")
    assert lp[0x1E:0x2C] == bytes.fromhex("0008000800000000000000000000")
    a = Assembler(BASE)
    host.emit_sound_player(a)
    trk.emit_command_stubs(a, ice_callback=0xA01B0000, target_event=459)
    trk.emit_data(a, [0] * 8)
    stubs = (
        ("trk_cb_straight", 0, 0, []),
        ("trk_cb_double", 0, robo_zap.DOUBLE_REQUESTED, []),
        ("trk_cb_homing", 1, 0, [459]),
    )
    for label, flag, double, events in stubs:
        m = Machine(a.link(), BASE)
        m.store(a.labels["trk_flag"], 7)
        m.store(a.labels["trk_double"], 7)
        m.regs[29], m.regs[31] = 0x80200000, 0x80049D50
        seen = []
        stop = m.run(a.labels[label])
        while stop.kind == "call":
            if stop.target & 0x1FFFFFFF == host.F_RAW_SOUND & 0x1FFFFFFF:
                seen.append(m.regs[4])
            stop = m.run(stop.resume)
        assert stop.target == 0xA01B0000 and m.regs[31] == 0x80049D50 and m.regs[29] == 0x80200000
        assert m.load(a.labels["trk_flag"]) == flag and seen == events
        assert m.load(a.labels["trk_double"]) == double


def test_spawn_xy_and_follower() -> None:
    art = effects.EffectArt((effects.EffectFrame(4, 2, 0, 0, bytes(8)),), (0x8001,))
    placed = effects.layout(art, 0x46000)
    a = Assembler(BASE)
    effects.emit_spawn(a, "trk_spawn", process="trk_target")
    effects.emit_process(a, "trk_target", follow=("trk_follow", "trk_heartbeat", -24, 54))
    effects.emit_descriptor(a, "tdesc", placed, art, ticks_per_frame=1, reserve=1)
    trk.emit_data(a, [0] * 8)
    # spawn_xy packs dy/dx
    m = Machine(a.link(), BASE)
    for head, at in (
        (effects.PROCESS_FREE_LIST, 0x80500000),
        (effects.OBJECT_FREE_LIST, 0x80600000),
    ):
        m.store(at, 0)
        m.store(head, at)
    m.regs[4:8] = [0x80310000, a.labels["tdesc"], ((-20 & 0xFFFF) << 16) | (-38 & 0xFFFF), 5]
    m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
    stop = m.run(a.labels["trk_spawn_xy"])
    child = 0x80380000
    while stop.kind == "call":
        m.regs[2] = child
        stop = m.run(stop.resume)
    assert m.load(child + effects.FX_SUBLAYER_DX) == (5 << 16) | (-38 & 0xFFFF)
    assert _s(m.load(child + effects.FX_DY)) == -20
    # follower: tracks the followed actor while the heartbeat moves, then cleans up
    m = Machine(a.link(), BASE)
    ctrl, actor, opp_ctrl, opp = 0x80300000, 0x80310000, 0x80320000, 0x80330000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(effects.FILE87_BASE_PTR, 0x80400000)
    m.store(ctrl + effects.FX_DESCRIPTOR, a.labels["tdesc"])
    m.store(a.labels["trk_follow"], opp_ctrl)
    m.store(opp_ctrl + host.CTRL_ACTOR, opp)
    m.regs[29] = ctrl + 0x628
    log, sleeps, beat = [], 0, 0
    stop = m.run(a.labels["trk_target"])
    while stop.kind == "call":
        t = stop.target & 0x1FFFFFFF
        log.append(t | 0x80000000)
        if t == effects.F_SLOT_ACQUIRE & 0x1FFFFFFF:
            m.regs[2] = 0x205
        elif t == effects.F_PALETTE_BIND & 0x1FFFFFFF:
            m.regs[2] = 0x90
        elif t == effects.F_ACTOR_CONSTRUCT & 0x1FFFFFFF:
            m.regs[2] = actor
        elif t == host.F_SLEEP & 0x1FFFFFFF and m.regs[4] == 1:
            sleeps += 1
            m.store(opp + host.ACTOR_X, 0x1000 * sleeps)
            m.store(opp + host.ACTOR_Y, 0x2000)
            if sleeps <= 3:  # the rocket is alive for three ticks
                beat += 1
                m.store(a.labels["trk_heartbeat"], beat)
        elif t == effects.F_PROCESS_EXIT & 0x1FFFFFFF:
            break
        stop = m.run(stop.resume)
    assert sleeps == 5  # three live ticks, then two missed heartbeats
    assert _s(m.load(actor + host.ACTOR_X)) == 0x1000 * 4 - (24 << 8)
    assert _s(m.load(actor + host.ACTOR_Y)) == 0x2000 + (54 << 8)
    assert log[-4:] == [
        effects.F_ACTOR_REMOVE,
        host.F_SLEEP,
        effects.F_SLOT_RELEASE,
        effects.F_PROCESS_EXIT,
    ]


def _near_setup(m: Machine) -> tuple[int, int, int]:
    ctrl, rocket, opp_ctrl, opp = 0x80300000, 0x80310000, 0x80320000, 0x80330000
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(ctrl + host.CTRL_ACTOR, rocket)
    m.store(opp_ctrl + host.CTRL_ACTOR, opp)
    m.store(opp_ctrl + trk.CTRL_HEALTH, 50 << 16)
    m.store(ctrl + trk.PHASE, 2 << 16)  # hunting
    m.store(ctrl + trk.DIR, 3)
    m.store(ctrl + trk.VX, 5 << 16)
    m.store(opp + host.ACTOR_X, 0x200000)
    m.store(opp + host.ACTOR_Y, 0x40000)
    return ctrl, rocket, opp


def test_callback_places_the_rocket_on_the_aim_point_when_near() -> None:
    a = _payload()
    m = Machine(a.link(), BASE)
    ctrl, rocket, _ = _near_setup(m)
    # 8 px short of the aim point: the first step is not near, the second (5 px on) is
    m.store(rocket + host.ACTOR_X, 0x200000 - (8 << 9))
    m.store(rocket + host.ACTOR_Y, 0x40000 + (trk.AIM_Y << 9))
    m.store(rocket + host.ACTOR_XVEL, 0x1234)
    m.store(rocket + host.ACTOR_YVEL, 0x5678)
    m.store(a.labels["trk_aim"], 0x80320000)
    calls, broke = _run_callback(m, a, {2: 0x80320000})
    assert not broke and calls == []  # no smoke, no sound
    assert m.load(rocket + host.ACTOR_X) == 0x200000
    assert m.load(rocket + host.ACTOR_Y) == 0x40000 + (trk.AIM_Y << 9)
    assert m.load(rocket + host.ACTOR_XVEL) == 0 and m.load(rocket + host.ACTOR_YVEL) == 0
    assert m.load(ctrl + trk.PHASE) == trk.DETONATE << 16
    assert m.load(ctrl + trk.TICKS) == 1


def test_callback_detonates_after_a_proximity_miss() -> None:
    a = _payload(spawn_returns=True)
    m = Machine(a.link(), BASE)
    ctrl, rocket, _ = _near_setup(m)
    m.store(ctrl + trk.PHASE, trk.DETONATE << 16)
    m.regs[29], m.regs[31] = 0x80200000, 0x8004CD18
    calls = []
    stop = m.run(a.labels["trk_callback"])
    while stop.kind == "call":
        target = stop.target & 0x1FFFFFFF
        calls.append((target, *m.regs[4:8]))
        if target == trk.F_FLIGHT_END & 0x1FFFFFFF:
            break
        stop = m.run(stop.resume)
    sounds = [c for c in calls if c[0] == host.F_RAW_SOUND & 0x1FFFFFFF]
    assert sounds and sounds[0][1] == 177
    assert calls[-1] == (trk.F_FLIGHT_END & 0x1FFFFFFF, rocket, *calls[-1][2:])
    assert m.regs[2] == 0x5A  # the explosion spawn ran first


PLAYER, PLAYER_ACTOR = 0x80340000, 0x80350000


def _world(m: Machine, enemies: dict[int, tuple[int, int, int, int, int]]) -> dict[int, int]:
    """Player at (0x100000, 0x40000) on path 1; ``enemies[class] = (ctrl, x, y, path,
    health)``. Returns the class -> controller answers of the scan."""

    m.store(host.PLAYER_CTRL, PLAYER)
    m.store(PLAYER + host.CTRL_ACTOR, PLAYER_ACTOR)
    m.store(PLAYER_ACTOR + host.ACTOR_X, 0x100000)
    m.store(PLAYER_ACTOR + host.ACTOR_Y, 0x40000)
    m.store(PLAYER_ACTOR + host.ACTOR_PATH, 1)
    for ctrl, x, y, path, health in enemies.values():
        actor = ctrl + 0x10000
        m.store(ctrl + host.CTRL_ACTOR, actor)
        m.store(ctrl + trk.CTRL_HEALTH, health << 16)  # halfword at +0x654
        m.store(actor + host.ACTOR_X, x)
        m.store(actor + host.ACTOR_Y, y)
        m.store(actor + host.ACTOR_PATH, path)
    return {cls: e[0] for cls, e in enemies.items()}


def _call_label(m: Machine, a: Assembler, label: str, answers: dict[int, int]) -> list[int]:
    m.regs[29], m.regs[31] = 0x80200000, 0x80001000
    seen = []
    stop = m.run(a.labels[label])
    while stop.kind == "call":
        seen.append(stop.target & 0x1FFFFFFF)
        stop = _call(m, stop, answers)
    assert stop.target == 0x80001000 and m.regs[29] == 0x80200000
    return seen


def test_pick_takes_the_nearest_living_enemy_in_range_on_the_path() -> None:
    a = _payload()
    reach = trk.TARGET_RANGE << 8
    cases = [
        ({}, 0),
        ({2: (0x80400000, 0x100000 + reach, 0x40000, 1, 9)}, 0x80400000),  # range edge
        ({2: (0x80400000, 0x100000 + reach + 1, 0x40000, 1, 9)}, 0),  # out of range
        ({2: (0x80400000, 0x100000, 0x40000 - reach - 1, 1, 9)}, 0),  # out of range (y)
        ({2: (0x80400000, 0x110000, 0x40000, 2, 9)}, 0),  # other path
        ({2: (0x80400000, 0x110000, 0x40000, 1, 0)}, 0),  # dead
        (
            {
                2: (0x80400000, 0x100000 + 0x30000, 0x40000, 1, 9),
                3: (0x80420000, 0x100000 - 0x20000, 0x40000, 1, 9),
                4: (0x80440000, 0x100000 + 0x10000, 0x40000, 1, 0),  # nearest, but dead
            },
            0x80420000,
        ),
        (
            {
                2: (0x80400000, 0x100000 + 0x30000, 0x40000, 1, 9),
                4: (0x80440000, 0x100000 + 0x10000, 0x40000, 1, 9),
            },
            0x80440000,
        ),
    ]
    for enemies, want in cases:
        m = Machine(a.link(), BASE)
        answers = _world(m, enemies)
        regs = [0x1111 * (k + 1) for k in range(8)]
        m.regs[16:24] = regs
        seen = _call_label(m, a, "trk_pick", answers)
        assert m.regs[2] == want, enemies
        assert seen == [FIND] * 3 and m.regs[16:24] == regs


def test_check_keeps_a_living_target_and_otherwise_retargets() -> None:
    a = _payload()
    near, far = (0x80400000, 0x110000, 0x40000, 1, 9), (0x80420000, 0x130000, 0x40000, 1, 9)
    # current target alive and present: kept, although another enemy is nearer
    m = Machine(a.link(), BASE)
    answers = _world(m, {2: near, 3: far})
    m.store(a.labels["trk_aim"], far[0])
    _call_label(m, a, "trk_check", answers)
    assert m.regs[2] == far[0] and m.load(a.labels["trk_follow"]) == far[0]
    # current target dead: the nearest living one
    m = Machine(a.link(), BASE)
    answers = _world(m, {2: near, 3: far[:4] + (0,)})
    m.store(a.labels["trk_aim"], far[0])
    _call_label(m, a, "trk_check", answers)
    assert m.regs[2] == near[0] and m.load(a.labels["trk_aim"]) == near[0]
    # current target gone (the v44 case: a stale controller), nobody else: unguided
    m = Machine(a.link(), BASE)
    answers = _world(m, {})
    m.store(a.labels["trk_aim"], far[0])
    m.store(a.labels["trk_follow"], far[0])
    _call_label(m, a, "trk_check", answers)
    assert m.regs[2] == 0 and m.load(a.labels["trk_aim"]) == 0
    assert m.load(a.labels["trk_follow"]) == 0  # the crosshair removes itself


def test_condition_refuses_without_a_target() -> None:
    a = _payload()
    trk.emit_condition(a)
    stock = trk.LP_ICE_CONDITION & 0x1FFFFFFF
    near = (0x80400000, 0x110000, 0x40000, 1, 9)
    for stock_answer, enemies, want, target in (
        (0x4000, {2: near}, 0x4000, 0x77),  # stock refusal: no scan, target untouched
        (0x8000, {}, 0x4000, 0),
        (0x8000, {2: near}, 0x8000, near[0]),
    ):
        m = Machine(a.link(), BASE)
        answers = _world(m, enemies)
        m.store(a.labels["trk_aim"], 0x77)
        m.regs[4:8] = [0xA0, 0xA1, 0xA2, 0xA3]
        m.regs[29], m.regs[31] = 0x80200000, 0x80001000
        stop = m.run(a.labels["trk_cond"])
        assert stop.kind == "call" and stop.target & 0x1FFFFFFF == stock
        assert m.regs[4:8] == [0xA0, 0xA1, 0xA2, 0xA3]
        m.regs[2] = stock_answer
        stop = m.run(stop.resume)
        while stop.kind == "call":
            stop = _call(m, stop, answers)
        assert stop.target == 0x80001000 and m.regs[2] == want
        assert m.load(a.labels["trk_aim"]) == target


def test_double_record_replaces_ice_clone() -> None:
    stock_clone = bytes.fromhex(
        "00800080000000018004a22c8003cf8c001400080007000000000000000000090007000000000000000000"
    )
    rec = trk.double_record(0xA01B1234)
    assert len(rec) == 0x2C and rec[:0x08] == stock_clone[:0x08]
    assert rec[0x08:0x12] == bytes.fromhex("8004A304A01B1234003C")  # straight rocket condition
    assert rec[0x12:0x1E] == bytes.fromhex("000900080008000000000000")  # F,B,B newest first
    assert rec[0x1E:0x2C] == bytes.fromhex("0008000900090000000000000000")


def test_double_launch_replays_the_creation_once_then_holds() -> None:
    root = 0xA01B1000
    a = Assembler(BASE)
    robo_zap.emit_double_launch(a, root)
    trk.emit_data(a, [0] * 8)
    sleep = host.F_SLEEP & 0x1FFFFFFF
    ctrl, file_base = 0x80300000, 0x80400000

    def run(state: int) -> tuple[list[int], int, int]:
        m = Machine(a.link(), BASE)
        m.store(host.CURRENT_CTRL, ctrl)
        m.store(robo_zap.FILE87_BASE_PTR, file_base)
        m.store(ctrl + host.CTRL_SCRIPT_CURSOR, 0x1234)
        m.store(a.labels["trk_double"], state)
        sleeps = []
        stop = m.run(a.labels["zap_again"])
        while stop.kind == "call":
            assert stop.target & 0x1FFFFFFF == sleep
            sleeps.append(m.regs[4])
            stop = m.run(stop.resume)
        assert stop.kind == "jump"
        if stop.target == root + (robo_zap.DOUBLE_CONTINUE_SRC - robo_zap.ICE_ROOT_SRC):
            assert m.regs[2] == ctrl  # the replaced lui/lw
        return sleeps, stop.target, m.load(a.labels["trk_double"])

    cont = root + (robo_zap.DOUBLE_CONTINUE_SRC - robo_zap.ICE_ROOT_SRC)
    replay = root + (robo_zap.DOUBLE_REPLAY_SRC - robo_zap.ICE_ROOT_SRC)
    assert run(0) == ([], cont, 0)  # single rocket: straight on
    sleeps, target, state = run(robo_zap.DOUBLE_REQUESTED)
    assert (sleeps, target, state) == ([robo_zap.DOUBLE_GAP_SLEEP], replay, robo_zap.DOUBLE_SECOND)
    assert run(robo_zap.DOUBLE_SECOND) == ([robo_zap.DOUBLE_EXTRA_HOLD], cont, 0)
    # the replay rewinds the parent's script to the creation token
    m = Machine(a.link(), BASE)
    m.store(host.CURRENT_CTRL, ctrl)
    m.store(robo_zap.FILE87_BASE_PTR, file_base)
    m.store(a.labels["trk_double"], robo_zap.DOUBLE_REQUESTED)
    stop = m.run(a.labels["zap_again"])
    stop = m.run(stop.resume)
    assert m.load(ctrl + host.CTRL_SCRIPT_CURSOR) == file_base + robo_zap.ZAP_TOKEN
