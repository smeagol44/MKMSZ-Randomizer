#!/usr/bin/env python3
"""Reproduce the Runtime-confirmed normal Ice Blast -> Pickup cancel proof.

Proof-only. The helper addresses are disposable proof ownership and MUST NOT be
treated as production-free caves.

The script intentionally accepts only the exact Wind placement-probe v04 base
used for the accepted 2026-10-02 runtime test.

Behavior:
- ordinary pickup manager still owns pickup input/proximity/facing checks;
- its action gate additionally accepts normal ground Ice Blast only;
- normal Ice root is identified as controller +0x6F0 == 0x8004AB84;
- native Ice mode 0x80111F98 must be zero, excluding directional variants;
- only after stock pickup gates pass is special lock 0x800BF308 cleared;
- stock then installs its ordinary pickup action/state/callback.

Air Ice Blast and Directional Ice are outside this proof.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

BASE_SHA = "5a431c048f6cbaefa4337357e7fede6ae9b9ce013b16cbcd5ea6040f5678286a"

ACTION_HELPER_ROM = 0x0009AE00
ACTION_HELPER_VA  = 0x8009A200
COMMIT_HELPER_ROM = 0x0009AE40
COMMIT_HELPER_VA  = 0x8009A240

ACTION_GATE_ROM = 0x00039AF8   # VA 0x80038EF8
COMMIT_ROM      = 0x00039BA4   # VA 0x80038FA4

ACTION_GATE_EXPECTED = bytes.fromhex(
    "948306AA "  # lhu v1,+0x6AA(a0)
    "14620034 "  # bne v1,v0,skip
    "00000000"
)
COMMIT_EXPECTED = bytes.fromhex(
    "3C04802C "
    "8C841AC0"
)

R = {
    "zero":0,"v0":2,"v1":3,"a0":4,"a1":5,"a2":6,"a3":7,
    "t0":8,"t1":9,"sp":29,"ra":31,
}

def i(op, rs, rt, imm):
    return ((op & 0x3F) << 26) | (R[rs] << 21) | (R[rt] << 16) | (imm & 0xFFFF)
def j(op, target):
    return ((op & 0x3F) << 26) | ((target >> 2) & 0x03FFFFFF)
def r(rs, rt, rd, sa, fn):
    return (R[rs] << 21) | (R[rt] << 16) | (R[rd] << 11) | ((sa & 31) << 6) | (fn & 63)
def lhu(rt, off, base): return i(0x25, base, rt, off)
def lw(rt, off, base): return i(0x23, base, rt, off)
def sh(rt, off, base): return i(0x29, base, rt, off)
def addiu(rt, rs, imm): return i(0x09, rs, rt, imm)
def lui(rt, imm): return i(0x0F, "zero", rt, imm)
def ori(rt, rs, imm): return i(0x0D, rs, rt, imm)
def beq(rs, rt, imm): return i(0x04, rs, rt, imm)
def bne(rs, rt, imm): return i(0x05, rs, rt, imm)
def jr(rs): return r(rs, "zero", "zero", 0, 0x08)
def jal(target): return j(0x03, target)
NOP = 0

def blob(words):
    return b"".join((w & 0xFFFFFFFF).to_bytes(4, "big") for w in words)

# Called at the stock action gate with:
#   a0 = live player controller
#   v0 = stock accepted action 0x303
# Return v1 as stock would, except normal ground Ice Blast is normalized to
# 0x303 so stock Pickup input/proximity logic is allowed to continue.
ACTION_HELPER = blob([
    lhu("v1",0x6AA,"a0"),
    addiu("t0","zero",0x303),
    beq("v1","t0",11), NOP,
    lw("t0",0x6F0,"a0"),
    lui("t1",0x8004), ori("t1","t1",0xAB84),
    bne("t0","t1",6), NOP,
    lui("t0",0x8011), lhu("t0",0x1F98,"t0"),
    bne("t0","zero",2), NOP,
    addiu("v1","zero",0x303),
    jr("ra"), NOP,
])
assert len(ACTION_HELPER) == 0x40

# Called only after stock pickup interaction/spatial gates have passed.
# Replay displaced player-controller load, then clear the native Ice special
# lock only when this is really normal ground Ice Blast.
COMMIT_HELPER = blob([
    lui("a0",0x802C), lw("a0",0x1AC0,"a0"),
    beq("a0","zero",12), NOP,
    lw("t0",0x6F0,"a0"),
    lui("t1",0x8004), ori("t1","t1",0xAB84),
    bne("t0","t1",7), NOP,
    lui("t0",0x8011), lhu("t0",0x1F98,"t0"),
    bne("t0","zero",3), NOP,
    lui("t0",0x800C), sh("zero",0xF308,"t0"),
    jr("ra"), NOP,
])
assert len(COMMIT_HELPER) == 0x44
assert COMMIT_HELPER_ROM == ACTION_HELPER_ROM + len(ACTION_HELPER)

ACTION_HOOK = blob([
    jal(ACTION_HELPER_VA),
    NOP,
    bne("v1","v0",0x33),  # resume stock skip target 0x80038FD0
])
COMMIT_HOOK = blob([jal(COMMIT_HELPER_VA), NOP])

def rol(v, s):
    s &= 31
    return v & 0xFFFFFFFF if not s else ((v << s) | (v >> (32 - s))) & 0xFFFFFFFF

def crc6102(data: bytearray):
    seed = 0xF8CA4DDC
    t1=t2=t3=t4=t5=t6=seed
    for off in range(0x1000, 0x101000, 4):
        d = int.from_bytes(data[off:off+4], "big")
        if ((t6+d) & 0xFFFFFFFF) < t6:
            t4 = (t4+1) & 0xFFFFFFFF
        t6 = (t6+d) & 0xFFFFFFFF
        t3 ^= d
        rr = rol(d, d & 31)
        t5 = (t5+rr) & 0xFFFFFFFF
        t2 ^= rr if t2 > d else (t6 ^ d)
        t1 = (t1 + (t5 ^ d)) & 0xFFFFFFFF
    return (t6^t4^t3) & 0xFFFFFFFF, (t5^t2^t1) & 0xFFFFFFFF

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base_rom", type=Path)
    ap.add_argument("output_rom", type=Path)
    args = ap.parse_args()

    base = args.base_rom.read_bytes()
    sha = hashlib.sha256(base).hexdigest()
    if sha != BASE_SHA:
        raise SystemExit(f"wrong proof base: {sha}")

    b = bytearray(base)
    if b[ACTION_GATE_ROM:ACTION_GATE_ROM+len(ACTION_GATE_EXPECTED)] != ACTION_GATE_EXPECTED:
        raise SystemExit("pickup action gate drifted")
    if b[COMMIT_ROM:COMMIT_ROM+len(COMMIT_EXPECTED)] != COMMIT_EXPECTED:
        raise SystemExit("pickup commit seam drifted")
    helper_end = ACTION_HELPER_ROM + len(ACTION_HELPER) + len(COMMIT_HELPER)
    if any(b[ACTION_HELPER_ROM:helper_end]):
        raise SystemExit("proof helper cave no longer zero")

    b[ACTION_HELPER_ROM:ACTION_HELPER_ROM+len(ACTION_HELPER)] = ACTION_HELPER
    b[COMMIT_HELPER_ROM:COMMIT_HELPER_ROM+len(COMMIT_HELPER)] = COMMIT_HELPER
    b[ACTION_GATE_ROM:ACTION_GATE_ROM+len(ACTION_HOOK)] = ACTION_HOOK
    b[COMMIT_ROM:COMMIT_ROM+len(COMMIT_HOOK)] = COMMIT_HOOK

    crc1, crc2 = crc6102(b)
    b[0x10:0x14] = crc1.to_bytes(4, "big")
    b[0x14:0x18] = crc2.to_bytes(4, "big")
    args.output_rom.write_bytes(b)

    print("base SHA-256", sha)
    print("output SHA-256", hashlib.sha256(b).hexdigest())
    print("CRC1/CRC2", f"{crc1:08X} / {crc2:08X}")

if __name__ == "__main__":
    main()
