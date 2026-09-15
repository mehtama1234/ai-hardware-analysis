#!/usr/bin/env python3
"""Preflight a fresh Colab VM for continuous Sky130 SAR experiments.

Upload the pinned model bundles first. The script installs ngspice, unpacks the
bundles, creates the local PDK path expected by the runners, and writes a
machine-readable preflight receipt before any circuit run is attempted.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tarfile
from pathlib import Path


def main() -> int:
    bundle = Path("/content/sky130-ngspice-bundle.tar.gz")
    deps = Path("/content/sky130-pdk-deps.tar.gz")
    manifest = Path("/content/sky130-ngspice-bundle-manifest.json")
    report = {"result_type": "colab_sky130_continuous_preflight", "bundle_present": bundle.exists(), "dependency_bundle_present": deps.exists(), "manifest_present": manifest.exists()}
    if not bundle.exists() or not manifest.exists():
        report["status"] = "missing_pinned_bundle"
        Path("/content/sky130-preflight.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 2
    # Persist progress before the potentially slow package installation.  A
    # remote notebook timeout can then be distinguished from a missing bundle
    # or a failed circuit run, and a later invocation can resume safely.
    report["status"] = "installing_ngspice"
    Path("/content/sky130-preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    if shutil.which("ngspice") is None:
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        subprocess.run(["apt-get", "install", "-y", "-qq", "ngspice"], check=True)
    root = Path("/content/sky130A")
    (root / "libs.tech").mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle, "r:gz") as archive:
        archive.extractall(root / "libs.tech")
    if deps.exists():
        with tarfile.open(deps, "r:gz") as archive:
            archive.extractall(root)
    pdk_link = Path("/root/eda-tools/pdks/sky130A")
    pdk_link.parent.mkdir(parents=True, exist_ok=True)
    if not pdk_link.exists():
        pdk_link.symlink_to(root)
    library = root / "libs.tech/ngspice/sky130.lib.spice"
    report.update({"ngspice": shutil.which("ngspice"), "sky130_library_present": library.exists(), "status": "ready" if library.exists() else "missing_sky130_library"})
    Path("/content/sky130-preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ready" else 3


if __name__ == "__main__":
    raise SystemExit(main())
