"""Read-only decoder for the opt-in MZRPH4 RMG native audio phase observer.

Usage:
  python3 analyze_phase_trace.py mkmszr-phase-trace.bin --output phase-summary.json
  python3 analyze_phase_trace.py mkmszr-phase-trace.bin --csv phase-rows.csv

The dump is an emulated host-side observation, not a native ROM/game patch.
Guest state is interpreted only where owners have verified the address/type.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from pathlib import Path

HEADER = struct.Struct("=8sIIQQQ")
RECORD = struct.Struct("=QQII34I")
NAMES = (
    "observed_ai_read_or_write", "emulated_ai_status", "emulated_dac_divisor",
    "emulated_ai_control", "emulated_bit_rate", "vi_clock", "vi_delay",
    "expected_refresh_rate", "audio_frame", "manager_ready", "vi_work_enabled",
    "native_min_frames", "native_target_frames", "native_capacity_frames",
    "native_reserve_frames", "last_audio_info_ptr", "previous_audio_info_frames",
    "output_info_index", "audio_info_ptr0", "audio_info_ptr1", "audio_info_ptr2",
    "command_list_index", "command_list_ptr0", "command_list_ptr1",
    "task_fresh", "task_queued", "task_active", "synth_ptr",
    "synth_sample_clock", "native_stage_raw", "selector_compact_raw",
    "inventory_box_state_raw", "tv_type_raw", "native_crystal_hz",
)
EVENTS = {1: "ai_len_read", 2: "dacrate_write",
          3: "control_write", 4: "bitrate_write"}
TRANSITIONS = (
    "emulated_dac_divisor", "emulated_ai_control", "emulated_bit_rate",
    "manager_ready", "vi_work_enabled", "native_min_frames",
    "native_target_frames", "native_capacity_frames", "native_reserve_frames",
    "audio_info_ptr0", "audio_info_ptr1", "audio_info_ptr2",
    "command_list_ptr0", "command_list_ptr1", "synth_ptr",
    "native_stage_raw", "selector_compact_raw", "tv_type_raw", "native_crystal_hz",
)


def read(path: Path) -> tuple[list[dict], dict]:
    blob = path.read_bytes()
    if len(blob) < HEADER.size:
        raise ValueError("Missing/truncated phase header")
    magic, version, rec_size, saved, total, overwritten = HEADER.unpack_from(blob)
    if ((magic, version, rec_size) != (b"MZRPH4\0\0", 4, RECORD.size)
            or overwritten != 0 or saved != total or
            len(blob) != HEADER.size + saved * RECORD.size):
        raise ValueError("Unsupported, truncated or overwritten phase capture")
    parsed = []
    previous_ns = 0
    for index in range(saved):
        seq, ns, event, count, *values = RECORD.unpack_from(
            blob, HEADER.size + index * RECORD.size
        )
        if seq != index or (index and ns < previous_ns) or event not in EVENTS:
            raise ValueError(f"Invalid sequence/time/event at record {index}")
        row = dict(zip(NAMES, values, strict=True))
        row.update({"sequence": seq, "monotonic_ns": ns,
                    "event": EVENTS[event], "guest_cp0_count": count})
        parsed.append(row)
        previous_ns = ns
    return parsed, {
        "sha256": hashlib.sha256(blob).hexdigest(),
        "filename": path.name, "record_size": RECORD.size,
        "saved": saved, "total": total, "overwritten": overwritten,
    }


def summarize(rows: list[dict], meta: dict) -> dict:
    start = rows[0]["monotonic_ns"] if rows else 0
    transitions = []
    previous = None
    for row in rows:
        if previous is not None:
            differences = {k: {"before": previous[k], "after": row[k]}
                           for k in TRANSITIONS if previous[k] != row[k]}
            if differences:
                transitions.append({
                    "event": row["event"], "record": row["sequence"],
                    "t_seconds_since_first": round(
                        (row["monotonic_ns"] - start) / 1e9, 6
                    ), "changes": differences,
                })
        previous = row
    return {
        "format": "MKMSZR_phase_provenance_v04",
        "source": meta, "recorded_events": {
            label: sum(r["event"] == label for r in rows) for label in EVENTS.values()
        },
        "first_12_records": rows[:12],
        "last_6_records": rows[-6:],
        "state_transitions_total": len(transitions),
        "first_100_state_transitions": transitions[:100],
        "limitations": [
            "AI_LEN values and producer states were recorded, not regenerated",
            "Do not compare host monotonic times across independent emulator processes",
            "Inventory box state and selector selection are raw words, not reliable opened/mode flags",
            "Previous AudioInfo frames are previous buffer's signed +4 halfword",
            "VI/audio state sampled at AI_LEN read, never inside native synthesis",
            "Probe records are dumped at normal process exit; abnormal app exit can lose data",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    rows, meta = read(args.capture)
    report = summarize(rows, meta)
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(output)
    else:
        print(output)
    if args.csv:
        with args.csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=(
                "sequence", "monotonic_ns", "event", "guest_cp0_count", *NAMES
            ))
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()
