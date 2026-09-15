import json
from pathlib import Path

from verification_platform.causal import TraceEvent, bind_frontier_to_causal_graph, build_causal_graph, build_causal_timeline, causal_graph_from_vcd, rank_frontier_root_causes, state_frontier, trace_events, verify_causal_graph, verify_causal_timeline, write_causal_graph


def test_causal_graph_contains_temporal_and_driver_edges(tmp_path: Path):
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \" out $end\n$enddefinitions $end\n#0\n0!\n0\"\n#5\n1!\n1\"\n#10\n0!\n0\"\n", encoding="utf-8")
    events = trace_events(wave, ["out", "enable"])
    graph = build_causal_graph(events, {"out": {"enable"}})
    assert len(graph["nodes"]) == 6
    assert any(edge["kind"] == "structural" for edge in graph["edges"])
    assert any(edge["kind"] == "temporal" for edge in graph["edges"])
    body = {key: value for key, value in graph.items() if key != "graph_sha256"}
    import hashlib
    assert graph["graph_sha256"] == hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert write_causal_graph(tmp_path / "causal.json", graph).is_file()
    assert verify_causal_graph(graph) == []


def test_causal_graph_verifier_rejects_tampering_and_cycles():
    graph = build_causal_graph(
        [TraceEvent("e0", "a", 0, "0"), TraceEvent("e1", "b", 1, "1")],
        {"b": {"a"}},
    )
    graph["edges"].append({"source": "e1", "target": "e0", "kind": "structural"})
    assert "causal graph contains a cycle" in verify_causal_graph(graph)


def test_state_frontier_reports_first_divergent_cycle():
    result = state_frontier([(0, "0"), (5, "1"), (10, "2")], [(0, "0"), (5, "0"), (10, "2")], signal="counter_q")
    assert result == {"status": "diverged", "signal": "counter_q", "index": 1, "cycle": 1, "time": 5, "observed": "1", "reference": "0", "prior_cycles_agreed": 1}


def test_state_frontier_fails_closed_on_incomplete_trace():
    result = state_frontier([(0, "0")], [(0, "0"), (5, "1")], signal="q")
    assert result["status"] == "incomplete"


def test_frontier_binds_to_causal_event_and_source_location(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut;\nassign out = enable;\nendmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \\\" out $end\n$enddefinitions $end\n#0\n0!\n0\\\"\n#5\n1!\n1\\\"\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    frontier = state_frontier([(0, "0"), (5, "1")], [(0, "0"), (5, "0")], signal="out")
    binding = bind_frontier_to_causal_graph(frontier, graph)
    assert binding["status"] == "available"
    assert binding["source_locations"][0]["line"] == 2


def test_frontier_binding_rejects_tampered_causal_graph(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut; assign out = enable; endmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \\\" out $end\n$enddefinitions $end\n#0\n0!\n0\\\"\n#5\n1!\n1\\\"\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    graph["nodes"].append({"id": "tampered", "signal": "out", "time": 5, "value": "x"})
    frontier = state_frontier([(0, "0"), (5, "1")], [(0, "0"), (5, "0")], signal="out")
    binding = bind_frontier_to_causal_graph(frontier, graph)
    assert binding["status"] == "blocked"
    assert "validation failed" in binding["reason"]


def test_causal_graph_from_vcd_attaches_rtl_digest_and_locations(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut;\nassign out = enable;\nendmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \\\" out $end\n$enddefinitions $end\n#0\n0!\n0\\\"\n#5\n1!\n1\\\"\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    structural = [edge for edge in graph["edges"] if edge["kind"] == "structural"]
    assert graph["rtl_sha256"]
    assert structural and structural[0]["rtl_locations"][0]["line"] == 2


def test_frontier_root_causes_are_source_bound_and_ranked(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut;\nassign mid = enable;\nassign out = mid;\nendmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \" mid $end\n$var wire 1 # out $end\n$enddefinitions $end\n#0\n0!\n0\"\n0#\n#5\n1!\n1\"\n1#\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    frontier = state_frontier([(0, "0"), (5, "1")], [(0, "0"), (5, "0")], signal="out")
    binding = bind_frontier_to_causal_graph(frontier, graph)
    result = rank_frontier_root_causes(binding, rtl)
    assert result["status"] == "available"
    assert result["candidates"][0]["line"] == 3
    assert result["candidates"][0]["text"] == "assign out = mid;"
    assert result["rtl_sha256"]


def test_frontier_root_causes_fail_closed_on_binding_tamper(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut; assign out = enable; endmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \" out $end\n$enddefinitions $end\n#0\n0!\n0\"\n#5\n1!\n1\"\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    frontier = state_frontier([(0, "0"), (5, "1")], [(0, "0"), (5, "0")], signal="out")
    binding = bind_frontier_to_causal_graph(frontier, graph)
    binding["source_locations"][0]["line"] = 99
    result = rank_frontier_root_causes(binding, rtl)
    assert result["status"] == "blocked"
    assert "digest" in result["blocked_reason"]


def test_causal_timeline_is_frontier_anchored_and_cycle_ordered(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut;\nassign mid = enable;\nassign out = mid;\nendmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \" mid $end\n$var wire 1 # out $end\n$enddefinitions $end\n#0\n0!\n0\"\n0#\n#5\n1!\n1\"\n1#\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    frontier = state_frontier([(0, "0"), (5, "1")], [(0, "0"), (5, "0")], signal="out")
    binding = bind_frontier_to_causal_graph(frontier, graph)
    timeline = build_causal_timeline(graph, frontier_node=binding["frontier_node"])
    assert timeline["status"] == "available"
    assert timeline["frontier_node"] == binding["frontier_node"]
    assert [event["time"] for event in timeline["events"]] == sorted(event["time"] for event in timeline["events"])
    assert timeline["events"][-1]["event_id"] == binding["frontier_node"]
    assert timeline["timeline_sha256"]
    assert verify_causal_timeline(timeline, graph) == []


def test_causal_timeline_verifier_rejects_tampering(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut; assign out = enable; endmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \" out $end\n$enddefinitions $end\n#0\n0!\n0\"\n#5\n1!\n1\"\n", encoding="utf-8")
    graph = causal_graph_from_vcd(wave, rtl, ["out"])
    frontier = state_frontier([(0, "0"), (5, "1")], [(0, "0"), (5, "0")], signal="out")
    binding = bind_frontier_to_causal_graph(frontier, graph)
    timeline = build_causal_timeline(graph, frontier_node=binding["frontier_node"])
    timeline["events"][0]["value"] = "tampered"
    errors = verify_causal_timeline(timeline, graph)
    assert any("disagrees with graph" in error or "self-digest" in error for error in errors)
