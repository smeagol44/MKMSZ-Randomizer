"""Boot-screen branding and deterministic seed flavor phrase."""

from __future__ import annotations

from ..data.boot_phrases import select_boot_phrase
from ..rom import RomImage
from .base import PatchContext
from .title_branding import edition_text

BOOT_TEXT_ROM = 0x000AF998
BOOT_TEXT_END = 0x000AFA24

TITLE_LINE_ROM = 0x000AF998
RANDOMIZER_LINE_ROM = 0x000AF9B3
EDITION_LINE_ROM = 0x000AF9C7
COPYRIGHT_LINE_ROM = 0x000AF9DC
PHRASE1_ROM = 0x000AF9F1
PHRASE2_ROM = 0x000AFA05
BY_SMEAG_ROM = 0x000AFA19
BLANK_ROM = 0x000AFA22

LICENSE_ROM = 0x000AFA98
LICENSE_END = 0x000AFABC

EXPECTED_BOOT_TEXT = bytes.fromhex(
    "4d4f5254414c204b4f4d4241545e204d5954484f4c4f474945533a00"
    "5355422d5a45524f5b000000"
    "7e31393937204d49445741592047414d455320494e432e00"
    "414c4c205249474854532052455345525645442e00000000"
    "4d49445741592c204d4f5254414c204b4f4d4241542c0000"
    "54484520445241474f4e2044455349474e2c205355422d5a45524f00"
)
EXPECTED_LICENSE_TEXT = bytes.fromhex(
    "554e444552204c4943454e53452e00004c4943454e534544204259204e494e54"
    "454e444f"
)

# Legal-screen text encoding uses stock special glyphs:
#   ^ -> registered sign, ~ -> copyright sign.
TITLE_LINE = "MORTAL KOMBAT^ MYTHOLOGIES"
RANDOMIZER_LINE = "R A N D O M I Z E R"
COPYRIGHT_LINE = "~2026 LA PAVADA INC."
BY_SMEAG_LINE = "BY SMEAG"
LICENSE_LINE = "NOT LICENSED BY NINTENDO"

# The stock legal screen has 13 text submissions. Repoint them to the packed
# MKMSZR layout while preserving the original vertical spacing:
# title, randomizer, edition, copyright, 2 blanks, 2 joke lines,
# 2 blanks, BY SMEAG, blank, NOT LICENSED BY NINTENDO.
BOOT_POINTER_PATCHES = (
    (0x0007A1E4, 0x2484ED98, 0x2484ED98),  # MORTAL KOMBAT^ MYTHOLOGIES
    (0x0007A208, 0x2484EDB4, 0x2484EDB3),  # R A N D O M I Z E R
    (0x0007A22C, 0x2484EDC0, 0x2484EDC7),  # <CHAR> EDITION
    (0x0007A250, 0x2484EDD8, 0x2484EDDC),  # copyright
    (0x0007A274, 0x2484EDF0, 0x2484EE22),  # blank
    (0x0007A298, 0x2484EE08, 0x2484EE22),  # blank
    (0x0007A2BC, 0x2484EE24, 0x2484EDF1),  # phrase line 1
    (0x0007A2E0, 0x2484EE3C, 0x2484EE05),  # phrase line 2
    (0x0007A304, 0x2484EE54, 0x2484EE22),  # blank
    (0x0007A328, 0x2484EE68, 0x2484EE22),  # blank
    (0x0007A34C, 0x2484EE80, 0x2484EE19),  # BY SMEAG
    (0x0007A370, 0x2484EE98, 0x2484EE22),  # blank
    (0x0007A394, 0x2484EEA8, 0x2484EE98),  # NOT LICENSED BY NINTENDO
)


def _write_slot(
    region: bytearray,
    address: int,
    size: int,
    text: str,
) -> None:
    encoded = text.encode("ascii")
    if len(encoded) + 1 > size:
        raise ValueError(
            f"boot legal line exceeds {size - 1} characters: {text!r}"
        )
    start = address - BOOT_TEXT_ROM
    region[start : start + size] = encoded + b"\x00" + bytes(size - len(encoded) - 1)


def build_boot_text(
    seed: str | None,
    edition_name: str | None = None,
) -> tuple[bytes, tuple[str, str]]:
    phrase = select_boot_phrase(seed)
    region = bytearray(BOOT_TEXT_END - BOOT_TEXT_ROM)

    _write_slot(region, TITLE_LINE_ROM, 27, TITLE_LINE)
    _write_slot(region, RANDOMIZER_LINE_ROM, 20, RANDOMIZER_LINE)
    _write_slot(region, EDITION_LINE_ROM, 21, edition_text(edition_name))
    _write_slot(region, COPYRIGHT_LINE_ROM, 21, COPYRIGHT_LINE)
    _write_slot(region, PHRASE1_ROM, 20, phrase[0])
    _write_slot(region, PHRASE2_ROM, 20, phrase[1])
    _write_slot(region, BY_SMEAG_ROM, 9, BY_SMEAG_LINE)

    return bytes(region), phrase


LICENSE_TEXT = LICENSE_LINE.encode("ascii") + b"\x00" + bytes(
    LICENSE_END - LICENSE_ROM - len(LICENSE_LINE.encode("ascii")) - 1
)


class BootBrandingPatch:
    """Install MKMSZR legal-screen branding and the seeded two-line joke."""

    name = "boot-branding"

    def __init__(self, edition_name: str | None = None):
        self.edition_name = edition_name

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        rom.expect_bytes(BOOT_TEXT_ROM, EXPECTED_BOOT_TEXT)
        rom.expect_bytes(LICENSE_ROM, EXPECTED_LICENSE_TEXT)
        for offset, expected, _replacement in BOOT_POINTER_PATCHES:
            rom.expect_u32(offset, expected)

        boot_text, phrase = build_boot_text(context.seed, self.edition_name)
        rom.write_bytes(BOOT_TEXT_ROM, boot_text)
        rom.write_bytes(LICENSE_ROM, LICENSE_TEXT)
        for offset, _expected, replacement in BOOT_POINTER_PATCHES:
            rom.write_u32(offset, replacement)

        phrase_note = phrase[0] if not phrase[1] else f"{phrase[0]} / {phrase[1]}"
        return (
            "brands the legal screen as MORTAL KOMBAT MYTHOLOGIES RANDOMIZER",
            f"uses {edition_text(self.edition_name)} on the legal screen",
            "credits BY SMEAG / NOT LICENSED BY NINTENDO",
            f"seed boot phrase: {phrase_note}",
        )
