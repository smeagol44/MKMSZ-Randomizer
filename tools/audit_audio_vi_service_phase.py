"""Read-only VI-to-native-audio service CP0 Count timing across RMG Observer v02 captures.

Usage:
  python tools/audit_audio_vi_service_phase.py --root /path/to/traces --out phase.json

Trace inputs are never modified or uploaded; ROM, emulator and network are unused.
Do not infer guest workload timing from host monotonic timestamps.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import statistics
import struct
from pathlib import Path

HEADER = struct.Struct("=8sIIQQQ")
RECORD = struct.Struct("=QQ10I")
RUNS = {"7": "7", "8": "8", "9": "9", "10": "10", "11": "20261009-234627"}


def load(path: Path) -> tuple[list[tuple[int, ...]], dict]:
    raw = path.read_bytes()
    magic, version, size, saved, total, overwritten = HEADER.unpack_from(raw)
    if (
        (magic, version, size) != (b"MZRHST1\x00", 1, RECORD.size)
        or saved != total
        or overwritten != 0
        or len(raw) != HEADER.size + saved * RECORD.size
    ):
        raise ValueError(f"Unsupported, incomplete or overwritten trace: {path}")
    rows = [RECORD.unpack_from(raw, HEADER.size + i * RECORD.size) for i in range(saved)]
    if any(row[0] != i for i, row in enumerate(rows)):
        raise ValueError(f"Broken trace sequence: {path}")
    return rows, {
        "file": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "records": saved,
        "overwritten": overwritten,
    }


def cp0_delta(a: int, b: int) -> int:
    return ((a - b + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def analyze(root: Path, suffix: str) -> dict:
    ai, ai_meta = load(root / f"mkmszr-ai-trace({suffix}).bin")
    vi, vi_meta = load(root / f"mkmszr-vi-trace({suffix}).bin")
    events = [r for r in vi if r[2] == 0x20]
    if not events:
        raise ValueError("No VI callbacks")
    vi_ns = [r[1] for r in events]
    services = []
    saw_status = False
    for item in ai:
        if item[2] == 0x12:
            saw_status = False
        if item[2] != 0x13 or saw_status:
            continue
        saw_status = True
        vi_index = bisect.bisect_right(vi_ns, item[1]) - 1
        if vi_index < 0:
            continue
        services.append((vi_index, cp0_delta(item[3], events[vi_index][3]),
                         bool(item[4] & 0x80000000)))
    if not services:
        raise ValueError("No native audio status service")
    indices = [r[0] for r in services]
    if len(indices) != len(set(indices)):
        raise ValueError("Multiple native services per emulated VI")
    missing_active = indices[-1] - indices[0] + 1 - len(indices)
    if missing_active:
        raise ValueError(f"{missing_active} active VI intervals without native audio service")
    phases = sorted(r[1] for r in services)

    def percentile(fraction: float) -> int:
        return phases[round((len(phases) - 1) * fraction)]

    return {
        "files": {"ai": ai_meta, "vi": vi_meta},
        "vi_events": len(events),
        "native_audio_services": len(services),
        "vi_events_before_first_service": indices[0],
        "trailing_vi_events_without_complete_service": len(events) - indices[-1] - 1,
        "active_vi_service_gaps": missing_active,
        "multiple_services_per_vi": 0,
        "native_rejected_services": sum(item[2] for item in services),
        "vi_delay_count_values": collections.Counter(r[4] for r in events).most_common(3),
        "first_status_phase_count": {
            "min": phases[0],
            "p05": percentile(0.05),
            "median": statistics.median(phases),
            "mean": round(statistics.fmean(phases), 2),
            "p95": percentile(0.95),
            "max": phases[-1],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema": "MKMSZR_vi_audio_service_phase_audit_v01",
        "runs": {label: analyze(args.root, suffix) for label, suffix in RUNS.items()},
        "interpretation": "No active-VI native audio service gaps, but event scheduling and "
        "full initial audio DMA phase not reconstructed. This does not establish a fix.",
        "limitations": [
            "First AI_STATUS read is after native audio work begins, not scheduler VI-handler entry.",
            "Requires the exact observer event schema and complete recordings.",
            "Observed VI/service guest Count offset does not identify the initial audio FIFO phase.",
            "No input, Inventory state, or guest-memory ownership trace is provided.",
        ],
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print("Observed native audio services:",
          sum(v["native_audio_services"] for v in result["runs"].values()))
    print("All active VI service gaps:", sum(v["active_vi_service_gaps"]
                                               for v in result["runs"].values()))


if __name__ == "__main__":
    main()
