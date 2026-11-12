"""Reptile specials proof v17 (Fighter recompiler plan, milestone 4 step 3.3). Disposable.

Specials proof v16 (Reverse Elbow: "almost perfect", owner) with its two details fixed:

* **No blood while passing through:** the hold no longer starts the stock hit effect
  (``0x800504C4``, the first call of the stock hit reaction it is modelled on).
* **Footsteps:** MKT's Run plays callback 8 (``0x8000518C``: a random one of sound group
  ``0x800A1A3C``, events 0x90-0x93) before frames 3 and 7 of its 9 (``donor_footsteps``). The
  dash plays MKT events 0x90 and 0x91, alternately, at those frames, in the last two isolated
  host chains (14 and 15: events 459, 478).

Usage::

    python3 MKMSZR_build_reptile-specials_proof_v17.py CLEAN.z64 MKT.z64 -o MKMSZR_reptile-specials_common_proof_v17.z64
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from mkmszr.checksum import calculate_crc_6102
from mkmszr.fighter_import import (
    body_build,
    combos,
    commands,
    common_moves,
    components,
    host,
    lower_special,
    physics,
    sound,
    voices,
)
from mkmszr.fighter_import import description as fd
from mkmszr.fighter_import import lower_projectile as lp
from mkmszr.fighter_import.mips import Assembler
from mkmszr.fighter_import.mkt_fighter import validate_mkt_n64_rev2

_spec = importlib.util.spec_from_file_location(
    "v01", HERE / "MKMSZR_build_generic-projectile_proof_v01.py"
)
assert _spec and _spec.loader
v01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v01)
_spec5 = importlib.util.spec_from_file_location(
    "v05", HERE / "MKMSZR_build_generic-projectile_proof_v05.py"
)
assert _spec5 and _spec5.loader
v05 = importlib.util.module_from_spec(_spec5)
_spec5.loader.exec_module(v05)
# 8 KiB v6 arena (v10: Acid Spit; 6 KiB was full; the v05 helper sizes the file-0x1B load and the heap floor from these;
# Sektor's teleport line ran a 16 KiB arena, Runtime-confirmed): two specials do not fit 2 KiB.
v05.PAYLOAD_LIMIT = 0x3000  # v15: 12 KiB (Reverse Elbow; 8 KiB was full)
v05.ARENA_LO = (0x801AF420 + v05.PAYLOAD_LIMIT) & 0xFFFF
TABLE_RESERVE = 0x100  # moved HP command table at the arena start
PROJECTILE_SLOTS = (0x0D, 0x12)  # empty stock table-1 slots: flight, impact
HELPER_SLOT = 0x26  # empty stock table-1 slot: the throw helper
HELPER_DY_PX = -2  # owner fine-tune on the ball's height (v08: 1-2 px low; +dy is down)
PROJECTILE_CHAINS = (sound.ISOLATED_CHAINS[10], sound.ISOLATED_CHAINS[11])  # host events 335, 336
REACTION_SLOT = 0x2B  # dummy stock reaction -> the lifted MKT arc
FIRST_SELECTOR = 3
SPECIALS = (("forceball_fast", "directional_ice_down"), ("forceball_slow", "ice_clone"))
ACID_SELECTOR = FIRST_SELECTOR + len(SPECIALS)  # 5
ACID_REACTION_SLOT = 0x23  # dummy stock reaction -> the lifted acid stagger
ACID_CHAINS = (sound.ISOLATED_CHAINS[12], sound.ISOLATED_CHAINS[13])  # sizzle, spit
ACID_OFFSET_PX = (-30, -36)  # start from the forceball's host correction (calibrate)
ACID_HELPER_DY_PX = -38
ACID_THROW_SCRIPT = 0x40  # body.secondary_scripts key (no table entry)
ELBOW_SELECTOR = ACID_SELECTOR + 1  # 6
ELBOW_SCRIPT = 0x41  # body.secondary_scripts key: MKT table-1 slot 11 (the elbow)
HOLD_REACTION = 0x4C  # reaction byte -> 0x800A1190[0x4C] (unused endless-sleep entry)
DONOR_TICKS = 2  # MKT 60 Hz -> host 30 Hz
STEP_CHAINS = (sound.ISOLATED_CHAINS[14], sound.ISOLATED_CHAINS[15])  # host events 459, 478
STEP_EVENTS = (0x90, 0x91)  # two of MKT's four footsteps (group 0x800A1A3C)
ACID_SLEEP_TICKS = 15  # owner: half MKT's 31-tick recovery

FIGHTER = "reptile"
SAMPLE_ROM = 0x00F20000
VOICE_CHAINS = sound.ISOLATED_CHAINS[:10]  # 11-12 (host 335/336) stay for the projectile


def _free_from(file87: bytearray, start: int) -> int:
    """First 16-aligned offset after the last used byte of the body tail [start, TYPE_END)."""

    end = body_build.TYPE_END
    used = start
    for off in range(end - 1, start - 1, -1):
        if file87[off] != 0xFF:
            used = off + 1
            break
    return (used + 0xF) & ~0xF


def build(clean: bytes, mkt: bytes) -> tuple[bytes, dict]:  # type: ignore[type-arg]
    assert hashlib.sha256(clean).hexdigest() == v01.CLEAN_SHA256, (
        "not the clean MKMSZ USA Rev. 0 ROM"
    )
    validate_mkt_n64_rev2(mkt)
    description = fd.load(FIGHTER)
    donor = description.donor_fighter_id
    rom = bytearray(clean)
    v01.proof_base(rom)
    moves, _ = components.load_programs(FIGHTER)
    programs = {m.name: m for m in moves}

    body = body_build.build_body(description, clean, mkt, body_build.Extras(), rom=rom)
    file87 = common_moves.apply(
        bytes(body.file), stock=body.clean_file, flipped=body.flipped,
        slide="slide" in description.body.common_animations,
    )
    # Forceball art and scripts in the free body tail (the file keeps its stock size).
    ball = next(s for s in programs["forceball_fast"].steps if s["op"] == "projectile")
    throw = next(s for s in programs["forceball_fast"].steps if s["op"] == "animate")
    helper = lp.donor_helper(body_build.Donor(mkt, donor), throw["anim"])
    art = lp.place_art(file87, mkt, donor, ball, PROJECTILE_SLOTS, body_build.TYPE_END,
                       at=body.chain_start, helper=helper, helper_slot=HELPER_SLOT,
                       throw_rate=int(throw["rate"]))  # fmt: skip
    acid = next(s for s in programs["acid_spit"].steps if s["op"] == "projectile")
    acid = dict(acid, offset=list(ACID_OFFSET_PX))
    acid = lp.centre_on_art(body_build.Donor(mkt, donor), acid)  # box on the drawn spit
    acid_throw = next(s for s in programs["acid_spit"].steps if s["op"] == "animate")
    acid_helper = lp.donor_helper(body_build.Donor(mkt, donor), acid_throw["anim"])
    acid_art = lp.place_art(file87, mkt, donor, acid, None, body_build.TYPE_END,
                            at=_free_from(file87, body.chain_start), helper=acid_helper,
                            throw_rate=int(acid_throw["rate"]))  # fmt: skip
    assert len(file87) == body_build.FILE87_SIZE, hex(len(file87))
    start = body_build.FILE87_ROM
    rom[start : start + len(file87)] = file87

    graph = combos.donor_graph(mkt, donor)
    (table, index) = description.body.sources.get(combos.COMBO_SLOT, (0, combos.COMBO_SLOT))
    low = combos.lower(graph, index if table == 1 else None, set(description.body.slots))
    combos.install(rom, low)

    vs, samples_end = voices.install(rom, clean, mkt, donor, VOICE_CHAINS, SAMPLE_ROM)
    events, samples_end = lp.install_sounds(
        rom, clean, mkt, donor, ball, PROJECTILE_CHAINS, (samples_end + 0xF) & ~0xF
    )
    acid_events, samples_end = lp.install_sounds(
        rom, clean, mkt, donor, acid, ACID_CHAINS[:1], (samples_end + 0xF) & ~0xF
    )
    bank = sound.MktSoundBank(mkt)
    spit = bank.event(bank.fighter_event(donor, 8))
    samples_end = sound.install(rom, clean, spit, ACID_CHAINS[1], (samples_end + 0xF) & ~0xF)
    acid_sounds = {8: ACID_CHAINS[1].event}
    for event, chain in zip(STEP_EVENTS, STEP_CHAINS, strict=True):
        samples_end = sound.install(rom, clean, bank.event(event), chain, (samples_end + 0xF) & ~0xF)

    # Payload: [0x000, 0x100) moved HP command table; then specials; then command stubs.
    v05.v6_infrastructure(rom)
    animations = {(t, i): s for s, (t, i, _) in description.body.secondary_scripts.items()}
    a = Assembler(v01.PAYLOAD_VA + TABLE_RESERVE, cached_calls=True)
    specials = {}
    for k, (name, power) in enumerate(SPECIALS):
        prog = programs[name]
        step = next(s for s in prog.steps if s["op"] == "projectile")
        lowered = lp.lower(step, art, events, REACTION_SLOT, clean)
        host.emit_transfer_thunk(a, f"{name}_thunk", FIRST_SELECTOR + k)
        lower_special.emit_gate_condition(a, f"{name}_cond", lower_special.GATES[power],
                                          lower_special.COSTS[power],
                                          alive=(f"{name}_alive", "acid_alive"))  # fmt: skip
        lower_special.emit_action(a, f"{name}_root", prog.steps, cost=lower_special.COSTS[power],
                                  animations=animations, child=f"{name}_ball",
                                  helper="forceball_helper")  # fmt: skip
        lp.emit_process(a, lowered, child=f"{name}_ball", prefix=f"{name}_", alive=f"{name}_alive")
        specials[name] = lowered
    throw_slot = animations[(int(throw["anim"]["table"]), int(throw["anim"]["slot"]))]
    helper_dy = lowered.dy + HELPER_DY_PX * lp.UNITS_PER_PX
    lp.emit_helper(a, art, 0, helper_dy, "forceball_helper", throw_slot)  # shared by both
    # Acid Spit (Ice Blast's slot).
    acid_low = lp.lower(acid, acid_art, acid_events, ACID_REACTION_SLOT, clean)
    acid_low = dataclasses.replace(acid_low, impact_flip=False, impact_keep_y=True)
    acid_steps = [dict(s, ticks=ACID_SLEEP_TICKS) if s["op"] == "sleep" else s
                  for s in programs["acid_spit"].steps]  # fmt: skip
    acid_body = description.body.secondary_scripts and body.script_offsets[ACID_THROW_SCRIPT]
    host.emit_transfer_thunk(a, "acid_spit_thunk", ACID_SELECTOR)
    lower_special.emit_gate_condition(a, "acid_spit_cond", lower_special.ICE_BLAST_GATE,
                                      lower_special.COSTS["ice_blast"],
                                      default=lower_special.ICE_BLAST_STOCK_TIER)  # fmt: skip
    lower_special.emit_action(a, "acid_spit_root", acid_steps,
                              cost=lower_special.COSTS["ice_blast"],
                              animations={(1, 6): ("at", acid_body)}, child="acid_ball",
                              helper="acid_helper", sounds=acid_sounds, face=False)  # fmt: skip
    lp.emit_process(a, acid_low, child="acid_ball", prefix="acid_", data="acid_", alive="acid_alive")
    lp.emit_helper(a, acid_art, 0, ACID_HELPER_DY_PX * lp.UNITS_PER_PX, "acid_helper", None,
                   body_at=acid_body)  # fmt: skip
    # Reverse Elbow (Ice Shatter's slot).
    host.emit_transfer_thunk(a, "elbow_dash_thunk", ELBOW_SELECTOR)
    lower_special.emit_gate_condition(a, "elbow_dash_cond", lower_special.GATES["ice_shatter"],
                                      lower_special.COSTS["ice_shatter"])  # fmt: skip
    elbow_records = lower_special.emit_action(
        a, "elbow_dash_root", programs["elbow_dash"].steps, cost=lower_special.COSTS["ice_shatter"],
        animations={(0, description.body.run_slot): ("at", body_build.RUN_TARGET),
                    (1, 0x0B): ("at", body.script_offsets[ELBOW_SCRIPT])},
        face=False, donor_ticks=DONOR_TICKS, reactions={"elbow_hold": HOLD_REACTION},
        speed=lambda v: physics.fold_donor_speeds(v, v, lambda d: d, lp.UNITS_PER_PX)[0],
        footsteps={(0, description.body.run_slot): lower_special.Footsteps(
            *lower_special.donor_footsteps(body_build.Donor(mkt, donor), description.body.run_slot),
            tuple(c.event for c in STEP_CHAINS))})  # fmt: skip
    lower_special.emit_hold_reaction(a, "elbow_hold", DONOR_TICKS)
    host.emit_sound_player(a)
    lp.emit_helper_data(a, "forceball_helper")
    lp.emit_helper_data(a, "acid_helper")
    for word in ("forceball_fast_alive", "forceball_slow_alive", "acid_alive"):
        a.label(word)  # set while that projectile lives (lower_special per-move limit)
        a.raw(0)
    lp.emit_data(a, lowered, v01.PAYLOAD_VA)
    lp.emit_data(a, acid_low, v01.PAYLOAD_VA, clean, data="acid_")  # one strike record and reaction for both
    lower_special.emit_strike_data(a, elbow_records, v01.PAYLOAD_VA)
    main = a.link()
    overrides = {name: (0, a.labels[f"{name}_cond"], a.labels[f"{name}_thunk"])
                 for name, _ in (*SPECIALS, ("acid_spit", "ice_blast"), ("elbow_dash", "ice_shatter"))}  # fmt: skip
    cmds = commands.donor_commands(mkt, moves, description.commands)
    stub_base = (v01.PAYLOAD_VA + TABLE_RESERVE + len(main) + 0xF) & ~0xF
    low_cmd = commands.lower(clean, cmds, set(description.remove_commands), v01.PAYLOAD_VA,
                             stub_base, overrides)  # fmt: skip
    assert all(v + 0x2C * 5 + 4 <= v01.PAYLOAD_VA + TABLE_RESERVE for v in low_cmd.moved.values())
    end = stub_base - v01.PAYLOAD_VA + len(low_cmd.stubs)
    assert end <= v05.PAYLOAD_LIMIT, f"payload 0x{end:X} > 0x{v05.PAYLOAD_LIMIT:X}"
    assert set(rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v05.PAYLOAD_LIMIT]) == {0xFF}
    payload = bytearray(v05.PAYLOAD_LIMIT)
    payload[TABLE_RESERVE : TABLE_RESERVE + len(main)] = main
    payload[stub_base - v01.PAYLOAD_VA : end] = low_cmd.stubs
    rom[v01.PAYLOAD_ROM : v01.PAYLOAD_ROM + v05.PAYLOAD_LIMIT] = payload
    commands.install(rom, clean, low_cmd, v01.PAYLOAD_ROM, v01.PAYLOAD_VA)

    # Selectors 3 and 4 -> the two action roots (over the v6 infrastructure's own entries).
    v01.guarded(rom, 0x4B654, "2cc20004", "2cc20007")  # selectors 3-6
    table_rom = host.TRANSFER_TABLE - v01.VA_TO_ROM + 4 * FIRST_SELECTOR
    v01.guarded(rom, table_rom, "a01af4202404000308012a9300000000",
                "".join(f"{a.labels[f'{n}_root']:08x}" for n in
                        ("forceball_fast", "forceball_slow", "acid_spit", "elbow_dash")))  # fmt: skip
    hold_rom = lp.REACTION_TABLE - v01.VA_TO_ROM + 4 * HOLD_REACTION
    v01.guarded(rom, hold_rom, f"{lp.DUMMY_REACTION:08x}", f"{a.labels['elbow_hold']:08x}")
    acid_reaction_rom = lp.REACTION_TABLE - v01.VA_TO_ROM + 4 * ACID_REACTION_SLOT
    v01.guarded(rom, acid_reaction_rom, f"{lp.DUMMY_REACTION:08x}",
                f"{a.labels['acid_reaction']:08x}")  # fmt: skip
    reaction_rom = lp.REACTION_TABLE - v01.VA_TO_ROM + 4 * REACTION_SLOT
    v01.guarded(rom, reaction_rom, f"{lp.DUMMY_REACTION:08x}", f"{a.labels['reaction']:08x}")
    type_rom = lp.TYPE_FILE_TABLE - v01.VA_TO_ROM + 4 * lp.PLAYER_TYPE
    v01.guarded(rom, type_rom, "00000000", f"{lp.PLAYER_FILE_BASE:08x}")

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"report": body.report, "voices": vs, "samples_end": samples_end,
                        "combos": low, "commands": low_cmd, "payload_end": end,
                        "art": art, "acid_art": acid_art, "specials": specials}  # fmt: skip


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("clean", type=Path)
    parser.add_argument("mkt", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    rom, info = build(args.clean.read_bytes(), args.mkt.read_bytes())
    args.output.write_bytes(rom)
    print("OUT", args.output)
    print("SHA256", hashlib.sha256(rom).hexdigest())
    r = info["report"]
    print(
        "BODY",
        {
            k: (hex(v) if isinstance(v, int) else v)
            for k, v in r.items()
            if not isinstance(v, (list, dict))
        },
    )
    print("VOICES", info["voices"].category, "samples to", hex(info["samples_end"]))
    print("COMBOS", list(info["combos"].strings), {hex(k): hex(v) for k, v in info["combos"].strikes.items()})
    print("COMMANDS", *info["commands"].report, sep="\n  ")
    print("PAYLOAD", hex(info["payload_end"]), "ART", info["art"])
    print("ACID ART", info["acid_art"])
    print("TEST", "debug stage select, max EXP; Reptile's forceballs as his own specials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
