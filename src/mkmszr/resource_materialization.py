"""Pure cross-stage pickup visual resource planner.

This module is intentionally not wired into the production patch pipeline yet.
It implements the runtime-confirmed extension-selector architecture and the
runtime-confirmed external-resource-ID -> embedded type-4 conversion, but the
normal browser/CLI path remains stage-local until a composed multi-item proof
ROM is manually validated.

The planner keeps award semantics separate from visual materialization.  Fixed
global pickup callbacks can be composed directly; stage-bound key/crystal
callbacks still require a destination-safe wrapper before production use.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from .data.pickups import STAGE_PICKUPS
from .errors import PatchError
from .global_items import logical_item_from_record

FILE_TABLE_ROM = 0x000A5010


@dataclass(frozen=True)
class StageResourceSpec:
    stage_id: int
    file_table_entry_rom: int
    rom_start: int
    rom_end: int

    @property
    def size(self) -> int:
        return self.rom_end - self.rom_start


STAGE_RESOURCES: dict[int, StageResourceSpec] = {
    0: StageResourceSpec(0, 0x000A5490, 0x00513710, 0x00523370),
    1: StageResourceSpec(1, 0x000A561C, 0x00698680, 0x0069A820),
    2: StageResourceSpec(2, 0x000A558C, 0x00611780, 0x00617C60),
    3: StageResourceSpec(3, 0x000A5670, 0x006BAEC0, 0x006DD470),
    4: StageResourceSpec(4, 0x000A537C, 0x0041C680, 0x00420F70),
    5: StageResourceSpec(5, 0x000A52E0, 0x00388260, 0x0038A790),
    8: StageResourceSpec(8, 0x000A51E4, 0x00296140, 0x0029A470),
    9: StageResourceSpec(9, 0x000A5334, 0x003B9700, 0x003BCD20),
}


@dataclass(frozen=True)
class VisualDonorSpec:
    stage_id: int
    record_index: int
    frame_count: int
    package_file_id: int | None = None


# Canonical sources deliberately avoid Earth zero-terminated pickup formats.
# Fire's Formula/Eye/Shield and Water's Health urn are normal external-ID
# bundles; they are converted to self-contained type-4 blocks by this module.
CANONICAL_VISUAL_DONORS: dict[str, VisualDonorSpec] = {
    "potion": VisualDonorSpec(2, 4, 8),
    "formula": VisualDonorSpec(5, 1, 8, 0x39),
    "eye": VisualDonorSpec(5, 11, 8, 0x39),
    "herbs": VisualDonorSpec(2, 3, 8),
    "health-urn": VisualDonorSpec(2, 0, 4, 0x73),
    "shield": VisualDonorSpec(5, 6, 8, 0x39),
    "extra-life": VisualDonorSpec(2, 5, 8),
    "mana": VisualDonorSpec(2, 2, 8),
    "strength-urn": VisualDonorSpec(4, 3, 8),
    "wind-circle": VisualDonorSpec(1, 3, 8),
    "wind-three-bars": VisualDonorSpec(1, 5, 8),
    "wind-triangle": VisualDonorSpec(1, 4, 8),
    "earth-square": VisualDonorSpec(3, 0, 12),
    "earth-four-square": VisualDonorSpec(3, 1, 9),
    "earth-triangle": VisualDonorSpec(3, 2, 9),
    "water-three-bars": VisualDonorSpec(2, 7, 8),
    "water-triangle": VisualDonorSpec(2, 6, 8),
    "water-moon": VisualDonorSpec(2, 8, 8),
    "fire-triangle-down": VisualDonorSpec(5, 14, 8),
    "fire-two-bars": VisualDonorSpec(5, 9, 8),
    "fire-triangle-up": VisualDonorSpec(5, 4, 8),
    "prison-l1": VisualDonorSpec(4, 0, 8),
    "prison-l2": VisualDonorSpec(4, 1, 8),
    "prison-l3": VisualDonorSpec(4, 2, 8),
    "bridge-omega": VisualDonorSpec(8, 0, 8),
    "bridge-rings": VisualDonorSpec(8, 1, 8),
    "bridge-arrow": VisualDonorSpec(8, 2, 8),
    "crystal-jataaka": VisualDonorSpec(9, 1, 8),
    "crystal-kia": VisualDonorSpec(9, 0, 8),
    "crystal-sareena": VisualDonorSpec(9, 2, 8),
}


@dataclass(frozen=True)
class PackageImage:
    width_word: int
    height: int
    payload: bytes


@dataclass(frozen=True)
class VisualFrame:
    metadata: bytes
    image_block: bytes

    def __post_init__(self) -> None:
        if len(self.metadata) != 8:
            raise ValueError("visual frame metadata must be exactly 8 bytes")


@dataclass(frozen=True)
class VisualBundle:
    key: str
    descriptor_control: int
    frames: tuple[VisualFrame, ...]

    def __post_init__(self) -> None:
        if not self.frames:
            raise ValueError("visual bundle must contain at least one frame")


@dataclass(frozen=True)
class MaterializedVisual:
    key: str
    selector: int
    selector_entry_offset: int
    descriptor_offset: int


@dataclass(frozen=True)
class StageResourcePlan:
    stage_id: int
    stock_size: int
    resource_file: bytes
    visuals: tuple[MaterializedVisual, ...]

    @property
    def expanded_size(self) -> int:
        return len(self.resource_file)

    def selector_for(self, key: str) -> int:
        for visual in self.visuals:
            if visual.key == key:
                return visual.selector
        raise KeyError(key)


def _be32(data: bytes | bytearray, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise PatchError(f"out-of-range 32-bit read at 0x{offset:X}")
    return int.from_bytes(data[offset : offset + 4], "big")


def _write_be32(data: bytearray, offset: int, value: int) -> None:
    data[offset : offset + 4] = (value & 0xFFFFFFFF).to_bytes(4, "big")


def _align4(value: int) -> int:
    return (value + 3) & ~3


def _stage_pickups(stage_id: int):
    try:
        return next(stage for stage in STAGE_PICKUPS if stage.stage_id == stage_id)
    except StopIteration as exc:
        raise PatchError(f"unknown stage ID {stage_id}") from exc


def _identity_selector(identity: bytes) -> int:
    return int.from_bytes(identity[0x14:0x18], "big")


def _compressed_image_size(block: bytes | bytearray, offset: int = 0) -> int:
    if offset < 0 or offset + 8 > len(block):
        raise PatchError("truncated embedded image header")
    size = block[offset] | (block[offset + 1] << 8) | (block[offset + 2] << 16)
    if size < 8:
        raise PatchError(f"invalid embedded image size {size}")
    if offset + size > len(block):
        raise PatchError("embedded image extends beyond source buffer")
    return size


def decode_type4(block: bytes) -> bytes:
    """Decode one self-contained MKMSZ type-4 block.

    The ring starts zeroed here.  This is sufficient for the planner's
    literal-only output and for unit tests.  Stock blocks may legally rely on
    ring history, so the planner copies them verbatim rather than decoding and
    re-encoding them.
    """

    size = _compressed_image_size(block)
    if size != len(block):
        block = block[:size]
    if block[3] & 0x3F != 4:
        raise PatchError(f"expected type-4 embedded image, got type {block[3] & 0x3F}")

    token_offset = int.from_bytes(block[4:8], "little")
    control_pos = 8
    token_pos = 4 + token_offset
    if token_pos > len(block):
        raise PatchError("type-4 token stream offset is out of range")

    ring = bytearray(1024)
    ring_index = 1
    control_mask = 0x80
    if control_pos >= len(block):
        raise PatchError("type-4 control stream is missing")
    control = block[control_pos]
    control_pos += 1
    output = bytearray()

    while True:
        if control & control_mask:
            if token_pos >= len(block):
                raise PatchError("type-4 literal token overruns block")
            value = block[token_pos]
            token_pos += 1
            output.append(value)
            ring[ring_index] = value
            ring_index = (ring_index + 1) & 0x3FF
        else:
            if token_pos + 2 > len(block):
                raise PatchError("type-4 back-reference token overruns block")
            b0 = block[token_pos]
            b1 = block[token_pos + 1]
            token_pos += 2
            source_index = (b0 << 2) | (b1 >> 6)
            if source_index == 0:
                break
            count = (b1 & 0x3F) + 2
            for index in range(count):
                value = ring[(source_index + index) & 0x3FF]
                output.append(value)
                ring[ring_index] = value
                ring_index = (ring_index + 1) & 0x3FF

        control_mask >>= 1
        if control_mask == 0:
            control_mask = 0x80
            if control_pos >= len(block):
                raise PatchError("type-4 control stream terminated before end token")
            control = block[control_pos]
            control_pos += 1

    return bytes(output)


def encode_type4_literals(raw: bytes) -> bytes:
    """Encode raw indexed pixels as a deterministic, self-contained type-4 block."""

    token_count = len(raw) + 1
    control_count = (token_count + 7) // 8
    controls = bytearray(control_count)
    for index in range(len(raw)):
        controls[index // 8] |= 0x80 >> (index % 8)

    token_stream = raw + b"\x00\x00"
    token_offset = 4 + len(controls)
    total_size = 8 + len(controls) + len(token_stream)
    if total_size > 0xFFFFFF:
        raise PatchError("type-4 image exceeds 24-bit size field")

    header = bytes(
        (
            total_size & 0xFF,
            (total_size >> 8) & 0xFF,
            (total_size >> 16) & 0xFF,
            4,
        )
    ) + token_offset.to_bytes(4, "little")
    encoded = header + bytes(controls) + token_stream
    if decode_type4(encoded) != raw:
        raise PatchError("internal type-4 round-trip verification failed")
    return encoded


def _read_bits_msb(data: bytes, bit_position: int, width: int) -> tuple[int, int]:
    value = 0
    for _ in range(width):
        byte_index = bit_position >> 3
        if byte_index >= len(data):
            raise PatchError("compressed package bitstream ended unexpectedly")
        bit_index = 7 - (bit_position & 7)
        value = (value << 1) | ((data[byte_index] >> bit_index) & 1)
        bit_position += 1
    return value, bit_position


def decompress_resource_package(blob: bytes) -> bytes:
    """Decode the MKMSZ package LZW stream used by stage image packages."""

    if len(blob) < 8:
        raise PatchError("compressed package is too small")
    expected_size = int.from_bytes(blob[:4], "big")
    source = blob[4:]

    table: list[bytes | None] = [bytes((value,)) for value in range(256)] + [None, None]
    next_code = 0x102
    width = 9
    bit_position = 0
    previous: bytes | None = None
    output = bytearray()

    while True:
        code, bit_position = _read_bits_msb(source, bit_position, width)
        if code == 0x100:
            table = [bytes((value,)) for value in range(256)] + [None, None]
            next_code = 0x102
            width = 9
            previous = None
            continue
        if code == 0x101:
            break

        if code < len(table) and table[code] is not None:
            entry = table[code]
            assert entry is not None
        elif code == next_code and previous is not None:
            entry = previous + previous[:1]
        else:
            raise PatchError(f"invalid package LZW code 0x{code:X}")

        output += entry

        if previous is not None and next_code < 0x1000:
            new_entry = previous + entry[:1]
            if next_code == len(table):
                table.append(new_entry)
            elif next_code < len(table):
                table[next_code] = new_entry
            else:
                table.extend([None] * (next_code - len(table)))
                table.append(new_entry)
            next_code += 1
            if width < 12 and next_code >= (1 << width) - 1:
                width += 1

        previous = entry

    if len(output) != expected_size:
        raise PatchError(
            f"package size mismatch: expected {expected_size}, decoded {len(output)}"
        )
    return bytes(output)


def parse_resource_package_images(package: bytes) -> dict[int, PackageImage]:
    """Parse the image section emitted by the native package loader."""

    if len(package) < 8:
        raise PatchError("decoded package is too small")
    count = int.from_bytes(package[:4], "big")
    cursor = 8
    result: dict[int, PackageImage] = {}

    for _ in range(count):
        if cursor + 12 > len(package):
            raise PatchError("truncated package image record")

        flags = int.from_bytes(package[cursor : cursor + 4], "big")
        width_word = int.from_bytes(package[cursor + 4 : cursor + 6], "big")
        height = int.from_bytes(package[cursor + 6 : cursor + 8], "big", signed=True)
        resource_id = int.from_bytes(package[cursor + 8 : cursor + 10], "big")
        if height < 0:
            raise PatchError(f"negative package image height for ID 0x{resource_id:X}")

        low_width = width_word & 0xFF
        stride = 256 if low_width == 0 else low_width
        if flags & 0x80000000:
            stride //= 2
        payload_size = stride * height
        payload_start = cursor + 12
        payload_end = payload_start + payload_size
        if payload_end > len(package):
            raise PatchError(f"package image 0x{resource_id:X} overruns decoded package")

        result[resource_id] = PackageImage(
            width_word=width_word,
            height=height,
            payload=bytes(package[payload_start:payload_end]),
        )
        cursor = _align4(payload_end)

    return result


def _package_images_from_rom(rom: bytes, file_id: int) -> dict[int, PackageImage]:
    entry = FILE_TABLE_ROM + file_id * 12
    start = _be32(rom, entry)
    end = _be32(rom, entry + 4)
    flag = _be32(rom, entry + 8)
    if flag != 1:
        raise PatchError(f"package file ID 0x{file_id:X} expected compression flag 1, got {flag}")
    if not (0 <= start < end <= len(rom)):
        raise PatchError(f"package file ID 0x{file_id:X} has invalid ROM bounds")
    return parse_resource_package_images(decompress_resource_package(rom[start:end]))


def extract_canonical_bundle(rom: bytes, key: str) -> VisualBundle:
    """Extract one canonical visual and normalize external frames to embedded type 4."""

    try:
        donor = CANONICAL_VISUAL_DONORS[key]
    except KeyError as exc:
        raise PatchError(f"no canonical visual donor registered for {key!r}") from exc

    stage = _stage_pickups(donor.stage_id)
    if donor.record_index >= len(stage.records):
        raise PatchError(f"{key}: donor record index is out of range")
    pickup = stage.records[donor.record_index]

    spec = STAGE_RESOURCES[donor.stage_id]
    selector = _identity_selector(pickup.identity)
    descriptor_offset = _be32(rom, spec.rom_start + selector * 4)
    if descriptor_offset == 0:
        raise PatchError(f"{key}: canonical selector {selector} is empty")

    descriptor_size = donor.frame_count * 4 + 8
    descriptor_start = spec.rom_start + descriptor_offset
    descriptor_end = descriptor_start + descriptor_size
    if descriptor_end > spec.rom_end:
        raise PatchError(f"{key}: descriptor exceeds source stage resource file")

    descriptor = rom[descriptor_start:descriptor_end]
    descriptor_control = _be32(descriptor, donor.frame_count * 4)
    descriptor_self = _be32(descriptor, donor.frame_count * 4 + 4)
    if descriptor_self != descriptor_offset:
        raise PatchError(
            f"{key}: descriptor self pointer 0x{descriptor_self:X} "
            f"does not match 0x{descriptor_offset:X}"
        )

    package_images: dict[int, PackageImage] | None = None
    frames: list[VisualFrame] = []

    for frame_index in range(donor.frame_count):
        record_offset = _be32(descriptor, frame_index * 4)
        record_start = spec.rom_start + record_offset
        record_end = record_start + 0x14
        if record_end > spec.rom_end:
            raise PatchError(f"{key}: frame {frame_index} record exceeds source file")
        record = rom[record_start:record_end]

        record_link = _be32(record, 0)
        external_id = _be32(record, 4)
        data_offset = _be32(record, 8)
        if record_link != record_offset + 8:
            raise PatchError(f"{key}: frame {frame_index} has unexpected record link")
        metadata = bytes(record[12:20])

        if external_id and not data_offset:
            if donor.package_file_id is None:
                raise PatchError(
                    f"{key}: external frame requires an explicit package file ID"
                )
            if package_images is None:
                package_images = _package_images_from_rom(rom, donor.package_file_id)
            try:
                raw = package_images[external_id].payload
            except KeyError as exc:
                raise PatchError(
                    f"{key}: package 0x{donor.package_file_id:X} lacks "
                    f"resource ID 0x{external_id:X}"
                ) from exc
            image_block = encode_type4_literals(raw)
        elif data_offset and not external_id:
            image_start = spec.rom_start + data_offset
            if image_start + 8 > spec.rom_end:
                raise PatchError(f"{key}: frame {frame_index} embedded image header is out of range")
            size = _compressed_image_size(rom, image_start)
            if image_start + size > spec.rom_end:
                raise PatchError(f"{key}: frame {frame_index} embedded image exceeds source file")
            image_block = bytes(rom[image_start : image_start + size])
        else:
            raise PatchError(
                f"{key}: frame {frame_index} is not a normal embedded/external resource record"
            )

        frames.append(VisualFrame(metadata=metadata, image_block=image_block))

    return VisualBundle(
        key=key,
        descriptor_control=descriptor_control,
        frames=tuple(frames),
    )


def build_extended_resource_file(
    stock_file: bytes,
    bundles: Iterable[VisualBundle],
    *,
    max_size: int | None = None,
) -> tuple[bytes, tuple[MaterializedVisual, ...]]:
    """Append a deterministic extension selector table and self-contained bundles."""

    if len(stock_file) % 4:
        raise PatchError("stock stage resource file size must be 4-byte aligned")

    by_key: dict[str, VisualBundle] = {}
    for bundle in bundles:
        previous = by_key.get(bundle.key)
        if previous is not None and previous != bundle:
            raise PatchError(f"conflicting visual bundles supplied for {bundle.key!r}")
        by_key[bundle.key] = bundle

    ordered = [by_key[key] for key in sorted(by_key)]
    output = bytearray(stock_file)
    extension_table_offset = len(output)
    output.extend(bytes(4 * len(ordered)))

    visuals: list[MaterializedVisual] = []
    for index, bundle in enumerate(ordered):
        while len(output) % 4:
            output.append(0)

        descriptor_offset = len(output)
        frame_count = len(bundle.frames)
        descriptor_size = frame_count * 4 + 8
        output.extend(bytes(descriptor_size))

        record_offsets: list[int] = []
        records_offset = len(output)
        output.extend(bytes(frame_count * 0x14))
        for frame_index in range(frame_count):
            record_offsets.append(records_offset + frame_index * 0x14)

        block_offsets: list[int] = []
        for frame in bundle.frames:
            while len(output) % 4:
                output.append(0)
            block_offsets.append(len(output))
            output.extend(frame.image_block)

        selector_entry_offset = extension_table_offset + index * 4
        selector = selector_entry_offset // 4
        _write_be32(output, selector_entry_offset, descriptor_offset)

        for frame_index, record_offset in enumerate(record_offsets):
            _write_be32(output, descriptor_offset + frame_index * 4, record_offset)

        _write_be32(
            output,
            descriptor_offset + frame_count * 4,
            bundle.descriptor_control,
        )
        _write_be32(
            output,
            descriptor_offset + frame_count * 4 + 4,
            descriptor_offset,
        )

        for frame_index, (record_offset, frame, block_offset) in enumerate(
            zip(record_offsets, bundle.frames, block_offsets, strict=True)
        ):
            _write_be32(output, record_offset, record_offset + 8)
            _write_be32(output, record_offset + 4, 0)
            _write_be32(output, record_offset + 8, block_offset)
            output[record_offset + 12 : record_offset + 20] = frame.metadata

            # Planner-generated external conversions must be self-contained.
            if _compressed_image_size(output, block_offset) != len(frame.image_block):
                raise PatchError(
                    f"{bundle.key}: frame {frame_index} image size/header mismatch"
                )

        visuals.append(
            MaterializedVisual(
                key=bundle.key,
                selector=selector,
                selector_entry_offset=selector_entry_offset,
                descriptor_offset=descriptor_offset,
            )
        )

    while len(output) % 4:
        output.append(0)

    if max_size is not None and len(output) > max_size:
        raise PatchError(
            f"expanded stage resource file is 0x{len(output):X} bytes; "
            f"limit is 0x{max_size:X}"
        )

    return bytes(output), tuple(visuals)


def plan_stage_resources(
    rom: bytes,
    stage_id: int,
    item_keys: Iterable[str],
    *,
    max_size: int | None = None,
) -> StageResourcePlan:
    """Build a pure resource-file plan for one destination stage.

    Every requested distinct logical visual is appended canonically.  The
    production integration may later add proven resident-resource reuse, but
    this conservative form never aliases a destination shell merely because it
    has a superficially similar role.
    """

    try:
        spec = STAGE_RESOURCES[stage_id]
    except KeyError as exc:
        raise PatchError(f"unknown stage ID {stage_id}") from exc

    start = _be32(rom, spec.file_table_entry_rom)
    end = _be32(rom, spec.file_table_entry_rom + 4)
    flag = _be32(rom, spec.file_table_entry_rom + 8)
    if (start, end, flag) != (spec.rom_start, spec.rom_end, 0):
        raise PatchError(
            f"stage {stage_id}: resource file-table guard failed; "
            f"got ({start:#x}, {end:#x}, {flag})"
        )

    keys = sorted(set(item_keys))
    bundles = [extract_canonical_bundle(rom, key) for key in keys]
    resource_file, visuals = build_extended_resource_file(
        bytes(rom[spec.rom_start : spec.rom_end]),
        bundles,
        max_size=max_size,
    )
    return StageResourcePlan(
        stage_id=stage_id,
        stock_size=spec.size,
        resource_file=resource_file,
        visuals=visuals,
    )


def apply_stage_resource_plan(
    rom: bytearray,
    plan: StageResourcePlan,
    relocation_start: int,
    *,
    expected_fill: int | None = 0xFF,
) -> tuple[int, int]:
    """Write one planned resource file to an explicitly owned ROM allocation.

    This helper does not choose allocations.  The caller owns collision checks
    and supplies the relocation start.  By default the target must still be
    0xFF-filled, which is appropriate for disposable proof allocations.
    """

    spec = STAGE_RESOURCES[plan.stage_id]
    relocation_end = relocation_start + len(plan.resource_file)
    if relocation_start < 0 or relocation_end > len(rom):
        raise PatchError("resource relocation exceeds ROM bounds")
    if expected_fill is not None:
        target = rom[relocation_start:relocation_end]
        if target != bytes((expected_fill,)) * len(target):
            raise PatchError(
                f"stage {plan.stage_id}: relocation target is not "
                f"0x{expected_fill:02X}-filled"
            )

    rom[relocation_start:relocation_end] = plan.resource_file
    _write_be32(rom, spec.file_table_entry_rom, relocation_start)
    _write_be32(rom, spec.file_table_entry_rom + 4, relocation_end)
    _write_be32(rom, spec.file_table_entry_rom + 8, 0)
    return relocation_start, relocation_end


def portable_fixed_callback_identity(key: str, selector: int) -> bytes:
    """Return a canonical pickup identity for a globally resident callback.

    Progression tokens intentionally fail closed here because their stock
    callbacks are stage-overlay functions.  They need the separate
    destination-safe wrapper path before global production integration.
    """

    try:
        donor = CANONICAL_VISUAL_DONORS[key]
    except KeyError as exc:
        raise PatchError(f"no canonical donor registered for {key!r}") from exc

    stage = _stage_pickups(donor.stage_id)
    pickup = stage.records[donor.record_index]
    logical = logical_item_from_record(donor.stage_id, donor.record_index, pickup)
    if logical.native_callback is None:
        raise PatchError(
            f"{key}: stock award callback is stage-bound; "
            "destination-safe token wrapper required"
        )
    if logical.key != key:
        raise PatchError(
            f"{key}: canonical donor decodes as unexpected logical item {logical.key!r}"
        )

    identity = bytearray(pickup.identity)
    identity[0x14:0x18] = selector.to_bytes(4, "big")
    return bytes(identity)
