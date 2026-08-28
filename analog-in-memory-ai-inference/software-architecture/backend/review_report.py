REPORT_SCHEMA_VERSION = "plain-language-review-v0.1"


def _top_items(items, limit=4):
    return items[:limit] if items else []


def _section(title, lines):
    return [f"## {title}", "", *lines, ""]


def _bullet(text):
    return f"- {text}"


def _gate_line(gate):
    return f"{gate['id']} {gate['name']}: {gate['status']}. {gate['evidence']} Next: {gate['required_next']}"


def build_review_report(
    analysis,
    quantization_report,
    runtime_profile,
    baseline_comparison,
    package_report,
    evidence_gates,
    adapter_report=None,
):
    model = analysis.get("model", {})
    summary = analysis.get("summary", {})
    runtime = runtime_profile.get("summary", {})
    baseline = baseline_comparison.get("summary", {})
    quant = quantization_report.get("summary", {})
    calibration = analysis.get("calibration", {})
    adapter_summary = (adapter_report or {}).get("summary", {})
    project = package_report.get("project") or {}

    what_to_say = [
        f"The model was imported as ONNX and analyzed as {model.get('operators', 0)} operators.",
        f"The current rule-based mapper places {summary.get('analog_coverage_percent', 0)}% of operators on the analog path.",
        f"The simulated completed inference is {runtime.get('latency_ms', 0)} ms and {runtime.get('energy_uj', 0)} uJ in {runtime_profile.get('runtime_mode_label', 'selected')} mode.",
        f"The estimated digital baseline comparison shows {baseline.get('energy_efficiency_x', 0)}x energy efficiency and {baseline.get('latency_speedup_x', 0)}x latency speedup for this setup.",
        f"The quantization policy is {quant.get('recommended_policy', 'not selected')} with {quant.get('protected_layers', 0)} protected layer(s).",
        f"The adapter registry shows {adapter_summary.get('available', 0)} local/available adapter(s), {adapter_summary.get('configured', 0)} configured external adapter(s), and {adapter_summary.get('not_connected', 0)} not connected.",
        f"The safe claim is: {evidence_gates.get('safe_claim', 'claim unavailable')}",
    ]

    what_not_to_claim = [
        "Do not claim production readiness. The archive is an evaluation package, not a compiled hardware executable.",
        "Do not claim measured hardware energy. Runtime and baseline numbers are simulated or estimated unless a board adapter supplies measured data.",
        "Do not imply external hardware, compiler, simulator, or power tools are connected unless the adapter registry marks them configured.",
        "Do not claim TOPS/W proves product value. This report compares completed-inference latency and energy and lists what was counted.",
        "Do not claim analog is automatically better than digital. The result depends on operator fit, numeric tolerance, boundaries, memory movement, and workload targets.",
        "Do not treat one edge workload as proof for all edge AI. The selected modality and target profile matter.",
    ]

    hard_parts = [
        f"Operator support: {summary.get('fallback_count', 0)} operator(s) require fallback or unsupported handling.",
        f"Boundary cost: {len(analysis.get('boundary_events', []))} analog/digital boundary event(s) are counted.",
        f"Calibration: profile {calibration.get('profile_id', 'unknown')} has provenance {calibration.get('provenance', 'unknown')} and confidence {calibration.get('confidence', 'unknown')}.",
        f"Runtime evidence: profile provenance is {runtime_profile.get('provenance', 'unknown')} with confidence {runtime_profile.get('confidence', 'unknown')}.",
        f"External tools: {adapter_summary.get('configured', 0)} configured external adapter(s); {adapter_summary.get('not_connected', 0)} adapter(s) not connected.",
        f"Package readiness: {package_report.get('claim_level', 'claim unavailable')}.",
    ]

    next_evidence = []
    for gate in evidence_gates.get("gates", []):
        if gate["status"] in {"blocked", "missing", "estimated"}:
            next_evidence.append(_gate_line(gate))

    markdown_lines = [
        "# Analog In-Memory AI Inference Review Report",
        "",
        f"Project: {project.get('name', 'not attached')}",
        f"Project ID: {project.get('project_id', 'not attached')}",
        f"Model: {model.get('name', 'model')}",
        f"Target: {model.get('device_class', 'target unknown')}",
        f"Overall status: {evidence_gates.get('overall_status', 'unknown')}",
        f"Package: {package_report.get('package_id', 'package unavailable')}",
        "",
        *_section("Short Answer", [evidence_gates.get("safe_claim", "No safe claim is available.")]),
        *_section("What To Say Clearly", [_bullet(item) for item in what_to_say]),
        *_section("What Not To Overclaim", [_bullet(item) for item in what_not_to_claim]),
        *_section("Hard Parts", [_bullet(item) for item in hard_parts]),
        *_section("Evidence Still Needed", [_bullet(item) for item in _top_items(next_evidence, 8)]),
        *_section(
            "What Was Counted In The Baseline",
            [_bullet(item) for item in baseline_comparison.get("counted", [])],
        ),
        *_section(
            "What Was Not Counted",
            [_bullet(item) for item in baseline_comparison.get("excluded", [])],
        ),
    ]

    return {
        "result_type": "plain_language_review_report",
        "schema_version": REPORT_SCHEMA_VERSION,
        "provenance": "assembled from local analysis artifacts",
        "confidence": "low",
        "title": "Analog In-Memory AI Inference Review Report",
        "summary": {
            "model_name": model.get("name", "model"),
            "project_id": project.get("project_id"),
            "project_name": project.get("name"),
            "target": model.get("device_class", "target unknown"),
            "overall_status": evidence_gates.get("overall_status", "unknown"),
            "safe_claim": evidence_gates.get("safe_claim", "claim unavailable"),
            "package_id": package_report.get("package_id", "package unavailable"),
        },
        "sections": {
            "what_to_say": what_to_say,
            "what_not_to_overclaim": what_not_to_claim,
            "hard_parts": hard_parts,
            "evidence_still_needed": _top_items(next_evidence, 8),
            "counted_in_baseline": baseline_comparison.get("counted", []),
            "not_counted": baseline_comparison.get("excluded", []),
            "adapter_status": (adapter_report or {}).get("adapters", []),
        },
        "markdown": "\n".join(markdown_lines).strip() + "\n",
    }
