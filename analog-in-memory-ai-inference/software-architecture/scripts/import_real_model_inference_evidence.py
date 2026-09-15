#!/usr/bin/env python3
"""Validate and normalize a GPU-host real-model inference handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(source: Path) -> dict[str, Any]:
    raw = json.loads(source.read_text(encoding="utf-8"))
    blockers: list[str] = []
    for key in ("evidence_kind", "model_profile", "protocol"):
        if key not in raw:
            blockers.append(f"missing top-level field: {key}")
    model = raw.get("model_profile", {})
    if not model.get("trained"):
        blockers.append("model_profile.trained must be true")
    if not any(model.get(key) for key in ("model_id", "model_revision", "model_sha256")):
        blockers.append("missing model identity")
    if not any(model.get(key) for key in ("tokenizer_id", "tokenizer_revision", "tokenizer_sha256")):
        blockers.append("missing tokenizer identity")
    if "synthetic" in json.dumps(raw).lower():
        blockers.append("synthetic workload marker present; real-model gate refuses promotion")
    if raw.get("evidence_kind") != "measured_gpu" or not raw.get("gpu_execution_accepted"):
        blockers.append("evidence must be accepted measured_gpu execution")
    protocol = raw.get("protocol", {})
    if not protocol.get("workloads"):
        blockers.append("protocol.workloads is empty")
    if not raw.get("rows") and not any(isinstance(raw.get(name), dict) and raw[name].get("rows") for name in ("prefill", "decode", "cached", "uncached")):
        blockers.append("missing serving latency rows")
    return {
        "schema_version": "real-model-inference-evidence-import-v0.1",
        "source": str(source),
        "source_sha256": sha256(source),
        "status": "ready_for_decision_package" if not blockers else "blocked",
        "evidence_kind": raw.get("evidence_kind"),
        "model": {key: model.get(key) for key in ("model_id", "model_revision", "model_sha256", "tokenizer_id", "tokenizer_revision", "tokenizer_sha256", "trained", "quality_passed") if key in model},
        "device": {key: raw.get(key) for key in ("device", "device_name", "torch_version") if key in raw},
        "workload_count": len(protocol.get("workloads", [])) if isinstance(protocol, dict) else 0,
        "blockers": blockers,
        "claim_boundary": {
            "allowed": "Only the evidence level and measured scope carried by the source report.",
            "refused": "Analog silicon benefit, production readiness, or measured energy without synchronized power evidence.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.source)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "real_model_inference_evidence_import.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "status": result["status"], "blockers": result["blockers"]}, indent=2))


if __name__ == "__main__":
    main()
