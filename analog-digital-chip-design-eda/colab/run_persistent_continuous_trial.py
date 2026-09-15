#!/usr/bin/env python3
"""Run one continuous-SAR trial and persist a download-safe result envelope.

Colab kernels can disappear after a subprocess finishes.  This entrypoint
therefore writes a small result JSON to ``/content`` regardless of whether
the circuit runner produced its normal evidence artifact.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    root = Path("/content")
    evidence = root / "evidence" / "aimc-simulator-adapters"
    evidence.mkdir(parents=True, exist_ok=True)
    runner = root / "ai-hardware-analysis" / "analog-digital-chip-design-eda" / "scripts" / "run_sky130_continuous_physical_sar.py"
    if not runner.exists():
        runner = root / "scripts" / "run_sky130_continuous_physical_sar.py"
    if not runner.exists():
        runner = root / "run_sky130_continuous_physical_sar.py"
    output_stem = os.environ.get("AIMC_CONTINUOUS_OUTPUT_STEM", "colab-persistent-continuous-trial")
    envelope = root / f"{output_stem}-envelope.json"
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(root / "scripts"))
    try:
        completed = subprocess.run(
            ["python", str(runner)], cwd=root, env=env,
            capture_output=True, text=True, check=False,
        )
        result = {
            "result_type": "colab_persistent_continuous_trial",
            "runner": str(runner),
            "runner_returncode": completed.returncode,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-12000:],
        }
    except Exception as exc:  # pragma: no cover - defensive remote envelope
        result = {"result_type": "colab_persistent_continuous_trial", "runner": str(runner), "error": repr(exc)}
    # When this entrypoint is run from an extracted repository, the circuit
    # runner writes beside that repository. Keep the legacy /content location
    # as a fallback for older bundles.
    repo_evidence = root / "ai-hardware-analysis" / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters"
    repo_evidence.mkdir(parents=True, exist_ok=True)
    child = repo_evidence / f"{output_stem}.json"
    if not child.exists():
        child = evidence / f"{output_stem}.json"
    if child.exists():
        result["child_artifact"] = str(child)
        try:
            result["child_report"] = json.loads(child.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result["child_report_error"] = str(exc)
    envelope.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(envelope, root / "colab-latest-result.json")
    print(json.dumps({"envelope": str(envelope), "runner_returncode": result.get("runner_returncode")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
