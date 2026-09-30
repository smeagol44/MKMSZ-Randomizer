const runtimeStatus = document.querySelector("#runtimeStatus");
const romFile = document.querySelector("#romFile");
const mktN64File = document.querySelector("#mktN64File");
const outfitMode = document.querySelector("#outfitMode");
const editionName = document.querySelector("#editionName");
const seed = document.querySelector("#seed");
const seedField = document.querySelector("#seedField");
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
const customRequiredPowersField = document.querySelector("#customRequiredPowersField");
const customRequiredPowers = document.querySelector("#customRequiredPowers");
const patchButton = document.querySelector("#patchButton");
const resultPanel = document.querySelector("#result");
const resultSeed = document.querySelector("#resultSeed");
const resultRequiredPowers = document.querySelector("#resultRequiredPowers");
const outputSha = document.querySelector("#outputSha");
const outputCrc = document.querySelector("#outputCrc");
const downloadButton = document.querySelector("#downloadButton");
const log = document.querySelector("#log");

let pyodide;
let runtimeReady = false;
let outputBytes = null;
let outputName = "MKMSZR-patched.z64";

function setLog(message, error = false) {
  log.textContent = message;
  log.style.color = error ? "#ffaaaa" : "";
}

function updateModeUi() {
  colorField.hidden = outfitMode.value !== "rgb";
  seedField.style.opacity = "1";
}

function updatePatchButton() {
  patchButton.disabled = !runtimeReady;
}

function updateGameSettingsUi() {
  const jumpAvailable = attackModern.checked && specialsModern.checked;
  if (!jumpAvailable) jumpButton.checked = false;
  jumpButton.disabled = !jumpAvailable;
}

function updateRequiredPowersUi() {
  const isCustom = requiredPowersMode.value === "custom";
  customRequiredPowersField.hidden = !isCustom;
  customRequiredPowers.disabled = !isCustom;
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

function outputFilename(inputName, mode, seedValue) {
  const stem = inputName.replace(/\.z64$/i, "");
  let suffix = mode === "vanilla" ? "mkmszr" : `mkmszr-${mode}`;
  const safeSeed = seedValue.replace(/[^a-z0-9_-]/gi, "").slice(0, 24);
  if (safeSeed) suffix += `-${safeSeed}`;
  return `${stem}-${suffix}.z64`;
}

async function bootRuntime() {
  try {
    runtimeStatus.textContent = "Loading Pyodide…";
    pyodide = await loadPyodide();

    runtimeStatus.textContent = "Loading MKMSZR core…";
    await pyodide.loadPackage("micropip");
    const wheelNameResponse = await fetch("./wheel-name.txt", { cache: "no-store" });
    if (!wheelNameResponse.ok) {
      throw new Error(`Could not resolve MKMSZR wheel name (HTTP ${wheelNameResponse.status})`);
    }
    const wheelName = (await wheelNameResponse.text()).trim();
    if (!wheelName.endsWith(".whl")) {
      throw new Error(`Invalid MKMSZR wheel manifest: ${wheelName || "(empty)"}`);
    }
    const wheelUrl = new URL(`./${wheelName}`, window.location.href).href;
    pyodide.globals.set("web_wheel_url", wheelUrl);
    await pyodide.runPythonAsync(`
import micropip
await micropip.install(str(web_wheel_url))
`);

    runtimeReady = true;
    runtimeStatus.dataset.state = "ready";
    runtimeStatus.textContent = "Patcher ready";
    updatePatchButton();
  } catch (error) {
    console.error(error);
    runtimeStatus.dataset.state = "error";
    runtimeStatus.textContent = "Runtime failed";
    setLog(`Could not initialize browser patcher: ${error.message ?? error}`, true);
  }
}

async function patchRom() {
  resultPanel.hidden = true;
  outputBytes = null;

  const targetFile = romFile.files?.[0];
  const donorFile = mktN64File.files?.[0];
  if (!targetFile) {
    setLog("Choose the clean MKMSZ N64 target ROM first.", true);
    return;
  }

  const customPowerText = customRequiredPowers.value.trim();
  const customPowerCount = Number(customPowerText);
  if (requiredPowersMode.value === "custom" &&
      (!customPowerText || !Number.isInteger(customPowerCount) || customPowerCount < 0 || customPowerCount > 9)) {
    setLog("Custom required powers must be a whole number from 0 to 9.", true);
    return;
  }

  const mode = outfitMode.value;
  let editionValue = normalizeEditionName(editionName.value).trim().replace(/\s+/g, " ");
  if (!editionValue) editionValue = "SUB-ZERO";
  editionName.value = editionValue;

  let seedValue = seed.value.trim();
  if (!seedValue) {
    seedValue = generateSeed();
    seed.value = seedValue;
  }

  patchButton.disabled = true;
  patchButton.textContent = "Patching…";
  setLog("Reading game files locally…");

  try {
    const targetBytes = await targetFile.arrayBuffer();
    pyodide.FS.writeFile("/tmp/input.z64", new Uint8Array(targetBytes));
    try { pyodide.FS.unlink("/tmp/mkt.z64"); } catch (_) {}
    if (donorFile) {
      const donorBytes = await donorFile.arrayBuffer();
      pyodide.FS.writeFile("/tmp/mkt.z64", new Uint8Array(donorBytes));
    }

    try { pyodide.FS.unlink("/tmp/output.z64"); } catch (_) {}

    pyodide.globals.set("web_has_mkt_donor", Boolean(donorFile));
    pyodide.globals.set("web_outfit_mode", mode);
    pyodide.globals.set("web_seed", seedValue);
    pyodide.globals.set("web_rgb", customColor.value);
    pyodide.globals.set("web_edition_name", editionValue);
    pyodide.globals.set("web_turn_lock", turnLock.checked);
    pyodide.globals.set("web_attack_modern", attackModern.checked);
    pyodide.globals.set("web_specials_modern", specialsModern.checked);
    pyodide.globals.set("web_jump_button", jumpButton.checked);
    pyodide.globals.set("web_run_auto", runAuto.checked);
    pyodide.globals.set("web_shuffle_power_progression", shufflePowerProgression.checked);
    pyodide.globals.set("web_enemy_randomization", enemyRandomization.checked);
    pyodide.globals.set("web_powers_as_pickups", powersAsPickups.checked);
    pyodide.globals.set("web_required_powers_mode", requiredPowersMode.value);
    pyodide.globals.set("web_custom_required_powers", requiredPowersMode.value === "custom" ? customPowerCount : 0);

    setLog("Validating game files and applying patches…");

    await pyodide.runPythonAsync(`
from pathlib import Path
from mkmszr.config import GameSettingsConfig, OutfitConfig, RandomizerConfig
from mkmszr.donors import extract_temple_intro_audio_assets, extract_toasty_assets
from mkmszr.patcher import patch_file

_mode = str(web_outfit_mode)
_seed = str(web_seed)
_rgb_hex = str(web_rgb).lstrip("#")
_rgb = tuple(int(_rgb_hex[i:i+2], 16) for i in (0, 2, 4))
_edition_name = str(web_edition_name)
_config = RandomizerConfig(
    seed=_seed,
    outfit=OutfitConfig(mode=_mode, rgb=_rgb if _mode == "rgb" else None),
    edition_name=_edition_name,
    shuffle_power_progression=bool(web_shuffle_power_progression),
    enemy_randomization=bool(web_enemy_randomization),
    powers_as_pickups=bool(web_powers_as_pickups),
    required_powers_mode=str(web_required_powers_mode),
    custom_required_powers=int(web_custom_required_powers) if str(web_required_powers_mode) == "custom" else None,
    game_settings=GameSettingsConfig(
        turn_lock=bool(web_turn_lock),
        attack_modern=bool(web_attack_modern),
        specials_modern=bool(web_specials_modern),
        jump_button=bool(web_jump_button),
        run_auto=bool(web_run_auto),
    ),
)
_mkt_bytes = Path("/tmp/mkt.z64").read_bytes() if bool(web_has_mkt_donor) else None
_toasty_assets = extract_toasty_assets(_mkt_bytes) if _mkt_bytes is not None else None
_temple_intro_audio_assets = (
    extract_temple_intro_audio_assets(_mkt_bytes) if _mkt_bytes is not None else None
)
_result = patch_file(
    Path("/tmp/input.z64"),
    Path("/tmp/output.z64"),
    _config,
    toasty_assets=_toasty_assets,
    temple_intro_audio_assets=_temple_intro_audio_assets,
)
web_patch_result = {
    "seed": _seed,
    "crc1": f"{_result.crc1:08X}",
    "crc2": f"{_result.crc2:08X}",
    "sha256": _result.output_sha256,
    "required_powers": _result.required_powers_count,
    "required_xp": _result.required_powers_xp,
    "enemy_randomization": bool(web_enemy_randomization),
}
`);

    const proxy = pyodide.globals.get("web_patch_result");
    const metadata = proxy.toJs({ dict_converter: Object.fromEntries });
    proxy.destroy();

    outputBytes = pyodide.FS.readFile("/tmp/output.z64");
    outputName = outputFilename(targetFile.name, mode, metadata.seed);

    resultSeed.textContent = metadata.seed;
    resultRequiredPowers.textContent = metadata.required_powers === null
      ? `Vanilla (stock XP ${metadata.required_xp})`
      : `${metadata.required_powers} (XP ${metadata.required_xp}; ${requiredPowersMode.value})`;
    outputSha.textContent = metadata.sha256;
    outputCrc.textContent = `${metadata.crc1} / ${metadata.crc2}`;
    resultPanel.hidden = false;
    setLog(
      `Success. Patched ${(outputBytes.byteLength / 1024 / 1024).toFixed(1)} MiB locally; no ROM data was uploaded.`
    );
  } catch (error) {
    console.error(error);
    const message = error.message ?? String(error);
    setLog(message.replace(/^PythonError:\s*/, ""), true);
  } finally {
    updatePatchButton();
    patchButton.textContent = "Patch MKMSZ N64";
  }
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

outfitMode.addEventListener("change", updateModeUi);
attackModern.addEventListener("change", updateGameSettingsUi);
specialsModern.addEventListener("change", updateGameSettingsUi);
requiredPowersMode.addEventListener("change", updateRequiredPowersUi);
customColor.addEventListener("input", () => { colorValue.value = customColor.value.toUpperCase(); });
editionName.addEventListener("input", () => {
  const normalized = normalizeEditionName(editionName.value);
  if (editionName.value !== normalized) editionName.value = normalized;
});
patchButton.addEventListener("click", patchRom);
downloadButton.addEventListener("click", downloadOutput);

updateModeUi();
updateGameSettingsUi();
updateRequiredPowersUi();
bootRuntime();
