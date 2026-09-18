memory.usememorydomain("RDRAM")

cfg_difficultymem = 0x0A5FA9
cfg_livesmem = 0x0A5FAB
cfg_continuesmem = 0x0A5FAD
menustop = false
currentmenumem = 0x0FD87B
frame = 0
seed = 0
seedLabel = ""
seedPass = {66,66,66,66,66,66}
gameplaymem = 0x0B56D4

quanchixp = 0
reqpowers = 0
quanchixpmem = 0x2EF49E

-- Consonant alphabet for seed (A–Z excluding A, E, I, O, U)
local consonants = {}
local charToDigit = {}
local excluded = { [65]=true, [69]=true, [73]=true, [79]=true, [85]=true }

for c = 65, 90 do
	if not excluded[c] then
		table.insert(consonants, c)
		charToDigit[c] = #consonants - 1
	end
end

local lastPassRead = {0, 0, 0, 0, 0, 0}

-- Password characters
passtitle1mem = 0x0AE948
passtitle2mem = 0x0AE94C

pass1mem = 0x0AE940
pass2mem = 0x0AE941
pass3mem = 0x0AE942
pass4mem = 0x0AE943
pass5mem = 0x0AE944
pass6mem = 0x0AE945

-- Button actions
buttonmem_A = 0x1114CD
buttonmem_B = 0x1114C9
buttonmem_L = 0x1114CF
buttonmem_R = 0x1114CB
buttonmem_CU = 0x1114D1
buttonmem_CR = 0x1114D3
buttonmem_CD = 0x1114D5
buttonmem_CL = 0x1114D7


--[[

Future ideas!
	- Add checks that are gotten from gaining in-game XP (first three "powerups"??). This could be done by tracking xp gained in a variable in this script before erasing it with overrideXP(). Actually, the same overrideXP() function can add whatever XP was gained up to that frame before erasing it. Then, as soon as that variable hits certain predefined numbers (1000, 2000 and 3000) the player is awarded with an item. Before randomizing the items, 3 new items should be added into the pool, then shuffled, then 3 random taken from it (or maybe just the first three?) and those 3 add them to a separate array that is going to be the "XP award pickups". This makes it so full avoidance of combat is discouraged and however required XP thresholds are little enough so that farming is not encouraged either
	
	- Add checks for bosses. This can be done by tracking level number and "enemy bar" value. 
	
	- Add checks for stage clear. This can be done by tracking from and to values of stages (if 0 then 1 == first mission level is clear).
	
	- Make base abilities as items. Easily done by removing button bindings on stage load. Recommended abilities to remove from least impactful to most: block, run, turn, low punch. 

--]]

--[[
Default values:
A = 02
B = 01
L = 08
R = 04
CU = 20
CR = 40
CD = 80
CL = 10

Digits:
01 - Turn
02 - Action
04 - Run
08 - Block
10 - High Punch
20 - High Kick
40 - Low Kick
80 - Low Punch

The Rest of the digits:
00 - Nothing
01 - Turn
02 - Action
03 - Turn
04 through 07 - Run
08 through 0F - Block
10 through 1F - High Punch
20 through 2F - High Kick
30 through 3F - High Punch
40 through 4F - Low Kick
50 through 5F - High Punch
60 through 6F - High Kick
70 through 7F - High Punch
80 through 8F - Low Punch
90 through 9F - High Punch
A0 through AF - Low Punch
B0 through BF - High Punch
C0 through CF - Low Punch
D0 through DF - High Punch
E0 through EF - Low Punch
F0 through FF - High Punch
--]]

--Stage Select Gameshark Code. I'm using this code but writing it from the lua script instead of loading a gameshark cheat.
--8100D42A 342E 
herbsmem = 0x0AD828
tabmem = 0x0AD814
glassmem = 0x0AD80C
lifemem = 0x0F1057 -- 
inputmem = 0x09A5A0 -- inputs as value. Every input the player does can be seen in this address, or the following 3 bytes. 
inputmem2 = 0x09A5A3
stageselectmem = 0x00D42A
inventoryopenmem = 0x0A5FA3
stagemem = 0x09A913 -- stage as value. When a stage is loaded, this address has the corresponding value to a stage.
--values for stages
--0 First mission
--1 Wind Temple
--3 Earth Temple
--2 Water Temple
--5 Fire Temple
--4 Prison Escape
--8 Bridge
--9 Fortress

currentexp = 0
currentexpmem = 0x11200E
maxpossiblexp = 0x270F

powerupgrade1 = 0x0055 --85
powerupgrade2 = 0x0102 --258
powerupgrade3 = 0x0342 --834
powerupgrade4 = 0x0582 --1410
powerupgrade5 = 0x0913 --2323
powerupgrade6 = 0x0CF3 --3315
powerupgrade7 = 0x1197 --4503
powerupgrade8 = 0x1717 --5911
powerupgrade9 = 0x1CBA --7345

maxexpmem_stg1 = 0x0A63FC --260
maxexpmem_stg2 = 0x0A63FE --875
maxexpmem_stg3 = 0x0A6402 --1425
maxexpmem_stg4 = 0x0A6400 --2375
maxexpmem_stg5 = 0x0A6406 --3350
maxexpmem_stg6 = 0x0A6404 --4525
maxexpmem_stg7 = 0x0A640C --7375
maxexpmem_stg8 = 0x0A640E --20000

inventorySlot01 = 0x0A600C
inventorySlot02 = 0x0A6010
inventorySlot03 = 0x0A6014
inventorySlot04 = 0x0A6018
inventorySlot05 = 0x0A601C
inventorySlot06 = 0x0A6020
inventorySlot07 = 0x0A6024
inventorySlot08 = 0x0A6028
inventorySlot09 = 0x0A602C
inventorySlot10 = 0x0A6030

inventoryPages = 0
currentPage = 1
invInitCheck = false
skipNextItemUseDetection = false
gameInventory = {inventorySlot01, inventorySlot02, inventorySlot03, inventorySlot04, inventorySlot05, inventorySlot06, inventorySlot07, inventorySlot08, inventorySlot09, inventorySlot10}

randoInventory = {} -- this is going to be the "actual" inventory. The one that can hold over 10 items. It's called "rando" because this whole project is to make a randomizer of the game, so this is the inventory "of the randomizer", hence randoInventory.
lastInventoryState = {}
inventoryFrozen = false
forceReloadOnOpen = false  -- helps delay loading until game re-renders its list
inventoryOpenLastFrame = false
lastRemovedSlotIndex = nil
pickupMessage = ""
pickupTimer = 0
mapPickupWindow = 0
inventoryOpenCounter = 0
heldKeyItems = {} -- Temporarily removed key items (used Glass visuals)

-- Item list
item_Empty = 0xFFFFFFFF
item_Antidote = 0x00000000 
item_Potion = 0x00000001 
item_Formula = 0x00000002 
item_Eye = 0x00000003 
item_Herbs = 0x00000004 
item_Urn_Replenish_Health = 0x00000005 
item_Shield = 0x00000006 
item_Tablet = 0x00000007 
item_Glass = 0x00000008 -- Key items dummy
item_Antidote2 = 0x00000009 
item_Urn_Extra_Life = 0x0000000A 
item_Urn_Super_Strength = 0x0000000B 
item_Healer = 0x0000000C 
item_Map = 0x0000000D 
item_Wind_Icon_Circle = 0x0000000E 
item_Wind_Icon_3_Bars = 0x0000000F 
item_Wind_Icon_Triangle = 0x00000010 
item_Earth_Icon_Square = 0x00000011 
item_Earth_Icon_4_Square = 0x00000012 
item_Earth_Icon_Triangle = 0x00000013 
item_Water_Icon_3_Bars = 0x00000014 
item_Water_Icon_Triangle = 0x00000015 
item_Water_Icon_Moon = 0x00000016 
item_Fire_Icon_Triangle_Down = 0x00000017 
item_Fire_Icon_2_Bars = 0x00000018 
item_Fire_Icon_Triangle_Up = 0x00000019 
item_Prison_L1_Key = 0x0000001A 
item_Prison_L2_Key = 0x0000001B 
item_Prison_L3_Key = 0x0000001C 
item_Fortress_Icon_Omega = 0x0000001D 
item_Fortress_Icon_Rings = 0x0000001E 
item_Fortress_Icon_Arrow = 0x0000001F 
item_CrystalJataaka = 0x00000020 
item_CrystalKia = 0x00000021 
item_CrystalSareena = 0x00000022
item_ShinnokAmulet = 0x00000023 
item_TabletOfTruth = 0x00000024
item_PowerUpgrade = 0x00000025 
item_Dummy = item_TabletOfTruth 

itemNames = {
    [item_Empty] = "Empty",
    [item_Antidote] = "Antidote",
    [item_Potion] = "Potion",
    [item_Formula] = "Formula",
    [item_Eye] = "Eye",
    [item_Herbs] = "Herbs",
    [item_Urn_Replenish_Health] = "Urn (Vitality)",
    [item_Shield] = "Shield",
    [item_Tablet] = "Tablet",
    [item_Glass] = "Glass",
    [item_Antidote2] = "Antidote II",
    [item_Urn_Extra_Life] = "Urn (Extra Life)",
    [item_Urn_Super_Strength] = "Urn (Strength)",
    [item_Healer] = "Healer",
    [item_Map] = "Map",
    [item_Wind_Icon_Circle] = "Wind Icon Circle",
    [item_Wind_Icon_Triangle] = "Wind Icon Triangle",
    [item_Wind_Icon_3_Bars] = "Wind Icon 3 Bars",
    [item_Earth_Icon_Square] = "Earth Icon Square",
    [item_Earth_Icon_4_Square] = "Earth Icon 4 Squares",
    [item_Earth_Icon_Triangle] = "Earth Icon Triangle",
    [item_Water_Icon_3_Bars] = "Water Icon 3 Bars",
    [item_Water_Icon_Triangle] = "Water Icon Triangle",
    [item_Water_Icon_Moon] = "Water Icon Moon",
    [item_Fire_Icon_Triangle_Down] = "Fire Icon Triangle Down",
    [item_Fire_Icon_2_Bars] = "Fire Icon 2 Bars",
    [item_Fire_Icon_Triangle_Up] = "Fire Icon Triangle Up",
    [item_Prison_L1_Key] = "Prison Level 1 Key",
    [item_Prison_L2_Key] = "Prison Level 2 Key",
    [item_Prison_L3_Key] = "Prison Level 3 Key",
    [item_Fortress_Icon_Omega] = "Bridge Icon Omega",
    [item_Fortress_Icon_Rings] = "Bridge Icon Rings",
    [item_Fortress_Icon_Arrow] = "Bridge Icon Arrow",
    [item_CrystalJataaka] = "Crystal (Jataaka)",
    [item_CrystalKia] = "Crystal (Kia)",
    [item_CrystalSareena] = "Crystal (Sareena)",
    [item_ShinnokAmulet] = "Shinnok's Amulet",
    [item_TabletOfTruth] = "Tablet of Truth",
    [item_PowerUpgrade] = "Power Upgrade"
}

keyItems = {
	item_Map,
	item_Wind_Icon_Circle,
	item_Wind_Icon_Triangle,
	item_Wind_Icon_3_Bars,
	item_Earth_Icon_Square,
	item_Earth_Icon_4_Square,
	item_Earth_Icon_Triangle,
	item_Water_Icon_3_Bars,
	item_Water_Icon_Triangle,
	item_Water_Icon_Moon,
	item_Fire_Icon_Triangle_Down,
	item_Fire_Icon_2_Bars,
	item_Fire_Icon_Triangle_Up,
	item_Prison_L1_Key,
	item_Prison_L2_Key,
	item_Prison_L3_Key,
	item_Fortress_Icon_Omega,
	item_Fortress_Icon_Rings,
	item_Fortress_Icon_Arrow,
	item_CrystalJataaka,
	item_CrystalKia,
	item_CrystalSareena
}

-- Map stage number to valid key items
local keyItemsPerStage = {
    [1] = {item_Wind_Icon_Circle, item_Wind_Icon_Triangle, item_Wind_Icon_3_Bars},
    [2] = {item_Water_Icon_3_Bars, item_Water_Icon_Triangle, item_Water_Icon_Moon},
    [3] = {item_Earth_Icon_Square, item_Earth_Icon_4_Square, item_Earth_Icon_Triangle},
    [4] = {item_Prison_L1_Key, item_Prison_L2_Key, item_Prison_L3_Key},
    [5] = {item_Fire_Icon_Triangle_Down, item_Fire_Icon_2_Bars, item_Fire_Icon_Triangle_Up},
    [8] = {item_Fortress_Icon_Omega, item_Fortress_Icon_Rings, item_Fortress_Icon_Arrow},
    [9] = {item_CrystalJataaka, item_CrystalKia, item_CrystalSareena}
}

itemArrayFull = {item_Antidote, item_Potion, item_Formula, item_Eye, item_Herbs, item_Urn_Replenish_Health, item_Shield, item_Tablet, item_Glass, item_Antidote2, item_Urn_Extra_Life, item_Urn_Super_Strength, item_Healer, item_Map, item_Wind_Icon_Circle, item_Wind_Icon_Triangle, item_Wind_Icon_3_Bars, item_Key_Wind_Icon, item_Earth_Icon_Square, item_Earth_Icon_4_Square, item_Earth_Icon_Triangle, item_Water_Icon_3_Bars, item_Water_Icon_Triangle, item_Water_Icon_Moon, item_Fire_Icon_Triangle_Down, item_Fire_Icon_2_Bars, item_Fire_Icon_Triangle_Up, item_Prison_L1_Key, item_Prison_L2_Key, item_Prison_L3_Key, item_Fortress_Icon_Omega, item_Fortress_Icon_Rings, item_Fortress_Icon_Arrow, item_CrystalJataaka, item_CrystalKia, item_CrystalSareena, item_ShinnokAmulet, item_TabletOfTruth, item_PowerUpgrade}

-- Stage 1 - Temple
stg1_item1 = 0x2F18B8 -- herbs
stg1_item2 = 0x2F18E8 -- herbs
stg1_item3 = 0x2F1918 -- herbs
stg1_item4 = 0x2F1948 -- herbs
stg1_item5 = 0x26E9A4 -- map
stg1_watchTimers = {0,0,0,0,0}  -- cooldown timer per item
stg1_checks = {0,0,0,0,0}
-- This will be shuffled in future. For now, hardcoded test values.
stg1_item_pool = {
	item_Herbs,
	item_Herbs,
	item_Herbs,
	item_Herbs,
	item_Map
}

-- Stage 2 - Wind
stg2_item1 = 0x2F6120 -- herbs
stg2_item2 = 0x2F6150 -- herbs
stg2_item3 = 0x2F6180 -- extra life
stg2_item4 = 0x2F61B0 -- key
stg2_item5 = 0x2F61E0 -- key
stg2_item6 = 0x2F6210 -- key
stg2_watchTimers = {0,0,0,0,0,0}
stg2_checks = {0,0,0,0,0,0}
stg2_item_pool = {
	item_Herbs,
	item_Herbs,
	item_Urn_Extra_Life,
	item_Wind_Icon_Circle,
	item_Wind_Icon_Triangle,
	item_Wind_Icon_3_Bars
}

-- Stage 3 - Earth
stg3_item1 = 0x2F55E0
stg3_item2 = 0x2F5610
stg3_item3 = 0x2F5640
stg3_item4 = 0x2F5550
stg3_item5 = 0x2F5670
stg3_item6 = 0x2F56A0
stg3_item7 = 0x2F5700
stg3_item8 = 0x2F5730
stg3_item9 = 0x2F5760
stg3_item10 = 0x2F56D0
stg3_item11 = 0x2F5580
stg3_item12 = 0x2F5790
stg3_item13 = 0x2F55B0
stg3_item14 = 0x2F57C0
stg3_item15 = 0x2F58B0
stg3_item16 = 0x2F58E0
stg3_item17 = 0x2F57F0
stg3_item18 = 0x2F5820
stg3_item19 = 0x2F5850
stg3_item20 = 0x2F5880
stg3_watchTimers = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
stg3_checks = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
stg3_item_pool = {
	item_Formula,
	item_Urn_Extra_Life,
	item_Herbs,
	item_Earth_Icon_Square,
	item_Urn_Extra_Life,
	item_Herbs, --mana,
	item_Urn_Extra_Life,
	item_Herbs,
	item_Herbs,
	item_Herbs, --mana,
	item_Earth_Icon_4_Square,
	item_Herbs,
	item_Earth_Icon_Triangle,
	item_Urn_Extra_Life,
	item_Eye,
	item_Shield,
	item_Herbs,
	item_Herbs,
	item_Herbs,
	item_Urn_Extra_Life
}

-- Stage 4 - Water
stg4_item1 = 0x2F2A10
stg4_item2 = 0x2F2A40
stg4_item3 = 0x2F2AD0
stg4_item4 = 0x2F2AA0
stg4_item5 = 0x2F2A70
stg4_item6 = 0x2F2B00
stg4_item7 = 0x2F29B0
stg4_item8 = 0x2F2B30
stg4_item9 = 0x2F29E0
stg4_watchTimers = {0,0,0,0,0,0,0,0,0}
stg4_checks = {0,0,0,0,0,0,0,0,0}
stg4_item_pool = {
	item_Herbs, --mana,
	item_Herbs,
	item_Water_Icon_Triangle,
	item_Urn_Extra_Life,
	item_Potion,
	item_Water_Icon_3_Bars,
	item_Urn_Replenish_Health,
	item_Water_Icon_Moon,
	item_Urn_Replenish_Health
}

-- Stage 5 - Fire
stg5_item1 = 0x2F14F4
stg5_item2 = 0x2F1524
stg5_item3 = 0x2F1374
stg5_item4 = 0x2F15E4
stg5_item5 = 0x2F13D4
stg5_item6 = 0x2F13A4
stg5_item7 = 0x2F1644
stg5_item8 = 0x2F1614
stg5_item9 = 0x2F1554
stg5_item10 = 0x2F1494
stg5_item11 = 0x2F1674
stg5_item12 = 0x2F1584
stg5_item13 = 0x2F15B4
stg5_item14 = 0x2F16A4
stg5_item15 = 0x2F14C4
stg5_item16 = 0x2F16D4
stg5_watchTimers = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
stg5_checks = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
stg5_item_pool = {
	item_Urn_Replenish_Health,
	item_Formula,
	item_Urn_Replenish_Health,
	item_Herbs,
	item_Fire_Icon_Triangle_Up,
	item_Urn_Replenish_Health,
	item_Shield,
	item_Herbs,
	item_Urn_Extra_Life,
	item_Fire_Icon_2_Bars,
	item_Urn_Extra_Life,
	item_Eye,
	item_Potion,
	item_Herbs,
	item_Fire_Icon_Triangle_Down,
	item_Herbs
}

-- Stage 6 - Prison
stg6_item1 = 0x2F22DC
stg6_item2 = 0x2F230C
stg6_item3 = 0x2F233C
stg6_item4 = 0x2F236C
stg6_item5 = 0x2F221C
stg6_item6 = 0x2F23CC
stg6_item7 = 0x2F224C
stg6_item8 = 0x2F227C
stg6_item9 = 0x2F239C
stg6_item10 = 0x2F22AC
stg6_watchTimers = {0,0,0,0,0,0,0,0,0,0}
stg6_checks = {0,0,0,0,0,0,0,0,0,0}
stg6_item_pool = {
	item_Herbs,
	item_Herbs,
	item_Herbs,
	item_Herbs,
	item_Prison_L1_Key,
	item_Herbs,
	item_Prison_L2_Key,
	item_Prison_L3_Key,
	item_Herbs,
	item_Urn_Super_Strength
}

-- Stage 7 - Bridge
stg7_item1 = 0x2F1ED4
stg7_item2 = 0x2F1F94
stg7_item3 = 0x2F1FC4
stg7_item4 = 0x2F1F04
stg7_item5 = 0x2F1FF4
stg7_item6 = 0x2F1F64
stg7_item7 = 0x2F1F34
stg7_item8 = 0x2F2054
stg7_item9 = 0x2F2024
stg7_item10 = 0x2F2084
stg7_watchTimers = {0,0,0,0,0,0,0,0,0,0}
stg7_checks = {0,0,0,0,0,0,0,0,0,0}
stg7_item_pool = {
	item_Fortress_Icon_Omega,
	item_Potion,
	item_Herbs,
	item_Fortress_Icon_Rings,
	item_Urn_Extra_Life,
	item_Urn_Replenish_Health,
	item_Fortress_Icon_Arrow,
	item_Urn_Replenish_Health,
	item_Urn_Replenish_Health,
	item_Urn_Replenish_Health
}
-- Stage 8 - Fortress
stg8_item1 = 0x2F14B0
stg8_item2 = 0x2F14E0
stg8_item3 = 0x2F1480
stg8_item4 = 0x2F13C0
stg8_item5 = 0x2F13F0
stg8_item6 = 0x2F1390
stg8_item7 = 0x2F1450
stg8_item8 = 0x2F1360
stg8_item9 = 0x2F1420
stg8_watchTimers = {0,0,0,0,0,0,0,0,0}
stg8_checks = {0,0,0,0,0,0,0,0,0}
stg8_item_pool = {
	item_Herbs,
	item_Herbs,
	item_Herbs,
	item_CrystalSareena,
	item_Herbs,
	item_CrystalJataaka,
	item_Herbs,
	item_CrystalKia,
	item_Herbs
}	

local powerUpgradeXPLevels = {
	[0] = 0x0000,
	[1] = powerupgrade1,
	[2] = powerupgrade2,
	[3] = powerupgrade3,
	[4] = powerupgrade4,
	[5] = powerupgrade5,
	[6] = powerupgrade6,
	[7] = powerupgrade7,
	[8] = powerupgrade8,
	[9] = powerupgrade9
}

local keyStageColors = {
	[1] = "skyblue",   		-- Wind
	[2] = "royalblue",	-- Water
	[3] = "sienna",    		-- Earth
	[4] = "darkgreen", 		-- Prison
	[5] = "orangered", 		-- Fire
	[8] = "gold",      		-- Bridge
	[9] = "fuchsia"    		-- Fortress
}

-- Each key item's icon shape: "circle", "square", "triangleUp", "triangleDown", etc.
local keyItemShapes = {
	[item_Wind_Icon_Circle] = "circle",
	[item_Wind_Icon_Triangle] = "triangleUp",
	[item_Wind_Icon_3_Bars] = "square",

	[item_Water_Icon_3_Bars] = "square",
	[item_Water_Icon_Triangle] = "triangleDown",
	[item_Water_Icon_Moon] = "circle",

	[item_Earth_Icon_Square] = "square",
	[item_Earth_Icon_4_Square] = "square",
	[item_Earth_Icon_Triangle] = "triangleDown",

	[item_Prison_L1_Key] = "square",
	[item_Prison_L2_Key] = "square",
	[item_Prison_L3_Key] = "square",

	[item_Fire_Icon_Triangle_Down] = "triangleDown",
	[item_Fire_Icon_2_Bars] = "square",
	[item_Fire_Icon_Triangle_Up] = "triangleUp",

	[item_Fortress_Icon_Omega] = "square",
	[item_Fortress_Icon_Rings] = "circle",
	[item_Fortress_Icon_Arrow] = "triangleUp",

	[item_CrystalJataaka] = "triangleUp",
	[item_CrystalSareena] = "triangleUp",
	[item_CrystalKia] = "triangleUp"
}

--[[-----------------------------------------------------

				GENERAL FUNCTIONS
These are mostly helpers for common stuff
--------------------------------------------------------]]

--check if array has value
local function has_value (tab, val)
    for index, value in ipairs(tab) do
        if value == val then
            return true
        end
    end
    return false
end

--string to hex (returns in string)
function string.tohex(str)
    return (str:gsub('.', function (c)
        return string.format('%02X', string.byte(c))
    end))
end

--string from hex (input is string)
function string.fromhex(str)
    return (str:gsub('..', function (cc)
        return string.char(tonumber(cc, 16))
    end))
end

--writes to 8 consecutive addresses
local function write8(address, value)
	for i = 1, 8, 1 do
		char = 0x00
		if i <= #value then
			char = value:sub(i,i)
			char = string.tohex(char)
			char = tonumber(char, 16)
		end
		local mem = address + i - 1
		memory.writebyte(mem, char)
	end
end

--writes to 4 consecutive addresses
local function write4(address, value)
	for i = 1, 4, 1 do
		char = 0x00
		if i <= #value then
			char = value:sub(i,i)
			char = string.tohex(char)
			char = tonumber(char, 16)
		end
		local mem = address + i - 1
		memory.writebyte(mem, char)
	end
end

-- Count how many power upgrades the player currently has
local function countPowerUpgrades()
	local count = 0
	for _, item in ipairs(randoInventory) do
		if item == item_PowerUpgrade then
			count = count + 1
		end
	end
	return count
end

--better wording for text display
local function displayTextAtLocation(text, x, y, color)
	gui.drawText(x,y,text,color, 0, 17, "Courier New","bold")
end

--display text on inventory open
local function displayInventoryText()
	if memory.readbyte(inventoryopenmem) == 1 and inventoryOpenCounter >= 5 then
		if inventoryFrozen then
			displayTextAtLocation("Can't turn pages right now", 35, 10, "goldenrod")
		end
		local powercolor = "gray"
		if reqpowers <= countPowerUpgrades() then
			powercolor = "darkgreen"
		end
		displayTextAtLocation(string.format("POWER REQ: %d",  reqpowers), 63, 0, powercolor)

		displayTextAtLocation(string.format("PAGE: %d / %d", currentPage, inventoryPages), 178, 80, "gray")

		-- Stage-specific check count
		local stage = memory.readbyte(stagemem)
		local checks = 0
		local total = 0
		local checkArray = nil

		-- values for stages

		--0 First mission
		--1 Wind Temple
		--3 Earth Temple
		--2 Water Temple
		--5 Fire Temple
		--4 Prison Escape
		--8 Bridge
		--9 Fortress

		if stage == 0 then
			checkArray = stg1_checks
		elseif stage == 1 then
			checkArray = stg2_checks
		elseif stage == 3 then
			checkArray = stg3_checks
		elseif stage == 2 then
			checkArray = stg4_checks
		elseif stage == 5 then
			checkArray = stg5_checks
		elseif stage == 4 then
			checkArray = stg6_checks
		elseif stage == 8 then
			checkArray = stg7_checks
		elseif stage == 9 then
			checkArray = stg8_checks
		end

		if checkArray then
			total = #checkArray
			for i = 1, total do
				if checkArray[i] == 1 then
					checks = checks + 1
				end
			end
			local color = (checks == total and total > 0) and "darkgreen" or "gray"
			displayTextAtLocation(string.format("LEVEL CHECKS:\n   %d / %d", checks, total), 178, 270, color)
		end
	end
end


-- Bottom message for when an item is picked up
local function displayPickupMessage()
	if pickupTimer > 0 then
		displayTextAtLocation(pickupMessage, 30, 450, "yellow")
		pickupTimer = pickupTimer - 1
		if pickupTimer == 0 then
			pickupMessage = ""
		end
	end
end

-- I don't want pages with only dummy items, c'mon
local function trimExtraDummies()
	local realItems = {}
	for _, item in ipairs(randoInventory) do
		if item ~= item_Dummy and item ~= item_PowerUpgrade then
			table.insert(realItems, item)
		end
	end

	local count = #realItems
	local missing = 10 - (count % 10)
	if missing ~= 10 then
		for i = 1, missing do
			table.insert(realItems, item_Dummy)
		end
	end

	-- Keep PowerUpgrades but at the end (or remove entirely if you prefer)
	for _, item in ipairs(randoInventory) do
		if item == item_PowerUpgrade then
			table.insert(realItems, item)
		end
	end

	randoInventory = realItems
end

-- Sort in ascending order
local function sortRandoInventory()
	table.sort(randoInventory, function(a, b)
		return a < b
	end)
	trimExtraDummies()
end

-- Define key item ownership
local function hasKeyItem(item)
	for _, invItem in ipairs(randoInventory) do
		if invItem == item then return true end
	end
	return false
end

-- Draw a triangle pointing up
local function drawTriangleUp(x, y, size, color)
	local half = math.floor(size / 2)

	local points = {
		{x, y - half},
		{x - half, y + half},
		{x + half, y + half}
	}

	gui.drawPolygon(points, color, color)
end

-- Draw a triangle pointing down
local function drawTriangleDown(x, y, size, color)
	local half = math.floor(size / 2)

	local points = {
		{x, y + half},       -- bottom point
		{x - half, y - half}, -- top left
		{x + half, y - half}  -- top right
	}

	gui.drawPolygon(points, color, color)
end

-- Draw a square
local function drawSquare(x, y, size, color)
	gui.drawRectangle(x - size // 2, y - size // 2, size, size, color, color)
end

-- Draw a circle
local function drawCircle(x, y, size, color)
	gui.drawEllipse(x - size // 2, y - size // 2, size, size, color, color)
end

local function drawKeyItemProgress()
	if memory.readbyte(inventoryopenmem) ~= 1 then return end

	local baseX = 212
	local baseY = 9
	local shapeSize = 12
	local itemSpacing = 16     -- space between shapes
	local stageSpacing = 10    -- extra space between groups of 3

	local stages = {1,3,2,5,4,8,9}
	local currentX = baseX

	for _, stage in ipairs(stages) do
		local keys = keyItemsPerStage[stage] or {}
		local color = keyStageColors[stage] or "white"

		for i = 1, #keys do
			local itemID = keys[i]
			local owned = hasKeyItem(itemID)
			local drawColor = owned and color or "gray"
			local x = currentX
			local y = baseY

			local shape = keyItemShapes[itemID] or "circle"

			if shape == "circle" then
				drawCircle(x, y, shapeSize, drawColor)
			elseif shape == "square" then
				drawSquare(x, y, shapeSize, drawColor)
			elseif shape == "triangleUp" then
				drawTriangleUp(x, y, shapeSize, drawColor)
			elseif shape == "triangleDown" then
				drawTriangleDown(x, y, shapeSize, drawColor)
			else
				gui.drawRectangle(x - shapeSize//2, y - shapeSize//2, shapeSize, shapeSize, drawColor, drawColor) -- fallback
			end
			currentX = currentX + itemSpacing
		end

		-- Add stage separation gap after group of 3
		currentX = currentX + stageSpacing
	end
end



--[[-----------------------------------------------------

				INVENTORY MANAGEMENT
Functions related to managing the inventory
--------------------------------------------------------]]

-- Ensures item is not nil (fallback to item_Empty)
local function getItem(index)
	return randoInventory[index] or item_Empty
end

local function clearWrongKeyItemsFromDisplay()
	local stage = memory.readbyte(stagemem)
	local allowedKeys = keyItemsPerStage[stage] or {}

	for i = 1, 10 do
		local addr = gameInventory[i]
		local item = memory.read_u32_be(addr)

		if has_value(keyItems, item) and not has_value(allowedKeys, item) then
			memory.write_u32_be(addr, item_Glass)
			lastInventoryState[i] = item_Glass
		end
	end
end

-- Writes a full inventory page to memory
local function loadInventoryPage()
	if currentPage > inventoryPages then currentPage = inventoryPages end
	if currentPage < 1 then currentPage = 1 end

	local visibleItems = {}
	for _, item in ipairs(randoInventory) do
		if item ~= item_PowerUpgrade then
			table.insert(visibleItems, item)
		end
	end

	local startIndex = (currentPage - 1) * 10 + 1
	for i = 1, 10 do
		local item = visibleItems[startIndex + i - 1] or item_Dummy
		memory.write_u32_be(gameInventory[i], item)
		if memory.readbyte(inventoryopenmem) == 1 then
			lastInventoryState[i] = item
		end
	end
	clearWrongKeyItemsFromDisplay()
end



-- Calculate how many pages we need
local function manageInventoryPages()
	local realItemCount = 0
	for _, item in ipairs(randoInventory) do
		if item ~= item_PowerUpgrade then
			realItemCount = realItemCount + 1
		end
	end

	inventoryPages = math.ceil(realItemCount / 10)
	if inventoryPages < 1 then inventoryPages = 1 end
	if currentPage > inventoryPages then currentPage = inventoryPages end
	if currentPage < 1 then currentPage = 1 end
end

-- Init randomizer inventory (debug/test mode)
local function invInit()
	if next(randoInventory) == nil and not invInitCheck then
		randoInventory = {
			item_Potion,
			item_Urn_Replenish_Health
		}
		sortRandoInventory()
		manageInventoryPages()
		loadInventoryPage()
		invInitCheck = true
	end
end

-- Next page (Right Input)
local function invNextPage()
	if inventoryFrozen then
		return
	end

	if inventoryPages > 0 then
		local rightPressed = memory.readbyte(inputmem + 2) == 32
		local invOpen = memory.readbyte(inventoryopenmem) == 1
		if invOpen and rightPressed and not menustop then
			if currentPage < inventoryPages then
				currentPage = currentPage + 1
				loadInventoryPage()
			end
			menustop = true
		end
	end
end

-- Previous page (Left Input)
local function invPrevPage()
	if inventoryFrozen then
		return
	end

	if inventoryPages > 0 then
		local leftPressed = memory.readbyte(inputmem + 2) == 128
		local invOpen = memory.readbyte(inventoryopenmem) == 1
		if invOpen and leftPressed and not menustop then
			if currentPage > 1 then
				currentPage = currentPage - 1
				loadInventoryPage()
			end
			menustop = true
		end
	end
end

-- Resets paging cooldown
local function resetMenuStop()
	if memory.readbyte(inputmem + 2) == 0 then
		menustop = false
	end
end

-- Determines if a visual inventory slot shows 'glass' but is hiding a key item
local function isFakeGlassSlot(slotIndex)
	local indexInRando = (currentPage - 1) * 10 + slotIndex
	local actualItem = randoInventory[indexInRando]
	return has_value(keyItems, actualItem)
end

-- Detects if any item has been used (slot set to item_Empty)
local function detectItemUse()
	if skipNextItemUseDetection then
		skipNextItemUseDetection = false
		return
	end

	if memory.readbyte(inventoryopenmem) ~= 1 then return end

	for i = 1, 10 do
		local indexInRando = (currentPage - 1) * 10 + i

		if indexInRando <= #randoInventory then
			local addr = gameInventory[i]
			local prev = lastInventoryState[i]
			local curr = memory.read_u32_be(addr)

			if prev and prev ~= item_Empty and curr == item_Empty then
				if lastRemovedSlotIndex ~= i then
			
					-- Check if this was a visual Glass representing a key item
					if isFakeGlassSlot(i) and prev == item_Glass then
						-- Move the actual key item temporarily out of randoInventory
						local removedItem = table.remove(randoInventory, indexInRando)
						table.insert(heldKeyItems, removedItem)
			
						-- Freeze the inventory like normal
						sortRandoInventory()
						manageInventoryPages()
						inventoryFrozen = true
						forceReloadOnOpen = true
						skipNextItemUseDetection = true
						lastRemovedSlotIndex = i
						break
					end
			
					-- Normal item was used
					table.remove(randoInventory, indexInRando)
					sortRandoInventory()
					manageInventoryPages()
					inventoryFrozen = true
					forceReloadOnOpen = true
					skipNextItemUseDetection = true
					lastRemovedSlotIndex = i
					break
				end
			end

			lastInventoryState[i] = curr
		else
			lastInventoryState[i] = item_Empty
		end
	end
end


-- Clear slot 10 if it becomes filled (prevents blocking pickups)
local function clearLastSlotIfFilled()
	-- Only run this when inventory is NOT open
	if memory.readbyte(inventoryopenmem) == 1 then return end

	local lastSlotValue = memory.read_u32_be(gameInventory[10])
	if lastSlotValue ~= item_Empty then
		memory.write_u32_be(gameInventory[10], item_Empty)
	end
end

local function handleInventoryTransition()
	local inventoryOpenNow = memory.readbyte(inventoryopenmem) == 1

	if inventoryOpenLastFrame and not inventoryOpenNow then
		lastRemovedSlotIndex = nil
	
		-- Clear all slots except first
		for i = 1, 10 do
			if i ~= 1 then
				memory.write_u32_be(gameInventory[i], item_Empty)
				lastInventoryState[i] = item_Empty
			end
		end
	
		-- 🛠️ Restore any temporarily held key items
		for _, item in ipairs(heldKeyItems) do
			table.insert(randoInventory, item)
		end
		heldKeyItems = {} -- Clear the buffer
	
		sortRandoInventory()
		manageInventoryPages()
	
		skipNextItemUseDetection = true
		inventoryFrozen = false
		inventoryOpenCounter = 0
	end

	if not inventoryOpenLastFrame and inventoryOpenNow then
		inventoryOpenCounter = 1
		sortRandoInventory()
	elseif inventoryOpenNow and inventoryOpenCounter > 0 then
		inventoryOpenCounter = inventoryOpenCounter + 1
		if inventoryOpenCounter == 5 then
			loadInventoryPage()
		end
	end

	inventoryOpenLastFrame = inventoryOpenNow
end


-- Add items to inventory / Used by pickup functions
local function addItemToInventory(itemID)
	table.insert(randoInventory, itemID)
	sortRandoInventory()
	manageInventoryPages()
	loadInventoryPage() -- Optional, call only if immediate UI refresh is needed
end

-- Called every frame if inventory is open
local function inventoryFunctions()
	invInit()
	invNextPage()
	invPrevPage()
	resetMenuStop()
	displayInventoryText()
	detectItemUse()
	clearLastSlotIfFilled()
	handleInventoryTransition()
	-- emergency fallback if inventory is open but slots are empty
	if memory.readbyte(inventoryopenmem) == 1 and not inventoryFrozen then
		local isReallyEmpty = true
		for i = 1, 10 do
			if memory.read_u32_be(gameInventory[i]) ~= item_Empty then
				isReallyEmpty = false
				break
			end
		end
		if isReallyEmpty and #randoInventory > 0 then
			loadInventoryPage()
		end
	end
end

--[[-----------------------------------------------------

				LEVEL CHECKS & KEYS 
Functions related to managing already read items from any level, and to know if the player has any 'key items' from that level
--------------------------------------------------------]]

local function checkStage1Pickups()
	if memory.readbyte(stagemem) ~= 0 or memory.read_u32_be(gameplaymem) < 0x10 then return end

	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	-- If A is held, start watching any unclaimed item
	if aHeld then
		for i = 1, #stg1_checks do
			if stg1_checks[i] == 0 and stg1_watchTimers[i] == 0 then
				stg1_watchTimers[i] = 30 -- watch this item for 30 frames
			end
		end
	end

	-- Watch active items
	for i = 1, #stg1_watchTimers do
		if stg1_watchTimers[i] > 0 and stg1_checks[i] == 0 then
			local addr = _G["stg1_item"..i]
			local val = memory.read_u32_be(addr)

			local picked = false
			if i == 5 then
				picked = val == 0x00000100
			else
				picked = val == 0x00000001
			end

			if picked then
				stg1_checks[i] = 1
				stg1_watchTimers[i] = 0
				addItemToInventory(stg1_item_pool[i])
				local itemName = itemNames[stg1_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg1_watchTimers[i] = stg1_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 2 - Wind Temple pickups
local function checkStage2Pickups()
	if memory.readbyte(stagemem) ~= 1 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	if aHeld then
		for i = 1, #stg2_checks do
			if stg2_checks[i] == 0 and stg2_watchTimers[i] == 0 then
				stg2_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg2_watchTimers do
		if stg2_watchTimers[i] > 0 and stg2_checks[i] == 0 then
			local addr = _G["stg2_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg2_checks[i] = 1
				stg2_watchTimers[i] = 0
				addItemToInventory(stg2_item_pool[i])
				local itemName = itemNames[stg2_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg2_watchTimers[i] = stg2_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 3 - Earth Temple pickups
local function checkStage3Pickups()
	if memory.readbyte(stagemem) ~= 3 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	if aHeld then
		for i = 1, #stg3_checks do
			if stg3_checks[i] == 0 and stg3_watchTimers[i] == 0 then
				stg3_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg3_watchTimers do
		if stg3_watchTimers[i] > 0 and stg3_checks[i] == 0 then
			local addr = _G["stg3_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg3_checks[i] = 1
				stg3_watchTimers[i] = 0
				addItemToInventory(stg3_item_pool[i])
				local itemName = itemNames[stg3_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg3_watchTimers[i] = stg3_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 4 - Water Temple pickups
local function checkStage4Pickups()
	if memory.readbyte(stagemem) ~= 2 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	if aHeld then
		for i = 1, #stg4_checks do
			if stg4_checks[i] == 0 and stg4_watchTimers[i] == 0 then
				stg4_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg4_watchTimers do
		if stg4_watchTimers[i] > 0 and stg4_checks[i] == 0 then
			local addr = _G["stg4_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg4_checks[i] = 1
				stg4_watchTimers[i] = 0
				addItemToInventory(stg4_item_pool[i])
				local itemName = itemNames[stg4_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg4_watchTimers[i] = stg4_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 5 - Fire Temple pickups
local function checkStage5Pickups()
	if memory.readbyte(stagemem) ~= 5 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	if aHeld then
		for i = 1, #stg5_checks do
			if stg5_checks[i] == 0 and stg5_watchTimers[i] == 0 then
				stg5_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg5_watchTimers do
		if stg5_watchTimers[i] > 0 and stg5_checks[i] == 0 then
			local addr = _G["stg5_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg5_checks[i] = 1
				stg5_watchTimers[i] = 0
				addItemToInventory(stg5_item_pool[i])
				local itemName = itemNames[stg5_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg5_watchTimers[i] = stg5_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 6 - Prison pickups
local function checkStage6Pickups()
	if memory.readbyte(stagemem) ~= 4 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	if aHeld then
		for i = 1, #stg6_checks do
			if stg6_checks[i] == 0 and stg6_watchTimers[i] == 0 then
				stg6_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg6_watchTimers do
		if stg6_watchTimers[i] > 0 and stg6_checks[i] == 0 then
			local addr = _G["stg6_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg6_checks[i] = 1
				stg6_watchTimers[i] = 0
				addItemToInventory(stg6_item_pool[i])
				local itemName = itemNames[stg6_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg6_watchTimers[i] = stg6_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 7 - Bridge pickups
local function checkStage7Pickups()
	if memory.readbyte(stagemem) ~= 8 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0

	if aHeld then
		for i = 1, #stg7_checks do
			if stg7_checks[i] == 0 and stg7_watchTimers[i] == 0 then
				stg7_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg7_watchTimers do
		if stg7_watchTimers[i] > 0 and stg7_checks[i] == 0 then
			local addr = _G["stg7_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg7_checks[i] = 1
				stg7_watchTimers[i] = 0
				addItemToInventory(stg7_item_pool[i])
				local itemName = itemNames[stg7_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg7_watchTimers[i] = stg7_watchTimers[i] - 1
			end
		end
	end
end

-- Stage 8 - Fortress pickups
local function checkStage8Pickups()
	if memory.readbyte(stagemem) ~= 9 or memory.read_u32_be(gameplaymem) < 0x10 then return end
	
	-- Sets the required XP to fight Quan-Chi (only applies when on Fortress level)
	local reqxp = string.format("0x%X", quanchixp)
	memory.write_u16_be(quanchixpmem, quanchixp)

	local aHeld = (memory.readbyte(inputmem + 3) & 0x04) ~= 0
	if aHeld then
		for i = 1, #stg8_checks do
			if stg8_checks[i] == 0 and stg8_watchTimers[i] == 0 then
				stg8_watchTimers[i] = 30
			end
		end
	end

	for i = 1, #stg8_watchTimers do
		if stg8_watchTimers[i] > 0 and stg8_checks[i] == 0 then
			local addr = _G["stg8_item"..i]
			local val = memory.read_u32_be(addr)
			local picked = val == 0x00000001

			if picked then
				stg8_checks[i] = 1
				stg8_watchTimers[i] = 0
				addItemToInventory(stg8_item_pool[i])
				local itemName = itemNames[stg8_item_pool[i]] or ("Item #" .. i)
				pickupMessage = "Picked up: " .. itemName
				print("[INFO] "..pickupMessage)
				pickupTimer = 120
			else
				stg8_watchTimers[i] = stg8_watchTimers[i] - 1
			end
		end
	end
end

local function overrideXP()
	local count = countPowerUpgrades()
	local desiredXP = powerUpgradeXPLevels[math.min(count, 9)] or 0x0000
	memory.write_u16_be(currentexpmem, desiredXP)
end

--[[-----------------------------------------------------

					RANDOMIZER 
The functions to actually randomize what every item is in each level
--------------------------------------------------------]]

function shuffleArray(t)
	for i = #t, 2, -1 do
		local j = math.random(1, i)
		t[i], t[j] = t[j], t[i]
	end
end

-- This is to know which locations need which items in order to get access (First Mission stage).
function buildStage1LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv) return true end
	}

	local locations = {}
	for index = 1, #stg1_item_pool do
		table.insert(locations, {
			stage = 0,
			index = index,
			pool = stg1_item_pool,
			addr = _G["stg1_item" .. index],
			access = accessRules[index],
			name = "FM " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Wind stage).
function buildStage2LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv)	return has_value(inv, item_Wind_Icon_Circle) end,
		[6] = function(inv) return has_value(inv, item_Wind_Icon_Triangle) end
	}

	local locations = {}
	for index = 1, #stg2_item_pool do
		table.insert(locations, {
			stage = 1,
			index = index,
			pool = stg2_item_pool,
			addr = _G["stg2_item" .. index],
			access = accessRules[index],
			name = "Wind " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Earth stage).
function buildStage3LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv) return true end,
		[6] = function(inv) return has_value(inv, item_Earth_Icon_Square) end,
		[7] = function(inv) return has_value(inv, item_Earth_Icon_Square) end,
		[8] = function(inv) return has_value(inv, item_Earth_Icon_Square) end,
		[9] = function(inv) return has_value(inv, item_Earth_Icon_Square) end,
		[10] = function(inv) return has_value(inv, item_Earth_Icon_Square) end,
		[11] = function(inv) return has_value(inv, item_Earth_Icon_Square) end,
		[12] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[13] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[14] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[15] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[16] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[17] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[18] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[19] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end,
		[20] = function(inv) return has_value(inv, item_Earth_Icon_4_Square) end
	}

	local locations = {}
	for index = 1, #stg3_item_pool do
		table.insert(locations, {
			stage = 3,
			index = index,
			pool = stg3_item_pool,
			addr = _G["stg3_item" .. index],
			access = accessRules[index],
			name = "Earth " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Water stage).
function buildStage4LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv)	return true end,
		[6] = function(inv) return has_value(inv, item_Water_Icon_Triangle) end,
		[7] = function(inv)	return true end,
		[8] = function(inv)	return has_value(inv, item_Water_Icon_3_Bars) end,
		[9] = function(inv)	return has_value(inv, item_Water_Icon_Moon) end
	}

	local locations = {}
	for index = 1, #stg4_item_pool do
		table.insert(locations, {
			stage = 2,
			index = index,
			pool = stg4_item_pool,
			addr = _G["stg4_item" .. index],
			access = accessRules[index],
			name = "Water " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Fire stage).
function buildStage5LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv) return true end,
		[6] = function(inv) return true end,
		[7] = function(inv) return true end,
		[8] = function(inv) return true end,
		[9] = function(inv) return true end,
		[10] = function(inv) return true end,
		[11] = function(inv) return true end,
		[12] = function(inv) return true end,
		[13] = function(inv) return true end,
		[14] = function(inv) return true end,
		[15] = function(inv) return true end,
		[16] = function(inv) return true end
	}

	local locations = {}
	for index = 1, #stg5_item_pool do
		table.insert(locations, {
			stage = 5,
			index = index,
			pool = stg5_item_pool,
			addr = _G["stg5_item" .. index],
			access = accessRules[index],
			name = "Fire " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Prison stage).
function buildStage6LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv) return true end,
		[6] = function(inv) return has_value(inv, item_Prison_L1_Key) end,
		[7] = function(inv) return has_value(inv, item_Prison_L1_Key) end,
		[8] = function(inv) return has_value(inv, item_Prison_L1_Key) and has_value(inv, item_Prison_L2_Key) end,
		[9] = function(inv) return has_value(inv, item_Prison_L1_Key) and has_value(inv, item_Prison_L2_Key) and has_value(inv, item_Prison_L3_Key) end,
		[10] = function(inv) return has_value(inv, item_Prison_L1_Key) and has_value(inv, item_Prison_L2_Key) end
	}

	local locations = {}
	for index = 1, #stg6_item_pool do
		table.insert(locations, {
			stage = 4,
			index = index,
			pool = stg6_item_pool,
			addr = _G["stg6_item" .. index],
			access = accessRules[index],
			name = "Prison " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Bridge stage).
function buildStage7LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv) return true end,
		[6] = function(inv) return true end,
		[7] = function(inv) return true end,
		[8] = function(inv) return true end,
		[9] = function(inv) return true end,
		[10] = function(inv) return true end,
		[11] = function(inv) return true end,
		[12] = function(inv) return true end,
		[13] = function(inv) return true end,
		[14] = function(inv) return has_value(inv, item_Fortress_Icon_Arrow) and has_value(inv, item_Fortress_Icon_Rings) and has_value(inv, item_Fortress_Icon_Omega) end,
		[15] = function(inv) return has_value(inv, item_Fortress_Icon_Arrow) and has_value(inv, item_Fortress_Icon_Rings) and has_value(inv, item_Fortress_Icon_Omega) end,
		[16] = function(inv) return has_value(inv, item_Fortress_Icon_Arrow) and has_value(inv, item_Fortress_Icon_Rings) and has_value(inv, item_Fortress_Icon_Omega) end
	}

	local locations = {}
	for index = 1, #stg7_item_pool do
		table.insert(locations, {
			stage = 8,
			index = index,
			pool = stg7_item_pool,
			addr = _G["stg7_item" .. index],
			access = accessRules[index],
			name = "Bridge " .. index
		})
	end

	return locations
end

-- This is to know which locations need which items in order to get access (Fortress stage).
function buildStage8LocationEntries()
	local accessRules = {
		[1] = function(inv) return true end,
		[2] = function(inv) return true end,
		[3] = function(inv) return true end,
		[4] = function(inv) return true end,
		[5] = function(inv) return true end,
		[6] = function(inv) return true end,
		[7] = function(inv) return true end,
		[8] = function(inv) return true end,
		[9] = function(inv) return true end
	}

	local locations = {}
	for index = 1, #stg8_item_pool do
		table.insert(locations, {
			stage = 9,
			index = index,
			pool = stg8_item_pool,
			addr = _G["stg8_item" .. index],
			access = accessRules[index],
			name = "Fortress " .. index
		})
	end

	return locations
end

-- Returns array of location requirements for whole game
function buildAllLocations()
	local all = {}
	for _, fn in ipairs({
		buildStage1LocationEntries,
		buildStage2LocationEntries,
		buildStage3LocationEntries,
		buildStage4LocationEntries,
		buildStage5LocationEntries,
		buildStage6LocationEntries,
		buildStage7LocationEntries,
		buildStage8LocationEntries
	}) do
		for _, loc in ipairs(fn()) do
			table.insert(all, loc)
		end
	end
	return all
end

-- Determines if inventory is in a beatable state
local function isBeatable(inventory)
	local powerCount = 0
	local hasKia, hasJataaka, hasSareena = false, false, false

	for _, item in ipairs(inventory) do
		if item == item_PowerUpgrade then
			powerCount = powerCount + 1
		elseif item == item_CrystalKia then
			hasKia = true
		elseif item == item_CrystalJataaka then
			hasJataaka = true
		elseif item == item_CrystalSareena then
			hasSareena = true
		end
	end

	return powerCount >= reqpowers and hasKia and hasJataaka and hasSareena
end

-- Sets required XP to fight Quan-Chi and power quantity accordingly
local function setQuanChiXPReq()
	quanchixp = math.random(0,6000)

	if quanchixp > 5911 then
		reqpowers = 9
	elseif quanchixp > 4503 then
		reqpowers = 8
	elseif quanchixp > 3315 then
		reqpowers = 7
	elseif quanchixp > 2323 then
		reqpowers = 6
	elseif quanchixp > 1410 then
		reqpowers = 5
	elseif quanchixp > 834 then
		reqpowers = 4
	elseif quanchixp > 258 then
		reqpowers = 3
	elseif quanchixp > 85 then
		reqpowers = 2
	else
		reqpowers = 1
	end
end

function shuffleAllStageItemPools()
	local stageBuilders = {
		buildStage1LocationEntries,
		buildStage2LocationEntries,
		buildStage3LocationEntries,
		buildStage4LocationEntries,
		buildStage5LocationEntries,
		buildStage6LocationEntries,
		buildStage7LocationEntries,
		buildStage8LocationEntries
	}



	local allLocations = {}
	for _, builder in ipairs(stageBuilders) do
		local locs = builder()
		for _, loc in ipairs(locs) do
			table.insert(allLocations, loc)
		end
	end

	local maxAttempts = 100
	local attempt = 0
	local valid = false

	while not valid and attempt < maxAttempts do
		attempt = attempt + 1

		-- Step 1: Collect all items
		local allItems = {}
		for _, loc in ipairs(allLocations) do
			table.insert(allItems, loc.pool[loc.index])
		end

		-- Step 2: Replace 9 herbs with PowerUpgrades
		setQuanChiXPReq() -- Sets the req XP to fight Quan-Chi
		print("[INFO] Setting powers required to: ".. reqpowers)
		local herbReplacementCount = 9
		local replaced = 0
		for i = 1, #allItems do
			if allItems[i] == item_Herbs and replaced < herbReplacementCount then
				allItems[i] = item_PowerUpgrade
				replaced = replaced + 1
			end
		end

		-- Step 3: Shuffle items
		shuffleArray(allItems)

		-- Step 4: Assign back to locations
		for i, loc in ipairs(allLocations) do
			loc.pool[loc.index] = allItems[i]
			loc.obtained = false
		end

		-- Step 5: Simulate progression
		local simulatedInventory = {}
		local changed = true

		while changed do
			changed = false
			for _, loc in ipairs(allLocations) do
				if not loc.obtained and loc.access(simulatedInventory) then
					table.insert(simulatedInventory, loc.pool[loc.index])
					loc.obtained = true
					changed = true
				end
			end
		end

		-- Step 6: Check win condition
		if isBeatable(simulatedInventory) then
			valid = true
			print("[INFO] Valid distribution found in " .. attempt .. " tries")
			break
		end
	end

	if not valid then
		print("[WARN] No valid item layout found after " .. maxAttempts .. " attempts")
	end
end

local function clearRandoState()
	-- Clear state and apply new seed
	randoInventory = {}
	-- Clear all item pickup flags and timers
	for i = 1, #stg1_checks do stg1_checks[i] = 0; stg1_watchTimers[i] = 0 end
	for i = 1, #stg2_checks do stg2_checks[i] = 0; stg2_watchTimers[i] = 0 end
	for i = 1, #stg3_checks do stg3_checks[i] = 0; stg3_watchTimers[i] = 0 end
	for i = 1, #stg4_checks do stg4_checks[i] = 0; stg4_watchTimers[i] = 0 end
	for i = 1, #stg5_checks do stg5_checks[i] = 0; stg5_watchTimers[i] = 0 end
	for i = 1, #stg6_checks do stg6_checks[i] = 0; stg6_watchTimers[i] = 0 end
	for i = 1, #stg7_checks do stg7_checks[i] = 0; stg7_watchTimers[i] = 0 end
	for i = 1, #stg8_checks do stg8_checks[i] = 0; stg8_watchTimers[i] = 0 end

	-- Reset all stage item pools
	stg1_item_pool = {item_Herbs, item_Herbs, item_Herbs, item_Herbs, item_Map}
	stg2_item_pool = {item_Herbs, item_Herbs, item_Urn_Extra_Life, item_Wind_Icon_Circle, item_Wind_Icon_Triangle, item_Wind_Icon_3_Bars}
	stg3_item_pool = {item_Formula, item_Urn_Extra_Life, item_Herbs, item_Earth_Icon_Square, item_Urn_Extra_Life, item_Herbs, item_Urn_Extra_Life, item_Herbs, item_Herbs, item_Herbs, item_Earth_Icon_4_Square, item_Herbs, item_Earth_Icon_Triangle, item_Urn_Extra_Life, item_Eye, item_Shield, item_Herbs, item_Herbs, item_Herbs, item_Urn_Extra_Life}
	stg4_item_pool = {item_Herbs, item_Herbs, item_Water_Icon_Triangle, item_Urn_Extra_Life, item_Potion, item_Water_Icon_3_Bars, item_Urn_Replenish_Health, item_Water_Icon_Moon, item_Urn_Replenish_Health}
	stg5_item_pool = {item_Urn_Replenish_Health, item_Formula, item_Urn_Replenish_Health, item_Herbs, item_Fire_Icon_Triangle_Up, item_Urn_Replenish_Health, item_Shield, item_Herbs, item_Urn_Extra_Life, item_Fire_Icon_2_Bars, item_Urn_Extra_Life, item_Eye, item_Potion, item_Herbs, item_Fire_Icon_Triangle_Down, item_Herbs}
	stg6_item_pool = {item_Herbs, item_Herbs, item_Herbs, item_Herbs, item_Prison_L1_Key, item_Herbs, item_Prison_L2_Key, item_Prison_L3_Key, item_Herbs, item_Urn_Super_Strength}
	stg7_item_pool = {item_Fortress_Icon_Omega, item_Potion, item_Herbs, item_Fortress_Icon_Rings, item_Urn_Extra_Life, item_Urn_Replenish_Health, item_Fortress_Icon_Arrow, item_Urn_Replenish_Health, item_Urn_Replenish_Health, item_Urn_Replenish_Health}
	stg8_item_pool = {item_Herbs, item_Herbs, item_Herbs, item_CrystalSareena, item_Herbs, item_CrystalJataaka, item_Herbs, item_CrystalKia, item_Herbs}

	-- Get init items again
	invInitCheck = false
end

-- Reads password if it changed, and Start was pressed
function checkPasswordSeedInput()
	-- Only if currently not on gameplay
	if memory.read_u32_be(gameplaymem) < 0x10 then
		local current = {}
		local changed = false
	
		-- Read 6 password characters from memory
		for i = 1, 6 do
			local addr = _G["pass" .. i .. "mem"]
			local val = memory.readbyte(addr)
			current[i] = val
			if val ~= lastPassRead[i] then
				changed = true
			end
		end
	
		-- Only proceed if changed AND Start is pressed
		local startPressed = (memory.readbyte(inputmem + 2) & 0x08) ~= 0  -- Start = 0x10
		if changed and startPressed then
			local newSeed = 0
			for i = 1, 6 do
				local ascii = current[i]
				local digit = charToDigit[ascii]
				if digit == nil then
					print("[ERROR] Invalid character in password: " .. tostring(ascii))
					return
				end
				newSeed = newSeed * 21 + digit
			end
	
			-- Update global seed
			seed = newSeed
			seedLabel = ""
			for i = 1, 6 do
				seedPass[i] = current[i]
				seedLabel = seedLabel .. string.char(current[i])
			end
			-- Clear anything done in current run
			clearRandoState()
			-- Reset RNG cleanly
			print("[INFO] New seed applied: " .. seedLabel)
			print("[INFO] Shuffling items...")
			math.randomseed(seed)
			for _ = 1, 3 do math.random() end  -- Lua RNG is known to need a few warm-up calls for full consistency
			shuffleAllStageItemPools()
			-- Re-run logic
			print("[INFO] Randomizer started!")
			print("[INFO] Current seed: " .. seedLabel)
			pickupMessage = "New seed entered: " .. seedLabel
			pickupTimer = 120
			-- Remember this state
			for i = 1, 6 do
				lastPassRead[i] = current[i]
			end
		end
	end
end

--[[-----------------------------------------------------

					INIT & GAME LOOP 
Main 'while true' of the script. The 'init' block is just a function that will be executed in the first second of the script being loaded, and won't be executed again, as it isn't needed.
--------------------------------------------------------]]

-- Converts a number into a table of 6 ASCII codes using only consonants (excludes A, E, I, O, U)
function numberToBase21Ascii(n)
    local consonants = {}
    local excluded = { [65]=true, [69]=true, [73]=true, [79]=true, [85]=true } -- A, E, I, O, U
    for c = 65, 90 do
        if not excluded[c] then
            table.insert(consonants, c)
        end
    end

    local result = {}
    local base = #consonants  -- 21
    for i = 1, 6 do
        local remainder = n % base
        table.insert(result, 1, consonants[remainder + 1]) -- prepend
        n = math.floor(n / base)
    end
    return result
end

-- This sets the seed, saves it to a local array, and also displays it in password screen
local function seedGenAndDisplay()
	-- Use system clock as random feed
	math.randomseed(os.time())
	local base = 21
	seed = 0
	for i = 1, 6 do
	    seed = seed * base + math.random(0, base - 1)
	end
	math.randomseed(seed)
	for _ = 1, 3 do math.random() end -- warm up calls

	local asciiList = numberToBase21Ascii(seed)
	for i, code in ipairs(asciiList) do
	    seedPass[i] = code
	    seedLabel = seedLabel .. string.char(code)
	end
	-- Write seed on password screen
	memory.writebyte(pass1mem, seedPass[1])
	memory.writebyte(pass2mem, seedPass[2])
	memory.writebyte(pass3mem, seedPass[3])
	memory.writebyte(pass4mem, seedPass[4])
	memory.writebyte(pass5mem, seedPass[5])
	memory.writebyte(pass6mem, seedPass[6])
end

-- Initializes the whole randomizer and sets all needed flags
local function initialization()

	while frame < 61 do

		-- After 1 sec do following only once
		if frame ==60 then
			print("------------------------")
			print("--  MKMSZ Randomizer  --")
			print("------------------------")
			print("[INFO] Booting up...")
			seedGenAndDisplay()
			-- Set lastPassRead to match the generated seed (prevents false positive)
			for i = 1, 6 do
				lastPassRead[i] = seedPass[i]
			end
			print("[INFO] Rewriting few item names...")
			write8(tabmem, "-------")
			write8(glassmem, "KEYITEM")
			write4(passtitle1mem, "SEED")
			memory.write_u32_be(passtitle2mem, 0x00000000)
			print("[INFO] Setting Difficulty to Very Hard...")
			memory.writebyte(cfg_difficultymem, 0x04)
			print("[INFO] Setting Lives to 6...")
			memory.writebyte(cfg_livesmem, 0x06)
			print("[INFO] Setting Continues to 4...")
			memory.writebyte(cfg_continuesmem, 0x04)
			print("[INFO] Enabling level select menu...")
			print("[WARN] Level select menu can crash the game!")
			memory.writebyte(stageselectmem, 0x34)
			memory.writebyte(stageselectmem+1, 0x2E)
			print("[INFO] Setting max XP per level...")
			memory.write_u16_be(maxexpmem_stg1, maxpossiblexp)
			memory.write_u16_be(maxexpmem_stg2, maxpossiblexp)
			memory.write_u16_be(maxexpmem_stg3, maxpossiblexp)
			memory.write_u16_be(maxexpmem_stg4, maxpossiblexp)
			print("[INFO] Making cheese...")
			memory.write_u16_be(maxexpmem_stg5, maxpossiblexp)
			memory.write_u16_be(maxexpmem_stg6, maxpossiblexp)
			memory.write_u16_be(maxexpmem_stg7, maxpossiblexp)
			memory.write_u16_be(maxexpmem_stg8, maxpossiblexp)
			print("[INFO] Shuffling items...")
			shuffleAllStageItemPools()
			print("[INFO] Randomizer started!")
			print("[INFO] Current seed: " .. seedLabel)

		end
    	frame = frame + 1
		emu.frameadvance()
	end
end

-- Run configs and flags
initialization()

-- MAIN LOOP
while true do
	gui.clearGraphics()		
	inventoryFunctions()
	checkPasswordSeedInput()
	displayPickupMessage()
	checkStage1Pickups()
	checkStage2Pickups()
	checkStage3Pickups()
	checkStage4Pickups()
	checkStage5Pickups()
	checkStage6Pickups()
	checkStage7Pickups()
	checkStage8Pickups()
	overrideXP()
	drawKeyItemProgress()
	emu.frameadvance()
end