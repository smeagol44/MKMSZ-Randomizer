#!/usr/bin/env python3
"""Decode the experimental MKMSZR RMG host-side observer traces.

Read-only stdlib. Supply one or more mkmszr-*-trace.bin files.
All timestamps are host CLOCK_MONOTONIC nanoseconds; cross-ring alignment is
approximate. Guest Count is only meaningful within same emulator run.
"""
import argparse
from collections import Counter
from pathlib import Path
import struct

HEADER = struct.Struct("=8sIIQQQ")
# The C structure has uint64_t sequence/ns, ten uint32_t event/count/a...h.
RECORD = struct.Struct("=QQ10I")
EVENTS = {
    0x10: "AI enqueue attempt",
    0x11: "AI enqueue after",
    0x12: "AI_LEN read",
    0x13: "AI_STATUS read",
    0x14: "AI dma end before",
    0x15: "AI dma end after",
    0x20: "VI callback",
    0x21: "VI next due",
    0x30: "RSP execute before",
    0x31: "RSP execute after",
    0x32: "RSP interrupt",
    0x33: "RSP task event",
    0x50: "SDL request",
    0x51: "SDL host drop",
    0x52: "SDL push result",
}


def read(path: Path):
    blob = path.read_bytes()
    if len(blob) < HEADER.size:
        raise ValueError(f"{path}: too small")
    magic, version, size, saved, total, lost = HEADER.unpack_from(blob)
    if magic.rstrip(b"\x00") != b"MZRHST1" or version != 1 or size != RECORD.size:
        raise ValueError(
            f"{path}: incompatible signature/version/record size: "
            f"{magic!r} {version} {size}"
        )
    if saved > 32768 or total < saved or lost != total - saved:
        raise ValueError(f"{path}: invalid ring header")
    if len(blob) != HEADER.size + saved * RECORD.size:
        raise ValueError(f"{path}: truncated or trailing data")
    rows = []
    prev_seq = None
    prev_ns = None
    for i in range(saved):
        row = RECORD.unpack_from(blob, HEADER.size + i * RECORD.size)
        seq, ns, event, count, *values = row
        if prev_seq is not None and seq != prev_seq + 1:
            raise ValueError(f"{path}: sequence gap inside persisted ring")
        if prev_ns is not None and ns < prev_ns:
            raise ValueError(f"{path}: non-monotonic timestamp")
        rows.append((seq, ns, event, count, values))
        prev_seq, prev_ns = seq, ns
    if rows and rows[0][0] != lost:
        raise ValueError(f"{path}: ring first sequence mismatch")
    return dict(path=str(path), saved=saved, total=total, overwritten=lost, rows=rows)


def report(trace):
    rows = trace["rows"]
    counts = Counter(row[2] for row in rows)
    print(f"\n{trace['path']}: total={trace['total']} "
          f"saved={trace['saved']} overwritten={trace['overwritten']}")
    for event, count in sorted(counts.items()):
        print(f"  {EVENTS.get(event, f'UNKNOWN 0x{event:X}')}: {count}")
    if rows:
        print(f"  host span: {(rows[-1][1] - rows[0][1]) / 1e9:.3f} seconds")
    if trace["overwritten"]:
        print("  NOTE: early events were overwritten; do not infer no earlier failures")
    host_drop_bytes = sum(row[4][0] for row in rows if row[2] == 0x51)
    host_push_failed = sum(row[4][3] == 0 for row in rows if row[2] == 0x52)
    if 0x50 in counts or 0x51 in counts or 0x52 in counts:
        print(f"  host-drop bytes in retained window: {host_drop_bytes}")
        print(f"  SDL push returned false in retained window: {host_push_failed}")
    if 0x13 in counts:
        full_reads = sum(bool(row[4][0] & 0x80000000) for row in rows if row[2] == 0x13)
        print(f"  AI_STATUS FULL reads in retained window: {full_reads}")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("traces", nargs="+", type=Path)
    args = ap.parse_args()
    for path in args.traces:
        report(read(path))

if __name__ == "__main__":
    main()
