"""Yosys-backed structural RTL intermediate representation."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any

from .ledger import ToolRun, sha256_file
from .runner import run_command


def extract_structural_ir(
    *sources: str | Path,
    top: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
) -> tuple[dict[str, Any], ToolRun]:
    """Parse RTL with Yosys and emit a stable structural IR.

    This deliberately preserves structural information rather than claiming
    to be a complete source AST.  A failed or unavailable parser is returned
    as ``blocked`` and cannot be used for context reduction claims.
    """
    if not sources or not top or not source_revision:
        raise ValueError("sources, top, and source_revision are required")
    root = Path(run_root)
    output = root / "rtl-structural.json"
    read_sources = "; ".join(f"read_verilog -sv {Path(source).resolve()}" for source in sources)
    command = ["yosys", "-p", f"{read_sources}; hierarchy -top {top}; proc; write_json {output.resolve()}"]
    tool_run = run_command(command, tool="yosys-rtl-structural-ir", run_root=root, source_revision=source_revision, timeout_seconds=timeout_seconds, expected_artifacts=["rtl-structural.json"], run_id="structural")
    result: dict[str, Any] = {
        "schema_version": "rtl-structural-ir-v1",
        "status": "passed" if tool_run.status == "passed" else "blocked",
        "top": top,
        "source_revision": source_revision,
        "sources": [{"path": str(Path(source).resolve()), "sha256": sha256_file(source)} for source in sources],
        "tool_run": asdict(tool_run),
    }
    if tool_run.status == "passed" and output.is_file():
        raw = json.loads(output.read_text(encoding="utf-8"))
        modules: dict[str, Any] = {}
        for name, module in sorted((raw.get("modules") or {}).items()):
            modules[name] = {
                "ports": sorted((module.get("ports") or {}).keys()),
                "netnames": sorted((module.get("netnames") or {}).keys()),
                "cells": sorted((module.get("cells") or {}).keys()),
                "memories": sorted((module.get("memories") or {}).keys()),
                "attributes": {key: module.get("attributes", {}).get(key) for key in sorted(module.get("attributes", {})) if key in {"top", "hdlname", "src"}},
            }
        result["modules"] = modules
        result["module_count"] = len(modules)
    else:
        result["modules"] = {}
        result["module_count"] = 0
        result["blocked_reason"] = "Yosys structural extraction did not complete"
    body = {key: value for key, value in result.items() if key != "ir_sha256"}
    result["ir_sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    ir_path = root / "rtl-structural-ir.json"
    ir_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result, tool_run


def verify_structural_ir(ir: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    body = {key: value for key, value in ir.items() if key != "ir_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if ir.get("ir_sha256") != expected:
        errors.append("structural IR self-digest does not match")
    if ir.get("schema_version") != "rtl-structural-ir-v1":
        errors.append("unsupported structural IR schema")
    if ir.get("status") == "passed" and int(ir.get("module_count", 0)) < 1:
        errors.append("passed structural IR has no modules")
    if ir.get("status") == "blocked" and not ir.get("blocked_reason"):
        errors.append("blocked structural IR has no reason")
    return errors


def extract_parser_cdfg(
    *sources: str | Path,
    top: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
) -> tuple[dict[str, Any], ToolRun]:
    """Extract a parser-backed signal/cell CDFG from Yosys JSON.

    Nodes and edges come from elaborated connectivity, not textual guesses.
    The artifact is structural: it does not claim that sequential cell timing
    or unsupported language constructs have been reduced to a complete CDFG.
    """
    if not sources or not top or not source_revision:
        raise ValueError("sources, top, and source_revision are required")
    root = Path(run_root)
    output = root / "yosys-cdfg.json"
    reads = "; ".join(f"read_verilog -sv {Path(source).resolve()}" for source in sources)
    command = ["yosys", "-p", f"{reads}; hierarchy -top {top}; proc; write_json {output.resolve()}"]
    tool_run = run_command(command, tool="yosys-parser-cdfg", run_root=root, source_revision=source_revision, timeout_seconds=timeout_seconds, expected_artifacts=["yosys-cdfg.json"], run_id="parser-cdfg")
    result: dict[str, Any] = {
        "schema_version": "parser-cdfg-v1",
        "status": "passed" if tool_run.status == "passed" else "blocked",
        "top": top,
        "source_revision": source_revision,
        "sources": [{"path": str(Path(source).resolve()), "sha256": sha256_file(source)} for source in sources],
        "scope": "yosys-elaborated-signal-cell-connectivity",
        "tool_run": asdict(tool_run),
        "nodes": [],
        "edges": [],
    }
    if tool_run.status == "passed" and output.is_file():
        raw = json.loads(output.read_text(encoding="utf-8"))
        for module_name, module in sorted((raw.get("modules") or {}).items()):
            visible_by_bit: dict[str, list[str]] = {}
            for name, net in sorted((module.get("netnames") or {}).items()):
                for bit in net.get("bits", []):
                    visible_by_bit.setdefault(str(bit), []).append(name)
            for name in sorted(module.get("netnames", {})):
                result["nodes"].append({"id": f"{module_name}:signal:{name}", "kind": "signal", "module": module_name, "name": name, "source": module["netnames"][name].get("attributes", {}).get("src")})
            for cell_name, cell in sorted((module.get("cells") or {}).items()):
                cell_id = f"{module_name}:cell:{cell_name}"
                result["nodes"].append({"id": cell_id, "kind": "cell", "module": module_name, "name": cell_name, "cell_type": cell.get("type"), "source": cell.get("attributes", {}).get("src")})
                directions = cell.get("port_directions", {})
                for port, bits in sorted((cell.get("connections") or {}).items()):
                    for bit in bits:
                        names = visible_by_bit.get(str(bit), [])
                        for signal_name in names:
                            signal_id = f"{module_name}:signal:{signal_name}"
                            if directions.get(port) == "output":
                                result["edges"].append({"source": cell_id, "target": signal_id, "port": port, "bit": bit})
                            elif directions.get(port) == "input":
                                result["edges"].append({"source": signal_id, "target": cell_id, "port": port, "bit": bit})
        result["node_count"] = len(result["nodes"])
        result["edge_count"] = len(result["edges"])
    else:
        result["blocked_reason"] = "Yosys parser CDFG extraction did not complete"
        result["node_count"] = 0
        result["edge_count"] = 0
    result["cdfg_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "parser-cdfg.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result, tool_run


def partition_parser_cdfg(
    cdfg: dict[str, Any],
    *,
    targets: list[str],
    max_nodes: int = 128,
) -> dict[str, Any]:
    """Build a bounded backward dependency cone from parser-backed CDFG data.

    The result is a functional context artifact for an agent.  It preserves
    the elaborated signal/cell edges that lead to the requested targets, but
    it is not executable RTL and is never marked equivalent to the DUT.
    """
    if not isinstance(targets, list) or not targets or any(not isinstance(item, str) or not item for item in targets):
        raise ValueError("targets must be a non-empty list of node identifiers")
    if max_nodes <= 0:
        raise ValueError("max_nodes must be positive")
    body = {key: value for key, value in cdfg.items() if key != "cdfg_sha256"}
    expected_digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if cdfg.get("cdfg_sha256") != expected_digest:
        raise ValueError("cannot partition invalid parser CDFG: self-digest does not match")
    if cdfg.get("status") != "passed":
        raise ValueError("cannot partition blocked parser CDFG")
    nodes = {node.get("id"): node for node in cdfg.get("nodes", []) if isinstance(node, dict) and isinstance(node.get("id"), str)}
    unknown = sorted(set(targets) - set(nodes))
    if unknown:
        raise ValueError(f"CDFG targets are unknown: {', '.join(unknown)}")
    incoming: dict[str, set[str]] = {}
    valid_edges: list[dict[str, Any]] = []
    for edge in cdfg.get("edges", []):
        if not isinstance(edge, dict) or edge.get("source") not in nodes or edge.get("target") not in nodes:
            raise ValueError("parser CDFG contains an edge with an unknown endpoint")
        source, target = edge["source"], edge["target"]
        incoming.setdefault(target, set()).add(source)
        valid_edges.append(edge)
    selected = set(targets)
    queue = sorted(targets)
    while queue:
        current = queue.pop(0)
        for predecessor in sorted(incoming.get(current, set())):
            if predecessor not in selected:
                selected.add(predecessor)
                queue.append(predecessor)
    result: dict[str, Any] = {
        "schema_version": "rtl-functional-cdfg-partition-v1",
        "source_cdfg_sha256": cdfg["cdfg_sha256"],
        "top": cdfg.get("top"),
        "targets": sorted(set(targets)),
        "max_nodes": max_nodes,
        "selected_node_count": len(selected),
        "functional_equivalence_proven": False,
        "claim_boundary": "parser-CDFG dependency context only; not executable RTL and not functional-equivalence evidence",
    }
    if len(selected) > max_nodes:
        result["status"] = "blocked"
        result["blocked_reason"] = f"dependency cone contains {len(selected)} nodes, exceeding max_nodes={max_nodes}"
        result["nodes"] = []
        result["edges"] = []
    else:
        result["status"] = "ready"
        result["nodes"] = [nodes[node_id] for node_id in sorted(selected)]
        result["edges"] = sorted(
            [edge for edge in valid_edges if edge["source"] in selected and edge["target"] in selected],
            key=lambda edge: (edge["source"], edge["target"], edge.get("port", ""), str(edge.get("bit", ""))),
        )
    result["partition_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def verify_parser_cdfg_partition(cdfg: dict[str, Any], partition: dict[str, Any]) -> list[str]:
    """Verify digest binding and exact backward-cone selection."""
    errors: list[str] = []
    cdfg_body = {key: value for key, value in cdfg.items() if key != "cdfg_sha256"}
    if cdfg.get("cdfg_sha256") != hashlib.sha256(json.dumps(cdfg_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest():
        errors.append("source parser CDFG self-digest does not match")
    if partition.get("schema_version") != "rtl-functional-cdfg-partition-v1":
        errors.append("unsupported functional CDFG partition schema")
    if partition.get("source_cdfg_sha256") != cdfg.get("cdfg_sha256"):
        errors.append("functional CDFG partition is not bound to the source CDFG")
    body = {key: value for key, value in partition.items() if key != "partition_sha256"}
    if partition.get("partition_sha256") != hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest():
        errors.append("functional CDFG partition self-digest does not match")
    if partition.get("status") not in {"ready", "blocked"}:
        errors.append("functional CDFG partition has invalid status")
    node_ids = {node.get("id") for node in partition.get("nodes", []) if isinstance(node, dict)}
    target_ids = set(partition.get("targets", []))
    if partition.get("status") == "ready" and not target_ids.issubset(node_ids):
        errors.append("ready functional CDFG partition omits a target")
    cdfg_ids = {node.get("id") for node in cdfg.get("nodes", []) if isinstance(node, dict)}
    if not node_ids.issubset(cdfg_ids):
        errors.append("functional CDFG partition contains an unknown node")
    cdfg_edges = []
    incoming: dict[str, set[str]] = {}
    for edge in cdfg.get("edges", []):
        if isinstance(edge, dict) and edge.get("source") in cdfg_ids and edge.get("target") in cdfg_ids:
            cdfg_edges.append(edge)
            incoming.setdefault(edge["target"], set()).add(edge["source"])
    for edge in partition.get("edges", []):
        if not isinstance(edge, dict) or edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            errors.append("functional CDFG partition contains an edge outside its node set")
    if partition.get("status") == "ready":
        expected_nodes = set(target_ids)
        queue = sorted(target_ids)
        while queue:
            current = queue.pop(0)
            for predecessor in sorted(incoming.get(current, set())):
                if predecessor not in expected_nodes:
                    expected_nodes.add(predecessor)
                    queue.append(predecessor)
        if node_ids != expected_nodes:
            errors.append("functional CDFG partition is not the exact backward dependency cone")
        canonical = lambda edge: json.dumps(edge, sort_keys=True, separators=(",", ":"))
        expected_edges = {canonical(edge) for edge in cdfg_edges if edge["source"] in expected_nodes and edge["target"] in expected_nodes}
        actual_edges = {canonical(edge) for edge in partition.get("edges", [])}
        if actual_edges != expected_edges:
            errors.append("functional CDFG partition edges do not match its induced dependency cone")
        if partition.get("selected_node_count") != len(node_ids):
            errors.append("functional CDFG partition node count does not match its node set")
    if partition.get("status") == "blocked" and not partition.get("blocked_reason"):
        errors.append("blocked functional CDFG partition has no reason")
    return errors


def reconstruct_functional_partition(
    source: str | Path,
    cdfg: dict[str, Any],
    partition: dict[str, Any],
    *,
    output: str | Path,
    source_revision: str,
) -> dict[str, Any]:
    """Reconstruct a compile-ready single-module slice for one signal target.

    The parser-CDFG partition supplies the bounded, digest-checked context;
    the existing conservative source rewriter supplies syntactic structure.
    Unsupported RTL constructs remain blocked.  This function deliberately
    does not assert functional equivalence; callers must run the solver gate.
    """
    if not source_revision:
        raise ValueError("source_revision is required")
    errors = verify_parser_cdfg_partition(cdfg, partition)
    if errors:
        raise ValueError("cannot reconstruct invalid functional partition: " + "; ".join(errors))
    source_path = Path(source).resolve()
    source_digest = sha256_file(source_path)
    cdfg_sources = {
        str(Path(item.get("path", "")).resolve()): item.get("sha256")
        for item in cdfg.get("sources", []) if isinstance(item, dict) and item.get("path")
    }
    if cdfg_sources.get(str(source_path)) != source_digest:
        raise ValueError("cannot reconstruct functional partition: source is not bound to the parser CDFG")
    result: dict[str, Any] = {
        "schema_version": "rtl-functional-partition-reconstruction-v1",
        "source_revision": source_revision,
        "source": str(source_path),
        "source_sha256": source_digest,
        "source_cdfg_sha256": cdfg["cdfg_sha256"],
        "partition_sha256": partition["partition_sha256"],
        "status": "blocked",
        "functional_equivalence_proven": False,
        "claim_boundary": "compile-ready dependency slice only; functional equivalence requires a separate solver proof",
    }
    if partition.get("status") != "ready":
        result["blocked_reason"] = "functional CDFG partition is blocked"
    else:
        target_nodes = [node for node in partition.get("nodes", []) if node.get("id") in set(partition.get("targets", []))]
        signal_targets = [node for node in target_nodes if node.get("kind") == "signal" and isinstance(node.get("name"), str)]
        if len(target_nodes) != 1 or len(signal_targets) != 1:
            result["blocked_reason"] = "reconstruction requires exactly one signal target"
        else:
            # Local import avoids the rtl_ast <-> debug dependency cycle at
            # module import time; debug uses this module for the solver gate.
            from .debug import generate_filtered_dut
            filtered = generate_filtered_dut(source, signal=signal_targets[0]["name"], source_revision=source_revision, output=output)
            result["filtered_dut"] = filtered
            if filtered.get("status") == "ready":
                result.update({"status": "ready", "output": filtered.get("output"), "filtered_sha256": filtered.get("filtered_sha256"), "target": signal_targets[0]["id"]})
            else:
                result["blocked_reason"] = str(filtered.get("blocked_reason", "source reconstruction was blocked"))
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def verify_functional_partition_reconstruction(
    reconstruction: dict[str, Any],
    cdfg: dict[str, Any],
    partition: dict[str, Any],
) -> list[str]:
    """Verify a reconstruction result before downstream use.

    Hashes are checked against the current source and emitted file, and both
    structural inputs must be the exact artifacts named by the result.  This
    keeps a stale or tampered filtered DUT from being treated as partition
    evidence merely because it compiles.
    """
    errors: list[str] = []
    errors.extend(verify_parser_cdfg_partition(cdfg, partition))
    if reconstruction.get("schema_version") != "rtl-functional-partition-reconstruction-v1":
        errors.append("unsupported functional partition reconstruction schema")
    if reconstruction.get("source_cdfg_sha256") != cdfg.get("cdfg_sha256"):
        errors.append("functional reconstruction is not bound to the source CDFG")
    if reconstruction.get("partition_sha256") != partition.get("partition_sha256"):
        errors.append("functional reconstruction is not bound to the source partition")
    source = Path(str(reconstruction.get("source", "")))
    if not source.is_file():
        errors.append("functional reconstruction source is missing")
    elif reconstruction.get("source_sha256") != sha256_file(source):
        errors.append("functional reconstruction source digest does not match")
    output = Path(str(reconstruction.get("output", ""))) if reconstruction.get("output") else None
    if reconstruction.get("status") == "ready":
        if output is None or not output.is_file():
            errors.append("ready functional reconstruction output is missing")
        elif reconstruction.get("filtered_sha256") != sha256_file(output):
            errors.append("functional reconstruction output digest does not match")
    body = {key: value for key, value in reconstruction.items() if key != "result_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if reconstruction.get("result_sha256") != expected:
        errors.append("functional reconstruction self-digest does not match")
    if reconstruction.get("status") not in {"ready", "blocked"}:
        errors.append("functional reconstruction has invalid status")
    if reconstruction.get("status") == "blocked" and not reconstruction.get("blocked_reason"):
        errors.append("blocked functional reconstruction has no reason")
    return errors


def partition_structural_ir(
    ir: dict[str, Any],
    *,
    module: str | None = None,
    max_items: int = 32,
) -> dict[str, Any]:
    """Create deterministic structural partitions from the extracted IR.

    A partition is a context-selection artifact, not a functional RTL
    replacement.  The manifest records exactly what was selected and carries
    the source IR digest so an agent cannot silently expand its context.
    """
    errors = verify_structural_ir(ir)
    if errors:
        raise ValueError("cannot partition invalid structural IR: " + "; ".join(errors))
    if ir.get("status") != "passed":
        raise ValueError("cannot partition blocked structural IR")
    if max_items <= 0:
        raise ValueError("max_items must be positive")
    modules = ir.get("modules", {})
    selected = [module] if module else sorted(modules)
    if any(name not in modules for name in selected):
        raise ValueError("requested structural module is not present")
    partitions: list[dict[str, Any]] = []
    for name in selected:
        structural = modules[name]
        cells = sorted(structural.get("cells", []))
        netnames = sorted(structural.get("netnames", []))
        ports = sorted(structural.get("ports", []))
        # Keep ports in every context and partition only the potentially large
        # cell/netname inventory into bounded, stable chunks.
        items = [("cell", item) for item in cells] + [("netname", item) for item in netnames]
        for offset in range(0, len(items) or 1, max_items):
            selected_items = items[offset:offset + max_items]
            partitions.append({
                "partition_id": f"{name}:{offset // max_items}",
                "module": name,
                "ports": ports,
                "cells": [item for kind, item in selected_items if kind == "cell"],
                "netnames": [item for kind, item in selected_items if kind == "netname"],
                "scope": "structural-context-only",
                "functional_equivalence_proven": False,
            })
    result: dict[str, Any] = {
        "schema_version": "rtl-structural-partitions-v1",
        "source_ir_sha256": ir["ir_sha256"],
        "top": ir["top"],
        "max_items": max_items,
        "partitions": partitions,
    }
    body = {key: value for key, value in result.items() if key != "partitions_sha256"}
    result["partitions_sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def verify_structural_partitions(ir: dict[str, Any], partitions: dict[str, Any]) -> list[str]:
    errors = []
    if partitions.get("schema_version") != "rtl-structural-partitions-v1":
        errors.append("unsupported structural partition schema")
    if partitions.get("source_ir_sha256") != ir.get("ir_sha256"):
        errors.append("structural partitions are not bound to the source IR")
    body = {key: value for key, value in partitions.items() if key != "partitions_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if partitions.get("partitions_sha256") != expected:
        errors.append("structural partition self-digest does not match")
    seen_cells: list[str] = []
    seen_netnames: list[str] = []
    for partition in partitions.get("partitions", []):
        module = partition.get("module")
        if module not in ir.get("modules", {}):
            errors.append(f"partition references unknown module: {module}")
            continue
        source = ir["modules"][module]
        if sorted(partition.get("ports", [])) != sorted(source.get("ports", [])):
            errors.append(f"partition ports do not match module: {module}")
        seen_cells.extend(f"{module}:{item}" for item in partition.get("cells", []))
        seen_netnames.extend(f"{module}:{item}" for item in partition.get("netnames", []))
    for module, source in ir.get("modules", {}).items():
        expected_cells = {f"{module}:{item}" for item in source.get("cells", [])}
        expected_netnames = {f"{module}:{item}" for item in source.get("netnames", [])}
        if set(seen_cells) != expected_cells:
            errors.append(f"partition cell inventory does not match module: {module}")
        if set(seen_netnames) != expected_netnames:
            errors.append(f"partition netname inventory does not match module: {module}")
    return errors


def run_functional_equivalence(
    reference_sources: list[str | Path],
    candidate_sources: list[str | Path],
    *,
    reference_top: str,
    candidate_top: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
    flatten: bool = False,
) -> dict[str, Any]:
    """Run a bounded Yosys equivalence check for a reconstructed partition.

    The two tops must have compatible interfaces and distinct module names.
    Equivalence is reported only when Yosys completes ``equiv_status -assert``;
    a compiled candidate or a structural match alone is never treated as proof.
    """
    if not reference_sources or not candidate_sources or not reference_top or not candidate_top or not source_revision:
        raise ValueError("reference/candidate sources, tops, and source_revision are required")
    if reference_top == candidate_top:
        raise ValueError("reference and candidate tops must be distinct")
    root = Path(run_root)
    output = root / "equivalence.json"
    reads = "; ".join(f"read_verilog -sv {Path(source).resolve()}" for source in [*reference_sources, *candidate_sources])
    flatten_pass = " flatten;" if flatten else ""
    # `equiv_make` requires process/memory lowering on older Yosys releases;
    # perform it explicitly so sequential filtered DUTs use the same gate as
    # combinational candidates.
    script = f"{reads}; proc; equiv_make {reference_top} {candidate_top} equiv; prep -top equiv;{flatten_pass} equiv_simple; equiv_induct; equiv_status -assert; write_json {output.resolve()}"
    tool_run = run_command(
        ["yosys", "-p", script],
        tool="yosys-equivalence",
        run_root=root,
        source_revision=source_revision,
        timeout_seconds=timeout_seconds,
        expected_artifacts=["equivalence.json"],
        run_id="equivalence",
    )
    result: dict[str, Any] = {
        "schema_version": "rtl-functional-equivalence-v1",
        "status": "proven" if tool_run.status == "passed" else "blocked",
        "reference_top": reference_top,
        "candidate_top": candidate_top,
        "reference_sources": [str(Path(source).resolve()) for source in reference_sources],
        "candidate_sources": [str(Path(source).resolve()) for source in candidate_sources],
        "source_revision": source_revision,
        "tool_run": asdict(tool_run),
    }
    if tool_run.status != "passed":
        result["blocked_reason"] = "equivalence solver did not prove the candidate"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "functional-equivalence.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
