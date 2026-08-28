PHYSICAL_AI_ROADMAP_SCHEMA_VERSION = "physical-ai-roadmap-v0.1"


STATUS_RANK = {
    "supported": 0,
    "needs measurement": 1,
    "roadmap connector": 2,
    "blocked": 3,
    "do not claim": 4,
}


def _source_status(measurement_evidence, source_id):
    for source in (measurement_evidence or {}).get("required_sources", []):
        if source.get("id") == source_id:
            return source.get("status", "missing")
    return "missing"


def _claim_summary(claim_readiness):
    summary = (claim_readiness or {}).get("summary", {})
    production = (claim_readiness or {}).get("production_claim", {})
    return {
        "supported_lab_claims": summary.get("supported_lab_claims", 0),
        "needs_review_lab_claims": summary.get("needs_review_lab_claims", 0),
        "blocked_lab_claims": summary.get("blocked_lab_claims", 0),
        "production_readiness": production.get("status", "blocked"),
    }


def _gate(gate_id, name, status, evidence_state, safe_claim, next_action, artifact=None, risk="medium"):
    return {
        "id": gate_id,
        "name": name,
        "status": status,
        "risk": risk,
        "artifact": artifact,
        "evidence_state": evidence_state,
        "safe_claim": safe_claim,
        "next_action": next_action,
    }


def _model_fit_gate(analysis, package_report):
    summary = (analysis or {}).get("summary", {})
    unsupported = sum(1 for layer in (analysis or {}).get("layers", []) if layer.get("placement") == "unsupported")
    fallback = sum(1 for layer in (analysis or {}).get("layers", []) if layer.get("placement") == "fallback")
    if unsupported:
        status = "blocked"
        safe_claim = "Do not claim deployability until unsupported operators are rewritten or implemented."
    elif fallback:
        status = "needs measurement"
        safe_claim = "Claim analysis-package fit only; fallback latency, energy, and accuracy still need evidence."
    else:
        status = "needs measurement" if (package_report or {}).get("readiness_stage") not in {"prototype-ready", "candidate"} else "supported"
        safe_claim = "Claim model/operator compatibility at analysis level until compiler and board evidence are attached."
    return _gate(
        "model_fit",
        "Model and operator fit",
        status,
        f"{summary.get('analog_coverage_percent', 0)}% analog coverage, {fallback} fallback, {unsupported} unsupported.",
        safe_claim,
        "Close unsupported and fallback operators, then attach compiler placement evidence.",
        artifact="analysis",
        risk="high" if unsupported else "medium",
    )


def _domain_gate(physical_ai_map):
    summary = (physical_ai_map or {}).get("summary", {})
    selected = (physical_ai_map or {}).get("selected_domain_label") or (physical_ai_map or {}).get("selected_domain", "unknown")
    evidence_gap = summary.get("main_evidence_gap", "domain evidence not attached")
    return _gate(
        "domain_fit",
        "Physical AI domain fit",
        "needs measurement",
        f"{selected}; main gap: {evidence_gap}.",
        "Use domain fit as roadmap context, not proof of chip performance.",
        "Attach domain metric, task dataset, physical failure mode, and customer environment evidence.",
        artifact="physical_ai_map",
    )


def _vla_gate(vla_readiness):
    summary = (vla_readiness or {}).get("summary", {})
    claim = (vla_readiness or {}).get("claim_level", "unknown")
    status = "blocked" if "not VLA-ready" in claim or "not vla-ready" in claim.lower() else "needs measurement"
    return _gate(
        "vla_transformer_fit",
        "Transformer and VLA fit",
        status,
        f"{(vla_readiness or {}).get('model_family', 'unknown')}; readiness score {summary.get('readiness_score', 'unknown')}.",
        "Do not use analog MAC efficiency alone as a VLA or robotics-readiness claim.",
        "Prove attention, memory movement, digital support, and action/multimodal boundary behavior on target graphs.",
        artifact="vla_readiness",
        risk="high" if status == "blocked" else "medium",
    )


def _weight_gate(weight_update_readiness):
    readiness = (weight_update_readiness or {}).get("readiness", "unknown")
    status = "blocked" if "blocked" in readiness else "needs measurement"
    if readiness in {"not_measured_for_updates"}:
        status = "do not claim"
    return _gate(
        "weight_update_fit",
        "Weight update fit",
        status,
        f"{(weight_update_readiness or {}).get('assumed_update_pattern', 'unknown')} update pattern; {readiness}.",
        (weight_update_readiness or {}).get("summary", {}).get("claim_boundary", "Do not claim adaptive updates without write evidence."),
        "Measure write latency, write energy, endurance, post-write accuracy, recalibration, and rollback.",
        artifact="weight_update_readiness",
        risk=(weight_update_readiness or {}).get("risk", "high"),
    )


def _calibration_gate(calibration_drift_readiness):
    readiness = (calibration_drift_readiness or {}).get("readiness", "unknown")
    status = "blocked" if readiness == "blocked_for_measured_claims" else "needs measurement"
    return _gate(
        "calibration_drift_fit",
        "Calibration and drift fit",
        status,
        f"{readiness}; {(calibration_drift_readiness or {}).get('summary', {}).get('analog_error_status', 'missing')} analog-error evidence.",
        (calibration_drift_readiness or {}).get("summary", {}).get("claim_boundary", "Production drift claims remain blocked."),
        "Run analog-error, thermal, board-stability, aging, recalibration, and failure-behavior sweeps.",
        artifact="calibration_drift_readiness",
        risk=(calibration_drift_readiness or {}).get("risk", "high"),
    )


def _control_gate(control_boundary):
    role = (control_boundary or {}).get("deterministic_control_role", "deterministic control boundary not defined")
    return _gate(
        "control_boundary_fit",
        "Deterministic control boundary",
        "needs measurement",
        role,
        "Claim inference acceleration only unless controller timing, safety handoff, and fallback behavior are specified.",
        "Attach controller contract, jitter budget, interlock behavior, actuator handoff, and safe fallback proof.",
        artifact="control_boundary",
        risk="high",
    )


def _sensor_gate(sensor_boundary_readiness):
    summary = (sensor_boundary_readiness or {}).get("summary", {})
    status = "blocked" if (sensor_boundary_readiness or {}).get("readiness") == "sensor_boundary_unproven" else "needs measurement"
    return _gate(
        "sensor_boundary_fit",
        "Sensor boundary fit",
        status,
        f"{summary.get('expected_sensors', 'unknown sensors')}; preprocessing owner: {summary.get('preprocessing_owner', 'unknown')}.",
        "Do not claim sensor-to-output efficiency from inference-only energy.",
        "Count AFE, event/tactile/sync, preprocessing, sensor-to-output latency, and host movement.",
        artifact="sensor_boundary_readiness",
        risk="high" if status == "blocked" else "medium",
    )


def _compiler_gate(compiler_ecosystem_readiness):
    summary = (compiler_ecosystem_readiness or {}).get("summary", {})
    readiness = (compiler_ecosystem_readiness or {}).get("readiness", "unknown")
    status = "supported" if readiness == "evidence_backed_mapping" else "roadmap connector"
    return _gate(
        "compiler_fit",
        "Compiler ecosystem fit",
        status,
        f"ONNX: {summary.get('onnx_status', 'unknown')}; PyTorch: {summary.get('pytorch_status', 'unknown')}; JAX/XLA: {summary.get('jax_xla_status', 'unknown')}.",
        "Claim ONNX-first prototype support only unless real compiler mapping and developer paths are implemented.",
        "Connect compiler mapping, explainable placement, PyTorch export, JAX/XLA or StableHLO path, and profiling/debug views.",
        artifact="compiler_ecosystem_readiness",
        risk="high" if status == "roadmap connector" else "medium",
    )


def _runtime_power_gate(runtime_profile, measurement_evidence):
    runtime_status = (runtime_profile or {}).get("provenance", "unknown")
    board_status = _source_status(measurement_evidence, "board_runtime")
    power_status = _source_status(measurement_evidence, "power_thermal")
    supported = board_status == "imported artifact" and power_status == "imported artifact"
    return _gate(
        "runtime_power_fit",
        "Runtime, power, and thermal fit",
        "supported" if supported else "needs measurement",
        f"runtime {runtime_status}; board {board_status}; power/thermal {power_status}.",
        "Keep latency, energy, and thermal claims in estimate or lab-review language until board and power evidence are imported.",
        "Attach board runtime traces and power/thermal artifacts that count host, fallback, conversion, idle, and thermal behavior.",
        artifact="measurement_evidence",
        risk="high" if not supported else "medium",
    )


def _task_accuracy_gate(measurement_evidence):
    accuracy_status = _source_status(measurement_evidence, "task_accuracy")
    analog_status = _source_status(measurement_evidence, "analog_error_simulation")
    supported = accuracy_status == "imported artifact" and analog_status == "imported artifact"
    return _gate(
        "task_accuracy_fit",
        "Task accuracy fit",
        "supported" if supported else "needs measurement",
        f"task accuracy {accuracy_status}; analog error {analog_status}.",
        "Do not claim the task survives analog mapping until task accuracy and analog-error evidence are both imported.",
        "Attach dataset-backed task metric and analog error/quantization impact evidence under the selected calibration profile.",
        artifact="measurement_evidence",
        risk="high" if not supported else "medium",
    )


def _evidence_gate(measurement_evidence, claim_readiness, evidence_audit, source_check_register):
    claims = _claim_summary(claim_readiness)
    source_checked = (source_check_register or {}).get("summary", {}).get("checked_items", 0)
    status = "blocked" if claims["production_readiness"] == "blocked" else "needs measurement"
    return _gate(
        "evidence_integrity",
        "Evidence and claim integrity",
        status,
        f"{claims['supported_lab_claims']} supported lab claims; {source_checked} source-checked examples; production {claims['production_readiness']}.",
        "Measured, imported, local, simulated, failed, and source-checked artifacts must stay separate.",
        "Import normalized evidence for blocked sources and preserve failed connector attempts in the audit trail.",
        artifact="claim_readiness",
        risk="high",
    )


def _gap_table(gates):
    gaps = []
    for gate in gates:
        if gate["status"] == "supported":
            continue
        gaps.append({
            "gate_id": gate["id"],
            "status": gate["status"],
            "claim_impact": "high" if gate["status"] in {"blocked", "do not claim"} or gate["risk"] == "high" else "medium",
            "evidence_gap": gate["evidence_state"],
            "next_action": gate["next_action"],
            "safe_claim": gate["safe_claim"],
        })
    return sorted(gaps, key=lambda item: STATUS_RANK.get(item["status"], 5))


def build_physical_ai_roadmap(
    package_report,
    analysis,
    runtime_profile,
    physical_ai_map=None,
    vla_readiness=None,
    weight_update_readiness=None,
    calibration_drift_readiness=None,
    control_boundary=None,
    sensor_boundary_readiness=None,
    compiler_ecosystem_readiness=None,
    measurement_evidence=None,
    claim_readiness=None,
    evidence_audit=None,
    source_check_register=None,
):
    gates = [
        _domain_gate(physical_ai_map),
        _model_fit_gate(analysis, package_report),
        _vla_gate(vla_readiness),
        _weight_gate(weight_update_readiness),
        _calibration_gate(calibration_drift_readiness),
        _control_gate(control_boundary),
        _sensor_gate(sensor_boundary_readiness),
        _compiler_gate(compiler_ecosystem_readiness),
        _runtime_power_gate(runtime_profile, measurement_evidence),
        _task_accuracy_gate(measurement_evidence),
        _evidence_gate(measurement_evidence, claim_readiness, evidence_audit, source_check_register),
    ]
    counts = {status: sum(1 for gate in gates if gate["status"] == status) for status in STATUS_RANK}
    gap_table = _gap_table(gates)
    claim_summary = _claim_summary(claim_readiness)
    safe_claim = (
        "Physical AI production readiness is blocked; use this as an evidence-backed roadmap package."
        if claim_summary["production_readiness"] == "blocked"
        else "Physical AI readiness still requires per-gate review before production claims."
    )
    return {
        "result_type": "physical_ai_roadmap",
        "schema_version": PHYSICAL_AI_ROADMAP_SCHEMA_VERSION,
        "provenance": "aggregated from package readiness, Physical AI gate artifacts, measurement evidence, claim readiness, evidence audit, and source-check register",
        "confidence": "low",
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "plain_reading": "This is the single roadmap view: what the analog chip can claim now, what remains measured-evidence work, and which Physical AI gates are blocked.",
            "safe_claim": safe_claim,
            "gate_count": len(gates),
            "supported": counts["supported"],
            "needs_measurement": counts["needs measurement"],
            "roadmap_connector": counts["roadmap connector"],
            "blocked": counts["blocked"],
            "do_not_claim": counts["do not claim"],
            **claim_summary,
        },
        "gates": gates,
        "gap_table": gap_table,
        "roadmap_package_view": [
            "Here is the physical system.",
            "Here is the model.",
            "Here is what the analog chip can run.",
            "Here is what stays digital.",
            "Here is what must be measured.",
            "Here is what failed or remains unconnected.",
            "Here is what claim is safe today.",
            "Here is the roadmap gap that must close next.",
        ],
        "what_not_to_claim": [
            "Do not convert source-checked market examples into proof that this chip supports a workload.",
            "Do not let fixed-weight inference efficiency imply adaptive Physical AI readiness.",
            "Do not let local estimates or replay fixtures upgrade production readiness.",
            "Do not claim full Physical AI readiness until compiler, board, power, accuracy, calibration, control, sensor, and reliability evidence satisfy their gates.",
        ],
    }
