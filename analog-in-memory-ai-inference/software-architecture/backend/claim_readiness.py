CLAIM_READINESS_SCHEMA_VERSION = "claim-readiness-v0.1"


def _sources_by_id(measurement_evidence):
    return {source.get("id"): source for source in measurement_evidence.get("required_sources", [])}


def _latest_payload(source):
    return ((source or {}).get("latest_import") or {}).get("payload") or {}


def _evidence_detail(source_id, source):
    payload = _latest_payload(source)
    if not payload:
        return None
    provenance = payload.get("provenance") or {}
    detail = {
        "source_id": source_id,
        "artifact_name": source.get("artifact_name"),
        "tool": provenance.get("tool", "not reported"),
        "confidence": source.get("confidence"),
    }
    if source_id == "task_accuracy":
        detail.update({
            "dataset_id": payload.get("dataset_id"),
            "metric_name": payload.get("metric_name"),
            "baseline_metric": payload.get("baseline_metric"),
            "candidate_metric": payload.get("candidate_metric"),
            "metric_delta": payload.get("metric_delta"),
            "tolerance": payload.get("tolerance"),
            "pass": payload.get("pass"),
            "record_count": payload.get("record_count"),
        })
    elif source_id == "analog_error_simulation":
        impact = payload.get("accuracy_impact") or {}
        detail.update({
            "error_model": payload.get("error_model"),
            "estimated_accuracy_drop": impact.get("estimated_drop"),
            "pass": impact.get("pass"),
            "calibration_profile": payload.get("calibration_profile"),
        })
    elif source_id == "board_runtime":
        trace = payload.get("trace") or []
        fallback_events = payload.get("fallback_events") or []
        detail.update({
            "package_id": payload.get("package_id"),
            "workload_id": payload.get("workload_id"),
            "board_id": payload.get("board_id"),
            "board_revision": payload.get("board_revision"),
            "runtime_version": payload.get("runtime_version"),
            "runtime_trace_id": payload.get("runtime_trace_id"),
            "latency_ms": payload.get("latency_ms"),
            "p50_latency_ms": payload.get("p50_latency_ms"),
            "p95_latency_ms": payload.get("p95_latency_ms"),
            "repetition_count": payload.get("repetition_count"),
            "start_timestamp": payload.get("start_timestamp"),
            "end_timestamp": payload.get("end_timestamp"),
            "host_overhead_boundary": payload.get("host_overhead_boundary"),
            "trace_events": len(trace),
            "fallback_events": len(fallback_events),
            "measurement_status": "local simulation" if provenance.get("tool") == "local-board-runtime-adapter" else "external or measured artifact",
            "measurement_level": provenance.get("measurement_level"),
            "runtime_mode": provenance.get("runtime_mode"),
        })
    elif source_id == "power_thermal":
        setup = payload.get("measurement_setup") or {}
        power_trace = payload.get("power_trace") or []
        temperature_trace = payload.get("temperature_trace") or []
        detail.update({
            "package_id": payload.get("package_id"),
            "workload_id": payload.get("workload_id"),
            "board_id": payload.get("board_id"),
            "runtime_trace_id": payload.get("runtime_trace_id"),
            "energy_uj": payload.get("energy_uj"),
            "average_power_mw": payload.get("average_power_mw"),
            "peak_power_mw": payload.get("peak_power_mw"),
            "sampling_rate": payload.get("sampling_rate"),
            "integration_start_timestamp": payload.get("integration_start_timestamp"),
            "integration_end_timestamp": payload.get("integration_end_timestamp"),
            "host_overhead_boundary": payload.get("host_overhead_boundary"),
            "meter": setup.get("meter"),
            "measured_rail": setup.get("measured_rail"),
            "supply_voltage": setup.get("supply_voltage"),
            "includes_host_overhead": setup.get("includes_host_overhead"),
            "not_measured_hardware": setup.get("not_measured_hardware"),
            "power_samples": len(power_trace),
            "temperature_samples": len(temperature_trace),
            "measurement_status": "local simulation" if setup.get("not_measured_hardware") is True or provenance.get("tool") == "local-power-thermal-adapter" else "external or measured artifact",
            "measurement_level": provenance.get("measurement_level"),
            "runtime_mode": setup.get("runtime_mode") or provenance.get("runtime_mode"),
        })
    elif source_id == "physical_flow":
        checks = payload.get("checks") or {}
        timing = payload.get("timing") or {}
        artifacts = payload.get("artifacts") or {}
        detail.update({
            "design_name": payload.get("design_name"),
            "flow_name": payload.get("flow_name"),
            "flow_status": payload.get("flow_status"),
            "critical_path_ns": timing.get("critical_path_ns"),
            "suggested_clock_period_ns": timing.get("suggested_clock_period_ns"),
            "suggested_clock_frequency_mhz": timing.get("suggested_clock_frequency_mhz"),
            "wns": timing.get("wns"),
            "tns": timing.get("tns"),
            "drc_violations": checks.get("drc_violations"),
            "lvs_errors": checks.get("lvs_errors"),
            "antenna_violations": checks.get("antenna_violations"),
            "gds_present": artifacts.get("gds"),
            "lef_present": artifacts.get("lef"),
            "sdf_present": artifacts.get("sdf"),
        })
    return {key: value for key, value in detail.items() if value is not None}


def _quality_issue_for_source(source_id, source):
    payload = _latest_payload(source)
    provenance = payload.get("provenance") or {}
    tool = str(provenance.get("tool", ""))
    if source_id == "board_runtime" and tool == "local-board-runtime-adapter":
        return "Board runtime artifact came from local simulation, not a real board or external simulator trace."
    if source_id == "board_runtime" and payload:
        if provenance.get("measurement_level") not in {"measured_board", "instrumented_runtime"}:
            return "Board runtime artifact is attached, but it does not carry measured_board or instrumented_runtime provenance."
        required = ["package_id", "workload_id", "board_id", "start_timestamp", "end_timestamp", "p50_latency_ms", "p95_latency_ms", "repetition_count", "host_overhead_boundary"]
        missing = [field for field in required if payload.get(field) in {None, ""}]
        if missing:
            return "Board runtime artifact is missing measured-runtime fields: " + ", ".join(missing) + "."
    if source_id == "power_thermal":
        setup = payload.get("measurement_setup") or {}
        if setup.get("not_measured_hardware") is True or tool == "local-power-thermal-adapter":
            return "Power/thermal artifact came from local simulation, not synchronized hardware measurement."
        if payload:
            if provenance.get("measurement_level") not in {"measured_board_power", "instrumented_power"}:
                return "Power/thermal artifact is attached, but it does not carry measured_board_power or instrumented_power provenance."
            required = ["package_id", "workload_id", "board_id", "runtime_trace_id", "integration_start_timestamp", "integration_end_timestamp", "average_power_mw", "peak_power_mw", "host_overhead_boundary"]
            missing = [field for field in required if payload.get(field) in {None, ""}]
            if missing:
                return "Power/thermal artifact is missing measured-power fields: " + ", ".join(missing) + "."
            if not setup.get("meter") or str(setup.get("meter")).lower() == "none":
                return "Power/thermal artifact does not name a meter or instrument source."
    if source_id == "task_accuracy" and payload:
        if payload.get("pass") is not True:
            delta = None
            try:
                delta = round(float(payload.get("baseline_metric")) - float(payload.get("candidate_metric")), 4)
            except Exception:
                delta = None
            detail = f"Task accuracy artifact reports pass=false"
            if delta is not None:
                detail += f" with metric delta {delta}"
            if payload.get("tolerance") is not None:
                detail += f" against tolerance {payload.get('tolerance')}"
            return detail + "."
    if source_id == "analog_error_simulation" and payload:
        impact = payload.get("accuracy_impact") or {}
        if impact.get("pass") is False:
            return "Analog error artifact reports accuracy_impact.pass=false."
    if source_id == "physical_flow" and payload:
        if payload.get("flow_status") != "flow completed":
            return "Physical-flow artifact is attached, but the flow did not complete."
        checks = payload.get("checks") or {}
        if any(checks.get(field) not in {0, 0.0, None} for field in ["drc_violations", "lvs_errors", "antenna_violations"]):
            return "Physical-flow artifact has DRC, LVS, or antenna violations."
        boundary = payload.get("claim_boundary") or {}
        if not boundary.get("not_allowed"):
            return "Physical-flow artifact does not state the stronger signoff or production claims it refuses."
    return None


def _energy_synchronization_issue(sources):
    runtime = _latest_payload(sources.get("board_runtime"))
    power = _latest_payload(sources.get("power_thermal"))
    if not runtime or not power:
        return None
    runtime_provenance = runtime.get("provenance") or {}
    power_provenance = power.get("provenance") or {}
    runtime_level = runtime_provenance.get("measurement_level")
    power_level = power_provenance.get("measurement_level")
    if runtime_level not in {"measured_board", "instrumented_runtime"}:
        return None
    if power_level not in {"measured_board_power", "instrumented_power"}:
        return None
    mismatches = []
    for field in ["package_id", "workload_id", "board_id"]:
        if runtime.get(field) and power.get(field) and runtime.get(field) != power.get(field):
            mismatches.append(field)
    if runtime.get("runtime_trace_id") and power.get("runtime_trace_id"):
        if runtime["runtime_trace_id"] != power["runtime_trace_id"]:
            mismatches.append("runtime_trace_id")
    if runtime.get("start_timestamp") and power.get("integration_start_timestamp"):
        if runtime["start_timestamp"] != power["integration_start_timestamp"]:
            mismatches.append("start_timestamp")
    if runtime.get("end_timestamp") and power.get("integration_end_timestamp"):
        if runtime["end_timestamp"] != power["integration_end_timestamp"]:
            mismatches.append("end_timestamp")
    if mismatches:
        return "Runtime and power artifacts are measured, but they do not describe the same run: " + ", ".join(mismatches) + "."
    return None


def _claim(claim_id, name, required_sources, sources, safe_when_supported, blocked_message, extra_quality_checks=None):
    missing = [source_id for source_id in required_sources if sources.get(source_id, {}).get("status") != "imported artifact"]
    quality_issues = [
        issue
        for source_id in required_sources
        for issue in [_quality_issue_for_source(source_id, sources.get(source_id))]
        if issue
    ]
    if extra_quality_checks and not missing:
        quality_issues.extend(issue for issue in extra_quality_checks(sources) if issue)
    if missing:
        status = "blocked"
    elif quality_issues:
        status = "needs review"
    else:
        status = "supported"
    imported = [
        {
            "source_id": source_id,
            "import_id": (sources.get(source_id, {}).get("latest_import") or {}).get("import_id"),
            "artifact_name": sources.get(source_id, {}).get("artifact_name"),
            "payload_status": (_latest_payload(sources.get(source_id)) or {}).get("pass"),
        }
        for source_id in required_sources
        if source_id not in missing
    ]
    evidence_details = [
        detail
        for source_id in required_sources
        for detail in [_evidence_detail(source_id, sources.get(source_id, {}))]
        if detail
    ]
    if status == "needs review":
        statement = "Required artifacts are attached, but the payload does not pass the claim-specific check: " + " ".join(quality_issues)
    else:
        statement = safe_when_supported if status == "supported" else blocked_message
    return {
        "id": claim_id,
        "name": name,
        "status": status,
        "required_sources": required_sources,
        "missing_sources": missing,
        "quality_issues": quality_issues,
        "imported_evidence": imported,
        "evidence_details": evidence_details,
        "safe_statement": statement,
    }


def build_claim_readiness(measurement_evidence, package_report=None):
    sources = _sources_by_id(measurement_evidence)
    lab_claims = [
        _claim(
            "C1",
            "Compiler placement is evidence-backed",
            ["compiler_mapping"],
            sources,
            "A compiler mapping artifact is attached for this package. It can support placement discussion, not production readiness.",
            "Compiler placement remains blocked because no compiler mapping artifact is attached.",
        ),
        _claim(
            "C2",
            "Latency is evidence-backed",
            ["board_runtime"],
            sources,
            "A board or simulator runtime trace is attached. It can support a latency discussion only at the evidence level reported by the payload.",
            "Measured latency remains blocked because no board or simulator runtime trace is attached.",
        ),
        _claim(
            "C3",
            "Energy is evidence-backed",
            ["board_runtime", "power_thermal"],
            sources,
            "Board runtime and power or thermal artifacts are attached for the same measured setup. Energy can be discussed for this runtime trace ID, package, workload, board, and run window only.",
            "Measured energy remains blocked until both runtime and power or thermal artifacts are attached.",
            extra_quality_checks=lambda current_sources: [_energy_synchronization_issue(current_sources)],
        ),
        _claim(
            "C4",
            "Accuracy is evidence-backed",
            ["analog_error_simulation", "task_accuracy"],
            sources,
            "Analog error and task accuracy artifacts are attached. Accuracy can be discussed for this dataset and tolerance.",
            "Accuracy under analog behavior remains blocked until analog error and task accuracy artifacts are both attached.",
        ),
        _claim(
            "C5",
            "Digital physical flow is evidence-backed",
            ["physical_flow"],
            sources,
            "A physical-flow artifact is attached. It can support a bounded claim that the selected digital controller reached the reported OpenLane or equivalent flow result.",
            "Digital physical-flow evidence remains blocked because no routed physical-flow artifact is attached.",
        ),
    ]
    supported = sum(1 for claim in lab_claims if claim["status"] == "supported")
    needs_review = sum(1 for claim in lab_claims if claim["status"] == "needs review")
    blocked = sum(1 for claim in lab_claims if claim["status"] == "blocked")
    production_claim = {
        "id": "P1",
        "name": "Production readiness",
        "status": "blocked",
        "required_sources": [source["id"] for source in measurement_evidence.get("required_sources", [])],
        "missing_sources": [],
        "safe_statement": "Production readiness is still blocked even if all lab evidence is attached. Yield, repeatability, drift, calibration cost, packaging, software integration, and customer operating conditions still need proof.",
    }
    return {
        "result_type": "claim_readiness",
        "schema_version": CLAIM_READINESS_SCHEMA_VERSION,
        "provenance": "derived from imported measurement evidence",
        "confidence": "medium" if supported else "low",
        "package_id": (package_report or {}).get("package_id") or measurement_evidence.get("summary", {}).get("package_id"),
        "summary": {
            "supported_lab_claims": supported,
            "blocked_lab_claims": blocked,
            "needs_review_lab_claims": needs_review,
            "production_claim": "blocked",
            "overall": "claim evidence needs review" if needs_review else "partial lab evidence" if supported else "no measured lab claims supported",
        },
        "lab_claims": lab_claims,
        "production_claim": production_claim,
        "do_not_claim": [
            "Do not turn one supported lab claim into a full hardware benchmark.",
            "Do not use compiler evidence as latency, energy, or accuracy evidence.",
            "Do not use board latency without power evidence as measured energy.",
            "Do not call a failed task-accuracy artifact support for accuracy preservation.",
            "Do not call a lab package production-ready.",
        ],
    }
