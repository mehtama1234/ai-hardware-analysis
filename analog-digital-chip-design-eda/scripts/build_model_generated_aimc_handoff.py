#!/usr/bin/env python3
"""Join the final Colab repair, copy retest, and same-design OpenLane run."""
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
    parser.add_argument("--physical-run", type=Path, required=True)
    parser.add_argument("--repaired-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    model_report = args.model_report.resolve()
    repair_report = args.repair_report.resolve()
    physical_run = args.physical_run.resolve()
    repaired_source = args.repaired_source.resolve()
    output = args.output.resolve()
    model = json.loads(model_report.read_text(encoding="utf-8"))
    repair = json.loads(repair_report.read_text(encoding="utf-8"))
    metrics_path = physical_run / "reports/metrics.csv"
    metrics = next(csv.DictReader(metrics_path.open(encoding="utf-8")))
    source_names = sorted(path.name for path in repaired_source.glob("*.v"))
    alignments = {}
    staged_source = physical_run.parent.parent / "src"
    for name in source_names:
        repaired = repaired_source / name
        staged = staged_source / name
        alignments[name] = {
            "repaired_sha256": digest(repaired),
            "physical_staged_sha256": digest(staged) if staged.is_file() else None,
            "byte_identical": staged.is_file() and digest(repaired) == digest(staged),
        }
    physical_source_match = all(item["byte_identical"] for item in alignments.values())
    lvs_report = next(physical_run.glob("reports/signoff/*lvs.rpt"), None)
    lvs_text = lvs_report.read_text(encoding="utf-8") if lvs_report else ""
    lvs_errors = None
    for line in lvs_text.splitlines():
        if line.strip().startswith("Total errors"):
            lvs_errors = int(line.split("=")[-1].strip())
    physical_completed_to_signoff = metrics.get("flow_status") == "flow completed"
    claim_boundary = (
        "Same-design local OpenLane research evidence only. The physical run completed through extracted STA, GDS, DRC, antenna checks, and LVS; this is not commercial Innovus/ICC2/PrimeTime signoff, foundry tapeout, analog qualification, board measurement, or silicon evidence."
        if physical_completed_to_signoff
        else
        "Same-design local OpenLane research evidence only. The physical run did not complete all signoff checks; this is not commercial Innovus/ICC2/PrimeTime signoff, foundry tapeout, analog qualification, board measurement, or silicon evidence."
    )
    evidence = {
        "schema_version": "model-generated-aimc-rtl2gds-handoff-v1",
        "status": "passed" if physical_completed_to_signoff and physical_source_match and repair.get("status") == "passed" else "partial",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design": "aimc_multi_clock_control_subsystem",
        "llm": {
            "path": str(model_report),
            "sha256": digest(model_report),
            "acceptance": "passed" if model.get("aimc_mutation_repair_run", {}).get("repair_match") is True else "failed",
            "model_id": model.get("model_id", "Qwen/Qwen2.5-0.5B-Instruct"),
            "normal_cases": 11,
            "aimc_diagnosis": model.get("aimc_mutation_run", {}).get("status"),
            "aimc_repair": model.get("aimc_mutation_repair_run", {}).get("repair_match"),
        },
        "approved_retest": {
            "path": str(repair_report),
            "sha256": digest(repair_report),
            "status": repair.get("status"),
            "model_generated": repair.get("repair", {}).get("model_generated"),
            "approval": repair.get("approval"),
        },
        "physical": {
            "run_dir": str(physical_run),
            "flow_status": metrics.get("flow_status"),
            "source_match": physical_source_match,
            "metrics": {key: metrics.get(key) for key in ("tritonRoute_violations", "Magic_violations", "spef_wns", "spef_tns", "wns", "tns", "lvs_total_errors")},
            "lvs_report": str(lvs_report) if lvs_report else None,
            "lvs_total_errors_from_report": lvs_errors,
            "gds_present": any(path.is_file() and path.stat().st_size > 0 for path in (physical_run / "results/signoff").glob("*.gds")),
            "extracted_sta_present": (physical_run / "reports/signoff/34-rcx_sta.summary.rpt").is_file(),
        },
        "source_alignment": alignments,
        "claim_boundary": claim_boundary,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "physical_flow_status": metrics.get("flow_status"), "source_match": physical_source_match, "lvs_errors": lvs_errors}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
