#!/usr/bin/env python3
"""Run the exhaustive AIMC scheduler/governor policy property suite."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / "labs/digital/aimc-control-plane-rtl"
PROPERTIES = RTL / "aimc_formal_properties.sv"
SOURCES = [RTL / name for name in ("aimc_tile_service_scheduler.v", "aimc_error_budget_governor.v")]
CASES = (("aimc_scheduler_no_sample", 1), ("aimc_scheduler_no_candidate", 1), ("aimc_scheduler_nominal", 1), ("aimc_governor_no_sample", 1), ("aimc_governor_high_residual", 1), ("aimc_governor_nominal", 1))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    results = []
    logs = []
    for top, sequence in CASES:
        command = ["yosys", "-p", f"read_verilog -formal -sv {' '.join(str(path) for path in SOURCES)} {PROPERTIES}; prep -top {top}; flatten; select -module {top}; sat -seq {sequence} -prove-asserts"]
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        log = run.stdout + run.stderr; logs.append(f"=== {top} ===\n{log}")
        results.append({"property": top, "sequence": sequence, "returncode": run.returncode, "passed": run.returncode == 0 and "SAT proof finished - no model found: SUCCESS!" in log})
    (output / "yosys.log").write_text("\n".join(logs), encoding="utf-8")
    (output / "property-proofs.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    passed = all(item["passed"] for item in results)
    report = {"schema_version": "aimc-formal-property-suite-v1", "status": "passed" if passed else "failed", "generated_at": datetime.now(timezone.utc).isoformat(), "scope": "Scheduler and error-budget governor policy boundary; not full multi-clock subsystem closure.", "sources": [{"path": str(path), "sha256": digest(path)} for path in [*SOURCES, PROPERTIES]], "proof": {"tool": "yosys-sat", "property_count": len(results), "property_runs": results, "result": "proven" if passed else "unknown", "log": str(output / "yosys.log")}, "claim_boundary": "Local exhaustive combinational policy properties only; not commercial EDA signoff, analog measurement, or silicon evidence."}
    (output / "formal-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "property_count": len(results), "output": str(output)}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
