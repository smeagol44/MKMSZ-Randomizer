"""A donor fighter's MKT combo strings on the MKMSZ player's combo graph (reusable component).

Record grammar (Static-confirmed: MKMSZ parser ``0x8004D764`` and driver ``0x8004D4C8``, MKT
driver around ``0x8005D17C``; the two games share it):

====  =======  =====================================================================
Off   Size     Meaning
====  =======  =====================================================================
+0    u8       flags: ``0x80`` = last option of its list
+1    u8       input window (ticks)
+2    u16      hit animation: slot (``0x80 | n`` = secondary/table-1 slot ``n``), phase
+4    u8       animation rate (ticks per frame)
+5    u8       button index (low nibble): 0 HP, 1 LP, 2 block, 3 HK, 4 LK
+6    u16      recovery animation, same encoding as +2
+8    u8       strike selector: index into the combo strike table (MKMSZ ``0x800B0D48``,
               MKT ``0x800B1C4C``; same index -> same reaction number in both games)
+9    u8       extra condition (1-based index into ``0x800A1170``; 1 away, 4 down)
+10   u16      zero
+12   u32      next option list, or a small recovery wait (no pointer: end of the string)
====  =======  =====================================================================

MKT keeps each fighter's two combo roots in ``0x800A8EB0`` (punch, entered from High Punch)
and ``0x800A8F28`` (kick, entered from High Kick); MKMSZ keeps the player's graph at ROM
``0xB1CB0`` (VA ``0x800B10B0``, six stock records) with its roots at ROM ``0xA1C70`` and
``0xA1CE8``.

Translation (Sektor proofs v61/v62, Wiki ``MKT-Adapter-Primitives`` "Combo-record
translation"; generalised here):

* records, option lists, windows, rates, buttons and conditions are copied; next pointers are
  relocated; option lists stay contiguous;
* table-0 animations keep their slot (MKMSZ primary slots are MKT table-0 indices); a
  table-1 animation (``0x80 | n``) becomes host primary :data:`COMBO_SLOT`, which the
  fighter description fills from that donor slot (``body.slot_sources``);
* strike selectors are translated by meaning (:data:`STRIKE_MAP`): selectors whose MKMSZ
  reaction is ``0x12`` ("knocked on back") corrupted the world in Sektor v61 and become the
  Runtime-confirmed knockback ``0x04``, whose damage is raised to 10 (owner decision).
"""

from __future__ import annotations

from dataclasses import dataclass

MKT_ROOTS = (0x800A8EB0, 0x800A8F28)  # punch, kick (by MKT fighter id)
HOST_RECORDS_ROM, HOST_RECORDS_VA, HOST_CAPACITY = 0xB1CB0, 0x800B10B0, 6
HOST_ROOT_PTRS_ROM = (0xA1C70, 0xA1CE8)  # punch, kick
STOCK_ROOTS = (0x800B10B0, 0x800B10F0)
STOCK_RECORDS = bytes.fromhex(
    "800910030200100200000000800b10c0000910040201100200000000800b10d0"
    "000913050304100201050000800b10f08009150101031002010100000000000e"
    "800c13030303130201000000800b11008009150102031302040100000000000e"
)
RECORD_REGION = (0x800A0000, 0x800C0000)  # MKT data segment: option lists; code lies below
COMBO_SLOT = 0x10  # host primary "elbow/combo"
LAST = 0x80

# Donor strike selector -> host selector. Same index, same reaction number in both tables
# (0x800B1C4C / 0x800B0D48); host reaction 0x12 ("knocked on back", indices 2 and 18) is not
# usable (Sektor v61), knockback 0x04 (reaction 0x14) is Runtime-confirmed (Sektor v62).
STRIKE_MAP = {
    0x00: 0x00,  # hit (reaction 0x10), Sektor v62
    0x01: 0x01,  # stumble (0x11), Sektor v62
    0x02: 0x04,  # knocked on back -> knockback (0x14), Sektor v62
    0x05: 0x05,  # uppercut (0x15), Sektor v62
    0x12: 0x04,  # knocked on back, damage 10 -> knockback (0x14), damage 7 (Reptile; Pending)
    0x09: 0x09,  # reaction 0x17, damage 7 in both tables (Rayden's last LP; Pending)
}
# Owner decision (2026-11-11, Reptile inputs proof v01): the knockback finisher (host strike
# record 0x800B0E30, selectors 4 and 20) does 10 damage, MKT's "knocked on back" value,
# instead of the stock 7. Only the combo driver reads that record (0x8004D638).
KNOCKBACK_RECORD_ROM, KNOCKBACK_SELECTOR = 0xB1A30, 0x04
KNOCKBACK_STOCK = bytes.fromhex("00410000003300851412070100000201")
KNOCKBACK_DAMAGE = 0x0A
CONDITIONS = {0x00, 0x01, 0x04}  # none, away, down (Sektor v62)
# Button index = the input event order of both games' handler tables (MKMSZ ``0x800A0478 +
# 0x78*i``: HP, LP, block, HK, LK; MKT grid events 0 HP, 1 LP, 3 HK, 4 LK). Rayden's kick
# string uses index 4 (LK); earlier labels had 2 and 4 swapped (labels only).
BUTTONS = {0: "HP", 1: "LP", 2: "BL", 3: "HK", 4: "LK"}


class ComboError(ValueError):
    pass


def _u32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o : o + 4], "big")


@dataclass(frozen=True)
class Graph:
    lists: tuple[tuple[int, ...], ...]  # option lists (donor record VAs), in discovery order
    roots: tuple[int, int]  # punch, kick (donor VAs of list heads)
    records: dict[int, bytes]  # donor VA -> 16 bytes
    dropped: tuple[tuple[int, int], ...] = ()  # (record VA, action VA): options that call an action


def donor_graph(mkt: bytes, fighter: int) -> Graph:
    """The fighter's two combo roots and every option list they reach. A next pointer may name
    the middle of a list (Rayden: two strings share a list's tail); that tail stays inside its
    list, whose records are then reached from both places (the host parser reads a list from
    any record to its last)."""

    roots = tuple(_u32(mkt, t - 0x80000000 + 4 * fighter) for t in MKT_ROOTS)
    runs: dict[int, tuple[int, ...]] = {}
    dropped: list[tuple[int, int]] = []
    records: dict[int, bytes] = {}
    queue = list(roots)
    while queue:
        head = queue.pop(0)
        if head in runs:
            continue
        va, lst = head, []
        while True:
            rec = mkt[va - 0x80000000 : va - 0x80000000 + 16]
            nxt = _u32(rec, 12)
            if nxt >= 0x80000000 and not RECORD_REGION[0] <= nxt < RECORD_REGION[1]:
                # The option ends in a routine (Rayden: 0x8004F3C0 starts his torpedo): a combo
                # into a special, which the host graph cannot call. Left out (logged).
                dropped.append((va, nxt))
            else:
                records[va] = rec
                lst.append(va)
                if nxt >= 0x80000000:
                    queue.append(nxt)
            if rec[0] & LAST:
                break
            va += 16
            if len(lst) > 8:
                raise ComboError(f"option list at 0x{head:08X} has no end")
        runs[head] = tuple(lst)
    # A run whose head option was left out starts at its next option: point there.
    for va, rec in list(records.items()):
        nxt = _u32(rec, 12)
        if nxt in runs and runs[nxt] and runs[nxt][0] != nxt:
            records[va] = rec[:12] + runs[nxt][0].to_bytes(4, "big")
        elif nxt in runs and not runs[nxt]:
            raise ComboError(f"0x{va:08X}: every option of the list at 0x{nxt:08X} calls an action")
    runs = {(r[0] if r else h): r for h, r in runs.items()}
    # Keep each run that is not the tail of a longer one, in discovery order.
    lists = [r for h, r in runs.items() if r and not any(h in o and h != o[0] for o in runs.values())]
    return Graph(tuple(lists), roots, records, tuple(dropped))  # type: ignore[arg-type]


def _animation(sel: int, table1_slot: int | None, slots: set[int], where: str) -> int:
    hi, phase = sel >> 8, sel & 0xFF
    if hi & 0x80:
        if table1_slot is None or hi & 0x7F != table1_slot:
            raise ComboError(f"{where}: donor table-1 animation 0x{hi & 0x7F:02X} has no host slot")
        return COMBO_SLOT << 8 | phase
    if hi not in slots:
        raise ComboError(f"{where}: host slot 0x{hi:02X} is not imported")
    return sel


@dataclass(frozen=True)
class Lowered:
    records: bytes  # host records, from HOST_RECORDS_VA
    roots: tuple[int, int]  # host VAs
    strings: tuple[str, ...]  # human-readable strings (entry button first)
    strikes: dict[int, int]  # donor -> host strike selectors used


def lower(graph: Graph, table1_slot: int | None, slots: set[int], capacity: int = HOST_CAPACITY) -> Lowered:
    """The host records for ``graph``. ``table1_slot``: the donor table-1 slot that host
    primary :data:`COMBO_SLOT` holds; ``slots``: the imported host primary slots."""

    n = sum(len(lst) for lst in graph.lists)
    if n > capacity:
        raise ComboError(f"{n} combo records do not fit the host graph ({capacity})")
    place: dict[int, int] = {}
    va = HOST_RECORDS_VA
    for lst in graph.lists:
        for rec in lst:
            place[rec] = va
            va += 16
    out, strikes = bytearray(), {}
    for lst in graph.lists:
        for donor_va in lst:
            rec = bytearray(graph.records[donor_va])
            where = f"record 0x{donor_va:08X}"
            for off in (2, 6):
                sel = int.from_bytes(rec[off : off + 2], "big")
                rec[off : off + 2] = _animation(sel, table1_slot, slots, where).to_bytes(2, "big")
            if rec[8] not in STRIKE_MAP:
                raise ComboError(f"{where}: strike selector 0x{rec[8]:02X} has no host meaning")
            strikes[rec[8]] = STRIKE_MAP[rec[8]]
            rec[8] = STRIKE_MAP[rec[8]]
            if rec[9] not in CONDITIONS:
                raise ComboError(f"{where}: condition {rec[9]} has no host meaning")
            nxt = _u32(rec, 12)
            if nxt >= 0x80000000:
                rec[12:16] = place[nxt].to_bytes(4, "big")
            out += rec
    return Lowered(bytes(out), (place[graph.roots[0]], place[graph.roots[1]]),
                   tuple(strings(graph)), strikes)  # fmt: skip


def strings(graph: Graph) -> list[str]:
    """Every complete string, e.g. ``HP, HP, D+LP`` (the entry button, then each record)."""

    def name(rec: bytes) -> str:
        cond = {1: "B+", 4: "D+"}.get(rec[9], "")
        return cond + BUTTONS.get(rec[5] & 0xF, f"?{rec[5] & 0xF}")

    out: list[str] = []

    def walk(head: int, path: list[str]) -> None:
        lst = next(lst for lst in graph.lists if head in lst)
        for va in lst[lst.index(head) :]:
            rec = graph.records[va]
            here = [*path, name(rec)]
            nxt = _u32(rec, 12)
            if nxt >= 0x80000000:
                walk(nxt, here)
            else:
                out.append(", ".join(here))

    walk(graph.roots[0], ["HP"])
    walk(graph.roots[1], ["HK"])
    return out


def install(rom: bytearray, low: Lowered) -> None:
    """Write the host records and roots (guarded against the clean bytes)."""

    end = HOST_RECORDS_ROM + 16 * HOST_CAPACITY
    if bytes(rom[HOST_RECORDS_ROM:end]) != STOCK_RECORDS:
        raise ComboError("host combo records are not stock")
    for ptr, stock in zip(HOST_ROOT_PTRS_ROM, STOCK_ROOTS, strict=True):
        if _u32(rom, ptr) != stock:
            raise ComboError(f"host combo root at ROM 0x{ptr:X} is not stock")
    rom[HOST_RECORDS_ROM : HOST_RECORDS_ROM + len(low.records)] = low.records
    if KNOCKBACK_SELECTOR in low.strikes.values():
        rec = KNOCKBACK_RECORD_ROM
        if bytes(rom[rec : rec + 16]) != KNOCKBACK_STOCK:
            raise ComboError("host knockback strike record is not stock")
        rom[rec + 10] = KNOCKBACK_DAMAGE
    for ptr, root in zip(HOST_ROOT_PTRS_ROM, low.roots, strict=True):
        rom[ptr : ptr + 4] = root.to_bytes(4, "big")
