"""Regression against supplied October 12 capture; no ROM/emulator execution.

Pass the directory containing the original four traces and session/onset JSON.
Private capture bytes are never embedded in this repository.
"""

import argparse
import hashlib
import json
from pathlib import Path

from analyze_pcm_trace import analyze
from decode_host_trace import read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    directory = args.capture
    ai = directory / "mkmszr-ai-trace.bin"
    assert hashlib.sha256(ai.read_bytes()).hexdigest() == (
        "5fee366a87919c665441594366cf91d34f1b1a27d8fb6ef07284937062fe05a0")
    session = json.loads((directory / "session.json").read_text())
    marker = {**json.loads((directory / "onset.json").read_text()), "kind": "host_observation"}
    result = analyze(read(ai), marker, session,
                     read(directory / "mkmszr-host-audio-trace.bin"),
                     read(directory / "mkmszr-vi-trace.bin"))
    assert not result["missing_evidence"], result["missing_evidence"]
    assert not result["committed_tail_mutations"]
    assert len(result["completed_before_playback_initialization"]) == 5060
    assert result["released_storage_initialization_instances"] == 892
    assert len(result["unqualified_queued_mutations"]) == 74
    assert len(result["promoted_incomplete_instances"]) == 33
    copies = result["active_head_source_reads"]
    assert copies["host_pairs_verified"] and not copies["host_pair_problems"]
    assert copies["all_core_copy_calls"] == 5210
    assert copies["assessed_buffers"] == copies["fully_read_buffers"] == 33
    assert copies["assessed_copy_calls"] == 66 and copies["assessed_bytes"] == 92928
    assert copies["all_particular_words_complete"]
    assert all(c["whole_task_complete_before_read"] for c in copies["evidence"])
    assert result["rom_identity"]["recorded_md5_matches_session"]
    assert result["rom_identity"]["trace_recorded_loaded_md5"] == "95b4d6d53085496780c0f5ba84a5ac8d"
    assert not result["rom_identity"]["rom_bytes_independently_rehashed_by_analyzer"]
    assert result["audible_onset"] is None and result["reported_marker"]["kind"] == "host_observation"
    assert result["time_epoch"] == "first VI callback"
    print("PASS existing capture: zero live-lease replacements; 892 recycled leases; "
          "33 complete-byte buffers read in 66 verified backend copies")
    print("Minimum particular-word lead (ms):", copies["minimum_particular_word_lead_ms"])


if __name__ == "__main__":
    main()
