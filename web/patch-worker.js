const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";

const INSTALL_CORE_PY = [
  "import micropip",
  "await micropip.install(str(web_wheel_url))"
].join("\n");

const VALIDATE_TARGET_PY = [
  "from pathlib import Path",
  "from mkmszr.rom import RomImage",
  "_web_target_source = Path('/tmp/preflight-target.rom').read_bytes()",
  "_web_target_rom = RomImage.from_bytes(_web_target_source, require_clean=True)",
  "web_validation_result = {'sha256': _web_target_rom.source_sha256}",
  "del _web_target_source"
].join("\n");

const VALIDATE_DONOR_PY = [
  "from pathlib import Path",
  "from mkmszr.donors.mkt_n64 import MKT_N64_REV2_SHA256, validate_mkt_n64_rev2",
  "_web_mkt_bytes = Path('/tmp/preflight-mkt.z64').read_bytes()",
  "validate_mkt_n64_rev2(_web_mkt_bytes)",
  "web_validation_result = {'sha256': MKT_N64_REV2_SHA256}"
].join("\n");

const PATCH_PY = [
  "from pathlib import Path",
  "from mkmszr.config import GameSettingsConfig, OutfitConfig, RandomizerConfig",
  "from mkmszr.donors import extract_temple_intro_audio_assets, extract_toasty_assets",
  "from mkmszr.patcher import patch_rom",
  "",
  "_mode = str(web_outfit_mode)",
  "_seed = str(web_seed)",
  "_rgb_hex = str(web_rgb).lstrip('#')",
  "_rgb = tuple(int(_rgb_hex[i:i+2], 16) for i in (0, 2, 4))",
  "_edition_name = str(web_edition_name)",
  "_config = RandomizerConfig(",
  "    seed=_seed,",
  "    outfit=OutfitConfig(mode=_mode, rgb=_rgb if _mode == 'rgb' else None),",
  "    edition_name=_edition_name,",
  "    shuffle_power_progression=bool(web_shuffle_power_progression),",
  "    enemy_randomization=bool(web_enemy_randomization),",
  "    powers_as_pickups=bool(web_powers_as_pickups),",
  "    required_powers_mode=str(web_required_powers_mode),",
  "    global_completion_mode=str(web_global_completion_mode),",
  "    custom_required_powers=int(web_custom_required_powers) if str(web_required_powers_mode) == 'custom' else None,",
  "    difficulty=str(web_difficulty),",
  "    lives=int(web_lives),",
  "    continues=int(web_continues),",
  "    persist_hp=bool(web_persist_hp),",
  "    game_settings=GameSettingsConfig(",
  "        turn_lock=bool(web_turn_lock),",
  "        attack_modern=bool(web_attack_modern),",
  "        specials_modern=bool(web_specials_modern),",
  "        jump_button=bool(web_jump_button),",
  "        run_auto=bool(web_run_auto),",
  "    ),",
  ")",
  "_mkt_bytes = _web_mkt_bytes if bool(web_has_mkt_donor) else None",
  "_toasty_assets = extract_toasty_assets(_mkt_bytes) if _mkt_bytes is not None else None",
  "_temple_intro_audio_assets = (",
  "    extract_temple_intro_audio_assets(_mkt_bytes) if _mkt_bytes is not None else None",
  ")",
  "_result = patch_rom(",
  "    _web_target_rom.fresh_copy(),",
  "    _config,",
  "    toasty_assets=_toasty_assets,",
  "    temple_intro_audio_assets=_temple_intro_audio_assets,",
  ")",
  "Path('/tmp/output.z64').write_bytes(_result.data)",
  "if Path('/tmp/output.z64').read_bytes() != _result.data:",
  "    raise OSError('output re-read verification failed')",
  "web_patch_result = {",
  "    'seed': _seed,",
  "    'crc1': f'{_result.crc1:08X}',",
  "    'crc2': f'{_result.crc2:08X}',",
  "    'sha256': _result.output_sha256,",
  "    'required_powers': _result.required_powers_count,",
  "    'required_xp': _result.required_powers_xp,",
  "    'enemy_randomization': bool(web_enemy_randomization),",
  "}"
].join("\n");

let pyodide = null;
let bootPromise = null;
let queue = Promise.resolve();
let targetReady = false;
let donorReady = false;

function errorPayload(error) {
  return {
    error: error?.message ?? String(error),
    stack: error?.stack ?? ""
  };
}

async function bootRuntime() {
  postMessage({ type: "runtime-status", message: "Loading Pyodide…" });
  importScripts(PYODIDE_BASE + "pyodide.js");
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

  postMessage({ type: "runtime-status", message: "Loading MKMSZR core…" });
  await pyodide.loadPackage("micropip");

  const manifestUrl = new URL("./wheel-name.txt", self.location.href);
  manifestUrl.search = "";
  const wheelNameResponse = await fetch(manifestUrl, { cache: "no-store" });
  if (!wheelNameResponse.ok) {
    throw new Error(
      "Could not resolve MKMSZR wheel name (HTTP " +
      wheelNameResponse.status + ")"
    );
  }

  const wheelName = (await wheelNameResponse.text()).trim();
  if (!wheelName.endsWith(".whl")) {
    throw new Error(
      "Invalid MKMSZR wheel manifest: " + (wheelName || "(empty)")
    );
  }

  const wheelUrl = new URL("./" + wheelName, self.location.href).href;
  pyodide.globals.set("web_wheel_url", wheelUrl);
  await pyodide.runPythonAsync(INSTALL_CORE_PY);

  pyodide.runPython("_web_target_rom = None\n_web_mkt_bytes = None");
  postMessage({ type: "runtime-ready" });
}

function ensureRuntime() {
  if (!bootPromise) {
    bootPromise = bootRuntime().catch((error) => {
      postMessage({ type: "runtime-error", ...errorPayload(error) });
      throw error;
    });
  }
  return bootPromise;
}

function readPythonDict(name) {
  const proxy = pyodide.globals.get(name);
  try {
    return proxy.toJs({ dict_converter: Object.fromEntries });
  } finally {
    proxy.destroy();
  }
}

function unlinkIfPresent(path) {
  try {
    pyodide.FS.unlink(path);
  } catch (_) {
    // File is already absent.
  }
}

async function validateTarget(message) {
  await ensureRuntime();
  targetReady = false;
  pyodide.runPython("_web_target_rom = None");

  pyodide.FS.writeFile(
    "/tmp/preflight-target.rom",
    new Uint8Array(message.bytes)
  );

  try {
    await pyodide.runPythonAsync(VALIDATE_TARGET_PY);
    const metadata = readPythonDict("web_validation_result");
    targetReady = true;
    postMessage({
      type: "validation-result",
      kind: "target",
      token: message.token,
      ok: true,
      sha256: metadata.sha256
    });
  } finally {
    unlinkIfPresent("/tmp/preflight-target.rom");
  }
}

async function validateDonor(message) {
  await ensureRuntime();
  donorReady = false;
  pyodide.runPython("_web_mkt_bytes = None");

  pyodide.FS.writeFile(
    "/tmp/preflight-mkt.z64",
    new Uint8Array(message.bytes)
  );

  try {
    await pyodide.runPythonAsync(VALIDATE_DONOR_PY);
    const metadata = readPythonDict("web_validation_result");
    donorReady = true;
    postMessage({
      type: "validation-result",
      kind: "donor",
      token: message.token,
      ok: true,
      sha256: metadata.sha256
    });
  } finally {
    unlinkIfPresent("/tmp/preflight-mkt.z64");
  }
}

function setPatchGlobals(config, hasDonor) {
  pyodide.globals.set("web_has_mkt_donor", Boolean(hasDonor));
  pyodide.globals.set("web_outfit_mode", config.outfitMode);
  pyodide.globals.set("web_seed", config.seed);
  pyodide.globals.set("web_rgb", config.rgb);
  pyodide.globals.set("web_edition_name", config.editionName);
  pyodide.globals.set("web_turn_lock", config.turnLock);
  pyodide.globals.set("web_attack_modern", config.attackModern);
  pyodide.globals.set("web_specials_modern", config.specialsModern);
  pyodide.globals.set("web_jump_button", config.jumpButton);
  pyodide.globals.set("web_run_auto", config.runAuto);
  pyodide.globals.set(
    "web_shuffle_power_progression",
    config.shufflePowerProgression
  );
  pyodide.globals.set("web_enemy_randomization", config.enemyRandomization);
  pyodide.globals.set("web_powers_as_pickups", config.powersAsPickups);
  pyodide.globals.set("web_required_powers_mode", config.requiredPowersMode);
  pyodide.globals.set("web_global_completion_mode", config.globalCompletionMode);
  pyodide.globals.set(
    "web_custom_required_powers",
    config.customRequiredPowers
  );
  pyodide.globals.set("web_difficulty", config.difficulty);
  pyodide.globals.set("web_lives", config.lives);
  pyodide.globals.set("web_continues", config.continues);
  pyodide.globals.set("web_persist_hp", config.persistHp);
}

async function patchRom(message) {
  await ensureRuntime();
  if (!targetReady) {
    throw new Error("The target ROM is not validated.");
  }
  if (message.hasDonor && !donorReady) {
    throw new Error("The selected MKT donor is not validated.");
  }

  unlinkIfPresent("/tmp/output.z64");
  setPatchGlobals(message.config, message.hasDonor);
  await pyodide.runPythonAsync(PATCH_PY);

  const metadata = readPythonDict("web_patch_result");
  const output = pyodide.FS.readFile("/tmp/output.z64");
  unlinkIfPresent("/tmp/output.z64");

  pyodide.runPython(
    "import gc\n_result = None\n_toasty_assets = None\n_temple_intro_audio_assets = None\ngc.collect()"
  );

  postMessage(
    {
      type: "build-complete",
      metadata,
      output: output.buffer
    },
    [output.buffer]
  );
}

async function handleMessage(message) {
  if (message.type === "init") {
    await ensureRuntime();
    return;
  }
  if (message.type === "validate-target") {
    await validateTarget(message);
    return;
  }
  if (message.type === "validate-donor") {
    await validateDonor(message);
    return;
  }
  if (message.type === "clear-target") {
    targetReady = false;
    if (pyodide) pyodide.runPython("_web_target_rom = None");
    return;
  }
  if (message.type === "clear-donor") {
    donorReady = false;
    if (pyodide) pyodide.runPython("_web_mkt_bytes = None");
    return;
  }
  if (message.type === "patch") {
    await patchRom(message);
  }
}

function reportMessageError(message, error) {
  const payload = errorPayload(error);

  if (message.type === "validate-target") {
    targetReady = false;
    postMessage({
      type: "validation-result",
      kind: "target",
      token: message.token,
      ok: false,
      ...payload
    });
    return;
  }

  if (message.type === "validate-donor") {
    donorReady = false;
    postMessage({
      type: "validation-result",
      kind: "donor",
      token: message.token,
      ok: false,
      ...payload
    });
    return;
  }

  if (message.type === "patch") {
    postMessage({ type: "build-error", ...payload });
  }
}

self.onmessage = (event) => {
  const message = event.data || {};
  queue = queue
    .then(() => handleMessage(message))
    .catch((error) => {
      reportMessageError(message, error);
    });
};
