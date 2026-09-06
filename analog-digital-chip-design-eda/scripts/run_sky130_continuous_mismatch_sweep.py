#!/usr/bin/env python3
"""Run a seeded capacitor-mismatch sweep through the complete continuous SAR.

This is intentionally a wrapper around the physical continuous-SAR runner.  It
does not replace device-level Monte Carlo: it tests the closed-loop code map
under a declared, reproducible capacitor-ratio perturbation model.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
RUNNER = ROOT / "scripts" / "run_sky130_continuous_physical_sar.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=130)
    parser.add_argument("--sigma-percent", type=float, default=1.0)
    parser.add_argument("--timeout-s", type=float, default=1200.0)
    parser.add_argument("--output-stem", default="sky130-continuous-physical-sar-mismatch")
    return parser.parse_args()


BASE_CAP_SCALES = (1.0, 0.75, 1.0, 1.0)


def trial_scales(rng: random.Random, sigma_percent: float) -> list[float]:
    sigma = sigma_percent / 100.0
    # The promoted candidate is not an all-ones capacitor bank: bit 1 uses a
    # measured 0.75x trim, while the LSB correction is applied separately by
    # AIMC_COUPLED_LSB_SCALE.  Variation must be applied around that actual
    # operating point or the sweep would test a different circuit.
    return [max(0.5, base * (1.0 + rng.gauss(0.0, sigma))) for base in BASE_CAP_SCALES]


def run_trial(index: int, scales: list[float], timeout_s: float, output_stem: str) -> dict[str, Any]:
    env = dict(os.environ)
    env.update(
        {
            "AIMC_CONTINUOUS_CONVERSION_COUNT": "5",
            "AIMC_CONTINUOUS_OUTPUT_STEM": f"{output_stem}-trial-{index:03d}",
            "AIMC_COUPLED_TIMEOUT_S": str(timeout_s),
            "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "1",
        }
    )
    for bit, scale in enumerate(scales):
        env[f"AIMC_COUPLED_BIT{bit}_CAP_SCALE"] = f"{scale:.10f}"
    env.setdefault("AIMC_COUPLED_LSB_SCALE", "1.5")
    env.setdefault("AIMC_CONTINUOUS_NMOS_WIDTH", "64")
    env.setdefault("AIMC_CONTINUOUS_PMOS_BANK", "8")
    try:
        completed = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s + 30.0,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "trial": index,
            "scales": scales,
            "status": "runner_timeout",
            "all_conversions_correct": False,
            "bottom_plate_in_legal_range": False,
        }
    artifact = EVIDENCE / f"{output_stem}-trial-{index:03d}.json"
    row: dict[str, Any] = {"trial": index, "scales": scales, "returncode": completed.returncode}
    if artifact.exists():
        data = json.loads(artifact.read_text(encoding="utf-8"))
        row.update(
            {
                "status": data.get("status"),
                "all_conversions_correct": data.get("all_conversions_correct", False),
                "bottom_plate_in_legal_range": data.get("bottom_plate_in_legal_range", False),
                "conversion_count": data.get("conversion_count", 0),
                "conversion_codes": [item.get("final_code") for item in data.get("conversions", [])],
                "expected_codes": [item.get("expected_code") for item in data.get("conversions", [])],
                "artifact": str(artifact.relative_to(ROOT)),
            }
        )
    else:
        row.update(
            {
                "status": "missing_trial_artifact",
                "all_conversions_correct": False,
                "bottom_plate_in_legal_range": False,
                "error_excerpt": (completed.stdout + completed.stderr)[-1000:],
            }
        )
    return row


def write_outputs(report: dict[str, Any], stem: str) -> None:
    json_path = EVIDENCE / f"{stem}.json"
    md_path = EVIDENCE / f"{stem}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = report["rows"]
    lines = [
        "# Sky130 Continuous Physical SAR Mismatch Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- trials: `{report['measured_trial_count']}/{report['trial_count']}`",
        f"- seed: `{report['seed']}`",
        f"- capacitor mismatch model: independent Gaussian perturbations around base scales `{report['base_cap_scales']}`, sigma `{report['sigma_percent']}%`",
        f"- full five-conversion code-map passes: `{report['full_map_pass_count']}/{report['trial_count']}`",
        f"- legal bottom-plate passes: `{report['legal_bottom_pass_count']}/{report['trial_count']}`",
        "",
        "## Purpose",
        "",
        "Each trial runs the same continuous four-bit, five-conversion physical SAR transient used by the nominal candidate. Only the four binary DAC capacitor scales are perturbed. The seed and sigma are recorded so the exact trial population can be replayed.",
        "",
        "## Trial Summary",
        "",
        "| trial | scales | status | code map | map pass | bottom legal |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        scales = ", ".join(f"{value:.5f}" for value in row["scales"])
        codes = ", ".join(str(value) for value in row.get("conversion_codes", [])) or "not measured"
        lines.append(
            f"| {row['trial']} | {scales} | {row.get('status')} | {codes} | {row.get('all_conversions_correct', False)} | {row.get('bottom_plate_in_legal_range', False)} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "A full-map pass means all five representative conversions produced their expected retained code and the reported bottom-plate values stayed within the declared supply range. This is stronger than an isolated DAC mismatch sweep because the perturbed values pass through the actual decision-dependent continuous controller.",
        "",
        "## Claim Boundary",
        "",
        "This is a reproducible capacitor-variation stress model, not foundry Monte Carlo. It does not prove random device mismatch, comparator offset/noise yield, extracted-layout behavior, DRC/LVS signoff, board behavior, or silicon acceptance.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.trials < 1:
        raise SystemExit("--trials must be positive")
    if args.sigma_percent < 0:
        raise SystemExit("--sigma-percent must be non-negative")
    rng = random.Random(args.seed)
    rows = []
    for index in range(args.trials):
        scales = trial_scales(rng, args.sigma_percent)
        row = run_trial(index, scales, args.timeout_s, args.output_stem)
        rows.append(row)
        print(
            f"trial,{index},status,{row.get('status')},map,{row.get('all_conversions_correct', False)},legal,{row.get('bottom_plate_in_legal_range', False)}",
            flush=True,
        )
    measured = [row for row in rows if row.get("conversion_count") == 5]
    full_map_pass = [row for row in rows if row.get("all_conversions_correct") and row.get("bottom_plate_in_legal_range")]
    report = {
        "result_type": "sky130_continuous_physical_sar_mismatch_sweep",
        "status": "continuous_sar_mismatch_stress_measured_not_foundry_yield_proof",
        "seed": args.seed,
        "sigma_percent": args.sigma_percent,
        "base_cap_scales": list(BASE_CAP_SCALES),
        "trial_count": args.trials,
        "measured_trial_count": len(measured),
        "full_map_pass_count": len(full_map_pass),
        "legal_bottom_pass_count": sum(row.get("bottom_plate_in_legal_range", False) for row in rows),
        "rows": rows,
        "claim_boundary": "seeded capacitor variation through the complete five-conversion continuous SAR; not foundry Monte Carlo, comparator noise/offset yield, extracted-layout, board, or silicon acceptance",
    }
    write_outputs(report, args.output_stem)
    print(f"status,{report['status']}")
    print(f"full_map_pass,{report['full_map_pass_count']}/{report['trial_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
