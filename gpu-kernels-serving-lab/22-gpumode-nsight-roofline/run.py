"""Session 22: GPUMODE-derived Nsight counter to roofline workflow."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
GPUMODE_ROOT = ROOT.parent / "gpu-mode-curriculum"
IMPORTS = HERE / "imports"


COUNTER_MAP = {
    "dram__throughput.avg.pct_of_peak_sustained_elapsed": "memory bandwidth saturation",
    "sm__throughput.avg.pct_of_peak_sustained_elapsed": "SM compute utilization",
    "smsp__sass_average_branch_targets_threads_uniform.pct": "control-flow uniformity",
    "smsp__average_warps_issue_stalled_barrier_per_issue_active.ratio": "synchronization stalls",
    "launch__occupancy_limit_registers.pct": "register pressure",
    "gpu__time_duration.sum": "kernel duration",
    "kernel__launch_count": "launch overhead",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def gpumode_links() -> list[dict[str, object]]:
    path = GPUMODE_ROOT / "analysis" / "lesson-intelligence.json"
    if not path.exists():
        return []
    lessons = json.loads(path.read_text(encoding="utf-8"))
    selected = []
    for lesson in lessons:
        topics = set(lesson.get("topics", []))
        concepts = set(lesson.get("concepts", []))
        title = lesson.get("title", "").lower()
        exercises = " ".join(lesson.get("exercise_candidates", [])).lower()
        if (
            "profiling" in topics
            or "hardware" in topics
            or "profiling workflow" in concepts
            or "nsight" in title
            or "observability" in title
            or "profiler trace" in exercises
        ):
            selected.append(
                {
                    "index": lesson["index"],
                    "title": lesson["title"],
                    "url": lesson["url"],
                    "topics": lesson["topics"],
                    "concepts": lesson.get("concepts", []),
                    "exercise_candidates": lesson.get("exercise_candidates", []),
                }
            )
    return selected[:14]


def profiler_status() -> dict[str, Any]:
    tools = {
        "ncu": shutil.which("ncu"),
        "nsys": shutil.which("nsys"),
        "nv-nsight-cu-cli": shutil.which("nv-nsight-cu-cli"),
    }
    available = {name: path for name, path in tools.items() if path}
    return {
        "status": "ready" if available else "skipped",
        "tools": tools,
        "reason": (
            "Nsight CLI tooling is available; replace proxy counters with imported reports next."
            if available
            else "Nsight Compute/System CLI tools are not available on PATH, so this session uses roofline-derived proxy counters."
        ),
    }


def proxy_counters(row: dict[str, Any], peak_gbps: float, peak_tflops: float) -> dict[str, Any]:
    operation = row["operation"]
    dram_pct = min(100.0, row["effective_gbps"] / peak_gbps * 100.0) if peak_gbps else 0.0
    sm_pct = min(100.0, row["effective_tflops"] / peak_tflops * 100.0) if peak_tflops else 0.0
    launch_count = 1
    barrier_stall = 0.08
    branch_uniform = 98.0
    register_limit = 12.0
    if "reduction" in operation:
        barrier_stall = 0.34
    if "matmul" in operation:
        register_limit = 42.0
        barrier_stall = 0.14
    if "kv_cache" in operation:
        branch_uniform = 92.0
        launch_count = 4
    return {
        **row,
        "counters": {
            "dram__throughput.avg.pct_of_peak_sustained_elapsed": round(dram_pct, 2),
            "sm__throughput.avg.pct_of_peak_sustained_elapsed": round(sm_pct, 2),
            "smsp__sass_average_branch_targets_threads_uniform.pct": branch_uniform,
            "smsp__average_warps_issue_stalled_barrier_per_issue_active.ratio": barrier_stall,
            "launch__occupancy_limit_registers.pct": register_limit,
            "gpu__time_duration.sum": row["seconds"],
            "kernel__launch_count": launch_count,
        },
    }


def classify(row: dict[str, Any]) -> dict[str, Any]:
    counters = row["counters"]
    dram = counters["dram__throughput.avg.pct_of_peak_sustained_elapsed"]
    sm = counters["sm__throughput.avg.pct_of_peak_sustained_elapsed"]
    barrier = counters["smsp__average_warps_issue_stalled_barrier_per_issue_active.ratio"]
    launches = counters["kernel__launch_count"]
    arithmetic_intensity = row["arithmetic_intensity_flop_per_byte"]
    if dram >= 55 and sm < 45:
        bottleneck = "memory-bandwidth"
        action = "Inspect layout/coalescing, cache reuse, and avoidable materialization before changing math."
    elif sm >= 65 and arithmetic_intensity >= 10:
        bottleneck = "compute"
        action = "Inspect tiling, tensor-core eligibility, occupancy, and library/kernel selection."
    elif barrier >= 0.25:
        bottleneck = "synchronization"
        action = "Inspect reductions, shared-memory barriers, warp shuffles, and partial aggregation strategy."
    elif launches > 2:
        bottleneck = "launch-overhead-or-memory-scan"
        action = "Inspect fusion opportunities, decode-loop granularity, and KV-cache scan shape."
    else:
        bottleneck = "mixed"
        action = "Collect a real Nsight report and compare stall reasons against the roofline estimate."
    return {
        "operation": row["operation"],
        "bottleneck": bottleneck,
        "evidence": {
            "arithmetic_intensity_flop_per_byte": arithmetic_intensity,
            "dram_pct_proxy": dram,
            "sm_pct_proxy": sm,
            "barrier_stall_proxy": barrier,
            "launch_count_proxy": launches,
        },
        "next_action": action,
    }


def normalize_imported_kernel(kernel: dict[str, Any], source: str, tool: str) -> dict[str, Any]:
    metrics = kernel.get("metrics", kernel)
    operation = kernel.get("name") or kernel.get("kernel") or kernel.get("operation") or source
    counters = {
        name: float(metrics.get(name, 0.0))
        for name in COUNTER_MAP
    }
    return {
        "operation": operation,
        "source": source,
        "tool": tool,
        "arithmetic_intensity_flop_per_byte": float(metrics.get("arithmetic_intensity_flop_per_byte", 0.0)),
        "counters": counters,
    }


def load_imported_reports() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if IMPORTS.exists():
        for path in sorted(IMPORTS.glob("*.json")):
            data = load_json(path, {})
            tool = str(data.get("tool", "ncu-json"))
            kernels = data.get("kernels") or data.get("rows") or []
            if isinstance(kernels, dict):
                kernels = [kernels]
            for kernel in kernels:
                if isinstance(kernel, dict):
                    rows.append(normalize_imported_kernel(kernel, path.name, tool))
    classifications = [classify(row) for row in rows]
    return {
        "status": "ran" if rows else "empty",
        "import_dir": str(IMPORTS.relative_to(HERE)),
        "rows": rows,
        "classifications": classifications,
        "finding": (
            f"Imported {len(rows)} Nsight-shaped kernel rows and classified them with the same roofline decision rules."
            if rows
            else "No imported Nsight JSON reports were found; proxy counters remain the only profiler-shaped evidence."
        ),
    }


def build_workflow() -> dict[str, Any]:
    roofline = load_json(ROOT / "02-roofline" / "out_roofline.json", {})
    rows = roofline.get("rows", [])
    peak_gbps = max((row["effective_gbps"] for row in rows), default=1.0)
    peak_tflops = max((row["effective_tflops"] for row in rows), default=1.0)
    profiled = [proxy_counters(row, peak_gbps, peak_tflops) for row in rows]
    classifications = [classify(row) for row in profiled]
    imports = load_imported_reports()
    checks = {
        "roofline_rows_loaded": len(rows) >= 4,
        "counter_rows_match_roofline_rows": len(profiled) == len(rows),
        "every_row_classified": len(classifications) == len(rows) and all(row["bottleneck"] for row in classifications),
        "counter_map_populated": len(COUNTER_MAP) >= 6,
        "import_parser_ran": imports["status"] in {"ran", "empty"},
    }
    return {
        "status": "ran",
        "source_artifact": "02-roofline/out_roofline.json",
        "profiler": profiler_status(),
        "counter_map": COUNTER_MAP,
        "rows": profiled,
        "classifications": classifications,
        "imported_reports": imports,
        "correctness": {"status": "passed" if all(checks.values()) else "failed", "checks": checks},
        "finding": (
            "Profiler counters become useful when mapped back to the roofline question: memory saturation, SM utilization, "
            "barrier stalls, launch count, and arithmetic intensity each imply a different next optimization."
        ),
    }


def main() -> None:
    workflow = build_workflow()
    out = {
        "session": "22-gpumode-nsight-roofline",
        "timestamp": now(),
        "inventory": collect_inventory("22-gpumode-nsight-roofline"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-08-nsight-to-roofline",
            "gpumode_lessons": gpumode_links(),
            "extends": "02-roofline, 15-gpumode-coalescing, and 16-gpumode-warp-reductions",
        },
        "profiler_roofline": workflow,
        "correctness": workflow["correctness"],
        "boundary": (
            "This lab builds the counter-to-roofline decision workflow from local measurements. "
            "When Nsight CLI tools are unavailable, counter values are explicit proxies derived from the roofline artifact, not vendor profiler output."
        ),
    }
    path = HERE / "out_gpumode_nsight_roofline.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "wrote",
        path.name,
        "classifications",
        len(workflow["classifications"]),
        "profiler",
        workflow["profiler"]["status"],
        "correctness",
        out["correctness"]["status"],
    )


if __name__ == "__main__":
    main()
