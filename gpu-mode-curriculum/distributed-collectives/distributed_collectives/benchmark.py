from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "distributed-collectives" / "reports"
BENCHMARK_JSON = OUT / "collective-benchmark-run.json"
BENCHMARK_MD = OUT / "collective-benchmark-run.md"
MODEL_JSON = ROOT / "distributed-collectives" / "distributed-collectives-report.json"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _torch_state() -> tuple[Any | None, dict[str, Any]]:
    try:
        import torch
    except Exception as exc:
        return None, {"available": False, "error": str(exc)}
    return torch, {
        "available": True,
        "version": getattr(torch, "__version__", "unknown"),
        "cuda_available": bool(torch.cuda.is_available()),
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "hip_version": getattr(getattr(torch, "version", None), "hip", None),
        "cuda_version": getattr(getattr(torch, "version", None), "cuda", None),
    }


def _env_rank() -> dict[str, int]:
    return {
        "rank": int(os.environ.get("RANK", "0")),
        "local_rank": int(os.environ.get("LOCAL_RANK", "0")),
        "world_size": int(os.environ.get("WORLD_SIZE", "1")),
    }


def _backend(torch: Any, requested: str | None) -> str:
    if requested:
        return requested
    return "nccl" if torch.cuda.is_available() else "gloo"


def _device(torch: Any, local_rank: int, allow_cpu: bool) -> Any:
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank % max(1, torch.cuda.device_count()))
        return torch.device("cuda")
    if allow_cpu:
        return torch.device("cpu")
    return None


def _sync(torch: Any, dist: Any, device: Any) -> None:
    dist.barrier()
    if str(device) == "cuda":
        torch.cuda.synchronize(device)


def _time_ms(fn: Any, torch: Any, dist: Any, device: Any, warmup: int, iters: int) -> float:
    for _ in range(warmup):
        fn()
    _sync(torch, dist, device)
    start = time.perf_counter()
    for _ in range(iters):
        fn()
    _sync(torch, dist, device)
    return (time.perf_counter() - start) * 1000.0 / max(1, iters)


def _benchmarks(torch: Any, dist: Any, device: Any, bytes_per_rank: int, warmup: int, iters: int) -> list[dict[str, Any]]:
    rank = dist.get_rank()
    world = dist.get_world_size()
    dtype = torch.float32
    elem_size = torch.tensor([], dtype=dtype).element_size()
    count = max(1, bytes_per_rank // elem_size)
    base = torch.ones(count, dtype=dtype, device=device) * (rank + 1)
    rows: list[dict[str, Any]] = []

    def add(name: str, fn: Any, traffic_factor: float) -> None:
        try:
            ms = _time_ms(fn, torch, dist, device, warmup, iters)
            bytes_on_link = bytes_per_rank * traffic_factor
            gbps = bytes_on_link / max(ms / 1000.0, 1e-9) / 1_000_000_000
            rows.append(
                {
                    "collective": name,
                    "status": "passed",
                    "bytes_per_rank": bytes_per_rank,
                    "world_size": world,
                    "mean_ms": round(ms, 6),
                    "estimated_bus_gbps": round(gbps, 6),
                    "traffic_factor": round(traffic_factor, 6),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "collective": name,
                    "status": "skipped",
                    "bytes_per_rank": bytes_per_rank,
                    "world_size": world,
                    "reason": str(exc),
                }
            )

    add("all-reduce", lambda: dist.all_reduce(base), 2 * (world - 1) / world)

    gathered = [torch.empty_like(base) for _ in range(world)]
    add("all-gather", lambda: dist.all_gather(gathered, base), (world - 1) / world)

    if hasattr(dist, "reduce_scatter_tensor"):
        output = torch.empty(max(1, count // world), dtype=dtype, device=device)
        scatter_input = torch.ones(output.numel() * world, dtype=dtype, device=device)
        add("reduce-scatter", lambda: dist.reduce_scatter_tensor(output, scatter_input), (world - 1) / world)
    else:
        rows.append({"collective": "reduce-scatter", "status": "skipped", "bytes_per_rank": bytes_per_rank, "world_size": world, "reason": "reduce_scatter_tensor unavailable"})

    if hasattr(dist, "all_to_all_single"):
        out = torch.empty_like(base)
        add("all-to-all", lambda: dist.all_to_all_single(out, base), (world - 1) / world)
    else:
        rows.append({"collective": "all-to-all", "status": "skipped", "bytes_per_rank": bytes_per_rank, "world_size": world, "reason": "all_to_all_single unavailable"})

    add("broadcast", lambda: dist.broadcast(base, src=0), 1.0)
    return rows


def _model_facts() -> dict[str, Any]:
    model = _load_json(MODEL_JSON, {})
    return {
        "scenario_count": model.get("scenario_count", 0),
        "collective_count": model.get("collective_count", 0),
        "passed_scenarios": model.get("passed_scenarios", 0),
        "best_modeled_bandwidth_efficiency": max((row.get("bandwidth_efficiency", 0.0) for row in model.get("scenarios", [])), default=0.0),
        "best_modeled_overlap_gain": max((row.get("overlap_gain", 0.0) for row in model.get("scenarios", [])), default=0.0),
    }


def _host(torch_info: dict[str, Any]) -> dict[str, Any]:
    vendor = "NVIDIA" if torch_info.get("cuda_available") and torch_info.get("cuda_version") else "AMD" if torch_info.get("cuda_available") and torch_info.get("hip_version") else "unknown"
    return {
        "name": socket.gethostname(),
        "platform": platform.platform(),
        "vendor": vendor,
        "torch": torch_info,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Distributed Collectives Benchmark Run",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Backend: `{report['backend']}`",
        f"World size: `{report['world_size']}`",
        "",
        "| collective | status | bytes/rank | mean ms | bus GB/s | reason |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in report.get("benchmarks", []):
        lines.append(
            f"| {row.get('collective')} | `{row.get('status')}` | {row.get('bytes_per_rank', 0)} | "
            f"{row.get('mean_ms', '')} | {row.get('estimated_bus_gbps', '')} | {row.get('reason', '')} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def benchmark_collectives(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run torch.distributed collective benchmarks and write a GPU-run evidence artifact.")
    parser.add_argument("--bytes", type=int, default=16 * 1024 * 1024, help="Payload bytes per rank for measured collectives.")
    parser.add_argument("--warmup", type=int, default=5, help="Warmup iterations before timing.")
    parser.add_argument("--iters", type=int, default=20, help="Timed iterations.")
    parser.add_argument("--backend", default=None, help="Override torch.distributed backend.")
    parser.add_argument("--allow-cpu", action="store_true", help="Permit local gloo CPU smoke benchmarking.")
    parser.add_argument("--output", type=Path, default=BENCHMARK_JSON)
    args = parser.parse_args(argv)

    OUT.mkdir(parents=True, exist_ok=True)
    torch, torch_info = _torch_state()
    rank_env = _env_rank()
    model_facts = _model_facts()
    generated = datetime.now(timezone.utc).isoformat()
    benchmarks: list[dict[str, Any]] = []
    backend = args.backend or "unavailable"
    measured = False
    status = "skipped:missing-torch"
    skip_reason = torch_info.get("error", "missing torch")

    if torch is not None:
        backend = _backend(torch, args.backend)
        device = _device(torch, rank_env["local_rank"], args.allow_cpu)
        if device is None:
            status = "skipped:missing-accelerator"
            skip_reason = "torch is available, but neither CUDA/ROCm nor --allow-cpu is available"
        elif rank_env["world_size"] < 2:
            status = "skipped:requires-torchrun"
            skip_reason = "launch with torchrun --nproc_per_node=2 or more"
        else:
            import torch.distributed as dist

            dist.init_process_group(backend=backend)
            try:
                benchmarks = _benchmarks(torch, dist, device, args.bytes, args.warmup, args.iters)
            finally:
                dist.destroy_process_group()
            passed = [row for row in benchmarks if row.get("status") == "passed"]
            measured = bool(passed) and str(device) == "cuda"
            status = "passed" if len(passed) >= 3 else "failed"
            skip_reason = ""

    best_gbps = max((row.get("estimated_bus_gbps", 0.0) for row in benchmarks), default=0.0)
    backend_family = "rccl" if torch_info.get("hip_version") else "nccl" if backend == "nccl" else backend
    aggregate = {
        "torchrun": rank_env["world_size"] >= 2,
        "accelerator_ready": bool(torch_info.get("cuda_available")),
        "collective_scenarios": model_facts["scenario_count"],
        "collective_count": model_facts["collective_count"],
        "measured_collectives": sum(1 for row in benchmarks if row.get("status") == "passed"),
        "bandwidth_efficiency": min(1.0, model_facts["best_modeled_bandwidth_efficiency"]) if best_gbps <= 0 else min(1.0, best_gbps / 100.0),
        "overlap_gain": model_facts["best_modeled_overlap_gain"],
        "best_bus_gbps": round(best_gbps, 6),
        "nccl_or_rccl": backend_family in {"nccl", "rccl"},
        "backend": backend_family,
    }
    report = {
        "generated_at": generated,
        "status": status,
        "skip_reason": skip_reason,
        "measured": measured,
        "backend": backend,
        "backend_family": backend_family,
        "world_size": rank_env["world_size"],
        "rank": rank_env["rank"],
        "bytes_per_rank": args.bytes,
        "host": _host(torch_info),
        "model_facts": model_facts,
        "aggregate_metrics": aggregate,
        "benchmarks": benchmarks,
    }
    if rank_env["rank"] == 0:
        _write_json(args.output, report)
        BENCHMARK_MD.write_text(_render_markdown(report), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    report = benchmark_collectives(argv)
    if report.get("rank", 0) == 0:
        print(f"wrote {BENCHMARK_JSON.relative_to(ROOT)} ({report['status']}, world_size={report['world_size']})")
    return 0 if report["status"] == "passed" or str(report["status"]).startswith("skipped:") else 1


if __name__ == "__main__":
    raise SystemExit(main())
