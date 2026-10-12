"""Prepare ROM identity and optionally mark audible onset. Never launches RMG."""

import argparse
import hashlib
import json
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--mark-onset", action="store_true")
    parser.add_argument("--uncertainty-seconds", type=float, default=3.0)
    args = parser.parse_args()
    if args.uncertainty_seconds < 0:
        raise ValueError("uncertainty cannot be negative")
    blob = args.rom.read_bytes()
    sha = hashlib.sha256(blob).hexdigest()
    if sha != args.expected_sha256.lower():
        raise ValueError("ROM SHA256 mismatch; stop, do not substitute a different composition")
    if blob[:4] != bytes.fromhex("80371240"):
        raise ValueError("use the exact big-endian z64 ROM; no byte-swapping here")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    session = {"rom_name": args.rom.name, "rom_sha256": sha,
               "rom_md5": hashlib.md5(blob).hexdigest(),
               "prepared_monotonic_ns": time.monotonic_ns(),
               "diagnostic": "pcm-unread-write-v01", "rich_rendering": "retained by exact ROM identity"}
    (args.output_dir/"session.json").write_text(json.dumps(session, indent=2)+"\n")
    print("Identity saved. No emulator launched. Capture directory:", args.output_dir)
    if args.mark_onset:
        input("Start RMG manually in another terminal. Press Enter immediately when acceleration is heard: ")
        marker = {"kind": "audible_onset", "monotonic_ns": time.monotonic_ns(),
                  "uncertainty_seconds": args.uncertainty_seconds,
                  "note": "Human report; uncertainty includes noticing/reaction delay, not a measured waveform"}
        (args.output_dir/"onset.json").write_text(json.dumps(marker, indent=2)+"\n")
        print("Onset marked. Quit RMG normally now; preserve the traces. Do not restart or load a state.")


if __name__ == "__main__":
    main()
