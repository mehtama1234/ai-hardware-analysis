import pytest
from pathlib import Path

from .repository_agent import build_repository_agent_requests, run_repository_agent


def test_repository_agent_builds_bounded_cross_role_trajectory():
    requests = build_repository_agent_requests(task_id="task-1", source_revision="rev-1", evidence=["failure.log", "counterexample.vcd"], failure_context="counterexample at cycle 4")
    assert len(requests) == 4
    assert {item["role"] for item in requests} == {"diagnostician", "reviewer", "repair_proposer"}
    assert all(item["allowed_source_revision"] == "rev-1" for item in requests)
    assert all(item["evidence"] == ["failure.log", "counterexample.vcd"] for item in requests)


def test_repository_agent_requires_supported_backend_and_grounding_inputs():
    with pytest.raises(ValueError, match="supported backend"):
        run_repository_agent(task_id="task-1", source_revision="rev-1", evidence=["failure.log"], failure_context="failure", backend="unsupported")
    with pytest.raises(ValueError, match="failure_context"):
        build_repository_agent_requests(task_id="task-1", source_revision="rev-1", evidence=["failure.log"], failure_context=" ")
    with pytest.raises(ValueError, match="supplied together"):
        build_repository_agent_requests(task_id="task-1", source_revision="rev-1", evidence=["failure.log"], failure_context="failure", repair_before="old")


def test_repository_agent_binds_exact_repair_choices_to_repair_role():
    requests = build_repository_agent_requests(task_id="task-1", source_revision="rev-1", evidence=["failure.log"], failure_context="failure", repair_before="old", repair_after="new")
    repair = next(item for item in requests if item["role"] == "repair_proposer")
    assert repair["repair_before"] == "old"
    assert repair["repair_after"] == "new"


def test_repository_agent_validates_exact_repair_choices_end_to_end(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {root / 'scripts/mock_repository_agent_backend.py'}")
    source = Path(__file__).resolve().parents[1] / "benchmarks/seeded_counter/counter.sv"
    result = run_repository_agent(task_id="task-1", source_revision="rev-1", evidence=["failure.log"], failure_context="failure", repair_before="else\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard", repair_after="else if (enable)\n      counter_q <= counter_q + 4'd1;", repair_source=source, backend="local")
    assert result["team"]["status"] == "available"
    repair = next(item for item in result["team"]["results"] if item["role"] == "repair_proposer")
    assert repair["grounded"] is True
    assert repair["bounded_repair"]["edit_operator"] == "exact_text_replace"
    assert result["patch_candidate"]["status"] == "review_required"
    assert result["patch_candidate"]["source"] == str(source.resolve())


def test_repository_agent_runs_through_local_jsonl_backend(monkeypatch, tmp_path):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {root / 'scripts/mock_repository_agent_backend.py'}")
    result = run_repository_agent(task_id="seeded-counter-hold", source_revision="counter-v1", evidence=["failure.log", "rtl/counter.sv"], failure_context="counter increments while enable is low", backend="local", output_root=tmp_path)
    assert result["team"]["status"] == "available"
    assert len(result["team"]["handoffs"]) == 4
    assert all(item["proposal"]["status"] == "review_required" for item in result["team"]["results"])
    assert result["claim_boundary"].startswith("bounded repository agent")
    assert (tmp_path / "repository-agent-run.json").is_file()
