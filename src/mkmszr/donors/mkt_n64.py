"""Donor extraction for Mortal Kombat Trilogy N64 USA Rev. 2."""

from __future__ import annotations

import hashlib
import zlib

from ..errors import RomValidationError
from ..patches.toasty_constants import ToastyAssets

MKT_N64_REV2_SHA256 = "30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb"
MKT_N64_REV2_SIZE = 12 * 1024 * 1024
N64_BIG_ENDIAN_MAGIC = 0x80371240

TOASTY_DICT_ROM = 0x000F0B18
TOASTY_DICT_SIZE = 0x100
TOASTY_IMAGE_ROM = 0x000F2FC0
TOASTY_IMAGE_COMPRESSED_SIZE = 0x0AA5
TOASTY_IMAGE_DECOMPRESSED_SIZE = 80 * 85
TOASTY_VISIBLE_WIDTH = 78
TOASTY_HEIGHT = 85
TOASTY_PALETTE_ROM = 0x000B9008

MKT_CTL_COMP_ROM = 0x00A8F588
MKT_CTL_COMP_SIZE = 0x17AE0
MKT_CTL_RAW_SIZE = 0x1F720
DONOR_SUBPATCH_111_OFF = 0x0F8C
DONOR_WAVE_77_OFF = 0x2F60
DONOR_PRED_77_OFF = 0x9EB0
DONOR_SAMPLE_ROM = 0x00B0FBFC
DONOR_SAMPLE_LEN = 0x816

EXPECTED_DICT_SHA256 = "dd467f1b389d8f1e83761062638748e4aec0e1f856900b8a24a299c07ff59b59"
EXPECTED_IMAGE_STREAM_SHA256 = "f78135df4dc0e8d7c1fe42cc3f3a921d162a3d6751a357390b64370e67736204"
EXPECTED_IMAGE_DECODED_SHA256 = "18eed9a06f82249cd7b3db3b83cb1cd0115df739ca77712fdc4e274413794736"
EXPECTED_PALETTE_SOURCE_SHA256 = "1e0864523ff24b957738682bd1e8f4d2354f87036dd908291b1e5e98393337dd"
EXPECTED_TARGET_TLUT_SHA256 = "d70dacdfe067f516b0647b62bf7effdb167bc077037f4a4f45e5d754168dae31"
EXPECTED_CTL_SHA256 = "8dc6f036dc795cba2aa151e2fa7833d3bc3ac70f454b48fcd50df6c6d365b836"
EXPECTED_PRED_SHA256 = "6ec8e062f6eff4c49755c0bb27de754313706bc6033f34601601c214235efc5f"
EXPECTED_SAMPLE_SHA256 = "57090534e758a3d0a1676722b2ce5715da2e0b13ac155aff9cc7df04822d678f"
EXPECTED_SUBPATCH = bytes.fromhex("646940003c00007f0000004d00027d00000a7f7f")
EXPECTED_WAVE = bytes.fromhex("0005b88c0000081600000000fffff733ffffffff00000000")

_PIECES = (
    (0, 0, 7, 32),
    (7, 0, 64, 32),
    (71, 0, 7, 32),
    (0, 32, 7, 32),
    (7, 32, 64, 32),
    (71, 32, 7, 32),
    (0, 64, 7, 21),
    (7, 64, 64, 21),
    (71, 64, 7, 21),
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode_dict64_final(source: bytes, dictionary: bytes) -> bytes:
    if len(source) < 6:
        raise ValueError("MKT Toasty image stream is truncated")
    header = int.from_bytes(source[:4], "big")
    if header >> 24 != 0x19:
        raise ValueError(f"unexpected MKT Toasty image compression type 0x{header >> 24:02X}")
    output_size = header & 0x00FFFFFF
    position = 4
    flip_length = source[position]
    position += 1
    if flip_length & 0x80:
        flip_length = ((flip_length & 0x7F) << 8) | source[position]
        position += 1

    flip_data = source[position : position + flip_length]
    position += flip_length
    flip_index = 0
    output = bytearray()

    while len(output) < output_size:
        if position >= len(source):
            raise ValueError("MKT Toasty image stream ended early")
        token = source[position]
        position += 1
        mode = token >> 6
        value = token & 0x3F

        if mode == 0:
            output.append(value)
        elif mode == 1:
            output.extend((value, value))
        elif mode == 2:
            flip_byte = flip_data[flip_index // 4]
            shift = 6 - 2 * (flip_index % 4)
            flip = (flip_byte >> shift) & 0x03
            flip_index += 1
            index = (value | ((flip & 0x01) << 6)) << 1
            if flip & 0x02:
                output.extend((dictionary[index + 1], dictionary[index]))
            else:
                output.extend((dictionary[index], dictionary[index + 1]))
        else:
            if position >= len(source):
                raise ValueError("MKT Toasty RLE token is truncated")
            count = source[position]
            position += 1
            output.extend((value,) * count)

        if len(output) > output_size:
            raise ValueError("MKT Toasty image stream overran its declared output size")

    return bytes(output)


def _build_visual_assets(decoded: bytes, source_palette: bytes) -> tuple[tuple[bytes, ...], bytes]:
    if len(decoded) != TOASTY_IMAGE_DECOMPRESSED_SIZE:
        raise ValueError("decoded MKT Toasty image has the wrong size")
    if len(source_palette) != 0x80:
        raise ValueError("MKT Toasty palette must contain 64 colors")

    visible = b"".join(
        decoded[row * 80 : row * 80 + TOASTY_VISIBLE_WIDTH]
        for row in range(TOASTY_HEIGHT)
    )

    palette_order: list[int] = []
    seen: set[int] = set()
    for pixel in visible:
        if pixel not in seen:
            seen.add(pixel)
            palette_order.append(pixel)

    remap = {old: new for new, old in enumerate(palette_order)}
    remapped = bytes(remap[pixel] for pixel in visible)

    colors = [
        source_palette[index * 2 : index * 2 + 2]
        for index in palette_order
    ]
    tlut = b"".join(colors)
    tlut += bytes(0x200 - len(tlut))

    slices: list[bytes] = []
    for x, y, width, height in _PIECES:
        stride = (width + 31) & ~31
        data = bytearray(stride * height)
        for row in range(height):
            source_row = remapped[(y + row) * TOASTY_VISIBLE_WIDTH : (y + row + 1) * TOASTY_VISIBLE_WIDTH]
            data[row * stride : row * stride + width] = source_row[x : x + width]
        slices.append(bytes(data))

    return tuple(slices), tlut


def validate_mkt_n64_rev2(source: bytes) -> None:
    if len(source) != MKT_N64_REV2_SIZE:
        raise RomValidationError(
            f"expected a {MKT_N64_REV2_SIZE}-byte MKT N64 ROM, got {len(source)} bytes"
        )
    magic = int.from_bytes(source[:4], "big")
    if magic != N64_BIG_ENDIAN_MAGIC:
        raise RomValidationError(
            f"expected big-endian MKT .z64 magic 0x{N64_BIG_ENDIAN_MAGIC:08X}, got 0x{magic:08X}"
        )
    digest = _sha256(source)
    if digest != MKT_N64_REV2_SHA256:
        raise RomValidationError(
            "unsupported MKT donor: expected Mortal Kombat Trilogy (USA) Rev. 2 SHA-256 "
            + MKT_N64_REV2_SHA256
        )


def extract_toasty_assets(source: bytes) -> ToastyAssets:
    """Extract the runtime-confirmed Toasty visual/audio assets from MKT Rev. 2."""

    validate_mkt_n64_rev2(source)

    dictionary = source[TOASTY_DICT_ROM : TOASTY_DICT_ROM + TOASTY_DICT_SIZE]
    image_stream = source[
        TOASTY_IMAGE_ROM : TOASTY_IMAGE_ROM + TOASTY_IMAGE_COMPRESSED_SIZE
    ]
    source_palette = source[TOASTY_PALETTE_ROM : TOASTY_PALETTE_ROM + 0x80]
    if _sha256(dictionary) != EXPECTED_DICT_SHA256:
        raise RomValidationError("MKT Toasty dictionary guard failed")
    if _sha256(image_stream) != EXPECTED_IMAGE_STREAM_SHA256:
        raise RomValidationError("MKT Toasty image-stream guard failed")
    if _sha256(source_palette) != EXPECTED_PALETTE_SOURCE_SHA256:
        raise RomValidationError("MKT Toasty palette guard failed")

    decoded = _decode_dict64_final(image_stream, dictionary)
    if _sha256(decoded) != EXPECTED_IMAGE_DECODED_SHA256:
        raise RomValidationError("MKT Toasty image decode did not match the confirmed retail asset")
    visual_slices, palette_tlut = _build_visual_assets(decoded, source_palette)
    if _sha256(palette_tlut) != EXPECTED_TARGET_TLUT_SHA256:
        raise RomValidationError("MKT Toasty palette translation guard failed")

    ctl = zlib.decompress(
        source[MKT_CTL_COMP_ROM : MKT_CTL_COMP_ROM + MKT_CTL_COMP_SIZE],
        -15,
    )
    if len(ctl) != MKT_CTL_RAW_SIZE or _sha256(ctl) != EXPECTED_CTL_SHA256:
        raise RomValidationError("MKT Toasty audio control-bank guard failed")

    subpatch = ctl[DONOR_SUBPATCH_111_OFF : DONOR_SUBPATCH_111_OFF + 20]
    wave = ctl[DONOR_WAVE_77_OFF : DONOR_WAVE_77_OFF + 24]
    predictor = ctl[DONOR_PRED_77_OFF : DONOR_PRED_77_OFF + 264]
    sample = source[DONOR_SAMPLE_ROM : DONOR_SAMPLE_ROM + DONOR_SAMPLE_LEN]
    if subpatch != EXPECTED_SUBPATCH:
        raise RomValidationError("MKT Toasty subpatch guard failed")
    if wave != EXPECTED_WAVE:
        raise RomValidationError("MKT Toasty waveform guard failed")
    if _sha256(predictor) != EXPECTED_PRED_SHA256:
        raise RomValidationError("MKT Toasty predictor guard failed")
    if _sha256(sample) != EXPECTED_SAMPLE_SHA256:
        raise RomValidationError("MKT Toasty sample guard failed")

    return ToastyAssets(
        visual_slices=visual_slices,
        palette_tlut=palette_tlut,
        audio_subpatch=subpatch,
        audio_wave=wave,
        audio_predictor=predictor,
        audio_sample=sample,
    )
