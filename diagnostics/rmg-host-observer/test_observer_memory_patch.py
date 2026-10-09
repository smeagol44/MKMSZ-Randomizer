"""Synthetic smoke: exact patch anchors + native C source observes but never writes."""
import os
import subprocess
import tempfile
from pathlib import Path

from observer_memory_patch import INJECT, apply


PREFIX = r"""
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define CP0_COUNT_REG 9
struct cp0 { uint32_t regs[32]; };
struct rdram { uint32_t* dram; size_t dram_size; };
struct r4300_core { struct cp0 cp0; struct rdram* rdram; };
struct mi_controller { struct r4300_core* r4300; };
struct vi_controller { struct mi_controller* mi; };
static const uint32_t* r4300_cp0_regs(const struct cp0* x) {return x->regs;}
static unsigned count=0, flags=0, cursor=0;
static void mkmszr_trace(uint32_t id, uint32_t cp0,
 uint32_t a, uint32_t b, uint32_t c, uint32_t d,
 uint32_t e, uint32_t f, uint32_t g, uint32_t h)
{
  (void)cp0;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;
  if (id==0x40) { count++;cursor=a;flags=h; }
  if (id==0x41) count++;
}
"""

SUFFIX = r"""
int main(void)
{
  struct rdram ram;
  struct r4300_core cpu = {0};
  struct mi_controller mi = {0};
  struct vi_controller vi = {0};
  uint32_t before=0,after=0,i;
  ram.dram_size=0x800000u;
  ram.dram=calloc(ram.dram_size/4,4);
  if(!ram.dram) return 5;
  ram.dram[0x111eccu/4u]=0x8028c538u;
  ram.dram[0x0eecd0u/4u]=0x801b3420u;
  ram.dram[0x1b2de0u/4u]=0x801feba0u;
  ram.dram[0x1af7d0u/4u]=0x4d4b5356u;
  cpu.rdram=&ram;mi.r4300=&cpu;vi.mi=&mi;
  for(i=0;i<ram.dram_size/4;i++) before ^= ram.dram[i]+i;
  mkmszr_memory_probe(&vi);
  for(i=0;i<ram.dram_size/4;i++) after ^= ram.dram[i]+i;
  free(ram.dram);
  if(before!=after || count!=2 || flags!=31 || cursor!=0x8028c538u) return 6;
  puts("PASS: two read-only events, correct flags, no memory mutation");
  return 0;
}
"""


def test() -> None:
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        f=d/"mock_vi.c"
        f.write_text('#include "device/memory/memory.h"\n'
                     '#include "mkmszr_trace.h"\n'
                     'unsigned int vi_clock_from_tv_standard(void) {return 0;}\n'
                     'void vi_vertical_interrupt_event(void) {\n'
                     '    new_vi();\n}\n')
        apply(f)
        s=f.read_text()
        assert s.count('mkmszr_memory_probe(vi);')==1
        assert s.count('#include "device/rdram/rdram.h"')==1
        try:
            apply(f)
        except RuntimeError as e:
            assert "already installed" in str(e)
        else:
            raise AssertionError("missing double-apply guard")
        c=d/"synthetic.c"
        c.write_text(PREFIX+INJECT+SUFFIX)
        binary=d/"synthetic"
        subprocess.run(["cc","-std=c11","-O2","-Wall","-Wextra","-Werror",
                        str(c),"-o",str(binary)],check=True)
        env={**os.environ,"MKMSZR_TRACE":"1","MKMSZR_TRACE_MEM":"1"}
        subprocess.run([str(binary)],env=env,check=True)
        print("PASS: pinned-anchor injection and idempotence")


if __name__ == "__main__":
    test()
