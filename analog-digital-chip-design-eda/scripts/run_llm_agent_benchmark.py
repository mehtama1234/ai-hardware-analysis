#!/usr/bin/env python3
"""Run the provider-neutral LLM verification-agent benchmark slice."""
from __future__ import annotations

import hashlib
import json
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import statistics

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verification_platform.agent import validate_agent_proposal
from verification_platform.reference_agent import propose_failure_diagnosis
from verification_platform.triage import Failure
from verification_platform.llm_backend import invoke_local_backend, invoke_openai_compatible_backend, invoke_local_backend_batch
from verification_platform.adversarial import review_proposal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/llm-agent-benchmark.json")
    args = parser.parse_args()
    taxonomy = json.loads((ROOT / "benchmarks/multi_design_pilot/fault-taxonomy.json").read_text())
    proposals, rejections = [], []
    model_runs = {"local-command": [], "openai-compatible-local": []}
    batch_requests = []
    batch_items = []
    design_rows = [{"design_id": design_id, "fault_class": fault_class} for design_id, fault_class in taxonomy["designs"].items()]
    for index, item in enumerate(sorted(design_rows, key=lambda row: row["design_id"]), 1):
        design_id = item["design_id"]
        failure_data = taxonomy.get("failure_cases", {}).get(design_id)
        if not isinstance(failure_data, dict):
            raise SystemExit(f"{design_id} has no versioned failure case")
        signal = str(failure_data["signal"])
        cycle = int(failure_data["cycle"])
        failure = Failure(cycle=cycle, signal=signal, expected=str(failure_data["expected"]), actual=str(failure_data["actual"]))
        source_revision = str(failure_data["source_revision"])
        evidence_names = failure_data["evidence"]
        evidence = [f"pilot://{design_id}/{name}" for name in evidence_names]
        proposal = propose_failure_diagnosis(failure, source_revision=source_revision, evidence=evidence, dependency_cone=[signal])
        proposals.append({"design_id": design_id, "fault_class": item["fault_class"], "proposal": proposal.record(), "grounded": proposal.source_revision == source_revision and set(proposal.evidence) == set(evidence)})
        request = {
            "task": "diagnose_failure",
            "design_id": design_id,
            "fault_class": item["fault_class"],
            "failure": {"cycle": failure.cycle, "signal": failure.signal, "expected": failure.expected, "actual": failure.actual},
            "allowed_source_revision": source_revision,
            "evidence": evidence,
            "dependency_cone": [signal],
            "output_contract": "diagnosis proposal; status must be review_required; do not claim closure",
        }
        batch_requests.append(request)
        batch_items.append({"item": item, "request": request})
        for name, invoke in (("local-command", invoke_local_backend), ("openai-compatible-local", invoke_openai_compatible_backend)):
            started = time.perf_counter()
            response = invoke(request)
            row = {"design_id": item["design_id"], "status": response.status, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "error": response.error}
            if response.proposal is not None:
                record = response.proposal.record()
                row["proposal"] = record
                row["grounded"] = record["source_revision"] == source_revision and set(record["evidence"]).issubset(set(evidence))
                row["diagnosis_match"] = record["kind"] == "diagnosis" and signal in record["action"] and str(failure.cycle) in record["action"]
                row["adversarial_review"] = review_proposal(response.proposal, source_revision=source_revision, evidence=evidence, signal=signal, cycle=failure.cycle)
            model_runs[name].append(row)
    batch_started = time.perf_counter()
    batch_results = invoke_local_backend_batch(batch_requests)
    batch_latency_ms = round((time.perf_counter() - batch_started) * 1000, 2)
    batch_runs = []
    for batch_item, response in zip(batch_items, batch_results):
        item = batch_item["item"]
        request = batch_item["request"]
        failure = request["failure"]
        signal = failure["signal"]
        cycle = int(failure["cycle"])
        source_revision = request["allowed_source_revision"]
        evidence = request["evidence"]
        row = {"design_id": item["design_id"], "status": response.status, "batch_latency_ms": batch_latency_ms, "error": response.error}
        if response.proposal is not None:
            record = response.proposal.record()
            row["proposal"] = record
            row["grounded"] = record["source_revision"] == source_revision and set(record["evidence"]).issubset(set(evidence))
            row["diagnosis_match"] = record["kind"] == "diagnosis" and signal in record["action"] and str(cycle) in record["action"]
            row["adversarial_review"] = review_proposal(response.proposal, source_revision=source_revision, evidence=evidence, signal=signal, cycle=cycle)
        batch_runs.append(row)
    local_probe = invoke_local_backend({"proposal_id": "probe", "kind": "diagnosis", "source_revision": "pilot-release-reference", "action": "inspect fault signal", "rationale": "probe only", "evidence": ["pilot://probe/baseline"]})
    http_probe = invoke_openai_compatible_backend({"proposal_id": "probe", "kind": "diagnosis", "source_revision": "pilot-release-reference", "action": "inspect fault signal", "rationale": "probe only", "evidence": ["pilot://probe/baseline"]})
    unsafe_cases = [
        {"proposal_id": "unsafe-claim", "kind": "diagnosis", "source_revision": "pilot-release-reference", "action": "close failure", "rationale": "unsupported", "evidence": ["pilot://x"], "claims": ["passed"]},
        {"proposal_id": "missing-evidence", "kind": "repair", "source_revision": "pilot-release-reference", "action": "edit signal", "rationale": "unsupported", "evidence": []},
        {"proposal_id": "bad-kind", "kind": "closure", "source_revision": "pilot-release-reference", "action": "close", "rationale": "unsupported", "evidence": ["pilot://x"]},
    ]
    for case in unsafe_cases:
        try:
            validate_agent_proposal(case)
        except ValueError as error:
            rejections.append({"proposal_id": case["proposal_id"], "rejected": True, "reason": str(error)})
    execution = subprocess.run([sys.executable, str(ROOT / "scripts/run_closure_lab.py")], cwd=ROOT, capture_output=True, text=True, check=False)
    execution_record = {"status": "passed" if execution.returncode == 0 else "blocked", "exit_code": execution.returncode}
    decision_path = ROOT / ".artifacts/closure-lab-decision.json"
    if decision_path.is_file():
        decision = json.loads(decision_path.read_text())
        execution_record.update({"decision": decision.get("decision"), "decision_sha256": decision.get("decision_sha256"), "passed_retests": decision.get("metrics", {}).get("passed_retests"), "design_count": decision.get("metrics", {}).get("design_count")})
    aimc_mutation_run = None
    aimc_mutation_repair_run = None
    counter_repair_run = None
    timeout_repair_run = None
    register_repair_run = None
    if os.environ.get("VERIFICATION_AIMC_MUTATION", "0").strip() == "1":
        mutation_output = ROOT / ".artifacts/aimc-mutation-case"
        mutation = subprocess.run([sys.executable, str(ROOT / "scripts/run_aimc_mutation_case.py"), "--output", str(mutation_output)], cwd=ROOT, capture_output=True, text=True, check=False)
        mutation_case = json.loads((mutation_output / "mutation-case.json").read_text(encoding="utf-8"))
        failure = mutation_case["failure"]
        evidence = [f"pilot://aimc_multi_clock_control_subsystem/{name}" for name in failure["evidence"]]
        source_context = (mutation_output / "src/aimc_micro_tile_controller.v").read_text(encoding="utf-8").splitlines()[112:145]
        source_context = "\n".join(line.split("// AIMC_MUTATION", 1)[0].rstrip() for line in source_context)
        request = {"task": "diagnose_failure", "design_id": "aimc_multi_clock_control_subsystem", "fault_class": "aimc-readout-path", "failure": {key: failure[key] for key in ("cycle", "signal", "expected", "actual")}, "observed_signals": failure["observed_signals"], "allowed_source_revision": failure["source_revision"], "evidence": evidence, "dependency_cone": [failure["signal"], "readout_fallback", "readout_valid"], "source_context": source_context, "expected_behavior": "When readout_fallback=0 and readout_valid=1, the controller must take the else-if readout_valid branch and report EXEC_ANALOG_ACCEPTED (execution_path=1). Explain which branch condition is inconsistent with those observed values and why it causes the actual execution_path=0.", "output_contract": "diagnosis proposal; status must be review_required; do not claim closure; rationale must identify the exact RTL branch condition and its effect using the supplied source context"}
        aimc_started = time.perf_counter()
        aimc_response = invoke_local_backend_batch([request])[0]
        aimc_mutation_run = {"design_id": request["design_id"], "status": aimc_response.status, "latency_ms": round((time.perf_counter() - aimc_started) * 1000, 2), "error": aimc_response.error, "mutation_case": mutation_case}
        if aimc_response.proposal is not None:
            record = aimc_response.proposal.record()
            aimc_mutation_run["proposal"] = record
            aimc_mutation_run["grounded"] = record["source_revision"] == request["allowed_source_revision"] and set(record["evidence"]).issubset(set(request["evidence"]))
            aimc_mutation_run["diagnosis_match"] = record["kind"] == "diagnosis" and failure["signal"] in record["action"] and str(failure["cycle"]) in record["action"]
            rationale = record["rationale"].lower()
            aimc_mutation_run["root_cause_supported"] = "readout_fallback" in rationale and ("invert" in rationale or "branch" in rationale or "condition" in rationale)
            aimc_mutation_run["adversarial_review"] = review_proposal(aimc_response.proposal, source_revision=request["allowed_source_revision"], evidence=request["evidence"], signal=failure["signal"], cycle=failure["cycle"])
            if os.environ.get("VERIFICATION_AIMC_REPAIR", "0").strip() == "1":
                repair_source_context = "if (!readout_fallback) begin\nelse if (readout_valid) begin"
                repair_request = {"task": "propose_repair", "design_id": request["design_id"], "fault_class": request["fault_class"], "failure": request["failure"], "observed_signals": failure["observed_signals"], "allowed_source_revision": request["allowed_source_revision"], "evidence": request["evidence"], "dependency_cone": request["dependency_cone"], "source_context": repair_source_context, "expected_behavior": request["expected_behavior"], "repair_before": failure["mutation_after"], "repair_after": failure["mutation_before"], "repair_requirement": "The deliberate mutation inverted the first condition. Select the exact before and after strings supplied in the request. Do not change assignments, branch ordering, signal names, or any other text.", "output_contract": "repair proposal; status must be review_required; do not claim closure; before and after must be exact RTL condition lines from the supplied choices"}
                repair_response = invoke_local_backend_batch([repair_request])[0]
                aimc_mutation_repair_run = {"design_id": request["design_id"], "status": repair_response.status, "error": repair_response.error}
                raw = repair_response.raw or {}
                if raw:
                    aimc_mutation_repair_run["raw_output"] = raw
                if repair_response.proposal is not None:
                    repair_record = repair_response.proposal.record()
                    aimc_mutation_repair_run["proposal"] = repair_record
                    aimc_mutation_repair_run["before"] = raw.get("before")
                    aimc_mutation_repair_run["after"] = raw.get("after")
                    aimc_mutation_repair_run["grounded"] = repair_record["source_revision"] == request["allowed_source_revision"] and set(repair_record["evidence"]).issubset(set(request["evidence"]))
                    aimc_mutation_repair_run["repair_match"] = raw.get("before") == failure["mutation_after"] and raw.get("after") == failure["mutation_before"]
                    aimc_mutation_repair_run["adversarial_review"] = review_proposal(repair_response.proposal, source_revision=request["allowed_source_revision"], evidence=request["evidence"], signal=failure["signal"], cycle=failure["cycle"])
    if os.environ.get("VERIFICATION_COUNTER_REPAIR", "0").strip() == "1":
        counter_case = taxonomy["failure_cases"]["seeded_counter"]
        counter_evidence = [f"pilot://seeded_counter/{name}" for name in counter_case["evidence"]]
        counter_request = {
            "task": "propose_repair",
            "design_id": "seeded_counter",
            "fault_class": taxonomy["designs"]["seeded_counter"],
            "failure": {key: counter_case[key] for key in ("cycle", "signal", "expected", "actual")},
            "observed_signals": {"enable": "0", "counter_q": counter_case["actual"]},
            "allowed_source_revision": counter_case["source_revision"],
            "evidence": counter_evidence,
            "dependency_cone": ["enable", "counter_q"],
            "source_context": "else\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard",
            "expected_behavior": "When enable=0, counter_q must hold its value; when enable=1, it may increment.",
            "repair_before": "counter_q <= counter_q + 4'd1;",
            "repair_after": "if (enable) counter_q <= counter_q + 4'd1;",
            "repair_requirement": "Select the exact before and after strings supplied in the request. Add only the missing enable guard; do not change reset behavior, signal names, or arithmetic.",
            "output_contract": "repair proposal; status must be review_required; do not claim closure; before and after must be exact RTL lines from the supplied choices",
        }
        counter_response = invoke_local_backend_batch([counter_request])[0]
        counter_repair_run = {"design_id": "seeded_counter", "status": counter_response.status, "error": counter_response.error}
        raw = counter_response.raw or {}
        if raw:
            counter_repair_run["raw_output"] = raw
        if counter_response.proposal is not None:
            record = counter_response.proposal.record()
            counter_repair_run["proposal"] = record
            counter_repair_run["grounded"] = record["source_revision"] == counter_request["allowed_source_revision"] and set(record["evidence"]).issubset(set(counter_request["evidence"]))
            counter_repair_run["repair_match"] = raw.get("before") == counter_request["repair_before"] and raw.get("after") == counter_request["repair_after"]
            counter_repair_run["adversarial_review"] = review_proposal(counter_response.proposal, source_revision=counter_request["allowed_source_revision"], evidence=counter_request["evidence"], signal=counter_case["signal"], cycle=counter_case["cycle"])
    if os.environ.get("VERIFICATION_TIMEOUT_REPAIR", "0").strip() == "1":
        timeout_case = taxonomy["failure_cases"]["seeded_timeout"]
        timeout_evidence = [f"pilot://seeded_timeout/{name}" for name in timeout_case["evidence"]]
        timeout_request = {
            "task": "propose_repair",
            "design_id": "seeded_timeout",
            "fault_class": taxonomy["designs"]["seeded_timeout"],
            "failure": {key: timeout_case[key] for key in ("cycle", "signal", "expected", "actual")},
            "observed_signals": {"start": "0", "timed_out": timeout_case["actual"], "count": "3"},
            "allowed_source_revision": timeout_case["source_revision"],
            "evidence": timeout_evidence,
            "dependency_cone": ["count", "timed_out", "start"],
            "source_context": "  else if (count != 3'd0) count <= count + 3'd1;\n  assign timed_out = count >= 3'd4;",
            "expected_behavior": "The timeout output must assert at the second post-start edge; the observed count is 3 at the failing edge.",
            "repair_before": "  assign timed_out = count >= 3'd4;",
            "repair_after": "  assign timed_out = count >= 3'd3;",
            "repair_operator_choices": ["lower_timeout_threshold"],
            "repair_requirement": "Select the exact before and after strings supplied in the request. Correct only the timeout threshold; do not change the counter update, reset, or signal names.",
            "output_contract": "repair proposal; status must be review_required; do not claim closure; before and after must be exact RTL lines from the supplied choices",
        }
        timeout_response = invoke_local_backend_batch([timeout_request])[0]
        timeout_repair_run = {"design_id": "seeded_timeout", "status": timeout_response.status, "error": timeout_response.error}
        raw = timeout_response.raw or {}
        if raw:
            timeout_repair_run["raw_output"] = raw
        if timeout_response.proposal is not None:
            record = timeout_response.proposal.record()
            timeout_repair_run["proposal"] = record
            timeout_repair_run["grounded"] = record["source_revision"] == timeout_request["allowed_source_revision"] and set(record["evidence"]).issubset(set(timeout_request["evidence"]))
            timeout_repair_run["edit_operator"] = raw.get("edit_operator")
            timeout_repair_run["before"] = timeout_request["repair_before"]
            timeout_repair_run["after"] = timeout_request["repair_after"]
            timeout_repair_run["repair_match"] = raw.get("edit_operator") == "lower_timeout_threshold"
            timeout_repair_run["adversarial_review"] = review_proposal(timeout_response.proposal, source_revision=timeout_request["allowed_source_revision"], evidence=timeout_request["evidence"], signal=timeout_case["signal"], cycle=timeout_case["cycle"])
    if os.environ.get("VERIFICATION_REGISTER_REPAIR", "0").strip() == "1":
        register_case = taxonomy["failure_cases"]["register_peripheral"]
        register_evidence = [f"pilot://register_peripheral/{name}" for name in register_case["evidence"]]
        register_request = {
            "task": "propose_repair",
            "design_id": "register_peripheral",
            "fault_class": taxonomy["designs"]["register_peripheral"],
            "failure": {key: register_case[key] for key in ("cycle", "signal", "expected", "actual")},
            "observed_signals": {"valid": "1", "write": "1", "addr": "1", "control": register_case["actual"]},
            "allowed_source_revision": register_case["source_revision"],
            "evidence": register_evidence,
            "dependency_cone": ["wr_en", "addr", "control"],
            "source_context": "else if (wr_en) control <= wdata; // SEEDED_BUG: decode addr zero before write",
            "expected_behavior": "A write to a nonzero address must leave control unchanged; only address zero may update control.",
            "repair_before": "else if (wr_en) control <= wdata;",
            "repair_after": "else if (wr_en && addr == 2'd0) control <= wdata;",
            "repair_requirement": "Select the exact before and after strings supplied in the request. Add only the address-zero decode; do not change reset behavior, data, or signal names.",
            "output_contract": "repair proposal; status must be review_required; do not claim closure; before and after must be exact RTL lines from the supplied choices",
        }
        register_response = invoke_local_backend_batch([register_request])[0]
        register_repair_run = {"design_id": "register_peripheral", "status": register_response.status, "error": register_response.error}
        raw = register_response.raw or {}
        if raw:
            register_repair_run["raw_output"] = raw
        if register_response.proposal is not None:
            record = register_response.proposal.record()
            register_repair_run["proposal"] = record
            register_repair_run["grounded"] = record["source_revision"] == register_request["allowed_source_revision"] and set(record["evidence"]).issubset(set(register_request["evidence"]))
            register_repair_run["repair_match"] = raw.get("before") == register_request["repair_before"] and raw.get("after") == register_request["repair_after"]
            register_repair_run["adversarial_review"] = review_proposal(register_response.proposal, source_revision=register_request["allowed_source_revision"], evidence=register_request["evidence"], signal=register_case["signal"], cycle=register_case["cycle"])
    model_runs["local-batch-command"] = batch_runs
    latencies = {name: [row.get("latency_ms", row.get("batch_latency_ms")) for row in rows if row.get("latency_ms", row.get("batch_latency_ms")) is not None] for name, rows in model_runs.items()}
    latency_summary = {name: {"count": len(values), "p50_ms": round(statistics.median(values), 2), "p95_ms": round(sorted(values)[max(0, int(len(values) * 0.95) - 1)], 2)} for name, values in latencies.items() if values}
    result = {"schema_version": "llm-verification-agent-benchmark-v1", "backend": "deterministic-reference", "design_count": len(proposals), "proposals": proposals, "model_runs": model_runs, "aimc_mutation_run": aimc_mutation_run, "aimc_mutation_repair_run": aimc_mutation_repair_run, "counter_repair_run": counter_repair_run, "timeout_repair_run": timeout_repair_run, "register_repair_run": register_repair_run, "aimc_root_cause_gate": os.environ.get("VERIFICATION_AIMC_ROOT_CAUSE", "0").strip() == "1", "aimc_repair_gate": os.environ.get("VERIFICATION_AIMC_REPAIR", "0").strip() == "1", "counter_repair_gate": os.environ.get("VERIFICATION_COUNTER_REPAIR", "0").strip() == "1", "timeout_repair_gate": os.environ.get("VERIFICATION_TIMEOUT_REPAIR", "0").strip() == "1", "register_repair_gate": os.environ.get("VERIFICATION_REGISTER_REPAIR", "0").strip() == "1", "reference_execution": execution_record, "unsafe_trajectory_rejections": rejections, "local_backend_probe": {"backend": local_probe.backend, "status": local_probe.status, "error": local_probe.error}, "openai_compatible_probe": {"backend": http_probe.backend, "status": http_probe.status, "error": http_probe.error}, "metrics": {"grounded_proposals": sum(item["grounded"] for item in proposals), "review_required": sum(item["proposal"]["status"] == "review_required" for item in proposals), "unsafe_rejected": len(rejections), "forbidden_claims_rejected": any(item["proposal_id"] == "unsafe-claim" for item in rejections), "model_cases": {name: sum(row["status"] == "available" for row in rows) for name, rows in model_runs.items()}, "model_grounded": {name: sum(row.get("grounded", False) for row in rows) for name, rows in model_runs.items()}, "model_diagnosis_match": {name: sum(row.get("diagnosis_match", False) for row in rows) for name, rows in model_runs.items()}, "model_blocked": {name: sum(row["status"] == "blocked" for row in rows) for name, rows in model_runs.items()}, "model_latency_ms": latencies, "model_latency_summary": latency_summary, "batch_latency": {"wall_clock_ms": batch_latency_ms, "case_count": len(batch_requests), "amortized_per_case_ms": round(batch_latency_ms / len(batch_requests), 2) if batch_requests else None, "basis": "one JSONL batch wall-clock measurement; not per-case latency"}}, "claim_boundary": "Provider-neutral agent contract and deterministic baseline only; local model quality is unmeasured unless a local command or OpenAI-compatible endpoint is configured."}
    result["evidence_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"design_count": result["design_count"], "grounded_proposals": result["metrics"]["grounded_proposals"], "unsafe_rejected": result["metrics"]["unsafe_rejected"], "output": str(output)}, sort_keys=True))
    return 0 if result["design_count"] == 11 and result["metrics"]["grounded_proposals"] == 11 and result["metrics"]["unsafe_rejected"] == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
