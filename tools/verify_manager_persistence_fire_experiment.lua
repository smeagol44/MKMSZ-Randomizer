-- BizHawk verifier for the manager-level Fire persistence experiment.
-- Use with BizHawk 2.11.1 / Ares64 and a fresh cold boot. Do not load savestates.

memory.usememorydomain("RDRAM")

local function u32(addr)
    return memory.read_u32_be(addr)
end

local function yesno(value)
    if value then return "YES" end
    return "NO"
end

while true do
    local magic = u32(0x1AF620)
    local version = u32(0x1AF624)
    local stateSize = u32(0x1AF628)
    local headerSize = u32(0x1AF62C)
    local fireBits = u32(0x1AF640)
    local stage = u32(0x09A910)
    local nativeFlag = u32(0x2F14F4)
    local callback = u32(0x2F14E0)

    local headerOk =
        magic == 0x4D4B5356 and
        version == 1 and
        stateSize == 0x200 and
        headerSize == 0x20

    gui.text(12, 12, "MKMSZR manager persistence Fire experiment")
    gui.text(12, 30, string.format(
        "V1 header: %s  magic=%08X ver=%d size=%X hdr=%X",
        yesno(headerOk), magic, version, stateSize, headerSize
    ))
    gui.text(12, 48, string.format(
        "Stage=%d  Fire bits=%08X  bit0=%d",
        stage, fireBits, fireBits & 1
    ))
    gui.text(12, 66, string.format(
        "Potion native flag=%08X  callback=%08X",
        nativeFlag, callback
    ))

    if callback == 0x800388FC then
        gui.text(12, 84, "Potion callback: VANILLA (expected)")
    else
        gui.text(12, 84, "Potion callback: NOT VANILLA")
    end

    emu.frameadvance()
end
