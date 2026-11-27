"""A described fighter built into a 16 MiB MKMSZ image (milestone 4 step 5 / milestone 5).

The generic form of the Reptile specials proof builders (``Experimental/
FighterRecompilerProofs/MKMSZR_build_reptile-specials_proof_vNN.py``), without their proof
harness (debug stage menu, max-EXP cheat, raw-loaded payload arena). Everything a fighter
needs comes from its description (``fighter_import.description``), its move programs
(``components``) and the reusable components; the builder only applies rules and allocates
host resources from pools:

* **body:** ``body_build`` + ``common_moves``; combos (``combos``); voices (``voices``);
* **specials,** in the description's ``specials`` order, each in the slot of the Sub-Zero
  power its command takes (``commands``), with its own transfer selector (from 3), its
  Sektor-style gate condition (``lower_special``) and action:

  - a move with a ``projectile`` step gets the generic projectile (``lower_projectile``).
    Moves whose projectile art is the same donor part share the art, the throw helper, the
    projectile sounds and the strike data (Reptile's two forceballs). The art goes into the
    free body tail of the fighter file, through the ``art_slots`` empty table-1 slots or, by
    default, virtual entries. The throw helper is drawn 2 px above its projectile;
  - each projectile process sets an alive word. ``limit: "per_move"`` moves refuse only
    while their own projectile or a projectile of a move without that limit lives; other
    moves refuse while any projectile lives;
  - victim reactions with no stock entry (the projectile's lifted reaction, ``elbow_hold``)
    take spare reaction-table entries from :data:`REACTION_POOL`;
  - ``sound`` steps, projectile sounds and ``footsteps`` take isolated host sound chains from
    the pool (the voice set's spare chains last);
  - ``effects`` (shared MKT ``create_fx`` art) go into the fighter file and play through one
    effect process; ``stealth`` uses the Eye item's effect with an Ice-paid timer;

* **presentation:** Power Ups icons (``fighter_icons``) and help (``fighter_help``) are left
  to the product patch, which applies them to the randomizer ROM.

:func:`build` links the payload (code and data of every special, the moved command tables
and the command stubs) at ``link_va`` and puts it at :data:`SCRATCH_ROM` (outside the
fighter's production footprint; production moves it into the fighter file).
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any

from . import (
    body_build,
    combos,
    commands,
    common_moves,
    components,
    effects,
    host,
    lower_special,
    mkt_effects,
    physics,
    sound,
    throw_sounds,
    voices,
)
from . import description as fd
from . import lower_projectile as lp
from .mips import Assembler
from .mkt_fighter import MktRom, validate_mkt_n64_rev2

VA_TO_ROM = 0x7FFFF400
LINK_VA = 0xA01AF420  # the proofs' payload address (any address works: production relocates)
SCRATCH_ROM = 0x00F10000  # the proofs' file 0x1B: the payload's place in the intermediate image
PAYLOAD_LIMIT = 0x4000
TABLE_RESERVE = 0x100  # moved command tables at the payload start
SAMPLE_ROM = 0x00F20000  # donor samples in the intermediate image (production moves them)
FIRST_SELECTOR = 3  # stock transfer selectors 0..2
TRANSFER_BOUND_ROM, TRANSFER_BOUND_STOCK = 0x4B654, 0x2CC20003  # sltiu v0, a2, 3
TRANSFER_ENTRIES_FREE = 5  # 0x800A105C..0x800A106C: zero and unreferenced (Memory map)
# Spare reaction-table entries (stock 0x8004E0C0 endless sleep, no strike record uses them;
# Wiki Memory-and-Allocation-Map): 0x2B, 0x23, then bytes 0x4C and 0x4E past the 64 reactions
# (blocked entries 0x0C and 0x0E).
REACTION_POOL = (0x2B, 0x23, 0x4C, 0x4E)
VOICE_CHAINS = sound.ISOLATED_CHAINS[:10]
EXTRA_CHAINS = sound.ISOLATED_CHAINS[10:]
HELPER_DY_PX = -2  # throw helper above its projectile (owner fine-tune, specials proofs v09/v11)


class BuildError(ValueError):
    pass


def with_hover(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """A move tuned ``airborne`` (it may start in the air, Rayden's torpedo) flies level on the
    host: ``hover`` (no gravity, no y motion, the airborne counter kept) after its begin and on
    every tick of its hit windows and carries. MKT's objects do not fall during a special, so
    this is the host's, not part of the move program (generator step 4, 2026-11-26)."""

    out: list[dict[str, Any]] = []
    for s in steps:
        s = dict(s)
        for key in ("on_hit", "on_block", "steps"):
            if key in s:
                s[key] = with_hover(s[key])
        if s["op"] in ("strike", "carry"):
            s["every_tick"] = [{"op": "hover"}, *with_hover(s.get("every_tick", []))]
        out.append(s)
        if s["op"] == "begin":
            out.append({"op": "hover"})
    return out


def impact_mirror(proj: dict[str, Any], ptune: dict[str, Any]) -> bool:
    """Host corrections for an "at opponent" impact, on by default since specials proof v19
    (Reptile, after Rayden v09-v18): MKT's ``flip_single`` faces it to the attacker, and the host
    then draws it the other way, so its art is mirrored (``place_art``); the impact also goes to
    the enemy the strike hit, at its whole position (``impact_at_hit``), and keeps the
    projectile's own height (``impact_keep_y``). A description can still turn each off."""

    at_opponent = proj.get("impact", {}).get("at") == "opponent"
    flip = bool(ptune.get("impact_flip", True))
    return bool(ptune.get("impact_mirror", at_opponent and flip))


def _int(v: Any) -> int:
    return int(v, 0) if isinstance(v, str) else int(v)


def _put32(rom: bytearray, off: int, word: int) -> None:
    rom[off : off + 4] = (word & 0xFFFFFFFF).to_bytes(4, "big")


def _guarded(rom: bytearray, off: int, old: int, new: int) -> None:
    if int.from_bytes(rom[off : off + 4], "big") != old:
        raise BuildError(f"ROM 0x{off:X} is not 0x{old:08X}")
    _put32(rom, off, new)


def smre_programs(mkt: bytes, fighter: int, records: dict[str, int], stored: dict[str, Any],
                  report: dict[str, Any]) -> dict[str, components.Move]:  # fmt: skip
    """The moves of ``records`` (move -> MKT command record) as the Special Move Recompile Engine
    writes them (``generate.Generator.program``), validated like stored programs. A stored
    program's ``grab`` flag (an owner classification) carries over. The engine's notes and
    unknowns go into ``report["smre"]``."""

    from . import generate

    gen = generate.Generator(mkt, fighter)
    docs, info = [], {}
    for move, record in records.items():
        prog, g, notes = gen.program(move, record)
        if move in stored and stored[move].grab:
            prog["grab"] = True
        docs.append(prog)
        info[move] = {"record": f"0x{record:08X}", "notes": notes + g.notes, "unknown": list(g.unknown)}
    report["smre"] = info
    try:
        made = components.validate_programs({"format": components.FORMAT, "moves": docs})
    except components.ProgramError as e:
        raise BuildError(f"SMRE program does not validate: {e}") from e
    return {m.name: m for m in made}


# Motions (a jump that sinks below the screen or rises to the floor; Sektor's teleport uppercut):
# MKT moves the sprite past the screen's bottom line, with no floor clip. The host keeps the
# fighter on his floor and draws his pose lower each tick: descriptor-only aliases of the frame
# (the image shared, the anchor y lowered by the depth), as Sektor's runtime-confirmed legacy
# teleport (proofs v04-v18).
SCREEN_BOTTOM_PX = 150  # MKT's bottom line below the floor (the legacy surface speed 0xC6666, v04)
SINK_HIDDEN_PX = 320  # the sink goes on to here (legacy: 311), then one far alias hides him
HIDDEN_PX = 1000


def _script_offset(file87: bytes, where: Any) -> int:
    if isinstance(where, tuple) and where[0] == "at":
        return where[1]
    if isinstance(where, tuple) and where[0] == "primary":
        return int.from_bytes(file87[4 * where[1] : 4 * where[1] + 4], "big")
    return int.from_bytes(file87[0x104 + 4 * where : 0x108 + 4 * where], "big")


def _depths(y: int, gravity: int, donor_ticks: int, start: float, stop: Any) -> tuple[list[int], float]:
    """Depths (px below the floor) each host tick along MKT's curve (16.16 per donor tick: y +=
    v, then v += g), from ``start`` until ``stop(depth)``; and the velocity at the end."""

    d, v, out = start, y / 65536, []
    while not stop(d):
        for _ in range(donor_ticks):
            d += v
            v += gravity / 65536
        out.append(round(d))
        if len(out) > 120:
            raise BuildError("a motion never reaches its end")
    return out, v


def motion_scripts(file87: bytearray, steps: list[dict[str, Any]], animations: dict, donor_ticks: int,
                   at: int) -> tuple[dict[int, lower_special.Motion], int]:  # fmt: skip
    """The alias scripts of a move's sinking and rising ``jump`` steps, placed from ``at`` in the
    fighter file; returns ``id(step) -> Motion`` and the next free offset."""

    out: dict[int, lower_special.Motion] = {}
    shown: tuple[int, int] | None = None  # (script, word) of the frame on screen
    running: int | None = None  # the running animation's script

    def be32(o: int) -> int:
        return int.from_bytes(file87[o : o + 4], "big")

    def put(o: int, v: int) -> None:
        file87[o : o + 4] = (v & 0xFFFFFFFF).to_bytes(4, "big")

    def alias(shape: int, depth: int) -> int:
        nonlocal at
        sub, mine = be32(shape), at
        put(mine, mine + 8)
        put(mine + 4, 0)
        file87[mine + 8 : mine + 18] = file87[sub : sub + 10]  # image, w, h, x
        y = int.from_bytes(file87[sub + 10 : sub + 12], "big", signed=True)
        file87[mine + 18 : mine + 20] = ((y - depth) & 0xFFFF).to_bytes(2, "big")
        at += 20
        return mine

    for step in steps:
        op = step["op"]
        if op in ("pose", "animate"):
            key = (int(step["anim"]["table"]), int(step["anim"]["slot"]))
            script = _script_offset(file87, animations[key])
            shown = (script, int(step["anim"].get("offset", 0)))
            running = script if step.get("until") == "running" else None
        if op != "jump" or step["until"] not in ("below_screen", "surface"):
            continue
        y, g = lp._int(step["y"]), lp._int(step["gravity"])
        if step["until"] == "below_screen":
            if shown is None:
                raise BuildError("a sink with no pose before it")
            shape = be32(shown[0] + 4 * shown[1])
            depths, _ = _depths(y, g, donor_ticks, 0, lambda d: d >= SINK_HIDDEN_PX)
            frames = [shape] + [alias(shape, d) for d in depths] + [alias(shape, HIDDEN_PX)]
            out[id(step)] = lower_special.Motion(at, len(frames))
        else:
            if running is None:
                raise BuildError("a rise with no running animation before it")
            shape = be32(running)
            depths, v = _depths(y, g, donor_ticks, SCREEN_BOTTOM_PX, lambda d: d <= 0)
            frames = [alias(shape, d) for d in depths[:-1]] + [shape]
            near = int(step.get("strike_near_px", 0))
            near_from = next((k for k, d in enumerate(depths[:-1] + [0]) if d < near), None) if "strike" in step else None
            out[id(step)] = lower_special.Motion(at, len(frames), near_from, round(v * 65536))
        script = at
        for k, f in enumerate(frames):
            put(script + 4 * k, f)
        if step["until"] == "below_screen":  # hold the hidden frame
            put(script + 4 * len(frames), 1)
            put(script + 4 * len(frames) + 4, script + 4 * (len(frames) - 1))
            at = script + 4 * len(frames) + 8
        else:  # then the running animation from its second frame
            put(script + 4 * len(frames), 1)
            put(script + 4 * len(frames) + 4, running + 4)
            at = script + 4 * len(frames) + 8
    return out, at


def _free_from(file87: bytearray, start: int) -> int:
    """First 16-aligned offset after the last used byte of the body tail [start, TYPE_END)."""

    end = body_build.TYPE_END
    used = start
    for off in range(end - 1, start - 1, -1):
        if file87[off] != 0xFF:
            used = off + 1
            break
    return (used + 0xF) & ~0xF


@dataclass
class _Group:
    """The moves whose projectile step has the same donor art and victim reaction (the art is
    placed once per donor art: Rayden's lightning and reversed lightning share it, but react
    differently, MKT 0x80 / 0x81)."""

    key: tuple[int, int, int]
    reaction: str
    moves: list[str]
    art: lp.ArtLayout
    events: dict[str, int]
    reaction_slot: int
    helper: str | None
    lowered: lp.Lowered | None = None
    first: bool = True  # the first group of its art (its labels and report key, as before)


@dataclass
class Built:
    rom: bytes  # 16 MiB image (no checksum update)
    payload: bytes  # the payload linked at ``link_va`` (also at SCRATCH_ROM in ``rom``)
    link_va: int
    file87: bytes
    samples: tuple[int, int]  # [start, end) ROM of the donor samples in ``rom``
    moved_tables: dict[str, int] = field(default_factory=dict)  # button -> table VA in the payload
    selectors: dict[str, int] = field(default_factory=dict)
    reactions: dict[str, int] = field(default_factory=dict)
    chains: dict[str, int] = field(default_factory=dict)  # what -> host event
    report: dict[str, Any] = field(default_factory=dict)


class _Pool:
    def __init__(self, items: tuple, what: str) -> None:
        self.items, self.what, self.used = list(items), what, 0

    def take(self) -> Any:
        if self.used >= len(self.items):
            raise BuildError(f"no {self.what} left")
        self.used += 1
        return self.items[self.used - 1]


def build(clean: bytes, mkt: bytes, name: str, *, link_va: int = LINK_VA,
          indirect: dict[str, int] | None = None) -> Built:  # fmt: skip
    validate_mkt_n64_rev2(mkt)
    d = fd.load(name)
    donor_id = d.donor_fighter_id
    donor = body_build.Donor(mkt, donor_id)
    rom = bytearray(clean)
    try:  # stored programs (references once SMRE writes the moves)
        stored, _ = components.load_programs(name)
    except FileNotFoundError:  # a fighter whose moves SMRE writes, with no references
        stored = []
    programs = {m.name: m for m in stored}
    report: dict[str, Any] = {}
    if d.smre:  # SMRE: the programs written from MKT's own code (the stored ones are references)
        programs.update(smre_programs(mkt, donor_id, d.smre, programs, report))
    order = list(d.specials) + [m for m, p in d.commands.items() if p and m not in d.specials]
    for move in order:
        if move not in programs:
            raise BuildError(f"{move}: no move program")

    # ---- body, file 0x87 ------------------------------------------------------------------
    body = body_build.build_body(d, clean, mkt, body_build.Extras(), rom=rom)
    file87 = common_moves.apply(
        bytes(body.file), stock=body.clean_file, flipped=body.flipped,
        slide="slide" in d.body.common_animations,
    )  # fmt: skip
    combo_graph = combos.donor_graph(mkt, donor_id)
    vs, samples_end = voices.install(rom, clean, mkt, donor_id, VOICE_CHAINS, SAMPLE_ROM)
    used_voices = len(set(vs.category.values()) - {None})
    chains = _Pool(tuple(EXTRA_CHAINS) + tuple(VOICE_CHAINS[used_voices:]), "isolated sound chains")
    voice_chains = list(VOICE_CHAINS[:used_voices])
    bank = sound.MktSoundBank(mkt)
    script_sound: tuple[int, int] | None = None  # (donor sound, host event): moves share it
    if d.body.script_sounds:  # body.script_sounds: the spare descriptor's event plays it
        (sfx,) = set(d.body.script_sounds.values())
        chain = chains.take()
        samples_end = voices.install_script_sound(rom, clean, mkt, donor_id, sfx, chain,
                                                  (samples_end + 0xF) & ~0xF, vs)  # fmt: skip
        script_sound = (sfx, chain.event)

    def install(donor_sound: sound.DonorSound) -> int:
        nonlocal samples_end
        chain = chains.take()
        samples_end = sound.install(rom, clean, donor_sound, chain, (samples_end + 0xF) & ~0xF)
        return chain.event

    animations: dict[tuple, int | tuple[str, int]] = {}
    for key, (t, i, _) in d.body.secondary_scripts.items():  # backwards ones: (t, i, "reverse")
        where = key if key < body_build.VIRTUAL_SCRIPT else ("at", body.script_offsets[key])
        animations[(t, i, "reverse") if key in d.body.reverse_scripts else (t, i)] = where
    animations[(0, d.body.run_slot)] = ("at", body_build.RUN_TARGET)
    for k in d.body.slots:  # host primary k holds MKT table-0 index k (the generic body rule)
        if k not in d.body.sources:  # (a slot with another source holds something else)
            animations.setdefault((0, k), ("primary", k))
    script_words = {(t, i): body.script_words[key] for key, (t, i, _) in d.body.secondary_scripts.items()
                    if key in body.script_words}  # fmt: skip

    # ---- projectile groups and art (fighter-file tail) -------------------------------------
    reactions = _Pool(REACTION_POOL, "spare reaction-table entries")
    groups: dict[tuple[tuple[int, int, int], str], _Group] = {}
    art_of: dict[tuple[int, int, int], tuple[lp.ArtLayout, dict[str, int], str | None]] = {}
    afterimage_of: dict[str, tuple[str, lp.ArtLayout, int]] = {}  # move -> (process, art, ticks)
    cooldown_of: dict[str, int] = {}  # move -> clock ticks (MKT ticks_since conditions, 60 Hz)
    steps_of: dict[str, list[dict[str, Any]]] = {}
    projectile_of: dict[str, dict[str, Any]] = {}
    placed_at = body.chain_start
    fighter_sounds: dict[int, int] = dict([script_sound]) if script_sound else {}
    footsteps: dict[str, tuple[int, ...]] = {}
    effect_art: dict[int, tuple[effects.EffectArt, effects.EffectLayout, dict[str, Any]]] = {}
    fx_info: dict[tuple[str, str], mkt_effects.MktEffect] = {}  # (move, "trail" | "impact")
    report["body"] = body.report
    for move in order:
        tune = d.specials.get(move, {})
        steps = list(programs[move].steps)
        if "sleep_ticks" in tune:  # owner: a different recovery (Acid Spit, specials proof v11)
            steps = [dict(s, ticks=_int(tune["sleep_ticks"])) if s["op"] == "sleep" else s for s in steps]
        if "strike_ticks" in tune:  # owner: a longer hit window (Rayden's torpedo, specials proof v05)
            steps = [dict(s, ticks=_int(tune["strike_ticks"])) if s["op"] == "strike" else s for s in steps]
        if tune.get("turn_back"):  # owner: after turning around, turn back rather than face
            steps = [dict(s, op="flip") if s["op"] == "face" else s for s in steps]  # (reversed lightning)
        if tune.get("airborne"):  # level flight while it may have started in the air (host detail)
            steps = with_hover(steps)
        ticks_per = _int(tune.get("donor_ticks", 1))
        if ticks_per > 1:  # projectile frame rates are donor ticks too (Rayden's lightning, v09)
            steps = [_projectile_rates(s, ticks_per) if s["op"] == "projectile" else s for s in steps]
        steps_of[move] = steps
        proj = next((s for s in steps if s["op"] == "projectile"), None)
        if proj is not None:
            ptune = tune.get("projectile", {})
            if "offset_px" in ptune:
                proj = dict(proj, offset=[_int(v) for v in ptune["offset_px"]])
            if ptune.get("box") == "centre_on_art":
                proj = lp.centre_on_art(donor, proj)
            projectile_of[move] = proj
            anim = proj["art"]
            akey = (_int(anim["table"]), _int(anim["slot"]), _int(anim.get("part", 1)))
            gkey = (akey, proj["strike"]["reaction"])
            if gkey in groups:
                groups[gkey].moves.append(move)
            elif akey in art_of:  # the art and sounds placed for another reaction
                art, events, helper_label = art_of[akey]
                stock = lp.host_reaction(proj["strike"]["reaction"])
                groups[gkey] = _Group(akey, proj["strike"]["reaction"], [move], art, events,
                                      stock if stock is not None else reactions.take(), helper_label,
                                      first=False)  # fmt: skip
            else:
                throw = next(s for s in steps if s["op"] == "animate")
                helper = lp.donor_helper(donor, throw["anim"])
                slots = tuple(_int(v) for v in ptune["art_slots"]) if "art_slots" in ptune else None
                at = placed_at if slots is not None else _free_from(file87, body.chain_start)
                art = lp.place_art(file87, mkt, donor_id, proj, slots, body_build.TYPE_END, at=at,
                                   helper=helper,
                                   helper_slot=_int(ptune["helper_slot"]) if "helper_slot" in ptune else None,
                                   throw_rate=int(throw["rate"]),
                                   impact_mirror=impact_mirror(proj, ptune))  # fmt: skip
                needed = len(lp.projectile_sounds(proj))
                events, samples_end = lp.install_sounds(
                    rom, clean, mkt, donor_id, proj, tuple(chains.take() for _ in range(needed)),
                    (samples_end + 0xF) & ~0xF,
                )  # fmt: skip
                stock = lp.host_reaction(proj["strike"]["reaction"])
                helper_label = f"{move}_helper" if helper is not None else None
                art_of[akey] = (art, events, helper_label)
                groups[gkey] = _Group(akey, proj["strike"]["reaction"], [move], art, events,
                                      stock if stock is not None else reactions.take(), helper_label)  # fmt: skip
        for s in _all_steps(steps):  # an afterimage: the fighter's own art for its process
            if s["op"] == "afterimage":
                rate = max(1, -(-_int(s["rate"]) // ticks_per))
                part = {"table": _int(s["anim"]["table"]), "slot": _int(s["anim"]["slot"]), "part": 1}
                art_step: dict[str, Any] = {"art": part, "rate": rate}
                first = lp.donor_part(donor, part).frames
                named = donor.m32(first[0] + 0x14) if first else 0
                if named & 0xFF000000 == 0x80000000:  # its frames name their palette (Rayden's
                    art_step["palette"] = hex(named)  # silhouette: white to cyan, 0x800B9AF0)
                art = lp.place_art(file87, mkt, donor_id, art_step, None,
                                   body_build.TYPE_END, at=_free_from(file87, body.chain_start))  # fmt: skip
                frames = len(first)
                afterimage_of[move] = (f"{move}_afterimage", art, frames * rate)
        cool = next((c for c in programs[move].command.get("conditions", []) if c["kind"] == "cooldown"), None)
        if cool is not None and proj is None:  # projectiles: the host one-projectile rule instead
            cooldown_of[move] = _int(cool["ticks"])  # the clock runs at MKT's rate
        unported: set[int] = set()
        silent = "sound" in tune.get("skip", ())  # owner: the move's sounds left out (no chains)
        for s in [] if silent else _all_steps(steps):  # nested steps too (Rayden's torpedo: on_hit)
            if s["op"] == "sound" and "random" not in s["sound"]:
                n = _int(s["sound"]["fighter"])
                if n not in fighter_sounds and n not in unported:
                    tracks = bank.tracks(bank.fighter_event(donor_id, n))
                    if len(tracks) == 1 and len(tracks[0].track) == 0x20:
                        fighter_sounds[n] = install(tracks[0])
                        continue
                    try:  # several tracks (Rayden's 5, event 0x205): one chain per track
                        for t in tracks:
                            sound.retarget(t.track, 0)
                    except ValueError:  # a stream the port cannot read: left out, reported
                        unported.add(n)
                        report.setdefault("unported_sounds", []).append((move, n))
                        continue
                    fighter_sounds[n], samples_end = sound.install_tracks(
                        rom, clean, tracks, tuple(chains.take() for _ in tracks), (samples_end + 0xF) & ~0xF)
                    report.setdefault("multi_track_sounds", []).append((move, n, len(tracks)))
        if unported:
            steps = _without_sounds(steps, unported)
            steps_of[move] = steps
        for s in [] if silent else _all_steps(steps):  # nested steps too (Rayden's torpedo: on_hit)
            if s["op"] == "sound":
                first = _int(s["sound"]["fighter"])
                for n in range(first, first + _int(s["sound"].get("random", 1))):  # every choice
                    if n not in fighter_sounds:
                        fighter_sounds[n] = install(bank.event(bank.fighter_event(donor_id, n)))
        if "footsteps" in tune:
            footsteps[move] = tuple(install(bank.event(_int(e))) for e in tune["footsteps"])
        for fx, spec in tune.get("effects", {}).items():
            art_fx = effects.mkt_animation_art(mkt, _int(spec["animation"]), _int(spec["dictionary"]))
            placed = effects.layout(art_fx, _free_from(file87, body.chain_start))
            if placed.end > body_build.TYPE_END or set(file87[placed.offset : placed.end]) != {0xFF}:
                raise BuildError(f"{move}: effect {fx} art does not fit the fighter file")
            file87[placed.offset : placed.end] = placed.data
            effect_art[int(fx)] = (art_fx, placed, spec)
        for fx in _unlowered_effects(projectile_of.get(move)):
            report.setdefault("effects_not_lowered", []).append((move, fx))
        for role, eff in _projectile_effects(projectile_of.get(move)):  # Sektor's smoke and explosion
            fx = _int(eff["mkt_fx"])
            info = mkt_effects.read(mkt, fx, _int(eff["place"]) if "place" in eff else None)
            fx_info[(move, role)] = info
            if fx in effect_art:
                continue
            start, end = MktRom(mkt).dictionary(donor_id)
            shared = mkt[mkt_effects.SHARED_DICTIONARY - 0x80000000 :][:0x100]
            art_fx = mkt_effects.art(mkt, info, [mkt[start:end], shared])
            placed = effects.layout(art_fx, _free_from(file87, body.chain_start))
            if placed.end > body_build.TYPE_END or set(file87[placed.offset : placed.end]) != {0xFF}:
                raise BuildError(f"{move}: MKT effect {fx} art does not fit the fighter file")
            file87[placed.offset : placed.end] = placed.data
            spec = {"ticks_per_frame": max(1, info.ticks_per_frame * physics.HOST_HZ // physics.DONOR_HZ),
                    "reserve": mkt_effects.TRAIL_RESERVE if role == "trail" else mkt_effects.EFFECT_RESERVE}  # fmt: skip
            effect_art[fx] = (art_fx, placed, spec)
            report.setdefault("mkt_effects", []).append((move, role, fx, hex(placed.offset), len(placed.data)))
    # His MKT throw routine's own sounds on the host throw's three stages (Sektor's arm: out, throw,
    # in). MKT's grab voice (voice group 3, every fighter) is left out (owner, 2026-11-27: grab
    # sounds dropped for now; Rayden had no sound chain for his).
    throw_events: dict[str, tuple[int, ...]] = {}
    for stage, numbers in throw_sounds.read(mkt, donor_id).items():
        for n in numbers:
            if n not in fighter_sounds:
                fighter_sounds[n] = install(bank.event(bank.fighter_event(donor_id, n)))
        if numbers:
            throw_events[stage] = tuple(fighter_sounds[n] for n in numbers)
    if throw_events:
        report["throw_sounds"] = {k: list(v) for k, v in throw_events.items()}
    motions: dict[int, lower_special.Motion] = {}
    for move in order:  # sinking and rising jumps: their alias scripts in the fighter file's tail
        if any(s["op"] == "jump" and s.get("until") in ("below_screen", "surface") for s in steps_of[move]):
            start = _free_from(file87, body.chain_start)
            made, end_at = motion_scripts(file87, steps_of[move], animations,
                                          _int(d.specials.get(move, {}).get("donor_ticks", 1)), start)  # fmt: skip
            if end_at > body_build.TYPE_END:
                raise BuildError(f"{move}: motion scripts do not fit the fighter file")
            motions.update(made)
    if len(file87) != body_build.FILE87_SIZE:
        raise BuildError("the fighter file changed size")
    rom[body_build.FILE87_ROM : body_build.FILE87_ROM + len(file87)] = file87

    # ---- payload ---------------------------------------------------------------------------
    # Ice costs: the description's (owner decisions), else none for a movement ability (owner
    # rule, 2026-11-24), twice Ice Blast's for a grab (owner rule, 2026-11-26), else the replaced
    # Sub-Zero power's.
    moves = list(programs.values())  # SMRE's where it writes them
    movement = {mv.name for mv in moves if mv.movement}
    grabs = {mv.name for mv in moves if mv.grab}
    costs = {m: d.costs.get(m, lower_special.MOVEMENT_COST if m in movement
                            else lower_special.GRAB_COST if m in grabs else lower_special.COSTS[p])
             for m, p in d.commands.items() if p}  # fmt: skip
    report["costs"] = dict(costs)
    if len(order) > TRANSFER_ENTRIES_FREE:
        raise BuildError("more specials than free transfer-table entries")
    selectors = {m: FIRST_SELECTOR + k for k, m in enumerate(order)}
    custom_reactions: dict[str, int] = {}  # meaning -> reaction-table entry
    reaction_labels: dict[str, str] = {}  # meaning -> its routine's label
    emitted: set[str] = set()  # meanings whose routine is in the payload
    per_move = [m for m in order if d.specials.get(m, {}).get("limit") == "per_move"]
    shared_limit = [m for m in projectile_of if m not in per_move]
    a = Assembler(link_va + TABLE_RESERVE, cached_calls=True)
    group_of = {m: g for g in groups.values() for m in g.moves}
    stealth_moves = []
    for move in order:
        tune = d.specials.get(move, {})
        power = d.commands[move]
        steps = steps_of[move]
        host.emit_transfer_thunk(a, f"{move}_thunk", selectors[move])
        if power == "ice_blast":
            gate, default = lower_special.ICE_BLAST_GATE, lower_special.ICE_BLAST_STOCK_TIER
        else:
            gate, default = lower_special.GATES[power], None
        alive: tuple[str, ...] = ()
        if move in per_move:
            alive = (f"{move}_alive", *(f"{m}_alive" for m in shared_limit))
        refuse = (lower_special.CTRL_STEALTH, lower_special.STEALTH_BIT) if "stealth" in tune else None
        relocates = any(s["op"] == "relocate" for s in _all_steps(steps))
        held_cond = next((c for c in programs[move].command.get("conditions", []) if c["kind"] == "held_for"), None)
        held = None
        if held_cond is not None:  # MKT ticks_since on the press stamp: the clock runs at MKT's rate
            held = ("hold_hp_stamp", _int(held_cond["ticks"]))
        lower_special.emit_gate_condition(a, f"{move}_cond", gate, costs[move], default=default,
                                          cooldown=(f"{move}_cooldown", cooldown_of[move]) if move in cooldown_of else None,
                                          target_range=lower_special.RELOCATE_RANGE if relocates else None,
                                          held=held,
                                          alive=alive, refuse_if=refuse,
                                          airborne=bool(tune.get("airborne") or tune.get("air_start")))  # fmt: skip
        g = group_of.get(move)
        meanings = {s["strike"]["reaction"] for s in _all_steps(steps) if s["op"] == "strike"}
        reaction_map = {}
        for meaning in meanings - set(lower_special.STOCK_REACTIONS):
            if meaning not in custom_reactions:
                custom_reactions[meaning] = reactions.take()
            reaction_map[meaning] = custom_reactions[meaning]
            spec = lower_special.VICTIM_REACTIONS.get(meaning)
            if spec is not None:  # its routine: named by the first move that uses it
                reaction_labels.setdefault(meaning, f"{move}_{spec.suffix}")
        words = [f"{reaction_labels[m]}_word" for m in sorted(reaction_map)
                 if m in lower_special.VICTIM_REACTIONS and lower_special.VICTIM_REACTIONS[m].word]  # fmt: skip
        foot = None
        if move in footsteps:
            slot = next(_int(s["anim"]["slot"]) for s in _all_steps(steps)
                        if s["op"] == "animate" and s.get("until") == "manual" and _int(s["anim"]["table"]) == 0)  # fmt: skip
            foot = {(0, slot): lower_special.Footsteps(*lower_special.donor_footsteps(donor, slot), footsteps[move])}
        fx_map = {fx: (f"fx_{fx}", _int(spec.get("dy_px", 0)) * lp.UNITS_PER_PX)
                  for fx, (_, _, spec) in effect_art.items()}  # fmt: skip
        for s in _all_steps(steps):  # a pose offset past its script shows another script's frame
            if s["op"] == "pose" and "offset" in s["anim"]:
                key = (_int(s["anim"]["table"]), _int(s["anim"]["slot"]))
                if key in script_words and _int(s["anim"]["offset"]) >= script_words[key]:
                    raise BuildError(f"{move}: pose offset {s['anim']['offset']} is past the "
                                     f"{script_words[key]} words of script {key}")  # fmt: skip
        records = lower_special.emit_action(
            a, f"{move}_root", steps, cost=costs[move], animations=animations,
            child=f"{move}_ball" if g else None, helper=g.helper if g else None,
            sounds=fighter_sounds, face=tune.get("face"), donor_ticks=_int(tune.get("donor_ticks", 1)),
            reactions=reaction_map,
            speed=lambda v: physics.fold_donor_speeds(v, v, lambda x: x, lp.UNITS_PER_PX)[0],
            footsteps=foot, stealth=f"{move}_stealth" if "stealth" in tune else None,
            effects=fx_map or None,
            carry=words[0] if words else None,
            skip=frozenset(tune.get("skip", ())),  # owner: steps left out (Rayden's torpedo turns)
            air_control=bool(tune.get("air_control")),  # owner: steer the closing drop
            cooldown=f"{move}_cooldown" if move in cooldown_of else None,
            afterimage=afterimage_of[move][0] if move in afterimage_of else None,
            motions=motions or None,
            air_start=bool(tune.get("air_start")),  # MKT's command has no ground check (Sektor's teleport)
            primary_scripts={k: int.from_bytes(file87[4 * k : 4 * k + 4], "big") for k in d.body.slots},
        )  # fmt: skip
        if g is not None:
            ptune = tune.get("projectile", {})
            low = lp.lower(projectile_of[move], g.art, g.events, g.reaction_slot, clean)
            low = dataclasses.replace(low, impact_flip=bool(ptune.get("impact_flip", True)),
                                      impact_keep_y=bool(ptune.get("impact_keep_y", True)),
                                      impact_at_hit=bool(ptune.get("impact_at_hit", True)))  # fmt: skip
            if (move, "trail") in fx_info:  # MKT rocket_smoke: one puff every other donor tick
                info, every = fx_info[(move, "trail")], _int(projectile_of[move]["trail"]["every"])
                if every * physics.HOST_HZ != physics.DONOR_HZ or info.dy:
                    raise BuildError(f"{move}: a trail every {every} donor ticks, {info.dy} px up, is not lowered")
                low = dataclasses.replace(low, trail=f"fx_{info.fx}", trail_dx=info.dx * lp.UNITS_PER_PX,
                                          trail_front=info.front)  # fmt: skip
            if "offset_px" not in ptune:  # MKT's own spawn offset: drawn as the stock token draws
                low = dataclasses.replace(low, owner_draw=True, render_position=True)
            if (move, "impact") in fx_info:  # at the projectile (MKT rocket_explode_fx)
                info = fx_info[(move, "impact")]
                low = dataclasses.replace(low, impact_effect=f"fx_{info.fx}", impact_effect_front=info.front)
            if "impact_toward_px" in ptune:  # owner: the impact nearer the attacker (facing him)
                low = dataclasses.replace(low, impact_dx=low.impact_dx
                                          + _int(ptune["impact_toward_px"]) * lp.UNITS_PER_PX)  # fmt: skip
            g.lowered = low
            lp.emit_process(a, low, child=f"{move}_ball", prefix=f"{move}_", data=f"g{_gid(g)}_",
                            alive=f"{move}_alive")  # fmt: skip
            if move == g.moves[-1] and g.helper is not None and g.first:  # once per art
                throw = next(s for s in steps if s["op"] == "animate")
                body_slot = animations[(_int(throw["anim"]["table"]), _int(throw["anim"]["slot"]))]
                dy = low.dy + HELPER_DY_PX * lp.UNITS_PER_PX
                if isinstance(body_slot, tuple):
                    lp.emit_helper(a, g.art, 0, dy, g.helper, None, body_at=body_slot[1])
                else:
                    lp.emit_helper(a, g.art, 0, dy, g.helper, body_slot)
        ctx = lower_special.ReactionContext(tune, _int(tune.get("donor_ticks", 1)), clean)
        for meaning in sorted(set(reaction_map) - emitted):
            spec = lower_special.VICTIM_REACTIONS.get(meaning)
            if spec is not None:
                spec.emit(a, reaction_labels[meaning], ctx)
                emitted.add(meaning)
        unknown = set(reaction_map) - set(reaction_labels)
        if unknown:
            raise BuildError(f"{move}: no host routine for reactions {sorted(unknown)}")
        if move in afterimage_of:
            label, art, ticks = afterimage_of[move]
            lp.emit_afterimage_process(a, label, art, ticks)
        if move in cooldown_of:  # its clock stamp (the move's ``stamp`` step writes it)
            while a.pc() & 3:
                a.nop()
            a.label(f"{move}_cooldown")
            a.raw(0)
        if relocates and "relocate" not in a.labels:
            lower_special.emit_relocate_routine(a)
        if "stealth" in tune:
            stealth_moves.append(move)
            lower_special.emit_stealth_timer(a, f"{move}_stealth", _int(tune["stealth"]["period"]),
                                             _int(tune["stealth"]["drain"]))  # fmt: skip
        if records:
            report.setdefault("strike_records", []).append((move, records))
    if effect_art:
        effects.emit_spawn(a)
        effects.emit_process(a, render_position=bool(fx_info))  # (Reptile's fire: as accepted)
        while a.pc() & 3:
            a.nop()
        for fx, (art_fx, placed, spec) in effect_art.items():
            effects.emit_descriptor(a, f"fx_{fx}", placed, art_fx, _int(spec["ticks_per_frame"]),
                                    _int(spec["reserve"]))  # fmt: skip
    host.emit_sound_player(a)
    throw_hooks = throw_sounds.emit_hooks(a, throw_events)
    for g in groups.values():
        if g.helper is not None and g.first:
            lp.emit_helper_data(a, g.helper)
    for m in projectile_of:
        a.label(f"{m}_alive")
        a.raw(0)
    for g in groups.values():
        lp.emit_data(a, g.lowered, link_va, clean, data=f"g{_gid(g)}_")  # type: ignore[arg-type]
    for _, records in report.get("strike_records", []):
        lower_special.emit_strike_data(a, records, link_va)
    if any(programs[m].command.get("release") for m in order):
        while a.pc() & 3:
            a.nop()
        a.label("hold_hp_stamp")  # the High Punch press, clock + 1 (commands' press wrapper)
        a.raw(0)
    main = a.link()
    # Transfer mode 0 refuses an airborne start, mode 1 does not (Wiki Player-Actions "Descriptor
    # selector and condition"): moves tuned "airborne" (Rayden's torpedo) take mode 1.
    overrides = {m: (1 if d.specials.get(m, {}).get("airborne") or d.specials.get(m, {}).get("air_start") else 0,
                     a.labels[f"{m}_cond"], a.labels[f"{m}_thunk"])
                 for m in order}  # fmt: skip
    cmds = commands.donor_commands(mkt, moves, d.commands)
    stub_base = (link_va + TABLE_RESERVE + len(main) + 0xF) & ~0xF
    low_cmd = commands.lower(clean, cmds, set(d.remove_commands), link_va, stub_base, overrides,
                             hold_word=a.labels.get("hold_hp_stamp"))  # fmt: skip
    if any(v + commands.RECORD * len(low_cmd.tables[k]) + 4 > link_va + TABLE_RESERVE
           for k, v in low_cmd.moved.items()):  # fmt: skip
        raise BuildError("moved command tables do not fit their reserve")
    end = stub_base - link_va + len(low_cmd.stubs)
    # Combo option lists past the host graph (Sektor's seventh record) follow the stubs.
    combo_at = (end + 0xF) & ~0xF
    combos_low = combos.lower(combo_graph, *_combo_slot(d), set(d.body.slots),
                              overflow_va=link_va + combo_at)  # fmt: skip
    combos.install(rom, combos_low)
    if combos_low.overflow:
        end = combo_at + len(combos_low.overflow)
    if end > PAYLOAD_LIMIT:
        raise BuildError(f"payload 0x{end:X} > 0x{PAYLOAD_LIMIT:X}")
    payload = bytearray(end)
    payload[TABLE_RESERVE : TABLE_RESERVE + len(main)] = main
    payload[stub_base - link_va : stub_base - link_va + len(low_cmd.stubs)] = low_cmd.stubs
    payload[combo_at : combo_at + len(combos_low.overflow)] = combos_low.overflow
    rom[SCRATCH_ROM : SCRATCH_ROM + end] = payload
    commands.install(rom, clean, low_cmd, SCRATCH_ROM, link_va, indirect=indirect)
    payload = bytearray(rom[SCRATCH_ROM : SCRATCH_ROM + end])  # with the moved tables

    # ---- stock words into the payload --------------------------------------------------------
    _guarded(rom, TRANSFER_BOUND_ROM, TRANSFER_BOUND_STOCK, TRANSFER_BOUND_STOCK - 3 + FIRST_SELECTOR + len(order))
    for m in order:
        _guarded(rom, host.TRANSFER_TABLE - VA_TO_ROM + 4 * selectors[m], 0, a.labels[f"{m}_root"])
    for stage, label in throw_hooks.items():  # the stock jal enters the payload's KSEG0 alias
        site, stock, _, _ = throw_sounds.SITES[stage]
        _guarded(rom, site - VA_TO_ROM, stock, 0x0C000000 | ((a.labels[label] >> 2) & 0x03FFFFFF))
    for g in groups.values():
        reaction_label = f"g{_gid(g)}_reaction"
        if reaction_label not in a.labels:  # a stock (host-kind) reaction
            continue
        _guarded(rom, lp.REACTION_TABLE - VA_TO_ROM + 4 * g.reaction_slot, lp.DUMMY_REACTION,
                 a.labels[reaction_label])  # fmt: skip
    for meaning, slot in custom_reactions.items():
        _guarded(rom, lp.REACTION_TABLE - VA_TO_ROM + 4 * slot, lp.DUMMY_REACTION,
                 a.labels[reaction_labels[meaning]])  # fmt: skip
    if groups:
        _guarded(rom, lp.TYPE_FILE_TABLE - VA_TO_ROM + 4 * lp.PLAYER_TYPE, 0, lp.PLAYER_FILE_BASE)

    report.update(chain_start=body.chain_start,
                  chains_used=voice_chains + chains.items[: chains.used])  # fmt: skip
    report.update(payload_end=end, voices=vs.category, combos=combos_low.strings,
                  commands=low_cmd.report, samples_end=samples_end)  # fmt: skip
    return Built(
        bytes(rom), bytes(payload), link_va, bytes(file87), (SAMPLE_ROM, samples_end), dict(low_cmd.moved),
        selectors, dict(custom_reactions) | {_report_key(g, groups): g.reaction_slot for g in groups.values()},
        {f"fighter sound {n}": e for n, e in fighter_sounds.items()}, report,
    )  # fmt: skip


def _gid(g: _Group) -> str:
    return f"{g.key[0]}_{g.key[1]}_{g.key[2]}" + ("" if g.first else f"_{g.reaction}")


def _report_key(g: _Group, groups: dict) -> str:
    return f"projectile {g.key}" + ("" if g.first else f" {g.reaction}")


def _combo_slot(d: fd.FighterDescription) -> tuple[int | None]:
    table, index = d.body.sources.get(combos.COMBO_SLOT, (0, combos.COMBO_SLOT))
    return (index if table == 1 else None,)


def _projectile_effects(step: dict[str, Any] | None) -> list[tuple[str, dict[str, Any]]]:
    """("trail" | "impact", effect) a projectile step starts that the backend lowers: its trail,
    and its impact when the impact is that effect (``end: effect``, Sektor's explosion). An
    effect beside an impact animation (Reptile's acid droplets, ``create_fx(0x2F)``) is not
    lowered yet (:func:`_unlowered_effects`)."""

    if step is None:
        return []
    impact = step.get("impact", {})
    found = [("trail", step.get("trail", {}).get("effect")),
             ("impact", impact.get("effect") if impact.get("end") == "effect" else None)]  # fmt: skip
    return [(role, eff) for role, eff in found if eff is not None]


def _unlowered_effects(step: dict[str, Any] | None) -> list[int]:
    impact = (step or {}).get("impact", {})
    return [_int(impact["effect"]["mkt_fx"])] if "effect" in impact and impact.get("end") != "effect" else []


def _projectile_rates(step: dict[str, Any], ticks_per: int) -> dict[str, Any]:
    """A projectile step with its flight and impact frame rates in host ticks (rounded up)."""

    out = dict(step, rate=max(1, -(-_int(step["rate"]) // ticks_per)))
    if "impact" in step and "rate" in step["impact"]:
        out["impact"] = dict(step["impact"], rate=max(1, -(-_int(step["impact"]["rate"]) // ticks_per)))
    if "wrap" in step:
        out["wrap"] = {"cooldown": max(1, -(-_int(step["wrap"]["cooldown"]) // ticks_per))}
    return out


def _without_sounds(steps: list[dict[str, Any]], numbers: set[int]) -> list[dict[str, Any]]:
    """The steps without the sound steps of ``numbers`` (sounds the importer cannot port yet)."""

    out = []
    for s in steps:
        if s["op"] == "sound" and _int(s["sound"].get("fighter", -1)) in numbers and "random" not in s["sound"]:
            continue
        s = dict(s)
        for key in ("steps", "every_tick", "on_hit", "on_block"):
            if key in s:
                s[key] = _without_sounds(s[key], numbers)
        out.append(s)
    return out


def _all_steps(steps: list[dict[str, Any]]):
    for s in steps:
        yield s
        for key in ("steps", "every_tick", "on_hit", "on_block"):
            yield from _all_steps(s.get(key, []))


# ---- production packaging (Sektor's accepted "option C" layout, made generic) ------------------
OUTPUT_SIZE = 0x02000000
TAIL = (0x01820000, 0x01880000)  # generated-output region for the fighter file and samples (Memory map)
FIXED_VA = 0xA01B30F0  # production pool tail after the Inventory legend (in shared file 0x1A)
POOL_END = 0x801B3420
RAW_LOADER, FILE_87 = 0x80065D64, 0x87
FILE_TABLE_ROM = 0xA5010
LINK_DELTAS = (0x12340, 0x24690)  # two more links (16-aligned: the payload aligns records)


@dataclass
class Production:
    rom: bytes  # 32 MiB image: the fighter's changes on the clean ROM, in production placement
    fixed: bytes  # fixed loader, linked at ``fixed_va`` (goes into shared file 0x1A)
    manifest: dict[str, Any]


def production(clean: bytes, mkt: bytes, name: str, *, fixed_va: int = FIXED_VA) -> Production:
    """The fighter in production placement (Sektor builds v48-v50, generic):

    * the payload is a relocatable blob, with its relocation table, in the free body tail of
      the fighter file (no RDRAM reservation); a fixed loader in shared file 0x1A wraps the 15
      stock file-0x87 loads, relocates the blob and refreshes every stock word that points
      into it. A moved command table is read through a pointer word in the fixed part
      (``commands.install(indirect=...)``);
    * the fighter file and the donor samples move to the generated-output tail :data:`TAIL`;
      Sub-Zero's stock file, the proof scratch and the intermediate samples stay clean.
    """

    from ..patches.rainbow_palette import EXPECTED_RAW_LOADER_JAL, LOAD_JAL_SITES
    from . import relocate

    probe = build(clean, mkt, name)
    buttons = sorted(probe.moved_tables)
    fixed_k1 = fixed_va | 0x20000000
    slots = {b: fixed_k1 + 4 * k for k, b in enumerate(buttons)}
    links = {dlt: build(clean, mkt, name, link_va=LINK_VA + dlt, indirect=slots) for dlt in (0, *LINK_DELTAS)}
    base = links[0]
    n = len(base.payload)
    relocs = relocate.find(base.payload, links[LINK_DELTAS[0]].payload, LINK_DELTAS[0])
    for dlt in LINK_DELTAS:
        if relocate.apply(base.payload, relocs, dlt) != links[dlt].payload:
            raise BuildError(f"relocation model does not reproduce the link at +0x{dlt:X}")
    refs: list[relocate.StockRef] = []
    jal_sites: dict[int, int] = {}
    scratch = (SCRATCH_ROM, SCRATCH_ROM + PAYLOAD_LIMIT)
    for off in range(0, len(clean), 4):
        if scratch[0] <= off < scratch[1] or off in (0x10, 0x14):
            continue
        wa = int.from_bytes(base.rom[off : off + 4], "big")
        moved = [int.from_bytes(links[dlt].rom[off : off + 4], "big") for dlt in LINK_DELTAS]
        if all(w == wa for w in moved):
            continue
        if off >= 0x00100000:
            raise BuildError(f"payload reference outside the main segment at ROM 0x{off:X}")
        va = off + VA_TO_ROM
        if all((w - wa) & 0xFFFFFFFF == dlt for w, dlt in zip(moved, LINK_DELTAS, strict=True)):
            refs.append(relocate.StockRef(va, (wa | 0x20000000) - LINK_VA, kseg0=not (wa >> 29) & 1))
        elif wa >> 26 == 3 and all(w >> 26 == 3 and (w - wa) & 0x03FFFFFF == dlt >> 2
                                   for w, dlt in zip(moved, LINK_DELTAS, strict=True)):  # fmt: skip
            jal_sites[off] = (((wa & 0x03FFFFFF) << 2) | 0xA0000000) - LINK_VA
        else:
            raise BuildError(f"unclassified payload reference at ROM 0x{off:X}")
    for b in buttons:
        refs.append(relocate.StockRef(slots[b], base.moved_tables[b] - LINK_VA))

    # Blob and relocation table in the fighter file's free body tail.
    file87 = bytearray(base.file87)
    table = relocate.encode(relocs)
    blob_off = _free_from(file87, base.report["chain_start"])
    if blob_off + n + len(table) > body_build.TYPE_END:
        # The body tail is taken (Rayden: his move art): append the blob to the file, inside the
        # file-size budget the runtime-confirmed placement allowed (body_build.SAFE_END).
        blob_off = (len(file87) + 0xF) & ~0xF
        file87 += b"\xff" * (blob_off + n + len(table) - len(file87))
        if len(file87) >= body_build.SAFE_END:
            raise BuildError(f"payload blob (0x{n:X} + table 0x{len(table):X}) does not fit the fighter file budget")
    table_off = blob_off + n
    blob_end = table_off + len(table)
    if set(file87[blob_off:blob_end]) != {0xFF}:
        raise BuildError(f"payload blob (0x{n:X} + table 0x{len(table):X}) does not fit the fighter file")
    file87[blob_off:table_off] = base.payload
    file87[table_off:blob_end] = table

    # Fixed part: the table pointer words, then the loader wrapper, relocator, trampolines, refs.
    a = Assembler(fixed_va, cached_calls=True)
    for _ in buttons:
        a.raw(0)
    tramp = relocate.emit_fixed(a, RAW_LOADER, FILE_87, LINK_VA, blob_off, table_off, refs,
                                sorted(set(jal_sites.values())))  # fmt: skip
    fixed = a.link()
    if (fixed_va & ~0x20000000) + len(fixed) > POOL_END:
        raise BuildError(f"fixed loader (0x{len(fixed):X} bytes) does not fit the pool tail")
    load_wrapper = a.labels["rel_load"] & ~0x20000000

    # 32 MiB image: the fighter's changes, placed as in production.
    image = bytearray(base.rom) + b"\xff" * (OUTPUT_SIZE - len(base.rom))
    image[scratch[0] : scratch[1]] = clean[scratch[0] : scratch[1]]
    stock87 = (body_build.FILE87_ROM, body_build.FILE87_ROM + body_build.FILE87_SIZE)
    image[stock87[0] : stock87[1]] = clean[stock87[0] : stock87[1]]
    s0, s1 = base.samples
    samples = bytes(image[s0:s1])
    image[s0:s1] = clean[s0:s1]
    f87_rom = TAIL[0]
    samples_rom = (f87_rom + len(file87) + 0xFFF) & ~0xFFF
    if samples_rom + len(samples) > TAIL[1]:
        raise BuildError("fighter file and samples do not fit the tail region")
    image[f87_rom : f87_rom + len(file87)] = file87
    image[samples_rom : samples_rom + len(samples)] = samples
    entry = FILE_TABLE_ROM + FILE_87 * 12
    if (int.from_bytes(image[entry : entry + 4], "big"), int.from_bytes(image[entry + 4 : entry + 8], "big")) != stock87:
        raise BuildError("file 0x87 entry is not stock")
    _put32(image, entry, f87_rom)
    _put32(image, entry + 4, f87_rom + len(file87))
    shift = samples_rom - s0
    for chain in base.report["chains_used"]:
        w = sound.MSZ_WAVES + chain.wave * 24
        o = int.from_bytes(image[w : w + 4], "big")
        if not s0 <= sound.MSZ_TBL + o < s1:
            raise BuildError(f"chain {chain.event}: sample outside the moved block")
        _put32(image, w, o + shift)
        dfn = sound.MSZ_EVENT_DEFS + chain.event * 16 + 8  # a multi-track event's tracks move too
        o = int.from_bytes(image[dfn : dfn + 4], "big")
        if s0 <= sound.MSZ_TRACKS + o < s1:
            _put32(image, dfn, o + shift)
    for site in LOAD_JAL_SITES:
        _guarded(image, site, EXPECTED_RAW_LOADER_JAL, 0x0C000000 | ((load_wrapper >> 2) & 0x03FFFFFF))
    for off, boff in jal_sites.items():
        _put32(image, off, 0x0C000000 | (((a.labels[tramp[boff]] & ~0x20000000) >> 2) & 0x03FFFFFF))
    manifest = {
        "fighter": name, "fixed_va": fixed_va, "fixed_len": len(fixed), "load_wrapper": load_wrapper,
        "blob_off": blob_off, "table_off": table_off, "blob_end": blob_end, "relocs": len(relocs),
        "refs": [[r.address, r.offset, r.kseg0] for r in refs], "jal_sites": {hex(o): b for o, b in jal_sites.items()},
        "file87_rom": f87_rom, "file87_size": len(file87), "samples_rom": samples_rom,
        "samples_end": samples_rom + len(samples), "tail": TAIL, "slack": body_build.TYPE_END - blob_end,
    }  # fmt: skip
    return Production(bytes(image), fixed, manifest)
