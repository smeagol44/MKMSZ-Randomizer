const runtimeStatus = document.querySelector("#runtimeStatus");
const romFile = document.querySelector("#romFile");
const outfitMode = document.querySelector("#outfitMode");
const seed = document.querySelector("#seed");
const seedField = document.querySelector("#seedField");
const colorField = document.querySelector("#colorField");
const customColor = document.querySelector("#customColor");
const colorValue = document.querySelector("#colorValue");
const patchButton = document.querySelector("#patchButton");
const resultPanel = document.querySelector("#result");
const resultSeed = document.querySelector("#resultSeed");
const outputSha = document.querySelector("#outputSha");
const outputCrc = document.querySelector("#outputCrc");
const patchList = document.querySelector("#patchList");
const pickupMode = document.querySelector("#pickupMode");
const bootPhrase = document.querySelector("#bootPhrase");
const downloadButton = document.querySelector("#downloadButton");
const log = document.querySelector("#log");

let pyodide;
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

function generateSeed() {
  const words = new Uint32Array(2);
  crypto.getRandomValues(words);
  return Array.from(words, (value) => value.toString(16).padStart(8, "0"))
    .join("")
    .toUpperCase();
}

function outputFilename(inputName, mode, seedValue) {
  const stem = inputName.replace(/\.(z64|n64|v64)$/i, "");
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

    runtimeStatus.dataset.state = "ready";
    runtimeStatus.textContent = "Patcher ready";
    patchButton.disabled = false;
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

  const file = romFile.files?.[0];
  if (!file) {
    setLog("Choose a clean MKMSZ USA .z64 ROM first.", true);
    return;
  }

  const mode = outfitMode.value;
  let seedValue = seed.value.trim();
  if (!seedValue) {
    seedValue = generateSeed();
    seed.value = seedValue;
  }

  patchButton.disabled = true;
  patchButton.textContent = "Patching…";
  setLog("Reading ROM locally…");

  try {
    const inputBytes = new Uint8Array(await file.arrayBuffer());
    pyodide.FS.writeFile("/tmp/input.z64", inputBytes);

    try { pyodide.FS.unlink("/tmp/output.z64"); } catch (_) {}

    pyodide.globals.set("web_outfit_mode", mode);
    pyodide.globals.set("web_seed", seedValue);
    pyodide.globals.set("web_rgb", customColor.value);

    setLog("Validating clean ROM and applying patches…");

    await pyodide.runPythonAsync(`
from pathlib import Path
from mkmszr.config import OutfitConfig, RandomizerConfig
from mkmszr.data.boot_phrases import select_boot_phrase
from mkmszr.patcher import patch_file

_mode = str(web_outfit_mode)
_seed = str(web_seed)
_rgb_hex = str(web_rgb).lstrip("#")
_rgb = tuple(int(_rgb_hex[i:i+2], 16) for i in (0, 2, 4))
_boot_phrase = select_boot_phrase(_seed)

_config = RandomizerConfig(
    seed=_seed,
    outfit=OutfitConfig(mode=_mode, rgb=_rgb if _mode == "rgb" else None),
)
_result = patch_file(Path("/tmp/input.z64"), Path("/tmp/output.z64"), _config)
web_patch_result = {
    "seed": _seed,
    "crc1": f"{_result.crc1:08X}",
    "crc2": f"{_result.crc2:08X}",
    "sha256": _result.output_sha256,
    "patches": [patch.name for patch in _result.patches],
    "pickup_mode": (
        "Stage-local ordinary pickups (84) + 9 XP progression rewards"
        if any(patch.name == "xp-progression" for patch in _result.patches)
        else "Stage-local ordinary pickups (84)"
        if any(patch.name == "pickup-randomization" for patch in _result.patches)
        else "Off"
    ),
    "boot_phrase": " / ".join(part for part in _boot_phrase if part),
}
`);

    const proxy = pyodide.globals.get("web_patch_result");
    const metadata = proxy.toJs({ dict_converter: Object.fromEntries });
    proxy.destroy();

    outputBytes = pyodide.FS.readFile("/tmp/output.z64");
    outputName = outputFilename(file.name, mode, metadata.seed);

    resultSeed.textContent = metadata.seed;
    outputSha.textContent = metadata.sha256;
    outputCrc.textContent = `${metadata.crc1} / ${metadata.crc2}`;
    patchList.textContent = metadata.patches.length ? metadata.patches.join(", ") : "CRC refresh only";
    pickupMode.textContent = metadata.pickup_mode;
    bootPhrase.textContent = metadata.boot_phrase;

    resultPanel.hidden = false;
    setLog(`Success. Patched ${(outputBytes.byteLength / 1024 / 1024).toFixed(1)} MiB locally; no ROM data was uploaded.`);
  } catch (error) {
    console.error(error);
    const message = error.message ?? String(error);
    setLog(message.replace(/^PythonError:\s*/, ""), true);
  } finally {
    patchButton.disabled = false;
    patchButton.textContent = "Patch ROM";
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
customColor.addEventListener("input", () => { colorValue.value = customColor.value.toUpperCase(); });
patchButton.addEventListener("click", patchRom);
downloadButton.addEventListener("click", downloadOutput);

updateModeUi();
bootRuntime();
