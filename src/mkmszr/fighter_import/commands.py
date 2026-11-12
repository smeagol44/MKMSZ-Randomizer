"""A donor fighter's MKT special commands on the MKMSZ player's button tables (reusable component).

Both games keep special commands as ``0x2C``-byte records in one table per button event (Wiki
``MKT-Adapter-Primitives`` "Special-move command translation"; ``Player-Actions-and-Special-
Moves``): two ``u16`` button masks, ``u32`` transfer selector, condition, action, ``u16``
window, six facing-right and seven facing-left direction tokens (newest first; 6 up, 7 down,
8 left, 9 right), zero ``u16`` sentinel after the last record. Masks: ``0x80`` LP, ``0x40`` LK,
``0x20`` HK, ``0x10`` HP. A record's mask lets any of its buttons through; MKT puts a
two-button command (Reptile's forceballs, ``0x90``) in each of its buttons' tables and checks
the second button in its condition.

Static-confirmed differences handled here:

* **Refusal.** MKT's parser ``0x8004BEB0`` tries the next record when a condition refuses; the
  MKMSZ parser ``0x8004A0E0`` ends the scan (``0x4000`` -> ``process_exit``). A command whose
  donor condition checks held buttons gets a stub condition: buttons held -> the host
  condition it calls; else it hands the rest of the table to the parser (the MKT order works).
* **Room.** The host tables are LP ``0x800B0F0C`` (2 records), LK ``0x800B0F68`` (1), HK
  ``0x800B0F98`` (1), HP ``0x800B1028`` (3), each loaded by one ``lui``/``addiu`` pair. A
  table that grows moves to caller-owned storage and its load pair is repointed.

Milestone 4 step 2: each donor command calls the action, condition and transfer selector of
the Sub-Zero power it replaces (the fighter description's ``commands``); host records whose
power no command uses stay, after the donor ones, unless the description removes them.
"""

from __future__ import annotations

from dataclasses import dataclass

from .mips import Assembler

RECORD = 0x2C
HELD_BUTTONS = 0x800BF2EE  # player's held buttons (``0x8003CD50``: & 0xFC, record-mask bits)
PARSER = 0x8004A0E0
BUTTONS = {"LP": 0x80, "LK": 0x40, "HK": 0x20, "HP": 0x10}
VA_TO_ROM = 0x7FFFF400


@dataclass(frozen=True)
class HostTable:
    button: str
    va: int
    capacity: int
    load: tuple[int, int]  # VAs of the lui / addiu (a0) that load the table


HOST_TABLES = (
    HostTable("HP", 0x800B1028, 3, (0x8003C88C, 0x8003C890)),
    HostTable("LP", 0x800B0F0C, 2, (0x8003C9D8, 0x8003C9DC)),
    HostTable("LK", 0x800B0F68, 1, (0x8003C95C, 0x8003C960)),
    HostTable("HK", 0x800B0F98, 1, (0x8003C850, 0x8003C854)),
)
# Sub-Zero's command records (Wiki Player-Actions-and-Special-Moves, stock reconciliation).
HOST_POWERS = {
    "spine_rip": 0x800B1028,
    "polar_blast": 0x800B1054,
    "freeze_on_contact": 0x800B1080,
    "ice_clone": 0x800B0F0C,
    "ice_blast": 0x800B0F38,  # also Air Ice Blast (airborne branch of its condition)
    "directional_ice_down": 0x800B0F68,
    "directional_ice_up": 0x800B0F98,
}
# Sub-Zero powers with no command record (Ice Shatter is contextual, after two Ice Blasts). A
# move may take one only with its own special (``lower(overrides=...)``): its record is new.
COMMANDLESS_POWERS = ("ice_shatter",)


class CommandError(ValueError):
    pass


def _u16(b: bytes, o: int) -> int:
    return int.from_bytes(b[o : o + 2], "big")


def _u32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o : o + 4], "big")


def record_at(image: bytes, va: int, delta: int) -> bytes:
    return bytes(image[va - delta : va - delta + RECORD])


@dataclass(frozen=True)
class Command:
    name: str
    donor_va: int
    record: bytes  # the donor record (MKT)
    calls: str | None  # host power whose action it calls; None: no action yet
    held: int  # buttons the donor condition requires held (0: none)


@dataclass(frozen=True)
class Lowered:
    tables: dict[str, list[bytes]]  # button -> records (host)
    moved: dict[str, int]  # button -> new table VA (outside the stock table)
    stubs: bytes  # code at the stub base
    report: list[str]


def _host_record(clean: bytes, cmd: Command, cond: int, override: tuple[int, int, int] | None) -> bytes:
    if override is None:
        stock = record_at(clean, HOST_POWERS[cmd.calls], VA_TO_ROM)  # type: ignore[index]
        selector, action = _u32(stock, 4), _u32(stock, 12)
    else:
        selector, action = override[0], override[2]
    rec = bytearray(cmd.record)
    rec[4:16] = selector.to_bytes(4, "big") + cond.to_bytes(4, "big") + action.to_bytes(4, "big")
    return bytes(rec)


def lower(clean: bytes, commands: list[Command], remove: set[str], storage: int,
          stub_base: int, overrides: dict[str, tuple[int, int, int]] | None = None) -> Lowered:  # fmt: skip
    """Host tables for ``commands``. ``storage``: VA (KSEG1) where grown tables go, in order;
    ``stub_base``: VA (KSEG1) of the condition stubs, linked after the tables are placed.
    ``overrides``: command name -> (transfer selector, condition, action) of the move's own
    special (milestone 4 step 3) instead of the replaced power's."""

    overrides = overrides or {}
    unwired = [c.name for c in commands if c.calls is None]
    used = {c.calls for c in commands if c.calls}
    for name in used | remove:
        if name not in HOST_POWERS and name not in COMMANDLESS_POWERS:
            raise CommandError(f"unknown host power {name!r}")
    for cmd in commands:
        if cmd.calls in COMMANDLESS_POWERS and cmd.name not in overrides:
            raise CommandError(f"{cmd.name}: {cmd.calls} has no command record; the move needs its own special")
    kept = {p for p in HOST_POWERS if p not in used and p not in remove}
    tables: dict[str, list[tuple[str, Command | None, int]]] = {}
    for table in HOST_TABLES:
        mask = BUTTONS[table.button]
        rows: list[tuple[str, Command | None, int]] = []
        for cmd in sorted((c for c in commands if c.calls), key=lambda c: c.donor_va):
            if (_u16(cmd.record, 0) | _u16(cmd.record, 2)) & mask:
                rows.append(("donor", cmd, 0))
        for name, va in HOST_POWERS.items():
            if name in kept and table.va <= va < table.va + RECORD * table.capacity:
                rows.append(("host", None, va))
        tables[table.button] = rows
    # Place the tables, then emit the stubs (they need each record's successor).
    moved: dict[str, int] = {}
    cursor = storage
    place: dict[str, int] = {}
    for table in HOST_TABLES:
        n = len(tables[table.button])
        if n > table.capacity:
            moved[table.button] = cursor
            place[table.button] = cursor
            cursor += RECORD * n + 4
        else:
            place[table.button] = table.va
    a = Assembler(stub_base, cached_calls=True)
    out: dict[str, list[bytes]] = {}
    report: list[str] = []
    for table in HOST_TABLES:
        recs = []
        for k, (kind, cmd, va) in enumerate(tables[table.button]):
            if kind == "host":
                recs.append(record_at(clean, va, VA_TO_ROM))
                report.append(f"{table.button}: keep {_name(va)}")
                continue
            assert cmd is not None and cmd.calls is not None
            override = overrides.get(cmd.name)
            if override is not None:
                stock_cond = override[1]
            else:
                stock_cond = _u32(record_at(clean, HOST_POWERS[cmd.calls], VA_TO_ROM), 8)
            cond = stock_cond
            if cmd.held:
                label = f"held_{table.button}_{k}"
                cond = a.pc()
                _emit_held(a, label, cmd.held, stock_cond, place[table.button] + RECORD * (k + 1))
            recs.append(_host_record(clean, cmd, cond, override))
            target = f"own special (slot of {cmd.calls})" if override else cmd.calls
            report.append(f"{table.button}: {cmd.name} -> {target}" + (" (held check)" if cmd.held else ""))
        out[table.button] = recs
    if unwired:
        report.append("no action yet: " + ", ".join(unwired))
    return Lowered(out, moved, a.link(), report)


def _name(va: int) -> str:
    return next(n for n, v in HOST_POWERS.items() if v == va)


def _emit_held(a: Assembler, label: str, mask: int, stock_cond: int, next_record: int) -> None:
    """Condition stub: every button of ``mask`` held -> ``stock_cond`` (tail call, ``ra``
    unchanged); else the parser scans on from ``next_record`` (it never returns)."""

    a.lui("t0", ((HELD_BUTTONS + 0x8000) >> 16) & 0xFFFF)
    a.lhu("t0", ((HELD_BUTTONS & 0xFFFF) ^ 0x8000) - 0x8000, "t0")
    a.andi("t0", "t0", mask)
    a.addiu("t1", "zero", mask)
    a.bne("t0", "t1", label + "_next")
    if stock_cond:
        a.j(stock_cond)
    else:
        a.jr("ra")
        a.addiu("v0", "zero", 0)
    a.label(label + "_next")
    a.lui("a0", ((next_record + 0x8000) >> 16) & 0xFFFF)
    a.addiu("a0", "a0", ((next_record & 0xFFFF) ^ 0x8000) - 0x8000)
    a.j(PARSER)


def install(rom: bytearray, clean: bytes, low: Lowered, storage_rom: int, storage_va: int) -> None:
    """Write the tables: in place (guarded, sentinel after the last record) or at
    ``storage_rom`` (mirroring ``storage_va``) with the table's load pair repointed."""

    for table in HOST_TABLES:
        recs = low.tables[table.button]
        span = RECORD * table.capacity + 2
        stock_rom = table.va - VA_TO_ROM
        if bytes(rom[stock_rom : stock_rom + span]) != clean[stock_rom : stock_rom + span]:
            raise CommandError(f"{table.button} table is not stock")
        data = b"".join(recs) + b"\0\0\0\0"
        if table.button in low.moved:
            va = low.moved[table.button]
            off = storage_rom + (va - storage_va)
            rom[off : off + len(data)] = data
            lui, addiu = (x - VA_TO_ROM for x in table.load)
            old_lui, old_addiu = _u32(rom, lui), _u32(rom, addiu)
            if (old_lui & 0xFFFF) != ((table.va + 0x8000) >> 16) or (old_addiu & 0xFFFF) != (table.va & 0xFFFF):
                raise CommandError(f"{table.button} table load is not stock")
            rom[lui : lui + 4] = ((old_lui & 0xFFFF0000) | ((va + 0x8000) >> 16 & 0xFFFF)).to_bytes(4, "big")
            rom[addiu : addiu + 4] = ((old_addiu & 0xFFFF0000) | (va & 0xFFFF)).to_bytes(4, "big")
        else:
            rom[stock_rom : stock_rom + len(data) - 2] = data[:-2]


def donor_commands(mkt: bytes, moves: list, spec: dict[str, str | None]) -> list[Command]:
    """Commands from the move programs (``command.src`` = the donor record) and the
    description's move -> host power map."""

    out = []
    for move in moves:
        if move.name not in spec:
            continue
        src = move.command.get("src", "")
        if not src.startswith("MKT 0x"):
            raise CommandError(f"{move.name}: command has no donor record")
        va = int(src[4:], 16)
        held = 0
        for cond in move.command.get("conditions", []):
            if cond.get("kind") == "buttons_held":
                held |= int(cond["mask"], 16)
        out.append(Command(move.name, va, record_at(mkt, va, 0x80000000), spec[move.name], held))
    missing = set(spec) - {c.name for c in out}
    if missing:
        raise CommandError(f"no move program for {', '.join(sorted(missing))}")
    return out
