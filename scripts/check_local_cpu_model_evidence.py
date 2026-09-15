#!/usr/bin/env python3
"""Independently check the bounded local CPU model supplemental receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    path = args.receipt.resolve()
    errors: list[str] = []
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
        return 1
    if receipt.get("schema_version") != "local-cpu-model-supplemental-evidence-v1":
        errors.append("schema mismatch")
    if receipt.get("receipt_sha256") != digest({k: v for k, v in receipt.items() if k != "receipt_sha256"}):
        errors.append("receipt digest mismatch")
    if receipt.get("backend") != "local_qwen_jsonl_cpu" or receipt.get("device") != "cpu" or receipt.get("cuda_available") is not False:
        errors.append("CPU-only provenance boundary is malformed")
    if receipt.get("model_id") != "Qwen/Qwen2.5-Coder-0.5B-Instruct":
        errors.append("unexpected model identity")
    report_info = receipt.get("report", {})
    report_path = path.parent / report_info.get("path", "")
    if not report_path.is_file() or sha256(report_path) != report_info.get("sha256"):
        errors.append("closure report digest mismatch")
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") != "passed" or report.get("passed_tasks") != 1 or report.get("task_count") != 1:
            errors.append("supplemental report is not exactly one passed task")
        if report.get("task_range", {}).get("start_index") != 8:
            errors.append("supplemental report is not the declared held-out index")
        tasks = report.get("tasks", [])
        if len(tasks) != 1 or tasks[0].get("task_id") != "arbiter-reset-grant" or not tasks[0].get("passed"):
            errors.append("held-out task identity or closure status mismatch")
    boundary = receipt.get("claim_boundary", "").lower()
    for required in ("cpu", "not authenticated t4", "not", "generalization"):
        if required not in boundary:
            errors.append(f"claim boundary missing: {required}")
    if receipt.get("status") != "passed":
        errors.append("receipt is not passed")
    result = {"schema_version": "local-cpu-model-supplemental-evidence-check-v1", "status": "passed" if not errors else "blocked", "receipt": str(path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
