"""Fighter swap: replace Sub-Zero with a fighter imported from the MKT donor ROM.

Every importable fighter (Reptile, Rayden and, since SMRE step 3 on 2026-11-27, Sektor) is
built from its description (``fighter_import.fighter_build.production``) on the clean MKMSZ ROM
and the user's MKT ROM; this patch moves the fighter's changes into the randomizer ROM:

* every word that build changes in the 16 MiB part is the fighter's and must still hold its
  clean value here (an owner conflict fails the build), except the derived words (a kept
  power's moved tier, ``fighter_build.tier_edits``), recomputed from this ROM after any
  power-order shuffle;
* fighter file 0x87 and the donor samples go to the generated-output tail
  ``[0x01820000, 0x01880000)``, which must still be free (``0xFF``);
* the Power Ups help text, icons and the outfit on the fighter's palette are applied from the
  description;
* the fixed loader goes into shared file 0x1A at KSEG0 ``0x801B30F0`` (pool tail after the
  Inventory legend), extending the file-0x1A entry.

It runs last in the pipeline so its guards see every upstream owner. SPECIALS must stay on
CLASSIC (the importer's input layer is the classic one). Sektor's legacy build
(``fighter_import.sektor_build``, production composition v13, Runtime-confirmed through v13)
is no longer used by the product; its transplant lists went with it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config import OutfitConfig
from ..errors import PatchError
from ..fighter_import import outfit
from ..rom import RomImage
from .base import PatchContext

FIGHTERS = ("sub-zero", "sektor", "reptile", "rayden")
# Fighters built from their description (fighter_import.fighter_build, milestone 5): every word
# the build changes is the fighter's, so no list is kept here.
DESCRIBED = ("reptile", "rayden", "sektor")  # Sektor since SMRE step 3 (2026-11-27)
OUTPUT_SIZE = 0x02000000
CLEAN_SIZE = 0x01000000
FIXED_VA = 0xA01B30F0  # production pool tail after the Inventory legend (ends 0x801B30E6)
POOL_BASE, POOL_END = 0x801AF820, 0x801B3420
FILE_TABLE, FILE_1A, FILE_87 = 0x000A5010, 0x1A, 0x87
TAIL = (0x01820000, 0x01880000)  # enlarged from 0x0186E4C0 for Rayden (Memory map)


def _be32(data, off: int) -> int:
    return int.from_bytes(data[off : off + 4], "big")


def _changed_words(a: bytes, b: bytes, size: int):
    """Word offsets in ``[0, size)`` where ``a`` and ``b`` differ (block-skipping scan)."""

    block = 0x1000
    for base in range(0, size, block):
        if a[base : base + block] == b[base : base + block]:
            continue
        for off in range(base, min(base + block, size), 4):
            if a[off : off + 4] != b[off : off + 4]:
                yield off


@dataclass(frozen=True)
class FighterSwapPatch:
    """Swap the player fighter for ``fighter`` imported from ``mkt`` (the MKT USA Rev. 2 ROM)."""

    fighter: str
    mkt: bytes
    outfit: OutfitConfig = field(default_factory=OutfitConfig)
    name: str = "fighter-swap"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if self.fighter in DESCRIBED:
            return _apply_described(self.fighter, self.mkt, rom, self.outfit, context.seed)
        raise PatchError(f"fighter {self.fighter!r} cannot be imported")


def _apply_described(fighter: str, mkt: bytes, rom: RomImage, outfit_config: OutfitConfig | None = None,
                     seed: str | None = None) -> tuple[str, ...]:  # fmt: skip
    """A described fighter (milestone 5): its production build (``fighter_build.production``)
    on the clean ROM; every word that build changes in the 16 MiB part is the fighter's and must
    still hold its clean value here (an owner conflict fails the build). Then the tail, the
    fixed loader in shared file 0x1A, and the Power Ups icons, help and outfit recolour from the
    description (``outfit``: his body palette entries and own colour, as Sektor's)."""

    from ..fighter_import import description, fighter_build, fighter_help, fighter_icons

    if len(rom.data) != OUTPUT_SIZE:
        raise PatchError("fighter swap needs the 32 MiB generated output")
    clean = rom._original
    made = fighter_build.production(clean, mkt, fighter, fixed_va=FIXED_VA)
    image, man = made.rom, made.manifest
    data = rom.data
    if tuple(man["tail"]) != TAIL:
        raise PatchError("fighter build uses another tail region")

    moved, conflicts = 0, []
    derived = set(man.get("derived", ()))  # recomputed below from this ROM (tier moves)
    for off in _changed_words(image, clean, CLEAN_SIZE):
        if off in (0x10, 0x14) or off in derived:  # checksum (the pipeline's), derived
            continue
        if data[off : off + 4] != clean[off : off + 4]:
            conflicts.append(f"0x{off:X}")
            continue
        data[off : off + 4] = image[off : off + 4]
        moved += 1
    if conflicts:
        raise PatchError(f"fighter swap: owner conflicts {conflicts[:8]}")
    if set(data[TAIL[0] : TAIL[1]]) != {0xFF}:
        raise PatchError("fighter tail region is not free in the randomizer ROM")
    data[TAIL[0] : TAIL[1]] = image[TAIL[0] : TAIL[1]]

    d = description.load(fighter)
    for off, (old, new) in fighter_build.tier_edits(bytes(data), d.tiers).items():  # after any shuffle
        rom.expect_u32(off, old)
        rom.write_u32(off, new)
    for off, blob in fighter_help.edits(bytes(data), clean, d.help).items():
        if off != fighter_help.power_help.HELP_TABLE_ROM:
            rom.expect_bytes(off, clean[off : off + len(blob)])
        rom.write_bytes(off, blob)
    icon_span = fighter_icons.apply(data, mkt, d.donor_fighter_id, d.icons)
    mode = (outfit_config or OutfitConfig()).mode.lower()
    if mode != "vanilla":
        if not d.outfit:
            raise PatchError(f"fighter {fighter} has no outfit recolour; use the vanilla outfit")
        f87 = (man["file87_rom"], man["file87_rom"] + man["file87_size"])
        data[f87[0] : f87[1]] = outfit.recolor(
            data[f87[0] : f87[1]], mode, entries=d.outfit["entries"], own=d.outfit["own"],
            hue=outfit_config.hue_degrees, rgb=outfit_config.rgb, seed=seed,  # type: ignore[union-attr]
        )  # fmt: skip

    f1a_end, at = _place_fixed(rom, made.fixed)
    return (
        f"fighter: {fighter} (built from its description and the MKT donor)",
        f"transplanted {moved} words; tail 0x{TAIL[0]:08X}-0x{TAIL[1]:08X}",
        (
            f"fixed loader 0x{FIXED_VA & ~0x20000000:08X}-0x{(FIXED_VA & ~0x20000000) + len(made.fixed):08X}; "
            f"file 0x1A end 0x{f1a_end:X} -> 0x{at + len(made.fixed):X}"
        ),
        f"payload blob 0x{man['blob_end'] - man['blob_off']:X} bytes in the fighter file, {man['relocs']} relocations",
        f"Power Ups icons: file 0x5D 0x{icon_span[0]:X}-0x{icon_span[1]:X}",
    )


def _place_fixed(rom: RomImage, fixed: bytes) -> tuple[int, int]:
    """The fixed loader into shared file 0x1A at :data:`FIXED_VA` (as Sektor's step 3)."""

    data = rom.data
    e1a = FILE_TABLE + FILE_1A * 12
    f1a_start, f1a_end = _be32(data, e1a), _be32(data, e1a + 4)
    fixed_k0 = FIXED_VA & ~0x20000000
    if POOL_BASE + (f1a_end - f1a_start) > fixed_k0:
        raise PatchError("file 0x1A already reaches the fighter's fixed loader")
    at = f1a_start + (fixed_k0 - POOL_BASE)
    if fixed_k0 + len(fixed) > POOL_END or set(data[f1a_end : at + len(fixed)]) != {0xFF}:
        raise PatchError("fighter fixed loader: pool tail not free")
    data[f1a_end:at] = bytes(at - f1a_end)  # padding inside the loaded file
    data[at : at + len(fixed)] = fixed
    rom.write_u32(e1a + 4, at + len(fixed))
    return f1a_end, at
