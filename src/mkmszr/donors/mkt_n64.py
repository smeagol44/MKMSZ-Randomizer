"""Donor extraction for Mortal Kombat Trilogy N64 USA Rev. 2."""

from __future__ import annotations

import hashlib
import zlib

from ..errors import RomValidationError
from ..patches.temple_intro_audio import MktAudioClip, TempleIntroAudioAssets
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

MKT_SUBPATCH_BASE = 0x06E0
MKT_WAVE_BASE = 0x2828
MKT_PRED_BASE = 0x4F48
MKT_TBL_BASE = 0x00AB4370
MKT_SSEQ_DEF_COMP_ROM = 0x00AA7090
MKT_SSEQ_DEF_COMP_SIZE = 0x07A6
MKT_SSEQ_DEF_RAW_SIZE = 0x2730
MKT_SSEQ_TRACK_BASE = 0x00AA7836
EXPECTED_SSEQ_DEF_SHA256 = (
    "6cdfcf946ba78f492aa731ee542aeca6faf34d9c61d51871565f23f87e59ef7e"
)

# key -> event, patch, subpatch, wave, event-track SHA, subpatch SHA,
# wave SHA, predictor SHA, sample length, sample SHA.
TEMPLE_AUDIO_PROFILES = {
    "friendship": (
        405, 225, 249, 251,
        "3de5cfba024da0ddbb6e95c948eea0cd2d3920e148d7d3663ce9efffa09c6480",
        "27906a1942204cef30361cc28c42b67e549d4c56364183b72eaaf8f3d1be5531",
        "6f64339492d1fcf286ecd0495a8a6e1b41c6f6bd8acac7c662c9fc205abfd04f",
        "992a9fd15fe392997db566f99a757d3defbe6bc2e422952fca3299c23e60cc37",
        0x0D14,
        "101e359820a2f06b3d6a317dc4806023ea1beaa404ecbab3721af21c53d7b8e3",
    ),
    "choose-your-destiny": (
        427, 365, 379, 347,
        "c8c466ffbb4ed610e6dcc0194cc9cb3345e977654392a2cef07112316e5685be",
        "e699567f1a494661bd81da34c561022da9d3e81e1104289140ee62c296dcbe05",
        "7a1b793f0e776d294a42c66f5cd768f718d6bde0c0ac1ebd597c0f02c7f38437",
        "c112e57369c1fb98f887287d111e8d06d9588a8a81a82ee3c79bb6f8fa09d813",
        0x1950,
        "9c04944d86d207643ee3db1a77ba5538ab4f4c94f250b8236deecb12b514702c",
    ),
    "excellent": (
        388, 255, 269, 264,
        "c4285638a2a1004570e9099b86e960791f7f8518ca1e7f0c24ef30bd191f5c96",
        "8a16a6fcd362caf67237f375981c1a72ed12808c639164483e3d59fb12ca73e4",
        "74bc21a7612f13ce023bee18902124ecee443d58d43da600a512ac717191487f",
        "6a28c578aef6e66f4ce4e5d55e787b50f284edd06f65d130ed32f506bb5a5307",
        0x0F54,
        "f20456f2345eae5d419c5762f4addf1f9a24c714042b5f103920a73fbc1f77f8",
    ),
    "superb": (
        354, 231, 254, 255,
        "9c6fabd4b085686821f614fb077a4eada91f3cc0b537a2b76424733c162ecdc0",
        "8cbdc9591b1d8faead44a35560d3e2407fefebf2d3bdf0357e9a514f352e1504",
        "ae29375017e9f255226382e3b5d9e997d58c4856ec79ed57cf7c274556338f79",
        "c81fb461e50946207d5bd419e1f43e14660573980c7aa298d3d7700d3d4e4cd8",
        0x0C72,
        "9cad9660994441b5be12fda50a1a1aafa34cc9c85c921cd3f8003cbe3ed5b4f0",
    ),
    "well-done": (
        355, 232, 255, 256,
        "866faf2d2bfa02cd493bb751831d546ede3798ab24414756af7c58e92cdb2be5",
        "330e7e7e15111a4a63d5a0e25aaf08a79448f2c2c6fe50f761b956fcd78d16c6",
        "c591a881bb69c2ad32f3598675b3346b0f78f3ce462483d73b44bdd5865c4f5e",
        "4853c7f52e719a9ef6e53da894ea8569e4c06334a422b354efcc0d250916473c",
        0x0D92,
        "ce11d623a1191c72f42c8ebc00cdaead57b423ebbae319b30c77c6aed36fc601",
    ),
    "liu-bike": (
        330, 86, 132, 177,
        "a5217b21ea12a31208320d6d7283abef8d5702b8287aed8046310c58d124db55",
        "45cbe8b97881926b1a3b628cdf253d667792e47377614496b46782fb4c88499d",
        "4fa0e32fbf6afb0d4da82c4e68cbf92a0f3cb279680b7c3ff26d0fb9b2b620b9",
        "5ee6f1c2f8ebb06d8d459a63f0047c50d41c0e6979ed648305f31efffd8f8460",
        0x1116,
        "362237e15956202c35a318f05723c512406ada9ba1ef0e6b04722faabd181d38",
    ),
    "raiden-bbb": (
        508, 416, 23, 391,
        "9177e881c80322d2fd8967168d41f3a59ff4a0fb79aae18745ec08438803654e",
        "f208d7aa26672b607300ffb80ef3a3c6ce02f3447a72d871f4f7f0c6897bd91b",
        "3c8325251322630efa97257909bcc43fa900b70891e34f42ef7d099e1e1107b2",
        "7c008693b7c469f666ef149a133fd059b1c753db4c1e6ddd950d3e3f627f3db3",
        0x1104,
        "c7d0caf60560505dc41f6f44cd727aa414a22ef840cf4c28f387f1307c8dddcc",
    ),
    "raiden-sss": (
        509, 417, 24, 392,
        "bb08d76054f07a17e4776a49119aa79d0f4cf151a175badde3325a1ad6ef48d9",
        "98fd0b4a589ebae0c0921da90d8ff4337874edc40b8a27efd4dadfa028f6b222",
        "5c5b7e8fec5b1034a4c0c4d6c30fc3aebaf4296d020e470aa163892b1b6ace65",
        "679a9cbe0237822b48bf20b0983501f4a4a924f51bb87a00582a2782245c508b",
        0x1248,
        "50ba8bc5d9946c9bef274aa4cb621a113b1b23d8a614d3530a313cc88291656f",
    ),
    "raiden-ttt": (
        510, 418, 25, 393,
        "c24f385593e04821ee3d844d9826a968fa09156bec92b2639d3b3e54637a49bb",
        "cb0ce1b2e378553f930e355d09f0bcd23c6ca09cd788708a193a3968d3e4f6ad",
        "f59cd497e7921aea115560c3cf3df53b278d8dcd6dabd90d9bf36ba13c851942",
        "7a17def7a4be8cf6ce8c689820347643fea8a92217a2137bedddfad31a41539a",
        0x0EB2,
        "c34d374e552047434438dfd850e4d9a652b7769efde58bdf098844808d1c0d21",
    ),
    "robot-run": (
        35, 89, 134, 157,
        "5b39ce3dac53f0f876c6c248336ed2af60f3135a730bbb799030fe401f894c11",
        "e9652a0d1268c3d8594f1fb3e3c7b92d383dc84338753979ca1da6df01d6f80a",
        "ae62a3052348ae42b36e8398521d08a40a4a37768146aba283ab59d0bed0184a",
        "fe254fd13384082246f533f29013fc05076cb62af9f6908b3665cef483972030",
        0x0BE2,
        "2191325d4a58f987929ec2cdd83e95b1937ec07d42cea0bbb484fa03c15cec59",
    ),
    "shao-laugh": (
        411, 250, 264, 263,
        "82801af41efce754e7ec82e780311afb7c43a816758a2bb1d4a975c94791026c",
        "36b5936f3f55c68f97167182b074d89f7c2ba5186edc74ba1fcbf8564bfe1458",
        "ac076df27ec6ff894101ea6774feef2aee0828efafaaa4b9902bfd449b26c532",
        "fbb9562b89e022549c3153543e762becde5530f27b1ab02c1167a158302a3c64",
        0x1A16,
        "477070e6cbcc7c37ae3a96496baf18c0cc556331f76e78f6bc0ce2a8b62af234",
    ),
}

EXPECTED_DICT_SHA256 = "dd467f1b389d8f1e83761062638748e4aec0e1f856900b8a24a299c07ff59b59"
EXPECTED_IMAGE_STREAM_SHA256 = "f78135df4dc0e8d7c1fe42cc3f3a921d162a3d6751a357390b64370e67736204"
EXPECTED_IMAGE_DECODED_SHA256 = "18eed9a06f82249cd7b3db3b83cb1cd0115df739ca77712fdc4e274413794736"
EXPECTED_PALETTE_SOURCE_SHA256 = "1e0864523ff24b957738682bd1e8f4d2354f87036dd908291b1e5e98393337dd"
EXPECTED_TARGET_TLUT_SHA256 = "687569e2c16520796b0f11ace50915827d50320e73ac15690f9e3bc5914e4a5b"
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

# Deterministic 16-color quantization confirmed in the accepted composition.
# Indices address the first-appearance palette of the donor's visible pixels.
CI4_PALETTE_SOURCES = (0, 15, 37, 10, 50, 1, 3, 40, 7, 51, 16, 47, 25, 45, 31, 41)
CI4_INDEX_MAP = (
    0, 5, 6, 6, 5, 10, 8, 8, 4, 8, 3, 9, 1, 10, 9, 1,
    10, 10, 12, 12, 10, 8, 9, 14, 12, 12, 7, 3, 10, 9, 10, 14,
    14, 14, 14, 3, 15, 2, 11, 10, 7, 15, 4, 9, 13, 13, 4, 11,
    9, 6, 4, 9, 6, 6, 4,
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

    if len(palette_order) != len(CI4_INDEX_MAP):
        raise ValueError("MKT Toasty visible palette differs from the confirmed 55 colors")
    remap = {pixel: CI4_INDEX_MAP[index] for index, pixel in enumerate(palette_order)}
    tlut = b"".join(
        source_palette[palette_order[index] * 2 : palette_order[index] * 2 + 2]
        for index in CI4_PALETTE_SOURCES
    )

    slices: list[bytes] = []
    for x, y, width, height in _PIECES:
        stride = (width + 31) & ~31
        data = bytearray(stride * height // 2)
        for row in range(height):
            source_row = visible[(y + row) * TOASTY_VISIBLE_WIDTH : (y + row + 1) * TOASTY_VISIBLE_WIDTH]
            for column in range(width):
                index = remap[source_row[x + column]]
                offset = row * (stride // 2) + column // 2
                data[offset] |= index << (4 if column % 2 == 0 else 0)
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


def extract_temple_intro_audio_assets(source: bytes) -> TempleIntroAudioAssets:
    """Extract only the approved seeded Temple-intro audio pool from MKT Rev. 2."""

    validate_mkt_n64_rev2(source)
    ctl = zlib.decompress(
        source[MKT_CTL_COMP_ROM : MKT_CTL_COMP_ROM + MKT_CTL_COMP_SIZE],
        -15,
    )
    if len(ctl) != MKT_CTL_RAW_SIZE or _sha256(ctl) != EXPECTED_CTL_SHA256:
        raise RomValidationError("MKT Temple audio control-bank guard failed")

    defs = zlib.decompress(
        source[
            MKT_SSEQ_DEF_COMP_ROM : MKT_SSEQ_DEF_COMP_ROM + MKT_SSEQ_DEF_COMP_SIZE
        ],
        -15,
    )
    if len(defs) != MKT_SSEQ_DEF_RAW_SIZE or _sha256(defs) != EXPECTED_SSEQ_DEF_SHA256:
        raise RomValidationError("MKT Temple audio SSEQ-definition guard failed")

    clips: list[MktAudioClip] = []
    for key, profile in TEMPLE_AUDIO_PROFILES.items():
        (
            event_id,
            expected_patch,
            expected_subpatch,
            expected_wave,
            event_sha,
            subpatch_sha,
            wave_sha,
            predictor_sha,
            expected_sample_len,
            sample_sha,
        ) = profile

        event_def = defs[event_id * 16 : (event_id + 1) * 16]
        event_len = int.from_bytes(event_def[4:8], "big")
        event_off = int.from_bytes(event_def[8:12], "big")
        event_track = zlib.decompress(
            source[MKT_SSEQ_TRACK_BASE + event_off :],
            -15,
        )[:event_len]
        if _sha256(event_track) != event_sha:
            raise RomValidationError(f"MKT Temple audio event guard failed: {key}")

        patch_id = int.from_bytes(event_track[0:4], "big")
        if patch_id != expected_patch:
            raise RomValidationError(f"MKT Temple audio patch ID changed: {key}")
        patch = ctl[patch_id * 4 : patch_id * 4 + 4]
        subpatch_id = int.from_bytes(patch[2:4], "big")
        if subpatch_id != expected_subpatch:
            raise RomValidationError(f"MKT Temple audio subpatch ID changed: {key}")

        subpatch = ctl[
            MKT_SUBPATCH_BASE + subpatch_id * 20 :
            MKT_SUBPATCH_BASE + (subpatch_id + 1) * 20
        ]
        if _sha256(subpatch) != subpatch_sha:
            raise RomValidationError(f"MKT Temple audio subpatch guard failed: {key}")
        wave_id = int.from_bytes(subpatch[10:12], "big")
        if wave_id != expected_wave:
            raise RomValidationError(f"MKT Temple audio waveform ID changed: {key}")

        wave = ctl[
            MKT_WAVE_BASE + wave_id * 24 :
            MKT_WAVE_BASE + (wave_id + 1) * 24
        ]
        if _sha256(wave) != wave_sha:
            raise RomValidationError(f"MKT Temple audio waveform guard failed: {key}")
        predictor = ctl[
            MKT_PRED_BASE + wave_id * 264 :
            MKT_PRED_BASE + (wave_id + 1) * 264
        ]
        if _sha256(predictor) != predictor_sha:
            raise RomValidationError(f"MKT Temple audio predictor guard failed: {key}")

        sample_start = MKT_TBL_BASE + int.from_bytes(wave[0:4], "big")
        sample_len = int.from_bytes(wave[4:8], "big")
        if sample_len != expected_sample_len:
            raise RomValidationError(f"MKT Temple audio sample length changed: {key}")
        sample = source[sample_start : sample_start + sample_len]
        if _sha256(sample) != sample_sha:
            raise RomValidationError(f"MKT Temple audio sample guard failed: {key}")

        clips.append(
            MktAudioClip(
                key=key,
                event_id=event_id,
                patch_id=patch_id,
                subpatch_id=subpatch_id,
                wave_id=wave_id,
                event_track=event_track,
                subpatch=subpatch,
                wave=wave,
                predictor=predictor,
                sample=sample,
            )
        )

    return TempleIntroAudioAssets(tuple(clips))
