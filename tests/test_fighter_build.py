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
# Reptile specials proof v23 (owner, 2026-11-26: "Acid spit works now"): the impact defaults
# (the enemy hit, MKT's flip with the art mirrored, the spit's own height). With his earlier
# acid settings (ACCEPTED_ACID_TUNING) the build still gives PAYLOAD_SHA256 / V22_FILE87_SHA256.
V23_PAYLOAD_SHA256 = "0249818fe8126966d4fd49545682758b82005776f829d13c56f30cf19fbdaaea"
V23_FILE87_SHA256 = "64e6d394ef95aad23ad45eb522c28d4ad3d88730919ade2b786d705cb2784bab"
# SMRE step 1 (owner, 2026-11-27: "let's remove it and have it being pure MKT"): MKT's forceballs
# do not turn to the opponent at the start (init_special); the accepted hand-written programs did.
# The fighter file is unchanged; with the turn restored (ACCEPTED_FORCEBALL_TURN) the build gives
# the V23 payload again.
V24_PAYLOAD_SHA256 = "749b6da96350f91e94285d01ea042b6a7a6ffcf5ba83d2e7a6ca7dd384e0b0a4"
ACCEPTED_FORCEBALL_TURN = {"face": True}


# Reptile's Acid Spit placement before v23 (his proofs v11-v22): the flip dropped, the impact
# at the player's opponent, unmirrored. Proof v23 took the defaults Rayden needed (accepted).
ACCEPTED_ACID_TUNING = {"impact_flip": False, "impact_keep_y": True, "impact_at_hit": False,
                        "impact_mirror": False}  # fmt: skip


def accepted_acid(monkeypatch: pytest.MonkeyPatch) -> None:
    import dataclasses

    from mkmszr.fighter_import import description

    real = description.load

    def load(name: str):  # type: ignore[no-untyped-def]
        d = real(name)
        if name != "reptile":
            return d
        specials = {k: dict(v) for k, v in d.specials.items()}
        specials["acid_spit"]["projectile"] = {**specials["acid_spit"]["projectile"], **ACCEPTED_ACID_TUNING}
        for move in ("forceball_fast", "forceball_slow"):
            specials[move].update(ACCEPTED_FORCEBALL_TURN)
        return dataclasses.replace(d, specials=specials)

    monkeypatch.setattr(description, "load", load)


def accepted_turn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reptile's forceballs as accepted through specials proof v23: turning at the start."""

    import dataclasses

    from mkmszr.fighter_import import description

    real = description.load

    def load(name: str):  # type: ignore[no-untyped-def]
        d = real(name)
        if name != "reptile":
            return d
        specials = {k: dict(v) for k, v in d.specials.items()}
        for move in ("forceball_fast", "forceball_slow"):
            specials[move].update(ACCEPTED_FORCEBALL_TURN)
        return dataclasses.replace(d, specials=specials)

    monkeypatch.setattr(description, "load", load)


@pytest.fixture(scope="module")
def roms() -> tuple[bytes, bytes]:
    return Path(CLEAN).read_bytes(), Path(MKT).read_bytes()


@needs_roms
def test_generic_build_reproduces_the_accepted_reptile(roms: tuple[bytes, bytes],
                                                      monkeypatch: pytest.MonkeyPatch) -> None:  # fmt: skip
    built = fb.build(*roms, "reptile")
    assert hashlib.sha256(built.payload).hexdigest() == V24_PAYLOAD_SHA256
    assert hashlib.sha256(built.file87).hexdigest() == V23_FILE87_SHA256
    accepted_turn(monkeypatch)
    assert hashlib.sha256(fb.build(*roms, "reptile").payload).hexdigest() == V23_PAYLOAD_SHA256
    assert built.selectors == {"forceball_fast": 3, "forceball_slow": 4, "acid_spit": 5, "elbow_dash": 6,
                               "invisibility": 7}  # fmt: skip
    assert sorted(built.reactions.values()) == [0x23, 0x2B, 0x4C]


@needs_roms
def test_with_the_earlier_acid_settings_the_build_is_composition_v03(
        roms: tuple[bytes, bytes], monkeypatch: pytest.MonkeyPatch) -> None:  # fmt: skip
    accepted_acid(monkeypatch)
    built = fb.build(*roms, "reptile")
    assert hashlib.sha256(built.payload).hexdigest() == PAYLOAD_SHA256
    assert hashlib.sha256(built.file87).hexdigest() == V22_FILE87_SHA256


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

    accepted_acid(monkeypatch)
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
    records = dict(built.report["strike_records"])["torpedo"]
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
    # xor t1, t1, t2 (the facing bit): each lightning's burst, and the Shocker's victim turning
    # to face him (v27)
    assert ws.count(0x012A4826) == 3
    # input map: five begins without a turn (both lightnings, teleport, torpedo, Shocker), three jumps
    assert ws.count(0x2739B05C) == 8
    # v11-v12 (owner screenshots, Wind): the burst goes to the enemy hit (the player's +0x640,
    # set by the collision core), at its whole position: path, path position, x, z; v15: the
    # bolt's own height kept (impact_keep_y), not the enemy's feet
    i = next(k for k, w in enumerate(ws) if w == 0x8D081AC0 and ws[k + 1] == 0x8D080640)
    copies = [w for w in ws[i : i + 20] if (w >> 16) == 0x8D09]  # lw t1, field(t0)
    assert [w & 0xFFFF for w in copies] == [0xDC, 0xE0, 0x2C, 0x34]
    assert 0x2529FFA0 not in ws and 0x2529FFE0 in ws  # addiu t1, t1, -0x60 / -0x20


@needs_roms
def test_a_pose_past_its_script_is_refused(roms: tuple[bytes, bytes], monkeypatch: pytest.MonkeyPatch) -> None:
    from mkmszr.fighter_import import generate

    real_program = generate.Generator.program

    def with_bad_pose(self, name: str, record: int):  # type: ignore[no-untyped-def]
        prog, g, notes = real_program(self, name, record)
        if name == "torpedo":  # every Rayden move is written by SMRE at build time
            prog["steps"].insert(5, {"op": "pose", "anim": {"table": 1, "slot": 0, "offset": 6},
                                     "src": {"anim": "MKT 0x800455A8"}})  # fmt: skip
        return prog, g, notes

    monkeypatch.setattr(generate.Generator, "program", with_bad_pose)
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
    # v17 (owner: no blink in v16): the draw tints through the per-vertex colours +0xA0..+0xAB
    # and recomputes them from the stage lighting while actor +0x8C bit 0x1000 is set
    assert 0x3129EFFF in ws  # andi t1, t1, 0xEFFF: lighting paused
    assert {0xA26900A0 + k for k in range(12)} <= set(ws)  # sb t1, 0xA0..0xAB(s3)
    assert 0x01364825 in ws  # or t1, t1, s6: the lighting bit back as it was
    assert not {0xA66900FC, 0xA66900FE, 0xA6690100} & set(ws)  # v16's sh t1, +0xFC..(s3)
    assert 0x24040004 in ws  # v18 (owner): addiu a0, zero, 4: two frames cyan, two normal


@needs_roms
def test_lightning_burst_sits_six_pixels_nearer(roms: tuple[bytes, bytes]) -> None:
    """v18 (owner: the burst "a bit too far past the enemy"): MKT's adjust -115 px, then
    ``impact_toward_px`` 6 toward Rayden: -109 px, -218 world units for the offset call."""

    built = fb.build(*roms, "rayden")
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    assert 0x2405FF26 in ws and 0x2405FF1A not in ws  # addiu a1, zero, -218 (not -230)


@needs_roms
def test_lightning_burst_follows_the_victim(roms: tuple[bytes, bytes]) -> None:
    """v17 (owner: the burst should follow the pushed enemy): MKT's burst copies the opponent's
    velocity every tick (0x800781F0); the host burst keeps its offset from the victim (path
    position, x, y, z) every tick."""

    built = fb.build(*roms, "rayden")
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    for k, field in enumerate((0xE0, 0x2C, 0x30, 0x34)):
        assert 0xAFA90024 + 4 * k in ws  # sw t1, 0x24+4k(sp): the offset
        assert 0x8EA90000 + field in ws  # lw t1, field(s5): the victim's
        assert 0x8FAA0024 + 4 * k in ws  # lw t2, 0x24+4k(sp)


@needs_roms
def test_a_frame_shared_by_flight_and_impact_is_drawn_twice(roms: tuple[bytes, bytes]) -> None:
    """v17 (owner video: the bolt jumped ahead once per loop): Rayden's donor frame 0x2024 ends
    the flight loop and opens the burst; the burst's copy (mirrored, its own palette) replaced
    the flight's. Each part now has its own drawn frames."""

    from mkmszr.fighter_import import components
    from mkmszr.fighter_import import lower_projectile as lp

    moves, _ = components.load_programs("rayden")
    step = next(s for m in moves if m.name == "lightning" for s in m.steps if s["op"] == "projectile")
    file87 = bytearray(0x200)
    art = lp.place_art(file87, roms[1], 24, step, None, 1 << 24, impact_mirror=True)

    def script(at: int) -> set[int]:
        words = []
        while (w := int.from_bytes(file87[at : at + 4], "big")) != 1:
            words.append(w)
            at += 4
        return set(words)

    assert len(script(art.flight_at)) == 6 and len(script(art.impact_at)) == 7
    assert not script(art.flight_at) & script(art.impact_at)


@needs_roms
def test_somersault_anchors_move_to_the_body(roms: tuple[bytes, bytes]) -> None:
    """v16 (owner: a mid-air turn shifted Rayden): his somersault anchors move 21 px; Reptile's
    (2 px off) stay."""

    clean, mkt = roms
    for name, expected in (("rayden", ["SOMERSAULT slot 0x1A: anchors moved 21 px to the body's centre"]),
                           ("reptile", [])):  # fmt: skip
        body = fb.body_build.build_body(fb.fd.load(name), clean, mkt, fb.body_build.Extras())
        assert [line for line in body.log if "SOMERSAULT" in line] == expected


@needs_roms
def test_reptile_acid_takes_the_impact_defaults(roms: tuple[bytes, bytes]) -> None:
    """Reptile specials proof v23 (accepted): Acid Spit's splash goes to the enemy hit, at its
    whole position (as Rayden's burst, v12), with MKT's flip and the art mirrored."""

    built = fb.build(*roms, "reptile")
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    i = next(k for k, w in enumerate(ws) if w == 0x8D081AC0 and ws[k + 1] == 0x8D080640)
    copies = [w for w in ws[i : i + 20] if (w >> 16) == 0x8D09]  # lw t1, field(t0)
    assert [w & 0xFFFF for w in copies] == [0xDC, 0xE0, 0x2C, 0x34]


def test_airborne_moves_hover_where_the_program_flew_level() -> None:
    """Generator step 4: ``hover`` is the backend's for moves tuned ``airborne`` (after the begin,
    and first on every tick of hit windows and carries), no longer a step of the program."""

    from mkmszr.fighter_import import components

    moves, _ = components.load_programs("rayden")
    torpedo = next(m for m in moves if m.name == "torpedo").steps
    assert not any(s["op"] == "hover" for s in fb._all_steps(torpedo))
    steps = fb.with_hover(torpedo)
    assert [s["op"] for s in steps[:2]] == ["begin", "hover"]
    window = next(s for s in steps if s["op"] == "strike")
    assert window["every_tick"] == [{"op": "hover"}]
    carry = next(s for s in window["on_hit"] if s["op"] == "carry")
    assert [s["op"] for s in carry["every_tick"]] == ["hover", "pass_through"]


@needs_roms
def test_reversed_lightning_in_the_air_ice_blast_slot(roms: tuple[bytes, bytes]) -> None:
    """Generator step 5 (specials proof v20): the generated D,B + LP program in Air Ice Blast's
    slot (a new LP record), sharing the lightning's art with its own reaction (MKT 0x81); the
    bolt wraps once at the screen edge by mirroring across the camera's centre."""

    built = fb.build(*roms, "rayden")
    assert built.selectors["reversed_lightning"] == 4
    assert "projectile (0, 67, 3) shock_stagger_toward" in built.reactions
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    assert 0x24160100 in ws  # li s6, WRAP_ARMED
    assert 0x8F290014 in ws and 0x87290000 in ws  # lw t1, 0x14(t9) (camera T), lh t1, 0(t9) (M00)
    assert 0x2739188C in ws  # the turn 0x8003188C (flip), through t9
    # v21 (owner on v20: "The bolt passes through enemies"; "with the zoomed out camera it
    # doesn't spawn off screen"): its strike checks run with the player-actor pointer holding the
    # bolt (sw s1 / sw s7 at 0x802E73DC), and the edge is judged at the bolt's own depth (view
    # row 2 halfwords at +0xC: lh t1, 0xC(t9); the focal 0x8009A8E8)
    assert ws.count(0xAD1173DC) >= 3 and ws.count(0xAD1773DC) >= 3  # 2 checks + the flight
    assert 0x8729000C in ws and 0x8D08A8E8 in ws


@needs_roms
def test_teleport_relocates_with_an_afterimage_and_a_cooldown(roms: tuple[bytes, bytes]) -> None:
    """Generator step 5 (specials proof v23): the generated D,U program in Directional Ice Up's
    slot: the afterimage runs as an effect-class process (not a projectile: specials stay free),
    the relocation is Sektor's reposition as a subroutine (enemy in range required by the
    condition), and MKT's 0x40-tick cooldown (32 host ticks) holds a word the condition reads."""

    from mkmszr.fighter_import import lower_special

    built = fb.build(*roms, "rayden")
    assert built.selectors["teleport"] == 5
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    assert 0x24040015 in ws  # li a0, 0x15: the afterimage process class
    # MKT's cooldown as a clock stamp (v30): the move stamps the 60 Hz clock, the condition
    # refuses until 0x40 ticks have passed (v23-v29: a timer process of 32 host ticks)
    assert 0x240A0040 in ws and 0x012A502B in ws  # li t2, 0x40; sltu t2, t1, t2
    assert ws.count(0x3C09802E) == 2  # lui t1, 0x802E: each condition reads the clock
    assert 0x24040086 in ws  # li a0, 134: the relocation distance (67 px)
    assert lower_special.RELOCATE_RANGE == 592


@needs_roms
def test_teleport_reappears_with_the_getup_and_its_own_sound(roms: tuple[bytes, bytes]) -> None:
    """v24 (owner on v23): the reappear is the body's getup (host primary 0x22, MKT table-0
    index 0x22, selected from table 0) with its built-in sound 7; the move's own sounds are
    skipped (owner: one sound); the afterimage draws at its owner's +0xD8 in the palette its
    frames name (Rayden's silhouette 0x800B9AF0)."""

    built = fb.build(*roms, "rayden")
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    k = next(i for i, w in enumerate(ws) if w == 0x00002021 and ws[i + 1] == 0x24050022)  # a0 = 0, a1 = 0x22
    assert ws[k + 2 : k + 4] == [0x3C198003, 0x2739FE54]  # the select 0x8002FE54, through t9
    assert 0x8E2600D8 in ws  # lw a2, 0xD8(s1): the owner's draw offset for the afterimage


@needs_roms
def test_rayden_shocker_release_hold_and_reaction(roms: tuple[bytes, bytes]) -> None:
    """Specials proof v25: the Shocker (MKT 0x800AB9F4, HP released after 0x38 donor ticks)
    sits in a release table hooked into the HP release event; the HP press callback is
    wrapped to count the hold; the strike selects the shock-hold reaction in spare entry
    0x4E (blocked entry 0x0E), whose routine is in the payload."""

    from mkmszr.fighter_import import commands as cmds
    from mkmszr.fighter_import import lower_projectile as lp

    built = fb.build(*roms, "rayden")
    assert built.reactions["shock_hold"] == 0x4E
    ((_, record),) = dict(built.report["strike_records"])["shocker"]
    assert record[8:12] == bytes((0x4E, 0x05, 0x20, 0x00))  # reaction, blocked, damage 32, no chip
    # v26 (owner on v25): the host box is (front edge, y, width back, height); v25's (0, ..., 61)
    # lay behind him. MKT's grab range |dx| < 0x37 in front:
    assert record[:8] == bytes.fromhex("0037000000370078")
    # v27 (owner on v26): a grab cannot be blocked (record +0xC bit 0x0002, the block test's
    # no-block bit) and costs twice Ice Blast's Ice (owner rule)
    assert record[12:14] == bytes.fromhex("0003")
    assert built.report["costs"]["shocker"] == 0x40 and built.report["costs"]["lightning"] == 0x20
    entry = lp.REACTION_TABLE - 0x7FFFF400 + 4 * 0x4E
    target = int.from_bytes(built.rom[entry : entry + 4], "big")
    assert built.link_va <= target < built.link_va + len(built.payload)
    slot = lambda record: record + cmds.PLAYER_TYPE_SLOT - cmds.VA_TO_ROM
    hooks = [int.from_bytes(built.rom[slot(r) : slot(r) + 4], "big")
             for r in (cmds.HP_RELEASE_RECORD, cmds.HP_PRESS_RECORD)]  # fmt: skip
    assert all(built.link_va <= h < built.link_va + len(built.payload) for h in hooks)
    ws = [int.from_bytes(built.payload[i : i + 4], "big") for i in range(0, len(built.payload), 4)]
    # v30: the hold is MKT's 0x38 ticks on the 60 Hz clock, since the press stamp (v25-v29: a
    # counter process whose running flag a stock process kill could leave stuck)
    assert 0x240A0038 in ws  # li t2, 0x38
    # v28 (owner on v27: "the enemies are being held for too long"): MKT holds the victim 96 donor
    # ticks while he plays 32 frames, 3 ticks each (0x80073378(8)). The victim's hold is 48 host
    # ticks; his shaking was 16 frames in 32 (the repeat count was scaled), so the victim stayed
    # held after he stopped. Now 32 frames in 48: 16 passes of [sleep 2, frame, sleep 1, frame];
    # the miss 7 passes (14 frames, MKT 0x8000E0C0(3, 0xF)).
    # SMRE step 2 (the grab rule): MKT's pose, a 3-tick pause, then 8 shocks of [frame, 3 ticks] x 4;
    # the victim's hold covers both (3 + 96 donor ticks = 50 host ticks)
    assert 0x24120032 in ws  # addiu s2, zero, 50: the victim's hold
    assert 0x24140008 in ws and 0x24140007 in ws  # addiu s4, zero, 8 / 7: the shocks, the miss
    # v27: sound 5 (MKT event 0x205, two tracks) is ported: one chain per track, both tracks in one
    # host event read from the sample area
    from mkmszr.fighter_import import sound

    assert "unported_sounds" not in built.report
    assert built.report["multi_track_sounds"] == [("shocker", 5, 2)]
    hosts = [c.event for c in built.report["chains_used"]]
    multi = [e for e in hosts if int.from_bytes(built.rom[sound.MSZ_EVENT_DEFS + 16 * e :][:2], "big") == 2]
    assert len(multi) == 1 and len(hosts) == 16  # the teleport's skipped sounds take no chain
    d = sound.MSZ_EVENT_DEFS + 16 * multi[0]
    at = sound.MSZ_TRACKS + int.from_bytes(built.rom[d + 8 : d + 12], "big")
    assert built.samples[0] <= at < built.samples[1] and int.from_bytes(built.rom[d + 4 : d + 8], "big") == 0x6C



# SMRE (2026-11-27): all five of Rayden's moves are written by the Special Move Recompile Engine
# at build time (his description's ``smre``). Step 1 (four moves) was byte-identical to specials
# proof v30 (payload c97596af...); step 2's grab rule writes the Shocker with MKT's 3-tick pause
# after the grab and a hold that ends with his shaking.
RAYDEN_V30_PAYLOAD_SHA256 = "05458f184d51373b"


@needs_roms
def test_rayden_and_reptile_moves_come_from_smre(roms: tuple[bytes, bytes]) -> None:
    built = fb.build(*roms, "rayden")
    assert hashlib.sha256(built.payload).hexdigest().startswith(RAYDEN_V30_PAYLOAD_SHA256)
    assert set(built.report["smre"]) == {"lightning", "reversed_lightning", "teleport", "torpedo", "shocker"}
    assert all(v["record"].startswith("0x800AB") for v in built.report["smre"].values())
    rep = fb.fd.load("reptile")
    assert set(rep.smre) == {"acid_spit", "forceball_fast", "forceball_slow", "elbow_dash", "invisibility"}
