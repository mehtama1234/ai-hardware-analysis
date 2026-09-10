"""Aggregate proof-of-value report for a customer regression job."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def build_regression_pov(run_root: str | Path) -> dict[str, Any]:
    root = Path(run_root)
    result = json.loads((root / "project-regression-result.json").read_text(encoding="utf-8"))
    cases = []
    covered = total = 0
    for index, case in enumerate(result.get("cases", []), 1):
        case_root = root / f"case-{index:03d}"
        coverage_path = case_root / "functional-coverage.json"
        coverage = json.loads(coverage_path.read_text(encoding="utf-8")) if coverage_path.is_file() else {"kind": "simulation_execution", "covered": int(case.get("status") == "passed"), "total": 1}
        covered += int(coverage["covered"])
        total += int(coverage["total"])
        cases.append({"index": index, "status": case.get("status"), "failure": case.get("failure"), "run_root": str(case_root), "coverage": coverage})
    report: dict[str, Any] = {
        "schema_version": "project-regression-pov-v1",
        "project_id": result.get("project_id"),
        "rtl_artifact_id": result.get("rtl_artifact_id"),
        "case_count": result.get("case_count", len(cases)),
        "passed_cases": result.get("passed_cases", 0),
        "failed_cases": result.get("failed_cases", 0),
        "status": result.get("status", "missing"),
        "cases": cases,
        "coverage": {"covered": covered, "total": total, "percentage": round(100.0 * covered / total, 4) if total else None},
        "claim_boundary": "regression metrics summarize captured simulations; they do not establish exhaustive functional coverage, formal proof, or hardware qualification",
    }
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return report


def write_regression_pov(run_root: str | Path) -> Path:
    output = Path(run_root) / "regression-proof-of-value-report.json"
    output.write_text(json.dumps(build_regression_pov(run_root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
