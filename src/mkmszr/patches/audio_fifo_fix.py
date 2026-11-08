"""Vanilla audio FIFO margin fix (audio speed-up / skip bug).

Each VI, the stock audio service (0x8007D4A8) first submits the previous PCM
buffer to the two-slot AI FIFO, then reads AI_LEN (head remainder only) and
sizes the next buffer as

    max(min, ((target - (AI_LEN >> 2) + reserve) & ~15) + 16)

with target 368, min 352 and reserve 320 from the boot-time audio config.
That keeps the FIFO nearly full with only ~1-3 ms of headroom. When the next
submission finds the FIFO still full, the buffer is dropped while the
synthesizer and WESS sequence have already advanced, so music runs ahead and
sound effects crackle. Under some timings (notably RMG's integer AI timebase,
where a 368-sample buffer is 20 Count shorter than one VI) small service
jitter tips the loop into sustained rejection bursts. Reproduced in the
unmodified vanilla ROM.

The boot audio setup (0x800012EC) writes the reserve into its config struct
with one immediate at VA 0x80001354. Lowering it from 320 to 272 keeps
~12 ms of queued audio while restoring three 16-sample steps of headroom.
"""

from __future__ import annotations

from ..rom import RomImage
from .base import PatchContext

RESERVE_IMMEDIATE_ROM = 0x00001F54
RESERVE_IMMEDIATE_VA = 0x80001354
STOCK_RESERVE = 320
FIXED_RESERVE = 272


def _addiu_v0_zero(value: int) -> int:
    return 0x24020000 | (value & 0xFFFF)  # addiu v0,zero,value


EXPECTED_WORD = _addiu_v0_zero(STOCK_RESERVE)  # 0x24020140
PATCHED_WORD = _addiu_v0_zero(FIXED_RESERVE)   # 0x24020110


class AudioFifoReservePatch:
    """Lower the stock audio-config reserve so the AI FIFO keeps headroom."""

    name = "audio-fifo-reserve"

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        del context
        rom.expect_u32(RESERVE_IMMEDIATE_ROM, EXPECTED_WORD)
        rom.write_u32(RESERVE_IMMEDIATE_ROM, PATCHED_WORD)
        return (
            (
                f"vanilla audio FIFO fix: config reserve {STOCK_RESERVE} -> {FIXED_RESERVE} "
                f"(VA 0x{RESERVE_IMMEDIATE_VA:08X} / ROM 0x{RESERVE_IMMEDIATE_ROM:08X})"
            ),
        )
