"""Synthetic v03 smoke: guarded injection and exact 551-vs-rational DMA timings."""
import os
import subprocess
import tempfile
from pathlib import Path

from observer_ai_duration_patch import NEW, OLD, apply

HEADER = r"""
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
enum { AI_LEN_REG=1, AI_DACRATE_REG=4 };
struct vi_controller {
    unsigned int clock, expected_refresh_rate, delay;
};
struct ai_controller {
    unsigned int regs[6];
    struct vi_controller* vi;
};
"""
ORIGINAL_FUNCTION = r"""
static unsigned int get_dma_duration(struct ai_controller* ai)
{
    unsigned int samples_per_sec = ai->vi->clock / (1 + ai->regs[AI_DACRATE_REG]);
    unsigned int bytes_per_sample = 4;
    unsigned int cpu_counts_per_sec = ai->vi->delay == 0 ? ai->vi->clock : ai->vi->delay * ai->vi->expected_refresh_rate;
""" + OLD + "}\n"
MAIN = r"""
int main(void)
{
    struct vi_controller vi = { 48681812u, 60u, 811092u };
    struct ai_controller ai = {{0}, &vi};
    ai.regs[AI_DACRATE_REG] = 2207u;
    ai.regs[AI_LEN_REG] = 1472u; /* 368 frames, stereo 16-bit */
    printf("%u\n",get_dma_duration(&ai));
    return 0;
}
"""


def test() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        source = tmp / "ai_controller.c"
        source.write_text('#include "mkmszr_trace.h"\n' + ORIGINAL_FUNCTION)
        apply(source)
        modified = source.read_text()
        assert modified.count(OLD) == 1
        assert modified.count(NEW) == 1
        try:
            apply(source)
        except RuntimeError as err:
            assert "already installed" in str(err)
        else:
            raise AssertionError("double-install unexpectedly allowed")
        c = tmp / "timing.c"
        c.write_text(HEADER + ORIGINAL_FUNCTION.replace(OLD, NEW) + MAIN)
        binary = tmp / "timing"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
             str(c), "-o", str(binary)],
            check=True,
        )
        unmodified = subprocess.check_output(
            [str(binary)], env={**os.environ, "MKMSZR_AI_RATIONAL_DIAG": "0"},
            text=True,
        ).strip()
        missing = subprocess.check_output(
            [str(binary)], env={k: v for k, v in os.environ.items()
                                if k != "MKMSZR_AI_RATIONAL_DIAG"},
            text=True,
        ).strip()
        opt_in = subprocess.check_output(
            [str(binary)], env={**os.environ, "MKMSZR_AI_RATIONAL_DIAG": "1"},
            text=True,
        ).strip()
        assert (unmodified, missing, opt_in) == ("811072", "811072", "812306")
        print("PASS: exact pinned-source injection, disabled parity,"
              " and fractional DMA calculation")


if __name__ == "__main__":
    test()
