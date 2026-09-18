-- BizHawk read-only verifier for the eight-stage ordinary-pickup persistence.
-- BizHawk 2.11.1 / Ares64. Use a fresh cold boot; do not load savestates.
--
-- The pickup-manager context at 0x802ECE20 is only meaningful during the
-- manager setup/restore path, so do not poll it every frame as a gameplay
-- readiness test. The old Lua randomizer already established 0x0B56D4 >= 0x10
-- as the reliable gameplay gate used by all stage pickup checks.

memory.usememorydomain("RDRAM")

local GAMEPLAY = 0x0B56D4
local STAGE = 0x09A913

local STAGES = {
    [0] = { name = "Temple",   bits = 0x1AF644 },
    [1] = { name = "Wind",     bits = 0x1AF648 },
    [2] = { name = "Water",    bits = 0x1AF64C },
    [3] = { name = "Earth",    bits = 0x1AF650 },
    [4] = { name = "Prison",   bits = 0x1AF654 },
    [5] = { name = "Fire",     bits = 0x1AF640 },
    [8] = { name = "Bridge",   bits = 0x1AF658 },
    [9] = { name = "Fortress", bits = 0x1AF65C },
}

local function u32(addr)
    return memory.read_u32_be(addr)
end

local function bitcount32(value)
    local count = 0
    for i = 0, 31 do
        if (value & (1 << i)) ~= 0 then count = count + 1 end
    end
    return count
end

while true do
    local magic = u32(0x1AF620)
    local version = u32(0x1AF624)
    local stateSize = u32(0x1AF628)
    local headerSize = u32(0x1AF62C)
    local headerOk =
        magic == 0x4D4B5356 and
        version == 1 and
        stateSize == 0x200 and
        headerSize == 0x20

    local gameplay = u32(GAMEPLAY)
    local inGameplay = gameplay >= 0x10
    local stage = memory.readbyte(STAGE)
    local info = STAGES[stage]

    gui.text(12, 12, "MKMSZR pickup persistence")
    gui.text(12, 30, string.format(
        "V1 header: %s  magic=%08X ver=%d size=%X hdr=%X",
        headerOk and "YES" or "NO", magic, version, stateSize, headerSize
    ))
    gui.text(12, 48, string.format(
        "Gameplay=%08X  active=%s",
        gameplay, inGameplay and "YES" or "NO"
    ))

    if inGameplay and info ~= nil then
        local bits = u32(info.bits)
        gui.text(12, 66, string.format(
            "Stage=%d %s  Bits=%08X  collected ordinary bits=%d",
            stage, info.name, bits, bitcount32(bits)
        ))
        gui.text(12, 84, "Test: collect ordinary pickup -> bit changes -> quit/re-enter -> item stays absent")
    elseif info ~= nil then
        gui.text(12, 66, string.format(
            "Stage byte=%d (%s), but gameplay is not active yet",
            stage, info.name
        ))
        gui.text(12, 84, "Waiting for gameplay; title/menu/transition states are ignored.")
    else
        gui.text(12, 66, string.format(
            "Stage byte=%d (no ordinary-pickup descriptor)",
            stage
        ))
    end

    gui.text(12, 106, string.format(
        "Fire=%08X Temple=%08X Wind=%08X Water=%08X",
        u32(0x1AF640), u32(0x1AF644), u32(0x1AF648), u32(0x1AF64C)
    ))
    gui.text(12, 124, string.format(
        "Earth=%08X Prison=%08X Bridge=%08X Fortress=%08X",
        u32(0x1AF650), u32(0x1AF654), u32(0x1AF658), u32(0x1AF65C)
    ))

    emu.frameadvance()
end
