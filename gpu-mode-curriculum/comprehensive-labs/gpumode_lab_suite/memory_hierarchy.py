from __future__ import annotations

import math

from .common import Check, emit


LAB_ID = "comp-lab-01-memory-hierarchy"


def memory_transactions(elements: int, stride: int, word_bytes: int = 4, segment_bytes: int = 128) -> int:
    touched_segments = {(i * stride * word_bytes) // segment_bytes for i in range(elements)}
    return len(touched_segments)


def shared_memory_bank_conflicts(stride: int, lanes: int = 32, banks: int = 32) -> dict[str, int | float]:
    hits: dict[int, int] = {}
    for lane in range(lanes):
        bank = (lane * stride) % banks
        hits[bank] = hits.get(bank, 0) + 1
    worst = max(hits.values())
    conflict_banks = sum(1 for count in hits.values() if count > 1)
    return {"stride": stride, "used_banks": len(hits), "worst_conflict": worst, "conflict_banks": conflict_banks}


def occupancy(registers_per_thread: int, threads_per_block: int, shared_bytes: int) -> dict[str, int | float]:
    max_threads_per_sm = 2048
    max_blocks_per_sm = 32
    registers_per_sm = 65536
    shared_per_sm = 100 * 1024
    by_threads = max_threads_per_sm // threads_per_block
    by_registers = registers_per_sm // max(1, registers_per_thread * threads_per_block)
    by_shared = shared_per_sm // max(1, shared_bytes)
    resident_blocks = max(1, min(max_blocks_per_sm, by_threads, by_registers, by_shared))
    resident_threads = resident_blocks * threads_per_block
    return {
        "resident_blocks": resident_blocks,
        "resident_threads": resident_threads,
        "occupancy": round(resident_threads / max_threads_per_sm, 4),
    }


def roofline_bound(flops: float, bytes_moved: float, peak_tflops: float, peak_gbps: float) -> dict[str, float | str]:
    ai = flops / bytes_moved
    memory_ceiling = ai * peak_gbps * 1e9
    compute_ceiling = peak_tflops * 1e12
    return {
        "arithmetic_intensity": round(ai, 4),
        "attainable_tflops": round(min(memory_ceiling, compute_ceiling) / 1e12, 4),
        "bound": "memory" if memory_ceiling < compute_ceiling else "compute",
    }


def run() -> dict[str, object]:
    contiguous = memory_transactions(1024, 1)
    strided = memory_transactions(1024, 8)
    bank1 = shared_memory_bank_conflicts(1)
    bank16 = shared_memory_bank_conflicts(16)
    occ = occupancy(registers_per_thread=48, threads_per_block=256, shared_bytes=24 * 1024)
    roof = roofline_bound(flops=2 * 2048**3, bytes_moved=3 * 2048**2 * 2, peak_tflops=125, peak_gbps=3000)
    checks = [
        Check("striding_increases_transactions", strided > contiguous, f"{contiguous} -> {strided}").__dict__,
        Check("unit_stride_uses_all_banks", bank1["used_banks"] == 32, str(bank1)).__dict__,
        Check("stride_16_has_conflicts", bank16["worst_conflict"] > 1, str(bank16)).__dict__,
        Check("occupancy_is_bounded", 0 < occ["occupancy"] <= 1, str(occ)).__dict__,
        Check("roofline_classifies_bound", roof["bound"] in {"memory", "compute"}, str(roof)).__dict__,
    ]
    return {
        "summary": "Models memory coalescing, shared-memory bank conflicts, occupancy, and roofline bounds.",
        "results": {"transactions": {"contiguous": contiguous, "strided": strided}, "bank_conflicts": [bank1, bank16], "occupancy": occ, "roofline": roof},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
