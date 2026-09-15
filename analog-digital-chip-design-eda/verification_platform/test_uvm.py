from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.uvm import generate_uvm_agent, probe_uvm_runtime, run_uvm_compile


def test_uvm_scaffold_contains_interface_and_traceable_components():
    source = generate_uvm_agent("CounterAgent", ["enable", "counter_q"])
    assert '`include "uvm_macros.svh"' in source
    assert "import uvm_pkg::*;" in source
    assert "interface counteragent_if" in source
    assert "counteragent_transaction" in source
    assert "counteragent_agent" in source
    assert "counteragent_driver" in source
    assert "counteragent_monitor" in source
    assert "counteragent_scoreboard" in source
    assert "counteragent_env" in source
    assert source.index("counteragent_driver") < source.index("counteragent_scoreboard") < source.index("counteragent_env")


def test_uvm_scaffold_rejects_empty_signal_list():
    try:
        generate_uvm_agent("CounterAgent", [])
    except ValueError as exc:
        assert "at least one" in str(exc)
    else:
        raise AssertionError("empty UVM interfaces must be rejected")


def test_uvm_runtime_probe_records_missing_package_fail_closed(tmp_path: Path):
    result = probe_uvm_runtime(simulator="definitely-missing-simulator", uvm_root=tmp_path / "missing", run_root=tmp_path / "run")
    assert result["status"] == "blocked"
    assert "uvm_pkg.sv" in result["blocked_reason"]
    assert Path(result["path"]).is_file()
    assert len(result["capability_sha256"]) == 64


def test_uvm_runtime_probe_reports_available_with_explicit_package_and_simulator(tmp_path: Path):
    package = tmp_path / "uvm_pkg.sv"
    package.write_text("package uvm_pkg; endpackage\n", encoding="utf-8")
    simulator = tmp_path / "simulator"
    simulator.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    simulator.chmod(0o755)
    result = probe_uvm_runtime(simulator=str(simulator), uvm_root=package)
    assert result["status"] == "available"
    assert result["uvm_package"].endswith("uvm_pkg.sv")


def test_uvm_compile_adapter_records_explicit_command_evidence(tmp_path: Path):
    package = tmp_path / "uvm_pkg.sv"
    package.write_text("package uvm_pkg; endpackage\n", encoding="utf-8")
    simulator = tmp_path / "simulator"
    simulator.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    simulator.chmod(0o755)
    source = tmp_path / "agent.sv"
    source.write_text("module agent; endmodule\n", encoding="utf-8")
    result = run_uvm_compile(
        source, uvm_root=package, compile_command=[str(simulator), str(source)],
        run_root=tmp_path / "run", source_revision="uvm-compile-v1",
    )
    assert result["status"] == "passed"
    assert result["compile"]["tool"] == "uvm-compile"
    assert Path(result["path"]).is_file()


def test_uvm_compile_adapter_can_require_bounded_runtime_markers(tmp_path: Path):
    package = tmp_path / "uvm_pkg.sv"
    package.write_text("package uvm_pkg; endpackage\n", encoding="utf-8")
    simulator = tmp_path / "simulator"
    simulator.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    simulator.chmod(0o755)
    runtime = tmp_path / "runtime"
    runtime.write_text("#!/bin/sh\nprintf 'UVM_RUNTIME_PASS\\n'\n", encoding="utf-8")
    runtime.chmod(0o755)
    source = tmp_path / "agent.sv"
    source.write_text("module agent; endmodule\n", encoding="utf-8")
    result = run_uvm_compile(
        source, uvm_root=package, compile_command=[str(simulator), str(source)],
        runtime_command=[str(runtime)], runtime_expected_markers=["UVM_RUNTIME_PASS"],
        run_root=tmp_path / "run", source_revision="uvm-runtime-v1",
    )
    assert result["status"] == "passed"
    assert result["runtime"]["tool"] == "uvm-runtime"
    assert result["runtime_observed_markers"] == ["UVM_RUNTIME_PASS"]
