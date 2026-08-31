from __future__ import annotations

from .common import Check, emit


LAB_ID = "comp-lab-08-profiler-evidence"


def classify(row: dict[str, float]) -> str:
    if row["dram_util_pct"] >= 75 and row["sm_util_pct"] < 70:
        return "memory-bandwidth"
    if row["sm_util_pct"] >= 75 and row["tensor_util_pct"] >= 50:
        return "tensor-core-compute"
    if row["launches"] > 1000 and row["sm_util_pct"] < 40:
        return "launch-overhead"
    if row["l2_hit_pct"] < 50 and row["dram_util_pct"] > 60:
        return "cache-locality"
    return "mixed"


def remediation(kind: str) -> list[str]:
    table = {
        "memory-bandwidth": ["coalesce loads", "increase arithmetic intensity", "reuse through shared memory"],
        "tensor-core-compute": ["check tile shape", "raise occupancy only if stalls dominate", "use profiler source counters"],
        "launch-overhead": ["fuse kernels", "capture graph", "batch small operations"],
        "cache-locality": ["improve layout", "tile working set", "avoid gather-heavy access"],
        "mixed": ["collect roofline", "split by kernel", "compare against baseline"],
    }
    return table[kind]


def evidence_report(rows: list[dict[str, float]]) -> list[dict[str, object]]:
    report = []
    for row in rows:
        kind = classify(row)
        report.append({"kernel": row["kernel"], "classification": kind, "remediation": remediation(kind)})
    return report


def run() -> dict[str, object]:
    rows = [
        {"kernel": "copy_stride8", "dram_util_pct": 88.0, "sm_util_pct": 32.0, "tensor_util_pct": 0.0, "l2_hit_pct": 45.0, "launches": 12},
        {"kernel": "wgmma_mainloop", "dram_util_pct": 52.0, "sm_util_pct": 91.0, "tensor_util_pct": 73.0, "l2_hit_pct": 82.0, "launches": 5},
        {"kernel": "tiny_ops", "dram_util_pct": 18.0, "sm_util_pct": 24.0, "tensor_util_pct": 0.0, "l2_hit_pct": 90.0, "launches": 1600},
    ]
    report = evidence_report(rows)
    classes = {row["classification"] for row in report}
    checks = [
        Check("detects_memory_bandwidth", "memory-bandwidth" in classes, str(classes)).__dict__,
        Check("detects_tensor_compute", "tensor-core-compute" in classes, str(classes)).__dict__,
        Check("detects_launch_overhead", "launch-overhead" in classes, str(classes)).__dict__,
        Check("every_row_has_remediation", all(row["remediation"] for row in report), str(report)).__dict__,
    ]
    return {
        "summary": "Classifies profiler counters into bottleneck diagnoses and remediation actions.",
        "results": {"report": report},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
