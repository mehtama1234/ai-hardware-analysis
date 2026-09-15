#!/usr/bin/env python3
"""Build one hash-bound local digital qualification decision package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("evidence/end-to-end-qualification-manifest.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    workspace = manifest_path.parents[1]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    workload = manifest["gates"]["workload"]
    evidence = workload["evidence"]
    selected = [
        "local_multimodule_report", "local_multimodule_runtime_trace",
        "local_multimodule_cost_trace", "local_module_error_decomposition",
        "local_transfer_table_fallback_policy", "local_transformer_transfer_table_runtime_trace",
        "local_transformer_fallback_output_audit",
        "local_transformer_per_vector_fallback_fingerprint",
    ]
    sources = {}
    for key in selected:
        entry = evidence[key]
        path = workspace / entry["path"]
        if not path.is_file():
            path = workspace.parent / entry["path"]
        if not path.is_file() or sha256(path) != entry["sha256"]:
            raise SystemExit(f"manifest-bound source is missing or stale: {key}: {path}")
        sources[key] = {"path": str(path), "sha256": sha256(path)}
    fingerprint = json.loads(Path(sources["local_transformer_per_vector_fallback_fingerprint"]["path"]).read_text())
    transformer_trace = json.loads(Path(sources["local_transformer_transfer_table_runtime_trace"]["path"]).read_text())
    policy = json.loads(Path(sources["local_transfer_table_fallback_policy"]["path"]).read_text())
    output = {
        "schema_version": "local-digital-qualification-package-v0.1",
        "result_type": "hash_bound_local_model_to_chip_digital_decision",
        "manifest": {"path": str(manifest_path), "sha256": sha256(manifest_path)},
        "decision": "digital_reference_and_deterministic_fallback_only",
        "analog_authorized": False,
        "workload_vectors": fingerprint["workload_vectors"],
        "target_modules": fingerprint["target_modules"],
        "fallback_parity": {
            "all_modules_numerically_equal": fingerprint["all_modules_numerically_equal"],
            "tolerance": {"atol": 3e-5, "rtol": 1e-5},
            "raw_hash_mismatch_count": fingerprint["total_mismatch_count"],
        },
        "runtime": {
            "scheduled_vectors": len(transformer_trace["events"]),
            "analog_instruction_count": transformer_trace["analog_instruction_count"],
            "all_routes_fallback": transformer_trace["all_routes_fallback"],
            "unsupported_converter_codes": policy["unsupported_codes"],
        },
        "gate_summary": {name: {"pass": gate["pass"], "status": gate["status"]}
                         for name, gate in manifest["gates"].items()},
        "sources": sources,
        "claim_boundary": "Local CPU/model replay, compiler fallback, converter-code policy, and modeled operation accounting only; no measured analog execution, hardware timing, energy, silicon yield, or production claim.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "local_digital_qualification_package.json"
    report_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "README.md").write_text(
        "# Local digital qualification package\n\n"
        "Decision: **digital reference and deterministic fallback only**.\n\n"
        "The package joins the frozen transformer workload, all-vector fallback parity, converter-code routing, runtime trace, error evidence, and modeled cost inputs. Analog authorization remains false because converter completeness, physical qualification, measured timing, and matched energy remain open.\n\n"
        "All source paths and SHA-256 hashes are recorded in `local_digital_qualification_package.json`.\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(report_path), "vectors": output["workload_vectors"],
                      "analog_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
