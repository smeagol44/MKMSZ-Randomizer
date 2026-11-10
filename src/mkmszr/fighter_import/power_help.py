"""Sektor's Power Ups help text (R4 presentation, user decision: Sektor's move names, empty
slots labelled as such).

The native Power Ups screen draws, for each unlocked slot, the help record the table at ROM
``0xA78A0`` names (the power-order shuffle permutes that table by record address). A record
is a zero-terminated list of string pointers, ``1`` separating its groups (title, command,
description). The nine stock records fill ``[0x800A6B30, 0x800A6CA0)`` and their strings
``[0x800AE5D8, 0x800AE914)``; nothing else points into either range except the button-name
table at ``0x800AEBB8``, which shares ``"LOW PUNCH"`` at ``0x800AE604`` (kept in place).

:func:`edits` rebuilds the nine records for Sektor in place (keyed by the Sub-Zero power
whose slot each Sektor move took, so they follow any shuffle), packs their strings into the
string block around the pinned string, and remaps the table entries.
"""

from __future__ import annotations

from ..patches.power_order import POWER_HELP, POWER_NAMES

VA_TO_ROM = 0x7FFFF400
HELP_TABLE_ROM = 0xA78A0
RECORDS = (0x800A6B30, 0x800A6CA0)
STRINGS = (0x800AE5D8, 0x800AE914)
PINNED = {0x800AE604: "LOW PUNCH"}  # also named by the button-name table 0x800AEBB8
EMPTY = (("--",),)
STOCK_SLIDE = (("SLIDE",), ("BLOCK, LOW PUNCH,", "LOW KICK, AND", "BACK"),
               ("CAN SLIDE UNDER", "PROJECTILES AND", "HIGH ATTACKS."))  # fmt: skip
STOCK_SUPER_SLIDE = (("SUPER SLIDE",), ("BLOCK, LOW PUNCH,", "HIGH PUNCH, AND", "BACK"),
                     ("SAME AS NORMAL", "SLIDE, EXCEPT IT", "IS LONGER", "REACHING AND CAN",
                      "TAKE OUT MULTIPLE", "ENEMIES."))  # fmt: skip
STOCK_POLAR_BLAST = (("POLAR BLAST",), ("TOWARDS,", "AWAY, AWAY,", "HIGH PUNCH."),
                     ("FREEZES ALL", "ENEMIES ON SCREEN", "WITHIN THE BLAST", "RADIUS."))  # fmt: skip

# Sub-Zero power (the slot) -> the help groups of the Sektor move in that slot.
SEKTOR_HELP: dict[str, tuple[tuple[str, ...], ...]] = {
    "ice-blast": (("STRAIGHT MISSILE",), ("FORWARD, FORWARD,", "LOW PUNCH"),
                  ("SEKTOR FIRES A", "MISSILE FROM HIS", "CHEST.")),
    "slide": STOCK_SLIDE,
    "directional-ice": (("TELEPORT", "UPPERCUT"), ("FORWARD, FORWARD,", "LOW KICK."),
                        ("SEKTOR TELEPORTS", "BEHIND THE NEAREST", "ENEMY AND",
                         "UPPERCUTS IT.")),
    "air-ice-blast": (("HEAT-SEEKING", "MISSILE"), ("FORWARD, DOWN,", "BACK, HIGH PUNCH."),
                      ("A MISSILE THAT", "HUNTS DOWN THE", "NEAREST ENEMY.")),
    "ice-clone": EMPTY,
    "ice-shatter": (("DOUBLE MISSILE",), ("BACK, BACK,", "FORWARD,", "LOW PUNCH."),
                    ("FIRES TWO", "MISSILES IN A ROW.")),
    "super-slide": EMPTY,
    "freeze-on-contact": STOCK_SUPER_SLIDE,
    "polar-blast": STOCK_POLAR_BLAST,
}  # fmt: skip
MAX_LINE = 18  # the longest stock line ("GIVES SUB-ZERO THE")
CHARSET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.-")  # characters the stock help uses


class HelpError(ValueError):
    pass


def _word(rom: bytes, off: int) -> int:
    return int.from_bytes(rom[off : off + 4], "big")


def _pack_strings(lines: list[str]) -> dict[str, int]:
    """String -> VA: pinned ones in place, the rest 4-aligned in the free spans."""

    where = {text: va for va, text in PINNED.items()}
    spans = []
    cursor = STRINGS[0]
    for va in sorted(PINNED):
        spans.append([cursor, va])
        cursor = (va + len(PINNED[va]) + 1 + 3) & ~3
    spans.append([cursor, STRINGS[1]])
    for text in lines:
        if text in where:
            continue
        need = len(text) + 1
        for span in spans:
            if span[0] + need <= span[1]:
                where[text] = span[0]
                span[0] = (span[0] + need + 3) & ~3
                break
        else:
            raise HelpError("Sektor help strings do not fit the stock string block")
    return where


def edits(
    rom: bytes, help_text: dict[str, tuple[tuple[str, ...], ...]] = SEKTOR_HELP
) -> dict[int, bytes]:
    """ROM offset -> bytes that put ``help_text`` on the Power Ups screen of ``rom`` (a clean
    or randomizer ROM after any power-order shuffle; the blocks must still be stock)."""

    by_record = {va: name for name, va in POWER_HELP.items()}
    table = [_word(rom, HELP_TABLE_ROM + 4 * i) for i in range(len(POWER_NAMES))]
    if sorted(table) != sorted(by_record):
        raise HelpError("Power Ups help table is not a permutation of the stock records")
    for va, text in PINNED.items():
        off = va - VA_TO_ROM
        if rom[off : off + len(text) + 1] != text.encode() + b"\0":
            raise HelpError(f"pinned string {text!r} moved")
    lines = []
    for name in POWER_NAMES:
        for group in help_text[name]:
            for line in group:
                if len(line) > MAX_LINE or not set(line) <= CHARSET:
                    raise HelpError(f"help line {line!r} is too long or uses other characters")
                if line not in lines:
                    lines.append(line)
    where = _pack_strings(lines)
    records, cursor = {}, RECORDS[0]
    blob = b""
    for name in POWER_NAMES:
        words: list[int] = []
        for k, group in enumerate(help_text[name]):
            if k:
                words.append(1)
            words += [where[line] for line in group]
        words.append(0)
        records[name] = cursor
        blob += b"".join(w.to_bytes(4, "big") for w in words)
        cursor += 4 * len(words)
    if cursor > RECORDS[1]:
        raise HelpError("Sektor help records do not fit the stock record block")
    out = {RECORDS[0] - VA_TO_ROM: blob + bytes(RECORDS[1] - cursor)}
    strings = bytearray(STRINGS[1] - STRINGS[0])
    for text, va in where.items():
        strings[va - STRINGS[0] : va - STRINGS[0] + len(text)] = text.encode()
    out[STRINGS[0] - VA_TO_ROM] = bytes(strings)
    out[HELP_TABLE_ROM] = b"".join(records[by_record[va]].to_bytes(4, "big") for va in table)
    return out


def read_help(rom: bytes) -> list[tuple[tuple[str, ...], ...]]:
    """The help groups the table of ``rom`` shows, slot by slot (for tests and reports)."""

    def text(va: int) -> str:
        off = va - VA_TO_ROM
        return rom[off : rom.index(b"\0", off)].decode("latin1")

    shown = []
    for i in range(len(POWER_NAMES)):
        off, groups, group = _word(rom, HELP_TABLE_ROM + 4 * i) - VA_TO_ROM, [], []
        while (w := _word(rom, off)) != 0:
            off += 4
            if w == 1:
                groups.append(tuple(group))
                group = []
            else:
                group.append(text(w))
        groups.append(tuple(group))
        shown.append(tuple(groups))
    return shown
