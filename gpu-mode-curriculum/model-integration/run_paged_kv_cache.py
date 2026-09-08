#!/usr/bin/env python3
"""Reference paged KV-cache correctness and capacity experiment."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from paged_cache import PagedKVCache  # noqa: E402

OUT = HERE / "reports" / "paged-kv-cache-cpu.json"


def main():
    torch.manual_seed(482)
    cache = PagedKVCache(capacity_pages=12, page_size=4, heads=2, head_dim=3)
    handles = [cache.allocate() for _ in range(3)]
    expected = {}
    for index, handle in enumerate(handles):
        chunks = []
        for count in (3 + index, 5, 2):
            key = torch.randn(2, count, 3); value = torch.randn(2, count, 3)
            cache.append(handle, key, value); chunks.append((key, value))
        expected[handle] = (torch.cat([row[0] for row in chunks], dim=1), torch.cat([row[1] for row in chunks], dim=1))
    parity = []
    for handle, (key, value) in expected.items():
        actual_key, actual_value = cache.gather(handle)
        parity.append(bool(torch.equal(actual_key, key) and torch.equal(actual_value, value) and cache.length(handle) == key.shape[1]))
    before = cache.snapshot(); cache.free(handles[1]); after_free = cache.snapshot()
    reused = cache.allocate()
    key = torch.ones(2, 7, 3); value = torch.full_like(key, 2)
    cache.append(reused, key, value); gathered = cache.gather(reused)
    capacity_rejected = False
    exhausted = cache.allocate()
    try:
        cache.append(exhausted, torch.zeros(2, 100, 3), torch.zeros(2, 100, 3))
    except MemoryError:
        capacity_rejected = True
    checks = {"all_sequence_parity": all(parity), "logical_lengths": all(cache.length(h) == expected[h][0].shape[1] for h in handles if h.sequence_id in cache.sequences),
              "free_reclaims_pages": after_free["free_pages"] > before["free_pages"],
              "reused_sequence_parity": bool(torch.equal(gathered[0], key) and torch.equal(gathered[1], value)),
              "capacity_rejected": capacity_rejected}
    report = {"experiment": "paged_kv_cache_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if all(checks.values()) else "failed", "measured": True,
              "gpu_execution_accepted": False, "page_size": 4, "capacity_pages": 12,
              "checks": checks, "snapshot_before_free": before, "snapshot_after_free": after_free,
              "scope": "CPU reference page allocator and gather oracle; no CUDA kernel, eviction policy, or model-quality claim",
              "source_sha256": {str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in (Path(__file__).resolve(), SERVING / "paged_cache.py")}}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": checks}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
