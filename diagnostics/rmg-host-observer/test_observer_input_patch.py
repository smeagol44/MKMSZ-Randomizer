"""Pinned-input-probe injection and standalone C opt-in/record-format test."""
from __future__ import annotations

import ast
import os
from pathlib import Path
import struct
import subprocess
import tempfile

from observer_input_patch import INJECT, apply


def observer_header() -> str:
    source = ast.parse(Path(__file__).with_name("observer_patch.py").read_text())
    for node in source.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "HEADER" for t in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError("Shared v01 trace header not found")


MOCK = '''
#include <string.h>
#include "device/r4300/r4300_core.h"
#define MKMSZR_TRACE_CAP 131072u
#define MKMSZR_TRACE_CHANNEL "input"
#include "mkmszr_trace.h"
void update_pif_ram(struct pif* pif)
{
    size_t k;
    for (k=0; k<PIF_CHANNELS_COUNT; ++k) { process_channel(&pif->channels[k]); }
    if (input.readController) { input.readController(-1, NULL); }
    netplay_update_input(pif);
}
'''


def program() -> str:
    return r"""
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
enum { PIF_CHANNELS_COUNT = 5, PIF_RAM_SIZE = 0x40, CP0_COUNT_REG = 9 };
struct cp0 { uint32_t regs[32]; };
struct r4300_core { struct cp0 cp0; };
struct pif_channel {
    void *jbd, *ijbd;
    uint8_t *tx, *tx_buf, *rx, *rx_buf;
};
struct pif {
    uint8_t *base, *ram;
    struct pif_channel channels[PIF_CHANNELS_COUNT];
    struct r4300_core *r4300;
};
static uint32_t *r4300_cp0_regs(struct cp0 *p) { return p->regs; }
#define MKMSZR_TRACE_CAP 256u
#define MKMSZR_TRACE_CHANNEL "input"
""" + observer_header() + INJECT + r"""
int main(void)
{
    uint8_t ram[PIF_RAM_SIZE] = {0};
    struct r4300_core core = {0};
    struct pif pif = {0};
    struct pif_channel *ch;
    pif.ram = ram;
    pif.r4300 = &core;
    core.cp0.regs[CP0_COUNT_REG] = 0x12345678u;
    ch = &pif.channels[0];
    ch->tx = ram;
    ch->rx = ram+1;
    ch->tx_buf = ram+2;
    ch->rx_buf = ram+3;
    ram[0] = 1;
    ram[1] = 4;
    ram[2] = 1;     /* JCMD_CONTROLLER_READ */
    ram[3] = 0;
    ram[4] = 8;     /* D-pad Up bit 0x0800 */
    ram[5] = 0xe2;  /* X = -30 */
    ram[6] = 0x2d;  /* Y = +45 */
    mkmszr_input_observe_joybus(&pif);
    if (getenv("MKMSZR_TRACE_INPUT") != NULL &&
        strcmp(getenv("MKMSZR_TRACE_INPUT"), "1") == 0 &&
        getenv("MKMSZR_TRACE") != NULL)
    {
        const mkmszr_trace_record *r = &mkmszr_trace_store.ring[0];
        if (mkmszr_trace_store.total != 1 || r->event != 0x60 ||
            r->guest_count != 0x12345678u || r->a != 0 ||
            r->b != 0x2de20800u || r->c != 0x0800u ||
            r->d != (uint32_t)-30 || r->e != 45u || r->f != 0u)
            return 13;
    }
    else if (mkmszr_trace_store.total != 0)
        return 14;
    return 0;
}
"""


def test() -> None:
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        mock = root / "pif.c"
        mock.write_text(MOCK)
        apply(mock)
        changed = mock.read_text()
        assert changed.count("mkmszr_input_observe_joybus") == 2
        assert changed.index("netplay_update_input(pif);") < changed.index(
            "mkmszr_input_observe_joybus(pif);"
        )
        try:
            apply(mock)
        except RuntimeError as err:
            assert "already installed" in str(err)
        else:
            raise AssertionError("Observer installed twice without error")
        binary = root / "pif-input-test"
        cpath = root / "test.c"
        cpath.write_text(program())
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function",
             str(cpath), "-o", str(binary)], check=True
        )
        off = root / "off"
        on = root / "on"
        off.mkdir()
        on.mkdir()
        subprocess.run([str(binary)], check=True, env={
            **os.environ, "XDG_CACHE_HOME": str(off),
            "MKMSZR_TRACE": "1", "MKMSZR_TRACE_INPUT": "0",
        })
        assert list(off.iterdir()) == [], "Disabled probe wrote file"
        subprocess.run([str(binary)], check=True, env={
            **os.environ, "XDG_CACHE_HOME": str(on),
            "MKMSZR_TRACE": "1", "MKMSZR_TRACE_INPUT": "1",
        })
        blob = (on / "mkmszr-input-trace.bin").read_bytes()
        hdr = struct.unpack_from("=8sIIQQQ", blob)
        assert hdr == (b"MZRHST1\0", 1, 56, 1, 1, 0)
        assert len(blob) == 40 + 56
        row = struct.unpack_from("=QQ10I", blob, 40)
        assert row[0] == 0 and row[2] == 0x60 and row[3] == 0x12345678
        assert row[4] == 0 and row[5] == 0x2de20800 and row[6] == 0x800
        print("PASS: RMG input probe pinned anchors, C build, response and opt-out")


if __name__ == "__main__":
    test()
