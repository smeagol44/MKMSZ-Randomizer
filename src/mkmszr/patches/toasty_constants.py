# ruff: noqa: E701, E702
"""Production-composition Toasty patch.

The patch contains no donor artwork or audio bytes. Callers supply translated
visual/audio assets through :class:\`ToastyAssets\`. The native feature is loaded
through file ID 0x1A into the reserved expansion pool and composes only with
already-owned production padding plus three guarded gameplay hooks.

The production probability is 80/1000 (8%). The earlier v47 manual integration
build used 500/1000 only as a fast validation diagnostic.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..allocations import ExpansionPoolAllocator
from ..data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM, RAW_FILE_LOADER_VA
from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext
from .box_indicator import BOX_REGION, BOX_REGION_END, BOX_REGION_ROM
from .inventory_boxes import SELECTOR_CAVE_BLOB, SELECTOR_CAVE_ROM, SELECTOR_CAVE_SIZE

# Runtime/presentation contract proven by v42/v44/v46.
COMMENT_DELAY_TICKS = 0x13
DEFAULT_PROBABILITY_PER_THOUSAND = 80
SLIDE_IN_TICKS = 3
HOLD_TICKS = 0x10
SLIDE_OUT_TICKS = 0x08
SLIDE_START_X_SHIFT = 78
SLIDE_STEP = 26
CUSTOM_PALETTE_SELECTOR = 0x11

RANDPER_VA = 0x80016008
REACTION_TRANSFER_VA = 0x8002E078
RAW_SOUND_VA = 0x80080A88
AUDIO_PREP_A_VA = 0x800008D4
AUDIO_PREP_B_VA = 0x800008DC
AUDIO_PARAM_VA = 0x802C1188
TOASTY_EVENT_ID = 52

QUALIFYING_REACTION_CALLBACKS = (
    0x800507D0,
    0x8005507C,
    0x800551A4,
    0x80055364,
    0x800554F4,
    0x800506A0,
    0x80050590,
)
QUALIFYING_REACTION_SELECTORS = (0x08, 0x0E, 0x12, 0x13, 0x14, 0x15, 0x17)
TARGET_REACTION_TABLE_ROM = 0x000A1D90

# Narrow successful/unblocked reaction seam and gameplay-HUD seams.
REACTION_HOOK_ROM = 0x0002EB28
REACTION_HOOK_VA = 0x8002DF28
REACTION_RETURN_VA = REACTION_HOOK_VA + 8
EXPECTED_REACTION_HOOK = bytes.fromhex("0C00B81E 03C02821")

HUD_HOOK_ROM = 0x0005D2E0
HUD_HOOK_VA = 0x8005C6E0
HUD_RETURN_VA = HUD_HOOK_VA + 8
EXPECTED_HUD_HOOK = bytes.fromhex("0C007AB9 A0C20046")

POST13_HOOK_ROM = 0x0005CCE0
POST13_RESUME_VA = 0x8005C0E8
EXPECTED_POST13_HOOK = bytes.fromhex("3C048029 8C841C10")

EXPANSION_FILE_ID = 0x1A
EXPANSION_FILE_ENTRY_ROM = FILE_TABLE_ROM + EXPANSION_FILE_ID * FILE_TABLE_ENTRY_SIZE

MODULE_K0 = 0x801B0000
MODULE_K1 = 0xA01B0000
MODULE_ROM = 0x00F68000
TITLE_ROM_START = 0x00F90000

INIT_LOADER_ROM = SELECTOR_CAVE_ROM + len(SELECTOR_CAVE_BLOB)
INIT_LOADER_VA = 0x80000000 + (INIT_LOADER_ROM - 0xC00)
INIT_LOADER_END = SELECTOR_CAVE_ROM + SELECTOR_CAVE_SIZE
CALL_TRAMP_ROM = BOX_REGION_END - 0x0C
CALL_TRAMP_VA = 0x80000000 + (CALL_TRAMP_ROM - 0xC00)
CALL_TRAMP_END = BOX_REGION_END

PICKUP_DESC_ROM = 0x000A257E
SSEQ_ENTRY_524 = 0x0097D528
PATCH_681_ROM = 0x0094875C
SUBPATCH_524_ROM = 0x0094B058
WAVE_133_ROM = 0x0094CDB0
EXPECTED_DESC_3B = bytes.fromhex("020c007f000000000000")
EXPECTED_ENTRY_524 = bytes.fromhex(
    "000002a900007f4000000078007800000000000c00113c7f811a123c00227820"
)
EXPECTED_PATCH_681 = bytes.fromhex("0100020c")
EXPECTED_SUBPATCH_524 = bytes.fromhex("646440013000007f0505008500017d00000a7f7f")
EXPECTED_WAVE_133 = bytes.fromhex(
    "000b832000001efa00000000fffffb50ffffffff00000000"
)

PATCH_68_ROM = 0x00947DC8
SUBPATCH_608_ROM = 0x0094B6E8
WAVE_533_ROM = 0x0094F330
PRED_533_ROM = 0x00972A38
EVENT_52_DATA_ROM = 0x009798B8
EVENT_52_PATCH_ROM = EVENT_52_DATA_ROM + 0x10
EXPECTED_EVENT_52 = bytes.fromhex(
    "0000000c00113c7f14123c0022227820000000d100007f400000007800780000"
)
EXPECTED_EVENT_52_PATCH = bytes.fromhex("000000d1")
TOASTY_EVENT_52_PATCH = bytes.fromhex("00000044")
EXPECTED_PATCH_68 = bytes.fromhex("01000260")
EXPECTED_SUBPATCH_608 = bytes.fromhex("006e40013700007f0000021500011b5804007f7f")
EXPECTED_WAVE_533 = bytes.fromhex(
    "0030717e000017500000000000000000ffffffff00000000"
)
EXPECTED_PRED_533_SHA256 = "54029ba413d939c0e219ab720d6830dc69ae48b60d26e1afa2fc89e1cd66646c"
MKMSZ_TBL_BASE = 0x009B0650
TARGET_WAVE_ID = 533
EXPECTED_AUDIO_CORRECTION = -2253

PIECE_GEOMETRY = (
    (7, 32), (64, 32), (7, 32),
    (7, 32), (64, 32), (7, 32),
    (7, 21), (64, 21), (7, 21),
)
DRAW_ORDER = (
    (0, 195, 135), (1, 202, 135), (2, 266, 135),
    (3, 195, 167), (4, 202, 167), (5, 266, 167),
    (6, 195, 199), (7, 202, 199), (8, 266, 199),
)
ALLOCATION_ORDER = (1, 4, 7, 0, 3, 6, 2, 5, 8)


@dataclass(frozen=True)
class ToastyAssets:
    """Translated assets supplied by a donor-aware caller.

    \`\`visual_slices\`\` are the nine already-padded CI8 slices in v38 order.
    \`\`palette_tlut\`\` is the 256-entry hardware-ready RGBA5551 TLUT.
    The audio fields are the confirmed donor subpatch/wave/predictor/sample.
    """

    visual_slices: tuple[bytes, ...]
    palette_tlut: bytes
    audio_subpatch: bytes
    audio_wave: bytes
    audio_predictor: bytes
    audio_sample: bytes

    def __post_init__(self) -> None:
        if len(self.visual_slices) != 9:
            raise ValueError("Toasty requires exactly nine visual slices")
        for index, ((width, height), data) in enumerate(
            zip(PIECE_GEOMETRY, self.visual_slices, strict=True)
        ):
            stride = (width + 31) & ~31
            expected = stride * height
            if len(data) != expected:
                raise ValueError(
                    f"Toasty slice {index} must be 0x{expected:X} bytes, got 0x{len(data):X}"
                )
        if len(self.palette_tlut) != 0x200:
            raise ValueError("Toasty palette TLUT must be exactly 0x200 bytes")
        if len(self.audio_subpatch) != 20:
            raise ValueError("Toasty donor subpatch must be exactly 20 bytes")
        if len(self.audio_wave) != 24:
            raise ValueError("Toasty donor waveform record must be exactly 24 bytes")
        if len(self.audio_predictor) != 264:
            raise ValueError("Toasty donor predictor book must be exactly 264 bytes")
        if len(self.audio_sample) != 0x816:
            raise ValueError("Toasty donor encoded sample must be exactly 0x816 bytes")
        correction = int.from_bytes(self.audio_wave[0x0C:0x10], "big", signed=True)
        if correction != EXPECTED_AUDIO_CORRECTION:
            raise ValueError(
                f"Toasty donor waveform correction must be {EXPECTED_AUDIO_CORRECTION}, got {correction}"
            )
