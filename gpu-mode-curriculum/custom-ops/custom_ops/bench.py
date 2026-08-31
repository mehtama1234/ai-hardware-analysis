from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

import torch

from .fused_bias_gelu_residual import fused_bias_gelu_residual, reference_bias_gelu_residual


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "custom-op-report.json"
REPORT_MD = ROOT / "reports" / "custom-op-report.md"


@dataclass(frozen=True)
class ShapeCase:
    name: str
    batch: int
    hidden: int
    dtype: str


SHAPES = [
    ShapeCase("small-mlp", 4, 128, "float32"),
    ShapeCase("decoder-hidden", 8, 768, "float32"),
    ShapeCase("wide-ffn", 16, 3072, "float32"),
    ShapeCase("bf16-transformer", 8, 1024, "bfloat16"),
]


def _dtype(name: str) -> torch.dtype:
    return {"float32": torch.float32, "bfloat16": torch.bfloat16}[name]


def _make_tensors(case: ShapeCase, seed: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    dtype = _dtype(case.dtype)
    x = torch.randn((case.batch, case.hidden), generator=generator, dtype=torch.float32).to(dtype).requires_grad_(True)
    bias = torch.randn((case.hidden,), generator=generator, dtype=torch.float32).to(dtype).requires_grad_(True)
    residual = torch.randn((case.batch, case.hidden), generator=generator, dtype=torch.float32).to(dtype).requires_grad_(True)
    return x, bias, residual


def _time_call(fn: Any, x: torch.Tensor, bias: torch.Tensor, residual: torch.Tensor, repeats: int) -> dict[str, float]:
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        out = fn(x, bias, residual)
        loss = out.float().sum()
        loss.backward()
        timings.append(time.perf_counter() - start)
        for tensor in (x, bias, residual):
            tensor.grad = None
    return {"median": median(timings), "min": min(timings), "max": max(timings)}


def run_case(case: ShapeCase, seed: int, repeats: int) -> dict[str, Any]:
    x_ref, bias_ref, residual_ref = _make_tensors(case, seed)
    x_fused = x_ref.detach().clone().requires_grad_(True)
    bias_fused = bias_ref.detach().clone().requires_grad_(True)
    residual_fused = residual_ref.detach().clone().requires_grad_(True)

    ref = reference_bias_gelu_residual(x_ref, bias_ref, residual_ref)
    fused = fused_bias_gelu_residual(x_fused, bias_fused, residual_fused)
    grad_seed = torch.ones_like(ref)
    ref.backward(grad_seed)
    fused.backward(grad_seed)

    atol = 4e-2 if case.dtype == "bfloat16" else 2e-5
    rtol = 4e-2 if case.dtype == "bfloat16" else 2e-5
    output_close = torch.allclose(ref.float(), fused.float(), atol=atol, rtol=rtol)
    grad_x_close = torch.allclose(x_ref.grad.float(), x_fused.grad.float(), atol=atol, rtol=rtol)
    grad_bias_close = torch.allclose(bias_ref.grad.float(), bias_fused.grad.float(), atol=atol, rtol=rtol)
    grad_residual_close = torch.allclose(residual_ref.grad.float(), residual_fused.grad.float(), atol=atol, rtol=rtol)

    x_bench, bias_bench, residual_bench = _make_tensors(case, seed + 1000)
    fused_timing = _time_call(fused_bias_gelu_residual, x_bench, bias_bench, residual_bench, repeats)
    x_bench, bias_bench, residual_bench = _make_tensors(case, seed + 2000)
    reference_timing = _time_call(reference_bias_gelu_residual, x_bench, bias_bench, residual_bench, repeats)

    elements = case.batch * case.hidden
    checks = {
        "output_close": bool(output_close),
        "grad_x_close": bool(grad_x_close),
        "grad_bias_close": bool(grad_bias_close),
        "grad_residual_close": bool(grad_residual_close),
        "finite_output": bool(torch.isfinite(fused.float()).all().item()),
    }
    return {
        "id": case.name,
        "shape": {"batch": case.batch, "hidden": case.hidden, "elements": elements},
        "dtype": case.dtype,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "max_abs_error": float((ref.float() - fused.float()).abs().max().item()),
        "grad_x_max_abs_error": float((x_ref.grad.float() - x_fused.grad.float()).abs().max().item()),
        "seconds": {"fused": fused_timing, "reference": reference_timing},
        "elements_per_second": round(elements / max(fused_timing["median"], 1e-9), 4),
    }


def accelerator_readiness() -> dict[str, Any]:
    return {
        "torch_version": torch.__version__,
        "torch_device": "cuda" if torch.cuda.is_available() else "cpu",
        "cuda_available": bool(torch.cuda.is_available()),
        "nvcc": bool(shutil.which("nvcc")),
        "ninja": bool(shutil.which("ninja")),
        "compiled_extension_status": "cuda-ready" if torch.cuda.is_available() and shutil.which("nvcc") else "source-only",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# PyTorch Custom Op Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Compiled extension status: `{report['accelerator_readiness']['compiled_extension_status']}`",
        "",
        "| case | dtype | shape | status | max abs error | grad x error | fused median s | elements/s |",
        "|---|---|---:|---|---:|---:|---:|---:|",
    ]
    for case in report["cases"]:
        shape = f"{case['shape']['batch']}x{case['shape']['hidden']}"
        lines.append(
            "| "
            f"{case['id']} | {case['dtype']} | {shape} | {case['status']} | "
            f"{case['max_abs_error']:.6g} | {case['grad_x_max_abs_error']:.6g} | "
            f"{case['seconds']['fused']['median']:.8f} | {case['elements_per_second']} |"
        )
    lines.extend(["", "## Source Promotion", ""])
    lines.append("- `custom-ops/csrc/fused_bias_gelu_residual.cpp` defines the PyTorch extension binding.")
    lines.append("- `custom-ops/csrc/fused_bias_gelu_residual_kernel.cu` contains the CUDA kernel skeleton and launcher contract.")
    lines.append("- Local CPU fallback verifies forward and backward numerics before accelerator promotion.")
    return "\n".join(lines).rstrip() + "\n"


def run_all(repeats: int = 5) -> dict[str, Any]:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    cases = [run_case(case, seed=1337 + index, repeats=repeats) for index, case in enumerate(SHAPES)]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(cases),
        "passed": sum(1 for case in cases if case["status"] == "passed"),
        "failed": sum(1 for case in cases if case["status"] != "passed"),
        "operator": "fused_bias_gelu_residual",
        "accelerator_readiness": accelerator_readiness(),
        "cases": cases,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
