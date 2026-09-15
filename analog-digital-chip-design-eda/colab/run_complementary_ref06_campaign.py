#!/usr/bin/env python3
"""Unpack the pinned one-shot input and run the complementary ref06 campaign."""
from __future__ import annotations

import shutil
import subprocess
import tarfile
from pathlib import Path


CONTENT = Path("/content")
INPUT = CONTENT / "aimc-complementary-ref06-input.tgz"
STAGE = CONTENT / "aimc-ref06-stage"


def main() -> int:
    STAGE.mkdir(exist_ok=True)
    with tarfile.open(INPUT, "r:gz") as bundle:
        bundle.extractall(STAGE)
    code = next(STAGE.glob("ai-hardware-analysis-complementary-swap-ref06-code*.tgz"))
    with tarfile.open(code, "r:gz") as bundle:
        bundle.extractall(CONTENT)
    source_root = STAGE / "analog-digital-chip-design-eda"
    shutil.copy2(source_root / ".artifacts/colab-sky130-bundle/sky130-ngspice-bundle.tar.gz", CONTENT / "sky130-ngspice-bundle.tar.gz")
    shutil.copy2(source_root / ".artifacts/colab-sky130-bundle/sky130-pdk-deps.tar.gz", CONTENT / "sky130-pdk-deps.tar.gz")
    shutil.copy2(source_root / ".artifacts/colab-sky130-bundle/sky130-ngspice-bundle-manifest.json", CONTENT / "sky130-ngspice-bundle-manifest.json")
    shutil.copy2(source_root / "colab/sky130-fixed-open-loop-complementary-swap-ref06-settings.json", CONTENT / "sky130-campaign-settings.json")
    runner = CONTENT / "ai-hardware-analysis/analog-digital-chip-design-eda/colab/run_corner_campaign.py"
    result = subprocess.run(["python3", str(runner)], cwd=CONTENT / "ai-hardware-analysis", text=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
