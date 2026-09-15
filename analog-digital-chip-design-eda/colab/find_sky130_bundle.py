#!/usr/bin/env python3
"""Locate pinned Sky130 archives on a mounted Google Drive."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


NAMES = ("sky130-ngspice-bundle.tar.gz", "sky130-pdk-deps.tar.gz", "sky130-ngspice-bundle-manifest.json")


def main() -> int:
    roots = [Path("/content/drive/MyDrive"), Path("/content/drive/Shareddrives")]
    found: dict[str, str] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.name in NAMES and path.name not in found:
                found[path.name] = str(path)
    copied = []
    for name, source in found.items():
        destination = Path("/content") / name
        shutil.copy2(source, destination)
        copied.append(str(destination))
    report = {"result_type": "colab_sky130_bundle_locator", "found": found, "copied": copied, "status": "ready" if "sky130-ngspice-bundle.tar.gz" in found and "sky130-ngspice-bundle-manifest.json" in found else "bundle_incomplete"}
    Path("/content/sky130-bundle-locator.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
