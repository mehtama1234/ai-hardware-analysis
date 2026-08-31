from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import torch


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "quantization-memory-formats"
REPORT_JSON = OUT / "quantization-report.json"
REPORT_MD = OUT / "reports" / "quantization-report.md"

SOURCE_REPORTS = [
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "model-integration/reports/tiny-transformer-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "hardware-capacity-planning/hardware-capacity-plan.json",
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sample_weight() -> torch.Tensor:
    torch.manual_seed(17)
    rows = torch.linspace(-2.5, 2.5, 192).unsqueeze(1)
    cols = torch.linspace(-1.5, 1.5, 256).unsqueeze(0)
    structured = torch.sin(rows * 1.7) + torch.cos(cols * 2.3)
    noise = torch.randn(192, 256) * 0.05
    outliers = torch.zeros_like(structured)
    outliers[::37, ::41] = 4.0
    return (structured + noise + outliers).to(torch.float32)


def _workload_input() -> torch.Tensor:
    torch.manual_seed(23)
    return torch.randn(128, 256, dtype=torch.float32)


def _fp8_e4m3(x: torch.Tensor) -> torch.Tensor:
    clipped = torch.clamp(x, -448.0, 448.0)
    signs = torch.sign(clipped)
    magnitude = torch.clamp(clipped.abs(), min=2**-6)
    exponent = torch.floor(torch.log2(magnitude)).clamp(-6, 7)
    step = torch.pow(torch.tensor(2.0), exponent - 3)
    quantized = torch.round(magnitude / step) * step
    return signs * quantized


def _int8_per_tensor(x: torch.Tensor) -> torch.Tensor:
    scale = torch.clamp(x.abs().max() / 127.0, min=1e-8)
    q = torch.round(x / scale).clamp(-127, 127)
    return q * scale


def _int8_per_channel(x: torch.Tensor) -> torch.Tensor:
    scale = torch.clamp(x.abs().amax(dim=1, keepdim=True) / 127.0, min=1e-8)
    q = torch.round(x / scale).clamp(-127, 127)
    return q * scale


NF4_CODEBOOK = torch.tensor(
    [-1.0, -0.696, -0.525, -0.394, -0.284, -0.184, -0.091, 0.0, 0.079, 0.160, 0.246, 0.337, 0.441, 0.563, 0.723, 1.0],
    dtype=torch.float32,
)


def _nf4_weight_only(x: torch.Tensor) -> torch.Tensor:
    scale = torch.clamp(x.abs().amax(dim=1, keepdim=True), min=1e-8)
    normalized = (x / scale).clamp(-1.0, 1.0)
    distances = (normalized.unsqueeze(-1) - NF4_CODEBOOK.to(x.device)).abs()
    q = distances.argmin(dim=-1)
    return NF4_CODEBOOK.to(x.device)[q] * scale


def _int4_symmetric(x: torch.Tensor) -> torch.Tensor:
    scale = torch.clamp(x.abs().amax(dim=1, keepdim=True) / 7.0, min=1e-8)
    q = torch.round(x / scale).clamp(-7, 7)
    return q * scale


FORMATS: list[dict[str, Any]] = [
    {"id": "fp32-reference", "bits": 32, "kind": "floating", "quantize": lambda x: x.clone()},
    {"id": "bf16-activation", "bits": 16, "kind": "floating", "quantize": lambda x: x.to(torch.bfloat16).to(torch.float32)},
    {"id": "fp8-e4m3-sim", "bits": 8, "kind": "floating", "quantize": _fp8_e4m3},
    {"id": "int8-per-tensor", "bits": 8, "kind": "integer", "quantize": _int8_per_tensor},
    {"id": "int8-per-channel", "bits": 8, "kind": "integer", "quantize": _int8_per_channel},
    {"id": "int4-symmetric", "bits": 4, "kind": "integer", "quantize": _int4_symmetric},
    {"id": "nf4-weight-only", "bits": 4, "kind": "codebook", "quantize": _nf4_weight_only},
]


def _time_call(fn: Callable[[], torch.Tensor], repeats: int = 6) -> tuple[torch.Tensor, float]:
    result = fn()
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        times.append(time.perf_counter() - start)
    return result, float(sorted(times)[len(times) // 2])


def _cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(torch.nn.functional.cosine_similarity(a.flatten(), b.flatten(), dim=0).item())


def _analyze_format(fmt: dict[str, Any], weight: torch.Tensor, inputs: torch.Tensor, reference_output: torch.Tensor) -> dict[str, Any]:
    quantized_weight, quant_seconds = _time_call(lambda: fmt["quantize"](weight))
    output, matmul_seconds = _time_call(lambda: inputs @ quantized_weight.T)
    error = output - reference_output
    raw_bytes = weight.numel() * 4
    payload_bytes = math.ceil(weight.numel() * fmt["bits"] / 8)
    scale_bytes = 0
    if "per-channel" in fmt["id"] or fmt["id"] in {"int4-symmetric", "nf4-weight-only"}:
        scale_bytes = weight.shape[0] * 4
    total_bytes = payload_bytes + scale_bytes
    compression = raw_bytes / total_bytes
    max_abs = float(error.abs().max().item())
    mse = float(torch.mean(error * error).item())
    cosine = _cosine(output, reference_output)
    pass_accuracy = max_abs <= 1.25 and mse <= 0.05 and cosine >= 0.999
    memory_bandwidth_gain = compression
    dequant_tax = quant_seconds / max(matmul_seconds, 1e-12)
    fused_speedup_proxy = max(0.1, memory_bandwidth_gain / (1.0 + min(dequant_tax, 4.0)))
    serving_fit = "best" if compression >= 4 and pass_accuracy else "good" if compression >= 2 and pass_accuracy else "debug-only"
    return {
        "format_id": fmt["id"],
        "kind": fmt["kind"],
        "bits": fmt["bits"],
        "payload_bytes": payload_bytes,
        "scale_bytes": scale_bytes,
        "total_bytes": total_bytes,
        "compression_vs_fp32": round(compression, 4),
        "max_abs_error": round(max_abs, 6),
        "mse": round(mse, 8),
        "cosine_similarity": round(cosine, 8),
        "quantize_seconds_median": round(quant_seconds, 8),
        "matmul_seconds_median": round(matmul_seconds, 8),
        "dequant_tax_ratio": round(dequant_tax, 4),
        "fused_speedup_proxy": round(fused_speedup_proxy, 4),
        "serving_fit": serving_fit,
        "status": "passed" if pass_accuracy else "needs-calibration",
    }


def _recommendations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row["format_id"]: row for row in rows}
    return [
        {
            "scenario": "debug-correctness",
            "recommended_format": "bf16-activation",
            "why": "Preserves high cosine similarity while cutting payload bytes in half for activation-oriented checks.",
            "facts": by_id.get("bf16-activation", {}),
        },
        {
            "scenario": "interactive-serving",
            "recommended_format": "int8-per-channel",
            "why": "Balances 4x weight compression with low output drift and avoids the larger dequantization tax of 4-bit formats.",
            "facts": by_id.get("int8-per-channel", {}),
        },
        {
            "scenario": "memory-constrained-serving",
            "recommended_format": "nf4-weight-only",
            "why": "Maximizes memory compression for serving when a fused dequantization kernel can hide the codebook lookup cost.",
            "facts": by_id.get("nf4-weight-only", {}),
        },
        {
            "scenario": "tensor-core-kernel-promotion",
            "recommended_format": "fp8-e4m3-sim",
            "why": "Models FP8-style range and mantissa pressure before promoting to hardware-specific tensor-core kernels.",
            "facts": by_id.get("fp8-e4m3-sim", {}),
        },
    ]


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[0], {}).get("benchmark_count", 0),
        "model_cases": reports.get(SOURCE_REPORTS[1], {}).get("case_count", 0),
        "serving_engines": reports.get(SOURCE_REPORTS[2], {}).get("engine_count", 0),
        "hardware_profiles": reports.get(SOURCE_REPORTS[3], {}).get("profile_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Quantization And Memory Formats",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "## Format Sweep",
        "",
        "| format | bits | compression | max abs error | cosine | dequant tax | speedup proxy | serving fit | status |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["formats"]:
        lines.append(
            f"| {row['format_id']} | {row['bits']} | {row['compression_vs_fp32']} | {row['max_abs_error']} | "
            f"{row['cosine_similarity']} | {row['dequant_tax_ratio']} | {row['fused_speedup_proxy']} | {row['serving_fit']} | {row['status']} |"
        )
    lines.extend(["", "## Recommendations", ""])
    for rec in report["recommendations"]:
        lines.append(f"- `{rec['scenario']}`: `{rec['recommended_format']}` - {rec['why']}")
    lines.extend(["", "## GPU Promotion Commands", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_quantization_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    weight = _sample_weight()
    inputs = _workload_input()
    reference_output = inputs @ weight.T
    rows = [_analyze_format(fmt, weight, inputs, reference_output) for fmt in FORMATS]
    source_reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    passed = sum(1 for row in rows if row["status"] == "passed")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "quantization-ready" if len(rows) >= 7 and passed >= 4 else "needs-work",
        "format_count": len(rows),
        "passed_format_count": passed,
        "calibration_needed_count": len(rows) - passed,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(source_reports),
        "shape": {"input_tokens": inputs.shape[0], "in_features": weight.shape[1], "out_features": weight.shape[0]},
        "formats": rows,
        "recommendations": _recommendations(rows),
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["quantized-kernel", "tensor-core-fp8", "serving-engine-quantization", "profiler-evidence"],
            "commands": [
                "python3 scripts/run_gpu_host_preflight.py",
                "nvidia-smi --query-gpu=name,memory.total,power.draw --format=csv",
                "python3 scripts/run_gpu_promotion_suite.py --run-id quantization-memory --execute",
                "vllm serve <model> --quantization <awq|gptq|fp8> --max-model-len <tokens>",
                "ncu --set full -o quantization-memory python3 <quantized_kernel_probe.py>",
                "nsys profile -o quantization-serving python3 <serving_quant_probe.py>",
            ],
            "note": "Local CPU simulation proves math and report wiring; final speedup claims require fused GPU dequantization kernels and measured serving throughput.",
        },
    }
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
