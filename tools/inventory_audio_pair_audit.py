#!/usr/bin/env python3
"""Read-only, pinned M64+SAVE v2 Inventory/audio snapshot comparison.

No emulator, ROM writes, PCM payloads, or chronology inferred from endpoints.
Usage: python tools/inventory_audio_pair_audit.py NORMAL ACCELERATED ROM --output JSON
ROM must be the existing inventory-audio-trace Fortress v01 diagnostic.
"""
import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path

ROM_SHA = "9b7c47758be500535ef10a4c0a063667e50cded66ab28a1b101f0182d4be3152"
STATE_BYTES = 16793412
RDRAM_START = 0x1BC
PC_OFFSET = 0x1002B30
CP0_OFFSET = 0x1002318
EVENT_OFFSET = 0x1002B40
EVENT_NAMES = {1: "VI", 2: "COMPARE", 4: "CHECK", 8: "SI", 16: "PI",
               32: "SPECIAL", 64: "AI", 128: "SP", 256: "DP", 32768: "RSP_TASK"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(path, rom):
    packed = Path(path).read_bytes()
    raw = gzip.decompress(packed)
    require(len(raw) == STATE_BYTES, "Unsupported serializer length")
    require(raw[:12] == b"M64+SAVE\x00\x02\x00\x00", "Not M64+SAVE v2")
    require(raw[12:44].decode("ascii").lower() == hashlib.md5(rom).hexdigest(),
            "State ROM identity mismatch; never cross-load production v02")
    wire = raw[RDRAM_START:RDRAM_START + 0x800000]
    ram = bytearray(0x800000)
    for i in range(4):
        ram[i::4] = wire[3-i::4]

    def mem(address, size):
        require(address >> 24 in (0x80, 0xA0), "Non-RDRAM pointer")
        offset = address & 0x1FFFFFFF
        require(offset + size <= len(ram), "Out-of-range RDRAM pointer")
        return ram[offset:offset + size]

    def u32(address):
        return int.from_bytes(mem(address, 4), "big")

    def u16(address):
        return int.from_bytes(mem(address, 2), "big")

    def wire32(offset):
        return struct.unpack_from("<I", raw, offset)[0]

    require(mem(0x80000400, 0x99C00) == rom[0x1000:0x9AC00],
            "Permanent code differs from diagnostic ROM")
    log = [u32(0x801B3408 + i * 4) for i in range(6)]
    require(log[4:] == [0x41494631, 0x20261008], "Wrong diagnostic log")
    events = []
    for offset in range(EVENT_OFFSET, EVENT_OFFSET + 1024, 8):
        kind = wire32(offset)
        if kind == 0xFFFFFFFF:
            break
        events.append({"type": kind, "name": EVENT_NAMES.get(kind, "OTHER"),
                       "count": wire32(offset + 4)})
    else:
        raise ValueError("Unterminated event queue")
    event_deadlines = {e["type"]: e["count"] for e in events}
    cp0_count = wire32(CP0_OFFSET + 9 * 4)
    ticks = u32(0x800A8038)
    milliseconds, fraction = u32(0x800A803C), u32(0x800A8044)
    require((milliseconds << 16) + fraction == ticks * 546133,
            "WESS fixed-point clock relation changed")
    player_samples = u32(0x800BA4D0)
    require(player_samples == ticks * 184, "Player tick/sample relation changed")
    synth = u32(0x800A8210)
    require(synth == 0x800BA3F4, "Different ALSynth layout")
    audio_infos = []
    for i in range(3):
        pointer = u32(0x800BA3E8 + i * 4)
        pcm = u32(pointer)
        require(pcm == pointer + 0x50, "Unexpected AudioInfo PCM placement")
        audio_infos.append({"pointer": hex(pointer), "pcm": hex(pcm),
                            "samples": u16(pointer + 4),
                            "task_type": u32(pointer + 8),
                            "command_list": hex(u32(pointer + 0x38)),
                            "command_bytes": u32(pointer + 0x3C)})
    nodes, cursor = u32(0x802E8234), u32(0x802C1BB8)
    # Native 0x8001BA80/84 establishes the first bank; two 1000-node banks.
    # The earlier single-state audit hardcoded only the second bank.
    base = cursor - nodes * 0x58
    require(base in (0x800C2950, 0x800D8110), "Unexpected render-node bank")
    palettes = []
    for index in range(0x240):
        if not u16(0x800B75D0 + index * 2):
            continue
        entry = 0x800B7A50 + index * 8
        if not u32(entry) or not 0x140 <= u16(entry + 6) < 0x240:
            continue
        palettes.append({"index": hex(index), "source": hex(u32(entry)),
                         "references": u16(entry + 4), "handle": hex(u16(entry + 6))})
    hud = u32(0x801B2DE0)
    status = wire32(0x160)
    ai = {"status": hex(status), "busy": bool(status & 0x40000000),
          "full": bool(status & 0x80000000), "dram_last_written": hex(wire32(0x154)),
          "len_last_written": wire32(0x158), "dacrate": wire32(0x164),
          "bitrate": wire32(0x168), "head_duration": wire32(0x174),
          "head_length": wire32(0x178), "tail_duration_raw": wire32(0x16C),
          "tail_length_raw": wire32(0x170),
          "tail_live": bool(status & 0x80000000),
          "remaining_head_counts_mod32": ((event_deadlines[64] - cp0_count) & 0xFFFFFFFF)
          if 64 in event_deadlines else None}
    return {"state": Path(path).name, "state_sha256": sha(packed),
            "permanent_code_exact": True,
            "rejections": {"count": log[0], "first_tick": log[1], "last_tick": log[2],
                           "last_ai_status": hex(log[3])},
            "clocks": {"wess_ticks": ticks, "milliseconds": milliseconds,
                       "fraction": fraction, "player_samples": player_samples,
                       "synth_samples": u32(synth + 0x20),
                       "next_player_callback_sample": u32(synth + 0x1C),
                       "audio_frames": u32(0x800A7F60), "vi_callbacks": u32(0x802E7DC0)},
            "cpu": {"count": cp0_count, "pc": hex(wire32(PC_OFFSET)),
                    "epc": hex(wire32(CP0_OFFSET + 14 * 4)),
                    "cause": hex(wire32(CP0_OFFSET + 13 * 4))},
            "vi": {"delay": wire32(0x130), "deadline": event_deadlines.get(1)},
            "ai": ai, "events": events,
            "rsp": {"status": hex(wire32(0xC0)), "pc": hex(wire32(0xE0)),
                    "core_tail_words": list(struct.unpack_from("<3I", raw, len(raw)-12))},
            "audio": {"last_info": hex(u32(0x800A7F70)),
                      "buffer_index": u32(0x800A7F6C), "infos": audio_infos,
                      "fresh_task": hex(u32(0x8009A534)),
                      "queued_task": hex(u32(0x8009A538)),
                      "active_task": hex(u32(0x8009A53C)),
                      "frame_samples": u32(0x800BA454),
                      "minimum_samples": u32(0x800BA450),
                      "maximum_samples": u32(0x800BA458),
                      "extra_samples": u32(0x800A8004)},
            "scheduler_queue": {"valid_count": u32(0x802C1978),
                                "first_index": u32(0x802C197C),
                                "capacity": u32(0x802C1980)},
            "inventory": {"stage": u32(0x8009A910), "process_state": u16(0x802ECE18),
                          "live": [hex(u32(0x800A600C+i*4)) for i in range(10)],
                          "backing": [hex(u32(0x800A6048+i*4)) for i in range(40)],
                          "powers_count": u32(0x800C1248)},
            "memory": {"arena_floor": hex(u32(0x800EECD0)),
                       "arena_cursor": hex(u32(0x80111ECC)),
                       "hud": hex(hud), "hud_sha256": sha(mem(hud, 0x1200)),
                       "fortress_anchor": hex(u32(0x802E822C))},
            "render": {"nodes_in_current_partial_frame": nodes, "cursor": hex(cursor),
                       "bank_base": hex(base), "cursor_consistent": True,
                       "graphics_cursor": hex(u32(0x801AE478)),
                       "texture_boundary": hex(u32(0x800BF2FC)),
                       "upload_queue": hex(u32(0x802C16C0)),
                       "completed_display_list_bytes": [u32(0x802C1B40), u32(0x802C1B54)]},
            "palettes": palettes}


def compare(a, b):
    delta = {key: b["clocks"][key] - a["clocks"][key]
             for key in ("wess_ticks", "audio_frames", "vi_callbacks", "synth_samples", "player_samples")}
    delta["rejections"] = b["rejections"]["count"] - a["rejections"]["count"]
    require(all(value >= 0 for value in delta.values()), "Snapshots reversed or counters reset")
    require(a["vi"]["delay"] == b["vi"]["delay"], "VI period changed at endpoints")
    for field in ("frame_samples", "minimum_samples", "maximum_samples", "extra_samples"):
        require(a["audio"][field] == b["audio"][field], "Audio constant changed: " + field)
    for field in ("dacrate", "bitrate"):
        require(a["ai"][field] == b["ai"][field], "AI constant changed: " + field)
    period = a["vi"]["delay"]
    nominal = delta["audio_frames"] * a["audio"]["frame_samples"]
    count_delta = (b["cpu"]["count"] - a["cpu"]["count"]) & 0xFFFFFFFF
    vi_delta = (b["vi"]["deadline"] - a["vi"]["deadline"]) & 0xFFFFFFFF
    freq = 48681812 // (a["ai"]["dacrate"] + 1)  # NTSC, pinned diagnostic
    minimum_lost = delta["rejections"] * a["audio"]["minimum_samples"]
    maximum_lost = delta["rejections"] * a["audio"]["maximum_samples"]
    return {"delta": delta, "nominal_synth_samples": nominal,
            "synth_surplus_over_nominal": delta["synth_samples"] - nominal,
            "extra_wess_ticks_over_two_per_frame": delta["wess_ticks"] - 2 * delta["audio_frames"],
            "vi_deadline_delta_mod32": vi_delta, "cp0_count_delta_mod32": count_delta,
            "vi_periods_from_deadline_mod32": vi_delta / period,
            "nominal_60hz_interval_seconds": delta["vi_callbacks"] / 60,
            "dac_integer_hz": freq,
            "conditional_rejected_sample_bounds": [minimum_lost, maximum_lost],
            "conditional_rejected_duration_seconds": [minimum_lost/freq, maximum_lost/freq],
            "limitations": ["Endpoints do not retain task generations, queue maxima, failure times, or wall time.",
                            "Count and deadlines are modulo 2^32; extra complete wraps cannot be recovered alone.",
                            "Lost-sample bounds assume fixed native limits, one attempt per frame, and no reset.",
                            "FIFO tail fields are stale whenever FULL is clear; AI_LEN register is the last write.",
                            "Partial render-node counts cannot be compared as complete-frame workload."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("normal")
    parser.add_argument("accelerated")
    parser.add_argument("rom")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rom = Path(args.rom).read_bytes()
    require(sha(rom) == ROM_SHA, "Wrong diagnostic ROM SHA-256")
    states = [decode(args.normal, rom), decode(args.accelerated, rom)]
    report = {"schema": "MKMSZR_inventory_audio_pair_v1", "rom_sha256": ROM_SHA,
              "states": states, "comparison": compare(*states)}
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
