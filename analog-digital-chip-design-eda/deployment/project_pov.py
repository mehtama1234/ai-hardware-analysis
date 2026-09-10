"""Customer-project proof-of-value aggregation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from verification_platform.coverage import rank_coverage_gaps


def build_project_pov(run_root: str | Path) -> dict[str, Any]:
    root = Path(run_root)

    def load(name: str, default: Any) -> Any:
        path = root / name
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

    result = load("project-simulation-result.json", {})
    closure = load("closure-report.json", [])
    diagnosis = load("diagnosis.json", {})
    verification_ir = load("verification-ir.json", {})
    covered = 1 if result.get("status") == "passed" else 0
    coverage = {"kind": "simulation_execution", "covered": covered, "total": 1}
    report: dict[str, Any] = {
        "schema_version": "project-pov-v1",
        "project_id": result.get("project_id"),
        "rtl_artifact_id": result.get("rtl_artifact_id"),
        "testbench_artifact_id": result.get("testbench_artifact_id"),
        "execution": {
            "status": result.get("status", "missing"),
            "tools": [run.get("tool") for run in (result.get("compile_run"), result.get("simulation_run")) if isinstance(run, dict)],
            "passed": sum(run.get("status") == "passed" for run in (result.get("compile_run"), result.get("simulation_run")) if isinstance(run, dict)),
            "failed": sum(run.get("status") == "failed" for run in (result.get("compile_run"), result.get("simulation_run")) if isinstance(run, dict)),
        },
        "failure": result.get("failure"),
        "diagnosis": diagnosis,
        "closure": {
            "total": len(closure),
            "failed": sum(item.get("status") == "failed" for item in closure),
            "proven": sum(item.get("status") == "proven" for item in closure),
            "open": sum(item.get("status") == "open" for item in closure),
            "results": closure,
        },
        "coverage": {**coverage, "percentage": float(covered * 100), "next_actions": rank_coverage_gaps([coverage]) if not covered else []},
        "traceability": {"tool_runs": len(verification_ir.get("tool_runs", [])), "verification_ir": str(root / "verification-ir.json") if (root / "verification-ir.json").is_file() else None},
        "claim_boundary": "simulation execution evidence is not functional, code, formal, or measured-hardware coverage",
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report


def write_project_pov(run_root: str | Path) -> Path:
    root = Path(run_root)
    output = root / "proof-of-value-report.json"
    output.write_text(json.dumps(build_project_pov(root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
