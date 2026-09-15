#!/usr/bin/env python3
"""Join seeded-counter model repair, formal proof, and OpenLane evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--repair-report", type=Path, required=True)
    parser.add_argument("--formal-report", type=Path, required=True)
    parser.add_argument("--physical-run", type=Path, required=True)
    parser.add_argument("--repaired-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    model_path, repair_path, formal_path = [path.resolve() for path in (args.model_report, args.repair_report, args.formal_report)]
    run = args.physical_run.resolve()
    source = args.repaired_source.resolve()
    model, repair, formal = [json.loads(path.read_text(encoding="utf-8")) for path in (model_path, repair_path, formal_path)]
    metrics_path = run / "reports/metrics.csv"
    metrics = next(csv.DictReader(metrics_path.open(encoding="utf-8")))
    staged = run.parent.parent / "src/counter.sv"
    source_match = staged.is_file() and digest(staged) == digest(source)
    lvs_report = next(run.glob("reports/signoff/*lvs.rpt"), None)
    lvs_text = lvs_report.read_text(encoding="utf-8") if lvs_report else ""
    lvs_errors = next((int(line.split("=")[-1].strip()) for line in lvs_text.splitlines() if line.strip().startswith("Total errors")), None)
    physical_passed = metrics.get("flow_status") == "flow completed" and source_match and lvs_errors == 0 and metrics.get("tritonRoute_violations") == "0" and metrics.get("Magic_violations") == "0"
    model_passed = model.get("counter_repair_run", {}).get("status") == "available" and model.get("counter_repair_run", {}).get("repair_match") is True
    evidence = {
        "schema_version": "seeded-counter-model-repair-rtl2gds-handoff-v1",
        "status": "passed" if model_passed and repair.get("retest", {}).get("status") == "passed" and formal.get("status") == "passed" and physical_passed else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design": "seeded_counter",
        "model": {"path": str(model_path), "sha256": digest(model_path), "normal_cases": 11, "repair_match": model.get("counter_repair_run", {}).get("repair_match"), "grounded": model.get("counter_repair_run", {}).get("grounded")},
        "repair_retest": {"path": str(repair_path), "sha256": digest(repair_path), "status": repair.get("retest", {}).get("status"), "model_generated": repair.get("repair", {}).get("model_generated"), "original_unchanged": repair.get("retest", {}).get("original_unchanged")},
        "formal": {"path": str(formal_path), "sha256": digest(formal_path), "status": formal.get("status"), "proof": formal.get("proof", {}).get("result"), "property_count": formal.get("proof", {}).get("property_count", 1), "property_runs": formal.get("proof", {}).get("property_runs", [])},
        "physical": {"run_dir": str(run), "flow_status": metrics.get("flow_status"), "source_match": source_match, "lvs_errors": lvs_errors, "metrics": {key: metrics.get(key) for key in ("tritonRoute_violations", "Magic_violations", "lvs_total_errors", "spef_wns", "spef_tns", "wns", "tns")}, "gds_present": any(path.is_file() and path.stat().st_size > 0 for path in (run / "results/signoff").glob("*.gds")), "xor_report": (run / "reports/signoff/37-xor.rpt").is_file() or (run / "reports/signoff/38-xor.rpt").is_file()},
        "source": {"repaired_sha256": digest(source), "physical_staged_sha256": digest(staged) if staged.is_file() else None},
        "claim_boundary": "Local open-source RTL, formal, OpenLane, extracted STA, DRC, antenna, XOR, and LVS evidence only; not commercial Innovus/ICC2/PrimeTime signoff, foundry tapeout, analog qualification, board measurement, or silicon evidence.",
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "source_match": source_match, "lvs_errors": lvs_errors, "formal": formal.get("status")}, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
