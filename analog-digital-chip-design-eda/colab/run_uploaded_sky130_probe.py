#!/usr/bin/env python3
"""Unpack uploaded Sky130 bundle and execute the portable runtime probe."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tarfile
from pathlib import Path


def main() -> int:
    bundle = Path("/content/sky130-ngspice-bundle.tar.gz")
    manifest = Path("/content/sky130-ngspice-bundle-manifest.json")
    root = Path("/content/sky130A/libs.tech")
    root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle, "r:gz") as archive:
        archive.extractall(root)
    dependency_bundle = Path("/content/sky130-pdk-deps.tar.gz")
    if dependency_bundle.exists():
        with tarfile.open(dependency_bundle, "r:gz") as archive:
            archive.extractall(Path("/content/sky130A"))
    expected = json.loads(manifest.read_text())
    files = []
    for path in sorted((root / "ngspice").rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(root / "ngspice")), "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    actual_bundle_hash = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    report = {"result_type": "colab_uploaded_sky130_probe", "bundle_hash_matches": actual_bundle_hash == expected.get("bundle_sha256"), "dependency_bundle_present": dependency_bundle.exists(), "actual_bundle_sha256": actual_bundle_hash, "expected_bundle_sha256": expected.get("bundle_sha256")}
    if report["bundle_hash_matches"]:
        probe = subprocess.run(["python", "/content/sky130_runtime_probe.py", "--sky130-lib", "/content/sky130A/libs.tech/ngspice/sky130.lib.spice", "--timeout-s", "60", "--output", "/content/sky130-runtime-probe.json"], capture_output=True, text=True, check=False)
        report["probe_returncode"] = probe.returncode
        report["probe_output"] = probe.stdout[-4000:]
        report["status"] = "probe_completed"
    else:
        report["status"] = "bundle_hash_mismatch"
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
