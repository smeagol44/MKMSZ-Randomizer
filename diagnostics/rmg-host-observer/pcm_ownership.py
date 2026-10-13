"""Replay AI leases and actual DMA word commits, not stale ready seals.

Pinned RMG source consumes guest PCM synchronously after events 0x12/0x14.
No hardware read cursor or other guest-memory writers are inferred here.
"""

from array import array


def replay(rows):
    writers = array("I", [0]) * 0x200000
    write_ns = array("Q", [0]) * 0x200000
    write_seq = array("Q", [0]) * 0x200000
    packets = {}
    completed = {}
    types = {}
    released_writers = {}
    qualified = {}
    copies = []
    head = tail = task = 0

    def word_range(packet):
        return packet["address"] // 4, (packet["address"] + packet["length"]) // 4

    def generation(packet):
        begin, end = word_range(packet)
        owners = set(writers[begin:end])
        return next(iter(owners)) if len(owners) == 1 and 0 not in owners else None

    def remember_release(packet, row):
        owner = generation(packet)
        packet["release_sequence"] = row[0]
        if owner in completed:
            released_writers[owner, packet["address"]] = {
                "tail_generation": packet["id"], "sequence": row[0], "ns": row[1],
            }

    for index, row in enumerate(rows):
        seq, ns, event, count, values = row
        if event == 0x85:
            task = values[0]
            types[task] = values[1]
        elif event == 0x87 and values[2] & 0x203 == 0x203:
            completed[values[0]] = row
            if tail and values[1] == 2:
                packet = packets[tail]
                if packet["owner_generation"] is None and generation(packet) == values[0]:
                    # A live lease's own complete observed synthesis binds it.
                    # A stale last writer discovered at ACCEPT does not.
                    packet["owner_generation"] = values[0]
                    packet["owner_bound_sequence"] = seq
        elif event == 0x81:
            full = bool(values[6] & 0x80000000)
            identifier = values[3] if full else values[0]
            address = values[4] if full else values[1]
            length = values[5] if full else values[2]
            packets[identifier] = {
                "id": identifier, "address": address, "length": length,
                "accept_sequence": seq, "accept_ns": ns,
                "owner_generation": None, "initial_writers": set(),
                "raw_seal": 0, "prior_released_lease": None,
                "has_qualified_replacement": False,
            }
            head, tail = values[0], values[3] if full else 0
        elif event == 0x8a and tail and values[0] == tail:
            packet = packets[tail]
            packet["raw_seal"] = values[1]
            if packet["prior_released_lease"] is None:
                packet["prior_released_lease"] = released_writers.get(
                    (values[1], packet["address"]))
        elif event == 0x83 and not values[7] & 16:
            destination, size, _task_type, _, identifier, overlap, changed, flags = values
            if overlap and identifier == tail and tail:
                packet = packets[tail]
                packet["initial_writers"].add(task)
                owner = packet["owner_generation"]
                if changed and flags & 8 and owner and owner != task and types.get(owner) == 2:
                    qualified[seq] = owner
                    packet["has_qualified_replacement"] = True
            destination &= 0x7ffffc
            # Same aligned words and wrap as the instrumented ParaLLEl stores.
            length = min(size, 0x800000 - destination)
            for start, bytes_ in ((destination, length), (0, size - length)):
                if not bytes_:
                    continue
                begin, end = start // 4, (start + bytes_) // 4
                writers[begin:end] = array("I", [task]) * (end - begin)
                write_ns[begin:end] = array("Q", [ns]) * (end - begin)
                write_seq[begin:end] = array("Q", [seq]) * (end - begin)
        elif event == 0x82:
            if head in packets:
                remember_release(packets[head], row)
            if tail:
                packet = packets[tail]
                packet["promotion_sequence"] = seq
                packet["promotion_ns"] = ns
                packet["writer_at_promotion"] = generation(packet)
                packet["completed_at_promotion"] = packet["writer_at_promotion"] in completed
            head, tail = values[0], values[3] if values[6] & 0x80000000 else 0

        offset = size = 0
        if event == 0x12 and values[0] < values[4]:
            offset, size = values[2] - values[4], values[4] - values[0]
        elif event == 0x14 and values[3]:
            offset, size = values[1] - values[3], values[3]
        if size and head in packets:
            packet = packets[head]
            address = packet["address"] + offset
            begin, end = address // 4, (address + size) // 4
            copies.append({
                "sequence": seq, "next_ai_ns": rows[index + 1][1] if index + 1 < len(rows) else None,
                "ns": ns, "count": count, "event": hex(event),
                "tail_generation": head, "offset": offset, "bytes": size,
                "physical_start": hex(address), "word_writers": sorted(set(writers[begin:end])),
                "latest_word_commit_sequence": max(write_seq[begin:end], default=0),
                "latest_word_commit_ns": max(write_ns[begin:end], default=0),
            })

    for packet in packets.values():
        packet["initial_writers"] = sorted(packet["initial_writers"])
    return {"packets": packets, "qualified_sequences": qualified,
            "copies": copies, "completed": completed}


def assess_promoted_initialization(ownership, identifiers, host_rows=None):
    """Assess actual pinned-backend source reads, not continuous DAC playback."""
    packets, completed = ownership["packets"], ownership["completed"]
    pairs_valid = None
    pair_problems = []
    if host_rows is not None:
        requests = [row for row in host_rows if row[2] == 0x50]
        results = [row for row in host_rows if row[2] == 0x52]
        copies = ownership["copies"]
        if len(requests) != len(copies) or len(results) != len(copies):
            pair_problems.append("core source-read and host request/result counts differ")
        elif any(copy["bytes"] != request[4][0] or copy["bytes"] != result[4][0]
                 or copy["next_ai_ns"] is None
                 or not copy["ns"] <= request[1] <= result[1] <= copy["next_ai_ns"]
                 or not result[4][3]
                 for copy, request, result in zip(copies, requests, results)):
            pair_problems.append("host size/order/success does not match synchronous core copy")
        if any(row[2] == 0x51 for row in host_rows):
            pair_problems.append("host dropped source reads")
        pairs_valid = not pair_problems
    evidence = []
    for copy in ownership["copies"]:
        if copy["tail_generation"] not in identifiers:
            continue
        packet = packets[copy["tail_generation"]]
        expected = packet["owner_generation"]
        if expected is None and len(packet["initial_writers"]) == 1:
            expected = packet["initial_writers"][0]
        complete = completed.get(expected)
        evidence.append({**copy, "expected_generation": expected,
                         "particular_words_complete_before_read": (
                             expected is not None and copy["word_writers"] == [expected]
                             and copy["latest_word_commit_sequence"] < copy["sequence"]),
                         "particular_word_lead_ms": (
                             copy["ns"] - copy["latest_word_commit_ns"]) / 1e6,
                         "whole_task_complete_before_read": bool(
                             complete and complete[0] < copy["sequence"]),
                         "whole_task_lead_ms": (
                             copy["ns"] - complete[1]) / 1e6 if complete else None})
    covered = set()
    for identifier in identifiers:
        cursor = 0
        for copy in sorted((c for c in evidence if c["tail_generation"] == identifier),
                           key=lambda c: c["offset"]):
            if copy["offset"] != cursor:
                break
            cursor += copy["bytes"]
        if cursor == packets[identifier]["length"]:
            covered.add(identifier)
    return {"host_pairs_verified": pairs_valid, "host_pair_problems": pair_problems,
            "all_core_copy_calls": len(ownership["copies"]), "evidence": evidence,
            "assessed_buffers": len(identifiers), "fully_read_buffers": len(covered),
            "assessed_copy_calls": len(evidence), "assessed_bytes": sum(c["bytes"] for c in evidence),
            "all_particular_words_complete": bool(evidence) and all(
                c["particular_words_complete_before_read"] for c in evidence),
            "minimum_particular_word_lead_ms": min(
                (c["particular_word_lead_ms"] for c in evidence), default=None),
            "scope": "Pinned RMG synchronous guest-PCM source copies; not a physical N64 DAC read cursor"}
