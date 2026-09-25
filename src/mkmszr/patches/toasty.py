"""Production Toasty composition patch."""

import hashlib

from ..errors import PatchError
from ..rom import RomImage
from .base import PatchContext
from .toasty_codegen import (
    _align,
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
        audio_rom=_align(MODULE_ROM+len(module),16)
        audio_end=audio_rom+len(self.assets.audio_sample)
        if audio_end>TITLE_ROM_START:
            raise PatchError("Toasty high-ROM allocation reaches title reservation")

        rom.expect_bytes(REACTION_HOOK_ROM,EXPECTED_REACTION_HOOK)
        rom.expect_bytes(HUD_HOOK_ROM,EXPECTED_HUD_HOOK)
        rom.expect_bytes(POST13_HOOK_ROM,EXPECTED_POST13_HOOK)
        rom.expect_bytes(EXPANSION_FILE_ENTRY_ROM,bytes(FILE_TABLE_ENTRY_SIZE))
        rom.expect_bytes(SELECTOR_CAVE_ROM,SELECTOR_CAVE_BLOB)
        rom.expect_bytes(INIT_LOADER_ROM,bytes(INIT_LOADER_END-INIT_LOADER_ROM))
        rom.expect_bytes(BOX_REGION_ROM,BOX_REGION)
        rom.expect_bytes(MODULE_ROM,b'\xFF'*(audio_end-MODULE_ROM))
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
            if start and end and end>start and not (end<=MODULE_ROM or start>=audio_end):
                raise PatchError(f"Toasty high-ROM allocation overlaps file 0x{file_id:02X}")

        sub=bytearray(self.assets.audio_subpatch);sub[0x0A:0x0C]=TARGET_WAVE_ID.to_bytes(2,'big')
        wave=bytearray(self.assets.audio_wave);wave[0:4]=(audio_rom-MKMSZ_TBL_BASE).to_bytes(4,'big')
        rom.write_bytes(SUBPATCH_608_ROM,bytes(sub));rom.write_bytes(WAVE_533_ROM,bytes(wave))
        rom.write_bytes(PRED_533_ROM,self.assets.audio_predictor);rom.write_bytes(EVENT_52_PATCH_ROM,TOASTY_EVENT_52_PATCH)
        rom.write_bytes(audio_rom,self.assets.audio_sample)

        rom.write_u32(EXPANSION_FILE_ENTRY_ROM,MODULE_ROM)
        rom.write_u32(EXPANSION_FILE_ENTRY_ROM+4,MODULE_ROM+len(module))
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
            f"Toasty module ROM 0x{MODULE_ROM:08X}..0x{MODULE_ROM+len(module)-1:08X} -> RDRAM 0x{MODULE_K0:08X}",
            f"dedicated Toasty audio sample ROM 0x{audio_rom:08X}..0x{audio_end-1:08X}; stock pickup audio unchanged",
            f"successful-reaction family uses {self.probability_per_thousand}/1000 test/product gate",
            "v42 3/16/8 lower-right presentation retained",
        )
