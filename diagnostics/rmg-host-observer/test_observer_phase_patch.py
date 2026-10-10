"""Synthetic RMG v04 phase probe: guarded injection, real C compile, opt-in parity."""

import os
import struct
import subprocess
import tempfile
from pathlib import Path

from observer_phase_patch import HEADER, apply


FAKE = """#include "mkmszr_trace.h"
void synthetic_read(void) {
        if (*value < ai->last_read)
}
void synthetic_write(void) {
        masked_write(&ai->regs[reg], value, mask);
        return;
    if (reg < AI_REGS_COUNT)
    {
        masked_write(&ai->regs[reg], value, mask);
    }
}
"""

C_SOURCE = r"""
#define _POSIX_C_SOURCE 200809L
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
struct rdram { uint32_t *dram; size_t dram_size; };
struct cp0 { uint32_t regs[32]; };
struct r4300_core { struct rdram *rdram; struct cp0 cp0; };
struct mi_controller { struct r4300_core *r4300; };
struct vi_controller { unsigned int clock, delay, expected_refresh_rate; };
enum {
    AI_DRAM_ADDR_REG, AI_LEN_REG, AI_CONTROL_REG,
    AI_STATUS_REG, AI_DACRATE_REG, AI_BITRATE_REG
};
enum { CP0_COUNT_REG = 9 };
struct ai_controller {
    struct mi_controller *mi;
    struct vi_controller *vi;
    uint32_t regs[6];
};
static uint32_t *r4300_cp0_regs(struct cp0 *p) { return p->regs; }
""" + HEADER + r"""
int main(void)
{
    struct rdram rd = {0};
    struct r4300_core core = {0};
    struct mi_controller mi = {0};
    struct vi_controller vi = {48681812, 811092, 60};
    struct ai_controller ai = {0};
    rd.dram_size = 8 * 1024 * 1024;
    rd.dram = calloc(1, rd.dram_size);
    if (rd.dram == NULL) return 31;
    rd.dram[0x000A7F60 / 4] = 1234;
    rd.dram[0x000C11E0 / 4] = 7;
    rd.dram[0x000A8FC8 / 4] = 48681812;
    core.rdram = &rd;
    core.cp0.regs[CP0_COUNT_REG] = 4567;
    mi.r4300 = &core;
    ai.mi = &mi;
    ai.vi = &vi;
    ai.regs[AI_DACRATE_REG] = 0x89F;
    mkmszr_phase_capture(&ai, 1u, 1280u);
    if (getenv("MKMSZR_TRACE_PHASE") != NULL &&
        strcmp(getenv("MKMSZR_TRACE_PHASE"), "1") == 0 &&
        getenv("MKMSZR_TRACE") != NULL)
    {
        const mkmszr_phase_record *rec;
        if (mkmszr_phase_store.total != 1u) return 32;
        rec = &mkmszr_phase_store.rows[0];
        if (rec->event != 1 || rec->guest_count != 4567 ||
            rec->field[0] != 1280 || rec->field[8] != 1234 ||
            rec->field[30] != 7 || rec->field[33] != 48681812)
            return 33;
    }
    else if (mkmszr_phase_store.total != 0u)
        return 34;
    free(rd.dram);
    return 0;
}
"""


def test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        work = Path(tmpdir)
        mock = work / "ai_controller.c"
        mock.write_text(FAKE)
        apply(mock)
        changed = mock.read_text()
        assert '#include "mkmszr_phase_trace.h"' in changed
        assert changed.count("mkmszr_phase_capture(") == 3
        assert "mkmszr_phase_capture(ai, 1u, *value)" in changed
        assert "mkmszr_phase_capture(ai, 2u, ai->regs[reg])" in changed
        assert "mkmszr_phase_capture(ai, 3u, ai->regs[reg])" in changed
        assert "mkmszr_phase_capture(ai, 4u, ai->regs[reg])" in changed
        assert (work / "mkmszr_phase_trace.h").read_text() == HEADER
        try:
            apply(mock)
        except RuntimeError as err:
            assert "already installed" in str(err)
        else:
            raise AssertionError("double source modification unexpectedly succeeded")

        source = work / "synthetic_phase.c"
        binary = work / "synthetic_phase"
        source.write_text(C_SOURCE)
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
             str(source), "-o", str(binary)],
            check=True,
        )

        offdir = work / "disabled"
        offdir.mkdir()
        subprocess.run(
            [str(binary)], check=True,
            env={**os.environ, "MKMSZR_TRACE": "1", "MKMSZR_TRACE_PHASE": "0",
                 "XDG_CACHE_HOME": str(offdir)},
        )
        assert not list(offdir.iterdir()), "disabled diagnostic wrote trace data"

        ondir = work / "enabled"
        ondir.mkdir()
        subprocess.run(
            [str(binary)], check=True,
            env={**os.environ, "MKMSZR_TRACE": "1", "MKMSZR_TRACE_PHASE": "1",
                 "XDG_CACHE_HOME": str(ondir)},
        )
        raw = (ondir / "mkmszr-phase-trace.bin").read_bytes()
        magic, version, record_size, saved, total, overwritten = struct.unpack_from(
            "=8sIIQQQ", raw
        )
        assert (magic, version, record_size, saved, total, overwritten) == (
            b"MZRPH4\0\0", 4, 160, 1, 1, 0
        )
        assert len(raw) == 40 + 160
        seq, ns, event, count, *fields = struct.unpack_from("=QQII34I", raw, 40)
        assert seq == 0 and ns > 0 and event == 1 and count == 4567
        assert fields[8] == 1234 and fields[30] == 7
        print("PASS: pin anchors, C header, real RDRAM reads, opt-out parity, ring export")


if __name__ == "__main__":
    test()
