"""Seeded MKT-backed Temple intro audio replacement."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ..data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM
from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext

RNG_DOMAIN = b"MKMSZR:TEMPLE-INTRO-AUDIO:V1\0"

AUDIO1_POOL = (
    "friendship",
    "choose-your-destiny",
    "excellent",
    "superb",
    "well-done",
    "liu-bike",
)
AUDIO2_POOL = (
    "raiden-bbb",
    "raiden-sss",
    "raiden-ttt",
    "robot-run",
    "shao-laugh",
)

TEMPLE_LINE_A_IMM_ROM = 0x000CB274
TEMPLE_LINE_B_IMM_ROM = 0x000CB280
TEMPLE_AUDIO2_IMM_ROM = 0x000CB2F8
EXPECTED_LINE_A = bytes.fromhex("24040041")
EXPECTED_LINE_B = bytes.fromhex("24040042")
EXPECTED_AUDIO2 = bytes.fromhex("24040043")

# Temple owns stock descriptors 0x41/0x42/0x43 and their one-shot SSEQ
# events 123/124/125. Keep the descriptor IDs stock and replace only the
# selected Temple event(s), so unrelated gameplay that reaches other
# descriptors cannot be hijacked by this feature.
TEMPLE_EVENT_A_ID = 123
TEMPLE_EVENT_B_ID = 124
TEMPLE_EVENT_AUDIO2_ID = 125
TEMPLE_EVENT_A_ROM = 0x0097A200
TEMPLE_EVENT_B_ROM = 0x0097A220
TEMPLE_EVENT_AUDIO2_ROM = 0x0097A240
EXPECTED_TEMPLE_EVENT_A = bytes.fromhex(
    "0000011800007f4000000078007800000000000c00113c7f8170123c00227820"
)
EXPECTED_TEMPLE_EVENT_B = bytes.fromhex(
    "0000011900007f4000000078007800000000000c00113c7f8229123c00227820"
)
EXPECTED_TEMPLE_EVENT_AUDIO2 = bytes.fromhex(
    "0000011a00007f4000000078007800000000000c00113c7f8347123c00227820"
)

# Isolated metadata host established by the full stock-SSEQ liveness audit.
# Event 329 has no descriptor owner. Across all 590 SSEQ entries / 882 tracks,
# patch 486 appears only as event 329's initial patch and never in an in-stream
# program change. Patch 486 uniquely owns subpatch 329, which uniquely owns
# waveform 319. Production reuses only this dead metadata chain.
ISOLATED_EVENT_ID = 329
ISOLATED_PATCH_ID = 486
ISOLATED_SUBPATCH_ID = 329
ISOLATED_WAVE_ID = 319

PATCH_BASE_ROM = 0x00947CB8
SUBPATCH_BASE_ROM = 0x00948768
WAVE_BASE_ROM = 0x0094C138
PRED_BASE_ROM = 0x00950490
ISOLATED_PATCH_ROM = PATCH_BASE_ROM + ISOLATED_PATCH_ID * 4
ISOLATED_SUBPATCH_ROM = SUBPATCH_BASE_ROM + ISOLATED_SUBPATCH_ID * 20
ISOLATED_WAVE_ROM = WAVE_BASE_ROM + ISOLATED_WAVE_ID * 24
ISOLATED_PRED_ROM = PRED_BASE_ROM + ISOLATED_WAVE_ID * 264

EXPECTED_ISOLATED_PATCH = bytes.fromhex("01000149")
EXPECTED_ISOLATED_SUBPATCH = bytes.fromhex(
    "647340003c00007f0505013f00017d00000a7f7f"
)
EXPECTED_ISOLATED_WAVE = bytes.fromhex(
    "00183232000019aa00000000fffffb50ffffffff00000000"
)
EXPECTED_ISOLATED_PRED_SHA256 = (
    "53b481faa8d55595a2496ef453c41cff02ec4ca793b7597972d56ccdf100136d"
)

# Superseded global carrier. These constants are retained only for regression
# tests proving that the Bridge/Prison-reachable stock route remains untouched.
LEGACY_CARRIER_DESC_ROM = 0x000A3794
LEGACY_CARRIER_EVENT_TRACK_ROM = 0x0097C7D8
LEGACY_CARRIER_PATCH_ROM = 0x009485C4
LEGACY_CARRIER_SUBPATCH_ROM = 0x0094A860
LEGACY_CARRIER_WAVE_ROM = 0x0094DFD8
EXPECTED_LEGACY_CARRIER_DESC = bytes.fromhex("01a6007f000000000000")
EXPECTED_LEGACY_CARRIER_EVENT_TRACK = bytes.fromhex(
    "0000024300007f4000000078007800000000000c00113c7f8159123c00227820"
)
EXPECTED_LEGACY_CARRIER_PATCH = bytes.fromhex("010001a6")
EXPECTED_LEGACY_CARRIER_SUBPATCH = bytes.fromhex(
    "647340004000007f0505019c00017d00000a7f7f"
)
EXPECTED_LEGACY_CARRIER_WAVE = bytes.fromhex(
    "001f31a20000115600000000fffffb50ffffffff00000000"
)

MKMSZ_TBL_BASE = 0x009B0650
TEMPLE_SAMPLE_ROM = 0x00F6BDF0
TEMPLE_SAMPLE_LIMIT = 0x00F6D810


@dataclass(frozen=True)
class MktAudioClip:
    key: str
    event_id: int
    patch_id: int
    subpatch_id: int
    wave_id: int
    event_track: bytes
    subpatch: bytes
    wave: bytes
    predictor: bytes
    sample: bytes


@dataclass(frozen=True)
class TempleIntroAudioAssets:
    clips: tuple[MktAudioClip, ...]

    def clip(self, key: str) -> MktAudioClip:
        for clip in self.clips:
            if clip.key == key:
                return clip
        raise KeyError(key)


def select_temple_intro_audio(seed: str) -> tuple[int, str]:
    """Return the selected Temple slot and clip key from an isolated seed domain."""

    if not seed:
        raise ValueError("Temple intro audio selection requires a non-empty seed")
    seed_bytes = seed.encode("utf-8")
    slot_digest = hashlib.sha256(RNG_DOMAIN + b"SLOT\0" + seed_bytes).digest()
    slot = 1 + int.from_bytes(slot_digest[:8], "big") % 2
    pool = AUDIO1_POOL if slot == 1 else AUDIO2_POOL
    clip_digest = hashlib.sha256(
        RNG_DOMAIN + f"AUDIO-{slot}\0".encode("ascii") + seed_bytes
    ).digest()
    key = pool[int.from_bytes(clip_digest[:8], "big") % len(pool)]
    return slot, key


class TempleIntroAudioPatch:
    """Replace exactly one Temple intro audio position with one seeded MKT clip."""

    name = "temple-intro-audio"

    def __init__(self, assets: TempleIntroAudioAssets):
        self.assets = assets

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        if not context.seed:
            return ("MKT Temple intro audio skipped because no seed was supplied",)

        slot, key = select_temple_intro_audio(context.seed)
        try:
            clip = self.assets.clip(key)
        except KeyError as exc:
            raise PatchError(f"MKT Temple intro audio asset missing: {key}") from exc

        rom.expect_bytes(TEMPLE_LINE_A_IMM_ROM, EXPECTED_LINE_A)
        rom.expect_bytes(TEMPLE_LINE_B_IMM_ROM, EXPECTED_LINE_B)
        rom.expect_bytes(TEMPLE_AUDIO2_IMM_ROM, EXPECTED_AUDIO2)
        rom.expect_bytes(TEMPLE_EVENT_A_ROM, EXPECTED_TEMPLE_EVENT_A)
        rom.expect_bytes(TEMPLE_EVENT_B_ROM, EXPECTED_TEMPLE_EVENT_B)
        rom.expect_bytes(TEMPLE_EVENT_AUDIO2_ROM, EXPECTED_TEMPLE_EVENT_AUDIO2)
        rom.expect_bytes(ISOLATED_PATCH_ROM, EXPECTED_ISOLATED_PATCH)
        rom.expect_bytes(ISOLATED_SUBPATCH_ROM, EXPECTED_ISOLATED_SUBPATCH)
        rom.expect_bytes(ISOLATED_WAVE_ROM, EXPECTED_ISOLATED_WAVE)
        pred = bytes(rom.data[ISOLATED_PRED_ROM:ISOLATED_PRED_ROM + 264])
        if hashlib.sha256(pred).hexdigest() != EXPECTED_ISOLATED_PRED_SHA256:
            raise PatchError("Temple intro audio isolated-host predictor guard failed")

        sample_end = TEMPLE_SAMPLE_ROM + len(clip.sample)
        if sample_end > TEMPLE_SAMPLE_LIMIT:
            raise PatchError("Temple intro donor sample exceeds production allocation")
        rom.expect_bytes(
            TEMPLE_SAMPLE_ROM,
            b"\xFF" * (TEMPLE_SAMPLE_LIMIT - TEMPLE_SAMPLE_ROM),
        )
        for file_id in range(0xAC):
            entry = FILE_TABLE_ROM + file_id * FILE_TABLE_ENTRY_SIZE
            start = rom.read_u32(entry)
            end = rom.read_u32(entry + 4)
            if start and end and end > start and not (
                end <= TEMPLE_SAMPLE_ROM or start >= TEMPLE_SAMPLE_LIMIT
            ):
                raise PatchError(
                    f"Temple intro audio allocation overlaps file 0x{file_id:02X}"
                )

        donor_event = bytearray(clip.event_track)
        if len(donor_event) != len(EXPECTED_TEMPLE_EVENT_A):
            raise PatchError("Temple intro donor event track does not fit Temple event")
        donor_event[0:4] = ISOLATED_PATCH_ID.to_bytes(4, "big")

        donor_subpatch = bytearray(clip.subpatch)
        if len(donor_subpatch) != 20:
            raise PatchError("Temple intro donor subpatch has unexpected size")
        donor_subpatch[0x0A:0x0C] = ISOLATED_WAVE_ID.to_bytes(2, "big")

        donor_wave = bytearray(clip.wave)
        if len(donor_wave) != 24 or len(clip.predictor) != 264:
            raise PatchError("Temple intro donor waveform metadata has unexpected size")
        donor_wave[0:4] = (TEMPLE_SAMPLE_ROM - MKMSZ_TBL_BASE).to_bytes(4, "big")

        rom.write_bytes(ISOLATED_SUBPATCH_ROM, bytes(donor_subpatch))
        rom.write_bytes(ISOLATED_WAVE_ROM, bytes(donor_wave))
        rom.write_bytes(ISOLATED_PRED_ROM, clip.predictor)
        rom.write_bytes(TEMPLE_SAMPLE_ROM, clip.sample)

        if slot == 1:
            rom.write_bytes(TEMPLE_EVENT_A_ROM, bytes(donor_event))
            rom.write_bytes(TEMPLE_EVENT_B_ROM, bytes(donor_event))
            untouched = "audio-2 stock descriptor 0x43 / event 125 retained"
        else:
            rom.write_bytes(TEMPLE_EVENT_AUDIO2_ROM, bytes(donor_event))
            untouched = "audio-1 stock descriptors 0x41/0x42 / events 123/124 retained"

        return (
            f"seeded Temple audio-{slot}: {key}",
            untouched,
            (
                f"selected donor sample ROM 0x{TEMPLE_SAMPLE_ROM:08X}.."
                f"0x{sample_end - 1:08X}; isolated host 486 -> 329 -> 319"
            ),
        )
