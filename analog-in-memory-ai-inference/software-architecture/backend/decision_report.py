DECISION_SCHEMA_VERSION = "decision-report-v0.1"


def _decision_label(analysis, runtime_profile, package_report, evidence_report, adapter_report):
    summary = analysis.get("summary", {})
    runtime = runtime_profile.get("summary", {})
    adapter_summary = adapter_report.get("summary", {})
    unsupported = [layer for layer in analysis.get("layers", []) if layer.get("placement") == "unsupported"]
    fallback = [layer for layer in analysis.get("layers", []) if layer.get("placement") == "fallback"]

    if unsupported or evidence_report.get("overall_status") == "blocked":
        return "not a fit yet"
    if not runtime.get("meets_latency_target") or not runtime.get("meets_energy_target"):
        return "not a fit yet"
    if fallback or summary.get("analog_coverage_percent", 0) < 45:
        return "needs rewrite"
    if runtime_profile.get("provenance") == "simulated" or adapter_summary.get("configured", 0) == 0:
        return "needs measurement"
    if package_report.get("readiness_stage") in {"simulator-ready", "prototype-ready", "candidate"}:
        return "good fit"
    return "needs measurement"


def _confidence(decision, evidence_report, adapter_report):
    if decision in {"not a fit yet", "needs rewrite"}:
        return "medium"
    if evidence_report.get("overall_status") == "evaluation only" or adapter_report.get("summary", {}).get("configured", 0) == 0:
        return "low"
    return "medium"


def _reasons(decision, analysis, runtime_profile, baseline_report, package_report, evidence_report, adapter_report):
    summary = analysis.get("summary", {})
    runtime = runtime_profile.get("summary", {})
    baseline = baseline_report.get("summary", {})
    adapter_summary = adapter_report.get("summary", {})
    reasons = [
        f"Analog coverage is {summary.get('analog_coverage_percent', 0)}% with {summary.get('fallback_count', 0)} fallback operator(s).",
        f"The completed-inference estimate is {runtime.get('latency_ms', 'n/a')} ms and {runtime.get('energy_uj', 'n/a')} uJ.",
        f"The estimated digital comparison is {baseline.get('energy_efficiency_x', 'n/a')}x energy efficiency and {baseline.get('latency_speedup_x', 'n/a')}x latency speedup.",
        f"Evidence status is {evidence_report.get('overall_status', 'unknown')}: {evidence_report.get('safe_claim', 'safe claim unavailable')}",
        f"Package readiness is {package_report.get('readiness_stage', 'unknown')}: {package_report.get('claim_level', 'claim unavailable')}.",
        f"External adapters: {adapter_summary.get('configured', 0)} configured, {adapter_summary.get('not_connected', 0)} not connected.",
    ]
    if decision == "needs rewrite":
        reasons.append("The main product issue is not speed alone; too little work reaches the analog path, so model shape or operator support should improve before stronger claims.")
    if decision == "needs measurement":
        reasons.append("The current result is useful for evaluation, but it still relies on estimates or simulation rather than a measured board run.")
    if decision == "not a fit yet":
        reasons.append("The current run should not be presented as a deployable hardware fit until blocked evidence or target misses are resolved.")
    return reasons


def _next_actions(decision, analysis, package_report, evidence_report, adapter_report):
    gates = evidence_report.get("gates", [])
    next_actions = []
    if decision == "needs rewrite":
        next_actions.append("Increase analog-friendly work by changing unsupported, fallback, or boundary-heavy regions before rerunning the project.")
    if decision == "needs measurement":
        next_actions.append("Connect simulator, board runtime, and power measurement adapters, then rerun the same project settings.")
    if decision == "not a fit yet":
        next_actions.append("Resolve blocked gates before comparing this run as a candidate.")
    for blocker in package_report.get("blockers", [])[:3]:
        next_actions.append(blocker.get("text"))
    for gate in gates:
        if gate.get("status") in {"blocked", "missing", "estimated"}:
            next_actions.append(f"{gate.get('name')}: {gate.get('required_next')}")
    deduped = []
    for item in next_actions:
        if item and item not in deduped:
            deduped.append(item)
    return deduped[:6]


def _what_to_say(decision, evidence_report):
    safe_claim = evidence_report.get("safe_claim", "This is an evaluation result, not production proof.")
    if decision == "good fit":
        return f"This workload looks like a good candidate, but the safe claim is still: {safe_claim}"
    if decision == "needs measurement":
        return f"This is promising as an evaluation result, but it needs measured simulator or board evidence before a hardware performance claim."
    if decision == "needs rewrite":
        return "This workload has useful signal, but the model or operator support should be improved before treating it as a strong analog fit."
    return "This workload is not ready to present as a fit yet. Fix the blocked evidence or target misses first."


def build_decision_report(analysis, runtime_profile, baseline_report, package_report, evidence_report, adapter_report):
    decision = _decision_label(analysis, runtime_profile, package_report, evidence_report, adapter_report)
    return {
        "result_type": "decision_report",
        "schema_version": DECISION_SCHEMA_VERSION,
        "provenance": "derived from local evaluation artifacts",
        "confidence": _confidence(decision, evidence_report, adapter_report),
        "decision": decision,
        "plain_answer": _what_to_say(decision, evidence_report),
        "summary": {
            "fit": analysis.get("summary", {}).get("fit"),
            "grade": analysis.get("summary", {}).get("grade"),
            "analog_coverage_percent": analysis.get("summary", {}).get("analog_coverage_percent"),
            "fallback_count": analysis.get("summary", {}).get("fallback_count"),
            "latency_ms": runtime_profile.get("summary", {}).get("latency_ms"),
            "energy_uj": runtime_profile.get("summary", {}).get("energy_uj"),
            "energy_efficiency_x": baseline_report.get("summary", {}).get("energy_efficiency_x"),
            "overall_status": evidence_report.get("overall_status"),
            "readiness_stage": package_report.get("readiness_stage"),
            "claim_level": package_report.get("claim_level"),
        },
        "reasons": _reasons(decision, analysis, runtime_profile, baseline_report, package_report, evidence_report, adapter_report),
        "next_actions": _next_actions(decision, analysis, package_report, evidence_report, adapter_report),
        "do_not_say": [
            "Do not call this measured hardware proof unless runtime and power data came from configured measurement adapters.",
            "Do not compare this result to a TOPS/W headline without checking what each side counted.",
            "Do not say analog is automatically better; say where this model does or does not fit the analog path.",
        ],
    }
