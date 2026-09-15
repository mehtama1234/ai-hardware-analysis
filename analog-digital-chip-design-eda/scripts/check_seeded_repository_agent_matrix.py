"""Independently validate the seeded repository-agent matrix evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "benchmarks/repository_scale/seeded_repository_agent_matrix.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    errors = []
    expected = {task["task_id"] for task in plan["tasks"]}
    if report.get("schema_version") != "repository-agent-matrix-report-v1":
        errors.append("unsupported matrix report schema")
    if report.get("source_revision") != plan["source_revision"]:
        errors.append("source revision mismatch")
    rows = report.get("tasks", [])
    if {row.get("task_id") for row in rows} != expected or len(rows) != len(expected):
        errors.append("matrix task set mismatch")
    for task in plan["tasks"]:
        run_path = args.report.parent / task["task_id"] / "repository-agent-run.json"
        if not run_path.is_file():
            errors.append(f"missing run record: {task['task_id']}")
            continue
        run = json.loads(run_path.read_text(encoding="utf-8"))
        team = run.get("team", {})
        repair = next((item for item in team.get("results", []) if item.get("role") == "repair_proposer"), {})
        candidate = run.get("patch_candidate", {})
        if team.get("status") != "available" or len(team.get("handoffs", [])) != 4:
            errors.append(f"incomplete team trajectory: {task['task_id']}")
        if repair.get("bounded_repair", {}).get("before") != task["repair_before"] or repair.get("bounded_repair", {}).get("after") != task["repair_after"]:
            errors.append(f"bounded repair mismatch: {task['task_id']}")
        if candidate.get("status") != "review_required" or candidate.get("source_revision") != plan["source_revision"]:
            errors.append(f"invalid patch candidate: {task['task_id']}")
    expected_digest = digest({key: value for key, value in report.items() if key != "report_sha256"})
    if report.get("report_sha256") != expected_digest:
        errors.append("matrix report digest mismatch")
    result = {"schema_version": "repository-agent-matrix-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": errors}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
