"""Fighter swap: replace Sub-Zero with a fighter imported from the MKT donor ROM.

Production form of the Sektor production-composition proof v13
(``Experimental/SektorTransplantBuilders/production/MKMSZR_build_sektor_production_v13.py``;
Runtime-confirmed by the user through v13). The importer builds the fighter from the clean
MKMSZ ROM and the user's MKT ROM (:func:`mkmszr.fighter_import.sektor_build.build`, with its
fixed loader linked for the production pool tail); this patch moves only the fighter's
changes into the randomizer ROM:

* every 16 MiB word the fighter build changes is classified, by an explicit list, as fighter
  (transplanted), derived (recomputed here) or importer proof infrastructure (dropped). An
  unclassified change fails the build;
* every transplanted word must still hold its clean value in the randomizer ROM (no owner
  conflict), else the build fails;
* the R4 tier/cost stock edits are recomputed from the randomizer ROM after any power-order
  shuffle (:func:`sektor_tiers.stock_edits`);
* fighter file 0x87 and the donor samples go to the generated-output tail
  ``[0x01820000, 0x0186E4C0)``, which must still be free (``0xFF``);
* the Power Ups help text, the Power Ups icons (from donor art) and the outfit on the
  fighter's palette are applied;
* the fixed loader (0x280 bytes for Sektor) goes into shared file 0x1A at KSEG0 ``0x801B30F0`` (pool tail
  after the Inventory legend), extending the file-0x1A entry.

It runs last in the pipeline so its guards see every upstream owner. SPECIALS must stay on
CLASSIC (the importer's input layer is the classic one).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config import OutfitConfig
from ..errors import PatchError
from ..fighter_import import outfit, power_help, power_icons
from ..fighter_import.actions import sektor_tiers
from ..rom import RomImage
from .base import PatchContext
from .rainbow_palette import LOAD_JAL_SITES

FIGHTERS = ("sub-zero", "sektor", "reptile")
# Fighters built from their description (fighter_import.fighter_build, milestone 5): every word
# the build changes is the fighter's, so no list is kept here.
DESCRIBED = ("reptile",)
OUTPUT_SIZE = 0x02000000
CLEAN_SIZE = 0x01000000
FIXED_VA = 0xA01B30F0  # production pool tail after the Inventory legend (ends 0x801B30E6)
POOL_BASE, POOL_END = 0x801AF820, 0x801B3420
FILE_TABLE, FILE_1A, FILE_87 = 0x000A5010, 0x1A, 0x87
TAIL = (0x01820000, 0x0186E4C0)
SOUND_TABLES = (0x00947000, 0x00980000)  # patch/subpatch/wave/book/track records

# Fighter words (transplanted), by ROM offset or range [start, end).
TRANSPLANT_SITES = frozenset({
    *LOAD_JAL_SITES,  # 15 file-0x87 load calls -> fixed loader
    0x0002F7A0,  # Run animation rate 2 -> 3
    0x0004B654,  # transfer-selector bound (selectors 3 teleport, 4 lifted Ice root)
    0x0005C8D4, 0x0005C9C8, 0x0005C9F8,  # throw sound hooks -> trampolines
    0x000A1C5C, 0x000A1C60,  # transfer table entries 3, 4
    0x000A1CE8,  # knee root (Sektor HK,HK combo)
    0x000A1E1C,  # reaction table entry 0x23
    0x000A3AD8, 0x000A3ADC,  # Sub-Zero player voice table (Sektor voice set)
    0x000A5664, 0x000A5668,  # file 0x87 entry (repointed to the tail)
    0x000B00D0,  # strike pointer, selector 0x13
    0x000B1A38,  # combo knockback strike record (selector 4): damage 7 -> 10 (Sektor build v62, owner)
})  # fmt: skip
TRANSPLANT_RANGES = (
    (0x000B1B0C, 0x000B1B94),  # LP (double, straight) and LK (teleport) records
    (0x000B1C80, 0x000B1D10),  # HP record (homing) and Sektor combo records
    SOUND_TABLES,
)
# R4 stock edits: recomputed from the randomizer ROM, never transplanted.
DERIVED_SITES = frozenset(
    {sektor_tiers.HK_RECORD_ROM, *sektor_tiers.SHATTER_BRANCHES, sektor_tiers.SUPER_SLIDE_GATE_ROM}
)
# Importer proof infrastructure (dropped).
DROP_SITES = frozenset({0x10, 0x14, 0x0000DD60, 0x0000DD64, 0x0000E028, 0x00015CD0, 0x00015CD4,
                        0x0007A3F4, 0x00066F64, 0x000A5154, 0x000A5158})  # fmt: skip
DROP_RANGES = (
    (0x00066FE0, 0x00066FEC),  # proof loader hook
    (0x0009A700, 0x0009A720),  # debug stage-menu mapper
    (0x0009AD84, 0x0009ADD4),  # proof bootstrap stub
    (0x0009B7DC, 0x0009B80C),  # debug stage-menu table
    (0x000A6FFC, 0x000A7010),  # max-EXP cheat
    (0x00F10000, 0x00F14000),  # proof file 0x1B (fixed loader harvested from here)
)


def _in(off: int, ranges) -> bool:
    return any(a <= off < b for a, b in ranges)


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
        if self.fighter != "sektor":
            raise PatchError(f"fighter {self.fighter!r} cannot be imported")
        from ..fighter_import.sektor_build import build

        if len(rom.data) != OUTPUT_SIZE:
            raise PatchError("fighter swap needs the 32 MiB generated output")
        clean = rom._original
        made = build(clean, self.mkt, fixed_va=FIXED_VA)
        sek, man = made["rom"], made["manifest"]
        if len(sek) != OUTPUT_SIZE or man["fixed_va"] != FIXED_VA:
            raise PatchError("fighter build has an unexpected layout")
        data = rom.data

        # 1. Classify and transplant every changed word of the 16 MiB part.
        moved, conflicts, unknown = 0, [], []
        for off in _changed_words(sek, clean, CLEAN_SIZE):
            if off in DROP_SITES or _in(off, DROP_RANGES) or off in DERIVED_SITES:
                continue
            if off in TRANSPLANT_SITES or _in(off, TRANSPLANT_RANGES):
                if data[off : off + 4] != clean[off : off + 4]:
                    conflicts.append(f"0x{off:X}")
                    continue
                data[off : off + 4] = sek[off : off + 4]
                moved += 1
                continue
            unknown.append(f"0x{off:X}")
        if unknown or conflicts:
            raise PatchError(f"fighter swap: unclassified {unknown[:8]} / owner conflicts {conflicts[:8]}")

        # 1b. R4 stock edits, recomputed from the randomizer ROM (after any power-order shuffle).
        for off, (old, new) in sektor_tiers.stock_edits(bytes(data)).items():
            rom.expect_u32(off, old)
            if _be32(sek, off) == _be32(clean, off):
                raise PatchError(f"fighter build does not edit derived site 0x{off:X}")
            rom.write_u32(off, new)

        # 2. Fighter file 0x87 and samples in the generated-output tail.
        if set(data[TAIL[0] : TAIL[1]]) != {0xFF}:
            raise PatchError("fighter tail region is not free in the randomizer ROM")
        data[TAIL[0] : TAIL[1]] = sek[TAIL[0] : TAIL[1]]
        f87 = (man["file87_rom"], man["file87_rom"] + man["file87_size"])
        entry87 = FILE_TABLE + FILE_87 * 12
        if (_be32(data, entry87), _be32(data, entry87 + 4)) != f87 or not TAIL[0] <= f87[0] < f87[1] <= TAIL[1]:
            raise PatchError("fighter file 0x87 entry does not name the tail copy")

        # 2b. Presentation: Power Ups help text (blocks must still be stock), icons, outfit.
        for off, blob in power_help.edits(bytes(data)).items():
            if off != power_help.HELP_TABLE_ROM:
                rom.expect_bytes(off, clean[off : off + len(blob)])
            rom.write_bytes(off, blob)
        icon_span = power_icons.apply(data, self.mkt)
        data[f87[0] : f87[1]] = outfit.recolor(
            data[f87[0] : f87[1]], self.outfit.mode.lower(),
            hue=self.outfit.hue_degrees, rgb=self.outfit.rgb, seed=context.seed,
        )  # fmt: skip

        # 3. Fixed loader into shared file 0x1A at FIXED_VA.
        e1a = FILE_TABLE + FILE_1A * 12
        f1a_start, f1a_end = _be32(data, e1a), _be32(data, e1a + 4)
        fixed_k0 = FIXED_VA & ~0x20000000
        if POOL_BASE + (f1a_end - f1a_start) > fixed_k0:
            raise PatchError("file 0x1A already reaches the fighter's fixed loader")
        fixed = sek[man["fixed_rom"] : man["fixed_rom"] + man["fixed_len"]]
        at = f1a_start + (fixed_k0 - POOL_BASE)
        if fixed_k0 + len(fixed) > POOL_END or set(data[f1a_end : at + len(fixed)]) != {0xFF}:
            raise PatchError("fighter fixed loader: pool tail not free")
        data[f1a_end:at] = bytes(at - f1a_end)  # padding inside the loaded file
        data[at : at + len(fixed)] = fixed
        rom.write_u32(e1a + 4, at + len(fixed))
        wrapper_jal = 0x0C000000 | ((man["load_wrapper"] >> 2) & 0x03FFFFFF)
        for site in LOAD_JAL_SITES:
            rom.expect_u32(site, wrapper_jal)

        return (
            f"fighter: {self.fighter} (imported from the MKT donor)",
            f"transplanted {moved} words; tail 0x{TAIL[0]:08X}-0x{TAIL[1]:08X}",
            (
                f"fixed loader 0x{fixed_k0:08X}-0x{fixed_k0 + len(fixed):08X}; "
                f"file 0x1A end 0x{f1a_end:X} -> 0x{at + len(fixed):X}"
            ),
            f"Power Ups icons: file 0x5D 0x{icon_span[0]:X}-0x{icon_span[1]:X}",
        )


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
    for off in _changed_words(image, clean, CLEAN_SIZE):
        if off in (0x10, 0x14):  # checksum, recomputed by the pipeline
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
