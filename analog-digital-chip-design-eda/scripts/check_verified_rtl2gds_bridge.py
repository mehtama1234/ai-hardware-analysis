#!/usr/bin/env python3
"""Independently verify the canonical verification-to-RTL2GDS bridge report."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "evidence/aimc-hardware-lab/verified-rtl2gds-bridge-latest.json"
RTL_DIR = ROOT / "labs/digital/aimc-control-plane-rtl"
PREP_DIR = ROOT / "labs/eda/aimc-multi-clock-control-subsystem-openlane-prep"
SOURCE_NAMES = [
    "aimc_multi_clock_control_subsystem.v",
    "aimc_micro_tile_controller.v",
    "aimc_operation_partition.v",
    "aimc_tile_readout.v",
    "aimc_scheduler_governor.v",
    "aimc_tile_service_scheduler.v",
    "aimc_error_budget_governor.v",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    report_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REPORT
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema_version") == "verified-rtl2gds-bridge-v1", "unsupported bridge schema")
    require(report.get("status") == "passed", "bridge report is not passed")
    require(report.get("design") == "aimc_multi_clock_control_subsystem", "unexpected design")

    requirements = ROOT / report["requirements"]["path"]
    testbench = ROOT / report["canonical_testbench"]["path"]
    require(requirements.is_file() and digest(requirements) == report["requirements"]["sha256"], "requirements hash mismatch")
    require(testbench.is_file() and digest(testbench) == report["canonical_testbench"]["sha256"], "testbench hash mismatch")

    alignment = report.get("source_alignment", {})
    require(set(alignment) == set(SOURCE_NAMES), "source alignment set is incomplete")
    for name in SOURCE_NAMES:
        canonical = RTL_DIR / name
        physical = PREP_DIR / "src" / name
        record = alignment[name]
        require(canonical.is_file() and physical.is_file(), f"missing aligned source: {name}")
        require(record.get("status") == "passed", f"source alignment did not pass: {name}")
        require(record.get("canonical_sha256") == digest(canonical), f"canonical source hash mismatch: {name}")
        require(record.get("physical_input_sha256") == digest(physical), f"physical source hash mismatch: {name}")
        require(record.get("byte_identical") is True, f"source is not byte-identical: {name}")

    simulation = report.get("simulation", {})
    compile_run = simulation.get("compile", {})
    sim_run = simulation.get("run", {})
    require(compile_run.get("status") == "passed" and compile_run.get("returncode") == 0, "RTL compilation did not pass")
    require(sim_run.get("status") == "passed" and sim_run.get("returncode") == 0, "RTL simulation did not pass")
    require(sim_run.get("pass_marker_present") is True, "simulation pass marker is missing")
    require(sim_run.get("fail_marker_absent") is True, "simulation contains a failure marker")

    physical = report.get("physical_signoff", {})
    manifest = PREP_DIR / str(physical.get("manifest", ""))
    require(manifest.is_file(), "physical manifest is missing")
    require(digest(manifest) == physical.get("manifest_sha256"), "physical manifest hash mismatch")
    checker = subprocess.run(
        [sys.executable, "scripts/check_aimc_multiclock_signoff.py", str(PREP_DIR), manifest.name],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(checker.returncode == 0, "independent physical signoff recheck failed")
    require(physical.get("checker", {}).get("status") == "passed", "bridge physical check was not passed")

    print(json.dumps({"status": "passed", "report": str(report_path), "sources": len(SOURCE_NAMES), "physical_recheck": "passed"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)

