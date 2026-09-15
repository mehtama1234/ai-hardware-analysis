#!/usr/bin/env python3
"""Compare the same pinned GPT-2 profile run on CPU and CUDA."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def wall(row: dict, side: str) -> float:
    modern = f"{side}_reference_wall_ms"
    legacy = f"{side}_cpu_reference_wall_ms"
    if modern in row:
        return float(row[modern])
    if legacy in row:
        return float(row[legacy])
    raise KeyError(modern)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu, cuda = load(args.cpu), load(args.cuda)
    failures = []
    if cpu.get("model", {}).get("revision") != cuda.get("model", {}).get("revision"):
        failures.append("model revisions differ")
    if cpu.get("fixture") != cuda.get("fixture"):
        failures.append("fixtures differ")
    if cpu.get("runtime", {}).get("device") != "cpu":
        failures.append("CPU control does not report cpu")
    if cuda.get("runtime", {}).get("device") != "cuda":
        failures.append("CUDA run does not report cuda")
    rows = []
    cuda_by_id = {row["id"]: row for row in cuda.get("variants", [])}
    for variant in cpu.get("variants", []):
        other = cuda_by_id.get(variant["id"])
        if other is None:
            failures.append(f"CUDA variant missing: {variant['id']}")
            continue
        cq, gq = variant["quality"], other["quality"]
        cpu_ms = [wall(row, "candidate") for row in cq["rows"]]
        cuda_ms = [wall(row, "candidate") for row in gq["rows"]]
        rows.append({
            "variant": variant["id"],
            "cpu_quality": {"nll_increase_nats": cq["nll_increase_nats"],
                            "argmax_agreement": cq["teacher_forced_argmax_agreement"],
                            "generation_exact_matches": cq["generation_exact_match_count"]},
            "cuda_quality": {"nll_increase_nats": gq["nll_increase_nats"],
                              "argmax_agreement": gq["teacher_forced_argmax_agreement"],
                              "generation_exact_matches": gq["generation_exact_match_count"]},
            "cpu_reference_wall_ms": cpu_ms,
            "cuda_reference_wall_ms": cuda_ms,
            "median_cpu_ms": statistics.median(cpu_ms),
            "median_cuda_ms": statistics.median(cuda_ms),
            "cpu_to_cuda_speedup": statistics.median(cpu_ms) / statistics.median(cuda_ms),
        })
        # The read-noise variant is intentionally stochastic; compare its
        # distribution in a repeated study instead of demanding bitwise parity
        # across devices. Deterministic variants must match exactly.
        if "noise" not in variant["id"]:
            for key in ("predicted_tokens", "teacher_forced_argmax_agreement", "generation_exact_match_count"):
                if cq[key] != gq[key]:
                    failures.append(f"{variant['id']}: quality field differs: {key}")
    result = {
        "schema_version": "gpt2-cpu-cuda-comparison-v0.1",
        "result_type": "matched_pinned_profile_device_comparison",
        "sources": {"cpu": str(args.cpu), "cuda": str(args.cuda)},
        "model_revision": cuda.get("model", {}).get("revision"),
        "variants": rows,
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "interpretation": "Timing compares the same numerical fixture and profile across CPU and CUDA. It is a device execution comparison, not an analog hardware comparison or energy measurement.",
        "claim_boundary": "No analog placement, silicon yield, analog speedup, or energy claim is made; profile quality remains a numerical-model result.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "status": result["status"], "variants": len(rows)}))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
