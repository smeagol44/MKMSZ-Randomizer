"""MKMSZ lowering of the ``projectile`` move component (Fighter recompiler plan, milestone 2).

The generic projectile on the native enemy-projectile path, no Ice-root patching (Wiki
``Fighter-Recompiler-Components#generic-projectile-lowering``; Runtime-confirmed bounded in
proof v06). From a move-program ``projectile`` step this module

* reads the donor art from the MKT script part the step names (frames, loop, and a palette
  bound by token 13), lays the frames out as type-4 images with one 64-colour palette record
  in the fighter file, and writes host frame scripts into free table-1 slots
  (:func:`place_art`);
* hosts the donor sounds (:func:`install_sounds`);
* lowers the strike record and the victim reaction by meaning (:func:`lower`);
* emits the spawn sequence, the class-0x700 projectile process and its data
  (:func:`emit_spawn`, :func:`emit_process`, :func:`emit_data`).

Timing: one host tick per MKT process tick for frames and sound cadence; speed through the
accepted rocket conversion (``physics.fold_donor_speeds``). Offsets: donor pixels, 2 world units
each; for this actor ``0x80031208``'s +y is down, as the donor's.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

from . import effects, host, physics, sound
from .body_build import Donor
from .mips import Assembler
from .mipsdis import decode
from .script import MKT

# Host routines and data (Static-confirmed; Wiki Function-Registry)
F_CLONE = 0x8002830C
F_PROJ_BUILD = 0x80047160
F_SELECT = 0x8002FE54
F_ADVANCE = 0x800304C0
F_SLEEP = 0x80028794
F_OFFSCREEN = 0x80035088
F_COLLIDE = 0x8002BA04
F_ACTOR_REMOVE = 0x80024B00
F_TEX_RELEASE = 0x8001C424
F_EXIT = 0x80028564
F_OFFSET = 0x80031208
ACTOR_LIST = 0x80111C98
PROJECTILE_CLASS = 0x700  # collision core gate 0x8002BB40: hits enemies
TYPE_FILE_TABLE = 0x800A0324  # [type] -> fighter-file base global; type 4 is 0 in stock
PLAYER_FILE_BASE = 0x80291C10
PLAYER_TYPE = 4
REACTION_TABLE = 0x800A1190
DUMMY_REACTION = 0x8004E0C0
OFFSCREEN_MARGIN = 200
ACTOR_D8 = 0x46  # projectile actor +0xD8, as Quan Chi's
UNITS_PER_PX = 2
MKT_TABLE1 = 0x168  # MKT get_char_ani table 1 (heap-relative)
KSEG1_TO_KSEG0 = 0x20000000
FOLLOW_SP = 0x24  # the child's frame: four offset words (0x20 is the texture handle)
FOLLOW_FIELDS = (host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Y, host.ACTOR_Z)
TRAIL_TICK_SP = 0x1C  # the child's frame: the trail has started (MKT rocket_smoke's toggle)
OWNER_SUBLAYER_SP, OWNER_PRIORITY_SP = 0x38, 0x3C  # the owner's layer, read before the build
ACTOR_PRIORITY = 0x5C
TRAIL_FIELDS = FOLLOW_FIELDS  # the flight's own position, kept while a trail puff starts behind it
HIT_X, HIT_Y = 0x802E83D8, 0x802C1BA0  # a projectile's victim x / y at its last hit (0x8002DCB0)
ACTOR_FLAGS, FACING_BIT = 0x8C, 0x10  # actor facing (0x800344F4, 0x8002B6F4)
ACTOR_SUBLAYER = 0xEC  # draw sub-layer within the actor priority +0x5C (as projectile.py)

# Victim reactions by meaning -> host. "base": a stock host reaction (leaf, no branches) copied
# into the payload with the donor arc converted; "host": a stock reaction used as is.
REACTION_LOWERING: dict[str, dict[str, Any]] = {
    "knockback_arc": {
        "base": 0x80057C14,  # host reaction 0x25: 0x800321D0(-0x3999A, -0x5A3D7, 0x8EE1), toward
        "length": 0x110,
        "donor_arc": (0x2CCCC, -0x6CCCC, 0x5199),  # MKT 0x80054830 (reaction 0x71): x toward, y, g
        "patch": {
            0x30: 0x3C05FFFC,
            0x33: 0x34A56667,
            0x34: 0x3C06FFFA,
            0x3B: 0x34C65C29,
            0x3D: 0x34078EE1,
        },
        "drop_sound": (8, 0x0C019342),  # jal 0x80064D08: stock hit sound 0x185
        # Victim morphs, run first as the stock launch reaction 0x0C (0x80052898) does: the
        # two-file enemies rebind to their full fighter file before a shared root is played
        # (0x800572C4: Temple MONK3 type 2 -> MONK2 file 0x89, type 1; 0x80057478: types
        # 0x15..0x17 and the other two-file families). Host 0x25 has no morph, so on a MONK3
        # its root 0x1E read the unfilled word 0xFFFFFFFF and the sprite setup crashed
        # (composition v02 save state, TLB store miss at 0x8001BF04).
        "morph": (0x800572C4, 0x80057478),
        "morph_at": 2,  # after the frame and the saved ra
    },
}
# The victim's end of Rayden's torpedo carry (``lower_special.emit_carry_reaction``). MKT
# 0x8005391C (given to the victim by 0x8006D3B4): stop, back on the ground, face him, its slot
# 0x1E in two phases, then a getup (0x800587FC(0x21)): it slumps where the carry ended. The host:
# the same lifted knockback with no push and no lift, so the victim falls from where it was held
# (owner on v03: it falls only when released) into root 0x1E and the host landing/getup.
# Specials proof v03-v07 used do_jump(0x33333, -0x6CCCD, 0x5199) here: that is Rayden's own bounce
# (0x8004558C), misread as the victim's (generator, 2026-11-25).
REACTION_LOWERING["torpedo_carry_release"] = {
    **REACTION_LOWERING["knockback_arc"],
    "donor_arc": (0, 0, 0x5199),
}
# Stumble-kind reactions: a lifted copy of the host Fire spiked-rod trap stumble, the reaction
# Sektor's rocket was accepted with (robo_zap, proof v35), without its 8-tick hit pause, its
# push rescaled by the donor push over MKT's rocket push (zap_stumble 0x33333, host 0x56666).
REACTION_LOWERING["acid_stagger"] = {
    "kind": "stumble",
    "base": 0x80051280,
    "end": 0x800513AC,
    "pause": 0x80051318,  # jal 0x80028794 (sleep 8)
    "push": (0x80051338, 0x80051340, 0x80051344, 0x80051348),  # lui/ori +push, lui/ori -push
    "stock_push": 0x56666,
    "donor_push": 0x26666,  # MKT reaction 0x72 (0x800547C8): +0x420 = 0x26666, then 0x80057F94
    "donor_ref": 0x33333,  # MKT zap_stumble (r_rocket), the host's accepted 0x56666
}
# MKT reaction 0x3B (r_rocket 0x80057B08 -> zap_stumble 0x80057BEC, Sektor's rockets): the same
# stumble at MKT's rocket push, the host's accepted 0x56666 (robo_zap, proof v35).
REACTION_LOWERING["rocket_stumble"] = {**REACTION_LOWERING["acid_stagger"], "donor_push": 0x33333}
# MKT reaction 0x80 (0x800539A8, Rayden's lightning): the hit preamble, a push away from the
# attacker at 0x26666, the hit voice, the victim's slot 0x20 played twice at rate 2 with its
# per-fighter shock palette (0x800A38B0[fighter], into process +0x440): the victim staggers back
# and blinks cyan. The host: Acid Spit's stumble (the same push; it plays the victim's root 0x20)
# plus a blink helper (``blink``) that alternates the victim's colour with cyan, as host enemies
# have no MKT palettes. The host draw (0x80018A8C) tints each actor through its per-vertex
# colours, red +0xA0..+0xA3, green +0xA4..+0xA7, blue +0xA8..+0xAB (one byte per corner), and
# recomputes them from the stage lighting (0x80024F74) every draw while actor +0x8C bit 0x1000 is
# set. The host's own flash does the same: 0x80034740 clears the bit and writes the colours (the
# shocked player brightens them, 0x80055858), 0x80034658 sets it again. Specials proof v16 wrote
# +0xFC/+0xFE/+0x100, which the draw reads only as alpha (+0xFC, under +0x8C & 0x6000): no blink.
REACTION_LOWERING["shock_stagger"] = {
    **REACTION_LOWERING["acid_stagger"],
    "donor_push": 0x26666,  # MKT 0x800539E8: away_x_vel 0x26666
    # owner on v17 (2026-11-26): half the speed, cyan and normal two frames each (every 2: one)
    "blink": {"colour": (0x20, 0xFF, 0xFF), "count": 8, "every": 4},
}
# MKT reaction 0x81 (0x80053A48, the reversed lightning's strikes): 0x80 with towards_x_vel, the
# victim pushed towards the attacker (hit from behind, it goes the bolt's way).
REACTION_LOWERING["shock_stagger_toward"] = {
    **REACTION_LOWERING["shock_stagger"],
    "donor_push": -0x26666,  # MKT 0x80053A88: towards_x_vel 0x26666
}
BLINK_PROCESS_ID = 0x100  # as the stealth timer
ACTOR_LIT_BIT = 0x1000  # actor +0x8C: colours from the stage lighting every draw
ACTOR_VERTEX_RGB = (0xA0, 0xA4, 0xA8)  # four corner bytes each
NORMAL_RGB = 0x80  # 0x80034740's unlit colour
# Host-kind reactions: a stock reaction-table entry used as is (no payload code). The roundhouse
# launch 0x0C knocks the victim away and runs the victim morphs (Rayden's lightning stand-in).
REACTION_LOWERING["tether_pull"] = {"kind": "tether"}
REACTION_LOWERING["launch"] = {"kind": "host", "slot": 0x0C}
BLOCKED_LOWERING = {"blocked": 0x05}
# Strike record +0xC flags: every stock record has 0x0001. The block test 0x80034888 (a1 = this
# halfword) reports no block when bit 0x0002 is set (0x80034940; Static-confirmed): a grab.
STRIKE_FLAGS, STRIKE_UNBLOCKABLE = 0x0001, 0x0002


def host_reaction(meaning: str) -> int | None:
    """The stock reaction-table entry of a host-kind meaning, else None."""

    spec = REACTION_LOWERING[meaning]
    return spec["slot"] if spec.get("kind") == "host" else None


def stumble_push(meaning: str) -> int:
    spec = REACTION_LOWERING[meaning]
    return round(spec["stock_push"] * spec["donor_push"] / spec["donor_ref"])


def lift_stumble(clean: bytes, meaning: str, dst_va: int) -> bytes:
    """A stumble-kind reaction lifted to run at ``dst_va`` (``fighter_import.lifter``)."""

    from . import lifter

    spec = REACTION_LOWERING[meaning]
    base, end = spec["base"], spec["end"]
    code = clean[base - 0x7FFFF400 : end - 0x7FFFF400]
    push = stumble_push(meaning) & 0xFFFFFFFF  # negative: towards the attacker (MKT 0x81)
    neg = -stumble_push(meaning) & 0xFFFFFFFF
    up, uo, dn, do = spec["push"]
    stock = {up: 0x3C020005, uo: 0x34426666, dn: 0x3C02FFFA, do: 0x3442999A, spec["pause"]: 0x0C00A1E5}
    for va, word in stock.items():
        if int.from_bytes(code[va - base : va - base + 4], "big") != word:
            raise ValueError(f"stumble word at 0x{va:08X} is not stock")
    patches = {spec["pause"]: 0, up: 0x3C020000 | push >> 16, uo: 0x34420000 | push & 0xFFFF,
               dn: 0x3C020000 | neg >> 16, do: 0x34420000 | neg & 0xFFFF}  # fmt: skip
    result = lifter.lift(code, base, dst_va, patches=patches, cached_calls=True)
    lifter.verify(code, result)
    return result.code


def _int(v: Any) -> int:
    return int(v, 0) if isinstance(v, str) else int(v)


# ---- donor art ------------------------------------------------------------------------------
@dataclass(frozen=True)
class DonorPart:
    frames: tuple[int, ...]  # frame records (heap-relative), in script order
    palette: int | None  # palette bound by token 13 (the next frame record's palette word)
    loops: bool
    loop_from: int = 0  # frame index the loop jumps back to (MKT acid: past the spit frames)


def donor_part(donor: Donor, anim: dict[str, Any], *, first_only: bool = False) -> DonorPart:
    """Frames of part ``anim['part']`` (1-based) of an MKT table-0/1 animation."""

    table, slot, part = _int(anim["table"]), _int(anim["slot"]), _int(anim.get("part", 1))
    base = 0 if table == 0 else MKT_TABLE1
    p = donor.m32(base + 4 * slot)
    for _ in range(part - 1):  # skip parts: each ends with a bare 0 word
        while True:
            v = donor.m32(p)
            p += 4
            if v == 0:
                break
            if MKT.is_token(v):
                p += 4 * len(MKT.operands[v])
    frames: list[int] = []
    at: list[int] = []
    palette, bind_next, loops, loop_from = None, False, False, 0
    while True:
        v = donor.m32(p)
        if v == 0:
            break
        if v == 1:
            loops = True
            target = donor.m32(p + 4)
            loop_from = at.index(target) if target in at else 0
            break
        if MKT.is_token(v):
            if v == 13:
                bind_next = True
            elif v != 12:
                raise ValueError(f"MKT token {v} in a projectile part is not supported")
            p += 4 * (1 + len(MKT.operands[v]))
            continue
        if bind_next:
            palette, bind_next = donor.m32(v + 0x14), False
        frames.append(v)
        if first_only:
            break
        at.append(p)
        p += 4
    return DonorPart(tuple(frames), palette, loops, loop_from)


@dataclass(frozen=True)
class Helper:
    """MKT's throw helper (token 11 creates it from a frame, tokens 12/14 step it: e.g.
    Reptile's forceball forming in his hands): its frame for each body frame from ``start``."""

    frames: tuple[int, ...]
    start: int  # index of the body frame it first shows with


def donor_helper(donor: Donor, anim: dict[str, Any]) -> Helper | None:
    """The helper shown during part ``anim['part']`` (1-based, default 1) of the animation."""

    table, slot, part = _int(anim["table"]), _int(anim["slot"]), _int(anim.get("part", 1))
    p = donor.m32((0 if table == 0 else MKT_TABLE1) + 4 * slot)
    for _ in range(part - 1):
        while True:
            v = donor.m32(p)
            p += 4
            if v == 0:
                break
            if MKT.is_token(v):
                p += 4 * len(MKT.operands[v])
    shown: list[int | None] = []
    helper, step_next = None, False
    while True:
        v = donor.m32(p)
        if v in (0, 1):
            break
        if MKT.is_token(v):
            if v == 11:
                helper = donor.m32(p + 4)
            step_next = v in (12, 14)
            p += 4 * (1 + len(MKT.operands[v]))
            continue
        if step_next:
            helper, step_next = v, False
        else:
            shown.append(helper)
        p += 4
    if helper is None:
        return None
    start = next(i for i, h in enumerate(shown) if h is not None)
    return Helper(tuple(h for h in shown[start:] if h is not None), start)


def mirror_axis(donor: Donor, rels: list[int], window: int = 7) -> int:
    """The anchor-relative column where an animation's frames, taken together, are densest (a
    ``window``-wide moving sum over every frame's pixels placed by its anchor): the core of an
    effect (Rayden's lightning burst: where its star is)."""

    hist: dict[int, int] = {}
    for rel in rels:
        f = donor.frame(rel)
        w, stride, padded = f["w"], f["stride"], f["padded"]
        for col in range(w):
            n = sum(1 for y in range(len(padded) // stride) if padded[y * stride + col])
            hist[col - f["x"]] = hist.get(col - f["x"], 0) + n
    lo, hi = min(hist), max(hist)
    half = window // 2
    sums = {a: sum(hist.get(b, 0) for b in range(a - half, a + half + 1)) for a in range(lo, hi + 1)}
    return max(sums, key=lambda a: (sums[a], -a))


def _frame(donor: Donor, rel: int, shift: int, mirror_at: int | None = None) -> effects.EffectFrame:
    """A donor frame for effect art. ``mirror_at``: mirrored around that anchor-relative column
    (:func:`mirror_axis`): rows reversed and the anchor moved so column ``a`` lands on
    ``2 * mirror_at - a``. One axis for every frame of an animation keeps its frames in place
    relative to each other (see ``place_art``'s ``impact_mirror``)."""

    f = donor.frame(rel)
    padded, x_anchor = f["padded"], f["x"]
    if mirror_at is not None:
        w, stride = f["w"], f["stride"]
        rows = [padded[y * stride : (y + 1) * stride] for y in range(len(padded) // stride)]
        padded = b"".join(bytes(r[:w][::-1]) + bytes(r[w:]) for r in rows)
        # column c sat at (c - x); its mirror w - 1 - c must sit at 2 * mirror_at - (c - x)
        x_anchor = w - 1 - f["x"] - 2 * mirror_at
    indices = bytes(0 if v == 0 else v + shift for v in padded)
    return effects.EffectFrame(f["w"], f["eh"], x_anchor, f["y"], indices)


@dataclass(frozen=True)
class ArtLayout:
    palette_record: int  # file offset of the 64-colour record (count word)
    flight_slot: int
    impact_slot: int | None
    impact_ticks: int
    tex_w: int
    tex_h: int
    helper_slot: int | None = None
    helper_start: int = 0  # body pose (0-based) the helper first shows with
    helper_frames: int = 0  # helper frames, one per body pose from helper_start
    # Virtual entries (no free table-1 slot): the *_slot fields are indices whose
    # ``0x104 + 4 * index`` word, inside the art, holds the script offset; projectile_actor_build
    # takes any index, fighter_select_animation only 16-bit ones, so the code sets cursors by
    # offset instead (``*_at``).
    virtual: bool = False
    flight_at: int = 0
    impact_at: int = 0
    helper_at: int = 0
    # A homing projectile's direction parts (MKT point_rocket): each part's looping script
    direction_at: tuple[int, ...] = ()


def place_art(
    file87: bytearray,
    mkt: bytes,
    donor_id: int,
    step: dict[str, Any],
    slots: tuple[int, int] | None,
    budget: int,
    at: int | None = None,
    helper: Helper | None = None,
    helper_slot: int | None = None,
    throw_rate: int = 0,
    impact_mirror: bool = False,
    render_dy_px: int = 0,
) -> ArtLayout:
    """Put the projectile's art in the fighter file and point table-1 ``slots`` (empty in
    stock) at its flight and impact scripts. By default it is appended; with ``at`` it is
    written from that offset inside the file (e.g. the body region's free tail, Sektor proof
    v47's heap-neutral placement) and must end by ``budget``.

    ``impact_mirror``: the impact animation is mirrored around its core, one axis for all its
    frames (:func:`mirror_axis`). Rayden's lightning burst is placed by MKT's flip and offset,
    star on the enemy, but faces away from him on the host (specials proof v09). Flipping the
    actor back (v10-v12) mirrored it around its anchor, outside the frames, ~115 px off (owner
    save state); mirroring each frame within its box (v13) put the off-centre star behind the
    enemy; around each frame's own core (v14) the frames jumped against each other (owner)."""

    cursor = len(file87) if at is None else at

    def put(data: bytes) -> int:
        nonlocal cursor
        start = cursor
        if at is not None and set(file87[start : start + len(data)]) - {0xFF}:
            raise ValueError(f"fighter file bytes at 0x{start:X} are not free")
        if start + len(data) > len(file87):
            file87.extend(bytes(start + len(data) - len(file87)))
        file87[start : start + len(data)] = data
        cursor = start + len(data)
        return start

    donor = Donor(mkt, donor_id)
    # The tether child keeps the first frame until its hit handoff.
    flight = donor_part(donor, step["art"], first_only="tether" in step)
    directions = step.get("homing", {}).get("directions")
    parts = ([donor_part(donor, {**directions["anim"], "part": k + 1}) for k in range(_int(directions["parts"]))]
             if directions else [])  # fmt: skip
    impact_step = step.get("impact", {})
    impact = donor_part(donor, impact_step["anim"]) if "anim" in impact_step else None
    if "palette" in step:
        flight_palette = list(effects.mkt_palette(mkt, _int(step["palette"])))
    else:  # the donor fighter's body palette
        from .projectile import mkt_color_to_host

        flight_palette = [mkt_color_to_host(c) for c in donor.palette()]
    if len(flight_palette) > 32:
        raise ValueError("flight palette must fit 32 colours")
    colours = flight_palette + [0] * (32 - len(flight_palette))
    # One drawn frame per (part, donor frame): a donor frame can open the impact and close the
    # flight loop (Rayden's 0x2024); the impact's copy takes the impact palette (and mirror), so
    # keyed by the donor frame alone it replaced the flight's: the bolt jumped ~115 px ahead
    # once per loop (specials proof v16, owner video).
    keys = [("flight", r) for r in dict.fromkeys([*flight.frames, *(r for p in parts for r in p.frames)])]
    frames = [_frame(donor, r, 0) for _, r in keys]
    if "tether" in step:
        # Donor clips from a left-origin rope object. MKMSZ clips back from the tip.
        frames = [replace(f, anchor_x=f.width) for f in frames]
    if render_dy_px:
        # The host subtracts the frame's Y anchor from its projected position.
        frames = [replace(f, anchor_y=f.anchor_y - render_dy_px) for f in frames]
    if impact is not None:
        impact_palette = (
            list(effects.mkt_palette(mkt, impact.palette)) if impact.palette else flight_palette
        )
        colours += impact_palette + [0] * (32 - len(impact_palette))
        impact_rels = list(dict.fromkeys(impact.frames))
        axis = mirror_axis(donor, impact_rels) if impact_mirror else None
        frames += [_frame(donor, r, 32, axis) for r in impact_rels]
        keys += [("impact", r) for r in impact_rels]
    if helper is not None:  # the helper's frames take the flight palette (MKT binds it from them)
        helper_rels = [r for r in dict.fromkeys(helper.frames) if ("flight", r) not in keys]
        frames += [_frame(donor, r, 0) for r in helper_rels]
        keys += [("flight", r) for r in helper_rels]
    art = effects.EffectArt(tuple(frames), tuple(colours), compressed=True)
    placed = effects.layout(art, (cursor + 3) & ~3)
    put(bytes(placed.offset - cursor) + placed.data)
    script_at = placed.script - placed.offset
    shape = {
        key: int.from_bytes(placed.data[script_at + 4 * i : script_at + 4 * i + 4], "big")
        for i, key in enumerate(keys)
    }

    def script(words: list[int]) -> int:
        return put(b"".join(w.to_bytes(4, "big") for w in words))

    rate = _int(step["rate"])
    # Frames shown by the close-range check steps appear once each (one advance per step);
    # the rest at ``rate``; the loop goes back to the donor's loop frame (MKT acid: 0x31B0).
    early = len(step.get("checks", []))
    flight_words = [shape["flight", r] for r in flight.frames[:early]]
    flight_words += [shape["flight", r] for r in flight.frames[early:] for _ in range(rate)]
    loop_word = (flight.loop_from if flight.loop_from < early
                 else early + (flight.loop_from - early) * rate)  # fmt: skip
    flight_at = cursor
    script(flight_words + [1, flight_at + 4 * loop_word])  # loop
    direction_at: list[int] = []
    for part in parts:  # every direction's loop at the flight rate (the flight's own is reused)
        if part.frames == flight.frames:
            direction_at.append(flight_at)
            continue
        at_ = cursor
        script([shape["flight", r] for r in part.frames for _ in range(rate)] + [1, at_ + 4 * part.loop_from * rate])
        direction_at.append(at_)
    impact_ticks = 0
    entries = [(slots[0] if slots else 0, flight_at)]
    if impact is not None:
        impact_rate = _int(impact_step["rate"])
        impact_words = [shape["impact", r] for r in impact.frames for _ in range(impact_rate)]
        impact_ticks = len(impact_words)
        impact_at = cursor
        script(impact_words + [1, impact_at + 4 * (impact_ticks - 1)])  # hold the last frame
        entries.append((slots[1] if slots else 0, impact_at))
    helper_at = 0
    if helper is not None:
        if (helper_slot is None and slots is not None) or throw_rate <= 0:
            raise ValueError("a helper needs its table-1 slot and the throw's frame rate")
        # One word per helper frame: the helper process points its cursor at the frame for the
        # owner's current body pose (:func:`emit_helper`), so it cannot drift from the body.
        helper_at = cursor
        n = len(helper.frames)
        script([shape["flight", r] for r in helper.frames] + [1, helper_at + 4 * (n - 1)])
        if slots is not None:
            entries.append((helper_slot, helper_at))
    virtual = slots is None
    if virtual:  # entry words in the art; their indices stand in for table-1 slots
        index = {}
        for name, where in (("flight", flight_at), ("impact", impact_at if impact else 0),
                            ("helper", helper_at)):  # fmt: skip
            if where:
                index[name] = (put(where.to_bytes(4, "big")) - 0x104) // 4
        flight_slot, impact_slot = index["flight"], index.get("impact")
        helper_slot = index.get("helper")
    else:
        flight_slot, impact_slot = slots[0], slots[1] if impact else None
    if cursor > budget:
        raise ValueError(f"projectile art ends at 0x{cursor:X}, past the budget 0x{budget:X}")
    for slot, where in entries if not virtual else ():
        off = 0x104 + 4 * slot
        if file87[off : off + 4] != bytes(4):
            raise ValueError(f"table-1 slot 0x{slot:X} is not empty")
        file87[off : off + 4] = where.to_bytes(4, "big")
    w, h = art.slot_size
    if helper is None and not virtual and not direction_at:
        return ArtLayout(placed.offset, flight_slot, impact_slot, impact_ticks, w, h)
    return ArtLayout(placed.offset, flight_slot, impact_slot, impact_ticks, w, h,
                     helper_slot, helper.start if helper else 0, len(helper.frames) if helper else 0,
                     virtual, flight_at, impact_at if impact else 0, helper_at, tuple(direction_at))  # fmt: skip


# ---- sounds, strike and reaction --------------------------------------------------------------
def _sounds(step: dict[str, Any]) -> list[tuple[str, Any]]:
    """(name, sound) the step hosts: the launch (``sound``, Sektor's missile), hum, impact."""

    wanted = [("launch", step.get("sound")), ("hum", step.get("hum", {}).get("sound")),
              ("impact", step.get("impact", {}).get("sound"))]  # fmt: skip
    return [(name, snd) for name, snd in wanted if snd]


def projectile_sounds(step: dict[str, Any]) -> list[str]:
    """The sounds a projectile step hosts (``install_sounds`` takes one chain each)."""

    return [name for name, _ in _sounds(step)]


def new_sounds(step: dict[str, Any], known: dict[int, int] | None = None) -> int:
    """How many of the step's sounds are not hosted yet (``known``: fighter sound -> event)."""

    return len({_int(snd["fighter"]) for _, snd in _sounds(step) if "fighter" in snd} - set(known or {}))


def install_sounds(
    rom: bytearray, clean: bytes, mkt: bytes, donor_id: int, step: dict[str, Any],
    chains: tuple[sound.HostChain, ...], sample_rom: int, known: dict[int, int] | None = None,
) -> tuple[dict[str, int], int]:  # fmt: skip
    """Host the launch, hum and impact sounds; returns their host events and the next sample
    address. ``known`` (fighter sound -> host event): the projectile sounds already hosted for
    another art (Sektor's homing missile: the straight missile's boom), reused and extended."""

    bank = sound.MktSoundBank(mkt)
    events: dict[str, int] = {}
    free = list(chains)
    known = {} if known is None else known
    for name, snd in _sounds(step):
        if "fighter" not in snd:
            raise ValueError("only fighter sounds are supported")
        n = _int(snd["fighter"])
        if n not in known:
            chain = free.pop(0)
            donor = bank.event(bank.fighter_event(donor_id, n))
            sample_rom = sound.install(rom, clean, donor, chain, sample_rom)
            known[n] = chain.event
        events[name] = known[n]
    return events, sample_rom


def lifted_reaction(clean: bytes, meaning: str) -> list[int]:
    """The host base reaction with the donor arc converted (standard-jump calibration)."""

    spec = REACTION_LOWERING[meaning]
    base, n = spec["base"], spec["length"] // 4
    words = [
        int.from_bytes(clean[base - 0x7FFFF400 + 4 * i : base - 0x7FFFF400 + 4 * i + 4], "big")
        for i in range(n)
    ]
    for i, w in enumerate(words):
        if decode(w, base + 4 * i).is_branch:
            raise ValueError("the base reaction must be a straight leaf")
    ax, ay, ag = arc(meaning)  # base convention: negative x = toward the attacker
    new = {0x30: 0x3C050000 | ((ax >> 16) & 0xFFFF), 0x33: 0x34A50000 | (ax & 0xFFFF),
           0x34: 0x3C060000 | ((ay >> 16) & 0xFFFF), 0x3B: 0x34C60000 | (ay & 0xFFFF),
           0x3D: 0x34070000 | (ag & 0xFFFF)}  # fmt: skip
    for i, stock in spec["patch"].items():
        if words[i] != stock:
            raise ValueError(f"base reaction word {i} is not stock")
        words[i] = new[i]
    index, stock = spec["drop_sound"]
    if words[index] != stock:
        raise ValueError("base reaction sound call is not stock")
    words[index] = 0
    morph: list[int] = []
    for target in spec.get("morph", ()):
        # lui v0, 0x802F; lw v0, CURRENT_CTRL(v0); lw a0, actor(v0); jal target; nop
        morph += [0x3C02802F, 0x8C42CE20, 0x8C4406E0, 0x0C000000 | ((target >> 2) & 0x3FFFFFF), 0]
    at = spec.get("morph_at", 0)
    return words[:at] + morph + words[at:]


@dataclass(frozen=True)
class Tether:
    reach_px: int
    pull_speed: int  # host velocity encoding
    stop_px: int
    daze_ticks: int  # host ticks


@dataclass(frozen=True)
class Lowered:
    art: ArtLayout
    speed: int  # host x speed (world units, 16.16)
    dx: int
    dy: int
    record: bytes  # 16-byte host strike record
    reaction_words: tuple[int, ...]
    hum_event: int | None
    hum_every: int
    impact_event: int | None
    reaction_meaning: str = "knockback_arc"
    checks: tuple[bytes, ...] = ()  # close-range strike records, one per early frame
    impact_at_opponent: bool = False
    impact_dx: int = 0  # world units, after facing the attacker (MKT multi_adjust_xy)
    impact_flip: bool = True  # MKT flip_single (Acid Spit v10: mirrored on the host)
    # Place an "at opponent" impact on the enemy the strike hit, at its whole position (path,
    # path position, x, y, z): with a path (+0xDC), the offset 0x80031208 only advances the path
    # position +0xE0 and x follows from it. On the ordinary hit path the collision core records a projectile
    # victim's x / y (HIT_X / HIT_Y, 0x8002DCB0) and then links the player and the victim (player
    # +0x640 = victim, 0x8002DD18). The projectile's own +0x640 is the player's opponent at
    # launch, which can be another enemy (Rayden's lightning burst on a far pillar, v10); copying
    # x and y alone left it at the bolt's path position on a walkway (v11, Wind).
    impact_at_hit: bool = False
    # Keep the projectile's own y at the opponent: MKT's objects share the fighters' ground y, but
    # the host projectile is raised by its offset (Acid Spit v13: splash 36 px below the hit).
    impact_keep_y: bool = False
    # MKT's burst copies the opponent's x / y velocity into itself every tick (0x800781F0), so it
    # rides with the push. The host: every tick the impact keeps its offset from the victim it
    # was placed on (path position, x, y, z), until the victim's controller holds another actor.
    impact_follow: bool = False
    # MKT's wrap (Rayden's reversed lightning, flight callback 0x80078070): the first time the
    # projectile leaves the screen it re-enters past the opposite edge; for ``wrap_cooldown``
    # ticks the flight keeps it, then it ends at the next exit as usual (0 = no wrap).
    wrap_cooldown: int = 0
    # MKT's rocket (Sektor, rocket1_proc 0x8007C100): a sound as it starts; the start speed
    # (``speed_reacting`` while the opponent is in a reaction); the flight callback's
    # acceleration (v += v >> n every donor tick, up to the cap: host speeds per host tick, two
    # donor ticks each, the last one steady); a trail effect (MKT rocket_smoke: create_fx every
    # other donor tick = every host tick, ``trail_dx`` donor units along its heading, behind it);
    # an impact effect at the projectile (MKT rocket_explode_fx), in front.
    launch_event: int | None = None
    speeds: tuple[int, ...] = ()  # host per-tick magnitudes (empty: ``speed`` throughout)
    speeds_reacting: tuple[int, ...] = ()
    trail: str | None = None  # an effects.emit_descriptor label
    trail_dx: int = 0  # world units along the projectile's heading (negative: behind)
    trail_front: bool = False
    impact_effect: str | None = None
    impact_effect_front: bool = True
    # Drawn at the owner's vertical draw offset (+0xD8), as the stock projectile token builds its
    # actor (0x80030AA4: Sektor's runtime-confirmed legacy rocket), so MKT's own spawn offset
    # (make_rocket's 5, 38 px) and its effects (drawn at 0x6C, as the fighters) apply as in MKT.
    # Projectiles placed by an owner-calibrated offset (Reptile's, Rayden's) keep ACTOR_D8.
    owner_draw: bool = False
    # MKT object depth 0 (make_rocket): one sprite layer behind its owner, the stock idiom
    # (+0xEC = owner +0xEC + 1, 0x80030D18; the legacy rocket's behind_owner), priority +0x5C his.
    behind_owner: bool = False
    # MKT rocket_smoke toggles: its first puff comes on the second flight tick
    trail_skip_first: bool = True
    # Its render position set as it is placed (effects.RENDER_POSITION: paused on its first tick,
    # it would be drawn at the stage's origin)
    render_position: bool = False
    homing: Homing | None = None  # MKT's homing flight (Sektor's rocket2_proc) instead of a straight one
    # The trail is placed from the projectile's drawn position (+0x38..: the position before this
    # tick's move), as MKT places a puff from the rocket it shows (Sektor SMRE proof v12: from
    # +0x2C the newest puff showed one tick's travel ahead, under the missile's body)
    trail_from_drawn: bool = True
    tether: Tether | None = None


def strike_record(strike: dict[str, Any], reaction_slot: int) -> bytes:
    """16-byte host strike record: donor box, reaction slot, blocked reaction by meaning, damage
    and chip damage, stock trailer."""

    box = [_int(v) for v in strike["box"]]
    record = b"".join((v & 0xFFFF).to_bytes(2, "big") for v in box)
    record += bytes((reaction_slot, BLOCKED_LOWERING[strike["blocked_reaction"]]))
    record += bytes((_int(strike["damage"]), _int(strike["block_damage"])))
    flags = STRIKE_FLAGS | (STRIKE_UNBLOCKABLE if strike.get("unblockable") else 0)
    return record + flags.to_bytes(2, "big") + bytes(2)


def arc(meaning: str) -> tuple[int, int, int]:
    """Host jump arguments (x, y, gravity) for a reaction meaning's donor arc."""

    x, y, g = REACTION_LOWERING[meaning]["donor_arc"]
    return (
        -physics.convert_velocity(x),
        -physics.convert_velocity(-y),
        physics.convert_acceleration(g),
    )


def lower(
    step: dict[str, Any], art: ArtLayout, events: dict[str, int], reaction_slot: int, clean: bytes
) -> Lowered:
    strike = step["strike"]
    record = strike_record(strike, reaction_slot)
    speed = physics.fold_donor_speeds(
        _int(step["speed"]), _int(step["speed"]), lambda d: d, UNITS_PER_PX
    )[0]
    dx, dy = (_int(v) * UNITS_PER_PX for v in step["offset"])
    meaning = strike["reaction"]
    kind = REACTION_LOWERING[meaning].get("kind", "arc")
    words = tuple(lifted_reaction(clean, meaning)) if kind == "arc" else ()
    checks = tuple(
        b"".join((_int(v) & 0xFFFF).to_bytes(2, "big") for v in c["box"]) + record[8:]
        for c in step.get("checks", [])
    )
    impact = step.get("impact", {})
    speeds: tuple[int, ...] = ()
    speeds_reacting: tuple[int, ...] = ()
    if "accel_shift" in step or "speed_reacting" in step:
        shift = _int(step.get("accel_shift", 0))
        cap = _int(step["cap"]) if "cap" in step else None
        if shift and cap is None:
            raise ValueError("projectile accel_shift needs a cap")

        def host_speeds(start: int) -> tuple[int, ...]:
            if not shift:
                return (physics.fold_donor_speeds(start, start, lambda d: d, UNITS_PER_PX)[0],)
            return tuple(physics.fold_donor_speeds(start, cap, lambda d: d + (d >> shift), UNITS_PER_PX))

        speeds = host_speeds(_int(step["speed"]))
        speeds_reacting = host_speeds(_int(step.get("speed_reacting", step["speed"])))
        speed = speeds[0]
    tether = None
    if "tether" in step:
        spec = step["tether"]
        pull_speed = _int(spec["pull_speed"])
        tether = Tether(_int(spec["reach_px"]),
                        physics.fold_donor_speeds(pull_speed, pull_speed, lambda d: d, UNITS_PER_PX)[0],
                        _int(spec["stop_px"]), max(1, (_int(spec["daze_ticks"]) + 1) // 2))
    return Lowered(
        art, speed, dx, dy, record, words,
        events.get("hum"), _int(step.get("hum", {}).get("every", 0)), events.get("impact"),
        meaning, checks, impact.get("at") == "opponent",
        _int(impact.get("adjust", [0, 0])[0]) * UNITS_PER_PX,
        impact_follow=impact.get("follow") == "opponent",
        wrap_cooldown=_int(step["wrap"]["cooldown"]) if "wrap" in step else 0,
        launch_event=events.get("launch"), speeds=speeds, speeds_reacting=speeds_reacting,
        behind_owner=bool(step.get("behind")), tether=tether,
    )  # fmt: skip


# ---- code ---------------------------------------------------------------------------------------
def emit_spawn(a: Assembler, child: str = "projectile", after: str = "after_spawn") -> None:
    """In the owner's action (``s0`` = its controller): start the class-0x700 child and copy the
    opponent links into it, as 0x8004CBC4 does."""

    a.li("a0", PROJECTILE_CLASS)
    a.la("a1", child)
    a.jal(F_CLONE)
    a.beqz("v0", after)
    a.lw("t0", 0x63C, "s0")
    a.sw("t0", 0x63C, "v0")
    a.lw("t0", 0x640, "s0")
    a.sw("t0", 0x640, "v0")
    a.sw("zero", 0x638, "v0")
    a.label(after)


AFTERIMAGE_CLASS = 0x15  # an effect process (the stock hit effect's class), not a projectile


AFTERIMAGE_FIELDS = (host.ACTOR_PATH, host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Y, host.ACTOR_Z)


def emit_afterimage_spawn(a: Assembler, process: str, after: str) -> None:
    """In the owner's action (``s1`` = his actor): keep where he stands and his facing in the
    process's words (it starts on the next tick, after he has moved: MKT makes the copy at
    once), then start the afterimage process."""

    a.la("t0", process + "_at")
    for k, field in enumerate(AFTERIMAGE_FIELDS):
        a.lw("t1", field, "s1")
        a.sw("t1", 4 * k, "t0")
    a.lhu("t1", ACTOR_FLAGS, "s1")
    a.sw("t1", 4 * len(AFTERIMAGE_FIELDS), "t0")
    a.li("a0", AFTERIMAGE_CLASS)
    a.la("a1", process)
    a.jal(F_CLONE)
    a.label(after)


def emit_afterimage_process(a: Assembler, label: str, art: ArtLayout, ticks: int) -> None:
    """Process ``label``: an actor built from the owner's (as a projectile's, at his place and
    facing) shows the art's script for ``ticks`` host ticks, then goes (MKT: Rayden's teleport
    leaves a copy of himself playing his silhouette, 0x80045854)."""

    a.label(label)
    a.addiu("sp", "sp", -0x40)
    host.load_controller(a)
    a.lhu("a0", 0x78, "s1")  # owner type
    a.li("a1", art.flight_slot)
    a.lw("a2", 0xD8, "s1")  # the owner's vertical draw offset (Rayden 0x6C; projectiles 0x46)
    a.li("a3", art.tex_w)
    a.li("t0", art.tex_h)
    a.sw("t0", 0x10, "sp")
    a.addiu("t0", "sp", 0x20)
    a.sw("t0", 0x14, "sp")
    a.li("t0", art.palette_record)
    a.sw("t0", 0x18, "sp")
    a.jal(F_PROJ_BUILD)
    host.load_controller(a)
    a.la("t0", label + "_at")  # where the owner stood, and his facing then
    for k, field in enumerate(AFTERIMAGE_FIELDS):
        a.lw("t1", 4 * k, "t0")
        a.sw("t1", field, "s1")
    a.lw("t1", 4 * len(AFTERIMAGE_FIELDS), "t0")
    a.andi("t1", "t1", FACING_BIT)
    a.lhu("t2", ACTOR_FLAGS, "s1")
    a.andi("t2", "t2", 0xFFFF ^ FACING_BIT)
    a.or_("t2", "t2", "t1")
    a.sh("t2", ACTOR_FLAGS, "s1")
    if art.virtual:
        host.set_cursor(a, art.flight_at)
    else:
        a.li("a0", 1)
        a.li("a1", art.flight_slot)
        a.jal(F_SELECT)
    a.li("s2", ticks)
    a.label(label + "_loop")
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(F_ADVANCE)
    a.li("a0", 1)
    a.jal(F_SLEEP)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", label + "_loop")
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", ACTOR_LIST)
    a.jal(F_ACTOR_REMOVE)
    a.lw("a0", 0x20, "sp")
    a.jal(F_TEX_RELEASE)
    a.jal(F_EXIT)
    a.label(label + "_at")
    for _ in range(len(AFTERIMAGE_FIELDS) + 1):
        a.raw(0)


def emit_process(a: Assembler, p: Lowered, child: str = "projectile", player: str = "play",
                 prefix: str = "", data: str = "", alive: str | None = None) -> None:  # fmt: skip
    """The projectile process. Needs :func:`host.emit_sound_player` (label ``player``) and
    :func:`emit_data` (labels ``data + "record"``, ``data + "reaction"``, checks) in the same
    assembly. ``prefix`` names its internal labels, so several processes can share one
    assembly. Options (Acid Spit, milestone 4 step 3): virtual art entries (cursor by offset),
    close-range checks on the first frames before flight (MKT ``acid_arc_step``: next frame,
    sleep 2, box check), and the impact at the opponent (MKT ``match_me_to_opponent``,
    ``flip_single``, ``multi_adjust_xy``)."""

    def select(slot: int | None, at: int) -> None:
        if p.art.virtual:
            host.set_cursor(a, at)
        else:
            a.li("a0", 1)
            a.li("a1", slot)
            a.jal(F_SELECT)

    def velocity(tag: str = "") -> None:
        host.load_controller(a)
        if p.speeds:  # the table's (see below)
            a.lw("t0", 0, "s4")
        else:
            a.li("t0", p.speed)
        a.lw("t1", 0x700, "s0")
        a.li("t2", 0x10)
        a.bne("t1", "t2", prefix + "set_vel" + tag)
        a.subu("t0", "zero", "t0")
        a.label(prefix + "set_vel" + tag)
        a.sw("t0", 0x14, "s1")

    def collide(record: str, hit: str) -> None:
        host.load_controller(a)
        a.la("a0", record)
        a.lui("t0", KSEG1_TO_KSEG0 >> 16)
        a.subu("a0", "a0", "t0")  # KSEG0 alias: the collision core rejects other records
        a.sw("a0", 0x638, "s0")
        if p.wrap_cooldown:  # victims ahead of the projectile, not of the player (see PLAYER_ACTOR)
            a.lui("t0", host.hi(PLAYER_ACTOR))
            a.lw("s7", host.lo(PLAYER_ACTOR), "t0")
            a.sw("s1", host.lo(PLAYER_ACTOR), "t0")
        a.move("a1", "zero")
        a.jal(F_COLLIDE)
        if p.wrap_cooldown:
            a.lui("t0", host.hi(PLAYER_ACTOR))
            a.sw("s7", host.lo(PLAYER_ACTOR), "t0")
        a.andi("v0", "v0", 0xFFFF)
        a.li("t0", 0x8000)
        a.beq("v0", "t0", hit)

    a.label(child)
    a.addiu("sp", "sp", -0x40)
    if alive is not None:  # this move's projectile is live (lower_special: per-move limit)
        a.la("t0", alive)
        a.li("t1", 1)
        a.sw("t1", 0, "t0")
    host.load_controller(a)
    if p.tether is not None:
        # The clone still owns the launching actor until projectile_build replaces it.
        a.la("t0", data + "owner")
        a.sw("s1", 0, "t0")
        a.la("t0", data + "victim")
        a.sw("zero", 0, "t0")
    if p.behind_owner:  # the owner's layer, while the clone's actor is still his
        a.lhu("t0", ACTOR_SUBLAYER, "s1")
        a.sw("t0", OWNER_SUBLAYER_SP, "sp")
        a.lhu("t0", ACTOR_PRIORITY, "s1")
        a.sw("t0", OWNER_PRIORITY_SP, "sp")
    a.lhu("a0", 0x78, "s1")  # owner type (4)
    a.li("a1", p.art.flight_slot)
    if p.owner_draw:  # the clone's actor is still the owner's here
        a.lw("a2", 0xD8, "s1")
    else:
        a.li("a2", ACTOR_D8)
    a.li("a3", p.art.tex_w)
    a.li("t0", p.art.tex_h)
    a.sw("t0", 0x10, "sp")
    a.addiu("t0", "sp", 0x20)
    a.sw("t0", 0x14, "sp")
    a.li("t0", p.art.palette_record)
    a.sw("t0", 0x18, "sp")
    a.jal(F_PROJ_BUILD)
    host.load_controller(a)
    a.li("t0", PROJECTILE_CLASS)
    a.sh("t0", 0x72, "s1")
    if p.tether is not None:
        a.lw("t0", 0x64, "s1")
        a.ori("t0", "t0", TETHER_RENDER)
        a.sw("t0", 0x64, "s1")
        a.sh("zero", TETHER_LENGTH, "s1")
    if p.behind_owner:
        a.lw("t0", OWNER_SUBLAYER_SP, "sp")
        a.addiu("t0", "t0", 1)
        a.sh("t0", ACTOR_SUBLAYER, "s1")
        a.lw("t0", OWNER_PRIORITY_SP, "sp")
        a.sh("t0", ACTOR_PRIORITY, "s1")
    a.move("a0", "s1")
    a.li("a1", p.dx)
    a.li("a2", p.dy)
    a.jal(F_OFFSET)
    if p.render_position:
        host.load_controller(a)
        effects.emit_render_position(a, "s1")
    if p.launch_event is not None:  # MKT rocket1_proc: its sound as it starts
        host.play_sound(a, p.launch_event, player)
    if p.speeds:  # s4: this tick's speed in the table (the reacting one if he is reacting)
        host.load_controller(a)
        host.opponent_reacting(a, "s0", "t8", prefix + "react_read")
        a.la("s4", prefix + "speeds")
        a.beqz("t8", prefix + "speeds_picked")
        a.la("s4", prefix + "speeds_reacting")
        a.label(prefix + "speeds_picked")
    if p.checks:  # MKT: the first frames stay put and check close-range boxes, then flight
        host.load_controller(a)
        select(p.art.flight_slot, p.art.flight_at)
        for k in range(len(p.checks)):
            host.load_controller(a)
            a.move("a0", "s1")
            a.jal(F_ADVANCE)
            a.li("a0", 2)
            a.jal(F_SLEEP)
            collide(f"{data}check{k}", prefix + "on_contact")
        velocity()
    else:
        velocity()
        select(p.art.flight_slot, p.art.flight_at)
    a.li("s3", 0)
    if p.trail is not None:
        a.sw("zero", TRAIL_TICK_SP, "sp")
    if p.wrap_cooldown:
        a.li("s6", WRAP_ARMED)
        a.li("t0", 0x7FFF)
        a.sw("t0", WRAP_LAST_SP, "sp")  # |view x| last tick (none yet)
    if p.homing is not None:  # MKT's homing flight; the strike only when it explodes
        emit_homing_flight(a, p, prefix, prefix + "h_explode",
                           lambda: collide(data + "record", prefix + "on_contact"))
        a.label(prefix + "h_explode")
        collide(data + "record", prefix + "on_contact")
        a.beq("zero", "zero", prefix + "on_contact")
    else:
        a.label(prefix + "fly")
        if p.speeds:  # this tick's speed; the next entry from the next tick (0 ends the table)
            velocity("_tick")
            a.lw("t0", 4, "s4")
            a.beqz("t0", prefix + "speed_kept")
            a.addiu("s4", "s4", 4)
            a.label(prefix + "speed_kept")
        if p.trail is not None:  # one puff a host tick, ``trail_dx`` along its heading: the missile
            # is moved there by the facing-aware offset that placed it (MKT multi_adjust_xy), the
            # puff starts at its position, and its position is put back
            if p.trail_skip_first:
                a.lw("t0", TRAIL_TICK_SP, "sp")
                a.li("t1", 1)
                a.sw("t1", TRAIL_TICK_SP, "sp")
                a.beqz("t0", prefix + "trail_done")
            host.load_controller(a)
            for k, field in enumerate(TRAIL_FIELDS):
                a.lw("t0", field, "s1")
                a.sw("t0", FOLLOW_SP + 4 * k, "sp")
            if p.trail_from_drawn:  # from where it is drawn: +0x2C has this tick's move already
                for src, dst in effects.RENDER_POSITION:
                    a.lw("t0", dst, "s1")
                    a.sw("t0", src, "s1")
            a.move("a0", "s1")
            a.li("a1", p.trail_dx)
            a.move("a2", "zero")
            a.jal(F_OFFSET)
            host.load_controller(a)
            a.move("a0", "s1")
            a.la("a1", p.trail)
            a.move("a2", "zero")
            if p.trail_front:
                a.li("a3", effects.FRONT_SUBLAYER)
            else:  # behind it: the next sub-layer
                a.lhu("a3", ACTOR_SUBLAYER, "s1")
                a.addiu("a3", "a3", 1)
            a.jal_label("fx_spawn")
            host.load_controller(a)
            for k, field in enumerate(TRAIL_FIELDS):
                a.lw("t0", FOLLOW_SP + 4 * k, "sp")
                a.sw("t0", field, "s1")
            a.label(prefix + "trail_done")
        if p.hum_event is not None:
            a.addiu("s3", "s3", 1)
            a.slti("t0", "s3", p.hum_every)
            a.bnez("t0", prefix + "no_hum")
            a.addiu("s3", "s3", -p.hum_every)
            host.play_sound(a, p.hum_event, player)
            a.label(prefix + "no_hum")
        if p.tether is not None:
            host.load_controller(a)
            emit_tether_length(a, prefix + "flight_span", data, p.tether, prefix + "done")
            a.beqz("t0", prefix + "flight_outside")
        collide(data + "record", prefix + "on_contact")
        if p.tether is not None:
            a.label(prefix + "flight_outside")
        host.load_controller(a)
        a.move("a0", "s1")
        a.jal(F_ADVANCE)
        a.li("a0", 1)
        a.jal(F_SLEEP)
        host.load_controller(a)
        if p.wrap_cooldown:  # s6: armed, then the cooldown ticks, then 0 (wrapped: exits end it)
            a.li("t0", WRAP_ARMED)
            a.beq("s6", "t0", prefix + "wrap_armed")
            a.beqz("s6", prefix + "exit_check")
            a.addiu("s6", "s6", -1)  # cooldown: the flight keeps it
            a.beq("zero", "zero", prefix + "fly")
            a.label(prefix + "wrap_armed")
            emit_past_screen_edge(a, "s1", "t5", prefix + "edge_done")  # out past the edge, own depth
            a.beqz("t5", prefix + "fly")
            emit_screen_mirror(a, "s1")
            a.li("s6", p.wrap_cooldown)
            a.beq("zero", "zero", prefix + "fly")
            a.label(prefix + "exit_check")
        a.move("a0", "s1")
        a.li("a1", OFFSCREEN_MARGIN)
        a.jal(F_OFFSCREEN)
        a.beqz("v0", prefix + "fly")
        a.beq("zero", "zero", prefix + "done")
    a.label(prefix + "on_contact")
    if p.tether is not None:
        emit_tether_contact(a, prefix, data, p.tether)
    if p.impact_event is not None:
        host.play_sound(a, p.impact_event, player)
    if p.impact_effect is not None:  # at the projectile (MKT rocket_explode_fx)
        host.load_controller(a)
        a.move("a0", "s1")
        a.la("a1", p.impact_effect)
        a.move("a2", "zero")
        if p.impact_effect_front:
            a.li("a3", effects.FRONT_SUBLAYER)
        else:
            a.lhu("a3", ACTOR_SUBLAYER, "s1")
            a.addiu("a3", "a3", 1)
        a.jal_label("fx_spawn")
    if p.art.impact_slot is not None:
        host.load_controller(a)
        a.sw("zero", 0x14, "s1")
        if p.impact_at_opponent and p.impact_at_hit:  # on the enemy hit (see Lowered)
            if p.impact_follow:
                a.move("s5", "zero")  # no victim: nothing to follow
            a.lui("t0", host.hi(host.PLAYER_CTRL))
            a.lw("t0", host.lo(host.PLAYER_CTRL), "t0")
            a.lw("t0", host.CTRL_OPPONENT, "t0")
            a.beqz("t0", prefix + "no_opponent")
            a.lw("t0", host.CTRL_ACTOR, "t0")
            a.beqz("t0", prefix + "no_opponent")
            # its whole position, as the teleport copies it: on a walkway the offset below moves
            # along the path from the path position, so x alone left the burst at the bolt's
            # (specials proof v11, Wind)
            fields = [host.ACTOR_PATH, host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Z]
            if not p.impact_keep_y:
                fields.append(host.ACTOR_Y)
            for field in fields:
                a.lw("t1", field, "t0")
                a.sw("t1", field, "s1")
            if p.impact_follow:  # the victim: its controller (s4) and actor (s5)
                a.lui("s4", host.hi(host.PLAYER_CTRL))
                a.lw("s4", host.lo(host.PLAYER_CTRL), "s4")
                a.lw("s4", host.CTRL_OPPONENT, "s4")
                a.move("s5", "t0")
        elif p.impact_at_opponent:  # on the opponent, facing the attacker, MKT's adjust
            a.lw("t0", host.CTRL_OPPONENT, "s0")
            a.beqz("t0", prefix + "no_opponent")
            a.lw("t0", host.CTRL_ACTOR, "t0")
            a.beqz("t0", prefix + "no_opponent")
            a.lw("t1", host.ACTOR_X, "t0")
            a.sw("t1", host.ACTOR_X, "s1")
            if not p.impact_keep_y:
                a.lw("t1", host.ACTOR_Y, "t0")
                a.sw("t1", host.ACTOR_Y, "s1")
        if p.impact_at_opponent:
            if p.impact_flip:
                a.lhu("t1", ACTOR_FLAGS, "s1")
                a.li("t2", FACING_BIT)
                a.xor("t1", "t1", "t2")
                a.sh("t1", ACTOR_FLAGS, "s1")
            a.move("a0", "s1")
            a.li("a1", p.impact_dx)
            a.move("a2", "zero")
            a.jal(F_OFFSET)
            host.load_controller(a)
            a.label(prefix + "no_opponent")
        if p.art.virtual:
            select(None, p.art.impact_at)
        else:
            a.li("a0", 1)
            a.li("a1", p.art.impact_slot)
            a.jal(F_SELECT)
        follow = p.impact_follow and p.impact_at_opponent and p.impact_at_hit
        if follow:  # the offsets from the victim, after the adjust (no victim: s5 = 0)
            host.load_controller(a)
            a.beqz("s5", prefix + "follow_none")
            for k, field in enumerate(FOLLOW_FIELDS):
                a.lw("t1", field, "s1")
                a.lw("t2", field, "s5")
                a.subu("t1", "t1", "t2")
                a.sw("t1", FOLLOW_SP + 4 * k, "sp")
            a.label(prefix + "follow_none")
        a.li("s2", p.art.impact_ticks)
        a.label(prefix + "impact_loop")
        host.load_controller(a)
        if follow:
            a.beqz("s5", prefix + "follow_skip")
            a.lw("t0", host.CTRL_ACTOR, "s4")
            a.bne("t0", "s5", prefix + "follow_lost")
            for k, field in enumerate(FOLLOW_FIELDS):
                a.lw("t1", field, "s5")
                a.lw("t2", FOLLOW_SP + 4 * k, "sp")
                a.addu("t1", "t1", "t2")
                a.sw("t1", field, "s1")
            a.beq("zero", "zero", prefix + "follow_skip")
            a.label(prefix + "follow_lost")
            a.move("s5", "zero")  # the victim gone: stay put
            a.label(prefix + "follow_skip")
        a.move("a0", "s1")
        a.jal(F_ADVANCE)
        a.li("a0", 1)
        a.jal(F_SLEEP)
        a.addiu("s2", "s2", -1)
        a.bnez("s2", prefix + "impact_loop")
    a.label(prefix + "done")
    if p.tether is not None:
        a.la("t0", data + "owner")
        a.sw("zero", 0, "t0")
        a.la("t0", data + "victim")
        a.sw("zero", 0, "t0")
    if p.homing is not None:  # its crosshair goes (the follower sees no target)
        a.la("t0", prefix + "follow")
        a.sw("zero", 0, "t0")
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", ACTOR_LIST)
    a.jal(F_ACTOR_REMOVE)
    a.lw("a0", 0x20, "sp")
    a.jal(F_TEX_RELEASE)
    if alive is not None:
        a.la("t0", alive)
        a.sw("zero", 0, "t0")
    a.jal(F_EXIT)
    a.label(prefix + "child_hang")
    a.beq("zero", "zero", prefix + "child_hang")
    if p.homing is not None:
        emit_homing_data(a, p.homing, prefix)
    if p.speeds:  # each ended by 0 (the last entry is the steady speed)
        for name, table in (("speeds", p.speeds), ("speeds_reacting", p.speeds_reacting)):
            a.label(prefix + name)
            for word in table:
                a.raw(word)
            a.raw(0)


# The host camera (Static-confirmed, the offscreen test 0x80035088): view = M * (world >> 8 + T)
# / 4096, with M a 3x3 rotation of halfwords (4.12) at 0x8009A930 (row 0: view x) and T the
# words at 0x8009A944/48/4C; the visible half-width at a depth is compared with view x.
CAMERA_VIEW = 0x8009A930
CAMERA_T = 0x14  # the translation, after the 3x3 matrix (+ 2 bytes padding)
WRAP_ARMED = 0x100
WRAP_LAST_SP = 0x34  # the child's frame, after the follow offsets (0x24..0x33)
# The visible half-width at a view depth is depth * 160 / focal (the projection 0x802C1148: m00 =
# focal / 160 = 1.25). The host's offscreen test compares view x with half that (depth * 80 /
# focal) plus its margin, 200: 40 units past the edge at Wind's normal depth 400 (the wrap the
# owner saw right in v20), 133 units inside it at the zoomed-out depth 832 (owner's save states,
# specials proof v21). The wrap triggers this far past the real edge (as v20 at normal zoom).
WRAP_MARGIN = 40
CAMERA_FOCAL = 0x8009A8E8  # focal length (200); the depth is the camera's T.z (0x802C1BB4 copies it)
VISIBLE_HALF = 160  # half the screen width in pixels
PLAYER_ACTOR = 0x802E73DC
# The enemy-victim scan (0x8002CC4C) skips an enemy that is not ahead of the player actor by the
# player's facing bit and x: fine for projectiles that fly forward. A wrapping projectile can
# meet enemies behind the player (Rayden's reversed lightning, specials proof v20: it never
# hit), so for its strike check the pointer holds the projectile's actor (a clone of the
# player's: the scan's other read, its type +0x78, is the same), then the player's again.


def _view(a: Assembler, actor: str, row: int, out: str) -> None:
    """``out`` = view coordinate ``row`` (0: x, 2: depth) of ``actor``, world units (t9: the
    camera view; uses t0, t1)."""

    a.move(out, "zero")
    for k, field in enumerate((host.ACTOR_X, host.ACTOR_Y, host.ACTOR_Z)):
        a.lw("t0", field, actor)
        a.sra("t0", "t0", 8)
        a.lw("t1", CAMERA_T + 4 * k, "t9")
        a.addu("t0", "t0", "t1")
        a.lh("t1", 6 * row + 2 * k, "t9")
        a.mult("t0", "t1")
        a.mflo("t0")
        a.nop()
        a.nop()
        a.addu(out, out, "t0")
    a.sra(out, out, 12)


def emit_past_screen_edge(a: Assembler, actor: str, out: str, done: str) -> None:
    """``out`` = 1 when ``actor`` is more than WRAP_MARGIN past the visible half-width at its own
    view depth (depth * 160 / focal) and moving further out (|view x| grew since last tick),
    else 0. The host's offscreen test 0x80035088 uses half that width plus 200, which is inside
    the screen on a zoomed-out camera (Wind: depth 832; specials proofs v20-v21: the bolt
    wrapped while still on screen)."""

    a.lui("t9", host.hi(CAMERA_VIEW))
    a.addiu("t9", "t9", host.lo(CAMERA_VIEW))
    _view(a, actor, 0, "t2")
    _view(a, actor, 2, "t3")
    a.sra("t0", "t2", 31)  # |view x|
    a.xor("t2", "t2", "t0")
    a.subu("t2", "t2", "t0")
    a.lw("t4", WRAP_LAST_SP, "sp")
    a.sw("t2", WRAP_LAST_SP, "sp")
    a.move(out, "zero")
    a.slt("t0", "t4", "t2")  # moving out
    a.beqz("t0", done)
    a.li("t0", VISIBLE_HALF)
    a.mult("t3", "t0")
    a.mflo("t3")
    a.nop()
    a.nop()
    a.lui("t0", host.hi(CAMERA_FOCAL))
    a.lw("t0", host.lo(CAMERA_FOCAL), "t0")
    a.div("t3", "t0")
    a.mflo("t3")
    a.nop()
    a.nop()
    a.addiu("t3", "t3", WRAP_MARGIN)
    a.slt(out, "t3", "t2")
    a.label(done)


def emit_screen_mirror(a: Assembler, actor: str) -> None:
    """Move ``actor`` to the mirror of its position across the camera's vertical centre plane:
    view x -> -view x at the same depth and height, so an actor just past one screen edge is just
    past the other (MKT's wrap is the 2D same: x to the opposite edge). In world fixed8 units:
    p -= (view_x * M0) >> 3 (2 * view_x * M0 / 4096, << 8)."""

    fields = (host.ACTOR_X, host.ACTOR_Y, host.ACTOR_Z)
    a.lui("t9", host.hi(CAMERA_VIEW))
    a.addiu("t9", "t9", host.lo(CAMERA_VIEW))
    a.move("t2", "zero")
    for k, field in enumerate(fields):
        a.lw("t0", field, actor)
        a.sra("t0", "t0", 8)
        a.lw("t1", CAMERA_T + 4 * k, "t9")
        a.addu("t0", "t0", "t1")
        a.lh("t1", 2 * k, "t9")
        a.mult("t0", "t1")
        a.mflo("t0")
        a.nop()
        a.nop()
        a.addu("t2", "t2", "t0")
    a.sra("t2", "t2", 12)  # view x
    for k, field in enumerate(fields):
        a.lh("t1", 2 * k, "t9")
        a.mult("t2", "t1")
        a.mflo("t0")
        a.nop()
        a.nop()
        a.sra("t0", "t0", 3)
        a.lw("t1", field, actor)
        a.subu("t1", "t1", "t0")
        a.sw("t1", field, actor)


HELPER_IDLE, HELPER_SHOWN, HELPER_LAUNCH = 0, 1, 2
HIT_REACTION_BIT = 0x04  # controller +0x6BE while in a hit reaction (host.CTRL_STATE_FLAGS)

# Where the host collision core puts a strike box (Static-confirmed, victim scan
# 0x8002CE24..0x8002D0E0): box values are scaled by 0.9 and doubled into world units, from the
# attacker actor's position with y - 0xD8 (box y grows downward). The facing bit mirrors x.
BOX_ORIGIN_UNITS = 0xD8
BOX_UNIT = 1.8  # world units per box unit (x 0.9, then << 1)


def drawn_band(donor: Donor, anim: dict[str, Any]) -> tuple[float, float]:
    """Box-space y span (top, bottom) of the visible rows of an art part's looping frames
    (from ``loop_from``), as the host draws them: frame rows from the anchor's y, ``UNITS_PER_PX``
    world units per pixel, from the projectile actor's position."""

    part = donor_part(donor, anim)
    top, bottom = float("inf"), float("-inf")
    for rel in part.frames[part.loop_from :]:
        f = donor.frame(rel)
        w, stride, pixels = f["w"], (f["w"] + 3) & ~3, f["padded"]
        rows = [y for y in range(f["eh"]) if any(pixels[y * stride : y * stride + w])]
        if rows:
            top = min(top, f["y"] + rows[0])
            bottom = max(bottom, f["y"] + rows[-1])
    if top == float("inf"):
        raise ValueError("art part has no visible pixels")
    to_box = lambda px: (BOX_ORIGIN_UNITS + UNITS_PER_PX * px) / BOX_UNIT
    return to_box(top), to_box(bottom)


def centre_on_art(donor: Donor, step: dict[str, Any]) -> dict[str, Any]:
    """``step`` with its strike box and close-range checks moved down by one shift that centres
    the strike box on the drawn flight art (Hypothesis; Reptile's acid, specials proof v13). MKT's
    boxes assume MKT's own box origin, so a thin donor box can miss the art on the host."""

    top, bottom = drawn_band(donor, step["art"])
    box = [_int(v) for v in step["strike"]["box"]]
    shift = round((top + bottom) / 2 - (box[1] + box[3] / 2))
    out = dict(step, strike=dict(step["strike"], box=[box[0], box[1] + shift, box[2], box[3]]))
    if "checks" in step:
        out["checks"] = [dict(c, box=[_int(c["box"][0]), _int(c["box"][1]) + shift,
                                      _int(c["box"][2]), _int(c["box"][3])])
                         for c in step["checks"]]  # fmt: skip
    return out


def phase_end_ticks(rate: int) -> int:
    """Ticks per frame of the host's ``animate_to_phase_end`` (``0x80031070``) at ``rate``: an odd
    rate of 2 or more sleeps ``rate - 1`` (Static-confirmed, ``0x80031094..0x800310AC``). The
    throw helper steps at this pace to stay with the body (specials proof v05, owner: "too
    slow")."""

    return rate - 1 if rate & 1 and rate >= 2 else rate
HELPER_MAX_TICKS = 120  # safety cap: the helper never outlives this


def emit_helper(a: Assembler, art: ArtLayout, dx: int, dy: int, label: str, body_slot: int | None,
                body_at: int | None = None) -> None:  # fmt: skip
    """The throw helper's process (spawned with :func:`emit_spawn` at the start of the throw).

    It follows the owner's body: each tick it reads the player's animation cursor in the throw
    script (table-1 ``body_slot``) and, for body pose *k* >= ``art.helper_start``, shows the
    helper frame of that pose (MKT's script order: one helper step per body pose), its last
    frame held. It is built when its first pose comes up and goes when the action asks for the
    launch (:func:`emit_helper_handover`); no collision. Specials proofs v03-v07 timed it on
    its own clock and drifted a pose or more (owner). ``dx``/``dy``: offset from the owner.

    It also goes as soon as the owner leaves the throw: in a hit reaction (controller
    ``+0x6BE`` bit ``0x04``) or in another action than at its start (``+0x6AA``). Without that it
    stayed up to ``HELPER_MAX_TICKS`` after a hit interrupted the throw (owner, Reptile
    production composition v01)."""

    state = label + "_state"
    a.label(label)
    a.addiu("sp", "sp", -0x40)
    a.li("s2", -1)  # last body pose shown
    a.li("s3", 0)  # built
    a.li("s4", HELPER_MAX_TICKS)
    a.lui("t0", host.hi(host.PLAYER_CTRL))
    a.lw("t0", host.lo(host.PLAYER_CTRL), "t0")
    a.lhu("s5", host.CTRL_ACTION_ID, "t0")  # the throw's action
    a.label(label + "_loop")
    a.la("t0", state)
    a.lw("t1", 0, "t0")
    a.li("t2", HELPER_LAUNCH)
    a.beq("t1", "t2", label + "_end")
    a.lui("t0", host.hi(host.PLAYER_CTRL))
    a.lw("t0", host.lo(host.PLAYER_CTRL), "t0")
    a.lhu("t1", host.CTRL_STATE_FLAGS, "t0")
    a.andi("t1", "t1", HIT_REACTION_BIT)
    a.bnez("t1", label + "_end")  # hit: the throw is over
    a.lhu("t1", host.CTRL_ACTION_ID, "t0")
    a.bne("t1", "s5", label + "_end")  # another action took over
    a.lw("t1", host.CTRL_SCRIPT_CURSOR, "t0")
    a.lw("t2", host.CTRL_ACTOR, "t0")
    a.lw("t2", host.ACTOR_FILE_BASE, "t2")
    if body_at is None:  # the throw script's table-1 entry
        a.lw("t3", 0x104 + 4 * body_slot, "t2")
    else:  # a script without a table entry (body.secondary_scripts, virtual)
        a.li("t3", body_at)
    a.addu("t3", "t2", "t3")
    a.subu("t1", "t1", "t3")
    a.sra("t1", "t1", 2)
    a.addiu("t1", "t1", -1)  # body pose on screen (the cursor is past it)
    a.slti("t4", "t1", art.helper_start)
    a.bnez("t4", label + "_wait")
    a.slti("t4", "t1", art.helper_start + art.helper_frames)
    a.beqz("t4", label + "_wait")  # past the throw: keep the last frame
    a.beq("t1", "s2", label + "_wait")
    a.move("s2", "t1")
    a.bnez("s3", label + "_show")
    host.load_controller(a)
    a.lhu("a0", 0x78, "s1")  # owner type (4)
    a.li("a1", art.helper_slot)
    a.li("a2", ACTOR_D8)
    a.li("a3", art.tex_w)
    a.li("t0", art.tex_h)
    a.sw("t0", 0x10, "sp")
    a.addiu("t0", "sp", 0x20)
    a.sw("t0", 0x14, "sp")
    a.li("t0", art.palette_record)
    a.sw("t0", 0x18, "sp")
    a.jal(F_PROJ_BUILD)
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", dx)
    a.li("a2", dy)
    a.jal(F_OFFSET)
    a.li("s3", 1)
    a.la("t0", state)
    a.li("t1", HELPER_SHOWN)
    a.sw("t1", 0, "t0")
    a.label(label + "_show")
    host.load_controller(a)
    a.lw("t2", host.ACTOR_FILE_BASE, "s1")
    if art.virtual:
        a.li("t3", art.helper_at)
    else:
        a.lw("t3", 0x104 + 4 * art.helper_slot, "t2")
    a.addu("t3", "t2", "t3")
    a.addiu("t1", "s2", -art.helper_start)
    a.sll("t1", "t1", 2)
    a.addu("t3", "t3", "t1")
    a.sw("t3", host.CTRL_SCRIPT_CURSOR, "s0")
    a.move("a0", "s1")
    a.jal(F_ADVANCE)
    a.label(label + "_wait")
    a.li("a0", 1)
    a.jal(F_SLEEP)
    a.addiu("s4", "s4", -1)
    a.bnez("s4", label + "_loop")
    a.label(label + "_end")
    a.beqz("s3", label + "_gone")
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", ACTOR_LIST)
    a.jal(F_ACTOR_REMOVE)
    a.lw("a0", 0x20, "sp")
    a.jal(F_TEX_RELEASE)
    a.label(label + "_gone")
    a.la("t0", state)
    a.sw("zero", 0, "t0")
    a.jal(F_EXIT)
    a.label(label + "_hang")
    a.beq("zero", "zero", label + "_hang")


def emit_helper_handover(a: Assembler, label: str, tag: str) -> None:
    """In the owner's action, before the launch: ask the helper ``label`` to go and wait (at
    most ``HELPER_MAX_TICKS``) until it has removed itself and released its texture."""

    state = label + "_state"
    a.la("t0", state)
    a.lw("t1", 0, "t0")
    a.beqz("t1", tag + "_gone")
    a.li("t1", HELPER_LAUNCH)
    a.sw("t1", 0, "t0")
    a.li("s2", HELPER_MAX_TICKS)
    a.label(tag + "_wait")
    a.li("a0", 1)
    a.jal(F_SLEEP)
    a.la("t0", state)
    a.lw("t1", 0, "t0")
    a.beqz("t1", tag + "_gone")
    a.addiu("s2", "s2", -1)
    a.bnez("s2", tag + "_wait")
    a.label(tag + "_gone")


def emit_helper_data(a: Assembler, label: str) -> None:
    """The helper's state word (idle 0, shown 1, launch requested 2)."""

    a.label(label + "_state")
    a.raw(HELPER_IDLE)


def emit_blink_start(a: Assembler, blink: str, then: str) -> None:
    """In the victim's reaction (its own process): start process ``blink`` with the victim's
    controller as its argument (+0x6F4, written after creation as effects do), then go on at
    ``then`` with the reaction's own sp and ra."""

    a.addiu("sp", "sp", -0x20)
    a.sw("ra", 0x18, "sp")
    a.sw("s0", 0x14, "sp")
    a.lui("t0", host.hi(host.CURRENT_CTRL))
    a.lw("s0", host.lo(host.CURRENT_CTRL), "t0")
    a.li("a0", BLINK_PROCESS_ID)
    a.la("a1", blink)
    a.jal(F_CLONE)
    a.beqz("v0", blink + "_none")  # no process left: no blink
    a.sw("s0", 0x6F4, "v0")
    a.label(blink + "_none")
    a.lw("s0", 0x14, "sp")
    a.lw("ra", 0x18, "sp")
    a.addiu("sp", "sp", 0x20)
    a.j_label(then)


def emit_blink(a: Assembler, label: str, rgb: tuple[int, int, int], count: int, every: int) -> None:
    """Process ``label``: ``count`` times, every ``every`` ticks, the victim's colour alternates
    between ``rgb`` (lighting paused, the corner colours written) and its own (the lighting bit
    as it was, or the unlit colour), then its own; it stops touching the victim as soon as its
    controller holds another actor (the victim gone)."""

    def colours(values: tuple[int, int, int]) -> None:
        for base, value in zip(ACTOR_VERTEX_RGB, values):
            a.li("t1", value)
            for corner in range(4):
                a.sb("t1", base + corner, "s3")

    def own(relight: str) -> None:  # the lighting bit back (lit actors), or the unlit colour
        a.bnez("s6", relight)
        colours((NORMAL_RGB,) * 3)
        a.label(relight)
        a.lhu("t1", ACTOR_FLAGS, "s3")
        a.or_("t1", "t1", "s6")
        a.sh("t1", ACTOR_FLAGS, "s3")

    a.label(label)
    host.load_controller(a)
    a.lw("s2", 0x6F4, "s0")  # the victim's controller
    a.lw("s3", host.CTRL_ACTOR, "s2")  # its actor, as at the start
    a.lhu("s6", ACTOR_FLAGS, "s3")
    a.andi("s6", "s6", ACTOR_LIT_BIT)  # lit by the stage
    a.li("s4", count)
    a.move("s5", "zero")  # 0: tint next, 1: own next
    a.label(label + "_step")
    a.lw("t0", host.CTRL_ACTOR, "s2")
    a.bne("t0", "s3", label + "_exit")
    a.bnez("s5", label + "_own")
    a.lhu("t1", ACTOR_FLAGS, "s3")
    a.andi("t1", "t1", 0xFFFF ^ ACTOR_LIT_BIT)
    a.sh("t1", ACTOR_FLAGS, "s3")
    colours(rgb)
    a.beq("zero", "zero", label + "_set")
    a.label(label + "_own")
    own(label + "_relight")
    a.label(label + "_set")
    a.li("t1", 1)
    a.xor("s5", "s5", "t1")
    a.li("a0", every)
    a.jal(F_SLEEP)
    a.addiu("s4", "s4", -1)
    a.bnez("s4", label + "_step")
    a.lw("t0", host.CTRL_ACTOR, "s2")
    a.bne("t0", "s3", label + "_exit")
    own(label + "_relight_end")
    a.label(label + "_exit")
    a.jal(F_EXIT)


def emit_data(a: Assembler, p: Lowered, base: int, clean: bytes | None = None, data: str = "") -> None:
    """Strike record (16-aligned, read through its KSEG0 alias), the close-range check records
    and the reaction: the lifted arc words, or (stumble kind) the stumble lifted here, which
    needs ``clean``."""

    while (a.pc() - base) % 16:
        a.nop()
    a.label(data + "record")
    for i in range(0, 16, 4):
        a.raw(int.from_bytes(p.record[i : i + 4], "big"))
    for k, rec in enumerate(p.checks):
        a.label(f"{data}check{k}")
        for i in range(0, 16, 4):
            a.raw(int.from_bytes(rec[i : i + 4], "big"))
    if host_reaction(p.reaction_meaning) is not None:
        return  # a stock reaction: nothing in the payload
    a.label(data + "reaction")
    spec = REACTION_LOWERING[p.reaction_meaning]
    if p.tether is not None:
        emit_tether_reaction(a, data, p.tether)
    elif spec.get("kind", "arc") == "stumble":
        if clean is None:
            raise ValueError("a stumble reaction is lifted from the clean ROM")
        if "blink" in spec:  # start the blink helper, then the stumble as the reaction itself
            emit_blink_start(a, data + "blink", data + "stumble")
            a.label(data + "stumble")
        code = lift_stumble(clean, p.reaction_meaning, a.pc())
        for i in range(0, len(code), 4):
            a.raw(int.from_bytes(code[i : i + 4], "big"))
        if "blink" in spec:
            b = spec["blink"]
            emit_blink(a, data + "blink", b["colour"], b["count"], b["every"])
    else:
        for word in p.reaction_words:
            a.raw(word)


# Scorpion's Prison rope (0x800413DC) uses this renderer contract; its enemy-side
# reaction 0x3D follows the boss's projectile and assumes the victim is the player.
TETHER_RENDER = 0x40
TETHER_LENGTH = 0x104
TETHER_VICTIM_ROOT = 0x20
TETHER_SELECT_LAST_FRAME = 0x8003044C  # the native spear uses the last recoil frame
TETHER_VICTIM_ACTION = 0x11A  # native rope exchange marker
CTRL_SCHEDULED_PC = 0x08  # 0x80032CD4 installs a new reaction entry here
TETHER_RELEASE = 0x800328FC
TETHER_WALL_MARGIN = 16  # whole world units; leave a small margin at a blocking wall
TETHER_PULL_LIMIT = 40  # host ticks
TETHER_STALL_LIMIT = 3  # consecutive passes with no approach
TETHER_PREV_GAP = 0x30
TETHER_STALL = 0x34


def _tether_owner(a: Assembler, data: str, done: str) -> None:
    """Load the active launch actor into t3, independently of its current action."""
    a.lui("t3", host.hi(host.PLAYER_CTRL))
    a.lw("t3", host.lo(host.PLAYER_CTRL), "t3")
    a.beqz("t3", done)
    a.lhu("t1", CTRL_HEALTH, "t3")
    a.beqz("t1", done)
    a.lhu("t1", host.CTRL_STATE_FLAGS, "t3")
    a.andi("t1", "t1", HIT_REACTION_BIT)
    a.bnez("t1", done)
    a.lw("t3", host.CTRL_ACTOR, "t3")
    a.beqz("t3", done)
    a.la("t1", data + "owner")
    a.lw("t1", 0, "t1")
    a.bne("t3", "t1", done)


def emit_tether_length(a: Assembler, tag: str, data: str, tether: Tether, done: str) -> None:
    """Clip the long rope sprite to the forward distance from the owner to its tip."""
    _tether_owner(a, data, done)
    a.lw("t0", host.ACTOR_X, "s1")
    a.lw("t2", host.ACTOR_X, "t3")
    a.subu("t0", "t0", "t2")
    a.lhu("t1", ACTOR_FLAGS, "s1")
    a.andi("t1", "t1", FACING_BIT)
    a.beqz("t1", tag + "_forward")
    a.subu("t0", "zero", "t0")
    a.label(tag + "_forward")
    a.bgez("t0", tag + "_ahead")
    a.move("t0", "zero")
    a.label(tag + "_ahead")
    a.sra("t0", "t0", 9)  # native renderer distance: (whole world units / 2)
    a.slti("t1", "t0", tether.reach_px)
    a.beqz("t1", done)
    a.sh("t0", TETHER_LENGTH, "s1")


def emit_tether_contact(a: Assembler, prefix: str, data: str, tether: Tether) -> None:
    """Follow the actual collision victim through the reel. A block or miss clears the rope."""
    done = prefix + "done"
    host.load_controller(a)
    a.sw("zero", host.ACTOR_XVEL, "s1")
    _tether_owner(a, data, done)
    a.lui("t0", host.hi(host.PLAYER_CTRL))
    a.lw("t0", host.lo(host.PLAYER_CTRL), "t0")
    a.lw("s5", host.CTRL_OPPONENT, "t0")
    a.beqz("s5", done)
    a.lw("t0", CTRL_SCHEDULED_PC, "s5")
    a.la("t1", data + "reaction")
    a.bne("t0", "t1", done)
    a.lhu("s6", 0x6D8, "s5")
    a.addiu("t0", "s6", -ENEMY_CLASSES[0])
    a.slti("t1", "t0", len(ENEMY_CLASSES))
    a.beqz("t1", done)
    a.bltz("t0", done)
    a.la("t0", data + "victim")
    a.sw("s5", 0, "t0")
    a.li("s7", TETHER_PULL_LIMIT + 2)  # the victim can start a scheduler pass later
    a.label(prefix + "reel")
    a.move("a0", "s6")
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.bne("v0", "s5", prefix + "reel_done")
    a.la("t0", data + "victim")
    a.lw("t1", 0, "t0")
    a.bne("t1", "s5", prefix + "reel_done")
    a.lhu("t0", host.CTRL_ACTION_ID, "s5")
    a.li("t1", TETHER_VICTIM_ACTION)
    a.beq("t0", "t1", prefix + "reel_actor")
    a.lw("t0", CTRL_SCHEDULED_PC, "s5")
    a.la("t1", data + "reaction")
    a.bne("t0", "t1", prefix + "reel_done")
    a.label(prefix + "reel_actor")
    a.lw("t4", host.CTRL_ACTOR, "s5")
    a.beqz("t4", prefix + "reel_done")
    host.load_controller(a)
    for field in (host.ACTOR_PATH, host.ACTOR_PATH_PARAM, host.ACTOR_X, host.ACTOR_Z):
        a.lw("t0", field, "t4")
        a.sw("t0", field, "s1")
    emit_tether_length(a, prefix + "reel_span", data, tether, prefix + "reel_done")
    a.move("a0", "s1")
    a.jal(F_ADVANCE)
    a.li("a0", 1)
    a.jal(F_SLEEP)
    a.addiu("s7", "s7", -1)
    a.bnez("s7", prefix + "reel")
    a.label(prefix + "reel_done")
    a.beq("zero", "zero", done)


def _tether_pose(a: Assembler, tag: str, *, last: bool = False) -> None:
    """Show a frame from the stock hit root when the victim's current file supplies it."""
    host.load_controller(a)
    a.lw("t0", host.ACTOR_FILE_BASE, "s1")
    a.beqz("t0", tag)
    a.lw("t1", 4 * TETHER_VICTIM_ROOT, "t0")
    a.blez("t1", tag)  # 0 or -1 is an absent root on split resources
    a.move("a0", "zero")
    a.li("a1", TETHER_VICTIM_ROOT)
    a.jal(F_SELECT)
    if last:
        a.jal(TETHER_SELECT_LAST_FRAME)
    host.load_controller(a)
    host.advance_animation(a)
    a.label(tag)


def emit_tether_reaction(a: Assembler, data: str, tether: Tether) -> None:
    """Player-side variant of the native rope reaction, using ordinary enemy motion and exit."""
    label = data + "reaction"
    a.addiu("sp", "sp", -0x38)
    a.sw("s0", 0x18, "sp")
    a.sw("s1", 0x1C, "sp")
    a.sw("s2", 0x20, "sp")
    a.sw("s3", 0x24, "sp")
    a.sw("ra", 0x28, "sp")
    host.load_controller(a)
    a.la("t0", data + "victim")
    a.lw("t1", 0, "t0")
    a.bne("t1", "s0", label + "_out")
    a.lhu("t0", CTRL_HEALTH, "s0")
    a.beqz("t0", label + "_out")
    a.lhu("t0", host.CTRL_AIRBORNE, "s0")
    a.bnez("t0", label + "_out")
    a.li("t0", TETHER_VICTIM_ACTION)
    a.sh("t0", host.CTRL_ACTION_ID, "s0")
    # The same two-file morphs as the stock launch, before a shared victim root.
    for fn in REACTION_LOWERING["knockback_arc"]["morph"]:
        host.load_controller(a)
        a.move("a0", "s1")
        a.jal(fn)
    host.load_controller(a)
    host.stop(a)
    _tether_pose(a, label + "_pull_pose")
    a.li("s2", TETHER_PULL_LIMIT)
    a.li("t0", 0x7FFFFFFF)
    a.sw("t0", TETHER_PREV_GAP, "sp")
    a.li("t0", TETHER_STALL_LIMIT)
    a.sw("t0", TETHER_STALL, "sp")
    a.label(label + "_pull")
    host.load_controller(a)
    a.la("t0", data + "victim")
    a.lw("t1", 0, "t0")
    a.bne("t1", "s0", label + "_out")
    _tether_owner(a, data, label + "_out")
    a.lw("t0", host.ACTOR_PATH, "t3")
    a.lw("t1", host.ACTOR_PATH, "s1")
    a.bne("t0", "t1", label + "_out")
    a.lw("t0", host.ACTOR_X, "t3")
    a.lw("t1", host.ACTOR_X, "s1")
    a.subu("s3", "t0", "t1")
    _abs(a, "t2", "s3", "t1")
    a.li("t1", tether.stop_px * UNITS_PER_PX << 8)
    a.slt("t0", "t1", "t2")
    a.beqz("t0", label + "_daze")
    # Fighter separation can stop the victim outside the donor's distance.
    a.lw("t0", TETHER_PREV_GAP, "sp")
    a.slt("t1", "t2", "t0")
    a.sw("t2", TETHER_PREV_GAP, "sp")
    a.li("t0", TETHER_STALL_LIMIT)
    a.bnez("t1", label + "_stall_count")
    a.lw("t0", TETHER_STALL, "sp")
    a.addiu("t0", "t0", -1)
    a.beqz("t0", label + "_daze")
    a.label(label + "_stall_count")
    a.sw("t0", TETHER_STALL, "sp")
    a.move("a0", "s1")
    a.addiu("a1", "sp", 0x10)
    a.addiu("a2", "sp", 0x14)
    a.jal(host.F_WALL_DISTANCE)
    host.load_controller(a)
    a.li("a1", tether.pull_speed)
    a.bltz("s3", label + "_left")
    a.lw("t0", 0x14, "sp")
    a.beq("zero", "zero", label + "_wall")
    a.label(label + "_left")
    a.subu("a1", "zero", "a1")
    a.lw("t0", 0x10, "sp")
    a.label(label + "_wall")
    a.slti("t0", "t0", TETHER_WALL_MARGIN)
    a.bnez("t0", label + "_daze")
    a.move("a0", "s1")
    a.jal(0x8002B1EC)  # native horizontal velocity setter (walkway and ordinary motion)
    host.sleep_tick(a)
    a.addiu("s2", "s2", -1)
    a.bnez("s2", label + "_pull")
    a.label(label + "_daze")
    a.la("t0", data + "victim")
    a.sw("zero", 0, "t0")
    host.stop(a)
    _tether_pose(a, label + "_daze_pose", last=True)
    # The victim's own routine keeps its hit state after the rope or owner leaves.
    host.sleep_ticks(a, tether.daze_ticks, label + "_dazing")
    a.label(label + "_out")
    host.load_controller(a)
    a.la("t0", data + "victim")
    a.lw("t1", 0, "t0")
    a.bne("t1", "s0", label + "_resume")
    a.sw("zero", 0, "t0")
    a.label(label + "_resume")
    a.lhu("t0", host.CTRL_ACTION_ID, "s0")
    a.li("t1", TETHER_VICTIM_ACTION)
    a.bne("t0", "t1", label + "_return")
    a.sh("zero", host.CTRL_ACTION_ID, "s0")
    a.label(label + "_return")
    a.move("a0", "s1")
    a.lw("s0", 0x18, "sp")
    a.lw("s1", 0x1C, "sp")
    a.lw("s2", 0x20, "sp")
    a.lw("s3", 0x24, "sp")
    a.lw("ra", 0x28, "sp")
    a.addiu("sp", "sp", 0x38)
    a.j(TETHER_RELEASE)
    a.label(data + "victim")
    a.raw(0)
    a.label(data + "owner")
    a.raw(0)


# ---- homing (MKT rocket2_proc: Sektor's homing missile) -----------------------------------------
F_FIND_CLASS = 0x80028510  # (class, mask) -> first other process with +0x6D8 & mask == class
F_FLIP = 0x8003188C  # (actor): mirror its facing
ENEMY_CLASSES = (2, 3, 4)  # ordinary enemy spawn slots 0x71..0x73 (the strike's victim scan)
CTRL_HEALTH = 0x654  # zero once dead (the strike's victim scan skips it)
TARGET_RANGE = 592  # world units, square, as the teleport's target (lower_special.RELOCATE_RANGE)
SUM_X_SP, SUM_Y_SP = 0x38, 0x3C  # the child's frame (after the build): this tick's displacement


@dataclass(frozen=True)
class Homing:
    """MKT's homing flight, two donor ticks a host tick (Sektor's legacy robo_tracker, proofs
    v42-v46, runtime-confirmed; its constants now read by SMRE): ``phases`` (donor ticks, y
    velocity taken each tick) then the hunt (``rocket_hunt``): aim ``aim_dy`` px below the
    target, explode within ``explode_within`` px (MKT's rough distance max + min / 2), steer
    by the unit vector times ``steer``, ``v += u - v >> damping``, renormalised to ``speed`` px
    a tick; ``timeout`` donor ticks of hunting. Velocities are donor 16.16 px a donor tick."""

    phases: tuple[tuple[int, int], ...]  # (ticks, climb)
    aim_dy: int
    explode_within: int
    steer: int
    speed: int
    damping: int
    timeout: int
    start_vx: int
    start_dir: int
    direction_at: tuple[int, ...]  # each direction's loop script (file offsets)
    smoke: tuple[tuple[int, int], ...] = ()  # each direction's puff offset (world units, MKT placement)
    marker: str | None = None  # the crosshair's descriptor label (effects.emit_descriptor)
    marker_offset: tuple[int, int] = (0, 0)  # world units from the target
    # Owner adjustment (2026-11-27, proof v14: circling the crosshair "going through the enemies
    # ... it should definitely hit"): the strike every tick while it flies, as the legacy's stock
    # loop did; MKT checks it only when it explodes.
    strike_in_flight: bool = False


def homing_of(step: dict[str, Any], art: ArtLayout) -> Homing:
    h = step["homing"]
    from .generate import _point_direction

    start_vx = _int(step["speed"])
    return Homing(
        tuple((_int(p["ticks"]), _int(p.get("climb", 0))) for p in h["phases"]),
        _int(h["aim_dy"]), _int(h["explode_within"]), _int(h["steer"]), _int(h["speed"]),
        _int(h["damping"]), _int(h["timeout"]), start_vx, _point_direction(start_vx, 0),
        art.direction_at,
        marker_offset=tuple(_int(v) * UNITS_PER_PX for v in h["marker"]["offset"]),  # type: ignore[arg-type]
    )  # fmt: skip


def _abs(a: Assembler, out: str, src: str, tmp: str) -> None:
    a.sra(tmp, src, 31)
    a.xor(out, src, tmp)
    a.subu(out, out, tmp)


def _rough(a: Assembler, out: str, x: str, y: str, ta: str, tb: str, tag: str) -> None:
    """``out`` = MKT's rough distance (0x8006C9C0): max(|x|, |y|) + min / 2."""

    _abs(a, ta, x, out)
    _abs(a, tb, y, out)
    a.slt(out, tb, ta)
    a.beqz(out, tag + "_ymax")
    a.sra(out, tb, 1)
    a.addu(out, out, ta)
    a.beq("zero", "zero", tag + "_done")
    a.label(tag + "_ymax")
    a.sra(out, ta, 1)
    a.addu(out, out, tb)
    a.label(tag + "_done")


def _at_least_one(a: Assembler, reg: str, tag: str) -> None:
    a.bnez(reg, tag + "_nz")
    a.li(reg, 1)
    a.label(tag + "_nz")


def emit_targeting(a: Assembler, prefix: str, range_units: int = TARGET_RANGE) -> None:
    """``<prefix>target(a0 = current target controller or 0) -> v0``: keep it while it is a
    present, living enemy, else the nearest (x) living enemy on the player's path within
    ``range_units`` (square) of him, or 0 (Sektor's legacy homing target, proof v45: the
    controller's last-opponent link can name a dead enemy). Preserves s0-s7."""

    tag = prefix + "target"
    a.label(tag)
    a.addiu("sp", "sp", -0x28)
    a.sw("ra", 0x24, "sp")
    for k, reg in enumerate(("s0", "s1", "s2", "s3")):
        a.sw(reg, 0x20 - 4 * k, "sp")
    a.move("s0", "a0")
    a.beqz("s0", tag + "_pick")
    a.li("s1", ENEMY_CLASSES[0])
    a.label(tag + "_present")  # still a present enemy process?
    a.move("a0", "s1")
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.beq("v0", "s0", tag + "_alive")
    a.addiu("s1", "s1", 1)
    a.slti("t0", "s1", ENEMY_CLASSES[-1] + 1)
    a.bnez("t0", tag + "_present")
    a.beq("zero", "zero", tag + "_pick")
    a.label(tag + "_alive")
    a.lhu("t0", CTRL_HEALTH, "s0")
    a.beqz("t0", tag + "_pick")
    a.lw("t0", host.CTRL_ACTOR, "s0")
    a.bnez("t0", tag + "_done")
    a.label(tag + "_pick")  # the nearest living enemy on the player's path, in range
    a.move("s0", "zero")
    a.lui("s3", host.hi(host.PLAYER_CTRL))
    a.lw("s3", host.lo(host.PLAYER_CTRL), "s3")
    a.beqz("s3", tag + "_done")
    a.lw("s3", host.CTRL_ACTOR, "s3")
    a.beqz("s3", tag + "_done")
    a.lui("s2", 0x7FFF)
    a.li("s1", ENEMY_CLASSES[0])
    a.label(tag + "_loop")
    a.move("a0", "s1")
    a.li("a1", 0xFFFF)
    a.jal(F_FIND_CLASS)
    a.beqz("v0", tag + "_next")
    a.lhu("t0", CTRL_HEALTH, "v0")
    a.beqz("t0", tag + "_next")
    a.lw("t3", host.CTRL_ACTOR, "v0")
    a.beqz("t3", tag + "_next")
    a.lw("t0", host.ACTOR_PATH, "t3")
    a.lw("t1", host.ACTOR_PATH, "s3")
    a.bne("t0", "t1", tag + "_next")
    for field in (host.ACTOR_Y, host.ACTOR_X):  # |enemy - player| within range (x last: t0)
        a.lw("t0", field, "t3")
        a.lw("t1", field, "s3")
        a.subu("t0", "t0", "t1")
        _abs(a, "t0", "t0", "t9")
        a.li("t1", range_units << 8)
        a.slt("t2", "t1", "t0")
        a.bnez("t2", tag + "_next")
    a.slt("t2", "t0", "s2")
    a.beqz("t2", tag + "_next")
    a.move("s2", "t0")
    a.move("s0", "v0")
    a.label(tag + "_next")
    a.addiu("s1", "s1", 1)
    a.slti("t0", "s1", ENEMY_CLASSES[-1] + 1)
    a.bnez("t0", tag + "_loop")
    a.label(tag + "_done")
    a.move("v0", "s0")
    a.lw("ra", 0x24, "sp")
    for k, reg in enumerate(("s0", "s1", "s2", "s3")):
        a.lw(reg, 0x20 - 4 * k, "sp")
    a.jr_ra()
    a.addiu("sp", "sp", 0x28)


def _emit_hunt(a: Assembler, h: Homing, tag: str) -> None:
    """Leaf ``tag``: one donor rocket_hunt step; s1 the missile's actor, s2/s3 its velocity,
    s7 the target controller, the stack sums this tick's displacement including this step's.
    ``v0 = 1`` (``v1`` = the target's actor) within the explosion distance of the aim point,
    without steering; else 0. Uses t0-t9."""

    a.label(tag)
    a.move("v0", "zero")
    a.beqz("s7", tag + "_done")
    a.lw("t0", host.CTRL_ACTOR, "s7")
    a.beqz("t0", tag + "_done")
    for field, vel, sum_sp, reg in ((host.ACTOR_X, "s2", SUM_X_SP, "t1"), (host.ACTOR_Y, "s3", SUM_Y_SP, "t2")):
        a.lw(reg, field, "t0")
        a.lw("t3", field, "s1")
        a.subu(reg, reg, "t3")
        a.sra(reg, reg, 9)  # 24.8 world units -> px (2 units a px)
        a.lw("t3", sum_sp, "sp")
        a.subu("t3", "t3", vel)
        a.sra("t3", "t3", 16)  # px the earlier steps of this tick moved
        a.subu(reg, reg, "t3")
    a.addiu("t2", "t2", h.aim_dy)
    _rough(a, "t4", "t1", "t2", "t5", "t6", tag + "_r0")
    a.slti("t4", "t4", h.explode_within)
    a.beqz("t4", tag + "_steer")
    a.move("v1", "t0")
    a.jr_ra()
    a.li("v0", 1)
    a.label(tag + "_steer")
    a.li("t3", h.steer)
    a.mult("t1", "t3")
    a.mflo("t1")
    a.mult("t2", "t3")
    a.mflo("t2")
    _rough(a, "t4", "t1", "t2", "t5", "t6", tag + "_r1")
    a.sra("t4", "t4", 16)
    _at_least_one(a, "t4", tag + "_n1")
    a.div("t1", "t4")
    a.mflo("t1")
    a.div("t2", "t4")
    a.mflo("t2")
    for vel, unit in (("s2", "t1"), ("s3", "t2")):
        a.sra("t5", vel, h.damping)
        a.addu(vel, vel, unit)
        a.subu(vel, vel, "t5")
    _rough(a, "t5", "s2", "s3", "t6", "t7", tag + "_r2")
    a.sra("t5", "t5", 16)
    _at_least_one(a, "t5", tag + "_n2")
    a.li("t6", h.speed)
    for vel in ("s2", "s3"):
        a.div(vel, "t5")
        a.mflo(vel)
        a.mult(vel, "t6")
        a.mflo(vel)
    a.label(tag + "_done")
    a.jr_ra()
    a.nop()


def _emit_direction(a: Assembler, tag: str) -> None:
    """Leaf ``tag(a0 = vx, a1 = vy) -> v0``: MKT point_rocket's direction (0 up .. 3 level by
    the 7/2 ratios, + 4 moving down)."""

    a.label(tag)
    _abs(a, "t0", "a0", "t2")
    _abs(a, "t1", "a1", "t2")
    a.move("v0", "zero")
    a.sll("t2", "t0", 3)
    a.subu("t2", "t2", "t0")
    a.srl("t2", "t2", 1)  # 3.5 |vx|
    a.sltu("t3", "t1", "t2")
    a.beqz("t3", tag + "_down")
    a.li("v0", 1)
    a.sltu("t3", "t1", "t0")
    a.beqz("t3", tag + "_down")
    a.li("v0", 2)
    a.sll("t2", "t1", 3)
    a.subu("t2", "t2", "t1")
    a.srl("t2", "t2", 1)  # 3.5 |vy|
    a.sltu("t3", "t2", "t0")
    a.beqz("t3", tag + "_down")
    a.li("v0", 3)
    a.label(tag + "_down")
    a.blez("a1", tag + "_done")
    a.addiu("v0", "v0", 4)
    a.label(tag + "_done")
    a.jr_ra()
    a.nop()


def emit_homing_flight(a: Assembler, p: Lowered, prefix: str, explode: str,
                       collide: Callable[[], None] | None = None) -> None:  # fmt: skip
    """The homing flight (in place of :func:`emit_process`'s straight one): per host tick the
    target kept (or re-picked), two donor steps (phases, then the hunt), the host velocity
    from their displacement (as the straight flight's speeds), the direction art and facing,
    one smoke puff at the direction's placement (from the second tick), the animation, a
    sleep. No strike while it flies (MKT checks it only when it explodes): within the
    explosion distance it is put on the aim point and stopped, then ``explode``; the hunt's
    timeout explodes it where it is. s2/s3 velocity, s4 phase << 16 | ticks left, s5
    direction, s6 hunt ticks left, s7 target controller."""

    h = p.homing
    assert h is not None
    hunt_phase = len(h.phases)
    host.load_controller(a)
    a.li("s2", h.start_vx)
    a.lw("t1", 0x700, "s0")  # the owner's facing (the builder's copy), as velocity()
    a.li("t2", 0x10)
    a.bne("t1", "t2", prefix + "h_vx")
    a.subu("s2", "zero", "s2")
    a.label(prefix + "h_vx")
    a.move("s3", "zero")
    a.li("s4", (h.phases[0][0] if h.phases else 0) | (0 if h.phases else hunt_phase << 16))
    a.li("s5", h.start_dir)
    a.li("s6", h.timeout)
    a.move("a0", "zero")
    a.jal_label(prefix + "target")
    a.move("s7", "v0")
    a.la("t0", prefix + "follow")
    a.sw("s7", 0, "t0")
    if h.marker is not None:  # the crosshair, kept on the target by its follower process
        a.beqz("s7", prefix + "h_nomark")
        a.lw("a0", host.CTRL_ACTOR, "s7")
        a.beqz("a0", prefix + "h_nomark")
        a.la("a1", h.marker)
        a.move("a2", "zero")
        a.li("a3", effects.FRONT_SUBLAYER)
        a.jal_label(prefix + "marker_spawn")
        a.label(prefix + "h_nomark")
    if p.trail is not None:
        a.sw("zero", TRAIL_TICK_SP, "sp")

    a.label(prefix + "h_tick")
    a.la("t0", prefix + "heartbeat")
    a.lw("t1", 0, "t0")
    a.addiu("t1", "t1", 1)
    a.sw("t1", 0, "t0")
    a.move("a0", "s7")
    a.jal_label(prefix + "target")
    a.move("s7", "v0")
    a.la("t0", prefix + "follow")
    a.sw("s7", 0, "t0")
    host.load_controller(a)
    a.sw("zero", SUM_X_SP, "sp")
    a.sw("zero", SUM_Y_SP, "sp")
    for k in range(2):  # two donor ticks a host tick
        step = f"{prefix}h_s{k}"
        for vel, sum_sp in (("s2", SUM_X_SP), ("s3", SUM_Y_SP)):
            a.lw("t0", sum_sp, "sp")
            a.addu("t0", "t0", vel)
            a.sw("t0", sum_sp, "sp")
        a.srl("t0", "s4", 16)
        for i, (ticks, climb) in enumerate(h.phases):
            a.li("t1", i)
            a.bne("t0", "t1", f"{step}_p{i}")
            if climb:
                a.li("t2", climb)
                a.subu("s3", "s3", "t2")
            a.addiu("s4", "s4", -1)
            a.andi("t2", "s4", 0xFFFF)
            a.bnez("t2", step + "_done")
            nxt = h.phases[i + 1][0] if i + 1 < len(h.phases) else 0
            a.li("s4", ((i + 1) << 16) | nxt)
            a.beq("zero", "zero", step + "_done")
            a.label(f"{step}_p{i}")
        a.addiu("s6", "s6", -1)  # the hunt: its timeout, then a step
        a.blez("s6", explode)
        a.jal_label(prefix + "hunt")
        a.bnez("v0", prefix + "h_near")
        a.label(step + "_done")
    host.load_controller(a)
    for sum_sp, field in ((SUM_X_SP, host.ACTOR_XVEL), (SUM_Y_SP, host.ACTOR_YVEL)):
        a.lw("t0", sum_sp, "sp")  # two donor ticks' displacement -> the host tick's (2/3, units)
        a.sll("t0", "t0", 1)
        a.li("t1", 3)
        a.div("t0", "t1")
        a.mflo("t0")
        a.sw("t0", field, "s1")
    a.move("a0", "s2")  # the direction art
    a.move("a1", "s3")
    a.jal_label(prefix + "direction")
    host.load_controller(a)
    a.beq("v0", "s5", prefix + "h_facing")
    a.move("s5", "v0")
    a.sll("t1", "v0", 2)
    a.la("t2", prefix + "directions")
    a.addu("t2", "t2", "t1")
    a.lw("t2", 0, "t2")
    a.lw("t0", host.ACTOR_FILE_BASE, "s1")
    a.addu("t0", "t0", "t2")
    a.sw("t0", host.CTRL_SCRIPT_CURSOR, "s0")
    a.label(prefix + "h_facing")  # mirrored when it flies towards -x
    a.slt("t0", "s2", "zero")
    a.sll("t0", "t0", 4)
    a.lhu("t1", ACTOR_FLAGS, "s1")
    a.andi("t1", "t1", FACING_BIT)
    a.beq("t0", "t1", prefix + "h_smoke")
    a.move("a0", "s1")
    a.jal(F_FLIP)
    a.label(prefix + "h_smoke")
    if p.trail is not None:  # MKT rocket_smoke(direction): from the second tick, at its placement
        a.lw("t0", TRAIL_TICK_SP, "sp")
        a.li("t1", 1)
        a.sw("t1", TRAIL_TICK_SP, "sp")
        a.beqz("t0", prefix + "h_smoked")
        host.load_controller(a)
        for k, field in enumerate(TRAIL_FIELDS):
            a.lw("t0", field, "s1")
            a.sw("t0", FOLLOW_SP + 4 * k, "sp")
        for src, dst in effects.RENDER_POSITION:  # from where it is drawn
            a.lw("t0", dst, "s1")
            a.sw("t0", src, "s1")
        a.sll("t1", "s5", 2)
        a.la("t2", prefix + "smoke")
        a.addu("t2", "t2", "t1")
        a.lh("a1", 0, "t2")
        a.lh("a2", 2, "t2")
        a.move("a0", "s1")
        a.jal(F_OFFSET)
        host.load_controller(a)
        a.move("a0", "s1")
        a.la("a1", p.trail)
        a.move("a2", "zero")
        a.lhu("a3", ACTOR_SUBLAYER, "s1")  # behind it
        a.addiu("a3", "a3", 1)
        a.jal_label("fx_spawn")
        host.load_controller(a)
        for k, field in enumerate(TRAIL_FIELDS):
            a.lw("t0", FOLLOW_SP + 4 * k, "sp")
            a.sw("t0", field, "s1")
        a.label(prefix + "h_smoked")
    if h.strike_in_flight and collide is not None:  # owner: it hits what it touches
        collide()
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(F_ADVANCE)
    a.li("a0", 1)
    a.jal(F_SLEEP)
    a.beq("zero", "zero", prefix + "h_tick")

    a.label(prefix + "h_near")  # on the aim point, stopped (the strike resolves there)
    host.load_controller(a)
    a.lw("t0", host.ACTOR_X, "v1")
    a.sw("t0", host.ACTOR_X, "s1")
    a.lw("t0", host.ACTOR_Y, "v1")
    a.li("t1", h.aim_dy << 9)
    a.addu("t0", "t0", "t1")
    a.sw("t0", host.ACTOR_Y, "s1")
    a.sw("zero", host.ACTOR_XVEL, "s1")
    a.sw("zero", host.ACTOR_YVEL, "s1")
    a.beq("zero", "zero", explode)

    _emit_hunt(a, h, prefix + "hunt")
    _emit_direction(a, prefix + "direction")
    emit_targeting(a, prefix)


def emit_homing_data(a: Assembler, h: Homing, prefix: str) -> None:
    """The flight's words: the heartbeat and target its crosshair follows, each direction's
    loop script offset and puff placement (dx, dy halfwords, world units)."""

    for name in ("heartbeat", "follow"):
        a.label(prefix + name)
        a.raw(0)
    a.label(prefix + "directions")
    for at in h.direction_at:
        a.raw(at)
    a.label(prefix + "smoke")
    for dx, dy in h.smoke or ((0, 0),) * len(h.direction_at):
        a.raw(((dx & 0xFFFF) << 16) | (dy & 0xFFFF))
