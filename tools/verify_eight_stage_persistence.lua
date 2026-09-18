-- BizHawk read-only verifier for the eight-stage ordinary-pickup persistence test.
-- BizHawk 2.11.1 / Ares64. Use a fresh cold boot; do not load savestates.

memory.usememorydomain("RDRAM")

local STAGES = {
    [0] = { name = "Temple",   expected = 4,  bits = 0x1AF644 },
    [1] = { name = "Wind",     expected = 6,  bits = 0x1AF648 },
    [2] = { name = "Water",    expected = 9,  bits = 0x1AF64C },
    [3] = { name = "Earth",    expected = 20, bits = 0x1AF650 },
    [4] = { name = "Prison",   expected = 10, bits = 0x1AF654 },
    [5] = { name = "Fire",     expected = 19, bits = 0x1AF640 },
    [8] = { name = "Bridge",   expected = 10, bits = 0x1AF658 },
    [9] = { name = "Fortress", expected = 9,  bits = 0x1AF65C },
}

local function u32(addr)
    return memory.read_u32_be(addr)
end

local function rdram_offset(ptr)
    if ptr >= 0x80000000 and ptr < 0x80800000 then
        return ptr - 0x80000000
    end
    if ptr >= 0xA0000000 and ptr < 0xA0800000 then
        return ptr - 0xA0000000
    end
    return nil
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

    local stage = u32(0x09A910)
    local info = STAGES[stage]

    local contextPtr = u32(0x2ECE20)
    local contextOff = rdram_offset(contextPtr)
    local liveCount = -1
    local recordBase = 0
    if contextOff ~= nil then
        liveCount = u32(contextOff + 0x6F4)
        recordBase = u32(contextOff + 0x6F8)
    end

    gui.text(12, 12, "MKMSZR eight-stage pickup persistence")
    gui.text(12, 30, string.format(
        "V1 header: %s  magic=%08X ver=%d size=%X hdr=%X",
        headerOk and "YES" or "NO", magic, version, stateSize, headerSize
    ))

    if info ~= nil then
        local bits = u32(info.bits)
        local managerReady = contextOff ~= nil and recordBase ~= 0 and liveCount >= 0
        local guardText = "WAIT"
        if managerReady then
            guardText = (liveCount == info.expected) and "OK" or "FAIL"
        end
        gui.text(12, 48, string.format(
            "Stage=%d %s  manager=%d/%d  guard=%s",
            stage, info.name, liveCount, info.expected, guardText
        ))
        gui.text(12, 66, string.format(
            "Bits=%08X  collected ordinary bits=%d",
            bits, bitcount32(bits)
        ))
        gui.text(12, 84, string.format(
            "Manager ctx=%08X  records=%08X",
            contextPtr, recordBase
        ))
        if not managerReady then
            gui.text(12, 142, "Manager not initialized yet; WAIT is normal outside gameplay.")
        end
    else
        gui.text(12, 48, string.format(
            "Stage=%d (not an ordinary-pickup descriptor stage)", stage
        ))
        gui.text(12, 66, string.format(
            "Manager ctx=%08X  live count=%d",
            contextPtr, liveCount
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
