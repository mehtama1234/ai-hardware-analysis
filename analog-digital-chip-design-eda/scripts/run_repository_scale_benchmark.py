#!/usr/bin/env python3
"""Run repository-scale fail-to-pass tasks from a checked-in manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verification_platform.repository_benchmark import run_repository_task, validate_task_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--canonical-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--task", action="append")
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_task_manifest(manifest)
    selected = set(args.task or [item["task_id"] for item in manifest["tasks"]])
    tasks = [item for item in manifest["tasks"] if item["task_id"] in selected]
    if len(tasks) != len(selected):
        missing = sorted(selected - {item["task_id"] for item in tasks})
        raise SystemExit(f"unknown task ids: {missing}")
    records: list[dict[str, Any]] = []
    for task in tasks:
        record = run_repository_task(
            task,
            canonical_root=task.get("canonical_root", args.canonical_root),
            baseline_root=task.get("baseline_root", args.baseline_root),
            candidate_root=task.get("candidate_root", args.candidate_root),
            output_root=args.output / task["task_id"],
            timeout_seconds=args.timeout_seconds,
        )
        records.append(record)
    report: dict[str, Any] = {
        "schema_version": "repository-scale-benchmark-report-v1",
        "manifest": str(args.manifest.resolve()),
        "task_count": len(records),
        "status": "passed" if records and all(item["status"] == "passed" for item in records) else "blocked",
        "records": records,
        "claim_boundary": "reproducible native command outcomes and source-integrity checks; not proof of general correctness",
    }
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "benchmark-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "task_count": report["task_count"], "output": str(args.output / "benchmark-report.json")}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
