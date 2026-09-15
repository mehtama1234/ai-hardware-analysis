#!/usr/bin/env python3
"""Attach verified Colab runtime provenance to a downloaded benchmark report."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_llm_model_evaluation import verify


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("colab_summary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    benchmark = args.benchmark.resolve()
    summary_path = args.colab_summary.resolve()
    try:
        payload = json.loads(benchmark.read_text(encoding="utf-8"))
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read Colab evidence: {error}", file=sys.stderr)
        return 2
    if verify(benchmark):
        print("source benchmark does not satisfy the base acceptance contract", file=sys.stderr)
        return 2
    if summary.get("schema_version") != "aimc-llm-agent-colab-run-v1" or summary.get("status") != "passed":
        print("Colab summary is not a passed v1 run", file=sys.stderr)
        return 2
    model_id = str(summary.get("model_id") or "")
    gpu = ""
    for step in summary.get("steps", []):
        if isinstance(step, dict) and step.get("command", [None])[0] == "bash":
            gpu = str(step.get("stdout_tail") or "").strip()
            if gpu:
                break
    if not model_id or not gpu:
        print("Colab summary has no model or GPU identity", file=sys.stderr)
        return 2
    payload.pop("evidence_sha256", None)
    payload["model_provenance"] = {
        "schema_version": "real-model-runtime-provenance-v1",
        "provider": "google-colab",
        "model_id": model_id,
        "accelerator": "cuda",
        "gpu": gpu,
        "weights_downloaded_in_runtime": True,
        "source_archive_only": True,
        "colab_summary_sha256": digest(summary_path),
        "source_benchmark_sha256": digest(benchmark),
        "claim_boundary": "Runtime provenance identifies the model execution only; it does not authorize RTL edits or release signoff.",
    }
    payload["evidence_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    errors = verify(output, require_real_model=True)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "output": str(output), "model_id": model_id, "gpu": gpu}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
