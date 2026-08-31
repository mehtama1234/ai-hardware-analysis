from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import torch


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "numerical-reproducibility"
REPORT_JSON = OUT / "numerical-reproducibility-report.json"
REPORT_MD = OUT / "reports" / "numerical-reproducibility-report.md"

SOURCE_REPORTS = [
    "quantization-memory-formats/quantization-report.json",
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "model-integration/reports/tiny-transformer-report.json",
    "moe-routing-all-to-all/moe-routing-report.json",
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sample_inputs() -> tuple[torch.Tensor, torch.Tensor]:
    torch.manual_seed(911)
    x = torch.randn(384, 256, dtype=torch.float32) * 0.25
    w = torch.randn(256, 192, dtype=torch.float32) * 0.20
    x[::29] += 3.0
    w[::31] -= 2.0
    return x, w


def _fp8_like(x: torch.Tensor) -> torch.Tensor:
    clipped = torch.clamp(x, -448.0, 448.0)
    sign = torch.sign(clipped)
    mag = torch.clamp(clipped.abs(), min=2**-6)
    exponent = torch.floor(torch.log2(mag)).clamp(-6, 7)
    step = torch.pow(torch.tensor(2.0), exponent - 3)
    return sign * torch.round(mag / step) * step


def _tf32_like(x: torch.Tensor) -> torch.Tensor:
    scale = 2.0**13
    return torch.round(x * scale) / scale


def _reversed_reduce_matmul(x: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    out = torch.zeros(x.shape[0], w.shape[1], dtype=torch.float32)
    for idx in range(x.shape[1] - 1, -1, -1):
        out += x[:, idx : idx + 1] * w[idx : idx + 1, :]
    return out


def _max_abs(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a - b).abs().max().item())


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(torch.nn.functional.cosine_similarity(a.flatten(), b.flatten(), dim=0).item())


def _repeatability(fn: Callable[[], torch.Tensor], reference: torch.Tensor, repeats: int = 5) -> dict[str, Any]:
    outputs = [fn() for _ in range(repeats)]
    drift = max(_max_abs(outputs[0], out) for out in outputs[1:])
    ref_error = _max_abs(reference, outputs[0])
    return {
        "repeat_count": repeats,
        "repeat_max_abs_drift": round(drift, 10),
        "reference_max_abs_error": round(ref_error, 8),
        "cosine_similarity": round(_cosine(reference, outputs[0]), 8),
    }


def _scenario(mode: str, x: torch.Tensor, w: torch.Tensor, reference: torch.Tensor) -> dict[str, Any]:
    if mode == "fp32-deterministic":
        fn = lambda: x @ w
        tolerance = 1e-6
        category = "strict"
    elif mode == "fp32-reversed-reduction":
        fn = lambda: _reversed_reduce_matmul(x, w)
        tolerance = 1e-4
        category = "order-sensitive"
    elif mode == "tf32-like":
        fn = lambda: _tf32_like(x) @ _tf32_like(w)
        tolerance = 5e-3
        category = "fast-math"
    elif mode == "bf16-like":
        fn = lambda: x.to(torch.bfloat16).to(torch.float32) @ w.to(torch.bfloat16).to(torch.float32)
        tolerance = 2e-1
        category = "low-precision"
    elif mode == "fp8-like":
        fn = lambda: _fp8_like(x) @ _fp8_like(w)
        tolerance = 2.0
        category = "calibration-required"
    else:
        raise ValueError(mode)
    repeat = _repeatability(fn, reference)
    passed = repeat["repeat_max_abs_drift"] <= tolerance and repeat["reference_max_abs_error"] <= tolerance
    return {
        "mode": mode,
        "category": category,
        "status": "passed" if passed else "tolerance-review",
        "tolerance": tolerance,
        **repeat,
        "determinism_policy": "bitwise-repeatable" if repeat["repeat_max_abs_drift"] == 0 else "tolerance-bounded",
    }


def _reduction_order() -> dict[str, Any]:
    torch.manual_seed(1234)
    values = torch.randn(1_000_000, dtype=torch.float32) * 0.001
    values[::997] += 1.0
    left = values.sum()
    right = torch.flip(values, dims=[0]).sum()
    pairwise = values.reshape(1000, 1000).sum(dim=1).sum()
    max_delta = max(float((left - right).abs().item()), float((left - pairwise).abs().item()), float((right - pairwise).abs().item()))
    return {
        "case": "parallel-reduction-order",
        "status": "passed" if max_delta <= 1e-3 else "tolerance-review",
        "left_sum": round(float(left.item()), 8),
        "right_sum": round(float(right.item()), 8),
        "pairwise_sum": round(float(pairwise.item()), 8),
        "max_order_delta": round(max_delta, 10),
        "tolerance": 1e-3,
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "quantization_formats": reports.get(SOURCE_REPORTS[0], {}).get("format_count", 0),
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[1], {}).get("benchmark_count", 0),
        "model_cases": reports.get(SOURCE_REPORTS[2], {}).get("case_count", 0),
        "moe_scenarios": reports.get(SOURCE_REPORTS[3], {}).get("scenario_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Numerical Reproducibility",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| mode | category | status | tolerance | repeat drift | reference error | cosine |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['mode']} | {row['category']} | {row['status']} | {row['tolerance']} | "
            f"{row['repeat_max_abs_drift']} | {row['reference_max_abs_error']} | {row['cosine_similarity']} |"
        )
    red = report["reduction_order"]
    lines.extend(
        [
            "",
            "## Reduction Order",
            "",
            f"- max order delta: `{red['max_order_delta']}`",
            f"- status: `{red['status']}`",
            "",
            "## GPU Host Promotion",
            "",
        ]
    )
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_numerical_reproducibility_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    x, w = _sample_inputs()
    reference = x @ w
    scenarios = [_scenario(mode, x, w, reference) for mode in ["fp32-deterministic", "fp32-reversed-reduction", "tf32-like", "bf16-like", "fp8-like"]]
    reduction_order = _reduction_order()
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    reviews = sum(1 for row in scenarios if row["status"] == "tolerance-review")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "reproducibility-ready" if passed >= 4 and reviews >= 1 and reduction_order["status"] == "passed" else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "tolerance_review_scenarios": reviews,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "reduction_order": reduction_order,
        "recommendations": [
            "Define per-kernel tolerances by precision mode instead of using one global epsilon.",
            "Keep strict repeatability checks separate from reference-accuracy checks.",
            "Treat fast-math and FP8-style modes as calibration-required until measured against model-level acceptance.",
            "Promote on CUDA and ROCm hosts with deterministic flags, profiler traces, and repeated seed runs.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["cuda-deterministic-reductions", "triton-fast-math-drift", "rocm-repeatability", "model-tolerance-gate"],
            "commands": [
                "CUBLAS_WORKSPACE_CONFIG=:4096:8 python3 scripts/run_numerical_reproducibility.py",
                "NVIDIA_TF32_OVERRIDE=0 python3 scripts/verify_numerical_reproducibility.py",
                "HIP_VISIBLE_DEVICES=0 python3 scripts/run_numerical_reproducibility.py",
                "nsys profile -o numerical-reproducibility python3 <precision_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id numerical-reproducibility --execute",
            ],
            "note": "Local CPU checks validate tolerance policy; real acceptance requires repeated CUDA/ROCm/Triton runs and model-level drift checks on accelerator hosts.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
