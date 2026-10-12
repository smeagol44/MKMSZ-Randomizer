"""ROM-free offline audit for RMG v04 audio DMA deadline bifurcations.

Usage: python tools/audit_audio_dma_deadlines.py --root /path/with/three-zips --out audit.json
Expected input names: mkmszr-cleanaudio.zip, mkmszr-slowdown.zip,
mkmszr-speedup.zip, each with mkmszr-{ai,vi}-trace.bin.
No emulator, ROM, network or device memory writes.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import itertools
import json
import statistics
import struct
import zipfile
from pathlib import Path

HEADER = struct.Struct("=8sIIQQQ")
RECORD = struct.Struct("=QQ10I")
COUNT_PER_BYTE = 551
VI_COUNT = 811092


def count_delta(a: int, b: int) -> int:
    return ((a - b + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def deadline_margin(next_count: int, dma_end_count: int, queued_bytes: int) -> int:
    return count_delta(next_count, dma_end_count + queued_bytes * COUNT_PER_BYTE)


def read_records(archive: zipfile.ZipFile, member: str) -> tuple[list[tuple], dict]:
    blob = archive.read(member)
    magic, version, size, saved, total, overwritten = HEADER.unpack_from(blob)
    if (magic, version, size) != (b"MZRHST1\x00", 1, RECORD.size):
        raise ValueError(f"Unexpected observer format: {member}")
    if saved != total or overwritten or len(blob) != HEADER.size + saved * size:
        raise ValueError(f"Truncated or overwritten observer trace: {member}")
    rows = [RECORD.unpack_from(blob, HEADER.size + i * size)
            for i in range(saved)]
    if any(r[0] != i for i, r in enumerate(rows)):
        raise ValueError(f"Broken observer sequence: {member}")
    return rows, {"sha256": hashlib.sha256(blob).hexdigest(), "records": saved}


def extract_services(ai: list[tuple], vi: list[tuple]) -> tuple[list[dict], int]:
    vi_events = [r for r in vi if r[2] == 0x20]
    vi_ns = [r[1] for r in vi_events]
    if not vi_ns:
        raise ValueError("No emulated VI events")
    first = vi_ns[0]
    services = []
    status = None
    write = None
    for index, r in enumerate(ai):
        if r[2] == 0x13 and status is None:
            status = (index, r)
        elif r[2] == 0x10:
            write = r
        elif r[2] == 0x12:
            if status is not None:
                start_index, start = status
                vi_index = bisect.bisect_right(vi_ns, start[1]) - 1
                if vi_index < 0:
                    raise ValueError("AI service before first VI")
                services.append({
                    "seconds": (start[1] - first) / 1e9,
                    "first_status_index": start_index,
                    "count": start[3],
                    "status": start[4],
                    "head_bytes": start[5],
                    "tail_bytes": start[6],
                    "ai_len_bytes": r[4],
                    "written_bytes": write[5] if write is not None else None,
                    "vi_index": vi_index,
                    "vi_status_offset_count": count_delta(
                        start[3], vi_events[vi_index][3]
                    ),
                })
            status = None
            write = None
    return services, first


def longest_size_run(services: list[dict], size: int) -> dict:
    candidates = []
    for value, pairs in itertools.groupby(
        enumerate(services), key=lambda item: item[1]["written_bytes"]
    ):
        group = list(pairs)
        if value == size:
            candidates.append((len(group), group[0][0], group[-1][0]))
    if not candidates:
        return {}
    n, a, b = max(candidates)
    subset = services[a:b + 1]
    deltas = [count_delta(y["count"], x["count"])
              for x, y in itertools.pairwise(subset)]
    return {
        "buffers": n,
        "t_first": subset[0]["seconds"],
        "t_last": subset[-1]["seconds"],
        "first_ai_len": subset[0]["ai_len_bytes"],
        "last_ai_len": subset[-1]["ai_len_bytes"],
        "first_status": subset[0]["status"],
        "last_status": subset[-1]["status"],
        "mean_service_count_interval": statistics.mean(deltas) if deltas else None,
    }


def find_fork(ai: list[tuple], services: list[dict], center_seconds: float) -> dict:
    selected = min(
        range(len(services)), key=lambda i: abs(services[i]["seconds"] - center_seconds)
    )
    failing = services[selected]
    if failing["status"] & 0x80000000 == 0 or selected + 1 >= len(services):
        raise ValueError(f"No full FIFO service at {center_seconds}")
    start = failing["first_status_index"]
    stop = services[selected + 1]["first_status_index"]
    ends = [r for r in ai[start + 1:stop] if r[2] == 0x14]
    if not ends:
        raise ValueError(f"No subsequent AI END after {center_seconds}")
    end = ends[0]
    next_service = services[selected + 1]
    queued_size = failing["tail_bytes"]
    return {
        "first_full_at_seconds": failing["seconds"],
        "first_full_guest_count": failing["count"],
        "queued_tail_bytes": queued_size,
        "first_ai_end_guest_count": end[3],
        "ai_end_count_after_first_status": count_delta(end[3], failing["count"]),
        "next_service_guest_count": next_service["count"],
        "next_service_minus_queued_dma_end_count": deadline_margin(
            next_service["count"], end[3], queued_size
        ),
        "counterfactual_tail_64_bytes_shorter_margin_count": deadline_margin(
            next_service["count"], end[3], queued_size - 64
        ),
        "next_service_status": next_service["status"],
        "next_service_written_bytes": next_service["written_bytes"],
        "next_service_ai_len_bytes": next_service["ai_len_bytes"],
    }


def audit_one(root: Path, label: str) -> dict:
    archive_path = root / f"mkmszr-{label}.zip"
    with zipfile.ZipFile(archive_path) as archive:
        ai, ai_meta = read_records(archive, "mkmszr-ai-trace.bin")
        vi, vi_meta = read_records(archive, "mkmszr-vi-trace.bin")
    services, start_ns = extract_services(ai, vi)
    result = {
        "inputs": {"zip": archive_path.name, "ai": ai_meta, "vi": vi_meta},
        "epoch_ns": start_ns,
        "services": len(services),
        "longest_368_buffer_run": longest_size_run(services, 1472),
        "longest_352_buffer_run": longest_size_run(services, 1408),
    }
    if label == "slowdown":
        result["fork"] = find_fork(ai, services, 191.417525)
    if label == "speedup":
        result["fork"] = find_fork(ai, services, 267.046551)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "model": {"cp0_count_per_pcm_byte": COUNT_PER_BYTE,
                  "vi_guest_count": VI_COUNT,
                  "duration_count": {
                      str(size): size * COUNT_PER_BYTE for size in
                      (1408, 1472, 1536, 1600)
                  }},
        "controls": {
            name: audit_one(args.root, name)
            for name in ("cleanaudio", "slowdown", "speedup")
        },
        "limits": [
            "Guest Count in RMG is observed, not independently predicted",
            "User's controller movements and exact Inventory-open time are not captured",
            "Selected fork timestamps refer to v04 session-specific observations",
            "Do not infer precise audible pitch or N64 hardware correctness",
        ],
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
