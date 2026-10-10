"""Add opt-in, host-only native audio-state provenance to pinned RMG observer v02.

This is NOT an audio correction. It reads physical RDRAM only at existing AI_LEN
reads and logs existing DAC/control/bitrate writes. No new guest MMIO reads,
Count updates, breakpoints, ROM patch, or changes to DMA/PCM scheduling.
"""
from pathlib import Path

SRC = Path("Source/3rdParty/mupen64plus-core/src/device/rcp/ai/ai_controller.c")
HEADER = r"""
/* MKMSZR phase provenance v04: opt-in; separate bounded host ring. */
#ifndef MKMSZR_PHASE_TRACE_V04
#define MKMSZR_PHASE_TRACE_V04
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MKMSZR_PHASE_CAP 32768u
#define MKMSZR_PHASE_FIELDS 34u

typedef struct {
    uint64_t sequence, monotonic_ns;
    uint32_t event, guest_count;
    uint32_t field[MKMSZR_PHASE_FIELDS];
} mkmszr_phase_record; /* 160 bytes */

typedef struct {
    char magic[8];
    uint32_t version, record_size;
    uint64_t saved, total, overwritten;
} mkmszr_phase_header;

typedef char mkmszr_phase_record_size_must_be_160[
    sizeof(mkmszr_phase_record) == 160 ? 1 : -1
];

static struct {
    mkmszr_phase_record rows[MKMSZR_PHASE_CAP];
    uint64_t total;
    int initialized, enabled;
} mkmszr_phase_store;

/* KSEG0/KSEG1 aliases to validated 8-MiB physical RDRAM. No MMIO. */
static uint32_t mkmszr_phase_word(const struct ai_controller *ai, uint32_t va)
{
    const struct rdram *rd;
    uint32_t phys;
    if (ai == NULL || ai->mi == NULL || ai->mi->r4300 == NULL)
        return 0;
    if ((va & UINT32_C(0xE0000000)) != UINT32_C(0x80000000) &&
        (va & UINT32_C(0xE0000000)) != UINT32_C(0xA0000000))
        return 0;
    rd = ai->mi->r4300->rdram;
    if (rd == NULL || rd->dram == NULL)
        return 0;
    phys = va & UINT32_C(0x1FFFFFFF);
    if ((phys & 3u) != 0 || phys > UINT32_C(0x007FFFFC) ||
        (size_t)phys + 4u > rd->dram_size)
        return 0;
    return rd->dram[phys >> 2];
}

static uint32_t mkmszr_phase_prior_frames(const struct ai_controller *ai,
                                          uint32_t previous_info)
{
    uint32_t data;
    if (!previous_info) return 0;
    data = mkmszr_phase_word(ai, previous_info + 4u);
    /* AudioInfo +4 is the first (big-endian) signed halfword. */
    return (uint32_t)(int32_t)(int16_t)(data >> 16);
}

static void mkmszr_phase_dump(void)
{
    const char *dir = getenv("XDG_CACHE_HOME");
    char filename[4096];
    FILE *f;
    uint64_t start, i;
    mkmszr_phase_header hdr;
    if (!mkmszr_phase_store.enabled) return;
    if (dir == NULL || *dir == '\0') dir = "/tmp";
    if (snprintf(filename, sizeof(filename), "%s/mkmszr-phase-trace.bin", dir)
        >= (int)sizeof(filename)) return;
    f = fopen(filename, "wb");
    if (f == NULL) return;
    memset(&hdr, 0, sizeof(hdr));
    memcpy(hdr.magic, "MZRPH4", 6);
    hdr.version = 4u;
    hdr.record_size = (uint32_t)sizeof(mkmszr_phase_record);
    hdr.total = mkmszr_phase_store.total;
    start = hdr.total > MKMSZR_PHASE_CAP ? hdr.total - MKMSZR_PHASE_CAP : 0u;
    hdr.saved = hdr.total - start;
    hdr.overwritten = start;
    fwrite(&hdr, sizeof(hdr), 1u, f);
    for (i = start; i < hdr.total; ++i)
        fwrite(&mkmszr_phase_store.rows[i & (MKMSZR_PHASE_CAP - 1u)],
               sizeof(mkmszr_phase_record), 1u, f);
    fclose(f);
}

static void mkmszr_phase_capture(struct ai_controller *ai, uint32_t event,
                                 uint32_t observed_value)
{
    struct timespec now;
    mkmszr_phase_record *r;
    uint64_t idx;
    uint32_t previous_info, synth, *d;
    const char *on;
    if (!mkmszr_phase_store.initialized) {
        mkmszr_phase_store.initialized = 1;
        on = getenv("MKMSZR_TRACE_PHASE");
        mkmszr_phase_store.enabled = (on != NULL && strcmp(on, "1") == 0 &&
            getenv("MKMSZR_TRACE") != NULL &&
            strcmp(getenv("MKMSZR_TRACE"), "1") == 0);
        if (mkmszr_phase_store.enabled) atexit(mkmszr_phase_dump);
    }
    if (!mkmszr_phase_store.enabled || ai == NULL || ai->mi == NULL ||
        ai->mi->r4300 == NULL || ai->vi == NULL)
        return;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) return;
    idx = mkmszr_phase_store.total++;
    r = &mkmszr_phase_store.rows[idx & (MKMSZR_PHASE_CAP - 1u)];
    memset(r, 0, sizeof(*r));
    r->sequence = idx;
    r->monotonic_ns =
        (uint64_t)now.tv_sec * UINT64_C(1000000000) + (uint64_t)now.tv_nsec;
    r->event = event;
    /* Read existing CP0 Count; deliberately do NOT update it. */
    r->guest_count =
        r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG];
    d = r->field;
    d[0] = observed_value;
    d[1] = ai->regs[AI_STATUS_REG];
    d[2] = ai->regs[AI_DACRATE_REG];
    d[3] = ai->regs[AI_CONTROL_REG];
    d[4] = ai->regs[AI_BITRATE_REG];
    d[5] = ai->vi->clock;
    d[6] = ai->vi->delay;
    d[7] = ai->vi->expected_refresh_rate;
    d[8] = mkmszr_phase_word(ai, UINT32_C(0x800A7F60)); /* frame */
    d[9] = mkmszr_phase_word(ai, UINT32_C(0x800A7F74)); /* manager ready */
    d[10] = mkmszr_phase_word(ai, UINT32_C(0x8009A530)); /* VI enable */
    d[11] = mkmszr_phase_word(ai, UINT32_C(0x800BA450)); /* min */
    d[12] = mkmszr_phase_word(ai, UINT32_C(0x800BA454)); /* target */
    d[13] = mkmszr_phase_word(ai, UINT32_C(0x800BA458)); /* capacity */
    d[14] = mkmszr_phase_word(ai, UINT32_C(0x800A8004)); /* reserve */
    previous_info = mkmszr_phase_word(ai, UINT32_C(0x800A7F70));
    d[15] = previous_info; /* previous completed AudioInfo pointer */
    d[16] = mkmszr_phase_prior_frames(ai, previous_info);
    d[17] = mkmszr_phase_word(ai, UINT32_C(0x800A7F6C));
    d[18] = mkmszr_phase_word(ai, UINT32_C(0x800BA3E8));
    d[19] = mkmszr_phase_word(ai, UINT32_C(0x800BA3EC));
    d[20] = mkmszr_phase_word(ai, UINT32_C(0x800BA3F0));
    d[21] = mkmszr_phase_word(ai, UINT32_C(0x800A7F68));
    d[22] = mkmszr_phase_word(ai, UINT32_C(0x800BA3E0));
    d[23] = mkmszr_phase_word(ai, UINT32_C(0x800BA3E4));
    d[24] = mkmszr_phase_word(ai, UINT32_C(0x8009A534));
    d[25] = mkmszr_phase_word(ai, UINT32_C(0x8009A538));
    d[26] = mkmszr_phase_word(ai, UINT32_C(0x8009A53C));
    synth = mkmszr_phase_word(ai, UINT32_C(0x800A8210));
    d[27] = synth;
    d[28] = synth ? mkmszr_phase_word(ai, synth + 0x20u) : 0u;
    d[29] = mkmszr_phase_word(ai, UINT32_C(0x8009A910)); /* native stage */
    d[30] = mkmszr_phase_word(ai, UINT32_C(0x800C11E0)); /* compact selector */
    d[31] = mkmszr_phase_word(ai, UINT32_C(0x800A60E8)); /* box/mode bits */
    d[32] = mkmszr_phase_word(ai, UINT32_C(0x80000300)); /* TV type */
    d[33] = mkmszr_phase_word(ai, UINT32_C(0x800A8FC8)); /* crystal */
}
#endif
"""

def replace_once(text: str, old: str, new: str) -> str:
    hits = text.count(old)
    if hits != 1:
        raise RuntimeError(f"Pinned RMG v0.9.0 anchor occurs {hits} times: {old[:85]!r}")
    return text.replace(old, new)


def apply(path: Path = SRC) -> None:
    source = path.read_text()
    if "mkmszr_phase_capture(" in source:
        raise RuntimeError("phase diagnostic is already installed")
    if '#include "mkmszr_trace.h"' not in source:
        raise RuntimeError("install v02 observer first")
    source = replace_once(
        source,
        '#include "device/rdram/rdram.h"\n',
        '#include "device/rdram/rdram.h"\n#include "mkmszr_phase_trace.h"\n',
    )
    source = replace_once(
        source,
        '        if (*value < ai->last_read)\n',
        '        mkmszr_phase_capture(ai, 1u, *value);\n'
        '        if (*value < ai->last_read)\n',
    )
    source = replace_once(
        source,
        '        masked_write(&ai->regs[reg], value, mask);\n        return;\n',
        '        masked_write(&ai->regs[reg], value, mask);\n'
        '        mkmszr_phase_capture(ai, 2u, ai->regs[reg]);\n'
        '        return;\n',
    )
    source = replace_once(
        source,
        '    if (reg < AI_REGS_COUNT)\n    {\n        masked_write(&ai->regs[reg], value, mask);\n    }\n',
        '    if (reg < AI_REGS_COUNT)\n    {\n        masked_write(&ai->regs[reg], value, mask);\n'
        '        if (reg == AI_CONTROL_REG)\n'
        '            mkmszr_phase_capture(ai, 3u, ai->regs[reg]);\n'
        '        else if (reg == AI_BITRATE_REG)\n'
        '            mkmszr_phase_capture(ai, 4u, ai->regs[reg]);\n'
        '    }\n',
    )
    path.write_text(source)
    (path.parent / "mkmszr_phase_trace.h").write_text(HEADER)


if __name__ == "__main__":
    apply()
    print("MKMSZR opt-in RMG phase provenance observer v04 installed")
