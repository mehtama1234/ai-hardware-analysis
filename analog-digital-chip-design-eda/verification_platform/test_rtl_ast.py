import json
import hashlib
from pathlib import Path

import pytest

from verification_platform.rtl_ast import extract_parser_cdfg, extract_structural_ir, partition_parser_cdfg, partition_structural_ir, reconstruct_functional_partition, run_functional_equivalence, verify_functional_partition_reconstruction, verify_parser_cdfg_partition, verify_structural_ir, verify_structural_partitions


def test_yosys_structural_ir_records_hierarchy_and_digest(tmp_path: Path):
    source = tmp_path / "counter.sv"
    source.write_text("module counter(input logic clk, input logic en, output logic q); always_ff @(posedge clk) if (en) q <= 1'b1; endmodule\n", encoding="utf-8")
    ir, tool_run = extract_structural_ir(source, top="counter", run_root=tmp_path / "run", source_revision="counter-v1")
    assert tool_run.status == "passed"
    assert ir["status"] == "passed"
    assert ir["module_count"] == 1
    assert "counter" in ir["modules"]
    assert "q" in ir["modules"]["counter"]["ports"]
    assert verify_structural_ir(ir) == []


def test_structural_ir_rejects_tampering(tmp_path: Path):
    source = tmp_path / "counter.sv"
    source.write_text("module counter(input clk, output q); assign q = clk; endmodule\n", encoding="utf-8")
    ir, _ = extract_structural_ir(source, top="counter", run_root=tmp_path / "run", source_revision="v1")
    ir["top"] = "other"
    assert "structural IR self-digest does not match" in verify_structural_ir(ir)


def test_structural_partitions_are_bounded_and_inventory_preserving(tmp_path: Path):
    source = tmp_path / "design.sv"
    source.write_text("module design(input logic clk, input logic a, output logic y); logic b; assign b = a; assign y = b; endmodule\n", encoding="utf-8")
    ir, _ = extract_structural_ir(source, top="design", run_root=tmp_path / "run", source_revision="v1")
    partitions = partition_structural_ir(ir, max_items=1)
    assert len(partitions["partitions"]) >= 1
    assert all(partition["functional_equivalence_proven"] is False for partition in partitions["partitions"])
    assert verify_structural_partitions(ir, partitions) == []


def test_structural_partitions_reject_tampering(tmp_path: Path):
    source = tmp_path / "design.sv"
    source.write_text("module design(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
    ir, _ = extract_structural_ir(source, top="design", run_root=tmp_path / "run", source_revision="v1")
    partitions = partition_structural_ir(ir)
    partitions["source_ir_sha256"] = "tampered"
    assert any("not bound to the source IR" in error for error in verify_structural_partitions(ir, partitions))


def test_functional_equivalence_requires_solver_proof(tmp_path: Path):
    reference = tmp_path / "gold.sv"
    candidate = tmp_path / "gate.sv"
    reference.write_text("module gold(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
    candidate.write_text("module gate(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
    result = run_functional_equivalence([reference], [candidate], reference_top="gold", candidate_top="gate", run_root=tmp_path / "equiv", source_revision="v1")
    assert result["status"] == "proven"
    assert result["tool_run"]["status"] == "passed"


def test_parser_cdfg_comes_from_elaborated_connectivity(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    result, tool_run = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    assert tool_run.status == "passed"
    assert result["status"] == "passed"
    assert result["scope"] == "yosys-elaborated-signal-cell-connectivity"
    assert result["node_count"] >= 4
    assert any(edge["port"] == "A" for edge in result["edges"])
    assert result["cdfg_sha256"]


def test_parser_cdfg_partition_preserves_backward_functional_cone(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    cdfg, _ = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "y")
    partition = partition_parser_cdfg(cdfg, targets=[target], max_nodes=16)
    assert partition["status"] == "ready"
    assert partition["functional_equivalence_proven"] is False
    assert target in {node["id"] for node in partition["nodes"]}
    assert verify_parser_cdfg_partition(cdfg, partition) == []


def test_parser_cdfg_partition_blocks_overlarge_cone(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    cdfg, _ = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "y")
    partition = partition_parser_cdfg(cdfg, targets=[target], max_nodes=1)
    assert partition["status"] == "blocked"
    assert verify_parser_cdfg_partition(cdfg, partition) == []


def test_parser_cdfg_partition_rejects_omitted_dependency_after_rehash(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    cdfg, _ = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "y")
    partition = partition_parser_cdfg(cdfg, targets=[target], max_nodes=16)
    partition["nodes"] = [node for node in partition["nodes"] if node["id"] != target]
    partition["partition_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in partition.items() if key != "partition_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert any("omits a target" in error or "exact backward" in error for error in verify_parser_cdfg_partition(cdfg, partition))


def test_functional_partition_reconstructs_compile_ready_slice(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    cdfg, _ = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "y")
    partition = partition_parser_cdfg(cdfg, targets=[target], max_nodes=16)
    reconstruction = reconstruct_functional_partition(source, cdfg, partition, output=tmp_path / "filtered.sv", source_revision="v1")
    assert reconstruction["status"] == "ready"
    assert reconstruction["functional_equivalence_proven"] is False
    assert reconstruction["source_cdfg_sha256"] == cdfg["cdfg_sha256"]
    assert verify_functional_partition_reconstruction(reconstruction, cdfg, partition) == []
    assert "module and2" in (tmp_path / "filtered.sv").read_text(encoding="utf-8")


def test_functional_partition_reconstruction_rejects_tampered_output(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    cdfg, _ = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "y")
    partition = partition_parser_cdfg(cdfg, targets=[target], max_nodes=16)
    reconstruction = reconstruct_functional_partition(source, cdfg, partition, output=tmp_path / "filtered.sv", source_revision="v1")
    (tmp_path / "filtered.sv").write_text((tmp_path / "filtered.sv").read_text(encoding="utf-8") + "// tampered\n", encoding="utf-8")
    assert any("output digest does not match" in error for error in verify_functional_partition_reconstruction(reconstruction, cdfg, partition))


def test_functional_partition_reconstruction_rejects_unbound_source(tmp_path: Path):
    source = tmp_path / "and.sv"
    source.write_text("module and2(input logic a, input logic b, output logic y); assign y = a & b; endmodule\n", encoding="utf-8")
    other = tmp_path / "other.sv"
    other.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    cdfg, _ = extract_parser_cdfg(source, top="and2", run_root=tmp_path / "cdfg", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "y")
    partition = partition_parser_cdfg(cdfg, targets=[target], max_nodes=16)
    with pytest.raises(ValueError, match="source is not bound"):
        reconstruct_functional_partition(other, cdfg, partition, output=tmp_path / "filtered.sv", source_revision="v1")
