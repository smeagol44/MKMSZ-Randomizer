import hashlib

import pytest

from mkmszr.config import RandomizerConfig
from mkmszr.patcher import build_pipeline
from mkmszr.patches.base import PatchContext
from mkmszr.patches.temple_intro_audio import (
    AUDIO1_POOL,
    AUDIO2_POOL,
    CARRIER_DESC_ROM,
    CARRIER_EVENT_TRACK_ROM,
    CARRIER_PATCH_ROM,
    CARRIER_PRED_ROM,
    CARRIER_SUBPATCH_ROM,
    CARRIER_WAVE_ROM,
    EXPECTED_AUDIO2,
    EXPECTED_CARRIER_DESC,
    EXPECTED_CARRIER_EVENT_TRACK,
    EXPECTED_CARRIER_PATCH,
    EXPECTED_CARRIER_SUBPATCH,
    EXPECTED_CARRIER_WAVE,
    EXPECTED_LINE_A,
    EXPECTED_LINE_B,
    TEMPLE_AUDIO2_IMM_ROM,
    TEMPLE_LINE_A_IMM_ROM,
    TEMPLE_LINE_B_IMM_ROM,
    TEMPLE_SAMPLE_LIMIT,
    TEMPLE_SAMPLE_ROM,
    MktAudioClip,
    TempleIntroAudioAssets,
    TempleIntroAudioPatch,
    select_temple_intro_audio,
)
from mkmszr.rom import RomImage


def _seed_for_slot(slot: int) -> str:
    for index in range(1000):
        seed = f"TEMPLE-{index:04d}"
        if select_temple_intro_audio(seed)[0] == slot:
            return seed
    raise AssertionError(f"could not find representative seed for audio-{slot}")


def _fake_assets() -> TempleIntroAudioAssets:
    clips = []
    for key in (*AUDIO1_POOL, *AUDIO2_POOL):
        event = bytearray(32)
        event[0:4] = (123).to_bytes(4, "big")
        subpatch = bytearray(20)
        subpatch[10:12] = (321).to_bytes(2, "big")
        wave = bytearray(24)
        clips.append(
            MktAudioClip(
                key=key,
                event_id=1,
                patch_id=123,
                subpatch_id=2,
                wave_id=321,
                event_track=bytes(event),
                subpatch=bytes(subpatch),
                wave=bytes(wave),
                predictor=bytes(264),
                sample=(key.encode("ascii") + b"\0")[:32],
            )
        )
    return TempleIntroAudioAssets(tuple(clips))


def _fake_rom(monkeypatch: pytest.MonkeyPatch) -> RomImage:
    data = bytearray(16 * 1024 * 1024)
    data[TEMPLE_LINE_A_IMM_ROM:TEMPLE_LINE_A_IMM_ROM + 4] = EXPECTED_LINE_A
    data[TEMPLE_LINE_B_IMM_ROM:TEMPLE_LINE_B_IMM_ROM + 4] = EXPECTED_LINE_B
    data[TEMPLE_AUDIO2_IMM_ROM:TEMPLE_AUDIO2_IMM_ROM + 4] = EXPECTED_AUDIO2
    data[CARRIER_DESC_ROM:CARRIER_DESC_ROM + len(EXPECTED_CARRIER_DESC)] = EXPECTED_CARRIER_DESC
    data[
        CARRIER_EVENT_TRACK_ROM:CARRIER_EVENT_TRACK_ROM + len(EXPECTED_CARRIER_EVENT_TRACK)
    ] = EXPECTED_CARRIER_EVENT_TRACK
    data[CARRIER_PATCH_ROM:CARRIER_PATCH_ROM + 4] = EXPECTED_CARRIER_PATCH
    data[CARRIER_SUBPATCH_ROM:CARRIER_SUBPATCH_ROM + 20] = EXPECTED_CARRIER_SUBPATCH
    data[CARRIER_WAVE_ROM:CARRIER_WAVE_ROM + 24] = EXPECTED_CARRIER_WAVE
    data[CARRIER_PRED_ROM:CARRIER_PRED_ROM + 264] = bytes(264)
    data[TEMPLE_SAMPLE_ROM:TEMPLE_SAMPLE_LIMIT] = b"\xFF" * (
        TEMPLE_SAMPLE_LIMIT - TEMPLE_SAMPLE_ROM
    )
    monkeypatch.setattr(
        "mkmszr.patches.temple_intro_audio.EXPECTED_CARRIER_PRED_SHA256",
        hashlib.sha256(bytes(264)).hexdigest(),
    )
    return RomImage(data=data, _original=bytes(data))


def test_pools_match_approved_product_contract() -> None:
    assert AUDIO1_POOL == (
        "friendship",
        "choose-your-destiny",
        "excellent",
        "superb",
        "well-done",
        "liu-bike",
    )
    assert "friendship-alt" not in AUDIO1_POOL
    assert AUDIO2_POOL == (
        "raiden-bbb",
        "raiden-sss",
        "raiden-ttt",
        "robot-run",
        "shao-laugh",
    )


@pytest.mark.parametrize("slot", (1, 2))
def test_seed_selection_is_deterministic_and_stays_in_slot_pool(slot: int) -> None:
    seed = _seed_for_slot(slot)
    first = select_temple_intro_audio(seed)
    assert first == select_temple_intro_audio(seed)
    assert first[0] == slot
    assert first[1] in (AUDIO1_POOL if slot == 1 else AUDIO2_POOL)


def test_pipeline_skips_temple_audio_without_donor_assets() -> None:
    pipeline = build_pipeline(RandomizerConfig(seed="TEMPLE"))
    assert TempleIntroAudioPatch not in [type(patch) for patch in pipeline.patches]


def test_pipeline_adds_temple_audio_when_donor_assets_exist() -> None:
    pipeline = build_pipeline(
        RandomizerConfig(seed="TEMPLE"),
        temple_intro_audio_assets=_fake_assets(),
    )
    assert TempleIntroAudioPatch in [type(patch) for patch in pipeline.patches]


def test_audio1_seed_replaces_both_line_branches_and_preserves_audio2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _seed_for_slot(1)
    rom = _fake_rom(monkeypatch)
    TempleIntroAudioPatch(_fake_assets()).apply(rom, PatchContext(seed=seed))

    carrier = bytes.fromhex("2404020a")
    assert bytes(rom.data[TEMPLE_LINE_A_IMM_ROM:TEMPLE_LINE_A_IMM_ROM + 4]) == carrier
    assert bytes(rom.data[TEMPLE_LINE_B_IMM_ROM:TEMPLE_LINE_B_IMM_ROM + 4]) == carrier
    assert bytes(rom.data[TEMPLE_AUDIO2_IMM_ROM:TEMPLE_AUDIO2_IMM_ROM + 4]) == EXPECTED_AUDIO2


def test_audio2_seed_preserves_stock_line_alternation_and_replaces_laugh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _seed_for_slot(2)
    rom = _fake_rom(monkeypatch)
    TempleIntroAudioPatch(_fake_assets()).apply(rom, PatchContext(seed=seed))

    assert bytes(rom.data[TEMPLE_LINE_A_IMM_ROM:TEMPLE_LINE_A_IMM_ROM + 4]) == EXPECTED_LINE_A
    assert bytes(rom.data[TEMPLE_LINE_B_IMM_ROM:TEMPLE_LINE_B_IMM_ROM + 4]) == EXPECTED_LINE_B
    assert bytes(rom.data[TEMPLE_AUDIO2_IMM_ROM:TEMPLE_AUDIO2_IMM_ROM + 4]) == bytes.fromhex(
        "2404020a"
    )
