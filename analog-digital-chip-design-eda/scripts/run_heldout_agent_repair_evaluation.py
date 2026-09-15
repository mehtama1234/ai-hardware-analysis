#!/usr/bin/env python3
"""Evaluate agent repair closure on a declared train/held-out mutation split."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "benchmarks/repository_scale/seeded_mutation_evaluation.json"
SUITE = ROOT / "benchmarks/repository_scale/seeded_multi_mutation_suite.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_split(output: Path, *, start: int, count: int, backend: str) -> dict[str, object]:
    split_output = output / ("train" if start == 0 else "heldout")
    command = [
        sys.executable, "scripts/run_seeded_agent_repair_closure.py",
        "--output", str(split_output), "--backend", backend,
        "--start-index", str(start), "--max-tasks", str(count),
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    report_path = split_output / "seeded-agent-repair-closure-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return {
        "command": command,
        "returncode": completed.returncode,
        "status": "passed" if completed.returncode == 0 else "blocked",
        "stdout_tail": completed.stdout[-3000:],
        "stderr_tail": completed.stderr[-3000:],
        "report": report,
        "report_path": str(report_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to reuse non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    mutations = [str(item["mutation_id"]) for item in suite["mutations"]]
    train_ids = [str(item) for item in plan["train_mutations"]]
    heldout_ids = [str(item) for item in plan["heldout_mutations"]]
    if train_ids + heldout_ids != mutations:
        raise SystemExit("evaluation split must preserve the suite order and cover every mutation exactly once")
    train = run_split(output, start=0, count=len(train_ids), backend=args.backend)
    heldout = run_split(output, start=len(train_ids), count=len(heldout_ids), backend=args.backend)

    def score(run: dict[str, object], expected: list[str]) -> dict[str, object]:
        report = run.get("report")
        tasks = report.get("tasks", []) if isinstance(report, dict) else []
        passed_ids = [str(item.get("task_id")) for item in tasks if item.get("passed") is True]
        model_selected = sum(item.get("model_selected_repair") is True for item in tasks)
        return {
            "expected_ids": expected,
            "observed_ids": [str(item.get("task_id")) for item in tasks],
            "total": len(tasks),
            "passed": len(passed_ids),
            "closure_rate": round(len(passed_ids) / len(expected), 6) if expected else None,
            "all_passed": passed_ids == expected,
            "model_selected_repair_count": model_selected,
            "model_selected_repair_rate": round(model_selected / len(expected), 6) if expected else None,
        }

    train_score = score(train, train_ids)
    heldout_score = score(heldout, heldout_ids)
    report = {
        "schema_version": "agent-repair-heldout-evaluation-report-v1",
        "plan": str(PLAN),
        "suite": str(SUITE),
        "backend": args.backend,
        "train": train_score,
        "heldout": heldout_score,
        "runs": {"train": train, "heldout": heldout},
        "status": "passed" if train_score["all_passed"] and heldout_score["all_passed"] else "blocked",
        "claim_boundary": "declared seeded train/held-out repair closure; not generalization to unseen repositories or autonomous production repair",
    }
    report["report_sha256"] = digest(report)
    path = output / "agent-repair-heldout-evaluation-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "backend": args.backend, "train": train_score, "heldout": heldout_score, "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
