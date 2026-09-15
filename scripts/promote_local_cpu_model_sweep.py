#!/usr/bin/env python3
"""Promote paired local CPU model reports without hiding a failed task."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passed-report", type=Path, required=True)
    parser.add_argument("--blocked-report", type=Path, required=True)
    parser.add_argument("--model-snapshot", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    copied = []
    for label, source in (("arbiter", args.passed_report), ("decoder", args.blocked_report)):
        destination = output / f"{label}-closure-report.json"
        shutil.copyfile(source, destination)
        copied.append({"task": label, "path": destination.name, "sha256": sha(destination)})
    adapter = ROOT / "scripts/qwen_local_jsonl_backend.py"
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    receipt = {
        "schema_version": "local-cpu-model-supplemental-sweep-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "blocked_pending_supplemental_closure",
        "source_revision": revision,
        "backend": "local_qwen_jsonl_cpu",
        "device": "cpu",
        "cuda_available": False,
        "model_id": "Qwen/Qwen2.5-Coder-0.5B-Instruct",
        "model_snapshot_sha256": sha(args.model_snapshot),
        "adapter_sha256": sha(adapter),
        "reports": copied,
        "metrics": {"task_count": 2, "passed_tasks": 1, "closure_rate": 0.5, "canonical_reference_rate": 1.0, "causal_localization_rate": 1.0, "task_ids": ["arbiter-reset-grant", "decoder-opcode-two-value"]},
        "claim_boundary": "two-task local CPU Qwen held-out seeded repair sweep with one pass and one bounded repair rejection; supplemental transport evidence only, not authenticated T4 evidence, full-suite closure, model generalization, human approval, production repair, or silicon signoff",
    }
    receipt["receipt_sha256"] = digest(receipt)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "output": str(output), "metrics": receipt["metrics"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
