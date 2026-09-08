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
NATIVE_CAPTURE = ROOT / "gpu-runs" / "imports" / "colab-t4-wmma-20260907T055545Z" / "profiler-evidence.json"


@dataclass(frozen=True)
class NormalizedRow:
    source: str
    name: str
    kind: str
    duration_us: float | None
    metrics: dict[str, float | None]


def number(value: str | int | float | None) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def metric_number(value: str | int | float | None) -> float | None:
    """Parse a counter without converting an absent counter into zero."""
    if value is None or value == "":
        return None
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
                    duration_us=metric_number(row.get("duration_us")),
                    metrics={
                        "dram_util_pct": metric_number(row.get("dram_util_pct")),
                        "sm_util_pct": metric_number(row.get("sm_util_pct")),
                        "tensor_util_pct": metric_number(row.get("tensor_util_pct")),
                        "l2_hit_pct": metric_number(row.get("l2_hit_pct")),
                        "launches": metric_number(row.get("launches")),
                        "bytes": metric_number(row.get("bytes")),
                        "flops": metric_number(row.get("flops")),
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
                    duration_us=metric_number(row.get("duration_us")),
                    metrics={
                        "vgpr": metric_number(row.get("vgpr")),
                        "sgpr": metric_number(row.get("sgpr")),
                        "waves_per_eu": metric_number(row.get("waves_per_eu")),
                        "valu_util_pct": metric_number(row.get("valu_util_pct")),
                        "fetch_size_bytes": metric_number(row.get("fetch_size_bytes")),
                        "write_size_bytes": metric_number(row.get("write_size_bytes")),
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
                duration_us=metric_number(span.get("duration_us")),
                metrics={
                    "kernels": metric_number(span.get("kernels")),
                    "memcpy_us": metric_number(span.get("memcpy_us")),
                },
            )
        )
    return rows


def classify(row: NormalizedRow) -> str:
    m = row.metrics
    if row.source == "nsight-compute":
        if any(m.get(key) is None for key in ("dram_util_pct", "sm_util_pct", "tensor_util_pct", "l2_hit_pct")):
            return "insufficient-data"
        if m["dram_util_pct"] >= 75 and m["sm_util_pct"] < 70:
            return "memory-bandwidth"
        if m["sm_util_pct"] >= 80 and m["tensor_util_pct"] >= 50:
            return "tensor-core-compute"
        if m["l2_hit_pct"] < 55 and m["dram_util_pct"] >= 60:
            return "cache-locality"
    if row.source == "rocprof":
        if any(m.get(key) is None for key in ("waves_per_eu", "valu_util_pct", "fetch_size_bytes", "write_size_bytes")):
            return "insufficient-data"
        if m["valu_util_pct"] >= 80 and m["waves_per_eu"] <= 4:
            return "compute-occupancy"
        if m["fetch_size_bytes"] > m["write_size_bytes"] * 2:
            return "memory-bandwidth"
    if row.source == "nsight-systems":
        if any(m.get(key) is None for key in ("kernels", "memcpy_us")) or row.duration_us is None:
            return "insufficient-data"
        if m["kernels"] > 1000:
            return "launch-overhead"
        if row.kind == "nccl":
            return "communication"
        if m["memcpy_us"] / max(1.0, row.duration_us) > 0.08:
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
        "insufficient-data": ["retain the raw capture", "collect the missing counters before classifying", "do not infer zero from an absent field"],
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
        missing_metrics = [key for key, value in row.metrics.items() if value is None]
        rows.append(
            {
                "source": row.source,
                "evidence_kind": "fixture",
                "measured": False,
                "name": row.name,
                "kind": row.kind,
                "duration_us": row.duration_us,
                "metrics": row.metrics,
                "missing_metrics": missing_metrics,
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
    native_captures: list[dict[str, Any]] = []
    if NATIVE_CAPTURE.exists():
        capture = json.loads(NATIVE_CAPTURE.read_text(encoding="utf-8"))
        native_captures.append({
            "artifact": str(NATIVE_CAPTURE.relative_to(ROOT.parent)),
            "artifact_sha256": __import__("hashlib").sha256(NATIVE_CAPTURE.read_bytes()).hexdigest(),
            "evidence_kind": "native-capture",
            "measured": capture.get("status") == "passed",
            "gpu_execution_accepted": capture.get("status") == "passed",
            "project": capture.get("project"),
            "tool_availability": capture.get("tool_availability", {}),
            "sass": {
                "status": capture.get("sass", {}).get("status"),
                "tensor_core_instruction_seen": capture.get("sass", {}).get("tensor_core_instruction_seen"),
                "instruction_line_count": capture.get("sass", {}).get("instruction_line_count"),
            },
            "nsight_compute": {
                "status": capture.get("nsight_compute", {}).get("status"),
                "version": capture.get("nsight_compute", {}).get("version"),
                "metric": capture.get("nsight_compute", {}).get("metric"),
                "returncode": capture.get("nsight_compute", {}).get("returncode"),
            },
            "source_sha256": capture.get("source_sha256", {}),
        })
    report = {
        "artifact": "profiler-evidence-report",
        "evidence_kind": "fixture",
        "measured": False,
        "gpu_execution_accepted": False,
        "scope": "deterministic profiler-shaped teaching fixtures and heuristic classifications; not captured device profiler evidence",
        "row_count": len(rows),
        "source_count": len({row["source"] for row in rows}),
        "native_capture_count": len(native_captures),
        "native_captures": native_captures,
        "source_sha256": {
            str(path.relative_to(ROOT.parent)): __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__).resolve(),
                         FIXTURES / "nsight_compute_kernels.csv",
                         FIXTURES / "nsight_systems_timeline.json",
                         FIXTURES / "rocprof_kernels.csv")
        },
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
        "Normalized rows are deterministic fixture evidence; native captures are listed separately.",
        "Fixture classifications are teaching heuristics, not verified hardware diagnoses.",
        "",
        f"Rows: {report['row_count']}",
        f"Sources: {report['source_count']}",
        f"Native captures: {report['native_capture_count']}",
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
