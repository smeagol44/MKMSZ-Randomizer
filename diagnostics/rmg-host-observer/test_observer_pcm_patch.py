"""Synthetic C/Python contract tests; never loads a ROM or runs an emulator."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

from analyze_pcm_trace import analyze
from observer_pcm_patch import CORE_PROBE
from pcm_ownership import assess_promoted_initialization, replay

PREFIX = r'''
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define EXPORT __attribute__((visibility("default")))
#define CALL
#define S8 3u
#define CP0_COUNT_REG 9
#define AI_STATUS_REG 3
#define AI_STATUS_BUSY 0x40000000u
#define AI_STATUS_FULL 0x80000000u
struct ai_dma { uint32_t address,length,duration; };
struct ai_controller {uint32_t regs[6];struct ai_dma fifo[2];uint32_t delayed_carry;};
struct device {struct {struct {uint32_t regs[32];} cp0;} r4300;
 struct ai_controller ai;struct {uint32_t *dram;size_t dram_size;} rdram;
 struct {uint32_t *mem;} sp;};
static struct device g_dev;
static struct {char MD5[33];} ROM_SETTINGS={"7EA59868ADA334E8EC7D050918B22749"};
static const uint32_t *r4300_cp0_regs(const void *p){return (const uint32_t*)p;}
static unsigned records=0,changed=0,flags=0,overlap=0;
static void mkmszr_trace(uint32_t event,uint32_t count,uint32_t a,uint32_t b,
 uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h)
{
 (void)count;(void)a;(void)b;(void)c;(void)d;(void)e;
 records++;if(event==0x83){overlap=f;changed=g;flags=h;}
}
'''

SUFFIX = r'''
static void copy_row(uint32_t dst,uint32_t src,uint32_t bytes)
{
 uint32_t j;
 MKMSZR_PCMBefore(dst,src,bytes,0x120);
 for(j=0;j<bytes;j+=4)
  g_dev.rdram.dram[((dst+j)&0x7ffffcu)/4]=g_dev.sp.mem[((src+j)&0x1ffcu)/4];
 MKMSZR_PCMAfter();
}
int main(int argc,char **argv)
{
 struct ai_controller *ai=&g_dev.ai;
 uint32_t i,before[1024];unsigned baseline;
 if(argc<2)return 90;
 g_dev.rdram.dram_size=0x800000;g_dev.rdram.dram=calloc(0x200000,4);
 g_dev.sp.mem=calloc(0x800,4);if(!g_dev.rdram.dram||!g_dev.sp.mem)return 91;
 for(i=0;i<0x800;i++)g_dev.sp.mem[i]=0x11223344;
 ai->fifo[0].address=0x1000;ai->fifo[0].length=0x400;ai->regs[3]=AI_STATUS_BUSY;
 mkmszr_pcm_accept(ai);MKMSZR_PCMTask(2,0);
 copy_row(0x2000,0,0x400);MKMSZR_PCMTaskEnd(0x243,0);
 ai->fifo[1].address=0x2000;ai->fifo[1].length=0x400;
 ai->regs[3]|=AI_STATUS_FULL;mkmszr_pcm_accept(ai);MKMSZR_PCMTask(2,0);
 for(i=0;i<0x800;i++)g_dev.sp.mem[i]=0x55667788;
 if(!strcmp(argv[1],"off")) {
  if(records)return 1;
  copy_row(0x2000,0,0x100);if(records)return 2;
 } else {
  /* Callbacks alone do not mutate RDRAM or FIFO state. */
  memcpy(before,g_dev.rdram.dram+0x2000/4,0x400);baseline=ai->regs[3];
  MKMSZR_PCMBefore(0x2000,0,0x100,0);MKMSZR_PCMAfter();
  if(memcmp(before,g_dev.rdram.dram+0x2000/4,0x400)||ai->regs[3]!=baseline)return 3;
  copy_row(0x2000,0,0x100);if(changed!=0x100||overlap!=0x100||(flags&63)!=47)return 4;
  copy_row(0x2000,0,0x100);if(changed||overlap!=0x100)return 5;
  copy_row(0x1000,0,0x100);if(overlap)return 6; /* active head is out of scope */
  ai->delayed_carry=1;copy_row(0x2000,0,0x100);if(overlap)return 7;
  copy_row(0x4000,0,0x100);if(changed!=0x100)return 8;
  /* Own-generation queued initialization is not an older-generation violation. */
  ai->delayed_carry=0;ai->fifo[1].address=0x5000;ai->fifo[1].length=0x400;
  mkmszr_pcm_accept(ai);MKMSZR_PCMTask(2,0);copy_row(0x5000,0,0x400);
  if(flags&32 || !changed || mkmszr_pcm.tail_ready_generation)return 13;
  MKMSZR_PCMTaskEnd(0x243,0);
  if(mkmszr_pcm.tail_ready_generation!=mkmszr_pcm.task_id)return 14;
  ai->delayed_carry=0;ai->fifo[1].address=0;copy_row(0x7ffff8,0x1ff8,16);
  if(overlap!=8||changed!=8)return 9; /* physical wrap */
  ai->delayed_carry=0;ai->fifo[0]=ai->fifo[1];ai->regs[3]&=~AI_STATUS_FULL;
  mkmszr_pcm_pop(ai,1);copy_row(0x2000,0,0x100);if(overlap)return 10;
  ai->regs[3]|=AI_STATUS_FULL;ai->fifo[1].address=0x800000;
  copy_row(0x2000,0,0x100);if(!(flags&16)||!mkmszr_pcm.invalid)return 11;
  if(mkmszr_pcm.begins!=mkmszr_pcm.commits)return 12;
 }
 puts("PASS PCM byte-change, identity-rewrite, release/carry/wrap, opt-out and read-only contracts");
 return 0;
}
'''


def row(seq, event, values, ns=None):
    return (seq, 1000000000+seq*1000000 if ns is None else ns, event, seq*100, values)


def decoder_tests():
    session = {"rom_md5": "7ea59868ada334e8ec7d050918b22749"}
    start = [(0x80, [2, 4096, 0, 0, 0, 0, 0, 0]),
             (0x86, [0x7EA59868, 0xADA334E8, 0xEC7D0509, 0x18B22749, 0x800000, 0, 0, 0])]

    def trace(events):
        return {"rows": [row(i, e, v) for i, (e, v) in enumerate(start + events)],
                "overwritten": 0}

    # A whole range completed for THIS lease before another writer mutates it.
    live = [(0x85, [1, 2, 0, 0, 0, 0, 0, 0]),
            (0x81, [1, 0x1000, 256, 2, 0x2000, 256, 0xc0000000, 0]),
            (0x8a, [2, 0, 1, 0x2000, 256, 0xc0000000, 0, 0]),
            (0x83, [0x2000, 256, 2, 0, 2, 256, 128, 79]),
            (0x84, [0x2000, 0x2000, 256, 1, 1, 2, 2, 1]),
            (0x8b, [0, 1, 2, 2, 0, 0, 0, 0]),
            (0x87, [1, 2, 0x243, 0, 0, 0, 0, 0]),
            (0x8a, [2, 1, 1, 0x2000, 256, 0xc0000000, 0, 0]),
            (0x85, [2, 2, 0, 0, 0, 0, 0, 0]),
            (0x83, [0x2000, 256, 2, 0, 2, 256, 128, 47]),
            (0x84, [0x2000, 0x2000, 256, 1, 2, 3, 3, 2]),
            (0x8b, [1, 2, 2, 2, 0, 0, 0, 0]),
            (0x13, [0x80000000, 0, 0, 0, 0, 0, 0, 0]),
            (0x89, [2, 2, 2, 2, 2, 0, 0, 0])]
    onset = {"kind": "audible_onset", "monotonic_ns": 1014000000,
             "uncertainty_seconds": 0.001}
    result = analyze(trace(live), onset, session)
    assert result["verdict"].startswith("DIFFERENT GENERATION")
    assert len(result["committed_tail_mutations"]) == 1
    assert result["committed_tail_mutations"][0]["older_completed_generation"] == 1
    assert result["committed_tail_mutations"][0]["relative_to_first_full_status"] == "before"
    same = list(live)
    same[9] = (0x83, [0x2000, 256, 2, 0, 2, 256, 0, 47])
    assert not analyze(trace(same), onset, session)["committed_tail_mutations"]
    assert analyze(trace(live), onset, {"rom_md5": "wrong"})["missing_evidence"]
    assert analyze({**trace(live), "overwritten": 1}, onset, session)["missing_evidence"]
    assert analyze(trace(live[:-1]), None, session)["missing_evidence"]
    assert analyze({"rows": [], "overwritten": 0}, None, None)["missing_evidence"]
    bad = list(live)
    bad[9] = (0x83, [0x2000, 256, 2, 0, 2, 256, 128, 63])
    assert analyze(trace(bad), onset, session)["missing_evidence"]

    # Mirror real false positive: old directly accepted HEAD has been released.
    reuse = [(0x81, [1, 0x2000, 256, 0, 0, 0, 0x40000000, 0]),
             (0x85, [1, 2, 0, 0, 0, 0, 0, 0]),
             (0x83, [0x2000, 256, 2, 0, 0, 0, 0, 9]),
             (0x87, [1, 2, 0x243, 0, 0, 0, 0, 0]),
             (0x82, [0, 0x2000, 256, 0, 0, 0, 0, 0]),
             (0x85, [2, 2, 0, 0, 0, 0, 0, 0]),
             (0x81, [2, 0x1000, 256, 0, 0, 0, 0x40000000, 0]),
             (0x81, [2, 0x1000, 256, 3, 0x2000, 256, 0xc0000000, 0]),
             (0x8a, [3, 1, 2, 0x2000, 256, 0xc0000000, 0, 0]),
             (0x83, [0x2000, 256, 2, 0, 3, 256, 128, 47]),
             (0x84, [0x2000, 0x2000, 256, 2, 1, 2, 2, 2]),
             (0x8b, [1, 2, 3, 2, 0, 0, 0, 0]),
             (0x87, [2, 2, 0x243, 0, 0, 0, 0, 0]),
             (0x8a, [3, 1, 2, 0x2000, 256, 0xc0000000, 0, 0]),
             (0x82, [3, 0x2000, 256, 0, 0x2000, 256, 0x40000000, 0]),
             (0x89, [2, 2, 2, 1, 1, 0, 0, 0])]
    reused = analyze(trace(reuse), None, session)
    assert not reused["committed_tail_mutations"]
    assert not reused["unqualified_queued_mutations"]
    assert len(reused["completed_before_playback_initialization"]) == 1
    assert reused["released_storage_initialization_instances"] == 1
    assert reused["rom_identity"]["recorded_md5_matches_session"]
    assert reused["rom_identity"]["session_declared_sha256"] is None
    assert not reused["rom_identity"]["rom_bytes_independently_rehashed_by_analyzer"]
    assert reused["first_full_status_seconds_from_vi"] is None
    host_marker = {**onset, "kind": "host_observation"}
    assert analyze(trace(live), host_marker, session)["committed_tail_mutations"][0][
        "relative_to_reported_audio_onset"].startswith("host observation")
    # First half is ready and read while the whole synthesis task is unfinished.
    partial = [(0x81, [1, 0x1000, 256, 0, 0, 0, 0x40000000, 0]),
               (0x85, [1, 2, 0, 0, 0, 0, 0, 0]),
               (0x81, [1, 0x1000, 256, 2, 0x2000, 256, 0xc0000000, 0]),
               (0x83, [0x2000, 128, 2, 0, 2, 128, 128, 79]),
               (0x82, [2, 0x2000, 256, 0, 0x2000, 256, 0x40000000, 0]),
               (0x12, [128, 0x40000000, 256, 1000, 256, 0, 0, 0]),
               (0x83, [0x2080, 128, 2, 0, 0, 0, 0, 9]),
               (0x87, [1, 2, 0x243, 0, 0, 0, 0, 0]),
               (0x14, [0x40000000, 256, 0, 128, 1000, 0, 0, 0])]
    byte_reads = assess_promoted_initialization(replay(trace(partial)["rows"]), {2})
    assert byte_reads["all_particular_words_complete"]
    assert not byte_reads["evidence"][0]["whole_task_complete_before_read"]
    assert byte_reads["fully_read_buffers"] == 1
    premature = list(partial)
    premature[5] = (0x12, [64, 0x40000000, 256, 1000, 256, 0, 0, 0])
    premature_reads = assess_promoted_initialization(replay(trace(premature)["rows"]), {2})
    assert not premature_reads["all_particular_words_complete"]
    assert premature_reads["evidence"][0]["word_writers"] == [0, 1]
    assert premature_reads["host_pairs_verified"] is None
    print("PASS decoder separates stale storage from a proven LIVE lease replacement")
    print("PASS byte readiness is independent of whole-task completion; unwritten read is rejected")


def main():
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp)/"pcm.c"
        binary = Path(temp)/"pcm"
        source.write_text(PREFIX+CORE_PROBE+SUFFIX)
        subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(source), "-o", str(binary)], check=True)
        for mode in ["off", "on"]:
            env = dict(os.environ)
            env["MKMSZR_TRACE"] = "1"
            env["MKMSZR_TRACE_PCM"] = "1" if mode == "on" else "0"
            subprocess.run([str(binary), mode], env=env, check=True)
        # Visibility alone cannot override a GNU export allowlist.
        version = Path(temp)/"export.ver"
        version.write_text('{global: MKMSZR_PCMBefore; MKMSZR_PCMAfter; MKMSZR_PCMTask; MKMSZR_PCMTaskEnd; '
                           'local: *; };\n')
        shared = Path(temp)/"pcm.so"
        subprocess.run(["cc", "-std=c11", "-fPIC", "-shared", "-fvisibility=hidden",
                        str(source), "-o", str(shared),
                        "-Wl,--version-script="+str(version)], check=True)
        lib = ctypes.CDLL(str(shared))
        for name in ["MKMSZR_PCMBefore", "MKMSZR_PCMAfter", "MKMSZR_PCMTask", "MKMSZR_PCMTaskEnd"]:
            getattr(lib, name)
        print("PASS diagnostic callbacks resolve across shared-library export boundary")
    decoder_tests()


if __name__ == "__main__":
    main()
