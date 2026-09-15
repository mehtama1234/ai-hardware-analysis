#!/usr/bin/env python3
"""Promote one local CPU Qwen closure run with an explicit claim boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--model-snapshot", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_copy = output / "cpu-closure-report.json"
    shutil.copyfile(args.report, report_copy)
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    model_hash = sha256(args.model_snapshot)
    adapter = ROOT / "scripts/qwen_local_jsonl_backend.py"
    receipt = {
        "schema_version": "local-cpu-model-supplemental-evidence-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if report.get("status") == "passed" and report.get("passed_tasks") == 1 else "blocked",
        "source_revision": revision,
        "backend": "local_qwen_jsonl_cpu",
        "device": "cpu",
        "cuda_available": False,
        "model_id": "Qwen/Qwen2.5-Coder-0.5B-Instruct",
        "model_snapshot_sha256": model_hash,
        "adapter_sha256": sha256(adapter),
        "task_range": report.get("task_range"),
        "passed_tasks": report.get("passed_tasks"),
        "report": {"path": report_copy.name, "sha256": sha256(report_copy)},
        "claim_boundary": "one local CPU Qwen held-out seeded repair trajectory; supplemental transport evidence only, not authenticated T4 evidence, full-suite closure, model generalization, human approval, production repair, or silicon signoff",
    }
    receipt["receipt_sha256"] = digest(receipt)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "output": str(output), "passed_tasks": receipt["passed_tasks"]}, sort_keys=True))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
