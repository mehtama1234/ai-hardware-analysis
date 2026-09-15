import hashlib
import json
import pytest

from verification_platform.alignment import align_cdfg_signals, align_signals, aligned_state_frontier


def test_alignment_uses_name_and_cycle_trace_evidence():
    trace = [(0, "0"), (5, "1")]
    result = align_signals({"golden_count": trace}, {"rtl_state": trace})
    item = result["alignments"][0]
    assert item["status"] == "aligned"
    assert item["rtl"] == "rtl_state"
    assert item["score"] == 0.45
    assert "cycle_trace_agreement" in item["reasons"]
    body = {key: value for key, value in result.items() if key != "alignment_sha256"}
    assert result["alignment_sha256"] == hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_alignment_discloses_ties():
    trace = [(0, "0"), (5, "1")]
    result = align_signals({"count": trace}, {"lane_a": trace, "lane_b": trace})
    item = result["alignments"][0]
    assert item["status"] == "ambiguous"
    assert result["ambiguous_count"] == 1
    assert item["rtl"] is None


def test_explicit_mapping_can_resolve_nonmatching_names():
    result = align_signals({"golden_count": [(0, "0")]}, {"state_q": [(0, "0")]}, explicit={"golden_count": "state_q"})
    item = result["alignments"][0]
    assert item["status"] == "explicit" and item["rtl"] == "state_q"


def test_alignment_uses_global_matching_instead_of_greedy_choice():
    result = align_signals(
        {"golden_count": [(0, "0"), (1, "1")], "golden_state": [(0, "0")]},
        {"rtl_count": [(0, "0"), (1, "1")], "rtl_state": [(0, "0"), (1, "1")]},
    )
    records = {item["reference"]: item for item in result["alignments"]}
    assert records["golden_count"]["rtl"] == "rtl_count"
    assert records["golden_state"]["rtl"] == "rtl_state"
    assert "global_max_weight_match" in records["golden_count"]["reasons"]


def test_aligned_state_frontier_finds_earliest_internal_divergence():
    reference = {"count": [(0, "0"), (5, "1")], "status": [(0, "0"), (5, "1")]}
    rtl = {"count_q": [(0, "0"), (5, "1")], "status_q": [(0, "0"), (5, "0")]}
    alignment = align_signals(reference, rtl)
    frontier = aligned_state_frontier(reference, rtl, alignment)
    assert frontier["status"] == "diverged"
    assert frontier["reference"] == "status"
    assert frontier["rtl"] == "status_q"
    assert frontier["cycle"] == 1
    assert frontier["divergence_count"] == 1
    assert frontier["divergences"][0]["reference"] == "status"


def test_aligned_state_frontier_retains_multiple_competing_frontiers():
    reference = {"first": [(0, "0"), (5, "1")], "second": [(0, "0"), (5, "1")]}
    rtl = {"first_q": [(0, "0"), (5, "0")], "second_q": [(0, "0"), (5, "0")]}
    alignment = align_signals(reference, rtl, explicit={"first": "first_q", "second": "second_q"})
    frontier = aligned_state_frontier(reference, rtl, alignment)
    assert frontier["status"] == "diverged"
    assert frontier["divergence_count"] == 2
    assert [item["reference"] for item in frontier["divergences"]] == ["first", "second"]


def test_aligned_state_frontier_blocks_unresolved_mapping():
    reference = {"state": [(0, "0")]}
    rtl = {"lane_a": [(0, "0")], "lane_b": [(0, "0")]}
    alignment = align_signals(reference, rtl)
    assert aligned_state_frontier(reference, rtl, alignment)["status"] == "blocked"


def test_alignment_can_use_structural_neighbor_similarity():
    trace = [(0, "0"), (1, "1")]
    result = align_signals(
        {"golden_sum": trace}, {"rtl_sum": trace, "rtl_other": trace},
        reference_neighbors={"golden_sum": {"golden_a", "golden_b"}},
        rtl_neighbors={"rtl_sum": {"rtl_a", "rtl_b"}, "rtl_other": {"rtl_x"}},
    )
    item = result["alignments"][0]
    assert item["status"] == "aligned"
    assert item["rtl"] == "rtl_sum"
    assert "structural_neighbor_similarity" in item["reasons"]


def test_cdfg_alignment_derives_structural_neighbors_and_provenance():
    trace = [(0, "0"), (1, "1")]
    reference_cdfg = {
        "nodes": [{"id": "golden_in"}, {"id": "golden_sum"}],
        "edges": [{"source": "golden_in", "target": "golden_sum"}],
    }
    rtl_cdfg = {
        "nodes": [{"id": "rtl_in"}, {"id": "rtl_sum"}],
        "edges": [{"source": "rtl_in", "target": "rtl_sum"}],
    }
    reference_cdfg["cdfg_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in reference_cdfg.items() if key != "cdfg_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    rtl_cdfg["cdfg_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in rtl_cdfg.items() if key != "cdfg_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    result = align_cdfg_signals(
        reference_cdfg,
        rtl_cdfg,
        {"golden_in": trace, "golden_sum": trace},
        {"rtl_in": trace, "rtl_sum": trace},
    )

    assert result["schema_version"] == "cdfg-signal-alignment-v1"
    assert result["reference_cdfg_sha256"] == reference_cdfg["cdfg_sha256"]
    assert result["rtl_edge_count"] == 1
    assert result["alignment"]["aligned_count"] == 2
    assert all(item["score_components"] for item in result["alignment"]["alignments"])
    assert "not proof of semantic equivalence" in result["claim_boundary"]


def test_cdfg_alignment_rejects_tampered_graph():
    graph = {"nodes": [{"id": "golden_q"}], "edges": []}
    graph["cdfg_sha256"] = hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    tampered = {**graph, "nodes": [{"id": "golden_other"}]}
    with pytest.raises(ValueError, match="digest does not match"):
        align_cdfg_signals(graph, tampered, {"golden_q": [(0, "0")]}, {"rtl_q": [(0, "0")]})


def test_cdfg_alignment_uses_node_role_and_degree_for_renamed_signals():
    reference = {"nodes": [{"id": "golden_state", "kind": "signal"}, {"id": "golden_a", "kind": "signal"}, {"id": "golden_b", "kind": "signal"}], "edges": [{"source": "golden_a", "target": "golden_state"}, {"source": "golden_state", "target": "golden_b"}]}
    rtl = {"nodes": [{"id": "rtl_alpha", "kind": "signal"}, {"id": "rtl_a", "kind": "signal"}, {"id": "rtl_b", "kind": "signal"}, {"id": "rtl_beta", "kind": "signal"}], "edges": [{"source": "rtl_a", "target": "rtl_alpha"}, {"source": "rtl_alpha", "target": "rtl_b"}]}
    for graph in (reference, rtl):
        graph["cdfg_sha256"] = hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    trace = [(0, "0"), (1, "1")]
    result = align_cdfg_signals(reference, rtl, {"golden_state": trace}, {"rtl_alpha": trace, "rtl_beta": trace})
    item = result["alignment"]["alignments"][0]
    assert item["status"] == "aligned"
    assert item["rtl"] == "rtl_alpha"
    assert "cdfg_node_role_and_degree_similarity" in item["reasons"]
    assert "node_role_and_degree" in item["score_components"]


def test_cdfg_alignment_normalizes_hierarchical_parser_ids_to_trace_names():
    reference = {
        "nodes": [
            {"id": "golden:signal:state", "name": "golden_state", "kind": "signal"},
            {"id": "golden:signal:input", "name": "golden_input", "kind": "signal"},
        ],
        "edges": [{"source": "golden:signal:input", "target": "golden:signal:state"}],
    }
    rtl = {
        "nodes": [
            {"id": "dut:signal:q", "name": "rtl_q", "kind": "signal"},
            {"id": "dut:signal:in", "name": "rtl_in", "kind": "signal"},
        ],
        "edges": [{"source": "dut:signal:in", "target": "dut:signal:q"}],
    }
    for graph in (reference, rtl):
        graph["cdfg_sha256"] = hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    trace = [(0, "0"), (1, "1")]
    result = align_cdfg_signals(
        reference, rtl,
        {"golden_state": trace}, {"rtl_q": trace},
    )
    item = result["alignment"]["alignments"][0]
    assert item["status"] == "aligned"
    assert item["rtl"] == "rtl_q"
