import pytest

from mkmszr.cli import _build_parser
from mkmszr.config import RandomizerConfig
from mkmszr.errors import PatchError
from mkmszr.patcher import build_pipeline
from mkmszr.patches.audio_fifo_fix import (
    EXPECTED_WORD,
    FIXED_RESERVE,
    PATCHED_WORD,
    RESERVE_IMMEDIATE_ROM,
    STOCK_RESERVE,
    AudioFifoReservePatch,
)
from mkmszr.patches.base import PatchContext
from mkmszr.rom import RomImage


def _rom(word: int) -> RomImage:
    data = bytearray(RESERVE_IMMEDIATE_ROM + 0x10)
    data[RESERVE_IMMEDIATE_ROM : RESERVE_IMMEDIATE_ROM + 4] = word.to_bytes(4, "big")
    return RomImage(data=data, _original=bytes(data))


def test_reserve_immediate_encoding() -> None:
    assert (STOCK_RESERVE, FIXED_RESERVE) == (320, 272)
    assert EXPECTED_WORD == 0x24020140  # addiu v0,zero,0x140
    assert PATCHED_WORD == 0x24020110   # addiu v0,zero,0x110
    # Keeps the stock 16-sample quantization of the sizing formula.
    assert FIXED_RESERVE % 16 == 0


def test_patch_rewrites_only_the_guarded_immediate() -> None:
    rom = _rom(EXPECTED_WORD)
    AudioFifoReservePatch().apply(rom, PatchContext())
    assert rom.read_u32(RESERVE_IMMEDIATE_ROM) == PATCHED_WORD
    assert rom.changed_spans() == ((RESERVE_IMMEDIATE_ROM + 3, RESERVE_IMMEDIATE_ROM + 4),)


def test_patch_refuses_unexpected_source() -> None:
    with pytest.raises(PatchError):
        AudioFifoReservePatch().apply(_rom(0x24020120), PatchContext())


def test_fix_is_default_on_and_can_be_disabled() -> None:
    def has_fix(config: RandomizerConfig) -> bool:
        return any(isinstance(p, AudioFifoReservePatch) for p in build_pipeline(config).patches)

    assert RandomizerConfig().audio_fifo_fix is True
    assert has_fix(RandomizerConfig(seed="AUDIO"))
    assert not has_fix(RandomizerConfig(seed="AUDIO", audio_fifo_fix=False))
    with pytest.raises(ValueError):
        RandomizerConfig(audio_fifo_fix="no")  # type: ignore[arg-type]


def test_cli_exposes_opt_out_flag() -> None:
    parser = _build_parser()
    assert parser.parse_args(["a.z64", "b.z64"]).no_audio_fifo_fix is False
    assert parser.parse_args(["a.z64", "b.z64", "--no-audio-fifo-fix"]).no_audio_fifo_fix is True
