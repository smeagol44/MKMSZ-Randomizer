"""Sektor build for MKMSZ: the importer's whole Sektor recipe as one function.

Mechanically derived from the proof builder
``Experimental/SektorTransplantBuilders/teleport/MKMSZR_build_sektor_teleport_v60.py`` (its
history is in that builder's description and the Wiki proof history), then extended in place:
v61 adds the donor's five flip poses and the generic pickup and grabbed-by-an-enemy recipes
(``common_moves``); v62 raises the combo knockback finishers' damage from 7 to 10 (owner). ``build`` is pinned by hash (``tests/test_fighter_swap.py`` checks
it when the ROMs are available). Inputs are the clean MKMSZ USA Rev. 0 ROM and the MKT USA
Rev. 2 N64 donor ROM; nothing from either is stored here.
"""

# ruff: noqa
# fmt: off
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
import bisect
import hashlib


def build(clean: bytes, mkt: bytes, *, fixed_va: int | None = None,
          link_va: int = 0xA01AF420) -> dict:
    """``{'rom': 32 MiB image with Sektor, 'manifest': {...}, 'log': [...]}``; a link
    pass (``link_va`` other than the default) returns only ``{'rom': ...}``.

    Each call (and each internal link pass) starts from the importer's default code
    generation state, as the proof builder did in a fresh process, so repeated builds in
    one process (tests, the web worker) give the same bytes."""

    from mkmszr.fighter_import import mips as _mips

    saved = _mips.DEFAULT_CACHED_CALLS
    _mips.DEFAULT_CACHED_CALLS = False
    try:
        return _build(clean, mkt, fixed_va=fixed_va, link_va=link_va)
    finally:
        _mips.DEFAULT_CACHED_CALLS = saved


def _build(clean: bytes, mkt: bytes, *, fixed_va: int | None, link_va: int) -> dict:

    _log_lines: list[str] = []

    def _log(*parts, **_kw) -> None:
        _log_lines.append(" ".join(str(p) for p in parts))

    assert hashlib.sha256(clean).hexdigest() == '9c18254abf6722b95aa782fcd310bd95f6bcf147da66beb77ce32ca90673ffc6'
    assert hashlib.sha256(mkt).hexdigest() == '30efdbe266dda8b8b12652a8d0a71b3b4bfec88bdf11ed12c219f5c4e1eaf7bb'



    MB = 0x8881C0
    ROBO_DICT = mkt[0x906A90:0x906B90]
    assert len(ROBO_DICT) == 0x100
    ORIG_FILE87_ROM = 0x748920
    CLEAN_SIZE = 0x459E0
    RR = 0xF40000
    TYPE_START = 0x14AC
    TYPE_END = 0x41684
    PALETTE_OFF = 0x4584C
    SAFE_V49 = 0x4E544
    ZERO_BLOCK = b'\0' * 8
    # Exact runtime-confirmed v53 native Sektor TLUT lower half.
    SEKTOR_PALETTE32 = bytes.fromhex(
        '0000defec63cb5baa95898f790b2843a88568014842f842d842b800880048003'
        'f7bdef7be739d6b5ce73bdefb5adad6ba52998c690848c638842842180008000'
    )
    assert len(SEKTOR_PALETTE32) == 64


    def be16(b, o): return int.from_bytes(b[o:o+2], 'big')
    def be32(b, o): return int.from_bytes(b[o:o+4], 'big')
    def put32(b, o, v): b[o:o+4] = int(v & 0xffffffff).to_bytes(4, 'big')
    def s16(v): return v - 0x10000 if v & 0x8000 else v
    def s32(v): return v - 0x100000000 if v & 0x80000000 else v
    def align4(v): return (v + 3) & ~3
    def align2(v): return (v + 1) & ~1

    def m32(rel): return be32(mkt, MB + rel)
    def is_donor_shape(rel):
        return isinstance(rel, int) and rel > 0 and MB + rel + 8 <= len(mkt) and m32(rel) == rel + 8 and m32(rel + 4) == 0


    # MKT mechanical arm has its own 8-color MECARM_P palette. Convert the donor
    # RGBA5551 colors into MKMSZ's A1BGR555 color space, then bind them to the closest
    # entries already present in the runtime-confirmed native Sektor TLUT.
    MECARM_RGBA5551=[0x07C0,0xD6B9,0xB5B1,0x94A9,0x6B5F,0x4215,0x294F,0x18CB]
    TARGET_TLUT=[int.from_bytes(SEKTOR_PALETTE32[i:i+2],'big') for i in range(0,64,2)]
    def target_rgb(v): return (v&31,(v>>5)&31,(v>>10)&31)
    def rgba5551_to_target(v):
        r=(v>>11)&31; g=(v>>6)&31; b=(v>>1)&31; a=v&1
        return (a<<15)|(b<<10)|(g<<5)|r
    ARM_TO_SEKTOR={0:0}
    for i,v in enumerate(MECARM_RGBA5551[1:],1):
        c=target_rgb(rgba5551_to_target(v))
        ARM_TO_SEKTOR[i]=min(range(1,32),key=lambda j:sum((a-b)**2 for a,b in zip(c,target_rgb(TARGET_TLUT[j]))))
    assert ARM_TO_SEKTOR=={0:0,1:17,2:19,3:20,4:22,5:24,6:25,7:26}


    # ---- Body (milestone 1): the generic builder from Sektor's description ----------------------
    # Sektor's frozen legacy adds its move frames (combo, throw arm composites, teleport, chest)
    # and its combo and throw script edits (fighter_import.body_build.Extras).
    from mkmszr.fighter_import import body_build as _bb, description as _desc
    SEKTOR = _desc.load('sektor')
    _donorb = _bb.Donor(mkt, SEKTOR.donor_fighter_id)
    assert _donorb.base == MB and _donorb.dictionary == ROBO_DICT
    def donor_frame(rel): return _donorb.frame(rel)
    def visible_rows(fr): return _bb.visible_rows(fr)
    def composite(body, arm): return _bb.composite(body, arm, ARM_TO_SEKTOR, codec='flattened-22+15')

    # New v54 visuals.
    RUN_RELS=[0x2708,0x271C,0x2730,0x2744,0x2758,0x276C]  # RBRUN1,3,5,7,9,11
    assert RUN_RELS == _donorb.frames(SEKTOR.body.run_slot)
    COMBO_RELS=[0x1C0C+i*0x14 for i in range(10)]            # RBELBOCOMBO1..10
    BODY_REL=0x22EC                                           # RBSHOLDER4
    ARM_RELS=[0x2318,0x2340,0x237C,0x2390,0x23B8,0x23CC,0x2408]  # seven sampled poses across Sektor's mechanical-arm arc
    TELE_RELS=[0x2F08,0x2B48,0x2B5C,0x2B70,0x2B84]  # teleport: last frame of donor slot 0x0D + secondary slot 3
    # v26: chest open frames (robot secondary slot 0: RBCHEST1, RBCHEST2) for the rocket.
    from mkmszr.fighter_import.actions import robo_zap as _zap0
    CHEST_RELS=list(_zap0.CHEST_FRAMES)
    # v61: the donor's flip poses (MKT table 0 slot 0x47, phase 1) for the generic grabbed recipe.
    FLIP_RELS = _donorb.phase(0x47)
    assert FLIP_RELS == [0x2588, 0x259C, 0x25B0, 0x25C4, 0x25D8], [hex(x) for x in FLIP_RELS]
    new_frames={r:donor_frame(r) for r in COMBO_RELS+[BODY_REL]+ARM_RELS+TELE_RELS+CHEST_RELS}
    assert [(new_frames[r]['w'],new_frames[r]['h'],new_frames[r]['x'],new_frames[r]['y']) for r in CHEST_RELS]==[(46,115,19,-5),(47,113,20,-7)]
    THROW_KEYS=[('throw-composite',r) for r in ARM_RELS]
    throw_frames={k:composite(new_frames[BODY_REL],new_frames[k[1]]) for k in THROW_KEYS}
    assert (throw_frames[('throw-composite',0x23B8)]['w'],throw_frames[('throw-composite',0x23B8)]['h'],throw_frames[('throw-composite',0x23B8)]['x'],throw_frames[('throw-composite',0x23B8)]['y'])==(114,115,88,-5)
    # v04: the only generated asset is a transparent frame; sink/emerge use descriptor-only aliases
    # of resident frames (anchor shifted, image shared), emitted in the teleport section.
    EMPTY_KEY=('empty',0)
    DERIVED_KEYS=[EMPTY_KEY]
    _extra_frames={r:new_frames[r] for r in COMBO_RELS+TELE_RELS+CHEST_RELS}
    _extra_frames.update(throw_frames)
    _extra_frames[EMPTY_KEY]=dict(w=4,h=2,x=0,y=0,stride=4,eh=2,padded=bytes(8),blocks=_bb.make_blocks(bytes(8),4,2),codec='derived')

    # Clean-derived ROM + v53 selector/logo convenience, no helper and stock arena.
    rom=bytearray(clean)
    def words_bytes(vals): return b''.join(int(v&0xffffffff).to_bytes(4,'big') for v in vals)
    def jal(va): return 0x0C000000|((va>>2)&0x03ffffff)
    DEBUG_MENU_VA=0x8000D0B8; A_ROUTE_JAL_ROM=0xE028; WRAP_LAST_ROM=0xDD60; COUNT_ROM=0xDD64
    MENU_TABLE_ROM=0x9B7DC; SELECTION_LOAD_ROM=0x15CD0; MAPPER_ROM=0x9A700; MAPPER_VA=0x80099B00
    ORIGINAL_MENU_POINTERS=(0x800AA034,0x800AA02C,0x800AA024,0x800AA01C,0x800AA014,0x800AA00C,0x800AA004,0x800A9FF4,0x800A9FEC,0x800A9FE0,0x800A9FD0,0)
    SAFE_MENU_POINTERS=(0x800AA034,0x800AA02C,0x800AA024,0x800AA01C,0x800AA014,0x800AA00C,0x800A9FEC,0x800A9FE0,0,0,0,0)
    MAPPER_WITH_SKIP=bytes.fromhex('3C03800C 8C6311E0 2C610006 50200001 24630002 3C028029 03E00008 A0441C0C')
    assert be32(rom,A_ROUTE_JAL_ROM)==0x0C00A0C3 and be32(rom,WRAP_LAST_ROM)==0x2414000A and be32(rom,COUNT_ROM)==0x2A82000B
    assert bytes(rom[MENU_TABLE_ROM:MENU_TABLE_ROM+48])==words_bytes(ORIGINAL_MENU_POINTERS)
    put32(rom,A_ROUTE_JAL_ROM,jal(DEBUG_MENU_VA)); put32(rom,WRAP_LAST_ROM,0x24140007); put32(rom,COUNT_ROM,0x2A820008)
    rom[MENU_TABLE_ROM:MENU_TABLE_ROM+48]=words_bytes(SAFE_MENU_POINTERS)
    put32(rom,SELECTION_LOAD_ROM,jal(MAPPER_VA)); put32(rom,SELECTION_LOAD_ROM+4,0)
    rom[MAPPER_ROM:MAPPER_ROM+len(MAPPER_WITH_SKIP)]=MAPPER_WITH_SKIP
    BOOT=0x7A3F4
    assert bytes(rom[BOOT:BOOT+24])==bytes.fromhex('0C01F113 00000000 0C01F143 00000000 0C018576 24040080')
    put32(rom,BOOT,0x10000003)
    assert bytes(rom[0x1C9A0:0x1C9A8])==clean[0x1C9A0:0x1C9A8] and be32(rom,0x66F64)==0x2442F420
    assert bytes(rom[0xA5154:0xA5160])==bytes(12) and bytes(rom[0x9AD84:0x9ADD4])==bytes(0x50)
    assert set(rom[0xF10000:0xF10400])=={0xFF}

    # Elbow/full combo (Sektor's combo presentation): all four MKMSZ native segments (3/2/3/5 visuals) and zeros.
    COMBO_TARGET=0x5E0
    combo_visual_pos=[0,1,2,4,5,7,8,9,11,12,13,14,15]
    combo_seq=[0,1,2,1,0,3,4,5,6,7,8,9,8]  # 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9
    def _combo_hook(b):
        words=[b.f32(COMBO_TARGET+4*i) for i in range(17)]
        assert [i for i,v in enumerate(words) if v==0]==[3,6,10,16]
        for pos,ix in zip(combo_visual_pos,combo_seq): words[pos]=b.shape_map[COMBO_RELS[ix]]
        assert be32(b.file,0x10*4)==COMBO_TARGET
        return {COMBO_TARGET+4*i: v for i, v in enumerate(words)}
    # Throw: the actual MKMSZ a_throw body is exactly 12 words / 9 visual shapes in three zero-terminated parts.
    # The command-heavy words beginning at +0x928 are a separate adjacent reaction/flip animation block and must not be rewritten as Throw.
    THROW_TARGET=0x8F8
    throw_visual_pos=[0,1,3,4,5,6,7,9,10]
    _throw_state={}
    def _throw_hook(b):
        throw_stance=b.shape_map[0x17A8]  # RBSTANCE7; retail Sektor throw itself enters from this already-resident pose.
        throw_shapes={r:b.shape_map[('throw-composite',r)] for r in ARM_RELS}
        # Seven genuine mechanical-arm phases plus the stance at entry/exit, shifted right one visual slot (v55).
        seq={0:throw_stance,1:throw_stance,3:throw_shapes[0x2318],4:throw_shapes[0x2340],5:throw_shapes[0x237C],
             6:throw_shapes[0x2390],7:throw_shapes[0x23B8],9:throw_shapes[0x23CC],10:throw_shapes[0x2408]}
        _throw_state.update(stance=throw_stance, shapes=throw_shapes, sequence=seq)
        for i in range(12):
            if i not in throw_visual_pos: assert be32(b.file,THROW_TARGET+4*i)==b.f32(THROW_TARGET+4*i)
        assert be32(b.file,0x23*4)==THROW_TARGET
        out={THROW_TARGET+4*pos: seq[pos] for pos in throw_visual_pos}
        for p in (14,17,20,23,26,29):
            assert THROW_TARGET+4*p not in b.owned and THROW_TARGET+4*p not in out
        return out
    _extras=_bb.Extras(frames=_extra_frames,
                       sets={'combo':COMBO_RELS,'throw':THROW_KEYS,'teleport':TELE_RELS,'chest':CHEST_RELS,'empty':DERIVED_KEYS},
                       key_order=['combo','throw','teleport','chest','flipped','empty'],
                       groups=[['throw'],['combo','teleport','chest','flipped','empty']],
                       script_hooks=[_combo_hook,_throw_hook])
    BODY=_bb.build_body(SEKTOR, clean, mkt, _extras, rom=rom)
    for _line in BODY.log: _log(_line)
    shape_map, frame_cache, frame_model, all_keys, groups = BODY.shape_map, BODY.frame_cache, BODY.frame_model, BODY.all_keys, BODY.groups
    slot_cfg, translated, script_targets = BODY.slot_cfg, BODY.translated, BODY.script_targets
    clean_f87, stock_shape_set = BODY.clean_file, BODY.stock_shape_set
    def f32(off): return BODY.f32(off)
    NEW_END, CHAIN_START = BODY.new_end, BODY.chain_start
    run_words, push_words, fallback_positions = BODY.run_words, BODY.push_words, BODY.fallback_positions
    throw_stance, throw_shapes, throw_sequence = _throw_state['stance'], _throw_state['shapes'], _throw_state['sequence']
    old_shapes=BODY.inherited
    assert len(old_shapes)==129 and len(groups)==64 and len(all_keys)==165  # v61: + 5 flip poses
    assert slot_cfg[0x0B]['words'] == [0x1A54,0x1A68,0x1A7C,0x1A90,5,0x1AA4,0,0x1A90,0]
    assert slot_cfg[0x14]['words'] == [0x1E28,0x1E3C,0x1E50,6,1,0x1E64,0x1E78,0,0x1E8C,0x1EA0,0x1EB4,0]
    assert slot_cfg[0x20]['words'] == [0x21AC,0x21C0,0x21D4,0x21E8,0x21AC,0x21FC,0x2210,0,0x21AC,0x21C0,0x21D4,0x21E8,0x21AC,0x21FC,0x2210,1,0x754]
    assert all_keys[len(old_shapes):len(old_shapes)+len(RUN_RELS)] == RUN_RELS
    assert [k for k in all_keys if k in FLIP_RELS] == FLIP_RELS
    patterns_count, TABLE_BYTES, STREAM_BYTES = BODY.encoded.patterns, len(BODY.encoded.table), BODY.encoded.stream_bytes

    # The body file into the staging location (file table entry 0x87).
    assert set(rom[RR:RR+CLEAN_SIZE])=={0xFF}
    rom[RR:RR+len(BODY.file)]=BODY.file
    put32(rom,0xA5664,RR); put32(rom,0xA566C,0)
    assert NEW_END==align4(CLEAN_SIZE) or set(clean[RR+CLEAN_SIZE:RR+NEW_END])=={0xFF}
    put32(rom,0xA5668,RR+NEW_END)

    # Existing v53 semantic guards remain true under relocation.
    assert translated[0x00]==[shape_map[x] for x in (0x1768,0x1780,0x1794,0x17A8,0x17BC)]+[1,0x2EC]
    assert translated[0x05]==[shape_map[0x1928],shape_map[0x193C],2,shape_map[0x1928],shape_map[0x1914],0]
    assert translated[0x0B][4]==5 and translated[0x14][3:5]==[6,0]
    assert translated[0x1A][-2:]==[1,script_targets[0x1A]+4]
    assert translated[0x1B][-2:]==[1,script_targets[0x1B]+4]
    assert translated[0x20][-2:]==[1,script_targets[0x20]+0x20]
    assert script_targets[0x09]+40==0x7C0 and script_targets[0x1B]+32<=0x7E8 and script_targets[0x20]+68<=0x684
    assert script_targets[0x12]+52<=0x84C and script_targets[0x1A]+32<=0x504
    assert be32(rom,RR+0x104+0x27*4)==0x1B0
    assert len(run_words)==8 and len(set(run_words[:6]))==6
    for slot in (0x0D,0x24,0x25): assert be32(rom,RR+slot*4)==f32(slot*4)
    for k in THROW_KEYS:
        assert throw_frames[k]['padded']!=new_frames[BODY_REL]['padded']
    assert ARM_RELS==[0x2318,0x2340,0x237C,0x2390,0x23B8,0x23CC,0x2408]
    assert bytes(rom[0x2F7A0:0x2F7A4]) == bytes.fromhex('24040003')     # v03 Run cadence (rate from the description)

    # Helper remains absent and stock arena restored.
    assert bytes(rom[0x1C9A0:0x1C9A8])==clean[0x1C9A0:0x1C9A8] and be32(rom,0x66F64)==0x2442F420
    assert bytes(rom[0xA5154:0xA5160])==bytes(12) and bytes(rom[0x9AD84:0x9ADD4])==bytes(0x50)
    assert set(rom[0xF10000:0xF10400])=={0xFF}

    # ============================================================================
    # Teleport v01 section (appended to the 16-colour/4-bpp v05-equivalent build).
    # Donor: MKT Rev. 2 Sektor F,F+LK -> do_body_propell(8) -> 0x80048368.
    # Host lifecycle: exact Runtime-confirmed Reverse Elbow v6 infrastructure
    # (file-0x1B raw payload at 0x801AF420, uncached entry, selector-3 bridge,
    # lock 0x800BF308, exit 0x800328FC + v6 non-returning fallback).
    # Disposable proof only. Silent (no SFX).
    # ============================================================================

    # ---- extra teleport scripts appended to file 0x87 ---------------------------
    TELE_POSE_REL = 0x2F08                       # last frame of donor slot 0x0D
    TELE_DROP_RELS = [0x2B48, 0x2B5C, 0x2B70, 0x2B70, 0x2B84]   # donor secondary slot 3
    LAND_RELS = [0x1EDC, 0x1EC8]                 # donor slot 0x16 frames [1], [0] (already resident)
    for r in [TELE_POSE_REL] + TELE_DROP_RELS + LAND_RELS + DERIVED_KEYS:
        assert r in shape_map, r

    SCRIPT_BASE = CHAIN_START                    # v47 (was align4(NEW_END))
    scripts = {}
    cur = SCRIPT_BASE
    def emit(name, words_):
        nonlocal cur
        scripts[name] = cur
        for i, v in enumerate(words_):
            put32(rom, RR + cur + 4 * i, v)
        cur += 4 * len(words_)
    # Each script holds its last frame with a self-jump so later advances cannot run past it.
    DROP_RATE = 3                     # donor rate 5 @60 Hz ~= 2.5 target ticks
    # Descriptor-only aliases: shape [sub, 0] + sub [image, w|h, x|y'] sharing the base image.
    # Donor anchor convention: feet = h - anchor_y; moving the image down by d is anchor_y - d.
    # MKT sinks the sprite down over the floor and off the bottom of the screen (no floor clip).
    SINK_DEPTHS = [13, 28, 46, 66, 89, 113, 140, 170, 202, 236, 273, 311]   # donor 5.95 px/t60 + 0.584 px/t60^2, every 2 donor ticks
    EMERGE_DEPTHS = [311, 236, 170, 113, 66, 28]                              # rises back over ~the donor emerge time
    def alias(base_key, d):
        nonlocal cur
        shape = cur; sub = shape + 8; base_sub = shape_map[base_key] + 8
        put32(rom, RR + shape, sub); put32(rom, RR + shape + 4, 0)
        rom[RR + sub:RR + sub + 10] = rom[RR + base_sub:RR + base_sub + 10]          # image, w, h, x
        y = int.from_bytes(rom[RR + base_sub + 10:RR + base_sub + 12], 'big', signed=True)
        rom[RR + sub + 10:RR + sub + 12] = ((y - d) & 0xFFFF).to_bytes(2, 'big')
        cur += 20
        return shape
    sink_alias = [alias(TELE_POSE_REL, d) for d in SINK_DEPTHS]
    emerge_alias = [alias(TELE_DROP_RELS[0], d) for d in EMERGE_DEPTHS]
    sink = cur
    sink_words = [shape_map[TELE_POSE_REL]] + sink_alias + [shape_map[EMPTY_KEY]]
    emit('SINK', sink_words + [1, sink + 4 * (len(sink_words) - 1)])      # holds the transparent frame
    SINK_STEPS = len(sink_words) - 1
    drop = cur
    emerge_words = emerge_alias + [shape_map[TELE_DROP_RELS[0]]]
    EMERGE_STEPS = len(emerge_words) - 1                                   # last step shows the full first rise frame
    rise_words = [shape_map[r] for r in TELE_DROP_RELS[1:]]
    drop_words = emerge_words + [6, 1, DROP_RATE] + rise_words             # callback 1: set rate for the rise
    emit('DROP', drop_words + [1, drop + 4 * (len(drop_words) - 1)])
    landa = cur
    emit('LANDA', [shape_map[LAND_RELS[0]], 1, landa])
    landb = cur
    emit('LANDB', [shape_map[LAND_RELS[1]], 1, landb])
    TELE_END = cur
    NEW_END_TELE = align4(TELE_END)
    assert NEW_END_TELE <= TYPE_END, (hex(NEW_END_TELE), hex(TYPE_END))
    CHAIN_END = NEW_END_TELE                      # v47: chain cursor; the file end (0xA5668) stays stock

    # ---- v21: rocket art + palette on the straight projectile (R2 step 2a) ----
    # Donor ROCKETD1 (MKT robot frame +0x2668: 39x9, anchor (26,3), codec 16) and ROCKET_P (retail record
    # 0x0BC3AC, 16 colours) as a raw/type-0 image + 64-entry palette record appended to file 0x87. The Zap
    # script's projectile frames point at it; two token-0x0B hooks (fighter_import.projectile, v87/v89 design)
    # bind ROCKET_P and pre-load the texture slot before publication, for this projectile only.
    # v23: the pre-load no longer calls the allocating 0x8001BF70 (v21 per-shot storage leak; v22's fixed
    # 368-byte buffer was overrun by the up/down Ice stance frame -> hang). It runs the render pass's
    # deferred slot upload early, into the slot's stock storage.
    from mkmszr.fighter_import import MktRom as _MktRom, projectile as _proj
    from mkmszr.fighter_import.mips import Assembler as _Asm
    _donor = _MktRom(mkt)
    (_part,) = _donor.frame_parts(7, 0x2668)
    assert (_part.width, _part.height, _part.anchor_x, _part.anchor_y, _part.codec) == (39, 9, 26, 3, 16)
    _heap = _donor.heap_bytes(7)
    _indices, _used = _proj.decode_mkt_codec16(_heap[_part.image:])
    assert _used == 130 and len(_indices) == 9 * 40
    ROCKET_P_ROM = 0x0BC3AC
    assert int.from_bytes(mkt[ROCKET_P_ROM:ROCKET_P_ROM + 4], 'big') == 16
    _pal = tuple(_proj.mkt_color_to_host(int.from_bytes(mkt[ROCKET_P_ROM + 4 + 2 * i:ROCKET_P_ROM + 6 + 2 * i], 'big')) for i in range(16))
    ROCKET = _proj.ProjectileArt(39, 9, 26, 3, _indices, _pal)
    _end = CHAIN_END
    ROCKET_IMAGE_OFF = _end
    ROCKET_PAL_OFF = (ROCKET_IMAGE_OFF + len(ROCKET.raw_image()) + 3) & ~3
    ROCKET_PAL_SRC = ROCKET_PAL_OFF + 4
    ROCKET_SHAPE_OFF = (ROCKET_PAL_OFF + len(ROCKET.palette_record()) + 3) & ~3
    ROCKET_DESC_OFF = ROCKET_SHAPE_OFF + 8
    _new_end = ROCKET_DESC_OFF + 12
    assert _new_end <= TYPE_END and set(rom[RR + _end:RR + _new_end]) == {0xFF}
    rom[RR + ROCKET_IMAGE_OFF:RR + ROCKET_IMAGE_OFF + len(ROCKET.raw_image())] = ROCKET.raw_image()
    rom[RR + ROCKET_PAL_OFF:RR + ROCKET_PAL_OFF + len(ROCKET.palette_record())] = ROCKET.palette_record()
    put32(rom, RR + ROCKET_SHAPE_OFF, ROCKET_DESC_OFF); put32(rom, RR + ROCKET_SHAPE_OFF + 4, 0)
    put32(rom, RR + ROCKET_DESC_OFF, ROCKET_IMAGE_OFF)
    put32(rom, RR + ROCKET_DESC_OFF + 4, (ROCKET.width << 16) | ROCKET.height)
    put32(rom, RR + ROCKET_DESC_OFF + 8, ((ROCKET.anchor_x & 0xFFFF) << 16) | (ROCKET.anchor_y & 0xFFFF))
    CHAIN_END = _new_end
    # v27 (R2 step 2d): second flat-rocket frame ROCKETD2 (+0x267C, same ROCKET_P) and the flight loop
    # script: MKT anirate 3 (60 Hz) resampled to one frame per host tick, entered at the flight child's phase.
    from mkmszr.fighter_import.actions import robo_zap as _zapf
    (_part2,) = _donor.frame_parts(7, _zapf.ROCKET_FRAMES[1])
    assert (_part2.width, _part2.height, _part2.anchor_x, _part2.anchor_y, _part2.codec) == (42, 10, 30, 4, 16)
    _indices2, _ = _proj.decode_mkt_codec16(_heap[_part2.image:])
    assert len(_indices2) == 10 * 44 and max(_indices2) < 16
    ROCKET2 = _proj.ProjectileArt(42, 10, 30, 4, _indices2, _pal)
    ROCKET2_IMAGE_OFF = _new_end
    ROCKET2_SHAPE_OFF = (ROCKET2_IMAGE_OFF + len(ROCKET2.raw_image()) + 3) & ~3
    ROCKET2_DESC_OFF = ROCKET2_SHAPE_OFF + 8
    FLIGHT_LOOP_OFF = ROCKET2_DESC_OFF + 12
    _cycle = _zapf.flight_frame_cycle((ROCKET_SHAPE_OFF, ROCKET2_SHAPE_OFF))
    assert _cycle == [ROCKET_SHAPE_OFF, ROCKET_SHAPE_OFF, ROCKET2_SHAPE_OFF, ROCKET_SHAPE_OFF, ROCKET2_SHAPE_OFF, ROCKET2_SHAPE_OFF]
    _loop_words = _cycle + [1, FLIGHT_LOOP_OFF]
    FLIGHT_ENTRY_OFF = FLIGHT_LOOP_OFF + 4 * (_zapf.CHILD_START_TICKS % len(_cycle))
    _new_end2 = FLIGHT_LOOP_OFF + 4 * len(_loop_words)
    assert _new_end2 <= TYPE_END and set(rom[RR + _new_end:RR + _new_end2]) == {0xFF}
    rom[RR + ROCKET2_IMAGE_OFF:RR + ROCKET2_IMAGE_OFF + len(ROCKET2.raw_image())] = ROCKET2.raw_image()
    put32(rom, RR + ROCKET2_SHAPE_OFF, ROCKET2_DESC_OFF); put32(rom, RR + ROCKET2_SHAPE_OFF + 4, 0)
    put32(rom, RR + ROCKET2_DESC_OFF, ROCKET2_IMAGE_OFF)
    put32(rom, RR + ROCKET2_DESC_OFF + 4, (ROCKET2.width << 16) | ROCKET2.height)
    put32(rom, RR + ROCKET2_DESC_OFF + 8, ((ROCKET2.anchor_x & 0xFFFF) << 16) | (ROCKET2.anchor_y & 0xFFFF))
    for _i, _w in enumerate(_loop_words):
        put32(rom, RR + FLIGHT_LOOP_OFF + 4 * _i, _w)
    CHAIN_END = _new_end2
    # v35 (R2 step 4): MKT rocket smoke puff (raw) and explosion (type 4) + palettes + frame scripts.
    from mkmszr.fighter_import import effects as _fx
    _fx_dict = mkt[slice(*_donor.dictionary(7))]
    assert _fx_dict == ROBO_DICT
    SMOKE = _zapf.smoke_art(mkt, _fx_dict)
    EXPLOSION = _zapf.explosion_art(mkt, _fx_dict)
    SMOKE_PLACED = _fx.layout(SMOKE, _new_end2)
    EXPLOSION_PLACED = _fx.layout(EXPLOSION, SMOKE_PLACED.end)
    _new_end3 = EXPLOSION_PLACED.end
    for _placed, _art in ((SMOKE_PLACED, SMOKE), (EXPLOSION_PLACED, EXPLOSION)):   # v39: no slot override
        for _i in range(len(_art.frames)):
            _desc = be32(_placed.data, be32(_placed.data, _placed.script + 4 * _i - _placed.offset) - _placed.offset)
            assert be32(_placed.data, _desc - 4 - _placed.offset) == 0
    assert _new_end3 <= TYPE_END and set(rom[RR + _new_end2:RR + _new_end3]) == {0xFF}
    for _placed in (SMOKE_PLACED, EXPLOSION_PLACED):
        rom[RR + _placed.offset:RR + _placed.end] = _placed.data
    CHAIN_END = _new_end3
    # v42 (R3): heat-seeking rocket art. Direction parts 1-3 and 5-7 of the rocket animation (robot heap 0x1300;
    # parts 4/8 are the level ROCKETD1/D2 already in the file) drawn with ROCKET_P, one resampled loop per
    # direction, and the crosshair (heap descriptor 0x2C64, palette 0x800BC3D0) as an effect.
    from mkmszr.fighter_import.actions import robo_tracker as _trk
    _dirs = _trk.direction_frames(_heap, ROBO_DICT)
    assert [(f.width, f.height) for f in _dirs[3]] == [(39, 9), (42, 10)] and _dirs[7] == _dirs[3]
    assert all(max(f.indices) < 16 for part in _dirs for f in part)
    _new_parts = [k for k in range(8) if k not in (3, 7)]
    _dir_data, _dir_shapes = _fx.layout_shapes([f for k in _new_parts for f in _dirs[k]], _new_end3)
    _at = _new_end3 + len(_dir_data)
    TRK_LOOPS = []
    _loop_blobs = bytearray()
    for _k in range(8):
        if _k in (3, 7):
            TRK_LOOPS.append(FLIGHT_LOOP_OFF)
            continue
        _i = _new_parts.index(_k)
        _cyc = _zapf.flight_frame_cycle((_dir_shapes[2 * _i], _dir_shapes[2 * _i + 1]))
        _loop_at = _at + len(_loop_blobs)
        for _w in _cyc + [1, _loop_at]:
            _loop_blobs += _w.to_bytes(4, 'big')
        TRK_LOOPS.append(_loop_at)
    TARGET = _trk.target_art(mkt, _heap, ROBO_DICT)
    assert (TARGET.frames[0].width, TARGET.frames[0].height, len(TARGET.palette)) == (30, 26, 8)
    TARGET_PLACED = _fx.layout(TARGET, _at + len(_loop_blobs))
    _new_end4 = TARGET_PLACED.end
    assert _new_end4 <= TYPE_END and set(rom[RR + _new_end3:RR + _new_end4]) == {0xFF}
    rom[RR + _new_end3:RR + _at] = _dir_data
    rom[RR + _at:RR + _at + len(_loop_blobs)] = _loop_blobs
    rom[RR + TARGET_PLACED.offset:RR + _new_end4] = TARGET_PLACED.data
    CHAIN_END = _new_end4
    assert be32(rom, 0xA5668) - RR == NEW_END == 0x459E0   # v47: stock file size
    _log('V47_CHAIN', hex(CHAIN_START), hex(CHAIN_END), 'slack left', hex(TYPE_END - CHAIN_END))
    _log('TRACKER_ART', 'frames', hex(_new_end3), hex(len(_dir_data)), 'loops', [hex(x) for x in TRK_LOOPS],
          'target', hex(TARGET_PLACED.offset), 'file87 end', hex(_new_end4), 'headroom', hex(SAFE_V49 - _new_end4))
    _log('EFFECTS', 'smoke', hex(SMOKE_PLACED.offset), hex(len(SMOKE_PLACED.data)), SMOKE.slot_size,
          'explosion', hex(EXPLOSION_PLACED.offset), hex(len(EXPLOSION_PLACED.data)), EXPLOSION.slot_size,
          'file87 end', hex(_new_end3), 'headroom', hex(SAFE_V49 - _new_end3))
    _log('ROCKET_FLIGHT', 'D2 image', hex(ROCKET2_IMAGE_OFF), 'shape', hex(ROCKET2_SHAPE_OFF), 'loop', hex(FLIGHT_LOOP_OFF),
          [hex(w) for w in _loop_words], 'entry', hex(FLIGHT_ENTRY_OFF), 'file87 end', hex(_new_end2))


    # ---- v19: action code from the importer library (src/mkmszr/fighter_import) ----
    # The teleport adapter, sound player and descriptor condition are now assembled by
    # mkmszr.fighter_import.actions.robo_teleport on the host primitive library; with these
    # parameters the payload is byte-identical to v18 (asserted below).
    from mkmszr.fighter_import.actions import robo_teleport as _rt

    PAYLOAD_VA = link_va   # v48: link passes relink the blob higher
    V48_LINK_PASS = PAYLOAD_VA != 0xA01AF420
    PAYLOAD_LIMIT = 0x4000                        # v29: arena 0x801AF420..0x801B3420 = production's Runtime-confirmed 16 KiB floor
    # (v20-v28: 0x1000). Static audit: no clean-ROM code addresses [0x801AF420,0x801B3420) except the two heap-base
    # sites this reservation patches (0x66F64, 0x66FE8); the range is allocator heap in the clean game.
    ARENA_END = 0x801AF420 + PAYLOAD_LIMIT
    _ARENA_LO = f'{(ARENA_END & 0xFFFF):04x}'
    STRIKE_WORDS = (0x0049FFF7, 0x00490057, 0x08021803, 0x00010E02)   # stock uppercut reaction/aux/trailer; damage 0x18 / chip 3 (v08)
    TELE_EVENT = 335                             # isolated host chain carrying MKT event 0x104 (v09)
    _params = _rt.TeleportParams(
        scripts=_rt.TeleportScripts(sink=scripts['SINK'], drop=scripts['DROP'], land_a=scripts['LANDA'],
                                    land_b=scripts['LANDB'], sink_steps=SINK_STEPS, emerge_steps=EMERGE_STEPS),
        strike_words=STRIKE_WORDS, sound_event=TELE_EVENT)
    # The library still reproduces the v18 teleport exactly with the v18 parameters (checked below);
    # v25 builds with emerge_on_floor: reappear on the target's floor rather than at its current height.
    from dataclasses import replace as _replace
    # v47: the v18 check uses v18's script offsets (after the old file end, not in the slack).
    _v18_shift = CHAIN_START - align4(NEW_END)
    _v18_params = _replace(_params, scripts=_replace(_params.scripts, sink=scripts['SINK'] - _v18_shift,
                           drop=scripts['DROP'] - _v18_shift, land_a=scripts['LANDA'] - _v18_shift,
                           land_b=scripts['LANDB'] - _v18_shift))
    _params = _replace(_params, emerge_on_floor=True, own_floor_fallback=True)   # v40: own-floor fallback
    _params = _replace(_params, floor_probe=True)                                  # v52: floor probe at the reappear spot
    _params = _replace(_params, probe_snap=True)                                  # v53: snap onto the nearest probed floor
    # v32: vanilla MKT teleport damage (stk_ro_tele 0x10 / chip 2); v08-v31 used 1.5x (0x18 / 3) by request.
    _params = _replace(_params, strike_words=(STRIKE_WORDS[0], STRIKE_WORDS[1], 0x08021002, STRIKE_WORDS[3]))
    assert STRIKE_WORDS[2] == 0x08021803
    _m = _rt.motion()
    EMERGE_VEL, GRAV_NOHIT, GRAV_HIT = _m.emerge_velocity, _m.gravity_nohit, _m.gravity_hit
    RANGE_UNITS, HIDDEN_TICKS, AIR_CAP = _params.range_units, _params.hidden_ticks, _params.air_cap
    DROP_RATE, SINK_TICKS, X_OFFSET = 3, 3, -10   # report-only (TELEPORT_PHYSICS line), as in v18
    _v18 = _rt.assemble(PAYLOAD_VA, _v18_params)
    for _w in (0x80091101, 0x01031002, 0x04000000, 0x0000000E):
        _v18.raw(_w)
    assert V48_LINK_PASS or hashlib.sha256(_v18.link()).hexdigest() == 'a35d9732bbe72c1d0a39fba280e03b14a5fb2532fe22b2f790a55c86ddce1c3a', 'library no longer reproduces v18'
    # v51: stock calls from KSEG1 payload code go through their cached KSEG0 address (t9), and lifted
    # routines reach stock code through KSEG0 stubs (fighter_import.mips / lifter cached_calls).
    from mkmszr.fighter_import import mips as _mips51
    _mips51.DEFAULT_CACHED_CALLS = True
    a = _rt.assemble(PAYLOAD_VA, _params)
    # v16: standalone Sektor HK,HK combo record (v62 'SEKTOR_KNEE_ROOT_SAFE') in the payload arena (KSEG1).
    a.label('knee_rec')
    for _w in (0x80091101, 0x01031002, 0x04000000, 0x0000000E):
        a.raw(_w)
    _V19_PAYLOAD_LEN = a.pc() - PAYLOAD_VA
    # ---- v20: re-host stock Ice Blast (R2 step 1) ----
    # The LP Ice Blast record's action becomes a lifted copy of stock callback 0x80049C34 whose ground branch
    # transfers to selector 4 instead of 0; selector 4 is a lifted, relocated copy of the stock root 0x8004AB84
    # (all three Ice modes). The lifter verifies both copies word-for-word against the clean ROM: only internal
    # j/jal are retargeted, plus the one declared patch. The teleport keeps selector 3 through a payload thunk.
    from mkmszr.fighter_import import host as _host, lifter as _lifter
    def _clean_code(va, end):
        return clean[va - 0x7FFFF400:end - 0x7FFFF400]
    _host.emit_transfer_thunk(a, 'tele_thunk', 3)
    from mkmszr.fighter_import.actions import robo_zap as _zap
    ICE_CB_SRC, ICE_CB_END = _zap.ICE_CALLBACK_SRC, _zap.ICE_CALLBACK_END
    ICE_ROOT_SRC, ICE_ROOT_END = _zap.ICE_ROOT_SRC, _zap.ICE_ROOT_END
    ICE_CB_VA = a.pc()
    _cb = _lifter.lift(_clean_code(ICE_CB_SRC, ICE_CB_END), ICE_CB_SRC, ICE_CB_VA, cached_calls=True,
                       patches={0x80049C70: 0x24040004})       # ground branch: move a0,zero -> addiu a0,zero,4
    _lifter.verify(_clean_code(ICE_CB_SRC, ICE_CB_END), _cb)
    _zap.check_stock(_cb)
    assert _cb.patched[0x80049C70][0] == 0x00002021            # stock 'move a0, zero' (selector 0)
    for _i in range(0, len(_cb.code), 4):
        a.raw(int.from_bytes(_cb.code[_i:_i + 4], 'big'))
    # v30 (R2 step 3a): MKT rocket sounds hosted in isolated chains (sound section below): chest 0x0B -> host 173,
    # launch 3 -> host 175, boom 0x0A -> host 177. The chest sound wraps the root's open phase; the launch sound
    # plays at creation (the Ice launch block is skipped); the boom replaces the Ice hit sound in a lifted copy of
    # the hit child, reached from the flight child and from a lifted copy of the straight helper (point-blank).
    ROCKET_SOUND_HOSTS = {'chest': 173, 'launch': 175, 'boom': 177}
    # v35: the boom wrapper also starts the MKT explosion at the contact position (fighter_import.effects).
    _zapf.emit_sound_wrappers(a, ROCKET_SOUND_HOSTS['chest'], ROCKET_SOUND_HOSTS['boom'], explosion='fx_explosion')
    _fx.emit_spawn(a)
    _zapf.emit_launch_stub(a)   # v40: launch Ice visuals removed
    # v42 (R3): heat-seeking rocket (fighter_import.actions.robo_tracker)
    TRK_SOUND_HOSTS = {'target': 459, 'cruise': 478}
    from mkmszr.fighter_import.actions import sektor_tiers as _tiers                 # v54 (R4)
    _trk.emit_command_stubs(a, ICE_CB_VA, TRK_SOUND_HOSTS['target'], extra_costs=_tiers.EXTRA_COST)  # v58: homing 0x40  # v54: double/homing costs
    _trk.emit_hunt(a)
    _trk.emit_direction(a)
    _trk.emit_targeting(a)                                                     # v45: nearest living enemy
    _tiers.emit_conditions(a)  # v58: homing 0x40                                                 # v54: tier conditions
    _trk.emit_condition(a, base='tier_homing')                                 # v45: HP condition (v54: on the Air Ice Blast slot)
    _trk.emit_callback(a, smoke='fx_smoke', explosion='fx_explosion', boom_event=ROCKET_SOUND_HOSTS['boom'])
    _fx.emit_spawn(a, 'trk_spawn', process='trk_target')
    _fx.emit_process(a, 'trk_target', follow=('trk_follow', 'trk_heartbeat',
                     _trk.TARGET_OFFSET[0] * 2, _trk.TARGET_OFFSET[1] * 2))
    _fx.emit_descriptor(a, 'trk_target_desc', TARGET_PLACED, TARGET, 1, _zapf.EXPLOSION_RESERVE)
    _trk.emit_data(a, TRK_LOOPS)
    # v41: MKT robo1_slam sounds on the player throw (fighter_import.actions.robo_throw), isolated host chains.
    from mkmszr.fighter_import.actions import robo_throw as _thr
    THROW_SOUND_HOSTS = {'grab_voice': 332, 'arm_out': 336, 'arm_throw': 437, 'arm_in': 453}
    _thr.emit_wrappers(a, (THROW_SOUND_HOSTS['grab_voice'], THROW_SOUND_HOSTS['arm_out']),
                       THROW_SOUND_HOSTS['arm_throw'], THROW_SOUND_HOSTS['arm_in'])
    _fx.emit_process(a)
    _fx.emit_descriptor(a, 'fx_smoke', SMOKE_PLACED, SMOKE, _zapf.FX_HOST_TICKS_PER_FRAME, _zapf.SMOKE_RESERVE)
    _fx.emit_descriptor(a, 'fx_explosion', EXPLOSION_PLACED, EXPLOSION, _zapf.FX_HOST_TICKS_PER_FRAME, _zapf.EXPLOSION_RESERVE)
    # v35: Fire spiked-rod trap stumble without its 8-tick hit pause (lifted; reaction 0x23 points here).
    TRAP_VA = a.pc()
    _trap = _lifter.lift(_clean_code(_zapf.TRAP_STUMBLE_SRC, _zapf.TRAP_STUMBLE_END), _zapf.TRAP_STUMBLE_SRC, TRAP_VA, cached_calls=True,
                         patches=_zapf.trap_stumble_patches())
    _lifter.verify(_clean_code(_zapf.TRAP_STUMBLE_SRC, _zapf.TRAP_STUMBLE_END), _trap)
    _zapf.check_stock(_trap)
    for _i in range(0, len(_trap.code), 4):
        a.raw(int.from_bytes(_trap.code[_i:_i + 4], 'big'))
    HIT_CHILD_VA = a.pc()
    _hit = _lifter.lift(_clean_code(_zapf.HIT_CHILD_SRC, _zapf.HIT_CHILD_END), _zapf.HIT_CHILD_SRC, HIT_CHILD_VA, cached_calls=True,
                        patches=_zapf.hit_child_patches(a.labels['zap_boom'], explosion=True))
    _lifter.verify(_clean_code(_zapf.HIT_CHILD_SRC, _zapf.HIT_CHILD_END), _hit)
    _zapf.check_stock(_hit)
    for _i in range(0, len(_hit.code), 4):
        a.raw(int.from_bytes(_hit.code[_i:_i + 4], 'big'))
    STRAIGHT_VA = a.pc()
    _str = _lifter.lift(_clean_code(_zapf.STRAIGHT_SRC, _zapf.STRAIGHT_END), _zapf.STRAIGHT_SRC, STRAIGHT_VA, cached_calls=True,
                        patches={**_zapf.straight_patches(HIT_CHILD_VA),
                                 **_zapf.point_blank_strike_patch()})       # v32: point-blank test uses the rocket record
    _lifter.verify(_clean_code(_zapf.STRAIGHT_SRC, _zapf.STRAIGHT_END), _str)
    _zapf.check_stock(_str)
    for _i in range(0, len(_str.code), 4):
        a.raw(int.from_bytes(_str.code[_i:_i + 4], 'big'))
    # v27: rocket flight child + per-tick callback + speed table (robo_zap.emit_flight), ahead of the root so
    # the root's child-creation patch knows the child's address. v30: contact goes to the lifted hit child.
    _zapf.emit_flight(a, FLIGHT_ENTRY_OFF, hit_child=HIT_CHILD_VA, smoke='fx_smoke',   # v35: smoke trail
                      homing_child='trk_child')                                          # v42: R3 dispatch
    _trk.emit_child(a, HIT_CHILD_VA, 'trk_target_desc')
    # v29: rocket creation setup, called from the lifted root right after its token advance (0x8004AEE4).
    _proj.emit_bind_after_creation(a, 'zap_post_token', ROCKET_PAL_SRC, ROCKET, behind_owner=True,
                                   on_create=_trk.on_create(ROCKET_SOUND_HOSTS['launch'], TRK_SOUND_HOSTS['cruise']),   # v42
                                   epilogue=_zapf.emit_mode_reload)
    ZAP_POST_TOKEN_VA = a.labels['zap_post_token']
    _zapf.emit_speed_table(a, 'zap_speeds')
    # v31 (R2 step 3b): the rocket's strike record (robo_zap.strike_record), read through its KSEG0 alias.
    _zapf.emit_strike_record(a, 'zap_strike')
    ZAP_STRIKE_KSEG0 = a.labels['zap_strike'] & ~0x20000000
    ICE_ROOT_VA = a.pc()
    def _root_patches(again_va):                                                # v51: stubs follow the root
        return {**_zap.placement_patches(), **_zap.close_patches(), **_zapf.child_patches(a.labels['zap_child']),
                **_zapf.post_token_patches(ZAP_POST_TOKEN_VA), **_zapf.root_sound_patches(a.labels['zap_chest_open']),
                **_zapf.root_straight_patch(STRAIGHT_VA), **_zapf.launch_visual_patches(a.labels['zap_no_tint']),
                **_zapf.double_patches(again_va)}
    ZAP_AGAIN_VA = ICE_ROOT_VA + len(_lifter.lift(_clean_code(ICE_ROOT_SRC, ICE_ROOT_END), ICE_ROOT_SRC, ICE_ROOT_VA,
                                                  cached_calls=True, patches=_root_patches(ICE_ROOT_VA)).code)
    # v24 (R2 step 2b): the lifted root places the projectile at the donor retail offset (+5,+38) through
    # the same host call 0x80031208 (v72 Runtime-confirmed placement). Only the LP rocket runs this copy.
    _root = _lifter.lift(_clean_code(ICE_ROOT_SRC, ICE_ROOT_END), ICE_ROOT_SRC, ICE_ROOT_VA, cached_calls=True,
                         patches={**_zap.placement_patches(), **_zap.close_patches(),       # v26: closing frame 2 ticks
                                  **_zapf.child_patches(a.labels['zap_child']),                # v27: rocket flight child
                                  **_zapf.post_token_patches(ZAP_POST_TOKEN_VA),               # v29: creation setup
                                  **_zapf.root_sound_patches(a.labels['zap_chest_open']),      # v30: chest sound, no Ice launch sound
                                  **_zapf.root_straight_patch(STRAIGHT_VA),
                                  **_zapf.launch_visual_patches(a.labels['zap_no_tint']),
                                  **_zapf.double_patches(ZAP_AGAIN_VA)})                    # v46: Double Missile   # v40: no launch ghosts/tint                   # v30: lifted straight helper
    _lifter.verify(_clean_code(ICE_ROOT_SRC, ICE_ROOT_END), _root)
    _zap.check_stock(_root)
    for _i in range(0, len(_root.code), 4):
        a.raw(int.from_bytes(_root.code[_i:_i + 4], 'big'))
    assert a.pc() == ZAP_AGAIN_VA
    _zapf.emit_double_launch(a, ICE_ROOT_VA)                                     # v46: zap_again
    assert a.labels['zap_again'] == ZAP_AGAIN_VA
    _log('ICE_REHOST', 'callback', hex(ICE_CB_VA), 'root', hex(ICE_ROOT_VA), 'root relocated j/jal', len(_root.relocated),
          'callback relocated', len(_cb.relocated), 'patches', {hex(k): (hex(v[0]), hex(v[1])) for k, v in _cb.patched.items()},
          'root patches', {hex(k): (hex(v[0]), hex(v[1])) for k, v in _root.patched.items()})
    payload = a.link()
    COND_VA = a.labels['cond']
    KNEE_REC_VA = a.labels['knee_rec']
    assert KNEE_REC_VA & 3 == 0 and (KNEE_REC_VA >> 28) == 0xA
    assert len(payload) <= PAYLOAD_LIMIT, hex(len(payload))
    PAYLOAD_ROM = 0x00F10000
    assert set(rom[PAYLOAD_ROM:PAYLOAD_ROM + PAYLOAD_LIMIT]) == {0xFF}
    rom[PAYLOAD_ROM:PAYLOAD_ROM + PAYLOAD_LIMIT] = payload + b'\0' * (PAYLOAD_LIMIT - len(payload))

    # ---- exact Reverse Elbow v6 infrastructure (guarded against clean bytes) ----
    def guarded(off, old_hex, new_hex):
        old = bytes.fromhex(old_hex); new = bytes.fromhex(new_hex)
        assert bytes(rom[off:off + len(old)]) == old, hex(off)
        rom[off:off + len(new)] = new
    guarded(0x4B654, '2cc20003', '2cc20005')                                  # permit selectors 3 (teleport) and 4 (Ice re-host)
    assert be32(rom, 0x66F60) == 0x3C02801B
    guarded(0x66F64, '2442f420', '2442' + _ARENA_LO)                         # arena prefix reservation
    guarded(0x66FE0, '27bdffe83c02801b2442f420', '0802686100000000' + '2442' + _ARENA_LO)  # loader hook
    guarded(0x9AD84, '00' * 0x50, (
        '27bdffe83c02801b2442' + _ARENA_LO + 'afbf00103c04800fac82ecd00c0198e400000000'
        '2404001b3c05801b24a5f4200c01975900000000'
        '3c0880113409270fa509200e8fbf001027bd001803e0000800000000'
    ).ljust(0xA0, '0'))                                                        # loader stub (+ v6 max EXP)
    guarded(0xA1C5C, '00' * 16, f'{PAYLOAD_VA:08x}' + f'{ICE_ROOT_VA:08x}' + '00000000' * 2)  # table[3] teleport, table[4] Ice re-host
    guarded(0xA5154, '00' * 8, f'{PAYLOAD_ROM:08x}{PAYLOAD_ROM + PAYLOAD_LIMIT:08x}')  # file 0x1B
    for off, old in ((0xA6FFC, '0104036b'), (0xA7000, '09470591'), (0xA7004, '11ad0d16'), (0xA700C, '1ccf4e20')):
        guarded(off, old, '270f270f')                                         # v6 EXP caps
    # Low Kick descriptor -> F,F + LK teleport (stock condition retained, as in v6)
    def descriptor(masks, sel, cond, action, window, right, left):
        b = bytearray(0x2C)
        b[0:2] = masks[0].to_bytes(2, 'big'); b[2:4] = masks[1].to_bytes(2, 'big')
        b[4:8] = sel.to_bytes(4, 'big'); b[8:12] = cond.to_bytes(4, 'big'); b[12:16] = action.to_bytes(4, 'big')
        b[16:18] = window.to_bytes(2, 'big')
        for n, t in enumerate(right): b[0x12 + 2 * n:0x14 + 2 * n] = t.to_bytes(2, 'big')
        for n, t in enumerate(left): b[0x1E + 2 * n:0x20 + 2 * n] = t.to_bytes(2, 'big')
        return bytes(b)
    STOCK_LK = descriptor((0x40, 0x40), 0, 0x8004A4A4, 0x80049CB0, 0x14, (8, 7), (9, 7))
    TELE_LK = descriptor((0x40, 0x40), 1, COND_VA, a.labels['tele_thunk'], 0x18, (9, 9), (8, 8))
    guarded(0xB1B68, STOCK_LK.hex(), TELE_LK.hex())
    assert be16(rom, 0xB1B94) == 0                                            # table sentinel intact
    # v20: LP Ice Blast record (0x800B0F38) action -> lifted callback (ground branch = selector 4)
    # v44: the LP Ice Blast record (D,F + LP) -> MKT's F,F + LP straight rocket, action via the v42 flag stub.
    guarded(_trk.LP_RECORD_ROM, clean[_trk.LP_RECORD_ROM:_trk.LP_RECORD_ROM + 0x2C].hex(),
            _trk.straight_record(a.labels['trk_cb_straight'], a.labels['tier_straight']).hex())  # v54: ground only
    assert clean[_trk.LP_RECORD_ROM:_trk.LP_RECORD_ROM + 0x14].hex() == '00800080000000018004a30480049c3400140009'
    # v46: Ice Clone's LP record (D,B + LP) -> MKT's B,B,F + LP Double Missile (user choice), via the double stub.
    guarded(_trk.DOUBLE_RECORD_ROM, clean[_trk.DOUBLE_RECORD_ROM:_trk.DOUBLE_RECORD_ROM + 0x2C].hex(),
            _trk.double_record(a.labels['trk_cb_double'], a.labels['tier_double']).hex())  # v54: Ice Shatter slot, 0x30
    assert clean[_trk.DOUBLE_RECORD_ROM:_trk.DOUBLE_RECORD_ROM + 0x10].hex() == '00800080000000018004a22c8003cf8c'
    # v42 (R3): Freeze on Contact's HP record (D,F,F + HP) -> F,D,B + HP heat-seeking rocket (user choice).
    assert clean[_trk.HP_RECORD_ROM + 0xC:_trk.HP_RECORD_ROM + 0x10].hex() == '8005a7b4'
    guarded(_trk.HP_RECORD_ROM, clean[_trk.HP_RECORD_ROM:_trk.HP_RECORD_ROM + 0x2C].hex(),
            _trk.descriptor_record(a.labels['trk_cb_homing'], a.labels['trk_cond']).hex())   # v45: + target condition

    # v54 (R4): Directional Ice up's HK table emptied, Ice Shatter skipped, Super Slide on the Freeze slot's tier.
    for _off, (_old, _new) in _tiers.stock_edits(bytes(rom)).items():
        guarded(_off, f'{_old:08x}', f'{_new:08x}')

    # ---- v09: donor sounds into isolated MKMSZ hosts (guarded) ----
    import zlib as _zlib
    _ctl = _zlib.decompress(mkt[0xA8F588:0xA8F588 + 0x17AE0], -15)
    _defs = _zlib.decompress(mkt[0xAA7090:0xAA7090 + 0x7A6], -15)
    assert hashlib.sha256(_ctl).hexdigest().startswith('8dc6f036dc795cba')
    assert hashlib.sha256(_defs).hexdigest().startswith('6cdfcf946ba78f49')
    def _donor(event_id):
        d = _defs[event_id * 16:event_id * 16 + 16]
        ln = int.from_bytes(d[4:8], 'big'); off = int.from_bytes(d[8:12], 'big')
        track = _zlib.decompress(mkt[0xAA7836 + off:], -15)[:ln]
        pid = int.from_bytes(track[0:4], 'big'); sid = int.from_bytes(_ctl[pid * 4 + 2:pid * 4 + 4], 'big')
        sub = _ctl[0x6E0 + sid * 20:0x6E0 + sid * 20 + 20]; wid = int.from_bytes(sub[10:12], 'big')
        wav = _ctl[0x2828 + wid * 24:0x2828 + wid * 24 + 24]; pred = _ctl[0x4F48 + wid * 264:0x4F48 + wid * 264 + 264]
        so = 0xAB4370 + int.from_bytes(wav[0:4], 'big'); sl = int.from_bytes(wav[4:8], 'big')
        return track, sub, wav, pred, mkt[so:so + sl]
    MSZ_SSEQ_TRACKS, MSZ_PATCH, MSZ_SUB, MSZ_WAVE, MSZ_PRED, MSZ_TBL = 0x979240, 0x947CB8, 0x948768, 0x94C138, 0x950490, 0x9B0650
    SOUND_ROM = 0xF20000
    SOUND_LIMIT = 0xF30000                 # v42: tracker sounds; clean ROM 0xFF to file 0x87 at 0xF40000
    # (donor event, sample sha256 prefix, host event, host patch, host subpatch, host wave, host track, patch, subpatch, wave, pred sha prefix)
    SOUNDS = (
        (0x104, '7e039ca338e13838', TELE_EVENT, 492, 335, 325,
         '000001ec00007f4000000078007800000000000c00113c7f8105123c00227820', '0100014f',
         '647340003c00007f0505014500017d00000a7f7f', '0018ce8c00000d5400000000fffffb50ffffffff00000000', '1fee28ccadb934a1'),
    )
    assert set(rom[SOUND_ROM:SOUND_LIMIT]) == {0xFF}
    _cur = SOUND_ROM
    for (dev, ssha, hev, hp, hs, hw, htrk, hpat, hsub, hwav, hpred) in SOUNDS:
        track, sub, wav, pred, smp = _donor(dev)
        assert hashlib.sha256(smp).hexdigest().startswith(ssha), hex(dev)
        toff = int.from_bytes(clean[0x976D60 + hev * 16 + 8:0x976D60 + hev * 16 + 12], 'big')
        assert int.from_bytes(clean[0x976D60 + hev * 16 + 4:0x976D60 + hev * 16 + 8], 'big') == 0x20 == len(track)
        trk_rom = MSZ_SSEQ_TRACKS + toff
        assert int.from_bytes(clean[trk_rom:trk_rom + 4], 'big') == hp
        assert hashlib.sha256(clean[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264]).hexdigest().startswith(hpred)
        t = bytearray(track); t[0:4] = hp.to_bytes(4, 'big')
        sb = bytearray(sub); sb[10:12] = hw.to_bytes(2, 'big')
        wv = bytearray(wav); wv[0:4] = (_cur - MSZ_TBL).to_bytes(4, 'big')
        guarded(trk_rom, htrk, bytes(t).hex())
        assert clean[MSZ_PATCH + hp * 4:MSZ_PATCH + hp * 4 + 4].hex() == hpat          # patch kept: -> host subpatch
        guarded(MSZ_SUB + hs * 20, hsub, bytes(sb).hex())
        guarded(MSZ_WAVE + hw * 24, hwav, bytes(wv).hex())
        rom[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264] = pred
        assert _cur + len(smp) <= SOUND_LIMIT
        rom[_cur:_cur + len(smp)] = smp
        _log('SOUND', hex(dev), '-> event', hev, 'patch', hp, 'sub', hs, 'wave', hw, 'sample ROM', hex(_cur), hex(len(smp)))
        _cur = (_cur + len(smp) + 0xF) & ~0xF

    # ---- v12: Sektor's MKT voice/attack set replaces Sub-Zero's player-only voice ----
    # Sub-Zero's voice: player (type 4) table 0x800A2EC8 (ROM 0xA3AC8) -> descriptors 0x20..0x2C -> events 30..43,
    # owned only by that table (no enemy table, no other descriptor). Each used Sub-Zero event keeps its slot and
    # descriptor; its 0x20-byte track is replaced by the donor track pointing at an isolated host chain.
    # Donor identities (arcade MK3 REV13 MKSOUND.ASM labels; MKT kept the slot order, durations match):
    #   attacks: robots have no attack voice, only rsnd_whoosh -> MKT triple 6 'whoosh #1' (event 416), triple 7
    #   'whoosh #3' (event 417); hurt: robo sparks ft 0x0F/0x10/0x11 (events 268/269/270); death ('wasted'):
    #   robo speech 1, ft 0x12 (event 271). Jump and slide/special yells: robots have none -> table entry 0 (skipped
    #   by 0x80064B00). Death gets its own descriptor 0x2A (stock-unreferenced, event 41) instead of sharing hurt 0x26.
    # v14: data-driven, donor-faithful voice rule (reusable for any MKT donor fighter).
    # MKT voice groups (arcade MK3 group_table semantics): 0 attack, 1 jump, 2 wasted, 3 grab, 4 throw voice,
    # 5 tripped, 6 face hit, 7 run, 8 shook, 9 death scream. Group table 0x800A19D4[group] -> {u16 count, then
    # count entries per voice group}; the fighter's voice group is 0x800A19FC[fighter] (Sektor 7 -> group 5,
    # robots). 0xFFFF = no sound for that group.
    # MKMSZ player categories -> MKT semantics (by the reactions that play them; MK3 MKREACT.ASM):
    #   0-1 attack effort  -> group 0 voice + rsnd_whoosh; MKMSZ plays one sample, so: voice if the donor has one,
    #                         else MKT whoosh #1 / #3 (triple slots 6 / 7)
    #   2-3, 4-5 stand-up hits -> group 6 'face hit' (r_hi/lo_punch, lo_kick, duck hits: rsnd_react_voice)
    #   6-7 launching hits -> group 2 'wasted' (r_hi_kick, r_roundhouse, r_uppercut, launching combos)
    #   8 jump -> group 1;  9 sweep family -> group 5 'tripped' (r_sweep, r_slide)
    #   10 knockdown landing (0x800546E8, after its own ground thud descriptor 0x10) and zero-HP death (0x80029100)
    #      -> MK3 land_on_my_back is shake_n_sound = rsnd_ground only, and a KO has no extra voice -> silent for every
    #      donor. (v14 used group 9 'death scream': Rejected, it is the pit/fatality scream.)
    #   11 slide/special yell -> no MK3 counterpart for robots -> silent
    #   run (descriptor 0x22 via the Run script) -> group 7
    MKT_GROUP_TABLE, MKT_VOICE_GROUP = 0x800A19D4, 0x800A19FC
    DONOR_FIGHTER = 7
    def _u16(va): return int.from_bytes(mkt[va - 0x80000000:va - 0x80000000 + 2], 'big')
    def _u32(va): return int.from_bytes(mkt[va - 0x80000000:va - 0x80000000 + 4], 'big')
    _vg = _u16(MKT_VOICE_GROUP + 2 * DONOR_FIGHTER)
    def donor_group(g):
        t = _u32(MKT_GROUP_TABLE + 4 * g); n = _u16(t)
        ev = [_u16(t + 2 + 2 * (_vg * n + k)) for k in range(n)]
        return [e & 0x7FFF for e in ev if e != 0xFFFF]
    _g = {g: donor_group(g) for g in range(10)}
    assert _vg == 5 and _g[0] == [] and _g[1] == [] and _g[5] == [] and _g[6] == [62, 63, 64] and _g[2] == [126, 127] \
        and _g[9] == [17] and _g[7] == [35], _g
    WHOOSH = [_u16(0x800A1AA8 + 2 * 6) & 0x7FFF, _u16(0x800A1AA8 + 2 * 7) & 0x7FFF]    # triple 6/7: whoosh #1/#3
    assert WHOOSH == [416, 417]
    WHOOSH_VOLUME = 1.0   # v17: v16's 0.85 Rejected - categories 0/1 also play the somersault jump (0x8002FB08), not only attacks
    def pair(evs):            # MKMSZ picks 1 of 2; keep every distinct donor sound, in table order
        d = list(dict.fromkeys(evs)); return (d * 2)[:2] if d else [None, None]
    _face = [e for e in _g[6] if e != 63]   # 62 and 63 are the same waveform (158) in MKT; 1-of-2 keeps both sounds
    CATEGORY_DONOR = {
        0: (_g[0] or WHOOSH)[0], 1: (_g[0] or WHOOSH)[1 % len(_g[0] or WHOOSH)],
        2: pair(_face)[0], 3: pair(_face)[1], 4: pair(_face)[0], 5: pair(_face)[1],
        6: pair(_g[2])[0], 7: pair(_g[2])[1],
        8: (_g[1] or [None])[0], 9: (_g[5] or [None])[0], 10: None, 11: None,
    }
    RUN_DONOR = _g[7][0]
    # host chains (isolated; see Audio system), one per distinct donor event
    HOST_POOL = [
        (159, 316, 159, 149, '0000013c00007f4000000078007800000000000c00113c7f3f123c0022227820', '0100009f',
         '647340003c00007f0505009500017d00000a7f7f', '000c1d6c0000064c00000000fffffb50ffffffff00000000', '1e18f07270047889'),
        (164, 321, 164, 154, '0000014100007f4000000078007800000000000c00113c7f8365123c00227820', '010000a4',
         '647340004e00007f0505009a00017d00000a7f7f', '000d19ae0000114400000000fffffb50ffffffff00000000', '5b3eef19e893868d'),
        (168, 325, 168, 158, '0000014500007f4000000078007800000000000c00113c7f43123c0022227820', '010000a8',
         '647340003c00007f0505009e00017d00000a7f7f', '000d54dc000006a600000000fffffb50ffffffff00000000', 'cc960512bcea3be8'),
        (170, 327, 170, 160, '0000014700007f4000000078007800000000000c00113c7f8375123c00227820', '010000aa',
         '647340004800007f050500a000017d00000a7f7f', '000d63ce0000193e00000000fffffb50ffffffff00000000', 'd5b755b9ead2f240'),
        (171, 328, 171, 161, '0000014800007f4000000078007800000000000c00113c7f6f123c0022227820', '010000ab',
         '647340004800007f050500a100017d00000a7f7f', '000d7d0c0000059800000000fffffb50ffffffff00000000', 'c77d9e2a5a0b3d9f'),
        (172, 329, 172, 162, '0000014900007f4000000078007800000000000c00113c7f8141123c00227820', '010000ac',
         '647340004800007f050500a200017d00000a7f7f', '000d82a4000009b400000000fffffb50ffffffff00000000', '41f7e8f634ffd33b'),
        (173, 330, 173, 163, '0000014a00007f4000000078007800000000000c00113c7f6b123c0022227820', '010000ad',
         '647340003c00007f050500a300017d00000a7f7f', '000d8c5800000aba00000000fffffb50ffffffff00000000', '2b7c8f1d366073d9'),
        (175, 332, 175, 165, '0000014c00007f4000000078007800000000000c00113c7f8109123c00227820', '010000af',
         '647340004800007f050500a500017d00000a7f7f', '000d9d54000006dc00000000fffffb50ffffffff00000000', '3d9376e9afdccac0'),
    ]
    _needed = list(dict.fromkeys([e for e in CATEGORY_DONOR.values() if e is not None]))
    assert len(_needed) <= len(HOST_POOL)
    VOICE_HOSTS = {dev: HOST_POOL[k] for k, dev in enumerate(_needed)}
    CAT_EVENT = {0: 31, 1: 32, 2: 38, 3: 39, 4: 36, 5: 37, 6: 34, 7: 35, 8: 43, 9: 40, 10: 41, 11: 42}   # stock events (10 via new desc 0x2A)
    CAT_DESC = {0: 0x20, 1: 0x21, 2: 0x27, 3: 0x28, 4: 0x25, 5: 0x26, 6: 0x23, 7: 0x24, 8: 0x2C, 9: 0x29, 10: 0x2A, 11: 0x2B}
    SZ_VOICE_MAP = {CAT_EVENT[c]: dev for c, dev in CATEGORY_DONOR.items() if dev is not None}
    NEW_TABLE = b''.join((CAT_DESC[c] if CATEGORY_DONOR[c] is not None else 0).to_bytes(2, 'big') for c in range(12))
    _log('CATEGORY_DONOR', CATEGORY_DONOR, 'RUN', RUN_DONOR)
    SZ_TABLE_ROM = 0xA3AC8
    assert clean[0xA2330 + 0x22 * 10:0xA2330 + 0x22 * 10 + 10].hex() == '00210064000000000000'   # descriptor 0x22 -> event 33
    guarded(SZ_TABLE_ROM, '00200021002700280025002600230024002c00290026002b', NEW_TABLE.hex())
    def _event_track_rom(e):
        assert int.from_bytes(clean[0x976D60 + e * 16 + 4:0x976D60 + e * 16 + 8], 'big') == 0x20
        return MSZ_SSEQ_TRACKS + int.from_bytes(clean[0x976D60 + e * 16 + 8:0x976D60 + e * 16 + 12], 'big')
    _donor_tracks = {}
    for dev, (hev, hp, hs, hw, htrk, hpat, hsub, hwav, hpred) in VOICE_HOSTS.items():
        track, sub, wav, pred, smp = _donor(dev)
        assert len(track) == 0x20, hex(dev)
        trk_rom = _event_track_rom(hev)
        assert clean[trk_rom:trk_rom + 0x20].hex() == htrk and clean[MSZ_PATCH + hp * 4:MSZ_PATCH + hp * 4 + 4].hex() == hpat
        assert hashlib.sha256(clean[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264]).hexdigest().startswith(hpred)
        sb = bytearray(sub); sb[10:12] = hw.to_bytes(2, 'big')
        wv = bytearray(wav); wv[0:4] = (_cur - MSZ_TBL).to_bytes(4, 'big')
        guarded(MSZ_SUB + hs * 20, hsub, bytes(sb).hex())
        guarded(MSZ_WAVE + hw * 24, hwav, bytes(wv).hex())
        rom[MSZ_PRED + hw * 264:MSZ_PRED + hw * 264 + 264] = pred
        assert _cur + len(smp) <= SOUND_LIMIT
        rom[_cur:_cur + len(smp)] = smp
        t = bytearray(track); t[0:4] = hp.to_bytes(4, 'big')
        if dev in WHOOSH:                      # v16: attack whooshes at 85% track volume (user request)
            assert t[6] == 0x7F and WHOOSH_VOLUME == 1.0
        _donor_tracks[dev] = bytes(t)
        _log('VOICE', 'MKT event', dev, '-> host', hev, hp, hs, hw, 'sample', hex(_cur), hex(len(smp)))
        _cur = (_cur + len(smp) + 0xF) & ~0xF
    for sze, dev in SZ_VOICE_MAP.items():
        trk_rom = _event_track_rom(sze)
        assert int.from_bytes(clean[trk_rom:trk_rom + 4], 'big') == 157 + sze          # stock patch 187 + (event - 30)
        rom[trk_rom:trk_rom + 0x20] = _donor_tracks[dev]
    _log('VOICE_MAP', {k: v for k, v in SZ_VOICE_MAP.items()}, 'SAMPLES_END', hex(_cur))

    # ---- v30: rocket sounds (fighter_import.sound) ----
    from mkmszr.fighter_import import sound as _snd
    _bank = _snd.MktSoundBank(mkt)
    _chains = {c.event: c for c in _snd.ISOLATED_CHAINS}
    for _name, _host in ROCKET_SOUND_HOSTS.items():
        _ev = _bank.fighter_event(DONOR_FIGHTER, _zapf.SOUND_OCHAR[_name])
        _d = _bank.event(_ev)
        _nxt = _snd.install(rom, clean, _d, _chains[_host], _cur)
        assert _nxt <= SOUND_LIMIT
        _log('ROCKET_SOUND', _name, 'ochar', hex(_zapf.SOUND_OCHAR[_name]), 'MKT event', hex(_ev), '-> host', _host,
              'sample', hex(_cur), hex(len(_d.sample)), _snd.sample_digest(_d)[:16])
        _cur = _nxt
    assert {_bank.fighter_event(DONOR_FIGHTER, _zapf.SOUND_OCHAR[k]) for k in ROCKET_SOUND_HOSTS} == {0x108, 0x100, 0x107}
    # v41: throw sounds. Grab voice = MKT voice group 3 for Sektor's voice group (v14 rule); arm sounds = robot ochar 0/1/2.
    assert _g[_thr.GRAB_VOICE_GROUP] == [0x67]
    _throw_donor = {'grab_voice': _g[_thr.GRAB_VOICE_GROUP][0],
                    'arm_out': _bank.fighter_event(DONOR_FIGHTER, _thr.ARM_OUT),
                    'arm_throw': _bank.fighter_event(DONOR_FIGHTER, _thr.ARM_THROW),
                    'arm_in': _bank.fighter_event(DONOR_FIGHTER, _thr.ARM_IN)}
    assert _throw_donor == {'grab_voice': 0x67, 'arm_out': 0xFD, 'arm_throw': 0xFE, 'arm_in': 0xFF}
    # v42: tracker sounds - target (ochar 0x0C) and cruise rocket (ochar 4).
    _trk_donor = {'target': _bank.fighter_event(DONOR_FIGHTER, _trk.TARGET_SOUND_OCHAR),
                  'cruise': _bank.fighter_event(DONOR_FIGHTER, _trk.CRUISE_SOUND_OCHAR)}
    assert _trk_donor == {'target': 0x109, 'cruise': 0x101}
    for _name, _host in TRK_SOUND_HOSTS.items():
        _d = _bank.event(_trk_donor[_name])
        _nxt = _snd.install(rom, clean, _d, _chains[_host], _cur)
        assert _nxt <= SOUND_LIMIT
        _log('TRACKER_SOUND', _name, 'MKT event', hex(_trk_donor[_name]), '-> host', _host, 'sample', hex(_cur), hex(len(_d.sample)))
        _cur = _nxt
    assert not set(THROW_SOUND_HOSTS.values()) & (set(ROCKET_SOUND_HOSTS.values()) | {TELE_EVENT} | {h[0] for h in VOICE_HOSTS.values()})
    for _name, _host in THROW_SOUND_HOSTS.items():
        _d = _bank.event(_throw_donor[_name])
        _nxt = _snd.install(rom, clean, _d, _chains[_host], _cur)
        assert _nxt <= SOUND_LIMIT
        _log('THROW_SOUND', _name, 'MKT event', hex(_throw_donor[_name]), '-> host', _host, 'sample', hex(_cur), hex(len(_d.sample)))
        _cur = _nxt
    for _va, _new in _thr.patches(a.labels['throw_grab'], a.labels['throw_throw'], a.labels['throw_release']).items():
        guarded(_va - 0x7FFFF400, f'{_thr.SITES[_va]:08x}', f'{_new:08x}')
    _log('THROW_HOOKS', {hex(k): hex(v) for k, v in _thr.patches(a.labels['throw_grab'], a.labels['throw_throw'], a.labels['throw_release']).items()})

    # ---- v16: Sektor's MKT combo strings (v62 Runtime-confirmed graph, reaction selectors MKMSZ-native) ----
    # Strings: HK,HK / HP,HP,D+LP / HP,HP,HK,B+HK / HP,HP,HK,HK,B+HK. See wiki Sektor takeover proof history v61/v62.
    COMBO_ROM, ELBOW_ROOT_PTR_ROM, KNEE_ROOT_PTR_ROM = 0xB1CB0, 0xA1C70, 0xA1CE8
    guarded(COMBO_ROM,
            '800910030200100200000000800b10c0' '000910040201100200000000800b10d0' '000913050304100201050000800b10f0'
            '8009150101031002010100000000000e' '800c13030303130201000000800b1100' '8009150102031302040100000000000e',
            '800910030300100200000000800b10c0' '000913010303100201000000800b10e0' '80090b01020110020504000000000010'
            '00091303010310020401000000000010' '800911010103100201000000800b1100' '80091303010310020401000000000010')
    assert be32(rom, ELBOW_ROOT_PTR_ROM) == 0x800B10B0                     # HP/elbow root unchanged
    guarded(KNEE_ROOT_PTR_ROM, '800b10f0', f'{KNEE_REC_VA:08x}')            # knee/HK root -> payload record
    _kr = PAYLOAD_ROM + (KNEE_REC_VA - PAYLOAD_VA)
    assert rom[_kr:_kr + 16].hex() == '8009110101031002040000000000000e'
    _log('COMBOS', 'graph at ROM', hex(COMBO_ROM), 'HK,HK record', hex(KNEE_REC_VA), 'ROM', hex(_kr))
    # v62: the knockback finishers (strike 0x04, record 0x800B0E30) do 10 damage instead of 7 (owner, 2026-11-11).
    guarded(0xB1A30, '00410000003300851412070100000201', '004100000033008514120a0100000201')

    # Zap script: projectile loop frames (+0xD90/+0xD94), token-0x0B constructor frame (+0xDBC) and the next
    # parent frame (+0xDC4, v80/v89: keeps the parent advance from restoring an Ice descriptor) -> rocket.
    _FALLBACK = be32(rom, RR + 0xD90)
    assert be32(rom, RR + 0xDB8) == 0x0B and be32(rom, RR + 0xD98) == 1 and be32(rom, RR + 0xD9C) == 0xD90
    for _pos in (0xD90, 0xD94, 0xDBC, 0xDC4):
        assert be32(rom, RR + _pos) == _FALLBACK, hex(_pos)
        put32(rom, RR + _pos, ROCKET_SHAPE_OFF)
    # v29: no token-handler patches and no code in ROM [0x9ADD4,0x9AF20): that span is the zero tail of the
    # F3DLX.Rej graphics microcode's overlay 1 (text +0x1024..+0x11C0, DMA'd into RSP IMEM 0x18DC..0x1A78).
    # The rocket's palette/sub-layer/speed/first-frame setup runs from the lifted root instead (zap_post_token).
    assert rom[_proj.TOKEN_PALETTE_CALL_ROM:_proj.TOKEN_PALETTE_CALL_ROM + 4].hex() == f'{_proj.STOCK_PALETTE_JAL:08x}'
    assert rom[_proj.TOKEN_INSERT_CALL_ROM:_proj.TOKEN_INSERT_CALL_ROM + 4].hex() == f'{_proj.STOCK_INSERT_JAL:08x}'
    assert set(rom[0x9ADD4:0x9AF20]) == {0}
    _log('ROCKET', 'image', hex(ROCKET_IMAGE_OFF), 'palette', hex(ROCKET_PAL_OFF), 'shape', hex(ROCKET_SHAPE_OFF),
          'file87 end', hex(_new_end), 'post-token routine', hex(ZAP_POST_TOKEN_VA))

    # ---- v26: chest open / hold / close (R2 step 2c) ----
    # MKT do_robo_zap: robo_open_chest_fast (RBCHEST1, RBCHEST2) -> rocket -> sleep 0x20 -> robo_close_chest.
    # The Zap script's parent frames carry the chest poses (robo_zap.chest_script_words); phase 1 ends early
    # and jumps to the unchanged token, so the projectile hooks keep their offsets. One lifted-root patch
    # shortens the closing frame's hold to the donor 4 ticks @60 Hz.
    _chest = _zap.chest_script_words(shape_map[CHEST_RELS[0]], shape_map[CHEST_RELS[1]])
    for _pos, _word in sorted(_chest.items()):
        assert be32(rom, RR + _pos) == (0 if _pos == _zap.ZAP_SCRIPT + 0x14 else _FALLBACK), hex(_pos)  # stock layout
        put32(rom, RR + _pos, _word)
    assert be32(rom, RR + _zap.ZAP_TOKEN) == 0x0B and be32(rom, RR + 0xDBC) == ROCKET_SHAPE_OFF
    # v31: player (type 4) strike-pointer table entry 0x13 (straight Ice projectile) -> the rocket record.
    guarded(_zapf.STRIKE_SELECTOR_SLOT_ROM, f'{_zapf.STOCK_STRIKE_POINTER:08x}', f'{ZAP_STRIKE_KSEG0:08x}')
    assert be32(rom, 0x800AF484 + 0x13 * 4 - 0x7FFFF400) == ZAP_STRIKE_KSEG0
    # v34: reaction-table entry 0x23 (stock: endless-sleep dummy 0x8004E0C0, unused) -> the stock Fire spiked-rod
    # trap stumble 0x80051280 (robo_zap.ROCKET_REACTION_ROUTINE); no copied code.
    _rslot = _zapf.REACTION_TABLE_ROM + 4 * _zapf.ROCKET_REACTION
    # v35: -> the lifted copy without the trap's 8-tick hit pause (KSEG1 payload; reaction routines are jalr'd).
    guarded(_rslot, f'{_zapf.STOCK_DUMMY_REACTION:08x}', f'{TRAP_VA:08x}')
    _log('REACTION', hex(_zapf.ROCKET_REACTION), '->', hex(TRAP_VA), '(lifted Fire spiked-rod trap stumble, no hit pause)',
          'relocated', len(_trap.relocated), 'patches', {hex(k): (hex(v[0]), hex(v[1])) for k, v in _trap.patched.items()})
    _log('STRIKE', 'record', _zapf.strike_record().hex(), 'at', hex(ZAP_STRIKE_KSEG0), 'type-4 selector 0x13 repointed')
    _log('CHEST', {hex(r): hex(shape_map[r]) for r in CHEST_RELS}, 'script', {hex(k): hex(v) for k, v in sorted(_chest.items())})

    # ============================================================================
    # v48 (option C step 2): the payload becomes a relocatable blob inside file 0x87.
    # Two more links of this same build at higher payload addresses give the relocations (word diff)
    # and the stock references into the payload; the blob (link A) goes into file 0x87's slack after
    # the v47 chain with its relocation table, and file 0x1B keeps only the fixed loader.
    # ============================================================================
    if V48_LINK_PASS:
        return {'rom': bytes(rom)}
    from mkmszr.fighter_import import relocate as _rel
    from mkmszr.patches.rainbow_palette import LOAD_JAL_SITES as _LOAD_SITES, EXPECTED_RAW_LOADER_JAL as _LOADER_JAL
    V48_DELTAS = (0x12340, 0x2468C)
    def _link_pass(delta):
        return build(clean, mkt, link_va=PAYLOAD_VA + delta)['rom']
    _links = {d: _link_pass(d) for d in V48_DELTAS}
    _n = len(payload)
    _relocs = _rel.find(payload, _links[V48_DELTAS[0]][PAYLOAD_ROM:PAYLOAD_ROM + _n], V48_DELTAS[0])
    for _d in V48_DELTAS:
        assert _rel.apply(payload, _relocs, _d) == _links[_d][PAYLOAD_ROM:PAYLOAD_ROM + _n], hex(_d)
    # Stock references into the payload: every other ROM word that moves with the link.
    _refs, _jal_sites = [], {}
    for _off in range(0, len(rom), 4):
        if PAYLOAD_ROM <= _off < PAYLOAD_ROM + PAYLOAD_LIMIT or _off in (0x10, 0x14):
            continue
        _wa = be32(rom, _off)
        _moves = [be32(_links[_d], _off) for _d in V48_DELTAS]
        if all(_w == _wa for _w in _moves):
            continue
        assert _off < 0x00100000, ('payload reference outside the main segment', hex(_off))
        _va = _off + 0x7FFFF400
        _target = _wa | 0x20000000
        if all((_w - _wa) & 0xFFFFFFFF == _d for _w, _d in zip(_moves, V48_DELTAS)):
            _refs.append(_rel.StockRef(_va, _target - PAYLOAD_VA, kseg0=not (_wa >> 29) & 1))
        elif _wa >> 26 == 3 and all(_w >> 26 == 3 and (_w - _wa) & 0x03FFFFFF == _d >> 2 for _w, _d in zip(_moves, V48_DELTAS)):
            _jal_sites[_off] = (((_wa & 0x03FFFFFF) << 2) | 0xA0000000) - PAYLOAD_VA
        else:
            raise AssertionError(('unclassified payload reference', hex(_off), hex(_wa), [hex(w) for w in _moves]))
    # v57: the rope companion keeps existing (stage overlays need it); see after the blob below.
    from mkmszr.fighter_import import attachment as _att
    # v59: slide and death from the common MKT animations already mapped onto the host slots; v60: + long fall.
    from mkmszr.fighter_import import common_moves as _common
    # v61: + pickup (first low punch 1,2,2,3,3) and the grabbed-by-an-enemy poses.
    rom[RR:RR + 0x459E0] = _common.apply(rom[RR:RR + 0x459E0], stock=clean_f87,
                                         flipped=BODY.flipped)
    # Blob and relocation table in file 0x87, after the v47 chain.
    _table = _rel.encode(_relocs)
    BLOB_OFF = (CHAIN_END + 0xF) & ~0xF
    TABLE_OFF = BLOB_OFF + _n
    BLOB_END = TABLE_OFF + len(_table)
    assert BLOB_END <= TYPE_END and set(rom[RR + BLOB_OFF:RR + BLOB_END]) == {0xFF}, hex(BLOB_END)
    rom[RR + BLOB_OFF:RR + TABLE_OFF] = payload
    rom[RR + TABLE_OFF:RR + BLOB_END] = _table
    assert be32(rom, 0xA5668) - RR == 0x459E0      # the file keeps its stock size
    # v57: 8x8 transparent companion frame after the relocation table; rope pairs draw it on the companion.
    COMPANION_OFF = (BLOB_END + 0xF) & ~0xF
    _cblob, COMPANION_SHAPE = _att.companion_frame(COMPANION_OFF)
    assert COMPANION_OFF + len(_cblob) <= TYPE_END and set(rom[RR + COMPANION_OFF:RR + COMPANION_OFF + len(_cblob)]) == {0xFF}
    rom[RR + COMPANION_OFF:RR + COMPANION_OFF + len(_cblob)] = _cblob
    rom[RR:RR + 0x400] = _att.transparent_companion(rom[RR:RR + 0x400], COMPANION_SHAPE)
    # Fixed part in file 0x1B (production: the 16 KiB pool tail).
    FIXED_VA = fixed_va if fixed_va is not None else PAYLOAD_VA      # v50
    _fx_asm = _Asm(FIXED_VA)
    _tramp = _rel.emit_fixed(_fx_asm, 0x80065D64, 0x87, PAYLOAD_VA, BLOB_OFF, TABLE_OFF, _refs, sorted(set(_jal_sites.values())))
    FIXED = _fx_asm.link()
    rom[PAYLOAD_ROM:PAYLOAD_ROM + PAYLOAD_LIMIT] = FIXED + b'\0' * (PAYLOAD_LIMIT - len(FIXED))
    for _off, _boff in _jal_sites.items():
        put32(rom, _off, 0x0C000000 | (((_fx_asm.labels[_tramp[_boff]] & ~0x20000000) >> 2) & 0x03FFFFFF))
    _load = _fx_asm.labels['rel_load'] & ~0x20000000
    for _site in _LOAD_SITES:
        assert be32(rom, _site) == _LOADER_JAL and be32(rom, _site + 4) == 0x24040087, hex(_site)
        put32(rom, _site, 0x0C000000 | ((_load >> 2) & 0x03FFFFFF))
    _log('V48_BLOB', 'file87', hex(BLOB_OFF), hex(_n), 'table', hex(TABLE_OFF), hex(len(_table)), 'relocs', len(_relocs),
          {k: sum(r.kind == k for r in _relocs) for k in range(4)}, 'slack left', hex(TYPE_END - BLOB_END))
    _log('V48_REFS', [(hex(r.address), hex(r.offset), 'k0' if r.kseg0 else 'k1') for r in _refs])
    _log('V48_TRAMPOLINES', {hex(o): (hex(b), _tramp[b], hex(_fx_asm.labels[_tramp[b]] & ~0x20000000)) for o, b in _jal_sites.items()})
    _log('V48_FIXED', hex(len(FIXED)), 'bytes at', hex(FIXED_VA), 'load wrapper', hex(_load), 'on', len(_LOAD_SITES), 'file-0x87 load sites')

    # ============================================================================
    # v49 (integration plan step 3): production-style ROM placement. Grow the image to 32 MiB (0xFF fill,
    # as production's generated output) and move fighter file 0x87 and the donor sound samples above
    # 16 MiB into one candidate region of the unassigned generated-output tail [0x01819C00, 0x02000000).
    # The old locations are wiped so nothing can read them by accident.
    # ============================================================================
    OUTPUT_SIZE = 0x02000000
    SEKTOR_ROM = 0x01820000
    SEKTOR_FILE87_ROM = SEKTOR_ROM
    SEKTOR_SAMPLES_ROM = (SEKTOR_FILE87_ROM + 0x459E0 + 0xFFF) & ~0xFFF
    assert len(rom) == 0x01000000
    rom.extend(b'\xFF' * (OUTPUT_SIZE - len(rom)))
    _f87 = (be32(rom, 0xA5664), be32(rom, 0xA5668))
    assert _f87 == (RR, RR + 0x459E0)
    rom[SEKTOR_FILE87_ROM:SEKTOR_FILE87_ROM + 0x459E0] = rom[RR:RR + 0x459E0]
    rom[RR:RR + 0x459E0] = b'\xFF' * 0x459E0
    put32(rom, 0xA5664, SEKTOR_FILE87_ROM); put32(rom, 0xA5668, SEKTOR_FILE87_ROM + 0x459E0)
    _samples_end = _cur
    _shift = SEKTOR_SAMPLES_ROM - SOUND_ROM
    rom[SEKTOR_SAMPLES_ROM:SEKTOR_SAMPLES_ROM + (_samples_end - SOUND_ROM)] = rom[SOUND_ROM:_samples_end]
    rom[SOUND_ROM:_samples_end] = b'\xFF' * (_samples_end - SOUND_ROM)
    _moved = []
    for _c in _snd.ISOLATED_CHAINS:
        _w = _snd.MSZ_WAVES + _c.wave * 24
        _o = be32(rom, _w)
        assert SOUND_ROM <= _snd.MSZ_TBL + _o < _samples_end, (_c, hex(_o))
        put32(rom, _w, _o + _shift)
        _moved.append(_c.wave)
    SEKTOR_END = SEKTOR_SAMPLES_ROM + (_samples_end - SOUND_ROM)
    assert SEKTOR_END <= OUTPUT_SIZE
    _log('V49_PLACEMENT', 'file87', hex(SEKTOR_FILE87_ROM), hex(SEKTOR_FILE87_ROM + 0x459E0), 'samples', hex(SEKTOR_SAMPLES_ROM),
          hex(SEKTOR_END), 'waves repointed', len(_moved), 'region', hex(SEKTOR_ROM), hex(SEKTOR_END))

    if True:                                                                    # v50
        _manifest = ({
            'fixed_va': FIXED_VA, 'fixed_len': len(FIXED), 'fixed_rom': PAYLOAD_ROM,
            'load_wrapper': _load, 'blob_off': BLOB_OFF, 'table_off': TABLE_OFF, 'blob_end': BLOB_END,
            'file87_rom': SEKTOR_FILE87_ROM, 'file87_size': 0x459E0, 'samples_rom': SEKTOR_SAMPLES_ROM, 'samples_end': SEKTOR_END,
            'refs': [[r.address, r.offset, r.kseg0] for r in _refs],
            'jal_sites': {hex(o): b for o, b in _jal_sites.items()},
        })

    # CIC-6102 CRC.
    def rol32(v,s):
        s&=31
        return v&0xffffffff if s==0 else ((v<<s)|(v>>(32-s)))&0xffffffff
    seed=0xF8CA4DDC; t1=t2=t3=t4=t5=t6=seed
    for off in range(0x1000,0x101000,4):
        value=be32(rom,off); total=(t6+value)&0xffffffff
        if total<t6:t4=(t4+1)&0xffffffff
        t6=total; t3^=value; r=rol32(value,value&31); t5=(t5+r)&0xffffffff; t2^=r if t2>value else (t6^value); t1=(t1+(t5^value))&0xffffffff
    crc1=(t6^t4^t3)&0xffffffff; crc2=(t5^t2^t1)&0xffffffff
    put32(rom,0x10,crc1); put32(rom,0x14,crc2)

    _log('SHA256',hashlib.sha256(rom).hexdigest())
    _log('CRC',f'{crc1:08X} / {crc2:08X}')
    _log('FILE87_SIZE',hex(NEW_END),'HEADROOM_V49',hex(SAFE_V49-NEW_END))
    _log('FRAMES',len(all_keys),'OLD',len(old_shapes),'RUN_ASSETS',len(RUN_RELS),'RUN_VISUAL_UNIQUE',len(set(run_words[:6])),'COMBO',len(COMBO_RELS),'THROW_KEYFRAMES',len(THROW_KEYS))
    _log('THROW_ARMS',[hex(r) for r in ARM_RELS]); _log('THROW_GEOMETRY',{hex(r):(throw_frames[('throw-composite',r)]['w'],throw_frames[('throw-composite',r)]['h'],throw_frames[('throw-composite',r)]['x'],throw_frames[('throw-composite',r)]['y']) for r in ARM_RELS})
    _log('THROW_SEQUENCE',{pos:('RBSTANCE7' if shp==throw_stance else next(hex(r) for r,v in throw_shapes.items() if v==shp)) for pos,shp in throw_sequence.items()})
    _log('MODELS',len(groups),'PATTERNS',patterns_count,'TABLE',hex(TABLE_BYTES),'STREAMS',hex(STREAM_BYTES))
    _log('TYPE_TABLE_ALIGN_PAD',hex(align4(TYPE_START+TABLE_BYTES)-(TYPE_START+TABLE_BYTES)))
    _log('SCRIPT_PACK','five former append scripts in dead pre-Type5 regions; High Kick packed item only')
    _log('PUSH_SCRIPT',[hex(x) for x in push_words]); _log('RUN_LIVE_SCRIPT',[hex(x) for x in run_words]); _log('RUN_POLICY','six genuine retail N64 poses only, immediate loop to +0xEE8, MKMSZ Run rate 3')
    _log('RUN_RATE_PATCH','ROM 0x2F7A0: 24040002 -> 24040003')
    _log('COMPACT_REPACK',len(all_keys),'frames /',patterns_count,'patterns / 16-colour 4-bpp')
    _log('TELEPORT_SCRIPTS',{k:hex(v) for k,v in scripts.items()},'FILE87_END',hex(NEW_END_TELE),'HEADROOM_V49',hex(SAFE_V49-NEW_END_TELE))
    _log('TELEPORT_PAYLOAD',hex(len(payload)),'bytes at ROM',hex(PAYLOAD_ROM),'-> 0x801AF420; strike record on stack (KSEG0)', [hex(x) for x in _params.strike_words])
    _log('ALIASES','sink',[hex(x) for x in sink_alias][:3],'... emerge',[hex(x) for x in emerge_alias][:3],'...','depths',SINK_DEPTHS,EMERGE_DEPTHS,'range',RANGE_UNITS)
    _log('TELEPORT_PHYSICS',dict(emerge_vel=hex(EMERGE_VEL&0xffffffff),grav_nohit=hex(GRAV_NOHIT),grav_hit=hex(GRAV_HIT),drop_rate=DROP_RATE,sink=SINK_TICKS,hidden=HIDDEN_TICKS,cap=AIR_CAP,x_offset=X_OFFSET))
    _log('COND',hex(COND_VA))
    _log('TEST_INPUT','Forward, Forward + Low Kick (classic controls, ground or air), target within 592 world units (square) on the same path')
    _log('COMBO_SEQUENCE','RBELBOCOMBO 1,2,3 / 2,1 / 4,5,6 / 7,8,9,10,9')
    _log('THROW_VISUAL_POSITIONS',throw_visual_pos)
    _log('FALLBACK_STOCK_SHAPE_REFS',len(fallback_positions))
    _log('ARM_PALETTE_MAP',ARM_TO_SEKTOR); _log('RUN_SUPPLEMENTAL_DEPENDENCIES','NONE'); _log('SWEEP_FALL_MODELS',[frame_model[x] for x in slot_cfg[0x1F]['shapes']]); _log('HELPER','REMOVED / native v53 palette architecture retained')
    return {'rom': bytes(rom), 'manifest': _manifest, 'log': _log_lines}
