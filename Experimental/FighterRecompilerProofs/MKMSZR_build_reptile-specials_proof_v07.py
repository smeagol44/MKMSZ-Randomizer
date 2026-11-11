"""Reptile specials proof v07 (Fighter recompiler plan, milestone 4 step 3.1). Disposable.

v07 is v06 with the forming ball two poses ahead of MKT's script instead of one (owner, v06:
the big crescent 0x3050 never showed; the helper process runs about a pose behind the body):
the tiny 6x7 spark 0x2FD4 is dropped, 0x3000 shows with the first pose, then 0x3028, then the
crescent held until the launch. v06's SHA-256 reproduces at commit ``538a241``.

v06 is v05 (no crash, owner) with the forming ball at the body's real pace (owner, v05: "still
a bit too slow"): the host's animate-to-phase-end plays an odd rate one tick faster (rate 3 ->
a pose every 2 ticks), so the helper now steps every 2 ticks instead of 3
(``lower_projectile.phase_end_ticks``). v05's SHA-256 reproduces at commit ``077d8b1``.

v05 fixes v04's crash and the helper's height (owner, v04: black screen and artifacts after
the forming ball and the flying ball were on screen together; the forming ball too low):

* handover: the helper stays until the action asks for the launch, removes itself, and only
  then the ball is spawned (two type-4 projectile objects never coexist);
* the helper at (0, the ball's dy): v03's (-30, -36) px was over his chest, v04's (0, 0) low
  in front of his knees.

v04's SHA-256 reproduces at commit ``c5dfc7f``.

v04 is v03 with the forming ball in Reptile's hands (owner, v03: "more to Reptile's front, and
sooner"): the helper is aligned to Reptile (offset 0, as MKT aligns it to its owner; v03 used
the ball's spawn offset, 30 px back and 36 px up) and starts one pose earlier, with the throw,
holding its last frame until the launch. v03's SHA-256 reproduces at commit ``cf45a90``.

v03 is v02 with the ball forming in Reptile's hands during the throw (owner: "I'd like to have
that object"): MKT's token-11 helper (frames 0x2FD4, 0x3000, 0x3028, 0x3050, the flight palette)
as a helper process (``lower_projectile.donor_helper``/``emit_helper``): it appears with his
second body pose, steps with each pose, and ends as the ball launches, at the ball's spawn
point. v02's SHA-256 reproduces at commit ``9c5d63f``.

v02 is v01 without the forceball "blink" (owner, v01): the throw script had taken three helper
frames (the ball forming in his hands; MKT shows them on the token-11 helper through token 12)
as body poses. The throw is now his five body poses and the four-frame retract. v01's SHA-256
reproduces at commit ``d39cd75``.

Inputs proof v05 (owner-accepted body, combos, throw, commands, slide) plus Reptile's two
forceballs as his own specials, from his move programs (``fighters/moves/reptile.json``) and
reusable components only:

* Forceball fast (F,F + HP+LP) in Directional Ice's slot (tier gate ``0x8004A4F4``, Ice
  ``0x60``); Forceball slow (B,B + HP+LP) in Ice Clone's slot (gate ``0x8004A2A8``, ``0x60``).
* Condition ``lower_special.emit_gate_condition`` (Sektor's accepted missile conditions,
  generic) behind the commands' both-buttons check; action ``lower_special.emit_action``
  entered through the Ice-root selector table (selectors 3 and 4): Reptile's MKT throw
  (table-1 slot 5, phases 1-2, copied to host secondary 0x25 by ``body.secondary_scripts``),
  the projectile at phase end, 8 ticks, the retract, exit.
* The projectile is backend v1 (``lower_projectile``, Runtime-confirmed in proof v06): art and
  scripts now in the fighter file's free body tail (file keeps its stock size and place), MKT
  speeds (fast ``0x59999``, slow ``0x26666``), strike, the lifted MKT arc reaction, hum and impact
  sounds (host chains 335/336 after the voice samples).

Acid Spit (Ice Blast's slot) is still Sub-Zero's Ice Blast; it comes next. Usage::

    python3 MKMSZR_build_reptile-specials_proof_v07.py CLEAN.z64 MKT.z64 -o MKMSZR_reptile-specials_common_proof_v07.z64
"""

from __future__ import annotations

import argparse
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
# 6 KiB v6 arena (v05: 4 KiB was full; the v05 helper sizes the file-0x1B load and the heap floor from these;
# Sektor's teleport line ran a 16 KiB arena, Runtime-confirmed): two specials do not fit 2 KiB.
v05.PAYLOAD_LIMIT = 0x1800
v05.ARENA_LO = (0x801AF420 + v05.PAYLOAD_LIMIT) & 0xFFFF
TABLE_RESERVE = 0x100  # moved HP command table at the arena start
PROJECTILE_SLOTS = (0x0D, 0x12)  # empty stock table-1 slots: flight, impact
HELPER_SLOT = 0x26  # empty stock table-1 slot: the throw helper
HELPER_LEAD = 2  # body poses earlier than MKT's script (owner: sooner; v06 still a pose late)
PROJECTILE_CHAINS = (sound.ISOLATED_CHAINS[10], sound.ISOLATED_CHAINS[11])  # host events 335, 336
REACTION_SLOT = 0x2B  # dummy stock reaction -> the lifted MKT arc
FIRST_SELECTOR = 3
SPECIALS = (("forceball_fast", "directional_ice_down"), ("forceball_slow", "ice_clone"))

FIGHTER = "reptile"
SAMPLE_ROM = 0x00F20000
VOICE_CHAINS = sound.ISOLATED_CHAINS[:10]  # 11-12 (host 335/336) stay for the projectile


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
                       throw_rate=int(throw["rate"]), helper_lead=HELPER_LEAD)  # fmt: skip
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
                                          lower_special.COSTS[power])  # fmt: skip
        lower_special.emit_action(a, f"{name}_root", prog.steps, cost=lower_special.COSTS[power],
                                  animations=animations, child=f"{name}_ball",
                                  helper="forceball_helper")  # fmt: skip
        lp.emit_process(a, lowered, child=f"{name}_ball", prefix=f"{name}_")
        specials[name] = lowered
    lp.emit_helper(a, art, 0, lowered.dy, "forceball_helper")  # shared by both
    host.emit_sound_player(a)
    lp.emit_helper_data(a, "forceball_helper")
    lp.emit_data(a, lowered, v01.PAYLOAD_VA)  # one strike record and reaction for both
    main = a.link()
    overrides = {name: (0, a.labels[f"{name}_cond"], a.labels[f"{name}_thunk"])
                 for name, _ in SPECIALS}  # fmt: skip
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
    v01.guarded(rom, 0x4B654, "2cc20004", "2cc20005")
    table_rom = host.TRANSFER_TABLE - v01.VA_TO_ROM + 4 * FIRST_SELECTOR
    v01.guarded(rom, table_rom, "a01af42024040003",
                "".join(f"{a.labels[f'{n}_root']:08x}" for n, _ in SPECIALS))  # fmt: skip
    reaction_rom = lp.REACTION_TABLE - v01.VA_TO_ROM + 4 * REACTION_SLOT
    v01.guarded(rom, reaction_rom, f"{lp.DUMMY_REACTION:08x}", f"{a.labels['reaction']:08x}")
    type_rom = lp.TYPE_FILE_TABLE - v01.VA_TO_ROM + 4 * lp.PLAYER_TYPE
    v01.guarded(rom, type_rom, "00000000", f"{lp.PLAYER_FILE_BASE:08x}")

    crc1, crc2 = calculate_crc_6102(rom)
    v01.put32(rom, 0x10, crc1)
    v01.put32(rom, 0x14, crc2)
    return bytes(rom), {"report": body.report, "voices": vs, "samples_end": samples_end,
                        "combos": low, "commands": low_cmd, "payload_end": end,
                        "art": art, "specials": specials}  # fmt: skip


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
    print("TEST", "debug stage select, max EXP; Reptile's forceballs as his own specials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
