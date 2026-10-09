"""Apply an opt-in, read-only RDRAM probe AFTER the existing RMG v01 observer.

Never applies to ROM and never reads AI MMIO. Tested with pinned RMG v0.9.0
structure signatures and synthetic 8-MiB RDRAM, not runtime validated.
"""
from pathlib import Path

SRC = Path('Source/3rdParty/mupen64plus-core/src/device/rcp/vi/vi_controller.c')
INJECT = r'''
/* MKMSZR memory observer v02: read-only; no guest MMIO access or writes. */
static uint32_t mkmszr_memory_word(const struct rdram* rd, uint32_t phys)
{
    if (rd == NULL || rd->dram == NULL || (phys & 3u) != 0 ||
        (size_t)phys + 4u > rd->dram_size) return 0;
    return rd->dram[phys >> 2];
}
static uint32_t mkmszr_memory_hash(const struct rdram* rd,
                                   uint32_t begin, uint32_t end)
{
    uint32_t h = UINT32_C(2166136261), p;
    if (rd == NULL || rd->dram == NULL || (begin & 3u) || (end & 3u) ||
        begin > end || (size_t)end > rd->dram_size) return 0;
    for (p = begin; p < end; p += 4u)
        h = (h ^ rd->dram[p >> 2]) * UINT32_C(16777619);
    return h;
}
static void mkmszr_memory_probe(const struct vi_controller* vi)
{
    static int enabled = -1;
    static uint32_t highest = 0;
    struct r4300_core* cpu;
    const struct rdram* rd;
    const char* opt;
    uint32_t cursor, base, hud, stage, magic, flags = 0;
    uint32_t count;
    if (enabled < 0) {
        opt = getenv("MKMSZR_TRACE_MEM");
        enabled = (opt != NULL && strcmp(opt, "1") == 0 &&
                   getenv("MKMSZR_TRACE") != NULL &&
                   strcmp(getenv("MKMSZR_TRACE"), "1") == 0);
    }
    if (!enabled || vi == NULL || vi->mi == NULL) return;
    cpu = vi->mi->r4300;
    if (cpu == NULL) return;
    rd = cpu->rdram;
    if (rd == NULL || rd->dram == NULL || rd->dram_size < 0x00290998u) return;
    cursor = mkmszr_memory_word(rd, 0x00111eccu);
    base = mkmszr_memory_word(rd, 0x000eecd0u);
    hud = mkmszr_memory_word(rd, 0x001b2de0u);
    stage = mkmszr_memory_word(rd, 0x0009a910u);
    magic = mkmszr_memory_word(rd, 0x001af7d0u);
    count = r4300_cp0_regs(&cpu->cp0)[CP0_COUNT_REG];
    if (cursor >= 0x801b3420u && cursor < 0x80290998u && cursor > highest)
        highest = cursor;
    if (base == 0x801b3420u) flags |= 1u;
    if (cursor >= base && cursor <= 0x80290990u) flags |= 2u;
    if (hud != 0 && hud >= 0x801b3420u && hud <= 0x8028f790u)
        flags |= 4u;
    if ((flags & 4u) && cursor >= hud + 0x1200u) flags |= 8u;
    if (magic == 0x4d4b5356u) flags |= 16u;
    mkmszr_trace(0x40u, count,
                 cursor, base, hud, stage, magic,
                 mkmszr_memory_word(rd, 0x000a7f60u), highest, flags);
    mkmszr_trace(0x41u, count,
                 mkmszr_memory_hash(rd, 0x001b28f0u, 0x001b2de0u),
                 mkmszr_memory_hash(rd, 0x001b2f50u, 0x001b30e4u),
                 mkmszr_memory_hash(rd, 0x001b30f0u, 0x001b33bcu),
                 mkmszr_memory_word(rd, 0x001b2de4u),
                 mkmszr_memory_word(rd, 0x000a60e8u),
                 mkmszr_memory_word(rd, 0x0009a530u),
                 mkmszr_memory_word(rd, 0x000a7f6cu),
                 mkmszr_memory_word(rd, 0x00111eccu));
}
'''


def replace_once(s: str, old: str, new: str) -> str:
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f'expected one anchor, got {n}: {old[:60]!r}')
    return s.replace(old,new)


def apply(path: Path = SRC) -> None:
    text = path.read_text()
    if 'mkmszr_memory_probe' in text:
        raise RuntimeError('memory observer already installed')
    if '#include "mkmszr_trace.h"' not in text:
        raise RuntimeError('v01 host observer must be installed first')
    text = replace_once(text, '#include "device/memory/memory.h"\n',
                        '#include "device/memory/memory.h"\n#include "device/rdram/rdram.h"\n')
    text = replace_once(text, 'unsigned int vi_clock_from_tv_standard(',
                        INJECT+'\nunsigned int vi_clock_from_tv_standard(')
    text = replace_once(text, '    new_vi();\n',
                        '    mkmszr_memory_probe(vi);\n    new_vi();\n')
    path.write_text(text)


if __name__ == '__main__':
    apply()
    print('MKMSZR v02 RDRAM observer installed')
