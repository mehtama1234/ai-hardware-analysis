from pathlib import Path
import hashlib
import json
import sys

import pytest

from verification_platform.orchestration import run_four_workstream_pipeline


def _cdfg(nodes):
    graph = {"nodes": nodes, "edges": []}
    graph["cdfg_sha256"] = hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return graph


def _inputs(tmp_path: Path):
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-A: output resets to zero\n", encoding="utf-8")
    rtl = tmp_path / "design.sv"
    rtl.write_text("module dut(input wire clk, input wire rst, output reg q); always @(posedge clk) if (rst) q <= 1'b0; endmodule\n", encoding="utf-8")
    protocol = tmp_path / "protocol.json"
    protocol.write_text('{"schema_version":"protocol-plan-v1","name":"design","addr_width":8,"data_width":32,"steps":[{"operation":"read","address":0,"expected":0}]}\n', encoding="utf-8")
    return spec, rtl, protocol


def test_four_workstream_pipeline_records_all_stage_statuses(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(spec, [rtl], top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"], tool="python", run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "passed"
    assert {result[key]["status"] for key in ("execution", "scheduling", "structural", "protocol")} == {"passed"}
    assert result["protocol"]["compiler"] == "passed"
    assert result["execution"]["verilator_lint"]["status"] == "passed"
    assert [tier["id"] for tier in result["tiers"]["tiers"]] == ["tier-1", "tier-2", "tier-3", "tier-4", "tier-5", "tier-6"]
    assert result["tiers"]["tiers"][0]["status"] == "passed"
    assert Path(tmp_path / "run/four-workstream-tier-evidence.json").is_file()
    assert result["checkpoint"]["completed"] == ["planning", "scheduling", "structural", "protocol"]
    assert result["checkpoint"]["status"] == "running"
    assert result["debug"]["status"] == "not_run"
    assert (tmp_path / "run/four-workstream-result.json").is_file()
    assert (tmp_path / "run/four-workstream-evidence-manifest.json").is_file()
    assert "four-workstream-evidence-manifest.json" in result["checkpoint"]["completed"] or "four-workstream-evidence-manifest.json" in json.loads((tmp_path / "run/workflow-checkpoint.json").read_text())["artifacts"]


def test_four_workstream_pipeline_records_executable_protocol_progress(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        protocol_execution_command=[sys.executable, "-c", "print('PROTOCOL_SEQUENCE_COVERAGE covered=1 total=1'); print('PROTOCOL_SEQUENCE_RESULT status=passed')"],
        run_root=tmp_path / "run", source_revision="protocol-execution-v1",
    )
    assert result["status"] == "passed"
    assert result["protocol"]["execution"]["status"] == "passed"
    assert result["protocol"]["execution"]["coverage"]["percentage"] == 100.0
    assert result["tiers"]["tiers"][2]["status"] == "passed"


def test_protocol_execution_can_require_generated_sequence_binding(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        protocol_execution_command=[sys.executable, "-c", "print('PROTOCOL_SEQUENCE_COVERAGE covered=1 total=1'); print('PROTOCOL_SEQUENCE_RESULT status=passed')"],
        protocol_require_generated_sequence=True,
        run_root=tmp_path / "run", source_revision="protocol-binding-v1",
    )
    assert result["protocol"]["execution"]["status"] == "blocked"
    assert "generated-sequence binding" in result["protocol"]["execution"]["blocked_reason"]


def test_four_workstream_pipeline_executes_checked_in_protocol_fixture(tmp_path: Path):
    spec, rtl, _ = _inputs(tmp_path)
    platform_root = Path(__file__).resolve().parents[1]
    fixture_root = platform_root / "benchmarks" / "protocol_execution"
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=fixture_root / "protocol_plan.json",
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        protocol_execution_command=[
            sys.executable, str(platform_root / "scripts" / "run_protocol_sequence_fixture.py"),
            str(tmp_path / "run" / "protocol" / "csr_sequence.sv"),
            str(fixture_root / "csr_dut.sv"), str(fixture_root / "tb.sv"),
        ],
        run_root=tmp_path / "run", source_revision="protocol-fixture-v1",
    )
    assert result["status"] == "passed"
    assert result["protocol"]["execution"]["status"] == "passed"
    assert result["protocol"]["execution"]["coverage"] == {"covered": 2, "total": 2, "percentage": 100.0}


def test_four_workstream_pipeline_records_executable_protocol_convergence(tmp_path: Path):
    spec, rtl, _ = _inputs(tmp_path)
    platform_root = Path(__file__).resolve().parents[1]
    fixture_root = platform_root / "benchmarks" / "protocol_execution"
    commands = [
        [sys.executable, "-c", "print('PROTOCOL_SEQUENCE_COVERAGE covered=1 total=2'); print('PROTOCOL_SEQUENCE_RESULT status=passed')"],
        [sys.executable, "-c", "print('PROTOCOL_SEQUENCE_COVERAGE covered=2 total=2'); print('PROTOCOL_SEQUENCE_RESULT status=passed')"],
    ]
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=fixture_root / "protocol_plan.json",
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        protocol_execution_commands=commands,
        run_root=tmp_path / "run", source_revision="protocol-convergence-v1",
    )
    assert result["status"] == "passed"
    assert result["protocol"]["execution"]["status"] == "passed"
    convergence = Path(result["protocol"]["execution_convergence"])
    assert json.loads(convergence.read_text(encoding="utf-8"))["status"] == "converged"
    assert str(convergence.relative_to(tmp_path / "run")) in json.loads((tmp_path / "run/workflow-checkpoint.json").read_text(encoding="utf-8"))["artifacts"]


def test_four_workstream_pipeline_checkpointed_functional_cdfg_partition(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    from verification_platform.rtl_ast import extract_parser_cdfg
    cdfg, _ = extract_parser_cdfg(rtl, top="dut", run_root=tmp_path / "probe", source_revision="v1")
    target = next(node["id"] for node in cdfg["nodes"] if node.get("kind") == "signal" and node.get("name") == "q")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        structural_partition_targets=[target], structural_partition_output=tmp_path / "run/structural/reconstructed.sv",
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1",
    )
    assert result["status"] == "passed"
    partition = result["structural"]["functional_partition"]
    assert partition["status"] == "ready"
    assert Path(tmp_path / "run/structural/functional-cdfg-partition.json").is_file()
    assert result["structural"]["functional_reconstruction"]["status"] == "ready"
    assert result["structural"]["functional_reconstruction_equivalence"]["status"] == "proven"
    assert Path(tmp_path / "run/structural/reconstructed.sv").is_file()


def test_four_workstream_pipeline_integrates_typed_collateral_intake(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v-collateral",
        collateral_entries=[
            {"kind": "specification", "path": spec.name},
            {"kind": "rtl", "path": rtl.name},
            {"kind": "protocol_plan", "path": protocol.name},
        ], collateral_root=tmp_path,
    )
    assert result["status"] == "passed"
    assert result["collateral"]["status"] == "ready"
    assert result["checkpoint"]["completed"][0] == "planning"
    assert Path(result["collateral"]["path"]).is_file()


def test_four_workstream_pipeline_blocks_on_collateral_conflict(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    duplicate = tmp_path / "spec-copy.md"
    duplicate.write_text(spec.read_text(encoding="utf-8"), encoding="utf-8")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v-collateral-blocked",
        collateral_entries=[
            {"kind": "specification", "path": spec.name},
            {"kind": "specification", "path": duplicate.name},
        ], collateral_root=tmp_path,
    )
    assert result["status"] == "blocked"
    assert "collateral" in result["blocked_reasons"]


def test_four_workstream_pipeline_blocks_on_execution_failure(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(spec, [rtl], top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "raise SystemExit(3)"], tool="python", run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "blocked"
    assert "execution" in result["blocked_reasons"]
    assert result["checkpoint"]["status"] == "blocked"


def test_four_workstream_pipeline_gates_explicit_uvm_capability_request(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="uvm-v1", uvm_root=tmp_path / "missing-uvm",
    )
    assert result["status"] == "blocked"
    assert result["uvm"]["status"] == "blocked"
    assert Path(tmp_path / "run/uvm/uvm-runtime-capability.json").is_file()


def test_four_workstream_pipeline_records_explicit_uvm_compile_evidence(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    package = tmp_path / "uvm_pkg.sv"
    package.write_text("package uvm_pkg; endpackage\n", encoding="utf-8")
    simulator = tmp_path / "uvm-simulator"
    simulator.write_text("#!/bin/sh\nprintf 'uvm compile ok\\n'\nexit 0\n", encoding="utf-8")
    simulator.chmod(0o755)
    source = tmp_path / "agent.sv"
    source.write_text("module agent; endmodule\n", encoding="utf-8")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="uvm-compile-v1",
        uvm_root=package, uvm_source=source,
        uvm_compile_command=[str(simulator), str(source)],
    )
    assert result["status"] == "passed"
    assert result["uvm"]["status"] == "passed"
    assert result["uvm"]["compile"]["tool"] == "uvm-compile"
    checkpoint = json.loads((tmp_path / "run/workflow-checkpoint.json").read_text(encoding="utf-8"))
    assert "uvm/compile/uvm-compile-result.json" in checkpoint["artifacts"]


def test_four_workstream_pipeline_records_bounded_uvm_runtime_evidence(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    package = tmp_path / "uvm_pkg.sv"
    package.write_text("package uvm_pkg; endpackage\n", encoding="utf-8")
    simulator = tmp_path / "uvm-simulator"
    simulator.write_text("#!/bin/sh\nprintf 'uvm compile ok\\n'\nexit 0\n", encoding="utf-8")
    simulator.chmod(0o755)
    source = tmp_path / "agent.sv"
    source.write_text("module agent; endmodule\n", encoding="utf-8")
    runtime = tmp_path / "uvm-runtime"
    runtime.write_text("#!/bin/sh\nprintf 'UVM_TEST_PASSED\\n'\nexit 0\n", encoding="utf-8")
    runtime.chmod(0o755)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="uvm-runtime-v1",
        uvm_root=package, uvm_source=source,
        uvm_compile_command=[str(simulator), str(source)],
        uvm_runtime_command=[str(runtime)],
        uvm_runtime_expected_markers=["UVM_TEST_PASSED"],
    )
    assert result["status"] == "passed"
    assert result["uvm"]["runtime"]["status"] == "passed"
    assert result["uvm"]["runtime_observed_markers"] == ["UVM_TEST_PASSED"]


def test_four_workstream_pipeline_rejects_partial_uvm_compile_inputs(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    with pytest.raises(ValueError, match="must be supplied together"):
        run_four_workstream_pipeline(
            spec, [rtl], top="dut", protocol_plan=protocol,
            command=[sys.executable, "-c", "print('ok')"], tool="python",
            run_root=tmp_path / "run", source_revision="uvm-invalid-v1",
            uvm_source=rtl,
        )


def test_four_workstream_pipeline_can_run_debug_and_optimization_inputs(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    waveform = tmp_path / "trace.vcd"
    waveform.write_text("$var wire 1 ! q $end\n$enddefinitions $end\n#0\n0!\n#5\n1!\n", encoding="utf-8")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1", debug_waveform=waveform, debug_rtl=rtl, debug_signal="q",
        debug_observed=[(0, "0"), (5, "1")], debug_reference=[(0, "0"), (5, "0")],
        debug_for_evidence=["q changes at cycle 1"], debug_against_evidence=["assignment is valid"],
        optimization_proposals=[{"candidate": {"utilization": 0.5}, "predicted_metrics": {"wns": 0.1, "area": 10, "power": 2}}],
    )
    assert result["status"] == "passed"
    assert result["debug"]["status"] == "review_required"
    assert result["claim_status"] == "review_required"
    assert "four-workstream-result.json" in json.loads((tmp_path / "run/workflow-checkpoint.json").read_text())["artifacts"]
    assert result["optimization"]["status"] == "ready"
    assert result["checkpoint"]["completed"] == ["planning", "scheduling", "structural", "protocol", "debug", "optimization"]
    assert (tmp_path / "run/debug/debug-package.json").is_file()
    assert (tmp_path / "run/optimization/recommendation.json").is_file()


def test_four_workstream_pipeline_records_cdfg_alignment_artifact(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    waveform = tmp_path / "trace.vcd"
    waveform.write_text("$var wire 1 ! q $end\n$enddefinitions $end\n#0\n0!\n#5\n1!\n", encoding="utf-8")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1", debug_waveform=waveform,
        debug_rtl=rtl, debug_signal="q", debug_observed=[(0, "0"), (5, "1")],
        debug_reference=[(0, "0"), (5, "0")],
        debug_reference_cdfg=_cdfg([{"id": "golden_q"}]),
        debug_rtl_cdfg=_cdfg([{"id": "rtl_q"}]),
        debug_reference_traces={"golden_q": [(0, "0"), (5, "0")]},
        debug_rtl_traces={"rtl_q": [(0, "0"), (5, "1")]},
        debug_for_evidence=["q changes"], debug_against_evidence=["assignment is valid"],
    )
    alignment = result["debug"]["cdfg_alignment"]
    assert alignment["status"] == "available"
    assert alignment["aligned_count"] == 1
    assert Path(alignment["path"]).is_file()


def test_four_workstream_pipeline_augments_protocol_from_coverage_gaps(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        protocol_coverage_gaps=[{"operation": "write", "address": 4, "data": 7}],
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1",
    )
    assert result["status"] == "passed"
    gap_path = Path(result["protocol"]["coverage_gaps"])
    assert gap_path.is_file()
    assert len(json.loads(gap_path.read_text(encoding="utf-8"))["steps"]) == 2
    assert result["checkpoint"]["completed"] == ["planning", "scheduling", "structural", "protocol"]


def test_four_workstream_pipeline_ingests_coverage_report_and_ranks_gaps(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    coverage = tmp_path / "coverage.json"
    coverage.write_text('{"kind":"functional","covered":7,"total":10}\n', encoding="utf-8")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        protocol_coverage_report=coverage,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1",
    )
    assert result["status"] == "passed"
    assert result["protocol"]["coverage_report"]["percentage"] == 70.0
    ranking = Path(result["protocol"]["coverage_ranking"])
    assert json.loads(ranking.read_text(encoding="utf-8"))["gaps"][0]["missing"] == 3


def test_four_workstream_pipeline_records_monotonic_coverage_convergence(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    first = tmp_path / "coverage-first.json"
    second = tmp_path / "coverage-second.json"
    first.write_text('{"kind":"functional","covered":7,"total":10}\n', encoding="utf-8")
    second.write_text('{"kind":"functional","covered":10,"total":10}\n', encoding="utf-8")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        protocol_coverage_reports=[first, second],
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="coverage-convergence-v1",
    )
    assert result["status"] == "passed"
    convergence = Path(result["protocol"]["coverage_convergence"])
    payload = json.loads(convergence.read_text(encoding="utf-8"))
    assert payload["status"] == "converged"
    assert payload["coverage_delta"] == 3
    assert payload["iterations_completed"] == 2
    assert "protocol/coverage-convergence.json" in json.loads((tmp_path / "run/workflow-checkpoint.json").read_text(encoding="utf-8"))["artifacts"]


def test_four_workstream_pipeline_rejects_non_monotonic_coverage(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    first = tmp_path / "coverage-first.json"
    second = tmp_path / "coverage-second.json"
    first.write_text('{"kind":"functional","covered":8,"total":10}\n', encoding="utf-8")
    second.write_text('{"kind":"functional","covered":7,"total":10}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="monotonically"):
        run_four_workstream_pipeline(
            spec, [rtl], top="dut", protocol_plan=protocol,
            protocol_coverage_reports=[first, second],
            command=[sys.executable, "-c", "print('ok')"], tool="python",
            run_root=tmp_path / "run", source_revision="coverage-convergence-blocked-v1",
        )


def test_coverage_ranking_is_bound_into_assertion_agent_context(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    coverage = tmp_path / "coverage.json"
    coverage.write_text('{"kind":"functional","covered":2,"total":3}\n', encoding="utf-8")
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        protocol_coverage_report=coverage,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="coverage-agent-v1",
        assertion_agent_backend="local",
    )
    assert result["status"] == "passed"
    assert result["assertion_agent"]["coverage_gap_ranking"].endswith("protocol/coverage-gaps.json")


def test_rejected_assertion_agent_output_is_checkpointed_as_blocked(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    backend = tmp_path / "invalid-agent.py"
    backend.write_text("print('{}')\n", encoding="utf-8")
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"{sys.executable} {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="blocked-agent-v1",
        assertion_agent_backend="local",
    )
    assert result["status"] == "blocked"
    assert result["assertion_agent"]["status"] == "blocked"
    assert (tmp_path / "run/four-workstream-result.json").is_file()
    assert (tmp_path / "run/workflow-checkpoint.json").is_file()


def test_four_workstream_pipeline_can_checkpoint_optimization_without_debug(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1",
        optimization_proposals=[{
            "candidate": {"utilization": 0.5},
            "predicted_metrics": {"wns": 0.1, "area": 10, "power": 2},
        }],
    )
    assert result["status"] == "passed"
    assert result["debug"]["status"] == "not_run"
    assert result["optimization"]["status"] == "ready"
    assert result["checkpoint"]["completed"] == ["planning", "scheduling", "structural", "protocol", "debug", "optimization"]
    assert result["checkpoint"]["skipped"] == ["debug"]


def test_four_workstream_pipeline_reuses_source_bound_optimization_state(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    kwargs = dict(
        top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"],
        tool="python", run_root=tmp_path / "run", source_revision="v1",
        optimization_proposals=[{"candidate": {"utilization": 0.5}, "predicted_metrics": {"wns": 0.1, "area": 10, "power": 2}}],
    )
    first = run_four_workstream_pipeline(spec, [rtl], **kwargs)
    second = run_four_workstream_pipeline(spec, [rtl], **kwargs)
    assert first["optimization"]["run_count"] == 0
    assert second["optimization"]["run_count"] == 0
    assert second["optimization"]["state_sha256"] == first["optimization"]["state_sha256"]


def test_four_workstream_pipeline_blocks_stale_optimization_state(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    common = dict(
        top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"],
        tool="python", run_root=tmp_path / "run", source_revision="v1",
        optimization_proposals=[{"candidate": {"utilization": 0.5}, "predicted_metrics": {"wns": 0.1, "area": 10, "power": 2}}],
    )
    assert run_four_workstream_pipeline(spec, [rtl], **common)["optimization"]["status"] == "ready"
    common["source_revision"] = "v2"
    result = run_four_workstream_pipeline(spec, [rtl], **common)
    assert result["optimization"]["status"] == "blocked"
    assert "different source revision" in result["optimization"]["reason"]
    assert "optimization" in result["blocked_reasons"]


def test_four_workstream_pipeline_records_explicit_optimization_measurement(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1",
        optimization_proposals=[{"candidate": {"utilization": 0.5}, "predicted_metrics": {"wns": 0.1, "area": 10, "power": 2}}],
        optimization_measurement={"fidelity": "proxy", "metrics": {"wns": 0.05, "area": 11, "power": 2.1}, "status": "passed", "runtime_seconds": 1.2, "tool": "openlane-proxy", "source_digest": hashlib.sha256(json.dumps([{"path": str(rtl.resolve()), "sha256": hashlib.sha256(rtl.read_bytes()).hexdigest()}], sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "configuration_digest": hashlib.sha256(json.dumps({"utilization": 0.5}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()},
    )
    assert result["status"] == "passed"
    assert result["optimization"]["status"] == "passed"
    assert result["optimization"]["run_count"] == 1
    assert result["optimization"]["measurement"]["configuration_digest"] == hashlib.sha256(json.dumps({"utilization": 0.5}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_four_workstream_pipeline_rejects_agent_without_debug_context(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    try:
        run_four_workstream_pipeline(spec, [rtl], top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"], tool="python", run_root=tmp_path / "run", source_revision="v1", agent_backend="local")
    except ValueError as error:
        assert "requires debug inputs" in str(error)
    else:
        raise AssertionError("agent execution without debug context was accepted")


def test_four_workstream_pipeline_runs_validated_local_agent(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    rtl.write_text("module dut(input wire clk, input wire enable, output reg q); always @(posedge clk) q <= enable; endmodule\n", encoding="utf-8")
    waveform = tmp_path / "trace.vcd"
    waveform.write_text("$var wire 1 ! enable $end\n$var wire 1 \" q $end\n$enddefinitions $end\n#0\n0!\n0\"\n#5\n1!\n1\"\n", encoding="utf-8")
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    import verification_platform.orchestration as orchestration_module
    requests = []
    original_invoke = orchestration_module.invoke_local_backend
    def capture_request(request):
        requests.append(request)
        return original_invoke(request)
    monkeypatch.setattr(orchestration_module, "invoke_local_backend", capture_request)
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1", debug_waveform=waveform, debug_rtl=rtl, debug_signal="q",
        debug_observed=[(0, "0"), (5, "1")], debug_reference=[(0, "0"), (5, "0")],
        debug_for_evidence=["q changes"], debug_against_evidence=["assignment is valid"], agent_backend="local",
    )
    assert result["status"] == "passed"
    assert result["agent"]["status"] == "available"
    assert result["agent"]["grounded"] is True
    assert requests and requests[0]["root_cause_candidates"]["status"] == "available"
    assert requests[0]["root_cause_candidates"]["candidates"][0]["line"] == 1


def test_four_workstream_pipeline_runs_review_only_repair_agent(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    waveform = tmp_path / "trace.vcd"
    waveform.write_text("$var wire 1 ! q $end\n$enddefinitions $end\n#0\n0!\n#5\n1!\n", encoding="utf-8")
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="repair-v1",
        debug_waveform=waveform, debug_rtl=rtl, debug_signal="q",
        debug_observed=[(0, "0"), (5, "1")], debug_reference=[(0, "0"), (5, "0")],
        debug_for_evidence=["q changes"], debug_against_evidence=["assignment is valid"],
        repair_agent_backend="local",
    )
    assert result["status"] == "passed"
    assert result["repair_agent"]["status"] == "available"
    assert result["repair_agent"]["grounded"] is True
    assert result["repair_agent"]["proposal"]["status"] == "review_required"


def test_four_workstream_pipeline_runs_approved_repair_retest_on_copy(tmp_path: Path):
    platform_root = Path(__file__).resolve().parents[1]
    spec = platform_root / "benchmarks" / "seeded_counter" / "spec.md"
    rtl = platform_root / "benchmarks" / "seeded_counter" / "counter.sv"
    protocol = platform_root / "benchmarks" / "protocol_execution" / "protocol_plan.json"
    debug_input = json.loads((platform_root / "benchmarks" / "seeded_counter" / "four-workstream-debug-input.json").read_text(encoding="utf-8"))
    destination = tmp_path / "run" / "debug" / "approved-repair" / "counter.sv"
    source = str(rtl.resolve())
    result = run_four_workstream_pipeline(
        spec, [rtl], top="counter", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="approved-repair-v1",
        debug_waveform=platform_root / "benchmarks" / "seeded_counter" / "runs" / "latest" / "waveform.vcd",
        debug_rtl=rtl, debug_signal="counter_q",
        debug_observed=[tuple(item) for item in debug_input["observed"]],
        debug_reference=[tuple(item) for item in debug_input["reference"]],
        debug_for_evidence=debug_input["for_evidence"], debug_against_evidence=debug_input["against_evidence"],
        approved_repair={
            "source": source, "destination": str(destination),
            "command": [sys.executable, str(platform_root / "scripts" / "run_counter_retest.py"), source],
            "human_approved": True,
            "proposal": {
                "requirement_id": "REQ-COUNTER-HOLD", "file": source, "line": 6,
                "before": "counter_q <= counter_q + 4'd1;",
                "after": "if (enable) counter_q <= counter_q + 4'd1;",
                "rationale": "guard the increment with the specification enable condition",
            },
        },
    )
    assert result["status"] == "passed"
    assert result["repair_retest"]["status"] == "passed"
    assert result["repair_retest"]["original_source_unchanged"] is True
    assert "PASS" in (tmp_path / "run" / "debug" / "approved-repair-retest" / "stdout.log").read_text(encoding="utf-8")
    checkpoint = json.loads((tmp_path / "run" / "workflow-checkpoint.json").read_text(encoding="utf-8"))
    assert "debug" in checkpoint["completed"]
    assert "debug/approved-repair-retest/repair-retest.json" in checkpoint["artifacts"]


def test_four_workstream_pipeline_runs_validated_assertion_agent(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol, command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1", assertion_agent_backend="local",
    )
    assert result["status"] == "passed"
    assert result["assertion_agent"]["status"] == "available"
    assert result["assertion_agent"]["proposal"]["status"] == "review_required"
    assert (tmp_path / "run/auto-formalization/agent-assertion-result.json").is_file()


def test_downstream_assertion_agent_records_team_provenance(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="team-bind-v1",
        agent_team_backend="local", agent_team_requests=[
            {"role": "assertion_generator", "task": "generate_assertion", "allowed_source_revision": "team-bind-v1", "evidence": ["team/input.json"], "requirement_id": "REQ-TEAM", "assertion": "assert property (@(posedge clk) req |-> ack);"},
        ], assertion_agent_backend="local",
    )
    assert result["status"] == "passed"
    assert result["agent_team"]["status"] == "available"
    assert result["assertion_agent"]["agent_team_sha256"] == result["agent_team"]["team_sha256"]
    assert result["assertion_agent"]["team_handoff_count"] == 1


def test_four_workstream_pipeline_records_solver_vacuity_for_admitted_assertion(monkeypatch, tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="solver-v1",
        assertion_agent_backend="local", assertion_solver_antecedent="rst",
    )
    assert result["status"] == "passed"
    assert result["assertion_solver_vacuity"]["status"] == "active"
    assert result["assertion_solver_vacuity"]["results"][0]["solver_status"] == "reachable"
    assert (tmp_path / "run/auto-formalization/solver-vacuity-result.json").is_file()


def test_four_workstream_pipeline_records_opt_in_formal_assertion_result(tmp_path: Path):
    root = Path(__file__).parents[1]
    spec = root / "benchmarks/seeded_counter/spec.md"
    rtl = root / "benchmarks/seeded_counter/counter.sv"
    protocol = root / "benchmarks/register_peripheral/protocol_sequence.json"
    formal = root / "benchmarks/seeded_counter/formal_model_check.sv"
    result = run_four_workstream_pipeline(
        spec, [rtl], top="counter", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="formal-v1",
        assertion_formal_sources=[formal], assertion_formal_top="formal_model_check",
        assertion_formal_sequence=6,
    )
    assert result["status"] == "passed"
    assert result["assertion_formal"]["status"] == "counterexample"
    assert result["claim_status"] == "review_required"
    assert result["checkpoint"]["completed"][0] == "planning"
    assert (tmp_path / "run/auto-formalization/proof/assertion-proof-result.json").is_file()


def test_four_workstream_assertion_agent_covers_all_planned_requirements(monkeypatch, tmp_path: Path):
    spec = tmp_path / "multi-spec.md"
    spec.write_text(
        "REQ-RESET: q is zero while rst is asserted\n"
        "REQ-HOLD: q holds its previous value when enable is low\n",
        encoding="utf-8",
    )
    rtl = tmp_path / "multi.sv"
    rtl.write_text(
        "module dut(input logic clk, input logic rst, input logic enable, output logic q); "
        "always_ff @(posedge clk) if (rst) q <= 1'b0; else if (enable) q <= 1'b1; "
        "endmodule\n",
        encoding="utf-8",
    )
    protocol = tmp_path / "protocol.json"
    protocol.write_text(
        '{"schema_version":"protocol-plan-v1","name":"design","addr_width":8,"data_width":32,'
        '"steps":[{"operation":"read","address":0,"expected":0}]}\n',
        encoding="utf-8",
    )
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="v1", assertion_agent_backend="local",
    )
    assert result["status"] == "passed"
    assert result["assertion_agent"]["status"] == "available"
    assert [item["requirement_id"] for item in result["assertion_agent"]["proposals"]] == ["REQ-RESET", "REQ-HOLD"]
    assert result["assertion_validation"]["requirements"] == ["REQ-RESET", "REQ-HOLD"]


def test_four_workstream_pipeline_can_run_compiled_verilator_stage(tmp_path: Path):
    root = Path(__file__).parents[1]
    result = run_four_workstream_pipeline(
        root / "benchmarks/seeded_counter/spec.md",
        [root / "benchmarks/seeded_counter/counter_reference.sv"],
        top="counter", protocol_plan=root / "benchmarks/register_peripheral/protocol_sequence.json",
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="compiled-v1",
        compiled_sim_harness=root / "benchmarks/seeded_counter/verilator_smoke.cpp",
    )
    assert result["status"] == "passed"
    assert result["compiled_simulation"]["status"] == "passed"
    assert result["checkpoint"]["completed"] == ["planning", "scheduling", "structural", "protocol"]


def test_four_workstream_pipeline_can_require_runtime_scheduling_evidence(tmp_path: Path):
    spec, rtl, protocol = _inputs(tmp_path)
    fixture = tmp_path / "timezero.sv"
    fixture.write_text(
        'module timezero; initial begin $display("TIMEZERO_REGRESSION_PASS"); end endmodule\n',
        encoding="utf-8",
    )
    result = run_four_workstream_pipeline(
        spec, [rtl], top="dut", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "run", source_revision="runtime-v1",
        scheduling_regression_source=fixture,
    )
    assert result["status"] == "passed"
    assert result["scheduling_runtime"]["outcome"] == "normal_completion"
    assert (tmp_path / "run/scheduling/runtime-regression.json").is_file()
