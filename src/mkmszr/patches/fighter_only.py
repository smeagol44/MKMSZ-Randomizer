"""Randomizer off: a vanilla game with an imported fighter (owner request, 2026-11-27).

The ROM the fighter recompiler proofs test, without their debug harness: the fighter's build
(:func:`fighter_import.fighter_build.build`, a 16 MiB image) and its payload transport, plus the
description's Power Ups help text, icons and outfit. Nothing of the randomizer is composed (the
pipeline adds only the logo bypass, the audio fix and the title branding).

Payload transport: the specials proofs' (Sektor SMRE proofs v01-v15, Rayden specials proofs,
Runtime-confirmed bounded): the arena prefix is reserved past the payload, the stock arena setup
(``0x80066FE0``) jumps to a stub at ``0x8009A184`` (ROM ``0x9AD84``) that loads the payload (file
``0x1B``, ROM ``SCRATCH_ROM``) to ``0x801AF420``. Left out of the proof harness: the debug stage
select and boot skip, the max-EXP write and the raised EXP caps.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config import OutfitConfig
from ..errors import PatchError
from ..fighter_import import outfit
from ..rom import RomImage
from .base import PatchContext

CLEAN_SIZE = 0x01000000
FILE_TABLE, FILE_1B = 0x000A5010, 0x1B
ARENA_PREFIX_ROM = 0x66F64  # addiu v0, v0, 0xF420: the arena's first free byte
ARENA_HOOK_ROM = 0x66FE0
STUB_ROM = 0x9AD84  # 0x50 zero bytes in the clean ROM (the proofs' loader stub)
STUB_VA = 0x8009A184


def transport_edits(link_va: int, payload_limit: int, scratch_rom: int) -> dict[int, tuple[bytes, bytes]]:
    """ROM offset -> (clean bytes, new bytes) of the payload transport."""

    arena = f"{(link_va + payload_limit) & 0xFFFF:04x}"
    jump = 0x08000000 | ((STUB_VA >> 2) & 0x03FFFFFF)
    stub = (
        "27bdffe8" "3c02801b" "2442" + arena +  # sp -= 0x18; v0 = the arena past the payload
        "afbf0010" "3c04800f" "ac82ecd0"  # save ra; the stock arena pointer
        "0c0198e4" "00000000"  # the stock arena setup
        "2404001b" "3c05801b" "24a5f420"  # a0 = file 0x1B, a1 = 0x801AF420
        "0c019759" "00000000"  # load it
        "8fbf0010" "27bd0018" "03e00008" "00000000"
    )
    return {
        ARENA_PREFIX_ROM: (bytes.fromhex("2442f420"), bytes.fromhex("2442" + arena)),
        ARENA_HOOK_ROM: (bytes.fromhex("27bdffe83c02801b2442f420"),
                         f"{jump:08x}000000002442{arena}"),
        STUB_ROM: (bytes(0x50), bytes.fromhex(stub)),
        FILE_TABLE + FILE_1B * 12: (bytes(8), (scratch_rom.to_bytes(4, "big")
                                              + (scratch_rom + payload_limit).to_bytes(4, "big"))),
    }  # fmt: skip


@dataclass(frozen=True)
class FighterOnlyPatch:
    """The imported ``fighter`` (from ``mkt``, MKT USA Rev. 2) on an otherwise vanilla ROM."""

    fighter: str
    mkt: bytes
    outfit: OutfitConfig = field(default_factory=OutfitConfig)
    name: str = "fighter-only"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        from ..fighter_import import description, fighter_build, fighter_help, fighter_icons

        if len(rom.data) != CLEAN_SIZE:
            raise PatchError("the fighter-only build needs the 16 MiB ROM")
        clean = rom._original
        made = fighter_build.build(clean, self.mkt, self.fighter)
        data = rom.data
        moved = 0
        for base in range(0, CLEAN_SIZE, 0x1000):
            if made.rom[base : base + 0x1000] == clean[base : base + 0x1000]:
                continue
            for off in range(base, base + 0x1000, 4):
                if off in (0x10, 0x14) or made.rom[off : off + 4] == clean[off : off + 4]:
                    continue
                rom.expect_bytes(off, clean[off : off + 4])
                data[off : off + 4] = made.rom[off : off + 4]
                moved += 1
        for off, (old, new) in transport_edits(
            made.link_va & ~0x20000000, fighter_build.PAYLOAD_LIMIT, fighter_build.SCRATCH_ROM
        ).items():
            rom.expect_bytes(off, old)
            rom.write_bytes(off, new if isinstance(new, bytes) else bytes.fromhex(new))

        d = description.load(self.fighter)
        for off, blob in fighter_help.edits(bytes(data), clean, d.help).items():
            if off != fighter_help.power_help.HELP_TABLE_ROM:
                rom.expect_bytes(off, clean[off : off + len(blob)])
            rom.write_bytes(off, blob)
        icon_span = fighter_icons.apply(data, self.mkt, d.donor_fighter_id, d.icons)
        mode = self.outfit.mode.lower()
        if mode != "vanilla":
            if not d.outfit:
                raise PatchError(f"fighter {self.fighter} has no outfit recolour; use the vanilla outfit")
            entry = FILE_TABLE + 0x87 * 12
            start, end = (int.from_bytes(data[entry + k : entry + k + 4], "big") for k in (0, 4))
            data[start:end] = outfit.recolor(
                data[start:end], mode, entries=d.outfit["entries"], own=d.outfit["own"],
                hue=self.outfit.hue_degrees, rgb=self.outfit.rgb, seed=context.seed,
            )  # fmt: skip
        return (
            f"fighter: {self.fighter} on a vanilla game (randomizer off)",
            f"{moved} fighter words; payload file 0x1B at ROM 0x{fighter_build.SCRATCH_ROM:X}",
            f"Power Ups icons: file 0x5D 0x{icon_span[0]:X}-0x{icon_span[1]:X}",
        )
