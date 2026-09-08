#!/usr/bin/env python3
"""Two-rank CPU/Gloo request dispatch correctness for serving architecture."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "reports" / "distributed-serving-cpu.json"


def worker(rank: int, rendezvous: str, directory: str) -> None:
    import torch.distributed as dist
    dist.init_process_group("gloo", init_method=rendezvous, rank=rank, world_size=2,
                            timeout=timedelta(seconds=30))
    try:
        prompts = (["rank-zero-a", "rank-zero-b", "rank-zero-c"] if rank == 0
                   else ["rank-one-a", "rank-one-b"])
        local = [{"rank": rank, "local_index": i, "prompt": prompt,
                  "text": f"{prompt}:served"} for i, prompt in enumerate(prompts)]
        gathered = [None, None]
        dist.all_gather_object(gathered, local)
        Path(directory, f"rank-{rank}.json").write_text(json.dumps({"rank": rank, "local": local, "gathered": gathered}) + "\n")
    finally:
        dist.destroy_process_group()


def main() -> int:
    import torch.multiprocessing as mp
    sys.path.insert(0, str(ROOT / "gpu-kernels-serving-lab"))
    from common.provenance import source_provenance
    report = {"experiment": "distributed_serving_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
              "status": "failed", "measured": True, "gpu_execution_accepted": False, "backend": "gloo",
              "world_size": 2, "scope": "two local CPU ranks exchange request/result objects; dispatch ordering and ownership correctness only, no HTTP, GPU, latency, or multi-host claim"}
    context = None
    try:
        with tempfile.TemporaryDirectory(prefix="gpu-distributed-serving-") as directory:
            context = mp.spawn(worker, args=((Path(directory) / "rendezvous").as_uri(), directory), nprocs=2, join=False)
            deadline = time.monotonic() + 90
            while not context.join(timeout=1):
                if time.monotonic() >= deadline: raise TimeoutError("distributed serving dispatch exceeded 90 seconds")
            rows = [json.loads(Path(directory, f"rank-{rank}.json").read_text()) for rank in range(2)]
            flat = [item for row in rows for item in row["local"]]
            expected = [{"rank": rank, "local_index": index, "prompt": prompt, "text": f"{prompt}:served"}
                        for rank, prompts in enumerate((("rank-zero-a", "rank-zero-b", "rank-zero-c"), ("rank-one-a", "rank-one-b")))
                        for index, prompt in enumerate(prompts)]
            checks = {"rank_ownership": [row["rank"] for row in rows] == [0, 1],
                      "global_order": flat == expected, "unique_requests": len({(x["rank"], x["local_index"]) for x in flat}) == 5,
                      "result_parity": all(x["text"] == f"{x['prompt']}:served" for x in flat),
                      "peer_agreement": all(row["gathered"][0] == rows[0]["local"] and row["gathered"][1] == rows[1]["local"] for row in rows)}
            report.update({"status": "passed" if all(checks.values()) else "failed", "checks": checks, "rank_reports": rows, "request_count": len(flat)})
    except Exception as exc:
        report["error"] = repr(exc)
    finally:
        if context is not None:
            for process in context.processes:
                if process.is_alive(): process.terminate()
            for process in context.processes: process.join(timeout=5)
    report["provenance"] = source_provenance(ROOT, [Path(__file__)])
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": report.get("checks", {})}, indent=2)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())
