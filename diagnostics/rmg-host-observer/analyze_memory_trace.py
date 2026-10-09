"""Read-only decoder for RMG v02 opt-in RDRAM observer data (VI ring).

Usage: python3 analyze_memory_trace.py mkmszr-vi-trace.bin
       python3 analyze_memory_trace.py mkmszr-vi-trace.bin --ai mkmszr-ai-trace.bin

This is VI-SAMPLED, not a live memory write trace. It cannot establish the
absence of transient corruption or between-VI arena peaks.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
from pathlib import Path

HEADER = struct.Struct("=8sIIQQQ")
RECORD = struct.Struct("=QQ10I")
FLOOR = 0x801B3420
LIMIT = 0x80290990
MKSV = 0x4D4B5356


def read(path: Path) -> list[tuple]:
    data = path.read_bytes()
    if len(data) < HEADER.size:
        raise ValueError(f"{path}: truncated header")
    magic, version, size, saved, total, lost = HEADER.unpack_from(data)
    if (magic.rstrip(b"\0"), version, size) != (b"MZRHST1", 1, RECORD.size):
        raise ValueError(f"{path}: unexpected format")
    if lost or saved != total or len(data) != HEADER.size + saved * size:
        raise ValueError(f"{path}: lost records, truncated or inconsistent")
    rows = [RECORD.unpack_from(data, HEADER.size + i * size) for i in range(saved)]
    if any(row[0] != i or (i and row[1] < rows[i - 1][1])
           for i, row in enumerate(rows)):
        raise ValueError(f"{path}: records not sequential and monotonic")
    return rows


def analyze(vi: list[tuple], ai: list[tuple] | None = None) -> dict:
    state = [r for r in vi if r[2] == 0x40]
    hashes = [r for r in vi if r[2] == 0x41]
    if not state or len(state) != len(hashes):
        raise ValueError("missing 0x40/0x41 VI memory events; enable "
                         "MKMSZR_TRACE=1 and MKMSZR_TRACE_MEM=1")
    first_ns = vi[0][1]
    bad = []
    changed = []
    last = None
    active_cursors = []
    audio_fails = sum(1 for r in (ai or []) if
                      r[2] == 0x13 and (r[4] & 0x80000000)) // 2
    stage_counts = collections.Counter()
    for current, digest in zip(state, hashes):
        if digest[0] != current[0] + 1 or digest[3] != current[3]:
            raise ValueError("memory records are not adjacent within a VI")
        _, ns, _, _, cursor, base, hud, stage, magic, frame, peak, flags = current
        _, _, _, _, h_code, h_legend, h_tail, cached_id, box, work, index, cursor2 = digest
        t = round((ns - first_ns) / 1e9, 5)
        active = base == FLOOR and magic == MKSV
        if active:
            stage_counts[stage] += 1
            if FLOOR <= cursor <= LIMIT:
                active_cursors.append(cursor)
            else:
                bad.append({"time_s": t, "reason": "arena cursor outside bounds",
                            "cursor": f"0x{cursor:08X}", "stage": stage})
            if hud and not (FLOOR <= hud <= LIMIT - 0x1200
                            and cursor >= hud + 0x1200):
                bad.append({"time_s": t, "reason": "HUD pointer not under current cursor",
                            "cursor": f"0x{cursor:08X}",
                            "hud": f"0x{hud:08X}", "stage": stage})
        if cursor2 != cursor:
            bad.append({"time_s": t, "reason": "cursor changed between adjacent probes"})
        triple = (h_code, h_legend, h_tail)
        if (last and active and last[0] and last[1] == stage
                and last[2] != triple):
            changed.append({"time_s": t, "stage": stage,
                            "from": [f"{v:08X}" for v in last[2]],
                            "to": [f"{v:08X}" for v in triple]})
        last = (active, stage, triple)
    max_cursor = max(active_cursors) if active_cursors else None
    return {
        "method": "read-only VI-sampled guest physical words; not every write",
        "vi_memory_samples": len(state),
        "active_samples": sum(stage_counts.values()),
        "per_stage_samples": dict(stage_counts),
        "arena_sampled_max": f"0x{max_cursor:08X}" if max_cursor else None,
        "minimum_sampled_headroom": LIMIT - max_cursor if max_cursor else None,
        "memory_invariant_alerts": len(bad),
        "alert_examples": bad[:40],
        "stable_stage_code_digest_changes": len(changed),
        "digest_changes_examples": changed[:25],
        "guest_fifo_full_pairs": audio_fails,
        "interpretation": "Invariants/digest changes require stage-lifecycle review; "
                          "zero alerts do not rule out corruption between VI samples",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vi", type=Path)
    parser.add_argument("--ai", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = analyze(read(args.vi), read(args.ai) if args.ai else None)
    result = json.dumps(report, indent=2) + "\n"
    if args.json_out:
        args.json_out.write_text(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
