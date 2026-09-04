#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
LABS_ROOT = HERE.parents[1]
GENERATOR = LABS_ROOT / "analog" / "analog-in-memory-foundation-model-hardware" / "python" / "integrated_scheduler_governor_runtime.py"
CSV_PATH = LABS_ROOT / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements" / "integrated-scheduler-governor-runtime.csv"

SIM_FIELDS = [
    "tile_actions",
    "busy",
    "residual",
    "drift",
    "sensitivity",
    "cumulative",
    "decision",
    "selected_tile",
    "reason",
    "next",
]

EXPECTED_FROM_CSV = {
    "tile_actions": "tile_actions",
    "busy": "tile_busy",
    "residual": "residual_q8",
    "drift": "drift_age",
    "sensitivity": "sensitivity_q8",
    "cumulative": "cumulative_error_q8",
    "decision": "final_decision",
    "selected_tile": "selected_tile",
    "reason": "final_reason_code",
    "next": "next_cumulative_error_q8",
}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def parse_simulation(stdout: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for raw in stdout.splitlines():
        if "," not in raw:
            continue
        name, rest = raw.split(",", 1)
        values = dict(re.findall(r"([a-z_]+)=([0-9]+)", rest))
        if all(field in values for field in SIM_FIELDS):
            rows[name] = values
    return rows


def load_expected() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def expected_name(row: dict[str, str]) -> str:
    return f"token_{int(row['token']):02d}_{row['final_reason']}"


def main() -> int:
    generated = run(["python3", str(GENERATOR)], HERE)
    if generated.returncode != 0:
        sys.stderr.write(generated.stdout)
        sys.stderr.write(generated.stderr)
        return generated.returncode

    compiled = run(
        [
            "iverilog",
            "-o",
            "aimc_scheduler_governor_tb",
            "aimc_tile_service_scheduler.v",
            "aimc_error_budget_governor.v",
            "aimc_scheduler_governor.v",
            "aimc_scheduler_governor_tb.v",
        ],
        HERE,
    )
    if compiled.returncode != 0:
        sys.stderr.write(compiled.stdout)
        sys.stderr.write(compiled.stderr)
        return compiled.returncode

    simulated = run(["vvp", "aimc_scheduler_governor_tb"], HERE)
    if simulated.returncode != 0:
        sys.stderr.write(simulated.stdout)
        sys.stderr.write(simulated.stderr)
        return simulated.returncode

    actual = parse_simulation(simulated.stdout)
    expected = load_expected()
    failures: list[str] = []
    expected_names = {expected_name(row) for row in expected}

    for row in expected:
        name = expected_name(row)
        if name not in actual:
            failures.append(f"{name}: missing from simulation output")
            continue
        for sim_field, csv_field in EXPECTED_FROM_CSV.items():
            if actual[name][sim_field] != row[csv_field]:
                failures.append(f"{name}: {sim_field} actual={actual[name][sim_field]} expected={row[csv_field]}")

    extra = sorted(set(actual) - expected_names)
    failures.extend(f"{name}: extra simulation row" for name in extra)

    if failures:
        print("FAIL generated_integrated_scheduler_governor_trace")
        for failure in failures:
            print(failure)
        return 1

    print("PASS generated_integrated_scheduler_governor_trace")
    print(f"cases {len(expected)}")
    print(f"csv {CSV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
