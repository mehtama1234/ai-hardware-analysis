#!/usr/bin/env python3
"""Join accepted LLM evidence with the canonical AIMC RTL2GDS evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_llm_model_evaluation import verify as verify_llm_report


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--rtl2gds-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    model_report = args.model_report.resolve()
    rtl2gds_report = args.rtl2gds_report.resolve()
    output = args.output.resolve()

    model_errors = verify_llm_report(model_report)
    model_payload = json.loads(model_report.read_text(encoding="utf-8"))
    aimc_model_run = model_payload.get("aimc_mutation_run")
    aimc_model_passed = isinstance(aimc_model_run, dict) and aimc_model_run.get("status") == "available" and aimc_model_run.get("grounded") is True and aimc_model_run.get("diagnosis_match") is True and aimc_model_run.get("adversarial_review", {}).get("accepted") is True
    physical = json.loads(rtl2gds_report.read_text(encoding="utf-8"))
    physical_passed = physical.get("status") == "passed"
    handoff = {
        "schema_version": "llm-rtl2gds-handoff-v1",
        "status": "passed" if not model_errors and physical_passed else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "llm_evidence": {
            "path": str(model_report),
            "sha256": digest(model_report),
            "acceptance": "passed" if not model_errors else "failed",
            "errors": model_errors,
            "model_cases": 11,
            "aimc_mutation_diagnosis": "passed" if aimc_model_passed else "absent_or_failed",
        },
        "rtl2gds_evidence": {
            "path": str(rtl2gds_report),
            "sha256": digest(rtl2gds_report),
            "status": physical.get("status"),
            "design": physical.get("design"),
        },
        "relationship": {
            "same_design_run": False,
            "same_design_model_diagnosis": aimc_model_passed,
            "meaning": "The LLM artifact proves review-gated diagnosis capability on the seeded RTL corpus and, when present, on a deliberately mutated AIMC controller. The RTL2GDS artifact proves canonical AIMC RTL/physical-input alignment and local physical checks. They are joined for traceability, not promoted to a model-edited AIMC signoff claim.",
            "next_same_design_gate": "Require approval, repair the AIMC copy, rerun identical-scope RTL checks, and revalidate physical inputs against the canonical design.",
        },
        "claim_boundary": "Evidence handoff only; no autonomous repair, commercial Innovus/ICC2/PrimeTime signoff, analog qualification, board measurement, silicon correctness, or tapeout claim.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": handoff["status"], "output": str(output), "same_design_run": False, "same_design_model_diagnosis": aimc_model_passed}))
    return 0 if handoff["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
