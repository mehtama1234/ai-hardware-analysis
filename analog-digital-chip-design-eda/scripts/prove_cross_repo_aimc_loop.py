#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen, Request


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
RTL = ROOT / "labs" / "digital" / "aimc-control-plane-rtl"
EVIDENCE = ROOT / "evidence" / "aimc-hardware-lab"
SIM_ADAPTER_EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SIM_PYTHON = Path.home() / "eda-tools" / "aimc-simulators-venv" / "bin" / "python"
if not SIM_PYTHON.exists():
    SIM_PYTHON = Path(sys.executable)
PACKAGE_ID = "pkg-e931662a01293df2"
BACKEND = "http://127.0.0.1:8025"
JSON_OUT = EVIDENCE / "cross-repo-loop-proof.json"
MD_OUT = EVIDENCE / "cross-repo-loop-proof.md"


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def request_json(url: str, *, method: str = "GET", timeout: int = 10, attempts: int = 3) -> dict[str, object]:
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, method=method)
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (TimeoutError, socket.timeout, URLError) as exc:
            last_exc = exc
            if attempt == attempts:
                break
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"{method} {url} failed after {attempts} attempts: {last_exc}") from last_exc


def get_json(url: str) -> dict[str, object]:
    return request_json(url, timeout=10)


def post_json(url: str) -> dict[str, object]:
    return request_json(url, method="POST", timeout=20)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def tool_status(payload: dict[str, object], tool_name: str) -> dict[str, object]:
    tools = payload.get("tools")
    if not isinstance(tools, list):
        return {}
    for item in tools:
        if isinstance(item, dict) and item.get("tool") == tool_name:
            return item
    return {}


def write_reports(report: dict[str, object]) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    claim_summary = report["claim_summary"]
    lines = [
        "# Cross-Repo AIMC Loop Proof",
        "",
        "This report records the proof that the restored workbench and the newer hardware lab are connected as one loop.",
        "",
        "## What Ran",
        "",
        "```text",
        "backend health",
        "  -> backend hardware placement",
        "  -> hardware-lab placement import",
        "  -> governor request generation",
        "  -> generated Verilog governor cases",
        "  -> RTL trace check",
        "  -> AIHWKIT/CrossSim adapter availability check",
        "  -> optional AIHWKIT/CrossSim payload run path",
        "  -> tensor-shaped AIHWKIT/CrossSim payload run path",
        "  -> trained-weight AIHWKIT/CrossSim payload run path",
        "  -> projection-stack AIHWKIT/CrossSim payload run path",
        "  -> transformer-MLP-block AIHWKIT/CrossSim payload run path",
        "  -> calibrated transformer-MLP-block AIHWKIT/CrossSim payload run path",
        "  -> calibrated deep transformer-MLP-stack AIHWKIT/CrossSim payload run path",
        "  -> attention-block AIHWKIT/CrossSim payload run path",
        "  -> calibrated attention-block AIHWKIT/CrossSim payload run path",
        "  -> calibrated residual governor bridge",
        "  -> residual-aware placement decisions",
        "  -> hardware-lab evidence export",
        "  -> backend hardware-lab evidence import",
        "  -> package claim-readiness refresh",
        "```",
        "",
        "## Result",
        "",
        f"- status: {report['status']}",
        f"- package: {report['package_id']}",
        f"- backend operators: {summary['backend_operators']}",
        f"- backend analog candidates: {summary['backend_analog_candidates']}",
        f"- governor rows: {summary['governor_rows']}",
        f"- backend governor rows: {summary['backend_governor_rows']}",
        f"- RTL: {summary['rtl']}",
        f"- exported evidence records: {summary['export_items']}",
        f"- backend import accepted: {summary['backend_import_accepted']}",
        f"- strict simulator/tool evidence imported: {summary.get('strict_tool_evidence_imported')}",
        f"- AIHWKIT adapter: {summary.get('aihwkit_adapter')}",
        f"- CrossSim adapter: {summary.get('crosssim_adapter')}",
        f"- optional simulator payloads: {json.dumps(summary.get('optional_simulator_payloads'), sort_keys=True)}",
        f"- tensor-shaped simulator payloads: {json.dumps(summary.get('tensor_shape_simulator_payloads'), sort_keys=True)}",
        f"- trained-weight simulator payloads: {json.dumps(summary.get('trained_weight_simulator_payloads'), sort_keys=True)}",
        f"- projection-stack simulator payloads: {json.dumps(summary.get('projection_stack_simulator_payloads'), sort_keys=True)}",
        f"- transformer-MLP-block simulator payloads: {json.dumps(summary.get('transformer_mlp_block_simulator_payloads'), sort_keys=True)}",
        f"- calibrated transformer-MLP-block simulator payloads: {json.dumps(summary.get('calibrated_transformer_mlp_block_simulator_payloads'), sort_keys=True)}",
        f"- calibrated deep transformer-MLP-stack simulator payloads: {json.dumps(summary.get('calibrated_deep_transformer_mlp_stack_simulator_payloads'), sort_keys=True)}",
        f"- attention-block simulator payloads: {json.dumps(summary.get('attention_block_simulator_payloads'), sort_keys=True)}",
        f"- calibrated attention-block simulator payloads: {json.dumps(summary.get('calibrated_attention_block_simulator_payloads'), sort_keys=True)}",
        f"- calibrated residual governor rows: {summary.get('calibrated_residual_governor_rows')}",
        f"- calibrated residual analog decisions: {summary.get('calibrated_residual_analog_decisions')}",
        f"- residual-aware placement allowed rows: {summary.get('residual_aware_placement_allowed')}",
        "",
        "## Claim Status",
        "",
        f"- supported lab claims: {claim_summary['supported_lab_claims']}",
        f"- needs-review lab claims: {claim_summary['needs_review_lab_claims']}",
        f"- blocked lab claims: {claim_summary['blocked_lab_claims']}",
        f"- production claim: {claim_summary['production_claim']}",
        f"- overall: {claim_summary['overall']}",
        "",
        "## What This Proves",
        "",
        "The model graph in the restored backend can produce a hardware-placement artifact. The hardware lab can import that artifact, convert it into governor-sized rows, generate Verilog cases, pass the RTL checker, check optional AIHWKIT/CrossSim availability, run small optional simulator fixtures, run tensor-shaped simulator payloads for the backend analog MatMul candidates, run trained-weight simulator payloads from the uploaded ONNX model, run a larger projection-stack ONNX replay, run a transformer-MLP-shaped ONNX replay with nonlinear and residual operations kept digital, run a held-out calibrated MLP replay, run a deeper held-out calibrated MLP-stack replay, run an attention-shaped ONNX replay with static projections separated from dynamic attention operations, run a held-out calibrated attention replay, convert calibrated residuals into governor decisions, filter structural placement through those residual-aware decisions, export normalized evidence, re-import that evidence into the backend package, and keep the deployment archive aligned with the API for residual-aware placement and C2/C3 claim-readiness boundaries.",
        "",
        "## What This Does Not Prove",
        "",
        "This does not prove measured board latency, measured energy, calibrated silicon behavior, pretrained foundation-model AIHWKIT/CrossSim agreement, analog macro layout, package reliability, or tapeout readiness. The backend correctly keeps latency and energy in needs-review status and keeps production readiness blocked. Measured energy needs measured runtime and measured power tied to the same runtime trace ID, package, workload, board, start time, and end time.",
        "",
    ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    health = get_json(f"{BACKEND}/health")
    require(health.get("status") == "ok", "backend health check failed")

    placement = get_json(f"{BACKEND}/deployment-packages/{PACKAGE_ID}/hardware-placement")
    summary = placement.get("summary") if isinstance(placement.get("summary"), dict) else {}
    require(summary.get("operators", 0) >= 1, "hardware placement has no operators")
    require(summary.get("analog_candidates", 0) >= 1, "hardware placement has no analog candidates")

    run(["python3", "scripts/import_backend_hardware_placement.py"], ROOT)
    imported_rows = read_rows(MEASURE / "backend-hardware-placement-governor-input.csv")
    require(len(imported_rows) == summary.get("operators"), "imported placement row count does not match backend operators")

    generator_output = run(["python3", "python/model_impact_governor_requests.py"], ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware")
    request_rows = read_rows(MEASURE / "model-impact-governor-requests.csv")
    backend_rows = [row for row in request_rows if row["policy"].startswith("backend_")]
    require(len(backend_rows) == len(imported_rows), "backend placement rows were not appended to governor requests")
    require(any(row["governor_decision"] == "1" for row in backend_rows), "backend placement rows contain no allowed analog case")

    rtl_output = run(["python3", "check_generated_model_impact_governor_trace.py"], RTL)
    require("PASS generated_model_impact_governor_trace" in rtl_output, "RTL governor trace failed")
    require(f"cases {len(request_rows)}" in rtl_output, "RTL case count does not match governor request rows")

    simulator_output = run([str(SIM_PYTHON), "scripts/check_aimc_simulator_adapters.py"], ROOT)
    require("aimc_simulator_adapter_status" in simulator_output, "simulator adapter status check did not run")
    simulator_status_path = SIM_ADAPTER_EVIDENCE / "simulator-adapter-status.json"
    require(simulator_status_path.exists(), "simulator adapter status JSON is missing")
    simulator_status = json.loads(simulator_status_path.read_text(encoding="utf-8"))
    aihwkit = tool_status(simulator_status, "aihwkit")
    crosssim = tool_status(simulator_status, "crosssim")
    optional_payload_output = run([str(SIM_PYTHON), "scripts/run_optional_aimc_simulator_payloads.py"], ROOT)
    require("optional_aimc_simulator_payloads" in optional_payload_output, "optional simulator payload run did not execute")
    optional_payload_summary_path = SIM_ADAPTER_EVIDENCE / "optional-simulator-payload-run-summary.json"
    require(optional_payload_summary_path.exists(), "optional simulator payload run summary is missing")
    optional_payload_summary = json.loads(optional_payload_summary_path.read_text(encoding="utf-8"))
    optional_results = optional_payload_summary.get("results") if isinstance(optional_payload_summary.get("results"), list) else []
    optional_statuses = {
        item.get("tool"): item.get("status")
        for item in optional_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    tensor_output = run([str(SIM_PYTHON), "scripts/run_tensor_shape_aimc_simulator_payloads.py"], ROOT)
    require("tensor_shape_aimc_simulator_payloads" in tensor_output, "tensor-shaped simulator payload run did not execute")
    tensor_summary_path = SIM_ADAPTER_EVIDENCE / "tensor-shape-simulator-payload-run-summary.json"
    require(tensor_summary_path.exists(), "tensor-shaped simulator payload run summary is missing")
    tensor_summary = json.loads(tensor_summary_path.read_text(encoding="utf-8"))
    require(tensor_summary.get("candidate_count") == 2, "tensor-shaped simulator payload run should cover 2 backend analog MatMul candidates")
    tensor_results = tensor_summary.get("results") if isinstance(tensor_summary.get("results"), list) else []
    tensor_statuses = {
        item.get("tool"): item.get("status")
        for item in tensor_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    trained_output = run([str(SIM_PYTHON), "scripts/run_trained_weight_aimc_simulator_payloads.py"], ROOT)
    require("trained_weight_aimc_simulator_payloads" in trained_output, "trained-weight simulator payload run did not execute")
    trained_summary_path = SIM_ADAPTER_EVIDENCE / "trained-weight-simulator-payload-run-summary.json"
    require(trained_summary_path.exists(), "trained-weight simulator payload run summary is missing")
    trained_summary = json.loads(trained_summary_path.read_text(encoding="utf-8"))
    require(trained_summary.get("candidate_count") == 2, "trained-weight simulator payload run should cover 2 backend analog MatMul candidates")
    trained_results = trained_summary.get("results") if isinstance(trained_summary.get("results"), list) else []
    trained_statuses = {
        item.get("tool"): item.get("status")
        for item in trained_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    projection_output = run([str(SIM_PYTHON), "scripts/run_projection_stack_aimc_simulator_payloads.py"], ROOT)
    require("projection_stack_aimc_simulator_payloads" in projection_output, "projection-stack simulator payload run did not execute")
    projection_summary_path = SIM_ADAPTER_EVIDENCE / "projection-stack-simulator-payload-run-summary.json"
    require(projection_summary_path.exists(), "projection-stack simulator payload run summary is missing")
    projection_summary = json.loads(projection_summary_path.read_text(encoding="utf-8"))
    require(projection_summary.get("candidate_count") == 4, "projection-stack simulator payload run should cover 4 MatMul candidates")
    projection_results = projection_summary.get("results") if isinstance(projection_summary.get("results"), list) else []
    projection_statuses = {
        item.get("tool"): item.get("status")
        for item in projection_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    transformer_mlp_output = run([str(SIM_PYTHON), "scripts/run_transformer_mlp_block_aimc_simulator_payloads.py"], ROOT)
    require("transformer_mlp_block_aimc_simulator_payloads" in transformer_mlp_output, "transformer MLP-block simulator payload run did not execute")
    transformer_mlp_summary_path = SIM_ADAPTER_EVIDENCE / "transformer-mlp-block-simulator-payload-run-summary.json"
    require(transformer_mlp_summary_path.exists(), "transformer MLP-block simulator payload run summary is missing")
    transformer_mlp_summary = json.loads(transformer_mlp_summary_path.read_text(encoding="utf-8"))
    require(transformer_mlp_summary.get("candidate_count") == 4, "transformer MLP-block simulator payload run should cover 4 MatMul candidates")
    transformer_mlp_results = transformer_mlp_summary.get("results") if isinstance(transformer_mlp_summary.get("results"), list) else []
    transformer_mlp_statuses = {
        item.get("tool"): item.get("status")
        for item in transformer_mlp_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    calibrated_transformer_mlp_output = run([str(SIM_PYTHON), "scripts/run_calibrated_transformer_mlp_block_aimc_simulator_payloads.py"], ROOT)
    require("calibrated_transformer_mlp_block_aimc_simulator_payloads" in calibrated_transformer_mlp_output, "calibrated transformer MLP-block simulator payload run did not execute")
    calibrated_transformer_mlp_summary_path = SIM_ADAPTER_EVIDENCE / "calibrated-transformer-mlp-block-simulator-payload-run-summary.json"
    require(calibrated_transformer_mlp_summary_path.exists(), "calibrated transformer MLP-block simulator payload run summary is missing")
    calibrated_transformer_mlp_summary = json.loads(calibrated_transformer_mlp_summary_path.read_text(encoding="utf-8"))
    require(calibrated_transformer_mlp_summary.get("candidate_count") == 4, "calibrated transformer MLP-block simulator payload run should cover 4 MatMul candidates")
    calibrated_transformer_mlp_results = calibrated_transformer_mlp_summary.get("results") if isinstance(calibrated_transformer_mlp_summary.get("results"), list) else []
    calibrated_transformer_mlp_statuses = {
        item.get("tool"): item.get("status")
        for item in calibrated_transformer_mlp_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    calibrated_deep_transformer_mlp_output = run([str(SIM_PYTHON), "scripts/run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads.py"], ROOT)
    require("calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads" in calibrated_deep_transformer_mlp_output, "calibrated deep transformer MLP-stack simulator payload run did not execute")
    calibrated_deep_transformer_mlp_summary_path = SIM_ADAPTER_EVIDENCE / "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json"
    require(calibrated_deep_transformer_mlp_summary_path.exists(), "calibrated deep transformer MLP-stack simulator payload run summary is missing")
    calibrated_deep_transformer_mlp_summary = json.loads(calibrated_deep_transformer_mlp_summary_path.read_text(encoding="utf-8"))
    require(calibrated_deep_transformer_mlp_summary.get("candidate_count") == 12, "calibrated deep transformer MLP-stack simulator payload run should cover 12 MatMul candidates")
    calibrated_deep_transformer_mlp_results = calibrated_deep_transformer_mlp_summary.get("results") if isinstance(calibrated_deep_transformer_mlp_summary.get("results"), list) else []
    calibrated_deep_transformer_mlp_statuses = {
        item.get("tool"): item.get("status")
        for item in calibrated_deep_transformer_mlp_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    attention_output = run([str(SIM_PYTHON), "scripts/run_attention_block_aimc_simulator_payloads.py"], ROOT)
    require("attention_block_aimc_simulator_payloads" in attention_output, "attention-block simulator payload run did not execute")
    attention_summary_path = SIM_ADAPTER_EVIDENCE / "attention-block-simulator-payload-run-summary.json"
    require(attention_summary_path.exists(), "attention-block simulator payload run summary is missing")
    attention_summary = json.loads(attention_summary_path.read_text(encoding="utf-8"))
    require(attention_summary.get("candidate_count") == 4, "attention-block simulator payload run should cover 4 static projection candidates")
    attention_results = attention_summary.get("results") if isinstance(attention_summary.get("results"), list) else []
    attention_statuses = {
        item.get("tool"): item.get("status")
        for item in attention_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    calibrated_attention_output = run([str(SIM_PYTHON), "scripts/run_calibrated_attention_block_aimc_simulator_payloads.py"], ROOT)
    require("calibrated_attention_block_aimc_simulator_payloads" in calibrated_attention_output, "calibrated attention-block simulator payload run did not execute")
    calibrated_attention_summary_path = SIM_ADAPTER_EVIDENCE / "calibrated-attention-block-simulator-payload-run-summary.json"
    require(calibrated_attention_summary_path.exists(), "calibrated attention-block simulator payload run summary is missing")
    calibrated_attention_summary = json.loads(calibrated_attention_summary_path.read_text(encoding="utf-8"))
    require(calibrated_attention_summary.get("candidate_count") == 4, "calibrated attention-block simulator payload run should cover 4 static projection candidates")
    calibrated_attention_results = calibrated_attention_summary.get("results") if isinstance(calibrated_attention_summary.get("results"), list) else []
    calibrated_attention_statuses = {
        item.get("tool"): item.get("status")
        for item in calibrated_attention_results
        if isinstance(item, dict) and isinstance(item.get("tool"), str)
    }
    calibrated_bridge_output = run(["python3", "scripts/run_calibrated_residual_governor_bridge.py"], ROOT)
    require("calibrated_residual_governor_bridge" in calibrated_bridge_output, "calibrated residual governor bridge did not execute")
    calibrated_bridge_path = SIM_ADAPTER_EVIDENCE / "calibrated-residual-governor-bridge.json"
    require(calibrated_bridge_path.exists(), "calibrated residual governor bridge JSON is missing")
    calibrated_bridge = json.loads(calibrated_bridge_path.read_text(encoding="utf-8"))
    calibrated_bridge_rows = calibrated_bridge.get("rows") if isinstance(calibrated_bridge.get("rows"), list) else []
    require(any(isinstance(row, dict) and row.get("accepted_as_positive_evidence") is True for row in calibrated_bridge_rows), "calibrated residual bridge has no accepted positive-evidence row")
    require(any(isinstance(row, dict) and row.get("governor_decision") == 1 for row in calibrated_bridge_rows), "calibrated residual bridge has no analog governor decision")
    residual_placement_output = run(["python3", "scripts/run_residual_aware_placement_decisions.py"], ROOT)
    require("residual_aware_placement_decisions" in residual_placement_output, "residual-aware placement decisions did not execute")
    residual_placement_path = SIM_ADAPTER_EVIDENCE / "residual-aware-placement-decisions.json"
    require(residual_placement_path.exists(), "residual-aware placement decision JSON is missing")
    residual_placement = json.loads(residual_placement_path.read_text(encoding="utf-8"))
    residual_placement_summary = residual_placement.get("summary") if isinstance(residual_placement.get("summary"), dict) else {}
    require(residual_placement_summary.get("residual_aware_analog_allowed", 0) >= 1, "residual-aware placement has no analog-allowed rows")

    export_output = run(["python3", "scripts/export_aimc_hardware_lab_evidence.py"], ROOT)
    require("items,6" in export_output, "hardware evidence export did not emit 6 items")
    require("valid,6" in export_output, "hardware evidence export did not validate 6 items")

    imported = post_json(f"{BACKEND}/deployment-packages/{PACKAGE_ID}/hardware-lab-evidence")
    require(imported.get("accepted_count") == 6, "backend hardware-lab import did not accept 6 ordinary records")
    require(imported.get("rejected_count") == 0, "backend hardware-lab import rejected records")
    strict_tool = imported.get("strict_tool_evidence") if isinstance(imported.get("strict_tool_evidence"), dict) else {}
    require(strict_tool.get("imported") is True, "strict analog tool evidence was not imported")

    claims = get_json(f"{BACKEND}/deployment-packages/{PACKAGE_ID}/claim-readiness")
    claim_summary = claims.get("summary") if isinstance(claims.get("summary"), dict) else {}
    require(claim_summary.get("supported_lab_claims") == 3, "unexpected supported claim count")
    require(claim_summary.get("needs_review_lab_claims") == 2, "unexpected needs-review claim count")
    require(claim_summary.get("production_claim") == "blocked", "production claim should remain blocked")

    report = {
        "result_type": "cross_repo_aimc_loop_proof",
        "status": "PASS",
        "package_id": PACKAGE_ID,
        "backend": BACKEND,
        "summary": {
            "backend_operators": summary.get("operators"),
            "backend_analog_candidates": summary.get("analog_candidates"),
            "governor_rows": len(request_rows),
            "backend_governor_rows": len(backend_rows),
            "rtl": "pass",
            "export_items": 6,
            "backend_import_accepted": imported.get("accepted_count"),
            "strict_tool_evidence_imported": strict_tool.get("imported"),
            "aihwkit_adapter": aihwkit.get("status", "unknown"),
            "crosssim_adapter": crosssim.get("status", "unknown"),
            "optional_simulator_payloads": optional_statuses,
            "tensor_shape_simulator_payloads": tensor_statuses,
            "trained_weight_simulator_payloads": trained_statuses,
            "projection_stack_simulator_payloads": projection_statuses,
            "transformer_mlp_block_simulator_payloads": transformer_mlp_statuses,
            "calibrated_transformer_mlp_block_simulator_payloads": calibrated_transformer_mlp_statuses,
            "calibrated_deep_transformer_mlp_stack_simulator_payloads": calibrated_deep_transformer_mlp_statuses,
            "attention_block_simulator_payloads": attention_statuses,
            "calibrated_attention_block_simulator_payloads": calibrated_attention_statuses,
            "calibrated_residual_governor_rows": len(calibrated_bridge_rows),
            "calibrated_residual_analog_decisions": sum(1 for row in calibrated_bridge_rows if isinstance(row, dict) and row.get("governor_decision") == 1),
            "residual_aware_placement_allowed": residual_placement_summary.get("residual_aware_analog_allowed"),
        },
        "claim_summary": claim_summary,
        "artifacts": {
            "backend_hardware_placement": str(MEASURE / "backend-hardware-placement.json"),
            "backend_governor_input": str(MEASURE / "backend-hardware-placement-governor-input.csv"),
            "governor_requests": str(MEASURE / "model-impact-governor-requests.csv"),
            "evidence_batch": str(EVIDENCE / "import-batch.json"),
            "simulator_adapter_status": str(simulator_status_path),
            "simulator_adapter_markdown": str(SIM_ADAPTER_EVIDENCE / "simulator-adapter-status.md"),
            "optional_simulator_payload_summary": str(optional_payload_summary_path),
            "tensor_shape_simulator_payload_summary": str(tensor_summary_path),
            "trained_weight_simulator_payload_summary": str(trained_summary_path),
            "projection_stack_simulator_payload_summary": str(projection_summary_path),
            "transformer_mlp_block_simulator_payload_summary": str(transformer_mlp_summary_path),
            "calibrated_transformer_mlp_block_simulator_payload_summary": str(calibrated_transformer_mlp_summary_path),
            "calibrated_deep_transformer_mlp_stack_simulator_payload_summary": str(calibrated_deep_transformer_mlp_summary_path),
            "attention_block_simulator_payload_summary": str(attention_summary_path),
            "calibrated_attention_block_simulator_payload_summary": str(calibrated_attention_summary_path),
            "calibrated_residual_governor_bridge": str(calibrated_bridge_path),
            "residual_aware_placement_decisions": str(residual_placement_path),
            "json_report": str(JSON_OUT),
            "markdown_report": str(MD_OUT),
        },
        "claim_boundary": {
            "allowed": "cross-repo prototype loop proof for model graph to hardware-lab evidence to backend claim readiness, with simulator adapter availability, small optional payload runs, tensor-shaped backend MatMul payload runs, trained-weight tiny-MLP payload runs, projection-stack payload runs, transformer-MLP-block payload runs, calibrated transformer-MLP-block payload runs, calibrated deep transformer-MLP-stack payload runs, attention-block payload runs, calibrated attention-block payload runs, calibrated residual governor bridge decisions, and residual-aware placement decisions recorded",
            "not_allowed": "measured board performance, measured power, measured energy without same-runtime-trace runtime and power evidence, calibrated silicon, pretrained foundation-model AIHWKIT/CrossSim agreement, analog macro layout, package reliability, or tapeout readiness",
        },
    }
    write_reports(report)

    print("PASS cross_repo_aimc_loop")
    print(f"package,{PACKAGE_ID}")
    print(f"backend_operators,{summary.get('operators')}")
    print(f"backend_analog_candidates,{summary.get('analog_candidates')}")
    print(f"governor_rows,{len(request_rows)}")
    print(f"backend_governor_rows,{len(backend_rows)}")
    print("rtl,pass")
    print("export_items,6")
    print("backend_import_accepted,6")
    print(f"strict_tool_evidence_imported,{strict_tool.get('imported')}")
    print(f"aihwkit_adapter,{aihwkit.get('status', 'unknown')}")
    print(f"crosssim_adapter,{crosssim.get('status', 'unknown')}")
    print(f"optional_simulator_payloads,{json.dumps(optional_statuses, sort_keys=True)}")
    print(f"tensor_shape_simulator_payloads,{json.dumps(tensor_statuses, sort_keys=True)}")
    print(f"trained_weight_simulator_payloads,{json.dumps(trained_statuses, sort_keys=True)}")
    print(f"projection_stack_simulator_payloads,{json.dumps(projection_statuses, sort_keys=True)}")
    print(f"transformer_mlp_block_simulator_payloads,{json.dumps(transformer_mlp_statuses, sort_keys=True)}")
    print(f"calibrated_transformer_mlp_block_simulator_payloads,{json.dumps(calibrated_transformer_mlp_statuses, sort_keys=True)}")
    print(f"calibrated_deep_transformer_mlp_stack_simulator_payloads,{json.dumps(calibrated_deep_transformer_mlp_statuses, sort_keys=True)}")
    print(f"attention_block_simulator_payloads,{json.dumps(attention_statuses, sort_keys=True)}")
    print(f"calibrated_attention_block_simulator_payloads,{json.dumps(calibrated_attention_statuses, sort_keys=True)}")
    print(f"calibrated_residual_governor_rows,{len(calibrated_bridge_rows)}")
    print(f"calibrated_residual_analog_decisions,{sum(1 for row in calibrated_bridge_rows if isinstance(row, dict) and row.get('governor_decision') == 1)}")
    print(f"residual_aware_placement_allowed,{residual_placement_summary.get('residual_aware_analog_allowed')}")
    print(f"report_json,{JSON_OUT}")
    print(f"report_markdown,{MD_OUT}")
    print(f"claim_summary,{json.dumps(claim_summary, sort_keys=True)}")
    print("generator," + generator_output.splitlines()[0])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL cross_repo_aimc_loop: {exc}", file=sys.stderr)
        raise
