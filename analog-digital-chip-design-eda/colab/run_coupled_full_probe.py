#!/usr/bin/env python3
"""Run all 16 physical DAC/comparator trial codes in Colab."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def main() -> int:
    pdk_link = Path("/root/eda-tools/pdks/sky130A")
    pdk_link.parent.mkdir(parents=True, exist_ok=True)
    if not pdk_link.exists():
        pdk_link.symlink_to("/content/sky130A")
    Path("/evidence/aimc-simulator-adapters").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({"AIMC_COUPLED_CODES": ",".join(str(code) for code in range(16)), "AIMC_COUPLED_TIMEOUT_S": "30", "AIMC_COUPLED_WORKERS": "4", "AIMC_COUPLED_OUTPUT_STEM": "colab-coupled-dac-comparator-full-parallel"})
    proc = subprocess.run(["python", "/content/run_sky130_coupled_dac_comparator_bit.py"], cwd="/content", env=env, capture_output=True, text=True, check=False)
    print(json.dumps({"result_type": "colab_coupled_dac_comparator_full", "returncode": proc.returncode, "status": "runner_completed" if proc.returncode == 0 else "runner_failed", "output_excerpt": (proc.stdout + proc.stderr)[-5000:]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
