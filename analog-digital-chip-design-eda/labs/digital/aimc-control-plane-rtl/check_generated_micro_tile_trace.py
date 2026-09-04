#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
LABS_ROOT = HERE.parents[1]
GENERATOR = LABS_ROOT / "analog" / "analog-in-memory-foundation-model-hardware" / "python" / "generate_micro_tile_rtl_vectors.py"
CSV_PATH = LABS_ROOT / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements" / "generated-micro-tile-rtl-vectors.csv"

SIM_FIELDS = [
    "path",
    "reason",
    "last_fallback_tile",
    "fallback_count",
    "accepted_count",
    "residual_fallback_count",
    "stale_fallback_count",
    "tile_health_action",
]

EXPECTED_FROM_CSV = {
    "path": "expected_path",
    "reason": "expected_reason",
    "last_fallback_tile": "last_fallback_tile_id",
    "fallback_count": "fallback_count",
    "accepted_count": "accepted_count",
    "residual_fallback_count": "residual_fallback_count",
    "stale_fallback_count": "stale_fallback_count",
    "tile_health_action": "tile_health_action",
}

ALLOWED_EXTRA_PREFIXES = (
    "maintenance_",
    "post_probe_",
)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def parse_simulation(stdout: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for raw in stdout.splitlines():
        if "," not in raw or raw.startswith("VCD info"):
            continue
        name, rest = raw.split(",", 1)
        values = dict(re.findall(r"([a-z_]+)=(-?[0-9]+)", rest))
        if all(field in values for field in SIM_FIELDS):
            rows[name] = values
    return rows


def load_expected() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
            "aimc_micro_tile_controller_tb",
            "aimc_operation_partition.v",
            "aimc_tile_readout.v",
            "aimc_micro_tile_controller.v",
            "aimc_micro_tile_controller_tb.v",
        ],
        HERE,
    )
    if compiled.returncode != 0:
        sys.stderr.write(compiled.stdout)
        sys.stderr.write(compiled.stderr)
        return compiled.returncode

    simulated = run(["vvp", "aimc_micro_tile_controller_tb"], HERE)
    if simulated.returncode != 0:
        sys.stderr.write(simulated.stdout)
        sys.stderr.write(simulated.stderr)
        return simulated.returncode

    actual = parse_simulation(simulated.stdout)
    expected = load_expected()
    failures: list[str] = []
    for row in expected:
        name = row["name"]
        if name not in actual:
            failures.append(f"{name}: missing from simulation output")
            continue
        for sim_field, csv_field in EXPECTED_FROM_CSV.items():
            if actual[name][sim_field] != row[csv_field]:
                failures.append(f"{name}: {sim_field} actual={actual[name][sim_field]} expected={row[csv_field]}")

    extra = sorted(
        name
        for name in set(actual) - {row["name"] for row in expected}
        if not name.startswith(ALLOWED_EXTRA_PREFIXES)
    )
    failures.extend(f"{name}: extra simulation row" for name in extra)

    if failures:
        print("FAIL generated_micro_tile_trace")
        for failure in failures:
            print(failure)
        return 1

    print("PASS generated_micro_tile_trace")
    print(f"cases {len(expected)}")
    print(f"csv {CSV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
