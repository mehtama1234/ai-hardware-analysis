from verification_platform.hypothesis import build_competing_hypotheses


def test_competing_hypotheses_are_balanced_and_ranked():
    result = build_competing_hypotheses(
        {"status": "available", "result_sha256": "c", "candidates": [
            {"file": "dut.sv", "line": 8, "text": "assign q = a;", "reason": "direct structural driver of the first divergent frontier event"},
            {"file": "dut.sv", "line": 4, "text": "assign a = b;", "reason": "direct RTL assignment to the first divergent frontier signal; selector/data dependencies require review"},
        ]},
        for_evidence=["output mismatch"], against_evidence=["implementation may be intentional"],
    )
    assert result["status"] == "available"
    assert result["hypotheses"][0]["line"] == 8
    assert result["hypotheses"][0]["status"] == "review_required"
    assert result["hypotheses"][0]["against_evidence"]
    assert result["hypotheses_sha256"]


def test_competing_hypotheses_fail_closed_without_candidates():
    result = build_competing_hypotheses({"status": "blocked"}, for_evidence=["x"], against_evidence=["y"])
    assert result["status"] == "blocked"
