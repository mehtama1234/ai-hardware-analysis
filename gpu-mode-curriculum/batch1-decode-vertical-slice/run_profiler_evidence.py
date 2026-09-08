#!/usr/bin/env python3
"""Capture framework profiler evidence for dynamic versus preallocated decode."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch.profiler import ProfilerActivity, profile, record_function

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT if (ROOT / "gpu-kernels-serving-lab").exists() else ROOT.parent
SERVING = REPO / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from neural_generator import NeuralGenerator  # noqa: E402

REPORT = HERE / "reports" / "profiler-evidence.json"
PROMPT = "attention cache"
MAX_TOKENS = 96
MODEL_HIDDEN = 128
MODEL_HEADS = 8


def _event_row(event) -> dict:
    row = {"name": event.key, "count": int(event.count), "cpu_time_us": float(event.cpu_time_total)}
    for attr in ("device_time_total", "self_device_time_total"):
        if hasattr(event, attr):
            row[attr + "_us"] = float(getattr(event, attr))
    return row


def _capture(generator: NeuralGenerator, mode: str) -> dict:
    cached = mode != "uncached"
    storage = "preallocated" if mode == "preallocated" else "dynamic"
    activities = [ProfilerActivity.CPU]
    if generator.device.type == "cuda":
        activities.append(ProfilerActivity.CUDA)
    with profile(activities=activities, record_shapes=True, profile_memory=True) as trace:
        with record_function(f"batch1_{mode}_decode"):
            generator.generate(PROMPT, MAX_TOKENS, cached=cached, cache_storage=storage)
    events = trace.key_averages()
    rows = sorted((_event_row(event) for event in events), key=lambda row: row.get("device_time_total_us", 0.0), reverse=True)
    cuda_rows = [row for row in rows if row.get("device_time_total_us", 0.0) > 0.0]
    return {
        "mode": mode,
        "cuda_kernel_event_count": len(cuda_rows),
        "cuda_time_total_us": sum(row.get("device_time_total_us", 0.0) for row in rows),
        "aten_cat_count": sum(row["count"] for row in rows if row["name"] == "aten::cat"),
        "top_events": rows[:40],
    }


def main() -> int:
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        generator = NeuralGenerator("cuda" if torch.cuda.is_available() else "cpu", hidden=MODEL_HIDDEN, heads=MODEL_HEADS)
        # Warm up the dispatcher and allocator outside the captured region.
        generator.generate(PROMPT, MAX_TOKENS, cached=True, cache_storage="preallocated")
        captures = [_capture(generator, mode) for mode in ("uncached", "cached", "preallocated")]
        checks = {
            "three_modes_captured": len(captures) == 3,
            "cuda_kernels_captured": generator.device.type != "cuda" or all(row["cuda_kernel_event_count"] > 0 for row in captures),
            "preallocated_cat_not_greater": captures[2]["aten_cat_count"] <= captures[1]["aten_cat_count"],
            "preallocated_kernel_observed": generator.device.type != "cuda" or any(
                "append_kv" in event["name"].lower() for event in captures[2]["top_events"]
            ),
        }
        report = {
            "experiment": "batch1_decode_profiler_evidence",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if all(checks.values()) else "failed",
            "evidence_kind": "measured_gpu" if generator.device.type == "cuda" else "measured_cpu",
            "device": str(generator.device),
            "gpu_execution_accepted": generator.device.type == "cuda" and all(checks.values()),
            "protocol": {"prompt": PROMPT, "max_tokens": MAX_TOKENS, "model_hidden": MODEL_HIDDEN, "model_heads": MODEL_HEADS, "activities": ["CPU", "CUDA" if generator.device.type == "cuda" else "CPU-only"]},
            "captures": captures,
            "checks": checks,
            "interpretation": "PyTorch profiler evidence counts framework and CUDA activity; it is not a substitute for Nsight Compute hardware counters.",
            "source_sha256": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).resolve(), SERVING / "neural_generator.py", ROOT / "model-integration/model_integration/tiny_transformer.py")},
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "evidence_kind": report["evidence_kind"], "device": report["device"], "checks": checks}, indent=2))
        return 0 if report["status"] == "passed" else 1
    finally:
        torch.set_num_threads(previous_threads)


if __name__ == "__main__":
    raise SystemExit(main())
