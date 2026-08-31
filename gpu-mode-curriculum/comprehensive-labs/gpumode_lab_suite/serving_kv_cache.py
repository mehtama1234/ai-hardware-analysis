from __future__ import annotations

from dataclasses import dataclass, field

from .common import Check, emit


LAB_ID = "comp-lab-05-serving-kv-cache"


@dataclass
class Request:
    request_id: str
    prompt_tokens: int
    output_tokens: int
    shared_prefix_tokens: int = 0
    generated: int = 0


@dataclass
class PagedKVCache:
    block_size: int
    free_blocks: list[int]
    allocations: dict[str, list[int]] = field(default_factory=dict)

    def allocate(self, request: Request) -> list[int]:
        private_tokens = max(0, request.prompt_tokens - request.shared_prefix_tokens)
        needed = (private_tokens + request.output_tokens + self.block_size - 1) // self.block_size
        if needed > len(self.free_blocks):
            raise RuntimeError("out of KV blocks")
        blocks = [self.free_blocks.pop(0) for _ in range(needed)]
        self.allocations[request.request_id] = blocks
        return blocks

    def release(self, request_id: str) -> None:
        self.free_blocks.extend(self.allocations.pop(request_id, []))
        self.free_blocks.sort()


def continuous_batch(requests: list[Request], max_batch: int) -> list[dict[str, object]]:
    active = requests[:max_batch]
    waiting = requests[max_batch:]
    timeline = []
    step = 0
    while active:
        step += 1
        for req in active:
            req.generated += 1
        finished = [req for req in active if req.generated >= req.output_tokens]
        active = [req for req in active if req.generated < req.output_tokens]
        while waiting and len(active) < max_batch:
            active.append(waiting.pop(0))
        timeline.append({"step": step, "active": [req.request_id for req in active], "finished": [req.request_id for req in finished]})
    return timeline


def run() -> dict[str, object]:
    requests = [
        Request("a", 1024, 4, 768),
        Request("b", 768, 3, 512),
        Request("c", 256, 2, 0),
        Request("d", 512, 1, 256),
    ]
    cache = PagedKVCache(block_size=16, free_blocks=list(range(512)))
    allocated = {req.request_id: cache.allocate(req) for req in requests}
    before_release = len(cache.free_blocks)
    cache.release("c")
    timeline = continuous_batch([Request(r.request_id, r.prompt_tokens, r.output_tokens, r.shared_prefix_tokens) for r in requests], max_batch=2)
    checks = [
        Check("prefix_sharing_reduces_blocks", len(allocated["a"]) < (requests[0].prompt_tokens + requests[0].output_tokens + 15) // 16, str(len(allocated["a"]))).__dict__,
        Check("release_returns_blocks", len(cache.free_blocks) > before_release, f"{before_release}->{len(cache.free_blocks)}").__dict__,
        Check("continuous_batch_finishes_all", timeline[-1]["active"] == [], str(timeline[-1])).__dict__,
        Check("scheduler_refills_batch", any(len(row["active"]) == 2 for row in timeline[1:]), "batch refill observed").__dict__,
    ]
    return {
        "summary": "Implements paged KV allocation, prefix sharing, release, and continuous batching.",
        "results": {"allocated_blocks": {k: len(v) for k, v in allocated.items()}, "timeline": timeline},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
