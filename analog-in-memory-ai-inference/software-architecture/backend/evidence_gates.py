GATE_SCHEMA_VERSION = "evidence-gates-v0.1"


def _gate(gate_id, name, status, evidence, required_next, severity="medium"):
    return {
        "id": gate_id,
        "name": name,
        "status": status,
        "severity": severity,
        "evidence": evidence,
        "required_next": required_next,
    }


def _overall_status(gates):
    if any(gate["status"] == "blocked" for gate in gates):
        return "blocked"
    if any(gate["status"] == "missing" for gate in gates):
        return "incomplete"
    if any(gate["status"] == "estimated" for gate in gates):
        return "evaluation only"
    return "ready for measured review"


def _safe_claim(overall_status):
    if overall_status == "blocked":
        return "This model is not ready to package for deployment."
    if overall_status == "incomplete":
        return "This model has a partial evaluation, but required evidence is missing."
    if overall_status == "evaluation only":
        return "This model has an evaluation package, but performance claims are estimated or simulated."
    return "This model is ready for measured hardware review, not production proof."


def build_evidence_gates(
    analysis,
    quantization_report,
    runtime_profile,
    baseline_comparison,
    package_report,
    adapter_report=None,
    measurement_evidence=None,
):
    layers = analysis.get("layers", [])
    unsupported = [layer for layer in layers if layer["placement"] == "unsupported"]
    fallback = [layer for layer in layers if layer["placement"] == "fallback"]
    boundaries = analysis.get("boundary_events", [])
    calibration = analysis.get("calibration", {})
    runtime_summary = runtime_profile.get("summary", {})
    baseline_summary = baseline_comparison.get("summary", {})
    adapter_summary = (adapter_report or {}).get("summary", {})
    measurement_summary = (measurement_evidence or {}).get("summary", {})

    gates = [
        _gate(
            "G1",
            "Model imported",
            "passed" if layers else "missing",
            f"{analysis.get('model', {}).get('name', 'model')} with {len(layers)} operators.",
            "Import a valid ONNX model." if not layers else "Keep model ID in the package manifest.",
            "high",
        ),
        _gate(
            "G2",
            "Operator support",
            "blocked" if unsupported else "estimated" if fallback else "passed",
            f"{len(unsupported)} unsupported operator(s), {len(fallback)} fallback operator(s).",
            "Rewrite unsupported operators or add runtime support." if unsupported else "Measure fallback cost on the target runtime." if fallback else "Keep support report with the package.",
            "high" if unsupported else "medium",
        ),
        _gate(
            "G3",
            "Analog and digital mapping",
            "estimated",
            f"{analysis.get('summary', {}).get('analog_coverage_percent', 0)}% analog coverage with {len(boundaries)} boundary event(s).",
            "Replace rule-based mapping with compiler-produced placement when available.",
        ),
        _gate(
            "G4",
            "Quantization policy",
            "estimated",
            f"{quantization_report.get('summary', {}).get('recommended_policy', 'policy unavailable')}; {quantization_report.get('summary', {}).get('protected_layers', 0)} protected layer(s).",
            "Run the selected modality dataset through the quantized model and compare the task metric.",
        ),
        _gate(
            "G5",
            "Calibration profile attached",
            "estimated" if calibration.get("provenance") == "simulated" else "passed",
            f"{calibration.get('profile_id', 'unknown')} from {calibration.get('provenance', 'unknown')} calibration.",
            "Attach measured board calibration before using hardware results." if calibration.get("provenance") == "simulated" else "Track board and calibration version in every report.",
        ),
        _gate(
            "G6",
            "Completed-inference profile",
            "estimated" if runtime_profile.get("provenance") == "simulated" else "passed",
            f"{runtime_summary.get('latency_ms', 0)} ms and {runtime_summary.get('energy_uj', 0)} uJ; status {runtime_summary.get('status', 'unknown')}.",
            "Replace simulated runtime data with simulator or board traces.",
            "high",
        ),
        _gate(
            "G7",
            "Target pass/fail",
            "passed" if runtime_summary.get("meets_latency_target") and runtime_summary.get("meets_energy_target") else "blocked",
            f"Latency target pass: {runtime_summary.get('meets_latency_target')}; energy target pass: {runtime_summary.get('meets_energy_target')}.",
            "Tune placement, runtime mode, or model shape until both targets pass.",
            "high",
        ),
        _gate(
            "G8",
            "Digital baseline comparison",
            "estimated" if baseline_comparison else "missing",
            f"Estimated energy efficiency {baseline_summary.get('energy_efficiency_x', 'n/a')}x and latency speedup {baseline_summary.get('latency_speedup_x', 'n/a')}x.",
            "Replace digital estimate with a measured baseline under the same accuracy and latency target.",
        ),
        _gate(
            "G9",
            "Package readiness",
            "passed" if package_report.get("readiness_stage") in {"simulator-ready", "prototype-ready", "candidate"} else "blocked" if package_report.get("readiness_stage") == "blocked" else "estimated",
            f"{package_report.get('readiness_stage', 'unknown')}: {package_report.get('claim_level', 'claim unavailable')}.",
            "Resolve blockers before claiming deployability.",
            "high",
        ),
        _gate(
            "G10",
            "External tool connections",
            "estimated" if adapter_report else "missing",
            f"{adapter_summary.get('available', 0)} local/available adapter(s), {adapter_summary.get('configured', 0)} configured external adapter(s), {adapter_summary.get('not_connected', 0)} not connected.",
            "Connect compiler, simulator, board runtime, and power measurement adapters before measured hardware claims.",
            "high",
        ),
        _gate(
            "G11",
            "Production claim safety",
            "estimated",
            "No measured board energy, thermal behavior, yield, repeatability, or long-term drift evidence in this prototype.",
            "Collect measured board results across operating conditions before production claims.",
            "high",
        ),
        _gate(
            "G12",
            "Measurement evidence contract",
            "estimated" if measurement_evidence else "missing",
            f"{measurement_summary.get('configured_sources', 0)} configured source(s), {measurement_summary.get('local_estimate_sources', 0)} local estimate source(s), {measurement_summary.get('missing_sources', 0)} missing source(s).",
            "Attach normalized compiler, simulator, board, power, and task-accuracy artifacts before upgrading claims.",
            "high",
        ),
    ]
    overall = _overall_status(gates)
    return {
        "result_type": "evidence_gate_report",
        "schema_version": GATE_SCHEMA_VERSION,
        "provenance": "assembled from local analysis artifacts",
        "confidence": "low",
        "overall_status": overall,
        "safe_claim": _safe_claim(overall),
        "gates": gates,
        "summary": {
            "passed": sum(1 for gate in gates if gate["status"] == "passed"),
            "estimated": sum(1 for gate in gates if gate["status"] == "estimated"),
            "blocked": sum(1 for gate in gates if gate["status"] == "blocked"),
            "missing": sum(1 for gate in gates if gate["status"] == "missing"),
        },
    }
