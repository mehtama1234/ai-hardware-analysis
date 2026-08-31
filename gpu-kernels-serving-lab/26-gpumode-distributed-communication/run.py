"""Session 26: GPUMODE-derived distributed communication and collectives lab."""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import csv
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.bench import median_seconds
from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
GPUMODE_ROOT = ROOT.parent / "gpu-mode-curriculum"
IMPORTS = HERE / "imports"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


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
        text = " ".join([title, " ".join(lesson.get("exercise_candidates", []))]).lower()
        if (
            "distributed" in topics
            or "collectives" in concepts
            or "nccl" in text
            or "nvshmem" in text
            or "all-reduce" in text
            or "distributed gemm" in text
        ):
            selected.append(
                {
                    "index": lesson["index"],
                    "title": lesson["title"],
                    "url": lesson["url"],
                    "topics": lesson["topics"],
                    "concepts": lesson.get("concepts", []),
                    "tools": lesson.get("tools", []),
                    "exercise_candidates": lesson.get("exercise_candidates", []),
                }
            )
    return selected[:18]


def collective_model() -> dict[str, Any]:
    # Conservative illustrative links, not measured hardware claims.
    topologies = [
        {"name": "pcie4_x16_proxy", "bandwidth_gbps": 32.0, "latency_us": 8.0},
        {"name": "nvlink_proxy", "bandwidth_gbps": 150.0, "latency_us": 3.0},
        {"name": "ethernet_200g_proxy", "bandwidth_gbps": 25.0, "latency_us": 20.0},
    ]
    message_sizes = [2**exp for exp in range(10, 29, 3)]
    world_sizes = [2, 4, 8]
    rows = []
    for topo in topologies:
        bw_bytes_s = topo["bandwidth_gbps"] * 1e9
        latency_s = topo["latency_us"] / 1e6
        for world in world_sizes:
            for size in message_sizes:
                ring_bytes = 2 * (world - 1) / world * size
                ring_time = 2 * (world - 1) * latency_s + ring_bytes / bw_bytes_s
                tree_steps = math.ceil(math.log2(world))
                tree_bytes = 2 * size
                tree_time = 2 * tree_steps * latency_s + tree_bytes / bw_bytes_s
                nvshmem_put_time = latency_s + size / bw_bytes_s
                best = min(
                    [
                        ("ring_allreduce", ring_time),
                        ("tree_allreduce", tree_time),
                        ("nvshmem_put_reduce_proxy", nvshmem_put_time),
                    ],
                    key=lambda item: item[1],
                )
                rows.append(
                    {
                        "topology": topo["name"],
                        "world_size": world,
                        "message_bytes": size,
                        "ring_us": round(ring_time * 1e6, 3),
                        "tree_us": round(tree_time * 1e6, 3),
                        "nvshmem_put_reduce_proxy_us": round(nvshmem_put_time * 1e6, 3),
                        "modeled_winner": best[0],
                        "regime": "latency-dominated" if size < 1 << 18 else "bandwidth-dominated",
                    }
                )
    crossover = []
    for topo in topologies:
        for world in world_sizes:
            candidates = [row for row in rows if row["topology"] == topo["name"] and row["world_size"] == world]
            first_bandwidth = next((row for row in candidates if row["regime"] == "bandwidth-dominated"), candidates[-1])
            crossover.append(
                {
                    "topology": topo["name"],
                    "world_size": world,
                    "first_bandwidth_dominated_bytes": first_bandwidth["message_bytes"],
                    "winner_at_crossover": first_bandwidth["modeled_winner"],
                }
            )
    return {
        "status": "ran",
        "rows": rows,
        "crossover": crossover,
        "finding": "All-reduce choice changes with message size, world size, latency, and bandwidth: small reductions are latency sensitive, while large gradients/KV transfers are bandwidth dominated.",
    }


def _worker(rank: int, world: int, n: int, queue: mp.Queue) -> None:
    torch.manual_seed(2600 + rank)
    tensor = torch.full((n,), float(rank + 1), dtype=torch.float32)
    queue.put((rank, tensor.tolist()))


def local_allreduce_proxy(world: int = 4, n: int = 4096) -> dict[str, Any]:
    def run_once() -> torch.Tensor:
        queue: mp.Queue = mp.Queue()
        procs = [mp.Process(target=_worker, args=(rank, world, n, queue)) for rank in range(world)]
        for proc in procs:
            proc.start()
        chunks = [torch.tensor(queue.get()[1], dtype=torch.float32) for _ in procs]
        for proc in procs:
            proc.join()
        return torch.stack(chunks).sum(dim=0)

    seconds = median_seconds(lambda: run_once(), warmup=1, repeat=3)
    out = run_once()
    expected = torch.full((n,), sum(range(1, world + 1)), dtype=torch.float32)
    max_error = float((out - expected).abs().max().item())
    bytes_reduced = world * n * 4
    return {
        "status": "ran",
        "world_size": world,
        "elements_per_rank": n,
        "bytes_reduced": bytes_reduced,
        "seconds": round(seconds, 6),
        "effective_gbps": round(bytes_reduced / seconds / 1e9, 6) if seconds > 0 else math.inf,
        "max_abs_error": round(max_error, 8),
        "finding": "The local multiprocessing proxy proves all ranks contribute to the same reduced tensor; it is a semantic check, not a GPU interconnect benchmark.",
    }


def runtime_readiness() -> dict[str, Any]:
    try:
        import torch.distributed as dist

        dist_available = dist.is_available()
        nccl_available = dist.is_nccl_available()
        gloo_available = dist.is_gloo_available()
    except Exception:
        dist_available = nccl_available = gloo_available = False
    tools = {
        "nvidia-smi": shutil.which("nvidia-smi"),
        "nccl-tests-all_reduce_perf": shutil.which("all_reduce_perf"),
        "nvshmem-info": shutil.which("nvshmem-info"),
        "ibv_devinfo": shutil.which("ibv_devinfo"),
    }
    nvshmem_probe = None
    if tools["nvshmem-info"]:
        code, stdout, stderr = run_cmd([tools["nvshmem-info"]])
        nvshmem_probe = {"returncode": code, "stdout": stdout[:1000], "stderr": stderr[:1000]}
    return {
        "status": "ready" if nccl_available and torch.cuda.device_count() > 1 else "skipped",
        "torch_distributed_available": dist_available,
        "nccl_backend_available": nccl_available,
        "gloo_backend_available": gloo_available,
        "torch_cuda_device_count": torch.cuda.device_count(),
        "tools": tools,
        "nvshmem_probe": nvshmem_probe,
        "reason": (
            "Real NCCL all-reduce timing needs at least two CUDA-visible GPUs plus NCCL test/runtime tools; NVSHMEM needs its runtime tools."
        ),
    }


def load_imported_benchmarks() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if IMPORTS.exists():
        for path in sorted(IMPORTS.glob("*.csv")):
            with path.open(newline="", encoding="utf-8") as handle:
                for raw in csv.DictReader(handle):
                    try:
                        rows.append(
                            {
                                "source": path.name,
                                "tool": "nccl-tests",
                                "message_bytes": int(raw.get("bytes", 0)),
                                "time_us": float(raw.get("time_us", raw.get("time", 0.0))),
                                "algbw_gbps": float(raw.get("algbw_gbps", raw.get("algbw", 0.0))),
                                "busbw_gbps": float(raw.get("busbw_gbps", raw.get("busbw", 0.0))),
                                "errors": int(float(raw.get("errors", 0))),
                            }
                        )
                    except (TypeError, ValueError):
                        continue
        for path in sorted(IMPORTS.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            tool = str(data.get("tool", "json"))
            for raw in data.get("rows", []):
                try:
                    rows.append(
                        {
                            "source": path.name,
                            "tool": tool,
                            "message_bytes": int(raw.get("message_bytes", raw.get("bytes", 0))),
                            "time_us": float(raw.get("time_us", 0.0)),
                            "algbw_gbps": float(raw.get("bandwidth_gbps", raw.get("algbw_gbps", 0.0))),
                            "busbw_gbps": float(raw.get("busbw_gbps", raw.get("bandwidth_gbps", 0.0))),
                            "errors": int(float(raw.get("errors", 0))),
                        }
                    )
                except (TypeError, ValueError):
                    continue
    rows.sort(key=lambda row: (row["tool"], row["message_bytes"]))
    best_by_tool = []
    for tool in sorted({row["tool"] for row in rows}):
        subset = [row for row in rows if row["tool"] == tool]
        best = max(subset, key=lambda row: row["busbw_gbps"])
        best_by_tool.append(
            {
                "tool": tool,
                "best_message_bytes": best["message_bytes"],
                "best_busbw_gbps": best["busbw_gbps"],
                "best_time_us": best["time_us"],
                "rows": len(subset),
            }
        )
    return {
        "status": "ran" if rows else "empty",
        "import_dir": str(IMPORTS.relative_to(HERE)),
        "rows": rows,
        "best_by_tool": best_by_tool,
        "finding": (
            f"Imported {len(rows)} collective benchmark rows from {len(best_by_tool)} tool family/families; compare best bus bandwidth against the modeled topology rows."
            if rows
            else "No NCCL/NVSHMEM benchmark exports were found; the communication model remains the only performance estimate."
        ),
    }


def main() -> None:
    model = collective_model()
    proxy = local_allreduce_proxy()
    readiness = runtime_readiness()
    imports = load_imported_benchmarks()
    checks = {
        "model_ran": model["status"] == "ran" and len(model["rows"]) > 0,
        "model_has_world_sizes": {row["world_size"] for row in model["rows"]} == {2, 4, 8},
        "proxy_ran": proxy["status"] == "ran",
        "proxy_correct": proxy["max_abs_error"] <= 1e-6,
        "runtime_classified": readiness["status"] in {"ready", "skipped"},
        "import_parser_ran": imports["status"] in {"ran", "empty"},
        "import_rows_error_free": all(row["errors"] == 0 for row in imports["rows"]),
    }
    out = {
        "session": "26-gpumode-distributed-communication",
        "timestamp": now(),
        "inventory": collect_inventory("26-gpumode-distributed-communication"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-12-distributed-communication",
            "gpumode_lessons": gpumode_links(),
            "extends": "12-jax-scaling-practicum, 20-gpumode-vllm-scheduler, 22-gpumode-nsight-roofline, and 25-gpumode-rocm-hip-portability",
        },
        "collective_model": model,
        "local_allreduce_proxy": proxy,
        "runtime_readiness": readiness,
        "imported_benchmarks": imports,
        "correctness": {
            "status": "passed" if all(checks.values()) else "failed",
            "checks": checks,
        },
        "boundary": (
            "This lab models collective communication regimes and verifies all-reduce semantics locally. "
            "It does not claim NCCL, NVSHMEM, InfiniBand, or multi-GPU performance unless those runtimes and devices are actually visible."
        ),
    }
    path = HERE / "out_gpumode_distributed_communication.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "wrote",
        path.name,
        "model",
        model["status"],
        "runtime",
        readiness["status"],
        "correctness",
        out["correctness"]["status"],
    )


if __name__ == "__main__":
    main()
