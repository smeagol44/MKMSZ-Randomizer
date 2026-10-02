"""Production Toasty composition patch."""

import hashlib

from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext
from .box_indicator import BOX_REGION, BOX_REGION_ROM
from .game_settings_turn import CONTROL_MODULE, SHARED_EXPANSION_ROM
from .toasty_codegen import (
    NOP,
    _build_call_trampoline,
    _build_init_loader,
    jal,
    jump,
    pack_toasty_module,
)
from .toasty_constants import *


class ToastyProductionCompositionPatch:
    """Compose the runtime-confirmed Toasty feature with the current production pipeline."""

    name='toasty-production-composition'

    def __init__(self,assets:ToastyAssets,*,probability_per_thousand:int=DEFAULT_PROBABILITY_PER_THOUSAND):
        self.assets=assets
        self.probability_per_thousand=probability_per_thousand
        self.module=pack_toasty_module(assets,probability_per_thousand)

    def apply(self,rom:RomImage,context:PatchContext)->tuple[str,...]:
        del context
        module=self.module.data
        module_end=MODULE_ROM+len(module)
        audio_rom=TOASTY_AUDIO_ROM
        audio_end=TOASTY_AUDIO_END_ROM
        if module_end>audio_rom:
            raise PatchError("Toasty module reaches fixed audio allocation")
        if audio_end>TOASTY_ROM_LIMIT:
            raise PatchError("Toasty high-ROM allocation exceeds audited bound")

        rom.expect_bytes(REACTION_HOOK_ROM,EXPECTED_REACTION_HOOK)
        rom.expect_bytes(HUD_HOOK_ROM,EXPECTED_HUD_HOOK)
        rom.expect_bytes(POST13_HOOK_ROM,EXPECTED_POST13_HOOK)
        control_end_rom = SHARED_EXPANSION_ROM + len(CONTROL_MODULE)
        expected_shared_entry = (
            SHARED_EXPANSION_ROM.to_bytes(4, "big")
            + control_end_rom.to_bytes(4, "big")
            + bytes(4)
        )
        rom.expect_bytes(EXPANSION_FILE_ENTRY_ROM, expected_shared_entry)
        rom.expect_bytes(SHARED_EXPANSION_ROM, CONTROL_MODULE)
        rom.expect_bytes(SELECTOR_CAVE_ROM,SELECTOR_CAVE_BLOB)
        rom.expect_bytes(INIT_LOADER_ROM,bytes(INIT_LOADER_END-INIT_LOADER_ROM))
        rom.expect_bytes(BOX_REGION_ROM,BOX_REGION)
        rom.expect_bytes(
            control_end_rom,
            b"\xFF" * (MODULE_ROM - control_end_rom),
        )
        rom.expect_bytes(MODULE_ROM,b'\xFF'*len(module))
        rom.expect_bytes(audio_rom,b'\xFF'*len(self.assets.audio_sample))
        for selector,callback in zip(QUALIFYING_REACTION_SELECTORS,QUALIFYING_REACTION_CALLBACKS,strict=True):
            if rom.read_u32(TARGET_REACTION_TABLE_ROM+selector*4)!=callback:
                raise PatchError(f"Toasty reaction selector 0x{selector:02X} no longer resolves to expected callback")

        rom.expect_bytes(PICKUP_DESC_ROM,EXPECTED_DESC_3B);rom.expect_bytes(SSEQ_ENTRY_524,EXPECTED_ENTRY_524)
        rom.expect_bytes(PATCH_681_ROM,EXPECTED_PATCH_681);rom.expect_bytes(SUBPATCH_524_ROM,EXPECTED_SUBPATCH_524)
        rom.expect_bytes(WAVE_133_ROM,EXPECTED_WAVE_133)

        rom.expect_bytes(PATCH_68_ROM,EXPECTED_PATCH_68);rom.expect_bytes(SUBPATCH_608_ROM,EXPECTED_SUBPATCH_608)
        rom.expect_bytes(EVENT_52_DATA_ROM,EXPECTED_EVENT_52);rom.expect_bytes(EVENT_52_PATCH_ROM,EXPECTED_EVENT_52_PATCH)
        rom.expect_bytes(WAVE_533_ROM,EXPECTED_WAVE_533)
        pred=bytes(rom.data[PRED_533_ROM:PRED_533_ROM+264])
        if hashlib.sha256(pred).hexdigest()!=EXPECTED_PRED_533_SHA256:
            raise PatchError("Toasty target predictor-533 guard failed")

        for file_id in range(0xAC):
            if file_id==EXPANSION_FILE_ID: continue
            entry=FILE_TABLE_ROM+file_id*FILE_TABLE_ENTRY_SIZE
            start=rom.read_u32(entry);end=rom.read_u32(entry+4)
            if start and end and end>start:
                overlaps_shared = not (end<=SHARED_EXPANSION_ROM or start>=module_end)
                overlaps_audio = not (end<=audio_rom or start>=audio_end)
                if overlaps_shared or overlaps_audio:
                    raise PatchError(f"Toasty high-ROM allocation overlaps file 0x{file_id:02X}")

        sub=bytearray(self.assets.audio_subpatch);sub[0x0A:0x0C]=TARGET_WAVE_ID.to_bytes(2,'big')
        wave=bytearray(self.assets.audio_wave);wave[0:4]=(audio_rom-MKMSZ_TBL_BASE).to_bytes(4,'big')
        rom.write_bytes(SUBPATCH_608_ROM,bytes(sub));rom.write_bytes(WAVE_533_ROM,bytes(wave))
        rom.write_bytes(PRED_533_ROM,self.assets.audio_predictor);rom.write_bytes(EVENT_52_PATCH_ROM,TOASTY_EVENT_52_PATCH)
        rom.write_bytes(audio_rom,self.assets.audio_sample)

        rom.write_u32(EXPANSION_FILE_ENTRY_ROM,SHARED_EXPANSION_ROM)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM+4,module_end)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM+8,0)
        rom.write_bytes(MODULE_ROM,module)

        init_loader=_build_init_loader();call_tramp=_build_call_trampoline()
        if len(init_loader)>INIT_LOADER_END-INIT_LOADER_ROM or len(call_tramp)!=CALL_TRAMP_END-CALL_TRAMP_ROM:
            raise AssertionError("Toasty static entry stubs exceed owned production padding")
        rom.write_bytes(INIT_LOADER_ROM,init_loader)
        rom.write_bytes(CALL_TRAMP_ROM,call_tramp)
        rom.write_u32(POST13_HOOK_ROM,jump(INIT_LOADER_VA));rom.write_u32(POST13_HOOK_ROM+4,NOP)
        rom.write_u32(HUD_HOOK_ROM,jal(CALL_TRAMP_VA));rom.write_u32(REACTION_HOOK_ROM,jal(CALL_TRAMP_VA))

        rom.expect_bytes(PICKUP_DESC_ROM,EXPECTED_DESC_3B);rom.expect_bytes(SSEQ_ENTRY_524,EXPECTED_ENTRY_524)
        rom.expect_bytes(PATCH_681_ROM,EXPECTED_PATCH_681);rom.expect_bytes(SUBPATCH_524_ROM,EXPECTED_SUBPATCH_524)
        rom.expect_bytes(WAVE_133_ROM,EXPECTED_WAVE_133)

        return (
            (
                f"shared file 0x{EXPANSION_FILE_ID:02X}: TURN prefix at "
                f"0x{SHARED_EXPANSION_ROM:08X}; Toasty ROM "
                f"0x{MODULE_ROM:08X}..0x{MODULE_ROM+len(module)-1:08X} -> "
                f"RDRAM 0x{MODULE_K0:08X}"
            ),
            f"dedicated Toasty audio sample ROM 0x{audio_rom:08X}..0x{audio_end-1:08X}; stock pickup audio unchanged",
            f"successful-reaction family uses {self.probability_per_thousand}/1000 test/product gate",
            "v42 3/16/8 lower-right presentation retained",
        )
