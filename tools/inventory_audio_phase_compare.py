#!/usr/bin/env python3
"""Read-only RMG MZRHST1 AI/VI/host trace comparison (no ROM or emulator).

Usage:
  python tools/inventory_audio_phase_compare.py AI_TRACE VI_TRACE [--host HOST_TRACE] [--output report.json]

Read guest Count differences only within an uninterrupted capture. Host
timestamps are monotonic but are not emulated time. Exit if rings were lost.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import json
import struct
from pathlib import Path

HEADER = struct.Struct("=8sIIQQQ")
RECORD = struct.Struct("=QQ10I")
AI_WRITE, AI_LEN, AI_STATUS, AI_END, VI, HOST_DROP = (0x10, 0x12, 0x13, 0x14, 0x20, 0x51)


def signed_count_delta(a: int, b: int) -> int:
    """Signed modulo-32-bit Count delta. Only use for nearby events."""
    return ((a - b + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def read(path: Path) -> list[tuple]:
    blob = path.read_bytes()
    if len(blob) < HEADER.size:
        raise ValueError(f"{path}: header truncated")
    magic, version, size, saved, total, overwritten = HEADER.unpack_from(blob)
    if (magic, version, size) != (b"MZRHST1\x00", 1, RECORD.size):
        raise ValueError(f"{path}: unexpected trace format")
    if total < saved or overwritten != total - saved or saved > 262144:
        raise ValueError(f"{path}: invalid ring counters")
    if len(blob) != HEADER.size + saved * RECORD.size:
        raise ValueError(f"{path}: truncated/trailing event payload")
    if overwritten:
        raise ValueError(f"{path}: {overwritten} earlier events overwritten")
    rows = [RECORD.unpack_from(blob, HEADER.size + i * RECORD.size)
            for i in range(saved)]
    if any(r[0] != i for i, r in enumerate(rows)):
        raise ValueError(f"{path}: sequence discontinuity")
    if any(a[1] > b[1] for a, b in zip(rows, rows[1:])):
        raise ValueError(f"{path}: timestamp regression")
    return rows


def analyze(ai: list[tuple], vi: list[tuple], host: list[tuple]) -> dict:
    callbacks = [r for r in vi if r[2] == VI]
    if not callbacks or not ai:
        raise ValueError("empty AI or VI trace")
    first_vi_ns = vi[0][1]
    vi_ns = [r[1] for r in callbacks]
    failures = []
    for i, r in enumerate(ai):
        if r[2] != AI_STATUS or not r[4] & 0x80000000:
            continue
        if i and ai[i-1][2] == AI_STATUS and ai[i-1][4] & 0x80000000:
            continue
        if i + 2 >= len(ai) or ai[i+1][2] != AI_STATUS or not ai[i+1][4] & 0x80000000 or ai[i+2][2] != AI_LEN:
            raise ValueError("native paired FULL read/feedback sequence absent")
        next_status = next((j for j in range(i + 2, len(ai)) if ai[j][2] == AI_STATUS), None)
        next_write = next((j for j in range(i + 2, len(ai)) if ai[j][2] == AI_WRITE), None)
        if next_status is None or next_write is None:
            raise ValueError("trace ends during a native rejection")
        ends = [e for e in ai[i+1:next_write+50] if e[2] == AI_END]
        feedback = next((e for e in ai[next_write+1:] if e[2] == AI_LEN), None)
        if len(ends) < 2 or feedback is None:
            raise ValueError("missing downstream AI DMA deadline or feedback")
        v = bisect.bisect_right(vi_ns, r[1]) - 1
        if v < 0:
            raise ValueError("failure predates first VI callback")
        status = ai[next_status]
        write = ai[next_write]
        failures.append({
            "time_s_from_first_vi": round((r[1] - first_vi_ns)/1e9, 6),
            "fifo_head_bytes": r[5],
            "fifo_tail_bytes": r[6],
            "feedback_ai_len_on_failure": ai[i+2][4],
            "failure_count_after_vi": signed_count_delta(r[3], callbacks[v][3]),
            "head_end_count_after_failure": signed_count_delta(ends[0][3], r[3]),
            "tail_end_count_minus_next_service": signed_count_delta(ends[1][3], status[3]),
            "next_service_ai_status": f"0x{status[4]:08X}",
            "next_accepted_samples": write[5] // 4,
            "next_feedback_ai_len": feedback[4],
        })
    clusters = []
    for f in failures:
        if not clusters or f["time_s_from_first_vi"] - clusters[-1][-1]["time_s_from_first_vi"] > 0.4:
            clusters.append([f])
        else:
            clusters[-1].append(f)
    accepted = [r for r in ai if r[2] == AI_WRITE]
    duration_ratios = collections.Counter(
        r[9] // r[5] for r in accepted if r[5] and r[9] % r[5] == 0)
    hosts = [r for r in host if r[2] == HOST_DROP]
    return {
        "vi_callbacks": len(callbacks),
        "vi_period_count_distribution": dict(collections.Counter(r[4] for r in callbacks)),
        "accepted_ai_writes": len(accepted),
        "ai_duration_count_per_byte_distribution": dict(duration_ratios),
        "fifo_rejections": len(failures),
        "rejection_groups": [{
            "count": len(g),
            "first_s": g[0]["time_s_from_first_vi"],
            "last_s": g[-1]["time_s_from_first_vi"],
        } for g in clusters],
        "host_drops": len(hosts),
        "host_discarded_bytes": sum(r[4] for r in hosts),
        "first_failures": failures[:5],
        "last_failures": failures[-3:] if len(failures) > 5 else [],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ai", type=Path)
    ap.add_argument("vi", type=Path)
    ap.add_argument("--host", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    report = analyze(read(args.ai), read(args.vi),
                     read(args.host) if args.host else [])
    data = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
