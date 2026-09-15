import hashlib
import json

from verification_platform.optimization import OptimizationRun, append_optimization_result, build_optimization_state, decide_fidelity_promotion, load_openlane_metrics, load_optimization_state, record_optimization_result, run_fidelity_command, select_next_candidate, verify_optimization_state, write_optimization_state


def test_optimization_state_calculates_pareto_frontier():
    state = build_optimization_state([
        OptimizationRun({"utilization": 0.5}, {"wns": -0.2, "area": 100, "power": 10}, "passed"),
        OptimizationRun({"utilization": 0.6}, {"wns": 0.1, "area": 110, "power": 9}, "passed"),
        OptimizationRun({"utilization": 0.7}, {"wns": -1.0, "area": 120, "power": 12}, "failed", failure_reason="routing overflow"),
    ])
    assert state.pareto_frontier == (0, 1)
    assert verify_optimization_state(state) == []


def test_optimization_state_rejects_failed_run_without_reason():
    try:
        OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "failed").validate()
    except ValueError as error:
        assert "failure reason" in str(error)
    else:
        raise AssertionError("invalid failed run was accepted")


def test_optimization_result_rejects_mismatched_configuration_digest():
    state = build_optimization_state([])
    recommendation = select_next_candidate(state, [{"candidate": {"x": 1}, "predicted_metrics": {"wns": 0, "area": 1, "power": 1}}])
    try:
        record_optimization_result(
            state, recommendation, fidelity="proxy", metrics={"wns": 0, "area": 1, "power": 1},
            status="passed", configuration_digest="0" * 64,
        )
    except ValueError as error:
        assert "configuration digest" in str(error)
    else:
        raise AssertionError("mismatched optimization configuration was accepted")


def test_optimization_result_rejects_mismatched_source_digest():
    state = build_optimization_state([])
    recommendation = select_next_candidate(state, [{"candidate": {"x": 1}, "predicted_metrics": {"wns": 0, "area": 1, "power": 1}}])
    recommendation["source_digest"] = "a" * 64
    try:
        record_optimization_result(
            state, recommendation, fidelity="full", metrics={"wns": 0, "area": 1, "power": 1},
            status="passed", source_digest="b" * 64,
        )
    except ValueError as error:
        assert "source digest" in str(error)
    else:
        raise AssertionError("mismatched optimization source was accepted")


def test_optimization_frontier_tampering_is_detected():
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    tampered = type(state)(state.priors, state.rules, state.sensitivities, state.runs, (99,))
    assert "inconsistent" in verify_optimization_state(tampered)[0]


def test_candidate_selection_is_budgeted_and_provenance_bound():
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    recommendation = select_next_candidate(state, [
        {"candidate": {"x": 3}, "predicted_metrics": {"wns": 0.3, "area": 90, "power": 8}, "estimated_runtime_seconds": 20},
        {"candidate": {"x": 2}, "predicted_metrics": {"wns": 0.2, "area": 80, "power": 7}, "estimated_runtime_seconds": 5},
    ], max_runtime_seconds=10)
    assert recommendation["candidate"] == {"x": 2}
    assert recommendation["measured"] is False
    assert recommendation["state_sha256"] == state.digest()


def test_candidate_selection_fails_when_budget_has_no_candidate():
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    try:
        select_next_candidate(state, [{"candidate": {"x": 2}, "predicted_metrics": {"wns": 1, "area": 1, "power": 1}, "estimated_runtime_seconds": 11}], max_runtime_seconds=10)
    except ValueError as error:
        assert "runtime budget" in str(error)
    else:
        raise AssertionError("budget-ineligible proposal was selected")


def test_candidate_selection_supports_explicit_search_modes():
    state = build_optimization_state([
        OptimizationRun({"x": 1, "y": 1}, {"wns": 0, "area": 1, "power": 1}, "passed"),
    ], priors={"candidate": {"x": 0, "y": 0}})
    proposals = [
        {"candidate": {"x": 1, "y": 1}, "predicted_metrics": {"wns": 1, "area": 1, "power": 1}},
        {"candidate": {"x": 2, "y": 2}, "predicted_metrics": {"wns": 0, "area": 2, "power": 2}, "repair": True},
    ]
    assert select_next_candidate(state, proposals, mode="explore")["candidate"] == {"x": 2, "y": 2}
    assert select_next_candidate(state, proposals, mode="repair")["candidate"] == {"x": 2, "y": 2}
    assert select_next_candidate(state, proposals, mode="prior_refinement")["candidate"] == {"x": 1, "y": 1}
    assert select_next_candidate(state, proposals, mode="diversify")["candidate"] == {"x": 2, "y": 2}


def test_candidate_selection_rejects_unknown_search_mode():
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    try:
        select_next_candidate(state, [], mode="random")
    except ValueError as error:
        assert "search mode" in str(error)
    else:
        raise AssertionError("unknown search mode was accepted")


def test_proxy_metrics_promote_only_when_all_limits_pass():
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    recommendation = select_next_candidate(state, [{"candidate": {"x": 2}, "predicted_metrics": {"wns": 1, "area": 1, "power": 1}}])
    decision = decide_fidelity_promotion(recommendation, {"wns": 0.1, "area": 90, "power": 8}, minimum_wns=0, maximum_area=100, maximum_power=10)
    assert decision["decision"] == "promote_to_full"
    rejected = decide_fidelity_promotion(recommendation, {"wns": -1, "area": 90, "power": 8}, minimum_wns=0, maximum_area=100, maximum_power=10)
    assert rejected["decision"] == "reject_at_proxy"
    assert "proxy WNS" in rejected["reasons"][0]


def test_measured_result_is_appended_only_to_matching_state():
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    recommendation = select_next_candidate(state, [{"candidate": {"x": 2}, "predicted_metrics": {"wns": 1, "area": 1, "power": 1}}])
    updated = record_optimization_result(state, recommendation, fidelity="proxy", metrics={"wns": 0.2, "area": 2, "power": 2}, status="passed", runtime_seconds=0.4)
    assert len(updated.runs) == 2
    assert updated.runs[-1].fidelity == "proxy"
    assert verify_optimization_state(updated) == []
    recommendation["state_sha256"] = "wrong"
    try:
        record_optimization_result(state, recommendation, fidelity="full", metrics={"wns": 0, "area": 1, "power": 1}, status="passed")
    except ValueError as error:
        assert "different state" in str(error)
    else:
        raise AssertionError("state-mismatched result was accepted")


def test_fidelity_command_requires_and_parses_metrics_artifact(tmp_path):
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    recommendation = select_next_candidate(state, [{"candidate": {"x": 2}, "predicted_metrics": {"wns": 1, "area": 1, "power": 1}}])
    result = run_fidelity_command(
        recommendation,
        ["python3", "-c", "import json; json.dump({'wns': 0.2, 'area': 2, 'power': 3}, open('metrics.json', 'w'))"],
        fidelity="proxy", run_root=tmp_path / "proxy", source_revision="test-v1",
    )
    assert result["status"] == "passed"
    assert result["metrics"] == {"wns": 0.2, "area": 2, "power": 3}
    assert result["metrics_artifact"]["path"] == "metrics.json"
    assert len(result["metrics_artifact"]["sha256"]) == 64
    assert result["metrics_artifact_path"] == "metrics.json"
    assert result["recommendation_state_sha256"] == state.digest()


def test_optimization_run_rejects_invalid_metrics_artifact_digest():
    try:
        OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed", metrics_artifact_sha256="not-a-digest").validate()
    except ValueError as error:
        assert "metrics_artifact_sha256" in str(error)
    else:
        raise AssertionError("invalid metrics artifact digest was accepted")


def test_optimization_run_rejects_invalid_source_and_configuration_digests():
    for field in ("source_digest", "configuration_digest"):
        kwargs = {field: "not-a-digest"}
        try:
            OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed", **kwargs).validate()
        except ValueError as error:
            assert field in str(error)
        else:
            raise AssertionError(f"invalid {field} was accepted")


def test_optimization_run_rejects_absolute_metrics_artifact_path():
    try:
        OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed", metrics_artifact_path="/tmp/metrics.json").validate()
    except ValueError as error:
        assert "metrics_artifact_path" in str(error)
    else:
        raise AssertionError("absolute metrics artifact path was accepted")


def test_fidelity_command_blocks_malformed_metrics(tmp_path):
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    recommendation = select_next_candidate(state, [{"candidate": {"x": 2}, "predicted_metrics": {"wns": 1, "area": 1, "power": 1}}])
    result = run_fidelity_command(
        recommendation, ["python3", "-c", "open('metrics.json', 'w').write('{}')"],
        fidelity="full", run_root=tmp_path / "full", source_revision="test-v1",
    )
    assert result["status"] == "blocked"
    assert "invalid measured metrics" in result["failure_reason"]


def test_openlane_metrics_are_mapped_to_common_qor_contract(tmp_path):
    metrics = tmp_path / "run" / "reports" / "metrics.csv"
    metrics.parent.mkdir(parents=True)
    metrics.write_text("DIEAREA_mm^2,spef_wns,total_power\n0.12,-0.4,2.5\n", encoding="utf-8")
    assert load_openlane_metrics(metrics.parents[1]) == {"wns": -0.4, "area": 0.12, "power": 2.5}


def test_openlane_metrics_fail_closed_when_power_is_missing(tmp_path):
    metrics = tmp_path / "run" / "reports" / "metrics.csv"
    metrics.parent.mkdir(parents=True)
    metrics.write_text("DIEAREA_mm^2,spef_wns\n0.12,-0.4\n", encoding="utf-8")
    try:
        load_openlane_metrics(metrics.parents[1])
    except ValueError as error:
        assert "missing power" in str(error)
    else:
        raise AssertionError("incomplete OpenLane metrics were accepted")


def test_openlane_metrics_reject_conflicting_aliases(tmp_path):
    metrics = tmp_path / "run" / "reports" / "metrics.csv"
    metrics.parent.mkdir(parents=True)
    metrics.write_text("DIEAREA_mm^2,CoreArea_um^2,spef_wns,total_power\n0.12,0.13,-0.4,2.5\n", encoding="utf-8")
    try:
        load_openlane_metrics(metrics.parents[1])
    except ValueError as error:
        assert "conflicting area aliases" in str(error)
    else:
        raise AssertionError("conflicting QoR aliases were accepted")


def test_persisted_optimization_state_is_digest_checked(tmp_path):
    path = tmp_path / "optimization" / "state.json"
    state = build_optimization_state([OptimizationRun({"x": 1}, {"wns": 0, "area": 1, "power": 1}, "passed")])
    write_optimization_state(state, str(path))
    assert load_optimization_state(path).digest() == state.digest()
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["priors"] = {"candidate": {"x": 9}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    try:
        load_optimization_state(path)
    except ValueError as error:
        assert "digest" in str(error)
    else:
        raise AssertionError("tampered persisted optimization state was accepted")


def test_append_optimization_result_rejects_stale_agent_and_preserves_history(tmp_path):
    path = tmp_path / "state.json"
    state = build_optimization_state([])
    write_optimization_state(state, str(path))
    recommendation = select_next_candidate(state, [{"candidate": {"x": 2}, "predicted_metrics": {"wns": 1, "area": 2, "power": 3}}])
    updated = append_optimization_result(path, recommendation, fidelity="proxy", metrics={"wns": 0.5, "area": 2, "power": 3}, status="passed")
    assert len(updated.runs) == 1
    assert load_optimization_state(path).runs == updated.runs
    try:
        append_optimization_result(path, recommendation, fidelity="full", metrics={"wns": 0.6, "area": 2, "power": 3}, status="passed")
    except ValueError as error:
        assert "different state" in str(error)
    else:
        raise AssertionError("stale optimization recommendation was accepted")
