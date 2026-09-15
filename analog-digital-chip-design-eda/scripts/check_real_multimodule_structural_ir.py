#!/usr/bin/env python3
"""Independently validate a real multi-module structural IR report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("report", type=Path); args = parser.parse_args()
    raw = json.loads(args.report.read_text(encoding="utf-8")); errors: list[str] = []
    if raw.get("schema_version") != "real-multimodule-structural-ir-report-v1": errors.append("schema mismatch")
    expected = raw.get("report_sha256"); body = dict(raw); body.pop("report_sha256", None)
    if not isinstance(expected, str) or digest(body) != expected: errors.append("report digest mismatch")
    designs = raw.get("designs", [])
    if raw.get("target_count") != len(designs) or not designs: errors.append("target count mismatch")
    for index, row in enumerate(designs):
        path = Path(str(row.get("ir_path", ""))); prefix = f"design[{index}]"
        if row.get("status") != "passed" or int(row.get("module_count", 0)) < 1: errors.append(f"{prefix} is not structurally passed")
        if not path.is_file(): errors.append(f"{prefix} IR is missing"); continue
        try: ir = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): errors.append(f"{prefix} IR is not JSON"); continue
        expected_ir = ir.get("ir_sha256"); ir_body = dict(ir); ir_body.pop("ir_sha256", None)
        if not isinstance(expected_ir, str) or digest(ir_body) != expected_ir: errors.append(f"{prefix} IR digest mismatch")
        if ir.get("schema_version") != "rtl-structural-ir-v1" or ir.get("status") != "passed": errors.append(f"{prefix} IR schema/status invalid")
        if row.get("ir_sha256") != expected_ir: errors.append(f"{prefix} report IR digest mismatch")
        cdfg_path = Path(str(row.get("cdfg_path", "")))
        if not cdfg_path.is_file():
            errors.append(f"{prefix} CDFG is missing")
            continue
        try: cdfg = json.loads(cdfg_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): errors.append(f"{prefix} CDFG is not JSON"); continue
        expected_cdfg = cdfg.get("cdfg_sha256"); cdfg_body = dict(cdfg); cdfg_body.pop("cdfg_sha256", None)
        if not isinstance(expected_cdfg, str) or digest(cdfg_body) != expected_cdfg: errors.append(f"{prefix} CDFG digest mismatch")
        if cdfg.get("schema_version") != "parser-cdfg-v1" or cdfg.get("status") != "passed": errors.append(f"{prefix} CDFG schema/status invalid")
        if row.get("cdfg_sha256") != expected_cdfg: errors.append(f"{prefix} report CDFG digest mismatch")
        if row.get("cdfg_node_count") != cdfg.get("node_count") or row.get("cdfg_edge_count") != cdfg.get("edge_count"): errors.append(f"{prefix} CDFG counts mismatch")
        partition_path = Path(str(row.get("partition_path", "")))
        if not partition_path.is_file(): errors.append(f"{prefix} partition is missing"); continue
        try: partition = json.loads(partition_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): errors.append(f"{prefix} partition is not JSON"); continue
        expected_partition = partition.get("partition_sha256"); partition_body = dict(partition); partition_body.pop("partition_sha256", None)
        if not isinstance(expected_partition, str) or digest(partition_body) != expected_partition: errors.append(f"{prefix} partition digest mismatch")
        if partition.get("status") != "ready" or partition.get("source_cdfg_sha256") != expected_cdfg: errors.append(f"{prefix} partition binding/status invalid")
        if row.get("partition_sha256") != expected_partition or row.get("partition_status") != partition.get("status") or row.get("partition_selected_node_count") != partition.get("selected_node_count"): errors.append(f"{prefix} report partition fields mismatch")
        if cdfg.get("node_count"):
            expected_reduction = round(1 - (int(partition.get("selected_node_count", 0)) / int(cdfg["node_count"])), 6)
            if row.get("context_reduction_ratio") != expected_reduction: errors.append(f"{prefix} context reduction metric mismatch")
        nodes = {node.get("id") for node in cdfg.get("nodes", []) if isinstance(node, dict)}
        selected = {node.get("id") for node in partition.get("nodes", []) if isinstance(node, dict)}
        targets = set(partition.get("targets", []))
        incoming: dict[str, set[str]] = {}
        for edge in cdfg.get("edges", []):
            if not isinstance(edge, dict) or edge.get("source") not in nodes or edge.get("target") not in nodes:
                errors.append(f"{prefix} CDFG has an invalid edge")
                continue
            incoming.setdefault(str(edge["target"]), set()).add(str(edge["source"]))
        expected_selected = set(targets); queue = sorted(targets)
        while queue:
            current = queue.pop(0)
            for predecessor in sorted(incoming.get(current, set())):
                if predecessor not in expected_selected:
                    expected_selected.add(predecessor); queue.append(predecessor)
        if not targets or not targets <= nodes: errors.append(f"{prefix} partition targets are invalid")
        if selected != expected_selected or partition.get("selected_node_count") != len(expected_selected): errors.append(f"{prefix} partition is not the exact backward cone")
        source_edges = {(str(edge.get("source")), str(edge.get("target")), str(edge.get("port", "")), str(edge.get("bit", ""))) for edge in cdfg.get("edges", []) if isinstance(edge, dict) and edge.get("source") in expected_selected and edge.get("target") in expected_selected}
        partition_edges = {(str(edge.get("source")), str(edge.get("target")), str(edge.get("port", "")), str(edge.get("bit", ""))) for edge in partition.get("edges", []) if isinstance(edge, dict)}
        if partition_edges != source_edges: errors.append(f"{prefix} partition edges do not match the source cone")
    result = {"schema_version": "real-multimodule-structural-ir-check-v1", "report": str(args.report), "status": "passed" if not errors else "blocked", "target_count": len(designs), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result); print(json.dumps(result, sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
