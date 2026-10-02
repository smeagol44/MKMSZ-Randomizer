"""Build the disposable MKMSZR pickup-placement coordinate probe.

Research tool, not a production patch.

The overlay prints native stage/selector plus the live player actor X/Y/Z words
in the same raw fixed8 coordinate family used by ordinary pickup records.

Accepted hand-authored placement convention from the 2026-10-02 Wind proof:
    pickup X = displayed player X
    pickup Z = displayed player Z
    pickup Y = displayed player Y + (28 << 8)
             = displayed player Y + 0x1C00

The +28 adjustment is a visual authoring convention established by manual
placement review. It does not change the engine's coordinate format.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mkmszr.data.addresses import (
    NATIVE_BOOTSTRAP_STUB_CAPACITY,
    NATIVE_BOOTSTRAP_STUB_ROM,
    NATIVE_BOOTSTRAP_STUB_VA,
    PROVEN_PAYLOAD_RDRAM,
)
from mkmszr.mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    jal,
    jr,
    lw,
    sh,
    sll,
    sltiu,
    srl,
    sw,
    words_blob,
)
from mkmszr.patches.arena import ArenaReservationPatch
from mkmszr.patches.base import PatchContext, PatchPipeline
from mkmszr.patches.flow_bypass import (
    BootLogoBypassPatch,
    SafeStageSelectSkipAutoSavePatch,
)
from mkmszr.patches.native_payload import (
    NativePayloadPatch,
    NativePayloadSpec,
    kseg1_alias,
)
from mkmszr.patches.stage_selector import SafeStageSelectorPatch
from mkmszr.rom import RomImage

HUD_HOOK_ROM = 0x0005D9CC
EXPECTED_HUD_CALL = 0x0C007AB9
DISPLACED_HUD_VA = 0x8001EAE4
TEXT_DRAW_VA = 0x80073E74
FONT_VA = 0x800B1E20
PLAYER_CTRL_PTR_VA = 0x802C1AC0
CURRENT_STAGE_VA = 0x8009A910
STAGE_SELECTOR_VA = 0x802C18F8
GAMEPLAY_ENABLE_VA = 0x802C1A04

BASE = PROVEN_PAYLOAD_RDRAM
UBASE = kseg1_alias(BASE)
WRAP_OFF = 0x020
HEX_OFF = 0x300
STR_OFF = 0x400
WRAP_UVA = UBASE + WRAP_OFF
HEX_UVA = UBASE + HEX_OFF
STR_UVA = UBASE + STR_OFF

LINES = (
    b"STG 00000000 SEL 00000000\x00",
    b"X   00000000 Y   00000000\x00",
    b"Z   00000000\x00",
    b"RAW FIXED8\x00",
)
line_offsets = []
cursor = 0
for line in LINES:
    line_offsets.append(cursor)
    cursor = (cursor + len(line) + 3) & ~3

REG = {
    "zero": 0, "v0": 2, "v1": 3, "a0": 4, "a1": 5, "a2": 6, "a3": 7,
    "t0": 8, "t1": 9, "t2": 10, "t3": 11, "t8": 24, "t9": 25,
    "s0": 16, "s1": 17, "s2": 18, "s3": 19, "s4": 20,
    "sp": 29, "ra": 31,
}
NOP = 0

def sb(rt: str, off: int, base: str) -> int:
    return (0x28 << 26) | (REG[base] << 21) | (REG[rt] << 16) | (off & 0xFFFF)

def build_hex32() -> bytes:
    e = Emitter()
    e.emit(addiu("t0", "zero", 8))
    e.label("loop")
    e.emit(srl("t1", "a0", 28), sltiu("t2", "t1", 10))
    e.beq("t2", "zero", "alpha"); e.emit(NOP)
    e.emit(addiu("t1", "t1", 0x30))
    e.beq("zero", "zero", "store"); e.emit(NOP)
    e.label("alpha")
    e.emit(addiu("t1", "t1", 0x37))
    e.label("store")
    e.emit(
        sb("t1", 0, "a1"),
        addiu("a1", "a1", 1),
        sll("a0", "a0", 4),
        addiu("t0", "t0", -1),
    )
    e.bne("t0", "zero", "loop"); e.emit(NOP)
    e.emit(jr("ra"), NOP)
    return e.finish()

def build_wrapper() -> bytes:
    e = Emitter()
    e.emit(addiu("sp", "sp", -0x40), sw("ra", 0x3C, "sp"))
    for i, reg in enumerate(("s0", "s1", "s2", "s3", "s4")):
        e.emit(sw(reg, 0x20 + i * 4, "sp"))

    # Preserve the displaced stock HUD submit first.
    e.emit(jal(DISPLACED_HUD_VA), NOP)

    # Front-end / Mission Objective / pre-gameplay paths remain stock.
    e.emit(*address_words("t9", GAMEPLAY_ENABLE_VA), lw("t9", 0, "t9"))
    e.beq("t9", "zero", "restore"); e.emit(NOP)

    e.emit(*address_words("t0", PLAYER_CTRL_PTR_VA), lw("t0", 0, "t0"))
    e.beq("t0", "zero", "restore"); e.emit(NOP)

    # Diagnostic convenience from the accepted v03 probe.
    e.emit(addiu("t1", "zero", 0xA6), sh("t1", 0x654, "t0"), sh("t1", 0x656, "t0"))

    # controller +0x6E0 -> live actor; actor +0x2C/+0x30/+0x34 -> X/Y/Z.
    e.emit(lw("t1", 0x6E0, "t0"))
    e.beq("t1", "zero", "restore"); e.emit(NOP)
    e.emit(lw("s0", 0x2C, "t1"), lw("s1", 0x30, "t1"), lw("s2", 0x34, "t1"))

    e.emit(*address_words("t2", CURRENT_STAGE_VA), lw("s3", 0, "t2"))
    e.emit(*address_words("t2", STAGE_SELECTOR_VA), lw("s4", 0, "t2"))

    def fmt(value: str, line: int, off: int) -> None:
        e.emit(
            addu("a0", value, "zero"),
            *address_words("a1", STR_UVA + line_offsets[line] + off),
            jal(HEX_UVA),
            NOP,
        )

    fmt("s3", 0, 4); fmt("s4", 0, 17)
    fmt("s0", 1, 4); fmt("s1", 1, 17)
    fmt("s2", 2, 4)

    # Draw below the stock HP bar. The fifth ABI argument is the native font ptr.
    for idx, y in enumerate((60, 72, 84, 96)):
        e.emit(
            *address_words("a0", STR_UVA + line_offsets[idx]),
            addiu("a1", "zero", 8),
            addiu("a2", "zero", y),
            addiu("a3", "zero", 2),
            *address_words("t8", FONT_VA),
            sw("t8", 0x10, "sp"),
            jal(TEXT_DRAW_VA),
            NOP,
        )

    e.label("restore")
    for i, reg in enumerate(("s0", "s1", "s2", "s3", "s4")):
        e.emit(lw(reg, 0x20 + i * 4, "sp"))
    e.emit(lw("ra", 0x3C, "sp"), addiu("sp", "sp", 0x40), jr("ra"), NOP)
    return e.finish()

class PlacementProbeHudPatch:
    name = "pickup-placement-probe-hud"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context
        rom.expect_u32(HUD_HOOK_ROM, EXPECTED_HUD_CALL)

        tramp_rom = NATIVE_BOOTSTRAP_STUB_ROM + NATIVE_BOOTSTRAP_STUB_CAPACITY - 16
        tramp_va = NATIVE_BOOTSTRAP_STUB_VA + NATIVE_BOOTSTRAP_STUB_CAPACITY - 16
        rom.expect_bytes(tramp_rom, bytes(16))
        rom.write_bytes(
            tramp_rom,
            words_blob([*address_words("t9", WRAP_UVA), jr("t9"), NOP]),
        )
        rom.write_u32(HUD_HOOK_ROM, jal(tramp_va))
        return (
            "prints native stage/selector and live actor raw fixed8 X/Y/Z",
            "runs only after gameplay-enable 0x802C1A04 is nonzero",
            "refills HP/resource to 0x00A6 for placement work",
        )

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("clean_rom", type=Path)
    ap.add_argument("output_rom", type=Path)
    args = ap.parse_args()

    source = args.clean_rom.read_bytes()
    rom = RomImage.from_bytes(source, require_clean=True)

    hexcode = build_hex32()
    wrapper = build_wrapper()
    payload = bytearray(0x600)
    payload[0:8] = words_blob([jr("ra"), NOP])
    payload[WRAP_OFF:WRAP_OFF + len(wrapper)] = wrapper
    payload[HEX_OFF:HEX_OFF + len(hexcode)] = hexcode
    for line, off in zip(LINES, line_offsets):
        payload[STR_OFF + off:STR_OFF + off + len(line)] = line

    PatchPipeline((
        SafeStageSelectorPatch(),
        SafeStageSelectSkipAutoSavePatch(),
        ArenaReservationPatch(),
        NativePayloadPatch(NativePayloadSpec(payload=bytes(payload))),
        PlacementProbeHudPatch(),
        BootLogoBypassPatch(),
    )).apply(rom, PatchContext(seed="PLACEMENT-PROBE"))

    crc1, crc2 = rom.update_header_crc()
    args.output_rom.write_bytes(rom.to_bytes())
    print("clean SHA-256", hashlib.sha256(source).hexdigest())
    print("output SHA-256", rom.output_sha256)
    print("CRC1/CRC2", f"{crc1:08X} / {crc2:08X}")

if __name__ == "__main__":
    main()
