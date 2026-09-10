"""Open-source project-collateral execution adapters for the pilot service."""
from __future__ import annotations

import json
from dataclasses import asdict
import hashlib
from pathlib import Path
import re
from typing import Any

from verification_platform.runner import run_command
from verification_platform.simulation import run_iverilog_vvp
from verification_platform.triage import failure_to_ir, parse_failure
from verification_platform.logic import dependency_cone
from verification_platform.closure import evaluate_closure, write_closure

MODULE_RE = re.compile(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)")
COVERAGE_RE = re.compile(r"COVERAGE\s+kind=(?P<kind>[A-Za-z_][\w-]*)\s+covered=(?P<covered>\d+)\s+total=(?P<total>\d+)")


def compile_project_rtl(
    record: dict[str, Any],
    *,
    collateral_root: str | Path,
    run_root: str | Path,
    source_revision: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Compile uploaded RTL with Icarus and persist the normal provenance ledger."""
    source = Path(collateral_root) / str(record["path"])
    if not source.is_file():
        raise FileNotFoundError(source)
    content = source.read_text(encoding="utf-8")
    modules = sorted(set(MODULE_RE.findall(content)))
    if not modules:
        raise ValueError("collateral contains no SystemVerilog module")
    top = modules[0]
    output = Path(run_root) / "compiled.out"
    tool_run = run_command(
        ["iverilog", "-g2012", "-s", top, "-o", str(output), str(source)],
        tool="iverilog-project-compile",
        run_root=run_root,
        source_revision=source_revision or str(record["version"]),
        timeout_seconds=timeout_seconds,
        expected_artifacts=["compiled.out"],
    )
    result = {
        "project_id": record["project_id"],
        "artifact_id": record["id"],
        "top_module": top,
        "modules": modules,
        "status": tool_run.status,
        "exit_code": tool_run.exit_code,
        "tool_run": asdict(tool_run),
    }
    result_path = Path(run_root) / "project-compile-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["result_path"] = str(result_path)
    return result


def lint_project_rtl(
    record: dict[str, Any],
    *,
    collateral_root: str | Path,
    run_root: str | Path,
    source_revision: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Run Verilator's static front end without claiming simulation coverage."""
    source = Path(collateral_root) / str(record["path"])
    if not source.is_file():
        raise FileNotFoundError(source)
    modules = sorted(set(MODULE_RE.findall(source.read_text(encoding="utf-8"))))
    if not modules:
        raise ValueError("collateral contains no SystemVerilog module")
    tool_run = run_command(
        ["verilator", "--lint-only", "--language", "1800-2012", "--top-module", modules[0], str(source)],
        tool="verilator-project-lint",
        run_root=run_root,
        source_revision=source_revision or str(record["version"]),
        timeout_seconds=timeout_seconds,
    )
    result = {"project_id": record["project_id"], "artifact_id": record["id"], "top_module": modules[0], "status": tool_run.status, "exit_code": tool_run.exit_code, "tool_run": asdict(tool_run)}
    result_path = Path(run_root) / "project-lint-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["result_path"] = str(result_path)
    return result


def simulate_project(
    rtl_record: dict[str, Any],
    testbench_record: dict[str, Any],
    *,
    collateral_root: str | Path,
    run_root: str | Path,
    source_revision: str = "unknown",
    timeout_seconds: float = 180.0,
) -> dict[str, Any]:
    """Run a customer RTL/testbench pair and preserve failure evidence."""
    rtl = Path(collateral_root) / str(rtl_record["path"])
    testbench = Path(collateral_root) / str(testbench_record["path"])
    if not rtl.is_file() or not testbench.is_file():
        raise FileNotFoundError("RTL or testbench collateral is missing")
    run_root = Path(run_root)
    compile_run, simulation_run = run_iverilog_vvp(
        rtl,
        testbench,
        run_root=run_root,
        source_revision=source_revision,
        binary_name="simulation.out",
        tool_prefix="project",
    )
    result: dict[str, Any] = {
        "project_id": rtl_record["project_id"],
        "rtl_artifact_id": rtl_record["id"],
        "testbench_artifact_id": testbench_record["id"],
        "status": simulation_run.status if simulation_run else compile_run.status,
        "compile_run": asdict(compile_run),
        "simulation_run": asdict(simulation_run) if simulation_run else None,
    }
    if simulation_run:
        stdout_path = run_root / "simulation" / "stdout.log"
        stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
        failure = parse_failure(stdout)
        coverage_match = COVERAGE_RE.search(stdout)
        if coverage_match:
            covered, total = int(coverage_match["covered"]), int(coverage_match["total"])
            if total <= 0 or covered > total:
                raise ValueError("coverage marker requires 0 <= covered <= total and total > 0")
            coverage_path = run_root / "functional-coverage.json"
            coverage_path.write_text(json.dumps({"kind": coverage_match["kind"], "covered": covered, "total": total}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result["coverage_path"] = str(coverage_path)
        if failure:
            result["status"] = "failed"
            result["failure"] = asdict(failure)
            triage = failure_to_ir(
                failure,
                root=run_root,
                source_revision=source_revision,
                artifact_paths=["simulation/stdout.log", "simulation/stderr.log", "waveform.vcd"],
            )
            triage_path = run_root / "verification-ir.json"
            triage.write(triage_path)
            result["triage_path"] = str(triage_path)
            result["triage_sha256"] = hashlib.sha256(triage_path.read_bytes()).hexdigest()
            closure_path = run_root / "closure-report.json"
            write_closure(evaluate_closure(triage), closure_path)
            result["closure_path"] = str(closure_path)
            result["diagnosis"] = {
                "status": "review_required",
                "signal": failure.signal,
                "dependency_cone": sorted(dependency_cone(rtl, failure.signal)),
                "hypothesis": f"inspect the RTL driver cone for {failure.signal} at the first failing cycle",
            }
            diagnosis_path = run_root / "diagnosis.json"
            diagnosis_path.write_text(json.dumps(result["diagnosis"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result["diagnosis_path"] = str(diagnosis_path)
    result_path = run_root / "project-simulation-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["result_path"] = str(result_path)
    return result
