#!/usr/bin/env python3
"""MKMSZR Sektor straight-missile v81 first-render transaction proof.

Input: exact Runtime-confirmed v75 missile baseline.
Output: disposable v81 proof.

This is deliberately NOT a production patch.  It preserves v75 placement, flight,
child ownership, Ice companion/tint process lifecycles, collision, and cleanup.
It changes only the two linked pieces of the projectile's *pre-insertion first-render
transaction*:

  1. the live slot-0x24 token-0x0B constructor operand is switched from the Ice
     resource entry to the already-imported genuine ROCKETD1 resource entry; and
  2. the token handler's pre-insertion actor palette selector store is forced to
     selector 0, matching the native Sektor TLUT already used successfully by v75's
     later rocket-frame wrapper.

The selector-store edit is intentionally global to token-0x0B construction in this
disposable diagnostic.  It is NOT a production/generic adapter implementation.
If runtime validates the seam, a later generic adapter wrapper must scope palette
binding to the projectile transaction and own palette lifetime explicitly.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

V75_SHA256 = "e77b334ffa8cc2d55500b22d2047560190ceec935cb390b256fe939244e9c2fb"
ROM_SIZE = 0x1000000

# Exact v75 proof facts / guarded edits.
FILE87_ROM_BASE = 0x00F40000
SLOT24_ROOT_REL = 0x00000DA0
LIVE_TOKEN_REL = 0x00000DB8
LIVE_OPERAND_REL = 0x00000DBC
ICE_ENTRY_REL = 0x00034A58
ROCKET_ENTRY_REL = 0x0004E6E4
CHILD_CURSOR_ENTRY_REL = 0x00000FD0
ROCKET_LOOP_REL = 0x00000D90

TOKEN_PALETTE_STORE_ROM = 0x000315E8   # VA 0x800309E8 inside token-0x0B handler
STOCK_SELECTOR_STORE = 0xA602009E      # sh v0,0x009e(s0)
PROOF_SELECTOR_STORE = 0xA600009E      # sh zero,0x009e(s0)


def be16(buf: bytearray | bytes, off: int) -> int:
    return int.from_bytes(buf[off:off+2], "big")


def be32(buf: bytearray | bytes, off: int) -> int:
    return int.from_bytes(buf[off:off+4], "big")


def put32(buf: bytearray, off: int, value: int) -> None:
    buf[off:off+4] = int(value & 0xFFFFFFFF).to_bytes(4, "big")


def rol32(v: int, s: int) -> int:
    s &= 31
    if s == 0:
        return v & 0xFFFFFFFF
    return ((v << s) | (v >> (32 - s))) & 0xFFFFFFFF


def update_crc_6102(rom: bytearray) -> tuple[int, int]:
    seed = 0xF8CA4DDC
    t1 = t2 = t3 = t4 = t5 = t6 = seed
    for off in range(0x1000, 0x101000, 4):
        value = be32(rom, off)
        total = (t6 + value) & 0xFFFFFFFF
        if total < t6:
            t4 = (t4 + 1) & 0xFFFFFFFF
        t6 = total
        t3 ^= value
        r = rol32(value, value & 31)
        t5 = (t5 + r) & 0xFFFFFFFF
        t2 ^= r if t2 > value else (t6 ^ value)
        t1 = (t1 + (t5 ^ value)) & 0xFFFFFFFF
    crc1 = (t6 ^ t4 ^ t3) & 0xFFFFFFFF
    crc2 = (t5 ^ t2 ^ t1) & 0xFFFFFFFF
    put32(rom, 0x10, crc1)
    put32(rom, 0x14, crc2)
    return crc1, crc2


def ranges_of_differences(a: bytes, b: bytes) -> list[tuple[int, int]]:
    assert len(a) == len(b)
    diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if not diffs:
        return []
    out: list[tuple[int, int]] = []
    start = prev = diffs[0]
    for i in diffs[1:]:
        if i == prev + 1:
            prev = i
        else:
            out.append((start, prev + 1))
            start = prev = i
    out.append((start, prev + 1))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline", type=Path, help="exact v75 ROM")
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    baseline = args.baseline.read_bytes()
    assert len(baseline) == ROM_SIZE, hex(len(baseline))
    got_sha = hashlib.sha256(baseline).hexdigest()
    assert got_sha == V75_SHA256, (got_sha, V75_SHA256)
    rom = bytearray(baseline)

    # --- Guard the resolved live constructor site. ---
    rr = FILE87_ROM_BASE
    assert be32(rom, rr + SLOT24_ROOT_REL) == ICE_ENTRY_REL
    assert be32(rom, rr + LIVE_TOKEN_REL) == 0x0000000B
    assert be32(rom, rr + LIVE_OPERAND_REL) == ICE_ENTRY_REL
    assert be32(rom, rr + ROCKET_ENTRY_REL) == ROCKET_ENTRY_REL + 8

    # Exact-v75 child cursor already resolves to the genuine rocket loop.
    # This proof intentionally does NOT touch child entry/cursor/flight machinery.
    assert be32(rom, rr + CHILD_CURSOR_ENTRY_REL) == ROCKET_LOOP_REL
    rocket_loop = [be32(rom, rr + ROCKET_LOOP_REL + 4*i) for i in range(4)]
    assert rocket_loop[0] == rocket_loop[1]
    assert rocket_loop[2:] == [1, ROCKET_LOOP_REL]

    # Guard the first-render palette seam in the stock token-0x0B handler.
    assert be32(rom, TOKEN_PALETTE_STORE_ROM) == STOCK_SELECTOR_STORE

    # Preserve the runtime-confirmed v75 placement and Ice helper process spawns.
    assert be32(rom, 0x4BBF0) == 0x24050005   # addiu a1,zero,+5
    assert be32(rom, 0x4BBFC) == 0x24060026   # addiu a2,zero,+38
    assert be32(rom, 0x4BC00) == 0x0C00C482   # jal 0x80031208
    assert be32(rom, 0x4BA68) == 0x0C00A0C3   # jal 0x8002830C
    assert be32(rom, 0x4BA84) == 0x0C00A0C3   # jal 0x8002830C

    # Preserve v75 child/callback route and calibrated constants.
    assert be32(rom, 0x4C484) == 0x080268A4   # j 0x8009A290
    assert be32(rom, 0x4C488) == 0x3C0A800A   # delay preload
    assert be32(rom, 0x9AE90) == 0x3C08802F
    assert be32(rom, 0x9AEB8) == 0x254AA2C8   # addiu t2,t2,-0x5D38 -> callback VA 0x8009A2C8
    # Input remains Forward, Forward + Low Punch, mirrored by facing.
    assert be16(rom, 0xB1B4A) == 9 and be16(rom, 0xB1B4C) == 9
    assert be16(rom, 0xB1B56) == 8 and be16(rom, 0xB1B58) == 8

    # --- v81: paired pre-insertion first-render transaction. ---
    put32(rom, rr + LIVE_OPERAND_REL, ROCKET_ENTRY_REL)
    put32(rom, TOKEN_PALETTE_STORE_ROM, PROOF_SELECTOR_STORE)

    crc1, crc2 = update_crc_6102(rom)

    # Exact-scope audit: apart from header CRC words, only the two guarded sites may differ.
    out = bytes(rom)
    diff_ranges = ranges_of_differences(baseline, out)
    allowed = {
        (0x10, 0x18),
        (TOKEN_PALETTE_STORE_ROM, TOKEN_PALETTE_STORE_ROM + 4),
        (rr + LIVE_OPERAND_REL, rr + LIVE_OPERAND_REL + 4),
    }
    # CRC byte differences can be subranges of 0x10..0x18, so validate every byte instead.
    for start, end in diff_ranges:
        for off in range(start, end):
            assert (0x10 <= off < 0x18) or \
                   (TOKEN_PALETTE_STORE_ROM <= off < TOKEN_PALETTE_STORE_ROM + 4) or \
                   (rr + LIVE_OPERAND_REL <= off < rr + LIVE_OPERAND_REL + 4), hex(off)

    args.output.write_bytes(out)
    print("OUTPUT", args.output)
    print("SHA256", hashlib.sha256(out).hexdigest())
    print("CRC1/CRC2", f"{crc1:08X} / {crc2:08X}")
    print("TEST_INPUT", "Forward, Forward + Low Punch")
    print("BASELINE", "exact Runtime-confirmed v75", V75_SHA256)
    print("CHANGE_1", "file87 +0xDBC constructor operand: +0x34A58 -> +0x4E6E4")
    print("CHANGE_2", "VA 0x800309E8 pre-insertion palette selector store: returned Ice selector -> 0")
    print("UNCHANGED", "v75 (+5,+38) placement; child ownership; acceleration/cadence; helpers/tint; collision; cleanup")
    print("NOTE", "selector-store patch is disposable token-0x0B diagnostic scope, not production adapter code")


if __name__ == "__main__":
    main()
