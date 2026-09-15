#!/usr/bin/env python3
"""Preflight the exact FS/FF Colab campaign deck configuration."""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[3]
    checker = repo / "analog-digital-chip-design-eda/scripts/check_continuous_deck_contract.py"
    cases = {}
    for corner in ("fs", "ff"):
        env = os.environ.copy()
        env.update({"AIMC_SKY130_CORNER": corner, "AIMC_CONTINUOUS_PWL_RISE_NS": "0.2", "PYTHONPATH": str(checker.parent)})
        proc = subprocess.run(["python3", str(checker)], cwd=repo, env=env, capture_output=True, text=True, check=False)
        try:
            report = ast.literal_eval(proc.stdout.strip())
        except (ValueError, SyntaxError):
            report = {"raw_stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
        cases[corner] = {"returncode": proc.returncode, "settings": {"AIMC_SKY130_CORNER": corner, "AIMC_CONTINUOUS_PWL_RISE_NS": 0.2}, "report": report, "pass": all(report.get(k) for k in ("corner_section", "finite_pwl_controls", "no_ideal_time_steps"))}
    result = {"schema_version": "corner-campaign-preflight-v0.1", "result_type": "sky130_corner_campaign_config_check", "cases": cases, "all_pass": all(v["pass"] for v in cases.values()), "claim_boundary": "Static deck configuration only; this does not prove ngspice execution, circuit correctness, yield, or energy."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"all_pass": result["all_pass"], "output": str(args.output)}, indent=2))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
