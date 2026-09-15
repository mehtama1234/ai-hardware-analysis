#!/usr/bin/env python3
"""Extract digest-bound structural IR for a real multi-module catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verification_platform.rtl_ast import extract_parser_cdfg, extract_structural_ir, partition_parser_cdfg


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_files(root: Path) -> list[Path]:
    base = root / "src" if (root / "src").is_dir() else root
    files = sorted(base.glob("*.sv")) + sorted(base.glob("*.v"))
    return [path for path in files if not path.name.lower().endswith(("_tb.v", "_tb.sv", "tb.v", "tb.sv"))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for index, design in enumerate(catalog.get("designs", [])):
        root = Path(str(design["root"]))
        sources = source_files(root)
        if root.name == "i2c-gpio-expander":
            sources.append(Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/platforms/ihp-sg13g2/verilog/sg13g2_io.v"))
        source_revision = digest({str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources})
        run_root = output / f"{index:02d}-{root.name}"
        ir, _ = extract_structural_ir(
            *sources, top=str(design["top"]), run_root=run_root,
            source_revision=source_revision, timeout_seconds=120,
        )
        cdfg, _ = extract_parser_cdfg(
            *sources, top=str(design["top"]), run_root=run_root,
            source_revision=source_revision, timeout_seconds=120,
        )
        incoming: dict[str, int] = {}
        for edge in cdfg.get("edges", []):
            incoming[str(edge.get("target"))] = incoming.get(str(edge.get("target")), 0) + 1
        targets = sorted(
            node["id"] for node in cdfg.get("nodes", [])
            if node.get("kind") == "signal" and node.get("module") == str(design["top"]) and incoming.get(node["id"], 0)
        )
        partition = partition_parser_cdfg(cdfg, targets=[targets[0]], max_nodes=512) if cdfg["status"] == "passed" and targets else {"status": "blocked", "blocked_reason": "no top-level signal with an incoming CDFG edge"}
        partition_path = run_root / "parser-cdfg-partition.json"
        partition_path.write_text(json.dumps(partition, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rows.append({
            "repository": design.get("repository"), "root": str(root), "top": design["top"],
            "source_count": len(sources), "status": "passed" if ir["status"] == "passed" and cdfg["status"] == "passed" else "blocked",
            "module_count": ir.get("module_count", 0), "ir_path": str(output / f"{index:02d}-{root.name}" / "rtl-structural-ir.json"),
            "ir_sha256": ir.get("ir_sha256"), "cdfg_path": str(run_root / "parser-cdfg.json"),
            "cdfg_sha256": cdfg.get("cdfg_sha256"), "cdfg_node_count": cdfg.get("node_count", 0),
            "cdfg_edge_count": cdfg.get("edge_count", 0),
            "partition_path": str(partition_path), "partition_sha256": partition.get("partition_sha256"),
            "partition_status": partition.get("status"), "partition_selected_node_count": partition.get("selected_node_count", 0),
            "context_reduction_ratio": round(1 - (int(partition.get("selected_node_count", 0)) / int(cdfg.get("node_count", 0))), 6) if cdfg.get("node_count") else None,
        })
    report = {
        "schema_version": "real-multimodule-structural-ir-report-v1",
        "catalog": str(args.catalog.resolve()), "target_count": len(rows), "designs": rows,
        "status": "passed" if rows and all(item["status"] == "passed" and int(item["module_count"]) > 0 for item in rows) else "blocked",
        "claim_boundary": "Yosys structural IR extraction and digest integrity only; not functional equivalence, debugging accuracy, or physical signoff",
    }
    report["report_sha256"] = digest(report)
    path = output / "real-multimodule-structural-ir-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "targets": len(rows), "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
