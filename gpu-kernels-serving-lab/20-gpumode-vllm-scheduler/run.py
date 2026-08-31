"""Session 20: GPUMODE-derived vLLM scheduler and KV-cache pressure lab."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
GPUMODE_ROOT = ROOT.parent / "gpu-mode-curriculum"


@dataclass(frozen=True)
class Request:
    id: str
    arrival_ms: int
    prompt_tokens: int
    output_tokens: int
    prefix_group: str
    shared_prefix_tokens: int


REQUESTS = [
    Request("r00", 0, 768, 96, "system-a", 512),
    Request("r01", 0, 896, 96, "system-a", 512),
    Request("r02", 12, 512, 128, "system-b", 384),
    Request("r03", 24, 1536, 64, "system-a", 512),
    Request("r04", 32, 384, 160, "system-c", 256),
    Request("r05", 48, 2048, 96, "system-long", 1024),
    Request("r06", 64, 640, 128, "system-b", 384),
    Request("r07", 84, 512, 192, "system-c", 256),
    Request("r08", 96, 3072, 64, "system-long", 1024),
    Request("r09", 128, 768, 96, "system-a", 512),
    Request("r10", 144, 896, 128, "system-b", 384),
    Request("r11", 160, 512, 160, "system-c", 256),
]

CONFIG = {
    "block_size_tokens": 16,
    "kv_capacity_blocks": 4096,
    "prefill_tokens_per_ms": 384,
    "decode_tokens_per_ms": 96,
    "max_batch_seqs": 6,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocks(tokens: int, block_size: int) -> int:
    return (tokens + block_size - 1) // block_size


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
            "serving" in topics
            or "attention" in topics
            or "kv cache" in concepts
            or "vllm" in title
            or "scheduler" in title
            or "prefill" in exercises
            or "decode" in exercises
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


def private_prompt_tokens(req: Request) -> int:
    return max(0, req.prompt_tokens - req.shared_prefix_tokens)


def request_blocks(req: Request, use_prefix_cache: bool, block_size: int) -> int:
    if use_prefix_cache:
        return blocks(private_prompt_tokens(req) + req.output_tokens, block_size)
    return blocks(req.prompt_tokens + req.output_tokens, block_size)


def prefix_blocks(requests: list[Request], block_size: int) -> int:
    seen: dict[str, int] = {}
    for req in requests:
        seen[req.prefix_group] = max(seen.get(req.prefix_group, 0), req.shared_prefix_tokens)
    return sum(blocks(tokens, block_size) for tokens in seen.values())


def kv_blocks_for(requests: list[Request], use_prefix_cache: bool, block_size: int) -> int:
    total = sum(request_blocks(req, use_prefix_cache, block_size) for req in requests)
    return total + (prefix_blocks(requests, block_size) if use_prefix_cache else 0)


def fcfs_static_batches(requests: list[Request], config: dict[str, int]) -> dict[str, Any]:
    block_size = config["block_size_tokens"]
    time_ms = 0
    completed = []
    peak_blocks = 0
    batches = []
    queue = sorted(requests, key=lambda req: (req.arrival_ms, req.id))
    while queue:
        ready_time = max(time_ms, queue[0].arrival_ms)
        ready = [req for req in queue if req.arrival_ms <= ready_time]
        batch = ready[: config["max_batch_seqs"]]
        queue = [req for req in queue if req not in batch]
        start = ready_time
        prompt_tokens = sum(req.prompt_tokens for req in batch)
        output_tokens = sum(req.output_tokens for req in batch)
        prefill_ms = max(1, (prompt_tokens + config["prefill_tokens_per_ms"] - 1) // config["prefill_tokens_per_ms"])
        decode_ms = max(1, (output_tokens + config["decode_tokens_per_ms"] - 1) // config["decode_tokens_per_ms"])
        first_token_ms = start + prefill_ms
        finish_ms = first_token_ms + decode_ms
        active_blocks = kv_blocks_for(batch, False, block_size)
        peak_blocks = max(peak_blocks, active_blocks)
        batches.append(
            {
                "start_ms": start,
                "finish_ms": finish_ms,
                "requests": [req.id for req in batch],
                "kv_blocks": active_blocks,
            }
        )
        for req in batch:
            completed.append(
                {
                    "id": req.id,
                    "arrival_ms": req.arrival_ms,
                    "first_token_ms": first_token_ms,
                    "finish_ms": finish_ms,
                    "ttft_ms": first_token_ms - req.arrival_ms,
                    "tpot_ms": round((finish_ms - first_token_ms) / req.output_tokens, 4),
                    "output_tokens": req.output_tokens,
                }
            )
        time_ms = finish_ms
    return summarize_policy("fcfs_static_batches", completed, batches, peak_blocks)


def continuous_paged_scheduler(requests: list[Request], config: dict[str, int]) -> dict[str, Any]:
    block_size = config["block_size_tokens"]
    waiting = sorted(requests, key=lambda req: (req.arrival_ms, req.id))
    pending_prefill: list[dict[str, Any]] = []
    decoding: list[dict[str, Any]] = []
    completed = []
    prefix_groups: dict[str, int] = {}
    peak_blocks = 0
    timeline = []
    time_ms = 0

    while waiting or pending_prefill or decoding:
        arrived = [req for req in waiting if req.arrival_ms <= time_ms]
        waiting = [req for req in waiting if req.arrival_ms > time_ms]
        for req in arrived:
            prefix_groups[req.prefix_group] = max(prefix_groups.get(req.prefix_group, 0), req.shared_prefix_tokens)
            pending_prefill.append({"request": req, "remaining_prompt": private_prompt_tokens(req)})

        active_count = len(pending_prefill) + len(decoding)
        if active_count < config["max_batch_seqs"] and waiting:
            next_arrival = waiting[0].arrival_ms
            if not pending_prefill and not decoding and time_ms < next_arrival:
                time_ms = next_arrival
                continue

        prefill_budget = config["prefill_tokens_per_ms"]
        for item in list(pending_prefill):
            if prefill_budget <= 0:
                break
            take = min(prefill_budget, item["remaining_prompt"])
            item["remaining_prompt"] -= take
            prefill_budget -= take
            if item["remaining_prompt"] <= 0:
                pending_prefill.remove(item)
                decoding.append(
                    {
                        "request": item["request"],
                        "remaining_output": item["request"].output_tokens,
                        "first_token_ms": time_ms + 1,
                    }
                )

        decode_budget = config["decode_tokens_per_ms"]
        active_decoders = sorted(decoding, key=lambda item: (item["request"].arrival_ms, item["request"].id))
        while decode_budget > 0 and active_decoders:
            progressed = False
            for item in list(active_decoders):
                if decode_budget <= 0:
                    break
                if item["remaining_output"] <= 0:
                    continue
                item["remaining_output"] -= 1
                decode_budget -= 1
                progressed = True
                if item["remaining_output"] == 0:
                    req = item["request"]
                    completed.append(
                        {
                            "id": req.id,
                            "arrival_ms": req.arrival_ms,
                            "first_token_ms": item["first_token_ms"],
                            "finish_ms": time_ms + 1,
                            "ttft_ms": item["first_token_ms"] - req.arrival_ms,
                            "tpot_ms": round((time_ms + 1 - item["first_token_ms"]) / req.output_tokens, 4),
                            "output_tokens": req.output_tokens,
                        }
                    )
                    decoding.remove(item)
                    active_decoders.remove(item)
            if not progressed:
                break

        live_requests = [item["request"] for item in pending_prefill] + [item["request"] for item in decoding]
        live_prefix_blocks = sum(blocks(tokens, block_size) for tokens in prefix_groups.values())
        live_private_blocks = sum(request_blocks(req, True, block_size) for req in live_requests)
        live_blocks = live_prefix_blocks + live_private_blocks
        peak_blocks = max(peak_blocks, live_blocks)
        timeline.append(
            {
                "time_ms": time_ms,
                "waiting": len(waiting),
                "prefill": len(pending_prefill),
                "decode": len(decoding),
                "kv_blocks": live_blocks,
            }
        )
        time_ms += 1

    return summarize_policy("continuous_paged_prefix_cache", completed, timeline, peak_blocks)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * pct))
    return round(ordered[index], 4)


def summarize_policy(name: str, completed: list[dict[str, Any]], trace: list[dict[str, Any]], peak_blocks: int) -> dict[str, Any]:
    ttft = [row["ttft_ms"] for row in completed]
    tpot = [row["tpot_ms"] for row in completed]
    total_output_tokens = sum(row["output_tokens"] for row in completed)
    start = min(row["arrival_ms"] for row in completed)
    finish = max(row["finish_ms"] for row in completed)
    makespan = max(1, finish - start)
    return {
        "name": name,
        "completed_requests": len(completed),
        "makespan_ms": makespan,
        "output_tokens": total_output_tokens,
        "tokens_per_second": round(total_output_tokens / makespan * 1000, 2),
        "mean_ttft_ms": round(statistics.mean(ttft), 3),
        "p95_ttft_ms": percentile(ttft, 0.95),
        "mean_tpot_ms": round(statistics.mean(tpot), 4),
        "p95_tpot_ms": percentile(tpot, 0.95),
        "peak_kv_blocks": peak_blocks,
        "trace_rows": len(trace),
        "trace_sample": trace[:8],
        "completed": sorted(completed, key=lambda row: row["id"]),
    }


def run_experiment() -> dict[str, Any]:
    requests = REQUESTS
    policies = [
        fcfs_static_batches(requests, CONFIG),
        continuous_paged_scheduler(requests, CONFIG),
    ]
    by_name = {policy["name"]: policy for policy in policies}
    baseline = by_name["fcfs_static_batches"]
    optimized = by_name["continuous_paged_prefix_cache"]
    block_size = CONFIG["block_size_tokens"]
    no_prefix_blocks = kv_blocks_for(requests, False, block_size)
    prefix_blocks_total = kv_blocks_for(requests, True, block_size)
    comparison = {
        "ttft_speedup": round(baseline["mean_ttft_ms"] / optimized["mean_ttft_ms"], 3),
        "throughput_speedup": round(optimized["tokens_per_second"] / baseline["tokens_per_second"], 3),
        "peak_kv_block_reduction_pct": round(
            (baseline["peak_kv_blocks"] - optimized["peak_kv_blocks"]) / baseline["peak_kv_blocks"] * 100,
            2,
        ),
        "full_workload_prefix_block_saving_pct": round((no_prefix_blocks - prefix_blocks_total) / no_prefix_blocks * 100, 2),
    }
    correctness = {
        "all_requests_completed": all(policy["completed_requests"] == len(requests) for policy in policies),
        "capacity_respected": all(policy["peak_kv_blocks"] <= CONFIG["kv_capacity_blocks"] for policy in policies),
        "prefix_cache_reduces_full_workload_blocks": prefix_blocks_total < no_prefix_blocks,
        "continuous_scheduler_improves_mean_ttft": optimized["mean_ttft_ms"] < baseline["mean_ttft_ms"],
    }
    return {
        "status": "ran",
        "config": CONFIG,
        "workload": [req.__dict__ for req in requests],
        "policies": policies,
        "kv_accounting": {
            "full_workload_blocks_without_prefix_cache": no_prefix_blocks,
            "full_workload_blocks_with_prefix_cache": prefix_blocks_total,
            "capacity_blocks": CONFIG["kv_capacity_blocks"],
        },
        "comparison": comparison,
        "correctness": {
            "status": "passed" if all(correctness.values()) else "failed",
            "checks": correctness,
        },
        "finding": (
            "Continuous batching lowers mean TTFT and improves output throughput on this deterministic workload, "
            "while paged prefix-cache accounting reduces KV blocks versus per-request prompt storage."
        ),
    }


def main() -> None:
    experiment = run_experiment()
    out = {
        "session": "20-gpumode-vllm-scheduler",
        "timestamp": now(),
        "inventory": collect_inventory("20-gpumode-vllm-scheduler"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-06-vllm-scheduler",
            "gpumode_lessons": gpumode_links(),
            "extends": "09-vllm-serving and 10-kv-cache-memory-manager",
        },
        "scheduler": experiment,
        "correctness": experiment["correctness"],
        "boundary": (
            "This is a deterministic scheduler and KV-accounting simulator. It models the serving shape "
            "behind vLLM-style continuous batching and paged KV caches, but it is not a vLLM internals clone "
            "and does not claim GPU kernel throughput."
        ),
    }
    path = HERE / "out_gpumode_vllm_scheduler.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "wrote",
        path.name,
        "policies",
        len(experiment["policies"]),
        "correctness",
        out["correctness"]["status"],
    )


if __name__ == "__main__":
    main()
