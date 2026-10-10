"""Align guest-visible PIF controller reads with emulated VI/audio events.

Usage: python3 analyze_input_audio_alignment.py --folder /path/to/traces \
  --report controller-audio-alignment.json --edges controller-edges.csv
Read-only, ROM-free; no emulator, hardware access, or guest clock changes.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
from pathlib import Path
import struct

H = struct.Struct("=8sIIQQQ")
R = struct.Struct("=QQ10I")

BUTTONS = (
    (0x0001, "D-right"), (0x0002, "D-left"),
    (0x0004, "D-down"), (0x0008, "D-up"),
    (0x0010, "Start"), (0x0020, "Z"), (0x0040, "B"), (0x0080, "A"),
    (0x0100, "C-right"), (0x0200, "C-left"), (0x0400, "C-down"),
    (0x0800, "C-up"), (0x1000, "R"), (0x2000, "L"),
)
# Important: the BUTTONS struct in pinned RMG's m64p_plugin.h has the
# above host bitfield order. The PIF reply itself is 4 raw Joybus bytes;
# do not infer event names by treating its first two bytes as a host uint16.


def read(path: Path) -> tuple[list[tuple], dict]:
    blob = path.read_bytes()
    if len(blob) < H.size:
        raise ValueError(f"Missing observer header: {path}")
    magic, version, record_size, saved, total, overwritten = H.unpack_from(blob)
    if (magic, version, record_size) != (b"MZRHST1\x00", 1, R.size):
        raise ValueError(f"Unsupported observer format: {path}")
    if overwritten or total != saved or len(blob) != H.size + saved * R.size:
        raise ValueError(f"Truncated or overwritten observer trace: {path}")
    rows = [R.unpack_from(blob, H.size + R.size * i)
            for i in range(saved)]
    if any(r[0] != i for i, r in enumerate(rows)):
        raise ValueError(f"Broken trace sequence: {path}")
    return rows, {
        "filename": path.name,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "saved": saved,
        "lost": overwritten,
    }


def decode_buttons(mask: int) -> str:
    return "+".join(name for bit, name in BUTTONS if mask & bit) or "none"


def input_edges(input_records: list[tuple], vi_records: list[tuple]) -> list[dict]:
    vi = [r for r in vi_records if r[2] == 0x20]
    vi_ns = [r[1] for r in vi]
    if not vi:
        raise ValueError("No VI event timeline")
    first_ns = vi_ns[0]
    last = {}
    edges = []
    for r in input_records:
        if r[2] != 0x60:
            continue
        port = r[4]
        if port > 3:
            continue
        raw = r[5]
        buttons = r[6]
        flags = r[9]
        state = (buttons, r[7], r[8], flags)
        prev = last.get(port)
        last[port] = state
        if prev == state:
            continue
        vindex = bisect.bisect_right(vi_ns, r[1]) - 1
        edges.append({
            "port": port,
            "t_vi_seconds": round((r[1] - first_ns) / 1e9, 6),
            "vi_event_index": vindex if vindex >= 0 else None,
            "guest_count_snapshot": r[3],
            "buttons_hex": f"0x{buttons:04x}",
            "buttons": decode_buttons(buttons) if flags == 0 else "invalid reply",
            "changed_buttons_hex": (
                f"0x{(prev[0] ^ buttons) if prev is not None else buttons:04x}"
            ),
            "stick_x": (r[7] if r[7] < 0x80000000 else r[7] - 0x100000000),
            "stick_y": (r[8] if r[8] < 0x80000000 else r[8] - 0x100000000),
            "reply_flags": flags,
            "raw_joybus_response_hex": f"{raw:08x}",
        })
    return edges


def rejected_audio_services(ai: list[tuple], start_ns: int) -> list[float]:
    first_status = None
    events = []
    for r in ai:
        if r[2] == 0x13 and first_status is None:
            first_status = r
        elif r[2] == 0x12:
            if first_status is not None and first_status[4] & 0x80000000:
                events.append((first_status[1] - start_ns) / 1e9)
            first_status = None
    return events


def severe_bursts(times: list[float], min_events: int = 10) -> list[dict]:
    clusters = []
    current = []
    for t in times:
        if current and t - current[-1] > 0.09:
            if len(current) >= min_events:
                clusters.append({"start_s": current[0], "end_s": current[-1],
                                 "rejections": len(current)})
            current = []
        current.append(t)
    if len(current) >= min_events:
        clusters.append({"start_s": current[0], "end_s": current[-1],
                         "rejections": len(current)})
    return clusters


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--edges", type=Path, required=True)
    args = parser.parse_args()
    inp, inp_meta = read(args.folder / "mkmszr-input-trace.bin")
    vi, vi_meta = read(args.folder / "mkmszr-vi-trace.bin")
    ai, ai_meta = read(args.folder / "mkmszr-ai-trace.bin")
    vi_events = [r for r in vi if r[2] == 0x20]
    epoch = vi_events[0][1]
    edges = input_edges(inp, vi)
    rejections = rejected_audio_services(ai, epoch)
    bursts = severe_bursts(rejections)
    comparisons = []
    for burst in bursts:
        start = burst["start_s"]
        port_zero_edges = [
            e for e in edges if e["port"] == 0
            and start - 10 <= e["t_vi_seconds"] <= start
        ]
        comparisons.append({
            "audio_burst": burst,
            "controller0_edges_in_previous_10_seconds": port_zero_edges,
            "controller0_edges_last_5_seconds": sum(
                e["t_vi_seconds"] >= start - 5 for e in port_zero_edges
            ),
        })
    report = {
        "format": "MKMSZR_rmg_pif_input_v05",
        "streams": {"input": inp_meta, "vi": vi_meta, "ai": ai_meta},
        "joybus_response_samples": sum(r[2] == 0x60 for r in inp),
        "controller_changes": len(edges),
        "native_full_rejection_events": len(rejections),
        "sustained_fifo_bursts": bursts,
        "input_at_precursors": comparisons,
        "limits": [
            "Records responses to guest PIF controller READ requests; not physical SDL timestamps.",
            "Only PIF command replies are known, not internal MKMSZ Inventory cursor moves.",
            "Input samples carry read-only CP0 Count, not a cp0_update_count call.",
            "Host monotonic clock aligns streams within one running emulator process only.",
            "Controller responses may postdate a VI callback; VI association is observational.",
            "An input edge before a FIFO failure is correlation, not causal attribution.",
            "Existing v04 traces did not have input recording and cannot be backfilled.",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    with args.edges.open("w", newline="") as f:
        fields = list(edges[0]) if edges else [
            "port", "t_vi_seconds", "vi_event_index",
            "guest_count_snapshot", "buttons_hex", "buttons",
            "changed_buttons_hex", "stick_x", "stick_y", "reply_flags",
            "raw_joybus_response_hex",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(edges)
    print("Input PIF responses:", report["joybus_response_samples"])
    print("Input changes:", len(edges), "Severe native bursts:", len(bursts))


if __name__ == "__main__":
    main()
