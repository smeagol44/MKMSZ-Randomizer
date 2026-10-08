#!/usr/bin/env python3
"""Generate a separate Flatpak manifest from pinned Flathub RMG v0.9.0.

Requires network access in GitHub Actions; never modifies the user's installation.
"""
import json
import urllib.request
from pathlib import Path

import yaml

base = "https://raw.githubusercontent.com/flathub/com.github.Rosalie241.RMG/master/com.github.Rosalie241.RMG.yml"
with urllib.request.urlopen(base, timeout=30) as req:
    manifest = yaml.safe_load(req.read())
assert manifest["app-id"] == "com.github.Rosalie241.RMG"
assert manifest["runtime-version"] == "6.11"
rmg = next(m for m in manifest["modules"] if m["name"] == "RMG")
source = next(s for s in rmg["sources"] if s.get("type") == "git")
assert source["tag"] == "v0.9.0"
assert source["commit"] == "453f6639734537908c4c2ca35244255bc5424e3d"
# Recover relative patch inputs required by the pinned Flathub recipe.
for module in manifest["modules"]:
    for entry in module.get("sources", []):
        if entry.get("type") == "patch":
            patch_path = Path(entry["path"])
            patch_path.parent.mkdir(parents=True, exist_ok=True)
            patch_url = "https://raw.githubusercontent.com/flathub/com.github.Rosalie241.RMG/master/" + str(patch_path)
            with urllib.request.urlopen(patch_url, timeout=30) as response:
                patch_path.write_bytes(response.read())
manifest["app-id"] = "org.mkmszr.RMGObserver"
manifest["command"] = "RMG"
manifest["finish-args"].extend([
    "--filesystem=xdg-cache/mkmszr-observer:create",
    "--filesystem=xdg-download:rw",
])
# Source patch is applied in flatpak-builder's sources phase, before CMake.
rmg["sources"].extend([
    {"type": "file", "path": "observer_patch.py"},
    {"type": "shell", "commands": ["python3 observer_patch.py"]},
])
rmg.setdefault("config-opts", []).append("-DINSTALL_DESKTOP_FILE=OFF")
Path("org.mkmszr.RMGObserver.json").write_text(json.dumps(manifest, indent=2))
print("Generated isolated Flatpak manifest; source pinned", source["commit"])
