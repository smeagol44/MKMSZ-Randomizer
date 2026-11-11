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
BLOCKED_LOWERING = {"blocked": 0x05}


def _int(v: Any) -> int:
    return int(v, 0) if isinstance(v, str) else int(v)


# ---- donor art ------------------------------------------------------------------------------
@dataclass(frozen=True)
class DonorPart:
    frames: tuple[int, ...]  # frame records (heap-relative), in script order
    palette: int | None  # palette bound by token 13 (the next frame record's palette word)
    loops: bool


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
    palette, bind_next, loops = None, False, False
    while True:
        v = donor.m32(p)
        if v == 0:
            break
        if v == 1:
            loops = True
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
        p += 4
    return DonorPart(tuple(frames), palette, loops)


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


def place_art(
    file87: bytearray,
    mkt: bytes,
    donor_id: int,
    step: dict[str, Any],
    slots: tuple[int, int],
    budget: int,
    at: int | None = None,
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
    flight_words = [shape[r] for r in flight.frames for _ in range(rate)]
    flight_at = cursor
    script(flight_words + [1, flight_at])  # loop
    impact_ticks = 0
    entries = [(slots[0], flight_at)]
    if impact is not None:
        impact_rate = _int(impact_step["rate"])
        impact_words = [shape[r] for r in impact.frames for _ in range(impact_rate)]
        impact_ticks = len(impact_words)
        impact_at = cursor
        script(impact_words + [1, impact_at + 4 * (impact_ticks - 1)])  # hold the last frame
        entries.append((slots[1], impact_at))
    if cursor > budget:
        raise ValueError(f"projectile art ends at 0x{cursor:X}, past the budget 0x{budget:X}")
    for slot, where in entries:
        off = 0x104 + 4 * slot
        if file87[off : off + 4] != bytes(4):
            raise ValueError(f"table-1 slot 0x{slot:X} is not empty")
        file87[off : off + 4] = where.to_bytes(4, "big")
    w, h = art.slot_size
    return ArtLayout(placed.offset, slots[0], slots[1] if impact else None, impact_ticks, w, h)


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
    return Lowered(
        art, speed, dx, dy, record, tuple(lifted_reaction(clean, strike["reaction"])),
        events.get("hum"), _int(step.get("hum", {}).get("every", 0)), events.get("impact"),
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
                 prefix: str = "") -> None:  # fmt: skip
    """The projectile process. Needs :func:`host.emit_sound_player` (label ``player``) and
    :func:`emit_data` (labels ``record`` and ``reaction``) in the same assembly. ``prefix``
    names its internal labels, so several processes can share one assembly."""

    a.label(child)
    a.addiu("sp", "sp", -0x40)
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
    host.load_controller(a)
    a.li("t0", p.speed)
    a.lw("t1", 0x700, "s0")
    a.li("t2", 0x10)
    a.bne("t1", "t2", prefix + "set_vel")
    a.subu("t0", "zero", "t0")
    a.label(prefix + "set_vel")
    a.sw("t0", 0x14, "s1")
    a.li("a0", 1)
    a.li("a1", p.art.flight_slot)
    a.jal(F_SELECT)
    a.li("s3", 0)
    a.label(prefix + "fly")
    if p.hum_event is not None:
        a.addiu("s3", "s3", 1)
        a.slti("t0", "s3", p.hum_every)
        a.bnez("t0", prefix + "no_hum")
        a.addiu("s3", "s3", -p.hum_every)
        host.play_sound(a, p.hum_event, player)
        a.label(prefix + "no_hum")
    host.load_controller(a)
    a.la("a0", "record")
    a.lui("t0", KSEG1_TO_KSEG0 >> 16)
    a.subu("a0", "a0", "t0")  # KSEG0 alias: the collision core rejects other records
    a.sw("a0", 0x638, "s0")
    a.move("a1", "zero")
    a.jal(F_COLLIDE)
    a.andi("v0", "v0", 0xFFFF)
    a.li("t0", 0x8000)
    a.beq("v0", "t0", prefix + "on_contact")
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
    a.jal(F_EXIT)
    a.label(prefix + "child_hang")
    a.beq("zero", "zero", prefix + "child_hang")


def emit_data(a: Assembler, p: Lowered, base: int) -> None:
    """Strike record (16-aligned, read through its KSEG0 alias) and the lifted reaction."""

    while (a.pc() - base) % 16:
        a.nop()
    a.label("record")
    for i in range(0, 16, 4):
        a.raw(int.from_bytes(p.record[i : i + 4], "big"))
    a.label("reaction")
    for word in p.reaction_words:
        a.raw(word)
