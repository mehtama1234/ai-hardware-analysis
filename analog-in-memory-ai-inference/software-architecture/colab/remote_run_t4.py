#!/usr/bin/env python3
"""Remote script executed by the authenticated Colab CLI T4 handoff."""

from __future__ import annotations

import json
import subprocess
import sys
import tarfile
from pathlib import Path


ROOT = Path("/content/ai-hardware-analysis")
SOFTWARE = ROOT / "analog-in-memory-ai-inference/software-architecture"
OUTPUT = Path("/content/gpt2-sar-t4")


def run(command: list[str], cwd: Path) -> None:
    print("$ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout[-12000:], flush=True)
    if result.stderr:
        print(result.stderr[-12000:], file=sys.stderr, flush=True)
    if result.returncode:
        raise SystemExit(f"command failed with return code {result.returncode}: {command[0]}")


def main() -> None:
    archive = Path("/content/ai-hardware-analysis.tgz")
    if not archive.exists():
        raise SystemExit(f"missing uploaded archive: {archive}")
    with tarfile.open(archive, "r:gz") as bundle:
        bundle.extractall(Path("/content"))
    if not (ROOT / "analog-in-memory-ai-inference").exists():
        raise SystemExit(f"missing unpacked repository: {ROOT}")
    run([sys.executable, "-m", "pip", "install", "-q", "torch", "transformers", "huggingface_hub"], SOFTWARE)
    run([sys.executable, str(SOFTWARE / "colab/run_profile_driven_gpt2_colab.py"),
         "--repo-root", str(ROOT), "--output", str(OUTPUT), "--fetch-model",
         "--execute-model", "--device", "cuda"], ROOT)
    run([sys.executable, str(SOFTWARE / "scripts/check_gpt2_hybrid_evaluation.py"),
         "--package", str(OUTPUT / "model-evaluation")], ROOT)
    receipt = json.loads((OUTPUT / "colab-receipt.json").read_text())
    print(json.dumps({"status": "passed", "device": receipt.get("environment", {}).get("device"),
                      "receipt": str(OUTPUT / "colab-receipt.json")}), flush=True)


if __name__ == "__main__":
    main()
