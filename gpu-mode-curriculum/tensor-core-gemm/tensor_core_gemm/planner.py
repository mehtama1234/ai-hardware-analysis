from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tensor-core-gemm"
REPORT_JSON = OUT / "tensor-core-gemm-report.json"
REPORT_MD = OUT / "reports" / "tensor-core-gemm-report.md"

SOURCE_REPORTS = [
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "compiler-runtime-inspection/compiler-runtime-report.json",
    "autotune-db/autotune-db.json",
    "quantization-memory-formats/quantization-report.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
]


@dataclass(frozen=True)
class GemmScenario:
    scenario_id: str
    m: int
    n: int
    k: int
    dtype: str
    bytes_per_operand: int
    cta_m: int
    cta_n: int
    cta_k: int
    warp_m: int
    warp_n: int
    warp_k: int
    mma_m: int
    mma_n: int
    mma_k: int
    stages: int
    epilogue: str


SCENARIOS = [
    GemmScenario("bf16-mlp-up-projection", 4096, 11008, 4096, "bf16", 2, 128, 128, 64, 64, 64, 64, 16, 8, 16, 3, "bias-gelu"),
    GemmScenario("fp16-attention-qkv", 8192, 3072, 4096, "fp16", 2, 128, 128, 64, 64, 64, 64, 16, 8, 16, 3, "bias"),
    GemmScenario("int8-weight-only-decode", 256, 4096, 4096, "int8", 1, 64, 128, 64, 32, 64, 64, 16, 8, 32, 4, "dequant-bias"),
    GemmScenario("fp8-training-gemm", 4096, 4096, 4096, "fp8", 1, 128, 128, 128, 64, 64, 64, 16, 8, 32, 4, "amax-scale"),
    GemmScenario("small-batch-lora", 64, 4096, 512, "bf16", 2, 64, 64, 64, 32, 32, 64, 16, 8, 16, 2, "residual-add"),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def _tile_count(row: GemmScenario) -> int:
    return _ceil_div(row.m, row.cta_m) * _ceil_div(row.n, row.cta_n) * _ceil_div(row.k, row.cta_k)


def _shared_memory_bytes(row: GemmScenario) -> int:
    a_tile = row.cta_m * row.cta_k * row.bytes_per_operand
    b_tile = row.cta_k * row.cta_n * row.bytes_per_operand
    return (a_tile + b_tile) * row.stages


def _tensor_core_eligible(row: GemmScenario) -> bool:
    return row.mma_m in {16, 32} and row.mma_n in {8, 16} and row.mma_k in {16, 32, 64} and row.k % row.mma_k == 0


def _register_pressure_proxy(row: GemmScenario) -> int:
    accum = row.warp_m * row.warp_n // 32
    operands = (row.warp_m * row.warp_k + row.warp_k * row.warp_n) // 64
    epilogue = 8 if row.epilogue in {"bias-gelu", "dequant-bias", "amax-scale"} else 4
    return accum + operands + epilogue


def _occupancy_proxy(row: GemmScenario) -> float:
    smem_factor = min(1.0, 164 * 1024 / max(_shared_memory_bytes(row), 1))
    reg_factor = min(1.0, 96 / max(_register_pressure_proxy(row), 1))
    stage_factor = 0.95 if row.stages <= 4 else 0.80
    return round(0.40 + 0.35 * smem_factor + 0.20 * reg_factor + 0.05 * stage_factor, 4)


def _arithmetic_intensity(row: GemmScenario) -> float:
    flops = 2 * row.m * row.n * row.k
    hbm = (row.m * row.k + row.k * row.n) * row.bytes_per_operand + row.m * row.n * 4
    return round(flops / max(hbm, 1), 4)


def _scenario(row: GemmScenario) -> dict[str, Any]:
    smem = _shared_memory_bytes(row)
    registers = _register_pressure_proxy(row)
    eligible = _tensor_core_eligible(row)
    occupancy = _occupancy_proxy(row)
    intensity = _arithmetic_intensity(row)
    epilogue_fused = row.epilogue != "none"
    passed = eligible and smem <= 164 * 1024 and registers <= 288 and occupancy >= 0.65
    return {
        "scenario_id": row.scenario_id,
        "status": "passed" if passed else "tuning-required",
        "shape": {"m": row.m, "n": row.n, "k": row.k, "dtype": row.dtype, "bytes_per_operand": row.bytes_per_operand},
        "cta_tile": {"m": row.cta_m, "n": row.cta_n, "k": row.cta_k},
        "warp_tile": {"m": row.warp_m, "n": row.warp_n, "k": row.warp_k},
        "mma_shape": {"m": row.mma_m, "n": row.mma_n, "k": row.mma_k},
        "pipeline_stages": row.stages,
        "epilogue": row.epilogue,
        "epilogue_fused": epilogue_fused,
        "tile_count": _tile_count(row),
        "shared_memory_bytes": smem,
        "register_pressure_proxy": registers,
        "tensor_core_eligible": eligible,
        "occupancy_proxy": occupancy,
        "arithmetic_intensity": intensity,
        "promotion_notes": [
            "Map this CTA/warp/MMA hierarchy to CUTLASS or CuTe layouts on GPU host.",
            "Inspect generated SASS for mma instructions and epilogue fusion.",
            "Compare against cuBLAS and Triton matmul for the same shape.",
        ],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[0], {}).get("benchmark_count", 0),
        "compiler_sources": reports.get(SOURCE_REPORTS[1], {}).get("source_count", 0),
        "autotune_records": reports.get(SOURCE_REPORTS[2], {}).get("record_count", 0),
        "quantization_formats": reports.get(SOURCE_REPORTS[3], {}).get("format_count", 0),
        "numerical_scenarios": reports.get(SOURCE_REPORTS[4], {}).get("scenario_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE CUTLASS CuTe Tensor Core GEMM",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | status | dtype | CTA | MMA | smem | regs | intensity | epilogue |",
        "|---|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        cta = row["cta_tile"]
        mma = row["mma_shape"]
        lines.append(
            f"| {row['scenario_id']} | {row['status']} | {row['shape']['dtype']} | "
            f"{cta['m']}x{cta['n']}x{cta['k']} | {mma['m']}x{mma['n']}x{mma['k']} | "
            f"{row['shared_memory_bytes']} | {row['register_pressure_proxy']} | {row['arithmetic_intensity']} | {row['epilogue']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_tensor_core_gemm_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    fused = sum(1 for row in scenarios if row["epilogue_fused"])
    tensor_core = sum(1 for row in scenarios if row["tensor_core_eligible"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "tensor-core-gemm-ready" if passed >= 4 and tensor_core >= 5 and fused >= 4 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "tensor_core_eligible_scenarios": tensor_core,
        "fused_epilogue_scenarios": fused,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach GEMM as CTA tile, warp tile, MMA instruction shape, pipeline stage count, and epilogue as one design object.",
            "Treat quantized GEMM as a memory-format and epilogue problem, not just a smaller dtype.",
            "Use CuTe/CUTLASS layout reasoning before writing handwritten inline PTX or WMMA fragments.",
            "Promote with cuBLAS, CUTLASS/CuTe, Triton, Nsight Compute, and numerical drift evidence on a GPU host.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["cutlass-build", "cute-layout-check", "tensor-core-sass", "cublas-baseline", "triton-baseline"],
            "commands": [
                "python3 scripts/run_gpu_host_preflight.py",
                "python3 scripts/run_tensor_core_gemm.py",
                "python3 scripts/verify_tensor_core_gemm.py",
                "ncu --set full -o tensor-core-gemm python3 <cutlass_gemm_probe.py>",
                "cuobjdump --dump-sass <cutlass_gemm_binary> | rg -i 'mma|wgmma'",
                "python3 scripts/run_gpu_promotion_suite.py --run-id tensor-core-gemm --execute",
            ],
            "note": "Local planner validates GEMM design constraints; final acceptance needs real CUTLASS/CuTe build, profiler counters, and cuBLAS/Triton comparisons.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
