#!/usr/bin/env python3
"""MKMSZR v57 PS1 Run recovery diagnostics.

This is deliberately NOT a POVBQ decoder and NOT a ROM builder.
The current PS1 POVBQ interpretation is rejected. This script only preserves
identity/structure guards so a future decoder investigation starts from the
correct donor bytes and Run script.
"""
from pathlib import Path
import hashlib
import zipfile

PS1_ZIP_SHA256 = "05fa703aefb3a265bb19ed2404215d84aa45bfe959f8d00881a11846ad91b39a"
ROBOT_BIN_SHA256 = "d5c2752c62179be1d118813d2cdae4c54d2f434cf303941c51529e9e6e4935d6"
ROBOT_DAT_SHA256 = "99c5ae8c98f10947172d9964e2d1649d28746060b113d61358a5699ec0bbedd0"
BIN_MEMBER = "PS1 - MKT (unpacked)/CODE/ROBOT.BIN"
DAT_MEMBER = "PS1 - MKT (unpacked)/CHARS1/ROBOT.DAT"
RUN_OFF = 0x140C


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def le16(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o+2], "little")


def le32(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o+4], "little")


def s16(b: bytes, o: int) -> int:
    return int.from_bytes(b[o:o+2], "little", signed=True)


def load_members(zip_path: Path):
    raw = zip_path.read_bytes()
    assert sha256(raw) == PS1_ZIP_SHA256, sha256(raw)
    with zipfile.ZipFile(zip_path) as z:
        rb = z.read(BIN_MEMBER)
        rd = z.read(DAT_MEMBER)
    assert sha256(rb) == ROBOT_BIN_SHA256, sha256(rb)
    assert sha256(rd) == ROBOT_DAT_SHA256, sha256(rd)
    return rb, rd


def descriptor(rd: bytes, index: int):
    # Current structural interpretation only; does not decode pixels.
    o = 8 + 12 * index
    first = le32(rd, o)
    typ = (first >> 24) & 0xFF
    data = first & 0xFFFFFF
    return {
        "index": index,
        "header_off": o,
        "data": data,
        "type": typ,
        "fileid": typ & 0x1F,
        "raw_width": rd[o+4],
        "padded_width": (rd[o+4] + 3) & ~3,
        "height": rd[o+5],
        "x": s16(rd, o+6),
        "y": s16(rd, o+8),
        "palette": le16(rd, o+10),
    }


def run_words(rb: bytes):
    # The historical v55/v56 work treated this as 19 dwords.
    return [le32(rb, RUN_OFF + 4*i) for i in range(19)]


def frame_ref_to_descriptor_index(v: int) -> int:
    # Guarded historical mapping used by the v55/v56 investigation.
    # Revalidate this if a future independent format source contradicts it.
    rel = v & 0xFFFFFF
    return (rel + 4 - 8) // 12


def main():
    root = Path(__file__).resolve().parent
    candidates = [
        root / "PS1 - MKT (unpacked).zip",
        Path("/mnt/data/PS1 - MKT (unpacked).zip"),
    ]
    zpath = next((p for p in candidates if p.exists()), None)
    if not zpath:
        raise SystemExit("PS1 - MKT (unpacked).zip not found")

    rb, rd = load_members(zpath)
    words = run_words(rb)
    refs = [v for v in words if (v & 0xFF000000) == 0x88000000]
    indices = [frame_ref_to_descriptor_index(v) for v in refs]

    print("PS1 donor identities: PASS")
    print(f"ROBOT.BIN +0x{RUN_OFF:X} words:")
    for i, v in enumerate(words):
        print(f"  {i:02d}: 0x{v:08X}")
    print("frame descriptor indices:", indices)
    assert indices == list(range(222, 234)), indices

    print("\nDescriptors 222..233:")
    for idx in indices:
        d = descriptor(rd, idx)
        print(
            f"  {idx}: data=0x{d['data']:06X} type=0x{d['type']:02X} "
            f"w={d['raw_width']} padded={d['padded_width']} h={d['height']} "
            f"x={d['x']} y={d['y']} pal={d['palette']}"
        )

    print("\nIMPORTANT:")
    print("  Structural guards passed. This does NOT validate the current POVBQ decoder.")
    print("  Do not build v57 until PS1 odd RBRUN1/3/5/7/9/11 decode coherently")
    print("  against their known-good N64 counterparts.")


if __name__ == "__main__":
    main()
