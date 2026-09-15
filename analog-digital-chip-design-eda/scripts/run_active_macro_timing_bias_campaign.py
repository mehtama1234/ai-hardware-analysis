#!/usr/bin/env python3
"""Run a reproducible extracted active-macro bias/evaluation timing campaign."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "evidence/aimc-simulator-adapters/switched-reference-dac/20260909-full-v1/run_active_converter_macro_extracted_transient.py"
DEFAULT_CANDIDATE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/routing-repair-20260913T160000Z"
DEFAULT_OUTPUT = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-timing-bias-campaign-20260913.json"


def run(candidate: Path, bias: float, eval_ns: float) -> dict[str, object]:
    env = {**os.environ, "AIMC_ISO_TAIL_BIAS_A": str(bias), "PYTHONPATH": str(ROOT / "scripts")}
    command = ["python3", str(RUNNER), "--candidate-dir", str(candidate), "--view", "extracted",
               "--timeout-seconds", "30", "--input-diffs-mv", "-50", "50"]
    env["AIMC_EVAL_START_NS"] = str(eval_ns)
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False, timeout=90)
    match = re.search(r'"output":\s*"([^"]+result\.json)"', proc.stdout)
    result = json.loads(Path(match.group(1)).read_text()) if match else None
    rows = result.get("rows", []) if isinstance(result, dict) else []
    return {
        "bias_a": bias,
        "eval_start_ns": eval_ns,
        "returncode": proc.returncode,
        "result_path": match.group(1) if match else None,
        "measured_case_count": len([r for r in rows if r.get("measured")]),
        "polarity_pass_count": len([r for r in rows if r.get("polarity_pass")]),
        "logic_margin_pass_count": len([r for r in rows if r.get("logic_margin_pass")]),
        "decision_diff_v": [r.get("decision_diff_v") for r in rows],
        "runner_stdout_tail": proc.stdout[-1000:],
        "runner_stderr_tail": proc.stderr[-1000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cases = [run(args.candidate.resolve(), 20e-6, value) for value in (8.2, 10.0, 12.0, 14.0)]
    report = {
        "result_type": "active_macro_timing_bias_campaign",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate": str(args.candidate.resolve()),
        "runner": str(RUNNER),
        "bias_a": 20e-6,
        "input_diffs_mv": [-50.0, 50.0],
        "cases": cases,
        "status": "timing_bias_campaign_passed_bounded_nominal" if all(c["polarity_pass_count"] == 2 and c["logic_margin_pass_count"] == 2 for c in cases[2:]) else "timing_bias_campaign_open",
        "accepted_converter": False,
        "claim_boundary": "Shows a bounded nominal timing/bias operating point for the extracted active macro; does not prove full converter, noise, mismatch, PVT, LVS, or silicon qualification.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(args.output), "cases": len(cases)}, indent=2))
    return 0 if report["status"] == "timing_bias_campaign_passed_bounded_nominal" else 1


if __name__ == "__main__":
    raise SystemExit(main())
