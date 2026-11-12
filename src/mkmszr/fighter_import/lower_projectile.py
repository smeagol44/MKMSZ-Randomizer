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

from dataclasses import dataclass
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
ACTOR_FLAGS, FACING_BIT = 0x8C, 0x10  # actor facing (0x800344F4, 0x8002B6F4)

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
    },
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
BLOCKED_LOWERING = {"blocked": 0x05}


def stumble_push(meaning: str) -> int:
    spec = REACTION_LOWERING[meaning]
    return round(spec["stock_push"] * spec["donor_push"] / spec["donor_ref"])


def lift_stumble(clean: bytes, meaning: str, dst_va: int) -> bytes:
    """A stumble-kind reaction lifted to run at ``dst_va`` (``fighter_import.lifter``)."""

    from . import lifter

    spec = REACTION_LOWERING[meaning]
    base, end = spec["base"], spec["end"]
    code = clean[base - 0x7FFFF400 : end - 0x7FFFF400]
    push = stumble_push(meaning)
    neg = -push & 0xFFFFFFFF
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


def donor_part(donor: Donor, anim: dict[str, Any]) -> DonorPart:
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


def _frame(donor: Donor, rel: int, shift: int) -> effects.EffectFrame:
    f = donor.frame(rel)
    indices = bytes(0 if v == 0 else v + shift for v in f["padded"])
    return effects.EffectFrame(f["w"], f["eh"], f["x"], f["y"], indices)


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
) -> ArtLayout:
    """Put the projectile's art in the fighter file and point table-1 ``slots`` (empty in
    stock) at its flight and impact scripts. By default it is appended; with ``at`` it is
    written from that offset inside the file (e.g. the body region's free tail, Sektor proof
    v47's heap-neutral placement) and must end by ``budget``."""

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
    flight = donor_part(donor, step["art"])
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
    rels = list(dict.fromkeys(flight.frames))
    frames = [_frame(donor, r, 0) for r in rels]
    if impact is not None:
        impact_palette = (
            list(effects.mkt_palette(mkt, impact.palette)) if impact.palette else flight_palette
        )
        colours += impact_palette + [0] * (32 - len(impact_palette))
        impact_rels = list(dict.fromkeys(impact.frames))
        frames += [_frame(donor, r, 32) for r in impact_rels]
        rels += impact_rels
    if helper is not None:  # the helper's frames take the flight palette (MKT binds it from them)
        helper_rels = [r for r in dict.fromkeys(helper.frames) if r not in rels]
        frames += [_frame(donor, r, 0) for r in helper_rels]
        rels += helper_rels
    art = effects.EffectArt(tuple(frames), tuple(colours), compressed=True)
    placed = effects.layout(art, (cursor + 3) & ~3)
    put(bytes(placed.offset - cursor) + placed.data)
    script_at = placed.script - placed.offset
    shape = {
        rel: int.from_bytes(placed.data[script_at + 4 * i : script_at + 4 * i + 4], "big")
        for i, rel in enumerate(rels)
    }

    def script(words: list[int]) -> int:
        return put(b"".join(w.to_bytes(4, "big") for w in words))

    rate = _int(step["rate"])
    # Frames shown by the close-range check steps appear once each (one advance per step);
    # the rest at ``rate``; the loop goes back to the donor's loop frame (MKT acid: 0x31B0).
    early = len(step.get("checks", []))
    flight_words = [shape[r] for r in flight.frames[:early]]
    flight_words += [shape[r] for r in flight.frames[early:] for _ in range(rate)]
    loop_word = (flight.loop_from if flight.loop_from < early
                 else early + (flight.loop_from - early) * rate)  # fmt: skip
    flight_at = cursor
    script(flight_words + [1, flight_at + 4 * loop_word])  # loop
    impact_ticks = 0
    entries = [(slots[0] if slots else 0, flight_at)]
    if impact is not None:
        impact_rate = _int(impact_step["rate"])
        impact_words = [shape[r] for r in impact.frames for _ in range(impact_rate)]
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
        script([shape[r] for r in helper.frames] + [1, helper_at + 4 * (n - 1)])
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
    if helper is None and not virtual:
        return ArtLayout(placed.offset, flight_slot, impact_slot, impact_ticks, w, h)
    return ArtLayout(placed.offset, flight_slot, impact_slot, impact_ticks, w, h,
                     helper_slot, helper.start if helper else 0, len(helper.frames) if helper else 0,
                     virtual, flight_at, impact_at if impact else 0, helper_at)  # fmt: skip


# ---- sounds, strike and reaction --------------------------------------------------------------
def install_sounds(
    rom: bytearray, clean: bytes, mkt: bytes, donor_id: int, step: dict[str, Any],
    chains: tuple[sound.HostChain, ...], sample_rom: int,
) -> tuple[dict[str, int], int]:  # fmt: skip
    """Host the hum and impact sounds; returns their host events and the next sample address."""

    bank = sound.MktSoundBank(mkt)
    events: dict[str, int] = {}
    wanted = [
        ("hum", step.get("hum", {}).get("sound")),
        ("impact", step.get("impact", {}).get("sound")),
    ]
    free = list(chains)
    for name, snd in wanted:
        if not snd:
            continue
        if "fighter" not in snd:
            raise ValueError("only fighter sounds are supported")
        chain = free.pop(0)
        donor = bank.event(bank.fighter_event(donor_id, _int(snd["fighter"])))
        sample_rom = sound.install(rom, clean, donor, chain, sample_rom)
        events[name] = chain.event
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
    return words


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


def strike_record(strike: dict[str, Any], reaction_slot: int) -> bytes:
    """16-byte host strike record: donor box, reaction slot, blocked reaction by meaning, damage
    and chip damage, stock trailer."""

    box = [_int(v) for v in strike["box"]]
    record = b"".join((v & 0xFFFF).to_bytes(2, "big") for v in box)
    record += bytes((reaction_slot, BLOCKED_LOWERING[strike["blocked_reaction"]]))
    record += bytes((_int(strike["damage"]), _int(strike["block_damage"])))
    return record + bytes.fromhex("00010000")


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
    return Lowered(
        art, speed, dx, dy, record, words,
        events.get("hum"), _int(step.get("hum", {}).get("every", 0)), events.get("impact"),
        meaning, checks, impact.get("at") == "opponent",
        _int(impact.get("adjust", [0, 0])[0]) * UNITS_PER_PX,
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

    def velocity() -> None:
        host.load_controller(a)
        a.li("t0", p.speed)
        a.lw("t1", 0x700, "s0")
        a.li("t2", 0x10)
        a.bne("t1", "t2", prefix + "set_vel")
        a.subu("t0", "zero", "t0")
        a.label(prefix + "set_vel")
        a.sw("t0", 0x14, "s1")

    def collide(record: str, hit: str) -> None:
        host.load_controller(a)
        a.la("a0", record)
        a.lui("t0", KSEG1_TO_KSEG0 >> 16)
        a.subu("a0", "a0", "t0")  # KSEG0 alias: the collision core rejects other records
        a.sw("a0", 0x638, "s0")
        a.move("a1", "zero")
        a.jal(F_COLLIDE)
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
    a.lhu("a0", 0x78, "s1")  # owner type (4)
    a.li("a1", p.art.flight_slot)
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
    a.move("a0", "s1")
    a.li("a1", p.dx)
    a.li("a2", p.dy)
    a.jal(F_OFFSET)
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
    a.label(prefix + "fly")
    if p.hum_event is not None:
        a.addiu("s3", "s3", 1)
        a.slti("t0", "s3", p.hum_every)
        a.bnez("t0", prefix + "no_hum")
        a.addiu("s3", "s3", -p.hum_every)
        host.play_sound(a, p.hum_event, player)
        a.label(prefix + "no_hum")
    collide(data + "record", prefix + "on_contact")
    host.load_controller(a)
    a.move("a0", "s1")
    a.jal(F_ADVANCE)
    a.li("a0", 1)
    a.jal(F_SLEEP)
    host.load_controller(a)
    a.move("a0", "s1")
    a.li("a1", OFFSCREEN_MARGIN)
    a.jal(F_OFFSCREEN)
    a.beqz("v0", prefix + "fly")
    a.beq("zero", "zero", prefix + "done")
    a.label(prefix + "on_contact")
    if p.impact_event is not None:
        host.play_sound(a, p.impact_event, player)
    if p.art.impact_slot is not None:
        host.load_controller(a)
        a.sw("zero", 0x14, "s1")
        if p.impact_at_opponent:  # on the opponent, facing the attacker, MKT's adjust
            a.lw("t0", host.CTRL_OPPONENT, "s0")
            a.beqz("t0", prefix + "no_opponent")
            a.lw("t0", host.CTRL_ACTOR, "t0")
            a.beqz("t0", prefix + "no_opponent")
            a.lw("t1", host.ACTOR_X, "t0")
            a.sw("t1", host.ACTOR_X, "s1")
            a.lw("t1", host.ACTOR_Y, "t0")
            a.sw("t1", host.ACTOR_Y, "s1")
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
        a.li("s2", p.art.impact_ticks)
        a.label(prefix + "impact_loop")
        host.load_controller(a)
        a.move("a0", "s1")
        a.jal(F_ADVANCE)
        a.li("a0", 1)
        a.jal(F_SLEEP)
        a.addiu("s2", "s2", -1)
        a.bnez("s2", prefix + "impact_loop")
    a.label(prefix + "done")
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


HELPER_IDLE, HELPER_SHOWN, HELPER_LAUNCH = 0, 1, 2

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
    its own clock and drifted a pose or more (owner). ``dx``/``dy``: offset from the owner."""

    state = label + "_state"
    a.label(label)
    a.addiu("sp", "sp", -0x40)
    a.li("s2", -1)  # last body pose shown
    a.li("s3", 0)  # built
    a.li("s4", HELPER_MAX_TICKS)
    a.label(label + "_loop")
    a.la("t0", state)
    a.lw("t1", 0, "t0")
    a.li("t2", HELPER_LAUNCH)
    a.beq("t1", "t2", label + "_end")
    a.lui("t0", host.hi(host.PLAYER_CTRL))
    a.lw("t0", host.lo(host.PLAYER_CTRL), "t0")
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
    a.label(data + "reaction")
    if REACTION_LOWERING[p.reaction_meaning].get("kind", "arc") == "stumble":
        if clean is None:
            raise ValueError("a stumble reaction is lifted from the clean ROM")
        code = lift_stumble(clean, p.reaction_meaning, a.pc())
        for i in range(0, len(code), 4):
            a.raw(int.from_bytes(code[i : i + 4], "big"))
    else:
        for word in p.reaction_words:
            a.raw(word)
