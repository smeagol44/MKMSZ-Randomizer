-- Read-only BizHawk verifier for MKMSZR stage-local key masking.
-- BizHawk 2.11.1 / Ares64. This script never writes RDRAM.

memory.usememorydomain("RDRAM")

local LIVE = 0x0A600C
local BOXES = {
    0x0A6048,
    0x0A6070,
    0x0A6098,
    0x0A60C0,
}
local STATE = 0x0A60E8
local MAGIC = 0x0A60EC
local STAGE = 0x09A913

local allowed = {
    [0] = "Temple: Map 0D",
    [1] = "Wind: 0E-10",
    [2] = "Water: 14-16",
    [3] = "Earth: 11-13",
    [4] = "Prison: 1A-1C",
    [5] = "Fire: 17-19",
    [8] = "Bridge: 1D-1F",
    [9] = "Fortress: 20-22",
}

local function u32(addr)
    return memory.read_u32_be(addr)
end

local function slots(base)
    local values = {}
    for i = 0, 9 do
        values[#values + 1] = string.format("%02X", u32(base + i * 4) & 0xFF)
    end
    return table.concat(values, " ")
end

while true do
    local state = u32(STATE)
    local active = (state & 0x3) + 1
    local stage = memory.readbyte(STAGE)

    gui.text(12, 12, "MKMSZR key-item stage masking")
    gui.text(12, 30, string.format(
        "MKBX=%08X  active=BOX %d / 4  stage=%d",
        u32(MAGIC), active, stage
    ))
    gui.text(12, 48, "Allowed: " .. (allowed[stage] or "no stage-local keys"))

    gui.text(12, 72, "LIVE : " .. slots(LIVE))
    for i = 1, 4 do
        local marker = (i == active) and ">" or " "
        gui.text(12, 72 + i * 18, string.format(
            "%sBOX%d: %s", marker, i, slots(BOXES[i])
        ))
    end

    gui.text(12, 164, "08 in LIVE = masked Glass placeholder")
    gui.text(12, 182, "Backing boxes should retain the true key IDs.")

    emu.frameadvance()
end
