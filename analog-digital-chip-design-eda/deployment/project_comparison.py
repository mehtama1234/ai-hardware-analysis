"""Baseline versus retest proof-of-value comparison."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from deployment.project_pov import build_project_pov


def compare_project_runs(baseline_root: str | Path, retest_root: str | Path) -> dict[str, Any]:
    baseline = build_project_pov(baseline_root)
    retest = build_project_pov(retest_root)
    if baseline.get("project_id") != retest.get("project_id"):
        raise ValueError("baseline and retest must belong to the same project")
    result: dict[str, Any] = {
        "schema_version": "project-pov-comparison-v1",
        "project_id": baseline.get("project_id"),
        "baseline": {"run_root": str(Path(baseline_root)), "status": baseline["execution"]["status"], "report_sha256": baseline["report_sha256"], "failure": baseline.get("failure"), "coverage_percentage": baseline["coverage"]["percentage"]},
        "retest": {"run_root": str(Path(retest_root)), "status": retest["execution"]["status"], "report_sha256": retest["report_sha256"], "failure": retest.get("failure"), "coverage_percentage": retest["coverage"]["percentage"]},
        "metrics": {
            "failure_resolved": baseline["execution"]["status"] == "failed" and retest["execution"]["status"] == "passed",
            "coverage_delta_percentage_points": round(retest["coverage"]["percentage"] - baseline["coverage"]["percentage"], 4),
            "baseline_tool_runs": baseline["execution"]["passed"] + baseline["execution"]["failed"],
            "retest_tool_runs": retest["execution"]["passed"] + retest["execution"]["failed"],
        },
        "claim_boundary": "comparison measures captured simulation runs; it does not establish functional coverage, formal proof, or hardware qualification",
    }
    result["comparison_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def write_comparison(baseline_root: str | Path, retest_root: str | Path) -> Path:
    output = Path(retest_root) / "baseline-comparison.json"
    output.write_text(json.dumps(compare_project_runs(baseline_root, retest_root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
