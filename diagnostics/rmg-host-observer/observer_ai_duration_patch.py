"""Apply one opt-in AI DMA timing diagnostic to pinned RMG v0.9.0.

Default (flag absent) retains the upstream expression byte-for-byte. With
MKMSZR_AI_RATIONAL_DIAG=1 it carries fractional CP0 ticks across the full DMA
length instead of truncating the Count-per-byte quotient. It is an
EXPERIMENTAL EMULATOR PATCH, not a guest ROM/gameplay patch or validated fix.
"""
from pathlib import Path

SRC = Path("Source/3rdParty/mupen64plus-core/src/device/rcp/ai/ai_controller.c")
OLD = "    return ai->regs[AI_LEN_REG] * (cpu_counts_per_sec / (bytes_per_sample * samples_per_sec));\n"
NEW = r"""    /* MKMSZR diagnostic v03: preserve upstream default unless explicitly enabled.
       Do not change FIFO push/drop behavior, guest registers or the audio plugin. */
    {
        static int mkmszr_use_rational_ai = -1;
        if (mkmszr_use_rational_ai < 0)
        {
            const char *opt = getenv("MKMSZR_AI_RATIONAL_DIAG");
            mkmszr_use_rational_ai = (opt != NULL && strcmp(opt, "1") == 0);
        }
        if (mkmszr_use_rational_ai)
        {
            uint64_t denom = (uint64_t)bytes_per_sample * samples_per_sec;
            if (denom != 0)
                return (unsigned int)(((uint64_t)ai->regs[AI_LEN_REG] *
                                        cpu_counts_per_sec) / denom);
        }
    }
    return ai->regs[AI_LEN_REG] * (cpu_counts_per_sec / (bytes_per_sample * samples_per_sec));
"""


def apply(path: Path = SRC) -> None:
    text = path.read_text()
    if "mkmszr_use_rational_ai" in text:
        raise RuntimeError("rational AI duration diagnostic already installed")
    if '#include "mkmszr_trace.h"' not in text:
        raise RuntimeError("host observer v01 must be applied first")
    if text.count(OLD) != 1:
        raise RuntimeError("pinned get_dma_duration return expression not unique")
    path.write_text(text.replace(OLD, NEW))


if __name__ == "__main__":
    apply()
    print("MKMSZR v03 AI duration diagnostic installed; opt-in only")
