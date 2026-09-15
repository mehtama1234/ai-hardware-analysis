#!/usr/bin/env python3
"""Build the pinned Sky130 and source archives expected by Colab bootstrap."""
from __future__ import annotations

import argparse
import tarfile
from pathlib import Path


def add_dir(archive: tarfile.TarFile, source: Path, arcname: str) -> None:
    if not source.is_dir():
        raise SystemExit(f"missing directory: {source}")
    archive.add(source, arcname=arcname, filter=lambda info: None if info.name.endswith((".pyc", "/__pycache__")) else info)


def require_root(path: Path, prefix: str) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = archive.getnames()
    if not any(name == prefix or name.startswith(prefix + "/") for name in names):
        raise SystemExit(f"archive root check failed for {path.name}: expected {prefix}/")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdk-root", type=Path, required=True, help="sky130A directory")
    parser.add_argument("--source-root", type=Path, required=True, help="ai-hardware-analysis directory")
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    pdk = args.pdk_root.resolve()
    source = args.source_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out / "sky130-ngspice-bundle.tar.gz", "w:gz") as archive:
        add_dir(archive, pdk / "libs.tech/ngspice", "ngspice")
    with tarfile.open(out / "sky130-pdk-deps.tar.gz", "w:gz") as archive:
        add_dir(archive, pdk / "libs.ref/sky130_fd_pr/spice", "libs.ref/sky130_fd_pr/spice")
    with tarfile.open(out / "ai-hardware-analysis.tgz", "w:gz") as archive:
        add_dir(archive, source / "analog-digital-chip-design-eda/scripts", "ai-hardware-analysis/analog-digital-chip-design-eda/scripts")
        add_dir(archive, source / "analog-digital-chip-design-eda/colab", "ai-hardware-analysis/analog-digital-chip-design-eda/colab")
    require_root(out / "sky130-ngspice-bundle.tar.gz", "ngspice")
    require_root(out / "sky130-pdk-deps.tar.gz", "libs.ref/sky130_fd_pr/spice")
    require_root(out / "ai-hardware-analysis.tgz", "ai-hardware-analysis/analog-digital-chip-design-eda")
    print(f"wrote bundles to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
