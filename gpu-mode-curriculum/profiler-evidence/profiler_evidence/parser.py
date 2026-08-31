from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "profiler-evidence" / "fixtures"
REPORTS = ROOT / "profiler-evidence" / "reports"
REPORT_JSON = REPORTS / "profiler-evidence-report.json"
REPORT_MD = REPORTS / "profiler-evidence-report.md"


@dataclass(frozen=True)
class NormalizedRow:
    source: str
    name: str
    kind: str
    duration_us: float
    metrics: dict[str, float]


def number(value: str | int | float | None) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def parse_nsight_compute(path: Path) -> list[NormalizedRow]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                NormalizedRow(
                    source="nsight-compute",
                    name=row["kernel"],
                    kind="kernel",
                    duration_us=number(row.get("duration_us")),
                    metrics={
                        "dram_util_pct": number(row.get("dram_util_pct")),
                        "sm_util_pct": number(row.get("sm_util_pct")),
                        "tensor_util_pct": number(row.get("tensor_util_pct")),
                        "l2_hit_pct": number(row.get("l2_hit_pct")),
                        "launches": number(row.get("launches")),
                        "bytes": number(row.get("bytes")),
                        "flops": number(row.get("flops")),
                    },
                )
            )
    return rows


def parse_rocprof(path: Path) -> list[NormalizedRow]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                NormalizedRow(
                    source="rocprof",
                    name=row["kernel"],
                    kind="kernel",
                    duration_us=number(row.get("duration_us")),
                    metrics={
                        "vgpr": number(row.get("vgpr")),
                        "sgpr": number(row.get("sgpr")),
                        "waves_per_eu": number(row.get("waves_per_eu")),
                        "valu_util_pct": number(row.get("valu_util_pct")),
                        "fetch_size_bytes": number(row.get("fetch_size_bytes")),
                        "write_size_bytes": number(row.get("write_size_bytes")),
                    },
                )
            )
    return rows


def parse_nsight_systems(path: Path) -> list[NormalizedRow]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for span in payload.get("spans", []):
        rows.append(
            NormalizedRow(
                source="nsight-systems",
                name=span["name"],
                kind=span.get("kind", "span"),
                duration_us=number(span.get("duration_us")),
                metrics={
                    "kernels": number(span.get("kernels")),
                    "memcpy_us": number(span.get("memcpy_us")),
                },
            )
        )
    return rows


def classify(row: NormalizedRow) -> str:
    m = row.metrics
    if row.source == "nsight-compute":
        if m.get("dram_util_pct", 0) >= 75 and m.get("sm_util_pct", 0) < 70:
            return "memory-bandwidth"
        if m.get("sm_util_pct", 0) >= 80 and m.get("tensor_util_pct", 0) >= 50:
            return "tensor-core-compute"
        if m.get("l2_hit_pct", 100) < 55 and m.get("dram_util_pct", 0) >= 60:
            return "cache-locality"
    if row.source == "rocprof":
        if m.get("valu_util_pct", 0) >= 80 and m.get("waves_per_eu", 0) <= 4:
            return "compute-occupancy"
        if m.get("fetch_size_bytes", 0) > m.get("write_size_bytes", 0) * 2:
            return "memory-bandwidth"
    if row.source == "nsight-systems":
        if m.get("kernels", 0) > 1000:
            return "launch-overhead"
        if row.kind == "nccl":
            return "communication"
        if m.get("memcpy_us", 0) / max(1.0, row.duration_us) > 0.08:
            return "host-device-transfer"
    return "mixed"


def remediation(kind: str) -> list[str]:
    table = {
        "memory-bandwidth": ["coalesce or vectorize memory access", "raise arithmetic intensity", "add tiling/reuse before retiming"],
        "tensor-core-compute": ["inspect MMA tile shape", "check tensor-core eligibility", "compare occupancy against stall reasons"],
        "cache-locality": ["change layout or blocking", "reduce gathers", "separate L2-hit and DRAM-bound kernels"],
        "compute-occupancy": ["reduce register pressure", "check wave occupancy", "try smaller tiles"],
        "launch-overhead": ["fuse small kernels", "use CUDA graphs", "batch decode work"],
        "communication": ["compare ring/tree/channel topology", "increase payload aggregation", "inspect overlap with compute"],
        "host-device-transfer": ["remove sync copies", "pin and batch transfers", "move preprocessing onto device"],
        "mixed": ["split by kernel", "collect roofline counters", "compare against baseline"],
    }
    return table[kind]


def normalize_all() -> list[dict[str, Any]]:
    parsed = [
        *parse_nsight_compute(FIXTURES / "nsight_compute_kernels.csv"),
        *parse_nsight_systems(FIXTURES / "nsight_systems_timeline.json"),
        *parse_rocprof(FIXTURES / "rocprof_kernels.csv"),
    ]
    rows = []
    for row in parsed:
        bottleneck = classify(row)
        rows.append(
            {
                "source": row.source,
                "name": row.name,
                "kind": row.kind,
                "duration_us": row.duration_us,
                "metrics": row.metrics,
                "classification": bottleneck,
                "remediation": remediation(bottleneck),
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows = normalize_all()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    report = {
        "artifact": "profiler-evidence-report",
        "row_count": len(rows),
        "source_count": len({row["source"] for row in rows}),
        "classification_counts": dict(sorted(counts.items())),
        "rows": rows,
        "checks": {
            "has_nsight_compute": any(row["source"] == "nsight-compute" for row in rows),
            "has_nsight_systems": any(row["source"] == "nsight-systems" for row in rows),
            "has_rocprof": any(row["source"] == "rocprof" for row in rows),
            "has_memory_bandwidth": "memory-bandwidth" in counts,
            "has_launch_overhead": "launch-overhead" in counts,
            "has_communication": "communication" in counts,
            "all_rows_have_remediation": all(row["remediation"] for row in rows),
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(markdown(report), encoding="utf-8")
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Profiler Evidence Report",
        "",
        f"Rows: {report['row_count']}",
        f"Sources: {report['source_count']}",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in report["classification_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Rows", "", "| Source | Name | Classification | Duration us | Remediation |", "|---|---|---|---|---|"])
    for row in report["rows"]:
        lines.append(
            f"| {row['source']} | {row['name']} | {row['classification']} | "
            f"{row['duration_us']} | {'; '.join(row['remediation'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"
