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
    physics,
    sound,
    voices,
)
from . import description as fd
from . import lower_projectile as lp
from .mips import Assembler
from .mkt_fighter import validate_mkt_n64_rev2

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
# Wiki Memory-and-Allocation-Map): 0x2B, 0x23, then byte 0x4C past the 64 reactions.
REACTION_POOL = (0x2B, 0x23, 0x4C)
VOICE_CHAINS = sound.ISOLATED_CHAINS[:10]
EXTRA_CHAINS = sound.ISOLATED_CHAINS[10:]
HELPER_DY_PX = -2  # throw helper above its projectile (owner fine-tune, specials proofs v09/v11)


class BuildError(ValueError):
    pass


def _int(v: Any) -> int:
    return int(v, 0) if isinstance(v, str) else int(v)


def _put32(rom: bytearray, off: int, word: int) -> None:
    rom[off : off + 4] = (word & 0xFFFFFFFF).to_bytes(4, "big")


def _guarded(rom: bytearray, off: int, old: int, new: int) -> None:
    if int.from_bytes(rom[off : off + 4], "big") != old:
        raise BuildError(f"ROM 0x{off:X} is not 0x{old:08X}")
    _put32(rom, off, new)


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
    """A projectile art shared by the moves whose projectile step has the same donor art."""

    key: tuple[int, int, int]
    moves: list[str]
    art: lp.ArtLayout
    events: dict[str, int]
    reaction_slot: int
    helper: str | None
    lowered: lp.Lowered | None = None


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
    moves, _ = components.load_programs(name)
    programs = {m.name: m for m in moves}
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
    combos_low = combos.lower(combos.donor_graph(mkt, donor_id),
                              *_combo_slot(d), set(d.body.slots))  # fmt: skip
    combos.install(rom, combos_low)
    vs, samples_end = voices.install(rom, clean, mkt, donor_id, VOICE_CHAINS, SAMPLE_ROM)
    used_voices = len(set(vs.category.values()) - {None})
    chains = _Pool(tuple(EXTRA_CHAINS) + tuple(VOICE_CHAINS[used_voices:]), "isolated sound chains")
    voice_chains = list(VOICE_CHAINS[:used_voices])
    bank = sound.MktSoundBank(mkt)
    if d.body.script_sounds:  # body.script_sounds: the spare descriptor's event plays it
        (sfx,) = set(d.body.script_sounds.values())
        samples_end = voices.install_script_sound(rom, clean, mkt, donor_id, sfx, chains.take(),
                                                  (samples_end + 0xF) & ~0xF, vs)  # fmt: skip

    def install(donor_sound: sound.DonorSound) -> int:
        nonlocal samples_end
        chain = chains.take()
        samples_end = sound.install(rom, clean, donor_sound, chain, (samples_end + 0xF) & ~0xF)
        return chain.event

    animations: dict[tuple[int, int], int | tuple[str, int]] = {}
    for key, (t, i, _) in d.body.secondary_scripts.items():
        animations[(t, i)] = key if key < body_build.VIRTUAL_SCRIPT else ("at", body.script_offsets[key])
    animations[(0, d.body.run_slot)] = ("at", body_build.RUN_TARGET)

    # ---- projectile groups and art (fighter-file tail) -------------------------------------
    reactions = _Pool(REACTION_POOL, "spare reaction-table entries")
    groups: dict[tuple[int, int, int], _Group] = {}
    steps_of: dict[str, list[dict[str, Any]]] = {}
    projectile_of: dict[str, dict[str, Any]] = {}
    placed_at = body.chain_start
    fighter_sounds: dict[int, int] = {}
    footsteps: dict[str, tuple[int, ...]] = {}
    effect_art: dict[int, tuple[effects.EffectArt, effects.EffectLayout, dict[str, Any]]] = {}
    report: dict[str, Any] = {"body": body.report}
    for move in order:
        tune = d.specials.get(move, {})
        steps = list(programs[move].steps)
        if "sleep_ticks" in tune:  # owner: a different recovery (Acid Spit, specials proof v11)
            steps = [dict(s, ticks=_int(tune["sleep_ticks"])) if s["op"] == "sleep" else s for s in steps]
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
            gkey = (_int(anim["table"]), _int(anim["slot"]), _int(anim.get("part", 1)))
            if gkey in groups:
                groups[gkey].moves.append(move)
            else:
                throw = next(s for s in steps if s["op"] == "animate")
                helper = lp.donor_helper(donor, throw["anim"])
                slots = tuple(_int(v) for v in ptune["art_slots"]) if "art_slots" in ptune else None
                at = placed_at if slots is not None else _free_from(file87, body.chain_start)
                art = lp.place_art(file87, mkt, donor_id, proj, slots, body_build.TYPE_END, at=at,
                                   helper=helper,
                                   helper_slot=_int(ptune["helper_slot"]) if "helper_slot" in ptune else None,
                                   throw_rate=int(throw["rate"]))  # fmt: skip
                needed = len(lp.projectile_sounds(proj))
                events, samples_end = lp.install_sounds(
                    rom, clean, mkt, donor_id, proj, tuple(chains.take() for _ in range(needed)),
                    (samples_end + 0xF) & ~0xF,
                )  # fmt: skip
                stock = lp.host_reaction(proj["strike"]["reaction"])
                groups[gkey] = _Group(gkey, [move], art, events, stock if stock is not None else reactions.take(),
                                      f"{move}_helper" if helper is not None else None)  # fmt: skip
        for s in steps:
            if s["op"] == "sound":
                n = _int(s["sound"]["fighter"])
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
    if len(file87) != body_build.FILE87_SIZE:
        raise BuildError("the fighter file changed size")
    rom[body_build.FILE87_ROM : body_build.FILE87_ROM + len(file87)] = file87

    # ---- payload ---------------------------------------------------------------------------
    costs = {m: d.costs.get(m, lower_special.COSTS[p]) for m, p in d.commands.items() if p}
    if len(order) > TRANSFER_ENTRIES_FREE:
        raise BuildError("more specials than free transfer-table entries")
    selectors = {m: FIRST_SELECTOR + k for k, m in enumerate(order)}
    custom_reactions: dict[str, int] = {}  # meaning -> reaction-table entry
    reaction_labels: dict[str, str] = {}  # meaning -> its routine's label
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
        lower_special.emit_gate_condition(a, f"{move}_cond", gate, costs[move], default=default,
                                          alive=alive, refuse_if=refuse)  # fmt: skip
        g = group_of.get(move)
        meanings = {s["strike"]["reaction"] for s in _all_steps(steps) if s["op"] == "strike"}
        reaction_map = {}
        for meaning in meanings - set(lower_special.STOCK_REACTIONS):
            if meaning not in custom_reactions:
                custom_reactions[meaning] = reactions.take()
            reaction_map[meaning] = custom_reactions[meaning]
        foot = None
        if move in footsteps:
            slot = next(_int(s["anim"]["slot"]) for s in _all_steps(steps)
                        if s["op"] == "animate" and s.get("until") == "manual" and _int(s["anim"]["table"]) == 0)  # fmt: skip
            foot = {(0, slot): lower_special.Footsteps(*lower_special.donor_footsteps(donor, slot), footsteps[move])}
        fx_map = {fx: (f"fx_{fx}", _int(spec.get("dy_px", 0)) * lp.UNITS_PER_PX)
                  for fx, (_, _, spec) in effect_art.items()}  # fmt: skip
        records = lower_special.emit_action(
            a, f"{move}_root", steps, cost=costs[move], animations=animations,
            child=f"{move}_ball" if g else None, helper=g.helper if g else None,
            sounds=fighter_sounds, face=tune.get("face"), donor_ticks=_int(tune.get("donor_ticks", 1)),
            reactions=reaction_map,
            speed=lambda v: physics.fold_donor_speeds(v, v, lambda x: x, lp.UNITS_PER_PX)[0],
            footsteps=foot, stealth=f"{move}_stealth" if "stealth" in tune else None,
            effects=fx_map or None,
        )  # fmt: skip
        if g is not None:
            ptune = tune.get("projectile", {})
            low = lp.lower(projectile_of[move], g.art, g.events, g.reaction_slot, clean)
            if "impact_flip" in ptune or "impact_keep_y" in ptune:
                low = dataclasses.replace(low, impact_flip=bool(ptune.get("impact_flip", True)),
                                          impact_keep_y=bool(ptune.get("impact_keep_y", False)))  # fmt: skip
            g.lowered = low
            lp.emit_process(a, low, child=f"{move}_ball", prefix=f"{move}_", data=f"g{_gid(g)}_",
                            alive=f"{move}_alive")  # fmt: skip
            if move == g.moves[-1] and g.helper is not None:
                throw = next(s for s in steps if s["op"] == "animate")
                body_slot = animations[(_int(throw["anim"]["table"]), _int(throw["anim"]["slot"]))]
                dy = low.dy + HELPER_DY_PX * lp.UNITS_PER_PX
                if isinstance(body_slot, tuple):
                    lp.emit_helper(a, g.art, 0, dy, g.helper, None, body_at=body_slot[1])
                else:
                    lp.emit_helper(a, g.art, 0, dy, g.helper, body_slot)
        if "elbow_hold" in reaction_map and "elbow_hold" not in reaction_labels:
            reaction_labels["elbow_hold"] = f"{move}_hold"
            lower_special.emit_hold_reaction(a, f"{move}_hold", _int(tune.get("donor_ticks", 1)))
        unknown = set(reaction_map) - set(reaction_labels)
        if unknown:
            raise BuildError(f"{move}: no host routine for reactions {sorted(unknown)}")
        if "stealth" in tune:
            stealth_moves.append(move)
            lower_special.emit_stealth_timer(a, f"{move}_stealth", _int(tune["stealth"]["period"]),
                                             _int(tune["stealth"]["drain"]))  # fmt: skip
        if records:
            report.setdefault("strike_records", []).append((move, records))
    if effect_art:
        effects.emit_spawn(a)
        effects.emit_process(a)
        while a.pc() & 3:
            a.nop()
        for fx, (art_fx, placed, spec) in effect_art.items():
            effects.emit_descriptor(a, f"fx_{fx}", placed, art_fx, _int(spec["ticks_per_frame"]),
                                    _int(spec["reserve"]))  # fmt: skip
    host.emit_sound_player(a)
    for g in groups.values():
        if g.helper is not None:
            lp.emit_helper_data(a, g.helper)
    for m in projectile_of:
        a.label(f"{m}_alive")
        a.raw(0)
    for g in groups.values():
        lp.emit_data(a, g.lowered, link_va, clean, data=f"g{_gid(g)}_")  # type: ignore[arg-type]
    for _, records in report.get("strike_records", []):
        lower_special.emit_strike_data(a, records, link_va)
    main = a.link()
    overrides = {m: (0, a.labels[f"{m}_cond"], a.labels[f"{m}_thunk"]) for m in order}
    cmds = commands.donor_commands(mkt, moves, d.commands)
    stub_base = (link_va + TABLE_RESERVE + len(main) + 0xF) & ~0xF
    low_cmd = commands.lower(clean, cmds, set(d.remove_commands), link_va, stub_base, overrides)
    if any(v + commands.RECORD * 5 + 4 > link_va + TABLE_RESERVE for v in low_cmd.moved.values()):
        raise BuildError("moved command tables do not fit their reserve")
    end = stub_base - link_va + len(low_cmd.stubs)
    if end > PAYLOAD_LIMIT:
        raise BuildError(f"payload 0x{end:X} > 0x{PAYLOAD_LIMIT:X}")
    payload = bytearray(end)
    payload[TABLE_RESERVE : TABLE_RESERVE + len(main)] = main
    payload[stub_base - link_va : end] = low_cmd.stubs
    rom[SCRATCH_ROM : SCRATCH_ROM + end] = payload
    commands.install(rom, clean, low_cmd, SCRATCH_ROM, link_va, indirect=indirect)
    payload = bytearray(rom[SCRATCH_ROM : SCRATCH_ROM + end])  # with the moved tables

    # ---- stock words into the payload --------------------------------------------------------
    _guarded(rom, TRANSFER_BOUND_ROM, TRANSFER_BOUND_STOCK, TRANSFER_BOUND_STOCK - 3 + FIRST_SELECTOR + len(order))
    for m in order:
        _guarded(rom, host.TRANSFER_TABLE - VA_TO_ROM + 4 * selectors[m], 0, a.labels[f"{m}_root"])
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
        selectors, dict(custom_reactions) | {f"projectile {g.key}": g.reaction_slot for g in groups.values()},
        {f"fighter sound {n}": e for n, e in fighter_sounds.items()}, report,
    )  # fmt: skip


def _gid(g: _Group) -> str:
    return f"{g.key[0]}_{g.key[1]}_{g.key[2]}"


def _combo_slot(d: fd.FighterDescription) -> tuple[int | None]:
    table, index = d.body.sources.get(combos.COMBO_SLOT, (0, combos.COMBO_SLOT))
    return (index if table == 1 else None,)


def _all_steps(steps: list[dict[str, Any]]):
    for s in steps:
        yield s
        for key in ("steps", "every_tick", "on_hit", "on_block"):
            yield from _all_steps(s.get(key, []))


# ---- production packaging (Sektor's accepted "option C" layout, made generic) ------------------
OUTPUT_SIZE = 0x02000000
TAIL = (0x01820000, 0x0186E4C0)  # generated-output region for the fighter file and samples
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
    table_off = blob_off + n
    blob_end = table_off + len(table)
    if blob_end > body_build.TYPE_END or set(file87[blob_off:blob_end]) != {0xFF}:
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
