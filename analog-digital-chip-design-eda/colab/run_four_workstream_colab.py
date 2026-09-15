"""Run the four-workstream verification demo from a Google Colab cell."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any
import sys

# Make the checked-in script namespace available both when this file is
# imported from a Colab cell and when it is invoked directly as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_time_zero_regression_matrix import run_matrix
from scripts.run_four_workstream_repair_matrix import run_matrix as run_repair_matrix, verify_matrix_report
from scripts.run_four_workstream_assertion_matrix import run_matrix as run_assertion_matrix, verify_matrix_report as verify_assertion_matrix_report


def run_demo(repo_root: str | Path | None = None, run_root: str | Path | None = None) -> dict[str, Any]:
    """Run the seeded four-workstream example and return its JSON result.

    The default backend is the repository's provider-free JSONL fixture. Set
    ``VERIFICATION_LLM_COMMAND`` before calling this function to use a local
    model worker instead. The function never modifies canonical RTL.
    """
    root = Path(repo_root or REPO_ROOT).resolve()
    output = Path(run_root) if run_root else Path(tempfile.mkdtemp(prefix="four-workstream-colab-"))
    output.mkdir(parents=True, exist_ok=True)
    protocol_fixture = root / "benchmarks" / "protocol_execution"
    protocol_command_path = output / "protocol-execution-command.json"
    protocol_command_path.write_text(json.dumps([
        "python3", str(root / "scripts" / "run_protocol_sequence_fixture.py"),
        str((output / "protocol" / "csr_sequence.sv").resolve()),
        str((protocol_fixture / "csr_dut.sv").resolve()),
        str((protocol_fixture / "tb.sv").resolve()),
    ]) + "\n", encoding="utf-8")
    scheduling_matrix = run_matrix(output / "scheduling-matrix", timeout_seconds=1.0)
    if scheduling_matrix["status"] != "passed":
        raise RuntimeError("time-zero scheduling matrix did not meet its expected classifications")
    repair_matrix = run_repair_matrix(output / "repair-matrix")
    if repair_matrix["status"] != "passed":
        raise RuntimeError("multi-design repair matrix did not meet its expected classifications")
    repair_matrix_integrity = verify_matrix_report(output / "repair-matrix" / "matrix-result.json")
    if not repair_matrix_integrity["valid"]:
        raise RuntimeError(f"multi-design repair matrix integrity failed: {repair_matrix_integrity['errors']}")
    assertion_matrix = run_assertion_matrix(output / "assertion-matrix")
    if assertion_matrix["status"] != "passed":
        raise RuntimeError("multi-design assertion matrix did not meet its expected classifications")
    assertion_matrix_integrity = verify_assertion_matrix_report(output / "assertion-matrix" / "matrix-result.json")
    if not assertion_matrix_integrity["valid"]:
        raise RuntimeError(f"multi-design assertion matrix integrity failed: {assertion_matrix_integrity['errors']}")
    counter_source = (root / "benchmarks" / "seeded_counter" / "counter.sv").resolve()
    approved_repair_path = output / "approved-repair.json"
    approved_repair_path.write_text(json.dumps({
        "source": str(counter_source),
        "destination": str((output / "debug" / "approved-repair" / "counter.sv").resolve()),
        "command": ["python3", str((root / "scripts" / "run_counter_retest.py").resolve()), str(counter_source)],
        "proposal_from_agent": True,
        "human_approved": True,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = [
        "python3", "scripts/run_four_workstream_pipeline.py",
        "--spec", "benchmarks/seeded_counter/spec.md",
        "--rtl", "benchmarks/seeded_counter/counter.sv",
        "--top", "counter",
        "--protocol-plan", "benchmarks/protocol_execution/protocol_plan.json",
        "--protocol-execution-command", str(protocol_command_path),
        "--protocol-require-generated-sequence",
        "--compiled-sim-harness", "benchmarks/seeded_counter/verilator_smoke.cpp",
        "--compiled-sim-rtl", "benchmarks/seeded_counter/counter_reference.sv",
        "--svm-checker-source", "benchmarks/svm_counter/counter_svm.sv",
        "--svm-harness", "benchmarks/svm_counter/harness.sv",
        "--svm-rtl", "benchmarks/seeded_counter/counter_reference.sv",
        "--svm-harness-top", "svm_harness",
        "--protocol-coverage-report", "benchmarks/seeded_counter/four-workstream-coverage-report.json",
        "--run-root", str(output),
        "--source-revision", "colab-demo-v1",
        "--collateral-root", ".",
        "--collateral-entry", "specification", "benchmarks/seeded_counter/spec.md",
        "--collateral-entry", "rtl", "benchmarks/seeded_counter/counter.sv",
        "--collateral-entry", "protocol_plan", "benchmarks/protocol_execution/protocol_plan.json",
        "--collateral-entry", "register_spec", "benchmarks/register_peripheral/structured_register_spec.json",
        "--scheduling-regression-source", "benchmarks/time_zero_regressions/normal_completion.sv",
        "--debug-input", "benchmarks/seeded_counter/four-workstream-debug-input.json",
        "--approved-repair", str(approved_repair_path),
        "--optimization-proposals", "benchmarks/seeded_counter/four-workstream-optimization-proposals.json",
        "--optimization-mode", "explore",
        "--agent-backend", "local",
        "--repair-agent-backend", "local",
        "--assertion-agent-backend", "local",
        "--agent-team-input", "benchmarks/seeded_counter/four-workstream-agent-team.json",
        "--agent-team-backend", "local",
        "--assertion-formal-source", "benchmarks/seeded_counter/formal_model_check.sv",
        "--assertion-formal-top", "formal_model_check",
        "--assertion-formal-sequence", "6",
        "--",
        "iverilog", "-g2012", "-t", "null", str((root / "benchmarks/seeded_counter/counter.sv").resolve()),
    ]
    environment = os.environ.copy()
    if not environment.get("VERIFICATION_LLM_COMMAND") and not environment.get("VERIFICATION_LLM_BATCH_COMMAND"):
        environment["VERIFICATION_LLM_COMMAND"] = f"python3 {root / 'scripts/mock_llm_backend.py'}"
    completed = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, check=False)
    if completed.returncode:
        # Preserve the complete orchestrator result when the pipeline reports
        # a contract rejection.  The subprocess intentionally emits JSON even
        # on a blocked result; retaining it makes model-admission failures
        # diagnosable from a downloaded Colab artifact rather than only from a
        # truncated exception string.
        try:
            failed_result = json.loads(completed.stdout)
        except (TypeError, ValueError):
            failed_result = None
        if isinstance(failed_result, dict):
            failure_path = output / "pipeline-result.json"
            failure_path.write_text(json.dumps(failed_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        else:
            failure_path = None
        detail = completed.stderr.strip() or completed.stdout.strip() or f"pipeline exited {completed.returncode}"
        if failure_path is not None:
            detail = f"{detail}; complete result: {failure_path}"
        raise RuntimeError(detail)
    result = json.loads(completed.stdout)
    patch_candidate = result.get("repair_agent", {}).get("patch_candidate", {})
    if patch_candidate.get("status") != "review_required":
        raise RuntimeError("agent repair output did not produce a validated review-only patch candidate")
    result["scheduling_matrix"] = {
        "status": scheduling_matrix["status"],
        "path": str((output / "scheduling-matrix" / "matrix-result.json").resolve()),
        "case_count": len(scheduling_matrix["cases"]),
        "claim_boundary": scheduling_matrix["claim_boundary"],
    }
    result["repair_matrix"] = {
        "status": repair_matrix["status"],
        "path": str((output / "repair-matrix" / "matrix-result.json").resolve()),
        "case_count": repair_matrix["case_count"],
        "claim_boundary": repair_matrix["claim_boundary"],
        "integrity": repair_matrix_integrity,
    }
    result["assertion_matrix"] = {
        "status": assertion_matrix["status"],
        "path": str((output / "assertion-matrix" / "matrix-result.json").resolve()),
        "case_count": assertion_matrix["case_count"],
        "claim_boundary": assertion_matrix["claim_boundary"],
        "integrity": assertion_matrix_integrity,
    }
    result["colab_run_root"] = str(output.resolve())
    return result


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2, sort_keys=True))
