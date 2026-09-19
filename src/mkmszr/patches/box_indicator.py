"""Runtime-confirmed native gameplay indicator for the active inventory box."""

from __future__ import annotations

from ..rom import RomImage
from .base import PatchContext

HUD_HOOK_ROM = 0x0005D9CC
EXPECTED_HUD_CALL = 0x0C007AB9  # jal 0x8001EAE4

BOX_REGION_ROM = 0x000AFA24
BOX_REGION_END = 0x000AFA98
BOX_WRAPPER_ROM = BOX_REGION_ROM
BOX_WRAPPER_VA = 0x800AEE24
BOX_TEXT_ROM = 0x000AFA80
BOX_TEXT_VA = 0x800AEE80

EXPECTED_BOX_REGION = bytes.fromhex(
    "414e4420414c4c204f5448455220434841524143544552004e414d4553204152"
    "452054524144454d41524b53204f46004d49445741592047414d455320494e43"
    "2e0000004449535452494255544544204259204d4944574159000000484f4d45"
    "20454e5445525441494e4d454e5420494e432e00"
)

# Runtime-confirmed wrapper from the v2 presentation proof. It preserves the
# displaced HUD call, reads active-box index bits from 0x800A60EB, rewrites the
# digit in "BOX 1 OF 4", then submits native text at x=230/y=210.
BOX_WRAPPER = bytes.fromhex(
    "27bdffe8afbf00140c007ab9000000003c08800a910960eb252900313504ee80"
    "a0890004240500e6240600d2240700023c08800b25081e20afa800100c01cf9d"
    "000000008fbf001427bd001803e0000800000000"
)

BOX_TEXT = b"BOX 1 OF 4\x00"
BOX_REGION = bytearray(BOX_REGION_END - BOX_REGION_ROM)
BOX_REGION[: len(BOX_WRAPPER)] = BOX_WRAPPER
BOX_REGION[BOX_TEXT_ROM - BOX_REGION_ROM : BOX_TEXT_ROM - BOX_REGION_ROM + len(BOX_TEXT)] = BOX_TEXT
BOX_REGION = bytes(BOX_REGION)

BOX_HOOK_CALL = 0x0C02BB89  # jal 0x800AEE24


class BoxIndicatorPatch:
    """Draw the active four-box inventory index through the native HUD text path."""

    name = "box-indicator"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context
        rom.expect_u32(HUD_HOOK_ROM, EXPECTED_HUD_CALL)
        rom.expect_bytes(BOX_REGION_ROM, EXPECTED_BOX_REGION)

        rom.write_bytes(BOX_REGION_ROM, BOX_REGION)
        rom.write_u32(HUD_HOOK_ROM, BOX_HOOK_CALL)

        return (
            "draws persistent native 'BOX n OF 4' at x=230, y=210",
            "active digit reads the existing four-box state; no new state is introduced",
        )
