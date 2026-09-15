#!/usr/bin/env python3
"""Reproduce the bounded local model-to-workload qualification handoff."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
SOFTWARE = PRODUCT_ROOT / "analog-in-memory-ai-inference/software-architecture"
GPT2 = SOFTWARE / "experiments/gpt2-hybrid-v1"
SCRIPTS = SOFTWARE / "scripts"
DEFAULT_EVALUATION = GPT2 / "runs/20260912-local-profile-replay-tensors-v4/evaluation.json"
DEFAULT_TENSORS = GPT2 / "runs/20260912-local-profile-replay-tensors-v4/projection_tensors.npz"
DEFAULT_CALIBRATION = GPT2 / "runs/20260911-local-affine-calibrated-adc12/calibration_report.json"
DEFAULT_CALIBRATED_TENSORS = GPT2 / "runs/20260911-local-affine-calibrated-adc12/projection_tensors.npz"
DEFAULT_GENERALIZATION = GPT2 / "qualification/calibration-generalization-comparison.json"
DEFAULT_OUTPUT = GPT2 / "qualification/local-profile-to-workload-qualification"


def run(command: list[str], cwd: Path) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, default=DEFAULT_EVALUATION)
    parser.add_argument("--tensor-artifact", type=Path, default=DEFAULT_TENSORS)
    parser.add_argument("--calibration-report", type=Path, default=DEFAULT_CALIBRATION)
    parser.add_argument("--calibrated-tensor-artifact", type=Path, default=DEFAULT_CALIBRATED_TENSORS)
    parser.add_argument("--calibration-generalization", type=Path, default=DEFAULT_GENERALIZATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = args.output.resolve()
    run([
        sys.executable, str(SCRIPTS / "run_local_profile_to_workload_qualification.py"),
        "--evaluation", str(args.evaluation.resolve()),
        "--tensor-artifact", str(args.tensor_artifact.resolve()),
        "--calibration-report", str(args.calibration_report.resolve()),
        "--calibrated-tensor-artifact", str(args.calibrated_tensor_artifact.resolve()),
        "--calibration-generalization", str(args.calibration_generalization.resolve()),
        "--output", str(output),
    ], SOFTWARE)
    run([sys.executable, str(SCRIPTS / "build_local_qualification_decision.py"), str(output)], SOFTWARE)
    run([sys.executable, str(SCRIPTS / "check_local_profile_to_workload_qualification.py"), str(output)], SOFTWARE)
    run([
        sys.executable, str(SCRIPTS / "check_gpt2_hybrid_evaluation.py"),
        "--package", str(args.evaluation.resolve().parent),
    ], SOFTWARE)
    run([sys.executable, str(PRODUCT_ROOT / "scripts/build_end_to_end_qualification_manifest.py")], PRODUCT_ROOT)
    run([sys.executable, str(PRODUCT_ROOT / "scripts/validate_end_to_end_handoff.py")], PRODUCT_ROOT)
    run([sys.executable, str(PRODUCT_ROOT / "scripts/check_local_digital_qualification_package.py"),
         str(PRODUCT_ROOT / "evidence/local-digital-qualification-v1")], PRODUCT_ROOT)
    run([sys.executable, str(PRODUCT_ROOT / "scripts/check_counterfactual_hybrid_advantage_report.py"),
         str(PRODUCT_ROOT / "evidence/counterfactual-hybrid-advantage-v2")], PRODUCT_ROOT)
    print("LOCAL END-TO-END QUALIFICATION OK: bounded package and product handoff validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
