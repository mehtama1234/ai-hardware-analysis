#!/usr/bin/env python3
"""Bind canonical RTL verification to the existing local RTL2GDS package.

This gate does not run OpenLane. It proves the important handoff invariant:
the RTL that passes the canonical simulation is byte-for-byte aligned with the
RTL revision named by the existing OpenLane signoff package, then independently
rechecks the physical package.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RTL_DIR = ROOT / "labs/digital/aimc-control-plane-rtl"
PREP_DIR = ROOT / "labs/eda/aimc-multi-clock-control-subsystem-openlane-prep"
SPEC = RTL_DIR / "aimc_multi_clock_control_subsystem_spec.md"
TOP = "aimc_multi_clock_control_subsystem_tb"
MAIN = "aimc_multi_clock_control_subsystem.v"
SOURCE_NAMES = [
    MAIN,
    "aimc_micro_tile_controller.v",
    "aimc_operation_partition.v",
    "aimc_tile_readout.v",
    "aimc_scheduler_governor.v",
    "aimc_tile_service_scheduler.v",
    "aimc_error_budget_governor.v",
]
TB = RTL_DIR / "aimc_multi_clock_control_subsystem_tb.v"
MANIFEST = PREP_DIR / "openlane-vsrc-aligned-manifest.json"
DEFAULT_OUTPUT = ROOT / "evidence/aimc-hardware-lab/verified-rtl2gds-bridge-latest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], cwd: Path, *, timeout: int = 120) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        output = (completed.stdout + completed.stderr).strip()
        return {
            "command": command,
            "returncode": completed.returncode,
            "status": "passed" if completed.returncode == 0 else "failed",
            "output_tail": output[-2000:],
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": None,
            "status": "blocked",
            "output_tail": str(exc),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "status": "blocked",
            "output_tail": f"timeout after {timeout}s: {exc}",
        }


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    missing = [
        str(path.relative_to(ROOT))
        for path in [SPEC, TB, MANIFEST, PREP_DIR / "constraint.sdc"]
        if not path.is_file()
    ]
    if missing:
        raise SystemExit(f"missing bridge inputs: {', '.join(missing)}")

    source_alignment: dict[str, object] = {}
    for name in SOURCE_NAMES:
        canonical = RTL_DIR / name
        physical = PREP_DIR / "src" / name
        if not canonical.is_file() or not physical.is_file():
            source_alignment[name] = {"status": "missing"}
            continue
        canonical_sha = digest(canonical)
        physical_sha = digest(physical)
        source_alignment[name] = {
            "canonical_sha256": canonical_sha,
            "physical_input_sha256": physical_sha,
            "byte_identical": canonical_sha == physical_sha,
            "status": "passed" if canonical_sha == physical_sha else "failed",
        }

    with tempfile.TemporaryDirectory(prefix="aimc-verified-rtl2gds-") as temp:
        binary = Path(temp) / "aimc_multi_clock_control_subsystem.vvp"
        compile_run = run(
            [
                "iverilog",
                "-g2012",
                "-s",
                TOP,
                "-o",
                str(binary),
                *[str(RTL_DIR / name) for name in SOURCE_NAMES],
                str(TB),
            ],
            ROOT,
        )
        simulation_run = (
            run(["vvp", str(binary)], ROOT)
            if compile_run["status"] == "passed"
            else {"status": "blocked", "reason": "compilation did not pass"}
        )
        simulation_output = str(simulation_run.get("output_tail", ""))
        simulation_run["pass_marker_present"] = "PASS aimc_multi_clock_control_subsystem_tb" in simulation_output
        simulation_run["fail_marker_absent"] = "FAIL " not in simulation_output

    signoff_run = run(
        [
            sys.executable,
            "scripts/check_aimc_multiclock_signoff.py",
            str(PREP_DIR),
            "openlane-vsrc-aligned-manifest.json",
        ],
        ROOT,
    )

    alignment_passed = bool(source_alignment) and all(
        item.get("byte_identical") is True for item in source_alignment.values() if isinstance(item, dict)
    ) and len(source_alignment) == len(SOURCE_NAMES)
    simulation_passed = (
        compile_run.get("status") == "passed"
        and simulation_run.get("status") == "passed"
        and simulation_run.get("pass_marker_present") is True
        and simulation_run.get("fail_marker_absent") is True
    )
    report = {
        "schema_version": "verified-rtl2gds-bridge-v1",
        "status": "passed" if alignment_passed and simulation_passed and signoff_run.get("status") == "passed" else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design": "aimc_multi_clock_control_subsystem",
        "requirements": {"path": str(SPEC.relative_to(ROOT)), "sha256": digest(SPEC)},
        "canonical_testbench": {"path": str(TB.relative_to(ROOT)), "sha256": digest(TB)},
        "source_alignment": source_alignment,
        "simulation": {"compile": compile_run, "run": simulation_run},
        "physical_signoff": {
            "package": str(PREP_DIR.relative_to(ROOT)),
            "manifest": MANIFEST.name,
            "manifest_sha256": digest(MANIFEST),
            "checker": signoff_run,
        },
        "claim_boundary": (
            "This gate joins canonical local RTL simulation to an existing aligned OpenLane signoff package. "
            "It is not commercial Innovus/ICC2/PrimeTime signoff, foundry tapeout, analog qualification, "
            "board measurement, or silicon evidence."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "alignment_passed": alignment_passed, "simulation_passed": simulation_passed, "physical_signoff": signoff_run.get("status")}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

