"""Native inventory randomizer HUD and key portraits.

This production patch promotes the Runtime-confirmed v20/v21 presentation architecture:

* stage-local key/icon/crystal IDs remain masked in LIVE inventory outside their
  origin stage, while text and portrait presentation resolves the authoritative
  four-box backing identity;
* one shared 36x48 CI8 portrait slot is registered through common image package
  file 0x5D, and the selected portrait is synchronously streamed from ROM;
* the selected-item paper shows the native retail title plus an eight-stage
  ``STG CHECKS KEYS`` table;
* the inventory XP panel keeps its stock EXPERIENCE POINTS row and replaces the
  second row with the configured requirement plus right-aligned ``CHKS ZZ-85``;
* large read-only tables/palettes are stored in generated-output ROM and lazily
  DMA-loaded into one bounded 0x1200-byte arena allocation per stage lifecycle.

The 21 portrait payloads and private font palettes are derived from the user's
clean ROM at build time. No ROM-derived binary asset is stored in the repo.
"""

from __future__ import annotations

import struct

from ..data.addresses import FILE_TABLE_ENTRY_SIZE, FILE_TABLE_ROM
from ..errors import PatchError
from ..mips import (
    Emitter,
    addiu,
    address_words,
    addu,
    and_,
    andi,
    jal,
    jr,
    jump,
    lbu,
    lui,
    lw,
    or_,
    sb,
    sll,
    sllv,
    sltiu,
    srl,
    sltu,
    subu,
    sw,
    words_blob,
)
from ..resource_materialization import (
    GLOBAL_OUTPUT_SIZE,
    GLOBAL_RESOURCE_REGION_END,
    decompress_resource_package,
)
from ..rom import RomImage
from .base import PatchContext
from .global_materialization import MATERIALIZER_HELPER_END_K0, MATERIALIZER_HELPER_END_ROM
from .inventory_boxes import BOX0_VA
from .native_payload import kseg1_alias
from .required_powers import VANILLA_XP_REQUIREMENT, resolve_required_powers
from .temple_special_check import EXPANSION_FILE_ENTRY_ROM
from .toasty_constants import TOASTY_AUDIO_ROM

NOP = 0

# Production shared-file tail. The global materializer ends exactly here and
# Toasty's fixed donor-audio allocation begins exactly 0x500 bytes later.
HUD_CODE_ROM = MATERIALIZER_HELPER_END_ROM
HUD_CODE_K0 = MATERIALIZER_HELPER_END_K0
HUD_CODE_K1 = kseg1_alias(HUD_CODE_K0)
HUD_CODE_SIZE = 0x500
HUD_CODE_END_ROM = HUD_CODE_ROM + HUD_CODE_SIZE
HUD_CODE_END_K0 = HUD_CODE_K0 + HUD_CODE_SIZE
HUD_STATE_DATA_PTR_OFF = 0x4F0
HUD_STATE_PREVIEW_CACHE_OFF = 0x4F4
HUD_STATE_DATA_PTR_K1 = HUD_CODE_K1 + HUD_STATE_DATA_PTR_OFF
HUD_STATE_PREVIEW_CACHE_K1 = HUD_CODE_K1 + HUD_STATE_PREVIEW_CACHE_OFF

if HUD_CODE_END_ROM != TOASTY_AUDIO_ROM:
    raise AssertionError("inventory HUD must fill the materializer-to-audio 0x500-byte tail")

# Generated-output ownership begins immediately after the eight 1 MiB global
# stage-resource slots. These regions are explicit, bounded, and non-overlapping.
PORTRAIT_ATLAS_ROM = GLOBAL_RESOURCE_REGION_END
PORTRAIT_BYTES = 0x6C0
PORTRAIT_COUNT = 21
PORTRAIT_ATLAS_SIZE = PORTRAIT_BYTES * PORTRAIT_COUNT
COMMON_PACKAGE_ROM = 0x01809000
COMMON_PACKAGE_CAPACITY = 0xB000
HUD_DATA_ROM = 0x01814000
HUD_DATA_SIZE = 0x1200
HUD_DATA_END_ROM = HUD_DATA_ROM + HUD_DATA_SIZE

if PORTRAIT_ATLAS_ROM != 0x01800000:
    raise AssertionError("global resource region end drifted")
if PORTRAIT_ATLAS_ROM + PORTRAIT_ATLAS_SIZE > COMMON_PACKAGE_ROM:
    raise AssertionError("portrait atlas overlaps common package allocation")
if COMMON_PACKAGE_ROM + COMMON_PACKAGE_CAPACITY != HUD_DATA_ROM:
    raise AssertionError("common image package capacity must end at HUD data")
if HUD_DATA_END_ROM > GLOBAL_OUTPUT_SIZE:
    raise AssertionError("inventory HUD generated-output allocations exceed 32 MiB")

# Permanent inventory presentation hooks / retired description-renderer region.
ROW_HOOK_ROM = 0x00074E68
ROW_HOOK_VA = 0x80074268
PREVIEW_HOOK_ROM = 0x00073C98
PREVIEW_HOOK_VA = 0x80073098
SECOND_LABEL_DRAW_ROM = 0x000759E0
SECOND_VALUE_DRAW_ROM = 0x00075B88
RETIRED_START_ROM = 0x00074EB8
RETIRED_END_ROM = 0x00074FA8
RETIRED_START_VA = 0x800742B8
RETIRED_END_VA = 0x800743A8
DETAIL_TRAMP_VA = 0x800742B8
SHARED_TRAMP_VA = 0x800742C8
ENSURE_DATA_VA = 0x800742D8

EXPECTED_ROW_HOOK = 0x0C01CF9D  # jal 0x80073E74
EXPECTED_PREVIEW_HOOK = 0x0C01CF3B  # jal 0x80073CEC
EXPECTED_SECOND_TEXT_DRAW = 0x0C01CF9D
EXPECTED_RETIRED_REGION = bytes.fromhex(
    "27bdffd0afb1001c2411001500001821afb40028241400ebafbf002cafb30024"
    "afb2002014a0000bafb00018000410803c01800a002208218c22600c00021080"
    "3c04800a008220218c846a740801d0c824130001000410803c04800a00822021"
    "8c846ca0241300013c12800b26521e4400031080004480218e02000014530003"
    "0000000026310004261000048e0400000c01d02124050002afb200108e040000"
    "00022fc200a22821000528430285282326100004022030210c01cf9d24070002"
    "8e0200001440ffed2631000b8fbf002c8fb400288fb300248fb200208fb1001c"
    "8fb0001827bd003003e0000800000000"
)

# Native functions/data used by the accepted v13 helper set.
ARENA_ALLOC_VA = 0x8006643C
ARENA_CURSOR_VA = 0x80111ECC
ROM_DMA_VA = 0x80001530
TEXT_DRAW_VA = 0x80073E74
TEXT_WIDTH_VA = 0x80074084
PAPER_FONT_VA = 0x800B1E44
LIST_FONT_VA = 0x800B1E20
LIST_FONT_ROM = 0x000B2A20
POWER_COUNT_VA = 0x800C1248
CURRENT_STAGE_VA = 0x8009A910
RENDER_VA = 0x80073CEC
STATE_UNCACHED_VA = 0xA01AF7D0
STATE_FLAGS_OFFSET = 0x10
PICKUP_BITS_OFFSET = 0x20

# One shared portrait slot registered in common permanent-image file 0x5D.
COMMON_PACKAGE_ID = 0x5D
CUSTOM_SPRITE_ID = 0x46C
CUSTOM_BACKING_PTR_VA = 0x800ED940 + CUSTOM_SPRITE_ID * 4
ITEM_FIRST = 0x0E
ITEM_COUNT = 21

# Native key/icon/crystal preview records. Payloads are copied from these stock
# compressed image packages; only the common carrier record gets a new sprite ID.
PORTRAIT_DONORS = (
    (0x7E, (0x3AC, 0x3AD, 0x3AE)),  # Wind 0E..10
    (0x34, (0x3AE, 0x3AC, 0x3AD)),  # Earth 11..13
    (0x73, (0x3AE, 0x3AD, 0x3AC)),  # Water 14..16
    (0x39, (0x3AC, 0x3AD, 0x3AE)),  # Fire 17..19
    (0x4D, (0x3AC, 0x3AD, 0x3AE)),  # Prison 1A..1C
    (0x2B, (0x3AE, 0x3AD, 0x3AC)),  # Bridge 1D..1F
    (0x6E, (0x3AE, 0x3AF, 0x3AD)),  # Crystals 20..22
)

LABELS = tuple(
    f"{group}{index}"
    for group in ("WIND", "EARTH", "WATER", "FIRE", "PRISON", "BRIDGE", "CRYS")
    for index in (1, 2, 3)
)
TITLES = (
    "WIND ICON",
    "WIND ICON",
    "WIND ICON",
    "EARTH ICON",
    "EARTH ICON",
    "EARTH ICON",
    "WATER ICON",
    "WATER ICON",
    "WATER ICON",
    "FIRE ICON",
    "FIRE ICON",
    "FIRE ICON",
    "LEVEL 1 KEY",
    "LEVEL 2 KEY",
    "LEVEL 3 KEY",
    "FORTRESS ICON",
    "FORTRESS ICON",
    "FORTRESS ICON",
    "JATAAKA'S CRYSTAL",
    "KIA'S CRYSTAL",
    "SAREENA'S CRYSTAL",
)

# abbr, MKSV ordinary-pickup word offset, total checks, key-bit shift, Temple extra flag.
STAGE_ROWS = (
    ("TEM", 0x24, 5, -1, 1),
    ("WND", 0x28, 6, 0, 0),
    ("WTR", 0x2C, 9, 6, 0),
    ("ERT", 0x30, 20, 3, 0),
    ("FIR", 0x20, 16, 9, 0),
    ("PRS", 0x34, 10, 12, 0),
    ("BRG", 0x38, 10, 15, 0),
    ("FOR", 0x3C, 9, 18, 0),
)

# User-approved screen-space colors. The first five use the exact Static-confirmed
# 15-bit BGR source encoding from v08. Bridge intentionally reproduces the v06
# descriptor bytes whose resulting purple was accepted; crystals reproduce the
# accepted v04/v05 lime source words.
PALETTE_TARGETS = (
    (170, 220, 255),
    (255, 225, 70),
    (65, 120, 255),
    (255, 85, 25),
    (85, 220, 100),
)
BRIDGE_V06_TARGET = (255, 185, 100)
CRYSTAL_SOURCE_WORDS = (
    0x0000,
    0x4F53,
    0x4F13,
    0x4F53,
    0x4F13,
    0x46D1,
    0x3E51,
    0x3611,
    0x3206,
    0x29C4,
    0x2184,
    0x2144,
    0x1902,
    0x10C2,
    0x0882,
    0x0082,
)
FONT_DESCRIPTOR_SIZE = 516


def _align(value: int, alignment: int = 16) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _be32(data: bytes | bytearray, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def _put32(data: bytearray, offset: int, value: int) -> None:
    data[offset : offset + 4] = (value & 0xFFFFFFFF).to_bytes(4, "big")


def _move(rd: str, rs: str) -> int:
    return addu(rd, rs, "zero")


def _srlv(rd: str, rt: str, rs: str) -> int:
    registers = {
        "zero": 0,
        "v0": 2,
        "v1": 3,
        "a0": 4,
        "a1": 5,
        "a2": 6,
        "a3": 7,
        "t0": 8,
        "t1": 9,
        "t2": 10,
        "t3": 11,
        "t4": 12,
        "t5": 13,
        "t6": 14,
        "t7": 15,
        "s0": 16,
        "s1": 17,
        "s2": 18,
        "s3": 19,
        "s4": 20,
        "s5": 21,
        "t8": 24,
        "t9": 25,
        "sp": 29,
        "ra": 31,
    }
    return (
        (registers[rs] << 21)
        | (registers[rt] << 16)
        | (registers[rd] << 11)
        | 0x06
    )


def _divu(rs: str, rt: str) -> int:
    registers = {"t3": 11, "t4": 12, "t7": 15}
    return (registers[rs] << 21) | (registers[rt] << 16) | 0x1B


def _mflo(rd: str) -> int:
    registers = {"v1": 3, "t8": 24}
    return (registers[rd] << 11) | 0x12


def _mfhi(rd: str) -> int:
    registers = {"t9": 25}
    return (registers[rd] << 11) | 0x10


def _trampoline(target: int) -> bytes:
    return words_blob([*address_words("t9", target), jr("t9"), NOP])


def _image_records(package: bytes) -> tuple[dict[int, bytes], int]:
    if len(package) < 8:
        raise PatchError("permanent-image package is too small")
    cursor = 8
    records: dict[int, bytes] = {}
    count = _be32(package, 0)
    for _ in range(count):
        if cursor + 12 > len(package):
            raise PatchError("permanent-image package has a truncated record header")
        flags, width_word, height, sprite_id, _unused = struct.unpack_from(
            ">IHhHH", package, cursor
        )
        if height < 0:
            raise PatchError("permanent-image package has a negative image height")
        stride = (width_word & 0xFF) or 256
        if flags & 0x80000000:
            stride //= 2
        end = _align(cursor + 12 + stride * height, 4)
        if end > len(package):
            raise PatchError("permanent-image package record overruns decoded file")
        if sprite_id in records:
            raise PatchError(f"duplicate permanent-image sprite 0x{sprite_id:X}")
        records[sprite_id] = bytes(package[cursor:end])
        cursor = end
    return records, cursor


def _package_raw(rom: RomImage, file_id: int) -> tuple[bytes, int, int]:
    entry = FILE_TABLE_ROM + file_id * FILE_TABLE_ENTRY_SIZE
    start = rom.read_u32(entry)
    end = rom.read_u32(entry + 4)
    flag = rom.read_u32(entry + 8)
    if flag != 1:
        raise PatchError(f"file 0x{file_id:02X} is not a compressed image package")
    if not 0 <= start < end <= len(rom.data):
        raise PatchError(f"file 0x{file_id:02X} has invalid ROM bounds")
    return decompress_resource_package(bytes(rom.data[start:end])), start, end


def _lzw_codes(raw: bytes) -> list[int]:
    clear = 0x100
    end = 0x101
    maximum = 1 << 12
    table = {bytes((index,)): index for index in range(256)}
    next_code = 0x102
    codes = [clear]
    current = b""
    for value in raw:
        char = bytes((value,))
        if not current:
            current = char
            continue
        joined = current + char
        if joined in table:
            current = joined
            continue
        codes.append(table[current])
        if next_code < maximum:
            table[joined] = next_code
            next_code += 1
        else:
            codes.append(clear)
            table = {bytes((index,)): index for index in range(256)}
            next_code = 0x102
        current = char
    if current:
        codes.append(table[current])
    codes.append(end)
    return codes


def _compress_resource_package(raw: bytes) -> bytes:
    bits = 9
    next_code = 0x102
    have_previous = False
    accumulator = 0
    pending = 0
    output = bytearray(len(raw).to_bytes(4, "big"))
    for code in _lzw_codes(raw):
        if code >= 1 << bits:
            raise PatchError(f"LZW code 0x{code:X} does not fit {bits} bits")
        accumulator = (accumulator << bits) | code
        pending += bits
        while pending >= 8:
            pending -= 8
            output.append((accumulator >> pending) & 0xFF)
            accumulator &= (1 << pending) - 1 if pending else 0
        if code == 0x100:
            bits = 9
            next_code = 0x102
            have_previous = False
        elif code == 0x101:
            pass
        elif not have_previous:
            have_previous = True
        else:
            next_code += 1
            if next_code == (1 << bits) - 1 and bits < 12:
                bits += 1
    if pending:
        output.append((accumulator << (8 - pending)) & 0xFF)
    packed = bytes(output)
    if decompress_resource_package(packed) != raw:
        raise PatchError("recompressed permanent-image package failed exact round trip")
    return packed


def _append_image_record(raw: bytes, record: bytes) -> bytes:
    records, image_end = _image_records(raw)
    sprite_id = int.from_bytes(record[8:10], "big")
    if sprite_id in records:
        raise PatchError(f"file 0x{COMMON_PACKAGE_ID:02X} already owns sprite 0x{sprite_id:X}")
    output = bytearray(raw[:image_end] + record + raw[image_end:])
    _put32(output, 0, _be32(raw, 0) + 1)
    parsed, new_end = _image_records(bytes(output))
    if parsed[sprite_id] != record:
        raise AssertionError("appended common portrait record changed")
    if output[new_end:] != raw[image_end:]:
        raise AssertionError("common image-package palette/tail moved")
    return bytes(output)


def _native_palette(stock: bytes, target: tuple[int, int, int]) -> bytes:
    if len(stock) != FONT_DESCRIPTOR_SIZE or _be32(stock, 0) != 0x10:
        raise PatchError("stock inventory list-font descriptor guard failed")
    tr, tg, tb = (round(component * 31 / 255) for component in target)
    output = bytearray(stock)
    for index in range(256):
        offset = 4 + index * 2
        source = int.from_bytes(stock[offset : offset + 2], "big")
        if source == 0:
            output[offset : offset + 2] = b"\0\0"
            continue
        sr = source & 0x1F
        sg = (source >> 5) & 0x1F
        sb = (source >> 10) & 0x1F
        level = max(sr, sg, sb) / 31.0
        rr = round(tr * level)
        gg = round(tg * level)
        bb = round(tb * level)
        if rr == 0 and gg == 0 and bb == 0:
            target5 = (tr, tg, tb)
            strongest = max(range(3), key=lambda item: target5[item])
            components = [0, 0, 0]
            components[strongest] = 1
            rr, gg, bb = components
        output[offset : offset + 2] = ((bb << 10) | (gg << 5) | rr).to_bytes(2, "big")
    return bytes(output)


def _accepted_bridge_palette(stock: bytes) -> bytes:
    tr, tg, tb = (round(component * 31 / 255) for component in BRIDGE_V06_TARGET)
    output = bytearray(stock)
    for index in range(16):
        offset = 4 + index * 2
        source = int.from_bytes(stock[offset : offset + 2], "big")
        red = (source >> 11) & 0x1F
        green = (source >> 6) & 0x1F
        blue = (source >> 1) & 0x1F
        level = max(red, green, blue) / 31.0
        rr = round(tr * level)
        gg = round(tg * level)
        bb = round(tb * level)
        output[offset : offset + 2] = (
            (rr << 11) | (gg << 6) | (bb << 1) | (source & 1)
        ).to_bytes(2, "big")
    return bytes(output)


def _accepted_crystal_palette(stock: bytes) -> bytes:
    output = bytearray(stock)
    for index, word in enumerate(CRYSTAL_SOURCE_WORDS):
        offset = 4 + index * 2
        output[offset : offset + 2] = word.to_bytes(2, "big")
    return bytes(output)


def _build_hud_data(rom: RomImage, *, required_count: int | None) -> tuple[bytes, dict[str, int]]:
    stock = bytes(rom.data[LIST_FONT_ROM : LIST_FONT_ROM + FONT_DESCRIPTOR_SIZE])
    palettes = [
        *(_native_palette(stock, target) for target in PALETTE_TARGETS),
        _accepted_bridge_palette(stock),
        _accepted_crystal_palette(stock),
    ]

    data = bytearray(HUD_DATA_SIZE)
    cursor = 0
    for descriptor in palettes:
        data[cursor : cursor + len(descriptor)] = descriptor
        cursor += len(descriptor)
    cursor = _align(cursor)

    label_ptrs = cursor
    cursor += ITEM_COUNT * 4
    font_ptrs = cursor
    cursor += ITEM_COUNT * 4
    title_ptrs = cursor
    cursor += ITEM_COUNT * 4
    cursor = _align(cursor)

    label_offsets: list[int] = []
    for label in LABELS:
        offset = cursor
        blob = label.encode("ascii") + b"\0"
        data[offset : offset + 8] = blob + bytes(8 - len(blob))
        cursor += 8
        label_offsets.append(offset)

    title_cache: dict[str, int] = {}
    title_offsets: list[int] = []
    for title in TITLES:
        if title not in title_cache:
            title_cache[title] = cursor
            blob = title.encode("ascii") + b"\0"
            data[cursor : cursor + len(blob)] = blob
            cursor += len(blob)
        title_offsets.append(title_cache[title])

    cursor = _align(cursor, 4)
    header = cursor
    data[cursor : cursor + 16] = b"STG CHECKS KEYS\0"
    cursor += 16
    meta = cursor
    cursor += len(STAGE_ROWS) * 16
    rows = cursor
    cursor += len(STAGE_ROWS) * 16

    for index, (abbr, state_offset, total, key_shift, extra) in enumerate(STAGE_ROWS):
        row_offset = rows + index * 16
        suffix = "---" if key_shift < 0 else "0-3"
        line = f"{abbr} 00-{total:02d} {suffix}".encode("ascii") + b"\0"
        data[row_offset : row_offset + 16] = line + bytes(16 - len(line))
        meta_offset = meta + index * 16
        _put32(data, meta_offset, row_offset)
        _put32(data, meta_offset + 4, state_offset)
        _put32(data, meta_offset + 8, 0xFFFFFFFF if key_shift < 0 else key_shift)
        _put32(data, meta_offset + 12, extra)

    requirement = cursor
    if required_count is None:
        requirement_text = f"REQUIRED XP {VANILLA_XP_REQUIREMENT}\0".encode("ascii")
        requirement_exact = 0
    else:
        requirement_text = f"REQUIRED POWERS 0/{required_count}\0".encode("ascii")
        requirement_exact = 1
    if len(requirement_text) > 0x18:
        raise AssertionError("native requirement HUD text exceeds fixed slot")
    data[cursor : cursor + len(requirement_text)] = requirement_text
    cursor += 0x18

    check = cursor
    data[cursor : cursor + len(b"00/85\0")] = b"00/85\0"
    cursor += 0x18

    for index, offset in enumerate(label_offsets):
        _put32(data, label_ptrs + index * 4, offset)
    for index in range(ITEM_COUNT):
        _put32(data, font_ptrs + index * 4, (index // 3) * FONT_DESCRIPTOR_SIZE)
    for index, offset in enumerate(title_offsets):
        _put32(data, title_ptrs + index * 4, offset)

    if cursor > HUD_DATA_SIZE:
        raise AssertionError("native inventory HUD data exceeds fixed 0x1200-byte slot")
    return bytes(data), {
        "label_ptrs": label_ptrs,
        "font_ptrs": font_ptrs,
        "title_ptrs": title_ptrs,
        "header": header,
        "meta": meta,
        "rows": rows,
        "requirement": requirement,
        "requirement_exact": requirement_exact,
        "check": check,
        "used": cursor,
    }


def _ensure_data_code() -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x18),
        sw("ra", 0x14, "sp"),
        sw("s0", 0x10, "sp"),
        *address_words("t0", HUD_STATE_DATA_PTR_K1),
        lw("s0", 0, "t0"),
    )
    e.beq("s0", "zero", "load")
    e.emit(NOP)
    e.emit(
        *address_words("t1", ARENA_CURSOR_VA),
        lw("t1", 0, "t1"),
        addiu("t2", "s0", HUD_DATA_SIZE),
        sltu("t2", "t1", "t2"),
    )
    e.beq("t2", "zero", "ready")
    e.emit(NOP)
    e.label("load")
    e.emit(
        addiu("a0", "zero", HUD_DATA_SIZE),
        jal(ARENA_ALLOC_VA),
        NOP,
        _move("s0", "v0"),
        *address_words("a0", HUD_DATA_ROM),
        _move("a1", "s0"),
        addiu("a2", "zero", HUD_DATA_SIZE),
        addiu("a3", "zero", 2),
        jal(ROM_DMA_VA),
        NOP,
        *address_words("t0", HUD_STATE_DATA_PTR_K1),
        sw("s0", 0, "t0"),
    )
    e.label("ready")
    e.emit(
        lui("t0", 0x2000),
        or_("v0", "s0", "t0"),
        lw("s0", 0x10, "sp"),
        lw("ra", 0x14, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x18),
    )
    return e.finish()


def _resolve_code() -> bytes:
    e = Emitter()
    e.emit(
        lui("t1", 0x800A),
        sll("t0", "a0", 2),
        addu("t3", "t1", "t0"),
        lw("v0", 0x600C, "t3"),
        addiu("t2", "zero", 8),
    )
    e.bne("v0", "t2", "done")
    e.emit(NOP)
    e.emit(
        lbu("t2", 0x60EB, "t1"),
        andi("t2", "t2", 3),
        sll("t3", "t2", 5),
        sll("t2", "t2", 3),
        addu("t2", "t2", "t3"),
        addu("t2", "t2", "t0"),
        addu("t2", "t2", "t1"),
        lw("v0", 0x6048, "t2"),
    )
    e.label("done")
    e.emit(jr("ra"), NOP)
    return e.finish()


def _row_code(resolve_va: int, data_layout: dict[str, int]) -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x30),
        sw("ra", 0x2C, "sp"),
        sw("a0", 0x20, "sp"),
        sw("a1", 0x24, "sp"),
        sw("a2", 0x28, "sp"),
        jal(ENSURE_DATA_VA),
        NOP,
        sw("v0", 0x14, "sp"),
        jal(resolve_va),
        _move("a0", "s1"),
        addiu("t0", "v0", -ITEM_FIRST),
        sltiu("t1", "t0", ITEM_COUNT),
    )
    e.beq("t1", "zero", "ordinary")
    e.emit(sll("t0", "t0", 2))
    e.emit(
        lw("t2", 0x14, "sp"),
        addiu("t1", "t2", data_layout["label_ptrs"]),
        addu("t1", "t1", "t0"),
        lw("t1", 0, "t1"),
        addu("a0", "t2", "t1"),
        addiu("t1", "t2", data_layout["font_ptrs"]),
        addu("t1", "t1", "t0"),
        lw("t1", 0, "t1"),
        addu("t1", "t2", "t1"),
        sw("t1", 0x10, "sp"),
    )
    e.beq("zero", "zero", "draw")
    e.emit(NOP)
    e.label("ordinary")
    # Preserve the native caller's fifth stack argument (font/palette pointer).
    # After this helper's -0x30 frame, old sp+0x10 is new sp+0x40.
    e.emit(lw("t1", 0x40, "sp"), sw("t1", 0x10, "sp"), lw("a0", 0x20, "sp"))
    e.label("draw")
    e.emit(
        lw("a1", 0x24, "sp"),
        lw("a2", 0x28, "sp"),
        jal(TEXT_DRAW_VA),        addiu("a3", "zero", 2),
        lw("ra", 0x2C, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x30),
    )
    return e.finish()


def _preview_code(resolve_va: int) -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x30),
        sw("ra", 0x2C, "sp"),
        sw("a0", 0x20, "sp"),
        sw("a1", 0x24, "sp"),
        sw("a3", 0x28, "sp"),
        sw("zero", 0x10, "sp"),
        jal(resolve_va),
        _move("a0", "s2"),
        addiu("t0", "v0", -ITEM_FIRST),
        sltiu("t1", "t0", ITEM_COUNT),
    )
    e.beq("t1", "zero", "ordinary")
    e.emit(NOP)
    e.emit(
        *address_words("t2", CURRENT_STAGE_VA),
        lw("t2", 0, "t2"),
        sll("t2", "t2", 5),
        addu("t2", "t2", "t0"),
        *address_words("t3", CUSTOM_BACKING_PTR_VA),
        lw("t3", 0, "t3"),
    )
    e.beq("t3", "zero", "ordinary")
    e.emit(NOP)
    e.emit(*address_words("t4", HUD_STATE_PREVIEW_CACHE_K1), lw("t5", 0, "t4"))
    e.beq("t5", "t2", "ready")
    e.emit(NOP)
    e.emit(
        sw("t2", 0, "t4"),
        sll("t5", "t0", 10),
        sll("t1", "t0", 9),
        addu("t5", "t5", "t1"),
        sll("t1", "t0", 7),
        addu("t5", "t5", "t1"),
        sll("t1", "t0", 6),
        addu("t5", "t5", "t1"),
        lui("a0", (PORTRAIT_ATLAS_ROM >> 16) & 0xFFFF),
        addu("a0", "a0", "t5"),
        _move("a1", "t3"),
        addiu("a2", "zero", PORTRAIT_BYTES),
        addiu("a3", "zero", 2),
        jal(ROM_DMA_VA),
        NOP,
    )
    e.label("ready")
    e.emit(addiu("a1", "zero", CUSTOM_SPRITE_ID))
    e.beq("zero", "zero", "draw")
    e.emit(NOP)
    e.label("ordinary")
    e.emit(lw("a1", 0x24, "sp"))
    e.label("draw")
    e.emit(
        lw("a0", 0x20, "sp"),
        addiu("a2", "zero", 109),
        lw("a3", 0x28, "sp"),
        jal(RENDER_VA),
        NOP,
        lw("ra", 0x2C, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x30),
    )
    return e.finish()


def _paper_code(resolve_va: int, data_layout: dict[str, int]) -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x60),
        sw("ra", 0x5C, "sp"),
        sw("s0", 0x58, "sp"),
        sw("s1", 0x54, "sp"),
        sw("s2", 0x50, "sp"),
        sw("s3", 0x4C, "sp"),
        sw("s4", 0x48, "sp"),
        sw("s5", 0x44, "sp"),
        jal(ENSURE_DATA_VA),
        NOP,
        sw("v0", 0x24, "sp"),
        jal(resolve_va),
        _move("a0", "s2"),
        addiu("t0", "v0", -ITEM_FIRST),
        sltiu("t1", "t0", ITEM_COUNT),
    )
    e.beq("t1", "zero", "after_title")
    e.emit(sll("t0", "t0", 2))
    e.emit(
        lw("t2", 0x24, "sp"),
        addiu("t1", "t2", data_layout["title_ptrs"]),
        addu("t1", "t1", "t0"),
        lw("t1", 0, "t1"),
        addu("a0", "t2", "t1"),
        sw("a0", 0x20, "sp"),
        jal(TEXT_WIDTH_VA),
        addiu("a1", "zero", 2),
        srl("t0", "v0", 1),
        addiu("t1", "zero", 235),
        subu("a1", "t1", "t0"),
        lw("a0", 0x20, "sp"),
        addiu("a2", "zero", 21),
        addiu("a3", "zero", 2),
        *address_words("t0", PAPER_FONT_VA),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
    )
    e.label("after_title")

    e.emit(*address_words("s0", BOX0_VA), addiu("s1", "zero", 40), _move("s2", "zero"))
    e.label("key_scan")
    e.emit(
        lw("t0", 0, "s0"),
        addiu("t1", "t0", -ITEM_FIRST),
        sltiu("t2", "t1", ITEM_COUNT),
    )
    e.beq("t2", "zero", "key_next")
    e.emit(addiu("t2", "zero", 1))
    e.emit(sllv("t2", "t2", "t1"), or_("s2", "s2", "t2"))
    e.label("key_next")
    e.emit(addiu("s0", "s0", 4), addiu("s1", "s1", -1))
    e.bne("s1", "zero", "key_scan")
    e.emit(NOP)

    e.emit(
        lw("t2", 0x24, "sp"),
        addiu("a0", "t2", data_layout["header"]),
        addiu("a1", "zero", 170),
        addiu("a2", "zero", 43),
        addiu("a3", "zero", 1),
        *address_words("t0", PAPER_FONT_VA),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
    )

    e.emit(
        lw("t2", 0x24, "sp"),
        addiu("s3", "t2", data_layout["meta"]),
        addiu("s4", "zero", len(STAGE_ROWS)),
        addiu("s5", "zero", 55),
    )
    e.label("row_loop")
    e.emit(
        lw("t6", 0, "s3"),
        lw("t2", 0x24, "sp"),
        addu("t6", "t6", "t2"),
        lw("t1", 4, "s3"),
        *address_words("t2", STATE_UNCACHED_VA),
        addu("t2", "t2", "t1"),
        lw("t3", 0, "t2"),
        _move("t4", "zero"),
    )
    e.label("check_pop")
    e.beq("t3", "zero", "check_done")
    e.emit(NOP)
    e.emit(addiu("t5", "t3", -1), and_("t3", "t3", "t5"), addiu("t4", "t4", 1))
    e.beq("zero", "zero", "check_pop")
    e.emit(NOP)
    e.label("check_done")
    e.emit(lw("t5", 12, "s3"))
    e.beq("t5", "zero", "extra_done")
    e.emit(NOP)
    e.emit(
        *address_words("t2", STATE_UNCACHED_VA),
        lw("t5", STATE_FLAGS_OFFSET, "t2"),
        andi("t5", "t5", 1),
        addu("t4", "t4", "t5"),
    )
    e.label("extra_done")
    e.emit(
        addiu("t7", "zero", 10),
        _divu("t4", "t7"),
        _mflo("t8"),
        _mfhi("t9"),
        addiu("t8", "t8", 0x30),
        sb("t8", 4, "t6"),
        addiu("t9", "t9", 0x30),
        sb("t9", 5, "t6"),
    )

    e.emit(lw("t1", 8, "s3"), sltiu("t2", "t1", ITEM_COUNT))
    e.beq("t2", "zero", "key_count_done")
    e.emit(NOP)
    e.emit(
        _srlv("t3", "s2", "t1"),
        andi("t3", "t3", 7),
        andi("t4", "t3", 1),
        srl("t5", "t3", 1),
        andi("t5", "t5", 1),
        addu("t4", "t4", "t5"),
        srl("t5", "t3", 2),
        andi("t5", "t5", 1),
        addu("t4", "t4", "t5"),
        addiu("t4", "t4", 0x30),
        sb("t4", 10, "t6"),
    )
    e.label("key_count_done")
    e.emit(
        _move("a0", "t6"),
        addiu("a1", "zero", 170),
        _move("a2", "s5"),
        addiu("a3", "zero", 1),
        *address_words("t0", PAPER_FONT_VA),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
        addiu("s3", "s3", 16),
        addiu("s4", "s4", -1),
        addiu("s5", "s5", 11),
    )
    e.bne("s4", "zero", "row_loop")
    e.emit(NOP)
    e.emit(
        lw("s5", 0x44, "sp"),
        lw("s4", 0x48, "sp"),
        lw("s3", 0x4C, "sp"),
        lw("s2", 0x50, "sp"),
        lw("s1", 0x54, "sp"),
        lw("s0", 0x58, "sp"),
        lw("ra", 0x5C, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x60),
    )
    return e.finish()


def _hud_code(data_layout: dict[str, int]) -> bytes:
    e = Emitter()
    e.emit(
        addiu("sp", "sp", -0x28),
        sw("ra", 0x24, "sp"),
        jal(ENSURE_DATA_VA),
        NOP,
        sw("v0", 0x18, "sp"),
    )
    if data_layout["requirement_exact"]:
        e.emit(
            *address_words("t0", POWER_COUNT_VA),
            lw("t1", 0, "t0"),
            sltiu("t2", "t1", 10),
        )
        e.bne("t2", "zero", "power_ok")
        e.emit(NOP)
        e.emit(addiu("t1", "zero", 9))
        e.label("power_ok")
        e.emit(
            lw("t3", 0x18, "sp"),
            addiu("t3", "t3", data_layout["requirement"]),
            addiu("t1", "t1", 0x30),
            sb("t1", 16, "t3"),
        )
    else:
        e.emit(lw("t3", 0x18, "sp"), addiu("t3", "t3", data_layout["requirement"]))
    e.emit(
        _move("a0", "t3"),
        addiu("a1", "zero", 121),
        addiu("a2", "zero", 173),
        addiu("a3", "zero", 1),
        *address_words("t0", LIST_FONT_VA),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
    )

    e.emit(
        *address_words("t0", STATE_UNCACHED_VA),
        addiu("t1", "t0", PICKUP_BITS_OFFSET),
        addiu("t2", "zero", 8),
        _move("t3", "zero"),
    )
    e.label("word_loop")
    e.emit(lw("t4", 0, "t1"))
    e.label("bit_loop")
    e.beq("t4", "zero", "next_word")
    e.emit(NOP)
    e.emit(addiu("t5", "t4", -1), and_("t4", "t4", "t5"), addiu("t3", "t3", 1))
    e.beq("zero", "zero", "bit_loop")
    e.emit(NOP)
    e.label("next_word")
    e.emit(addiu("t1", "t1", 4), addiu("t2", "t2", -1))
    e.bne("t2", "zero", "word_loop")
    e.emit(NOP)
    e.emit(lw("t4", STATE_FLAGS_OFFSET, "t0"), andi("t4", "t4", 1), addu("t3", "t3", "t4"))

    e.emit(
        lw("t6", 0x18, "sp"),
        addiu("t6", "t6", data_layout["check"]),
        addiu("t7", "zero", 10),
        _divu("t3", "t7"),
        _mflo("v1"),
        _mfhi("t9"),
        addiu("t8", "v1", 0x30),
        sb("t8", 0, "t6"),
        addiu("t9", "t9", 0x30),
        sb("t9", 1, "t6"),
        _move("a0", "t6"),
        addiu("a1", "zero", 1),
        jal(TEXT_WIDTH_VA),
        NOP,
        addiu("t0", "zero", 304),
        subu("a1", "t0", "v0"),
        lw("t6", 0x18, "sp"),
        addiu("a0", "t6", data_layout["check"]),
        addiu("a2", "zero", 173),
        addiu("a3", "zero", 1),
        *address_words("t0", LIST_FONT_VA),
        sw("t0", 0x10, "sp"),
        jal(TEXT_DRAW_VA),
        NOP,
        lw("ra", 0x24, "sp"),
        jr("ra"),
        addiu("sp", "sp", 0x28),
    )
    return e.finish()


def _dispatch_code(row_va: int, preview_va: int, hud_va: int) -> bytes:
    e = Emitter()
    e.emit(andi("t0", "ra", 0xFFFF), addiu("t1", "zero", 0x4270))
    e.beq("t0", "t1", "row")
    e.emit(NOP)
    e.emit(addiu("t1", "zero", 0x30A0))
    e.beq("t0", "t1", "preview")
    e.emit(NOP)
    e.emit(jump(hud_va), NOP)
    e.label("row")
    e.emit(jump(row_va), NOP)
    e.label("preview")
    e.emit(jump(preview_va), NOP)
    return e.finish()


def _build_runtime(data_layout: dict[str, int]) -> tuple[bytes, bytes, dict[str, int]]:
    ensure = _ensure_data_code()
    resolve = _resolve_code()
    resolve_va = ENSURE_DATA_VA + len(ensure)
    if len(ensure) + len(resolve) > RETIRED_END_VA - ENSURE_DATA_VA:
        raise AssertionError("ensure-data + resolver overflow retired permanent region")

    module = bytearray(HUD_CODE_SIZE)
    cursor = 0
    layout: dict[str, int] = {}

    def take(name: str, blob: bytes, alignment: int = 16) -> int:
        nonlocal cursor
        cursor = _align(cursor, alignment)
        offset = cursor
        module[offset : offset + len(blob)] = blob
        cursor += len(blob)
        layout[f"{name}_offset"] = offset
        layout[f"{name}_size"] = len(blob)
        return HUD_CODE_K1 + offset

    row_va = take("row", _row_code(resolve_va, data_layout))
    preview_va = take("preview", _preview_code(resolve_va))
    paper_va = take("paper", _paper_code(resolve_va, data_layout))
    hud_va = take("hud", _hud_code(data_layout))
    dispatch_va = take("dispatch", _dispatch_code(row_va, preview_va, hud_va), 4)
    if cursor > HUD_STATE_DATA_PTR_OFF:
        raise AssertionError("inventory HUD runtime helpers overlap fixed state words")
    _put32(module, HUD_STATE_DATA_PTR_OFF, 0)
    _put32(module, HUD_STATE_PREVIEW_CACHE_OFF, 0xFFFFFFFF)

    permanent = bytearray(RETIRED_END_ROM - RETIRED_START_ROM)
    permanent[0:16] = _trampoline(paper_va)
    permanent[16:32] = _trampoline(dispatch_va)
    ensure_offset = ENSURE_DATA_VA - RETIRED_START_VA
    permanent[ensure_offset : ensure_offset + len(ensure)] = ensure
    permanent[
        ensure_offset + len(ensure) : ensure_offset + len(ensure) + len(resolve)
    ] = resolve

    layout.update(
        {
            "used": cursor,
            "row_va": row_va,
            "preview_va": preview_va,
            "paper_va": paper_va,
            "hud_va": hud_va,
            "dispatch_va": dispatch_va,
            "ensure_size": len(ensure),
            "resolve_size": len(resolve),
        }
    )
    return bytes(module), bytes(permanent), layout


def _build_portrait_atlas(rom: RomImage) -> tuple[bytes, bytes]:
    atlas_parts: list[bytes] = []
    first_record: bytes | None = None
    for file_id, sprite_ids in PORTRAIT_DONORS:
        raw, _start, _end = _package_raw(rom, file_id)
        records, _image_end = _image_records(raw)
        for sprite_id in sprite_ids:
            try:
                record = records[sprite_id]
            except KeyError as exc:
                raise PatchError(
                    f"file 0x{file_id:02X} is missing portrait sprite 0x{sprite_id:X}"
                ) from exc
            flags, width_word, height, _stored_sprite, _unused = struct.unpack_from(
                ">IHhHH", record, 0
            )
            stride = (width_word & 0xFF) or 256
            if flags & 0x80000000:
                stride //= 2
            if stride != 36 or height != 48:
                raise PatchError(
                    f"portrait sprite 0x{sprite_id:X} has unexpected {stride}x{height} geometry"
                )
            payload = record[12 : 12 + PORTRAIT_BYTES]
            if len(payload) != PORTRAIT_BYTES:
                raise PatchError(f"portrait sprite 0x{sprite_id:X} is truncated")
            atlas_parts.append(payload)
            if first_record is None:
                first_record = record

    atlas = b"".join(atlas_parts)
    if len(atlas) != PORTRAIT_ATLAS_SIZE or first_record is None:
        raise AssertionError("portrait atlas size drifted")
    seed_record = bytearray(first_record)
    struct.pack_into(">H", seed_record, 8, CUSTOM_SPRITE_ID)
    return atlas, bytes(seed_record)


def _guard_output_span(rom: RomImage, start: int, end: int, *, ignore_file: int | None = None) -> None:
    if not 0 <= start < end <= len(rom.data):
        raise PatchError(f"inventory HUD output span [0x{start:X},0x{end:X}) exceeds ROM")
    if bytes(rom.data[start:end]) != b"\xFF" * (end - start):
        raise PatchError(f"inventory HUD output span [0x{start:X},0x{end:X}) is not blank")
    for file_id in range(0xAC):
        if file_id == ignore_file:
            continue
        entry = FILE_TABLE_ROM + file_id * FILE_TABLE_ENTRY_SIZE
        file_start = rom.read_u32(entry)
        file_end = rom.read_u32(entry + 4)
        if file_start and file_end > file_start and start < file_end and end > file_start:
            raise PatchError(
                f"inventory HUD output span overlaps file 0x{file_id:02X} "
                f"[0x{file_start:X},0x{file_end:X})"
            )


class InventoryHudPatch:
    """Install the accepted native randomizer Inventory HUD in the shared product path."""

    name = "inventory-randomizer-hud"

    def __init__(self, required_powers_mode: str, custom_required_powers: int | None = None):
        self.required_powers_mode = required_powers_mode
        self.custom_required_powers = custom_required_powers

    def apply(self, rom: RomImage, context: PatchContext) -> tuple[str, ...]:
        required_count, _required_xp = resolve_required_powers(
            self.required_powers_mode,
            self.custom_required_powers,
            context.seed,
        )

        if len(rom.data) != GLOBAL_OUTPUT_SIZE:
            raise PatchError("inventory HUD requires the normal 32 MiB generated output")
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 0, 0x00F68000)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 4, MATERIALIZER_HELPER_END_ROM)
        rom.expect_u32(EXPANSION_FILE_ENTRY_ROM + 8, 0)
        rom.expect_bytes(HUD_CODE_ROM, b"\xFF" * HUD_CODE_SIZE)

        rom.expect_u32(ROW_HOOK_ROM, EXPECTED_ROW_HOOK)
        rom.expect_u32(PREVIEW_HOOK_ROM, EXPECTED_PREVIEW_HOOK)
        rom.expect_u32(SECOND_LABEL_DRAW_ROM, EXPECTED_SECOND_TEXT_DRAW)
        rom.expect_u32(SECOND_VALUE_DRAW_ROM, EXPECTED_SECOND_TEXT_DRAW)
        rom.expect_bytes(RETIRED_START_ROM, EXPECTED_RETIRED_REGION)

        atlas, seed_record = _build_portrait_atlas(rom)
        common_raw, _old_common_start, _old_common_end = _package_raw(rom, COMMON_PACKAGE_ID)
        common_records, _image_end = _image_records(common_raw)
        if CUSTOM_SPRITE_ID in common_records:
            raise PatchError("common file 0x5D already owns inventory HUD sprite 0x46C")
        expanded_common = _append_image_record(common_raw, seed_record)
        packed_common = _compress_resource_package(expanded_common)
        common_end = COMMON_PACKAGE_ROM + len(packed_common)
        if common_end > COMMON_PACKAGE_ROM + COMMON_PACKAGE_CAPACITY:
            raise PatchError("expanded common image package exceeds owned 0xB000 capacity")

        _guard_output_span(rom, PORTRAIT_ATLAS_ROM, PORTRAIT_ATLAS_ROM + len(atlas))
        _guard_output_span(rom, COMMON_PACKAGE_ROM, common_end, ignore_file=COMMON_PACKAGE_ID)
        _guard_output_span(rom, HUD_DATA_ROM, HUD_DATA_END_ROM)

        hud_data, data_layout = _build_hud_data(rom, required_count=required_count)
        module, permanent, runtime_layout = _build_runtime(data_layout)

        rom.write_bytes(PORTRAIT_ATLAS_ROM, atlas)
        rom.write_bytes(COMMON_PACKAGE_ROM, packed_common)
        common_entry = FILE_TABLE_ROM + COMMON_PACKAGE_ID * FILE_TABLE_ENTRY_SIZE
        rom.write_u32(common_entry + 0, COMMON_PACKAGE_ROM)
        rom.write_u32(common_entry + 4, common_end)
        rom.write_u32(common_entry + 8, 1)
        rom.write_bytes(HUD_DATA_ROM, hud_data)

        rom.write_bytes(HUD_CODE_ROM, module)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM + 4, HUD_CODE_END_ROM)
        rom.write_bytes(RETIRED_START_ROM, permanent)
        rom.write_u32(ROW_HOOK_ROM, jal(SHARED_TRAMP_VA))
        rom.write_u32(PREVIEW_HOOK_ROM, jal(SHARED_TRAMP_VA))
        rom.write_u32(SECOND_LABEL_DRAW_ROM, NOP)
        rom.write_u32(SECOND_VALUE_DRAW_ROM, jal(SHARED_TRAMP_VA))

        requirement_note = (
            f"exact required powers {required_count}"
            if required_count is not None
            else f"stock Fortress XP requirement {VANILLA_XP_REQUIREMENT}"
        )
        return (
            "bounded Runtime-confirmed inventory labels, paper table and streamed key portraits",
            "one shared file-0x5D sprite 0x46C streams the selected key/icon/crystal portrait",
            (
                f"HUD runtime tail K0 0x{HUD_CODE_K0:08X}..0x{HUD_CODE_END_K0 - 1:08X}; "
                f"helper bytes used 0x{runtime_layout['used']:X}"
            ),
            f"native HUD requirement display: {requirement_note}; right-aligned XX/85 uses persistent check state",
            "HUD read-only data uses one lazy 0x1200-byte main-arena allocation per stage lifecycle",
        )