#!/usr/bin/env python3
"""Run and evaluate the complete provider-free closure-lab reference loop."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "benchmarks" / "multi_design_pilot"


def main() -> int:
    run = subprocess.run([sys.executable, str(PILOT / "ci_gate.py")], cwd=ROOT, capture_output=True, text=True)
    validation = json.loads((PILOT / "runs/latest/clean-checkout-validation.json").read_text(encoding="utf-8")) if (PILOT / "runs/latest/clean-checkout-validation.json").is_file() else {"valid": False}
    summary = json.loads((PILOT / "runs/latest/pilot-summary.json").read_text(encoding="utf-8")) if (PILOT / "runs/latest/pilot-summary.json").is_file() else {}
    metrics = summary.get("metrics", {})
    ready = (
        run.returncode == 0
        and validation.get("valid") is True
        and summary.get("passed_retests") == summary.get("design_count")
        and metrics.get("all_artifacts_verified") is True
        and metrics.get("original_sources_unchanged") == summary.get("design_count")
        and metrics.get("next_test_proposals_reviewable") == summary.get("design_count")
    )
    decision = {
        "schema_version": "closure-lab-decision-v1",
        "backend_policy": "open-source-only",
        "hardware_required": False,
        "decision": "reference_closure_ready_for_human_signoff" if ready else "blocked",
        "closure_claim": "reference workflow only; no exhaustive coverage, formal completeness, silicon correctness, or customer ROI",
        "pilot_summary_sha256": summary.get("summary_sha256"),
        "validation": validation,
        "metrics": {
            "design_count": summary.get("design_count"),
            "agent_proposals_reviewable": metrics.get("agent_proposals_reviewable"),
            "next_test_proposals_reviewable": metrics.get("next_test_proposals_reviewable"),
            "passed_retests": summary.get("passed_retests"),
            "all_artifacts_verified": metrics.get("all_artifacts_verified"),
            "original_sources_unchanged": metrics.get("original_sources_unchanged"),
            "unique_fault_classes": metrics.get("unique_fault_classes"),
            "scope_comparable": validation.get("scope_comparable"),
        },
        "blockers": [] if ready else ["closure gates did not all pass; inspect pilot summary and clean-checkout validation"],
    }
    body = json.dumps(decision, sort_keys=True, separators=(",", ":"))
    decision["decision_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    output = ROOT / ".artifacts" / "closure-lab-decision.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(decision, sort_keys=True))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
