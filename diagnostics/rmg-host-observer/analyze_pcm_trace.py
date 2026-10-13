"""Classify committed ParaLLEl DMA writes to an unstarted AI-tail buffer.

No ROM execution. Old captures without the write protocol are inconclusive.
"""

import argparse
import hashlib
import json
from pathlib import Path

from decode_host_trace import read
from pcm_ownership import assess_promoted_initialization, replay


def analyze(trace, onset=None, session=None, host_trace=None, vi_trace=None):
    rows = trace["rows"]
    problems = []
    if trace["overwritten"]:
        problems.append("early records overwritten: lead-up unavailable")
    starts = [r for r in rows if r[2] == 0x80]
    ends = [r for r in rows if r[2] == 0x89]
    if len(starts) != 1 or starts[0][4][:2] != [2, 4096]:
        problems.append("PCM protocol start missing/repeated/incompatible; old capture lacks writes")
    if len(ends) != 1:
        problems.append("normal-exit PCM coverage summary missing/repeated")
    elif ends[0][4][0] != ends[0][4][1] or any(ends[0][4][5:]):
        problems.append("unmatched write hooks, invalid ranges or reentrant/pending write")
    identities = [r for r in rows if r[2] == 0x86]
    loaded_md5 = None
    if len(identities) == 1:
        loaded_md5 = "".join(f"{v:08x}" for v in identities[0][4][:4])
        if identities[0][4][4] != 0x800000:
            problems.append("unsupported RDRAM size")
    else:
        problems.append("loaded-ROM identity missing/repeated")
    if not session:
        problems.append("capture session ROM identity missing")
    elif loaded_md5 != session.get("rom_md5", "").lower():
        problems.append("loaded-ROM MD5 differs from supplied session ROM")
    if session and rows and rows[0][1] < session.get("prepared_monotonic_ns", 0):
        problems.append("trace predates session preparation; stale capture")
    if not any(r[2] == 0x85 and r[4][1] == 2 for r in rows):
        problems.append("no observed audio task type 2: wrong plugin/path or incomplete capture")
    if onset and (not rows or not rows[0][1] <= onset["monotonic_ns"] <= rows[-1][1]):
        problems.append("audible-onset marker outside the captured run")
    audio_rows = sum(r[2] == 0x83 and r[4][2] == 2 for r in rows)
    if len(ends) == 1 and ends[0][4][2] != audio_rows:
        problems.append("audio write-row coverage differs from exit summary")
    first_full = next((r for r in rows if r[2] == 0x13 and r[4][0] & 0x80000000), None)
    first_vi = next((r for r in (vi_trace or trace)["rows"] if r[2] == 0x20), None)
    epoch = first_vi[1] if first_vi else rows[0][1] if rows else 0
    ownership = replay(rows)
    tail_id = 0
    task = None
    completed = set()
    task_types = {}
    ready_tail = 0
    writes = []
    unsealed = []
    initial_fills = []
    recycled = set()
    promoted_incomplete = set()
    same_value = 0
    safe_audio = 0
    for i, row in enumerate(rows):
        _, ns, event, count, values = row
        if event in (0x81, 0x82):
            tail_id = values[3] if values[6] & 0x80000000 else 0
            ready_tail = 0
        if event == 0x85:
            task = values[0]
            task_types[task] = values[1]
        if event == 0x87 and values[2] & 0x203 == 0x203:
            completed.add(values[0])
        if event == 0x8a:
            if values[0] != tail_id:
                problems.append("ready-generation record has mismatched AI-tail identity")
            ready_tail = values[1]
        if event != 0x83:
            continue
        dest, size, task_type, pc, owner, overlap, changed, flags = values
        if flags & 16:
            problems.append(f"invalid write/ownership snapshot at sequence {row[0]}")
        if not overlap:
            safe_audio += task_type == 2
            continue
        if i+2 >= len(rows) or rows[i+1][2] != 0x84 or rows[i+2][2] != 0x8b:
            problems.append(f"missing byte-proof detail at sequence {row[0]}")
            continue
        detail = rows[i+1][4]
        provenance = rows[i+2][4]
        if provenance[:3] != [ready_tail, task, owner]:
            problems.append(f"mismatched write generation provenance at sequence {row[0]}")
        if owner != tail_id or not owner or detail[7] != task:
            problems.append(f"missing/mismatched tail or task generation at sequence {row[0]}")
        if changed > overlap or overlap > size or not flags & 8:
            problems.append(f"unverified changed-byte evidence at sequence {row[0]}")
        if not changed:
            same_value += 1
            continue
        if flags & 16 or not flags & 8 or not flags & 2 or owner != tail_id or not owner:
            continue
        proven_owner = ownership["qualified_sequences"].get(row[0])
        if proven_owner is None:
            fill = {"sequence": row[0], "count": count, "task_generation": task,
                    "tail_generation": owner, "completed_tail_writer": ready_tail,
                    "changed_unread_bytes": changed}
            packet = ownership["packets"].get(owner, {})
            if ((packet.get("writer_at_promotion") == task and packet.get("completed_at_promotion")
                 or packet.get("owner_generation") == task)
                    and not packet.get("has_qualified_replacement")):
                fill["note"] = "New lease's complete synthesis finished before promotion; stale bytes from a released lease are not live ownership"
                prior = packet.get("prior_released_lease")
                if prior and prior["sequence"] < packet["accept_sequence"]:
                    recycled.add(owner)
                    fill["prior_released_lease"] = prior
                initial_fills.append(fill)
            else:
                fill["note"] = "Live older-packet ownership is unproved; promotion/task completion alone does not establish consumption of unwritten bytes"
                if packet.get("promotion_sequence") is not None and not packet.get("completed_at_promotion"):
                    promoted_incomplete.add(owner)
                unsealed.append(fill)
            continue
        relation = "audible onset not marked"
        delta = None
        if onset and onset.get("kind") == "audible_onset":
            delta = (ns-onset["monotonic_ns"])/1e9
            uncertainty = onset["uncertainty_seconds"]
            relation = ("before reported audible-onset window" if delta < -uncertainty else
                        "after reported audible-onset window" if delta > uncertainty else
                        "within audible-onset uncertainty window")
        elif onset:
            delta = (ns-onset["monotonic_ns"])/1e9
            relation = "host observation marker only; acoustic/emulated onset unknown"
        writes.append({
            "sequence": row[0], "count": count, "seconds_from_first_vi": (ns-epoch)/1e9,
            "task_generation": task, "latched_task_type": task_type,
            "rsp_pc_context": hex(pc), "write_start_physical": hex(dest), "row_bytes": size,
            "tail_generation": owner, "tail_start_physical": hex(detail[1]),
            "older_completed_generation": proven_owner,
            "raw_stale_ready_generation": ready_tail,
            "tail_length": detail[2], "overlap_bytes": overlap, "changed_unread_bytes": changed,
            "first_changed_physical": hex(detail[0]),
            "relative_to_first_full_status": (
                "before" if row[0] < first_full[0] else "after"
            ) if first_full else "no FULL-status marker",
            "relative_to_reported_audio_onset": relation, "onset_delta_seconds": delta,
        })
    audible = bool(onset and onset.get("kind") == "audible_onset")
    reads = assess_promoted_initialization(
        ownership, promoted_incomplete, host_trace["rows"] if host_trace else None)
    if host_trace and host_trace["overwritten"]:
        reads["host_pairs_verified"] = False
        reads["host_pair_problems"].append("host ring lead-up overwritten")
    if problems:
        verdict = "INCONCLUSIVE: missing/incomplete evidence; stop"
    elif writes:
        verdict = "DIFFERENT GENERATION MUTATED COMPLETED UNREAD AI-TAIL PCM"
    elif unsealed:
        if (reads["host_pairs_verified"] and reads["all_particular_words_complete"]
                and reads["fully_read_buffers"] == len(promoted_incomplete)):
            verdict = "NO QUALIFIED LIVE-LEASE REPLACEMENT; ASSESSED BACKEND READS CONSUMED COMPLETE BYTE GENERATIONS"
        else:
            verdict = "NO QUALIFIED LIVE-LEASE REPLACEMENT; PROMOTED INITIALIZATION REQUIRES BYTE-CONSUMPTION ASSESSMENT"
    elif audible:
        verdict = "REPORTED FAILURE WITHOUT OBSERVED OLDER-COMPLETED-GENERATION REPLACEMENT"
    else:
        verdict = "INCONCLUSIVE: no reported acceleration; stop"
    return {
        "verdict": verdict, "missing_evidence": sorted(set(problems)),
        "loaded_rom_md5": loaded_md5, "session": session, "reported_marker": onset,
        "audible_onset": onset if audible else None,
        "rom_identity": {
            "trace_recorded_loaded_md5": loaded_md5,
            "session_declared_md5": session.get("rom_md5") if session else None,
            "session_declared_sha256": session.get("rom_sha256") if session else None,
            "recorded_md5_matches_session": bool(session and loaded_md5 == session.get("rom_md5", "").lower()),
            "rom_bytes_independently_rehashed_by_analyzer": False,
            "note": "0x86 independently records the loaded core's ROM_SETTINGS MD5; filename/SHA-256 are declared in session, not recorded by this trace",
        },
        "time_epoch": "first VI callback" if first_vi else "first AI record (no VI ring supplied)",
        "first_full_status_seconds_from_epoch": (first_full[1]-epoch)/1e9 if first_full else None,
        "first_full_status_seconds_from_vi": (first_full[1]-epoch)/1e9 if first_full and first_vi else None,
        "first_full_note": "FULL-status observation is a rejection proxy, not an acoustic onset",
        "safe_audio_write_rows": safe_audio, "identical_value_overlap_rows": same_value,
        "committed_tail_mutations": writes, "coverage_summary": ends[0][4] if len(ends) == 1 else None,
        "unqualified_queued_mutations": unsealed,
        "completed_before_playback_initialization": initial_fills,
        "released_storage_initialization_instances": len(recycled),
        "promoted_incomplete_instances": sorted(promoted_incomplete),
        "active_head_source_reads": reads,
        "limitations": [
            "Observes ParaLLEl RSP DMA stores only; CPU/PI/RDP/wild writers are unmeasured.",
            "A queued device tail has not started playback; late AI event delivery can still affect console portability.",
            "Only mutation after binding a live lease's completed synthesis proves older-packet replacement; a seal at new acceptance is stale-byte provenance, not semantic ownership.",
            "Pinned-core AI_LEN/end events identify synchronous backend source reads; they do not record a physical N64 DAC byte cursor or final audible output.",
            "Task type is latched from DMEM OSTask at first-run; RSP PC is context, not an exact JIT-store PC.",
            "Queueing before own synthesis completes can be legal; only writes over an older completed generation qualify.",
            "Human onset marker has a reported uncertainty; precedence alone is not causation.",
            "Opt-in observer can perturb phase; no non-reproduction certifies health.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ai", type=Path)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--onset", type=Path)
    parser.add_argument("--marker-only", action="store_true",
                        help="retain Enter as host observation; do not infer acoustic onset window")
    parser.add_argument("--host", type=Path, help="host audio ring to verify synchronous source reads")
    parser.add_argument("--vi", type=Path, help="VI ring providing the actual first-VI time epoch")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    onset = json.loads(args.onset.read_text()) if args.onset else None
    if onset and args.marker_only:
        onset = {**onset, "original_kind": onset.get("kind"), "kind": "host_observation"}
    if onset and (onset.get("kind") not in ("audible_onset", "host_observation") or
                  onset.get("uncertainty_seconds", -1) < 0):
        raise ValueError("invalid audible-onset marker")
    try:
        trace = read(args.ai)
        result = analyze(trace, onset, json.loads(args.session.read_text()),
                         read(args.host) if args.host else None,
                         read(args.vi) if args.vi else None)
    except (ValueError, OSError) as error:
        result = {"verdict": "INCONCLUSIVE: invalid capture; stop",
                  "missing_evidence": [str(error)], "committed_tail_mutations": []}
    result["trace_sha256"] = hashlib.sha256(args.ai.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(result["verdict"])
    print("Changed unread-tail rows:", len(result["committed_tail_mutations"]))
    for problem in result["missing_evidence"]:
        print("Missing:", problem)


if __name__ == "__main__":
    main()
