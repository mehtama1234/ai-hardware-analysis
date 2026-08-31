from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "compiler-runtime-inspection"
REPORT_JSON = OUT / "compiler-runtime-report.json"
REPORT_MD = OUT / "reports" / "compiler-runtime-report.md"


SOURCE_GROUPS = {
    "cuda": ROOT / "kernel-benchmarks" / "kernels" / "cuda",
    "triton": ROOT / "kernel-benchmarks" / "kernels" / "triton",
    "custom-op": ROOT / "custom-ops" / "csrc",
    "hip": ROOT / "programming-projects" / "rocm-hip-port",
}


FEATURE_PATTERNS = {
    "global_kernel": re.compile(r"__global__|triton\.jit|@triton\.jit"),
    "shared_memory": re.compile(r"__shared__|tl\.make_block_ptr|shared", re.IGNORECASE),
    "barrier": re.compile(r"__syncthreads|tl\.debug_barrier|barrier", re.IGNORECASE),
    "vectorized_load": re.compile(r"float4|int4|tl\.load|reinterpret_cast", re.IGNORECASE),
    "tensor_core_hint": re.compile(r"wmma|mma|dot|tl\.dot|tensor", re.IGNORECASE),
    "launch_indexing": re.compile(r"blockIdx|threadIdx|program_id|hipBlockIdx|hipThreadIdx"),
    "bounds_mask": re.compile(r"if\s*\(|mask=|where\(|boundary_check", re.IGNORECASE),
    "atomic": re.compile(r"atomic|tl\.atomic", re.IGNORECASE),
}


RISK_RULES = [
    ("missing_bounds_mask", "source has kernel launch indexing but no visible bounds/mask guard"),
    ("barrier_without_shared_memory", "barrier appears without an obvious shared-memory or block-pointer use"),
    ("tensor_core_without_shape_contract", "tensor-core hint appears without an explicit tile or shape contract"),
    ("no_runtime_validation_command", "source group lacks a concrete GPU-host validation command"),
]


PROMOTION_COMMANDS = {
    "cuda": [
        "nvcc -O3 --ptx kernel-benchmarks/kernels/cuda/memory.cu -o /tmp/gpumode-memory.ptx",
        "ncu --set full python3 scripts/run_kernel_benchmarks.py",
    ],
    "triton": [
        "TRITON_KERNEL_DUMP=1 python3 scripts/run_kernel_benchmarks.py",
        "python3 scripts/build_autotune_db.py",
    ],
    "custom-op": [
        "python3 scripts/run_custom_ops.py",
        "nsys profile python3 scripts/run_model_integration.py",
    ],
    "hip": [
        "hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port",
        "rocprof /tmp/rocm-hip-port",
    ],
}


@dataclass
class SourceRow:
    group: str
    path: str
    lines: int
    features: dict[str, bool]
    risk_ids: list[str]
    promotion_commands: list[str]


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for group, root in SOURCE_GROUPS.items():
        if not root.exists():
            continue
        for path in sorted(root.iterdir()):
            if path.suffix in {".cu", ".py", ".cpp"} or path.name.endswith(".hip.cpp"):
                files.append((group, path))
    return files


def inspect_source(group: str, path: Path) -> SourceRow:
    text = path.read_text(encoding="utf-8")
    features = {name: bool(pattern.search(text)) for name, pattern in FEATURE_PATTERNS.items()}
    risks = []
    if features["launch_indexing"] and not features["bounds_mask"]:
        risks.append("missing_bounds_mask")
    if features["barrier"] and not features["shared_memory"]:
        risks.append("barrier_without_shared_memory")
    if features["tensor_core_hint"] and not re.search(r"tile|block|shape|BLOCK|MMA|wmma", text):
        risks.append("tensor_core_without_shape_contract")
    if not PROMOTION_COMMANDS.get(group):
        risks.append("no_runtime_validation_command")
    return SourceRow(
        group=group,
        path=str(path.relative_to(ROOT)),
        lines=len(text.splitlines()),
        features=features,
        risk_ids=risks,
        promotion_commands=PROMOTION_COMMANDS.get(group, []),
    )


def summarize(rows: list[SourceRow]) -> dict[str, Any]:
    groups = sorted({row.group for row in rows})
    feature_counts = {
        name: sum(1 for row in rows if row.features.get(name))
        for name in FEATURE_PATTERNS
    }
    risk_counts: dict[str, int] = {}
    for row in rows:
        for risk in row.risk_ids:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
    return {
        "source_count": len(rows),
        "group_count": len(groups),
        "groups": groups,
        "feature_counts": feature_counts,
        "risk_counts": risk_counts,
        "promotion_command_count": sum(len(row.promotion_commands) for row in rows),
    }


def build_compiler_runtime_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    rows = [inspect_source(group, path) for group, path in source_files()]
    summary = summarize(rows)
    required_groups = {"cuda", "triton", "custom-op", "hip"}
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "inspection-ready" if summary["source_count"] >= 10 and required_groups.issubset(summary["groups"]) else "incomplete",
        **summary,
        "risk_rules": [{"id": risk_id, "description": description} for risk_id, description in RISK_RULES],
        "source_rows": [
            {
                "group": row.group,
                "path": row.path,
                "lines": row.lines,
                "features": row.features,
                "risk_ids": row.risk_ids,
                "promotion_commands": row.promotion_commands,
            }
            for row in rows
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["cuda-kernel-compile", "triton-kernel-sweep", "torch-custom-extension", "rocm-hip-port", "profiler-capture"],
            "note": "Static inspection identifies source-level compiler/runtime risks; final acceptance requires PTX/LLVM/profiler evidence from a GPU host.",
        },
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Compiler Runtime Inspection",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Sources: `{report['source_count']}`",
        f"Groups: `{', '.join(report['groups'])}`",
        "",
        "## Feature Counts",
        "",
        "| feature | sources |",
        "|---|---:|",
    ]
    for name, count in report["feature_counts"].items():
        lines.append(f"| {name} | {count} |")
    lines.extend(["", "## Source Rows", "", "| group | path | lines | risks | promotion commands |", "|---|---|---:|---|---|"])
    for row in report["source_rows"]:
        risks = ", ".join(row["risk_ids"]) or "none"
        commands = "<br>".join(row["promotion_commands"][:2])
        lines.append(f"| {row['group']} | `{row['path']}` | {row['lines']} | {risks} | {commands} |")
    lines.extend(["", "## GPU Host Promotion", "", report["gpu_host_promotion"]["note"]])
    return "\n".join(lines).rstrip() + "\n"
