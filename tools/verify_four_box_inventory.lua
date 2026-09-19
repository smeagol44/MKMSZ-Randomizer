-- BizHawk read-only verifier for MKMSZR four-box inventory experiment.
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
local INVENTORY_OPEN = 0x0A5FA3
local ACTIONS = 0x0BF2EE
local GAMEPLAY = 0x0B56D4
local STAGE = 0x09A913

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
    local latch = (state & 0x100) ~= 0
    local magic = u32(MAGIC)
    local gameplay = u32(GAMEPLAY)
    local stage = memory.readbyte(STAGE)
    local invOpen = memory.readbyte(INVENTORY_OPEN)
    local actions = memory.read_u16_be(ACTIONS)

    gui.text(12, 12, "MKMSZR 4-box inventory - phase 1")
    gui.text(12, 30, string.format(
        "MKBX=%08X  active=BOX %d / 4  latch=%s",
        magic, active, latch and "ON" or "off"
    ))
    gui.text(12, 48, string.format(
        "stage=%d gameplay=%08X invOpen=%d actions=%04X",
        stage, gameplay, invOpen, actions
    ))

    gui.text(12, 72, "LIVE : " .. slots(LIVE))
    for i = 1, 4 do
        local marker = (i == active) and ">" or " "
        gui.text(12, 72 + i * 18, string.format(
            "%sBOX%d: %s", marker, i, slots(BOXES[i])
        ))
    end

    gui.text(12, 164, "Switch outside inventory: Block + Use + Left/Right")
    gui.text(12, 182, "Right: next box   Left: previous box   wraps 1 <-> 4")

    emu.frameadvance()
end
