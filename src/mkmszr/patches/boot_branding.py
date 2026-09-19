"""Boot-screen branding and deterministic seed flavor phrase."""

from __future__ import annotations

from ..data.boot_phrases import BOOT_PHRASE_LINE_LIMIT, select_boot_phrase
from ..rom import RomImage
from .base import PatchContext

BOOT_TEXT_ROM = 0x000AF9BE
BOOT_TEXT_END = 0x000AFA24
PHRASE1_ROM = 0x000AF9E1
PHRASE2_ROM = 0x000AF9F5
BY_SMEAG_ROM = 0x000AFA09
BLANK_ROM = 0x000AFA78

LICENSE_ROM = 0x000AFA98
LICENSE_END = 0x000AFABC

EXPECTED_BOOT_TEXT = bytes.fromhex(
    "00007e31393937204d49445741592047414d455320494e432e00414c4c205249"
    "474854532052455345525645442e000000004d49445741592c204d4f5254414c"
    "204b4f4d4241542c000054484520445241474f4e2044455349474e2c20535542"
    "2d5a45524f00"
)
EXPECTED_LICENSE_TEXT = bytes.fromhex(
    "554e444552204c4943454e53452e00004c4943454e534544204259204e494e54"
    "454e444f"
)

# Each instruction is an existing addiu a0,a0,low16(string_va) in the boot
# legal-text routine. The first two original title pointers remain untouched.
BOOT_POINTER_PATCHES = (
    (0x0007A22C, 0x2484EDC0, 0x2484EDBE),  # RANDOMIZER
    (0x0007A250, 0x2484EDD8, 0x2484EDC9),  # copyright
    (0x0007A274, 0x2484EDF0, 0x2484EE78),  # blank
    (0x0007A298, 0x2484EE08, 0x2484EE78),  # blank
    (0x0007A2BC, 0x2484EE24, 0x2484EDE1),  # phrase line 1
    (0x0007A2E0, 0x2484EE3C, 0x2484EDF5),  # phrase line 2
    (0x0007A304, 0x2484EE54, 0x2484EE78),  # blank
    (0x0007A328, 0x2484EE68, 0x2484EE78),  # blank
    (0x0007A34C, 0x2484EE80, 0x2484EE09),  # BY SMEAG
    (0x0007A370, 0x2484EE98, 0x2484EE78),  # blank
    (0x0007A394, 0x2484EEA8, 0x2484EE98),  # LICENSED BY NINTENDO
)


def _slot(text: str) -> bytes:
    encoded = text.encode("ascii")
    if len(encoded) > BOOT_PHRASE_LINE_LIMIT:
        raise ValueError(
            f"boot phrase line exceeds {BOOT_PHRASE_LINE_LIMIT} characters: {text!r}"
        )
    return encoded + b"\x00" + bytes(BOOT_PHRASE_LINE_LIMIT - len(encoded))


def build_boot_text(seed: str | None) -> tuple[bytes, tuple[str, str]]:
    phrase = select_boot_phrase(seed)
    region = bytearray(BOOT_TEXT_END - BOOT_TEXT_ROM)

    def write_string(offset: int, text: str) -> None:
        encoded = text.encode("ascii") + b"\x00"
        start = offset - BOOT_TEXT_ROM
        region[start : start + len(encoded)] = encoded

    write_string(0x000AF9BE, "RANDOMIZER")
    write_string(0x000AF9C9, "~1997 MIDWAY GAMES INC.")
    region[PHRASE1_ROM - BOOT_TEXT_ROM : PHRASE1_ROM - BOOT_TEXT_ROM + 20] = _slot(
        phrase[0]
    )
    region[PHRASE2_ROM - BOOT_TEXT_ROM : PHRASE2_ROM - BOOT_TEXT_ROM + 20] = _slot(
        phrase[1]
    )
    write_string(BY_SMEAG_ROM, "BY SMEAG")
    return bytes(region), phrase


LICENSE_TEXT = b"LICENSED BY NINTENDO\x00" + bytes(
    LICENSE_END - LICENSE_ROM - len(b"LICENSED BY NINTENDO\x00")
)


class BootBrandingPatch:
    """Install MKMSZR boot branding and the seed-selected two-line message."""

    name = "boot-branding"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        rom.expect_bytes(BOOT_TEXT_ROM, EXPECTED_BOOT_TEXT)
        rom.expect_bytes(LICENSE_ROM, EXPECTED_LICENSE_TEXT)
        # The empty-line pointers intentionally target the byte immediately
        # after BoxIndicatorPatch's code cave, making pipeline order explicit.
        rom.expect_bytes(BLANK_ROM, b"\x00")
        for offset, expected, _replacement in BOOT_POINTER_PATCHES:
            rom.expect_u32(offset, expected)

        boot_text, phrase = build_boot_text(context.seed)
        rom.write_bytes(BOOT_TEXT_ROM, boot_text)
        rom.write_bytes(LICENSE_ROM, LICENSE_TEXT)
        for offset, _expected, replacement in BOOT_POINTER_PATCHES:
            rom.write_u32(offset, replacement)

        phrase_note = phrase[0] if not phrase[1] else f"{phrase[0]} / {phrase[1]}"
        return (
            "brands the legal screen as MKMSZ Randomizer while retaining Midway/Nintendo lines",
            "adds BY SMEAG in the lower portion",
            f"seed boot phrase: {phrase_note}",
        )
