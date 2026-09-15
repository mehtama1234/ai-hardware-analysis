#!/usr/bin/env python3
"""Run the specification-model proof for the repaired seeded counter."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "benchmarks/seeded_counter/formal_model_check.sv"
PROPERTIES = ROOT / "benchmarks/seeded_counter/formal_properties.sv"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repaired-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.repaired_source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    log = output / "yosys.log"
    command = ["yosys", "-p", f"read_verilog -formal -sv {source} {FORMAL}; prep -top formal_model_check; flatten; select -module formal_model_check; sat -seq 6 -prove-asserts"]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    property_runs = []
    for top, sequence in (("counter_reset_property", 4), ("counter_hold_property", 6), ("counter_enable_property", 6)):
        property_run = subprocess.run(
            ["yosys", "-p", f"read_verilog -formal -sv {source} {PROPERTIES}; prep -top {top}; flatten; select -module {top}; sat -seq {sequence} -prove-asserts"],
            cwd=ROOT, capture_output=True, text=True, check=False)
        property_runs.append({"property": top, "sequence": sequence, "returncode": property_run.returncode, "passed": property_run.returncode == 0 and "SAT proof finished - no model found: SUCCESS!" in (property_run.stdout + property_run.stderr)})
    log.write_text(run.stdout + run.stderr, encoding="utf-8")
    (output / "property-proofs.json").write_text(json.dumps(property_runs, indent=2) + "\n", encoding="utf-8")
    passed = run.returncode == 0 and "SAT proof finished - no model found: SUCCESS!" in (run.stdout + run.stderr) and all(item["passed"] for item in property_runs)
    report = {
        "schema_version": "seeded-counter-formal-model-v1",
        "status": "passed" if passed else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(source), "sha256": digest(source)},
        "specification_model": {"path": str(FORMAL), "sha256": digest(FORMAL)},
        "proof": {"tool": "yosys-sat", "sequence": 6, "returncode": run.returncode, "result": "proven" if passed else "unknown", "log": str(log), "property_count": len(property_runs), "property_runs": property_runs},
        "claim_boundary": "Bounded formal equivalence to the seeded counter specification model after reset; not a complete proof of all system properties or silicon signoff.",
    }
    (output / "formal-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "proof": report["proof"]["result"], "output": str(output)}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
