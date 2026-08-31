"""Session 10: simulate KV-cache block allocation and prefix reuse."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent


@dataclass
class Scenario:
    name: str
    requests: int
    prompt_tokens: int
    generated_tokens: int
    shared_prefix_tokens: int


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocks(tokens: int, block_size: int) -> int:
    return (tokens + block_size - 1) // block_size


def simulate(s: Scenario, block_size: int, capacity_blocks: int) -> dict[str, object]:
    random.seed(0)
    per_request_no_prefix = blocks(s.prompt_tokens + s.generated_tokens, block_size)
    no_prefix_total = s.requests * per_request_no_prefix
    shared = blocks(s.shared_prefix_tokens, block_size) if s.shared_prefix_tokens else 0
    private_prompt = max(0, s.prompt_tokens - s.shared_prefix_tokens)
    per_request_private = blocks(private_prompt + s.generated_tokens, block_size)
    prefix_total = shared + s.requests * per_request_private
    saved = no_prefix_total - prefix_total
    return {
        "name": s.name,
        "requests": s.requests,
        "prompt_tokens": s.prompt_tokens,
        "generated_tokens": s.generated_tokens,
        "shared_prefix_tokens": s.shared_prefix_tokens,
        "block_size": block_size,
        "capacity_blocks": capacity_blocks,
        "blocks_without_prefix_cache": no_prefix_total,
        "blocks_with_prefix_cache": prefix_total,
        "blocks_saved": saved,
        "saved_pct": round(saved / no_prefix_total * 100, 2) if no_prefix_total else 0,
        "fits_without_prefix_cache": no_prefix_total <= capacity_blocks,
        "fits_with_prefix_cache": prefix_total <= capacity_blocks,
    }


def main() -> None:
    scenarios = [
        Scenario("short independent chats", 64, 256, 128, 0),
        Scenario("shared system prompt", 64, 1024, 128, 768),
        Scenario("long context low concurrency", 8, 8192, 256, 4096),
        Scenario("batch pressure", 192, 512, 128, 256),
    ]
    block_size = 16
    capacity_blocks = 4096
    rows = [simulate(s, block_size, capacity_blocks) for s in scenarios]
    out = {
        "session": "10-kv-cache-memory-manager",
        "timestamp": now(),
        "inventory": collect_inventory("10-kv-cache-memory-manager"),
        "assumptions": {
            "block_size_tokens": block_size,
            "capacity_blocks": capacity_blocks,
            "note": "This is a block allocator model, not vLLM internals.",
        },
        "rows": rows,
        "boundary": (
            "This proves the memory-accounting shape of block-based KV allocation and prefix reuse. "
            "It does not claim to reproduce vLLM's exact scheduler or eviction policy."
        ),
    }
    path = HERE / "out_kv_cache_memory_manager.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name)
    for row in rows:
        print(row["name"], row["saved_pct"], "% saved", "fits:", row["fits_with_prefix_cache"])


if __name__ == "__main__":
    main()

