from __future__ import annotations

from dataclasses import dataclass

from .common import Check, emit


LAB_ID = "comp-lab-03-compiler-autotune"


@dataclass(frozen=True)
class Schedule:
    block_m: int
    block_n: int
    block_k: int
    num_warps: int
    stages: int


def candidate_schedules() -> list[Schedule]:
    return [
        Schedule(16, 16, 32, 4, 3),
        Schedule(32, 32, 32, 4, 4),
        Schedule(64, 32, 32, 8, 4),
        Schedule(64, 64, 32, 8, 5),
        Schedule(128, 64, 64, 8, 5),
    ]


def score(schedule: Schedule, m: int, n: int, k: int) -> dict[str, float | int]:
    tile_ops = 2 * schedule.block_m * schedule.block_n * schedule.block_k
    tiles = ((m + schedule.block_m - 1) // schedule.block_m) * ((n + schedule.block_n - 1) // schedule.block_n) * ((k + schedule.block_k - 1) // schedule.block_k)
    smem = (schedule.block_m * schedule.block_k + schedule.block_k * schedule.block_n) * 2
    occupancy_penalty = max(1.0, smem / (64 * 1024)) * schedule.num_warps / 4
    reuse = tile_ops / max(1, smem)
    cost = tiles * occupancy_penalty / reuse
    return {"tiles": tiles, "shared_bytes": smem, "reuse": round(reuse, 4), "cost": round(cost, 6)}


def choose(m: int, n: int, k: int) -> tuple[Schedule, dict[str, float | int]]:
    ranked = [(schedule, score(schedule, m, n, k)) for schedule in candidate_schedules()]
    return min(ranked, key=lambda row: row[1]["cost"])


def should_fuse(producer_bytes: int, consumer_bytes: int, extra_registers: int) -> dict[str, object]:
    saved_bytes = producer_bytes + consumer_bytes
    register_pressure = extra_registers > 32
    return {"fuse": saved_bytes > 4096 and not register_pressure, "saved_bytes": saved_bytes, "register_pressure": register_pressure}


def run() -> dict[str, object]:
    best, best_score = choose(4096, 4096, 4096)
    small, small_score = choose(256, 256, 256)
    fusion = should_fuse(8192, 8192, extra_registers=12)
    no_fusion = should_fuse(8192, 8192, extra_registers=64)
    checks = [
        Check("large_problem_prefers_large_tile", best.block_m >= 64, f"{best} {best_score}").__dict__,
        Check("small_problem_has_valid_schedule", small_score["tiles"] > 0, f"{small} {small_score}").__dict__,
        Check("fusion_saves_memory_when_pressure_ok", bool(fusion["fuse"]), str(fusion)).__dict__,
        Check("register_pressure_blocks_fusion", not bool(no_fusion["fuse"]), str(no_fusion)).__dict__,
    ]
    return {
        "summary": "Scores CUDA/Triton-style schedules and fusion decisions with explicit cost signals.",
        "results": {"large_best": best.__dict__ | best_score, "small_best": small.__dict__ | small_score, "fusion": fusion, "no_fusion": no_fusion},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
