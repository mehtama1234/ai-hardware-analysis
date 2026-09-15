from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.logic import dependency_cdfg, dependency_cone, dependency_graph, dependency_locations, dependency_paths


def test_dependency_cone_follows_assignments(tmp_path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("assign out = state + enable;\nassign state = input_data;\n", encoding="utf-8")
    assert dependency_cone(rtl, "out") == {"state", "enable", "input_data"}


def test_dependency_cone_includes_procedural_guard_and_ignores_literals(tmp_path):
    rtl = tmp_path / "counter.sv"
    rtl.write_text("always @(posedge clk) if (enable) counter_q <= counter_q + 4'd1;\n", encoding="utf-8")
    assert dependency_cone(rtl, "counter_q") == {"enable"}


def test_dependency_graph_and_paths_preserve_causal_backtrace(tmp_path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("assign out = state + enable;\nassign state = input_data;\n", encoding="utf-8")
    assert dependency_graph(rtl) == {"out": {"state", "enable"}, "state": {"input_data"}}
    assert dependency_paths(rtl, "out") == [["out", "enable"], ["out", "state", "input_data"]]


def test_dependency_cdfg_is_bounded_and_source_located(tmp_path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("assign out = state + enable;\nassign state = input_data;\n", encoding="utf-8")
    cdfg = dependency_cdfg(rtl, {"out"})
    assert cdfg["schema_version"] == "dependency-cdfg-v1"
    assert {node["id"] for node in cdfg["nodes"]} == {"out", "state", "enable", "input_data"}
    assert any(edge["source"] == "state" and edge["locations"][0]["line"] == 1 for edge in cdfg["edges"])
    assert cdfg["cdfg_sha256"]


def test_dependency_locations_bind_driver_to_source_line(tmp_path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut;\nassign out = enable;\nendmodule\n", encoding="utf-8")
    assert dependency_locations(rtl)[("out", "enable")] == [{"file": str(rtl), "line": 2}]
