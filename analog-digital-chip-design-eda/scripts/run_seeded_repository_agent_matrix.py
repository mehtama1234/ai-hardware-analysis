"""Run bounded repository-agent diagnosis/repair handoffs across eight designs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.repository_agent import run_repository_agent


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "benchmarks/repository_scale/seeded_repository_agent_matrix.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m5/agent-matrix")
    parser.add_argument("--backend", choices=("mock", "local"), default="local")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {ROOT / 'scripts/mock_repository_agent_backend.py'}"
    results = []
    for task in plan["tasks"]:
        result = run_repository_agent(
            task_id=task["task_id"], source_revision=plan["source_revision"],
            evidence=["failure.log", task["source"]], failure_context=task["failure_context"],
            repair_before=task["repair_before"], repair_after=task["repair_after"],
            repair_source=ROOT / task["source"], backend="local",
            output_root=args.output / task["task_id"],
        )
        results.append({
            "task_id": task["task_id"], "status": result["team"]["status"],
            "handoffs": len(result["team"]["handoffs"]),
            "patch_candidate_status": result.get("patch_candidate", {}).get("status", result.get("patch_candidate_status")),
            "run_sha256": result["run_sha256"],
        })
    report = {
        "schema_version": "repository-agent-matrix-report-v1",
        "source_revision": plan["source_revision"], "backend": args.backend,
        "task_count": len(results), "tasks": results,
        "status": "passed" if all(item["status"] == "available" and item["patch_candidate_status"] == "review_required" for item in results) else "blocked",
        "claim_boundary": "bounded agent-to-patch-candidate handoffs over the declared seeded matrix; not repair correctness, model quality, or release signoff",
    }
    report["report_sha256"] = digest(report)
    path = args.output / "repository-agent-matrix-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "tasks": report["task_count"], "patch_candidates": sum(item["patch_candidate_status"] == "review_required" for item in results), "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
