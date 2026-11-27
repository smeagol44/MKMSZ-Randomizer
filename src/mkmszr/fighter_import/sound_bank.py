"""More MKMSZ sound host chains: the sound bank and the event module, enlarged and moved.

The 16 isolated chains (:data:`sound.ISOLATED_CHAINS`) are the stock bank's only unreachable
event -> patch -> subpatch -> waveform sets (Wiki ``Sounds-and-Music``), and the bank has no
other free records. Extra chains are therefore appended (owner, 2026-11-27: the "more sounds"
route, option 1). Static-confirmed host facts (clean MKMSZ USA Rev. 0):

* **Sound bank** (WESS module ``SN64``, ROM :data:`BANK_ROM`): a 0x20-byte header (``+0x18``:
  the size of the tables after the patch-group header, ``0x2F088``), a 0x18-byte patch-group header (``+4``
  patches, ``+8`` subpatches, ``+0xC`` waveforms, ``+0x10`` drum maps: u16 count and u16 record
  size each; ``+0x14`` the extra-data size), then the patches (4 bytes), subpatches (20),
  waveforms (24) and drum maps, each padded to 8, then the extra data: an 8-byte header (``+2``
  a count of 16-byte records, ``+4`` the loop count), the loops (0x30 bytes) and one 264-byte
  predictor book per waveform. The driver's module init (``0x80086688``) derives every table
  from these counts and gives waveform *i* the book ``books + 264 * i`` (``0x800868F8``).
* **Event module** (``SSEQ``, ROM :data:`EVENTS_ROM`): a 0x20-byte header (``+0xC`` event count,
  ``+0x18`` the definitions' size), 16-byte definitions (u16 track count, ``+4`` length, ``+8``
  offset from the track base), and the track base right after the definitions.
* **Boot** reads both from ROM through the ``lui``/``addiu`` pairs :data:`BANK_REF` and
  :data:`EVENTS_REF` (``0x800012EC``; no other reference) and allocates them, then every event,
  from the audio heap (``0x80088DF0``, at boot only). The heap has ``0x820`` bytes free after
  boot (owner save state, vanilla, stage 1); :func:`heap_use` gives the ROM-dependent part.

:func:`relocate` writes the enlarged bank and event module at a ROM address and points boot at
them: the stock records as they are in the given ROM (so other owners' edits, e.g. Toasty's
host chain, are kept), the extra chains' records appended, and every event's tracks repacked
after the new definitions (offsets rewritten, lengths unchanged).
"""

from __future__ import annotations

from dataclasses import dataclass, field

BANK_ROM, EVENTS_ROM = 0x947C80, 0x976D40
BANK_REF, EVENTS_REF = 0x00001FFC, 0x00002044  # ROM of the lui/addiu pairs at VA 0x800013FC / 0x80001444
STOCK_REFS = {BANK_REF: (0x3C110094, 0x26317C80), EVENTS_REF: (0x3C130097, 0x26736D40)}
HEAP_FREE = 0x820  # audio heap free after boot, clean ROM (Wiki Sounds-and-Music)
HEAP_MARGIN = 0x100  # kept free
BOOK = 264


def _u16(b: bytes, o: int) -> int:
    return int.from_bytes(b[o : o + 2], "big")


def _u32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o : o + 4], "big")


def _a8(n: int) -> int:
    return (n + 7) & ~7


def _a16(n: int) -> int:
    return (n + 15) & ~15


def module_addresses(rom: bytes) -> tuple[int, int]:
    """The bank's and the event module's ROM addresses, from the boot code."""

    out = []
    for ref in (BANK_REF, EVENTS_REF):
        hi, lo = _u32(rom, ref) & 0xFFFF, _u32(rom, ref + 4) & 0xFFFF
        out.append((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo))
    return out[0], out[1]


@dataclass(frozen=True)
class Bank:
    """A parsed sound bank (offsets relative to its start)."""

    counts: tuple[int, int, int, int]  # patches, subpatches, waveforms, drum maps
    sizes: tuple[int, int, int, int]
    tables: tuple[int, int, int, int]  # where each table starts
    extra: int  # the extra data's start
    extra_size: int
    books: int  # the first predictor book

    @classmethod
    def parse(cls, data: bytes) -> Bank:
        if data[:4] != b"SN64":
            raise ValueError("not a WESS SN64 sound bank")
        counts = tuple(_u16(data, 0x24 + 4 * k) for k in range(4))
        sizes = tuple(_u16(data, 0x26 + 4 * k) for k in range(4))
        at, tables = 0x38, []
        for n, s in zip(counts, sizes, strict=True):
            tables.append(at)
            at = _a8(at + n * s)
        extra_size = _u32(data, 0x34)
        books = at + 8 + 16 * _u16(data, at + 2) + 0x30 * _u16(data, at + 4)
        if books + BOOK * counts[2] != at + extra_size:
            raise ValueError("sound bank: the books do not end the extra data")
        return cls(counts, sizes, tuple(tables), at, extra_size, books)  # type: ignore[arg-type]

    @property
    def end(self) -> int:
        return self.extra + self.extra_size


@dataclass
class Extension:
    """Chains appended to the bank: per chain its track (one, ``0x14``-byte header first) and its
    subpatch, waveform and book records, in chain order (event, patch, subpatch and waveform
    numbers count up from the stock counts)."""

    base: tuple[int, int, int, int]  # first new event, patch, subpatch, waveform
    records: list[tuple[bytes, bytes, bytes, bytes]] = field(default_factory=list)

    def chain(self, k: int):
        from .sound import HostChain

        e, p, s, w = self.base
        return HostChain(e + k, p + k, s + k, w + k)


def extension_for(rom: bytes) -> Extension:
    """An empty extension for the bank and event module ``rom``'s boot code names."""

    bank_at, events_at = module_addresses(rom)
    b = Bank.parse(_bank_bytes(rom, bank_at))
    return Extension((_u32(rom, events_at + 0xC), b.counts[0], b.counts[1], b.counts[2]))


def _bank_bytes(rom: bytes, at: int) -> bytes:
    """The whole bank at ``at``: its header, the patch-group header and everything after it."""

    return bytes(rom[at : at + 0x38 + _u32(rom, at + 0x18)])


def grown_bank(data: bytes, ext: Extension) -> bytes:
    """``data`` with the extension's patches (one subpatch each), subpatches, waveforms and books
    appended to their tables; counts, sizes and the extra-data books updated."""

    b = Bank.parse(data)
    k = len(ext.records)
    if (b.counts[0], b.counts[1], b.counts[2]) != ext.base[1:]:
        raise ValueError("the extension was made for another bank")
    patches = bytearray(data[b.tables[0] : b.tables[0] + 4 * b.counts[0]])
    subs = bytearray(data[b.tables[1] : b.tables[1] + 20 * b.counts[1]])
    waves = bytearray(data[b.tables[2] : b.tables[2] + 24 * b.counts[2]])
    drums = data[b.tables[3] : b.tables[3] + b.counts[3] * b.sizes[3]]
    extra = bytearray(data[b.extra : b.end])
    for i, (_, sub, wave, book) in enumerate(ext.records):
        patches += bytes([1, 0]) + (b.counts[1] + i).to_bytes(2, "big")
        subs += sub[:10] + (b.counts[2] + i).to_bytes(2, "big") + sub[12:20]
        waves += wave
        extra += book
    head = bytearray(data[:0x38])
    counts = (b.counts[0] + k, b.counts[1] + k, b.counts[2] + k, b.counts[3])
    for j, n in enumerate(counts):
        head[0x24 + 4 * j : 0x26 + 4 * j] = n.to_bytes(2, "big")
    head[0x34:0x38] = len(extra).to_bytes(4, "big")
    body = bytearray()
    for table in (patches, subs, waves, drums):
        body += table
        body += bytes(_a8(len(body) + 0x38) - 0x38 - len(body))
    body += extra
    head[0x18:0x1C] = len(body).to_bytes(4, "big")
    out = bytes(head + body)
    if Bank.parse(out).books != Bank.parse(out).extra + (b.books - b.extra):
        raise ValueError("sound bank: the extra data moved inside")
    return out


def events_bytes(rom: bytes, at: int, ext: Extension) -> bytes:
    """The event module at ``at`` with the extension's events appended and every event's tracks
    repacked right after the definitions (16-aligned each)."""

    head = bytearray(rom[at : at + 0x20])
    if head[:4] != b"SSEQ":
        raise ValueError("not a WESS SSEQ event module")
    n = _u32(head, 0xC)
    if n != ext.base[0]:
        raise ValueError("the extension was made for another event module")
    defs_at, base = at + 0x20, at + 0x20 + _u32(head, 0x18)
    defs = [bytearray(rom[defs_at + 16 * i : defs_at + 16 * i + 16]) for i in range(n)]
    tracks = [bytes(rom[base + _u32(d, 8) : base + _u32(d, 8) + _u32(d, 4)]) for d in defs]
    for track, _, _, _ in ext.records:
        defs.append(bytearray((1).to_bytes(2, "big") + bytes(2) + len(track).to_bytes(4, "big") + bytes(8)))
        tracks.append(track)
    blob = bytearray()
    for d, t in zip(defs, tracks, strict=True):
        if len(blob) & 0xF:
            blob += bytes(16 - (len(blob) & 0xF))
        d[8:12] = len(blob).to_bytes(4, "big")
        blob += t
    head[0xC:0x10] = len(defs).to_bytes(4, "big")
    head[0x18:0x1C] = (16 * len(defs)).to_bytes(4, "big")
    return bytes(head) + b"".join(bytes(d) for d in defs) + bytes(blob)


def relocate(rom: bytearray, ext: Extension, at: int, end: int) -> tuple[int, int]:
    """The enlarged bank and event module at ROM ``at`` (16-aligned, below ``end``, free), and
    boot pointed at them. Returns the two modules' new addresses."""

    bank_at, events_at = module_addresses(rom)
    for ref, words in STOCK_REFS.items():
        if (_u32(rom, ref), _u32(rom, ref + 4)) != words:
            raise ValueError(f"boot sound reference at ROM 0x{ref:X} is not stock")
    bank = grown_bank(_bank_bytes(rom, bank_at), ext)
    events = events_bytes(rom, events_at, ext)
    new_bank = at
    new_events = _a16(new_bank + len(bank))
    if new_events + len(events) > end or set(rom[at : new_events + len(events)]) != {0xFF}:
        raise ValueError("sound module region is not free or too small")
    rom[new_bank : new_bank + len(bank)] = bank
    rom[new_events : new_events + len(events)] = events
    for ref, addr in ((BANK_REF, new_bank), (EVENTS_REF, new_events)):
        hi, lo = (addr + 0x8000) >> 16, addr & 0xFFFF
        rom[ref : ref + 4] = ((_u32(rom, ref) & 0xFFFF0000) | hi).to_bytes(4, "big")
        rom[ref + 4 : ref + 8] = ((_u32(rom, ref + 4) & 0xFFFF0000) | lo).to_bytes(4, "big")
    return new_bank, new_events


def heap_use(rom: bytes) -> int:
    """The ROM-dependent part of the audio heap after boot: the bank, the event definitions and
    every event's tracks (``0x800887A8``: 8-aligned 12 bytes per track, plus its length), each
    allocation 16-aligned (``0x80088DF0``). Clean ROM: ``0x6BBD0``."""

    bank_at, events_at = module_addresses(rom)
    bank = _u32(rom, bank_at + 0x18)
    n, defs = _u32(rom, events_at + 0xC), _u32(rom, events_at + 0x18)
    d = events_at + 0x20
    pool = sum(_a8(12 * _u16(rom, d + 16 * i)) + _u32(rom, d + 16 * i + 4) for i in range(n))
    return _a16(bank) + _a16(defs) + _a16(pool)


def check_heap(rom: bytes, clean: bytes) -> int:
    """The audio heap growth over the clean ROM; refuses more than :data:`HEAP_FREE` less
    :data:`HEAP_MARGIN`."""

    grown = heap_use(rom) - heap_use(clean)
    if grown > HEAP_FREE - HEAP_MARGIN:
        raise ValueError(f"audio heap: 0x{grown:X} more than the clean ROM, over the 0x{HEAP_FREE - HEAP_MARGIN:X} budget")
    return grown
