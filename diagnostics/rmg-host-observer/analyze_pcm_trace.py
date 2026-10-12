"""Classify committed ParaLLEl DMA writes to an unstarted AI-tail buffer.

No ROM execution. Old captures without the write protocol are inconclusive.
"""

import argparse
import hashlib
import json
from pathlib import Path

from decode_host_trace import read


def analyze(trace, onset=None, session=None):
    rows = trace["rows"]
    problems = []
    if trace["overwritten"]:
        problems.append("early records overwritten: lead-up unavailable")
    starts = [r for r in rows if r[2] == 0x80]
    ends = [r for r in rows if r[2] == 0x89]
    if len(starts) != 1 or starts[0][4][:2] != [1, 4096]:
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
    first_vi = next((r for r in rows if r[2] == 0x20), None)
    epoch = first_vi[1] if first_vi else rows[0][1] if rows else 0
    tail_id = 0
    task = None
    writes = []
    same_value = 0
    safe_audio = 0
    for i, row in enumerate(rows):
        _, ns, event, count, values = row
        if event in (0x81, 0x82):
            tail_id = values[3] if values[6] & 0x80000000 else 0
        if event == 0x85:
            task = values[0]
        if event != 0x83:
            continue
        dest, size, task_type, pc, owner, overlap, changed, flags = values
        if flags & 16:
            problems.append(f"invalid write/ownership snapshot at sequence {row[0]}")
        if not overlap:
            safe_audio += task_type == 2
            continue
        if i+1 >= len(rows) or rows[i+1][2] != 0x84:
            problems.append(f"missing byte-proof detail at sequence {row[0]}")
            continue
        detail = rows[i+1][4]
        if owner != tail_id or not owner or detail[7] != task:
            problems.append(f"missing/mismatched tail or task generation at sequence {row[0]}")
        if changed > overlap or overlap > size or not flags & 8:
            problems.append(f"unverified changed-byte evidence at sequence {row[0]}")
        if not changed:
            same_value += 1
            continue
        if flags & 16 or not flags & 8 or not flags & 2 or owner != tail_id or not owner:
            continue
        relation = "audible onset not marked"
        delta = None
        if onset:
            delta = (ns-onset["monotonic_ns"])/1e9
            uncertainty = onset["uncertainty_seconds"]
            relation = ("before reported audible-onset window" if delta < -uncertainty else
                        "after reported audible-onset window" if delta > uncertainty else
                        "within audible-onset uncertainty window")
        writes.append({
            "sequence": row[0], "count": count, "seconds_from_first_vi": (ns-epoch)/1e9,
            "task_generation": task, "latched_task_type": task_type,
            "rsp_pc_context": hex(pc), "write_start_physical": hex(dest), "row_bytes": size,
            "tail_generation": owner, "tail_start_physical": hex(detail[1]),
            "tail_length": detail[2], "overlap_bytes": overlap, "changed_unread_bytes": changed,
            "first_changed_physical": hex(detail[0]),
            "relative_to_first_full_status": (
                "before" if row[0] < first_full[0] else "after"
            ) if first_full else "no FULL-status marker",
            "relative_to_reported_audio_onset": relation, "onset_delta_seconds": delta,
        })
    audible = bool(onset and onset.get("kind") == "audible_onset")
    if problems:
        verdict = "INCONCLUSIVE: missing/incomplete evidence; stop"
    elif writes:
        verdict = "COMMITTED CHANGED BYTES IN UNSTARTED AI TAIL"
    elif audible:
        verdict = "REPORTED FAILURE WITHOUT OBSERVED RSP-DMA TAIL MUTATION"
    else:
        verdict = "INCONCLUSIVE: no reported acceleration; stop"
    return {
        "verdict": verdict, "missing_evidence": sorted(set(problems)),
        "loaded_rom_md5": loaded_md5, "session": session, "audible_onset": onset,
        "first_full_status_seconds_from_vi": (first_full[1]-epoch)/1e9 if first_full else None,
        "first_full_note": "FULL-status observation is a rejection proxy, not an acoustic onset",
        "safe_audio_write_rows": safe_audio, "identical_value_overlap_rows": same_value,
        "committed_tail_mutations": writes, "coverage_summary": ends[0][4] if len(ends) == 1 else None,
        "limitations": [
            "Observes ParaLLEl RSP DMA stores only; CPU/PI/RDP/wild writers and active-head overlap are unmeasured.",
            "A queued device tail has not started playback; late AI event delivery can still affect console portability.",
            "A mutation proves unread sample replacement, not corruption of all memory or its acoustic impact.",
            "Task type is latched from DMEM OSTask at first-run; RSP PC is context, not an exact JIT-store PC.",
            "Human onset marker has a reported uncertainty; precedence alone is not causation.",
            "Opt-in observer can perturb phase; no non-reproduction certifies health.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ai", type=Path)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--onset", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    onset = json.loads(args.onset.read_text()) if args.onset else None
    if onset and (onset.get("kind") != "audible_onset" or
                  onset.get("uncertainty_seconds", -1) < 0):
        raise ValueError("invalid audible-onset marker")
    try:
        trace = read(args.ai)
        result = analyze(trace, onset, json.loads(args.session.read_text()))
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
