"""Apply the MKMSZR observation-only trace to exactly RMG v0.9.0 source.

Run as a Flatpak-builder 'shell' source after checkout, before CMake.
No emulator execution, ROM edits, enqueue retries, or playback changes.
"""
from pathlib import Path

from observer_memory_patch import apply as install_memory_probe
from observer_phase_patch import apply as install_phase_probe

CORE = Path("Source/3rdParty/mupen64plus-core/src/device/rcp")
AUDIO = Path("Source/RMG-Audio/sdl_backend.cpp")

HEADER = r"""
#ifndef MKMSZR_OBSERVER_H
#define MKMSZR_OBSERVER_H
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef MKMSZR_TRACE_CAP
#define MKMSZR_TRACE_CAP 32768u
#endif
#define MKMSZR_TRACE_VERSION 1u

typedef struct {
    uint64_t sequence, monotonic_ns;
    uint32_t event, guest_count;
    uint32_t a, b, c, d, e, f, g, h;
} mkmszr_trace_record;
typedef struct {
    char magic[8];
    uint32_t version, record_size;
    uint64_t saved, total, overwritten;
} mkmszr_trace_file_header;
static struct {
    mkmszr_trace_record ring[MKMSZR_TRACE_CAP];
    uint64_t total;
    int initialized, enabled;
} mkmszr_trace_store;

static void mkmszr_trace_dump(void)
{
    const char *dir = getenv("XDG_CACHE_HOME");
    char path[4096];
    FILE *out;
    uint64_t first, i;
    mkmszr_trace_file_header header;
    if (!mkmszr_trace_store.enabled) return;
    if (!dir || !*dir) dir = "/tmp";
    if (snprintf(path, sizeof(path), "%s/mkmszr-%s-trace.bin",
                 dir, MKMSZR_TRACE_CHANNEL) >= (int)sizeof(path)) return;
    out = fopen(path, "wb");
    if (!out) return;
    memset(&header, 0, sizeof(header));
    memcpy(header.magic, "MZRHST1", 7);
    header.version = MKMSZR_TRACE_VERSION;
    header.record_size = (uint32_t)sizeof(mkmszr_trace_record);
    header.total = mkmszr_trace_store.total;
    first = header.total > MKMSZR_TRACE_CAP ? header.total - MKMSZR_TRACE_CAP : 0;
    header.overwritten = first;
    header.saved = header.total - first;
    fwrite(&header, sizeof(header), 1, out);
    for (i = first; i < header.total; i++)
        fwrite(&mkmszr_trace_store.ring[i & (MKMSZR_TRACE_CAP-1u)],
               sizeof(mkmszr_trace_record), 1, out);
    fclose(out);
}

static void mkmszr_trace(uint32_t event, uint32_t guest_count,
                         uint32_t a, uint32_t b, uint32_t c, uint32_t d,
                         uint32_t e, uint32_t f, uint32_t g, uint32_t h)
{
    struct timespec t;
    mkmszr_trace_record *r;
    uint64_t n;
    if (!mkmszr_trace_store.initialized) {
        const char *env = getenv("MKMSZR_TRACE");
        mkmszr_trace_store.initialized = 1;
        mkmszr_trace_store.enabled = (env && strcmp(env, "1") == 0);
        if (mkmszr_trace_store.enabled) atexit(mkmszr_trace_dump);
    }
    if (!mkmszr_trace_store.enabled) return;
    if (clock_gettime(CLOCK_MONOTONIC, &t) != 0) return;
    n = mkmszr_trace_store.total++;
    r = &mkmszr_trace_store.ring[n & (MKMSZR_TRACE_CAP-1u)];
    r->sequence = n;
    r->monotonic_ns = (uint64_t)t.tv_sec * 1000000000u + (uint64_t)t.tv_nsec;
    r->event = event;
    r->guest_count = guest_count;
    r->a=a; r->b=b; r->c=c; r->d=d;
    r->e=e; r->f=f; r->g=g; r->h=h;
}
#endif
"""

def replace_once(path: Path, needle: str, replacement: str):
    text = path.read_text()
    count = text.count(needle)
    if count != 1:
        raise RuntimeError(f"{path}: expected 1 match, got {count} for {needle[:110]!r}")
    path.write_text(text.replace(needle, replacement))
    print(f"patched {path}: {needle[:50]!r}")

def add_trace_header(path: Path, channel: str):
    (path.parent / "mkmszr_trace.h").write_text(HEADER)
    capacities = {"ai": 262144, "vi": 131072, "rsp": 262144,
                  "host-audio": 131072}
    capacity = capacities[channel]
    replace_once(path, '#include <string.h>',
                 '#include <string.h>\n#define MKMSZR_TRACE_CAP '
                 + str(capacity) + 'u\n#define MKMSZR_TRACE_CHANNEL "'
                 + channel + '"\n#include "mkmszr_trace.h"')

ai = CORE / "ai/ai_controller.c"
add_trace_header(ai, "ai")
replace_once(ai,
    '    unsigned int duration = get_dma_duration(ai) * ai->dma_modifier;\n',
    '    unsigned int duration = get_dma_duration(ai) * ai->dma_modifier;\n'
    '    mkmszr_trace(0x10, r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        ai->regs[AI_STATUS_REG], ai->regs[AI_LEN_REG], ai->regs[AI_DRAM_ADDR_REG],\n'
    '        ai->fifo[0].length, ai->fifo[1].length, duration, ai->last_read, 0);\n')
replace_once(ai,
    '        do_dma(ai, &ai->fifo[0]);\n    }\n}\n\nstatic void fifo_pop',
    '        do_dma(ai, &ai->fifo[0]);\n    }\n'
    '    mkmszr_trace(0x11, r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        ai->regs[AI_STATUS_REG], ai->fifo[0].length, ai->fifo[1].length,\n'
    '        ai->fifo[0].duration, ai->fifo[1].duration, ai->last_read, 0, 0);\n'
    '}\n\nstatic void fifo_pop')
replace_once(ai,
    '        *value = get_remaining_dma_length(ai);\n',
    '        *value = get_remaining_dma_length(ai);\n'
    '        mkmszr_trace(0x12, r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '            *value, ai->regs[AI_STATUS_REG], ai->fifo[0].length,\n'
    '            ai->fifo[0].duration, ai->last_read, 0, 0, 0);\n')
replace_once(ai,
    '    else if (reg < AI_REGS_COUNT)\n    {\n        *value = ai->regs[reg];\n    }\n',
    '    else if (reg < AI_REGS_COUNT)\n    {\n        *value = ai->regs[reg];\n'
    '        if (reg == AI_STATUS_REG)\n'
    '            mkmszr_trace(0x13, r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '                *value, ai->fifo[0].length, ai->fifo[1].length,\n'
    '                ai->last_read, 0, 0, 0, 0);\n'
    '    }\n')
replace_once(ai,
    'void ai_end_of_dma_event(void* opaque)\n{\n    struct ai_controller* ai = (struct ai_controller*)opaque;\n',
    'void ai_end_of_dma_event(void* opaque)\n{\n    struct ai_controller* ai = (struct ai_controller*)opaque;\n'
    '    mkmszr_trace(0x14, r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        ai->regs[AI_STATUS_REG], ai->fifo[0].length, ai->fifo[1].length,\n'
    '        ai->last_read, ai->fifo[0].duration, ai->fifo[1].duration, 0, 0);\n')
replace_once(ai,
    '    fifo_pop(ai);\n    raise_rcp_interrupt(ai->mi, MI_INTR_AI);\n',
    '    fifo_pop(ai);\n    raise_rcp_interrupt(ai->mi, MI_INTR_AI);\n'
    '    mkmszr_trace(0x15, r4300_cp0_regs(&ai->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        ai->regs[AI_STATUS_REG], ai->fifo[0].length, ai->fifo[1].length,\n'
    '        ai->last_read, ai->fifo[0].duration, ai->fifo[1].duration, 0, 0);\n')

vi = CORE / "vi/vi_controller.c"
add_trace_header(vi, "vi")
replace_once(vi,
    '    new_vi();\n',
    '    mkmszr_trace(0x20, r4300_cp0_regs(&vi->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        vi->delay, vi->field, vi->regs[VI_STATUS_REG], 0, 0, 0, 0, 0);\n'
    '    new_vi();\n')
replace_once(vi,
    '    add_interrupt_event_count(&vi->mi->r4300->cp0, VI_INT, next_vi);\n',
    '    add_interrupt_event_count(&vi->mi->r4300->cp0, VI_INT, next_vi);\n'
    '    mkmszr_trace(0x21, r4300_cp0_regs(&vi->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        next_vi, vi->delay, vi->field, 0, 0, 0, 0, 0);\n')

rsp = CORE / "rsp/rsp_core.c"
add_trace_header(rsp, "rsp")
replace_once(rsp,
    '    uint32_t rsp_cycles = rsp.doRspCycles(sp->first_run) / 2;\n',
    '    /* First-run task boundary only; ParaLLEl emits millions of zero-cycle '
    'polls. */\n'
    '    uint32_t mkmszr_rsp_first = sp->first_run;\n'
    '    if (mkmszr_rsp_first)\n'
    '        mkmszr_trace(0x30, r4300_cp0_regs(&sp->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '            sp->regs[SP_STATUS_REG], sp->rsp_wait, mkmszr_rsp_first,\n'
    '            sp->mi->regs[MI_INTR_REG], 0, 0, 0, 0);\n'
    '    uint32_t rsp_cycles = rsp.doRspCycles(sp->first_run) / 2;\n'
    '    if (mkmszr_rsp_first || (sp->regs[SP_STATUS_REG] & (SP_STATUS_HALT | SP_STATUS_BROKE)))\n'
    '        mkmszr_trace(0x31, r4300_cp0_regs(&sp->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '            sp->regs[SP_STATUS_REG], sp->rsp_wait, rsp_cycles,\n'
    '            sp->mi->regs[MI_INTR_REG], 0, 0, 0, 0);\n')
replace_once(rsp,
    'void rsp_interrupt_event(void* opaque)\n{\n    struct rsp_core* sp = (struct rsp_core*)opaque;\n',
    'void rsp_interrupt_event(void* opaque)\n{\n    struct rsp_core* sp = (struct rsp_core*)opaque;\n'
    '    mkmszr_trace(0x32, r4300_cp0_regs(&sp->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '        sp->regs[SP_STATUS_REG], sp->rsp_wait, sp->rsp_status,\n'
    '        sp->mi->regs[MI_INTR_REG], 0, 0, 0, 0);\n')
replace_once(rsp,
    'void rsp_task_event(void* opaque)\n{\n    struct rsp_core* sp = (struct rsp_core*)opaque;\n',
    'void rsp_task_event(void* opaque)\n{\n    struct rsp_core* sp = (struct rsp_core*)opaque;\n'
    '    if (sp->rsp_wait)\n'
    '        mkmszr_trace(0x33, r4300_cp0_regs(&sp->mi->r4300->cp0)[CP0_COUNT_REG],\n'
    '            sp->regs[SP_STATUS_REG], sp->rsp_wait, 0, 0, 0, 0, 0, 0);\n')

add_trace_header(AUDIO, "host-audio")
replace_once(AUDIO,
    '    double acceptableLatency = ((double)sdl_backend->frequency * 0.2) * 4.0;\n',
    '    double acceptableLatency = ((double)sdl_backend->frequency * 0.2) * 4.0;\n'
    '    mkmszr_trace(0x50, 0, (uint32_t)size, (uint32_t)audioQueued,\n'
    '        (uint32_t)acceptableLatency, sdl_backend->frequency,\n'
    '        sdl_backend->speed_factor, 0, 0, 0);\n')
replace_once(AUDIO,
    '    if (audioQueued >= acceptableLatency)\n    {\n        return;\n    }\n',
    '    if (audioQueued >= acceptableLatency)\n    {\n'
    '        mkmszr_trace(0x51, 0, (uint32_t)size, (uint32_t)audioQueued,\n'
    '            (uint32_t)acceptableLatency, sdl_backend->frequency, 0, 0, 0, 0);\n'
    '        return;\n    }\n')
replace_once(AUDIO,
    '    SDL_PutAudioStreamData(sdl_backend->stream, sdl_backend->resample_buffer, size);\n',
    '    bool mkmszr_queued = SDL_PutAudioStreamData(sdl_backend->stream,\n'
    '                                          sdl_backend->resample_buffer, size);\n'
    '    mkmszr_trace(0x52, 0, (uint32_t)size, (uint32_t)audioQueued,\n'
    '        (uint32_t)acceptableLatency, mkmszr_queued ? 1u : 0u,\n'
    '        sdl_backend->frequency, 0, 0, 0);\n')

install_memory_probe(vi)
install_phase_probe(ai)
print("MKMSZR observer + opt-in RDRAM v02 and phase provenance v04 applied to pinned RMG")
