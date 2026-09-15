#!/usr/bin/env python3
"""Create a hash manifest for the minimal Sky130 ngspice model bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def main() -> int:
    root = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice"
    out = Path("sky130-ngspice-bundle-manifest.json")
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(root)), "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {"result_type": "sky130_ngspice_bundle_manifest", "root": str(root), "file_count": len(files), "files": files, "top_level_library": "sky130.lib.spice"}
    report["bundle_sha256"] = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"files,{len(files)}")
    print(f"bundle_sha256,{report['bundle_sha256']}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
