"""Donor (MKT) sounds into isolated MKMSZ sound host chains.

MKT side (USA Rev. 2): the sound bank control file and event definitions are deflated
in ROM; ``ochar_sound(n)`` / ``ft_sound(n)`` resolve through a per-fighter table
``0x800A1ED4[fighter] -> u16 event[n]``. MKMSZ side (USA Rev. 0): an event's track
names a patch -> subpatch -> waveform (+ predictor book); a chain that no stock path can
reach is "isolated" (Wiki ``Sounds-and-Music``, Isolated sound host chains). Hosting a
donor sound rewrites one isolated chain to the donor's track/subpatch/waveform/book and
stores the sample in free ROM; the host event is then played by event number.

Runtime-confirmed for the Sektor teleport sound (event 335, proof v09) and voice set
(v15); this module is the same procedure as a reusable component.
"""

from __future__ import annotations

import hashlib
import zlib
from dataclasses import dataclass

# MKT USA Rev. 2
MKT_CTL_ROM, MKT_CTL_LEN = 0xA8F588, 0x17AE0
MKT_DEFS_ROM, MKT_DEFS_LEN = 0xAA7090, 0x7A6
MKT_TRACKS_ROM = 0xAA7836
MKT_SAMPLES_ROM = 0xAB4370
MKT_FIGHTER_SOUNDS = 0x800A1ED4  # [fighter] -> u16 event table
TRACK_HEADER = 0x14

# MKMSZ USA Rev. 0
MSZ_EVENT_DEFS = 0x976D60  # 16 bytes per event: u16 tracks, length, offset (from MSZ_TRACKS)
MSZ_TRACKS = 0x979240
MSZ_PATCHES = 0x947CB8  # 4 bytes: u8 subpatch count, u8 0, u16 first subpatch
MSZ_SUBPATCHES = 0x948768  # 20 bytes, waveform at +0x0A
MSZ_WAVES = 0x94C138  # 24 bytes, sample offset (from MSZ_TBL) at +0, length at +4
MSZ_BOOKS = 0x950490  # 264 bytes
MSZ_TBL = 0x9B0650


@dataclass(frozen=True)
class HostChain:
    event: int
    patch: int
    subpatch: int
    wave: int


# Clean-ROM audit (Wiki Sounds-and-Music, 2026-11-07). In use by the Sektor proof line:
# 159/164/168/170/171/172 (voice set), 335 (teleport).
ISOLATED_CHAINS = tuple(
    HostChain(*c)
    for c in (
        (159, 316, 159, 149), (164, 321, 164, 154), (168, 325, 168, 158),
        (170, 327, 170, 160), (171, 328, 171, 161), (172, 329, 172, 162),
        (173, 330, 173, 163), (175, 332, 175, 165), (177, 334, 177, 167),
        (332, 489, 332, 322), (335, 492, 335, 325), (336, 493, 336, 326),
        (437, 594, 437, 427), (453, 610, 453, 443), (459, 616, 459, 449),
        (478, 635, 478, 468),
    )
)  # fmt: skip


@dataclass(frozen=True)
class DonorSound:
    event: int
    track: bytes  # one track: 0x14-byte header (patch number at +0), then its stream
    subpatch: bytes  # 20 bytes
    wave: bytes  # 24 bytes
    book: bytes  # 264 bytes
    sample: bytes


class MktSoundBank:
    def __init__(self, mkt: bytes) -> None:
        self.mkt = mkt
        self.ctl = zlib.decompress(mkt[MKT_CTL_ROM : MKT_CTL_ROM + MKT_CTL_LEN], -15)
        self.defs = zlib.decompress(mkt[MKT_DEFS_ROM : MKT_DEFS_ROM + MKT_DEFS_LEN], -15)

    def _u(self, va: int, size: int) -> int:
        return int.from_bytes(self.mkt[va - 0x80000000 : va - 0x80000000 + size], "big")

    def fighter_event(self, fighter: int, index: int) -> int:
        """``ft_sound(index)`` for a fighter: its table entry (event number)."""

        table = self._u(MKT_FIGHTER_SOUNDS + 4 * fighter, 4)
        return self._u(table + 2 * index, 2) & 0x7FFF

    def event(self, event: int) -> DonorSound:
        tracks = self.tracks(event)
        if len(tracks) != 1 or len(tracks[0].track) != 0x20:
            raise ValueError(f"MKT event {event:#x} is not a single 0x20-byte track")
        return tracks[0]

    def tracks(self, event: int) -> list[DonorSound]:
        """Every track of the event (a ``0x14``-byte header, patch first and stream length at
        ``+0x10``, then the stream), each with its patch's records and sample."""

        d = self.defs[event * 16 : event * 16 + 16]
        count = int.from_bytes(d[0:2], "big")
        length, offset = int.from_bytes(d[4:8], "big"), int.from_bytes(d[8:12], "big")
        data = zlib.decompress(self.mkt[MKT_TRACKS_ROM + offset :], -15)[:length]
        out, at = [], 0
        for _ in range(count):
            size = TRACK_HEADER + int.from_bytes(data[at + 0x10 : at + 0x14], "big")
            out.append(self._sound(event, data[at : at + size]))
            at += size
        if not length - 8 < at <= length:  # padding after the last track (event 0x205: 4 bytes)
            raise ValueError(f"MKT event {event:#x}: tracks do not fill its 0x{length:X} bytes")
        return out

    def _sound(self, event: int, track: bytes) -> DonorSound:
        patch = int.from_bytes(track[0:4], "big")
        sub = int.from_bytes(self.ctl[patch * 4 + 2 : patch * 4 + 4], "big")
        subpatch = self.ctl[0x6E0 + sub * 20 : 0x6E0 + sub * 20 + 20]
        wid = int.from_bytes(subpatch[10:12], "big")
        wave = self.ctl[0x2828 + wid * 24 : 0x2828 + wid * 24 + 24]
        book = self.ctl[0x4F48 + wid * 264 : 0x4F48 + wid * 264 + 264]
        start = MKT_SAMPLES_ROM + int.from_bytes(wave[0:4], "big")
        sample = self.mkt[start : start + int.from_bytes(wave[4:8], "big")]
        return DonorSound(event, track, subpatch, wave, book, sample)


def host_track_rom(clean: bytes, event: int) -> int:
    d = MSZ_EVENT_DEFS + event * 16
    if int.from_bytes(clean[d + 4 : d + 8], "big") != 0x20:
        raise ValueError(f"host event {event} is not a single 0x20-byte track")
    return MSZ_TRACKS + int.from_bytes(clean[d + 8 : d + 12], "big")


def check_chain(clean: bytes, chain: HostChain) -> None:
    """The chain's stock links, as audited (track -> patch -> its one subpatch -> wave)."""

    track = host_track_rom(clean, chain.event)
    if int.from_bytes(clean[track : track + 4], "big") != chain.patch:
        raise ValueError(f"host {chain.event}: track patch mismatch")
    p = MSZ_PATCHES + chain.patch * 4
    if clean[p] != 1 or int.from_bytes(clean[p + 2 : p + 4], "big") != chain.subpatch:
        raise ValueError(f"host {chain.event}: patch does not own exactly its subpatch")
    s = MSZ_SUBPATCHES + chain.subpatch * 20
    if int.from_bytes(clean[s + 10 : s + 12], "big") != chain.wave:
        raise ValueError(f"host {chain.event}: subpatch waveform mismatch")


def install(
    rom: bytearray, clean: bytes, donor: DonorSound, chain: HostChain, sample_rom: int, ext=None
) -> int:
    """Host ``donor`` in ``chain``; the sample goes at ``sample_rom`` (16-aligned).

    Every rewritten record must still hold its clean bytes. Returns the next free
    16-aligned sample address. A chain past the stock bank (``ext``, a
    :class:`sound_bank.Extension`) gets its records in the extension, in chain order; they are
    written when the bank is enlarged (:func:`sound_bank.relocate`).
    """

    if ext is not None and chain.event >= ext.base[0]:
        if chain != ext.chain(len(ext.records)):
            raise ValueError(f"extra chain {chain} out of order")
        if sample_rom & 0xF:
            raise ValueError("sample address must be 16-byte aligned")
        if set(rom[sample_rom : sample_rom + len(donor.sample)]) != {0xFF}:
            raise ValueError(f"sample area at {sample_rom:#x} is not free")
        rom[sample_rom : sample_rom + len(donor.sample)] = donor.sample
        wave = (sample_rom - MSZ_TBL).to_bytes(4, "big") + donor.wave[4:]
        ext.records.append((chain.patch.to_bytes(4, "big") + donor.track[4:], donor.subpatch, wave, donor.book))
        return (sample_rom + len(donor.sample) + 0xF) & ~0xF
    check_chain(clean, chain)
    track = host_track_rom(clean, chain.event)
    data = chain.patch.to_bytes(4, "big") + donor.track[4:]
    if bytes(rom[track : track + len(data)]) != clean[track : track + len(data)]:
        raise ValueError(f"host {chain.event}: record at {track:#x} already modified")
    rom[track : track + len(data)] = data
    return _install_records(rom, clean, donor, chain, sample_rom)


def _install_records(rom: bytearray, clean: bytes, donor: DonorSound, chain: HostChain, sample_rom: int) -> int:
    """The chain's subpatch, waveform and book records, and the sample."""

    if sample_rom & 0xF:
        raise ValueError("sample address must be 16-byte aligned")
    writes = {
        MSZ_SUBPATCHES + chain.subpatch * 20: donor.subpatch[:10]
        + chain.wave.to_bytes(2, "big")
        + donor.subpatch[12:],
        MSZ_WAVES + chain.wave * 24: (sample_rom - MSZ_TBL).to_bytes(4, "big") + donor.wave[4:],
        MSZ_BOOKS + chain.wave * 264: donor.book,
    }
    for off, data in writes.items():
        if bytes(rom[off : off + len(data)]) != clean[off : off + len(data)]:
            raise ValueError(f"host {chain.event}: record at {off:#x} already modified")
        rom[off : off + len(data)] = data
    if set(rom[sample_rom : sample_rom + len(donor.sample)]) != {0xFF}:
        raise ValueError(f"sample area at {sample_rom:#x} is not free")
    rom[sample_rom : sample_rom + len(donor.sample)] = donor.sample
    return (sample_rom + len(donor.sample) + 0xF) & ~0xF


def sample_digest(donor: DonorSound) -> str:
    return hashlib.sha256(donor.sample).hexdigest()


# WESS sequence streams (MKT and MKMSZ share the format; Wiki Sounds-and-Music): each event is a
# MIDI-style variable-length delta, then an opcode and its arguments. Only the opcodes SFX
# tracks use are known here; any other refuses the port.
WESS_ARGS = {0x07: 2, 0x0C: 1, 0x0D: 1, 0x11: 2, 0x12: 1, 0x22: 0, 0x23: 0}
WESS_PATCH, WESS_NOTE_ON, WESS_END = 0x07, 0x11, 0x22  # patch change: little-endian u16


def retarget(track: bytes, patch: int) -> bytes:
    """``track`` playing host ``patch``: its header patch and every in-stream patch change. The
    notes must all play the header's patch (one sample per track)."""

    own = int.from_bytes(track[0:4], "big")
    end = TRACK_HEADER + int.from_bytes(track[0x10:0x14], "big")
    out = bytearray(patch.to_bytes(4, "big") + track[4:end])
    pos, current, played = TRACK_HEADER, own, set()
    while True:
        while track[pos] & 0x80:  # delta time
            pos += 1
        pos += 1
        op = track[pos]
        if op not in WESS_ARGS:
            raise ValueError(f"WESS opcode {op:#x} at +{pos:#x} is not supported")
        if op == WESS_PATCH:
            current = int.from_bytes(track[pos + 1 : pos + 3], "little")
            out[pos + 1 : pos + 3] = patch.to_bytes(2, "little")
        elif op == WESS_NOTE_ON:
            played.add(current)
        pos += 1 + WESS_ARGS[op]
        if op == WESS_END:
            break
        if pos >= end:
            raise ValueError("WESS stream has no end")
    if played - {own}:
        raise ValueError(f"track notes play patches {sorted(played)}, not only its own {own}")
    return bytes(out)


def install_tracks(rom: bytearray, clean: bytes, tracks: list[DonorSound], chains: tuple[HostChain, ...],
                   sample_rom: int) -> tuple[int, int]:  # fmt: skip
    """Host a multi-track donor event: each track in its own chain (records and sample as
    :func:`install`), the retargeted tracks together after the samples, and the first chain's
    event definition pointed at them (track count, length, offset from :data:`MSZ_TRACKS`). The
    sequence loader reads every event from ROM by that offset into a pool sized from the
    lengths (Static-confirmed: ``0x800880EC``, ``0x80088B10``). Returns the event to play and
    the next free 16-aligned address."""

    if len(chains) != len(tracks):
        raise ValueError("one chain per track")
    data = b""
    for donor, chain in zip(tracks, chains, strict=True):
        check_chain(clean, chain)
        sample_rom = _install_records(rom, clean, donor, chain, sample_rom)
        data += retarget(donor.track, chain.patch)
    if set(rom[sample_rom : sample_rom + len(data)]) != {0xFF}:
        raise ValueError(f"track area at {sample_rom:#x} is not free")
    rom[sample_rom : sample_rom + len(data)] = data
    d = MSZ_EVENT_DEFS + chains[0].event * 16
    if bytes(rom[d : d + 16]) != clean[d : d + 16]:
        raise ValueError(f"event {chains[0].event} definition already modified")
    rom[d : d + 2] = len(tracks).to_bytes(2, "big")
    rom[d + 4 : d + 8] = len(data).to_bytes(4, "big")
    rom[d + 8 : d + 12] = (sample_rom - MSZ_TRACKS).to_bytes(4, "big")
    return chains[0].event, (sample_rom + len(data) + 0xF) & ~0xF
