const runtimeStatus = document.querySelector("#runtimeStatus");
const romFile = document.querySelector("#romFile");
const mktN64File = document.querySelector("#mktN64File");
const romValidation = document.querySelector("#romValidation");
const mktValidation = document.querySelector("#mktValidation");
const romDropZone = document.querySelector("#romDropZone");
const mktDropZone = document.querySelector("#mktDropZone");
const romFileName = document.querySelector("#romFileName");
const mktFileName = document.querySelector("#mktFileName");
const donorExtrasStatus = document.querySelector("#donorExtrasStatus");
const outfitMode = document.querySelector("#outfitMode");
const editionName = document.querySelector("#editionName");
const seed = document.querySelector("#seed");
const seedField = document.querySelector("#seedField");
const randomSeedButton = document.querySelector("#randomSeedButton");
const copySeedButton = document.querySelector("#copySeedButton");
const colorField = document.querySelector("#colorField");
const customColor = document.querySelector("#customColor");
const colorValue = document.querySelector("#colorValue");
const turnLock = document.querySelector("#turnLock");
const attackModern = document.querySelector("#attackModern");
const specialsModern = document.querySelector("#specialsModern");
const jumpButton = document.querySelector("#jumpButton");
const runAuto = document.querySelector("#runAuto");
const shufflePowerProgression = document.querySelector("#shufflePowerProgression");
const enemyRandomization = document.querySelector("#enemyRandomization");
const powersAsPickups = document.querySelector("#powersAsPickups");
const requiredPowersMode = document.querySelector("#requiredPowersMode");
const globalCompletionMode = document.querySelector("#globalCompletionMode");
const customRequiredPowersField = document.querySelector("#customRequiredPowersField");
const customRequiredPowers = document.querySelector("#customRequiredPowers");
const difficulty = document.querySelector("#difficulty");
const startingLives = document.querySelector("#startingLives");
const startingContinues = document.querySelector("#startingContinues");
const persistHp = document.querySelector("#persistHp");
const debugAllKeys = document.querySelector("#debugAllKeys");
const disableAudioFix = document.querySelector("#disableAudioFix");
const debugOptionsSummary = document.querySelector("#debugOptionsSummary");
const randomizerFeaturesSummary = document.querySelector("#randomizerFeaturesSummary");
const runSettingsSummary = document.querySelector("#runSettingsSummary");
const gameSettingsSummary = document.querySelector("#gameSettingsSummary");
const buildSummarySeed = document.querySelector("#buildSummarySeed");
const buildSummaryText = document.querySelector("#buildSummaryText");
const buildSummaryRun = document.querySelector("#buildSummaryRun");
const patchButton = document.querySelector("#patchButton");
const buildProgress = document.querySelector("#buildProgress");
const buildMessage = document.querySelector("#buildMessage");
const resultPanel = document.querySelector("#result");
const resultSeed = document.querySelector("#resultSeed");
const resultRequiredPowers = document.querySelector("#resultRequiredPowers");
const outputSha = document.querySelector("#outputSha");
const outputCrc = document.querySelector("#outputCrc");
const downloadButton = document.querySelector("#downloadButton");
const copyResultSeedButton = document.querySelector("#copyResultSeedButton");
const changeSettingsButton = document.querySelector("#changeSettingsButton");
const log = document.querySelector("#log");
const fighterName = document.querySelector("#fighterName");
const fighterHint = document.querySelector("#fighterHint");
const swapFighterButton = document.querySelector("#swapFighterButton");
const outfitLabel = document.querySelector("#outfitLabel");
const fighterDialog = document.querySelector("#fighterDialog");
const fighterCanvas = document.querySelector("#fighterCanvas");
const fighterStageStatus = document.querySelector("#fighterStageStatus");
const fighterHover = document.querySelector("#fighterHover");

const FIGHTER_LABELS = { "sub-zero": "Sub-Zero", sektor: "Sektor" };
const FIGHTER_HINT_DEFAULT =
  "Validate the MKT donor ROM to import a fighter from Mortal Kombat Trilogy.";

const SILLY_MESSAGES = [
  "Cooling down...",
  "Shaving monks' heads...",
  "Randomizing random randomness...",
  "Doing pushups...",
  "Promoting Lin Kuei to Grandmaster...",
  "Assembling bits...",
  "Activating Temple traps...",
  "Worshiping Raiden...",
  "Making Richard Divizio look fabulous...",
  "Pulling the Master Sword...",
  "Playing the Ocarina...",
  "Chasing MIPS...",
  "Claiming the high ground...",
  "Making the Force be with us...",
  "Doing, doing not, and not trying...",
  "Hello there!",
  "Eating cheese...",
  "Shuffling the deck of cards...",
  "Escaping the cyborgs...",
  "Placing random encounters...",
  "Deactivating DLSS and raytracing...",
  "Turning off Lumen...",
  "Unloading the framebuffer...",
  "Making sure ice is cold...",
  "Getting over here...",
  "Dressing up Lia...",
  "Learning Kung-Fu...",
  "Consulting the Elder Gods...",
  "Polishing the Dragon Medallion...",
  "Convincing Fujin to stop blowing things around...",
  "Checking Quan Chi's pockets...",
  "Recounting skulls...",
  "Freezing the loading screen...",
  "Unfreezing the loading screen...",
  "Hiding secret fights...",
  "Counting polygons...",
  "Asking Scorpion to chill...",
  "Looking for Noob...",
  "Feeding the portal...",
  "Rewinding the cartridge...",
  "Testing our might...",
  "Consulting the Lin Kuei handbook...",
  "Defrosting Sub-Zero...",
  "Refreezing Sub-Zero...",
  "Looking for the missing Temple Map...",
  "Pretending Quan Chi can be trusted...",
  "Asking Shinnok nicely...",
  "Avoiding suspiciously placed spikes...",
  "Counting monks...",
  "Misplacing the Fortress keys...",
  "Finding the Fortress keys again...",
  "Teaching Scorpion basic geography...",
  "Repainting the ninjas...",
  "Checking if Smoke is actually smoke...",
  "Installing more ice...",
  "Removing unnecessary fire...",
  "Giving Fujin a fan...",
  "Repairing the Earth Temple...",
  "Draining the Water Temple...",
  "Turning the Wind Temple down a notch...",
  "Asking the Fire Temple to calm down...",
  "Putting the Mythologies back in order...",
  "Rolling for initiative...",
  "Blaming RNG...",
  "Praising RNG...",
  "Sacrificing a controller to RNG...",
  "Rolling a natural 1...",
  "Rolling a natural 20...",
  "Searching behind the waterfall...",
  "Checking every suspicious wall...",
  "Blowing into the cartridge...",
  "Expanding the pak...",
  "Polishing the polygons...",
  "Feeding the RSP...",
  "Asking the RDP what it did...",
  "Finding one more code cave...",
  "Pretending undefined behavior is a feature...",
  "Making the checksum feel important...",
  "Putting the bits back where we found them...",
  "Wondering why this actually works..."
];

let patchWorker = null;
let runtimeReady = false;
let isBuilding = false;
let outputBytes = null;
let outputName = "MKMSZR-patched.z64";
let activeBuild = null;
let sillyTimer = null;
let sillyDeck = [];
let lastSillyMessage = null;

const targetValidation = { token: 0, state: "idle" };
const donorValidation = { token: 0, state: "idle" };
// Fighter swap: the select screen is decoded from the donor in the worker once per donor.
let selectedFighter = "sub-zero";
const selectScreen = { token: 0, state: "idle", data: null, image: null, hover: -1 };

function setLog(message, error = false) {
  log.textContent = message;
  log.style.color = error ? "#ffaaaa" : "";
}

function setFileValidation(element, state, message) {
  element.dataset.state = state;
  element.textContent = message;
}

function updateModeUi() {
  colorField.hidden = outfitMode.value !== "rgb";
  seedField.style.opacity = "1";
  updateSummaries();
}

function donorIsUsable() {
  return donorValidation.state === "idle" || donorValidation.state === "valid";
}

function updatePatchButton() {
  updateFighterUi();
  patchButton.disabled = !runtimeReady ||
    isBuilding ||
    targetValidation.state !== "valid" ||
    !donorIsUsable();
}

function updateGameSettingsUi() {
  const imported = selectedFighter !== "sub-zero";
  if (imported) specialsModern.checked = false;
  specialsModern.disabled = imported;
  const jumpAvailable = attackModern.checked && specialsModern.checked;
  if (!jumpAvailable) jumpButton.checked = false;
  jumpButton.disabled = !jumpAvailable;
  updateSummaries();
}

function updateRequiredPowersUi() {
  const isCustom = requiredPowersMode.value === "custom";
  customRequiredPowersField.hidden = !isCustom;
  customRequiredPowers.disabled = !isCustom;
  updateSummaries();
}

function normalizeEditionName(value) {
  return value.toUpperCase().replace(/[^A-Z0-9 -]/g, "").slice(0, 12);
}

function generateSeed() {
  const words = new Uint32Array(2);
  crypto.getRandomValues(words);
  return Array.from(words, (value) => value.toString(16).padStart(8, "0"))
    .join("")
    .toUpperCase();
}

function selectedText(select) {
  return select.options[select.selectedIndex]?.textContent ?? select.value;
}

function formatMode(value) {
  if (value === "seeded") return "Seeded";
  if (value === "rgb") return "Custom";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function fortressSummary() {
  if (requiredPowersMode.value === "custom") {
    return "Custom " + customRequiredPowers.value;
  }
  return selectedText(requiredPowersMode);
}

function updateSummaries() {
  debugOptionsSummary.textContent = [
    debugAllKeys.checked ? "All stage keys" : "",
    disableAudioFix.checked ? "Audio fix off" : ""
  ].filter(Boolean).join(" · ") || "Off";
  randomizerFeaturesSummary.textContent = [
    "Powers: " + (powersAsPickups.checked ? "pickups" : "XP"),
    shufflePowerProgression.checked ? "shuffled" : "vanilla order",
    "Enemies: " + (enemyRandomization.checked ? "random" : "vanilla"),
    "Fortress: " + fortressSummary()
  ].join(" · ");

  runSettingsSummary.textContent = [
    selectedText(difficulty),
    startingLives.value + " Lives",
    startingContinues.value + " Continues",
    persistHp.checked ? "Persistent HP" : "Full HP on re-entry"
  ].join(" · ");

  gameSettingsSummary.textContent = [
    "TURN: " + (turnLock.checked ? "LOCK" : "TOGGLE"),
    "ATTACK: " + (attackModern.checked ? "MODERN" : "CLASSIC"),
    "SPECIALS: " + (specialsModern.checked ? "MODERN" : "CLASSIC"),
    "JUMP: " + (jumpButton.checked ? "BUTTON" : "DPAD"),
    "RUN: " + (runAuto.checked ? "AUTO" : "HOLD")
  ].join(" · ");

  const seedValue = seed.value.trim();
  buildSummarySeed.textContent = seedValue
    ? "Seed: " + seedValue
    : "Seed: random on patch";
  buildSummaryText.textContent = [
    "Fighter: " + FIGHTER_LABELS[selectedFighter],
    "Outfit: " + formatMode(outfitMode.value),
    "Powers: " + (powersAsPickups.checked ? "pickups" : "XP") +
      (shufflePowerProgression.checked ? " + shuffled" : ""),
    "Enemies: " + (enemyRandomization.checked ? "random" : "vanilla"),
    "Fortress: " + fortressSummary(),
    "Completion: " + selectedText(globalCompletionMode),
    debugAllKeys.checked ? "DEBUG: all stage keys" : "",
    disableAudioFix.checked ? "DEBUG: audio fix off" : ""
  ].filter(Boolean).join(" · ");

  buildSummaryRun.textContent = [
    "Run: " + selectedText(difficulty) + " / " + startingLives.value +
      " lives / " + startingContinues.value + " continues / " +
      (persistHp.checked ? "persistent HP" : "full HP re-entry"),
    gameSettingsSummary.textContent
  ].join(" · ");
}

async function copyText(value, button) {
  if (!value) return;
  try {
    await navigator.clipboard.writeText(value);
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = original; }, 1200);
  } catch (error) {
    setLog("Could not copy to clipboard: " + (error.message ?? error), true);
  }
}

function assignDroppedFile(input, file) {
  const transfer = new DataTransfer();
  transfer.items.add(file);
  input.files = transfer.files;
  input.dispatchEvent(new Event("change", { bubbles: true }));
}

function wireDropZone(zone, input) {
  zone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      input.click();
    }
  });
  for (const eventName of ["dragenter", "dragover"]) {
    zone.addEventListener(eventName, (event) => {
      event.preventDefault();
      zone.classList.add("dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    zone.addEventListener(eventName, (event) => {
      event.preventDefault();
      zone.classList.remove("dragging");
    });
  }
  zone.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (file) assignDroppedFile(input, file);
  });
}

function outputFilename(inputName, mode, seedValue) {
  const stem = inputName.replace(/\.(?:z64|v64|n64)$/i, "");
  let suffix = mode === "vanilla" ? "mkmszr" : "mkmszr-" + mode;
  const safeSeed = seedValue.replace(/[^a-z0-9_-]/gi, "").slice(0, 24);
  if (safeSeed) suffix += "-" + safeSeed;
  return stem + "-" + suffix + ".z64";
}

function shuffleMessages(messages) {
  const shuffled = [...messages];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
  }
  return shuffled;
}

function refillSillyDeck() {
  sillyDeck = shuffleMessages(SILLY_MESSAGES);
  if (lastSillyMessage && sillyDeck.length > 1 &&
      sillyDeck[0] === lastSillyMessage) {
    [sillyDeck[0], sillyDeck[1]] = [sillyDeck[1], sillyDeck[0]];
  }
}

function nextSillyMessage() {
  if (!sillyDeck.length) refillSillyDeck();
  lastSillyMessage = sillyDeck.shift();
  return lastSillyMessage;
}

function startSillyProgress() {
  sillyDeck = [];
  lastSillyMessage = null;
  buildProgress.hidden = false;
  buildMessage.textContent = nextSillyMessage();

  clearInterval(sillyTimer);
  sillyTimer = setInterval(() => {
    buildMessage.textContent = nextSillyMessage();
  }, 3600);
}

function stopSillyProgress() {
  clearInterval(sillyTimer);
  sillyTimer = null;
  sillyDeck = [];
  lastSillyMessage = null;
  buildProgress.hidden = true;
}

function friendlyValidationError(raw) {
  const lines = String(raw || "Validation failed.")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const last = lines.at(-1) || "Validation failed.";
  return last.replace(/^[A-Za-z_][A-Za-z0-9_.]*:\s*/, "");
}

async function validateTargetSelection() {
  const token = ++targetValidation.token;
  const file = romFile.files?.[0];

  if (!file) {
    targetValidation.state = "idle";
    romFileName.textContent = "Drop MKMSZ ROM here";
    romDropZone.dataset.state = "idle";
    setFileValidation(romValidation, "idle", "No target ROM selected.");
    patchWorker?.postMessage({ type: "clear-target" });
    updatePatchButton();
    return;
  }

  targetValidation.state = "validating";
  romFileName.textContent = file.name;
  romDropZone.dataset.state = "validating";
  setFileValidation(romValidation, "validating", "Checking target ROM...");
  updatePatchButton();

  try {
    const bytes = await file.arrayBuffer();
    if (token !== targetValidation.token) return;
    patchWorker.postMessage(
      { type: "validate-target", token, bytes },
      [bytes]
    );
  } catch (error) {
    if (token !== targetValidation.token) return;
    targetValidation.state = "invalid";
    romDropZone.dataset.state = "invalid";
    setFileValidation(
      romValidation,
      "invalid",
      "Could not read target ROM: " + (error.message ?? error)
    );
    updatePatchButton();
  }
}

async function validateDonorSelection() {
  const token = ++donorValidation.token;
  const file = mktN64File.files?.[0];

  if (!file) {
    donorValidation.state = "idle";
    mktFileName.textContent = "Drop MKT donor here";
    mktDropZone.dataset.state = "idle";
    donorExtrasStatus.textContent = "Donor extras disabled";
    donorExtrasStatus.dataset.state = "idle";
    setFileValidation(mktValidation, "idle", "Optional donor not selected.");
    patchWorker?.postMessage({ type: "clear-donor" });
    resetSelectScreen();
    setFighter("sub-zero");
    updatePatchButton();
    return;
  }

  donorValidation.state = "validating";
  resetSelectScreen();
  setFighter("sub-zero");
  mktFileName.textContent = file.name;
  mktDropZone.dataset.state = "validating";
  donorExtrasStatus.textContent = "Checking donor extras…";
  donorExtrasStatus.dataset.state = "validating";
  setFileValidation(mktValidation, "validating", "Checking MKT donor...");
  updatePatchButton();

  try {
    const bytes = await file.arrayBuffer();
    if (token !== donorValidation.token) return;
    patchWorker.postMessage(
      { type: "validate-donor", token, bytes },
      [bytes]
    );
  } catch (error) {
    if (token !== donorValidation.token) return;
    donorValidation.state = "invalid";
    mktDropZone.dataset.state = "invalid";
    donorExtrasStatus.textContent = "Donor extras disabled";
    donorExtrasStatus.dataset.state = "invalid";
    setFileValidation(
      mktValidation,
      "invalid",
      "Could not read MKT donor: " + (error.message ?? error)
    );
    updatePatchButton();
  }
}

function handleValidationResult(message) {
  if (message.kind === "target") {
    if (message.token !== targetValidation.token) return;
    if (message.ok) {
      targetValidation.state = "valid";
      romDropZone.dataset.state = "valid";
      setFileValidation(
        romValidation,
        "valid",
        "✓ Valid MKMSZ USA Rev. 0 · SHA-256 " + message.sha256
      );
    } else {
      targetValidation.state = "invalid";
      romDropZone.dataset.state = "invalid";
      setFileValidation(
        romValidation,
        "invalid",
        "✗ " + friendlyValidationError(message.error)
      );
    }
  } else if (message.kind === "donor") {
    if (message.token !== donorValidation.token) return;
    if (message.ok) {
      donorValidation.state = "valid";
      mktDropZone.dataset.state = "valid";
      donorExtrasStatus.textContent = "Toasty + Temple intro extras enabled";
      donorExtrasStatus.dataset.state = "valid";
      setFileValidation(
        mktValidation,
        "valid",
        "✓ Valid MKT USA Rev. 2 donor · SHA-256 " + message.sha256
      );
    } else {
      donorValidation.state = "invalid";
      mktDropZone.dataset.state = "invalid";
      donorExtrasStatus.textContent = "Donor extras disabled";
      donorExtrasStatus.dataset.state = "invalid";
      setFileValidation(
        mktValidation,
        "invalid",
        "✗ " + friendlyValidationError(message.error)
      );
    }
  }
  updateFighterUi();
  updatePatchButton();
}

function setFighter(fighter) {
  selectedFighter = FIGHTER_LABELS[fighter] ? fighter : "sub-zero";
  const imported = selectedFighter !== "sub-zero";
  fighterName.textContent = FIGHTER_LABELS[selectedFighter] +
    (imported ? " (imported from MKT)" : "");
  outfitLabel.textContent = FIGHTER_LABELS[selectedFighter] + " outfit";
  updateFighterUi();
  updateGameSettingsUi();
}

function updateFighterUi() {
  const donorValid = donorValidation.state === "valid";
  swapFighterButton.disabled = !donorValid || !runtimeReady || isBuilding;
  if (!donorValid) {
    fighterHint.textContent = FIGHTER_HINT_DEFAULT;
  } else if (selectedFighter !== "sub-zero") {
    fighterHint.textContent =
      FIGHTER_LABELS[selectedFighter] + " needs SPECIALS: CLASSIC; Specials Modern is locked off.";
  } else {
    fighterHint.textContent = "Pick a fighter from Mortal Kombat Trilogy's select screen.";
  }
}

function resetSelectScreen() {
  selectScreen.token += 1;
  selectScreen.state = "idle";
  selectScreen.data = null;
  selectScreen.image = null;
  selectScreen.hover = -1;
}

function selectScreenCellAt(x, y) {
  const data = selectScreen.data;
  if (!data) return -1;
  const [w, h] = data.cell;
  return data.cells.findIndex((cell) =>
    x >= cell.x && x < cell.x + w && y >= cell.y && y < cell.y + h);
}

function describeCell(index) {
  const cell = selectScreen.data?.cells[index];
  if (!cell) return "\u00a0";
  if (cell.hidden) return "? \u2014 hidden fighter";
  if (cell.fighter) {
    return cell.name + (cell.fighter === selectedFighter ? " \u2014 selected" : " \u2014 click to select");
  }
  return cell.name + " \u2014 not importable yet";
}

function drawSelectScreen() {
  const ctx = fighterCanvas.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, fighterCanvas.width, fighterCanvas.height);
  if (!selectScreen.image) return;
  ctx.drawImage(selectScreen.image, 0, 0);
  const cell = selectScreen.data.cells[selectScreen.hover];
  fighterHover.textContent = describeCell(selectScreen.hover);
  fighterCanvas.style.cursor = cell?.fighter ? "pointer" : "default";
  if (!cell) return;
  // MKT's selection box: a 2-pixel frame the size of a portrait cell.
  const [w, h] = selectScreen.data.cell;
  const t = selectScreen.data.box_thickness;
  const [r, g, b] = selectScreen.data.box_color;
  ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
  ctx.fillRect(cell.x, cell.y, w, t);
  ctx.fillRect(cell.x, cell.y + h - t, w, t);
  ctx.fillRect(cell.x, cell.y, t, h);
  ctx.fillRect(cell.x + w - t, cell.y, t, h);
}

function handleSelectScreen(message) {
  if (message.token !== selectScreen.token) return;
  if (!message.ok) {
    selectScreen.state = "error";
    fighterStageStatus.hidden = false;
    fighterStageStatus.textContent =
      "Could not read the select screen: " + (message.error || "unknown error");
    return;
  }
  const data = JSON.parse(message.meta);
  const pixels = new Uint8ClampedArray(message.rgba);
  const offscreen = document.createElement("canvas");
  offscreen.width = data.width;
  offscreen.height = data.height;
  offscreen.getContext("2d").putImageData(new ImageData(pixels, data.width, data.height), 0, 0);
  selectScreen.state = "ready";
  selectScreen.data = data;
  selectScreen.image = offscreen;
  const current = data.cells.findIndex((cell) => cell.fighter === selectedFighter);
  selectScreen.hover = current >= 0 ? current :
    data.cells.findIndex((cell) => cell.fighter);
  fighterStageStatus.hidden = true;
  drawSelectScreen();
}

function openFighterDialog() {
  if (swapFighterButton.disabled) return;
  if (selectScreen.state === "idle" || selectScreen.state === "error") {
    selectScreen.state = "loading";
    fighterStageStatus.hidden = false;
    fighterStageStatus.textContent = "Loading the select screen…";
    patchWorker.postMessage({ type: "select-screen", token: selectScreen.token });
  }
  drawSelectScreen();
  fighterDialog.showModal();
  fighterCanvas.focus();
}

function canvasPoint(event) {
  const rect = fighterCanvas.getBoundingClientRect();
  return [
    (event.clientX - rect.left) * fighterCanvas.width / rect.width,
    (event.clientY - rect.top) * fighterCanvas.height / rect.height
  ];
}

function chooseCell(index) {
  const cell = selectScreen.data?.cells[index];
  if (!cell?.fighter) return;
  fighterDialog.close("chosen");
  setFighter(cell.fighter);
}

function moveSelection(dx, dy) {
  const data = selectScreen.data;
  if (!data) return;
  const from = data.cells[selectScreen.hover] ?? data.cells[0];
  let best = -1;
  let bestScore = Infinity;
  data.cells.forEach((cell, index) => {
    const ddx = cell.column - from.column;
    const ddy = cell.row - from.row;
    if ((dx && Math.sign(ddx) !== dx) || (dy && Math.sign(ddy) !== dy)) return;
    const along = dx ? Math.abs(ddx) : Math.abs(ddy);
    const across = dx ? Math.abs(ddy) : Math.abs(ddx);
    const score = across * 10 + along;
    if (score < bestScore) {
      bestScore = score;
      best = index;
    }
  });
  if (best >= 0) {
    selectScreen.hover = best;
    drawSelectScreen();
  }
}

function handleBuildComplete(message) {
  const metadata = message.metadata;
  outputBytes = new Uint8Array(message.output);
  outputName = outputFilename(
    activeBuild.inputName,
    activeBuild.mode,
    metadata.seed
  );

  resultSeed.textContent = metadata.seed;
  resultRequiredPowers.textContent = metadata.required_powers === null
    ? "Vanilla (stock XP " + metadata.required_xp + ")"
    : metadata.required_powers +
      " (XP " + metadata.required_xp + "; " +
      activeBuild.requiredPowersMode + ")";
  outputSha.textContent = metadata.sha256;
  outputCrc.textContent = metadata.crc1 + " / " + metadata.crc2;
  resultPanel.hidden = false;

  isBuilding = false;
  stopSillyProgress();
  patchButton.textContent = "Patch MKMSZ N64";
  setLog(
    "Success. Patched " +
    (outputBytes.byteLength / 1024 / 1024).toFixed(1) +
    " MiB locally; no ROM data was uploaded."
  );
  activeBuild = null;
  updatePatchButton();
}

function handleBuildError(message) {
  console.error("MKMSZR patch failed:", message.error, message.stack || "");
  isBuilding = false;
  stopSillyProgress();
  patchButton.textContent = "Patch MKMSZ N64";

  const details = [message.error, message.stack]
    .filter(Boolean)
    .join("\n\n");
  setLog(details.replace(/^PythonError:\s*/, ""), true);
  activeBuild = null;
  updatePatchButton();
}

function handleWorkerMessage(event) {
  const message = event.data || {};

  if (message.type === "runtime-status") {
    runtimeStatus.textContent = message.message;
    return;
  }

  if (message.type === "runtime-ready") {
    runtimeReady = true;
    runtimeStatus.dataset.state = "ready";
    runtimeStatus.textContent = "Patcher ready";
    updateFighterUi();
    updatePatchButton();
    return;
  }

  if (message.type === "runtime-error") {
    runtimeReady = false;
    runtimeStatus.dataset.state = "error";
    runtimeStatus.textContent = "Runtime failed";
    setLog(
      "Could not initialize browser patcher: " +
      (message.error || "unknown error"),
      true
    );
    updatePatchButton();
    return;
  }

  if (message.type === "validation-result") {
    handleValidationResult(message);
    return;
  }

  if (message.type === "build-complete") {
    handleBuildComplete(message);
    return;
  }

  if (message.type === "select-screen") {
    handleSelectScreen(message);
    return;
  }

  if (message.type === "build-error") {
    handleBuildError(message);
  }
}

function initWorker() {
  const workerUrl = new URL("./patch-worker.js", import.meta.url);
  workerUrl.search = import.meta.url.search;
  patchWorker = new Worker(workerUrl, { name: "mkmszr-patcher" });
  patchWorker.addEventListener("message", handleWorkerMessage);
  patchWorker.addEventListener("error", (event) => {
    console.error(event);
    runtimeReady = false;
    runtimeStatus.dataset.state = "error";
    runtimeStatus.textContent = "Runtime failed";
    setLog("Browser patch worker crashed: " + event.message, true);
    updatePatchButton();
  });
  patchWorker.postMessage({ type: "init" });
}

async function patchRom() {
  resultPanel.hidden = true;
  outputBytes = null;

  const targetFile = romFile.files?.[0];
  const donorFile = mktN64File.files?.[0];
  if (!targetFile || targetValidation.state !== "valid") {
    setLog("Choose and validate the clean MKMSZ N64 target ROM first.", true);
    return;
  }
  if (donorFile && donorValidation.state !== "valid") {
    setLog("The selected MKT donor must validate before patching.", true);
    return;
  }
  if (selectedFighter !== "sub-zero" && !donorFile) {
    setLog("An imported fighter needs the validated MKT donor ROM.", true);
    return;
  }

  const customPowerText = customRequiredPowers.value.trim();
  const customPowerCount = Number(customPowerText);
  if (requiredPowersMode.value === "custom" &&
      (!customPowerText || !Number.isInteger(customPowerCount) ||
       customPowerCount < 0 || customPowerCount > 9)) {
    setLog("Custom required powers must be a whole number from 0 to 9.", true);
    return;
  }

  const livesText = startingLives.value.trim();
  const livesValue = Number(livesText);
  if (!livesText || !Number.isInteger(livesValue) ||
      livesValue < 1 || livesValue > 10) {
    setLog("Lives must be a whole number from 1 to 10.", true);
    return;
  }

  const continuesText = startingContinues.value.trim();
  const continuesValue = Number(continuesText);
  if (!continuesText || !Number.isInteger(continuesValue) ||
      continuesValue < 0 || continuesValue > 5) {
    setLog("Continues must be a whole number from 0 to 5.", true);
    return;
  }

  const mode = outfitMode.value;
  let editionValue = normalizeEditionName(editionName.value)
    .trim()
    .replace(/\s+/g, " ");
  if (!editionValue) editionValue = "SUB-ZERO";
  editionName.value = editionValue;

  let seedValue = seed.value.trim();
  if (!seedValue) {
    seedValue = generateSeed();
    seed.value = seedValue;
    updateSummaries();
  }

  activeBuild = {
    inputName: targetFile.name,
    mode,
    requiredPowersMode: requiredPowersMode.value
  };

  isBuilding = true;
  patchButton.textContent = "Patching…";
  setLog("");
  startSillyProgress();
  updatePatchButton();

  patchWorker.postMessage({
    type: "patch",
    hasDonor: Boolean(donorFile),
    config: {
      outfitMode: mode,
      seed: seedValue,
      rgb: customColor.value,
      editionName: editionValue,
      turnLock: turnLock.checked,
      attackModern: attackModern.checked,
      specialsModern: specialsModern.checked,
      jumpButton: jumpButton.checked,
      runAuto: runAuto.checked,
      shufflePowerProgression: shufflePowerProgression.checked,
      enemyRandomization: enemyRandomization.checked,
      powersAsPickups: powersAsPickups.checked,
      requiredPowersMode: requiredPowersMode.value,
      globalCompletionMode: globalCompletionMode.value,
      customRequiredPowers:
        requiredPowersMode.value === "custom" ? customPowerCount : 0,
      difficulty: difficulty.value,
      lives: livesValue,
      continues: continuesValue,
      persistHp: persistHp.checked,
      debugAllKeys: debugAllKeys.checked,
      disableAudioFix: disableAudioFix.checked,
      fighter: selectedFighter
    }
  });
}

function downloadOutput() {
  if (!outputBytes) return;
  const blob = new Blob([outputBytes], { type: "application/octet-stream" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = outputName;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

romFile.addEventListener("change", validateTargetSelection);
mktN64File.addEventListener("change", validateDonorSelection);
wireDropZone(romDropZone, romFile);
wireDropZone(mktDropZone, mktN64File);
randomSeedButton.addEventListener("click", () => {
  seed.value = generateSeed();
  updateSummaries();
});
copySeedButton.addEventListener("click", () => copyText(seed.value.trim(), copySeedButton));
copyResultSeedButton.addEventListener("click", () => copyText(resultSeed.textContent, copyResultSeedButton));
changeSettingsButton.addEventListener("click", () => {
  document.querySelector("#outfitMode").scrollIntoView({ behavior: "smooth", block: "center" });
});
outfitMode.addEventListener("change", updateModeUi);
attackModern.addEventListener("change", updateGameSettingsUi);
specialsModern.addEventListener("change", updateGameSettingsUi);
turnLock.addEventListener("change", updateSummaries);
jumpButton.addEventListener("change", updateSummaries);
runAuto.addEventListener("change", updateSummaries);
shufflePowerProgression.addEventListener("change", updateSummaries);
enemyRandomization.addEventListener("change", updateSummaries);
powersAsPickups.addEventListener("change", updateSummaries);
difficulty.addEventListener("change", updateSummaries);
startingLives.addEventListener("input", updateSummaries);
startingContinues.addEventListener("input", updateSummaries);
persistHp.addEventListener("change", updateSummaries);
debugAllKeys.addEventListener("change", updateSummaries);
disableAudioFix.addEventListener("change", updateSummaries);
globalCompletionMode.addEventListener("change", updateSummaries);
customRequiredPowers.addEventListener("input", updateSummaries);
seed.addEventListener("input", updateSummaries);
requiredPowersMode.addEventListener("change", updateRequiredPowersUi);
customColor.addEventListener("input", () => {
  colorValue.value = customColor.value.toUpperCase();
});
editionName.addEventListener("input", () => {
  const normalized = normalizeEditionName(editionName.value);
  if (editionName.value !== normalized) editionName.value = normalized;
});
patchButton.addEventListener("click", patchRom);
swapFighterButton.addEventListener("click", openFighterDialog);
fighterDialog.addEventListener("close", () => {
  if (fighterDialog.returnValue === "sub-zero") setFighter("sub-zero");
});
fighterCanvas.addEventListener("mousemove", (event) => {
  const [x, y] = canvasPoint(event);
  const index = selectScreenCellAt(x, y);
  if (index >= 0 && index !== selectScreen.hover) {
    selectScreen.hover = index;
    drawSelectScreen();
  }
});
fighterCanvas.addEventListener("click", (event) => {
  const [x, y] = canvasPoint(event);
  chooseCell(selectScreenCellAt(x, y));
});
fighterCanvas.addEventListener("keydown", (event) => {
  const moves = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
  if (moves[event.key]) {
    event.preventDefault();
    moveSelection(...moves[event.key]);
  } else if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    chooseCell(selectScreen.hover);
  }
});
downloadButton.addEventListener("click", downloadOutput);

setFileValidation(romValidation, "idle", "No target ROM selected.");
setFileValidation(mktValidation, "idle", "Optional donor not selected.");
setFighter("sub-zero");
updateModeUi();
updateGameSettingsUi();
updateRequiredPowersUi();
updateSummaries();
updatePatchButton();
initWorker();
