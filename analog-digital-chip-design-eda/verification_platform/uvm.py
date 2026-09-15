"""Deterministic UVM scaffold generation; execution requires a UVM-capable simulator."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import shutil
from typing import Any

from .runner import run_command


def generate_uvm_agent(agent_name: str, signals: list[str]) -> str:
    if not agent_name.isidentifier() or not signals or any(not signal.isidentifier() for signal in signals):
        raise ValueError("agent name and at least one valid signal are required")
    prefix = agent_name.lower()
    signal_declarations = "\n".join(f"  logic {signal};" for signal in signals)
    transaction_fields = "\n".join(f"  rand logic {signal};" for signal in signals)
    return f"""// Generated UVM scaffold; review and compile against the target UVM library.
`include \"uvm_macros.svh\"
import uvm_pkg::*;

interface {prefix}_if(input logic clk);
{signal_declarations}
endinterface

class {prefix}_transaction extends uvm_sequence_item;
  `uvm_object_utils({prefix}_transaction)
{transaction_fields}
  function new(string name=\"{prefix}_transaction\"); super.new(name); endfunction
endclass

class {prefix}_agent extends uvm_agent;
  `uvm_component_utils({prefix}_agent)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

// Dependency order: interface -> transaction -> driver/monitor -> agent -> scoreboard -> env.
class {prefix}_driver extends uvm_driver #({prefix}_transaction);
  `uvm_component_utils({prefix}_driver)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class {prefix}_monitor extends uvm_monitor;
  `uvm_component_utils({prefix}_monitor)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class {prefix}_scoreboard extends uvm_scoreboard;
  `uvm_component_utils({prefix}_scoreboard)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class {prefix}_env extends uvm_env;
  `uvm_component_utils({prefix}_env)
  {prefix}_agent agent;
  {prefix}_scoreboard scoreboard;
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass
"""


def write_uvm_agent(agent_name: str, signals: list[str], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_uvm_agent(agent_name, signals), encoding="utf-8")
    return output


def probe_uvm_runtime(
    *,
    simulator: str = "verilator",
    uvm_root: str | Path | None = None,
    run_root: str | Path | None = None,
) -> dict[str, Any]:
    """Record whether a UVM package and simulator are available.

    This is a capability probe only.  It does not claim that a particular
    scaffold compiles or that the simulator implements the complete UVM LRM.
    An explicit package path is required so the result is reproducible.
    """
    if not simulator or not isinstance(simulator, str):
        raise ValueError("simulator must be a non-empty executable name")
    executable = shutil.which(simulator)
    package_path = None
    if uvm_root is not None:
        candidate = Path(uvm_root)
        package_path = candidate if candidate.name == "uvm_pkg.sv" else candidate / "src" / "uvm_pkg.sv"
        if not package_path.is_file():
            package_path = candidate / "uvm_pkg.sv"
    result: dict[str, Any] = {
        "schema_version": "uvm-runtime-capability-v1",
        "simulator": simulator,
        "simulator_path": executable,
        "uvm_root": str(Path(uvm_root).resolve()) if uvm_root is not None else None,
        "uvm_package": str(package_path.resolve()) if package_path is not None and package_path.is_file() else None,
        "status": "available" if executable and package_path is not None and package_path.is_file() else "blocked",
        "claim_boundary": "UVM package/simulator presence probe only; does not prove UVM compilation, scheduling, or runtime compatibility",
    }
    if result["status"] == "blocked":
        missing = []
        if not executable:
            missing.append(f"simulator executable: {simulator}")
        if package_path is None or not package_path.is_file():
            missing.append("uvm_pkg.sv")
        result["blocked_reason"] = "missing " + " and ".join(missing)
    result["capability_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if run_root is not None:
        output = Path(run_root) / "uvm-runtime-capability.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["path"] = str(output)
    return result


def run_uvm_compile(
    source: str | Path,
    *,
    uvm_root: str | Path,
    compile_command: list[str],
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
    expected_artifacts: list[str] | None = None,
    runtime_command: list[str] | None = None,
    runtime_expected_markers: list[str] | None = None,
) -> dict[str, Any]:
    """Run an explicit UVM compile command after capability validation.

    The command is caller-owned because simulator option syntax differs across
    Verilator, commercial simulators, and vendor wrappers.  The adapter never
    invokes a shell and never treats compilation as runtime UVM evidence.
    """
    source_path = Path(source).resolve()
    if not source_revision or not source_path.is_file() or not compile_command or any(not isinstance(item, str) or not item for item in compile_command):
        raise ValueError("source, source_revision, and a non-empty compile command are required")
    capability = probe_uvm_runtime(simulator=compile_command[0], uvm_root=uvm_root)
    if runtime_command is not None and (not runtime_command or any(not isinstance(item, str) or not item for item in runtime_command)):
        raise ValueError("runtime_command must be a non-empty list of non-empty strings")
    markers = list(runtime_expected_markers or [])
    if any(not isinstance(item, str) or not item for item in markers):
        raise ValueError("runtime_expected_markers must contain non-empty strings")
    result: dict[str, Any] = {
        "schema_version": "uvm-compile-result-v1",
        "source_revision": source_revision,
        "source": {"path": str(source_path), "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest()},
        "uvm_capability": capability,
        "compile": None,
        "runtime": None,
        "runtime_markers": markers,
        "status": "blocked",
        "claim_boundary": "UVM compile-command evidence only; optional runtime evidence requires explicit pass markers and does not claim complete UVM compatibility",
    }
    if capability["status"] != "available":
        result["blocked_reason"] = "UVM capability validation failed: " + str(capability.get("blocked_reason", "unknown reason"))
    else:
        tool_run = run_command(
            compile_command, tool="uvm-compile", run_root=run_root, source_revision=source_revision,
            timeout_seconds=timeout_seconds, expected_artifacts=list(expected_artifacts or []), run_id="uvm-compile",
        )
        result["compile"] = asdict(tool_run)
        result["status"] = "passed" if tool_run.status == "passed" else "blocked"
        if result["status"] != "passed":
            result["blocked_reason"] = "UVM compile command did not pass"
        elif runtime_command is not None:
            runtime_root = Path(run_root) / "runtime"
            runtime_run = run_command(
                runtime_command, tool="uvm-runtime", run_root=runtime_root,
                source_revision=source_revision, timeout_seconds=timeout_seconds,
                run_id="uvm-runtime",
            )
            result["runtime"] = asdict(runtime_run)
            runtime_output = (runtime_root / "stdout.log").read_text(encoding="utf-8") if (runtime_root / "stdout.log").is_file() else ""
            missing_markers = [marker for marker in markers if marker not in runtime_output]
            result["runtime_observed_markers"] = [marker for marker in markers if marker in runtime_output]
            if runtime_run.status != "passed" or missing_markers:
                result["status"] = "blocked"
                result["blocked_reason"] = "UVM runtime did not pass or omitted required markers"
                result["runtime_missing_markers"] = missing_markers
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = Path(run_root) / "uvm-compile-result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["path"] = str(output)
    return result
