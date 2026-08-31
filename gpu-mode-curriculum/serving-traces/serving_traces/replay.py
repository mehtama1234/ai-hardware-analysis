from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class RequestTrace:
    request_id: str
    arrival_ms: float
    prompt_tokens: int
    output_tokens: int
    shared_prefix_tokens: int = 0
    priority: int = 0


@dataclass(frozen=True)
class ReplayConfig:
    block_size: int = 16
    kv_capacity_blocks: int = 4096
    prefill_ms_per_token: float = 0.018
    decode_ms_per_token: float = 0.42
    max_prefill_batch: int = 4
    max_decode_batch: int = 16
    batch_efficiency: float = 0.78


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    fraction = rank - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def _prefix_blocks(request: RequestTrace, config: ReplayConfig, prefix_cache_enabled: bool) -> int:
    if not prefix_cache_enabled:
        return 0
    return _ceil_div(max(0, request.shared_prefix_tokens), config.block_size)


def _private_blocks(request: RequestTrace, config: ReplayConfig, prefix_cache_enabled: bool) -> int:
    private_prompt = request.prompt_tokens
    if prefix_cache_enabled:
        private_prompt = max(0, request.prompt_tokens - request.shared_prefix_tokens)
    return _ceil_div(private_prompt + request.output_tokens, config.block_size)


def _aggregate(policy: str, requests: list[RequestTrace], rows: list[dict[str, Any]], config: ReplayConfig) -> dict[str, Any]:
    completed = [row for row in rows if row["status"] == "completed"]
    ttft = [row["ttft_ms"] for row in completed]
    tpot = [row["tpot_ms"] for row in completed]
    e2e = [row["e2e_ms"] for row in completed]
    output_tokens = sum(row["output_tokens"] for row in completed)
    first_arrival = min((request.arrival_ms for request in requests), default=0.0)
    makespan = max((row["finish_ms"] for row in completed), default=first_arrival) - first_arrival
    return {
        "policy": policy,
        "request_count": len(requests),
        "completed_count": len(completed),
        "rejected_count": len(rows) - len(completed),
        "total_output_tokens": output_tokens,
        "makespan_ms": round(makespan, 4),
        "output_tokens_per_second": round(output_tokens / max(makespan / 1000.0, 1e-9), 4),
        "mean_ttft_ms": round(mean(ttft), 4) if ttft else 0.0,
        "p50_ttft_ms": round(_percentile(ttft, 0.50), 4),
        "p95_ttft_ms": round(_percentile(ttft, 0.95), 4),
        "mean_tpot_ms": round(mean(tpot), 4) if tpot else 0.0,
        "mean_e2e_ms": round(mean(e2e), 4) if e2e else 0.0,
        "peak_live_kv_blocks": max((row["peak_live_kv_blocks"] for row in rows), default=0),
        "prefix_cache_blocks_saved": sum(row.get("prefix_cache_blocks_saved", 0) for row in rows),
        "kv_capacity_blocks": config.kv_capacity_blocks,
    }


def _static_replay(requests: list[RequestTrace], config: ReplayConfig) -> dict[str, Any]:
    now = 0.0
    rows: list[dict[str, Any]] = []
    for request in sorted(requests, key=lambda row: (row.arrival_ms, -row.priority, row.request_id)):
        private_blocks = _private_blocks(request, config, prefix_cache_enabled=False)
        if private_blocks > config.kv_capacity_blocks:
            rows.append(
                {
                    "request_id": request.request_id,
                    "status": "rejected",
                    "arrival_ms": request.arrival_ms,
                    "prompt_tokens": request.prompt_tokens,
                    "output_tokens": request.output_tokens,
                    "kv_blocks_allocated": 0,
                    "prefix_cache_blocks_saved": 0,
                    "peak_live_kv_blocks": 0,
                    "admission_ms": None,
                    "first_token_ms": None,
                    "finish_ms": None,
                    "ttft_ms": 0.0,
                    "tpot_ms": 0.0,
                    "e2e_ms": 0.0,
                }
            )
            continue
        admission = max(now, request.arrival_ms)
        prefill_done = admission + request.prompt_tokens * config.prefill_ms_per_token
        first_token = prefill_done + config.decode_ms_per_token
        finish = prefill_done + request.output_tokens * config.decode_ms_per_token
        now = finish
        rows.append(
            {
                "request_id": request.request_id,
                "status": "completed",
                "arrival_ms": request.arrival_ms,
                "prompt_tokens": request.prompt_tokens,
                "output_tokens": request.output_tokens,
                "kv_blocks_allocated": private_blocks,
                "prefix_cache_blocks_saved": 0,
                "peak_live_kv_blocks": private_blocks,
                "admission_ms": round(admission, 4),
                "first_token_ms": round(first_token, 4),
                "finish_ms": round(finish, 4),
                "ttft_ms": round(first_token - request.arrival_ms, 4),
                "tpot_ms": round((finish - first_token) / max(request.output_tokens - 1, 1), 4),
                "e2e_ms": round(finish - request.arrival_ms, 4),
            }
        )
    return {"summary": _aggregate("static-batching", requests, rows, config), "requests": rows}


def _continuous_replay(requests: list[RequestTrace], config: ReplayConfig) -> dict[str, Any]:
    ordered = sorted(requests, key=lambda row: (row.arrival_ms, -row.priority, row.request_id))
    rows: dict[str, dict[str, Any]] = {}
    waiting = ordered[:]
    active: list[dict[str, Any]] = []
    prefix_blocks: set[int] = set()
    live_private_blocks = 0
    peak_live = 0
    now = min((request.arrival_ms for request in ordered), default=0.0)

    while waiting or active:
        ready = [request for request in waiting if request.arrival_ms <= now]
        if not ready and not active and waiting:
            now = waiting[0].arrival_ms
            ready = [request for request in waiting if request.arrival_ms <= now]

        ready.sort(key=lambda row: (-row.shared_prefix_tokens, -row.priority, row.arrival_ms, row.request_id))
        for request in ready[: config.max_prefill_batch]:
            waiting.remove(request)
            prefix_needed = _prefix_blocks(request, config, prefix_cache_enabled=True)
            new_prefix_blocks = max(0, prefix_needed - len(prefix_blocks))
            private_blocks = _private_blocks(request, config, prefix_cache_enabled=True)
            if live_private_blocks + len(prefix_blocks) + new_prefix_blocks + private_blocks > config.kv_capacity_blocks:
                rows[request.request_id] = {
                    "request_id": request.request_id,
                    "status": "rejected",
                    "arrival_ms": request.arrival_ms,
                    "prompt_tokens": request.prompt_tokens,
                    "output_tokens": request.output_tokens,
                    "kv_blocks_allocated": 0,
                    "prefix_cache_blocks_saved": 0,
                    "peak_live_kv_blocks": peak_live,
                    "admission_ms": None,
                    "first_token_ms": None,
                    "finish_ms": None,
                    "ttft_ms": 0.0,
                    "tpot_ms": 0.0,
                    "e2e_ms": 0.0,
                }
                continue
            for block in range(len(prefix_blocks), len(prefix_blocks) + new_prefix_blocks):
                prefix_blocks.add(block)
            live_private_blocks += private_blocks
            prefill_tokens = max(0, request.prompt_tokens - request.shared_prefix_tokens)
            prefill_done = now + prefill_tokens * config.prefill_ms_per_token / max(len(ready[: config.max_prefill_batch]), 1)
            rows[request.request_id] = {
                "request_id": request.request_id,
                "status": "completed",
                "arrival_ms": request.arrival_ms,
                "prompt_tokens": request.prompt_tokens,
                "output_tokens": request.output_tokens,
                "kv_blocks_allocated": private_blocks + new_prefix_blocks,
                "prefix_cache_blocks_saved": max(0, prefix_needed - new_prefix_blocks),
                "peak_live_kv_blocks": 0,
                "admission_ms": round(now, 4),
                "first_token_ms": None,
                "finish_ms": None,
                "ttft_ms": 0.0,
                "tpot_ms": 0.0,
                "e2e_ms": 0.0,
            }
            active.append(
                {
                    "request": request,
                    "generated": 0,
                    "ready_ms": prefill_done,
                    "private_blocks": private_blocks,
                    "first_token_ms": None,
                }
            )
            peak_live = max(peak_live, live_private_blocks + len(prefix_blocks))

        decode_ready = [row for row in active if row["ready_ms"] <= now]
        if not decode_ready:
            next_times = []
            if active:
                next_times.append(min(row["ready_ms"] for row in active))
            if waiting:
                next_times.append(waiting[0].arrival_ms)
            if not next_times:
                break
            now = max(now, min(next_times))
            continue

        batch = decode_ready[: config.max_decode_batch]
        step_ms = config.decode_ms_per_token * (1.0 + (len(batch) - 1) * (1.0 - config.batch_efficiency))
        now += step_ms
        finished = []
        for state in batch:
            request = state["request"]
            state["generated"] += 1
            if state["first_token_ms"] is None:
                state["first_token_ms"] = now
                rows[request.request_id]["first_token_ms"] = round(now, 4)
            if state["generated"] >= request.output_tokens:
                rows[request.request_id]["finish_ms"] = round(now, 4)
                rows[request.request_id]["ttft_ms"] = round(now - request.arrival_ms if request.output_tokens == 1 else state["first_token_ms"] - request.arrival_ms, 4)
                rows[request.request_id]["tpot_ms"] = round((now - state["first_token_ms"]) / max(request.output_tokens - 1, 1), 4)
                rows[request.request_id]["e2e_ms"] = round(now - request.arrival_ms, 4)
                live_private_blocks -= state["private_blocks"]
                finished.append(state)
        for state in finished:
            active.remove(state)
        for row in rows.values():
            row["peak_live_kv_blocks"] = peak_live

    request_rows = [rows[request.request_id] for request in ordered if request.request_id in rows]
    return {"summary": _aggregate("continuous-batching-prefix-cache", requests, request_rows, config), "requests": request_rows}


def replay_trace(trace: dict[str, Any], config: ReplayConfig | None = None) -> dict[str, Any]:
    config = config or ReplayConfig(**trace.get("config", {}))
    requests = [RequestTrace(**row) for row in trace["requests"]]
    static = _static_replay(requests, config)
    continuous = _continuous_replay(requests, config)
    checks = {
        "all_static_completed": static["summary"]["completed_count"] == len(requests),
        "all_continuous_completed": continuous["summary"]["completed_count"] == len(requests),
        "continuous_throughput_gte_static": continuous["summary"]["output_tokens_per_second"] >= static["summary"]["output_tokens_per_second"],
        "prefix_cache_saves_blocks": continuous["summary"]["prefix_cache_blocks_saved"] > 0
        if any(row.shared_prefix_tokens for row in requests)
        else True,
        "p95_ttft_gte_p50": continuous["summary"]["p95_ttft_ms"] >= continuous["summary"]["p50_ttft_ms"],
        "kv_peak_within_capacity": continuous["summary"]["peak_live_kv_blocks"] <= config.kv_capacity_blocks,
    }
    return {
        "trace_id": trace["trace_id"],
        "title": trace["title"],
        "description": trace.get("description", ""),
        "config": config.__dict__,
        "policies": [static, continuous],
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
    }
