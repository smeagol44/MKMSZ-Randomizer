"""Observe actual ParaLLEl RSP DMA stores against the unstarted AI tail.

Pinned RMG v0.9.0, opt-in only. No ROM, timing, retry or FIFO policy change.
"""

from pathlib import Path

CORE_PROBE = r'''
/* PCM observer: all callbacks execute synchronously on the emulation thread. */
static struct {
    int initialized, enabled, pending, bad_pending;
    uint32_t next_id, head_id, tail_id, task_id, task_type;
    uint32_t dst, src, bytes, pc, tail, tail_length, overlap;
    uint32_t first_changed, old_hash, incoming_hash;
    uint32_t begins, commits, audio_rows, overlaps, changed_rows, invalid, nested;
    uint32_t *word_writer;
    uint32_t task_types[65536];
    unsigned char completed[65536];
    uint32_t tail_ready_generation, ready_before;
    unsigned char old_bytes[4096];
} mkmszr_pcm;

static uint32_t mkmszr_pcm_count(void)
{
    return r4300_cp0_regs(&g_dev.r4300.cp0)[CP0_COUNT_REG];
}

static void mkmszr_pcm_summary(void)
{
    mkmszr_trace(0x89, mkmszr_pcm_count(), mkmszr_pcm.begins,
        mkmszr_pcm.commits, mkmszr_pcm.audio_rows, mkmszr_pcm.overlaps,
        mkmszr_pcm.changed_rows, mkmszr_pcm.invalid, mkmszr_pcm.nested,
        mkmszr_pcm.pending ? 1u : 0u);
    free(mkmszr_pcm.word_writer);
}

static int mkmszr_pcm_enabled(void)
{
    if (!mkmszr_pcm.initialized) {
        const char *env = getenv("MKMSZR_TRACE_PCM");
        const char *trace = getenv("MKMSZR_TRACE");
        mkmszr_pcm.initialized = 1;
        mkmszr_pcm.enabled = env && trace && strcmp(env,"1") == 0
            && strcmp(trace,"1") == 0;
        if (mkmszr_pcm.enabled) {
            uint32_t words[4]={0,0,0,0}, i;
            mkmszr_pcm.word_writer = (uint32_t*)calloc(0x200000u, sizeof(uint32_t));
            if (!mkmszr_pcm.word_writer) mkmszr_pcm.invalid++;
            mkmszr_trace(0x80, mkmszr_pcm_count(), 2, 4096, 0x200000u, 65536, 0, 0, 0, 0);
            for (i=0;i<32;i++) {
                unsigned char c=(unsigned char)ROM_SETTINGS.MD5[i];
                uint32_t v=c>='0' && c<='9' ? c-'0' :
                    c>='A' && c<='F' ? c-'A'+10 :
                    c>='a' && c<='f' ? c-'a'+10 : 0;
                words[i/8]=(words[i/8]<<4)|v;
            }
            mkmszr_trace(0x86, mkmszr_pcm_count(), words[0],words[1],words[2],words[3],
                (uint32_t)g_dev.rdram.dram_size,0,0,0);
            /* Registered after trace dump: summary runs before dump at exit. */
            atexit(mkmszr_pcm_summary);
        }
    }
    return mkmszr_pcm.enabled;
}

static uint32_t mkmszr_pcm_tail_address(const struct ai_controller *ai)
{
    /* do_dma applies carry when this queued tail becomes the head. */
    return ai->fifo[1].address + (ai->delayed_carry ? 0x2000u : 0u);
}

static uint32_t mkmszr_pcm_sealed(uint32_t address, uint32_t length)
{
    uint32_t k, generation=0, owner;
    if (!mkmszr_pcm.word_writer || !length || (address & 3) || (length & 3)
        || address >= 0x800000u || length > 0x800000u-address) return 0;
    for (k=0;k<length;k+=4) {
        owner=mkmszr_pcm.word_writer[(address+k)/4];
        if (!owner || owner>=65536 || !mkmszr_pcm.completed[owner]
            || mkmszr_pcm.task_types[owner]!=2) return 0;
        if (!generation) generation=owner;
        if (generation!=owner) return 0;
    }
    return generation;
}

static void mkmszr_pcm_ready_record(struct ai_controller *ai)
{
    mkmszr_trace(0x8a,mkmszr_pcm_count(),mkmszr_pcm.tail_id,
        mkmszr_pcm.tail_ready_generation,mkmszr_pcm.task_id,
        mkmszr_pcm_tail_address(ai),ai->fifo[1].length,
        ai->regs[AI_STATUS_REG],0,0);
}

static void mkmszr_pcm_occupancy(struct ai_controller *ai, uint32_t event)
{
    mkmszr_trace(event, mkmszr_pcm_count(), mkmszr_pcm.head_id,
        ai->fifo[0].address, ai->fifo[0].length, mkmszr_pcm.tail_id,
        mkmszr_pcm_tail_address(ai), ai->fifo[1].length,
        ai->regs[AI_STATUS_REG], ai->delayed_carry);
}

static void mkmszr_pcm_accept(struct ai_controller *ai)
{
    if (!mkmszr_pcm_enabled()) return;
    if (ai->regs[AI_STATUS_REG] & AI_STATUS_FULL) {
        mkmszr_pcm.tail_id = ++mkmszr_pcm.next_id;
        mkmszr_pcm.tail_ready_generation = mkmszr_pcm_sealed(
            mkmszr_pcm_tail_address(ai),ai->fifo[1].length);
    } else
        mkmszr_pcm.head_id = ++mkmszr_pcm.next_id;
    mkmszr_pcm_occupancy(ai, 0x81);
    mkmszr_pcm_ready_record(ai);
}

static void mkmszr_pcm_pop(struct ai_controller *ai, uint32_t had_tail)
{
    if (!mkmszr_pcm_enabled()) return;
    mkmszr_pcm.head_id = had_tail ? mkmszr_pcm.tail_id : 0;
    mkmszr_pcm.tail_id = 0;
    mkmszr_pcm.tail_ready_generation = 0;
    mkmszr_pcm_occupancy(ai, 0x82);
    mkmszr_pcm_ready_record(ai);
}

EXPORT void CALL MKMSZR_PCMTask(uint32_t type, uint32_t pc)
{
    if (!mkmszr_pcm_enabled()) return;
    mkmszr_pcm.task_id++;
    if (mkmszr_pcm.task_id >= 65536) {mkmszr_pcm.invalid++;return;}
    mkmszr_pcm.task_type = type;
    mkmszr_pcm.task_types[mkmszr_pcm.task_id]=type;
    mkmszr_trace(0x85, mkmszr_pcm_count(), mkmszr_pcm.task_id,
        type, pc, 0, 0, 0, 0, 0);
}

EXPORT void CALL MKMSZR_PCMTaskEnd(uint32_t status, uint32_t pc)
{
    struct ai_controller *ai=&g_dev.ai;
    uint32_t id=mkmszr_pcm.task_id;
    if (!mkmszr_pcm_enabled() || !id || id>=65536) return;
    /* HALT|BROKE|TASKDONE; a yielded/running task is not complete. */
    if ((status & 0x203u)!=0x203u || mkmszr_pcm.completed[id]) return;
    mkmszr_pcm.completed[id]=1;
    mkmszr_trace(0x87,mkmszr_pcm_count(),id,mkmszr_pcm.task_type,status,pc,0,0,0,0);
    if ((ai->regs[AI_STATUS_REG] & AI_STATUS_FULL) && !mkmszr_pcm.tail_ready_generation)
        mkmszr_pcm.tail_ready_generation=mkmszr_pcm_sealed(
            mkmszr_pcm_tail_address(ai),ai->fifo[1].length);
    mkmszr_pcm_ready_record(ai);
}

EXPORT void CALL MKMSZR_PCMBefore(uint32_t dst, uint32_t src,
                                 uint32_t bytes, uint32_t pc)
{
    struct ai_controller *ai = &g_dev.ai;
    const unsigned char *ram = (const unsigned char*)g_dev.rdram.dram;
    const unsigned char *spmem = (const unsigned char*)g_dev.sp.mem;
    uint32_t k, address, source, tail, flags;
    if (!mkmszr_pcm_enabled()) return;
    mkmszr_pcm.begins++;
    if (mkmszr_pcm.pending) {
        mkmszr_pcm.nested++;
        mkmszr_pcm.bad_pending = 1;
    }
    mkmszr_pcm.pending = 1;
    mkmszr_pcm.dst = dst;
    mkmszr_pcm.src = src;
    mkmszr_pcm.bytes = bytes;
    mkmszr_pcm.pc = pc;
    mkmszr_pcm.tail = tail = mkmszr_pcm_tail_address(ai);
    mkmszr_pcm.tail_length = ai->fifo[1].length;
    mkmszr_pcm.ready_before = mkmszr_pcm.tail_ready_generation;
    mkmszr_pcm.overlap = 0;
    mkmszr_pcm.old_hash = mkmszr_pcm.incoming_hash = 2166136261u;
    if (mkmszr_pcm.task_type == 2) mkmszr_pcm.audio_rows++;
    flags = ai->regs[AI_STATUS_REG];
    if (bytes > 4096 || (bytes & 3) || !ram || !spmem || !mkmszr_pcm.word_writer
        || !mkmszr_pcm.task_id || mkmszr_pcm.task_id >= 65536
        || g_dev.rdram.dram_size != 0x800000u
        || ((flags & AI_STATUS_FULL) &&
            (tail >= 0x800000u || ai->fifo[1].length > 0x800000u-tail))) {
        mkmszr_pcm.invalid++;
        mkmszr_pcm.bad_pending = 1;
        return;
    }
    if (!(flags & AI_STATUS_FULL)) return;
    /* Exact physical byte mapping of the pinned plugin's 32-bit stores.
       Includes word alignment and independent SP/RDRAM wrap. */
    for (k=0; k<bytes; k++) {
        address = ((dst + (k & ~3u)) & 0x7ffffcu) + (k & 3u);
        source = ((src + (k & ~3u)) & 0x1ffcu) + (k & 3u);
        if (address >= tail && address-tail < ai->fifo[1].length) {
            unsigned char old = ram[address ^ S8];
            unsigned char incoming = spmem[source ^ S8];
            mkmszr_pcm.old_bytes[k] = old;
            mkmszr_pcm.overlap++;
            mkmszr_pcm.old_hash = (mkmszr_pcm.old_hash ^ old)*16777619u;
            mkmszr_pcm.incoming_hash =
                (mkmszr_pcm.incoming_hash ^ incoming)*16777619u;
        }
    }
}

EXPORT void CALL MKMSZR_PCMAfter(void)
{
    struct ai_controller *ai = &g_dev.ai;
    const unsigned char *ram = (const unsigned char*)g_dev.rdram.dram;
    const unsigned char *spmem = (const unsigned char*)g_dev.sp.mem;
    uint32_t k, address, source, changed=0, match=1, flags=1, now_hash=2166136261u;
    if (!mkmszr_pcm_enabled()) return;
    mkmszr_pcm.commits++;
    if (!mkmszr_pcm.pending) {
        mkmszr_pcm.nested++;
        return;
    }
    if (ai->regs[AI_STATUS_REG] & AI_STATUS_FULL) flags |= 2;
    if (mkmszr_pcm.overlap) flags |= 4;
    if (mkmszr_pcm.ready_before && mkmszr_pcm.ready_before!=mkmszr_pcm.task_id) flags |= 32;
    else if (mkmszr_pcm.overlap) flags |= 64;
    /* Nothing may promote/rebind the tail inside one synchronous DMA row. */
    if (mkmszr_pcm.bad_pending || mkmszr_pcm.tail != mkmszr_pcm_tail_address(ai)
        || mkmszr_pcm.tail_length != ai->fifo[1].length) flags |= 16;
    if (!(flags & 16)) {
        for (k=0; k<mkmszr_pcm.bytes && mkmszr_pcm.overlap; k++) {
            address = ((mkmszr_pcm.dst+(k & ~3u)) & 0x7ffffcu)+(k & 3u);
            source = ((mkmszr_pcm.src+(k & ~3u)) & 0x1ffcu)+(k & 3u);
            if (address >= mkmszr_pcm.tail &&
                address-mkmszr_pcm.tail < mkmszr_pcm.tail_length) {
                unsigned char after = ram[address ^ S8];
                if (after != spmem[source ^ S8]) match = 0;
                if (after != mkmszr_pcm.old_bytes[k]) {
                    if (!changed) mkmszr_pcm.first_changed = address;
                    changed++;
                }
                now_hash = (now_hash ^ after)*16777619u;
            }
        }
        if (match) flags |= 8;
        for (k=0;k<mkmszr_pcm.bytes;k+=4)
            mkmszr_pcm.word_writer[((mkmszr_pcm.dst+k)&0x7ffffcu)/4]=mkmszr_pcm.task_id;
    }
    if (mkmszr_pcm.overlap) mkmszr_pcm.overlaps++;
    if (changed) mkmszr_pcm.changed_rows++;
    if (mkmszr_pcm.task_type == 2 || mkmszr_pcm.overlap || (flags & 16))
        mkmszr_trace(0x83, mkmszr_pcm_count(), mkmszr_pcm.dst & 0x7ffffcu,
            mkmszr_pcm.bytes, mkmszr_pcm.task_type, mkmszr_pcm.pc,
            mkmszr_pcm.tail_id, mkmszr_pcm.overlap, changed, flags);
    if (mkmszr_pcm.overlap)
        mkmszr_trace(0x84, mkmszr_pcm_count(), changed ? mkmszr_pcm.first_changed : 0,
            mkmszr_pcm.tail, mkmszr_pcm.tail_length, mkmszr_pcm.head_id,
            mkmszr_pcm.old_hash, now_hash, mkmszr_pcm.incoming_hash,
            mkmszr_pcm.task_id);
    if (mkmszr_pcm.overlap)
        mkmszr_trace(0x8b,mkmszr_pcm_count(),mkmszr_pcm.ready_before,
            mkmszr_pcm.task_id,mkmszr_pcm.tail_id,mkmszr_pcm.task_type,0,0,0,0);
    mkmszr_pcm.pending = mkmszr_pcm.bad_pending = 0;
}
'''

BRIDGE_HEADER = r'''
#ifndef MKMSZR_PCM_BRIDGE_H
#define MKMSZR_PCM_BRIDGE_H
#include <stdint.h>
extern void (*mkmszr_pcm_task)(uint32_t, uint32_t);
extern void (*mkmszr_pcm_end)(uint32_t, uint32_t);
extern void (*mkmszr_pcm_before)(uint32_t, uint32_t, uint32_t, uint32_t);
extern void (*mkmszr_pcm_after)(void);
#endif
'''


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"{path}: PCM observer anchor mismatch")
    path.write_text(text.replace(old, new))


def apply(root: Path) -> None:
    core = root / "Source/3rdParty/mupen64plus-core/src/device/rcp/ai/ai_controller.c"
    plugin = root / "Source/3rdParty/mupen64plus-rsp-parallel"
    if "MKMSZR_PCMBefore" in core.read_text():
        raise RuntimeError("PCM observer already installed")
    exports = root / "Source/3rdParty/mupen64plus-core/src/api/api_export.ver"
    replace(exports, 'PluginGetVersion;',
            'MKMSZR_PCMBefore;\nMKMSZR_PCMAfter;\nMKMSZR_PCMTask;\nMKMSZR_PCMTaskEnd;\nPluginGetVersion;')
    replace(core, '#include "device/rdram/rdram.h"',
            '#include "device/rdram/rdram.h"\n#include "device/device.h"\n'
            '#include "main/main.h"\n#include "main/rom.h"\n#include "api/m64p_types.h"')
    replace(core, '#define AI_STATUS_FULL UINT32_C(0x80000000)',
            '#define AI_STATUS_FULL UINT32_C(0x80000000)\n'+CORE_PROBE)
    # In the existing observer, 0x11 occurs after fifo_push has really accepted.
    replace(core, '    mkmszr_trace(0x11,',
            '    mkmszr_pcm_accept(ai);\n    mkmszr_trace(0x11,')
    replace(core, '    fifo_pop(ai);\n',
            '    uint32_t mkmszr_pcm_had_tail = ai->regs[AI_STATUS_REG] & AI_STATUS_FULL;\n'
            '    fifo_pop(ai);\n    mkmszr_pcm_pop(ai, mkmszr_pcm_had_tail);\n')
    (plugin / "mkmszr_pcm_bridge.h").write_text(BRIDGE_HEADER)
    parallel = plugin / "parallel.cpp"
    replace(parallel, '#include <cstdarg>', '#include <cstdarg>\n#include <cstdlib>\n'
            '#include <cstring>\n#include <dlfcn.h>\n#include "mkmszr_pcm_bridge.h"\n'
            'void (*mkmszr_pcm_task)(uint32_t,uint32_t) = nullptr;\n'
            'void (*mkmszr_pcm_end)(uint32_t,uint32_t) = nullptr;\n'
            'void (*mkmszr_pcm_before)(uint32_t,uint32_t,uint32_t,uint32_t) = nullptr;\n'
            'void (*mkmszr_pcm_after)(void) = nullptr;')
    replace(parallel, '\t\tif (cycles)\n\t\t{',
            '\t\tif (cycles)\n\t\t{\n'
            '\t\t\tif (mkmszr_pcm_task) mkmszr_pcm_task(\n'
            '\t\t\t    RSP::cpu.get_state().dmem[0xfc0/4], *RSP::rsp.SP_PC_REG);')
    replace(parallel, '\t\treturn cycles;',
            '\t\tif (mkmszr_pcm_end) mkmszr_pcm_end(*RSP::rsp.SP_STATUS_REG, *RSP::rsp.SP_PC_REG);\n'
            '\t\treturn cycles;')
    startup = '\t\treturn M64ERR_SUCCESS;\n\t}\n\n\tEXPORT m64p_error CALL PluginShutdown'
    replacement = '''\t\tconst char *pcm = std::getenv("MKMSZR_TRACE_PCM");
\t\tconst char *trace = std::getenv("MKMSZR_TRACE");
\t\tif (pcm && trace && std::strcmp(pcm,"1")==0 && std::strcmp(trace,"1")==0) {
\t\t\tmkmszr_pcm_task = reinterpret_cast<decltype(mkmszr_pcm_task)>(dlsym(CoreLibHandle,"MKMSZR_PCMTask"));
\t\t\tmkmszr_pcm_end = reinterpret_cast<decltype(mkmszr_pcm_end)>(dlsym(CoreLibHandle,"MKMSZR_PCMTaskEnd"));
\t\t\tmkmszr_pcm_before = reinterpret_cast<decltype(mkmszr_pcm_before)>(dlsym(CoreLibHandle,"MKMSZR_PCMBefore"));
\t\t\tmkmszr_pcm_after = reinterpret_cast<decltype(mkmszr_pcm_after)>(dlsym(CoreLibHandle,"MKMSZR_PCMAfter"));
\t\t\tif (!mkmszr_pcm_task || !mkmszr_pcm_end || !mkmszr_pcm_before || !mkmszr_pcm_after) return M64ERR_INCOMPATIBLE;
\t\t}
\t\treturn M64ERR_SUCCESS;
\t}

\tEXPORT m64p_error CALL PluginShutdown'''
    replace(parallel, startup, replacement)
    cp0 = plugin / "rsp/cp0.cpp"
    replace(cp0, '#include "../rsp_1.1.h"',
            '#include "../rsp_1.1.h"\n#include "../mkmszr_pcm_bridge.h"')
    # A dedicated suffix inside rsp_dma_write, NOT the DMA-read loop.
    start = '\tstatic void rsp_dma_write(RSP::CPUState *rsp)'
    text = cp0.read_text()
    prefix, suffix = text.split(start, 1)
    anchor = '\t\t\tunsigned j = 0;\n\n\t\t\tdo\n'
    if suffix.count(anchor) != 1:
        raise RuntimeError("DMA write-row pre-store anchor mismatch")
    suffix = suffix.replace(anchor,
        '\t\t\tunsigned j = 0;\n'
        '\t\t\tif (mkmszr_pcm_before) mkmszr_pcm_before(dest, source, (length+3u)&~3u, rsp->pc);\n\n'
        '\t\t\tdo\n')
    anchor = '\t\t\tsource += length;\n\t\t\tdest += length + skip;'
    if suffix.count(anchor) != 1:
        raise RuntimeError("DMA write-row post-store anchor mismatch")
    suffix = suffix.replace(anchor,
        '\t\t\tif (mkmszr_pcm_after) mkmszr_pcm_after();\n'+anchor)
    cp0.write_text(prefix+start+suffix)
    cmake = plugin / "CMakeLists.txt"
    replace(cmake, 'target_link_libraries(${NAME_PLUGIN_M64P} PUBLIC lightning)',
            'target_link_libraries(${NAME_PLUGIN_M64P} PUBLIC lightning ${CMAKE_DL_LIBS})')

