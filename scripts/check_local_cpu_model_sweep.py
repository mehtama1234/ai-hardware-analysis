#!/usr/bin/env python3
"""Independently verify the paired local CPU model sweep."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha(path: Path) -> str:
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
    if receipt.get("schema_version") != "local-cpu-model-supplemental-sweep-v1":
        errors.append("schema mismatch")
    if receipt.get("receipt_sha256") != digest({k: v for k, v in receipt.items() if k != "receipt_sha256"}):
        errors.append("receipt digest mismatch")
    if receipt.get("status") != "blocked_pending_supplemental_closure":
        errors.append("sweep must remain explicitly blocked")
    if receipt.get("device") != "cpu" or receipt.get("cuda_available") is not False or receipt.get("backend") != "local_qwen_jsonl_cpu":
        errors.append("CPU-only provenance boundary is malformed")
    metrics = receipt.get("metrics", {})
    if metrics != {"task_count": 2, "passed_tasks": 1, "closure_rate": 0.5, "canonical_reference_rate": 1.0, "causal_localization_rate": 1.0, "task_ids": ["arbiter-reset-grant", "decoder-opcode-two-value"]}:
        errors.append("sweep metrics mismatch")
    reports = receipt.get("reports", [])
    if len(reports) != 2:
        errors.append("sweep report count mismatch")
    else:
        loaded = {}
        for item in reports:
            report_path = path.parent / item.get("path", "")
            if not report_path.is_file() or sha(report_path) != item.get("sha256"):
                errors.append(f"report digest mismatch: {item.get('task')}")
            else:
                loaded[item.get("task")] = json.loads(report_path.read_text(encoding="utf-8"))
        arbiter = loaded.get("arbiter", {})
        decoder = loaded.get("decoder", {})
        if arbiter.get("status") != "passed" or arbiter.get("passed_tasks") != 1 or not arbiter.get("tasks", [{}])[0].get("passed"):
            errors.append("arbiter report is not the expected pass")
        if decoder.get("status") != "blocked" or decoder.get("passed_tasks") != 0 or decoder.get("tasks", [{}])[0].get("passed"):
            errors.append("decoder report is not the expected bounded failure")
    boundary = receipt.get("claim_boundary", "").lower()
    for required in ("cpu", "one pass", "one bounded repair rejection", "not authenticated t4", "not", "generalization"):
        if required not in boundary:
            errors.append(f"claim boundary missing: {required}")
    result = {"schema_version": "local-cpu-model-supplemental-sweep-check-v1", "status": "passed" if not errors else "blocked", "receipt": str(path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
