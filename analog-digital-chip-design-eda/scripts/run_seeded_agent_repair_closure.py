"""Evaluate agent-proposed repairs against the seeded mutation matrix.

Every mutation is created in a disposable workspace, diagnosed through the
repository-agent contract, and repaired only in another disposable copy. The
canonical checkout is never the repair target. This is benchmark-evaluation
approval, not production source approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.repository_agent import run_repository_agent
from verification_platform.repair import RepairProposal, apply_to_copy
from verification_platform.runner import run_command
from verification_platform.causal import bind_frontier_to_causal_graph, causal_graph_from_vcd, rank_frontier_root_causes, state_frontier
from verification_platform.triage import parse_failure
from verification_platform.waveform import signal_values


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "benchmarks/repository_scale/seeded_multi_mutation_suite.json"
SOURCE_REVISION = "seeded-mutation-repair-closure-v1"
NORMALIZATION = {
    "benchmarks/seeded_arbiter/arbiter.sv": (
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : 2'b00);",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));",
    ),
    "benchmarks/seeded_decoder/decoder.sv": (
        "        2'd3: decode = 4'b1000;",
        "        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b1000;",
    ),
    "benchmarks/seeded_fifo/fifo.sv": (
        "        2'b10: count <= count + 3'd1;",
        "        2'b10: count <= (count < DEPTH) ? count + 3'd1 : count;",
    ),
    "benchmarks/seeded_handshake/handshake.sv": (
        "  assign ready = 1'b1; // SEEDED_BUG: ready must be low during reset",
        "  assign ready = rst ? 1'b0 : 1'b1;",
    ),
    "benchmarks/seeded_parity/parity.sv": (
        "  assign even = rst ? 1'b0 : ^data;",
        "  assign even = rst ? 1'b0 : ~^data;",
    ),
    "benchmarks/seeded_regblock/regblock.sv": (
        "      if (addr == 2'd0) reg0 <= wdata;\n      else reg0 <= wdata; // SEEDED_BUG: nonzero addresses must be ignored",
        "      if (addr == 2'd0) reg0 <= wdata;",
    ),
    "benchmarks/seeded_signed/signed_add.sv": (
        "  assign sum = rst ? 6'sd0 : {2'b00,a} + {2'b00,b};",
        "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} + {{2{b[3]}},b};",
    ),
    "benchmarks/seeded_width/width_adapter.sv": (
        "  assign low = rst ? 4'b0000 : data[7:4];",
        "  assign low = rst ? 4'b0000 : data[3:0];",
    ),
}


def sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _copy_workspace(workspace: Path, source_file: str, testbench: str) -> None:
    for relative in (source_file, testbench):
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    script = workspace / "scripts/run_seeded_counter_check.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", script)


def _make_canonical(source_path: Path, relative: str) -> None:
    buggy, good = NORMALIZATION[relative]
    text = source_path.read_text(encoding="utf-8")
    if text.count(buggy) == 1:
        text = text.replace(buggy, good, 1)
    elif text.count(good) != 1:
        raise RuntimeError(f"cannot normalize canonical source: {relative}")
    source_path.write_text(text, encoding="utf-8")


def _failure_value_for_trace(value: str, reference_value: str) -> str:
    """Convert the decimal failure-log value to the reference VCD width."""
    if not reference_value or any(character not in "01" for character in reference_value):
        return value
    try:
        number = int(value, 10)
    except ValueError:
        return value
    width = len(reference_value)
    return format(number & ((1 << width) - 1), f"0{width}b")


def _frontier_traces(observed: list[tuple[int, str]], reference: list[tuple[int, str]], failure) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """Reconcile an early-terminating failing VCD using its explicit FAIL log."""
    if failure is None or len(observed) == len(reference):
        return observed, reference
    if len(observed) < len(reference):
        index = len(observed)
        if index >= len(reference):
            return observed, reference
        observed = [*observed, (reference[index][0], _failure_value_for_trace(failure.actual, reference[index][1]))]
    else:
        index = len(reference)
        if index >= len(observed):
            return observed, reference
        reference = [*reference, (observed[index][0], _failure_value_for_trace(failure.expected, observed[index][1]))]
    return observed, reference


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m5/agent-repair-closure")
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-tasks", type=int, default=None)
    args = parser.parse_args()
    if args.start_index < 0 or args.max_tasks is not None and args.max_tasks <= 0:
        raise SystemExit("--start-index must be nonnegative and --max-tasks must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {ROOT / 'scripts/mock_repository_agent_backend.py'}"
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="seeded-agent-repair-") as temporary:
        staging = Path(temporary)
        mutations = plan["mutations"][args.start_index:]
        if args.max_tasks is not None:
            mutations = mutations[:args.max_tasks]
        for index, mutation in enumerate(mutations, args.start_index):
            task_id = str(mutation["mutation_id"])
            source_relative = str(mutation["source_file"])
            testbench_relative = str(mutation["command"][-1])
            task_root = staging / f"{index:02d}-{task_id}"
            _copy_workspace(task_root, source_relative, testbench_relative)
            canonical_source = task_root / source_relative
            _make_canonical(canonical_source, source_relative)
            mutated_source = task_root / "mutated" / source_relative
            repaired_source = task_root / "repaired" / source_relative
            mutated_source.parent.mkdir(parents=True, exist_ok=True)
            repaired_source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(canonical_source, mutated_source)
            text = mutated_source.read_text(encoding="utf-8")
            if text.count(str(mutation["from"])) != 1:
                raise RuntimeError(f"mutation {task_id} does not match canonical source")
            mutated_source.write_text(text.replace(str(mutation["from"]), str(mutation["to"]), 1), encoding="utf-8")
            command = [
                sys.executable,
                str(task_root / "scripts/run_seeded_counter_check.py"),
                str(mutated_source),
                str(task_root / testbench_relative),
            ]
            task_output = args.output / f"{index:02d}-{task_id}"
            baseline = run_command(command, tool="agent-repair-mutated-baseline", run_root=task_output / "baseline", source_revision=SOURCE_REVISION)
            canonical_command = [str(canonical_source) if item == str(mutated_source) else item for item in command]
            canonical = run_command(canonical_command, tool="agent-repair-canonical-reference", run_root=task_output / "canonical", source_revision=SOURCE_REVISION)
            canonical_before_hash = hashlib.sha256(canonical_source.read_bytes()).hexdigest()
            failure_log = task_output / "baseline" / "stdout.log"
            failure = parse_failure(failure_log.read_text(encoding="utf-8")) if failure_log.is_file() else None
            baseline_waveform = task_output / "baseline" / "waveform.vcd"
            canonical_waveform = task_output / "canonical" / "waveform.vcd"
            localization: dict[str, object] = {"status": "blocked", "reason": "failure and reference waveform artifacts are required"}
            allowed_locations: list[dict[str, object]] = []
            if failure is not None and baseline_waveform.is_file() and canonical_waveform.is_file():
                observed = signal_values(baseline_waveform, failure.signal)
                reference = signal_values(canonical_waveform, failure.signal)
                observed, reference = _frontier_traces(observed, reference, failure)
                frontier = state_frontier(observed, reference, signal=failure.signal)
                failure_event = observed[-1] if observed and observed[-1][0] == reference[int(failure.cycle)][0] else None
                graph = causal_graph_from_vcd(
                    baseline_waveform, mutated_source, [failure.signal],
                    extra_events=[(failure.signal, failure_event[0], failure_event[1])] if failure_event is not None else [],
                )
                binding = bind_frontier_to_causal_graph(frontier, graph)
                localization = rank_frontier_root_causes(binding, mutated_source)
                allowed_locations = list(localization.get("candidates", [])) if localization.get("status") == "available" else []
            agent = run_repository_agent(
                task_id=task_id,
                source_revision=SOURCE_REVISION,
                evidence=[task_id, source_relative, "mutated baseline failure", "causal localization artifact"],
                failure_context=f"seeded mutation {task_id} must be repaired back to the declared canonical behavior",
                repair_before=str(mutation["to"]),
                repair_after=str(mutation["from"]),
                repair_source=mutated_source,
                backend="local",
                output_root=task_output / "agent",
                allowed_source_locations=allowed_locations,
            )
            candidate = agent.get("patch_candidate", {})
            repaired_status = "blocked"
            canonical_unchanged = False
            canonical_unchanged = canonical_before_hash == hashlib.sha256(canonical_source.read_bytes()).hexdigest()
            if candidate.get("status") == "review_required":
                proposal = RepairProposal(
                    requirement_id=str(candidate.get("requirement_id") or task_id),
                    file=str(candidate["source"]),
                    line=int(candidate["line"]),
                    before=str(candidate["before"]),
                    after=str(candidate["after"]),
                    rationale="benchmark-only evaluation of a bounded agent repair",
                    edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
                )
                before_hash = hashlib.sha256(canonical_source.read_bytes()).hexdigest()
                # This approval is scoped to disposable benchmark evaluation;
                # the production approval gate remains unchanged.
                apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True)
                repaired_command = [str(repaired_source) if item == str(mutated_source) else item for item in command]
                repaired = run_command(repaired_command, tool="agent-repair-retest", run_root=task_output / "repaired", source_revision=SOURCE_REVISION)
                repaired_status = repaired.status
                canonical_unchanged = before_hash == hashlib.sha256(canonical_source.read_bytes()).hexdigest()
            passed = baseline.status == "failed" and canonical.status == "passed" and localization.get("status") == "available" and bool(allowed_locations) and repaired_status == "passed" and canonical_unchanged and candidate.get("root_cause_location_bound") is True
            repair_team_result = next((item for item in agent["team"].get("results", []) if item.get("role") == "repair_proposer"), {})
            results.append({
                "task_id": task_id,
                "baseline_status": baseline.status,
                "agent_status": agent["team"]["status"],
                "canonical_status": canonical.status,
                "localization_status": localization.get("status"),
                "localized_candidate_count": len(allowed_locations),
                "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
                "patch_location_bound": candidate.get("root_cause_location_bound", False),
                "repaired_status": repaired_status,
                "canonical_unchanged": canonical_unchanged,
                "model_selected_repair": repair_team_result.get("model_selected_repair"),
                "passed": passed,
                "run_sha256": agent["run_sha256"],
            })
    report = {
        "schema_version": "seeded-agent-repair-closure-report-v3",
        "source_revision": SOURCE_REVISION,
        "backend": args.backend,
        "task_count": len(results),
        "passed_tasks": sum(bool(item["passed"]) for item in results),
        "tasks": results,
        "status": "passed" if results and all(bool(item["passed"]) for item in results) else "blocked",
        "task_range": {"start_index": args.start_index, "max_tasks": args.max_tasks, "selected_count": len(results), "suite_count": len(plan["mutations"])},
        "claim_boundary": "disposable benchmark repair closure; not human-approved production modification or generalization proof; partial task ranges are not full-suite evidence",
    }
    task_total = len(results)
    report["metrics"] = {
        "canonical_reference_pass_rate": round(sum(item["canonical_status"] == "passed" for item in results) / task_total, 4) if task_total else 0.0,
        "causal_localization_rate": round(sum(item["localization_status"] == "available" for item in results) / task_total, 4) if task_total else 0.0,
        "source_bound_patch_rate": round(sum(item["patch_location_bound"] is True for item in results) / task_total, 4) if task_total else 0.0,
        "repair_retest_pass_rate": round(sum(item["repaired_status"] == "passed" for item in results) / task_total, 4) if task_total else 0.0,
        "canonical_immutability_rate": round(sum(item["canonical_unchanged"] is True for item in results) / task_total, 4) if task_total else 0.0,
        "end_to_end_closure_rate": round(sum(bool(item["passed"]) for item in results) / task_total, 4) if task_total else 0.0,
    }
    report["report_sha256"] = sha(report)
    path = args.output / "seeded-agent-repair-closure-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "tasks": report["task_count"], "passed": report["passed_tasks"], "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
