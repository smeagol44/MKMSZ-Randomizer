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
    track: bytes  # 0x20-byte single track; patch number at +0
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
        d = self.defs[event * 16 : event * 16 + 16]
        length, offset = int.from_bytes(d[4:8], "big"), int.from_bytes(d[8:12], "big")
        track = zlib.decompress(self.mkt[MKT_TRACKS_ROM + offset :], -15)[:length]
        if len(track) != 0x20:
            raise ValueError(f"MKT event {event:#x} is not a single 0x20-byte track")
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
    rom: bytearray, clean: bytes, donor: DonorSound, chain: HostChain, sample_rom: int
) -> int:
    """Host ``donor`` in ``chain``; the sample goes at ``sample_rom`` (16-aligned).

    Every rewritten record must still hold its clean bytes. Returns the next free
    16-aligned sample address.
    """

    check_chain(clean, chain)
    if sample_rom & 0xF:
        raise ValueError("sample address must be 16-byte aligned")
    writes = {
        host_track_rom(clean, chain.event): chain.patch.to_bytes(4, "big") + donor.track[4:],
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
