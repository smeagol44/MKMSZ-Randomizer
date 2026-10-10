"""Read-only pinned RMG v0.9.0 audio FIFO/PCM audit; requires local trace files.

Run: python tools/audit_audio_fifo_phase.py --root /path/to/traces --out audit.json
No ROM, emulator or network access. Does not establish N64 hardware equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER = struct.Struct("=8sIIQQQ")
RECORD = struct.Struct("=QQ10I")
BUSY = 0x40000000
FULL = 0x80000000


def cp0_delta(a: int, b: int) -> int:
    """Signed CP0 Count difference, including 32-bit wraparound."""
    value = (a - b) & 0xFFFFFFFF
    return value - (1 << 32) if value & 0x80000000 else value


def native_pcm_frames(previous_ai_len: int) -> int:
    """Established MKMSZ USA Rev0 feedback formula (frames per VI)."""
    n = ((368 - (previous_ai_len >> 2) + 320) & ~15) + 16
    return max(352, min(704, n))


def read_trace(path: Path) -> tuple[list[tuple[int, ...]], dict]:
    raw = path.read_bytes()
    magic, version, size, saved, total, overwritten = HEADER.unpack_from(raw)
    if (
        magic != b"MZRHST1\0" or version != 1 or size != RECORD.size
        or total != saved or overwritten or len(raw) != HEADER.size + saved * size
    ):
        raise ValueError(f"Incomplete, overwritten, or unsupported capture: {path}")
    rows = [RECORD.unpack_from(raw, HEADER.size + i * RECORD.size) for i in range(saved)]
    if any(row[0] != i for i, row in enumerate(rows)):
        raise ValueError(f"Broken trace sequence: {path}")
    return rows, {"filename": path.name, "sha256": hashlib.sha256(raw).hexdigest(),
                  "records": saved, "overwritten": overwritten}


def analyze(ai: list[tuple[int, ...]], vi: list[tuple[int, ...]]) -> dict:
    epoch = next(r[1] for r in vi if r[2] == 0x20)
    active = False
    deadline = None
    head_len = head_duration = 0
    previous_feedback = None
    checked_len = checked_pcm = 0
    first_status = None
    statuses = []
    writes = []
    services = []
    rejections = []
    interleavings = []
    for index, row in enumerate(ai):
        kind, ns, count = row[2], row[1], row[3]
        if kind == 0x11 and (row[4] & 0xC0000000) == BUSY:
            active = True
            head_len, head_duration = row[5], row[7]
            deadline = (count + head_duration) & 0xFFFFFFFF
        elif kind == 0x15:
            if (row[4] & 0xC0000000) == BUSY:
                active = True
                head_len, head_duration = row[5], row[8]
                deadline = (count + head_duration) & 0xFFFFFFFF
            else:
                active, deadline = False, None
        elif kind == 0x13:
            statuses.append((index, row))
            if first_status is None:
                first_status = row
        elif kind == 0x10:
            writes.append(row)
            if previous_feedback is None or row[5] != 4 * native_pcm_frames(previous_feedback):
                raise ValueError(f"Unexpected native generated PCM size at record {index}")
            if row[9] != row[5] * 551:
                raise ValueError(f"Non-pinned emulated Count/byte at record {index}")
            checked_pcm += 1
        elif kind == 0x12:
            remaining = max(0, cp0_delta(deadline, count)) if active and deadline is not None else 0
            predicted = (remaining * head_len // head_duration) & ~7 if active and head_duration else 0
            if row[4] != predicted:
                raise ValueError(f"AI_LEN mismatch at record {index}: {row[4]} != {predicted}")
            checked_len += 1
            if statuses:
                first_idx, first = statuses[0]
                failed = not writes
                if failed:
                    if not (first[4] & FULL) or (
                        previous_feedback is None or native_pcm_frames(previous_feedback) != 352
                    ):
                        raise ValueError(f"Unexplained native rejection at record {first_idx}")
                    rejections.append({"t": (first[1] - epoch) / 1e9, "head": first[5],
                                       "tail": first[6], "count": first[3],
                                       "row_index": first_idx})
                if len(statuses) > 1 and (first[4] & FULL):
                    for later_idx, later in statuses[1:]:
                        if not (later[4] & FULL):
                            ends = [v for v in ai[first_idx + 1:later_idx] if v[2] == 0x14]
                            if ends:
                                dma_end = ends[-1]
                                interleavings.append({
                                    "t": (first[1] - epoch) / 1e9,
                                    "first_status_count": first[3],
                                    "dma_end_count": dma_end[3],
                                    "later_status_count": later[3],
                                    "dma_end_after_first_count": cp0_delta(dma_end[3], first[3]),
                                    "later_read_after_dma_end": cp0_delta(later[3], dma_end[3]),
                                    "subsequent_ai_len": row[4],
                                    "note": "Later status may be diagnostic rejection logger, not game decision",
                                })
                services.append({"t": (first[1] - epoch) / 1e9, "count": first[3],
                                 "row_index": first_idx, "failed": failed,
                                 "size": writes[0][5] // 4 if writes else None})
            statuses, writes, first_status = [], [], None
            previous_feedback = row[4]
    groups = []
    current = []
    for item in rejections:
        if current and item["t"] - current[-1]["t"] > 0.085:
            groups.append(current)
            current = []
        current.append(item)
    if current:
        groups.append(current)
    episodes = []
    for group in groups:
        first = group[0]
        next_service = next((s for s in services if s["row_index"] > first["row_index"]), None)
        ai_end_idx = next((i for i in range(first["row_index"] + 1, len(ai))
                           if ai[i][2] == 0x14), None)
        delta = None
        if next_service is not None and ai_end_idx is not None:
            end = ai[ai_end_idx]
            post = ai[ai_end_idx + 1]
            if post[2] != 0x15:
                raise ValueError("AI end/post-event ordering changed")
            if (post[4] & 0xC0000000) == BUSY:
                tail_end_count = (end[3] + post[8]) & 0xFFFFFFFF
                delta = cp0_delta(next_service["count"], tail_end_count)
        episodes.append({"rejections": len(group),
                         "start_sec": round(first["t"], 6),
                         "end_sec": round(group[-1]["t"], 6),
                         "first_head_bytes": first["head"], "first_tail_bytes": first["tail"],
                         "next_service_minus_tail_dma_end_count": delta})
    longest = current_run = 0
    for service in services:
        if not service["failed"] and service["size"] == 368:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 0
    return {"exact_ai_len_reads": checked_len, "exact_accepted_pcm_sizes": checked_pcm,
            "native_rejected_submissions": len(rejections),
            "longest_368_frame_only_streak": longest,
            "episodes": episodes, "status_dma_end_interleavings": interleavings}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    runs = {"7": "7", "8": "8", "9": "9", "10": "10", "11": "20261009-234627"}
    report = {"schema": "MKMSZR_fifo_phase_readonly_v01", "runs": {}, "totals": {},
              "limitations": [
                  "Assumes exact RMG v0.9.0 observer event encoding and 551 Count/byte",
                  "Infers rejected (unsubmitted) generated sizes from native size recurrence",
                  "Observed DMA deadlines are exogenous; not proof of N64 hardware scheduling",
                  "Diagnostic logger extra instructions can affect phase and recovery",
                  "No unmonitored guest memory or early input/callback invariants are evaluated",
              ]}
    for label, suffix in runs.items():
        ai, ai_meta = read_trace(args.root / f"mkmszr-ai-trace({suffix}).bin")
        vi, vi_meta = read_trace(args.root / f"mkmszr-vi-trace({suffix}).bin")
        report["runs"][label] = {"source": {"ai": ai_meta, "vi": vi_meta}, **analyze(ai, vi)}
    for field in ("exact_ai_len_reads", "exact_accepted_pcm_sizes", "native_rejected_submissions"):
        report["totals"][field] = sum(run[field] for run in report["runs"].values())
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["totals"], indent=2))


if __name__ == "__main__":
    main()
